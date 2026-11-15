# Décisions techniques proposées — dossier, orchestration et exécution

**Prompt 3 · Conception seulement · 15 novembre 2026.**

Cette note propose des choix pour un parcours utilisateur évolutif. Elle ne construit aucun composant, ne modifie pas le produit et ne déploie rien. Aucune nouvelle installation, aucun appel d’inférence applicatif et aucune opération AWS n’ont été réalisés pour cette conception. La route convenue demeure `amazon-bedrock-runtime`, profil `alphaforge`, compte `471112821226`, région d’entrée `us-east-1`, modèle `global.openai.gpt-6-astra`.

## 1. Recommandation

Proposer un **noyau de dossier versionné indépendant du framework**, quatre agents métier distincts, un moteur d’exécution remplaçable et des adaptateurs d’outils explicitement autorisés.

**LangGraph est le premier moteur à qualifier après validation de la conception**, avec un stockage local SQLite et des artefacts immuables sur disque. Sa persistance par thread, ses interruptions et ses commandes de reprise correspondent au besoin de discussions reprises, de branches et de corrections. Ce choix est motivé par les mécanismes documentés et le code inspecté, pas par une intégration déjà réussie dans AlphaForge.

**Strands Graph est une alternative de premier rang** : il supporte les graphes conditionnels et cycliques, les interruptions et la sérialisation d’un état de reprise. Son fournisseur Bedrock explicite et ses mécanismes de session méritent la même épreuve de qualification. La différence n’est pas « flexible contre rigide » ; elle porte sur l’intégration de nos contrats, les frontières de persistance et la complexité réellement conservée dans le code applicatif.

Une machine à états Python explicite constitue le contrôle de comparaison et un choix de repli crédible si elle satisfait ces exigences avec moins de complexité. Il ne faut pas maintenir simultanément trois moteurs en production. Après validation, une tranche d’essai bornée doit permettre au responsable technique de trancher et de documenter le résultat, sans demander au porteur de choisir arbitrairement une bibliothèque.

L’exécution reste d’abord locale, conformément au parcours retenu. **AgentCore Runtime** et **Step Functions avec Lambda** sont des options de déploiement ou d’exécution durable, pas des remplaçants du dossier métier. Le passage au cloud se justifierait par des travaux qui doivent survivre à l’arrêt du Mac, plusieurs utilisateurs ou des ressources distribuées ; il demanderait une décision sur l’exploitation, les accès et les coûts.

## 2. Séparer les couches pour ne pas confondre leurs garanties

| Couche | Responsabilité | Ce qu’elle ne garantit pas |
|---|---|---|
| Dossier et règles métier | Révisions, questions, preuves, contraintes, résultats, conflits, droits de modification et invalidations | Qualité d’un texte généré sans vérification de son contenu |
| Orchestration | Décider quels travaux autorisés sont prêts ; lancer les quatre rôles ; reprendre, attendre, annuler et borner | Validité financière ou vérité d’une source |
| Exécution et outils | Appels Bedrock, recherche, lecture, calcul, contrôle indépendant ; entrées/sorties/erreurs observables | Pertinence d’une méthode simplement parce qu’elle s’exécute |
| Persistance et exploitation | Transactions, artefacts, sauvegarde, accès, files de travail et traces | Reproductibilité exacte d’une nouvelle génération ni résidence physique de l’inférence |
| Parcours utilisateur | Projeter l’état du dossier, montrer les alternatives et recueillir corrections ou choix | Remplacement silencieux des faits ou résultats dans le texte de présentation |

Les quatre agents restent **Agent0 qualification/formalisation, Agent1 recherche/revue, Agent2 analyse/résolution, Agent3 restitution/interaction**. Le noyau transactionnel et l’ordonnanceur sont du logiciel, pas un cinquième agent métier. Plusieurs tâches ou appels peuvent appartenir au même rôle ; le nombre d’agents n’est pas le nombre d’inférences.

Une révision de fond peut solliciter les quatre rôles. Un changement de niveau de détail d’une explication peut réutiliser des pièces toujours valides et ne solliciter qu’Agent3. Il faut montrer cette réutilisation, sans simuler de nouveaux travaux ni effacer les responsabilités des autres agents.

