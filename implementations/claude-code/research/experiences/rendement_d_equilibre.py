"""Rendement d'équilibre (15 novembre 2026). Hors produit, lecture seule, graine fixe.

    uv run python research/experiences/rendement_d_equilibre.py

Essai décidé après la critique d'ensemble de la recherche (aucun critère écrit d'avance) : une analyse qui ne crédite
aucun rendement conclut toujours pour « ne rien changer ». Au lieu de supposer un rendement, on calcule celui qu'il
faudrait : de combien par an le titre ajouté doit-il battre le taux sans risque pour que l'option « 10 % du titre »
ne soit pas plus défavorable que « ne rien changer », selon la mesure retenue ? Tous les autres actifs sont crédités
du taux sans risque (3,22 % par an). Trajectoires de 3 ans, bloc de 13 semaines.
"""

import numpy as np

from datathon2026 import analytics as a
from datathon2026 import tools as T

SEED, WEEKS, THR, RF = 2026, 156, 0.15, 1.0322 ** (1 / 52) - 1
m = T.Session().market
base = T.load_scenarios()["robert"]["portefeuille_actuel"]
cols = list(m.weekly_returns.columns)
R = m.weekly_returns.to_numpy()
N = len(R)
w0 = np.array([base.get(c, 0.0) for c in cols])
GRID = np.arange(0, 0.81, 0.01)


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


def equilibre(X, ticker, inner):
    """Plus petit surcroît annuel de rendement du titre pour lequel l'option n'est pas plus défavorable, par mesure."""
    Xc = X - X.mean(axis=0) + RF
    d = a.blend(base, ticker, 0.10)
    w1 = np.array([d.get(c, 0.0) for c in cols])
    j = cols.index(ticker)
    p0 = (Xc @ w0)[inner]
    ref = {"finir sous la valeur de départ": np.mean(np.prod(1 + p0, axis=1) < 1), "franchir 15 % de baisse en route": np.mean(dd(p0) < -THR)}
    out = {k: None for k in ref}
    p1 = (Xc @ w1)[inner]
    for g in GRID:
        p = p1 + w1[j] * ((1 + g) ** (1 / 52) - 1)
        val = {"finir sous la valeur de départ": np.mean(np.prod(1 + p, axis=1) < 1), "franchir 15 % de baisse en route": np.mean(dd(p) < -THR)}
        for k in ref:
            if out[k] is None and val[k] <= ref[k]:
                out[k] = g
    return out, ref


inner = idx(N, WEEKS, 4_000, 13, SEED)
print(f"Tous les actifs crédités du taux sans risque ({(1 + RF) ** 52 - 1:.2%} par an) ; trajectoires de {WEEKS} semaines ; grille de 0 à 80 % par pas de 1 point")
for t in ("TSLA", "QQQ", "BTC-USD"):
    eq, ref = equilibre(R, t, inner)
    print(f"\n10 % de {t} — référence « ne rien changer » : " + " ; ".join(f"{k} {v:.3f}" for k, v in ref.items()))
    outer = idx(N, N, 200, 13, SEED + 1)
    samples = {k: [] for k in eq}
    for o in outer:
        e, _ = equilibre(R[o], t, inner)
        for k in e:
            samples[k].append(np.nan if e[k] is None else e[k])
    for k in eq:
        s = np.array(samples[k])
        hors = np.mean(np.isnan(s))
        q = np.nanquantile(s, [.05, .5, .95]) if hors < 1 else [np.nan] * 3
        print(f"   {k:34s} : surcroît de rendement d'équilibre " + ("au-delà de 80 % par an" if eq[k] is None else f"{eq[k]:.0%} par an")
              + f" ; sur 200 histoires rééchantillonnées : 5 % {q[0]:.0%}, médiane {q[1]:.0%}, 95 % {q[2]:.0%} ; au-delà de la grille dans {hors:.0%} des histoires")
