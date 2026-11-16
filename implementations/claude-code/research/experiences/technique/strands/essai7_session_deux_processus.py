"""Essai 7 : persistance d'une session et reprise dans un NOUVEAU processus.

Processus « a » : l'agent pose sa question à la personne (interruption), puis le processus s'arrête.
Processus « b » : un agent neuf relit la session sur disque et reprend avec la réponse.
Un appel de modèle par processus attendu.

Relance (dans cet ordre) :
  uv run --with strands-agents python research/experiences/technique/strands/essai7_session_deux_processus.py a
  uv run --with strands-agents python research/experiences/technique/strands/essai7_session_deux_processus.py b
"""
import json
import os
import shutil
import sys

import commun
from strands import Agent, tool
from strands.session.file_session_manager import FileSessionManager
from strands.types.tools import ToolContext

ETAPE = sys.argv[1]
SESSIONS = commun.SORTIES / "sessions"
RELAIS = commun.SORTIES / "essai7_interruption.json"


@tool(context=True)
def demander_a_la_personne(question: str, tool_context: ToolContext) -> str:
    """Pose une question à la personne et attend sa réponse. À utiliser quand une information nécessaire manque."""
    reponse = tool_context.interrupt("question_a_la_personne", reason={"question": question})
    return f"Réponse de la personne : {reponse}"


def fichiers():
    for racine, _, noms in os.walk(SESSIONS):
        for n in sorted(noms):
            p = os.path.join(racine, n)
            print("     ", os.path.relpath(p, SESSIONS), os.path.getsize(p), "octets")


if ETAPE == "a" and SESSIONS.exists():
    shutil.rmtree(SESSIONS)  # dossier de cet essai uniquement

agent = Agent(
    agent_id="agent0",
    model=commun.modele(f"essai7-{ETAPE}"),
    tools=[demander_a_la_personne],
    session_manager=FileSessionManager(session_id="essai7", storage_dir=str(SESSIONS)),
    callback_handler=None,
    system_prompt="Tu qualifies une demande. S'il manque l'horizon, tu le demandes par l'outil, puis tu réponds en une phrase.",
)
print(f"processus {ETAPE} (pid {os.getpid()}) : messages présents à la création de l'agent :",
      [(m["role"], [list(b)[0] for b in m["content"]]) for m in agent.messages])
etat = agent._interrupt_state  # attribut privé, lu seulement pour constater ce qui a été restauré
print("   état d'interruption restauré : activé =", etat.activated, "| interruptions =", [i.to_dict() for i in etat.interrupts.values()])

if ETAPE == "a":
    res = agent("Robert veut savoir si garder 40 % de Tesla est risqué.")
    print("   raison d'arrêt :", res.stop_reason)
    RELAIS.write_text(json.dumps([i.to_dict() for i in res.interrupts or []], ensure_ascii=False), encoding="utf-8")
    print("   fichiers de session écrits :")
    fichiers()
else:
    attendues = json.loads(RELAIS.read_text(encoding="utf-8"))
    res = agent([{"interruptResponse": {"interruptId": i["id"], "response": "7 ans"}} for i in attendues])
    print("   raison d'arrêt après reprise :", res.stop_reason)
    print("   réponse :", str(res).strip()[:240])
    print("   historique :", [(m["role"], [list(b)[0] for b in m["content"]]) for m in agent.messages])
    print("   fichiers de session après reprise :")
    fichiers()
    un = next(p for p in sorted(SESSIONS.rglob("message_*.json")))
    print("   contenu du premier fichier de message (en clair) :", un.read_text(encoding="utf-8")[:330])
commun.bilan(f"essai7-{ETAPE}")
