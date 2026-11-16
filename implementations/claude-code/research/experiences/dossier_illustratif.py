"""Nombres du dossier illustratif de Robert (15 novembre 2026). Hors produit, lecture seule, graine fixe.

    uv run python research/experiences/dossier_illustratif.py

Complète research/experiences/ecart_et_niveau.py pour l'exemple du document d'architecture : option à 5 % (révision),
comparateurs désignés par règle (fonds le plus corrélé au titre ; titre de volatilité la plus proche), écarts appariés
et intervalles. Aucun critère écrit d'avance : ce sont les nombres d'un exemple.
"""

import numpy as np

from datathon2026 import analytics as a
from datathon2026 import data
from datathon2026 import tools as T

SEED, WEEKS, THR, RF = 2026, 156, 0.15, 1.0322 ** (1 / 52) - 1
m = T.Session().market
u = data.load_universe().set_index("ticker")
base = T.load_scenarios()["robert"]["portefeuille_actuel"]
cols = list(m.weekly_returns.columns)
R = m.weekly_returns.to_numpy()
N = len(R)
w0 = np.array([base.get(c, 0.0) for c in cols])
C = m.weekly_returns.corr()
vol = m.weekly_returns.std(ddof=1) * np.sqrt(52)
fonds = [t for t in cols if u.loc[t, "asset_class"].startswith("etf")]
titres = [t for t in cols if not u.loc[t, "asset_class"].startswith("etf") and t != "TSLA" and base.get(t, 0) == 0]
f_star = max(fonds, key=lambda t: C.loc["TSLA", t])
v_star = min(titres, key=lambda t: abs(vol[t] - vol["TSLA"]))
print(f"Comparateurs par règle : fonds le plus corrélé à TSLA = {f_star} (corrélation {C.loc['TSLA', f_star]:.2f}) ; actif isolé de volatilité la plus proche = {v_star} ({vol[v_star]:.2f} contre {vol['TSLA']:.2f})")


def w_add(t, s):
    d = a.blend(base, t, s)
    return np.array([d.get(c, 0.0) for c in cols])


def idx(n_obs, weeks, n, block, seed):
    rng = np.random.default_rng(seed)
    out = np.empty((n, weeks), dtype=np.int64)
    out[:, 0] = rng.integers(0, n_obs, n)
    new, starts = rng.random((n, weeks)) < 1.0 / block, rng.integers(0, n_obs, (n, weeks))
    for t in range(1, weeks):
        out[:, t] = np.where(new[:, t], starts[:, t], (out[:, t - 1] + 1) % n_obs)
    return out


def dd(p):
    v = np.cumprod(1 + p, axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.ones((len(v), 1)), v], axis=1), axis=1)[:, 1:]
    return (v / peak - 1).min(axis=1)


def hyp(X, h):
    c = X - X.mean(axis=0)
    return c + (RF if h == "taux sans risque" else 0.0)


