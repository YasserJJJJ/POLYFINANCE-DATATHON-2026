"""Essai 9 — les événements qu'une interface peut suivre. Un appel de modèle (en flux), dans l'agent 3.

Le graphe pose une question (interruption), reçoit la réponse, émet des événements d'avancement,
puis l'agent 3 rédige une phrase par Amazon Bedrock : les fragments du texte arrivent en mode « messages ».
"""
import json
from collections import Counter

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.types import Command, interrupt

from commun import SORTIES, EntreeAgent2, EntreeAgent3, Etat, construire, fil, modele, noeuds

import sys

ESSAI = "essai09"
MODES = ["updates", "values", "custom", "messages", "tasks", "checkpoints"]
# Budget de jetons de l'agent 3. Avec 60, le modèle a épuisé son budget en réflexion et n'a rendu aucun texte.
BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 400


def texte(contenu) -> str:
    if isinstance(contenu, str):
        return contenu
    return "".join(b.get("text", "") for b in contenu if isinstance(b, dict) and b.get("type") == "text")


def types_de_blocs(contenu) -> list:
    return ["texte"] if isinstance(contenu, str) else sorted({b.get("type") for b in contenu if isinstance(b, dict)})


def fonctions() -> dict:
    f = noeuds(ESSAI)
    calcul = f["agent2"]

    def agent0(etat: Etat) -> dict:
        if etat.get("montant") is None:
            reponse = interrupt({"question": "Quel montant envisagez-vous d'investir ?", "champ": "montant"})
            return {"montant": float(reponse), "theme": "volatilité", "journal": ["agent0"]}
        return {}

    def agent2(etat: EntreeAgent2) -> dict:
        ecrire = get_stream_writer()
        ecrire({"type": "avancement", "role": "agent2", "etape": "calcul lancé"})
        resultat = calcul(etat)
        ecrire({"type": "avancement", "role": "agent2", "etape": "calcul terminé", "resultat": resultat["calcul"]})
        return resultat

    def agent3(etat: EntreeAgent3) -> dict:
        reponse = modele(max_tokens=BUDGET).invoke(
            f"Écris une seule phrase courte en français : le dixième du montant vaut {etat['calcul']['dixieme_du_montant']} $.")
        return {"restitution": texte(reponse.content),
                "journal": [f"agent3 : budget {BUDGET} jetons ; arrêt = {reponse.response_metadata.get('stopReason')} ; "
                            f"jetons = {reponse.usage_metadata} ; blocs = {types_de_blocs(reponse.content)}"]}

    f.update(agent0=agent0, agent2=agent2, agent3=agent3)
    return f


def resume(mode, charge):
    if mode == "updates":
        return {k: ([i.value for i in v] if k == "__interrupt__" else sorted(v) if isinstance(v, dict) else str(v)[:80])
                for k, v in charge.items()}
    if mode == "values":
        return {"cles": sorted(charge)}
    if mode == "messages":
        fragment, meta = charge
        return {"fragment": texte(fragment.content), "blocs": types_de_blocs(fragment.content), "noeud": meta.get("langgraph_node")}
    if mode == "tasks":
        return {"noeud": charge.get("name"), "fin": "result" in charge or "error" in charge, "cles": sorted(charge)}
    if mode == "checkpoints":
        return {"suivants": charge.get("next"), "pas": (charge.get("metadata") or {}).get("step")}
    return charge


if __name__ == "__main__":
    graphe = construire(ESSAI, checkpointer=InMemorySaver(), fonctions=fonctions())
    config = fil("etude-interface")
    evenements = []
    for entree in ({"demande": "Investir dans Tesla"}, Command(resume="5000")):
        evenements.append({"mode": "(appelant)", "resume": "envoi de la demande" if isinstance(entree, dict) else "envoi de la réponse de la personne"})
        for mode, charge in graphe.stream(entree, config, stream_mode=MODES):
            evenements.append({"mode": mode, "resume": resume(mode, charge)})

    with open(SORTIES / f"essai09_evenements_budget{BUDGET}.jsonl", "w") as f:
        for e in evenements:
            f.write(json.dumps(e, ensure_ascii=False, default=str) + "\n")
    print("nombre d'événements par mode :", dict(Counter(e["mode"] for e in evenements)))
    for e in evenements:
        if e["mode"] in ("(appelant)", "updates", "custom", "messages"):
            print(f"  {e['mode']:<11} {json.dumps(e['resume'], ensure_ascii=False, default=str)[:170]}")
    print("exemple « tasks »       :", next(e["resume"] for e in evenements if e["mode"] == "tasks"))
    print("exemple « checkpoints » :", next(e["resume"] for e in evenements if e["mode"] == "checkpoints"))
    final = graphe.get_state(config).values
    print("restitution finale :", repr(final["restitution"]))
    print("trace de l'agent 3 :", final["journal"][-1])
