"""Essai 5 : une limite de tours.

L'outil oblige à enchaîner quatre appels (chaque réponse donne le code du suivant).
On plafonne à deux tours : limits={"turns": 2}. Deux appels de modèle attendus.

Relance : uv run --with strands-agents python research/experiences/technique/strands/essai5_limite_de_tours.py
"""
import commun
from strands import Agent, tool

SUITE = {"A": "B", "B": "C", "C": "D", "D": "FIN"}
VUS = []


@tool
def suivant(code: str) -> str:
    """Renvoie le code suivant de la chaîne. À rappeler avec le code reçu, jusqu'à recevoir FIN."""
    VUS.append(code)
    return SUITE.get(code, "FIN")


agent = Agent(model=commun.modele("essai5"), tools=[suivant], callback_handler=None,
              system_prompt="Tu suis la chaîne un appel à la fois, puis tu dis « terminé ».")
res = agent("Commence par suivant(code='A') et continue jusqu'à FIN.", limits={"turns": 2})
print("raison d'arrêt :", res.stop_reason)
print("codes réellement demandés à l'outil :", VUS)
print("cycles selon Strands :", res.metrics.cycle_count)
print("dernier message :", res.message["role"], [list(b)[0] for b in res.message["content"]])
print("historique :", [(m["role"], [list(b)[0] for b in m["content"]]) for m in agent.messages])
print("jetons cumulés :", res.metrics.accumulated_usage)
commun.bilan("essai5")
