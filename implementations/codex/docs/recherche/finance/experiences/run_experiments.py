"""Isolated discriminating finance experiments; see PROTOCOLE.md."""
from bisect import bisect_right
import csv
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys

import highspy
import numpy as np
from scipy.optimize import linprog, minimize
from scipy.stats import norm
from sklearn.covariance import ledoit_wolf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = ROOT / "data" / "alphaforge_starter"
SEED = 20261115


def lp(c, aub=None, bub=None, aeq=None, beq=None, bounds=None):
    return linprog(c, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq,
                   bounds=bounds, method="highs")


def iis_experiment():
    cases = []
    for strategy in [0, 4]:
        h = highspy.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("iis_strategy", strategy)
        h.addVar(0, highspy.kHighsInf)
        h.addRow(.4, highspy.kHighsInf, 1, [0], [1.0])
        h.addRow(-highspy.kHighsInf, .3, 1, [0], [1.0])
        h.run()
        status, iis = h.getIis()
        cases.append({
            "strategy": strategy, "solve_status": str(h.getModelStatus()),
            "get_iis_status": str(status), "valid": iis.valid_,
            "iis_status": int(iis.status_), "row_index": iis.row_index_,
            "row_bound": iis.row_bound_, "col_index": iis.col_index_,
            "col_bound": iis.col_bound_,
        })
    a, b = [[-1], [1]], [-.4, .3]
    deletion = [
        {"removed_row": k, "remaining_feasible": lp([0], [a[1-k]], [b[1-k]]).success}
        for k in [0, 1]
    ]
    assert not lp([0], a, b).success
    assert all(x["remaining_feasible"] for x in deletion)
    assert cases[1]["row_index"] == [0, 1]
    return {"cases": cases, "independent_interface_deletion_checks": deletion,
            "analytical_certificate": "0.4 <= x <= 0.3 is impossible; each single inequality is feasible.",
            "independence_limit": "SciPy and highspy both use HiGHS; the inequality proof is solver-independent."}


def robert_experiment():
    # Variables: five weights then five absolute deviations.
    w0 = np.array([0, .35, .20, .20, .25])
    stress_losses = np.array([[0, .05, 0, .20, .50], [0, .15, .02, .10, .25]])
    result = []
    for reserve in [.30, .40]:
        c = np.r_[np.zeros(5), np.full(5, .5)]
        a = np.r_[np.c_[np.eye(5), -np.eye(5)],
                  np.c_[-np.eye(5), -np.eye(5)],
                  np.c_[stress_losses, np.zeros((2, 5))]]
        b = np.r_[w0, -w0, [.15, .15]]
        solution = lp(c, a, b, [np.r_[np.ones(5), np.zeros(5)]], [1],
                      [(reserve, 1), (0, 1), (0, 1), (0, 1), (0, .10)] + [(0, 1)]*5)
        assert solution.success
        w = solution.x[:5]
        assert abs(solution.fun - reserve) < 1e-9
        assert np.max(a @ solution.x - b) < 1e-8
        result.append({"reserve_fraction": reserve, "weights": w.tolist(),
                       "minimum_turnover_fraction": solution.fun,
                       "scenario_loss_fractions": (stress_losses @ w).tolist(),
                       "constraint_max_violation": float(max(0, np.max(a @ solution.x-b)))})
    impossible = lp([0]*5, [[-1, 0, 0, 0, 0], [0, 0, 0, 0, -1]],
                    [-.4, -.7], [[1]*5], [1], [(0, 1)]*5)
    assert impossible.status == 2
    return {"asset_order": ["reserve_abstracte", "XBB.TO", "ZST.TO", "XIU.TO", "TSLA"],
            "capital_cad": 100000, "results": result,
            "infeasible_reserve40_tsla70_status": impossible.status,
            "proof": "With unchanged total capital, half-L1 equals all positive weight changes. A new reserve r forces turnover >=r. Feasible LP solutions attain r.",
            "limit": "Illustrative zero-return reserve and fixed stress shocks; no taxes, fees, liabilities beyond stated withdrawal, or product guarantee."}


def gmv(cov, cap=None):
    n = len(cov)
    answer = minimize(lambda w: w @ cov @ w * 10000, np.ones(n)/n,
                      jac=lambda w: 20000*cov@w,
                      constraints=[{"type":"eq", "fun":lambda w:w.sum()-1,
                                    "jac":lambda w:np.ones(n)}],
                      bounds=None if cap is None else [(0, cap)]*n,
                      method="SLSQP", options={"ftol":1e-13, "maxiter":2000})
    if not answer.success:
        raise RuntimeError(answer.message)
    assert abs(answer.x.sum()-1) < 1e-7
    if cap is not None:
        assert answer.x.min() >= -1e-7 and answer.x.max() <= cap+1e-7
    return answer.x


def references():
    s = np.array([[.04,.006,.002],[.006,.09,.004],[.002,.004,.16]])
    u = np.linalg.solve(s, np.ones(3)); analytical = u/u.sum()
    error = float(np.max(np.abs(gmv(s)-analytical)))
    assert error < 1e-6
    # Tail mass 0.5 of three equiprobable losses: fractional boundary matters.
    losses = np.array([-.01, .02, .10])
    mass = .5  # worst half is .10 * 1/3 plus .02 * 1/6, divided by .5
    c = np.r_[1., np.ones(3)/(3*mass)]
    a = np.c_[-np.ones(3), -np.eye(3)]
    answer = lp(c, a, -losses, bounds=[(None,None)]+[(0,None)]*3)
    ref = (.10/3+.02/6)/mass
    assert answer.success and abs(answer.fun-ref)<1e-10
    return {"gmv_reference_weights": analytical.tolist(), "gmv_max_abs_error":error,
            "es_losses":losses.tolist(), "es_tail_mass":mass,
            "es_lp":answer.fun, "es_fractional_tail_reference":ref}


