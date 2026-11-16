> **Conception, non construite** (15 novembre 2026). Rien de ce document n'est en service dans le produit. Les passages sur le calendrier, les décisions à prendre et l'organisation du travail sont historiques : ce ne sont pas des consignes. Certaines pièces de travail citées (`research/fiches/`, `research/R08-…`, `docs/etat.md`, `docs/coordination.md`) ne sont pas dans cette archive. Entrée de l'archive : `LIRE_EN_PREMIER.md`.

# 06 — Comparatif technique et choix motivés

Les contrats des documents 02 à 05 disent ce qu'il faut exécuter. Ce document compare les moyens sérieux de le faire, à partir de petits essais menés le 15 novembre entre 14 h et 15 h, hors produit. Chaque essai a son dossier sous `research/experiences/technique/`, avec un `LISEZMOI.md`, ses scripts et ses sorties ; les comptes rendus sont dans `research/fiches/architecture/technique-*.json`.

Trois règles ont été tenues. Aucune ressource AWS n'a été créée, modifiée ni supprimée. Rien n'a été installé dans le projet : les bibliothèques essayées l'ont été dans des environnements jetables, et `pyproject.toml` comme `uv.lock` sont inchangés. Toutes les inférences sont passées par Amazon Bedrock (29 appels du modèle Haiku 5.5, un reclassement, deux plongements, douze recherches web par AgentCore, dont onze pour lire la documentation). Chaque conduite a été observée une fois, sur un seul modèle, qui n'est pas celui que le produit emploie par défaut.

## 1. Ce qu'il faut exécuter

| Besoin | Ce que les contrats exigent |
|---|---|
| Enchaînement | Des tâches déduites du graphe de questions ; aucune transition décidée par un modèle ; des sous-questions ouvertes en cours d'étude ; des bornes de réouverture |
| Persistance | Des pièces immuables adressées par leur contenu ; un journal en ajout seul, chaîné ; un état en vigueur déduit ; des branches |
| Reprise | Ne refaire aucune tâche terminée ; survivre à l'arrêt du processus ; suspendre sur une question sans bloquer le reste |
| Invalidation | Périmer exactement ce qui dérive d'une pièce remplacée ; rétablir sans recalcul ce qui redevient valable |
| Outils | Des outils disjoints par rôle ; une sortie à structure imposée ; un refus journalisé ; aucune sortie tronquée admise |
| Calculs | Rejouables hors ligne : graine, version du code et du catalogue, empreintes des données |
| Recherche | Bibliothèque de fiches, recherche pendant la demande, citation contrôlée par le code |
| Observation | Savoir, pour chaque pièce, qui l'a produite, avec quel appel, et pouvoir le prouver |
| Interface | Suivre une étude, poser une question, enregistrer un affichage et une réaction |
| Route AWS | Toute inférence par Amazon Bedrock ; une contribution réelle d'AWS à la solution |

## 2. Les options et ce qui a été essayé

| Option | Ce qui a été fait | Verdict de l'essai |
|---|---|---|
| **A. Dossier et greffier maison**, bibliothèque standard de Python | Un prototype de 313 lignes et 118 assertions, sans appel de modèle : révision d'un seul champ, variante, arrêt d'un processus puis reprise, écritures concurrentes, retour en vigueur, retrait d'une pièce erronée, affichage et réaction, export des relations | Retenir pour le dossier et l'enchaînement. Ne fait rien de la boucle d'un rôle |
| **B. LangGraph** 1.2.22, avec `langchain-aws` et un point de reprise SQLite | Onze essais, 8 appels de modèle : graphe de quatre nœuds, question à la personne sur trois processus, panne en plein nœud, historique, correction amont, bifurcation, écritures concurrentes, événements, télémétrie | Écarter comme dossier et comme greffier. Utile, au plus, pour suspendre et reprendre une exécution |
| **C. Strands Agents** 1.65.0, la bibliothèque d'agents d'AWS | Dix essais, 19 appels de modèle : outil, sortie imposée valide, invalide et tronquée, outils disjoints, limite de tours, interruption, session sur deux processus, graphe, traces | Retenir pour la boucle d'un rôle seulement. Écarter son graphe et ses sessions |
| **D. Services AWS d'enchaînement et de persistance** : Step Functions, S3, DynamoDB, AgentCore, bases de connaissances, garde-fous | En lecture seule : inventaire du compte, simulation des droits, validation d'une définition d'une quinzaine d'états, dix-sept essais d'états isolés, nos contrats de dossier sur un émulateur local, lecture de la documentation ; 5 appels de modèle pour la recherche | Retenir ce qui marche sans ressource. Écarter pour porter le produit |
| **E. Boucle directe sur l'API Converse de Bedrock** | Déjà en service dans le produit actuel (`src/datathon2026/agent.py`) : outils, raison d'arrêt, identifiant de requête AWS gardé. Le produit n'a ni outil forcé ni sortie à schéma imposé : ils n'ont été essayés que hors produit (R09, M1 et M2). Non réessayée aujourd'hui | Voie proposée pour la boucle des rôles, sans qu'un essai l'ait départagée de la voie C |

