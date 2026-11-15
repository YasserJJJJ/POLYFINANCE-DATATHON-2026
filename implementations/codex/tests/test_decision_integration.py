"""Executable integration invariants; no real inference in this test suite."""
import copy
from pathlib import Path

import pytest

from alphaforge_app.decision.finance import examples
from alphaforge_app.decision.service import DecisionService, pointer


@pytest.fixture
def services(tmp_path):
    created = []

    def make():
        obj = DecisionService(tmp_path)
        created.append(obj)
        return obj
    yield make
    for obj in created:
        obj.pool.shutdown(wait=True)
        obj.workflow.close()


def test_real_robert_revision_preserves_independent_proof_and_changes_calculations(services):
    s = services()
    ex = examples()[0]
    old = s.create(ex["prompt"], ex["facts"], False, background=False)
    assert old["status"] == "complete", old["runs"][-1]["error"]
    old_analysis = old["current_analysis"]
    old_research = next(a for a in old["artifacts"] if a["id"] == "research" and a["usable"])
    old_baseline = next(a for a in old["artifacts"] if a["id"] == "baseline_stress" and a["usable"])
    new = s.revise(old["id"], "Correction du retrait à 40 000 CAD.", {"withdrawal_cad": 40000},
                   old["revision"], background=False)
    assert new["status"] == "complete", new["runs"][-1]["error"]
    assert new["active_problem"]["withdrawal_cad"] == 40000
    assert new["current_analysis"]["ref"] != old_analysis["ref"]
    assert new["current_analysis"]["hash"] != old_analysis["hash"]
    current_research = next(a for a in new["artifacts"] if a["id"] == "research" and a["usable"])
    assert current_research["ref"] == old_research["ref"]
    assert current_research["hash"] == old_research["hash"]
    baseline = next(a for a in new["artifacts"] if a["id"] == "baseline_stress" and a["usable"])
    assert (baseline["ref"], baseline["hash"]) == (old_baseline["ref"], old_baseline["hash"])
    assert "baseline_stress@1" in new["comparison"]["reused"]
    assert len([a for a in new["attempts"] if a["tool"] == "finance.baseline_stress"]) == 1
    assert new["current_analysis"]["content"]["chain"]["baseline_stress_ref"] == baseline["ref"]
    old_min = next(o for o in old_analysis["content"]["options"] if o["id"] == "minimum_turnover")
    new_min = next(o for o in new["current_analysis"]["content"]["options"] if o["id"] == "minimum_turnover")
    assert old_min["metrics"]["turnover_cad"]["value"] == pytest.approx(30000)
    assert new_min["metrics"]["turnover_cad"]["value"] == pytest.approx(40000)
    assert not s.store.artifact(old["id"], old_analysis["ref"])["usable"]
    assert s.store.artifact(old["id"], old_analysis["ref"])["content"] == old_analysis["content"]
    assert "research@1" in new["comparison"]["reused"]
    assert "analysis@1" in new["comparison"]["invalidated"]
    assert [t["role"] for t in new["tasks"]] == ["agent0", "agent1", "agent2", "agent3"] * 2
    for a in new["artifacts"]:
        for ref in a["input_refs"]:
            assert "@" in ref and not ref.startswith("$")
        if a["type"] == "questions":
            assert not any(str(ref).startswith("$") for n in a["content"]["nodes"] for ref in n["result_refs"])
    # A later explicit correction can return to 30k without overwriting either
    # prior result; this is a new version, not a rollback of history.
    again = s.revise(new["id"], "Correction : le retrait impératif reste 30 000 CAD.",
                     {"withdrawal_cad": 30000}, new["revision"], background=False)
    assert again["status"] == "complete"
    assert again["current_analysis"]["ref"] == "analysis@3"
    assert again["active_problem"]["withdrawal_cad"] == 30000
    changed = s.revise(again["id"], "Capital corrigé à 200 000 CAD.", {"capital_cad": 200000},
                       again["revision"], background=False)
    assert changed["status"] == "complete"
    current = next(a for a in changed["artifacts"] if a["id"] == "baseline_stress" and a["usable"])
    assert current["ref"] == "baseline_stress@2"
    assert current["hash"] != baseline["hash"]
    assert "baseline_stress@1" in changed["comparison"]["invalidated"]


