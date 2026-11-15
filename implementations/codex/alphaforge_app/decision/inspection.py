"""Read actual tool/data capabilities; no model and no financial forecast."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from ..datasets import load_dataset


def inspect_inputs(problem: dict) -> dict:
    project = Path(__file__).resolve().parents[2]
    dataset = load_dataset()
    tickers = {x["ticker"].strip().upper() for x in problem.get("holdings", [])}
    if problem.get("comparison"):
        tickers.add(problem["comparison"]["ticker"].strip().upper())
    missing = sorted(tickers - dataset.assets.keys())
    manifest = {
        "assets": [dataset.assets[t] for t in sorted(tickers - set(missing))],
        "missing_tickers": missing,
        "series": {t: {"observations": len(dataset.prices[t]), "start": min(dataset.prices[t]),
                       "end": max(dataset.prices[t])} for t in sorted(tickers - set(missing))},
        "fx": {"series": "CAD per USD", "observations": len(dataset.fx), "start": min(dataset.fx), "end": max(dataset.fx)},
        "files": dataset.files, "sources": dataset.sources,
        "calendar": {"start": dataset.calendar[0], "end": dataset.calendar[-1], "count": len(dataset.calendar)},
        "requested_knowledge_date": problem.get("knowledge_date"),
        "validation": "Fichiers effectivement ouverts ; schémas, valeurs positives, dates et devises validés par load_dataset.",
        "limits": ["Ce catalogue ne prouve ni la qualité économique de chaque cours ni un univers point-in-time.",
                   "L'Agent2 vérifiera les dates d'acquisition, la grille admissible et le change lors du calcul."],
    }
    evidence = []
    for relative in ("docs/methodology.md", "docs/implementation/methodes_runtime.md"):
        p = project / relative
        data = p.read_bytes()
        text = data.decode()
        h = hashlib.sha256(data).hexdigest()
        # Full short methodology; bounded extract of the longer finance note.
        excerpt = text[:12000]
        evidence.append({
            "id": "implementation-" + h[:12], "version": h,
            "source": {"title": relative, "url": relative, "kind": "technical_documentation",
                       "authority": "Projet AlphaForge ; méthode qualifiée par tests, pas publication empirique"},
            "known_at": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(),
            "reading_level": "full_text" if len(text) <= 12000 else "targeted_passages",
            "passage": excerpt, "passages": [{"text": excerpt, "line_start": 1, "line_end": len(excerpt.splitlines()),
                                             "text_truncated": len(text) > 12000}],
            "capture": {"path": relative, "sha256": h},
            "scope": "Contrat actuel de l'outil ; ne prouve pas qu'il existait historiquement.",
            "limitations": manifest["limits"],
        })
    return {
        "data_manifest": manifest, "evidence": evidence,
        "methods": [{
            "id": "retrospective-comparison-v2", "admitted": True,
            "implementation": "alphaforge_app.decision.finance.analyze",
            "domain": "Description achat-conservation sur le snapshot disponible ; aucune optimisation/prévision.",
            "assumptions": ["Politique historique explicitement déclarée : poids initiaux et redistribution proportionnelle des autres positions.",
                            "Prix ajustés utilisés une fois, distributions réinvesties dans chaque actif.",
                            "Valorisation CAD, change as-of contrôlé ; fractions de titres.",
                            "Frais et fiscalité non modélisés ; toute la grille commune admissible."],
            "source_ids": [e["id"] for e in evidence],
        }],
        "gaps": [{"code": "missing_asset", "message": "Actifs absents : " + ", ".join(missing)}] if missing else [],
        "contradictions": [], "limitations": manifest["limits"],
        "receipts": [{"tool_id": "load_dataset", "status": "success", "files": dataset.files}],
    }


def verify_calculation_inputs(inspection: dict, result: dict) -> dict:
    """Check the actual bytes and acquisition dates used by the calculator."""
    manifest = inspection["data_manifest"]
    provenance = result["provenance"]
    calculated = {row["file"]: {"sha256": row["sha256"], "rows": row["rows"]}
                  for row in provenance["data"]}
    dates = provenance["availability"]
    retrieved = {name: max(row["retrieved_on"] for row in manifest["sources"] if row["file"] == name)
                 for name in dates["snapshot_retrieved_on"]}
    if (manifest["files"] != calculated
            or manifest["requested_knowledge_date"] != dates["knowledge_date"]
            or retrieved != dates["snapshot_retrieved_on"]):
        raise ValueError("Le calcul et l'inspection n'utilisent pas les mêmes fichiers ou dates de connaissance.")
    return {
        "id": "inspected_data_matches_calculation", "status": "sufficient",
        "method": "Égalité des empreintes, nombres de lignes, dates d'acquisition et date de connaissance.",
        "scope": "Version exacte des données entre Agent1 et Agent2 ; pas certification de la qualité des cours.",
    }
