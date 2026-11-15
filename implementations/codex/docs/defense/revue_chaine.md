# Revue indépendante de la chaîne de décision — Prompt 5

Relecteur : session `/root/critique_chaine`, 15 novembre 2026. Le contrôle
préalable de `session_meta` confirme `amazon-bedrock-runtime`
([preuve](proofs/chaine_session.json)). Je n’ai pas écrit les modules examinés
au Prompt 4. Les corrections ci-dessous ont été réalisées après reproduction
et délégation explicite de l’intégrateur du Prompt 5.

La chaîne est réelle : les quatre rôles ont des appels, des contextes et des
écritures distincts. Cela ne suffit pas à valider toutes ses promesses. La revue
initiale a reproduit trois défauts : une correction effaçait des faits extraits
encore vrais ; une attente effaçait la réponse partielle et son manque concret ;
un contrôle arithmétique insuffisant pouvait recevoir une restitution déclarée
suffisante. Les trois reproductions passent après les corrections P5.

## Périmètre et nature des preuves

Ont été lus : conception, contrats d’échange, parcours et contrôles, contrat
d’intégration, README, état de reprise, `models.py`, `store.py`, `service.py`,
`workflow.py`, `api.py`, ainsi que les exports complets du `final_demo`.
La projection des questions et des résultats dans `workbench.js` a été
inspectée pour comprendre ce qui reste visible.

Les [tests indépendants](../../tests/test_p5_chain_review.py) utilisent le vrai
magasin, le vrai workflow et le vrai calcul financier. La recherche documentaire
est un double explicitement vide. Les extractions et les réponses des rôles
nécessaires aux cas adversariaux sont des doubles ; aucune nouvelle inférence
n’est effectuée par ces tests. Le défaut arithmétique est une injection de panne
de contrôle après un vrai calcul, pas la découverte d’un mauvais nombre produit
par le solveur.

Les exports Robert et Amira constituent, eux, des traces AWS réelles antérieures :
douze reçus Bedrock distincts, quatre rôles pour chacun des trois passages.
La [vérification indépendante](proofs/chaine_archived_aws_integrity.json) retrouve
les empreintes des artefacts et l’égalité des textes/pointeurs entre registre
d’analyse et restitution courante. Elle ne certifie pas l’interprétation
financière du modèle.

Les observations avant correction sont conservées directement dans `proofs/`.
Les observations après correction sont dans `proofs/chaine_after/`. Elles ne
remplacent pas les anciennes preuves.

## Défauts reproduits et corrections

| ID | Gravité | Observation vérifiable avant correction | Impact | Correction et vérification |
|---|---|---|---|---|
| CH-01 | Élevée | Un capital de 100 000 CAD extrait de « Mon capital est de 100 000 CAD » devient `null` après une correction portant seulement sur le retrait. Le contexte du nouveau Agent0 ne contient plus le capital. | Une révision ordinaire détruit le contexte financier déjà déclaré. Les exemples préremplis masquaient le défaut car leurs faits structurés n’avaient pas cette dépendance. | Chaque demande reçoit une capture `request_source.<run_id>` immutable. Le fait extrait dépend de cette capture et conserve son `source_ref`, au lieu de dépendre du curseur `request` remplacé au message suivant. Les anciennes extractions sont prises en charge sans réécriture de leur contenu. Les tests vérifient conservation du fait, puis invalidation effective lorsqu’il est explicitement corrigé. |
| CH-02 | Élevée | Sans montant de retrait, les rôles exécutés sont Agent0→Agent1→Agent2→Agent3→Agent0. L’analyse historique contient `withdrawal_cad: Valeur nécessaire absente`, mais le dossier final a `current_view=null`, `current_analysis=null`, aucune clarification courante et des questions déclarées résolues. | L’utilisateur attend une clarification sans voir ce qu’il doit préciser. Le retour récursif détruit précisément l’explication qu’il devait conserver. | Le retour Agent0, sans nouvel événement humain, écrit une qualification et des questions d’attente sans réécrire `problem`. Analyse et vue partielles restent courantes. `pending_clarifications` expose explicitement la version de qualification ; `active_problem` demeure égal à l’artefact stocké. |
| CH-03 | Élevée | Une vérification `independent_recomputation` au statut `insufficient` est injectée après un calcul réel. La vue garde les conclusions, les options et `arithmetic.status=sufficient`. | Le statut global du résultat contournait le contrôle déterminant. La fidélité de copie pouvait faire passer un résultat non vérifié pour suffisamment contrôlé. | Barrière de contrôles intégrée par l’intégrateur P5 dans Agent2/Agent3. Le test indépendant exige absence de conclusions et absence du statut arithmétique `sufficient` dans ce cas. |
| CH-04 | Modérée | Le cas AWS incomplet examiné par l’intégrateur contient la citation « dans douze mois » et la valeur proposée `12`. Le garde lexical initial ne reconnaissait que des chiffres et rejetait l’extraction. | Une information effectivement donnée est redemandée ; la clarification accuse artificiellement un manque. | Ancrage limité aux cardinaux français zéro à vingt immédiatement suivis de l’unité correspondante. Les tests admettent « douze mois », « quinze ans », « une année » et rejettent un nombre différent, la mauvaise unité ou des expressions hors de cette portée. Aucune valeur par défaut ni conversion d’unité n’est ajoutée. |

