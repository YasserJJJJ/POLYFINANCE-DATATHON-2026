# Journal des implémentations candidates

15 novembre 2026. Ce journal ne prescrit pas une pile de production et ne ferme
pas le choix des méthodes. Une priorité signifie « prochain test qui pourrait
changer une décision ». Les expériences déjà réalisées sont séparées des
lectures de documentation et du code non exécuté.

## Protocoles proposés et état réel

| Priorité / question | Candidat et protocole discriminant | État dans ce cycle / condition de passage |
|---|---|---|
| P0 — financer un besoin exprimé | LP de budget, réserve, plafonds et rotation. Cas Robert, puis flux de dates différentes, frais fixes/proportionnels et cas infaisables. Comparer une borne analytique, résidus et optima alternatifs. | LP SciPy/HiGHS isolé exécuté ; rotation 30/40 % retrouvée, allocations non uniques. Les retraits dans une trajectoire et les frais ne sont pas implémentés. |
| P0 — expliquer un conflit | HiGHS direct : état du modèle, stratégie IIS explicite, bornes et lignes ; retirer chaque membre du sous-système obtenu. Confronter à un exemple algébrique, puis à des cas de limites numériques/temps. | highspy 1.16.0 testé sur `x≥0,4`, `x≤0,3`, `x≥0`. La stratégie légère ne donne pas l'IIS ; stratégie 4 réussit ici. Ni tous les LP ni les MIP sont validés. Un IIS n'est pas nécessairement de cardinalité minimale. |
| P0 — préserver la comptabilité | Petit simulateur de positions/flux avec cas sans rendement, apport/retrait, dividende, split, FX constant puis variable et coûts. Vérifier richesse finale, rendement hors flux et absence de double comptage. | Protocole seulement. C'est une condition de passage avant de comparer des plans de retraits, quel que soit le simulateur retenu. |
| P1 — covariance suffisamment stable ? | Covariance empirique, contraction identité, corrélation constante et contraintes justifiées. Même jeu complet de rendements, calendrier et objectif ; cas GMV soluble puis fenêtres hors temps, bootstrap en blocs, coûts et dérive des poids. | Empirique/identité exécutées avec scikit-learn + SLSQP : 15 blocs. Corrélation constante non exécutée. Le conditionnement amélioré ne vaut pas supériorité financière. |
| P1 — risque de pertes pertinent ? | CVaR LP indépendant puis PyPortfolioOpt/CVXPY : quantile fractionnaire, pertes répétées, probabilités non uniformes, signes, contraintes et variation de β. Éprouver le choix d'horizon et le nombre effectif d'événements extrêmes. | Petit LP ES indépendant exécuté ; code PyPortfolioOpt lu, bibliothèque non exécutée. Avec 252 jours et β=95 %, environ 12,6 observations équiprobables portent la queue : précision limitée, pas prédiction garantie. |
| P1 — rééquilibrage et coûts cohérents ? | cvxportfolio ou bt : même politique, cash, calendrier et coûts que la comptabilité de référence ; montrer la différence entre poids constants quotidiens et détention entre dates de rééquilibrage. | README et extraits code cvxportfolio lus ; bt README lu ; aucun simulateur exécuté. Ne pas multiplier directement chaque rendement par le poids cible en prétendant mesurer le turnover réalisé. |
| P1 — choisir entre solutions admissibles | Présenter dominance/coûts/risques, puis critère de départage qualifié ; pymcdm/pyDecision ou méthode directe si agrégation justifiée. Varier unités, normalisation et poids, tester renversement de classement. | Documentations et licences lues seulement. Un classement TOPSIS ne transforme pas des préférences inventées en décision objective. |
| P2 — financer plusieurs objectifs incertains | Reproduire un exemple de Das et al. avant adaptation : flux, richesse, états, distribution, frontière efficiente, troncature et convergence de grille. Comparer politique fixe et dynamique, puis stress du modèle et coûts. | Texte primaire partiel lu ; aucun résultat de leur papier reproduit. Les probabilités sont conditionnelles au modèle, pas des probabilités objectives de réussite du client. |
| P2 — ambiguïté de modèle déterminante ? | DRO Wasserstein, moment constraints ou stress robuste : vérifier classe de pertes, indépendance/queues, dimension et calibration du rayon ; comparer à CVaR/stress déterministe admissibles. | Théorie primaire partielle lue. Pas de solveur DRO exécuté, pas de garantie transférée hors hypothèses. |
| P2 — plusieurs objectifs non convexes ? | Pyomo/OR-Tools si variables entières nécessaires ; pymoo si frontière non convexe et aucune formulation certifiée adéquate. Sur petits cas, énumération de référence et certificats d'écart lorsque disponibles. | Documentation seulement. Évolutionnaire ≠ optimum global certifié ; un choix de solveur ne prouve pas la nécessité d'un MILP. |
| P2 — sélection après nombreux essais ? | arch/bootstrap, DSR indépendant, puis pypbo si le protocole correspond au problème : journal des essais, dépendance, moments, partitions et fuite temporelle. Vérifier d'abord une distribution nulle soluble. | Simulation nulle normale exécutée ; ni DSR complet ni PBO exécutés. Aucune valeur critique universelle de Sharpe. |
| À la demande — scénarios larges | EMA Workbench si l'exploration de scénarios/incertitudes est qualifiée ; plan d'expérience, couverture et critère de décision. | README/licence seulement. La recherche d'un scénario favorable n'est pas une validation. |

