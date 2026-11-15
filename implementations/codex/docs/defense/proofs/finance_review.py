"""Independent P5 finance audit. Python calculations only; no model client.

Run: .venv/bin/python docs/defense/proofs/finance_review.py
The CSV oracle does not use datasets.py or analytics.py. The reserve oracle
enumerates vertices/kinks in weight space and does not call an LP solver.
"""
from __future__ import annotations

import bisect
import copy
import csv
import hashlib
import itertools
import json
import math
import statistics
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from alphaforge_app.decision import finance


def example(name):
    return copy.deepcopy(next(e["facts"] for e in finance.examples() if e["id"] == name))


def reserve_metrics(problem, weights):
    """Literal financial identities; no production helpers."""
    initial = {h["ticker"]: h["weight"] for h in problem["holdings"]}
    initial.setdefault("RESERVE_ABSTRAITE", 0)
    capital, withdrawal = problem["capital_cad"], problem["withdrawal_cad"]
    losses = {
        s["id"]: -capital * math.fsum(weights.get(t, 0) * s["returns"].get(t, 0)
                                     for t in weights)
        for s in problem["scenarios"]
    }
    residuals = {
        "budget": abs(math.fsum(weights.values()) - 1),
        "nonnegative": max(-min(weights.values()), 0),
        "reserve": max(withdrawal / capital - weights.get("RESERVE_ABSTRAITE", 0), 0),
        **{"cap:" + t: max(weights.get(t, 0) - cap, 0)
           for t, cap in problem["max_asset_weights"].items()},
    }
    if problem["scenario_loss_limit_cad"] is not None:
        residuals.update({"loss:" + name: max(loss - problem["scenario_loss_limit_cad"], 0) / capital
                          for name, loss in losses.items()})
    funded = weights.get("RESERVE_ABSTRAITE", 0) * capital >= withdrawal - capital * 1e-8
    return {
        "turnover_cad": capital * sum(abs(weights.get(t, 0) - w) for t, w in initial.items()) / 2,
        "losses_cad": losses,
        "wealth_after_withdrawal_cad": {k: capital - loss - withdrawal if funded else None
                                        for k, loss in losses.items()},
        "max_violation_fraction": max(residuals.values()),
    }


def vertex_minimum(problem):
    """Enumerate all constraint/kink vertices of the convex piecewise-linear objective."""
    initial = {h["ticker"]: h["weight"] for h in problem["holdings"]}
    initial.setdefault("RESERVE_ABSTRAITE", 0)
    names = sorted(initial)
    n = len(names)
    constraints, boundaries = [], []
    for i, name in enumerate(names):
        row = np.eye(n)[i]
        upper = problem["max_asset_weights"].get(name, 1)
        constraints += [(-row, 0), (row, upper)]
        boundaries += [(row, 0), (row, upper), (row, initial[name])]
    row = np.eye(n)[names.index("RESERVE_ABSTRAITE")]
    q = problem["withdrawal_cad"] / problem["capital_cad"]
    constraints.append((-row, -q))
    boundaries.append((row, q))
    if problem["scenario_loss_limit_cad"] is not None:
        for scenario in problem["scenarios"]:
            row = np.array([-scenario["returns"].get(t, 0) for t in names])
            rhs = problem["scenario_loss_limit_cad"] / problem["capital_cad"]
            constraints.append((row, rhs))
            boundaries.append((row, rhs))
    unique = {(tuple(row), rhs): (row, rhs) for row, rhs in boundaries}
    best = None
    feasible_count = 0
    for chosen in itertools.combinations(unique.values(), n - 1):
        matrix = np.array([np.ones(n), *[r for r, _ in chosen]])
        rhs = np.array([1, *[b for _, b in chosen]])
        try:
            point = np.linalg.solve(matrix, rhs)
        except np.linalg.LinAlgError:
            continue
        if max(float(r @ point - b) for r, b in constraints) > 1e-9:
            continue
        feasible_count += 1
        turnover = sum(abs(point[i] - initial[t]) for i, t in enumerate(names)) / 2
        if best is None or turnover < best["turnover_fraction"]:
            best = {"turnover_fraction": float(turnover),
                    "weights": {t: float(point[i]) for i, t in enumerate(names)}}
    return {"feasible_vertices_counted": feasible_count, "minimum": best,
            "method": "Intersection de n-1 frontières/ruptures avec le budget; aucun solveur LP."}


