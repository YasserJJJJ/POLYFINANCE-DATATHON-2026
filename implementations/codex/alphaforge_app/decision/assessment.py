"""Deterministic assessment of calculator checks, independent of agent prose."""
from __future__ import annotations


def assess_checks(result: dict) -> dict:
    checks = result.get("checks", [])
    failures = [
        c.get("id", "unnamed")
        for c in checks
        if c.get("status") in {"insufficient", "error", "failed", "invalid", "missing"}
        or c.get("numerical_checks_pass") is False
    ]
    if result.get("status") in {"complete", "conditional"} and not checks:
        failures.append("missing_verification")
    if failures:
        return {"status": "insufficient", "failed_check_ids": failures}
    if not checks:
        return {"status": "not_established", "failed_check_ids": []}
    statuses = {c.get("status") for c in checks}
    if statuses == {"sufficient"}:
        status = "sufficient"
    elif statuses <= {"sufficient", "sufficient_with_reservation"}:
        status = "conditional"
    elif result.get("status") == "infeasible" and all(
        c.get("certified") is True or c.get("status") == "sufficient" for c in checks
    ):
        status = "sufficient"
    else:
        status = "partial"
    return {"status": status, "failed_check_ids": []}
