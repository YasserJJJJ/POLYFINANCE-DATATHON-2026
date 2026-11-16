"""API locale (FastAPI). Sur AWS, le même code est servi par Lambda (lambda_handler.py, adaptateur Mangum).

Lancer : uvicorn api:app --reload --port 8000   (depuis le dossier backend/)
"""
from __future__ import annotations

import json
import math
import queue
import threading

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from alphaforge import calculs, gardien, llm, sources, stockage
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


def _nombre_saisi(valeur):
    """Convertit les chaînes numériques ; conserve les autres pour la règle donnees."""
    if isinstance(valeur, str):
        try:
            nombre = float(valeur)
        except ValueError:
            return valeur
        if math.isfinite(nombre):
            return int(nombre) if nombre.is_integer() else nombre
    # Une entrée non finie doit rester sérialisable dans le dossier d'erreur.
    if isinstance(valeur, float) and not math.isfinite(valeur):
        return str(valeur)
    return valeur


def _normaliser_requete(req: Requete) -> Requete:
    profil, demande = dict(req.profil), dict(req.demande)
    for champ in ("horizon_ans", "epargne_totale_cad", "somme_a_preserver_cad",
                  "retrait_prevu_ans", "tolerance"):
        if champ in profil:
            profil[champ] = _nombre_saisi(profil[champ])
    if "montant_cad" in demande:
        demande["montant_cad"] = _nombre_saisi(demande["montant_cad"])
    if isinstance(profil.get("exclusions"), str):
        profil["exclusions"] = [profil["exclusions"]]
    return Requete(profil=profil, demande=demande)


def _dossier_invalide(req: Requete) -> Dossier | None:
    erreurs = gardien.erreurs_entree(req.profil, req.demande)
    if not erreurs:
        return None
    d = Dossier(profil=req.profil, demande=req.demande)
    d.regles = gardien.appliquer_regles(d.profil, d.demande, {})
    d.verdict = gardien.verdict(d.regles)
    d.questions = erreurs
    return d


def _analyser_requete(req: Requete, sur_etape=None) -> dict:
    req = _normaliser_requete(req)
    ticker = req.demande.get("ticker")
    if ticker and (not isinstance(ticker, str) or ticker not in univers().index):
        raise HTTPException(status_code=422, detail=(
            f"L'actif demandé ne fait pas partie des {len(univers())} actifs du jeu de départ."
        ))
    invalide = _dossier_invalide(req)
    if invalide is not None:
        return invalide.to_dict()
    return analyser(req.profil, req.demande, sur_etape)


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
    req = _normaliser_requete(req)
    invalide = _dossier_invalide(req)
    if invalide is not None:
        return {"profil": invalide.profil, "demande": invalide.demande, "questions": invalide.questions}
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
        dossier = _analyser_requete(req)
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
            dossier = _analyser_requete(req, lambda e: file.put({"type": "etape", **e}))
            stockage.sauvegarder_dossier(dossier)
            file.put({"type": "dossier", "dossier": dossier})
        except HTTPException as e:
            file.put({"type": "erreur", "statut": e.status_code, "detail": e.detail})
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
