"""Independent financial references and explicit failure boundaries."""
import copy
import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from alphaforge_app.decision import finance
from alphaforge_app.datasets import Dataset


def reserve_problem(**updates):
    value = {
        "decision_type": "reserve_allocation", "question": "Cas de référence.",
        "currency": "CAD", "capital_cad": 100,
        "holdings": [{"ticker": "A", "weight": 1}],
        "withdrawal_cad": 25, "withdrawal_months": 12, "horizon_years": 4,
        "max_asset_weights": {}, "scenario_loss_limit_cad": None, "scenarios": [],
        "objective": "minimize_reallocated_capital", "reserve_policy": "abstract_nominal",
        "assumptions": [], "unknowns": [], "clarifications": [],
    }
    value.update(updates)
    return value


def example(ident):
    return copy.deepcopy(next(x["facts"] for x in finance.examples() if x["id"] == ident))


def resolve_pointer(value, pointer):
    for token in pointer.lstrip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def assert_serializable_and_linked(result):
    json.dumps(result, allow_nan=False)
    for claim in result["claims"]:
        for ref in claim["result_refs"]:
            assert resolve_pointer(result, ref["pointer"]) is not None
            assert ref["unit"]


@pytest.mark.parametrize("withdrawal", [30000, 40000])
def test_robert_minimum_is_proved_by_independent_reserve_bound(withdrawal):
    problem = example("robert")
    problem["withdrawal_cad"] = withdrawal
    original = copy.deepcopy(problem)
    result = finance.analyze(problem)
    assert result["status"] == "conditional"
    assert problem == original
    baseline, optimum = result["options"][:2]
    assert baseline["admissible"] is False
    assert optimum["metrics"]["turnover_cad"]["value"] == pytest.approx(withdrawal)
    assert optimum["metrics"]["reserve_cad"]["value"] >= withdrawal - .001
    assert optimum["weights"]["TSLA"] <= .1 + finance.TOL
    # A zero initial reserve requires Q/V buys. Half-L1 equals total buys,
    # independently of the LP implementation and its arbitrary optimum.
    assert .5 * sum(abs(optimum["weights"].get(t, 0) - baseline["weights"].get(t, 0))
                      for t in baseline["weights"]) == pytest.approx(withdrawal / 100000)
    checks = {c["id"]: c for c in result["checks"]}
    assert checks["constraints"]["numerical_checks_pass"]
    assert checks["independent_lower_bound"]["attained"]
    assert result["optimal_face"]["non_unique_witness_found"]
    assert result["optimal_face"]["secondary_preference_selected"] is False
    for option in result["options"][1:]:
        assert option["admissible"]
        assert option["metrics"]["turnover_cad"]["value"] == pytest.approx(withdrawal, abs=.002)
        for shock in option["scenario_results"]:
            assert shock["kind"] == "hypothetical"
            assert shock["probability"] is None
            assert shock["loss_cad"] <= 15000 + .001
            assert shock["wealth_after_withdrawal_cad"] == pytest.approx(
                100000 - shock["loss_cad"] - withdrawal)
    assert result["provenance"]["data"][0]["market_data_used"] is False
    assert_serializable_and_linked(result)


def test_cap_can_dominate_reserve_bound_on_a_new_problem():
    result = finance.analyze(reserve_problem(max_asset_weights={"A": .6}))
    optimum = result["options"][1]
    # Only A and reserve are allowed: A <= .6 forces a sale of .4.
    assert optimum["weights"]["A"] == pytest.approx(.6)
    assert optimum["metrics"]["turnover_cad"]["value"] == pytest.approx(40)
    assert optimum["metrics"]["reserve_cad"]["value"] == pytest.approx(40)
    assert result["optimal_face"]["non_unique_witness_found"] is False


def test_existing_reserve_is_counted_without_forcing_new_purchases():
    result = finance.analyze(reserve_problem(
        holdings=[{"ticker": "A", "weight": .6}, {"ticker": finance.RESERVE, "weight": .4}],
        withdrawal_cad=30))
    assert result["options"][1]["metrics"]["turnover_cad"]["value"] == pytest.approx(0)
    assert result["options"][0]["admissible"]


def test_scenario_can_make_simple_lower_bound_non_tight():
    result = finance.analyze(reserve_problem(
        holdings=[{"ticker": "A", "weight": 1}, {"ticker": "B", "weight": 0}],
        withdrawal_cad=0, scenario_loss_limit_cad=10,
        scenarios=[{"id": "s", "kind": "hypothetical", "horizon_months": 12,
                    "returns": {"A": -.5, "B": 0}}]))
    assert result["status"] == "conditional"
    # Loss <= 10 on capital 100 requires w_A <= .2; total sales >= .8.
    assert result["options"][1]["metrics"]["turnover_cad"]["value"] == pytest.approx(80)
    bound = next(c for c in result["checks"] if c["id"] == "independent_lower_bound")
    assert bound["status"] == "partial"
    assert bound["lower_bound_fraction"] == 0
    assert bound["attained"] is False
    assert next(c for c in result["checks"] if c["id"] == "constraints")["numerical_checks_pass"]


