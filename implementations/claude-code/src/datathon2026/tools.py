"""Outils déterministes. Chaque outil inscrit ses résultats au registre et renvoie un résumé
compact (identifiants et valeurs affichées) utilisable par le workflow fixe comme par l'agent."""

from __future__ import annotations

import hashlib
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import analytics as a
from . import data
from .evidence import Registry
from .paths import CONFIG_DIR, STARTER_DIR

ORIGIN = "datathon2026.tools"


def load_scenarios(path: Path | None = None) -> dict:
    with open(path or CONFIG_DIR / "scenarios.toml", "rb") as f:
        return tomllib.load(f)


@dataclass
class Session:
    """État d'une exécution : marché, registre, trace des appels d'outils."""

    conv: a.Conventions = field(default_factory=a.Conventions)
    registry: Registry = field(default_factory=Registry)
    trace: list[dict] = field(default_factory=list)
    groups: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self):
        self.market = a.Market(self.conv)
        if not self.groups:
            self.groups = load_scenarios()["groupes"]
        self._group_of = {t: g for g, ts in self.groups.items() for t in ts}

    def group_of(self, ticker: str) -> str:
        return self._group_of.get(ticker, "Non classé")

    def call(self, tool: str, fn, /, **kwargs) -> dict:
        t0 = time.perf_counter()
        n0 = len(self.registry.records)
        out = fn(self, **kwargs)
        new_ids = list(self.registry.records)[n0:]
        self.trace.append(
            {"outil": tool, "arguments": kwargs, "enregistrements": new_ids, "duree_ms": round((time.perf_counter() - t0) * 1000, 1)}
        )
        return out


def _summary(registry: Registry, ids: dict[str, str]) -> dict:
    return {k: {"id": rid, "valeur": registry[rid].display()} for k, rid in ids.items()}


def _date(ts) -> str | None:
    return None if ts is None else ts.date().isoformat()


def _weights(weights: dict[str, float]) -> dict[str, float]:
    """Poids reçus d'un appelant (agent compris) : somme proche de 1, ramenée exactement à 1."""
    total = sum(weights.values()) if weights else 0.0
    if not weights or min(weights.values()) < 0 or abs(total - 1) > 5e-3:
        raise ValueError(f"poids positifs dont la somme vaut 1 attendus (somme reçue : {total:.4f})")
    return {t: w / total for t, w in weights.items()}


# ---------------------------------------------------------------- outils


def data_manifest(s: Session) -> dict:
    """Provenance et limites des données : empreintes SHA-256, fraîcheur du change, durée de l'échantillon, biais de l'univers."""
    ids = {}
    for name in ("prices_daily.csv", "fx_usdcad_daily.csv", "assets_universe.csv"):
        digest = hashlib.sha256((STARTER_DIR / name).read_bytes()).hexdigest()
        r = s.registry.add("D", f"Fichier {name}", digest[:16], "text", "source", "jeu de départ AlphaForge (PolyFinances)",
                           inputs={"sha256": digest})
        ids[name] = r.id
    r = s.registry.add("D", "Âge maximal du taux de change utilisé (jours)", s.market.fx_age_max, "days", "mesuré", ORIGIN,
                       conventions=["dernier taux Banque du Canada connu à la date de valorisation"])
    ids["fx_age_max"] = r.id
    days = s.market.daily.index
    per = (days[0].date().isoformat(), days[-1].date().isoformat())
    ids["duree_echantillon"] = s.registry.add("D", "Durée de l'échantillon de prix", (days[-1] - days[0]).days / 365.25, "years", "mesuré",
                                              ORIGIN, period=per).id
    ids["biais_univers"] = s.registry.add("D", "Limite connue de l'univers d'actifs",
                                          "univers constitué après coup, parmi des titres importants à la date d'extraction (biais du survivant)",
                                          "text", "source", "data/README.md (jeu de départ PolyFinances)").id
    return _summary(s.registry, ids)


