"""Folio API: durable commands, historical truth and isolated calculations.

No model or document network request is used. Real deterministic finance tools
run on declared fictitious inputs; the research callable is an explicit double.
"""
import copy
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from alphaforge_app.decision import api, folio_api
from alphaforge_app.decision.folio_projection import at_revision, project
from alphaforge_app.decision.service import DecisionService
from alphaforge_app.decision.store import Conflict, Store, digest


ROOT = Path(__file__).resolve().parents[1]
ROBERT = json.loads((ROOT / "docs/defense/proofs/demo/extracted-initial.json").read_text())["active_problem"]


def research_double(problem, **kwargs):
    return {"evidence": [], "methods": [], "gaps": ["Fixture : aucune recherche réseau."],
            "contradictions": [], "receipts": [], "limitations": []}


@pytest.fixture
def service(tmp_path):
    obj = DecisionService(tmp_path / "folio", researcher=research_double)
    yield obj
    obj.pool.shutdown(wait=True)
    obj.workflow.close()


@pytest.fixture
def client(service, monkeypatch):
    monkeypatch.setattr(api, "service", lambda: service)
    app = FastAPI()
    app.include_router(folio_api.router)
    with TestClient(app) as client:
        yield client


def make_robert(service):
    return service.create("Exemple fictif Robert.", copy.deepcopy(ROBERT), False,
                          background=False, request_id="seed")


def test_durable_creation_same_key_across_independent_store_connections(tmp_path):
    root = tmp_path / "atomic"
    stores = [Store(root), Store(root)]
    def create(index):
        return stores[index].create("Fictif", {"capital_cad": 100}, False, request_id="same-key")
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(create, (0, 1)))
    assert outcomes[0] == outcomes[1]
    reopened = Store(root)
    assert len(reopened.list()) == 1
    assert reopened.create("Fictif", {"capital_cad": 100}, False, request_id="same-key") == outcomes[0]
    with pytest.raises(Conflict):
        reopened.create("Contenu différent", {"capital_cad": 100}, False, request_id="same-key")


def test_command_and_mutation_rollback_together(tmp_path, monkeypatch):
    store = Store(tmp_path / "rollback")
    remember = store._remember_command
    def crash(*args):
        raise RuntimeError("Crash contrôlé avant commit.")
    monkeypatch.setattr(store, "_remember_command", crash)
    with pytest.raises(RuntimeError):
        store.create("Fictif", {}, False, request_id="retry")
    assert store.list() == []
    with store.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM api_commands").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 0
    monkeypatch.setattr(store, "_remember_command", remember)
    store.create("Fictif", {}, False, request_id="retry")
    assert len(store.list()) == 1


def test_object_is_not_published_before_complete_durable_write(tmp_path, monkeypatch):
    from alphaforge_app.decision import store as store_module
    store = Store(tmp_path / "atomic-object")
    link = store_module.os.link
    def crash(source, destination):
        assert Path(source).read_bytes()
        assert not Path(destination).exists()
        raise RuntimeError("Arrêt contrôlé avant publication de l’objet complet.")
    monkeypatch.setattr(store_module.os, "link", crash)
    with pytest.raises(RuntimeError):
        store._object({"immutable": True})
    assert list((store.root / "objects").glob("*.json")) == []
    monkeypatch.setattr(store_module.os, "link", link)
    h = store._object({"immutable": True})
    assert store._load_object(h) == {"immutable": True}
    assert store._object({"immutable": True}) == h


def test_crash_after_intake_before_dispatch_resumes_same_run(service):
    dossier, run = service.store.create("Exemple fictif Robert.", ROBERT, False, request_id="after-intake")
    assert service.store.snapshot(dossier)["revision"] == 1
    result = service.create("Exemple fictif Robert.", ROBERT, False,
                            request_id="after-intake", background=False)
    assert result["id"] == dossier and result["active_run_id"] == run
    assert result["status"] == "complete"
    assert result["revision"] == 5
    replay = service.create("Exemple fictif Robert.", ROBERT, False,
                            request_id="after-intake", background=False)
    assert len(replay["runs"]) == 1
    assert len(replay["tasks"]) == 4
    assert replay["revision"] == 5


def test_revise_replay_does_not_fail_stale_revision_or_duplicate_run(service):
    before = make_robert(service)
    after = service.revise(before["id"], "Retrait corrigé.", {"withdrawal_cad": 40000},
                           before["revision"], request_id="correction", background=False)
    replay = service.revise(before["id"], "Retrait corrigé.", {"withdrawal_cad": 40000},
                            before["revision"], request_id="correction", background=False)
    assert replay["active_run_id"] == after["active_run_id"]
    assert replay["revision"] == after["revision"]
    assert len(replay["runs"]) == 2
    with pytest.raises(Conflict):
        service.revise(before["id"], "Retrait corrigé.", {"withdrawal_cad": 50000},
                       before["revision"], request_id="correction", background=False)


