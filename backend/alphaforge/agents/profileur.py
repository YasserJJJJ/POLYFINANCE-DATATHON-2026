"""Profileur : comprend la demande, structure le profil, repère ce qui manque.

Le LLM (à brancher) extrait les champs d'une phrase libre. Le code calcule les
jauges. Version hors ligne : correspondance de mots-clés simple.
"""
from __future__ import annotations

import re
import time

from ..donnees import univers
from ..dossier import Dossier
from ..profil import evaluer

MOTS_EFFET_DE_MODE = ["tout le monde", "en parle", "médiatis", "à la mode", "buzz", "hype", "ne pas rater",
                      "exploser", "fusée"]
CHAMPS_ESSENTIELS = {"horizon_ans": "Dans combien d'années penses-tu avoir besoin de cet argent ?",
                     "epargne_totale_cad": "Combien as-tu d'épargne au total, environ ?",
                     "montant_cad": "Quel montant veux-tu placer ?"}


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


def executer(d: Dossier) -> None:
    debut = time.perf_counter()
    texte = d.demande.get("texte", "")
    if not d.demande.get("ticker"):
        d.demande["ticker"] = _trouver_ticker(texte)
    if not d.demande.get("montant_cad"):
        d.demande["montant_cad"] = _trouver_montant(texte)

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
              f"(limite : {ev['limite']}).")
    if d.questions:
        detail += f" {len(d.questions)} question(s) à poser."
    d.tracer("Profileur", "structure le profil", detail, debut=debut)
