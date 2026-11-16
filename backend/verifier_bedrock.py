"""Vérifie l'accès aux modèles Bedrock avec AWS_PROFILE (défaut : alphaforge).

Lancer depuis backend/ :  python verifier_bedrock.py
Code de sortie : 0 si les deux modèles répondent, 1 sinon (identifiants absents ou expirés, modèle refusé…).
"""
import os
import sys

# Sous Windows, une sortie redirigée est en cp1252 : « → » ou « É » faisaient planter le script.
for flux in (sys.stdout, sys.stderr):
    if hasattr(flux, "reconfigure"):
        flux.reconfigure(encoding="utf-8", errors="replace")

os.environ.setdefault("AWS_PROFILE", "alphaforge")
os.environ.setdefault("AWS_REGION", "us-east-1")

import boto3  # noqa: E402

from alphaforge import llm  # noqa: E402

try:
    identite = boto3.client("sts", region_name=llm.REGION).get_caller_identity()
except Exception as e:  # profil absent, clés expirées, pas de réseau
    print(f"ÉCHEC identifiants AWS → {type(e).__name__}: {e}")
    print("Renouvelle les identifiants (bloc « Windows (PowerShell) » de Workshop Studio, puis "
          ".\\infra\\enregistrer_identifiants.ps1). L'application reste utilisable en mode hors ligne.")
    sys.exit(1)

print("Compte AWS :", identite["Account"][:4] + "…" + identite["Account"][-2:])
echecs = 0
for modele in (llm.MODELE_PRINCIPAL, llm.MODELE_LEGER):
    try:
        reponse = llm.appeler("Réponds en une phrase courte, en français.", "Dis bonjour à l'équipe AlphaForge.",
                             modele, 60, agent="Vérification")
        print(f"OK  {modele} → {reponse.strip()}")
    except Exception as e:  # on affiche l'erreur telle quelle pour la diagnostiquer
        echecs += 1
        print(f"ÉCHEC {modele} → {type(e).__name__}: {e}")
sys.exit(1 if echecs else 0)
