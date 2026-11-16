"""Expériences discriminantes sur les méthodes de l'agent 2 (15 novembre 2026). Hors produit :
lit les données par la bibliothèque du projet, n'écrit rien, n'appelle aucun service. Graine fixe.

    uv run --with arch --with scikit-learn python research/experiences/methodes_analyse.py

Cas : portefeuille fictif de Robert (config/scenarios.toml), ajout de Tesla ou de QQQ ; univers de 31 actifs.

Critères écrits AVANT l'exécution (une expérience qui ne peut pas échouer n'en est pas une) :

X1  Longueur de bloc. Si, entre la longueur estimée automatiquement (Politis-White 2004, correction
    Patton-Politis-White 2009, sur les rendements et sur leurs carrés) et 13 semaines (choix manuel du
    calcul exploratoire), la part des trajectoires de 3 ans franchissant 15 % bouge de plus de 5 points
    pour une option, la longueur de bloc est une hypothèse à afficher et le résultat se donne en fourchette.
X2  Annualisation du notebook d'introduction. Si « (1 + moyenne quotidienne) ^ jours - 1 » s'écarte du
    rendement composé réalisé de plus de 2 points par an pour au moins un actif, cette formule est
    écartée de toute restitution. Si la corrélation « quotidienne, devise de cotation » s'écarte de la
    corrélation « hebdomadaire, dollars canadiens » de plus de 0,10 pour au moins une paire sur dix, la
    convention de corrélation doit être déclarée dans le dossier.
X3  Moyenne contre variance. Si l'intervalle à 90 % de l'écart de rendement moyen entre Tesla et le
    portefeuille actuel contient zéro, aucun écart de rendement historique ne peut fonder une conclusion.
    Si passer de l'hebdomadaire au quotidien réduit l'erreur type de la volatilité d'au moins un tiers
    sans réduire celle de la moyenne, la règle « risque estimable, rendement non » est confirmée ici.
X4  Niveaux contre écarts appariés. Si l'intervalle à 90 % de l'écart apparié (10 % Tesla moins actuel)
    exclut zéro alors que les intervalles de niveau se chevauchent, l'agent 2 compare les options par
    écarts appariés sur les mêmes trajectoires, pas par niveaux.
X5  Contraction de la covariance. Si, pour des portefeuilles à poids fixés par la demande, la volatilité
    prévue change de moins de 0,3 point et les parts de risque de moins de 2 points entre covariance
    d'échantillon et Ledoit-Wolf, la contraction est inutile pour comparer des options données ; si, hors
    échantillon, le portefeuille de variance minimale construit sur la covariance d'échantillon est plus
    volatil que celui de Ledoit-Wolf, la contraction est obligatoire dès qu'un agent optimise des poids.
X6  Le rééchantillonnage vaut-il prévision ? Fenêtre croissante : à chaque date, scénarios d'un an tirés
    du seul passé, comparés à l'année réellement suivie. Si la part des années réalisées tombant dans la
    bande 5 %-95 % des scénarios sort de l'intervalle [80 %, 97 %], le produit ne peut pas présenter ces
    parts comme des probabilités, seulement comme des scénarios construits sur le passé.
"""

import numpy as np
import pandas as pd
from arch.bootstrap import optimal_block_length
from sklearn.covariance import LedoitWolf

from datathon2026 import analytics as a
from datathon2026 import data
from datathon2026 import tools as T

SEED = 2026
m = T.Session().market
sc = T.load_scenarios()
base = sc["robert"]["portefeuille_actuel"]
tick = ["XBB.TO", "ZST.TO", "XIU.TO", "SPY", "TSLA", "QQQ"]
R = m.weekly_returns[tick]
X, N = R.to_numpy(), len(R)
options = {"actuel": None, "10 % TSLA": ("TSLA", .10), "10 % QQQ": ("QQQ", .10)}
W = {k: np.array([(base if v is None else a.blend(base, *v)).get(t, 0.0) for t in tick]) for k, v in options.items()}


def boot_idx(n_obs, weeks, n, block, seed):
    """Indices d'un rééchantillonnage stationnaire (blocs géométriques de moyenne `block`, échantillon circulaire)."""
    rng = np.random.default_rng(seed)
    idx = np.empty((n, weeks), dtype=np.int64)
    idx[:, 0] = rng.integers(0, n_obs, n)
    new, starts = rng.random((n, weeks)) < 1.0 / block, rng.integers(0, n_obs, (n, weeks))
    for t in range(1, weeks):
        idx[:, t] = np.where(new[:, t], starts[:, t], (idx[:, t - 1] + 1) % n_obs)
    return idx