def test_capital_scaling_and_horizon_do_not_create_forecasts():
    problem = example("robert")
    initial = finance.analyze(problem)
    for key in ["capital_cad", "withdrawal_cad", "scenario_loss_limit_cad"]:
        problem[key] *= 7
    problem["horizon_years"] = 19
    scaled = finance.analyze(problem)
    assert scaled["options"][1]["weights"] == pytest.approx(initial["options"][1]["weights"])
    assert scaled["options"][1]["metrics"]["turnover_cad"]["value"] == pytest.approx(
        initial["options"][1]["metrics"]["turnover_cad"]["value"] * 7)
    assert scaled["provenance"]["input_sha256"] != initial["provenance"]["input_sha256"]
    assert not any("forecast" in key for key in scaled["options"][1]["metrics"])


def test_sensitivity_solves_revised_problem_without_changing_baseline():
    result = finance.analyze(example("robert"))
    probe = next(s for s in result["sensitivity"] if s["changes"] == {"withdrawal_cad": 40000})
    assert probe["minimum_reallocated_capital_cad"] == pytest.approx(40000)
    assert probe["baseline_unchanged"]
    assert probe["diagnostics"]["numerical_checks_pass"]
    assert result["inputs"]["withdrawal_cad"] == 30000
    assert result["options"][0]["weights"]["TSLA"] == .25
    assert any("max_asset_weights" in s["changes"] for s in result["sensitivity"])


@pytest.mark.parametrize("updates,field", [
    ({"reserve_policy": "real_instrument_unknown"}, "reserve_policy"),
    ({"scenario_loss_limit_cad": 10}, "scenarios"),
    ({"max_asset_weights": {"NOT_DECLARED": .1}}, "max_asset_weights"),
    ({"clarifications": [{"field": "fees", "question": "Quel coût ?", "blocking": True}]}, "fees"),
])
def test_missing_information_is_explicit(updates, field):
    result = finance.analyze(reserve_problem(**updates))
    assert result["status"] == "missing_input"
    assert result["missing"][0]["field"] == field
    assert result["claims"] == []
    assert_serializable_and_linked(result)


@pytest.mark.parametrize("returns", [{"A": -.2}, {"B": 0}, {}])
def test_missing_scenario_return_is_not_zero_even_for_zero_weight_asset(returns):
    result = finance.analyze(reserve_problem(
        holdings=[{"ticker": "A", "weight": 1}, {"ticker": "B", "weight": 0}],
        scenarios=[{"id": "s", "kind": "hypothetical", "horizon_months": 12, "returns": returns}]))
    assert result["status"] == "missing_input"
    assert "Aucun zéro imputé" in result["missing"][0]["reason"]


def test_scenario_horizon_requires_same_withdrawal_date():
    result = finance.analyze(reserve_problem(
        scenarios=[{"id": "s", "kind": "hypothetical", "horizon_months": 48, "returns": {"A": -.2}}]))
    assert result["status"] == "missing_input"
    assert "horizon_months" in result["missing"][0]["field"]


@pytest.mark.parametrize("updates", [
    {"holdings": [{"ticker": "A", "weight": .7}]},
    {"holdings": [{"ticker": "A", "weight": .5}, {"ticker": "a", "weight": .5}]},
    {"holdings": [{"ticker": "A", "weight": True}]},
    {"holdings": [{"ticker": "A", "weight": -1}, {"ticker": "B", "weight": 2}]},
    {"capital_cad": float("nan")}, {"withdrawal_cad": -1},
    {"max_asset_weights": []}, {"scenarios": {}},
])
def test_invalid_numbers_and_weights_do_not_reach_a_financial_conclusion(updates):
    result = finance.analyze(reserve_problem(**updates))
    assert result["status"] == "error"
    assert result["claims"] == []
    assert_serializable_and_linked(result)


def test_solver_failure_is_technical_and_not_economic_infeasibility(monkeypatch):
    def broken_solver(*args, **kwargs):
        raise RuntimeError("simulated solver unavailability")
    monkeypatch.setattr(finance, "linprog", broken_solver)
    result = finance.analyze(reserve_problem())
    assert result["status"] == "error"
    assert result["options"] == []
    assert result["claims"] == []
    assert result["checks"][0]["id"] == "execution"
    assert_serializable_and_linked(result)


