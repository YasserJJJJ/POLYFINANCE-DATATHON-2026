# R09 — Expériences discriminantes sur les méthodes (15 novembre 2026)

Petites expériences menées pendant la recherche sur les processus professionnels, pour vérifier une méthode avant de la recommander. Elles sont **hors produit** : elles lisent les données par la bibliothèque du projet, n'écrivent rien dans le produit et ne changent aucun comportement.

Chaque critère a été écrit dans l'en-tête du script **avant** l'exécution, pour que l'expérience puisse échouer. Les vérifications ajoutées après lecture des premiers résultats (X3 bis, X4 bis, X5 bis, X7) et le multivers repris de la recherche sont signalés comme tels : ils n'ont pas de critère écrit d'avance.

| Reproduire | Commande |
|---|---|
| Méthodes de l'agent 2 (aucun service appelé, graine 2026) | `uv run --with arch --with scikit-learn python research/experiences/methodes_analyse.py` |
| Qualification par un modèle (40 appels Bedrock) | `uv run python research/experiences/modele_qualification_et_citations.py m1` |
| Citations mot pour mot (5 appels Bedrock) | `uv run python research/experiences/modele_qualification_et_citations.py m2 TEXTE DÉBUT FIN` |

Sorties conservées dans `research/experiences/sorties/` (texte des résultats, réponses brutes des modèles avec les identifiants de requête AWS). Les bibliothèques `arch` 9.0.0 et `scikit-learn` 1.9.1 sont chargées à la volée, sans modifier `pyproject.toml`.

Cas étudié : portefeuille fictif de Robert (`config/scenarios.toml` : 40 % XBB.TO, 10 % ZST.TO, 30 % XIU.TO, 20 % SPY), ajout de 10 % de Tesla ou de 10 % de QQQ ; 261 semaines, du 19 novembre 2021 au 12 novembre 2026, en dollars canadiens.

## Vue d'ensemble

| | Question | Critère écrit d'avance | Résultat | Ce que cela décide |
|---|---|---|---|---|
| X1 | La longueur des blocs du rééchantillonnage change-t-elle la conclusion ? | Écart de plus de 5 points entre la longueur automatique et 13 semaines | **Non déclenché** : 3,6 points au plus | Un résultat par longueur de bloc suffit entre 1,5 et 13 semaines ; mais la règle automatique ne tranche pas seule (voir détail) |
| X2 | La formule d'annualisation du notebook d'introduction est-elle utilisable ? | Écart de plus de 2 points par an pour un actif ; corrélations décalées de plus de 0,10 pour une paire sur dix | **Déclenché deux fois** : 18 actifs sur 31 ; 28 % des paires | Formule écartée de toute restitution ; la convention de corrélation se déclare dans le dossier |
| X3 | Le rendement moyen est-il estimable ? Le risque l'est-il mieux ? | L'intervalle de l'écart de rendement contient zéro ; passer au quotidien réduit d'un tiers l'erreur sur la volatilité | **Première partie confirmée, seconde manquée** | Aucun écart de rendement historique ne fonde une conclusion ; l'argument « plus d'observations, donc risque mieux connu » ne tient pas sur nos données |
| X4 | Compare-t-on des options par niveaux ou par écarts ? | L'écart apparié exclut zéro alors que les niveaux se chevauchent | **Déclenché** | L'agent 2 compare les options sur les mêmes trajectoires |
| X4 bis | La « part maximale » affichée par le produit est-elle déterminée par les données ? | Ajout après coup, sans critère | De « aucune part » à 25 % selon l'histoire tirée | Ce chiffre ne peut pas être présenté comme un seuil |
| X5 | Faut-il contracter la matrice de covariance ? | Portefeuilles donnés : moins de 0,3 point de volatilité et de 2 points de part de risque ; optimisation : l'échantillon fait pire hors échantillon | **Contredit pour la méthode courante, confirmé après correction** | La contraction vers l'identité déforme notre univers ; contracter les corrélations, et seulement si un agent optimise |
| X6 | Les parts de trajectoires valent-elles des probabilités ? | Part des années réalisées dans la bande 5 %–95 % hors de [80 %, 97 %] | **Déclenché** : 4 mesures sur 8 hors de l'intervalle | Le produit parle de scénarios construits sur le passé, jamais de probabilités |
| X8 | Dans un monde stationnaire et connu, cinq ans suffisent-ils à estimer la part à trois ans ? | Moins de 90 % des échantillons à moins de 10 points de la vraie part, rendement imposé ; signe de l'écart correct dans 95 % des échantillons | **Niveau : déclenché** (21 % à 77 %) ; **écart : tenu** dans 11 configurations sur 12 | Les parts de trajectoires ne restituent pas un niveau ; elles servent à comparer des options |
| X7 | Le niveau de risque repose-t-il sur une seule année ? | Ajout après coup, sans critère | Sous la moyenne historique : de 2,6 % à 31,9 % selon l'année retirée. Retirer 2022 enlève 12 à 19 points sous les trois hypothèses de rendement ; ordre des options inchangé | Tout niveau porte une réserve ; seules les comparaisons entre options sont défendables |
| Multivers | Que reste-t-il quand on fait varier tous les choix d'analyse à la fois ? | Calcul de la recherche sur la confrontation, réexécuté | Sur 486 variantes qui font aussi varier la question (seuil, horizon) : niveau de 0,2 % à 90,5 %. À question fixée, 54 variantes : de 1,0 % à 67,4 %. Écart positif dans toutes | Le contradicteur éprouve d'abord l'hypothèse de rendement et la sous-période ; la longueur de bloc pèse dix fois moins |
| Écart et niveau | À question fixée, l'écart est-il établi, et est-il propre à Tesla ? | Ajout après les rapports des vérificateurs, sans critère | Signe de l'écart positif dans 98,5 à 100 % des histoires rééchantillonnées ; taille de 15 à 40 points ; un actif de volatilité voisine donne le même écart | Le produit conclut sur le sens d'un écart, donne sa taille avec un intervalle, et ne nomme le titre que si l'écart lui est propre |
| Rendement d'équilibre | Que faudrait-il que le titre rapporte pour que l'option se vaille ? | Ajout après la critique d'ensemble, sans critère | Tesla : 13 points par an de plus que le taux sans risque pour la perte à l'échéance (8 à 26) ; plus de 80 pour la baisse en route | L'étude dit autre chose que « le risque augmente » sans supposer de rendement |
| M1 | Un modèle seul qualifie-t-il correctement une demande ? | Quatre seuils (détection, fausses alertes, invention, donnée absente) | **Tous tenus** sur un jeu facile | L'extraction par modèle avec schéma est utilisable ; les cas difficiles restent à éprouver |
| M2 | Un modèle recopie-t-il ses citations à l'identique ? | 95 % de citations retrouvées ; abstention sur les questions sans réponse | **Tenus** : 145 sur 145 ; 20 sur 20 | La citation tapée puis contrôlée par le code est viable ; le contrôle ne dit pas si la citation soutient l'affirmation |

