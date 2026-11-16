"""Réglages communs aux essais Strands (expérience technique, pas le produit).

- Toute inférence passe par Amazon Bedrock : profil « alphaforge », région us-east-1.
- Chaque appel Bedrock est journalisé dans sorties/appels_bedrock.jsonl (identifiant de
  requête AWS, jetons, durée) par un crochet posé sur le client boto3, pas par Strands.
- Un plafond dur de vingt appels est tenu par ce journal, tous essais confondus.
- Aucune exportation OpenTelemetry : OTEL_SDK_DISABLED=true (sauf si l'essai 9 dit autre chose).
- Les noms d'hôtes résolus par le processus sont relevés, pour voir vers où il parle.
"""
import json
import os
import pathlib
import socket
import time

os.environ.setdefault("OTEL_SDK_DISABLED", "true")
for _v in ("OTEL_EXPORTER_OTLP_ENDPOINT", "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "LANGFUSE_BASE_URL"):
    os.environ.pop(_v, None)

import boto3  # noqa: E402
from botocore.config import Config  # noqa: E402
from strands.models import BedrockModel  # noqa: E402

DOSSIER = pathlib.Path(__file__).parent
SORTIES = DOSSIER / "sorties"
SORTIES.mkdir(exist_ok=True)
JOURNAL = SORTIES / "appels_bedrock.jsonl"
PLAFOND = 20
MODELE = "global.anthropic.claude-haiku-5-5"

HOTES: set[str] = set()
_getaddrinfo = socket.getaddrinfo


def _getaddrinfo_note(host, *a, **k):
    HOTES.add(str(host))
    return _getaddrinfo(host, *a, **k)


socket.getaddrinfo = _getaddrinfo_note


def ecrire(chemin: pathlib.Path, ligne: dict) -> None:
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False, default=str) + "\n")


def nb_appels() -> int:
    if not JOURNAL.exists():
        return 0
    return sum(1 for ligne in open(JOURNAL, encoding="utf-8") if '"evenement": "debut"' in ligne)


def modele(essai: str, max_tokens: int = 300, streaming: bool = False) -> BedrockModel:
    """Modèle Bedrock de Strands, avec journal des appels posé sur le client boto3."""
    session = boto3.Session(profile_name="alphaforge", region_name="us-east-1")
    m = BedrockModel(
        model_id=MODELE,
        boto_session=session,
        boto_client_config=Config(retries={"max_attempts": 1, "mode": "standard"}, read_timeout=60),
        max_tokens=max_tokens,
        streaming=streaming,
    )
    debuts: list[float] = []

    def avant(**kwargs):
        if nb_appels() >= PLAFOND:
            raise RuntimeError(f"Plafond de {PLAFOND} appels Bedrock atteint : essai arrêté.")
        debuts.append(time.time())
        ecrire(JOURNAL, {"evenement": "debut", "essai": essai, "pid": os.getpid(), "t": time.time()})

    def apres(http_response=None, parsed=None, model=None, **kwargs):
        meta = (parsed or {}).get("ResponseMetadata", {})
        ecrire(
            JOURNAL,
            {
                "evenement": "fin",
                "essai": essai,
                "operation": getattr(model, "name", None),
                "statut_http": meta.get("HTTPStatusCode"),
                "id_requete_aws": meta.get("RequestId"),
                "jetons": (parsed or {}).get("usage"),  # présent seulement hors flux (Converse)
                "raison_arret": (parsed or {}).get("stopReason"),
                "duree_s": round(time.time() - debuts[-1], 2) if debuts else None,
            },
        )

    m.client.meta.events.register("before-call.bedrock-runtime.*", avant)
    m.client.meta.events.register("after-call.bedrock-runtime.*", apres)
    return m


def bilan(essai: str) -> None:
    lignes = [json.loads(x) for x in open(JOURNAL, encoding="utf-8")] if JOURNAL.exists() else []
    fins = [x for x in lignes if x["evenement"] == "fin" and x["essai"].startswith(essai)]
    print(f"\n[{essai}] appels Bedrock de cet essai (toutes relances) : {len(fins)} ; total tous essais : {nb_appels()}/{PLAFOND}")
    for x in fins[-6:]:
        print("   ", x["operation"], x["statut_http"], x["id_requete_aws"], x["jetons"], x["raison_arret"], x["duree_s"], "s")
    print(f"[{essai}] hôtes résolus par ce processus : {sorted(HOTES)}")
