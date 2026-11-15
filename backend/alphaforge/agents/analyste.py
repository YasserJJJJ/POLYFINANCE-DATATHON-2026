"""Analyste : choisit les mesures utiles et appelle les outils de calcul.

Chaque résultat devient un fait F-n dans le registre. Le LLM (à brancher)
pourra choisir quelles comparaisons ajouter ; les chiffres viennent toujours
des outils.
"""
from __future__ import annotations

import time

from .. import calculs
from ..donnees import FENETRE, SOURCE_FX, SOURCE_PRIX, controle_qualite, info_actif
from ..dossier import Dossier
from ..format import dollars

REFERENCE = "XIU.TO"  # marché canadien large, pour donner un ordre de grandeur


def mesures_actif(ticker: str, portefeuille: list[str] | None = None) -> dict:
    """Les mesures dont le Gardien a besoin, pour n'importe quel actif (sans créer de faits)."""
    info = info_actif(ticker)
    pc = calculs.pire_chute(ticker)
    return {**pc, "volatilite_pct": calculs.volatilite_annualisee(ticker),
            "rendement_annualise_pct": calculs.rendement_annualise(ticker), "secteur": info["sector"],
            "asset_class": info["asset_class"], "devise": info["currency"],
            "correlations": {t: calculs.correlation(ticker, t) for t in (portefeuille or []) if t != ticker},
            "qualite": controle_qualite(ticker)}


def executer(d: Dossier) -> None:
    debut = time.perf_counter()
    ticker = d.demande["ticker"]
    info = info_actif(ticker)
    d.qualite_donnees = controle_qualite(ticker)
    d.tracer("Contrôle données", "7 contrôles avant calcul",
             f"{sum(c['statut'] == 'ok' for c in d.qualite_donnees)}/{len(d.qualite_donnees)} contrôles réussis "
             f"pour {ticker}.", debut=debut)

    debut = time.perf_counter()
    periode = f"du {FENETRE[0]} au {FENETRE[1]}"
    methode_cad = "adj_close" + (", converti en CAD (taux BdC du jour)" if info["currency"] == "USD" else "")
    ids: dict[str, str] = {}

    ids["secteur"] = d.ajouter_fait(f"Secteur de {info['name']}", info["sector"], "", "FAIT",
                                    "assets_universe.csv (jeu de départ)", "Lu tel quel", "lu").id
    pc = calculs.pire_chute(ticker)
    ids["chute"] = d.ajouter_fait(f"Pire chute de {ticker}", pc["pire_chute_pct"], "%", "FAIT", SOURCE_PRIX,
                                  f"Baisse maximale sommet → creux {periode}, {methode_cad}. "
                                  f"Sommet {pc['date_sommet']}, creux {pc['date_creux']}.").id
    if pc["recupere"]:
        ids["recuperation"] = d.ajouter_fait(f"Temps pour retrouver le sommet ({ticker})", pc["recuperation_annees"],
                                             "an(s)", "FAIT", SOURCE_PRIX,
                                             f"Du creux ({pc['date_creux']}) au retour au sommet ({pc['date_retour']}).").id
    else:
        ids["recuperation"] = d.ajouter_fait(f"Sommet non retrouvé ({ticker})", pc["annees_depuis_creux"], "an(s)",
                                             "FAIT", SOURCE_PRIX,
                                             f"Au {FENETRE[1]}, le sommet du {pc['date_sommet']} n'est pas retrouvé.").id
    vol = calculs.volatilite_annualisee(ticker)
    ids["volatilite"] = d.ajouter_fait(f"Volatilité annualisée de {ticker}", vol, "%/an", "FAIT", SOURCE_PRIX,
                                       f"Écart-type des rendements log quotidiens × √{365 if info['asset_class'] == 'crypto' else 252}, {periode}.").id
    rend = calculs.rendement_annualise(ticker)
    ids["rendement"] = d.ajouter_fait(f"Rendement annualisé passé de {ticker}", rend, "%/an", "FAIT", SOURCE_PRIX,
                                      f"Taux de croissance annuel composé {periode}, en CAD. "
                                      "Le passé ne prédit pas le futur.").id
    p12 = calculs.pire_annee_glissante(ticker)
    ids["pire12"] = d.ajouter_fait(f"Pire période de 12 mois ({ticker})", p12["pire_12_mois_pct"], "%", "FAIT",
                                   SOURCE_PRIX, f"Rendements sur 52 semaines glissantes, fin {p12['fin_periode']}. "
                                                f"{p12['part_periodes_negatives_pct']} % des périodes de 12 mois sont négatives.").id

    montant = d.demande.get("montant_cad") or 0
    perte = calculs.perte_en_dollars(montant, pc["pire_chute_pct"])
    ids["perte"] = d.ajouter_fait("Perte si la pire chute se répétait", perte, "$", "SCENARIO",
                                  f"Calcul sur {ids['chute']}", f"{dollars(montant)} × {pc['pire_chute_pct']} %. "
                                  "Scénario fictif : la prochaine baisse peut être plus forte ou plus faible.").id

    correls = {}
    for t in d.profil.get("portefeuille_actuel", []) or []:
        if t != ticker:
            correls[t] = calculs.correlation(ticker, t)
    if correls:
        ids["correlation"] = d.ajouter_fait(f"Corrélation de {ticker} avec tes placements", correls, "", "FAIT",
                                            SOURCE_PRIX, "Corrélation des rendements hebdomadaires (vendredi), en CAD.").id

    if ticker != REFERENCE:
        ref = calculs.pire_chute(REFERENCE)
        ids["reference"] = d.ajouter_fait(f"Pour comparer : pire chute de {REFERENCE} (marché canadien)",
                                          ref["pire_chute_pct"], "%", "FAIT", SOURCE_PRIX, f"Même méthode, {periode}.").id

    d.demande["mesures"] = {**pc, "volatilite_pct": vol, "rendement_annualise_pct": rend, "secteur": info["sector"],
                            "asset_class": info["asset_class"], "devise": info["currency"], "correlations": correls,
                            "qualite": d.qualite_donnees}
    d.demande["ids_faits"] = ids
    d.tracer("Analyste", "appelle les outils de calcul",
             f"{len(d.faits)} faits produits (pire chute {pc['pire_chute_pct']} %, volatilité {vol} %/an). "
             f"Sources : prix Yahoo Finance{', ' + SOURCE_FX if info['currency'] == 'USD' else ''}.",
             list(ids.values()), debut)
