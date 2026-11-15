"""Point d'entrée AWS Lambda (Function URL) : la même API FastAPI qu'en local, servie par Mangum.

Au démarrage à froid, les données du jeu de départ sont copiées depuis Amazon S3 (la source de vérité)
vers /tmp, puis `ALPHAFORGE_DATA` pointe dessus. Sans `ALPHAFORGE_DATA_BUCKET`, on utilise les fichiers
du dépôt, comme en local.
"""
import os
from pathlib import Path


def _preparer_donnees() -> None:
    bucket = os.environ.get("ALPHAFORGE_DATA_BUCKET")
    if not bucket:
        return
    import boto3

    prefixe = os.environ.get("ALPHAFORGE_DATA_PREFIX", "data/")
    dossier = Path("/tmp/alphaforge_data")
    dossier.mkdir(parents=True, exist_ok=True)
    s3 = boto3.client("s3")
    for objet in s3.list_objects_v2(Bucket=bucket, Prefix=prefixe).get("Contents", []):
        nom = objet["Key"][len(prefixe):]
        cible = dossier / nom
        if nom and not nom.endswith("/") and not cible.exists():
            s3.download_file(bucket, objet["Key"], str(cible))
    os.environ["ALPHAFORGE_DATA"] = str(dossier)


_preparer_donnees()

from mangum import Mangum  # noqa: E402

from api import app  # noqa: E402

handler = Mangum(app, lifespan="off")
