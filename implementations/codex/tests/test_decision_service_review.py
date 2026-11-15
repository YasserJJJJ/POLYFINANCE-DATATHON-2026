"""Independent service contracts. All model responses here are test doubles."""

import copy
import json

import pytest

from alphaforge_app.bedrock import BedrockError
from alphaforge_app.decision import service as service_module
from alphaforge_app.decision.service import DecisionService


FACTS = {
    "decision_type": "reserve_allocation",
    "currency": "CAD",
    "capital_cad": 100,
    "withdrawal_cad": 30,
    "withdrawal_months": 12,
    "objective": "minimize_reallocated_capital",
    "reserve_policy": "abstract_nominal",
    "holdings": [{"ticker": "A", "weight": 1.0}],
    "scenarios": [{"id": "shock", "label": "Fictif", "kind": "hypothetical",
                   "horizon_months": 12, "returns": {"A": -0.1}}],
    "scenario_loss_limit_cad": 20,
}


class ModelDouble:
    model = "global.openai.gpt-6-astra"

    def __init__(self, override=None):
        self.calls = []
        self.override = override

    def generate(self, messages, **kwargs):
        role = kwargs["schema_name"].split("_", 1)[0]
        context = json.loads(messages[-1]["content"])
        self.calls.append({"role": role, "context": context})
        values = {
            "agent0": {"updates": [], "contradictions": [], "clarifications": [],
                       "interpretation": "Fixture : seuls les faits structurés."},
            "agent1": {"evidence_ids": ["source-fixture"], "method_ids": [],
                       "unresolved": [], "decision": "calculate_conditionally", "reason": "Fixture"},
            "agent2": {"tool": "reserve_allocation", "question_addressed": "Fixture",
                       "checks_to_inspect": [], "sensitivity_fields": [], "reason": "Fixture"},
            "agent3": {"claim_order": ["claim-fixture"], "emphasis": "conditions",
                       "detail_level": "standard", "follow_up_fields": [], "reason": "Fixture"},
        }
        value = values[role]
        if self.override:
            self.override(role, value, context)
        return {
            "parsed": value, "request_id": f"test-double-{len(self.calls)}",
            "provider": "test_double_no_inference",
            "model": self.model, "usage": {"total_tokens": 0},
        }


def research_double(problem, **kwargs):
    return {
        "evidence": [{"id": "source-fixture", "known_at": "2026-11-15",
                      "source": {"url": "https://example.org/fixture", "title": "Test fixture"},
                      "reading_level": "targeted_passages", "passage": "Fixture only."}],
        "methods": [], "gaps": [{"code": "not_a_real_instrument", "message": "Fixture abstraite."}],
        "contradictions": [], "receipts": [], "limitations": [],
    }


def finance_double(problem):
    return {
        "status": "conditional", "method": {"id": "test-fixture", "version": 1},
        "inputs": copy.deepcopy(problem), "options": [],
        "checks": [{"id": "fixture", "status": "sufficient", "method": "test fixture"}],
        "claims": [{"id": "claim-fixture", "text": "Résultat de la fixture sous hypothèses.",
                    "result_refs": []}],
        "limitations": ["Simulation du contrat de service uniquement."],
        "missing": [], "provenance": {"fixture": True},
    }


@pytest.fixture
def make_service(tmp_path):
    created = []

    def make(**kwargs):
        obj = DecisionService(
            tmp_path / str(len(created)),
            client=kwargs.pop("client", ModelDouble()),
            finance=kwargs.pop("finance", finance_double),
            researcher=kwargs.pop("researcher", research_double),
            **kwargs,
        )
        created.append(obj)
        return obj

    yield make
    for service in created:
        service.pool.shutdown(wait=True)
        service.workflow.close()


def test_four_roles_have_separate_model_calls_commits_and_observed_inputs(make_service):
    client = ModelDouble()
    service = make_service(client=client)
    snapshot = service.create("Exercice fictif explicite.", FACTS, background=False)
    assert snapshot["status"] == "complete"
    assert [x["role"] for x in client.calls] == ["agent0", "agent1", "agent2", "agent3"]
    tasks = snapshot["tasks"]
    assert [t["role"] for t in tasks] == ["agent0", "agent1", "agent2", "agent3"]
    assert all(t["status"] == "complete" and t["output_refs"] for t in tasks)
    assert "request@1" in tasks[0]["read_set"]
    assert "problem@1" in tasks[1]["read_set"]
    assert {"problem@1", "research@1", "research_review@1"} <= set(tasks[2]["read_set"])
    assert {"analysis@1", "analysis_review@1"} <= set(tasks[3]["read_set"])
    assert client.calls[1]["context"]["documentary_results"] == service.store.artifact(
        snapshot["id"], "research@1"
    )["content"]
    assert snapshot["current_view"]["content"]["human_acceptance"] is None


