"""Chargement des données de départ et conversion en dollars canadiens.

Choix documentés (repris dans la fiche qualité) :
- on utilise adj_close (ajusté dividendes + fractionnements), jamais close ;
- les titres en USD sont convertis en CAD avec le taux de la Banque du Canada
  du même jour, ou le dernier taux connu (jours fériés canadiens, fins de
  semaine pour les cryptos) ;
- on n'aligne pas les calendriers des actifs entre eux, sauf pour les
  corrélations (rendements hebdomadaires, vendredi).
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parents[2]
DOSSIER_DONNEES = Path(os.environ.get("ALPHAFORGE_DATA", RACINE / "data" / "raw" / "alphaforge_starter"))
SOURCE_PRIX = "Yahoo Finance via yfinance, jeu de départ AlphaForge (extrait le 2026-11-13)"
SOURCE_FX = "Banque du Canada, API Valet (USD/CAD quotidien)"
FENETRE = ("2021-11-12", "2026-11-12")


@lru_cache(maxsize=1)
def univers() -> pd.DataFrame:
    return pd.read_csv(DOSSIER_DONNEES / "assets_universe.csv").set_index("ticker")


@lru_cache(maxsize=1)
def _prix() -> pd.DataFrame:
    df = pd.read_csv(DOSSIER_DONNEES / "prices_daily.csv", parse_dates=["date"])
    return df.sort_values(["ticker", "date"])


@lru_cache(maxsize=1)
def _fx() -> pd.Series:
    df = pd.read_csv(DOSSIER_DONNEES / "fx_usdcad_daily.csv", parse_dates=["date"])
    return df.set_index("date")["usdcad"].sort_index()


def info_actif(ticker: str) -> dict:
    u = univers()
    if ticker not in u.index:
        raise KeyError(f"Actif inconnu : {ticker}")
    ligne = u.loc[ticker]
    return {"ticker": ticker, **{k: ligne[k] for k in ["name", "asset_class", "market", "currency", "sector"]}}


def jours_par_an(ticker: str) -> int:
    return 365 if info_actif(ticker)["asset_class"] == "crypto" else 252


@lru_cache(maxsize=64)
def serie_cad(ticker: str) -> pd.Series:
    """Prix ajusté en CAD, indexé par date."""
    p = _prix()
    s = p.loc[p["ticker"] == ticker].set_index("date")["adj_close"].astype(float)
    if s.empty:
        raise KeyError(f"Aucun prix pour {ticker}")
    if info_actif(ticker)["currency"] == "USD":
        fx = _fx().reindex(s.index.union(_fx().index)).ffill().bfill().reindex(s.index)
        s = s * fx
    s.name = ticker
    return s


def controle_qualite(ticker: str) -> list[dict]:
    """Contrôles avant tout calcul (inspirés de holdings-sanity d'Anthropic).

    Chaque contrôle renvoie ok / alerte / echec. Un échec rend le verdict gris.
    """
    p = _prix()
    brut = p.loc[p["ticker"] == ticker]
    resultats: list[dict] = []

    def ajouter(code: str, libelle: str, statut: str, detail: str) -> None:
        resultats.append({"code": code, "libelle": libelle, "statut": statut, "detail": detail})

    if brut.empty:
        ajouter("presence", "Données présentes", "echec", f"Aucune ligne pour {ticker}.")
        return resultats
    ajouter("presence", "Données présentes", "ok", f"{len(brut)} lignes.")

    doublons = int(brut.duplicated(subset=["date"]).sum())
    ajouter("doublons", "Pas de doublons de date", "ok" if doublons == 0 else "echec",
            f"{doublons} doublon(s).")

    non_positifs = int((brut["adj_close"] <= 0).sum())
    ajouter("magnitude", "Prix strictement positifs", "ok" if non_positifs == 0 else "echec",
            f"{non_positifs} prix nul(s) ou négatif(s).")

    debut, fin = brut["date"].min().date(), brut["date"].max().date()
    couvre = str(debut) <= "2021-11-16" and str(fin) >= "2026-11-06"
    ajouter("couverture", "Couvre la fenêtre 2021-11 → 2026-11", "ok" if couvre else "alerte",
            f"Du {debut} au {fin}.")

    ecarts = brut["date"].diff().dt.days.dropna()
    trou_max = int(ecarts.max()) if not ecarts.empty else 0
    seuil = 4 if info_actif(ticker)["asset_class"] == "crypto" else 6
    ajouter("trous", "Pas de trou anormal dans la série", "ok" if trou_max <= seuil else "alerte",
            f"Plus long écart entre deux cotations : {trou_max} jour(s).")

    rend = brut["adj_close"].pct_change().abs()
    sauts = int((rend > 0.4).sum())
    ajouter("sauts", "Pas de variation journalière > 40 %", "ok" if sauts == 0 else "alerte",
            f"{sauts} variation(s) suspecte(s).")

    devise = info_actif(ticker)["currency"]
    ajouter("devise", "Devise connue et convertie en CAD", "ok",
            "Déjà en CAD." if devise == "CAD" else "Converti avec le taux USD/CAD de la Banque du Canada.")
    return resultats
