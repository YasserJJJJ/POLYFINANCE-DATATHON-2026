# Recherche financière — décisions, contradictions et portée

15 novembre 2026. Recherche et expériences isolées, sans modification du produit.
L'architecture Agent0 / Agent1 / Agent2 / Agent3 est conservée. Les références Uxxx
renvoient à l'inventaire commun ; les lectures approfondies et leur version sont
décrites dans `03_registre_sources.md` et `06_sources_primaires_et_nv.md`.
Collecter un fichier ne vaut pas le lire.

## D1. Quelle décision financière doit-on effectivement résoudre ?

Le comparateur actuel montre l'effet historique de poids imposés. Il ne résout
pas encore une décision où besoin de liquidités, horizon, limites de risque et
préférences changent l'ensemble admissible et les arbitrages. La première
extension substantielle est un **plan de financement des objectifs et une
comparaison de solutions admissibles**. Le choix du risque à minimiser vient
ensuite ; une allocation ne devient pas pertinente parce que son solveur converge.

Exemple Robert, strictement illustratif : capital 100 000 CAD, retrait de
30 000 CAD dans un an, plafond TSLA 10 %, contraintes de pertes dans des chocs
explicitement choisis. Agent0 doit préciser si le retrait est incontournable,
la disponibilité des actifs, si le capital est nominal ou réel, les autres
flux et les préférences entre coûts, risque et croissance. Agent2 peut alors :

