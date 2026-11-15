#!/usr/bin/env python3
"""Reproducible local qualification; AWS calls require the explicit --aws flag."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import sqlite3
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from alphaforge_app.decision.workflow import DecisionWorkflow


class MachineReference:
    """Narrow comparison fixture, deliberately not a second production engine."""

    def __init__(self, path, callback):
        self.path, self.callback = path, callback
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS cursors(id TEXT PRIMARY KEY, state TEXT)")

    def _save(self, run_id, state):
        with sqlite3.connect(self.path) as db:
            db.execute(
                "INSERT INTO cursors VALUES (?,?) ON CONFLICT(id) DO UPDATE SET state=excluded.state",
                (run_id, json.dumps(state)),
            )

    def inspect(self, run_id):
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT state FROM cursors WHERE id=?", (run_id,)).fetchone()
        return json.loads(row[0]) if row else {"status": "not_found"}

    def run(self, run_id, initial):
        state = {**initial, "run_id": run_id, "step_index": 0,
                 "next_role": "agent0", "status": "running"}
        self._save(run_id, state)
        return self.resume(run_id)

    def resume(self, run_id):
        state = self.inspect(run_id)
        if state["status"] in {"complete", "waiting"}:
            return state
        state["status"] = "running"
        while state["status"] == "running":
            try:
                state.update(self.callback(state["next_role"], dict(state)))
            except OSError:
                state["status"] = "error"
            self._save(run_id, state)
        return state

    def close(self):
        pass


def qualify(factory, name, directory):
    started = time.monotonic()
    calls = []
    failed = False

    def callback(role, state):
        nonlocal failed
        calls.append({"role": role, "step_index": state["step_index"]})
        if role == "agent2" and not failed:
            failed = True
            raise OSError("qualification failure before role output")
        n = int(role[-1])
        return {"step_index": state["step_index"] + 1,
                "next_role": f"agent{n+1}" if n < 3 else None,
                "status": "running" if n < 3 else "complete"}

    path = directory / f"{name}.sqlite"
    first = factory(path, callback)
    interrupted = first.run("failure", {"dossier_id": "fixture"})
    assert interrupted["status"] == "error"
    first.close()
    second = factory(path, callback)
    assert second.inspect("failure")["status"] == "error"
    resumed = second.resume("failure")
    assert resumed["status"] == "complete"
    assert [x["role"] for x in calls] == ["agent0", "agent1", "agent2", "agent2", "agent3"]
    second.close()

    waiting_calls = []

    def wait(role, state):
        waiting_calls.append(role)
        return {"step_index": state["step_index"] + 1,
                "status": "waiting", "next_role": "agent0"}

    waiting = factory(directory / f"{name}-waiting.sqlite", wait)
    assert waiting.run("human", {})["status"] == "waiting"
    assert waiting.resume("human")["status"] == "waiting"
    assert waiting_calls == ["agent0"]
    waiting.close()
    return {
        "engine": name,
        "status": "passed",
        "failure_status": interrupted["status"],
        "resumed_status": resumed["status"],
        "calls": calls,
        "waiting_did_not_synthesize_approval": True,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "scope": "single-process restart via fresh instances; temporary persistent SQLite; synthetic roles",
    }


def aws_probe():
    from alphaforge_app.bedrock import BedrockClient
    from alphaforge_app.decision.research import research

    client = BedrockClient()
    response = client.generate(
        [{"role": "user", "content": 'Test technique. Réponds {"connected":true}.'}],
        json_schema={"type": "object", "properties": {"connected": {"type": "boolean"}},
                     "required": ["connected"], "additionalProperties": False},
        max_tokens=512, reasoning_effort="low",
    )
    result = research(
        {"decision_type": "reserve_allocation", "reserve_policy": "abstract_nominal"},
        query="site:cdic.ca eligible deposits guaranteed investment certificate",
    )
    return {
        "identity": client.identity,
        "inference": {k: v for k, v in response.items() if k not in ("text", "tool_calls")},
        "research": result,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aws", action="store_true", help="one paid model call and one AWS search")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/implementation/proofs/runtime_qualification.json")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="alphaforge-qualification-") as directory:
        engines = [
            qualify(DecisionWorkflow, "langgraph", Path(directory)),
            qualify(MachineReference, "explicit_machine_reference", Path(directory)),
        ]
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "versions": {name: importlib.metadata.version(name) for name in (
            "langgraph", "langgraph-checkpoint-sqlite", "langchain-core", "langsmith",
            "beautifulsoup4", "pypdf", "fonttools", "boto3", "botocore",
        )},
        "engines": engines,
        "decision": "langgraph",
        "reason": "Both pass the small persistence/transition fixture. LangGraph retains supported graph/checkpoint machinery; the domain commit contract remains independent.",
        "limitations": [
            "Not a throughput benchmark or distributed-worker qualification.",
            "Strands was reviewed during conception but not installed or run in this comparison.",
            "Commit-before-checkpoint, cycles, budgets and tracing are exercised in tests/test_decision_workflow.py.",
        ],
        "aws_calls_in_this_run": bool(args.aws),
    }
    if args.aws:
        report["aws"] = aws_probe()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({"output": str(args.output), "engines": engines,
                      "aws_calls": bool(args.aws)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
