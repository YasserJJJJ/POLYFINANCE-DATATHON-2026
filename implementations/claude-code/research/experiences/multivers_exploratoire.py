"""Multivers exploratoire (15 novembre 2026), écrit par la recherche sur la confrontation, relu et réexécuté.

    uv run python research/experiences/multivers_exploratoire.py > research/experiences/sorties/multivers_exploratoire.json

Hors produit, lecture seule :
lit les données par la bibliothèque du projet, n'écrit rien dans le dépôt, n'appelle aucun service.
But : mesurer sur NOS données (cas Robert) l'ordre de grandeur de trois sources de variation d'une
part de trajectoires, pour fixer d'avance des critères de verdict réalistes :
  E1 bruit de simulation (graines), E2 taille des blocs, E3 retrait d'une année, E4 petit multivers.
Ce sont des scénarios rééchantillonnés à partir de cinq années observées, pas des probabilités de l'avenir.
"""
import itertools
import json
import sys

import numpy as np

from datathon2026 import analytics as a
from datathon2026 import tools as T

m = T.Session().market
base = T.load_scenarios()["robert"]["portefeuille_actuel"]
tick = ["XBB.TO", "ZST.TO", "XIU.TO", "SPY", "TSLA", "QQQ"]
R = m.weekly_returns[tick].dropna()
X0, N0 = R.to_numpy(), len(R)
opts = {"actuel": None, "10 % TSLA": ("TSLA", .10), "10 % QQQ": ("QQQ", .10)}
W = {k: np.array([(base if v is None else a.blend(base, *v)).get(t, 0.0) for t in tick]) for k, v in opts.items()}
RF_W = 1.032 ** (1 / 52) - 1


def boot(Xm, weeks, n, block, seed):
    N = len(Xm)
    rng = np.random.default_rng(seed)
    idx = np.empty((n, weeks), dtype=np.int64)
    idx[:, 0] = rng.integers(0, N, n)
    new, starts = rng.random((n, weeks)) < 1.0 / block, rng.integers(0, N, (n, weeks))
    for t in range(1, weeks):
        idx[:, t] = np.where(new[:, t], starts[:, t], (idx[:, t - 1] + 1) % N)
    return Xm[idx]


def dd(P, w):
    v = np.cumprod(1 + P @ w, axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.ones((len(v), 1)), v], axis=1), axis=1)[:, 1:]
    return (v / peak - 1).min(axis=1)


def shares(Xm, weeks, n, block, seed, thr):
    P = boot(Xm, weeks, n, block, seed)
    return {k: float(np.mean(dd(P, w) < -thr)) for k, w in W.items()}


def mean_hyp(Xm, hyp):
    if hyp == "historique":
        return Xm
    c = Xm - Xm.mean(axis=0)
    return c + (RF_W if hyp == "taux sans risque" else 0.0)


out = {"echantillon": {"semaines": N0, "debut": str(R.index[0].date()), "fin": str(R.index[-1].date())}}

# E1 — bruit de simulation : 8 graines, 10 000 trajectoires, 156 semaines, blocs de 13, seuil 15 %
e1 = [shares(X0, 156, 10_000, 13, s, .15) for s in range(100, 108)]
out["E1_graines"] = {k: {"moyenne": round(np.mean([e[k] for e in e1]), 4), "ecart_type": round(np.std([e[k] for e in e1], ddof=1), 4)} for k in W}
d = [e["10 % TSLA"] - e["actuel"] for e in e1]
out["E1_graines"]["ecart TSLA - actuel"] = {"moyenne": round(np.mean(d), 4), "ecart_type": round(np.std(d, ddof=1), 4)}

# E2 — taille moyenne des blocs
out["E2_blocs"] = {b: {k: round(v, 3) for k, v in shares(X0, 156, 10_000, b, 2026, .15).items()} for b in (2, 4, 8, 13, 26, 52)}

# E3 — retrait d'une tranche de 52 semaines (échantillon circulaire recollé)
years = [(i * 52, min((i + 1) * 52, N0) if i < 4 else N0) for i in range(5)]
e3 = {}
for i, (lo, hi) in enumerate(years):
    Xm = np.delete(X0, np.s_[lo:hi], axis=0)
    e3[f"sans {R.index[lo].date()} -> {R.index[hi - 1].date()}"] = {k: round(v, 3) for k, v in shares(Xm, 156, 10_000, 13, 2026, .15).items()}
out["E3_retrait_annee"] = e3

# E4 — petit multivers : 3 blocs x 3 hypothèses de moyenne x 3 seuils x 3 horizons x 6 échantillons = 486
grid = {"bloc": (4, 13, 26), "moyenne": ("historique", "taux sans risque", "aucune"), "seuil": (.125, .15, .175),
        "horizon": (104, 156, 208), "retrait": (None, 0, 1, 2, 3, 4)}
rows = []
for b, h, thr, wk, ret in itertools.product(*grid.values()):
    Xm = X0 if ret is None else np.delete(X0, np.s_[years[ret][0]:years[ret][1]], axis=0)
    s = shares(mean_hyp(Xm, h), wk, 4000, b, 2026, thr)
    rows.append({"bloc": b, "moyenne": h, "seuil": thr, "horizon": wk, "retrait": ret, **s})
dT = np.array([r["10 % TSLA"] - r["actuel"] for r in rows])
dQ = np.array([r["10 % TSLA"] - r["10 % QQQ"] for r in rows])
lvl = np.array([r["10 % TSLA"] for r in rows])
q = lambda x: [round(float(v), 3) for v in np.quantile(x, [0, .05, .25, .5, .75, .95, 1])]
out["E4_multivers"] = {
    "specifications": len(rows),
    "niveau 10 % TSLA (min, 5 %, 25 %, mediane, 75 %, 95 %, max)": q(lvl),
    "ecart TSLA - actuel": q(dT), "part des specifications ou ecart > 0": round(float(np.mean(dT > 0)), 3),
    "part ou ecart > 0,02": round(float(np.mean(dT > .02)), 3),
    "ecart TSLA - QQQ": q(dQ), "part des specifications ou TSLA > QQQ": round(float(np.mean(dQ > 0)), 3),
    "part ou TSLA - QQQ > 0,02": round(float(np.mean(dQ > .02)), 3),
}
# quelle décision pèse le plus : étendue des médianes par modalité, pour le niveau et pour l'écart
eff = {}
for f, vals in grid.items():
    medL = [float(np.median([r["10 % TSLA"] for r in rows if r[f] == v])) for v in vals]
    medD = [float(np.median([r["10 % TSLA"] - r["actuel"] for r in rows if r[f] == v])) for v in vals]
    eff[f] = {"etendue du niveau": round(max(medL) - min(medL), 3), "etendue de l'ecart": round(max(medD) - min(medD), 3)}
out["E4_multivers"]["poids des decisions"] = eff
json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
