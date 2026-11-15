"""Independent transaction-contract review; no live model or external calls."""
import copy
import json
from types import SimpleNamespace

import pytest

from alphaforge_app.decision.models import ChangeSet
from alphaforge_app.decision.store import Conflict, Store


@pytest.fixture
def state(tmp_path):
    store = Store(tmp_path / "review")
    dossier, run = store.create("Exemple de transaction", {"capital_cad": 100, "currency": "CAD"}, False)
    return store, dossier, run


def change(store, run, role, step, reads, writes, next_role=None, status="running"):
    task, cached = store.begin_task(run, role, step, reads)
    assert cached is None
    return ChangeSet(run_id=run, task_id=task, role=role, read_set=reads,
                     writes=writes, next_role=next_role, status=status,
                     reason="Revue indépendante de contrat.")


def write(ident, type_, refs, content=None):
    return {"id": ident, "type": type_, "input_refs": refs, "content": content or {"test": True}}


def completed_pipeline(store, run):
    steps = [
        ("agent0", ["request@1", "fact.capital_cad@1"], "problem", "problem", "agent1"),
        ("agent1", ["problem@1", "fact.currency@1"], "research", "research", "agent2"),
        ("agent2", ["problem@1", "research@1"], "analysis", "analysis", "agent3"),
        ("agent3", ["analysis@1"], "view", "view", None),
    ]
    for i, (role, reads, ident, type_, next_role) in enumerate(steps):
        # Research in this fixture has an explicit currency-only scope.
        refs = ["fact.currency@1"] if role == "agent1" else reads
        store.commit(change(store, run, role, i, reads, [write(ident, type_, refs)],
                            next_role, "complete" if next_role is None else "running"))


def test_logical_analysis_cannot_be_created_as_an_agent0_assertion(state):
    store, dossier, run = state
    before = store.snapshot(dossier)["revision"]
    cs = change(store, run, "agent0", 0, ["request@1"],
                [write("analysis", "assertion", ["request@1"])])
    with pytest.raises(Conflict):
        store.commit(cs)
    snapshot = store.snapshot(dossier)
    assert snapshot["revision"] == before
    assert snapshot["current_analysis"] is None


def test_staged_output_cannot_rely_on_a_head_invalidated_in_same_commit(state):
    store, dossier, run = state
    before = store.snapshot(dossier)["revision"]
    cs = change(store, run, "agent0", 0, ["request@1", "fact.capital_cad@1"], [
        write("fact.capital_cad", "assertion", ["request@1"],
              {"field": "capital_cad", "value": 200, "origin": "assumed"}),
        write("problem", "problem", ["fact.capital_cad@1"], {"capital_cad": 100}),
    ])
    with pytest.raises(Conflict):
        store.commit(cs)
    snapshot = store.snapshot(dossier)
    assert snapshot["revision"] == before
    assert store.artifact(dossier, "fact.capital_cad@1")["usable"]
    assert snapshot["active_problem"] is None


def test_staged_new_dependency_resolves_to_new_version_atomically(state):
    store, dossier, run = state
    cs = change(store, run, "agent0", 0, ["request@1", "fact.capital_cad@1"], [
        write("fact.capital_cad", "assertion", ["request@1"],
              {"field": "capital_cad", "value": 200, "origin": "assumed"}),
        write("problem", "problem", ["$fact.capital_cad"], {"capital_cad": 200}),
        write("questions.agent0", "questions", ["$problem"],
              {"nodes": [{"result_refs": ["$problem"]}]}),
    ], "agent1")
    saved = store.commit(cs)
    assert saved["output_refs"] == ["fact.capital_cad@2", "problem@1", "questions.agent0@1"]
    assert store.artifact(dossier, "fact.capital_cad@1")["usable"] is False
    new = store.artifact(dossier, "problem@1")
    assert new["usable"]
    assert new["input_refs"] == ["fact.capital_cad@2"]
    question = store.artifact(dossier, "questions.agent0@1")
    assert question["content"]["nodes"][0]["result_refs"] == ["problem@1"]


