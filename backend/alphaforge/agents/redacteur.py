"""Rédacteur : explique le dossier sans rien y ajouter.

Le modèle reformule pour la personne. Le CODE vérifie ensuite son texte (garde-fou
qui empêche, pas qui rappelle) :
- chaque nombre écrit doit déjà exister dans le dossier ;
- chaque F-n cité doit exister ;
- aucun mot de conseil (« achète », « je recommande »…) ;
- chaque phrase porte une étiquette FAIT / HYPOTHESE / SCENARIO.
Un défaut trouvé est NOMMÉ et renvoyé au modèle pour un second essai. S'il persiste,
on garde les phrases modèles, déterministes. Le Rédacteur ne contredit jamais le Gardien.
"""
from __future__ import annotations

import json
import re
import time

from .. import llm
from ..dossier import Dossier
from ..format import dollars

INTERDITS = ["achetez", "achète", "achèterais", "vendez", "vends", "je recommande", "je te recommande",
             "je vous recommande", "garanti", "sans risque", "tu devrais acheter"]
TYPES = {"FAIT", "HYPOTHESE", "SCENARIO"}
SECTIONS = ("reformulation", "miroir", "pourquoi", "ce_qui_changerait")

# Étiquette de l'explication de chaque règle du Gardien :
# - SCENARIO : situation fictive (« si la pire chute se répétait », reste après un placement fictif) ;
# - HYPOTHESE : dépend d'un seuil ou d'un barème choisi par l'équipe (concentration, volatilité > 25 %, 0,8…) ;
# - FAIT : constat observé (secteur lu, temps de récupération mesuré).
TYPE_REGLE = {"capacite": "SCENARIO", "preserver": "SCENARIO", "concentration": "HYPOTHESE",
              "diversification": "HYPOTHESE", "coussin": "HYPOTHESE", "retrait": "HYPOTHESE",
              "horizon": "FAIT", "exclusion": "FAIT", "donnees": "FAIT"}

SYSTEME = """Tu es le Rédacteur d'un outil éducatif qui donne un second avis sur une décision d'investissement
(simulation, jamais de conseil personnalisé). Le verdict est déjà décidé par des règles en code : tu ne le changes
pas, tu l'expliques. Tu tutoies, tu écris en français clair, phrases courtes, sans jargon (ou jargon expliqué).
Adapte le niveau de détail à l'expérience de la personne.

RÈGLES STRICTES :
1. N'écris AUCUN nombre qui n'apparaît pas déjà dans le dossier fourni. Pas de calcul, pas d'arrondi nouveau.
2. Chaque phrase a un type : FAIT (chiffre observé), HYPOTHESE (méthode, limite, seuil choisi) ou SCENARIO
   (situation fictive, ex. « si la pire chute se répétait »). Cite les identifiants F-n qui la soutiennent.
3. Ne dis jamais d'acheter, de vendre, ni « je recommande ». Ne promets rien.
4. Le « miroir » met en regard UNE phrase de la personne (citée mot pour mot) et ce que montrent les chiffres.

Format JSON :
{"reformulation": "<une phrase qui reformule la demande>",
 "miroir": [{"texte": "...", "type": "SCENARIO", "faits": ["F-7"]}],
 "pourquoi": [{"texte": "...", "type": "FAIT", "faits": ["F-2"]}],
 "ce_qui_changerait": [{"texte": "...", "type": "HYPOTHESE", "faits": []}]}
"pourquoi" : 2 à 4 phrases, en commençant par ce qui pèse le plus dans le verdict."""


def _phrase(texte: str, type_: str, faits: list[str] | None = None) -> dict:
    return {"texte": texte, "type": type_, "faits": [f for f in (faits or []) if f]}


def _limite_objection(o) -> dict:
    """Une vérification du Sceptique qui a produit une mesure est un FAIT qui cite le fait recalculé ;
    une limite de méthode (fenêtre courte, borne minimale) est une HYPOTHESE."""
    ids = re.findall(r"F-\d+", o.reponse)
    if o.reponse.startswith(("Recalcul fait", "Vérifié", "Comparaison faite")):
        return _phrase(o.reponse, "FAIT", ids or [o.cible])
    return _phrase(o.reponse, "HYPOTHESE", [o.cible])


