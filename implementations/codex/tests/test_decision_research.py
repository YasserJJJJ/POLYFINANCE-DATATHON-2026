import hashlib
import json
from datetime import datetime, timezone

import httpx
import pytest

from alphaforge_app.decision import research as module


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    root = tmp_path
    corpus = root / "docs/recherche"
    captures = corpus / "collecte"
    captures.mkdir(parents=True)
    body = (
        b"<html><title>Primary portfolio document</title><main>"
        b"<p>Portfolio liquidity does not establish a contractual capital guarantee. "
        b"The original instrument terms must be checked for the withdrawal date.</p>"
        b"<p>Historical returns describe observations, not guaranteed future returns.</p>"
        b"</main></html>"
    )
    (captures / "U999.html").write_bytes(body)
    meta = {
        "status": 200, "sha256": hashlib.sha256(body).hexdigest(),
        "retrieved_at": "2026-11-15T10:00:00+00:00",
        "local_raw": "collecte/U999.html",
        "local_text": "collecte/U999.extrait.txt",
        "requested_url": "https://example.org/paper", "content_type": "text/html",
    }
    (captures / "U999.json").write_text(json.dumps(meta))
    # This forged neighbouring extraction must never become our evidence.
    (captures / "U999.extrait.txt").write_text("An ESG score of 99 is guaranteed.")
    monkeypatch.setattr(module, "ROOT", root)
    monkeypatch.setattr(module, "CORPUS_ROOT", corpus)
    monkeypatch.setattr(module, "CAPTURE_ROOT", root / "runtime/captures")
    spec = {"id": "U999", "metadata": captures / "U999.json"}
    monkeypatch.setattr(module, "_catalog", lambda problem, query: [spec])
    return captures


def test_quotes_are_reextracted_from_hash_verified_raw_not_adjacent_text(corpus):
    result = module.research({"decision_type": "explanation"}, query="portfolio liquidity", allow_web=False)
    evidence = result["evidence"][0]
    assert "contractual capital guarantee" in evidence["passage"]
    assert "ESG score of 99" not in evidence["passage"]
    assert evidence["review_status"] == "extracted_for_role_review"
    assert evidence["known_at"].startswith("2026-11-15")
    captured_text = module.ROOT / evidence["capture"]["text_path"]
    assert hashlib.sha256(captured_text.read_bytes()).hexdigest() == evidence["capture"]["text_sha256"]


def test_hash_mismatch_is_not_returned_as_evidence(corpus):
    (corpus / "U999.html").write_text("Modified capture")
    result = module.research({}, allow_web=False)
    assert result["evidence"] == []
    assert result["receipts"][0]["error_code"] == "CaptureHashMismatch"
    assert any(g["code"] == "document_access_incomplete" for g in result["gaps"])


def test_knowledge_date_rejects_later_capture_and_does_not_backdate(corpus, monkeypatch):
    monkeypatch.setattr(module, "_aws_search", lambda _: pytest.fail("No present-day search for old cutoff"))
    result = module.research({"knowledge_date": "2020-01-01"}, allow_web=True)
    assert result["evidence"] == []
    assert any(g["code"] == "source_after_knowledge_date" for g in result["gaps"])
    assert result["receipts"][-1]["reason"] == "historical_knowledge_cutoff"


def test_search_snippets_never_become_documentary_proof(monkeypatch):
    monkeypatch.setattr(module, "_catalog", lambda *_: [])
    monkeypatch.setattr(module, "_aws_search", lambda _: (
        [{"url": "https://example.org/unreadable", "snippet": "Guaranteed principal, ESG 99"}],
        [{"tool_id": "aws_invoke_web_search", "status": "success", "execution_id": "S"}],
    ))
    monkeypatch.setattr(module, "_fetch_http", lambda *_: (
        None, {"tool_id": "http_document_capture", "status": "failed",
               "error_code": "HTTP_403", "execution_id": "F"},
    ))
    result = module.research({"decision_type": "reserve_allocation"}, query="ESG reserve")
    assert result["evidence"] == []
    assert {g["code"] for g in result["gaps"]} >= {
        "real_reserve_not_qualified", "esg_measurement_missing", "document_access_incomplete"
    }


def test_aws_search_rejects_wrong_account_before_search(monkeypatch):
    operations = []

    class Session:
        def client(self, service, **kwargs):
            operations.append(service)
            assert service == "sts"
            return self

        def get_caller_identity(self):
            return {"Account": "000000000000"}

    monkeypatch.setattr(module.boto3, "Session", lambda **_: Session())
    hits, receipts = module._aws_search("public research")
    assert not hits
    assert operations == ["sts"]
    assert receipts[-1]["error_code"] == "AccountMismatch"


def test_http_capture_has_real_passage_hash_and_publication_claim(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "CAPTURE_ROOT", tmp_path / "captures")
    monkeypatch.setattr(module, "_public_url", lambda _: None)
    html = (
        '<html><head><title>A primary document</title>'
        '<meta name="citation_publication_date" content="2024-01-02"></head><main>'
        '<p>Historical portfolio measurements describe their sample and assumptions. '
        'They do not establish future investment performance or any contractual guarantee.</p>'
        '<p>Contradictions need an applicable source and independent examination, not a vote.</p>'
        '</main></html>'
    )
    real_client = httpx.Client
    transport = httpx.MockTransport(lambda request: httpx.Response(
        200, text=html, headers={"content-type": "text/html"}, request=request
    ))
    monkeypatch.setattr(module.httpx, "Client", lambda **kwargs: real_client(
        **kwargs, transport=transport
    ))
    evidence, receipt = module._fetch_http("https://example.org/primary", "historical portfolio")
    assert receipt["status"] == "success"
    assert evidence["published_at_claim"] == "2024-01-02"
    assert evidence["known_at"].startswith(datetime.now(timezone.utc).date().isoformat())
    path = tmp_path / evidence["capture"]["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["capture"]["sha256"]
    assert evidence["reading_level"] == "targeted_passages"


def test_private_and_credential_urls_are_rejected():
    for url in ["http://example.org/", "https://user:secret@example.org/", "https://example.org:8080/"]:
        with pytest.raises(ValueError):
            module._public_url(url)


def test_site_restriction_uses_api_filter_and_checks_returned_domains(monkeypatch):
    parameters = []

    class Session:
        def client(self, service, **kwargs):
            return self

        def get_caller_identity(self):
            return {"Account": module.EXPECTED_ACCOUNT, "ResponseMetadata": {"RequestId": "STS"}}

        def invoke_web_search(self, **kwargs):
            parameters.append(kwargs)
            return {
                "ResponseMetadata": {"RequestId": "SEARCH"},
                "results": [
                    {"url": "https://www.cdic.ca/covered", "title": "Primary"},
                    {"url": "https://notcdic.ca/lookalike", "title": "Wrong host"},
                ],
            }

    monkeypatch.setattr(module.boto3, "Session", lambda **_: Session())
    hits, receipts = module._aws_search("site:CDIC.ca eligible deposit")
    assert parameters[0]["filters"] == {"domainFilter": {"include": ["cdic.ca"]}}
    assert [hit["url"] for hit in hits] == ["https://www.cdic.ca/covered"]
    assert receipts[-1]["discarded_domain_count"] == 1
    assert module._authority("https://notcdic.ca/lookalike") == "unclassified_requires_review"
