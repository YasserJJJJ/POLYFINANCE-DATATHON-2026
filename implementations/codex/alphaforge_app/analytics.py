"""Deterministic, retrospective portfolio comparisons in Canadian dollars.

Weights are initial capital fractions, with no inter-asset rebalancing. Each
adjusted-price series represents distributions reinvested in that same asset.
This module does not estimate expected returns or select an optimal portfolio.
"""

from __future__ import annotations

import math
import statistics
from datetime import date, timedelta
from typing import Any, Mapping, Sequence

from .datasets import DataError, Dataset, load_dataset


DAYS_PER_YEAR = 365.2425
MODEL_VERSION = "cad-buy-and-hold-v1"


def validate_weights(weights: Mapping[str, float]) -> dict[str, float]:
    if not isinstance(weights, Mapping) or not weights:
        raise DataError("Le portefeuille doit contenir au moins un poids.")
    parsed: dict[str, float] = {}
    for ticker, weight in weights.items():
        if not isinstance(ticker, str) or not ticker.strip():
            raise DataError("Chaque position doit avoir un ticker.")
        if isinstance(weight, bool):
            raise DataError("Un poids doit être numérique, pas booléen.")
        try:
            value = float(weight)
        except (ValueError, TypeError) as exc:
            raise DataError(f"Poids invalide pour {ticker}.") from exc
        if not math.isfinite(value) or value < 0:
            raise DataError("Les poids doivent être finis et positifs ou nuls.")
        normalized = ticker.strip().upper()
        if normalized in parsed:
            raise DataError(f"Ticker répété après normalisation : {normalized}.")
        parsed[normalized] = value
    total = math.fsum(parsed.values())
    if not math.isclose(total, 1.0, abs_tol=1e-8, rel_tol=0.0):
        raise DataError(
            f"La somme des poids doit être 1 (100 %), valeur reçue : {total:.6g}."
        )
    # Absorb only floating point roundoff. Never interpret percent weights as
    # fractions or silently normalize an incorrectly specified allocation.
    return {ticker: value / total for ticker, value in parsed.items() if value > 0}


def set_target_weight(
    weights: Mapping[str, float], ticker: str, target_weight: float
) -> dict[str, float]:
    """Set one initial weight; preserve relative weights of all other assets."""
    original = validate_weights(weights)
    ticker = ticker.strip().upper()
    if isinstance(target_weight, bool):
        raise DataError("Poids cible invalide.")
    try:
        target = float(target_weight)
    except (TypeError, ValueError) as exc:
        raise DataError("Poids cible invalide.") from exc
    if not ticker or not math.isfinite(target) or not 0 <= target <= 1:
        raise DataError("Le poids cible doit être compris entre 0 et 1.")
    others = {name: weight for name, weight in original.items() if name != ticker}
    other_total = math.fsum(others.values())
    if target < 1 and other_total <= 1e-12:
        raise DataError(
            "Préciser un actif de destination : aucun autre poids à redistribuer."
        )
    result = (
        {name: (1 - target) * weight / other_total for name, weight in others.items()}
        if other_total > 0
        else {}
    )
    if target > 0:
        result[ticker] = target
    return validate_weights(result)


def compound_annual_growth(
    first_value: float, last_value: float, first_date: str, last_date: str
) -> float:
    """CAGR as a fraction using actual elapsed calendar time."""
    years = (
        date.fromisoformat(last_date) - date.fromisoformat(first_date)
    ).days / DAYS_PER_YEAR
    if years <= 0 or first_value <= 0 or last_value <= 0:
        raise DataError("Le CAGR nécessite une période et des valeurs positives.")
    return math.expm1(math.log(last_value / first_value) / years)


def drawdowns(values: Sequence[float]) -> list[float]:
    """Fractions below the running high; zero initially, nonpositive afterwards."""
    if not values:
        return []
    peak = values[0]
    if peak <= 0:
        raise DataError("La valeur initiale doit être positive.")
    result = []
    for value in values:
        if not math.isfinite(value) or value <= 0:
            raise DataError("Les valeurs doivent être positives et finies.")
        peak = max(peak, value)
        result.append(value / peak - 1.0)
    return result


