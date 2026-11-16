"""Rien sans source : chaque chiffre, chaque règle et chaque agent renvoie à une donnée, une méthode ou une
référence du registre (alphaforge/sources.py), et un seuil de l'équipe est toujours dit comme une hypothèse."""
import re

import pytest

from alphaforge import sources
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS

CAS = [(n, {}) for n in PERSONAS] + [("robert", {"ticker": "ENB.TO"}), ("amira", {"ticker": "ETH-USD"}),
                                     ("mateo", {"ticker": "XBB.TO"})]


def _run(nom, demande):
    p = PERSONAS[nom]
    return analyser(p["profil"], {**p["demande"], **demande})


def test_registre_coherent_et_honnete():
    ids = set(sources.REFERENCES)
    for cle, j in list(sources.JUSTIFICATIONS.items()) + list(sources.AGENTS.items()):
        for r in j.get("references", []) + j.get("donnees", []):
            assert r in ids, (cle, r)
    for rid, ref in sources.REFERENCES.items():
        for champ in ("type", "auteurs", "titre", "annee", "examen", "apport"):
            assert ref.get(champ), (rid, champ)
        assert ref["type"] in ("donnees", "reglementation", "recherche", "methode", "interne"), rid
        # Une référence non relue ne doit jamais se présenter comme vérifiée.
        if "non relu" in ref["examen"]:
            assert "vérifi" not in ref["examen"].replace("non vérifié", ""), rid


@pytest.mark.parametrize("nom, demande", CAS)
def test_chaque_fait_a_des_sources_et_une_donnee(nom, demande):
    d = _run(nom, demande)
    for f in d["faits"]:
        assert f["references"], f["libelle"]
        assert all(r in sources.REFERENCES for r in f["references"]), f
        if f["type"] != "HYPOTHESE":   # un chiffre de marché vient toujours d'un fichier du jeu de départ
            assert any(sources.REFERENCES[r]["type"] == "donnees" for r in f["references"]), f["libelle"]


@pytest.mark.parametrize("nom, demande", CAS)
def test_chaque_regle_a_une_nature_et_des_sources(nom, demande):
    for r in _run(nom, demande)["regles"]:
        assert r["type"] in ("FAIT", "HYPOTHESE", "SCENARIO"), r
        assert r["references"] and all(x in sources.REFERENCES for x in r["references"]), r["code"]


@pytest.mark.parametrize("nom, demande", CAS)
def test_chaque_etape_de_la_trace_dit_pourquoi_l_agent_est_concu_ainsi(nom, demande):
    for t in _run(nom, demande)["trace"]:
        assert t["references"], t["agent"]


@pytest.mark.parametrize("nom", list(PERSONAS))
def test_les_seuils_de_l_equipe_sont_au_registre_comme_hypotheses(nom):
    d = _run(nom, {})
    hyp = [f for f in d["faits"] if f["type"] == "HYPOTHESE"]
    assert len(hyp) >= 4 and all("hypothèse de l'équipe" in f["libelle"] for f in hyp)
    # La règle de perte supportable cite le barème qu'elle applique.
    capacite = next(r for r in d["regles"] if r["code"] == "capacite")
    assert any(f["id"] in capacite["faits"] for f in hyp)


def test_le_rendement_passe_affiche_son_incertitude():
    d = _run("robert", {})
    rend = next(f for f in d["faits"] if f["libelle"].startswith("Rendement annualisé passé"))
    assert "Erreur type" in rend["methode"] and "ne sert jamais au verdict" in rend["methode"]
    assert "demiguel-2009" in rend["references"]


def test_limites_sourcees_et_adaptees_a_la_demande():
    amira = _run("amira", {})["texte"]["limites"]          # horizon 15 ans, BTC en USD
    assert any("dépasse les 5 ans de données" in ph["texte"] for ph in amira)
    assert any("Banque du Canada" in ph["texte"] for ph in amira)
    mateo = _run("mateo", {})["texte"]["limites"]           # ENB.TO, en CAD, horizon 10 ans
    assert not any("Banque du Canada" in ph["texte"] for ph in mateo)
    assert any("yfinance" in ph["texte"] for ph in mateo)
    for ph in amira + mateo:
        assert all(r in sources.REFERENCES for r in ph.get("references", []))


def test_api_expose_le_registre():
    import api
    reg = api.sources_du_projet()
    assert set(reg) == {"references", "justifications", "agents"} and len(reg["references"]) >= 25


def test_doc_sources_a_jour():
    # docs/sources.md est généré depuis le registre : il ne doit jamais diverger du code.
    from pathlib import Path
    import generer_doc_sources as g
    assert Path(g.CIBLE).read_text(encoding="utf-8") == g.generer(), "relancer : python generer_doc_sources.py"