Preuves CH-01 :
[avant](proofs/chaine_extracted_fact_revision.json),
[après](proofs/chaine_after/chaine_extracted_fact_revision.json),
[compatibilité avec l’ancienne provenance](proofs/chaine_after/chaine_extracted_fact_revision_legacy.json).

Preuves CH-02 :
[avant](proofs/chaine_incomplete.json),
[après](proofs/chaine_after/chaine_incomplete.json).

Preuves CH-03 :
[avant](proofs/chaine_arithmetic_check.json),
[après](proofs/chaine_after/chaine_arithmetic_check.json).

CH-04 est couvert par huit cas de `test_french_duration_words_require_matching_explicit_value_and_unit`.
Les formes non prises en charge restent des clarifications ; ce garde lexical
n’est pas une preuve de justesse sémantique de toute l’extraction.

Commande de vérification :

```bash
.venv/bin/python -m pytest -q \
  tests/test_p5_chain_review.py \
  tests/test_decision_store_review.py \
  tests/test_decision_service_review.py \
  tests/test_decision_workflow.py
```

Résultat après intégration des corrections : **42 tests réussis**, dont 14 cas de
cette revue ; treize avertissements de dépréciation d’une dépendance. La sortie
exacte est conservée dans [chaine_after_checks.json](proofs/chaine_after_checks.json).
Ce chiffre n’est pas le résultat de la suite globale, exécutée séparément par
l’intégrateur.

## Ce que les contributions des rôles démontrent

| Rôle | Influence réellement observable | Limite de la preuve |
|---|---|---|
| Agent0 | Extraction validée, questions et qualification ; changement des faits transmis au calcul. | Dans les douze reçus du `final_demo`, les trois passages Agent0 n’ajoutent aucun fait (`updates=[]`) : les cas étaient déjà entièrement structurés. Ils ne démontraient donc pas la robustesse d’une correction après extraction libre. |
| Agent1 | Sélection et critique documentaire ; décision de poursuivre, d’approfondir ou de retourner à la qualification. | Le nombre de pièces et le succès de récupération ne prouvent pas leur nécessité. Les routes d’approfondissement et de clarification sont testables, mais les trois passages finaux P4 suivent tous `calculate_conditionally`. |
| Agent2 | Choix d’un outil admis ou refus de calcul ; résultats fournis par le calcul indépendant. | Avant P5, ses listes libres de contrôles et sensibilités étaient surtout conservées comme avis. Le simple choix du bon outil ne prouvait pas l’exécution des contrôles demandés. |
| Agent3 | Ordre des identifiants de conclusions ; conservation déterministe des textes et des montants calculés. | Lors de la revue initiale, `emphasis`, `detail_level` et `follow_up_fields` étaient stockés sans adaptation correspondante de l’affichage. La preuve d’une restitution personnalisée était donc plus étroite que la preuve de fidélité des nombres. |

