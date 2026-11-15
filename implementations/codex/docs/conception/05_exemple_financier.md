# Robert : financement d'un retrait et révision du dossier

**Conception du 15 novembre 2026, soumise à validation.** Ce parcours décrit le
travail attendu des quatre agents ; il n'est pas une nouvelle exécution de ces
agents ni une fonction construite. Ses confirmations sont celles du personnage
fictif du Prompt 1. Ses résultats numériques proviennent des expériences déjà
réalisées aux Prompts 1 et 2. Aucun calcul expérimental supplémentaire, appel de
modèle produit ou changement de logiciel n'a été effectué pour ce document.

## 1. Demande, faits et sous-problèmes

> « J'ai un portefeuille fictif de 100 000 CAD. Je prépare ma retraite dans
> quatre ans, mais j'aurai besoin de 30 000 CAD dans douze mois. Tesla représente
> 25 % du portefeuille. Je voudrais modifier le moins possible mes placements. »

Agent0 conserve la demande avant de la formaliser. « Modifier le moins possible »
pourrait désigner nombre de lignes, capital réalloué, frais ou impôt : ces
objectifs ne sont pas interchangeables. Dans la branche fictive déjà définie
au Prompt 1, Robert confirme le **capital réalloué**, sans frais ni fiscalité
modélisés. Il confirme aussi un retrait nominal impératif, sans réserve extérieure
ni vente future d'actifs risqués pour le financer.

| Élément du mandat illustratif | Valeur / statut / provenance | Conséquence |
|---|---|---|
| Capital et positions initiales | 100 000 CAD ; XBB.TO 35 %, ZST.TO 20 %, XIU.TO 20 %, TSLA 25 % ; faits de l'exemple P1, pas positions réelles constatées | Base fixe `w0` pour mesurer toute modification |
| Liquidité à douze mois | 30 000 CAD nominaux, impératifs ; confirmation fictive P1 §7 | Sous-problème de financement d'une échéance |
| Horizon du solde | Quatre ans ; pas de capital final garanti demandé dans cette branche | Ne fournit ni rendement attendu ni validation à quatre ans |
| Exposition TSLA | Au plus 10 % **du capital à l'allocation initiale** ; préférence confirmée dans P1 | Contrainte datée ; ni plafond permanent ni plafond du solde après retrait |
| Pertes dans les chocs étudiés | Au plus 15 000 CAD par choc ; convention de l'exercice P1 | Ne représente ni perte maximale future ni tolérance psychométrique calibrée |
| Réserve réalisable | Instrument, conditions et protection inconnus | Recherche requise avant toute conclusion sur un placement réel |
| Mise en œuvre | Aucun ordre ; aucune réallocation exécutée | La révision de 30 à 40 kCAD garde le même `w0` |

Agent0 produit un mandat versionné et quatre sous-problèmes liés :

1. **Financer** le retrait à son échéance : que signifie « disponible nominalement »
   et quelle preuve permettrait de l'affirmer ?
2. **Rendre admissible** l'allocation initiale : budget, réserve et plafond TSLA.
3. **Comparer** les allocations admissibles : modification minimale, pertes
   dans les scénarios et arbitrages non départagés.
4. **Qualifier la portée** : coûts, instruments, date du retrait et risques non
   représentés pourraient-ils invalider la conclusion ?

Chaque sous-problème garde ses parents, entrées, inconnues et critères de réussite.
Une méthode ou un actif n'est pas sélectionné à partir de l'âge de Robert.

## 2. Une recherche peut rouvrir le problème parent

Une première hypothèse de travail pourrait être : « ZST sert déjà de réserve ».
Agent1 doit examiner cette hypothèse avant qu'Agent2 compte les 20 % de ZST
comme liquidité nominale certaine. **Le dossier disponible ne contient pas de
preuve établissant que ZST garantit le montant nominal requis à l'échéance.**
Un historique de prix ou une volatilité faible ne fournit pas cette preuve.
Ce constat d'insuffisance documentaire n'est pas une nouvelle vérification
des conditions actuelles de ce FNB.

