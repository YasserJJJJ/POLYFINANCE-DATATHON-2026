"""Read-only P5 delivery audit and optional state backup; no inference.

The backup contains SQLite snapshots and immutable state, not market data or
the full documentary corpus. Never restore it over a more recent live state.
"""
import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from alphaforge_app.decision.store import Store
from alphaforge_app.decision.service import pointer


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", action="store_true")
    args = parser.parse_args()
    proofs = ROOT / "docs/defense/proofs"
    state = ROOT / "runtime/decision"
    store = Store(state)
    cases = {
        "robert": "4089e4b0d70f40b6b20d832fa261e1dc",
        "amira": "f281a9067e4544138fa178fa4ee0b850",
        "incomplete": "e6405c6c61f64c5b89c11262ce9b9669",
        "impossible_before_routing_fix": "5ea414c5e4aa487f95045ae3f3d2010d",
        "impossible": "1f7d3a73d5924a09ba73925655dce389",
    }
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "local_read_only_no_model_calls",
        "tests": [
            {"scope": "integrated_before_final_routing_and_numeric_type_fixes",
             "passed": 178, "source": "pytest-output.txt"},
            {"scope": "routing_evidence_chain_finance_inspection_integration_followup",
             "passed": 63, "source": "pytest-followup.txt"},
            {"scope": "numeric_types_finance_service_followup",
             "passed": 101, "source": "finance_budget_pytest.txt"},
        ],
        "test_count_note": "Suites se recouvrant ; ne pas additionner les comptes.",
        "cases": {}, "model_calls_in_audit": 0,
    }
    request_ids = set()
    for name, ident in cases.items():
        snapshot = store.snapshot(ident)
        assert snapshot["status"] != "running"
        for piece in snapshot["artifacts"]:
            store._load_object(piece["hash"])
        for attempt in snapshot["attempts"]:
            store._load_object(attempt["input_hash"])
            if attempt["tool"] == "bedrock.converse":
                assert attempt["provider"] == "amazon-bedrock-runtime"
                assert attempt["account_id"] == "471112821226"
                assert attempt["status"] == "complete"
                request_ids.add(attempt["request_id"])
        for run in snapshot["runs"]:
            manifest = run["request"]["software_manifest"]
            bundle = store._load_object(manifest["source_bundle_object"])
            assert set(bundle["files"]) == set(manifest["files"])
            assert all(hashlib.sha256(content.encode()).hexdigest() == manifest["files"][path]
                       for path, content in bundle["files"].items())
        analysis = snapshot.get("current_analysis")
        view = snapshot.get("current_view")
        if analysis:
            available = {c["id"]: c for c in analysis["content"]["claims"]}
            for claim in view["content"]["claims"]:
                assert claim["text"] == available[claim["id"]]["text"]
                for ref in claim["result_refs"]:
                    pointer(analysis["content"], ref["pointer"])
        report["cases"][name] = {
            "id": ident, "revision": snapshot["revision"], "status": snapshot["status"],
            "artifacts_verified": len(snapshot["artifacts"]),
            "operation_inputs_verified": len(snapshot["attempts"]),
            "source_bundles_verified": len(snapshot["runs"]),
            "analysis_status": analysis["content"]["status"] if analysis else None,
            "view_available": bool(view),
        }
    report["unique_aws_requests_in_demonstration_dossiers"] = len(request_ids)
    report["aws_request_ids"] = sorted(request_ids)
    report["replays"] = {
        path.stem: {key: json.loads(path.read_text()).get(key)
                    for key in ("equivalent", "source_bundle_verified", "model_calls")}
        for path in (proofs / "replay").glob("*.json")
    }
    assert all(r["equivalent"] and r["source_bundle_verified"] for r in report["replays"].values())
    ui = json.loads((proofs / "ui_review.json").read_text())
    report["ui_report"] = "ui_review.json"
    report["ui_reviewed_source_matches_current"] = (
        ui["reviewed_ui_sha256"] ==
        hashlib.sha256((ROOT / "alphaforge_app/static/workbench.js").read_bytes()).hexdigest()
    )
    assert report["ui_reviewed_source_matches_current"]
    write(proofs / "verification.json", report)
    if args.backup:
        archive = ROOT / "artifacts/AlphaForge_Prompt5_etat_2026-11-15.tar.gz"
        if archive.exists():
            raise FileExistsError("Archive déjà présente ; aucune sauvegarde écrasée.")
        with tempfile.TemporaryDirectory(prefix="alphaforge-p5-backup-") as directory:
            destination = Path(directory) / "decision"
            shutil.copytree(state, destination, ignore=shutil.ignore_patterns(
                "*.sqlite3", "*-wal", "*-shm", "*.lock"))
            db_checks = {}
            for name in ("dossiers.sqlite3", "checkpoints.sqlite3"):
                with sqlite3.connect(state / name) as source, sqlite3.connect(destination / name) as target:
                    source.backup(target)
                    db_checks[name] = target.execute("PRAGMA integrity_check").fetchone()[0]
                    assert db_checks[name] == "ok"
            restored = Store(destination)
            assert all(restored.snapshot(ident)["revision"] == report["cases"][name]["revision"]
                       for name, ident in cases.items())
            objects = list((destination / "objects").glob("*.json"))
            for path in objects:
                assert hashlib.sha256(path.read_bytes()).hexdigest() == path.stem
            archive.parent.mkdir(exist_ok=True)
            with tarfile.open(archive, "w:gz") as tar:
                tar.add(destination, arcname="decision")
            backup = {
                "archive": str(archive.relative_to(ROOT)),
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "bytes": archive.stat().st_size, "sqlite": db_checks,
                "objects_verified": len(objects), "restored_case_ids": list(cases.values()),
                "scope": "État du service principal ; conserver projet, données et corpus séparément.",
                "no_inference": True,
            }
            write(proofs / "state_backup.json", backup)
    print(json.dumps({"cases": report["cases"],
                      "unique_aws_requests": len(request_ids)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
