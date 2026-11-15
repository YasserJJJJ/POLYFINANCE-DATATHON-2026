"""Sceptique : cherche une faille précise dans les faits et force une vérification.

Agent aux outils BORNÉS : il ne peut demander que des vérifications du catalogue
ci-dessous, que le code exécute. Pas d'opinion libre : chaque objection cite un F-n.
Le modèle choisit 1 à 3 vérifications pertinentes et formule l'objection ; sans
modèle, on applique toutes les vérifications pertinentes.
"""
from __future__ import annotations

import time

from .. import calculs, llm
from ..donnees import _prix
from ..dossier import Dossier, Objection

MAX_OBJECTIONS = 3


def _chute_en_devise_locale(ticker: str) -> float:
    p = _prix()
    s = p.loc[p["ticker"] == ticker].set_index("date")["adj_close"].astype(float)
    return round(float((s / s.cummax() - 1).min()) * 100, 1)


# Chaque vérification : (applicable ?, fait visé, texte par défaut, exécution → réponse)
def _devise(d: Dossier, m: dict, ids: dict) -> str:
    usd = _chute_en_devise_locale(d.demande["ticker"])
    f = d.ajouter_fait(f"Pire chute de {d.demande['ticker']} en USD (sans conversion)", usd, "%", "FAIT",
                       "Yahoo Finance", "Même calcul, sans conversion en CAD.")
    return (f"Recalcul fait ({f.id}) : {usd} % en USD contre {m['pire_chute_pct']} % en CAD "
            f"(écart de {round(m['pire_chute_pct'] - usd, 1)} point(s)). On garde la mesure en CAD.")


def _recuperation(d: Dossier, m: dict, ids: dict) -> str:
    return (f"Le Gardien utilise {m['annees_depuis_creux']} an(s) comme minimum : la récupération réelle "
            "sera au moins aussi longue.")


def _fenetre(d: Dossier, m: dict, ids: dict) -> str:
    return "Limite ajoutée au texte final : la pire chute est celle observée sur 5 ans, pas un maximum."


ECART_NET_POINTS = 10  # écart à partir duquel on dit que la chute « tient surtout au placement » (choix de rédaction)


def _reference(d: Dossier, m: dict, ids: dict) -> str:
    ref = d.fait(ids.get("reference", ""))
    if not ref:
        return "Pas de référence disponible : comparaison impossible."
    ticker, chute = d.demande["ticker"], m["pire_chute_pct"]
    ecart = round(abs(chute) - abs(ref.valeur), 1)
    tete = (f"Comparaison faite avec le marché canadien large ({ref.id} : {ref.valeur} %) : la chute de "
            f"{ticker} ({chute} %) ")
    if ecart >= ECART_NET_POINTS:
        return tete + "est nettement plus forte : elle tient surtout au placement lui-même."
    if ecart > 0:
        return tete + "est un peu plus forte : une bonne partie vient du marché dans son ensemble."
    return tete + "n'est pas plus forte que celle du marché."


def _une_annee(d: Dossier, m: dict, ids: dict) -> str:
    f = d.fait(ids["pire12"])
    return (f"Vérifié ({f.id}) : sur 12 mois glissants, la pire baisse est de {f.valeur} %. "
            "Une baisse forte peut donc survenir en moins d'un an.")


SEUIL_GARDIEN = 0.8  # même seuil que la règle « Diversification réelle » de gardien.py


def _concentration(d: Dossier, m: dict, ids: dict) -> str:
    forts = {t: c for t, c in (m.get("correlations") or {}).items() if c >= 0.6}
    if not forts:
        return "Vérifié : corrélations avec les placements actuels toutes sous 0,6."
    texte = "Vérifié : ce placement bouge en partie avec " + ", ".join(f"{t} ({c})" for t, c in forts.items()) + "."
    if all(c < SEUIL_GARDIEN for c in forts.values()):
        texte += " Le Gardien ne parle de fausse diversification qu'à partir de 0,8 (seuil de l'équipe)."
    return texte


