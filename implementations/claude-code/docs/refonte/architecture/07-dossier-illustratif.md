> **Conception, non construite** (15 novembre 2026). Rien de ce document n'est en service dans le produit. Les passages sur le calendrier, les décisions à prendre et l'organisation du travail sont historiques : ce ne sont pas des consignes. Certaines pièces de travail citées (`research/fiches/`, `research/R08-…`, `docs/etat.md`, `docs/coordination.md`) ne sont pas dans cette archive. Entrée de l'archive : `LIRE_EN_PREMIER.md`.

# 07 — Dossier illustratif et parcours contrasté

Deux parcours montrent ce que chaque rôle reçoit, crée et transforme. **Ce ne sont pas des traces d'exécution** : l'application décrite ici n'existe pas encore. Trois marques distinguent ce qui est dit :

- **[mesuré]** : nombre calculé le 15 novembre sur les données du projet, par un script nommé, hors produit ;
- **[illustratif]** : pièce écrite pour l'exemple (une demande, une réponse, un portefeuille fictif, un texte de restitution) ;
- **[attendu]** : comportement que le futur système devra avoir, non exécuté.

Trois précautions. Les pièces montrées sont des **extraits** : une fiche de qualification réelle porte les six éléments du profil, une note réelle porte aussi son bloc de coûts et sa table de couverture. Les parts de trajectoires sont des scénarios construits sur cinq années observées, pas des probabilités ; les autres nombres sont des mesures sur la fenêtre observée. Enfin ces calculs ont été faits **avant** que le catalogue soit écrit : ils emploient un seuil (15 %), un horizon (trois ans) et deux parts (5 % et 10 %) pris pour l'exemple dans des domaines que le système balaierait en entier, et une partie seulement de la batterie fixe. Là où une règle du document 05 demanderait davantage, c'est dit.

Les numéros entre crochets (C01, R16…) renvoient à la table de résolution (document 01). Scripts des nombres : `research/experiences/dossier_illustratif.py`, `ecart_et_niveau.py`, `rendement_d_equilibre.py`, `calibration_reechantillonnage.py`, `parcours_contraste.py` ; sorties dans `research/experiences/sorties/`.

## Parcours 1 — Robert et un titre isolé

### Vue d'ensemble

| Étape | Qui | Ce qui entre | Ce qui est créé | Ce qui change dans le dossier |
|---|---|---|---|---|
| 1 | La personne | — | Demande : « J'aimerais consacrer une partie de mon portefeuille à Tesla ; on en parle partout. » [illustratif] | Version 1 de la demande |
| 2 | Agent 0, puis le code | Demande ; profil de l'énoncé ; catalogue ; fiche des données | Fiche de qualification ; une question à la personne ; les questions de recherche, instanciées depuis la table du catalogue | Le problème existe ; une variable nécessaire manque ; l'horizon du calcul est borné à trois ans |
| 3 | La personne | Question affichée | Réponse : elle retient le portefeuille fictif proposé [illustratif] | Version 2 de la demande, de nature « précision » |
| 4 | Agent 1 | Questions de recherche ; bibliothèque ; données | Dossier de preuves ; plan des méthodes ; fiche produit ; une contradiction entre sources | Les formulations ont un statut ; une objection d'origine « recherche » attend la note |
| 5 | Agent 2 ; le code pour les options de base, la batterie et les rendus | Fiche de qualification ; plan des méthodes ; fiche produit | Options ; plan d'analyse scellé ; calculs ; note d'analyse | Les comparaisons existent, typées |
| 6 | Batterie fixe, puis contradicteur ; l'agent 2 amende | Plan, note, table des variantes | Objections, verdicts, effets requis, réserves, bilan de confrontation | Une illustration réservée, un avis inscrit en limite ; aucun amendement dans cet exemple |
| 7 | Agent 3 ; le code désigne la question | Conclusion ; registre, réserves et bilan ; abstentions | Restitution aux trois profondeurs ; question posée après l'analyse | Affichage enregistré |
| 8 | La personne | Restitution affichée | Deux précisions : « pas de retrait », « plutôt 5 % » [illustratif] | Version 3 de la demande ; aucun calcul refait |
| 9 | La personne | Restitution révisée | Une correction : le poids de deux lignes du portefeuille [illustratif] | Version 4 de la demande ; révision ciblée |