def raw_csv_history(weights, capital=25000, ignore_fx=False, rebalance=False):
    """Rebuild CAD wealth, CAGR, drawdown and dispersion directly from original CSVs."""
    folder = ROOT / "data/alphaforge_starter"
    def read(name):
        with (folder / name).open(newline="", encoding="utf-8-sig") as stream:
            return list(csv.DictReader(stream))
    assets = {r["ticker"]: r for r in read("assets_universe.csv")}
    prices = {t: {} for t in assets}
    for row in read("prices_daily.csv"):
        prices[row["ticker"]][row["date"]] = float(row["adj_close"])
    days = sorted(set.intersection(*(set(prices[t]) for t in assets
                                     if assets[t]["asset_class"] != "crypto")))
    fx = {r["date"]: float(r["usdcad"]) for r in read("fx_usdcad_daily.csv")}
    fx_days = sorted(fx)
    fx_used = {d: fx_days[bisect.bisect_right(fx_days, d) - 1] for d in days}
    panel = {
        t: [prices[t][d] * (fx[fx_used[d]] if assets[t]["currency"] == "USD" and not ignore_fx else 1)
            for d in days] for t in weights
    }
    if rebalance:
        wealth = [capital]
        for i in range(1, len(days)):
            wealth.append(wealth[-1] * sum(w * panel[t][i] / panel[t][i - 1] for t, w in weights.items()))
    else:
        wealth = [capital * sum(w * panel[t][i] / panel[t][0] for t, w in weights.items())
                  for i in range(len(days))]
    years = (date.fromisoformat(days[-1]) - date.fromisoformat(days[0])).days / 365.2425
    returns = [wealth[i] / wealth[i - 1] - 1 for i in range(1, len(wealth))]
    running_peak, max_dd = wealth[0], 0
    for value in wealth:
        running_peak = max(running_peak, value)
        max_dd = min(max_dd, value / running_peak - 1)
    return {
        "start": days[0], "end": days[-1], "observations": len(days),
        "fx_carried_dates": sum(d != fx_used[d] for d in days),
        "max_fx_age_days": max((date.fromisoformat(d) - date.fromisoformat(fx_used[d])).days for d in days),
        "metrics": {
            "ending_value_cad": wealth[-1],
            "total_return_pct": (wealth[-1] / wealth[0] - 1) * 100,
            "cagr_pct": ((wealth[-1] / wealth[0]) ** (1 / years) - 1) * 100,
            "volatility_pct": statistics.stdev(returns) * math.sqrt(len(returns) / years) * 100,
            "max_drawdown_pct": max_dd * 100,
        },
        "days": days, "wealth": wealth,
    }


def compact_history(history):
    return {k: v for k, v in history.items() if k not in {"days", "wealth"}}


