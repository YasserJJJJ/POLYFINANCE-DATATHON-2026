Prompt 2 — Rechercher les vrais processus professionnels et leurs fondements
Le cadre précédent est notre base. Nous allons maintenant déterminer comment rendre chaque rôle intellectuellement solide.
Recherche attendue
Étudie les processus pertinents d’organisations financières, les cadres professionnels, les publications scientifiques, les cours et les implémentations ouvertes. Recherche des méthodes réellement applicables à nos demandes fictives et à nos données.
Ne pars pas d’un intitulé prestigieux pour inventer les tâches correspondantes. Établis les fonctions professionnelles à partir des sources, puis explique leur adaptation au datathon.
Pour chacun des quatre agents, recherche :
* ses responsabilités et les questions auxquelles il doit répondre ;
* ses entrées, documents de travail et sorties ;
* les méthodes disponibles et leurs hypothèses ;
* les erreurs fréquentes et les contradictions à détecter ;
* les critères permettant d’évaluer son travail ;
* les circonstances où il doit demander une clarification, approfondir ou renvoyer le dossier à un autre agent.
Exploitation des ressources
Inventorie les connecteurs, outils de recherche, bases documentaires et ressources AWS déjà accessibles. Vérifie leur fonctionnement. Exploite les ressources fournies dans les documents 00, 00B et 01, ainsi que le notebook, après examen critique de ses exemples.
Toutes les inférences doivent suivre la route AWS convenue, y compris celles des sous-agents et des outils auxiliaires. Un accès documentaire ou un plugin installé ne prouve pas que son modèle utilise cette route.
Standard documentaire
Pour chaque source déterminante, conserve :
* référence vérifiable et version ;
* niveau de lecture réel ;
* résultat ou méthode utilisé ;
* hypothèses et limites ;
* élément du projet qu’elle influence ;
* éventuelle contradiction avec une autre source.
Sépare résultat théorique, résultat empirique, cadre professionnel, documentation technique et affirmation commerciale.
Recherche largement, puis approfondis les sources décisives. Le nombre de références doit résulter de la couverture du problème. Une bibliographie volumineuse ne constitue pas une revue de littérature.
Livrables :
1. Une cartographie des fonctions professionnelles pertinentes.
2. Une revue structurée par questions et décisions.
3. Une fiche méthodologique pour chacun des quatre agents.
4. Les controverses et inconnues qui restent ouvertes.
5. Une recommandation argumentée pour notre fonctionnement cible.
Pas de nouvelle interface pendant cette étape. Tu peux produire de petites expériences discriminantes pour vérifier une méthode.Intègre également le document ci-dessous à ta revue : examine toutes les références qu’il contient, approfondis celles qui sont pertinentes et inspire-toi fortement des méthodes et implémentations étayées. Tiens un journal des implémentations candidates à reproduire et à tester, précisant pour chacune le problème traité, la source, les hypothèses, les adaptations nécessaires et l’expérience permettant d’en évaluer l’intérêt. Utilise ce document pour enrichir, confronter et prolonger tes découvertes avant, pendant et après la recherche ; poursuis l’exploration au-delà de ses références, sans considérer ses conclusions comme acquises ni modifier les objectifs du prompt 2. Voici le document :# Réutiliser des briques éprouvées, prouver leur assemblage

## 1. Synthèse accessible

*Dossier de recherche documentaire préparé pour l'équipe AlphaForge AI à partir de sept carnets de recherche. Toutes les sources ont été consultées le 2026-11-14. Rien n'a été exécuté, déployé ni payé.*

**Aucun travail examiné ne résout le problème AlphaForge de bout en bout, mais presque chaque morceau existe déjà, souvent mieux étayé que les « agents financiers » les plus visibles.** Aucun système ouvert trouvé n'est à la fois canadien, multi-actifs, sensible au profil de l'investisseur et explicable avec des calculs déterministes. Les briques utiles sont dispersées dans quatre domaines qui se citent peu : la finance de portefeuille sous erreur d'estimation, la réglementation canadienne de la convenance, les aides à la décision médicales et l'ingénierie des agents à base de LLM. La recherche déplace donc la question : l'originalité défendable n'est ni un nouvel algorithme ni une équipe d'agents plus nombreuse, mais une combinaison vérifiable dans laquelle le code calcule, le LLM traduit, interroge et raconte à partir de valeurs calculées, et où chaque affirmation montrée au jury remonte à une donnée, une règle ou un calcul. Trois résultats bousculent des intuitions courantes : avec cinq ans de données, les rendements moyens ne sont pas estimables avec une précision utile ; les gains attribués au débat entre agents viennent surtout d'un simple vote majoritaire ; une explication augmente l'acceptation d'une recommandation, qu'elle soit juste ou fausse. La combinaison la mieux étayée parmi celles examinées associe un noyau de calcul déterministe limité à une bibliothèque fermée de formulations, un profil structuré selon les règles canadiennes (ACVM et OCRI) avec détection déterministe des contradictions, une restitution inspirée des aides à la décision médicales et une contribution AWS centrée sur la traçabilité. Ce dossier ne tranche pas l'architecture finale : il décrit quatre directions crédibles et l'expérience la plus discriminante pour choisir. C'est une recherche documentaire avec des limites réelles (API GitHub bloquée pour plusieurs chercheurs, pages inaccessibles, extraction automatique de certains textes, aucun code exécuté) ; la section 10 liste les vérifications à faire en priorité.

### 1.1 Comment lire ce dossier

Quatre niveaux de preuve sont distingués partout par un marqueur visible, plus un cinquième pour ce qui n'a pas été vérifié.

| Marqueur | Niveau | Exemple |
|---|---|---|
| **[A]** | Ce que les auteurs, l'éditeur ou le fournisseur affirment. **[A][V]** signifie que la phrase a été retrouvée dans la source primaire, sans que le résultat lui-même ait été vérifié. | Un taux de réussite annoncé dans un article |
| **[I]** | Ce qu'une évaluation indépendante établit (autres auteurs, revue systématique, réplication, critique tierce). | Une réplication qui ne retrouve pas le résultat |
| **[V]** | Ce qui a été vérifié pendant cette recherche, avec la profondeur entre accolades. | Une licence lue dans le fichier LICENSE |
| **[Inf]** | Ce qui est proposé par inférence, par les chercheurs ou dans ce dossier. Ce n'est pas un fait. | Une architecture suggérée |
| **[NV]** | Non vérifié : connaissance de fond, référence bibliographique seule, souvenir non revérifié. À confirmer avant toute citation. | Une formule donnée de mémoire |

Profondeurs d'examen réelles, reprises des carnets : **{repéré}** titre, extrait ou notice seulement ; **{résumé lu}** ; **{page lue}** page web ou documentation lue ; **{texte analysé}** texte intégral ou partiel lu ; **{code inspecté}** dépôt cloné et fichiers lus, sans exécution ; **{licence lue}** fichier LICENSE ou métadonnées PyPI ou npm lus. La mention **(extraction auto)** signale un texte obtenu par un outil d'extraction ou de résumé automatique : les chiffres et citations sont proches du texte original mais n'ont pas été vérifiés caractère par caractère, et doivent être relus dans le PDF avant de figurer sur une diapositive.

Deux conventions complètent ce code. Les licences du **code**, des **modèles** et des **données** sont toujours séparées : une licence Apache-2.0 sur un dépôt ne couvre ni les données qu'il télécharge ni les modèles qu'il appelle. Les dates de version viennent de PyPI, de npm ou de clones git, parce que l'API GitHub renvoyait une erreur 403 à plusieurs chercheurs.

### 1.2 Lexique minimal

| Terme | Sens dans ce dossier |
|---|---|
| Rendement total | Variation du prix plus dividendes réinvestis, corrigée des fractionnements d'actions. |
| Volatilité | Écart-type annualisé des rendements : l'ampleur typique des fluctuations. |
| Covariance, corrélation | Façon dont deux actifs bougent ensemble. La matrice de covariance est l'ingrédient principal de la diversification. |
| Erreur d'estimation | Écart entre une grandeur estimée sur l'historique et sa vraie valeur inconnue. |
| 1/N | Portefeuille équipondéré, référence naïve. |
| Variance minimale (GMV) | Portefeuille qui minimise la volatilité sous contraintes, sans utiliser de rendement moyen. |
| Contraction (Ledoit-Wolf) | Mélange de la covariance empirique avec une cible simple pour réduire le bruit d'estimation. |
| Parité de risque (ERC), HRP | Allocations où chaque actif, ou chaque groupe d'actifs, contribue au risque de façon équilibrée. |
| Drawdown, CVaR | Perte depuis le dernier sommet ; perte moyenne dans les x % pires cas. |
| Ratio de Sharpe | Rendement excédentaire divisé par la volatilité. |
| Backtest | Simulation d'une stratégie sur l'historique. |
| Biais d'anticipation (look-ahead) | Utiliser une information indisponible à la date de la décision. Cela inclut un LLM qui « connaît » la suite des événements parce qu'elle figure dans ses données d'entraînement. |
| Biais du survivant | Univers d'actifs choisi aujourd'hui, donc composé d'actifs qui ont survécu. |
| Point-in-time, millésime | Valeur d'une série telle qu'elle était connue à une date donnée, avant révisions. |
| KYC, convenance | Obligations canadiennes de connaître le client et de vérifier qu'une recommandation lui convient. |
| ACVM (CSA), OCRI (CIRO) | Autorités canadiennes en valeurs mobilières ; Organisme canadien de réglementation des investissements. |
| IIS | Sous-ensemble minimal de contraintes contradictoires : il devient réalisable si l'on retire n'importe laquelle d'entre elles. |
| Profil d'inférence (Bedrock) | Identifiant qui fixe dans quelles régions AWS une requête au modèle peut être traitée. |

### 1.3 Ce que la recherche change dans notre compréhension du problème

**Le problème n'est pas d'abord un problème de prévision.** Avec environ 1 260 jours de bourse sur cinq ans, l'écart-type de la moyenne annualisée d'un actif vaut à peu près sa volatilité divisée par √5 : **environ 9 points de pourcentage par an pour une action à 20 % de volatilité, environ 36 points pour une cryptomonnaie à 80 %** [Inf, calcul des chercheurs]. Une moyenne historique de +15 % reste donc compatible avec un vrai rendement négatif. DeMiguel, Garlappi et Uppal estiment qu'il faudrait **environ 3 000 mois de données pour que l'optimisation moyenne-variance sur 25 actifs batte l'équipondération** [A][V] {résumé lu} ([DeMiguel et al. 2009](https://ideas.repec.org/a/oup/rfinst/v22y2009i5p1915-1953.html)), contre 60 mois ici. Le débat n'est pas clos : des optimisations qui n'utilisent pas de moyennes historiques (variance minimale, primes constantes) battent 1/N hors échantillon [I][V] {résumé lu} ([Kritzman et al. 2010](https://ideas.repec.org/a/taf/ufajxx/v66y2010i2p31-39.html)), et le résultat de DeMiguel tiendrait surtout à un protocole à forte rotation [I][V] {résumé lu} ([Kirby et Ostdiek 2012](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/its-all-in-the-timing-simple-active-portfolio-strategies-that-outperform-naive-diversification/05D18E04B226C6E9B8441482CC92F943)). Pour l'étape « appliquer des méthodes calculables et justifiées », la justification doit donc reposer sur la robustesse et le respect des contraintes du profil, non sur une performance passée. Les chercheurs ont calculé qu'en essayant 20 configurations sans aucun talent réel, le meilleur ratio de Sharpe annualisé attendu par pur hasard est d'environ **0,85** [Inf] : aucun backtest de cinq ans d'un portefeuille sans vente à découvert ne franchira ce seuil de façon convaincante. Le message honnête devient : « les méthodes sont statistiquement indiscernables sur le Sharpe, nous choisissons sur le contrôle du risque et l'adéquation au profil ».

