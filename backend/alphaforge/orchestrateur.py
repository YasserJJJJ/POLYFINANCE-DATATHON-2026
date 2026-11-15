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

from . import gardien
from .agents import analyste, profileur, redacteur, sceptique
from .donnees import info_actif
from .dossier import Dossier
from .format import fr
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
        m = analyste.mesures_actif(t, d.profil.get("portefeuille_actuel"))
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
    m_ref = analyste.mesures_actif(ref, d.profil.get("portefeuille_actuel"))
    etat = gardien.verdict(gardien.appliquer_regles(d.profil, {**d.demande, "ticker": ref}, m_ref))["etat"]
    fait = d.demande["ids_faits"].get("reference")
    return {"nom": "Placement large, même montant", "ticker": ref, "libelle_actif": info["name"],
            "montant_cad": d.demande["montant_cad"], "horizon_ans": d.profil.get("horizon_ans"), "etat": etat,
            "faits": [fait] if fait else [],
            "note": (f"Pour comparer, le marché canadien large : pire chute observée {fr(m_ref['pire_chute_pct'])} %, "
                     f"contre {fr(m['pire_chute_pct'])} % pour {d.demande['ticker']}.")}


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
    if not d.demande.get("ticker") or d.demande.get("montant_cad") is None:
        d.verdict = {"etat": "indetermine", "libelle": gardien.LIBELLES_ETAT["indetermine"],
                     "respectees": 0, "evaluees": 0}
        return d.to_dict()

    analyste.executer(d)
    publier()
    sceptique.executer(d)
    publier()

    debut = time.perf_counter()
    m, ids = d.demande["mesures"], d.demande["ids_faits"]
    d.regles = gardien.appliquer_regles(d.profil, d.demande, m, ids)
    d.verdict = gardien.verdict(d.regles)
    ticker = d.demande["ticker"]
    d.options = [{"nom": "Ta demande", "ticker": ticker, "montant_cad": d.demande["montant_cad"],
                  "horizon_ans": d.profil.get("horizon_ans"), "etat": d.verdict["etat"]}]
    exclusion = any(r.code == "exclusion" and r.niveau == "rouge" for r in d.regles)
    if d.verdict["etat"] in ("incoherent", "ajustement") and not exclusion:
        aj = gardien.plus_petit_ajustement(d.profil, d.demande, m)
        if aj:
            d.options.append({"nom": "Version ajustée", "ticker": ticker, "changement": aj["changement"],
                              "etat": aj["etat"],
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
    d.tracer("Gardien", "applique les règles et décide",
             f"{d.verdict['libelle']} ({d.verdict['respectees']}/{d.verdict['evaluees']} règles respectées). "
             f"Grille de bascule : {len(d.bascule.get('cases', []))} combinaisons recalculées.",
             [f for r in d.regles for f in r.faits if f], debut)
    publier()

    redacteur.executer(d)
    publier()
    return d.to_dict()