def _modele_de_phrases(d: Dossier) -> dict:
    """Version déterministe : sert de repli et de référence."""
    p, dem, ids = d.profil, d.demande, d.demande["ids_faits"]
    nom = p.get("nom", "toi")
    epargne = p.get("epargne_totale_cad") or 0
    poids = dem["montant_cad"] / epargne * 100 if epargne else 0
    reformulation = (f"{nom} envisage de placer {dollars(dem['montant_cad'])} dans {dem['ticker']}, soit {poids:.0f} % "
                     f"de son épargne, avec un horizon de {p.get('horizon_ans')} an(s).")
    miroir = []
    perte = d.fait(ids["perte"])
    for citation in p.get("citations", [])[:1]:
        miroir.append(_phrase(f"Tu as dit : « {citation} ». Si ce placement revivait sa pire chute observée, "
                              f"il perdrait environ {dollars(abs(perte.valeur))}.", "SCENARIO", [ids["perte"], ids["chute"]]))
    pourquoi = [_phrase(r.explication, TYPE_REGLE.get(r.code, "HYPOTHESE"), r.faits)
                for r in d.regles if r.niveau in ("rouge", "orange", "gris")]
    if not pourquoi:
        pourquoi = [_phrase(r.explication, TYPE_REGLE.get(r.code, "HYPOTHESE"), r.faits)
                    for r in d.regles if r.niveau == "ok"][:2]
    changerait = []
    aj = next((o for o in d.options if o.get("changement")), None)
    if aj:
        ch, morceaux = aj["changement"], []
        if "montant_cad" in ch:
            morceaux.append(f"ramener le montant à {dollars(ch['montant_cad'])}")
        if "horizon_ans" in ch:
            morceaux.append(f"allonger l'horizon à {ch['horizon_ans']} ans")
        changerait.append(_phrase("Ce qui changerait l'avis : " + " et ".join(morceaux) + ".", "SCENARIO"))
    alt = next((o for o in d.options if o.get("ticker") and o.get("ticker") != dem["ticker"]), None)
    if alt:
        changerait.append(_phrase(f"Une option compatible avec tes exclusions existe : {alt['ticker']} "
                                  f"({alt.get('libelle_actif', '')}), même montant.", "SCENARIO", alt.get("faits")))
    return {"reformulation": reformulation, "miroir": miroir, "pourquoi": pourquoi, "ce_qui_changerait": changerait}


def _dossier_pour_modele(d: Dossier, base: dict) -> str:
    p = d.profil
    resume = {
        "personne": {k: p.get(k) for k in ("nom", "age", "experience", "horizon_ans", "epargne_totale_cad",
                                            "somme_a_preserver_cad", "exclusions", "envie", "peur")},
        "ses_mots": p.get("citations", []) + ([d.demande.get("texte")] if d.demande.get("texte") else []),
        "jauges": {k: p["evaluation"].get(k) for k in ("tolerance", "capacite", "score_retenu", "limite",
                                                        "perte_max_retenue_pct")},
        "demande": {k: d.demande.get(k) for k in ("ticker", "montant_cad")},
        "verdict": d.verdict,
        "regles": [{"libelle": r.libelle, "niveau": r.niveau, "explication": r.explication, "faits": r.faits}
                   for r in d.regles],
        "faits": [{"id": f.id, "libelle": f.libelle, "valeur": f.valeur, "unite": f.unite, "type": f.type}
                  for f in d.faits],
        "options": d.options,
        "tensions": p.get("tensions", []),
        "phrases_de_reference": base,
    }
    return json.dumps(resume, ensure_ascii=False, default=str)


def _nombres_autorises(d: Dossier, base: dict) -> set[float]:
    sources = [json.dumps(base, ensure_ascii=False), json.dumps(d.options, default=str),
               json.dumps(d.verdict), json.dumps(d.profil.get("evaluation", {}), default=str),
               " ".join(r.explication for r in d.regles), " ".join(d.profil.get("citations", [])),
               d.demande.get("texte", "") or ""]
    for f in d.faits:
        sources.append(f"{f.valeur} {f.methode} {f.libelle}")
        if isinstance(f.valeur, (int, float)):
            sources.append(str(abs(f.valeur)))
    for champ in ("epargne_totale_cad", "somme_a_preserver_cad", "horizon_ans", "retrait_prevu_ans", "age"):
        if d.profil.get(champ) is not None:
            sources.append(str(d.profil[champ]))
    autorises = set()
    for s in sources:
        autorises |= llm.nombres(s)
    return autorises | {float(i) for i in range(0, 11)}