def profile_facts(s: Session, persona: str, scenario: dict | None = None) -> dict:
    """Faits de profil : déclarés dans l'énoncé, hypothèses de démonstration, inconnus."""
    p = data.load_personas()[persona]
    reg, ids = s.registry, {}
    src = {"amira": "énoncé, p. 5", "mateo": "énoncé, p. 6", "robert": "énoncé, p. 7"}[persona]
    h = p["horizon_ans"]
    horizon = f"{h['min']} à {h['max']} ans" if "max" in h else f"{h['min']} ans ou plus"
    for key, label, value, unit in [
        ("nom", "Prénom (profil fictif)", p["nom"], "text"),
        ("age", "Âge", p["age"], "count"),
        ("profil_risque", "Profil de risque déclaré", p["profil_risque"], "text"),
        ("horizon", "Horizon de placement", horizon, "text"),
        ("objectif", "Objectif", p["objectif"], "text"),
        ("experience", "Expérience en placement", p["experience"], "text"),
    ]:
        ids[key] = reg.add("P", label, value, unit, "déclaré", src, subject=p["nom"]).id
    ids["horizon_min"] = reg.add("P", "Horizon minimal", h["min"], "years", "déclaré", src, subject=p["nom"]).id
    for i, pref in enumerate(p["preferences"], 1):
        ids[f"preference_{i}"] = reg.add("P", "Préférence déclarée", pref, "text", "déclaré", src, subject=p["nom"]).id
    for key, label in [
        ("capacite_perte", "Capacité de perte (perte supportable sans compromettre les projets)"),
        ("liquidite", "Besoins de liquidité et retraits prévus"),
        ("patrimoine", "Patrimoine total et part concernée"),
    ]:
        ids[key] = reg.add("P", label, None, "text", "inconnu", "non fourni par l'énoncé", subject=p["nom"]).id
    if scenario:
        ids["demande"] = reg.add("P", "Demande formulée", scenario["demande"], "text", "scénario", "scénario de démonstration",
                                 subject=p["nom"]).id
        ids["origine"] = reg.add("P", "Origine de la demande", scenario["origine_demande"], "text", "scénario",
                                 "scénario de démonstration", subject=p["nom"]).id
    return _summary(reg, ids)


def asset_metrics(s: Session, ticker: str, horizon_years: float = 3) -> dict:
    """Description historique d'un actif : rendement, volatilité, pire baisse et sa durée, 2022, pire fenêtre."""
    m, reg, c = s.market, s.registry, s.conv
    m.check_tickers([ticker])
    v = m.daily[ticker].dropna()
    per = (v.index[0].date().isoformat(), v.index[-1].date().isoformat())
    conv = c.notes()
    name = m.universe.loc[ticker, "name"]
    ids = {}
    ids["cagr"] = reg.add("R", f"Rendement annualisé {ticker}", a.cagr(v), "pct", "mesuré", ORIGIN, subject=ticker,
                          period=per, conventions=conv, inputs={"nom": name}).id
    ids["vol"] = reg.add("R", f"Volatilité annualisée {ticker}", a.annual_vol(m.weekly_returns[ticker]), "pct", "mesuré", ORIGIN,
                         subject=ticker, period=per, conventions=conv).id
    dd = a.max_drawdown(v)
    ids["perte_max"] = reg.add("R", f"Pire baisse depuis un sommet {ticker}", dd.depth, "pct", "mesuré", ORIGIN, subject=ticker,
                               period=per, conventions=conv + ["série quotidienne de l'actif"]).id
    ids["sommet"] = reg.add("R", f"Date du sommet précédant la pire baisse {ticker}", _date(dd.peak), "date", "mesuré", ORIGIN, subject=ticker).id
    ids["creux"] = reg.add("R", f"Date du creux {ticker}", _date(dd.trough), "date", "mesuré", ORIGIN, subject=ticker).id
    ids["retour_sommet"] = reg.add("R", f"Date de retour au sommet {ticker}", _date(dd.recovery) or "pas encore retrouvé à la fin de l'échantillon",
                                   "date", "mesuré", ORIGIN, subject=ticker).id
    ids["duree_sous_sommet"] = reg.add("R", f"Durée sous le sommet {ticker}", dd.days_underwater(v.index[-1]) / 365.25, "years", "mesuré",
                                       ORIGIN, subject=ticker, period=per).id
    r22 = a.period_return(v, "2021-12-31", "2022-12-31")
    ids["rendement_2022"] = reg.add("R", f"Rendement 2022 {ticker}", r22, "pct", "mesuré", ORIGIN, subject=ticker,
                                    period=("2021-12-31", "2022-12-31"), conventions=conv).id
    w = a.worst_window(v, horizon_years)
    ids["pire_fenetre"] = reg.add("R", f"Pire rendement sur une fenêtre de {horizon_years:g} ans {ticker}", w.worst, "pct", "mesuré", ORIGIN,
                                  subject=ticker, period=per, conventions=conv,
                                  inputs={"debut_pire_fenetre": _date(w.worst_start), "fenetres_glissantes": w.n_starts}).id
    ids["fenetres_independantes"] = reg.add("R", f"Fenêtres de {horizon_years:g} ans sans chevauchement dans l'échantillon", w.n_independent,
                                            "count", "mesuré", ORIGIN, subject=ticker, period=per).id
    return _summary(reg, ids)


