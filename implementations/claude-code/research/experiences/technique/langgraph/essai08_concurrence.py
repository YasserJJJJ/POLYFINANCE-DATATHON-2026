"""Essai 8 — deux écritures concurrentes sur le même fil. Aucun appel de modèle.

A. Deux écritures successives qui nomment la même tête : la seconde (tête périmée) est-elle refusée ?
B. Deux processus écrivent au même instant depuis la tête qu'ils ont lue.
C. Deux processus lancent le graphe entier au même instant sur le même fil.
"""
import json
import subprocess
import sys
import time

from commun import DEMANDE, compteurs, construire, fil, remise_a_zero, sauvegarde

ESSAI, BASE = "essai08", "essai08.sqlite"
ESSAI_C, BASE_C = "essai08_lancements", "essai08_lancements.sqlite"


def ident(config):
    return (config or {}).get("configurable", {}).get("checkpoint_id")


def ecrivain(nom, valeur, instant):
    graphe = construire(ESSAI, checkpointer=sauvegarde(BASE))
    tete = graphe.get_state(fil("etude-1")).config  # la tête que cet écrivain prolonge
    time.sleep(max(0.0, float(instant) - time.time()))
    try:
        ecrit = graphe.update_state(tete, {"montant": float(valeur), "journal": [f"écriture de {nom}"]}, as_node="agent3")
        print(json.dumps({"ecrivain": nom, "tete_lue": ident(tete), "point_ecrit": ident(ecrit), "erreur": None}))
    except Exception as e:
        print(json.dumps({"ecrivain": nom, "tete_lue": ident(tete), "erreur": f"{type(e).__name__}: {e}"[:200]}))


def lanceur(nom, instant):
    graphe = construire(ESSAI_C, checkpointer=sauvegarde(BASE_C), pause=0.15)
    time.sleep(max(0.0, float(instant) - time.time()))
    try:
        r = graphe.invoke({"demande": DEMANDE.replace("5000", nom)}, fil("etude-2"))
        print(json.dumps({"lanceur": nom, "restitution": r["restitution"], "journal": r["journal"], "erreur": None}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"lanceur": nom, "erreur": f"{type(e).__name__}: {e}"[:300]}, ensure_ascii=False))


def ensemble(*commandes):
    instant = str(time.time() + 2.5)  # départ commun, le temps que les processus s'initialisent
    procs = [subprocess.Popen([sys.executable, __file__, *c, instant], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             for c in commandes]
    for p in procs:
        sortie, erreurs = p.communicate()
        print("  ", sortie.strip() or erreurs.strip()[-300:])


if __name__ == "__main__":
    if sys.argv[1:2] == ["ecrivain"]:
        ecrivain(*sys.argv[2:5])
    elif sys.argv[1:2] == ["lanceur"]:
        lanceur(*sys.argv[2:4])
    else:
        remise_a_zero(ESSAI)
        graphe = construire(ESSAI, checkpointer=sauvegarde(BASE, neuf=True))
        config = fil("etude-1")
        graphe.invoke({"demande": DEMANDE}, config)

        print("A. deux écritures successives qui nomment la même tête")
        tete = graphe.get_state(config).config
        e1 = graphe.update_state(tete, {"montant": 1111.0, "journal": ["écriture 1"]}, as_node="agent3")
        try:
            e2 = graphe.update_state(tete, {"montant": 2222.0, "journal": ["écriture 2 (tête périmée)"]}, as_node="agent3")
            p1, p2 = graphe.get_state(e1), graphe.get_state(e2)
            dernier = graphe.get_state(config)
            print(f"   seconde écriture acceptée ; parents : {ident(p1.parent_config) == ident(tete)} et {ident(p2.parent_config) == ident(tete)} (même tête)")
            print(f"   dernier état du fil : montant = {dernier.values['montant']} ; journal = {dernier.values['journal'][-2:]}")
            print("   l'écriture 1 figure-t-elle dans le dernier état ?", "écriture 1" in dernier.values["journal"])
        except Exception as e:
            print("   seconde écriture refusée :", type(e).__name__, str(e)[:200])

        print("B. deux processus écrivent au même instant")
        ensemble(("ecrivain", "P1", "3333"), ("ecrivain", "P2", "4444"))
        dernier = graphe.get_state(config)
        print(f"   dernier état du fil : montant = {dernier.values['montant']} ; journal = {dernier.values['journal'][-2:]}")
        print("   points du fil :", len(list(graphe.get_state_history(config))))

        print("C. deux processus lancent le graphe au même instant sur le même fil")
        remise_a_zero(ESSAI_C)
        saver_c = sauvegarde(BASE_C, neuf=True)
        saver_c.setup()
        ensemble(("lanceur", "6000"), ("lanceur", "7000"))
        graphe_c = construire(ESSAI_C, checkpointer=saver_c)
        historique = list(graphe_c.get_state_history(fil("etude-2")))
        dernier = graphe_c.get_state(fil("etude-2"))
        print("   exécutions par nœud :", compteurs(ESSAI_C))
        print(f"   points du fil : {len(historique)} ; dernier état : {dernier.values.get('restitution')} ; journal = {dernier.values.get('journal')}")
        enfants = {}
        for s in historique:
            enfants.setdefault(ident(s.parent_config), []).append(ident(s.config))
        print("   points ayant plusieurs enfants (lignes parallèles non déclarées) :", sum(len(v) > 1 for v in enfants.values()))