## 3. Le contrat commun aux architectures

### 3.1 Dossier immuable par révision et écritures proposées

Les agents ne modifient pas directement l’état partagé. Ils produisent un **`ChangeSet`** contenant :

- `base_revision`, les versions du `read_set`, les opérations typées et les écritures proposées ;
- le motif, les preuves invoquées, le rôle, `task_id`, l’identifiant de tentative et une clé d’idempotence ;
- les nouvelles pièces ou leurs références et les conséquences attendues sur les dépendances.

Seul le noyau valide les droits par champ, les références, les invariants et les conflits, puis enregistre une nouvelle révision. Une clé d’idempotence déjà commise rend le résultat antérieur ; réutiliser la même clé avec un contenu différent est rejeté.

**Trois identités restent distinctes :**

| Identité | Exemple de changement | Effet |
|---|---|---|
| Révision du dossier | La personne remplace un retrait de 30 000 par 40 000 CAD | Nouvelle vue cohérente du dossier et recalcul des dépendances |
| Version métier d’un artefact | Une source est amendée, une formulation ou un résultat est corrigé | Nouvelle pièce avec sa provenance et ses relations |
| Tentative d’exécution | Un appel échoue puis est relancé sur les mêmes entrées | Nouvelle trace technique ; pas nécessairement une nouvelle conclusion métier |

Un checkpoint du framework est une quatrième notion : il décrit où reprendre une exécution. Ce n’est ni une révision utilisateur ni une preuve financière.

L’utilisabilité courante d’une pièce est contextualisée par sa version, la branche et la révision du dossier. Elle appartient à la projection ou à une relation versionnée gérée par le noyau, pas à un champ global réécrit dans les octets de l’artefact. Le même calcul peut rester valide dans une variante conservant ses entrées et devenir périmé pour le mandat principal corrigé.

L’acceptation d’un `ChangeSet` ne signifie pas que son contenu est scientifiquement vrai. Le noyau distingue validation de forme, cohérence, autorisation, contrôles numériques et ancrage documentaire. Les jugements d’adéquation et les incertitudes conservent leur provenance et leur statut.

### 3.2 Quatre graphes reliés, avec des objets identifiables

| Graphe | Objets et relations | Règle essentielle |
|---|---|---|
| Questions | Questions, sous-questions, inconnues, critères et dépendances versionnées | Une question peut être ouverte, résolue sous hypothèses, contestée ou rouverte ; elle n’est pas assimilée à un message de chat |
| Tâches | Travail assigné à un rôle, entrées requises, tentatives, résultats, erreurs et attente humaine | Les dépendances de calcul d’une révision sont acycliques ; une boucle de révision crée de nouveaux travaux et versions |
| Preuves | Documents, passages, données, calculs, assertions et relations `supports`, `refutes`, portée et date | Un document collecté n’est pas une preuve suffisante ; une contradiction ne se résout pas par majorité de citations |
| Parcours | Projection courante : ce qui est prêt, manquant, ancien, en cours ou soumis à la personne | L’interface ne reconstruit pas arbitrairement un état à partir du dernier texte reçu |

Ces graphes sont des modèles métier, pas nécessairement quatre bases de graphes. Des objets et relations stockés dans des tables relationnelles suffisent à une première réalisation locale ; le modèle doit rester exportable.

Un cycle d’exécution tel que `Agent2 → Agent1 → Agent2` est légitime. Il ne doit pas créer une dépendance de calcul circulaire du type « résultat R1 dépend de R2 qui dépend de R1 » dans la même révision acceptée. Les relations de contestation ou de discussion ne sont pas confondues avec les dépendances nécessaires au calcul.

### 3.3 Réouverture et invalidation ciblée

Le noyau entretient un index de dépendances. Une invalidation signifie **« ne plus utiliser cette pièce comme résultat courant dans cette portée »**, pas supprimer l’histoire.

