> **Conception, non construite** (15 novembre 2026). Rien de ce document n'est en service dans le produit. Les passages sur le calendrier, les décisions à prendre et l'organisation du travail sont historiques : ce ne sont pas des consignes. Certaines pièces de travail citées (`research/fiches/`, `research/R08-…`, `docs/etat.md`, `docs/coordination.md`) ne sont pas dans cette archive. Entrée de l'archive : `LIRE_EN_PREMIER.md`.

# 05 — Types de résultats et règles de présentation

Les expériences du 15 novembre (`research/R09-…`) ont montré que certains résultats dépendent fortement des conventions de calcul, que d'autres ne sont pas déterminés par cinq ans de données, et que certaines comparaisons tiennent dans tout ce qui a été essayé. Ce document dit comment le système distingue ces résultats, de l'analyse jusqu'aux titres et aux graphiques. Il ne transforme aucun constat fait sur Robert ou sur Tesla en règle du moteur. Les numéros entre crochets renvoient à la table de résolution (document 01).

## 1. Règles de procédure et constats

- Une **règle de procédure** dit comment calculer et quoi vérifier. Elle vaut pour tout dossier. Exemples : comparer deux options sur les mêmes trajectoires ; faire varier l'hypothèse de rendement ; retirer tour à tour chaque année de l'échantillon ; chercher un comparateur de volatilité voisine ; calculer sous deux conventions.
- Un **constat** est ce que ces procédures ont donné sur un dossier. Il vaut pour les données, le portefeuille, les options et la question de ce dossier. Exemples mesurés sur le dossier de Robert : la longueur de bloc pèse peu ; l'écart entre « 10 % de Tesla » et « ne rien changer » est positif dans toutes les variantes ; cet écart n'est pas propre à Tesla.

Le moteur ne contient que des règles de procédure. Un constat se **remesure à chaque dossier** ; il n'est réemployé que si les empreintes des données, des portefeuilles et de la formulation sont les mêmes (document 02, « encore applicable »). En particulier, l'ordre dans lequel la batterie éprouve les choix d'analyse n'est pas figé d'après Robert : elle les éprouve tous, et classe leur influence sur le dossier en cours.

## 2. Sept types de résultats

Toute affirmation de la conclusion porte un type, une portée et des conditions de réemploi. L'agent 2 choisit le type parmi ceux que la formulation de calcul autorise ; l'agent 3 ne peut pas le changer. À chaque type correspond un jeu de rendus, calculé par le code avant le travail de l'agent 3 : un seul rendu par type, de sorte que deux restitutions de la même note ne puissent pas s'ouvrir sur deux chiffres différents [R12, C13].