Agent1 ne remplace donc pas silencieusement ZST par « cash ». Il renvoie au
mandat parent :

- **Conclusion sur un instrument réel : en attente.** Rechercher les documents
  primaires actuels des instruments envisageables, leur échéance, disponibilité,
  protection, coûts et limites. Ce travail n'est pas accompli dans cet exemple.
- **Branche pédagogique conditionnelle : calculable.** Conserver le besoin,
  isoler une réserve nominale abstraite à rendement nul et rendre son existence
  explicite comme hypothèse. Agent0 enregistre la portée de cette branche ;
  Agent2 peut alors calculer sans présenter la réserve comme un produit accessible.

Le retour modifie la structure du problème : il introduit un compartiment
distinct de ZST et interdit de qualifier une allocation de « financement
effectivement assuré » à partir du seul résultat du solveur.

| Preuve ou hypothèse mobilisée | Source et lecture disponibles | Usage autorisé |
|---|---|---|
| Besoin, positions, plafond, chocs | [P1 §7](../refonte/01_diagnostic_et_contrat.md), exemple fictif confirmé ; [inspection P1](../refonte/inspection_diagnostic.json) | Paramètres du cas, pas informations de marché actuelles |
| Finalité, liquidité et contraintes avant allocation | Corpus CFA examiné au P2 ; [fiche Agent1](../recherche/methode_sources/01_fondements_et_agent1.md) | Organiser la qualification ; aucun poids « recommandé par CFA » |
| Objectif linéarisable, contraintes et certificat | Boyd–Vandenberghe 2004, passages de convexité/dualité ; [F01](../recherche/finance/06_sources_primaires_et_nv.md) | Justifier le LP et distinguer modèle admissible et besoin réel |
| Diagnostic d'infaisabilité | Chinneck 2007, diapositives ciblées ; [F02](../recherche/finance/06_sources_primaires_et_nv.md) | Expliquer un conflit si nécessaire ; un IIS n'est pas la meilleure réparation |
| Solutions numériques et limite des garanties | [résultats P2](../recherche/finance/experiences/results.json), objet `robert` ; [protocole](../recherche/finance/experiences/PROTOCOLE.md) | Réutiliser les résultats réellement exécutés et leur preuve algébrique |

Ces lectures sont réutilisées, pas présentées comme une nouvelle recherche.
L'adoption d'un modèle de rendement, de CVaR ou de probabilité d'objectif exigerait
d'autres hypothèses et une raison liée au besoin. Aucune n'est nécessaire pour
répondre à la question conditionnelle de modification minimale ici.

## 3. Contrat mathématique de la branche illustrative

Notation : `V0 = 100 000 CAD`, `t0` date d'allocation hypothétique, `t1 = t0 + 12 mois`.
Ces dates relatives ne désignent pas des cours observés au 15 novembre 2026.
Le retrait `Q` est de 30 000 puis 40 000 CAD. Ordre des compartiments :

`w = (réserve abstraite, XBB.TO, ZST.TO, XIU.TO, TSLA)`

`w0 = (0, 0.35, 0.20, 0.20, 0.25)` (poids fractionnaires).

Les chocs P1 à douze mois, sans probabilité, sont repris intégralement :

| Compartiment | Rendement du choc actions | Rendement du choc obligations |
|---|---:|---:|
| Réserve abstraite | 0 % | 0 % |
| XBB.TO | −5 % | −15 % |
| ZST.TO | 0 % | −2 % |
| XIU.TO | −20 % | −10 % |
| TSLA | −50 % | −25 % |

Pour éviter une ambiguïté de devise, le contrat de conception traite ces nombres
comme **chocs de valeur en CAD**. Ce sont des paramètres synthétiques, pas des
rendements en USD auxquels on aurait ajouté un FX observé. Une étude séparant
prix local et change devrait remplacer explicitement cette convention.

Agent2 résout :

\[
\min_w T(w)=\frac12\sum_i|w_i-w_{0,i}|
\]