def test_variant_replay_preserves_parent_and_returns_one_child(service):
    before = make_robert(service)
    child = service.revise(before["id"], "Variante.", {"withdrawal_cad": 40000},
                           before["revision"], "variant", request_id="variant", background=False)
    again = service.revise(before["id"], "Variante.", {"withdrawal_cad": 40000},
                           before["revision"], "variant", request_id="variant", background=False)
    assert child["id"] == again["id"] != before["id"]
    assert len(service.store.list()) == 2
    assert digest(service.store.snapshot(before["id"])) == digest(before)


def test_variant_from_history_uses_historical_inputs_and_keeps_current_lease(client, service):
    before = make_robert(service)
    current = service.revise(before["id"], "Retrait corrigé.", {"withdrawal_cad": 40000},
                             before["revision"], background=False)
    # No full ProblemSpec supplied by the client: the backend must capture r5.
    child = service.revise(before["id"], "Variante historique.", {"scenario_loss_limit_cad": 1000},
                           current["revision"], "variant", source_revision=5,
                           request_id="historical-variant", background=False)
    assert child["active_problem"]["withdrawal_cad"] == 30000
    assert child["active_problem"]["scenario_loss_limit_cad"] == 1000
    origin = project(child)["origin"]
    assert origin["source_revision"] == 5 and origin["revision"] == 10
    inherited = project(child)["facts"]["withdrawal_cad"]
    assert inherited["inherited_from"]["dossier_id"] == before["id"]
    assert inherited["inherited_from"]["source_revision"] == 5
    assert "inherited_from" not in project(child)["facts"]["scenario_loss_limit_cad"]
    rows = client.get("/api/folio/dossiers").json()["dossiers"]
    assert next(r for r in rows if r["id"] == child["id"])["origin"] == origin
    with pytest.raises(ValueError):
        service.revise(before["id"], "Correction.", {}, 10, "replace", source_revision=5)
    response = client.post(f"/api/folio/dossiers/{before['id']}/revise", json={
        "request_id": "missing-source", "message": "Variante.", "changes": {},
        "base_revision": 10, "intent": "variant", "source_revision": 999,
    })
    assert response.status_code == 404


def test_variant_keeps_extracted_origin_and_cross_dossier_source(tmp_path):
    from alphaforge_app.decision.models import ChangeSet
    store = Store(tmp_path / "origins")
    dossier, run = store.create("Capital fictif de 100 CAD.", {}, False)
    task, _ = store.begin_task(run, "agent0", 0, ["request@1"])
    store.commit(ChangeSet(run_id=run, task_id=task, role="agent0", read_set=["request@1"],
        writes=[{"id": "fact.capital_cad", "type": "assertion", "input_refs": ["request@1"],
                 "content": {"field": "capital_cad", "value": 100, "origin": "extracted",
                             "source_ref": "request@1", "quote": "100 CAD"}}],
        next_role="agent1", status="running", reason="Extraction de test, sans inférence."))
    child, _ = store.revise(dossier, "Variante.", {}, 2, "variant", source_revision=2)
    fact = store.artifact(child, "fact.capital_cad@1")["content"]
    assert fact["origin"] == "extracted"
    assert fact["inherited_from"]["artifact_ref"] == "fact.capital_cad@1"
    assert fact["inherited_from"]["dossier_id"] == dossier
    assert fact["inherited_from"]["sha256"] == store.artifact(dossier, "fact.capital_cad@1")["hash"]


def test_historical_heads_events_agents_and_receipts_do_not_leak_future(service):
    before = make_robert(service)
    after = service.revise(before["id"], "Retrait corrigé.", {"withdrawal_cad": 40000},
                           before["revision"], background=False)
    old = at_revision(after, before["revision"])
    v = project(old, historical=True)
    assert v["stats"]["min_reallocation_cad"] == 30000
    assert v["analysis"] == before["current_analysis"]["content"]
    assert old["current_analysis"]["usable"]
    assert old["active_run_id"] == before["active_run_id"]
    assert old["status"] == "complete"
    assert all(e["revision"] <= 5 for e in old["events"])
    assert len(old["tasks"]) == 4
    assert len(old["runs"]) == 1
    assert all(a["task_id"].startswith(before["active_run_id"]) for a in old["attempts"])
    assert not any(a["version"] > 1 for a in old["artifacts"])
    assert v["simple_reference"]["independent"]["turnover_cad"] == 30000
    assert project(after)["simple_reference"] is None


