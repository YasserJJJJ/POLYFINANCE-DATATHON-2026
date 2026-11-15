# Isobare — un instrument pour comparer

**Ouvrir : http://127.0.0.1:8770/directions/isobare/**

Isobare transforme le dossier en instrument de mesure : entrées à gauche,
champ de comparaison au centre, registre des preuves à droite. Les filets,
les graduations et les annotations définissent l'espace ; aucun empilement
de cartes arrondies. Les graphismes sont écrits en SVG et CSS, sans image
produite par un modèle. La direction reste un prototype à valider.

## Deux références réellement examinées

| Référence | Lecture réelle et droits | Principe retenu | Application et limites |
|---|---|---|---|
| Charles Joseph Minard, *Carte figurative des pertes successives en hommes de l'Armée française dans la campagne de Russie*, 1869 ; [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Minard.png) | Page consultée par HTTP, image téléchargée puis vue ; notice domaine public lue. [Image examinée](proofs/references/isobare-minard.png). | Les nombres et annotations restent proches des marques visuelles ; les dimensions partagent un repère explicite. | Les pertes des options sont comparées sur une même échelle, avec chiffre à l'extrémité. La carte historique n'est ni un modèle de finance ni une preuve d'utilisabilité. Aucun trajet ou surface ne simule une donnée absente. |
| Elborgo, photographie *Tektronix 465 Oscilloscope*, 1er octobre 2007 ; [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Tektronix_465_Oscilloscope.jpg) | Page et licence lues, façade téléchargée et vue. Licence [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) proposée, également GFDL. [Photo examinée, inchangée](proofs/references/isobare-oscilloscope-front.jpg). | Champ de mesure central quadrillé ; contrôles organisés par fonction ; unités locales ; distinction entre réglage et résultat. | Paramètres financiers regroupés à gauche, comparaison centrale, preuves accessibles sans changer de dossier. Aucun faux cadran ou oscilloscope animé : des boutons rotatifs simulés réduiraient la précision des montants. La photographie n'est pas embarquée dans le prototype. |

Les trois recherches ont utilisé `bedrock-agentcore.InvokeWebSearch`, profil
`alphaforge`, sans WebAnswer. Reçus :
[recherche Minard](proofs/references/isobare-search-1.json),
[recherche CERN](proofs/references/isobare-search-2.json),
[recherche Tektronix](proofs/references/isobare-search-3.json).
[Route de cette branche](proofs/references/isobare-route.json) :
`amazon-bedrock-runtime` reconfirmé dans `session_meta`.

Deux divergences d'image ont été détectées visuellement. L'image obtenue
depuis la page CERN montrait une bibliothèque et des terminaux, pas les
écrans de la salle de contrôle annoncée ; elle n'a pas servi de référence.
Le fichier `Tektronix465.jpeg` montrait un circuit interne ; la recherche
a été poursuivie jusqu'à une photographie montrant réellement la façade.
Ces observations justifient la consultation visuelle après récupération,
plutôt que l'adoption du seul intitulé. Aucune licence CERN n'est supposée.
Les références sont esthétiques et fonctionnelles, sans validation utilisateur.

## Système visuel

- **Matière :** papier technique cyan très pâle `#d2e7e4`, encre `#132d30`,
  panneaux secondaires `#e7f1ec`, repère de sélection ivoire `#f1f4d7`.
- **Composition :** trois travées orthogonales, bordures continues,
  résultats en grands chiffres, marges de mesure homogènes. À moins de
  1180 px, le registre passe sous le champ. À 390 px, le résultat précède
  les contrôles pour rester immédiatement accessible.
- **Typographie :** chiffres et annotations en polices monospace système ;
  titres condensés en Impact/Arial Narrow avec repli sans-serif. Aucun appel
  externe de police. Les chiffres alignés facilitent la comparaison.
