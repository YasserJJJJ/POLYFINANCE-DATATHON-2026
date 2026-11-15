#!/usr/bin/env python3
"""Verify the nominated AWS account and optionally run three small live probes.

No credentials, request prompts, private model reasoning, or AWS error bodies
are written to the report. --live performs billed inference in the verified
event account; it never creates or deploys infrastructure.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alphaforge_app.bedrock import BedrockClient, BedrockError  # noqa: E402


def summary(result: dict) -> dict:
    return {
        key: result[key]
        for key in (
            "model",
            "request_id",
            "usage",
            "latency_ms",
            "server_latency_ms",
            "stop_reason",
            "provider",
            "region",
            "account_id",
        )
    }


def probe(live: bool = False) -> dict:
    client = BedrockClient()
    report = {
        "identity": client.identity,
        "packages": {
            name: importlib.metadata.version(name) for name in ("boto3", "botocore", "jsonschema")
        },
        "checks": [],
        "infrastructure_created": False,
    }
    if not live:
        return report
    schema = {
        "type": "object",
        "properties": {
            "language": {"type": "string", "enum": ["fr"]},
            "horizon_years": {"type": "integer"},
            "objective": {"type": "string"},
            "liquidity_known": {"type": "boolean"},
        },
        "required": ["language", "horizon_years", "objective", "liquidity_known"],
        "additionalProperties": False,
    }
    first = client.generate(
        [
            {
                "role": "system",
                "content": "Extrais uniquement les informations explicites. Réponds en français.",
            },
            {
                "role": "user",
                "content": "Je veux préserver mon capital sur quatre ans. Je n'ai pas précisé mes besoins de liquidité.",
            },
        ],
        json_schema=schema,
        schema_name="profile_probe",
        max_tokens=1024,
        reasoning_effort="medium",
    )
    parsed = first["parsed"]
    assert parsed["language"] == "fr" and parsed["horizon_years"] == 4
    assert parsed["liquidity_known"] is False
    report["checks"].append({"name": "french_strict_json", "passed": True, **summary(first)})

    tools = [
        {
            "type": "function",
            "name": "get_scenario_result",
            "description": "Consulte le résultat numérique déjà calculé d'un scénario fictif.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {"scenario_id": {"type": "string", "enum": ["reference"]}},
                "required": ["scenario_id"],
                "additionalProperties": False,
            },
        }
    ]
    messages = [
        {
            "role": "system",
            "content": "Tu expliques des scénarios fictifs. Utilise les outils pour les nombres et ne les invente jamais.",
        },
        {"role": "user", "content": "Consulte le scénario reference et indique sa valeur finale en CAD."},
    ]
    called = client.generate(
        messages,
        tools=tools,
        tool_choice={"name": "get_scenario_result"},
        max_tokens=1024,
        reasoning_effort="medium",
    )
    assert len(called["tool_calls"]) == 1
    call = called["tool_calls"][0]
    assert call["name"] == "get_scenario_result"
    assert call["arguments"] == {"scenario_id": "reference"}
    report["checks"].append({"name": "typed_tool_call", "passed": True, **summary(called)})
    messages.extend(
        [
            {
                "role": "assistant",
                "content": called["text"],
                "tool_calls": called["tool_calls"],
            },
            {
                "role": "tool",
                "tool_call_id": call["id"],
                "content": json.dumps({"scenario_id": "reference", "final_value": 9876.54, "currency": "CAD"}),
            },
        ]
    )
    final_schema = {
        "type": "object",
        "properties": {"final_value": {"type": "number"}, "currency": {"type": "string"}},
        "required": ["final_value", "currency"],
        "additionalProperties": False,
    }
    final = client.generate(
        messages,
        tools=tools,
        json_schema=final_schema,
        schema_name="tool_roundtrip_probe",
        max_tokens=1024,
        reasoning_effort="medium",
    )
    assert final["parsed"] == {"final_value": 9876.54, "currency": "CAD"}
    report["checks"].append({"name": "tool_result_fidelity", "passed": True, **summary(final)})
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Run three small billed model calls.")
    args = parser.parse_args()
    try:
        print(json.dumps(probe(args.live), indent=2, ensure_ascii=False))
    except BedrockError as exc:
        print(json.dumps({"error": exc.as_dict()}, indent=2, ensure_ascii=False))
        raise SystemExit(1)
