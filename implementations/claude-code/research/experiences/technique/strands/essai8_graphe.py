"""Essai 8 : dans un graphe Strands de deux agents, ce que reçoit exactement le nœud aval.

Nœud « recherche » (sortie à structure imposée) -> nœud « analyse ».
L'entrée du nœud aval est journalisée telle que le modèle la reçoit
(sorties/essai8_entree_noeud_aval.json). Deux appels de modèle attendus.

État au 15 novembre : deux passages faits, tous deux arrêtés par MaxTokensReachedException
(plafond de 300 jetons trop bas : le raisonnement du modèle consomme la sortie), le premier dans
« recherche », le second dans « analyse » après que l'entrée du nœud aval a été journalisée.
Les deux plafonds sont maintenant à 900 ; CETTE version n'a pas été relancée (budget d'appels).
Le passage complet d'un graphe est dans essai8b_reprise_graphe.py.

Relance : uv run --with strands-agents python research/experiences/technique/strands/essai8_graphe.py
"""
import json

import commun
from pydantic import BaseModel, Field
from strands import Agent
from strands.hooks import BeforeModelCallEvent, HookProvider
from strands.multiagent import GraphBuilder

ENTREE = commun.SORTIES / "essai8_entree_noeud_aval.json"


class FichePreuve(BaseModel):
    """Fiche de preuve (essai)."""

    affirmation: str = Field(description="Une phrase")
    empreinte_source: str = Field(description="Recopie exactement : sha256:abc123")
    soutien: str = Field(description="soutient, soutient en partie, ne soutient pas")


class JournalEntree(HookProvider):
    def register_hooks(self, registry, **kwargs):
        registry.add_callback(BeforeModelCallEvent, self.noter)

    def noter(self, event: BeforeModelCallEvent):
        ENTREE.write_text(json.dumps({"consigne_systeme": event.agent.system_prompt, "messages": event.agent.messages},
                                     ensure_ascii=False, indent=1, default=str), encoding="utf-8")


recherche = Agent(name="agent1_recherche", model=commun.modele("essai8-recherche", max_tokens=900), callback_handler=None,
                  structured_output_model=FichePreuve,
                  system_prompt="Tu remplis la fiche demandée, sans autre texte. Contenu fictif d'essai.")
analyse = Agent(name="agent2_analyse", model=commun.modele("essai8-analyse", max_tokens=900), callback_handler=None,
                hooks=[JournalEntree()], system_prompt="Tu réponds en une phrase.")

b = GraphBuilder()
b.add_node(recherche, "recherche")
b.add_node(analyse, "analyse")
b.add_edge("recherche", "analyse")
b.set_entry_point("recherche")
graphe = b.build()

res = graphe("La concentration sur un seul titre augmente-t-elle la dispersion des issues ? Source d'essai : sha256:abc123.")
print("statut du graphe :", res.status)
print("ordre d'exécution :", [n.node_id for n in res.execution_order])
r = res.results["recherche"].result
print("sortie structurée du nœud amont (objet Python) :", repr(r.structured_output))
print("\nENTRÉE EXACTE du nœud aval (messages envoyés au modèle) :")
print(ENTREE.read_text(encoding="utf-8"))
print("réponse du nœud aval :", str(res.results["analyse"].result).strip()[:240])
print("jetons cumulés du graphe :", res.accumulated_usage)
commun.bilan("essai8")
