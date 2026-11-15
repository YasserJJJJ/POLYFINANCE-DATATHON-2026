# Méthode de comparaison AlphaForge

Version `cad-buy-and-hold-v1`, 15 novembre 2026.

Le moteur compare des allocations **fictives initiales** sur un instantané historique commun. Il ne prévoit pas les marchés et ne sélectionne pas le portefeuille au meilleur rendement passé.

## Données et temporalité

Les données viennent du starter des organisateurs, acquis le 13 novembre 2026. Chaque résultat porte les empreintes SHA-256 des fichiers lus, leurs nombres de lignes, leurs sources et la période effectivement utilisée. Le moteur conserve les originaux et ne télécharge rien.

`adj_close` inclut déjà les ajustements de distributions et de splits selon le README du starter. Aucun dividende ni split n’est ajouté une seconde fois. Pour un actif USD, l’indice de rendement total exprimé en CAD est proportionnel à `adj_close × FXUSDCAD`. Le taux utilisé est celui de la date de prix ou, à défaut, la dernière date antérieure. Il est interdit de prendre une observation future. Un report supérieur à sept jours est refusé : c’est un seuil opérationnel d’obsolescence, pas une garantie financière.

La grille reste identique entre candidats : intersection des dates disponibles pour tous les instruments hors crypto du snapshot. Elle contient 1 228 séances dans le jeu fourni. Aucun cours ni rendement n’est imputé. Les cryptoactifs sont eux aussi échantillonnés sur cette grille. Cela rend les comparaisons homogènes mais peut masquer un creux crypto de fin de semaine ; le résultat et l’interface doivent conserver cet avertissement.

La date D désigne une valorisation conventionnelle à **D+1, 00:00 UTC**. La bougie crypto D est alors achevée, les actions ont clôturé, et le taux de change D est normalement publié. La Banque du Canada publie une moyenne indicative, généralement avant 16 h 30 heure de l’Est, avec exceptions possibles. La documentation ne garantit pas une synchronisation transactionnelle des trois marchés et le snapshot ne contient pas les heures réelles de publication.

Il s’agit d’une **relecture rétrospective**, pas d’un backtest réalisable sans connaissance future : l’univers a été sélectionné en 2026, les prix ajustés sont issus du téléchargement de 2026 et aucune histoire de millésimes macro n’est reconstruite. La macro n’entre pas dans ces calculs.

## Calculs

Pour capital initial C, poids initiaux \(w_i\) et séries ajustées en CAD \(P_{i,t}\) :

`V(t) = C × Σ_i w_i × P(i,t) / P(i,0)`.

La somme des poids doit être égale à 1, avec positions positives ou nulles, sans levier. Les poids sont des fractions (0,25), jamais des pourcentages implicitement normalisés (25). Ce choix est le domaine de calcul de ce prototype, pas une règle universelle de placement.

Cette stratégie conserve les positions ; les distributions sont réinvesties dans le même instrument. Les poids dérivent avec les rendements. Il n’y a pas de rééquilibrage quotidien, de versements ou retraits, de frais de change/transaction ni d’impôts. Les frais internes d’un FNB sont déjà reflétés dans ses cours.

- Rendement cumulé : `V(fin)/V(début) − 1`.
- CAGR : `(V(fin)/V(début))^(365,2425/jours écoulés) − 1`.
- Drawdown à t : `V(t)/max(V(0)…V(t)) − 1`. Le minimum est négatif ou nul ; il mesure un creux observé sur la grille et ne borne jamais une perte future.
- Volatilité annualisée : écart-type échantillonnal des rendements simples entre observations, multiplié par `sqrt(nombre d’intervalles/années écoulées)`. Le moteur ne mélange pas arbitrairement 252 et 365. Cette annualisation reste une convention qui suppose des intervalles comparables et une mise à l’échelle en racine du temps ; les intervalles des week-ends/jours fériés sont inégaux.
- Perte moyenne de la queue historique à 95 % : moyenne opposée des 5 % plus faibles rendements entre observations, avec poids fractionnaire à la frontière empirique. Ce n’est ni une prévision de CVaR quotidienne ni une estimation sur l’horizon personnel.
- Concentration : poids et indice HHI des **instruments détenus**. Les parts de devise sont les devises de cotation ; ni le risque économique de change ni le chevauchement réel des compositions de FNB ne sont inférés.