| Déclencheur | Pièces à réexaminer | Pièces potentiellement réutilisables |
|---|---|---|
| Changement de retrait, horizon, devise ou contrainte | Mandat, admissibilité, formulation, résultats dépendants et restitution | Sources ou calculs indépendants du champ changé, après contrôle du `read_set` |
| Nouvelle version d’une source | Assertions et décisions dépendant du passage modifié | Ancienne version pour une analyse historiquement datée ; ne pas la remplacer rétroactivement |
| Correction d’une méthode ou de données | Résultats produits avec l’ancienne version, comparaisons et conclusions | Profil, documents non concernés, autres branches sans cette dépendance |
| Erreur ou réponse d’outil incomplète | Tâche et conclusions exigeant ce résultat | Travaux déjà validés qui n’en dépendent pas ; état partiel explicite |
| Changement de style ou profondeur d’explication | Projection et restitution | Les mêmes faits, réserves et résultats ; aucune nouvelle vérité financière |
| Choix humain d’une autre hypothèse | Nouvelle branche ou révision attribuée à ce choix | Les faits de source restent des faits ; une préférence humaine ne transforme pas une assertion fausse en vraie |

Les règles de dépendance et d’invalidation sont à écrire dans AlphaForge, quel que soit le moteur. Un framework ne sait pas spontanément qu’une modification de retrait invalide une allocation mais laisse une définition de CVaR applicable.

### 3.4 Branches et pièces partagées

Les branches représentent des scénarios ou hypothèses explicites. Elles partagent des **références à des versions immuables**, pas un objet courant que chaque agent peut écraser. Une pièce réutilisée garde ses données, période, méthode, conditions d’applicabilité et accès.

La réutilisation exige une signature des entrées pertinentes : version des données et de la méthode, paramètres, périmètre temporel, unités, contraintes concernées et contexte d’autorisation. Une simple ressemblance entre deux demandes ne suffit pas. Une empreinte identique démontre l’identité des octets, pas l’adéquation à une autre question.

Une fusion de branches est une proposition : comparaison des changements depuis leur ancêtre commun, détection des conflits et revue des dépendances. Aucun `last writer wins`. Deux branches incompatibles peuvent rester côte à côte ; le système ne doit pas inventer un compromis pour obtenir un dossier unique.

### 3.5 Évolution des méthodes et outils

Le système doit pouvoir représenter une méthode nouvelle avant de savoir l’exécuter. Agent1 peut apporter ses sources, ses hypothèses, ses limites et des implémentations candidates ; Agent2 peut proposer une formulation, des conditions d’applicabilité et un protocole de validation. Ces propositions deviennent des pièces versionnées du dossier. Si aucun outil admis ne permet de les éprouver, l’état est « méthode proposée, validation ou capacité manquante », avec un travail identifié pour lever cette limite.

Un registre versionné sépare donc **méthodes documentées**, **implémentations évaluées** et **outils exécutables autorisés**. Chaque outil admis précise schémas d’entrée/sortie, version de code, effets de bord, droits, route d’inférence éventuelle, contrôles et provenance. Un lien GitHub, un texte de modèle ou un nouveau nom de méthode ne suffit pas à rendre du code exécutable. Une extension dans le cadre accepté peut être qualifiée techniquement ; une extension qui change les finalités, droits, données transmises ou coûts convenus demande l’accord correspondant.

Ce registre ne doit pas enfermer le raisonnement dans les quelques fonctions déjà construites. Il doit rendre visibles les besoins non couverts et permettre une extension vérifiable, tout en conservant les outils et résultats antérieurs pour reproduire les analyses qui les utilisaient.

## 4. Comparaison des moteurs et plateformes

Les capacités ci-dessous proviennent des pages et fichiers inspectés. **Aucun de ces frameworks n’a été installé ou intégré pour cette conception.** Les opérations AWS déjà prouvées sont rapportées en section 8.

