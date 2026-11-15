"""P5 independent financial review: CSV and vertex oracles, no model doubles."""
import copy
import json
import runpy
from pathlib import Path

import pytest
from pydantic import ValidationError

from alphaforge_app.decision import finance
from alphaforge_app.decision.models import ProblemSpec, RevisionRequest

ROOT = Path(__file__).resolve().parents[1]
ORACLE = runpy.run_path(str(ROOT / "docs/defense/proofs/finance_review.py"))


def example(name):
    return ORACLE["example"](name)


@pytest.mark.parametrize("changes", [
    {}, {"withdrawal_cad": 40000}, {"scenario_loss_limit_cad": 1000},
    {"max_asset_weights": {"TSLA": .01}},
])
def test_lp_minimum_matches_independent_weight_space_vertex_enumeration(changes):
    problem = example("robert")
    problem.update(changes)
    result = finance.analyze(problem)
    oracle = ORACLE["vertex_minimum"](problem)
    assert result["status"] == "conditional"
    assert result["options"][1]["metrics"]["turnover_cad"]["value"] == pytest.approx(
        oracle["minimum"]["turnover_fraction"] * problem["capital_cad"], abs=.001)
    for option in result["options"][1:]:
        independently = ORACLE["reserve_metrics"](problem, option["weights"])
        assert independently["max_violation_fraction"] <= 1e-8
        assert independently["turnover_cad"] == pytest.approx(
            result["options"][1]["metrics"]["turnover_cad"]["value"], abs=.002)
        for scenario in option["scenario_results"]:
            assert scenario["loss_cad"] == pytest.approx(independently["losses_cad"][scenario["id"]])


def test_impossible_reserve_certificate_survives_an_unresolved_question():
    problem = example("robert")
    problem.update(withdrawal_cad=120000, holdings=[], clarifications=[
        {"field": "withdrawal_cad", "question": "Le retrait dépasse le capital.", "blocking": True}])
    result = finance.analyze(problem)
    assert result["status"] == "infeasible"
    assert result["options"] == []
    proof = result["checks"][0]
    assert proof["certified"] and proof["independent_of_solver"]
    assert proof["shortfall_cad"] == 20000
    assert "holdings" not in proof["minimal_input_fields"]
    assert result["inputs"]["clarifications"] == problem["clarifications"]
    for reference in result["claims"][0]["result_refs"]:
        value = result
        for token in reference["pointer"].lstrip("/").split("/"):
            value = value[int(token)] if isinstance(value, list) else value[token]
        assert isinstance(value, (int, float))


@pytest.mark.parametrize("changes", [
    {"reserve_policy": "real_instrument_unknown"}, {"currency": "USD"},
    {"objective": "compare_historical"}, {"capital_cad": True}, {"withdrawal_cad": float("inf")},
])
def test_minimal_certificate_never_changes_the_economic_model(changes):
    problem = example("robert")
    problem["withdrawal_cad"] = 120000
    problem.update(changes)
    assert finance.reserve_budget_certificate(problem) is None


@pytest.mark.parametrize("name,weights", [
    ("baseline", {"SPY": .45, "XIU.TO": .30, "TSLA": .25}),
    ("target_variant", {"SPY": .54, "XIU.TO": .36, "TSLA": .10}),
])
def test_amira_and_final_export_match_independent_raw_csv_oracle(name, weights):
    oracle = ORACLE["raw_csv_history"](weights)
    result = finance.analyze(example("amira"))
    saved = json.loads((ROOT / "docs/implementation/proofs/final_demo/amira-initial.json").read_text())
    for analysis in [result, saved["current_analysis"]["content"]]:
        option = next(o for o in analysis["options"] if o["id"] == name)
        for metric, expected in oracle["metrics"].items():
            tolerance = .0051 if metric.endswith("_cad") else 5.1e-7
            assert option["metrics"][metric]["value"] == pytest.approx(expected, rel=0, abs=tolerance)
        assert [p["date"] for p in option["series"]] == oracle["days"]
        assert [p["value"] for p in option["series"]] == pytest.approx(oracle["wealth"], rel=0, abs=.0051)
    assert (oracle["start"], oracle["end"], oracle["observations"]) == ("2021-11-12", "2026-11-12", 1228)
    assert oracle["fx_carried_dates"] == 10
    assert oracle["max_fx_age_days"] == 3


