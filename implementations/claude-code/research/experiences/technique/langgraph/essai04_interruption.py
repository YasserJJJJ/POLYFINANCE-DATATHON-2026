"""Essai 4 — question à la personne, arrêt du processus, reprise dans un nouveau processus ; puis panne en plein nœud.

Trois processus distincts par scénario :
  depart  : l'agent 0 pose une question (interrupt) ; le processus s'arrête sans nettoyage ;
  reponse : un nouveau processus relit l'état, transmet la réponse ; l'agent 2 tombe en panne (os._exit) ;
  reprise : un troisième processus relance depuis le dernier point de reprise.
Le scénario est joué deux fois : durabilité par défaut (« async ») puis « sync ». Aucun appel de modèle.

    python essai04_interruption.py                 # joue tout
    python essai04_interruption.py depart defaut   # une seule phase
"""
import os
import subprocess
import sys

from langgraph.types import Command, interrupt

from commun import SORTIES, EntreeAgent2, Etat, compteurs, construire, fil, noeuds, noter_execution, remise_a_zero, sauvegarde


def noms(durabilite):
    suffixe = durabilite or "defaut"
    return f"essai04_{suffixe}", f"essai04_{suffixe}.sqlite", SORTIES / f"essai04_{suffixe}_panne_faite"


def graphe(durabilite, neuf=False):
    essai, base, temoin = noms(durabilite)
    f = noeuds(essai)
    agent2_normal = f["agent2"]

    def agent0(etat: Etat) -> dict:
        noter_execution(essai, "agent0 (début du nœud)")
        if etat.get("montant") is None:
            reponse = interrupt({"question": "Quel montant envisagez-vous d'investir ?",
                                 "champ": "montant", "nature": "inconnue nécessaire"})
            noter_execution(essai, "agent0 (après la réponse)")
            return {"montant": float(reponse), "theme": "volatilité",
                    "journal": [f"agent0 : montant déclaré {reponse}"]}
        return {"journal": ["agent0 : rien à demander"]}

    def agent2(etat: EntreeAgent2) -> dict:
        if not temoin.exists():
            noter_execution(essai, "agent2 (tué par la panne)")
            temoin.write_text("panne simulée une fois")
            os._exit(137)  # arrêt brutal au milieu du nœud
        return agent2_normal(etat)

    f.update(agent0=agent0, agent2=agent2)
    return construire(essai, checkpointer=sauvegarde(base, neuf=neuf), fonctions=f)


def phase(nom, durabilite):
    essai, _, temoin = noms(durabilite)
    config = fil("etude-question")
    options = {"durability": durabilite} if durabilite else {}
    if nom == "depart":
        remise_a_zero(essai)
        temoin.unlink(missing_ok=True)
        r = graphe(durabilite, neuf=True).invoke({"demande": "Investir dans Tesla"}, config, **options)
        print(f"[pid {os.getpid()}] question reçue par l'appelant : {[i.value for i in r['__interrupt__']]}")
        sys.stdout.flush()
        os._exit(0)  # arrêt du processus sans nettoyage
    g = graphe(durabilite)
    etat = g.get_state(config)
    questions = [i.value for t in etat.tasks for i in t.interrupts]
    import sqlite3
    base = sqlite3.connect(SORTIES / noms(durabilite)[1])
    print(f"[pid {os.getpid()}] état relu : nœuds suivants = {etat.next} ; questions en attente = {questions} ; "
          f"journal = {etat.values.get('journal')} ; points enregistrés = "
          f"{base.execute('select count(*) from checkpoints').fetchone()[0]} ; écritures en attente = "
          f"{base.execute('select count(*) from writes').fetchone()[0]}")
    sys.stdout.flush()
    if nom == "reponse":
        g.invoke(Command(resume="5000"), config, **options)  # meurt dans l'agent 2
        print("inattendu : la panne n'a pas eu lieu")
    else:
        r = g.invoke(None, config, **options)
        print(f"[pid {os.getpid()}] restitution : {r['restitution']} ; journal = {r['journal']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        phase(sys.argv[1], None if len(sys.argv) < 3 or sys.argv[2] == "defaut" else sys.argv[2])
    else:
        for durabilite in (None, "sync"):
            print(f"\n=== durabilité : {durabilite or 'par défaut (async)'} ===")
            for p in ("depart", "reponse", "reprise"):
                r = subprocess.run([sys.executable, __file__, p, durabilite or "defaut"], capture_output=True, text=True)
                print(f"-- processus « {p} », code de sortie {r.returncode}\n   {r.stdout.strip()}")
                if r.stderr.strip() and r.returncode not in (0, 137):
                    print("   erreur :", r.stderr.strip()[-500:])
            print("exécutions par nœud :", compteurs(noms(durabilite)[0]))