### Agent 0 : la fiche de qualification [illustratif, extrait]

| Pièce | Contenu | Origine |
|---|---|---|
| Décision | Ajouter un titre isolé à un portefeuille | Catalogue |
| Fait : titre visé | Tesla, rattaché à l'actif TSLA de l'univers | Demande : « à Tesla » |
| Fait : motif déclaré | « on en parle partout » ; sans effet sur le profil | Demande |
| Fait : profil de risque | Faible à modéré, « non chiffré » | Énoncé |
| Fait : horizon | Trois à cinq ans | Énoncé |
| Fait : objectif | Préserver le capital ; forme mesurable « à départager » entre baisse en cours de route et perte à l'échéance | Énoncé |
| Écart apparent | Un titre isolé est demandé ; l'objectif est de préserver le capital et le profil déclaré est faible à modéré. Ce n'est pas un jugement de convenance | Les deux citations |
| Inconnue nécessaire | Portefeuille de départ | Table des variables de la décision [C01] |
| Inconnues à balayer | Part envisagée ; perte acceptée ; retrait prévu avant l'échéance ; horizon du calcul | Même table ; les domaines viennent du catalogue [R16] |
| Inconnue non informable | La capacité à absorber une perte : la situation financière n'est pas recueillie | Même table |
| Abstention | Au-delà de trois ans : aucune trajectoire. L'horizon déclaré va jusqu'à cinq ans ; quatre et cinq ans ne seront pas étudiés | Table des horizons du catalogue [C10, C12] |
| Signaux retenus | La demande vient de la personne ; il y a un écart apparent avec le profil ; l'horizon déclaré dépasse ce que les données portent | Demande et énoncé |
| Questions de recherche | Que disent les données de ce titre ? Quelle mesure rend « préserver le capital » ? Quelles formulations comparent l'ajout d'un titre sur ces données ? | Instanciées par le code, depuis la table du catalogue, pour cette décision et ces signaux [R01] |

**Une clarification utile.** La seule question posée avant l'analyse est celle sans laquelle rien ne se calcule : « Quel est votre portefeuille actuel ? ». Le produit propose avec elle un portefeuille fictif, pièce du catalogue (40 % XBB.TO, 10 % ZST.TO, 30 % XIU.TO, 20 % SPY), que le répondant peut retenir ; le fait porte alors l'origine « proposé par le produit, retenu par le répondant ». La part envisagée et la perte acceptée ne sont pas demandées : elles se balaient. [attendu]

**Aucune découverte n'atteint ici le problème parent.** La limite d'horizon est connue dès la qualification, par une table du catalogue : ce n'est pas une trouvaille de la recherche. Le mécanisme du document 04 servirait si, par exemple, un test de condition échouait sur le titre demandé. [attendu]

### Agent 1 : le dossier de preuves [extrait]

| Question | Réponse | Fondement |
|---|---|---|
| Mesure de « préserver le capital » | Étayée avec réserve : une perte maximale sur une période ; deux lectures possibles, en route ou à l'échéance | Une fiche tirée d'un cours du CFA Institute [registre, QUA-S09] ; un cours seul plafonne la réponse [L01] [illustratif] |
| Rendement moyen passé | Hypothèse de statut « borne » au catalogue : calculée, montrée, jamais base d'une affirmation | Résultat théorique [ANA-S01] ; [mesuré] il faudrait 453 ans pour distinguer une prime de 5 points (R09, X3) |
| Écarts entre options sur trajectoires rééchantillonnées | Formulation autorisée ; la batterie fixe du catalogue s'applique | [ANA-S02] ; [mesuré sur des processus simulés, R09, X8] le signe de l'écart est juste dans 99 à 100 % des échantillons à trois ans, 91 à 100 % à un an |
| Proportion de trajectoires comme niveau | Admise en illustration seulement | [mesuré sur des processus simulés, R09, X8] à trois ans, 21 à 77 % seulement des échantillons donnent le niveau à 10 points près |
| Ce que les données disent du titre | Fiche produit : action américaine, secteur « consommation discrétionnaire », cotée en dollars américains ; coûts : inconnus ; risques observés : renvois à des calculs du dossier | Fiche des données |
| Les perspectives du titre justifient-elles le risque ? | **Sans preuve** : ni états financiers ni nouvelles dans les données | — |

