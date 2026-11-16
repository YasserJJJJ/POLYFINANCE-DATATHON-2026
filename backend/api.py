"""API locale (FastAPI). Sur AWS, le même code est servi par Lambda (lambda_handler.py, adaptateur Mangum).

Lancer : uvicorn api:app --reload --port 8000   (depuis le dossier backend/)
"""
from __future__ import annotations

import json
import queue
import threading

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from alphaforge import calculs, llm, sources, stockage
from alphaforge.agents import profileur
from alphaforge.donnees import serie_cad, univers
from alphaforge.dossier import Dossier
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
    return {"ok": True, "llm": llm.acces_verifie(), "raison": llm.raison_indisponible(),
            "modeles": {"principal": llm.nom(llm.MODELE_PRINCIPAL), "leger": llm.nom(llm.MODELE_LEGER)}}


@app.get("/api/personas")
def personas() -> dict:
    return PERSONAS


@app.get("/api/actifs")
def actifs() -> list[dict]:
    return univers().reset_index().to_dict(orient="records")


@app.get("/api/sources")
def sources_du_projet() -> dict:
    """Registre des sources : données, règles de calcul, références et choix de l'équipe (alphaforge/sources.py)."""
    return sources.registre()


@app.get("/api/questions")
def questions() -> list[dict]:
    return QUESTIONS_TOLERANCE


@app.post("/api/comprendre")
def comprendre(req: Requete) -> dict:
    """Étape « On vérifie ensemble » : seulement le Profileur (rapide, sans calcul de marché)."""
    d = Dossier(profil=dict(req.profil), demande=dict(req.demande))
    profileur.executer(d)
    return {"profil": d.profil, "demande": d.demande, "questions": d.questions}


@app.get("/api/serie/{ticker}")
def serie(ticker: str) -> dict:
    """Prix hebdomadaire en CAD, base 100, pour le graphique de la pire chute."""
    try:
        s = serie_cad(ticker).resample("W-FRI").last().dropna()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    base = float(s.iloc[0])
    return {"ticker": ticker, "pire_chute": calculs.pire_chute(ticker),
            "points": [{"date": str(i.date()), "valeur": round(float(v) / base * 100, 2)} for i, v in s.items()]}


@app.post("/api/analyse")
def analyse(req: Requete) -> dict:
    try:
        dossier = analyser(req.profil, req.demande)
    except KeyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    stockage.sauvegarder_dossier(dossier)  # archivage S3 sur AWS ; sans effet en local
    return dossier


@app.post("/api/analyse/flux")
def analyse_flux(req: Requete) -> StreamingResponse:
    """Même analyse, envoyée au fil de l'eau : une ligne JSON par étape terminée, puis le dossier complet.
    Sur Lambda (Mangum), la réponse arrive d'un bloc à la fin : l'interface sait aussi lire ce cas."""
    file: queue.Queue = queue.Queue()

    def travail() -> None:
        try:
            dossier = analyser(req.profil, req.demande, lambda e: file.put({"type": "etape", **e}))
            stockage.sauvegarder_dossier(dossier)
            file.put({"type": "dossier", "dossier": dossier})
        except KeyError as e:
            file.put({"type": "erreur", "statut": 422, "detail": str(e)})
        except Exception as e:  # noqa: BLE001 - l'erreur est envoyée à l'interface au lieu de couper le flux
            file.put({"type": "erreur", "statut": 500, "detail": type(e).__name__})
        file.put(None)

    threading.Thread(target=travail, daemon=True).start()

    def lignes():
        while (message := file.get()) is not None:
            yield json.dumps(message, ensure_ascii=False, default=str) + "\n"

    return StreamingResponse(lignes(), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
