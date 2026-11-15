"""Le registre des faits décrit la méthode réellement appliquée (recalcul indépendant de l'audit)."""
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS


def _faits(nom):
    p = PERSONAS[nom]
    return {f["libelle"]: f for f in analyser(p["profil"], p["demande"])["faits"]}


def test_methodes_exactes_pour_un_actif_en_usd():
    f = _faits("robert")   # TSLA, en USD
    chute = f["Pire chute de TSLA"]["methode"]
    assert "dernier taux publié" in chute and "dividendes réinvestis" in chute
    assert "change USD/CAD inclus" in f["Volatilité annualisée de TSLA"]["methode"]
    assert "Pire période de 52 semaines (TSLA, cours du vendredi)" in f
    recup = f["Temps entre le creux et le retour au sommet (TSLA)"]
    assert recup["valeur"] == 1.9 and "2,9 an(s)" in recup["methode"]   # 2022-01-03 → 2024-12-05


def test_pas_de_mention_de_change_pour_un_actif_en_cad():
    f = _faits("mateo")    # ENB.TO, en CAD
    assert "change" not in f["Volatilité annualisée de ENB.TO"]["methode"]
