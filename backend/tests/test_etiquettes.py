"""Étiquettes FAIT / HYPOTHESE / SCENARIO : un seuil de l'équipe n'est pas un fait, une situation fictive non plus."""
import re

import pytest

from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS

SEUIL = re.compile(r"\bseuils?\b|\blimite\b|capacité de perte|/100", re.I)
SCENARIO = re.compile(r"\bsi\b.*\b(revivait|se répétait)\b|\bferait baisser\b|\bperdrait\b", re.I)


def _phrases(d):
    t = d["texte"]
    return [ph for s in ("miroir", "pourquoi", "ce_qui_changerait", "limites") for ph in t[s]]


@pytest.mark.parametrize("nom", list(PERSONAS))
def test_aucun_fait_ne_porte_un_seuil_ou_un_scenario(nom):
    p = PERSONAS[nom]
    for ph in _phrases(analyser(p["profil"], p["demande"])):
        if ph["type"] == "FAIT":
            assert not SEUIL.search(ph["texte"]), ph
            assert not SCENARIO.search(ph["texte"]), ph
            assert ph["faits"], ph   # un FAIT cite toujours au moins un F-n


def test_recalcul_du_sceptique_est_un_fait_qui_cite_le_fait_recalcule():
    p = PERSONAS["robert"]   # TSLA est en USD : le Sceptique recalcule la chute sans conversion
    d = analyser(p["profil"], p["demande"])
    usd = next(f for f in d["faits"] if "en USD" in f["libelle"])
    lim = next(ph for ph in d["texte"]["limites"] if ph["texte"].startswith("Recalcul fait"))
    assert lim["type"] == "FAIT" and usd["id"] in lim["faits"]
