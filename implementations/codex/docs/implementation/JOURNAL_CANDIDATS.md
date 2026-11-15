# Admission des implémentations — construction Prompt 4

## Qualification complémentaire — Prompt 5

La [revue indépendante](../defense/README.md) confirme les calculs examinés,
avec les restrictions suivantes :

- J02/J04 : sources de demande immuables, ancrage français borné et rejet
  des booléens numériques ; révision libre réellement testée.
- J07 : certificat budgétaire algébrique séparé, garde explicite, aucune
  relaxation ; routage revu indépendamment et quatre rôles exécutés sur AWS.
- J10 : redistribution et fenêtre historiques déclarées dans un objet typé,
  sinon clarification/refus ; méthode v2. Oracle CSV indépendant.
- J13/J14 : retrait corrigé sans perdre le capital, branches indépendantes
  réutilisées et conclusions invalidées ; contrôles de reprise conservés.
- J15/J16 : conflits matériels non résolus bloquants, pièces consultées
  séparées des citations retenues, contrôle arithmétique fondé sur les checks.
  L'implication logique de chaque citation reste non certifiée.
- J17 : questions regroupées sans perdre les formulations distinctes,
  observations documentaires datées avant calcul, preuves réelles consultées.

La référence simple et le bras sans LLM reproduisent les résultats numériques
des problèmes formalisés : aucune supériorité de rendement n'est attribuée à
l'orchestration. Les admissions historiques ci-dessous ne sont pas effacées.

## Admissions initiales

Ce journal prolonge celui du [Prompt 2](../recherche/03_journal_candidats.md).
Il ne réécrit pas ses niveaux de lecture historiques.

| Candidats d'origine | Problème et source | Adaptation réellement exécutée | Expérience et décision |
|---|---|---|---|
| J01/J18 — collecte sourcée | CFA, principes de revue ; AgentCore InvokeWebSearch et corpus local | Requête et reçus AWS, capture originale hashée, extraction de passages exacts, date de capture séparée de la publication ; sélection critique Agent1 | Recherche réelle et tests des erreurs/dates/domaines. **Admis, borné** : trois résultats et un approfondissement, pas revue exhaustive. |
| J02/J04 — qualification | Cadres professionnels et résultats critiques sur extraction LLM | ProblemSpec, origines par champ, citations, valeurs inconnues, déclarations structurées prioritaires, clarification | Cas d'extraction numérique non ancrée, signe moins et reprises testés. **Admis dans le périmètre**, sans instrument de profil psychométrique. |
| J07 — retrait et faisabilité | Boyd/Vandenberghe §4.3, HiGHS, conception Robert | SciPy `linprog` sur demi-L1, réserve abstraite explicite, plafonds initiaux, budget de perte sous chocs | Bornes, primal-dual, optima multiples et cas infaisables. Robert réel 30→40. **Admis**. L'IIS général reste reporté. |
| J10 — données admissibles | Données starter, documentation de change/ajustements, moteur historique existant | Inspection réelle Agent1 et contre-vérification des hashes/dates Agent2 ; CAD, as-of, capture antérieure exigée | Données acquises en 2026 refusées pour une décision de 2020 ; divergences hash/date injectées. **Admis** pour description historique, pas simulation point-in-time. |
| J13 — « et si » contrôlé | Motif OptiGuide, corrigé par lecture de son code au Prompt 2 | Paramètres typés et outils fixes ; révision du dossier et sondages de sensibilité | Retrait 30→40, retour 40→30, capital modifié, maintien des branches indépendantes. **Admis sans génération de code**. |
| J14 — graphe/reprise | LangGraph/Strands, documentation et inspection du Prompt 2 | LangGraph 1.2.22, SQLiteSaver 3.1.3 ; métier séparé des checkpoints | Panne avant/après commit, réouverture, attente, conflit, deux opérations concurrentes. **LangGraph admis** ; Strands non exécuté ici et reporté. |
| J15 — registre/vérification | CRITIC, AIS/ALCE, contrats de conception | Claims calculés, pointeurs exacts, droits d'écriture, cinq contrôles distincts | Refus d'une écriture hors rôle, pointeurs vérifiés, fidélité textuelle comparée. **Admis**, aucune garantie d'exactitude financière globale. |
| J17 — restitution | Principes IPDAS/interaction, conception validée | Comparaison même unité, preuves accessibles, correction simple, historique et erreurs visibles | Robert via UI et AWS ; Amira réelle ; bureau/mobile, export, réponse périmée et coupure réseau. **Parcours admis**, pas preuve utilisateur de meilleure décision. |
| J05/J06/J08/J09/J11 | Covariance, allocateurs, CVaR optimisée, objectifs, ESG | Aucune de ces familles ajoutée artificiellement aux deux problèmes initiaux | **Reportées** jusqu'à question justifiant ces méthodes, données admissibles et expérience spécifique. Les sources et expériences isolées du Prompt 2 restent disponibles. |
| J16 — documents non fiables | CaMeL/AgentDojo, motifs du Prompt 2 | Contenus non fiables, extraction bornée, routes/permissions imposées hors du modèle | **Partiel** : protections techniques testées, pas de banc financier complet contre attaques adaptatives. |

Les versions et reçus sont dans `proofs/`, les hypothèses exactes dans
[finance.md](finance.md), les limites réseau dans [aws_runtime.md](aws_runtime.md).
Les tests déterministes, revues indépendantes et exécutions AWS sont des
preuves séparées. Le coût des modèles n'est pas estimé à partir des anciens
prix du dossier fourni : les usages sont enregistrés, la facture n'a pas été
réconciliée.