| Type | Ce que le calcul doit fournir | Comment l'agent 2 l'affirme | Comment l'agent 3 le montre | Interdit | Nouvelle analyse imposée si |
|---|---|---|---|---|---|
| **1. Mesure historique** | Valeur observée, fenêtre, convention de la table du catalogue (rendement total composé, avant frais, devise, fréquence ; jamais annualisé sur moins d'un an) [L10] | Au passé, datée : « sur la fenêtre observée, … » | Titre au passé ; tableau ou courbe de l'historique ; mentions « une seule histoire », « avant frais », « en dollars courants » [L08, L09] | La présenter comme une borne ou un seuil pour l'avenir | Les données, le portefeuille ou la convention changent |
| **2. Estimation avec incertitude** | Valeur, intervalle d'échantillonnage, méthode de l'intervalle | Valeur et intervalle ensemble | Barre avec intervalle ; jamais la valeur seule dans un titre | Une précision plus fine que l'intervalle | Idem |
| **3. Proportion de trajectoires simulées** | Part sous chaque hypothèse de rendement de la grille ; intervalle d'échantillonnage ; sensibilité au retrait d'une année ; erreur de simulation | Seulement comme illustration, dans la partie « dépend d'une hypothèse » | Dans le détail, en pourcentage, avec sa plage, qui est l'enveloppe de toutes les variantes ; libellé « part des scénarios construits à partir des années observées » | Les mots « probabilité », « risque de », « chances » ; un titre, un chiffre de tête, une jauge ; un compte « sur 100 » ; une place avant la comparaison qu'elle illustre | Idem, ou changement de seuil ou d'horizon |
| **4. Comparaison entre options** | Écart apparié ; intervalle d'échantillonnage sous chaque valeur de base de la batterie ; signe dans toutes les variantes à question fixée ; même écart pour un comparateur de volatilité voisine | « Le sens est établi » seulement si l'intervalle à 90 % exclut zéro sous chaque valeur de base et si le signe est le même dans toute la batterie ; la taille avec son intervalle ; mention si l'écart n'est pas propre au titre | En tête de la restitution ; barres d'écart avec intervalle ; phrase de sens avant la taille | Un écart dont l'intervalle à 90 % contient zéro présenté comme une différence ; un nom de titre quand l'écart est celui de tout titre aussi volatil | Une option change ; le comparateur change |
| **5. Condition ou rendement d'équilibre** | Valeur d'équilibre sous chaque hypothèse de base, intervalle, mesure retenue, et une issue « hors du domaine » quand aucune valeur essayée ne suffit [L07]. Ce type reçoit aussi le test inversé (la baisse du titre qui amènerait le portefeuille à un seuil donné [R05]) et le taux requis par un objectif, quand la personne donne un montant [C12] | « Il faudrait que … pour que … » | Au conditionnel, comme une question posée à la personne ; jamais comme une attente ; jamais parmi les parts de trajectoires | Toute tournure de prévision ou de fréquence | L'hypothèse de base ou la mesure change |
| **6. Résultat sensible aux conventions** | Une valeur par convention déclarée (fréquence, devise, rééquilibrage, change neutralisé ou non) | Toutes les valeurs ; une conclusion seulement si elle tient sous chacune | Les valeurs côte à côte, conventions nommées | Une valeur unique | Toujours recalculé sous chaque convention |
| **7. Conclusion insuffisamment étayée** | Ce qui manque : donnée, source, test | « Sans preuve », « non testable », ou abstention motivée | Dans un bloc à part, au même niveau que les résultats ; avec ce qu'il faudrait pour conclure | La taire ; la trancher par une formule générale | — |

### Ce qui permet d'affirmer un sens

Convention de l'équipe, inscrite à la table des seuils, à réviser par l'essai « marges sous hypothèse nulle » (document 09). Elle n'emploie aucune marge en points : un signe conservé, un intervalle qui exclut zéro. Elle garde pourtant un nombre choisi, le niveau de 90 % de l'intervalle, qui est lui-même une convention sans source.

- Le sens d'un écart est **établi** si l'intervalle à 90 % de l'écart apparié, obtenu en rééchantillonnant l'histoire, exclut zéro sous chaque valeur de base de la batterie de sa formulation, et si l'écart garde le même signe dans toutes les variantes de cette batterie, à question fixée. Pour des trajectoires, les valeurs de base sont chaque hypothèse de rendement de base et chaque longueur de bloc de base ; pour une mesure de risque, chaque fréquence déclarée.
- Il est **établi avec réserve** s'il tient sous les hypothèses de base et se renverse sous une hypothèse « borne » seulement : l'affirmation porte alors la réserve nommée, et le rendement d'équilibre l'accompagne [C07].
- Il est **non établi** sinon, et l'affirmation est de type 7.
- Aucun écart dont l'intervalle contient zéro n'est restitué comme une différence. Cette résolution d'affichage tient au niveau de l'intervalle, 90 % aujourd'hui, qui reste à caler.
- Le titre demandé n'est nommé que si l'écart entre lui et le comparateur de volatilité voisine est lui-même établi ; sinon l'affirmation parle d'« un titre isolé aussi volatil ». La note dit si le comparateur désigné change sous une autre convention ou après retrait d'une année [C20].

**Hypothèses de base et bornes.** Le catalogue donne un statut à chaque hypothèse de rendement : « base » pour l'absence de rendement crédité et pour le taux sans risque observé ; « borne d'affichage » pour la moyenne des cinq années, qu'aucun échantillon de cette taille ne fonde. Il en va de même des longueurs de bloc : le tirage semaine par semaine est une borne, connue pour sous-estimer les baisses. Une borne est calculée et montrée comme l'extrémité étiquetée d'une plage (« si l'on prolongeait les rendements des cinq dernières années ») ; elle ne fonde jamais une affirmation [C07, C09].

