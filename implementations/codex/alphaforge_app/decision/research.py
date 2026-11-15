"""Bounded documentary research: captured source text, not generated evidence.

Search uses the verified team AWS account. HTTP/PDF extraction is deterministic.
Dates from a search index never establish historical availability of a capture.
The role using these passages still has to assess entailment and applicability.
"""

from __future__ import annotations

import hashlib
import io
import ipaddress
import json
import os
import re
import socket
import tempfile
import time
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import boto3
import httpx
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from bs4 import BeautifulSoup
from pypdf import PdfReader

from alphaforge_app.bedrock import EXPECTED_ACCOUNT, REGION

ROOT = Path(__file__).resolve().parents[2]
CORPUS_ROOT = ROOT / "docs/recherche"
CAPTURE_ROOT = ROOT / "runtime/decision/research"
MAX_BYTES = 10 * 1024 * 1024
MAX_WEB_RESULTS = 3
MAX_PASSAGE_CHARS = 2200
VERSION = "1.0"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tokens(text: str) -> set[str]:
    plain = "".join(c for c in unicodedata.normalize("NFKD", text.lower())
                    if not unicodedata.combining(c))
    return set(re.findall(r"[a-z][a-z0-9]{3,}", plain)) - {
        "avec", "pour", "dans", "from", "that", "this", "have", "will", "what",
        "which", "their", "your", "plus", "moins", "comment", "quel", "quels",
    }


def _passages(text: str, query: str, *, limit: int = 3) -> list[dict[str, Any]]:
    lines = text.splitlines()
    terms = _tokens(query)
    # Windows are exact excerpts, not model-written summaries.
    windows = []
    for start in range(0, len(lines), 5):
        end = min(len(lines), start + 14)
        passage = "\n".join(lines[start:end]).strip()
        if len(passage) < 90:
            continue
        score = len(terms & _tokens(passage))
        windows.append((score, start, end, passage))
    selected = []
    for score, start, end, passage in sorted(windows, key=lambda x: (-x[0], x[1])):
        if selected and score == 0:
            continue
        if any(abs(start - p["line_start"] + 1) < 14 for p in selected):
            continue
        # Locate truncated excerpts honestly; their line range is a containing
        # range and text_truncated records that the last line may be partial.
        selected.append({
            "line_start": start + 1,
            "line_end": end,
            "text": passage[:MAX_PASSAGE_CHARS],
            "text_truncated": len(passage) > MAX_PASSAGE_CHARS,
            "selection": "deterministic_keyword_window",
            "match_terms": sorted(terms & _tokens(passage)),
        })
        if len(selected) == limit:
            break
    return selected


def _receipt(tool: str, status: str, started: str, **fields: Any) -> dict[str, Any]:
    return {
        "tool_id": tool,
        "version": VERSION,
        "execution_id": _hash(f"{tool}:{started}:{time.monotonic_ns()}".encode())[:24],
        "started_at": started,
        "finished_at": _now(),
        "status": status,
        **fields,
    }


def _date_limit(problem: dict[str, Any]) -> date | None:
    value = problem.get("knowledge_date")
    if not value:
        return None
    return date.fromisoformat(str(value)[:10])


def _in_time(known_at: str | None, limit: date | None) -> bool:
    if limit is None:
        return True
    if not known_at:
        return False
    try:
        return date.fromisoformat(known_at[:10]) <= limit
    except (TypeError, ValueError):
        return False


def _catalog(problem: dict[str, Any], query: str) -> list[dict[str, Any]]:
    """Small relevant corpus selected by decision, with lexical extension."""
    kind = problem.get("decision_type", "explanation")
    common = ["U341"]
    if kind == "reserve_allocation":
        common += ["boyd_convex", "U050"]
    elif kind == "historical_comparison":
        common += ["U001", "U002", "U003", "U342", "fred_realtime"]
    else:
        common += ["U001", "U002"]
    if _tokens(query) & {"cvar", "tail", "expected", "shortfall", "conditionnelle"}:
        common += ["cvar2000"]
    if _tokens(query) & {"linear", "lineaire", "optimisation", "optimization"}:
        common += ["boyd_convex"]
    output = []
    for source_id in dict.fromkeys(common):
        if source_id.startswith("U"):
            meta = CORPUS_ROOT / "collecte" / f"{source_id}.json"
        else:
            meta = CORPUS_ROOT / "finance/sources" / f"{source_id}.json"
        spec = {"id": source_id, "metadata": meta}
        if source_id == "boyd_convex":
            # PDF pages 160–166: chapter 4.3; 167 starts quadratic programs.
            spec["pdf_pages"] = list(range(160, 167))
            spec["title"] = "Convex Optimization — Boyd et Vandenberghe, chapitre 4.3"
        output.append(spec)
    return output


