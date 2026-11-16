"""Dossiers de démonstration : vérification complète et cohérence des seuils."""

import pytest

from datathon2026 import analytics as a
from datathon2026 import report, workflow
from datathon2026 import tools as T


@pytest.fixture(scope="module")
def session():
    return T.Session()


@pytest.mark.parametrize("name", list(workflow.WORKFLOWS))
def test_dossier_passes_verification_and_renders(name):
    d = workflow.WORKFLOWS[name]().to_dict()
    assert d["verification"]["ok"], d["verification"]["problemes"]
    assert "[" not in d["resume"]["texte"]  # aucune référence non résolue
    page = report.render(d)
    assert 'class="bad"' not in page


def test_robert_flip_point_is_consistent(session):
    sc = T.load_scenarios()["robert"]
    out = T.share_sweep(session, "test", sc["portefeuille_actuel"], "TSLA", sc["seuil_perte"])
    flip = out["_brut"]["part_max"]
    depth = lambda x: a.max_drawdown(a.portfolio(session.market, a.blend(sc["portefeuille_actuel"], "TSLA", x)).index).depth  # noqa: E731
    assert depth(flip) >= sc["seuil_perte"] > depth(round(flip + 0.01, 2))


def test_amira_variant_respects_cap(session):
    sc = T.load_scenarios()["amira"]
    out = T.diversification_sweep(session, "test", sc["portefeuille_propose"], sc["panier_diversification"], sc["plafond_risque_groupe"])
    w = out["_brut"]["poids"]
    p = a.portfolio(session.market, w)
    groups = {}
    for t, rc in p.risk_contrib.items():
        groups[session.group_of(t)] = groups.get(session.group_of(t), 0) + rc
    assert max(groups.values()) <= sc["plafond_risque_groupe"]


def test_changing_a_hypothesis_changes_the_conclusion():
    sc = dict(T.load_scenarios()["robert"])
    tight = workflow.robert(dict(sc, seuil_perte=-0.13)).to_dict()
    loose = workflow.robert(dict(sc, seuil_perte=-0.20)).to_dict()
    part = lambda d: next(r["value"] for r in d["enregistrements"].values() if r["label"].startswith("Part maximale de TSLA"))  # noqa: E731
    assert part(tight) < part(loose)


def test_tools_reject_invalid_inputs_instead_of_returning_an_empty_result(session):
    base = {"XBB.TO": 0.6, "XIU.TO": 0.4}
    with pytest.raises(ValueError, match="seuil_perte"):
        T.share_sweep(session, "test", base, "GLD", 0.129)  # seuil positif : erreur d'unité de l'appelant
    with pytest.raises(ValueError, match="plafond"):
        T.diversification_sweep(session, "test", base, {"GLD": 1.0}, 50)
    with pytest.raises(ValueError, match="somme"):
        T.portfolio_metrics(session, "test", {"XBB.TO": 0.6, "XIU.TO": 0.6})
    with pytest.raises(ValueError, match="part"):
        a.blend(base, "GLD", 10)
    thirds = T.portfolio_metrics(session, "tiers", {"XBB.TO": 0.333333, "XIU.TO": 0.333333, "GLD": 0.333333})  # arrondi toléré
    assert thirds["vol"]["id"] in session.registry


@pytest.mark.parametrize("name", list(workflow.WORKFLOWS))
def test_saved_dossier_can_be_reloaded_and_reverified_offline(name):
    import json

    from datathon2026.dossier import Dossier

    saved = json.loads(json.dumps(workflow.WORKFLOWS[name]().to_dict(), ensure_ascii=False, default=str))
    again = json.loads(json.dumps(Dossier.from_dict(saved).to_dict(), ensure_ascii=False, default=str))
    assert again == saved
