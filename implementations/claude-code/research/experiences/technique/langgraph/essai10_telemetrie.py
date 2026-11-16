"""Essai 10 — télémétrie par défaut : quels hôtes le processus contacte-t-il ? Un appel de modèle.

On observe le comportement SANS le réglage de commun.py (variables de traçage laissées telles quelles),
en enregistrant toute résolution de nom et toute connexion sortante.
"""
import os
import socket
import threading
import time

os.environ["ESSAI_TELEMETRIE_PAR_DEFAUT"] = "1"  # commun.py ne force alors rien

noms_resolus, connexions = [], []
_resoudre, _connecter = socket.getaddrinfo, socket.socket.connect


def _espion_resolution(hote, *a, **k):
    noms_resolus.append(str(hote))
    return _resoudre(hote, *a, **k)


def _espion_connexion(self, adresse):
    connexions.append(str(adresse))
    return _connecter(self, adresse)


socket.getaddrinfo = _espion_resolution
socket.socket.connect = _espion_connexion


def etape(titre):
    print(f"{titre:<58} noms résolus = {sorted(set(noms_resolus))} ; connexions = {len(connexions)}")


if __name__ == "__main__":
    variables = sorted(v for v in os.environ if v.startswith(("LANGSMITH", "LANGCHAIN", "LANGGRAPH", "OTEL_")))
    print("variables de traçage présentes dans l'environnement (noms seulement) :", variables or "aucune")

    import langchain_aws  # noqa: F401
    import langchain_core  # noqa: F401
    import langgraph  # noqa: F401
    import langsmith
    from langsmith import utils as ls_utils
    etape("après import de langgraph, langchain-core, langchain-aws")

    from commun import DEMANDE, construire, fil, modele, sauvegarde
    graphe = construire("essai10", checkpointer=sauvegarde("essai10.sqlite", neuf=True))
    graphe.invoke({"demande": DEMANDE}, fil("etude-1"))
    list(graphe.get_state_history(fil("etude-1")))
    time.sleep(1.5)  # laisser le temps à un éventuel envoi en arrière-plan
    etape("après un graphe local complet (SQLite)")

    print("traçage LangSmith actif par défaut :", ls_utils.tracing_is_enabled(),
          "; version de langsmith :", langsmith.__version__)
    modele(max_tokens=20).invoke("Réponds par le seul mot : prêt.")
    time.sleep(1.5)
    etape("après un appel de modèle par Bedrock")
    tiers = sorted({n for n in noms_resolus if not n.endswith(".amazonaws.com")})
    print("hôtes hors amazonaws.com :", tiers or "aucun")
    print("fils d'exécution encore vivants :", sorted(t.name for t in threading.enumerate()))
