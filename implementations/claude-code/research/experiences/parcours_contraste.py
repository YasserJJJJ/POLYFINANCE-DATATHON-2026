"""Parcours contrasté (15 novembre 2026) : mesures pour le dossier illustratif de Mateo. Hors produit, lecture seule.

    uv run python research/experiences/parcours_contraste.py

Demande fictive : « Mon portefeuille est-il bien diversifié ? Je voudrais aussi qu'il respecte mes préférences ESG,
sans pétrole. » Portefeuille fictif, inventé pour l'exemple (aucun n'est donné par l'énoncé).
Aucun critère écrit d'avance : ce sont les nombres d'un exemple, pas une expérience discriminante.
"""

import numpy as np

from datathon2026 import data
from datathon2026 import tools as T

SEED = 2026
m = T.Session().market
u = data.load_universe().set_index("ticker")
P0 = {"XIU.TO": .25, "SPY": .25, "ENB.TO": .10, "CNQ.TO": .10, "RY.TO": .10, "XBB.TO": .20}


def sans(p, retires):
    q = {k: v for k, v in p.items() if k not in retires}
    s = sum(q.values())
    return {k: v / s for k, v in q.items()}


def remplace(p, a, b):
    return {(b if k == a else k): v for k, v in p.items()}


OPTIONS = {
    "ne rien changer": P0,
    "sans le secteur Énergie (ENB.TO, CNQ.TO)": sans(P0, {"ENB.TO", "CNQ.TO"}),
    "fonds filtré ESGV à la place de SPY": remplace(P0, "SPY", "ESGV"),
    "les deux": remplace(sans(P0, {"ENB.TO", "CNQ.TO"}), "SPY", "ESGV"),
    "sans les producteurs seulement (CNQ.TO)": sans(P0, {"CNQ.TO"}),
}
tick = sorted({t for p in OPTIONS.values() for t in p})
Rw = m.weekly_returns[tick]
biz = m.daily[m.daily.index.day_of_week < 5][tick].dropna()
Rd = biz.pct_change().dropna()
print("Secteur des lignes détenues en direct :", {t: u.loc[t, "sector"] for t in P0})
print("Part du secteur Énergie visible dans les lignes en direct : %.0f %% ; à l'intérieur de XIU.TO : inconnue (aucune composition de fonds dans les données)" % (100 * (P0["ENB.TO"] + P0["CNQ.TO"])))
print(f"Semaines : {len(Rw)} ; jours ouvrables communs : {len(Rd)}")


def w_of(p):
    return np.array([p.get(t, 0.0) for t in tick])


def dd(r):
    v = np.cumprod(1 + r, axis=-1)
    peak = np.maximum.accumulate(np.concatenate([np.ones(v.shape[:-1] + (1,)), v], axis=-1), axis=-1)[..., 1:]
    return (v / peak - 1).min(axis=-1)


def mesures(X, w, k):
    r = X @ w
    C = np.cov(X, rowvar=False)
    var = w @ C @ w
    rc = w * (C @ w) / var
    tail = np.sort(r)[: max(1, int(round(0.05 * len(r))))]
    return {"vol": np.sqrt(var * k), "pire_baisse": float(dd(r)), "pires_5pc": float(tail.mean()), "n_eff": float(1 / np.sum(rc ** 2)), "rc": rc}


def idx(n, b, B, seed):
    rng = np.random.default_rng(seed)
    out = np.empty((B, n), dtype=np.int64)
    out[:, 0] = rng.integers(0, n, B)
    new, starts = rng.random((B, n)) < 1 / b, rng.integers(0, n, (B, n))
    for t in range(1, n):
        out[:, t] = np.where(new[:, t], starts[:, t], (out[:, t - 1] + 1) % n)
    return out


Xw, Xd = Rw.to_numpy(), Rd.to_numpy()
I = idx(len(Xw), 13, 2000, SEED)
ref = mesures(Xw, w_of(P0), 52)
print("\nMesures hebdomadaires en dollars canadiens (volatilité annualisée ; pire baisse observée ; perte moyenne des 5 % pires semaines ; nombre effectif de lignes en risque)")
for name, p in OPTIONS.items():
    w = w_of(p)
    a_, d_ = mesures(Xw, w, 52), mesures(Xd, w, 252)
    top = max(zip(a_["rc"], tick))
    energie = sum(x for x, t in zip(a_["rc"], tick) if u.loc[t, "sector"] == "Energy")
    energie_d = sum(x for x, t in zip(d_["rc"], tick) if u.loc[t, "sector"] == "Energy")
    line = (f"   {name:42s} vol {a_['vol']:.4f} (quotidien {d_['vol']:.4f}) ; pire baisse {a_['pire_baisse']:+.4f} ; pires semaines {a_['pires_5pc']:+.4f} ; lignes effectives {a_['n_eff']:.2f} (quotidien {d_['n_eff']:.2f})"
            f" ; premier contributeur {top[1]} {top[0]:.3f} ; part de risque des titres Énergie {energie:.3f} (quotidien {energie_d:.3f})")
    if p is not P0:
        w0 = w_of(P0)
        dv, dc, dw, dn = [], [], [], []
        for i in I:
            x = Xw[i]
            a1, a0 = mesures(x, w, 52), mesures(x, w0, 52)
            dv.append(a1["vol"] - a0["vol"]); dc.append(a1["pires_5pc"] - a0["pires_5pc"]); dw.append(a1["pire_baisse"] - a0["pire_baisse"]); dn.append(a1["n_eff"] - a0["n_eff"])
        q = lambda z: f"{np.quantile(z, .05):+.4f} à {np.quantile(z, .95):+.4f}"  # noqa: E731
        line += f"\n      écarts appariés avec « ne rien changer », intervalles à 90 % : volatilité {a_['vol'] - ref['vol']:+.4f} ({q(dv)}) ; pires semaines {a_['pires_5pc'] - ref['pires_5pc']:+.4f} ({q(dc)}) ; pire baisse {a_['pire_baisse'] - ref['pire_baisse']:+.4f} ({q(dw)}) ; lignes effectives {a_['n_eff'] - ref['n_eff']:+.2f} ({q(dn)})"
    print(line)

