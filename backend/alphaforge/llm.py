"""Accès aux modèles Claude sur Amazon Bedrock.

Désactivé par défaut : sans ALPHAFORGE_LLM=bedrock, chaque agent utilise sa
version déterministe (modèles de texte). Ça permet de développer et de tester
sans compte AWS, et garantit une démo de secours.
"""
from __future__ import annotations

import json
import os

# Identifiants recommandés par l'atelier AWS du datathon (profils d'inférence « global »).
MODELE_LEGER = os.environ.get("ALPHAFORGE_MODELE_LEGER", "global.amazon.nova-2-lite-v1:0")
MODELE_PRINCIPAL = os.environ.get("ALPHAFORGE_MODELE", "global.anthropic.claude-sonnet-5")
REGION = os.environ.get("AWS_REGION", "us-east-1")  # région du compte d'équipe du datathon


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
    # Certains modèles renvoient d'abord un bloc de raisonnement : on concatène tous les blocs texte.
    return "".join(b["text"] for b in reponse["output"]["message"]["content"] if "text" in b)


def appeler_json(systeme: str, message: str, modele: str | None = None) -> dict:
    texte = appeler(systeme + "\nRéponds uniquement avec un objet JSON valide.", message, modele)
    debut, fin = texte.find("{"), texte.rfind("}")
    return json.loads(texte[debut:fin + 1])
