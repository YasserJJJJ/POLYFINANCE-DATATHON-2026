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
from ..garde_fous import mots_de_conseil, rapport_calcule, sans_accents

TYPES = {"FAIT", "HYPOTHESE", "SCENARIO"}
SECTIONS = ("reformulation", "miroir", "pourquoi", "ce_qui_changerait")
# Sections rédigées par le modèle. « ce_qui_changerait » reste écrit par le code : seul le Gardien sait ce qui
# change le verdict (un modèle a déjà inventé un levier inexistant et un seuil faux dans cette section).
SECTIONS_MODELE = ("reformulation", "miroir", "pourquoi")

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
 "pourquoi": [{"texte": "...", "type": "FAIT", "faits": ["F-2"]}]}
"pourquoi" : 2 à 4 phrases, en commençant par ce qui pèse le plus dans le verdict.
Ne parle pas de ce qui changerait le verdict : cette partie est calculée par le code."""


def _phrase(texte: str, type_: str, faits: list[str] | None = None) -> dict:
    return {"texte": texte, "type": type_, "faits": [f for f in (faits or []) if f]}


def _limite_objection(o) -> dict:
    """Une vérification du Sceptique qui a produit une mesure est un FAIT qui cite le fait recalculé ;
    une limite de méthode (fenêtre courte, borne minimale) est une HYPOTHESE."""
    ids = re.findall(r"F-\d+", o.reponse)
    if o.reponse.startswith(("Recalcul fait", "Vérifié", "Comparaison faite")):
        return _phrase(o.reponse, "FAIT", ids or [o.cible])
    return _phrase(o.reponse, "HYPOTHESE", [o.cible])


def _est_persona(d: Dossier) -> bool:
    from ..personas import PERSONAS
    return d.profil.get("nom") in {v["profil"]["nom"] for v in PERSONAS.values()}


def _modele_de_phrases(d: Dossier) -> dict:
    """Version déterministe : sert de repli et de référence."""
    p, dem, ids = d.profil, d.demande, d.demande["ids_faits"]
    nom = p.get("nom") or "Toi"
    epargne = p.get("epargne_totale_cad")
    toi = nom.lower() == "toi"
    sujet, verbe, sa = ("Tu", "envisages", "ton") if toi else (nom, "envisage", "son")
    morceaux = [f"{sujet} {verbe} de placer {dollars(dem['montant_cad'])} dans {dem['ticker']}"]
    if isinstance(epargne, (int, float)) and epargne > 0 and isinstance(dem.get("montant_cad"), (int, float)):
        morceaux.append(f"soit {dem['montant_cad'] / epargne * 100:.0f} % de {sa} épargne")
    if p.get("horizon_ans") is not None:
        morceaux.append(f"avec un horizon de {p.get('horizon_ans')} an(s)")
    reformulation = ", ".join(morceaux) + "."
    miroir = []
    perte = d.fait(ids["perte"])
    # Une citation qui contient elle-même une formule de conseil (« achète maintenant ») n'est pas reprise.
    for citation in [c for c in p.get("citations", []) if not mots_de_conseil(c)][:1]:
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


DATE_ISO = re.compile(r"(\d{4})-\d{2}-\d{2}")
CITATION = re.compile(r"«\s*(.+?)\s*»")
# Un petit entier n'est toléré que sans unité (« 3 options ») : « 3 ans » ou « 3 % » doit venir du dossier.
AVEC_UNITE = re.compile(r"(\d[\d\s  ]*(?:[.,]\d+)?)\s*(?:%|\$|ans?\b|an\(s\)|fois\b|mois\b|points?\b)")
PETITS = {float(i) for i in range(0, 11)} | {100.0}
NOTATION = re.compile(r"\d\s*[kK]\b|\d[eE][+-]?\d")


def _nombres_exacts(texte: str) -> set[float]:
    """Comme llm.nombres, mais sans arrondi : 70,94 reste 70.94 (différent de 70,9)."""
    out = set()
    for brut in llm._NOMBRE.findall(texte or ""):
        try:
            out.add(abs(float(re.sub(r"[\s  ]", "", brut).replace(",", "."))))
        except ValueError:
            continue
    return out


def _normaliser(s: str) -> str:
    s = s.lower().replace("’", "'").replace("\u202f", " ").replace("\xa0", " ")
    return re.sub(r"\s+", " ", re.sub(r"[«»\"“”.,!?;:]", " ", s)).strip()


def _mots_de_la_personne(d: Dossier) -> list[str]:
    return [m for m in d.profil.get("citations", []) + [d.demande.get("texte") or ""] if m]


def _nombres_autorises(d: Dossier, base: dict) -> set[float]:
    """Nombres du dossier. La phrase libre et les citations n'en font PAS partie : un nombre écrit par la
    personne (« Tesla va monter de 300 % ») ne doit jamais devenir un chiffre présenté comme établi.
    Ses mots restent citables mot pour mot, entre « », et sont contrôlés à part."""
    ev = {k: v for k, v in d.profil.get("evaluation", {}).items() if k != "capacite_raisons"}
    sources = [json.dumps(base, ensure_ascii=False), json.dumps(d.options, default=str),
               json.dumps(d.verdict), json.dumps(ev, default=str), " ".join(r.explication for r in d.regles)]
    for f in d.faits:
        sources.append(f"{f.valeur} {f.methode} {f.libelle}")
        if isinstance(f.valeur, (int, float)):
            sources.append(str(abs(f.valeur)))
    for champ in ("epargne_totale_cad", "somme_a_preserver_cad", "horizon_ans", "retrait_prevu_ans", "age"):
        if d.profil.get(champ) is not None:
            sources.append(str(d.profil[champ]))
    for champ in ("montant_cad",):
        if d.demande.get(champ) is not None:
            sources.append(str(d.demande[champ]))
    autorises = set()
    for s in sources:
        s = DATE_ISO.sub(lambda m: m.group(1), s)   # 2023-01-03 → 2023 : le jour et le mois n'autorisent rien
        autorises |= _nombres_exacts(s) | llm.nombres(s)
    return autorises


MARQUE_SCENARIO = re.compile(r"\bsi\b.{0,80}\b(?:se repetait|revivait|survenait|se reproduisait|retombait)\b"
                             r"|\bferait (?:baisser|perdre|passer)\b|\bperdrait\b|\bbaisserait\b")
MARQUE_HYPOTHESE = re.compile(r"\bseuils?\b|\blimites?\b|/100|capacite de perte|\bbaremes?\b")


def etiquette_juste(texte: str, type_: str, faits: list[str]) -> str:
    """Étiquette que le code impose : une situation fictive est un SCENARIO ; une phrase qui repose sur un
    seuil ou un barème de l'équipe est une HYPOTHESE ; un FAIT sans aucun F-n n'est pas un fait vérifiable."""
    bas = sans_accents(texte.lower())
    if MARQUE_SCENARIO.search(bas):
        return "SCENARIO"
    if type_ == "FAIT" and (MARQUE_HYPOTHESE.search(bas) or not faits):
        return "HYPOTHESE"
    return type_


def corriger_etiquettes(texte: dict) -> tuple[dict, list[str]]:
    """Corrige en code les étiquettes du modèle (au lieu de refuser tout le texte) et dit ce qui a changé."""
    corrections, sortie = [], dict(texte)
    for section in ("miroir", "pourquoi", "ce_qui_changerait"):
        phrases = []
        for ph in texte.get(section) or []:
            juste = etiquette_juste(ph["texte"], ph["type"], ph.get("faits") or [])
            if juste != ph["type"]:
                corrections.append(f"« {ph['texte'][:40]}… » : {ph['type']} → {juste}")
            phrases.append({**ph, "type": juste})
        sortie[section] = phrases
    return sortie, corrections


# Affirmations d'un état au présent (« ta demande est cohérente »). Le conditionnel (« serait », « si ») reste permis.
DIT_COHERENT = re.compile(r"(?<!in)coherente?s? avec ta situation|(?:est|reste) (?:tout a fait |bien )?(?<!in)coherente?s?"
                          r"|toutes les regles sont respectees")
DIT_INCOHERENT = re.compile(r"(?:est|reste) (?:tout a fait |bien )?incoherente?s?|incoherente?s? avec ta situation")


def contredit_le_verdict(phrase: str, etat: str | None) -> bool:
    bas = sans_accents(phrase.lower())
    if not etat or re.search(r"\bsi\b|\bserait\b|\bdeviendrait\b|\bpas coherent", bas) or "ajust" in bas:
        return False
    return bool((DIT_COHERENT.search(bas) and etat != "coherent") or (DIT_INCOHERENT.search(bas) and etat != "incoherent"))


def verifier(texte_json: dict, autorises: set[float], ids_valides: set[str],
             ses_mots: list[str] | None = None, etat: str | None = None) -> list[str]:
    """Renvoie la liste des défauts NOMMÉS (vide = texte accepté). Ne lève jamais d'exception :
    une réponse mal formée du modèle devient un défaut, pas une panne de l'analyse."""
    defauts = []
    if not isinstance(texte_json, dict):
        return ["la réponse n'est pas un objet JSON"]
    reform = texte_json.get("reformulation")
    if not isinstance(reform, str) or not reform.strip():
        defauts.append("la reformulation est absente")
        reform = ""
    phrases = [reform]
    for section in SECTIONS_MODELE[1:]:
        bloc = texte_json.get(section) or []
        if not isinstance(bloc, list):
            defauts.append(f"la section « {section} » n'est pas une liste")
            continue
        for ph in bloc:
            if not isinstance(ph, dict) or not isinstance(ph.get("texte"), str) or not ph["texte"].strip():
                defauts.append(f"une phrase de « {section} » est vide ou mal formée")
                continue
            faits = ph.get("faits") or []
            if not isinstance(faits, list) or not all(isinstance(f, str) for f in faits):
                defauts.append(f"la liste des faits de « {ph['texte'][:50]}… » est mal formée")
                faits = []
            if ph.get("type") not in TYPES:
                defauts.append(f"la phrase « {ph['texte'][:50]}… » a un type invalide ({ph.get('type')})")
            inconnus = [f for f in faits if f not in ids_valides]
            if inconnus:
                defauts.append(f"tu cites des faits qui n'existent pas : {', '.join(inconnus)}")
            phrases.append(ph["texte"])
    if not texte_json.get("pourquoi"):
        defauts.append("la section « pourquoi » est vide")
    mots = [_normaliser(m) for m in (ses_mots or [])]
    for ph in phrases:
        # Citations : mot pour mot dans les mots de la personne ; leurs nombres sont alors les siens, pas des faits.
        hors_citation = ph
        for c in CITATION.findall(ph):
            if ses_mots is not None and not any(_normaliser(c) in m for m in mots):
                defauts.append(f"citation non textuelle : « {c[:50]} »")
            else:
                hors_citation = hors_citation.replace(c, " ")
        if NOTATION.search(hors_citation):
            defauts.append(f"notation de nombre ambiguë dans « {ph[:60]}… » : écris le nombre en entier")
        en_trop = {n for n in _nombres_exacts(hors_citation) if n not in autorises and n not in PETITS}
        for brut in AVEC_UNITE.findall(hors_citation):
            en_trop |= {n for n in _nombres_exacts(brut) if n not in autorises}
        if en_trop:
            defauts.append(f"nombre(s) absent(s) du dossier : {', '.join(f'{n:g}' for n in sorted(en_trop))} "
                           f"dans « {ph[:60]}… »")
        if rapport_calcule(hors_citation):
            defauts.append(f"rapport ou quantité en lettres dans « {ph[:50]}… » : aucun calcul, cite les chiffres du dossier")
        if contredit_le_verdict(ph, etat):
            defauts.append(f"« {ph[:50]}… » contredit le verdict du Gardien ({etat}) : tu ne changes pas le verdict")
        interdits = mots_de_conseil(ph)
        if interdits:
            defauts.append(f"mot(s) de conseil interdit(s) : {', '.join(interdits)}")
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
                defauts = verifier(propose, autorises, ids_valides, _mots_de_la_personne(d), d.verdict.get("etat"))
            except Exception as e:
                journal.append(f"essai {essai} : réponse inutilisable ({type(e).__name__})")
                break
            if not defauts:
                texte, corrections = corriger_etiquettes(
                    {**base, **{k: propose.get(k, base[k]) for k in SECTIONS_MODELE}})
                source = llm.nom(llm.MODELE_PRINCIPAL)
                journal.append(f"essai {essai} : accepté par le contrôle d'ancrage")
                if corrections:
                    journal.append(f"{len(corrections)} étiquette(s) corrigée(s) par le code : "
                                   + " ; ".join(corrections[:3]))
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
        (_phrase("Les montants et l'épargne de ce profil sont fictifs (scénario de l'équipe).", "SCENARIO")
         if _est_persona(d) else
         _phrase("Les montants sont ceux que tu as saisis : ils ne sont pas vérifiés, l'analyse reste une simulation.",
                 "HYPOTHESE")),
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
