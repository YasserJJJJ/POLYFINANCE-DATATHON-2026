"""Essai 6 — Comment nos contrats de dossier s'écriraient sur S3 et DynamoDB. ÉMULATEUR LOCAL, PAS AWS.

La bibliothèque « moto » intercepte les appels boto3 dans le processus : rien ne part vers AWS, aucune
ressource réelle n'est créée, et des identifiants factices sont posés avant tout import de boto3.
Cet essai prouve que le code s'écrit ainsi et que l'émulateur se conduit ainsi ; il ne prouve pas
la conduite du vrai service (à vérifier sur AWS si l'option est retenue).

Ce qu'il éprouve :
  1. pièce immuable identifiée par son empreinte (clé S3 = empreinte ; écriture refusée si la clé existe) ;
  2. journal en ajout seul, une seule écriture à la fois par branche (écriture conditionnelle DynamoDB) ;
  3. tête déduite du journal ; variante = branche qui partage les pièces ; invalidation sélective.

    uv run --with "moto[s3,dynamodb]" python research/experiences/technique/services_aws/essai6_emulation_locale.py
"""

from __future__ import annotations

import hashlib
import json
import os

os.environ.update({"AWS_ACCESS_KEY_ID": "factice", "AWS_SECRET_ACCESS_KEY": "factice", "AWS_DEFAULT_REGION": "us-east-1"})
os.environ.pop("AWS_PROFILE", None)

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402
from moto import mock_aws  # noqa: E402

from commun import ecrire, maintenant  # noqa: E402

SEAU, TABLE = "alphaforge-dossier-essai", "alphaforge-journal-essai"


