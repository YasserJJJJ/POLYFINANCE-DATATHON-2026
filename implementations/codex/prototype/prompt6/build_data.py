"""Build a read-only, traceable projection of the executed Prompt 5 dossiers.

No inference, no database connection and no financial recalculation.
Run from any directory with the project's Python.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXPORTS = ROOT / "docs/defense/proofs/demo"

CASES = [
    ("robert", "Robert", "Préparer un retrait, préserver les choix", [
        ("extracted-initial", "Retrait initial", "30 000 CAD à douze mois"),
        ("withdrawal_revision", "Retrait corrigé", "Le retrait passe à 40 000 CAD"),
        ("profile_revision", "Contrainte de perte révisée", "Le budget de perte passe à 1 000 CAD"),
    ]),
    ("amira", "Amira", "Comprendre une concentration", [
        ("amira-initial", "Comparaison historique", "TSLA : 25 % ou 10 % au départ"),
    ]),
    ("incomplet", "Une demande à préciser", "Un besoin exprimé, des informations manquantes", [
        ("incomplete-initial", "En attente de précisions", "Retrait à douze mois, montant inconnu"),
    ]),
    ("impossible", "Un retrait impossible", "Comprendre le conflit sans inventer une solution", [
        ("impossible-after", "Diagnostic budgétaire", "120 000 CAD demandés pour 100 000 CAD de capital"),
    ]),
]

ROLES = [
    ("agent0", "Qualifier", "Formalise la question et l'origine des informations."),
    ("agent1", "Étayer", "Examine les sources, les méthodes et leurs limites."),
    ("agent2", "Calculer", "Exécute et contrôle les calculs sur les entrées admises."),
    ("agent3", "Expliquer", "Organise les affirmations permises par le dossier."),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pointer(obj: Any, value: str) -> Any:
    for part in value.lstrip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    return obj


def stats(analysis: dict | None) -> dict:
    """Convenience values; all pointers address the unmodified analysis below."""
    if not analysis:
        return {}
    result: dict[str, Any] = {"bindings": {}}
    for index, option in enumerate(analysis.get("options", [])):
        metrics = option.get("metrics", {})
        if option["id"] == "minimum_turnover":
            for key, target in [("turnover_cad", "min_reallocation_cad"), ("reserve_cad", "reserve_cad")]:
                result[target] = metrics[key]["value"]
                result["bindings"][target] = f"/options/{index}/metrics/{key}/value"
            result["losses_cad"] = {s["id"]: s["loss_cad"] for s in option.get("scenario_results", [])}
            result["bindings"]["losses_cad"] = f"/options/{index}/scenario_results"
        if option["id"] in {"baseline", "target_variant"} and "total_return_pct" in metrics:
            result[option["id"]] = {k: v["value"] for k, v in metrics.items()}
            result["bindings"][option["id"]] = f"/options/{index}/metrics"
    for i, check in enumerate(analysis.get("checks", [])):
        if "shortfall_cad" in check:
            result["shortfall_cad"] = check["shortfall_cad"]
            result["bindings"]["shortfall_cad"] = f"/checks/{i}/shortfall_cad"
    return result


def project_version(filename: str, label: str, subtitle: str) -> dict:
    path = EXPORTS / f"{filename}.json"
    raw = json.loads(path.read_text())
    artifact = raw.get("current_analysis")
    analysis = artifact["content"] if artifact else None
    view = (raw.get("current_view") or {}).get("content", {})
    source = {
        "dossier_id": raw["id"], "dossier_revision": raw["revision"],
        "export": str(path.relative_to(ROOT)), "export_sha256": sha(path),
        "analysis_ref": f"analysis@{artifact['version']}" if artifact else None,
        "analysis_sha256": artifact["hash"] if artifact else None,
        "run_id": raw["active_run_id"], "recorded_at": raw["updated_at"],
        "product_url": f"http://127.0.0.1:8768/?dossier={raw['id']}",
        "scope": "Instantané exécuté, conservé en lecture seule ; ce n'est pas un nouveau run.",
    }
    facts = {}
    for item in raw["artifacts"]:
        if item["id"].startswith("fact."):
            field = item["id"][5:]
            if field not in facts or item["version"] > facts[field]["version"]:
                facts[field] = {
                    **item["content"], "artifact_ref": f"{item['id']}@{item['version']}",
                    "version": item["version"], "sha256": item["hash"],
                }
    # Absence is made explicit; no default financial value is introduced.
    for field, value in raw["active_problem"].items():
        facts.setdefault(field, {
            "field": field, "value": value, "origin": "unknown" if value is None else "not_recorded",
            "source_ref": None, "artifact_ref": None, "version": 0,
        })
    proofs = []
    for claim in (analysis or {}).get("claims", []):
        bindings = []
        for binding in claim.get("result_refs", []):
            bindings.append({**binding, "value": pointer(analysis, binding["pointer"])})
        proofs.append({
            "id": claim["id"], "kind": "calculation", "title": claim["text"],
            "claim_kind": claim["kind"], "scope": claim.get("scope"),
            "bindings": bindings, "artifact_ref": source["analysis_ref"],
            "artifact_sha256": source["analysis_sha256"],
            "method": (analysis or {}).get("method", {}),
            "checks": (analysis or {}).get("checks", []),
        })
    for evidence in view.get("inspected_evidence", raw.get("evidence", [])):
        src = evidence.get("source", {})
        proofs.append({
            "id": evidence["id"], "kind": "document",
            "title": src.get("title", evidence["id"]), "url": src.get("url"),
            "source_kind": src.get("kind"), "reading_level": evidence.get("reading_level"),
            "passage": evidence.get("passage"), "passages": evidence.get("passages", []),
            "scope": evidence.get("scope"), "limitations": evidence.get("limitations", []),
            "selected_by_agent1": evidence.get("selected_by_agent1", False),
            "selection_status": evidence.get("selection_status", "not_selected_or_not_recorded"),
            "entailment_status": evidence.get("entailment_status", "not_independently_verified_per_claim"),
            "known_at": evidence.get("known_at"), "version": evidence.get("version"),
            "capture": evidence.get("capture"),
        })
    agents = []
    for role, name, mission in ROLES:
        tasks = [t for t in raw["tasks"] if t["run_id"] == raw["active_run_id"] and t["role"] == role]
        attempts = [
            a for a in raw["attempts"]
            if a["role"] == role and a["task_id"].startswith(raw["active_run_id"])
        ]
        agents.append({
            "id": role, "name": name, "mission": mission,
            "status": tasks[-1]["status"] if tasks else "not_executed",
            "tasks": tasks,
            "attempts": [{
                "id": a["id"], "tool": a["tool"], "status": a["status"],
                "input_hash": a.get("input_hash"), "started_at": a.get("started_at"),
                "finished_at": a.get("finished_at"), "request_id": a.get("request_id"),
                "provider": (a.get("detail") or {}).get("provider", a.get("provider")),
                "model": (a.get("detail") or {}).get("model", a.get("model")),
                "region": (a.get("detail") or {}).get("region", a.get("region")),
                "usage": a.get("usage"), "parsed": (a.get("detail") or {}).get("parsed"),
            } for a in attempts],
            "output_refs": list(dict.fromkeys(r for t in tasks for r in t.get("output_refs", []))),
        })
    questions = []
    seen = set()
    for q in (raw.get("pending_clarifications") or {}).get("questions", []):
        key = (q.get("field"), q.get("question"))
        if key not in seen:
            seen.add(key)
            questions.append(q)
    comparison = raw.get("comparison") or {}
    current_request = next((e["payload"].get("prompt") for e in raw["events"] if e["kind"] == "request_received"), None)
    return {
        "id": f"r{raw['revision']}", "revision": raw["revision"], "label": label, "subtitle": subtitle,
        "status": raw["status"], "analysis_status": (analysis or {}).get("status", "not_calculated"),
        "source": source, "problem": raw["active_problem"], "request": current_request,
        "facts": facts, "analysis": analysis, "stats": stats(analysis),
        "claims": (analysis or {}).get("claims", []),
        "limits": view.get("calculation_limitations", (analysis or {}).get("limitations", [])),
        "documentary_limits": view.get("documentary_limitations", []),
        "documentary_issues": view.get("documentary_issues", []),
        "documentary_contradictions": view.get("documentary_contradictions", []),
        "controls": view.get("controls", {}), "proofs": proofs, "agents": agents,
        "questions": questions, "question_graph": raw.get("questions", []),
        "events": [{k: e[k] for k in ["id", "kind", "actor", "revision", "payload", "created_at"]} for e in raw["events"]],
        "changes": {k: comparison.get(k, []) for k in ["changed_fields", "invalidated", "reused"]},
        "changes_kind": "recorded_events" if comparison else "initial_version",
        "simple_reference": None,
    }


def build() -> dict:
    cases = []
    manifest = []
    for ident, name, subtitle, versions in CASES:
        projected = [project_version(*v) for v in versions]
        if ident == "robert":
            refpath = ROOT / "docs/defense/proofs/finance_review.json"
            reference = json.loads(refpath.read_text())["simple_reserve_reference"]
            projected[0]["simple_reference"] = {
                **reference,
                "id": "simple_reference",
                "label": "Règle simple examinée indépendamment",
                "scope": "Robert r5 uniquement : mêmes positions initiales, retrait de 30 000 CAD, plafond TSLA 10 %, budget de perte 15 000 CAD et chocs déclarés.",
                "source": str(refpath.relative_to(ROOT)),
                "source_sha256": sha(refpath), "pointer": "/simple_reserve_reference",
                "conclusion": "Cette règle atteint elle aussi le minimum de 30 000 CAD. Le LP ne prouve aucune supériorité de la couche agentique.",
                "not_an_agent_output": True,
            }
        for version in projected:
            version["source"]["download_url"] = f"/api/prototype/source/{ident}/{version['id']}"
            manifest.append(version["source"])
        cases.append({
            "id": ident, "name": name, "subtitle": subtitle,
            "version_count": len(projected), "status": projected[-1]["status"],
            "default_version_id": projected[0]["id"], "versions": projected,
        })
    data = {
        "schema_version": "prototype-projection-v1",
        "mode": "read_only_archived_dossiers",
        "inference_calls": 0,
        "notice": "Prototype de présentation. Archives exécutées P5 ; explorations locales séparées du dossier produit.",
        "cases": cases,
    }
    (HERE / "data").mkdir(parents=True, exist_ok=True)
    for filename, value in [("cases.json", data), ("manifest.json", manifest)]:
        (HERE / "data" / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    return data


if __name__ == "__main__":
    data = build()
    print(json.dumps({"cases": len(data["cases"]), "versions": sum(c["version_count"] for c in data["cases"]), "output": str(HERE / "data/cases.json")}))
