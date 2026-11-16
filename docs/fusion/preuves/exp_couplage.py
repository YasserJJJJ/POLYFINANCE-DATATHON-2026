"""Expérience isolée : le moteur historique de B (stdlib) peut-il nourrir la règle « perte supportable » de C ?"""
import sys, json, inspect
sys.path.insert(0, sys.argv[1])
from alphaforge_app import analytics as an
from alphaforge_app.datasets import load_dataset
ds = load_dataset(sys.argv[2])
print("set_target_weight:", inspect.signature(an.set_target_weight))
out = {}
cas = {
 "robert": ({"XIU.TO": 1/3, "XBB.TO": 1/3, "RY.TO": 1/3}, "TSLA", 80000/400000, 400000, 15.5),
 "amira":  ({"QQQ": 0.5, "NVDA": 0.5}, "BTC-USD", 10000/40000, 40000, None),
 "mateo":  ({"XIU.TO": 0.5, "XBB.TO": 0.5}, "ENB.TO", 15000/120000, 120000, None),
}
for nom, (base, t, part, cap, limite) in cas.items():
    apres = an.set_target_weight(base, t, part)
    r = an.compare_portfolios([{"id": "avant", "name": "avant", "weights": base}, {"id": "apres", "name": "apres", "weights": apres}], capital_cad=cap, dataset=ds)
    seul = an.analyze_portfolio({t: 1.0}, capital_cad=cap, dataset=ds)
    def m(o):
        mm = o.get("metrics", o)
        return {k: mm.get(k) for k in ("max_drawdown_pct", "volatility_pct", "cagr_pct", "ending_value_cad", "drawdown_peak_date", "drawdown_trough_date")}
    a, b = (m(o) for o in r["options"])
    out[nom] = {"poids_apres": {k: round(v, 4) for k, v in apres.items()}, "avant": a, "apres": b, "actif_seul": m(seul),
                "approx_C_poids_x_pire_chute_pct": round(part * abs(m(seul)["max_drawdown_pct"]), 2),
                "ecart_apparie_drawdown_pts": round(b["max_drawdown_pct"] - a["max_drawdown_pct"], 2),
                "fenetre": [r["meta"]["start"], r["meta"]["end"], r["meta"]["observations"]]}
print(json.dumps(out, indent=1, ensure_ascii=False))
json.dump(out, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)
