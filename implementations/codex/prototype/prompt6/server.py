"""Local reference prototype: archived dossiers + isolated deterministic exploration.

Launch: .venv/bin/python -m uvicorn prototype.prompt6.server:app --host 127.0.0.1 --port 8770
No access to DossierStore, no AWS client and no write to the product's state.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

from alphaforge_app.decision.finance import analyze
from alphaforge_app.decision.models import ProblemSpec
from .build_data import HERE, ROOT, stats

app = FastAPI(title="AlphaForge — prototype de référence", version="0.6-prototype")
DATA = json.loads((HERE / "data/cases.json").read_text())
INDEX = {c["id"]: c for c in DATA["cases"]}


@app.middleware("http")
async def local_mutations_only(request: Request, call_next):
    # The prototype is a local tool, not a remotely callable calculation service.
    if request.method == "POST":
        origin = request.headers.get("origin")
        if origin and origin not in {"http://127.0.0.1:8770", "http://localhost:8770"}:
            return JSONResponse({"detail": "Origine externe refusée."}, status_code=403)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


def version_for(case_id: str, version_id: str | None = None) -> dict:
    case = INDEX.get(case_id)
    if not case:
        raise HTTPException(404, "Dossier de référence inconnu.")
    version_id = version_id or case["default_version_id"]
    for version in case["versions"]:
        if version["id"] == version_id:
            return version
    raise HTTPException(404, "Version de référence inconnue.")


@app.get("/api/prototype/health")
def health():
    return {
        "status": "ok", "version": app.version, "mode": "prototype",
        "inference_calls": 0, "product_mutations": False,
        "exploration": "existing_finance_engine_on_copied_inputs",
    }


@app.get("/api/prototype/cases")
def list_cases():
    return {k: v for k, v in DATA.items() if k != "cases"} | {
        "cases": [{k: v for k, v in c.items() if k != "versions"} for c in DATA["cases"]],
    }


@app.get("/api/prototype/cases/{case_id}")
def case(case_id: str):
    version_for(case_id)
    return INDEX[case_id]


@app.get("/api/prototype/source/{case_id}/{version_id}")
def source(case_id: str, version_id: str):
    version = version_for(case_id, version_id)
    path = ROOT / version["source"]["export"]
    # Refuse a changed source rather than download data under the old hash.
    if hashlib.sha256(path.read_bytes()).hexdigest() != version["source"]["export_sha256"]:
        raise HTTPException(409, "L'export source a changé depuis la préparation du prototype.")
    return FileResponse(path, media_type="application/json", filename=f"{case_id}-{version_id}-dossier.json")


class ExploreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: str = "robert"
    version_id: str | None = None
    changes: dict[str, Any] = Field(default_factory=dict, max_length=4)
    simulate_error: bool = False


ALLOWED = {
    "capital_cad": (0, 1e12, "CAD"),
    "withdrawal_cad": (0, 1e12, "CAD"),
    "scenario_loss_limit_cad": (0, 1e12, "CAD"),
    "tsla_cap": (0, 1, "fraction"),
}


@app.post("/api/prototype/explore")
async def explore(request: ExploreRequest):
    version = version_for(request.case_id, request.version_id)
    if request.case_id != "robert":
        raise HTTPException(422, "L'exploration locale porte actuellement sur le modèle de réserve de Robert. Les autres dossiers restent consultables.")
    if request.simulate_error:
        raise HTTPException(503, {
            "code": "prototype_simulated_error",
            "message": "Erreur simulée pour examiner la reprise. Aucun calcul lancé ; le dossier principal est intact.",
            "simulated": True, "retry": "Renvoyer les mêmes paramètres avec simulate_error=false.",
        })
    problem = deepcopy(version["problem"])
    changes = []
    for field, value in request.changes.items():
        if field not in ALLOWED:
            raise HTTPException(422, f"Paramètre non exposé dans cette exploration : {field}.")
        low, high, unit = ALLOWED[field]
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise HTTPException(422, f"{field} requiert un nombre fini entre {low} et {high} {unit}.")
        if field == "capital_cad" and value == 0:
            raise HTTPException(422, "Le capital doit être strictement positif.")
        before = problem["max_asset_weights"].get("TSLA") if field == "tsla_cap" else problem[field]
        if field == "tsla_cap":
            problem["max_asset_weights"]["TSLA"] = value
        else:
            problem[field] = value
        if before != value:
            changes.append({"field": field, "before": before, "after": value, "unit": unit,
                            "origin": "declared_for_local_scenario"})
    problem = ProblemSpec.model_validate(problem).model_dump()
    # The existing deterministic tool does the work. No LLM, task loop, checkpoint
    # or archived conclusion is used to generate these results.
    analysis = await run_in_threadpool(analyze, problem)
    analysis_hash = hashlib.sha256(json.dumps(analysis, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    baseline_unchanged = not any(c["field"] == "capital_cad" for c in changes)
    dependency_preview = {
        "kind": "dependency_preview_not_recorded_events",
        "label": "Dépendances prévues pour une future révision du dossier ; aucun événement d'agent produit ici.",
        "reusable": ["Scénarios déclarés", "Positions initiales", "Bibliographie générique"],
        "to_review": ["Qualification du besoin", "Applicabilité documentaire", "Conclusion et restitution"],
        "recalculated": ["Allocation", "Contraintes", "Sensibilités"],
        "baseline_stress": "unchanged_inputs_reusable_in_future_revision" if baseline_unchanged else "dependent_on_changed_capital",
        "local_execution": "all_applicable_numeric_results_reexecuted_without_artifact_cache",
        "local_execution_notice": "Les calculs locaux, y compris le diagnostic initial applicable, sont réexécutés. Les résultats indiqués comme réutilisables décrivent une future révision, pas un réemploi réalisé ici.",
    }
    if baseline_unchanged:
        dependency_preview["reusable"].append("Diagnostic des pertes du portefeuille initial")
    else:
        dependency_preview["to_review"].append("Diagnostic initial : les pertes CAD dépendent du capital")
    return {
        "mode": "local_calculation",
        "notice": "Calcul déterministe réel sur une copie des paramètres. Aucun agent relancé, aucune révision du dossier produit.",
        "base_case_id": request.case_id, "base_version_id": version["id"],
        "base_source": version["source"], "problem": problem, "analysis": analysis,
        "stats": stats(analysis), "claims": analysis.get("claims", []),
        "limits": analysis.get("limitations", []), "changes": changes,
        "dependency_preview": dependency_preview,
        "receipt": {
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "implementation": "alphaforge_app.decision.finance.analyze",
            "result_sha256": analysis_hash, "inference_calls": 0, "product_mutations": 0,
            "artifact_cache_reused": False,
            "source_sha256": hashlib.sha256((ROOT / "alphaforge_app/decision/finance.py").read_bytes()).hexdigest(),
        },
        "simple_reference": None,
        "simple_reference_notice": "La référence simple publiée concerne seulement le dossier Robert r5. Elle n'est pas extrapolée à cette variante.",
    }


# Only the prototype directory is exposed, never the repository or runtime state.
app.mount("/", StaticFiles(directory=HERE, html=True), name="prototype")