| Candidat | Capacités pertinentes documentées ou inspectées | Intégrations propres à AlphaForge | Raisons de le choisir / limites à éprouver |
|---|---|---|---|
| **Machine à états explicite en Python** | Liberté de concevoir transitions, travaux, concurrence et stockage avec les bibliothèques actuelles | Tout le cycle de tâches, checkpoints, interruptions, migrations, visualisation et reprise est à écrire | Très transparente, bonne référence de simplicité et de contrôle. Sérieuse pour un dossier riche si l’investissement de fiabilisation est assumé ; l’extension des cas accroît le coût de maintien des mécanismes génériques |
| **LangGraph** | Graphe d’exécution, état, `Command`, interruptions ; checkpointers par thread et stores inter-threads ; reprise et time travel documentés | Envelopper les rôles, brancher le client Bedrock, lier checkpoint/tâche/révision, intégrer `ChangeSet` et restrictions, gérer export et tests de reprise | Premier candidat proposé pour interactions reprises et branches. Un checkpoint ne fait pas la fusion métier. `interrupt` reprend le nœud depuis son début : les effets précédents doivent être idempotents ou isolés |
| **Strands Graph** | Nœuds agents ou code, arêtes conditionnelles, graphes acycliques et cycliques, limites d’exécution, interruptions et sérialisation des nœuds prêts ; fournisseur Bedrock | Noyau métier, adaptation de session persistante, contrats des résultats, liaison des checkpoints, droits et contrôle des effets | Alternative sérieuse pour orchestration explicite sur Bedrock. La version inspectée restaure l’état interrompu, mais une exécution déjà terminée peut être réinitialisée à la désérialisation : distinguer réouverture métier et reprise technique |
| **Strands Harness et outils multi-agents** | Boucle agentique, gestion du contexte, outils intégrés, délégation avec politiques d’héritage ; outil Graph dont la topologie est conçue par le modèle | Enveloppes de rôle fixes, restrictions d’outils, admission des travaux proposés et persistance métier | Utile à l’intérieur d’un rôle de recherche ou d’analyse nécessitant exploration. Ne pas confondre ce Graph dynamique avec `GraphBuilder` contrôlé par l’application. L’héritage par défaut doit être explicite ; une délégation libre ne doit pas recréer ou fusionner les quatre responsabilités |
| **Step Functions Standard + Lambda** | Orchestration durable, historique, conditions, parallélisme, retries et intégrations ; attente humaine possible par pattern de callback documenté | Découpage des travaux, stockage du dossier, adaptateurs d’agents, callbacks sécurisés, idempotence, contrôles métier et interface | Pertinent pour exécutions distribuées ou longues indépendantes du Mac. Ni intrinsèquement rigide ni prêt pour notre dossier : les branches sémantiques et invalidations restent applicatives. Déploiement, IAM et coûts de transitions/exécution à prendre en charge |
| **Step Functions Express + Lambda** | Exécution courte ; Express asynchrone at-least-once, synchrone at-most-once ; limites et intégrations différentes de Standard | Même noyau métier, reprise externe si nécessaire, déduplication renforcée | Bon candidat pour sous-travaux courts et idempotents à volume important. Moins adapté comme contenant d’un dossier attendant une personne : durée documentée de cinq minutes et absence du pattern callback `.waitForTaskToken` |
| **AgentCore Runtime** | Hébergement serveur d’agents et d’outils, isolation de session, exécution asynchrone et intégration de frameworks documentées | Application à déployer, fournisseur explicite, stockage durable, identité des utilisateurs, contrat de session, observabilité et coûts | Peut héberger LangGraph, Strands ou un moteur explicite. Ce n’est pas un choix exclusif entre « LangGraph » et « AgentCore ». Une session de runtime ne remplace pas l’historique du dossier, sa sauvegarde ou les règles de réouverture |

**Précisions importantes :**

