"""Banc de 12 cas du Gardien (voie « Gardien, AWS, tests »).

Chaque cas fixe une persona, une demande et les règles qui doivent se déclencher. Le verdict vient du code,
pas d'un modèle : les tests tournent hors ligne (ALPHAFORGE_LLM=off, voir conftest.py) et donnent toujours
le même résultat.

Les résultats attendus suivent la logique des règles, pas un instantané des chiffres. Ils dépendent des seuils
de `profil.py` (hypothèses de l'équipe) : si un seuil change, ce banc dit quel cas bascule.

Tests de propriété en plus des 12 cas :
- monotonie : un montant plus petit ou un horizon plus long ne rend jamais le verdict pire ;
- stabilité : la même demande, lancée plusieurs fois, donne le même verdict et les mêmes règles ;
- anti-générique : le même placement, demandé par trois profils, ne produit pas la même réponse.
"""
import pytest

from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS

RANG = {"coherent": 0, "ajustement": 1, "incoherent": 2, "indetermine": 3}
NON_OK = ("orange", "rouge", "gris")


def lancer(nom, profil=None, demande=None):
    p = {**PERSONAS[nom]["profil"], **(profil or {})}
    d = {**PERSONAS[nom]["demande"], **(demande or {})}
    return analyser(p, d)


def regles_non_ok(dossier):
    return {r["code"] for r in dossier["regles"] if r["niveau"] in NON_OK}


# (nom du cas, persona, changements de profil, changements de demande, verdict attendu, règles qui se déclenchent)
CAS = [
    ("01 Robert : Tesla, 20 % de l'épargne", "robert", {}, {}, "ajustement", {"concentration"}),
    ("02 Robert : un FNB obligataire", "robert", {}, {"ticker": "XBB.TO", "montant_cad": 20000}, "coherent", set()),
    ("03 Robert : Tesla, sans fonds d'urgence", "robert", {"fonds_urgence": False}, {}, "ajustement",
     {"concentration", "coussin"}),
    ("04 Robert : Tesla, retrait prévu dans 1 an", "robert", {"retrait_prevu_ans": 1}, {}, "incoherent", {"retrait", "concentration"}),
    ("05 Robert : somme à préserver trop haute", "robert", {"somme_a_preserver_cad": 390000}, {}, "incoherent",
     {"preserver", "concentration"}),
    ("06 Robert : toute son épargne en Tesla", "robert", {}, {"montant_cad": 400000}, "incoherent",
     {"capacite", "preserver", "concentration"}),
    ("07 Amira : 10 000 $ en Bitcoin", "amira", {}, {}, "ajustement", {"concentration"}),
    ("08 Amira : un FNB canadien large", "amira", {}, {"ticker": "XIU.TO", "montant_cad": 10000}, "coherent", set()),
    ("09 Amira : Bitcoin, argent requis dans 1 an", "amira", {"retrait_prevu_ans": 1}, {}, "incoherent", {"retrait", "concentration"}),
    ("10 Mateo : Enbridge, secteur exclu", "mateo", {}, {}, "incoherent", {"exclusion"}),
    ("11 Mateo : un FNB ESG compatible", "mateo", {}, {"ticker": "ESGV", "montant_cad": 15000}, "coherent", set()),
    ("12 Amira : horizon et montant absents", "amira", {"horizon_ans": None}, {"montant_cad": None, "texte": ""}, "indetermine", set()),
]


@pytest.mark.parametrize("nom, persona, profil, demande, etat, regles", CAS, ids=[c[0] for c in CAS])
def test_cas(nom, persona, profil, demande, etat, regles):
    d = lancer(persona, profil, demande)
    assert d["verdict"]["etat"] == etat, (nom, d["verdict"], regles_non_ok(d))
    if etat != "indetermine":
        assert regles_non_ok(d) == regles, (nom, regles_non_ok(d))


def test_le_gris_ne_conclut_pas_et_pose_une_question():
    d = lancer("amira", {"horizon_ans": None})
    assert d["verdict"]["etat"] == "indetermine"
    assert d["verdict"]["evaluees"] == 0
    assert d["questions"], "un verdict gris doit dire ce qu'il manque"


@pytest.mark.parametrize("persona", ["amira", "mateo", "robert"])
def test_monotonie_un_montant_plus_petit_n_aggrave_jamais(persona):
    base = PERSONAS[persona]["demande"]["montant_cad"]
    rangs = [RANG[lancer(persona, demande={"montant_cad": round(base * f)})["verdict"]["etat"]]
             for f in (1, 0.75, 0.5, 0.3, 0.1, 0.05)]
    assert rangs == sorted(rangs, reverse=True), rangs


@pytest.mark.parametrize("persona", ["amira", "mateo", "robert"])
def test_monotonie_un_horizon_plus_long_n_aggrave_jamais(persona):
    base = PERSONAS[persona]["profil"]["horizon_ans"]
    rangs = [RANG[lancer(persona, {"horizon_ans": h})["verdict"]["etat"]] for h in (base, base + 2, base + 5, base + 10)]
    assert rangs == sorted(rangs, reverse=True), rangs


@pytest.mark.parametrize("persona", ["amira", "mateo", "robert"])
def test_stabilite_la_meme_demande_donne_le_meme_verdict(persona):
    essais = [lancer(persona) for _ in range(3)]
    assert len({e["verdict"]["etat"] for e in essais}) == 1
    assert len({tuple(sorted(regles_non_ok(e))) for e in essais}) == 1
    assert len({tuple((f["id"], str(f["valeur"])) for f in e["faits"]) for e in essais}) == 1


def test_anti_generique_le_meme_placement_ne_donne_pas_la_meme_reponse():
    """Même titre, même part de l'épargne : trois vies, donc trois lectures différentes."""
    reponses = {}
    for nom in ("amira", "mateo", "robert"):
        epargne = PERSONAS[nom]["profil"]["epargne_totale_cad"]
        reponses[nom] = lancer(nom, demande={"ticker": "TSLA", "montant_cad": round(epargne * 0.2),
                                             "texte": "Je veux mettre 20 % de mon épargne dans Tesla."})
    verdicts = {n: r["verdict"]["etat"] for n, r in reponses.items()}
    seuils = {n: next(r["explication"] for r in d["regles"] if r["code"] == "capacite") for n, d in reponses.items()}
    assert len(set(seuils.values())) == 3, "les explications de perte supportable doivent différer selon le profil"
    assert len(set(verdicts.values())) >= 2, verdicts
    textes = {n: r["texte"]["reformulation"] for n, r in reponses.items()}
    assert len(set(textes.values())) == 3


@pytest.mark.parametrize("persona", ["amira", "mateo", "robert"])
def test_chaque_regle_non_ok_cite_ses_preuves(persona):
    d = lancer(persona)
    ids = {f["id"] for f in d["faits"]}
    for r in d["regles"]:
        if r["niveau"] in ("orange", "rouge") and r["code"] not in ("exclusion",):
            assert any(f in ids for f in r["faits"]), (r["code"], r["faits"])


def test_aucune_phrase_affichee_ne_conseille_d_acheter():
    interdits = ("achète", "achetez", "vends", "vendez", "je recommande")
    for nom in PERSONAS:
        t = lancer(nom)["texte"]
        for section in ("reformulation", "verdict", "miroir", "pourquoi", "ce_qui_changerait", "limites"):
            contenu = t.get(section) or []
            phrases = contenu if isinstance(contenu, list) else [contenu]
            for p in phrases:
                texte = (p["texte"] if isinstance(p, dict) else str(p)).lower()
                assert not any(mot in texte for mot in interdits), (nom, section, texte)