def portfolio_metrics(s: Session, name: str, weights: dict[str, float], horizon_years: float = 3) -> dict:
    """Portefeuille fictif rééquilibré chaque semaine : volatilité, pire baisse, 2022, contributions au risque, groupes."""
    m, reg, c = s.market, s.registry, s.conv
    weights = _weights(weights)
    p = a.portfolio(m, weights)
    per = (p.index.index[0].date().isoformat(), p.index.index[-1].date().isoformat())
    conv = c.notes() + ["Portefeuille fictif rééquilibré chaque semaine aux poids indiqués (hypothèse)"]
    ids = {}
    ids["poids"] = reg.add("R", f"Composition {name}", ", ".join(f"{t} {w * 100:.0f} %" for t, w in weights.items()), "text", "hypothèse",
                           "scénario de démonstration", subject=name).id
    ids["cagr"] = reg.add("R", f"Rendement annualisé {name}", a.cagr(p.index), "pct", "mesuré", ORIGIN, subject=name, period=per,
                          conventions=conv).id
    ids["vol"] = reg.add("R", f"Volatilité annualisée {name}", a.annual_vol(p.weekly), "pct", "mesuré", ORIGIN, subject=name, period=per,
                         conventions=conv).id
    dd = a.max_drawdown(p.index)
    ids["perte_max"] = reg.add("R", f"Pire baisse depuis un sommet {name}", dd.depth, "pct", "mesuré", ORIGIN, subject=name, period=per,
                               conventions=conv + ["série hebdomadaire : les creux en cours de semaine ne sont pas vus"]).id
    ids["rendement_2022"] = reg.add("R", f"Rendement 2022 {name}", a.period_return(p.index, "2021-12-31", "2022-12-31"), "pct", "mesuré",
                                    ORIGIN, subject=name, period=("2021-12-31", "2022-12-31"), conventions=conv).id
    w = a.worst_window(p.index, horizon_years)
    ids["pire_fenetre"] = reg.add("R", f"Pire rendement sur une fenêtre de {horizon_years:g} ans {name}", w.worst, "pct", "mesuré", ORIGIN,
                                  subject=name, period=per, conventions=conv).id
    for t, rc in sorted(p.risk_contrib.items(), key=lambda kv: -kv[1]):
        ids[f"poids_{t}"] = reg.add("R", f"Poids de {t} dans {name}", weights[t], "pct", "hypothèse", "scénario de démonstration",
                                    subject=name).id
        ids[f"risque_{t}"] = reg.add("R", f"Part du risque (variance) due à {t} dans {name}", rc, "pct", "mesuré", ORIGIN, subject=name,
                                     period=per, conventions=conv + ["covariance échantillon des rendements hebdomadaires"]).id
    top3 = sum(sorted(p.risk_contrib.values(), reverse=True)[:3])
    ids["risque_top3"] = reg.add("R", f"Part du risque des trois premières lignes de {name}", top3, "pct", "mesuré", ORIGIN, subject=name,
                                 period=per, conventions=conv).id
    gw, gr = {}, {}
    for t in weights:
        g = s.group_of(t)
        gw[g] = gw.get(g, 0.0) + weights[t]
        gr[g] = gr.get(g, 0.0) + p.risk_contrib[t]
    for g in sorted(gr, key=lambda g: -gr[g]):
        ids[f"groupe_poids_{g}"] = reg.add("R", f"Poids du groupe {g} dans {name}", gw[g], "pct", "hypothèse", "scénario de démonstration",
                                           subject=name).id
        ids[f"groupe_risque_{g}"] = reg.add("R", f"Part du risque du groupe {g} dans {name}", gr[g], "pct", "mesuré", ORIGIN, subject=name,
                                            period=per, conventions=conv + ["regroupement : config/scenarios.toml"]).id
    for k, rid_ in ids.items():  # tout calcul sur ce portefeuille dépend de sa composition fictive
        if k != "poids" and reg[rid_].status == "mesuré":
            reg[rid_].inputs.setdefault("depend_de", []).append(ids["poids"])
    out = _summary(reg, ids)
    out["_brut"] = {"risk_contrib": p.risk_contrib, "groupes_risque": gr, "groupes_poids": gw, "perte_max": dd.depth}
    return out


