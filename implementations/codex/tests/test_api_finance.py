"""End-to-end financial contracts, using the frozen competition snapshot."""

import copy
import json
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

import alphaforge_app.main as main
from alphaforge_app.datasets import load_dataset
from alphaforge_app.personas import BY_ID


@pytest.fixture(scope="module")
def snapshot():
    return load_dataset()


@pytest.fixture
def client(monkeypatch, tmp_path, snapshot):
    # These tests never invoke a model or write into the application's reports.
    monkeypatch.setattr(main, "_dataset", snapshot)
    monkeypatch.setattr(main, "RUNTIME", tmp_path / "reports")
    with TestClient(main.app) as test_client:
        yield test_client


def request_for(persona_id):
    persona = BY_ID[persona_id]
    return {
        "persona": persona_id,
        "prompt": persona["prompt"],
        "portfolio": copy.deepcopy(persona["portfolio"]),
        "settings": copy.deepcopy(persona["settings"]),
        "use_ai": False,
    }


def analyze(client, payload):
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200, response.text
    result = response.json()
    json.dumps(result, allow_nan=False)
    return result


@pytest.mark.parametrize("persona_id", ["robert", "amira", "mateo"])
def test_complete_personas_recalculate_and_cite_real_sources(client, persona_id):
    payload = request_for(persona_id)
    result = analyze(client, payload)
    baseline = result["comparison"]["baseline"]
    alternative = result["comparison"]["alternative"]
    settings = payload["settings"]
    assert result["mode"] == "calculation"
    assert result["agent"] is None
    assert baseline["metrics"]["max_drawdown_pct"] <= 0
    assert alternative["metrics"]["max_drawdown_pct"] <= 0
    assert baseline["metrics"]["max_drawdown_pct"] != alternative["metrics"]["max_drawdown_pct"]
    assert alternative["weights"].get(settings["focus_ticker"], 0) == pytest.approx(settings["focus_weight"] / 100)
    assert sum(alternative["weights"].values()) == pytest.approx(1)
    assert [point["date"] for point in baseline["series"]] == [
        point["date"] for point in alternative["series"]
    ]
    assert result["data"]["observations"] == 1228
    assert result["data"]["analysis_mode"] == "retrospective_replay"
    assert len(result["data"]["files"]["prices_daily.csv"]["sha256"]) == 64
    ids = {source["id"] for source in result["sources"]}
    assert all(set(observation["source_ids"]) <= ids for observation in result["observations"])
    case_source = next(source for source in result["sources"] if source["id"] == "case")
    assert "hypothèses" in case_source["note"]
    assert any("hypothèses fictives" in limitation for limitation in result["limitations"])
    for source in result["sources"]:
        if source["url"].startswith("/"):
            linked = client.get(source["url"])
            assert linked.status_code == 200, source["url"]
            assert len(linked.text) > 100


@pytest.mark.parametrize("persona_id", ["robert", "amira", "mateo"])
def test_persona_only_request_inherits_that_personas_demo_settings(client, persona_id):
    result = analyze(client, {"persona": persona_id, "use_ai": False})
    expected = BY_ID[persona_id]["settings"]
    for field in ("horizon_years", "focus_ticker", "focus_weight", "max_drawdown_pct"):
        assert result["settings"][field] == expected[field]
    assert result["profile"]["horizon_years"] == expected["horizon_years"]
    expected_ticker = expected["focus_ticker"]
    assert result["comparison"]["alternative"]["weights"].get(expected_ticker, 0) == pytest.approx(expected["focus_weight"] / 100)


def test_partial_settings_preserve_persona_defaults(client):
    result = analyze(client, {"persona": "amira", "settings": {"capital": 20000}, "use_ai": False})
    assert result["settings"]["capital"] == 20000
    assert result["settings"]["horizon_years"] == 15
    assert result["settings"]["focus_ticker"] == "NVDA"
    assert result["comparison"]["baseline"]["metrics"]["initial_value_cad"] == 20000