## 3. Comparatif par besoin

« Testé » veut dire exécuté aujourd'hui ; « lu » veut dire lu dans le code ou la documentation ; le reste est dit non établi.

| Besoin | A. Maison | B. LangGraph | C. Strands | D. Services AWS | E. Converse direct |
|---|---|---|---|---|---|
| **Enchaînement** | Une tâche part quand ses entrées sont en vigueur, jamais deux fois pour les mêmes entrées. Testé sur un graphe fixe de six tâches ; sous-questions en cours d'étude et bornes de réouverture non faites | Arêtes fixées dans le code ; suit le flot de contrôle, pas les dépendances entre données. Création de tâches en cours d'exécution non éprouvée | Boucle d'un rôle seulement, avec une raison d'arrêt explicite. Testé | Step Functions décide hors de tout modèle : 15 essais d'états sur 17 donnent la transition qu'attendait la chaîne du cadre de travail ; l'une au moins (un second « change » mène à « interrompue ») n'est plus celle du contrat (04, section 4). Aucune exécution réelle | Boucle d'un rôle seulement |
| **Persistance** | Pièces sous l'empreinte de leur contenu, journal chaîné par branche, état déduit, altération détectée. Testé | Points de reprise horodatés, sans empreinte ; un point se réécrit en place ; ni nom de branche, ni tête par branche. Testé | Une session est un historique de conversation modifiable. Testé | S3 versionné refuserait un écrasement ; l'état déduit et les branches restent à écrire. Émulateur local seulement | Aucune |
| **Reprise** | Processus tué pendant une tâche : un autre reprend et n'exécute que le reste ; les deux tentatives sont au journal. Testé. Panne entre une pièce et son événement : non essayée | Son point fort : la question survit à l'arrêt, les nœuds terminés ne sont pas refaits. Le nœud interrompu repart de son début. Testé | Un rôle reprend dans un autre processus. Le graphe perd la sortie du nœud amont et se déclare terminé. Testé | Reprise d'une exécution échouée, dans les quatorze jours. Lu | Sans objet : une tâche de rôle est atomique, on la relance |
| **Invalidation** | L'ensemble périmé est exact pour six champs corrigés un à un ; une valeur rétablie remet les pièces en vigueur sans aucun appel. Testé | Absente : tout l'aval est rejoué. Le cache de nœuds évite des recalculs, mais sert un résultat obsolète si la version du code n'est pas dans sa clé. Mesuré | Aucune | Aucun service ne la fournit | Sans objet |
| **Outils et erreurs** | Droits de dépôt par auteur ; une exception devient un événement ; deux échecs interrompent l'étude. Testé. Portes de contenu à écrire | Outil d'un autre rôle refusé ; erreurs rendues au modèle si on l'active. Testé | Outils par rôle, crochet de refus journalisé, limite de tours, sortie validée, troncature signalée. Testé. Des réessais cachés par défaut | Réessais et renvois conformes, sur erreurs simulées | Liste d'outils par appel, raison d'arrêt, identifiant de requête : en service. Outil forcé et sortie à schéma imposé : offerts par l'API, essayés hors produit, absents du produit |
| **Calculs** | Clé d'une tâche : nom, version, empreintes des entrées. Pièges constatés : 1 et 1.0 n'ont pas la même empreinte, deux codages d'un accent non plus | N'apporte rien | N'apporte rien | N'apporte rien ; Lambda demanderait d'empaqueter les bibliothèques de calcul | Sans objet |
| **Recherche** | Rien | Rien | Non essayée | Recherche web d'AgentCore, reclassement Cohere et plongements Titan appelés depuis un script d'essai, hors produit, sans ressource ; citation contrôlée par le code. Testé une fois : la citation obtenue existe mot pour mot, mais ne répond pas clairement à la question. La recherche rend des extraits ; la lecture d'un document entier reste à essayer. Une base de connaissances demanderait quatre à cinq ressources | Sans objet |
| **Observation** | Le journal est la trace, lisible avec un éditeur de texte ; export PROV-JSON relu par la bibliothèque `prov`. Testé | Flux d'événements de moteur ; traçage vers un tiers inactif par défaut. Testé | Mesures par cycle ; pas d'identifiant de requête AWS sans un crochet supplémentaire. Testé | Sans rien créer, l'historique CloudTrail garde chaque appel de modèle, retrouvé par son identifiant, et CloudWatch les compte. Le reclassement et la recherche web n'y figurent pas. Testé | Identifiant de requête, jetons et raison d'arrêt dans chaque réponse |
| **Interface** | Une bibliothèque appelée par l'application : cinq écritures, quatre lectures ; pas de flux, l'interface relit l'état. Lu dans le code ; affichage et réaction testés dans un seul processus | Événements de moteur (nœud, canal), à traduire en événements de dossier. Testé | Une interruption rend un objet simple. Testé au niveau de l'API | L'interface devrait garder un jeton et le renvoyer. Non essayé | Sans objet |
| **Route AWS** | Aucune contribution par elle-même | Bedrock seul hôte contacté. Testé | Bedrock seul hôte contacté. Testé | Tout | Bedrock |
| **Coût** | Aucune dépendance ; un code à nous, à maintenir | 40 paquets de plus, dont un client de traçage tiers, inactif | 40 paquets de plus, Strands compris | Des ressources à créer la veille de la fermeture du compte ; rien ne survit à lundi 13 h 59 | Aucune dépendance nouvelle |

