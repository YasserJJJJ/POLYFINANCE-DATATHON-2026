# AlphaForge — Diagnostic et contrat de refonte proposé

15 novembre 2026. **Proposition soumise à validation ; aucune refonte du produit engagée.**

Le prototype actuel est un comparateur financier réel, accompagné d'une restitution agentique limitée. Il ne réalise pas encore l'organisation intellectuelle demandée. Son principal défaut est d'avoir fait d'une méthode de comparaison disponible la définition du produit, avant de construire la qualification, la recherche, la résolution argumentée et la révision.

Une partie de la rigueur numérique existe. La profondeur scientifique et le fonctionnement des quatre agents restent à construire. Il faut conserver la première et rendre les seconds exécutables.

## 1. Périmètre de l'examen et préservation

L'examen porte sur le mandat original du 14 novembre, le cadrage révisé du 15 novembre, l'atlas des ressources, les décisions documentées, le code du produit, ses contrôles financiers et les traces conservées. Il ne constitue pas une nouvelle revue intégrale des 36 PDF ou de toutes les publications signalées dans ces documents.

Références principales :

- [Mandat original](../../02_CONTEXTE_ET_MANDAT_DE_LANCEMENT_CLAUDE_CODE.md), notamment lignes 15–34, 119–149 et 159–206.
- [Vision initiale révisée](../../revision_2026-11-15/01_VISION_INITIALE_PROFIL_ET_ARCHITECTURE_OUVERTE.md), notamment lignes 23–47, 127–168, 199–213 et 348–361.
- [Mandat intégré AWS](../../revision_2026-11-15/02_MANDAT_INTEGRE_ORCHESTRATEUR_AWS.md), notamment lignes 115–127, 159–184, 196–243 et 261–287.
- [Atlas et plan d'exploitation](../../revision_2026-11-15/00B_ATLAS_DES_RESSOURCES_ET_PLAN_EXPLOITATION.md), notamment lignes 61–110.
- [Décision de produit](../product-decision.md), [méthodologie](../methodology.md), [références](../references.md), [choix d'expérience](../ux-decisions.md) et [validation financière](../validation-finance.md).

État de référence : commit `bce93c5e806f8421cac62795410b30f9ad1557ae`. Le code, les données, les rapports existants, le service local et les livrables précédents sont conservés. La sauvegarde existante `artifacts/AlphaForge_local_2026-11-15.zip` n'est pas remplacée.

Les seules additions de cette étape sont ce diagnostic, un [script d'inspection](inspection_diagnostic.py) et ses [résultats](inspection_diagnostic.json). Les appels API de contrôle ont utilisé un processus isolé et un dossier temporaire supprimé, sans appeler Bedrock ni écrire dans les rapports du produit. Le contrôle par empreintes porte sur les onze fichiers préexistants d'`alphaforge_app`, hors `__pycache__` : ils sont identiques avant et après. Ce contrôle ne constitue pas une vérification globale des données, archives ou services ; aucune opération de modification n'a été engagée sur ces éléments.

**Évolution du mandat :** les textes précédents autorisaient une réorganisation, y compris une fusion des rôles, sous réserve de justifier une meilleure réponse au besoin. Le défaut historique n'est donc pas simplement d'avoir utilisé un seul agent. C'est de n'avoir ni assuré les fonctions attendues autrement, ni démontré que leur réduction répondait mieux à l'objectif. La nouvelle instruction impose désormais les quatre rôles Agent 0–3 ; toute suppression, fusion ou substitution requiert une proposition et l'accord du porteur.

## 2. Ce que le produit exécute

Le parcours actuel est le suivant :

1. Un formulaire reçoit un persona, un portefeuille, une demande libre et quelques réglages.
2. Le serveur complète les valeurs depuis le persona et calcule immédiatement deux allocations.
3. La variante impose un nouveau poids à un instrument et redistribue les autres poids proportionnellement.
4. Si Bedrock est demandé, un agent peut appeler trois fonctions : recalculer cette variante, consulter des fiches et relire le profil déjà constitué.
5. Un nouvel appel de restitution reçoit les résultats ; il génère un texte et sélectionne des observations numériques prédéfinies.
6. Le serveur archive le rapport final. L'interface affiche chiffres, courbes, sources, questions et limites.

Cette chaîne est visible dans [main.py](../../alphaforge_app/main.py), lignes 178–245, et [orchestrator.py](../../alphaforge_app/orchestrator.py), lignes 14–35 et 136–259. Les sous-agents qui ont construit ou audité le logiciel ne sont pas des agents exécutés dans ce parcours.

| Nature | Fonction effectivement présente | Portée exacte |
|---|---|---|
| Opérationnelle | Calcul de richesse historique en CAD, rendement géométrique, volatilité, drawdown, queue empirique, concentration par instruments et fenêtres historiques | Calculs déterministes sur un instantané ; pas de prévision, de financement d'objectif ou d'allocation optimisée |
| Opérationnelle | Appels AWS Bedrock et appels d'outils locaux | Une boucle agentique, puis une restitution ; pas quatre responsabilités dotées de leurs propres dossiers |
| Opérationnelle | Graphiques, modification des poids, recalcul, export du dernier résultat, retour au résultat précédent | Les courbes viennent des données calculées ; les contrôles ne sont pas une animation fictive |
| Simulation de cas | Personnages et portefeuilles de démonstration | Les biographies officielles sont distinguées des avoirs, capitaux et seuils fictifs ajoutés |
| Texte généré | Titre, synthèse qualitative, questions, contradictions éventuelles et conditions de révision | Ces champs ne prouvent pas l'exécution d'une qualification, d'une critique indépendante ou d'une révision |
| Consultation limitée | `read_evidence` sélectionne parmi six fiches Python | Aucune recherche web ni lecture des pages liées pendant la demande |
| Absente | Chaîne de qualification, recherche spécialisée, choix de méthode, débat documenté et révision des dépendances | Aucun ensemble de dossiers intermédiaires matérialisant ces fonctions |

Il n'y a pas de faux découpage visuel en quatre agents dans le prototype. Les états de chargement indiquent une requête en cours. L'ambiguïté vient surtout du sens attribué aux mots « profil », « preuves », « sources lues » ou « révision » au regard des opérations beaucoup plus étroites qui leur correspondent.

### Parcours représentatif inspecté et reproduit

Le [rapport Mateo conservé depuis le navigateur](../../artifacts/ui-export.json), créé à `2026-11-15T12:13:15.141704+00:00`, documente deux appels AWS et les trois outils `compare_scenario`, `read_evidence`, `inspect_profile`. Ce sont des traces d'exécution antérieure, pas une nouvelle exécution des modèles pendant cet audit.

Le moteur a été réexécuté localement avec les paramètres du rapport : **les comparaisons et les scénarios reproduits sont exactement identiques**.

| Mateo, capital fictif de 10 000 CAD | Référence | XOM retiré, autres poids proportionnels |
|---|---:|---:|
| Valeur finale historique | 17 772,24 CAD | 15 804,05 CAD |
| Rendement cumulé | 77,72 % | 58,04 % |
| Perte maximale depuis un sommet observé | 12,68 % | 18,57 % |

Le retrait de XOM satisfait l'exclusion directe, mais détériore ce risque historique. C'est un contre-exemple utile, correctement calculé. Il ne prouve ni qu'une autre allocation admissible n'existe pas, ni que les fonds restants satisfont l'exclusion indirecte ou une préférence ESG plus large.

Deux contrôles ciblés éclairent les fonctions absentes :

- Robert avec horizons structurés de **1, 4 et 15 ans** reçoit les mêmes comparaisons numériques. L'horizon retourné change, mais aucun problème financier dépendant de l'horizon n'est résolu.
- En mode calcul, annoncer un retrait impératif de **3 000 CAD dans douze mois sur 10 000 CAD** ne change pas l'analyse ; le rapport conserve « Besoins de retrait » parmi les inconnues. Un champ structuré `withdrawals` est rejeté par l'API avec le statut 422, car ce concept n'existe pas dans son contrat.

Ce ne sont pas des défauts arithmétiques : ils révèlent le périmètre du produit. Avec Bedrock, le texte peut modifier un ticker ou son poids au moyen de l'outil ; il n'existe cependant aucun outil pour formaliser un flux de retrait et reconstruire l'analyse autour de celui-ci. L'audit ne prétend pas avoir testé une nouvelle réponse générée sur ce cas.

## 3. Écart fonctionnel par agent

| Rôle exigé | Ce qui s'en rapproche actuellement | Ce qui manque |
|---|---|---|
| **Agent 0 — qualification et formalisation** | Champs de formulaire, persona, texte libre ; `inspect_profile` relit l'objet prérempli | Extraction de faits avec provenance, inconnues déterminantes, clarification avant résolution, objectifs, contraintes dures, préférences, questions de recherche et problème formalisé |
| **Agent 1 — recherche et revue de littérature** | Six fiches résumant sources et conventions ; niveaux de lecture annoncés | Recherche adaptée à la demande, documents récupérés, passages précis, comparaison des méthodes, conditions d'application, arguments contradictoires et lacunes |
| **Agent 2 — analyse et résolution** | Un moteur réel et une règle de variante | Plan d'analyse issu du problème et du dossier de preuves, solutions concurrentes, contrôle d'admissibilité, sensibilités, critique et conclusion conditionnelle défendue |
| **Agent 3 — restitution et interaction** | Prose contextualisée, observations chiffrées, courbes et accès aux fiches | Adaptation explicite du niveau d'explication, examen contradictoire, réponses enregistrées aux questions, réouverture d'un dossier et révision traçable |

Les sept observations possibles sont écrites dans [main.py](../../alphaforge_app/main.py), lignes 127–145. Le modèle en sélectionne trois à cinq. Ce dispositif protège les chiffres, mais borne aussi la substance de l'explication. Les questions produites après calcul ne deviennent ni des faits de profil ni des événements de révision.

Le rapport JSON final est une archive utile. Il n'est pas une mémoire de recherche : les résultats intermédiaires des outils ne sont pas tous conservés comme artefacts autonomes et chaque nouvelle variante écrase la précédente dans la réponse en cours. Le navigateur peut échanger deux résultats ; il ne conserve pas la filiation de décisions d'un dossier.

## 4. Décisions qui ont appauvri le projet

| Décision observable | Où elle est établie | Pourquoi elle pose problème à l'échelle du mandat |
|---|---|---|
| Définir le produit par « que change une exposition ? » | [product-decision.md](../product-decision.md), lignes 7–20 | Une sous-question utile devient l'entrée obligatoire. L'utilisateur ne peut plus faire choisir la méthode à partir de son besoin |
| Retenir principalement ce que le starter permet immédiatement | Même fichier, lignes 17–20 ; [references.md](../references.md), ligne 9 | Les données manquantes ont surtout servi à réserver des branches, sans recherche discriminante documentée permettant de décider si les acquérir changerait le produit |
| Calculer avant de qualifier | [main.py](../../alphaforge_app/main.py), lignes 185–198 | Les questions et les tensions arrivent après le résultat qu'elles devraient aider à définir |
| Remplacer la recherche par la sélection de fiches | [evidence.py](../../alphaforge_app/evidence.py), lignes 3–63 | Une bibliographie préparatoire devient le plafond du travail documentaire ; aucune méthode n'est confrontée à de nouvelles preuves pendant le parcours |
| Arrêter la boucle après un calcul et une lecture réussis | [orchestrator.py](../../alphaforge_app/orchestrator.py), lignes 195–198 | L'arrêt dépend d'une liste d'outils accomplis, pas de la résolution des questions ou de la suffisance des preuves |
| Limiter la restitution à quelques phrases et observations préétablies | Même fichier, lignes 36–87 et 224–251 | La protection contre les chiffres inventés a été obtenue en réduisant excessivement la richesse des conclusions représentables |
| Traiter les questions et conditions comme du texte final | [app.js](../../alphaforge_app/static/app.js), lignes 273, 362 et 434 | L'interface permet un autre calcul, mais pas la résolution d'une question ni la propagation d'une correction |

Ces éléments établissent les choix et leurs effets ; ils n'établissent pas une intention de tromper. Les documents reconnaissent plusieurs limites et ne prétendent pas avoir validé un solveur robuste ou une revue complète.

La recherche initiale comportait une démarche plus ambitieuse : critères préalables, alternative sérieuse, expérience capable de réfuter le choix, puis intégration. La sélection du comparateur n'est pas accompagnée de cette démonstration. Des contrôles réussis de formules et de boutons ne compensent pas l'absence d'évaluation de cette décision de produit.

L'atlas des 36 PDF indiquait lui-même que la couche scientifique financière restait à construire. Les corrections du notebook concernant FX, CAGR et calendriers ont été utiles. Il n'était nécessaire ni de reprendre chaque cellule, ni d'utiliser tous les services AWS : il fallait choisir les ressources selon les questions à résoudre.

## 5. Conserver, reprendre, remplacer

**Conserver comme composants :**

- Le moteur numérique, ses conventions explicites et ses cas de contrôle indépendants.
- L'instantané et ses empreintes, les originaux, les avertissements temporels et les traces existantes.
- Le transport Bedrock effectif, les schémas d'outils et les métadonnées d'appels, avec toutes les inférences sur AWS comme demandé.
- La séparation entre résultats calculés et rédaction, les erreurs annoncées, les limites ESG et les résultats défavorables visibles.
- Les courbes, l'export, les vues progressives et la lisibilité visuelle, après intégration dans un parcours plus riche.
- Les personas comme exemples et tests contrastés, ainsi que les fiches comme début de bibliothèque, avec leur niveau de lecture réel.

**Reprendre selon le problème :**

- Les calendriers : la grille actuelle dépend de tout l'univers hors crypto, y compris des instruments non détenus ; elle peut masquer des creux de fin de semaine.
- Les fenêtres historiques fixes, les frais, les flux, les instruments nécessaires et les dates de connaissance. Toute nouvelle méthode réclame ses propres conventions et validations.
- Les liens de preuve : passer d'une source générale à un passage ou un calcul soutenant une assertion précise.
- Les profils et niveaux d'explication ; montrer les conséquences en CAD quand le besoin est monétaire.
- L'évaluation : distinguer correction numérique, pertinence de la recherche, qualité de décision et compréhension. Un découpage temporel ne supprime pas, seul, le biais d'un univers choisi en 2026.

**Remplacer dans le fonctionnement :**

- Le passage systématique « formulaire → poids cible → commentaire » par la chaîne des quatre agents.
- La liste statique comme unique outil de recherche par une recherche, une lecture et une qualification effectives, avec réutilisation explicite du travail antérieur.
- Les questions non répondables par des échanges enregistrés.
- Les rapports indépendants par des dossiers versionnés et des dépendances de calcul.
- L'assimilation entre « l'appel a réussi » et « le travail scientifique est suffisamment étayé ».

Il ne s'agit ni de conserver le comparateur comme plafond, ni de réécrire tous ses composants.

## 6. Contrat fonctionnel proposé

**AlphaForge est un atelier de décision financière sur situations fictives. Une demande y devient un dossier qualifié, recherché, calculé, contestable et révisable, produit par quatre agents aux responsabilités distinctes. Le système compare les options pertinentes et défend une conclusion conditionnelle ; il peut aussi conclure à une incompatibilité ou à des preuves insuffisantes.**

Le produit accepte une demande courte ou un dossier plus riche. Les trois personas sont des points de départ facultatifs. Il doit pouvoir traiter des questions d'allocation, de concentration, de liquidité, d'exclusion ou d'exploration d'un actif sans les ramener automatiquement au même calcul.

| Agent | Travail effectivement attendu | Document de travail consultable | Condition de transmission |
|---|---|---|---|
| **0** | Comprendre, extraire les faits et leurs sources, distinguer déclaré/supposé/inconnu/contradictoire, clarifier ce qui change la décision, formaliser les sous-problèmes | **Demande et profil qualifiés** : objectifs, contraintes, préférences, flux, horizons, inconnues, questions de recherche, critères de réussite | Les inconnues bloquantes ont une réponse, ou les branches conditionnelles sont explicitement définies |
| **1** | Rechercher et lire les éléments déterminants, comparer les méthodes, examiner les conditions d'application et les contre-arguments | **Dossier de preuves** : recherches, documents, passages localisables, dates, provenance, méthodes candidates, arguments pour/contre et lacunes | La méthode envisagée dispose d'un support pertinent ; l'insuffisance éventuelle est signalée à Agent 0 ou 2 |
| **2** | Formaliser et exécuter l'analyse, comparer une référence et des solutions sérieuses, contrôler les contraintes, tester la fragilité, défendre la conclusion | **Dossier d'analyse** : méthode, alternatives, données, paramètres, calculs, vérifications, sensibilités, objections et conclusion conditionnelle | Chaque résultat est reproductible et chaque conclusion respecte la portée des preuves |
| **3** | Présenter fidèlement, adapter la profondeur au destinataire, permettre l'examen et recevoir corrections ou contestations | **Restitution et journal de révision** : conclusions reliées aux dossiers, explications à plusieurs niveaux, questions et demandes de reprise | La présentation ne rajoute pas de faits ; une correction revient aux responsabilités concernées |

Un orchestrateur technique coordonne les passages et les retours. Il ne remplace aucun des quatre agents. Les quatre rôles doivent avoir de véritables missions, contextes, outils et sorties observables ; quatre noms sur une animation ne suffisent pas. Un modèle, un client AWS ou un processus peuvent être partagés sans fusionner ces responsabilités.

La confrontation des arguments fait partie du travail obligatoire : Agent 1 conserve les preuves défavorables ; Agent 2 expose le meilleur contre-argument et tente de réfuter ses conclusions au moyen de vérifications. Des spécialistes peuvent assister ces agents, notamment pour une critique méthodologique. Leur accord n'est jamais pris comme preuve indépendante.

Chaque document possède un identifiant de dossier, une version, ses parents, son auteur fonctionnel, ses entrées, son statut et les exécutions associées. Chaque calcul conserve données, paramètres, version de méthode, sorties et contrôles. Chaque assertion renvoie à une preuve ou à une hypothèse déclarée. Les traces doivent exposer les actions et les justifications vérifiables ; elles n'exigent pas le raisonnement privé des modèles.

La recherche peut réutiliser une ressource déjà qualifiée ; cela doit être visible. Une source simplement repérée ne devient pas une source lue. Une limite technique de durée ou d'appels conduit à un statut partiel et une reprise possible, pas à une conclusion artificiellement définitive. L'approfondissement dépend des questions susceptibles de changer la décision, sans quota décoratif de publications.

La mise en œuvre reste locale sur le Mac à ce stade ; les inférences restent routées par AWS Bedrock. Le choix de framework, de stockage ou de services supplémentaires sera justifié après validation de ce contrat, sans demander au porteur de trancher des préférences techniques arbitraires.

## 7. Exemple complet de l'expérience visée

**Ce parcours est une cible proposée, pas une fonction déjà livrée.** Les calculs illustratifs ci-dessous ont été exécutés pour vérifier leur arithmétique. Les scénarios et la réserve sont fictifs ; aucune revue de littérature nouvelle, calibration de risque ou validation d'instrument de réserve n'est revendiquée par cet exemple.

### Demande initiale et Agent 0

Robert écrit :

> « J'ai un portefeuille fictif de 100 000 CAD. Je prépare ma retraite dans quatre ans, mais j'aurai besoin de 30 000 CAD dans douze mois. Tesla représente 25 % du portefeuille. Je voudrais réduire cette tension en modifiant le moins possible mes placements. Explique-moi les possibilités simplement, avec les calculs accessibles. »

Il joint son portefeuille : 35 % XBB, 20 % ZST, 20 % XIU, 25 % TSLA. Agent 0 ne lui attribue pas automatiquement une nouvelle allocation.

L'agent clarifie les points décisifs : retrait impératif ou modulable, réserve extérieure éventuelle, sens de « modifier le moins possible », plafond souhaité sur TSLA et besoin éventuel de capital garanti sur le solde. Il distingue un montant de perte acceptable d'une garantie de perte maximale future.

Pour cet exemple seulement, Robert confirme : pas de réserve extérieure ; 30 000 CAD nominaux disponibles sans vente d'actifs risqués à douze mois ; plafond initial TSLA de 10 % ; solde investissable quatre ans, sans objectif de montant garanti ; minimiser le montant réalloué. Après explication, un budget de perte de 15 000 CAD dans les scénarios étudiés est une contrainte de l'exercice, jamais une garantie future.

Document **R0-v1 — Demande qualifiée** : ces confirmations, leur provenance, le portefeuille, les échéances, les contraintes dures, les préférences et les questions restantes. L'âge ne détermine aucun poids.

Questions transmises à Agent 1 : comment distinguer disponibilité nominale et risque de marché ? Quelles méthodes permettent d'étudier un retrait daté et une modification minimale ? Quelles hypothèses rendent les scénarios pertinents ? Quels risques et coûts pourraient invalider la solution ?

### Agent 1 : recherche et choix conditionnel de méthode

L'agent recherche les passages pertinents sur planification avec objectifs et liquidité, modélisation des flux, scénarios de risque et réallocation sous contraintes. Il consulte aussi les documents primaires des instruments de réserve envisageables : une faible volatilité passée d'un FNB ne prouve pas un remboursement nominal à une date donnée.

Il examine au moins les possibilités qui peuvent changer la décision : simple baisse de TSLA, séparation d'une réserve dédiée, allocation sous contraintes, et maintien de positions avec financement du retrait par ventes futures. Il compare leurs hypothèses et limites. Il n'adopte pas une optimisation moyenne–variance simplement parce qu'un solveur existe.

Document **R1-v1 — Dossier de recherche** : pour chaque conclusion déterminante, passage précis, source/version, date de publication ou de disponibilité, date de consultation, niveau de lecture, conditions d'application, argument contraire et conséquence sur la méthode. Les textes inaccessibles restent signalés ; les références anciennes servent de pistes, sans être transformées en résultats validés.

Pour poursuivre l'illustration arithmétique, la réserve est un compartiment nominal abstrait à rendement nul, distinct de XBB et ZST. Les coûts et la fiscalité sont provisoirement nuls. Ce sont des hypothèses de calcul explicites, pas des caractéristiques déjà établies d'un placement accessible.

### Agent 2 : calculs, comparaison et confrontation

Le problème illustratif consiste à minimiser la part du capital déplacée, sous budget de 100 %, poids non négatifs, réserve d'au moins 30 %, TSLA au plus 10 % et pertes inférieures ou égales à 15 000 CAD dans les scénarios spécifiés.

Pour les poids initiaux `w0` et les poids candidats `w`, la part déplacée est `T = ½ × Σ |w − w0|`. Pour un scénario de rendements `r`, la perte est `L = −100 000 × Σ(w × r)`. Ce calcul porte sur une valeur à douze mois ; il n'est pas une mesure de drawdown sur une trajectoire.

Deux chocs sont fixés **uniquement pour rendre cet exemple calculable** :

| Instrument | Choc actions | Choc obligations |
|---|---:|---:|
| Réserve nominale abstraite | 0 % | 0 % |
| XBB | −5 % | −15 % |
| ZST | 0 % | −2 % |
| XIU | −20 % | −10 % |
| TSLA | −50 % | −25 % |

Ils ne reçoivent aucune probabilité et ne représentent pas toute l'incertitude. Dans le produit visé, la justification, l'élargissement et la sensibilité des scénarios font partie du dossier ; ces deux chocs ne deviennent pas les scénarios fixes universels de la refonte.

| Option | Réserve / XBB / ZST / XIU / TSLA | Capital déplacé | Perte : choc actions | Perte : choc obligations | Admissibilité dans l'exercice |
|---|---|---:|---:|---:|---|
| **A. Portefeuille actuel** | 0 / 35 / 20 / 20 / 25 % | 0 CAD | 18 250 CAD | 13 900 CAD | Non : réserve, plafond TSLA et premier budget de perte |
| **B. TSLA à 5 %, redistribution actuelle** | 0 / 44,333… / 25,333… / 25,333… / 5 % | 20 000 CAD | 9 783,33 CAD | 10 940 CAD | Non : absence de réserve dédiée |
| **C. Réserve et plafond TSLA** | 30 / 35 / 5 / 20 / 10 % | 30 000 CAD | 10 750 CAD | 9 850 CAD | Oui, sous les hypothèses déclarées |

Agent 2 contrôle les sommes, les contraintes et les pertes. Dans C, le premier choc produit par exemple `35 000 × 5 % + 20 000 × 20 % + 10 000 × 50 % = 10 750 CAD`. Après ce choc et le retrait, le patrimoine restant est de `100 000 − 10 750 − 30 000 = 59 250 CAD`.

Une preuve limitée est possible : il faut déplacer au moins 30 % du portefeuille pour créer une réserve de 30 % à partir d'une réserve nulle, sans financement extérieur. C atteint cette borne et respecte les contraintes ; il minimise donc le montant déplacé **dans ce modèle**. D'autres allocations peuvent atteindre le même minimum. Cela ne prouve ni une allocation financière universellement optimale, ni les meilleurs frais ou impôts.

Le contre-argument est conservé : B perd moins que C dans le choc actions. Choisir C n'est donc pas « choisir le meilleur chiffre ». B échoue à la contrainte de disponibilité définie par Robert. C satisfait les contraintes étudiées, mais sa dépendance aux scénarios, aux coûts omis et à la réalité de la réserve doit être examinée.

Document **R2-v1 — Dossier d'analyse** : les trois options, leurs paramètres, calculs exécutés, contrôles de contraintes, preuve du minimum conditionnel, contre-arguments, sensibilités et limites. Les simulations historiques peuvent compléter ce dossier avec le moteur existant, en étant distinguées de ces chocs prospectifs fictifs.

### Agent 3 : restitution et examen

Une présentation simple pourrait dire :

> « Réduire Tesla ne résout pas, à lui seul, ton besoin de disposer de 30 000 CAD. Dans l'exercice retenu, l'option C constitue cette réserve et limite l'exposition initiale à Tesla. Elle déplace le minimum de capital nécessaire selon notre modèle. Elle n'est pas la moins perdante dans chaque scénario, et la protection de la réserve doit être vérifiée pour l'instrument finalement envisagé. »

Document **R3-v1 — Restitution** : cette conclusion, les montants exacts insérés depuis R2-v1, les liens vers contraintes et passages, les objections et ce qui ferait changer la conclusion.

Robert peut choisir « essentiel », « expliquer » ou « examiner les calculs ». Changer ce niveau modifie la présentation, pas les résultats. Il peut ouvrir une contrainte, un passage ou un calcul, répondre à une question et contester une assertion.

### Révision réelle

Robert précise ensuite : « Le retrait sera finalement de 40 000 CAD. »

Agent 3 enregistre une demande de révision. Agent 0 produit R0-v2 et marque la réserve de 30 000 CAD comme insuffisante. Agent 1 réutilise les passages encore applicables avec leur provenance, puis vérifie les éléments affectés. Agent 2 invalide l'admissibilité de C et recalcule.

Un candidat illustratif D devient **40 % de réserve, 30 % XBB, 0 % ZST, 20 % XIU, 10 % TSLA**. Il déplace 40 000 CAD par rapport au portefeuille initial ; les pertes calculées sont 10 500 CAD et 9 000 CAD. Après retrait, les montants restants sont respectivement 49 500 CAD et 51 000 CAD.

Ce candidat atteint la nouvelle borne minimale de 40 % dans le même modèle. Agent 3 présente la différence entre versions, avec sa cause. L'ancienne analyse reste consultable. Si la modification portait sur la date du retrait ou l'instrument de réserve, la recherche documentaire et la modélisation temporelle devraient elles aussi être réexaminées.

## 8. Conditions de réception de la refonte

La réception ne reposera ni sur le nombre de sources ni sur quatre panneaux intitulés « agents ». Un premier parcours complet devra montrer :

1. Une demande libre transformée en problème explicite **avant** toute solution proposée, avec inconnues et provenance des faits.
2. Une exécution identifiable de chacun des quatre agents et leurs documents intermédiaires. Un rôle sans travail ne peut être marqué « terminé ».
3. Une recherche réellement exécutée, ou une réutilisation explicitement identifiée, avec passages déterminants et examen d'une objection.
4. Un choix de méthode qui répond au problème, comparé à une référence simple et à une alternative sérieuse lorsque pertinente.
5. Des calculs reproductibles, des contraintes vérifiées et une distinction entre preuve formelle conditionnelle, vérification numérique, observation empirique et utilité décisionnelle.
6. Une conclusion reliée aux preuves, capable de reconnaître qu'une option est inadmissible, fragile ou indéterminée.
7. Une restitution adaptée sans changement des faits, et des questions auxquelles l'utilisateur peut réellement répondre.
8. Une correction significative qui crée une nouvelle version et relance les agents ou calculs affectés ; le résultat ancien reste inspectable.
9. Un parcours d'échec explicite : source introuvable, données insuffisantes, contradiction non résolue ou erreur AWS, sans masquer la partie non réalisée.
10. Des contrôles contrastés sur liquidité, concentration et exclusions, afin que le premier exemple ne devienne pas un nouveau plafond arbitraire du produit.

Après validation seulement, la réalisation pourra commencer par ce parcours complet et vérifier les contrats avant de multiplier les fonctions ou de refaire l'habillage. Le prototype actuel restera la référence conservée.

## 9. Décisions de direction soumises au porteur

1. **Valider ce contrat comme base de la refonte, ou préciser la promesse à corriger.** Il prévoit que le système puisse privilégier une option lorsqu'il peut défendre cette préférence, tout en montrant les alternatives, les objections et les conditions qui changeraient la conclusion.
2. **Choisir la première démonstration approfondie : Robert et un retrait daté ; Mateo et des exclusions documentées ; ou Amira et la concentration réelle.** Recommandation : Robert, car il oblige immédiatement à relier qualification, recherche, contraintes, calculs et révision. Les autres situations restent des tests de généralité du produit.