**Une preuve contradictoire.** Sur le rééchantillonnage à long horizon, une source annonce un biais et deux études de 2026 le classent premier pour simuler des baisses ; les trois ne sont connues que par leur résumé (registre, ANA-C09 et sources ajoutées par le vérificateur). L'agent 1 en fait une pièce « contradiction entre sources », avec le test du catalogue qui les départagerait sur nos données : la calibration sur des processus connus. La ligne du plan reçoit une réserve, et le code inscrit une objection d'origine « recherche », qui attend la note. [attendu]

### Agent 2 : options, comparaison calculée, conclusion

Options. La règle du catalogue en impose quatre : « ne rien changer » ; l'ajout demandé, dont la part se balaie puisque Robert ne l'a pas dite ; et deux comparateurs, à la même part : le fonds de l'univers le plus corrélé au titre, QQQ (corrélation 0,59), et l'actif isolé non détenu de volatilité la plus proche, Bitcoin (51 % contre 56 %). [mesuré] L'agent 2 n'en ajoute pas ici ; il aurait pu ajouter une autre part du même titre, en la marquant comme sienne. La note dit ce que vaut la désignation : le fonds reste QQQ quand on retire tour à tour chaque année ; l'actif de volatilité voisine devient Shopify si l'on retire la première. [mesuré]

**Une comparaison calculée** [mesuré]. Écart, avec « ne rien changer », de la part des trajectoires de trois ans ; intervalles à 90 % sur 400 histoires rééchantillonnées, à la longueur de bloc de treize semaines.

| Option | Baisse de plus de 15 % en route, au taux sans risque | Même mesure, sans rendement crédité | Perte à l'échéance, au taux sans risque | Même mesure, sans rendement crédité |
|---|---|---|---|---|
| 10 % de Tesla | +25,6 points (+16,2 à +42,3) | +24,9 (+17,3 à +40,4) | +7,7 (+4,2 à +13,4) | +2,6 (−0,7 à +3,5) |
| 5 % de Tesla | +9,9 (+4,1 à +18,1) | +9,9 (+5,7 à +17,9) | +3,4 (+1,0 à +6,7) | +1,1 (−1,0 à +1,9) |
| 10 % de QQQ | +9,7 (+2,7 à +14,1) | +8,5 (+5,4 à +14,2) | +3,1 (+1,4 à +4,6) | −0,0 (−0,8 à +1,2) |
| 10 % de Bitcoin | +28,0 (+14,1 à +39,0) | +23,2 (+16,8 à +35,7) | +9,5 (+4,6 à +12,3) | +0,8 (−1,5 à +2,3) |

Sur la baisse en route, l'écart entre 10 % de Tesla et 10 % de Bitcoin va de −13,8 à +18,6 points au taux sans risque : il contient zéro. L'écart entre 10 % de Tesla et 10 % de QQQ va de +8,9 à +32,9 points au taux sans risque et de +8,6 à +30,9 sans rendement crédité : il est au-dessus de zéro.

Selon la longueur de bloc, l'écart de « 10 % de Tesla » sur la baisse en route reste au-dessus de zéro [mesuré] :

| Longueur de bloc | Au taux sans risque | Sans rendement crédité |
|---|---|---|
| 4 semaines | +22,0 à +40,1 | +21,9 à +36,8 |
| 13 semaines | +16,4 à +41,4 | +18,4 à +41,5 |
| 26 semaines | +11,4 à +43,2 | +14,0 à +43,2 |
| 1 semaine (borne) | +25,6 à +37,2 | +23,6 à +34,3 |

La ligne de treize semaines vient d'un autre tirage que la table précédente, d'où un écart de quelques dixièmes de point.

**Une conclusion correctement délimitée** [illustratif pour le texte, mesuré pour les nombres]. Les quatre parties et les types sont ceux du document 05.

