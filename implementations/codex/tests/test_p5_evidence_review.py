"""Independent P5 evidence contracts.

The corpus is a deliberately contradictory test fixture, not a claim about the
real starter data. The production retriever reads, hashes and extracts it.
Model replies in these unit tests are explicit doubles; no inference is made.
"""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from alphaforge_app.decision import research as research_module
from alphaforge_app.decision.finance import examples
from alphaforge_app.decision.service import DecisionService


CONFLICT = (
    "P5-CONVENTION-CONFLICT: les deux documents de test attribuent des conventions "
    "incompatibles au même champ adj_close ; le traitement des distributions reste non résolu."
)


def create_corpus(root: Path):
    """Create local counter-evidence that the real retriever must actually read."""
    captures = root / "collecte"
    captures.mkdir(parents=True, exist_ok=True)
    texts = {
        "U901": (
            "Document de test P5, convention A. Dans cette fixture fictive, le champ "
            "adj_close du fichier prices_daily.csv inclut les distributions réinvesties "
            "et les fractionnements. Son ratio est donc un rendement total avec revenus. "
            "Cette déclaration n'est pas une donnée réelle du starter."
        ),
        "U902": (
            "Document de test P5, convention B contradictoire. Dans cette même fixture "
            "fictive, le même champ adj_close du fichier prices_daily.csv exclut les "
            "distributions et corrige seulement les fractionnements. Son ratio est donc "
            "un rendement de prix sans revenus. Ce document contredit explicitement la "
            "convention A, et ne doit pas être fusionné en une convention implicite. "
            "Cette déclaration n'est pas une donnée réelle du starter."
        ),
    }
    specs = []
    for ident, text in texts.items():
        raw = f"<html><title>Fixture P5 {ident}</title><main><p>{text}</p></main></html>".encode()
        (captures / f"{ident}.html").write_bytes(raw)
        meta = {
            "status": 200,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "retrieved_at": "2026-11-15T00:00:00+00:00",
            "local_raw": f"collecte/{ident}.html",
            "requested_url": f"https://example.org/p5-fixture/{ident}",
            "content_type": "text/html",
        }
        path = captures / f"{ident}.json"
        path.write_text(json.dumps(meta))
        specs.append({"id": ident, "metadata": path})
    return specs


@pytest.fixture
def captured_counterexample(tmp_path, monkeypatch):
    root = tmp_path
    corpus = root / "corpus"
    specs = create_corpus(corpus)
    monkeypatch.setattr(research_module, "ROOT", root)
    monkeypatch.setattr(research_module, "CORPUS_ROOT", corpus)
    monkeypatch.setattr(research_module, "CAPTURE_ROOT", root / "captures")
    monkeypatch.setattr(research_module, "_catalog", lambda *_: specs)
    return research_module.research(
        {"decision_type": "historical_comparison", "knowledge_date": "2026-11-15"},
        query="adj_close distributions reinvesties convention contradictoire",
        allow_web=False,
    )


class EvidenceReviewDouble:
    model = "global.openai.gpt-6-astra"

    def __init__(self, override=None):
        self.contexts = {}
        self.override = override

    def generate(self, messages, **kwargs):
        role = kwargs["schema_name"].split("_", 1)[0]
        context = json.loads(messages[-1]["content"])
        self.contexts[role] = context
        outputs = {
            "agent0": {"updates": [], "contradictions": [], "clarifications": [],
                       "interpretation": "Double P5 : entrées structurées conservées."},
            "agent1": {"evidence_ids": [], "method_ids": ["retrospective-comparison-v2"],
                       "unresolved": [CONFLICT], "decision": "calculate_conditionally",
                       "reason": "Double P5 : calcul descriptif conditionnel, conflit à restituer."},
            "agent2": {"tool": "historical_comparison", "question_addressed": "Fixture P5",
                       "checks_to_inspect": [], "sensitivity_fields": [],
                       "reason": "Double P5 : conserver le conflit de convention dans les limites."},
            "agent3": {"claim_order": [], "emphasis": "conditions", "detail_level": "detailed",
                       "follow_up_fields": [], "reason": "Double P5 : restitution conditionnelle."},
        }
        if role == "agent1":
            outputs[role]["evidence_ids"] = [
                e["id"] for e in context["documentary_results"]["evidence"]
                if e.get("source_id") in {"U901", "U902"}
            ]
        if self.override:
            self.override(role, outputs[role], context)
        return {"parsed": outputs[role], "request_id": f"p5-double-{role}",
                "provider": "test_double_no_inference", "model": self.model,
                "usage": {"total_tokens": 0}}