- LangGraph inspecté : commit `08a2016953789a4f579b4d36bd1967941ec62012`, version `1.2.22` dans le `pyproject.toml`, licence MIT. Strands inspecté : commit `c8e1351a5a6218c8f5c2417534aedbd021882a76`, version déterminée par tags, licence Apache-2.0. Il faudra épingler les distributions effectivement retenues.
- Strands Graph dispose réellement de reprise : `serialize_state` conserve résultats, états interrompus, prochains nœuds et métriques ; `deserialize_state` distingue une exécution terminée d’une exécution à reprendre. Cela interdit de le réduire à une chaîne sans mémoire. Les garanties d’un gestionnaire de session concret restent à tester.
- Les garanties « exactly-once » de Step Functions Standard décrivent son modèle d’exécution, avec exception des retries configurés. Elles ne garantissent pas magiquement qu’un effet externe, une facture ou un enregistrement de résultat sera unique dans toutes les fenêtres de panne.
- Les limites Lambda dépendent de la famille de fonction et du mode d’invocation. La documentation courante distingue notamment la limite usuelle de 15 minutes et certaines invocations Managed Instances plus longues. Aucun choix de service ne doit reposer sur « Lambda dure toujours 15 minutes » ; le découpage doit de toute façon libérer un worker pendant une attente humaine.
- **Strands Harness** et **AgentCore Harness**, également présenté dans la documentation AWS actuelle, sont deux produits distincts. Cette note ne propose pas d’adopter une boucle d’inférence gérée supplémentaire dont les appels, modèles auxiliaires et coûts n’ont pas été qualifiés.

## 5. Stockage : local d’abord, modèle exportable

| Option | Proposition de responsabilités | Concurrence et reprise | Coût, accès et limites |
|---|---|---|---|
| **SQLite + artefacts locaux** | Transactions pour révisions, relations, tâches, tentatives et journal ; documents volumineux/fichiers de résultats immuables par empreinte ; références dans le dossier | Transactions courtes, un écrivain à la fois, lectures concurrentes compatibles avec le mode choisi ; verrouillage optimiste sur la révision ; worker ne garde pas de transaction ouverte pendant un appel modèle | Approprié à l’usage sur Mac. Pas de frais cloud de stockage, mais dépend de la disponibilité, des droits et de la sauvegarde du Mac. Ne pas présenter un dossier synchronisé de fichiers comme une base multi-utilisateurs sûre |
| **S3 + DynamoDB** | S3 pour documents et résultats ; DynamoDB pour métadonnées, têtes de branches, tâches et événements ; versions d’objets et empreintes conservées | Écritures conditionnelles/transactions sur les métadonnées et contrôle de révision ; leases de workers et déduplication à concevoir. Pas de transaction unique automatiquement commune à S3 et DynamoDB | Pertinent pour plusieurs workers/utilisateurs et exécution durable. Demande schéma d’accès, IAM, sauvegarde, coûts de requêtes/stockage et export hors compte éphémère. Pas de ressource existante AlphaForge vérifiée justifiant une migration immédiate |

Le choix local ne fige pas le produit. Une interface de dépôt doit séparer les opérations métier des mécanismes de stockage : lire une révision, proposer un changement, rechercher les dépendances, réclamer une tâche, enregistrer une tentative et récupérer un artefact.

Pour l’atomicité avec des fichiers locaux, écrire dans un fichier temporaire, vérifier puis finaliser l’artefact par renommage atomique sur le même volume avant de commettre sa référence dans SQLite. La synchronisation sur disque et les paramètres SQLite doivent assurer la durabilité au niveau de panne retenu ; un test d’arrêt de processus ne démontre pas la résistance à une coupure électrique. Ce protocole vise à laisser au pire un fichier orphelin, pas un résultat accepté pointant vers un fichier inachevé. Prévoir inventaire et nettoyage des orphelins, sans supprimer de pièce encore référencée. La sauvegarde doit capturer de manière cohérente base, journal éventuel et artefacts ; copier un fichier SQLite actif au hasard ne suffit pas.

Le même principe s’applique au cloud : dépôt S3 terminé et identifié avant transaction des métadonnées ; réconciliation des objets orphelins et des tâches inachevées. Versioning, empreintes ou Object Lock ne prouvent pas la justesse du contenu et ne remplacent pas une copie hors du compte temporaire.

**Un seul dossier fait autorité.** Si le framework utilise son propre checkpointer, il doit référencer les révisions et événements métier, sans créer une seconde « vérité » modifiable. Le checkpoint et le commit applicatif peuvent être désynchronisés par une panne ; le noyau doit pouvoir détecter cette situation et reconstruire l’état de travail à partir des événements acceptés.

## 6. Concurrence, reprise et interventions humaines

### 6.1 Travail parallèle sans écrasement