## 4. Choix proposé

**Le dossier et l'enchaînement : écrits par nous (A).** Aucune bibliothèque essayée ne fournit ce qui fait la valeur du dossier : l'adressage par contenu, l'état déduit, l'invalidation ciblée, le retour en vigueur. LangGraph, sans réglage, rejoue tout l'aval d'une correction ; son cache de nœuds évite ces recalculs, mais ne marque rien comme périmé et sert un résultat obsolète si la version du code n'entre pas dans sa clé ; il accepte deux écritures concurrentes sans erreur ; les sessions de Strands sont des fichiers modifiables ; aucun service AWS ne déduit ce qui dépend d'une pièce remplacée. Le prototype montre que ces conduites tiennent dans quelques centaines de lignes, dans le vocabulaire même du contrat. Support : des fichiers (un journal par branche, des pièces rangées par empreinte) pour une démonstration sur un poste, parce qu'un tiers les lit sans outil et que l'export est une simple copie ; SQLite si plusieurs processus doivent écrire.

**La boucle d'un rôle : deux voies, et un choix qui n'est pas tiré d'un essai.** Un rôle devient une tâche courte et atomique du greffier : il reçoit des pièces, il appelle le modèle avec ses seuls outils, il rend une sortie structurée que la porte admet ou refuse. Deux voies tiennent cette boucle. L'essai Strands conclut pour Strands, l'appel direct restant un repli. Je propose l'ordre inverse, appel direct d'abord (E), Strands en repli (C), pour deux raisons qui ne sont pas des mesures : le produit a déjà une boucle directe, qui garde l'identifiant de requête de chaque appel ; et ajouter quarante paquets la veille du dépôt est un risque que rien n'oblige à prendre. Ce que cette boucle n'a pas encore : l'outil forcé et la sortie à schéma imposé. Aucun essai ne dit laquelle des deux voies est la plus simple à tenir pour cinq ou six conversations ; un essai court, la même tâche écrite des deux façons, le dirait.

**La recherche : AWS, sans ressource (D, en partie).** La recherche web d'AgentCore pour la recherche pendant la demande, le reclassement par Bedrock pour la bibliothèque de fiches, et le contrôle des citations par notre code. Ces moyens ont été essayés depuis des scripts d'essai, hors produit.

