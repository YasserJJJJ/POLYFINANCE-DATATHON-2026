"""Prompt 5 independent chain review.

No model inference is executed here. Role responses and documentary retrieval
are explicit test doubles; finance.analyze, Store and DecisionWorkflow are real.
P5_CHAIN_PROOF_DIR optionally records the observed evidence before assertions.
"""
import copy
import json
import os
from pathlib import Path

import pytest

from alphaforge_app.decision.finance import analyze, examples
from alphaforge_app.decision.service import DecisionService
from alphaforge_app.decision.store import digest


def documentary_double(problem, **kwargs):
    return {
        "evidence": [], "methods": [], "gaps": [], "contradictions": [],
        "receipts": [], "limitations": ["Test double; no documentary conclusion."],
    }


def persist(name, value):
    directory = os.environ.get("P5_CHAIN_PROOF_DIR")
    if directory:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        (path / ("chaine_" + name + ".json")).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        )


@pytest.fixture
def service_factory(tmp_path):
    services = []

    def make(**kwargs):
        service = DecisionService(
            tmp_path / str(len(services)),
            researcher=documentary_double, **kwargs,
        )
        services.append(service)
        return service

    yield make
    for service in services:
        service.pool.shutdown(wait=True)
        service.workflow.close()


@pytest.mark.parametrize("legacy_source", [False, True])
def test_extracted_capital_survives_correction_of_withdrawal(service_factory, legacy_source):
    """An explicit corrected withdrawal must not erase previously stated capital."""
    service = service_factory()
    example = copy.deepcopy(examples()[0])
    example["facts"].pop("capital_cad")
    prompt = "Mon capital est de 100 000 CAD."
    contexts = []

    def role_double(run, task, role, context, *args):
        if role != "agent0":
            return None
        contexts.append(copy.deepcopy(context))
        initial = context["request"]["kind"] == "initial"
        return {
            "updates": [{
                "field": "capital_cad", "value_json": "100000",
                "quote": prompt, "origin": "extracted",
                "rationale": "Explicit stated capital; fixture extraction.",
            }] if initial else [],
            "contradictions": [], "clarifications": [],
            "interpretation": "Controlled extraction; no model inference.",
        }

    service._infer = role_double
    current_agent0 = service._agent0
    if legacy_source:
        def legacy_agent0(run, task, heads, state):
            result = current_agent0(run, task, heads, state)
            for write in result["writes"]:
                if write.id == "fact.capital_cad":
                    write.input_refs = [heads["request"]["ref"]]
                    write.content["source_ref"] = heads["request"]["ref"]
            return result
        service._agent0 = legacy_agent0
    initial = service.create(prompt, example["facts"], False, background=False)
    service._agent0 = current_agent0
    assert initial["status"] == "complete"
    capital = next(a for a in initial["artifacts"] if a["id"] == "fact.capital_cad")
    revised = service.revise(
        initial["id"], "Correction : retrait de 40 000 CAD.",
        {"withdrawal_cad": 40000}, initial["revision"], background=False,
    )
    observed = {
        "mode": "controlled_role_and_research_doubles_real_finance_store_workflow",
        "initial_capital": initial["active_problem"]["capital_cad"],
        "initial_capital_provenance": capital,
        "revised_status": revised["status"],
        "revised_capital": revised["active_problem"]["capital_cad"],
        "revised_current_facts_received": contexts[1]["current_facts"],
        "comparison": revised["comparison"],
    }
    persist("extracted_fact_revision" + ("_legacy" if legacy_source else ""), observed)
    assert revised["active_problem"]["capital_cad"] == 100000
    assert revised["status"] == "complete"
    retained = service.store.artifact(initial["id"], capital["ref"])
    assert retained["usable"]
    assert retained["content"] == capital["content"]
    corrected = service.revise(
        initial["id"], "Le capital est en réalité de 120 000 CAD.",
        {"capital_cad": 120000}, revised["revision"], background=False,
    )
    assert corrected["active_problem"]["capital_cad"] == 120000
    assert not service.store.artifact(initial["id"], capital["ref"])["usable"]
    assert "baseline_stress@1" in corrected["comparison"]["invalidated"]


def test_incomplete_request_keeps_actionable_missing_field_current(service_factory):
    """A waiting dossier must still explain exactly which answer is missing."""
    service = service_factory()
    facts = copy.deepcopy(examples()[0]["facts"])
    facts.pop("withdrawal_cad")
    facts["question"] = "Un retrait est prévu ; je n'ai pas donné son montant."
    snapshot = service.create(facts["question"], facts, False, background=False)
    view = (snapshot["current_view"] or {}).get("content", {})
    analysis = (snapshot["current_analysis"] or {}).get("content", {})
    visible = (
        view.get("questions", [])
        + snapshot["active_problem"].get("clarifications", [])
        + analysis.get("missing", [])
    )
    missing_in_history = [
        a["content"].get("missing")
        for a in snapshot["artifacts"] if a["id"] == "analysis"
    ]
    persist("incomplete", {
        "mode": "deterministic_control_real_finance_store_workflow_research_double",
        "status": snapshot["status"], "current_view": snapshot["current_view"],
        "current_analysis": snapshot["current_analysis"],
        "active_clarifications": snapshot["active_problem"]["clarifications"],
        "visible_missing_fields": visible, "historical_missing": missing_in_history,
        "task_roles": [t["role"] for t in snapshot["tasks"]],
        "questions": snapshot["questions"],
    })
    assert snapshot["status"] == "waiting"
    assert any(item.get("field") == "withdrawal_cad" for item in visible)
    assert snapshot["current_view"]["content"]["status"] == "missing_input"
    assert snapshot["current_analysis"]["content"]["status"] == "missing_input"
    original_problem = service.store.artifact(snapshot["id"], "problem@1")
    assert snapshot["active_problem"] == original_problem["content"]
    assert original_problem["usable"]
    assert snapshot["pending_clarifications"]["qualification_ref"] == "qualification@2"
    assert any(
        q["field"] == "withdrawal_cad"
        for q in snapshot["pending_clarifications"]["questions"]
    )


