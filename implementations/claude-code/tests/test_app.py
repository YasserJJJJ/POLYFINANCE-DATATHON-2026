"""Application web : construction du scénario, recalcul réel et erreurs lisibles (sans AWS)."""

import pytest

from datathon2026 import app
from datathon2026 import tools as T


def test_bootstrap_reads_config_and_excludes_held_assets():
    b = app.bootstrap()
    sc = T.load_scenarios()["robert"]
    assert b["robert"]["actif"] == sc["actif_demande"]
    assert not {a["t"] for a in b["actifs"]} & set(sc["portefeuille_actuel"])
    assert b["profils"]["mateo"]["reference"] is False


def test_changing_a_hypothesis_recomputes_the_dossier():
    base = app.produce({"profil": "robert", "mode": "reference", "hypotheses": {}})
    tight = app.produce({"profil": "robert", "mode": "reference", "hypotheses": {"seuil": 13}})
    assert base["controle"]["ok"] and tight["controle"]["ok"]
    assert base["hypotheses_modifiees"] == [] and tight["hypotheses_modifiees"] == ["seuil de perte"]
    assert base["html"] != tight["html"]  # la part maximale compatible change avec le seuil


def test_other_asset_and_amira_cap_run():
    gold = app.produce({"profil": "robert", "mode": "reference", "hypotheses": {"actif": "BTC-USD", "alternative": "GLD", "part": 8}})
    assert gold["controle"]["ok"] and set(gold["hypotheses_modifiees"]) == {"actif étudié", "alternative comparée", "part étudiée"}
    cap = app.produce({"profil": "amira", "mode": "reference", "hypotheses": {"plafond": 40}})
    assert cap["controle"]["ok"] and cap["hypotheses_modifiees"] == ["plafond de risque par groupe"]


@pytest.mark.parametrize("payload, message", [
    ({"profil": "inconnu"}, "profil"),
    ({"profil": "robert", "hypotheses": {"part": 80}}, "part"),
    ({"profil": "robert", "hypotheses": {"actif": "XXX"}}, "symbole"),
    ({"profil": "robert", "hypotheses": {"actif": "SPY"}}, "absents du portefeuille"),
    ({"profil": "robert", "hypotheses": {"actif": "QQQ"}}, "différents"),
    ({"profil": "mateo", "mode": "reference"}, "agent"),
    ({"profil": "robert", "mode": "reference", "demande": "Autre demande"}, "demande libre"),
])
def test_invalid_inputs_give_readable_errors(payload, message):
    with pytest.raises(ValueError, match=message):
        app.produce(payload)
