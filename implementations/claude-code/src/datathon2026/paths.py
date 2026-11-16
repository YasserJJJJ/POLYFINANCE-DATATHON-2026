"""Chemins du projet. Le dossier des données brutes peut être remplacé par DATATHON_STARTER_DIR."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
STARTER_DIR = Path(os.environ.get("DATATHON_STARTER_DIR", DATA_DIR / "raw" / "alphaforge_starter"))
EXTERNAL_DIR = DATA_DIR / "external"
PROCESSED_DIR = DATA_DIR / "processed"
