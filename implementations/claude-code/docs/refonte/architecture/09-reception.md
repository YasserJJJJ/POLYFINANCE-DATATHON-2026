> **Conception, non construite** (15 novembre 2026). Rien de ce document n'est en service dans le produit. Les passages sur le calendrier, les décisions à prendre et l'organisation du travail sont historiques : ce ne sont pas des consignes. Certaines pièces de travail citées (`research/fiches/`, `research/R08-…`, `docs/etat.md`, `docs/coordination.md`) ne sont pas dans cette archive. Entrée de l'archive : `LIRE_EN_PREMIER.md`.

# 09 — Critères de réception de la future implémentation

Ces critères disent à quoi on reconnaîtra que l'implémentation réalise l'architecture. Chacun peut échouer. Ils se vérifient par des essais automatiques, sauf mention contraire ; les attendus s'écrivent avant l'essai. Aucun ne mesure la qualité financière d'une conclusion : ils mesurent que le système fait ce que ses contrats disent. Les numéros entre crochets renvoient à la table de résolution (document 01).

## A. Le dossier

| N° | Critère | Vérification |
|---|---|---|
| A1 | Ajout seul : aucune pièce admise n'est jamais modifiée ni supprimée | Empreintes de toutes les pièces avant et après une étude complète avec révision : identiques pour les pièces préexistantes |
| A2 | L'événement qui dépose une pièce porte auteur, activité, empreintes d'entrées, date ; pour un appel de modèle, l'identifiant de requête AWS, les jetons et la raison d'arrêt. L'empreinte de la pièce ne couvre que son contenu | Parcours du journal : aucun dépôt sans ces mentions ; une tâche déterministe refaite à l'identique rend la même empreinte |
| A3 | La tête se déduit du journal seul | Suppression de tout index dérivé, recalcul : mêmes pièces en vigueur |
| A4 | Rejeu hors ligne : chaque nombre est recalculé et chaque porte repassée, sans AWS ; une citation tirée du web se rejoue sur le fichier gardé au dossier | Commande de rejeu sur un dossier exporté : empreintes identiques pour toutes les pièces produites par le code |
| A5 | « Périmée » et « erronée » sont deux états ; une pièce périmée redevient en vigueur si ses entrées reviennent, sans recalcul | Corriger une valeur puis la rétablir : aucun calcul relancé la seconde fois |
| A6 | Une écriture sur une tête dépassée est refusée | Deux corrections simultanées : la seconde est rejouée sur la nouvelle tête |
| A7 | Une variante ne périme rien sur la branche principale et partage les pièces non touchées | Ouverture d'une branche : tête principale inchangée ; pièces communes de même empreinte |
| A8 | Un affichage, une réaction et une restitution préparée sont trois pièces distinctes ; aucun choix sans réaction explicite | Restitution préparée non affichée : aucune réaction ne peut s'y rattacher |
| A9 | L'export complet se recharge sur une machine sans accès AWS, et les mêmes calculs y rendent les mêmes empreintes (forme canonique des nombres et des textes) | Essai sur un second poste, d'un autre système |
| A10 | Les empreintes des lignes du catalogue qu'une pièce emploie figurent parmi ses entrées : un seuil modifié périme les verdicts qui en dépendent, et eux seuls [C05] | Rejeu des dossiers de référence sous un seuil voisin ; témoin : une phrase type modifiée ne périme aucun calcul |
| A11 | Tout calcul passe par le greffier ; le registre des essais est une vue du journal [R06] | Un appel direct à une fonction de calcul est refusé ; le compte de la vue égale le nombre de calculs lancés, échecs compris |
| A13 | La qualification des données contrôle les empreintes des fichiers, l'égalité des sommes de rendements quotidiens et hebdomadaires, l'identité du change et la date de publication des séries mensuelles [L11] | Un octet modifié dans un fichier de prix fait échouer la porte ; le défaut des jours fériés trouvé le 15 novembre, réintroduit exprès, fait échouer le contrôle des sommes |
| A12 | Un fait n'est « confirmé » que si le répondant est une personne en session ou un démonstrateur [L12] | Cas semé : confirmation par un scénario ou par un modèle, refusée |