| Partie | N° | Affirmation | Type |
|---|---|---|---|
| 1. Ce qui tient sous toutes les hypothèses essayées | A1 | Ajouter 10 % d'un titre isolé aussi volatil que Tesla rend plus fréquentes les baisses de plus de 15 % en cours de route, sur trois ans. Le sens est établi : l'intervalle est au-dessus de zéro sous les deux hypothèses de base et aux trois longueurs de bloc de base, et le signe est le même dans les 54 variantes calculées. Taille : de 16 à 42 points à la longueur de treize semaines, de 11 à 43 selon la longueur. Mention : l'écart n'est pas propre à Tesla ; celui de l'actif de volatilité voisine ne s'en distingue pas. À 5 %, l'intervalle est lui aussi au-dessus de zéro sous les deux hypothèses de base (4 à 18 points) ; le reste de la batterie n'a pas été calculé à cette part | 4 |
| | A2 | Sur la fenêtre observée, une seule histoire, la pire baisse du portefeuille avec 10 % du titre a été de −15,3 % en valorisation hebdomadaire et de −16,7 % en valorisation quotidienne ; sans rien changer, de −12,3 % et de −12,7 % | 6 |
| 2. Ce qui dépend d'une hypothèse | A3 | En illustration : la part des scénarios où le portefeuille avec 10 % du titre franchit 15 % va de 16 % à 67 % selon les variantes, hors moyenne passée ; elle est de 45 % au taux sans risque. Pour « ne rien changer » : 19 % au taux sans risque, 35 % sans rendement crédité, plage non calculée pour l'exemple | 3 |
| 3. Ce qui dépend de la personne | A4 | Pour que l'ajout de 10 % du titre ne rende pas plus fréquente une perte au bout de trois ans, il faudrait qu'il rapporte, avant frais, environ 13 points par an de plus que le taux sans risque (entre 8 et 26). Calculé sous une seule hypothèse de base | 5 |
| | A5 | Pour la baisse en route : sur l'histoire observée, aucune valeur du domaine essayé (jusqu'à 80 points par an) ne suffit ; dans un quart des histoires rééchantillonnées, une valeur de 44 à 80 points suffit. Résultat au bord du domaine, non exploré au-delà | 5 |
| | — | Le cas qui s'applique : si un retrait est prévu avant trois ans, c'est la baisse en route qui compte (A1, A5) ; sinon, la perte à l'échéance (A4, A6). Ce n'est pas une affirmation : c'est l'inconnue « retrait prévu » qui départage | — |
| 4. Ce qu'aucun calcul ne donne | A6 | Sur la perte à l'échéance, le sens n'est pas établi : positif au taux sans risque (de 4 à 13 points), non distinguable de zéro sans rendement crédité | 7 |
| | A7 | À part égale, l'écart entre l'ajout du titre et celui du fonds le plus corrélé va de 9 à 33 points au taux sans risque et de 9 à 31 sans rendement crédité, à la seule longueur de treize semaines. Au sens du document 05, ce sens n'est pas encore établi : il manque les autres longueurs de bloc et le retrait de chaque année | 7 |
| | A8 | Les perspectives du titre : sans preuve (abstention de l'agent 1, reprise) | 7 |
| | A9 | L'horizon de quatre à cinq ans : non étudié (abstention de l'agent 0, reprise) | 7 |

Toutes les options font pire que « ne rien changer » sur la baisse en route : A4 et A5 valent « sur le seul risque », et la note le dit (document 03, porte d'analyse).

État de l'étude : menée à terme ; couverture **partielle** (quatre et cinq ans, et les perspectives du titre, restent hors de portée) ; **conditionnelle** (un retrait prévu change la mesure qui compte).

### Batterie fixe, recherche, contradicteur : les objections

Une règle s'applique avant toute objection, à la porte d'analyse : le titre n'est nommé que si son écart se distingue de celui de l'actif de volatilité la plus proche. Ici l'écart entre les deux contient zéro [mesuré] : la note parle donc d'emblée d'« un titre isolé aussi volatil », sans objection ni verdict.

Pour les objections, les critères sont ceux de la table des seuils ; aucun n'est écrit pendant la demande.

| Origine | Objection | Visée | Test | Résultat | Verdict [attendu] |
|---|---|---|---|---|---|
| Batterie fixe | Le résultat tient-il à une seule année ? | A1, A3 | Retrait tour à tour de chaque année, au taux sans risque | [mesuré] L'écart reste entre +23,0 et +31,5 points ; le niveau avec 10 % du titre passe de 45 % à 26 % sans la première année | A1 tient ; A3 porte la réserve |
| Batterie fixe | La pire baisse n'est-elle vue que le vendredi ? | A2 | Valorisation quotidienne | [mesuré] −16,7 % au lieu de −15,3 % | Les deux valeurs sont données : type 6 |
| Recherche (agent 1) | Le rééchantillonnage est-il fiable à trois ans ? | A1, A3 | Calibration sur des processus connus | [mesuré sur des processus simulés] Signe juste dans 99 à 100 % des échantillons ; niveau à 10 points près dans 21 à 77 % | A1 tient ; A3 garde sa réserve |
| Contradicteur | L'écart dépasse-t-il celui d'un actif quelconque de l'univers ? | A1 | Même ajout avec chacun des 27 actifs non détenus | [mesuré] L'écart est positif pour 17 ou 18 d'entre eux selon l'hypothèse ; celui de Tesla est au quatrième ou cinquième rang | Tient : la formule « aussi volatil » est confirmée, et l'écart n'est pas celui de n'importe quel actif |
| Contradicteur | « Ne rien changer » est-il lui-même à l'abri du seuil ? | A2, A3, pour les valeurs de « ne rien changer » | Un test du catalogue sur le seul portefeuille de départ | [attendu, non calculé pour l'exemple] | [attendu] |
| Contradicteur | Les perspectives de Tesla peuvent justifier le risque | La conclusion | Aucun : ni états financiers ni nouvelles | — | Non testable : avis joint, affiché dans les limites |