def load_returns():
    tickers = sorted(["GLD","QQQ","SPY","TSLA","XIU.TO","XBB.TO","ZST.TO","TLT"])
    fx = {r["date"]:float(r["usdcad"]) for r in csv.DictReader((DATA/"fx_usdcad_daily.csv").open())}
    fdates = sorted(fx)
    prices = {t:{} for t in tickers}
    for row in csv.DictReader((DATA/"prices_daily.csv").open()):
        t, d = row["ticker"], row["date"]
        if t not in prices: continue
        factor = 1.
        if row["currency"] == "USD":
            j = bisect_right(fdates, d)-1
            assert j>=0
            factor=fx[fdates[j]]
        prices[t][d] = float(row["adj_close"])*factor
    dates = sorted(set.intersection(*(set(prices[t]) for t in tickers)))
    p = np.array([[prices[t][d] for t in tickers] for d in dates])
    return tickers, dates, p[1:]/p[:-1]-1


def covariance_experiment():
    tickers, dates, r = load_returns()
    out = {k:[] for k in ["equal", "sample_gmv", "lw_identity_gmv"]}
    weights = {k:[] for k in out}
    folds = []
    for start in range(252, len(r)-62, 63):
        train, test = r[start-252:start], r[start:start+63]
        empirical = np.cov(train, rowvar=False, ddof=1)
        shrunk, intensity = ledoit_wolf(train)
        ws = {"equal":np.ones(len(tickers))/len(tickers),
              "sample_gmv":gmv(empirical,.35), "lw_identity_gmv":gmv(shrunk,.35)}
        for method,w in ws.items():
            # Constant weights inside each block: daily rebalancing, frictionless.
            out[method].extend((test @ w).tolist())
            weights[method].append(w)
        folds.append({"train_start":dates[start-252], "train_end":dates[start],
                      "test_first_return_end":dates[start+1], "test_end":dates[start+63],
                      "lw_intensity":float(intensity),
                      "sample_condition":float(np.linalg.cond(empirical)),
                      "lw_condition":float(np.linalg.cond(shrunk))})
    last_start = list(range(252, len(r)-62, 63))[-1]
    train = r[last_start-252:last_start]
    bases = {"sample_gmv":gmv(np.cov(train,rowvar=False),.35),
             "lw_identity_gmv":gmv(ledoit_wolf(train)[0],.35)}
    rng = np.random.default_rng(SEED)
    deviations = {k:[] for k in bases}
    for _ in range(100):
        starts = rng.integers(0,248,size=51)
        indices = np.concatenate([np.arange(j,j+5) for j in starts])[:252]
        x = train[indices]
        for method,cov in [("sample_gmv",np.cov(x,rowvar=False)),
                           ("lw_identity_gmv",ledoit_wolf(x)[0])]:
            deviations[method].append(float(np.abs(gmv(cov,.35)-bases[method]).sum()))
    summary={}
    for method, series in out.items():
        ws = weights[method]
        summary[method] = {
            "oos_volatility_pct_sqrt252":float(np.std(series,ddof=1)*np.sqrt(252)*100),
            "mean_half_l1_target_change":float(np.mean([np.abs(b-a).sum()/2 for a,b in zip(ws,ws[1:])])),
            "last_weights":ws[-1].tolist(),
        }
        if method in deviations:
            summary[method]["bootstrap_weight_l1_mean"]=float(np.mean(deviations[method]))
            summary[method]["bootstrap_weight_l1_p95"]=float(np.quantile(deviations[method],.95))
    return {"tickers":tickers, "common_price_rows":len(dates), "return_rows":len(r),
            "folds":folds, "oos_return_count":len(out["equal"]), "summary":summary,
            "limits":["Universe chosen retrospectively in 2026; diagnostic only.",
                      "Daily constant weights assume frictionless daily rebalancing. Target changes at block boundaries are not total realized turnover.",
                      "Same date labels do not imply synchronous US/CAD prices and BoC FX.",
                      "LW identity target differs from Honey 2004 constant-correlation target.",
                      "No claim of statistical significance or forecasting performance."]}


def sharpe_experiment():
    rng=np.random.default_rng(SEED)
    z=rng.standard_normal((100000,20))
    common=rng.standard_normal((100000,1))
    independent=z/np.sqrt(5)
    correlated=(np.sqrt(.8)*common+np.sqrt(.2)*z)/np.sqrt(5)
    result={}
    for name,m in [("independent",independent),("rho_0_8",correlated)]:
        maximum=m.max(axis=1)
        result[name]={"mean_max":float(maximum.mean()),
                      "p95_max":float(np.quantile(maximum,.95)),
                      "prob_max_exceeds_0_85":float(np.mean(maximum>.85))}
    result["independent_exact_p95"] = float(norm.ppf(.95**(1/20))/np.sqrt(5))
    result["annual_mean_se_pct_for_vol20_80"]=[20/np.sqrt(5),80/np.sqrt(5)]
    return result


if __name__ == "__main__":
    result={"created_at":datetime.now(timezone.utc).isoformat(), "seed":SEED,
            "python":sys.version,
            "packages":{k:version(k) for k in ["numpy","scipy","highspy","scikit-learn"]},
            "data_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in [DATA/"prices_daily.csv", DATA/"fx_usdcad_daily.csv"]},
            "references":references(), "iis":iis_experiment(),
            "robert":robert_experiment(), "covariance":covariance_experiment(),
            "sharpe_null":sharpe_experiment()}
    (HERE/"results.json").write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps({k:result[k] for k in ["packages","references","robert","sharpe_null"]},indent=2))
    print(json.dumps(result["covariance"]["summary"],indent=2))
