"""Create a local recovery snapshot; no inference, credentials or deployment."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from alphaforge_app.datasets import resolve_data_directory

DEST = ROOT / "artifacts/folio_integre"
PATHS = [
    "alphaforge_app", "scripts", "tests", "requirements.txt",
    "Ouvrir_AlphaForge.command", "README.md", "docs/folio", "docs/recherche",
    "docs/conception", "docs/implementation", "docs/defense",
    "runtime/decision/objects", "runtime/decision/research",
]


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def included(info: tarfile.TarInfo):
    if "__pycache__" in info.name.split("/") or info.name.endswith((".pyc", ".DS_Store")):
        return None
    return info


def main():
    DEST.mkdir(exist_ok=True)
    for name in ("dossiers", "checkpoints"):
        with sqlite3.connect(ROOT / f"runtime/decision/{name}.sqlite3") as source:
            with sqlite3.connect(DEST / f"{name}.sqlite3") as target:
                source.backup(target)
    archive = DEST / "folio-0.7.0-source-et-etat.tar.gz"
    temporary = archive.with_suffix(".tmp")
    data = resolve_data_directory()
    with tarfile.open(temporary, "w:gz", compresslevel=5) as tar:
        for name in PATHS:
            if (ROOT / name).exists():
                tar.add(ROOT / name, arcname=name, filter=included)
        for name in ("dossiers", "checkpoints"):
            tar.add(DEST / f"{name}.sqlite3", arcname=f"runtime/decision/{name}.sqlite3")
        tar.add(data, arcname="data/alphaforge_starter", filter=included)
    os.replace(temporary, archive)
    files = [
        path for path in (ROOT / "alphaforge_app").rglob("*")
        if path.is_file() and path.suffix in {".py", ".js", ".html", ".css"}
        and "__pycache__" not in path.parts
    ]
    with tarfile.open(archive, "r:gz") as tar:
        for path in files:
            content = tar.extractfile(str(path.relative_to(ROOT))).read()
            assert hashlib.sha256(content).hexdigest() == digest(path)
        for name in ("dossiers", "checkpoints"):
            content = tar.extractfile(f"runtime/decision/{name}.sqlite3").read()
            assert hashlib.sha256(content).hexdigest() == digest(DEST / f"{name}.sqlite3")
    manifest = {
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "version": "0.7.0",
        "archive": archive.name,
        "sha256": digest(archive),
        "bytes": archive.stat().st_size,
        "archive_readback_verified": True,
        "database_backups": {
            name: {"sha256": digest(DEST / f"{name}.sqlite3"), "method": "SQLite backup API"}
            for name in ("dossiers", "checkpoints")
        },
        "data_source": str(data),
        "source_hashes": {str(path.relative_to(ROOT)): digest(path) for path in files},
        "scope": "Local source, state, approved corpus and starter snapshot. "
                 "No credentials or virtual environment. Other realization excluded.",
    }
    (DEST / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps({"backup_verified": True, "source_files": len(files),
                      "bytes": manifest["bytes"]}))


if __name__ == "__main__":
    main()