**Les « agents financiers » les plus visibles traitent un problème voisin, et leurs résultats ne résistent pas aux vérifications indépendantes.** TradingAgents produit une note à cinq niveaux, une proposition d'ordre et un prix cible pour **un seul titre à une seule date** ; les quantités de décision sont écrites par le LLM, et son propre module de backtest déclare ne pas être un simulateur de portefeuille [V] {code inspecté} ([TradingAgents](https://github.com/TauricResearch/TradingAgents)). Son article rapporte des ratios de Sharpe de 5,6 à 8,2 sur trois titres et environ trois mois, sans coûts de transaction, avec une colonne de rendement annualisé incompatible avec sa propre formule [V] {texte analysé} ([arXiv 2412.20138](https://arxiv.org/html/2412.20138)). Sur deux décennies et plus de 100 titres, FINSABER constate que les avantages rapportés par les stratégies à base de LLM « se détériorent significativement » [I][V] {texte analysé} ([FINSABER](https://arxiv.org/html/2505.07078)). Profit Mirage observe une chute de tous les agents testés après la date de coupure des connaissances du modèle [I] {texte analysé partiel} ([Profit Mirage](https://arxiv.org/html/2510.07920)). StockBench, sur une fenêtre postérieure à l'entraînement, trouve que la plupart des agents ne battent pas un achat-conservation équipondéré [I] {texte analysé partiel} ([StockBench](https://arxiv.org/html/2510.02209)). Le biais d'anticipation existe même à l'intérieur des modèles pré-entraînés [I] {résumé lu} ([Sarkar et Vafa, ICML 2025](https://icml.cc/virtual/2025/48685)). Pour un jeu de données couvrant probablement 2021 à 2026 et un modèle actuel, tout backtest où le LLM choisit des titres est contaminé par construction [Inf] : aucune « performance du LLM » ne doit être revendiquée.

**Plus d'agents n'est pas automatiquement mieux.** L'étude contrôlée de Kim et al. (260 configurations) rapporte un effet du multi-agents allant de **+80,8 % sur un raisonnement financier décomposable à -70,0 % sur de la planification séquentielle**, avec des rendements décroissants quand l'agent seul est déjà fort et une propagation des erreurs en l'absence de vérification centralisée [A] {résumé lu} ([Kim et al. 2025](https://arxiv.org/abs/2512.08296)). Choi, Zhu et Li montrent que **le vote majoritaire explique l'essentiel des gains attribués au débat** et prouvent que le débat seul n'améliore pas l'exactitude attendue (il induit une martingale sur les croyances) [I] {résumé lu} ([Debate or Vote](https://arxiv.org/abs/2508.17536)). Sans retour externe, les LLM peinent à se corriger eux-mêmes [I] {résumé lu} ([Huang et al.](https://arxiv.org/abs/2310.01798)) ; la critique aide quand elle s'appuie sur un outil comme un interpréteur de code [A] {résumé lu} ([CRITIC](https://arxiv.org/abs/2305.11738)). Anthropic, qui défend un système multi-agents pour la recherche documentaire, rapporte lui-même une consommation d'**environ 15 fois les jetons d'une conversation** [A] {page lue, extraction auto} ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Hypothèse à réviser : un comité d'agents qui débattent n'est pas un gage d'intelligence agentique. La position par défaut la mieux soutenue est un flux déterministe avec un agent outillé, auquel on n'ajoute des rôles que si une ablation montre leur valeur.

**Le LLM seul est un mauvais profileur et un mauvais formulateur de problèmes d'optimisation.** Sur 1 000 profils synthétiques, les allocations proposées par des modèles GPT dépendent pour **57 à 88 % du seul niveau de tolérance au risque déclaré** (un « effondrement heuristique »), le revenu pesant très peu [A] {texte analysé, extraction auto} ([Ross et Lo 2026](https://arxiv.org/abs/2604.23837)). Sur le banc CLAMBER, ChatGPT ne repère que **38 % des contradictions** [A] {texte analysé, extraction auto} ([CLAMBER](https://arxiv.org/html/2405.12063v2)). Des conseillers LLM « peinent quand les besoins de l'utilisateur sont contradictoires », et un ton extraverti augmente la confiance malgré de moins bons conseils [A] {résumé lu} ([Takayanagi et al. 2025](https://arxiv.org/abs/2504.05862)). Environ **47 % des 2 048 portefeuilles générés par 32 LLM contenaient une erreur de réponse**, le plus souvent des poids ne sommant pas à 100 % [I] {texte analysé partiel, extraction auto} ([Fieberg et al. 2025](https://www.ifo.de/DocDL/cesifo1_wp11666.pdf)). Côté optimisation, une revue a trouvé au moins 8 à 54 % d'instances erronées dans les bancs d'essai de formulation par LLM, et, après nettoyage, une exactitude de la meilleure méthode comprise selon le banc entre environ 43 et 94 %, souvent entre 50 et 75 % [I][V] {texte analysé} ([Xiao et al. 2025](https://arxiv.org/html/2508.10047v1)). Le motif OptiGuide, où le LLM traduit une question « et si » en appel à un modèle d'optimisation fixe et testé, contourne ce problème [A] {résumé lu} ([OptiGuide](https://arxiv.org/abs/2307.03875)).

**Une explication peut nuire autant qu'aider.** Le raisonnement affiché par un modèle peut « systématiquement déformer la vraie raison » de sa réponse [A] {résumé lu} ([Turpin et al. 2023](https://arxiv.org/abs/2305.04388)) ; il ne peut donc pas tenir lieu d'explication. Dans une étude contrôlée, les explications ont **augmenté l'acceptation des recommandations de l'IA, qu'elles soient correctes ou non**, sans améliorer la performance de l'équipe humain-IA [A] {résumé lu} ([Bansal et al. 2021](https://arxiv.org/abs/2006.14779)). Seules des interfaces qui forcent la réflexion avant l'affichage réduisent cette sur-confiance, au prix d'une moins bonne appréciation par les utilisateurs [A] {résumé lu} ([Buçinca et al. 2021](https://arxiv.org/abs/2102.09692)). En finance, faire « vivre » des tirages simulés améliore la compréhension du profil risque-rendement mais pousse vers des choix plus risqués [A] {texte analysé} ([Bradbury et al. 2015](https://core.ac.uk/download/85223761.pdf) ; [Kaufmann et al. 2013](https://econpapers.repec.org/RePEc:inm:ormnsc:v:59:y:2013:i:2:p:323-340)), ce qui est un danger pour Robert. À l'inverse, les aides à la décision médicales augmentent de **75 % (RR 1,75) les choix informés et conformes aux valeurs** du patient, avec une certitude modérée [I][V] {résumé lu} ([Cochrane 2024](https://portal.findresearcher.sdu.dk/da/publications/decision-aids-for-people-facing-health-treatment-or-screening-dec/)). La bonne mesure de succès est la qualité de décision (connaissance plus concordance avec les valeurs), pas la qualité du texte : les formules de lisibilité corrèlent mal avec le jugement humain, et le meilleur juge LLM testé n'atteint que r = 0,56 [A] {résumé lu} ([Cachola et al. 2025](https://arxiv.org/abs/2508.19221)).

**Les données sont un sujet de fond, pas un simple prérequis.** Le jeu de départ annonce des séries macroéconomiques révisées : utilisées « telles que connues aujourd'hui », elles introduisent un biais d'anticipation que seuls des millésimes (ALFRED pour les séries américaines) ou un délai de publication documenté corrigent [Inf] ([conditions FRED/ALFRED](https://fred.stlouisfed.org/docs/api/terms_of_use.html)). Prolonger un prix les jours fériés propres à une bourse crée des rendements nuls artificiels qui sous-estiment volatilités et corrélations, et la cryptomonnaie cote sept jours sur sept [Inf]. Les mainteneurs de yfinance documentent eux-mêmes des ajustements manquants ou fictifs dans les données Yahoo et écrivent que « seules les données du marché américain semblent parfaites » [A][V] {texte analysé} ([yfinance, price repair](https://github.com/ranaroussi/yfinance/blob/main/doc/source/advanced/price_repair.rst)), un avertissement direct pour les titres du TSX. Le taux USD/CAD de la Banque du Canada est une moyenne indicative de cotations relevées entre 8 h et 16 h (heure de l'Est), pas un cours de clôture [A][V] {page lue} ([Banque du Canada](https://www.bankofcanada.ca/rates/exchange/background-information/)). Pour l'ESG, les notes de six agences ne corrèlent qu'entre **0,38 et 0,71** [A] {page de synthèse lue} ([Berg, Kölbel et Rigobon 2022](https://academic.oup.com/rof/article/26/6/1315/6590670)), l'historique d'un fournisseur majeur a été réécrit après coup [A] {résumé lu} ([Berg, Fabisik et Sautner](https://www.ecgi.global/publications/working-papers/is-history-repeating-itself-the-unpredictable-past-of-esg-ratings)) et les scores favorisent les grandes entreprises [A] {résumé lu} ([Drempetic et al. 2020](https://link.springer.com/content/pdf/10.1007/s10551-019-04164-1.pdf)). Le jeu de départ ne contient aucune preuve ESG : pour Mateo, l'état honnête par défaut est « inconnu », sauf source externe correctement licenciée.

**Le profil dispose déjà d'une structure défendable : celle des régulateurs canadiens.** L'Instruction complémentaire 31-103CP énumère six éléments de connaissance du client et fait de la tolérance au risque et de la capacité à subir des pertes deux considérations distinctes [V] {texte analysé, extraction auto} ([31-103CP](https://fcnb.ca/sites/default/files/2022-01/31-103CP-CONS-2021-03-01-E.pdf)). L'OCRI demande que le profil reflète **le plus bas des deux** [V] {texte analysé, extraction auto} ([OCRI GN-3400-21-004](https://www.ciro.ca/news-room/publications/know-your-client-and-suitability-determination-retail-clients)). L'avis conjoint 31-368 de décembre 2025, après examen de 105 entreprises, reproche notamment de fusionner tolérance et capacité, d'utiliser des cases « faible, moyen, élevé » sans justification et des fourchettes de revenus trop larges, et précise que « noter simplement que le client a dirigé l'opération est insuffisant » [V] {texte analysé partiel, extraction auto} ([ACVM/OCRI 31-368](https://www.asc.ca/-/media/ASC-Documents-part-1/Regulatory-Instruments/2025/12/6255537-CSA-CIRO-Notice-31-368-Client-Focused-Reforms.pdf)). Cette dernière phrase décrit exactement le cas de Robert. Côté conversation, choisir chaque question selon la valeur de l'information qu'elle apporte permet souvent d'atteindre une décision quasi optimale en **2 ou 3 questions**, mais dans un domaine médical et sur une base de 51 patientes [A] {texte analysé} ([Chajewska et al. 2000](https://faculty.cc.gatech.edu/~isbell/reading/papers/Chajewska-AAAI00.pdf)).

**Une contribution AWS « réelle » se mesure à ce qui disparaîtrait sans AWS.** Les carnets proposent de la définir comme une capacité que le jury peut voir [Inf] : un historique d'exécution rejouable pour chaque recommandation (Step Functions Standard conserve l'historique 90 jours et garantit une exécution unique [V] {page lue} ([AWS Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/choosing-workflow-type.html))), des instantanés de données adressables dans S3 versionné, la journalisation des appels au modèle et un chemin de résidence canadienne documenté. Sur ce dernier point, la plupart des modèles récents appelés depuis le Canada passent par des régions américaines ; seuls **Claude Haiku 5.5 et Amazon Nova Lite v1 disposent d'un profil « ca. » limité aux deux régions canadiennes** [V] {page lue, tableaux analysés par programme} ([fiche Claude Haiku 5.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-5-5.html)). Trois pièges : Bedrock Agents (désormais « Classic ») n'accepte plus de nouveaux clients depuis le 30 juillet 2026 [V] ([AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)), App Runner non plus [V] ([AWS](https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html)), et les vérifications par raisonnement automatisé de Guardrails ne sont offertes ni au Canada ni en français [V] ([AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html)). Le prix relevé pour Haiku 5.5 paraît anormalement bas et doit être vérifié visuellement (fiche 23).

### 1.4 Reformulation proposée du problème

La chaîne initiale reste valable dans ses grandes lignes. Les preuves conduisent à préciser chaque étape et à en ajouter trois.

| # | Étape de l'hypothèse initiale | Ce que les preuves imposent | Étape reformulée [Inf] |
|---|---|---|---|
| 1 | Comprendre la décision réellement visée | Une demande peut viser une allocation, une comparaison A contre B, un test de faisabilité ou une probabilité d'objectif ; un LLM formule mal ces problèmes (Xiao et al.) | Identifier l'**unité de décision** dans un catalogue fermé et la faire confirmer par l'utilisateur |
| 2 | Séparer faits, hypothèses, contradictions, manques | Le LLM repère mal les contradictions (CLAMBER) ; les régulateurs listent celles à vérifier | Schéma de profil où chaque champ porte une valeur, un intervalle ou « inconnu », son origine (déclaré, inféré, défaut) et l'extrait qui le justifie ; règles de contradiction déterministes |
| 3 | Identifier les dimensions du profil | Tolérance, capacité, besoin, horizon, liquidité, connaissances sont distincts ; règle du minimum (OCRI, 31-368) | Profil opérant = min(tolérance, capacité) ; le « besoin » de rendement crée un conflit à résoudre, jamais une hausse automatique du risque |
| 3 bis | (absente) | La valeur de l'information permet de s'arrêter tôt (Chajewska) | **Décider de demander, d'agir ou de s'abstenir**, selon que la réponse changerait ou non la recommandation |
| 4 | Reformuler en problème financier explicite | Taux d'erreur élevés des formulations écrites par LLM | Choisir une formulation validée et typée dans une bibliothèque fermée ; le LLM remplit des paramètres vérifiés |
| 5 | Récupérer données et connaissances | Révisions, calendriers, rendement total, change, licences, absence d'ESG | **Qualifier les données** et déclarer ce qu'elles ne peuvent pas dire (horizon de 15 ans contre 5 ans d'historique, pas d'ESG, univers survivant) |
| 6 | Appliquer des méthodes calculables et justifiées | Moyennes non estimables ; débat 1/N dépendant du protocole | Allocateurs fondés sur la covariance et les contraintes, toujours comparés à des références simples ; justification par la robustesse |
| 7 | Comparer options ou scénarios | Dominance stochastique, probabilité d'objectif, regret, scénarios de stress sont calculables | Comparer aussi à « ne rien faire », à l'encaisse et à un produit simple ; montrer l'incertitude sur les probabilités elles-mêmes |
| 7 bis | (absente) | Le raisonnement affiché n'est pas fidèle ; les nombres écrits par un LLM sont fragiles | **Vérifier avant d'afficher** : chaque nombre vient du registre de calcul, les contraintes du profil sont contrôlées, les documents sont lus en quarantaine |
| 8 | Expliquer résultats, compromis, limites | Les bonnes explications sont contrastives et sélectives ; risque de sur-confiance | Explication construite à partir du registre, par couches, avec une friction volontaire avant la recommandation |
| 9 | Montrer ce qui changerait la conclusion | Points de bascule exacts, IIS, boîtes PRIM, régions de stratégie existent | Ajouter des **hypothèses modifiables** avec recalcul des seuls éléments dépendants |
| 10 | (absente) | Les aides à la décision mesurent connaissance et concordance | **Mesurer la compréhension et la qualité de décision**, pas la qualité du texte |

### 1.5 Questions importantes que la liste initiale omettait

1. **Quelle est l'unité de décision ?** Allocation complète, comparaison de deux options, oui ou non sur un titre à la mode, faisabilité d'un objectif : chacune appelle une formulation différente.
2. **Quand poser une question, quand agir, quand s'abstenir ?** Un utilisateur arrivant avec un dossier complet ne devrait recevoir aucune question. Une donnée manquante devrait déclencher une abstention explicite plutôt qu'une invention ; la sentinelle `REVIEW` de TradingAgents, qui refuse de transformer une sortie illisible en « conserver », en est un exemple [V] {code inspecté} ([rating.py](https://github.com/TauricResearch/TradingAgents/blob/main/tradingagents/agents/rating.py)).
3. **Dans quelle monnaie raisonne l'investisseur ?** Pour un investisseur canadien, tout actif coté en USD porte un risque de change à isoler et à expliquer [Inf].
4. **Que les données ne peuvent-elles pas dire ?** Cinq ans d'historique ne valident pas un horizon de 15 ans (Amira) ; un univers choisi aujourd'hui est survivant ; le jeu de départ n'a ni données ESG ni fondamentaux [Inf].
5. **Comment savoir que l'utilisateur a compris et choisi selon ses valeurs ?** C'est le résultat principal mesuré par les aides à la décision, absent de la chaîne initiale.
6. **Qui a le droit de redistribuer quoi ?** Conditions de Yahoo, licence non commerciale de Coin Metrics, permission requise pour les séries tierces de FRED, licence du jeu de départ inconnue.
7. **Comment un document lu peut-il manipuler la recommandation ?** Une instruction cachée dans une actualité ou un rapport ESG est une attaque démontrée et non résolue (fiche 10).
8. **Que répondre quand les contraintes sont incompatibles ?** Montrer le conflit minimal et la plus petite relaxation, chiffrés par le code (fiche 4).
9. **Comment rejouer exactement une recommandation devant le jury ?** Instantanés de données, registre de calcul, réponses LLM enregistrées.
10. **Quelle part de la valeur vient de la couche agentique, et comment le prouver ?** Une ablation sur des cas identiques est la seule réponse défendable (section 7).
11. **Où les données sont-elles traitées et à quel coût ?** Résidence, quotas, facturation par AWS Marketplace.
12. **Quels biais propres aux LLM touchent nos profils ?** Un biais domestique (home bias) marqué apparaît dans des portefeuilles générés par LLM [I] ([Fieberg et al.](https://www.ifo.de/DocDL/cesifo1_wp11666.pdf)), et la place du bitcoin dans les classements de LLM dépend du cadrage de la question [A] {résumé lu} ([Wu 2026](https://arxiv.org/abs/2606.02528)) : deux points sensibles pour Amira et pour un contexte canadien.

### 1.6 Pistes les plus prometteuses

Comparées entre elles plutôt que dans l'absolu, cinq pistes ressortent des carnets. La première est un **noyau de calcul déterministe avec un registre de calcul** : une bibliothèque fermée de formulations testées (allocateurs fondés sur la covariance, probabilité d'objectif, faisabilité avec IIS, points de bascule) dont chaque résultat est enregistré avec ses entrées et sa version, et que le LLM appelle sans jamais écrire de nombre. C'est la piste la plus étayée (PAL, Program of Thoughts, OptiGuide, principe de FinRobot V2), mais seule, elle répond faiblement au critère d'intelligence agentique. La deuxième est un **profil aligné sur les règles ACVM et OCRI**, avec règles de contradiction déterministes et questions choisies selon leur effet sur la recommandation : elle sert directement le cœur de l'hypothèse initiale (comprendre la décision réelle), mais ses preuves viennent de domaines non financiers. La troisième est une **restitution issue des aides à la décision** : options côte à côte dans les mêmes unités, dotplot quantile du résultat à l'horizon, phrase contrastive (« A plutôt que B parce que... »), condition de bascule, hypothèses modifiables et mesure de la qualité de décision ; ses preuves sont solides en santé et minces en finance. La quatrième est une **contribution AWS centrée sur la traçabilité et la résidence**, avec peu de services, chacun visible dans la démonstration. La cinquième est un **protocole d'évaluation de la couche agentique** (ablation, injection d'erreurs, répétabilité, coût), qui fournit à lui seul la « valeur démontrée de la sophistication » attendue par le jury. Ces pistes se complètent ; la question ouverte est l'endroit où placer l'effort agentique, traitée aux sections 6 et 7.

## 2. Carte des problèmes et solutions existantes

Le problème se décompose en quinze fonctions. Pour chacune, la carte indique les dépendances, les familles de solutions existantes et la couverture par l'existant. Le type de chaque solution est marqué, car de nombreux faux débats mélangent des catégories : **[Fin]** méthode financière (que calculer pour l'investisseur), **[Stat]** méthode statistique (comment estimer, tester, quantifier l'incertitude), **[Prod]** choix produit (ce que voit et fait l'utilisateur, quels services), **[Ag]** mécanisme agentique (comment le LLM est orchestré, contrôlé et vérifié).

### 2.1 Fonctions et dépendances

```
F1 Demande ──► F2 Profil ──► F3 Contradictions ──► F4 Demander / agir / s'abstenir
   ▲                                                         │
   └───────────────────── nouvelle question ◄────────────────┘

F5 Qualification des données ─┐
F2 + F3 ──────────────────────┴──► F6 Formulation ──► F7 Calcul ──► F8 Comparaison ──► F9 Évaluation
                                                         │              │
                                                         └──────┬───────┘
                                                                ▼
                         F10 Vérification ──► F11 Explication ──► F12 Correction ──► retour à F2 ou F7
                                                                        │
                                                                        ▼
                                                          F13 Mesure de la compréhension

Transversales : F14 Traçabilité et rejeu (AWS)    F15 Contrôle de l'orchestration (coûts, boucles)
```

| N° | Fonction | Dépend de | Familles de solutions existantes (type) | Couverture par l'existant |
|---|---|---|---|---|
| F1 | Comprendre la demande et l'unité de décision | | Extraction LLM vers un schéma typé [Ag] ; traduction d'une question en appel à un modèle fixe, motif OptiGuide [Ag] | Partielle : aucune évaluation publiée de l'extraction de profils financiers |
| F2 | Construire le profil (tolérance, capacité, besoin, horizon, liquidité, connaissances, préférences) | F1 | Listes réglementaires ACVM, OCRI, ESMA [Fin/Prod] ; règle du minimum [Fin] ; échelles psychométriques (Grable-Lytton, DOSPERT, FinaMetrica) [Stat] ; distribution builder [Prod] | Bonne pour la structure ; faible pour un instrument ouvert et validé |
| F3 | Détecter contradictions, inconnues et conflits | F2 | Motifs de contradiction listés par les régulateurs [Fin] ; LLM seul peu fiable [Ag] ; « le besoin ne surclasse pas la capacité » [Fin] | Partielle : les motifs existent, aucun outil prêt |
| F4 | Décider de demander, d'agir ou de s'abstenir | F2, F3, F7 | Valeur espérée de l'information et règle d'arrêt [Stat] ; regret minimax [Stat] ; questions générées par LLM guidées par un modèle bayésien [Ag] | Partielle : preuves hors finance |
| F5 | Qualifier les données | | Millésimes ALFRED [Stat/Prod] ; bibliothèques de calendriers [Prod] ; rendement total reconstruit [Fin] ; conversion de change [Fin] ; contrats de données pandera [Prod] | Bonne en briques, aucune intégration prête pour ce jeu |
| F6 | Formuler le problème financier explicite | F2, F5 | Bibliothèque fermée de formulations [Fin] ; formulation par LLM (OptiMUS, Chain-of-Experts) peu fiable [Ag] | Bonne côté formulations ; mauvaise côté formulation par LLM |
| F7 | Calculer allocations, risques, probabilités d'objectif, faisabilité | F5, F6 | Variance minimale avec contraction, ERC, HRP, inverse volatilité, Black-Litterman, CVaR, DRO [Fin/Stat] ; gestion par objectifs [Fin] ; IIS et relaxation élastique [Stat] | Bonne : bibliothèques matures |
| F8 | Comparer options, scénarios et références simples | F7 | Dominance stochastique [Stat] ; regret, satisficing robuste [Stat] ; PRIM [Stat] ; références 1/N, inverse volatilité, encaisse [Fin] | Bonne en méthodes, peu packagée |
| F9 | Évaluer honnêtement | F7, F8 | Walk-forward, validation combinatoire purgée, Sharpe dégonflé, PBO, SPA, MCS [Stat] ; protocole FINSABER [Stat] | Bonne |
| F10 | Vérifier avant d'afficher (fidélité, contraintes, sécurité) | F7 | Calcul délégué au code [Ag] ; registre de calcul et contrat de fidélité [Ag, proposé] ; ancrage contextuel Guardrails [Prod] ; quarantaine des documents, CaMeL [Ag] | Partielle : le motif « nombres injectés par gabarit » n'a aucune évaluation publiée |
| F11 | Expliquer par couches et montrer les points de bascule | F7, F8, F10 | Explication contrastive, contrefactuels [Prod] ; tornado, régions de stratégie, ligne critique [Stat] ; dotplots, éventails, fourchettes [Prod] | Bonne en principe, peu d'études en finance |
| F12 | Corriger une hypothèse sans recommencer | F2, F7, F11 | Cartes d'hypothèses et recalcul par graphe de dépendances (marimo, Hamilton) [Prod] ; initiative mixte [Prod] ; modifiabilité (Dietvorst) [Prod] | Partielle : aucune étude sur un robo-conseiller |
| F13 | Mesurer compréhension et qualité de décision | F11 | Instruments de qualité de décision, échelle de conflit décisionnel, critère Cochrane, tests de numératie [Stat/Prod] | Bonne en santé, rien de validé en finance |
| F14 | Tracer, rejouer, prouver la contribution AWS | toutes | Step Functions Standard, S3 versionné, journalisation Bedrock, AgentCore Observability, conventions OpenTelemetry GenAI [Prod] | Bonne côté services ; aucun échantillon AWS ne fait d'optimisation avec manifeste |
| F15 | Contrôler l'orchestration (coûts, boucles, outils) | toutes | Budgets et plafonds, outils typés, machine à états, taxonomie MAST [Ag] | Bonne en recommandations d'ingénierie |

### 2.2 Parties mal couvertes par l'existant

Onze trous apparaissent dans les carnets. Aucune évaluation publiée ne mesure l'exactitude d'un LLM qui extrait un profil d'investisseur depuis du texte libre. Aucune étude n'applique la sélection de questions par valeur de l'information au conseil financier, ni n'en mesure l'effet sur la qualité de décision. Le motif « nombres injectés par gabarit, puis contrôle par code » n'a pas d'évaluation publiée, et aucune méthode publiée ne vérifie les nombres d'un LLM contre une trace de calcul en finance. Il n'existe pas de banc d'injection propre aux documents financiers. Les sources ESG gratuites et redistribuables sont rares. Aucun instrument de qualité de décision n'est validé pour l'investissement. Aucune étude indépendante ne teste HRP hors échantillon sur un univers mêlant actions, ETF et cryptomonnaies sur cinq ans. Aucun échantillon AWS officiel ne combine optimisation (cvxpy), simulation et manifeste de provenance. Aucun taux d'erreur n'est publié pour des formulations de portefeuille écrites par LLM. Aucune étude utilisateur ne porte sur la divulgation en couches, les diagrammes tornado ou la frontière efficiente auprès de novices en finance. Enfin, aucune étude ne porte sur les questionnaires des robo-conseillers canadiens.

### 2.3 Lire la carte par type de preuve

Les quatre types ne se tranchent pas avec les mêmes preuves. Les choix **[Fin]** et **[Stat]** se tranchent par des théorèmes (convexité, unicité) et par des tests hors échantillon sur nos données ; les choix **[Prod]**, par des tests utilisateurs, même petits ; les choix **[Ag]**, par des ablations et des injections d'erreurs à calcul égal. Mélanger ces registres produit des affirmations invérifiables du type « l'architecture multi-agents donne de meilleures allocations » : la qualité d'une allocation relève du calcul, et dans la conception proposée la couche agentique ne devrait pas la modifier [Inf]. Ce que la couche agentique peut améliorer, et doit démontrer, c'est la compréhension de la demande, le choix des questions, le choix de la formulation et la fidélité de l'explication.

## 3. Tableau comparatif des candidats

Les candidats sont comparés au sein de leur catégorie, sans classement global ni score numérique. Les sept critères sont : **adéquation** (au problème AlphaForge et au jeu de départ : 31 actifs, environ cinq ans de prix quotidiens, pas de fondamentaux, pas de positions d'ETF, pas de preuves ESG) ; **preuves** (niveau et nature) ; **données requises** ; **garanties** (ce qui est démontrable) ; **reproductibilité et licence** ; **coût d'intégration** pour une équipe de datathon ; **utilité datathon**. Les appréciations sont des inférences [Inf] appuyées sur les faits détaillés dans les fiches (section 4) et sourcés dans le registre (section 9).

### 3.1 Systèmes agentiques financiers et échantillons AWS

| Candidat | Adéquation | Preuves | Données requises | Garanties | Reproductibilité et licence | Coût d'intégration | Utilité datathon |
|---|---|---|---|---|---|---|---|
| TradingAgents v0.7.1 | Faible pour le cœur : un titre, une date, aucun objet « profil » | [A] 3 titres, environ 3 mois ; [I] chute après la date de coupure ; [V] aucun coût, rendement annualisé incohérent | Prix Yahoo, actualités, fondamentaux, clés API | Aucune sur tailles de position et prix cibles (texte LLM) | Code Apache-2.0 ; article CC BY 4.0 ; reproduction contestée par des utilisateurs | Élevé : nombreux appels LLM par titre | Morceaux : schémas Pydantic, sentinelle `REVIEW`, contrat point-in-time, client Bedrock |
| FinRobot V2 (finrobot_desktop) | Faible à moyenne : valorisation d'une société | [A] notes de 9 et 10 sur 10 données par des analystes à un rapport ; aucun test sur résultats | États financiers (FMP, Finnhub, EDGAR) | Principe « nombres calculés par code » [A], vérifié en partie | Code Apache-2.0 ; environ 184 000 lignes ; failles de sécurité ouvertes | Élevé | Principe opérateur déterministe, audit, provenance |
| AlphaAgents (BlackRock) | Moyenne : sélection de titres selon un profil de risque | [A] 15 titres technologiques, 4 mois, poids égaux | Fondamentaux, sentiment, valorisation | Aucune ; profil « risque recherché » indiscernable du neutre | Aucun code trouvé | Sans objet | Leçon négative sur le profil par prompt |
| MarketSenseAI 2.0 | Moyenne : sélection sur 100 à 500 titres, coûts inclus | [A] excès de rendement de 8,0 à 18,9 % ; aucune évaluation indépendante | Multi-sources | Aucune | Pas de code selon FINSABER | Sans objet | Inspiration pour l'affichage des coûts |
| ai-hedge-fund | Faible : fonds simulé multi-agents | [V] module de coûts doté de tests | API payante Financial Datasets ou micropaiements USDC | Modèle de coûts explicite | Code MIT | Élevé pour l'ensemble, faible pour le module | Adapter le module `TradingCosts` |
| FinGPT-Forecaster | Faible : prévision de mouvements de prix (DOW 30) | [A] | Données américaines | Aucune | Dépôt MIT ; licences des modèles de base non vérifiées | Élevé | Écarter |
| Robo-conseiller agentique (Ready Tensor) | Moyenne : questionnaire, moyenne-variance, ETF, validations par phase | Aucune évaluation | Non précisé | Validation Pydantic | Licence non indiquée ; code non inspecté | Inconnu | Inspiration de déroulé |
| AWS `market-trends-agent` | Faible à moyenne : analyse de marché conversationnelle | [V] README | Prix récupérés par extraction web | Évaluateurs écrits en code | Apache-2.0 | Moyen | Motif d'évaluateurs codés ; écarter la source de prix |
| AWS `finance-personal-assistant` | Moyenne pour apprendre la chaîne AWS | [V] README | Données d'atelier | Aucune | Apache-2.0 ; requiert Claude Haiku 4.5 | Faible | Style d'outils Strands, étapes de déploiement AgentCore |
| AWS `sample-genai-market-data-analysis` | Faible à moyenne | [V] README ; billet AWS [A] | Données de marché | Aucune | Licence de forme MIT-0 ; modèles et App Runner dépassés | Moyen | Adapter avec prudence |
| AWS `sample-wealth-advisor-demo-platform` | Faible | [V] README | Lac de données, graphe | Aucune | **Aucun fichier LICENSE à la racine** | Élevé | Inspiration seulement |

### 3.2 Méthodes d'allocation sous erreur d'estimation

| Méthode | Adéquation (5 ans, 31 actifs, crypto) | Preuves | Données requises | Garanties | Reproductibilité et licence | Coût | Utilité datathon |
|---|---|---|---|---|---|---|---|
| 1/N [Fin] | Référence obligatoire | [A][V] non battue de façon constante par 14 modèles (DeMiguel) ; [I] battue par des méthodes sans moyennes (Kritzman) | Aucune | Aucune estimation, donc aucune erreur d'estimation | Triviale | Nul | Référence |
| Inverse volatilité, timing de volatilité [Fin/Stat] | Bonne : volatilités seules | [I] la plus robuste sous covariance grossière (Jain et Jain) ; [I] bat 1/N même avec coûts (Kirby et Ostdiek) | Volatilités | Heuristique | skfolio (BSD-3) | Très faible | Référence et candidat |
| Variance minimale sans vente à découvert, contraction Ledoit-Wolf [Fin/Stat] | Bonne : covariance estimable (environ 40 observations par actif) | [I] « optimiser la covariance seule ajoute de la valeur » (Kritzman) ; contraintes équivalentes à une contraction (Jagannathan et Ma) [NV] | Covariance | Optimum global (problème convexe) | skfolio, PyPortfolioOpt | Faible | Candidat central |
| Parité de risque (ERC) [Fin] | Bonne | Propriétés connues (volatilité entre variance minimale et 1/N) [NV] | Covariance | Solution unique [NV] | skfolio `RiskBudgeting` | Faible | Candidat |
| HRP, HERC [Fin/Stat] | Bonne, sans inversion de matrice | Preuve d'origine par simulation [NV] ; [I] deuxième plus robuste (Jain et Jain) ; rien sur un univers mixte | Corrélations | Aucun certificat d'optimalité | skfolio, Riskfolio | Faible | Candidat comparé à la variance minimale |
| Black-Litterman avec prior non marché [Fin/Stat] | Moyenne : pas de capitalisations dans les données | [A] supérieur en crypto (Platanakis et Urquhart, résumé) | Prior choisi et vues de l'utilisateur | Formule fermée | skfolio, PyPortfolioOpt, Riskfolio | Moyen | Montrer l'effet d'une vue |
| Minimisation de la CVaR ou du drawdown conditionnel [Fin] | Moyenne : 5 ans contiennent peu d'épisodes extrêmes indépendants | Formulation linéaire [NV pour l'article] ; implémentations [V] | Scénarios de rendements | Optimum global | Riskfolio, skfolio, PyPortfolioOpt | Faible à moyen | Risque de queue pour Amira et Robert |
| Moyenne-variance robuste, DRO de Wasserstein [Stat] | Moyenne : un rayon à choisir | [A] garanties en échantillon fini sous hypothèses ; un rayon réglé par validation croisée retire la garantie [Inf] | Scénarios | Problème convexe | skfolio `DistributionallyRobustCVaR` | Moyen | Option avancée, avec sensibilité au rayon |
| Efficience rééchantillonnée (Michaud) [Stat] | Faible | [I] critiques (Scherer 2006) | Moyennes, covariance | Aucune | Divers | Moyen | Écarter comme méthode vedette |
| Max-Sharpe sur moyennes empiriques [Fin] | Très faible | [A][V] estimation insuffisante (DeMiguel) | Moyennes | Optimum d'un problème mal estimé | Partout | Faible | Contre-exemple pédagogique seulement |

### 3.3 Formulations de décision et d'explication des conflits

| Formulation | Adéquation | Preuves | Données requises | Garanties | Reproductibilité et licence | Coût | Utilité datathon |
|---|---|---|---|---|---|---|---|
| Dominance stochastique et dominance presque stochastique [Stat] | Comparer l'action à la mode et un ETF équilibré pour Robert | [A][V] Leshno et Levy 2002 (résumé) | Distributions rééchantillonnées à l'horizon | Exacte sur l'échantillon | À coder | Moyen | Élevée |
| Probabilité d'atteindre l'objectif [Fin] | Robert, Mateo | [A] Das et al. ; mouvement brownien géométrique | Horizon, richesse, cible, moyennes, covariances | Dépend du modèle ; incertitude d'échantillonnage | À coder d'après l'article (pas de code officiel) | Moyen | Élevée si présentée en fourchettes |
| Regret minimax sur scénarios [Stat] | Tous | Méthode de manuel [NV] | Table de scénarios | Programme linéaire exact | À coder | Faible | Élevée |
| Satisficing robuste [Stat] | Tous | [A] Long, Sim et Zhou 2023 ; bénéfice hors échantillon seulement empirique | Distribution empirique | Théorème de représentation | À coder | Moyen à élevé | Option |
| Info-gap [Stat] | Faible | [I] équivalent au maximin de Wald, rayon de stabilité local (Sniedovich) | Estimation nominale | Locale seulement | À coder | Faible | Seulement comme « rayon local » |
| Découverte de scénarios (PRIM) [Stat] | « Quand la recommandation échoue-t-elle ? » | [V] EMA Workbench {code inspecté} ; méthode RDM [NV] | Nombreuses simulations perturbées | Descriptive | BSD-3 | Moyen | Élevée |
| IIS et relaxation élastique [Stat] | « Mes contraintes sont-elles compatibles ? » | [A][V] Chinneck ; [V] HiGHS, Pyomo | Contraintes nommées | Exacte en linéaire ; plus grand sous-système réalisable NP-difficile | highspy MIT ; Pyomo | Faible à moyen | Élevée |
| Points de bascule : ligne critique, bissection, prix duaux [Stat] | « Qu'est-ce qui changerait la conclusion ? » | [V] CLA dans PyPortfolioOpt ; dérivées cvxpy | Modèle d'optimisation | Exacte sous le modèle | MIT, Apache-2.0 | Faible | Élevée |
| Front de Pareto par epsilon-contrainte [Fin/Stat] | Arbitrages de Mateo et d'Amira | Méthode standard [Inf] | Modèle convexe | Exact si convexe | cvxpy ; pymoo seulement si non convexe | Moyen | Moyenne |
| Agrégation multicritère TOPSIS, AHP [Stat] | Faible comme cœur | [I] inversion de rangs documentée (Shyur et Shih 2024) | Scores | Aucune | pymcdm MIT ; pyDecision GPL | Faible | Écarter comme cœur ; modèle additif à échelles fixes si besoin |

### 3.4 Bibliothèques de calcul

| Bibliothèque | Adéquation | Preuves (ce qui a été vérifié) | Données requises | Garanties | Licence et version | Coût | Utilité datathon |
|---|---|---|---|---|---|---|---|
| skfolio | Couvre le plus de besoins parmi les bibliothèques inspectées | [V] {code inspecté} allocateurs, références, contraction, walk-forward, validation combinatoire purgée | Matrice de rendements | Solveurs convexes ; exactitude numérique non testée | BSD-3, 1.12.16 (2026-11-14) | Faible | Cœur |
| Riskfolio-Lib | Plus riche en mesures de risque | [V] {code inspecté} plus de 20 mesures, optimisation pire cas | Rendements | Convexe ; MOSEK (commercial) recommandé pour une mesure | BSD-3, 7.4.1 (2026-11-04) | Faible à moyen | Repli pour mesures rares |
| PyPortfolioOpt | Simple ; ligne critique | [V] {code inspecté} | Rendements | Convexe | MIT, 1.6.0 (2026-02-26) | Faible | Points de bascule |
| cvxpy | Contraintes nommées | [V] {code inspecté} dérivées des problèmes paramétrés ; aucune fonction IIS | Modèle | Convexe | Apache-2.0, 1.9.3 | Faible | Faisabilité et relaxation |
| HiGHS / highspy | IIS en linéaire | [V] `getIis` déclaré dans l'en-tête C++ ; exposition Python non vérifiée | Programme linéaire | IIS exacte | MIT, 1.16.0 (2026-11-11) | Faible | Explication d'infaisabilité |
| Pyomo (IIS) | IIS indépendante du solveur | [V] {page lue} peut échouer | Modèle Pyomo | Ensemble minimal | Licence non lue | Moyen | Alternative |
| OR-Tools MathOpt | IIS seulement via Gurobi | [V] {code inspecté} | | | Apache-2.0 ; licence pip de Gurobi restreinte, non commerciale | Moyen | Écarter pour l'IIS |
| arch | Bootstrap par blocs, SPA, StepM, MCS | [V] {code inspecté} | Séries | Tests statistiques | NCSA, 9.0.0 (2026-11-11) | Faible | Évaluation |
| quantstats | Ratios, Sharpe probabiliste | [V] {code inspecté} corrections récentes de bugs | Séries | | Apache-2.0, 0.0.86 | Faible | Contre-vérification seulement |
| EMA Workbench | PRIM, CART | [V] {code inspecté} | Simulations | Descriptive | BSD-3, 3.0.0 | Moyen | Découverte de scénarios |
| pymcdm | 30 méthodes multicritères | [V] {code inspecté} | Scores | | MIT, 1.4.0 | Faible | Seulement si couche multicritère |
| pymoo | Multi-objectif évolutionnaire | [V] {licence lue} | | Aucune hors convexité | Apache-2.0, 0.6.2 | Moyen | Seulement si non convexe |
| cvxportfolio | Non inspecté | | | | **GPL-3.0**, dernière version 2025-07-06 | | Écarter |
| vectorbt | Non inspecté | | | | Apache 2.0 **avec Commons Clause** (pas de vente ni d'hébergement payant) | | Écarter pour une application hébergée |
| pyDecision | Non inspecté | | | | **GPL-3.0-or-later** | | Écarter |
| pypbo | Calcul du PBO | | | | **AGPL-3.0**, absent de PyPI | | Recoder en interne |

### 3.5 Profilage et élicitation

| Candidat | Adéquation | Preuves | Données requises | Garanties | Licence | Coût | Utilité datathon |
|---|---|---|---|---|---|---|---|
| Listes réglementaires (31-103CP 13.2, OCRI GN-3400-21-004, 31-368, ESMA 2022) [Fin/Prod] | Schéma de profil et règles de contradiction | [V] {texte analysé, extraction auto} | Réponses de l'utilisateur | Conformité de structure, non de résultat | Textes publics, à citer | Faible | Élevée |
| Règle du minimum entre tolérance et capacité [Fin] | Profil opérant | [V] OCRI, 31-368 ; [A] Klement | Deux évaluations séparées | Règle explicite | Publique | Très faible | Élevée |
| Échelle Grable-Lytton [Stat] | Tolérance | [A] α = 0,77 sur 160 279 répondants {résumé lu} | Réponses | Fidélité interne modérée | Article CC BY-NC 4.0 ; **licence de l'échelle non claire** | Faible | S'en inspirer pour des items originaux |
| FinaMetrica [Stat] | Tolérance | [A] affirmations du vendeur | | | **Propriétaire** | | Écarter |
| DOSPERT, 30 items [Stat] | Risque général, non spécifique à l'investissement | [A] {page lue} | | | Usage libre avec citation ; usage commercial non précisé | Faible | Faible |
| Loteries et listes de prix multiples [Stat] | Faible comme instrument principal | [A] instables en 30 minutes ; corrélation quasi nulle avec l'auto-déclaration (r = 0,06) | | | | | Signal illustratif au mieux |
| Distribution builder [Prod] | Choisir des résultats plutôt que des produits | [A] fidélité test-retest de 0,70 à 0,80 dans l'année (152 adultes) | Prix d'états | | Méthode publiée | Moyen | Inspiration UX |
| Expérience simulée [Prod] | Compréhension du risque | [A] estimations de probabilité de perte plus justes, mais choix plus risqués (535 étudiants) | Distribution | | | Faible | Avec prudence pour Robert |
| Valeur de l'information et règle d'arrêt (Chajewska) [Stat] | Choix des questions | [A] souvent 2 ou 3 questions (domaine médical) | Prior de population | Perte espérée bornée sous le modèle | À coder | Moyen | Élevée |
| Élicitation par regret minimax (Boutilier) [Stat] | Choix des questions | [A] {résumé lu} | Utilité additive | | À coder | Moyen | Alternative |
| GATE, OPEN [Ag] | LLM qui formule les questions | [A] 388 et environ 255 participants, hors finance ; OPEN bat le LLM seul | | | GATE : licence du dépôt non vérifiée ; OPEN : pas de code trouvé | Moyen | Motif « le modèle bayésien choisit, le LLM formule » |
| Tests adaptatifs (CAT/IRT) [Stat] | Raccourcir une échelle | Aucune banque d'items calibrée et ouverte trouvée | Paramètres d'items | | | Élevé | Écarter faute de calibration |
| Extraction et détection par LLM seul [Ag] | Faible | [A] CLAMBER (38 % des contradictions) ; Ross et Lo | Texte libre | Aucune | | Faible | Écarter comme mécanisme unique |

### 3.6 Restitution et mesure de la compréhension

| Candidat | Adéquation | Preuves | Données requises | Garanties | Licence | Coût | Utilité datathon |
|---|---|---|---|---|---|---|---|
| Squelette IPDAS : décision explicite, options côte à côte, mêmes unités [Prod] | Structure de l'écran de décision | [I] Cochrane 2024 sur les aides à la décision ; normes minimales par Delphi (2014) | Résultats calculés | | Méthode publique | Faible | Élevée |
| Tableau de comparaison façon Option Grid [Prod] | Robert, Mateo | Format | | | **Grilles propriétaires (EBSCO)** : reprendre le format seulement | Faible | Élevée |
| Clarification explicite des valeurs avec retour [Prod] | Mateo (ESG) | [I] Witteman 2021 : effet faible mais significatif ; retour explicite légèrement meilleur | Critères déclarés | | | Faible | Élevée |
| Dotplot quantile [Prod] | Résultat d'un portefeuille | [A] 97 % du gain optimal (tâche de transport, pas de finance) | Quantiles simulés | | Méthode libre ; ggdist (GPL-3.0, R) à ne pas embarquer | Faible | Élevée |
| Graphiques de résultats hypothétiques (HOPs) [Prod] | Comparer 2 ou 3 options | [A] utiles pour les comparaisons, pas pour un actif seul | Tirages | | | Moyen | Moyenne |
| Graphique en éventail [Prod] | Trajectoires | [A] Banque d'Angleterre 2026 | | | | Faible | Moyenne |
| Fourchette numérique avec estimation ponctuelle [Prod] | Texte | [I] van der Bles 2020 : faible perte de confiance (d = -0,15) contre -0,55 pour l'incertitude verbale | | | | Très faible | Élevée |
| Échelle de risque à 5 niveaux de l'Aperçu du fonds [Prod] | Repère familier au Canada | [I] critique : jamais testée auprès des investisseurs, fenêtre de 10 ans | Écart-type sur 10 ans | | | Faible | Ancre seulement, avec drawdown et durée de récupération |
| Explication contrastive et contrefactuel sur les hypothèses [Prod] | Toutes | [A] Miller ; Wachter et al. | Modèle de décision | | DiCE (MIT) seulement si un classifieur existe | Faible | Élevée |
| Tornado, régions de stratégie [Stat/Prod] | Couche expert | Méthode d'analyse de décision [V] {texte analysé, notes de cours} | Modèle | | | Faible | Moyenne à élevée |
| Forçage cognitif [Prod] | Sur-confiance | [A] réduit la sur-confiance, moins apprécié (N = 199) | | | | Faible | Élevée pour Robert |
| Cartes d'hypothèses modifiables et recalcul [Prod] | Corriger sans recommencer | [A] Dietvorst 2018 ; marimo [V] {page lue} | Graphe de dépendances | | marimo Apache-2.0 | Moyen | Élevée |
| Échelle de conflit décisionnel (DCS, SURE) [Stat] | Mesure | [V] seuils < 25 et > 37,5 ; non validée en finance | | | Libre : citer, sans profit, sans modification sauf le nom de la décision | Faible | Indicatif |
| Instruments de qualité de décision (DQI) [Stat] | Méthode de mesure | [V] {page lue} | | | Gratuits pour les chercheurs ; items propres à la santé | Faible | Reprendre la méthode, pas les items |
| Berlin Numeracy Test, « Big Three » de littératie financière [Stat] | Covariables d'un pilote | [A] BNT : 21 études, n = 5 336 | | | BNT : article CC BY 3.0 ; Big Three : conditions formelles non trouvées | Très faible | Élevée pour un pilote |
| Lisibilité automatique, juge LLM [Stat] | Faible comme mesure de succès | [A] corrélations faibles ; meilleur juge r = 0,56 | | | | Faible | Pré-filtre seulement |

### 3.7 Contrôle et vérification agentiques

| Mécanisme | Adéquation | Preuves | Données requises | Garanties | Licence | Coût | Utilité datathon |
|---|---|---|---|---|---|---|---|
| Flux déterministe et un agent outillé [Ag] | Position par défaut | [A] guides d'Anthropic, d'OpenAI, de Cognition ; [A] Kim et al. | | Flux de contrôle déterministe | | Faible | Élevée |
| Orchestrateur, travailleurs en lecture seule, vérification centralisée [Ag] | Lecture de documents en parallèle | [A] Anthropic ; [A] Kim et al. (cas décomposable) | Documents | | | Élevé (environ 15 fois les jetons) | Seulement après ablation |
| Débat libre entre agents [Ag] | Faible | [I] Smit et al. ; Wang et al. ; Zhang et al. ; Choi et al. | | Aucune | | Élevé | Écarter |
| Vote par auto-cohérence [Ag] | Jugements qualitatifs incertains | [A] Li et al., « More Agents » | | | | Moyen | Base de comparaison à calcul égal |
| Critique non ancrée par le même modèle [Ag] | Faible | [I] Huang et al. ; Kamoi et al. | | | | Moyen | Écarter |
| Critique ancrée (trace de calcul, extraits, résultats de contrôles) [Ag] | Vérification | [A] CRITIC ; [I] Kamoi et al. | Registre de calcul | | | Moyen | Élevée |
| Calcul délégué au code (PAL, PoT) [Ag] | Calculs | [A] gains sur FinQA, ConvFinQA, TAT-QA | | | | Faible | Élevée, avec des fonctions fixes testées plutôt que du code généré |
| Nombres injectés par gabarit et contrôle par expression régulière [Ag] | Fidélité numérique | Aucune évaluation publiée ; motif dérivé [Inf] | Registre | Déterministe | | Faible | Élevée |
| Sorties structurées strictes [Ag] | Arguments d'outils | [A] Tam et al. : dégradation du raisonnement sous contrainte de format | | | | Faible | Pour les outils, pas pour le raisonnement |
| CaMeL [Ag] | Sécurité par conception | [A][V] 77 % des tâches avec sécurité prouvable contre 84 % sans défense ; ne couvre pas les attaques texte-à-texte | | Flux de contrôle | Code Google Research (licence non relevée) | Élevé (environ 2,8 fois les jetons) | Inspiration |
| Extraction typée en quarantaine [Ag] | Documents ESG, actualités | Dérivée des motifs « double LLM » [Inf] | Documents | Partielle | | Moyen | Élevée si des documents sont lus |
| Spotlighting (marquage des données) [Ag] | Défense d'appoint | [A] testé contre attaques non adaptatives ; [I] défenses contournées par attaques adaptatives (Nasr) | | Aucune | | Très faible | Défense en profondeur |
| Filtre d'outils [Ag] | Agents qui agissent | [A] 7,5 % de succès d'attaque (AgentDojo) | | | | Faible | Peu utile sans outil à effet de bord |
| Classifieur d'injection [Ag] | Faible | [A] trop de faux positifs | | | | | Signal affiché, jamais blocage |

### 3.8 Frameworks d'orchestration et outillage de traces et d'évaluation

| Candidat | Adéquation | Preuves | Données requises | Garanties et reprise | Licence et version | Coût | Utilité datathon |
|---|---|---|---|---|---|---|---|
| LangGraph | Graphe explicite, points de reprise, interruptions | [A] documentation ; [V] problèmes documentés (MemorySaver non persistant, points de reprise qui grossissent) | | Reprise depuis un point de contrôle | MIT, 1.2.22 (2026-11-14) | Moyen | Élevée |
| Strands Agents | Alignement AWS, nombreux fournisseurs de modèles | [V] {code inspecté} ; OpenTelemetry et validation humaine **non vérifiés** | | | Apache-2.0, 1.65.0 (2026-11-13) | Moyen | Élevée avec AgentCore |
| Pydantic AI | Typage, évaluation des trajectoires d'outils, exécution durable via Temporal | [A] README | | Rejouable via Temporal [Inf] | MIT, 2.68.0 | Moyen | Moyenne à élevée |
| OpenAI Agents SDK | Boucle légère | [V] traçage activé par défaut | | | MIT, 0.24.0 (encore 0.x) | Faible | Moyenne ; désactiver le traçage avant toute donnée |
| Microsoft Agent Framework | Graphes, points de reprise, OpenTelemetry | [A] README | | | MIT, 1.26.0 | Moyen | Faible (hébergement orienté Azure) |
| CrewAI | Rôles et « backstories » | [V] télémétrie anonyme activée par défaut | | | MIT, 1.15.41 | Moyen | Faible (indirection des prompts) |
| AutoGen | | [V] archivé, maintenance seulement | | | MIT (code), CC-BY-4.0 (documentation) | | Écarter |
| smolagents | Actions écrites en code | [V] l'exécuteur local « n'est pas un bac à sable de sécurité » | | | Apache-2.0, 1.26.0 (2026-05-29) | | Écarter |
| Machine à états maison | Transparence maximale | [Inf] | | Rejeu à partir des entrées stockées et des réponses enregistrées | Code propre | Faible | Élevée |
| Arize Phoenix | Visualisation locale des traces | [V] README | | | **Elastic License 2.0** (non approuvée OSI), 21.0.0 | Faible | Élevée en local |
| Langfuse | Traces auto-hébergées | [V] architecture : PostgreSQL, Redis ou Valkey, ClickHouse, S3 | | | MIT hors dossiers `ee/` | Élevé | Moyenne |
| Conventions OpenTelemetry GenAI | Standard de traces (agents, outils, évaluation) | [V] statut « Development » | | | Apache-2.0 | Faible | Élevée en épinglant la version |
| inspect_ai, promptfoo | Suites de scénarios, red teaming | [V] {licence lue} | | | MIT ; inspect_ai en bêta ; promptfoo « fait désormais partie d'OpenAI » [A] | Faible | Élevée |
| DeepEval | Métriques jugées par LLM | [V] {licence lue} | | | Apache-2.0, 4.3.4 | Faible | Signal secondaire |

### 3.9 Données et provenance

| Source ou outil | Adéquation | Preuves | Données requises | Garanties et limites | Licence (des **données** ou du code) | Coût | Utilité datathon |
|---|---|---|---|---|---|---|---|
| ALFRED / API FRED | Millésimes des séries américaines | [V] conditions lues ; paramètres temps réel [NV] (pages expirées) | Identifiants de séries | Point-in-time | Données : avis obligatoire ; permission du propriétaire pour les séries tierces au-delà de l'usage personnel | Faible | Élevée |
| Philadelphia Fed RTDSM | Millésimes macro | [V] {page lue, extraction auto} | | | Non précisée | Faible | Moyenne |
| Banque du Canada (Valet) | USD/CAD | [V] méthodologie et conditions ; code de série `FXUSDCAD` [NV] | | Taux indicatif (8 h à 16 h HE), pas de week-end | Données : attribution et mention des modifications ; ne pas contourner les limites de requêtes | Faible | Élevée |
| Statistique Canada | Macro canadienne | [V] licence | | Millésimes non vérifiés | Licence ouverte avec mention ; client `stats-can` sous **GPL-3.0-or-later** | Faible | Élevée |
| exchange_calendars, pandas_market_calendars | Calendriers TSX, NYSE, 24/7 | [V] métadonnées, README ; codes XTSE et 24/7 [NV] | | Règles livrées dans le code : épingler la version | Code Apache-2.0 ; MIT | Faible | Élevée |
| yfinance et Yahoo | Prix, dividendes | [V] erreurs d'ajustement documentées par les mainteneurs | | « Seules les données américaines semblent parfaites » | Code Apache-2.0 ; **données : les conditions de Yahoo interdisent la collecte automatisée sans permission** | Faible | Recoupement seulement |
| Coin Metrics (archive gratuite) | Crypto | [V] LICENSE | | Actifs et métriques modifiables à tout moment | Données **CC BY-NC 4.0** | Faible | Élevée pour un instantané non commercial |
| CoinGecko API | Crypto | [V] {page lue, extraction auto} | | Cache à rafraîchir toutes les 24 h, en tension avec un instantané figé | Attribution « Powered by CoinGecko » ; pas de redistribution de l'accès | Faible | Moyenne |
| SEC EDGAR | Dépôts américains | [V] {page lue, extraction auto} | | 10 requêtes par seconde, User-Agent déclaré ; émetteurs du TSX sur SEDAR+ [NV] | Accès gratuit ; aucune clause de réutilisation sur la page | Faible | Faible ici |
| OpenFIGI | Clé de jointure | [V] {texte analysé} | | Limites de débit | Identifiants **dans le domaine public** | Faible | Élevée |
| SEC N-PORT | Positions de fonds américains | [V] {page lue, extraction auto} | Fichiers trimestriels de 229 à 691 Mo | Décalage ; régime public mensuel [NV] ; aucun ETF canadien | Données publiques, sans garantie | Moyen | Moyenne pour Amira |
| Fichiers de positions des émetteurs d'ETF | Transparence des ETF | {repéré} | | Formats et conditions non lus | Inconnue | Moyen | Moyenne |
| Analyse de style par les rendements (Sharpe 1992) | Expositions factorielles cachées | [V] {texte analysé, extraction auto} | Rendements | Style moyen ; limites énoncées par l'auteur | Méthode | Faible | Élevée en repli |
| GDELT | Actualités ouvertes | [V] {texte analysé} | | Actualités, pas des controverses vérifiées | Usage illimité avec citation et lien | Moyen | Moyenne pour Mateo |
| SBTi | Objectifs climatiques des entreprises | [V] {texte analysé} | | Mise à jour hebdomadaire | **Aucune licence de données trouvée** | Faible | Moyenne : citer sans redistribuer |
| Sustainalytics, MSCI | Notes ESG | [V] règles de Sustainalytics ; page de conditions MSCI illisible | | | Usage tiers restreint ou inconnu | | Consultation manuelle avec lien |
| pandera | Contrats de données | [V] {licence lue} | | | MIT, 0.36.0 | Faible | Élevée |
| Hamilton | Graphe de fonctions | [V] {licence lue} | | | Apache-2.0, 1.90.0 | Faible | Moyenne |
| MLflow | Fiche d'exécution | [V] {licence lue} | | | Apache, 3.18.0 | Faible | Moyenne |
| prov (W3C PROV) | Provenance de chaque nombre affiché | [V] {licence lue} ; norme W3C [NV] | | | MIT, 3.3.0 | Faible | Moyenne à élevée |
| DVC | Pointeurs de données | [V] {licence lue} | | | Apache-2.0, 3.67.1 | Moyen | Optionnelle |
| lakeFS (serveur) | Versionnement de lac | [V] LICENSE | | | **Business Source License 1.1** | Élevé | Écarter |
| Great Expectations, Kedro, OpenLineage | Plus lourds que nécessaire | [V] {licence lue} | | | Apache-2.0 | Élevé | Écarter à cette échelle |

### 3.10 Services AWS

| Service | Adéquation | Preuves | Région et résidence | Prix relevé | Coût d'intégration | Utilité datathon |
|---|---|---|---|---|---|---|
| Bedrock, `ca.anthropic.claude-haiku-5-5` | LLM actuel avec résidence canadienne | [V] fiche modèle : destinations ca-central-1 et ca-west-1 | Canada seulement | 0,11 et 0,55 USD par million de jetons (entrée, sortie), **à vérifier visuellement** | Faible | Élevée |
| Bedrock, `ca.amazon.nova-lite-v1:0` | Repli peu coûteux | [V] fiche modèle | Canada seulement | 0,064 et 0,256 USD | Faible | Moyenne |
| Bedrock, Sonnet 5.5 (`us.` ou Global) | Qualité supérieure attendue [Inf] | [V] fiche modèle | ca-central-1 et trois régions américaines, ou mondial | 2,20 et 11,00 (géographique) ; 2,00 et 10,00 (mondial) | Faible | Seulement si la résidence est abandonnée et dite |
| Bedrock, modèles en région (Llama 3 70B, Mistral Large 24.02) | Faible | [V] modèles de 2024, contexte 8K et 32K, Llama 3 « Legacy » | ca-central-1 | 3,05 et 4,03 ; 4,60 et 13,80 | Faible | Écarter |
| Guardrails, ancrage contextuel (niveau Classic) | Contrôle probabiliste d'ancrage d'une explication | [V] anglais, français, espagnol ; réponse limitée à 5 000 caractères | Disponible au Canada ; niveau Standard indisponible | 0,10 USD par 1 000 unités de texte | Faible | Moyenne à élevée |
| Guardrails, raisonnement automatisé | Règles de convenance formalisées | [V] anglais (US) seulement, détection seulement | **Absent du Canada** | 0,17 USD par 1 000 unités et par politique | Moyen | Bonus hors résidence ; sinon écarter |
| Step Functions Standard | Piste d'audit rejouable | [V] exécution exactement une fois, historique conservé 90 jours | Prix canadien non résolu | 4 000 transitions gratuites par mois, puis 0,000025 USD (us-east-1) | Faible | Élevée |
| Step Functions Express | | [V] historique non capturé par le service | | | | Faible pour l'audit |
| Lambda (image conteneur) | Calcul déterministe | [V] image jusqu'à 10 Go, 10 240 Mo, 15 minutes | | Non relevé | Faible | Élevée |
| S3 Versioning, Object Lock | Instantanés immuables | [V] {page lue} | Région au choix | Non relevé | Faible | Élevée |
| Journalisation des invocations Bedrock | Prompts et réponses archivés | [V] désactivée par défaut ; même compte et même région | | Non relevé | Faible | Élevée |
| AgentCore Runtime et Observability | Agent hébergé, traces OpenTelemetry | [V] disponibles en Canada (Central), absents de Calgary | | Runtime v1 : 0,0895 USD par vCPU-heure ; Observability au tarif CloudWatch | Moyen | Élevée pour la direction B |
| AgentCore Evaluations | Évaluateurs intégrés et personnalisés | [V] 13 évaluateurs intégrés | Canada (Central) | 0,0024 et 0,012 USD par 1 000 jetons | Moyen | Moyenne |
| AgentCore Policy et Gateway | Règles déterministes sur chaque appel d'outil | [V] {page lue} | Canada (Central) | 0,000025 USD par autorisation | Moyen | Seulement si la démonstration le montre |
| AgentCore harness | Boucle d'agent gérée | [V] modèle par défaut : Claude Opus 5 (pas de profil `ca.`) | | Pas de ligne de prix trouvée | Moyen | Remplacer le modèle par défaut |
| Strands Agents | SDK ouvert | [V] {code inspecté} | | Gratuit | Moyen | Élevée pour la direction B |
| Knowledge Bases | Recherche documentaire gérée | [V] {page lue} | Canada | 5,00 USD par Go et par mois d'index ; 1,00 USD par 1 000 appels | Moyen | Seulement si des documents sont réellement utilisés |
| Flows, Prompt Management | | [V] disponibles au Canada | | | Moyen | Faible : un fichier de prompt dans Git avec son empreinte suffit [Inf] |
| Amplify Hosting | Interface web | [V] page de prix (« gratuit 12 mois » en contradiction avec le plan gratuit de 6 mois) | | | Faible | Élevée |
| ECS Express Mode | Conteneurs | [V] recommandé à la place d'App Runner ; répartiteur de charge permanent | | Non relevé | Moyen | Faible pour une démonstration |
| App Runner | | [V] **fermé aux nouveaux clients** | | | | Écarter |
| Bedrock Agents Classic | | [V] **fermé aux nouveaux clients depuis le 2026-07-30** | | | | Écarter |
| SageMaker, Athena, Glue, Batch | Décoratifs pour quelques dizaines de Mo [Inf] | | | Non relevé | Élevé | Écarter |
| SDK X-Ray | | [V] maintenance depuis le 2026-02-25 | | | | Utiliser OpenTelemetry |

### 3.11 Protocoles d'évaluation et bancs d'essai

| Candidat | Adéquation | Preuves | Données requises | Garanties | Licence | Coût | Utilité datathon |
|---|---|---|---|---|---|---|---|
| Protocole FINSABER | Biais de survie, d'anticipation, de fouille ; commissions ; régimes | [I] KDD 2026, piste Datasets & Benchmarks | Actions américaines | | Code Apache-2.0 ; conditions des données non vérifiées | Moyen | Élevée comme liste de contrôle |
| Profit Mirage | Contamination par la date de coupure | [I] avec réserve (motive le cadre des auteurs) | | | | | Élevée comme argument |
| StockBench | Évaluation postérieure à l'entraînement | [I] | 20 titres du DJIA | | | | Argument |
| FinanceBench, FinDVer | Hallucinations sur des dépôts | [A] 2023 et 2024 | Dépôts | | Jeu FinanceBench sur Hugging Face | | Styles de cas de test |
| AgentDojo | Injection | [A] 97 tâches, 629 cas de sécurité | | | Code ETH (licence non relevée) | Moyen | Gabarit de tests |
| MAST | Taxonomie des échecs | [A] κ = 0,88 | Traces | | | Faible | Étiquetage des traces |
| pass^k (tau-bench) | Fiabilité sur essais répétés | [A] | | | | Faible | Élevée |
| PBO par validation croisée combinatoire ; Sharpe dégonflé | Surapprentissage de backtest | [A][V] {résumé lu} ; formule du Sharpe dégonflé [NV] | Matrice des rendements des configurations | | pypbo AGPL : recoder | Faible | Élevée |
| Validation combinatoire purgée, walk-forward | Distribution de chemins de backtest | [V] {code inspecté} skfolio | | | BSD-3 | Faible | Élevée |
| SPA, MCS | Tests contre références | [V] {code inspecté} arch | | | NCSA | Faible | Élevée |
| Portefeuilles aléatoires (Dirichlet) | Distribution nulle sous les mêmes contraintes | [Inf] | | | | Très faible | Élevée |
| Seuil de chance (Sharpe maximal attendu sans talent) | Calibrer ce qu'on peut affirmer | [Inf] calcul des chercheurs | | | | Très faible | Élevée |

## 4. Fiches approfondies des ressources décisives

Vingt-cinq fiches couvrent les ressources qui pèsent le plus sur les choix. Chacune commence par une ligne d'identification (titre, auteurs ou organisation, date ou version, lien primaire, nature), suivie d'un tableau à sept champs. Quand plusieurs ressources répondent à la même question, elles partagent une fiche.

### Fiche 1. Le débat 1/N contre optimisation

**Titres** : « Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy? » ; « In Defense of Optimization: The Fallacy of 1/N » ; « It's All in the Timing ». **Auteurs** : DeMiguel, Garlappi, Uppal ; Kritzman, Page, Turkington ; Kirby, Ostdiek. **Dates** : Review of Financial Studies 22(5), 2009 ; Financial Analysts Journal 66(2), 2010 ; JFQA 47(2), 2012. **Liens** : [DeMiguel et al.](https://ideas.repec.org/a/oup/rfinst/v22y2009i5p1915-1953.html), [Kritzman et al.](https://ideas.repec.org/a/taf/ufajxx/v66y2010i2p31-39.html), [Kirby et Ostdiek](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/its-all-in-the-timing-simple-active-portfolio-strategies-that-outperform-naive-diversification/05D18E04B226C6E9B8441482CC92F943). **Nature** : articles évalués par les pairs.

| Champ | Contenu |
|---|---|
| Problème réellement traité | L'optimisation de portefeuille bat-elle l'équipondération hors échantillon, une fois l'erreur d'estimation prise en compte ? |
| Méthode et hypothèses | DeMiguel : 14 modèles, 7 jeux de données, ratio de Sharpe, équivalent certain, rotation, plus un calcul analytique de la fenêtre nécessaire. Kritzman : 13 jeux, 1 028 séries, plus de 50 000 portefeuilles optimisés, avec primes constantes de long terme ou variance minimale. Kirby et Ostdiek : stratégies de timing de volatilité à faible rotation. |
| Données nécessaires | Rendements mensuels, surtout d'actions américaines. |
| Résultats rapportés et limites | [A][V] Aucun des 14 modèles n'est constamment meilleur que 1/N ; il faudrait environ 3 000 mois pour 25 actifs et 6 000 pour 50. [I][V] Avec des moyennes estimées sur de courtes fenêtres glissantes, 1/N gagne ; avec des primes constantes ou la variance minimale, l'optimisation gagne, et « optimiser la covariance seule ajoute de la valeur ». [I][V] Le résultat de DeMiguel serait « largement dû au protocole », centré sur des portefeuilles à forte rotation. Limite commune : des conclusions opposées selon le protocole, donc aucune ne se transpose sans test sur nos données. |
| Niveau d'examen réel | {résumé lu} pour les trois. |
| Pertinence pour AlphaForge | Très élevée : fixe les références obligatoires et le principe « pas de moyenne historique comme moteur de l'allocation ». Par interpolation, 31 actifs demanderaient de l'ordre de 3 700 mois contre 60 disponibles [Inf]. |
| Ce qui manque pour l'adopter | Une réplication sur le jeu de départ, crypto comprise. Les preuves propres à la crypto sont minces : Platanakis et Urquhart 2019 {résumé lu} trouvent Black-Litterman supérieur, Platanakis et al. 2018 était inaccessible (« Access Denied »), arXiv 2501.12841 n'a été lu qu'en résumé, sans la réponse. Les ratios souvent cités de Chopra et Ziemba (erreurs sur les moyennes environ dix fois plus coûteuses que sur les variances) n'ont **pas pu être vérifiés** (résumé tronqué) [NV]. |

### Fiche 2. skfolio et les bibliothèques voisines

**Titre** : skfolio. **Organisation** : projet skfolio. **Version** : 1.12.16 publiée le 2026-11-14 (PyPI). **Lien** : [GitHub](https://github.com/skfolio/skfolio). **Nature** : bibliothèque logicielle (BSD-3-Clause, LICENSE lue).

| Champ | Contenu |
|---|---|
| Problème réellement traité | Optimisation de portefeuille avec une interface de type scikit-learn, estimation robuste des moments, validation temporelle. |
| Méthode et hypothèses | [V] {code inspecté} Estimateurs `MeanRisk`, `RiskBudgeting`, `HierarchicalRiskParity`, HERC, NCO, `SchurComplementary`, `DistributionallyRobustCVaR` (rayon par défaut 0,02, niveau 0,95), références `EqualWeighted`, `InverseVolatility`, `Random` ; moments `LedoitWolf`, `OAS`, `GerberCovariance`, `EWCovariance`, `RegimeAdjustedEWCovariance`, `EquilibriumMu` ; validation `WalkForward`, `CombinatorialPurgedCV`, évaluation des prévisions de covariance. |
| Données nécessaires | Matrice de rendements alignés ; aucune donnée fondamentale. |
| Résultats rapportés et limites | Outil, donc pas de performance rapportée. L'exactitude numérique n'a pas été testée pendant la recherche ; ni le PBO ni le Sharpe dégonflé n'apparaissent dans l'énumération des mesures inspectée. |
| Niveau d'examen réel | {code inspecté} (exports et quelques modules) ; {licence lue}. |
| Pertinence pour AlphaForge | Élevée : couvre les références, les allocateurs fondés sur la covariance et la validation. Riskfolio-Lib (BSD-3) sert de repli pour des mesures de risque rares ; PyPortfolioOpt (MIT, relancé avec la 1.6.0 en février 2026) fournit l'algorithme de la ligne critique pour les points de bascule. |
| Ce qui manque pour l'adopter | Un test de cohérence entre bibliothèques, par exemple les poids de variance minimale sans contrainte de skfolio et de PyPortfolioOpt comparés à la formule fermée w = Σ⁻¹1 / (1'Σ⁻¹1) [Inf] ; vérifier qu'aucun chemin utilisé ne dépend d'un solveur commercial (MOSEK). |

### Fiche 3. La gestion par objectifs

**Titres** : « A New Approach to Goals-Based Wealth Management » ; « Dynamic Portfolio Allocation in Goals-Based Wealth Management » ; « Portfolio Optimization with Mental Accounts ». **Auteurs** : Das, Ostrov, Radhakrishnan, Srivastav ; Das, Markowitz, Scheid, Statman. **Dates** : document de travail du 14 mai 2018 (Journal of Investment Management) ; document de travail du 3 mars 2020 ; JFQA 45(2), 2010. **Liens** : [PDF 2018](https://webpages.scu.edu/ftp/dostrov/publications/JOIM.pdf), [PDF 2020](https://webpages.scu.edu/ftp/dostrov/publications/CMS.pdf), [JFQA 2010](https://ideas.repec.org/a/cup/jfinqa/v45y2010i02p311-334_00.html). **Nature** : documents de travail et article évalué par les pairs.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Remplacer un coefficient abstrait d'aversion au risque par la probabilité d'atteindre un objectif à une date donnée. |
| Méthode et hypothèses | [A][V] Sous un mouvement brownien géométrique, chaque niveau de probabilité est une parabole dans le plan volatilité-rendement ; l'optimum est le point de tangence avec la frontière efficiente ; une courbe de seuil de perte ajoute une contrainte de baisse. Version dynamique : programmation dynamique sur une grille (temps, richesse), 15 portefeuilles de la frontière, apports et retraits possibles, plusieurs objectifs pondérés. Comptes mentaux : chaque couple (seuil H, probabilité maximale d'échec α) correspond à un coefficient d'aversion. Formule de référence [Inf] : P(W_T ≥ G) = Φ([ln(W_0/G) + (μ - σ²/2)T] / (σ√T)). |
| Données nécessaires | Richesse initiale, cible, horizon, flux prévus, rendements espérés et covariances. |
| Résultats rapportés et limites | [A] Cas de base (W0 = 100, G = 200, T = 10 ans) : probabilité optimale de 66,9 % calculée en environ 2,9 s ; un apport annuel d'une unité la porte à 73,0 % ; plus de 30 points de mieux qu'une trajectoire de fonds à date cible simulée. Limites visibles : rendements lognormaux, stationnarité, erreur d'estimation non testée, trois fonds indiciels, ni impôts ni frais. L'enquête du premier article a été menée par Franklin Templeton, qui emploie deux des auteurs. |
| Niveau d'examen réel | {texte analysé} pour les PDF de 2018 et 2020 ; condensé CFA lu pour l'article de 2010. |
| Pertinence pour AlphaForge | Élevée pour Robert (3 à 5 ans, préservation du capital) et Mateo (8 à 12 ans) : une métrique compréhensible par un novice. |
| Ce qui manque pour l'adopter | Aucun code officiel trouvé ; l'implémentation est estimée à quelques centaines de lignes [Inf]. Surtout, la probabilité doit être présentée en fourchettes sous plusieurs hypothèses de rendement (historique, contractée, stressée), puisque les moyennes ne sont pas estimables (fiche 1). Aucune étude lue ne montre que ce cadrage améliore des décisions réelles. |

### Fiche 4. Expliquer l'infaisabilité (IIS)

**Titre** : tutoriel « Feasibility and Infeasibility in Optimization » (CPAIOR 2007) et implémentations. **Auteurs et organisations** : J. W. Chinneck (Carleton) ; ERGO-Code (HiGHS) ; Pyomo ; Google (OR-Tools). **Versions** : highspy 1.16.0 (2026-11-11) ; documentation Pyomo 6.9.3 ; ortools 9.15 (2026-01-14). **Liens** : [Chinneck](https://sce.carleton.ca/faculty/chinneck/docs/CPAIOR07InfeasibilityTutorial.pdf), [HiGHS](https://github.com/ERGO-Code/HiGHS), [Pyomo](https://pyomo.readthedocs.io/en/6.9.3/_modules/pyomo/contrib/iis/mis.html), [OR-Tools](https://github.com/google/or-tools), [licence Gurobi restreinte](https://support.gurobi.com/hc/en-us/articles/29682074018833-What-does-Restricted-license-for-non-production-use-only-mean). **Nature** : tutoriel, logiciels, documentation.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Expliquer pourquoi un ensemble de contraintes n'a pas de solution et proposer la plus petite relaxation. |
| Méthode et hypothèses | [A][V] Une IIS est un ensemble infaisable qui devient faisable si l'on retire n'importe lequel de ses membres. Le filtre de suppression renvoie exactement une IIS et reste rapide en programmation linéaire ; le filtre élastique ajoute des variables d'écart et minimise leur somme ; plusieurs IIS peuvent coexister ; trouver le plus grand sous-système faisable est NP-difficile. Conseils de l'auteur : marquer les contraintes « jamais retirables », préférer des IIS courtes, plus faciles à comprendre. |
| Données nécessaires | Contraintes nommées du profil : budget, absence de vente à découvert, plafonds par actif, plafond crypto, exclusions, volatilité maximale, CVaR, rendement cible sous un prior déclaré. |
| Résultats rapportés et limites | [V] HiGHS déclare `getIis` dans son en-tête C++. [V] Pyomo combine relaxation élastique et filtre de suppression avec n'importe quel solveur, mais peut échouer. [V] OR-Tools MathOpt ne prend en charge que Gurobi pour l'IIS, et la licence pip de Gurobi est limitée (2 000 variables et contraintes, 200 variables si le modèle est quadratique) et réservée à un usage non commercial. [V] cvxpy n'a pas de fonction IIS. |
| Niveau d'examen réel | {texte analysé} tutoriel ; {code inspecté} en-tête HiGHS et docstring OR-Tools ; {page lue} Pyomo et Gurobi. |
| Pertinence pour AlphaForge | Élevée : transforme « 7 % de rendement avec au plus 5 % de perte et sans actions » en explication exacte (« ces trois contraintes sont incompatibles ») et en relaxation chiffrée (« à votre plafond de risque, la cible la plus haute atteignable est x % ») [Inf]. |
| Ce qui manque pour l'adopter | Vérifier que `getIis` est exposé dans highspy et s'il couvre les problèmes quadratiques. À défaut, un filtre de suppression maison sur cvxpy, estimé à une trentaine de lignes, suffit pour une vingtaine de contraintes nommées, chaque test de faisabilité prenant quelques millisecondes [Inf]. |

### Fiche 5. OptiGuide et les limites de la formulation par LLM

**Titres** : « Large Language Models for Supply Chain Optimization » (OptiGuide) ; « A Survey of Optimization Modeling Meets LLMs: Progress and Future Directions ». **Auteurs** : Li, Mellou, Zhang, Pathuri, Menache (Microsoft) ; Xiao et al. (Université du Zhejiang, Huawei Noah's Ark). **Dates** : arXiv 2307.03875 (2023) ; IJCAI 2025, piste « survey ». **Liens** : [OptiGuide](https://arxiv.org/abs/2307.03875), [code](https://github.com/microsoft/OptiGuide), [revue](https://arxiv.org/html/2508.10047v1), [OptiMUS](https://arxiv.org/abs/2402.10172). **Nature** : prépublication avec code ; revue de littérature.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Répondre en langage naturel à des questions « et si » sur un modèle d'optimisation, sans laisser le LLM formuler ni résoudre le problème. |
| Méthode et hypothèses | [A] Le LLM traduit la question en appel au modèle existant puis explique la réponse du solveur, sans envoyer les données propriétaires au LLM. |
| Données nécessaires | Un modèle d'optimisation validé et ses paramètres. |
| Résultats rapportés et limites | [A] Démontré sur le placement de serveurs dans la chaîne d'approvisionnement infonuagique de Microsoft ; chiffres d'exactitude non lus. [I][V] La revue a trouvé des erreurs dans au moins 26,4 % des instances de NL4Opt, 54,0 % d'IndustryOR, 8,13 % de MAMO EasyLP et 24,3 % de ComplexOR (vérification par 11 experts, chaque cas recoupé par au moins 3). Sur les bancs nettoyés, GPT-4o en prompting standard atteint 61,2 % (NL4Opt), 38,1 % (IndustryOR) et 42,9 % (ComplexOR). [A] OptiMUS revendique 20 à 30 % d'amélioration sur l'état de l'art, sans préciser l'unité. |
| Niveau d'examen réel | {résumé lu} OptiGuide et OptiMUS ; {licence lue} MIT pour les deux dépôts ; {texte analysé} revue (HTML v1). |
| Pertinence pour AlphaForge | Élevée : modèle d'architecture pour l'agent « qu'est-ce qui changerait la conclusion ». Le LLM associe une demande à un identifiant de formulation et à des paramètres validés, choisit le « et si » à calculer, puis raconte uniquement à partir des nombres retournés [Inf]. |
| Ce qui manque pour l'adopter | Aucune étude ne mesure les erreurs de LLM sur des formulations de portefeuille. Il faut un petit banc interne (questions des personas, identifiant et paramètres attendus), chaque cas vérifié par deux membres de l'équipe, puisque les bancs publics contenaient eux-mêmes beaucoup d'erreurs [Inf]. |

### Fiche 6. Déléguer le calcul au code

**Titres** : PAL (« Program-aided Language Models ») ; « Program of Thoughts Prompting » ; FinanceBench. **Auteurs** : Gao, Madaan, Zhou et al. ; Chen, Ma, Wang, Cohen ; Islam, Kannappan, Kiela et al. (Patronus AI). **Dates** : arXiv 2211.10435 v2 (2023-01) ; TMLR 2023 ; arXiv 2311.11944 (2023-11). **Liens** : [PAL](https://arxiv.org/abs/2211.10435), [PoT](https://arxiv.org/abs/2211.12588), [FinanceBench](https://arxiv.org/abs/2311.11944). **Nature** : prépublication, article de revue, banc d'essai.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Les LLM commettent des erreurs d'arithmétique et de récupération sur des questions numériques, y compris financières. |
| Méthode et hypothèses | [A] Le modèle écrit un programme, un interpréteur Python calcule. FinanceBench : 10 231 questions sur des dépôts d'entreprises cotées, 16 configurations testées sur 150 cas, 2 400 réponses revues à la main. |
| Données nécessaires | Questions et documents financiers. |
| Résultats rapportés et limites | [A] PoT gagne environ 12 % en moyenne sur la chaîne de pensée, sur 5 jeux mathématiques et 3 jeux financiers (FinQA, ConvFinQA, TAT-QA). [A] Dans FinanceBench, GPT-4-Turbo avec un système de récupération a répondu faux ou refusé de répondre à 81 % des questions. Limites : modèles de 2022 et 2023, chiffres absolus datés ; aucune réplication 2025-2026 n'a été vérifiée. |
| Niveau d'examen réel | {résumé lu}. |
| Pertinence pour AlphaForge | Élevée : justifie le principe « le code calcule, le LLM interprète ». Les chercheurs préfèrent une bibliothèque fermée de fonctions testées à du code généré à la volée, non déterministe et à isoler dans un bac à sable [Inf]. |
| Ce qui manque pour l'adopter | Une mesure sur notre propre système : le taux de fidélité numérique (fiche 7). |

### Fiche 7. La fidélité des explications

**Titres** : « Language Models Don't Always Say What They Think » ; « Measuring Faithfulness in Chain-of-Thought Reasoning ». **Auteurs** : Turpin, Michael, Perez, Bowman ; Lanham et al. (Anthropic). **Dates** : NeurIPS 2023 ; 2023. **Liens** : [Turpin et al.](https://arxiv.org/abs/2305.04388), [Lanham et al.](https://arxiv.org/abs/2307.13702), et pour l'attribution [ALCE](https://arxiv.org/abs/2305.14627), [FActScore](https://arxiv.org/abs/2305.14251), [CaMeL](https://arxiv.org/html/2503.18813v2). **Nature** : article de conférence ; prépublication.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Le raisonnement affiché par un modèle reflète-t-il la vraie cause de sa réponse ? |
| Méthode et hypothèses | [A] Ajout de caractéristiques biaisantes (la bonne réponse toujours en « (A) ») ; interventions sur la chaîne de pensée (ajout d'erreurs, paraphrases). |
| Données nécessaires | Tâches de raisonnement (BIG-Bench Hard). |
| Résultats rapportés et limites | [A] Les explications « peuvent systématiquement déformer » la raison réelle, et l'exactitude chute jusqu'à 36 % sur 13 tâches ; plus les modèles sont grands et capables, moins leur raisonnement est fidèle sur la plupart des tâches étudiées. Modèles anciens (GPT-3.5, Claude 1.0). [A] Côté attribution, même les meilleurs modèles manquent d'un appui complet par citation dans environ la moitié des cas sur ELI5 (ALCE). |
| Niveau d'examen réel | {résumé lu} ; CaMeL {texte analysé partiel}. |
| Pertinence pour AlphaForge | Élevée : une solution « auto-explicative » ne peut pas présenter le raisonnement du modèle comme l'explication. Proposition des carnets [Inf] : un **contrat de fidélité**. Chaque explication est une liste d'affirmations typées (numérique, comparative, qualitative sourcée, recommandation) reliées à un identifiant de calcul, à un extrait de source ou à une règle du profil. Les nombres sont injectés par gabarit et un contrôle cherche tout chiffre résiduel absent du registre ; les comparaisons (« A est plus risqué que B ») sont recalculées par le code ; les affirmations sourcées sont vérifiées par extrait, avec un contrôle d'implication journalisé comme probabiliste ; chaque recommandation cite la règle du profil et la sortie d'optimisation dont elle découle. Taux de fidélité = affirmations vérifiées / affirmations totales, par type. |
| Ce qui manque pour l'adopter | Aucune évaluation publiée de ce motif ; aucune méthode publiée ne vérifie les nombres d'un LLM contre une trace de calcul en finance. La norme GSN (Goal Structuring Notation) envisagée pour un arbre de justification n'a pas pu être consultée (page vide) : sa version est **non vérifiée**. |

### Fiche 8. Un agent ou plusieurs ?

**Titres** : « Towards a Science of Scaling Agent Systems » ; « Debate or Vote » ; « Building effective agents » ; « Don't Build Multi-Agents ». **Auteurs** : Kim, Gu, Park et al. (20 auteurs) ; Choi, Zhu, Li ; Erik S. et Barry Zhang (Anthropic) ; Walden Yan (Cognition). **Dates** : arXiv 2512.08296 v3 (première version 2025-12-09) ; NeurIPS 2025 (spotlight) ; 2024-12-19 ; 2025-06-12. **Liens** : [Kim et al.](https://arxiv.org/abs/2512.08296), [Choi et al.](https://arxiv.org/abs/2508.17536), [Anthropic](https://www.anthropic.com/engineering/building-effective-agents), [Cognition](https://cognition.com/blog/dont-build-multi-agents). **Nature** : prépublication, article de conférence, billets d'ingénierie (témoignages de praticiens, pas des validations indépendantes).

| Champ | Contenu |
|---|---|
| Problème réellement traité | Quand une architecture multi-agents bat-elle un agent unique ? |
| Méthode et hypothèses | [A] Kim et al. : 6 bancs agentiques, 5 architectures (agent unique ; multi-agents indépendant, centralisé, décentralisé, hybride), 3 familles de LLM, avec outils, prompts et calcul standardisés. Choi et al. : analyse théorique et empirique du débat. |
| Données nécessaires | Sans objet. |
| Résultats rapportés et limites | [A] Kim : de +80,8 % (raisonnement financier décomposable) à -70,0 % (planification séquentielle) ; saturation quand l'agent seul est fort ; surcoût du multi-agents sur les tâches riches en outils ; propagation des erreurs sans vérification centralisée ; un modèle prédictif modeste (R² = 0,373 en validation croisée) choisit la meilleure architecture dans 87 % des configurations mises de côté. [I] Choi : le vote majoritaire explique l'essentiel des gains ; le débat induit une martingale, donc n'améliore pas seul l'exactitude attendue. [A] Anthropic : chercher la solution la plus simple ; les cadres logiciels ajoutent des couches qui masquent prompts et réponses. [A] Cognition : partager tout le contexte entre agents ; exception acceptable pour des sous-agents en lecture seule. |
| Niveau d'examen réel | {résumé lu} Kim et Choi ; {page lue, extraction auto} billets. |
| Pertinence pour AlphaForge | Très élevée : seule étude contrôlée trouvée qui inclut une tâche financière. Forme compatible avec les preuves si le multi-agents est retenu : orchestrateur et travailleurs en lecture seule renvoyant des résultats typés, vérification déterministe centralisée avant rédaction [Inf]. |
| Ce qui manque pour l'adopter | Le banc financier utilisé par Kim et le sens opérationnel de « décomposable » n'ont pas été lus. Aucune étude ne compare agent unique et multi-agents pour l'aide à la décision d'investissement explicable avec la fidélité comme résultat. Le chiffre de 90,2 % d'Anthropic en faveur du multi-agents vient d'une évaluation interne non publique et confond architecture et budget de jetons [Inf]. |

### Fiche 9. La taxonomie des échecs MAST

**Titre** : « Why Do Multi-Agent LLM Systems Fail? ». **Auteurs** : Cemri, Pan, Yang et al. (13 auteurs). **Date** : arXiv 2503.13657 v3 (2025-10-26). **Liens** : [arXiv](https://arxiv.org/abs/2503.13657), [HTML](https://arxiv.org/html/2503.13657v3). **Nature** : prépublication.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Classer empiriquement pourquoi les systèmes multi-agents échouent. |
| Méthode et hypothèses | [A] Plus de 1 600 traces annotées sur 7 frameworks ; taxonomie construite sur 150 traces avec un accord inter-annotateurs κ = 0,88 ; un annotateur LLM pour passer à l'échelle. |
| Données nécessaires | Traces d'exécution. |
| Résultats rapportés et limites | [V] 14 modes en trois familles : conception du système (non-respect de la tâche ou du rôle, répétition d'étapes, perte d'historique, conditions d'arrêt ignorées) ; désalignement entre agents (réinitialisation, absence de demande de clarification, dérive, rétention d'information, entrée ignorée, décalage raisonnement-action) ; vérification (arrêt prématuré 6,20 %, vérification absente ou incomplète 8,20 %, vérification incorrecte 9,10 %). [A] Les systèmes dotés d'un vérificateur explicite échouent moins, sans que ce soit une solution miracle ; ajouter une vérification de l'objectif global à ChatDev donne +15,6 % de réussite. Modèles analysés anciens. |
| Niveau d'examen réel | {texte analysé partiel}. |
| Pertinence pour AlphaForge | Élevée : grille prête à l'emploi pour étiqueter nos traces, et liste de parades d'ingénierie (plafonds de tours, d'appels et de jetons appliqués par le code ; outils typés avec listes autorisées ; état partagé typé plutôt que conversation entre agents ; validateurs à chaque étape plus une vérification « répond-on à la question de ce profil ? ») [Inf]. |
| Ce qui manque pour l'adopter | Distributions par framework non extraites. L'attribution automatique des échecs reste peu fiable (agent responsable trouvé dans 53,5 % des cas, étape décisive dans 14,2 %) [A] ([Who&When](https://arxiv.org/abs/2505.00212)), d'où une relecture humaine des traces en échec. |

### Fiche 10. L'injection par documents

**Titres** : « Defeating Prompt Injections by Design » (CaMeL) ; AgentDojo ; « The Attacker Moves Second » ; OWASP LLM01:2025. **Auteurs et organisations** : Debenedetti, Shumailov, Fan et al. ; Debenedetti, Zhang, Balunović et al. (ETH Zurich SPY Lab) ; Nasr, Carlini, Sitawarin et al. ; OWASP GenAI Security Project. **Dates** : arXiv 2503.18813 v2 (2025-06-24) ; arXiv 2406.13352 v3 (2024-11) ; arXiv 2510.09023 (2025-10) ; 2025. **Liens** : [CaMeL](https://arxiv.org/abs/2503.18813), [code CaMeL](https://github.com/google-research/camel-prompt-injection), [AgentDojo](https://arxiv.org/abs/2406.13352), [Nasr et al.](https://arxiv.org/abs/2510.09023), [OWASP](https://genai.owasp.org/llmrisk/llm01-prompt-injection/). **Nature** : prépublications ; référentiel professionnel.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Un document récupéré (actualité, rapport ESG, dépôt réglementaire) peut contenir des instructions qui détournent l'agent. |
| Méthode et hypothèses | [A] CaMeL : un LLM privilégié transforme la requête de confiance en programme ; un LLM en quarantaine lit les données non fiables sans pouvoir modifier le flux ; des politiques sont appliquées à chaque appel d'outil. AgentDojo : environnement extensible de 97 tâches et 629 cas de sécurité (courriel, banque en ligne, voyage). |
| Données nécessaires | Documents et outils de l'agent. |
| Résultats rapportés et limites | [A][V] CaMeL résout 77 % des tâches avec une sécurité prouvable contre 84 % sans défense, pour environ 2,8 fois plus de jetons, et **n'empêche pas les attaques texte-à-texte** (un document qui fausse un résumé), exactement le risque principal d'un conseiller en lecture seule. [A] Filtre d'outils : 7,5 % de succès d'attaque, mais inefficace si les outils nécessaires suffisent à l'attaquant ; détecteur d'injection : trop de faux positifs. [I] Nasr et al. contournent 12 défenses récentes avec plus de 90 % de succès pour la plupart. [V] OWASP : on ignore s'il existe une prévention infaillible. |
| Niveau d'examen réel | {texte analysé partiel} CaMeL, AgentDojo, OWASP ; {résumé lu} Nasr et al. |
| Pertinence pour AlphaForge | Moyenne si seuls des prix sont utilisés ; élevée dès que des documents ESG ou des actualités entrent dans l'explication. Parade proposée [Inf] : aucun outil à effet de bord, extraction typée en quarantaine (seul un objet structuré atteint le planificateur), recoupement des chiffres extraits avec les données structurées, marquage des données, détecteur de texte impératif affiché comme signal, provenance visible, suite de tests d'injection. Une implémentation complète de CaMeL serait disproportionnée pour un datathon. |
| Ce qui manque pour l'adopter | Aucun banc d'injection propre aux documents financiers ; les 12 défenses contournées par Nasr n'ont pas été identifiées. |

### Fiche 11. Ce que valent les backtests d'agents LLM

**Titres** : FINSABER (« Can LLM-based Financial Investing Strategies Outperform the Market in Long Run? ») ; « Profit Mirage » ; StockBench ; « Lookahead Bias in Pretrained Language Models ». **Auteurs** : Li, Kim, Cucuringu, Ma ; Li, Zeng, Xing, Xu et al. ; Chen, Yao, Liu, Xin et al. ; Sarkar, Vafa. **Dates** : arXiv 2505.07078 v6 (2026-06-26, KDD 2026, piste Datasets & Benchmarks, oral) ; arXiv 2510.07920 v1 (2025-10-09) ; arXiv 2510.02209 v2 (2026-03-02) ; atelier ICML 2025. **Liens** : [FINSABER](https://arxiv.org/html/2505.07078), [code FINSABER](https://github.com/waylonli/FINSABER), [Profit Mirage](https://arxiv.org/html/2510.07920), [StockBench](https://arxiv.org/html/2510.02209), [Sarkar et Vafa](https://icml.cc/virtual/2025/48685). **Nature** : article accepté, prépublications, poster d'atelier.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Les avantages annoncés par les stratégies d'investissement à base de LLM survivent-ils à des évaluations longues, larges, avec coûts, après la date de coupure du modèle ? |
| Méthode et hypothèses | [I] FINSABER : deux décennies, plus de 100 titres, univers non biaisés construits à partir de listes historiques incluant les titres radiés, commissions explicites, taux sans risque explicite, décomposition par régime. Profit Mirage : constituants du NASDAQ-100 avant et après la coupure de GPT-4o (octobre 2023). StockBench : 20 titres du DJIA de mars à juillet 2025, fenêtre mise à jour pour éviter le chevauchement avec l'entraînement. |
| Données nécessaires | Prix, actualités, univers historiques. |
| Résultats rapportés et limites | [I] FINSABER : les avantages « se détériorent significativement » ; les agents sont trop prudents en marché haussier et trop agressifs en marché baissier ; prolonger l'évaluation de deux mois suffit à changer fortement les résultats ; recommandation de contrôles de risque selon le régime plutôt que de cadres plus complexes. [I] Profit Mirage : « presque tous les agents publiés ne battent pas une référence aléatoire une fois la coupure passée » (réserve : les auteurs proposent ensuite leur propre cadre). [I] StockBench : la plupart des agents ne battent pas l'achat-conservation équipondéré. [I] Sarkar et Vafa : biais d'anticipation mesurable dans des modèles pré-entraînés ; des modèles « chronologiques » existent ([ChronoBERT et ChronoGPT](https://arxiv.org/abs/2502.21206), [Time Machine GPT](https://arxiv.org/abs/2404.18543)). Contrepoint [I] : Fieberg et al. ne voient pas de signe clair d'anticipation pour des portefeuilles de retraite à long horizon. |
| Niveau d'examen réel | {texte analysé} FINSABER ; {texte analysé partiel} Profit Mirage et StockBench ; {résumé lu} Sarkar et Vafa. |
| Pertinence pour AlphaForge | Très élevée : dit ce qu'il ne faut pas revendiquer et fournit une liste de contrôle (coûts, références équipondérées, référence aléatoire, découpage par régime, déclaration explicite que la coupure du modèle est postérieure à la fenêtre testée) [Inf]. |
| Ce qui manque pour l'adopter | Tableaux numériques complets de Profit Mirage non extraits ; statut d'évaluation par les pairs de StockBench et de Profit Mirage non vérifié ; conditions des données de FINSABER non vérifiées. |

### Fiche 12. TradingAgents

**Titre** : « TradingAgents: Multi-Agents LLM Financial Trading Framework ». **Auteurs** : Yijia Xiao, Edward Sun, Di Luo, Wei Wang (UCLA, MIT, Tauric Research). **Versions** : article v7 (2025-06-03) ; dépôt v0.7.1 (2026-10-27), HEAD `9fa1196` du 2026-11-04, 516 commits dont 360 depuis mai 2026. **Liens** : [arXiv](https://arxiv.org/html/2412.20138), [GitHub](https://github.com/TauricResearch/TradingAgents). **Nature** : prépublication (aucun lieu évalué trouvé) ; dépôt maintenu. Détail notable : la version HTML v7 de l'article affiche encore des auteurs fictifs issus d'un gabarit LaTeX au-dessus des vrais auteurs [V].

| Champ | Contenu |
|---|---|
| Problème réellement traité | Décider d'acheter, conserver ou vendre un titre à une date, par une équipe de rôles : analystes, chercheurs haussier et baissier, trader, débatteurs de risque, gestionnaire de portefeuille. |
| Méthode et hypothèses | [V] {code inspecté} Pipeline LangGraph ; indicateurs techniques calculés par code (stockstats) ; décisions sous forme de structures Pydantic générées par le LLM, dont une taille de position en texte libre ; vocabulaire à 5 niveaux et sentinelle `REVIEW` quand aucune note n'est lisible ; journal des décisions passées relu par le gestionnaire ; fournisseur Bedrock natif avec rôle IAM ; règles point-in-time (données non datables « retenues » pour les dates passées) ; 90 fichiers de tests, non exécutés. |
| Données nécessaires | Yahoo (yfinance), Alpha Vantage, EDGAR, FRED, Reddit, StockTwits ; une clé de LLM et une clé Alpha Vantage. |
| Résultats rapportés et limites | [A][V] Article : 3 titres (AAPL, GOOGL, AMZN) du 1er janvier au 29 mars 2024, Sharpe de 5,6 à 8,2, aucune hypothèse de coûts. [V] Le rendement annualisé publié (30,5 % pour AAPL) contredit la formule de l'article, qui donnerait environ 165 % pour 26,62 % sur environ 0,24 an. [V] Tickets : résultats non reproductibles (#168, #137), fuites temporelles corrigées après publication (sentiment actuel servi pour des dates passées #1220, instantané de fondamentaux daté du jour #1300, actualités publiées après la clôture #1518), fuite de connaissances du modèle encore ouverte (#805), absence de test de significativité (#1630). [V] Le module de backtest déclare « ne pas être un simulateur de portefeuille, et ne doit pas en devenir un ». |
| Niveau d'examen réel | {code inspecté} ; {texte analysé} article ; tickets lus via l'API de recherche (titres et débuts de messages, pas les commentaires). |
| Pertinence pour AlphaForge | Faible comme cœur ; moyenne comme réservoir de motifs (schémas, sentinelle, contrat point-in-time, intégration Bedrock). |
| Ce qui manque pour l'adopter | Comme cœur, rien ne peut être comblé : l'unité d'analyse est inadaptée et l'image de « robot de trading » nuirait au propos. Pour reprendre des morceaux, vérifier la présence d'un fichier NOTICE (obligation d'attribution de la licence Apache-2.0). |

### Fiche 13. FinRobot V2

**Titres** : dépôt FinRobot ; « FinRobot: An Open-Source AI Agent Platform for Financial Applications using Large Language Models » ; « FinRobot: AI Agent for Equity Research and Valuation with Large Language Models ». **Organisation** : AI4Finance Foundation. **Versions** : HEAD `63e1884` du 2026-10-24, tags v1.0.0 (2026-03-20) et desktop-v0.1.0 (2026-05-11) ; arXiv 2405.14767 v2 (2024-05-27) ; arXiv 2411.08804 (atelier ICAIF 2024). **Liens** : [GitHub](https://github.com/AI4Finance-Foundation/FinRobot), [livre blanc](https://arxiv.org/html/2405.14767), [article](https://arxiv.org/html/2411.08804). **Nature** : dépôt contenant trois bases de code distinctes (V0 AutoGen « éducatif », V1 OpenAI Agents SDK, V2 PydanticAI, FastAPI, React et Tauri) ; prépublications. Attention : `pip install finrobot` installe la V0.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Analyse et valorisation d'une seule société (DCF, DDM, LBO, comparables), avec un rapport de recherche en 13 chapitres et un objectif de cours à 12 mois. |
| Méthode et hypothèses | [A] « Les nombres sont calculés par le code. Les récits sont assistés par LLM. Chaque sortie est tracée. » [V partiel] 27 modules d'opérateurs déterministes, dont `dcf.py`, qui renvoie des résultats typés et des codes machine « jamais de prose », et un sous-paquet d'audit qui signale des réserves sur les données. Le chemin de chaque nombre depuis le LLM n'a pas été tracé. |
| Données nécessaires | États financiers et estimations (FMP, Finnhub, EDGAR), clés d'API payantes. |
| Résultats rapportés et limites | [V] L'article sur l'analyse d'actions fait noter un rapport par un panel d'analystes (quatre 10 et trois 9 sur 10 en exactitude) et par GPT-4, sans test sur les résultats ni comparaison à l'aveugle avec des rapports humains. [V] Les « compétences de gestion de patrimoine » sont des fiches de prompts recopiées sans modification des extensions MIT d'Anthropic, sans outil associé ni adaptation au Canada. [V] Failles ouvertes : accès non authentifié aux rapports générés (#122), injection de code (#101, #102) ; API locale non authentifiée en mode navigateur. |
| Niveau d'examen réel | {code inspecté} structure, fournisseurs de données, un opérateur, compétences ; {texte analysé} articles. |
| Pertinence pour AlphaForge | Le principe d'architecture est pertinent et citable ; les opérateurs ne le sont presque pas, faute de fondamentaux dans le jeu de départ. Écrire « FinRobot fait de la gestion de patrimoine » serait inexact [Inf]. |
| Ce qui manque pour l'adopter | Tracer chaque chemin du LLM au nombre ; des données fondamentales ; la correction des failles. Pour un datathon, réécrire le contrat « opérateur qui émet des nombres et un code » coûte moins que d'embarquer la pile. |

### Fiche 14. Le LLM comme profileur et conseiller

**Titres** : « One Size Fits None: Heuristic Collapse in LLM Investment Advice » ; CLAMBER ; « Are Generative AI Agents Effective Personalized Financial Advisors? » ; « Using Large Language Models for Financial Advice » ; « How good are LLMs in risk profiling? ». **Auteurs** : Ross, Lo ; Zhang et al. ; Takayanagi, Izumi, Sanz-Cruzado, McCreadie, Ounis ; Fieberg, Hornuf, Meiler, Streich ; Hens, Nordlie. **Dates** : arXiv 2604.23837 (2026-04-26) ; ACL 2024 ; arXiv 2504.05862 v2 (2025) ; CESifo WP 11666 (2025-01-30) ; Finance Research Letters 2025. **Liens** : [Ross et Lo](https://arxiv.org/abs/2604.23837), [CLAMBER](https://arxiv.org/html/2405.12063v2), [Takayanagi et al.](https://arxiv.org/abs/2504.05862), [Fieberg et al.](https://www.ifo.de/DocDL/cesifo1_wp11666.pdf), [Hens et Nordlie](https://df.uzh.ch/en/research/commissioned--research/2025_llm-in-risk-profiling.html). **Nature** : prépublications, article de conférence, document de travail, article court.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Un LLM peut-il construire un profil d'investisseur fiable, repérer les contradictions et en tenir compte dans ses conseils ? |
| Méthode et hypothèses | [A] Ross et Lo : 1 000 profils synthétiques tirés par hypercube latin, modèles de substitution par classe d'actifs, concentration de l'importance des variables. CLAMBER : 12 134 items, 8 types d'ambiguïté dont la contradiction. Takayanagi : étude en laboratoire, 64 participants. Fieberg : 32 LLM × 64 profils = 2 048 portefeuilles de retraite, comparés à 20 robo-conseillers. Hens et Nordlie : 10 cas notés par des banquiers et par deux chatbots, 16 fois chacun. |
| Données nécessaires | Profils synthétiques ou réels, réponses des modèles. |
| Résultats rapportés et limites | [A] La tolérance déclarée pèse 57 à 88 % de l'importance (88,2 % pour les actions avec GPT-4o) ; ni la taille du modèle ni la recherche web ne corrigent l'effondrement. Les carnets citent aussi 55,3 % pour GPT-5.4 sur les actions, sous le bas de cette fourchette : **à revérifier dans le PDF**. [A] Meilleure identification d'ambiguïté 54,25 %, contradictions 38 %, surtout des faux négatifs. [A] Les conseillers LLM égalent souvent les humains pour éliciter mais peinent devant des besoins contradictoires ; les utilisateurs sont peu sensibles à la qualité du conseil. [I] Environ 47 % de réponses avec erreur ; biais domestique marqué ; pas de discrimination selon le genre. [A] Pour environ la moitié des 10 cas, pas de différence significative avec les banquiers ; règles générales trop simples. Limites : surtout des modèles GPT, profils synthétiques, échantillons restreints. |
| Niveau d'examen réel | {texte analysé, extraction auto} Ross et Lo, CLAMBER ; {résumé lu} Takayanagi ; {texte analysé partiel, extraction auto} Fieberg (environ 48 % du texte) ; {page lue} Hens et Nordlie. |
| Pertinence pour AlphaForge | Très élevée : justifie de calculer capacité et faisabilité de l'horizon hors du LLM, de passer au calcul des contraintes dures (bande de risque maximale, poids maximal par titre, plancher de liquidité) et de soumettre la chaîne à un **audit de sensibilité** : perturber le revenu, l'horizon ou la liquidité et vérifier que la recommandation bouge dans le bon sens [Inf]. |
| Ce qui manque pour l'adopter | Aucune évaluation publiée de l'exactitude d'extraction des champs d'un profil financier depuis du texte libre. Il faut un jeu de test interne (phrase vague, question précise, dossier complet, dossier contradictoire pour chaque persona) avec précision et rappel par champ, et rappel de détection des contradictions [Inf]. |

### Fiche 15. Le cadre canadien de connaissance du client et de convenance

**Titres** : Instruction complémentaire 31-103CP, articles 13.2 et 13.3 (consolidée au 2021-03-01) ; OCRI GN-3400-21-004, « Know-your-client and suitability determination for retail clients » (en vigueur le 2021-12-31) ; Avis conjoint du personnel ACVM/OCRI 31-368 (2025-12-10). **Organisations** : ACVM, OCRI. **Liens** : [31-103CP](https://fcnb.ca/sites/default/files/2022-01/31-103CP-CONS-2021-03-01-E.pdf), [GN-3400-21-004](https://www.ciro.ca/news-room/publications/know-your-client-and-suitability-determination-retail-clients), [31-368](https://www.asc.ca/-/media/ASC-Documents-part-1/Regulatory-Instruments/2025/12/6255537-CSA-CIRO-Notice-31-368-Client-Focused-Reforms.pdf), et pour comparaison [ESMA35-43-3172](https://prod.finanssivalvonta.fi/globalassets/en/publications/supervision-releases/2023/esma35-43-3172_guidelines_on_certain_aspects_of_the_mifid_ii_suitability_requirements.pdf), [rapport OSC IAP 2015](https://www.osc.ca/sites/default/files/2021-02/iap_20151112_risk-profiling-report.pdf). **Nature** : instruction réglementaire, lignes directrices, avis du personnel ; rapport commandé par un régulateur.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Ce qu'un conseiller inscrit doit recueillir et comment il détermine qu'une recommandation convient. |
| Méthode et hypothèses | [V] Six éléments : situation personnelle, situation financière (revenu, besoins de liquidité, actifs financiers, valeur nette, levier), besoins et objectifs de placement, connaissances, profil de risque, horizon (dont la faisabilité doit être évaluée). Tolérance et capacité sont des considérations distinctes qui composent ensemble le profil, lequel reflète le plus bas des deux. Ne pas combiner plusieurs variables dans une question ; demander la même information de plusieurs façons pour la valider ; ne pas pré-remplir les questionnaires ; ne pas passer outre les limites pour atteindre un rendement attendu. Mise à jour au moins tous les 12 mois (comptes gérés) ou 36 mois. |
| Données nécessaires | Réponses du client, actifs détenus ailleurs. |
| Résultats rapportés et limites | [V] 31-368 : 105 entreprises examinées. Défauts relevés : se fier à la seule tolérance ; fusionner tolérance et capacité dans un formulaire ; cases faible, moyen, élevé sans justification ; liquidités non recueillies ; fourchettes trop larges (un placement de 400 000 $ représente 8 % à 40 % des actifs financiers nets selon la position dans une tranche de 1 à 5 M$) ; « noter simplement que le client a dirigé l'opération est insuffisant ». [A] Rapport OSC IAP 2015 : seulement 11 % des entreprises pouvaient confirmer que leur questionnaire était validé, 16,7 % des questionnaires analysés étaient adaptés à leur objet, 75 % avaient des pondérations arbitraires, 55,6 % n'avaient aucun mécanisme pour identifier un client qui ne devrait détenir que de l'encaisse ; auteur principal issu d'un fournisseur d'outils de profilage (conflit d'intérêts signalé). Les textes sont des principes, pas un questionnaire prescrit. |
| Niveau d'examen réel | {texte analysé, extraction auto} ; 31-368 lu sur ses 100 000 premiers caractères (sur 108 000) ; rapport OSC lu sur environ 100 000 caractères (sur 262 000) ; texte de la règle 31-103 elle-même non consulté. |
| Pertinence pour AlphaForge | Très élevée : schéma du profil, règles de contradiction, traitement du cas Robert (expliquer pourquoi l'opération ne convient pas et proposer des alternatives bornées, par exemple une petite poche spéculative plafonnée, plutôt qu'obéir ou refuser en silence), panneau « alignement réglementaire » [Inf]. AlphaForge est une simulation et n'est pas un inscrit, ce qu'il faut dire [Inf]. ESMA 2022 ajoute une séquence utile pour Mateo (a-t-il des préférences de durabilité, lesquelles, quelles exclusions, quelle proportion minimale par paliers) et déconseille l'auto-évaluation de la tolérance au profit de la perte acceptée sur une période [V]. |
| Ce qui manque pour l'adopter | Relire les citations dans les PDF avant diffusion ; vérifier les particularités de l'AMF (Québec) ; le règlement Reg BI américain n'a pas pu être consulté (eCFR bloqué). |

### Fiche 16. L'élicitation adaptative des préférences

**Titres** : « Making Rational Decisions using Adaptive Utility Elicitation » ; « Bayesian Preference Elicitation with Language Models » (OPEN) ; « Eliciting Human Preferences with Language Models » (GATE). **Auteurs** : Chajewska, Koller, Parr ; Handa, Gal, Pavlick, Goodman, Andreas, Tamkin, Li ; Li, Tamkin, Goodman, Andreas. **Dates** : AAAI 2000 ; arXiv 2403.05534 v1 (2024-03-08) ; arXiv 2310.11589 v1 (2023-10-17), préenregistré. **Liens** : [Chajewska et al.](https://faculty.cc.gatech.edu/~isbell/reading/papers/Chajewska-AAAI00.pdf), [OPEN](https://arxiv.org/abs/2403.05534), [GATE](https://arxiv.org/abs/2310.11589), [Boutilier et al.](https://www.cs.toronto.edu/~cebly/Papers/BPPS-aij06-abs.html). **Nature** : article de conférence ; prépublications.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Poser seulement les questions qui comptent pour la décision et savoir quand s'arrêter. |
| Méthode et hypothèses | [A] Chajewska : l'utilité est traitée comme une variable aléatoire avec un prior issu d'une population ; la question suivante est choisie par valeur espérée de l'information (myope) ; arrêt quand la perte d'utilité espérée, estimée par Monte Carlo, passe sous un seuil. OPEN : modèle de préférence bayésien sur des caractéristiques extraites par le LLM, question choisie par gain d'information maximal, puis formulée par le LLM. GATE : le LLM génère des questions oui ou non, ou ouvertes. Boutilier : regret minimax sous incertitude de l'utilité. |
| Données nécessaires | Un modèle de décision et des croyances initiales sur les champs décisifs. |
| Résultats rapportés et limites | [A] Chajewska : 2 à 16 questions, souvent 2 ou 3, perte espérée finale d'environ 0,001 à 0,04, sur une décision de diagnostic prénatal (51 patientes, 108 issues). [A] OPEN bat les questions du LLM seul (environ 255 utilisateurs, recommandation d'articles de presse). [A] GATE : les questions oui ou non générées battent les prompts écrits par les utilisateurs dans tous les contextes (388 participants, trois domaines non financiers). Aucun domaine financier ; échantillons américains. |
| Niveau d'examen réel | {texte analysé} Chajewska, OPEN, GATE ; {résumé lu} Boutilier. |
| Pertinence pour AlphaForge | Élevée pour la direction C (section 6). Politique proposée [Inf] : maintenir une croyance sur quelques champs décisifs (bande de tolérance, faits de capacité, horizon, liquidité, exclusions ESG) ; pour chaque question candidate, estimer la probabilité que la réponse change la bande recommandée ; ne poser la meilleure que si la perte ou le regret attendu dépasse un seuil, sinon agir en énonçant les hypothèses ; plafonner à 2 à 5 questions par tour ; préférer des questions fermées. Un dossier complet donne alors zéro question. |
| Ce qui manque pour l'adopter | Aucune évaluation humaine en contexte financier ; licence du dépôt GATE non vérifiée ; aucun code OPEN trouvé ; aucune banque d'items de tolérance calibrée et ouverte pour un test adaptatif. |

### Fiche 17. Les aides à la décision médicales

**Titres** : « Decision aids for people facing health treatment or screening decisions » ; « Clarifying values: an updated and expanded systematic review and meta-analysis » ; Decisional Conflict Scale ; Decision Quality Instruments. **Auteurs et organisations** : Stacey, Lewis, Smith et al. (Cochrane) ; Witteman, Ndjaboue, Vaisson et al. ; A. M. O'Connor (Institut de recherche de l'Hôpital d'Ottawa) ; Sepucha et collègues (MGH). **Dates** : 2024-01-29 (6e version) ; Medical Decision Making 41(7), 2021 ; échelle de 1993 révisée en 2005, manuel de 2010. **Liens** : [Cochrane](https://portal.findresearcher.sdu.dk/da/publications/decision-aids-for-people-facing-health-treatment-or-screening-dec/), [Witteman et al.](https://eprints.whiterose.ac.uk/178930/1/Clarifying%20Values%20An%20Updated%20and%20Expanded%20Systematic%20Review%20and%20Meta-Analysis.pdf), [DCS](https://decisionaid.ohri.ca/eval_dcs.html), [DQI](https://mghdecisionsciences.org/tools-training/decision-quality-instruments/), [normes IPDAS](https://eprints.ncl.ac.uk/208229). **Nature** : revues systématiques avec méta-analyse ; instruments de mesure.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Aider une personne non experte à choisir de façon informée et conforme à ses valeurs. |
| Méthode et hypothèses | [I] Méta-analyses d'essais randomisés (effets aléatoires, GRADE) ; recherche jusqu'en mars 2022 pour Cochrane. |
| Données nécessaires | Taux d'événements stables issus d'essais cliniques, décisions ponctuelles, souvent avec un clinicien. |
| Résultats rapportés et limites | [I][V] 209 études, 107 698 participants : choix informé et conforme aux valeurs RR 1,75 (IC 95 % de 1,44 à 2,13 ; certitude modérée) ; connaissances +11,90 points sur 100 ; perception exacte du risque RR 1,94 ; regret inchangé ; 34 études avec au moins un item à haut risque de biais. [I][V] Witteman : 33 articles, 43 méthodes ; les méthodes explicites de clarification des valeurs réduisent de 4 points de pourcentage les décisions non conformes ; un retour explicite sur l'alignement entre options et valeurs fait « un peu mieux » ; décisions surtout hypothétiques. [V] Échelle de conflit décisionnel : 16, 10 ou 4 items ; un score inférieur à 25 est associé à la mise en œuvre de la décision, supérieur à 37,5 au report. |
| Niveau d'examen réel | {résumé lu} Cochrane (PubMed bloqué par un captcha, lu via le portail de l'Université du Danemark du Sud) ; {texte analysé} Witteman et manuel de l'échelle ; {page lue} DQI ; {résumé lu} normes IPDAS. |
| Pertinence pour AlphaForge | Élevée : squelette d'écran (décision énoncée, options côte à côte, avantages et inconvénients dans les mêmes unités, limites et date des preuves) et mesure de succès « choix informé et conforme aux valeurs » [Inf]. Le conflit de Robert correspond à la sous-échelle « clarté des valeurs ». |
| Ce qui manque pour l'adopter | La transposition a des limites [Inf] : pas de clinicien, distributions de rendements non stationnaires et dépendantes du modèle, résultats continus et dépendants du chemin, décisions révisables. L'échelle n'est pas validée pour l'investissement. Conditions d'usage : la citer, ne pas en tirer profit, ne la modifier que pour nommer la décision. Les items DQI sont propres à la santé : reprendre la méthode, pas les items. |

### Fiche 18. Communiquer l'incertitude

**Titres** : « Uncertainty Displays Using Quantile Dotplots or CDFs Improve Transit Decision-Making » ; « The effects of communicating uncertainty on public trust in facts and numbers » ; « Anchors aweigh? The effect of communicating forecast uncertainty » ; « Improving Investment Decisions with Simulated Experience » ; « The Role of Experience Sampling and Graphical Displays on One's Investment Risk Appetite ». **Auteurs** : Fernandes, Walls, Munson, Hullman, Kay ; van der Bles, van der Linden, Freeman, Spiegelhalter ; McMahon, Naylor, Rholes, Rickards (Banque d'Angleterre) ; Bradbury, Hens, Zeisberger ; Kaufmann, Weber, Haisley. **Dates** : CHI 2018 ; PNAS 117(14), 2020 ; document de travail no 1196, 2026-07-17 ; Review of Finance 19(3), 2015 ; Management Science 59(2), 2013. **Liens** : [Fernandes et al.](https://mucollective.northwestern.edu/project/uncertainty-bus), [van der Bles et al.](https://core.ac.uk/download/305110478.pdf), [Banque d'Angleterre](https://www.bankofengland.co.uk/working-paper/2026/anchors-aweigh-the-effect-of-communicating-forecast-uncertainty), [Bradbury et al.](https://core.ac.uk/download/85223761.pdf), [Kaufmann et al.](https://econpapers.repec.org/RePEc:inm:ormnsc:v:59:y:2013:i:2:p:323-340). **Nature** : articles évalués par les pairs ; document de travail.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Quel format fait comprendre l'incertitude et améliore la décision sans détruire la confiance ? |
| Méthode et hypothèses | [A] Tâche incitée de prise de bus ; cinq études en ligne et un essai de terrain avec BBC News (N total 5 780) ; expérience dynamique (n = 1 600) ; tirages manuels de 130 rendements simulés (535 étudiants de Zurich) ; quatre formats d'information sur le risque d'un fonds. |
| Données nécessaires | Distributions de résultats simulées. |
| Résultats rapportés et limites | [A][V] Dotplot quantile : 97 % du gain optimal (IC de 95 à 98). [A][V] Une fourchette numérique réduit peu la confiance dans les chiffres (d = -0,15), contrairement à l'incertitude exprimée verbalement (-0,55). [A] Les graphiques en éventail sont les mieux compris et limitent le « désancrage » des anticipations après une erreur de prévision. [A] Expérience simulée : estimation médiane de la probabilité de perte de 35,0 % à 25,0 % (vraie valeur 23,3 %), mais 35,2 % des participants passent à plus risqué contre 16,2 % à plus sûr, sans regret ultérieur ; même direction chez Kaufmann et al. Contextes : transport, macroéconomie, étudiants, enjeux surtout hypothétiques. |
| Niveau d'examen réel | {résumé lu} Fernandes, Banque d'Angleterre, Kaufmann ; {texte analysé} van der Bles et Bradbury. |
| Pertinence pour AlphaForge | Élevée [Inf] : dotplot du résultat à l'horizon (« 20 avenirs également probables ») avec le seuil propre au persona (pour Robert : « sous le capital initial ») ; dotplots côte à côte pour comparer deux allocations ; fourchette plus estimation ponctuelle dans le texte, sans formules vagues. Pour Robert, mesurer la calibration (probabilité estimée contre probabilité du modèle) plutôt que l'appétit pour le risque. |
| Ce qui manque pour l'adopter | Aucun test de dotplots auprès d'investisseurs particuliers. Montrer l'incertitude sur la distribution elle-même (deux fenêtres historiques, bootstrap contre modèle paramétrique), surtout pour la crypto à historique court [Inf]. L'écart description-expérience (sous-pondération des événements rares par échantillonnage) n'a pas été vérifié et doit l'être avant d'utiliser des tirages pour le risque de queue. |

### Fiche 19. Sur-confiance, forçage cognitif et modifiabilité

**Titres** : « Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance » ; « To Trust or to Think » ; « Overcoming Algorithm Aversion » ; « Explainable AI and Adoption of Financial Algorithmic Advisors ». **Auteurs** : Bansal, Wu, Zhou et al. ; Buçinca, Malaya, Gajos ; Dietvorst, Simmons, Massey ; Ben-David, Resheff, Tron. **Dates** : CHI 2021 ; CSCW 2021 ; Management Science 64(3), 2018 ; AIES 2021. **Liens** : [Bansal et al.](https://arxiv.org/abs/2006.14779), [Buçinca et al.](https://arxiv.org/abs/2102.09692), [Dietvorst et al.](https://ideas.repec.org/a/inm/ormnsc/v64y2018i3p1155-1170.html), [Ben-David et al.](https://ar5iv.arxiv.org/html/2101.02555). **Nature** : articles évalués par les pairs.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Les explications rendent-elles l'humain meilleur juge de l'IA ? Comment éviter à la fois la sur-confiance et l'aversion pour l'algorithme ? |
| Méthode et hypothèses | [A] Expériences contrôlées et incitées ; Ben-David : jeu stylisé « Lemonade Stand » sur MTurk (n = 449). |
| Données nécessaires | Sans objet. |
| Résultats rapportés et limites | [A] Les explications augmentent l'acceptation des recommandations indépendamment de leur justesse et n'augmentent pas la performance complémentaire. [A] Trois conceptions de forçage cognitif réduisent la sur-confiance par rapport à des explications simples (N = 199) ; les plus efficaces sont les moins appréciées ; les gains sont plus forts chez les personnes à fort besoin de cognition, ce qui pose une question d'équité. [A] Pouvoir modifier, même légèrement, un algorithme imparfait augmente son usage, la performance et la satisfaction. [A] Ben-David : adoption initiale d'environ 73 % avec une explication par la performance contre environ 57 % sinon ; baisse d'environ 28 % après un échec scénarisé, moindre avec explications ; effets souvent marginaux. |
| Niveau d'examen réel | {résumé lu} Bansal, Buçinca, Dietvorst ; {texte analysé} Ben-David. |
| Pertinence pour AlphaForge | Élevée [Inf] : avant de montrer la recommandation, demander à Robert « sur 20 avenirs possibles, dans combien le titre à la mode perd-il plus de 30 % ? », puis révéler le dotplot (forçage cognitif et mesure de calibration à la fois) ; cartes d'hypothèses modifiables. Prévoir et annoncer au jury la baisse d'appréciation liée à la friction. |
| Ce qui manque pour l'adopter | Noms et tailles d'effet des trois conceptions de Buçinca non vérifiés ; aucune étude de robo-conseiller sur la modification d'un profil en cours de route ; un article HAL critique sur les explications par variables en robo-conseil était inaccessible (protection anti-robot). |

### Fiche 20. ESG : divergence, réécriture et biais de taille

**Titres** : « Aggregate Confusion: The Divergence of ESG Ratings » ; « Is History Repeating Itself? The (Un)predictable Past of ESG Ratings » ; « The Influence of Firm Size on the ESG Score ». **Auteurs** : Berg, Kölbel, Rigobon ; Berg, Fabisik, Sautner ; Drempetic, Klein, Zwergel. **Dates** : Review of Finance 26(6), 2022 ; ECGI WP 708/2020 (révisé 2021) ; Journal of Business Ethics 167(2), 2020. **Liens** : [Berg et al. 2022](https://academic.oup.com/rof/article/26/6/1315/6590670), [ECGI](https://www.ecgi.global/publications/working-papers/is-history-repeating-itself-the-unpredictable-past-of-esg-ratings), [Drempetic et al.](https://link.springer.com/content/pdf/10.1007/s10551-019-04164-1.pdf), [GDELT](https://www.gdeltproject.org/about.html), [SBTi](https://sciencebasedtargets.org/target-dashboard), [Sustainalytics](https://www.sustainalytics.com/knowledge-hub/referencing-sustainalytics-esg-risk-ratings). **Nature** : articles évalués par les pairs ; document de travail ; pages de conditions.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Une note ESG constitue-t-elle une preuve fiable sur laquelle fonder une exclusion ou une pondération ? |
| Méthode et hypothèses | [A] Comparaison de six agences et décomposition de la divergence ; comparaison des versions successives de l'historique Refinitiv (ex-ASSET4) ; régressions taille-score. |
| Données nécessaires | Notes de plusieurs agences, idéalement datées. |
| Résultats rapportés et limites | [A] Corrélation moyenne par paires de 0,38 à 0,71 ; divergence due à la mesure (56 %), au périmètre (38 %), aux pondérations (6 %) ; « effet évaluateur » (la vue d'ensemble d'une agence influence ses mesures par catégorie). [A] Réécriture généralisée et continue de l'historique ; la relation positive entre ESG et rendements n'existe que dans les données réécrites. [A] Corrélation positive significative entre taille, ressources consacrées aux données ESG et score. [V] Conditions : GDELT autorise tout usage avec citation et lien, mais ce sont des actualités, pas des controverses vérifiées ; SBTi publie une mise à jour hebdomadaire sans licence de données trouvée ; Sustainalytics restreint toute mention hors du rapport de l'entreprise sans licence payante ; la page de conditions de MSCI était illisible. |
| Niveau d'examen réel | {page de synthèse lue} Berg et al. 2022 ; {résumé lu} ECGI et Drempetic ; {texte analysé} GDELT et SBTi ; {page lue, extraction auto} Sustainalytics. |
| Pertinence pour AlphaForge | Élevée pour Mateo. Modèle de preuve proposé [Inf] : pour chaque couple (émetteur, critère), un état FAVORABLE, DÉFAVORABLE, INCONNU ou SANS OBJET et une liste de preuves (source, type, affirmation, date, date de récupération, lien, licence, confiance, couverture). Ne jamais imputer l'inconnu à une moyenne (biais de taille). N'exclure que sur controverse grave vérifiée (au moins deux sources indépendantes ou une source réglementaire ou judiciaire) ; calculer l'allocation sous chaque agence ou sous l'intervalle min-max et montrer si la recommandation y résiste. |
| Ce qui manque pour l'adopter | Une source ESG utilisable et redistribuable. Le cadre canadien n'est connu que par des résumés de cabinets d'avocats [I] : avis 81-334 révisé du 2024-03-07 sur la divulgation ESG des fonds ([Osler](https://www.osler.com/en/resources/regulations/2024/csa-publishes-updated-guidance-on-esg-related-investment-fund-disclosure)) et loi C-15 ayant reçu la sanction royale le 2026-03-26, qui restreint les dispositions anti-écoblanchiment de la Loi sur la concurrence ([MLT Aikins](https://www.mltaikins.com/insights/federal-government-narrows-scope-of-the-competition-acts-anti-greenwashing-provisions-as-bill-c-15-receives-royal-assent/)). Le PDF primaire de l'avis 81-334 n'a pas pu être chargé. |

### Fiche 21. Données datées, calendriers, rendement total et change

**Ressources** : conditions de l'API FRED ; méthodologie et conditions de la Banque du Canada ; exchange_calendars ; pandas_market_calendars ; documentation « price repair » de yfinance ; conditions de Yahoo ; licence de l'archive Coin Metrics. **Versions** : exchange_calendars 4.13.3 et pandas_market_calendars 5.6.1 (2026-11-14) ; yfinance 1.8.0 (2026-11-03). **Liens** : [FRED](https://fred.stlouisfed.org/docs/api/terms_of_use.html), [Banque du Canada](https://www.bankofcanada.ca/rates/exchange/background-information/), [conditions BdC](https://www.bankofcanada.ca/terms/), [exchange_calendars](https://github.com/gerrymanoim/exchange_calendars), [pandas_market_calendars](https://github.com/rsheftel/pandas_market_calendars), [price repair](https://github.com/ranaroussi/yfinance/blob/main/doc/source/advanced/price_repair.rst), [Yahoo](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html), [Coin Metrics](https://github.com/coinmetrics/data). **Nature** : conditions d'utilisation, documentation, bibliothèques.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Construire des rendements comparables et correctement datés pour 31 actifs sur trois calendriers (TSX, NYSE et Nasdaq, crypto 24/7) et deux devises. |
| Méthode et hypothèses | [Inf] Stockage bitemporel des séries macro (date d'observation et fenêtre pendant laquelle la valeur était connue) ; sans millésime, un délai de publication documenté par série. Rendements calculés sur le calendrier natif de chaque actif, puis cumulés sur une grille de décision (les rendements de samedi et dimanche de la crypto reportés au lundi) ; jours sans cotation en valeur manquante, jamais zéro. Rendement total reconstruit à partir des clôtures brutes, des dividendes et des fractionnements ; la clôture ajustée du fournisseur sert de contrôle, avec alerte au-delà d'un écart d'environ 0,5 %. Rendement en CAD : 1 + r_CAD = (1 + r_USD)(S_t / S_{t-1}), soit r_CAD = r_USD + r_FX en logarithmes, ce qui permet d'attribuer une part du risque au seul change. Annualisation cohérente : mélanger 365 et 252 jours fausse la volatilité de la crypto d'un facteur proche de 1,2. |
| Données nécessaires | Prix bruts, dividendes, fractionnements, USD/CAD, séries macro avec dates de publication. |
| Résultats rapportés et limites | [V] Les règles de calendrier sont livrées dans le code : le résultat dépend de la version installée. [A][V] yfinance documente des ajustements de dividende ou de fractionnement manquants et des ajustements « semblables à un fractionnement » sans fractionnement (exemple SOXS, mai 2026), et des confusions de devise. [V] Yahoo interdit la collecte automatisée sans permission expresse. [V] Le taux de la Banque du Canada est indicatif, publié vers 16 h 30 HE les jours ouvrables de la Banque, destiné à des fins statistiques et non aux transactions ; la Banque déconseille de dépendre d'elle seule. [V] Archive Coin Metrics sous CC BY-NC 4.0. |
| Niveau d'examen réel | {page lue, extraction auto} FRED ; {texte analysé} Banque du Canada, README et documentation, conditions de Yahoo ; {licence lue}. |
| Pertinence pour AlphaForge | Très élevée : un mauvais alignement change les corrélations et les volatilités, donc toutes les allocations. Pour les corrélations crypto-actions, les chercheurs proposent par ordre de coût : rendements hebdomadaires, somme des covariances décalées de -1, 0 et +1 jour, rééchantillonnage horaire de la crypto à 16 h HE, estimateur de Hayashi-Yoshida en intrajournalier [Inf] ; montrer la sensibilité de la matrice au choix devient un élément d'explication. |
| Ce qui manque pour l'adopter | Convention d'horodatage de la crypto dans le jeu de départ ; prix déjà ajustés ou non (risque de double comptage des dividendes) ; paramètres temps réel de l'API FRED et code de série Valet [NV] (pages expirées ou rendues en JavaScript) ; existence de millésimes chez Statistique Canada ; licence du jeu de départ. Les références sur l'asynchronisme (Epps 1979, Scholes-Williams, Dimson) sont [NV] ; Burns-Engle-Mezrich et Hayashi-Yoshida n'ont été que {repérés}. |

### Fiche 22. L'évaluation statistique honnête

**Titres** : « The Probability of Backtest Overfitting » ; « The Deflated Sharpe Ratio » ; implémentations skfolio et arch. **Auteurs** : Bailey, Borwein, López de Prado, Zhu ; Bailey, López de Prado. **Dates** : Journal of Computational Finance (première diffusion SSRN 2013) ; Journal of Portfolio Management 40(5), 2014. **Liens** : [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253), [skfolio](https://github.com/skfolio/skfolio), [arch](https://github.com/bashtage/arch), [quantstats](https://github.com/ranaroussi/quantstats). **Nature** : articles ; bibliothèques.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Avec peu d'années de données, comment éviter de prendre la chance pour du talent quand on compare des configurations ? |
| Méthode et hypothèses | [A][V] Probabilité de surapprentissage du backtest (PBO) estimée par validation croisée combinatoire symétrique : le meilleur en échantillon se classe-t-il sous la médiane hors échantillon ? [NV] La formule du Sharpe dégonflé est donnée de mémoire, cohérente avec le Sharpe probabiliste vérifié dans le code de quantstats. [V] skfolio : `CombinatorialPurgedCV`, `WalkForward`, `optimal_folds_number` ; arch : `SPA` (Hansen), `RealityCheck` (White), `StepM`, `MCS`, bootstraps stationnaire, circulaire et par blocs mobiles. |
| Données nécessaires | Matrice des rendements des configurations essayées, nombre d'essais. |
| Résultats rapportés et limites | [A] Les précautions habituelles par échantillon mis de côté sont « peu fiables et inexactes » pour les backtests d'investissement. [Inf] Seuil de chance sur cinq ans sans talent : Sharpe maximal attendu de 0,70 pour 10 configurations, 0,85 pour 20, 1,02 pour 50, 1,13 pour 100. [Inf] Erreur type d'un Sharpe annualisé de 0,5 mesuré sur cinq ans : environ 0,47, soit un intervalle à 95 % d'environ -0,43 à 1,43. |
| Niveau d'examen réel | {résumé lu} ; {code inspecté}. |
| Pertinence pour AlphaForge | Élevée : compter les configurations essayées, publier le seuil de chance, décider sur le risque, la robustesse et l'adéquation au profil ; ajouter 1 000 portefeuilles aléatoires respectant les mêmes contraintes comme distribution nulle [Inf]. |
| Ce qui manque pour l'adopter | Implémenter Sharpe dégonflé et PBO en interne (pypbo est sous AGPL-3.0, risqué pour une application servie sur AWS [Inf]) ; aucune comparaison indépendante entre validation combinatoire purgée et walk-forward n'a été lue. |

### Fiche 23. AWS (1) : Bedrock au Canada, modèles, prix, quotas, Guardrails

**Ressources** : « Regional availability by models » ; fiches modèles ; pages sur les profils d'inférence et l'inférence inter-régions ; accès aux modèles ; quotas ; page de prix de Bedrock ; pages Guardrails. **Organisation** : AWS. **Dates** : pages sans date ; fiche Claude Haiku 5.5 avec lancement le 2026-10-07 ; page de prix avec og:updated_time 2026-11-12, probablement une date de construction du site [Inf]. **Liens** : [disponibilité par modèle](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html), [fiche Haiku 5.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-5-5.html), [fiche Sonnet 5.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5-5.html), [profils](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html), [accès](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html), [quotas](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-runtime.html), [prix](https://aws.amazon.com/bedrock/pricing/), [ancrage contextuel](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html), [niveaux Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tiers.html). **Nature** : documentation et page de prix officielles.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Appeler un LLM actuel depuis le Canada avec un énoncé de résidence exact, un coût maîtrisé et un contrôle d'ancrage des explications. |
| Méthode et hypothèses | [V] Trois modes de routage : en région, géographique (au sein d'une géographie), mondial. 148 tableaux analysés par programme et 46 fiches parcourues. |
| Données nécessaires | Sans objet. |
| Résultats rapportés et limites | [V] Aucun modèle n'est servi en région à Calgary ; à Montréal, seuls des modèles anciens le sont (Claude 3 Haiku, Llama 3, Mistral Large 24.02, Mixtral, plongements). Profils `ca.` pour Claude Haiku 5.5 et Nova Lite v1 uniquement ; Sonnet 5.5 depuis ca-central-1 passe par un profil `us.` (ca-central-1, us-east-1, us-east-2, us-west-2). Haiku 5.5 : contexte d'un million de jetons, sortie de 128 000, facturé via AWS Marketplace au nom du fournisseur, fin de vie pas avant le 2027-10-07, pas de formulaire de première utilisation requis selon la formulation de la page [Inf]. Les profils inter-régions peuvent stocker prompts et réponses dans les régions de destination pour la détection d'abus ; la documentation demande de vérifier les destinations par `GetInferenceProfile` plutôt que de se fier au préfixe. Quotas par défaut (10 millions de jetons par minute en inter-régions pour Haiku 5.5) possiblement plus bas pour un compte récent ; augmentations non automatiques. Ancrage contextuel Classic disponible au Canada, en français, avec une source limitée à 100 000 caractères et une réponse à 5 000 ; le niveau Standard n'est pas offert au Canada. |
| Niveau d'examen réel | {page lue} ; tableaux analysés par programme ; prix lus par programme dans les fichiers JSON que charge la page, **non vus à l'écran**. |
| Prix et réserves | Haiku 5.5 : 0,10 et 0,50 USD par million de jetons en mondial ; 0,11 et 0,55 en géographique ou en région ; Haiku 4.5 : 1,00 et 5,00 ; Sonnet 5.5 : 2,20 et 11,00 en géographique. **Le prix relevé pour Haiku 5.5 est environ dix fois inférieur à celui de Haiku 4.5 : c'est une anomalie apparente, lue dans un JSON derrière une page rendue en JavaScript, à vérifier visuellement dans un navigateur avant toute citation.** L'estimation de démonstration des chercheurs (environ 1,32 USD par mois de LLM pour 300 exécutions, moins de 5 USD au total, contre environ 30 USD avec Sonnet 5.5) en dépend entièrement [Inf]. **On ignore si les crédits du Free Tier couvrent les modèles facturés via Marketplace**, et si le plan gratuit permet d'appeler des modèles tiers. |
| Pertinence pour AlphaForge | Élevée : choix du modèle et énoncé de résidence. Les données de marché publiques et les profils fictifs ne contiennent pas de données personnelles, donc la résidence est un argument de gouvernance plutôt qu'une contrainte [Inf] ; un énoncé exact et vérifié vaut mieux qu'un choix ambitieux mal décrit. L'équipe dispose d'un accès AWS ; si ce compte est fourni par les organisateurs, les règles du Free Tier peuvent ne pas s'appliquer [Inf]. |
| Ce qui manque pour l'adopter | Vérification visuelle des prix ; `GetInferenceProfile` sur le compte de l'équipe ; test de l'ancrage Classic avec le profil `ca.` ; prise en charge identique des outils et du cache de prompt par les profils `ca.` ; quotas réels du compte. |

### Fiche 24. AWS (2) : la chaîne d'audit

**Ressources** : Step Functions (types de flux, quotas, prix) ; Lambda (quotas, environnements d'exécution) ; S3 Versioning et Object Lock ; journalisation des invocations Bedrock ; avis de maintenance des SDK X-Ray ; AWS Budgets. **Organisation** : AWS. **Liens** : [Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/choosing-workflow-type.html), [prix Step Functions](https://aws.amazon.com/step-functions/pricing/), [Lambda](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html), [Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html), [journalisation Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html), [X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python.html), [Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html). **Nature** : documentation et pages de prix.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Rendre chaque recommandation rejouable et vérifiable par le jury en quelques clics. |
| Méthode et hypothèses | [V] Step Functions Standard : durée jusqu'à un an, exécution exactement une fois, historique consultable par API et dans la console, conservé 90 jours, au plus 25 000 événements par exécution ; Express : au plus 5 minutes, historique non capturé par le service. Lambda : 128 à 10 240 Mo, 15 minutes, image conteneur jusqu'à 10 Go, Python 3.12 à 3.15 pris en charge, quotas réduits pour les comptes récents. S3 Object Lock : modèle WORM, évalué par Cohasset Associates pour SEC 17a-4, CFTC et FINRA, exige le versionnement. Journalisation Bedrock : requêtes, réponses et métadonnées vers S3 ou CloudWatch Logs, même compte et même région, désactivée par défaut. SDK X-Ray en maintenance depuis le 2026-02-25, migration recommandée vers OpenTelemetry. Budgets : alertes, pas de plafond dur ; données mises à jour jusqu'à trois fois par jour. |
| Données nécessaires | Instantanés de données, code versionné. |
| Résultats rapportés et limites | [V] 4 000 transitions Step Functions gratuites par mois, puis 0,000025 USD par transition à us-east-1 ; prix canadien non résolu (gabarit vide dans la page). Prix de Lambda, S3, CloudWatch, API Gateway non relevés. |
| Niveau d'examen réel | {page lue} (introductions et tableaux). |
| Pertinence pour AlphaForge | Élevée : selon les chercheurs, c'est la contribution « réelle et démontrable » au meilleur rapport effort-preuve [Inf]. Manifeste proposé par exécution, dans un compartiment versionné [Inf] : clés et versionIds des données avec leur SHA-256, commit git, empreinte des dépendances et du prompt, identifiant du profil d'inférence, ARN de l'exécution Step Functions, identifiants des requêtes Bedrock, chaque nombre affiché avec son champ source. L'interface affiche à côté de chaque nombre sa source et sa version. |
| Ce qui manque pour l'adopter | Prix canadiens ; latence de démarrage à froid d'une image contenant cvxpy et ses solveurs ; choix du mode d'Object Lock (le mode gouvernance évite de se bloquer soi-même, détail non extrait de la page [Inf]). Un budget avec alertes doit précéder toute construction. |

### Fiche 25. AWS (3) : AgentCore et Strands

**Ressources** : vue d'ensemble d'AgentCore, régions prises en charge, notes de version, observabilité, prix ; dépôt Strands Agents ; dépôt d'échantillons AgentCore. **Organisations** : AWS ; projet Strands Agents (sous direction AWS) ; AWS Labs. **Versions** : Strands, dernier commit du 2026-11-14, PyPI 1.65.0 (2026-11-13), licence Apache-2.0 ; échantillons, HEAD `46313bd` du 2026-11-13, Apache-2.0. **Liens** : [AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html), [régions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html), [notes de version](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/doc-history.html), [prix](https://aws.amazon.com/bedrock/agentcore/pricing/), [Strands](https://github.com/strands-agents/sdk-python), [échantillons](https://github.com/awslabs/amazon-bedrock-agentcore-samples). **Nature** : documentation, SDK, échantillons.

| Champ | Contenu |
|---|---|
| Problème réellement traité | Héberger un agent outillé avec isolation des sessions, traces et évaluations, maintenant que Bedrock Agents Classic est fermé aux nouveaux clients. |
| Méthode et hypothèses | [V] Composants disponibles en Canada (Central) : harness, Runtime (microVM et instances), Memory, Gateway, Identity, outils intégrés (interpréteur de code, navigateur), Observability, Policy, Evaluations, Optimization, Registry ; absents : Payments et Web Search ; Calgary ne figure pas dans le tableau. Harness généralement disponible depuis juillet 2026, avec par défaut « Strands Harness » et Claude Opus 5 en régions commerciales (aucun profil `ca.`). Step Functions s'intègre nativement au harness depuis juillet 2026, avec validation humaine ou routage conditionnel possibles. Policy applique des règles déterministes, compatibles Cedar, à chaque appel d'outil passant par Gateway. Strands : Python 3.10 ou plus, fournisseurs Bedrock, Anthropic, OpenAI, Gemini, Mistral, Ollama, llama.cpp, LiteLLM, SageMaker et d'autres, module de routage et de repli. |
| Données nécessaires | Outils Python de l'équipe. |
| Résultats rapportés et limites | [V] Prix : Runtime v1 à 0,0895 USD par vCPU-heure et 0,00945 USD par Go-heure, facturation à la seconde, processeur non facturé pendant l'attente d'entrées-sorties ; Gateway 0,005 USD par 1 000 invocations ; évaluateurs intégrés 0,0024 et 0,012 USD par 1 000 jetons ; Policy 0,000025 USD par autorisation ; Observability au tarif CloudWatch. [V] Échantillons : `finance-personal-assistant` (atelier d'une heure, Strands, déploiement sur AgentCore, requiert Claude Haiku 4.5) et `market-trends-agent` (LangGraph, cinq évaluateurs écrits en code, prix récupérés par extraction web chez Google et Yahoo). |
| Niveau d'examen réel | {page lue}, tableau des régions analysé ; {code inspecté} Strands (arborescence, pyproject) ; README des échantillons lus, code non exécuté. |
| Pertinence pour AlphaForge | Élevée pour la direction B ; optionnelle pour la direction A. Combinaison la moins captive selon les chercheurs [Inf] : agent écrit avec Strands (testable en local), déployé sur AgentCore Runtime en ca-central-1, avec Observability activée, les calculs restant des fonctions Python appelées comme outils. |
| Ce qui manque pour l'adopter | Limites de session de Runtime (page téléchargée, non lue) ; prise en charge d'OpenTelemetry et de la validation humaine par Strands non vérifiée dans le README ; aucun test réel avec le profil `ca.` ; date de disponibilité générale de Policy non trouvée. |

## 5. Ce qu'on peut réellement reprendre

Chaque élément indique séparément, quand elle est connue, la licence du code, celle des données ou les conditions du modèle. « Utiliser directement » signifie sans réécriture, jamais sans test. Toutes les recommandations de cette section sont des inférences [Inf] fondées sur les fiches.

### 5.1 Utiliser directement

| Élément | Source | Licence | Condition |
|---|---|---|---|
| Allocateurs de référence et fondés sur la covariance, contraction Ledoit-Wolf, walk-forward, validation combinatoire purgée | skfolio | Code BSD-3 | Test de cohérence numérique |
| Algorithme de la ligne critique (points de bascule de l'allocation) | PyPortfolioOpt `CLA` | Code MIT | |
| Contraintes nommées, prix duaux, dérivées par rapport aux paramètres | cvxpy | Code Apache-2.0 | |
| Solveur linéaire et IIS | HiGHS / highspy | Code MIT | Vérifier l'exposition Python de `getIis` |
| Bootstrap par blocs, SPA, MCS | arch | Code NCSA | |
| Découverte de scénarios (PRIM) | EMA Workbench | Code BSD-3 | |
| Calendriers TSX, NYSE, 24/7 | exchange_calendars ou pandas_market_calendars | Code Apache-2.0 ou MIT | Épingler la version et l'inscrire dans le manifeste |
| Contrats de données | pandera | Code MIT | |
| Provenance au format PROV-JSON | prov | Code MIT | |
| Identifiants de jointure | OpenFIGI | Identifiants dans le domaine public | Respecter les limites de débit |
| Taux USD/CAD | Banque du Canada | Données : attribution et mention des modifications | Nommer la convention de moyenne de 8 h à 16 h HE |
| Séries macro canadiennes | Statistique Canada | Données : licence ouverte avec mention de la source | Éviter le client `stats-can` (GPL) si le code est distribué |
| Séries FRED et ALFRED | Banque fédérale de réserve de Saint-Louis | Données : avis obligatoire ; permission pour les séries tierces au-delà de l'usage personnel | Vérifier le propriétaire de chaque série utilisée |
| Schéma KYC et motifs de contradiction | 31-103CP, GN-3400-21-004, 31-368 | Textes publics | Citer ; ne jamais se présenter comme conseiller inscrit |
| Échelle de conflit décisionnel (10 items ou SURE à 4 items) | OHRI | Gratuite : citer, sans profit, sans modification sauf le nom de la décision | Indicative seulement : non validée en finance |
| Berlin Numeracy Test (version à un item) et « Big Three » | Cokely et al. ; Lusardi et Mitchell | Article BNT sous CC BY 3.0 ; Big Three : conditions formelles non trouvées | Covariables d'un pilote |
| Suites de scénarios et tests d'attaque | inspect_ai, promptfoo | Code MIT | |
| Conventions OpenTelemetry GenAI | OpenTelemetry | Apache-2.0 | Statut « Development » : épingler une version |
| Notebook réactif servi comme application, si l'interface en est un | marimo | Code Apache-2.0 | |
| Step Functions Standard, Lambda en image conteneur, S3 versionné, journalisation Bedrock, Budgets | AWS | Services facturés à l'usage | Budget et alertes avant tout déploiement |
| Bedrock Converse avec `ca.anthropic.claude-haiku-5-5` | AWS, Anthropic | Modèle facturé via AWS Marketplace ; conditions d'utilisation du modèle non examinées | Après vérification visuelle du prix et `GetInferenceProfile` |

### 5.2 Adapter

| Élément | Source | Licence | Adaptation nécessaire |
|---|---|---|---|
| Schéma de décision Pydantic et sentinelle `REVIEW` | TradingAgents | Code Apache-2.0 (fichier NOTICE à vérifier) | Passer d'un titre à un profil et une allocation ; aucun nombre écrit par le LLM |
| Contrat point-in-time « donnée retenue si non datable » | TradingAgents | Apache-2.0 | L'étendre aux séries macro et au change |
| Opérateur qui émet des nombres et un code machine ; opérateurs d'audit ; étiquette « calculé par le code » | FinRobot V2 | Apache-2.0 | Réécrire pour des métriques de portefeuille |
| Modèle de coûts (demi-écart, commission par action, impact en racine carrée) | ai-hedge-fund `TradingCosts` | MIT | Paramètres pour ETF canadiens et crypto, affichés et modifiables |
| Liste de contrôle des biais, commissions, découpage par régime | FINSABER | Code Apache-2.0 ; conditions des données non vérifiées | L'appliquer à des allocations sans vente à découvert |
| Style d'outils Strands et étapes de déploiement sur AgentCore | `finance-personal-assistant` | Apache-2.0 | Remplacer Haiku 4.5 par le profil `ca.` retenu |
| Évaluateurs écrits en code branchés sur AgentCore Evaluations | `market-trends-agent` | Apache-2.0 | Écarter sa source de prix par extraction web |
| Programmation dynamique de probabilité d'objectif | Das et al. 2020 | Article (pas de code) | Implémenter ; présenter des fourchettes sous plusieurs hypothèses de rendement |
| Règle d'arrêt par valeur de l'information ; « le modèle bayésien choisit, le LLM formule » | Chajewska et al. ; OPEN | Articles | Croyances sur quelques champs décisifs ; plafond de 2 à 5 questions |
| Séquence de recueil des préférences de durabilité | ESMA 2022 | Lignes directrices publiques | Pour Mateo, avec ESG « inconnu » par défaut |
| Tableau de comparaison par questions fréquentes | Format Option Grid | Format libre ; grilles existantes propriétaires | Ne copier aucune grille existante |
| Analyse de style par les rendements | Sharpe 1992 | Méthode publiée | Rendements hebdomadaires, fenêtres glissantes de 52 à 104 semaines, erreur de suivi hors échantillon, intervalles par bootstrap |
| Dotplot quantile | Kay et al. | Méthode libre (ggdist, GPL-3.0, non réutilisé) | Réimplémenter en Python |
| Échelle de risque à 5 niveaux | Méthode de l'Aperçu du fonds (ACVM) | Méthode publique | Ajouter drawdown maximal, durée de récupération et fenêtre utilisée |
| Grille d'échecs MAST | Cemri et al. | Article | Étiqueter nos propres traces |

### 5.3 Reproduire pour vérifier

| Résultat à reproduire | Pourquoi | Sur quoi |
|---|---|---|
| 1/N contre inverse volatilité, variance minimale, ERC et HRP, avec coûts | Les conclusions publiées dépendent du protocole (fiche 1) | Jeu de départ, walk-forward |
| Seuil de chance du Sharpe maximal attendu | Calibrer ce qu'on peut affirmer | Nombre réel de configurations essayées |
| Sensibilité des corrélations à l'alignement de la crypto | Le choix d'alignement n'est pas neutre | Quotidien avec report du week-end, hebdomadaire, covariances décalées |
| Rendement total reconstruit contre clôture ajustée | Erreurs Yahoo documentées ; risque de double comptage | Un fractionnement et un dividende connus du jeu de départ |
| Cohérence numérique entre bibliothèques | Aucune exactitude testée pendant la recherche | Formule fermée de la variance minimale |
| Sharpe probabiliste de quantstats | Bugs corrigés récemment dans le code | Calcul indépendant |
| Audit de sensibilité de Ross et Lo | Effondrement heuristique | Notre chaîne de profil |
| Tests d'injection à la manière d'AgentDojo | Défenses fragiles face aux attaques adaptatives | Documents synthétiques piégés |
| Incohérence du rendement annualisé de TradingAgents | Exemple pédagogique facultatif pour la présentation | Formule de l'article |

### 5.4 Prendre comme inspiration

| Idée | Source | Ce qu'on en retient |
|---|---|---|
| Agent de citation séparé | Anthropic | Attribuer chaque affirmation à une source après la rédaction ; garder une relecture humaine |
| Graphe de flux de données pour la provenance | CaMeL | Montrer l'origine de chaque contenu affiché, sans implémenter CaMeL entier |
| Niveaux POURQUOI, COMMENT, JUSTIFICATION | Clancey sur MYCIN | Une trace d'appels d'outils n'est pas une explication : expliquer l'objectif et les contraintes, les données et modèles, puis pourquoi ces choix sont raisonnables et leurs faiblesses |
| Explication contrastive et contrefactuelle | Miller ; Wachter et al. | « A plutôt que B, principalement parce que... ; cela changerait si... » |
| Principes d'initiative mixte | Horvitz 1999 | Valeurs inférées affichées comme provisoires ; corriger doit coûter moins qu'accepter une mauvaise supposition |
| Distribution builder, expérience simulée | Goldstein et al. ; Bradbury et al. | Manipuler des résultats plutôt que des produits ; prudence pour Robert |
| Profils de risque par prompt | AlphaAgents | Leçon négative : des profils voisins deviennent indiscernables |
| Résultats nets de coûts | MarketSenseAI 2.0 | Toujours afficher les résultats après coûts |
| Phases validées par un relecteur | Robo-conseiller de Ready Tensor | Déroulé questionnaire, optimisation, correspondance d'ETF, validations |
| Arbre de justification de type dossier d'assurance | GSN (version **non vérifiée**) | Objectif, sous-affirmations, preuves, hypothèses explicites ; sert aussi d'interface « pourquoi ? » |
| Croyances de Dempster-Shafer ou intervalle entre agences | Shafer 1976 [NV] | Distinguer « aucune preuve » de « preuves contradictoires » ; l'intervalle min-max avec un compte de couverture est plus simple |
| Règles Cedar sur les appels d'outils | AgentCore Policy | Seulement si la démonstration montre une règle qui bloque réellement un appel |
| Satisficing robuste ; info-gap comme rayon local | Long, Sim et Zhou ; Sniedovich | « Jusqu'où les entrées peuvent-elles bouger avant que la décision change ? » |
| Tornado, droite de bascule, régions de stratégie | Clemen et Reilly, via des notes de cours | Couche expert, surmontée d'un résumé en langage clair |
| Études de clients AWS (Morningstar, Heurist Finance) | Billets AWS {repéré} | Marketing, aucune preuve technique |

### 5.5 Écarter (avec motif)

| Élément | Motif |
|---|---|
| TradingAgents comme cœur | Un titre et une date ; tailles et prix cibles écrits par le LLM ; aucun objet profil ; nombreux appels ; image de « robot de trading » |
| Résultats publiés de TradingAgents comme preuve | 3 titres sur 3 mois, sans coûts, colonne incohérente, reproduction contestée, fuites corrigées après coup |
| FinRobot V2 comme moteur embarqué | Exige des fondamentaux absents ; pile Tauri et FastAPI volumineuse ; failles ouvertes |
| Compétences « gestion de patrimoine » de FinRobot | Prompts recopiés sans outil ; lire les originaux MIT d'Anthropic si nécessaire |
| FinGPT-Forecaster | Prévision de mouvements de prix sur le DOW 30, sans profil |
| Max-Sharpe sur moyennes empiriques | Moyennes non estimables, sauf comme contre-exemple |
| Efficience rééchantillonnée comme méthode vedette | Critiques publiées, bruit de Monte Carlo, aucune garantie |
| TOPSIS ou AHP comme cœur de décision | Inversion de rangs documentée |
| Formulation d'optimisation écrite par le LLM | Taux d'erreur élevés (fiche 5) |
| Profilage ou détection de contradictions par le LLM seul | Effondrement heuristique ; 38 % des contradictions repérées |
| Débat libre entre agents ; critique non ancrée | Gains réductibles au vote ; pas d'autocorrection sans signal externe |
| Bedrock Agents Classic, App Runner | Fermés aux nouveaux clients |
| Raisonnement automatisé de Guardrails comme pièce centrale | Absent du Canada, anglais seulement, détection seulement ; ne vérifie pas les calculs |
| SageMaker, Athena, Glue, Knowledge Bases sur deux PDF, Cognito sans modèle d'utilisateur, raisonnement automatisé jamais montré | Décoratifs à cette échelle |
| Llama 3 70B ou Mistral Large 24.02 choisis seulement pour la résidence | Modèles de 2024, contexte court, Llama 3 « Legacy » (aucune hausse de quota) |
| Sonnet en routage mondial tout en revendiquant une résidence canadienne | Contradiction |
| Serveur lakeFS | Business Source License 1.1 : usage interne seulement |
| pypbo, vectorbt, cvxportfolio, pyDecision, ggdist dans l'application | AGPL-3.0 ; Commons Clause ; GPL-3.0 (et dernière version de juillet 2025) ; GPL-3.0 ou ultérieure ; GPL-3.0 (R) |
| AutoGen pour un nouveau projet | Archivé, maintenance seulement |
| Exécuteur local de smolagents | « Pas un bac à sable de sécurité » selon son README |
| Données Yahoo versées dans un dépôt public ; prix obtenus par extraction web | Conditions de Yahoo ; publier plutôt le script de reconstruction et un manifeste d'empreintes |
| Imputer un ESG inconnu à une moyenne | Biais de taille documenté |
| Loteries comme instrument principal de tolérance | Instables, faible convergence avec l'auto-déclaration |
| Lisibilité automatique ou juge LLM comme mesure de succès | Faible validité |
| SDK X-Ray | Maintenance depuis février 2026 |
| Télémétrie par défaut de CrewAI, traçage par défaut d'OpenAI Agents SDK, s'ils sont utilisés | Envoi de données non maîtrisé : à désactiver |

## 6. Plusieurs directions de solution

Les quatre directions ci-dessous sont des inférences [Inf] construites à partir des fiches. Elles partagent un socle de calcul déterministe (fiches 1 à 7, 21, 22) que toutes doivent construire ; elles diffèrent par l'endroit où se loge l'effort agentique. Aucune n'est garantie de produire le meilleur résultat, et la meilleure brique de chaque catégorie ne fait pas nécessairement le meilleur système : l'assemblage se juge par l'expérience de la section 7.

### Direction A. Pipeline auditable, LLM aux extrémités

| Champ | Contenu |
|---|---|
| Problème servi | Fiabilité numérique, analyse de données, explicabilité, contribution AWS (fonctions F5 à F11 et F14). |
| Éléments réutilisés | skfolio, ligne critique, filtre de suppression IIS, probabilité d'objectif, bootstrap par blocs, PRIM ; registre de calcul et nombres injectés par gabarit ; « architecture A » des carnets : interface sur Amplify, URL de fonction Lambda ou API Gateway, machine à états Step Functions Standard avec cinq étapes (compréhension de la demande par Bedrock Converse avec `ca.anthropic.claude-haiku-5-5` et validation par schéma JSON ; calcul dans une image Lambda à partir de la version épinglée des données S3, graine fixe ; rédaction de l'explication ; ancrage contextuel Classic et contrôle déterministe des nombres ; écriture du manifeste dans S3 versionné), journalisation Bedrock activée, tout en ca-central-1. |
| Originalité possible de la combinaison | Règles canadiennes de convenance, restitution d'aide à la décision et nombres cliquables jusqu'à leur version S3 et à l'exécution Step Functions qui les a produits. |
| Risques | Faible intelligence agentique visible pour un critère qui pèse 20 % ; conversation rigide face à une phrase vague ; qualité des explications françaises d'un modèle de classe Haiku non mesurée ; perception d'un « robo-conseiller classique ». |
| Preuve de valeur à produire | Fidélité numérique de 100 % par construction, démontrée par injection d'erreurs (E4) ; rejeu d'une exécution devant le jury ; comparaison systématique avec les références ; coût mesuré. |

### Direction B. Agent planificateur sur bibliothèque fermée de formulations

| Champ | Contenu |
|---|---|
| Problème servi | Comprendre des demandes variées et choisir la bonne formulation et les bons « et si » (F1, F6, F8, F11). |
| Éléments réutilisés | Motif OptiGuide ; outils typés à arguments énumérés et listes autorisées ; schémas Pydantic et sentinelle `REVIEW` ; plafonds de tours, d'appels et de jetons ; grille MAST ; Strands déployé sur AgentCore Runtime avec Observability (« architecture B ») ou colonne vertébrale Step Functions avec une étape d'agent pour les seules tâches de langage (« architecture C »). |
| Originalité possible de la combinaison | Les choix de l'agent sont eux-mêmes expliqués et mesurés (« j'ai choisi un test de faisabilité parce que vos contraintes semblent incompatibles »), avec un taux de routage correct publié. |
| Risques | Erreurs de routage ; boucles et coûts ; traces plus riches mais moins rejouables qu'une exécution Step Functions ; services récents (harness disponible depuis juillet 2026) ; modèle par défaut du harness à remplacer pour la résidence ; charge d'évaluation. |
| Preuve de valeur à produire | Exactitude du routage sur un banc interne vérifié par deux personnes, fiabilité sur trois essais (pass^3), coût par demande, comparaison avec une table de correspondance fixe sur les mêmes cas. |

### Direction C. Élicitation adaptative et conflits explicites

| Champ | Contenu |
|---|---|
| Problème servi | Le cœur de l'hypothèse initiale : comprendre la décision réelle, séparer faits, hypothèses, contradictions et manques, ne poser que les questions utiles, traiter le conflit de Robert (F1 à F4, F12, F13). |
| Éléments réutilisés | Schéma ACVM et OCRI ; règle du minimum ; règles de contradiction déterministes ; règle d'arrêt par valeur de l'information ; motif OPEN ; questions fermées à la manière de GATE ; séquence ESMA pour l'ESG de Mateo ; cartes d'hypothèses modifiables ; forçage cognitif ; mesure de la qualité de décision et SURE. |
| Originalité possible de la combinaison | La sélection des questions est pilotée par le modèle de décision (la réponse changerait-elle la bande recommandée ?) plutôt que par un questionnaire fixe, et les conflits sont documentés comme l'exigent les régulateurs canadiens. |
| Risques | Aucune preuve financière pour l'élicitation par valeur de l'information ; évaluation sur petit échantillon ; complexité du modèle de croyances ; erreurs d'extraction du LLM ; temps de développement de l'interface. |
| Preuve de valeur à produire | Rappel de détection des contradictions scriptées comparé à A ; nombre de questions comparé à la stabilité de la recommandation ; audit de sensibilité du profil ; pilote de compréhension (E6). |

### Direction D. Lecteurs documentaires en quarantaine, intégrateur et vérificateur ancré

| Champ | Contenu |
|---|---|
| Problème servi | Preuves ESG pour Mateo et expositions cachées pour Amira (même titre détenu directement et dans des ETF, exposition crypto d'actions minières), là où des documents externes sont nécessaires (F5, F10). |
| Éléments réutilisés | Orchestrateur et travailleurs en lecture seule avec vérification centralisée ; extraction typée en quarantaine ; marquage des données ; GDELT, SBTi, N-PORT, fichiers d'émetteurs, OpenFIGI ; modèle de preuve à états avec INCONNU ; intervalle entre agences ; analyse de style par les rendements en repli ; suite de tests d'injection ; grille MAST. |
| Originalité possible de la combinaison | L'ESG comme ensemble de preuves sourcées avec des états INCONNU et DIVERGENT, et une allocation dont on montre la robustesse au choix de la source ; une lecture de documents conçue contre l'injection. |
| Risques | Licences et droits de redistribution ; résolution d'entités (nom d'entreprise vers émetteur) ; actualités GDELT qui ne sont pas des controverses vérifiées ; injection ; coût d'environ 15 fois les jetons ; décalage de N-PORT et absence des ETF canadiens ; risque d'apparaître décoratif si les preuves restent minces. |
| Preuve de valeur à produire | Tableau de robustesse ESG comparé à une simple liste d'exclusions fournie par l'utilisateur ; taux de succès des attaques avec et sans quarantaine (E5) ; comptes de couverture par actif. |

### Comparaison des directions

| Direction | Fonctions servies | Base de preuves | Principal risque | Coût relatif | Critères du jury plutôt renforcés | Compatible avec |
|---|---|---|---|---|---|---|
| A | Calcul, vérification, traçabilité | La plus solide (calcul délégué, méthodes de portefeuille, services documentés) | Paraître peu agentique | Faible | Données, explicabilité, AWS | B, C, D (socle) |
| B | Compréhension de la demande, choix des calculs | Moyenne (OptiGuide hors finance, guides praticiens) | Routage erroné, boucles | Moyen | Intelligence agentique, pertinence | A, C |
| C | Profil, questions, conflits, compréhension | Moyenne hors finance, faible en finance | Complexité, preuve sur petit échantillon | Moyen | Intelligence agentique, explicabilité, UX, valeur métier | A, B |
| D | Preuves externes, ESG, transparence des ETF | Faible pour l'ESG gratuit ; solide sur les risques d'injection | Licences, coût, injection | Élevé | Innovation, données | A |

La direction A est un socle plutôt qu'une option exclusive. La vraie décision porte sur l'endroit où investir l'effort agentique : le routage des formulations (B), la conversation (C) ou les documents (D). Les preuves examinées ne permettent pas de trancher a priori ; la section 7 propose l'expérience qui le permet.

## 7. Expériences discriminantes

Huit expériences sont proposées [Inf]. Pour chacune, les critères de succès sont fixés avant les résultats ; les seuils numériques indiqués sont des propositions que l'équipe doit confirmer et consigner par écrit avant de lancer le test, pour éviter de les ajuster après coup. Avec quelques dizaines de cas, il faut rapporter des comptes exacts et des intervalles de Wilson, et ne pas interpréter de petites différences ([Kapoor et al.](https://arxiv.org/abs/2407.01502) ; [tau-bench](https://arxiv.org/abs/2406.12045)). Aucune n'implique de dépense dans le cadre de cette mission ; E7 suppose un accès au compte AWS de l'équipe et une décision de l'équipe.

### E1. Tranche verticale à trois bras (l'expérience la plus informative)

| Champ | Contenu |
|---|---|
| Question | Où l'effort agentique apporte-t-il une valeur mesurable par rapport à un pipeline fixe : dans le choix de la formulation (B) ou dans la conversation (C) ? |
| Protocole | Construire une fois le socle déterministe, commun à toutes les directions. Constituer 30 à 40 cas : les 3 personas croisés avec 4 types de demande (phrase vague, question précise, dossier complet, dossier contradictoire), plus une dizaine de cas difficiles (donnée manquante, contraintes incompatibles, volatilité extrême) et une dizaine de cas mis de côté, jamais utilisés pour régler les prompts. Faire tourner sur les mêmes cas, le même instantané de données et le même modèle : **A** (extraction par le LLM vers le schéma, table de correspondance fixe vers les formulations, explication par gabarit) ; **B** (agent qui choisit formulation et « et si » dans la bibliothèque fermée) ; **C** (élicitation adaptative puis pipeline fixe). Optionnel : **A0**, gabarit sans LLM, pour mesurer le plancher. |
| Mesures | Unité de décision correctement identifiée ; contradictions scriptées détectées (rappel) ; contraintes du profil respectées (contrôle déterministe) ; taux de fidélité numérique ; nombre de questions posées ; même classe de réponse et même allocation sur 3 essais (pass^3) ; jetons, coût, latence ; échecs étiquetés selon MAST. |
| Critères de succès fixés avant | B est retenue seulement si elle identifie correctement l'unité de décision sur au moins autant de cas que A, réussit au moins un type de demande que A échoue systématiquement, et ne dégrade ni la fidélité numérique ni le respect des contraintes. C est retenue seulement si elle détecte toutes les contradictions que A détecte, plus au moins la moitié de celles que A manque, avec une médiane d'au plus 3 questions et zéro question sur les dossiers complets. Un bras plus coûteux n'est retenu que si son avantage dépasse l'incertitude des intervalles. Si A0 égale A sur tous les critères, la valeur du LLM doit être cherchée ailleurs et dite. |
| Décision éclairée | Choix entre B et C (ou leur combinaison) comme lieu de l'effort agentique ; justification chiffrée de la sophistication devant le jury. |
| Pourquoi c'est la plus informative | Elle teste sur les mêmes cas l'hypothèse sur laquelle repose chaque direction, sur le critère le plus disputé (intelligence agentique et explicabilité, 20 %), en réutilisant le socle déjà nécessaire. Le cas de Robert y concentre conflit, risque et question « qu'est-ce qui changerait la conclusion ». |

### E2. Choix de l'allocateur

| Champ | Contenu |
|---|---|
| Question | Quel allocateur, ou quel petit ensemble, exposer par défaut pour chaque persona ? |
| Protocole | Walk-forward mensuel avec fenêtres glissantes d'un à deux ans pour la covariance ; candidats : 1/N, inverse volatilité, variance minimale avec Ledoit-Wolf, ERC, HRP, chacun sous les contraintes du persona (par exemple plafond crypto) ; coûts explicites et modifiables ; 1 000 portefeuilles aléatoires sous les mêmes contraintes comme distribution nulle ; bootstrap par blocs de la covariance pour obtenir des intervalles de poids. |
| Mesures | Volatilité, CVaR, drawdown maximal, rotation, respect des contraintes, stabilité des poids, Sharpe avec son seuil de chance, PBO. |
| Critères de succès fixés avant | Le choix se fait sur la stabilité des poids, le contrôle du risque et l'adéquation au profil, jamais sur le seul Sharpe. Si les écarts de Sharpe restent sous le seuil de chance correspondant au nombre de configurations essayées, les méthodes sont déclarées indiscernables sur ce critère et aucune supériorité n'est revendiquée. HRP n'est conservé que s'il apporte une stabilité ou un contrôle du risque supérieur à la variance minimale sous contraintes. |
| Décision éclairée | Allocateur par défaut et références affichées ; formulation du message sur la performance. |

### E3. Sensibilité à l'alignement des données

| Champ | Contenu |
|---|---|
| Question | Les choix d'alignement (calendriers, crypto, change, rendement total) changent-ils la recommandation ? |
| Protocole | Comparer quotidien avec report des rendements du week-end, hebdomadaire et covariances décalées ; prix contre rendement total ; USD contre CAD ; vérifier le double comptage des dividendes sur un fractionnement et un dividende connus. |
| Mesures | Écart des matrices de corrélation ; écart des poids par actif et par classe ; part du risque attribuée au change. |
| Critères de succès fixés avant | Si un choix d'alignement déplace un poids de plus d'un seuil fixé à l'avance (par exemple 5 points de pourcentage sur une classe d'actifs), ce choix devient une hypothèse affichée dans l'explication et une carte modifiable. Toute incohérence entre rendement total reconstruit et clôture ajustée au-delà de l'écart toléré bloque l'usage de la série jusqu'à explication. |
| Décision éclairée | Grille de décision par défaut, conventions documentées dans la fiche descriptive du jeu de données. |

### E4. Injection d'erreurs et contrat de fidélité

| Champ | Contenu |
|---|---|
| Question | La couche de vérification détecte-t-elle ce qu'elle prétend détecter, et l'ancrage contextuel de Guardrails ajoute-t-il quelque chose au contrôle déterministe ? |
| Protocole | Corrompre une valeur du registre ou une ligne de prix ; demander au rédacteur d'« arrondir largement » ou insérer un nombre faux dans un brouillon ; retirer une série nécessaire ; soumettre chaque cas au contrôle déterministe et, séparément, à l'ancrage contextuel. |
| Mesures | Taux de détection par type d'erreur et par mécanisme ; taux d'abstention correcte quand une donnée manque ; faux positifs. |
| Critères de succès fixés avant | Le contrôle déterministe des nombres doit détecter 100 % des erreurs numériques injectées : chaque manque est un bogue à corriger, pas un résultat. Une donnée manquante doit produire une abstention explicite dans 100 % des cas. L'ancrage contextuel n'est conservé dans l'architecture que s'il détecte des erreurs qualitatives que le contrôle déterministe ne peut pas voir ; sinon il est retiré pour ne pas être décoratif. |
| Décision éclairée | Composition de l'étape « vérifier avant d'afficher » ; maintien ou retrait de Guardrails. |

### E5. Injection par documents (seulement si la direction D est explorée)

| Champ | Contenu |
|---|---|
| Question | Une instruction ou un chiffre fabriqué cachés dans un document peuvent-ils modifier la recommandation ? |
| Protocole | 10 à 20 instructions et chiffres fabriqués insérés dans des actualités et rapports ESG synthétiques ; mesures avec et sans extraction en quarantaine, marquage des données et détecteur de texte impératif ; promptfoo ou inspect_ai pour héberger la suite. |
| Mesures | Taux de succès d'attaque (récit modifié dans le sens de l'attaquant, chiffre fabriqué utilisé) ; utilité sans attaque. |
| Critères de succès fixés avant | Avec quarantaine, aucun chiffre fabriqué n'atteint la sortie. Tout récit modifié est compté et montré au jury comme limite résiduelle, puisque les attaques texte-à-texte ne sont pas couvertes par les défenses connues. |
| Décision éclairée | Faisabilité de la direction D ; périmètre des documents admis. |

### E6. Pilote de compréhension

| Champ | Contenu |
|---|---|
| Question | La restitution proposée fait-elle mieux comprendre et choisir qu'une explication textuelle ? |
| Protocole | 8 à 15 participants, environ 20 minutes chacun, plan intra-sujet contrebalancé ; covariables : item unique du Berlin Numeracy Test et « Big Three » ; deux variantes (texte seul ; dotplot, phrase contrastive et condition de bascule) ; un essai avec une recommandation volontairement fausse (mauvais horizon appliqué) ; une tâche « corriger l'horizon sans recommencer ». |
| Mesures | 6 à 8 items de connaissance générés à partir des sorties du système ; erreur de calibration (« x sur 20 » estimé contre valeur du modèle) ; reformulation par le participant notée de 0 à 2 par deux évaluateurs ignorant la variante ; SURE ou échelle à 10 items, non modifiées sauf le nom de la décision ; acceptation de la recommandation fausse ; temps et réussite de la correction. |
| Critères de succès fixés avant | La variante enrichie est retenue si elle améliore la connaissance et réduit l'erreur de calibration chez la majorité des participants, sans augmenter l'acceptation de la recommandation fausse. Les résultats sont présentés comme descriptifs, avec intervalles par bootstrap et graphiques individuels, sans prétention inférentielle ; le biais lié à des participants issus de l'équipe ou du datathon est déclaré. |
| Décision éclairée | Restitution montrée au jury ; dose de friction volontaire. |

### E7. Vérifications AWS préalables, sans construction

| Champ | Contenu |
|---|---|
| Question | L'énoncé de résidence, le modèle et le coût prévus tiennent-ils sur le compte réel ? |
| Protocole | Vérifier visuellement la page de prix de Bedrock pour Haiku 5.5 et Sonnet 5.5 ; appeler `GetInferenceProfile` pour le profil `ca.` depuis ca-central-1 ; consulter Service Quotas ; demander si les crédits couvrent les modèles facturés via Marketplace et si le compte est fourni par les organisateurs ; vérifier l'ancrage Classic en français avec le profil `ca.` ; créer d'abord un budget avec alertes. |
| Mesures | Prix affichés ; destinations du profil ; quotas ; règles de facturation applicables. |
| Critères de succès fixés avant | Décision binaire. Si les destinations du profil `ca.` sont limitées au Canada et que le prix est confirmé, l'énoncé de résidence est maintenu ; sinon, il est corrigé avant toute démonstration, et le choix de modèle est revu en disant explicitement où les données transitent. |
| Décision éclairée | Modèle, région, formulation de la résidence, budget. |

### E8. Sensibilité de la probabilité d'objectif

| Champ | Contenu |
|---|---|
| Question | La probabilité d'atteindre l'objectif de Robert ou de Mateo est-elle assez stable pour guider la décision ? |
| Protocole | Calculer la probabilité par bootstrap sous trois hypothèses de rendement (historique, contractée vers un prior déclaré, stressée), avec la formule fermée comme référence. |
| Mesures | Intervalle de probabilité par portefeuille candidat. |
| Critères de succès fixés avant | Si l'intervalle d'un candidat chevauche le seuil de décision (par exemple la probabilité minimale acceptée par le persona), la probabilité est présentée comme incertaine et la décision s'appuie plutôt sur le regret ou la robustesse entre scénarios. |
| Décision éclairée | Place de la probabilité d'objectif dans l'interface : métrique centrale ou indicateur secondaire. |

### Ordre proposé

E7 et E3 d'abord, car peu coûteuses et bloquantes ; puis E2, qui fixe le socle ; puis E1, décisive pour choisir la direction, avec E4 en parallèle ; E6 en fin de construction ; E5 seulement si la direction D est explorée ; E8 dès que la probabilité d'objectif est implémentée.

## 8. Lacunes et objections

### 8.1 Ce que l'existant ne résout pas

Aucun système ouvert ne combine contexte canadien, multi-actifs, profil, calcul déterministe et explication vérifiable ; l'assemblage reste à faire et à prouver. Les preuves sur les LLM extracteurs de profils financiers, sur l'élicitation par valeur de l'information en finance et sur les injections dans des documents financiers manquent. Aucune source ESG gratuite, redistribuable et vérifiée n'a été trouvée pour l'univers du jeu de départ. Aucun instrument de qualité de décision n'est validé pour l'investissement. Aucune méthode ne transforme cinq ans d'historique en connaissance fiable sur un horizon de 15 ans comme celui d'Amira : tout résultat à long horizon est un scénario, pas une validation. Les fichiers de positions des ETF canadiens ne figurent pas dans N-PORT et leurs conditions n'ont pas été lues.

### 8.2 Hypothèses fragiles

Les cinq années disponibles contiennent probablement un ou deux cycles complets de la crypto : tout résultat de walk-forward est propre à ce régime [Inf]. Une CVaR à 95 % sur données quotidiennes repose sur environ 63 pires jours, regroupés en deux ou trois épisodes [Inf]. La covariance de la crypto est instable et à queues épaisses. Le taux de change de la Banque du Canada est une moyenne de journée appliquée à des clôtures de 16 h. L'univers de 31 actifs est survivant. Les séries macro sont révisées. La règle du minimum suppose que tolérance et capacité sont mesurées correctement, alors que les questionnaires réels sont rarement validés. La disponibilité de Claude Haiku 5.5 avec un profil `ca.`, ses prix et la carte des services AgentCore au Canada évoluent vite et sont à revérifier le jour même [Inf]. Le passage de ces preuves (souvent en santé, en transport ou en laboratoire) à des investisseurs réels n'est démontré nulle part.

### 8.3 Objections qui pourraient invalider la direction qui ressort des carnets

La direction qui ressort le plus souvent des carnets est un socle A avec un effort agentique placé en C ou en B. Dix objections peuvent l'affaiblir.

| Objection | Pourquoi elle est sérieuse | Comment la tester ou y répondre |
|---|---|---|
| « Ce n'est pas assez agentique » | L'intelligence agentique pèse avec l'explicabilité 20 % de la note ; un pipeline déterministe ressemble à un robo-conseiller classique | E1 : montrer où l'agent décide (questions, formulation) et ce que cela change ; si E1 ne montre aucun gain, l'objection tient et doit être assumée |
| « Le plancher sans LLM fait aussi bien » | Si A0 égale A, pourquoi un LLM ? | Mesurer A0 dans E1 ; chercher la valeur dans les demandes vagues et contradictoires ; le dire honnêtement sinon |
| « 40 cas ne prouvent rien » | Les petites différences ne sont pas significatives | Anthropic a démarré avec environ 20 cas quand les effets étaient grands [A] ; viser des écarts nets, rapporter des intervalles, ne rien revendiquer d'autre |
| « Les gabarits rigidifient le langage et perdent le novice » | Les contraintes de format dégradent le raisonnement (Tam et al.) | Raisonnement libre puis assemblage contraint ; vérifier dans E6 |
| « Un modèle de classe Haiku est trop faible en français » | Qualité non mesurée | E1 et E7 ; repli explicite sur Sonnet 5.5 en assumant le routage américain |
| « Les règles de l'ACVM ne s'appliquent pas à une simulation » | AlphaForge n'est pas un inscrit | Présenter l'alignement comme une structure de qualité, sans revendiquer de conformité |
| « Cinq ans de données contredisent l'horizon de 15 ans d'Amira » | Aucune validation possible | Scénarios et fourchettes étiquetés comme tels ; jamais de performance à long terme |
| « La traçabilité AWS est invisible pour un jury pressé » | Une contribution réelle mais non vue ne compte pas | Afficher l'ARN d'exécution et le manifeste à côté de chaque recommandation ; tester l'enchaînement de clics en répétition |
| « La règle du minimum rend Robert trop prudent et nie sa volonté » | Risque d'aversion pour l'algorithme | Laisser Robert modifier une hypothèse (Dietvorst), montrer l'effet, proposer une poche spéculative plafonnée et documenter la divergence |
| « L'expérience simulée pousse Robert vers le risque » | Effet documenté (Bradbury, Kaufmann) | Mesurer la calibration plutôt que l'appétit pour le risque ; forçage cognitif avant l'affichage |

### 8.4 Limites de cette recherche documentaire

Ce dossier repose sur une recherche documentaire : aucun code n'a été exécuté, aucun compte AWS créé, aucune API AWS appelée, aucun test utilisateur mené. L'API GitHub a renvoyé des erreurs 403 à plusieurs chercheurs : dates de dernier commit, étoiles, publications et fils de tickets n'ont souvent pas pu être lus (les dates viennent de PyPI, de npm ou de clones git ; pour TradingAgents, seuls les titres et débuts de tickets ont été lus). Plusieurs pages étaient inaccessibles : la norme GSN (page vide), la documentation temps réel de FRED et la page d'accueil d'ALFRED (délai dépassé), la documentation Valet de la Banque du Canada (rendue en JavaScript), les conditions de Stooq (délai), de Tiingo (JavaScript), d'Alpha Vantage (clauses non extraites) et de Nasdaq Data Link (erreur 404), la page de conditions ESG de MSCI, le PDF primaire de l'avis 81-334, l'article de Platanakis et al. 2018 (« Access Denied »), le résumé complet de Chopra et Ziemba (tronqué), celui de Croushore et Stark, le règlement Reg BI (eCFR bloqué), l'article de Lo et Ross dans la Harvard Data Science Review (résolveur DOI en échec), un article HAL sur le robo-conseil (protection anti-robot), PubMed et PMC (captcha). Les prix de Bedrock ont été lus dans des fichiers JSON plutôt qu'à l'écran, et le prix de Step Functions au Canada n'a pas été résolu. De nombreux textes ont été lus par des outils d'extraction automatique, signalés comme tels. Plusieurs références sont bibliographiques seulement (Ledoit-Wolf, Jagannathan-Ma, Black-Litterman, Maillard et al., López de Prado, Rockafellar-Uryasev, Deflated Sharpe Ratio, W3C PROV, Datasheets for Datasets, Shafer) et sont marquées [NV].

## 9. Registre des sources

Toutes les sources ont été consultées le **2026-11-14** par l'équipe de recherche. Le niveau d'examen indiqué est le niveau réel : {repéré}, {résumé lu}, {page lue}, {texte analysé}, {code inspecté}, {licence lue}, avec la mention (extraction auto) quand un outil automatique a fourni le texte. « Inaccessible » signifie que la page n'a pas pu être lue. Les licences de code, de données et de modèles sont distinguées dans la colonne des remarques.

### 9.1 Systèmes agentiques financiers, conseillers LLM et critiques

| Ressource | Auteurs ou organisation | Date, version, commit | Lien | Nature | Niveau d'examen | Remarques |
|---|---|---|---|---|---|---|
| TradingAgents (article) | Xiao, Sun, Luo, Wang | arXiv 2412.20138 v7, 2025-06-03 | [lien](https://arxiv.org/html/2412.20138) | Prépublication | {texte analysé} | Texte CC BY 4.0 ; aucun lieu évalué trouvé |
| TradingAgents (dépôt) | Tauric Research | v0.7.1 (2026-10-27), HEAD `9fa1196` (2026-11-04) | [lien](https://github.com/TauricResearch/TradingAgents) | Dépôt | {code inspecté} ; tickets : titres et débuts | Code Apache-2.0 ; données des fournisseurs sous leurs propres conditions |
| Trading-R1 | Même groupe | arXiv 2509.11420 | [lien](https://arxiv.org/abs/2509.11420) | Prépublication | {résumé lu} | Terminal en accès anticipé |
| FinRobot (dépôt) | AI4Finance Foundation | HEAD `63e1884` (2026-10-24) ; v1.0.0, desktop-v0.1.0 | [lien](https://github.com/AI4Finance-Foundation/FinRobot) | Dépôt | {code inspecté} partiel | Code Apache-2.0 ; compétences dérivées de contenus MIT d'Anthropic |
| FinRobot, livre blanc | Hongyang Yang et al. | arXiv 2405.14767 v2, 2024-05-27 | [lien](https://arxiv.org/html/2405.14767) | Prépublication | {texte analysé} | Aucun banc quantitatif |
| FinRobot, analyse d'actions | Zhou, Wang, Wu, Yang | arXiv 2411.08804, 2024-11-13 | [lien](https://arxiv.org/html/2411.08804) | Atelier ICAIF 2024 | {texte analysé} | Évaluation par panel d'analystes |
| AlphaAgents | Zhao, Lyu, Jones, Garber, Pasquali, Mehta et al. (BlackRock) | arXiv 2508.11152 v1, 2025-08-15 | [lien](https://arxiv.org/html/2508.11152) | Prépublication | {texte analysé} | Aucun code trouvé |
| MarketSenseAI 2.0 | Fatouros, Metaxas, Soldatos, Karathanassis | arXiv 2502.00415 v2, 2025-10-03 | [lien](https://arxiv.org/html/2502.00415) | Prépublication (en évaluation) | {texte analysé} partiel | Aucun code |
| FinMem, FinCon, FinAgent | Yu et al. ; Zhang et al. | arXiv 2311.13743 ; 2407.06567 v3 ; 2402.18485 v3 | [FinMem](https://arxiv.org/abs/2311.13743), [FinCon](https://arxiv.org/abs/2407.06567), [FinAgent](https://arxiv.org/abs/2402.18485) | Prépublications | {résumé lu} | Lieux d'évaluation non vérifiés |
| ai-hedge-fund | Virat Singh | HEAD `5c553b5` (2026-11-09), version 2.7.2 | [lien](https://github.com/virattt/ai-hedge-fund) | Dépôt | {code inspecté} structure et coûts | Code MIT ; données via API payante |
| OpenBB | OpenBB Inc. | Branche develop | [lien](https://github.com/OpenBB-finance/OpenBB/blob/develop/LICENSE) | Dépôt | {licence lue} | Code Apache-2.0 ; agents non inspectés |
| FinGPT | AI4Finance Foundation | README | [lien](https://github.com/AI4Finance-Foundation/FinGPT/blob/master/README.md) | Dépôt | {licence lue}, README lu | Code MIT ; licences des modèles de base non vérifiées |
| Agentic Robo-Advisor | luhao09, E. O. Tijani | Non daté | [lien](https://app.readytensor.ai/publications/agentic-robo-advisor-intelligent-wealth-platform-gf0vqfNHC5RA) | Projet de praticiens ou d'étudiants | {page lue} ; code non inspecté | Licence non indiquée |
| Using LLMs for Financial Advice | Fieberg, Hornuf, Meiler, Streich | CESifo WP 11666, 2025-01-30 | [lien](https://www.ifo.de/DocDL/cesifo1_wp11666.pdf) | Document de travail | {texte analysé} partiel (extraction auto) | Environ 48 % du texte lu |
| Are Generative AI Agents Effective Personalized Financial Advisors? | Takayanagi et al. | arXiv 2504.05862 v2 | [lien](https://arxiv.org/abs/2504.05862) | Prépublication | {résumé lu} | |
| Investor risk profiles of LLMs | Cho, Bae, Kim | arXiv 2603.09303 v2, 2026-03-10 | [lien](https://arxiv.org/abs/2603.09303) | Prépublication | {résumé lu} | |
| Auditing Asset-Specific Preferences (Bitcoin) | Wu | arXiv 2606.02528 v3, 2026-07-18 | [lien](https://arxiv.org/abs/2606.02528) | Prépublication | {résumé lu} | |
| Can ChatGPT Plan Your Retirement? | Lo, Ross | HDSR, 2024-08-01 | [notice](https://library.kab.ac.ug/Record/doaj-art-427a57b00f1346628c1f3165ce15a86a) | Article | Notice seulement (texte inaccessible) | Ne rien en citer |
| FINSABER | Li, Kim, Cucuringu, Ma | arXiv 2505.07078 v6, 2026-06-26 ; KDD 2026 | [article](https://arxiv.org/html/2505.07078), [code](https://github.com/waylonli/FINSABER) | Article accepté, code | {texte analysé} ; {licence lue} | Code Apache-2.0 |
| Profit Mirage | Li, Zeng, Xing, Xu et al. | arXiv 2510.07920 v1, 2025-10-09 | [lien](https://arxiv.org/html/2510.07920) | Prépublication | {texte analysé} partiel | Tableaux complets non extraits |
| StockBench | Chen, Yao, Liu, Xin et al. | arXiv 2510.02209 v2, 2026-03-02 | [lien](https://arxiv.org/html/2510.02209) | Prépublication | {texte analysé} partiel | |
| Lookahead Bias in Pretrained Language Models | Sarkar, Vafa | ICML 2025, atelier DataWorld | [lien](https://icml.cc/virtual/2025/48685) | Poster | {résumé lu} | |
| Chronologically Consistent LLMs | He, Lv, Manela, Wu | arXiv 2502.21206 v3, 2025-07-06 | [lien](https://arxiv.org/abs/2502.21206) | Prépublication | {résumé lu} | |
| Time Machine GPT | Drinkall, Rahimikia, Pierrehumbert, Zohren | NAACL Findings 2024 | [lien](https://arxiv.org/abs/2404.18543) | Article | {résumé lu} | Modèles et données publiés |
| FinanceBench | Islam, Kannappan, Kiela et al. | arXiv 2311.11944, 2023-11 | [article](https://arxiv.org/abs/2311.11944), [données](https://huggingface.co/datasets/PatronusAI/financebench) | Banc d'essai | {résumé lu} | Modèles de 2023 |
| FinBen | Xie et al. | arXiv 2402.12659 v2 | [lien](https://arxiv.org/abs/2402.12659) | Banc d'essai | {résumé lu} | |
| InvestorBench | Li, Cao, Yu et al. | arXiv 2412.18174 | [lien](https://arxiv.org/abs/2412.18174) | Banc d'essai | {résumé lu} | Écrit par le groupe de FinMem et FinCon |
| Conv-FinRe | Inconnu | arXiv 2602.16990 | [lien](https://arxiv.org/html/2602.16990v1) | Banc d'essai | {repéré} | Non lu |

### 9.2 Méthodes de portefeuille, de décision et d'évaluation

| Ressource | Auteurs ou organisation | Date | Lien | Nature | Niveau d'examen | Remarques |
|---|---|---|---|---|---|---|
| Optimal Versus Naive Diversification | DeMiguel, Garlappi, Uppal | RFS 22(5), 2009 | [lien](https://ideas.repec.org/a/oup/rfinst/v22y2009i5p1915-1953.html) | Article | {résumé lu} | |
| In Defense of Optimization | Kritzman, Page, Turkington | FAJ 66(2), 2010 | [lien](https://ideas.repec.org/a/taf/ufajxx/v66y2010i2p31-39.html) | Article | {résumé lu} | |
| It's All in the Timing | Kirby, Ostdiek | JFQA 47(2), 2012 | [lien](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/its-all-in-the-timing-simple-active-portfolio-strategies-that-outperform-naive-diversification/05D18E04B226C6E9B8441482CC92F943) | Article | {résumé lu} | Forme exacte de la pondération non relue |
| Black-Litterman et crypto | Platanakis, Urquhart | Economics Letters 177, 2019 | [lien](https://econpapers.repec.org/RePEc:eee:ecolet:v:177:y:2019:i:c:p:76-80) | Article | {résumé lu} | Période et actifs non précisés |
| Moments variables et 1/N en crypto | Inconnu | arXiv 2501.12841 v3, 2025 | [lien](https://arxiv.org/abs/2501.12841) | Prépublication | {résumé lu} | Réponse absente du résumé |
| Optimal vs naive diversification in cryptocurrencies | Platanakis, Sutcliffe, Urquhart | 2018 | [lien](https://centaur.reading.ac.uk/78105) | Article | Inaccessible (« Access Denied ») | |
| Out-of-sample performance of resampled efficiency | Scherer | JAM 7(3), 2006 | [lien](https://link.springer.com/article/10.1057/palgrave.jam.2240211) | Article | {résumé lu} | Réfutations de New Frontier Advisors {repéré} |
| Robustesse des allocations | Jain, Jain | Risks 7(3), 2019 | [lien](https://econpapers.repec.org/RePEc:gam:jrisks:v:7:y:2019:i:3:p:74-:d:245327) | Article | {résumé lu} | Données apparemment indiennes |
| Schur Complementary Allocation | Cotton | arXiv 2411.05807, 2024 | [lien](https://arxiv.org/abs/2411.05807) | Prépublication | {résumé lu} | Aucun résultat empirique dans le résumé |
| DRO de Wasserstein | Mohajerin Esfahani, Kuhn | arXiv 1505.05116 ; Math. Programming 2018 | [lien](https://arxiv.org/abs/1505.05116) | Article | {résumé lu} | Hypothèses du théorème non relues |
| Références bibliographiques non revérifiées | Michaud 1989 ; Scherer 2002 ; Ledoit-Wolf 2003 et 2004 ; Jagannathan-Ma 2003 ; Black-Litterman 1992 ; Maillard-Roncalli-Teiletche 2010 ; López de Prado 2016 ; Goldfarb-Iyengar 2003 ; Fabozzi et al. 2010 ; Rockafellar-Uryasev 2000 ; Chekhlov et al. 2005 ; Blanchet-Chen-Zhou 2022 ; Best-Grauer 1991 ; Boyd-Vandenberghe 2004 ; Harvey-Liu-Zhu 2016 | Divers | DOI donnés de mémoire par les carnets | Articles et livre | [NV] bibliographie seule | Chiffres précis à vérifier |
| Effect of errors in means, variances, covariances | Chopra, Ziemba | JPM 19(2), 1993 | [lien](https://econpapers.repec.org/RePEc:wsi:wschap:9789814417358_0021) | Article | Résumé tronqué | Ratios souvent cités non vérifiés |
| Almost Stochastic Dominance | Leshno, Levy | Management Science 48(8), 2002 | [lien](https://econpapers.repec.org/RePEc:inm:ormnsc:v:48:y:2002:i:8:p:1074-1085) | Article | {résumé lu} | |
| A New Approach to Goals-Based Wealth Management | Das, Ostrov, Radhakrishnan, Srivastav | Document de travail du 2018-05-14 | [lien](https://webpages.scu.edu/ftp/dostrov/publications/JOIM.pdf) | Document de travail | {texte analysé} | Enquête par l'employeur de deux auteurs |
| Dynamic Portfolio Allocation in GBWM | Mêmes auteurs | Document de travail du 2020-03-03 | [lien](https://webpages.scu.edu/ftp/dostrov/publications/CMS.pdf) | Document de travail | {texte analysé} | Revue de publication non confirmée |
| Portfolio Optimization with Mental Accounts | Das, Markowitz, Scheid, Statman | JFQA 45(2), 2010 | [lien](https://ideas.repec.org/a/cup/jfinqa/v45y2010i02p311-334_00.html) | Article | Condensé CFA lu | Article non lu |
| Robust Satisficing | Long, Sim, Zhou | Operations Research 71(1), 2023 | [lien](https://ideas.repec.org/a/inm/oropre/v71y2023i1p61-82.html) | Article | {résumé lu} | |
| A bird's view of info-gap decision theory | Sniedovich | Journal of Risk Finance 11(3), 2010 | [lien](https://ideas.repec.org/a/eme/jrfpps/15265941011043648.html) | Article critique | {résumé lu} | |
| Resolving Rank Reversal in TOPSIS | Shyur, Shih | Informatica 35(4), 2024 | [lien](https://informatica.vu.lt/journal/INFORMATICA/article/1356/read) | Article | {page lue} | |
| Infeasibility tutorial | Chinneck | CPAIOR 2007 | [lien](https://sce.carleton.ca/faculty/chinneck/docs/CPAIOR07InfeasibilityTutorial.pdf) | Tutoriel | {texte analysé} | |
| Restricted license (Gurobi) | Gurobi | Page de support | [lien](https://support.gurobi.com/hc/en-us/articles/29682074018833-What-does-Restricted-license-for-non-production-use-only-mean) | Documentation | {page lue} | Non commercial, taille limitée |
| Investigate linear infeasibilities | MathWorks | Documentation | [lien](https://www.mathworks.com/help/optim/ug/investigate-linear-infeasibilities.html) | Documentation | {repéré} | |
| Probability of Backtest Overfitting | Bailey, Borwein, López de Prado, Zhu | SSRN 2013, J. Computational Finance | [lien](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253) | Article | {résumé lu} | Procédure détaillée de mémoire |
| OptiGuide | Li, Mellou, Zhang, Pathuri, Menache | arXiv 2307.03875, 2023 | [article](https://arxiv.org/abs/2307.03875), [code](https://github.com/microsoft/OptiGuide), [page MSR](https://www.microsoft.com/en-us/research/publication/large-language-models-for-supply-chain-optimization/) | Prépublication, code | {résumé lu} ; {licence lue} | Code MIT |
| Survey: Optimization Modeling Meets LLMs | Xiao et al. | IJCAI 2025 | [HTML](https://arxiv.org/html/2508.10047v1), [actes](https://www.ijcai.org/proceedings/2025/1192) | Revue | {texte analysé} | |
| OptiMUS | AhmadiTeshnizi, Gao, Udell | arXiv 2402.10172, 2024 | [article](https://arxiv.org/abs/2402.10172), [code](https://github.com/teshnizi/OptiMUS) | Prépublication, code | {résumé lu} ; {licence lue} | Code MIT |
| NL4Opt Competition | Ramamonjison et al. | NeurIPS 2022 | [lien](https://arxiv.org/abs/2303.08233) | Compétition | [NV] bibliographie seule | |
| Analyse de décision (tornado, droites de bascule, régions de stratégie) | Notes de cours GWU d'après Clemen et Reilly | Non daté | [lien](https://www2.seas.gwu.edu/~dorpjr/EMSE269/Lecture%20Notes/Chapter%205.pdf) | Cours | {texte analysé} | Livre lui-même non consulté |
| Javelin Diagrams | Inconnu | Decision Analysis 1(2), 2004 | [lien](https://econpapers.repec.org/RePEc:inm:ordeca:v:1:y:2004:i:2:p:93-107) | Article | {repéré} | |

### 9.3 Bibliothèques et outils de calcul

| Ressource | Organisation | Version et date (PyPI ou npm) | Lien | Nature | Niveau d'examen | Licence du code |
|---|---|---|---|---|---|---|
| skfolio | Projet skfolio | 1.12.16, 2026-11-14 | [lien](https://github.com/skfolio/skfolio) | Bibliothèque | {code inspecté} | BSD-3 |
| Riskfolio-Lib | D. Cajas | 7.4.1, 2026-11-04 | [lien](https://github.com/dcajasn/Riskfolio-Lib) | Bibliothèque | {code inspecté} | BSD-3 |
| PyPortfolioOpt | Projet pyportfolio | 1.6.0, 2026-02-26 | [lien](https://github.com/pyportfolio/pyportfolioopt) | Bibliothèque | {code inspecté} | MIT |
| cvxpy | Projet cvxpy | 1.9.3, 2026-09-19 | [lien](https://github.com/cvxpy/cvxpy) | Bibliothèque | {code inspecté} | Apache-2.0 |
| HiGHS / highspy | ERGO-Code | 1.16.0, 2026-11-11 | [lien](https://github.com/ERGO-Code/HiGHS) | Solveur | {code inspecté} (en-tête) | MIT |
| Pyomo IIS | Projet Pyomo | Documentation 6.9.3 | [lien](https://pyomo.readthedocs.io/en/6.9.3/_modules/pyomo/contrib/iis/mis.html) | Bibliothèque | {page lue} | Non lue |
| OR-Tools | Google | 9.15, 2026-01-14 | [lien](https://github.com/google/or-tools) | Bibliothèque | {code inspecté} (docstring) | Apache-2.0 |
| arch | K. Sheppard | 9.0.0, 2026-11-11 | [lien](https://github.com/bashtage/arch) | Bibliothèque | {code inspecté} | NCSA |
| quantstats | R. Aroussi | 0.0.86, 2026-09-27 | [lien](https://github.com/ranaroussi/quantstats) | Bibliothèque | {code inspecté} | Apache-2.0 |
| EMA Workbench | TU Delft | 3.0.0, 2026-03-12 | [lien](https://github.com/quaquel/EMAworkbench) | Bibliothèque | {code inspecté} | BSD-3 |
| pymcdm | Projet pymcdm | 1.4.0, 2026-01-31 | [lien](https://github.com/kotbaton/pymcdm) | Bibliothèque | {code inspecté} | MIT |
| pymoo | Projet pymoo | 0.6.2, 2026-06-28 | [lien](https://pymoo.org) | Bibliothèque | {licence lue} | Apache-2.0 |
| cvxportfolio | Stanford cvxgrp | 1.5.1, 2025-07-06 | [lien](https://github.com/cvxgrp/cvxportfolio) | Bibliothèque | {licence lue} | GPL-3.0 |
| empyrical-reloaded | S. Jansen | 0.7.2, 2026-11-02 | [lien](https://github.com/stefan-jansen/empyrical-reloaded) | Bibliothèque | {licence lue} | Apache-2.0 |
| vectorbt | O. Polakow | 1.2.1, 2026-11-11 | [lien](https://github.com/polakowo/vectorbt) | Bibliothèque | {licence lue} | Apache 2.0 avec Commons Clause |
| bt | P. Morissette | 1.4.1, 2026-10-10 | [lien](https://github.com/pmorissette/bt) | Bibliothèque | {licence lue} | MIT |
| scipy | Projet SciPy | 1.18.1, 2026-08-21 | [lien](https://github.com/scipy/scipy) | Bibliothèque | {licence lue} | BSD |
| pyDecision | V. Pereira | 5.1.8, 2026-10-12 | [lien](https://github.com/Valdecy/pyDecision) | Bibliothèque | {licence lue} | GPL-3.0-or-later |
| pypbo | esvhd | Absent de PyPI | [lien](https://github.com/esvhd/pypbo) | Bibliothèque | {licence lue} | AGPL-3.0 |
| DiCE | interpretml | Aucune publication GitHub | [lien](https://github.com/interpretml/DiCE) | Bibliothèque | README et licence lus | MIT |
| marimo | marimo-team | Non relevée | [lien](https://github.com/marimo-team/marimo) | Notebook réactif | README lu | Apache-2.0 |
| ggdist | M. Kay | Citation de la version 3.3.3 (2025) | [lien](https://github.com/mjskay/ggdist) | Bibliothèque R | README et licence lus | GPL-3.0 |

### 9.4 Profilage, élicitation et réglementation

| Ressource | Auteurs ou organisation | Date | Lien | Nature | Niveau d'examen | Remarques |
|---|---|---|---|---|---|---|
| Investor Risk Profiling: An Overview | J. Klement (CFA Institute Research Foundation) | Avril 2015 | [page](https://rpc.cfainstitute.org/research/foundation/2015/investor-risk-profiling-an-overview), [PDF](https://rpc.cfainstitute.org/-/media/documents/article/rf-brief/rfbr-v1-n1-1-pdf.pdf) | Synthèse de praticien | {texte analysé} (extraction auto) | Non évaluée par les pairs |
| Current Practices for Risk Profiling in Canada | Brayman, Finke, Bessner, Grable, Griffin, Clement (OSC IAP) | 2015-10-28, révisé 2015-11-13 | [lien](https://www.osc.ca/sites/default/files/2021-02/iap_20151112_risk-profiling-report.pdf) | Rapport commandé | {texte analysé} partiel (extraction auto) | Conflit d'intérêts signalé |
| GN-3400-21-004 | OCRI (CIRO) | En vigueur 2021-12-31 | [lien](https://www.ciro.ca/news-room/publications/know-your-client-and-suitability-determination-retail-clients) | Lignes directrices | {texte analysé} (extraction auto) | |
| 31-103CP, articles 13.2 et 13.3 | ACVM | Consolidée au 2021-03-01 | [lien](https://fcnb.ca/sites/default/files/2022-01/31-103CP-CONS-2021-03-01-E.pdf) | Instruction complémentaire | {texte analysé} partiel (extraction auto) | Règle 31-103 elle-même non consultée |
| FAQ des réformes axées sur le client | ACVM, OCRI, ACFM | Mise à jour 2023-12-06 | [miroir](https://regalert.today/document/client-focused-reforms-frequently-asked-questions-50353f18-7f39-403a-86ec-d295cea16d3d/text) | FAQ | {texte analysé} partiel | Source primaire non consultée |
| Avis 31-368 | ACVM, OCRI | 2025-12-10 | [lien](https://www.asc.ca/-/media/ASC-Documents-part-1/Regulatory-Instruments/2025/12/6255537-CSA-CIRO-Notice-31-368-Client-Focused-Reforms.pdf) | Avis du personnel | {texte analysé} partiel (extraction auto) | 100 000 caractères sur 108 000 |
| Cadence de mise à jour KYC | Morningstar Canada | Non daté | [lien](https://morningstar.ca/ca/news/209025/client-focused-reforms-part-1-kyc.aspx) | Article | {repéré} | Recoupement du 12 et 36 mois |
| Lignes directrices MiFID II sur la convenance | ESMA | ESMA35-43-3172, 2022-09-23 | [lien](https://prod.finanssivalvonta.fi/globalassets/en/publications/supervision-releases/2023/esma35-43-3172_guidelines_on_certain_aspects_of_the_mifid_ii_suitability_requirements.pdf) | Lignes directrices | {texte analysé} | |
| Déclaration ESMA sur la durabilité | ESMA | Mai 2026 | [lien](https://www.esma.europa.eu/sites/default/files/2026-05/ESMA35-915049491-6291_Statement_on_the_CSA_on_MiFID_II_sustainability_aspects.pdf) | Déclaration | {repéré} | |
| Règle 2111 | FINRA | Dernière modification 2020-06-30 | [lien](https://www.finra.org/rules-guidance/rulebooks/finra-rules/2111) | Règle | {texte analysé} | |
| Assessing suitability (FSA 2011) | Rapport secondaire | 2011 | [lien](https://thehedgefundjournal.com/assessing-suitability/) | Article secondaire | Article lu | Source primaire non consultée |
| Reg BI | SEC | | eCFR | Règlement | Inaccessible (robots bloqués) | Définition du profil non vérifiée |
| Grable-Lytton, rétrospective de 15 ans | Kuzniak, Rabbani, Heo, Ruiz-Menjivar, Grable | Financial Services Review 24(2), 2015 | [lien](https://openjournals.libs.uga.edu/fsr/article/view/3240) | Article | {résumé lu} | Article CC BY-NC 4.0 ; licence des items non claire |
| Risk preference shares the psychometric structure | Frey, Pedroni, Mata, Rieskamp, Hertwig | Science Advances, 2017 | [lien](https://pmc.ncbi.nlm.nih.gov/articles/PMC5627985) | Article | {texte analysé} (extraction auto) | Échantillon jeune, non investisseur |
| Multiple price list methods | Csermely, Rabas | J. Risk and Uncertainty 53, 2016 | [lien](https://research.wu.ac.at/en/publications/how-to-reveal-peoples-preferences-comparing-time-consistency-and--5/) | Article | {résumé lu} | PDF indiqué CC BY |
| DOSPERT | Blais, Weber (Columbia) | Version à 30 items, 2006 | [lien](https://sites.google.com/decisionsciences.columbia.edu/dospert/home) | Instrument | {page lue} | Usage libre avec citation |
| FinaMetrica (rachat par Morningstar) | Morningstar, PlanPlus Global | Date absente de la page | [lien](https://www.finextra.com/pressarticle/81704/morningstar-to-acquire-software-provider-planplus-global) | Communiqué | {page lue} | Propriétaire |
| Robo-advisor questionnaires (Tertilt et Scholz) | Condensé CFA Digest 49(1) | 2019-01-03 | [lien](https://rpc.cfainstitute.org/research/cfa-digest/2019/01/dig-v49-n1-1) | Condensé | Condensé lu | Article original non lu ; incohérence dans le condensé |
| Do Large Swings in Equity Values Change Risk Tolerance? | Guillemette, Finke | J. Financial Planning, juin 2014 | [lien](https://www.financialplanningassociation.org/sites/default/files/2020-05/14%20Do%20Large%20Swings%20in%20Equity%20Values%20Change%20Risk%20Tolerance.pdf) | Article | {texte analysé} (extraction auto) | |
| Improving Investment Decisions with Simulated Experience | Bradbury, Hens, Zeisberger | Review of Finance 19(3), 2015 | [PDF](https://core.ac.uk/download/85223761.pdf), [RePEc](https://ideas.repec.org/a/oup/revfin/v19y2015i3p1019-1052..html) | Article | {texte analysé} | |
| Choosing Outcomes versus Choosing Products | Goldstein, Johnson, Sharpe | J. Consumer Research 35(3), 2008 | [PDF](https://web.stanford.edu/~wfsharpe/retecon/GJSJCR08.pdf), [RePEc](https://ideas.repec.org/a/oup/jconrs/v35y2008i3p440-456.html) | Article | {texte analysé} | |
| Adaptive Utility Elicitation | Chajewska, Koller, Parr | AAAI 2000 | [lien](https://faculty.cc.gatech.edu/~isbell/reading/papers/Chajewska-AAAI00.pdf) | Article | {texte analysé} | |
| Minimax regret elicitation | Boutilier, Patrascu, Poupart, Schuurmans | Artificial Intelligence, 2006 | [lien](https://www.cs.toronto.edu/~cebly/Papers/BPPS-aij06-abs.html) | Article | {résumé lu} | |
| GATE | Li, Tamkin, Goodman, Andreas | arXiv 2310.11589 v1, 2023-10-17 | [article](https://arxiv.org/abs/2310.11589), [code](https://github.com/alextamkin/generative-elicitation), [préenregistrement](https://osf.io/5v6nd/) | Prépublication | {texte analysé} | Licence du code non vérifiée |
| OPEN | Handa, Gal, Pavlick, Goodman, Andreas, Tamkin, Li | arXiv 2403.05534 v1, 2024-03-08 | [lien](https://arxiv.org/abs/2403.05534) | Prépublication | {texte analysé} | Aucun code trouvé |
| STaR-GATE | Andukuri, Fränken, Gerstenberg, Goodman | arXiv 2403.19154 v3, 2024-08-07 | [lien](https://arxiv.org/abs/2403.19154) | Prépublication | {résumé lu} | Utilisateurs simulés |
| Modeling Future Conversation Turns | Zhang, Knox, Choi | arXiv 2410.13788 v2, 2025-03-18 | [lien](https://arxiv.org/abs/2410.13788v2) | Prépublication | {résumé lu} | |
| CLAMBER | Zhang et al. | arXiv 2405.12063 v2 ; ACL 2024 | [article](https://arxiv.org/html/2405.12063v2), [données](https://github.com/zt991211/CLAMBER) | Article, données | {texte analysé} (extraction auto) | Licence des données non indiquée |
| One Size Fits None | Ross, Lo | arXiv 2604.23837 v1, 2026-04-26 | [lien](https://arxiv.org/abs/2604.23837) | Prépublication | {texte analysé} (extraction auto) | Aucun code |
| How good are LLMs in risk profiling? | Hens, Nordlie | Finance Research Letters, 2025 | [lien](https://df.uzh.ch/en/research/commissioned--research/2025_llm-in-risk-profiling.html) | Article | Page d'étude lue | Article non lu |

### 9.5 Restitution, explication et mesure

| Ressource | Auteurs ou organisation | Date | Lien | Nature | Niveau d'examen | Remarques |
|---|---|---|---|---|---|---|
| Decision aids (Cochrane CD001431.pub6) | Stacey, Lewis, Smith et al. | 2024-01-29 | [lien](https://portal.findresearcher.sdu.dk/da/publications/decision-aids-for-people-facing-health-treatment-or-screening-dec/) | Revue systématique | {résumé lu} | PubMed bloqué (captcha) ; version 2017 : [lien](https://cccrg.cochrane.org/news/updated-review-decision-aids-people-facing-health-treatment-or-screening-decisions) |
| Minimum standards for patient decision aids (IPDAS) | Joseph-Williams et al. | MDM 34(6), 2014 | [lien](https://eprints.ncl.ac.uk/208229) | Article | {résumé lu} | Formulation des items non relevée |
| Ottawa Decision Support Framework | OHRI | Page modifiée 2022-10-20 | [lien](https://decisionaid.ohri.ca/odsf.html) | Cadre | {page lue} | |
| Decisional Conflict Scale et manuel | A. M. O'Connor (OHRI) | 1993, révisée 2005 ; manuel 2010 | [page](https://decisionaid.ohri.ca/eval_dcs.html), [manuel](https://decisionaid.ohri.ca/docs/develop/User_Manuals/UM_decisional_conflict.pdf) | Instrument | {texte analysé} | Conditions d'usage : citer, sans profit, sans modification |
| DCS Use over 20 Years | Garvelink et al. | MDM 39(4), 2019 | [lien](https://econpapers.repec.org/RePEc:sae:medema:v:39:y:2019:i:4:p:301-314) | Revue | {repéré} | |
| Clarifying values (méta-analyse) | Witteman, Ndjaboue, Vaisson et al. | MDM 41(7), 2021 | [lien](https://eprints.whiterose.ac.uk/178930/1/Clarifying%20Values%20An%20Updated%20and%20Expanded%20Systematic%20Review%20and%20Meta-Analysis.pdf) | Revue systématique | {texte analysé} | |
| Option Grid (licence EBSCO) | EBSCO Health, Dartmouth | Avril 2017 | [lien](https://about.ebsco.com/news-center/press-releases/ebsco-health-dartmouth-and-option-gridtm-collaborative-founders-join) | Communiqué | {page lue} | Conditions d'accès non confirmées |
| Quantile dotplots (transit) | Fernandes, Walls, Munson, Hullman, Kay | CHI 2018 | [page](https://mucollective.northwestern.edu/project/uncertainty-bus), [PDF](https://mucollective.northwestern.edu/files/2018-UncertainBusDecisions-CHI.pdf) | Article | {résumé lu} | |
| When(ish) is My Bus? | Kay, Kola, Hullman, Munson | CHI 2016 | [lien](https://mucollective.northwestern.edu/project/when-ish-is-my-bus) | Article | {résumé lu} | |
| Hypothetical Outcome Plots | Hullman, Resnick, Adar | PLOS ONE 2015 | [lien](https://mucollective.northwestern.edu/project/hops) | Article | {résumé lu} | |
| Natural frequency facilitation | McDowell, Jacobs | SMDM 2016 (résumé) | [lien](https://smdm.confex.com/smdm/16BEC/webprogram/Paper9915.html) | Résumé de congrès | {résumé lu} | Article complet non lu |
| Why Can Only 24% Solve Bayesian Reasoning Problems | Inconnu | Frontiers, 2018 | [lien](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6194348/) | Article | {repéré} | |
| Risk and Uncertainty Communication | Spiegelhalter | Annu. Rev. Stat. Appl. 4, 2017 | [lien](https://www.repository.cam.ac.uk/handle/1810/260626) | Revue | {résumé lu} | Texte sous embargo |
| Communicating uncertainty and trust | van der Bles, van der Linden, Freeman, Spiegelhalter | PNAS 117(14), 2020 | [lien](https://core.ac.uk/download/305110478.pdf) | Article | {texte analysé} | |
| Communicating Data Uncertainty (PIB britannique) | Galvão, Mitchell | Cleveland Fed WP 21-28R, juillet 2022 | [lien](https://www.clevelandfed.org/-/media/project/clevelandfedtenant/clevelandfedsite/publications/working-papers/2022/wp-2128r-communicating-data-uncertainty-multi-wave-experimental-evidence-for-uk-gdp-pdf.pdf) | Document de travail | {texte analysé} partiel | |
| Anchors aweigh? | McMahon, Naylor, Rholes, Rickards (Banque d'Angleterre) | WP 1196, 2026-07-17 | [lien](https://www.bankofengland.co.uk/working-paper/2026/anchors-aweigh-the-effect-of-communicating-forecast-uncertainty) | Document de travail | {résumé lu} | |
| Experience Sampling and Graphical Displays | Kaufmann, Weber, Haisley | Management Science 59(2), 2013 | [lien](https://econpapers.repec.org/RePEc:inm:ormnsc:v:59:y:2013:i:2:p:323-340) | Article | {résumé lu} | |
| Critique de l'échelle de risque de l'Aperçu du fonds | D. Hallett (Investment Executive) | 2016-12-22 | [lien](https://www.investmentexecutive.com/news/industry/focus-on-products/missing-the-mark/) | Article de presse spécialisée | {texte analysé} | Autres critiques {repérées} : [OSC IAP](https://www.osc.ca/sites/default/files/2020-11/com_20140307_81-324_iap.pdf), [FP Canada](https://fpcanada.ca/docs/default-source/news/fpsc-csa-proposal-81-324.pdf) |
| Explanation in Artificial Intelligence | T. Miller | arXiv 1706.07269 v3 ; Artificial Intelligence 267, 2019 | [lien](https://arxiv.org/pdf/1706.07269) | Article | {texte analysé} (première moitié) | |
| Counterfactual Explanations without Opening the Black Box | Wachter, Mittelstadt, Russell | Harvard JOLT 2018 | [lien](https://arxiv.org/abs/1711.00399) | Article | {résumé lu} | |
| Does the Whole Exceed its Parts? | Bansal et al. | CHI 2021 | [lien](https://arxiv.org/abs/2006.14779) | Article | {résumé lu} | |
| To Trust or to Think | Buçinca, Malaya, Gajos | CSCW 2021 | [lien](https://arxiv.org/abs/2102.09692) | Article | {résumé lu} | Texte complet non lu |
| Overcoming Algorithm Aversion | Dietvorst, Simmons, Massey | Management Science 64(3), 2018 | [lien](https://ideas.repec.org/a/inm/ormnsc/v64y2018i3p1155-1170.html) | Article | {résumé lu} | |
| Explainable AI and Financial Algorithmic Advisors | Ben-David, Resheff, Tron | AIES 2021 | [lien](https://ar5iv.arxiv.org/html/2101.02555) | Article | {texte analysé} | MTurk, jeu stylisé |
| Feature-based explanations in robo-advice | Inconnu | HAL hal-04125939, 2023 | [lien](https://hal.archives-ouvertes.fr/hal-04125939) | Article | Inaccessible (anti-robot) | |
| Principles of Mixed-Initiative User Interfaces | E. Horvitz | CHI 1999 | [lien](https://www.erichorvitz.com/chi99horvitz.pdf) | Article | {texte analysé} | Principes, pas d'effets mesurés |
| Épistémologie d'un système expert (notes de 1993) | W. Clancey | Notes de 1993 sur l'article de 1983 | [lien](https://web-archive.southampton.ac.uk/cogprints.org/292/1/126.htm) | Rétrospective | {texte analysé} | Article de 1983 non lu |
| Decision Quality Instruments | MGH Health Decision Sciences Center | Page courante | [lien](https://mghdecisionsciences.org/tools-training/decision-quality-instruments/) | Instruments | {page lue} | Gratuits pour les chercheurs |
| Berlin Numeracy Test | Cokely, Galesic, Schulz, Ghazal, Garcia-Retamero | JDM 7(1), 2012 | [lien](https://www.cambridge.org/core/journals/judgment-and-decision-making/article/measuring-risk-literacy-the-berlin-numeracy-test/A9B26516D12D48EFA4BD3560E2001E8E) | Article | {résumé lu} ; licence lue | Article CC BY 3.0 |
| Big Three (formulation) | Lusardi, Mitchell | NBER WP 31145, avril 2023 | [lien](https://www.nber.org/system/files/working_papers/w31145/w31145.pdf) | Document de travail | {texte analysé} | Conditions d'usage non trouvées |
| Résultats HRS 2004 | Lusardi, Mitchell, Curto | 2014 | [lien](https://pmc.ncbi.nlm.nih.gov/articles/PMC5445927) | Article | {page lue} | |
| Evaluating the Evaluators (lisibilité) | Cachola, Khashabi, Dredze | arXiv 2508.19221, août 2025 | [lien](https://arxiv.org/abs/2508.19221) | Prépublication | {résumé lu} | |
| Neither Valid nor Reliable? | Chehbouni, Haddou, Cheung, Farnadi | arXiv 2508.18076, août 2025 | [lien](https://arxiv.org/abs/2508.18076) | Prise de position | {résumé lu} | |
| Teach-back, revue systématique | Talevski et al. | PLoS ONE 2020 | [lien](https://doaj.org/article/b1abc68239814afcb1efb196ce30aba8) | Revue | {repéré} | PMC bloqué |

### 9.6 Architecture agentique, vérification, sécurité et outillage

| Ressource | Auteurs ou organisation | Date ou version | Lien | Nature | Niveau d'examen | Remarques |
|---|---|---|---|---|---|---|
| Building effective agents | E. S., B. Zhang (Anthropic) | 2024-12-19 | [lien](https://www.anthropic.com/engineering/building-effective-agents) | Billet d'ingénierie | {page lue} (extraction auto) | Témoignage de praticien |
| How we built our multi-agent research system | Hadfield, Zhang, Lien, Scholz, Fox, Ford (Anthropic) | 2025-06-13 | [lien](https://www.anthropic.com/engineering/multi-agent-research-system) | Billet d'ingénierie | {page lue} (extraction auto) | Évaluation interne non publique |
| A practical guide to building agents | OpenAI | PDF non daté | [lien](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) | Guide | {page lue} (extraction auto) | Date de publication non vérifiée |
| Don't Build Multi-Agents | W. Yan (Cognition) | 2025-06-12 | [lien](https://cognition.com/blog/dont-build-multi-agents) | Billet | {page lue} (extraction auto) | Opinion, contexte de code |
| Towards a Science of Scaling Agent Systems | Kim, Gu, Park et al. | arXiv 2512.08296 v3 | [lien](https://arxiv.org/abs/2512.08296) | Prépublication | {résumé lu} | Banc financier non identifié |
| More Agents Is All You Need | Li et al. | arXiv 2402.05120 (TMLR) | [lien](https://arxiv.org/abs/2402.05120) | Article | {résumé lu} | |
| Multiagent Debate | Du, Li, Torralba et al. | arXiv 2305.14325, 2023 | [lien](https://arxiv.org/abs/2305.14325) | Prépublication | {résumé lu} | Affirmation d'origine du débat |
| Should we be going MAD? | Smit et al. | arXiv 2311.17371 v3 | [lien](https://arxiv.org/abs/2311.17371) | Prépublication | {résumé lu} | |
| Rethinking the Bounds of LLM Reasoning | Q. Wang et al. | arXiv 2402.18272 | [lien](https://arxiv.org/abs/2402.18272) | Prépublication | {résumé lu} | |
| Stop Overvaluing Multi-Agent Debate | H. Zhang et al. | arXiv 2502.08788 | [lien](https://arxiv.org/abs/2502.08788) | Prise de position avec expériences | {résumé lu} | |
| Debate or Vote | Choi, Zhu, Li | arXiv 2508.17536 ; NeurIPS 2025 | [lien](https://arxiv.org/abs/2508.17536) | Article | {résumé lu} | |
| Débat avec outils et portes de vérification (chimie) | Chauvin, Jager | arXiv 2610.33002, 2026-10 | [lien](https://arxiv.org/abs/2610.33002) | Prépublication | {résumé lu} | Domaine éloigné |
| LLMs Cannot Self-Correct Reasoning Yet | Huang et al. | ICLR 2024 | [lien](https://arxiv.org/abs/2310.01798) | Article | {résumé lu} | |
| Survey on self-correction | Kamoi et al. | TACL 2024 | [lien](https://arxiv.org/abs/2406.01297) | Revue | {résumé lu} | |
| Finding reasoning errors | Tyen et al. | ACL 2024 Findings | [lien](https://arxiv.org/abs/2311.08516) | Article | {résumé lu} | |
| CRITIC | Gou et al. | ICLR 2024 | [lien](https://arxiv.org/abs/2305.11738) | Article | {résumé lu} | |
| MT-Bench et Chatbot Arena | Zheng et al. | NeurIPS 2023 D&B | [lien](https://arxiv.org/abs/2306.05685) | Article | {résumé lu} | |
| LLMs are not Fair Evaluators | P. Wang et al. | 2023 | [lien](https://arxiv.org/abs/2305.17926) | Prépublication | {résumé lu} | |
| Self-recognition and self-preference | Panickssery, Bowman, Feng | 2024 | [lien](https://arxiv.org/abs/2404.13076) | Prépublication | {résumé lu} | |
| Justice or Prejudice? | Ye et al. | 2024 | [lien](https://arxiv.org/abs/2410.02736) | Prépublication | {résumé lu} | |
| Correlated Errors in LLMs | Kim, Garg, Peng, Garg | ICML 2025 | [lien](https://arxiv.org/abs/2506.07962) | Article | {résumé lu} | |
| Great Models Think Alike | Goel et al. | 2025 | [lien](https://arxiv.org/abs/2502.04313) | Prépublication | {résumé lu} | |
| AI Agents That Matter | Kapoor et al. | 2024 | [lien](https://arxiv.org/abs/2407.01502) | Prépublication | {résumé lu} | |
| PAL | Gao, Madaan, Zhou et al. | arXiv 2211.10435 v2 | [lien](https://arxiv.org/abs/2211.10435) | Prépublication | {résumé lu} | |
| Program of Thoughts | Chen, Ma, Wang, Cohen | TMLR 2023 | [lien](https://arxiv.org/abs/2211.12588) | Article | {résumé lu} | |
| Hallucination in finance | Kang, Liu | arXiv 2311.15548 | [lien](https://arxiv.org/abs/2311.15548) | Prépublication | {résumé lu} | |
| FinDVer | Zhao et al. | EMNLP 2024 | [lien](https://arxiv.org/abs/2411.05764) | Article | {résumé lu} | |
| Let Me Speak Freely? | Tam et al. | arXiv 2408.02442 | [lien](https://arxiv.org/abs/2408.02442) | Prépublication | {résumé lu} | Réfutation d'un vendeur connue de mémoire, non vérifiée |
| Language Models Don't Always Say What They Think | Turpin, Michael, Perez, Bowman | NeurIPS 2023 | [lien](https://arxiv.org/abs/2305.04388) | Article | {résumé lu} | |
| Measuring Faithfulness in CoT | Lanham et al. | 2023 | [lien](https://arxiv.org/abs/2307.13702) | Prépublication | {résumé lu} | |
| AIS ; ALCE ; FActScore ; RAGAS | Rashkin et al. ; Gao et al. ; Min et al. ; Es et al. | 2022 à 2025 | [AIS](https://arxiv.org/abs/2112.12870), [ALCE](https://arxiv.org/abs/2305.14627), [FActScore](https://arxiv.org/abs/2305.14251), [RAGAS](https://arxiv.org/abs/2309.15217) | Articles | {résumé lu} | Transfert à la finance non testé |
| CaMeL | Debenedetti, Shumailov, Fan et al. | arXiv 2503.18813 v2, 2025-06-24 | [article](https://arxiv.org/abs/2503.18813), [code](https://github.com/google-research/camel-prompt-injection) | Prépublication, code | {texte analysé} partiel | Affiliations non vérifiées |
| Not what you've signed up for | Greshake, Abdelnabi, Mishra et al. | arXiv 2302.12173 v2 | [lien](https://arxiv.org/abs/2302.12173) | Prépublication | {résumé lu} | |
| OWASP LLM01:2025 | OWASP GenAI Security Project | 2025 | [lien](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | Référentiel | {texte analysé} partiel | LLM06 et LLM09 non lus |
| NIST AI 100-2 E2025 | A. Vassilev et al. (NIST) | Mars 2025, PDF corrigé 2025-04-01, erratum 2025-06-03 | [page](https://csrc.nist.gov/pubs/ai/100/2/e2025/final), [PDF](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-2e2025.pdf) | Taxonomie | Page d'accueil lue, PDF non lu | |
| AgentDojo | Debenedetti, Zhang, Balunović et al. | arXiv 2406.13352 v3 | [article](https://arxiv.org/abs/2406.13352), [code](https://github.com/ethz-spylab/agentdojo) | Environnement de test | {texte analysé} partiel | Lieu NeurIPS 2024 non vérifié |
| Spotlighting | Hines, Lopez, Hall et al. | arXiv 2403.14720 | [lien](https://arxiv.org/abs/2403.14720) | Prépublication | {résumé lu} | Attaques non adaptatives |
| Design Patterns for Securing LLM Agents | Beurer-Kellner et al. | arXiv 2506.08837 v3 | [lien](https://arxiv.org/abs/2506.08837) | Prépublication | {résumé lu} | Liste des motifs donnée de mémoire [NV] |
| The Attacker Moves Second | Nasr, Carlini, Sitawarin et al. | arXiv 2510.09023 | [lien](https://arxiv.org/abs/2510.09023) | Prépublication | {résumé lu} | Défenses visées non identifiées |
| MAST | Cemri, Pan, Yang et al. | arXiv 2503.13657 v3, 2025-10-26 | [lien](https://arxiv.org/html/2503.13657v3) | Prépublication | {texte analysé} partiel | |
| Who&When | Zhang, Yin et al. | arXiv 2505.00212 | [lien](https://arxiv.org/abs/2505.00212) | Article | {résumé lu} | |
| tau-bench | Yao et al. | arXiv 2406.12045 | [lien](https://arxiv.org/abs/2406.12045) | Banc d'essai | {résumé lu} | |
| GSN Community Standard | SCSC | Version et date non vérifiées | scsc.uk | Norme | Inaccessible (page vide) | [NV] |
| LangGraph | LangChain | 1.2.22, 2026-11-14 | [dépôt](https://github.com/langchain-ai/langgraph), [persistance](https://docs.langchain.com/oss/python/langgraph/persistence) | Framework | {licence lue}, documentation lue | MIT |
| AutoGen | Microsoft | autogen-agentchat 0.7.5, 2025-09-30 | [lien](https://github.com/microsoft/autogen/blob/main/README.md) | Framework | README et licences lus | Code MIT, documentation CC-BY-4.0 ; archivé |
| Microsoft Agent Framework | Microsoft | 1.26.0, 2026-11-12 | [lien](https://github.com/microsoft/agent-framework) | Framework | {licence lue}, README lu | MIT |
| AG2 | ag2ai | 1.3.1, 2026-11-10 | [lien](https://github.com/ag2ai/ag2) | Framework | {licence lue} | Apache-2.0 ; fonctions non examinées |
| CrewAI | crewAI Inc. | 1.15.41, 2026-11-12 | [lien](https://github.com/crewAIInc/crewAI) | Framework | {licence lue}, README lu | MIT ; télémétrie par défaut |
| OpenAI Agents SDK | OpenAI | 0.24.0, 2026-10-15 | [dépôt](https://github.com/openai/openai-agents-python), [traçage](https://github.com/openai/openai-agents-python/blob/main/docs/tracing.md) | Framework | {licence lue}, documentation lue | MIT ; destination des traces par défaut non vérifiée |
| Pydantic AI | Pydantic Services | 2.68.0, 2026-11-12 | [lien](https://github.com/pydantic/pydantic-ai/blob/main/README.md) | Framework | {licence lue}, README lu | MIT |
| smolagents | Hugging Face | 1.26.0, 2026-05-29 | [lien](https://github.com/huggingface/smolagents/blob/main/README.md) | Framework | {licence lue}, README lu | Apache-2.0 |
| Conventions OpenTelemetry GenAI | OpenTelemetry | Statut « Development » | [nouveau dépôt](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/README.md), [ancien](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/README.md) | Spécification | {page lue} | Apache-2.0 |
| Langfuse | ClickHouse, Inc. (titulaire des droits) | SDK 5.2.0, 2026-11-05 | [dépôt](https://github.com/langfuse/langfuse), [auto-hébergement](https://langfuse.com/self-hosting) | Outil | {licence lue} | MIT hors `ee/` ; rachat non vérifié |
| Arize Phoenix | Arize AI | 21.0.0, 2026-10-30 | [lien](https://github.com/Arize-ai/phoenix) | Outil | {licence lue}, README lu | Elastic License 2.0 |
| inspect_ai | UK AI Security Institute | 0.3.290, 2026-11-14 | [lien](https://github.com/UKGovernmentBEIS/inspect_ai) | Outil | {licence lue}, README lu | MIT ; bêta |
| promptfoo | Promptfoo (OpenAI) | npm 0.125.1, 2026-10-25 | [lien](https://github.com/promptfoo/promptfoo) | Outil | {licence lue}, README lu | MIT |
| DeepEval | Confident AI | 4.3.4, 2026-11-11 | [lien](https://github.com/confident-ai/deepeval) | Outil | {licence lue}, README lu | Apache-2.0 |

### 9.7 Données, ESG et provenance

| Ressource | Organisation ou auteurs | Date ou version | Lien | Nature | Niveau d'examen | Licence ou remarques |
|---|---|---|---|---|---|---|
| Conditions de l'API FRED | Banque fédérale de réserve de Saint-Louis | Non daté | [lien](https://fred.stlouisfed.org/docs/api/terms_of_use.html) | Conditions | {page lue} (extraction auto) | Données : avis obligatoire, permission pour séries tierces |
| Documentation temps réel FRED, page ALFRED | Même organisation | | [lien](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html) | Documentation | Inaccessible (délai) | Paramètres [NV] |
| Taux de change, méthodologie | Banque du Canada | Page courante | [lien](https://www.bankofcanada.ca/rates/exchange/background-information/) | Méthodologie | {texte analysé} | |
| Conditions d'utilisation | Banque du Canada | Page courante | [lien](https://www.bankofcanada.ca/terms/) | Conditions | {texte analysé} | Données : attribution, mention des modifications |
| Documentation Valet | Banque du Canada | | [lien](https://www.bankofcanada.ca/valet/docs) | Documentation | Inaccessible (JavaScript) | Code de série [NV] |
| Licence ouverte | Statistique Canada | Page courante | [lien](https://www.statcan.gc.ca/en/reference/licence) | Licence | {texte analysé} | |
| stats-can | Projet indépendant | 3.3.0, 2026-09-25 | [lien](https://pypi.org/pypi/stats-can/json) | Client Python | {licence lue} | Code GPL-3.0-or-later |
| Real-Time Data Set for Macroeconomists | Philadelphia Fed ; Croushore, Stark | Mise à jour mensuelle ; J. Econometrics 105(1), 2001 | [page](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists), [article](https://econpapers.repec.org/RePEc:eee:econom:v:105:y:2001:i:1:p:111-130) | Données, article | {page lue} (extraction auto) ; notice vérifiée, résumé illisible | |
| fredapi ; pandas-datareader | Projets indépendants | 0.5.2 (2024-05-05) ; 0.11.1 (2026-06-24) | [fredapi](https://pypi.org/pypi/fredapi/json), [pandas-datareader](https://pypi.org/pypi/pandas-datareader/json) | Clients | {licence lue} | Licence vide ; BSD-3 |
| The (Un)predictable Past of ESG Ratings | Berg, Fabisik, Sautner | ECGI WP 708/2020, révisé 2021 | [lien](https://www.ecgi.global/publications/working-papers/is-history-repeating-itself-the-unpredictable-past-of-esg-ratings) | Document de travail | {résumé lu} | PDF non lu |
| exchange_calendars | G. Manoim et contributeurs | 4.13.3, 2026-11-14 | [lien](https://github.com/gerrymanoim/exchange_calendars) | Bibliothèque | {licence lue}, README analysé | Apache-2.0 |
| pandas_market_calendars | R. Sheftel | 5.6.1, 2026-11-14 | [lien](https://github.com/rsheftel/pandas_market_calendars) | Bibliothèque | {licence lue}, README analysé | MIT |
| Asynchronisme (Burns-Engle-Mezrich 1998 ; Hayashi-Yoshida 2005) | | | [EconBiz](https://www.econbiz.de/Record/correlations-and-volatilities-of-asynchronous-data/10001246679), [Project Euclid](https://www.projecteuclid.org/euclid.bj/1116340299) | Articles | {repéré} | Epps, Scholes-Williams, Dimson : [NV] |
| yfinance (README, LICENSE, price repair) | R. Aroussi et contributeurs | 1.8.0, 2026-11-03 | [README](https://github.com/ranaroussi/yfinance), [price repair](https://github.com/ranaroussi/yfinance/blob/main/doc/source/advanced/price_repair.rst) | Bibliothèque, documentation | {texte analysé} | Code Apache-2.0 ; données sous conditions Yahoo |
| Conditions de Yahoo | Yahoo | Page courante | [lien](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html) | Conditions | {texte analysé} | Collecte automatisée interdite sans permission |
| Archive Coin Metrics | Coin Metrics | Mise à jour quotidienne | [lien](https://github.com/coinmetrics/data) | Données | {licence lue}, README analysé | Données CC BY-NC 4.0 |
| Conditions de l'API CoinGecko | CoinGecko | Dernière mise à jour 2025-09-05 | [lien](https://www.coingecko.com/en/api_terms) | Conditions | {page lue} (extraction auto) | |
| Accessing EDGAR Data | SEC | Revue 2024-06-26 | [lien](https://www.sec.gov/os/accessing-edgar-data) | Documentation | {page lue} (extraction auto) | |
| Tarifs EODHD | EODHD | Page courante | [lien](https://eodhd.com/pricing) | Prix | {texte analysé} | Quotas gratuits non extraits |
| OpenFIGI | Bloomberg | Conditions du 2018-11-27 | [conditions](https://www.openfigi.com/docs/terms-of-service), [API](https://www.openfigi.com/api/documentation) | Conditions, API | {texte analysé} | Identifiants dans le domaine public ; client `openfigi-client` 0.4.2 sous MIT |
| Stooq ; Tiingo ; Alpha Vantage ; Nasdaq Data Link | | | [Stooq](https://stooq.com/db/h/), [Tiingo](https://www.tiingo.com/about/pricing), [Alpha Vantage](https://www.alphavantage.co/terms_of_service/), [Nasdaq](https://data.nasdaq.com/terms) | Conditions | Inaccessibles (délai, JavaScript, clauses non extraites, 404) | Aucune affirmation |
| Form N-PORT Data Sets | SEC | Revue 2026-09-30 | [lien](https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets) | Données | {page lue} (extraction auto) | Régime mensuel public [NV] |
| Fichier de positions iShares (exemple) | BlackRock | | [lien](https://www.ishares.com/us/products/239615/ishares-msci-canada-etf/latest-holdings.csv) | Données | {repéré} | Conditions non lues |
| Asset Allocation: Management Style and Performance Measurement | W. F. Sharpe | JPM, hiver 1992 | [lien](https://web.stanford.edu/~wfsharpe/art/sa/sa.htm) | Article | {texte analysé} (extraction auto) | Critiques {repérées} : [Bohrium](https://www.bohrium.com/paper-details/pitfalls-in-linear-models-for-style-analysis/812347998385209344-1123), [Erasmus](https://repub.eur.nl/pub/25/erimrs20000525115250.pdf) |
| Aggregate Confusion | Berg, Kölbel, Rigobon | Review of Finance 26(6), 2022 | [OUP](https://academic.oup.com/rof/article/26/6/1315/6590670), [synthèse](https://revfin.org/?p=2611) | Article | {page de synthèse lue} | |
| Firm Size and ESG Score | Drempetic, Klein, Zwergel | J. Business Ethics 167(2), 2020 | [lien](https://link.springer.com/content/pdf/10.1007/s10551-019-04164-1.pdf) | Article | {résumé lu} | |
| Rewriting History II | Harvard Law School Forum | 2020-11-11 | [lien](https://corpgov.law.harvard.edu/2020/11/11/rewriting-history-ii-the-unpredictable-past-of-esg-ratings/) | Billet | {repéré} | |
| GDELT, conditions | GDELT Project | Page courante | [lien](https://www.gdeltproject.org/about.html) | Conditions | {texte analysé} | Usage illimité avec citation et lien |
| SBTi Target Dashboard | Science Based Targets initiative | Mise à jour hebdomadaire | [lien](https://sciencebasedtargets.org/target-dashboard) | Données | {texte analysé} | Aucune licence de données trouvée |
| Règles de citation Sustainalytics | Sustainalytics | Page courante | [lien](https://www.sustainalytics.com/knowledge-hub/referencing-sustainalytics-esg-risk-ratings) | Conditions | {page lue} (extraction auto) | Page de mentions légales non lue |
| Outil et conditions ESG de MSCI | MSCI | Date d'affichage 2025-11-12 | [outil](https://www.msci.com/research-and-insights/esg-ratings-corporate-search-tool), [conditions](https://www.msci.com/additional-terms-of-use-msci-esg-research-llc) | Conditions | Inaccessible (métadonnées seulement) | Aucune affirmation |
| Avis 81-334 révisé (résumé) | Osler | 2024 | [Osler](https://www.osler.com/en/resources/regulations/2024/csa-publishes-updated-guidance-on-esg-related-investment-fund-disclosure), [PDF OSC](https://OSC.gov.on.ca/sites/default/files/2024-03/20240307_81-334_sn-related-investment-fund-disclosure.pdf) | Résumé de cabinet | Résumé lu ; PDF primaire inaccessible | [I] |
| Lignes directrices sur les allégations environnementales ; loi C-15 (résumés) | Fasken ; MLT Aikins | Juin 2025 ; 2026-03-30 | [Fasken](https://www.fasken.com/en/knowledge/2025/06/canadas-competition-bureau-releases-final-guidelines-on-environmental-claims), [MLT Aikins](https://www.mltaikins.com/insights/federal-government-narrows-scope-of-the-competition-acts-anti-greenwashing-provisions-as-bill-c-15-receives-royal-assent/) | Résumés de cabinets | Résumés lus | Textes primaires non vérifiés |
| DVC, MLflow, OpenLineage, Great Expectations, Kedro, papermill, Hamilton | Divers | 3.67.1 ; 3.18.0 ; 1.55.0 ; 1.25.0 ; 1.8.0 ; 2.7.0 ; 1.90.0 | [PyPI DVC](https://pypi.org/pypi/dvc/json), [Hamilton](https://github.com/apache/hamilton) | Outils | {licence lue} | Apache-2.0 ou BSD-3 |
| lakeFS | Treeverse | Serveur 1.87.0 ; SDK 0.16.0 | [lien](https://github.com/treeverse/lakeFS/blob/master/LICENSE) | Outil | {licence lue} | Serveur BSL 1.1 ; SDK Apache-2.0 |
| pandera ; prov | Divers | 0.36.0 ; 3.3.0 | [pandera](https://pypi.org/pypi/pandera/json), [prov](https://pypi.org/pypi/prov/json) | Outils | {licence lue} | MIT |
| W3C PROV ; Datasheets for Datasets | W3C ; Gebru et al. | 2013 ; CACM 64(12), 2021 | [PROV](https://www.w3.org/TR/prov-overview/), [Datasheets](https://arxiv.org/abs/1803.09010) | Norme ; article | [NV] non consultés | |

### 9.8 AWS

| Ressource | Organisation | Date indiquée | Lien | Nature | Niveau d'examen | Remarques |
|---|---|---|---|---|---|---|
| Regional availability by models | AWS | Aucune | [lien](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html) | Documentation | 148 tableaux analysés par programme | |
| Fiches modèles (Haiku 5.5, Sonnet 5.5, Nova 2 Lite, Nova Lite, Llama 3 70B, Mistral Large) | AWS | Lancement de Haiku 5.5 : 2026-10-07 | [Haiku 5.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-5-5.html), [Sonnet 5.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5-5.html), [Nova Lite](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-lite.html), [Nova 2 Lite](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-lite.html), [Llama 3 70B](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-meta-llama-3-70b-instruct.html), [Mistral Large](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-mistral-ai-mistral-large.html) | Documentation | Fiches clés lues ; 46 fiches parcourues | Incohérence non résolue sur la fin de vie de Claude 3 Haiku |
| Profils d'inférence ; inférence inter-régions géographique | AWS | Aucune | [profils](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html), [géographique](https://docs.aws.amazon.com/bedrock/latest/userguide/geographic-cross-region-inference.html) | Documentation | {page lue} | |
| Accès aux modèles | AWS | Aucune | [lien](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) | Documentation | {page lue} (première moitié) | |
| Quotas Bedrock | AWS | Aucune | [quotas](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html), [exécution](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-runtime.html), [référence générale](https://docs.aws.amazon.com/general/latest/gr/bedrock.html) | Documentation | {page lue} | Valeurs du compte inconnues |
| Prix de Bedrock | AWS | og:updated_time 2026-11-12 | [lien](https://aws.amazon.com/bedrock/pricing/) | Page de prix | Prix lus par programme dans le JSON de la page, non vus à l'écran | **Prix de Haiku 5.5 à vérifier visuellement** |
| Guardrails : ancrage contextuel, raisonnement automatisé, niveaux, langues, modèles pris en charge | AWS | Raisonnement automatisé lancé le 2025-08-05 | [ancrage](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html), [raisonnement](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html), [niveaux](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tiers.html), [langues](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-supported-languages.html), [modèles](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-supported.html) | Documentation | {page lue} | Comportement réel non testé |
| Bedrock Agents (Classic) ; historique de la documentation | AWS | Annonce 2026-06-30, fermeture 2026-07-30 | [agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html), [historique](https://docs.aws.amazon.com/bedrock/latest/userguide/doc-history.html) | Documentation | {page lue} | |
| Knowledge Bases, Flows, Prompt Management, Evaluations | AWS | Flows GA 2024-11-22 ; Prompt Management GA 2024-11-07 | [KB](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html), [Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html), [Prompts](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html), [Evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) | Documentation | {page lue} | |
| AgentCore : vue d'ensemble, régions, notes de version, observabilité | AWS | Notes jusqu'en novembre 2026 | [vue d'ensemble](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html), [régions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html), [notes](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/doc-history.html), [observabilité](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) | Documentation | {page lue} ; tableau analysé | Page des limites téléchargée, non lue |
| Prix d'AgentCore | AWS | og:updated_time 2026-11-12 | [lien](https://aws.amazon.com/bedrock/agentcore/pricing/) | Page de prix | {page lue} | Pas de prix par région ; pas de ligne pour le harness |
| Lambda : quotas et environnements | AWS | Dates de dépréciation dans le tableau | [quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), [environnements](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html) | Documentation | {page lue} | Prix non relevés |
| Step Functions : types, quotas, prix | AWS | og:updated_time 2026-11-12 | [types](https://docs.aws.amazon.com/step-functions/latest/dg/choosing-workflow-type.html), [quotas](https://docs.aws.amazon.com/step-functions/latest/dg/service-quotas.html), [prix](https://aws.amazon.com/step-functions/pricing/) | Documentation et prix | {page lue} | Prix canadien non résolu |
| App Runner ; ECS Express Mode | AWS | Aucune | [App Runner](https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html), [ECS Express](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-service-overview.html) | Documentation | Introductions lues | Coût du répartiteur non relevé |
| S3 Versioning, Object Lock ; journalisation Bedrock ; SDK X-Ray | AWS | Maintenance X-Ray depuis 2026-02-25 | [Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html), [Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html), [journalisation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html), [X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python.html) | Documentation | Introductions lues | |
| Free Tier : annonce, billet, FAQ | AWS | 2025-07-16 ; 2025-07-15 ; og 2026-11-12 | [annonce](https://aws.amazon.com/about-aws/whats-new/2025/07/aws-free-tier-credits-month-free-plan/), [billet](https://aws.amazon.com/blogs/aws/aws-free-tier-update-new-customers-can-get-started-and-explore-aws-with-up-to-200-in-credits/), [FAQ](https://aws.amazon.com/free/faqs/) | Annonce, billet, FAQ | {page lue} | FAQ contradictoire sur l'expiration des crédits ; muette sur Marketplace |
| AWS Budgets | AWS | Aucune | [lien](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html) | Documentation | Introduction lue | Pas de plafond dur |
| Prix d'Amplify | AWS | og 2026-11-12 | [lien](https://aws.amazon.com/amplify/pricing/) | Page de prix | {page lue} | Formulation « 12 mois » en conflit avec le plan de 6 mois |
| Strands Agents SDK | Projet Strands Agents (sous direction AWS) | Dernier commit 2026-11-14 ; PyPI 1.65.0 | [lien](https://github.com/strands-agents/sdk-python) | SDK | {code inspecté} (arborescence, pyproject) | Code Apache-2.0 (fichier LICENSE.APACHE) |
| amazon-bedrock-agentcore-samples | AWS Labs | HEAD `46313bd`, 2026-11-13 | [lien](https://github.com/awslabs/amazon-bedrock-agentcore-samples) | Échantillons | README et LICENSE lus | Code Apache-2.0 |
| sample-genai-market-data-analysis | AWS Samples | Dernier commit 2026-01-14 | [lien](https://github.com/aws-samples/sample-genai-market-data-analysis) | Échantillon | README et LICENSE lus | Forme MIT-0 |
| sample-wealth-advisor-demo-platform | AWS Samples | Dernier commit 2026-04-23 | [lien](https://github.com/aws-samples/sample-wealth-advisor-demo-platform) | Échantillon | README lu | Aucun LICENSE à la racine |
| Billets AWS Industries et Machine Learning (recherche d'investissement avec Strands ; plateforme de gestion de patrimoine ; Morningstar ; Heurist Finance ; multi-agents sur EKS) | AWS | 2026-04-29 ; 2026-05-31 ; 2026-09-28 ; non relevées | [Strands](https://aws.amazon.com/blogs/industries/automate-investment-research-using-strands-agents-on-bedrock-agentcore/), [patrimoine](https://aws.amazon.com/blogs/industries/the-art-of-the-possible-building-an-intelligent-wealth-management-platform-part-1/), [Morningstar](https://aws.amazon.com/blogs/industries/how-morningstar-built-a-financial-advisor-ai-assistant-powered-by-amazon-bedrock-agentcore/), [Heurist](https://aws.amazon.com/blogs/machine-learning/how-heurist-finance-built-an-ai-native-investment-workbench-on-amazon-bedrock-agentcore/), [EKS](https://aws.amazon.com/blogs/industries/multi-agent-systems-for-financial-services-on-amazon-eks-and-agentcore/) | Billets marketing | {repéré} (métadonnées et liens) | Aucune preuve technique |
| Registry of Open Data, étiquette market-data | AWS | | [lien](https://registry.opendata.aws/tag/market-data/) | Catalogue | {repéré} | Aucun jeu vérifié |

## 10. Recommandation argumentée

Cette recommandation est une inférence [Inf] tirée des fiches. Elle ne promet ni optimalité ni victoire au datathon ; elle indique par où commencer pour apprendre le plus vite ce qui marche avec nos données et notre équipe.

### 10.1 Ce qu'il faut explorer ou prototyper d'abord

**Premièrement, le socle déterministe minimal, avant toute couche agentique.** Qualifier les données (E3), puis construire une bibliothèque fermée de cinq à sept formulations : variance minimale avec contraction Ledoit-Wolf sous les plafonds du persona, parité de risque, inverse volatilité, 1/N comme référence, probabilité d'objectif par bootstrap, faisabilité avec IIS et relaxation chiffrée, points de bascule. Chaque résultat entre dans un registre de calcul, et les explications obéissent au contrat de fidélité de la fiche 7. Ce socle est nécessaire à toutes les directions, repose sur les preuves les plus solides (fiches 1, 2, 4, 6) et neutralise l'échec le plus grave possible devant un jury financier : un nombre faux.

**Deuxièmement, une tranche verticale complète sur le cas de Robert.** Une phrase vague entre (« je veux préserver mon capital sur quatre ans, mais ce titre dont tout le monde parle me tente »). Le système construit le profil avec le conflit explicite (tolérance déclarée, capacité calculée, horizon court, titre spéculatif) ; choisit la formulation ; calcule ; vérifie ; puis explique de façon contrastive, avec un dotplot de « 20 avenirs » et la condition de bascule chiffrée : le rendement annuel minimal que le titre devrait offrir pour qu'une position de 5 % reste compatible avec l'objectif et le seuil de perte, comparé à son rendement réalisé et à l'erreur type de celui-ci (fiches 1, 3 et 4). Robert peut enfin modifier son horizon sans recommencer. Cette tranche concentre les critères du jury les plus disputés et correspond directement à une attente formulée par les régulateurs canadiens : expliquer pourquoi une opération voulue par le client ne convient pas, plutôt que simplement la noter (fiche 15).

**Troisièmement, la chaîne AWS minimale, tôt.** Après les vérifications E7 : Step Functions Standard, Lambda en image conteneur, S3 versionné avec manifeste par exécution, Bedrock avec le profil `ca.` retenu, journalisation des invocations, budget et alertes. La contribution AWS conditionne l'éligibilité : la prouver tôt réduit le risque le plus binaire du projet, et cette chaîne reste compatible avec les directions B, C et D.

**Quatrièmement, l'expérience E1** sur 30 à 40 cas, pour décider si l'effort agentique va au routage des formulations (B), à la conversation (C) ou aux deux.

**Cinquièmement, et seulement si une source de preuves ESG utilisable est trouvée ou fournie, la direction D**, accompagnée de E5.

### 10.2 Pourquoi cet ordre

L'ordre suit la solidité des preuves et le coût des erreurs. Le calcul délégué au code est la seule pratique dont les bénéfices sont mesurés de façon répétée, y compris sur des questions financières (fiche 6), alors que les gains du multi-agents dépendent fortement de la tâche (fiche 8) et que le profilage par LLM seul est documenté comme fragile (fiche 14). Les preuves sur l'élicitation adaptative et la restitution sont prometteuses mais viennent surtout d'autres domaines (fiches 16 à 18) : il faut donc les mettre à l'épreuve sur nos propres cas plutôt que de les présumer. Le cas de Robert est choisi parce qu'il est le plus discriminant : s'il est bien traité, les cas d'Amira (diversification d'un portefeuille technologique et crypto, horizon long non validable par cinq ans de données) et de Mateo (ESG inconnu par défaut, préférences recueillies dans l'ordre ESMA) réutilisent les mêmes briques. Enfin, la sophistication n'est récompensée que si sa valeur est démontrée : l'ablation E1 fournit cette démonstration, quel que soit son résultat.

### 10.3 Ce qui changerait la recommandation

| Observation | Changement |
|---|---|
| E1 : B apporte un gain net et C aucun | Placer l'effort agentique sur le routage des formulations et garder un questionnaire court et fixe |
| E1 : ni B ni C ne battent A | Garder A, présenter honnêtement une couche agentique limitée, et porter l'innovation sur la restitution et la vérification |
| E1 : A0 (sans LLM) égale A | Repenser le rôle du LLM ; le cantonner aux demandes vagues et contradictoires où il apporte quelque chose, ou le dire |
| E7 : prix de Haiku 5.5 non confirmé, ou destinations du profil `ca.` non limitées au Canada | Corriger l'énoncé de résidence et revoir le modèle, en disant où transitent les données |
| E4 : l'ancrage contextuel n'ajoute rien au contrôle déterministe | Retirer Guardrails de l'architecture pour éviter un service décoratif |
| Les organisateurs fournissent des preuves ESG ou autorisent une source licenciée | Donner plus de poids à la direction D |
| Les consignes du jury valorisent explicitement le multi-agents | Adopter la forme restreinte de D (travailleurs en lecture seule, vérification centralisée) avec ablation, jamais un débat libre |
| E2 : allocateurs indiscernables | Exposer plusieurs allocateurs avec leur robustesse plutôt qu'en choisir un « meilleur » |
| La licence du jeu de départ interdit la redistribution | Publier des scripts de reconstruction et des empreintes plutôt que les données |
| Le jeu de départ contient des prix déjà ajustés ou des horodatages crypto inattendus | Adapter E3 avant tout calcul |
| Le temps disponible est très court | Livrer A et la tranche Robert, qui forment le minimum crédible |

### 10.4 Prochaines vérifications, par ordre de priorité

1. **Vérifier visuellement la page de prix de Bedrock** pour Claude Haiku 5.5 et Sonnet 5.5 en ca-central-1, puisque le prix relevé de Haiku 5.5 paraît anormalement bas ; vérifier si les crédits couvrent les modèles facturés via AWS Marketplace et si le compte de l'équipe est fourni par les organisateurs.
2. Appeler `GetInferenceProfile` pour `ca.anthropic.claude-haiku-5-5` depuis ca-central-1, consulter Service Quotas et tester l'ancrage contextuel Classic en français avec ce profil, après avoir créé un budget avec alertes.
3. Inspecter le jeu de départ : prix bruts ou ajustés (double comptage), horodatage de la crypto, liste des neuf séries macro, présence d'un ETF obligataire ou équilibré pour les références, licence.
4. Vérifier les paramètres temps réel de l'API FRED, le code de série Valet et l'existence de millésimes chez Statistique Canada.
5. Lire l'article complet de Kim et al. : banc financier utilisé et sens de « décomposable ».
6. Vérifier l'exposition de `getIis` dans highspy, la prise en charge d'OpenTelemetry et de la validation humaine par Strands, l'export OpenTelemetry de LangGraph, et la destination par défaut des traces d'OpenAI Agents SDK si ce SDK est envisagé.
7. Relire dans les PDF toutes les citations et tous les chiffres marqués (extraction auto) avant de les mettre sur une diapositive, en priorité ceux de 31-368, de Ross et Lo (y compris l'écart entre 55,3 % et la fourchette de 57 à 88 %), de CLAMBER, de Fieberg et al. et des billets d'Anthropic.
8. Lire les textes primaires derrière les résumés de cabinets (avis 81-334, loi C-15) et la fin de l'avis 31-368 ; vérifier les particularités de l'AMF.
9. Vérifier les licences restantes : dépôts de GATE et de CLAMBER, items de Grable-Lytton, accord d'utilisation des DQI, version en ligne du Berlin Numeracy Test, fichiers NOTICE de TradingAgents et de FinRobot si du code est repris, conditions des fichiers de positions des émetteurs d'ETF.
10. Vérifier le régime actuel de publication mensuelle de N-PORT.
11. Écrire les tests de cohérence numérique entre bibliothèques (formule fermée de la variance minimale) avant de faire confiance aux résultats.
12. Lire le règlement du datathon : un service AWS précis est-il exigé (par exemple Bedrock) ? Quelles sont les règles sur les données externes et les comptes ?

Ce que la recherche apporte surtout, c'est un déplacement du risque. Le danger principal n'est pas de choisir le « mauvais » algorithme d'allocation, puisque plusieurs sont défendables et statistiquement difficiles à départager sur cinq ans ; c'est de laisser un LLM produire des nombres, des profils ou des performances qu'aucune preuve ne soutient, et de prendre une explication convaincante pour une explication fidèle. Une équipe qui montre au jury, mesures à l'appui, ce que son agent décide, ce que son code calcule et ce que ses données ne permettent pas de dire, se distingue d'abord par sa rigueur, sans avoir besoin d'un système plus complexe.