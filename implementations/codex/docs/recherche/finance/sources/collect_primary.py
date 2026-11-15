"""Read-only HTTP collection for finance research; never invokes a model.

Uses the system curl trust store (Python's CA store rejected some university
certificates). A downloaded document is NOT evidence of a critical reading.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SOURCES = {
    "sr26_2": "https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf",
    "chinneck2007": "https://sce.carleton.ca/faculty/chinneck/docs/CPAIOR07InfeasibilityTutorial.pdf",
    "ledoit_honey": "https://ledoit.net/Honey_2004.pdf",
    "ledoit_upf": "https://econ-papers.upf.edu/papers/691.pdf",
    "boyd_convex": "https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf",
    "dgu_ssrn": "https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID911512_code23161.pdf?abstractid=911512",
    "wasserstein": "https://arxiv.org/pdf/1505.05116v3",
    "crypto_moments": "https://arxiv.org/pdf/2501.12841v3",
    "schur": "https://arxiv.org/pdf/2411.05807v1",
    "fred_realtime": "https://fred.stlouisfed.org/docs/api/fred/realtime_period.html",
    "gw_sensitivity": "https://www2.seas.gwu.edu/~dorpjr/EMSE269/Lecture%20Notes/Chapter%205.pdf",
}


def collect(item):
    name, url = item
    raw = HERE / (name + ".raw")
    result = {
        "id": name, "url": url,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "reading_level": "download_only",
    }
    proc = subprocess.run(
        ["curl", "-L", "-sS", "--max-time", "40", "-o", str(raw),
         "-w", "%{http_code}\n%{url_effective}\n%{content_type}", url],
        capture_output=True, text=True,
    )
    result.update(curl_exit=proc.returncode, transport=proc.stdout,
                  error=proc.stderr or None)
    if raw.exists():
        content = raw.read_bytes()
        result.update(bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
        if content.startswith(b"%PDF"):
            pdf = raw.with_suffix(".pdf")
            raw.replace(pdf)
            subprocess.run(["pdftotext", "-layout", str(pdf), str(raw.with_suffix(".txt"))],
                           check=False, capture_output=True)
            result["local_raw"] = pdf.name
        else:
            result["local_raw"] = raw.name
    (HERE / (name + ".json")).write_text(json.dumps(result, indent=2))
    return name, result["transport"].splitlines()[:1], result.get("bytes")


if __name__ == "__main__":
    selected = sys.argv[1:] or list(SOURCES)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(collect, [(k, SOURCES[k]) for k in selected]):
            print(result)
