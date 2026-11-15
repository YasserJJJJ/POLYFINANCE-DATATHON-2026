"""Independent arithmetic/provenance checks of the Folio review revisions.

No product financial module, model call, or network request is used.
"""
import datetime
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).parent


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def main():
    report = {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "revisions": []}
    for revision, withdrawal, loss_limit, minimum in (
        (10, 40000, 15000, 40000),
        (15, 1000, 15000, 15000),
        (20, 40000, 1000, 74400),
    ):
        # Raw HTTP capture: JS JSON parse/stringify would normalize 100000.0 to
        # 100000 and invalidate the store's type-sensitive canonical hashes.
        payload = json.loads((OUT / f"robert-r{revision}-source.json").read_text())
        snapshot, v = payload["snapshot"], payload["version"]
        p, analysis = v["problem"], v["analysis"]
        assert p["withdrawal_cad"] == withdrawal
        assert p["scenario_loss_limit_cad"] == loss_limit
        assert abs(v["stats"]["min_reallocation_cad"] - minimum) < 1e-6
        calls = [a for a in snapshot["attempts"]
                 if a["tool"] == "bedrock.converse" and a["task_id"].startswith(snapshot["active_run_id"])]
        assert len(calls) == 4
        assert {a["role"] for a in calls} == {"agent0", "agent1", "agent2", "agent3"}
        assert all(a["status"] == "complete" and a["request_id"] for a in calls)
        assert all(a["provider"] == "amazon-bedrock-runtime" for a in calls)
        assert all(a["model"] == "global.openai.gpt-6-astra" for a in calls)
        for artifact in snapshot["artifacts"]:
            assert digest(artifact["content"]) == artifact["hash"], artifact["ref"]
        inputs = analysis["method"]["inputs"]
        capital, w0 = inputs["capital_cad"], inputs["weights"]
        checked_options = []
        for option in analysis["options"]:
            w = option["weights"]
            assert abs(sum(w.values()) - 1) < 1e-8
            turnover = capital / 2 * sum(abs(w.get(a, 0) - w0.get(a, 0)) for a in set(w) | set(w0))
            losses = {s["id"]: -capital * sum(w[a] * s["returns"][a] for a in w)
                      for s in inputs["scenarios"]}
            assert abs(turnover - option["metrics"]["turnover_cad"]["value"]) < 1e-6
            for s in option["scenario_results"]:
                assert abs(losses[s["id"]] - s["loss_cad"]) < 1e-6
            if option["admissible"]:
                assert min(w.values()) >= -1e-8
                assert capital * w.get("RESERVE_ABSTRAITE", 0) + 1e-6 >= withdrawal
                assert max(losses.values()) <= loss_limit + 1e-6
                for asset, cap in p["max_asset_weights"].items():
                    assert w.get(asset, 0) <= cap + 1e-8
            checked_options.append({"id": option["id"], "turnover_cad": turnover,
                                    "losses_cad": losses, "admissible": option["admissible"]})
        changes = v["changes"]
        assert "research@1" in changes["reused"]
        assert "baseline_stress@1" in changes["reused"]
        assert any(x.startswith("analysis@") for x in changes["invalidated"])
        assert any(x.startswith("view@") for x in changes["invalidated"])
        assert v["simple_reference"] is None
        report["revisions"].append({
            "revision": revision, "withdrawal_cad": withdrawal, "loss_limit_cad": loss_limit,
            "minimum_cad": v["stats"]["min_reallocation_cad"],
            "audit_scenario_error": revision == 15,
            "error_scope": "Le relecteur a modifié le retrait au lieu de la perte admise ; corrigé en r20." if revision == 15 else None,
            "run_id": snapshot["active_run_id"], "aws_request_ids": [a["request_id"] for a in calls],
            "independent_arithmetic": checked_options, "changes": changes,
        })
    report["scope"] = (
        "Arithmétique et admissibilité recalculées indépendamment. "
        "Le minimum global de r20 dépend du certificat du solveur ; "
        "ce script ne constitue pas une seconde résolution indépendante du LP."
    )
    (OUT / "audit_revisions.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    manifest = json.loads((OUT / "live_cases.json").read_text())
    manifest["initial_studies_scope"] = "Les entrées cases.* décrivent les études initiales r5, conservées intactes dans les captures."
    manifest["revision_history"] = report["revisions"]
    manifest["current_robert"] = {"id": manifest["cases"]["robert"]["id"], "revision": 20,
                                "snapshot": "robert-r20-source.json", "withdrawal_cad": 40000,
                                "scenario_loss_limit_cad": 1000, "min_reallocation_cad": 74400}
    manifest["revision_verification"] = "audit_revisions.json"
    (OUT / "live_cases.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps([{k: r[k] for k in ("revision", "withdrawal_cad", "loss_limit_cad", "minimum_cad")}
                      for r in report["revisions"]], indent=2))


if __name__ == "__main__":
    main()
