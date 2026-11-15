"""Inventaire et collecte documentaire HTTP, sans modèle ni exécution de code tiers."""
from __future__ import annotations

import concurrent.futures
import hashlib
import html
import json
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
INPUTS = [
    BASE / "00_prompt2_et_dossier_fourni.md",
    ROOT / "revision_2026-11-15/00_DECORTICAGE_MULTIDIMENSIONNEL.md",
    ROOT / "revision_2026-11-15/00B_ATLAS_DES_RESSOURCES_ET_PLAN_EXPLOITATION.md",
    ROOT / "revision_2026-11-15/01_VISION_INITIALE_PROFIL_ET_ARCHITECTURE_OUVERTE.md",
    ROOT / "revision_2026-11-15/extractions/Introduction-Datathon.txt",
    ROOT / "revision_2026-11-15/RESSOURCES_LIENS_PUBLICS.md",
]
URL_PATTERN = re.compile(r'https?://[^\s<>\)\]"`]+')


def inventory():
    records = {}
    for path in INPUTS:
        section = ""
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if line.startswith("#"):
                section = line.lstrip("# ").strip()
            for raw in URL_PATTERN.findall(line):
                url = raw.rstrip(".,;")
                if url not in records:
                    records[url] = {
                        "id": "U" + str(len(records) + 1).zfill(3),
                        "url": url, "occurrences": [],
                    }
                records[url]["occurrences"].append({
                    "file": str(path.relative_to(ROOT)), "line": number,
                    "section": section, "context": line[:3500],
                })
    return list(records.values())


def collect(record):
    cache = BASE / "collecte"
    cache.mkdir(exist_ok=True)
    meta_path = cache / (record["id"] + ".json")
    if meta_path.exists():
        return json.loads(meta_path.read_text())
    started = time.monotonic()
    out = {"id": record["id"], "requested_url": record["url"],
           "retrieved_at": datetime.now(timezone.utc).isoformat(),
           "mode": "HTTP_GET_sans_inference",
           "reading_level": "collecte_automatique_non_lecture_critique"}
    try:
        req = urllib.request.Request(record["url"], headers={
            "User-Agent": "AlphaForge-Documentary-Research/1.0 (academic prototype; local archive)",
            "Accept": "text/html,application/pdf,application/json,text/plain;q=0.9,*/*;q=0.5",
        })
        with urllib.request.urlopen(req, timeout=25) as response:
            data = response.read(20_000_001)
            out.update(status=response.status, final_url=response.url,
                       content_type=response.headers.get("Content-Type", ""),
                       last_modified=response.headers.get("Last-Modified"))
        if len(data) > 20_000_000:
            out["error"] = "Document supérieur à 20 Mo : collecte bornée, contenu non archivé."
        else:
            is_pdf = data.startswith(b"%PDF")
            extension = ".pdf" if is_pdf else ".html" if "html" in out["content_type"] else ".txt"
            raw_path = cache / (record["id"] + extension)
            raw_path.write_bytes(data)
            out.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                       local_raw=str(raw_path.relative_to(BASE)))
            text_path = cache / (record["id"] + ".extrait.txt")
            if is_pdf:
                result = subprocess.run(["pdftotext", "-layout", str(raw_path), str(text_path)],
                                        capture_output=True, timeout=30)
                if result.returncode:
                    out["extraction_error"] = result.stderr.decode(errors="replace")[:400]
                else:
                    out["local_text"] = str(text_path.relative_to(BASE))
            else:
                text = data.decode("utf-8", errors="replace")
                title = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
                if title:
                    out["title"] = html.unescape(re.sub(r"\s+", " ", title.group(1))).strip()
                text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", text, flags=re.I | re.S)
                text = re.sub(r"</?(?:p|div|section|h[1-6]|li|tr|br)\b[^>]*>", "\n", text, flags=re.I)
                text = html.unescape(re.sub(r"<[^>]+>", " ", text))
                text = re.sub(r"[ \t]+", " ", text)
                text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()
                text_path.write_text(text)
                out["local_text"] = str(text_path.relative_to(BASE))
    except urllib.error.HTTPError as exc:
        out.update(status=exc.code, error=str(exc))
    except Exception as exc:
        out["error"] = type(exc).__name__ + ": " + str(exc)[:300]
    out["duration_s"] = round(time.monotonic() - started, 2)
    meta_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    return out


if __name__ == "__main__":
    records = inventory()
    (BASE / "inventaire_urls.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
    print(f"Inventaire : {len(records)} URLs, dont "
          f"{sum(any('00_prompt2' in o['file'] for o in r['occurrences']) for r in records)} "
          "dans le document fourni.", flush=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for n, result in enumerate(pool.map(collect, records), 1):
            results.append(result)
            if n % 25 == 0:
                print(f"Collecte {n}/{len(records)} ; statuts {dict(Counter(r.get('status','erreur') for r in results))}", flush=True)
    (BASE / "resultats_collecte.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print("Terminé :", dict(Counter(r.get("status", "erreur") for r in results)), flush=True)
