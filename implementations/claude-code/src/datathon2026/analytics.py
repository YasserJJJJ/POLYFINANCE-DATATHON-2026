"""Calculs déterministes de description historique (aucune prévision).

Conventions (décision D3, `docs/decisions.md`) :
- valeur quotidienne de chaque actif sur son propre calendrier, en devise de base, à partir de la
  clôture ajustée et du dernier taux Banque du Canada connu à la date (fraîcheur conservée) ;
- comparaisons entre actifs et portefeuilles sur rendements hebdomadaires (dernière observation
  de chaque semaine se terminant le vendredi), ce qui neutralise les jours fériés TSX/US et la
  cotation 7 j/7 des cryptoactifs ;
- volatilité annualisée = écart type hebdomadaire × √52 ;
- portefeuilles fictifs rééquilibrés chaque semaine aux poids indiqués (hypothèse).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import data

WEEKS_PER_YEAR = 52


@dataclass(frozen=True)
class Conventions:
    base_currency: str = "CAD"
    start: str = "2021-11-12"
    end: str = "2026-11-12"
    weekly_anchor: str = "W-FRI"

    def notes(self) -> list[str]:
        return [
            f"Valeurs en {self.base_currency}, converties au dernier taux Banque du Canada connu à la date",
            f"Période d'observation {self.start} → {self.end}",
            "Clôtures ajustées des dividendes et fractionnements (méthode Yahoo Finance)",
            "Rendements hebdomadaires : dernière observation de chaque semaine se terminant le vendredi",
            "Volatilité annualisée : écart type hebdomadaire × √52",
        ]


class Market:
    """Séries de valeur en devise de base, calculées une seule fois pour toute l'exécution."""

    def __init__(self, conv: Conventions = Conventions(), prices: pd.DataFrame | None = None, fx: pd.DataFrame | None = None):
        if conv.base_currency not in {"CAD", "USD"}:
            raise ValueError("devise de base : CAD ou USD")
        self.conv = conv
        prices = data.load_prices() if prices is None else prices
        fx = data.load_fx() if fx is None else fx
        p = prices[(prices["date"] >= conv.start) & (prices["date"] <= conv.end)]
        fxs = fx[["date", "usdcad"]].rename(columns={"date": "fx_date"}).sort_values("fx_date")
        m = pd.merge_asof(p.sort_values("date"), fxs, left_on="date", right_on="fx_date", direction="backward")
        needs_fx = m["currency"] != conv.base_currency
        if conv.base_currency == "CAD":
            factor = np.where(needs_fx, m["usdcad"], 1.0)
        else:
            factor = np.where(needs_fx, 1.0 / m["usdcad"], 1.0)
        m["value"] = m["adj_close"] * factor
        m["fx_age_days"] = np.where(needs_fx, (m["date"] - m["fx_date"]).dt.days, 0)
        if m.loc[needs_fx, "usdcad"].isna().any():
            raise ValueError("taux de change absent avant la première date de la série FX")
        self.daily = m.pivot(index="date", columns="ticker", values="value").sort_index()
        self.fx_age_max = int(m["fx_age_days"].max())
        self.fx_stale_share = float((m.loc[needs_fx, "fx_age_days"] > 0).mean()) if needs_fx.any() else 0.0
        wv = self.daily.resample(conv.weekly_anchor).last()
        # La dernière case hebdomadaire est étiquetée par son vendredi, qui peut dépasser la dernière
        # observation : on la ramène à la date réelle pour ne jamais afficher une date sans donnée.
        last = self.daily.index[-1]
        wv.index = wv.index.where(wv.index <= last, last)
        self.weekly_values = wv
        self.weekly_returns = self.weekly_values.pct_change(fill_method=None).iloc[1:]
        self.universe = data.load_universe().set_index("ticker")

    def check_tickers(self, tickers) -> None:
        missing = sorted(set(tickers) - set(self.daily.columns))
        if missing:
            raise KeyError(f"tickers inconnus : {missing}")


# ---------------------------------------------------------------- métriques élémentaires


def total_return(v: pd.Series) -> float:
    v = v.dropna()
    return float(v.iloc[-1] / v.iloc[0] - 1)


def cagr(v: pd.Series) -> float:
    v = v.dropna()
    years = (v.index[-1] - v.index[0]).days / 365.25
    return float((v.iloc[-1] / v.iloc[0]) ** (1 / years) - 1)


