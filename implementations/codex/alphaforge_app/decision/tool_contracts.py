"""Fixed executable scope, distinct from bibliographic method candidates.

Hashes identify inspected code and qualification material. Their presence is
not a claim that all tests passed on this version or that a runtime result is
valid. The calculator and service must still enforce their runtime checks.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def executable_contracts() -> list[dict]:
    root = Path(__file__).resolve().parents[2]
    material = []
    for path, kind in (
        ("alphaforge_app/decision/finance.py", "executable_implementation"),
        ("docs/implementation/finance.md", "project_method_documentation"),
        ("tests/test_decision_finance.py", "qualification_test_source_not_execution_receipt"),
        ("tests/test_decision_inspection.py", "data_provenance_test_source_not_execution_receipt"),
    ):
        file = root / path
        material.append({
            "path": path, "kind": kind,
            "sha256": hashlib.sha256(file.read_bytes()).hexdigest() if file.exists() else None,
            "available": file.exists(),
        })
    shared = {
        "registry_status": "implemented_fixed_tool",
        "implementation": "alphaforge_app.decision.finance.analyze",
        "implementation_sha256": material[0]["sha256"],
        "qualification_material": material,
        "admission_basis": (
            "Outil fixe enregistré par le projet, avec implémentation, qualification "
            "reproductible disponible et invariants exigés à chaque exécution. "
            "Ce registre ne prétend pas qu'une suite a été exécutée pour ce hash. "
            "L'admission d'un outil local est distincte du statut candidat d'une "
            "méthode bibliographique et de la validité de son résultat courant."
        ),
        "runtime_result_gate": (
            "Domaine et entrées admissibles, contrôles d'exécution suffisants, "
            "aucun conflit documentaire bloquant non résolu."
        ),
    }
    return [
        {
            **shared,
            "id": "reserve-budget-contradiction-v1",
            "tool": "reserve_budget_diagnostic",
            "implementation": "alphaforge_app.decision.finance.analyze_budget_diagnostic",
            "domain": "Retrait supérieur au capital sous réserve abstraite nominale CAD, objectif de réallocation minimale.",
            "required_checks": ["reserve_budget_contradiction"],
            "runtime_result_gate": (
                "Diagnostic limité aux six paramètres déclarés ; preuve algébrique sans solveur, "
                "sans donnée de marché et sans allocation. Une lacune documentaire reste ouverte "
                "et interdit toujours les conclusions qui en dépendent."
            ),
            "limitations": [
                "Certificat conditionnel aux entrées déclarées, sans validation de leur réalité.",
                "Aucun IIS global, aucune contrainte relâchée, aucune allocation autorisée.",
            ],
        },
        {
            **shared,
            "id": "reserve-turnover-lp-v1",
            "tool": "reserve_allocation",
            "domain": "Minimum de capital réalloué, demi-L1, contraintes affines, scénarios et réserve abstraite explicites.",
            "required_checks": ["constraints", "independent_lower_bound", "multiple_optima"],
            "limitations": [
                "La borne indépendante peut être partielle ; optimalité numérique soumise aux contrôles primal-dual.",
                "Aucun instrument réel garanti, probabilité de scénario, coût ou horizon dynamique n'est qualifié.",
            ],
        },
        {
            **shared,
            "id": "retrospective-comparison-v2",
            "tool": "historical_comparison",
            "domain": "Comparaison descriptive achat-conservation sur le snapshot admissible, valorisation CAD.",
            "required_checks": ["historical_policy", "snapshot_availability", "calendar_fx", "adjustments"],
            "limitations": [
                "Pas de prévision, d'univers point-in-time, ni de convenance personnelle certifiée.",
                "Le traitement des ajustements reste limité aux garanties effectivement établies par les données et les contrôles.",
            ],
        },
    ]