@pytest.fixture
def reviewed_counterexample(tmp_path, captured_counterexample):
    research_result = copy.deepcopy(captured_counterexample)
    research_result["contradictions"].append({
        "code": "p5_fixture_convention_conflict",
        "source_refs": [e["id"] for e in research_result["evidence"]],
        "message": CONFLICT, "status": "requires_review",
    })
    client = EvidenceReviewDouble()
    service = DecisionService(
        tmp_path / "dossiers", client=client,
        researcher=lambda *args, **kwargs: copy.deepcopy(research_result),
    )
    case = next(e for e in examples() if e["id"] == "amira")
    try:
        snapshot = service.create(case["prompt"], case["facts"], use_ai=True, background=False)
        yield snapshot, client
    finally:
        service.pool.shutdown(wait=True)
        service.workflow.close()


def test_counterevidence_was_retrieved_from_real_raw_captures(captured_counterexample):
    evidence = captured_counterexample["evidence"]
    assert {e["source_id"] for e in evidence} == {"U901", "U902"}
    assert "inclut les distributions" in evidence[0]["passage"]
    assert "exclut les distributions" in evidence[1]["passage"]
    assert all(e["review_status"] == "extracted_for_role_review" for e in evidence)
    receipts = [r for r in captured_counterexample["receipts"] if r["tool_id"] == "local_corpus_read"]
    assert len(receipts) == 2
    assert all(r["status"] == "success" for r in receipts)
    assert {r["capture_sha256"] for r in receipts} == {e["capture"]["sha256"] for e in evidence}


def test_material_research_disagreement_survives_to_current_view(reviewed_counterexample):
    snapshot, _ = reviewed_counterexample
    assert snapshot["status"] in {"complete", "waiting"}
    research_review = next(a for a in snapshot["artifacts"] if a["id"] == "research_review")
    assert CONFLICT in research_review["content"]["unresolved"]
    view = snapshot["current_view"]["content"]
    assert CONFLICT in json.dumps(view["limitations"], ensure_ascii=False)


def test_evidence_question_cannot_be_resolved_with_unreviewed_conflict(reviewed_counterexample):
    snapshot, _ = reviewed_counterexample
    piece = next(a for a in snapshot["artifacts"] if a["id"] == "questions.agent1")
    node = next(n for n in piece["content"]["nodes"] if n["id"] == "evidence")
    assert node["status"] != "resolved"


def test_agent3_receives_review_and_contradictions_it_must_present(reviewed_counterexample):
    _, client = reviewed_counterexample
    assert CONFLICT in json.dumps(client.contexts["agent3"], ensure_ascii=False)


def test_unannotated_retriever_conflict_blocks_numerical_claims(reviewed_counterexample):
    snapshot, _ = reviewed_counterexample
    review = next(a for a in snapshot["artifacts"] if a["id"] == "research_review")["content"]
    assert review["blocking_issues"][0]["origin"] == "retriever_conflict_not_disposed_by_review"
    assert not any(a["tool"] == "finance.analyze" for a in snapshot["attempts"])
    view = snapshot["current_view"]["content"]
    assert view["claims"] == []
    assert view["controls"]["documentary_grounding"]["status"] == "insufficient"


def test_inspected_but_unselected_sources_are_distinct_from_citations(reviewed_counterexample):
    snapshot, _ = reviewed_counterexample
    view = snapshot["current_view"]["content"]
    assert all(e["selected_by_agent1"] for e in view["citations"])
    assert len(view["inspected_evidence"]) > len(view["citations"])
    assert any(e["selection_status"] == "inspected_not_selected" for e in view["inspected_evidence"])
    assert all(e["entailment_status"] == "not_independently_verified_per_claim" for e in view["citations"])


def test_model_scope_judgment_cannot_clear_material_data_conflict(tmp_path, captured_counterexample):
    def attempt_resolution(role, response, context):
        if role != "agent1":
            return
        response["issues"] = [{
            "id": "material_data_conflict", "kind": "data_quality", "scope": "data",
            "severity": "blocking", "status": "resolved_in_scope",
            "message": CONFLICT,
            "evidence_ids": response["evidence_ids"],
            "resolution_basis": "Le modèle affirme seul avoir résolu la convention.",
        }]

    service = DecisionService(
        tmp_path / "invalid_resolution", client=EvidenceReviewDouble(attempt_resolution),
        researcher=lambda *args, **kwargs: copy.deepcopy(captured_counterexample),
    )
    case = next(e for e in examples() if e["id"] == "amira")
    try:
        snapshot = service.create(case["prompt"], case["facts"], background=False)
        review = next(a for a in snapshot["artifacts"] if a["id"] == "research_review")["content"]
        assert review["blocking_issues"][0]["status"] == "unresolved"
        assert review["blocking_issues"][0]["resolution_rejected"]
        assert not any(a["tool"] == "finance.analyze" for a in snapshot["attempts"])
    finally:
        service.pool.shutdown(wait=True)
        service.workflow.close()
