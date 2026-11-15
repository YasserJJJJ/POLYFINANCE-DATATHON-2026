# Folio — système visuel réalisé

[Comparaison avec le prototype choisi](proofs/final/fidelite-folio.png) : même dossier Robert, même minimum, captures 1440 × 1000. L’intégration ajoute une barre des pièces et le statut d’archive ; elle conserve composition, typographie, matière et contrepoint.

## Grammaire

Newsreader pour la lecture éditoriale, les grands résultats et les annotations ; DM Sans pour actions, unités et formulaire. Fontes locales, licences OFL dans `alphaforge_app/static/folio/fonts/`. Aucun média de référence copié.

Papier `#eee9dd`, papier clair `#f6f2e8`, encre `#20372c`, secondaire `#596257`, rouge d’annotation `#a33726`, filets `#b7b9a8`. Les variables sont définies dans `style.css`. Grain de papier et contours SVG sont décoratifs : ils n’encodent ni risque ni rendement.

Les filets organisent la page ; la marge apporte les renvois, le texte central développe une raison et l’annotation pose un contrepoint. Le grand nombre est un lien vers sa preuve, accompagné de son unité et de sa portée. La référence simple est rappelée au voisinage du minimum lorsqu’elle est disponible.

## Composants et usages

| Élément | Usage |
|---|---|
| Masthead + chapitres | Orientation dans un dossier ; Comprendre, Comparer, Réviser. |
| Appareil de lecture | Profil, Étude, Historique, Recherche, Export ; accessible sans imposer quatre écrans d’agents. |
| Page d’ouverture | Bibliothèque éditoriale, recherche textuelle, demandes fictives ; ouverture d’un dossier sans résultat ancien visible sous sa nouvelle identité. |
| Double page / annotation | Demande et conclusion en regard ; contrepoint sous la conclusion ; note contextualisée. |
| Planche comparative | Mêmes unités, choix de l’option regardée, valeurs ouvrant leur preuve. Pas de graphique probabiliste avec deux chocs. |
| Figure historique | Courbes issues des séries effectives, axe CAD et dates ; styles de trait distincts et tableau des métriques. Vue mobile à axes lisibles, sans changer la série. |
| Erratum | Formulaire explicite : provenance, unité, effet ; aperçu, variante et correction séparés. Une réponse à une qualification incomplète propose la correction par les agents. |
| Marge documentaire | `dialog` natif, contexte conservé, Escape et focus de retour ; passages, métriques, hypothèses et artefacts. |
| Révision | Tableau avant/après ; résumé des dépendances ; identifiants détaillés à la demande. |
| États ouverts | Inconnue explicitement nommée ; questions humaines regroupées, tâches de recherche séparées. Pas de réserve abstraite supposée lorsque sa nature manque. |

Les composants existent dans `render.js` et `shared.js`, le comportement dans `controller.js`. Les préférences de lecture sont séparées du profil financier.

## Contrôles et critique

Captures finales inspectées : Robert essentiel/profond, comparaison, preuve, révision ; Amira historique/variante/mobile ; profil incomplet et impossibilité. La composition conserve son identité en niveaux de gris par la typographie, les filets, la marge et les différentes densités de lecture.

Corrections visuelles et d’usage : hiérarchie des titres, focus programmatique non décoratif, régions de tableaux accessibles au clavier, axes mobiles lisibles, numéros liés à la bonne métrique, libellés financiers humains dans le profil, provenance ouverte par annotation. Les détails structurés conservent leurs identifiants et valeurs originaux.

[Contrastes calculés](proofs/final/contrastes.json) et [vérification navigateur](proofs/final/verification.json). Le mouvement réduit est respecté ; aucun mouvement ne prétend représenter une activité d’agent. Ces contrôles ne remplacent pas l’essai humain de l’expérience.

Les références décisives restent celles du [prototype Folio](../directions_artistiques/folio.md) et du [canvas initial](../experience/README.md) : principes retenus, niveaux de lecture et limites de transfert y sont conservés. L’intégration n’a pas nécessité de nouvelle identité ni de nouvel outil d’inférence externe.

Les montants longs ont un dimensionnement dépendant de leur longueur dans le titre, sans abréviation financière implicite. Le [contrôle à 320 px](proofs/final/grands-montants.json) conserve **300 000 000 CAD** en entier et les détails restent lisibles. Les rectangles d’une table défilante ou d’un SVG décoratif peuvent dépasser son cadre interne ; le contrôle de débordement porte aussi sur la largeur effective de la page.
