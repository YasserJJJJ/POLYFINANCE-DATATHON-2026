"""Failure contracts at the agent/calculation boundary; no model calls here."""

from __future__ import annotations

import copy
import json
import re

import pytest

from alphaforge_app import main, orchestrator
from alphaforge_app.bedrock import BedrockError
from alphaforge_app.personas import BY_ID


def tool(call_id, name, arguments):
    return {"id": call_id, "name": name, "arguments": arguments}


def answer(*, calls=None, parsed=None):
    return {
        "text": "",
        "tool_calls": calls or [],
        "parsed": parsed,
        "request_id": "contract-test-request",
        "model": "global.openai.gpt-6-astra",
        "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        "latency_ms": 0,
        "stop_reason": "tool_use" if calls else "end_turn",
    }


def conclusion(**updates):
    value = {
        "title": "Une comparaison conditionnelle",
        "text": "Les observations calculées éclairent le compromis sans garantir le futur.",
        "selected_observation_ids": ["drawdown", "focus", "comfort"],
        "questions": [],
        "contradictions": [],
        "conditions": ["Réexaminer si le besoin de liquidité change."],
    }
    value.update(updates)
    return value


def successful_tools():
    return [
        tool("compare", "compare_scenario", {"focus_ticker": "TSLA", "focus_weight": 5}),
        tool("sources", "read_evidence", {"source_ids": ["starter", "method", "cfa"]}),
    ]


class FakeClient:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = []

    def generate(self, messages, **kwargs):
        self.calls.append({"messages": copy.deepcopy(messages), **kwargs})
        value = next(self.replies)
        if isinstance(value, Exception):
            raise value
        return value


@pytest.fixture
def run_analysis(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "RUNTIME", tmp_path)

    def run(replies):
        client = FakeClient(replies)
        monkeypatch.setattr(orchestrator, "get_client", lambda: client)
        persona = BY_ID["robert"]
        request = main.AnalyzeRequest(
            persona="robert",
            prompt=persona["prompt"],
            portfolio=persona["portfolio"],
            settings=persona["settings"],
            use_ai=True,
        )
        response = main.analyze(request)
        # Each report remains a valid, complete export even on agent failure.
        stored = json.loads((tmp_path / f"{response['id']}.json").read_text())
        assert stored["id"] == response["id"]
        return response, client

    return run


def test_required_calculation_failure_never_claims_agent_success(run_analysis):
    bad = tool("bad", "compare_scenario", {"focus_ticker": "INEXISTANT", "focus_weight": 5})
    response, client = run_analysis(
        [answer(calls=[bad, successful_tools()[1]]), answer(), answer(), answer()]
    )
    assert len(client.calls) == 4
    assert response["mode"] == "calculation"
    assert response["agent"]["status"] == "error"
    assert response["settings"]["focus_ticker"] == "TSLA"
    assert response["comparison"]["alternative"]["metrics"]["ending_value_cad"] > 0
    assert any(item["tool"] == "compare_scenario" and item["status"] == "error"
               for item in response["trace"])


def test_later_tool_error_is_visible_as_degraded_analysis(run_analysis):
    bad = tool("bad", "compare_scenario", {"focus_ticker": "INEXISTANT", "focus_weight": 5})
    response, client = run_analysis(
        [answer(calls=[*successful_tools(), bad]), answer(parsed=conclusion())]
    )
    assert len(client.calls) == 2
    assert response["agent"]["status"] != "success"
    assert any(item["tool"] == "compare_scenario" and item["status"] == "error"
               for item in response["trace"])
    final_call = client.calls[-1]
    assert not final_call.get("tools")
    assert all(item["role"] != "tool" and not item.get("tool_calls")
               for item in final_call["messages"])
    dossier = json.loads(final_call["messages"][-1]["content"])
    assert dossier["erreurs_outils"] == response["agent"]["tool_errors"]
    assert dossier["erreurs_outils"][0]["tool"] == "compare_scenario"
    observed = {item["id"]: item for item in response["observations"]}
    assert len(response["summary"]["findings"]) == 3
    assert all(item == observed[item["id"]] for item in response["summary"]["findings"])


