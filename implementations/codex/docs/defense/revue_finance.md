# Revue financière indépendante — Prompt 5

État : 15 novembre 2026. Les résultats numériques publiés pour Robert et Amira
sont reproduits. Deux défauts de frontière du mandat ont justifié une correction :
les conventions historiques étaient implicites pour le moteur ; une clarification
pouvait masquer une contradiction de budget déjà démontrable. Aucun optimum
financier universel, instrument garanti ou bénéfice personnel n'est établi.

La revue a commencé en lecture seule. Les modifications de `models.py`,
`finance.py` et des tests financiers ont ensuite été autorisées par l'intégrateur.
L'auteur de cette revue n'avait pas construit ces modules. Les modifications de
service, d'inspection documentaire et d'interface appartiennent à d'autres travaux.

## Sources et protocole

Pièces lues : contrat de conception, exemple financier et
`docs/conception/exemples/robert_dossier.json` ; contrat d'intégration,
`docs/implementation/finance.md`, README ; trois exports finaux de décision et
export Robert invalidé ; `decision/finance.py`, `decision/inspection.py`,
`decision/models.py`, sections de qualification/calcul du service ;
`analytics.py`, `datasets.py`, README et métadonnées du starter.

Le JSON de conception dit explicitement que les événements de ses agents et
humains sont fictifs. Il n'est pas une preuve d'exécution du produit. Les exports
`final_demo` sont des traces distinctes ; cette revue contrôle leurs nombres et
leurs entrées, sans déduire d'une cohérence arithmétique une preuve de qualité des
inférences.

La métadonnée de la session `/root/critique_finance`, fichier local
`rollout-2026-11-15T14-00-07-01a1e094-bec9-70a0-9eaf-1d8d1367444c.jsonl`,
indique `model_provider=amazon-bedrock-runtime`. Aucun outil de modèle externe
n'a été appelé. Tous les essais numériques de cette revue sont des calculs
Python sans modèle. Aucun faux modèle n'est présenté comme une exécution AWS.

Preuves :

- [Résultats avant correction](proofs/finance_before_patch.json) : entrées,
  sorties complètes, heure et hash du module antérieur.
- [Script indépendant](proofs/finance_review.py) et
  [résultats après correction](proofs/finance_review.json).
- [Tests de revue](../../tests/test_p5_finance_review.py).
- [Résultat pytest](proofs/finance_pytest.txt) et
  [rapport XML](proofs/finance_pytest.xml) : **76 tests réussis** sur les trois
  fichiers ciblés. Les 13 avertissements proviennent de la dépréciation
  `asyncio.iscoroutinefunction` dans LangSmith.

Reproduction :

```bash
.venv/bin/python docs/defense/proofs/finance_review.py
.venv/bin/python -m pytest -q tests/test_decision_finance.py tests/test_decision_inspection.py tests/test_p5_finance_review.py
```

Les empreintes des fichiers de prix, univers, FX et métadonnées sont enregistrées.
Les anciens exports conservent leurs hashes et leur méthode historique v1 ;
leur hash de code n'a pas à égaler celui du code corrigé. Aucun ancien export
n'a été réécrit pour lui attribuer une exécution v2.

## Défauts confirmés, impact et correction

### FIN-01 — conventions historiques absentes ou textuellement incompatibles

**Gravité : majeure pour une nouvelle demande libre ; les chiffres de l'exemple
Amira ne sont pas invalidés.** Confirmé au moteur avant correction.

Reproduction enregistrée :

1. Prendre `next(e["facts"] for e in examples() if e["id"] == "amira")`.
2. Retirer toutes les hypothèses, ou remplacer `assumptions` par
   « Les autres poids SPY et XIU doivent rester inchangés, sans redistribution
   proportionnelle. ».
3. Appeler `finance.analyze`.

Le résultat antérieur était `conditional`, avec SPY 54 %, XIU 36 %, TSLA 10 %.
Une hypothèse demandant seulement la période du 2024-01-01 au 2025-01-01 donnait
toute la période 2021-11-12 → 2026-11-12. Ces sorties sont dans
`finance_before_patch.json`, cas `contradicted_redistribution`,
`specific_window` et `absent_historical_conventions`.

