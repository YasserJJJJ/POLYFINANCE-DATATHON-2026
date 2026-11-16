"""Essai 7 — bifurcation depuis un point antérieur (variante) : la ligne d'origine reste-t-elle intacte ?

Aucun appel de modèle.
"""
import json

from commun import DEMANDE, compteurs, construire, difference, fil, point_apres, remise_a_zero, sauvegarde

ESSAI = "essai07"


def ident(config):
    return (config or {}).get("configurable", {}).get("checkpoint_id")


def photo(graphe, config) -> dict:
    """Contenu de chaque point du fil, par identifiant, pour comparer avant et après."""
    return {ident(s.config): json.dumps({"valeurs": s.values, "parent": ident(s.parent_config), "suivants": s.next},
                                        sort_keys=True, ensure_ascii=False, default=str)
            for s in graphe.get_state_history(config)}


if __name__ == "__main__":
    remise_a_zero(ESSAI)
    saver = sauvegarde("essai07.sqlite", neuf=True)
    graphe = construire(ESSAI, checkpointer=saver)
    config = fil("etude-1")
    graphe.invoke({"demande": DEMANDE}, config)
    tete_origine = ident(graphe.get_state(config).config)
    avant, c0 = photo(graphe, config), compteurs(ESSAI)

    amont = point_apres(graphe, config, ("agent1",))
    variante = graphe.update_state(amont.config, {"montant": 8000.0}, as_node="agent0")
    graphe.invoke(None, variante)
    apres = photo(graphe, config)

    print(f"points du fil : {len(avant)} avant, {len(apres)} après la variante")
    print("ligne d'origine intacte (mêmes identifiants, mêmes contenus) :", all(apres.get(k) == v for k, v in avant.items()))
    print("nœuds exécutés pour la variante :", difference(compteurs(ESSAI), c0))
    tete = graphe.get_state(config)
    print("« dernier état » du fil après la variante :", tete.values["restitution"],
          "; est-ce la tête d'origine ?", ident(tete.config) == tete_origine)
    print("ligne d'origine relue par son identifiant :", graphe.get_state(fil("etude-1", tete_origine)).values["restitution"])
    print("métadonnées du point de bifurcation :", dict(graphe.get_state(variante).metadata))

    # Une écriture sur la ligne d'origine fait rebasculer le « dernier état » du fil.
    graphe.update_state(fil("etude-1", tete_origine), {"journal": ["la personne confirme la ligne principale"]}, as_node="agent3")
    print("« dernier état » après une écriture sur la ligne d'origine :", graphe.get_state(config).values["restitution"])

    # Peut-on loger la variante dans un fil à part (branche nommée) ?
    try:
        saver.copy_thread("etude-1", "etude-1-variante")
        print("copie du fil : faite ;", len(list(graphe.get_state_history(fil("etude-1-variante")))), "points copiés")
    except Exception as e:
        print("copie du fil avec SqliteSaver :", type(e).__name__, str(e)[:160])