| Moyen | Usage pour l'agent 1 | Essayé | Limite constatée | Sort proposé |
|---|---|---|---|---|
| Recherche web d'AgentCore | Trouver des documents pendant la demande | Oui : elle a servi aux 211 recherches du matin, puis à un essai de bout en bout | Rend des extraits, qui changent dans le temps ; ne laisse aucune trace dans CloudTrail ni dans CloudWatch | Retenue ; l'extrait, son empreinte et l'identifiant de requête sont gardés au moment de l'appel |
| Lecture d'un document téléchargé | Lecture approfondie, par le spécialiste « lecteur » | Non, dans une chaîne de produit ; à la main le matin, pour constituer le registre | Textes payants ou illisibles ; consignes cachées possibles | Outil du produit, à essayer ; critère E7 du document 09 |
| Reclassement Cohere par Bedrock | Classer les fiches et les extraits pour une question | Oui, une fois | Qualité en français, sur nos fiches, non mesurée ; aucune trace côté AWS | Retenu ; à mesurer sur des couples question-fiche |
| Plongements Titan | Recherche par proximité | Oui, deux appels | Sans utilité pour quelques dizaines de fiches | Non retenu dans la première version |
| Base de connaissances Bedrock, S3 Vectors | Bibliothèque gérée, citations intégrées | Non : documentation lue | Quatre à cinq ressources à créer | Écartée |
| Contrôle de citation | Existence mot pour mot d'un passage | Oui (R09, M2 ; essai du jour) | Prouve l'existence, pas le soutien | Par notre code |

**L'observation : notre journal, et la preuve tenue par AWS.** Le journal du dossier garde l'identifiant de chaque appel ; l'historique CloudTrail et les métriques CloudWatch permettent à un tiers de retrouver côté AWS les appels de modèle, et eux seuls : le reclassement et la recherche web n'y figurent pas. Ces relevés sont à exporter avant la fermeture du compte.

**Écartés pour porter le produit** : LangGraph ; le graphe et les sessions de Strands ; Step Functions, DynamoDB, Lambda, les bases de connaissances, et les composants d'AgentCore autres que la recherche web. Aucun ne fournit l'invalidation ciblée ni le rejeu hors ligne. LangGraph et Strands ajoutent chacun quarante paquets ; les services AWS demandent des créations de ressources la veille de la fermeture. La définition Step Functions validée décrit la chaîne du cadre de travail, avant les corrections de la revue : elle est gardée comme trace de l'essai, pas comme description des transitions.

Règle retenue pour la suite [L03] : une bibliothèque ne porte une fonction à contrat (porte, persistance, reprise, invalidation) que si un essai a montré ce qu'une étape aval reçoit, ce qui déclenche une étape, ce qui est écrit pour la reprise, et si cela peut être réécrit.

**Ce qui dépend d'un accord** (décision de direction 2) : un compartiment S3 versionné comme copie des pièces et du journal ; un garde-fou Bedrock en second contrôle de la restitution, à essayer d'abord en français ; le journal des invocations Bedrock, qui est un réglage de tout le compte, lequel est partagé.

### Ce que les essais imposent aux contrats

| Constat | Précision portée aux contrats |
|---|---|
| Si l'auteur ou la date entrent dans l'empreinte, une tâche refaite ne retrouve jamais la même pièce | L'empreinte ne couvre que le contenu ; auteur, activité, entrées et date vivent dans l'événement qui dépose la pièce (02, principe 2) |
| Deux pièces de même contenu n'en font qu'une : un retrait frapperait deux contextes | Une pièce cite ce sur quoi elle porte (02, principe 2) |
| 1 et 1.0, ou deux codages d'un accent, donnent deux empreintes | Forme canonique des nombres et des textes avant toute empreinte (02, section 8) |
| Une écriture de la personne, préparée pendant qu'une tâche s'exécute, est refusée dès que le journal avance | Les faits d'exécution sont rejoués d'office ; une réaction de la personne n'est jamais perdue (02, section 7) |
| Une question posée au milieu de la boucle d'un rôle laisse une conversation à moitié faite hors du dossier, et rejoue ce qui précède à la reprise | Une tâche de rôle est atomique : la question à la personne est une pièce de sortie (03, règle 4) |
| Une sortie tronquée peut avoir l'apparence d'une sortie valide | La porte refuse toute sortie dont la raison d'arrêt n'est pas celle attendue ; l'événement garde le modèle, les jetons, la raison d'arrêt et l'identifiant de requête (03, règles 4 et 5) |
| Une bibliothèque d'agents peut relancer des appels sans le dire | Limites explicites de tours et de réessais ; le compte des appels se lit sur le journal et se rapproche de CloudWatch (03, règle 4 ; 09, H1 et H6) |

### Ce qui reste à vérifier avant de construire

