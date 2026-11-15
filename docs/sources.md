# Sources, méthodes et hypothèses

> Fichier généré par `backend/generer_doc_sources.py` à partir de `backend/alphaforge/sources.py`. Ne pas modifier à la main : modifier le registre, puis relancer le script.

Chaque élément montré à la personne répond à trois questions : **quelle donnée** (fichier, colonne), **quelle règle de calcul** (appliquée par le code) et **sur quelle base** (réglementation, recherche, ou choix de l'équipe dit comme tel). Le niveau d'examen de chaque source vient du dossier de recherche de l'équipe (14 nov. 2026) : une référence non relue n'est jamais présentée comme vérifiée.

## Faits calculés par l'Analyste

| Élément | Données | Règle de calcul | Références | Hypothèse de l'équipe |
|---|---|---|---|---|
| `chute` | Organisateurs du datathon (2026), Banque du Canada (2026) | Pire chute = min sur t de (P_t / max_{s≤t} P_s − 1), P en $ CA (adj_close × taux USD/CAD du jour ou dernier taux publié). | A. Chekhlov (2005), Mainteneurs de yfinance (2026) | — |
| `recuperation` | Organisateurs du datathon (2026), Banque du Canada (2026) | Années = (premier jour où P retrouve le sommet précédant le creux − date du creux) / 365,25. Si le sommet n'est pas retrouvé : années écoulées depuis le creux (borne minimale). | A. Chekhlov (2005) | — |
| `volatilite` | Organisateurs du datathon (2026), Banque du Canada (2026) | Écart-type des rendements log quotidiens × √252 (actions, FNB) ou × √365 (cryptoactifs, cotés 7 j/7). Cotations par an mesurées dans le jeu : 250,8 et 365,2. | H. Markowitz (1952), Équipe AlphaForge (Adam) (2026) | — |
| `rendement` | Organisateurs du datathon (2026), Banque du Canada (2026) | TCAC = (P_fin / P_début)^(1 / années) − 1. Erreur type de la moyenne ≈ volatilité / √années. | V. DeMiguel (2009), A. M. van der Bles (2020) | — |
| `pire12` | Organisateurs du datathon (2026), Banque du Canada (2026) | Pire rendement sur 52 semaines glissantes, cours du vendredi. Mesure hebdomadaire : peut sous-estimer la pire baisse sur 12 mois de cotations quotidiennes. | A. Chekhlov (2005) | — |
| `perte` | Organisateurs du datathon (2026), Banque du Canada (2026) | Perte de scénario = montant placé × pire chute observée. Scénario fictif : la prochaine baisse peut être plus forte ou plus faible. | S. Das (2010) | — |
| `correlation` | Organisateurs du datathon (2026), Banque du Canada (2026) | Corrélation de Pearson des rendements hebdomadaires (cours du vendredi), pour aligner les calendriers TSX, américains et crypto (7 j/7). | H. Markowitz (1952), Équipe AlphaForge (Adam) (2026) | — |
| `secteur` | Organisateurs du datathon (2026) | Lu tel quel dans assets_universe.csv. | Autorité européenne des marchés financiers (ESMA) (2022), F. Berg (2022) | — |
| `reference` | Organisateurs du datathon (2026) | Même calcul de pire chute que pour la demande, sur XIU.TO (indice canadien large), pour distinguer le risque du placement de celui du marché. | A. Chekhlov (2005) | — |
| `devise_usd` | Organisateurs du datathon (2026) | Même calcul de pire chute, sur adj_close en USD, sans conversion, pour mesurer l'effet du change. | Banque du Canada (2026) | — |
| `alternative` | Organisateurs du datathon (2026), Banque du Canada (2026), Organisateurs du datathon (2026) | Premier placement large, hors des secteurs exclus, que le Gardien juge acceptable au même montant. | Autorité européenne des marchés financiers (ESMA) (2022), F. Berg (2022) | — |

## Seuils et barèmes de l'équipe (faits HYPOTHESE)

| Élément | Données | Règle de calcul | Références | Hypothèse de l'équipe |
|---|---|---|---|---|
| `h_perte` | — | Perte supportable = 5 + 0,35 × score retenu (score de 0 à 100), soit de 5 % à 40 % de l'épargne. Score retenu = le plus bas entre tolérance et capacité. | Organisme canadien de réglementation des investissements (OCRI) (2021), Autorités canadiennes en valeurs mobilières (ACVM) (2021), Brayman (2015) | Barème linéaire choisi par l'équipe, non validé empiriquement ; publié pour être discuté. |
| `h_capacite` | — | Capacité = 50 points, puis + ou − selon horizon, revenu stable, fonds d'urgence, dettes et retrait prévu (barème détaillé à l'étape 2). | Autorités canadiennes en valeurs mobilières (ACVM) (2021), Brayman (2015) | Barème de points choisi par l'équipe à partir des éléments de connaissance du client. |
| `h_concentration` | — | Part maximale de l'épargne dans un actif très volatil : 5 % (score < 35), 10 % (35 à 64), 20 % (65 et plus). | H. Markowitz (1952), ACVM et OCRI (2025) | Trois paliers choisis par l'équipe. Limite connue : l'avis 31-368 critique les catégories « faible, moyen, élevé » non justifiées ; une fonction continue du score est à l'étude. |
| `h_volatil` | — | Un actif est « très volatil » au-delà de 30 %/an (règle de concentration) et « volatil » au-delà de 25 %/an (règle de retrait). | H. Markowitz (1952) | Seuils choisis par l'équipe ; à titre de repère, l'indice canadien large (XIU.TO) a une volatilité de 13,1 %/an sur la période. |
| `h_correlation` | — | On parle de fausse diversification à partir d'une corrélation de 0,8 avec un placement déjà détenu. | H. Markowitz (1952) | Seuil choisi par l'équipe. |

