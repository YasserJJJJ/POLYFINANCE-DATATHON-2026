"""L'horizon se lit aussi dans les mots courants ; le placement n'est jamais demandé (il est facultatif)."""
import pytest

from alphaforge.agents import profileur
from alphaforge.dossier import Dossier


@pytest.mark.parametrize("phrase, horizon", [
    ("je veux investir 1000 CAD avec un retour dau moins 30 cad la premiere annee", 1),
    ("je veux investir 10000 CAD pour un gain de 30 CAD d'ici au moins un an", 1),
    ("Je veux placer 5 000 $ dans 10 ans", 10),
    ("sur cinq ans", 5),
    ("je vise l'an prochain", 1),
    ("J'ai 26 ans et je veux mettre 10 000 $ en Bitcoin", None),   # un âge, pas un horizon
    ("Je veux mettre 10 000 $ en Bitcoin.", None),
])
def test_horizon_lu_dans_la_phrase(phrase, horizon):
    assert profileur._trouver_horizon(phrase) == horizon


def test_sans_placement_on_ne_demande_ni_placement_ni_horizon_deja_dit():
    d = Dossier(profil={"nom": "Toi"}, demande={"texte": "je veux investir 1000 CAD avec un retour d'au moins 30 $ la première année",
                                                "ticker": None, "montant_cad": None})
    profileur.executer(d)
    assert d.profil["horizon_ans"] == 1 and d.demande["montant_cad"] == 1000
    assert not any("placement" in q.lower() for q in d.questions)
    assert not any("années" in q for q in d.questions)
