"""Read-only Folio projections of the authoritative dossier.

An archive replays committed invalidations and writes. It never borrows current
heads, future agent results or the current run's status. Projection does not call
a model, a solver, or a document retrieval service.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from .models import ProblemSpec
from .service import BASELINE_FIELDS, RESEARCH_FIELDS, ROLE_NAMES, pointer
from .store import Missing, canonical, digest

ROOT = Path(__file__).resolve().parents[2]
SHORT_NAMES = {"agent0": "Qualifier", "agent1": "Étayer", "agent2": "Calculer", "agent3": "Expliquer"}
MISSIONS = {
    "agent0": "Formalise la question et l’origine des informations.",
    "agent1": "Examine les sources, les méthodes et leurs limites.",
    "agent2": "Exécute et contrôle les calculs sur les entrées admises.",
    "agent3": "Organise les affirmations permises par le dossier.",
}


def _heads(snapshot):
    return {a["id"]: a for a in snapshot["artifacts"] if a["usable"]}


def _comparison(snapshot, heads):
    revision = next((r for r in reversed(snapshot["revisions"]) if r["kind"] == "revision_requested"), None)
    if not revision:
        return None
    payload = revision["payload"]
    before_refs = set(payload.get("invalidated", [])) | set(payload.get("reused", []))
    usable_refs = {a["ref"] for a in heads.values()}
    old_inputs = (payload.get("before") or {}).get("inputs", {})
    current = heads.get("problem", {}).get("content")
    interpreted = {"fact." + k for k, value in (current or {}).items()
                   if k in old_inputs and old_inputs[k] != value}
    return {
        "before": payload.get("before"), "after": heads.get("analysis", {}).get("content"),
        "changed_fields": sorted(set(payload.get("changed_fields", [])) | interpreted),
        "invalidated": sorted(before_refs - usable_refs), "reused": sorted(before_refs & usable_refs),
        "provisional": current is None,
    }


def at_revision(snapshot, revision=None):
    """Return the live snapshot or the state just after a financial commit.

    Historical agent activity includes only tasks committed by this revision.
    An in-flight or later failed task is not retroactively shown as completed.
    """
    if revision is None:
        return copy.deepcopy(snapshot)
    records = {r["revision"]: r for r in snapshot["revisions"]}
    if revision not in records:
        raise Missing(f"revision:{revision}")
    selected = records[revision]
    result = copy.deepcopy(snapshot)
    result["revisions"] = [r for r in result["revisions"] if r["revision"] <= revision]
    result["artifacts"] = [a for a in result["artifacts"] if a["revision"] <= revision]
    by_revision = {}
    for artifact in result["artifacts"]:
        by_revision.setdefault(artifact["revision"], []).append(artifact)
        artifact["usable"] = False
    heads = {}
    for record in result["revisions"]:
        invalid = set(record["payload"].get("invalidated", []))
        for key, artifact in list(heads.items()):
            if artifact["ref"] in invalid:
                artifact["usable"] = False
                del heads[key]
        for artifact in by_revision.get(record["revision"], []):
            if artifact["id"] in heads:
                heads[artifact["id"]]["usable"] = False
            artifact["usable"] = True
            heads[artifact["id"]] = artifact

    commits = {r["payload"]["task_id"]: r for r in result["revisions"]
               if r["kind"] == "agent_commit" and r["payload"].get("task_id")}
    result["tasks"] = [t for t in result["tasks"] if t["id"] in commits]
    for task in result["tasks"]:
        task.update(status="complete", error=None, committed_revision=commits[task["id"]]["revision"])
    # The financial commit boundary includes writes and its task return.
    times = [selected["created_at"]]
    times += [a["created_at"] for a in result["artifacts"] if a["revision"] == revision]
    times += [t["finished_at"] for t in result["tasks"]
              if t["committed_revision"] == revision and t.get("finished_at")]
    request_refs = {a["ref"] for a in result["artifacts"] if a["id"] == "request"}
    runs_in_scope = [r for r in result["runs"] if r["request"].get("request_ref") in request_refs]
    selected_request_refs = {a["ref"] for a in result["artifacts"]
                             if a["id"] == "request" and a["revision"] == revision}
    times += [r["created_at"] for r in runs_in_scope
              if r["request"].get("request_ref") in selected_request_refs]
    cutoff = max(times)
    result["events"] = [e for e in result["events"]
                        if e["revision"] <= revision and e["created_at"] <= cutoff]
    task_ids = set(commits)
    result["attempts"] = [a for a in result["attempts"]
                          if a["task_id"] in task_ids and a.get("finished_at") and a["finished_at"] <= cutoff]
    result["runs"] = runs_in_scope
    request = heads.get("request", {}).get("content", {})
    request_ref = heads.get("request", {}).get("ref")
    active = next((r for r in reversed(result["runs"]) if r["request"].get("request_ref") == request_ref), None)
    if active is None and result["runs"]:
        active = result["runs"][-1]
    result["active_run_id"] = active["id"] if active else None
    for run in result["runs"]:
        tasks = [t for t in result["tasks"] if t["run_id"] == run["id"]]
        last = tasks[-1] if tasks else {}
        # Older snapshots may lack saved state metadata; a committed view ends
        # a normal run, while a following agent0 commit can put it in waiting.
        state = last.get("result_status")
        if state is None:
            commit = commits.get(last.get("id"), {}).get("payload", {})
            state = "complete" if "view" in commit.get("writes", []) else "running"
        if active and run["id"] != active["id"] and state in {"running", "waiting", "error"}:
            state = "superseded"
        run.update(status=state or "running", current_role=last.get("next_role"),
                   error=None, updated_at=last.get("finished_at") or run["created_at"])
    result.update(
        revision=revision, updated_at=cutoff,
        status=active["status"] if active else "running",
        active_problem=heads.get("problem", {}).get("content"),
        current_analysis=heads.get("analysis"), current_view=heads.get("view"),
        pending_clarifications={
            "qualification_ref": heads.get("qualification", {}).get("ref"),
            "questions": heads.get("qualification", {}).get("content", {}).get("clarifications", []),
        },
        questions=[n for key, a in heads.items() if key.startswith("questions.")
                   for n in a.get("content", {}).get("nodes", [])],
        evidence=list({canonical(e): e for a in heads.values() if a["type"] == "research"
                       for e in a["content"].get("evidence", [])}.values()),
        historical={"revision": revision, "as_of": cutoff,
                    "scope": "État après cette révision financière ; seules les tâches déjà commises sont incluses."},
    )
    result["comparison"] = _comparison(result, heads)
    result["route"]["verified_requests"] = [a["request_id"] for a in result["attempts"] if a.get("request_id")]
    return result


def archives(snapshot):
    names = {
        "request_received": "Demande reçue", "revision_requested": "Correction reçue",
        "agent_commit": "Contribution",
    }
    result = []
    for record in snapshot["revisions"]:
        state = at_revision(snapshot, record["revision"])
        result.append({
            "revision": record["revision"], "status": state["status"],
            "analysis_status": (state.get("current_analysis") or {}).get("content", {}).get("status"),
            "label": (ROLE_NAMES.get(record["actor"], names.get(record["kind"], record["kind"]))),
            "created_at": record["created_at"],
        })
    return result


def stats(analysis):
    result = {"bindings": {}}
    for i, option in enumerate((analysis or {}).get("options", [])):
        metrics = option.get("metrics", {})
        if option.get("id") == "minimum_turnover":
            for key, target in (("turnover_cad", "min_reallocation_cad"), ("reserve_cad", "reserve_cad")):
                if key in metrics:
                    result[target] = metrics[key]["value"]
                    result["bindings"][target] = f"/options/{i}/metrics/{key}/value"
            result["losses_cad"] = {s["id"]: s["loss_cad"] for s in option.get("scenario_results", [])}
            result["bindings"]["losses_cad"] = f"/options/{i}/scenario_results"
        if option.get("id") in {"baseline", "target_variant"} and "total_return_pct" in metrics:
            result[option["id"]] = {k: v["value"] for k, v in metrics.items()}
            result["bindings"][option["id"]] = f"/options/{i}/metrics"
    for i, check in enumerate((analysis or {}).get("checks", [])):
        if "shortfall_cad" in check:
            result["shortfall_cad"] = check["shortfall_cad"]
            result["bindings"]["shortfall_cad"] = f"/checks/{i}/shortfall_cad"
    return result


def calculation_proofs(analysis, source):
    proofs = []
    for claim in (analysis or {}).get("claims", []):
        bindings = []
        for binding in claim.get("result_refs", []):
            item = copy.deepcopy(binding)
            try:
                item["value"] = pointer(analysis, binding["pointer"])
                item["resolved"] = True
            except (KeyError, IndexError, TypeError, ValueError):
                item.update(value=None, resolved=False, error="Pointeur non résolu ; valeur non prouvée.")
            bindings.append(item)
        proofs.append({
            "id": claim["id"], "kind": "calculation", "title": claim["text"],
            "claim_kind": claim.get("kind"), "scope": claim.get("scope"),
            "bindings": bindings, "artifact_ref": source.get("analysis_ref"),
            "artifact_sha256": source.get("analysis_sha256"),
            "method": (analysis or {}).get("method", {}), "checks": (analysis or {}).get("checks", []),
        })
    return proofs


def _simple_reference(problem, analysis):
    """The P5 independent result is evidence only for its exact financial inputs."""
    if not analysis or analysis.get("status") not in {"conditional", "complete"}:
        return None
    export_path = ROOT / "docs/defense/proofs/demo/extracted-initial.json"
    proof_path = ROOT / "docs/defense/proofs/finance_review.json"
    if not export_path.is_file() or not proof_path.is_file():
        return None
    expected = json.loads(export_path.read_text())["active_problem"]
    # A reworded question is allowed; every parameter and epistemic condition
    # remains identical, including dates, assumptions and remaining unknowns.
    keys = set(ProblemSpec.model_fields) - {"question"}
    if any(problem.get(k) != expected.get(k) for k in keys):
        return None
    reference = json.loads(proof_path.read_text())["simple_reserve_reference"]
    if stats(analysis).get("min_reallocation_cad") != reference["independent"]["turnover_cad"]:
        return None
    return {
        **reference, "id": "simple_reference", "label": "Règle simple examinée indépendamment",
        "scope": "Entrées financières et hypothèses identiques au Robert r5 vérifié.",
        "source": str(proof_path.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(proof_path.read_bytes()).hexdigest(),
        "input_source": str(export_path.relative_to(ROOT)),
        "input_source_sha256": hashlib.sha256(export_path.read_bytes()).hexdigest(),
        "pointer": "/simple_reserve_reference",
        "conclusion": "Cette règle atteint elle aussi le minimum de 30 000 CAD. Le LP ne prouve aucune supériorité de la couche agentique.",
        "not_an_agent_output": True,
    }


def project(snapshot, *, historical=False):
    heads = _heads(snapshot)
    artifact = snapshot.get("current_analysis")
    analysis = artifact["content"] if artifact else None
    view = (snapshot.get("current_view") or {}).get("content", {})
    problem = snapshot.get("active_problem")
    qualified = problem is not None
    if problem is None:
        # Surface captured values while qualification is pending. Their original
        # fact origins remain visible; no ProblemSpec defaults become facts.
        problem = {a["content"]["field"]: a["content"]["value"]
                   for a in heads.values() if a["id"].startswith("fact.")}
    source = {
        "dossier_id": snapshot["id"], "dossier_revision": snapshot["revision"],
        "analysis_ref": artifact.get("ref") if artifact else None,
        "analysis_sha256": artifact.get("hash") if artifact else None,
        "run_id": snapshot.get("active_run_id"), "recorded_at": snapshot["updated_at"],
        "snapshot_sha256": digest(snapshot), "scope": "archive" if historical else "current_dossier",
        "export_sha256": digest(at_revision(snapshot, snapshot["revision"])),
        "export_scope": "Archive du commit financier sélectionné ; le suivi vivant postérieur est distinct.",
        "download_url": f"/api/folio/dossiers/{snapshot['id']}/export?revision={snapshot['revision']}",
    }
    facts = {
        a["id"][5:]: {**a["content"], "artifact_ref": a["ref"], "version": a["version"], "sha256": a["hash"]}
        for a in heads.values() if a["id"].startswith("fact.")
    }
    for field, value in problem.items():
        facts.setdefault(field, {"field": field, "value": value, "origin": "unknown" if value is None else "not_recorded",
                                 "source_ref": None, "artifact_ref": None, "version": 0})
    proofs = calculation_proofs(analysis, source)
    for evidence in view.get("inspected_evidence", snapshot.get("evidence", [])):
        src = evidence.get("source", {})
        owners = [a for a in heads.values() if a["type"] == "research" and
                  any(e.get("id") == evidence.get("id") for e in a["content"].get("evidence", []))]
        proofs.append({
            **copy.deepcopy(evidence), "id": evidence["id"], "kind": "document",
            "title": src.get("title", evidence["id"]), "url": src.get("url"), "source_kind": src.get("kind"),
            "artifact_refs": [a["ref"] for a in owners],
            "artifact_hashes": [a["hash"] for a in owners],
            "selected_by_agent1": evidence.get("selected_by_agent1", False),
            "entailment_status": evidence.get("entailment_status", "not_independently_verified_per_claim"),
        })
    agents = []
    for role, name in SHORT_NAMES.items():
        tasks = [t for t in snapshot["tasks"] if t["run_id"] == snapshot["active_run_id"] and t["role"] == role]
        task_ids = {t["id"] for t in tasks}
        attempts = [a for a in snapshot["attempts"] if a["task_id"] in task_ids]
        agents.append({
            "id": role, "name": name, "mission": MISSIONS[role],
            "status": tasks[-1]["status"] if tasks else "not_executed",
            "tasks": copy.deepcopy(tasks), "attempts": copy.deepcopy(attempts),
            "output_refs": list(dict.fromkeys(r for t in tasks for r in t.get("output_refs", []))),
        })
    questions = view.get("questions", []) + snapshot.get("pending_clarifications", {}).get("questions", [])
    questions = list({canonical(q): q for q in questions}.values())
    initial = next((e["payload"].get("prompt") for e in snapshot["events"] if e["kind"] == "request_received"), None)
    comparison = snapshot.get("comparison") or {}
    origin = snapshot.get("origin")
    if isinstance(origin, str):
        origin = json.loads(origin)
    return {
        "id": f"r{snapshot['revision']}", "revision": snapshot["revision"],
        "origin": origin,
        "label": snapshot["title"], "subtitle": "Dossier fictif et versionné",
        "status": snapshot["status"], "analysis_status": (analysis or {}).get("status", "not_calculated"),
        "source": source, "request": initial, "problem": problem, "facts": facts,
        "problem_qualified": qualified,
        "current_request": heads.get("request", {}).get("content", {}).get("prompt"),
        "analysis": analysis, "stats": stats(analysis), "claims": (analysis or {}).get("claims", []),
        "limits": view.get("calculation_limitations", (analysis or {}).get("limitations", [])),
        "documentary_limits": view.get("documentary_limitations", []),
        "documentary_issues": view.get("documentary_issues", []),
        "documentary_contradictions": view.get("documentary_contradictions", []),
        "controls": view.get("controls", {}), "proofs": proofs, "agents": agents,
        "questions": questions, "question_graph": snapshot.get("questions", []),
        "events": snapshot["events"],
        "changes": {k: comparison.get(k, []) for k in ("changed_fields", "invalidated", "reused")},
        "changes_kind": "recorded_events" if comparison else "initial_version",
        "simple_reference": _simple_reference(problem, analysis),
    }


def dependency_preview(snapshot, changes):
    """Hypothesis about a later revision, never a claim of cache reuse."""
    changed = set(changes)
    return {
        "kind": "dependency_preview_not_recorded_events",
        "label": "Dépendances prévues pour une future révision ; aucun agent exécuté dans cet aperçu.",
        "reusable": (["Diagnostic initial des pertes"] if not changed.intersection(BASELINE_FIELDS) else []),
        "to_review": ["Qualification du besoin", "Conclusion et restitution"] +
                     (["Dossier documentaire"] if changed.intersection(RESEARCH_FIELDS) else ["Applicabilité des preuves conservées"]),
        "recalculated": ["Résultats numériques applicables", "Contraintes et sensibilités"],
        "baseline_stress": "unchanged_inputs_reusable_in_future_revision" if not changed.intersection(BASELINE_FIELDS)
                           else "dependent_on_modified_inputs",
        "local_execution": "all_applicable_numeric_results_reexecuted_without_artifact_cache",
        "local_execution_notice": "Tous les calculs applicables de cet aperçu sont réexécutés. Le réemploi indiqué est une prévision pour une révision ultérieure.",
    }
