"""Trois défauts de qualification : demande impossible, univers, types HTTP."""
import asyncio
import copy
import json

import pytest
from fastapi import HTTPException

import api
from alphaforge import gardien
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS
from test_reference_personas import sans_variations


@pytest.fixture(autouse=True)
def hors_ligne(monkeypatch):
    monkeypatch.setenv("ALPHAFORGE_LLM", "off")
    monkeypatch.delenv("ALPHAFORGE_DATA_BUCKET", raising=False)


def requete(profil=None, demande=None, nom="robert"):
    p = copy.deepcopy(PERSONAS[nom])
    return api.Requete(profil={**p["profil"], **(profil or {})},
                       demande={**p["demande"], **(demande or {})})


def lire_flux(req):
    reponse = api.analyse_flux(req)

    async def lire():
        return [part async for part in reponse.body_iterator]

    return [json.loads(ligne) for part in asyncio.run(lire()) for ligne in part.splitlines()]


def test_demande_impossible_est_indeterminee_par_donnees():
    req = requete({"epargne_totale_cad": 100000}, {"montant_cad": 120000})
    for d in (api.analyse(req), analyser(req.profil, req.demande), lire_flux(req)[-1]["dossier"]):
        assert d["verdict"]["etat"] == "indetermine"
        assert len(d["regles"]) == 1
        assert d["regles"][0]["code"] == "donnees" and d["regles"][0]["niveau"] == "gris"
        assert "le montant dépasse l'épargne totale" in d["regles"][0]["explication"].lower()
        assert d["bascule"] == {}


def test_actif_hors_univers_reste_une_erreur_expliquee_en_francais():
    req = requete(demande={"ticker": "ACTIF-INCONNU", "texte": ""})
    with pytest.raises(HTTPException) as erreur:
        api.analyse(req)
    assert erreur.value.status_code == 422
    assert "31 actifs du jeu de départ" in erreur.value.detail
    dernier = lire_flux(req)[-1]
    assert dernier == {"type": "erreur", "statut": 422, "detail": erreur.value.detail}


def test_chaines_numeriques_converties_sans_changer_le_dossier_ni_la_requete():
    req = requete({"horizon_ans": "4", "epargne_totale_cad": "400000",
                   "somme_a_preserver_cad": "300000", "retrait_prevu_ans": "4", "tolerance": "30"},
                  {"montant_cad": "80000"})
    copie = req.model_dump()
    d = api.analyse(req)
    attendu = api.analyse(requete())
    assert sans_variations(d) == sans_variations(attendu)
    assert req.model_dump() == copie
    assert sans_variations(lire_flux(req)[-1]["dossier"]) == sans_variations(attendu)
    compris = api.comprendre(req)
    assert compris["profil"]["horizon_ans"] == 4 and compris["demande"]["montant_cad"] == 80000


@pytest.mark.parametrize("champ, valeur", [
    ("horizon_ans", "quatre"),
    ("montant_cad", "inconnu"),
    ("horizon_ans", ""),
    ("montant_cad", ""),
    ("horizon_ans", True),
    ("montant_cad", True),
    ("horizon_ans", "NaN"),
    ("montant_cad", "Infinity"),
    ("horizon_ans", float("nan")),
    ("montant_cad", float("inf")),
    ("epargne_totale_cad", "inconnue"),
    ("retrait_prevu_ans", "bientôt"),
    ("somme_a_preserver_cad", "beaucoup"),
])
def test_entree_non_numerique_est_invalide_sans_erreur_500(champ, valeur):
    req = requete(demande={champ: valeur}) if champ == "montant_cad" else requete(profil={champ: valeur})
    d = api.analyse(req)
    assert d["verdict"]["etat"] == "indetermine"
    assert d["regles"][0]["code"] == "donnees" and d["regles"][0]["niveau"] == "gris"
    assert "Il faut" in d["regles"][0]["explication"]
    assert d["faits"] == [] and d["appels_modele"] == []
    json.dumps(d, allow_nan=False)
    assert api.comprendre(req)["questions"]
    dernier = lire_flux(req)[-1]
    assert dernier["type"] == "dossier" and dernier["dossier"]["verdict"]["etat"] == "indetermine"


def test_gardien_valide_avant_de_calculer_le_score():
    req = requete({"horizon_ans": "quatre"})
    r = gardien.appliquer_regles(req.profil, req.demande, {})
    assert gardien.verdict(r)["etat"] == "indetermine" and r[0].code == "donnees"


def test_exclusion_chaine_equivaut_a_la_liste_d_un_element():
    req = requete({"exclusions": "Énergie"}, nom="mateo")
    d = api.analyse(req)
    attendu = api.analyse(requete({"exclusions": ["Énergie"]}, nom="mateo"))
    assert sans_variations(d) == sans_variations(attendu)
    assert gardien.exclusions_normalisees({"exclusions": "Énergie"}) == ["energy"]
    assert next(r for r in d["regles"] if r["code"] == "exclusion")["niveau"] == "rouge"