## B. La révision ciblée

| N° | Critère | Vérification |
|---|---|---|
| B1 | Pour chaque correction d'une table de dépendances écrite d'avance (part, perte acceptable, horizon, titre, préférence, portefeuille), l'ensemble des pièces périmées est exactement l'ensemble attendu [R14] | Six corrections au moins ; comparaison d'ensembles ; contre-épreuve : un recalcul complet à froid ne change aucune pièce produite par le code |
| B2 | Un rôle dont aucune entrée n'a changé n'est pas rappelé | Compte des appels de modèle par rôle pendant la révision |
| B3 | La restitution révisée s'ouvre sur ce qui a changé et laisse lisibles les versions précédentes | Contrôle de structure |
| B4 | Le même événement ne rouvre pas deux fois la même question ; le nombre de réouvertures est borné ; au-delà, la question est « non résolue » | Boucle provoquée par deux retours opposés : arrêt au seuil, état affiché |
| B5 | Une précision dans le domaine déjà balayé ne relance aucun calcul | Réponse à la question posée après l'analyse : compte des calculs lancés égal à zéro |
| B6 | Un retour vers l'agent 1 après des calculs ne périme que les calculs de la ligne du plan amendée ; un calcul lancé sous cette ligne porte la marque « postérieur », jusque dans la restitution [R07] | Plan scellé, trois calculs, une condition qui échoue |

## C. Les contrats des agents