print("\nFonds filtré contre fonds large")
for label, X, k in (("hebdomadaire, CAD", Rw, 52), ("quotidien, CAD", Rd, 252)):
    c = X["ESGV"].corr(X["SPY"])
    print(f"   {label} : corrélation ESGV-SPY {c:.3f} ; volatilité ESGV {X['ESGV'].std() * np.sqrt(k):.4f}, SPY {X['SPY'].std() * np.sqrt(k):.4f}")
e, s = Rw["ESGV"].to_numpy(), Rw["SPY"].to_numpy()
dvol = [(e[i].std(ddof=1) - s[i].std(ddof=1)) * np.sqrt(52) for i in I]
print(f"   écart de volatilité ESGV moins SPY : {(e.std(ddof=1) - s.std(ddof=1)) * np.sqrt(52):+.4f} ; intervalle à 90 % de {np.quantile(dvol, .05):+.4f} à {np.quantile(dvol, .95):+.4f}")
print("\nCorrélations selon la convention (hebdomadaire CAD | quotidien CAD)")
for a_, b_ in (("XIU.TO", "SPY"), ("XIU.TO", "XBB.TO"), ("ENB.TO", "XIU.TO"), ("CNQ.TO", "XIU.TO"), ("RY.TO", "XIU.TO")):
    print(f"   {a_:7s} {b_:7s} {Rw[a_].corr(Rw[b_]):+.2f} | {Rd[a_].corr(Rd[b_]):+.2f}")

# --- Complément ajouté après la revue de cohérence (15 novembre, 16 h) : l'écart de lignes effectives selon la
# longueur de bloc du rééchantillonnage et selon la fréquence des rendements.
print("\nÉcart de lignes effectives avec « ne rien changer », selon la longueur de bloc et la fréquence (intervalle à 90 %, 2 000 histoires)")
w0_ = w_of(P0)
for name in ("sans le secteur Énergie (ENB.TO, CNQ.TO)", "sans les producteurs seulement (CNQ.TO)", "fonds filtré ESGV à la place de SPY"):
    w = w_of(OPTIONS[name])
    for label, X, blocs in (("hebdomadaire", Xw, (1, 4, 13, 26)), ("quotidien", Xd, (5, 20, 65, 130))):
        for b in blocs:
            d = [mesures(X[i], w, 1)["n_eff"] - mesures(X[i], w0_, 1)["n_eff"] for i in idx(len(X), b, 2000, SEED + b)]
            print(f"   {name:42s} {label:13s} bloc de {b:3d} : de {np.quantile(d, .05):+.2f} à {np.quantile(d, .95):+.2f} ; négatif dans {np.mean(np.array(d) < 0):.3f}")

# Écart de volatilité du fonds filtré avec le fonds large, selon la fréquence et la longueur de bloc.
print("\nÉcart de volatilité annualisée ESGV moins SPY, selon la fréquence et la longueur de bloc (intervalle à 90 %, 2 000 histoires)")
for label, X, k, blocs in (("hebdomadaire", Rw, 52, (1, 4, 13, 26)), ("quotidien", Rd, 252, (5, 20, 65, 130))):
    e_, s_ = X["ESGV"].to_numpy(), X["SPY"].to_numpy()
    for b in blocs:
        d = [(e_[i].std(ddof=1) - s_[i].std(ddof=1)) * np.sqrt(k) for i in idx(len(X), b, 2000, SEED + 100 + b)]
        print(f"   {label:13s} bloc de {b:3d} : observé {(e_.std(ddof=1) - s_.std(ddof=1)) * np.sqrt(k):+.4f} ; de {np.quantile(d, .05):+.4f} à {np.quantile(d, .95):+.4f} ; positif dans {np.mean(np.array(d) > 0):.3f}")
