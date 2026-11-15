"""Orchestrateur en code : une machine à états à ordre fixe.

Profileur → Contrôle données + Analyste → Sceptique → Gardien → Rédacteur.
Aucune IA ne choisit l'ordre. Chaque agent lit et complète le même dossier.
Si une information essentielle manque, on s'arrête au Profileur et le verdict
est gris, avec les questions à poser.
"""
from __future__ import annotations

import copy
import time

from . import gardien
from .agents import analyste, profileur, redacteur, sceptique
from .donnees import info_actif
from .dossier import Dossier


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
                               "Même méthode que pour la demande, en CAD, 2021-11-12 → 2026-11-12.")
            return {"nom": "Alternative compatible avec tes valeurs", "ticker": t, "libelle_actif": info["name"],
                    "montant_cad": d.demande["montant_cad"], "horizon_ans": d.profil.get("horizon_ans"),
                    "etat": etat, "faits": [f.id]}
    return None


def analyser(profil: dict, demande: dict) -> dict:
    d = Dossier(profil=copy.deepcopy(profil), demande=copy.deepcopy(demande))

    profileur.executer(d)
    if not d.demande.get("ticker") or d.demande.get("montant_cad") is None:
        d.verdict = {"etat": "indetermine", "libelle": gardien.LIBELLES_ETAT["indetermine"],
                     "respectees": 0, "evaluees": 0}
        return d.to_dict()

    analyste.executer(d)
    sceptique.executer(d)

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
    if exclusion:
        alt = _alternative(d)
        if alt:
            d.options.append(alt)
    d.options.append({"nom": "Ne rien changer", "montant_cad": 0, "horizon_ans": d.profil.get("horizon_ans"),
                      "etat": "coherent"})
    if d.verdict["etat"] != "indetermine":
        d.bascule = gardien.grille_bascule(d.profil, d.demande, m)
    d.tracer("Gardien", "applique les règles et décide",
             f"{d.verdict['libelle']} ({d.verdict['respectees']}/{d.verdict['evaluees']} règles respectées). "
             f"Grille de bascule : {len(d.bascule.get('cases', []))} combinaisons recalculées.",
             [f for r in d.regles for f in r.faits if f], debut)

    redacteur.executer(d)
    return d.to_dict()