def worst_dd(paths):
    v = np.cumprod(1 + paths, axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.ones((len(v), 1)), v], axis=1), axis=1)[:, 1:]
    return (v / peak - 1).min(axis=1)


def auto_block(s):
    o = optimal_block_length(np.asarray(s, dtype=float))
    return float(o["stationary"].iloc[0])


print(f"Échantillon : {N} semaines, du {R.index[0].date()} au {R.index[-1].date()}")

# ---------------------------------------------------------------- X1
print("\nX1. Longueur de bloc estimée (rééchantillonnage stationnaire), en semaines")
blocks_auto = {}
for k, w in W.items():
    r = X @ w
    c = r - r.mean()
    blocks_auto[k] = (auto_block(r), auto_block(np.abs(c)), auto_block(c ** 2))
    print(f"   {k:10s} rendements {blocks_auto[k][0]:5.1f} | valeurs absolues {blocks_auto[k][1]:5.1f} | carrés {blocks_auto[k][2]:5.1f}")
per_asset = {t: (auto_block(R[t]), auto_block((R[t] - R[t].mean()) ** 2)) for t in tick}
print("   par actif (rendements, carrés) :", {t: (round(u, 1), round(v, 1)) for t, (u, v) in per_asset.items()})
b_ret = max(v[0] for v in blocks_auto.values())
b_sq = max(v[2] for v in blocks_auto.values())
print(f"   retenus pour la comparaison : {b_ret:.1f} (rendements) et {b_sq:.1f} (carrés), contre 13 (choix manuel)")

centered = X - X.mean(axis=0)
for name, Xm in (("moyennes historiques", X), ("aucun rendement moyen crédité", centered)):
    print(f"   Part des trajectoires de 3 ans dont la pire baisse franchit 15 % | finissant sous le départ — {name}")
    for block in sorted({1.0, 2.0, 4.0, 8.0, 13.0, 26.0, 52.0, round(b_ret, 1), round(b_sq, 1)}):
        idx = boot_idx(N, 156, 10_000, max(block, 1.0), SEED)
        row = []
        for k, w in W.items():
            p = (Xm @ w)[idx]
            row.append(f"{k} {np.mean(worst_dd(p) < -0.15):.3f} | {np.mean(np.prod(1 + p, axis=1) < 1):.3f}")
        print(f"      bloc {block:5.1f} : " + " ; ".join(row))

# ---------------------------------------------------------------- X2
print("\nX2. Formule d'annualisation du notebook contre rendement composé réalisé (devise de cotation, quotidien)")
px = data.adj_close_wide(data.load_prices())
rows = []
for t in px.columns:
    s = px[t].dropna()
    r = s.pct_change().dropna()
    k = 365 if t.endswith("-USD") else 252
    years = (s.index[-1] - s.index[0]).days / 365.25
    rows.append((t, (1 + r.mean()) ** k - 1, (s.iloc[-1] / s.iloc[0]) ** (1 / years) - 1, r.std() * np.sqrt(k)))
ann = pd.DataFrame(rows, columns=["actif", "notebook", "compose", "vol"]).set_index("actif")
ann["ecart"] = ann["notebook"] - ann["compose"]
ann["demi_variance"] = ann["vol"] ** 2 / 2
print(ann.sort_values("ecart", ascending=False).head(8).round(3).to_string())
print(f"   actifs dont l'écart dépasse 2 points : {(ann['ecart'].abs() > 0.02).sum()} sur {len(ann)} ; écart médian {ann['ecart'].median():+.3f} ; maximal {ann['ecart'].max():+.3f}")
rank_nb = (ann["notebook"] / ann["vol"]).rank(ascending=False)
rank_co = (ann["compose"] / ann["vol"]).rank(ascending=False)
print(f"   classement « rendement / risque » : {int((rank_nb != rank_co).sum())} actifs changent de rang ; plus grand saut {int((rank_nb - rank_co).abs().max())} rangs")

nb_ret = px.apply(lambda s: s.dropna().pct_change())
c_nb, c_w = nb_ret.corr(), m.weekly_returns.corr()
iu = np.triu_indices(len(px.columns), 1)
gap = (c_nb.loc[px.columns, px.columns].to_numpy() - c_w.loc[px.columns, px.columns].to_numpy())[iu]
print(f"   corrélations : {len(gap)} paires ; écart absolu médian {np.median(np.abs(gap)):.3f} ; part des paires au-delà de 0,10 : {np.mean(np.abs(gap) > 0.10):.3f} ; au-delà de 0,20 : {np.mean(np.abs(gap) > 0.20):.3f}")
for u, v in (("XIU.TO", "XBB.TO"), ("SPY", "XIU.TO"), ("BTC-USD", "SPY"), ("TSLA", "SPY"), ("GLD", "XIU.TO"), ("SPY", "XBB.TO"), ("SPY", "AGG")):
    print(f"      {u:8s} {v:7s} notebook {c_nb.loc[u, v]:+.2f} | hebdomadaire en CAD {c_w.loc[u, v]:+.2f}")

