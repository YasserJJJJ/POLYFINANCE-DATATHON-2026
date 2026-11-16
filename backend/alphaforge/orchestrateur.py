"""Orchestrateur en code : une machine à états à ordre fixe.

Profileur → Contrôle données + Analyste → Sceptique → Gardien → Rédacteur.
Aucune IA ne choisit l'ordre. Chaque agent lit et complète le même dossier.
Si une information essentielle manque, on s'arrête au Profileur et le verdict
est gris, avec les questions à poser.
"""
from __future__ import annotations

import copy
import time
from collections.abc import Callable
from dataclasses import asdict

from . import gardien, llm, plan_ouvert
from .agents import analyste, profileur, redacteur, sceptique
from .donnees import info_actif
from .dossier import Dossier
from .format import fr
from .profil import symboles_portefeuille
from .sources import references_de


# Placements larges essayés, dans l'ordre, quand une exclusion bloque la demande.
CANDIDATS_ALTERNATIVE = ["ESGV", "XIU.TO", "XBB.TO", "FTS.TO"]


def _alternative(d: Dossier) -> dict | None:
    """Premier placement large, hors secteurs exclus, que le Gardien juge acceptable au même montant."""
    exclusions = gardien.exclusions_normalisees(d.profil)
    for t in CANDIDATS_ALTERNATIVE:
        info = info_actif(t)
        if t == d.demande["ticker"] or any(e in str(info["sector"]).lower() for e in exclusions):
            continue
        m = analyste.mesures_actif(t, symboles_portefeuille(d.profil.get("portefeuille_actuel")))
        etat = gardien.verdict(gardien.appliquer_regles(d.profil, {**d.demande, "ticker": t}, m))["etat"]
        if etat in ("coherent", "ajustement"):
            f = d.ajouter_fait(f"Pire chute de {t} ({info['name']})", m["pire_chute_pct"], "%", "FAIT",
                               "Yahoo Finance via yfinance, jeu de départ AlphaForge",
                               "Même méthode que pour la demande, en CAD, 2021-11-12 → 2026-11-12.",
                               references=references_de("alternative"))
            return {"nom": "Alternative compatible avec tes exclusions de secteur", "ticker": t, "libelle_actif": info["name"],
                    "montant_cad": d.demande["montant_cad"], "horizon_ans": d.profil.get("horizon_ans"),
                    "etat": etat, "faits": [f.id]}
    return None


def _placement_large(d: Dossier, m: dict) -> dict | None:
    """Le même montant dans le marché canadien large, jugé par le Gardien : une règle simple ferait-elle aussi bien ?"""
    ref = analyste.REFERENCE
    info = info_actif(ref)
    if d.demande["ticker"] == ref or any(e in str(info["sector"]).lower() for e in gardien.exclusions_normalisees(d.profil)):
        return None
    m_ref = analyste.mesures_actif(ref, symboles_portefeuille(d.profil.get("portefeuille_actuel")))
    etat = gardien.verdict(gardien.appliquer_regles(d.profil, {**d.demande, "ticker": ref}, m_ref))["etat"]
    fait = d.demande["ids_faits"].get("reference")
    return {"nom": "Placement large, même montant", "ticker": ref, "libelle_actif": info["name"],
            "montant_cad": d.demande["montant_cad"], "horizon_ans": d.profil.get("horizon_ans"), "etat": etat,
            "faits": [fait] if fait else [],
            "note": (f"Pour comparer, le marché canadien large : pire chute observée {fr(m_ref['pire_chute_pct'])} %, "
                     f"contre {fr(m['pire_chute_pct'])} % pour {d.demande['ticker']}.")}


def _question_retrait(d: Dossier, m: dict) -> None:
    """Teste une hypothèse séparée, sans compléter le profil de la personne."""
    horizon = d.profil.get("horizon_ans")
    if d.profil.get("retrait_prevu_ans") is not None or horizon is None:
        return
    regles = gardien.appliquer_regles({**d.profil, "retrait_prevu_ans": horizon}, d.demande, m)
    alternatif = gardien.verdict(regles)
    if alternatif["etat"] == d.verdict["etat"]:
        return
    fait = d.ajouter_fait(
        "Hypothèse testée : retrait à l'horizon déclaré", horizon, "an(s)", "HYPOTHESE",
        "Horizon déclaré et Gardien, sans modification du profil",
        f"Recalcul avec retrait_prevu_ans = horizon_ans : {d.verdict['etat']} → {alternatif['etat']}. "
        "Le verdict affiché conserve les données fournies.",
        references=references_de("h_retrait_decisif"),
    )
    d.questions.append(
        f"Question décisive — Prévois-tu un retrait dans {fr(horizon)} an(s), à ton horizon déclaré ? "
        f"Avec ce retrait, le verdict passerait de « {d.verdict['libelle']} » à "
        f"« {alternatif['libelle']} ». Cette date reste à confirmer ({fait.id})."
    )


