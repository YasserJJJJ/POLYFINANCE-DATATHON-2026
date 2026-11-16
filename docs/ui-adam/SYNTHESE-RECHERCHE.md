# Recherche d'interface — synthèse

15 novembre 2026, branche `ui-adam` (créée depuis `2ba71af`). Le journal détaillé des références est dans `recherche/` : chaque ligne dit ce qui a été réellement ouvert et ce qui ne l'a pas été.

## Méthode

Neuf difficultés, réparties en trois recherches menées en parallèle. Pour chacune : question, solutions existantes, fonctionnement concret, pertinence pour nous, hypothèse de conception, puis confrontation au parcours réel dans les cinq prototypes.

| Recherche | Difficultés | Journal |
|---|---|---|
| 1 | restitution d'un verdict, comparaison avant/après, manipulation d'un paramètre, incertitude, niveaux de lecture | `recherche/recherche-1-restitution.md` (21 lignes, 12 pages consultées) |
| 2 | provenance, travail des agents, chargement et reprise, historique et réversibilité, résultat périmé, nature des champs | `recherche/recherche-2-provenance.md` (24 lignes, 20 pages consultées) |
| 3 | matières visuelles, composants libres et licences, polices, accessibilité | `recherche/recherche-3-matieres.md` (30 lignes, 25 consultées) |

## Outils réellement utilisés

| Capacité | Usage |
|---|---|
| Recherche web et ouverture de pages | les trois journaux |
| Dépôt Git et moteur du produit, exécutés hors ligne | 45 analyses réelles servant de données communes |
| Preuves de la tranche 4 de la fusion | appels Bedrock réels (identifiants, jetons, latences) |
| Navigateur intégré | inspection des prototypes sur ordinateur et à 375 px |
| Cinq réalisations en parallèle | un prototype par direction, sur le même socle |

Non utilisés, et pourquoi : Figma, Canva, Adobe (connecteurs non autorisés dans cette session, et les prototypes devaient être manipulables, pas dessinés) ; aucune bibliothèque externe (les prototypes s'ouvrent hors ligne). Aucune dépense engagée.

## Limites de la recherche, à connaître

- Les pages ont été lues par un outil qui en rend un résumé, pas le texte brut.
- Plusieurs sources voulues n'ont pas pu être ouvertes : NYT (bloqué), Bloomberg (403), Betterment (404), Vanguard (connexion requise), EUR-Lex pour le document d'informations clés (404). Aucun planificateur grand public ni terminal financier réel n'a donc été inspecté ; rien n'est cité à leur sujet.
- Aucune étude trouvée ne porte sur des particuliers lisant un historique de cinq ans : les hypothèses sur l'incertitude sont des transferts à tester.
- Le diff entre deux états et l'avant/après n'ont pas de source consultée : ce sont des propositions.

## Ce que la recherche a changé dans la conception

| # | Hypothèse retenue | Origine | Où elle est appliquée |
|---|---|---|---|
| 1 | Un résultat modifié devient **périmé** tout de suite, et n'est recalculé que sur action explicite | notebooks réactifs en mode différé (recherche 2) | socle : `proposer` puis `appliquer` ; les cinq prototypes |
| 2 | Trois statuts impossibles à confondre : analyse courante, aperçu, archive | historiques de versions (recherche 2) | socle : `statut()` ; les cinq prototypes |
| 3 | Les révisions ne s'effacent pas ; restaurer crée une nouvelle révision | Figma (recherche 2) | socle : `restaurer` |
| 4 | Annuler après coup plutôt que confirmer avant | A List Apart, GOV.UK (recherche 2) | Fil surtout |
| 5 | Le travail des rôles est un journal d'étapes réelles, code et modèle distingués, sans « réflexion » mise en scène | Google PAIR, WCAG 4.1.3 (recherche 2) | les cinq ; `relireTrace` est étiqueté « relecture » |
| 6 | Deux niveaux de divulgation, pas trois | Nielsen Norman Group (recherche 1) | verdict et raisons, puis preuve à la demande |
| 7 | Du chiffre à la référence en deux gestes ; pas de pourcentage de confiance | Google PAIR (recherche 2) | preuve dans les cinq |
| 8 | Le passé se marque dans le dessin : axe daté, fenêtre observée, aucun prolongement ; l'avertissement générique ne suffit pas | étude citée par la recherche 1, position de la FCA | graphiques des cinq |
| 9 | L'écart apparié est le message, pas le niveau | recherche A de la fusion, raisonnement de conception | Épure en fait son principe ; présent partout |
| 10 | La phrase du verdict peut porter ses propres réglages | Bret Victor (recherche 1) | Carnet |
| 11 | La frontière du verdict se trace dans la grille, avec libellé et forme, jamais la couleur seule | recherche 1 | Relief |
| 12 | « Indéterminé » est un vrai résultat, avec sa raison et ce qui le lèverait | recherche 1 | les cinq |
| 13 | Écran « ce que nous avons compris », une nature par ligne ; un inconnu n'est jamais comblé en silence | GOV.UK (recherche 2) | socle : `profilLignes` ; les cinq |
| 14 | Texte jamais posé sur une texture ; grain statique ; éléments natifs (`dialog`, `range`, `details`) plutôt que des bibliothèques | WCAG 2.2, recherche 3 | les cinq |

Écartés : pourcentage de confiance affiché (trompeur ici) ; troisième profil de lecture « technique » séparé (le Pupitre le porte comme direction entière) ; affichage de l'incertitude en fréquences sur de nombreuses fenêtres (le moteur n'en calcule que trois, on montre celles-là) ; caustiques d'eau et distorsion de lentille (aucune technique légère fiable, et aucun usage qui les justifie).

## Composants libres examinés

| Composant | Licence lue sur le dépôt | Décision |
|---|---|---|
| Tufte CSS | MIT | idée reprise (notes de marge), code réécrit : il masque les notes sur petit écran |
| d3-contour, Observable Plot | ISC | écartés des prototypes (aucune dépendance) ; candidats si Relief est retenu |
| uPlot | MIT | candidat pour les courbes en production |
| cmdk | MIT, exige React 18 et Radix | candidat pour le Pupitre en production ; `dialog` natif dans le prototype |
| ninja-keys | MIT, dépend de Lit | écarté |
| img-comparison-slider | MIT | écarté : un `input type=range` natif suffit |
| Source Serif, IBM Plex, JetBrains Mono, Inter | OFL-1.1 | à embarquer si la direction retenue en a besoin ; piles système dans les prototypes |

Le texte des fichiers de licence n'a pas été lu, seulement la mention sur la page du dépôt.

## Constats sur le produit faits en chemin

1. Le gabarit du produit écrit les mesures avec six décimales (« −20,595922 % »). Les prototypes arrondissent à l'écran et gardent la valeur exacte dans la preuve. À corriger dans le Rédacteur quelle que soit la direction retenue.
2. Amira est « incohérente » à tous les montants, même 500 $ : son portefeuille fictif dépasse déjà sa capacité de perte, et toute part de Bitcoin l'aggrave un peu. C'est fidèle à la règle K5, mais la grille n'a alors plus rien à montrer. C'est une décision de produit, pas d'interface.
3. Le produit n'a ni historique ni état conservé. L'historique des prototypes vit dans le navigateur ; l'intégrer demandera de décider où il vit vraiment.
4. Un dossier détaillé n'existe que pour l'horizon déclaré : la grille montant × horizon ne donne que des états. Relief le dit à l'écran.