Dans cet exemple, la batterie et les règles du catalogue font l'essentiel ; le contradicteur ajoute un test, l'objection que son contrat exige sur « ne rien changer », non calculée ici, et un avis. Ce qu'il apporte au-delà de la batterie est précisément ce que l'essai d'erreurs semées doit mesurer (document 09, I4).

### Agent 3 : restitution et question [illustratif, extrait]

Extrait de la profondeur « essentiel » : le résumé d'ouverture et la question. La restitution complète rend chacune des neuf affirmations, avec ses réserves ; cet extrait ne reproduit ni A2, ni A3, ni A5, ni A7. Les deux premières lignes sont insérées par le code.

> *Simulation. Aucun représentant inscrit, aucun comité, aucune conformité. Aucune relecture humaine de ce dossier.*
> *Étude menée à terme ; couverture partielle ; conditionnelle. Elle vaut pour les cinq années de données du jeu de départ, avant frais et en dollars courants, jusqu'à la date de validité fixée au catalogue.*
>
> **Écart constaté par rapport au profil déclaré.** Vous demandez un titre isolé. Votre objectif déclaré est de préserver le capital, et votre profil de risque déclaré est « faible à modéré ».
>
> **Ce que les cinq années observées établissent.** Vous n'avez pas dit quelle part vous envisagez ; deux ont été essayées. Ajouter 10 % d'un titre isolé aussi volatil que Tesla à ce portefeuille rend plus fréquentes, dans les scénarios construits à partir de ces années, les baisses de plus de 15 % en cours de route sur trois ans : l'écart avec « ne rien changer » va de 16 à 42 points, et il n'est pas propre à Tesla. À 5 %, l'écart va de 4 à 18 points ; les autres vérifications n'ont pas été faites à cette part. Réserve : deux sources se contredisent sur cette méthode à long horizon.
>
> **Ce qu'il faudrait.** Sur la perte au bout de trois ans, le sens n'est pas établi : il dépend du rendement qu'on crédite. Si l'on crédite à tous les actifs le taux sans risque, il faudrait, pour un ajout de 10 %, que le titre rapporte, avant frais, environ 13 points par an de plus (entre 8 et 26) pour que l'ajout ne rende pas cette perte plus fréquente. Ce calcul n'a pas été fait pour 5 %.
>
> **Ce qui dépend de vous.** Prévoyez-vous de retirer de l'argent de ce portefeuille avant trois ans ? (Oui ; non ; je ne sais pas.) Si oui, ce sont les baisses en cours de route qui comptent ; sinon, c'est la valeur au bout de trois ans.
>
> **Ce que nous ne pouvons pas dire.** Rien, dans nos données, ne permet de juger les perspectives de Tesla, ni ce qui se passerait au-delà de trois ans. Nous n'avons aucune donnée de frais.

La question est désignée par le code : l'inconnue « retrait prévu » change la mesure qui s'applique. La part, elle, ne donne lieu à aucune question : aux deux parts essayées, le cas est le même. La question est rédigée par l'agent 3, et sa réponse entrera par l'agent 0. [attendu]

### Deux précisions : rien n'est recalculé

