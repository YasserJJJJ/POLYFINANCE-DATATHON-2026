"""Create and verify a local-only preservation archive using an explicit allowlist."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    included = set()
    for name in ("README.md", "WORKLOG.md", ".gitignore", ".gitattributes", "requirements.txt",
                 "requirements-docs.txt", "Ouvrir_AlphaForge.command"):
        included.add(ROOT / name)
    for folder in ("alphaforge_app", "scripts", "tests", "docs", "data", "examples"):
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix not in (".pyc", ".log"):
                included.add(path)
    # Preserve original design context required by the decision dossier links.
    for path in (ROOT / "revision_2026-11-15").glob("*.md"):
        included.add(path)
    case = ROOT / "analyse/sources/Datathon_AlphaForge_Conversion_Markdown/Datathon_Case_Officiel_2026_FR.md"
    included.add(case)
    for path in (ROOT / "artifacts/screens").glob("*.png"):
        included.add(path)
    for extension in ("*.webm", "*.mp4"):
        for path in (ROOT / "artifacts").glob(extension):
            included.add(path)
    for path in (ROOT / "output/pdf").glob("*.pdf"):
        included.add(path)
    for name in ("ui-verification.json", "ui-export.json"):
        path = ROOT / "artifacts" / name
        if path.is_file():
            included.add(path)
    revision = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        text=True, capture_output=True,
    )
    manifest = {
        "purpose": "Sauvegarde locale privée AlphaForge — pas une autorisation de redistribution des données.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_git_commit": revision.stdout.strip() if revision.returncode == 0 else None,
        "files": {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in sorted(included)},
    }
    destination = ROOT / "artifacts/AlphaForge_local_2026-11-15.zip"
    destination.parent.mkdir(exist_ok=True)
    temporary = destination.with_suffix(".tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(included):
            archive.write(path, path.relative_to(ROOT))
        archive.writestr("MANIFEST_SHA256.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    with tempfile.TemporaryDirectory(prefix="alphaforge-restore-") as directory:
        with zipfile.ZipFile(temporary) as archive:
            assert archive.testzip() is None, "Archive CRC invalide"
            archive.extractall(directory)
        restored = Path(directory)
        for name, expected in manifest["files"].items():
            assert digest((restored / name).read_bytes()) == expected, name
        import sys
        sys.path.insert(0, str(restored))
        from alphaforge_app.datasets import load_dataset
        from alphaforge_app.analytics import analyze_portfolio
        dataset = load_dataset(restored / "data/alphaforge_starter")
        result = analyze_portfolio({"XIU.TO": 1.0}, dataset=dataset)
        assert result["metrics"]["ending_value_cad"] > 0
    temporary.replace(destination)
    verification = {
        "archive": str(destination), "files": len(included),
        "bytes": destination.stat().st_size,
        "sha256": digest(destination.read_bytes()),
        "source_git_commit": manifest["source_git_commit"],
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "verification": "CRC, empreintes et calcul depuis copie restaurée réussis.",
    }
    (destination.parent / "backup-verification.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2)
    )
    print(json.dumps(verification, ensure_ascii=False))


if __name__ == "__main__":
    main()
