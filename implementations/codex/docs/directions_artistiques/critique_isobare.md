# Revue indépendante ciblée — Isobare

**[Ouvrir Isobare](http://127.0.0.1:8770/directions/isobare/)**. Revue effectuée par l’auteur de Folio, qui n’a écrit ni les fichiers Isobare ni le contrôleur commun. Aucun fichier Isobare n’a été modifié par ce relecteur.

Périmètre : pages réellement rendues, transitions communes, restitution financière, clavier, invariance des deux présentations et cas impossible. Le moteur financier n’est pas réaudité intégralement ici. Script et résultats : [review.cjs](proofs/critique_isobare/review.cjs), [results.json](proofs/critique_isobare/results.json). Captures desktop, mobile, lecture instrumentée, preuve et impossibilité dans le même répertoire.

## Ce qui tient à l’examen

- Robert r5 montre bien **30 000 CAD**, et la règle simple atteignant ce minimum est explicitement présentée comme contrepoint indépendant.
- Les pertes sont rattachées aux deux chocs hypothétiques ; le graphique n’invente ni trajectoire ni probabilité. Cercle et carré complètent la distinction par trait plein/pointillé. Le tableau donne les valeurs exactes.
- Le changement de niveau conserve exactement le même objet profil, les mêmes statistiques et les mêmes options. La lecture instrumentée introduit la méthode avant la comparaison : c’est une modification réelle de hiérarchie.
- L’ouverture d’une preuve, sa fermeture par Escape et le retour du focus au déclencheur fonctionnent.
- Un retrait de **120 000 CAD** déclenche le moteur réel : le champ de minimum est absent, zéro option est produite et les statistiques portent un déficit de **20 000 CAD**. Après la correction de formulation de l’auteur, le texte confirme qu’aucun minimum ni allocation admissible n’est établi.
- Le retour à l’état précédent restaure **30 000 CAD**. La variante est clairement distinguée d’une archive et aucun faux agent en cours d’exécution n’est montré.
- Les documents font 390 et 320 pixels de large aux mêmes tailles de viewport : aucun débordement global. Graphique et tableau disposent de régions de défilement local.

## Observations, impact et corrections

| Observation vérifiable | Impact | Correction et état |
|---|---|---|
| Le titre initial « Même mouvement » accompagnait un graphique comprenant le portefeuille initial, qui déplace 0 CAD, et des options déplaçant 30 000 CAD. | Une égalité visuelle était annoncée pour des valeurs différentes. | Remplacé par l’auteur par **« Même question. Pertes différentes. »** ; confirmé dans la capture desktop. Le terme « pertes » est préférable à « risques », car il décrit les deux scénarios effectivement mesurés. |
| `result(s)` énonçait initialement « Le minimum réduit le capital déplacé » même en absence de résultat. | Un dossier impossible conservait le récit d’une résolution. | Conditionnement ajouté par l’auteur. Test réel 120 000 CAD et capture `impossible.png` confirment le texte **« Aucun minimum ni allocation admissible établis »**. |
| Première CSS inspectée : limites à 10 px ; états graphiques à 7 px ; plusieurs contrôles mobiles à 8–10 px. Après première correction, taille calculée des limites = 12 px, légende des chocs = 10 px, en-têtes du tableau = 8 px. | La densité instrumentale gêne la lecture des unités et la distinction des pertes, surtout sur téléphone ; ce n’est pas un défaut de contraste. | L’auteur a augmenté les limites et plusieurs annotations. Demande ciblée restante au moment de la mesure : porter les légendes et en-têtes nécessaires à l’interprétation à environ 12 px, tout en conservant les repères décoratifs plus discrets. |
| Axe 4.14.0 signale `landmark-unique` sur `.controls` et `region` sur `.subtop`. | Les deux colonnes complémentaires ne sont pas nommées distinctement au lecteur d’écran ; l’état du dossier se trouve hors des régions de navigation. | Nommer les `aside` « Paramètres du dossier » / « Registre de preuve » et donner une région nommée au bandeau. Signalé à l’auteur. |
| Dans le **composant partagé** `methodDetails(s)`, le dossier impossible affichait encore « Nature du résultat : Optimum conditionnel d’un programme linéaire ». | La section méthodologique contredit l’absence d’optimum pourtant correctement affichée plus haut. | Correction annoncée par le responsable du contrôleur : certificat retrait ≤ réserve ≤ capital et déficit de 20 000 CAD, sans optimum prétendu. Le recontrôle ciblé est confié à l’autre relecteur via Folio pour éviter de dupliquer le test partagé. |
| La ligne technique « minimiser ½ × Σ |w − w₀| » présente un objectif en fraction du capital, tandis que la sortie est en CAD. La méthode détaillée fournit correctement le facteur `Capital ×`. | Les deux expressions ont le même optimum pour un capital constant positif, mais l’échelle du résultat n’est pas la même. | Amélioration mineure : écrire « fraction de capital » dans le bandeau ou inclure le facteur Capital. Aucun chiffre faux n’a été observé. |

## Contraste et appréciation visuelle

Le langage d’instrument est cohérent : grille de mesure, colonnes latérales, chiffres monospaces, formes graphiques sobres. Les preuves restent visibles en marge et la limite de la référence simple est proche du résultat. Cette densité offre un avantage pour examiner rapidement plusieurs montants ; elle demande davantage d’attention qu’une page narrative.

Axe ne relève aucune violation de contraste dans ce passage, mais **55 nœuds restent incomplets** pour cette règle, notamment dans les zones tramées/SVG. Ce résultat ne vaut donc pas certificat. Un calcul indépendant des couleurs de base donne :

| Texte / fond | Ratio |
|---|---:|
| Encre `#132d30` / papier `#d2e7e4` | 11,27:1 |
| Secondaire `#36585a` / papier `#d2e7e4` | 6,03:1 |
| Encre / panneau `#e7f1ec` | 12,58:1 |
| Secondaire / panneau | 6,74:1 |

Ces ratios sont consignés dans [contrasts.json](proofs/critique_isobare/contrasts.json). Ils couvrent les aplats, pas chaque effet de texture ou d’anticrénelage. L’objection principale restante porte sur le corps des petites légendes, pas sur les couleurs.

## Portée de la conclusion

La direction ne masque pas le contrepoint financier central et résiste aux transitions effectivement exercées. Les corrections demandées sont ciblées : suppression de deux formulations excessives, lisibilité de certains repères, noms accessibles et cohérence du texte méthodologique partagé. La compréhension d’un utilisateur humain et la préférence entre cette densité et les autres directions restent à valider.
