"""Analyste : choisit les mesures utiles et appelle les outils de calcul.

Chaque résultat devient un fait F-n dans le registre. Le LLM (à brancher)
pourra choisir quelles comparaisons ajouter ; les chiffres viennent toujours
des outils.
"""
from __future__ import annotations

import math
import time

import pandas as pd

from .. import calculs, portefeuille
from ..donnees import FENETRE, SOURCE_FX, SOURCE_PRIX, controle_qualite, info_actif, univers
from ..dossier import Dossier
from ..format import dollars, fr
from ..gardien import (CLASSES_TITRE_UNIQUE, RETRAIT_PROCHE_ANS, SEUIL_CORRELATION, SEUIL_TRES_VOLATIL,
                       SEUIL_VOLATIL_RETRAIT)
from ..profil import symboles_portefeuille
from ..sources import references_de

REFERENCE = "XIU.TO"  # marché canadien large, pour donner un ordre de grandeur


def mesures_actif(ticker: str, portefeuille: list[str] | None = None) -> dict:
    """Les mesures dont le Gardien a besoin, pour n'importe quel actif (sans créer de faits)."""
    info = info_actif(ticker)
    pc = calculs.pire_chute(ticker)
    return {**pc, "volatilite_pct": calculs.volatilite_annualisee(ticker),
            "rendement_annualise_pct": calculs.rendement_annualise(ticker), "secteur": info["sector"],
            "asset_class": info["asset_class"], "devise": info["currency"],
            "correlations": {t: calculs.correlation(ticker, t) for t in symboles_portefeuille(portefeuille)
                             if t != ticker and t in univers().index},
            "qualite": controle_qualite(ticker)}


def _faits_hypotheses(d: Dossier, ids: dict, avec_correlations: bool, volatilite: float, asset_class: str) -> None:
    """Les seuils et barèmes de l'équipe entrent au registre comme faits HYPOTHESE : ils sont visibles, chiffrés,
    sourcés et dits comme des choix, au lieu de rester cachés dans le texte des règles."""
    ev = d.profil.get("evaluation") or {}
    origine = "Barème de l'équipe (backend/alphaforge/profil.py), publié et modifiable"
    if ev.get("perte_max_retenue_pct") is not None:
        ids["h_perte"] = d.ajouter_fait(
            "Perte supportable retenue pour ton profil (hypothèse de l'équipe)", ev["perte_max_retenue_pct"], "%",
            "HYPOTHESE", origine,
            f"5 + 0,35 × score retenu. Score retenu = le plus bas entre tolérance ({fr(ev['tolerance'])}) et capacité "
            f"({fr(ev['capacite'])}), soit {fr(ev['score_retenu'])} (limite : {ev['limite']}).").id
    if ev.get("perte_max_capacite_pct") is not None:
        ids["h_capacite"] = d.ajouter_fait(
            "Capacité de perte selon ta situation (hypothèse de l'équipe)", ev["perte_max_capacite_pct"], "%",
            "HYPOTHESE", origine, "5 + 0,35 × score de capacité. Détail du score : "
            + " ; ".join(ev.get("capacite_raisons") or []) + ".").id
    tres_volatil = volatilite > SEUIL_TRES_VOLATIL
    if ev.get("seuil_concentration_pct") is not None:
        ids["h_concentration"] = d.ajouter_fait(
            "Part maximale de l'épargne dans un actif très volatil, pour ton profil (hypothèse de l'équipe)",
            ev["seuil_concentration_pct"], "%", "HYPOTHESE", origine,
            f"5 + 0,15 × score retenu ({fr(ev['score_retenu'])}), soit de 5 % à 20 % : une fonction continue, "
            "pour qu'un point de score ne fasse pas basculer le verdict.").id
    if not tres_volatil and asset_class in CLASSES_TITRE_UNIQUE and ev.get("seuil_titre_unique_pct") is not None:
        ids["h_titre"] = d.ajouter_fait(
            "Part maximale de l'épargne dans un seul titre moins volatil, pour ton profil (hypothèse de l'équipe)",
            ev["seuil_titre_unique_pct"], "%", "HYPOTHESE", origine,
            "Deux fois le seuil des actifs très volatils : une seule entreprise peut chuter seule, même si son prix "
            "bouge moins que la moyenne des actifs risqués.").id
    retrait = d.profil.get("retrait_prevu_ans")
    if tres_volatil and retrait is not None and retrait <= RETRAIT_PROCHE_ANS:
        ids["h_retrait_proche"] = d.ajouter_fait(
            "Retrait jugé proche (hypothèse de l'équipe)", RETRAIT_PROCHE_ANS, "an(s)", "HYPOTHESE", origine,
            f"Un retrait prévu dans {RETRAIT_PROCHE_ANS} ans ou moins rend incohérente une concentration au-delà du "
            "seuil sur un actif très volatil : il resterait peu de temps pour attendre une remontée.").id
    ids["h_volatil"] = d.ajouter_fait(
        "Seuil « actif très volatil » (hypothèse de l'équipe)", SEUIL_TRES_VOLATIL, "%/an", "HYPOTHESE", origine,
        f"Au-delà de {SEUIL_TRES_VOLATIL} %/an, la règle de concentration s'applique ; au-delà de "
        f"{SEUIL_VOLATIL_RETRAIT} %/an, un retrait prévu avant la récupération est jugé risqué.").id
    if avec_correlations:
        ids["h_correlation"] = d.ajouter_fait(
            "Seuil de fausse diversification (hypothèse de l'équipe)", SEUIL_CORRELATION, "", "HYPOTHESE", origine,
            "À partir de cette corrélation hebdomadaire avec un placement déjà détenu, le nouveau placement ne "
            "diversifie pas.").id


