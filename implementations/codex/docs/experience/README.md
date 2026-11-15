# À ouvrir et essayer — proposition Prompt 6

**[Prototype interactif](http://127.0.0.1:8770/) ·
[Canvas visuel](http://127.0.0.1:8770/canvas.html) ·
[Démonstration de 75 secondes](http://127.0.0.1:8770/demo.html)**

Double-cliquer **[Ouvrir_le_prototype.command](../../Ouvrir_le_prototype.command)**
pour démarrer ou rouvrir le prototype. L’application existante reste sur
[8768](http://127.0.0.1:8768/) ; ses fichiers et dossiers n’ont pas été remplacés.

**Direction recommandée : le carnet de décision vivant.**
La conclusion et sa limite viennent avant les agents. Une preuve s’ouvre
dans le contexte du chiffre. Une variante reste séparée du dossier ; une
révision explique ce qui a changé, ce qui reste valable et pourquoi.

Version **0.1, proposée pour validation**, 15 novembre 2026.
L’intégration dans le produit attend la validation de la direction visuelle
et des interactions majeures, conformément au Prompt 6.

## Un essai en quelques minutes

1. Ouvrir **Robert**, à 30 000 CAD. Lire la limite et la référence simple :
   elle atteint aussi le minimum.
2. Ouvrir **Pourquoi ce chiffre ?**, puis les contrôles. Fermer le panneau
   ramène à la décision.
3. Passer à **Les options**, puis **La méthode** : mêmes chiffres,
   mêmes hypothèses, davantage de profondeur.
4. Dans **Explorer une variante**, passer le retrait à 40 000 CAD.
   Le moteur calcule réellement sur une copie ; aucun agent n’est relancé.
5. Utiliser le résultat dans la copie du prototype, puis **Revenir à l’archive**.
   La base d’origine est conservée. Modifier ensuite un champ marque un
   résultat précédent comme ancien et empêche son adoption ambiguë.
6. Essayer **Simuler une erreur**, puis reprendre avec les mêmes paramètres.
7. Ouvrir **Ce qui a changé** : les trois états 30 000 / 40 000 / 74 400 CAD
   proviennent de révisions réellement exécutées, avec leurs événements.
8. Ouvrir **Amira** : deux trajectoires historiques et leurs valeurs exactes.
   Puis examiner le dossier incomplet et le retrait impossible.

## Ce qui fonctionne ici

- Quatre dossiers de référence, six états archivés, avec provenance et
  téléchargements exacts.
- Trois profondeurs de lecture, profil consultable avec origine, sources
  filtrables, contrôles distincts et reçus des quatre agents.
- Répartition/tableau sur les mêmes options de Robert ; trajectoires
  quotidiennes d’Amira avec axe calendaire réel, données exactes et CSV.
- Calcul de variantes Robert par le moteur existant : retrait, budget
  de perte, capital et plafond initial de TSLA.
- Copie locale, retour à l’archive, résultat daté par sa base, gestion des
  champs modifiés, reprise d’erreur et navigation pendant un calcul.
- Demande libre et clarification conservées comme **brouillons locaux**.

La nouvelle interface ne lance pas les quatre agents. Les passages AWS
affichés appartiennent aux exécutions archivées. Une exploration appelle
le moteur Python seul et réexécute ses calculs ; ses listes de résultats
réutilisables sont une **prévision de dépendances**, pas un journal de
réutilisation effectué. Les listes de réutilisation des trois révisions
archivées sont, elles, tirées des événements enregistrés.

## Canvas et fondements

| Pièce | Contenu |
|---|---|
| [CANVAS](CANVAS.md) | Promesse, navigation, carte des vues, contrats d’expérience, capacités, composants et dépendances |
| [Recherche](recherche.md) | Huit références qualifiées, produits examinés, trois directions distinctes et limites des preuves |
| [Matrice d’adaptation](matrice_adaptation.md) | Invariants financiers, ordre, vocabulaire, représentations et limites aux trois niveaux |
| [Paramètres](parametres.md) | Signification, provenance, valeurs, unités, domaines, recalcul et annulation |
| [Contrat du prototype](contrat_prototype.md) | Données archivées, API locale, calculs, état local et intégration future |
| [Correspondance](correspondance.md) | Élément proposé → composant → données → comportement vérifié → futur raccordement |
| [Outils](outils.md) | Accès effectivement testés, choix des outils, plugins non nécessaires, route AWS |
| [Audit initial](audit_initial.md) | Application 0.5 observée avant conception, desktop et mobile |
| [Revue du prototype](audit_prototype.md) | Critique indépendante, défauts démontrés et contre-vérifications ciblées |
| [État de reprise](ETAT_REPRISE.md) | Relancer, modifier, conserver les références et reprendre après validation |

La [vidéo](../../prototype/prompt6/demo/README.md) et son
[script](proofs/demo.cjs) montrent des interactions réelles, sans nouvelle
inférence ni activité décorative. Une erreur de prototype y est explicitement
simulée. Les scripts et journaux conservent les conditions de l’essai.

## Contrôles et corrections

La revue UX a été confiée à une nouvelle branche qui n’a écrit ni
l’interface ni l’adaptateur. Une seconde revue des données a été réalisée
par l’auteur de l’adaptateur, qui n’a pas écrit l’interface : cette
indépendance est partielle et déclarée.

Les contre-exemples ont fait corriger notamment :

- une variante r5 réouverte depuis r15 qui pouvait sembler rattachée à r15 ;
- un résultat encore visible après modification de ses paramètres ;
- une affirmation de plusieurs optima sur un résultat qui ne l’établissait pas ;
- un certificat budgétaire expliqué comme un résultat de solveur, et une
  liaison du déficit vers le mauvais champ ;
- l’arrondi d’un petit minimum de 0,15 CAD en 0 CAD ;
- un libellé blanc de graphique insuffisamment contrasté, un débordement
  à 320 px et une navigation pendant calcul qui provoquait une erreur ;
- un libellé interne suggérant une réutilisation de calcul dans l’exploration
  locale, alors qu’il s’agit seulement d’entrées indépendantes réutilisables.

Chaque correction a reçu une contre-vérification ciblée. Les résultats
figurent dans [proofs/audit/prototype](proofs/audit/prototype/),
[la revue des données](proofs/data_review.json) et
[la vérification de l’adaptateur](../../prototype/prompt6/data/verification.json).
Les nombres de tests successifs se recouvrent : ils ne sont pas additionnés.

Le contrôle axe ciblé n’a plus de violation détectée après correction.
Clavier, focus, Escape, 1440/390/320 px, invariants d’affichage et parcours
essentiels ont été examinés. Ce n’est ni une certification WCAG exhaustive,
ni un essai avec lecteurs d’écran, ni une étude démontrant la compréhension.
La première conclusion mobile est accessible plus tôt qu’avant ; cela ne
suffit pas à prouver que la décision est mieux comprise.

## Limites et validation attendue

La copie locale n’est pas une branche durable de production. Les demandes
libres et corrections autres que les paramètres Robert ne relancent pas
la qualification. Amira est consultable mais son éditeur de variantes
n’est pas branché. Langues supplémentaires, glossaire étendu, graphes
de sensibilité guidés et tests humains restent à qualifier.

Les limites financières de la défense restent visibles : réserve abstraite,
chocs sans probabilités, frais et fiscalité exclus, optima conditionnels,
référence simple aussi performante sur le minimum Robert r5, comparaison
d’Amira rétrospective et non prédictive.

**Votre validation porte sur la direction visuelle et les interactions
majeures.** Les choix de HTML/CSS/SVG, serveur local, adaptateur et
vérifications sont réversibles et ont été pris dans le mandat autorisé.
Après votre retour, la correspondance servira de contrat d’intégration :
les événements réels remplaceront les états locaux prévus, sans modifier
silencieusement l’expérience approuvée.
