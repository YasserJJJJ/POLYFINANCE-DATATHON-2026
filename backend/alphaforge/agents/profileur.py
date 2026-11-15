"""Profileur : comprend la demande, structure le profil, repère ce qui manque.

Le modèle lit la phrase libre et propose des champs. Le code les VALIDE (symbole
connu, nombres plausibles, secteurs existants) et ne remplit que les champs vides :
une correction faite par la personne n'est jamais écrasée. Le code calcule les jauges.
Repli hors ligne : correspondance de mots-clés.
"""
from __future__ import annotations

import re
import time
from functools import lru_cache

from .. import llm
from ..donnees import univers
from ..dossier import Dossier
from ..profil import evaluer

MOTS_EFFET_DE_MODE = ["tout le monde", "en parle", "médiatis", "à la mode", "buzz", "hype", "ne pas rater",
                      "exploser", "fusée"]
CHAMPS_ESSENTIELS = {"horizon_ans": "Dans combien d'années penses-tu avoir besoin de cet argent ?",
                     "epargne_totale_cad": "Combien as-tu d'épargne au total, environ ?",
                     "montant_cad": "Quel montant veux-tu placer ?"}
CHAMPS_PROFIL = ["horizon_ans", "epargne_totale_cad", "somme_a_preserver_cad", "retrait_prevu_ans",
                 "revenu_stable", "fonds_urgence", "dettes_importantes"]

SYSTEME = """Tu es le Profileur d'un outil éducatif d'aide à la décision d'investissement (simulation).
Tu lis la phrase d'une personne et tu en extrais UNIQUEMENT ce qui y est écrit. Tu ne devines rien :
si une information n'est pas dans la phrase, mets null. Tu ne donnes aucun conseil.
Champs à produire :
- ticker : le symbole du placement visé, choisi STRICTEMENT dans la liste fournie, sinon null
- montant_cad : montant à placer, en dollars canadiens (nombre), sinon null
- epargne_totale_cad : épargne totale déclarée (nombre), sinon null
- somme_a_preserver_cad : somme que la personne ne veut pas risquer (nombre), sinon null
- horizon_ans : dans combien d'années elle aura besoin de l'argent (nombre), sinon null
- retrait_prevu_ans : retrait prévu avant, en années (nombre), sinon null
- revenu_stable, fonds_urgence, dettes_importantes : true / false / null
- exclusions : secteurs que la personne veut éviter, choisis dans la liste fournie (liste, souvent vide)
- envie : ce qu'elle veut, en quelques mots tirés de la phrase, sinon null
- peur : ce qui l'inquiète, en quelques mots tirés de la phrase, sinon null"""


def _catalogue() -> tuple[str, list[str], list[str]]:
    u = univers()
    lignes = [f"{t} : {r['name']}" for t, r in u.iterrows()]
    secteurs = sorted({str(s) for s in u["sector"]})
    return "\n".join(lignes), list(u.index), secteurs


def _nombre(v) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if 0 <= x < 1e9 else None


@lru_cache(maxsize=128)
def extraire_llm(texte: str) -> dict:
    """Extraction par le modèle léger, validée champ par champ. Mise en cache par texte."""
    catalogue, tickers, secteurs = _catalogue()
    brut = llm.appeler_json(SYSTEME, f"Placements possibles :\n{catalogue}\n\nSecteurs possibles : "
                                     f"{', '.join(secteurs)}\n\nPhrase : « {texte} »", llm.MODELE_LEGER, 600)
    propre: dict = {}
    if brut.get("ticker") in tickers:
        propre["ticker"] = brut["ticker"]
    for champ in ["montant_cad", "epargne_totale_cad", "somme_a_preserver_cad", "horizon_ans", "retrait_prevu_ans"]:
        x = _nombre(brut.get(champ))
        if x is not None and (champ not in ("horizon_ans", "retrait_prevu_ans") or x <= 60):
            propre[champ] = x
    for champ in ["revenu_stable", "fonds_urgence", "dettes_importantes"]:
        if isinstance(brut.get(champ), bool):
            propre[champ] = brut[champ]
    exclusions = [s for s in (brut.get("exclusions") or []) if s in secteurs]
    if exclusions:
        propre["exclusions"] = exclusions
    for champ in ["envie", "peur"]:
        if isinstance(brut.get(champ), str) and brut[champ].strip():
            propre[champ] = brut[champ].strip()[:160]
    return propre


