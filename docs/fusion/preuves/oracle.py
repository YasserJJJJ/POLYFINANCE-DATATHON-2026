import sys, json, math
import pandas as pd, numpy as np
D = sys.argv[1]
px = pd.read_csv(f"{D}/prices_daily.csv", parse_dates=["date"])
fx = pd.read_csv(f"{D}/fx_usdcad_daily.csv", parse_dates=["date"])
uni = pd.read_csv(f"{D}/assets_universe.csv")
print("colonnes prix:", list(px.columns)); print("colonnes fx:", list(fx.columns)); print("colonnes univers:", list(uni.columns))
fxcol = [c for c in fx.columns if c != "date"][0]
fxs = fx.set_index("date")[fxcol].astype(float).sort_index()
tcol = "ticker" if "ticker" in px.columns else "symbol"
out = {}
for t in ["TSLA", "BTC-USD", "ENB.TO", "SPY"]:
    d = px[px[tcol] == t].set_index("date").sort_index()
    cur = d["currency"].iloc[0] if "currency" in d.columns else "?"
    s = d["adj_close"].astype(float)
    res = {"devise_cotation": cur, "n_obs": int(len(s)), "debut": str(s.index[0].date()), "fin": str(s.index[-1].date())}
    series = {"locale": s}
    if cur == "USD":
        f = fxs.reindex(s.index.union(fxs.index)).ffill().reindex(s.index)   # dernier taux connu, sans regard vers l'avant
        series["CAD"] = s * f
    for name, x in series.items():
        x = x.dropna()
        yrs = (x.index[-1] - x.index[0]).days / 365.25
        cagr = (x.iloc[-1] / x.iloc[0]) ** (1 / yrs) - 1
        lr = np.log(x / x.shift(1)).dropna()
        w = x.resample("W-FRI").last().dropna(); wr = w.pct_change().dropna()
        dd = (x / x.cummax() - 1).min(); ddw = (w / w.cummax() - 1).min()
        res[name] = {"rendement_annualise_pct": round(cagr * 100, 2),
                     "vol_quot_log_r252_pct": round(lr.std() * math.sqrt(252) * 100, 2),
                     "vol_quot_log_r365_pct": round(lr.std() * math.sqrt(365) * 100, 2),
                     "vol_hebdo_simple_r52_pct": round(wr.std() * math.sqrt(52) * 100, 2),
                     "pire_baisse_quot_pct": round(dd * 100, 2), "pire_baisse_hebdo_pct": round(ddw * 100, 2)}
    out[t] = res
def wk(t):
    d = px[px[tcol] == t].set_index("date").sort_index()["adj_close"].astype(float)
    if (px[px[tcol] == t]["currency"].iloc[0] if "currency" in px.columns else "") == "USD":
        d = d * fxs.reindex(d.index.union(fxs.index)).ffill().reindex(d.index)
    return d.resample("W-FRI").last().dropna().pct_change()
c = pd.concat([wk("TSLA"), wk("SPY")], axis=1, join="inner").dropna().corr().iloc[0, 1]
out["corr_TSLA_SPY_hebdo_CAD"] = round(float(c), 3)
json.dump(out, open(sys.argv[2], "w"), indent=1, ensure_ascii=False); print(json.dumps(out, indent=1, ensure_ascii=False))
