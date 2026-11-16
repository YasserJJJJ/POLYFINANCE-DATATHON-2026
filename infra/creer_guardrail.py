"""Crée (ou retrouve) le Guardrail Bedrock d'AlphaForge et en publie une version.

    python infra/creer_guardrail.py              # crée ou retrouve le guardrail, publie une version
    python infra/creer_guardrail.py --verifier   # n'écrit rien : affiche ce qui serait créé

À LANCER EN ÉQUIPE, au moment du déploiement (voir docs/deploiement.md) : ce script crée une ressource dans le
compte AWS partagé. Il est idempotent : relancé, il retrouve le guardrail existant par son nom.

Ce que le guardrail ajoute au contrôle en code du Rédacteur (il ne le remplace jamais) :
  - un sujet refusé « conseil d'achat ou de vente » ;
  - une liste de formules interdites, en plus de garde_fous.py ;
  - l'ancrage contextuel : la réponse doit rester fidèle au dossier envoyé comme source (grounding_source).
Si le guardrail bloque une réponse (stopReason = guardrail_intervened), llm.py lève LLMIndisponible et le
Rédacteur retombe sur ses phrases modèles, exactement comme après un refus du contrôle d'ancrage.

Après création, activer avec les variables d'environnement affichées (ALPHAFORGE_GUARDRAIL_ID et _VERSION).
Non testé sur le vrai compte au moment de l'écriture : les tests (backend/tests/test_llm.py) utilisent un faux client.
"""
from __future__ import annotations

import argparse
import os
import sys

for _flux in (sys.stdout, sys.stderr):
    if hasattr(_flux, "reconfigure"):
        _flux.reconfigure(encoding="utf-8", errors="replace")

NOM = "alphaforge-garde-fou"
REGION = os.environ.get("AWS_REGION", "us-east-1")

CONFIG = dict(
    name=NOM,
    description="AlphaForge : refuse le conseil d'achat ou de vente et vérifie l'ancrage du texte sur le dossier.",
    topicPolicyConfig={"topicsConfig": [{
        "name": "conseil-achat-vente",
        # 200 caractères au plus (limite de l'API).
        "definition": "Recommander d'acheter, de vendre ou de conserver un placement précis, ou promettre un "
                      "rendement, à une personne donnée.",
        "examples": ["Je te recommande d'acheter Tesla.", "Achète du bitcoin maintenant.",
                     "Vends ce titre avant qu'il baisse.", "Ce placement est sans risque, fonce."],
        "type": "DENY",
    }]},
    wordPolicyConfig={"wordsConfig": [{"text": t} for t in
                                      ("achète maintenant", "je te recommande", "je recommande", "garanti",
                                       "sans risque", "fonce")]},
    contextualGroundingPolicyConfig={"filtersConfig": [{"type": "GROUNDING", "threshold": 0.7},
                                                       {"type": "RELEVANCE", "threshold": 0.5}]},
    blockedInputMessaging="Cette demande ne peut pas être traitée par le second avis.",
    blockedOutputsMessaging="Réponse bloquée par le garde-fou : le texte du second avis est rédigé par le code.",
)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true", help="affiche la configuration sans rien créer")
    a = p.parse_args()
    if a.verifier:
        import json
        print(json.dumps(CONFIG, ensure_ascii=False, indent=2))
        print("\nRien n'a été créé (--verifier).")
        return

    import boto3

    profil = os.environ.get("AWS_PROFILE") or (None if os.environ.get("AWS_ACCESS_KEY_ID") else "datathon")
    bedrock = boto3.Session(profile_name=profil, region_name=REGION).client("bedrock")
    existant = next((g for g in bedrock.list_guardrails().get("guardrails", []) if g["name"] == NOM), None)
    if existant:
        identifiant = existant["id"]
        print(f"Guardrail déjà là : {identifiant}")
    else:
        identifiant = bedrock.create_guardrail(**CONFIG)["guardrailId"]
        print(f"Guardrail créé : {identifiant}")
    version = bedrock.create_guardrail_version(guardrailIdentifier=identifiant,
                                               description="Version publiée pour l'API AlphaForge")["version"]
    print(f"Version publiée : {version}\n")
    print("À ajouter à l'environnement de l'API (Lambda ou local) :")
    print(f"  ALPHAFORGE_GUARDRAIL_ID={identifiant}")
    print(f"  ALPHAFORGE_GUARDRAIL_VERSION={version}")


if __name__ == "__main__":
    main()
