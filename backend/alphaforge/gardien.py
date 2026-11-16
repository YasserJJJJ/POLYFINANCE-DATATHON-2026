"""Gardien : règles explicites, en code. C'est lui qui décide du verdict.

Le LLM n'intervient jamais ici. Chaque règle renvoie un niveau, une explication
et les faits (F-n) qui la soutiennent. Les seuils viennent de profil.py.
"""
from __future__ import annotations

import math
import os

from . import portefeuille
from .dossier import Regle
from .format import dollars, fr
from .profil import evaluer, symboles_portefeuille
from .sources import references_de

# Seuils de l'équipe (hypothèses, inchangés) : nommés une seule fois pour être affichés comme faits HYPOTHESE.
SEUIL_VOLATIL_RETRAIT = 25      # %/an : au-delà, un retrait avant récupération est risqué
SEUIL_TRES_VOLATIL = 30         # %/an : au-delà, la règle de concentration s'applique
SEUIL_CORRELATION = 0.8         # au-delà, on parle de fausse diversification
RETRAIT_PROCHE_ANS = 5          # retrait dans 5 ans ou moins : une concentration très volatile devient rouge
CLASSES_TITRE_UNIQUE = ("equity", "crypto")  # un seul émetteur : la concentration compte même sous 30 %/an

# Nature de l'explication de chaque règle (affichée comme étiquette) :
# SCENARIO = situation fictive ; HYPOTHESE = repose sur un seuil de l'équipe ; FAIT = constat observé.
TYPE_REGLE = {"capacite": "SCENARIO", "preserver": "SCENARIO", "concentration": "HYPOTHESE",
              "diversification": "HYPOTHESE", "coussin": "HYPOTHESE", "retrait": "HYPOTHESE",
              "horizon": "FAIT", "exclusion": "FAIT", "donnees": "FAIT"}

ORDRE = {"gris": 4, "rouge": 3, "orange": 2, "ok": 1, "non_evaluee": 0}
ETATS = {"gris": "indetermine", "rouge": "incoherent", "orange": "ajustement", "ok": "coherent"}
LIBELLES_ETAT = {
    "coherent": "Cohérent avec ta situation",
    "ajustement": "Cohérent avec un ajustement",
    "incoherent": "Incohérent avec ta situation",
    "indetermine": "Impossible de conclure : il manque une information",
}


# Mots français courants pour les secteurs de assets_universe.csv (l'interface envoie déjà les noms anglais).
SYNONYMES_SECTEURS = {"énergie": "energy", "energie": "energy", "pétrole": "energy", "petrole": "energy",
                      "gaz": "energy", "pipelines": "energy", "cryptoactifs": "crypto", "cryptos": "crypto",
                      "technologies": "information technology", "technologie": "information technology",
                      "finance": "financials", "santé": "health care", "services publics": "utilities"}


# Libellés français des secteurs de assets_universe.csv (affichage seulement ; la comparaison reste en anglais).
SECTEURS_FR = {"Energy": "Énergie", "Crypto asset": "Cryptoactifs", "Financials": "Finance",
               "Information Technology": "Technologies", "Consumer Discretionary": "Consommation discrétionnaire",
               "Health Care": "Santé", "Utilities": "Services publics", "Industrials": "Industrie",
               "Consumer Staples": "Consommation de base", "Communication Services": "Communication",
               "Materials": "Matériaux", "Real Estate": "Immobilier"}


def exclusions_normalisees(profil: dict) -> list[str]:
    """Exclusions en minuscules, sans entrée vide (une chaîne vide excluait tous les secteurs)."""
    sortie = []
    exclusions = profil.get("exclusions") or []
    if isinstance(exclusions, str):
        exclusions = [exclusions]
    for e in exclusions:
        e = str(e).strip().lower()
        if e:
            sortie.append(SYNONYMES_SECTEURS.get(e, e))
    return sortie


