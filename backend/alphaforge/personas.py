"""Les 3 personas du cas officiel, complétées par des montants fictifs.

Âge, profil de risque, horizon, expérience et préférences : énoncé officiel.
Montants, fonds d'urgence, sommes à préserver et demandes : SCÉNARIO FICTIF de l'équipe.
"""

PERSONAS = {
    "amira": {
        "profil": {
            "nom": "Amira", "age": 26, "profession": "Ingénieure logicielle",
            "experience": "intermédiaire", "horizon_ans": 15, "tolerance": 80,
            "epargne_totale_cad": 40000, "somme_a_preserver_cad": 5000,
            "revenu_stable": True, "fonds_urgence": True, "dettes_importantes": False,
            "retrait_prevu_ans": None, "exclusions": [],
            "portefeuille_actuel": ["QQQ", "NVDA"],
            "citations": ["Je veux faire croître mon capital à long terme",
                          "Je ne veux pas tout miser sur la techno"],
        },
        "demande": {"texte": "Je veux mettre 10 000 $ en Bitcoin.", "ticker": "BTC-USD", "montant_cad": 10000},
        "source_profil": "Énoncé officiel, persona 01 (risque élevé, 15 ans et plus)",
    },
    "mateo": {
        "profil": {
            "nom": "Mateo", "age": 41, "profession": "Gestionnaire des opérations",
            "experience": "intermédiaire", "horizon_ans": 10, "tolerance": 50,
            "epargne_totale_cad": 120000, "somme_a_preserver_cad": 30000,
            "revenu_stable": True, "fonds_urgence": True, "dettes_importantes": False,
            "retrait_prevu_ans": None, "exclusions": ["Energy"],
            "portefeuille_actuel": ["XIU.TO", "XBB.TO"],
            "citations": ["Je veux éviter les entreprises liées à des controverses environnementales",
                          "Je cherche un équilibre entre croissance et stabilité"],
        },
        "demande": {"texte": "Je veux mettre 15 000 $ dans Enbridge pour les dividendes.", "ticker": "ENB.TO",
                    "montant_cad": 15000},
        "source_profil": "Énoncé officiel, persona 02 (modéré, 8 à 12 ans, ESG)",
    },
    "robert": {
        "profil": {
            "nom": "Robert", "age": 59, "profession": "Professionnel de la santé",
            "experience": "avancée", "horizon_ans": 4, "tolerance": 30,
            "epargne_totale_cad": 400000, "somme_a_preserver_cad": 300000,
            "revenu_stable": True, "fonds_urgence": True, "dettes_importantes": False,
            "retrait_prevu_ans": 4, "exclusions": [],
            "portefeuille_actuel": ["XIU.TO", "XBB.TO", "RY.TO"],
            "citations": ["Je veux préserver mon capital", "Tout le monde parle de Tesla en ce moment"],
        },
        "demande": {"texte": "Je veux mettre 80 000 $ dans Tesla, tout le monde en parle.", "ticker": "TSLA",
                    "montant_cad": 80000},
        "source_profil": "Énoncé officiel, persona 03 (faible à modéré, 3 à 5 ans)",
    },
}
