"""Folio transport over the existing four-agent service and immutable dossier."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import Field

from . import api
from .assessment import assess_checks
from .finance import analyze, reserve_budget_diagnostic_applicable
from .folio_projection import (
    archives, at_revision, calculation_proofs, dependency_preview, project, stats,
)
from .models import NewDossier, NumericInt, ProblemSpec, RevisionRequest, StrictModel
from .store import digest, now

router = APIRouter(prefix="/api/folio")


class CreateRequest(NewDossier):
    request_id: str = Field(min_length=1, max_length=200)


class ReviseRequest(RevisionRequest):
    request_id: str = Field(min_length=1, max_length=200)
    source_revision: NumericInt | None = Field(default=None, ge=1)


class PreviewRequest(StrictModel):
    base_revision: NumericInt = Field(ge=1)
    changes: dict = Field(default_factory=dict)


@router.get("/dossiers")
def dossiers():
    return {"dossiers": api.service().store.list()}


@router.get("/examples")
def examples():
    return api.examples()


@router.get("/dossiers/{dossier_id}")
def dossier(dossier_id: str, revision: int | None = Query(default=None, ge=1)):
    snapshot = api.call(api.service().store.snapshot, dossier_id)
    selected = api.call(at_revision, snapshot, revision)
    return {"snapshot": selected, "current_revision": snapshot["revision"],
            "version": project(selected, historical=revision is not None),
            "archives": archives(snapshot)}


@router.post("/dossiers", status_code=202)
def create(body: CreateRequest):
    return api.call(api.service().create, body.prompt, body.facts, body.use_ai, request_id=body.request_id)


@router.post("/dossiers/{dossier_id}/revise", status_code=202)
def revise(dossier_id: str, body: ReviseRequest):
    return api.call(api.service().revise, dossier_id, body.message, body.changes,
                    body.base_revision, body.intent, request_id=body.request_id,
                    source_revision=body.source_revision)


@router.post("/dossiers/{dossier_id}/resume", status_code=202)
def resume(dossier_id: str):
    return api.call(api.service().resume, dossier_id)


def preview_snapshot(snapshot, changes):
    """Calculate from explicit selected inputs without altering any store.

    Existing documentary blockers remain blockers, except for the mathematical
    reserve-budget certificate which does not require market evidence. A local
    preview never invents a fresh agent review of changed inputs.
    """
    ProblemSpec.model_validate(changes)
    base = project(snapshot, historical=True)
    # A dossier may await its first qualified ProblemSpec. Only usable captured
    # facts are then admissible; schema defaults denote absent/unsupported input.
    problem = copy.deepcopy(snapshot.get("active_problem") or {
        a["content"]["field"]: a["content"]["value"] for a in snapshot["artifacts"]
        if a["usable"] and a["id"].startswith("fact.")
    })
    before_problem = copy.deepcopy(problem)
    actual_changes = {k: value for k, value in changes.items() if problem.get(k) != value}
    problem.update(copy.deepcopy(changes))
    problem = ProblemSpec.model_validate(problem).model_dump()
    heads = {a["id"]: a for a in snapshot["artifacts"] if a["usable"]}
    research_review = heads.get("research_review", {}).get("content", {})
    blockers = research_review.get("blocking_issues", [])
    executed = not blockers or reserve_budget_diagnostic_applicable(problem)
    if executed:
        analysis = analyze(problem)
    else:
        analysis = {
            "status": "missing_input", "method": {"id": "documentary_review_required"},
            "inputs": problem, "options": [], "checks": [], "claims": [], "limitations": [],
            "missing": [{"field": "documentary_evidence", "reason": item.get("message", "Preuve contestée.")}
                        for item in blockers],
            "provenance": {"source_review_ref": heads.get("research_review", {}).get("ref")},
        }
    assessment = assess_checks(analysis)
    if assessment["failed_check_ids"]:
        analysis.update(status="error", options=[], claims=[], sensitivity=[])
        analysis.pop("optimal_face", None)
    analysis["verification_assessment"] = assessment
    source_file = Path(__file__).with_name("finance.py")
    receipt = {
        "executed_at": now(), "implementation": "alphaforge_app.decision.finance.analyze",
        "calculation_executed": executed, "result_sha256": digest(analysis),
        "inputs_sha256": digest(problem), "source_sha256": hashlib.sha256(source_file.read_bytes()).hexdigest(),
        "inference_calls": 0, "product_mutations": 0, "artifact_cache_reused": False,
        "base_dossier_id": snapshot["id"], "base_revision": snapshot["revision"],
        "scope": "Aperçu déterministe ; aucun agent ni validation documentaire renouvelée.",
    }
    source = {
        "dossier_id": snapshot["id"], "dossier_revision": snapshot["revision"],
        "analysis_ref": None, "analysis_sha256": receipt["result_sha256"],
        "scope": "local_preview_not_committed", "recorded_at": receipt["executed_at"],
        "base_source": base["source"],
    }
    facts = copy.deepcopy(base["facts"])
    for field, value in actual_changes.items():
        facts[field] = {"field": field, "value": value, "origin": "declared_for_preview",
                        "artifact_ref": None, "source_ref": None, "version": None}
    delta = [{"field": k, "before": before_problem.get(k), "after": value}
             for k, value in actual_changes.items()]
    notice = "Aperçu calculé sur une copie. Aucun agent relancé, aucune révision enregistrée ; l’applicabilité des preuves doit être réexaminée avant adoption."
    version = {
        **base, "id": "preview-" + receipt["result_sha256"][:12], "label": "Aperçu non enregistré",
        "status": analysis["status"], "analysis_status": analysis["status"],
        "source": source, "problem": problem, "facts": facts, "analysis": analysis,
        "stats": stats(analysis), "claims": analysis.get("claims", []),
        "limits": list(dict.fromkeys(analysis.get("limitations", []) + [notice])),
        "proofs": calculation_proofs(analysis, source),
        "agents": [], "events": [], "controls": {
            "arithmetic": {"status": assessment["status"], "method": analysis.get("checks", []),
                           "scope": "Calcul local uniquement."},
            "documentary_grounding": {"status": "not_reexamined", "scope": "Preuves du dossier de départ seulement."},
            "external_validity": {"status": "not_established", "scope": "Aucune performance future ni décision réelle validée."},
        },
        "questions": [{"field": m.get("field"), "question": m.get("reason"), "blocking": True}
                      for m in analysis.get("missing", [])],
        "changes": {"changed_fields": list(actual_changes), "invalidated": [], "reused": []},
        "changes_kind": "dependency_preview_not_recorded_events", "simple_reference": None,
        "local": True, "local_notice": notice,
        "problem_qualified": False,
        "dependency_preview": dependency_preview(snapshot, actual_changes),
    }
    return {
        "version": version,
        "comparison": {"before": base, "after": version, "changes": delta,
                       "dependency_preview": version["dependency_preview"],
                       "kind": "local_preview_not_recorded_events"},
        "receipt": receipt,
    }


@router.post("/dossiers/{dossier_id}/preview")
def preview(dossier_id: str, body: PreviewRequest):
    snapshot = api.call(api.service().store.snapshot, dossier_id)
    selected = api.call(at_revision, snapshot, body.base_revision)
    return api.call(preview_snapshot, selected, body.changes)


@router.get("/dossiers/{dossier_id}/export")
def export(dossier_id: str, revision: int | None = Query(default=None, ge=1)):
    snapshot = api.call(api.service().store.snapshot, dossier_id)
    selected = api.call(at_revision, snapshot, revision)
    # Original artifacts, inputs, source captures, event and model receipts are
    # exported, not only the convenient UI projection.
    return JSONResponse(selected, headers={
        "Content-Disposition": f'attachment; filename="dossier-{dossier_id}-r{selected["revision"]}.json"',
        "X-Content-SHA256": digest(selected), "Cache-Control": "no-store",
    })
