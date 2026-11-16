"""Essai 11 (complément) — erreurs d'outils, outils disjoints par rôle, relance d'un nœud. Aucun appel de modèle.

Les demandes d'outil sont fabriquées à la main (comme si un modèle les avait émises) pour observer
ce que fait le moteur quand un outil échoue ou quand un rôle demande un outil qui n'est pas le sien.
"""
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import RetryPolicy

from commun import compteurs, noter_execution, remise_a_zero

ESSAI = "essai11"


@tool
def calculer_volatilite(titre: str) -> str:
    """Calcule la volatilité d'un titre (outil de l'agent 2)."""
    raise ValueError(f"série de prix absente pour {titre}")


@tool
def chercher_fiche(sujet: str) -> str:
    """Cherche une fiche de preuve (outil de l'agent 1)."""
    return f"fiche sur {sujet}"


def demande_d_outil(nom, arguments):
    return {"messages": [AIMessage(content="", tool_calls=[{"name": nom, "args": arguments, "id": "appel-1", "type": "tool_call"}])]}


def jouer(titre, noeud_outils, entree):
    g = StateGraph(MessagesState)
    g.add_node("outils", noeud_outils)
    g.add_edge(START, "outils")
    g.add_edge("outils", END)
    try:
        dernier = g.compile().invoke(entree)["messages"][-1]
        print(f"  {titre} : message rendu au modèle, statut = {getattr(dernier, 'status', None)} ; contenu = {str(dernier.content)[:150]}")
    except Exception as e:
        print(f"  {titre} : exception remontée au graphe : {type(e).__name__} : {str(e)[:120]}")


class PanneTransitoire(Exception):
    pass


if __name__ == "__main__":
    print("erreurs d'outils :")
    jouer("outil qui échoue, réglage par défaut", ToolNode([calculer_volatilite]), demande_d_outil("calculer_volatilite", {"titre": "TSLA"}))
    jouer("outil qui échoue, handle_tool_errors=True", ToolNode([calculer_volatilite], handle_tool_errors=True),
          demande_d_outil("calculer_volatilite", {"titre": "TSLA"}))
    jouer("arguments invalides, réglage par défaut", ToolNode([chercher_fiche]), demande_d_outil("chercher_fiche", {"mauvais": 1}))
    print("outils disjoints :")
    jouer("le rôle 1 demande l'outil du rôle 2", ToolNode([chercher_fiche]), demande_d_outil("calculer_volatilite", {"titre": "TSLA"}))

    print("relance d'un nœud (RetryPolicy) :")
    remise_a_zero(ESSAI)

    def fragile(etat: MessagesState) -> dict:
        noter_execution(ESSAI, "noeud_fragile")
        if compteurs(ESSAI)["noeud_fragile"] < 3:
            raise PanneTransitoire("service momentanément indisponible")
        return {"messages": [AIMessage(content="réussi au troisième essai")]}

    g = StateGraph(MessagesState)
    g.add_node("fragile", fragile, retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.01, jitter=False, retry_on=PanneTransitoire))
    g.add_edge(START, "fragile")
    g.add_edge("fragile", END)
    print("  résultat :", g.compile().invoke({"messages": []})["messages"][-1].content, "; exécutions :", compteurs(ESSAI))
