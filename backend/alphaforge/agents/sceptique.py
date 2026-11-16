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
from ..format import fr
from ..sources import references_de
from ..garde_fous import mots_de_conseil, rapport_calcule, sans_accents

MAX_OBJECTIONS = 3
# Issue d'une vérification : « confirmee » = elle donne raison au Sceptique, « ecartee » = le fait tient tel quel,
# « limite » = une limite de méthode, sans calcul qui puisse trancher.
ECART_DEVISE_POINTS = 2   # écart CAD/USD à partir duquel le change compte vraiment (choix de rédaction)
BAISSE_RAPIDE_PCT = 20    # pire baisse sur 12 mois à partir de laquelle une chute « rapide » est confirmée


def _chute_en_devise_locale(ticker: str) -> float:
    p = _prix()
    s = p.loc[p["ticker"] == ticker].set_index("date")["adj_close"].astype(float)
    return round(float((s / s.cummax() - 1).min()) * 100, 1)


# Chaque vérification : (applicable ?, fait visé, texte par défaut, exécution → réponse)
def _devise(d: Dossier, m: dict, ids: dict) -> tuple[str, str]:
    usd = _chute_en_devise_locale(d.demande["ticker"])
    f = d.ajouter_fait(f"Pire chute de {d.demande['ticker']} en USD (sans conversion)", usd, "%", "FAIT",
                       "Yahoo Finance", "Même calcul, sans conversion en CAD.",
                       references=references_de("devise_usd"))
    ecart = round(m["pire_chute_pct"] - usd, 1)
    return (f"Recalcul fait ({f.id}) : {fr(usd)} % en USD contre {fr(m['pire_chute_pct'])} % en CAD "
            f"(écart de {fr(ecart)} point(s)). On garde la mesure en CAD.",
            "confirmee" if abs(ecart) >= ECART_DEVISE_POINTS else "ecartee")


def _recuperation(d: Dossier, m: dict, ids: dict) -> tuple[str, str]:
    return (f"Le Gardien utilise {fr(m['annees_depuis_creux'])} an(s) comme minimum : la récupération réelle "
            "sera au moins aussi longue.", "confirmee")


def _fenetre(d: Dossier, m: dict, ids: dict) -> tuple[str, str]:
    return "Limite ajoutée au texte final : la pire chute est celle observée sur 5 ans, pas un maximum.", "limite"


ECART_NET_POINTS = 10  # écart à partir duquel on dit que la chute « tient surtout au placement » (choix de rédaction)


def _reference(d: Dossier, m: dict, ids: dict) -> tuple[str, str]:
    ref = d.fait(ids.get("reference", ""))
    if not ref:
        return "Pas de référence disponible : comparaison impossible.", "limite"
    ticker, chute = d.demande["ticker"], m["pire_chute_pct"]
    ecart = round(abs(chute) - abs(ref.valeur), 1)
    tete = (f"Comparaison faite avec le marché canadien large ({ref.id} : {fr(ref.valeur)} %) : la chute de "
            f"{ticker} ({fr(chute)} %) ")
    if ecart >= ECART_NET_POINTS:
        return tete + "est nettement plus forte : elle tient surtout au placement lui-même.", "ecartee"
    if ecart > 0:
        return tete + "est un peu plus forte : une bonne partie vient du marché dans son ensemble.", "confirmee"
    return tete + "n'est pas plus forte que celle du marché.", "confirmee"


def _une_annee(d: Dossier, m: dict, ids: dict) -> tuple[str, str]:
    f = d.fait(ids["pire12"])
    tete = f"Vérifié ({f.id}) : sur 52 semaines glissantes (cours du vendredi), la pire baisse est de {fr(f.valeur)} %. "
    if f.valeur <= -BAISSE_RAPIDE_PCT:
        return tete + "Une baisse forte peut donc survenir en moins d'un an.", "confirmee"
    return tete + "Sur la période, aucune baisse aussi forte n'est survenue en moins d'un an.", "ecartee"


SEUIL_GARDIEN = 0.8  # même seuil que la règle « Diversification réelle » de gardien.py


