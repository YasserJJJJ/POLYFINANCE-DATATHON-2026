"""Contrôle d'ancrage du Rédacteur, testé avec un faux modèle (aucun appel à Bedrock)."""
import json
import types

import pytest

from alphaforge import llm
from alphaforge.agents import redacteur
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS


def faux_modele(monkeypatch, fabriquer):
    """Branche un faux modèle sur le SEUL Rédacteur. `fabriquer(reference)` reçoit les phrases de référence
    du dossier et renvoie la réponse JSON du « modèle »."""
    appels = []

    def appeler_json(systeme, consigne, modele=None, max_tokens=0):
        reference = json.loads(consigne.split("\n\nDéfauts")[0])["phrases_de_reference"]
        appels.append(consigne)
        return fabriquer(reference)

    faux = types.SimpleNamespace(actif=lambda: True, appeler_json=appeler_json, nom=llm.nom,
                                 MODELE_PRINCIPAL=llm.MODELE_PRINCIPAL, raison_indisponible=lambda: None,
                                 nombres=llm.nombres, _NOMBRE=llm._NOMBRE)
    monkeypatch.setattr(redacteur, "llm", faux)
    return appels


def _robert(demande=None):
    p = PERSONAS["robert"]
    return analyser(p["profil"], {**p["demande"], **(demande or {})})


def test_ce_qui_changerait_reste_ecrit_par_le_code(monkeypatch):
    def fabriquer(ref):
        return {**ref, "ce_qui_changerait": [{"texte": "L'avis pourrait changer si la décision s'appuyait moins "
                                                       "sur l'attention médiatique.", "type": "HYPOTHESE", "faits": []}]}
    faux_modele(monkeypatch, fabriquer)
    d = _robert()
    assert d["texte"]["source"] == llm.nom(llm.MODELE_PRINCIPAL)
    textes = " ".join(ph["texte"] for ph in d["texte"]["ce_qui_changerait"])
    assert "médiatique" not in textes and 20000.0 in llm.nombres(textes)