def verifier(texte_json: dict, autorises: set[float], ids_valides: set[str]) -> list[str]:
    """Renvoie la liste des défauts NOMMÉS (vide = texte accepté)."""
    defauts = []
    # Toujours permis : petits entiers (« 3 options », « 2 ans ») et l'échelle des jauges (« 30/100 »).
    autorises = autorises | {float(i) for i in range(0, 11)} | {100.0}
    if not isinstance(texte_json.get("reformulation"), str) or not texte_json["reformulation"].strip():
        defauts.append("la reformulation est absente")
    phrases = [texte_json.get("reformulation", "")]
    for section in SECTIONS[1:]:
        for ph in texte_json.get(section, []) or []:
            if not isinstance(ph, dict) or not str(ph.get("texte", "")).strip():
                defauts.append(f"une phrase de « {section} » est vide ou mal formée")
                continue
            if ph.get("type") not in TYPES:
                defauts.append(f"la phrase « {ph['texte'][:50]}… » a un type invalide ({ph.get('type')})")
            inconnus = [f for f in ph.get("faits", []) if f not in ids_valides]
            if inconnus:
                defauts.append(f"tu cites des faits qui n'existent pas : {', '.join(inconnus)}")
            phrases.append(ph["texte"])
    if not texte_json.get("pourquoi"):
        defauts.append("la section « pourquoi » est vide")
    for ph in phrases:
        en_trop = sorted(n for n in llm.nombres(ph) if n not in autorises)
        if en_trop:
            defauts.append(f"nombre(s) absent(s) du dossier : {', '.join(str(n).rstrip('0').rstrip('.') for n in en_trop)} "
                           f"dans « {ph[:60]}… »")
        bas = f" {ph.lower()} "
        mots = [m for m in INTERDITS if re.search(rf"\b{re.escape(m)}\b", bas)]
        if mots:
            defauts.append(f"mot(s) de conseil interdit(s) : {', '.join(mots)}")
    return defauts


def executer(d: Dossier) -> None:
    debut = time.perf_counter()
    base = _modele_de_phrases(d)
    texte, source, journal = base, "modèles de phrases (hors ligne)", []

    if llm.actif():
        autorises = _nombres_autorises(d, base)
        ids_valides = {f.id for f in d.faits}
        consigne = _dossier_pour_modele(d, base)
        for essai in (1, 2):
            try:
                propose = llm.appeler_json(SYSTEME, consigne, llm.MODELE_PRINCIPAL, 1800)
            except Exception as e:
                journal.append(f"essai {essai} : réponse inutilisable ({type(e).__name__})")
                break
            defauts = verifier(propose, autorises, ids_valides)
            if not defauts:
                texte = {k: propose.get(k, base[k]) for k in SECTIONS}
                source = llm.nom(llm.MODELE_PRINCIPAL)
                journal.append(f"essai {essai} : accepté par le contrôle d'ancrage")
                break
            journal.append(f"essai {essai} : refusé — " + " ; ".join(defauts[:3]))
            # Boucle fermée : le défaut nommé devient la consigne du prochain essai.
            consigne += ("\n\nDéfauts de ta réponse précédente, détectés par le contrôle automatique : "
                         + " ; ".join(defauts) + ". Ne les reproduis pas.")
        else:
            journal.append("repli sur les modèles de phrases")
        if source != llm.nom(llm.MODELE_PRINCIPAL) and journal and not journal[-1].startswith("repli"):
            journal.append("repli sur les modèles de phrases")
    elif llm.raison_indisponible():
        journal.append(llm.raison_indisponible())

    limites = [
        _phrase("Les chiffres décrivent la période 2021-2026. Ils ne prédisent pas l'avenir.", "HYPOTHESE"),
        _phrase("Les montants et l'épargne de ce profil sont fictifs.", "SCENARIO"),
    ] + [_limite_objection(o) for o in d.objections]

    v = d.verdict
    d.texte = {
        **texte,
        "verdict": f"{v['libelle']} : {v['respectees']} règle(s) respectée(s) sur {v['evaluees']}.",
        "tensions": d.profil.get("tensions", []),
        "limites": limites,
        "avertissement": "Simulation éducative. Ceci n'est pas un conseil financier personnalisé.",
        "source": source,
        "controle": journal,
    }
    d.tracer("Rédacteur", "explique le dossier, puis passe le contrôle d'ancrage",
             f"Texte : {source}. " + (" · ".join(journal) if journal else "Contrôle « jamais achetez » : ok."),
             debut=debut)
