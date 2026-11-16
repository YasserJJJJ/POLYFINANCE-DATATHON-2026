> **Conception, non construite** (15 novembre 2026). Rien de ce document n'est en service dans le produit. Les passages sur le calendrier, les décisions à prendre et l'organisation du travail sont historiques : ce ne sont pas des consignes. Certaines pièces de travail citées (`research/fiches/`, `research/R08-…`, `docs/etat.md`, `docs/coordination.md`) ne sont pas dans cette archive. Entrée de l'archive : `LIRE_EN_PREMIER.md`.

# 00 — Architecture à quatre agents : synthèse du fonctionnement proposé

Rédigé le 15 novembre 2026, entre 14 h et 17 h 45. **Ceci est une proposition à valider.** Rien n'est construit : le produit n'a pas été modifié, aucune ressource AWS n'a été créée, rien n'a été commité. La validation des recherches autorisait la conception ; elle ne valait pas validation de l'architecture, et ce document ne la présume pas.

Les neuf livrables demandés sont dans ce dossier ; l'index est à la section 10.

**Quelques mots employés partout.**

| Mot | Sens |
|---|---|
| Dossier | Tout ce qu'une étude produit, conservé pièce par pièce, avec l'auteur de chaque pièce et ce dont elle découle |
| Catalogue | Les règles écrites d'avance par l'équipe, avant toute demande : quelles décisions le produit sait traiter, quelles méthodes de calcul, quels seuils. Il n'est pas encore écrit |
| Porte | Un contrôle fait par du code, qui admet ou refuse une pièce avant qu'elle entre au dossier |
| Greffier | Le code qui ordonne les tâches et tient le dossier ; ce n'est pas un modèle |
| Batterie fixe | La série de vérifications que le code refait sur toute analyse : autre hypothèse de rendement, une année retirée, autre fréquence |
| Relecteur, vérificateur | Dans ces documents : un sous-agent du même modèle, chargé de réfuter. Jamais une personne, sauf si c'est écrit |

## 1. Ce qui se passe quand une personne pose une demande

1. **La personne écrit sa demande**, avec ses mots. Rien n'est supposé à sa place.
2. **L'agent 0 en fait un problème.** Il rattache la demande à une décision que le catalogue connaît, et extrait chaque fait avec la phrase qui le fonde. Le code classe ensuite ce qui manque, d'après une table. Une seule sorte de manque suspend l'étude : une variable sans laquelle rien ne se calcule, comme le portefeuille de départ. Le reste (la part envisagée, la perte acceptée, l'horizon) ne se demande pas avant l'analyse : cela s'essaie sur toute une plage.
3. **L'agent 1 cherche ce qu'on sait.** Les questions de recherche sont ouvertes par le code, d'après la décision et ce que l'agent 0 a relevé dans la demande. Pour chacune, l'agent 1 réemploie une fiche de la bibliothèque, vérifie une source qui a pu changer, ou cherche sur le web par AWS. Il dit ce que chaque source établit, dans quelles conditions, et ce qui la contredit. Il en tire un plan : quelles méthodes de calcul sont permises pour cette demande, avec quelles réserves.
4. **L'agent 2 résout.** Il choisit la mesure qui correspond à l'objectif, arrête son plan avant les calculs d'analyse, fait calculer, puis écrit une conclusion en quatre parties : ce qui tient sous toutes les hypothèses, ce qui dépend d'une hypothèse, ce qui dépend de la personne, ce qu'aucun calcul ne donne.
5. **Sa conclusion est contestée**, d'abord par la batterie fixe, puis par un contradicteur qui n'a pas vu son raisonnement. Une objection ne vaut que par un test que le code exécute. Si le test renverse une affirmation, la restitution est bloquée jusqu'à ce que l'agent 2 l'ait amendée, et le code vérifie l'amendement.
6. **L'agent 3 restitue.** Un résumé qui tient seul, puis le détail, à trois profondeurs qui disent les mêmes choses. Chaque nombre s'ouvre sur son calcul, chaque source sur son passage. Ce qu'on ne peut pas dire occupe la même place que ce qu'on peut dire.
7. **Une question, s'il y en a une qui compte.** Le code repère l'inconnue dont la réponse changerait la conclusion ; l'agent 3 la pose. S'il n'y en a pas, il ne demande rien.
8. **La personne répond, corrige ou explore.** « Je me suis trompé », « ma situation a changé », « et si… » sont trois gestes différents. Dans les deux premiers cas, seul ce qui dépendait de l'ancienne valeur est refait ; dans le troisième, une branche s'ouvre et rien n'est perdu.

