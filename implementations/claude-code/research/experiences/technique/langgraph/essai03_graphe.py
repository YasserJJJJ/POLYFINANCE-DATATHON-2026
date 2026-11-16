"""Essai 3 — graphe de quatre nœuds à état typé, point de reprise sur SQLite. Aucun appel de modèle."""
import sqlite3
from typing import TypedDict

from pydantic import BaseModel

from commun import DEMANDE, SORTIES, compteurs, construire, fil, remise_a_zero, sauvegarde

ESSAI = "essai03"


def essai_typage() -> None:
    """Ce que le moteur contrôle vraiment sur les types de l'état."""
    from langgraph.graph import END, START, StateGraph

    def monter(schema, *fonctions):
        g = StateGraph(schema)
        precedent = START
        for i, f in enumerate(fonctions):
            g.add_node(f"n{i}", f)
            g.add_edge(precedent, f"n{i}")
            precedent = f"n{i}"
        g.add_edge(precedent, END)
        return g.compile()

    def tenter(titre, graphe):
        try:
            print(f"  {titre} : accepté, état final = {graphe.invoke({'montant': 1.0})}")
        except Exception as e:
            print(f"  {titre} : refusé par {type(e).__name__} : {str(e)[:140]}")

    class EtatDict(TypedDict):
        montant: float

    class EtatPydantic(BaseModel):
        montant: float

    tenter("TypedDict, un nœud écrit un texte dans un champ « float »",
           monter(EtatDict, lambda e: {"montant": "beaucoup"}))
    tenter("TypedDict, un nœud écrit une clé absente du schéma",
           monter(EtatDict, lambda e: {"autre": 1}))
    tenter("Pydantic, mauvais type écrit par le dernier nœud",
           monter(EtatPydantic, lambda e: {"montant": "beaucoup"}))
    tenter("Pydantic, mauvais type écrit puis lu par un nœud suivant",
           monter(EtatPydantic, lambda e: {"montant": "beaucoup"}, lambda e: {}))


if __name__ == "__main__":
    remise_a_zero(ESSAI)
    graphe = construire(ESSAI, checkpointer=sauvegarde("essai03.sqlite", neuf=True))
    config = fil("etude-1")
    final = graphe.invoke({"demande": DEMANDE}, config)
    print("état final :", final)
    print("exécutions par nœud :", compteurs(ESSAI))

    # Une autre instance du graphe, sur le même fichier, retrouve l'état.
    autre = construire(ESSAI, checkpointer=sauvegarde("essai03.sqlite"))
    relu = autre.get_state(config)
    print("état relu identique :", relu.values == final, "; nœuds suivants :", relu.next)
    autre.invoke(None, config)  # relancer un fil terminé ne doit rien refaire
    print("exécutions après relance d'un fil terminé :", compteurs(ESSAI))

    con = sqlite3.connect(SORTIES / "essai03.sqlite")
    for (nom,) in con.execute("select name from sqlite_master where type='table'"):
        colonnes = [c[1] for c in con.execute(f"pragma table_info({nom})")]
        print(f"table {nom} : {con.execute(f'select count(*) from {nom}').fetchone()[0]} lignes ; colonnes {colonnes}")
    print("identifiants des points :", [r[0] for r in con.execute("select checkpoint_id from checkpoints order by checkpoint_id")][:3], "…")
    print("format d'un point enregistré :", con.execute("select type, length(checkpoint) from checkpoints limit 1").fetchone())

    print("contrôle des types par le moteur :")
    essai_typage()
