"""Read the immutable AlphaForge starter snapshot without downloading new data."""

from __future__ import annotations

import csv
import hashlib
import math
import os
from bisect import bisect_right
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


class DataError(ValueError):
    """The available snapshot cannot support the requested calculation."""


@dataclass(frozen=True)
class Dataset:
    assets: dict[str, dict[str, str]]
    prices: dict[str, dict[str, float]]
    fx: dict[str, float]
    calendar: tuple[str, ...]
    files: dict[str, dict[str, Any]]
    sources: list[dict[str, str]]
    directory: str

    def fx_on(self, observation_date: str) -> tuple[float, str, int]:
        """Last published-date FX value on or before D; never look forward."""
        dates = sorted(self.fx)
        index = bisect_right(dates, observation_date) - 1
        if index < 0:
            raise DataError(f"Aucun taux CAD/USD antérieur au {observation_date}.")
        used = dates[index]
        age = (date.fromisoformat(observation_date) - date.fromisoformat(used)).days
        return self.fx[used], used, age

    def catalog(self) -> list[dict[str, str]]:
        return [dict(self.assets[ticker]) for ticker in sorted(self.assets)]


def resolve_data_directory(data_dir: str | Path | None = None) -> Path:
    """An explicit path takes priority, then environment and portable locations."""
    if data_dir is not None:
        candidates = [Path(data_dir)]
    elif os.environ.get("ALPHAFORGE_DATA_DIR"):
        candidates = [Path(os.environ["ALPHAFORGE_DATA_DIR"])]
    else:
        project = Path(__file__).resolve().parents[1]
        candidates = [
            project / "data" / "alphaforge_starter",
            project / "data",
            Path.home() / "Downloads" / "Datathon2026" / "alphaforge_starter",
        ]
    for candidate in candidates:
        if (candidate / "prices_daily.csv").is_file():
            return candidate.resolve()
    raise DataError(
        "Jeu AlphaForge introuvable. Définir ALPHAFORGE_DATA_DIR vers le dossier "
        "contenant assets_universe.csv, prices_daily.csv et fx_usdcad_daily.csv."
    )


def _rows(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise DataError(f"Fichier de données absent : {path.name}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not required.issubset(reader.fieldnames or []):
            raise DataError(f"Colonnes obligatoires absentes de {path.name}.")
        return list(reader)


def _positive(value: str, context: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DataError(f"Valeur numérique invalide : {context}.") from exc
    if not math.isfinite(number) or number <= 0:
        raise DataError(f"Valeur positive finie requise : {context}.")
    return number


def _valid_date(value: str, context: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except (ValueError, TypeError) as exc:
        raise DataError(f"Date invalide : {context}.") from exc
    if parsed.isoformat() != value:
        raise DataError(f"Date ISO YYYY-MM-DD requise : {context}.")
    return value


def load_dataset(data_dir: str | Path | None = None) -> Dataset:
    """Validate and load the supplied data; adjusted prices are never readjusted."""
    directory = resolve_data_directory(data_dir)
    asset_rows = _rows(
        directory / "assets_universe.csv",
        {"ticker", "name", "asset_class", "market", "currency"},
    )
    assets: dict[str, dict[str, str]] = {}
    for row in asset_rows:
        ticker = row["ticker"].strip()
        if not ticker or ticker in assets:
            raise DataError("Ticker vide ou dupliqué dans assets_universe.csv.")
        if row["currency"] not in {"CAD", "USD"}:
            raise DataError(f"Devise non prise en charge : {row['currency']}.")
        assets[ticker] = dict(row, ticker=ticker)

    price_rows = _rows(
        directory / "prices_daily.csv", {"date", "ticker", "adj_close", "currency"}
    )
    prices: dict[str, dict[str, float]] = {ticker: {} for ticker in assets}
    for row in price_rows:
        ticker = row["ticker"]
        if ticker not in assets:
            raise DataError(f"Ticker de prix absent de l'univers : {ticker}.")
        if row["currency"] != assets[ticker]["currency"]:
            raise DataError(f"Devise incohérente pour {ticker}.")
        day = _valid_date(row["date"], f"prix {ticker}")
        if day in prices[ticker]:
            raise DataError(f"Prix dupliqué : {ticker}, {day}.")
        prices[ticker][day] = _positive(row["adj_close"], f"{ticker}, {day}")
    if any(not series for series in prices.values()):
        raise DataError("Au moins un actif de l'univers ne possède aucun prix.")

    fx_rows = _rows(directory / "fx_usdcad_daily.csv", {"date", "usdcad"})
    fx: dict[str, float] = {}
    for row in fx_rows:
        day = _valid_date(row["date"], "FX")
        if day in fx:
            raise DataError(f"Taux de change dupliqué : {day}.")
        fx[day] = _positive(row["usdcad"], f"FX {day}")
    if not fx:
        raise DataError("Aucun taux de change dans le jeu.")

    # Keep a stable comparison grid, regardless of which candidate is selected.
    # On the supplied snapshot this is the 1,228 common Canadian/U.S. sessions.
    equity_dates = [
        set(prices[ticker])
        for ticker, asset in assets.items()
        if asset["asset_class"] != "crypto"
    ]
    if not equity_dates:
        equity_dates = [set(series) for series in prices.values()]
    calendar = tuple(sorted(set.intersection(*equity_dates)))
    if len(calendar) < 2:
        raise DataError("Moins de deux dates communes exploitables.")

    metadata_file = directory / "sources_metadata.csv"
    sources = (
        _rows(metadata_file, {"file", "source", "source_url", "retrieved_on"})
        if metadata_file.is_file()
        else []
    )
    files: dict[str, dict[str, Any]] = {}
    counts = {
        "assets_universe.csv": len(asset_rows),
        "prices_daily.csv": len(price_rows),
        "fx_usdcad_daily.csv": len(fx_rows),
        "sources_metadata.csv": len(sources),
    }
    for name, count in counts.items():
        path = directory / name
        if path.is_file():
            files[name] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "rows": count,
            }
    return Dataset(assets, prices, fx, calendar, files, sources, str(directory))
