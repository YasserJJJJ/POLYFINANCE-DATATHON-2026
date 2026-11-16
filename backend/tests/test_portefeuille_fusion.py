"""Réception K2–K5 : moteur réel, échecs explicites et frontière sans modèle."""
import copy
import json
from types import SimpleNamespace

import pytest

from alphaforge import gardien, llm, portefeuille
from alphaforge.agents import analyste, profileur, sceptique
from alphaforge.dossier import Dossier
from alphaforge.moteurs.historique.analytics import analyze_portfolio
from alphaforge.moteurs.historique.datasets import DataError
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS
from alphaforge.profil import evaluer


def entree(nom="robert", **profil):
    p = copy.deepcopy(PERSONAS[nom])
    return {**p["profil"], **profil}, p["demande"]


def capacite(d):
    return next(r for r in d["regles"] if r["code"] == "capacite")


@pytest.mark.parametrize("nom", ["robert", "amira", "mateo"])
def test_avant_identique_au_recalcul_seul_et_unites_publiques(nom):
    p, dem = entree(nom)
    c = portefeuille.comparer(p, dem)
    seul = analyze_portfolio(p["portefeuille_actuel"], p["epargne_totale_cad"],
                             dataset=portefeuille.jeu_donnees())
    assert c["disponible"]
    assert c["fenetre"] == {"debut": "2021-11-12", "fin": "2026-11-12", "observations": 1228}
    for francais, moteur in portefeuille.METRIQUES.items():
        assert c["avant"][francais] == seul["metrics"][moteur]
    assert c["avant"]["pire_chute_pct"] < -10  # ni fraction, ni seconde multiplication par 100


def test_gain_robert_et_retour_explicite_a_l_approximation(monkeypatch):
    p, dem = entree()
    monkeypatch.delenv("ALPHAFORGE_CAPACITE", raising=False)
    d = analyser(p, dem)
    c, r = d["comparaison"], capacite(d)
    assert c["avant"]["pire_chute_pct"] == pytest.approx(-14.256677)
    assert c["apres"]["pire_chute_pct"] == pytest.approx(-20.595922)
    assert c["ecarts"]["pire_chute_pts"] == pytest.approx(-6.339245)
    assert c["ecarts"]["sens_pire_chute"] == "aggrave"
    assert r["niveau"] == "orange"
    assert "-20,595922" in r["explication"] and "-14,256677" in r["explication"]
    assert all(c["faits"][cle] in r["faits"]
               for cle in ("avant_pire_chute", "apres_pire_chute", "ecart_pire_chute"))
    monkeypatch.setenv("ALPHAFORGE_CAPACITE", "approximation")
    ancien = analyser(p, dem)
    assert ancien["comparaison"] == c
    assert capacite(ancien)["niveau"] == "ok"
    assert "14,2 %" in capacite(ancien)["explication"]
    assert "reste du portefeuille stable" in capacite(ancien)["explication"]
    assert next(o for o in ancien["options"] if o["nom"] == "Version ajustée")["montant_cad"] == 38000


@pytest.mark.parametrize("allocation", [None, [], {}])
def test_portefeuille_inconnu_garde_l_approximation(allocation):
    p, dem = entree(portefeuille_actuel=allocation)
    d = analyser(p, dem)
    assert d["comparaison"] == {"disponible": False, "raison": "Le portefeuille actuel est inconnu."}
    assert "14,2 %" in capacite(d)["explication"]
    assert "reste du portefeuille stable" in capacite(d)["explication"]


@pytest.mark.parametrize("allocation", [
    {"INCONNU": 1}, ["XIU.TO", "INCONNU"], {"XIU.TO": 0.9},
    {"XIU.TO": float("nan")}, "XIU.TO", False,
])
def test_allocations_absentes_ou_invalides_expliquees_sans_exception(allocation):
    p, dem = entree(portefeuille_actuel=allocation)
    c = portefeuille.comparer(p, dem)
    assert c["disponible"] is False and c["raison"]
    assert "avant" not in c and "apres" not in c  # aucun zéro fictif


def test_dataerror_et_fichier_illisible_expliques(monkeypatch):
    p, dem = entree()
    for erreur in (DataError("Colonnes obligatoires absentes."), OSError("test")):
        def echouer():
            raise erreur
        monkeypatch.setattr(portefeuille, "jeu_donnees", echouer)
        c = portefeuille.comparer(p, dem)
        assert not c["disponible"] and c["raison"]


