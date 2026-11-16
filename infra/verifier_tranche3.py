"""Capture quelques analyses HTTP et compare leur décision à la même entrée hors ligne.

Le serveur doit être lancé séparément avec AWS_PROFILE=alphaforge et AWS_REGION=us-east-1.
Ce vérificateur n'appelle aucun modèle lui-même ; seule l'API ciblée en appelle.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import time
import urllib.request

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "backend"))
os.environ["ALPHAFORGE_LLM"] = "off"
os.environ["ALPHAFORGE_DATA_BUCKET"] = ""

from api import Requete, _analyser_requete  # noqa: E402
from alphaforge.personas import PERSONAS  # noqa: E402


def cas():
    exemples = {nom: {k: deepcopy(PERSONAS[nom][k]) for k in ("profil", "demande")}
                for nom in ("robert", "amira")}
    libre = deepcopy(exemples["amira"])
    libre["profil"].update(nom="Cas libre contradictoire", citations=[])
    libre["demande"]["texte"] = (
        "Je veux mettre 10 000 $ en Bitcoin, doubler rapidement mon argent sans aucun risque. "
        "Je ne veux perdre aucune somme et tout le monde en parle.")
    exemples["contradictoire"] = libre
    return exemples


def lire(url, entree=None):
    req = urllib.request.Request(url, data=json.dumps(entree).encode() if entree else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.loads(response.read())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default="http://127.0.0.1:8765")
    p.add_argument("--sortie", type=Path, required=True)
    p.add_argument("--cas", choices=["tous", "robert"], default="tous")
    p.add_argument("--reprendre", action="store_true", help="réutilise les dossiers déjà capturés sans nouvel appel")
    a = p.parse_args()
    a.sortie.mkdir(parents=True, exist_ok=True)

    def sauver(nom, objet):
        (a.sortie / nom).write_text(json.dumps(objet, ensure_ascii=False, indent=2, default=str) + "\n")

    sante = lire(a.url.rstrip("/") + "/api/sante")
    sauver("sante.json", sante)
    assert sante["region"] == "us-east-1"
    assert set(sante["modeles_ids"].values()) == {
        "global.anthropic.claude-sonnet-5", "global.amazon.nova-2-lite-v1:0"}
    bilan = {}
    for nom, entree in cas().items():
        if a.cas != "tous" and nom != a.cas:
            continue
        hors_ligne = _analyser_requete(Requete(**deepcopy(entree)))
        sauver(f"{nom}-entree.json", entree)
        sauver(f"{nom}-hors-ligne.json", hors_ligne)
        mesure = a.sortie / f"{nom}-mesure.json"
        if a.reprendre and (a.sortie / f"{nom}-bedrock.json").exists():
            dossier = json.loads((a.sortie / f"{nom}-bedrock.json").read_text())
            duree = json.loads(mesure.read_text())["duree_http_s"] if mesure.exists() else None
        else:
            debut = time.perf_counter()
            dossier = lire(a.url.rstrip("/") + "/api/analyse", entree)
            duree = round(time.perf_counter() - debut, 3)
            sauver(f"{nom}-bedrock.json", dossier)
            sauver(f"{nom}-mesure.json", {"duree_http_s": duree})
        controles = {cle: dossier[cle] == hors_ligne[cle] for cle in ("verdict", "regles", "options", "bascule")}
        appels = dossier["appels_modele"]
        bilan[nom] = {"duree_http_s": duree, "duree_agents_ms": sum(t["duree_ms"] for t in dossier["trace"]),
                      "decisions_identiques": controles,
                      "nombre_appels": len(appels), "appels": appels,
                      "jetons_entree": sum(e["jetons_entree"] or 0 for e in appels),
                      "jetons_sortie": sum(e["jetons_sortie"] or 0 for e in appels),
                      "source_texte": dossier["texte"]["source"],
                      "controle_ancrage": dossier["texte"]["controle"]}
        sauver("bilan.json", bilan)
        print(json.dumps({nom: bilan[nom]}, ensure_ascii=False), flush=True)
        assert appels and all(e["request_id"] for e in appels), "Preuve d'appel incomplète"
        assert all(controles.values()), "Décision différente : consigner l'incompatibilité"
    return bilan


if __name__ == "__main__":
    main()
