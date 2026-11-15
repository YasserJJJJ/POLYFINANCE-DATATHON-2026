"""Recompute a saved calculation locally, without repeating any inference.

This compares numerical artifacts. It does not replay a user's decision or
claim deterministic model generation. Archived source is verified, not executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from alphaforge_app.decision.finance import analyze
from alphaforge_app.decision.store import Store


def equivalent(a, b):
    if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-8)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equivalent(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(equivalent(x, y) for x, y in zip(a, b))
    return a == b


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dossier")
    parser.add_argument("--state-root", type=Path, default=ROOT / "runtime/decision")
    parser.add_argument("--analysis-ref")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    store = Store(args.state_root)
    snapshot = store.snapshot(args.dossier)
    piece = store.artifact(args.dossier, args.analysis_ref) if args.analysis_ref else snapshot["current_analysis"]
    report = {"dossier": args.dossier, "model_calls": 0,
              "scope": "Recalcul local avec le moteur courant ; aucune inférence rejouée."}
    if not piece:
        report.update(status="no_current_calculation", equivalent=False)
    else:
        original = piece["content"]
        replay = analyze(original["inputs"])
        fields = ("status", "options", "claims")
        comparisons = {key: equivalent(original.get(key), replay.get(key)) for key in fields}
        report.update(
            status="compared", analysis_ref=piece["ref"],
            original_method=original["method"]["id"], current_method=replay["method"]["id"],
            comparisons=comparisons, equivalent=all(comparisons.values()),
            original_claims=original.get("claims", []), recomputed_claims=replay.get("claims", []),
            tolerance={"relative": 1e-10, "absolute": 1e-8},
        )
        task = next(t for t in snapshot["tasks"] if piece["ref"] in t.get("output_refs", []))
        run = next(r for r in snapshot["runs"] if r["id"] == task["run_id"])
        manifest = run["request"].get("software_manifest", {})
        report["source_run_id"] = run["id"]
        bundle_hash = manifest.get("source_bundle_object")
        if bundle_hash:
            bundle = store._load_object(bundle_hash)
            report["source_bundle_verified"] = all(
                hashlib.sha256(text.encode()).hexdigest() == manifest["files"].get(name)
                for name, text in bundle["files"].items()
            )
            report["source_bundle_object"] = bundle_hash
        else:
            report["source_bundle_verified"] = False
            report["source_bundle_limitation"] = "Ancien run : hashes conservés, pas de bundle de sources embarqué."
        report["interpretation"] = (
            "L'égalité numérique ne valide ni données fournisseur ni choix personnel. "
            "Une différence de méthode exige examen ; aucune migration implicite des entrées."
        )
    text = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text)
    return 0 if report["equivalent"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