## Règles du Gardien

| Élément | Données | Règle de calcul | Références | Hypothèse de l'équipe |
|---|---|---|---|---|
| `regle-capacite` | — | Impact = (montant / épargne) × |pire chute|. Rouge au-delà de la capacité de perte, orange au-delà de la tolérance, sinon respectée. | Organisme canadien de réglementation des investissements (OCRI) (2021), Autorités canadiennes en valeurs mobilières (ACVM) (2021), A. Chekhlov (2005) | — |
| `regle-preserver` | — | Rouge si épargne − montant < somme à préserver. | A. B. Chhabra (2005), S. Das (2010) | — |
| `regle-exclusion` | — | Rouge si le secteur de l'actif fait partie des exclusions déclarées. | Autorité européenne des marchés financiers (ESMA) (2022), F. Berg (2022) | — |
| `regle-retrait` | — | Rouge si l'actif est volatil (> 25 %/an) et que le retrait prévu arrive avant la récupération observée. | Autorités canadiennes en valeurs mobilières (ACVM) (2021) | — |
| `regle-horizon` | — | Orange si l'horizon est plus court que le temps de récupération observé après la pire chute. | Autorités canadiennes en valeurs mobilières (ACVM) (2021), A. Chekhlov (2005) | — |
| `regle-concentration` | — | Orange si la part de l'épargne dépasse le seuil de concentration du profil, pour un actif très volatil (> 30 %/an). | H. Markowitz (1952), ACVM et OCRI (2025) | — |
| `regle-coussin` | — | Orange sans fonds d'urgence : une dépense imprévue pourrait forcer une vente au mauvais moment. | Autorités canadiennes en valeurs mobilières (ACVM) (2021) | — |
| `regle-diversification` | — | Orange si la corrélation avec un placement détenu atteint 0,8. | H. Markowitz (1952) | — |
| `regle-donnees` | — | Gris si une information essentielle manque ou si un contrôle de données échoue : on ne conclut pas sans elle. | ACVM et OCRI (2025), Équipe AlphaForge (Adam) (2026) | — |

## Profil, verdict et explication

