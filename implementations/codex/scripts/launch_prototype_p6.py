#!/usr/bin/env python3
"""Open the isolated Prompt 6 prototype; preserve all product processes and state."""
from pathlib import Path
import json
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:8770"


def check():
    try:
        with urllib.request.urlopen(URL + "/api/prototype/health", timeout=2) as r:
            return json.load(r)
    except OSError:
        return None


if __name__ == "__main__":
    status = check()
    if status and status.get("version") != "0.6-prototype":
        sys.exit("Le port 8770 répond avec un autre service. Aucun processus n'a été arrêté.")
    if not status:
        runtime = ROOT / "runtime" / "prototype_p6"
        runtime.mkdir(parents=True, exist_ok=True)
        python = ROOT / ".venv" / "bin" / "python"
        with (runtime / "server.log").open("ab") as log:
            process = subprocess.Popen(
                [str(python), "-m", "uvicorn", "prototype.prompt6.server:app",
                 "--host", "127.0.0.1", "--port", "8770"],
                cwd=ROOT, stdout=log, stderr=log, start_new_session=True,
            )
        for _ in range(40):
            status = check()
            if status:
                break
            if process.poll() is not None:
                sys.exit(f"Le prototype n'a pas démarré. Voir {runtime / 'server.log'}")
            time.sleep(.25)
        if not status:
            sys.exit(f"Le prototype ne répond pas encore. Voir {runtime / 'server.log'}")
        (runtime / "launcher.json").write_text(json.dumps({
            "pid": process.pid, "url": URL, "workspace": str(ROOT),
            "product_modified": False,
        }, indent=2))
    print(URL)
    if "--no-browser" not in sys.argv:
        webbrowser.open(URL)
