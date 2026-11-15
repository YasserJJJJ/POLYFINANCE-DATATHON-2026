"""Gardien : règles explicites, en code. C'est lui qui décide du verdict.

Le LLM n'intervient jamais ici. Chaque règle renvoie un niveau, une explication
et les faits (F-n) qui la soutiennent. Les seuils viennent de profil.py.
"""
from __future__ import annotations

from .dossier import Regle
from .format import dollars
from .profil import evaluer

ORDRE = {"gris": 4, "rouge": 3, "orange": 2, "ok": 1, "non_evaluee": 0}
ETATS = {"gris": "indetermine", "rouge": "incoherent", "orange": "ajustement", "ok": "coherent"}
LIBELLES_ETAT = {
    "coherent": "Cohérent avec ta situation",
    "ajustement": "Cohérent avec un ajustement",
    "incoherent": "Incohérent avec ta situation",
    "indetermine": "Impossible de conclure : il manque une information",
}


def appliquer_regles(profil: dict, demande: dict, m: dict, f: dict | None = None) -> list[Regle]:
    """profil : champs du profil ; demande : ticker, montant_cad ; m : mesures
    calculées ; f : identifiants des faits (pour relier chaque règle à ses preuves)."""
    f = f or {}
    ev = evaluer(profil)
    regles: list[Regle] = []
    epargne = profil.get("epargne_totale_cad")
    montant = demande.get("montant_cad")

    manquants = [nom for nom, v in [("horizon", profil.get("horizon_ans")), ("épargne totale", epargne),
                                    ("montant", montant), ("tolérance", ev["tolerance"])] if v is None]
    if any(c["statut"] == "echec" for c in m.get("qualite", [])):
        manquants.append("données de marché fiables")
    # Valeurs impossibles : on ne conclut pas (sinon division par zéro, ou un montant négatif jugé « cohérent »).
    invalides = [nom for nom, v in [("une épargne totale positive", epargne), ("un montant positif", montant),
                                    ("un horizon d'au moins 1 an", profil.get("horizon_ans"))]
                 if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0
                                       or (nom.startswith("un horizon") and v < 1))]
    if manquants or invalides:
        morceaux = (["Il manque : " + ", ".join(manquants) + "."] if manquants else []) + \
                   (["Il faut " + ", ".join(invalides) + "."] if invalides else [])
        regles.append(Regle("donnees", "Informations essentielles", "gris", " ".join(morceaux)))
        return regles

    poids = montant / epargne
    chute = abs(m["pire_chute_pct"])
    impact = round(poids * chute, 1)

    # 1. Capacité et tolérance de perte
    if impact > ev["perte_max_capacite_pct"]:
        niveau, txt = "rouge", (f"Si ce placement revivait sa pire chute ({m['pire_chute_pct']} %), ton épargne "
                                f"baisserait de {impact} %. Ta capacité de perte est estimée à "
                                f"{ev['perte_max_capacite_pct']} %.")
    elif impact > ev["perte_max_tolerance_pct"]:
        niveau, txt = "orange", (f"La pire chute observée ferait baisser ton épargne de {impact} %. C'est dans ta "
                                 f"capacité ({ev['perte_max_capacite_pct']} %), mais au-delà de ce que tu dis "
                                 f"vouloir risquer ({ev['perte_max_tolerance_pct']} %).")
    else:
        niveau, txt = "ok", (f"La pire chute observée ferait baisser ton épargne de {impact} %, sous ta limite "
                             f"de {ev['perte_max_retenue_pct']} %.")
    regles.append(Regle("capacite", "Perte supportable", niveau, txt, [f.get("chute", "")]))

    # 2. Somme à préserver
    preserver = profil.get("somme_a_preserver_cad")
    if preserver is not None:
        reste = epargne - montant
        ok = reste >= preserver
        regles.append(Regle("preserver", "Somme à préserver", "ok" if ok else "rouge",
                            f"Après ce placement, il resterait {dollars(reste)} hors de ce titre, pour "
                            f"{dollars(preserver)} à préserver."))

    # 3. Exclusions (valeurs)
    exclusions = [e.lower() for e in profil.get("exclusions", [])]
    secteur = str(m.get("secteur", ""))
    if exclusions:
        touche = any(e in secteur.lower() for e in exclusions)
        regles.append(Regle("exclusion", "Respect de tes exclusions", "rouge" if touche else "ok",
                            f"Secteur de l'actif : {secteur}. " + ("Il fait partie de tes exclusions."
                                                                   if touche else "Il n'est pas exclu."),
                            [f.get("secteur", "")]))

    # 4. Retrait prévu avant récupération, sur un actif volatil
    retrait = profil.get("retrait_prevu_ans")
    recup = m.get("recuperation_annees") if m.get("recupere") else None
    if retrait is not None:
        risque = m["volatilite_pct"] > 25 and (recup is None or retrait < recup)
        regles.append(Regle("retrait", "Retrait prévu", "rouge" if risque else "ok",
                            (f"Tu prévois de retirer de l'argent dans {retrait} an(s). Ce placement est volatil "
                             f"({m['volatilite_pct']} %/an) et a mis "
                             + (f"{recup} an(s)" if recup else "plus que la période observée")
                             + " à se remettre de sa pire chute.") if risque else
                            "Le retrait prévu laisse le temps de traverser une baisse comparable.",
                            [f.get("volatilite", ""), f.get("recuperation", "")]))

    # 5. Horizon plus court que le temps de récupération observé
    horizon = profil["horizon_ans"]
    if m.get("recupere"):
        trop_court = horizon < m["recuperation_annees"]
        detail = f"il a fallu {m['recuperation_annees']} an(s) pour revenir au sommet"
    else:
        trop_court = horizon < m["annees_depuis_creux"]
        detail = f"le sommet n'est toujours pas retrouvé {m['annees_depuis_creux']} an(s) après le creux"
    regles.append(Regle("horizon", "Horizon et temps de récupération", "orange" if trop_court else "ok",
                        f"Ton horizon est de {horizon} an(s) ; après la pire chute, {detail}.",
                        [f.get("recuperation", "")]))

    # 6. Concentration sur un actif très volatil
    if m["volatilite_pct"] > 30:
        trop = poids * 100 > ev["seuil_concentration_pct"]
        regles.append(Regle("concentration", "Concentration", "orange" if trop else "ok",
                            f"Ce placement représente {poids * 100:.0f} % de ton épargne. Pour un actif aussi "
                            f"volatil, le seuil retenu pour ton profil est {ev['seuil_concentration_pct']:.0f} %.",
                            [f.get("volatilite", "")]))

    # 7. Coussin de sécurité
    if profil.get("fonds_urgence") is not None:
        regles.append(Regle("coussin", "Fonds d'urgence", "ok" if profil["fonds_urgence"] else "orange",
                            "Tu as un fonds d'urgence." if profil["fonds_urgence"] else
                            "Sans fonds d'urgence, une dépense imprévue pourrait forcer une vente au mauvais moment."))

    # 8. Fausse diversification (si on connaît les placements actuels)
    correl = m.get("correlations") or {}
    deja = demande.get("ticker") and demande.get("ticker") in (profil.get("portefeuille_actuel") or [])
    note_deja = f" Tu détiens déjà {demande['ticker']} : ce placement s'y ajoute." if deja else ""
    if correl:
        forts = {t: c for t, c in correl.items() if c >= 0.8}
        t_max, c_max = max(correl.items(), key=lambda kv: kv[1])
        regles.append(Regle("diversification", "Diversification réelle", "orange" if forts else "ok",
                            (("Très corrélé à ce que tu détiens déjà : " + ", ".join(f"{t} ({c})" for t, c in forts.items())
                              + ". Ça ne diversifie pas.") if forts else
                             (f"Corrélation la plus forte avec tes placements : {t_max} ({c_max}), sous le seuil de 0,8 "
                              "retenu par l'équipe pour parler de fausse diversification.")) + note_deja,
                            [f.get("correlation", "")]))
    else:
        regles.append(Regle("diversification", "Diversification réelle", "non_evaluee",
                            (f"Tu ne détiens que {demande['ticker']} : diversification non évaluée." if deja else
                             "Placements actuels inconnus : diversification non évaluée.")))
    return regles