| Élément | Données | Règle de calcul | Références | Hypothèse de l'équipe |
|---|---|---|---|---|
| `jauges` | — | Deux jauges séparées, tolérance (ce que tu veux risquer) et capacité (ce que ta situation permet) ; on retient la plus basse. | Autorités canadiennes en valeurs mobilières (ACVM) (2021), Organisme canadien de réglementation des investissements (OCRI) (2021), ACVM et OCRI (2025) | — |
| `questions` | — | Score de tolérance = moyenne des 3 réponses (0, 33, 67 ou 100). | J. Grable (1999), Autorité européenne des marchés financiers (ESMA) (2022) | Points par réponse choisis par l'équipe. |
| `verdict` | — | Le plus grave des niveaux des règles décide : rouge → incohérent, orange → ajustement, gris → impossible de conclure, sinon cohérent. Aucun modèle n'intervient. | ACVM et OCRI (2025), M. Turpin (2023), Kim (2025) | — |
| `ajustement` | — | Plus petit montant (au pas de 100 $), puis plus petit allongement d'horizon, qui améliore le verdict d'au moins un état. | S. Wachter (2018), T. Miller (2019) | — |
| `bascule` | — | Verdict du Gardien recalculé pour 8 montants × 20 horizons, sans modèle. | S. Wachter (2018) | — |

## Agents : pourquoi chacun est conçu ainsi

| Agent | Conception | Références |
|---|---|---|
| Profileur | Le modèle léger lit la phrase ; le code valide chaque champ ; la personne corrige à l'étape 2. | Zhang et al. (2024), Ross (2026), Autorités canadiennes en valeurs mobilières (ACVM) (2021) |
| Contrôle données | 7 contrôles avant tout calcul ; un échec rend le verdict gris. | Mainteneurs de yfinance (2026), Équipe AlphaForge (Adam) (2026) |
| Analyste | Calcule en code et écrit chaque fait F-n avec sa source et sa méthode. | L. Gao (2023), M. Turpin (2023) |
| Sceptique | Ne peut demander que des vérifications du catalogue, exécutées par le code. | Gou et al. (2024), Huang et al. (2024), Choi (2025) |
| Gardien | Règles écrites en code, ordre fixe, arbitre unique du verdict. | Erik S. (2024), Kim (2025), ACVM et OCRI (2025) |
| Rédacteur | Le modèle rédige ; le code refuse tout nombre absent du dossier, toute formule de conseil, toute contradiction du verdict, et corrige les étiquettes. | M. Turpin (2023), Huang et al. (2024), T. Miller (2019), G. Bansal et al. (2021) |

## Registre des références

### Données