CATALOGUE = {
    "devise": (lambda m, ids: m["devise"] == "USD", "chute",
               "La pire chute est-elle mesurée en dollars canadiens ? Pour un investisseur canadien, le taux de change compte.",
               "Recalculer la pire chute en USD et comparer.", _devise),
    "recuperation_inconnue": (lambda m, ids: not m["recupere"], "recuperation",
                              "Le sommet n'est pas retrouvé : le temps de récupération n'est pas connu, il n'est pas nul.",
                              "Utiliser le temps écoulé depuis le creux comme borne minimale.", _recuperation),
    "fenetre_courte": (lambda m, ids: True, "chute",
                       "La fenêtre ne couvre que 5 ans. Une crise plus forte (2008, 2020) n'y figure pas.",
                       "Marquer la pire chute comme borne observée, pas comme pire cas possible.", _fenetre),
    "comparer_marche": (lambda m, ids: "reference" in ids, "chute",
                        "Cette chute vient-elle du placement lui-même ou de tout le marché ?",
                        "Comparer à la pire chute du marché canadien large.", _reference),
    "rapidite_baisse": (lambda m, ids: "pire12" in ids, "pire12",
                        "Une baisse forte peut-elle arriver vite, avant que la personne ait le temps de réagir ?",
                        "Lire la pire période de 12 mois glissants.", _une_annee),
    "diversification": (lambda m, ids: bool(m.get("correlations")), "correlation",
                        "Ce placement diversifie-t-il vraiment ce que tu détiens déjà ?",
                        "Lire les corrélations avec le portefeuille actuel.", _concentration),
}

SYSTEME = """Tu es le Sceptique d'un comité d'analyse (simulation éducative, pas de conseil).
Ton rôle : trouver les failles possibles des chiffres avant qu'ils soient présentés.
Tu ne peux demander QUE des vérifications de la liste fournie : tu ne calcules rien toi-même.
Choisis les 1 à 3 vérifications les plus utiles pour CETTE personne et CETTE demande.
Pour chacune, écris une objection courte (une phrase, en français, vouvoiement interdit : tutoie),
sans aucun chiffre que tu inventerais.
Format : {"objections": [{"code": "<code de la liste>", "texte": "<objection>"}]}"""


def _choix_llm(d: Dossier, possibles: list[str]) -> list[tuple[str, str]]:
    p, m = d.profil, d.demande["mesures"]
    contexte = (f"Personne : {p.get('nom')}, horizon {p.get('horizon_ans')} an(s), expérience {p.get('experience')}, "
                f"exclusions {p.get('exclusions')}, placements actuels {p.get('portefeuille_actuel')}.\n"
                f"Demande : {d.demande.get('texte')} ({d.demande['ticker']}, {d.demande['montant_cad']} $).\n"
                f"Faits : " + "; ".join(f"{f.id} {f.libelle} = {f.valeur} {f.unite}" for f in d.faits) + "\n"
                f"Vérifications possibles :\n" + "\n".join(f"- {c} : {CATALOGUE[c][3]}" for c in possibles))
    brut = llm.appeler_json(SYSTEME, contexte, llm.MODELE_PRINCIPAL, 700)
    choix = []
    for o in brut.get("objections", [])[:MAX_OBJECTIONS]:
        if o.get("code") in possibles and o["code"] not in [c for c, _ in choix]:
            texte = str(o.get("texte", "")).strip()[:300]
            if texte and not llm.nombres(texte) - {1.0, 2.0, 3.0, 5.0, 12.0}:  # aucun chiffre inventé
                choix.append((o["code"], texte))
            else:
                choix.append((o["code"], CATALOGUE[o["code"]][2]))
    return choix


def executer(d: Dossier) -> None:
    debut = time.perf_counter()
    m, ids = d.demande["mesures"], d.demande["ids_faits"]
    possibles = [c for c, (ok, *_rest) in CATALOGUE.items() if ok(m, ids)]
    source = "règles (hors ligne)"
    choix: list[tuple[str, str]] = []
    if llm.actif():
        try:
            choix = _choix_llm(d, possibles)
            source = llm.nom(llm.MODELE_PRINCIPAL)
        except Exception:
            choix = []
    if not choix:
        choix = [(c, CATALOGUE[c][2]) for c in possibles if c in ("devise", "recuperation_inconnue", "fenetre_courte")]
        choix = choix[:MAX_OBJECTIONS]

    for code, texte in choix:
        _ok, cible, _defaut, recalcul, executer_verif = CATALOGUE[code]
        obj = Objection(f"O-{len(d.objections) + 1}", ids.get(cible, ids["chute"]), texte, recalcul)
        obj.reponse = executer_verif(d, m, ids)
        obj.resolue = True
        d.objections.append(obj)

    d.tracer("Sceptique", "objecte et force des vérifications",
             f"{len(d.objections)} objection(s) choisie(s) parmi {len(possibles)} vérifications autorisées "
             f"({source}). Chacune a été exécutée par le code.",
             [o.cible for o in d.objections], debut)