def erreurs_entree(profil: dict, demande: dict) -> list[str]:
    """Entrées invalides, à contrôler avant les scores et les calculs de marché."""
    erreurs = []
    champs = [
        ("une épargne totale positive", profil.get("epargne_totale_cad"), 0),
        ("un montant positif", demande.get("montant_cad"), 0),
        ("un horizon d'au moins 1 an", profil.get("horizon_ans"), 1),
        ("une somme à préserver numérique", profil.get("somme_a_preserver_cad"), None),
        ("un retrait prévu numérique", profil.get("retrait_prevu_ans"), None),
        ("une tolérance numérique", profil.get("tolerance"), None),
    ]
    for nom, valeur, minimum in champs:
        if valeur is None:
            continue  # les champs manquants peuvent encore être extraits du texte
        if (isinstance(valeur, bool) or not isinstance(valeur, (int, float))
                or (isinstance(valeur, float) and not math.isfinite(valeur))
                or (minimum is not None and (valeur <= 0 or valeur < minimum))):
            erreurs.append(f"Il faut {nom}.")
    if not erreurs:
        montant, epargne = demande.get("montant_cad"), profil.get("epargne_totale_cad")
        if montant is not None and epargne is not None and montant > epargne:
            erreurs.append("Le montant dépasse l'épargne totale.")
    return erreurs


def appliquer_regles(profil: dict, demande: dict, m: dict, f: dict | None = None) -> list[Regle]:
    """Applique les règles, puis rattache à chacune sa nature (FAIT/HYPOTHESE/SCENARIO) et ses sources."""
    regles = _regles(profil, demande, m, f)
    for r in regles:
        r.type = TYPE_REGLE.get(r.code, "HYPOTHESE")  # type: ignore[assignment]
        r.references = references_de(f"regle-{r.code}")
    return regles


def _regle_capacite(profil: dict, demande: dict, m: dict, f: dict, ev: dict, comparaison=None) -> Regle:
    """Une seule règle, utilisée par le dossier et la recherche exhaustive."""
    poids = demande["montant_cad"] / profil["epargne_totale_cad"]
    chute = abs(m["pire_chute_pct"])
    impact = round(poids * chute, 1)

    # 1. Capacité et tolérance de perte
    if comparaison is None:
        comparaison = (portefeuille.comparer(profil, demande)
                       if os.environ.get("ALPHAFORGE_CAPACITE") != "approximation" else {})
    faits_capacite = [f.get("chute", ""), f.get("h_perte", ""), f.get("h_capacite", "")]
    if comparaison.get("disponible"):
        avant = abs(comparaison["avant"]["pire_chute_pct"])
        impact = abs(comparaison["apres"]["pire_chute_pct"])
        ecart = comparaison["ecarts"]["pire_chute_pts"]
        anterieur = avant > ev["perte_max_capacite_pct"]
        attribuable = not (anterieur and ecart >= 0)
        niveau = ("rouge" if impact > ev["perte_max_capacite_pct"] and attribuable else
                  "orange" if impact > ev["perte_max_tolerance_pct"] else "ok")
        txt = (f"Pire baisse du portefeuille après la demande : {fr(-impact)} %, "
               f"contre {fr(-avant)} % avant ; écart après moins avant : {fr(ecart)} points "
               f"({comparaison['ecarts']['sens_pire_chute']}). "
               f"Capacité de perte : {fr(ev['perte_max_capacite_pct'])} % ; "
               f"tolérance : {fr(ev['perte_max_tolerance_pct'])} %. ")
        if anterieur:
            txt += "Le portefeuille actuel dépassait déjà la capacité avant cette demande. "
            if not attribuable:
                txt += ("La demande n'aggrave pas cette baisse : cet état antérieur ne la rend pas rouge "
                        "(hypothèse d'attribution de l'équipe).")
        faits_capacite = [f.get(cle, "") for cle in (
            "avant_pire_chute", "apres_pire_chute", "ecart_pire_chute",
            "h_perte", "h_capacite", "h_attribution",
        )]
    elif impact > ev["perte_max_capacite_pct"]:
        niveau, txt = "rouge", (f"Si ce placement revivait sa pire chute ({fr(m['pire_chute_pct'])} %), ton épargne "
                                f"baisserait de {fr(impact)} %. Ta capacité de perte est estimée à "
                                f"{fr(ev['perte_max_capacite_pct'])} %.")
    elif impact > ev["perte_max_tolerance_pct"]:
        niveau, txt = "orange", (f"La pire chute observée ferait baisser ton épargne de {fr(impact)} %. C'est dans ta "
                                 f"capacité ({fr(ev['perte_max_capacite_pct'])} %), mais au-delà de ce que tu dis "
                                 f"vouloir risquer ({fr(ev['perte_max_tolerance_pct'])} %).")
    else:
        niveau, txt = "ok", (f"La pire chute observée ferait baisser ton épargne de {fr(impact)} %, sous ta limite "
                             f"de {fr(ev['perte_max_retenue_pct'])} %.")
    if not comparaison.get("disponible"):
        txt += " Cette approximation suppose le reste du portefeuille stable."
    return Regle("capacite", "Perte supportable", niveau, txt, faits_capacite)