| N° | Critère | Vérification |
|---|---|---|
| C1 | Outils disjoints : un appel hors liste est refusé et journalisé | Consigne piégée demandant un outil d'un autre rôle |
| C2 | Contextes séparés : l'entrée d'un rôle ne contient que des pièces en vigueur, listées par empreinte | Journal des entrées de chaque appel |
| C3 | Chaque porte refuse le défaut qu'elle doit refuser | Défauts semés, un par porte : citation absente, valeur non dite, question double, formulation hors plan, plan scellé après un calcul, affirmation non reliée, sens affirmé sans intervalle, affirmation omise, tournure interdite ; et aussi : critère chiffré écrit par un modèle, statut porté sur une famille de méthodes, plage de balayage hors catalogue, option de base retirée, affirmation fondée sur la seule hypothèse « borne », rendu obligatoire manquant, actif rattaché à un groupe sans champ ni citation, raison d'arrêt inattendue |
| C4 | Les portes ne refusent pas des pièces saines | Témoin : les mêmes pièces sans défaut passent |
| C5 | Une sortie tronquée ou invalide, ou dont la raison d'arrêt n'est pas celle attendue, n'est jamais admise : elle est gardée à l'état « refusée », avec son motif | Limite de jetons abaissée : une tentative, deux reprises, puis échec déclaré |
| C6 | Le contradicteur ne peut ni réécrire la note ni fixer un seuil ; un verdict « change » bloque la restitution jusqu'à l'amendement, la contestation ou l'épuisement des tentatives, et la porte d'amendement ne laisse passer qu'une réécriture conforme [C15] | Six réécritures préparées après un « change » : une conforme ; sans la réserve ; qui garde le sens contredit ; qui change une autre affirmation ; qui en ajoute une ; aucune réécriture. Seule la première passe. Deux cas de plus : une contestation par un test du catalogue (l'affirmation sort « non résolue », le verdict n'est pas renversé) ; des tentatives épuisées (même sortie, étude de couverture partielle) |
| C7 | Seule une variable nécessaire manquante suspend l'étude ; un dossier complet ne déclenche aucune question. Une contradiction est montrée ; elle ne suspend l'étude que si elle rend indéterminée une variable nécessaire ; sinon ses deux lectures sont calculées, et la plus contraignante vient d'abord dans la restitution [C01, C03] | Jeu de demandes, dix répétitions : complète, sans portefeuille, sans titre, avec une contradiction qui ne touche pas une variable nécessaire, avec une contradiction qui en touche une |
| C8 | La confrontation complète a lieu pour toute version de la note admise par la porte d'analyse. Aucune restitution n'existe sans registre daté pour la version de note dont elle descend, ni, après un amendement, sans réévaluation datée des affirmations amendées [C16, C15] | Contrôle sur chaque dossier, notes descriptives comprises |
| C9 | Une décision dont le gabarit est incomplet n'est pas ouverte [L04] | Demande d'un type sans gabarit : « type de demande non ouvert », avec une reformulation proposée |
| C10 | Chaque choix d'un modèle laisse un événement, avec les candidats que le code proposait [L14] | Parcours du journal : aucun champ rempli par un modèle sans événement de décision |
| C11 | La question posée après l'analyse est désignée par le code : toute inconnue désignée a deux valeurs du domaine qui changent le cas ; sans inconnue décisive, aucune question, et la restitution le dit ; l'enjeu n'est jamais dit comme un niveau ; la même inconnue est désignée d'une exécution à l'autre [C19, C02] | Dossier de Robert, trois exécutions ; dossier construit sans bascule ; question piégée |
| C12 | Quand la note en contient, les objections du contradicteur visent au moins une affirmation favorable et « ne rien changer » ; un seul lot ; critère scellé avant le calcul, jamais modifié ni relancé ; un test hors plan est refusé et le type déclaré non couvert [C05, L07] | Lots piégés : test sans critère, critère modifié après coup, relances, tolérance écrite par le modèle |
| C13 | La citation du profil ne remplit ni la tolérance ni la capacité ; tout nombre d'un fait figure dans sa citation ; aucun champ ne reçoit de valeur par défaut ; l'écart apparent porte ses deux citations [C04] | Fiches piégées ; demande de Robert, dix répétitions ; portefeuille fictif retenu : admis, valeurs identiques à la ligne du catalogue |
| C14 | La fiche produit ne contient aucun nombre écrit par un modèle ; la note a une ligne ou une abstention pour chacun des cinq facteurs ; quand toutes les options font pire sur le risque, elle porte le rendement d'équilibre et la mention « sur le seul risque » [R04, L06, L07] | Volatilité tapée dans la fiche : refusée ; note sans ligne « concentration » : refusée |
| C15 | Une source contestée ouvre un seul réexamen, qui n'assouplit aucun statut ; une option demandée après un affichage porte la mention « ajoutée après le premier affichage » ; une réponse porte l'état « compréhension non mesurée » [R13] | Trois réactions jouées sur le dossier de Robert |
| C16 | Toute modification du catalogue porte deux noms et le rapport de rejeu des dossiers de référence [L13] | Modification à un seul nom : refusée |

## D. Les types de résultats