sous

\[
\sum_i w_i=1,\qquad w_i\ge0,\qquad
w_{\mathrm{réserve}}\ge Q/V_0,\qquad w_{\mathrm{TSLA}}\le0{,}10,
\]

\[
L_s(w)=-V_0\sum_i w_i r_{s,i}\le15\,000\ \text{CAD},
\qquad s\in\{\mathrm{actions},\mathrm{obligations}\}.
\]

Le LP exécuté introduit `d_i ≥ w_i−w0_i` et `d_i ≥ w0_i−w_i`, puis minimise
`½Σd_i`. Le montant réalloué est `V0×T`. Ce **turnover à sens unique** ne compte
pas deux fois ventes et achats ; il n'est ni des frais ni le nombre d'opérations.

Hypothèses : positions fractionnaires ; absence de financement extérieur,
levier, coûts, taxes et inflation ; réserve disponible et stable jusqu'à `t1` ;
chocs terminaux appliqués aux allocations initiales, sans stratégie de
rééquilibrage intermédiaire. Ces hypothèses délimitent le résultat, elles ne
décrivent pas toutes des possibilités vérifiées.

Pour une solution dont la réserve finance le retrait, la richesse restante dans
le scénario est `W_s(t1 après retrait)=V0−L_s−Q`. Le retrait n'est pas une perte
de marché. Aucun drawdown de trajectoire ou résultat à quatre ans n'est calculé
par ces deux chocs terminaux.

## 4. Résultats réutilisés et solutions non uniques

Les poids ci-dessous sont affichés en pourcentage. Les valeurs P2 proches de
20 % et 10 % ne diffèrent que par leur représentation flottante ; les valeurs
brutes restent conservées dans le JSON.

| Option et origine | Réserve / XBB / ZST / XIU / TSLA | Montant réalloué depuis `w0` | Perte actions | Perte obligations | Retrait financé dans le modèle |
|---|---|---:|---:|---:|---|
| A, portefeuille initial P1 | 0 / 35 / 20 / 20 / 25 | 0 CAD | 18 250 CAD | 13 900 CAD | Non ; réserve, plafond TSLA et premier budget de perte échouent |
| B, TSLA 5 % avec redistribution proportionnelle P1 | 0 / 44,333… / 25,333… / 25,333… / 5 | 20 000 CAD | 9 783,33 CAD | 10 940 CAD | Non ; aucune réserve dédiée |
| C30, candidat P1 | 30 / 35 / 5 / 20 / 10 | 30 000 CAD | 10 750 CAD | 9 850 CAD | Oui pour 30 kCAD, sous hypothèses |
| E30, solution du LP P2 | 30 / 20 / 20 / 20 / 10 | 30 000 CAD | 10 000 CAD | 7 900 CAD | Oui pour 30 kCAD, sous hypothèses |
| D40, candidat révisé P1 | 40 / 30 / 0 / 20 / 10 | 40 000 CAD | 10 500 CAD | 9 000 CAD | Oui pour 40 kCAD, sous hypothèses |
| E40, solution du LP P2 | 40 / 10 / 20 / 20 / 10 | 40 000 CAD | 9 500 CAD | 6 400 CAD | Oui pour 40 kCAD, sous hypothèses |

Les scénarios et budgets sont identiques entre comparaisons. C30 et E30
deviennent insuffisants pour financer 40 kCAD ; leur admissibilité à 30 kCAD ne
doit pas être réutilisée dans le mandat révisé.

**Preuve du minimum conditionnel.** Comme `Σ(w−w0)=0`, la demi-somme des
variations absolues égale la somme des augmentations de poids. Créer une réserve
`q=Q/V0` depuis zéro impose donc `T≥q`. Les solutions C30/E30 atteignent
`T=0,30` et satisfont les contraintes ; D40/E40 atteignent `T=0,40`. Elles
atteignent la borne inférieure du problème correspondant. La preuve porte sur
ce modèle, pas sur les coûts réels ou l'utilité financière universelle.