Un exemple AWS important est présent dans Robert : Agent1 qualifie la
programmation linéaire de méthode « non admise à l’exécution » et Agent2 écrit
que son choix d’outil ne vaut pas autorisation d’exécuter cette méthode.
Le service P4 exécute tout de même le calcul. Cela peut résulter d’un contrat
insuffisant sur l’admission de l’outil local, plutôt que d’un mauvais LP ; cela
réfute néanmoins une lecture selon laquelle ces avis constituaient déjà une
barrière effective. Le constat a été transmis au relecteur des preuves et à
l’intégrateur pour leur qualification et leur correctif.

## Influence du profil et du mandat

Une modification de contrainte a un effet vérifiable : passer le plafond de
perte des scénarios à zéro fait passer le capital minimal déplacé de
30 000 à 100 000 CAD. L’analyse change, tandis que `baseline_stress@1`, qui
décrit toujours les mêmes positions et les mêmes chocs, est correctement
réutilisé ([preuve](proofs/chaine_risk_constraint.json)).

Ce résultat établit l’influence d’une contrainte financière déclarée. Il
n’établit pas une qualification psychométrique ni un effet de l’âge, de la
persona ou du niveau de connaissances. Ces distinctions ne doivent pas être
aplaties sous le seul mot « profil ».

L’horizon de Robert ou d’Amira ne doit pas être présenté comme une projection.
Les avis AWS conservés distinguent explicitement les chocs à douze mois de
l’horizon de quatre ans et la fenêtre historique de l’horizon de quinze ans.
Le contrôle de cette portée dans la communication reste nécessaire même si
changer un champ d’horizon n’altère pas les chiffres d’un calcul rétrospectif.

## Invalidation, reprise, artefacts et contestabilité

Les tests ciblés du noyau et du service vérifient les versions périmées, les
droits d’écriture, les références non lues, les reprises d’échec et les tâches
déjà commises. Le correctif CH-01 ne dispense pas de ces contrôles : la capture
de provenance est effectivement incluse dans le `read_set` d’Agent0 ; remplacer
le fait lui-même invalide ses descendants.

Les tests P4 de reprise sont des interruptions contrôlées. Ils soutiennent
l’absence de second calcul après commit et avant checkpoint. Ils ne prouvent
pas une facturation AWS exactement une fois après une coupure avant réception
du reçu. Cette limite est correctement annoncée dans l’état de reprise.

Les **dix-neuf entrées exactes d’opérations** présentes dans les
exports cumulés Robert révisé et Amira ont été retrouvées dans
`runtime/decision/objects/`, avec les empreintes attendues
([vérification](proofs/chaine_reproducibility.json)).
Le JSON exporté contient les empreintes de ces entrées, mais pas tous leurs
contenus. Il permet l’examen du dossier ; il ne constitue pas à lui seul une
archive autonome de reproduction. Conserver objets, code, dépendances, données
et captures reste nécessaire.

La contestation et la correction existent sous forme de nouvelles demandes
versionnées ; une variante conserve un dossier distinct. L’événement d’affichage
reste séparé de l’accord humain. Les preuves inspectées ne démontrent pas
l’efficacité de l’explication auprès d’utilisateurs ni leur compréhension
effective. Aucun simple affichage ou export ne doit devenir cette preuve.

## Vérification indépendante des vues réelles P5

La [revue UI](proofs/ui_review.json) examine les dossiers existants du serveur
local au moyen de Playwright. Je n’avais pas écrit le workbench avant cette
revue. Les appels de création, correction et reprise sont laissés à
l’intégrateur ; le navigateur n’émet que des lectures et les événements
automatiques d’affichage. Cette revue n’a déclenché aucune nouvelle inférence.

Le dossier incomplet `e6405c6c61f64c5b89c11262ce9b9669`, révision 4, garde
correctement l’échéance de **12 mois** et ne présente aucune allocation.
L’écran affichait toutefois **21 cartes** : sept répétitions exactes entre
les nœuds et les clarifications, plus quatorze formulations sur sept champs.
Ce défaut d’ergonomie a été corrigé après délégation explicite : le texte est
dédupliqué par champ, puis toutes les formulations distinctes d’un champ sont
regroupées dans une carte. Il reste **7 cartes et 14 formulations visibles**.
Aucune équivalence sémantique n’est devinée ; deux questions différentes sur
un même champ restent conservées, y compris si elles partagent un identifiant.
Les raisons et le caractère bloquant sont également conservés.

