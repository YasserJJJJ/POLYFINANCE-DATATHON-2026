"""Question de précision après le verdict : la réponse du modèle passe les mêmes garde-fous que le verdict."""
import pytest

from alphaforge import llm, precision
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS


@pytest.fixture(scope="module")
def dossier():
    p = PERSONAS["robert"]
    return analyser(p["profil"], p["demande"])


def _modele(monkeypatch, reponse):
    monkeypatch.setattr(precision.llm, "actif", lambda *a: True)
    monkeypatch.setattr(precision.llm, "appeler_json", lambda *a, **k: reponse)
    monkeypatch.setattr(precision.llm, "nom", lambda m: "Claude (faux)")


def test_hors_ligne_renvoie_vers_le_detail(dossier):
    r = precision.repondre(dossier, "Pourquoi incohérent ?")
    assert r["source"] == "hors ligne" and "Le détail" in r["reponse"]


def test_une_reponse_ancree_est_montree_avec_ses_faits(monkeypatch, dossier):
    chute = next(f for f in dossier["faits"] if f["libelle"].startswith("Pire chute de TSLA"))
    _modele(monkeypatch, {"reponse": f"Tesla a déjà perdu {str(abs(chute['valeur'])).replace('.', ',')} % sur la période.",
                          "faits": [chute["id"], "F-999"]})
    r = precision.repondre(dossier, "C'est quoi la pire chute ?")
    assert r["source"] == "Claude (faux)" and r["faits"] == [chute["id"]]


@pytest.mark.parametrize("reponse, defaut", [
    ("Tesla pourrait perdre 87,3 % l'an prochain.", "nombre absent du dossier"),
    ("Je te recommande d'acheter Tesla.", "formule de conseil"),
    ("Ta demande est cohérente avec ta situation.", "contredit le verdict"),
    ("C'est presque trois fois plus risqué que le marché.", "calcul écrit en lettres"),
])
def test_une_reponse_non_ancree_est_refusee(monkeypatch, dossier, reponse, defaut):
    _modele(monkeypatch, {"reponse": reponse, "faits": []})
    r = precision.repondre(dossier, "Explique-moi")
    assert r["reponse"] == precision.REPLI and defaut in r["source"]