## X1 — Longueur de bloc du rééchantillonnage stationnaire

Méthode : règle automatique de Politis et White (2004), corrigée par Patton, Politis et White (2009), telle qu'implantée dans `arch.bootstrap.optimal_block_length`.

- Longueur estimée sur les rendements du portefeuille : 1,1 à 1,5 semaine. Sur leurs carrés : 0,3 à 1,6. Sur leurs valeurs absolues : 15,6 à 15,8 semaines.
- Lecture : les rendements ne se suivent pas d'une semaine à l'autre, mais l'agitation persiste (les semaines agitées se suivent). La règle automatique donne donc deux réponses très différentes selon ce qu'on lui demande de préserver ; elle est conçue pour l'estimation d'une moyenne, pas pour une pire baisse sur trois ans.
- Part des trajectoires de 3 ans dont la pire baisse franchit 15 %, avec les moyennes historiques : bloc de 1,5 semaine : 4,1 % (actuel), 21,3 % (10 % Tesla), 7,1 % (10 % QQQ) ; bloc de 13 semaines : 5,6 %, 20,9 %, 10,7 % ; bloc de 52 semaines : 4,5 %, 25,6 %, 8,8 %.
- Sans rendement moyen crédité : bloc de 1,5 : 34,8 %, 63,9 %, 44,2 % ; bloc de 13 : 35,4 %, 60,3 %, 43,9 % ; bloc de 52 : 42,8 %, 54,8 %, 47,2 %.
- Plus grand déplacement entre 1,5 et 13 semaines : 3,6 points. Entre 1 et 52 semaines : jusqu'à 9,6 points, mais un bloc d'un an ne laisse que cinq blocs indépendants dans l'échantillon.

Verdict : critère non déclenché. Le choix manuel de 13 semaines du calcul exploratoire est proche de la longueur estimée sur les valeurs absolues. Recommandation : calculer à deux longueurs (celle des rendements et celle des valeurs absolues) et n'afficher une fourchette que si elles divergent de plus de 5 points. L'ordre des options ne change à aucune longueur ; l'hypothèse de rendement déplace les résultats de 30 à 40 points, soit dix fois plus que la longueur de bloc.

## X2 — Les formules du notebook d'introduction

