"""Cas limites : une entrée impossible donne un verdict gris expliqué, jamais une exception ni un faux « cohérent »."""
import pytest

from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS


def _run(nom, profil=None, demande=None):
    p = PERSONAS[nom]
    return analyser({**p["profil"], **(profil or {})}, {**p["demande"], **(demande or {})})


@pytest.mark.parametrize("profil, demande", [
    ({"epargne_totale_cad": 0}, None),            # avant : ZeroDivisionError (HTTP 500)
    ({"epargne_totale_cad": -8000}, None),        # avant : « -8000 % de son épargne »
    (None, {"montant_cad": -80000}),              # avant : « Cohérent 7/7 »
    (None, {"montant_cad": 0}),
    ({"horizon_ans": 0}, None),
    ({"horizon_ans": -3}, None),
])
def test_valeur_impossible_donne_gris_explique(profil, demande):
    d = _run("robert", profil, demande)
    assert d["verdict"]["etat"] == "indetermine"
    assert d["regles"][0]["code"] == "donnees" and "Il faut" in d["regles"][0]["explication"]


def test_valeurs_valides_inchangees():
    assert _run("robert")["verdict"]["etat"] == "ajustement"


# --- Version ajustée : elle doit améliorer l'état et viser le montant exact de bascule ---
RANG = {"coherent": 0, "ajustement": 1, "incoherent": 2, "indetermine": 3}


def _ajustee(d):
    return next((o for o in d["options"] if o["nom"] == "Version ajustée"), None)


def test_version_ajustee_robert_est_le_montant_exact_de_bascule():
    from alphaforge import gardien
    d = _run("robert")
    aj = _ajustee(d)
    assert aj and aj["etat"] == "coherent"
    # 20 000 $ = 5 % de 400 000 $, exactement le seuil : c'est le plus petit ajustement (avant : 16 000 $).
    assert aj["montant_cad"] == 20000
    p, dem = PERSONAS["robert"]["profil"], PERSONAS["robert"]["demande"]
    m = d["demande"]["mesures"]
    au_dessus = gardien.verdict(gardien.appliquer_regles(p, {**dem, "montant_cad": 20100}, m))["etat"]
    assert au_dessus != "coherent"


@pytest.mark.parametrize("nom, profil", [
    ("robert", {"fonds_urgence": False}),   # avant : « Version ajustée » à 60 000 $, toujours « ajustement »
    ("robert", {}), ("amira", {}), ("mateo", {}),
])
def test_version_ajustee_ameliore_toujours_l_etat(nom, profil):
    d = _run(nom, profil)
    aj = _ajustee(d)
    if aj:
        assert RANG[aj["etat"]] < RANG[d["verdict"]["etat"]], (aj, d["verdict"])


# --- Textes de diversification fidèles aux chiffres ---
def _regle(d, code):
    return next(r for r in d["regles"] if r["code"] == code)


def test_diversification_ok_ne_dit_pas_se_comporte_differemment_et_cite_la_correlation():
    # Amira demande NVDA en détenant QQQ : corrélation de 0,75, sous 0,8 (avant : « Se comporte différemment »).
    d = _run("amira", {"portefeuille_actuel": ["QQQ"]}, {"ticker": "NVDA"})
    r = _regle(d, "diversification")
    assert r["niveau"] == "ok"
    assert "différemment" not in r["explication"]
    assert "0,8" in r["explication"] and "équipe" in r["explication"]


def test_titre_deja_detenu_n_est_pas_presente_comme_placements_inconnus():
    d = _run("robert", {"portefeuille_actuel": ["TSLA"]})
    r = _regle(d, "diversification")
    assert "inconnus" not in r["explication"] and "TSLA" in r["explication"]


# --- Entrées hors bornes ---
def test_exclusion_vide_n_exclut_pas_tout_et_exclusion_en_francais_appliquee():
    d = _run("mateo", {"exclusions": [""]}, {"ticker": "XIU.TO", "texte": ""})
    assert not any(r["code"] == "exclusion" and r["niveau"] == "rouge" for r in d["regles"])   # avant : rouge
    d = _run("mateo", {"exclusions": ["Énergie"]})       # avant : ignorée sans prévenir
    assert _regle(d, "exclusion")["niveau"] == "rouge"


def test_tolerance_bornee_entre_0_et_100():
    from alphaforge.profil import evaluer
    ev = evaluer({**PERSONAS["robert"]["profil"], "tolerance": None,
                  "reponses_tolerance": {"q_amis": 500, "q_mot": 500, "q_chute": 500}})
    assert ev["tolerance"] == 100 and ev["perte_max_tolerance_pct"] <= 40   # avant : 180 %


def test_placement_detenu_inconnu_ignore_sans_bloquer_l_analyse():
    d = _run("robert", {"portefeuille_actuel": ["XIU.TO", "FOO"]})     # avant : KeyError → HTTP 422
    assert d["verdict"]["etat"] == "ajustement"
    assert any("FOO" in t["detail"] for t in d["trace"] if t["agent"] == "Analyste")
