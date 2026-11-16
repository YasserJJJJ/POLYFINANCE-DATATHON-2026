"""Filet figé depuis C évalué : aucune régénération automatique par les tests."""
import copy
import json
from pathlib import Path

import pytest

from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS

REFERENCE = Path(__file__).with_name("reference")
CHAMPS_CONTRAT_2 = ("version_contrat", "comparaison", "appels_modele")


def sans_variations(dossier):
    """Seules les durées et les trois ajouts de contrat échappent à la comparaison."""
    resultat = copy.deepcopy(dossier)
    for champ in CHAMPS_CONTRAT_2:
        resultat.pop(champ, None)
    for etape in resultat["trace"]:
        etape["duree_ms"] = 0
    return resultat


@pytest.mark.parametrize("nom", ["robert", "amira", "mateo"])
def test_reference_persona(nom, monkeypatch):
    monkeypatch.setenv("ALPHAFORGE_LLM", "off")
    entree = PERSONAS[nom]
    attendu = json.loads((REFERENCE / f"{nom}.json").read_text())
    obtenu = analyser(entree["profil"], entree["demande"])
    # Compare notamment verdict, règles, tous les attributs des faits, options et grille.
    assert sans_variations(obtenu) == sans_variations(attendu)