Le [test de composant](../../tests/test_p5_ui_review.cjs) utilise un instantané
injecté dans le navigateur, sans dossier serveur ni inférence. Il couvre trois
couches de provenance, deux questions réellement différentes sur le même
champ, les identifiants partagés, les questions closes, les raisons, le contexte
de réponse et le format mobile. Il réussit, ainsi que les sept vérifications
existantes de `tests/workbench_rendering.cjs`. La capture réelle
[mobile après correction](proofs/ui/incomplete-mobile-after.png) confirme le
regroupement sans débordement horizontal à 390 pixels.

Le dossier Robert `4089e4b0d70f40b6b20d832fa261e1dc`, révision 15, conserve
le capital extrait de **100 000 CAD** et le retrait corrigé de **40 000 CAD**.
Passer le budget de perte des scénarios de 15 000 à **1 000 CAD** fait passer
le minimum réalloué de **40 000 à 74 400 CAD**. L’écran avant/après affiche
ces valeurs et précise qu’il compare des témoins parmi des optima multiples ;
les écarts de poids ne sont donc pas présentés comme tous nécessaires.
Pendant la révision, les anciennes cartes de réponse étaient retirées de
la synthèse et conservées dans leur portée historique.

Les sources de Robert montrent trois pièces sélectionnées et deux consultées
non sélectionnées ; Amira en montre cinq et six. Les libellés distinguent
explicitement sélection et vérification de chaque affirmation. Le bouton
de provenance ouvre les chemins, dates et empreintes des captures.
Les réserves documentaires sont annoncées comme **commentaires de revue**
distincts des résultats du calcul. Les codes machine isolés visibles dans
une première vue Robert ont disparu de la révision 15 après la correction
de l’intégrateur ; la vue brute reste inspectable.

Le cas impossible initial `5ea414c5e4aa487f95045ae3f3d2010d` reste une
preuve négative : il termine en attente, sans analyse ni vue, donc sans
certificat numérique visible. L’écran ne fabrique aucune allocation.
Le défaut est en amont du rendu : l’infaisabilité est routée comme une
demande de clarification.

Après correction, le nouveau dossier `1f7d3a73d5924a09ba73925655dce389`
atteint la révision 5 avec quatre reçus AWS, une analyse et une vue
`infeasible`. Le [certificat affiché](proofs/ui/impossible-certificate-claim.png)
énonce **120 000 CAD de retrait**, **100 000 CAD de capital** et
**20 000 CAD de déficit**, sous réserve abstraite financée sans apport externe.
Les trois boutons « Valeur liée » ouvrent exactement ces trois valeurs dans
`analysis@1`. Le texte et les pointeurs de la restitution correspondent à ceux
du registre d’analyse ; aucune carte d’allocation n’est affichée. Le contrôle
inspectable montre la contradiction `R ≥ retrait > capital` et `R ≤ capital`,
bornée à ce sous-ensemble nécessaire des contraintes, sans IIS global.

Une observation Agent1 disait encore que le contrôle et le reçu étaient
« absents » après leur production par Agent2. Le rendu porte désormais le titre
**« Observations à la revue Agent 1, avant le calcul »**, et renvoie aux
contrôles ultérieurs. Le [rendu corrigé](proofs/ui/impossible-answer-after-label.png)
et le test de composant confirment que les observations d’origine restent
visibles et identiques dans la trace inspectable. Cette datation n’est pas
un rapprochement automatique entre chaque obligation Agent1 et son éventuel
résultat Agent2 : ce mécanisme reste à implémenter, et aucun conflit n’est
déclaré résolu par simple changement de libellé.

## Conclusions bornées de la revue

La fidélité des affirmations financières courantes aux sorties stockées est
vérifiée sur les exports AWS examinés. Les contraintes financières influencent
réellement le calcul. L’invalidation sélective, les droits d’écriture et la
reprise ont des mécanismes exécutables et testés.

La robustesse des cas incomplets et des corrections libres n’était pas établie
par les démonstrations P4 : deux contre-exemples l’ont réfutée avant réparation.
Le contrôle de suffisance arithmétique présentait aussi une faille de
propagation, indépendamment de la justesse des chiffres des démonstrations.
Les corrections sont vérifiées par des tests ciblés ; les nouvelles traces
AWS et le parcours visuel après redémarrage sont documentés séparément par
l’intégrateur du Prompt 5.