Tout cela s'inscrit dans le **dossier** : chaque pièce y est conservée telle qu'elle a été écrite. Un tiers peut y lire comment la demande est devenue une conclusion, et pourquoi la conclusion a changé.

## 2. Les quatre responsabilités

| | Agent 0 — Qualification et formalisation | Agent 1 — Recherche critique | Agent 2 — Analyse et résolution | Agent 3 — Restitution et interaction |
|---|---|---|---|---|
| **Il reçoit** | La demande, le profil de l'énoncé, les réponses | Les questions de recherche, la bibliothèque, les données | Le problème formalisé, le plan des méthodes | La conclusion, les objections, les abstentions |
| **Il décide** | La décision en jeu ; les faits et leur citation ; ce que la demande signale ; la forme mesurable d'un objectif | Quelles sources valent pour ce cas ; quand approfondir ; quel statut donner à chaque méthode ; quelles réserves | La mesure ; la méthode parmi celles permises ; les options à ajouter ; ce que la conclusion affirme ; comment amender | Les mots, le détail de chaque profondeur, l'ordre des blocs sous une tête fixée ; la formulation d'une question |
| **Il ne peut pas** | Déduire une valeur non dite ; lever une contradiction ; classer un titre | Calculer ; assouplir une analyse sur la foi d'une source non relue | Écrire un nombre ; retirer une option de base ; introduire un actif que personne n'a nommé ; fixer un seuil | Créer un fait ; changer la nature d'un résultat ; interpréter un silence |
| **Il produit** | La fiche de qualification | Le dossier de preuves, le plan des méthodes, la fiche produit | La note d'analyse et sa conclusion | La restitution, les questions d'après l'analyse |
| **Ce qui le contrôle** | Chaque citation retrouvée mot pour mot ; chaque nombre retrouvé dans sa citation | Chaque passage retrouvé ; chaque méthode testée sur les données | Plan arrêté avant les calculs ; chaque affirmation reliée à un calcul ou, pour une abstention reprise, à la pièce qu'elle reprend | Aucune affirmation omise ; aucune phrase sans affirmation |
| **Comment on saura qu'il apporte quelque chose** | Demandes difficiles annotées à la main | Jugements relus par deux personnes ; le plan change avec la demande | Demandes où la bonne mesure n'est pas celle de l'exemple | Ce que des lecteurs comprennent, comparé à ce qu'ils croient comprendre |

Deux précisions sur l'interaction. Avant l'analyse, c'est l'agent 0 qui rédige la question, et toute réponse entre par lui. L'agent 3 propose le classement d'une réaction ; la personne le confirme, et une table de code l'achemine. Les contrats complets, en dix points par agent, sont dans le document 03.

## 3. La place du contradicteur et des fonctions d'organisation

Ces deux éléments pourraient, mal placés, devenir une autre architecture sans qu'on l'ait décidé. Voici exactement ce qu'ils sont.

**Le contradicteur** est un spécialiste de la responsabilité 2 : confronter les hypothèses fait partie de la mission de l'agent 2, et l'auteur d'une note la conteste mal. Dit sans détour, c'est une **cinquième conversation de modèle**, dans un contexte neuf ; ce n'est pas une cinquième responsabilité. Il n'a ni question propre, ni conclusion, ni parole vers la personne, ni pouvoir sur le travail des autres agents. Il choisit des objections dans une grille et les tests qui les tranchent ; il n'écrit aucun seuil et ne rend aucun verdict. Il est lancé pour toute note d'analyse, par une règle et non par un modèle. Ce n'est pas un contrôle indépendant, et le produit n'emploie pas ce mot. Le réduire à une batterie de tests, ou en faire un cinquième agent, serait un changement d'architecture : il vous reviendrait.

