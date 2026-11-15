"""Persistent execution cursor for four decision roles; the store owns commits.

Role callbacks must implement the commit/return idempotency contract:
``task_id = run_id + ":" + step_index``. On retry after commit but before
checkpoint, return the task's saved return value instead of repeating its work.
No model client or tool is created by this module.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Callable, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langsmith import tracing_context

ROLES = ("agent0", "agent1", "agent2", "agent3")


class _State(TypedDict):
    payload: dict[str, Any]


def _copy(value: Any) -> Any:
    """Only JSON data crosses the checkpoint/domain boundary."""
    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))


def _failure(exc: Exception) -> dict[str, Any]:
    if callable(getattr(exc, "as_dict", None)):
        return _copy(exc.as_dict())
    return {
        "code": type(exc).__name__,
        "message": "L'étape a échoué ; sa reprise conserve les étapes déjà commises.",
        "retryable": not isinstance(exc, (TypeError, ValueError)),
    }


class DecisionWorkflow:
    """Small LangGraph facade with local checkpoints and explicit restarts.

    ``role_callback(role, state)`` returns a JSON state/update with an incremented
    step_index, status (running/waiting/complete) and next_role. The callback
    persists the authoritative task, effects and saved return in the dossier.
    Waiting never implies approval: plain resume leaves a waiting run waiting.
    A clarification normally creates a new run in the dossier service.
    """

    engine = "langgraph"

    def __init__(
        self,
        checkpoint_path: str | Path,
        role_callback: Callable[[str, dict[str, Any]], dict[str, Any]],
        *,
        max_transitions: int = 24,
    ) -> None:
        if max_transitions < 1:
            raise ValueError("max_transitions doit être positif.")
        self.path = Path(checkpoint_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.role_callback = role_callback
        self.max_transitions = max_transitions
        self._locks_guard = threading.Lock()
        self._run_locks: dict[str, threading.RLock] = {}
        self._connection = sqlite3.connect(
            str(self.path), check_same_thread=False, timeout=30
        )
        with sqlite3.connect(self.path, timeout=30) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS workflow_failures "
                "(run_id TEXT PRIMARY KEY, error_json TEXT NOT NULL)"
            )
        self._saver = SqliteSaver(self._connection)
        graph = StateGraph(_State)
        for role in ROLES:
            graph.add_node(role, self._node(role))
        graph.add_conditional_edges(START, self._route)
        for role in ROLES:
            graph.add_conditional_edges(role, self._route)
        self._graph = graph.compile(checkpointer=self._saver)

    def _lock(self, run_id: str) -> threading.RLock:
        with self._locks_guard:
            return self._run_locks.setdefault(run_id, threading.RLock())

    def _config(self, run_id: str) -> dict[str, Any]:
        return {
            "configurable": {"thread_id": run_id},
            "recursion_limit": self.max_transitions + 4,
            "callbacks": [],
        }

    @staticmethod
    def _route(state: _State) -> str:
        payload = state["payload"]
        if payload.get("status") in {"waiting", "complete", "error", "cancelled"}:
            return END
        role = payload.get("next_role")
        if role not in ROLES:
            raise ValueError("La prochaine responsabilité doit être un des quatre rôles.")
        return role

    def _node(self, role: str):
        def execute(state: _State) -> _State:
            before = _copy(state["payload"])
            step = before["step_index"]
            if step >= self.max_transitions:
                return {
                    "payload": {
                        **before,
                        "status": "error",
                        "error": {
                            "code": "TransitionBudgetExceeded",
                            "message": "Le budget de transitions du run est atteint.",
                            "retryable": False,
                        },
                    }
                }
            update = self.role_callback(role, _copy(before))
            if not isinstance(update, dict):
                raise TypeError("Le callback doit rendre un état JSON.")
            after = {**before, **_copy(update)}
            if after.get("run_id") != before["run_id"]:
                raise ValueError("Un callback ne peut pas changer de run.")
            if after.get("step_index") != step + 1:
                raise ValueError("Le callback doit avancer step_index d'une unité.")
            if after.get("status") not in {
                "running", "waiting", "complete", "error", "cancelled"
            }:
                raise ValueError("Statut de callback inconnu.")
            self._route({"payload": after})
            after["current_role"] = role
            return {"payload": after}

        return execute

    def _record_error(self, run_id: str, error: dict[str, Any] | None) -> None:
        with sqlite3.connect(self.path, timeout=30) as connection:
            if error is None:
                connection.execute("DELETE FROM workflow_failures WHERE run_id=?", (run_id,))
            else:
                connection.execute(
                    "INSERT INTO workflow_failures(run_id,error_json) VALUES (?,?) "
                    "ON CONFLICT(run_id) DO UPDATE SET error_json=excluded.error_json",
                    (run_id, json.dumps(error, ensure_ascii=False)),
                )

    def inspect(self, run_id: str) -> dict[str, Any]:
        with self._lock(run_id), tracing_context(enabled=False):
            snapshot = self._graph.get_state(self._config(run_id))
            if not snapshot.values:
                return {"run_id": run_id, "status": "not_found", "engine": self.engine}
            result = _copy(snapshot.values["payload"])
            result["workflow"] = {
                "engine": self.engine,
                "thread_id": run_id,
                "next_nodes": list(snapshot.next),
                "checkpoint_id": snapshot.config.get("configurable", {}).get("checkpoint_id"),
            }
            with sqlite3.connect(self.path, timeout=30) as connection:
                failure = connection.execute(
                    "SELECT error_json FROM workflow_failures WHERE run_id=?", (run_id,)
                ).fetchone()
            if failure:
                result["status"] = "error"
                result["error"] = json.loads(failure[0])
                if snapshot.next:
                    result["current_role"] = snapshot.next[0]
            return result

    def _invoke(self, run_id: str, value: _State | None) -> dict[str, Any]:
        # Explicit local tracing scope overrides inherited LangSmith settings.
        # Imported framework dependencies do not constitute an inference route.
        with tracing_context(enabled=False):
            try:
                self._graph.invoke(value, config=self._config(run_id))
            except Exception as exc:
                self._record_error(run_id, _failure(exc))
            else:
                self._record_error(run_id, None)
        return self.inspect(run_id)

    def run(self, run_id: str, initial_state: dict[str, Any]) -> dict[str, Any]:
        if not run_id or len(run_id) > 200:
            raise ValueError("run_id doit être non vide et borné.")
        initial = _copy(initial_state)
        fingerprint = hashlib.sha256(
            json.dumps(initial, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        with self._lock(run_id):
            existing = self.inspect(run_id)
            if existing["status"] != "not_found":
                if existing.get("_initial_hash") != fingerprint:
                    raise ValueError("Ce run existe avec d'autres entrées.")
                return existing
            initial.update(
                run_id=run_id,
                step_index=initial.get("step_index", 0),
                status=initial.get("status", "running"),
                next_role=initial.get("next_role", "agent0"),
                _initial_hash=fingerprint,
            )
            if not isinstance(initial["step_index"], int) or initial["step_index"] < 0:
                raise ValueError("step_index doit être un entier positif ou nul.")
            self._route({"payload": initial})
            return self._invoke(run_id, {"payload": initial})

    def resume(
        self, run_id: str, resume_state: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Retry only pending nodes; a completed run is not started over.

        ``resume_state`` is reserved for trusted service code after validating a
        dependency/human event. It must not be passed directly from HTTP JSON.
        An ordinary resume of a waiting run does not synthesize that event.
        """
        with self._lock(run_id):
            existing = self.inspect(run_id)
            if existing["status"] == "not_found":
                return existing
            if resume_state is not None:
                if existing["status"] != "waiting":
                    raise ValueError("Un nouvel état de reprise exige un run en attente.")
                update = _copy(resume_state)
                if not update.get("resume_event_ref"):
                    raise ValueError("La reprise doit référencer un événement validé.")
                if any(key in update for key in ("run_id", "step_index", "_initial_hash")):
                    raise ValueError("La reprise ne peut pas modifier l'identité ou le compteur.")
                payload = {k: v for k, v in existing.items() if k != "workflow"}
                payload.update(update)
                payload["status"] = "running"
                return self._invoke(run_id, {"payload": payload})
            if existing["status"] in {"complete", "waiting", "cancelled"}:
                return existing
            if not existing["workflow"]["next_nodes"]:
                return existing
            return self._invoke(run_id, None)

    def close(self) -> None:
        """Call only after workers have stopped."""
        self._connection.close()