**Impact :** le moteur pouvait calculer selon une convention fixe non
formalisée dans les paramètres. La restitution de ses nombres exacts ne
garantissait donc pas la fidélité au mandat. Le service demandait au modèle
de documenter les conventions, mais l'outil ne pouvait pas en vérifier
l'admission.

**Correction du noyau réalisée :** `ProblemSpec.historical_policy` est un objet
nullable. Il contient `redistribution` et `window`. Le calcul admet uniquement
`proportional_other_holdings` et `all_common_available`, sans dates
supplémentaires. Une politique absente entraîne `missing_input` ; une autre
redistribution ou une fenêtre spécifique entraîne `unsupported`, sans options
ni claims. L'exemple Amira déclare explicitement cette politique. La méthode
devient `retrospective-comparison-v2` et enregistre la politique et son contrôle.

Les anciens problèmes restent lisibles avec `historical_policy=null`, mais un
nouveau calcul exige une requalification. Aucune migration silencieuse ne
transforme leurs anciennes hypothèses textuelles en choix humain confirmé.

**Limite :** la correction rend les conventions calculatoires contrôlables ;
elle ne comprend pas arbitrairement le texte. Si une nouvelle phrase contredit
une ancienne politique structurée, Agent0 doit corriger le champ ou produire une
clarification bloquante. La revue du moteur ne certifie pas ce comportement
AWS. Le test d'une révision en langage naturel appartient à l'intégration.

### FIN-02 — clarification et infaisabilité algébrique confondues

**Gravité : moyenne ; perte de diagnostic, pas proposition d'une allocation
invalide.** Confirmé dans l'ordre de validation antérieur et reproduit par
un cas contrôlé. L'intégrateur a en outre signalé un parcours AWS dans lequel
Agent0 classait le retrait supérieur au capital comme clarification bloquante.
Cette observation AWS n'a pas été réexécutée par l'auteur de la présente revue.

Cas : capital 100 000 CAD, retrait 120 000 CAD, réserve abstraite nominale,
objectif de réallocation minimale, question bloquante « Le retrait dépasse le
capital ». L'ordre antérieur de `analyze` vérifiait les clarifications avant
d'atteindre le solveur. Il retournait `missing_input`, alors que l'incompatibilité
entre réserve et budget est déjà prouvable sans connaître les poids.

**Correction réalisée :** `reserve_budget_certificate(problem)` contrôle six
entrées structurées : type de décision, devise, objectif, politique de réserve,
capital et retrait. Sous le modèle long-only financé par le capital déclaré :

`réserve ≥ retrait > capital`, tandis que `réserve ≤ capital`.

Le moteur retourne désormais `infeasible`, sans allocation, avec certificat
indépendant du solveur et claim déterministe lié aux montants 120 000,
100 000 et 20 000 CAD. Il conserve les autres questions dans les entrées.
L'absence de positions ne masque pas cette contradiction nécessaire.
Une autre devise, un autre objectif, une réserve réelle inconnue ou des nombres
invalides ne déclenchent pas ce certificat.

**Limite :** ce certificat ne dit pas quelle exigence modifier. Il ne constitue
ni un IIS du modèle entier, ni une preuve qu'aucun apport externe ou autre
mandat imaginable ne pourrait convenir. Le service doit conserver ce résultat
certifié lorsqu'il rencontre aussi des clarifications ; ce point est à vérifier
dans la preuve d'intégration.

## Calculs indépendants et comparaisons

### Robert

Le vérificateur indépendant n'appelle ni `_lp_model`, ni `_solve`, ni `linprog`.
Il énumère les intersections des frontières de contraintes et des ruptures de
la fonction demi-L1, dans l'espace des poids. Le minimum d'une fonction
linéaire sur chaque cellule bornée est atteint à un sommet. Cela fournit ici
un contrôle numérique indépendant de la formulation du solveur, en plus de
la borne algébrique de réserve.