def test_montant_superieur_a_epargne_refuse_par_adaptateur():
    p, dem = entree()
    c = portefeuille.comparer(p, {**dem, "montant_cad": p["epargne_totale_cad"] + 1})
    assert c == {"disponible": False, "raison": "Le montant dépasse l'épargne totale."}


def test_ajout_ligne_existante_et_montant_egal_a_epargne():
    p, dem = entree(portefeuille_actuel={"TSLA": 0.25, "XIU.TO": 0.75})
    c = portefeuille.comparer(p, dem)  # ajout 20 %, et non poids cible 20 %
    assert c["poids_apres"] == pytest.approx({"TSLA": 0.4, "XIU.TO": 0.6})
    tout = portefeuille.comparer(p, {**dem, "montant_cad": p["epargne_totale_cad"]})
    assert tout["disponible"] and tout["poids_apres"] == {"TSLA": 1}


def test_tous_les_nombres_k3_sont_des_faits_et_hypothese_liste_visible():
    p, dem = entree()
    d = analyser(p, dem)
    c, faits = d["comparaison"], {f["id"]: f for f in d["faits"]}
    for bras in ("avant", "apres"):
        for cle, suffixe in [("pire_chute_pct", "pire_chute"), ("volatilite_pct", "volatilite"),
                             ("rendement_annualise_pct", "rendement"), ("valeur_finale_cad", "valeur_finale")]:
            f = faits[c["faits"][f"{bras}_{suffixe}"]]
            assert f["valeur"] == c[bras][cle]
            assert f["type"] == ("FAIT" if bras == "avant" else "SCENARIO")
            assert "historique-B" in f["methode"] and "grille commune" in f["methode"]
            assert f["references"]
    for cle, section, key in [
        ("poids_avant", None, "poids_avant"), ("poids_apres", None, "poids_apres"),
        ("fenetre_portefeuille", None, "fenetre"),
        ("ecart_pire_chute", "ecarts", "pire_chute_pts"), ("ecart_volatilite", "ecarts", "volatilite_pts"),
    ]:
        assert faits[c["faits"][cle]]["valeur"] == (c[section][key] if section else c[key])
    liste = analyser({**p, "portefeuille_actuel": list(p["portefeuille_actuel"])}, dem)
    h = next(f for f in liste["faits"] if f["id"] == liste["comparaison"]["faits"]["h_equiponderation"])
    assert h["type"] == "HYPOTHESE" and h["valeur"] == c["poids_avant"]
    assert liste["comparaison"]["origine_poids"] == "hypothese_equiponderee"
    assert liste["comparaison"]["avant"] == c["avant"]


def test_limites_crypto_et_limites_communes_conservees():
    p, dem = entree("amira")
    c = portefeuille.comparer(p, dem)
    assert any("Crypto échantillonnée aux seules séances communes" in v for v in c["limites"])
    assert any("pas prévision" in v for v in c["limites"])


def test_attribution_ne_rougit_pas_une_demande_qui_reduit_un_depassement_existant():
    p, dem = entree("amira")
    dem["ticker"] = "XIU.TO"
    d = analyser(p, dem)
    c, r = d["comparaison"], capacite(d)
    assert abs(c["avant"]["pire_chute_pct"]) > evaluer(p)["perte_max_capacite_pct"]
    assert c["ecarts"]["sens_pire_chute"] == "ameliore"
    assert r["niveau"] == "orange"  # tolérance encore dépassée, pas rouge pour le risque antérieur
    assert "dépassait déjà" in r["explication"]
    h = next(f for f in d["faits"] if f["id"] == c["faits"]["h_attribution"])
    assert h["type"] == "HYPOTHESE" and h["id"] in r["faits"]
    aggrave = analyser(p, {**dem, "ticker": "BTC-USD"})
    assert capacite(aggrave)["niveau"] == "rouge"


def test_cache_charge_une_fois_compare_les_deux_bras_et_recalcule_par_montant(monkeypatch):
    portefeuille.jeu_donnees.cache_clear()
    portefeuille._comparer.cache_clear()
    charger, comparer = portefeuille.load_dataset, portefeuille.compare_portfolios
    charges, appels = [], []
    def charge(chemin):
        charges.append(str(chemin))
        return charger(chemin)
    def compare(options, **kwargs):
        appels.append(copy.deepcopy(options))
        return comparer(options, **kwargs)
    monkeypatch.setattr(portefeuille, "load_dataset", charge)
    monkeypatch.setattr(portefeuille, "compare_portfolios", compare)
    p, dem = entree()
    a = portefeuille.comparer(p, dem)
    a["avant"]["pire_chute_pct"] = 999
    a["faits"]["avant_pire_chute"] = "F-invente"
    b = portefeuille.comparer({**p, "horizon_ans": 15}, dem)
    c = portefeuille.comparer(p, {**dem, "montant_cad": 40000})
    assert len(charges) == 1 and len(appels) == 2
    assert all([v["id"] for v in appel] == ["avant", "apres"] for appel in appels)
    assert b["avant"]["pire_chute_pct"] < 0 and b["faits"] == {}
    assert c["apres"] != b["apres"] and c["avant"] == b["avant"]