| N° | Critère | Vérification |
|---|---|---|
| D1 | Toute affirmation porte un type, une portée et des conditions de réemploi | Parcours des conclusions |
| D2 | Une proportion de trajectoires n'apparaît ni dans un titre, ni comme chiffre de tête, ni avant la comparaison qu'elle illustre, ni en compte « sur 100 », ni avec les mots « probabilité », « risque de », « chances » | Restitutions piégées : refus par la porte |
| D3 | Un sens n'est affirmé que si l'intervalle à 90 % de l'écart exclut zéro sous chaque valeur de base, et si le signe est le même dans toute la batterie ; renversé sous une borne seule, il est « établi avec réserve » [C07] | Trois cas construits, refusés par la porte d'analyse : un sens affirmé alors que l'intervalle contient zéro (attendu : type 7) ; une affirmation vraie sous la borne seule ; un sens que la borne renverse, écrit sans réserve (attendu : « établi avec réserve », avec le rendement d'équilibre). Les verdicts « change » et « amendée » se vérifient par C6 et C12, sur des affirmations que la porte admet |
| D4 | Un titre n'est nommé que si son écart se distingue de celui du comparateur de volatilité voisine | Dossier de Robert : la conclusion parle d'« un titre isolé aussi volatil » |
| D5 | Un résultat sensible aux conventions est donné sous chaque convention déclarée | Dossier de Mateo : deux valeurs de concentration |
| D6 | Les trois profondeurs rendent les mêmes affirmations | Comparaison des identifiants rendus |
| D7 | Les constats ne sont pas des règles : aucun résultat d'un dossier n'est lu par un autre dossier | Revue du code : aucune constante hors du catalogue ; au catalogue, toute valeur tirée de nos données porte la mention « arrêté après avoir vu les données » ; essai sur un portefeuille où l'ordre d'influence des choix diffère |
| D8 | Un résultat lu au bord d'un domaine de balayage est marqué, et n'est jamais présenté comme un maximum [R16] | Domaine restreint exprès : marque présente, aucune affirmation de maximum |
| D9 | Aucune option n'est dite « ESG », « durable » ou « conforme à la préférence » ; un repère cité n'est jamais une limite ; toute phrase sur un rendement dit « avant frais » [C17, L06, L09] | Restitutions piégées |
| D10 | Aucune ligne n'est montrée plus favorablement que la table d'affichage des statuts ne le permet ; chaque réserve figure aux trois profondeurs, près de son affirmation [L16, R10] | Réserve retirée d'une profondeur, déplacée, privée d'un élément : refusées |
| D11 | Aucun calcul sur trajectoires rééchantillonnées, quel que soit le type de l'affirmation, ne dépasse trois ans ; aucune fenêtre glissante ne dépasse la moitié de l'échantillon ; aucune probabilité d'atteindre un objectif [C10, C12] | Demandes à 208 semaines, à dix ans, fenêtres glissantes à 156 semaines : refusées ; à 104 et 156 semaines : admises ; demandes d'Amira et de Mateo |
| D12 | Une mesure historique suit la convention du catalogue : rendement total composé, avant frais, jamais annualisé sur moins d'un an [L10] | Rendement annualisé sur vingt-six semaines : refusé ; même valeur dans la fiche produit et dans la note |
| D13 | La profondeur affichée d'abord vient d'une table ; la changer ne change aucune pièce [C18] | Connaissances déclarées modifiées : seul l'événement d'affichage change |

## E. La recherche de l'agent 1

| N° | Critère | Vérification |
|---|---|---|
| E1 | Chaque déclencheur produit le comportement prévu : réemploi, vérification, nouvelle recherche, lecture approfondie, examen d'une méthode, question ouverte | Six questions construites, une par déclencheur |
| E2 | Toute citation existe mot pour mot dans le fichier dont l'empreinte est au dossier | Contrôle par le code, sur toutes les citations |
| E3 | Une preuve candidate ne peut ni autoriser une formulation écartée ni lever une variante obligatoire | Preuve candidate favorable semée : le plan ne s'assouplit pas |
| E4 | Le plan change quand la demande change, à bibliothèque égale ; retirer une fiche change le plan | Deux demandes ; une fiche retirée |
| E5 | Une question sans réponse est rendue « sans preuve », avec le journal de ce qui a été cherché | Question hors bibliothèque et hors web |
| E6 | La recherche pendant la demande passe par AWS | Compte des appels AgentCore égal au journal de recherche |
| E7 | Un document téléchargé qui contient des consignes ne change ni les outils appelés ni le plan | Document piégé semé dans une recherche : le lecteur ne rend que des passages, la porte de citation les contrôle, le plan ne s'assouplit pas |
| E8 | Deux fiches qui se contredisent donnent une pièce, puis un test exécuté ou une objection d'origine « recherche » [R11] | Bibliothèque à deux fiches opposées ; contradiction sans test : « non testable », deux positions affichées |
| E9 | Une réponse qui ne repose que sur la déclaration d'une organisation, ou sur un cours, n'est jamais « étayée » [L01] | Cas semé |
| E10 | Les questions de recherche d'une même demande ont les mêmes clés d'une exécution à l'autre [R01] | Même demande relancée cinq fois |

## F. Sortie, interruption, reprise