def test_commit_cannot_add_unobserved_dependency(state):
    store, dossier, run = state
    cs = change(store, run, "agent0", 0, ["request@1"],
                [write("problem", "problem", ["fact.capital_cad@1"])])
    with pytest.raises(Conflict):
        store.commit(cs)
    assert store.snapshot(dossier)["active_problem"] is None


def test_read_set_cannot_be_changed_by_worker(state):
    store, dossier, run = state
    cs = change(store, run, "agent0", 0, ["request@1", "fact.capital_cad@1"],
                [write("problem", "problem", ["request@1"])])
    cs.read_set = ["request@1"]
    with pytest.raises(Conflict):
        store.commit(cs)
    assert store.snapshot(dossier)["active_problem"] is None


def test_correction_hides_old_conclusions_immediately_and_reuses_independent_evidence(state):
    store, dossier, run = state
    completed_pipeline(store, run)
    old = store.snapshot(dossier)
    analysis_hash = old["current_analysis"]["hash"]
    _, new_run = store.revise(dossier, "Capital corrigé", {"capital_cad": 200}, old["revision"])
    updated = store.snapshot(dossier)
    assert updated["active_run_id"] == new_run
    assert updated["active_problem"] is None
    assert updated["current_analysis"] is None
    assert updated["current_view"] is None
    assert store.artifact(dossier, "analysis@1")["hash"] == analysis_hash
    assert store.artifact(dossier, "analysis@1")["usable"] is False
    assert store.artifact(dossier, "research@1")["usable"]
    assert updated["comparison"]["before"] == old["current_analysis"]["content"]
    assert updated["comparison"]["after"] is None
    with pytest.raises(Conflict):
        store.record_display(dossier, "view@1")


def test_late_result_cannot_publish_after_correction(state):
    store, dossier, run = state
    cs = change(store, run, "agent0", 0, ["request@1"],
                [write("problem", "problem", ["request@1"])], "agent1")
    revision = store.snapshot(dossier)["revision"]
    _, new_run = store.revise(dossier, "Capital corrigé", {"capital_cad": 200}, revision)
    with pytest.raises(Conflict):
        store.commit(cs)
    updated = store.snapshot(dossier)
    assert updated["active_run_id"] == new_run
    assert updated["active_problem"] is None


def test_superseded_run_cannot_start_a_new_task(state):
    store, dossier, run = state
    revision = store.snapshot(dossier)["revision"]
    store.revise(dossier, "Capital corrigé", {"capital_cad": 200}, revision)
    with pytest.raises(Conflict):
        store.begin_task(run, "agent0", 0, ["request@1"])
    old = next(r for r in store.snapshot(dossier)["runs"] if r["id"] == run)
    assert old["status"] == "superseded"


def test_completed_commit_is_reused_after_store_reopen_without_new_revision(state):
    store, dossier, run = state
    reads = ["request@1", "fact.capital_cad@1"]
    cs = change(store, run, "agent0", 0, reads,
                [write("problem", "problem", reads)], "agent1")
    saved = store.commit(cs)
    revision = store.snapshot(dossier)["revision"]
    reopened = Store(store.root)
    task_id, cached = reopened.begin_task(run, "agent0", 0, reads)
    assert cached == saved
    assert reopened.committed_task(task_id) == saved
    assert reopened.commit(cs) == saved
    assert reopened.snapshot(dossier)["revision"] == revision


def test_variant_is_separate_and_preserves_parent_and_origin_revision(state):
    store, dossier, run = state
    completed_pipeline(store, run)
    before = copy.deepcopy(store.snapshot(dossier))
    variant, new_run = store.revise(dossier, "Variante 200", {"capital_cad": 200},
                                    before["revision"], "variant")
    assert variant != dossier
    parent = store.snapshot(dossier)
    assert parent["revision"] == before["revision"]
    assert parent["current_analysis"]["hash"] == before["current_analysis"]["hash"]
    assert parent["current_view"]["hash"] == before["current_view"]["hash"]
    child = store.snapshot(variant)
    assert child["active_run_id"] == new_run
    assert child["current_analysis"] is None
    assert store.artifact(variant, "fact.capital_cad@1")["content"]["value"] == 200
    assert store.artifact(variant, "fact.currency@1")["content"]["value"] == "CAD"