def _load_local(spec: dict[str, Any], query: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    started = _now()
    try:
        metadata_path = Path(spec["metadata"])
        meta = json.loads(metadata_path.read_text())
        if meta.get("status") not in (None, 200) or meta.get("error"):
            raise ValueError("CaptureUnavailable")
        base = CORPUS_ROOT if spec["id"].startswith("U") else metadata_path.parent
        raw = (base / meta["local_raw"]).resolve()
        # Paths come from our bounded catalog, not arbitrary model references.
        raw.relative_to(CORPUS_ROOT.resolve())
        data = raw.read_bytes()
        raw_hash = _hash(data)
        if meta.get("sha256") != raw_hash:
            raise ValueError("CaptureHashMismatch")
        # Re-extract from the verified raw capture. A neighbouring .txt file
        # without an original extraction hash cannot authenticate a quotation.
        text, extracted_title, _ = _extract(
            data, meta.get("content_type", ""), raw.suffix,
            pdf_pages=spec.get("pdf_pages"),
        )
        text_path = _store_bytes(text.encode(), ".txt")
        passages = _passages(text, query)
        if not passages:
            raise ValueError("NoReadablePassage")
        known_at = meta.get("retrieved_at")
        evidence = {
            "id": f"local-{spec['id']}-{raw_hash[:12]}",
            "version": 1,
            "source_id": spec["id"],
            "source": {
                "url": meta.get("requested_url") or meta.get("url"),
                "title": spec.get("title") or meta.get("title") or extracted_title or spec["id"],
                "kind": "captured_document",
                "authority": _authority(meta.get("requested_url") or meta.get("url") or ""),
            },
            "known_at": known_at,
            "known_at_basis": "timestamp_of_exact_captured_version",
            "reading_level": "targeted_passages",
            "review_status": "extracted_for_role_review",
            "passages": passages,
            "passage": passages[0]["text"],
            "capture": {
                "path": str(raw.relative_to(ROOT)),
                "sha256": raw_hash,
                "text_sha256": _hash(text.encode()),
                "text_path": str(text_path.relative_to(ROOT)),
            },
            "scope": {"query": query, "source_version": raw_hash, "pdf_pages": spec.get("pdf_pages")},
            "limitations": [
                "Passages extraits automatiquement ; pertinence et ancrage restent à examiner.",
                "Date de capture conservatrice ; elle ne prouve pas la disponibilité de cette version à une date antérieure.",
            ],
        }
        receipt = _receipt(
            "local_corpus_read", "success", started,
            parameters={"source_id": spec["id"]}, output_refs=[evidence["id"]],
            capture_sha256=raw_hash,
        )
        return evidence, receipt
    except (OSError, KeyError, ValueError) as exc:
        return None, _receipt(
            "local_corpus_read", "failed", started,
            parameters={"source_id": spec["id"]},
            error_code=str(exc) if type(exc) is ValueError else type(exc).__name__,
        )


def _extract(
    data: bytes, content_type: str, suffix: str = "", *,
    pdf_pages: list[int] | None = None,
) -> tuple[str, str, str | None]:
    if data.startswith(b"%PDF") or "pdf" in content_type or suffix == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        # All extracted pages are labelled; no claim of reading the entire PDF.
        pages = []
        selected = pdf_pages or list(range(1, min(60, len(reader.pages)) + 1))
        for n in selected:
            if 1 <= n <= len(reader.pages):
                pages.append(f"[PDF page {n}]\n{reader.pages[n - 1].extract_text() or ''}")
        return "\n\n".join(pages), str((reader.metadata or {}).get("/Title", "")), None
    soup = BeautifulSoup(data, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    published = None
    for attrs in (
        {"name": "citation_publication_date"},
        {"property": "article:published_time"},
        {"name": "date"},
    ):
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            published = str(tag["content"])
            break
    for tag in soup(["script", "style", "nav", "footer", "noscript"]):
        tag.decompose()
    body = soup.find("main") or soup.find("article") or soup.body or soup
    text = "\n".join(
        line.strip() for line in body.get_text("\n", strip=True).splitlines() if line.strip()
    )
    return text, title, published


def _public_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("PublicHTTPSRequired")
    if parsed.port not in (None, 443):
        raise ValueError("NonStandardPort")
    addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ValueError("NonPublicAddress")


def _authority(url: str) -> str:
    hostname = urlsplit(url).hostname or ""
    def belongs(domain: str) -> bool:
        return hostname == domain or hostname.endswith("." + domain)

    if belongs("wikipedia.org"):
        return "secondary_encyclopedia"
    if hostname in {"ideas.repec.org", "econpapers.repec.org"}:
        return "bibliographic_record_with_abstract"
    if hostname == "github.com":
        return "software_repository_documentation"
    if any(belongs(domain) for domain in ("cdic.ca", "cfainstitute.org", "bankofcanada.ca")):
        return "institutional_publisher_scope_to_review"
    if belongs("stanford.edu") and ".pdf" in url:
        return "author_hosted_primary_text"
    return "unclassified_requires_review"


def _store_bytes(data: bytes, suffix: str) -> Path:
    CAPTURE_ROOT.mkdir(parents=True, exist_ok=True)
    path = CAPTURE_ROOT / f"{_hash(data)}{suffix}"
    if not path.exists():
        # Publish only a completely written file, also under concurrent fetches.
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=CAPTURE_ROOT, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temporary, path)
        except FileExistsError:
            pass
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    if _hash(path.read_bytes()) != _hash(data):
        raise ValueError("CaptureWriteMismatch")
    return path


def _fetch_http(url: str, query: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    started = _now()
    current = url
    try:
        with httpx.Client(
            timeout=httpx.Timeout(20.0, connect=7.0), follow_redirects=False,
            trust_env=False, headers={"User-Agent": "AlphaForgeResearch/1.0"},
        ) as client:
            for _ in range(5):
                _public_url(current)
                with client.stream("GET", current) as response:
                    if response.is_redirect:
                        current = urljoin(current, response.headers["location"])
                        continue
                    response.raise_for_status()
                    body = bytearray()
                    for chunk in response.iter_bytes():
                        body.extend(chunk)
                        if len(body) > MAX_BYTES:
                            raise ValueError("DocumentSizeLimit")
                    content_type = response.headers.get("content-type", "")
                    if not any(x in content_type for x in ("html", "pdf", "text/plain")):
                        raise ValueError("UnsupportedDocumentType")
                    data = bytes(body)
                    break
            else:
                raise ValueError("RedirectLimit")
        text, title, published_at = _extract(data, content_type)
        if len(text) < 200 or re.search(
            r"captcha|access denied|verify you are human|radware",
            f"{title} {text[:500]}", re.I,
        ):
            raise ValueError("AccessBarrierOrUnreadable")
        passages = _passages(text, query)
        if not passages:
            raise ValueError("NoReadablePassage")
        raw = _store_bytes(data, ".pdf" if data.startswith(b"%PDF") else ".html")
        extracted = _store_bytes(text.encode(), ".txt")
        digest = _hash(data)
        evidence = {
            "id": f"web-{digest[:20]}",
            "version": 1,
            "source": {"url": url, "resolved_url": current, "title": title,
                       "kind": "captured_document", "authority": _authority(current)},
            "known_at": started,
            "known_at_basis": "timestamp_of_exact_captured_version",
            "published_at_claim": published_at,
            "reading_level": "targeted_passages",
            "review_status": "extracted_for_role_review",
            "passages": passages,
            "passage": passages[0]["text"],
            "capture": {
                "path": str(raw.relative_to(ROOT)),
                "sha256": digest,
                "text_path": str(extracted.relative_to(ROOT)),
                "text_sha256": _hash(text.encode()),
            },
            "scope": {"query": query, "source_version": digest},
            "limitations": [
                "Capture et extraction ne prouvent ni l'exactitude ni l'applicabilité.",
                "Métadonnées de publication à recouper ; elles ne rétrodatent pas la capture.",
                "PDF : extraction bornée aux soixante premières pages, sans OCR.",
            ],
        }
        return evidence, _receipt(
            "http_document_capture", "success", started,
            parameters={"url": url}, resolved_url=current,
            output_refs=[evidence["id"]], capture_sha256=digest,
        )
    except Exception as exc:
        code = str(exc) if type(exc) is ValueError else type(exc).__name__
        if isinstance(exc, httpx.HTTPStatusError):
            code = f"HTTP_{exc.response.status_code}"
        return None, _receipt(
            "http_document_capture", "failed", started,
            parameters={"url": url}, error_code=code,
        )


def _aws_search(query: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    started = _now()
    receipts = []
    try:
        if os.environ.get("AWS_BEARER_TOKEN_BEDROCK"):
            raise ValueError("UnexpectedBearerToken")
        config = Config(
            signature_version="v4", ignore_configured_endpoint_urls=True,
            connect_timeout=7, read_timeout=25,
            retries={"mode": "standard", "total_max_attempts": 2},
        )
        session = boto3.Session(profile_name="alphaforge", region_name=REGION)
        identity = session.client(
            "sts", config=config, endpoint_url=f"https://sts.{REGION}.amazonaws.com"
        ).get_caller_identity()
        if identity["Account"] != EXPECTED_ACCOUNT:
            raise ValueError("AccountMismatch")
        receipts.append(_receipt(
            "aws_sts_identity", "success", started,
            account_id=identity["Account"], region=REGION, profile="alphaforge",
            provider_request_id=identity["ResponseMetadata"].get("RequestId"),
        ))
        parameters = {
            "webSearchId": "web-search.v1", "searchQuery": query,
            "maxResults": MAX_WEB_RESULTS,
        }
        domains = sorted({d.lower() for d in re.findall(r"\bsite:([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", query)})
        if domains:
            parameters["filters"] = {"domainFilter": {"include": domains}}
        response = session.client(
            "bedrock-agentcore", config=config,
            endpoint_url=f"https://bedrock-agentcore.{REGION}.amazonaws.com",
        ).invoke_web_search(**parameters)
        results = []
        for item in response.get("results", [])[:MAX_WEB_RESULTS]:
            hostname = (urlsplit(item.get("url", "")).hostname or "").lower()
            if domains and not any(hostname == domain or hostname.endswith("." + domain) for domain in domains):
                continue
            results.append({
                "title": item.get("title"), "url": item.get("url"),
                "snippet": item.get("text", "")[:3000],
                "published_at_index_claim": str(item.get("publishedAt")) if item.get("publishedAt") else None,
            })
        receipts.append(_receipt(
            "aws_invoke_web_search", "success", started,
            parameters=parameters, account_id=EXPECTED_ACCOUNT, profile="alphaforge",
            region=REGION, provider_request_id=response["ResponseMetadata"].get("RequestId"),
            result_count=len(results), raw_result_count=len(response.get("results", [])),
            discarded_domain_count=len(response.get("results", [])) - len(results),
            results=results,
            mode="ranked_search_no_WebAnswer",
            measured_cost=None,
        ))
        return results, receipts
    except (BotoCoreError, ClientError, ValueError) as exc:
        code = (
            exc.response.get("Error", {}).get("Code", type(exc).__name__)
            if isinstance(exc, ClientError) else
            str(exc) if type(exc) is ValueError else type(exc).__name__
        )
        request_id = (
            exc.response.get("ResponseMetadata", {}).get("RequestId")
            if isinstance(exc, ClientError) else None
        )
        receipts.append(_receipt(
            "aws_invoke_web_search", "failed", started,
            parameters={"searchQuery": query, "maxResults": MAX_WEB_RESULTS},
            provider_request_id=request_id, error_code=code,
        ))
        return [], receipts


def research(
    problem: dict[str, Any], *, query: str | None = None, allow_web: bool = True
) -> dict[str, Any]:
    """Return captured passages, documentary candidates and explicit gaps.

    No evidence item is a generated numerical observation or ESG score. Search
    snippets remain in receipts until the linked document is actually captured.
    """
    kind = problem.get("decision_type", "explanation")
    defaults = {
        "reserve_allocation": "short term withdrawal nominal capital protection liquidity linear programming portfolio",
        "historical_comparison": "historical portfolio comparison diversification estimation risk backtest limitations currency",
        "explanation": str(problem.get("question") or "portfolio decision methods assumptions evidence"),
    }
    query = (query or defaults.get(kind, defaults["explanation"])).strip()[:500]
    if not query:
        raise ValueError("La question documentaire ne peut pas être vide.")
    limit = _date_limit(problem)
    result: dict[str, Any] = {
        "evidence": [], "methods": [], "gaps": [], "contradictions": [],
        "receipts": [], "limitations": [
            "La collecte fournit des passages à examiner ; elle ne certifie pas leur soutien à une assertion.",
            "Aucun score ESG, rendement attendu ou propriété contractuelle n'est imputé.",
        ],
        "query": query, "knowledge_date": limit.isoformat() if limit else None,
    }

    def admit(evidence: dict[str, Any] | None) -> None:
        if evidence is None:
            return
        if not _in_time(evidence.get("known_at"), limit):
            result["gaps"].append({
                "code": "source_after_knowledge_date",
                "source_ref": evidence["id"], "known_at": evidence.get("known_at"),
                "message": "Cette version capturée n'est pas établie comme disponible à la date de connaissance.",
            })
            return
        if not any(item["id"] == evidence["id"] for item in result["evidence"]):
            result["evidence"].append(evidence)

    for spec in _catalog(problem, query):
        evidence, receipt = _load_local(spec, query)
        result["receipts"].append(receipt)
        admit(evidence)

    if allow_web and (limit is None or limit >= datetime.now(timezone.utc).date()):
        hits, receipts = _aws_search(query)
        result["receipts"].extend(receipts)
        for hit in hits:
            if not hit.get("url"):
                continue
            evidence, receipt = _fetch_http(hit["url"], query)
            result["receipts"].append(receipt)
            if evidence:
                evidence["search_index"] = hit
                index_date = hit.get("published_at_index_claim")
                primary_date = evidence.get("published_at_claim")
                if index_date and primary_date and index_date[:10] != primary_date[:10].replace("/", "-"):
                    result["contradictions"].append({
                        "code": "publication_metadata_disagreement",
                        "source_ref": evidence["id"],
                        "index_claim": index_date, "document_claim": primary_date,
                        "status": "requires_review",
                        "message": "Les dates déclarées diffèrent ; version initiale et mise à jour restent à distinguer.",
                    })
            admit(evidence)
    else:
        result["receipts"].append(_receipt(
            "aws_invoke_web_search", "skipped", _now(),
            reason="historical_knowledge_cutoff" if allow_web else "web_not_allowed",
        ))

    by_source = {item.get("source_id"): item for item in result["evidence"]}
    for source, method_id, title in (
        ("boyd_convex", "linear_programming", "Programmation linéaire sous contraintes explicites"),
        ("cvar2000", "cvar_scenario_optimization", "CVaR sous distribution ou scénarios justifiés"),
        ("U001", "naive_diversification_benchmark", "Référence de diversification naïve et risque d'estimation"),
    ):
        if source in by_source:
            result["methods"].append({
                "id": method_id, "version": 1, "name": title,
                "status": "documented_candidate",
                "source_refs": [by_source[source]["id"]],
                "executable_admission": False,
                "limitations": ["La pertinence, l'implémentation et les contrôles doivent être qualifiés séparément."],
            })
    if "U001" in by_source and "U002" in by_source:
        result["contradictions"].append({
            "code": "optimization_empirical_results_differ",
            "source_refs": [by_source["U001"]["id"], by_source["U002"]["id"]],
            "status": "context_dependent",
            "message": "Les conclusions empiriques sur optimisation et diversification diffèrent selon méthodes et protocoles ; aucune supériorité universelle n'est établie.",
        })
    if kind == "reserve_allocation":
        result["gaps"].append({
            "code": "real_reserve_not_qualified",
            "message": "Aucun contrat d'instrument réel n'a été qualifié pour assurer disponibilité et nominal du retrait.",
            "effect": "abstract_conditional_only" if problem.get("reserve_policy") == "abstract_nominal" else "blocks_real_instrument_claim",
        })
    if re.search(r"\besg\b|durabil|sustainab", query, re.I):
        result["gaps"].append({
            "code": "esg_measurement_missing",
            "message": "Aucune mesure ESG datée, définie et comparable n'est disponible dans ce résultat.",
        })
    if not result["evidence"]:
        result["gaps"].append({"code": "no_admissible_document", "message": "Aucun passage admissible dans la portée et la date demandées."})
    failures = [r for r in result["receipts"] if r["status"] == "failed"]
    if failures:
        result["gaps"].append({
            "code": "document_access_incomplete",
            "message": "Certaines recherches ou captures ont échoué ; les reçus indiquent lesquelles.",
            "execution_refs": [r["execution_id"] for r in failures],
        })
    return result
