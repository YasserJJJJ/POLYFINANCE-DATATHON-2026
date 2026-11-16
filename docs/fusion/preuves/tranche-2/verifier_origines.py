"""Contrôle des transferts et originaux, sans extraction ni modification."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

racine = Path(__file__).resolve().parents[4]
archives = Path("/Users/vpro/Downloads/IMPLEMENTATION")
manifest = json.loads((Path(__file__).with_name("transferts.json")).read_text())
resultat = {"transferts": [], "archives": {}}


def sha(octets):
    return hashlib.sha256(octets).hexdigest()


for entree in manifest:
    archive = archives / entree["archive"]
    empreinte = sha(archive.read_bytes())
    assert empreinte == entree["archive_sha256"]
    resultat["archives"][archive.name] = empreinte
    with zipfile.ZipFile(archive) as z:
        source = z.read(entree["source"])
    assert sha(source) == entree["sha256_original"]
    destination = (racine / entree["destination"]).read_bytes()
    corps = b"".join(destination.splitlines(keepends=True)[4:])
    if entree["adaptation"] == "en-tête seulement":
        assert corps == source
    elif entree["adaptation"] == "imports du test":
        assert corps == source.replace(b"alphaforge_app.", b"alphaforge.moteurs.historique.")
    else:
        blend = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "blend")
        attendu = ast.get_source_segment(source.decode(), blend).encode() + b"\n"
        assert corps == attendu
    resultat["transferts"].append({"destination": entree["destination"], "identite_verifiee": True,
                                    "sha256_original": sha(source)})

archive_c = archives / "IMPLEMENTATION_identifiant-a-attribuer_2026-11-15 (Yahya).zip"
resultat["archives"][archive_c.name] = sha(archive_c.read_bytes())
assert resultat["archives"][archive_c.name] == "d05b2736b9fd9a891f55dfa137bb4503d8f02e3c1b1cf10f6d76c5b24a259a75"

proteges = ["implementations", "data", "infra", "frontend", "backend/alphaforge/dossier.py",
            "backend/alphaforge/profil.py", "backend/alphaforge/llm.py", "backend/api.py",
            "backend/alphaforge/agents/redacteur.py", "docs/contrats.md"]
subprocess.run(["git", "diff", "--exit-code", "fusion/t1", "--", *proteges], cwd=racine, check=True)
resultat["fichiers_reserves_et_originaux_git_inchanges"] = proteges
resultat["prix_sha256"] = sha((racine / "data/raw/alphaforge_starter/prices_daily.csv").read_bytes())
assert resultat["prix_sha256"] == "ff2a3f2d0a7d72ea835e8d616d041e0510f018340cef3d3e55b918830e8a569d"
kit = json.loads((racine / "docs/fusion/SOURCE_MANIFEST.json").read_text())
resultat["documents_source"] = {}
for entree in kit["files"]:
    if entree["path"] in ("CADRE-COMMUN.md", "DOSSIER-FUSION.md", "PROMPT-2-analyse-de-portefeuille.md"):
        empreinte = sha((Path(kit["source"]) / entree["path"]).read_bytes())
        # Le porteur a complété les autorisations et l'isolation du prompt 2
        # entre sa copie historique T1 et son invocation actuelle.
        attendue = ("d31de60289a340a6837c74be0a818f989dc64966e9b51fc77f8336dfd29ba761"
                    if entree["path"] == "PROMPT-2-analyse-de-portefeuille.md" else entree["sha256"])
        assert empreinte == attendue
        resultat["documents_source"][entree["path"]] = {
            "sha256_manifeste_T1": entree["sha256"], "sha256_version_recue": empreinte,
            "identique_T1": empreinte == entree["sha256"],
        }
print(json.dumps(resultat, ensure_ascii=False, indent=2))
