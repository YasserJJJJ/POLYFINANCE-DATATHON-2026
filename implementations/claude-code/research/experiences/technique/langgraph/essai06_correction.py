"""Essai 6 — corriger une valeur amont puis relancer : quels nœuds sont réexécutés ?

La valeur corrigée est « montant ». Seul l'agent 2 la lit ; l'agent 3 lit le résultat de l'agent 2 ;
l'agent 1 n'en dépend pas. Une invalidation sélective ne referait donc que les agents 2 et 3.
Quatre scénarios : chaîne ou losange, sans cache puis avec le cache de nœuds (CachePolicy + SqliteCache).
Aucun appel de modèle.

    python essai06_correction.py                    # joue tout
    python essai06_correction.py autre-processus    # relit le cache depuis un autre processus et un autre fil
"""
import subprocess
import sys
from pathlib import Path

from langgraph.cache.sqlite import SqliteCache

from commun import (DEMANDE, SORTIES, EntreeAgent2, compteurs, construire, difference, fil, noeuds,
                    noter_execution, point_apres, remise_a_zero, sauvegarde)


def monter(forme, avec_cache, neuf):
    essai = f"essai06_{forme}_{'avec_cache' if avec_cache else 'sans_cache'}"
    cache = None
    if avec_cache:
        chemin = SORTIES / f"{essai}_cache.sqlite"
        if neuf:
            chemin.unlink(missing_ok=True)
        cache = SqliteCache(path=str(chemin))
    graphe = construire(essai, forme=forme, checkpointer=sauvegarde(f"{essai}.sqlite", neuf=neuf),
                        cache=cache, avec_cache=avec_cache)
    return essai, graphe


def scenario(forme, avec_cache):
    essai, graphe = monter(forme, avec_cache, neuf=True)
    remise_a_zero(essai)
    config = fil("etude-1")
    graphe.invoke({"demande": DEMANDE}, config)
    c0 = compteurs(essai)

    amont = point_apres(graphe, config, ("agent1",) if forme == "chaine" else ("agent1", "agent2"))
    corrige = graphe.update_state(amont.config, {"montant": 8000.0}, as_node="agent0")
    r1 = graphe.invoke(None, corrige)
    c1 = compteurs(essai)

    retour = graphe.update_state(amont.config, {"montant": 5000.0}, as_node="agent0")
    r2 = graphe.invoke(None, retour)
    c2 = compteurs(essai)

    print(f"\n=== {forme}, {'avec' if avec_cache else 'sans'} cache de nœuds ===")
    print("première exécution               :", c0)
    print("après correction montant → 8000  :", difference(c1, c0), "→", r1["restitution"])
    print("après retour à montant = 5000    :", difference(c2, c1), "→", r2["restitution"])


def autre_processus():
    """Même graphe, même fichier de cache, nouveau processus et nouveau fil : le travail est-il refait ?"""
    essai, graphe = monter("losange", True, neuf=False)
    avant = compteurs(essai)
    r = graphe.invoke({"demande": DEMANDE}, fil("etude-d-un-autre-fil"))
    print("\n=== autre processus, autre fil, mêmes entrées, cache SQLite partagé ===")
    print("exécutions supplémentaires :", difference(compteurs(essai), avant), "→", r["restitution"])


DECALAGE = 0.0  # « version du code » du calcul ci-dessous : la changer simule une formule corrigée


def agent2_versionne(etat: EntreeAgent2) -> dict:
    noter_execution("essai06_code", "agent2")
    return {"calcul": {"dixieme_du_montant": etat["montant"] / 10 + DECALAGE},
            "journal": [f"agent2 : formule avec décalage {DECALAGE}"]}


def meme_fonction_code_change():
    """Même fonction (même nom qualifié), mêmes entrées, comportement changé : le cache sert-il l'ancien résultat ?"""
    global DECALAGE
    essai = "essai06_code"
    remise_a_zero(essai)
    chemin = SORTIES / "essai06_code_cache.sqlite"
    chemin.unlink(missing_ok=True)
    f = noeuds(essai)
    f["agent2"] = agent2_versionne
    graphe = construire(essai, forme="losange", checkpointer=sauvegarde("essai06_code.sqlite", neuf=True),
                        cache=SqliteCache(path=str(chemin)), avec_cache=True, fonctions=f)
    r1 = graphe.invoke({"demande": DEMANDE}, fil("avant-changement"))
    c1 = compteurs(essai)
    DECALAGE = 1.0
    r2 = graphe.invoke({"demande": DEMANDE}, fil("apres-changement"))
    print("\n=== même fonction, formule changée (dixième + 1), mêmes entrées, même cache ===")
    print("avant le changement :", c1, "→", r1["restitution"])
    print("après le changement :", difference(compteurs(essai), c1), "→", r2["restitution"],
          "(501.0 attendu si la nouvelle formule a tourné ; 500.0 = ancien résultat servi par le cache)")


def code_modifie():
    """Autre fonction (autre nom qualifié) branchée sous le même nom de nœud, mêmes entrées, même cache."""
    meme_fonction_code_change()
    essai = "essai06_losange_avec_cache"
    f = noeuds(essai)

    def agent2(etat: EntreeAgent2) -> dict:
        noter_execution(essai, "agent2 (autre fonction)")
        return {"calcul": {"dixieme_du_montant": etat["montant"] / 10 + 1}, "journal": ["agent2 : nouvelle formule"]}

    f["agent2"] = agent2
    graphe = construire(essai, forme="losange", checkpointer=sauvegarde("essai06_code_modifie.sqlite", neuf=True),
                        cache=SqliteCache(path=str(SORTIES / f"{essai}_cache.sqlite")), avec_cache=True, fonctions=f)
    avant = compteurs(essai)
    r = graphe.invoke({"demande": DEMANDE}, fil("etude-code-modifie"))
    print("\n=== autre fonction sous le même nom de nœud (formule : dixième + 1), mêmes entrées, même cache ===")
    print("exécutions supplémentaires :", difference(compteurs(essai), avant), "→", r["restitution"],
          "(501.0 attendu si le nouveau code a tourné)")


if __name__ == "__main__":
    if sys.argv[1:] == ["autre-processus"]:
        autre_processus()
    elif sys.argv[1:] == ["code-modifie"]:
        code_modifie()
    else:
        for forme in ("chaine", "losange"):
            for avec_cache in (False, True):
                scenario(forme, avec_cache)
        for phase in ("autre-processus", "code-modifie"):
            r = subprocess.run([sys.executable, __file__, phase], capture_output=True, text=True)
            print(r.stdout.rstrip(), r.stderr.strip()[-400:] if r.returncode else "")
