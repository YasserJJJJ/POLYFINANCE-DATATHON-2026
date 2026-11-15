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
from .dossier import Dossier


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
    d.options = [{"nom": "Ta demande", "montant_cad": d.demande["montant_cad"],
                  "horizon_ans": d.profil.get("horizon_ans"), "etat": d.verdict["etat"]}]
    if d.verdict["etat"] in ("incoherent", "ajustement"):
        aj = gardien.plus_petit_ajustement(d.profil, d.demande, m)
        if aj:
            d.options.append({"nom": "Version ajustée", "changement": aj["changement"], "etat": aj["etat"],
                              "montant_cad": aj["changement"].get("montant_cad", d.demande["montant_cad"]),
                              "horizon_ans": aj["changement"].get("horizon_ans", d.profil.get("horizon_ans"))})
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