def empreinte(contenu: dict) -> str:
    return "sha256-" + hashlib.sha256(json.dumps(contenu, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]


def deposer(s3, contenu: dict) -> tuple[str, str]:
    """Dépose une pièce sous son empreinte. Rend (empreinte, 'creee' | 'deja_la' | 'ecrasee_sans_controle')."""
    e = empreinte(contenu)
    try:
        s3.put_object(Bucket=SEAU, Key=f"pieces/{e}", Body=json.dumps(contenu, ensure_ascii=False).encode(), IfNoneMatch="*")
        return e, "creee"
    except ClientError as err:
        if err.response["Error"]["Code"] in ("PreconditionFailed", "412"):
            return e, "deja_la"
        raise


def tete(ddb, branche: str) -> dict | None:
    r = ddb.query(TableName=TABLE, KeyConditionExpression="branche = :b", ExpressionAttributeValues={":b": {"S": branche}},
                  ScanIndexForward=False, Limit=1, ConsistentRead=True)["Items"]
    return {"rang": int(r[0]["rang"]["N"]), "evenement": json.loads(r[0]["evenement"]["S"])} if r else None


def ajouter(ddb, branche: str, tete_vue: int, evenement: dict) -> str:
    """Ajoute un événement qui prolonge la tête vue. Refusé si quelqu'un a écrit entre-temps."""
    try:
        ddb.put_item(TableName=TABLE, Item={"branche": {"S": branche}, "rang": {"N": str(tete_vue + 1)},
                                            "evenement": {"S": json.dumps(evenement, ensure_ascii=False)}},
                     ConditionExpression="attribute_not_exists(rang)")
        return "accepte"
    except ClientError as err:
        if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return "refuse_tete_deplacee"
        raise


def en_vigueur(ddb, branche: str) -> dict[str, str]:
    """Rejoue le journal de la branche (et de sa branche mère jusqu'au point de bifurcation) : rôle -> empreinte."""
    items = ddb.query(TableName=TABLE, KeyConditionExpression="branche = :b", ExpressionAttributeValues={":b": {"S": branche}},
                      ConsistentRead=True)["Items"]
    evenements = [json.loads(i["evenement"]["S"]) for i in items]
    etat: dict[str, str] = {}
    if evenements and evenements[0]["type"] == "bifurcation":
        mere = ddb.query(TableName=TABLE, KeyConditionExpression="branche = :b AND rang <= :r", ConsistentRead=True,
                         ExpressionAttributeValues={":b": {"S": evenements[0]["mere"]}, ":r": {"N": str(evenements[0]["rang_mere"])}})["Items"]
        evenements = [json.loads(i["evenement"]["S"]) for i in mere] + evenements[1:]
    for ev in evenements:
        if ev["type"] == "piece":
            etat[ev["role"]] = ev["empreinte"]
            for dependant in ev.get("invalide", []):   # invalidation sélective, décidée par le greffier
                etat.pop(dependant, None)
    return etat


@mock_aws
def main() -> None:
    s3, ddb = boto3.client("s3"), boto3.client("dynamodb")
    s3.create_bucket(Bucket=SEAU)
    s3.put_bucket_versioning(Bucket=SEAU, VersioningConfiguration={"Status": "Enabled"})
    ddb.create_table(TableName=TABLE, BillingMode="PAY_PER_REQUEST",
                     KeySchema=[{"AttributeName": "branche", "KeyType": "HASH"}, {"AttributeName": "rang", "KeyType": "RANGE"}],
                     AttributeDefinitions=[{"AttributeName": "branche", "AttributeType": "S"}, {"AttributeName": "rang", "AttributeType": "N"}])
    constats: dict = {"quand": maintenant(), "avertissement": "émulateur moto : conduite locale, pas celle d'AWS"}

    # 1. Pièces immuables.
    demande = {"type": "demande", "texte": "Ajouter 10 % de Tesla ?", "horizon_ans": 3}
    e1, s1 = deposer(s3, demande)
    _, s2 = deposer(s3, demande)
    constats["1_piece_deposee_deux_fois"] = [s1, s2]
    constats["1_versions_de_la_cle"] = len(s3.list_object_versions(Bucket=SEAU, Prefix=f"pieces/{e1}").get("Versions", []))

    # 2. Journal en ajout seul, une écriture à la fois.
    constats["2_premier_evenement"] = ajouter(ddb, "principale", 0, {"type": "piece", "role": "demande", "empreinte": e1})
    vue = tete(ddb, "principale")["rang"]
    e_calc, _ = deposer(s3, {"type": "calcul", "entrees": [e1], "resultat": "fictif"})
    constats["2_ecrivain_A"] = ajouter(ddb, "principale", vue, {"type": "piece", "role": "calcul", "empreinte": e_calc, "entrees": [e1]})
    constats["2_ecrivain_B_meme_tete"] = ajouter(ddb, "principale", vue, {"type": "piece", "role": "restitution", "empreinte": "x"})

    # 3. Correction sur la ligne principale : la demande change, le calcul qui en dépendait cesse d'être en vigueur.
    avant = en_vigueur(ddb, "principale")
    e2, _ = deposer(s3, demande | {"horizon_ans": 2})
    rang_avant_correction = tete(ddb, "principale")["rang"]
    ajouter(ddb, "principale", rang_avant_correction, {"type": "piece", "role": "demande", "empreinte": e2, "remplace": e1, "invalide": ["calcul"]})
    constats["3_en_vigueur_avant_correction"] = avant
    constats["3_en_vigueur_apres_correction"] = en_vigueur(ddb, "principale")
    # Variante : une branche qui part d'avant la correction, partage les pièces, et laisse la ligne principale intacte.
    ajouter(ddb, "variante-qqq", 0, {"type": "bifurcation", "mere": "principale", "rang_mere": rang_avant_correction})
    e3, _ = deposer(s3, {"type": "option", "titre": "QQQ"})
    ajouter(ddb, "variante-qqq", 1, {"type": "piece", "role": "option", "empreinte": e3})
    constats["3_en_vigueur_variante"] = en_vigueur(ddb, "variante-qqq")
    constats["3_principale_inchangee_par_la_variante"] = en_vigueur(ddb, "principale") == constats["3_en_vigueur_apres_correction"]
    constats["3_objets_dans_le_seau"] = s3.list_objects_v2(Bucket=SEAU)["KeyCount"]

    ecrire("essai6_emulation_locale.json", constats)
    for k, v in constats.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