- **Marques :** segment plein et point pour le choc actions ; segment
  discontinu et carré ouvert pour le choc obligations. La distinction
  persiste en gris. La réserve de la barre de répartition est hachurée.
- **Mouvement :** aucune animation décorative, aucune progression simulée.
  L'état de chargement reflète le calcul ou la lecture effective.
- **Ton :** énoncés courts et unités locales. « Conditionnel » reste visible,
  sans prétendre que le modèle minimise le risque.

## Deux niveaux, mêmes chiffres

| | Lecture directe | Lecture instrumentée |
|---|---|---|
| Entrée principale | Minimum à réallouer et condition de financement | Équation objectif en tête, résultat condensé |
| Priorité suivante | Contrepoint de la règle simple puis pertes comparées | Formulation, contraintes, matrice des chocs et accès aux contrôles avant le graphique |
| Comparaison d'entrée | Minimum, règle simple, portefeuille initial | Toutes les options calculées et la règle simple |
| Détail | Preuves en boîte native, composition après sélection | Même preuve et composition, données d'hypothèses visibles dans la page |
| Invariants | Montants, chocs, limites, portée de la référence simple | Strictement identiques |

Le changement de niveau ne déclenche aucun appel de calcul. Le profil
financier est séparé de cette préférence d'affichage. Une modification du
retrait déclenche le moteur existant sur une copie, clairement étiquetée.

## Parcours et correspondance technique

| Action | Donnée ou comportement réel |
|---|---|
| Lire 30 000 CAD | `s.v.stats.min_reallocation_cad`, Robert r5 ; pas de nombre recopié dans le code |
| Comparer les pertes | Options normalisées par le contrôleur commun, unités CAD, même échelle partant de zéro |
| Examiner la règle simple | Preuve indépendante bornée à r5, absente d'une variante locale |
| Sélectionner une option | Composition issue des poids de cette option ; pas de nouvelle recommandation |
| Ouvrir une preuve | Dialogue commun avec chemin JSON, valeur, hypothèses, contrôles et empreintes |
| Préparer 40 000 CAD | Modifie le brouillon uniquement ; ne lance rien |
| Calculer | `POST /api/prototype/explore` ; aucune inférence, aucun agent relancé, dossier principal inchangé |
| Voir la révision | Comparaison avant/après placée juste après le résultat, avant les graphiques ; distinction archive/copie locale |
| Annuler | Restaure l'état précédent du contrôleur ; aucun historique produit écrasé |
| Examiner r15 | Archive distincte, aucune affirmation de multiplicité sans témoin |

`../shared/experience.js` gère l'état, les échanges, les preuves et le calcul.
Isobare possède uniquement son rendu, sa composition et ses styles. Aucun
module du moteur ni serveur n'a été changé pour cette direction.

## Vérification et limites

[Script ciblé](proofs/references/isobare-check.cjs) et
[résultats](proofs/references/isobare-checks.json) : quatorze contrôles
réussis, dont identité des chiffres entre niveaux, preuve et retour du focus
par Échap, comparaison de quatre options, retrait réel 40 000, zéro inférence,
annulation vers r5, r15 sans multiplicité inventée, absence d'erreur JavaScript
et de débordement global à 390 px.

Les captures [bureau](proofs/references/isobare-desktop.png),
[instrumentée](proofs/references/isobare-deep.png),
[révision](proofs/references/isobare-revision.png) et
[mobile](proofs/references/isobare-mobile.png) rendent la direction
inspectable. La direction et les références ont été examinées visuellement.

La densité fait partie du choix artistique : elle mérite un essai humain,
particulièrement pour des novices. Sur téléphone, graphiques et tableau
possèdent un défilement horizontal explicite et accessible au clavier ;
aucune donnée n'est supprimée pour gagner de la place. Le modèle reste celui
de Robert, sans frais/impôts/inflation ni projection à quatre ans. Aucun
résultat utilisateur ni bénéfice d'apprentissage n'est revendiqué à ce stade.