def test_cache_change_restitue_exactement_b_sans_recalculer_ni_anticiper():
    from test_moteur_historique import fixture
    original = fixture()
    vue = portefeuille._DonneesAvecCacheChange(original)
    for jour in original.calendar:
        assert vue.fx_on(jour) == original.fx_on(jour)
        assert vue.fx_on(jour) == original.fx_on(jour)
    assert vue.fx_on.cache_info().misses == 3 and vue.fx_on.cache_info().hits == 3
    assert vue.fx_on("2024-01-02") == (1.2, "2024-01-01", 1)
    with pytest.raises(DataError):
        vue.fx_on("2023-12-31")


def test_recherche_exacte_ne_saute_pas_un_montant_favorable_non_monotone(monkeypatch):
    # L'ancienne dichotomie ratait l'îlot à 800 CAD en rencontrant un milieu défavorable.
    favorables = {200, 300, 800}
    monkeypatch.setattr(gardien, "_etat",
                        lambda _p, d, _m: "coherent" if d["montant_cad"] in favorables else "incoherent")
    assert gardien._montant_exact({}, {}, {}, 200, 1000, "coherent") == 800


@pytest.mark.parametrize("nom,ticker", [
    ("robert", "TSLA"), ("robert", "RY.TO"), ("amira", "BTC-USD"),
    ("amira", "XIU.TO"), ("mateo", "ENB.TO"),
])
def test_sous_calcul_de_recherche_identique_a_compare_portfolios(nom, ticker):
    p, dem = entree(nom)
    for fraction in (0, 0.001, 0.2, 0.435, 1):
        demande = {**dem, "ticker": ticker, "montant_cad": p["epargne_totale_cad"] * fraction}
        complet = portefeuille.comparer(p, demande)
        recherche = portefeuille.comparer_pertes(p, demande)
        assert complet["disponible"] and recherche["disponible"]
        for bras in ("avant", "apres"):
            assert recherche[bras]["pire_chute_pct"] == complet[bras]["pire_chute_pct"]
        for cle in ("pire_chute_pts", "sens_pire_chute"):
            assert recherche["ecarts"][cle] == complet["ecarts"][cle]


def test_revision_amira_xiu_et_grille_non_monotone_expliquee():
    p, dem = entree("amira")
    dem["ticker"] = "XIU.TO"
    assert analyser(p, {**dem, "montant_cad": 14000})["verdict"]["etat"] == "ajustement"
    assert analyser(p, {**dem, "montant_cad": 17500})["verdict"]["etat"] == "coherent"
    d = analyser(p, {**dem, "montant_cad": 35000})
    b, c = d["bascule"], d["comparaison"]
    assert c["ecarts"]["sens_pire_chute"] == "ameliore"
    assert b["monotonie_montant"]["observee"] is False
    h = next(f for f in d["faits"] if f["id"] == c["faits"]["h_non_monotonie"])
    assert h["type"] == "HYPOTHESE" and "exemple_observe" in h["valeur"]
    assert h["id"] in b["monotonie_montant"]["faits"]
    assert all(c["faits"][cle] in h["methode"]
               for cle in ("avant_pire_chute", "apres_pire_chute", "ecart_pire_chute"))
    assert "n'est pas une erreur" in b["monotonie_montant"]["explication"]


@pytest.mark.parametrize("nom", ["robert", "amira"])
def test_tesla_et_bitcoin_aggravants_restent_monotones(nom):
    p, dem = entree(nom)
    d = analyser(p, dem)
    assert d["comparaison"]["ecarts"]["sens_pire_chute"] == "aggrave"
    for horizon in d["bascule"]["horizons"]:
        ligne = sorted((c["montant_cad"], gardien.RANG[c["etat"]])
                       for c in d["bascule"]["cases"] if c["horizon_ans"] == horizon)
        rangs = [rang for _, rang in ligne]
        assert rangs == sorted(rangs)