Une tâche reçoit un instantané d’entrées et un `read_set`. Le noyau et les adaptateurs construisent ou contrôlent ce dernier à partir du contexte effectivement transmis et des résultats de lecture fournis pendant la tâche ; le modèle ne peut pas retirer une entrée pour contourner l’invalidation. On ne prétend pas observer avec certitude quels passages ont influencé son raisonnement : un contexte borné permet un suivi conservateur sans rattacher chaque tâche au dossier entier. Avant commit, le noyau compare ces versions :

- si les entrées utilisées sont toujours valides et les écritures compatibles, il peut accepter ou rebaser explicitement le changement ;
- si une entrée déterminante a changé, il rejette le résultat comme obsolète pour la branche courante, ou le conserve dans une branche d’analyse séparée ;
- si deux changements se contredisent, il crée un conflit à résoudre, sans arbitrage fondé sur l’ordre d’arrivée.

Un résultat devenu obsolète conserve son coût, son invocation et son contenu ; il ne devient pas une réussite courante. Le contrôle porte sur les dépendances réellement lues, pas seulement sur un numéro global qui invaliderait inutilement toutes les recherches à chaque correction typographique.

Un worker réclame une tâche au moyen d’un lease identifié et renouvelable. La fin d’un lease ne prouve pas qu’un appel externe s’est arrêté. Une reprise doit examiner l’état de la tentative avant de relancer, surtout si un outil a des effets de bord.

### 6.2 Reprise explicite

États utiles à distinguer : prêt, en exécution, attente d’une personne, attente d’une dépendance, réussi, partiel, échoué, annulation demandée, annulé et obsolète. Le statut du dossier est une projection de ces états et des conclusions admissibles ; il ne dépend pas uniquement du dernier appel réussi.

Une annulation arrête la planification et les commits devenus non souhaités. Elle ne garantit ni l’arrêt immédiat d’un appel déjà parti ni l’absence de coût. Une réponse tardive doit être enregistrée comme telle et ne pas écraser la correction humaine intervenue entre-temps.

La reprise technique et la réouverture utilisateur restent distinctes. « Continuer une tentative interrompue » réutilise ses entrées si elles sont encore valides. « Revoir la décision avec un nouvel horizon » crée une révision métier et de nouveaux travaux. Les checkpoints opaques d’une ancienne version de framework ne doivent pas être la seule sauvegarde disponible.

### 6.3 Intervention humaine

Une demande de clarification ou de décision comporte le champ ou la question concernée, les options quand elles sont utiles, la conséquence de chaque réponse et la révision visée. La réponse humaine devient un événement attribué ; elle est contrôlée comme toute autre proposition.

On ne garde pas une inférence ou une fonction de calcul active pour attendre cette réponse. L’attente est persistée, puis le travail reprendra sur une révision explicite. L’absence de réponse n’est ni une approbation ni une valeur numérique.

Un humain peut corriger une préférence, demander une autre hypothèse, contester une preuve ou choisir entre solutions admissibles. Le parcours doit distinguer ces actes : accepter un scénario ne valide pas une source, et demander une explication plus simple ne modifie pas les réserves financières.

## 7. Droits, route d’inférence et budgets

### Droits effectifs

Les outils sont accordés par rôle et tâche, avec paramètres bornés :

- Agent0 : qualification, lecture des informations utiles et propositions sur le mandat ;
- Agent1 : recherche documentaire, récupération et qualification de sources ; aucune écriture directe dans un résultat numérique validé ;
- Agent2 : calculs et contrôles admis, propositions de méthode ou de scénario ; aucune relaxation silencieuse d’une contrainte ;
- Agent3 : consultation, restitution, enregistrement de questions/corrections ; aucune réécriture du registre par la prose.

Ces droits sont appliqués par le noyau et les adaptateurs. Un prompt, un nom d’agent ou un filtre d’affichage d’outils MCP ne remplace pas ce contrôle. Les textes externes restent des données non fiables ; ils ne peuvent pas ajouter un outil, changer la route d’inférence ou autoriser un envoi.