def _concentration(d: Dossier, m: dict, ids: dict) -> tuple[str, str]:
    forts = {t: c for t, c in (m.get("correlations") or {}).items() if c >= 0.6}
    if not forts:
        return "Vérifié : corrélations avec les placements actuels toutes sous 0,6.", "ecartee"
    texte = "Vérifié : ce placement bouge en partie avec " + ", ".join(f"{t} ({fr(c)})" for t, c in forts.items()) + "."
    if all(c < SEUIL_GARDIEN for c in forts.values()):
        texte += " Le Gardien ne parle de fausse diversification qu'à partir de 0,8 (seuil de l'équipe)."
    return texte, "confirmee"


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
                f"Vérifications possibles :\n" + "\n".join(f"- {fr(c)} : {CATALOGUE[c][3]}" for c in possibles))
    brut = llm.appeler_json(SYSTEME, contexte, llm.MODELE_PRINCIPAL, 700)
    choix = []
    for o in (brut.get("objections") or [])[:MAX_OBJECTIONS]:
        if not isinstance(o, dict):
            continue
        if o.get("code") in possibles and o["code"] not in [c for c, _ in choix]:
            texte = str(o.get("texte", "")).strip()[:300]
            if texte and _texte_acceptable(o["code"], texte):
                choix.append((o["code"], texte))
            else:
                choix.append((o["code"], CATALOGUE[o["code"]][2]))
    return choix


# Mots du thème de chaque vérification : l'objection rédigée par le modèle doit parler de la vérification
# que le code exécute (sinon on affiche la question du catalogue).
THEMES = {"devise": ("dollar", "change", "usd", "cad", "devise"),
          "recuperation_inconnue": ("sommet", "recup", "remont"),
          "fenetre_courte": ("fenetre", "5 ans", "cinq ans", "borne", "pire cas", "historique", "crise", "periode",
                             "plancher", "plafond", "observe"),
          "comparer_marche": ("marche",),
          "rapidite_baisse": ("vite", "rapide", "12 mois", "un an", "moins d'un an", "brutal"),
          "diversification": ("diversif", "correl", "bouge", "detiens", "portefeuille")}


def _texte_acceptable(code: str, texte: str) -> bool:
    """Aucun chiffre inventé, aucune formule de conseil, et le texte parle bien de la vérification choisie."""
    bas = sans_accents(texte.lower())
    return (not llm.nombres(texte) - {1.0, 2.0, 3.0, 5.0, 12.0} and not mots_de_conseil(texte)
            and not rapport_calcule(texte)
            and any(mot in bas for mot in THEMES.get(code, ())))


def executer(d: Dossier) -> None:
    debut = time.perf_counter()
    m, ids = d.demande["mesures"], d.demande["ids_faits"]
    possibles = [c for c, (ok, *_rest) in CATALOGUE.items() if ok(m, ids)]
    source = "règles (hors ligne)"
    choix: list[tuple[str, str]] = []
    if llm.actif():
        try:
            choix = _choix_llm(d, possibles)
            source = (llm.nom(llm.MODELE_PRINCIPAL) if choix else
                      "règles : le modèle n'a proposé aucune vérification valide")
        except Exception as e:
            choix, source = [], f"règles : réponse du modèle inutilisable ({type(e).__name__})"
    if not choix:
        choix = [(c, CATALOGUE[c][2]) for c in possibles if c in ("devise", "recuperation_inconnue", "fenetre_courte")]
        choix = choix[:MAX_OBJECTIONS]

    for code, texte in choix:
        _ok, cible, _defaut, recalcul, executer_verif = CATALOGUE[code]
        obj = Objection(f"O-{len(d.objections) + 1}", ids.get(cible, ids["chute"]), texte, recalcul)
        obj.reponse, obj.issue = executer_verif(d, m, ids)
        obj.resolue = True   # la vérification a été exécutée ; son résultat est dans `issue`
        d.objections.append(obj)

    bilan = {i: sum(o.issue == i for o in d.objections) for i in ("confirmee", "ecartee", "limite")}
    d.tracer("Sceptique", "objecte et force des vérifications",
             f"{len(d.objections)} objection(s) choisie(s) parmi {len(possibles)} vérifications autorisées "
             f"({source}). Chacune a été exécutée par le code : {bilan['confirmee']} confirmée(s), "
             f"{bilan['ecartee']} écartée(s), {bilan['limite']} limite(s) notée(s).",
             [o.cible for o in d.objections], debut)