# ---------------------------------------------------------------- X3
print("\nX3. Moyenne contre variance (erreurs types par rééchantillonnage stationnaire, 5 000 tirages)")
biz = m.daily[m.daily.index.day_of_week < 5]  # rendements calculés après retrait des jours fériés (sinon le rendement du lendemain est perdu)
for t in ("TSLA", "SPY", "XIU.TO", "XBB.TO"):
    out = []
    for label, r, k in (("hebdo", m.weekly_returns[t].to_numpy(), 52), ("quotidien", biz[t].dropna().pct_change().dropna().to_numpy(), 252)):
        n = len(r)
        b = max(auto_block((r - r.mean()) ** 2), 1.0)
        samp = r[boot_idx(n, n, 5_000, b, SEED)]
        mu, vol = samp.mean(axis=1) * k, samp.std(axis=1, ddof=1) * np.sqrt(k)
        out.append(f"{label} (n={n}) : moyenne {r.mean() * k:+.3f} ± {mu.std():.3f} ; volatilité {r.std(ddof=1) * np.sqrt(k):.3f} ± {vol.std():.3f}")
    print(f"   {t:7s} " + " | ".join(out))
r_p, r_t = X @ W["actuel"], X[:, tick.index("TSLA")]
d = r_t - r_p
idx = boot_idx(N, N, 5_000, max(auto_block(d), 1.0), SEED)
diff = d[idx].mean(axis=1) * 52
print(f"   écart de rendement moyen annuel Tesla moins portefeuille actuel : {d.mean() * 52:+.3f} ; intervalle à 90 % de {np.quantile(diff, .05):+.3f} à {np.quantile(diff, .95):+.3f}")
sd_ann = d.std(ddof=1) * np.sqrt(52)
print(f"   années d'historique pour distinguer une prime de 5 points par an à deux erreurs types : {(2 * sd_ann / 0.05) ** 2:.0f} (écart type de l'écart : {sd_ann:.3f})")

# ---------------------------------------------------------------- X4
print("\nX4. Niveaux contre écarts appariés (5 000 rééchantillons de l'historique, mêmes semaines pour les deux options)")
idx = boot_idx(N, N, 5_000, max(b_sq, 1.0), SEED)
stats = {}
for k in ("actuel", "10 % TSLA"):
    p = (X @ W[k])[idx]
    tail = np.sort(p, axis=1)[:, : max(1, int(round(0.05 * N)))]
    stats[k] = {"perte moyenne des 5 % pires semaines": tail.mean(axis=1), "volatilité annualisée": p.std(axis=1, ddof=1) * np.sqrt(52), "pire baisse sur 5 ans": worst_dd(p)}
for s in stats["actuel"]:
    u, v = stats["actuel"][s], stats["10 % TSLA"][s]
    dlt = v - u
    q = lambda z: f"de {np.quantile(z, .05):+.4f} à {np.quantile(z, .95):+.4f}"  # noqa: E731
    print(f"   {s} : actuel {q(u)} ; 10 % TSLA {q(v)} ; écart apparié {q(dlt)} ; part des tirages où 10 % TSLA est plus défavorable : {np.mean(np.abs(v) > np.abs(u)):.3f}")

# ---------------------------------------------------------------- X5
print("\nX5. Contraction de la covariance (31 actifs, 261 semaines)")
Rw = m.weekly_returns
S = np.cov(Rw.to_numpy(), rowvar=False)
lw = LedoitWolf().fit(Rw.to_numpy())
print(f"   intensité de contraction de Ledoit-Wolf : {lw.shrinkage_:.3f} ; conditionnement : échantillon {np.linalg.cond(S):.0f}, contracté {np.linalg.cond(lw.covariance_):.0f}")
cols = list(Rw.columns)
ports = {"Robert actuel": base, "Robert 10 % TSLA": a.blend(base, "TSLA", .10), "Amira proposé": sc["amira"]["portefeuille_propose"]}
for name, wd in ports.items():
    w = np.array([wd.get(c, 0.0) for c in cols])
    res = []
    for C in (S, lw.covariance_):
        var = w @ C @ w
        res.append((np.sqrt(var * 52), w * (C @ w) / var))
    print(f"   {name:17s} volatilité prévue : échantillon {res[0][0]:.4f}, contractée {res[1][0]:.4f} ; plus grand déplacement d'une part de risque : {np.abs(res[0][1] - res[1][1]).max():.4f}")
