"""Accès aux modèles sur Amazon Bedrock, avec repli hors ligne.

ALPHAFORGE_LLM :
- "auto" (défaut) : essaie Bedrock ; à la première erreur d'accès (pas d'identifiants,
  clés expirées), on bascule en mode hors ligne pour le reste de la session ;
- "bedrock" : idem, mais signale chaque erreur dans la trace ;
- "off" : jamais d'appel (tests, démo de secours).

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


def appeler(systeme: str, message: str, modele: str | None = None, max_tokens: int = 1200) -> str:
    """Appel à l'API Converse. Renvoie tout le texte de la réponse."""
    if not actif():
        raise LLMIndisponible(raison_indisponible())
    try:
        import boto3  # importé ici pour que le mode hors ligne n'en dépende pas

        if "bedrock" not in _client:
            _client["bedrock"] = boto3.client("bedrock-runtime", region_name=REGION)
        modele = modele or MODELE_PRINCIPAL
        config = {"maxTokens": max_tokens}
        if "anthropic" not in modele:  # les modèles Claude récents refusent le paramètre temperature
            config["temperature"] = 0.2
        reponse = _client["bedrock"].converse(
            modelId=modele,
            system=[{"text": systeme}],
            messages=[{"role": "user", "content": [{"text": message}]}],
            inferenceConfig=config,
        )
    except Exception as e:  # identifiants absents ou expirés, réseau, quota…
        nom_erreur = type(e).__name__
        if nom_erreur in ("NoCredentialsError", "ProfileNotFound", "UnrecognizedClientException",
                          "ExpiredTokenException", "ExpiredToken", "AccessDeniedException",
                          "EndpointConnectionError",
                          "NoRegionError", "ImportError", "ModuleNotFoundError"):
            _etat["indisponible"] = f"Bedrock indisponible ({nom_erreur})"
        raise LLMIndisponible(f"{nom_erreur}: {e}") from e
    # Certains modèles renvoient d'abord un bloc de raisonnement : on concatène tous les blocs texte.
    return "".join(b["text"] for b in reponse["output"]["message"]["content"] if "text" in b)


def extraire_json(texte: str) -> dict:
    debut, fin = texte.find("{"), texte.rfind("}")
    if debut == -1 or fin == -1:
        raise ValueError("aucun objet JSON dans la réponse")
    return json.loads(texte[debut:fin + 1])


def appeler_json(systeme: str, message: str, modele: str | None = None, max_tokens: int = 1500) -> dict:
    return extraire_json(appeler(systeme + "\nRéponds uniquement avec un objet JSON valide, sans texte autour.",
                                 message, modele, max_tokens))


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
