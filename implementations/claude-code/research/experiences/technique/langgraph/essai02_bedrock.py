"""Essai 2 — un appel de modèle par Amazon Bedrock (profil « alphaforge »), puis une sortie à structure imposée.

Deux appels de modèle, courts.
"""
import json
import time

from pydantic import BaseModel, Field

from commun import MODELE, PROFIL, REGION, SORTIES, modele


class FaitDeclare(BaseModel):
    """Un fait déclaré par la personne dans sa demande."""
    champ: str = Field(description="nom du champ, par exemple « montant »")
    valeur: str = Field(description="valeur telle que déclarée")
    citation: str = Field(description="extrait mot pour mot de la demande")


if __name__ == "__main__":
    bilan = {"modele": MODELE, "profil": PROFIL, "region": REGION}

    m = modele(max_tokens=40)
    t0 = time.time()
    r = m.invoke("Réponds par le seul mot : prêt.")
    bilan["appel_simple"] = {"texte": r.content if isinstance(r.content, str) else r.content,
                             "jetons": r.usage_metadata, "duree_s": round(time.time() - t0, 2),
                             "modele_repondant": r.response_metadata.get("model_name"),
                             "raison_d_arret": r.response_metadata.get("stopReason")}
    print("appel simple :", bilan["appel_simple"])

    structure = modele(max_tokens=200)
    print("choix d'outil reconnus pour ce modèle :", structure.supports_tool_choice_values)
    t0 = time.time()
    s = structure.with_structured_output(FaitDeclare, include_raw=True).invoke(
        "Demande : « Je veux investir 5000 $ dans Tesla sur dix ans. » Extrais le fait déclaré sur le montant.")
    bilan["sortie_structuree"] = {"objet": s["parsed"].model_dump() if s["parsed"] else None,
                                  "erreur_d_analyse": str(s["parsing_error"]) if s["parsing_error"] else None,
                                  "duree_s": round(time.time() - t0, 2),
                                  "choix_d_outil_reconnus": list(structure.supports_tool_choice_values or [])}
    print("sortie à structure imposée :", bilan["sortie_structuree"])
    (SORTIES / "essai02_bedrock.json").write_text(json.dumps(bilan, indent=1, ensure_ascii=False, default=str))