def test_structured_aws_failure_survives_to_run_and_retries_only_failed_role(make_service):
    fail_once = True

    def override(role, value, context):
        nonlocal fail_once
        if role == "agent2" and fail_once:
            fail_once = False
            raise BedrockError("Session expirée de la fixture.", code="ExpiredToken",
                               request_id="aws-request-fixture", retryable=False)

    client = ModelDouble(override)
    service = make_service(client=client)
    failed = service.create("Exercice.", FACTS, background=False)
    assert failed["status"] == "error"
    assert failed["current_analysis"] is None
    assert failed["current_view"] is None
    error = failed["runs"][-1]["error"]
    assert error["code"] == "ExpiredToken"
    assert error["request_id"] == "aws-request-fixture"
    resumed = service.resume(failed["id"], background=False)
    assert resumed["status"] == "complete"
    assert [x["role"] for x in client.calls] == ["agent0", "agent1", "agent2", "agent2", "agent3"]
    assert any(a["status"] == "error" for a in resumed["attempts"])


def test_agent2_clarification_does_not_execute_the_declined_finance_tool(make_service):
    calls = []

    def override(role, value, context):
        if role == "agent2":
            value.update(tool="clarification", reason="Le périmètre doit être clarifié.")

    def finance(problem):
        calls.append(problem)
        return finance_double(problem)

    service = make_service(client=ModelDouble(override), finance=finance)
    snapshot = service.create("Exercice.", FACTS, background=False)
    assert not calls
    assert snapshot["status"] == "waiting"
    assert not any(a["tool"] == "finance.analyze" for a in snapshot["attempts"])


def test_agent1_deepen_performs_a_bounded_new_search_before_analysis(make_service):
    searches = []
    review_count = 0

    def researcher(problem, **kwargs):
        searches.append({"problem": copy.deepcopy(problem), **kwargs})
        return research_double(problem)

    def override(role, value, context):
        nonlocal review_count
        if role == "agent1":
            review_count += 1
            if review_count == 1:
                value.update(decision="deepen", reason="Rechercher les conditions de liquidité.",
                             unresolved=["Conditions de liquidité non établies."])

    service = make_service(client=ModelDouble(override), researcher=researcher)
    snapshot = service.create("Exercice.", FACTS, background=False)
    assert len(searches) >= 2
    assert len(searches) <= 3
    assert snapshot["status"] in {"complete", "waiting"}


def test_nested_extraction_cannot_introduce_unquoted_weights(make_service):
    prompt = "Je souhaite comparer mon portefeuille."
    facts = {k: v for k, v in FACTS.items() if k != "holdings"}

    def override(role, value, context):
        if role == "agent0":
            value["updates"] = [{
                "field": "holdings",
                "value_json": '[{"ticker":"INVENTED","weight":0.731}]',
                "quote": prompt, "origin": "extracted", "rationale": "Fixture adversariale.",
            }]

    service = make_service(client=ModelDouble(override))
    snapshot = service.create(prompt, facts, background=False)
    assert snapshot["active_problem"]["holdings"] == []
    assert snapshot["active_problem"]["clarifications"]
    assert not any(
        a["id"] == "fact.holdings" and a["content"]["value"] == [{"ticker": "INVENTED", "weight": 0.731}]
        for a in snapshot["artifacts"]
    )


def test_persisted_local_dossiers_can_be_opened_without_aws_session(tmp_path, monkeypatch):
    attempts = []

    def no_aws():
        attempts.append(True)
        raise BedrockError("Session expirée.", code="ExpiredToken", request_id="fixture")

    monkeypatch.setattr(service_module, "BedrockClient", no_aws)
    service = DecisionService(tmp_path / "offline", finance=finance_double, researcher=research_double)
    try:
        assert service.store.list() == []
        assert attempts == []
    finally:
        service.pool.shutdown(wait=True)
        service.workflow.close()


def test_agent1_cannot_select_a_method_identifier_absent_from_research(make_service):
    def override(role, value, context):
        if role == "agent1":
            value["method_ids"] = ["fabricated-method"]

    service = make_service(client=ModelDouble(override))
    snapshot = service.create("Exercice.", FACTS, background=False)
    review = service.store.artifact(snapshot["id"], "research_review@1")["content"]
    assert "fabricated-method" not in review["method_ids"]


def test_explanation_research_tracks_the_asked_topic_on_revision(make_service):
    searches = []

    def researcher(problem, **kwargs):
        searches.append(copy.deepcopy(problem))
        return research_double(problem)

    def override(role, value, context):
        if role == "agent2":
            value["tool"] = "clarification"

    service = make_service(client=ModelDouble(override), researcher=researcher)
    first_question = "Expliquez la CVaR et ses hypothèses."
    first = service.create(
        first_question,
        {"decision_type": "explanation", "question": first_question,
         "objective": "explain", "currency": "CAD"},
        background=False,
    )
    assert first_question == searches[0]["question"]
    second_question = "Expliquez plutôt le ratio de Sharpe."
    revised = service.revise(
        first["id"], second_question, {"question": second_question},
        first["revision"], background=False,
    )
    assert len(searches) >= 2
    assert searches[-1]["question"] == second_question
    assert any(
        a["id"] == "research" and a["version"] > 1 for a in revised["artifacts"]
    )
