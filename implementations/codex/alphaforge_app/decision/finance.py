"""Financial decisions with explicit scopes, solver diagnostics and provenance.

No model calls, downloaded market data, persona allocation or cached P3 output.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from datetime import date, datetime, timedelta, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linprog

from .. import analytics, datasets

VERSION = "decision-finance-v2"
RESERVE = "RESERVE_ABSTRAITE"
TOL = 1e-8
FACE_TOL = 1e-9
DISTINCT_TOL = 1e-6


class InputIssue(ValueError):
    def __init__(self, field: str, reason: str, status: str = "missing_input"):
        self.field, self.reason, self.status = field, reason, status
        super().__init__(reason)


def _number(value: Any, field: str, *, minimum: float = 0,
            maximum: float | None = None, positive: bool = False) -> float:
    if value is None:
        raise InputIssue(field, "Valeur nécessaire absente.")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputIssue(field, "Nombre fini requis ; aucun pourcentage implicite.", "error")
    x = float(value)
    if not math.isfinite(x) or x < minimum or (positive and x <= minimum):
        raise InputIssue(field, "Valeur numérique hors domaine.", "error")
    if maximum is not None and x > maximum:
        raise InputIssue(field, f"Valeur supérieure à {maximum}.", "error")
    return x


def _ticker(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputIssue(field, "Identifiant d'actif absent.", "error")
    return value.strip().upper()


def _weights(problem: dict) -> dict[str, float]:
    holdings = problem.get("holdings")
    if not isinstance(holdings, list) or not holdings:
        raise InputIssue("holdings", "Positions initiales nécessaires.")
    weights = {}
    for i, h in enumerate(holdings):
        if not isinstance(h, dict):
            raise InputIssue(f"holdings.{i}", "Position structurée requise.", "error")
        ticker = _ticker(h.get("ticker"), f"holdings.{i}.ticker")
        if ticker in weights:
            raise InputIssue("holdings", f"Position répétée : {ticker}.", "error")
        weights[ticker] = _number(h.get("weight"), f"holdings.{i}.weight", maximum=1)
    total = math.fsum(weights.values())
    if not math.isclose(total, 1, rel_tol=0, abs_tol=TOL):
        raise InputIssue("holdings", "Les poids fractionnaires doivent totaliser 1.", "error")
    return {t: w / total for t, w in weights.items()}


def _caps(problem: dict, weights: dict) -> dict[str, float]:
    supplied = problem.get("max_asset_weights")
    if supplied is None:
        supplied = {}
    if not isinstance(supplied, dict):
        raise InputIssue("max_asset_weights", "Un dictionnaire de plafonds est requis.", "error")
    caps = {}
    for key, value in supplied.items():
        t = _ticker(key, "max_asset_weights")
        if t in caps:
            raise InputIssue("max_asset_weights", f"Plafond répété : {t}.", "error")
        if t not in weights:
            raise InputIssue("max_asset_weights", f"{t} absent de l'univers déclaré ; ajouter une position de poids zéro si pertinent.")
        caps[t] = _number(value, f"max_asset_weights.{t}", maximum=1)
    return caps


def _metric(value: Any, unit: str) -> dict:
    return {"value": value, "unit": unit}


def _check(ident: str, status: str, method: str, scope: str, **extra) -> dict:
    return {"id": ident, "status": status, "method": method, "scope": scope, **extra}


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False, separators=(",", ":")).encode()).hexdigest()


def _provenance(problem: dict) -> dict:
    paths = [Path(__file__), Path(analytics.__file__), Path(datasets.__file__)]
    root = Path(__file__).resolve().parents[2]
    return {
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "input_sha256": _sha(problem),
        "code": [{"path": str(p.resolve().relative_to(root)),
                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
        "packages": {p: version(p) for p in ["numpy", "scipy"]},
        "data": [],
        "model_inference_calls": 0,
    }


def _base(problem: dict) -> dict:
    return {"status": "missing_input", "method": {"id": VERSION, "version": 1},
            "inputs": copy.deepcopy(problem), "options": [], "checks": [],
            "claims": [], "limitations": [], "missing": [], "sensitivity": [],
            "provenance": _provenance(problem)}


def _scenarios(problem: dict, tickers: list[str], months: float) -> list[dict]:
    rows = problem.get("scenarios")
    if rows is None:
        rows = []
    if not isinstance(rows, list):
        raise InputIssue("scenarios", "Liste de scénarios requise.", "error")
    result, seen = [], set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("returns"), dict):
            raise InputIssue(f"scenarios.{i}.returns", "Rendements explicites requis pour chaque actif.")
        ident = row.get("id")
        if not isinstance(ident, str) or not ident or ident in seen:
            raise InputIssue(f"scenarios.{i}.id", "Identifiant unique requis.", "error")
        seen.add(ident)
        if row.get("kind") != "hypothetical":
            raise InputIssue(f"scenarios.{i}.kind", "Ce LP accepte seulement des chocs hypothétiques explicitement étiquetés.", "unsupported")
        horizon = _number(row.get("horizon_months"), f"scenarios.{i}.horizon_months", positive=True)
        if not math.isclose(horizon, months, rel_tol=0, abs_tol=TOL):
            raise InputIssue(f"scenarios.{i}.horizon_months", "Le choc doit viser l'échéance du retrait ; aucune extrapolation temporelle.")
        returns = {}
        for name, value in row["returns"].items():
            t = _ticker(name, f"scenarios.{i}.returns")
            if t in returns:
                raise InputIssue(f"scenarios.{i}.returns", "Actif répété après normalisation.", "error")
            returns[t] = _number(value, f"scenarios.{i}.returns.{t}", minimum=-1)
        absent = sorted(set(tickers) - {RESERVE} - set(returns))
        if absent:
            raise InputIssue(f"scenarios.{i}.returns", "Rendements absents : " + ", ".join(absent) + ". Aucun zéro imputé.")
        if RESERVE in returns and returns[RESERVE] != 0:
            raise InputIssue(f"scenarios.{i}.returns.{RESERVE}", "La politique abstract_nominal définit un rendement nul.", "unsupported")
        # This zero follows the explicitly selected abstract policy, never an ETF proxy.
        returns[RESERVE] = 0.0
        result.append({"id": ident, "label": str(row.get("label") or ident),
                       "returns": {t: returns[t] for t in tickers},
                       "kind": "hypothetical", "horizon_months": months,
                       "currency_convention": "synthetic_CAD_value_returns",
                       "probability": None})
    return result


def _lp_model(tickers: list[str], w0: np.ndarray, caps: dict, q: float,
              scenarios: list[dict], loss_limit_fraction: float | None) -> dict:
    n = len(tickers)
    c = np.r_[np.zeros(n), np.full(n, .5)]
    a = np.r_[np.c_[np.eye(n), -np.eye(n)], np.c_[-np.eye(n), -np.eye(n)]]
    b = np.r_[w0, -w0]
    if loss_limit_fraction is not None:
        for s in scenarios:
            a = np.vstack([a, np.r_[[-s["returns"][t] for t in tickers], np.zeros(n)]])
            b = np.r_[b, loss_limit_fraction]
    lower = np.zeros(2 * n)
    lower[tickers.index(RESERVE)] = q
    upper = np.r_[[caps.get(t, 1.0) for t in tickers], np.ones(n)]
    return {"n": n, "c": c, "a": a, "b": b,
            "aeq": np.array([np.r_[np.ones(n), np.zeros(n)]]), "beq": np.array([1.0]),
            "lower": lower, "upper": upper}


def _solve(m: dict, c: np.ndarray | None = None, face: float | None = None) -> dict:
    objective = m["c"] if c is None else c
    a, b = m["a"], m["b"]
    if face is not None:
        a, b = np.vstack([a, m["c"]]), np.r_[b, face + FACE_TOL]
    if np.any(m["lower"] > m["upper"]):
        return {"status": "infeasible", "solver_status": 2,
                "message": "Borne inférieure supérieure à la borne supérieure.",
                "independent_certificate": "lower_bound_exceeds_upper_bound"}
    r = linprog(objective, A_ub=a, b_ub=b, A_eq=m["aeq"], b_eq=m["beq"],
                bounds=list(zip(m["lower"], m["upper"])), method="highs")
    if not r.success:
        return {"status": "infeasible" if r.status == 2 else "error",
                "solver_status": int(r.status), "message": str(r.message),
                "independent_certificate": None}
    x = r.x
    primal = max(0.0, float(np.max(a @ x - b)),
                 float(np.max(np.abs(m["aeq"] @ x - m["beq"]))),
                 float(np.max(m["lower"] - x)), float(np.max(x - m["upper"])))
    stationarity = (objective - a.T @ r.ineqlin.marginals
                    - m["aeq"].T @ r.eqlin.marginals
                    - r.lower.marginals - r.upper.marginals)
    dual_value = (b @ r.ineqlin.marginals + m["beq"] @ r.eqlin.marginals
                  + m["lower"] @ r.lower.marginals + m["upper"] @ r.upper.marginals)
    dual_sign_error = max(0.0, float(np.max(r.ineqlin.marginals)),
                          float(np.max(-r.lower.marginals)), float(np.max(r.upper.marginals)))
    gap = abs(float(r.fun - dual_value))
    stationary = float(np.max(np.abs(stationarity)))
    numerical_pass = max(primal, gap, stationary, dual_sign_error) <= TOL
    return {
        "status": "conditional" if numerical_pass else "error",
        "solver_status": int(r.status), "message": str(r.message),
        "weights": x[:m["n"]], "objective": float(r.fun),
        "diagnostics": {"primal_max_residual_fraction": primal,
                        "stationarity_max_residual": stationary,
                        "primal_dual_objective_gap": gap, "dual_sign_error": dual_sign_error,
                        "tolerance": TOL, "numerical_checks_pass": numerical_pass},
    }


def _constraint_checks(weights: dict, caps: dict, capital: float, withdrawal: float,
                       scenarios: list[dict], loss_limit: float | None) -> list[dict]:
    checks = []
    def add(ident, residual, unit, observed, limit, tolerance):
        checks.append({"constraint": ident, "residual": float(max(0, residual)),
                       "unit": unit, "observed": float(observed), "limit": float(limit),
                       "tolerance": tolerance, "satisfied": residual <= tolerance})
    add("budget", abs(math.fsum(weights.values()) - 1), "fraction", math.fsum(weights.values()), 1, TOL)
    for t, w in weights.items():
        add("nonnegative:" + t, -w, "fraction", w, 0, TOL)
        if t in caps:
            add("asset_cap:" + t, w - caps[t], "fraction", w, caps[t], TOL)
    reserve = weights.get(RESERVE, 0) * capital
    add("reserve", withdrawal - reserve, "CAD", reserve, withdrawal, capital * TOL)
    if loss_limit is not None:
        for s in scenarios:
            loss = -capital * math.fsum(weights[t] * s["returns"][t] for t in weights)
            add("scenario_loss:" + s["id"], loss - loss_limit, "CAD", loss, loss_limit, capital * TOL)
    return checks


def _reserve_option(ident: str, label: str, weights: dict, w0: dict, caps: dict,
                    capital: float, withdrawal: float, scenarios: list[dict],
                    loss_limit: float | None, diagnostics: dict | None = None) -> dict:
    turnover = .5 * math.fsum(abs(weights[t] - w0[t]) for t in w0)
    checks = _constraint_checks(weights, caps, capital, withdrawal, scenarios, loss_limit)
    funded = weights[RESERVE] * capital >= withdrawal - capital * TOL
    losses = []
    for s in scenarios:
        loss = -capital * math.fsum(weights[t] * s["returns"][t] for t in weights)
        losses.append({"id": s["id"], "label": s["label"], "loss_cad": loss,
                       "wealth_before_withdrawal_cad": capital - loss,
                       "wealth_after_withdrawal_cad": capital - loss - withdrawal if funded else None,
                       "horizon_months": s["horizon_months"], "kind": s["kind"],
                       "probability": None, "unit": "CAD"})
    return {"id": ident, "label": label, "weights": weights,
            "weight_unit": "fraction_of_initial_capital",
            "metrics": {"turnover_cad": _metric(turnover * capital, "CAD"),
                        "turnover_pct": _metric(turnover * 100, "percent"),
                        "reserve_cad": _metric(weights[RESERVE] * capital, "CAD")},
            "scenario_results": losses, "admissible": all(c["satisfied"] for c in checks),
            "constraint_checks": checks,
            "violations": [c for c in checks if not c["satisfied"]],
            "diagnostics": diagnostics or {}}


def _reserve_analysis(problem: dict, result: dict, weights: dict, capital: float) -> dict:
    if problem.get("objective") != "minimize_reallocated_capital":
        raise InputIssue("objective", "Préciser si l'objectif est de minimiser le capital réalloué.")
    if problem.get("reserve_policy") != "abstract_nominal":
        raise InputIssue("reserve_policy", "La réserve réelle n'est pas qualifiée. Une branche abstract_nominal doit être explicitement choisie pour ce calcul.")
    withdrawal = _number(problem.get("withdrawal_cad"), "withdrawal_cad")
    months = _number(problem.get("withdrawal_months"), "withdrawal_months", positive=True)
    weights = {**weights, RESERVE: weights.get(RESERVE, 0.0)}
    caps = _caps(problem, weights)
    tickers = sorted(weights)
    weights = {t: weights[t] for t in tickers}
    scenarios = _scenarios(problem, tickers, months)
    limit = problem.get("scenario_loss_limit_cad")
    limit = None if limit is None else _number(limit, "scenario_loss_limit_cad")
    if limit is not None and not scenarios:
        raise InputIssue("scenarios", "Un budget de perte exige des rendements de scénarios explicites.")
    w0 = np.array([weights[t] for t in tickers])
    model = _lp_model(tickers, w0, caps, withdrawal / capital, scenarios,
                      None if limit is None else limit / capital)
    result["method"] = {
        "id": "reserve-turnover-lp-v1", "version": 1,
        "domain": "Réallocation initiale, positions fractionnaires, réserve abstraite, chocs CAD terminaux.",
        "sources": [{"url": "https://web.stanford.edu/~boyd/cvxbook/", "scope": "Formulation LP, dualité."}],
        "assumptions": ["Aucun frais, impôt ni inflation modélisé.",
                        "Réserve abstraite à rendement nul disponible à l'échéance ; aucun instrument réel assimilé.",
                        "Plafonds d'exposition à t0 ; pas sur les poids après retrait ou variation des cours.",
                        "Chocs de valeur en CAD à l'échéance du retrait, sans probabilités."],
        "equations": {"objective": "min 0.5 * sum(abs(w-w0))",
                      "scenario_loss": "-capital_cad * sum(w_i * r_si)",
                      "remaining_wealth": "capital_cad - scenario_loss_cad - withdrawal_cad"},
        "inputs": {"asset_order": tickers, "weights": weights, "caps": caps,
                   "capital_cad": capital, "withdrawal_cad": withdrawal,
                   "withdrawal_months": months, "weight_unit": "fraction", "return_unit": "fraction",
                   "withdrawal_fraction": withdrawal / capital,
                   "scenarios": scenarios, "scenario_loss_limit_cad": limit},
    }
    result["limitations"] = list(result["method"]["assumptions"]) + [
        "Le minimum de capital réalloué ne minimise ni frais réels ni risque ni rendement.",
        "Ces chocs ne mesurent pas un drawdown de trajectoire et ne bornent pas la perte future.",
        "L'horizon du solde ne reçoit aucune prévision ; aucun calcul à quatre ans n'est inféré.",
        "L'univers admissible est celui des positions déclarées, y compris les poids zéro, plus la réserve abstraite.",
    ]
    if not scenarios:
        result["limitations"].append("Aucun scénario de rendement fourni : risque de marché non évalué.")
    result["provenance"]["data"] = [{"kind": "declared_and_hypothetical_parameters",
                                     "sha256": _sha(result["method"]["inputs"]),
                                     "market_data_used": False}]
    result["options"] = [_reserve_option("baseline", "Allocation initiale", weights, weights, caps,
                                         capital, withdrawal, scenarios, limit)]
    solved = _solve(model)
    if solved["status"] in {"infeasible", "error"}:
        result["status"] = solved["status"]
        certificate = solved.get("independent_certificate")
        if sum(caps.get(t, 1.0) for t in tickers) < 1 - TOL:
            certificate = "La somme des plafonds est inférieure au budget de 100 %."
        if withdrawal > capital:
            certificate = "Le retrait dépasse le capital, sans financement extérieur autorisé."
        result["checks"].append(_check("feasibility", solved["status"], "HiGHS LP",
                                      "Contraintes déclarées, sans relaxation.",
                                      solver={k: v.tolist() if isinstance(v, np.ndarray) else v
                                              for k, v in solved.items()},
                                      independent_certificate=certificate))
        result["limitations"].append("Aucun IIS calculé ; un statut d'infaisabilité n'identifie pas à lui seul la meilleure relaxation.")
        return result
    best = {t: float(w) for t, w in zip(tickers, solved["weights"])}
    option = _reserve_option("minimum_turnover", "Minimum de capital réalloué",
                             best, weights, caps, capital, withdrawal, scenarios, limit, solved["diagnostics"])
    if not option["admissible"]:
        result["status"] = "error"
        result["checks"].append(_check("constraints", "insufficient", "Contrôle indépendant des contraintes",
                                      "Allocation proposée refusée.", violations=option["violations"]))
        return result
    result["options"].append(option)
    minimum = option["metrics"]["turnover_pct"]["value"] / 100
    mandatory_sales = math.fsum(max(0, weights[t] - caps.get(t, 1.0)) for t in tickers)
    required_reserve_purchase = max(0, withdrawal / capital - weights[RESERVE])
    bound = max(mandatory_sales, required_reserve_purchase)
    bound_tight = abs(minimum - bound) <= TOL
    result["checks"] += [
        _check("constraints", "sufficient", "Résidus primal, stationnarité et dualité",
               "Ce LP uniquement ; aucune validation d'instrument.", **solved["diagnostics"]),
        _check("independent_lower_bound", "sufficient" if bound_tight else "partial",
               "Demi-L1 = somme des augmentations = somme des diminutions",
               "T ≥ max(achat nécessaire de réserve, ventes imposées par plafonds).",
               lower_bound_fraction=bound, attained=bound_tight, gap_fraction=minimum - bound),
    ]
    # Range each weight over the numerically optimal face. These are witnesses,
    # not a hidden preference for any secondary objective.
    ranges, alternate, face_failures = {}, None, []
    for i, t in enumerate(tickers):
        extrema = []
        for direction in [1, -1]:
            c = np.zeros(2 * len(tickers)); c[i] = direction
            extreme = _solve(model, c, face=minimum)
            if extreme["status"] != "conditional":
                face_failures.append({"ticker": t, "direction": direction, "status": extreme["status"]})
                break
            extrema.append(float(extreme["weights"][i]))
            if alternate is None and np.max(np.abs(extreme["weights"] - solved["weights"])) > DISTINCT_TOL:
                alternate = {name: float(w) for name, w in zip(tickers, extreme["weights"])}
        if len(extrema) == 2:
            ranges[t] = {"minimum": extrema[0], "maximum": extrema[1], "unit": "fraction"}
    if alternate is not None:
        alt = _reserve_option("alternative_minimum", "Autre allocation au minimum, à tolérance",
                              alternate, weights, caps, capital, withdrawal, scenarios, limit)
        face_gap = abs(alt["metrics"]["turnover_pct"]["value"] / 100 - minimum)
        alt["diagnostics"]["optimal_face_gap_fraction"] = face_gap
        if alt["admissible"] and face_gap <= FACE_TOL + TOL:
            result["options"].append(alt)
        else:
            face_failures.append({"status": "independent_constraint_check_failed"})
    result["optimal_face"] = {"weight_ranges": ranges, "non_unique_witness_found": len(result["options"]) > 2,
                              "turnover_band_fraction": FACE_TOL, "distinct_weight_threshold": DISTINCT_TOL,
                              "failures": face_failures, "secondary_preference_selected": False,
                              "scope": "Extrêmes sur la face optimale à tolérance ; aucun optimum de risque recherché."}
    result["checks"].append(_check("multiple_optima", "partial" if face_failures else "sufficient",
                                  "Min/max de chaque poids à rotation ≤ minimum + tolérance",
                                  result["optimal_face"]["scope"],
                                  non_unique_witness_found=len(result["options"]) > 2))
    refs = [{"pointer": "/options/1/metrics/turnover_cad/value", "unit": "CAD"}]
    result["claims"] = [
        {"id": "minimum_reallocation", "kind": "conditional_optimality",
         "text": f"Dans ce modèle, le minimum de capital réalloué est de {option['metrics']['turnover_cad']['value']:,.2f} CAD.",
         "result_refs": refs, "scope": "Branche abstraite, contraintes déclarées et tolérances numériques."},
        {"id": "reserve_scope", "kind": "limitation",
         "text": "La réserve est abstraite ; aucune garantie d'un instrument réel n'est établie.",
         "result_refs": [], "scope": "Aucun résultat hors du modèle."},
    ]
    if len(result["options"]) > 2:
        result["claims"].append({"id": "multiple_optima", "kind": "numerical_witness",
                                 "text": "Plusieurs allocations atteignent le minimum à la tolérance déclarée ; aucun critère de départage n'a été inventé.",
                                 "result_refs": [{"pointer": "/optimal_face/non_unique_witness_found", "unit": "boolean"}],
                                 "scope": result["optimal_face"]["scope"]})
    # Explicit parameter probes; never rewrite the active problem.
    probes = [({"withdrawal_cad": max(0, withdrawal - .1 * capital)}, "retrait −10 % du capital"),
              ({"withdrawal_cad": withdrawal + .1 * capital}, "retrait +10 % du capital")]
    for t, cap in caps.items():
        for delta in [-.05, .05]:
            changed = min(1, max(0, cap + delta))
            if changed != cap:
                probes.append(({"max_asset_weights": {**caps, t: changed}}, f"plafond {t} {delta * 100:+g} points"))
    for changes, label in probes:
        q2 = changes.get("withdrawal_cad", withdrawal)
        cap2 = changes.get("max_asset_weights", caps)
        m2 = _lp_model(tickers, w0, cap2, q2 / capital, scenarios, None if limit is None else limit / capital)
        s = _solve(m2)
        result["sensitivity"].append({
            "label": label, "kind": "hypothetical_parameter_probe", "changes": changes,
            "status": s["status"],
            "minimum_reallocated_capital_cad": float(s["objective"] * capital) if s["status"] == "conditional" else None,
            "weights": {t: float(w) for t, w in zip(tickers, s["weights"])} if s["status"] == "conditional" else None,
            "diagnostics": s.get("diagnostics", {}),
            "unit": "CAD", "baseline_unchanged": True,
            "scope": "Sondage explicite ±10 % du capital sur le retrait ou ±5 points sur le plafond ; pas préférence ni prévision."})
    result["status"] = "conditional"
    return result


def _historical_analysis(problem: dict, result: dict, weights: dict, capital: float) -> dict:
    if problem.get("objective") != "compare_historical":
        raise InputIssue("objective", "Objectif compare_historical nécessaire.")
    policy = problem.get("historical_policy")
    if not isinstance(policy, dict):
        raise InputIssue(
            "historical_policy",
            "Préciser la règle de redistribution et la fenêtre historique. "
            "Aucune convention n'est déduite d'une hypothèse textuelle.")
    if policy.get("redistribution") is None:
        raise InputIssue("historical_policy.redistribution", "Règle de redistribution explicite nécessaire.")
    if policy["redistribution"] != "proportional_other_holdings":
        raise InputIssue(
            "historical_policy.redistribution",
            "Ce calcul redistribue proportionnellement les autres positions. "
            "La règle demandée exige une autre méthode.", "unsupported")
    window = policy.get("window")
    if not isinstance(window, dict) or window.get("kind") is None:
        raise InputIssue("historical_policy.window", "Fenêtre historique explicite nécessaire.")
    if (window["kind"] != "all_common_available"
            or window.get("start_date") is not None or window.get("end_date") is not None):
        raise InputIssue(
            "historical_policy.window",
            "Ce calcul utilise toute la fenêtre commune admissible du snapshot. "
            "Une période spécifique nécessite une méthode supplémentaire qualifiée.", "unsupported")
    if problem.get("withdrawal_cad") not in (None, 0):
        raise InputIssue("withdrawal_cad", "Le calcul historique ne modélise pas les retraits ; utiliser un modèle de flux.", "unsupported")
    if problem.get("scenarios") or problem.get("scenario_loss_limit_cad") is not None:
        raise InputIssue("scenarios", "Ce mode n'applique pas les contraintes de chocs synthétiques.", "unsupported")
    if RESERVE in weights:
        raise InputIssue("holdings", "La réserve abstraite n'a pas de prix historiques.", "unsupported")
    comparison = problem.get("comparison")
    if not isinstance(comparison, dict):
        raise InputIssue("comparison", "Actif et poids cible nécessaires.")
    t = _ticker(comparison.get("ticker"), "comparison.ticker")
    target = _number(comparison.get("target_weight"), "comparison.target_weight", maximum=1)
    end = problem.get("knowledge_date")
    try:
        parsed = date.fromisoformat(end)
        if parsed.isoformat() != end:
            raise ValueError
    except (ValueError, TypeError):
        raise InputIssue("knowledge_date", "Date de connaissance YYYY-MM-DD nécessaire.")
    dataset = datasets.load_dataset()
    wanted = set(weights) | {t}
    absent = sorted(wanted - set(dataset.assets))
    if absent:
        raise InputIssue("holdings", "Prix/identité absents du snapshot : " + ", ".join(absent))
    needed = {"assets_universe.csv", "prices_daily.csv"}
    if any(dataset.assets[name]["currency"] == "USD" for name in wanted):
        needed.add("fx_usdcad_daily.csv")
    known = {}
    for name in needed:
        dates = [row.get("retrieved_on") for row in dataset.sources if row.get("file") == name]
        if not dates:
            raise InputIssue("knowledge_date", f"Date de disponibilité du snapshot non documentée pour {name}.")
        try:
            if any(date.fromisoformat(d).isoformat() != d for d in dates):
                raise ValueError
        except (ValueError, TypeError):
            raise InputIssue("knowledge_date", f"Date de disponibilité invalide pour {name}.")
        known[name] = max(dates)
        if known[name] > end:
            raise InputIssue("knowledge_date", f"{name} a été acquis le {known[name]}, après la date demandée. Tronquer ses prix ne recrée pas un millésime ancien.")
    variant = analytics.set_target_weight(weights, t, target)
    # The documented valuation of row D is D+1 00:00 UTC. Date-only cutoffs
    # include that entire knowledge day, but never a still-incomplete row D.
    price_end = (parsed - timedelta(days=1)).isoformat()
    compared = analytics.compare_portfolios(
        [{"id": "baseline", "name": "Allocation initiale", "weights": weights},
         {"id": "target_variant", "name": f"Exposition initiale {t} à {target:.1%}", "weights": variant}],
        capital_cad=capital, end=price_end, dataset=dataset)
    caps = _caps(problem, {**weights, **{k: 0 for k in variant if k not in weights}})
    for option in compared["options"]:
        metrics = {}
        for name, value in option["metrics"].items():
            unit = "CAD" if name.endswith("_cad") else "percent" if name.endswith("_pct") else "date" if name.endswith("_date") else "intervals_per_year"
            metrics[name] = _metric(value, unit)
        violations = [{"constraint": "asset_cap:" + name, "observed": option["weights"].get(name, 0),
                       "limit": cap, "unit": "fraction", "residual": option["weights"].get(name, 0) - cap}
                      for name, cap in caps.items() if option["weights"].get(name, 0) > cap + TOL]
        result["options"].append({"id": option["id"], "label": option["name"],
                                  "weights": option["weights"], "weight_unit": "fraction_of_initial_capital",
                                  "metrics": metrics, "series": option["series"],
                                  "scenario_results": [{"kind": "historical_window", **s}
                                                       for s in option["scenarios"]],
                                  "concentration": option["concentration"], "holdings": option["holdings"],
                                  "admissible": not violations, "violations": violations,
                                  "admissibility_scope": "Poids initiaux et plafonds seulement ; pas convenance personnelle.",
                                  "diagnostics": {"warnings": option["warnings"]}})
    meta = compared["meta"]
    result["method"] = {"id": "retrospective-comparison-v2", "version": 2,
                        "implementation": analytics.MODEL_VERSION,
                        "domain": "Comparaison descriptive achat-conservation d'allocations initiales.",
                        "declared_policy": copy.deepcopy(policy),
                        "assumptions": [meta["return_policy"], meta["cost_policy"]],
                        "sources": dataset.sources, "metadata": meta}
    result["provenance"]["data"] = [{"file": name, **value} for name, value in dataset.files.items()]
    result["provenance"]["availability"] = {"knowledge_date": end, "snapshot_retrieved_on": known,
                                           "latest_allowed_price_date": price_end,
                                           "historical_point_in_time_universe": False,
                                           "exact_publication_times_available": False}
    result["checks"] = [
        _check("historical_policy", "sufficient", "Règle et fenêtre structurées explicitement déclarées",
               "Redistribution proportionnelle et totalité de la grille commune admissible ; aucune autre convention inférée.",
               policy=copy.deepcopy(policy)),
        _check("snapshot_availability", "sufficient_with_reservation", "Comparaison dates d'acquisition/date de connaissance",
               "Snapshot disponible à date, pas reconstitution d'un univers historique.", dates=known),
        _check("calendar_fx", "sufficient_with_reservation", "Grille commune ; adj_close USD × FX as-of, âge ≤7 jours",
               meta["valuation_time_rule"], max_fx_age_days=meta["max_fx_age_days"]),
        _check("adjustments", "sufficient_with_reservation", "adj_close utilisé une seule fois",
               "Distributions réinvesties dans chaque actif ; aucune addition des dividendes/splits."),
    ]
    result["limitations"] = meta["limitations"] + [
        "La date de connaissance filtre aussi la disponibilité de la capture ; elle ne rend pas le prix ajusté point-in-time.",
        "Aucun rendement manquant n'est imputé ; la comparaison exige les prix sur la grille commune.",
        "Les fenêtres historiques réinitialisent l'allocation à leur début ; ce ne sont pas des chocs futurs.",
        "L'horizon déclaré n'est pas prédit par cette histoire.",
        "Les plafonds portent sur les poids initiaux ; ils ne contraignent pas les poids après variation des cours.",
    ]
    for i, o in enumerate(result["options"]):
        result["claims"].append({"id": "historical_return_" + o["id"], "kind": "historical_observation",
                                 "text": f"{o['label']} : rendement total rétrospectif de {o['metrics']['total_return_pct']['value']:.2f} %, du {meta['start']} au {meta['end']}.",
                                 "result_refs": [{"pointer": f"/options/{i}/metrics/total_return_pct/value", "unit": "percent"},
                                                 {"pointer": "/method/metadata/start", "unit": "date"},
                                                 {"pointer": "/method/metadata/end", "unit": "date"}],
                                 "scope": "Descriptif, avant frais de transaction/change/impôts ; aucune prévision."})
    result["status"] = "conditional"
    return result


def reserve_budget_diagnostic_applicable(problem: dict) -> bool:
    """Admit only the bounded budget diagnostic, never an allocation."""
    if (not isinstance(problem, dict)
            or problem.get("decision_type") != "reserve_allocation"
            or problem.get("currency") != "CAD"
            or problem.get("objective") != "minimize_reallocated_capital"
            or problem.get("reserve_policy") != "abstract_nominal"):
        return False
    try:
        capital = _number(problem.get("capital_cad"), "capital_cad", positive=True, maximum=1e12)
        withdrawal = _number(problem.get("withdrawal_cad"), "withdrawal_cad")
    except InputIssue:
        return False
    return withdrawal > capital


def reserve_budget_certificate(problem: dict) -> dict | None:
    """Prove one contradiction under the declared inputs, not an IIS.

    Other missing inputs cannot repair W > C under this method's long-only,
    fully funded, zero-return reserve policy.
    """
    if not reserve_budget_diagnostic_applicable(problem):
        return None
    capital = float(problem["capital_cad"])
    withdrawal = float(problem["withdrawal_cad"])
    fields = ("decision_type", "currency", "objective", "reserve_policy",
              "capital_cad", "withdrawal_cad")
    return _check(
        "reserve_budget_contradiction", "infeasible",
        "Contradiction algébrique entre réserve et budget",
        "Sous-ensemble nécessaire des contraintes du modèle déclaré ; aucun IIS global.",
        certified=True, independent_of_solver=True,
        proof="R ≥ retrait > capital et R ≤ capital : les contraintes sont incompatibles.",
        capital_cad=capital, withdrawal_cad=withdrawal,
        shortfall_cad=withdrawal - capital, unit="CAD",
        minimal_input_fields=list(fields),
        declared_inputs={field: copy.deepcopy(problem[field]) for field in fields},
        assumptions=[
            "Allocation long-only entièrement financée par le capital déclaré ; aucun apport extérieur.",
            "Réserve abstraite nominale disponible à l'échéance, à rendement nul.",
            "Le retrait doit être financé par cette réserve dès l'allocation initiale.",
        ])


def analyze_budget_diagnostic(problem: dict) -> dict:
    """Execute only the budget certificate; refuse all broader calculations."""
    if not reserve_budget_diagnostic_applicable(problem):
        raise ValueError("Entrées hors domaine du diagnostic budgétaire borné.")
    result = analyze(problem)
    if result["method"]["id"] != "reserve-budget-contradiction-v1" or result["options"]:
        raise ValueError("Le diagnostic budgétaire ne peut pas produire une allocation.")
    return result


def analyze(problem: dict) -> dict:
    """Return a JSON-serializable analysis or a structured, explicit limitation."""
    if not isinstance(problem, dict):
        return {"status": "error", "method": {"id": VERSION}, "inputs": None, "options": [],
                "checks": [], "claims": [], "limitations": [], "missing": [
                    {"field": "problem", "reason": "Objet JSON requis."}], "provenance": {}}
    try:
        result = _base(problem)
    except (TypeError, ValueError, OverflowError):
        return {"status": "error", "method": {"id": VERSION}, "inputs": None, "options": [],
                "checks": [], "claims": [], "limitations": [], "missing": [
                    {"field": "problem", "reason": "Entrées JSON finies requises."}], "provenance": {}}
    try:
        certificate = reserve_budget_certificate(problem)
        if certificate is not None:
            result["status"] = "infeasible"
            result["method"] = {
                "id": "reserve-budget-contradiction-v1", "version": 1,
                "domain": certificate["scope"],
                "assumptions": certificate["assumptions"],
                "sources": [{"kind": "declared_inputs", "pointer": "/checks/0/declared_inputs"}],
                "equations": {"reserve_budget": "withdrawal_cad <= reserve_cad <= capital_cad"},
            }
            result["checks"] = [certificate]
            result["claims"] = [{
                "id": "reserve_budget_infeasible", "kind": "infeasibility_certificate",
                "text": (
                    f"Le retrait demandé de {certificate['withdrawal_cad']:,.2f} CAD dépasse "
                    f"le capital de {certificate['capital_cad']:,.2f} CAD de "
                    f"{certificate['shortfall_cad']:,.2f} CAD. Le financement par la réserve "
                    "abstraite est impossible dans ce modèle, sans apport extérieur."
                ),
                "result_refs": [
                    {"pointer": "/checks/0/withdrawal_cad", "unit": "CAD"},
                    {"pointer": "/checks/0/capital_cad", "unit": "CAD"},
                    {"pointer": "/checks/0/shortfall_cad", "unit": "CAD"},
                ],
                "scope": certificate["scope"],
            }]
            result["limitations"] = certificate["assumptions"] + [
                "Cette contradiction suffit à prouver l'infaisabilité dans le modèle déclaré.",
                "Les autres clarifications restent ouvertes ; aucune contrainte n'est relâchée.",
                "Aucun IIS global calculé ; aucune préférence de réparation déduite.",
            ]
            result["provenance"]["data"] = [{
                "kind": "declared_and_hypothetical_parameters",
                "sha256": _sha(certificate["declared_inputs"]), "market_data_used": False,
            }]
            return result
        kind = problem.get("decision_type")
        if kind not in {"reserve_allocation", "historical_comparison"}:
            raise InputIssue("decision_type", "Ce moteur traite reserve_allocation et historical_comparison.", "unsupported")
        if problem.get("currency") != "CAD":
            raise InputIssue("currency", "Devise de décision CAD requise ; aucune conversion implicite.", "unsupported")
        capital = _number(problem.get("capital_cad"), "capital_cad", positive=True, maximum=1e12)
        weights = _weights(problem)
        if problem.get("horizon_years") is not None:
            _number(problem["horizon_years"], "horizon_years", positive=True)
        for item in problem.get("clarifications") or []:
            if isinstance(item, dict) and item.get("blocking") is True:
                raise InputIssue(item.get("field", "clarification"), item.get("question", "Clarification bloquante."))
        if kind == "reserve_allocation":
            result = _reserve_analysis(problem, result, weights, capital)
        else:
            result = _historical_analysis(problem, result, weights, capital)
        # Every returned success has finite JSON numbers, including nested
        # diagnostics. Overflow is a technical failure, never a valid estimate.
        json.dumps(result, allow_nan=False)
        return result
    except InputIssue as exc:
        result["status"] = exc.status
        result["missing"].append({"field": exc.field, "reason": exc.reason})
    except datasets.DataError as exc:
        result["status"] = "missing_input"
        result["missing"].append({"field": "data", "reason": str(exc)})
    except Exception as exc:
        # Operational failure is never evidence of economic infeasibility.
        result["status"] = "error"
        result["checks"] = [_check("execution", "error", type(exc).__name__,
                                   "Échec technique ; aucune conclusion financière produite.")]
        result["missing"].append({"field": "execution", "reason": str(exc)})
        result["options"] = []
        result["sensitivity"] = []
        result.pop("optimal_face", None)
    result["claims"] = []
    return result


def baseline_stress(problem: dict) -> dict:
    """Initial-portfolio shocks, independent of any withdrawal or constraint.

    Only the four projected inputs below enter the calculation and its hash.
    A full ProblemSpec may be passed, but no other field is read or retained.
    """
    fields = ("capital_cad", "holdings", "scenarios", "currency")
    projected = {k: copy.deepcopy(problem.get(k)) for k in fields} if isinstance(problem, dict) else {}
    try:
        result = _base(projected)
    except (TypeError, ValueError, OverflowError):
        return {"status": "error", "method": {"id": "baseline-stress-v1"},
                "inputs": None, "scenario_results": [], "options": [], "checks": [],
                "claims": [], "limitations": [], "missing": [
                    {"field": "problem", "reason": "Entrées projetées JSON finies requises."}],
                "provenance": {}}
    result["scenario_results"] = []
    result["method"] = {
        "id": "baseline-stress-v1", "version": 1,
        "domain": "Pertes du portefeuille initial sous chocs terminaux CAD déclarés.",
        "equation": "loss_cad = -capital_cad * sum(initial_weight_i * scenario_return_i)",
        "assumptions": ["Poids initiaux constants dans la formule de choc terminal.",
                        "Rendements synthétiques exprimés en fraction de valeur CAD, sans probabilité.",
                        "Aucun instrument réel ni garantie déduit d'un scénario."],
        "sources": [{"kind": "declared_inputs", "pointer": "/inputs",
                     "scope": "Capital, positions, devise et chocs fournis ; aucune donnée de marché."}],
        "dependency_fields": list(fields),
    }
    result["limitations"] = [
        "Diagnostic du portefeuille initial, pas une allocation proposée ni un contrôle d'admissibilité.",
        "Ne calcule ni financement d'un retrait, ni richesse après retrait, ni perte future garantie.",
        "Ces pertes terminales ne décrivent pas une trajectoire ni un drawdown.",
        "Branche indépendante du besoin de liquidité, pas un deuxième modèle de risque.",
    ]
    try:
        if not isinstance(problem, dict):
            raise InputIssue("problem", "Objet JSON requis.", "error")
        if projected["currency"] != "CAD":
            raise InputIssue("currency", "Devise CAD requise ; aucune conversion implicite.", "unsupported")
        capital = _number(projected["capital_cad"], "capital_cad", positive=True, maximum=1e12)
        weights = _weights(projected)
        rows = projected["scenarios"]
        if not isinstance(rows, list) or not rows:
            raise InputIssue("scenarios", "Au moins un scénario explicite est nécessaire.")
        seen = set()
        for i, row in enumerate(rows):
            if not isinstance(row, dict) or not isinstance(row.get("returns"), dict):
                raise InputIssue(f"scenarios.{i}.returns", "Rendements explicites requis pour chaque actif.")
            ident = row.get("id")
            if not isinstance(ident, str) or not ident or ident in seen:
                raise InputIssue(f"scenarios.{i}.id", "Identifiant unique requis.", "error")
            seen.add(ident)
            if row.get("kind") != "hypothetical":
                raise InputIssue(f"scenarios.{i}.kind", "Choc hypothétique explicitement étiqueté requis.", "unsupported")
            horizon = _number(row.get("horizon_months"), f"scenarios.{i}.horizon_months", positive=True)
            returns = {}
            for key, value in row["returns"].items():
                t = _ticker(key, f"scenarios.{i}.returns")
                if t in returns:
                    raise InputIssue(f"scenarios.{i}.returns", "Actif répété après normalisation.", "error")
                returns[t] = _number(value, f"scenarios.{i}.returns.{t}", minimum=-1)
            absent = sorted(set(weights) - set(returns))
            if absent:
                raise InputIssue(f"scenarios.{i}.returns",
                                 "Rendements absents : " + ", ".join(absent) + ". Aucun zéro imputé, même à la réserve.")
            portfolio_return = math.fsum(weight * returns[t] for t, weight in weights.items())
            result["scenario_results"].append({
                "id": ident, "label": str(row.get("label") or ident),
                "kind": "hypothetical", "horizon_months": horizon, "probability": None,
                "loss_cad": -capital * portfolio_return,
                "portfolio_return_pct": portfolio_return * 100,
                "units": {"loss_cad": "CAD", "portfolio_return_pct": "percent",
                          "horizon_months": "months"},
            })
        result["checks"] = [_check(
            "baseline_input_contract", "sufficient", "Validation des quatre entrées et somme pondérée",
            "Poids fractionnaires, capital positif, rendements finis ≥ −100 %, horizon propre à chaque choc.",
            weight_sum=math.fsum(weights.values()), missing_returns_imputed=False)]
        for i, row in enumerate(result["scenario_results"]):
            result["claims"].append({
                "id": "baseline_loss_" + row["id"], "kind": "conditional_scenario",
                "text": f"{row['label']} : perte du portefeuille initial de {row['loss_cad']:,.2f} CAD.",
                "result_refs": [{"pointer": f"/scenario_results/{i}/loss_cad", "unit": "CAD"}],
                "scope": "Choc hypothétique sur les positions initiales, sans probabilité.",
            })
        result["provenance"]["data"] = [{"kind": "declared_and_hypothetical_parameters",
                                         "sha256": _sha(projected), "market_data_used": False}]
        result["status"] = "conditional"
        json.dumps(result, allow_nan=False)
        return result
    except InputIssue as exc:
        result["status"] = exc.status
        result["missing"].append({"field": exc.field, "reason": exc.reason})
    except Exception as exc:
        result["status"] = "error"
        result["missing"].append({"field": "execution", "reason": str(exc)})
    result["scenario_results"] = []
    result["claims"] = []
    result["checks"] = []
    return result


def examples() -> list[dict]:
    """Only explicit, editable inputs. No precomputed output or persona defaults."""
    robert = {
        "decision_type": "reserve_allocation", "question": "Financer un retrait en déplaçant le moins de capital.",
        "currency": "CAD", "capital_cad": 100000,
        "holdings": [{"ticker": t, "weight": w} for t, w in
                     [("XBB.TO", .35), ("ZST.TO", .20), ("XIU.TO", .20), ("TSLA", .25)]],
        "withdrawal_cad": 30000, "withdrawal_months": 12, "horizon_years": 4,
        "max_asset_weights": {"TSLA": .10}, "scenario_loss_limit_cad": 15000,
        "scenarios": [{"id": ident, "label": label, "kind": "hypothetical", "horizon_months": 12,
                       "returns": dict(zip(["XBB.TO", "ZST.TO", "XIU.TO", "TSLA", RESERVE], values))}
                      for ident, label, values in [
                          ("actions", "Choc actions hypothétique", [-.05, 0, -.20, -.50, 0]),
                          ("obligations", "Choc obligations hypothétique", [-.15, -.02, -.10, -.25, 0])]],
        "objective": "minimize_reallocated_capital", "comparison": None,
        "reserve_policy": "abstract_nominal", "knowledge_date": "2026-11-15",
        "assumptions": [{"id": "example_scope", "text": "Exercice fictif ; réserve abstraite, coûts/fiscalité nuls, chocs CAD synthétiques sans probabilité ; aucun placement réel garanti.", "origin": "assumed"}],
        "unknowns": ["Instrument réel de réserve et conditions non qualifiés."], "clarifications": [],
    }
    amira = {
        "decision_type": "historical_comparison", "question": "Comparer deux expositions initiales à TSLA sur le snapshot disponible.",
        "currency": "CAD", "capital_cad": 25000,
        "holdings": [{"ticker": t, "weight": w} for t, w in [("SPY", .45), ("XIU.TO", .30), ("TSLA", .25)]],
        "withdrawal_cad": None, "withdrawal_months": None, "horizon_years": 15,
        "max_asset_weights": {}, "scenario_loss_limit_cad": None, "scenarios": [],
        "objective": "compare_historical", "comparison": {"ticker": "TSLA", "target_weight": .10},
        "historical_policy": {"redistribution": "proportional_other_holdings",
                              "window": {"kind": "all_common_available"}},
        "reserve_policy": None, "knowledge_date": "2026-11-15",
        "assumptions": [{"id": "retrospective", "text": "Entrées fictives choisies pour comparaison descriptive, achat-conservation, sans projection à quinze ans ; aucune allocation officielle de persona.", "origin": "assumed"},
                        {"id": "redistribution", "text": "Le capital libéré par la réduction de TSLA est redistribué proportionnellement aux autres positions initiales.", "origin": "declared"},
                        {"id": "historical_window", "text": "Utiliser toute la fenêtre commune admissible du snapshot disponible à knowledge_date, sans projection au-delà de l'histoire observée.", "origin": "declared"}],
        "unknowns": ["Compositions de FNB et exclusions ESG non établies."], "clarifications": [],
    }
    return [{"id": "robert", "title": "Robert — retrait et réserve abstraite",
             "prompt": "Dans cet exercice fictif, je dois retirer 30 000 CAD dans douze mois. Comparons les changements minimaux sous les hypothèses fournies.",
             "facts": robert, "suggested_revision": {"message": "Le retrait sera finalement de 40 000 CAD.", "changes": {"withdrawal_cad": 40000}}},
            {"id": "amira", "title": "Amira — comparaison historique d'exposition",
             "prompt": "Compare mon allocation fictive actuelle à une exposition initiale de 10 % à TSLA. Je demande une analyse historique, pas une prévision.",
             "facts": amira, "suggested_revision": {"message": "Compare plutôt une exposition initiale de 5 % à TSLA.", "changes": {"comparison": {"ticker": "TSLA", "target_weight": .05}}}}]
