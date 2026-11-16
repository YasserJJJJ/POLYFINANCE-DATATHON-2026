"""Essai 8 bis : un graphe Strands reprend-il après une panne sans refaire le nœud déjà fait ?

Processus « a » : le nœud « recherche » s'exécute (1 appel), puis le processus est TUÉ (os._exit)
juste avant l'appel de modèle du nœud « analyse ».
Processus « b » : graphe reconstruit sur la même session ; on regarde si « recherche » est refait.
Sert aussi de passage propre pour l'essai 8 (statut, ordre, entrée du nœud aval).

Relance (dans cet ordre) :
  uv run --with strands-agents python research/experiences/technique/strands/essai8b_reprise_graphe.py a
  uv run --with strands-agents python research/experiences/technique/strands/essai8b_reprise_graphe.py b
"""
import json
import os
import shutil
import sys

import commun
from pydantic import BaseModel, Field
from strands import Agent
from strands.hooks import BeforeModelCallEvent, HookProvider
from strands.multiagent import GraphBuilder
from strands.session.file_session_manager import FileSessionManager

ETAPE = sys.argv[1]
SESSIONS = commun.SORTIES / "sessions_graphe"
ENTREE = commun.SORTIES / "essai8b_entree_noeud_aval.json"
TACHE = "La concentration sur un seul titre augmente-t-elle la dispersion des issues ? Source d'essai : sha256:abc123."


class FichePreuve(BaseModel):
    """Fiche de preuve (essai)."""

    affirmation: str = Field(description="Une phrase")
    empreinte_source: str = Field(description="Recopie exactement : sha256:abc123")
    soutien: str = Field(description="soutient, soutient en partie, ne soutient pas")


class JournalEntreePuisPanne(HookProvider):
    def register_hooks(self, registry, **kwargs):
        registry.add_callback(BeforeModelCallEvent, self.noter)

    def noter(self, event: BeforeModelCallEvent):
        ENTREE.write_text(json.dumps({"processus": ETAPE, "messages": event.agent.messages}, ensure_ascii=False, indent=1, default=str),
                          encoding="utf-8")
        if ETAPE == "a":
            print("   PANNE SIMULÉE : processus tué avant l'appel de modèle du nœud « analyse ».", flush=True)
            os._exit(17)


if ETAPE == "a" and SESSIONS.exists():
    shutil.rmtree(SESSIONS)  # dossier de cet essai uniquement

recherche = Agent(name="agent1_recherche", model=commun.modele(f"essai8b-{ETAPE}-recherche", max_tokens=900), callback_handler=None,
                  structured_output_model=FichePreuve,
                  system_prompt="Tu remplis la fiche demandée, sans autre texte. Contenu fictif d'essai.")
analyse = Agent(name="agent2_analyse", model=commun.modele(f"essai8b-{ETAPE}-analyse", max_tokens=900), callback_handler=None,
                hooks=[JournalEntreePuisPanne()], system_prompt="Tu réponds en une phrase.")

b = GraphBuilder()
b.add_node(recherche, "recherche")
b.add_node(analyse, "analyse")
b.add_edge("recherche", "analyse")
b.set_entry_point("recherche")
b.set_graph_id("graphe_essai8b")
b.set_session_manager(FileSessionManager(session_id="essai8b", storage_dir=str(SESSIONS)))
graphe = b.build()
print(f"processus {ETAPE} : état du graphe à la construction : statut = {graphe.state.status},",
      "nœuds faits =", [n.node_id for n in graphe.state.completed_nodes], flush=True)

res = graphe(TACHE)
print("statut du graphe :", res.status)
print("ordre d'exécution :", [n.node_id for n in res.execution_order])
print("nœuds faits / en échec :", res.completed_nodes, "/", res.failed_nodes)
print("sortie structurée du nœud amont, relue de la session :", repr(res.results["recherche"].result.structured_output))
print("réponse du nœud aval :", str(res.results["analyse"].result).strip()[:240])
print("jetons cumulés du graphe :", res.accumulated_usage)
print("entrée du nœud aval :", ENTREE.read_text(encoding="utf-8")[:900])
print("fichiers de session du graphe :")
for racine, _, noms in os.walk(SESSIONS):
    for n in sorted(noms):
        p = os.path.join(racine, n)
        print("     ", os.path.relpath(p, SESSIONS), os.path.getsize(p), "octets")
commun.bilan(f"essai8b-{ETAPE}")