def test_display_event_is_separate_from_acceptance_and_financial_revision(state):
    store, dossier, run = state
    completed_pipeline(store, run)
    before = store.snapshot(dossier)
    event_id = store.record_display(dossier, "view@1")
    after = store.snapshot(dossier)
    assert after["revision"] == before["revision"]
    event = next(e for e in after["events"] if e["id"] == event_id)
    assert event["kind"] == "view_displayed"
    assert event["payload"] == {"view_ref": "view@1", "accepted": False}


def test_successful_operation_receipt_is_reused_after_restart(state):
    store, dossier, run = state
    task, _ = store.begin_task(run, "agent0", 0, ["request@1"])
    calls = []
    def execute():
        calls.append(1)
        return {"request_id": "test-only", "value": 5}
    first = store.operation(task, "agent0", "test_tool", {"x": 2}, execute)
    second = Store(store.root).operation(task, "agent0", "test_tool", {"x": 2}, execute)
    assert first == second
    assert len(calls) == 1
    assert len(store.snapshot(dossier)["attempts"]) == 1


def test_qualification_cannot_adopt_unquoted_numbers_nested_in_holdings(tmp_path):
    from alphaforge_app.decision.service import DecisionService
    service = DecisionService.__new__(DecisionService)
    service.store = Store(tmp_path / "qualification")
    dossier, run_id = service.store.create("Comparer mon portefeuille.", {}, True)
    run, _, heads = service.store.context(run_id)
    response = {
        "updates": [{
            "field": "holdings",
            "value_json": json.dumps([{"ticker": "TSLA", "weight": .5},
                                      {"ticker": "SPY", "weight": .5}]),
            "quote": "Comparer mon portefeuille.", "origin": "extracted",
            "rationale": "Injection contrôlée de nombres non déclarés pour le test.",
        }],
        "contradictions": [], "clarifications": [], "interpretation": "Réponse simulée de test.",
    }
    service._infer = lambda *args, **kwargs: copy.deepcopy(response)
    result = service._agent0(run, "unused-test-task", heads, {"step_index": 0})
    assert not any(w.id == "fact.holdings" for w in result["writes"])
    problem = next(w.content for w in result["writes"] if w.id == "problem")
    assert any(c["field"] == "holdings" and c["blocking"] for c in problem["clarifications"])


def test_agent2_clarification_choice_does_not_execute_financial_calculation():
    from alphaforge_app.decision.finance import examples
    from alphaforge_app.decision.service import DecisionService
    service = DecisionService.__new__(DecisionService)
    service.store = SimpleNamespace(operation=lambda task, role, tool, args, execute: execute())
    calls = []
    def financial_calculation(problem):
        calls.append(problem)
        return {"status": "conditional", "method": {}, "claims": [], "checks": [], "options": []}
    service.finance = financial_calculation
    service._infer = lambda *args, **kwargs: {
        "tool": "clarification", "question_addressed": "Convention encore ambiguë.",
        "checks_to_inspect": [], "sensitivity_fields": [],
        "reason": "Ne pas calculer avant qualification de cette convention.",
    }
    problem = examples()[0]["facts"]
    heads = {
        "problem": {"ref": "problem@1", "type": "problem", "content": problem},
        "research": {"ref": "research@1", "type": "research", "content": {"methods": [], "gaps": []}},
        "research_review": {"ref": "research_review@1", "type": "review", "content": {}},
    }
    result = service._agent2({"request": {"use_ai": True}}, "unused-test-task", heads, {"step_index": 2})
    assert calls == []
    analysis = next(w.content for w in result["writes"] if w.id == "analysis")
    assert analysis["status"] not in {"complete", "conditional"}