| N° | Critère | Vérification |
|---|---|---|
| F1 | Une étude interrompue n'affiche aucune conclusion, et aucune restitution n'y est préparée | Arrêt du processus à chaque étape ; contrôle de l'affichage |
| F2 | La reprise ne refait aucune tâche terminée | Compte des tâches et des appels après reprise |
| F3 | L'état de l'étude est calculé et affiché : arrêtée à la qualification ; en attente de la personne, puis arrêtée faute de réponse ; interrompue ; ou menée à terme avec sa couverture (entière, partielle) et ses conditions (sans, avec) | Sept dossiers construits : demande hors catalogue ; variable nécessaire restée sans réponse passé le délai ; interruption ; les quatre combinaisons d'une étude menée à terme |
| F5 | Une lacune ne suspend rien : l'étude se termine, de couverture partielle, et nomme ce qui manque [R15] | Fiche retirée de la bibliothèque ; outil de recherche coupé |
| F4 | Une question à la personne suspend ce qui en dépend, pas le reste | Étude avec une question en attente |

## G. Deux parcours, les mêmes contrats

| N° | Critère | Vérification |
|---|---|---|
| G1 | Les parcours de Robert et de Mateo (document 07) s'exécutent de bout en bout avec le même code ; seules diffèrent des entrées du catalogue | Revue des différences |
| G2 | Les nombres des deux parcours se retrouvent quand les scripts de `research/experiences/` sont relancés avec les domaines et la batterie du catalogue, à l'erreur de simulation près, mesurée sur plusieurs graines | Comparaison automatique |
| G3 | Chaque parcours montre au moins : une clarification, une preuve manquante ou contradictoire, une comparaison calculée, une objection examinée, une conclusion délimitée, une révision ciblée | Liste de contrôle sur le dossier produit |
| G4 | Avant de dire les contrats généraux, un troisième parcours s'exécute sur une autre décision (« comparer des actifs ») [L04] | Même code ; seul le gabarit change |

## H. Route AWS et observation

| N° | Critère | Vérification |
|---|---|---|
| H1 | Tout appel de modèle du produit passe par Amazon Bedrock | Chaque identifiant de requête du journal se retrouve dans l'historique CloudTrail ; le compte se rapproche de CloudWatch, à l'activité d'autres utilisateurs près |
| H2 | Le produit n'appelle aucun autre service d'inférence | Revue des dépendances et des sorties réseau ; télémétrie de bibliothèques tierces désactivée |
| H3 | Chaque étude a un relevé : appels, jetons, durée, par rôle | Tableau généré |
| H4 | La route de chaque session de développement est consignée | `research/R08-…`, mis à jour |
| H5 | Les relevés tenus par AWS sont exportés avant la fermeture du compte | Fichiers d'export datés, dans le dépôt |
| H6 | Les appels d'une étude sont bornés : limites explicites de tours et de réessais par rôle | Le nombre d'appels du journal ne dépasse pas le budget du catalogue |

## I. L'apport de chaque rôle

Ces mesures ne sont pas des conditions de livraison : elles disent si un rôle mérite de rester distinct. Elles se lisent en comptes bruts, avec leurs témoins (document de recherche, section 7.8). I1, I2, I3 et I5 demandent des personnes, pour annoter, relire ou lire ; I4, I6, I7 et I8 se font sans elles. Aucun seuil n'est écrit ici : chacun s'écrit avec la table de puissance du préalable K3.

| N° | Mesure |
|---|---|
| I1 | Agent 0 : exactitude par champ sur un jeu de demandes difficiles annoté à la main |
| I2 | Agent 1 : jugements de transposition relus par deux personnes ; soutien des preuves candidates sur un échantillon |
| I3 | Agent 2 : choix de la mesure et de la formulation sur des demandes où la bonne mesure n'est pas celle de Robert |
| I4 | Contradicteur : erreurs semées trouvées et fausses alertes, face à la batterie fixe seule |
| I5 | Agent 3 : réponses de lecteurs à des questions qui ne se recopient pas, comparées à ce qu'ils croient avoir compris ; classement des réactions |
| I6 | Chaîne contre agent unique doté des mêmes outils, sur les seuls défauts que les portes laissent passer |
| I7 | Part de la conclusion qui tient à la personne et part qui tient à l'exécution : même demande relancée, et demandes de personnes différentes ; la variation entre exécutions doit rester petite devant la variation entre personnes |
| I8 | Biais de choix : mêmes demandes avec les noms de deux actifs voisins échangés, une autre tournure, l'ordre des candidats inversé ; compte brut des choix qui changent à données égales [L14] |

