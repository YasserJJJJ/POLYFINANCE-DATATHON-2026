"""Bougies de l'accueil : calculées par le code, à partir des clôtures du jeu de départ."""
from alphaforge.calculs import bougies_mensuelles
from alphaforge.donnees import serie_cad


def test_une_bougie_par_mois_coherente_et_en_base_100():
    b = bougies_mensuelles("XIU.TO")
    assert 55 <= len(b) <= 62                     # 2021-11 → 2026-11
    assert b[0]["o"] == 100.0
    assert all(x["b"] <= min(x["o"], x["c"]) and x["h"] >= max(x["o"], x["c"]) for x in b)
    assert [x["mois"] for x in b] == sorted({x["mois"] for x in b})
    s = serie_cad("XIU.TO")
    assert abs(b[-1]["c"] - float(s.iloc[-1]) / float(s.iloc[0]) * 100) < 0.01