def test_tool_error_reaches_the_next_planning_turn_before_recovery(run_analysis):
    bad = tool("bad", "compare_scenario", {"focus_ticker": "INEXISTANT", "focus_weight": 5})
    response, client = run_analysis([
        answer(calls=[bad, successful_tools()[1]]),
        answer(calls=[successful_tools()[0]]),
        answer(parsed=conclusion()),
    ])
    assert len(client.calls) == 3
    assert response["mode"] == "bedrock"
    assert response["agent"]["status"] == "partial"
    error_results = [
        item for item in client.calls[1]["messages"]
        if item.get("role") == "tool" and item.get("tool_call_id") == "bad"
    ]
    assert error_results and error_results[0].get("is_error") is True
    assert client.calls[1].get("tools")
    assert not client.calls[-1].get("tools")


def test_generated_numbers_cannot_bypass_the_deterministic_findings(run_analysis):
    response, client = run_analysis(
        [
            answer(calls=successful_tools()),
            answer(parsed=conclusion(
                title="Capital garanti à 100 %",
                conditions=["Le rendement futur atteindra 25 %."],
                questions=["Visez-vous 40 % de rendement ?"],
                contradictions=["Votre perte est garantie à 0 %."],
            )),
        ]
    )
    assert len(client.calls) == 2
    generated_prose = [
        response["summary"]["title"],
        response["summary"]["text"],
        *response["summary"].get("conditions", []),
        *response["profile"]["unknown"],
        *response["profile"]["contradictions"],
    ]
    assert all(not re.search(r"\d|[%$€]", text) for text in generated_prose)
    # Deterministic observations remain permitted to show their calculated values.
    assert any("%" in item["text"] for item in response["summary"]["findings"])


@pytest.mark.parametrize("selected", [
    ["focus", "comfort", "future_return_guarantee"],
    ["focus", "comfort"],
    ["focus", "comfort", "horizon", "drawdown", "tradeoff", "esg"],
])
def test_invalid_observation_selection_rejects_generated_conclusion(run_analysis, selected):
    response, client = run_analysis(
        [
            answer(calls=successful_tools()),
            answer(parsed=conclusion(selected_observation_ids=selected)),
        ]
    )
    assert len(client.calls) == 2
    assert response["mode"] == "calculation"
    assert response["agent"]["status"] == "error"
    assert response["summary"]["title"] != "Une comparaison conditionnelle"


def test_expired_aws_session_preserves_calculations_and_diagnostic(run_analysis):
    response, client = run_analysis(
        [BedrockError(
            "La session AWS a expiré. Renouvelez le profil alphaforge.",
            code="ExpiredToken",
            request_id="expired-request-id",
        )]
    )
    assert len(client.calls) == 1
    assert response["mode"] == "calculation"
    assert response["agent"]["status"] == "error"
    assert response["comparison"]["baseline"]["metrics"]["initial_value_cad"] == 10000
    # Preserve the sanitized operational reason and request identifier.
    diagnostic = json.dumps(response["agent"], ensure_ascii=False)
    assert "ExpiredToken" in diagnostic
    assert "expired-request-id" in diagnostic


def test_failed_conclusion_rolls_back_a_successful_variant_change(run_analysis):
    changed = tool("changed", "compare_scenario", {"focus_ticker": "TSLA", "focus_weight": 90})
    response, client = run_analysis([
        answer(calls=[changed, successful_tools()[1]]),
        BedrockError("Réponse tronquée.", code="IncompleteOutput", request_id="final-failure"),
    ])
    assert len(client.calls) == 2
    assert response["mode"] == "calculation"
    assert response["agent"]["status"] == "error"
    assert response["settings"]["focus_weight"] == 5
    assert response["request"]["settings"]["focus_weight"] == 5
    alternative = response["comparison"]["alternative"]["portfolio"]
    assert next(item["weight"] for item in alternative if item["ticker"] == "TSLA") == 0.05
    focus = next(item for item in response["observations"] if item["id"] == "focus")
    assert "5.0 %" in focus["text"] and "90.0 %" not in focus["text"]
    # The attempted variant remains auditable without changing the displayed result.
    assert any(item["tool"] == "compare_scenario" and "90 %" in item["detail"]
               for item in response["trace"])
    assert response["agent"]["error"]["request_id"] == "final-failure"


def test_oversized_tool_batch_stops_before_executing_tools(run_analysis):
    calls = [
        tool(f"excess-{index}", "compare_scenario", {"focus_ticker": "TSLA", "focus_weight": 90})
        for index in range(7)
    ]
    response, client = run_analysis([answer(calls=calls)])
    assert len(client.calls) == 1
    assert response["mode"] == "calculation"
    assert response["agent"]["status"] == "error"
    assert response["settings"]["focus_weight"] == 5
    assert all(item["tool"] != "compare_scenario" for item in response["trace"])
