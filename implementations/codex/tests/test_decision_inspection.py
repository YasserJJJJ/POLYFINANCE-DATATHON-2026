"""Real inventory and provenance consistency, with no network/model calls."""
import copy
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest

from alphaforge_app.datasets import resolve_data_directory
from alphaforge_app.decision.finance import analyze, examples
from alphaforge_app.decision.inspection import inspect_inputs, verify_calculation_inputs


@pytest.fixture(scope="module")
def inspected_history():
    problem = copy.deepcopy(next(e["facts"] for e in examples() if e["id"] == "amira"))
    inspection = inspect_inputs(problem)
    result = analyze(problem)
    assert result["status"] == "conditional"
    return problem, inspection, result


def test_real_inventory_dates_captures_and_historical_provenance(inspected_history):
    problem, inspection, result = inspected_history
    manifest = inspection["data_manifest"]
    directory = resolve_data_directory()
    requested = {h["ticker"] for h in problem["holdings"]} | {problem["comparison"]["ticker"]}
    assert {a["ticker"] for a in manifest["assets"]} == requested
    assert manifest["missing_tickers"] == []
    csv_rows = {}
    for name, recorded in manifest["files"].items():
        path = directory / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == recorded["sha256"]
        with path.open(encoding="utf-8-sig", newline="") as handle:
            csv_rows[name] = list(csv.DictReader(handle))
        assert len(csv_rows[name]) == recorded["rows"]
    for ticker in requested:
        dates = [r["date"] for r in csv_rows["prices_daily.csv"] if r["ticker"] == ticker]
        assert manifest["series"][ticker] == {
            "observations": len(dates), "start": min(dates), "end": max(dates)}
    fx_dates = [r["date"] for r in csv_rows["fx_usdcad_daily.csv"]]
    assert manifest["fx"]["observations"] == len(fx_dates)
    assert manifest["fx"]["start"] == min(fx_dates)
    assert manifest["fx"]["end"] == max(fx_dates)
    assert manifest["requested_knowledge_date"] == result["provenance"]["availability"]["knowledge_date"]
    # This example authorizes the whole admissible snapshot; both calculations
    # use exactly the same common sessions, not a ticker-specific subperiod.
    assert manifest["calendar"] == {
        "start": result["method"]["metadata"]["start"],
        "end": result["method"]["metadata"]["end"],
        "count": result["method"]["metadata"]["observations"],
    }
    calculated_files = {row["file"]: {"sha256": row["sha256"], "rows": row["rows"]}
                        for row in result["provenance"]["data"]}
    assert manifest["files"] == calculated_files
    check = verify_calculation_inputs(inspection, result)
    assert check["id"] == "inspected_data_matches_calculation"
    assert check["status"] == "sufficient"
    assert "pas certification" in check["scope"]
    root = Path(__file__).resolve().parents[1]
    for evidence in inspection["evidence"]:
        path = root / evidence["capture"]["path"]
        raw = path.read_bytes()
        text = raw.decode()
        assert evidence["version"] == evidence["capture"]["sha256"] == hashlib.sha256(raw).hexdigest()
        assert evidence["passage"] == text[:12000]
        assert evidence["passages"][0]["text_truncated"] is (len(text) > 12000)
        assert evidence["reading_level"] == ("targeted_passages" if len(text) > 12000 else "full_text")
        # This is the documented filesystem version date, not proof of first
        # public availability or of a historical publication timestamp.
        assert datetime.fromisoformat(evidence["known_at"]) == datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)


@pytest.mark.parametrize("mutation", ["hash", "rows", "knowledge_date", "acquisition_date", "missing_file"])
def test_cross_agent_provenance_check_rejects_divergence(inspected_history, mutation):
    _, inspection, result = inspected_history
    changed = copy.deepcopy(result)
    prices = next(r for r in changed["provenance"]["data"] if r["file"] == "prices_daily.csv")
    if mutation == "hash":
        prices["sha256"] = "0" * 64
    elif mutation == "rows":
        prices["rows"] += 1
    elif mutation == "knowledge_date":
        changed["provenance"]["availability"]["knowledge_date"] = "2026-11-14"
    elif mutation == "acquisition_date":
        changed["provenance"]["availability"]["snapshot_retrieved_on"]["prices_daily.csv"] = "2026-11-12"
    else:
        changed["provenance"]["data"] = [r for r in changed["provenance"]["data"] if r["file"] != "prices_daily.csv"]
    with pytest.raises(ValueError, match="mêmes fichiers ou dates"):
        verify_calculation_inputs(inspection, changed)


def test_inspection_normalizes_tickers_like_finance(inspected_history):
    problem, initial_inspection, _ = inspected_history
    modified = copy.deepcopy(problem)
    for holding in modified["holdings"]:
        holding["ticker"] = " " + holding["ticker"].lower() + " "
    modified["comparison"]["ticker"] = " tsla "
    inspection = inspect_inputs(modified)
    assert inspection["data_manifest"]["assets"] == initial_inspection["data_manifest"]["assets"]
    assert inspection["data_manifest"]["series"] == initial_inspection["data_manifest"]["series"]
    assert inspection["data_manifest"]["missing_tickers"] == []
    assert inspection["gaps"] == []


def test_inventory_does_not_establish_historical_availability(inspected_history):
    problem, _, _ = inspected_history
    modified = copy.deepcopy(problem)
    modified["knowledge_date"] = "2020-01-01"
    inspection = inspect_inputs(modified)
    assert inspection["data_manifest"]["files"]
    assert inspection["data_manifest"]["requested_knowledge_date"] == "2020-01-01"
    assert inspection["receipts"][0]["status"] == "success"
    calculation = analyze(modified)
    assert calculation["status"] == "missing_input"
    assert calculation["missing"][0]["field"] == "knowledge_date"
    assert calculation["options"] == []
    assert calculation["claims"] == []
