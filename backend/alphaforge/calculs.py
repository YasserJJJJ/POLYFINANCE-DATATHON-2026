"""Outils de calcul : les « calculatrices » des agents.

Fonctions pures et déterministes. Aucun LLM ne produit de chiffre : les agents
appellent ces fonctions et citent le résultat (voir dossier.Fait).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .donnees import jours_par_an, serie_cad


def pire_chute(ticker: str) -> dict:
    """Baisse maximale d'un sommet à un creux sur la fenêtre disponible (en CAD)."""
    s = serie_cad(ticker)
    sommet_courant = s.cummax()
    baisse = s / sommet_courant - 1
    date_creux = baisse.idxmin()
    date_sommet = s.loc[:date_creux].idxmax()
    valeur_sommet = s.loc[date_sommet]
    apres = s.loc[date_creux:]
    retour = apres[apres >= valeur_sommet]
    date_retour = retour.index[0] if not retour.empty else None
    jours_recup = (date_retour - date_creux).days if date_retour is not None else None
    return {
        "pire_chute_pct": round(float(baisse.min()) * 100, 1),
        "date_sommet": str(date_sommet.date()),
        "date_creux": str(date_creux.date()),
        "date_retour": str(date_retour.date()) if date_retour is not None else None,
        "recuperation_annees": round(jours_recup / 365.25, 1) if jours_recup is not None else None,
        "recupere": date_retour is not None,
        "annees_depuis_creux": round((s.index[-1] - date_creux).days / 365.25, 1),
    }


def volatilite_annualisee(ticker: str) -> float:
    s = serie_cad(ticker)
    rend = np.log(s / s.shift(1)).dropna()
    return round(float(rend.std() * math.sqrt(jours_par_an(ticker))) * 100, 1)


def rendement_annualise(ticker: str) -> float:
    s = serie_cad(ticker)
    annees = (s.index[-1] - s.index[0]).days / 365.25
    return round(float((s.iloc[-1] / s.iloc[0]) ** (1 / annees) - 1) * 100, 1)


def _hebdo(ticker: str) -> pd.Series:
    return serie_cad(ticker).resample("W-FRI").last().dropna()


def pire_annee_glissante(ticker: str) -> dict:
    """Pire rendement sur 12 mois glissants (pas hebdomadaire)."""
    h = _hebdo(ticker)
    r = (h / h.shift(52) - 1).dropna()
    fin = r.idxmin()
    return {"pire_12_mois_pct": round(float(r.min()) * 100, 1), "fin_periode": str(fin.date()),
            "part_periodes_negatives_pct": round(float((r < 0).mean()) * 100, 1)}


def correlation(t1: str, t2: str) -> float:
    """Corrélation des rendements hebdomadaires (calendriers alignés le vendredi)."""
    a, b = _hebdo(t1).pct_change(), _hebdo(t2).pct_change()
    df = pd.concat([a, b], axis=1, join="inner").dropna()
    return round(float(df.corr().iloc[0, 1]), 2)


def perte_en_dollars(montant: float, chute_pct: float) -> float:
    """Scénario : si le montant subissait la pire chute observée."""
    return round(montant * chute_pct / 100, 0)
