"""Calcul exploratoire du diagnostic de refonte (15 novembre 2026). Hors produit : lit les données
par la bibliothèque du projet, n'écrit rien, n'appelle aucun service. Graine fixe.

    uv run python docs/refonte/calcul_exploratoire.py

Cas : Robert, portefeuille fictif de config/scenarios.toml, ajout de Tesla ou de QQQ.
Les parts de trajectoires viennent d'un rééchantillonnage stationnaire par blocs de l'historique
hebdomadaire : ce sont des scénarios tirés de cinq années observées, pas des probabilités de l'avenir.
"""

import numpy as np

from datathon2026 import analytics as a
from datathon2026 import data
from datathon2026 import tools as T

SEED, N_PATHS, BLOCK = 2026, 10_000, 13
m = T.Session().market
base = T.load_scenarios()["robert"]["portefeuille_actuel"]
tick = ["XBB.TO", "ZST.TO", "XIU.TO", "SPY", "TSLA", "QQQ"]
R = m.weekly_returns[tick].dropna()
X, N = R.to_numpy(), len(R)
options = {"actuel": None, "5 % TSLA": ("TSLA", .05), "9 % TSLA": ("TSLA", .09), "10 % TSLA": ("TSLA", .10),
           "16 % TSLA": ("TSLA", .16), "20 % TSLA": ("TSLA", .20), "10 % QQQ": ("QQQ", .10)}
W = {k: np.array([(base if v is None else a.blend(base, *v)).get(t, 0.0) for t in tick]) for k, v in options.items()}


def boot(Xm, weeks, n=N_PATHS, block=BLOCK, seed=SEED):
    """Rééchantillonnage stationnaire : blocs de longueur géométrique, moyenne `block`, échantillon circulaire."""
    rng = np.random.default_rng(seed)
    idx = np.empty((n, weeks), dtype=np.int64)
    idx[:, 0] = rng.integers(0, N, n)
    new, starts = rng.random((n, weeks)) < 1.0 / block, rng.integers(0, N, (n, weeks))
    for t in range(1, weeks):
        idx[:, t] = np.where(new[:, t], starts[:, t], (idx[:, t - 1] + 1) % N)
    return Xm[idx]


def worst_drawdown(P, w):
    v = np.cumprod(1 + P @ w, axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.ones((len(v), 1)), v], axis=1), axis=1)[:, 1:]
    return (v / peak - 1).min(axis=1)


def share(P, w, thr):
    return round(float(np.mean(worst_drawdown(P, w) < -thr)), 3)


print(f"Échantillon : {N} semaines communes, du {R.index[0].date()} au {R.index[-1].date()}")

print("\n1. Plus grande part qui n'aurait pas franchi le seuil sur l'historique (grille de 1 point, 0 à 30 %)")
for thr in (-0.10, -0.12, -0.125, -0.13, -0.15, -0.175, -0.20, -0.25):
    out = {t: T.share_sweep(T.Session(), "x", base, t, thr)["_brut"]["part_max"] for t in ("TSLA", "QQQ")}
    print(f"   seuil {thr:+.3f} :", {t: ("impossible" if v is None else round(v, 2)) for t, v in out.items()})

print("\n2. Historique, une seule trajectoire : pire baisse ; perte moyenne des 5 % pires semaines ; volatilité annualisée")
for k, w in W.items():
    r = X @ w
    v = np.cumprod(1 + r)
    dd = (v / np.maximum.accumulate(np.r_[1, v])[1:] - 1).min()
    worst = np.sort(r)[: max(1, int(round(0.05 * N)))]
    print(f"   {k:10s} {dd:+.3f} ; {worst.mean():+.4f} (sur {len(worst)} semaines) ; {r.std(ddof=1) * np.sqrt(52):.3f}")

print("\n3. Rendement moyen : moyenne arithmétique annualisée, erreur type (volatilité / racine du nombre d'années)")
for t in ("TSLA", "QQQ", "XIU.TO", "XBB.TO"):
    r = R[t]
    mu, se = (1 + r.mean()) ** 52 - 1, r.std(ddof=1) * np.sqrt(52) / np.sqrt(N / 52)
    print(f"   {t:7s} {mu:+.3f} ; erreur type {se:.3f} ; à deux erreurs types : de {mu - 2 * se:+.2f} à {mu + 2 * se:+.2f}")

macro = data.load_macro()
y2 = macro[(macro["series_id"] == "BD.CDN.2YR.DQ.YLD") & (macro["date"] >= R.index[0]) & (macro["date"] <= R.index[-1])]
rf_year = float(y2["value"].mean()) / 100
print(f"\n   Taux sans risque retenu : obligations du Canada à 2 ans, moyenne sur la fenêtre {rf_year * 100:.2f} % ({len(y2)} observations)")

centered = X - X.mean(axis=0)
tsla_only = X.copy()
tsla_only[:, tick.index("TSLA")] += (X @ W["actuel"]).mean() - X[:, tick.index("TSLA")].mean()
hypotheses = {"moyennes historiques": X, "taux sans risque pour tous les actifs": centered + (1 + rf_year) ** (1 / 52) - 1,
              "aucun rendement moyen crédité": centered, "Tesla seule ramenée à la moyenne du portefeuille actuel": tsla_only}

