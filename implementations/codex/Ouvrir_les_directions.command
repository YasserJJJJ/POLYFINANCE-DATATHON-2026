#!/bin/zsh
cd "$(dirname "$0")" || exit 1
./.venv/bin/python scripts/launch_prototype_p6.py --no-browser || exit 1
open "http://127.0.0.1:8770/directions/"