def historical_expected_shortfall(
    returns: Sequence[float], tail_probability: float = 0.05
) -> float:
    """Mean loss in an exact empirical lower tail, using fractional boundary mass.

    Returned as a fraction (positive loss, potentially negative if all tail
    returns were gains). It refers to sampled intervals, not a fixed future day.
    """
    if not returns or not 0 < tail_probability <= 1:
        raise DataError("Échantillon et probabilité de queue invalides.")
    ordered = sorted(returns)
    mass = len(ordered) * tail_probability
    whole = int(math.floor(mass))
    fraction = mass - whole
    weighted = math.fsum(ordered[:whole])
    if fraction > 1e-12:
        weighted += fraction * ordered[whole]
    return -weighted / mass


def _period(dates: Sequence[str], start: str | None, end: str | None) -> list[str]:
    for label, value in (("début", start), ("fin", end)):
        if value is not None:
            try:
                parsed = date.fromisoformat(value)
            except (ValueError, TypeError) as exc:
                raise DataError(f"Date de {label} invalide (YYYY-MM-DD).") from exc
            if parsed.isoformat() != value:
                raise DataError(f"Date de {label} invalide (YYYY-MM-DD).")
    if start and end and start > end:
        raise DataError("La date de début doit précéder la date de fin.")
    chosen = [day for day in dates if (not start or day >= start) and (not end or day <= end)]
    if len(chosen) < 3:
        raise DataError("Au moins trois dates communes sont nécessaires.")
    return chosen


