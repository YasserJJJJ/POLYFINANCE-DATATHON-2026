"""Depuis la racine : PYTHONPATH=backend python ce_fichier.py [--url API-BEDROCK].

Sans --url : captures et comparaison C hors ligne. Avec --url : une exécution
réelle de chacun des trois personas, puis égalité des cinq objets décisionnels.
Les inférences sont réalisées par l'API cible, pas par ce script.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import sys
import time
import urllib.request

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parents[3] / "backend"))
os.environ["ALPHAFORGE_LLM"] = "off"
os.environ["ALPHAFORGE_DATA_BUCKET"] = ""
os.environ.pop("ALPHAFORGE_CAPACITE", None)
import api
from alphaforge import sources
from alphaforge.personas import PERSONAS


def sauver(nom, objet):
    (ICI / nom).write_text(json.dumps(objet, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def lire(url, entree=None):
    req = urllib.request.Request(url, data=json.dumps(entree).encode() if entree else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url")
    a = p.parse_args()
    if a.url:
        sante = lire(a.url.rstrip("/") + "/api/sante")
        assert sante["region"] == "us-east-1" and sante["llm"]
        assert set(sante["modeles_ids"].values()) == {
            "global.anthropic.claude-sonnet-5", "global.amazon.nova-2-lite-v1:0"}
        sauver("sante-bedrock.json", sante)
    bilan = {}
    for nom in ("robert", "amira", "mateo"):
        entree = {k: copy.deepcopy(PERSONAS[nom][k]) for k in ("profil", "demande")}
        hors = api._analyser_requete(api.Requete(**entree))
        sauver(f"{nom}-entree.json", entree)
        sauver(f"{nom}-hors-ligne.json", hors)
        if a.url:
            # Ne jamais répéter silencieusement une inférence déjà capturée.
            cible = ICI / f"{nom}-bedrock.json"
            if cible.exists():
                raise RuntimeError(f"Capture déjà présente : {cible}")
            t = time.perf_counter()
            d = lire(a.url.rstrip("/") + "/api/analyse", entree)
            duree = round(time.perf_counter() - t, 3)
            sauver(cible.name, d)
            egalites = {k: d[k] == hors[k] for k in ("verdict", "regles", "options", "bascule", "comparaison")}
            appels = d["appels_modele"]
            bilan[nom] = {"duree_http_s": duree, "egalites": egalites, "appels": appels,
                          "nombre_appels": len(appels),
                          "jetons": sum((x["jetons_entree"] or 0) + (x["jetons_sortie"] or 0) for x in appels)}
            sauver("bilan-bedrock.json", bilan)
            assert all(egalites.values()), egalites
            assert appels and all(x["request_id"] for x in appels)
            print(nom, json.dumps(bilan[nom], ensure_ascii=False), flush=True)
        else:
            os.environ["ALPHAFORGE_CAPACITE"] = "approximation"
            seul_c = api._analyser_requete(api.Requete(**entree))
            os.environ.pop("ALPHAFORGE_CAPACITE")
            sauver(f"{nom}-approximation.json", seul_c)
            bilan[nom] = {"fusion": {"verdict": hors["verdict"], "capacite": next(r for r in hors["regles"] if r["code"] == "capacite")},
                          "approximation": {"verdict": seul_c["verdict"], "capacite": next(r for r in seul_c["regles"] if r["code"] == "capacite")}}
    if a.url:
        return
    sauver("comparaison-avec-c.json", bilan)
    variants = [
        ("cas4-sans-epargne", "robert", {"epargne_totale_cad": None}, {}),
        ("cas5-sans-retrait", "robert", {"retrait_prevu_ans": None}, {}),
        ("cas6-impossible", "robert", {"epargne_totale_cad": 100000}, {"montant_cad": 120000}),
        ("cas8-retrait10", "robert", {"retrait_prevu_ans": 10}, {}),
        ("cas8-montant20000", "robert", {"retrait_prevu_ans": 10}, {"montant_cad": 20000}),
        ("amira-xiu14000", "amira", {}, {"ticker": "XIU.TO", "montant_cad": 14000}),
        ("amira-xiu35000", "amira", {}, {"ticker": "XIU.TO", "montant_cad": 35000}),
    ]
    for nom, persona, profil, demande in variants:
        entree = copy.deepcopy(PERSONAS[persona])
        entree["profil"].update(profil)
        entree["demande"].update(demande)
        sauver(nom + ".json", api._analyser_requete(api.Requete(**{k: entree[k] for k in ("profil", "demande")})))
    try:
        api._analyser_requete(api.Requete(profil=PERSONAS["robert"]["profil"],
                                         demande={"ticker": "GME", "montant_cad": 80000, "texte": "GameStop"}))
    except api.HTTPException as e:
        sauver("cas7-gamestop.json", {"statut": e.status_code, "message": e.detail})
    sauver("registre.json", sources.registre())


if __name__ == "__main__":
    main()
