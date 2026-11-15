"""Archive chaque dossier de décision dans Amazon S3 (JSON), pour pouvoir le rejouer et le montrer.

Actif seulement si `ALPHAFORGE_DATA_BUCKET` est défini (sur AWS). Une erreur de stockage ne doit jamais
casser l'analyse : on l'ignore et on continue.
"""
from __future__ import annotations

import json
import os
import time
import uuid


def sauvegarder_dossier(dossier: dict) -> str | None:
    """Écrit le dossier dans s3://<bucket>/dossiers/. Renvoie la clé S3, ou None si rien n'a été écrit."""
    bucket = os.environ.get("ALPHAFORGE_DATA_BUCKET")
    if not bucket:
        return None
    try:
        import boto3

        cle = f"dossiers/{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}.json"
        boto3.client("s3").put_object(
            Bucket=bucket, Key=cle, ContentType="application/json",
            Body=json.dumps(dossier, ensure_ascii=False, default=str).encode("utf-8"))
        return cle
    except Exception:  # noqa: BLE001 - jamais bloquant pour l'utilisateur
        return None