**Le solveur n'a pas choisi la meilleure allocation selon tous les critères.**
E30 perd moins que C30 dans les deux chocs, et E40 moins que D40, pour la même
rotation. C'est une comparaison réelle sur les critères affichés. Pourtant le
LP ne minimise que la rotation : il n'a exécuté aucun objectif secondaire de
perte, aucune optimisation de rendement et aucune recherche de frontière
complète. Son ordre interne peut sélectionner un optimum parmi plusieurs.

Agent2 présente les alternatives et leur contre-argument. Si Robert demande
de privilégier la plus faible perte dans ces scénarios à rotation minimale,
Agent0 formalise ce critère secondaire et ses limites ; Agent2 doit alors
résoudre et vérifier ce **nouveau problème**. Il ne prétend pas qu'E30/E40
optimisent déjà ce critère. D'autres préférences — coût fiscal, exposition,
qualité de la réserve — pourraient changer le départage.

## 5. Conclusion conditionnelle et boucle de révision

Une restitution fidèle par Agent3 pourrait être :

> « Réduire Tesla ne suffit pas à constituer les 30 000 CAD dont tu as besoin.
> Dans notre exercice avec réserve abstraite, déplacer 30 000 CAD est le minimum
> possible. Plusieurs répartitions atteignent ce minimum. La solution calculée
> E30 perd 10 000 et 7 900 CAD dans les deux chocs choisis, contre 10 750 et
> 9 850 CAD pour C30. Ces chiffres ne garantissent pas tes pertes futures.
> Nous devons encore vérifier un instrument de réserve réel et préciser ce
> qui départage les solutions avant d'aller plus loin. »

L'explication est reliée à des objets versionnés, dont les identifiants ci-dessous
sont **des identifiants de conception** et non des traces d'agents exécutés :

| Événement | Travail de l'agent et réouverture | Documents et résultats affectés |
|---|---|---|
| Demande initiale | Agent0 qualifie besoin/contraintes et décompose les questions ; Agent1 examine financement et méthodes | Mandat `ROB-M1`, preuves `ROB-P1` ; origine fictive de chaque confirmation visible |
| Réserve assimilée à ZST sans preuve | Agent1 constate la lacune, renvoie au parent ; Agent0 distingue conclusion sur instrument réel et branche abstraite | Hypothèse révisée dans `ROB-M1a`, lacune de preuve conservée ; aucun statut « instrument validé » |
| Branche abstraite acceptée dans le scénario | Agent2 utilise le LP déjà vérifié, montre C30/E30 et leurs limites ; Agent3 restitue | Analyse `ROB-A1`, restitution `ROB-R1`, liens vers résultats P1/P2 réutilisés |
| Robert change le retrait : 40 000 CAD | Agent3 transmet la modification ; Agent0 crée `ROB-M2`, remplace seulement `Q` et réévalue ses dépendances ; Agent1 réutilise les passages toujours pertinents | Admissibilité des réserves 30 kCAD périmée ; besoins d'instrument/coûts à revoir si cette modification les affecte |
| Analyse de la nouvelle branche | Agent2 réutilise D40/E40 déjà calculés dans P1/P2 pour illustrer le futur recalcul ; Agent3 explique cause et différence | `ROB-A2` et `ROB-R2` distinguent résultat réutilisé et nouvelle exécution future |
| Contestation : « Je veux 10 % TSLA après retrait » | Agent0 constate que le plafond a changé de base/date ; Agent2 doit reformuler les contraintes, potentiellement par scénario | Les allocations actuelles ne certifient pas ce nouveau plafond ; nouvelle analyse requise |
| Coût, date, réserve extérieure ou garantie nouvellement précisés | Agent0 révise besoin/état ; Agent1 recherche les faits déterminants ; Agent2 invalide les résultats dépendants | Pas de simple changement de texte sur des chiffres inchangés |

