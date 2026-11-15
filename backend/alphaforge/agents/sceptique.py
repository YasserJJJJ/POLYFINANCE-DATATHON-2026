"""Sceptique : cherche une faille précise dans les faits et force un recalcul.

Pas d'opinion libre : chaque objection cite un F-n et demande une vérification
que le code exécute. Version hors ligne : 3 objections types, appliquées
seulement quand elles sont pertinentes. Le LLM (à brancher) pourra en proposer
d'autres, toujours sous la forme {cible, texte, recalcul}.
"""
from __future__ import annotations

import time

import pandas as pd

from ..donnees import _prix
from ..dossier import Dossier, Objection

MAX_OBJECTIONS = 3


def _chute_en_devise_locale(ticker: str) -> float:
    p = _prix()
    s = p.loc[p["ticker"] == ticker].set_index("date")["adj_close"].astype(float)
    return round(float((s / s.cummax() - 1).min()) * 100, 1)


def executer(d: Dossier) -> None:
    debut = time.perf_counter()
    m, ids = d.demande["mesures"], d.demande["ids_faits"]
    ticker = d.demande["ticker"]

    if m["devise"] == "USD":
        usd = _chute_en_devise_locale(ticker)
        obj = Objection(f"O-{len(d.objections) + 1}", ids["chute"],
                        f"La pire chute ({m['pire_chute_pct']} %) est-elle mesurée en dollars canadiens ? "
                        "Pour un investisseur canadien, le taux de change compte.",
                        "Recalculer la pire chute en USD et comparer.")
        ecart = round(m["pire_chute_pct"] - usd, 1)
        f = d.ajouter_fait(f"Pire chute de {ticker} en USD (sans conversion)", usd, "%", "FAIT", "Yahoo Finance",
                           "Même calcul, sans conversion en CAD.")
        obj.resolue = True
        obj.reponse = (f"Recalcul fait ({f.id}) : {usd} % en USD contre {m['pire_chute_pct']} % en CAD "
                       f"(écart de {ecart} point(s)). On garde la mesure en CAD.")
        d.objections.append(obj)

    if not m["recupere"]:
        obj = Objection(f"O-{len(d.objections) + 1}", ids["recuperation"],
                        "Le sommet n'est pas retrouvé : le temps de récupération n'est pas connu, il n'est pas nul.",
                        "Utiliser le temps écoulé depuis le creux comme borne minimale.")
        obj.resolue = True
        obj.reponse = (f"Le Gardien utilise {m['annees_depuis_creux']} an(s) comme minimum : la récupération réelle "
                       "sera au moins aussi longue.")
        d.objections.append(obj)

    if len(d.objections) < MAX_OBJECTIONS:
        obj = Objection(f"O-{len(d.objections) + 1}", ids["chute"],
                        "La fenêtre ne couvre que 5 ans. Une crise plus forte (2008, 2020) n'y figure pas.",
                        "Marquer la pire chute comme borne observée, pas comme pire cas possible.")
        obj.resolue = True
        obj.reponse = "Limite ajoutée au texte final : la pire chute est celle observée sur 5 ans, pas un maximum."
        d.objections.append(obj)

    d.tracer("Sceptique", "objecte et force des recalculs",
             f"{len(d.objections)} objection(s), toutes traitées par recalcul ou par une limite affichée.",
             [o.cible for o in d.objections], debut)