def test_failed_arithmetic_check_cannot_receive_sufficient_view_status(service_factory):
    """Fault injection: a terminal result status must not override failed checks."""
    def finance_with_failed_check(problem):
        result = analyze(problem)
        result["checks"].append({
            "id": "independent_recomputation",
            "status": "insufficient",
            "method": "Controlled arithmetic-verification failure injection.",
            "scope": "The claimed minimum cannot be verified.",
        })
        return result

    service = service_factory(finance=finance_with_failed_check)
    example = examples()[0]
    snapshot = service.create(example["prompt"], example["facts"], False, background=False)
    view = (snapshot["current_view"] or {}).get("content", {})
    persist("arithmetic_check", {
        "mode": "fault_injection_real_finance_plus_insufficient_check_no_model",
        "status": snapshot["status"], "view_status": view.get("status"),
        "arithmetic_control": view.get("controls", {}).get("arithmetic"),
        "claims": view.get("claims"), "options": view.get("options"),
    })
    assert view.get("controls", {}).get("arithmetic", {}).get("status") != "sufficient"
    assert not view.get("claims")


def test_risk_constraint_changes_feasible_allocation(service_factory):
    """The numeric scenario-loss constraint has observable financial influence."""
    service = service_factory()
    example = examples()[0]
    initial = service.create(example["prompt"], example["facts"], False, background=False)
    revised = service.revise(
        initial["id"], "Je fixe la perte maximale sous ces scénarios à zéro.",
        {"scenario_loss_limit_cad": 0}, initial["revision"], background=False,
    )
    def minimum(snapshot):
        return next(
            o for o in snapshot["current_analysis"]["content"]["options"]
            if o["id"] == "minimum_turnover"
        )["metrics"]["turnover_cad"]["value"]
    persist("risk_constraint", {
        "mode": "deterministic_control_real_finance_store_workflow_research_double",
        "before_turnover_cad": minimum(initial),
        "after_turnover_cad": minimum(revised),
        "after_constraint": revised["active_problem"]["scenario_loss_limit_cad"],
        "changed_fields": revised["comparison"]["changed_fields"],
        "reused": revised["comparison"]["reused"],
    })
    assert minimum(revised) > minimum(initial)
    assert "baseline_stress@1" in revised["comparison"]["reused"]


@pytest.mark.parametrize("field, value, prompt, accepted", [
    ("withdrawal_months", 12, "Le retrait est dans douze mois.", True),
    ("horizon_years", 15, "Mon horizon est de quinze ans.", True),
    ("horizon_years", 1, "Mon horizon est d'une année.", True),
    ("withdrawal_months", 12, "Le retrait est dans douze ans.", False),
    ("withdrawal_months", 15, "Le retrait est dans douze mois.", False),
    ("withdrawal_months", 22, "Le retrait est dans vingt-deux mois.", False),
    ("withdrawal_months", 12, "Le retrait est dans cent douze mois.", False),
    ("withdrawal_months", 12, "Le retrait est dans moins douze mois.", False),
])
def test_french_duration_words_require_matching_explicit_value_and_unit(
    service_factory, field, value, prompt, accepted,
):
    service = service_factory()
    facts = copy.deepcopy(examples()[0]["facts"])
    facts.pop(field)

    def role_double(run, task, role, context, *args):
        if role != "agent0":
            return None
        return {
            "updates": [{"field": field, "value_json": str(value), "quote": prompt,
                         "origin": "extracted", "rationale": "Controlled duration extraction."}],
            "clarifications": [], "contradictions": [], "interpretation": "No model inference.",
        }

    service._infer = role_double
    snapshot = service.create(prompt, facts, False, background=False)
    assert snapshot["active_problem"][field] == (value if accepted else None)
    if not accepted:
        assert snapshot["status"] == "waiting"
        assert any(
            question["field"] == field
            for question in snapshot["pending_clarifications"]["questions"]
        )


def test_archived_real_aws_claims_and_artifact_hashes_are_faithful():
    """Read archived real AWS exports; this test itself performs no inference."""
    proof_root = Path(__file__).resolve().parents[1] / "docs/implementation/proofs/final_demo"
    receipts = []
    for filename in ("robert-revised.json", "amira-initial.json"):
        dossier = json.loads((proof_root / filename).read_text())
        for artifact in dossier["artifacts"]:
            assert digest(artifact["content"]) == artifact["hash"]
        analysis = dossier["current_analysis"]["content"]
        originals = {c["id"]: c for c in analysis["claims"]}
        for claim in dossier["current_view"]["content"]["claims"]:
            assert claim["text"] == originals[claim["id"]]["text"]
            assert claim["result_refs"] == originals[claim["id"]]["result_refs"]
        for attempt in dossier["attempts"]:
            if attempt["tool"] != "bedrock.converse":
                continue
            assert attempt["detail"]["provider"] == "amazon-bedrock-runtime"
            receipts.append({
                "file": filename, "role": attempt["role"],
                "request_id": attempt["detail"]["request_id"],
                "provider": attempt["detail"]["provider"],
                "model": attempt["detail"]["model"],
            })
    persist("archived_aws_integrity", {
        "mode": "read_only_verification_of_archived_real_aws_receipts",
        "receipts": receipts, "count": len(receipts),
        "result": "content hashes and current claim text/pointers match",
        "limits": "Archived request IDs do not independently prove semantic correctness.",
    })
    assert len(receipts) == 12
