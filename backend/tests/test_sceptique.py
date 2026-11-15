"""Sceptique : ses vérifications disent ce que les chiffres montrent, et la trace dit qui a choisi."""
import types

import pytest

from alphaforge import llm
from alphaforge.agents import analyste, profileur, sceptique
from alphaforge.dossier import Dossier
from alphaforge.personas import PERSONAS


def _dossier(ticker, portefeuille=None, nom="robert"):
    p = PERSONAS[nom]
    d = Dossier(profil={**p["profil"], "portefeuille_actuel": portefeuille or []},
                demande={**p["demande"], "ticker": ticker, "texte": ""})
    profileur.executer(d)
    analyste.executer(d)
    return d


def test_comparaison_au_marche_ne_conclut_pas_sans_condition():
    # XBB.TO (obligations) chute à peine moins que XIU.TO : avant, « propre à ce placement, pas au marché ».
    d = _dossier("XBB.TO")
    rep = sceptique._reference(d, d.demande["mesures"], d.demande["ids_faits"])
    assert "propre à ce placement" not in rep and "n'est pas plus forte" in rep
    d = _dossier("TSLA")
    assert "tient surtout au placement" in sceptique._reference(d, d.demande["mesures"], d.demande["ids_faits"])


def test_correlation_moyenne_renvoie_au_seuil_du_gardien():
    d = _dossier("NVDA", ["QQQ"], "amira")   # corrélation NVDA~QQQ de 0,75 : entre 0,6 et 0,8
    rep = sceptique._concentration(d, d.demande["mesures"], d.demande["ids_faits"])
    assert "0,8" in rep and "seuil de l'équipe" in rep