Le seuil et l'horizon ne sont pas des choix d'analyse : ils appartiennent à la question de la personne. Ils se balaient à part, sur le domaine du catalogue, et le résultat de ce balayage va dans la partie « dépend de la personne ». Un résultat lu au bord d'un domaine porte la marque « bord de domaine, non exploré au-delà » ; il n'est jamais présenté comme un maximum ni comme un seuil [R16]. Le balayage de la part ne rend jamais une part recommandée ni une part maximale [L05].

### Les types et les quatre parties de la conclusion

| Partie de la conclusion | Types qu'elle peut contenir |
|---|---|
| 1. Ce qui tient sous toutes les hypothèses essayées | 4 (sens établi), 1, 6 |
| 2. Ce qui dépend d'une hypothèse | 3 (en illustration), 4 (établi avec réserve), 2 |
| 3. Ce qui dépend de la personne | 5, et les cas que départage une inconnue à balayer |
| 4. Ce qu'aucun calcul ne donne | 7 |

Aucune affirmation sans type, et un seul type par affirmation : une mesure historique donnée sous plusieurs conventions est de type 6. Les cas que départage une inconnue ne sont pas des affirmations : ils renvoient à des affirmations typées. Un écart qui ne se distingue pas de zéro est une affirmation de type 7 ; quand il nuance une comparaison établie (« l'écart n'est pas propre au titre »), il s'écrit comme une mention de cette comparaison.

### Ce qui n'est pas un résultat

Quatre sortes d'éléments s'affichent sans être des affirmations typées.

- **Les constats sur les déclarations** : un écart apparent entre la demande et le profil déclaré, une contradiction non levée. Ils se montrent par leurs deux citations, sous la formule « écart constaté par rapport au profil déclaré ». L'absence d'écart ne s'établit jamais : elle s'affiche avec la réserve « capacité de perte inconnue » [C04].
- **Les relevés de l'étude** : nombre d'essais, de tests, d'objections par verdict, types d'objection non couverts. Ce sont des nombres du code, qui décrivent le travail et non le portefeuille [R06]. L'état de l'étude, la fenêtre des données et la date de validité en font partie.
- **Les repères cités** : un nombre tiré d'un texte, comme le plafond par émetteur d'un règlement sur les fonds ou une hypothèse de rendement publiée. Il se montre comme une citation, avec sa nature et sa source ; il n'entre dans aucun verdict et n'est jamais présenté comme une limite [L06].
- **Les marques** qui suivent une affirmation jusqu'à la restitution : « exploratoire » (calcul hors plan), « postérieur » (calcul lancé sous une ligne du plan amendée après des résultats), « ajoutée après le premier affichage », « bord de domaine », « passage cité, soutien non relu ».

## 3. Le profil de risque de l'énoncé

L'énoncé donne à chaque profil un « profil de risque » (élevé, modéré, faible à modéré). C'est un **fait déclaré**, d'origine « énoncé », conservé tel quel. Ses composantes ne sont pas renseignées : la tolérance (ce que la personne accepte de voir) et la capacité (ce qu'elle peut absorber) restent des **inconnues**.

Conséquences :

- le profil déclaré sert à constater un écart entre la demande et le profil, en mots (« la demande porte sur un titre isolé ; le profil déclaré est faible à modéré ») ;
- il ne sert jamais à fabriquer un seuil chiffré : un seuil de perte ne vient que d'une réponse de la personne ; à défaut, il se balaie, et il n'est demandé après l'analyse que si deux valeurs du domaine mènent à deux cas différents [C02] ;
- l'étude dit ce qui dépend de la composante inconnue, et la question posée après l'analyse porte sur elle.

## 4. Les préférences ESG

| Ce que les données permettent de vérifier | Ce qui demanderait d'autres sources |
|---|---|
| Le secteur de chacune des vingt actions (champ « sector » du jeu de départ) : une exclusion par secteur est vérifiable pour les lignes détenues en direct | La composition des fonds : un fonds large peut contenir le secteur exclu, et rien ne permet de le voir |
| L'étiquette d'un fonds de l'univers, décrit comme filtré selon des critères ESG : c'est un fait sur l'étiquette | Les critères de ce filtrage, leur application, les controverses |
| Le comportement de ce fonds face au fonds large (corrélation, volatilité), comme toute comparaison de type 4 | Une notation ESG des titres, d'une ou de plusieurs agences, avec leur désaccord |

