"""Accès aux modèles sur Amazon Bedrock, avec repli hors ligne.

ALPHAFORGE_LLM :
- "auto" (défaut) et "bedrock" (même comportement) : essaie Bedrock ; une erreur d'accès
  suspend brièvement les essais (ALPHAFORGE_REESSAI_SECONDES, 15 s par défaut).
  Un refus propre à un modèle ne suspend pas l'autre ;
  une erreur passagère (quota, délai dépassé) ne fait retomber que l'agent concerné, pour cette analyse ;
- "off" : jamais d'appel (tests, démo de secours).

Délais bornés : 5 s pour se connecter, 40 s pour une réponse, 2 tentatives au plus.

Chaque agent garde une version déterministe : la démo marche même sans réseau.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
from contextlib import contextmanager
from contextvars import ContextVar

# Identifiants recommandés par l'atelier AWS du datathon (profils d'inférence « global »).
MODELE_LEGER = os.environ.get("ALPHAFORGE_MODELE_LEGER", "global.amazon.nova-2-lite-v1:0")
MODELE_PRINCIPAL = os.environ.get("ALPHAFORGE_MODELE", "global.anthropic.claude-sonnet-5")
REGION = os.environ.get("AWS_REGION", "us-east-1")  # région du compte d'équipe du datathon
NOMS = {MODELE_PRINCIPAL: "Claude Sonnet (Bedrock)", MODELE_LEGER: "Nova Lite (Bedrock)"}

_etat = {"indisponible": None}
_client = {}
_verrou = threading.RLock()
_journal: ContextVar[tuple[dict, ...]] = ContextVar("alphaforge_appels", default=())


class LLMIndisponible(Exception):
    pass


def journal_appels() -> list[dict]:
    """Livre puis vide le journal de l'analyse courante (crochet final de l'orchestrateur).

    Les entrées ne contiennent que des métadonnées. L'API ouvre en plus une
    portée dans le fil qui exécute chaque analyse, y compris le flux NDJSON.
    """
    entrees = _journal.get()
    _journal.set(())
    return [dict(e) for e in entrees] if mode() != "off" else []


@contextmanager
def portee_analyse():
    """Isole aussi les analyses interrompues avant le crochet final du dossier."""
    jeton = _journal.set(())
    try:
        yield
    finally:
        _journal.reset(jeton)


def _maintenant() -> float:
    return time.monotonic()


def _delai_reessai() -> float:
    try:
        return min(300, max(1, float(os.environ.get("ALPHAFORGE_REESSAI_SECONDES", "15"))))
    except ValueError:
        return 15


def _actualiser() -> None:
    """Appelé sous verrou ; permet le rétablissement sans redémarrage."""
    maintenant = _maintenant()
    if _etat.get("indisponible") and maintenant >= _etat.get("reessai_a", 0):
        _etat["indisponible"] = None
        _etat.pop("sts_ok", None)
        _client.clear()
    modeles = _etat.setdefault("modeles", {})
    for modele, erreur in list(modeles.items()):
        if maintenant >= erreur["reessai_a"]:
            del modeles[modele]


def _noter_erreur(erreur: Exception, modele: str | None = None) -> None:
    nom_erreur = type(erreur).__name__
    code = getattr(erreur, "response", {}).get("Error", {}).get("Code", nom_erreur)
    raison = f"Bedrock indisponible ({code})"
    # Les identifiants sont communs ; une interdiction d'invoquer un modèle ne l'est pas.
    globales = ("NoCredentialsError", "PartialCredentialsError", "ProfileNotFound",
                "ExpiredTokenException", "ExpiredToken", "InvalidClientTokenId",
                "UnrecognizedClientException", "ImportError", "ModuleNotFoundError", "NoRegionError")
    with _verrou:
        if modele is None or code in globales or nom_erreur in globales:
            _etat.update(indisponible=raison, reessai_a=_maintenant() + _delai_reessai(), sts_ok=False)
            _client.clear()
        elif code in ERREURS_ACCES or nom_erreur in ERREURS_ACCES:
            _etat.setdefault("modeles", {})[modele] = {
                "raison": raison, "reessai_a": _maintenant() + _delai_reessai()}


def mode() -> str:
    return os.environ.get("ALPHAFORGE_LLM", "auto")


def actif(modele: str | None = None) -> bool:
    if mode() == "off":
        return False
    with _verrou:
        _actualiser()
        return _etat["indisponible"] is None and modele not in _etat["modeles"]


def raison_indisponible() -> str | None:
    if mode() == "off":
        return "mode hors ligne demandé (ALPHAFORGE_LLM=off)"
    with _verrou:
        _actualiser()
        return _etat["indisponible"]


def nom(modele: str) -> str:
    return NOMS.get(modele, modele)


ERREURS_ACCES = ("NoCredentialsError", "ProfileNotFound", "UnrecognizedClientException", "ExpiredTokenException",
                 "ExpiredToken", "AccessDeniedException", "EndpointConnectionError", "NoRegionError",
                 "InvalidClientTokenId", "ImportError", "ModuleNotFoundError")


def _config():
    from botocore.config import Config
    return Config(connect_timeout=5, read_timeout=40, retries={"max_attempts": 2, "mode": "standard"})


def _nouveau_client(service: str):
    import boto3  # jamais importé en mode off
    # Session neuve : les identifiants renouvelés sont relus après le délai de reprise.
    return boto3.Session(region_name=REGION).client(service, config=_config())


def acces_verifie() -> bool:
    """Vérifie sans appeler de modèle que des identifiants valides existent.
    Sert à l'indicateur de l'interface : il ne doit pas annoncer Bedrock avant d'avoir pu le joindre."""
    if not actif():
        return False
    with _verrou:
        if _etat.get("sts_ok") and _maintenant() < _etat.get("sts_verifier_a", 0):
            return True
    try:
        _nouveau_client("sts").get_caller_identity()
        with _verrou:
            _etat.update(sts_ok=True, sts_verifier_a=_maintenant() + _delai_reessai())
    except Exception as e:
        _noter_erreur(e)
        return False
    return actif()


