"""P5 independent documentary audit; --live explicitly uses the AWS client.

The two counter-documents are labelled synthetic test fixtures throughout.
They are passed through the production retriever, not appended as model output.
No expected contradiction judgment is supplied to the live model.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from alphaforge_app.decision import research
from alphaforge_app.decision.finance import analyze, examples
from alphaforge_app.decision.service import DecisionService, pointer
from test_p5_evidence_review import create_corpus

OUT = Path(__file__).resolve().parent


def save(name, payload):
    path = OUT / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return path


def independent_historical_endpoint_check(dossier):
    """Direct CSV arithmetic, independent of analytics/analyze implementation.

    This validates the saved adjusted-price convention mathematically. It does
    not certify whether the provider actually included every distribution.
    """
    from alphaforge_app.datasets import resolve_data_directory

    directory = resolve_data_directory()
    with (directory / "prices_daily.csv").open() as handle:
        prices = {(r["date"], r["ticker"]): r for r in csv.DictReader(handle)}
    with (directory / "fx_usdcad_daily.csv").open() as handle:
        fx = {r["date"]: float(r["usdcad"]) for r in csv.DictReader(handle)}
    result = dossier["current_analysis"]["content"]
    start, end = result["method"]["metadata"]["start"], result["method"]["metadata"]["end"]

    def cad_price(day, ticker):
        row = prices[day, ticker]
        rate = fx[max(d for d in fx if d <= day)] if row["currency"] == "USD" else 1
        return float(row["adj_close"]) * rate

    capital = dossier["active_problem"]["capital_cad"]
    checks = []
    for option in result["options"]:
        independently_calculated = capital * sum(
            weight * cad_price(end, ticker) / cad_price(start, ticker)
            for ticker, weight in option["weights"].items()
        )
        recorded = option["metrics"]["ending_value_cad"]["value"]
        checks.append({
            "option": option["id"], "independent_ending_cad": independently_calculated,
            "recorded_ending_cad": recorded, "absolute_error_cad": abs(independently_calculated - recorded),
            "independent_return_pct": (independently_calculated / capital - 1) * 100,
        })
    return {
        "method": "V0 × sum(initial_weight × endpoint_CAD_adjusted_price / initial_CAD_adjusted_price)",
        "data_directory": str(directory), "start": start, "end": end, "checks": checks,
        "scope": "Saved adjusted-price convention only; no proof of provider data economics or future performance.",
    }


def audit_saved_demonstrations():
    reports = {}
    for name in ("robert-initial", "robert-revised", "amira-initial"):
        path = ROOT / "docs/implementation/proofs/final_demo" / f"{name}.json"
        dossier = json.loads(path.read_text())
        result = dossier["current_analysis"]["content"]
        view = dossier["current_view"]["content"]
        review = max(
            (a for a in dossier["artifacts"] if a["id"] == "research_review"),
            key=lambda a: a["version"],
        )["content"]
        evidence = view["citations"]
        capture_checks = []
        for e in evidence:
            capture = e.get("capture", {})
            source_path = ROOT / capture["path"]
            raw_ok = source_path.exists() and hashlib.sha256(source_path.read_bytes()).hexdigest() == capture["sha256"]
            text_path = ROOT / capture["text_path"] if capture.get("text_path") else None
            text_ok = (
                hashlib.sha256(text_path.read_bytes()).hexdigest() == capture["text_sha256"]
                if text_path and text_path.exists() else None
            )
            passage_checks = []
            if text_path and text_path.exists():
                lines = text_path.read_text().splitlines()
                for p in e.get("passages", []):
                    contained = "\n".join(lines[p["line_start"] - 1:p["line_end"]]).strip()
                    passage_checks.append(contained.startswith(p["text"]))
            capture_checks.append({
                "id": e["id"], "source_url": e["source"].get("url"),
                "known_at": e.get("known_at"), "reading_level": e.get("reading_level"),
                "raw_capture_exists_and_hash_matches": raw_ok,
                "extracted_text_hash_matches": text_ok,
                "passages_match_declared_line_windows": passage_checks,
                "selected_by_agent1": e["id"] in review["evidence_ids"],
            })
        claim_checks = [{
            "id": claim["id"],
            "text_matches_calculation": claim["text"] == next(c["text"] for c in result["claims"] if c["id"] == claim["id"]),
            "pointers_resolve": [
                {"pointer": ref["pointer"], "value": pointer(result, ref["pointer"])}
                for ref in claim.get("result_refs", [])
            ],
        } for claim in view["claims"]]
        recomputed = analyze(copy.deepcopy(dossier["active_problem"]))
        reports[name] = {
            "path": str(path.relative_to(ROOT)),
            "saved_dossier_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "capture_checks": capture_checks, "claim_checks": claim_checks,
            "same_claim_text_from_direct_finance_without_agents": recomputed["claims"] == result["claims"],
            "citation_count": len(evidence),
            "agent1_selected_count": len(review["evidence_ids"]),
            "review_unresolved_verbatim_in_view_limits": [
                {"text": issue, "present": issue in view["limitations"]}
                for issue in review["unresolved"]
            ],
            "research_conflicts": [
                c for a in dossier["artifacts"] if a["id"] == "research"
                for c in a["content"].get("contradictions", [])
            ],
            "independent_historical_endpoints": (
                independent_historical_endpoint_check(dossier) if name == "amira-initial" else None
            ),
            "limitations_of_audit": [
                "No new inference; recomputation uses the current deterministic finance implementation.",
                "A changed local technical note may no longer hash to the historical evidence capture.",
                "Identical finance results do not measure decision quality, user understanding or retrieval recall.",
            ],
        }
    save("preuves_final_demo_audit.json", reports)
    return reports


def live_counterexample():
    corpus = OUT / "preuves_corpus"
    specs = create_corpus(corpus)
    retrievals = []

    def actual_retriever(problem, **kwargs):
        # The model receives only the true reader output, without a prewritten
        # contradiction or intended decision. Web is irrelevant to this fixture.
        with patch.object(research, "CORPUS_ROOT", corpus), \
             patch.object(research, "CAPTURE_ROOT", OUT / "preuves_captures"), \
             patch.object(research, "_catalog", lambda *_: specs):
            result = research.research(problem, query=kwargs.get("query"), allow_web=False)
            retrievals.append(copy.deepcopy(result))
            return result

    case = next(e for e in examples() if e["id"] == "amira")
    service = DecisionService(ROOT / "runtime/defense_preuves_counterexample", researcher=actual_retriever)
    try:
        dossier = service.create(case["prompt"], case["facts"], use_ai=True, background=False)
        save("preuves_live_counterexample.json", dossier)
        save("preuves_live_retrievals.json", retrievals)
        summary = {
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "fixture_warning": "Two synthetic contradictory documents; neither is real starter metadata.",
            "retriever": "alphaforge_app.decision.research.research",
            "retrieval_count": len(retrievals),
            "real_reader_receipts": [r for result in retrievals for r in result["receipts"]],
            "dossier_id": dossier["id"], "status": dossier["status"],
            "research_reviews": [
                a["content"] for a in dossier["artifacts"] if a["id"] == "research_review"
            ],
            "view": dossier.get("current_view", {}).get("content") if dossier.get("current_view") else None,
            "aws_calls": [
                {"tool": a.get("tool"), "role": a.get("role"), "status": a.get("status"),
                 "request_id": a.get("request_id"), "provider": a.get("provider"),
                 "model": a.get("model"), "region": a.get("region"),
                 "account_id": a.get("account_id"), "usage": a.get("usage"),
                 "latency_ms": a.get("latency_ms"), "error": a.get("error")}
                for a in dossier["attempts"] if a.get("tool") == "bedrock.converse"
            ],
            "runs": dossier["runs"],
        }
        save("preuves_live_counterexample_summary.json", summary)
        print(json.dumps({
            "status": dossier["status"], "dossier_id": dossier["id"],
            "research_review_count": len(summary["research_reviews"]),
            "retrieval_count": len(retrievals),
            "aws_call_count": len(summary["aws_calls"]),
            "view_status": summary["view"].get("status") if summary["view"] else None,
            "path": str(OUT / "preuves_live_counterexample.json"),
        }, ensure_ascii=False))
    finally:
        service.pool.shutdown(wait=True)
        service.workflow.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    report = audit_saved_demonstrations()
    print(json.dumps({
        name: {
            "raw_hash_failures": [r["id"] for r in r["capture_checks"] if not r["raw_capture_exists_and_hash_matches"]],
            "same_finance_claims": r["same_claim_text_from_direct_finance_without_agents"],
            "selected_vs_cited": [r["agent1_selected_count"], r["citation_count"]],
        } for name, r in report.items()
    }, ensure_ascii=False))
    if args.live:
        live_counterexample()
