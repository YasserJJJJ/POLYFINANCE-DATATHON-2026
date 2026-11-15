"""API locale (FastAPI). Sur AWS, le même code sera servi par Lambda / AgentCore.

Lancer : uvicorn api:app --reload --port 8000   (depuis le dossier backend/)
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from alphaforge.donnees import univers
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS
from alphaforge.profil import QUESTIONS_TOLERANCE

app = FastAPI(title="AlphaForge API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Requete(BaseModel):
    profil: dict
    demande: dict


@app.get("/api/sante")
def sante() -> dict:
    return {"ok": True}


@app.get("/api/personas")
def personas() -> dict:
    return PERSONAS


@app.get("/api/actifs")
def actifs() -> list[dict]:
    return univers().reset_index().to_dict(orient="records")


@app.get("/api/questions")
def questions() -> list[dict]:
    return QUESTIONS_TOLERANCE


@app.post("/api/analyse")
def analyse(req: Requete) -> dict:
    try:
        return analyser(req.profil, req.demande)
    except KeyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
