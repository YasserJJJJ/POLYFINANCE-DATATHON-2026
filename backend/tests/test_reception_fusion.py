"""Les dix cas du prompt 4. Aucun réseau ni identifiant AWS requis."""
import builtins
import copy
import re

import pytest
from fastapi import HTTPException

import api
from alphaforge import sources
from alphaforge.personas import PERSONAS


@pytest.fixture(autouse=True)
def hors_ligne(monkeypatch):
    monkeypatch.setenv("ALPHAFORGE_LLM", "off")
    monkeypatch.setenv("ALPHAFORGE_DATA_BUCKET", "")
    monkeypatch.delenv("ALPHAFORGE_CAPACITE", raising=False)


def entree(nom="robert", profil=None, demande=None):
    p = copy.deepcopy(PERSONAS[nom])
    return api.Requete(profil={**p["profil"], **(profil or {})},
                       demande={**p["demande"], **(demande or {})})


def dossier(nom="robert", profil=None, demande=None):
    return api._analyser_requete(entree(nom, profil, demande))


def test_01_robert_perte_appariee_et_options():
    d = dossier()
    assert d["verdict"]["etat"] == "incoherent"
    c = d["comparaison"]
    r = next(r for r in d["regles"] if r["code"] == "capacite")
    assert {c["faits"]["apres_pire_chute"], c["faits"]["avant_pire_chute"]} <= set(r["faits"])
    assert "Version ajustée" in {o["nom"] for o in d["options"]} and d["suggestions"]["placements"]
    ph = next(p for p in d["texte"]["pourquoi"] if "Sur la même fenêtre historique" in p["texte"])
    assert c["faits"]["ecart_pire_chute"] in ph["faits"] and "plus profonde" in ph["texte"]


def test_02_amira_concentration_et_limites_crypto():
    d = dossier("amira")
    assert d["verdict"]["etat"] != "coherent"
    assert next(r for r in d["regles"] if r["code"] == "concentration")["niveau"] != "ok"
    assert d["comparaison"]["disponible"]
    limites = " ".join(p["texte"] for p in d["texte"]["limites"]).lower()
    assert "crypto" in limites and "2022" in limites and "achat-conservation" in limites
    assert "cinq ans" in limites and "communes" in limites


def test_03_mateo_preference_prime_sur_ecart_favorable():
    d = dossier("mateo")
    assert d["verdict"]["etat"] == "incoherent"
    assert next(r for r in d["regles"] if r["code"] == "exclusion")["niveau"] == "rouge"
    assert d["comparaison"]["ecarts"]["sens_pire_chute"] == "ameliore"
    assert d["suggestions"]["placements"] and all(pl["ticker"] != "ENB.TO" for pl in d["suggestions"]["placements"])
    assert any("moins profonde" in p["texte"] for p in d["texte"]["pourquoi"])


def test_04_epargne_manquante_pas_de_grille():
    d = dossier(profil={"epargne_totale_cad": None})
    assert d["verdict"]["etat"] == "indetermine" and d["questions"] and not d["bascule"]


def test_05_retrait_inconnu_question_decisive_en_premier():
    d = dossier(profil={"retrait_prevu_ans": None})
    assert d["profil"]["retrait_prevu_ans"] is None
    assert d["verdict"]["etat"] == "ajustement"
    assert d["questions"][0].startswith("Question décisive")
    assert "passerait" in d["questions"][0] and "Incohérent" in d["questions"][0]
    assert re.search(r"F-\d+", d["questions"][0])


def test_06_montant_impossible_aucune_allocation():
    d = dossier(profil={"epargne_totale_cad": 100000}, demande={"montant_cad": 120000})
    assert d["verdict"]["etat"] == "indetermine"
    assert "le montant dépasse l'épargne totale" in d["regles"][0]["explication"].lower()
    assert not d["comparaison"].get("poids_apres") and not d["bascule"]


def test_07_gamestop_message_explicite():
    with pytest.raises(HTTPException) as exc:
        dossier(demande={"ticker": "GME", "texte": "Je veux placer 80000 CAD dans GameStop."})
    assert exc.value.status_code == 422
    assert "31 actifs du jeu de départ" in exc.value.detail
    assert "KeyError" not in exc.value.detail


def test_08_retrait_puis_montant_accord_grille_comparaison():
    initial = dossier()
    retrait = dossier(profil={"retrait_prevu_ans": 10})
    montant = dossier(profil={"retrait_prevu_ans": 10}, demande={"montant_cad": 20000})
    for d in (initial, retrait, montant):
        case = next(c for c in d["bascule"]["cases"]
                    if c["montant_cad"] == d["demande"]["montant_cad"]
                    and c["horizon_ans"] == d["profil"]["horizon_ans"])
        assert case["etat"] == d["verdict"]["etat"]
    # Les identifiants F-n sont locaux à chaque dossier ; un fait de retrait peut disparaître.
    assert {k: v for k, v in initial["comparaison"].items() if k != "faits"} == {
        k: v for k, v in retrait["comparaison"].items() if k != "faits"}
    assert retrait["comparaison"]["apres"] != montant["comparaison"]["apres"]
    assert retrait["comparaison"]["avant"] == montant["comparaison"]["avant"]


def test_09_chaine_de_preuve_complete():
    d = dossier()
    f = next(f for f in d["faits"] if f["id"] == d["comparaison"]["faits"]["apres_pire_chute"])
    assert "Moteur historique-B" in f["methode"] and "achat" in f["methode"].lower()
    assert f["source"] and f["references"]
    assert all(r in sources.REFERENCES for r in f["references"])
    assert any(sources.REFERENCES[r]["type"] == "donnees" for r in f["references"])


def test_10_sans_identifiants_ni_sdk_memes_decisions(monkeypatch):
    attendu = dossier()
    for k in ("AWS_PROFILE", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
        monkeypatch.delenv(k, raising=False)
    importer = builtins.__import__
    def sans_sdk(nom, *args, **kwargs):
        if nom.split(".")[0] in {"boto3", "botocore"}:
            raise AssertionError("Aucun SDK AWS ne doit être requis hors ligne")
        return importer(nom, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", sans_sdk)
    obtenu = dossier()
    assert obtenu["appels_modele"] == []
    for k in ("verdict", "regles", "options", "bascule", "comparaison"):
        assert obtenu[k] == attendu[k]
    # L'égalité avec des appels réels est vérifiée dans les captures Bedrock des cas 1–3.