ones = np.ones(len(cols))
real = {"échantillon": [], "Ledoit-Wolf": [], "poids égaux": []}
for start in range(104, N - 25, 26):
    tr, te = Rw.to_numpy()[start - 104:start], Rw.to_numpy()[start:start + 26]
    for label, C in (("échantillon", np.cov(tr, rowvar=False)), ("Ledoit-Wolf", LedoitWolf().fit(tr).covariance_)):
        w = np.linalg.solve(C, ones)
        w /= w.sum()
        real[label].append((te @ w).std(ddof=1) * np.sqrt(52))
    real["poids égaux"].append((te @ (ones / len(cols))).std(ddof=1) * np.sqrt(52))
print(f"   variance minimale sans contrainte, 104 semaines d'estimation puis 26 semaines réalisées, {len(real['échantillon'])} fenêtres : volatilité réalisée moyenne "
      + " ; ".join(f"{k} {np.mean(v):.4f}" for k, v in real.items()))
print("   fenêtres où l'échantillon fait pire que Ledoit-Wolf :", int(np.sum(np.array(real["échantillon"]) > np.array(real["Ledoit-Wolf"]))), "sur", len(real["échantillon"]))

# ---------------------------------------------------------------- X6
print("\nX6. Le rééchantillonnage vaut-il prévision ? Fenêtre croissante, horizon d'un an, 2 000 scénarios par date")
for min_train in (104, 156):
    for k in ("actuel", "10 % TSLA"):
        r = X @ W[k]
        pit_dd, pit_fin = [], []
        for t in range(min_train, N - 52 + 1):
            train = r[:t]
            sims = train[boot_idx(t, 52, 2_000, 13, SEED + t)]
            real_path = r[t:t + 52][None, :]
            pit_dd.append(np.mean(worst_dd(sims) <= worst_dd(real_path)[0]))
            pit_fin.append(np.mean(np.prod(1 + sims, axis=1) <= np.prod(1 + real_path)))
        pit_dd, pit_fin = np.array(pit_dd), np.array(pit_fin)
        inside = lambda z: np.mean((z >= .05) & (z <= .95))  # noqa: E731
        print(f"   passé d'au moins {min_train} semaines, {k:10s} : {len(pit_dd)} dates de départ (environ {len(pit_dd) / 52 + 1:.0f} années sans chevauchement)"
              f" | pire baisse : dans la bande 5-95 % {inside(pit_dd):.2f}, plus grave que 95 % des scénarios {np.mean(pit_dd < .05):.2f}, plus douce que 95 % {np.mean(pit_dd > .95):.2f}, rang médian {np.median(pit_dd):.2f}"
              f" | valeur finale : dans la bande {inside(pit_fin):.2f}, rang médian {np.median(pit_fin):.2f}")

# ================================================================ Ajouts APRÈS lecture des premiers résultats
# (vérifications de robustesse décidées en voyant X3, X4 et X5 : elles n'ont pas de critère écrit d'avance)

print("\nX3 bis. Même comparaison avec un bloc commun en temps calendaire (13 semaines ; 63 jours ouvrables)")
for t in ("TSLA", "SPY", "XIU.TO", "XBB.TO"):
    out = []
    for label, r, k, b in (("hebdo", m.weekly_returns[t].to_numpy(), 52, 13), ("quotidien", biz[t].dropna().pct_change().dropna().to_numpy(), 252, 63)):
        samp = r[boot_idx(len(r), len(r), 5_000, b, SEED)]
        out.append(f"{label} : moyenne ± {(samp.mean(axis=1) * k).std():.3f} ; volatilité ± {(samp.std(axis=1, ddof=1) * np.sqrt(k)).std():.3f}")
    print(f"   {t:7s} " + " | ".join(out))

