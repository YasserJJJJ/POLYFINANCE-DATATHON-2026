"""Profil : deux jauges séparées, tolérance (ce qu'on veut risquer) et capacité
(ce qu'on peut se permettre de perdre). On retient la plus basse des deux,
comme le prévoient les Réformes axées sur le client (ACVM / OCRCVM).

Tous les barèmes ci-dessous sont des HYPOTHÈSES de l'équipe, affichées comme
telles dans l'interface. Propriétaire des seuils : Gardien (à valider).
"""
from __future__ import annotations

# 3 questions inspirées de l'échelle de tolérance de Grable & Lytton (1999).
QUESTIONS_TOLERANCE = [
    {
        "id": "q_amis",
        "texte": "Comment tes proches te décriraient-ils face au risque ?",
        "choix": [("J'évite le risque", 0), ("Prudent·e", 33), ("Je prends des risques calculés", 67),
                  ("J'aime prendre des risques", 100)],
        "source": "Grable & Lytton (1999), item 1, adapté",
    },
    {
        "id": "q_mot",
        "texte": "Quand tu penses au mot « risque », qu'est-ce qui te vient en premier ?",
        "choix": [("Une perte", 0), ("De l'incertitude", 33), ("Une occasion", 67), ("Un frisson", 100)],
        "source": "Grable & Lytton (1999), item 4, adapté",
    },
    {
        "id": "q_chute",
        "texte": "Ton placement perd 20 % en 3 mois. Que fais-tu ?",
        "choix": [("Je vends tout", 0), ("Je vends une partie", 33), ("Je ne touche à rien", 67),
                  ("J'en rachète", 100)],
        "source": "Grable & Lytton (1999), item 10, adapté (mise en situation)",
    },
]


def score_tolerance(reponses: dict[str, int] | None, defaut: float | None = None) -> float | None:
    if reponses:
        valeurs = [v for v in reponses.values() if v is not None]
        if valeurs:
            return round(sum(valeurs) / len(valeurs), 0)
    return defaut


def score_capacite(p: dict) -> tuple[float | None, list[str]]:
    """Barème transparent : chaque point ajouté ou retiré est expliqué."""
    horizon = p.get("horizon_ans")
    if horizon is None:
        return None, ["Horizon inconnu : capacité non calculable."]
    score, raisons = 50.0, []
    if horizon >= 10:
        score += 25; raisons.append("Horizon de 10 ans ou plus : +25")
    elif horizon >= 5:
        score += 10; raisons.append("Horizon de 5 à 10 ans : +10")
    elif horizon >= 3:
        score -= 10; raisons.append("Horizon de 3 à 5 ans : -10")
    else:
        score -= 25; raisons.append("Horizon de moins de 3 ans : -25")
    if p.get("revenu_stable") is True:
        score += 10; raisons.append("Revenu stable : +10")
    elif p.get("revenu_stable") is False:
        score -= 10; raisons.append("Revenu instable : -10")
    if p.get("fonds_urgence") is True:
        score += 10; raisons.append("Fonds d'urgence : +10")
    elif p.get("fonds_urgence") is False:
        score -= 15; raisons.append("Pas de fonds d'urgence : -15")
    if p.get("dettes_importantes"):
        score -= 10; raisons.append("Dettes importantes : -10")
    retrait = p.get("retrait_prevu_ans")
    if retrait is not None and retrait < 3:
        score -= 15; raisons.append("Retrait prévu dans moins de 3 ans : -15")
    return max(0.0, min(100.0, score)), raisons


def perte_max_pct(score: float) -> float:
    """Score 0-100 → baisse de portefeuille supportable (5 % à 40 %)."""
    return round(5 + 0.35 * score, 1)


def seuil_concentration_pct(score: float) -> float:
    """Poids maximal d'un actif très volatil selon le score retenu."""
    if score < 35:
        return 5.0
    if score < 65:
        return 10.0
    return 20.0


def evaluer(p: dict) -> dict:
    tol = score_tolerance(p.get("reponses_tolerance"), p.get("tolerance"))
    cap, raisons = score_capacite(p)
    retenu = None if tol is None or cap is None else min(tol, cap)
    return {
        "tolerance": tol,
        "capacite": cap,
        "capacite_raisons": raisons,
        "score_retenu": retenu,
        "limite": None if retenu is None else ("tolérance" if tol <= cap else "capacité"),
        "perte_max_tolerance_pct": None if tol is None else perte_max_pct(tol),
        "perte_max_capacite_pct": None if cap is None else perte_max_pct(cap),
        "perte_max_retenue_pct": None if retenu is None else perte_max_pct(retenu),
        "seuil_concentration_pct": None if retenu is None else seuil_concentration_pct(retenu),
    }