def test_capital_scales_dollars_but_not_return_or_loss_rates(client):
    payload = request_for("robert")
    base = analyze(client, payload)
    payload["settings"]["capital"] *= 3
    large = analyze(client, payload)
    for option in ("baseline", "alternative"):
        before = base["comparison"][option]["metrics"]
        after = large["comparison"][option]["metrics"]
        assert after["ending_value_cad"] == pytest.approx(before["ending_value_cad"] * 3, abs=0.02)
        for field in ("total_return_pct", "max_drawdown_pct", "cagr_pct", "volatility_pct"):
            assert after[field] == pytest.approx(before[field])


def test_slider_at_original_weight_is_an_identity_and_threshold_does_not_move_prices(client):
    payload = request_for("robert")
    payload["settings"]["focus_weight"] = 25
    identity = analyze(client, payload)
    assert identity["comparison"]["baseline"]["series"] == identity["comparison"]["alternative"]["series"]
    payload["settings"]["max_drawdown_pct"] = 1
    low = analyze(client, payload)
    payload["settings"]["max_drawdown_pct"] = 90
    high = analyze(client, payload)
    assert low["comparison"] == high["comparison"]
    low_text = next(item["text"] for item in low["observations"] if item["id"] == "comfort")
    high_text = next(item["text"] for item in high["observations"] if item["id"] == "comfort")
    assert "dépasse le repère" in low_text
    assert "ne dépasse pas le repère" in high_text
    assert "ne garantit pas" in low_text and "ne garantit pas" in high_text


def test_esg_exclusion_is_a_direct_holding_change_not_a_certification(client):
    result = analyze(client, request_for("mateo"))
    baseline = result["comparison"]["baseline"]
    alternative = result["comparison"]["alternative"]
    assert baseline["weights"]["XOM"] == 0.1
    assert "XOM" not in alternative["weights"]
    assert "ESGV" in alternative["weights"]
    # On this frozen sample the exclusion worsens the sampled drawdown.
    # The explanation must report this, rather than promising lower risk.
    assert abs(alternative["metrics"]["max_drawdown_pct"]) > abs(baseline["metrics"]["max_drawdown_pct"])
    drawdown = next(item["text"] for item in result["observations"] if item["id"] == "drawdown")
    assert "plus forte" in drawdown
    esg = next(item["text"] for item in result["summary"]["findings"] if item["id"] == "esg")
    assert "ne certifie pas" in esg
    assert alternative["concentration"]["look_through_available"] is False


@pytest.mark.parametrize("portfolio", [
    [{"ticker": "TSLA", "weight": 0.2}],
    [{"ticker": "TSLA", "weight": -0.1}, {"ticker": "SPY", "weight": 1.1}],
    [{"ticker": "TSLA", "weight": 0.5}, {"ticker": "TSLA", "weight": 0.5}],
    [{"ticker": "UNKNOWN", "weight": 1}],
])
def test_invalid_portfolios_are_rejected(client, portfolio):
    payload = request_for("robert")
    payload["portfolio"] = portfolio
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_saved_report_preserves_financial_results(client):
    result = analyze(client, request_for("amira"))
    report = client.get(f"/api/report/{result['id']}")
    assert report.status_code == 200
    restored = report.json()
    assert restored["comparison"] == result["comparison"]
    assert restored["data"]["files"] == result["data"]["files"]


def test_starter_source_uses_configured_snapshot_directory(client, monkeypatch, tmp_path, snapshot):
    # A restored installation must serve its own snapshot documentation, not
    # an unrelated original absolute path on the author's laptop.
    marker = "# Documentation du snapshot restauré\n" * 5
    (tmp_path / "README.md").write_text(marker)
    monkeypatch.setattr(main, "_dataset", replace(snapshot, directory=str(tmp_path)))
    response = client.get("/api/source/starter")
    assert response.status_code == 200
    assert response.text == marker