def test_ajustement_hausse_le_plus_proche_et_texte_purement_constatif():
    p, dem = entree("amira")
    dem.update(ticker="XIU.TO", montant_cad=14000)
    d = analyser(p, dem)
    aj = next(o for o in d["options"] if o["nom"] == "Version ajustée")
    assert aj["montant_cad"] == 16300 and aj["sens"] == "hausse" and aj["etat"] == "coherent"
    texte = d["texte"]["ce_qui_changerait"][0]["texte"]
    assert texte == aj["constat"] and "CAD" in texte
    assert "la règle « Perte supportable » serait respectée" in texte
    assert "hausse" in texte and "ramener" not in texte and "acheter" not in texte
    # Exhaustivité de la proximité : tous les paliers strictement plus proches,
    # de part et d'autre, échouent à améliorer l'état.
    m = d["demande"]["mesures"]
    for montant in range(11800, 16300, gardien.PAS_MONTANT):
        r = gardien.appliquer_regles(p, {**dem, "montant_cad": montant}, m)
        assert gardien.verdict(r)["etat"] != "coherent"
    r = gardien.appliquer_regles(p, {**dem, "montant_cad": 16300}, m)
    assert gardien.verdict(r)["etat"] == aj["etat"]


def test_robert_sans_retrait_question_decisive_sans_inventer_la_date():
    p, dem = entree(retrait_prevu_ans=None)
    d = analyser(p, dem)
    assert d["profil"]["retrait_prevu_ans"] is None and p["retrait_prevu_ans"] is None
    assert d["verdict"]["etat"] == "ajustement"
    question = next(q for q in d["questions"] if "Question décisive" in q)
    assert "4" in question and "Incohérent" in question and "confirmer" in question
    h = next(f for f in d["faits"] if f["libelle"] == "Hypothèse testée : retrait à l'horizon déclaré")
    assert h["type"] == "HYPOTHESE" and h["valeur"] == 4 and h["id"] in question
    assert analyser({**p, "retrait_prevu_ans": 4}, dem)["verdict"]["etat"] == "incoherent"


def test_pas_de_question_decisive_si_le_verdict_ne_change_pas():
    p, dem = entree("mateo")
    assert not any("Question décisive" in q for q in analyser(p, dem)["questions"])


@pytest.mark.parametrize("nom,inferes,issue", [
    ("robert", False, "confirmee"), ("mateo", False, "ecartee"), ("robert", True, "limite"),
])
def test_critique_portefeuille_bornee_et_sans_effet_sur_verdict(nom, inferes, issue):
    p, dem = entree(nom)
    if inferes:
        p["portefeuille_actuel"] = list(p["portefeuille_actuel"])
    d = Dossier(p, dem)
    profileur.executer(d)
    analyste.executer(d)
    avant = gardien.verdict(gardien.appliquer_regles(p, dem, d.demande["mesures"]))
    sceptique.executer(d)
    apres = gardien.verdict(gardien.appliquer_regles(p, dem, d.demande["mesures"]))
    objection = next(o for o in d.objections if "toutes les lignes" in o.texte)
    assert objection.issue == issue and objection.resolue
    assert len(d.objections) <= 3 and avant == apres


@pytest.mark.parametrize("nom", ["robert", "amira", "mateo"])
def test_faux_client_ne_change_aucune_decision_ni_comparaison(nom, monkeypatch):
    p, dem = entree(nom)
    monkeypatch.setenv("ALPHAFORGE_LLM", "off")
    hors_ligne = analyser(p, dem)
    appels = []
    def converse(**kwargs):
        appels.append(kwargs["modelId"])
        # Réponse locale fixe : aucune inférence, aucun réseau.
        return {"output": {"message": {"content": [{"text": json.dumps({
            "objections": [{"code": "comparer_marche", "texte": "Le marché explique-t-il cette chute ?"}],
            "verdict": "coherent", "comparaison": {"avant": 999},
        })}]}}, "stopReason": "end_turn"}
    monkeypatch.setenv("ALPHAFORGE_LLM", "auto")
    monkeypatch.setattr(llm, "_etat", {"indisponible": None})
    monkeypatch.setattr(llm, "_client", {"bedrock": SimpleNamespace(converse=converse)})
    avec_faux = analyser(p, dem)
    assert appels
    for cle in ("verdict", "regles", "bascule", "comparaison"):
        assert avec_faux[cle] == hors_ligne[cle], cle
    # Les options sont identiques ; seul le numéro F-n d'un fait créé après le Sceptique peut glisser.
    sans_ids = lambda options: [{k: v for k, v in o.items() if k != "faits"} for o in options]
    assert sans_ids(avec_faux["options"]) == sans_ids(hors_ligne["options"])
