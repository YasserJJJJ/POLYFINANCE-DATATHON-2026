"""Ce que cinq ans établissent sur un écart et sur un niveau (15 novembre 2026). Hors produit, lecture seule, graine fixe.

    uv run python research/experiences/ecart_et_niveau.py

Vérifications décidées après les rapports des vérificateurs de la recherche (aucun critère écrit d'avance) :
ils reprochent au multivers de mêler la question (seuil, horizon) et les choix d'analyse, à la dépendance à une
année d'être mesurée sous la seule moyenne historique, à la marge de verdict d'ignorer l'incertitude d'échantillon,
et à l'écart attribué à Tesla de ne pas être propre à Tesla. Tout est recalculé ici à question fixée :
part des trajectoires de 3 ans dont la pire baisse franchit 15 %.
"""

import numpy as np

from datathon2026 import analytics as a
from datathon2026 import tools as T

SEED, WEEKS, THR, RF = 2026, 156, 0.15, 1.0322 ** (1 / 52) - 1
m = T.Session().market
base = T.load_scenarios()["robert"]["portefeuille_actuel"]
cols = list(m.weekly_returns.columns)
Rall = m.weekly_returns.to_numpy()
N = len(Rall)
w0 = np.array([base.get(c, 0.0) for c in cols])


def w_add(t, s=0.10):
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
    if h == "moyennes historiques":
        return X
    c = X - X.mean(axis=0)
    return c + (RF if h == "taux sans risque" else 0.0)


HYP = ("moyennes historiques", "taux sans risque", "aucun rendement")
years = [(i * 52, (i + 1) * 52 if i < 4 else N) for i in range(5)]


def shares(X, ws, block=13, n=10_000, seed=SEED):
    I = idx(len(X), WEEKS, n, block, seed)
    return [float(np.mean(dd((X @ w)[I]) < -THR)) for w in ws]


wT = w_add("TSLA")
print(f"Question fixée : trajectoires de {WEEKS} semaines, seuil de {THR:.0%} ; {N} semaines observées")

print("\nA. Étendue à question fixée (niveau avec 10 % de Tesla ; écart avec « ne rien changer »), 4 000 trajectoires par variante")
rows = []
for b in (4, 13, 26):
    for h in HYP:
        for ret in (None, 0, 1, 2, 3, 4):
            X = Rall if ret is None else np.delete(Rall, np.s_[years[ret][0]:years[ret][1]], axis=0)
            s0, s1 = shares(hyp(X, h), [w0, wT], block=b, n=4_000)
            rows.append((b, h, ret, s1, s1 - s0))
lv, gp = np.array([r[3] for r in rows]), np.array([r[4] for r in rows])
print(f"   54 variantes (bloc, hypothèse de rendement, année retirée) : niveau de {lv.min():.3f} à {lv.max():.3f} ; écart de {gp.min():+.3f} à {gp.max():+.3f} ; écart positif dans {np.mean(gp > 0):.3f} des variantes")
full = [r for r in rows if r[2] is None]
print(f"   9 variantes sur l'échantillon complet : niveau de {min(r[3] for r in full):.3f} à {max(r[3] for r in full):.3f} ; écart de {min(r[4] for r in full):+.3f} à {max(r[4] for r in full):+.3f}")
no_hist = [r for r in rows if r[1] != "moyennes historiques"]
print(f"   36 variantes sans la moyenne historique : niveau de {min(r[3] for r in no_hist):.3f} à {max(r[3] for r in no_hist):.3f} ; écart de {min(r[4] for r in no_hist):+.3f} à {max(r[4] for r in no_hist):+.3f}")

print("\nB. Retrait d'une année, sous chaque hypothèse de rendement (bloc de 13, 10 000 trajectoires), et erreur type par retrait d'un bloc annuel")
for h in HYP:
    s0, s1 = shares(hyp(Rall, h), [w0, wT])
    lev, gap = [], []
    for lo, hi in years:
        X = np.delete(Rall, np.s_[lo:hi], axis=0)
        u0, u1 = shares(hyp(X, h), [w0, wT])
        lev.append(u1)
        gap.append(u1 - u0)
    lev, gap = np.array(lev), np.array(gap)
    jk = lambda z: float(np.sqrt(4 / 5 * np.sum((z - z.mean()) ** 2)))  # noqa: E731
    print(f"   {h:22s} : niveau {s1:.3f} (sans chaque année : " + ", ".join(f"{x:.3f}" for x in lev) + f" ; erreur type {jk(lev):.3f}) | écart {s1 - s0:+.3f} (" + ", ".join(f"{x:+.3f}" for x in gap) + f" ; erreur type {jk(gap):.3f})")

print("\nC. Intervalle d'échantillonnage de l'écart : 400 histoires rééchantillonnées (bloc de 13), 2 000 trajectoires chacune")
outer = idx(N, N, 400, 13, SEED + 1)
inner = idx(N, WEEKS, 2_000, 13, SEED + 2)
for h in HYP:
    g, l = [], []
    for o in outer:
        X = hyp(Rall[o], h)
        p0, p1 = (X @ w0)[inner], (X @ wT)[inner]
        s0, s1 = np.mean(dd(p0) < -THR), np.mean(dd(p1) < -THR)
        g.append(s1 - s0)
        l.append(s1)
    g, l = np.array(g), np.array(l)
    print(f"   {h:22s} : niveau, intervalle à 90 % de {np.quantile(l, .05):.3f} à {np.quantile(l, .95):.3f} | écart, de {np.quantile(g, .05):+.3f} à {np.quantile(g, .95):+.3f} ; écart positif dans {np.mean(g > 0):.3f} des histoires")

print("\nD. L'écart est-il propre à Tesla ? Ajout de 10 % de chacun des 27 actifs hors portefeuille (bloc de 13, 4 000 trajectoires)")
vol = m.weekly_returns.std(ddof=1) * np.sqrt(52)
others = [c for c in cols if base.get(c, 0.0) == 0.0]
for h in ("aucun rendement", "taux sans risque", "moyennes historiques"):
    X = hyp(Rall, h)
    res = shares(X, [w0] + [w_add(t) for t in others], n=4_000)
    gaps = sorted(((res[i + 1] - res[0], t) for i, t in enumerate(others)), reverse=True)
    rank = [t for _, t in gaps].index("TSLA") + 1
    near = min((t for t in others if t != "TSLA"), key=lambda t: abs(vol[t] - vol["TSLA"]))
    gT, gN = dict((t, g) for g, t in gaps)["TSLA"], dict((t, g) for g, t in gaps)[near]
    print(f"   {h:22s} : écart positif pour {sum(g > 0 for g, _ in gaps)} actifs sur {len(others)} ; Tesla {gT:+.3f}, rang {rank} ; premiers : " + ", ".join(f"{t} {g:+.3f}" for g, t in gaps[:5])
          + f" ; actif de volatilité la plus proche ({near}, {vol[near]:.2f} contre {vol['TSLA']:.2f}) : {gN:+.3f}")
