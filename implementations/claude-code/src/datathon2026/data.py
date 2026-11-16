"""Chargement du jeu de départ AlphaForge et conversions de base.

Règles reprises du README du jeu de départ :
- les prix sont dans la devise de cotation (.TO en CAD, le reste en USD) ;
- aucune ligne n'est remplie ni alignée : une ligne n'existe que les jours de cotation ;
- utiliser adj_close pour les rendements ; ne pas réappliquer les splits ;
- le fichier FX n'a pas de ligne les jours fériés canadiens : on reporte le dernier taux connu.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pandas as pd

from .paths import CONFIG_DIR, STARTER_DIR


def _read(name: str, starter_dir: Path | None = None, **kwargs) -> pd.DataFrame:
    path = (starter_dir or STARTER_DIR) / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path} introuvable. Copiez le jeu de départ dans data/raw/alphaforge_starter "
            "(voir data/README.md) ou définissez DATATHON_STARTER_DIR."
        )
    return pd.read_csv(path, **kwargs)


def load_universe(starter_dir: Path | None = None) -> pd.DataFrame:
    return _read("assets_universe.csv", starter_dir)


def load_prices(tickers: list[str] | None = None, starter_dir: Path | None = None) -> pd.DataFrame:
    df = _read("prices_daily.csv", starter_dir, parse_dates=["date"])
    if tickers is not None:
        missing = set(tickers) - set(df["ticker"].unique())
        if missing:
            raise KeyError(f"Tickers absents du jeu de départ : {sorted(missing)}")
        df = df[df["ticker"].isin(tickers)]
    return df.sort_values(["ticker", "date"]).reset_index(drop=True)


def load_corporate_actions(starter_dir: Path | None = None) -> pd.DataFrame:
    return _read("corporate_actions.csv", starter_dir, parse_dates=["ex_date"])


def load_fx(starter_dir: Path | None = None) -> pd.DataFrame:
    return _read("fx_usdcad_daily.csv", starter_dir, parse_dates=["date"]).sort_values("date")


def load_macro(series_ids: list[str] | None = None, starter_dir: Path | None = None) -> pd.DataFrame:
    """Séries macro au format long. Attention : les séries mensuelles sont datées au mois
    de référence, pas à la date de publication (risque de fuite d'information en simulation)."""
    df = _read("macro_rates.csv", starter_dir, parse_dates=["date"])
    if series_ids is not None:
        df = df[df["series_id"].isin(series_ids)]
    return df.sort_values(["series_id", "date"]).reset_index(drop=True)


def load_personas(path: Path | None = None) -> dict[str, dict]:
    with open(path or CONFIG_DIR / "personas.toml", "rb") as f:
        return tomllib.load(f)


def adj_close_wide(prices: pd.DataFrame) -> pd.DataFrame:
    """Tableau date × ticker des clôtures ajustées, sans remplissage (NaN = pas de cotation)."""
    return prices.pivot(index="date", columns="ticker", values="adj_close").sort_index()


def convert_currency(
    prices: pd.DataFrame,
    target: str = "CAD",
    fx: pd.DataFrame | None = None,
    columns: tuple[str, ...] = ("open", "high", "low", "close", "adj_close"),
) -> pd.DataFrame:
    """Convertit les colonnes de prix dans la devise cible avec le taux Banque du Canada.

    Le taux du jour D est utilisé ; s'il manque (jour férié canadien, fin de semaine pour
    les cryptos), le dernier taux connu à D est reporté (aucune information future).
    Les dates antérieures au premier taux disponible restent NaN.
    """
    target = target.upper()
    if target not in {"CAD", "USD"}:
        raise ValueError("target doit être 'CAD' ou 'USD'")
    fx = (fx if fx is not None else load_fx())[["date", "usdcad"]].sort_values("date")
    out = pd.merge_asof(prices.sort_values("date"), fx, on="date", direction="backward")
    factor = pd.Series(1.0, index=out.index)
    if target == "CAD":
        factor[out["currency"] == "USD"] = out["usdcad"]
    else:
        factor[out["currency"] == "CAD"] = 1.0 / out["usdcad"]
    for col in columns:
        out[col] = out[col] * factor
    out["currency"] = target
    return out.drop(columns="usdcad").sort_values(["ticker", "date"]).reset_index(drop=True)
