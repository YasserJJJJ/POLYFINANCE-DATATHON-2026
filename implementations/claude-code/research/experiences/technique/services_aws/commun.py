"""Outils communs aux essais « services AWS ». Lecture seule : aucun appel de création.

- session() : profil « alphaforge », région us-east-1.
- sonde() : lance un appel de lecture et classe le résultat (autorisé, refusé, erreur).
- appel_modele() : compte et journalise chaque inférence Bedrock ; plafond dur à vingt.
- ecrire() : conserve une sortie en JSON sous sorties/.

boto3 n'envoie aucune télémétrie à un tiers : il ne parle qu'aux points d'accès AWS appelés.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import time
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

ICI = Path(__file__).parent
SORTIES = ICI / "sorties"
SORTIES.mkdir(exist_ok=True)
JOURNAL_MODELE = SORTIES / "appels_bedrock.jsonl"
PLAFOND_APPELS = 20
PROFIL, REGION = "alphaforge", "us-east-1"
HAIKU = "global.anthropic.claude-haiku-5-5"
REFUS = ("AccessDenied", "AccessDeniedException", "UnauthorizedOperation", "UnauthorizedException", "NotAuthorized")


def session() -> boto3.Session:
    return boto3.Session(profile_name=PROFIL, region_name=REGION)


def client(service: str):
    return session().client(service, config=Config(retries={"max_attempts": 2}, connect_timeout=8, read_timeout=30))


def masquer(texte: str) -> str:
    """Ne garde que les quatre derniers chiffres d'un numéro de compte AWS."""
    return re.sub(r"(?<!\d)\d{12}(?!\d)", lambda m: "…" + m.group()[-4:], texte)


def maintenant() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def sonde(nom: str, appel, resume=lambda r: None) -> dict:
    """Appelle une opération de lecture et dit si elle est autorisée. Ne lève jamais."""
    debut = time.time()
    try:
        rep = appel()
        return {"sonde": nom, "etat": "autorise", "resume": resume(rep), "ms": round(1000 * (time.time() - debut)),
                "requestId": rep.get("ResponseMetadata", {}).get("RequestId")}
    except ClientError as e:
        code = e.response["Error"]["Code"]
        etat = "refuse" if any(code.startswith(r) for r in REFUS) else "erreur"
        return {"sonde": nom, "etat": etat, "code": code, "message": masquer(e.response["Error"].get("Message", ""))[:300],
                "ms": round(1000 * (time.time() - debut))}
    except (BotoCoreError, Exception) as e:  # noqa: BLE001 - une sonde ne doit pas arrêter l'inventaire
        return {"sonde": nom, "etat": "erreur", "code": type(e).__name__, "message": masquer(str(e))[:300],
                "ms": round(1000 * (time.time() - debut))}


def appels_faits() -> int:
    return sum(1 for _ in JOURNAL_MODELE.open(encoding="utf-8")) if JOURNAL_MODELE.exists() else 0


def appel_modele(essai: str, modele: str, nature: str, appel) -> dict:
    """Fait une inférence Bedrock (conversation, plongement, reclassement), plafonnée et journalisée."""
    if appels_faits() >= PLAFOND_APPELS:
        raise RuntimeError(f"Plafond de {PLAFOND_APPELS} appels de modèle atteint : voir {JOURNAL_MODELE}")
    debut = time.time()
    ligne = {"quand": maintenant(), "essai": essai, "modele": modele, "nature": nature}
    try:
        rep = appel()
        ligne |= {"requestId": rep["ResponseMetadata"]["RequestId"], "ms": round(1000 * (time.time() - debut)),
                  "jetons": rep.get("usage"), "arret": rep.get("stopReason")}
        return rep
    except Exception as e:  # noqa: BLE001
        ligne |= {"erreur": f"{type(e).__name__}: {e}"[:300]}
        raise
    finally:
        with JOURNAL_MODELE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ligne, ensure_ascii=False, default=str) + "\n")


def ecrire(nom: str, contenu) -> Path:
    chemin = SORTIES / nom
    chemin.write_text(masquer(json.dumps(contenu, ensure_ascii=False, indent=2, default=str)) + "\n", encoding="utf-8")
    return chemin
