"""Frontière K1–K4 entre les allocations du profil et le moteur historique B.

Les métriques publiques de B sont déjà en points de pourcentage (tests de
transfert), les poids sont des fractions et le capital est en CAD.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import math

from .donnees import DOSSIER_DONNEES
from .moteurs.allocation import blend
from .moteurs.historique.analytics import (
    MODEL_VERSION, _cad_panel, _period, _wealth, compare_portfolios, drawdowns, validate_weights,
)
from .moteurs.historique.datasets import DataError, load_dataset
from .profil import normaliser_portefeuille

POLITIQUE = "achat-conservation, grille commune des séances, CAD, change daté au plus tard du jour"
METRIQUES = {
    "pire_chute_pct": "max_drawdown_pct",
    "volatilite_pct": "volatility_pct",
    "rendement_annualise_pct": "cagr_pct",
    "valeur_finale_cad": "ending_value_cad",
}


class _DonneesAvecCacheChange:
    """Vue du snapshot immuable : mémorise les réponses exactes de B.fx_on.

    La grille répète les mêmes dates pour chaque montant. Ce cache évite de
    retrier la même série FX, sans remplacer la sélection de date de B.
    """
    def __init__(self, original):
        self._original = original
        self.fx_on = lru_cache(maxsize=4096)(original.fx_on)

    def __getattr__(self, nom):
        return getattr(self._original, nom)


@lru_cache(maxsize=1)
def jeu_donnees():
    """Même chemin et même cycle de chargement que donnees.py ; aucun réseau."""
    return _DonneesAvecCacheChange(load_dataset(DOSSIER_DONNEES))


@lru_cache(maxsize=512)
def _comparer(poids: tuple, ticker: str, montant: float, capital: float) -> dict:
    """Le cache dépend de l'allocation et du montant, jamais de l'horizon.

    Un appel au moteur pour les deux bras. Le résultat mis en cache reste privé :
    ni les identifiants de faits ni les modifications du client ne le contaminent.
    """
    avant = dict(poids)
    apres = blend(avant, ticker, montant / capital)
    resultat = compare_portfolios(
        [{"id": "avant", "weights": avant}, {"id": "apres", "weights": apres}],
        capital_cad=capital, dataset=jeu_donnees(),
    )
    bras = {
        nom: {cle: option["metrics"][source] for cle, source in METRIQUES.items()}
        for nom, option in zip(("avant", "apres"), resultat["options"])
    }
    ecart = round(bras["apres"]["pire_chute_pct"] - bras["avant"]["pire_chute_pct"], 6)
    meta = resultat["meta"]
    return {
        "disponible": True, "raison": None, "moteur": "historique-B",
        "version_moteur": MODEL_VERSION, "politique": POLITIQUE,
        "fenetre": {"debut": meta["start"], "fin": meta["end"], "observations": meta["observations"]},
        "poids_avant": avant, "poids_apres": apres, **bras,
        "ecarts": {
            "pire_chute_pts": ecart,
            "volatilite_pts": round(bras["apres"]["volatilite_pct"] - bras["avant"]["volatilite_pct"], 6),
            "sens_pire_chute": "aggrave" if ecart < 0 else "ameliore" if ecart > 0 else "neutre",
        },
        # Les avertissements propres aux instruments (crypto, FNB, ESGV)
        # complètent les limites communes sans les remplacer.
        "limites": list(dict.fromkeys(meta["limitations"] + [
            limite for option in resultat["options"] for limite in option["warnings"]
        ])),
        "faits": {},
    }


@lru_cache(maxsize=128)
def _panneau(jeu, tickers: tuple):
    return _cad_panel(jeu, tickers, _period(jeu.calendar, None, None))[0]


@lru_cache(maxsize=8192)
def _baisse(jeu, poids: tuple, capital: float) -> float:
    """Sous-calcul de B pour chercher un montant, sans scénarios ni restitution.

    Mêmes validate_weights, _cad_panel, _wealth et drawdowns que compare_portfolios.
    Conversion de la fraction de drawdowns en points, comme B._metrics.
    L'égalité avec les métriques complètes est testée ; aucune formule nouvelle.
    """
    allocation = validate_weights(dict(poids))
    valeurs = _wealth(allocation, _panneau(jeu, tuple(allocation)), capital)
    return round(min(drawdowns(valeurs)) * 100, 6)


def _comparer_pertes(poids: tuple, ticker: str, montant: float, capital: float) -> dict:
    jeu = jeu_donnees()
    avant = _baisse(jeu, poids, capital)
    apres = _baisse(jeu, tuple(sorted(blend(dict(poids), ticker, montant / capital).items())), capital)
    ecart = round(apres - avant, 6)
    return {"disponible": True, "avant": {"pire_chute_pct": avant}, "apres": {"pire_chute_pct": apres},
            "ecarts": {"pire_chute_pts": ecart,
                       "sens_pire_chute": "aggrave" if ecart < 0 else "ameliore" if ecart > 0 else "neutre"}}


def _avec_entrees(profil: dict, demande: dict, calcul) -> dict:
    """Validation commune aux mesures complètes et au sous-calcul de recherche."""
    try:
        poids, origine = normaliser_portefeuille(profil.get("portefeuille_actuel"))
        if poids is None:
            return {"disponible": False, "raison": "Le portefeuille actuel est inconnu."}
        capital, montant = profil.get("epargne_totale_cad"), demande.get("montant_cad")
        for valeur in (capital, montant):
            if isinstance(valeur, bool) or not isinstance(valeur, (int, float)) or not math.isfinite(valeur):
                raise ValueError("L'épargne et le montant doivent être des nombres finis en CAD.")
        if capital <= 0 or montant < 0:
            raise ValueError("L'épargne doit être positive et le montant ne peut pas être négatif.")
        if montant > capital:
            raise ValueError("Le montant dépasse l'épargne totale.")
        ticker = demande.get("ticker")
        if not isinstance(ticker, str) or not ticker:
            raise ValueError("Le symbole du placement demandé est manquant.")
        # Valider les symboles exacts de C avant la normalisation propre à B,
        # y compris une ligne de poids nul : aucun symbole inconnu n'est masqué.
        inconnus = sorted((set(poids) | {ticker}) - set(jeu_donnees().assets))
        if inconnus:
            raise DataError("Symboles absents du jeu de données : " + ", ".join(inconnus))
        if capital > 1e12:  # même domaine que compare_portfolios, y compris pour le sous-calcul
            raise DataError("Le capital fictif doit être compris entre 0 et 10¹² CAD.")
        resultat = deepcopy(calcul(tuple(sorted(poids.items())), ticker, montant, capital))
        resultat["origine_poids"] = origine
        return resultat
    except (DataError, ValueError, TypeError, OverflowError) as exc:
        return {"disponible": False, "raison": str(exc)}
    except OSError:
        return {"disponible": False, "raison": "Les fichiers du jeu de données ne sont pas lisibles."}


def comparer(profil: dict, demande: dict) -> dict:
    """Dictionnaire K3 ; un seul appel complet à B pour les deux bras."""
    return _avec_entrees(profil, demande, _comparer)


def comparer_pertes(profil: dict, demande: dict) -> dict:
    """Mesures de perte seules pour la recherche ; ne remplace jamais K3 dans le dossier."""
    return _avec_entrees(profil, demande, _comparer_pertes)