1. vérifier budget, unités, échéances et admissibilité ;
2. calculer la réserve nécessaire sous les hypothèses choisies et ses alternatives
   (une réserve abstraite à rendement nul n'est pas un produit garanti) ;
3. chercher un ajustement de poids limitant la rotation, puis comparer parmi les
   solutions proches des optima de risque ou de coût ;
4. montrer ce qui change avec un retrait de 40 000 CAD, des coûts non nuls,
   une autre échéance ou un choc plus sévère ;
5. retourner à la qualification si aucun arbitrage n'a été exprimé entre
   plusieurs solutions non dominées.

Notre LP isolé retrouve les minima de rotation de 30 % et 40 % prouvés dans le
diagnostic, mais **d'autres poids que les solutions C/D**. Pour 30 % de réserve,
il trouve [réserve 30, XBB 20, ZST 20, XIU 20, TSLA 10] %, avec pertes de 10 000
et 7 900 CAD dans les deux chocs ; pour 40 %, [40, 10, 20, 20, 10] %, avec pertes
de 9 500 et 6 400 CAD. Tous atteignent la borne de rotation ≥ augmentation de
la réserve. La pluralité des optima est donc matérielle. Une règle explicite
de départage ou une présentation des alternatives est nécessaire.

La simulation de trajectoires avec retraits devra distinguer rendement pondéré
par le temps, rendement monétaire/IRR et richesse nette après flux. Un drawdown
calculé naïvement sur le compte après retrait confond une sortie voulue et une
perte de marché. Le seuil de perte dans deux scénarios terminaux ne borne pas
le drawdown de toutes les trajectoires.

Fondements : CFA 2026 U341 (cadrage professionnel traité par Agent1) ; Boyd &
Vandenberghe, chap. 4–5 (formulation, convexité et certificats) ; Chinneck U049
(infaisabilité) ; Das et al. U046/U047 (objectifs et programmation dynamique).
Les modèles probabilistes d'objectifs sont des candidats lorsque les hypothèses
de distribution et les flux sont qualifiés, pas une source de probabilités
futures objectives à extraire des seuls cinq ans.

## D2. Cinq ans rendent-ils toute optimisation inutile ?

**Non.** L'erreur type approximative d'une moyenne annualisée vaut σ/√Y sous
observations indépendantes et moments constants. Pour Y=5 : 8,944 points à
20 % de volatilité, 35,777 points à 80 %. Cela établit la faiblesse d'une
estimation naïve dans ce cadre ; ni l'inestimabilité absolue des moyennes ni
l'impossibilité de toutes décisions utiles. Dépendance, changements de régime,
information économique et a priori modifient le problème.

Le résumé publié de DeMiguel–Garlappi–Uppal (U001, RFS 2009) conditionne les
3 000 / 6 000 mois à des modèles et paramètres calibrés sur les actions
américaines. Interpoler ces deux chiffres pour conclure « 3 700 mois nécessaires
pour les 31 actifs du starter » n'est pas justifié. Notre accès aux PDF proposés
échoue : la page auteur retourne du HTML malgré HTTP 200, et le miroir universitaire
une 404. Nous n'avons donc pas reconstitué leurs démonstrations. Le résumé suffit
à rejeter le caractère universel que le dossier ajoute au résultat.

Kritzman–Page–Turkington (U002, résumé développé) et Kirby–Ostdiek (U003, résumé
éditeur) contestent précisément certaines configurations et entrées de ces
comparaisons ; ils ne prouvent pas que toute optimisation bat 1/N. Les coûts,
contraintes, univers et informations disponibles doivent être communs.

La variance minimale n'exige pas de moyenne attendue mais dépend de la covariance.
Ledoit–Wolf réduit l'erreur de covariance selon une perte statistique choisie.
La note UPF de juin 2003, ancêtre de *Honey* 2004, utilise une cible à
corrélation constante ; `sklearn.covariance.ledoit_wolf` utilise une identité
scalaire. Les appeler simplement « Ledoit–Wolf » masque une différence réelle.
Ni contraction, ni risque pair, ni hiérarchie ne suppriment le choix de l'univers,
de la fenêtre, des contraintes et de la fonction de perte.

**Expérience locale préspécifiée** : huit actifs CAD, 252 rendements
d'entraînement puis 63 hors échantillon, plafonds uniformes 35 %. Sur les blocs
disponibles, volatilités annualisées √252 : 1/N 12,4767 %, GMV empirique 4,4755 %,
GMV avec contraction identité 4,4867 %. Ce dernier a une sensibilité moyenne L1
des poids plus faible sous notre bootstrap en blocs : 0,05514 contre 0,06219.
Ce protocole montre faisabilité et une stabilisation modeste, pas une domination
statistique. Les portefeuilles de risque sont largement obligataires ; le
risque plus bas n'atteste pas qu'ils satisfont un objectif de croissance.

**Décision proposée** : garder ajustement minimal, 1/N admissible et GMV contraint
comme comparaisons utiles si le problème posé les justifie ; comparer les
estimateurs. Ne pas fixer cinq ou sept formulations comme plafond arbitraire.
Une nouvelle méthode entre lorsque son hypothèse ou sa garantie répond à une
incertitude susceptible de changer la décision.

## D3. Que garantissent CVaR, robustesse et IIS ?

Pour des scénarios de perte linéaire ℓs(w), la formulation
`min α + Σ ps us/(1−β)`, `us ≥ ℓs(w)−α`, `us ≥ 0`, est un LP si les contraintes
sur w sont linéaires. Elle optimise le risque dans les scénarios et probabilités
spécifiés. Elle ne garantit ni rendement, ni queue future, ni perte maximale.
La CVaR à 95 % n'est pas le drawdown maximal et une CVaR à une journée ne s'étend
pas mécaniquement à un horizon de quatre ans.

Rockafellar–Uryasev 2000 (source primaire récupérée via la bibliographie de
l'auteur U345) pose explicitement une distribution continue pour simplifier
ses théorèmes. Son approximation par scénarios motive le LP ; pour une
distribution empirique discrète, prendre « moyenne des pertes ≥ VaR » sans
fractionner la masse frontière peut être faux. Notre contrôle indépendant donne
7,3333 % pour la pire moitié des pertes équiprobables −1 %, 2 %, 10 %, identique
au LP. Une implémentation de production doit valider quantiles, égalités,
pondérations, unités et conventions de signe.

La robustesse distributionnelle de Mohajerin Esfahani–Kuhn (U152, arXiv v3 2017,
publié en 2018) considère une boule de Wasserstein. Les garanties finies
dépendent notamment d'un échantillonnage sous une distribution commune,
d'hypothèses de queue, du rayon et de la dimension. Le théorème 3.5 ne donne pas
une assurance hors régime pour des rendements crypto dépendants. Un rayon
choisi pour produire une belle allocation ne porte pas la garantie du théorème.
Candidate utile si l'ambiguïté de distribution est définie et sa calibration
testable ; elle reste une extension, pas une obligation.

Un **IIS** est un sous-ensemble infaisable qui devient faisable lorsqu'on enlève
n'importe lequel de ses membres. Il n'est pas forcément de cardinalité minimale,
il peut ne pas être unique, et il ne désigne pas le meilleur assouplissement.
Les bornes des variables font partie du diagnostic. Les états *infaisable*,
*non borné*, *limite numérique/temps* sont distincts. Chinneck, diapositives
4, 7–9 et 15, sépare IIS, ensemble faisable maximal et réparation.

Test HiGHS 1.16.0 : le `getIis()` léger par défaut peut renvoyer `kOk`,
`valid_=True` et un ensemble vide sur un problème infaisable élémentaire.
`iis_strategy=4` fournit ici les deux lignes conflictuelles et un statut
irréductible ; la suppression de chaque ligne et une preuve analytique le
confirment. Agent2 doit inspecter ces états et vérifier son certificat, jamais
transformer un booléen de l'API en explication financière.

Une relaxation doit garder les contraintes incontournables intactes et porter
une unité/coût/autorisation. Remplacer une limite exprimée par l'utilisateur
par une pénalité inventée n'est pas une résolution.

## D4. Quel test de performance est défendable ?

Bailey–López de Prado, version auteur du 31 juillet 2014, distingue maximum
attendu sous essais multiples, seuil ajusté, moments des rendements et longueur
de l'historique (pp. 7–9, annexe 3). L'affirmation du dossier « 0,85 donc aucun
backtest long seulement ne peut convaincre » n'en découle pas.

Notre simulation de **l'approximation explicite** de vingt Sharpe indépendants
N(0,1/5) produit un maximum moyen 0,8361, mais un quantile 95 % de 1,2513
(formule exacte 1,251845). Avec corrélation 0,8, la moyenne devient 0,3753.
Ce n'est pas une reproduction complète du DSR : volatilité connue,
normalité et structure de dépendance sont imposées. Elle réfute la confusion
entre moyenne d'un maximum et valeur critique universelle.

Un test honnête consigne tous les candidats/paramètres essayés, réserve les
fenêtres de validation, déclare les coûts et compare des portefeuilles réalisables
sous les mêmes contraintes. Le survivant 2026 et les données ajustées a posteriori
ne deviennent pas un univers historiquement disponible grâce à une séparation
train/test. Les backtests d'agents rencontrent aussi la contamination temporelle
des textes et modèles ; c'est distinct des erreurs du moteur numérique.

La validation doit comporter : équations et références indépendantes,
résidus/conditions d'optimalité, sensibilité, tests hors temps adaptés à
l'usage, confrontation au besoin utilisateur et revue des limites. La guidance
américaine **SR 26-2 du 17 avril 2026** remplace ici la référence automatique à
SR 11-7 : ses principes concernent les modèles quantitatifs traditionnels,
avec proportionnalité. Elle exclut explicitement l'IA générative/agentique
(p. 3, note 3). Son utilisation pour organiser les agents est une analogie
de gouvernance, pas une conformité réglementaire revendiquée.

## D5. Données admissibles : dates, devise, droits et ESG

La date économique, la date de publication, la révision et l'instant auquel
une observation était accessible sont quatre informations différentes.
Un délai de publication appliqué à une série révisée ne restitue pas le
millésime initial. FRED/ALFRED distingue la période réelle par
`realtime_start`/`realtime_end` ; les pages et extractions de Philadelphie U276
confirment le concept de vintages. Sans vintages, une analyse macro historique
doit être rétrospective et déclarée telle, ou exclue d'un test prédictif.

Les taux BoC sont indicatifs, moyennés sur une période de la journée ; ce ne sont
ni des taux d'exécution ni des cours synchrones avec toutes les clôtures.
CAD = USD × USDCAD, conversion avant rendement, report as-of borné sans donnée
future. Pour la crypto, préciser les intervalles UTC et l'instant de valorisation
commun, pas seulement multiplier une volatilité par √365. Les corrélations
calculées paire par paire sur calendriers différents peuvent mélanger les
intervalles et ne pas former une matrice positive semi-définie.

Le starter annonce déjà ses `close` ajustés des splits et ses `adj_close`
ajustés des distributions. Réappliquer les splits ou additionner les dividendes
aux rendements ajustés serait une erreur. Une reconstruction indépendante
exige des prix réellement bruts, événements vérifiés et convention documentée ;
un seuil de divergence de 0,5 % n'est pas une norme justifiée par le dossier.

Le rendement ou la corrélation d'un ETF ne révèle pas sa composition. Sharpe
1992 (U294) estime des expositions de style : ce sont des estimations de facteurs,
pas des holdings ni une preuve d'absence d'activité exclue. Le CSV iShares U293
est daté du 12 novembre 2026 et vise **iShares MSCI Canada ETF**, pas XIU.TO ;
il comporte ses propres restrictions d'usage. Une association par nom ou pays
serait une erreur d'identité.

Les scores ESG divergent par périmètre, mesure et pondération, et des historiques
ont été réécrits : ces constats motivent la traçabilité, pas l'abandon de toute
analyse. Définir l'exclusion de Mateo avec Agent0, vérifier entité/filiale,
période, métrique et source primaire avec Agent1, calculer la part couverte et
la part inconnue avec Agent2. Une cible SBTi validée n'est ni la preuve d'un
résultat obtenu ni un score ESG global ; GDELT est une piste de recherche,
pas un verdict de controverse.

Enfin **GPL/AGPL ne signifie pas interdit**. Distinguer licence du code,
licence des poids de modèle, droits des données et mode de livraison.
Un projet peut satisfaire les obligations de redistribution ou choisir une
autre implémentation pour une raison explicite. La GPL ne dispense pas de
respecter les données Yahoo et la licence permissive d'un client API ne
licencie pas son contenu. Recopier puis « réécrire » du code pour échapper à sa
licence n'est pas une stratégie retenue. Les restrictions Commons Clause
(vectorbt) ou BSL (serveur lakeFS) nécessitent leur propre analyse d'usage ;
elles ne se confondent pas avec le copyleft.

## Ce que ce travail autorise à décider

La prochaine conception peut disposer d'un Agent2 scientifique substantiel :
faisabilité du besoin, solutions multiples, risque et financement, diagnostics
de données, sensibilité et limites vérifiables. Elle ne dispose pas encore d'une
preuve de supériorité financière d'un agent, d'une allocation conseillée, d'une
probabilité de réussite calibrée ni de droits universels de redistribution des
données. Les expériences isolées ne sont pas intégrées au produit.