- Le verrou de fichier qui refuse une écriture concurrente n'a été essayé que sur ce poste ; le module qu'il emploie n'existe pas sous Windows, et sur un disque partagé ou synchronisé il n'est pas sûr. À essayer sur la machine cible, ou passer à SQLite.
- Tous les essais ont tourné une fois, sur le modèle Haiku 5.5 ; le produit en emploie un autre par défaut. La sortie imposée, les outils disjoints et la limite de tours sont à refaire sur le modèle retenu pour chaque rôle.
- Dans les essais, le raisonnement du modèle a épuisé un plafond de jetons trop bas : trois troncatures, dont deux non voulues. Il faut un plafond qui garantisse une sortie non vide. Un arrêt « content_filtered » est resté inexpliqué.
- La lecture d'un document entier par le spécialiste « lecteur » n'a pas été essayée.
- Après lundi 13 h 59, toute inférence demande un autre compte Bedrock : le modèle et le compte doivent être des paramètres.
- Une panne entre le rangement d'une pièce et son événement, et la reprise d'une tâche écrite par un modèle, n'ont pas été essayées.
- Les mêmes calculs donnent-ils les mêmes empreintes sur deux machines ? Non établi.
- Le prototype relit tout le journal à chaque opération : suffisant pour quelques dizaines d'événements, pas au-delà.
- Pourquoi le reclassement et la recherche web n'apparaissent ni dans CloudTrail ni dans CloudWatch : non établi. D'ici là, leur seule preuve est l'identifiant gardé par le produit.
- Les droits de création de ressources ne sont que simulés ; une limite de l'atelier peut refuser une création réelle.

## 5. La route d'inférence, vérifiée à 14 h 55

- **Session principale de développement** : Amazon Bedrock, profil `alphaforge`, région `us-east-1`, modèle `us.anthropic.claude-fable-5-2` ; aucune clé directe dans l'environnement. Les sous-agents des workflows héritent de cette route.
- **L'exception signalée demeure.** Une session de bureau nommée « Projet Datathon-2026 », inactive, est celle que `docs/coordination.md` dit fonctionner sur abonnement. Je ne l'ai pas interrogée : lui écrire déclencherait une inférence hors AWS. Elle se lève en fermant cette session, ou en la relançant par `scripts/claude-bedrock.sh`. Une session de terminal plus ancienne, inactive elle aussi, n'a pas été vérifiée.
- Le compte est partagé : CloudWatch y montre des appels qui ne viennent pas de ce projet. Un rapprochement entre notre journal et les métriques ne peut donc se faire qu'« à l'activité d'autres utilisateurs près », ou par identifiant de requête dans CloudTrail.

Le détail, et les relevés de 14 h 01 et 14 h 30, sont dans `research/R08-outils-routes-et-ressources-2026-11-15.md`.

## 6. Journal des briques candidates

Le dossier du porteur « Réutiliser des briques éprouvées » (section 5) proposait cinq sorts : utiliser, adapter, reproduire pour vérifier, s'inspirer, écarter. Voici ce que l'architecture en fait, et ce qui a réellement été vérifié.

### Réutiliser telles quelles

| Brique | Rôle dans l'architecture | Vérifié | Reste à vérifier |
|---|---|---|---|
| API Converse de Bedrock, sortie à schéma imposé | La boucle de chaque rôle | En service pour l'appel et les outils ; sortie imposée essayée hors produit (R09, M1 et M2) | Le modèle, le prix et le profil d'inférence retenus pour chaque rôle |
| Recherche web d'AgentCore | La recherche pendant la demande | Essayée depuis un script d'essai | Sa trace côté AWS ; la lecture d'un document entier |
| Reclassement Cohere par Bedrock | Recherche dans la bibliothèque de fiches | Essayé | La qualité du classement en français, sur nos fiches |
| Bibliothèque `arch` (rééchantillonnage par blocs) | Diagnostic de longueur de bloc ; le rééchantillonnage lui-même est écrit par nous | Essayée (R09, X1) | Cohérence numérique avec notre code |
| Bibliothèque `prov` | Relecture de l'export des relations | Aller-retour identique sur 156 enregistrements | Aucun validateur des contraintes de la norme |
| Textes canadiens sur la connaissance du client | Vocabulaire de la fiche de qualification | Lus dans des consolidations anglaises non officielles (R07) | Relecture dans le texte officiel français avant toute citation ; ne jamais se présenter comme représentant inscrit |
| Historique CloudTrail et métriques CloudWatch | Preuve des inférences tenue par AWS | Appels retrouvés par identifiant | Export avant lundi 13 h 59 |

### Adapter

