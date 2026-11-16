"""Éléments communs aux essais LangGraph. Expérience technique, pas le produit.

Les quatre nœuds sont du code déterministe sans modèle : les essais 3 à 8 mesurent
le moteur (enchaînement, reprise, historique, bifurcation), pas la qualité d'un agent.
"""
import operator
import os
import re
import sys
import time
from pathlib import Path
from typing import Annotated, TypedDict

# Télémétrie : LangSmith (dépendance obligatoire de langchain-core) ne trace que si
# ces variables l'activent. On force l'arrêt avant tout import de langchain / langgraph.
# (L'essai 10 pose ESSAI_TELEMETRIE_PAR_DEFAUT=1 pour observer le comportement sans ce réglage.)
if os.environ.get("ESSAI_TELEMETRIE_PAR_DEFAUT") != "1":
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

ICI = Path(__file__).resolve().parent
SORTIES = ICI / "sorties"
SORTIES.mkdir(exist_ok=True)

MODELE = "global.anthropic.claude-haiku-5-5"
PROFIL, REGION = "alphaforge", "us-east-1"
DEMANDE = "Investir 5000 $ ; thème : volatilité"


# --- Compteurs d'exécution réelle des nœuds (une ligne par exécution, fiable entre processus) ---

def noter_execution(essai: str, noeud: str) -> None:
    with open(SORTIES / f"executions_{essai}.log", "a") as f:
        f.write(f"{noeud}\t{os.getpid()}\t{time.time():.3f}\n")


def compteurs(essai: str) -> dict:
    chemin = SORTIES / f"executions_{essai}.log"
    c: dict = {}
    if chemin.exists():
        for ligne in chemin.read_text().splitlines():
            nom = ligne.split("\t")[0]
            c[nom] = c.get(nom, 0) + 1
    return dict(sorted(c.items()))


def remise_a_zero(essai: str) -> None:
    (SORTIES / f"executions_{essai}.log").unlink(missing_ok=True)


def difference(apres: dict, avant: dict) -> dict:
    return {k: apres.get(k, 0) - avant.get(k, 0) for k in sorted(set(apres) | set(avant))}


# --- État typé partagé et entrées déclarées de chaque rôle ---

class Etat(TypedDict, total=False):
    demande: str          # texte tel que saisi
    montant: float        # fait déclaré, lu par l'analyse seulement
    theme: str            # sujet de recherche, lu par la recherche seulement
    fiches: list          # écrit par l'agent 1
    calcul: dict          # écrit par l'agent 2
    restitution: str      # écrit par l'agent 3
    journal: Annotated[list, operator.add]   # réducteur : ajout seul


class EntreeAgent0(TypedDict, total=False):
    demande: str


class EntreeAgent1(TypedDict, total=False):
    theme: str


class EntreeAgent2(TypedDict, total=False):
    montant: float


class EntreeAgent3(TypedDict, total=False):
    fiches: list
    calcul: dict


def noeuds(essai: str, pause: float = 0.0) -> dict:
    """Quatre rôles en miniature. Chaque nœud ne reçoit que les clés de son entrée déclarée."""

    def agent0(etat: EntreeAgent0) -> dict:
        noter_execution(essai, "agent0")
        time.sleep(pause)
        montant = re.search(r"(\d+)\s*\$", etat["demande"])
        theme = re.search(r"thème\s*:\s*(\w+)", etat["demande"])
        return {"montant": float(montant.group(1)), "theme": theme.group(1),
                "journal": ["agent0 : faits déclarés extraits"]}

    def agent1(etat: EntreeAgent1) -> dict:
        noter_execution(essai, "agent1")
        time.sleep(pause)
        return {"fiches": [f"fiche sur « {etat['theme']} »"],
                "journal": [f"agent1 : recherche sur {etat['theme']}"]}

    def agent2(etat: EntreeAgent2) -> dict:
        noter_execution(essai, "agent2")
        time.sleep(pause)
        return {"calcul": {"dixieme_du_montant": etat["montant"] / 10},
                "journal": [f"agent2 : calcul pour {etat['montant']}"]}

    def agent3(etat: EntreeAgent3) -> dict:
        noter_execution(essai, "agent3")
        time.sleep(pause)
        return {"restitution": f"{len(etat['fiches'])} fiche(s) ; dixième du montant = "
                               f"{etat['calcul']['dixieme_du_montant']}",
                "journal": ["agent3 : restitution préparée"]}

    return {"agent0": agent0, "agent1": agent1, "agent2": agent2, "agent3": agent3}


def construire(essai: str, forme: str = "chaine", checkpointer=None, cache=None,
               avec_cache: bool = False, pause: float = 0.0, fonctions: dict | None = None):
    """Graphe de quatre nœuds. forme = « chaine » (0→1→2→3) ou « losange » (0→{1,2}→3)."""
    from langgraph.graph import END, START, StateGraph
    from langgraph.types import CachePolicy

    g = StateGraph(Etat)
    for nom, f in (fonctions or noeuds(essai, pause)).items():
        g.add_node(nom, f, cache_policy=CachePolicy() if avec_cache else None)
    g.add_edge(START, "agent0")
    if forme == "chaine":
        g.add_edge("agent0", "agent1")
        g.add_edge("agent1", "agent2")
        g.add_edge("agent2", "agent3")
    else:
        g.add_edge("agent0", "agent1")
        g.add_edge("agent0", "agent2")
        g.add_edge(["agent1", "agent2"], "agent3")
    g.add_edge("agent3", END)
    return g.compile(checkpointer=checkpointer, cache=cache)


def sauvegarde(nom_base: str, neuf: bool = False):
    """Point de reprise sur un fichier SQLite du dossier sorties/."""
    import sqlite3

    from langgraph.checkpoint.sqlite import SqliteSaver

    chemin = SORTIES / nom_base
    if neuf:
        for suffixe in ("", "-wal", "-shm"):
            Path(str(chemin) + suffixe).unlink(missing_ok=True)
    return SqliteSaver(sqlite3.connect(str(chemin), check_same_thread=False))


def fil(nom: str, point: str | None = None) -> dict:
    c = {"configurable": {"thread_id": nom}}
    if point:  # « checkpoint_ns » est exigé par update_state (KeyError sinon), pas par get_state
        c["configurable"].update(checkpoint_id=point, checkpoint_ns="")
    return c


def point_apres(graphe, config: dict, suivants: tuple):
    """Point de reprise de l'historique dont les nœuds suivants sont ceux indiqués (le plus ancien)."""
    trouves = [s for s in graphe.get_state_history(config) if tuple(sorted(s.next)) == tuple(sorted(suivants))]
    return trouves[-1]


# --- Route d'inférence : boto3, profil « alphaforge », us-east-1, Amazon Bedrock (API Converse) ---

def modele(max_tokens: int = 120, **options):
    import boto3
    from langchain_aws import ChatBedrockConverse

    client = boto3.Session(profile_name=PROFIL, region_name=REGION).client("bedrock-runtime")

    def _compter(**_):  # une ligne par requête HTTP réellement envoyée à Bedrock
        with open(SORTIES / "appels_bedrock.log", "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')}\t{Path(sys.argv[0]).name}\n")

    client.meta.events.register("before-send.bedrock-runtime", _compter)
    return ChatBedrockConverse(client=client, model=MODELE, provider="anthropic",
                               region_name=REGION, max_tokens=max_tokens, **options)
