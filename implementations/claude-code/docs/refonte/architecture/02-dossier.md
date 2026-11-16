> **Conception, non construite** (15 novembre 2026). Rien de ce document n'est en service dans le produit. Les passages sur le calendrier, les décisions à prendre et l'organisation du travail sont historiques : ce ne sont pas des consignes. Certaines pièces de travail citées (`research/fiches/`, `research/R08-…`, `docs/etat.md`, `docs/coordination.md`) ne sont pas dans cette archive. Entrée de l'archive : `LIRE_EN_PREMIER.md`.

# 02 — Le dossier de décision : contrat

Le dossier est l'objet qui relie les quatre agents. Il doit permettre à quelqu'un qui n'a pas suivi l'étude de comprendre comment une demande est devenue une conclusion, puis pourquoi cette conclusion a changé. Ce document dit ce qu'il contient, qui fait autorité sur quoi, qui peut écrire quoi, et comment les versions se conservent. Le choix du support technique en découle (document 06).

Statut des éléments : ce contrat est une proposition de conception. Les repères dont il s'inspire sont nommés là où ils servent ; aucun n'est repris comme une conformité. Les numéros entre crochets (C05, R14, L11…) renvoient à la table de résolution (document 01).

## 1. Principes

1. **On ajoute, on ne modifie pas.** Chaque pièce est une version immuable. Corriger, c'est ajouter une version qui remplace la précédente ; l'ancienne reste lisible. Retirer une pièce fausse, c'est ajouter un événement de retrait : la pièce reste lisible, elle ne sert plus.
2. **Une pièce s'identifie par l'empreinte de son seul contenu.** Quatre mentions l'accompagnent, portées par l'événement qui la dépose et non par la pièce : son auteur (un rôle avec l'identifiant du modèle, un module de code avec sa version, ou la personne), l'activité qui l'a produite (avec, pour un appel de modèle, l'identifiant de requête AWS, les jetons et la raison d'arrêt), les empreintes de ses entrées, la date. Sans cette séparation, une tâche refaite ne retrouverait jamais la même pièce. En contrepartie, deux pièces de même contenu n'en font qu'une : toute pièce cite donc ce sur quoi elle porte.
3. **Un journal d'événements, en ajout seul**, dit ce qui s'est passé et dans quel ordre. Le greffier seul date et ordonne : aucun rôle, aucune personne ne fournit une date. Chaque événement porte l'empreinte du précédent, de sorte qu'une altération du journal se voit.
4. **L'état en vigueur se déduit.** On appelle *tête* d'une branche le dernier événement de son journal. Ce qui est « en vigueur » à cette tête se calcule à partir du journal et des dépendances ; personne ne l'écrit.
5. **Aucun nombre calculé, aucun seuil, aucun verdict n'est écrit par un modèle.** Un modèle écrit des textes, des citations et des choix dans des listes fermées (un statut, un type, une partie) ; le code vérifie, calcule et range. Une exception, contrôlée : l'agent 0 recopie les valeurs que la personne ou l'énoncé ont dites, nombres compris, et la porte vérifie que tout nombre d'un fait figure tel quel dans sa citation. Les valeurs d'un portefeuille proposé par le produit sont recopiées par le code, non par l'agent 0.
6. **Le catalogue est une entrée comme une autre.** Les règles que le code applique (seuils, grilles, tables) sont écrites d'avance par l'équipe dans un catalogue versionné. Chaque plan, chaque calcul, chaque verdict, chaque comparateur et chaque question désignée compte, parmi ses empreintes d'entrée, celles des lignes du catalogue qu'il emploie : un seuil modifié périme ce qui en dépendait, et cela seulement [C05]. La version d'ensemble du catalogue est une mention de l'événement, pour l'audit : elle n'entre dans aucune empreinte d'entrée.

Repères : la norme de provenance du W3C (entités, activités, agents, révision, invalidation) pour le vocabulaire des relations ; les principes d'intégrité des données « attribuable, lisible, contemporain, original, exact » ; la norme d'audit sur la documentation pour le « test du tiers » (document 10 pour ce qui en a été lu).

## 2. Objets

Chaque objet a un type, une empreinte, un auteur, des entrées. Les champs propres sont donnés ici ; le schéma exact se fixe à la construction.

| Famille | Objet | Champs propres | Créé par | Fait autorité |
|---|---|---|---|---|
| Demande | **Demande** | Texte tel que saisi ; langue ; **répondant**, écrit par l'interface et jamais par un modèle : personne en session, démonstrateur, scénario écrit par l'équipe, client simulé (réservé aux essais) [L12] | La personne (par l'interface) | La personne |
| | **Version de la demande** | Nature : initiale ; précision (une inconnue reçoit une valeur, en réponse à une question ou de l'initiative de la personne) ; correction (« je me suis trompé ») ; changement (« ma situation a changé ») ; variante (« et si… ») ; ce qui change ; version précédente ; branche | La personne ; l'agent 0 l'enregistre et la rattache | La personne |
| Profil | **Fait déclaré** | Un fait par champ (l'un des six éléments et leurs sous-champs) ; valeur ; citation mot pour mot ; origine : énoncé, demande, réponse, ou « proposé par le produit, retenu par le répondant » (le portefeuille fictif) ; répondant ; état : déclaré, confirmé (par une personne en session ou un démonstrateur seulement), contesté puis maintenu | Agent 0 ; porte de citation | La personne ou l'énoncé |
| | **Préférence** et **contrainte** | Formulation de la personne ; lectures opératoires tirées de la table « préférence vers contrainte » ; dure ou souple ; vérifiable ou non dans les données | Agent 0 ; le code pour les lectures | La personne |
| | **Inconnue** | Champ ; statut pris dans la table des variables de la décision : nécessaire, à balayer, ou non informable (aucune question fermée ni aucune donnée du produit ne peut la renseigner, comme la capacité à absorber une perte) ; pourquoi | Agent 0 ; le code pour le statut | Le catalogue |
| | **Contradiction** | Les deux déclarations en cause, leurs citations ; règle déclenchée ; état : à clarifier, portée en alternatives, levée par la personne. Elle est montrée à la personne dès qu'elle est constatée ; ce n'est pas une question : la personne la lève si elle le veut, par une précision ou une correction | Agent 0 ; règles du code | La personne pour la lever |
| | **Écart apparent** | La citation de la demande et la déclaration qu'elle semble contredire (profil de risque, objectif, préférence) ; nature de l'actif lue dans les données. Ce n'est ni un jugement de convenance, ni une affirmation chiffrée [C04] | Agent 0 | Les deux citations |
| Questions | **Question** | Type : décision, recherche, calcul, à la personne ; parent ; clé de dédoublonnage (type, objet, paramètres) ; critère de résolution ; responsable (un rôle, ou « l'équipe, hors exécution » pour une lacune) ; état : ouverte ; résolue (réponse « étayée ») ; résolue sous condition (réponse « étayée avec réserve ») ; sans preuve ; non résolue (réouvertures épuisées, ou tâche en échec) ; événements qui la rouvrent ; nombre de réouvertures | Le code, qui instancie les questions de la table du catalogue pour la décision et les signaux retenus par l'agent 0 ; l'agent 0 (questions ajoutées, typées) ; agents 1 et 2 (sous-questions de leur domaine) | Le rôle responsable |
| | **Question à la personne** | Champ visé (un seul) ; formulation ; forme de réponse ; enjeu ; état : préparée, posée, répondue, sans réponse. Un auteur par geste : désignation, rédaction, enregistrement de la réponse | Avant l'analyse : la porte désigne (variable nécessaire manquante), l'agent 0 rédige. Après l'analyse : le code désigne (inconnue qui change le cas), l'agent 3 rédige. La réponse entre toujours par l'agent 0 [C19] | La personne |
| | **Lacune** | Une question « sans preuve » dont le remède appartient à l'équipe : ce qui a été cherché, les affirmations touchées. Le greffier ne l'attend jamais [R15] | Le rôle qui la rencontre | L'équipe, hors exécution |
| Données et sources | **Jeu de données** | Quatre pièces [L11] : les fichiers et leurs empreintes ; la table des conventions (devise de référence, fréquence, jour d'observation, rendement total avant frais, report du change vers l'avant seulement) ; une fiche par actif, calculée par le code sous chaque convention déclarée ; les limites, chacune reliée aux formulations qu'elle interdit, dont l'univers fait de survivants | Qualification des données (code) | Les fichiers d'origine |
| | **Source** | Référence, version, date de consultation, nature (cadre, résultat empirique ou théorique, guide, cours, déclaration d'une organisation, document commercial) ; empreinte du fichier ; niveau de lecture réel | Agent 1 ; l'équipe pour la bibliothèque | Le fichier |
| | **Passage** | Extrait mot pour mot ; emplacement ; empreinte du fichier | Agent 1 ; porte de citation | Le fichier |
| | **Fiche de preuve** | Question traitée (même clé que les questions de recherche) ; résultat ; hypothèses ; réserves de la source ; domaine d'application ; condition d'application testable ; niveau de lecture ; statut de qualification : qualifiée (relue par un membre nommé de l'équipe, relecture inscrite au journal) ou candidate (non relue par une personne : fiche de la bibliothèque écrite par des sous-agents, ou preuve trouvée pendant la demande) ; date de vérification | L'équipe (fiches de la bibliothèque, qualifiées ou candidates) ; agent 1 (candidates, pendant la demande) | La bibliothèque versionnée |
| | **Fiche produit** | Par actif cité et par rubrique (nature, structure, devise, secteur, coûts, risques, liquidité) : une valeur ou « inconnu », et un état : déclaré par sa source, recoupé, contredit, invérifiable. Aucun nombre propre : les « risques observés » renvoient à des calculs du dossier. Un verdict « information suffisante pour tel type de conclusion », calculé par règle [R04] | Agent 1 ; le code pour les renvois et le verdict | Les données et les passages cités |
| | **Contradiction entre sources** | Deux liens de preuve opposés ; le test du catalogue qui les départagerait, ou la mention qu'aucun n'existe [R11] | Agent 1 | Le test, s'il existe |
| | **Lien de preuve** | Trois éléments distincts : le renvoi (passage, calcul, fait ou hypothèse, dont l'existence est contrôlée) ; ce que cet élément établit, dit en une phrase ; l'inférence vers ce qu'il appuie, qui peut être une réponse à une question de recherche, une ligne du plan des méthodes, une rubrique de la fiche produit ou une affirmation (soutient, contredit, conditionne) ; elle se juge : par qui, quand, avec quel résultat (soutient, en partie, non, non jugé, contesté) | Agents 1 et 2 ; porte pour l'existence | Le juge nommé |
| Hypothèses et méthodes | **Hypothèse** | Énoncé ; origine ; vérifiable ou non ; état : posée, éprouvée, réfutée ; pour une hypothèse de rendement, statut du catalogue : base ou borne d'affichage [C07] | Agents 0, 1, 2 ; le catalogue pour la grille | Le test qui l'éprouve |
| | **Formulation** | Entrée du catalogue : usage, usages exclus, calcul, tests de condition, horizons admissibles, variantes de la batterie, rendus obligatoires, version | L'équipe | Le catalogue versionné |
| | **Test de condition** | Formulation ; données ; résultat ; critère (identifiant dans la table des seuils). Exécuté une seule fois pour une formulation, un objet (un actif, ou le portefeuille d'une option), un jeu de données et des paramètres ; tous les rôles relisent le même résultat [C06]. Les tests sur les actifs précèdent le plan des méthodes ; ceux qui portent sur le portefeuille d'une option s'exécutent quand l'option existe | Le code | Le code |
| | **Plan des méthodes** | Une ligne par formulation utile à la question, chaque ligne étant une pièce : autorisée, autorisée avec variantes ajoutées, écartée ; réserves ; fiches qui la fondent. Le statut ne peut que restreindre ce que les tests admettent. Une version ouverte après des calculs cite sa cause et porte la marque « amendée après des résultats » [R07] | Agent 1 | Agent 1, dans les limites du catalogue |
| Analyse | **Option** | Portefeuille ; origine : « ne rien changer », demandée, comparateur désigné par règle, proposée par l'agent 2 (une autre part, ou une autre combinaison, des seuls actifs que la personne a nommés ou qu'une règle a désignés [L14]), demandée par la personne dans une nouvelle version de la demande | Le code pour les options de base et les comparateurs ; agent 2 pour ses ajouts | La règle du catalogue |
| | **Plan d'analyse** | Une ligne par option et par formulation, chaque ligne étant une pièce ; grandeur visée ; version de la batterie fixe ; variantes ajoutées ; domaines de balayage cités par leur empreinte ; scellé (empreinte et heure). Ajouter une option ajoute des lignes : les calculs des autres lignes restent en vigueur | Agent 2 | Agent 2 ; le scellé le fige |
| | **Calcul** | Formulation et version ; empreintes des lignes du catalogue employées ; entrées par empreinte ; paramètres ; graine ; demandeur ; ligne du plan dont il relève, ou « hors plan » ; résultat typé ; incertitude d'échantillon ; erreur de simulation ; marques : exploratoire, postérieur à un amendement, bord de domaine | Le code | Le code |
| | **Table des variantes** | Ce que la batterie fixe a donné pour chaque affirmation possible, à question fixée | Le code, au scellement du plan [C08] | Le code |
| | **Rendu** | Ce qu'il faut pour montrer une affirmation, selon son type : sens, taille, intervalle, mention « distinguable », pas d'arrondi, phrase type [R12] | Le code | Le code |
| Contrôle | **Contrôle de porte** | Pièce ; règle ; résultat ; motif de refus | Les portes (code) | Le code |
| | **Objection** | Type de la grille ; affirmation visée, ou formulation visée tant que la note n'existe pas ; test ; critère (identifiant de la table des seuils, scellé avant le calcul) ; résultat ; verdict : tient, amendée, change, non testable ; origine : batterie fixe, contradicteur, recherche, personne ; état : en attente, jugée, exécutée sans verdict (aucun critère au catalogue : le type compte alors comme non couvert) | Le contradicteur, la batterie, l'agent 1 ou la personne ; le code pour le résultat et le verdict | Le code pour le verdict |
| | **Effet requis** | Ce qu'un verdict impose à l'affirmation visée : réserve à porter, plage à afficher, ligne à réviser [C15] | Le code | Le code |
| | **Réserve** | Pièce structurée rattachée à une affirmation : objet, cause, éléments obligatoires. Trois origines : un verdict ; une réserve écrite par l'agent 1 sur la ligne du plan des méthodes qu'emploie l'affirmation ; une réserve de la source, portée par la fiche de preuve. Dans les trois cas le code la rattache ; l'agent 3 la formule, il ne la crée pas [R10] | Le code, qui la rattache | Le code |
| | **Bilan de confrontation** | Types d'objection couverts et non couverts, nombre de tests, réserves par affirmation, objections non testables, état : close, close avec réserves, close avec revue incomplète [R10] | Le code | Le code |
| Conclusions | **Affirmation** | Clé stable et versions ; texte ; partie de la conclusion ; type de résultat (document 05) ; calculs et options visés, ou, pour un type 7, la pièce qu'elle reprend (abstention, lacune, réponse « sans preuve », objection non testable, calcul dont l'intervalle contient zéro) ; portée ; conditions de validité et de réemploi ; sens pour la demande (favorable, défavorable, neutre), calculé par le code [R08] ; état : en vigueur, amendée, non résolue | Agent 2 ; le code pour le sens | Agent 2, sous contrôle des portes |
| | **Réponse à l'objection** | La version d'affirmation qui répond à un verdict, ou la contestation, unique, par un test du catalogue. Une contestation ne renverse pas un verdict : les deux résultats sont gardés, et l'affirmation devient « non résolue » | Agent 2 | La porte d'amendement |
| | **Conclusion** | Affirmations rangées en quatre parties | Agent 2 | Agent 2 |
| | **Abstention** | Ce qui n'est pas traité ; pourquoi ; ce qu'il faudrait pour le traiter. Toute abstention d'un rôle amont est reprise par l'agent 2 comme une affirmation de type 7, dans la quatrième partie de la conclusion : elle ne peut donc pas être omise à la restitution. Seule exception : l'abstention qui arrête l'étude à la qualification (demande hors catalogue, gabarit incomplet), que l'interface affiche avec la reformulation proposée (document 04, section 5) | Agents 0, 1, 2 | Le rôle auteur |
| Restitution | **Restitution préparée** | Les trois profondeurs ; blocs ; pour chaque phrase de fait, l'affirmation qu'elle rend | Agent 3 | Agent 3, sous contrôle des portes |
| | **Affichage** | Restitution et version montrées ; profondeur et son motif (valeur par défaut, fait déclaré, choix de la personne) ; heure | L'interface (code) | Le journal |
| | **Réaction** | Affichage auquel elle répond ; répondant ; nature : réponse, choix, correction, changement de situation, demande de variante, contestation (d'un chiffre, d'une donnée, d'une source, d'une méthode), hors périmètre ; objet visé ; texte ; état de compréhension : non mesurée (valeur par défaut), confirmée, non confirmée | La personne ; l'agent 3 propose le classement, la personne le confirme | La personne |
| Exécution | **Manifeste d'entrées** | Pour chaque tâche : empreintes des pièces remises, empreinte de la consigne, identifiant du modèle, empreintes des lignes du catalogue remises [R14] | Le greffier | Le journal |
| | **Décision d'un modèle** | Événement : les candidats que le code proposait, le choix fait dans cette liste, et le motif écrit au moment de décider [L14] | Le rôle | Le journal |
| | **Événement**, **invalidation**, **réouverture**, **retrait**, **relecture** | Type ; cause ; cible ; tête prolongée ; pour une relecture, le nom du relecteur et son constat | Le greffier ; la personne ; l'équipe | Le journal |

### Le catalogue : où vivent les décisions prises d'avance

Dire que « le code ne décide rien » serait inexact : le code calcule, rend des verdicts, désigne des comparateurs et des questions. Ces décisions de fond ne sont prises ni par un modèle pendant une demande, ni par le code de sa propre autorité : elles sont écrites d'avance par l'équipe, dans le catalogue, et le code les applique. Le catalogue est donc la pièce où il faut regarder pour savoir ce qui a été décidé avant toute demande.

Pour chaque type de décision, les tables des variables, des questions de recherche, des formulations, des options de base et des types de résultat permis forment un **gabarit de décision**. Une décision dont le gabarit est incomplet n'est pas ouverte : la porte de qualification répond « type de demande non ouvert » [L04].

| Table du catalogue | Ce qu'elle fixe | Lue par |
|---|---|---|
| Décisions et variables | Pour chaque type de décision, chaque variable et son statut : nécessaire, à balayer, non informable [C01] | Agent 0, porte de qualification |
| Questions de recherche | Par type de décision et par signal, les questions à ouvrir, leur type, leur critère, leurs paramètres [R01] | Le code, agent 0, agent 1 |
| Formulations | Usage, usages exclus, tests de condition, horizons admissibles, rendus ; un seul catalogue pour l'agent 1, l'agent 2 et le contradicteur [C06, C10, R03] | Agents 1 et 2, contradicteur, calculs |
| Hypothèses de rendement | La grille, et le statut de chacune : base, ou borne d'affichage [C07] | Calculs, agent 3 |
| Batterie fixe | Les dimensions d'analyse et leurs valeurs, croisées à question fixée, dont quatre longueurs de bloc : une semaine (borne), quatre, treize et vingt-six semaines ; la liste de ses clés [C08, C09] | Calculs, contradicteur |
| Domaines de balayage | Par inconnue de la personne : domaine, pas, règle de bord [R16] ; le domaine de la part contient les repères cités [L06] | Calculs, agent 2 |
| Options et comparateurs | Par type de décision, les options de base ; la règle des comparateurs : candidats (les actifs isolés non détenus, hors le titre demandé), échantillon, convention, départage [C20] ; le portefeuille fictif que le produit propose avec la question du portefeuille de départ | Calculs, agent 2 |
| Seuils, critères et repères | Identifiant, statistique, règle de chaque verdict, lieu d'emploi, origine, mention « arrêté après avoir vu les données » s'il y a lieu, sensibilité [C05, L16]. Les **repères cités** d'un texte (un plafond d'un règlement de fonds, une hypothèse publiée) y figurent avec leur passage et la mention « sans effet sur un verdict » [L06] | Calculs, portes ; les rôles n'en citent que les identifiants |
| Convention des mesures historiques | Par grandeur : définition, unité, règle d'annualisation, périodes, avant frais, devise, fréquence ; une seule fonction de calcul par grandeur [L10] | Calculs |
| Grille des objections | Les types d'objection, les tests qui les tranchent, leurs domaines de paramètres | Contradicteur, calculs |
| Préférence vers contrainte | Les lectures opératoires d'une préférence non financière [C17] | Agent 0, calculs |
| Couverture des horizons | Ce que chaque tranche d'horizon peut recevoir : trajectoires, mesures, abstention [C12] | Les quatre agents |
| Affichage des statuts | Pour chaque statut d'un rôle amont, un traitement parmi six : affirmer, affirmer avec la réserve, illustrer seulement, dire que ce n'est pas établi, poser la question, bloquer [L16] ; tournures par type ; phrases types | Agent 3, porte de restitution |
| Profondeur proposée | La première profondeur affichée, selon ce que la personne a déclaré [C18] | Interface |
| Correspondance professionnelle | Ce que chaque rôle transpose, ce qui n'est pas simulé [C14] | Le code, pour la déclaration de portée |
| Bornes et durées | Réouvertures, tentatives d'amendement, nombre de questions, délai de réponse à une question, budgets, durées de validité des sources et des faits déclarés | Greffier |
| Plan de supervision | Qui relit quoi, quand, sur quelle liste de contrôle ; toute modification du catalogue porte deux noms [L13] | L'équipe ; l'agent 3 pour l'état affiché |
| Jeux d'essai | Cas, base saine, transformation, réponse attendue ; taux d'atteinte par hasard de chaque critère [L15] | Les essais de réception |
| Bibliothèque | Les fiches de preuve tenues par l'équipe, chacune avec son statut de qualification ; aujourd'hui toutes candidates | Agent 1 |

**Aucune de ces tables n'est encore écrite.** Ce document en fixe la structure. Leur contenu, pour la seule décision « ajouter un titre », est le premier travail de la construction (document 00, section 8) ; les valeurs éparses que citent ces documents (trois ans, quatre longueurs de bloc, deux hypothèses de base) en sont les premières lignes, pas le catalogue.

### Ensembles nommés

Plusieurs noms des contrats désignent un ensemble de pièces, et non une pièce.

| Ensemble | Ce qu'il réunit | Sa version |
|---|---|---|
| Fiche de qualification | Faits déclarés, préférences, contraintes, inconnues, contradictions, écart apparent, signaux retenus, abstentions de l'agent 0 | Change champ par champ : chaque pièce a la sienne |
| Fiche des données | Les quatre pièces du jeu de données | Celle de l'instantané |
| Dossier de preuves | Sources, passages, fiches de preuve, liens, contradictions entre sources, fiche produit, plan des méthodes, journal de recherche (requêtes, documents écartés et motif) | Celle du plan des méthodes |
| Note d'analyse | Options, plan d'analyse, affirmations, table de couverture, bloc de coûts | L'empreinte de la liste de ses affirmations et de son plan ; un amendement donne une version suivante |
| Journal de révision | Vue calculée : ce qui a été périmé, par quel événement | — |

### Vues calculées

Plusieurs « documents » que les fiches de la recherche confiaient à un rôle ne sont pas des pièces : ce sont des vues que le code tire du journal, toujours à jour et jamais écrites à la main [R06, R14].

| Vue | Ce qu'elle montre |
|---|---|
| Registre des essais | Tout calcul lancé, par demandeur, avec la ligne du plan dont il relève ou la mention « hors plan » |
| Écarts au plan | Les calculs lancés hors du plan scellé ; l'agent 2 n'en écrit que le motif |
| Registre des objections | Toutes les objections, quelle que soit leur origine, avec leurs versions |
| Relevé d'antériorité | Les calculs faits sous un plan qui les précède ; ceux faits sous une ligne amendée |
| Mémoire de synthèse | Les décisions des modèles et leur motif, les informations contraires et leur traitement, les refus des portes, ce qui n'a pas été vérifié |
| Parcours utilisateur | Les sept étapes lisibles du document 04 |
| État de l'étude | Calculé sur les questions, les affirmations et les tâches (document 04, section 5) ; il existe même quand aucune conclusion n'a été écrite |

## 3. Relations

| Relation | De | Vers | Qui la pose | Contrôle |
|---|---|---|---|---|
| dérive de | Toute pièce | Ses entrées | L'activité qui produit la pièce | Le greffier refuse une pièce qui cite une pièce qu'on ne lui a pas remise. Une pièce rendue après le remplacement d'une de ses entrées est admise à l'état « périmée » |
| produit par | Pièce | Activité (rôle ou outil, requête AWS, version) | Le greffier | Automatique |
| attribué à | Pièce | Auteur | Le greffier | Droits de la section 5 |
| remplace | Version | Version précédente | L'auteur de la nouvelle version | Même auteur ou même rôle |
| appartient à | Pièce | Tête d'une branche | Le greffier | Calculé : la pièce est admise et ses dépendances directes y appartiennent |
| retiré par | Pièce erronée | Événement de retrait, avec sa cause | L'agent 1 pour ses sources, passages et fiches candidates ; le code pour un calcul ; l'équipe | Irréversible ; ce qui en dérive est signalé |
| répond à | Pièce | Question, ou objection | Le rôle responsable | Critère de résolution de la question ; porte d'amendement pour une objection |
| soutient, contredit, conditionne | Passage, calcul, fait, hypothèse | Affirmation, réponse à une question de recherche, ligne du plan des méthodes, rubrique de la fiche produit | Agents 1 et 2 | Existence par le code ; soutien par un juge nommé |
| éprouve | Objection | Version d'une affirmation | Contradicteur, batterie, agent 1, personne | Verdict par le code |
| rend | Phrase de restitution | Affirmation, ou élément affichable sans type (document 05) | Agent 3 | Porte : toute phrase de fait désigne l'affirmation ou l'élément qu'elle rend ; aucune affirmation de la conclusion omise |
| réagit à | Réaction | Affichage | L'interface | Automatique |

**Maille des dépendances.** La révision ciblée ne vaut que ce que vaut la finesse des liens « dérive de » [R07, R14]. Trois règles. Les pièces sont petites : un fait par champ du profil, une ligne par formulation dans le plan des méthodes, une affirmation par ligne de conclusion. Chaque tâche a un manifeste d'entrées, écrit par le greffier. Chaque pièce produite cite, parmi ces entrées, celles dont elle dérive ; une porte refuse un lien vers une pièce qui n'a pas été remise. Pour une pièce écrite par un modèle, un lien peut manquer sans qu'un rejeu le montre : c'est une limite, que l'essai de révision ciblée (document 09, B1) mesure contre une table de dépendances attendues, écrite d'avance.

## 4. États d'une pièce

| État | Sens | Comment on y entre | Comment on en sort |
|---|---|---|---|
| Refusée | La porte ne l'a pas admise ; elle est gardée avec le motif | Contrôle de porte négatif | Jamais : une nouvelle version est proposée |
| En vigueur | Admise, et toutes ses entrées sont en vigueur | Contrôle de porte positif | Une entrée est remplacée ou retirée |
| Périmée | Juste pour ses entrées, mais l'une de ses dépendances directes n'est plus en vigueur à la tête. C'est un statut calculé par rapport à une tête, pas un retrait | Calcul du greffier à chaque changement de tête | Redevient en vigueur si les mêmes dépendances reviennent |
| Remplacée | Une version plus récente de la même pièce a été admise ; elle reste lisible et n'est plus remise comme entrée. C'est, comme « périmée », un état calculé | Dépôt d'une nouvelle version par son auteur | Redevient en vigueur si le même contenu est déposé de nouveau : un retour à une valeur antérieure |
| Erronée | Retirée parce que fausse (erreur de calcul, citation qui ne soutient pas, source retirée). Elle ne sert plus jamais, à aucune tête | Événement de retrait, avec sa cause | Jamais |

Une fiche de preuve porte en plus un **statut de qualification** : *qualifiée* (relue par un membre nommé de l'équipe) ou *candidate* (non relue par une personne, qu'elle vienne de la bibliothèque ou qu'elle ait été trouvée pendant la demande ; citation contrôlée, soutien non relu). Aujourd'hui, toutes les fiches sont candidates. Une pièce candidate est en vigueur ; elle ne peut servir qu'à rendre l'analyse plus prudente (document 03, agent 1).

« Périmée » et « erronée » ne se confondent pas : la première dit que la question a changé, la seconde que la réponse était fausse. Une restitution qui s'appuyait sur une pièce devenue erronée est signalée à la personne ; une restitution qui s'appuyait sur une pièce devenue périmée est simplement remplacée.

## 5. Qui peut quoi

C : créer. V : ajouter une nouvelle version de sa propre pièce. R : retirer comme erronée. Une case vide interdit.

| Famille | Personne | Agent 0 | Agent 1 | Agent 2 | Contradicteur | Agent 3 | Code (portes, calculs, greffier) | Équipe, hors exécution |
|---|---|---|---|---|---|---|---|---|
| Demande et versions | C | Enregistre | | | | | | |
| Profil, inconnues, contradictions, écart apparent | Confirme, corrige | C, V | | | | | Statut des variables ; règles de cohérence | |
| Questions | | C, V (ajouts typés) | C, V (recherche) | C, V (calcul) | | | C (questions de la table ; question décisive) ; états | Répond aux lacunes |
| Questions à la personne | Répond | Rédige (avant l'analyse) ; enregistre toute réponse | | | | Rédige (après l'analyse) | Désigne ; contrôle la rédaction | |
| Jeu de données | | | | | | | C | Remplace l'instantané |
| Sources, passages, fiches candidates, fiche produit, liens de preuve | Conteste | | C, V, R | C (liens vers des calculs) | | | Contrôle d'existence ; renvois chiffrés | Qualifie, R |
| Catalogue (toutes ses tables) | | | Propose une formulation | | | | | C, V |
| Plan des méthodes | | | C, V | | | | Tests de condition ; statut plancher | |
| Options, plan d'analyse | Demande une option, par une nouvelle version de la demande | | | C, V (ses ajouts ; le plan) | | | Options de base, comparateurs, scellé | |
| Calculs, table des variantes, rendus | | | Demande (tests de condition) | Demande | Demande (tests des objections) | Demande (rendus existants) | C, R | |
| Objections | Peut en soulever | | Peut en soulever (origine « recherche ») | Répond | C | | C (batterie fixe ; inscription des objections d'origine « recherche » et « personne ») ; résultat, verdict, effet requis, réserves, bilan | |
| Affirmations, conclusion, abstentions | | C (abstentions) | C (abstentions) | C, V | | | Sens ; état de l'étude | |
| Lacunes ; contradictions entre sources | | C (lacunes) | C | C (lacunes) | | | C (lacune d'un test d'objection refusé) | Répond aux lacunes |
| Restitution préparée | | | | | | C, V | | |
| Affichage, réaction | Réagit | | | | | Propose le classement d'une réaction | C (affichage) | |
| Événements | Réactions | Décisions | Décisions ; retours de sa liste ; retrait de ses sources | Décisions ; retours de sa liste | Décisions ; déclarations de non-couverture | Décisions | Tous les autres ; invalidations | Décisions de catalogue ; relectures |

Trois conséquences. Le contradicteur n'écrit ni la conclusion ni les seuils ; il ne peut qu'inscrire des objections. L'agent 3 n'a aucun droit sur les faits : il crée des restitutions et rédige des questions. Aucun rôle n'écrit à un autre : chacun dépose des pièces et des événements, que le greffier achemine d'après une table de code.

## 6. Cinq distinctions

**Précision, correction, changement ou variante.** Une **précision** donne une valeur à une inconnue, en réponse à une question ou de l'initiative de la personne. Si cette valeur est dans le domaine déjà balayé, le code sélectionne le cas de la conclusion, sans rappeler l'agent 2 et sans périmer aucun calcul ; sinon, le calcul qui manque est demandé. Pour le reste, la personne dit ce qu'elle fait, et l'interface propose trois gestes. « Je me suis trompé » est une **correction** : l'ancienne valeur n'a jamais valu, et la conclusion qui en dépendait est montrée dans l'historique comme n'ayant jamais été applicable à la personne. « Ma situation a changé » est un **changement** : l'ancienne conclusion a valu jusqu'à cette date. Dans les deux cas la branche principale avance : les pièces qui dépendaient de l'ancienne valeur deviennent périmées, les autres restent en vigueur. « Et si… » est une **variante** : elle ouvre une branche, qui partage toutes les pièces dont les dépendances n'ont pas changé, a sa propre tête, et ne périme rien sur la branche principale. Deux branches se comparent ; elles ne se fusionnent pas d'office.

**Historiquement correct ou encore applicable.** Un calcul est une fonction de ses entrées. Il n'est jamais « faux » parce que la demande a changé ; il est périmé. S'il redevient utile (mêmes empreintes d'entrées), il est réemployé sans recalcul. La restitution n'emploie que des pièces en vigueur ; le journal montre les périmées, avec l'événement qui les a périmées.

**Source retrouvée ou preuve qui soutient.** Le code établit qu'un passage figure dans un fichier. Il n'établit pas que ce passage soutient l'affirmation. Le lien de preuve garde les deux : « existence contrôlée » et « soutien jugé par… ». Une affirmation dont les liens n'ont que l'existence est restituée avec la mention « passage cité, soutien non relu ».

**Préparé, affiché, choisi.** Ce que l'agent 3 a préparé n'a pas forcément été vu ; ce qui a été vu n'a pas forcément été compris ni choisi. L'affichage est un événement de l'interface ; un choix est une réaction explicite de la personne, rattachée à l'affichage qu'elle avait sous les yeux. Aucun choix ne se déduit d'un affichage ni d'un silence. La compréhension n'est pas mesurée dans la première version, et le produit le dit.

**Décidé d'avance ou décidé pendant la demande.** Toute règle appliquée par le code vient du catalogue, écrit par l'équipe avant la demande. Tout choix fait pendant la demande vient d'un modèle, dans une liste fermée, avec son motif, ou de la personne. Le dossier permet de dire, pour chaque élément d'une conclusion, de laquelle de ces trois mains il vient.

## 7. Versions, branches, clôture

- Rien n'est supprimé pendant la vie du dossier. Une version remplacée garde son empreinte et reste ouvrable.
- Une seule écriture à la fois par branche : tout événement nomme la tête qu'il prolonge ; si la tête a bougé, il est refusé. Les faits d'exécution sont alors rejoués d'office sur la nouvelle tête. Une réaction de la personne n'est jamais perdue : elle nomme l'affichage auquel elle répond, elle est toujours enregistrée, et si cet affichage n'est plus le dernier, l'interface le lui dit et lui demande de confirmer.
- La clôture fige le dossier : après elle, on n'ajoute que des pièces datées et motivées, on ne retire rien. L'export (pièces, journal, version du code et du catalogue, empreintes des données) permet de rejouer l'étude sans AWS.
- Un document trouvé sur le web pendant la demande est conservé avec le dossier, sous son empreinte : sans lui, la porte de citation ne se rejoue pas. Ces fichiers restent dans le dossier privé ; ils ne sont pas versés au dépôt public, faute de droit de les redistribuer. Un export destiné à un tiers porte la citation, l'empreinte, l'adresse et la date.
- Refaire une étude pour la montrer crée une version ou un dossier distinct, jamais un remplacement silencieux ; l'interface dit si l'on regarde l'état scellé ou une reprise.

### Trois sortes de tâches

La règle « une tâche déjà faite pour les mêmes entrées n'est pas refaite » ne vaut pas de la même façon pour tout.

| Sorte | Exemples | Réemploi |
|---|---|---|
| Déterministe | Calculs, tests de condition, portes, verdicts (la graine, la version du code et les empreintes des lignes du catalogue employées font partie des entrées) | Sûr : même résultat pour les mêmes entrées ; se rejoue |
| Non déterministe | Toute pièce écrite par un modèle | Admis comme une économie : la pièce déjà admise est gardée tant que ses dépendances directes sont en vigueur ; la refaire donne une nouvelle version, jamais un écrasement |
| Volatile | Recherche web, vérification de la version d'une source | Valable pour une durée fixée au catalogue ; au-delà, la tâche est à refaire et la date de consultation fait partie de la pièce |

Coupure anticipée : si une tâche refaite rend une pièce de même empreinte que la précédente, rien n'est rouvert en aval.

## 8. Ce que le support doit garantir

Ajout seul et ordre total des événements par branche ; adressage par contenu ; lecture de n'importe quelle version passée ; calcul de l'état en vigueur ; refus d'une écriture sur une tête dépassée ; branches nommées, chacune avec sa tête ; export complet ; lisibilité par un tiers sans outil particulier. Le document 06 compare les supports sur ces exigences.

Une exigence vient du prototype : une **forme canonique** avant toute empreinte. Sans elle, 1 et 1.0, ou deux codages du même mot accentué, donnent deux empreintes, et un calcul peut dédoubler ou périmer des pièces sans raison de fond. Les nombres sont donc codés à une précision fixée, les textes normalisés, les valeurs non numériques refusées.