def verdict(regles: list[Regle]) -> dict:
    pire = max((r.niveau for r in regles), key=lambda n: ORDRE[n])
    etat = ETATS.get(pire, "coherent")
    evaluees = [r for r in regles if r.niveau in ("ok", "orange", "rouge")]
    respectees = sum(r.niveau == "ok" for r in evaluees)
    return {"etat": etat, "libelle": LIBELLES_ETAT[etat], "respectees": respectees, "evaluees": len(evaluees)}


FRACTIONS = [1, 0.75, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05]


def grille_bascule(profil: dict, demande: dict, m: dict) -> dict:
    """Recalcule le verdict sur une grille montant × horizon (sans LLM).
    Sert aux curseurs de bascule de l'interface et au plus petit ajustement."""
    base_h = profil.get("horizon_ans") or 1
    horizons = list(range(1, max(21, int(base_h) + 6)))
    montant = demande["montant_cad"]
    montants = [round(montant * fr) for fr in FRACTIONS]
    cases = []
    for mt in montants:
        for h in horizons:
            r = appliquer_regles({**profil, "horizon_ans": h}, {**demande, "montant_cad": mt}, m)
            cases.append({"montant_cad": mt, "horizon_ans": h, "etat": verdict(r)["etat"]})
    return {"montants": montants, "horizons": horizons, "cases": cases}


