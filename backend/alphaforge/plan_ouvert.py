"""Plan ouvert : la personne donne un montant et sa situation, mais pas de placement.

Le Gardien juge le même montant sur chaque placement de la liste (hors exclusions), en code, sans modèle.
Le plan est réalisable si au moins un placement passe toutes les règles, réalisable avec un ajustement si
seuls des ajustements passent, pas réalisable sinon. On montre 1 à 3 placements qui passent, un par
famille, en partant de la pire chute observée la plus faible : jamais au rendement passé, qui serait lu
comme une prévision. C'est une simulation de ce que les règles acceptent, pas une recommandation.
"""
from __future__ import annotations

import time
from collections import Counter

from . import gardien
from .agents import analyste
from .donnees import univers
from .dossier import Dossier
from .format import dollars, fr
from .profil import symboles_portefeuille
from .sources import references_de

FAMILLES = {"etf_bond": "Obligations", "etf_equity": "Marché large (FNB d'actions)", "etf_commodity": "Or",
            "equity": "Action d'une entreprise", "crypto": "Cryptoactif"}
MAX_PLACEMENTS = 3
LIBELLES = {"coherent": "Ton plan est réalisable",
            "ajustement": "Ton plan est réalisable avec un ajustement",
            "incoherent": "Ton plan n'est pas réalisable avec ta situation"}
CRITERE = ("Un placement par famille, en partant de la pire chute observée la plus faible. "
           "Aucun classement au rendement passé, qui serait lu comme une prévision.")


def _choisir(juges: list[dict], etat: str) -> list[dict]:
    """D'abord un placement par famille ; s'il y a moins de 3 familles, on complète dans le même ordre."""
    candidats = sorted((j for j in juges if j["etat"] == etat), key=lambda j: abs(j["m"]["pire_chute_pct"]))
    retenus, familles = [], set()
    for j in candidats:
        if j["famille"] not in familles and len(retenus) < MAX_PLACEMENTS:
            retenus.append(j)
            familles.add(j["famille"])
    for j in candidats:
        if j not in retenus and len(retenus) < MAX_PLACEMENTS:
            retenus.append(j)
    return sorted(retenus, key=lambda j: abs(j["m"]["pire_chute_pct"]))


def juger_liste(d: Dossier, exclure: set[str] | frozenset = frozenset()) -> tuple[list[dict], Counter]:
    """Le Gardien juge le même montant sur chaque placement de la liste, hors exclusions et hors `exclure`."""
    exclusions = gardien.exclusions_normalisees(d.profil)
    portefeuille = symboles_portefeuille(d.profil.get("portefeuille_actuel"))
    juges, ecartes = [], Counter()
    for ticker, info in univers().iterrows():
        if ticker in exclure:
            continue
        if any(e in str(info["sector"]).lower() for e in exclusions):
            ecartes["Secteur exclu"] += 1
            continue
        m = analyste.mesures_actif(ticker, portefeuille)
        regles = gardien.appliquer_regles(d.profil, {**d.demande, "ticker": ticker}, m)
        v = gardien.verdict(regles)
        juges.append({"ticker": ticker, "nom": info["name"], "famille": FAMILLES.get(info["asset_class"], "Autre"),
                      "m": m, "regles": regles, "etat": v["etat"]})
        if v["etat"] != "coherent":
            for r in regles:
                if r.niveau in ("rouge", "orange", "gris"):
                    ecartes[r.libelle] += 1
    return juges, ecartes


def _placements(d: Dossier, retenus: list[dict]) -> list[dict]:
    sortie = []
    for j in retenus:
        f = d.ajouter_fait(f"Pire chute de {j['ticker']} ({j['nom']})", j["m"]["pire_chute_pct"], "%", "FAIT",
                           "Yahoo Finance via yfinance, jeu de départ AlphaForge",
                           "Même méthode pour tous les placements de la liste, en CAD, 2021-11-12 → 2026-11-12.",
                           references=references_de("alternative"))
        sortie.append({"ticker": j["ticker"], "nom": j["nom"], "famille": j["famille"], "etat": j["etat"],
                       "pire_chute_pct": j["m"]["pire_chute_pct"], "volatilite_pct": j["m"]["volatilite_pct"],
                       "a_ajuster": [r.libelle for r in j["regles"] if r.niveau in ("orange", "rouge")],
                       "faits": [f.id]})
    return sortie


def _bilan_qualite(juges: list[dict]) -> list[dict]:
    """Les 7 contrôles de données, résumés sur tous les placements jugés (le pire statut l'emporte)."""
    rang = {"ok": 0, "alerte": 1, "echec": 2}
    bilan: dict[str, dict] = {}
    for j in juges:
        for c in j["m"].get("qualite") or []:
            b = bilan.setdefault(c["code"], {"code": c["code"], "libelle": c["libelle"], "statut": "ok", "ok": 0, "n": 0})
            b["n"] += 1
            b["ok"] += c["statut"] == "ok"
            if rang.get(c["statut"], 0) > rang[b["statut"]]:
                b["statut"] = c["statut"]
    return [{"code": b["code"], "libelle": b["libelle"], "statut": b["statut"],
             "detail": f"réussi pour {b['ok']} placement(s) sur {b['n']}"} for b in bilan.values()]


