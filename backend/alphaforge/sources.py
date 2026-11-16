"""Registre des sources : sur quoi repose chaque chiffre, chaque règle et chaque choix des agents.

Trois questions pour chaque élément montré à la personne :
  1. quelle DONNÉE (fichier du jeu de départ, colonne) ;
  2. quelle RÈGLE DE CALCUL (formule exacte, appliquée par le code) ;
  3. sur quelle BASE (réglementation, recherche publiée, ou choix de l'équipe dit comme tel).

Les références viennent surtout du dossier de recherche de l'équipe (« Réutiliser des briques éprouvées, prouver
leur assemblage », Adam, 14 nov. 2026). Le champ `examen` reprend honnêtement le niveau de lecture qu'il indique :
« page lue », « texte analysé », « résumé lu », ou « référence classique, non relue pendant le datathon ». On ne
surclasse jamais une source : une référence non relue n'est pas présentée comme vérifiée.

Un seuil choisi par l'équipe n'a pas de source qui le « prouve » : il est étiqueté HYPOTHESE, avec ce qui l'inspire
et ce qui le critique (ex. l'avis ACVM/OCRI 31-368 reproche les catégories « faible / moyen / élevé » non justifiées).
"""
from __future__ import annotations

# --------------------------------------------------------------------------------------------- références
# type : donnees | reglementation | recherche | methode | interne
REFERENCES: dict[str, dict] = {
    "donnees-profil": {
        "type": "donnees", "auteurs": "Personne utilisatrice ; équipe pour les personas fictives",
        "titre": "Profil et demande saisis : portefeuille_actuel, epargne_totale_cad, montant_cad",
        "annee": "2026", "publication": "Entrées du dossier de simulation", "lien": "",
        "examen": "types et poids validés par le code ; déclarations non vérifiées auprès d'un dépositaire",
        "apport": "Poids et capital de départ déclarés. Les montants et poids des trois personas sont fictifs "
                  "et restent à valider par le porteur. Une liste sans poids est une hypothèse d'équipondération.",
    },
    "moteur-historique-b": {
        "type": "methode", "auteurs": "Équipe AlphaForge, réalisation B (Folio 0.7.0)",
        "titre": "Comparaison appariée cad-buy-and-hold-v1", "annee": "2026",
        "publication": "backend/alphaforge/moteurs/historique/analytics.py et datasets.py",
        "lien": "", "examen": "code transféré de l'archive B ; empreintes vérifiées ; tests d'origine exécutés",
        "apport": "Achat-conservation en CAD sur la grille commune fixe ; FX du jour ou antérieur (7 jours maximum). "
                  "Pire baisse sommet-creux, volatilité des rendements simples annualisée par la fréquence observée, "
                  "TCAC sur le temps calendaire. Les sorties *_pct sont déjà en points. "
                  "Les limites de meta.limitations et les avertissements des instruments restent dans le dossier.",
    },
    "allocation-a": {
        "type": "methode", "auteurs": "Équipe AlphaForge, réalisation A (datathon2026 0.1.0)",
        "titre": "Ajout proportionnel blend", "annee": "2026",
        "publication": "backend/alphaforge/moteurs/allocation.py, original analytics.py:192-198",
        "lien": "", "examen": "fonction copiée de l'archive A et testée, formule inchangée",
        "apport": "Réduit les poids initiaux par 1 − part, puis ajoute part à la ligne demandée, même déjà détenue.",
    },
    "fusion-k5": {
        "type": "interne", "auteurs": "Équipe AlphaForge",
        "titre": "Contrats K3–K5 et attribution de la perte supportable", "annee": "2026",
        "publication": "docs/fusion/CADRE-COMMUN.md, sections 6 et 14", "lien": "",
        "examen": "mandat d'intégration lu ; hypothèse d'équipe à valider par le porteur (décision 4)",
        "apport": "Seuils inchangés, évalués sur le portefeuille après la demande. Un dépassement antérieur de "
                  "capacité ne rend pas la demande rouge si elle n'aggrave pas la baisse. La tolérance reste évaluée. "
                  "Retour au calcul antérieur avec ALPHAFORGE_CAPACITE=approximation.",
    },
    # ---- Données (le jeu de départ officiel, fourni par les organisateurs) ----
    "donnees-prix": {
        "type": "donnees", "auteurs": "Organisateurs du datathon ; Yahoo Finance via yfinance",
        "titre": "prices_daily.csv, colonne adj_close (jeu de départ AlphaForge)", "annee": "2026",
        "publication": "data/raw/alphaforge_starter/, extrait le 2026-11-13, fenêtre 2021-11-12 → 2026-11-12",
        "lien": "https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html",
        "examen": "fichier lu et recalculé indépendamment (audit du 15 nov.)",
        "apport": "Prix ajustés des dividendes et des fractionnements, pour 31 actifs. Conditions Yahoo : usage "
                  "personnel, pas de collecte automatisée sans permission.",
    },
    "donnees-change": {
        "type": "donnees", "auteurs": "Banque du Canada", "titre": "Taux de change USD/CAD quotidien (API Valet), "
        "fx_usdcad_daily.csv, colonne usdcad", "annee": "2026", "publication": "jeu de départ AlphaForge",
        "lien": "https://www.bankofcanada.ca/rates/exchange/background-information/",
        "examen": "méthodologie : texte analysé (dossier de recherche) ; fichier recalculé (audit)",
        "apport": "Taux indicatif : moyenne de cotations relevées entre 8 h et 16 h (heure de l'Est), publiée les jours "
                  "ouvrables de la Banque. Ce n'est pas un cours de clôture.",
    },
    "donnees-univers": {
        "type": "donnees", "auteurs": "Organisateurs du datathon", "titre": "assets_universe.csv, colonnes sector, "
        "currency, asset_class", "annee": "2026", "publication": "jeu de départ AlphaForge",
        "lien": "", "examen": "fichier lu",
        "apport": "Secteur, devise et classe de chaque actif. Étiquettes simplifiées : ce n'est ni une classification "
                  "officielle ni une donnée ESG.",
    },
    "yfinance-reparation": {
        "type": "methode", "auteurs": "Mainteneurs de yfinance", "titre": "Price repair (documentation)",
        "annee": "2026", "publication": "dépôt ranaroussi/yfinance",
        "lien": "https://github.com/ranaroussi/yfinance/blob/main/doc/source/advanced/price_repair.rst",
        "examen": "texte analysé (dossier de recherche)",
        "apport": "Les mainteneurs documentent des ajustements manquants ou fictifs dans les données Yahoo et écrivent "
                  "que seules les données américaines semblent parfaites : une limite pour les titres du TSX.",
    },
    # ---- Réglementation canadienne (structure du profil, sans prétendre à une conformité) ----
    "acvm-31-103cp": {
        "type": "reglementation", "auteurs": "Autorités canadiennes en valeurs mobilières (ACVM)",
        "titre": "Instruction complémentaire 31-103CP, articles 13.2 et 13.3 (connaissance du client, convenance)",
        "annee": "2021", "publication": "version consolidée au 2021-03-01",
        "lien": "https://fcnb.ca/sites/default/files/2022-01/31-103CP-CONS-2021-03-01-E.pdf",
        "examen": "texte analysé, extraction automatique (dossier de recherche)",
        "apport": "Six éléments de connaissance du client (situation financière, besoins de liquidité, horizon dont la "
                  "faisabilité doit être évaluée…). Tolérance au risque et capacité à subir des pertes sont deux "
                  "considérations distinctes.",
    },
    "ocri-gn-3400": {
        "type": "reglementation", "auteurs": "Organisme canadien de réglementation des investissements (OCRI)",
        "titre": "GN-3400-21-004, Know-your-client and suitability determination for retail clients",
        "annee": "2021", "publication": "en vigueur le 2021-12-31",
        "lien": "https://www.ciro.ca/news-room/publications/know-your-client-and-suitability-determination-retail-clients",
        "examen": "texte analysé, extraction automatique (dossier de recherche)",
        "apport": "Le profil de risque doit refléter le plus bas des deux : tolérance ou capacité.",
    },
    "acvm-ocri-31-368": {
        "type": "reglementation", "auteurs": "ACVM et OCRI", "titre": "Avis conjoint du personnel 31-368, Réformes "
        "axées sur le client", "annee": "2025", "publication": "2025-12-10, examen de 105 entreprises",
        "lien": "https://www.asc.ca/-/media/ASC-Documents-part-1/Regulatory-Instruments/2025/12/6255537-CSA-CIRO-Notice-31-368-Client-Focused-Reforms.pdf",
        "examen": "texte analysé partiel, extraction automatique (dossier de recherche)",
        "apport": "Reproche de fusionner tolérance et capacité, d'utiliser des catégories « faible, moyen, élevé » sans "
                  "justification, et précise que noter que le client a dirigé l'opération est insuffisant.",
    },
    "osc-iap-2015": {
        "type": "reglementation", "auteurs": "Brayman, Finke, Bessner, Grable, Griffin, Clement (OSC IAP)",
        "titre": "Current Practices for Risk Profiling in Canada", "annee": "2015",
        "publication": "rapport commandé par la Commission des valeurs mobilières de l'Ontario",
        "lien": "https://www.osc.ca/sites/default/files/2021-02/iap_20151112_risk-profiling-report.pdf",
        "examen": "texte analysé partiel, extraction automatique (dossier de recherche)",
        "apport": "75 % des questionnaires analysés avaient des pondérations arbitraires : publier son barème et le "
                  "dire hypothétique est le minimum honnête.",
    },
    "esma-2022": {
        "type": "reglementation", "auteurs": "Autorité européenne des marchés financiers (ESMA)",
        "titre": "Orientations MiFID II sur certains aspects de l'adéquation (ESMA35-43-3172)", "annee": "2022",
        "publication": "2022-09-23",
        "lien": "https://prod.finanssivalvonta.fi/globalassets/en/publications/supervision-releases/2023/esma35-43-3172_guidelines_on_certain_aspects_of_the_mifid_ii_suitability_requirements.pdf",
        "examen": "texte analysé (dossier de recherche)",
        "apport": "Recueillir les préférences de durabilité de la personne (exclusions déclarées) plutôt que les "
                  "déduire ; déconseille l'auto-évaluation seule de la tolérance au profit de la perte acceptée.",
    },
    # ---- Recherche en finance ----
    "markowitz-1952": {
        "type": "recherche", "auteurs": "H. Markowitz", "titre": "Portfolio Selection", "annee": "1952",
        "publication": "Journal of Finance 7(1), p. 77-91", "lien": "https://doi.org/10.2307/2975974",
        "examen": "référence classique, non relue pendant le datathon",
        "apport": "La diversification réduit le risque à condition que les placements ne bougent pas ensemble : "
                  "d'où la corrélation et la limite de concentration.",
    },
    "demiguel-2009": {
        "type": "recherche", "auteurs": "V. DeMiguel, L. Garlappi, R. Uppal",
        "titre": "Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy?", "annee": "2009",
        "publication": "Review of Financial Studies 22(5)",
        "lien": "https://ideas.repec.org/a/oup/rfinst/v22y2009i5p1915-1953.html", "examen": "résumé lu (dossier de recherche)",
        "apport": "Les rendements moyens historiques ne sont pas estimables avec précision sur quelques années : on ne "
                  "s'en sert jamais pour décider, et on affiche leur erreur type.",
    },
    "chekhlov-2005": {
        "type": "recherche", "auteurs": "A. Chekhlov, S. Uryasev, M. Zabarankin",
        "titre": "Drawdown Measure in Portfolio Optimization", "annee": "2005",
        "publication": "International Journal of Theoretical and Applied Finance 8(1)", "lien": "",
        "examen": "référence bibliographique, non relue (dossier de recherche : [NV])",
        "apport": "Définition de la baisse maximale depuis un sommet (drawdown), mesure de risque compréhensible.",
    },
    "chhabra-2005": {
        "type": "recherche", "auteurs": "A. B. Chhabra",
        "titre": "Beyond Markowitz: A Comprehensive Wealth Allocation Framework for Individual Investors", "annee": "2005",
        "publication": "Journal of Wealth Management 7(4)", "lien": "",
        "examen": "référence citée dans le plan de l'équipe, non relue pendant le datathon",
        "apport": "Séparer une part protégée de l'épargne (« somme à préserver ») de la part exposée au marché.",
    },
    "das-2010": {
        "type": "recherche", "auteurs": "S. Das, H. Markowitz, J. Scheid, M. Statman",
        "titre": "Portfolio Optimization with Mental Accounts", "annee": "2010", "publication": "JFQA 45(2)",
        "lien": "https://ideas.repec.org/a/cup/jfinqa/v45y2010i02p311-334_00.html", "examen": "condensé CFA lu (dossier de recherche)",
        "apport": "Raisonner par objectif et par seuil de perte (compte mental) plutôt que par un coefficient abstrait.",
    },
    "grable-lytton-1999": {
        "type": "recherche", "auteurs": "J. Grable, R. H. Lytton",
        "titre": "Financial risk tolerance revisited: the development of a risk assessment instrument", "annee": "1999",
        "publication": "Financial Services Review 8(3), p. 163-181", "lien": "https://openjournals.libs.uga.edu/fsr/article/view/3240",
        "examen": "lien vers la rétrospective de 15 ans (Kuzniak et al., 2015), résumé lu ; article de 1999 non relu",
        "apport": "Les 3 questions sont adaptées de cette échelle (fidélité interne α = 0,77 sur 160 279 répondants "
                  "selon la rétrospective). Les points par réponse sont un barème de l'équipe.",
    },
    "berg-2022": {
        "type": "recherche", "auteurs": "F. Berg, J. F. Kölbel, R. Rigobon", "titre": "Aggregate Confusion: The Divergence of ESG Ratings",
        "annee": "2022", "publication": "Review of Finance 26(6)", "lien": "https://academic.oup.com/rof/article/26/6/1315/6590670",
        "examen": "page de synthèse lue (dossier de recherche)",
        "apport": "Les notes ESG de six agences ne corrèlent qu'entre 0,38 et 0,71 : on n'invente pas de note ESG, on "
                  "applique seulement les exclusions déclarées par la personne.",
    },
    # ---- Explicabilité et conception des agents ----
    "wachter-2018": {
        "type": "recherche", "auteurs": "S. Wachter, B. Mittelstadt, C. Russell",
        "titre": "Counterfactual Explanations without Opening the Black Box", "annee": "2018", "publication": "Harvard JOLT",
        "lien": "https://arxiv.org/abs/1711.00399", "examen": "résumé lu (dossier de recherche)",
        "apport": "Expliquer une décision par le plus petit changement qui la ferait basculer : la version ajustée et "
                  "les curseurs de bascule.",
    },
    "miller-2019": {
        "type": "recherche", "auteurs": "T. Miller", "titre": "Explanation in Artificial Intelligence: Insights from the Social Sciences",
        "annee": "2019", "publication": "Artificial Intelligence 267", "lien": "https://arxiv.org/abs/1706.07269",
        "examen": "texte analysé, première moitié (dossier de recherche)",
        "apport": "Une bonne explication est contrastive (« ceci plutôt que cela ») et sélective : on commence par ce qui "
                  "pèse le plus dans le verdict.",
    },
    "turpin-2023": {
        "type": "recherche", "auteurs": "M. Turpin, J. Michael, E. Perez, S. Bowman",
        "titre": "Language Models Don't Always Say What They Think", "annee": "2023", "publication": "NeurIPS 2023",
        "lien": "https://arxiv.org/abs/2305.04388", "examen": "résumé lu (dossier de recherche)",
        "apport": "Le raisonnement affiché par un modèle peut déformer la vraie raison de sa réponse : il ne peut pas "
                  "servir d'explication, d'où des chiffres et un verdict produits par le code.",
    },
    "gao-pal-2023": {
        "type": "recherche", "auteurs": "L. Gao, A. Madaan, S. Zhou et al.", "titre": "PAL: Program-aided Language Models",
        "annee": "2023", "publication": "arXiv 2211.10435 ; ICML 2023", "lien": "https://arxiv.org/abs/2211.10435",
        "examen": "résumé lu (dossier de recherche)",
        "apport": "Déléguer le calcul au code plutôt qu'au modèle réduit les erreurs numériques, y compris sur des "
                  "questions financières (FinQA, TAT-QA).",
    },
    "gou-critic-2024": {
        "type": "recherche", "auteurs": "Gou et al.", "titre": "CRITIC: Large Language Models Can Self-Correct with "
        "Tool-Interactive Critiquing", "annee": "2024", "publication": "ICLR 2024", "lien": "https://arxiv.org/abs/2305.11738",
        "examen": "résumé lu (dossier de recherche)",
        "apport": "Une critique aide quand elle s'appuie sur un outil qui vérifie : le Sceptique ne peut demander que des "
                  "vérifications exécutées par le code.",
    },
    "huang-2024": {
        "type": "recherche", "auteurs": "Huang et al.", "titre": "Large Language Models Cannot Self-Correct Reasoning Yet",
        "annee": "2024", "publication": "ICLR 2024", "lien": "https://arxiv.org/abs/2310.01798", "examen": "résumé lu (dossier de recherche)",
        "apport": "Sans retour extérieur, un modèle se corrige mal lui-même : le texte du Rédacteur est contrôlé par le "
                  "code, pas par lui-même.",
    },
    "choi-2025": {
        "type": "recherche", "auteurs": "Choi, Zhu, Li", "titre": "Debate or Vote: Which Yields Better Decisions "
        "in Multi-Agent LLMs?", "annee": "2025", "publication": "NeurIPS 2025", "lien": "https://arxiv.org/abs/2508.17536",
        "examen": "résumé lu (dossier de recherche)",
        "apport": "Le débat libre entre agents n'améliore pas seul l'exactitude : on a préféré une contradiction outillée "
                  "et un arbitre en code (le Gardien).",
    },
    "anthropic-2024": {
        "type": "recherche", "auteurs": "Erik S., Barry Zhang (Anthropic)", "titre": "Building effective agents",
        "annee": "2024", "publication": "billet d'ingénierie, 2024-12-19", "lien": "https://www.anthropic.com/engineering/building-effective-agents",
        "examen": "page lue, extraction automatique (dossier de recherche) ; témoignage de praticiens",
        "apport": "Préférer un flux simple et explicite, aux étapes fixes, à un orchestrateur piloté par un modèle.",
    },
    "kim-2025": {
        "type": "recherche", "auteurs": "Kim, Gu, Park et al.", "titre": "Towards a Science of Scaling Agent Systems",
        "annee": "2025", "publication": "arXiv 2512.08296", "lien": "https://arxiv.org/abs/2512.08296",
        "examen": "résumé lu (dossier de recherche)",
        "apport": "Plus d'agents n'est pas toujours mieux (de +80,8 % à -70,0 % selon la tâche) ; les erreurs se "
                  "propagent sans vérification centralisée : d'où un Gardien unique qui décide.",
    },
    "clamber-2024": {
        "type": "recherche", "auteurs": "Zhang et al.", "titre": "CLAMBER: A Benchmark of Identifying and Clarifying "
        "Ambiguous Information Needs", "annee": "2024", "publication": "ACL 2024", "lien": "https://arxiv.org/html/2405.12063v2",
        "examen": "texte analysé, extraction automatique (dossier de recherche)",
        "apport": "Un modèle seul ne repère que 38 % des contradictions : le Profileur lit la phrase, mais le code valide "
                  "chaque champ et la personne corrige à l'étape 2.",
    },
    "ross-lo-2026": {
        "type": "recherche", "auteurs": "Ross, Lo", "titre": "One Size Fits None: Heuristic Collapse in LLM Investment Advice",
        "annee": "2026", "publication": "arXiv 2604.23837", "lien": "https://arxiv.org/abs/2604.23837",
        "examen": "texte analysé, extraction automatique (dossier de recherche)",
        "apport": "Les conseils de modèles GPT dépendent à 57-88 % de la seule tolérance déclarée : les jauges et la "
                  "capacité sont calculées par le code, jamais par le modèle.",
    },
    "bansal-2021": {
        "type": "recherche", "auteurs": "G. Bansal et al.", "titre": "Does the Whole Exceed its Parts? The Effect of AI "
        "Explanations on Complementary Team Performance", "annee": "2021", "publication": "CHI 2021",
        "lien": "https://arxiv.org/abs/2006.14779", "examen": "résumé lu (dossier de recherche)",
        "apport": "Une explication augmente l'acceptation d'une recommandation, juste ou fausse : on montre les limites "
                  "et l'incertitude, pas seulement des arguments.",
    },
    "van-der-bles-2020": {
        "type": "recherche", "auteurs": "A. M. van der Bles, S. van der Linden, A. Freeman, D. Spiegelhalter",
        "titre": "The effects of communicating uncertainty on public trust in facts and numbers", "annee": "2020",
        "publication": "PNAS 117(14)", "lien": "https://core.ac.uk/download/305110478.pdf", "examen": "texte analysé (dossier de recherche)",
        "apport": "Une fourchette chiffrée réduit peu la confiance (d = -0,15), bien moins qu'une incertitude vague : "
                  "on affiche l'erreur type plutôt qu'un « environ ».",
    },
    "dossier-adam": {
        "type": "interne", "auteurs": "Équipe AlphaForge (Adam)", "titre": "Réutiliser des briques éprouvées, prouver leur "
        "assemblage (dossier de recherche documentaire)", "annee": "2026", "publication": "document interne du 2026-11-14",
        "lien": "", "examen": "document de l'équipe ; chaque affirmation y porte son propre niveau de preuve",
        "apport": "Synthèse de sept carnets de recherche : choix des méthodes, pièges des données, conception des agents.",
    },
}

