"""Crée (ou retrouve) le Guardrail Bedrock d'AlphaForge et en publie une version.

    python infra/creer_guardrail.py              # crée ou retrouve le guardrail, publie une version
    python infra/creer_guardrail.py --verifier   # n'écrit rien : affiche ce qui serait créé

À lancer après autorisation du porteur et affichage du plan (voir docs/deploiement.md).
Il retrouve un guardrail existant par son nom. AWS_PROFILE est respecté ; défaut : alphaforge.

Ce que le guardrail ajoute au contrôle en code du Rédacteur (il ne le remplace jamais) :
  - un sujet refusé « conseil d'achat ou de vente » ;
  - une liste de formules interdites, en plus de garde_fous.py ;
  - l'ancrage contextuel : la réponse doit rester fidèle au dossier envoyé comme source (grounding_source).
Si le guardrail bloque une réponse (stopReason = guardrail_intervened), llm.py lève LLMIndisponible et le
Rédacteur retombe sur ses phrases modèles, exactement comme après un refus du contrôle d'ancrage.

Après création, activer avec les variables d'environnement affichées (ALPHAFORGE_GUARDRAIL_ID et _VERSION).
Le journal conserve l'identité de la ressource ; un échec de publication supprime uniquement le guardrail
créé par cette tentative. Un guardrail préexistant n'est jamais supprimé.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

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
    p.add_argument("--journal", type=Path, help="nouveau journal JSON de création")
    a = p.parse_args()
    if a.verifier:
        print(json.dumps(CONFIG, ensure_ascii=False, indent=2))
        print("\nRien n'a été créé (--verifier).")
        return

    import boto3

    profil = os.environ.get("AWS_PROFILE") or (None if os.environ.get("AWS_ACCESS_KEY_ID") else "alphaforge")
    session = boto3.Session(profile_name=profil, region_name=REGION)
    if session.client("sts").get_caller_identity()["Account"] != "471112821226" or REGION != "us-east-1":
        raise ValueError("Le mandat autorise uniquement le compte 471112821226 en us-east-1.")
    bedrock = session.client("bedrock")
    chemin = a.journal or Path(__file__).parent / "build" / f"guardrail-{time.time_ns()}.json"
    if chemin.exists():
        raise ValueError(f"Journal déjà présent : {chemin}. Choisir un nouveau --journal.")
    journal = {"nom": NOM, "region": REGION, "cree_par_tentative": False, "statut": "en_cours"}

    def enregistrer():
        chemin.parent.mkdir(parents=True, exist_ok=True)
        temporaire = chemin.with_suffix(".tmp")
        temporaire.write_text(json.dumps(journal, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
        temporaire.replace(chemin)

    enregistrer()
    try:
        existant = next((g for g in bedrock.list_guardrails().get("guardrails", []) if g["name"] == NOM), None)
        if existant:
            identifiant = existant["id"]
            journal.update(id=identifiant, arn=existant["arn"])
            print(f"Guardrail déjà là : {identifiant}")
        else:
            cree = bedrock.create_guardrail(**CONFIG)
            identifiant = cree["guardrailId"]
            journal.update(id=identifiant, arn=cree["guardrailArn"], cree_par_tentative=True)
            enregistrer()
            print(f"Guardrail créé : {identifiant}", flush=True)
        for _ in range(30):
            statut = bedrock.get_guardrail(guardrailIdentifier=identifiant)["status"]
            if statut == "READY":
                break
            if statut == "FAILED":
                raise RuntimeError("La création du Guardrail a échoué.")
            time.sleep(2)
        else:
            raise TimeoutError("Le Guardrail n'est pas prêt après 60 secondes.")
        version = bedrock.create_guardrail_version(guardrailIdentifier=identifiant,
                                                   description="Version publiée pour l'API AlphaForge")["version"]
        journal.update(version=version, statut="publie")
        enregistrer()
    except Exception as e:
        journal.update(statut="echec", erreur=str(e))
        if journal["cree_par_tentative"]:
            try:
                bedrock.delete_guardrail(guardrailIdentifier=journal["id"])
                journal["statut"] = "supprime_apres_echec"
            except Exception as nettoyage:
                journal["erreur_nettoyage"] = str(nettoyage)
        enregistrer()
        raise
    print(f"Version publiée : {version}\n")
    print("À ajouter à l'environnement de l'API (Lambda ou local) :")
    print(f"  ALPHAFORGE_GUARDRAIL_ID={identifiant}")
    print(f"  ALPHAFORGE_GUARDRAIL_VERSION={version}")


if __name__ == "__main__":
    main()