def test_raw_csv_oracle_distinguishes_fx_and_rebalancing_errors():
    weights = {"SPY": .45, "XIU.TO": .30, "TSLA": .25}
    correct = ORACLE["raw_csv_history"](weights)["metrics"]["ending_value_cad"]
    no_fx = ORACLE["raw_csv_history"](weights, ignore_fx=True)["metrics"]["ending_value_cad"]
    rebalanced = ORACLE["raw_csv_history"](weights, rebalance=True)["metrics"]["ending_value_cad"]
    assert abs(correct - no_fx) > 100
    assert abs(correct - rebalanced) > 100


@pytest.mark.parametrize("policy,status", [
    (None, "missing_input"),
    ({}, "missing_input"),
    ({"redistribution": "proportional_other_holdings"}, "missing_input"),
    ({"redistribution": "other", "window": {"kind": "all_common_available"}}, "unsupported"),
    ({"redistribution": "proportional_other_holdings", "window": {
        "kind": "specified_window", "start_date": "2024-01-01", "end_date": "2025-01-01"}}, "unsupported"),
    ({"redistribution": "proportional_other_holdings", "window": {
        "kind": "all_common_available", "start_date": "2024-01-01"}}, "unsupported"),
])
def test_historical_policy_is_explicit_and_unsupported_conventions_are_rejected(policy, status):
    problem = example("amira")
    problem["historical_policy"] = policy
    result = finance.analyze(problem)
    assert result["status"] == status
    assert result["options"] == [] and result["claims"] == []
    assert result["missing"][0]["field"].startswith("historical_policy")


def test_old_problem_remains_readable_but_needs_requalification_before_new_calculation():
    problem = example("amira")
    problem.pop("historical_policy")
    parsed = ProblemSpec.model_validate(problem).model_dump()
    assert parsed["historical_policy"] is None
    assert finance.analyze(parsed)["status"] == "missing_input"


def test_declared_long_horizon_is_not_used_as_a_historical_forecast():
    problem = example("amira")
    initial = finance.analyze(problem)
    changed = copy.deepcopy(problem)
    changed["horizon_years"] = 40
    revised = finance.analyze(changed)
    assert initial["options"] == revised["options"]
    assert initial["provenance"]["input_sha256"] != revised["provenance"]["input_sha256"]
    assert any("horizon" in limit.lower() for limit in revised["limitations"])


def test_historical_initial_caps_are_checked_even_if_neither_option_is_admissible():
    problem = example("amira")
    problem["max_asset_weights"] = {"TSLA": .01}
    result = finance.analyze(problem)
    assert result["status"] == "conditional"  # Historical values, not feasible allocation selection.
    assert all(not o["admissible"] for o in result["options"])
    assert all(o["violations"][0]["constraint"] == "asset_cap:TSLA" for o in result["options"])


@pytest.mark.parametrize("changes", [
    {"withdrawal_cad": 100}, {"scenario_loss_limit_cad": 1000},
    {"scenarios": [{"id": "s", "kind": "hypothetical", "label": "s",
                    "horizon_months": 12, "returns": {"SPY": -.2, "XIU.TO": -.2, "TSLA": -.5}}]},
])
def test_historical_comparison_does_not_ignore_structured_cashflow_or_loss_constraints(changes):
    problem = example("amira")
    problem.update(changes)
    result = finance.analyze(problem)
    assert result["status"] == "unsupported"
    assert result["options"] == [] and result["claims"] == []


@pytest.mark.parametrize("changes", [
    {"capital_cad": True}, {"withdrawal_cad": True}, {"withdrawal_months": True},
    {"horizon_years": True}, {"scenario_loss_limit_cad": False},
    {"max_asset_weights": {"TSLA": False}},
    {"holdings": [{"ticker": "TSLA", "weight": True}]},
    {"comparison": {"ticker": "TSLA", "target_weight": False}},
    {"scenarios": [{"id": "s", "label": "s", "kind": "hypothetical",
                    "horizon_months": True, "returns": {"TSLA": -.2}}]},
    {"scenarios": [{"id": "s", "label": "s", "kind": "hypothetical",
                    "horizon_months": 12, "returns": {"TSLA": False}}]},
])
def test_boolean_financial_inputs_are_rejected_before_pydantic_coercion(changes):
    problem = example("robert")
    problem.update(changes)
    with pytest.raises(ValidationError, match="booléen"):
        ProblemSpec.model_validate(problem)


