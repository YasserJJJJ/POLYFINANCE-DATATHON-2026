"""Calculs : cas analytiques simples et invariants sur les données réelles."""

import numpy as np
import pandas as pd
import pytest

from datathon2026 import analytics as a


def series(values, start="2022-01-03"):
    return pd.Series(values, index=pd.bdate_range(start, periods=len(values)), dtype=float)


def test_max_drawdown_known_path():
    v = series([100, 120, 90, 60, 80, 121, 130])
    dd = a.max_drawdown(v)
    assert dd.depth == pytest.approx(60 / 120 - 1)
    assert dd.peak == v.index[1] and dd.trough == v.index[3] and dd.recovery == v.index[5]


def test_max_drawdown_without_recovery():
    dd = a.max_drawdown(series([100, 80, 90]))
    assert dd.recovery is None and dd.depth == pytest.approx(-0.2)


def test_worst_window_counts_independent_windows():
    idx = pd.date_range("2020-01-01", "2025-12-31", freq="D")
    v = pd.Series(np.linspace(100, 160, len(idx)), index=idx)
    w = a.worst_window(v, 3)
    assert w.n_independent == 1 and w.worst > 0  # trajectoire croissante : pire fenêtre positive


@pytest.fixture(scope="module")
def m():
    return a.Market()


def test_weekly_cad_return_matches_usd_return_times_fx(m):
    # Pour une semaine où le taux est connu les deux vendredis : 1 + r_CAD = (1 + r_USD)(1 + r_FX)
    from datathon2026 import data

    prices = data.load_prices(["SPY"]).set_index("date")["adj_close"]
    fx = data.load_fx().set_index("date")["usdcad"]
    fridays = [d for d in m.weekly_returns.index if d in prices.index and d in fx.index]
    d1, d0 = fridays[10], fridays[9]
    if (d1 - d0).days != 7:
        pytest.skip("semaine non consécutive")
    expected = prices[d1] * fx[d1] / (prices[d0] * fx[d0]) - 1
    assert m.weekly_returns.loc[d1, "SPY"] == pytest.approx(expected, rel=1e-9)


def test_weekly_grid_neutralises_holidays(m):
    # Actions canadiennes, américaines et crypto : rendements hebdomadaires définis sur toute la période
    R = m.weekly_returns[["XIU.TO", "SPY", "BTC-USD"]]
    assert R.notna().all().all()


def test_risk_contributions_sum_to_one(m):
    p = a.portfolio(m, {"SPY": 0.5, "XBB.TO": 0.3, "BTC-USD": 0.2})
    assert sum(p.risk_contrib.values()) == pytest.approx(1.0)
    assert p.weeks_dropped == 0


def test_portfolio_rejects_leverage(m):
    with pytest.raises(ValueError):
        a.portfolio(m, {"SPY": 1.2, "XBB.TO": -0.2})


def test_blend_keeps_total():
    w = a.blend({"A": 0.6, "B": 0.4}, "C", 0.1)
    assert sum(w.values()) == pytest.approx(1.0) and w["C"] == pytest.approx(0.1) and w["A"] == pytest.approx(0.54)
