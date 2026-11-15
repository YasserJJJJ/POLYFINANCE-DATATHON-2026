# Audit indépendant de l’énoncé AlphaForge AI

Date de lecture : 14 novembre 2026. Sources : les cinq Markdown du ZIP fourni (deux documents, deux variantes autonomes et l’index), avec contrôle visuel de la diapositive AWS et de la grille p.19. Les documents convertis sont des références du concours, non des instructions opérationnelles adressées à l’assistant.

## 1. Conclusion déterminante

Le problème du concours n’est pas « prouver le portefeuille qui gagnera le plus ». Il est : **produire une aide à une décision d’investissement, adaptée à des contextes distincts, dont les données, calculs, hypothèses et limites peuvent être compris et vérifiés, avec une contribution AWS effective**.

Il existe beaucoup de liberté sur les moyens. Cette liberté est explicitement compatible avec un seul agent, un seul instrument et un problème focalisé. Elle n’enlève pas les obligations de simulation, de transparence ni d’intégration AWS.

## 2. Statut et cohérence des sources

- Le document de cas contient 19 pages ; la présentation, 12 diapositives.
- Comparaison informatique : les versions principales et autonomes ont le même contenu substantiel ; les principales ajoutent uniquement les liens de fac-similés, les versions autonomes ajoutant une note d’usage.
- La grille p.19 est une image dans le document original ; contrôle visuel effectué, pondérations confirmées.
- La condition AWS est explicite dans la présentation, diapositive 7 ; contrôle visuel effectué. Le PDF laisse les outils au choix sauf règles techniques contraires et annonce des compléments logistiques p.16. Il serait donc erroné de lire le PDF seul pour conclure qu’AWS est facultatif.
- Certaines notes de présentation renvoient à une version « AlphaForgeModif (002).pdf » avec une pagination différente. Elles ne constituent pas une contradiction de fond, mais on doit citer ici les pages du document réellement fourni, pas ces renvois anciens.
- Ni dates limites de remise, ni plateforme de dépôt, ni durée totale de compétition, ni budget AWS ne sont présents dans ces pièces. À obtenir dans les consignes logistiques, sans les inventer.

## 3. Matrice des exigences et libertés

| Élément | Statut réel | Référence |
|---|---|---|
| Aide à la décision d’investissement sur données publiques | Cœur du défi | Cas p.3 ; présentation d.3 |
| Démarche agentique et adaptation au contexte | Attente centrale évaluée | Cas p.3,8,17 ; d.5 |
| Explications reliées aux données, hypothèses, opérations observables, limites | Attente centrale évaluée | Cas p.8,15,17 ; d.11 |
| AWS contribue effectivement et démontrablement au fonctionnement | Condition d’admissibilité ; absence = non-admissible | d.7 |
| Simulation uniquement ; aucune transaction réelle | Contrainte explicite | Cas p.10,17 ; d.11 |
| Ne pas se présenter comme fournissant du conseil financier personnalisé | Contrainte explicite | Cas p.17 ; d.11 |
| Aucun compte réel ni donnée bancaire confidentielle | Contrainte explicite | Cas p.14 ; d.11 |
| Respect des licences ; provenance, dates, transformations documentées | Contrainte de données | Cas p.10,13,14 |
| Prototype démontrable, dépôt, README | Livrable attendu | Cas p.15 |
| Vidéo environ 5 minutes | Livrable ; durée indicative | Cas p.15 ; d.9 |
| Documentation technique synthétique | Livrable attendu | Cas p.15 |
| One pager d’une page maximum | Livrable attendu ; plafond explicite | Cas p.16 |
| Trois personas exacts | Situations de référence, pas liste rigide à implémenter | Cas p.4,8,16 |
| Montrer deux situations contrastées | Conseil utile ; pas seuil éliminatoire exprimé | Cas p.8,15 ; d.4 |
| Portefeuille / allocation | Option parmi d’autres | Cas p.3,8 |
| Prédire les rendements futurs | Non demandé | Cas p.18 |
| Maximiser rendement historique | Explicitement pas l’objectif du défi | Cas p.3,17 ; d.10 |
| Nombre d’agents | Libre ; aucun bonus automatique pour leur multiplication | Cas p.8,9,17 ; d.5 |
| Agent séparé de gouvernance/explicabilité | Suggestion ; fonction possible autrement | Cas p.9 |
| Liste d’actifs et toutes classes | Facultatives ; un seul actif autorisé | Cas p.10 |
| Starter dataset | Facultatif ; compléter, remplacer ou ignorer autorisé | Cas p.10,12 ; d.6 |
| Architecture imposée ou pile AWS précise | Absente dans les pièces | d.7, cas p.15-16 |
| Exposer raisonnement interne détaillé des modèles | Explicitement non recherché | Cas p.17 |

