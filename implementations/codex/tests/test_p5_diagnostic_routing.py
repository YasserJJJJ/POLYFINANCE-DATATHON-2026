"""A budget contradiction must not enter a documentary-deepening cycle.

Explicit role/research doubles reproduce the decisions observed in an AWS run.
The store, graph, diagnostic, controls and presentation are production code.
"""
import copy

import pytest

from alphaforge_app.decision.finance import examples
from alphaforge_app.decision.service import DecisionService
from alphaforge_app.decision.tool_contracts import executable_contracts


@pytest.mark.parametrize("requested_decision", ["deepen", "clarify"])
def test_budget_certificate_survives_unresolved_documentary_work(tmp_path, requested_decision):
    facts = copy.deepcopy(examples()[0]["facts"])
    facts["withdrawal_cad"] = 120000
    facts["clarifications"] = [{
        "field": "withdrawal_cad", "question": "Le retrait dépasse le capital.",
        "blocking": True,
    }]
    calls = []

    def researcher(*args, **kwargs):
        calls.append("retrieve")
        return {"evidence": [], "methods": [], "gaps": [], "contradictions": [{
            "code": "unresolved_source", "message": "Source non résolue.",
        }], "receipts": [], "limitations": []}

    def broad_finance(_):
        raise AssertionError("Aucun LP ou calcul de marché n'est admis ici.")

    service = DecisionService(tmp_path, researcher=researcher, finance=broad_finance)

    def role_double(run, task, role, context, *args):
        if role == "agent1":
            return {
                "decision": requested_decision, "reason": "Document manquant.",
                "method_ids": ["reserve-budget-contradiction-v1"], "evidence_ids": [],
                "unresolved": ["Source non résolue."], "issues": [],
            }
        if role == "agent2":
            return {
                "tool": "clarification", "question_addressed": facts["question"],
                "checks_to_inspect": [], "sensitivity_fields": [], "reason": "Document manquant.",
            }
        return None

    service._infer = role_double
    try:
        snapshot = service.create("Question budgétaire.", facts, False, background=False)
        assert calls == ["retrieve"]
        assert [t["role"] for t in snapshot["tasks"]] == ["agent0", "agent1", "agent2", "agent3"]
        review = next(a["content"] for a in snapshot["artifacts"] if a["id"] == "research_review")
        assert review["decision"] == requested_decision
        assert review["blocking_issues"]
        assert review["kernel_routing"]["allocation_permitted"] is False
        assert review["executable_method_ids"] == ["reserve-budget-contradiction-v1"]
        assert review["bibliographic_method_ids"] == []
        result = snapshot["current_analysis"]["content"]
        assert result["status"] == "infeasible"
        assert result["options"] == []
        assert result["checks"][0]["shortfall_cad"] == 20000
        attempts = [a["tool"] for a in snapshot["attempts"]]
        assert "finance.reserve_budget_diagnostic" in attempts
        assert "finance.analyze" not in attempts
        assert "finance.baseline_stress" not in attempts
        view = snapshot["current_view"]["content"]
        assert view["controls"]["arithmetic"]["status"] == "sufficient"
        assert view["controls"]["documentary_grounding"]["status"] == "insufficient"
        assert "Source non résolue." in view["limitations"]
    finally:
        service.pool.shutdown(wait=True)
        service.workflow.close()


def test_diagnostic_contract_is_separate_from_allocation():
    tools = {t["tool"]: t for t in executable_contracts()}
    assert tools["reserve_budget_diagnostic"]["required_checks"] == ["reserve_budget_contradiction"]
    assert tools["reserve_allocation"]["required_checks"] != ["reserve_budget_contradiction"]
    assert "sans allocation" in tools["reserve_budget_diagnostic"]["runtime_result_gate"]
