"""Small qualified corpus: sources, scope of reading, and explicit limitations."""

SOURCES = [
    {
        "id": "starter", "title": "Instantané AlphaForge — données et conventions",
        "publisher": "Datathon Polyfinances / Yahoo Finance / Banque du Canada",
        "url": "/api/source/starter", "as_of": "2026-11-13", "kind": "Données",
        "note": "31 actifs. Prix ajustés, dividendes réinvestis, données en CAD/USD. Univers choisi en 2026 ; aucune preuve ESG ni composition détaillée des FNB.",
        "reading": "README intégral et empreintes des six CSV vérifiés.",
        "tags": ["prices", "risk", "concentration", "esg", "fx"],
    },
    {
        "id": "cfa", "title": "Objectifs, contraintes et capacité à prendre du risque",
        "publisher": "CFA Institute — curriculum 2026",
        "url": "https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/basics-of-portfolio-planning-and-construction",
        "as_of": "2026-11-15", "kind": "Cadre professionnel",
        "note": "Le profil distingue objectifs, horizon, liquidité, volonté et capacité de supporter une perte. L’âge seul ne fixe pas l’allocation.",
        "reading": "Introduction, objectifs pédagogiques et synthèse publics lus ; chapitre payant non lu.",
        "tags": ["profile", "risk", "horizon", "esg"],
    },
    {
        "id": "boc", "title": "Méthode des taux de change",
        "publisher": "Banque du Canada",
        "url": "https://www.bankofcanada.ca/rates/exchange/background-information-on-foreign-exchange-rates/",
        "as_of": "2026-11-15", "kind": "Source de données",
        "note": "Le change sert à une valorisation indicative. La convention de date et le dernier taux disponible sont déclarés ; ce n’est pas un prix exécutable.",
        "reading": "Page méthodologique consultée ; conventions du starter lues.",
        "tags": ["fx", "prices"],
    },
    {
        "id": "fred", "title": "Dates de connaissance et révisions des séries",
        "publisher": "Federal Reserve Bank of St. Louis",
        "url": "https://fred.stlouisfed.org/docs/api/fred/realtime_period.html",
        "as_of": "2026-11-15", "kind": "Documentation",
        "note": "Les séries économiques sont révisables. Une observation ancienne récupérée aujourd’hui ne prouve pas ce qui était connu autrefois. Aucune série macro n’est utilisée pour choisir les allocations ici.",
        "reading": "Documentation Real-Time Periods lue.",
        "tags": ["temporal", "macro", "risk"],
    },
    {
        "id": "method", "title": "Méthode AlphaForge — calculs et limites",
        "publisher": "AlphaForge",
        "url": "/api/source/method", "as_of": "2026-11-15", "kind": "Méthode",
        "note": "Rejeu historique buy-and-hold, conversion CAD, calendrier commun, CAGR sur temps écoulé, baisse depuis un sommet. Les scénarios ne sont ni des prévisions ni des tests indépendants de performance.",
        "reading": "Méthode implémentée et contrôlée par des cas numériques ciblés.",
        "tags": ["risk", "method", "prices", "concentration"],
    },
    {
        "id": "case", "title": "Le défi et ses trois profils fictifs",
        "publisher": "Polyfinances — cas officiel fourni",
        "url": "/api/source/case", "as_of": "2026-11-15", "kind": "Énoncé",
        "note": "Amira, Mateo et Robert sont des situations de référence. Les montants, avoirs et seuils proposés dans l’application sont des hypothèses de démonstration modifiables, ajoutées par AlphaForge.",
        "reading": "Cas converti et cadrage v2 consultés.",
        "tags": ["profile", "simulation"],
    },
]


def lookup(ids: list[str]) -> list[dict]:
    index = {source["id"]: source for source in SOURCES}
    missing = sorted(set(ids) - index.keys())
    if missing:
        raise ValueError(f"Sources inconnues : {', '.join(missing)}")
    return [index[key] for key in dict.fromkeys(ids)]