def _documenter_monotonie(d: Dossier) -> None:
    """Observe la grille exacte ; n'en lisse aucune case."""
    if not d.bascule or not d.comparaison.get("disponible"):
        return
    cases = {(c["montant_cad"], c["horizon_ans"]): c["etat"] for c in d.bascule["cases"]}
    montants = sorted(d.bascule["montants"])
    exemple = None
    for h in d.bascule["horizons"]:
        for petit, grand in zip(montants, montants[1:]):
            if gardien.RANG[cases[petit, h]] > gardien.RANG[cases[grand, h]]:
                exemple = {"montant_bas_cad": petit, "montant_haut_cad": grand, "horizon_ans": h,
                           "etat_bas": cases[petit, h], "etat_haut": cases[grand, h]}
                break
        if exemple:
            break
    explication = (
        "Un montant plus élevé peut améliorer le verdict quand le placement diversifie le portefeuille. "
        "Les cases sont les résultats exacts du Gardien ; une amélioration n'est pas une erreur de grille."
        if exemple else "Aucune inversion de verdict observée sur les montants de cette grille."
    )
    d.bascule["monotonie_montant"] = {
        "observee": exemple is None, "explication": explication, "exemple": exemple,
        "faits": [d.comparaison["faits"]["h_non_monotonie"],
                  d.comparaison["faits"]["avant_pire_chute"],
                  d.comparaison["faits"]["apres_pire_chute"],
                  d.comparaison["faits"]["ecart_pire_chute"]],
    }
    if exemple:
        hypothese = d.fait(d.comparaison["faits"]["h_non_monotonie"])
        hypothese.valeur = {"explication": hypothese.valeur, "exemple_observe": exemple}
        hypothese.methode += " Exemple issu des cases de la grille, recalculées par le Gardien."


def analyser(profil: dict, demande: dict, sur_etape: Callable[[dict], None] | None = None) -> dict:
    """`sur_etape` reçoit chaque étape de la trace dès que son agent a fini (affichage en direct)."""
    d = Dossier(profil=copy.deepcopy(profil), demande=copy.deepcopy(demande))
    publiees = 0

    def publier() -> None:
        nonlocal publiees
        if sur_etape:
            for t in d.trace[publiees:]:
                sur_etape({"etape": asdict(t), "faits": [asdict(f) for f in d.faits],
                           "objections": [asdict(o) for o in d.objections] if t.agent == "Sceptique" else []})
        publiees = len(d.trace)

    profileur.executer(d)
    publier()
    if not d.demande.get("ticker") and d.demande.get("montant_cad") is not None:
        plan_ouvert.executer(d)          # pas de placement choisi : le Gardien juge le plan sur toute la liste
        publier()
        d.appels_modele = llm.journal_appels()
        return d.to_dict()
    if not d.demande.get("ticker") or d.demande.get("montant_cad") is None:
        d.verdict = {"etat": "indetermine", "libelle": gardien.LIBELLES_ETAT["indetermine"],
                     "respectees": 0, "evaluees": 0}
        d.appels_modele = llm.journal_appels()
        return d.to_dict()

    analyste.executer(d)
    publier()
    sceptique.executer(d)
    publier()

    debut = time.perf_counter()
    m, ids = d.demande["mesures"], d.demande["ids_faits"]
    d.regles = gardien.appliquer_regles(d.profil, d.demande, m, ids)
    d.verdict = gardien.verdict(d.regles)
    if d.verdict["etat"] == "indetermine":
        d.questions = [q for q in gardien.questions_manquantes(d.profil, d.demande) if q not in d.questions] + d.questions
    _question_retrait(d, m)
    ticker = d.demande["ticker"]
    d.options = [{"nom": "Ta demande", "ticker": ticker, "montant_cad": d.demande["montant_cad"],
                  "horizon_ans": d.profil.get("horizon_ans"), "etat": d.verdict["etat"]}]
    exclusion = any(r.code == "exclusion" and r.niveau == "rouge" for r in d.regles)
    if d.verdict["etat"] in ("incoherent", "ajustement") and not exclusion:
        aj = gardien.plus_petit_ajustement(d.profil, d.demande, m)
        if aj:
            d.options.append({"nom": "Version ajustée", "ticker": ticker, "changement": aj["changement"],
                              "etat": aj["etat"],
                              **{k: aj[k] for k in ("sens", "constat") if k in aj},
                              "montant_cad": aj["changement"].get("montant_cad", d.demande["montant_cad"]),
                              "horizon_ans": aj["changement"].get("horizon_ans", d.profil.get("horizon_ans"))})
    alt = _alternative(d) if exclusion else None
    if alt:
        d.options.append(alt)          # l'alternative est déjà un placement large compatible avec les exclusions
    else:
        large = _placement_large(d, m)
        if large:
            d.options.append(large)
    if d.verdict["etat"] != "indetermine":
        d.bascule = gardien.grille_bascule(d.profil, d.demande, m)
        _documenter_monotonie(d)
    if d.verdict["etat"] == "incoherent":
        plan_ouvert.suggerer(d)
    d.tracer("Gardien", "applique les règles et décide",
             f"{d.verdict['libelle']} ({d.verdict['respectees']}/{d.verdict['evaluees']} règles respectées). "
             f"Grille de bascule : {len(d.bascule.get('cases', []))} combinaisons recalculées."
             + (f" {len(d.suggestions['placements'])} autre(s) placement(s) de la liste passent tes règles."
                if d.suggestions else ""),
             [f for r in d.regles for f in r.faits if f], debut)
    publier()

    redacteur.executer(d)
    # Pont de restitution dans le fichier possédé par T2 : le gabarit T1 disait
    # toujours « ramener ». T4 pourra consommer directement option.constat.
    ajustee = next((o for o in d.options if o.get("constat")), None)
    if ajustee:
        phrases = d.texte.get("ce_qui_changerait") or []
        d.texte["ce_qui_changerait"] = [
            {"texte": ajustee["constat"], "type": "SCENARIO", "faits": []}, *phrases[1:]
        ]
    publier()
    d.appels_modele = llm.journal_appels()
    return d.to_dict()
