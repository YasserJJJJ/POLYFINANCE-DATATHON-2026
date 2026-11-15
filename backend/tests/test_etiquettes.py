"""Étiquettes FAIT / HYPOTHESE / SCENARIO : un seuil de l'équipe n'est pas un fait, une situation fictive non plus."""
import re

import pytest

from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS

SEUIL = re.compile(r"\bseuils?\b|\blimite\b|capacité de perte|/100", re.I)
SCENARIO = re.compile(r"\bsi\b.*\b(revivait|se répétait)\b|\bferait baisser\b|\bperdrait\b", re.I)


def _phrases(d):
    t = d["texte"]
    return [ph for s in ("miroir", "pourquoi", "ce_qui_changerait", "limites") for ph in t[s]]


@pytest.mark.parametrize("nom", list(PERSONAS))
def test_aucun_fait_ne_porte_un_seuil_ou_un_scenario(nom):
    p = PERSONAS[nom]
    for ph in _phrases(analyser(p["profil"], p["demande"])):
        if ph["type"] == "FAIT":
            assert not SEUIL.search(ph["texte"]), ph
            assert not SCENARIO.search(ph["texte"]), ph
            assert ph["faits"], ph   # un FAIT cite toujours au moins un F-n


def test_recalcul_du_sceptique_est_un_fait_qui_cite_le_fait_recalcule():
    p = PERSONAS["robert"]   # TSLA est en USD : le Sceptique recalcule la chute sans conversion
    d = analyser(p["profil"], p["demande"])
    usd = next(f for f in d["faits"] if "en USD" in f["libelle"])
    lim = next(ph for ph in d["texte"]["limites"] if ph["texte"].startswith("Recalcul fait"))
    assert lim["type"] == "FAIT" and usd["id"] in lim["faits"]


def test_reformulation_sans_epargne_ni_horizon_et_au_tutoiement():
    profil = {"nom": "Toi", "horizon_ans": None, "epargne_totale_cad": None, "tolerance": 50}
    d = analyser(profil, {"texte": "", "ticker": "TSLA", "montant_cad": 1000})
    r = d["texte"]["reformulation"]
    assert r.startswith("Tu envisages de placer") and "None" not in r and "0 %" not in r


def test_montants_fictifs_seulement_pour_les_personas():
    p = PERSONAS["robert"]
    lim_persona = " ".join(ph["texte"] for ph in analyser(p["profil"], p["demande"])["texte"]["limites"])
    lim_toi = " ".join(ph["texte"] for ph in analyser({**p["profil"], "nom": "Toi"}, p["demande"])["texte"]["limites"])
    assert "fictifs" in lim_persona and "fictifs" not in lim_toi and "saisis" in lim_toi


@pytest.mark.parametrize("nom", list(PERSONAS))
def test_decimales_a_la_francaise_dans_les_textes_affiches(nom):
    p = PERSONAS[nom]
    d = analyser(p["profil"], p["demande"])
    textes = [r["explication"] for r in d["regles"]] + [o["reponse"] for o in d["objections"]] + \
             [ph["texte"] for s in ("pourquoi", "limites") for ph in d["texte"][s]]
    assert not [t for t in textes if re.search(r"\d\.\d", t)], textes


# --- poids_pct : une seule source de vérité pour le pourcentage de l'épargne ---
def test_poids_pct_calcule_une_fois_et_coherent_avec_le_cas_13_vs_12_pourcent():
    from alphaforge.agents import profileur
    from alphaforge.dossier import Dossier
    # Cas réel qui divergeait : 15 000 $ sur 120 000 $ = 12,5 % -> JS « 13 % » (toFixed), Python « 12 % » (round).
    d = Dossier(profil={"epargne_totale_cad": 120000}, demande={"montant_cad": 15000, "texte": ""})
    profileur.executer(d)
    assert d.profil["evaluation"]["poids_pct"] == 12


def test_poids_pct_absent_si_montant_ou_epargne_manquant():
    from alphaforge.agents import profileur
    from alphaforge.dossier import Dossier
    d = Dossier(profil={"epargne_totale_cad": None}, demande={"montant_cad": 15000, "texte": ""})
    profileur.executer(d)
    assert "poids_pct" not in d.profil["evaluation"]