def annual_vol(weekly_r: pd.Series) -> float:
    return float(weekly_r.dropna().std(ddof=1) * math.sqrt(WEEKS_PER_YEAR))


@dataclass
class Drawdown:
    depth: float
    peak: pd.Timestamp
    trough: pd.Timestamp
    recovery: pd.Timestamp | None  # première date où la valeur retrouve le sommet ; None si jamais

    def days_to_recover(self) -> int | None:
        return None if self.recovery is None else int((self.recovery - self.trough).days)

    def days_underwater(self, end: pd.Timestamp) -> int:
        return int(((self.recovery or end) - self.peak).days)


def max_drawdown(v: pd.Series) -> Drawdown:
    v = v.dropna()
    dd = v / v.cummax() - 1
    trough = dd.idxmin()
    peak = v.loc[:trough].idxmax()
    after = v.loc[trough:]
    rec = after[after >= v.loc[peak]]
    return Drawdown(float(dd.min()), peak, trough, rec.index[0] if len(rec) else None)


def period_return(v: pd.Series, start: str, end: str) -> float | None:
    """Rendement entre la dernière valeur connue au plus tard à `start` et à `end`."""
    v = v.dropna()
    a, b = v.loc[:start], v.loc[:end]
    if a.empty or b.empty or a.index[-1] == b.index[-1]:
        return None
    return float(b.iloc[-1] / a.iloc[-1] - 1)


@dataclass
class Window:
    worst: float | None
    worst_start: pd.Timestamp | None
    n_starts: int
    n_independent: int  # nombre de fenêtres sans chevauchement dans l'échantillon


def worst_window(v: pd.Series, years: float) -> Window:
    """Pire rendement observé sur toutes les fenêtres glissantes de `years` ans de l'échantillon."""
    v = v.dropna()
    span = (v.index[-1] - v.index[0]).days / 365.25
    horizon = pd.DateOffset(days=round(years * 365.25))
    starts = v.index[v.index + horizon <= v.index[-1]]
    if len(starts) == 0:
        return Window(None, None, 0, 0)
    ends = v.reindex(starts + horizon, method="ffill").to_numpy()
    r = ends / v.loc[starts].to_numpy() - 1
    i = int(np.nanargmin(r))
    return Window(float(r[i]), starts[i], len(starts), int(span // years))


# ---------------------------------------------------------------- portefeuilles fictifs


@dataclass
class PortfolioStats:
    weights: dict[str, float]
    weekly: pd.Series  # rendements hebdomadaires du portefeuille
    index: pd.Series  # valeur (base 1)
    weeks_used: int
    weeks_dropped: int
    risk_contrib: dict[str, float]  # part de la variance, somme = 1


def portfolio(m: Market, weights: dict[str, float]) -> PortfolioStats:
    if not weights or abs(sum(weights.values()) - 1) > 1e-9 or min(weights.values()) < 0:
        raise ValueError("poids positifs dont la somme vaut 1 (portefeuille sans levier ni vente à découvert)")
    tickers = list(weights)
    m.check_tickers(tickers)
    w = np.array([weights[t] for t in tickers])
    R = m.weekly_returns[tickers]
    full = R.dropna()
    rp = full @ w
    first = full.index[0] - pd.Timedelta(weeks=1)
    index = pd.concat([pd.Series([1.0], index=[first]), (1 + rp).cumprod()])
    cov = full.cov().to_numpy()
    var = float(w @ cov @ w)
    rc = w * (cov @ w) / var
    return PortfolioStats(
        weights=dict(weights),
        weekly=rp,
        index=index,
        weeks_used=len(full),
        weeks_dropped=len(R) - len(full),
        risk_contrib=dict(zip(tickers, map(float, rc))),
    )


def blend(base: dict[str, float], ticker: str, share: float) -> dict[str, float]:
    """Réduit proportionnellement `base` pour consacrer `share` du total à `ticker`."""
    if not 0 <= share <= 1:
        raise ValueError("part attendue entre 0 et 1 (ex. 0.10 pour 10 %)")
    out = {t: w * (1 - share) for t, w in base.items()}
    out[ticker] = out.get(ticker, 0.0) + share
    return {t: w for t, w in out.items() if w > 0}