def share_sweep(s: Session, name: str, base: dict[str, float], ticker: str, loss_threshold: float, max_share: float = 0.30) -> dict:
    """Part maximale de `ticker` ajoutable à `base` sans que la pire baisse historique du portefeuille dépasse le seuil."""
    m, reg = s.market, s.registry
    if not -1 < loss_threshold < 0:
        raise ValueError("seuil_perte attendu entre -1 et 0 (ex. -0.15 pour une baisse de 15 %)")
    base = _weights(base)
    grid = np.round(np.arange(0, max_share + 1e-9, 0.01), 2)
    depths = {float(x): a.max_drawdown(a.portfolio(m, a.blend(base, ticker, float(x))).index).depth for x in grid}
    ok = [x for x, d in depths.items() if d >= loss_threshold]
    flip = max(ok) if ok else None
    ids = {
        "seuil": reg.add("R", "Seuil de perte retenu", loss_threshold, "pct", "hypothèse", "scénario de démonstration",
                         subject=name).id,
        "part_max": reg.add("R", f"Part maximale de {ticker} compatible avec le seuil (pire baisse historique)", flip, "pct", "mesuré",
                            ORIGIN, subject=name, conventions=[f"grille de 0 à {max_share:.0%} par pas de 1 point", "pire baisse hebdomadaire 2021-2026"],
                            inputs={"profondeurs": depths}).id,
    }
    reg[ids["part_max"]].inputs["depend_de"] = [ids["seuil"]]
    out = _summary(reg, ids)
    out["_brut"] = {"profondeurs": depths, "part_max": flip}
    return out


def diversification_sweep(s: Session, name: str, base: dict[str, float], sleeve: dict[str, float], cap: float) -> dict:
    """Plus petite part α à déplacer de `base` vers le panier `sleeve` pour qu'aucun groupe ne
    dépasse `cap` de la part du risque : w(α) = (1 − α)·base + α·sleeve, α par pas de 5 points."""
    m, reg = s.market, s.registry
    if not 0 < cap <= 1:
        raise ValueError("plafond attendu entre 0 et 1 (ex. 0.5 pour 50 % du risque)")
    base = _weights(base)
    tot = sum(sleeve.values())
    if tot <= 0 or min(sleeve.values()) < 0:
        raise ValueError("panier attendu : poids positifs")
    sleeve = {t: w / tot for t, w in sleeve.items()}

    def mix(alpha: float) -> dict[str, float]:
        out = {t: (1 - alpha) * w for t, w in base.items()}
        for t, w in sleeve.items():
            out[t] = out.get(t, 0.0) + alpha * w
        return {t: w for t, w in out.items() if w > 1e-12}

    path = {}
    for alpha in np.round(np.arange(0, 1 + 1e-9, 0.05), 2):
        p = a.portfolio(m, mix(float(alpha)))
        groups: dict[str, float] = {}
        for t, rc in p.risk_contrib.items():
            g = s.group_of(t)
            groups[g] = groups.get(g, 0.0) + rc
        path[float(alpha)] = max(groups.values())
    feasible = [x for x, g in path.items() if g <= cap]
    alpha = min(feasible) if feasible else None
    ids = {
        "panier": reg.add("R", f"Panier de diversification de {name}", ", ".join(f"{t} {w * 100:.0f} %" for t, w in sleeve.items()), "text",
                          "hypothèse", "scénario de démonstration", subject=name).id,
        "part_deplacee": reg.add("R", f"Part minimale à déplacer vers le panier pour respecter le plafond ({name})", alpha, "pct", "mesuré",
                                 ORIGIN, subject=name, conventions=["grille par pas de 5 points", "part du risque par groupe, covariance hebdomadaire"],
                                 inputs={"part_max_groupe_selon_alpha": path}).id,
        "plafond": reg.add("R", f"Plafond de part du risque par groupe ({name})", cap, "pct", "hypothèse", "scénario de démonstration",
                           subject=name).id,
    }
    reg[ids["part_deplacee"]].inputs["depend_de"] = [ids["panier"], ids["plafond"]]
    out = _summary(reg, ids)
    out["_brut"] = {"alpha": alpha, "poids": mix(alpha) if alpha is not None else None, "chemin": path}
    return out


def correlation(s: Session, t1: str, t2: str) -> dict:
    m, reg = s.market, s.registry
    R = m.weekly_returns[[t1, t2]].dropna()
    rho = float(R[t1].corr(R[t2]))
    per = (R.index[0].date().isoformat(), R.index[-1].date().isoformat())
    rid = reg.add("R", f"Corrélation hebdomadaire {t1} / {t2}", rho, "ratio", "mesuré", ORIGIN, subject=f"{t1}, {t2}", period=per,
                  conventions=s.conv.notes()).id
    return _summary(reg, {"correlation": rid})
