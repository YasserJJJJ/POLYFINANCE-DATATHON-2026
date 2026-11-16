"""Essai 4 : outils disjoints par rôle, et crochet qui refuse et journalise un appel non autorisé.

A. Deux agents aux outils disjoints : chacun ne voit que les siens (sans appel de modèle).
B. Un agent monté PAR ERREUR avec un outil d'un autre rôle : le crochet refuse l'appel,
   la fonction n'est pas exécutée, le refus est journalisé (2 appels de modèle).
C. Appel direct agent.tool.xxx(...) : le crochet s'applique-t-il aussi ? (sans appel de modèle)

Relance : uv run --with strands-agents python research/experiences/technique/strands/essai4_outils_par_role.py
"""
import commun
from strands import Agent, tool
from strands.hooks import BeforeToolCallEvent, HookProvider

REFUS = commun.SORTIES / "essai4_refus.jsonl"
EXECUTIONS = []


@tool
def chercher_fiche(question: str) -> str:
    """Cherche une fiche de preuve dans la bibliothèque (réponse FICTIVE d'essai)."""
    EXECUTIONS.append(("chercher_fiche", question))
    return "Fiche F-001 (fictive) : la concentration augmente la dispersion des issues."


@tool
def calculer_volatilite(symbole: str) -> str:
    """Calcule la volatilité annualisée d'un titre (valeur FICTIVE d'essai)."""
    EXECUTIONS.append(("calculer_volatilite", symbole))
    return "volatilité annualisée fictive : 55 %"


OUTILS_PAR_ROLE = {"agent1_recherche": {"chercher_fiche"}, "agent2_analyse": {"calculer_volatilite"}}


class Portier(HookProvider):
    """Refuse tout outil hors de la liste du rôle, et l'écrit au journal."""

    def __init__(self, role: str):
        self.role = role

    def register_hooks(self, registry, **kwargs):
        registry.add_callback(BeforeToolCallEvent, self.verifier)

    def verifier(self, event: BeforeToolCallEvent):
        nom = event.tool_use["name"]
        if nom not in OUTILS_PAR_ROLE[self.role]:
            commun.ecrire(REFUS, {"role": self.role, "outil": nom, "entree": event.tool_use.get("input"), "decision": "refus"})
            event.cancel_tool = f"Outil « {nom} » interdit au rôle {self.role}."


def agent(role, outils):
    return Agent(name=role, model=commun.modele("essai4"), tools=outils, hooks=[Portier(role)], callback_handler=None,
                 system_prompt="Tu réponds en une phrase.")


print("A. outils vus par chaque rôle")
a1, a2 = agent("agent1_recherche", [chercher_fiche]), agent("agent2_analyse", [calculer_volatilite])
print("   agent1 :", a1.tool_names, "| agent2 :", a2.tool_names)
print("   spécifications envoyées au modèle pour agent1 :", [s["name"] for s in a1.tool_registry.get_all_tool_specs()])

print("\nB. agent1 monté par erreur avec les deux outils ; on lui demande un calcul")
fautif = agent("agent1_recherche", [chercher_fiche, calculer_volatilite])
res = fautif("Utilise l'outil calculer_volatilite pour TSLA et donne le résultat.")
print("   raison d'arrêt :", res.stop_reason, "| réponse :", str(res).strip()[:260])
print("   fonctions réellement exécutées :", EXECUTIONS)
for m in fautif.messages:
    for b in m["content"]:
        if "toolResult" in b:
            print("   résultat d'outil vu par le modèle :", b["toolResult"]["status"], "|", b["toolResult"]["content"])
print("   journal des refus :", open(REFUS, encoding="utf-8").read().strip().splitlines()[-1] if REFUS.exists() else "VIDE")

print("\nC. appel direct, sans modèle : fautif.tool.calculer_volatilite(symbole='TSLA')")
try:
    r = fautif.tool.calculer_volatilite(symbole="TSLA")
    print("   résultat :", r)
except Exception as e:
    print("   EXCEPTION :", type(e).__name__, str(e)[:200])
print("   fonctions réellement exécutées :", EXECUTIONS)
commun.bilan("essai4")
