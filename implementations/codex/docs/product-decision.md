# Décision de produit AlphaForge

15 novembre 2026 — statut : choix implémenté pour le prototype, à réviser après essai utilisateur.

## Question retenue

**Que change une modification explicite de mon exposition, et quelles preuves permettent de comprendre ce changement ?**

Le parcours compare une allocation de référence et une variante calculée sur les mêmes données. L’utilisateur change un poids ; les autres positions sont redistribuées proportionnellement. Il observe les montants, risques historiques, scénarios et limites. L’agent peut qualifier la demande et sélectionner les outils et références pertinents. Les valeurs numériques restent produites par le moteur.

Ce choix répond au cas officiel : aide à la décision adaptée aux profils et auto-explicative, avec moyens libres. Le concours ne demande pas le portefeuille gagnant d’un backtest. Le choix actuel n’est pas présenté comme une victoire expérimentale sur toutes les autres directions.

## Alternatives considérées

| Candidat | Bénéfice distinctif | Preuve/data nécessaire | Décision présente et condition de réouverture |
| --- | --- | --- | --- |
| **A — Comparateur d’adéquation et de compromis** | Une modification de préférence ou d’exposition produit une différence calculable et explicable. | Série ajustée, devise commune, hypothèses explicites, sources et mesure du changement. | **Retenu.** Les données présentes suffisent à un parcours complet. À réviser si les essais montrent que la comparaison ne répond pas à une vraie question utilisateur. |
| **B — Diversification cachée** | Détecter les mêmes entreprises derrière actions et FNB. | Compositions détaillées et datées des fonds, règle de rapprochement des émetteurs. | **Réservé.** Les poids de tickers ne mesurent pas le chevauchement économique. À rouvrir lorsque des compositions utilisables et datées sont obtenues. |
| **C — Recherche ESG et couverture des preuves** | Mettre en regard exclusions personnelles, sources et faits établis/contestés/inconnus. | Définition d’exclusion et preuves datées de politiques, holdings et controverses. | **Partiellement couvert comme détection des limites.** Retirer XOM est un changement d’exposition directe, pas une certification ESG. À approfondir avec un corpus adapté aux exclusions réellement demandées. |
| **D — Allocation robuste sous contraintes** | Étudier des compromis calculés sous un ensemble explicite de scénarios/incertitudes. | Préférences et contraintes justifiées, estimation, scénarios, validation numérique et comparaison hors échantillon. | **Réservé.** Les familles covariance régularisée, moyenne–variance et CVaR ont été repérées ; aucun solveur robuste ni bénéfice empirique n’est revendiqué dans ce prototype. À rouvrir si l’utilisateur demande une allocation et si les hypothèses deviennent défendables. |

Une simple comparaison de poids n’est pas rebaptisée « optimisation robuste ». Elle fournit une référence transparente à laquelle comparer ultérieurement une méthode plus complexe.

## Ce qui rend le résultat vérifiable

- Deux allocations passent par la même formule d’achat-conservation, la même grille de dates et le même instantané.
- Le changement de poids préserve le budget et les proportions relatives des autres positions ; aucune allocation n’est déduite de l’âge.
- Les avoirs, capitaux et repères de perte des trois démonstrations sont **ajoutés par AlphaForge**. Ils sont présentés comme hypothèses modifiables, jamais comme informations des personas officiels.
- Le drawdown est une baisse observée et négative dans l’API. Le seuil de confort est comparé à sa valeur absolue ; modifier ce seuil ne modifie pas les prix.
- Le profil peut changer la question et l’interprétation. Modifier un horizon ne fabrique ni données futures ni probabilité de réussite.
- Un résultat défavorable doit rester visible. Dans l’instantané testé, le retrait de l’exposition directe à XOM du scénario Mateo augmente le drawdown observé ; l’API le dit explicitement.

## État des preuves

Les essais d’API exécutent les trois cas complets, le curseur d’exposition, l’échelle du capital, les erreurs de poids, la perte comparée au seuil et la restitution des sources. Ils excluent les appels LLM afin d’isoler la fidélité financière. Le moteur possède aussi des contrôles numériques sur données artificielles indépendantes.

Les scénarios historiques servent à expliquer les compromis, pas à annoncer une supériorité hors échantillon. Les limites de calendrier, FX, absence de holdings et acquisition tardive sont détaillées dans [methodology.md](methodology.md).

## Sources exactes et niveau de lecture

| Source | Niveau utilisé | Rôle et limite |
| --- | --- | --- |
| [Cas officiel converti, pages 3–8, 15–19](../analyse/sources/Datathon_AlphaForge_Conversion_Markdown/Datathon_Case_Officiel_2026_FR.md) | Passages du défi, personas et évaluation lus ; source fournie par l’utilisateur. | Établit l’objectif et les libertés du concours. |
| [Cadrage v2, §7 et registre des références](../revision_2026-11-15/00_DECORTICAGE_MULTIDIMENSIONNEL.md) | Matrice des quatre candidats, données et garanties lues. | Base de comparaison locale, pas étude utilisateur. |
| Starter, `README.md` et `sources_metadata.csv`, acquisition 2026-11-13 | Conventions lues ; fichiers identifiés par empreintes. | Prix ajustés, devises, biais de sélection ; pas de preuve ESG ou de holdings. |
| [CFA Institute, Basics of Portfolio Planning and Construction, 2026](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/basics-of-portfolio-planning-and-construction) | Introduction, objectifs et synthèse publics lus dans le corpus projet ; chapitre payant non lu. | Séparation objectifs, horizon, liquidité, volonté et capacité de risque. Ne détermine pas les poids de nos personas. |
| [Banque du Canada, Background information on foreign exchange rates](https://www.bankofcanada.ca/rates/exchange/background-information-on-foreign-exchange-rates/) | Sections publication et méthode lues, 2026-11-15. | Taux indicatifs CAD par unité étrangère, publication généralement avant 16 h 30 ET. |
| [FRED, Real-Time Periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html) | Documentation lue dans le corpus projet. | Distingue observation et connaissance ; aucun vintage macro reconstruit ici. |
| [Ledoit et Wolf, Honey, I Shrunk the Sample Covariance Matrix](https://ledoit.net/honey.pdf) | Résumé du manuscrit des auteurs repéré dans le cadrage initial ; résultats non reproduits. | Alternative de régularisation à évaluer si une covariance estimée devient nécessaire. |
| [Rockafellar et Uryasev, Optimization of Conditional Value-at-Risk, 2000](https://doi.org/10.21314/JOR.2000.038) | Référence et [bibliographie auteur](https://uryasev.github.io/publications/) repérées dans le cadrage ; texte non intégralement analysé pour ce prototype. | Famille d’optimisation à approfondir. L’ES empirique descriptif affiché par le moteur n’est pas un solveur CVaR. |
| [DeMiguel, Garlappi et Uppal, Optimal Versus Naive Diversification, 2009](https://doi.org/10.1093/rfs/hhm075) | Référence et résumé repérés ; texte publié non accessible via le lecteur utilisé. | Motive une référence simple et une validation hors échantillon, sans prétendre que 1/N domine toujours. |

Les références repérées restent des pistes. Elles ne sont pas comptées comme méthodes testées, résultats reproduits ou lectures intégrales.