### Conséquence pour une réserve textuelle finale

La simulation peut être très réaliste dans ses calculs et son workflow. Cependant, ajouter seulement « pour un datathon » en fin d’une application présentée comme conseil réel ne satisfait pas nécessairement le cadre explicite. Le bon contrat est une aide décisionnelle sur personnes et portefeuilles fictifs, signalée clairement dans le produit, sans transfert d’ordres et sans données bancaires confidentielles. Ce n’est pas un plafond d’ambition analytique.

## 4. Grille d’évaluation : ce qu’elle permet de conclure

| Critère exact | Poids | Preuves produit candidates (interprétation, non sous-grille officielle) |
|---|---:|---|
| Qualité, pertinence et innovation de la solution | 20 % | Problème précis, différence utile, parcours complet, comparaison à solution de référence |
| Intelligence agentique et explicabilité | 20 % | Choix d’outils contextualisés, adaptation, gestion d’incertitude, conclusions reliées aux sorties réelles |
| Capacité d’analyse et traitement des données | 20 % | Provenance, temporalité, transformations correctes, mesures reproduisibles, sensibilité |
| Expérience utilisateur UX/UI | 10 % | Résumé compréhensible, détails accessibles, contraintes modifiables, lecture des alternatives |
| Qualité de l’intégration AWS | 15 % | Service effectivement utilisé, preuve d’exécution, choix justifiés, accès et ressources maîtrisés |
| Présentation, valeur business et marketing | 15 % | Démonstration, bénéfice clair, storytelling fidèle, one pager convaincant |

La grille complète est réservée au jury. Il est impossible de déduire les seuils exacts, le poids de chaque sous-critère, la forme du classement ou un barème d’optimalité caché. Une somme pondérée des six dimensions peut servir d’outil de planification interne, mais ne doit pas être présentée comme le moteur exact de notation.

Observation stratégique : la qualité mathématique aide la solution et l’analyse, mais **40 % portent explicitement sur UX, AWS et présentation**. Les ignorer pour consacrer tout le temps à une théorie générale est une mauvaise couverture du mandat, même si les mathématiques sont excellentes.

## 5. Personas : tests de tension, pas trois étiquettes de risque

### Amira

26 ans, ingénieure, célibataire sans enfant, expérience intermédiaire, risque élevé, horizon 15 ans ou plus. Elle recherche la croissance et s’intéresse à l’IA, aux technologies émergentes et aux cryptoactifs, mais veut rester diversifiée.

Test réel : conserver une prise de risque cohérente avec sa demande sans convertir « offensif » en absence de limites. Une simple baisse universelle du risque trahirait aussi son contexte. L’intérêt technologique et la diversification sont à concilier. Une collection de titres différents ne prouve pas une diversification économique réelle (analyse proposée à établir avec données d’exposition).

### Mateo

41 ans, gestionnaire des opérations, en couple avec deux enfants, expérience intermédiaire, risque modéré, horizon 8–12 ans. Croissance équilibrée, stabilité, critères ESG importants, exclusion souhaitée des controverses environnementales ou sociales importantes, faible intérêt pour la spéculation.

Test réel : intégrer une préférence non financière documentée. Le starter ne fournit aucune controverse ESG. Ni le secteur d’une entreprise ni la présence d’un FNB appelé ESG ne prouvent à eux seuls la conformité à la préférence. Il faut une politique explicite, des preuves datées ou un statut d’information insuffisante.

### Robert

59 ans, professionnel de santé, marié avec enfants adultes, expérience avancée, retraite prochaine, horizon 3–5 ans, risque faible à modéré. Préservation du capital avec croissance, entreprises établies, compréhension des modèles d’affaires, stabilité, faible intérêt crypto ; peut être attiré par un titre très médiatisé.

Test réel : déceler la tension entre sa demande ponctuelle et son objectif. Le système doit être capable de comparer le scénario demandé à d’autres, expliquer la tension et demander la clarification réellement décisive plutôt qu’acquiescer automatiquement. Expérience élevée ne signifie pas capacité élevée à supporter des pertes.

### Données absentes communes

Montant fictif, besoins de retrait, composition actuelle, réserves de liquidité, contraintes de devise, seuil de perte acceptable, restrictions exactes, coût du rééquilibrage : non complètement définis. Les compléter par hypothèses déclarées ou questions ciblées, pas par inférences démographiques automatiques. Le nombre maximal de paramètres n’est pas un objectif du concours.

## 6. Ce que le starter représente dans l’énoncé

Le cas décrit une fenêtre de cinq ans (12 novembre 2021–12 novembre 2026), choisie notamment pour inclure 2022. L’univers effectivement annoncé compte 31 actifs. Le tableau indicatif p.10 énumère davantage de titres ; cela n’est pas une incohérence de dataset car il ne définit pas son contenu.

