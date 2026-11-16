"""Export des relations d'une branche au format PROV-JSON, avec la seule bibliothèque standard.

Choix d'export :
- pièce = entité ; exécution d'une tâche, retrait, affichage = activités ; auteurs = agents ;
- « remplace » = wasDerivedFrom de type prov:Revision ;
- seul le retrait d'une pièce erronée devient wasInvalidatedBy : dans PROV, une entité invalidée
  ne sert plus jamais. « Périmée » est un état relatif à une tête ; il ne s'exporte pas ainsi ;
- « réagit à » n'existe pas dans PROV : wasInfluencedBy, typé af:reagitA.
"""
from __future__ import annotations

from dossier import PRINCIPALE, Dossier


def _nom(s: str) -> dict:
    return {"$": s, "type": "prov:QUALIFIED_NAME"}


def exporter(dossier: Dossier, branche: str = PRINCIPALE) -> dict:
    doc: dict[str, dict] = {k: {} for k in (
        "entity", "activity", "agent", "used", "wasGeneratedBy", "wasAssociatedWith", "wasAttributedTo",
        "wasDerivedFrom", "wasInvalidatedBy", "wasInfluencedBy")}

    def lien(relation: str, **champs) -> None:
        doc[relation][f"_:{relation}{len(doc[relation]) + 1}"] = {f"prov:{k}": v for k, v in champs.items()}

    def piece(h: str, emplacement: str) -> str:
        nom = f"af:piece-{h[:16]}"
        doc["entity"].setdefault(nom, {"prov:type": _nom(f"af:{emplacement.replace(':', '-')}"), "af:empreinte": h})
        return nom

    lancements: dict[str, str] = {}
    for e in dossier.evenements(branche):
        agent, court = f"af:{e['auteur']}", e["empreinte"][:16]
        doc["agent"].setdefault(agent, {})
        if e["type"] == "depot":
            p = piece(e["piece"], e["emplacement"])
            lien("wasAttributedTo", entity=p, agent=agent)
            if e["remplace"] and e["remplace"] != e["piece"]:
                lien("wasDerivedFrom", generatedEntity=p, usedEntity=piece(e["remplace"], e["emplacement"]),
                     type=_nom("prov:Revision"))
        elif e["type"] == "tache_lancee":
            lancements[e["cle"]] = e["date"]
        elif e["type"] == "tache_terminee":
            a, p = f"af:activite-{e['cle'][:16]}", piece(e["piece"], e["emplacement"])
            doc["activity"][a] = {"prov:startTime": lancements.get(e["cle"], e["date"]), "prov:endTime": e["date"],
                                  "af:tache": e["tache"], "af:version": e["version"]}
            lien("wasGeneratedBy", entity=p, activity=a, time=e["date"])
            lien("wasAssociatedWith", activity=a, agent=agent)
            lien("wasAttributedTo", entity=p, agent=agent)
            for emplacement, h in e["entrees"].items():
                lien("used", activity=a, entity=piece(h, emplacement))
                lien("wasDerivedFrom", generatedEntity=p, usedEntity=piece(h, emplacement), activity=a)
        elif e["type"] == "retrait":
            a = f"af:retrait-{court}"
            doc["activity"][a] = {"prov:startTime": e["date"], "af:motif": e["motif"]}
            lien("wasInvalidatedBy", entity=f"af:piece-{e['piece'][:16]}", activity=a, time=e["date"])
            lien("wasAssociatedWith", activity=a, agent=agent)
        elif e["type"] == "affichage":
            a = f"af:affichage-{court}"
            doc["activity"][a] = {"prov:startTime": e["date"]}
            lien("used", activity=a, entity=piece(e["piece"], "restitution"))
            lien("wasAssociatedWith", activity=a, agent=agent)
        elif e["type"] == "reaction":
            r = f"af:reaction-{court}"
            doc["entity"][r] = {"prov:type": _nom("af:reaction"), "af:nature": e["nature"]}
            lien("wasAttributedTo", entity=r, agent=agent)
            lien("wasInfluencedBy", influencee=r, influencer=f"af:affichage-{e['affichage'][:16]}",
                 type=_nom("af:reagitA"))
    return {"prefix": {"af": "urn:alphaforge:dossier:"}, **{k: v for k, v in doc.items() if v}}


def controler_avec_prov(texte: str) -> dict:
    """Relit l'export avec le paquet « prov » (facultatif) : nombre d'enregistrements et aller-retour."""
    from prov.model import ProvDocument

    lu = ProvDocument.deserialize(content=texte, format="json")
    relu = ProvDocument.deserialize(content=lu.serialize(format="json"), format="json")
    return {"enregistrements": len(lu.get_records()), "aller_retour_identique": lu == relu, "provn": lu.get_provn()}
