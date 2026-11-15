"""Vérifie l'accès à Claude sur Bedrock avec le profil AWS « datathon ».

Lancer depuis backend/ :  python verifier_bedrock.py
"""
import os

os.environ.setdefault("AWS_PROFILE", "datathon")
os.environ.setdefault("AWS_REGION", "us-east-1")

import boto3  # noqa: E402

from alphaforge import llm  # noqa: E402

identite = boto3.client("sts", region_name=llm.REGION).get_caller_identity()
print("Compte AWS :", identite["Account"])
for modele in (llm.MODELE_PRINCIPAL, llm.MODELE_LEGER):
    try:
        reponse = llm.appeler("Réponds en une phrase courte, en français.", "Dis bonjour à l'équipe AlphaForge.", modele, 60)
        print(f"OK  {modele} → {reponse.strip()}")
    except Exception as e:  # on affiche l'erreur telle quelle pour la diagnostiquer
        print(f"ÉCHEC {modele} → {type(e).__name__}: {e}")
