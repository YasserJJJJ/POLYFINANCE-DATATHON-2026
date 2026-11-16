"""Tests de fumée sur le jeu de départ et les conversions."""

import numpy as np
import pandas as pd
import pytest

from datathon2026 import data


@pytest.fixture(scope="module")
def prices():
    return data.load_prices()


def test_universe_has_31_assets():
    u = data.load_universe()
    assert len(u) == 31
    assert u["ticker"].is_unique


def test_prices_cover_universe_without_duplicates(prices):
    u = data.load_universe()
    assert set(prices["ticker"]) == set(u["ticker"])
    assert not prices.duplicated(["date", "ticker"]).any()
    assert (prices["adj_close"] > 0).all()


def test_listing_currency_matches_suffix(prices):
    is_tsx = prices["ticker"].str.endswith(".TO")
    assert (prices.loc[is_tsx, "currency"] == "CAD").all()
    assert (prices.loc[~is_tsx, "currency"] == "USD").all()


def test_wide_table_has_no_fill(prices):
    wide = data.adj_close_wide(prices)
    # Crypto cote 7 j/7, les actions non : des NaN doivent subsister les fins de semaine.
    assert wide["BTC-USD"].notna().sum() > wide["AAPL"].notna().sum()
    assert wide["AAPL"].isna().any()


def test_convert_to_cad_uses_same_day_rate_and_carries_forward():
    fx = pd.DataFrame({"date": pd.to_datetime(["2024-01-02", "2024-01-03"]), "usdcad": [1.30, 1.40]})
    p = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02", "2024-01-04", "2024-01-02", "2024-01-01"]),
            "ticker": ["AAPL", "AAPL", "RY.TO", "BTC-USD"],
            "open": 1.0, "high": 1.0, "low": 1.0, "close": 100.0, "adj_close": 100.0,
            "volume": 1, "currency": ["USD", "USD", "CAD", "USD"],
        }
    )
    out = data.convert_currency(p, "CAD", fx=fx).set_index(["ticker", "date"])["close"]
    assert out[("AAPL", pd.Timestamp("2024-01-02"))] == pytest.approx(130.0)
    assert out[("AAPL", pd.Timestamp("2024-01-04"))] == pytest.approx(140.0)  # taux reporté
    assert out[("RY.TO", pd.Timestamp("2024-01-02"))] == pytest.approx(100.0)  # déjà en CAD
    assert np.isnan(out[("BTC-USD", pd.Timestamp("2024-01-01"))])  # avant le premier taux


def test_convert_to_usd_divides_cad_prices():
    fx = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "usdcad": [1.25]})
    p = pd.DataFrame(
        {"date": pd.to_datetime(["2024-01-02"]), "ticker": ["RY.TO"], "open": 1.0, "high": 1.0,
         "low": 1.0, "close": 125.0, "adj_close": 125.0, "volume": 1, "currency": ["CAD"]}
    )
    assert data.convert_currency(p, "USD", fx=fx)["close"].iloc[0] == pytest.approx(100.0)


def test_personas_load():
    personas = data.load_personas()
    assert set(personas) == {"amira", "mateo", "robert"}
    assert personas["robert"]["horizon_ans"] == {"min": 3, "max": 5}