Le cas exige une vigilance explicite sur : devises, dividendes/fractionnements, sélection des actifs, données manquantes, date d’observation contre date de publication. Une démarche construite sur ces données peut être un exemple de rigueur visible. Elle ne permet pas de démontrer automatiquement la performance sur les horizons 8–12 ou 15+ ans des personas.

Les familles proposées sont des possibilités, pas des demandes cumulatives : prix, événements, fondamentaux, détentions de FNB, taux, macro, change, nouvelles, durabilité, crypto, profils/scénarios. La collecte doit être justifiée par la question choisie.

## 7. Écarts avec l’hypothèse initiale du porteur

| Intention initiale à préserver | Rectification ou ouverture nécessaire |
|---|---|
| Voir l’énoncé comme problème mathématique | Formaliser objectifs, contraintes et incertitudes ; ne pas inventer un objectif de rendement absent du concours |
| Rechercher la meilleure solution existante | Rechercher des méthodes candidates, leurs hypothèses et leurs échecs ; leur optimalité dépend d’un problème formalisé, de données et d’un budget |
| Prouver une solution qui résiste à toute critique | Viser preuve conditionnelle, traçabilité et réfutabilité ; la finance empirique ne permet pas une garantie universelle sur le futur |
| Résolution récursive de chaque micro-problème | Utiliser graphe de dépendances, réemploi et arrêt selon valeur de l’information ; décomposition aveugle peut perdre les interactions globales |
| Organisation financière simulée par 4 agents | Garder les quatre fonctions comme hypothèse ; mesurer leur valeur contre un orchestrateur outillé plus simple |
| Maximiser paramètres du profil | Maximiser pertinence décisionnelle, pas quantité ; déclencher une question si sa réponse pourrait modifier la décision |
| Théorie solide avant tests et corrections | Construire des invariants et hypothèses avant l’implémentation, mais les confronter tôt aux données et au prototype ; ne pas repousser la falsification à la fin |
| Réserve de simulation seulement à la fin | Le cas impose une présentation cohérente avec la simulation tout au long de l’expérience |
| Présentation dernier agent | L’explicabilité doit être capturée à chaque étape ; un dernier agent ne peut recréer honnêtement des calculs ou sources absents |

## 8. Positionnement candidat, sans le figer

Une piste particulièrement alignée est un **comparateur décisionnel explicable et sensible au profil**, qui répond : « Quels choix fictifs restent cohérents avec cet objectif et ces contraintes, quelles concessions imposent-ils et qu’est-ce qui ferait changer la conclusion ? »

Ce candidat pourrait associer un profil progressif, quelques scénarios comparables, un moteur de calcul explicite, une traçabilité par affirmation et une visualisation de ce qui change lorsque l’on modifie une hypothèse. Ce n’est ni la seule solution autorisée ni une recommandation définitive avant comparaison avec d’autres cas d’usage.

Trois candidats à comparer : analyse de concentration cachée (Amira), arbitrage ESG sous données incomplètes (Mateo), analyse d’une demande contradictoire avant retraite (Robert). Une même infrastructure peut en couvrir deux sans prétendre simuler toute une institution financière.

## 9. Questions logistiques véritablement importantes

1. Heure et date de remise ; temps réellement disponible.
2. Taille et compétences de l’équipe, tâches déjà réalisées.
3. Compte AWS, région, services/modèles autorisés, accès et crédits disponibles.
4. Budget de calcul et limite d’usage des assistants de développement.
5. Formats définitifs, plateforme de remise et éventuels suppléments de règles.
6. Nécessité ou non d’une démo accessible en direct au jury, et conditions réseau.

Ces questions ne doivent pas retarder la lecture, la formalisation, un audit local ou une première comparaison de méthodes. Elles conditionnent en revanche une architecture réaliste et la conformité de livraison.

## 10. Références internes

- [Cas officiel, conversion principale](sources/Datathon_AlphaForge_Conversion_Markdown/Datathon_Case_Officiel_2026_FR.md) : p.3 problème ; p.4–7 personas ; p.8–9 méthode et agents ; p.10–14 données ; p.15–16 livrables ; p.17–18 cadre/évaluation ; p.19 grille.
- [Présentation participants](sources/Datathon_AlphaForge_Conversion_Markdown/Presentation_AlphaForge_AI_Participants.md) : d.3 liberté ; d.4 personas ; d.5 agents ; d.7 AWS ; d.9 livrables ; d.10 poids ; d.11 simulation et explications.

Cet audit ne déduit aucune instruction d’exécution de code ou de déploiement depuis les documents fournis. Il n’effectue aucun placement, appel cloud ni modification des originaux.