outer, inner = idx(N, N, 400, 13, SEED + 1), idx(N, WEEKS, 2_000, 13, SEED + 2)
opts = {"5 % de TSLA": w_add("TSLA", .05), "10 % de TSLA": w_add("TSLA", .10), f"10 % de {f_star}": w_add(f_star, .10), f"10 % de {v_star}": w_add(v_star, .10)}
for h in ("taux sans risque", "aucun rendement"):
    print(f"\nHypothèse : {h} — écart avec « ne rien changer » de la part des trajectoires de 3 ans franchissant 15 % (et de celles finissant sous le départ)")
    full = hyp(R, h)
    b0 = (full @ w0)[idx(N, WEEKS, 10_000, 13, SEED)]
    ref = (np.mean(dd(b0) < -THR), np.mean(np.prod(1 + b0, axis=1) < 1))
    res = {k: ([], []) for k in opts}
    spec, spec_f = [], []
    for o in outer:
        X = hyp(R[o], h)
        p0 = (X @ w0)[inner]
        s0, t0 = np.mean(dd(p0) < -THR), np.mean(np.prod(1 + p0, axis=1) < 1)
        cur = {}
        for k, w in opts.items():
            p = (X @ w)[inner]
            cur[k] = np.mean(dd(p) < -THR) - s0
            res[k][0].append(cur[k])
            res[k][1].append(np.mean(np.prod(1 + p, axis=1) < 1) - t0)
        spec.append(cur["10 % de TSLA"] - cur[f"10 % de {v_star}"])
        spec_f.append(cur["10 % de TSLA"] - cur[f"10 % de {f_star}"])
    I10 = idx(N, WEEKS, 10_000, 13, SEED)
    for k, w in opts.items():
        p = (full @ w)[I10]
        g, t = np.array(res[k][0]), np.array(res[k][1])
        print(f"   {k:16s} : baisse en route {np.mean(dd(p) < -THR) - ref[0]:+.3f} (90 % : {np.quantile(g, .05):+.3f} à {np.quantile(g, .95):+.3f} ; positif dans {np.mean(g > 0):.3f}) | perte à l'échéance {np.mean(np.prod(1 + p, axis=1) < 1) - ref[1]:+.3f} (90 % : {np.quantile(t, .05):+.3f} à {np.quantile(t, .95):+.3f} ; positif dans {np.mean(t > 0):.3f})")
    spec = np.array(spec)
    print(f"   écart propre au titre (10 % de TSLA moins 10 % de {v_star}) : 90 % de {np.quantile(spec, .05):+.3f} à {np.quantile(spec, .95):+.3f}")
    spec_f = np.array(spec_f)
    print(f"   écart entre 10 % de TSLA et 10 % de {f_star} (fonds comparateur) : 90 % de {np.quantile(spec_f, .05):+.3f} à {np.quantile(spec_f, .95):+.3f} ; positif dans {np.mean(spec_f > 0):.3f}")
    print(f"   niveaux de « ne rien changer » (illustration) : baisse en route {ref[0]:.3f} ; perte à l'échéance {ref[1]:.3f}")


# --- Compléments ajoutés après la revue de cohérence (15 novembre, 16 h) ---------------------------------------
# 1. L'intervalle de l'écart « 10 % de TSLA » (baisse en route) à chaque longueur de bloc de la grille proposée.
print("\nÉcart « 10 % de TSLA » contre « ne rien changer », baisse en route de plus de 15 % sur 3 ans, selon la longueur de bloc (intervalle à 90 %, 400 histoires, 2 000 trajectoires)")
for b in (1, 4, 13, 26):
    o_b, i_b = idx(N, N, 400, b, SEED + 10 + b), idx(N, WEEKS, 2_000, b, SEED + 20 + b)
    for h in ("taux sans risque", "aucun rendement"):
        g = []
        for o in o_b:
            X = hyp(R[o], h)
            g.append(np.mean(dd((X @ opts["10 % de TSLA"])[i_b]) < -THR) - np.mean(dd((X @ w0)[i_b]) < -THR))
        g = np.array(g)
        print(f"   bloc de {b:2d} semaine(s), {h:17s} : de {np.quantile(g, .05):+.3f} à {np.quantile(g, .95):+.3f} ; positif dans {np.mean(g > 0):.3f}")

# 2. La pire baisse observée, en valorisation hebdomadaire et quotidienne (jours ouvrables communs).
biz = m.daily[m.daily.index.day_of_week < 5][cols].dropna()
Rd = biz.pct_change().dropna().to_numpy()
for nom, w in (("ne rien changer", w0), ("10 % de TSLA", opts["10 % de TSLA"])):
    print(f"Pire baisse observée, {nom:16s} : hebdomadaire {dd((R @ w)[None, :])[0]:+.3f} ; quotidienne {dd((Rd @ w)[None, :])[0]:+.3f}")

# 3. Le comparateur de volatilité voisine change-t-il quand on retire une année ?
an = N // 5
for k in range(5):
    garde = np.r_[0:k * an, (k + 1) * an:N] if k < 4 else np.r_[0:k * an]
    v = m.weekly_returns.iloc[garde].std(ddof=1) * np.sqrt(52)
    c = m.weekly_returns.iloc[garde].corr()
    print(f"Sans l'année {k + 1} : fonds le plus corrélé = {max(fonds, key=lambda t: c.loc['TSLA', t])} ; volatilité la plus proche = {min(titres, key=lambda t: abs(v[t] - v['TSLA']))}")
