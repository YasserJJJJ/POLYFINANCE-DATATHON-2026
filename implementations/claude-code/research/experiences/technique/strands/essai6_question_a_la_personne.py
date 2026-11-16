"""Essai 6 : une interruption pour poser une question à la personne, puis la reprise (même processus).

L'outil demander_a_la_personne suspend la boucle (tool_context.interrupt). On reprend en
rappelant l'agent avec la réponse. Deux appels de modèle attendus (un avant, un après).

Relance : uv run --with strands-agents python research/experiences/technique/strands/essai6_question_a_la_personne.py
"""
import commun
from strands import Agent, tool
from strands.types.tools import ToolContext

PASSAGES = []


@tool(context=True)
def demander_a_la_personne(question: str, tool_context: ToolContext) -> str:
    """Pose une question à la personne et attend sa réponse. À utiliser quand une information nécessaire manque."""
    PASSAGES.append("corps de l'outil, avant l'interruption")
    reponse = tool_context.interrupt("question_a_la_personne", reason={"question": question})
    PASSAGES.append("corps de l'outil, après l'interruption")
    return f"Réponse de la personne : {reponse}"


agent = Agent(model=commun.modele("essai6"), tools=[demander_a_la_personne], callback_handler=None,
              system_prompt="Tu qualifies une demande. S'il manque l'horizon, tu le demandes par l'outil, puis tu réponds en une phrase.")
avant = commun.nb_appels()
res = agent("Robert veut savoir si garder 40 % de Tesla est risqué.")
print("1. raison d'arrêt :", res.stop_reason)
print("   interruptions :", [i.to_dict() for i in res.interrupts or []])
print("   appels de modèle jusqu'ici :", commun.nb_appels() - avant, "| passages :", PASSAGES)
print("   historique :", [(m["role"], [list(b)[0] for b in m["content"]]) for m in agent.messages])

print("\n   Rappel de l'agent avec un texte ordinaire au lieu d'une réponse (doit être refusé, sans appel de modèle) :")
try:
    agent("Bonjour")
except Exception as e:
    print("   EXCEPTION :", type(e).__name__, str(e)[:160])

if res.stop_reason == "interrupt":
    reponses = [{"interruptResponse": {"interruptId": i.id, "response": "7 ans"}} for i in res.interrupts]
    res2 = agent(reponses)
    print("\n2. raison d'arrêt après reprise :", res2.stop_reason)
    print("   réponse :", str(res2).strip()[:300])
    print("   appels de modèle au total :", commun.nb_appels() - avant, "| passages :", PASSAGES)
    print("   historique :", [(m["role"], [list(b)[0] for b in m["content"]]) for m in agent.messages])
commun.bilan("essai6")