def _faits_portefeuille(d: Dossier, ids: dict) -> None:
    """Chaque nombre de K3 a sa preuve ; les mesures de C restent distinctes."""
    c = d.comparaison = portefeuille.comparer(d.profil, d.demande)
    if not c["disponible"]:
        return
    methode = (f"Moteur historique-B ({c['version_moteur']}) : {c['politique']}. "
               f"Du {c['fenetre']['debut']} au {c['fenetre']['fin']}, "
               f"{c['fenetre']['observations']} observations. "
               "Prix ajustés ; métriques en points de pourcentage. "
               "Aucune soustraction avec les mesures d'un titre du moteur C.")

    def fait(cle, libelle, valeur, unite, type_, detail="", justification="portefeuille"):
        identifiant = d.ajouter_fait(
            libelle, valeur, unite, type_, "Jeu de départ AlphaForge et moteur historique B",
            methode + (" " + detail if detail else ""), references=references_de(justification),
        ).id
        c["faits"][cle] = ids[cle] = identifiant

    declare = c["origine_poids"] == "declare"
    if not declare:
        fait("h_equiponderation", "Poids inconnus : hypothèse d'équipondération",
             c["poids_avant"], "fraction", "HYPOTHESE",
             "Chaque symbole distinct reçoit la même fraction de l'épargne ; à faire confirmer.",
             "h_equiponderation")
    fait("fenetre_portefeuille", "Fenêtre commune de comparaison", c["fenetre"], "", "FAIT")
    fait("poids_avant", "Allocation actuelle utilisée", c["poids_avant"], "fraction",
         "FAIT" if declare else "HYPOTHESE", "Poids déclarés." if declare else "Poids supposés égaux.")
    fait("poids_apres", "Allocation après ajout du placement", c["poids_apres"], "fraction", "SCENARIO",
         "Ajout blend de A : chaque poids initial × (1 − montant/épargne), puis ajout de montant/épargne au titre.",
         "allocation-ajout")
    libelles = {
        "pire_chute_pct": ("pire_chute", "Pire baisse du portefeuille", "%"),
        "volatilite_pct": ("volatilite", "Volatilité du portefeuille", "%/an"),
        "rendement_annualise_pct": ("rendement", "Rendement annualisé passé du portefeuille", "%/an"),
        "valeur_finale_cad": ("valeur_finale", "Valeur finale rétrospective du portefeuille", "$"),
    }
    for bras in ("avant", "apres"):
        for mesure, (cle, libelle, unite) in libelles.items():
            fait(f"{bras}_{cle}", f"{libelle} {'avant' if bras == 'avant' else 'après'} la demande",
                 c[bras][mesure], unite,
                 ("FAIT" if declare else "HYPOTHESE") if bras == "avant" else "SCENARIO")
    fait("ecart_pire_chute", "Écart de pire baisse : après moins avant",
         c["ecarts"]["pire_chute_pts"], "points", "SCENARIO",
         f"Sens calculé : {c['ecarts']['sens_pire_chute']}. Valeurs négatives : un écart négatif aggrave la baisse.")
    fait("ecart_volatilite", "Écart de volatilité : après moins avant",
         c["ecarts"]["volatilite_pts"], "points", "SCENARIO")
    fait("h_attribution", "Attribution de la perte supportable (hypothèse de l'équipe)",
         "Un dépassement antérieur de capacité ne rend pas la demande rouge si elle n'aggrave pas la pire baisse.",
         "", "HYPOTHESE", "La tolérance reste évaluée ; les seuils restent inchangés.", "h_attribution")
    fait("h_non_monotonie", "Montant et risque : monotonie conditionnelle (hypothèse de l'équipe)",
         "Quand une demande diversifie le portefeuille et améliore sa pire baisse, un montant plus élevé "
         "peut donner un meilleur verdict. Chaque case est jugée séparément ; ce constat n'est pas un conseil.",
         "", "HYPOTHESE",
         f"Comparaison liée : avant {c['faits']['avant_pire_chute']}, après {c['faits']['apres_pire_chute']}, "
         f"écart {c['faits']['ecart_pire_chute']}. Décision du porteur, révision de l'invariant 7.",
         "h_non_monotonie")
    fait("limites_portefeuille", "Limites de la comparaison historique", c["limites"], "", "FAIT")


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
    usd = info["currency"] == "USD"
    methode_cad = ("adj_close (dividendes réinvestis, fractionnements appliqués)"
                   + (", converti en CAD au taux BdC du jour, ou au dernier taux publié (fins de semaine, fériés)"
                      if usd else ""))
    change = ", en CAD (effet du change USD/CAD inclus)" if usd else ", en CAD"
    ids: dict[str, str] = {}

    ids["secteur"] = d.ajouter_fait(f"Secteur de {info['name']}", info["sector"], "", "FAIT",
                                    "assets_universe.csv (jeu de départ)", "Lu tel quel", "lu").id
    pc = calculs.pire_chute(ticker)
    ids["chute"] = d.ajouter_fait(f"Pire chute de {ticker}", pc["pire_chute_pct"], "%", "FAIT", SOURCE_PRIX,
                                  f"Baisse maximale sommet → creux {periode}, {methode_cad}. "
                                  f"Sommet {pc['date_sommet']}, creux {pc['date_creux']}.").id
    if pc["recupere"]:
        sous_l_eau = round((pd.Timestamp(pc["date_retour"]) - pd.Timestamp(pc["date_sommet"])).days / 365.25, 1)
        ids["recuperation"] = d.ajouter_fait(f"Temps entre le creux et le retour au sommet ({ticker})",
                                             pc["recuperation_annees"], "an(s)", "FAIT", SOURCE_PRIX,
                                             f"Du creux ({pc['date_creux']}) au retour au sommet ({pc['date_retour']}). "
                                             f"Depuis le sommet ({pc['date_sommet']}), le prix est resté sous son "
                                             f"sommet {fr(sous_l_eau)} an(s).").id
    else:
        ids["recuperation"] = d.ajouter_fait(f"Sommet non retrouvé ({ticker})", pc["annees_depuis_creux"], "an(s)",
                                             "FAIT", SOURCE_PRIX,
                                             f"Au {FENETRE[1]}, le sommet du {pc['date_sommet']} n'est pas retrouvé.").id
    vol = calculs.volatilite_annualisee(ticker)
    ids["volatilite"] = d.ajouter_fait(f"Volatilité annualisée de {ticker}", vol, "%/an", "FAIT", SOURCE_PRIX,
                                       f"Écart-type des rendements log quotidiens × √{365 if info['asset_class'] == 'crypto' else 252}"
                                       f"{change}, {periode}.").id
    rend = calculs.rendement_annualise(ticker)
    # Erreur type d'une moyenne annuelle estimée sur T années ≈ σ / √T (approximation) : sur 5 ans, elle est
    # grande. On l'affiche pour que le rendement passé ne soit jamais lu comme une promesse (DeMiguel et al., 2009).
    annees = (pd.Timestamp(FENETRE[1]) - pd.Timestamp(FENETRE[0])).days / 365.25
    erreur_type = round(vol / math.sqrt(annees), 1)
    ids["rendement"] = d.ajouter_fait(f"Rendement annualisé passé de {ticker}", rend, "%/an", "FAIT", SOURCE_PRIX,
                                      f"Taux de croissance annuel composé {periode}{change}, dividendes réinvestis. "
                                      f"Erreur type de cette moyenne ≈ volatilité / √années = {fr(erreur_type)} points : "
                                      f"la vraie moyenne peut s'écarter d'environ ± {fr(round(2 * erreur_type, 1))} points. "
                                      "Le passé ne prédit pas le futur ; ce chiffre ne sert jamais au verdict.").id
    p12 = calculs.pire_annee_glissante(ticker)
    ids["pire12"] = d.ajouter_fait(f"Pire période de 52 semaines ({ticker}, cours du vendredi)",
                                   p12["pire_12_mois_pct"], "%", "FAIT",
                                   SOURCE_PRIX, f"Rendements sur 52 semaines glissantes, cours du vendredi, fin "
                                                f"{p12['fin_periode']}. Mesure hebdomadaire : la pire baisse sur 12 mois "
                                                "de cotations quotidiennes peut être plus forte. "
                                                f"{fr(p12['part_periodes_negatives_pct'])} % des périodes de 12 mois sont négatives.").id

    montant = d.demande.get("montant_cad") or 0
    perte = calculs.perte_en_dollars(montant, pc["pire_chute_pct"])
    ids["perte"] = d.ajouter_fait("Perte si la pire chute se répétait", perte, "$", "SCENARIO",
                                  f"Calcul sur {ids['chute']}", f"{dollars(montant)} × {pc['pire_chute_pct']} %. "
                                  "Scénario fictif : la prochaine baisse peut être plus forte ou plus faible.").id

    correls, inconnus = {}, []
    for t in symboles_portefeuille(d.profil.get("portefeuille_actuel")):
        if t == ticker:
            continue
        try:
            correls[t] = calculs.correlation(ticker, t)
        except KeyError:      # placement détenu absent du jeu de données : on l'ignore et on le dit
            inconnus.append(t)
    if correls:
        ids["correlation"] = d.ajouter_fait(f"Corrélation de {ticker} avec tes placements", correls, "", "FAIT",
                                            SOURCE_PRIX, "Corrélation des rendements hebdomadaires (vendredi), en CAD.").id

    if ticker != REFERENCE:
        ref = calculs.pire_chute(REFERENCE)
        ids["reference"] = d.ajouter_fait(f"Pour comparer : pire chute de {REFERENCE} (marché canadien)",
                                          ref["pire_chute_pct"], "%", "FAIT", SOURCE_PRIX, f"Même méthode, {periode}.").id

    _faits_hypotheses(d, ids, bool(correls), vol, info["asset_class"])
    # Chaque fait est relié à ses sources : données, règle de calcul, base théorique ou réglementaire (sources.py).
    for cle, fid in ids.items():
        d.fait(fid).references = references_de(cle)

    _faits_portefeuille(d, ids)
    d.demande["mesures"] = {**pc, "volatilite_pct": vol, "rendement_annualise_pct": rend, "secteur": info["sector"],
                            "asset_class": info["asset_class"], "devise": info["currency"], "correlations": correls,
                            "qualite": d.qualite_donnees}
    d.demande["ids_faits"] = ids
    d.tracer("Analyste", "appelle les outils de calcul",
             f"{len(d.faits)} faits produits (pire chute {pc['pire_chute_pct']} %, volatilité {vol} %/an). "
             f"Sources : prix Yahoo Finance{', ' + SOURCE_FX if info['currency'] == 'USD' else ''}."
             + (f" Placement(s) détenu(s) sans données, ignoré(s) : {', '.join(inconnus)}." if inconnus else ""),
             list(ids.values()), debut)
