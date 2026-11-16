"""Déploie AlphaForge sur AWS en une commande (compte d'équipe du datathon, région us-east-1).

    python infra/deployer.py                      # tout : S3, Lambda + Function URL, interface sur Amplify
    python infra/deployer.py --plan               # lecture seule : ressources et politiques exactes
    python infra/deployer.py --frontend s3        # choix explicite d'un hébergement statique S3
    python infra/deployer.py --seulement-construire   # fabrique le zip et l'interface, sans toucher à AWS

Ce que ça crée (idempotent : on peut le relancer pour mettre à jour) :
  - un bucket S3 `alphaforge-<compte>-<région>` : données du jeu de départ (data/), code (code/), dossiers de
    décision archivés par l'API (dossiers/) ;
  - un rôle IAM `alphaforge-lambda` : journaux, lecture/écriture du bucket, appel des modèles Bedrock ;
  - une fonction Lambda `alphaforge-api` (Python 3.12) avec une Function URL publique ;
  - l'interface React, hébergée sur AWS Amplify (déploiement manuel, sans Git).

Identifiants : AWS_PROFILE (défaut « alphaforge ») ou variables AWS_* du terminal.
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
COMPTE_ATTENDU = "471112821226"
MODELES = [os.environ.get("ALPHAFORGE_MODELE", "global.anthropic.claude-sonnet-5"),
           os.environ.get("ALPHAFORGE_MODELE_LEGER", "global.amazon.nova-2-lite-v1:0")]
POLITIQUE_LOGS = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"


def etape(texte: str) -> None:
    print(f"\n▶ {texte}", flush=True)


def session():
    import boto3
    from botocore.exceptions import ProfileNotFound

    profil = os.environ.get("AWS_PROFILE")
    if not profil and not os.environ.get("AWS_ACCESS_KEY_ID"):
        profil = "alphaforge"
    try:
        return boto3.Session(profile_name=profil, region_name=REGION) if profil else boto3.Session(region_name=REGION)
    except ProfileNotFound:
        sys.exit("Profil AWS introuvable. Lance d'abord infra\\enregistrer_identifiants.ps1 (voir infra/README.md).")


def ressources_modeles(bedrock) -> list[str]:
    """Résout en lecture les profils utilisés et toutes leurs destinations réelles."""
    arns = set()
    for modele in MODELES:
        profil = bedrock.get_inference_profile(inferenceProfileIdentifier=modele)
        if profil.get("status") != "ACTIVE" or not profil.get("models"):
            raise ValueError(f"Profil d'inférence indisponible : {modele}")
        arns.add(profil["inferenceProfileArn"])
        arns.update(m["modelArn"] for m in profil["models"])
    if any("*" in arn for arn in arns):
        raise ValueError("Une ressource Bedrock résolue contient un joker.")
    return sorted(arns)


def politique_execution(bucket: str, arns_modeles: list[str], arn_guardrail: str | None = None) -> dict:
    regles = [
        {"Effect": "Allow", "Action": "s3:ListBucket", "Resource": f"arn:aws:s3:::{bucket}",
         "Condition": {"StringLike": {"s3:prefix": ["data/*"]}}},
        {"Effect": "Allow", "Action": "s3:GetObject", "Resource": f"arn:aws:s3:::{bucket}/data/*"},
        {"Effect": "Allow", "Action": "s3:PutObject", "Resource": f"arn:aws:s3:::{bucket}/dossiers/*"},
        {"Effect": "Allow", "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
         "Resource": arns_modeles},
    ]
    if arn_guardrail:
        regles.append({"Effect": "Allow", "Action": "bedrock:ApplyGuardrail", "Resource": arn_guardrail})
    return {"Version": "2012-10-17", "Statement": regles}


def plan_deploiement(s, frontend: str, concurrence: int) -> dict:
    """Aucun appel de création, aucune inférence et aucune construction locale."""
    compte = s.client("sts").get_caller_identity()["Account"]
    if compte != COMPTE_ATTENDU or REGION != "us-east-1":
        raise ValueError("Le mandat autorise uniquement le compte 471112821226 en us-east-1.")
    if not 1 <= concurrence <= 5:
        raise ValueError("La concurrence réservée doit être comprise entre 1 et 5.")
    bedrock = s.client("bedrock")
    arns = ressources_modeles(bedrock)
    guardrail = os.environ.get("ALPHAFORGE_GUARDRAIL_ID")
    arn_guardrail = None
    if guardrail:
        arn_guardrail = bedrock.get_guardrail(
            guardrailIdentifier=guardrail,
            guardrailVersion=os.environ.get("ALPHAFORGE_GUARDRAIL_VERSION", "DRAFT"))["guardrailArn"]
    bucket = f"alphaforge-{compte}-{REGION}"
    groupe = f"/aws/lambda/{NOM_FONCTION}"
    logs_existants = s.client("logs").describe_log_groups(logGroupNamePrefix=groupe).get("logGroups", [])
    return {
        "compte": compte, "region": REGION, "frontend": frontend,
        "ressources": [
            {"service": "s3", "nom": bucket, "arn": f"arn:aws:s3:::{bucket}", "acces": "privé"},
            {"service": "iam", "nom": NOM_ROLE, "arn": f"arn:aws:iam::{compte}:role/{NOM_ROLE}"},
            {"service": "lambda", "nom": NOM_FONCTION,
             "arn": f"arn:aws:lambda:{REGION}:{compte}:function:{NOM_FONCTION}",
             "url": "Function URL publique, AuthType NONE", "concurrence_reservee": concurrence},
            {"service": "amplify" if frontend == "amplify" else "s3",
             "nom": NOM_APP_AMPLIFY if frontend == "amplify" else f"alphaforge-web-{compte}-{REGION}",
             "acces": "interface publique ; aucun dossier de décision"},
            {"service": "logs", "nom": groupe, "creation": "automatique lors des invocations Lambda"},
        ],
        "cors": "Origine exacte du site Amplify ou S3 obtenue avant de configurer Lambda ; aucun joker.",
        "politique_role": politique_execution(bucket, arns, arn_guardrail),
        "politique_journaux": POLITIQUE_LOGS,
        "modeles": MODELES, "guardrail_existant": arn_guardrail,
        "groupe_journaux_existait": any(g["logGroupName"] == groupe for g in logs_existants),
        "creation_guardrail": "Commande séparée infra/creer_guardrail.py ; --verifier pour son plan.",
    }


class SuiviCreations:
    """Journal durable des seules ressources créées par cette tentative."""
    def __init__(self, chemin: Path, plan: dict):
        if chemin.exists():
            raise ValueError(f"Journal déjà présent : {chemin}. Choisir un nouveau --journal.")
        self.chemin = chemin
        self.donnees = {"statut": "en_cours", "plan": plan, "creations": []}
        self.enregistrer()

    def enregistrer(self):
        self.chemin.parent.mkdir(parents=True, exist_ok=True)
        temporaire = self.chemin.with_suffix(".tmp")
        temporaire.write_text(json.dumps(self.donnees, ensure_ascii=False, indent=2, default=str) + "\n",
                              encoding="utf-8")
        temporaire.replace(self.chemin)

    def ajouter(self, service: str, nom: str, arn: str):
        self.donnees["creations"].append({"service": service, "nom": nom, "arn": arn,
                                          "region": REGION, "etat": "cree"})
        self.enregistrer()


def _noter(suivi, service, nom, arn):
    if suivi is not None:
        suivi.ajouter(service, nom, arn)


def _code_erreur(e):
    return getattr(e, "response", {}).get("Error", {}).get("Code", type(e).__name__)


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

def bucket_s3(s3, compte: str, suivi=None) -> str:
    nom = f"alphaforge-{compte}-{REGION}"
    etape(f"Amazon S3 : bucket {nom}")
    try:
        s3.head_bucket(Bucket=nom)
        print("  déjà là")
    except Exception as e:
        if _code_erreur(e) not in ("404", "NoSuchBucket", "NotFound"):
            raise
        args = {"Bucket": nom}
        if REGION != "us-east-1":
            args["CreateBucketConfiguration"] = {"LocationConstraint": REGION}
        s3.create_bucket(**args)
        _noter(suivi, "s3", nom, f"arn:aws:s3:::{nom}")
        print("  créé")
    s3.put_public_access_block(Bucket=nom, PublicAccessBlockConfiguration={
        "BlockPublicAcls": True, "IgnorePublicAcls": True, "BlockPublicPolicy": True, "RestrictPublicBuckets": True})
    data = RACINE / "data" / "raw" / "alphaforge_starter"
    for f in sorted(data.iterdir()):
        if f.is_file() and f.suffix in (".csv", ".md", ".txt"):
            s3.upload_file(str(f), nom, f"data/{f.name}")
    print(f"  données du jeu de départ envoyées dans s3://{nom}/data/")
    return nom


def role_iam(iam, politique: dict, suivi=None) -> str:
    etape(f"IAM : rôle {NOM_ROLE}")
    confiance = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "sts:AssumeRole",
                                                        "Principal": {"Service": "lambda.amazonaws.com"}}]}
    try:
        arn = iam.create_role(RoleName=NOM_ROLE, AssumeRolePolicyDocument=json.dumps(confiance),
                              Description="AlphaForge : API Lambda, S3 et Bedrock")["Role"]["Arn"]
        _noter(suivi, "iam", NOM_ROLE, arn)
        print("  créé")
    except iam.exceptions.EntityAlreadyExistsException:
        arn = iam.get_role(RoleName=NOM_ROLE)["Role"]["Arn"]
        print("  déjà là")
    iam.attach_role_policy(RoleName=NOM_ROLE, PolicyArn=POLITIQUE_LOGS)
    iam.put_role_policy(RoleName=NOM_ROLE, PolicyName="alphaforge-acces", PolicyDocument=json.dumps(politique))
    return arn


def fonction_lambda(lam, s3, bucket: str, archive: Path, role_arn: str, origine: str,
                    concurrence: int, suivi=None) -> str:
    etape(f"AWS Lambda : fonction {NOM_FONCTION}")
    cle = "code/alphaforge-lambda.zip"
    s3.upload_file(str(archive), bucket, cle)
    env = {"Variables": {"ALPHAFORGE_DATA_BUCKET": bucket, "ALPHAFORGE_LLM": "auto",
                         "ALPHAFORGE_ORIGINES_INTERFACE": origine,
                         "ALPHAFORGE_MODELE": MODELES[0], "ALPHAFORGE_MODELE_LEGER": MODELES[1]}}
    # Guardrail Bedrock (infra/creer_guardrail.py) : transmis à la fonction s'il est défini dans le terminal.
    for variable in ("ALPHAFORGE_GUARDRAIL_ID", "ALPHAFORGE_GUARDRAIL_VERSION"):
        if os.environ.get(variable):
            env["Variables"][variable] = os.environ[variable]
    existe = True
    try:
        lam.get_function(FunctionName=NOM_FONCTION)
    except lam.exceptions.ResourceNotFoundException:
        existe = False
    if not existe:
        for essai in range(12):  # le rôle IAM met quelques secondes à être utilisable
            try:
                creee = lam.create_function(
                    FunctionName=NOM_FONCTION, Runtime="python3.12", Role=role_arn,
                    Handler="lambda_handler.handler", Code={"S3Bucket": bucket, "S3Key": cle},
                    Timeout=90, MemorySize=1536, Environment=env,
                    Description="AlphaForge : API du second avis")
                _noter(suivi, "lambda", NOM_FONCTION, creee["FunctionArn"])
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
    # Posée avant l'adresse publique : jamais de fenêtre avec une concurrence non bornée.
    lam.put_function_concurrency(FunctionName=NOM_FONCTION, ReservedConcurrentExecutions=concurrence)
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
        # Un refus d'autorisation remonte au nettoyage de la tentative ; aucun contournement.
    print(f"  URL de l'API : {url}")
    return url


def application_amplify(session_aws, suivi=None) -> dict:
    """Obtient le domaine avant de configurer le CORS de Lambda."""
    etape("AWS Amplify : application et branche")
    amp = session_aws.client("amplify")
    app = next((a for a in amp.list_apps(maxResults=100)["apps"] if a["name"] == NOM_APP_AMPLIFY), None)
    if not app:
        app = amp.create_app(name=NOM_APP_AMPLIFY, description="AlphaForge AI : interface du second avis")["app"]
        _noter(suivi, "amplify", app["appId"], app["appArn"])
        print("  application créée")
    branche = "main"
    try:
        amp.get_branch(appId=app["appId"], branchName=branche)
    except amp.exceptions.NotFoundException:
        creee = amp.create_branch(appId=app["appId"], branchName=branche, stage="PRODUCTION")["branch"]
        _noter(suivi, "amplify_branch", f"{app['appId']}/{branche}", creee["branchArn"])
    return app


def interface_amplify(session_aws, archive: Path, app: dict) -> str:
    etape("AWS Amplify : publication de l'interface")
    amp = session_aws.client("amplify")
    branche = "main"
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
        raise RuntimeError(f"Le déploiement Amplify a fini avec le statut {statut}.")
    return f"https://{branche}.{app['defaultDomain']}"


def interface_s3(session_aws, compte: str, dossier_dist: Path, suivi=None) -> str:
    etape("Amazon S3 : site statique pour l'interface")
    import mimetypes

    s3 = session_aws.client("s3")
    nom = f"alphaforge-web-{compte}-{REGION}"
    try:
        s3.head_bucket(Bucket=nom)
    except Exception as e:
        if _code_erreur(e) not in ("404", "NoSuchBucket", "NotFound"):
            raise
        args = {"Bucket": nom}
        if REGION != "us-east-1":
            args["CreateBucketConfiguration"] = {"LocationConstraint": REGION}
        s3.create_bucket(**args)
        _noter(suivi, "s3", nom, f"arn:aws:s3:::{nom}")
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


def verifier(url_api: str) -> dict:
    etape("Vérification de l'API déployée")
    for tentative in range(6):
        try:
            with urllib.request.urlopen(url_api.rstrip("/") + "/api/sante", timeout=60) as r:
                sante = json.loads(r.read())
            if not sante.get("ok"):
                raise RuntimeError("L'API indique ok=false.")
            print(f"  /api/sante : ok={sante['ok']} · agents IA (Bedrock) : {'oui' if sante['llm'] else 'non'}"
                  + ("" if sante["llm"] else f" ({sante.get('raison')})"))
            return sante
        except Exception as e:  # noqa: BLE001
            print(f"  essai {tentative + 1}/6 : {type(e).__name__}")
            time.sleep(6)
    raise RuntimeError("L'API ne répond pas après six essais ; consulter CloudWatch.")


def noter_journaux(s, suivi: SuiviCreations) -> None:
    """Ne revendique jamais un groupe antérieur à cette tentative."""
    creations = suivi.donnees["creations"]
    if suivi.donnees["plan"]["groupe_journaux_existait"] or any(r["service"] == "logs" for r in creations):
        return
    if not any(r["service"] == "lambda" for r in creations):
        return
    nom = f"/aws/lambda/{NOM_FONCTION}"
    groupes = s.client("logs").describe_log_groups(logGroupNamePrefix=nom).get("logGroups", [])
    for groupe in groupes:
        if groupe["logGroupName"] == nom:
            suivi.ajouter("logs", nom, groupe["arn"])
            break


def nettoyer(s, suivi: SuiviCreations) -> None:
    """Retour arrière borné au journal ; jamais de découverte suivie de suppression."""
    etape("Nettoyage des seules ressources créées par cette tentative")
    absentes = {"NoSuchEntity", "NoSuchEntityException", "NoSuchBucket", "ResourceNotFoundException",
                "NotFoundException"}
    for ressource in reversed(suivi.donnees["creations"]):
        if ressource["etat"] == "supprime":
            continue
        service, nom = ressource["service"], ressource["nom"]
        try:
            if service == "logs":
                s.client("logs").delete_log_group(logGroupName=nom)
            elif service == "amplify_branch":
                application, branche = nom.split("/", 1)
                s.client("amplify").delete_branch(appId=application, branchName=branche)
            elif service == "amplify":
                s.client("amplify").delete_app(appId=nom)
            elif service == "lambda":
                s.client("lambda").delete_function(FunctionName=nom)
            elif service == "iam":
                iam = s.client("iam")
                try:
                    iam.delete_role_policy(RoleName=nom, PolicyName="alphaforge-acces")
                except Exception as e:
                    if _code_erreur(e) not in absentes:
                        raise
                iam.detach_role_policy(RoleName=nom, PolicyArn=POLITIQUE_LOGS)
                iam.delete_role(RoleName=nom)
            elif service == "s3":
                s3 = s.client("s3")
                for page in s3.get_paginator("list_objects_v2").paginate(Bucket=nom):
                    objets = [{"Key": o["Key"]} for o in page.get("Contents", [])]
                    if objets:
                        resultat = s3.delete_objects(Bucket=nom, Delete={"Objects": objets, "Quiet": True})
                        if resultat.get("Errors"):
                            raise RuntimeError(f"Suppression S3 incomplète : {resultat['Errors']}")
                s3.delete_bucket(Bucket=nom)
            else:
                raise ValueError(f"Service non prévu pour le nettoyage : {service}")
            ressource["etat"] = "supprime"
        except Exception as e:
            if _code_erreur(e) in absentes:
                ressource["etat"] = "supprime"
            else:
                ressource["etat"] = "nettoyage_echoue"
                ressource["erreur_nettoyage"] = str(e)
        suivi.enregistrer()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--frontend", choices=["amplify", "s3"], default="amplify")
    p.add_argument("--seulement-construire", action="store_true", help="construit les zips sans appeler AWS")
    p.add_argument("--plan", action="store_true", help="affiche le plan en lecture seule, sans construire")
    p.add_argument("--concurrence", type=int, default=2, help="concurrence réservée Lambda, de 1 à 5 (défaut 2)")
    p.add_argument("--journal", type=Path, help="nouveau fichier JSON de suivi des créations et du nettoyage")
    a = p.parse_args()
    if a.seulement_construire and not a.plan:
        BUILD.mkdir(parents=True, exist_ok=True)
        construire_zip_lambda()
        construire_interface(None)
        print("\nConstruction terminée (rien n'a été envoyé sur AWS).")
        return

    s = session()
    plan = plan_deploiement(s, a.frontend, a.concurrence)
    print(json.dumps(plan, ensure_ascii=False, indent=2), flush=True)
    if a.plan:
        return
    BUILD.mkdir(parents=True, exist_ok=True)
    archive = construire_zip_lambda()
    # Échouer localement sur une compilation avant de créer les ressources.
    construire_interface(None)
    suivi = SuiviCreations(a.journal or BUILD / f"creation-{time.time_ns()}.json", plan)
    compte = plan["compte"]
    try:
        app = application_amplify(s, suivi) if a.frontend == "amplify" else None
        origine = (f"https://main.{app['defaultDomain']}" if app else
                   f"http://alphaforge-web-{compte}-{REGION}.s3-website-{REGION}.amazonaws.com")
        s3, iam, lam = s.client("s3"), s.client("iam"), s.client("lambda")
        bucket = bucket_s3(s3, compte, suivi)
        role = role_iam(iam, plan["politique_role"], suivi)
        url_api = fonction_lambda(lam, s3, bucket, archive, role, origine, a.concurrence, suivi)
        suivi.donnees.update(url_api=url_api, url_interface=origine, sante=verifier(url_api))
        noter_journaux(s, suivi)
        interface = construire_interface(url_api)
        url_web = (interface_amplify(s, interface, app) if app else
                   interface_s3(s, compte, RACINE / "frontend" / "dist", suivi))
        suivi.donnees["statut"] = "deployee"
        suivi.enregistrer()
    except Exception as e:
        suivi.donnees.update(statut="echec", erreur=str(e), code_erreur=_code_erreur(e))
        suivi.enregistrer()
        try:
            noter_journaux(s, suivi)
        except Exception as erreur_logs:
            suivi.donnees["verification_journaux_echouee"] = str(erreur_logs)
            suivi.enregistrer()
        nettoyer(s, suivi)
        print(f"Déploiement arrêté. État et nettoyage : {suivi.chemin}", file=sys.stderr)
        raise
    print("\n" + "=" * 60)
    print(f"Interface : {url_web}")
    print(f"API       : {url_api}api/sante")
    print(f"S3        : s3://{bucket}/ (data/, dossiers/)")
    print("=" * 60)


if __name__ == "__main__":
    main()
