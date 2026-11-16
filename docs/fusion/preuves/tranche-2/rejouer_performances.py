"""Depuis la racine : ALPHAFORGE_LLM=off PYTHONPATH=backend python <ce fichier>.

Mesure locale sans réseau, caches applicatifs vidés avant chaque analyse.
Le cache du système de fichiers et les imports Python restent chauds.
"""
import copy
import json
import os
import time

os.environ["ALPHAFORGE_LLM"] = "off"
os.environ["ALPHAFORGE_DATA_BUCKET"] = ""
os.environ.pop("ALPHAFORGE_CAPACITE", None)

from alphaforge import donnees, portefeuille
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS


def vider():
    for fonction in (portefeuille._comparer, portefeuille.jeu_donnees,
                     portefeuille._panneau, portefeuille._baisse,
                     donnees.univers, donnees._prix, donnees._fx, donnees.serie_cad):
        fonction.cache_clear()


resultats = {}
for nom in ("robert", "amira", "mateo", "amira_xiu_14000"):
    entree = copy.deepcopy(PERSONAS["amira" if nom.startswith("amira") else nom])
    if nom == "amira_xiu_14000":
        entree["demande"].update(ticker="XIU.TO", montant_cad=14000)
    durees = []
    for _ in range(3):
        vider()
        debut = time.perf_counter()
        dossier = analyser(entree["profil"], entree["demande"])
        durees.append(round((time.perf_counter() - debut) * 1000, 3))
    resultats[nom] = {
        "durees_ms": durees, "maximum_ms": max(durees),
        "verdict": dossier["verdict"],
        "niveaux": {r["code"]: r["niveau"] for r in dossier["regles"]},
        "comparaison": dossier["comparaison"],
        "ajustement": next((o for o in dossier["options"] if o["nom"] == "Version ajustée"), None),
    }
print(json.dumps({
    "conditions": "3 analyses par cas, sans modèle ni réseau ; caches applicatifs vidés, imports déjà chargés.",
    "resultats": resultats,
}, ensure_ascii=False, indent=2, allow_nan=False))
