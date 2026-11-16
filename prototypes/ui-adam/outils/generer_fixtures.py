"""Génère les données communes des cinq prototypes à partir du moteur réel, hors ligne.

Aucun calcul n'est fait ici : chaque dossier vient de `orchestrateur.analyser` (mode ALPHAFORGE_LLM=off),
chaque série du moteur historique transféré de B, chaque appel de modèle des preuves de la tranche 4.
Usage : cd backend && ALPHAFORGE_LLM=off python ../prototypes/ui-adam/outils/generer_fixtures.py
"""
import copy, datetime, json, os, subprocess, sys
from pathlib import Path

os.environ["ALPHAFORGE_LLM"] = "off"
RACINE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RACINE / "backend"))
import api  # noqa: E402
from alphaforge import portefeuille as P  # noqa: E402
from alphaforge.moteurs.historique import analytics as an  # noqa: E402
from alphaforge.orchestrateur import analyser  # noqa: E402
from alphaforge.personas import PERSONAS  # noqa: E402

PAS = 5  # une séance sur cinq : assez pour un tracé, sans alourdir le fichier


def cle(montant, retrait, exclusion):
    return f"m={int(montant)};r={'na' if retrait is None else retrait};x={1 if exclusion else 0}"


def series(dossier):
    k = dossier.get("comparaison") or {}
    if not k.get("disponible"):
        return None
    capital = dossier["profil"]["epargne_totale_cad"]
    r = an.compare_portfolios(
        [{"id": "avant", "weights": k["poids_avant"]}, {"id": "apres", "weights": k["poids_apres"]}],
        capital_cad=capital, dataset=P.jeu_donnees())
    sortie = {}
    for nom, o in zip(("avant", "apres"), r["options"]):
        pts = o["series"][::PAS] + ([o["series"][-1]] if (len(o["series"]) - 1) % PAS else [])
        sortie[nom] = [[p["date"], round(p["value"], 0), round(p["drawdown_pct"], 2)] for p in pts]
        sortie[nom + "_fenetres"] = [{"nom": s["name"], "debut": s["start"], "fin": s["end"],
                                      "rendement_pct": s["total_return_pct"], "pire_chute_pct": s["max_drawdown_pct"]}
                                     for s in o["scenarios"]]
    return sortie


def un(profil, demande, base=False):
    d = analyser(copy.deepcopy(profil), copy.deepcopy(demande))
    d["series_portefeuille"] = series(d)
    if not base:
        d.pop("bascule", None)
    return d


def cas(nom, retraits, exclusions):
    p = PERSONAS[nom]
    base = un(p["profil"], p["demande"], base=True)
    montants = list(base["bascule"]["montants"])
    for o in base["options"]:
        m = (o.get("changement") or {}).get("montant_cad")
        if m and m not in montants:
            montants.append(m)
    variantes = {}
    for r in retraits:
        for x in exclusions:
            for m in montants:
                profil = {**p["profil"], "retrait_prevu_ans": r, "exclusions": list(p["profil"]["exclusions"]) if x else []}
                variantes[cle(m, r, x)] = un(profil, {**p["demande"], "montant_cad": m})
    r0, x0 = p["profil"].get("retrait_prevu_ans"), bool(p["profil"]["exclusions"])
    variantes[cle(p["demande"]["montant_cad"], r0, x0)]["bascule"] = base["bascule"]
    reel = RACINE / "docs/fusion/preuves/tranche4" / f"{nom}-bedrock.json"
    execution = None
    if reel.exists():
        b = json.loads(reel.read_text(encoding="utf-8"))
        execution = {"source": str(reel.relative_to(RACINE)), "appels_modele": b["appels_modele"],
                     "trace": [{"agent": t["agent"], "duree_ms": t["duree_ms"]} for t in b["trace"]],
                     "texte": {c: b["texte"].get(c) for c in ("reformulation", "miroir", "pourquoi")}}
    return {"id": nom, "source_profil": p.get("source_profil"), "depart": cle(p["demande"]["montant_cad"], r0, x0),
            "parametres": {"montant": sorted(montants, reverse=True), "retrait": retraits,
                           "exclusion": [bool(x) for x in exclusions]},
            "serie_actif": api.serie(p["demande"]["ticker"]), "variantes": variantes, "execution_reelle": execution}


def special(profil, demande):
    try:
        return {"ok": True, "dossier": api.analyse(api.Requete(profil=profil, demande=demande))}
    except Exception as e:  # l'API répond par une erreur explicite : on garde son message exact
        return {"ok": False, "statut": getattr(e, "status_code", None), "message": str(getattr(e, "detail", e))}


rob = PERSONAS["robert"]
sortie = {
    "meta": {
        "genere_le": datetime.datetime.now().isoformat(timespec="seconds"),
        "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RACINE, capture_output=True, text=True).stdout.strip(),
        "mode": "moteur réel, hors ligne (ALPHAFORGE_LLM=off) : textes en gabarit, aucun appel de modèle",
        "pas_series": PAS,
        "avertissement": "Données de démonstration : dossiers précalculés par le moteur réel. Profils, montants et poids fictifs.",
    },
    "cas": {
        "robert": cas("robert", [rob["profil"]["retrait_prevu_ans"], None], [False]),
        "amira": cas("amira", [None], [False]),
        "mateo": cas("mateo", [None], [True, False]),
    },
    "speciaux": {
        "sans_epargne": special({**rob["profil"], "epargne_totale_cad": None}, rob["demande"]),
        "impossible": special({**rob["profil"], "epargne_totale_cad": 100000, "somme_a_preserver_cad": None},
                              {**rob["demande"], "montant_cad": 120000}),
        "hors_univers": special(rob["profil"], {"texte": "Je veux mettre 20 000 $ dans GameStop.", "ticker": "GME", "montant_cad": 20000}),
    },
    "sources": api.sources_du_projet(),
    "questions": api.questions(),
    "actifs": api.actifs(),
}
dest = Path(__file__).resolve().parents[1] / "socle"
texte = json.dumps(sortie, ensure_ascii=False, separators=(",", ":"), default=str)
(dest / "fixtures.js").write_text("window.AF_FIXTURES=" + texte + ";\n", encoding="utf-8")
print("écrit", dest / "fixtures.js", round(len(texte) / 1e6, 2), "Mo")
for n, c in sortie["cas"].items():
    print(n, c["depart"], len(c["variantes"]), "variantes", {k: v["verdict"]["etat"] for k, v in list(c["variantes"].items())[:20]})
for n, s in sortie["speciaux"].items():
    print(n, s["ok"], (s.get("message") or s["dossier"]["verdict"]["etat"]), (s.get("dossier") or {}).get("questions"))