Le système peut donc affirmer « parmi vos lignes détenues en direct, aucune n'appartient au secteur exclu » ; il ne peut pas affirmer « ce portefeuille ne contient pas de pétrole », ni « ce fonds respecte vos préférences ». Une préférence ESG se recueille en détail (ce qu'il faut exclure, jusqu'où), s'applique comme une contrainte là où elle est vérifiable, et donne lieu ailleurs à une abstention de type 7 qui nomme la source manquante.

La chaîne va donc au bout [C17]. Une table du catalogue traduit la préférence en lectures : sans exclusion ; sans les lignes que la personne désigne dans le secteur qu'elle nomme ; le fonds filtré à la place du fonds large. L'agent 0 ne choisit aucun secteur et ne classe aucun titre : le secteur vient des données, le choix vient de la personne. Les options se comparent par écarts appariés, comme les autres. Aucune n'est dite « ESG », « durable » ou « conforme à la préférence » : elle se nomme « sans le secteur de l'énergie » ou « avec le fonds que son émetteur dit filtré, critères absents de nos données ». Une recherche pendant la demande qui ne trouve rien ne vaut jamais absence de controverse.

## 5. L'horizon

Une table du catalogue, « couverture des horizons », donne la même réponse aux quatre rôles [C10, C12].

| Horizon du calcul | Ce que l'étude peut donner |
|---|---|
| Jusqu'à trois ans (156 semaines) | Trajectoires rééchantillonnées, pour comparer des options ; mesures historiques |
| Fenêtres historiques glissantes | Jusqu'à la moitié de l'échantillon (130 semaines) ; à trois ans, l'histoire observée se montre comme une trajectoire unique |
| De trois à dix ans | Abstention motivée sur toute distribution ; à la place : mesures historiques, écarts à trois ans, rendement d'équilibre |
| Dix ans et plus | Abstention ; un taux requis, de type 5, seulement si la personne donne un montant. Aucune probabilité d'atteindre un objectif |

L'horizon déclaré par la personne reste un fait ; l'horizon du calcul est un paramètre balayé (un, deux, trois ans). La borne de trois ans est une convention de l'équipe, arrêtée après avoir vu les données. La calibration faite ce jour ne porte que sur un an et sur trois ans (R09, X8) ; deux ans n'ont pas été calibrés. La borne ne bouge que par une nouvelle version du catalogue, après la calibration du document 09 (K2).

**Les usages d'un sous-échantillon** [C11]. « Hors échantillon » recouvre quatre usages, que le catalogue traite séparément : choisir une option sur un échantillon mis de côté est écarté ; éprouver la stabilité d'un écart par sous-période (retrait de chaque année, départ décalé) appartient à la batterie fixe ; comparer aux années réalisées est un constat descriptif, sans verdict ; contrôler une prévision de risque est admissible avec réserve, et n'est pas implémenté. Aucun sous-échantillon n'est plus court que l'horizon du calcul : convention sans source, arrêtée après avoir vu les données.

## 6. Ce que l'agent 3 doit respecter

- Chaque phrase de fait rend une affirmation, dont elle hérite le type, ou l'un des quatre éléments de la section 2 qui s'affichent sans type. La porte de restitution refuse une phrase dont la tournure n'est pas celle du type (liste de tournures par type dans le catalogue), un titre qui porte une proportion de trajectoires, un graphique d'un type non autorisé pour l'affirmation qu'il montre.
- L'ordre de tête est fixé : ce qui est établi (types 4 et 1), ce qu'il faudrait (type 5), ce qui dépend de la personne, ce qui dépend d'une hypothèse (type 3, en illustration), ce qu'on ne peut pas dire (type 7).
- Les trois profondeurs rendent les mêmes affirmations ; seul le détail change. Chaque réserve y figure, près de son affirmation.
- Une question posée à la personne dit son enjeu comme un écart ou un changement de mesure, jamais comme un niveau.
- Un résumé ne peut pas être plus affirmatif que la plus faible des affirmations qu'il résume.