La séparation des rôles ne garantit pas l’indépendance des erreurs : les modèles peuvent partager une même erreur et les mêmes sources. Les contrôles numériques indépendants, passages primaires, cas contradictoires et revues humaines gardent leur rôle.

### Route explicite

Le moteur retenu reçoit un adaptateur Bedrock configuré, avec contrôle du compte, du profil et du modèle. **Pas de repli silencieux** vers un autre fournisseur, une région ou un modèle par défaut. Strands inspecté a notamment des valeurs par défaut différentes de la route retenue ; elles ne doivent pas décider de l’exécution.

Chaque appel effectif doit enregistrer modèle/profil, région d’entrée, identifiant de requête, usage disponible, durée, motif d’arrêt et erreur éventuelle. Les appels de sortie structurée, correction de schéma, synthèse, résumé de contexte et évaluation comptent aussi. Les secrets et le raisonnement interne ne sont pas nécessaires à ce registre.

Le contrôle de route s’applique séparément aux éventuels embeddings, reclassements, extraction documentaire assistée, juges et services de mémoire qui extraient des faits par modèle. Un service hébergé sur AWS n’assure pas à lui seul que toutes ses intégrations utilisent le modèle convenu.

### Budget et coûts

Le budget est attaché au dossier, à la branche et aux tâches : nombre d’appels, entrées/sorties maximales prévues, opérations de recherche, durée active et retries. Une reprise ne remet pas le compteur métier à zéro. Les bornes techniques d’un framework et l’attente d’une personne sont comptabilisées séparément.

Les coûts dominants restent à mesurer : inférence principale et auxiliaire, recherche, répétitions après erreurs, puis stockage, logs, transitions ou durée de runtime selon le déploiement. Aucun tarif ni montant total n’est inventé ici. L’estimation doit citer le tarif daté et distinguer tokens normaux, cache et prix des services.

La page AWS de retries consultée décrit un comportement 2026 soumis à opt-in. Dans la documentation locale de botocore `1.44.3`, `Config(retries.max_attempts)` compte les retries après l’appel initial ; `total_max_attempts` inclut l’initial. Éviter de multiplier involontairement les tentatives entre SDK, boucle agent et ordonnanceur. Une interruption réseau après réception possible par le fournisseur peut rendre l’issue d’un appel inconnue : ne pas promettre un coût exactly-once.

## 8. Ce qui est prouvé et ce qui reste à qualifier

Déjà vérifié dans la recherche : identité AWS du compte convenu ; profil Astra actif ; invocations produit antérieures avec identifiants de requête ; un `InvokeWebSearch` réussi ; configuration de journalisation des invocations Bedrock vide lors du contrôle ; aucun AgentCore Runtime dans la liste vérifiée. Ces faits ne prouvent pas la capacité d’une nouvelle architecture ni ses performances sous charge.

Les capacités de frameworks proviennent de code/documentation. La recherche antérieure a vérifié `ListAgentRuntimes` et exécuté `InvokeWebSearch` ; elle n’a ni déployé ni invoqué un agent hébergé dans AgentCore Runtime. Les opérations applicatives Step Functions, Lambda, S3/DynamoDB et AgentCore Memory/Gateway/Runtime, ainsi que les quotas utiles à une exploitation prolongée, restent à qualifier. Aucun nouvel appel AWS n’a été fait pour cette conception.

**Épreuve proposée après validation**, sur un même petit dossier et des fixtures reproductibles :

| Situation | Résultat attendu pour qualifier le moteur |
|---|---|
| Réponse humaine pendant un calcul en cours | Nouvelle révision conservée ; réponse tardive identifiée et non appliquée si son `read_set` est obsolète |
| Deux recherches partagent une source mais divergent sur son usage | Une capture versionnée réutilisable, deux interprétations attribuées et éventuellement contradictoires |
| Arrêt après dépôt d’artefact avant commit | Pas de faux résultat validé ; orphelin détectable et reprise sans perte silencieuse |
| Arrêt après commit avant checkpoint | Reprise reconnaît le commit existant et ne l’applique pas une seconde fois |
| Deux branches modifient la même contrainte | Conflit visible ou maintien de branches distinctes, jamais écrasement |
| Erreur d’outil, credentials expirés, budget atteint | Erreurs structurées ; état partiel/attente adapté ; aucun récit de réussite fabriqué |
| Reprise après mise à jour du framework | Migration contrôlée ou reconstruction depuis le dossier ; archive originale conservée |
| Travail de chaque rôle | Opérations, décisions et pièces identifiables ; aucune preuve basée seulement sur quatre libellés dans une interface |

