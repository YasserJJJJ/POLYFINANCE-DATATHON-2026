# Contrat commun — trois interprétations

La galerie et le contrôleur commun sont intégrés par le parent. Chaque direction
possède son HTML, son CSS et son module JS dans son propre répertoire.
L'ancien prototype et le moteur sont conservés.

## Modules

Importer depuis `../shared/experience.js` :

- `mount(render, {name})` : charge Robert r5, puis appelle `render(s)`, qui
  retourne le HTML de `#app`. Les changements sont gérés par délégation.
- `esc(value)`, `money(number)` (sans suffixe CAD), `pct(fraction)`.
- `options(s)` : options du calcul + référence simple indépendante lorsqu'elle
  existe, normalisées `{id,label,weights,turnover,losses:{actions,obligations},
  admissible,reference,raw}`.
- `allocation(option)` : répartition horizontale avec labels accessibles.
- `revisionForm(s)` : formulaire commun utilisable, styles locaux libres.
- `versionSelect(s)` : sélecteur des trois archives, états clairement précalculés.
- `delta(s)` : fragment présentant différences avec l'état précédent.
- `methodDetails(s)` : méthode, hypothèses, limites, liens vers preuves.
- `limits(s)` : limites déterminantes toujours visibles.

État `s` : `{v, archives, level:'accessible'|'deep', view:'overview'|'compare'|
'revise', selected:'minimum_turnover', local:false|receipt, previous:null|version,
history:[], busy:false,error:null, notice:null}`. `s.v` est une version projetée
de `/data/cases.json` : `.problem`, `.analysis`, `.stats`, `.proofs`, `.source`,
`.simple_reference`, `.limits`.

## Interactions déléguées

Boutons :
`data-action="view" data-view="overview|compare|revise"`,
`data-action="level" data-level="accessible|deep"`,
`data-action="select" data-option="minimum_turnover|alternative_minimum|simple_reference|baseline"`,
`data-action="proof" data-proof="minimum_reallocation|sources|method|agents"`,
`data-action="undo"`, `data-action="reset"`.

Le sélecteur `data-version-select` navigue les archives r5/r10/r15.
Le formulaire `data-scenario` contient `name="withdrawal_cad"` et
`name="scenario_loss_limit_cad"`, numériques, pas de curseurs implicites.
Submit lance le moteur existant sur une copie, sans dossier ni agents.
Le bouton `data-action="draft"` data-withdrawal="40000" remplit seulement
le formulaire. Le rendu doit maintenir un titre principal `h1`.

Une boîte de preuve native `<dialog>` est injectée après #app et gérée par
le module commun (focus, Escape, sources, téléchargements). Ses styles
locaux sont libres avec `.evidence-dialog`, `.proof-content`, `.proof-close`.

## Invariants

Même Robert r5 à l'entrée ; 100 000 CAD ; retrait 30 000 à 12 mois ; budget
15 000 par choc ; TSLA ≤10 % initialement. Minimum 30 000 CAD. La référence
simple atteint aussi ce minimum ; le premier optimum n'est pas le moins
risqué. Pas de probabilities ni de garantie du capital. Chocs hypothétiques,
réserve abstraite, frais/impôts/inflation exclus, fractions admises. Quatre
ans déclarés ne sont pas quatre ans simulés. Les deux niveaux conservent
ces informations. r15 n'a pas de témoin de multiplicité.

Les graphismes originaux sont déterministes. Aucune inférence auxiliaire.
Chaque direction explique matière + composition sans présenter de décor
comme une donnée financière.