P0/P1/P2 ordonnent les dépendances du problème actuel. Une question utilisateur
nouvelle peut inverser ces priorités. Aucune taille fixe de catalogue n'est
requise.

## Observations de code qui changent le protocole

- **PyPortfolioOpt**, commit `a6638d2e06dae6f444fd022cfd4b3c528902a85b` :
  `risk_models.py:509–543` distingue trois cibles. La branche
  `constant_variance` remplace les NaN par zéro via `np.nan_to_num` avant
  l'estimation scikit-learn. Son constructeur peut conserver des lignes
  partiellement manquantes. Il faut donc contrôler le calendrier et les données
  complètes en entrée ; laisser cette substitution représenter une absence de
  cotation comme rendement nul serait une hypothèse financière silencieuse.
  `efficient_cvar.py:94–152` met en œuvre les auxiliaires du LP équiprobable.
- **cvxportfolio**, commit `351c782b9b8b395c1a5f886b77e0d55f1bc9396e` :
  `policies.py:1004–1048` assemble objectif, contraintes, cash, benchmark et
  solveur de secours. `simulator.py:264–315` calcule les poids depuis les
  positions, les trades depuis leur écart, puis applique des contraintes de
  volumes. Ce traitement répond à une limite de notre expérience à poids
  constants ; sa seule lecture ne valide pas tout le simulateur. Un changement
  de solveur de secours doit être consigné avec tolérances et résidus.
- **HiGHS**, commit `f3f113d230429a8c0014b12ab0dd1a3847e58c55` :
  `HighsOptions.h:1460–1467` distingue test léger, rayon dual, LP élastique et
  recherche d'un vrai IIS (`4`). La version installée testée est 1.16.0 ;
  un HEAD de dépôt et une distribution publiée ne sont pas assimilés.

Les copies des extraits et leurs URL/empreintes sont dans `sources/`.
Ces trois lectures sont ciblées ; aucune n'est une revue intégrale du dépôt.

## Licences vérifiées et versions examinées

Les liens suivants ouvrent les **métadonnées locales du commit exact**, puis
`license_url` donne la source primaire et `license_sha256` son empreinte.
Les licences ont été lues ; sauf mention ci-dessus, le moteur de la bibliothèque
n'a pas été audité ni exécuté. Un paquet installé n'est pas identifié par le
HEAD récolté : la version d'expérience figure dans `requirements.lock`.

