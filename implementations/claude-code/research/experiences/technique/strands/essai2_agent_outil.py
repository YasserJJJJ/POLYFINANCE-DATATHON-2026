"""Essai 2 : un agent Strands sur Bedrock (profil alphaforge) avec un outil Python.

Question : l'appel passe-t-il, et récupère-t-on l'identifiant de requête AWS et les jetons
de chaque appel ? Deux appels de modèle attendus (demande d'outil, puis réponse).

Relance : uv run --with strands-agents python research/experiences/technique/strands/essai2_agent_outil.py
"""
import json

import commun
from strands import Agent, tool
from strands.hooks import AfterModelCallEvent, HookProvider

APPELS_OUTIL = []


@tool
def pire_baisse(symbole: str) -> str:
    """Renvoie la pire baisse observée d'un titre (valeur FICTIVE d'essai), en pourcentage."""
    APPELS_OUTIL.append(symbole)
    return json.dumps({"symbole": symbole, "pire_baisse_pct": -43.2, "fictif": True})


class Observateur(HookProvider):
    """Ce que Strands donne après chaque appel de modèle."""

    def register_hooks(self, registry, **kwargs):
        registry.add_callback(AfterModelCallEvent, self.apres)

    def apres(self, event: AfterModelCallEvent):
        r = event.stop_response
        print("  crochet AfterModelCallEvent : raison d'arrêt =", r.stop_reason if r else None,
              "| blocs =", [list(b)[0] for b in r.message["content"]] if r else None,
              "| exception =", event.exception)


agent = Agent(
    model=commun.modele("essai2"),
    tools=[pire_baisse],
    system_prompt="Tu réponds en une phrase. Tu n'inventes aucun chiffre : tu appelles l'outil.",
    callback_handler=None,
    hooks=[Observateur()],
)
res = agent("Quelle est la pire baisse de TSLA ?")
print("raison d'arrêt :", res.stop_reason)
print("réponse :", str(res).strip())
print("outil exécuté avec :", APPELS_OUTIL)
print("jetons cumulés selon Strands :", res.metrics.accumulated_usage)
print("nombre de cycles selon Strands :", res.metrics.cycle_count)
inv = res.metrics.agent_invocations[-1] if res.metrics.agent_invocations else None
print("détail par cycle selon Strands :", [getattr(c, "usage", c) for c in getattr(inv, "cycles", [])])
print("un identifiant de requête AWS dans le résultat Strands ?",
      "RequestId" in json.dumps(res.metrics.get_summary(), default=str) or "request_id" in json.dumps(res.metrics.get_summary(), default=str))
commun.bilan("essai2")
