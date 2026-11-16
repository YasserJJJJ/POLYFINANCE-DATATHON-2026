"""Essai 3 : sortie à structure imposée (modèle Pydantic), cas valide, invalide, tronqué.

Relance : uv run --with strands-agents python research/experiences/technique/strands/essai3_sortie_structuree.py [valide|invalide|tronquee]
Sans argument : les trois cas (3 à 5 appels de modèle).
"""
import sys
from typing import Literal

import commun
from pydantic import BaseModel, Field, field_validator
from strands import Agent

CAS = sys.argv[1:] or ["valide", "invalide", "tronquee"]
CONSIGNE = "Tu remplis la structure demandée, sans autre texte."
DEMANDE = "Formalise : « Robert, 58 ans, veut savoir si garder 40 % de Tesla est risqué d'ici sa retraite dans 7 ans. »"


class Qualification(BaseModel):
    """Qualification d'une demande (essai)."""

    type_de_question: Literal["concentration", "horizon", "liquidite", "autre"]
    horizon_annees: int = Field(ge=0, le=60)
    inconnues: list[str] = Field(max_length=3, description="Au plus trois inconnues, en quelques mots")


class QualificationRefusee(Qualification):
    """Même structure, avec une porte qui refuse toujours (pour voir la conduite sur sortie invalide)."""

    @field_validator("horizon_annees")
    @classmethod
    def refuser(cls, v):
        raise ValueError("refus volontaire de l'essai : horizon non accepté")


class QualificationLongue(BaseModel):
    """Structure qui demande un texte long (pour provoquer la troncature)."""

    resume_detaille: str = Field(description="Résumé d'au moins trois cents mots")
    type_de_question: Literal["concentration", "horizon", "liquidite", "autre"]


def essayer(nom, structure, max_tokens, limites):
    print(f"\n=== cas {nom} : structure {structure.__name__}, max_tokens={max_tokens}, limites={limites} ===")
    avant = commun.nb_appels()
    agent = Agent(model=commun.modele(f"essai3-{nom}", max_tokens=max_tokens), system_prompt=CONSIGNE, callback_handler=None)
    try:
        res = agent(DEMANDE, structured_output_model=structure, limits=limites)
        print("raison d'arrêt :", res.stop_reason)
        print("structured_output :", repr(res.structured_output))
        print("texte de la réponse :", repr(str(res)[:200]))
    except Exception as e:  # on veut voir quelle exception sort, et avec quel message
        print("EXCEPTION :", type(e).__module__ + "." + type(e).__name__, "|", str(e)[:300])
    print("appels de modèle consommés par ce cas :", commun.nb_appels() - avant)
    print("messages laissés dans l'agent :", [(m["role"], [list(b)[0] for b in m["content"]]) for m in agent.messages])
    for m in agent.messages:
        for b in m["content"]:
            if "toolResult" in b:
                print("  résultat d'outil renvoyé au modèle :", b["toolResult"]["status"], "|", str(b["toolResult"]["content"])[:260])


if "valide" in CAS:
    essayer("valide", Qualification, 400, None)
if "invalide" in CAS:
    essayer("invalide", QualificationRefusee, 400, {"structured_output_attempts": 1})
if "tronquee" in CAS:
    essayer("tronquee", QualificationLongue, 40, {"structured_output_attempts": 1})
commun.bilan("essai3")