def suggerer(d: Dossier) -> None:
    """Après un « incohérent » sur le placement demandé : les placements de la liste qui passent les règles
    de la personne, comme pour un plan sans placement (hors placement demandé et hors options déjà montrées)."""
    deja = {d.demande.get("ticker")} | {o.get("ticker") for o in d.options if o.get("ticker")}
    juges, _ecartes = juger_liste(d, exclure=deja)
    retenus = _choisir(juges, "coherent") or _choisir(juges, "ajustement")
    if not retenus:
        return
    d.suggestions = {"placements": _placements(d, retenus), "critere": CRITERE, "evalues": len(juges),
                     "passent": sum(j["etat"] == "coherent" for j in juges)}


def executer(d: Dossier) -> None:
    debut = time.perf_counter()
    premier = d.demande.get("ticker") or next(iter(univers().index))
    essai = gardien.appliquer_regles(d.profil, {**d.demande, "ticker": premier},
                                     analyste.mesures_actif(premier, symboles_portefeuille(d.profil.get("portefeuille_actuel"))))
    if gardien.verdict(essai)["etat"] == "indetermine" and gardien.informations_manquantes(d.profil, d.demande):
        # Une information essentielle de la personne manque (horizon, épargne, tolérance) : on ne conclut pas.
        d.regles, d.verdict = essai, gardien.verdict(essai)
        d.questions = gardien.questions_manquantes(d.profil, d.demande) + d.questions
        d.tracer("Gardien", "juge le plan sur la liste des placements",
                 "Impossible de conclure : " + essai[0].explication, debut=debut)
        return
    juges, ecartes = juger_liste(d)
    d.qualite_donnees = _bilan_qualite(juges)
    d.tracer("Analyste", "mesure chaque placement de la liste",
             f"{len(juges)} placements mesurés avec les mêmes outils de calcul (pire chute, volatilité, récupération), "
             f"{ecartes['Secteur exclu']} écarté(s) d'avance par tes exclusions.", debut=debut)
    d.tracer("Sceptique", "objecte et force des vérifications",
             "Plan ouvert : aucun placement n'est encore choisi, il n'y a pas de chiffre à contester. Les "
             "vérifications reprennent dès qu'un placement est analysé seul.")

    debut = time.perf_counter()
    etat, retenus = "incoherent", []
    for cible in ("coherent", "ajustement"):
        retenus = _choisir(juges, cible)
        if retenus:
            etat = cible
            break
    passent = sum(j["etat"] == "coherent" for j in juges)
    avec_ajustement = sum(j["etat"] == "ajustement" for j in juges)
    placements = _placements(d, retenus)
    reference = retenus[0] if retenus else min(juges, key=lambda j: gardien.RANG[j["etat"]], default=None)
    d.regles = reference["regles"] if reference else []
    bloquante = ecartes.most_common(1)[0][0] if ecartes and etat == "incoherent" else None
    d.verdict = {"etat": etat, "libelle": LIBELLES[etat], "respectees": passent, "evaluees": len(juges)}
    d.plan = {"ouvert": True, "evalues": len(juges), "passent": passent, "avec_ajustement": avec_ajustement,
              "placements": placements, "critere": CRITERE,
              "regles_de": reference["ticker"] if reference else None,
              "ecartes": [{"raison": r, "nombre": n} for r, n in ecartes.most_common()],
              "bloquante": bloquante}
    d.tracer("Gardien", "juge le plan sur la liste des placements",
             f"{LIBELLES[etat]} : {passent} placement(s) sur {len(juges)} passent toutes les règles, "
             f"{avec_ajustement} avec un ajustement.", [p["faits"][0] for p in placements], debut)

    montant, horizon = d.demande.get("montant_cad"), d.profil.get("horizon_ans")
    pourquoi = []
    if placements:
        noms = ", ".join(f"{p['ticker']} ({p['famille'].lower()})" for p in placements)
        pourquoi.append({"texte": f"Placements de la liste qui passent les règles pour toi : {noms}.",
                         "type": "SCENARIO", "faits": [p["faits"][0] for p in placements]})
        pourquoi.append({"texte": CRITERE, "type": "HYPOTHESE", "faits": []})
    if bloquante:
        pourquoi.append({"texte": f"La règle qui bloque le plus souvent : « {bloquante} ». Change ce point de ta demande "
                                  "pour voir le plan basculer.", "type": "HYPOTHESE", "faits": []})
    d.texte = {
        "source": "code",
        "reformulation": f"Tu as {dollars(montant)} à placer sur {fr(horizon)} an(s), sans placement choisi.",
        "verdict": LIBELLES[etat], "tensions": [], "miroir": [], "pourquoi": pourquoi, "ce_qui_changerait": [],
        "limites": [{"texte": "Ce sont des placements que les règles acceptent pour toi, pas une recommandation : choisis-en "
                              "un pour voir son analyse complète.", "type": "HYPOTHESE", "faits": []}],
        "avertissement": "Simulation éducative. Ceci n'est pas un conseil financier personnalisé.",
    }
    d.tracer("Rédacteur", "explique, sans rien ajouter",
             "Plan ouvert : texte écrit par le code à partir du jugement du Gardien, sans appel de modèle.")