Comparer LangGraph, Strands Graph et le moteur explicite sur ces invariants, l’effort d’intégration, les dépendances, le coût et la lisibilité du diagnostic. La qualification ne demande pas de reproduire trois produits complets.

## 9. Décisions autonomes et changements de direction

**Avant validation du Prompt 3 :** aucune construction. La présente recommandation n’est pas cette validation.

**Après validation de la conception**, relèvent du responsable technique : choix final entre les moteurs satisfaisant le contrat, versions compatibles, organisation des modules, schéma de tables, index, stockage des empreintes, mécanisme de verrouillage, adaptateurs et tests. Ces choix doivent être motivés et traçables ; ils ne requièrent pas un vote du porteur sur chaque préférence de bibliothèque.

**Demandent un accord parce qu’ils changent la direction :** fusion/suppression d’un rôle, réduction du parcours à un questionnaire ou allocateur figé, abandon de la révision/provenance, changement de route d’inférence, déplacement de l’usage local vers un service partagé, nouvelle audience ou transmission de données, dépendance à un abonnement/service payant modifiant le cadre convenu. Le constat d’une difficulté de framework n’autorise pas ces changements silencieux.

Une optimisation purement technique n’est pas un changement de direction si elle conserve les responsabilités, documents, droits, comportements utilisateur et garanties acceptés. Si aucun candidat ne respecte ces conditions, documenter précisément l’obstacle avant de proposer une modification du contrat.

## 10. Sources techniques et portée de lecture

- [Recherche : contrats, critique et mémoire](../recherche/aws_agentique/02_orchestration_critique_et_contrats.md) ; [journal des implémentations](../recherche/aws_agentique/03_journal_implementations_et_ressources.md) ; [annexe des 134 liens d’atelier](../recherche/aws_agentique/04_annexe_atelier_134.md). Ces documents distinguent code inspecté, lecture ciblée et fonctionnement réellement testé.
- **LangGraph U254/U255** : [persistance](https://docs.langchain.com/oss/python/langgraph/persistence) ; [code `Command` et `interrupt`](https://github.com/langchain-ai/langgraph/blob/08a2016953789a4f579b4d36bd1967941ec62012/libs/langgraph/langgraph/types.py#L843). Corps documentaire et code ciblé lus, pas intégration exécutée.
- **Strands U126**, documentation Graph archivée dans `../recherche/aws_agentique/sources/strands_graph_docs.txt:1134` ; [code de sérialisation/reprise](https://github.com/strands-agents/sdk-python/blob/c8e1351a5a6218c8f5c2417534aedbd021882a76/strands-py/src/strands/multiagent/graph.py#L1354). Les passages 1354–1408 et 1560–1596 ont été relus pour cette conception.
- **Strands U421/U456** : [Vended tools](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/), [MCP](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/). Passages outils, héritage, transports et filtrage lus dans l’annexe atelier ; pas serveur lancé.
- **AWS U038** : [Standard/Express](https://docs.aws.amazon.com/step-functions/latest/dg/choosing-workflow-type.html), tableau d’intégrations et sémantique lus ; **U116** : [limites Lambda](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), passages des familles et durées relus. Aucune limite générale de page ne remplace les quotas effectifs du compte.
- **AWS U122** : [AgentCore overview](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html), sections Harness, Runtime, Memory et Gateway relues ; capacités documentées, services non déployés.
- **AWS U377** : [retries](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html), avertissement et mécanismes lus ; docstring botocore locale conservée dans `../recherche/aws_agentique/sources/atelier_botocore_retries.json`.
- [Preuves d’accès et limites de route](../recherche/aws_agentique/01_preuves_aws_et_recherche.md). La région d’entrée et un profil global ne prouvent pas une résidence physique exclusivement canadienne.
