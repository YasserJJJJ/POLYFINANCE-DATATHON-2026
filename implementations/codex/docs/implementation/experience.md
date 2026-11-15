# Atelier de dossiers — expérience réalisée

Cette tranche conserve l’ancienne interface et ajoute `workbench.html`,
`workbench.css` et `workbench.js`. Aucun résultat d’exemple n’est embarqué
dans ces fichiers. Les données affichées viennent de l’API locale des dossiers.

## Parcours

- Bibliothèque des dossiers persistants, ouverture par identifiant dans l’URL,
  création depuis une demande libre ou des entrées d’exemple explicitement
  fictives.
- Faits modifiables : capital, retrait, échéance, horizon et objet JSON complet
  pour les positions, contraintes, scénarios et hypothèses. Un champ inconnu
  n’est pas rempli automatiquement.
- Quatre cartes de rôles, alimentées par les tâches, tentatives et pièces
  attribuées. Les identifiants fournisseur sont accessibles dans l’activité.
- Les clarifications adressées à la personne restent distinctes des nœuds de
  recherche, de calcul et de preuve. Ces derniers sont présentés avec leurs
  critères, dépendances et motifs de réouverture dans le mandat inspectable.
- Vues séparées : synthèse, demande, preuves, activité, versions. Les objets
  non couverts par une carte spécialisée restent inspectables en JSON.
- Révision depuis un message libre, un nouveau montant de retrait ou des
  changements structurés. Choix explicite entre modification et variante.
- Reprise demandée au serveur ; aucun état de reprise réussi n’est fabriqué
  par l’interface. Export JSON du dossier et de sa portée actuelle.

## Versions et états

Le polling lit l’instantané réel. Une correction masque immédiatement la
restitution précédente pendant son envoi. Après admission, le serveur doit
retirer les vues et calculs dépendants de l’usage courant jusqu’à leur
réexamen. L’interface respecte `usable: false` et `current_view: null`.

Une révision de dossier n’est pas directement comparée à la révision de
production d’une vue : des commits indépendants peuvent faire avancer le
dossier. Les indicateurs d’utilisabilité du serveur font autorité.
Une réponse GET tardive portant une révision plus ancienne est écartée.
L’en-tête utilise le titre de la vue courante ou le type de décision ; il
ne réaffiche pas comme besoin courant le montant du titre historique initial.
L’export est suspendu pendant l’envoi HTTP d’une mutation, puis reprend avec
l’état effectivement admis par le serveur.

L’affichage d’une vue admissible dans l’onglet Synthèse et une page visible
produit `POST /display` avec sa référence. Ce reçu n’est jamais décrit comme
un accord. Les erreurs d’enregistrement sont visibles.

## Lisibilité et interaction

Interface française sans dépendance ni police distante ; corps système,
titres Georgia, contraste graphite et vert sur crème. Les données calculées
en portefeuille reçoivent des barres SVG accompagnées de valeurs textuelles.
Les historiques disponibles reçoivent des courbes descriptives en CAD,
avec périodes et aucune projection implicite. Les violations de contraintes
et l’admissibilité dans le modèle restent visibles pour chaque option.
La couleur ne constitue pas l’unique indicateur d’état.

Les champs passent sur une seule colonne au petit écran. Navigation clavier,
dialogue natif de pièces, libellés de contrôles et réduction des animations
sont pris en charge. Aucun pourcentage d’avancement ni attente factice.

## Limites et vérifications

La profondeur des explications dépend du contenu réellement fourni par
Agent 3. Développer le détail révèle les explications de la même vue ; cela
ne produit pas une nouvelle inférence ni un diagnostic de compréhension.

Les graphes métier sont inspectables par leurs données et références ; une
visualisation interactive de graphe n’est pas incluse dans cette tranche.
Les contrôles et citations absents restent absents, sans score global inventé.

## Réception exécutée le 15 novembre 2026

Le test navigateur [workbench_ui.cjs](../../tests/workbench_ui.cjs) utilise
Playwright et l’API réelle, sans réponse de succès simulée. L’option `--ai`
est nécessaire pour demander de nouvelles inférences ; sans elle, une
création demande le mode déterministe. `WORKBENCH_DOSSIER` ouvre un dossier
existant sans le recréer ni le réviser.

```sh
WORKBENCH_BASE=http://127.0.0.1:8768 node tests/workbench_ui.cjs --ai

# Revue d'un dossier existant, sans nouvelle inférence
WORKBENCH_BASE=http://127.0.0.1:8768 \
WORKBENCH_DOSSIER=471bf771807a4956b5e19cd731fabf6d \
node tests/workbench_ui.cjs
```

Parcours exécuté depuis l’interface :

- Robert à 30 000 CAD, puis correction explicite à 40 000 CAD ; dossier
  `471bf771807a4956b5e19cd731fabf6d`, révisions 5 puis 10.
- Huit identifiants de requêtes Bedrock réels conservés : les quatre rôles
  interviennent dans chacune des deux versions.
- Export du dossier sélectionné, ouverture des preuves au clavier et
  événement d’affichage avec `accepted: false`.
- Coupure réseau injectée **dans le navigateur de test seulement**, erreur
  visible puis récupération après actualisation.
- Rejeu **dans le navigateur seulement** de la véritable ancienne réponse
  GET à 30 000 CAD : la révision courante et le montant 40 000 CAD sont
  conservés. Le serveur et ses résultats ne sont pas modifiés par ce test.