@pytest.mark.parametrize("updates", [
    {"withdrawal_cad": 101},
    {"max_asset_weights": {finance.RESERVE: .2}},
    {"max_asset_weights": {"A": .4, finance.RESERVE: .4}},
    {"withdrawal_cad": 0, "max_asset_weights": {finance.RESERVE: 0},
     "scenario_loss_limit_cad": 10,
     "scenarios": [{"id": "s", "kind": "hypothetical", "horizon_months": 12, "returns": {"A": -.5}}]},
])
def test_infeasible_constraints_never_become_silent_relaxations(updates):
    result = finance.analyze(reserve_problem(**updates))
    assert result["status"] == "infeasible"
    assert all(o["id"] == "baseline" and not o["admissible"] for o in result["options"])
    assert all(c["kind"] == "infeasibility_certificate" for c in result["claims"])
    assert "IIS" in " ".join(result["limitations"])
    assert_serializable_and_linked(result)


def miniature_dataset():
    days = ("2023-01-02", "2023-07-03", "2024-01-02")
    names = ["assets_universe.csv", "prices_daily.csv", "fx_usdcad_daily.csv"]
    return Dataset(
        assets={t: {"ticker": t, "name": t, "currency": currency,
                    "asset_class": "equity", "market": "synthetic"}
                for t, currency in [("CAD", "CAD"), ("USD", "USD")]},
        prices={"CAD": dict(zip(days, [100, 80, 120])),
                "USD": dict(zip(days, [100, 100, 100]))},
        fx=dict(zip(days, [1, 2, 2])), calendar=days,
        files={name: {"sha256": hashlib.sha256(name.encode()).hexdigest(), "rows": 3}
               for name in names},
        sources=[{"file": name, "retrieved_on": "2024-01-03",
                  "source": "test fixture", "source_url": "urn:synthetic:reference"} for name in names],
        directory="synthetic-test-fixture")


def historical_problem(**updates):
    value = example("amira")
    value.update(capital_cad=100, holdings=[{"ticker": "CAD", "weight": 1}],
                 comparison={"ticker": "USD", "target_weight": .5}, knowledge_date="2024-01-03")
    value.update(updates)
    return value


def test_historical_reference_fx_cagr_drawdown_and_adjustment_once(monkeypatch):
    data = miniature_dataset()
    monkeypatch.setattr(finance.datasets, "load_dataset", lambda: data)
    result = finance.analyze(historical_problem())
    assert result["status"] == "conditional"
    baseline, variant = result["options"]
    assert baseline["metrics"]["ending_value_cad"]["value"] == 120
    assert baseline["metrics"]["max_drawdown_pct"]["value"] == -20
    days = (date(2024, 1, 2) - date(2023, 1, 2)).days
    cagr = ((120 / 100) ** (365.2425 / days) - 1) * 100
    assert baseline["metrics"]["cagr_pct"]["value"] == pytest.approx(cagr, abs=1e-6)
    # USD price is flat. Its CAD value doubles through FX; final mixed wealth:
    # 50*(120/100) + 50*((100*2)/(100*1)) = 160.
    assert variant["metrics"]["ending_value_cad"]["value"] == 160
    assert variant["metrics"]["total_return_pct"]["value"] == 60
    assert variant["series"][1]["value"] == 140
    assert result["method"]["metadata"]["end"] == "2024-01-02"
    assert all(s["kind"] == "historical_window" for s in baseline["scenario_results"])
    assert_serializable_and_linked(result)


def test_historical_old_knowledge_date_rejects_newer_acquisition(monkeypatch):
    monkeypatch.setattr(finance.datasets, "load_dataset", miniature_dataset)
    result = finance.analyze(historical_problem(knowledge_date="2023-07-04"))
    assert result["status"] == "missing_input"
    assert result["missing"][0]["field"] == "knowledge_date"
    assert "millésime" in result["missing"][0]["reason"]
    assert result["options"] == []


@pytest.mark.parametrize("failure", ["stale_fx", "no_prior_fx", "missing_price", "missing_vintage"])
def test_historical_missing_or_stale_information_fails_explicitly(monkeypatch, failure):
    data = miniature_dataset()
    if failure == "stale_fx":
        data.fx.clear()
        data.fx["2022-12-01"] = 1
    elif failure == "no_prior_fx":
        data.fx.pop("2023-01-02")
    elif failure == "missing_price":
        data.prices["USD"].pop("2023-07-03")
    else:
        data.sources.clear()
    monkeypatch.setattr(finance.datasets, "load_dataset", lambda: data)
    result = finance.analyze(historical_problem())
    assert result["status"] == "missing_input"
    assert result["claims"] == []
    assert_serializable_and_linked(result)


