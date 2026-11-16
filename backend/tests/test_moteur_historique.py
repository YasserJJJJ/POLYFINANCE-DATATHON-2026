# Provenance : IMPLEMENTATION_IDENTIFIANT_A_ATTRIBUER_2026-11-15 (codex).zip
# Origine : tests/test_analytics.py
# SHA-256 original : d5f309f489483f6a2495ed82dbb98c788129ff84fe34e0cd614d12170f9d832d
# Transfert : 2026-11-15 ; formules inchangées.
import math
import unittest

from alphaforge.moteurs.historique.analytics import (
    DAYS_PER_YEAR,
    analyze_portfolio,
    compare_portfolios,
    compound_annual_growth,
    drawdowns,
    historical_expected_shortfall,
    set_target_weight,
    validate_weights,
)
from alphaforge.moteurs.historique.datasets import DataError, Dataset


def fixture():
    dates = ("2024-01-01", "2024-01-02", "2024-01-03")
    return Dataset(
        assets={
            "CAD": {"ticker": "CAD", "name": "Canadian asset", "currency": "CAD", "asset_class": "equity"},
            "USD": {"ticker": "USD", "name": "US asset", "currency": "USD", "asset_class": "equity"},
        },
        prices={"CAD": dict(zip(dates, (100, 120, 90))), "USD": dict(zip(dates, (100, 110, 100)))},
        fx={"2024-01-01": 1.2, "2024-01-03": 1.5},
        calendar=dates,
        files={},
        sources=[],
        directory="synthetic",
    )


class FinancialInvariants(unittest.TestCase):
    def test_fx_is_multiplicative_and_only_looks_back(self):
        data = fixture()
        result = analyze_portfolio({"USD": 1}, dataset=data)
        self.assertEqual([row["value"] for row in result["series"]], [10000, 11000, 12500])
        self.assertEqual(result["metrics"]["total_return_pct"], 25)
        self.assertEqual(result["meta"]["fx_stale_dates"], 1)
        self.assertEqual(data.fx_on("2024-01-02"), (1.2, "2024-01-01", 1))
        with self.assertRaises(DataError):
            data.fx_on("2023-12-31")

    def test_buy_and_hold_has_drift_and_does_not_rebalance_daily(self):
        result = analyze_portfolio({"CAD": 0.5, "USD": 0.5}, dataset=fixture())
        self.assertEqual([row["value"] for row in result["series"]], [10000, 11500, 10750])
        self.assertEqual(result["metrics"]["ending_value_cad"], 10750)
        ending = {row["ticker"]: row["ending_weight_pct"] for row in result["holdings"]}
        self.assertAlmostEqual(ending["CAD"], 4500 / 10750 * 100, places=5)
        self.assertAlmostEqual(result["metrics"]["max_drawdown_pct"], (10750 / 11500 - 1) * 100, places=5)

    def test_cagr_is_geometric_not_annualized_arithmetic_average(self):
        # +100%, then -50% leaves initial wealth unchanged.
        self.assertEqual(compound_annual_growth(100, 100, "2022-01-01", "2024-01-01"), 0)
        expected = 1.21 ** (DAYS_PER_YEAR / 730) - 1
        self.assertAlmostEqual(compound_annual_growth(100, 121, "2022-01-01", "2024-01-01"), expected)

    def test_drawdown_uses_running_peak_not_initial_wealth(self):
        actual = drawdowns([100, 120, 90, 110, 130, 104])
        for value, expected in zip(actual, [0, 0, -0.25, -1 / 12, 0, -0.2]):
            self.assertAlmostEqual(value, expected)

    def test_target_weight_preserves_other_ratios_and_budget(self):
        result = set_target_weight({"A": 0.6, "B": 0.3, "C": 0.1}, "A", 0.2)
        self.assertAlmostEqual(math.fsum(result.values()), 1)
        self.assertAlmostEqual(result["B"] / result["C"], 3)
        self.assertAlmostEqual(result["A"], 0.2)
        with self.assertRaises(DataError):
            set_target_weight({"A": 1.0}, "A", 0.2)

    def test_exact_empirical_tail_with_fractional_boundary(self):
        # 1.5 observations in the 50% tail: full -30%, half -10%.
        self.assertAlmostEqual(historical_expected_shortfall([-0.3, -0.1, 0.2], 0.5), 0.35 / 1.5)
        self.assertAlmostEqual(historical_expected_shortfall([-0.3, -0.1, 0.2], 0.05), 0.3)

    def test_bad_weights_and_unknown_symbols_fail_explicitly(self):
        for weights in ({"CAD": 50, "USD": 50}, {"CAD": -0.1, "USD": 1.1}, {"CAD": float("nan")}, {"CAD": True}):
            with self.assertRaises(DataError):
                validate_weights(weights)
        with self.assertRaisesRegex(DataError, "absents"):
            analyze_portfolio({"UNKNOWN": 1}, dataset=fixture())

    def test_comparisons_share_dates_and_scaling_capital_does_not_change_returns(self):
        options = [{"id": "a", "weights": {"CAD": 1}}, {"id": "b", "weights": {"USD": 1}}]
        low = compare_portfolios(options, 1000, dataset=fixture())
        high = compare_portfolios(options, 10000, dataset=fixture())
        self.assertEqual(low["meta"]["observations"], 3)
        for left, right in zip(low["options"], high["options"]):
            self.assertEqual(left["metrics"]["total_return_pct"], right["metrics"]["total_return_pct"])
            self.assertAlmostEqual(left["metrics"]["ending_value_cad"] * 10, right["metrics"]["ending_value_cad"])
        self.assertEqual(
            [row["date"] for row in low["options"][0]["series"]],
            [row["date"] for row in low["options"][1]["series"]],
        )


if __name__ == "__main__":
    unittest.main()
