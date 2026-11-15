from __future__ import annotations

import copy
import json
import math
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .evidence import SOURCES
from .personas import BY_ID, PERSONAS

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / "runtime"
STATIC = Path(__file__).parent / "static"
app = FastAPI(title="AlphaForge · Folio", version="0.7.0", docs_url="/api/docs")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])
_dataset = None
_dataset_lock = threading.Lock()


class Holding(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    ticker: str = Field(min_length=1, max_length=20)
    weight: float = Field(ge=0, le=1)


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    horizon_years: float = Field(default=4, gt=0, le=50)
    capital: float = Field(default=10000, ge=1, le=1e9)
    currency: Literal["CAD"] = "CAD"
    max_drawdown_pct: float = Field(default=15, ge=0, le=100)
    focus_ticker: str = Field(default="TSLA", min_length=1, max_length=20)
    focus_weight: float = Field(default=5, ge=0, le=100)


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(default="", max_length=8000)
    persona: Literal["robert", "amira", "mateo"] = "robert"
    portfolio: list[Holding] = Field(default_factory=list, max_length=31)
    settings: Settings = Field(default_factory=Settings)
    use_ai: bool = False

    @model_validator(mode="before")
    @classmethod
    def persona_settings(cls, value):
        if not isinstance(value, dict):
            return value
        persona = BY_ID.get(value.get("persona", "robert"))
        if persona is None:
            return value
        supplied = value.get("settings", {})
        if isinstance(supplied, Settings):
            supplied = supplied.model_dump(exclude_unset=True)
        if not isinstance(supplied, dict):
            return value
        return {**value, "settings": {**persona["settings"], **supplied}}

    @model_validator(mode="after")
    def validate_portfolio(self):
        if self.portfolio:
            tickers = [h.ticker for h in self.portfolio]
            if len(tickers) != len(set(tickers)):
                raise ValueError("Un symbole ne peut apparaître qu’une fois.")
            if not math.isclose(sum(h.weight for h in self.portfolio), 1, abs_tol=1e-7):
                raise ValueError("Les poids doivent totaliser 100 %.")
        return self


def get_dataset():
    global _dataset
    if _dataset is None:
        with _dataset_lock:
            if _dataset is None:
                from .datasets import load_dataset
                _dataset = load_dataset()
    return _dataset


def assets_list():
    data = get_dataset()
    assets = data.assets
    return list(assets.values()) if isinstance(assets, dict) else assets


def calculate(payload: dict) -> dict:
    from .analytics import compare_portfolios, set_target_weight

    weights = {h["ticker"]: h["weight"] for h in payload["portfolio"] if h["weight"] > 0}
    settings = payload["settings"]
    ticker = settings["focus_ticker"]
    known = {a["ticker"] for a in assets_list()}
    missing = (set(weights) | {ticker}) - known
    if missing:
        raise ValueError("Symbole absent de l’instantané : " + ", ".join(sorted(missing)))
    variant = set_target_weight(weights, ticker, settings["focus_weight"] / 100)
    result = compare_portfolios(
        [{"id": "baseline", "name": "Portefeuille de référence", "weights": weights},
         {"id": "alternative", "name": "Hypothèse modifiée", "weights": variant}],
        capital_cad=settings["capital"], dataset=get_dataset(),
    )
    baseline, alternative = result["options"]
    for option in (baseline, alternative):
        option["portfolio"] = [{"ticker": k, "weight": v} for k, v in option["weights"].items()]
    b_scenarios = {s["id"]: s for s in baseline["scenarios"]}
    scenarios = [
        {"name": s["name"], "start": s["start"], "end": s["end"],
         "baseline_return_pct": b_scenarios[s["id"]]["total_return_pct"],
         "alternative_return_pct": s["total_return_pct"]}
        for s in alternative["scenarios"] if s["id"] in b_scenarios
    ]
    return {"comparison": {"baseline": baseline, "alternative": alternative},
            "scenarios": scenarios, "data": result["meta"]}


def observations(payload, result):
    settings = payload["settings"]
    b = result["comparison"]["baseline"]["metrics"]
    a = result["comparison"]["alternative"]["metrics"]
    ticker = settings["focus_ticker"]
    current = next((h["weight"] * 100 for h in payload["portfolio"] if h["ticker"] == ticker), 0)
    threshold = settings["max_drawdown_pct"]
    bdd, add = abs(b["max_drawdown_pct"]), abs(a["max_drawdown_pct"])
    risk_direction = "moins forte" if add < bdd else "plus forte" if add > bdd else "identique"
    observations = [
        {"id": "drawdown", "text": f"La baisse maximale historique passe de {bdd:.1f} % à {add:.1f} % : elle est {risk_direction} dans l’hypothèse modifiée.", "source_ids": ["starter", "method"]},
        {"id": "focus", "text": f"L’exposition directe initiale à {ticker} passe de {current:.1f} % à {settings['focus_weight']:.1f} %. Les autres positions sont redimensionnées proportionnellement.", "source_ids": ["method"]},
        {"id": "comfort", "text": f"La baisse historique de l’hypothèse modifiée {'dépasse' if add > threshold else 'ne dépasse pas'} le repère de confort de {threshold:g} %. Ce repère ne garantit pas un plafond de perte future.", "source_ids": ["method", "cfa"]},
        {"id": "tradeoff", "text": f"Sur cette période passée, le rendement cumulé est de {b['total_return_pct']:.1f} % pour la référence et de {a['total_return_pct']:.1f} % pour l’hypothèse modifiée. Le classement historique ne prédit pas le classement futur.", "source_ids": ["starter", "method"]},
        {"id": "horizon", "text": "L’horizon déclaré décrit le besoin de l’investisseur. Il ne transforme pas l’historique disponible en prévision ; les besoins de retrait et la capacité de perte restent à préciser.", "source_ids": ["cfa"]},
        {"id": "lookthrough", "text": "Le nombre de lignes du portefeuille ne mesure pas ses expositions économiques. La composition détaillée des FNB manque : les recouvrements avec les actions détenues restent à vérifier.", "source_ids": ["starter"]},
        {"id": "esg", "text": "Retirer une position directe ne certifie pas les autres placements : l’instantané ne fournit ni compositions détaillées des FNB ni preuves de controverses ESG.", "source_ids": ["starter", "cfa"]},
    ]
    return observations


@app.middleware("http")
async def local_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method == "POST" and origin and origin != str(request.base_url).rstrip("/"):
        return JSONResponse({"detail": "Cette application accepte les requêtes de son interface locale."}, status_code=403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.get("/api/health")
def health():
    return {"status": "ok", "version": app.version, "hosting": "local",
            "application": "alphaforge", "workspace": str(ROOT),
            "inference": "AWS Bedrock", "region": "us-east-1"}


@app.get("/api/bootstrap")
def bootstrap():
    return {
        "assets": assets_list(), "personas": PERSONAS,
        "methodology": {"title": "Comparer des hypothèses, comprendre les compromis",
                        "currency": "CAD", "period": "2021–2026",
                        "description": "Rejeu historique de deux allocations fictives, dividendes réinvestis. Aucune prévision de rendement.",
                        "assumptions": "Montants, avoirs et repères de confort des démonstrations ajoutés par AlphaForge et modifiables."},
        "sources": SOURCES, "version": app.version,
    }


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    started = time.perf_counter()
    payload = request.model_dump()
    if not payload["portfolio"]:
        payload["portfolio"] = copy.deepcopy(BY_ID[request.persona]["portfolio"])
    try:
        result = calculate(payload)
    except (ValueError, KeyError) as exc:
        raise HTTPException(422, str(exc)) from exc
    persona = BY_ID[request.persona]
    obs = observations(payload, result)
    findings = [o for o in obs if o["id"] in ("drawdown", "focus", "comfort", "horizon")]
    if request.persona == "mateo":
        findings.append(next(o for o in obs if o["id"] == "esg"))
    profile = {
        "name": persona["name"], "horizon_years": request.settings.horizon_years,
        "risk_tolerance": persona["risk_tolerance"], "goal": persona["goal"],
        "known": ["Profil de démonstration sélectionné", "Horizon et hypothèses éditables"],
        "unknown": ["Besoins de retrait", "Capacité financière réelle à supporter une perte"],
        "contradictions": [],
    }
    response = {
        "id": uuid.uuid4().hex, "mode": "calculation", "profile": profile,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary": {"title": "Une hypothèse change. Les conséquences deviennent visibles.",
                    "text": "Les chiffres ci-dessous comparent deux allocations sur le même historique. Modifie l’exposition étudiée pour explorer le compromis ; l’agent peut ensuite examiner ta demande et sélectionner les preuves pertinentes.",
                    "findings": findings},
        **result, "sources": SOURCES,
        "trace": [{"step": 1, "tool": "compare_portfolios", "status": "success",
                   "detail": "Calcul réel en CAD, calendrier commun et scénarios historiques.",
                   "duration_ms": round((time.perf_counter() - started) * 1000)}],
        "limitations": list(result["data"].get("limitations", [])),
        "settings": payload["settings"], "request": payload,
        "observations": obs, "agent": None,
    }
    response["limitations"] += [
        "Les avoirs et le capital des personas sont des hypothèses fictives modifiables.",
        "Aucune certification ESG, aucun modèle de prévision ni garantie de capital.",
        "La composition interne des FNB n’est pas disponible dans cet instantané.",
    ]
    if request.use_ai:
        attempted = copy.deepcopy(response)
        try:
            from .orchestrator import enrich
            response = enrich(copy.deepcopy(payload), attempted, calculate, observations)
        except Exception as exc:
            from .bedrock import BedrockError
            response["mode"] = "calculation"
            response["agent"] = {"status": "error", "message": "L’analyse Bedrock n’a pas abouti. Les calculs affichés restent ceux du moteur local."}
            if isinstance(exc, BedrockError):
                response["agent"]["error"] = exc.as_dict()
            elif isinstance(exc, (ValueError, TimeoutError)):
                response["agent"]["error"] = {
                    "code": "AgentValidationError" if isinstance(exc, ValueError) else "AgentTimeout",
                    "message": str(exc), "retryable": True,
                }
            response["trace"] = attempted["trace"]
            response["trace"].append({"step": len(response["trace"]) + 1, "tool": "bedrock",
                                      "status": "error", "detail": type(exc).__name__,
                                      "request_id": getattr(exc, "request_id", None)})
            response["limitations"].append("Analyse d’agent indisponible pour cette exécution ; aucun remplacement de fournisseur.")
    response["duration_ms"] = round((time.perf_counter() - started) * 1000)
    RUNTIME.mkdir(exist_ok=True)
    dest = RUNTIME / f"{response['id']}.json"
    temp = dest.with_suffix(".tmp")
    temp.write_text(json.dumps(response, ensure_ascii=False, indent=2, allow_nan=False))
    temp.replace(dest)
    return response


@app.get("/api/report/{analysis_id}")
def report(analysis_id: str):
    if len(analysis_id) != 32 or any(c not in "0123456789abcdef" for c in analysis_id):
        raise HTTPException(404)
    path = RUNTIME / f"{analysis_id}.json"
    if not path.is_file():
        raise HTTPException(404)
    return FileResponse(path, media_type="application/json", filename=f"alphaforge-{analysis_id[:8]}.json")


@app.get("/api/source/{source_id}", response_class=PlainTextResponse)
def source(source_id: str):
    files = {
        "starter": Path(get_dataset().directory) / "README.md",
        "method": ROOT / "docs/methodology.md",
        "case": ROOT / "data/Datathon_Case_Officiel_2026_FR.md",
    }
    path = files.get(source_id)
    if path is None or not path.is_file():
        raise HTTPException(404)
    return path.read_text()


@app.get("/")
def index():
    return FileResponse(STATIC / "folio" / "index.html", headers={"Cache-Control": "no-store"})


@app.get("/workbench")
def workbench():
    return FileResponse(STATIC / "workbench.html")


@app.get("/legacy")
def legacy():
    return FileResponse(STATIC / "index.html")


from .decision.api import router as decision_router
app.include_router(decision_router)
from .decision.folio_api import router as folio_router
app.include_router(folio_router)


if STATIC.exists():
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
