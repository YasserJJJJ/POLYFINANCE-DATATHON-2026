"""Accès aux modèles sur Amazon Bedrock, avec repli hors ligne.

ALPHAFORGE_LLM :
- "auto" (défaut) et "bedrock" (même comportement) : essaie Bedrock ; à la première erreur d'accès
  (pas d'identifiants, clés expirées), on bascule en mode hors ligne pour le reste de la session ;
  une erreur passagère (quota, délai dépassé) ne fait retomber que l'agent concerné, pour cette analyse ;
- "off" : jamais d'appel (tests, démo de secours).

Délais bornés : 5 s pour se connecter, 40 s pour une réponse, 2 tentatives au plus.

Chaque agent garde une version déterministe : la démo marche même sans réseau.
"""
from __future__ import annotations

import json
import os
import re

# Identifiants recommandés par l'atelier AWS du datathon (profils d'inférence « global »).
MODELE_LEGER = os.environ.get("ALPHAFORGE_MODELE_LEGER", "global.amazon.nova-2-lite-v1:0")
MODELE_PRINCIPAL = os.environ.get("ALPHAFORGE_MODELE", "global.anthropic.claude-sonnet-5")
REGION = os.environ.get("AWS_REGION", "us-east-1")  # région du compte d'équipe du datathon
NOMS = {MODELE_PRINCIPAL: "Claude Sonnet (Bedrock)", MODELE_LEGER: "Nova Lite (Bedrock)"}

_etat = {"indisponible": None}
_client = {}


class LLMIndisponible(Exception):
    pass


def journal_appels() -> list[dict]:
    """Point de branchement K6 ; la tranche 3 instrumentera les appels Bedrock."""
    return []


def mode() -> str:
    return os.environ.get("ALPHAFORGE_LLM", "auto")


def actif() -> bool:
    return mode() != "off" and _etat["indisponible"] is None


def raison_indisponible() -> str | None:
    if mode() == "off":
        return "mode hors ligne demandé (ALPHAFORGE_LLM=off)"
    return _etat["indisponible"]


def nom(modele: str) -> str:
    return NOMS.get(modele, modele)


ERREURS_ACCES = ("NoCredentialsError", "ProfileNotFound", "UnrecognizedClientException", "ExpiredTokenException",
                 "ExpiredToken", "AccessDeniedException", "EndpointConnectionError", "NoRegionError",
                 "InvalidClientTokenId", "ImportError", "ModuleNotFoundError")


def _config():
    from botocore.config import Config
    return Config(connect_timeout=5, read_timeout=40, retries={"max_attempts": 2, "mode": "standard"})


def acces_verifie() -> bool:
    """Vérifie une fois, sans appeler de modèle (STS, gratuit), que des identifiants valides existent.
    Sert à l'indicateur de l'interface : il ne doit pas annoncer Bedrock avant d'avoir pu le joindre."""
    if not actif():
        return False
    if "sts_ok" not in _etat:
        try:
            import boto3
            boto3.client("sts", region_name=REGION, config=_config()).get_caller_identity()
            _etat["sts_ok"] = True
        except Exception as e:
            _etat["sts_ok"] = False
            _etat["indisponible"] = f"Bedrock indisponible ({type(e).__name__})"
    return bool(_etat["sts_ok"]) and actif()


def appeler(systeme: str, message: str, modele: str | None = None, max_tokens: int = 1200,
            source_ancrage: str | None = None) -> str:
    """Appel à l'API Converse. Renvoie tout le texte de la réponse."""
    if not actif():
        raise LLMIndisponible(raison_indisponible())
    try:
        import boto3  # importé ici pour que le mode hors ligne n'en dépende pas

        if "bedrock" not in _client:
            _client["bedrock"] = boto3.client("bedrock-runtime", region_name=REGION, config=_config())
        modele = modele or MODELE_PRINCIPAL
        config = {"maxTokens": max_tokens}
        if "anthropic" not in modele:  # les modèles Claude récents refusent le paramètre temperature
            config["temperature"] = 0.2
        contenu = [{"text": message}]
        arguments = dict(modelId=modele, system=[{"text": systeme}], inferenceConfig=config)
        guardrail = os.environ.get("ALPHAFORGE_GUARDRAIL_ID")
        if guardrail:
            # Bedrock Guardrails, en plus du contrôle en code (jamais à la place). Pour l'ancrage contextuel,
            # Guardrails a besoin de la source à laquelle comparer la réponse : on la marque « grounding_source ».
            arguments["guardrailConfig"] = {"guardrailIdentifier": guardrail,
                                            "guardrailVersion": os.environ.get("ALPHAFORGE_GUARDRAIL_VERSION", "DRAFT"),
                                            "trace": "enabled"}
            if source_ancrage:
                contenu = [{"guardContent": {"text": {"text": source_ancrage[:100_000], "qualifiers": ["grounding_source"]}}},
                           {"guardContent": {"text": {"text": message[:5_000], "qualifiers": ["query"]}}},
                           {"text": message}]
        arguments["messages"] = [{"role": "user", "content": contenu}]
        reponse = _client["bedrock"].converse(**arguments)
    except Exception as e:  # identifiants absents ou expirés, réseau, quota…
        nom_erreur = type(e).__name__
        code = getattr(e, "response", {}).get("Error", {}).get("Code", "") if hasattr(e, "response") else ""
        if nom_erreur in ERREURS_ACCES or code in ERREURS_ACCES:  # erreur d'accès : on passe hors ligne
            _etat["indisponible"] = f"Bedrock indisponible ({nom_erreur})"
        raise LLMIndisponible(f"{nom_erreur}: {e}") from e
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
                 source_ancrage: str | None = None) -> dict:
    return extraire_json(appeler(systeme + "\nRéponds uniquement avec un objet JSON valide, sans texte autour.",
                                 message, modele, max_tokens, source_ancrage))


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