| Brique | Adaptation | Vérifié |
|---|---|---|
| Schéma de décision typé et sentinelle de revue (TradingAgents) | Nos pièces typées et nos portes ; aucun nombre calculé écrit par un modèle | Principe en service dans le produit (`evidence.py`) |
| Règle « donnée retenue si non datable » (TradingAgents) | Étendue à la macro et au change : règle du projet | En service pour le change (dernier taux connu). Pour la macro : règle écrite, non codée ; aucune série mensuelle n'est encore employée |
| Opérateur qui émet un nombre et un code machine (FinRobot) | Nos calculs et nos rendus | En service pour les nombres ; rendus à écrire |
| Règle d'arrêt par valeur de l'information | Réduite à : poser la question si deux valeurs du domaine changent le cas | Non essayée |
| Séquence de recueil des préférences de durabilité (ESMA) | Table « préférence vers contrainte » | Calculs du parcours de Mateo faits |
| Tableau de comparaison par questions | Table des options de la note | Non essayé auprès de lecteurs |
| Grille d'échecs des systèmes à plusieurs agents (MAST) | Étiqueter nos propres traces dans les essais d'apport | Non fait |
| Strands Agents | La boucle d'un rôle seulement, en solution de repli | Essayé aujourd'hui |

### Reproduire pour vérifier

| Résultat | État |
|---|---|
| Sensibilité des corrélations à l'alignement des séries | Fait (R09, X2) : la corrélation dépend de la convention pour 28 % des paires |
| Rendement reconstruit contre clôture ajustée | Une erreur trouvée et corrigée dans notre propre calcul quotidien (R09, X3) ; contrôle sur un dividende connu : à faire |
| Cohérence numérique entre bibliothèques | À faire |
| Variation de la conclusion d'une exécution à l'autre | À faire : critère I7 du document 09 |
| Injection par un document piégé | À faire : critère E7 du document 09 |
| Calibration du rééchantillonnage sur des processus connus | Fait à trois ans (R09, X8) ; à étendre |

### S'inspirer

| Idée | Ce que l'architecture en retient |
|---|---|
| Un agent de citation séparé | L'existence d'un passage est contrôlée par le code ; son soutien est jugé à part |
| Un graphe de flux de données pour la provenance | Les liens « dérive de » et le manifeste d'entrées |
| Explication contrastive (« A plutôt que B ; cela changerait si… ») | Les quatre parties de la conclusion, le rendement d'équilibre, le test inversé |
| Initiative mixte : corriger doit coûter moins qu'accepter une supposition | Aucune valeur par défaut ; les trois gestes |
| Arbre de justification | Le graphe de preuves, qui répond à « pourquoi ? » |
| Distinguer « aucune preuve » de « preuves contradictoires » | « Sans preuve » d'un côté, « contradiction entre sources » de l'autre |
| Jusqu'où les entrées peuvent bouger avant que la décision change | Le balayage, et la question posée après l'analyse |

### Écarter

| Brique | Motif |
|---|---|
| Contraction de la covariance (`scikit-learn`) | R09, X5 : fausse telle quelle sur un univers qui mêle obligations et cryptoactifs ; inutile tant qu'aucun rôle n'optimise des poids |
| LangGraph comme dossier ou comme greffier | Ni empreinte, ni ajout seul garanti, ni refus d'une écriture concurrente ; sans réglage, tout l'aval est rejoué, et son cache ne marque rien comme périmé (essais 5 à 8) |
| Graphe et sessions de Strands | Sortie perdue à la reprise ; état modifiable hors du dossier |
| Step Functions, DynamoDB, Lambda, bases de connaissances, autres composants d'AgentCore | Aucune invalidation ciblée, aucun rejeu hors ligne, ressources à créer la veille de la fermeture ; la définition Step Functions validée, qui décrit la chaîne d'avant les corrections, est gardée comme trace de l'essai |
| Règles de contrôle d'accès d'AgentCore sur les appels d'outils | Les outils disjoints sont déjà imposés par la liste remise à chaque appel |
| Programmation dynamique de probabilité d'objectif ; échelle de risque à cinq niveaux | Le système ne produit ni probabilité d'atteindre un objectif, ni niveau de risque (document 05) |
| Graphique de fréquences par points | Le compte « sur 100 » n'est pas retenu dans la première version (C13) |
| Débat libre entre agents ; critique non ancrée | Une objection n'agit que par un test calculé |
| Formulation de calcul écrite par un modèle | Formulations du catalogue seulement |
| Les éléments que le dossier du porteur écartait déjà | Motifs inchangés |
