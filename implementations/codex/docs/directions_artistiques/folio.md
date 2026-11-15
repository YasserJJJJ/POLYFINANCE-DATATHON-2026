# Folio — une décision à lire, annoter et réviser

À ouvrir : **[Folio](http://127.0.0.1:8770/directions/folio/)**. Le serveur du prototype doit être actif sur le port 8770. Cette direction utilise exclusivement le contrôleur partagé `prototype/prompt6/directions/shared/experience.js` et le moteur local existant.

## Parti pris

Une revue de décision, avec une page continue plutôt qu’un assemblage de cartes. Le dossier se lit comme une double page : un titre qui pose la question, le résultat en regard, un contrepoint indépendant immédiatement sous la conclusion et des notes marginales qui donnent accès aux preuves. Le passage au calcul détaillé change l’ordre de lecture, pas seulement la quantité de texte.

La matière évoque le papier et l’encre : fond ivoire légèrement tramé, vert sombre pour le texte, rouge d’annotation, filets francs, grandes différences de corps. Le motif de contours est un SVG original et décoratif, exclu de l’arbre d’accessibilité. Il ne représente aucune série financière et ne porte ni axe ni légende de données.

La composition donne trois gestes principaux :

- **Comprendre** : lire la conclusion, son minimum conditionnel et la limite « la référence simple atteint aussi ce minimum ».
- **Comparer** : examiner une planche tabulaire dans les mêmes unités, puis sélectionner la répartition qui mérite d’être regardée.
- **Réviser** : rédiger un erratum sur une copie locale, calculer puis lire les différences avant/après.

Cette direction favorise une lecture calme, les explications et la contestation documentée. Elle convient moins à la surveillance de nombreux dossiers ou au pilotage simultané de paramètres ; ce n’est pas un terminal de marché.

## Deux références visuelles effectivement examinées

Recherche réalisée par `alphaforge_app.decision.research._aws_search`, route AWS existante, puis lectures HTTP et captures Chromium locales. Les réponses et reçus sont conservés dans `docs/directions_artistiques/proofs/references/folio/*-search.json`. Aucune inférence de service de design.

| Référence vérifiable | Examen réel et version | Ce qui est retenu | Application et limites |
|---|---|---|---|
| Financial Times, [Visual Vocabulary](https://ft-interactive.github.io/visual-vocabulary/) | Page HTTP 200, texte intégral de la page d’entrée lu, écran rendu à 1440 × 1100 inspecté visuellement le 15 novembre 2026. Page évolutive non numérotée ; empreinte HTML conservée dans `ft-http.json`. | Choisir la représentation selon la relation à examiner ; texte et graphique se complètent. L’introduction précise que la collection n’est ni exhaustive ni un assistant automatique. | La comparaison repose sur un tableau de montants et une barre de composition. Deux chocs sans probabilités ne deviennent pas une distribution, une courbe de rendement ou une frontière. Cette ressource est un guide professionnel ; son esthétique ne prouve pas l’utilisabilité de Folio. |
| [Emergence Magazine](https://emergencemagazine.org/) | Page HTTP 200, texte d’accueil lu, premier écran rendu à 1440 × 1100 inspecté visuellement le 15 novembre 2026 : composition pleine page, matière d’archive photographiée, titre de revue et navigation limitée. Version web courante, promotion du volume 7. Empreinte dans `emergence-http.json`. | Un objet éditorial peut faire sentir la matière et ménager une hiérarchie forte sans multiplier les panneaux. | Folio traduit cet esprit en papier, marges, serif et annotation originale. Aucun média, logo, extrait graphique ni composition exacte n’est repris. Le produit observé est un magazine culturel : aucune efficacité financière ou accessibilité transférable n’est présumée. |

Captures : `docs/directions_artistiques/proofs/references/folio/ft.png`, `emergence.png`. Les premières captures prises avant stabilisation étaient blanches ; elles ont été remplacées après attente du rendu et des fontes, puis réellement regardées. Le code du site de référence n’a pas été réutilisé. Les droits de reproduction de leurs médias n’ont pas été qualifiés ; aucun de ces médias n’est embarqué.

Les fontes locales **Newsreader** et **DM Sans** sont celles déjà fournies par le prototype. Leurs fichiers de licence OFL et leur provenance restent dans `prototype/prompt6/assets/`. Aucun téléchargement de fonte, abonnement ou service tiers supplémentaire à l’exécution.

## Composition et système visuel

| Élément | Décision |
|---|---|
| Typographie éditoriale | Newsreader pour les titres, résultats et légendes majeures ; DM Sans pour les actions, unités, paramètres et traces. Les nombres importants ne sont pas écrits dans une image. |
| Couleurs | Papier `#eee9dd`, encre `#20372c`, annotation `#a33726`, texte secondaire `#596257`. Les états admissible/non admissible portent également un mot et un signe. |
| Structure | Masthead de revue, trois chapitres, deux niveaux de lecture ; grille de marges pour les preuves ; filets plutôt que surfaces arrondies. |
| Graphique | Barre de composition générée par le contrôleur à partir des poids réels, avec noms et pourcentages ; même information dans la légende. Les pertes sont des montants exacts dans un tableau. |
| Preuve | Panneau natif `dialog` en marge droite : contexte conservé, fermeture Escape, retour au déclencheur. |
| Correction | Page « Erratum », encre rouge et formulaire de valeurs explicites. Le bouton d’exemple prépare la saisie ; la soumission déclenche seule le calcul. |
| Responsive | La marge devient une bande de notes ; les grandes colonnes s’empilent ; seule la planche comparative défile horizontalement dans une région nommée. |
| Mouvement | Aucun spectacle de progression. Attente textuelle pendant la requête réelle. Réduction des mouvements respectée. |

## Adaptation qui change réellement la lecture

| Invariant | Lecture essentielle | Lecture approfondie |
|---|---|---|
| Même Robert, même archive, mêmes calculs | Question et grand résultat en premier ; explication contrastive et réserve sur la référence simple immédiatement ensuite. | Bande de résultat condensée, paramètres du mandat, objectif et contraintes avant la répartition. |
| Même minimum et même comparaison indépendante | « La simplicité fait aussi bien » est expliquée en prose. | Le minimum est relié à l’objectif `capital × ½ Σ |poids − poids initiaux|`, aux contraintes et aux chocs. |
| Même portée | Aucun rendement promis, réserve abstraite et limites maintenues. | Hypothèses, tableau des chocs, contrôles et sources accessibles sans retirer les limites communes. |
| Même capacité d’action | Comparer, ouvrir une preuve, corriger et annuler. | Les mêmes actions ; ordre de lecture centré sur l’examen de la méthode. |

Le niveau de lecture ne modifie ni les faits financiers ni les résultats. Aucun lien n’est inféré entre âge, richesse, compétence ou tolérance au risque.

## Contrat entre affichage et comportement

| Interaction | Source et transformation réelles |
|---|---|
| Ouvrir Robert | `/api/prototype/cases/robert`, archive r5 ; minimum de 30 000 CAD produit précédemment par le moteur. |
| Ouvrir un chiffre | `data-proof="minimum_reallocation"` ; affirmation, pointeurs de résultat, contrôles et export du contrôleur partagé. |
| Comparer | `options(s)` : portefeuille initial, minimum, autre minimum lorsqu’il existe et référence simple indépendante lorsqu’elle est disponible. |
| Choisir une répartition | `data-action="select"` ; seule la répartition inspectée change, aucun optimum ne se substitue silencieusement au dossier. |
| Corriger le retrait | `revisionForm(s)` et POST `/api/prototype/explore` ; copie locale, vrai calcul Python, aucune nouvelle invocation d’agent. |
| Voir la révision | `delta(s)` est présenté directement en tête de la comparaison après calcul : avant, après, écart, entrées conservées et calculs réexécutés. |
| Annuler | Historique local du contrôleur ; état précédent restauré. Il n’est pas présenté comme un effacement de l’archive. |
| Examiner une autre archive | Sélecteur r5/r10/r15 ; mention de résultat précalculé. Aucun calcul ou agent relancé pour cette navigation. |
| Examiner les agents | Contributions et traces de l’archive ; en variante locale, le panneau précise qu’aucun agent n’a été relancé. |

Le partage d’un contrôleur identique entre les directions rend la comparaison visuelle plus honnête. Il n’y a ni moteur alternatif, ni résultat numérique codé spécialement pour cette page.

## Vérifications et limites

Les résultats sont consignés dans `docs/directions_artistiques/proofs/references/folio/verification.json`, avec un script reproductible `verify.cjs`. Captures desktop, lecture approfondie, planche, erratum, révision calculée et mobile dans le même répertoire.

Le parcours de vérification examine le minimum r5, l’ouverture/fermeture de preuve et le retour du focus, l’invariance lors du changement de niveau, la sélection de la référence simple, le retrait à 40 000 CAD et son vrai recalcul, la différence immédiatement visible, l’annulation, puis l’archive r15 sans inventer un témoin de multiplicité. Les débordements sont contrôlés à 390 et 320 pixels.

La revue indépendante de l’auteur d’Isobare a établi deux défauts : une interprétation d’optimum persistait après un retrait impossible de 120 000 CAD, et le titre « sans tout déplacer » restait affiché quand un budget de perte nul obligeait à déplacer les 100 000 CAD. Les deux textes sont désormais conditionnés au résultat réel. Ces deux cas ont été recalculés et recontrôlés ; traces dans `docs/directions_artistiques/proofs/references/folio/correction-verification.json`. Les régions complémentaires ont reçu des noms accessibles et les limites essentielles ont été portées à 13 px. Le contrôle ciblé des régions ne relève plus de violation. La texture rend une partie du contrôle automatique de contraste indéterminée ; les couleurs de base ont été contrôlées indépendamment par le relecteur.

La validation visuelle humaine de cette direction reste attendue. Ce prototype n’intègre pas de branches persistantes, de nouveau dialogue de qualification, de langue supplémentaire, de glossaire adaptatif ou de modification du dossier principal. Les archives et les calculs locaux restent distingués. La facilité de compréhension doit encore être jugée par l’utilisateur ; une belle mise en page n’est pas une preuve de qualité de décision.
