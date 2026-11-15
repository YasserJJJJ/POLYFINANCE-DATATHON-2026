"""Exercise the real HTTP API; --live explicitly enables billable AWS calls.

No reference outputs are fed to the agents. --existing accepts IDs from an
already started live demonstration, avoiding duplicate initial requests.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from alphaforge_app.decision.finance import examples


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def await_dossier(client, ident):
    deadline = time.monotonic() + 600
    prior = None
    while time.monotonic() < deadline:
        result = client.get(f"/api/dossiers/{ident}")
        result.raise_for_status()
        d = result.json()
        state = (d["revision"], d["status"], tuple((t["role"], t["status"]) for t in d["tasks"]))
        if state != prior:
            print(ident, d["revision"], d["status"], state[2], flush=True)
            prior = state
        if d["status"] in {"complete", "waiting", "error"}:
            return d
        time.sleep(1)
    raise TimeoutError("La démonstration attend encore une exécution. Les dossiers restent reprenables.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://127.0.0.1:8768")
    p.add_argument("--live", action="store_true", help="Utiliser les quatre inférences AWS par passage.")
    p.add_argument("--existing", type=Path, help="JSON contenant robert_aws et amira_aws déjà créés.")
    p.add_argument("--output", type=Path, default=ROOT / "runtime/decision-demo")
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    ids = json.loads(args.existing.read_text()) if args.existing else {}
    client = httpx.Client(base_url=args.base, timeout=30, trust_env=False)
    summary = {"live_requested": args.live, "api": args.base, "cases": {}, "reference_outputs_used": False}
    for example in examples():
        key = example["id"] + "_aws"
        if key not in ids:
            reply = client.post("/api/dossiers", json={
                "prompt": example["prompt"], "facts": example["facts"], "use_ai": args.live})
            reply.raise_for_status()
            ids[key] = reply.json()["id"]
        ident = ids[key]
        d = await_dossier(client, ident)
        # A re-opened, already revised dossier is not its initial snapshot.
        loaded_name = ("robert-loaded.json" if example["id"] == "robert"
                       and d.get("active_problem") and d["active_problem"].get("withdrawal_cad") != 30000
                       else f"{example['id']}-initial.json")
        write(args.output / loaded_name, d)
        if d["status"] != "complete":
            summary["cases"][example["id"]] = {"id": ident, "status": d["status"], "error": d["runs"][-1]["error"]}
            continue
        if example["id"] == "robert":
            if d["active_problem"]["withdrawal_cad"] == 30000:
                revision = example["suggested_revision"]
                reply = client.post(f"/api/dossiers/{ident}/revise", json={
                    **revision, "intent": "replace", "base_revision": d["revision"]})
                reply.raise_for_status()
                pending = reply.json()
                assert pending["current_view"] is None, "L’ancienne vue ne doit pas rester courante."
                write(args.output / "robert-invalidated.json", pending)
                d = await_dossier(client, ident)
            write(args.output / "robert-revised.json", d)
        analysis = d["current_analysis"]["content"] if d["current_analysis"] else None
        summary["cases"][example["id"]] = {
            "id": ident, "status": d["status"], "revision": d["revision"],
            "analysis_status": analysis["status"] if analysis else None,
            "method": analysis["method"]["id"] if analysis else None,
            "claims": analysis["claims"] if analysis else [],
            "changed_fields": d["comparison"]["changed_fields"] if d["comparison"] else [],
            "reused": d["comparison"]["reused"] if d["comparison"] else [],
            "invalidated": d["comparison"]["invalidated"] if d["comparison"] else [],
            "roles": [{"role": t["role"], "status": t["status"], "output_refs": t["output_refs"]} for t in d["tasks"]],
            "aws_calls": [{"request_id": a.get("request_id"), "role": a["role"], "usage": a.get("usage"),
                           "provider": a.get("provider"), "model": a.get("model"), "status": a["status"]}
                          for a in d["attempts"] if a["tool"] == "bedrock.converse"],
        }
    write(args.output / "ids.json", ids)
    write(args.output / "summary.json", summary)
    print(json.dumps({k: {"id": v["id"], "status": v["status"]} for k, v in summary["cases"].items()}, ensure_ascii=False), flush=True)
    return 0 if all(c["status"] == "complete" for c in summary["cases"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