| Projet | Licence du dépôt à la version examinée | Source primaire figée |
|---|---|---|
| skfolio | BSD 3 clauses | [métadonnées](sources/code/skfolio__skfolio/metadata.json) |
| Riskfolio-Lib | BSD 3 clauses | [métadonnées](sources/code/dcajasn__Riskfolio-Lib/metadata.json) |
| PyPortfolioOpt | MIT | [métadonnées](sources/code/pyportfolio__pyportfolioopt/metadata.json) |
| CVXPY | Apache 2.0 | [métadonnées](sources/code/cvxpy__cvxpy/metadata.json) |
| HiGHS | MIT | [métadonnées](sources/code/ERGO-Code__HiGHS/metadata.json) |
| Pyomo | BSD 3 clauses | [métadonnées](sources/code/Pyomo__pyomo/metadata.json) |
| OR-Tools | Apache 2.0 | [métadonnées](sources/code/google__or-tools/metadata.json) |
| SciPy | BSD 3 clauses, avec avis tiers à vérifier pour la distribution | [métadonnées](sources/code/scipy__scipy/metadata.json) |
| arch | University of Illinois/NCSA, texte avec attribution, conditions de redistribution et non-endorsement | [métadonnées](sources/code/bashtage__arch/metadata.json) |
| QuantStats | Apache 2.0 | [métadonnées](sources/code/ranaroussi__quantstats/metadata.json) |
| empyrical-reloaded | Apache 2.0 | [métadonnées](sources/code/stefan-jansen__empyrical-reloaded/metadata.json) |
| EMA Workbench | BSD 3 clauses | [métadonnées](sources/code/quaquel__EMAworkbench/metadata.json) |
| pymcdm | MIT | [métadonnées](sources/code/kotbaton__pymcdm/metadata.json) |
| pymoo | Apache 2.0 | [métadonnées](sources/code/anyoptimization__pymoo/metadata.json) |
| cvxportfolio | GPL version 3 | [métadonnées](sources/code/cvxgrp__cvxportfolio/metadata.json) |
| bt | MIT | [métadonnées](sources/code/pmorissette__bt/metadata.json) |
| vectorbt | Apache 2.0 **avec Commons Clause 1.0** | [métadonnées](sources/code/polakowo__vectorbt/metadata.json) |
| pyDecision | GPL version 3 ou ultérieure, mention explicite du projet | [métadonnées](sources/code/Valdecy__pyDecision/metadata.json) |
| pypbo | AGPL version 3 | [métadonnées](sources/code/esvhd__pypbo/metadata.json) |
| DiCE | MIT | [métadonnées](sources/code/interpretml__DiCE/metadata.json) |
| marimo | Apache 2.0 | [métadonnées](sources/code/marimo-team__marimo/metadata.json) |
| ggdist | Texte GPL version 3 présent ; déclaration de portée complète du paquet R à revérifier avant livraison | [métadonnées](sources/code/mjskay__ggdist/metadata.json) |

La GPL autorise l'exécution du programme ; la distribution d'un travail couvert
déclenche des obligations de licence/source. L'AGPL ajoute notamment une obligation
d'offre de source pour certaines versions modifiées utilisées via un réseau
(§13). Leur compatibilité se juge sur l'usage et la livraison envisagés, pas sur
une interdiction générale de recherche ou d'utilisation commerciale.

Commons Clause définit ici une restriction de vente incluant certains services
d'hébergement/support dont la valeur provient substantiellement du logiciel.
Ce n'est pas « Apache standard ». Le texte BSL du serveur lakeFS U305 est encore
un autre régime ; le registre en garde la version et les limites de lecture.
Ces observations documentaires ne remplacent pas l'examen du produit livré.

DiCE, marimo et ggdist servent éventuellement l'interaction/restitution ; leurs
algorithmes ne résolvent pas le besoin financier à la place d'Agent0/Agent2.
skfolio et Riskfolio restent des candidats comparables : richesse du catalogue
ou API pratique ne suffit pas à les sélectionner. Pour QuantStats/empyrical,
vérifier indépendamment annualisation, rendement excessif, drawdown avec flux
et calendrier avant de publier leurs métriques.

## Journal d'exécution

Exécuté une fois dans l'environnement isolé : GMV de référence, ES fractionnaire,
LP Robert, diagnostics IIS, simulation du maximum de Sharpe, covariance et
stabilité sur données du starter. Scripts et résultats conservés dans
`experiences/`. La correction d'un commentaire n'a pas entraîné de nouveaux
résultats.

Lu mais non exécuté : sources partielles PyPortfolioOpt/cvxportfolio/HiGHS,
notebook N01 et textes primaires répertoriés. Les contrôles Valet/FRED/SEC portent
sur les réponses effectivement obtenues ; aucune cellule d'inférence ni
d'acquisition yfinance du notebook n'a été lancée.

Non réalisé : adoption d'une bibliothèque en production, optimisation dynamique,
DRO, comparaison après coûts, ESG agrégé, reproduction complète d'un papier,
validation prospective ou inférence LLM supplémentaire.
