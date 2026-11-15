"""Profileur hors ligne (démo de secours) : il lit le montant à placer, pas l'épargne."""
import pytest

from alphaforge.agents import profileur


@pytest.mark.parametrize("phrase, attendu", [
    # Phrase de l'audit : avant, le montant lu était 80 000 $ (l'épargne).
    ("J'ai 80 000 $ d'épargne, je veux en préserver 50 000, je veux mettre 10 000 $ dans Shopify pour 6 ans.",
     {"ticker": "SHOP.TO", "montant_cad": 10000.0, "epargne_totale_cad": 80000.0}),
    ("I want to put 5000 dollars in Nvidia for 10 years, I have 50k saved.",
     {"ticker": "NVDA", "montant_cad": 5000.0, "epargne_totale_cad": 50000.0}),
    ("J'ai 60 000 $ de côté et je veux placer 5 k$ dans Tesla.",
     {"ticker": "TSLA", "montant_cad": 5000.0, "epargne_totale_cad": 60000.0}),
    ("Je veux mettre 80 000 $ dans Tesla, tout le monde en parle.", {"ticker": "TSLA", "montant_cad": 80000.0}),
])
def test_repli_hors_ligne_lit_le_bon_montant(phrase, attendu):
    champs, source = profileur.extraire(phrase)
    assert source == "mots-clés (hors ligne)" and champs == attendu


def test_la_trace_dit_quand_la_lecture_vient_du_cache(monkeypatch):
    import types
    from alphaforge import llm
    profileur.extraire_llm.cache_clear()
    faux = types.SimpleNamespace(actif=lambda: True, nom=llm.nom, MODELE_LEGER=llm.MODELE_LEGER,
                                 appeler_json=lambda *a, **k: {"ticker": "TSLA", "montant_cad": 1000})
    monkeypatch.setattr(profileur, "llm", faux)
    _, s1 = profileur.extraire("Je veux mettre 1000 $ dans Tesla.")
    _, s2 = profileur.extraire("Je veux mettre 1000 $ dans Tesla.")
    profileur.extraire_llm.cache_clear()
    assert "cache" not in s1 and "cache" in s2
