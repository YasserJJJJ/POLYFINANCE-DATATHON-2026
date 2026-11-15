"""Official personas plus clearly identified, editable demonstration assumptions."""

PERSONAS = [
    {
        "id": "robert", "name": "Robert", "age": 59, "horizon": "3–5 ans",
        "description": "Préserver son capital, sans ignorer un titre qui l’intrigue.",
        "prompt": "Je prépare un besoin de capital dans quatre ans. Un titre comme Tesla m’attire, mais je veux comprendre ce qu’une exposition plus faible changerait au risque de mon portefeuille.",
        "risk_tolerance": "Faible à modérée — persona officiel",
        "goal": "Préservation du capital et cohérence de la concentration",
        "portfolio": [
            {"ticker": "XBB.TO", "weight": 0.35},
            {"ticker": "ZST.TO", "weight": 0.20},
            {"ticker": "XIU.TO", "weight": 0.20},
            {"ticker": "TSLA", "weight": 0.25},
        ],
        "settings": {"horizon_years": 4, "capital": 10000, "currency": "CAD",
                     "max_drawdown_pct": 15, "focus_ticker": "TSLA", "focus_weight": 5},
    },
    {
        "id": "amira", "name": "Amira", "age": 26, "horizon": "15 ans ou plus",
        "description": "Chercher la croissance et rendre la concentration visible.",
        "prompt": "Je souhaite investir à long terme dans la technologie et les cryptoactifs, en gardant une diversification cohérente. Que change une exposition plus faible à NVIDIA ?",
        "risk_tolerance": "Élevée — persona officiel",
        "goal": "Croissance à long terme et diversification",
        "portfolio": [
            {"ticker": "QQQ", "weight": 0.40},
            {"ticker": "NVDA", "weight": 0.30},
            {"ticker": "BTC-USD", "weight": 0.20},
            {"ticker": "XIU.TO", "weight": 0.10},
        ],
        "settings": {"horizon_years": 15, "capital": 10000, "currency": "CAD",
                     "max_drawdown_pct": 35, "focus_ticker": "NVDA", "focus_weight": 10},
    },
    {
        "id": "mateo", "name": "Mateo", "age": 41, "horizon": "8–12 ans",
        "description": "Concilier stabilité, croissance et préférences ESG.",
        "prompt": "Je cherche un équilibre entre croissance et stabilité sur dix ans. Je voudrais exclure mon exposition directe à Exxon et comprendre ce qu’on peut vraiment affirmer sur les autres placements du point de vue ESG.",
        "risk_tolerance": "Modérée — persona officiel",
        "goal": "Équilibre et exclusions documentées",
        "portfolio": [
            {"ticker": "ESGV", "weight": 0.40},
            {"ticker": "XIU.TO", "weight": 0.20},
            {"ticker": "XBB.TO", "weight": 0.30},
            {"ticker": "XOM", "weight": 0.10},
        ],
        "settings": {"horizon_years": 10, "capital": 10000, "currency": "CAD",
                     "max_drawdown_pct": 20, "focus_ticker": "XOM", "focus_weight": 0},
    },
]

BY_ID = {p["id"]: p for p in PERSONAS}