print("\nX4 bis. La « part maximale de Tesla sous le seuil de 15 % » est-elle déterminée par cinq ans d'historique ?")
shares = np.arange(0, 31) / 100
Wg = np.array([[a.blend(base, "TSLA", s).get(t, 0.0) if s else base.get(t, 0.0) for t in tick] for s in shares])
hist = np.array([worst_dd((X @ w)[None, :])[0] for w in Wg])
print(f"   sur l'historique observé : part maximale {shares[hist >= -0.15].max():.2f} (pire baisse à 10 % : {hist[10]:+.3f})")
for block in (1.5, 13.0):
    idx = boot_idx(N, N, 2_000, block, SEED)
    dd = np.stack([worst_dd((X @ w)[idx]) for w in Wg], axis=1)  # tirages x parts
    ok = dd >= -0.15
    pmax = np.where(ok.any(axis=1), (ok * shares).max(axis=1), -0.01)
    q = np.quantile(pmax, [.05, .25, .5, .75, .95])
    print(f"   bloc {block:4.1f} : part maximale sur 2 000 histoires rééchantillonnées — 5 % {q[0]:.2f}, quart {q[1]:.2f}, médiane {q[2]:.2f}, trois quarts {q[3]:.2f}, 95 % {q[4]:.2f}"
          f" ; aucune part admissible : {np.mean(pmax < 0):.3f} ; plafond de la grille (30 %) atteint : {np.mean(pmax >= 0.30):.3f}")

print("\nX5 bis. Contraction de la matrice de corrélation (variances d'échantillon conservées), et test sur les seules actions")
sd = Rw.std(ddof=1).to_numpy()
lwc = LedoitWolf().fit(Rw.to_numpy() / sd)
C_corr = lwc.covariance_ * np.outer(sd, sd)
print(f"   intensité sur données réduites : {lwc.shrinkage_:.3f}")
for name, wd in ports.items():
    w = np.array([wd.get(c, 0.0) for c in cols])
    v0, v1 = w @ S @ w, w @ C_corr @ w
    print(f"   {name:17s} volatilité prévue : échantillon {np.sqrt(v0 * 52):.4f}, corrélation contractée {np.sqrt(v1 * 52):.4f} ; plus grand déplacement d'une part de risque : {np.abs(w * (S @ w) / v0 - w * (C_corr @ w) / v1).max():.4f}")
stocks = [c for c in cols if c in set(sum((sc["groupes"][g] for g in ("Technologie", "Consommation discrétionnaire", "Autres actions")), [])) and c != "QQQ"]
E = Rw[stocks].to_numpy()
one = np.ones(len(stocks))
res = {"échantillon": [], "Ledoit-Wolf": [], "corrélation contractée": [], "poids égaux": []}
for est in (52, 104):
    for k in res:
        res[k] = []
    for start in range(est, N - 25, 26):
        tr, te = E[start - est:start], E[start:start + 26]
        s_tr = tr.std(axis=0, ddof=1)
        cands = {"échantillon": np.cov(tr, rowvar=False), "Ledoit-Wolf": LedoitWolf().fit(tr).covariance_,
                 "corrélation contractée": LedoitWolf().fit(tr / s_tr).covariance_ * np.outer(s_tr, s_tr)}
        for label, C in cands.items():
            w = np.linalg.solve(C, one)
            w /= w.sum()
            res[label].append((te @ w).std(ddof=1) * np.sqrt(52))
        res["poids égaux"].append((te @ (one / len(stocks))).std(ddof=1) * np.sqrt(52))
    print(f"   {len(stocks)} actions, variance minimale sans contrainte, {est} semaines d'estimation, {len(res['échantillon'])} fenêtres de 26 semaines : volatilité réalisée moyenne "
          + " ; ".join(f"{k} {np.mean(v):.4f}" for k, v in res.items())
          + f" ; fenêtres où l'échantillon fait pire que Ledoit-Wolf : {int(np.sum(np.array(res['échantillon']) > np.array(res['Ledoit-Wolf'])))}")

print("\nX7. Dépendance à une sous-période (reproduction indépendante d'un constat de la recherche sur la confrontation ; ajout sans critère écrit d'avance)")
print("   Part des trajectoires de 3 ans franchissant 15 %, moyennes de l'échantillon restant, bloc de 13 semaines, 10 000 trajectoires")
slices = [("échantillon complet", None)] + [(f"sans l'année {i + 1} ({R.index[s].date()} au {R.index[min(s + 51, N - 1)].date()})", (s, min(s + 52, N))) for i, s in enumerate(range(0, N - 1, 52)) if s + 26 < N]
for label, cut in slices:
    keep = np.ones(N, dtype=bool)
    if cut:
        keep[cut[0]:cut[1]] = False
    Xs = X[keep]
    idx = boot_idx(len(Xs), 156, 10_000, 13, SEED)
    print(f"   {label:55s} ({len(Xs)} semaines) : " + " ; ".join(f"{k} {np.mean(worst_dd((Xs @ w)[idx]) < -0.15):.3f}" for k, w in W.items())
          + f" | pire baisse observée à 10 % TSLA : {worst_dd((Xs @ W['10 % TSLA'])[None, :])[0]:+.3f}")