| Cas | Minimum code, CAD | Minimum indépendant, CAD | Résultat |
|---|---:|---:|---|
| Retrait 30 000 | 30 000 | 30 000 | Contraintes satisfaites |
| Retrait 40 000 | 40 000 | 40 000 | Contraintes satisfaites |
| Pertes plafonnées à 1 000 par choc | 74 400 | 74 400 | La borne simple de 30 000 n'est plus serrée |
| TSLA plafonné à 1 % | 30 000 | 30 000 | Nouvelle contrainte respectée |
| Retrait 110 000 | Infaisable | Aucun sommet admissible | Aucune relaxation |

Les chocs sont hypothétiques, exprimés en variations de valeur CAD à douze
mois. TSLA n'est donc pas converti une deuxième fois par un FX historique.
Le retrait est un flux distinct de la perte. Les deux plans sont calculés
depuis les mêmes positions initiales ; 40 000 CAD n'est pas le montant
supplémentaire à déplacer après exécution préalable du plan à 30 000 CAD.

| Option | Réallocation, CAD | Perte actions, CAD | Perte obligations, CAD |
|---|---:|---:|---:|
| Initiale | 0 | 18 250 | 13 900 |
| LP pour retrait 30 000 | 30 000 | 10 000 | 7 900 |
| Autre optimum retourné pour 30 000 | 30 000 | 4 750 | 7 150 |
| Référence simple admissible pour 30 000 | 30 000 | 9 600 | 8 620 |
| LP pour retrait 40 000 | 40 000 | 9 500 | 6 400 |
| Autre optimum retourné pour 40 000 | 40 000 | 2 750 | 6 150 |

La référence simple vend TSLA jusqu'à 10 %, puis finance le reste du retrait
proportionnellement aux trois autres positions : réserve 30 %, TSLA 10 %,
XBB 28 %, XIU 16 %, ZST 16 %. Elle atteint elle aussi le minimum et
satisfait toutes les contraintes. Le LP ne domine pas cette référence dans
les deux chocs ; son autre optimum domine numériquement sa première solution
dans les deux chocs pour les données examinées.

**Interprétation autorisée :** minimum de capital réalloué, avec multiplicité
visible. **Interprétation non établie :** le premier portefeuille retourné serait
le moins risqué ou le meilleur pour Robert. Il serait incorrect de présenter
la comparaison à la seule allocation initiale inadmissible comme une preuve
que l'optimiseur bat une règle simple admissible.

Le solde après retrait vaut 60 000 / 62 100 CAD pour le premier optimum à
30 000 ; 50 500 / 53 600 CAD pour celui à 40 000. Le moteur laisse ce
solde `null` sur la baseline qui ne finance pas la réserve. L'oracle conserve
la même distinction économique.

### Amira

Le second oracle ouvre les CSV directement avec `csv.DictReader`. Il construit
la grille commune, applique `adj_close × FXUSDCAD` aux actifs USD, conserve
les unités achetées initialement et recalcule les statistiques. Il n'utilise
ni `datasets.py`, ni `analytics.py`, ni leurs statistiques intermédiaires.

Période : 2021-11-12 → 2026-11-12 ; 1 228 observations ; dix reports de
FX, âge maximal trois jours. Capital initial identique de 25 000 CAD ;
achat-conservation, mêmes observations et mêmes règles pour toutes les options.

| Mesure | SPY 45 / XIU 30 / TSLA 25 | SPY 54 / XIU 36 / TSLA 10 | Référence simple, un tiers chacun |
|---|---:|---:|---:|
| Valeur finale, CAD | 44 515,751412 | 46 874,022321 | 43 090,829498 |
| Rendement total, % | 78,063006 | 87,496089 | 72,363318 |
| CAGR, % | 12,233000 | 13,397844 | 11,505033 |
| Volatilité annualisée, % | 20,032058 | 15,962031 | 22,542268 |
| Drawdown observé, % | −26,871589 | −19,878378 | −31,403814 |

Les exports et les calculs actuels correspondent aux arrondis publiés :
tolérance absolue de 0,0051 CAD pour la richesse et de 0,00000051 point
pour les pourcentages. Les 1 228 valeurs de richesse sont aussi comparées.

