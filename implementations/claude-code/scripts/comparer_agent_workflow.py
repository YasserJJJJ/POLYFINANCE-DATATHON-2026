"""Compare les dossiers de l'agent Bedrock au workflow fixe (critère de réfutation (a) de D1).

Lit `runs/*/dossier.json` et écrit un tableau Markdown sur la sortie standard :
    uv run python scripts/comparer_agent_workflow.py > docs/comparaison-agent-workflow.md
Aucun appel AWS ni recalcul : tout vient des dossiers enregistrés.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1] / "runs"
REFERENCE = {"robert-agent": "robert-tsla", "amira-agent": "amira-croissance"}  # dossier d'agent → workflow fixe de même scénario


def call_name(t: dict) -> str:
    a = t.get("arguments") or {}
    if t["outil"] == "metriques_actif":  # appel en erreur enregistré sous le nom vu par l'agent
        t = dict(t, outil="asset_metrics")
    if t["outil"] == "asset_metrics":
        name = f"asset_metrics({a.get('ticker')})"
    elif t["outil"] == "correlation":
        name = f"correlation({a.get('t1')}, {a.get('t2')})"
    elif t["outil"] == "share_sweep":
        name = f"share_sweep({a.get('ticker')})"
    else:
        name = t["outil"]
    return name + (" [erreur]" if t.get("erreur") else "")


def calls(d: dict) -> Counter:
    return Counter(call_name(t) for t in d["trace"])


def listing(c: Counter) -> str:
    return ", ".join(f"{k} ×{n}" if n > 1 else k for k, n in sorted(c.items())) or "—"


def main() -> int:
    dossiers = {f.parent.name: json.loads(f.read_text(encoding="utf-8")) for f in sorted(RUNS.glob("*/dossier.json"))}
    agents = {k: d for k, d in dossiers.items() if d.get("aws", {}).get("appels")}
    out = ["# Agent Bedrock et workflow fixe : comparaison des dossiers enregistrés", "",
           "Fichier produit par `scripts/comparer_agent_workflow.py` à partir de `runs/*/dossier.json` ; ne pas le modifier à la main.",
           "Critère de réfutation (a) de D1 : « sur des demandes variées, l'agent choisit les mêmes outils que le workflow fixe ».", "",
           "## Dossiers de l'agent", "",
           "| Dossier | Demande | Appels Bedrock | Jetons entrée | Jetons sortie | Corrections demandées | Affirmations | Valeurs reliées | Contrôle |",
           "|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for k, d in agents.items():
        a, v = d["aws"], d["verification"]
        out.append(f"| `{k}` | {d['demande']} | {len(a['appels'])} | {sum(c['inputTokens'] or 0 for c in a['appels'])} | "
                   f"{sum(c['outputTokens'] or 0 for c in a['appels'])} | {a['corrections_demandees']} | {v['affirmations']} | "
                   f"{v['valeurs_reliees']} | {'conforme' if v['ok'] else 'en échec'} |")
    out += ["", "## Scénarios de démonstration : outils de l'agent face au workflow fixe", "",
            "| Scénario | Appels communs | Ajoutés par l'agent | Absents chez l'agent |", "|---|---|---|---|"]
    for k, ref in REFERENCE.items():
        if k in dossiers and ref in dossiers:
            ag, wf = calls(dossiers[k]), calls(dossiers[ref])
            out.append(f"| `{k}` / `{ref}` | {listing(ag & wf)} | {listing(ag - wf)} | {listing(wf - ag)} |")
    out += ["", "## Demandes libres : parcours choisis par l'agent, sans workflow fixe correspondant", "",
            "| Dossier | Outils appelés |", "|---|---|"]
    for k, d in agents.items():
        if k not in REFERENCE:
            out.append(f"| `{k}` | {listing(calls(d))} |")
    out += ["", "## Lecture", "",
            "- Scénarios de démonstration : les hypothèses fournies (portefeuille, parts étudiées, seuil, panier) dictent presque le parcours ; "
            "l'agent y suit le workflow fixe à quelques appels près. Sur ces demandes, le workflow fixe suffit et ne coûte aucun jeton.",
            "- Demandes libres : l'agent compose un parcours propre à chaque demande (comparaison d'actifs sans portefeuille, hypothèses posées "
            "et déclarées, erreur d'outil rapportée) ; aucun workflow fixe ne les couvre.",
            "- Limite : un dossier par demande, un seul modèle ; la variabilité d'une exécution à l'autre n'est pas mesurée ici.", ""]
    sys.stdout.write("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
