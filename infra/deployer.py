"""Déploie AlphaForge sur AWS en une commande (compte d'équipe du datathon, région us-east-1).

    python infra/deployer.py                      # tout : S3, Lambda + Function URL, interface sur Amplify
    python infra/deployer.py --frontend s3        # interface sur un site statique S3 si Amplify est refusé
    python infra/deployer.py --seulement-construire   # fabrique le zip et l'interface, sans toucher à AWS

Ce que ça crée (idempotent : on peut le relancer pour mettre à jour) :
  - un bucket S3 `alphaforge-<compte>-<région>` : données du jeu de départ (data/), code (code/), dossiers de
    décision archivés par l'API (dossiers/) ;
  - un rôle IAM `alphaforge-lambda` : journaux, lecture/écriture du bucket, appel des modèles Bedrock ;
  - une fonction Lambda `alphaforge-api` (Python 3.12) avec une Function URL publique ;
  - l'interface React, hébergée sur AWS Amplify (déploiement manuel, sans Git).

Identifiants : profil AWS « datathon » (voir infra/enregistrer_identifiants.ps1) ou variables AWS_* du terminal.
Aucune clé n'est écrite dans le dépôt.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

# Sous Windows, une sortie non redirigée vers un terminal UTF-8 (ou redirigée dans un fichier) est en
# cp1252 par défaut : « ▶ » fait planter le script avant même le premier appel AWS.
for _flux in (sys.stdout, sys.stderr):
    if hasattr(_flux, "reconfigure"):
        _flux.reconfigure(encoding="utf-8", errors="replace")

RACINE = Path(__file__).resolve().parents[1]
BUILD = RACINE / "infra" / "build"
NOM_FONCTION = "alphaforge-api"
NOM_ROLE = "alphaforge-lambda"
NOM_APP_AMPLIFY = "alphaforge"
REGION = os.environ.get("AWS_REGION", "us-east-1")


def etape(texte: str) -> None:
    print(f"\n▶ {texte}", flush=True)


def session():
    import boto3
    from botocore.exceptions import ProfileNotFound

    profil = os.environ.get("AWS_PROFILE")
    if not profil and not os.environ.get("AWS_ACCESS_KEY_ID"):
        profil = "datathon"
    try:
        return boto3.Session(profile_name=profil, region_name=REGION) if profil else boto3.Session(region_name=REGION)
    except ProfileNotFound:
        sys.exit("Profil AWS introuvable. Lance d'abord infra\\enregistrer_identifiants.ps1 (voir infra/README.md).")


# ----------------------------------------------------------------------------- construction (sans AWS)

def construire_zip_lambda() -> Path:
    etape("Construction du paquet Lambda (dépendances Linux, Python 3.12)")
    pkg = BUILD / "lambda"
    shutil.rmtree(pkg, ignore_errors=True)
    pkg.mkdir(parents=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--target", str(pkg),
                    "--platform", "manylinux2014_x86_64", "--python-version", "3.12", "--implementation", "cp",
                    "--only-binary=:all:", "-r", str(RACINE / "backend" / "requirements-lambda.txt")], check=True)
    shutil.copytree(RACINE / "backend" / "alphaforge", pkg / "alphaforge",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy(RACINE / "backend" / "api.py", pkg / "api.py")
    shutil.copy(RACINE / "backend" / "lambda_handler.py", pkg / "lambda_handler.py")
    archive = BUILD / "alphaforge-lambda.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(pkg.rglob("*")):
            # On écarte les caches et les tests des bibliothèques (pandas/tests pèse plusieurs dizaines de Mo).
            if f.is_file() and "__pycache__" not in f.parts and "tests" not in f.relative_to(pkg).parts:
                z.write(f, f.relative_to(pkg).as_posix())
    print(f"  {archive.name} : {archive.stat().st_size / 1e6:.1f} Mo")
    return archive


def construire_interface(url_api: str | None) -> Path:
    etape("Construction de l'interface React")
    front = RACINE / "frontend"
    windows = os.name == "nt"
    if not (front / "node_modules").exists():
        subprocess.run(["npm", "ci"], cwd=front, check=True, shell=windows)
    env = {**os.environ, "VITE_API_URL": (url_api or "").rstrip("/")}
    subprocess.run(["npm", "run", "build"], cwd=front, check=True, shell=windows, env=env)
    archive = BUILD / "alphaforge-interface.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted((front / "dist").rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(front / "dist").as_posix())
    print(f"  {archive.name} : {archive.stat().st_size / 1e6:.1f} Mo (API : {url_api or 'même origine'})")
    return archive


# ----------------------------------------------------------------------------- AWS

def bucket_s3(s3, compte: str) -> str:
    nom = f"alphaforge-{compte}-{REGION}"
    etape(f"Amazon S3 : bucket {nom}")
    try:
        s3.head_bucket(Bucket=nom)
        print("  déjà là")
    except Exception:  # noqa: BLE001
        args = {"Bucket": nom}
        if REGION != "us-east-1":
            args["CreateBucketConfiguration"] = {"LocationConstraint": REGION}
        s3.create_bucket(**args)
        print("  créé")
    data = RACINE / "data" / "raw" / "alphaforge_starter"
    for f in sorted(data.iterdir()):
        if f.is_file() and f.suffix in (".csv", ".md", ".txt"):
            s3.upload_file(str(f), nom, f"data/{f.name}")
    print(f"  données du jeu de départ envoyées dans s3://{nom}/data/")
    return nom


def role_iam(iam, bucket: str) -> str:
    etape(f"IAM : rôle {NOM_ROLE}")
    confiance = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "sts:AssumeRole",
                                                        "Principal": {"Service": "lambda.amazonaws.com"}}]}
    try:
        arn = iam.create_role(RoleName=NOM_ROLE, AssumeRolePolicyDocument=json.dumps(confiance),
                              Description="AlphaForge : API Lambda, S3 et Bedrock")["Role"]["Arn"]
        print("  créé")
    except iam.exceptions.EntityAlreadyExistsException:
        arn = iam.get_role(RoleName=NOM_ROLE)["Role"]["Arn"]
        print("  déjà là")
    iam.attach_role_policy(RoleName=NOM_ROLE,
                           PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole")
    politique = {"Version": "2012-10-17", "Statement": [
        {"Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
         "Resource": [f"arn:aws:s3:::{bucket}", f"arn:aws:s3:::{bucket}/*"]},
        {"Effect": "Allow", "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
         "Resource": "*"}]}
    iam.put_role_policy(RoleName=NOM_ROLE, PolicyName="alphaforge-acces", PolicyDocument=json.dumps(politique))
    return arn


def fonction_lambda(lam, s3, bucket: str, archive: Path, role_arn: str) -> str:
    etape(f"AWS Lambda : fonction {NOM_FONCTION}")
    cle = "code/alphaforge-lambda.zip"
    s3.upload_file(str(archive), bucket, cle)
    env = {"Variables": {"ALPHAFORGE_DATA_BUCKET": bucket, "ALPHAFORGE_LLM": "auto"}}
    existe = True
    try:
        lam.get_function(FunctionName=NOM_FONCTION)
    except lam.exceptions.ResourceNotFoundException:
        existe = False
    if not existe:
        for essai in range(12):  # le rôle IAM met quelques secondes à être utilisable
            try:
                lam.create_function(FunctionName=NOM_FONCTION, Runtime="python3.12", Role=role_arn,
                                    Handler="lambda_handler.handler", Code={"S3Bucket": bucket, "S3Key": cle},
                                    Timeout=90, MemorySize=1536, Environment=env,
                                    Description="AlphaForge : API du second avis")
                break
            except lam.exceptions.InvalidParameterValueException as e:
                if "role" not in str(e).lower() or essai == 11:
                    raise
                time.sleep(5)
        print("  créée")
    else:
        lam.update_function_code(FunctionName=NOM_FONCTION, S3Bucket=bucket, S3Key=cle)
        lam.get_waiter("function_updated_v2").wait(FunctionName=NOM_FONCTION)
        lam.update_function_configuration(FunctionName=NOM_FONCTION, Timeout=90, MemorySize=1536, Environment=env,
                                          Role=role_arn)
        print("  mise à jour")
    lam.get_waiter("function_updated_v2").wait(FunctionName=NOM_FONCTION)
    return fonction_url(lam)


def fonction_url(lam) -> str:
    # Les en-têtes CORS sont déjà ajoutés par FastAPI : ne pas les configurer aussi ici (valeurs en double).
    try:
        url = lam.create_function_url_config(FunctionName=NOM_FONCTION, AuthType="NONE")["FunctionUrl"]
    except lam.exceptions.ResourceConflictException:
        url = lam.get_function_url_config(FunctionName=NOM_FONCTION)["FunctionUrl"]
    permissions = [
        dict(StatementId="url-public", Action="lambda:InvokeFunctionUrl", Principal="*", FunctionUrlAuthType="NONE"),
        dict(StatementId="invoke-public", Action="lambda:InvokeFunction", Principal="*", InvokedViaFunctionUrl=True),
    ]
    for p in permissions:
        try:
            lam.add_permission(FunctionName=NOM_FONCTION, **p)
        except lam.exceptions.ResourceConflictException:
            pass
        except Exception as e:  # noqa: BLE001 - ancien boto3 : paramètre inconnu
            print(f"  permission {p['StatementId']} non ajoutée ({type(e).__name__}) : mets boto3 à jour "
                  "(pip install -U boto3) puis relance")
    print(f"  URL de l'API : {url}")
    return url


def interface_amplify(session_aws, archive: Path) -> str:
    etape("AWS Amplify : hébergement de l'interface")
    amp = session_aws.client("amplify")
    app = next((a for a in amp.list_apps(maxResults=100)["apps"] if a["name"] == NOM_APP_AMPLIFY), None)
    if not app:
        app = amp.create_app(name=NOM_APP_AMPLIFY, description="AlphaForge AI : interface du second avis")["app"]
        print("  application créée")
    branche = "main"
    try:
        amp.create_branch(appId=app["appId"], branchName=branche, stage="PRODUCTION")
    except amp.exceptions.BadRequestException:
        pass  # la branche existe déjà
    depot = amp.create_deployment(appId=app["appId"], branchName=branche)
    requete = urllib.request.Request(depot["zipUploadUrl"], data=archive.read_bytes(), method="PUT",
                                     headers={"Content-Type": "application/zip"})
    urllib.request.urlopen(requete, timeout=120).read()
    amp.start_deployment(appId=app["appId"], branchName=branche, jobId=depot["jobId"])
    for _ in range(60):
        statut = amp.get_job(appId=app["appId"], branchName=branche, jobId=depot["jobId"])["job"]["summary"]["status"]
        if statut in ("SUCCEED", "FAILED", "CANCELLED"):
            break
        time.sleep(4)
    if statut != "SUCCEED":
        sys.exit(f"Le déploiement Amplify a fini avec le statut {statut}. Essaie : python infra/deployer.py --frontend s3")
    return f"https://{branche}.{app['defaultDomain']}"


def interface_s3(session_aws, compte: str, dossier_dist: Path) -> str:
    etape("Amazon S3 : site statique pour l'interface")
    import mimetypes

    s3 = session_aws.client("s3")
    nom = f"alphaforge-web-{compte}-{REGION}"
    try:
        s3.head_bucket(Bucket=nom)
    except Exception:  # noqa: BLE001
        args = {"Bucket": nom}
        if REGION != "us-east-1":
            args["CreateBucketConfiguration"] = {"LocationConstraint": REGION}
        s3.create_bucket(**args)
    s3.put_public_access_block(Bucket=nom, PublicAccessBlockConfiguration={
        "BlockPublicAcls": False, "IgnorePublicAcls": False, "BlockPublicPolicy": False, "RestrictPublicBuckets": False})
    s3.put_bucket_website(Bucket=nom, WebsiteConfiguration={"IndexDocument": {"Suffix": "index.html"}})
    s3.put_bucket_policy(Bucket=nom, Policy=json.dumps({"Version": "2012-10-17", "Statement": [
        {"Effect": "Allow", "Principal": "*", "Action": "s3:GetObject", "Resource": f"arn:aws:s3:::{nom}/*"}]}))
    for f in sorted(dossier_dist.rglob("*")):
        if f.is_file():
            type_mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            s3.upload_file(str(f), nom, f.relative_to(dossier_dist).as_posix(), ExtraArgs={"ContentType": type_mime})
    return f"http://{nom}.s3-website-{REGION}.amazonaws.com"


def verifier(url_api: str) -> None:
    etape("Vérification de l'API déployée")
    for tentative in range(6):
        try:
            with urllib.request.urlopen(url_api.rstrip("/") + "/api/sante", timeout=60) as r:
                sante = json.loads(r.read())
            print(f"  /api/sante : ok={sante['ok']} · agents IA (Bedrock) : {'oui' if sante['llm'] else 'non'}"
                  + ("" if sante["llm"] else f" ({sante.get('raison')})"))
            return
        except Exception as e:  # noqa: BLE001
            print(f"  essai {tentative + 1}/6 : {type(e).__name__}")
            time.sleep(6)
    print("  L'API ne répond pas encore : regarde les journaux CloudWatch de la fonction alphaforge-api.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--frontend", choices=["amplify", "s3"], default="amplify")
    p.add_argument("--seulement-construire", action="store_true", help="construit les zips sans appeler AWS")
    a = p.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)

    archive = construire_zip_lambda()
    if a.seulement_construire:
        construire_interface(None)
        print("\nConstruction terminée (rien n'a été envoyé sur AWS).")
        return

    s = session()
    compte = s.client("sts").get_caller_identity()["Account"]
    print(f"Compte AWS : {compte} · région {REGION}")
    s3, iam, lam = s.client("s3"), s.client("iam"), s.client("lambda")
    bucket = bucket_s3(s3, compte)
    role = role_iam(iam, bucket)
    url_api = fonction_lambda(lam, s3, bucket, archive, role)
    verifier(url_api)
    interface = construire_interface(url_api)
    if a.frontend == "amplify":
        url_web = interface_amplify(s, interface)
    else:
        url_web = interface_s3(s, compte, RACINE / "frontend" / "dist")
    print("\n" + "=" * 60)
    print(f"Interface : {url_web}")
    print(f"API       : {url_api}api/sante")
    print(f"S3        : s3://{bucket}/ (data/, dossiers/)")
    print("=" * 60)


if __name__ == "__main__":
    main()
