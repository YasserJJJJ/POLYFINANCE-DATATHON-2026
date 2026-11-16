"""Recherche web par Amazon Bedrock AgentCore (API InvokeWebSearch), sur le compte AWS du datathon.

Outil de recherche documentaire pour le développement, pas un composant du produit. Aucune
ressource AWS n'est créée : l'outil « web-search.v1 » est géré par AWS. Chaque appel est journalisé
(requête, RequestId, nombre de résultats) dans research/outils/journal_recherches.jsonl.

    uv run python research/outils/recherche_web.py "requête" [--n 8] [--domaine osfi-bsif.gc.ca] [--apres 2020-01-01]

Un résultat de recherche n'est pas une lecture : le texte renvoyé est un extrait de la page.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import boto3

JOURNAL = Path(__file__).with_name("journal_recherches.jsonl")


def search(query: str, n: int = 8, domains: list[str] | None = None, after: str | None = None, profile: str = "alphaforge",
           region: str = "us-east-1") -> list[dict]:
    client = boto3.Session(profile_name=profile, region_name=region).client("bedrock-agentcore")
    filters: dict = {}
    if domains:
        filters["domainFilter"] = {"include": domains}
    if after:
        filters["publishedDateFilter"] = {"publishedAfter": dt.datetime.fromisoformat(after)}
    kwargs = {"webSearchId": "web-search.v1", "searchQuery": query[:200], "maxResults": max(1, min(n, 25))}
    if filters:
        kwargs["filters"] = filters
    resp = client.invoke_web_search(**kwargs)
    results = [{"titre": r.get("title"), "url": r.get("url"), "date": r["publishedAt"].date().isoformat() if r.get("publishedAt") else None,
                "extrait": r.get("text", "")} for r in resp.get("results", [])]
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"quand": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "requete": query, "domaines": domains,
                            "apres": after, "resultats": len(results), "requestId": resp["ResponseMetadata"]["RequestId"]}, ensure_ascii=False) + "\n")
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Recherche web par Amazon Bedrock AgentCore (route AWS).")
    ap.add_argument("requete")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--domaine", action="append", help="restreindre à un domaine (répétable)")
    ap.add_argument("--apres", help="publié après cette date (AAAA-MM-JJ)")
    ap.add_argument("--extrait", type=int, default=600, help="nombre de caractères d'extrait affichés")
    args = ap.parse_args()
    for i, r in enumerate(search(args.requete, args.n, args.domaine, args.apres), 1):
        print(f"[{i}] {r['titre']}\n    {r['url']}" + (f"  ({r['date']})" if r["date"] else ""))
        print("    " + " ".join(r["extrait"].split())[: args.extrait])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
