"""Rédacteur : explique le dossier sans rien y ajouter.

Chaque phrase porte une étiquette (FAIT / HYPOTHESE / SCENARIO) et les F-n qui
la soutiennent. Il ne contredit jamais le Gardien et ne dit jamais « achetez ».
Version hors ligne : modèles de phrases. Le LLM (à brancher) reformulera ces
phrases selon le niveau de la personne, puis passera le contrôle d'ancrage.
"""
from __future__ import annotations

import time

from ..dossier import Dossier
from ..format import dollars

INTERDITS = ["achetez", "achète", "vendez", "vends", "je recommande", "je te recommande", "garanti"]


def _phrase(texte: str, type_: str, faits: list[str] | None = None) -> dict:
    return {"texte": texte, "type": type_, "faits": [f for f in (faits or []) if f]}


def executer(d: Dossier) -> None:
    debut = time.perf_counter()
    p, dem, ids, m = d.profil, d.demande, d.demande["ids_faits"], d.demande["mesures"]
    v = d.verdict
    nom = p.get("nom", "toi")
    epargne = p.get("epargne_totale_cad") or 0
    poids = dem["montant_cad"] / epargne * 100 if epargne else 0

    reformulation = (f"{nom} envisage de placer {dollars(dem['montant_cad'])} dans {dem['ticker']}, soit {poids:.0f} % "
                     f"de son épargne, avec un horizon de {p.get('horizon_ans')} an(s).")

    miroir = []
    perte = d.fait(ids["perte"])
    for citation in p.get("citations", [])[:1]:
        miroir.append(_phrase(f"Tu as dit : « {citation} ». Si ce placement revivait sa pire chute observée, "
                              f"il perdrait environ {dollars(abs(perte.valeur))}.",
                              "SCENARIO", [ids["perte"], ids["chute"]]))

    pourquoi = [_phrase(r.explication, "FAIT" if r.niveau != "non_evaluee" else "HYPOTHESE", r.faits)
                for r in d.regles if r.niveau in ("rouge", "orange")]
    if not pourquoi:
        pourquoi = [_phrase(r.explication, "FAIT", r.faits) for r in d.regles if r.niveau == "ok"][:2]

    changerait = []
    if d.options and len(d.options) > 1 and d.options[1].get("changement"):
        ch = d.options[1]["changement"]
        morceaux = []
        if "montant_cad" in ch:
            morceaux.append(f"ramener le montant à {dollars(ch['montant_cad'])}")
        if "horizon_ans" in ch:
            morceaux.append(f"allonger l'horizon à {ch['horizon_ans']} ans")
        changerait.append(_phrase("Ce qui changerait l'avis : " + " et ".join(morceaux) + ".", "HYPOTHESE"))

    limites = [
        _phrase("Les chiffres décrivent la période 2021-2026. Ils ne prédisent pas l'avenir.", "HYPOTHESE"),
        _phrase("Les montants et l'épargne de ce profil sont fictifs.", "SCENARIO"),
    ]
    limites += [_phrase(o.reponse, "HYPOTHESE", [o.cible]) for o in d.objections]

    d.texte = {
        "reformulation": reformulation,
        "verdict": f"{v['libelle']} — {v['respectees']} règle(s) respectée(s) sur {v['evaluees']}.",
        "tensions": p.get("tensions", []),
        "miroir": miroir,
        "pourquoi": pourquoi,
        "ce_qui_changerait": changerait,
        "limites": limites,
        "avertissement": "Simulation éducative. Ceci n'est pas un conseil financier personnalisé.",
    }
    tout = " ".join([reformulation] + [x["texte"] for k in ("miroir", "pourquoi", "ce_qui_changerait")
                                       for x in d.texte[k]]).lower()
    probleme = [mot for mot in INTERDITS if f" {mot} " in f" {tout} "]
    d.tracer("Rédacteur", "explique le dossier",
             "Texte produit, chaque phrase étiquetée et reliée à ses faits."
             + (f" Mots interdits détectés : {probleme}." if probleme else " Contrôle « jamais achetez » : ok."),
             debut=debut)