def _agent_par_defaut(modele: str, source_ancrage: str | None) -> str:
    """Convention des trois appelants C, en attendant leur argument explicite en T4."""
    if source_ancrage is not None:
        return "Rédacteur"
    return "Profileur" if modele == MODELE_LEGER else "Sceptique"


def _preuve(reponse: dict, debut: float, agent: str, modele: str, garde_fou: str) -> None:
    # Transfert adapté de A : src/datathon2026/agent.py, BedrockAgent._converse.
    # Empreinte et correspondance des champs dans preuves/tranche3/provenance-appels.json.
    entree = {
        "agent": agent, "modele": modele,
        "request_id": reponse.get("ResponseMetadata", {}).get("RequestId"),
        "stop_reason": reponse.get("stopReason"),
        "jetons_entree": reponse.get("usage", {}).get("inputTokens"),
        "jetons_sortie": reponse.get("usage", {}).get("outputTokens"),
        "latence_ms": reponse.get("metrics", {}).get("latencyMs") or round((time.perf_counter() - debut) * 1000),
        "garde_fou": garde_fou,
    }
    _journal.set((*_journal.get(), entree))


def appeler(systeme: str, message: str, modele: str | None = None, max_tokens: int = 1200,
            source_ancrage: str | None = None, agent: str | None = None) -> str:
    """Appel à l'API Converse. Renvoie tout le texte de la réponse."""
    modele = modele or MODELE_PRINCIPAL
    if not actif(modele):
        with _verrou:
            raison = _etat.get("modeles", {}).get(modele, {}).get("raison")
        raise LLMIndisponible(raison or raison_indisponible())
    agent = agent or _agent_par_defaut(modele, source_ancrage)
    debut, tente, garde_fou = time.perf_counter(), False, "absent"
    try:
        with _verrou:
            if "bedrock" not in _client:
                _client["bedrock"] = _nouveau_client("bedrock-runtime")
            client = _client["bedrock"]
        config = {"maxTokens": max_tokens}
        if "anthropic" not in modele:  # les modèles Claude récents refusent le paramètre temperature
            config["temperature"] = 0.2
        contenu = [{"text": message}]
        arguments = dict(modelId=modele, system=[{"text": systeme}], inferenceConfig=config)
        guardrail = os.environ.get("ALPHAFORGE_GUARDRAIL_ID")
        if guardrail and source_ancrage is not None:
            garde_fou = "configure"
            # Bedrock Guardrails, en plus du contrôle en code (jamais à la place). Pour l'ancrage contextuel,
            # Guardrails a besoin de la source à laquelle comparer la réponse : on la marque « grounding_source ».
            arguments["guardrailConfig"] = {"guardrailIdentifier": guardrail,
                                            "guardrailVersion": os.environ.get("ALPHAFORGE_GUARDRAIL_VERSION", "DRAFT"),
                                            "trace": "enabled"}
            # Bedrock limite « query » à une unité de texte (1 000 caractères).
            # Le dossier n'est pas la question : il reste la source, et la consigne
            # complète est contrôlée comme contenu. Seul le Rédacteur fournit
            # cette source ; le catalogue du Profileur n'est pas une réponse à filtrer.
            question = ("Explique la demande et le verdict du dossier fourni. Reformule la demande, "
                        "expose les tensions entre les attentes et la situation, puis explique les règles "
                        "et les faits cités. Reprends uniquement les faits de la source, sans changer "
                        "les calculs ni le verdict.")
            contenu = [{"guardContent": {"text": {"text": source_ancrage[:100_000],
                                                   "qualifiers": ["grounding_source"]}}},
                       {"guardContent": {"text": {"text": question, "qualifiers": ["query"]}}},
                       {"guardContent": {"text": {"text": message, "qualifiers": ["guard_content"]}}}]
        arguments["messages"] = [{"role": "user", "content": contenu}]
        tente = True
        reponse = client.converse(**arguments)
    except Exception as e:  # identifiants absents ou expirés, réseau, quota…
        nom_erreur = type(e).__name__
        if tente:
            metadata = getattr(e, "response", {})
            _preuve({**metadata, "stopReason": "erreur:" + metadata.get("Error", {}).get("Code", nom_erreur)},
                    debut, agent, modele, garde_fou)
        _noter_erreur(e, modele)
        raise LLMIndisponible(f"{nom_erreur}: {e}") from e
    _preuve(reponse, debut, agent, modele,
            "bloque" if reponse.get("stopReason") == "guardrail_intervened" else garde_fou)
    if reponse.get("stopReason") == "guardrail_intervened":
        # Le Guardrail a bloqué la réponse : même traitement qu'un refus du contrôle d'ancrage (repli en code).
        raise LLMIndisponible("guardrail_intervened : réponse bloquée par Bedrock Guardrails")
    # Certains modèles renvoient d'abord un bloc de raisonnement : on concatène tous les blocs texte.
    return "".join(b["text"] for b in reponse["output"]["message"]["content"] if "text" in b)


def extraire_json(texte: str) -> dict:
    debut, fin = texte.find("{"), texte.rfind("}")
    if debut == -1 or fin == -1:
        raise ValueError("aucun objet JSON dans la réponse")
    return json.loads(texte[debut:fin + 1])


def appeler_json(systeme: str, message: str, modele: str | None = None, max_tokens: int = 1500,
                 source_ancrage: str | None = None, agent: str | None = None) -> dict:
    return extraire_json(appeler(systeme + "\nRéponds uniquement avec un objet JSON valide, sans texte autour.",
                                 message, modele, max_tokens, source_ancrage, agent))


_NOMBRE = re.compile(r"\d[\d\s  ]*(?:[.,]\d+)?")


def nombres(texte: str) -> set[float]:
    """Tous les nombres d'un texte, normalisés (12 346 → 12346.0 ; 3,5 → 3.5 ; signe ignoré)."""
    trouves = set()
    for brut in _NOMBRE.findall(texte or ""):
        propre = re.sub(r"[\s  ]", "", brut).replace(",", ".")
        try:
            trouves.add(round(abs(float(propre)), 1))
        except ValueError:
            continue
    return trouves