QUESTIONS_MANQUANTS = {
    "horizon": "Dans combien d'années auras-tu besoin de cet argent ?",
    "épargne totale": "Combien as-tu d'épargne au total, en dollars canadiens ?",
    "montant": "Combien veux-tu placer ?",
    "tolérance": "Quel risque es-tu prêt à prendre ? Réponds aux 3 questions « Ton rapport au risque », ou règle la puce « risque ».",
}


def informations_manquantes(profil: dict, demande: dict) -> list[str]:
    """Informations essentielles absentes : sans elles, le Gardien ne conclut pas (verdict gris)."""
    ev = evaluer(profil)
    return [nom for nom, v in [("horizon", profil.get("horizon_ans")), ("épargne totale", profil.get("epargne_totale_cad")),
                               ("montant", demande.get("montant_cad")), ("tolérance", ev["tolerance"])] if v is None]


def questions_manquantes(profil: dict, demande: dict) -> list[str]:
    return [QUESTIONS_MANQUANTS[nom] for nom in informations_manquantes(profil, demande)]


def _regles(profil: dict, demande: dict, m: dict, f: dict | None = None, *, _avec_capacite: bool = True) -> list[Regle]:
    """profil : champs du profil ; demande : ticker, montant_cad ; m : mesures
    calculées ; f : identifiants des faits (pour relier chaque règle à ses preuves)."""
    f = f or {}
    erreurs = erreurs_entree(profil, demande)
    if erreurs:
        return [Regle("donnees", "Informations essentielles", "gris", " ".join(erreurs))]
    ev = evaluer(profil)
    regles: list[Regle] = []
    epargne = profil.get("epargne_totale_cad")
    montant = demande.get("montant_cad")

    manquants = informations_manquantes(profil, demande)
    if any(c["statut"] == "echec" for c in m.get("qualite", [])):
        manquants.append("données de marché fiables")
    if manquants:
        regles.append(Regle("donnees", "Informations essentielles", "gris", "Il manque : " + ", ".join(manquants) + "."))
        return regles

    poids = montant / epargne
    if _avec_capacite:
        regles.append(_regle_capacite(profil, demande, m, f, ev))

    # 2. Somme à préserver
    preserver = profil.get("somme_a_preserver_cad")
    if preserver is not None:
        reste = epargne - montant
        ok = reste >= preserver
        regles.append(Regle("preserver", "Somme à préserver", "ok" if ok else "rouge",
                            f"Après ce placement, il resterait {dollars(reste)} hors de ce titre, pour "
                            f"{dollars(preserver)} à préserver."))

    # 3. Exclusions (valeurs)
    exclusions = exclusions_normalisees(profil)
    secteur = str(m.get("secteur", ""))
    if exclusions:
        touche = any(e in secteur.lower() for e in exclusions)
        regles.append(Regle("exclusion", "Respect de tes exclusions", "rouge" if touche else "ok",
                            f"Secteur de l'actif : {SECTEURS_FR.get(secteur, secteur)}"
                            + (f" ({secteur}). " if secteur in SECTEURS_FR else ". ") + ("Il fait partie de tes exclusions."
                                                                   if touche else "Il n'est pas exclu."),
                            [f.get("secteur", "")]))

    # 4. Retrait prévu avant récupération, sur un actif volatil
    retrait = profil.get("retrait_prevu_ans")
    recup = m.get("recuperation_annees") if m.get("recupere") else None
    if retrait is not None:
        risque = m["volatilite_pct"] > SEUIL_VOLATIL_RETRAIT and (recup is None or retrait < recup)
        regles.append(Regle("retrait", "Retrait prévu", "rouge" if risque else "ok",
                            (f"Tu prévois de retirer de l'argent dans {retrait} an(s). Ce placement est volatil "
                             f"({fr(m['volatilite_pct'])} %/an) et a mis "
                             + (f"{fr(recup)} an(s)" if recup else "plus que la période observée")
                             + " à se remettre de sa pire chute.") if risque else
                            "Le retrait prévu laisse le temps de traverser une baisse comparable.",
                            [f.get("volatilite", ""), f.get("recuperation", ""), f.get("h_volatil", "")]))

    # 5. Horizon plus court que le temps de récupération observé
    horizon = profil["horizon_ans"]
    if m.get("recupere"):
        trop_court = horizon < m["recuperation_annees"]
        detail = f"il a fallu {fr(m['recuperation_annees'])} an(s) pour revenir au sommet"
    else:
        trop_court = horizon < m["annees_depuis_creux"]
        detail = f"le sommet n'est toujours pas retrouvé {fr(m['annees_depuis_creux'])} an(s) après le creux"
    regles.append(Regle("horizon", "Horizon et temps de récupération", "orange" if trop_court else "ok",
                        f"Ton horizon est de {horizon} an(s) ; après la pire chute, {detail}.",
                        [f.get("recuperation", "")]))

    # 6. Concentration : sur un actif très volatil, et sur un seul titre même moins volatil
    tres_volatil = m["volatilite_pct"] > SEUIL_TRES_VOLATIL
    if tres_volatil or m.get("asset_class") in CLASSES_TITRE_UNIQUE:
        seuil = ev["seuil_concentration_pct"] if tres_volatil else ev["seuil_titre_unique_pct"]
        trop = poids * 100 > seuil
        proche = tres_volatil and retrait is not None and retrait <= RETRAIT_PROCHE_ANS
        niveau = ("rouge" if proche else "orange") if trop else "ok"
        nature = "un actif aussi volatil" if tres_volatil else "un seul titre, moins volatil"
        txt = (f"Ce placement représente {poids * 100:.0f} % de ton épargne. Pour {nature}, le seuil retenu pour ton "
               f"profil est {fr(int(seuil) if seuil == int(seuil) else seuil)} %.")
        if niveau == "rouge":
            txt += (f" Tu prévois de retirer de l'argent dans {retrait} an(s) : si près du besoin, dépasser ce seuil "
                    "n'est pas cohérent avec ta situation.")
        regles.append(Regle("concentration", "Concentration", niveau, txt,
                            [f.get("volatilite", ""), f.get("h_concentration" if tres_volatil else "h_titre", ""),
                             f.get("h_volatil", "")] + ([f.get("h_retrait_proche", "")] if niveau == "rouge" else [])))

    # 7. Coussin de sécurité
    if profil.get("fonds_urgence") is not None:
        regles.append(Regle("coussin", "Fonds d'urgence", "ok" if profil["fonds_urgence"] else "orange",
                            "Tu as un fonds d'urgence." if profil["fonds_urgence"] else
                            "Sans fonds d'urgence, une dépense imprévue pourrait forcer une vente au mauvais moment."))

    # 8. Fausse diversification (si on connaît les placements actuels)
    correl = m.get("correlations") or {}
    deja = demande.get("ticker") and demande.get("ticker") in symboles_portefeuille(profil.get("portefeuille_actuel"))
    note_deja = f" Tu détiens déjà {demande['ticker']} : ce placement s'y ajoute." if deja else ""
    if correl:
        forts = {t: c for t, c in correl.items() if c >= SEUIL_CORRELATION}
        t_max, c_max = max(correl.items(), key=lambda kv: kv[1])
        regles.append(Regle("diversification", "Diversification réelle", "orange" if forts else "ok",
                            (("Très corrélé à ce que tu détiens déjà : " + ", ".join(f"{t} ({fr(c)})" for t, c in forts.items())
                              + ". Ça ne diversifie pas.") if forts else
                             (f"Corrélation la plus forte avec tes placements : {t_max} ({fr(c_max)}), sous le seuil de 0,8 "
                              "retenu par l'équipe pour parler de fausse diversification.")) + note_deja,
                            [f.get("correlation", ""), f.get("h_correlation", "")]))
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
    Recherche décroissante exhaustive : K5 ne garantit pas la monotonie d'un mélange.
    Les mesures par montant et les réponses FX sont mises en cache par l'adaptateur."""
    bas, haut = int(bon // PAS_MONTANT), int(mauvais // PAS_MONTANT)
    for palier in range(haut, bas, -1):
        montant = palier * PAS_MONTANT
        if _etat(profil, {**demande, "montant_cad": montant}, m) == cible:
            return montant
    return int(bon)


def plus_petit_ajustement(profil: dict, demande: dict, m: dict) -> dict | None:
    """Variation de montant la plus proche qui améliore l'état, dans les deux sens.

    Tous les paliers admissibles sont visités par distance croissante ; à égalité,
    la baisse passe d'abord. Aucun ordre de risque n'est supposé. Si aucun montant
    n'améliore l'état, essayer les cinq allongements d'horizon du socle.
    """
    base_h = profil["horizon_ans"]
    regles_actuelles = appliquer_regles(profil, demande, m)
    actuel = verdict(regles_actuelles)["etat"]
    if actuel in ("coherent", "indetermine"):
        return None
    montant = demande["montant_cad"]
    # Ces règles ne dépendent ni du montant ni de l'horizon testé. Si leur niveau
    # suffit à maintenir l'état, aucune recherche de montant/horizon ne peut aider.
    fixes = [r for r in _regles(profil, demande, m, _avec_capacite=False)
             if r.code in ("exclusion", "retrait", "coussin", "diversification")]
    if fixes and RANG[verdict(fixes)["etat"]] >= RANG[actuel]:
        return None
    ev = evaluer(profil)
    bas = (math.ceil(montant / PAS_MONTANT) - 1) * PAS_MONTANT
    haut = (math.floor(montant / PAS_MONTANT) + 1) * PAS_MONTANT
    plafond = profil["epargne_totale_cad"]
    while bas >= PAS_MONTANT or haut <= plafond:
        baisse = bas >= PAS_MONTANT and (haut > plafond or montant - bas <= haut - montant)
        essai = bas if baisse else haut
        if baisse:
            bas -= PAS_MONTANT
        else:
            haut += PAS_MONTANT
        dem = {**demande, "montant_cad": essai}
        autres = _regles(profil, dem, m, _avec_capacite=False)
        if RANG[verdict(autres)["etat"]] >= RANG[actuel]:
            continue  # rejet prouvé par les autres règles, sans calcul financier inutile
        comparaison = ({} if os.environ.get("ALPHAFORGE_CAPACITE") == "approximation"
                       else portefeuille.comparer_pertes(profil, dem))
        nouvelles = [_regle_capacite(profil, dem, m, {}, ev, comparaison), *autres]
        etat = verdict(nouvelles)["etat"]
        if RANG[etat] < RANG[actuel]:
            anciens_niveaux = {r.code: r.niveau for r in regles_actuelles}
            changements = [
                (f"la règle « {r.libelle} » serait respectée" if r.niveau == "ok" else
                 f"la règle « {r.libelle} » passerait au niveau {r.niveau}")
                for r in nouvelles if ORDRE[r.niveau] < ORDRE[anciens_niveaux[r.code]]
            ]
            return {"changement": {"montant_cad": essai}, "etat": etat,
                    "sens": "baisse" if baisse else "hausse",
                    "constat": (f"À {dollars(essai).replace('$', 'CAD')}, " + " ; ".join(changements) + ". "
                                f"Le verdict serait « {LIBELLES_ETAT[etat]} » "
                                f"(variation à la {'baisse' if baisse else 'hausse'} dans cette simulation).")}
    for k in range(1, 6):
        etat = _etat({**profil, "horizon_ans": base_h + k}, demande, m)
        if RANG[etat] < RANG[actuel]:
            return {"changement": {"horizon_ans": base_h + k}, "etat": etat}
    return None
