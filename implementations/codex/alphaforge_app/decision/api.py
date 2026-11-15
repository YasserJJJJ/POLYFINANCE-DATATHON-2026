from __future__ import annotations

import threading
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .models import DisplayRequest, NewDossier, RevisionRequest
from .service import DecisionService
from .store import Conflict, Missing

router = APIRouter(prefix="/api/dossiers")
_service = None
_lock = threading.Lock()
ROOT = Path(__file__).resolve().parents[2] / "runtime" / "decision"


def service():
    global _service
    with _lock:
        if _service is None:
            _service = DecisionService(ROOT)
        return _service


def call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Missing as exc:
        raise HTTPException(404, "Dossier ou pièce introuvable.") from exc
    except Conflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except (ValueError, ValidationError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/examples")
def examples():
    from .finance import examples as values
    return {"examples": values()}


@router.get("")
def dossiers():
    return {"dossiers": service().store.list()}


@router.post("", status_code=202)
def create(body: NewDossier):
    return call(service().create, body.prompt, body.facts, body.use_ai)


@router.get("/{dossier_id}")
def snapshot(dossier_id: str):
    return call(service().store.snapshot, dossier_id)


@router.post("/{dossier_id}/revise", status_code=202)
def revise(dossier_id: str, body: RevisionRequest):
    return call(service().revise, dossier_id, body.message, body.changes, body.base_revision, body.intent)


@router.post("/{dossier_id}/resume", status_code=202)
def resume(dossier_id: str):
    return call(service().resume, dossier_id)


@router.get("/{dossier_id}/export")
def export(dossier_id: str):
    value = call(service().store.snapshot, dossier_id)
    return JSONResponse(value, headers={"Content-Disposition": f'attachment; filename="dossier-{dossier_id}.json"'})


@router.get("/{dossier_id}/artifacts/{artifact_id}/{version}")
def artifact(dossier_id: str, artifact_id: str, version: int):
    return call(service().store.artifact, dossier_id, f"{artifact_id}@{version}")


@router.post("/{dossier_id}/display")
def display(dossier_id: str, body: DisplayRequest):
    return {"event_id": call(service().store.record_display, dossier_id, body.view_ref)}