Deux contrôles discriminants donnent des chiffres différents : supprimer à
tort le FX conduit à 40 924,513465 CAD pour l'allocation initiale ; rééquilibrer
quotidiennement conduit à 50 137,716650 CAD. Ces calculs sont étiquetés comme
contrefactuels de vérification, jamais comme résultats du produit.

La cible de 10 % n'est pas optimisée sur cette histoire. Son avantage sur les
deux références examinées est un constat sur cette fenêtre, pas une estimation
de l'avantage à quinze ans. La référence un tiers/un tiers/un tiers n'est pas
présentée comme un profil Amira ni comme un portefeuille adapté.

## Bonnes propriétés confirmées

| Propriété | Preuve et portée |
|---|---|
| Profil → paramètres explicites | Les exemples fournissent capital, poids, retrait/plafonds ou comparaison ; aucun âge ne déclenche une allocation dans le moteur courant. Les paramètres sont fictifs, pas un profil de convenance établi. |
| Horizons distingués | Passer l'horizon Amira de 15 à 40 ans conserve exactement les observations, modifie le hash des entrées et n'invente aucune projection. Les scénarios Robert doivent viser l'échéance du retrait. |
| Réserve distincte de ZST | La réserve est un compartiment abstrait séparé. `real_instrument_unknown` empêche le LP admis ; aucune garantie de ZST n'est inférée. |
| Contraintes historiques | Un retrait positif, un budget de perte ou des chocs structurés sont refusés. Les plafonds de poids initiaux sont vérifiés ; avec TSLA au plus 1 %, les deux options Amira sont explicitement inadmissibles. Le statut global reste celui d'une observation historique, sans allocation choisie. |
| Dates admissibles | Une `knowledge_date` antérieure à l'acquisition du snapshot provoque `missing_input`. La date limite de prix tient compte de la convention D+1 UTC. |
| Traitement des données | Pas de double ajout des splits/dividendes ; conversion CAD conforme ; la macro mensuelle non disponible à date n'entre pas dans ces calculs. |
| Comparaison équitable | Grille et capital identiques entre options ; frais de transaction, de change et impôts exclus pour toutes. Les fenêtres de stress réinitialisent les positions et le disent. |
| Révision Robert | L'export invalidé n'a ni problème, ni analyse, ni vue courants. Les nouvelles pertes et réserves correspondent au retrait révisé ; le diagnostic de pertes initiales reste indépendant du retrait. |

## Limites confirmées et hypothèses non prouvées

La base et la date d'un plafond ne sont pas encore un objet financier
paramétrable. `max_asset_weights` signifie t0 dans le modèle. Pour le premier
optimum Robert à 30 000, TSLA représente environ 12,08 % du solde après retrait
dans le choc obligations, malgré un poids de 10 % à t0. Une demande « 10 %
après retrait » constitue donc un autre mandat. Le cas textuel avant correction
est conservé dans `finance_before_patch.json`, chemin `/cases/post_withdrawal_text` : le noyau
seul ne comprend pas ce changement. Le service doit le qualifier hors domaine
ou demander une précision. **Aucun échec AWS de ce cas n'est affirmé ici.**

Les sources du starter documentent leur acquisition et leurs transformations,
mais elles ne certifient pas la qualité économique de chaque cours. L'univers
sélectionné en 2026 et les cours ajustés de ce millésime sont rétrospectifs.
La grille commune hors crypto peut supprimer un creux entre observations.
Les distributions sont traitées selon `adj_close` et les déclarations du
fournisseur, sans audit externe de chaque événement d'entreprise.

La tolérance, les coûts réels, les impôts, le risque de trajectoire, la
capacité personnelle de perte, les compositions de FNB et les préférences ESG
ne sont pas établis. Les résultats ne suffisent pas à transformer les deux
exemples en conseil personnalisé.

Les calculs financiers et leurs nouvelles frontières structurées sont vérifiés.
La fidélité de toute extraction en langage naturel, la préservation de
l'infaisabilité dans le workflow et la restitution visuelle finale exigent les
preuves séparées d'intégration. Cette revue ne les remplace pas.

