"""Pin financial candidate repositories and retrieve license text, no execution."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent / "code"
REPOS = {
    "skfolio/skfolio": "LICENSE",
    "dcajasn/Riskfolio-Lib": "LICENSE",
    "pyportfolio/pyportfolioopt": "LICENSE.txt",
    "cvxpy/cvxpy": "LICENSE",
    "ERGO-Code/HiGHS": "LICENSE.txt",
    "Pyomo/pyomo": "LICENSE.md",
    "google/or-tools": "LICENSE",
    "bashtage/arch": "LICENSE.md",
    "ranaroussi/quantstats": "LICENSE.txt",
    "quaquel/EMAworkbench": "LICENSE.md",
    "kotbaton/pymcdm": "LICENSE",
    "anyoptimization/pymoo": "LICENSE",
    "cvxgrp/cvxportfolio": "LICENSE",
    "stefan-jansen/empyrical-reloaded": "LICENSE",
    "polakowo/vectorbt": "LICENSE.md",
    "pmorissette/bt": "LICENSE",
    "scipy/scipy": "LICENSE.txt",
    "Valdecy/pyDecision": "LICENSE",
    "esvhd/pypbo": "LICENSE",
    "interpretml/DiCE": "LICENSE",
    "marimo-team/marimo": "LICENSE",
    "mjskay/ggdist": "LICENSE",
}


def get(repo_file):
    repo, filename = repo_file
    target = HERE / repo.replace("/", "__")
    target.mkdir(parents=True, exist_ok=True)
    meta = {"repo": repo, "retrieved_at": datetime.now(timezone.utc).isoformat()}
    proc = subprocess.run(["git", "ls-remote", "https://github.com/"+repo+".git", "HEAD"],
                          capture_output=True, text=True, timeout=45)
    sha = proc.stdout.split()[0] if proc.stdout.strip() else None
    meta.update(head_sha=sha, git_exit=proc.returncode, error=proc.stderr or None)
    if sha:
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/{filename}"
        path = target / "LICENSE.txt"
        p = subprocess.run(["curl", "-L", "-sS", "--max-time", "30", "-o", str(path),
                            "-w", "%{http_code}", url], capture_output=True, text=True)
        meta.update(license_url=url, license_status=p.stdout, license_path=filename)
        if path.exists():
            meta["license_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    (target / "metadata.json").write_text(json.dumps(meta, indent=2))
    return repo, sha, meta.get("license_status")


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(get, REPOS.items()):
            print(result, flush=True)
