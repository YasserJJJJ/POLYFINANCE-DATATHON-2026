"""Calibration du rééchantillonnage stationnaire sur des processus connus (15 novembre 2026). Hors produit, sans données réelles.

    uv run python research/experiences/calibration_reechantillonnage.py

Question (posée par la recherche sur l'analyse) : quand le monde est stationnaire et connu, un échantillon de 261 semaines
permet-il d'estimer par rééchantillonnage la part des trajectoires dont la pire baisse franchit 15 % ?

Critère écrit AVANT l'exécution :
X8  Si, le rendement moyen étant imposé à sa vraie valeur, moins de 90 % des échantillons de 261 semaines donnent une part
    à moins de 10 points de la vraie part à trois ans, les formulations « part de trajectoires » ne restituent pas de
    niveau : seulement des écarts appariés entre options, et le niveau à titre d'illustration.
    Écart apparié : si le signe de l'écart entre deux portefeuilles (le second étant le premier amplifié) est correct dans
    au moins 95 % des échantillons, la comparaison est déclarée informative.

Trois processus hebdomadaires, de volatilité annuelle voisine de 10 % (celle du portefeuille « 10 % de Tesla ») :
A  tirages indépendants gaussiens ; B  GARCH(1,1) à forte persistance (0,10 ; 0,85) ; C  deux régimes (calme, crise) de
durées moyennes 150 et 26 semaines. Rendement moyen : nul, puis 0,17 % par semaine.
"""

import numpy as np

SEED, N, S, PATHS, BLOCK, THR = 2026, 261, 400, 2000, 13, 0.15
SIG = 0.102 / np.sqrt(52)
K = 0.073 / 0.102  # second portefeuille : même hasard, volatilité du portefeuille actuel


def worst_dd(p):
    v = np.cumprod(1 + p, axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.ones((len(v), 1)), v], axis=1), axis=1)[:, 1:]
    return (v / peak - 1).min(axis=1)


def boot_idx(n_obs, weeks, n, block, rng):
    idx = np.empty((n, weeks), dtype=np.int64)
    idx[:, 0] = rng.integers(0, n_obs, n)
    new, starts = rng.random((n, weeks)) < 1.0 / block, rng.integers(0, n_obs, (n, weeks))
    for t in range(1, weeks):
        idx[:, t] = np.where(new[:, t], starts[:, t], (idx[:, t - 1] + 1) % n_obs)
    return idx


def simulate(kind, n_paths, weeks, mu, rng):
    """Chocs centrés de volatilité inconditionnelle proche de SIG, auxquels on ajoute mu."""
    if kind == "A":
        e = rng.normal(0, SIG, (n_paths, weeks))
    elif kind == "B":
        a, b = 0.10, 0.85
        w = SIG ** 2 * (1 - a - b)
        burn = 200
        z = rng.normal(size=(n_paths, weeks + burn))
        e = np.empty_like(z)
        var = np.full(n_paths, SIG ** 2)
        for t in range(weeks + burn):
            e[:, t] = np.sqrt(var) * z[:, t]
            var = w + a * e[:, t] ** 2 + b * var
        e = e[:, burn:]
    else:
        p_in, p_out = 1 / 150, 1 / 26
        pi = p_in / (p_in + p_out)
        s_c = SIG / np.sqrt((1 - pi) + pi * 2.5 ** 2)  # la volatilité des chocs vaut SIG ; l'écart de moyenne entre régimes s'y ajoute
        state = rng.random(n_paths) < pi
        e = np.empty((n_paths, weeks))
        for t in range(weeks):
            u = rng.random(n_paths)
            state = np.where(state, u > p_out, u < p_in)
            e[:, t] = rng.normal(size=n_paths) * np.where(state, 2.5 * s_c, s_c) + np.where(state, -0.004, 0.004 * pi / (1 - pi))
    return e + mu


rng = np.random.default_rng(SEED)
print(f"{S} échantillons de {N} semaines par processus ; {PATHS} trajectoires rééchantillonnées par échantillon ; bloc moyen {BLOCK} ; seuil {THR:.0%}")
for mu, mu_label in ((0.0, "rendement moyen nul"), (0.0017, "rendement moyen de 0,17 % par semaine")):
    for kind, name in (("A", "tirages indépendants"), ("B", "GARCH persistant"), ("C", "deux régimes")):
        for weeks in (52, 156):
            truth_paths = simulate(kind, 100_000, weeks, mu, rng)
            truth = float(np.mean(worst_dd(truth_paths) < -THR))
            truth2 = float(np.mean(worst_dd(K * truth_paths) < -THR))
            samples = simulate(kind, S, N, mu, rng)
            idx = boot_idx(N, weeks, PATHS, BLOCK, rng)
            est_hist, est_true, diff_sign = [], [], []
            for x in samples:
                est_hist.append(np.mean(worst_dd(x[idx]) < -THR))
                c = x - x.mean() + mu
                e1 = np.mean(worst_dd(c[idx]) < -THR)
                est_true.append(e1)
                diff_sign.append(e1 - np.mean(worst_dd(K * c[idx]) < -THR))
            est_hist, est_true, diff_sign = map(np.array, (est_hist, est_true, diff_sign))
            q = lambda z: f"médiane {np.median(z):.3f}, de {np.quantile(z, .05):.3f} à {np.quantile(z, .95):.3f}"  # noqa: E731
            print(f"   {mu_label} | {name:20s} | horizon {weeks:3d} sem. | vraie part {truth:.3f}"
                  f" | moyenne de l'échantillon : {q(est_hist)}, à moins de 10 points {np.mean(np.abs(est_hist - truth) <= .10):.2f}"
                  f" | moyenne imposée : {q(est_true)}, à moins de 10 points {np.mean(np.abs(est_true - truth) <= .10):.2f}"
                  f" | écart avec le portefeuille moins volatil : vrai {truth - truth2:+.3f}, signe correct {np.mean(diff_sign > 0):.2f}")
