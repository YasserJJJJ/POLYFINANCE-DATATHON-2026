"""Start or reuse only this project's loopback server, then open the browser."""
from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
STATE = RUNTIME / "server.json"


def health(port):
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f"http://127.0.0.1:{port}/api/health", timeout=1) as reply:
            result = json.load(reply)
            return (result.get("application") == "alphaforge" and result.get("workspace") == str(ROOT)
                    and result.get("version") == "0.7.0")
    except (OSError, ValueError, urllib.error.URLError):
        return False


def available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    RUNTIME.mkdir(exist_ok=True)
    previous = {}
    if STATE.is_file():
        try:
            previous = json.loads(STATE.read_text())
        except ValueError:
            pass
    port = 8768
    if not health(port):
        if not available(port):
            raise SystemExit("Le port Folio 8768 est occupé par un serveur d’une autre version. Aucun autre service n’a été consulté ou arrêté. Relancez le serveur de ce dossier après l’avoir fermé.")
        with (RUNTIME / "server.log").open("ab") as log:
            child = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "alphaforge_app.main:app",
                 "--host", "127.0.0.1", "--port", str(port), "--no-access-log"],
                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                start_new_session=True,
            )
        state = {"pid": child.pid, "port": port, "workspace": str(ROOT)}
        temp = STATE.with_suffix(".tmp")
        temp.write_text(json.dumps(state))
        temp.replace(STATE)
        for _ in range(40):
            if health(port):
                break
            if child.poll() is not None:
                raise SystemExit(f"Le serveur n’a pas démarré. Voir {RUNTIME / 'server.log'}")
            time.sleep(0.25)
        else:
            raise SystemExit(f"Serveur non prêt. Voir {RUNTIME / 'server.log'}")
    url = f"http://127.0.0.1:{port}"
    print(f"AlphaForge est prêt : {url}", flush=True)
    if not args.no_browser:
        webbrowser.open(url)


if __name__ == "__main__":
    main()