Un second spécialiste existe : le **lecteur de document**, que l'agent 1 emploie pour tout texte téléchargé. C'est une sixième conversation de modèle, qui n'a qu'un outil de lecture ; elle isole le reste du système d'une consigne cachée dans un document.

**Les fonctions d'organisation** sont du code : un greffier, des portes, des calculs, une batterie fixe, la qualification des données, l'interface. Elles ne sont pas neutres pour autant : le code calcule, rend des verdicts, désigne les comparateurs et la question à poser. Ces décisions de fond ne sont prises ni par un modèle pendant une demande, ni par le code de sa propre autorité : **elles sont écrites d'avance par l'équipe, dans le catalogue**. Pour chaque élément d'une conclusion, le dossier permet donc de dire de quelle main il vient : une règle écrite d'avance, un choix d'un modèle pendant la demande, ou une déclaration de la personne.

**Deux présences humaines.** La personne agit pendant l'étude. L'équipe agit hors exécution : elle tient le catalogue, qualifie les fiches de la bibliothèque, relit tout dossier montré hors de l'équipe. Personne n'approuve une conclusion ; il n'y a ni représentant inscrit, ni comité, ni conformité, et le produit le dit.

**Ce qui n'existe pas encore du côté des personnes.** Aucune fiche de la bibliothèque n'a été relue par un membre de l'équipe : celles qui existent ont été écrites et vérifiées par des sous-agents. Tant que c'est le cas, aucune réponse de l'agent 1 ne peut être dite « étayée » sans réserve, et la restitution le dira.

## 4. Les boucles

| Boucle | Ce qui la déclenche | Ce qui la borne |
|---|---|---|
| **Approfondir une recherche** | Aucune fiche ne répond ; une source a pu changer ; deux sources se contredisent ; une source n'est connue que par un résumé ; une méthode manque | Un budget ; à défaut de réponse, « sans preuve », avec ce qui a été cherché |
| **Remonter au problème** | Une découverte met en cause une hypothèse du problème : un test qui échoue sur le titre demandé, une mesure sans méthode | Le problème est reformulé, ou l'étude s'abstient ; une cause ne rouvre qu'une fois |
| **Contester et amender** | Un test renverse ou nuance une affirmation | Une confrontation par version de la note, une passe d'amendement ; au-delà, l'affirmation est dite « non résolue », avec les deux positions |
| **Réviser** | La personne répond, corrige, change de situation, conteste | Seul ce qui dérive de la pièce remplacée est refait ; le reste est réemployé |
| **Explorer** | « Et si… » | Une branche, qui ne touche pas à la ligne principale |