Robert répond : « Non, pas de retrait. Et je pensais plutôt à 5 %. » [illustratif] Ce sont deux **précisions** : chacune remplace une inconnue par une valeur, la première en réponse à la question, la seconde de sa propre initiative, et les deux valeurs sont dans le domaine déjà balayé.

| Rouvert | Conservé, réemployé sans recalcul |
|---|---|
| Version 3 de la demande ; faits « aucun retrait prévu » et « part envisagée : 5 % » | Fiche des données ; dossier de preuves ; plan des méthodes ; fiche produit |
| La sélection du cas, par le code : la mesure qui compte est la perte à l'échéance, à la part de 5 % | Tous les calculs, y compris ceux de la part de 5 % ; la note et ses affirmations |
| La restitution, ouverte sur « ce qui a changé » | Les objections et leurs verdicts ; les versions précédentes, lisibles |

L'agent 2 n'est pas rappelé. Nouvelle tête de restitution [mesuré pour les nombres] : avec 5 % du titre demandé, l'écart sur la baisse en route va de 4 à 18 points ; sur la perte à l'échéance, la mesure qui compte désormais, le sens n'est pas établi (positif au taux sans risque, non distinguable de zéro sans rendement crédité). À cette part, ni le reste de la batterie ni la comparaison avec un actif aussi volatil n'ont été calculés pour l'exemple : dans le système, le balayage les aurait produits pour chaque part du domaine.

### Une correction : une révision ciblée

Robert se reprend : il s'est trompé sur deux lignes de son portefeuille. Dans l'interface, il corrige leurs poids : le fonds d'obligations XBB.TO passe de 40 % à 30 %, le fonds à très court terme ZST.TO de 10 % à 20 %. [illustratif] L'interface lui fait dire s'il s'est trompé, si sa situation a changé ou s'il explore ; il s'est trompé : c'est une correction. Aucun nombre n'a été calculé pour ce portefeuille corrigé ; ce qui suit est le comportement attendu.

| Périmé, puis refait | Reste en vigueur |
|---|---|
| Le fait « portefeuille de départ » ; les options, qui en dérivent toutes ; le plan d'analyse, rescellé ; les calculs et la table des variantes | La fiche des données ; les autres faits du profil |
| Les affirmations, les objections qui les visaient, les réserves, le bilan | Le dossier de preuves, le plan des méthodes, la fiche produit : l'agent 1 n'est pas rappelé |
| La restitution | La désignation des deux comparateurs : inchangée ici, parce que les lignes détenues sont les mêmes. Les tests de condition, si aucun ne lit le portefeuille : à vérifier contre la table de dépendances (document 09, B1) |

L'ancienne conclusion reste lisible dans l'historique, comme n'ayant jamais valu pour lui. S'il avait dit « ma situation a changé », la même révision aurait eu lieu, et l'ancienne conclusion aurait été montrée comme ayant valu jusqu'à cette date. S'il avait dit « et si c'était du QQQ ? », une branche aurait été ouverte, sans rien périmer. [attendu]

## Parcours 2 — Mateo, une diversification et une préférence

Ce parcours diffère sur ce qui compte : le type de décision (vérifier, et non ajouter), la mesure (concentration, et non baisse), l'horizon (hors de portée des données), la préférence (non financière), l'absence de titre vedette. **Le gabarit de cette décision n'est pas encore écrit** : d'après le document 02, elle ne serait donc pas « ouverte ». Ce parcours montre ce que ce gabarit devra contenir. [attendu]

### Vue d'ensemble