def run():
    output = {
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "inference": {"model_calls": 0, "scope": "Contrôles Python; aucune simulation de modèle"},
        "code_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in [Path(finance.__file__), Path(__file__)]},
        "data_sha256": {
            name: hashlib.sha256((ROOT / "data/alphaforge_starter" / name).read_bytes()).hexdigest()
            for name in ["assets_universe.csv", "prices_daily.csv",
                         "fx_usdcad_daily.csv", "sources_metadata.csv"]
        },
        "reserve_cases": {}, "historical_cases": {}, "boundary_cases": {},
    }
    for name, changes in [
        ("robert_30000", {}), ("robert_40000", {"withdrawal_cad": 40000}),
        ("tight_loss_1000", {"scenario_loss_limit_cad": 1000}),
        ("cap_1_percent", {"max_asset_weights": {"TSLA": .01}}),
        ("impossible_withdrawal_110000", {"withdrawal_cad": 110000}),
    ]:
        problem = example("robert")
        problem.update(changes)
        analysis = finance.analyze(problem)
        output["reserve_cases"][name] = {
            "problem": problem, "status": analysis["status"], "checks": analysis["checks"],
            "claims": analysis["claims"], "oracle": vertex_minimum(problem),
            "options": [{"id": o["id"], "weights": o["weights"],
                         "independent": reserve_metrics(problem, o["weights"])}
                        for o in analysis["options"]],
        }
    problem = example("robert")
    benchmark = {"RESERVE_ABSTRAITE": .3, "TSLA": .1, "XBB.TO": .28, "XIU.TO": .16, "ZST.TO": .16}
    output["simple_reserve_reference"] = {
        "construction": "Vendre TSLA à 10 %, financer le solde du retrait proportionnellement aux trois autres positions.",
        "weights": benchmark, "independent": reserve_metrics(problem, benchmark),
    }
    for name, weights in [
        ("amira_initial", {"SPY": .45, "XIU.TO": .30, "TSLA": .25}),
        ("amira_target", {"SPY": .54, "XIU.TO": .36, "TSLA": .10}),
        ("simple_equal_thirds", {"SPY": 1 / 3, "XIU.TO": 1 / 3, "TSLA": 1 / 3}),
    ]:
        output["historical_cases"][name] = compact_history(raw_csv_history(weights))
    output["negative_controls"] = {
        "wrongly_omit_fx": compact_history(raw_csv_history({"SPY": .45, "XIU.TO": .30, "TSLA": .25}, ignore_fx=True)),
        "different_daily_rebalancing": compact_history(raw_csv_history({"SPY": .45, "XIU.TO": .30, "TSLA": .25}, rebalance=True)),
        "scope": "Calculs volontairement différents, jamais présentés comme le résultat du produit.",
    }
    for name, changes in [
        ("missing_policy", {"historical_policy": None}),
        ("other_redistribution", {"historical_policy": {"redistribution": "other", "window": {"kind": "all_common_available"}}}),
        ("specified_window", {"historical_policy": {"redistribution": "proportional_other_holdings",
                                                  "window": {"kind": "specified_window", "start_date": "2024-01-01", "end_date": "2025-01-01"}}}),
        ("withdrawal_not_supported", {"withdrawal_cad": 100}),
        ("loss_constraint_not_supported", {"scenario_loss_limit_cad": 1000}),
        ("before_snapshot", {"knowledge_date": "2026-11-12"}),
        ("one_percent_initial_cap", {"max_asset_weights": {"TSLA": .01}}),
    ]:
        problem = example("amira")
        problem.update(changes)
        result = finance.analyze(problem)
        output["boundary_cases"][name] = {
            "changes": changes, "status": result["status"], "missing": result["missing"],
            "options": [{"id": o["id"], "weights": o["weights"], "admissible": o["admissible"],
                         "violations": o["violations"]} for o in result["options"]],
        }
    problem = example("robert")
    problem.update(withdrawal_cad=120000, holdings=[], clarifications=[
        {"field": "withdrawal_cad", "question": "Le retrait dépasse le capital.", "blocking": True}])
    output["minimal_infeasibility_certificate"] = finance.analyze(problem)
    output["saved_exports"] = {}
    for name in ["robert-initial", "robert-revised", "amira-initial"]:
        path = ROOT / "docs/implementation/proofs/final_demo" / (name + ".json")
        dossier = json.loads(path.read_text())
        analysis = dossier["current_analysis"]["content"]
        output["saved_exports"][name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "status": analysis["status"], "method": analysis["method"]["id"],
            "inputs": analysis["inputs"],
            "code_matches_current": [
                {"path": c["path"], "matches": hashlib.sha256((ROOT / c["path"]).read_bytes()).hexdigest() == c["sha256"]}
                for c in analysis["provenance"]["code"]],
            "options": [{"id": o["id"], "metrics": o["metrics"], "weights": o["weights"]} for o in analysis["options"]],
        }
    path = ROOT / "docs/defense/proofs/finance_review.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    return output


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "reserve": {k: {"status": v["status"], "oracle": v["oracle"]["minimum"]} for k, v in result["reserve_cases"].items()},
        "historical": result["historical_cases"],
        "boundaries": {k: v["status"] for k, v in result["boundary_cases"].items()},
    }, ensure_ascii=False, indent=2))
