"""Accès aux modèles Claude sur Amazon Bedrock.

Désactivé par défaut : sans ALPHAFORGE_LLM=bedrock, chaque agent utilise sa
version déterministe (modèles de texte). Ça permet de développer et de tester
sans compte AWS, et garantit une démo de secours.
"""
from __future__ import annotations

import json
import os

MODELE_LEGER = os.environ.get("ALPHAFORGE_MODELE_LEGER", "")    # ex. un modèle Claude Haiku sur Bedrock
MODELE_PRINCIPAL = os.environ.get("ALPHAFORGE_MODELE", "")       # ex. un modèle Claude Sonnet sur Bedrock
REGION = os.environ.get("AWS_REGION", "ca-central-1")


def actif() -> bool:
    return os.environ.get("ALPHAFORGE_LLM") == "bedrock"


def appeler(systeme: str, message: str, modele: str | None = None, max_tokens: int = 1200) -> str:
    """Appel simple à l'API Converse de Bedrock. Renvoie le texte de la réponse."""
    import boto3  # importé ici pour que le mode hors ligne n'en dépende pas

    client = boto3.client("bedrock-runtime", region_name=REGION)
    reponse = client.converse(
        modelId=modele or MODELE_PRINCIPAL,
        system=[{"text": systeme}],
        messages=[{"role": "user", "content": [{"text": message}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.2},
    )
    return reponse["output"]["message"]["content"][0]["text"]


def appeler_json(systeme: str, message: str, modele: str | None = None) -> dict:
    texte = appeler(systeme + "\nRéponds uniquement avec un objet JSON valide.", message, modele)
    debut, fin = texte.find("{"), texte.rfind("}")
    return json.loads(texte[debut:fin + 1])
