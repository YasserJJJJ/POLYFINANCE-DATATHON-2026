#!/usr/bin/env bash
# Lance l'application web locale AlphaForge et ouvre le navigateur (http://127.0.0.1:8765).
set -euo pipefail
cd "$(dirname "$0")/.."
exec uv run python -m datathon2026.app --ouvrir "$@"