for weeks, label in ((156, "3 ans"), (104, "2 ans")):
    print(f"\n4. Part des trajectoires de {label} dont la pire baisse franchit le seuil ({N_PATHS} trajectoires, bloc moyen {BLOCK} semaines, graine {SEED})")
    for name, Xm in hypotheses.items():
        P = boot(Xm, weeks)
        print(f"   — {name}")
        for thr in (0.12, 0.15, 0.20):
            print(f"      seuil {thr:.2f} :", {k: share(P, w, thr) for k, w in W.items()})

print("\n5. Stabilité : seuil 15 %, 3 ans, moyennes historiques")
for block in (4, 13, 26):
    P = boot(X, 156, block=block)
    print(f"   bloc moyen {block:2d} :", {k: share(P, W[k], 0.15) for k in ("actuel", "10 % TSLA", "10 % QQQ")})
vals = [share(boot(X, 156, seed=sd), W["10 % TSLA"], 0.15) for sd in (1, 2, 3, 4, 5)]
print("   cinq graines, 10 % TSLA :", vals, "; écart type", round(float(np.std(vals, ddof=1)), 4))

print("\n6. Perte à l'échéance plutôt que baisse en route")
print("   Historique : rendement le plus bas sur toutes les fenêtres glissantes de 3 ans (nombre de fenêtres)")
for k, v in options.items():
    w = base if v is None else a.blend(base, *v)
    win = a.worst_window(a.portfolio(m, w).index, 3)
    print(f"   {k:10s} {win.worst:+.3f} ({win.n_starts} départs, {win.n_independent} fenêtre sans chevauchement)")
print("   Part des trajectoires de 3 ans finissant sous la valeur de départ")
for name, Xm in hypotheses.items():
    P = boot(Xm, 156)
    print(f"   — {name} :", {k: round(float(np.mean(np.prod(1 + P @ w, axis=1) < 1)), 3) for k, w in W.items()})

print("\n7. Sensibilité aux conventions de calcul (pire baisse historique ; rendement annualisé composé)")
daily = m.daily[list(base) + ["TSLA"]].ffill().dropna()
span = (daily.index[-1] - daily.index[0]).days / 365.25
fridays = daily.resample("W-FRI").last().index


def low(v):
    v = np.asarray(v, dtype=float)
    return float((v / np.maximum.accumulate(v) - 1).min())


for part in (0.0, 0.06, 0.07, 0.09, 0.10, 0.20):
    w = a.blend(base, "TSLA", part) if part else dict(base)
    cols, wv = list(w), np.array(list(w.values()))
    p = a.portfolio(m, w)  # convention du produit : rééquilibrage et valorisation hebdomadaires
    vals, cur, prev = [1.0], 1.0, daily.index[0]
    for end in fridays:  # rééquilibrage hebdomadaire, valorisation quotidienne
        seg = daily.loc[(daily.index > prev) & (daily.index <= end), cols]
        if seg.empty:
            continue
        start = daily.loc[prev, cols].to_numpy()
        vals += [cur * float((wv * row / start).sum()) for row in seg.to_numpy()]
        cur, prev = vals[-1], seg.index[-1]
    hold = (daily[cols] / daily[cols].iloc[0] * wv).sum(axis=1).to_numpy()  # achat-conservation, valorisation quotidienne
    print(f"   Tesla {part:4.0%} | produit : {low(p.index):+.4f}, rendement {a.cagr(p.index):+.3f}"
          f" | même rééquilibrage, vu chaque jour : {low(vals):+.4f}"
          f" | achat-conservation : {low(hold):+.4f}, rendement {(hold[-1] / hold[0]) ** (1 / span) - 1:+.3f}")
peak = m.daily["TSLA"].dropna().loc[:"2022-06-30"].idxmax()
print(f"   Sommet de Tesla avant sa pire baisse : {peak.date()} ({peak.day_name()})")

print("\n8. Même demande, même scénario, trois profils (workflow fixe du produit)")
from datathon2026 import workflow  # noqa: E402

sc_robert = T.load_scenarios()["robert"]
ref = workflow.robert(dict(sc_robert)).to_dict()
for persona in ("amira", "mateo"):
    d = workflow.robert(dict(sc_robert, persona=persona)).to_dict()
    diff = [x["id"] for x, y in zip(ref["affirmations"], d["affirmations"]) if x["texte"] != y["texte"]]
    same = [ref["enregistrements"][h["valeur"]]["display"] for h in ref["chiffres_cles"]] == [d["enregistrements"][h["valeur"]]["display"] for h in d["chiffres_cles"]]
    print(f"   {persona} : {len(diff)} affirmations différentes sur {len(d['affirmations'])} ({', '.join(diff)}) ; chiffres clés identiques : {same} ; contrôle conforme : {d['verification']['ok']}")
