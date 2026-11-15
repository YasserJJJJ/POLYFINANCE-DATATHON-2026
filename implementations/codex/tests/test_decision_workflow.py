import json
import sqlite3

import pytest
from langsmith.run_helpers import get_tracing_context

from alphaforge_app.decision.workflow import DecisionWorkflow


def _next(role, state):
    index = int(role[-1])
    return {
        "step_index": state["step_index"] + 1,
        "status": "complete" if index == 3 else "running",
        "next_role": None if index == 3 else f"agent{index + 1}",
    }


def test_resume_after_process_restart_preserves_completed_roles(tmp_path):
    calls = []

    def fail(role, state):
        calls.append(role)
        if role == "agent2":
            raise OSError("injected outage")
        return _next(role, state)

    path = tmp_path / "checkpoint.sqlite"
    first = DecisionWorkflow(path, fail)
    failed = first.run("R1", {"dossier_id": "D1"})
    assert failed["status"] == "error"
    assert failed["current_role"] == "agent2"
    assert failed["step_index"] == 2
    first.close()

    def succeed(role, state):
        calls.append(role)
        return _next(role, state)

    resumed = DecisionWorkflow(path, succeed)
    assert resumed.inspect("R1")["error"]["code"] == "OSError"
    completed = resumed.resume("R1")
    assert completed["status"] == "complete"
    assert completed["step_index"] == 4
    assert calls == ["agent0", "agent1", "agent2", "agent2", "agent3"]
    assert resumed.resume("R1")["status"] == "complete"
    assert len(calls) == 5
    resumed.close()


def test_commit_before_checkpoint_reuses_domain_saved_return(tmp_path):
    """The domain commit survives even when the framework never sees its return."""
    domain_path = tmp_path / "domain.sqlite"
    with sqlite3.connect(domain_path) as db:
        db.execute("CREATE TABLE tasks(id TEXT PRIMARY KEY, saved_return TEXT)")
        db.execute("CREATE TABLE effects(task_id TEXT)")
    fail_once = True
    invocations = []

    def callback(role, state):
        nonlocal fail_once
        key = f"{state['run_id']}:{state['step_index']}"
        invocations.append(key)
        with sqlite3.connect(domain_path) as db:
            saved = db.execute("SELECT saved_return FROM tasks WHERE id=?", (key,)).fetchone()
            if saved:
                return json.loads(saved[0])
            result = _next(role, state)
            db.execute("INSERT INTO effects VALUES (?)", (key,))
            db.execute("INSERT INTO tasks VALUES (?,?)", (key, json.dumps(result)))
        if role == "agent1" and fail_once:
            fail_once = False
            raise RuntimeError("crash after commit, before checkpoint")
        return result

    path = tmp_path / "checkpoint.sqlite"
    workflow = DecisionWorkflow(path, callback)
    assert workflow.run("R2", {})["status"] == "error"
    workflow.close()
    workflow = DecisionWorkflow(path, callback)
    assert workflow.resume("R2")["status"] == "complete"
    assert invocations.count("R2:1") == 2
    with sqlite3.connect(domain_path) as db:
        assert db.execute("SELECT count(*) FROM effects").fetchone()[0] == 4
    workflow.close()


def test_waiting_is_persistent_and_plain_resume_is_not_human_approval(tmp_path):
    calls = []

    def wait(role, state):
        calls.append(role)
        return {"step_index": state["step_index"] + 1, "status": "waiting",
                "next_role": "agent0", "waiting_reason": "clarification"}

    path = tmp_path / "checkpoint.sqlite"
    workflow = DecisionWorkflow(path, wait)
    assert workflow.run("R3", {})["status"] == "waiting"
    workflow.close()
    workflow = DecisionWorkflow(path, wait)
    assert workflow.resume("R3")["status"] == "waiting"
    assert calls == ["agent0"]
    with pytest.raises(ValueError, match="événement"):
        workflow.resume("R3", {"next_role": "agent0"})
    workflow.close()


def test_research_analysis_cycle_has_distinct_steps_and_bounded_work(tmp_path):
    sequence = []

    def callback(role, state):
        sequence.append(role)
        step = state["step_index"]
        targets = ["agent1", "agent2", "agent1", "agent2", "agent3", None]
        return {"step_index": step + 1, "next_role": targets[step],
                "status": "complete" if targets[step] is None else "running"}

    workflow = DecisionWorkflow(tmp_path / "cycle.sqlite", callback)
    assert workflow.run("R4", {})["status"] == "complete"
    assert sequence == ["agent0", "agent1", "agent2", "agent1", "agent2", "agent3"]
    workflow.close()

    def loop(role, state):
        return {"step_index": state["step_index"] + 1, "status": "running", "next_role": role}

    bounded = DecisionWorkflow(tmp_path / "bounded.sqlite", loop, max_transitions=3)
    result = bounded.run("R5", {})
    assert result["status"] == "error"
    assert result["error"]["code"] == "TransitionBudgetExceeded"
    assert result["step_index"] == 3
    assert bounded.resume("R5")["step_index"] == 3
    bounded.close()


def test_external_tracing_is_disabled_even_when_inherited(tmp_path, monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
    seen = []

    def callback(role, state):
        seen.append(get_tracing_context()["enabled"])
        return _next(role, state)

    workflow = DecisionWorkflow(tmp_path / "trace.sqlite", callback)
    assert workflow.run("R6", {})["status"] == "complete"
    assert seen == [False] * 4
    workflow.close()


def test_run_id_cannot_be_reused_to_replace_inputs(tmp_path):
    workflow = DecisionWorkflow(tmp_path / "identity.sqlite", _next)
    assert workflow.run("R7", {"dossier_id": "D1"})["status"] == "complete"
    with pytest.raises(ValueError, match="autres entrées"):
        workflow.run("R7", {"dossier_id": "D2"})
    workflow.close()
