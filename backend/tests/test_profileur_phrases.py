"""Profileur : rien ne se perd en silence dans la phrase libre, et une correction de la personne tient."""
from alphaforge.agents import profileur
from alphaforge.dossier import Dossier
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS


def _lire(texte, profil=None, demande=None):
    d = Dossier(profil=dict(profil or {}), demande={"texte": texte, **(demande or {})})
    profileur.executer(d)
    return d


def test_un_deuxieme_placement_n_est_plus_ignore_en_silence():
    # Phrase de l'audit : avant, le Bitcoin disparaissait sans question.
    d = _lire("Je veux mettre 10 000 $ dans Tesla et 5 000 $ en Bitcoin, j'ai 60 000 $ de côté.")
    assert d.demande["ticker"] == "TSLA"
    assert any("BTC-USD" in q and "un placement à la fois" in q for q in d.questions)


def test_un_seul_placement_ne_declenche_pas_cette_question():
    d = _lire("Je veux mettre 80 000 $ dans Tesla, tout le monde en parle.")
    assert not any("un placement à la fois" in q for q in d.questions)


def test_gain_rapide_sans_risque_est_signale_comme_contradiction():
    d = _lire("Je veux doubler mon argent vite, sans aucun risque, avec 15 000 $ dans Bitcoin.")
    assert any("se contredisent" in t for t in d.profil["tensions"])


def test_un_champ_vide_par_la_personne_n_est_pas_re_rempli_a_l_analyse(monkeypatch):
    # Le modèle lit dans la phrase « pas de fonds d'urgence » et « 9 ans » ; la personne a choisi « Je ne sais pas »
    # (None) et corrigé l'horizon à 4 ans à l'étape 2. Sans le drapeau, l'analyse ré-écrasait ses choix.
    monkeypatch.setattr(profileur, "extraire", lambda texte: ({"fonds_urgence": False, "horizon_ans": 9.0}, "faux modèle"))
    p = {**PERSONAS["robert"]["profil"], "fonds_urgence": None, "horizon_ans": 4}
    dem = {"texte": "Pas de fonds d'urgence, 9 ans.", "ticker": "TSLA", "montant_cad": 80000}
    sans = analyser(p, dem)
    assert sans["profil"]["fonds_urgence"] is False          # comportement sans relecture : champ vide rempli
    avec = analyser(p, {**dem, "texte_lu": True})
    assert avec["profil"]["fonds_urgence"] is None and avec["profil"]["horizon_ans"] == 4
    assert "relue" in avec["profil"]["extraits"]["source"]