def test_different_historical_problem_uses_actual_data_and_trace(services):
    s = services()
    ex = examples()[1]
    d = s.create(ex["prompt"], ex["facts"], False, background=False)
    assert d["status"] == "complete", d["runs"][-1]["error"]
    analysis = d["current_analysis"]["content"]
    assert analysis["method"]["id"] == "retrospective-comparison-v2"
    assert len(analysis["options"]) == 2
    assert analysis["status"] == "conditional"
    for claim in d["current_view"]["content"]["claims"]:
        original = next(c for c in analysis["claims"] if c["id"] == claim["id"])
        assert claim["text"] == original["text"]
        for ref in claim["result_refs"]:
            pointer(analysis, ref["pointer"])
    assert d["current_view"]["content"]["controls"]["external_validity"]["status"] == "not_established"


def test_free_text_correction_updates_comparison_after_qualification(services):
    s = services()
    ex = examples()[0]
    old = s.create(ex["prompt"], ex["facts"], False, background=False)
    def extracted(run, task, role, context, *args):
        if role != "agent0":
            return None
        return {"updates": [{"field": "withdrawal_cad", "value_json": "40000",
                             "quote": "Le retrait sera de 40 000 CAD.", "origin": "extracted",
                             "rationale": "Correction explicite du montant."}],
                "contradictions": [], "clarifications": [], "interpretation": "Correction du retrait."}
    s._infer = extracted  # Explicit model response fixture; no real inference.
    new = s.revise(old["id"], "Le retrait sera de 40 000 CAD.", {}, old["revision"], background=False)
    assert new["status"] == "complete"
    assert new["active_problem"]["withdrawal_cad"] == 40000
    assert "fact.withdrawal_cad" in new["comparison"]["changed_fields"]
    assert "fact.withdrawal_cad@1" in new["comparison"]["invalidated"]
    assert "fact.withdrawal_cad@1" not in new["comparison"]["reused"]
    assert "baseline_stress@1" in new["comparison"]["reused"]
    assert new["comparison"]["provisional"] is False
    corrected = next(a for a in new["artifacts"] if a["id"] == "fact.withdrawal_cad" and a["usable"])
    assert corrected["content"]["origin"] == "extracted"


def test_interruption_after_commit_is_resumed_in_new_service_without_duplicate_tool(services):
    first = services()
    original_callback = first.workflow.role_callback
    stopped = False

    def interruption(role, state):
        nonlocal stopped
        value = original_callback(role, state)
        if role == "agent2" and not stopped:
            stopped = True
            raise RuntimeError("Controlled interruption after commit before checkpoint")
        return value
    first.workflow.role_callback = interruption
    ex = examples()[0]
    d = first.create(ex["prompt"], ex["facts"], False, background=False)
    assert d["status"] == "error"
    assert d["current_analysis"]
    assert d["current_view"] is None
    old_ref = d["current_analysis"]["ref"]
    second = services()
    resumed = second.resume(d["id"], background=False)
    assert resumed["status"] == "complete", resumed["runs"][-1]["error"]
    assert resumed["current_analysis"]["ref"] == old_ref
    assert len([a for a in resumed["attempts"] if a["tool"] == "finance.analyze"]) == 1
    assert len([a for a in resumed["artifacts"] if a["id"] == "analysis"]) == 1
    assert len([a for a in resumed["artifacts"] if a["id"] == "view"]) == 1


def test_missing_and_unknown_data_are_not_fabricated(services):
    s = services()
    facts = copy.deepcopy(examples()[0]["facts"])
    facts.pop("withdrawal_cad")
    d = s.create("Un retrait est prévu, sans montant indiqué.", facts, False, background=False)
    assert d["status"] == "waiting"
    assert d["active_problem"]["withdrawal_cad"] is None
    assert not any(a["type"] == "analysis" and a["content"]["options"] for a in d["artifacts"])


def test_local_api_preserves_revision_conflict_and_offline_reading(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from alphaforge_app.main import app
    from alphaforge_app.decision import api
    s = DecisionService(tmp_path)
    monkeypatch.setattr(api, "_service", s)
    try:
        client = TestClient(app)
        assert client.get("/api/dossiers/examples").status_code == 200
        d_id, _ = s.store.create("Cas.", {"capital_cad": 100}, use_ai=False)
        response = client.post(f"/api/dossiers/{d_id}/revise",
                               json={"message": "Correction", "changes": {"capital_cad": 200},
                                     "intent": "replace", "base_revision": 0})
        assert response.status_code == 409
        assert client.get(f"/api/dossiers/{d_id}/export").status_code == 200
        assert client.get("/api/dossiers/missing").status_code == 404
        assert client.post(f"/api/dossiers/{d_id}/display", json={"view_ref": "view@1"}).status_code == 409
    finally:
        s.pool.shutdown(wait=True)
        s.workflow.close()
