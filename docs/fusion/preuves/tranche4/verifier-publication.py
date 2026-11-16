"""Réception réelle : une analyse publique Robert, NDJSON, CORS et archivage S3."""
import base64
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
import time
import urllib.error
import urllib.request

import boto3

PREUVES = Path(__file__).resolve().parent
RACINE = PREUVES.parents[3]
SORTIE = PREUVES / "public"
SORTIE.mkdir(exist_ok=True)


def sauver(nom, objet):
    (SORTIE / nom).write_text(json.dumps(objet, ensure_ascii=False, indent=2, default=str) + "\n")


def get(url):
    with urllib.request.urlopen(url, timeout=45) as r:
        return r.status, dict(r.headers), r.read()


journal = json.loads((PREUVES / "redéploiement.json").read_text())
assert journal["statut"] == "deployee"
api, interface = journal["url_api"].rstrip("/"), journal["url_interface"]
s = boto3.Session(profile_name="alphaforge", region_name="us-east-1")
assert s.client("sts").get_caller_identity()["Account"] == "471112821226"
status, headers, contenu = get(api + "/api/sante")
sante = json.loads(contenu)
sauver("sante.json", sante)
assert status == 200 and sante["ok"] and sante["llm"] and sante["region"] == "us-east-1"
status_web, _, html = get(interface)
sauver("interface.json", {"url": interface, "status": status_web, "octets": len(html),
                         "sha256": hashlib.sha256(html).hexdigest()})
assert status_web == 200 and b'<div id="root">' in html
assets = []
for chemin in re.findall(r'(?:src|href)="(/assets/[^" ]+)"', html.decode()):
    statut, _, contenu_asset = get(interface.rstrip('/') + chemin)
    local = (RACINE / 'frontend/dist' / chemin.lstrip('/')).read_bytes()
    assert statut == 200 and contenu_asset == local
    assets.append({'chemin': chemin, 'identique_dist_local': True,
                   'sha256': hashlib.sha256(local).hexdigest()})
assert len(assets) >= 2
sauver('assets.json', assets)

cors = {}
for origine in (interface, "https://origine-inconnue.example"):
    req = urllib.request.Request(api + "/api/analyse", method="OPTIONS",
                                 headers={"Origin": origine, "Access-Control-Request-Method": "POST",
                                          "Access-Control-Request-Headers": "content-type"})
    try:
        r = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        r = e
    with r:
        cors[origine] = {"statut": r.code, "origine_autorisee": r.headers.get("Access-Control-Allow-Origin")}
sauver("cors.json", cors)
assert cors[interface] == {"statut": 200, "origine_autorisee": interface}
assert cors["https://origine-inconnue.example"]["statut"] == 400

entree = json.loads((PREUVES / "robert-entree.json").read_text())
requete = urllib.request.Request(api + "/api/analyse/flux", data=json.dumps(entree).encode(),
                                headers={"Content-Type": "application/json", "Origin": interface})
debut_utc = datetime.now(timezone.utc).isoformat()
debut = time.perf_counter()
lignes, receptions, dossier = [], [], None
with urllib.request.urlopen(requete, timeout=180) as response:
    entetes_a = time.perf_counter() - debut
    entetes = dict(response.headers)
    while ligne := response.readline():
        reception = time.perf_counter() - debut
        evenement = json.loads(ligne)
        lignes.append(evenement)
        receptions.append({"type": evenement["type"], "apres_s": round(reception, 6),
                           "agent": evenement.get("etape", {}).get("agent")})
        if evenement["type"] == "dossier":
            dossier = evenement["dossier"]
        assert evenement["type"] != "erreur", evenement
sauver("evenements.json", lignes)
sauver("reception-ndjson.json", {"url": api + "/api/analyse/flux", "debut_utc": debut_utc,
                               "entetes_apres_s": entetes_a, "entetes": entetes, "receptions": receptions})
assert dossier and len(receptions) >= 2
sauver("robert-bedrock.json", dossier)
reference = json.loads((PREUVES / "robert-hors-ligne.json").read_text())
controles = {k: reference[k] == dossier[k] for k in ("verdict", "regles", "options", "bascule", "comparaison")}
assert all(controles.values()), controles
assert dossier["appels_modele"] and all(a["request_id"] for a in dossier["appels_modele"])
assert all(a["stop_reason"] == "end_turn" for a in dossier["appels_modele"]), dossier["appels_modele"]

bucket = next(r["nom"] for r in journal["plan"]["ressources"] if r["service"] == "s3")
s3 = s.client("s3")
archive = None
for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix="dossiers/"):
    for objet in page.get("Contents", []):
        if objet["LastModified"] < datetime.fromisoformat(debut_utc).replace(microsecond=0):
            continue
        contenu = s3.get_object(Bucket=bucket, Key=objet["Key"])["Body"].read()
        if json.loads(contenu) == dossier:
            archive = {"bucket": bucket, "cle": objet["Key"], "egalite_complete": True,
                       "sha256": hashlib.sha256(contenu).hexdigest()}
            (SORTIE / "robert-s3.json").write_bytes(contenu)
assert archive, "Aucune copie exacte du dossier dans S3"
sauver("archivage.json", archive)
configuration = s.client("lambda").get_function_configuration(FunctionName="alphaforge-api")
code_sha = base64.b64encode(hashlib.sha256((RACINE / "infra/build/alphaforge-lambda.zip").read_bytes()).digest()).decode()
assert configuration["CodeSha256"] == code_sha
concurrence = s.client("lambda").get_function_concurrency(FunctionName="alphaforge-api")
sauver("lambda.json", {**{k: configuration[k] for k in ("FunctionArn", "Runtime", "Role", "Timeout",
                                                     "MemorySize", "CodeSha256", "LastModified")},
                      "ReservedConcurrentExecutions": concurrence["ReservedConcurrentExecutions"],
                      "code_local_identique": True})
assert concurrence["ReservedConcurrentExecutions"] == 2
bilan = {"sante_ok": True, "interface_ok": True, "cors_ok": True, "decisions_identiques": controles,
         "archivage": archive, "appels": dossier["appels_modele"],
         "premiere_ligne_s": receptions[0]["apres_s"], "derniere_ligne_s": receptions[-1]["apres_s"],
         "etalement_lignes_s": round(receptions[-1]["apres_s"] - receptions[0]["apres_s"], 6)}
sauver("bilan.json", bilan)
print(json.dumps(bilan, ensure_ascii=False, indent=2))
