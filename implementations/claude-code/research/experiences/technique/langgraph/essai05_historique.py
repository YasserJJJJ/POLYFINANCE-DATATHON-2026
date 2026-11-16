"""Essai 5 — l'historique des états d'un fil, et ce qu'un point de reprise enregistre. Aucun appel de modèle."""
from commun import DEMANDE, compteurs, construire, fil, remise_a_zero, sauvegarde

ESSAI = "essai05"


def ident(config):
    return (config or {}).get("configurable", {}).get("checkpoint_id")


if __name__ == "__main__":
    remise_a_zero(ESSAI)
    saver = sauvegarde("essai05.sqlite", neuf=True)
    graphe = construire(ESSAI, checkpointer=saver)
    config = fil("etude-1")
    graphe.invoke({"demande": DEMANDE}, config)

    print("historique (du plus ancien au plus récent) :")
    for s in reversed(list(graphe.get_state_history(config))):
        print(f"  pas {s.metadata.get('step'):>2} source={s.metadata.get('source'):<5} point={ident(s.config)} "
              f"parent={ident(s.parent_config)} suivants={s.next} clés={sorted(s.values)} créé={s.created_at}")

    brut = saver.get_tuple(config)
    print("\nce qu'un point enregistre :", sorted(brut.checkpoint))
    print("versions des canaux :", brut.checkpoint["channel_versions"])
    print("métadonnées :", dict(brut.metadata))
    print("écritures en attente rattachées :", len(brut.pending_writes or []))

    # Deux exécutions identiques donnent-elles le même identifiant (adressage par le contenu) ?
    graphe.invoke({"demande": DEMANDE}, fil("etude-jumelle"))
    a, b = graphe.get_state(config), graphe.get_state(fil("etude-jumelle"))
    print("\nmêmes valeurs :", a.values == b.values, "; même identifiant :", ident(a.config) == ident(b.config),
          f"({ident(a.config)} / {ident(b.config)})")

    # Un point existant peut-il être réécrit par l'interface publique du point de reprise ?
    try:
        brut.checkpoint["channel_values"]["restitution"] = "contenu réécrit après coup"
        saver.put(brut.parent_config, brut.checkpoint, brut.metadata, {})
        relu = graphe.get_state(config)
        print("réécriture d'un point existant : acceptée ; même identifiant :", ident(relu.config) == ident(brut.config),
              "; restitution relue :", relu.values["restitution"])
    except Exception as e:
        print("réécriture d'un point existant : refusée par", type(e).__name__, str(e)[:200])
    print("exécutions par nœud (deux fils) :", compteurs(ESSAI))