def test_valid_integer_float_and_boolean_fields_remain_accepted():
    problem = example("robert")
    problem["capital_cad"] = 100000
    problem["withdrawal_cad"] = 30000.0
    problem["clarifications"] = [{"field": "x", "question": "À préciser.", "blocking": True}]
    parsed = ProblemSpec.model_validate(problem).model_dump()
    assert parsed["capital_cad"] == 100000.0
    assert parsed["withdrawal_cad"] == 30000.0
    assert parsed["clarifications"][0]["blocking"] is True
    assert RevisionRequest(message="Révision", base_revision=1).base_revision == 1
    with pytest.raises(ValidationError, match="booléen"):
        RevisionRequest(message="Révision", base_revision=True)


@pytest.mark.parametrize("decision", ["deepen", "clarify", "calculate_conditionally"])
def test_budget_routing_preserves_documentary_review_and_never_calls_allocation_tools(
        tmp_path, monkeypatch, decision):
    """Scripted control arm only: no model client, AWS receipt or real source."""
    from alphaforge_app.decision.service import DecisionService

    def forbidden(*args, **kwargs):
        raise AssertionError("Un outil d'allocation ou de marché ne doit pas être appelé.")

    class ScriptedReviewService(DecisionService):
        def _infer(self, run, task_id, role, context, output_schema, instructions):
            assert run["request"]["use_ai"] is False
            if role == "agent1":
                return {
                    "evidence_ids": [], "method_ids": [],
                    "decision": decision, "reason": "Avis documentaire scripté pour test.",
                    "unresolved": ["Conflit documentaire de la fixture."], "issues": [],
                }
            return None

    def scripted_research(*args, **kwargs):
        return {
            "evidence": [], "methods": [], "gaps": [{"code": "fixture_gap", "message": "Lacune de test."}],
            "contradictions": [{"code": "fixture_conflict", "message": "Conflit documentaire de la fixture."}],
            "receipts": [], "limitations": [],
        }

    monkeypatch.setattr(finance, "linprog", forbidden)
    monkeypatch.setattr(finance, "baseline_stress", forbidden)
    monkeypatch.setattr(finance.datasets, "load_dataset", forbidden)
    service = ScriptedReviewService(tmp_path, finance=forbidden, researcher=scripted_research)
    try:
        problem = example("robert")
        problem.update(withdrawal_cad=120000, holdings=[], scenarios=[], clarifications=[
            {"field": "capital_cad", "question": "Confirmer ce capital déclaré.", "blocking": True}])
        dossier = service.create("Contrôle scripté, aucune inférence.", problem, use_ai=False, background=False)
        assert dossier["status"] == "complete"
        assert dossier["current_analysis"]["content"]["status"] == "infeasible"
        view = dossier["current_view"]["content"]
        assert view["options"] == [] and view["ai_used"] is False
        assert view["research_review"]["decision"] == decision
        assert view["research_review"]["kernel_routing"]["requested_decision"] == decision
        assert view["research_review"]["kernel_routing"]["allocation_permitted"] is False
        assert view["documentary_issues"][0]["status"] == "unresolved"
        assert view["controls"]["documentary_grounding"]["status"] == "insufficient"
        assert view["controls"]["mandate"]["status"] == "insufficient"
        assert view["questions"][0]["field"] == "capital_cad"
        tools = [a["tool"] for a in dossier["attempts"]]
        assert "finance.reserve_budget_diagnostic" in tools
        assert not any(t in tools for t in ["finance.analyze", "finance.baseline_stress", "bedrock.converse"])
    finally:
        service.pool.shutdown(wait=True)
        service.workflow.close()


@pytest.mark.parametrize("changes", [
    {"withdrawal_cad": 100000}, {"withdrawal_cad": 99999},
    {"reserve_policy": "real_instrument_unknown"}, {"reserve_policy": None},
    {"currency": "USD"}, {"decision_type": "historical_comparison"},
    {"objective": "compare_historical"}, {"capital_cad": True},
    {"capital_cad": 0}, {"capital_cad": 1e13}, {"withdrawal_cad": float("nan")},
])
def test_bounded_budget_tool_cannot_be_used_outside_its_domain(changes):
    problem = example("robert")
    problem["withdrawal_cad"] = 120000
    problem.update(changes)
    assert finance.reserve_budget_diagnostic_applicable(problem) is False
    with pytest.raises(ValueError, match="hors domaine"):
        finance.analyze_budget_diagnostic(problem)