- Aucun débordement horizontal en 1440 px et 390 px ; aucune erreur JavaScript.

Le premier parcours a passé 14 contrôles en environ 54 secondes. Une revue
supplémentaire a passé 12 contrôles, notamment le GET ancien et la séparation
entre questions du dossier et clarifications personnelles, sans nouvelle
inférence.

Preuves :
[réception du parcours](../../artifacts/workbench-ui/verification.json),
[réception de la revue](../../artifacts/workbench-ui/review/verification.json),
[export 30 000](../../artifacts/workbench-ui/robert-30000.json),
[export 40 000](../../artifacts/workbench-ui/robert-40000.json),
[capture desktop](../../artifacts/workbench-ui/review/overview-viewport.png),
[capture mobile](../../artifacts/workbench-ui/review/overview-mobile-viewport.png).

Les captures sont des vues du produit et les exports des réponses réelles.
Les fichiers de données antérieurs restent des preuves de leur exécution
datée, même si le dossier est révisé à nouveau après cette réception.

### Relecture financière et cas de rendu ciblés

Une relecture indépendante a relevé et fait corriger :

- les fenêtres historiques doivent montrer rendement et repli, pas seulement
  leurs dates ;
- une nouvelle analyse infaisable qui conserve le portefeuille initial comme
  référence ne produit pas une « solution » à zéro capital réalloué ;
- lorsqu’il existe plusieurs optima, les écarts entre deux témoins affichés
  ne sont pas tous imposés par la révision du besoin.

Le test [workbench_rendering.cjs](../../tests/workbench_rendering.cjs) a passé
sept contrôles sur ces cas, les deux courbes historiques, les unités et le
rendu mobile. Il utilise les sorties effectivement calculées par le moteur
Python local, injectées dans un navigateur isolé **pour ce test de composant
seulement**. Il ne crée aucun dossier serveur, ne simule aucune contribution
d’agent et ne fait aucun appel AWS.

[Réception des composants](../../artifacts/workbench-ui/component-tests/verification.json).
Le graphe mobile a été inspecté visuellement ; ses graduations restent lisibles
sans être coupées.

### Réception du dossier Amira réel et métriques historiques

Le dossier existant `8cddaec5d89642de8f38d0b704658763`, révision 5, a été
ouvert sur l’API locale `http://127.0.0.1:8768`. La revue a passé onze
contrôles généraux puis huit contrôles ciblés après correction du rendu.
Elle n’a créé ni révisé de dossier et n’a déclenché **aucune nouvelle
inférence**. Les quatre reçus Bedrock du dossier sont ceux de son exécution
préalable ; l’interface a seulement enregistré son reçu d’affichage.

La synthèse historique sélectionne désormais explicitement six métriques :
rendement cumulé, rendement annualisé, valeur finale, repli maximal,
volatilité annualisée et capital initial. Les autres métriques et contrôles
restent intégralement inspectables dans le détail JSON de chaque option.
La sélection ne dépend plus de l’ordre des clés renvoyées par l’API.

Les valeurs affichées correspondent aux données enregistrées :

- allocation initiale : rendement cumulé de 78,06 %, valeur finale de
  44 515,75 CAD et repli maximal de −26,87 % ;
- variante TSLA initiale à 10 % : rendement cumulé de 87,50 %, valeur finale
  de 46 874,02 CAD et repli maximal de −19,88 % ;
- fenêtre 2022 de l’allocation initiale : rendement de −23,23 %, repli de
  −26,60 % et valeur finale de 19 192,77 CAD.

Ces historiques descriptifs conservent leurs dates, unités et limites.
Le texte rappelle que les allocations sont réinitialisées au début de
chaque fenêtre. Les deux trajectoires en CAD, les onze pièces de preuve
et les quatre rôles distincts correspondent au dossier serveur.

La revue visuelle a aussi détecté un débordement interne auparavant masqué
par le panneau : le tableau imposait une largeur minimale à toute la carte
mobile. Une largeur minimale nulle sur la carte corrige ce comportement.
À 390 px, la carte et sa grille mesurent maintenant 320 px ; le tableau
de 514 px défile dans son conteneur de 286 px. Les six métriques restent
entièrement visibles. Captures desktop et mobile inspectées, sans erreur
JavaScript.

Preuves :
[réception générale Amira](../../artifacts/workbench-ui/amira-real/verification.json),
[contrôles ciblés après correction](../../artifacts/workbench-ui/amira-real/historical-metrics-check.json),
[export du dossier](../../artifacts/workbench-ui/amira-real/ui-export.json),
[carte desktop](../../artifacts/workbench-ui/amira-real/historical-option-desktop.png),
[carte mobile](../../artifacts/workbench-ui/amira-real/historical-option-mobile.png),
[preuves affichées](../../artifacts/workbench-ui/amira-real/evidence-desktop.png).

Les sources désignées par un chemin relatif affichent « Document local —
voir provenance », sans fabriquer de route HTTP. Un contrôle DOM ciblé sur
`docs/methodology.md` et `docs/implementation/finance.md` confirme l’absence
de lien erroné et l’accès au passage enregistré inchangé par le bouton de
provenance. Les neuf liens Web absolus du dossier sont conservés. Aucun
nouvel appel AWS : [preuve ciblée](../../artifacts/workbench-ui/amira-real/local-sources-check.json).
