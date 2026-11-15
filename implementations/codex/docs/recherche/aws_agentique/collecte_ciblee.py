"""Collecte documentaire bornée, sans inférence ni exécution du code téléchargé."""
from __future__ import annotations

import concurrent.futures
import hashlib
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parent


def fetch(item: dict) -> dict:
    name, url = item["id"], item["url"]
    folder = BASE / "sources"
    folder.mkdir(exist_ok=True)
    meta_path = folder / f"{name}.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text())
    meta = {"id": name, "url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "mode": "HTTP_GET_sans_inference", "reading_level": "collecte_non_lecture"}
    try:
        req = Request(url, headers={"User-Agent": "AlphaForge-Research/1.0",
                                    "Accept": "text/html,application/pdf,application/json,*/*"})
        with urlopen(req, timeout=30) as response:
            data = response.read(12_000_001)
            meta.update(status=response.status, final_url=response.url,
                        content_type=response.headers.get("Content-Type", ""),
                        last_modified=response.headers.get("Last-Modified"))
        if len(data) > 12_000_000:
            raise ValueError("Document supérieur à la limite de 12 Mo")
        ext = "pdf" if data.startswith(b"%PDF") else "raw"
        target = folder / f"{name}.{ext}"
        target.write_bytes(data)
        meta.update(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                    raw_file=str(target.relative_to(BASE)))
        text_file = folder / f"{name}.txt"
        if ext == "pdf":
            run = subprocess.run(["pdftotext", "-layout", str(target), str(text_file)],
                                 capture_output=True, timeout=30)
            if run.returncode:
                raise ValueError("Échec extraction PDF")
        else:
            text = data.decode("utf-8", errors="replace")
            if "html" in meta["content_type"]:
                match = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
                if match:
                    meta["title"] = html.unescape(re.sub(r"\s+", " ", match.group(1)))
                text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", text, flags=re.S | re.I)
                text = re.sub(r"</?(?:p|div|h[1-6]|li|tr|br|section)\b[^>]*>", "\n", text, flags=re.I)
                text = html.unescape(re.sub(r"<[^>]+>", " ", text))
                text = re.sub(r"[ \t]+", " ", text)
                text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()
            text_file.write_text(text)
        meta["text_file"] = str(text_file.relative_to(BASE))
    except Exception as exc:
        meta["error"] = f"{type(exc).__name__}: {exc}"[:500]
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    return meta


if __name__ == "__main__":
    items = json.loads(Path(sys.argv[1]).read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for result in pool.map(fetch, items):
            print(result["id"], result.get("status", "error"), result.get("bytes"),
                  result.get("error", ""), flush=True)