def test_revision_intake_archive_has_no_old_analysis_and_has_new_run(service):
    before = make_robert(service)
    dossier, run = service.store.revise(before["id"], "Retrait corrigé.", {"withdrawal_cad": 40000},
                                        before["revision"])
    snapshot = service.store.snapshot(dossier)
    archive = at_revision(snapshot, snapshot["revision"])
    assert archive["current_analysis"] is None
    assert archive["current_view"] is None
    assert archive["active_run_id"] == run
    assert archive["status"] == "running"
    assert not project(archive)["claims"]
    assert project(archive)["problem"]["capital_cad"] == 100000
    assert project(archive)["problem"]["withdrawal_cad"] == 40000
    assert project(archive)["problem_qualified"] is False
    assert project(archive)["facts"]["withdrawal_cad"]["origin"] == "declared"
    assert all(a["status"] == "not_executed" for a in project(archive)["agents"])


def test_preview_isolated_numeric_provenance_and_no_inference(client, service):
    before = make_robert(service)
    response = client.post(f"/api/folio/dossiers/{before['id']}/preview", json={
        "base_revision": before["revision"], "changes": {"withdrawal_cad": 40000},
    })
    assert response.status_code == 200
    value = response.json()
    assert value["version"]["stats"]["min_reallocation_cad"] == 40000
    assert value["receipt"]["inference_calls"] == 0
    assert value["receipt"]["artifact_cache_reused"] is False
    assert value["version"]["agents"] == [] and value["version"]["events"] == []
    assert value["version"]["simple_reference"] is None
    assert value["version"]["source"]["analysis_ref"] is None
    assert all(b["resolved"] for p in value["version"]["proofs"] for b in p["bindings"])
    assert digest(service.store.snapshot(before["id"])) == digest(before)


def test_preview_impossible_and_missing_do_not_invent_allocations(client, service):
    before = make_robert(service)
    url = f"/api/folio/dossiers/{before['id']}/preview"
    impossible = client.post(url, json={"base_revision": 5, "changes": {"withdrawal_cad": 120000}}).json()
    assert impossible["version"]["analysis_status"] == "infeasible"
    assert impossible["version"]["analysis"]["options"] == []
    assert impossible["version"]["stats"]["shortfall_cad"] == 20000
    assert "min_reallocation_cad" not in impossible["version"]["stats"]
    missing = client.post(url, json={"base_revision": 5, "changes": {"withdrawal_cad": None}}).json()
    assert missing["version"]["analysis_status"] == "missing_input"
    assert missing["version"]["analysis"]["options"] == []
    assert missing["version"]["questions"]


def test_preview_preserves_documentary_blocker_except_independent_budget_certificate(service):
    before = make_robert(service)
    review = next(a for a in before["artifacts"] if a["id"] == "research_review" and a["usable"])
    review["content"]["blocking_issues"] = [{"message": "Source contradictoire non résolue."}]
    blocked = folio_api.preview_snapshot(before, {"withdrawal_cad": 40000})
    assert blocked["receipt"]["calculation_executed"] is False
    assert blocked["version"]["analysis"]["options"] == []
    assert blocked["version"]["analysis_status"] == "missing_input"
    impossible = folio_api.preview_snapshot(before, {"withdrawal_cad": 120000})
    assert impossible["receipt"]["calculation_executed"] is True
    assert impossible["version"]["analysis_status"] == "infeasible"


def test_export_historical_and_invalid_commands(client, service):
    before = make_robert(service)
    service.revise(before["id"], "Retrait corrigé.", {"withdrawal_cad": 40000},
                   before["revision"], background=False)
    response = client.get(f"/api/folio/dossiers/{before['id']}?revision=5")
    assert response.status_code == 200
    assert response.json()["current_revision"] == 10
    assert response.json()["version"]["stats"]["min_reallocation_cad"] == 30000
    exported = client.get(f"/api/folio/dossiers/{before['id']}/export?revision=5")
    assert exported.json()["revision"] == 5
    assert exported.json()["current_analysis"]["content"] == before["current_analysis"]["content"]
    assert exported.headers["x-content-sha256"] == digest(exported.json())
    assert response.json()["version"]["source"]["export_sha256"] == exported.headers["x-content-sha256"]
    assert client.get(f"/api/folio/dossiers/{before['id']}?revision=999").status_code == 404
    assert client.post(f"/api/folio/dossiers/{before['id']}/preview", json={
        "base_revision": 5, "changes": {"withdrawal_cad": True},
    }).status_code == 422
    assert client.post("/api/folio/dossiers", json={"prompt": "Fictif"}).status_code == 422