RANG = {"coherent": 0, "ajustement": 1, "incoherent": 2, "indetermine": 3}
PAS_MONTANT = 100  # précision du montant ajusté, en $


def _etat(profil: dict, demande: dict, m: dict) -> str:
    return verdict(appliquer_regles(profil, demande, m))["etat"]


def _montant_exact(profil: dict, demande: dict, m: dict, bon: float, mauvais: float, cible: str) -> int:
    """Plus grand montant (au pas de 100 $) entre `bon` (atteint la cible) et `mauvais` (ne l'atteint pas).
    La grille est monotone en montant (vérifiée par les tests), donc une recherche par dichotomie suffit."""
    bas, haut = int(bon // PAS_MONTANT), int(mauvais // PAS_MONTANT)
    while haut - bas > 1:
        milieu = (bas + haut) // 2
        if _etat(profil, {**demande, "montant_cad": milieu * PAS_MONTANT}, m) == cible:
            bas = milieu
        else:
            haut = milieu
    return max(bas * PAS_MONTANT, int(bon))


def plus_petit_ajustement(profil: dict, demande: dict, m: dict) -> dict | None:
    """Plus petit changement (montant d'abord, puis horizon) qui rend la demande cohérente,
    sinon qui l'améliore au moins d'un état. Un « ajustement » qui ne change pas l'état n'en est pas un."""
    base_h = profil["horizon_ans"]
    actuel = _etat(profil, demande, m)
    montant = demande["montant_cad"]
    for cible in ("coherent", "ajustement"):
        if RANG[cible] >= RANG[actuel]:
            continue
        precedent = montant
        for fr in FRACTIONS[1:]:
            essai = round(montant * fr)
            if _etat(profil, {**demande, "montant_cad": essai}, m) == cible:
                exact = _montant_exact(profil, demande, m, essai, precedent, cible)
                return {"changement": {"montant_cad": exact}, "etat": cible}
            precedent = essai
        for k in range(1, 6):
            if _etat({**profil, "horizon_ans": base_h + k}, demande, m) == cible:
                return {"changement": {"horizon_ans": base_h + k}, "etat": cible}
    return None