| Id | Référence | Ce qu'elle justifie | Niveau d'examen |
|---|---|---|---|
| `donnees-prix` | Organisateurs du datathon ; Yahoo Finance via yfinance (2026). *prices_daily.csv, colonne adj_close (jeu de départ AlphaForge)*. data/raw/alphaforge_starter/, extrait le 2026-11-13, fenêtre 2021-11-12 → 2026-11-12. [lien](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html) | Prix ajustés des dividendes et des fractionnements, pour 31 actifs. Conditions Yahoo : usage personnel, pas de collecte automatisée sans permission. | fichier lu et recalculé indépendamment (audit du 15 nov.) |
| `donnees-change` | Banque du Canada (2026). *Taux de change USD/CAD quotidien (API Valet), fx_usdcad_daily.csv, colonne usdcad*. jeu de départ AlphaForge. [lien](https://www.bankofcanada.ca/rates/exchange/background-information/) | Taux indicatif : moyenne de cotations relevées entre 8 h et 16 h (heure de l'Est), publiée les jours ouvrables de la Banque. Ce n'est pas un cours de clôture. | méthodologie : texte analysé (dossier de recherche) ; fichier recalculé (audit) |
| `donnees-univers` | Organisateurs du datathon (2026). *assets_universe.csv, colonnes sector, currency, asset_class*. jeu de départ AlphaForge. | Secteur, devise et classe de chaque actif. Étiquettes simplifiées : ce n'est ni une classification officielle ni une donnée ESG. | fichier lu |

### Réglementation

| Id | Référence | Ce qu'elle justifie | Niveau d'examen |
|---|---|---|---|
| `acvm-31-103cp` | Autorités canadiennes en valeurs mobilières (ACVM) (2021). *Instruction complémentaire 31-103CP, articles 13.2 et 13.3 (connaissance du client, convenance)*. version consolidée au 2021-03-01. [lien](https://fcnb.ca/sites/default/files/2022-01/31-103CP-CONS-2021-03-01-E.pdf) | Six éléments de connaissance du client (situation financière, besoins de liquidité, horizon dont la faisabilité doit être évaluée…). Tolérance au risque et capacité à subir des pertes sont deux considérations distinctes. | texte analysé, extraction automatique (dossier de recherche) |
| `ocri-gn-3400` | Organisme canadien de réglementation des investissements (OCRI) (2021). *GN-3400-21-004, Know-your-client and suitability determination for retail clients*. en vigueur le 2021-12-31. [lien](https://www.ciro.ca/news-room/publications/know-your-client-and-suitability-determination-retail-clients) | Le profil de risque doit refléter le plus bas des deux : tolérance ou capacité. | texte analysé, extraction automatique (dossier de recherche) |
| `acvm-ocri-31-368` | ACVM et OCRI (2025). *Avis conjoint du personnel 31-368, Réformes axées sur le client*. 2025-12-10, examen de 105 entreprises. [lien](https://www.asc.ca/-/media/ASC-Documents-part-1/Regulatory-Instruments/2025/12/6255537-CSA-CIRO-Notice-31-368-Client-Focused-Reforms.pdf) | Reproche de fusionner tolérance et capacité, d'utiliser des catégories « faible, moyen, élevé » sans justification, et précise que noter que le client a dirigé l'opération est insuffisant. | texte analysé partiel, extraction automatique (dossier de recherche) |
| `osc-iap-2015` | Brayman, Finke, Bessner, Grable, Griffin, Clement (OSC IAP) (2015). *Current Practices for Risk Profiling in Canada*. rapport commandé par la Commission des valeurs mobilières de l'Ontario. [lien](https://www.osc.ca/sites/default/files/2021-02/iap_20151112_risk-profiling-report.pdf) | 75 % des questionnaires analysés avaient des pondérations arbitraires : publier son barème et le dire hypothétique est le minimum honnête. | texte analysé partiel, extraction automatique (dossier de recherche) |
| `esma-2022` | Autorité européenne des marchés financiers (ESMA) (2022). *Orientations MiFID II sur certains aspects de l'adéquation (ESMA35-43-3172)*. 2022-09-23. [lien](https://prod.finanssivalvonta.fi/globalassets/en/publications/supervision-releases/2023/esma35-43-3172_guidelines_on_certain_aspects_of_the_mifid_ii_suitability_requirements.pdf) | Recueillir les préférences de durabilité de la personne (exclusions déclarées) plutôt que les déduire ; déconseille l'auto-évaluation seule de la tolérance au profit de la perte acceptée. | texte analysé (dossier de recherche) |

### Recherche publiée

| Id | Référence | Ce qu'elle justifie | Niveau d'examen |
|---|---|---|---|
| `markowitz-1952` | H. Markowitz (1952). *Portfolio Selection*. Journal of Finance 7(1), p. 77-91. [lien](https://doi.org/10.2307/2975974) | La diversification réduit le risque à condition que les placements ne bougent pas ensemble : d'où la corrélation et la limite de concentration. | référence classique, non relue pendant le datathon |
| `demiguel-2009` | V. DeMiguel, L. Garlappi, R. Uppal (2009). *Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy?*. Review of Financial Studies 22(5). [lien](https://ideas.repec.org/a/oup/rfinst/v22y2009i5p1915-1953.html) | Les rendements moyens historiques ne sont pas estimables avec précision sur quelques années : on ne s'en sert jamais pour décider, et on affiche leur erreur type. | résumé lu (dossier de recherche) |
| `chekhlov-2005` | A. Chekhlov, S. Uryasev, M. Zabarankin (2005). *Drawdown Measure in Portfolio Optimization*. International Journal of Theoretical and Applied Finance 8(1). | Définition de la baisse maximale depuis un sommet (drawdown), mesure de risque compréhensible. | référence bibliographique, non relue (dossier de recherche : [NV]) |
| `chhabra-2005` | A. B. Chhabra (2005). *Beyond Markowitz: A Comprehensive Wealth Allocation Framework for Individual Investors*. Journal of Wealth Management 7(4). | Séparer une part protégée de l'épargne (« somme à préserver ») de la part exposée au marché. | référence citée dans le plan de l'équipe, non relue pendant le datathon |
| `das-2010` | S. Das, H. Markowitz, J. Scheid, M. Statman (2010). *Portfolio Optimization with Mental Accounts*. JFQA 45(2). [lien](https://ideas.repec.org/a/cup/jfinqa/v45y2010i02p311-334_00.html) | Raisonner par objectif et par seuil de perte (compte mental) plutôt que par un coefficient abstrait. | condensé CFA lu (dossier de recherche) |
| `grable-lytton-1999` | J. Grable, R. H. Lytton (1999). *Financial risk tolerance revisited: the development of a risk assessment instrument*. Financial Services Review 8(3), p. 163-181. [lien](https://openjournals.libs.uga.edu/fsr/article/view/3240) | Les 3 questions sont adaptées de cette échelle (fidélité interne α = 0,77 sur 160 279 répondants selon la rétrospective). Les points par réponse sont un barème de l'équipe. | lien vers la rétrospective de 15 ans (Kuzniak et al., 2015), résumé lu ; article de 1999 non relu |
| `berg-2022` | F. Berg, J. F. Kölbel, R. Rigobon (2022). *Aggregate Confusion: The Divergence of ESG Ratings*. Review of Finance 26(6). [lien](https://academic.oup.com/rof/article/26/6/1315/6590670) | Les notes ESG de six agences ne corrèlent qu'entre 0,38 et 0,71 : on n'invente pas de note ESG, on applique seulement les exclusions déclarées par la personne. | page de synthèse lue (dossier de recherche) |
| `wachter-2018` | S. Wachter, B. Mittelstadt, C. Russell (2018). *Counterfactual Explanations without Opening the Black Box*. Harvard JOLT. [lien](https://arxiv.org/abs/1711.00399) | Expliquer une décision par le plus petit changement qui la ferait basculer : la version ajustée et les curseurs de bascule. | résumé lu (dossier de recherche) |
| `miller-2019` | T. Miller (2019). *Explanation in Artificial Intelligence: Insights from the Social Sciences*. Artificial Intelligence 267. [lien](https://arxiv.org/abs/1706.07269) | Une bonne explication est contrastive (« ceci plutôt que cela ») et sélective : on commence par ce qui pèse le plus dans le verdict. | texte analysé, première moitié (dossier de recherche) |
| `turpin-2023` | M. Turpin, J. Michael, E. Perez, S. Bowman (2023). *Language Models Don't Always Say What They Think*. NeurIPS 2023. [lien](https://arxiv.org/abs/2305.04388) | Le raisonnement affiché par un modèle peut déformer la vraie raison de sa réponse : il ne peut pas servir d'explication, d'où des chiffres et un verdict produits par le code. | résumé lu (dossier de recherche) |
| `gao-pal-2023` | L. Gao, A. Madaan, S. Zhou et al. (2023). *PAL: Program-aided Language Models*. arXiv 2211.10435 ; ICML 2023. [lien](https://arxiv.org/abs/2211.10435) | Déléguer le calcul au code plutôt qu'au modèle réduit les erreurs numériques, y compris sur des questions financières (FinQA, TAT-QA). | résumé lu (dossier de recherche) |
| `gou-critic-2024` | Gou et al. (2024). *CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing*. ICLR 2024. [lien](https://arxiv.org/abs/2305.11738) | Une critique aide quand elle s'appuie sur un outil qui vérifie : le Sceptique ne peut demander que des vérifications exécutées par le code. | résumé lu (dossier de recherche) |
| `huang-2024` | Huang et al. (2024). *Large Language Models Cannot Self-Correct Reasoning Yet*. ICLR 2024. [lien](https://arxiv.org/abs/2310.01798) | Sans retour extérieur, un modèle se corrige mal lui-même : le texte du Rédacteur est contrôlé par le code, pas par lui-même. | résumé lu (dossier de recherche) |
| `choi-2025` | Choi, Zhu, Li (2025). *Debate or Vote: Which Yields Better Decisions in Multi-Agent LLMs?*. NeurIPS 2025. [lien](https://arxiv.org/abs/2508.17536) | Le débat libre entre agents n'améliore pas seul l'exactitude : on a préféré une contradiction outillée et un arbitre en code (le Gardien). | résumé lu (dossier de recherche) |
| `anthropic-2024` | Erik S., Barry Zhang (Anthropic) (2024). *Building effective agents*. billet d'ingénierie, 2024-12-19. [lien](https://www.anthropic.com/engineering/building-effective-agents) | Préférer un flux simple et explicite, aux étapes fixes, à un orchestrateur piloté par un modèle. | page lue, extraction automatique (dossier de recherche) ; témoignage de praticiens |
| `kim-2025` | Kim, Gu, Park et al. (2025). *Towards a Science of Scaling Agent Systems*. arXiv 2512.08296. [lien](https://arxiv.org/abs/2512.08296) | Plus d'agents n'est pas toujours mieux (de +80,8 % à -70,0 % selon la tâche) ; les erreurs se propagent sans vérification centralisée : d'où un Gardien unique qui décide. | résumé lu (dossier de recherche) |
| `clamber-2024` | Zhang et al. (2024). *CLAMBER: A Benchmark of Identifying and Clarifying Ambiguous Information Needs*. ACL 2024. [lien](https://arxiv.org/html/2405.12063v2) | Un modèle seul ne repère que 38 % des contradictions : le Profileur lit la phrase, mais le code valide chaque champ et la personne corrige à l'étape 2. | texte analysé, extraction automatique (dossier de recherche) |
| `ross-lo-2026` | Ross, Lo (2026). *One Size Fits None: Heuristic Collapse in LLM Investment Advice*. arXiv 2604.23837. [lien](https://arxiv.org/abs/2604.23837) | Les conseils de modèles GPT dépendent à 57-88 % de la seule tolérance déclarée : les jauges et la capacité sont calculées par le code, jamais par le modèle. | texte analysé, extraction automatique (dossier de recherche) |
| `bansal-2021` | G. Bansal et al. (2021). *Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance*. CHI 2021. [lien](https://arxiv.org/abs/2006.14779) | Une explication augmente l'acceptation d'une recommandation, juste ou fausse : on montre les limites et l'incertitude, pas seulement des arguments. | résumé lu (dossier de recherche) |
| `van-der-bles-2020` | A. M. van der Bles, S. van der Linden, A. Freeman, D. Spiegelhalter (2020). *The effects of communicating uncertainty on public trust in facts and numbers*. PNAS 117(14). [lien](https://core.ac.uk/download/305110478.pdf) | Une fourchette chiffrée réduit peu la confiance (d = -0,15), bien moins qu'une incertitude vague : on affiche l'erreur type plutôt qu'un « environ ». | texte analysé (dossier de recherche) |

### Documentation de méthode

| Id | Référence | Ce qu'elle justifie | Niveau d'examen |
|---|---|---|---|
| `yfinance-reparation` | Mainteneurs de yfinance (2026). *Price repair (documentation)*. dépôt ranaroussi/yfinance. [lien](https://github.com/ranaroussi/yfinance/blob/main/doc/source/advanced/price_repair.rst) | Les mainteneurs documentent des ajustements manquants ou fictifs dans les données Yahoo et écrivent que seules les données américaines semblent parfaites : une limite pour les titres du TSX. | texte analysé (dossier de recherche) |

### Document de l'équipe

| Id | Référence | Ce qu'elle justifie | Niveau d'examen |
|---|---|---|---|
| `dossier-adam` | Équipe AlphaForge (Adam) (2026). *Réutiliser des briques éprouvées, prouver leur assemblage (dossier de recherche documentaire)*. document interne du 2026-11-14. | Synthèse de sept carnets de recherche : choix des méthodes, pièges des données, conception des agents. | document de l'équipe ; chaque affirmation y porte son propre niveau de preuve |
