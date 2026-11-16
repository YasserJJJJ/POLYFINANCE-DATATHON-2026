"""Filet figé par tranche : aucune régénération automatique par les tests."""
import copy
import json
from pathlib import Path

import pytest

from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS

REFERENCE = Path(__file__).with_name("reference")
CHAMPS_VARIABLES = ("appels_modele",)


def sans_variations(dossier):
    """K3 actif est désormais figé aussi ; seules durées et preuves d'appels varient."""
    resultat = copy.deepcopy(dossier)
    for champ in CHAMPS_VARIABLES:
        resultat.pop(champ, None)
    for etape in resultat["trace"]:
        etape["duree_ms"] = 0
    return resultat


@pytest.mark.parametrize("nom", ["robert", "amira", "mateo"])
def test_reference_persona(nom, monkeypatch):
    monkeypatch.setenv("ALPHAFORGE_LLM", "off")
    entree = PERSONAS[nom]
    attendu = json.loads((REFERENCE / f"{nom}.json").read_text(encoding="utf-8"))
    obtenu = analyser(entree["profil"], entree["demande"])
    # Compare notamment verdict, règles, tous les attributs des faits, options et grille.
    assert sans_variations(obtenu) == sans_variations(attendu)
