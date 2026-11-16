"""Chaîne jouet : six tâches, fonctions pures qui déclarent leurs entrées. Aucun appel de modèle.

Toutes les valeurs sont fictives et le disent (« fictif »). Les dépendances suivent le tableau
« ce qui rouvre, et ce qui reste » du document 04, section 3.
"""
from __future__ import annotations

import random
from collections import Counter

from dossier import Tache, canon

APPELS: Counter = Counter()  # nombre d'exécutions réelles de chaque fonction, pour les assertions

TACHES = [
    Tache("qualification", "agent0", ("fait:objectif", "fait:titre", "fait:part"), "decision"),
    Tache("preuves", "agent1", ("decision", "catalogue"), "preuves"),
    Tache("plan", "agent2", ("decision", "preuves", "fait:horizon"), "plan"),
    Tache("calculs", "code", ("plan", "donnees", "catalogue"), "calculs"),
    Tache("objections", "contradicteur", ("plan", "calculs", "catalogue"), "objections"),
    Tache("restitution", "agent3", ("calculs", "objections", "fait:perte_acceptable", "fait:prenom"), "restitution"),
]
SORTIES = {t.nom: t.sortie for t in TACHES}
DROITS = {"personne": ("fait:",), "code": ("donnees", "catalogue")}  # qui dépose quoi ; le reste vient des tâches

FAITS = {"fait:objectif": "Préserver le capital", "fait:titre": "TSLA", "fait:part": 10,
         "fait:horizon": 5, "fait:prenom": "Robert"}  # « fait:perte_acceptable » manque : c'est la question posée
DONNEES = {"instantane": "jouet-2026-11-15", "fenetre": ["2016-01", "2025-12"], "fictif": True}
CATALOGUE = {"version": "jouet-1", "graine": 2026, "seuil_ecart_pts": 2.0,
             "methodes": {"ecarts_apparies": ["pire_baisse", "rendement"], "equilibre": ["rendement"]}}


def qualification(e):
    APPELS["qualification"] += 1
    mesure = "pire_baisse" if "préserver" in e["fait:objectif"].lower() else "rendement"
    return {"decision": "ajout_titre", "titre": e["fait:titre"], "part_pct": e["fait:part"], "mesure": mesure}


def preuves(e):
    APPELS["preuves"] += 1
    d = e["decision"]
    methodes = sorted(m for m, usages in e["catalogue"]["methodes"].items() if d["mesure"] in usages)
    return {"fiches": [f"fiche-produit-{d['titre']}", f"fiche-mesure-{d['mesure']}"], "methodes": methodes}


def plan(e):
    APPELS["plan"] += 1
    d = e["decision"]
    return {"options": ["ne_rien_changer", f"{d['titre']}@{d['part_pct']}"], "mesure": d["mesure"],
            "methodes": e["preuves"]["methodes"], "horizon_ans": e["fait:horizon"], "scelle": True}


def _tirage(e) -> float:
    graine = f"{e['catalogue']['graine']}|{canon(e['plan']).decode()}|{e['donnees']['instantane']}"
    return round(random.Random(graine).uniform(3.0, 9.0), 2)


def calculs(e):
    APPELS["calculs"] += 1
    return {"fictif": True, "ecart_pts": -_tirage(e), "graine": e["catalogue"]["graine"]}  # signe faux : essai (f)


def calculs_v2(e):
    APPELS["calculs"] += 1
    return {"fictif": True, "ecart_pts": _tirage(e), "graine": e["catalogue"]["graine"]}


def objections(e):
    APPELS["objections"] += 1
    tient = abs(e["calculs"]["ecart_pts"]) > e["catalogue"]["seuil_ecart_pts"]
    return {"registre": [{"type": "sous_periode", "vise": e["plan"]["mesure"], "ecart_eprouve": e["calculs"]["ecart_pts"],
                          "verdict": "tient" if tient else "change"}]}


def restitution(e):
    APPELS["restitution"] += 1
    cas = "au-delà" if abs(e["calculs"]["ecart_pts"]) > e["fait:perte_acceptable"] else "en deçà"
    return {"fictif": True, "pour": e["fait:prenom"], "cas": cas, "ecart_pts": e["calculs"]["ecart_pts"],
            "perte_acceptable_pct": e["fait:perte_acceptable"],
            "verdicts": [o["verdict"] for o in e["objections"]["registre"]]}


FONCTIONS = {"qualification": qualification, "preuves": preuves, "plan": plan, "calculs": calculs,
             "objections": objections, "restitution": restitution}
