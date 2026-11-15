"""Inspection locale du prototype, sans réseau ni modification du produit.

Depuis la racine :
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/refonte/inspection_diagnostic.py

Les appels API restent dans un processus isolé, avec rapports temporaires supprimés.
La sortie standard est le seul livrable. Aucune inférence Bedrock n'est demandée.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

import alphaforge_app.main as main
from alphaforge_app.personas import BY_ID


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request_for(persona):
    p = BY_ID[persona]
    return {
        "persona": persona,
        "prompt": p["prompt"],
        "portfolio": copy.deepcopy(p["portfolio"]),
        "settings": copy.deepcopy(p["settings"]),
        "use_ai": False,
    }


def post(client, payload):
    response = client.post("/api/analyze", json=payload)
    if response.status_code != 200:
        raise RuntimeError(response.text)
    return response.json()


def illustrative_numbers():
    # Hypothèses fictives, distinctes du snapshot et d'une prévision financière.
    D = Decimal
    assets = ["reserve_nominale", "XBB.TO", "ZST.TO", "XIU.TO", "TSLA"]
    portfolios = {
        "A_actuel": [D(0), D(".35"), D(".20"), D(".20"), D(".25")],
        "B_TSLA_5pct_proportionnel": [
            D(0), D(".35") * D(".95") / D(".75"),
            D(".20") * D(".95") / D(".75"),
            D(".20") * D(".95") / D(".75"), D(".05"),
        ],
        "C_reserve_30pct": [D(".30"), D(".35"), D(".05"), D(".20"), D(".10")],
        "D_revision_reserve_40pct": [D(".40"), D(".30"), D(0), D(".20"), D(".10")],
    }
    shocks = {
        "choc_actions": [D(0), D("-.05"), D(0), D("-.20"), D("-.50")],
        "choc_obligations": [D(0), D("-.15"), D("-.02"), D("-.10"), D("-.25")],
    }
    results = {}
    for name, weights in portfolios.items():
        withdrawal = D(40000) if name.startswith("D_") else D(30000)
        reserve = D(100000) * weights[0]
        losses = {
            scenario: -D(100000) * sum(w * r for w, r in zip(weights, returns))
            for scenario, returns in shocks.items()
        }
        turnover = sum(abs(w - initial) for w, initial in zip(weights, portfolios["A_actuel"])) / 2
        results[name] = {
            "weights": {a: float(w) for a, w in zip(assets, weights)},
            "reserve_cad": float(reserve),
            "withdrawal_cad": float(withdrawal),
            "turnover_one_way_pct": float(turnover * 100),
            "scenario_loss_cad": {s: float(v.quantize(D(".01"))) for s, v in losses.items()},
            "reserve_constraint_met": reserve >= withdrawal,
            "tsla_cap_10pct_met": weights[-1] <= D(".10"),
            "scenario_loss_budget_15000_met": all(v <= D(15000) for v in losses.values()),
            "wealth_after_withdrawal_cad": {
                s: float((D(100000) - v - withdrawal).quantize(D(".01")))
                for s, v in losses.items()
            } if reserve >= withdrawal else None,
        }
    return {
        "status": "illustration_arithmetique_uniquement_pas_un_resultat_du_produit",
        "capital_cad": 100000,
        "scenario_returns": {s: dict(zip(assets, map(float, r))) for s, r in shocks.items()},
        "assumptions": [
            "Réserve nominale fictive, rendement nul, disponible à douze mois.",
            "Ni frais, ni fiscalité, ni inflation ; allocations fractionnaires.",
            "Chocs hypothétiques à douze mois, sans probabilité ni calibration empirique.",
            "Le budget de perte porte sur ces chocs, pas sur le drawdown futur.",
            "La réserve nominale n'est assimilée à aucun FNB du starter.",
            "Le montant déplacé n'est pas une estimation des coûts de transaction.",
        ],
        "results": results,
    }


def inspect():
    product_paths = [p for p in (ROOT / "alphaforge_app").rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts]
    before = {str(p.relative_to(ROOT)): digest(p) for p in product_paths}
    archive_path = ROOT / "artifacts/ui-export.json"
    archive = json.loads(archive_path.read_text())
    archive_recomputed = main.calculate(copy.deepcopy(archive["request"]))
    saved_runtime = main.RUNTIME
    try:
        with tempfile.TemporaryDirectory(prefix="alphaforge-audit-") as directory:
            main.RUNTIME = Path(directory) / "reports"
            with TestClient(main.app) as client:
                base_request = request_for("robert")
                base = post(client, base_request)
                short_request = copy.deepcopy(base_request)
                short_request["settings"]["horizon_years"] = 1
                short = post(client, short_request)
                long_request = copy.deepcopy(base_request)
                long_request["settings"]["horizon_years"] = 15
                long = post(client, long_request)
                withdrawal_request = copy.deepcopy(base_request)
                withdrawal_request["prompt"] = (
                    "Mon capital est de 10 000 CAD. Je dois retirer 3 000 CAD dans "
                    "douze mois ; le reste peut rester investi quatre ans. "
                    "Ce besoin est impératif. Analyse les possibilités."
                )
                withdrawal = post(client, withdrawal_request)
                unsupported = copy.deepcopy(withdrawal_request)
                unsupported["withdrawals"] = [{"amount_cad": 3000, "months": 12}]
                rejected = client.post("/api/analyze", json=unsupported)
                semantic_inspection = {
                    "mode": "calculation_sans_inference",
                    "horizons_1_4_15_identical_comparisons": short["comparison"] == base["comparison"] == long["comparison"],
                    "returned_horizons": [r["profile"]["horizon_years"] for r in [short, base, long]],
                    "withdrawal_in_free_text_identical_comparison": withdrawal["comparison"] == base["comparison"],
                    "withdrawal_prompt": withdrawal_request["prompt"],
                    "withdrawal_still_listed_unknown": withdrawal["profile"]["unknown"],
                    "structured_withdrawals_http_status": rejected.status_code,
                    "structured_withdrawals_error": rejected.json(),
                    "scope": (
                        "En mode Bedrock, le modèle peut changer ticker/poids via l'outil. "
                        "Il ne dispose pas d'un outil de formalisation des retraits. "
                        "Aucune nouvelle génération n'a été testée ici."
                    ),
                }
    finally:
        main.RUNTIME = saved_runtime
    after = {str(p.relative_to(ROOT)): digest(p) for p in product_paths}
    calls = archive["agent"]["calls"]
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "product_content_unchanged": before == after,
        "product_file_hashes": before,
        "new_model_calls": 0,
        "representative_recorded_run": {
            "path": str(archive_path.relative_to(ROOT)),
            "sha256": digest(archive_path),
            "report_id": archive["id"],
            "created_at": archive["created_at"],
            "recorded_model_call_count": len(calls),
            "tools": archive["agent"]["tools"],
            "recorded_calls": calls,
            "exact_comparison_reproduced": archive_recomputed["comparison"] == archive["comparison"],
            "exact_scenarios_reproduced": archive_recomputed["scenarios"] == archive["scenarios"],
            "baseline_metrics": archive_recomputed["comparison"]["baseline"]["metrics"],
            "alternative_metrics": archive_recomputed["comparison"]["alternative"]["metrics"],
            "data_files": archive_recomputed["data"]["files"],
        },
        "semantic_inspection": semantic_inspection,
        "target_experience_illustration": illustrative_numbers(),
    }


if __name__ == "__main__":
    print(json.dumps(inspect(), ensure_ascii=False, indent=2, allow_nan=False))
