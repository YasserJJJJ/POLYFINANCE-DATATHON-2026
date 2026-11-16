"""Sceptique : ses vérifications disent ce que les chiffres montrent, et la trace dit qui a choisi."""
import types

import pytest

from alphaforge import llm
from alphaforge.agents import analyste, profileur, sceptique
from alphaforge.dossier import Dossier
from alphaforge.personas import PERSONAS


def _dossier(ticker, portefeuille=None, nom="robert"):
    p = PERSONAS[nom]
    d = Dossier(profil={**p["profil"], "portefeuille_actuel": portefeuille or []},
                demande={**p["demande"], "ticker": ticker, "texte": ""})
    profileur.executer(d)
    analyste.executer(d)
    return d


def test_comparaison_au_marche_ne_conclut_pas_sans_condition():
    # XBB.TO (obligations) chute à peine moins que XIU.TO : avant, « propre à ce placement, pas au marché ».
    d = _dossier("XBB.TO")
    rep, issue = sceptique._reference(d, d.demande["mesures"], d.demande["ids_faits"])
    assert "propre à ce placement" not in rep and "n'est pas plus forte" in rep and issue == "confirmee"
    d = _dossier("TSLA")
    rep, issue = sceptique._reference(d, d.demande["mesures"], d.demande["ids_faits"])
    assert "tient surtout au placement" in rep and issue == "ecartee"


def test_correlation_moyenne_renvoie_au_seuil_du_gardien():
    d = _dossier("NVDA", ["QQQ"], "amira")   # corrélation NVDA~QQQ de 0,75 : entre 0,6 et 0,8
    rep, issue = sceptique._concentration(d, d.demande["mesures"], d.demande["ids_faits"])
    assert "0,8" in rep and "seuil de l'équipe" in rep and issue == "confirmee"


def _faux_modele(monkeypatch, reponse):
    faux = types.SimpleNamespace(actif=lambda: True, appeler_json=lambda *a, **k: reponse, nom=llm.nom,
                                 MODELE_PRINCIPAL=llm.MODELE_PRINCIPAL, nombres=llm.nombres)
    monkeypatch.setattr(sceptique, "llm", faux)


def test_objection_hors_sujet_ou_de_conseil_remplacee_par_la_question_du_catalogue(monkeypatch):
    # Objection réellement écrite par Claude pour Mateo (code « fenetre_courte », texte sur l'exclusion).
    hors_sujet = ("Enbridge fait partie du secteur Energy que tu exclus explicitement, donc cet achat contredit "
                  "directement tes propres critères.")
    _faux_modele(monkeypatch, {"objections": [{"code": "fenetre_courte", "texte": hors_sujet},
                                              {"code": "comparer_marche", "texte": "Achète, le marché va monter."}]})
    d = _dossier("ENB.TO", nom="mateo")
    sceptique.executer(d)
    textes = [o.texte for o in d.objections]
    assert textes == [sceptique.CATALOGUE["fenetre_courte"][2], sceptique.CATALOGUE["comparer_marche"][2]]


@pytest.mark.parametrize("reponse", [{"objections": []}, {"objections": [{"code": "inexistant", "texte": "x"}]}, {}])
def test_la_trace_ne_dit_pas_claude_quand_on_retombe_sur_les_regles(monkeypatch, reponse):
    _faux_modele(monkeypatch, reponse)
    d = _dossier("TSLA")
    sceptique.executer(d)
    detail = d.trace[-1].detail
    assert d.objections and "règles" in detail and llm.nom(llm.MODELE_PRINCIPAL) not in detail


# --- Le Sceptique peut avoir tort : chaque vérification dit si elle lui donne raison ---
@pytest.mark.parametrize("ticker, nom, issue", [("TSLA", "robert", "confirmee"),     # écart CAD/USD de 2,1 points
                                                ("BTC-USD", "amira", "ecartee")])     # écart de 1,7 point
def test_le_recalcul_en_devise_confirme_ou_ecarte_l_objection(ticker, nom, issue):
    d = _dossier(ticker, nom=nom)
    assert sceptique._devise(d, d.demande["mesures"], d.demande["ids_faits"])[1] == issue


def test_une_baisse_lente_ecarte_l_objection_de_rapidite():
    d = _dossier("XBB.TO")
    rep, issue = sceptique._une_annee(d, d.demande["mesures"], d.demande["ids_faits"])
    assert issue == "ecartee" and "moins d'un an" in rep


@pytest.mark.parametrize("nom", ["amira", "mateo", "robert"])
def test_chaque_objection_a_une_issue_et_la_trace_fait_le_bilan(nom):
    d = _dossier(PERSONAS[nom]["demande"]["ticker"], nom=nom)
    sceptique.executer(d)
    assert d.objections and all(o.issue in ("confirmee", "ecartee", "limite") for o in d.objections)
    assert "confirmée(s)" in d.trace[-1].detail and "écartée(s)" in d.trace[-1].detail