# --------------------------------------------------------------------------------------------- justifications
# Pour chaque élément : données utilisées, règle de calcul appliquée par le code, références, et, s'il y a lieu,
# l'hypothèse de l'équipe (un choix, pas un fait).
JUSTIFICATIONS: dict[str, dict] = {
    "portefeuille": {
        "donnees": ["donnees-prix", "donnees-change", "donnees-univers", "donnees-profil"],
        "calcul": "Deux allocations, un appel à compare_portfolios de B, même fenêtre et grille. "
                  "Écarts = après − avant ; écart de pire baisse négatif → aggrave, positif → ameliore, nul → neutre. "
                  "Jamais de soustraction entre mesures de C et de B.",
        "references": ["moteur-historique-b"],
    },
    "allocation-ajout": {
        "donnees": ["donnees-profil"], "calcul": "part = montant / épargne ; poids après = poids avant × (1 − part), "
                                 "puis ajout de part à la ligne demandée.",
        "references": ["allocation-a", "moteur-historique-b"],
    },
    "h_equiponderation": {
        "donnees": [], "calcul": "Une liste de N symboles distincts sans poids reçoit 1/N par ligne.",
        "references": ["fusion-k5"],
        "hypothese": "Poids inconnus supposés égaux ; aucune déclaration de la personne n'est inventée.",
    },
    "h_attribution": {
        "donnees": [], "calcul": "Si la pire baisse avant dépasse déjà la capacité et que l'écart après − avant "
                                 "est positif ou nul, ne pas attribuer le rouge à cette demande.",
        "references": ["fusion-k5"],
        "hypothese": "Choix d'attribution de l'équipe à valider ; aucun seuil modifié.",
    },
    "h_non_monotonie": {
        "donnees": ["donnees-profil"],
        "calcul": "Chaque montant est recalculé. Un ajout diversifiant peut réduire la pire baisse et améliorer "
                  "le verdict quand son montant augmente. La grille conserve ces résultats.",
        "references": ["fusion-k5", "moteur-historique-b"],
        "hypothese": "Invariant 7 révisé par le porteur : monotonie conditionnelle, aucun lissage de la grille.",
    },
    "h_retrait_decisif": {
        "donnees": [], "calcul": "Date de retrait absente : comparer le verdict fourni au verdict avec retrait "
                                 "à l'horizon déclaré. Question décisive seulement si l'état diffère.",
        "references": ["acvm-31-103cp", "fusion-k5"],
        "hypothese": "Hypothèse testée séparément ; ni la date ni le verdict affiché ne sont remplacés.",
    },
    # ---- Faits calculés par l'Analyste ----
    "chute": {"donnees": ["donnees-prix", "donnees-change"],
              "calcul": "Pire chute = min sur t de (P_t / max_{s≤t} P_s − 1), P en $ CA (adj_close × taux USD/CAD du "
                        "jour ou dernier taux publié).",
              "references": ["chekhlov-2005", "yfinance-reparation"]},
    "recuperation": {"donnees": ["donnees-prix", "donnees-change"],
                     "calcul": "Années = (premier jour où P retrouve le sommet précédant le creux − date du creux) / 365,25. "
                               "Si le sommet n'est pas retrouvé : années écoulées depuis le creux (borne minimale).",
                     "references": ["chekhlov-2005"]},
    "volatilite": {"donnees": ["donnees-prix", "donnees-change"],
                   "calcul": "Écart-type des rendements log quotidiens × √252 (actions, FNB) ou × √365 (cryptoactifs, "
                             "cotés 7 j/7). Cotations par an mesurées dans le jeu : 250,8 et 365,2.",
                   "references": ["markowitz-1952", "dossier-adam"]},
    "rendement": {"donnees": ["donnees-prix", "donnees-change"],
                  "calcul": "TCAC = (P_fin / P_début)^(1 / années) − 1. Erreur type de la moyenne ≈ volatilité / √années.",
                  "references": ["demiguel-2009", "van-der-bles-2020"]},
    "pire12": {"donnees": ["donnees-prix", "donnees-change"],
               "calcul": "Pire rendement sur 52 semaines glissantes, cours du vendredi. Mesure hebdomadaire : peut "
                         "sous-estimer la pire baisse sur 12 mois de cotations quotidiennes.",
               "references": ["chekhlov-2005"]},
    "perte": {"donnees": ["donnees-prix", "donnees-change"],
              "calcul": "Perte de scénario = montant placé × pire chute observée. Scénario fictif : la prochaine baisse "
                        "peut être plus forte ou plus faible.",
              "references": ["das-2010"]},
    "correlation": {"donnees": ["donnees-prix", "donnees-change"],
                    "calcul": "Corrélation de Pearson des rendements hebdomadaires (cours du vendredi), pour aligner "
                              "les calendriers TSX, américains et crypto (7 j/7).",
                    "references": ["markowitz-1952", "dossier-adam"]},
    "secteur": {"donnees": ["donnees-univers"], "calcul": "Lu tel quel dans assets_universe.csv.",
                "references": ["esma-2022", "berg-2022"]},
    "reference": {"donnees": ["donnees-prix"], "calcul": "Même calcul de pire chute que pour la demande, sur XIU.TO "
                  "(indice canadien large), pour distinguer le risque du placement de celui du marché.",
                  "references": ["chekhlov-2005"]},
    "devise_usd": {"donnees": ["donnees-prix"], "calcul": "Même calcul de pire chute, sur adj_close en USD, sans "
                   "conversion, pour mesurer l'effet du change.", "references": ["donnees-change"]},
    "alternative": {"donnees": ["donnees-prix", "donnees-change", "donnees-univers"],
                    "calcul": "Premier placement large, hors des secteurs exclus, que le Gardien juge acceptable au même montant.",
                    "references": ["esma-2022", "berg-2022"]},
    # ---- Hypothèses de l'équipe (seuils et barèmes) ----
    "h_perte": {"donnees": [], "calcul": "Perte supportable = 5 + 0,35 × score retenu (score de 0 à 100), soit de 5 % à 40 % "
                "de l'épargne. Score retenu = le plus bas entre tolérance et capacité.",
                "references": ["ocri-gn-3400", "acvm-31-103cp", "osc-iap-2015"],
                "hypothese": "Barème linéaire choisi par l'équipe, non validé empiriquement ; publié pour être discuté."},
    "h_capacite": {"donnees": [], "calcul": "Capacité = 50 points, puis + ou − selon horizon, revenu stable, fonds "
                   "d'urgence, dettes et retrait prévu (barème détaillé à l'étape 2).",
                   "references": ["acvm-31-103cp", "osc-iap-2015"],
                   "hypothese": "Barème de points choisi par l'équipe à partir des éléments de connaissance du client."},
    "h_concentration": {"donnees": [], "calcul": "Part maximale de l'épargne dans un actif très volatil = 5 + 0,15 × "
                        "score retenu, soit de 5 % à 20 %.",
                        "references": ["markowitz-1952", "acvm-ocri-31-368"],
                        "hypothese": "Fonction continue choisie par l'équipe, à la place de trois paliers : l'avis 31-368 "
                                     "critique les catégories « faible, moyen, élevé » non justifiées, et un point de score "
                                     "ne doit pas faire basculer le verdict."},
    "h_titre": {"donnees": [], "calcul": "Part maximale de l'épargne dans un seul titre (action ou cryptoactif) qui n'est "
                "pas très volatil = 2 × le seuil des actifs très volatils, soit de 10 % à 40 %.",
                "references": ["markowitz-1952"],
                "hypothese": "Facteur 2 choisi par l'équipe : une seule entreprise porte un risque propre que la "
                             "volatilité ne montre pas toujours."},
    "h_retrait_proche": {"donnees": [], "calcul": "Un retrait prévu dans 5 ans ou moins rend rouge une concentration "
                         "au-delà du seuil, sur un actif très volatil.",
                         "references": ["acvm-31-103cp"],
                         "hypothese": "Horizon de 5 ans choisi par l'équipe : peu de temps pour attendre une remontée."},
    "h_volatil": {"donnees": [], "calcul": "Un actif est « très volatil » au-delà de 30 %/an (règle de concentration) et "
                  "« volatil » au-delà de 25 %/an (règle de retrait).", "references": ["markowitz-1952"],
                  "hypothese": "Seuils choisis par l'équipe ; à titre de repère, l'indice canadien large (XIU.TO) a une "
                               "volatilité de 13,1 %/an sur la période."},
    "h_correlation": {"donnees": [], "calcul": "On parle de fausse diversification à partir d'une corrélation de 0,8 "
                      "avec un placement déjà détenu.", "references": ["markowitz-1952"],
                      "hypothese": "Seuil choisi par l'équipe."},
    # ---- Règles du Gardien ----
    "regle-capacite": {"calcul": "Impact = |pire baisse du portefeuille après|, comparé aux seuils de capacité "
                       "(rouge) et de tolérance (orange). Un dépassement antérieur de capacité non aggravé ne "
                       "rend pas la demande rouge. Sans comparaison, ou avec ALPHAFORGE_CAPACITE=approximation : "
                       "(montant / épargne) × |pire chute du titre C|, reste du portefeuille supposé stable.",
                       "references": ["ocri-gn-3400", "acvm-31-103cp", "chekhlov-2005",
                                      "moteur-historique-b", "fusion-k5"]},
    "regle-preserver": {"calcul": "Rouge si épargne − montant < somme à préserver.", "references": ["chhabra-2005", "das-2010"]},
    "regle-exclusion": {"calcul": "Rouge si le secteur de l'actif fait partie des exclusions déclarées.",
                        "references": ["esma-2022", "berg-2022"]},
    "regle-retrait": {"calcul": "Rouge si l'actif est volatil (> 25 %/an) et que le retrait prévu arrive avant la "
                      "récupération observée.", "references": ["acvm-31-103cp"]},
    "regle-horizon": {"calcul": "Orange si l'horizon est plus court que le temps de récupération observé après la pire chute.",
                      "references": ["acvm-31-103cp", "chekhlov-2005"]},
    "regle-concentration": {"calcul": "Orange si la part de l'épargne dépasse le seuil de concentration du profil : seuil "
                            "des actifs très volatils (> 30 %/an), ou seuil d'un seul titre moins volatil. Rouge si, en "
                            "plus, l'actif est très volatil et qu'un retrait est prévu dans 5 ans ou moins.",
                            "references": ["markowitz-1952", "acvm-ocri-31-368", "acvm-31-103cp"]},
    "regle-coussin": {"calcul": "Orange sans fonds d'urgence : une dépense imprévue pourrait forcer une vente au "
                      "mauvais moment.", "references": ["acvm-31-103cp"]},
    "regle-diversification": {"calcul": "Orange si la corrélation avec un placement détenu atteint 0,8.",
                              "references": ["markowitz-1952"]},
    "regle-donnees": {"calcul": "Gris si une information essentielle manque ou si un contrôle de données échoue : on ne "
                      "conclut pas sans elle.", "references": ["acvm-ocri-31-368", "dossier-adam"]},
    # ---- Profil, verdict et explication ----
    "jauges": {"calcul": "Deux jauges séparées, tolérance (ce que tu veux risquer) et capacité (ce que ta situation "
               "permet) ; on retient la plus basse.", "references": ["acvm-31-103cp", "ocri-gn-3400", "acvm-ocri-31-368"]},
    "questions": {"calcul": "Score de tolérance = moyenne des 3 réponses (0, 33, 67 ou 100).",
                  "references": ["grable-lytton-1999", "esma-2022"],
                  "hypothese": "Points par réponse choisis par l'équipe."},
    "verdict": {"calcul": "Le plus grave des niveaux des règles décide : rouge → incohérent, orange → ajustement, gris → "
                "impossible de conclure, sinon cohérent. Aucun modèle n'intervient.",
                "references": ["acvm-ocri-31-368", "turpin-2023", "kim-2025"]},
    "ajustement": {"calcul": "Montant le plus proche de la demande qui améliore le verdict d'au moins un état, "
                   "recherche exhaustive au pas de 100 CAD dans les deux sens, entre 100 CAD et l'épargne totale. "
                   "À distance égale, baisse examinée d'abord. Si aucun montant ne convient, premier allongement "
                   "d'horizon de 1 à 5 ans qui améliore l'état. Constat de simulation, pas de conseil.",
                   "references": ["wachter-2018", "miller-2019", "fusion-k5"]},
    "bascule": {"calcul": "Verdict du Gardien recalculé pour 8 montants × 20 horizons, sans modèle.",
                "references": ["wachter-2018"]},
}

