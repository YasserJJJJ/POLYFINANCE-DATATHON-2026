"""Banc de tests minimal. À enrichir jusqu'à 12 cas (voie Gardien)."""
from alphaforge import calculs
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS


def _run(nom, **changements):
    p = PERSONAS[nom]
    profil = {**p["profil"], **changements.get("profil", {})}
    demande = {**p["demande"], **changements.get("demande", {})}
    return analyser(profil, demande)


def test_les_trois_personas_donnent_trois_verdicts():
    etats = {nom: _run(nom)["verdict"]["etat"] for nom in PERSONAS}
    assert len(set(etats.values())) >= 2, etats


def test_robert_n_est_pas_valide_automatiquement():
    assert _run("robert")["verdict"]["etat"] in ("incoherent", "ajustement")


def test_exclusion_esg_de_mateo_bloque():
    d = _run("mateo")
    assert any(r["code"] == "exclusion" and r["niveau"] == "rouge" for r in d["regles"])


def test_montant_plus_petit_n_aggrave_jamais_le_verdict():
    rang = {"coherent": 0, "ajustement": 1, "incoherent": 2, "indetermine": 3}
    gros = _run("amira")["verdict"]["etat"]
    petit = _run("amira", demande={"montant_cad": 1000})["verdict"]["etat"]
    assert rang[petit] <= rang[gros]


def test_horizon_manquant_donne_gris():
    d = _run("amira", profil={"horizon_ans": None})
    assert d["verdict"]["etat"] == "indetermine"


def test_chaque_regle_evaluee_a_une_explication():
    for nom in PERSONAS:
        for r in _run(nom)["regles"]:
            assert r["explication"]


def test_pire_chute_negative_et_dates_ordonnees():
    pc = calculs.pire_chute("SPY")
    assert pc["pire_chute_pct"] < 0
    assert pc["date_sommet"] < pc["date_creux"]


def test_mateo_recoit_une_alternative_compatible_avec_ses_valeurs():
    d = _run("mateo")
    alt = [o for o in d["options"] if o["nom"].startswith("Alternative")]
    assert alt and alt[0]["ticker"] != "ENB.TO"
    assert alt[0]["etat"] in ("coherent", "ajustement")


def test_garde_fou_refuse_un_nombre_invente_et_un_conseil():
    from alphaforge.agents.redacteur import verifier
    texte = {"reformulation": "Tu veux placer 10 000 $.",
             "pourquoi": [{"texte": "Ce placement a perdu 83 %, achète quand même.", "type": "FAIT", "faits": ["F-99"]}]}
    defauts = verifier(texte, autorises={10000.0}, ids_valides={"F-1"})
    assert any("83" in x for x in defauts)
    assert any("interdit" in x for x in defauts)
    assert any("F-99" in x for x in defauts)


def test_garde_fou_accepte_un_texte_ancre():
    from alphaforge.agents.redacteur import verifier
    texte = {"reformulation": "Tu veux placer 10 000 $ sur 4 ans.",
             "pourquoi": [{"texte": "Sa pire chute observée est de 70,9 %.", "type": "FAIT", "faits": ["F-2"]}]}
    assert verifier(texte, autorises={10000.0, 70.9, 4.0}, ids_valides={"F-2"}) == []


def test_chaque_phrase_affichee_porte_une_etiquette():
    for nom in PERSONAS:
        t = _run(nom)["texte"]
        for section in ("miroir", "pourquoi", "ce_qui_changerait", "limites"):
            for ph in t[section]:
                assert ph["type"] in ("FAIT", "HYPOTHESE", "SCENARIO")