La révision 30→40 kCAD compare **deux plans depuis le même portefeuille initial** :
aucun plan n'a été exécuté. Si une simulation avait déjà réalloué les positions,
ou si les prix avaient changé, le nouvel état initial devrait être enregistré ;
les 40 kCAD ne représenteraient plus automatiquement le montant supplémentaire
à déplacer. L'ancienne version demeure consultable avec son mandat.

L'horizon de quatre ans reste une question ouverte. Si Robert demande le capital
probable à la retraite, la présente analyse ne suffit plus : Agent0 précise
l'objectif, Agent1 examine modèles/données, Agent2 qualifie les flux et
l'incertitude. La réponse ne consiste pas à extrapoler les deux chocs à un an.

## 6. Provenance exacte et contrôles de passage

| Pièce déjà produite | Version et contenu utilisé |
|---|---|
| `inspection_diagnostic.json` P1 | Créé le `2026-11-15T13:08:53.608642+00:00` ; objet `target_experience_illustration` : paramètres, chocs, A/B/C/D ; SHA-256 `eb375713e41f09690253c8beceb7ab6ebe6ca82408c705982d1aadff355a3c6b` |
| `results.json` P2 | Créé le `2026-11-15T13:57:35.919492+00:00` ; objet `robert` ; SHA-256 `c10a911163975d63f71588925d778e54ce25493afc9ac56b8515c81106b8e8a2` |
| Environnement P2 | Python 3.15.2 ; NumPy 2.5.4 ; SciPy 1.18.1, `linprog(method="highs")`. `highspy` 1.16.0 sert au test IIS séparé ; ne pas confondre sa version avec celle embarquée par SciPy. scikit-learn 1.9.1 concerne l'expérience covariance, pas le LP Robert. |
| Valeurs brutes E30 | Poids `[0.3,0.19999999999999996,0.2,0.2,0.1]`, objectif `0.3`, pertes fractionnaires `[0.1,0.079]`, maximum de violation des inégalités enregistré `0.0` |
| Valeurs brutes E40 | Poids `[0.4,0.09999999999999998,0.2,0.2,0.1]`, objectif `0.4`, pertes fractionnaires `[0.095,0.064]`, maximum de violation des inégalités enregistré `0.0` |

Le LP Robert ne lit pas les CSV de cours/FX : ses paramètres sont synthétiques.
Les empreintes des CSV présentes ailleurs dans `results.json` appartiennent aux
autres expériences ; elles ne rendent pas ces chocs historiques ou calibrés.
La graine commune 20261115 concerne les expériences aléatoires, pas une
incertitude simulée dans ce LP déterministe.

Les contrôles P2 déjà exécutés vérifient succès du solveur, objectif à moins de
`10⁻⁹` de la borne de réserve et résidu maximal des inégalités `<10⁻⁸`.
La borne algébrique est indépendante du solveur. Les tableaux arrondissent pour
lecture ; les poids, unités et résultats bruts restent accessibles.

Pour la future réalisation, les conditions de passage sont :

- budget, bornes, réserve et plafond contrôlés **sur la solution non arrondie**,
  avec unités/tolérances et état exact du solveur ;
- état numérique, faisabilité mathématique et réalisation financière distingués ;
- chocs datés relativement, sans probabilités inventées ; retrait séparé des pertes ;
- instrument de réserve non présenté comme validé sans preuve correspondante ;
- optima multiples visibles, tout départage nouveau qualifié et recalculé ;
- changement de retrait, date, frais ou base du plafond TSLA relié aux conclusions
  invalidées ; aucun indicateur historique inchangé utilisé comme réponse de substitution ;
- conservation du rôle de chacun des quatre agents, des réutilisations de preuves
  et des motifs de retour, sans revendiquer une nouvelle exécution dans ce document.

Si le modèle devient infaisable, Agent2 doit isoler le conflit et sa portée,
pas relâcher une exigence à l'insu de Robert. Si la preuve de réserve manque,
il peut conclure sur la branche abstraite tout en laissant la conclusion sur
l'instrument réel ouverte. La construction de ce parcours attend la validation
de la conception.