def _trouver_ticker(texte: str) -> str | None:
    t = texte.lower()
    for ticker, ligne in univers().iterrows():
        noms = {ticker.lower(), ticker.split(".")[0].split("-")[0].lower(), str(ligne["name"]).lower().split(" ")[0]}
        if any(re.search(rf"\b{re.escape(n)}\b", t) for n in noms if len(n) > 2):
            return ticker
    if "bitcoin" in t:
        return "BTC-USD"
    return None


def _trouver_montant(texte: str) -> float | None:
    m = re.search(r"(\d[\d\s]*)\s*(k|000)?\s*\$", texte.replace(" ", " "))
    if not m:
        return None
    valeur = float(m.group(1).replace(" ", ""))
    return valeur * 1000 if m.group(2) == "k" else valeur


def extraire(texte: str) -> tuple[dict, str]:
    """Renvoie (champs extraits, source). Essaie le modèle, sinon les mots-clés."""
    if texte.strip() and llm.actif():
        try:
            return extraire_llm(texte.strip()), llm.nom(llm.MODELE_LEGER)
        except Exception:
            pass
    champs = {}
    if (t := _trouver_ticker(texte)):
        champs["ticker"] = t
    if (m := _trouver_montant(texte)) is not None:
        champs["montant_cad"] = m
    return champs, "mots-clés (hors ligne)"


def executer(d: Dossier) -> None:
    debut = time.perf_counter()
    texte = d.demande.get("texte", "") or ""
    extraits, source = extraire(texte) if texte else ({}, "aucun texte")

    appliques = {}
    for champ in ("ticker", "montant_cad"):
        if d.demande.get(champ) is None and extraits.get(champ) is not None:
            d.demande[champ] = appliques[champ] = extraits[champ]
    for champ in CHAMPS_PROFIL:
        if d.profil.get(champ) is None and extraits.get(champ) is not None:
            d.profil[champ] = appliques[champ] = extraits[champ]
    if not d.profil.get("exclusions") and extraits.get("exclusions"):
        d.profil["exclusions"] = appliques["exclusions"] = extraits["exclusions"]
    for champ in ("envie", "peur"):
        if extraits.get(champ):
            d.profil[champ] = extraits[champ]
    d.profil["extraits"] = {"champs": appliques, "source": source}

    d.profil["evaluation"] = evaluer(d.profil)
    ev = d.profil["evaluation"]

    for champ, question in CHAMPS_ESSENTIELS.items():
        valeur = d.demande.get(champ) if champ == "montant_cad" else d.profil.get(champ)
        if valeur is None:
            d.questions.append(question)
    if not d.demande.get("ticker"):
        d.questions.append("Quel placement as-tu en tête (nom ou symbole) ?")

    tensions = []
    if any(mot in texte.lower() for mot in MOTS_EFFET_DE_MODE):
        tensions.append("Demande très médiatisée : la décision s'appuie sur l'attention publique plutôt que "
                        "sur ta situation.")
    if ev["tolerance"] is not None and ev["capacite"] is not None and abs(ev["tolerance"] - ev["capacite"]) >= 25:
        tensions.append(f"Écart entre ce que tu veux risquer ({ev['tolerance']:.0f}/100) et ce que ta "
                        f"situation permet ({ev['capacite']:.0f}/100).")
    d.profil["tensions"] = tensions

    detail = (f"Demande comprise : {d.demande.get('ticker')} pour {d.demande.get('montant_cad')} $. "
              f"Tolérance {ev['tolerance']}, capacité {ev['capacite']} → on retient {ev['score_retenu']} "
              f"(limite : {ev['limite']}). Lecture de la phrase : {source}")
    if appliques:
        detail += f", {len(appliques)} champ(s) rempli(s) après validation par le code"
    detail += "."
    if d.questions:
        detail += f" {len(d.questions)} question(s) à poser."
    d.tracer("Profileur", "structure le profil", detail, debut=debut)