Une étude finit toujours dans un état calculé et affiché : arrêtée à la qualification (la demande n'est pas de celles que le catalogue traite) ; en attente de la personne ; interrompue ; ou menée à terme, avec deux mentions : sa couverture, entière ou partielle, et si elle dépend d'une condition. Une panne ne devient jamais une conclusion.

## 5. Ce que le système a le droit d'affirmer

Les expériences du matin ont montré que cinq ans de données n'établissent aucun niveau de risque, mais établissent le sens de certaines comparaisons. L'architecture en tire des règles de procédure, pas des vérités sur un titre :

- sept types de résultats, de la mesure historique à la conclusion insuffisamment étayée, chacun avec ce qu'il permet d'écrire, de titrer et de dessiner ;
- un sens de comparaison n'est dit « établi » que s'il tient sous chaque hypothèse de base et dans toutes les variantes ; s'il se renverse sous la seule hypothèse du passé prolongé, il est « établi avec réserve » ; sinon, « non établi » ;
- une proportion de trajectoires n'est jamais un chiffre de tête ni une probabilité ;
- le profil de risque de l'énoncé est repris comme une donnée déclarée ; ses composantes restent des inconnues ;
- une préférence ESG s'applique là où les données permettent de la vérifier, et donne ailleurs une abstention qui nomme ce qui manque ;
- un constat fait sur Robert ou sur Tesla n'est jamais une règle du moteur : il se remesure à chaque dossier.

## 6. Les moyens techniques

Quatre essais ont été menés, hors produit (document 06). Chaque conduite a été observée une fois, sur un seul modèle.

| Besoin | Choix | Pourquoi |
|---|---|---|
| Dossier et enchaînement | Écrits par nous | Aucune bibliothèque essayée ne périme seulement ce qui dépend d'une pièce remplacée. Un prototype de 313 lignes, 392 avec l'export, tient les huit conduites demandées |
| Boucle de chaque rôle | Appel direct d'Amazon Bedrock, comme dans le produit actuel ; la bibliothèque d'agents d'AWS en solution de repli | Ce choix n'est pas tiré d'un essai : l'essai concluait pour la bibliothèque. Mes deux raisons : la boucle existe déjà, et quarante paquets de plus la veille du dépôt sont un risque inutile. Un essai court peut les départager |
| Recherche | Recherche web d'AgentCore et reclassement par Bedrock | Essayés depuis des scripts d'essai, sans créer de ressource. La lecture d'un document entier reste à essayer |
| Preuve des inférences | Le journal du dossier, et l'historique que tient AWS | Les appels de modèle s'y retrouvent par leur identifiant ; le reclassement et la recherche web n'y figurent pas |

**Ce qu'AWS apporte réellement** : toutes les inférences des quatre agents et des deux spécialistes ; la recherche pendant la demande ; le classement des fiches ; une trace des appels de modèle tenue hors de notre code. Écartés : LangGraph comme dossier, qui ne fournit pas ce dont le dossier a besoin ; Step Functions et les services de persistance, qui demanderaient en plus des créations de ressources la veille de la fermeture du compte.

## 7. Contradictions et jonctions : où l'on en est

Les vingt contradictions, les seize passages de relais et les seize lacunes ont été repris un à un contre les documents (document 01). Aucun n'était entièrement corrigé dans les fiches : elles avaient été relues avant la critique d'ensemble. Chacun a maintenant une décision, un contrat modifié et une vérification prévue. Des quatorze résolutions proposées ce matin, onze sont reprises et précisées, trois sont amendées.

Une revue adverse de ces onze documents a ensuite rendu 125 constats. Ceux de fond sont corrigés ; une seconde passe a trouvé trente restes, corrigés à leur tour, sans troisième passe. Ce qui n'est pas corrigé est dit (document 01, section 10).

Douze questions restent ouvertes, avec leur effet (document 01, section 8). Les quatre qui pèsent le plus :

- **le catalogue n'est pas écrit.** Ces documents en fixent la structure et donnent de quoi le remplir pour une seule décision, « ajouter un titre ». Valider l'architecture, c'est valider un contenant ;
- **les tolérances chiffrées des verdicts n'ont aucune source** : tant qu'un essai de calibration n'est pas fait, seuls décident un signe conservé et un intervalle qui exclut zéro ;
- **aucune fiche de la bibliothèque n'a été relue par une personne** ;
- **ces résolutions retirent des décisions aux rôles**, pour les donner à des règles écrites d'avance. L'apport de chaque rôle ne se prouvera que par les mesures du document 09, dont la moitié demandent des personnes. Si elles échouent, la question d'une fusion vous reviendra.

## 8. Architecture cible et ordre de livraison

Les deux sont séparés exprès : aucune étape de l'ordre de livraison ne retire une fonction de la cible.

**L'architecture cible** est celle des documents 02 à 05 : quatre agents, deux spécialistes, le dossier, les quatre décisions de l'énoncé pour ses trois profils, la recherche pendant la demande, les trois gestes de révision.

**Échéances, relues à 15 h sur la page officielle.**

| Quand | Quoi |
|---|---|
| Dimanche 15 novembre, 23 h 59 | Dépôt GitHub et application |
| Lundi 16 novembre, 13 h 59 | Fermeture des comptes AWS et destruction des données |
| Lundi 16 novembre, 14 h | Vidéo, résumé d'une page, documentation technique |
| Vendredi 20 novembre, 14 h | Présentations des finalistes |

La page ne dit ni le fuseau horaire, ni ce que recouvre « application » : à confirmer auprès des organisateurs. **Accès, vérifiés à 14 h 55** : Bedrock et AgentCore répondent sur la route convenue. **Le dépôt n'a aucun dépôt distant configuré**, et un seul commit.

**Ordre proposé.** Chaque étape laisse un produit qui fonctionne et dit ce qu'il ne fait pas encore. Les durées sont mes estimations, pas des mesures.

| Étape | Contenu | Durée estimée | Ce qui reste restreint, et affiché comme tel |
|---|---|---|---|
| 0 | Filet de sécurité : dépôt distant, commit de l'existant et de ces documents | Un quart d'heure, dès votre accord | — |
| 1 | Le catalogue pour « ajouter un titre » ; le dossier et le greffier ; le moteur de calcul refait selon le document 05 | Trois à quatre heures | Une seule décision ouverte |
| 2 | Une tranche complète sur cette décision : les quatre agents et les deux spécialistes réellement exécutés, chacun avec ses portes | Quatre à six heures | Fiches non relues par une personne ; budget de recherche court ; interface existante adaptée |
| 3 | La révision : question après l'analyse, trois gestes, branche | — | — |
| 4 | « Vérifier une diversification », avec la préférence : le profil de Mateo | — | Abstention sur le contenu des fonds |
| 5 | Les critères de réception du document 09, automatisés | — | Les mesures qui demandent des personnes viennent après |
| 6 | « Comparer des actifs » et « jusqu'où accepter le risque » : le profil d'Amira ; les calibrations ; les jeux d'essai | — | — |

En dehors de la construction, trois choses ont une échéance : exporter avant lundi 13 h 59 les relevés qu'AWS tient de nos appels ; produire pour lundi 14 h la vidéo, le résumé d'une page et la documentation technique ; et, après la fermeture du compte, disposer d'un autre compte Bedrock, le modèle et le compte étant des paramètres.

**Ce que deviennent les trois profils en chemin.** Le produit actuel traite déjà Robert et Amira par un enchaînement fixe, et des demandes libres par un agent. Tant qu'une décision n'est pas ouverte dans le nouveau catalogue, ses dossiers actuels restent disponibles, étiquetés comme produits par le moteur précédent ; ils ne sont ni supprimés, ni présentés comme conformes à cette architecture.

**Ce soir.** À 17 h 45, il reste environ six heures, dont trois quarts d'heure à garder pour le dépôt lui-même. Les étapes 1 et 2 demandent sept à dix heures : d'après mes propres estimations, la tranche complète ne tient pas ce soir.

| Option | Ce qui est déposé ce soir | Durée estimée | Ce qu'on risque |
|---|---|---|---|
| A. La tranche étroite, de bout en bout | Les quatre agents et les deux spécialistes sur la demande de Robert, avec un catalogue minimal | Sept à dix heures | Elle ne tient pas avant 23 h 59 |
| B. Le socle, par incréments | Le catalogue pour une décision, le dossier, le nouveau moteur de calcul ; puis l'agent 0 et l'agent 2 s'il reste du temps. Les rôles non construits sont dits non exécutés | Trois à cinq heures pour le catalogue, le dossier et le moteur | Un dépôt où les quatre rôles ne s'exécutent pas tous dans la nouvelle architecture |
| C. Ne rien construire ce soir | Le produit actuel, cette proposition, les prototypes et les calculs | Un quart d'heure | Un dépôt qui montre une conception, pas son exécution |

Ma proposition : C tout de suite, pour que le dépôt existe ; puis B, par incréments, chacun déposé dès qu'il est « vert », avec un arrêt à 22 h 30. « Vert » veut dire : les tests du dépôt passent, le rejeu hors ligne retrouve les mêmes empreintes, et ce qui est construit s'exécute sur la demande de Robert. La tranche complète viendrait ensuite, hors de l'échéance de ce soir. Dans tous les cas, les quatre responsabilités restent dans le projet, et le dépôt dit ce qui s'exécute et ce qui ne s'exécute pas encore.

**Durée d'une étude.** Non mesurée. D'après les essais, une étude complète compterait quinze à trente-cinq appels de modèle et des calculs de quelques dizaines de secondes : plusieurs minutes. Devant un jury, elle se montrerait donc en rejeu, avec une révision faite en direct.

## 9. Ce qui vous revient

### A. Décisions de direction

1. **Le fonctionnement cible lui-même**, dont deux points à confirmer expressément : le contradicteur comme spécialiste de la responsabilité 2, donc une cinquième conversation de modèle ; les décisions de fond logées dans un catalogue écrit d'avance, ce qui rend les rôles plus étroits.
2. **Les ressources AWS.** Par défaut, rien n'est créé. Trois ajouts possibles : un compartiment S3 versionné comme copie du dossier ; un garde-fou Bedrock en second contrôle de la restitution ; le journal des invocations, qui toucherait tout le compte, partagé avec d'autres.
3. **Les personnes.** Quatre points. Le format de la démonstration : un membre de l'équipe répond en direct, ou un scénario écrit par l'équipe est rejoué ; je propose l'étude en rejeu et une réponse donnée en direct, chaque réponse portant le nom de celui qui l'a donnée. Les fiches : qui relit, avant le dépôt, la douzaine de fiches de l'étape 2 ? Sinon aucune réponse n'est « étayée » sans réserve. La supervision : deux membres nommés peuvent-ils relire, avant lundi 14 h, chaque dossier montré au jury, et toute modification du catalogue portera-t-elle deux noms ? Sinon chaque dossier affichera « aucune relecture humaine ». Enfin, un essai de lecture auprès de quelques personnes est-il autorisé ?
4. **Les données externes.** Par défaut, aucune n'est ajoutée. Deux ajouts changeraient ce que le produit peut dire. Des hypothèses de rendement publiées permettraient une projection centrale à dix ans et plus, pour les seules grandes classes d'actifs, soit huit actifs sur trente et un, et sans dispersion ; sans elles, deux profils sur trois ne reçoivent qu'une abstention sur leur horizon réel, et entre trois et dix ans il n'y aurait de toute façon rien. Les frais des fonds, pris aux pages des émetteurs, rempliraient le bloc des coûts ; sans eux, il dit ce qui manque. Toute donnée ajoutée se documente avant usage.
5. **Le modèle de chaque conversation.** Le produit emploie un modèle par défaut, les essais d'aujourd'hui en ont employé un autre, plus petit. Je propose de garder le modèle actuel du produit pour les quatre agents et le lecteur, et de n'en donner un autre au contradicteur que si l'essai d'erreurs semées le justifie.
6. **Le périmètre de ce soir** : C puis B, comme je le propose ; B seul ; C seul ; ou A malgré l'estimation. Et l'heure d'arrêt.

### B. Ce que j'ai tranché, et qui vous avait été soumis à 13 h 50

Ces points de méthode figuraient parmi les décisions de direction de l'étape précédente. Votre consigne m'a fait les trancher ; chacun peut être renversé.

| Point | Ce qui est retenu | Où |
|---|---|---|
| Plus de niveau en chiffre de tête | L'écart entre options d'abord ; un niveau seulement en illustration | 01, C13 |
| Le vocabulaire du constat | « Écart constaté par rapport au profil déclaré », jamais « ne convient pas » | 01, C04 |
| Avancer avec des inconnues nommées | L'étude se poursuit sans réponse, alors que les avis canadiens décrivent un questionnaire qui bloque : l'écart est dit dans le produit | 01, C01 et C03 |
| Le côté rendement | Le rendement d'équilibre : ce que l'option devrait rapporter pour se valoir | 01, L07 |
| Ce qui n'est pas simulé | Dit dans chaque restitution, par un texte que le code insère | 01, C14 et L13 |

### C. Pour information : la restriction de la recherche

À 13 h 50, je recommandais un agent 1 limité à la bibliothèque : aucune source ne valide une revue de littérature faite en quelques minutes par un agent seul. Vous avez demandé que la recherche puisse approfondir ; elle le peut. La restriction qui demeure dans la première version est celle-ci : une source trouvée pendant la demande peut rendre l'analyse plus prudente, jamais moins. Le chemin pour la lever passe par une relecture humaine, que personne n'assure aujourd'hui (document 03).

### D. Trois actions qui ne sont pas de mon ressort

Donner l'emplacement du dépôt GitHub et l'accord pour y pousser. Fermer ou relancer la session de bureau qui fonctionne hors de la route AWS. Faire vérifier `scripts/configurer-aws-workshop.sh`, modifié par une autre main à 12 h 12, avant tout commit : je ne l'ai pas ouvert.

## 10. Index des livrables

| Livrable demandé | Document |
|---|---|
| 1. Synthèse du fonctionnement proposé | `00-synthese.md` (ce document) |
| 2. Résolution des contradictions et des jonctions | `01-resolutions.md` |
| 3. Contrats des agents et du dossier | `02-dossier.md`, `03-contrats-des-agents.md` |
| 4. Graphes et règles de révision | `04-graphes-et-revision.md` ; types de résultats : `05-types-de-resultats.md` |
| 5. Comparatif technique et choix motivés | `06-comparatif-technique.md` |
| 6. Dossier illustratif et parcours contrasté | `07-dossier-illustratif.md` |
| 7. Schémas | `08-schemas.md` et `schemas/` |
| 8. Critères de réception | `09-reception.md` |
| 9. Décisions de direction | Section 9 ci-dessus |
| Ce que font réellement des organisations | `10-pratiques-observees.md` |

Pièces d'appui : relevés des relecteurs, essais et revue de cohérence dans `research/fiches/architecture/` ; essais techniques dans `research/experiences/technique/` ; calculs des deux parcours dans `research/experiences/` ; routes et ressources dans `research/R08-…`.

## 11. Ce qui est établi, et ce qui ne l'est pas

| | |
|---|---|
| **Mesuré** | Les nombres des deux parcours, calculés sur les données du projet par des scripts nommés. Les conduites du dossier, sur un prototype sans modèle. Le comportement de deux bibliothèques et, pour AWS, des seuls appels sans ressource (recherche web, reclassement, historique des appels) ; chaque conduite une fois, sur un seul modèle |
| **Lu ou simulé, non exécuté** | Step Functions (définition validée, états essayés un à un) ; S3 et DynamoDB (émulateur local) ; les droits de création de ressources (simulation) |
| **Vérifié contre des sources** | Les quarante-huit références de la recherche complémentaire : passages retrouvés mot pour mot ; huit sources corrigées, et plusieurs lectures ramenées à ce que les sources portent. Vérification faite par un sous-agent, pas par une personne |
| **Conçu, non exécuté** | Les contrats, les portes, les graphes, la révision, le catalogue, la boucle des cinq ou six conversations de modèle, les deux parcours de bout en bout. Le document 07 distingue ce qui est mesuré, illustratif et attendu ; le document 09 ne contient que de l'attendu |
| **Convention, sans source** | La borne de trois ans, la grille des longueurs de bloc, le niveau de 90 % des intervalles, la table de profondeur, la confrontation unique, le pourcentage plutôt que le compte « sur 100 » |
| **Non établi** | Que chaque rôle apporte quelque chose qu'un agent unique doté des mêmes outils n'apporterait pas. Que des lecteurs comprennent la restitution. Que le dossier tienne sur une autre machine. Combien de temps dure une étude |