| Étape | Qui | Ce qui est créé | Différence avec le parcours 1 |
|---|---|---|---|
| 1 | La personne | Demande : « Mon portefeuille est-il bien diversifié ? Je voudrais aussi qu'il respecte mes préférences ESG, sans pétrole. » [illustratif] | Deux demandes en une ; une préférence |
| 2 | Agent 0 | Décision « vérifier une diversification », contrainte de préférence ; question : le portefeuille | Autre décision du catalogue, autres variables nécessaires |
| 3 | La personne | Portefeuille fictif : 25 % XIU.TO, 25 % SPY, 10 % ENB.TO, 10 % CNQ.TO, 10 % RY.TO, 20 % XBB.TO [illustratif] | — |
| 4 | Agent 0, puis la personne | Contradiction : « sans pétrole », et deux lignes que les données rangent dans le secteur de l'énergie (Enbridge, Canadian Natural Resources). Elle est montrée aussitôt et ne suspend pas l'étude. Le rapprochement entre « pétrole » et ce secteur est proposé par le produit, pas dit par Mateo ; les données ne distinguent pas les activités à l'intérieur du secteur. Mateo précise de lui-même : « les deux » | La clarification porte sur une préférence, pas sur un nombre ; aucune question ne suspend l'étude |
| 5 | Agent 1 | Plan des méthodes ; fiche produit des fonds | Aucune fiche qualifiée ne fonde la mesure de concentration |
| 6 | Agent 2 | Options ; calculs de concentration ; conclusion | Comparaison de mesures de risque, sans seuil de perte |
| 7 | Batterie fixe, puis contradicteur | Objections | Une convention de fréquence, et non une hypothèse de rendement |
| 8 | Agent 3 | Restitution ; l'abstention de l'agent 1 sur le contenu des fonds y est rendue | Le bloc « ce qu'on ne peut pas dire » est central |
| 9 | La personne | Correction : « seulement Canadian Natural Resources » | Révision d'une option, pas d'un nombre |

### Ce que chaque rôle établit

**Agent 0.** Le profil de risque « modéré » et l'horizon « huit à douze ans » sont des faits de l'énoncé ; la table des horizons borne aussitôt l'étude : aucune trajectoire. La préférence est recueillie dans les mots de la personne. L'agent 0 ne classe aucun titre lui-même : le secteur vient des données, et le choix des lignes vient de la personne. La fiche dit ce qui est vérifiable (le secteur des lignes détenues en direct) et ce qui ne l'est pas (ce que contiennent les fonds). [illustratif]

**Agent 1.** *Une preuve manquante, deux fois.* Le jeu de données décrit un fonds comme filtré selon des critères ESG ; il ne donne ni ces critères ni la composition du fonds, pas plus que celle du fonds canadien large. Réponse : « sans preuve » sur le respect de la préférence par les fonds. Il peut chercher le document de l'émetteur [attendu] : ce qu'il rapporterait serait une preuve candidate, qui peut ajouter une réserve (« le fonds large détient des sociétés du secteur exclu »), jamais établir que le portefeuille respecte la préférence. Par ailleurs, aucune fiche de la bibliothèque ne fonde la mesure de concentration employée ici : la ligne du plan porte la réserve « méthode non qualifiée par la littérature lue », et une lacune est consignée [attendu]. Les corrélations dépendent de la convention (R09, X2) : la batterie les calcule sous deux fréquences.

**Agent 2.** *Une comparaison calculée* [mesuré, `parcours_contraste.py`].

| Option | Volatilité annualisée | Lignes effectives en risque | Écart de volatilité avec « ne rien changer » | Écart de lignes effectives |
|---|---|---|---|---|
| Ne rien changer | 9,91 % | 4,59 | — | — |
| Sans les deux lignes du secteur de l'énergie | 9,66 % | 2,96 | −0,24 point (−0,78 à +0,38) | −1,63 (−1,73 à −1,47) |
| Fonds filtré à la place du fonds américain large | 10,04 % | 4,50 | +0,14 point (+0,08 à +0,19) | −0,09 (−0,15 à −0,05) |

Intervalles à 90 %, à la longueur de bloc de treize semaines. L'écart de lignes effectives de la deuxième option reste au-dessous de zéro à quatre longueurs de bloc et sous deux fréquences : de −1,73 à −1,43 en rendements hebdomadaires, de −1,58 à −1,29 en rendements quotidiens. [mesuré]

*Une conclusion correctement délimitée* [illustratif pour le texte].