def test_historical_does_not_ignore_withdrawals():
    result = finance.analyze(historical_problem(withdrawal_cad=1))
    assert result["status"] == "unsupported"
    assert result["missing"][0]["field"] == "withdrawal_cad"


def test_live_starter_example_comparison_and_provenance():
    result = finance.analyze(example("amira"))
    assert result["status"] == "conditional"
    baseline, variant = result["options"]
    assert baseline["metrics"]["total_return_pct"]["value"] == pytest.approx(78.063006)
    assert variant["metrics"]["total_return_pct"]["value"] == pytest.approx(87.496089)
    assert baseline["series"][0]["value"] == variant["series"][0]["value"] == 25000
    assert [p["date"] for p in baseline["series"]] == [p["date"] for p in variant["series"]]
    assert baseline["metrics"]["max_drawdown_pct"]["value"] < 0
    assert variant["weights"]["TSLA"] == .1
    assert result["provenance"]["availability"]["historical_point_in_time_universe"] is False
    root = Path(__file__).resolve().parents[1]
    for code in result["provenance"]["code"]:
        assert hashlib.sha256((root / code["path"]).read_bytes()).hexdigest() == code["sha256"]
    assert result["provenance"]["data"]
    assert result["provenance"]["model_inference_calls"] == 0
    assert_serializable_and_linked(result)


def test_baseline_stress_is_independent_of_withdrawal_and_matches_baseline_losses():
    problem = example("robert")
    first = finance.baseline_stress(problem)
    comparison = finance.analyze(problem)
    problem["withdrawal_cad"] = 40000
    problem["withdrawal_months"] = 24
    problem["max_asset_weights"] = {"TSLA": .01}
    second = finance.baseline_stress(problem)
    assert first["status"] == second["status"] == "conditional"
    assert first["scenario_results"] == second["scenario_results"]
    assert first["provenance"]["input_sha256"] == second["provenance"]["input_sha256"]
    assert set(first["inputs"]) == {"capital_cad", "holdings", "scenarios", "currency"}
    expected = {"actions": 18250, "obligations": 13900}
    for row in first["scenario_results"]:
        assert row["loss_cad"] == pytest.approx(expected[row["id"]])
        other = next(s for s in comparison["options"][0]["scenario_results"] if s["id"] == row["id"])
        assert row["loss_cad"] == pytest.approx(other["loss_cad"])
        assert "wealth_after_withdrawal_cad" not in row
        assert row["units"]["loss_cad"] == "CAD"
        assert row["probability"] is None
    assert first["options"] == []
    assert "admissible" not in first
    assert_serializable_and_linked(first)


def test_baseline_stress_recalculates_on_capital_or_shock_change():
    problem = example("robert")
    initial = finance.baseline_stress(problem)
    problem["capital_cad"] = 200000
    scaled = finance.baseline_stress(problem)
    assert scaled["scenario_results"][0]["loss_cad"] == pytest.approx(36500)
    assert scaled["provenance"]["input_sha256"] != initial["provenance"]["input_sha256"]
    problem["capital_cad"] = 100000
    problem["scenarios"][0]["returns"]["TSLA"] = -.8
    shocked = finance.baseline_stress(problem)
    assert shocked["scenario_results"][0]["loss_cad"] == pytest.approx(25750)
    assert shocked["scenario_results"][1] == initial["scenario_results"][1]
    assert shocked["provenance"]["input_sha256"] != initial["provenance"]["input_sha256"]


@pytest.mark.parametrize("missing", ["active_return", "zero_weight_return", "scenarios", "horizon"])
def test_baseline_stress_missing_information_is_not_imputed(missing):
    problem = example("robert")
    if missing == "active_return":
        problem["scenarios"][1]["returns"].pop("TSLA")
    elif missing == "zero_weight_return":
        problem["holdings"].append({"ticker": "UNSPECIFIED", "weight": 0})
    elif missing == "scenarios":
        problem["scenarios"] = []
    else:
        problem["scenarios"][0].pop("horizon_months")
    result = finance.baseline_stress(problem)
    assert result["status"] == "missing_input"
    assert result["scenario_results"] == []
    assert result["claims"] == []
    assert_serializable_and_linked(result)


def test_baseline_stress_does_not_assume_a_reserve_return_from_unread_policy():
    problem = example("robert")
    problem["holdings"] = [{"ticker": finance.RESERVE, "weight": 1}]
    for scenario in problem["scenarios"]:
        scenario["returns"].pop(finance.RESERVE)
    result = finance.baseline_stress(problem)
    assert result["status"] == "missing_input"
    assert finance.RESERVE in result["missing"][0]["reason"]
    assert "reserve_policy" not in result["inputs"]
