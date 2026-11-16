"""Contrat 2 actif : les symboles restent compatibles, les poids sont utilisés."""
import copy

import pytest

from alphaforge import llm
from alphaforge.agents import sceptique
from alphaforge.dossier import Dossier
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS
from alphaforge.profil import normaliser_portefeuille, symboles_portefeuille


@pytest.mark.parametrize("portefeuille", [None, [], {}])
def test_portefeuille_inconnu(portefeuille):
    assert normaliser_portefeuille(portefeuille) == (None, None)
    assert symboles_portefeuille(portefeuille) == []


def test_poids_declares_et_hypothese_equiponderee_sans_mutation():
    entree = {"XIU.TO": 0.7, "XBB.TO": 0.3}
    poids, origine = normaliser_portefeuille(entree)
    assert poids == entree and poids is not entree and origine == "declare"
    assert normaliser_portefeuille(["XIU.TO", "XBB.TO"]) == (
        {"XIU.TO": 0.5, "XBB.TO": 0.5}, "hypothese_equiponderee"
    )
    assert normaliser_portefeuille(["XIU.TO", "XIU.TO"]) == ({"XIU.TO": 1.0}, "hypothese_equiponderee")
    assert symboles_portefeuille(entree) == ["XIU.TO", "XBB.TO"]
    assert entree == {"XIU.TO": 0.7, "XBB.TO": 0.3}


@pytest.mark.parametrize("portefeuille", [
    {"XIU.TO": 0.7, "XBB.TO": 0.2},
    {"XIU.TO": 0.7, "XBB.TO": 0.4},
    {"XIU.TO": -0.1, "XBB.TO": 1.1},
    {"XIU.TO": "1"},
    {"XIU.TO": True},
    {"XIU.TO": None},
    {"XIU.TO": float("nan")},
    {"XIU.TO": float("inf")},
    {"XIU.TO": 10**400},
    {"XIU.TO": 0},
    "XIU.TO",
    False,
    0,
    [""],
    [12],
])
def test_portefeuille_invalide_refuse(portefeuille):
    with pytest.raises(ValueError):
        normaliser_portefeuille(portefeuille)


def test_erreur_d_arrondi_machine_et_poids_nul_acceptes():
    poids, origine = normaliser_portefeuille({str(i): 0.1 for i in range(10)})
    assert len(poids) == 10 and origine == "declare"
    assert normaliser_portefeuille({"XIU.TO": 1, "XBB.TO": 0})[0] == {"XIU.TO": 1, "XBB.TO": 0}


@pytest.mark.parametrize("nom", ["robert", "amira", "mateo"])
def test_les_appelants_lisent_les_symboles_et_conservent_les_poids(nom):
    entree = copy.deepcopy(PERSONAS[nom])
    symboles = entree["profil"]["portefeuille_actuel"]
    poids = {t: (i + 1) / sum(range(1, len(symboles) + 1)) for i, t in enumerate(symboles)}
    profil = {**entree["profil"], "portefeuille_actuel": poids}
    obtenu = analyser(profil, entree["demande"])
    attendu = analyser(entree["profil"], entree["demande"])
    assert obtenu["profil"]["portefeuille_actuel"] == poids
    assert profil["portefeuille_actuel"] == poids
    # K3 actif : les mesures du titre C restent identiques ; le portefeuille B
    # dépend désormais des poids. Ne plus exiger l'ignorance des poids de T1.
    assert obtenu["demande"]["mesures"] == attendu["demande"]["mesures"]
    assert obtenu["version_contrat"] == "2"
    assert obtenu["comparaison"]["poids_avant"] == poids
    assert obtenu["comparaison"]["avant"] != attendu["comparaison"]["avant"]
    assert obtenu["appels_modele"] == []


def test_sceptique_recoit_la_liste_des_symboles(monkeypatch):
    messages = []
    monkeypatch.setattr(llm, "appeler_json", lambda _s, message, *_a: messages.append(message) or {})
    d = Dossier(profil={"portefeuille_actuel": {"XIU.TO": 0.7, "XBB.TO": 0.3}},
                demande={"mesures": {}, "ticker": "TSLA", "montant_cad": 100})
    sceptique._choix_llm(d, [])
    assert "placements actuels ['XIU.TO', 'XBB.TO']" in messages[0]


def test_champs_vides_independants_entre_dossiers():
    premier, second = Dossier({}, {}), Dossier({}, {})
    premier.comparaison["disponible"] = False
    premier.appels_modele.append({"agent": "essai"})
    assert second.comparaison == {} and second.appels_modele == []
    appels = llm.journal_appels()
    appels.append({"agent": "essai"})
    assert llm.journal_appels() == []


@pytest.mark.parametrize("incomplete", [False, True])
def test_journal_branche_sur_toutes_les_sorties(incomplete, monkeypatch):
    preuve = [{"agent": "Profileur", "request_id": "appel-factice-du-test"}]
    monkeypatch.setattr(llm, "journal_appels", lambda: preuve)
    p = PERSONAS["robert"]
    demande = {"texte": "", "texte_lu": True} if incomplete else p["demande"]
    assert analyser(p["profil"], demande)["appels_modele"] == preuve