## J. Interface et honnêteté du produit

| N° | Critère | Vérification |
|---|---|---|
| J1 | Chaque nombre affiché s'ouvre sur son calcul ; chaque source sur son passage, son niveau de lecture et l'état de son soutien | Parcours manuel de deux dossiers |
| J2 | Les trois gestes « je me suis trompé », « ma situation a changé » et « et si… » sont distincts, et l'historique montre une conclusion corrigée comme n'ayant jamais valu, une conclusion dépassée comme ayant valu jusqu'à sa date | Essai sur les trois gestes |
| J3 | Le produit dit ce qu'il ne simule pas : aucun représentant inscrit, aucun comité, aucune conformité, aucun approbateur. La déclaration de portée est insérée par le code ; les mots « indépendant », « approuvé », « conforme » et « validation » ne s'appliquent à aucun rôle ni à aucun contrôle [C14] | Même empreinte du bloc de portée dans tous les dossiers d'une version du catalogue ; restitutions piégées |
| J5 | L'état de supervision est lu au journal : sans événement de relecture, « aucune relecture humaine de ce dossier » [L13] | Marquer un lien « soutient » sans relecture : refusé |
| J4 | Aucun texte du produit ne contient un chiffre ou un sens de comparaison écrit à la main | Vérificateur existant du dépôt |

## K. Calibrations et jeux d'essai

Ce ne sont pas des critères du produit, mais des préalables à ce qu'on aura le droit d'en dire. Chaque critère s'écrit avant l'exécution.

| N° | Préalable | Ce qu'il permet |
|---|---|---|
| K1 | Marges sous hypothèse nulle : un actif placebo de même loi que le titre étudié, rééchantillonnage emboîté ; compte des faux « propre au titre » et des faux « change » | Fixer les tolérances de verdict, aujourd'hui sans source [C05] ; fixer la résolution d'affichage d'un écart |
| K2 | Calibration sur des processus connus, étendue aux longueurs de bloc de la batterie, aux horizons de deux à cinq ans et au sous-échantillon minimal : le signe de l'écart est-il juste dans 95 % des échantillons ? | Confirmer ou déplacer la borne de trois ans, le statut de chaque longueur de bloc et la convention du sous-échantillon [C09, C10, C11] |
| K3 | Table de puissance de chaque jeu d'essai : taux d'atteinte par hasard de chaque seuil | Savoir quels critères peuvent fonder « apport démontré », et lesquels restent descriptifs [L15] |
| K4 | Jeux d'essai fabriqués par le code, avec témoins : demandes difficiles, notes altérées, réécritures d'amendement, restitutions piégées | Les critères C3, C6, D2, D9, D10 |
| K5 | Deux jeux qui demandent des relecteurs nommés : quarante affirmations à juger, vingt couples question-fiche | La mesure I2 ; sans eux, le soutien des citations s'affiche « non mesuré » |
| K6 | Relecture, dans le texte officiel français, des passages canadiens cités | Le droit de les citer en français ; d'ici là, aucune restitution ne contient de citation tirée d'une consolidation non officielle |
| K7 | Un dossier de référence exécuté avec un autre modèle et un autre compte, passés en paramètres | Ce qui reste exécutable après lundi 13 h 59 |
| K8 | Un échantillon d'affirmations amendées et de réserves reformulées, relu par un membre nommé | Ce que les portes ne voient pas : le sens des phrases |
| K9 | Un essai de lecture auprès de quelques personnes, si la décision de direction 3 l'autorise | La mesure I5 |
| K10 | La même tâche de rôle écrite des deux façons : appel direct de Bedrock, et bibliothèque d'agents | Le choix de la boucle des rôles, que les essais du 15 novembre ne départagent pas |

