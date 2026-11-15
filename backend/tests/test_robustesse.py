"""Cas limites : une entrée impossible donne un verdict gris expliqué, jamais une exception ni un faux « cohérent »."""
import pytest

from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS


def _run(nom, profil=None, demande=None):
    p = PERSONAS[nom]
    return analyser({**p["profil"], **(profil or {})}, {**p["demande"], **(demande or {})})


@pytest.mark.parametrize("profil, demande", [
    ({"epargne_totale_cad": 0}, None),            # avant : ZeroDivisionError (HTTP 500)
    ({"epargne_totale_cad": -8000}, None),        # avant : « -8000 % de son épargne »
    (None, {"montant_cad": -80000}),              # avant : « Cohérent 7/7 »
    (None, {"montant_cad": 0}),
    ({"horizon_ans": 0}, None),
    ({"horizon_ans": -3}, None),
])
def test_valeur_impossible_donne_gris_explique(profil, demande):
    d = _run("robert", profil, demande)
    assert d["verdict"]["etat"] == "indetermine"
    assert d["regles"][0]["code"] == "donnees" and "Il faut" in d["regles"][0]["explication"]


def test_valeurs_valides_inchangees():
    assert _run("robert")["verdict"]["etat"] == "ajustement"
