"""Question de précision posée après le verdict, dans la conversation : le Rédacteur répond sur le dossier.

Mêmes garde-fous que le texte du verdict : aucun nombre absent du dossier, aucune formule de conseil, aucun
calcul écrit en lettres, aucune contradiction du verdict. Si un contrôle échoue, on ne montre pas la réponse
du modèle : on le dit, et on renvoie vers le détail.
"""
from __future__ import annotations

import json

from . import llm
from .agents.redacteur import contredit_le_verdict
from .garde_fous import mots_de_conseil, rapport_calcule

SYSTEME = """Tu es le Rédacteur d'un outil de second avis (simulation éducative, pas de conseil).
Une personne pose une question sur SON dossier d'analyse, fourni ci-dessous.
Réponds en 2 à 4 phrases, en français, en la tutoyant, avec des mots simples (explique un terme technique en le citant).
Tu n'utilises QUE des nombres présents dans le dossier ; tu n'en calcules aucun, ni en chiffres ni en lettres.
Tu ne dis jamais d'acheter, de vendre ou que tu recommandes quelque chose. Tu ne contredis jamais le verdict.
N'écris jamais d'identifiant comme F-3 dans ta réponse : mets les identifiants des faits utilisés dans « faits ».
Si le dossier ne permet pas de répondre, dis-le et dis quelle information de la demande changerait la réponse.
Format : {"reponse": "<texte>", "faits": ["F-3"]}"""

REPLI = ("Je ne peux pas répondre à cette question à partir des chiffres de ton dossier sans risquer d'en inventer. "
         "Ouvre « Le détail » pour voir toutes les règles et leurs sources, ou change ta demande.")
PETITS = {1.0, 2.0, 3.0, 4.0, 5.0, 10.0, 12.0, 100.0}


def _contexte(dossier: dict) -> str:
    utile = {
        "demande": {k: (dossier.get("demande") or {}).get(k) for k in ("texte", "ticker", "montant_cad")},
        "verdict": dossier.get("verdict"),
        "reformulation": (dossier.get("texte") or {}).get("reformulation"),
        "regles": [{k: r.get(k) for k in ("libelle", "niveau", "explication")} for r in dossier.get("regles") or []],
        "faits": [{k: f.get(k) for k in ("id", "libelle", "valeur", "unite", "type")} for f in dossier.get("faits") or []],
        "options": [{k: o.get(k) for k in ("nom", "ticker", "montant_cad", "horizon_ans", "etat", "note")}
                    for o in dossier.get("options") or []],
        "plan": {k: (dossier.get("plan") or {}).get(k) for k in ("passent", "evalues", "placements", "bloquante")}
        if dossier.get("plan") else None,
    }
    return json.dumps(utile, ensure_ascii=False, default=str)


def repondre(dossier: dict, question: str) -> dict:
    question = (question or "").strip()[:500]
    if not question:
        return {"reponse": "Écris ta question, ou ce que tu veux changer dans ta demande.", "faits": [], "source": "code"}
    if not llm.actif():
        return {"reponse": "Les agents sont hors ligne : la réponse détaillée se trouve dans « Le détail ».",
                "faits": [], "source": "hors ligne"}
    contexte = _contexte(dossier)
    try:
        brut = llm.appeler_json(SYSTEME, f"Dossier : {contexte}\n\nQuestion : {question}", llm.MODELE_PRINCIPAL, 600,
                                agent="Rédacteur")
    except Exception as e:  # noqa: BLE001 - réponse inutilisable ou modèle indisponible : on le dit
        return {"reponse": REPLI, "faits": [], "source": f"repli ({type(e).__name__})"}
    reponse = str(brut.get("reponse", "")).strip()[:900]
    etat = (dossier.get("verdict") or {}).get("etat")
    defauts = []
    if not reponse:
        defauts.append("réponse vide")
    if mots_de_conseil(reponse):
        defauts.append("formule de conseil")
    if rapport_calcule(reponse):
        defauts.append("calcul écrit en lettres")
    if llm.nombres(reponse) - llm.nombres(contexte) - llm.nombres(question) - PETITS:
        defauts.append("nombre absent du dossier")
    if contredit_le_verdict(reponse, etat):
        defauts.append("contredit le verdict")
    if defauts:
        return {"reponse": REPLI, "faits": [], "source": "refus du contrôle : " + ", ".join(defauts)}
    ids = {f.get("id") for f in dossier.get("faits") or []}
    faits = [f for f in brut.get("faits") or [] if isinstance(f, str) and f in ids]
    return {"reponse": reponse, "faits": faits, "source": llm.nom(llm.MODELE_PRINCIPAL)}