## Addendum — diagnostic borné et validation des booléens

Relecture indépendante du correctif d'intégration
`reserve_budget_diagnostic_applicable` / `analyze_budget_diagnostic`,
du routage Agent1/Agent2 et de `tool_contracts.py`.
L'intégrateur avait constaté qu'un véritable run AWS
`5ea414c5e4aa487f95045ae3f3d2010d` pouvait encore finir en attente après deux
demandes d'approfondissement. Cette observation est attribuée à l'intégrateur ;
les essais du présent addendum sont des contrôles déterministes sans inférence.

**Le nouveau routage reste dans son domaine.** Trois revues scriptées,
explicitement étiquetées comme fixtures et exécutées avec `use_ai=False`,
demandent respectivement `deepen`, `clarify` et `calculate_conditionally`.
Avec retrait 120 000 et capital déclaré 100 000, les trois parcours exécutent
uniquement `finance.reserve_budget_diagnostic`, puis présentent le certificat.
Les tests remplacent `linprog`, `baseline_stress`, le chargement des données
de marché et le calcul général injecté par des fonctions qui lèvent une
exception si elles sont appelées. Aucune ne l'est.

L'avis Agent1 d'origine reste présent, `kernel_routing` explique le routage,
les contradictions demeurent `unresolved`, la question de confirmation du
capital reste visible et les contrôles de mandat et de preuve documentaire
restent `insufficient`. Aucune allocation n'est produite. Hors du domaine
strict du diagnostic — retrait au plus égal au capital, autre devise,
objectif incompatible, réserve réelle inconnue ou nombres invalides — l'outil
borné refuse l'appel. Le registre ne prétend pas que les documents ou tests
hashés constituent une nouvelle exécution qualifiante.

**FIN-03 — coercition des booléens avant les contrôles financiers.
Gravité : majeure pour les entrées JSON mal typées ; défaut préexistant,
corrigé pendant cette relecture.** La garde brute refuse `capital_cad=true`.
Cependant, avant correction, `ProblemSpec.model_validate(...).model_dump()`
convertissait ce booléen en `1.0`, après quoi le diagnostic devenait admissible.
La même coercition existait pour les retraits, horizons, plafonds, poids et
rendements de scénarios : `false` pouvait ainsi devenir un rendement nul.
L'API reçoit les faits dans un dictionnaire ; la validation du problème est
donc le point qui doit empêcher cette altération avant le calcul.

Reproduction avant correction enregistrée dans
[finance_bool_before.json](proofs/finance_bool_before.json) : capital `true`
accepté comme 1 CAD ; poids `true` accepté comme 100 % ; rendement `false`
accepté comme 0 %. Il s'agit d'une preuve directe de validation Pydantic,
pas d'un faux journal AWS.

Correction : les types `NumericFloat` et `NumericInt` ajoutent un
`BeforeValidator` qui refuse les booléens avant toute conversion. Tous les
champs numériques concernés, y compris poids/cibles, dictionnaires de plafonds
et de rendements, horizons imbriqués et numéro de révision, l'utilisent.
Les entiers et flottants licites restent admis ; les véritables champs
booléens tels que `clarifications[].blocking` restent inchangés.

Preuves après correction et empreintes des quatre modules relus :
[finance_budget_review.json](proofs/finance_budget_review.json).
Validation ciblée : **101 tests réussis**, notamment dix formes d'entrées
financières booléennes, onze frontières du diagnostic et les trois décisions
de routage scriptées. Résultats :
[texte pytest](proofs/finance_budget_pytest.txt),
[XML pytest](proofs/finance_budget_pytest.xml).

La relecture n'a pas trouvé de passage du diagnostic borné vers une allocation
ou une conclusion sur la validité des documents. Elle ne prouve pas que tout
appel AWS réussira : les étapes précédentes de collecte et d'inférence peuvent
encore échouer opérationnellement. La preuve arithmétique reste conditionnelle
aux six entrées déclarées et au modèle sans apport extérieur ; elle ne
certifie ni leur véracité ni le mandat réel du demandeur.