Le notebook fourni par les organisateurs calcule un « rendement annualisé » par `(1 + moyenne quotidienne) ^ jours − 1` et des corrélations sur des rendements quotidiens en devise de cotation.

- Rendement : pour Shopify, la formule affiche +22,9 % par an alors que le rendement composé réalisé est de −0,0 % ; Ethereum : +6,8 % contre −15,4 % ; Nvidia : +60,9 % contre +40,6 % ; Tesla : +22,8 % contre +2,9 % ; Bitcoin : +16,2 % contre +2,1 %. L'écart dépasse 2 points pour 18 actifs sur 31 (médiane +3,1 points) et vaut à peu près la moitié de la variance, comme la théorie le prévoit.
- Le classement « rendement sur risque » du notebook change de rang pour 21 actifs sur 31 (jusqu'à 8 rangs) quand on utilise le rendement composé.
- Corrélations : entre la convention du notebook et la convention du produit (hebdomadaire, dollars canadiens), l'écart dépasse 0,10 pour 28,0 % des 465 paires et 0,20 pour 1,9 %. Exemples : Bitcoin et SPY, +0,43 contre +0,23 ; SPY et AGG, +0,22 contre +0,09 ; or et XIU.TO, +0,33 contre +0,17.

Verdict : les deux critères sont déclenchés. La formule du notebook dirait à un lecteur que Tesla « a rapporté 22,8 % par an » quand un achat au début de la fenêtre a rapporté 2,9 % par an. Elle reste correcte comme espérance par période, pas comme rendement obtenu. La corrélation n'a pas une valeur unique : fréquence et devise doivent figurer dans le dossier, et une conclusion de diversification doit tenir sous les deux conventions.

## X3 — Rendement moyen et volatilité

| Actif | Rendement moyen annuel (hebdo) | Volatilité (hebdo) | Rendement moyen annuel (quotidien) | Volatilité (quotidien) |
|---|---|---|---|---|
| TSLA | +20,5 % ± 24,9 | 55,7 % ± 3,2 | +22,7 % ± 26,0 | 58,9 % ± 1,9 |
| SPY | +14,6 % ± 6,2 | 14,9 % ± 1,0 | +15,0 % ± 5,8 | 16,7 % ± 1,5 |
| XIU.TO | +13,5 % ± 5,6 | 12,5 % ± 0,7 | +13,7 % ± 5,0 | 13,1 % ± 0,7 |
| XBB.TO | +0,9 % ± 2,8 | 6,6 % ± 0,4 | +0,9 % ± 2,8 | 6,6 % ± 0,3 |

(Erreurs types par rééchantillonnage stationnaire, 5 000 tirages ; 261 semaines ou 1 254 jours.)

- Écart de rendement moyen entre Tesla et le portefeuille actuel : +12,8 points par an, intervalle à 90 % de −26,8 à +51,7 points. Il contient zéro.
- Pour distinguer une prime de 5 points par an à deux erreurs types, il faudrait 453 ans d'historique.
- Passer au quotidien ne réduit pas l'erreur sur le rendement moyen (confirmé pour les quatre actifs). Il ne réduit l'erreur sur la volatilité d'un tiers que pour Tesla (3,2 à 1,9). Avec un bloc commun en temps calendaire (vérification ajoutée après coup : 13 semaines et 63 jours), il ne la réduit d'un tiers pour aucun actif, et l'augmente pour SPY (1,3 à 1,7).

Verdict : première partie confirmée, seconde manquée. La volatilité est connue à moins d'un dixième de sa valeur près (erreur type de 6 à 9 % de la valeur avec le bloc commun) ; le rendement moyen à 3 à 25 points près : pour Tesla et pour XBB.TO, l'erreur type dépasse la valeur estimée. Mais l'argument classique « la variance s'estime mieux quand on multiplie les observations » ne se vérifie pas ici : comme l'agitation persiste, ce sont les cinq années, et non le nombre d'observations, qui limitent la précision. La volatilité dépend aussi de la fréquence (SPY : 14,9 % en hebdomadaire, 16,7 % en quotidien).

Erreur corrigée en cours de route : une première version calculait les rendements quotidiens sans retirer d'abord les jours fériés, ce qui perdait le rendement du lendemain (somme des rendements quotidiens de XBB.TO : 0,145 au lieu de 0,046). Le contrôle qui l'a révélée, comparer la somme des rendements quotidiens à celle des rendements hebdomadaires, est repris dans la fiche de l'agent 2.

## X4 — Niveaux contre écarts appariés

5 000 histoires rééchantillonnées de cinq ans, les mêmes semaines pour les deux options. Intervalles à 90 %.

| Mesure | Actuel | 10 % Tesla | Écart apparié |
|---|---|---|---|
| Perte moyenne des 5 % pires semaines | −2,38 % à −1,66 % | −3,01 % à −2,33 % | −0,87 à −0,46 point |
| Volatilité annualisée | 6,67 % à 7,92 % | 9,39 % à 10,97 % | +2,38 à +3,43 points |
| Pire baisse sur 5 ans | −16,1 % à −5,4 % | −23,6 % à −8,0 % | −10,4 à −0,2 point |

Les niveaux se chevauchent pour deux mesures sur trois, alors que l'écart exclut zéro pour les trois. Tesla à 10 % est plus défavorable dans 100 %, 100 % et 96,1 % des tirages.

Verdict : critère déclenché. Le niveau d'une pire baisse est très mal déterminé par cinq ans (de −5 % à −16 % pour le portefeuille actuel) ; l'écart entre deux options l'est beaucoup mieux. L'agent 2 doit comparer par écarts sur les mêmes trajectoires et restituer l'incertitude du niveau.

### X4 bis — La « part maximale de Tesla sous le seuil de 15 % » (ajout après coup)

Le produit affiche aujourd'hui une part maximale de 9 %, lue sur l'unique histoire observée. Sur 2 000 histoires rééchantillonnées (bloc de 13 semaines), cette part vaut : aucune part admissible dans 10,3 % des cas (le portefeuille actuel franchit lui-même le seuil) ; 7 % au premier quartile ; 12 % en médiane ; 17 % au troisième quartile ; 25 % au 95e centile. Avec un bloc de 1,5 semaine : mêmes quartiles, 6,5 % de cas sans part admissible.

Lecture : « 9 % » est un point dans une plage qui va de zéro à un quart du portefeuille. Le chiffre ne peut pas être présenté comme un seuil ; il doit l'être comme une lecture d'une seule histoire, accompagnée de cette plage.

## X5 — Contraction de la covariance

- Intensité de contraction de Ledoit et Wolf (cible : identité) sur les 31 actifs : 0,039 ; le conditionnement passe de 69 023 à 278.
- Portefeuilles donnés par la demande : la volatilité prévue passe de 7,31 % à 7,86 % pour le portefeuille actuel de Robert (0,55 point) et une part de risque se déplace de 5,5 points. Le critère d'innocuité (0,3 point, 2 points) n'est pas tenu.
- Cause : la cible ajoute à chaque actif une fraction de la variance moyenne de l'univers, dominée par les cryptoactifs. Elle gonfle la variance des obligations, cent fois plus faible.
- Variance minimale hors échantillon sur les 31 actifs : la covariance d'échantillon fait mieux (0,41 % de volatilité réalisée contre 4,39 %), parce que l'univers contient un quasi-placement de trésorerie (ZST.TO) que la contraction pénalise. Le critère « la contraction est obligatoire » n'est donc pas déclenché sur l'univers complet.
- Vérifications ajoutées après coup. Contraction des corrélations, variances conservées : la volatilité prévue bouge de 0,11 point (Robert actuel), 0,17 point (10 % Tesla) et 0,71 point (portefeuille d'Amira, soit 2,3 % de sa valeur) ; les parts de risque de 0,4 point au plus. Sur les 20 actions seules, variance minimale hors échantillon : 10,89 % (échantillon), 9,46 % (Ledoit-Wolf), 9,34 % (corrélations contractées), 11,77 % (poids égaux) avec 52 semaines d'estimation ; 8,99 %, 8,36 %, 8,30 %, 10,87 % avec 104 semaines. L'échantillon fait pire dans 7 fenêtres sur 8, puis 5 sur 6.

Verdict : appliquer `sklearn.covariance.LedoitWolf` tel quel à un univers qui mêle obligations et cryptoactifs est une erreur. Pour comparer des portefeuilles dont les poids viennent de la demande, la contraction des corrélations change peu de chose et n'est pas nécessaire. Dès qu'un agent choisit des poids par optimisation parmi des actifs risqués, elle devient nécessaire.

## X6 — Le rééchantillonnage vaut-il prévision ?

À chaque date, 2 000 scénarios d'un an tirés du seul passé connu à cette date, comparés à l'année réellement suivie.

| Passé minimal | Option | Dates de départ | Pire baisse réalisée dans la bande 5 %–95 % | Rang médian de la pire baisse | Valeur finale dans la bande | Rang médian de la valeur finale |
|---|---|---|---|---|---|---|
| 104 semaines | Actuel | 106 | 80 % | 0,74 | 84 % | 0,86 |
| 104 semaines | 10 % Tesla | 106 | 84 % | 0,86 | 63 % | 0,90 |
| 156 semaines | Actuel | 54 | 100 % | 0,75 | 96 % | 0,79 |
| 156 semaines | 10 % Tesla | 54 | 100 % | 0,87 | 100 % | 0,74 |

Un outil bien calibré donnerait une part proche de 90 % et un rang médian proche de 0,50. Quatre parts sur huit sortent de l'intervalle fixé d'avance, et tous les rangs médians sont entre 0,74 et 0,90 : les années réalisées ont été systématiquement plus favorables que les scénarios. Jamais une année réalisée n'a été pire que 95 % des scénarios.

Verdict : critère déclenché. Les scénarios tirés d'un passé qui contenait la baisse de 2022 étaient trop sombres pour les années qui ont suivi ; l'inverse se produirait après des années calmes. Le test est faible (deux à trois années sans chevauchement), mais le biais est de même sens partout. Le produit ne peut donc pas écrire « probabilité » : il écrit « part des scénarios construits à partir des cinq années observées », et montre comment cette part change avec l'hypothèse de rendement.

## X8 — Calibration sur des processus connus

Question posée par la recherche sur l'analyse : la méthode se trompe-t-elle même quand le monde est stationnaire ? Script `research/experiences/calibration_reechantillonnage.py`, sans données réelles. Trois processus de volatilité annuelle voisine de 10 % : tirages indépendants, volatilité persistante (GARCH), deux régimes (calme et crise, durées moyennes de 150 et 26 semaines). Pour chacun, 400 échantillons de 261 semaines ; sur chaque échantillon, la part des trajectoires de 3 ans franchissant 15 % est estimée par rééchantillonnage (bloc de 13 semaines) et comparée à la vraie part du processus.

| Processus | Rendement moyen | Vraie part à 3 ans | Estimations, rendement imposé à sa vraie valeur (5e au 95e centile) | À moins de 10 points | Estimations avec la moyenne de l'échantillon | À moins de 10 points |
|---|---|---|---|---|---|---|
| Tirages indépendants | nul | 64,4 % | 47,3 % à 75,3 % | 77 % | 18,8 % à 93,7 % | 29 % |
| Volatilité persistante | nul | 61,8 % | 37,5 % à 80,8 % | 54 % | 17,5 % à 93,4 % | 31 % |
| Deux régimes | nul | 52,8 % | 29,0 % à 85,6 % | 39 % | 2,8 % à 95,8 % | 17 % |
| Tirages indépendants | 0,17 % par semaine | 22,2 % | 5,2 % à 38,6 % | 56 % | 1,7 % à 60,0 % | 37 % |
| Volatilité persistante | 0,17 % par semaine | 23,7 % | 2,1 % à 51,8 % | 33 % | 0,5 % à 61,7 % | 26 % |
| Deux régimes | 0,17 % par semaine | 34,7 % | 0,4 % à 74,9 % | 21 % | 0,0 % à 86,1 % | 17 % |

À un an, la méthode fait mieux quand le rendement est imposé (de 39 % à 99 % des échantillons à moins de 10 points selon le processus), sans atteindre partout le seuil.

Écart entre deux portefeuilles soumis aux mêmes chocs, l'un moins volatil que l'autre : le signe estimé est correct dans 99 % à 100 % des échantillons à 3 ans, et dans 91 % à 100 % à un an (91 % pour les deux régimes avec rendement positif, où beaucoup d'échantillons ne contiennent aucune crise).

Verdict : critère déclenché pour le niveau, tenu pour l'écart dans 11 configurations sur 12. Même dans un monde qui ne change pas, cinq ans ne fixent pas la part des trajectoires de trois ans qui franchissent un seuil : avec un rendement positif, l'estimation va de quelques pour cent à plus du tiers, voire aux trois quarts, selon l'échantillon tiré. Le rendement moyen en est la première cause, la rareté des crises la seconde. La comparaison de deux options sur les mêmes trajectoires reste fiable. Conséquence : une part de trajectoires se restitue comme un écart entre options, jamais comme un niveau de risque.

## X7 — Dépendance à une sous-période (ajout après coup)

Constat avancé par la recherche sur la confrontation, reproduit ici par un calcul séparé. Part des trajectoires de 3 ans franchissant 15 %, bloc de 13 semaines, quand on retire une année de l'échantillon :

| Échantillon | Actuel | 10 % Tesla | 10 % QQQ |
|---|---|---|---|
| Complet (261 semaines) | 5,6 % | 20,9 % | 10,7 % |
| Sans la première année (novembre 2021 à novembre 2022) | 0,0 % | 2,6 % | 0,0 % |
| Sans la deuxième | 6,8 % | 22,8 % | 13,6 % |
| Sans la troisième | 10,5 % | 31,9 % | 17,5 % |
| Sans la quatrième | 7,2 % | 22,2 % | 12,6 % |
| Sans la cinquième | 8,1 % | 27,1 % | 14,1 % |

Sans la première année, la pire baisse observée à 10 % de Tesla passe de −15,3 % à −10,0 %. Le niveau de risque affiché repose donc presque entièrement sur la baisse de 2022 ; l'ordre des trois options, lui, ne change dans aucune variante.

## Multivers exploratoire (calcul de la recherche sur la confrontation, relu et réexécuté)

Script : `research/experiences/multivers_exploratoire.py` ; résultats : `research/experiences/sorties/multivers_exploratoire.json`. 486 variantes : trois longueurs de bloc, trois hypothèses de rendement, trois seuils (12,5 %, 15 %, 17,5 %), trois horizons (2, 3 et 4 ans), six échantillons (complet, ou privé d'une année). 4 000 trajectoires par variante.

- Part des trajectoires franchissant le seuil avec 10 % de Tesla : de 0,2 % à 90,5 % (médiane 42,9 %).
- Écart entre « 10 % de Tesla » et « ne rien changer » : positif dans 100 % des variantes, supérieur à 2 points dans 97,7 %. Même constat entre Tesla et QQQ.
- Poids de chaque choix sur le niveau (étendue des médianes) : hypothèse de rendement 38,3 points ; seuil 31,7 ; année retirée 29,9 ; horizon 27,4 ; longueur de bloc 1,9.
- Bruit de simulation sur huit graines à 10 000 trajectoires : écart type de 0,5 point pour « 10 % de Tesla ».

Lecture : la conclusion comparative (« ajouter Tesla augmente le risque de franchir le seuil ») résiste à tous les choix d'analyse essayés. Aucun niveau ne résiste. Le registre des objections de l'exemple du contrat éprouvait déjà l'hypothèse de rendement, la valorisation quotidienne et le rééquilibrage ; il lui manquait le retrait d'une année, l'un des choix les plus influents.

### Deux reproches fondés des vérificateurs, et ce qu'ils changent

- Le multivers mêle la question et la méthode. Le seuil et l'horizon appartiennent à la demande de la personne ; l'hypothèse de rendement, la longueur de bloc et l'échantillon sont des choix d'analyse. L'étendue « 0,2 % à 90,5 % » additionne les deux et ne doit pas être citée comme une sensibilité aux choix d'analyse.
- Une part de variantes de même signe n'est pas une preuve statistique : les 486 variantes viennent des mêmes 261 semaines. La preuve que l'écart est positif vient d'ailleurs : du rééchantillonnage de l'histoire (ci-dessous, partie C) et de la calibration sur processus connus (X8).

## Écart et niveau à question fixée (ajout après les rapports des vérificateurs)

Script : `research/experiences/ecart_et_niveau.py`. Question fixée : part des trajectoires de 3 ans dont la pire baisse franchit 15 %. Hypothèses de rendement : moyennes historiques, taux sans risque (3,22 % par an), aucun rendement.

**A. Étendue selon les seuls choix d'analyse.** Sur 54 variantes (trois longueurs de bloc, trois hypothèses de rendement, échantillon complet ou privé d'une année) : niveau avec 10 % de Tesla de 1,0 % à 67,4 % ; écart avec « ne rien changer » de +1,0 à +34,4 points, positif dans les 54. Sans la moyenne historique, que le contrat écarte déjà (36 variantes) : niveau de 16,4 % à 67,4 %, écart de +14,7 à +34,4 points. Sur l'échantillon complet (9 variantes) : niveau de 20,6 % à 64,1 %, écart de +14,7 à +31,5 points.

**B. Retrait d'une année sous chaque hypothèse**, avec l'erreur type obtenue en retirant tour à tour chaque bloc annuel.

| Hypothèse de rendement | Niveau, échantillon complet | Niveau sans la première année | Erreur type du niveau | Écart, échantillon complet | Erreur type de l'écart |
|---|---|---|---|---|---|
| Moyennes historiques | 20,9 % | 2,6 % | 20,4 points | +15,3 points | 13,4 points |
| Taux sans risque | 44,8 % | 26,1 % | 19,3 points | +25,6 points | 6,2 points |
| Aucun rendement | 60,3 % | 48,0 % | 13,4 points | +24,9 points | 9,2 points |

Retirer la première année enlève 18,3, 18,7 et 12,3 points au niveau. Cinq blocs annuels sont peu pour ce calcul d'erreur type : il donne un ordre de grandeur.

**C. Intervalle d'échantillonnage** (400 histoires rééchantillonnées, 2 000 trajectoires chacune, intervalles à 90 %).

| Hypothèse de rendement | Niveau avec 10 % de Tesla | Écart avec « ne rien changer » | Histoires où l'écart est positif |
|---|---|---|---|
| Moyennes historiques | 0,6 % à 59,6 % | +0,6 à +38,9 points | 98,5 % |
| Taux sans risque | 22,5 % à 61,6 % | +16,2 à +42,3 points | 100 % |
| Aucun rendement | 43,9 % à 74,5 % | +17,3 à +40,4 points | 100 % |

**D. L'écart est-il propre à Tesla ?** On ajoute 10 % de chacun des 27 actifs absents du portefeuille. L'écart est positif pour 15 à 18 d'entre eux selon l'hypothèse. Tesla est au 4e ou au 5e rang (+25,2 points sans rendement crédité, +24,8 au taux sans risque, +14,7 sous moyennes historiques), derrière Ethereum, Shopify et Nvidia. Bitcoin, l'actif de volatilité la plus proche (51 % contre 56 %), donne +23,9, +27,4 et +27,5 points.

Lecture.

- **Le niveau n'est pas établi.** À hypothèse de rendement donnée, il est connu à 13 à 20 points près ; d'une hypothèse à l'autre, il va du simple au triple.
- **Le sens de l'écart est établi.** Ajouter 10 % de Tesla accroît la part des trajectoires qui franchissent le seuil dans toutes les variantes et dans 98,5 à 100 % des histoires rééchantillonnées.
- **La taille de l'écart est imprécise** : entre 15 et 40 points.
- **L'écart n'est pas propre à Tesla.** C'est celui d'un titre isolé très volatil : Bitcoin donne le même. Une conclusion qui nomme Tesla doit le dire.
- Conséquence pour les marges de verdict du contradicteur : une marge de 2 points mesure la reproductibilité du calcul (bruit de 0,5 point entre graines), pas la solidité d'un niveau, dont l'incertitude est dix fois plus grande.

## Rendement d'équilibre (ajout après la critique d'ensemble, sans critère écrit d'avance)

Script : `research/experiences/rendement_d_equilibre.py`. La critique d'ensemble relève qu'une analyse qui ne crédite aucun rendement conclut toujours pour « ne rien changer ». Plutôt que de supposer un rendement, on calcule celui qu'il faudrait : de combien par an le titre ajouté doit-il battre le taux sans risque pour que « 10 % du titre » ne soit pas plus défavorable que « ne rien changer » ? Tous les autres actifs sont crédités du taux sans risque (3,22 % par an). Trajectoires de 3 ans, bloc de 13 semaines, 4 000 trajectoires ; intervalle sur 200 histoires rééchantillonnées.

Référence « ne rien changer » sous cette hypothèse : 24,2 % des trajectoires finissent sous la valeur de départ, 19,7 % franchissent 15 % de baisse en route (niveaux donnés pour situer le calcul, non établis).

| Option | Pour ne pas finir plus souvent sous la valeur de départ | Pour ne pas franchir plus souvent 15 % de baisse en route |
|---|---|---|
| 10 % de Tesla | 13 points par an (5e au 95e centile : 8 à 26) | Au-delà de 80 points par an (hors grille dans 75 % des histoires) |
| 10 % de QQQ | 5 points par an (3 à 7) | 34 points par an (14 à 42) |
| 10 % de Bitcoin | 18 points par an (8 à 25) | Au-delà de 80 points par an (hors grille dans 72 % des histoires) |

Lecture : le rendement n'est pas supposé, il devient un seuil à juger. « Pour que 10 % de Tesla ne rendent pas plus fréquente une perte à trois ans, il faudrait que Tesla rapporte environ 13 points par an de plus que le taux sans risque ; aucun rendement vraisemblable ne compense la baisse en cours de route. » La personne peut dire si elle y croit. Limites : une seule hypothèse de base, un intervalle large, et le même échantillon de cinq ans.

## M1 — Qualification d'une demande par un modèle seul

Huit demandes libres écrites pour l'expérience, cinq répétitions chacune, modèle `global.anthropic.claude-sonnet-5-5` par l'API Converse avec schéma imposé (40 appels, 49 315 jetons d'entrée, 34 116 de sortie).

- Contradictions plantées signalées : 20 sur 20 (seuil : 19).
- Fausses contradictions sur les deux demandes nettes : 0 sur 10 (seuil : 1).
- Champs remplis alors que la demande ne dit rien : 0 sur 80 (seuil : 2).
- Absence de données ESG citée parmi les inconnues : 5 sur 5.
- La question prioritaire porte sur le même sujet aux cinq répétitions pour chacune des huit demandes.
- Hors critère : 20 questions sur 40 en contiennent deux (« …, et quelle perte… ») ; longueur médiane de 177 caractères.

Verdict : critères tenus. Limites : huit demandes courtes, contradictions explicites, un seul tour, un seul modèle, rédigées par la personne qui a écrit le schéma. L'expérience montre que l'extraction avec schéma ne fabrique pas d'information sur des cas nets ; elle ne dit rien des contradictions implicites, des messages longs, ni de la qualité de la formalisation qui suit. La règle « une seule question à la fois » doit être contrôlée par le code.

## M2 — Citations mot pour mot

Texte : Instruction complémentaire 31-103CP, article 13.2 sur la connaissance du client (version anglaise, 22 336 caractères). Huit questions, dont deux sans réponse dans le texte ; deux exécutions de cinq répétitions.

- Citations retrouvées à l'identique dans le texte (espaces et guillemets normalisés) : 64 sur 64, puis 81 sur 81.
- Abstentions sur les questions sans réponse : 10 sur 10, deux fois.
- Un premier essai avec une limite de 4 000 jetons a produit une sortie tronquée, donc un JSON invalide : le motif d'arrêt doit être contrôlé avant toute lecture d'une sortie structurée.

Verdict : critères tenus. Le contrôle par le code garantit qu'une citation existe dans la source ; il ne garantit pas qu'elle soutient l'affirmation à laquelle elle est attachée. Ce second contrôle reste à concevoir (relecture par un autre rôle, ou échantillon vérifié à la main).

## Compléments de l'étape d'architecture (15 novembre, 16 h, sans critère écrit d'avance)

Calculs ajoutés aux scripts des deux parcours illustratifs après la revue de cohérence des documents d'architecture. Ce sont les nombres d'exemples, pas des expériences discriminantes : aucun critère n'a été écrit avant. Scripts : `research/experiences/dossier_illustratif.py` et `parcours_contraste.py` ; sorties dans `research/experiences/sorties/`. Les nombres déjà publiés par ces scripts se retrouvent à l'identique après l'ajout.

**Portefeuille de Robert, 10 % de Tesla, baisse de plus de 15 % en cours de route sur trois ans.**

- Écart avec « ne rien changer », intervalle à 90 %, selon la longueur de bloc, au taux sans risque puis sans rendement crédité : une semaine, +25,6 à +37,2 et +23,6 à +34,3 ; quatre semaines, +22,0 à +40,1 et +21,9 à +36,8 ; treize semaines, +16,4 à +41,4 et +18,4 à +41,5 ; vingt-six semaines, +11,4 à +43,2 et +14,0 à +43,2. L'écart est positif dans toutes les histoires rééchantillonnées, à chaque longueur.
- Écart entre 10 % de Tesla et 10 % de QQQ, le fonds le plus corrélé : +8,9 à +32,9 points au taux sans risque, +8,6 à +30,9 sans rendement crédité ; positif dans toutes les histoires. Calculé à la seule longueur de treize semaines.
- Pire baisse observée, sur les jours ouvrables communs : −15,3 % en valorisation hebdomadaire et −16,7 % en valorisation quotidienne avec 10 % de Tesla ; −12,3 % et −12,7 % sans rien changer. Le diagnostic du matin donnait −17,5 % en quotidien, par un autre script et une autre convention de jours : c'est −16,7 % qui a une sortie enregistrée.
- Comparateurs désignés par règle quand on retire tour à tour chaque année : le fonds le plus corrélé reste QQQ ; l'actif de volatilité la plus proche est Bitcoin, sauf sans la première année, où c'est Shopify.

**Portefeuille fictif de Mateo, lignes effectives en risque.** Écart avec « ne rien changer », intervalle à 90 %, à quatre longueurs de bloc : sans les deux lignes du secteur de l'énergie, de −1,73 à −1,43 en rendements hebdomadaires et de −1,58 à −1,29 en rendements quotidiens ; sans Canadian Natural Resources seulement, de −1,04 à −0,85 et de −0,96 à −0,85 ; avec le fonds filtré à la place du fonds large, de −0,15 à −0,05 et de −0,15 à −0,06. Négatif dans toutes les histoires, dans les trois cas.

## Ce que ces expériences ne disent pas

- Elles portent sur un portefeuille, deux ajouts et cinq années. Aucun résultat n'est une propriété générale des marchés.
- Les intervalles viennent du rééchantillonnage des mêmes cinq années : ils mesurent ce que ces années laissent incertain, pas ce qu'une autre période aurait montré.
- Les expériences avec modèle sont de petite taille et sans jeu de cas difficile ; elles écartent un échec grossier, elles ne mesurent pas une fiabilité.
- Aucune ne mesure la compréhension d'un lecteur, ni l'apport d'un rôle à la qualité du dossier.