# Agents et étapes de l'orchestrateur : pourquoi chacun est conçu ainsi.
AGENTS: dict[str, dict] = {
    "Profileur": {"role": "Le modèle léger lit la phrase ; le code valide chaque champ ; la personne corrige à l'étape 2.",
                  "references": ["clamber-2024", "ross-lo-2026", "acvm-31-103cp"]},
    "Contrôle données": {"role": "7 contrôles avant tout calcul ; un échec rend le verdict gris.",
                         "references": ["yfinance-reparation", "dossier-adam"]},
    "Analyste": {"role": "Calcule en code et écrit chaque fait F-n avec sa source et sa méthode.",
                 "references": ["gao-pal-2023", "turpin-2023"]},
    "Sceptique": {"role": "Ne peut demander que des vérifications du catalogue, exécutées par le code.",
                  "references": ["gou-critic-2024", "huang-2024", "choi-2025"]},
    "Gardien": {"role": "Règles écrites en code, ordre fixe, arbitre unique du verdict.",
                "references": ["anthropic-2024", "kim-2025", "acvm-ocri-31-368"]},
    "Rédacteur": {"role": "Le modèle rédige ; le code refuse tout nombre absent du dossier, toute formule de conseil, "
                  "toute contradiction du verdict, et corrige les étiquettes.",
                  "references": ["turpin-2023", "huang-2024", "miller-2019", "bansal-2021"]},
}


def references_de(cle: str) -> list[str]:
    """Identifiants de toutes les sources d'un élément : ses données, puis ses références."""
    j = JUSTIFICATIONS.get(cle, {})
    return list(dict.fromkeys(j.get("donnees", []) + j.get("references", [])))


def references_agent(agent: str) -> list[str]:
    return list(AGENTS.get(agent, {}).get("references", []))


def registre() -> dict:
    """Tout le registre, pour l'API (/api/sources) et la documentation."""
    return {"references": REFERENCES, "justifications": JUSTIFICATIONS, "agents": AGENTS}