Les fenêtres 2022, mars 2023 et douze derniers mois disponibles sont déclarées dans le code. Chaque scénario réinitialise les mêmes poids à son début et indique les dates réellement retenues. Elles ne reçoivent aucune probabilité future. Une fenêtre en dehors de la période demandée est omise.

## Choix de méthode et alternatives

Le premier besoin est d’isoler une décision compréhensible : augmenter ou diminuer la part initiale d’un instrument, en redistribuant le reste proportionnellement. La transformation est exacte : `w_j'=(1−c)w_j/(1−w_focus)` pour les autres instruments. Elle préserve le budget et leurs proportions relatives. Si aucun autre actif n’est disponible pour recevoir le solde, la requête est refusée plutôt qu’inventer une destination.

| Méthode | Apport | Limite et décision actuelle |
| --- | --- | --- |
| Allocations explicites et comparaison de sensibilité | Les préférences et variations sont visibles ; aucune moyenne future n’est estimée. | Retenue pour le prototype. Les poids proposés restent des scénarios, pas des allocations optimales. |
| Optimisation moyenne–variance avec paramètres estimés | Formalisation efficace si objectif, préférences et paramètres pertinents sont connus. | Non retenue au premier parcours : un optimum de l’échantillon ne résout ni l’estimation ni l’horizon du client. |
| Covariance régularisée ou optimisation robuste | Peut réduire une fragilité d’estimation ou contrôler un ensemble d’incertitudes explicite. | À évaluer seulement avec un jeu de scénarios motivé, des contraintes explicites et une comparaison hors échantillon. Aucun bénéfice mesuré n’est revendiqué ici. |
| 1/N sur un univers explicite | Référence simple sans estimation de rendement attendu. | Utile comme candidat comparable si elle respecte les mêmes contraintes ; pas de supériorité universelle revendiquée. |

Les calculs ne transforment pas une préférence de risque, un âge ou une tolérance de perte en coefficient arbitraire. Ils n’affichent aucune « probabilité de réussite » inventée. Les garanties sont conditionnelles : budget respecté, calcul reproductible sur le snapshot, conversion et formule correctement appliquées.

## Références et niveau de lecture

1. Organisateurs, `alphaforge_starter/README.md` et `sources_metadata.csv`, acquisition déclarée 2026-11-13. Lus pour les conventions d’ajustement, devises, calendriers et limites de l’univers.
2. Banque du Canada, [Background information on foreign exchange rates](https://www.bankofcanada.ca/rates/exchange/background-information-on-foreign-exchange-rates/), consulté le 2026-11-15. Sections Publication details et Calculation methodology lues. Les taux sont des CAD par unité étrangère, indicatifs et non transactionnels.
3. DeMiguel, Garlappi et Uppal, « Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy? », *Review of Financial Studies* 22(5), 2009, 1915–1953, [DOI 10.1093/rfs/hhm075](https://doi.org/10.1093/rfs/hhm075). Référence et résumé repérés ; texte publié non accessible par le lecteur utilisé. Elle motive un benchmark simple et une évaluation hors échantillon, sans transférer une conclusion de performance à notre univers.

## Validation

`python -m unittest discover -s tests -p test_analytics.py` vérifie avec des données artificielles indépendantes :

- conversion FX multiplicative et absence de regard vers le futur ;
- achat-conservation avec dérive réelle des poids ;
- CAGR géométrique sur un aller-retour +100 %/−50 % ;
- drawdown depuis le sommet courant ;
- conservation du budget et des proportions lors d’un changement de poids ;
- queue empirique avec frontière fractionnaire ;
- refus des symboles inconnus, poids négatifs, non finis ou mal normalisés ;
- grille partagée et invariance des rendements à l’échelle du capital.

Ces tests établissent des propriétés du moteur, pas la qualité financière des données fournisseur ni une performance future.