| Partie | N° | Affirmation | Type |
|---|---|---|---|
| 1. Ce qui tient | M1 | Le portefeuille de départ compte six lignes, et 4,6 lignes effectives en risque (4,3 en rendements quotidiens). Le premier contributeur, le fonds canadien large, porte 29 % du risque. Les deux lignes du secteur de l'énergie pèsent 20 % du portefeuille et portent 29 % du risque (26 % en rendements quotidiens) | 6 |
| | M2 | Écarter ces deux lignes concentre le risque : les lignes effectives passent de 4,6 à 3,0, et le premier contributeur passe de 29 % à 42 % du risque. Le sens est établi, sous les deux fréquences et à chaque longueur de bloc essayée | 4 |
| | M3 | Le fonds filtré se comporte presque comme le fonds large (corrélation de 0,99 sous les deux fréquences), avec une volatilité supérieure : de 1,2 à 1,8 point en rendements hebdomadaires, de 0,9 à 1,9 en rendements quotidiens, à chaque longueur de bloc essayée | 4 |
| | M4 | Après cette exclusion, aucune ligne détenue en direct n'appartient au secteur de l'énergie | 1 |
| 4. Ce qu'aucun calcul ne donne | M5 | La baisse de volatilité qui accompagne l'exclusion ne se distingue pas de zéro | 7 |
| | M6 | Ce que contiennent les fonds, et donc si le portefeuille est « sans pétrole » : sans preuve | 7 |
| | M7 | Ce que deviendrait ce portefeuille sur huit à douze ans : non étudié | 7 |

Aucune affirmation ne dit que le portefeuille est, ou n'est pas, « bien diversifié » : M1 et M2 donnent les mesures, la personne juge. État de l'étude : menée à terme ; couverture partielle ; sans condition.

**Batterie fixe et contradicteur.** La batterie pose l'objection de convention : « la concentration tient-elle à la fréquence des rendements ? ». Résultat [mesuré] : 4,28 lignes effectives au départ, 2,83 sans les deux lignes, en rendements quotidiens. Verdict [attendu] : tient ; les deux valeurs sont données. Le contradicteur vise M1, qui décrit « ne rien changer », par un test du catalogue [attendu, non calculé], et ajoute un avis non testable : le fonds canadien large contient vraisemblablement des sociétés du secteur écarté, ce qu'aucune donnée ne permet de vérifier ; l'avis est joint à M6. [attendu]

**Agent 3.** La restitution ouvre sur la concentration, puis sur ce que la préférence coûte et ne coûte pas, puis sur un bloc « ce que nous ne pouvons pas dire » de même rang : le contenu des fonds, les critères du fonds filtré, l'horizon. Aucune phrase ne dit que le portefeuille respecte la préférence, et aucune option n'est dite « ESG » : elles se nomment « sans les deux lignes du secteur de l'énergie » et « avec le fonds que son émetteur dit filtré ». [attendu]

**Révision ciblée.** Mateo corrige : « seulement Canadian Natural Resources, je garde Enbridge ». Rouvert : la contrainte, l'option qui en découle, ses calculs, les affirmations M2, M4 et M5, les objections qui les visaient, la restitution. Conservé : la fiche des données, le dossier de preuves, les calculs de « ne rien changer » et du fonds filtré. L'option nouvelle est calculée à ce moment [mesuré] : volatilité de 9,51 %, 3,63 lignes effectives ; l'écart de lignes effectives va de −1,04 à −0,85 en rendements hebdomadaires et de −0,96 à −0,85 en rendements quotidiens, à chaque longueur de bloc essayée.

## Ce que les deux parcours éprouvent

| Exigence | Parcours 1 | Parcours 2 |
|---|---|---|
| Clarification utile | Le portefeuille, seule variable nécessaire | Le portefeuille ; puis une contradiction montrée, que la personne lève d'elle-même |
| Preuve manquante ou contradictoire | Sources opposées sur la méthode ; rien sur les perspectives du titre | Rien sur le contenu des fonds ; aucune fiche pour la mesure employée |
| Comparaison calculée | Écarts de parts de trajectoires, avec intervalles | Écarts de volatilité et de concentration, avec intervalles |
| Objection examinée | Année retirée ; valorisation quotidienne ; calibration ; ensemble de l'univers | Fréquence des rendements ; un avis non testable |
| Conclusion délimitée | Un sens établi, un sens non établi, un rendement d'équilibre | Un état mesuré, un sens établi, un effet non distinguable, deux abstentions |
| Révision ciblée | Deux précisions sans recalcul, puis un portefeuille corrigé | Une préférence corrigée |
| Limite connue dès la qualification | Horizon de cinq ans : étude bornée à trois | Horizon de huit à douze ans : aucune trajectoire |
| Ce dont le contrat doit pouvoir se passer | — | D'un titre vedette ; d'un seuil de perte |

Les mêmes contrats doivent servir les deux parcours ; seuls changeraient le gabarit de la décision, les variables nécessaires, les formulations autorisées et les types d'objection. [attendu : c'est le critère G1 du document 09, et le second gabarit reste à écrire]
