"""Plan ouvert : sans placement choisi, le Gardien juge le plan sur toute la liste, sans modèle."""
import pytest

from alphaforge import gardien
from alphaforge.agents import analyste
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS


def _ouvert(nom, profil=None, montant=None):
    p = PERSONAS[nom]
    return analyser({**p["profil"], **(profil or {})},
                    {"ticker": None, "montant_cad": montant or p["demande"]["montant_cad"], "texte": ""})


@pytest.mark.parametrize("nom", ["amira", "mateo", "robert"])
def test_les_placements_proposes_passent_vraiment_les_regles(nom):
    d = _ouvert(nom)
    plan = d["plan"]
    assert plan["ouvert"] and 1 <= len(plan["placements"]) <= 3
    for pl in plan["placements"]:
        m = analyste.mesures_actif(pl["ticker"], [])
        p = PERSONAS[nom]
        regles = gardien.appliquer_regles(p["profil"], {"ticker": pl["ticker"], "montant_cad": d["demande"]["montant_cad"]},
                                          analyste.mesures_actif(pl["ticker"], d["profil"].get("portefeuille_actuel") and
                                                                 [t for t in (d["profil"]["portefeuille_actuel"] or [])]))
        assert pl["etat"] == d["verdict"]["etat"] and m["pire_chute_pct"] == pl["pire_chute_pct"]
        assert gardien.verdict(regles)["etat"] == pl["etat"]
    assert [abs(p["pire_chute_pct"]) for p in plan["placements"]] == sorted(abs(p["pire_chute_pct"]) for p in plan["placements"])


def test_les_exclusions_sont_respectees_et_comptees():
    d = _ouvert("mateo")
    assert all(p["ticker"] not in ("ENB.TO", "SU.TO", "CNQ.TO", "XOM") for p in d["plan"]["placements"])
    assert any(e["raison"] == "Secteur exclu" for e in d["plan"]["ecartes"])


def test_un_plan_impossible_dit_la_regle_qui_bloque():
    d = _ouvert("robert", {"somme_a_preserver_cad": 395000})
    assert d["verdict"]["etat"] == "incoherent" and not d["plan"]["placements"]
    assert d["plan"]["bloquante"] == "Somme à préserver"


def test_une_information_essentielle_manquante_reste_grise():
    d = _ouvert("robert", {"horizon_ans": None})
    assert d["verdict"]["etat"] == "indetermine" and "horizon" in d["regles"][0]["explication"]


def test_aucun_conseil_et_aucun_classement_au_rendement():
    d = _ouvert("robert")
    textes = " ".join(ph["texte"] for k in ("pourquoi", "limites") for ph in d["texte"][k]).lower()
    assert not any(m in textes for m in ("achète", "achetez", "je recommande", "vends"))
    assert "pas une recommandation" in textes and "rendement passé" in textes
    assert not d["questions"] or all("placement as-tu en tête" not in q for q in d["questions"])


def test_chaque_placement_propose_renvoie_a_un_fait_du_registre():
    d = _ouvert("amira")
    ids = {f["id"] for f in d["faits"]}
    assert all(p["faits"] and p["faits"][0] in ids for p in d["plan"]["placements"])


@pytest.mark.parametrize("ticker", [None, "XIU.TO"])
def test_sans_tolerance_on_demande_le_risque_jamais_un_placement(ticker):
    p = {**PERSONAS["robert"]["profil"], "tolerance": None, "reponses_tolerance": {}}
    d = analyser(p, {"ticker": ticker, "montant_cad": 10000, "texte": ""})
    assert d["verdict"]["etat"] == "indetermine"
    assert any("risque es-tu prêt à prendre" in q for q in d["questions"])
    assert not any("placement as-tu en tête" in q for q in d["questions"])
