#!/bin/zsh
set -eu
cd -- "$(dirname -- "$0")"
if [[ ! -x .venv/bin/python ]]; then
  echo "Préparer l’environnement : python3 -m venv .venv puis .venv/bin/python -m pip install -r requirements.txt"
  read "?Appuie sur Entrée pour fermer."
  exit 1
fi
if ! .venv/bin/python scripts/launch.py; then
  read "?Appuie sur Entrée pour fermer."
  exit 1
fi
