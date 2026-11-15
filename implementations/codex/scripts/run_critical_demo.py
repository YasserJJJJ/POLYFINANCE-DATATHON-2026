"""Prompt 5 adversarial demonstration through the real API and AWS route.

The saved IDs make a rerun observational rather than silently duplicating
billable calls. An intentional new experiment needs a new output directory.
No expected financial outputs are provided to the agents.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from alphaforge_app.decision.finance import examples


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def wait(client, ident):
    deadline = time.monotonic() + 900
    previous = None
    while time.monotonic() < deadline:
        response = client.get("/api/dossiers/" + ident)
        response.raise_for_status()
        dossier = response.json()
        status = (dossier["revision"], dossier["status"])
        if status != previous:
            print(ident, *status, flush=True)
            previous = status
        if dossier["status"] in {"complete", "waiting", "error"}:
            return dossier
        time.sleep(2)
    raise TimeoutError("Dossier conservé et reprenable ; aucune nouvelle demande créée.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8768")
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/defense/proofs/demo")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    ids_file = args.output / "ids.json"
    ids = json.loads(ids_file.read_text()) if ids_file.exists() else {}
    client = httpx.Client(base_url=args.base, timeout=30, trust_env=False)
    robert, amira = copy.deepcopy(examples())
    impossible = copy.deepcopy(robert["facts"])
    impossible["withdrawal_cad"] = 120000
    extracted = copy.deepcopy(robert["facts"])
    extracted.pop("capital_cad")
    cases = {
        "incomplete": {
            "prompt": "Je souhaite préserver mon capital et financer un retrait dans douze mois. "
                      "Je ne connais pas encore le montant à retirer et ne fournis ni capital ni positions. Pouvez-vous conclure ?",
            "facts": {},
        },
        "impossible": {
            "prompt": "Critique : vérifier le retrait de 120 000 CAD avec 100 000 CAD de capital, "
                      "dans les conditions abstraites explicites jointes. Ne modifier aucune contrainte.",
            "facts": impossible,
        },
        "extracted": {
            "prompt": "Mon capital est de 100 000 CAD. Dans cet exercice fictif, analyser le retrait "
                      "de 30 000 CAD à douze mois sous les hypothèses structurées jointes.",
            "facts": extracted,
        },
        "amira": {"prompt": amira["prompt"], "facts": amira["facts"]},
    }
    for name, payload in cases.items():
        if name not in ids:
            payload["use_ai"] = True
            save(args.output / (name + "-input.json"), payload)
            response = client.post("/api/dossiers", json=payload)
            response.raise_for_status()
            ids[name] = response.json()["id"]
            save(ids_file, ids)
    for name in cases:
        path = args.output / (name + "-initial.json")
        if not path.exists():
            save(path, wait(client, ids[name]))

    # Two different revisions: unstructured correction, then a structured
    # loss budget. Both are plans relative to the same initial holdings.
    for name, changes, message in [
        ("withdrawal_revision", {}, "Le retrait sera finalement de 40 000 CAD."),
        ("profile_revision", {"scenario_loss_limit_cad": 1000},
         "Mon budget maximal de perte dans chacun des deux scénarios est désormais de 1 000 CAD. "
         "Conserver le retrait de 40 000 CAD et le même portefeuille initial."),
    ]:
        path = args.output / (name + ".json")
        if path.exists():
            continue
        if name not in ids:
            current = wait(client, ids["extracted"])
            response = client.post("/api/dossiers/" + current["id"] + "/revise", json={
                "base_revision": current["revision"], "intent": "replace",
                "changes": changes, "message": message,
            })
            response.raise_for_status()
            pending = response.json()
            save(args.output / (name + "-pending.json"), pending)
            ids[name] = current["id"]
            save(ids_file, ids)
        save(path, wait(client, ids[name]))
    records = {}
    for path in args.output.glob("*.json"):
        value = json.loads(path.read_text())
        if not isinstance(value, dict) or "active_problem" not in value or path.stem.endswith("-pending"):
            continue
        analysis = (value.get("current_analysis") or {}).get("content", {})
        records[path.stem] = {
            "id": value["id"], "revision": value["revision"], "status": value["status"],
            "analysis_status": analysis.get("status"), "claims": analysis.get("claims", []),
            "capital_cad": (value.get("active_problem") or {}).get("capital_cad"),
            "withdrawal_cad": (value.get("active_problem") or {}).get("withdrawal_cad"),
            "view_available": bool(value.get("current_view")),
            "comparison": value.get("comparison"),
            "aws_receipts": [{"role": a["role"], "request_id": a.get("request_id"),
                              "status": a["status"], "provider": a.get("provider"),
                              "usage": a.get("usage")}
                             for a in value["attempts"] if a["tool"] == "bedrock.converse"],
        }
    save(args.output / "summary.json", {
        "mode": "actual_http_and_aws", "expected_outputs_supplied": False,
        "cases": records,
        "note": "Comptages par export cumulatifs ; dédupliquer les request_id pour compter les appels.",
    })
    return 1 if any(v["status"] == "error" for v in records.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