def _metrics(dates: Sequence[str], values: Sequence[float]) -> dict[str, Any]:
    returns = [b / a - 1 for a, b in zip(values, values[1:])]
    years = (date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days / DAYS_PER_YEAR
    periods_per_year = len(returns) / years
    # This is the conventional dispersion of sampled simple returns, annualized
    # with the observed grid frequency. It assumes comparable independent
    # intervals; weekend/holiday lengths are disclosed in the metadata.
    volatility = statistics.stdev(returns) * math.sqrt(periods_per_year)
    dd = drawdowns(values)
    trough = min(range(len(dd)), key=dd.__getitem__)
    peak = max(range(trough + 1), key=values.__getitem__)
    return {
        "initial_value_cad": round(values[0], 2),
        "ending_value_cad": round(values[-1], 2),
        "total_return_pct": round((values[-1] / values[0] - 1) * 100, 6),
        "cagr_pct": round(compound_annual_growth(values[0], values[-1], dates[0], dates[-1]) * 100, 6),
        "volatility_pct": round(volatility * 100, 6),
        "max_drawdown_pct": round(dd[trough] * 100, 6),
        "drawdown_peak_date": dates[peak],
        "drawdown_trough_date": dates[trough],
        "worst_interval_pct": round(min(returns) * 100, 6),
        "historical_expected_shortfall_95_pct": round(
            historical_expected_shortfall(returns) * 100, 6
        ),
        "observed_intervals_per_year": round(periods_per_year, 6),
    }


def _cad_panel(
    dataset: Dataset, tickers: Sequence[str], dates: Sequence[str]
) -> tuple[dict[str, list[float]], dict[str, Any]]:
    rates: dict[str, float] = {}
    used_dates: dict[str, str] = {}
    fx_ages: dict[str, int] = {}
    uses_usd = any(dataset.assets[ticker]["currency"] == "USD" for ticker in tickers)
    if uses_usd:
        for day in dates:
            rate, used, age = dataset.fx_on(day)
            if age > 7:
                raise DataError(
                    f"Taux de change trop ancien au {day} ({age} jours)."
                )
            rates[day], used_dates[day], fx_ages[day] = rate, used, age
    panel: dict[str, list[float]] = {}
    for ticker in tickers:
        series = dataset.prices[ticker]
        usd = dataset.assets[ticker]["currency"] == "USD"
        missing = [day for day in dates if day not in series]
        if missing:
            raise DataError(f"Prix absent pour {ticker} au {missing[0]}.")
        panel[ticker] = [
            series[day] * (rates[day] if usd else 1.0) for day in dates
        ]
    return panel, {
        "fx_stale_dates": sum(age > 0 for age in fx_ages.values()),
        "max_fx_age_days": max(fx_ages.values(), default=0),
        "fx_carried_dates": [
            {"valuation_date": day, "fx_observation_date": used_dates[day], "age_days": age}
            for day, age in fx_ages.items() if age > 0
        ],
    }


def _wealth(
    weights: Mapping[str, float], panel: Mapping[str, Sequence[float]], capital: float
) -> list[float]:
    first_series = next(iter(panel.values()))
    return [
        capital * math.fsum(weight * panel[ticker][i] / panel[ticker][0] for ticker, weight in weights.items())
        for i in range(len(first_series))
    ]


def _scenario_windows(first: str, last: str) -> list[dict[str, str]]:
    recent_start = (date.fromisoformat(last) - timedelta(days=365)).isoformat()
    candidates = [
        {"id": "year_2022", "name": "Année 2022", "start": "2021-12-31", "end": "2022-12-31"},
        {"id": "march_2023", "name": "Mars 2023", "start": "2023-03-08", "end": "2023-03-24"},
        {"id": "recent_year", "name": "Douze derniers mois disponibles", "start": recent_start, "end": last},
    ]
    return [item for item in candidates if item["start"] >= first and item["end"] <= last]


def _analyze(
    option: Mapping[str, Any],
    weights: dict[str, float],
    dates: list[str],
    panel: dict[str, list[float]],
    dataset: Dataset,
    capital: float,
) -> dict[str, Any]:
    values = _wealth(weights, panel, capital)
    metrics = _metrics(dates, values)
    dd = drawdowns(values)
    holdings: list[dict[str, Any]] = []
    currency_weights: dict[str, float] = {}
    class_weights: dict[str, float] = {}
    for ticker, weight in weights.items():
        asset = dataset.assets[ticker]
        gross = panel[ticker][-1] / panel[ticker][0]
        local = dataset.prices[ticker][dates[-1]] / dataset.prices[ticker][dates[0]]
        holdings.append({
            "ticker": ticker,
            "name": asset["name"],
            "initial_weight_pct": round(weight * 100, 6),
            "ending_weight_pct": round(capital * weight * gross / values[-1] * 100, 6),
            "total_return_cad_pct": round((gross - 1) * 100, 6),
            "total_return_local_pct": round((local - 1) * 100, 6),
            "currency": asset["currency"],
            "asset_class": asset["asset_class"],
        })
        currency_weights[asset["currency"]] = currency_weights.get(asset["currency"], 0) + weight * 100
        class_weights[asset["asset_class"]] = class_weights.get(asset["asset_class"], 0) + weight * 100
    largest = max(weights, key=weights.__getitem__)
    scenarios = []
    for window in _scenario_windows(dates[0], dates[-1]):
        indexes = [i for i, day in enumerate(dates) if window["start"] <= day <= window["end"]]
        if len(indexes) < 3:
            continue
        scenario_dates = [dates[i] for i in indexes]
        scenario_panel = {ticker: [panel[ticker][i] for i in indexes] for ticker in weights}
        scenario_metrics = _metrics(scenario_dates, _wealth(weights, scenario_panel, capital))
        scenarios.append({
            **window,
            "requested_start": window["start"],
            "requested_end": window["end"],
            "start": scenario_dates[0],
            "end": scenario_dates[-1],
            "total_return_pct": scenario_metrics["total_return_pct"],
            "max_drawdown_pct": scenario_metrics["max_drawdown_pct"],
            "ending_value_cad": scenario_metrics["ending_value_cad"],
            "allocation_reset_at_start": True,
        })
    warnings = []
    if any(dataset.assets[ticker]["asset_class"] == "crypto" for ticker in weights):
        warnings.append(
            "Crypto échantillonnée aux seules séances communes : les creux "
            "intrajournaliers et de fin de semaine peuvent être invisibles."
        )
    if any(dataset.assets[ticker]["asset_class"].startswith("etf") for ticker in weights):
        warnings.append(
            "Les poids portent sur les instruments. Les compositions des FNB "
            "ne sont pas disponibles : les expositions communes ne sont pas mesurées."
        )
    if "ESGV" in weights:
        warnings.append(
            "Le nom ESGV ne constitue pas une vérification des exclusions ou "
            "controverses correspondant à vos préférences."
        )
    return {
        "id": str(option.get("id", "portfolio")),
        "name": str(option.get("name", "Portefeuille")),
        "weights": weights,
        "metrics": metrics,
        "series": [
            {"date": day, "value": round(value, 2), "drawdown_pct": round(loss * 100, 6)}
            for day, value, loss in zip(dates, values, dd)
        ],
        "scenarios": scenarios,
        "holdings": sorted(holdings, key=lambda item: -item["initial_weight_pct"]),
        "concentration": {
            "largest_initial_weight_pct": round(weights[largest] * 100, 6),
            "largest_initial_ticker": largest,
            "instrument_hhi": round(math.fsum(weight * weight for weight in weights.values()), 8),
            "listing_currency_weights_pct": {key: round(value, 6) for key, value in currency_weights.items()},
            "asset_class_weights_pct": {key: round(value, 6) for key, value in class_weights.items()},
            "look_through_available": False,
        },
        "warnings": warnings,
    }


def compare_portfolios(
    options: Sequence[Mapping[str, Any]],
    capital_cad: float = 10_000,
    start: str | None = None,
    end: str | None = None,
    dataset: Dataset | None = None,
) -> dict[str, Any]:
    """Compare initial allocations on one calendar and one immutable snapshot."""
    dataset = dataset or load_dataset()
    if not options or len(options) > 20:
        raise DataError("Fournir entre un et vingt portefeuilles.")
    if isinstance(capital_cad, bool):
        raise DataError("Le capital fictif doit être positif et fini.")
    try:
        capital = float(capital_cad)
    except (ValueError, TypeError) as exc:
        raise DataError("Capital fictif invalide.") from exc
    if not math.isfinite(capital) or not 0 < capital <= 1e12:
        raise DataError("Le capital fictif doit être compris entre 0 et 10¹² CAD.")
    weights = [validate_weights(option.get("weights", {})) for option in options]
    tickers = sorted({ticker for item in weights for ticker in item})
    unknown = sorted(set(tickers) - set(dataset.assets))
    if unknown:
        raise DataError("Symboles absents du jeu de données : " + ", ".join(unknown))
    dates = _period(dataset.calendar, start, end)
    panel, fx_meta = _cad_panel(dataset, tickers, dates)
    results = [
        _analyze(option, allocation, dates, panel, dataset, capital)
        for option, allocation in zip(options, weights)
    ]
    years = (date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days / DAYS_PER_YEAR
    meta = {
        "model_version": MODEL_VERSION,
        "analysis_mode": "retrospective_replay",
        "start": dates[0],
        "end": dates[-1],
        "requested_start": start,
        "requested_end": end,
        "observations": len(dates),
        "elapsed_years": round(years, 8),
        "currency": "CAD",
        "valuation_time_rule": "Date D valorisée à D+1 00:00:00 UTC; prix actions de D et bougie crypto UTC de D achevée.",
        "first_valuation_at": (date.fromisoformat(dates[0]) + timedelta(days=1)).isoformat() + "T00:00:00Z",
        "last_valuation_at": (date.fromisoformat(dates[-1]) + timedelta(days=1)).isoformat() + "T00:00:00Z",
        "calendar": "Intersection fixe des dates de tous les actifs hors crypto du snapshot; aucune imputation de prix.",
        "calendar_session_count_full_snapshot": len(dataset.calendar),
        "fx_policy": "adj_close USD × FXUSDCAD indicatif daté D ou dernière date antérieure; âge maximal 7 jours.",
        **fx_meta,
        "return_policy": "Achat-conservation; dividendes réinvestis dans chaque actif via adj_close; aucun rééquilibrage entre actifs.",
        "volatility_policy": "Écart-type échantillonnal des rendements simples entre observations × racine(nombre d'intervalles / années écoulées).",
        "cost_policy": "Hors frais de transaction, frais de change et impôts; frais internes des fonds déjà reflétés dans les cours.",
        "files": dataset.files,
        "sources": dataset.sources,
        "limitations": [
            "Comparaison rétrospective, pas prévision ni backtest de sélection historiquement réalisable : univers et prix ajustés acquis en 2026.",
            "Le drawdown est le creux observé sur cette grille; il ne borne pas une perte future et ignore les mouvements entre observations.",
            "La volatilité annualisée suppose des intervalles comparables et une mise à l'échelle en racine du temps; week-ends et jours fériés créent des intervalles inégaux.",
            "Le taux FX est une moyenne indicative, pas un cours exécutable synchronisé avec la clôture des actifs.",
            "L'heure de valorisation est une convention documentaire; les fichiers ne contiennent pas l'historique des heures exactes de publication.",
            "Les fenêtres historiques sont descriptives, choisies à l'avance dans le code; aucune probabilité de scénario futur ne leur est attribuée.",
            "Aucun score ESG, exposition réelle des FNB, valorisation fondamentale ou capacité personnelle de perte n'est déduit de ces données.",
        ],
    }
    return {"options": results, "meta": meta}


def analyze_portfolio(
    weights: Mapping[str, float],
    capital_cad: float = 10_000,
    start: str | None = None,
    end: str | None = None,
    dataset: Dataset | None = None,
) -> dict[str, Any]:
    result = compare_portfolios(
        [{"id": "portfolio", "name": "Portefeuille", "weights": weights}],
        capital_cad=capital_cad,
        start=start,
        end=end,
        dataset=dataset,
    )
    return {**result["options"][0], "meta": result["meta"]}
