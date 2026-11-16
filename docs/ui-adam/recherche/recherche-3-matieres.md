# Recherche 3 : matières, techniques et composants libres pour cinq prototypes

Date : 2026-11-15. Méthode : pages ouvertes via WebFetch (résumé produit par un petit modèle : les licences sont celles lues sur la page du dépôt, les tailles absentes sont marquées « non vérifié »). Les résultats de WebSearch seuls ne comptent PAS comme « consulté ». Aucun produit réel (Linear, Stripe, etc.) n'a pu être ouvert : voir « Limites de la recherche ».

## 1. Journal des références

| # | Lien | Élément inspecté | Apport | Limites | Licence | Usage (direction) | Décision | Statut |
|---|---|---|---|---|---|---|---|---|
| 1 | https://github.com/edwardtufte/tufte-css | README, fichiers | CSS seul pour sidenotes/marginnotes ; copier `tufte.css` + dossier `et-book` | « maintenu mais pas en développement actif » ; poids non indiqué | MIT | 1 Carnet | adapter (reprendre le principe, réécrire le CSS) | consulté |
| 2 | https://edwardtufte.github.io/tufte-css/ | démo, structure des notes | Sidenote = `label.margin-toggle` + `input` checkbox + `span.sidenote` ; masquées sur écran étroit, révélées par bascule | Libellé vide (numéro généré en CSS) ; accessibilité clavier/lecteur d'écran non traitée ; ⊕ seul comme indice | MIT (via #1) | 1 Carnet | adapter : remplacer par `<details>`/`aside` nommé | consulté |
| 3 | https://github.com/etbook/et-book (la page ouverte est un 404) puis https://github.com/edwardtufte/et-book | police ET Book | Serif de Tufte, webfont | Formats non listés ; jeu de caractères français non vérifié | MIT (dit « personnel et commercial ») | 1 Carnet | écarter (préférer Source Serif, plus complète) | consulté (le premier lien : 404) |
| 4 | https://github.com/d3/d3-contour | README | Marching squares sur grille numérique | Taille et dépendances non indiquées | ISC | 2 Relief | retenir en référence ; implémenter à la main si zéro dépendance exigée | consulté |
| 5 | https://d3js.org/d3-contour/contour | API | `contours().size([n,m]).thresholds([...])(values)` → MultiPolygon GeoJSON ; `values[i + j*n]` ; `smooth(true)` par défaut ; rendu par `d3.geoPath()` | Sortie GeoJSON : il faut convertir en `d` SVG (réécrire ~30 lignes de marching squares si pas de d3) | ISC (via #4) | 2 Relief | adapter | consulté |
| 6 | https://observablehq.com/@d3/contours | exemple isolignes | — | HTTP 429, non ouvert | n/a | 2 Relief | n/a | non vérifié |
| 7 | https://github.com/observablehq/plot | README | Bibliothèque SVG concise, marques en couches | Marque contour/densité non confirmée sur la page ; taille non indiquée | ISC | 2 Relief, 5 Épure | écarter pour prototype (dépendances) ; peut servir en production | consulté |
| 8 | https://github.com/leeoniya/uPlot | README | ~50 Ko min, canvas 2D, très rapide (chiffres de l'auteur, 1 machine, 2023) | Canvas : pas de DOM accessible, texte alternatif à fournir ; surdimensionné pour une grille 2D | MIT | 3 Pupitre (séries temporelles) | écarter pour l'instant | consulté |
| 9 | https://github.com/pacocoursey/cmdk | README | Palette de commandes, annonce accessibilité testée VoiceOver (revendication de l'auteur) | Requiert React 18 et Radix Dialog : inutilisable en HTML pur | MIT | 3 Pupitre | retenir pour la production React ; écarter pour prototype | consulté |
| 10 | https://github.com/ssleptsov/ninja-keys | README | Web component (Lit), clavier, thèmes, parties CSS, hors framework | Dépend de Lit ; poids non indiqué ; date de dernière activité non lue | MIT | 3 Pupitre | adapter si CDN acceptable, sinon écrire ~80 lignes (`<dialog>` + liste filtrée) | consulté |
| 11 | https://github.com/sneas/img-comparison-slider | README | Web component, <12 Ko min / <4 Ko gzip, `keyboard` activé par défaut, variables CSS, poignée personnalisable | Touches non documentées ; Custom Elements/Shadow DOM requis | MIT | 5 Épure | retenir (ou écrire un `<input type=range>` natif, plus accessible et sans dépendance) | consulté |
| 12 | https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/feTurbulence | attributs | `baseFrequency`, `numOctaves`, `stitchTiles`, `seed` ; espace linearRGB par défaut | La page ne donne ni exemple ni avertissement perf. (le croquis de grain ci-dessous vient de mes connaissances, non testé) | n/a | 1, 4 | retenir | consulté |
| 13 | https://master.dev/blog/pure-css-halftone-effect-in-3-declarations/ (redirige vers blog.master.dev) | code | Trame : `radial-gradient` + `linear-gradient` + `background-blend-mode: multiply` + `filter: contrast(16)` | Gris de départ ≥ #777 ; gros points flous ; Firefox/`filter()` partiels ; points non ronds avec distorsion | licence du code non indiquée | 4 Fil, 1 | adapter | consulté |
| 14 | https://joshwcomeau.com/css/backdrop-filter | pièges | Échantillonne seulement l'arrière-plan direct ; bords tronqués ; scintillement en haut ; flou + texte = lisibilité à protéger par fond semi-opaque ; bug Firefox sticky | Pas de chiffres de performance | n/a | 4 Fil (verre cannelé) | retenir (pièges) | consulté |
| 15 | https://en.wikipedia.org/wiki/Ordered_dithering | formule | Matrice de Bayer 4×4 = 1/16·[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]] ; `c' = palette(c + r·(M[x mod n][y mod n] − ½))` ; sans branchement, motif lié à l'écran | Encyclopédie ; pseudo-code (le nôtre) non vérifié à l'exécution | CC BY-SA (contenu) | 4 Fil, 3 Pupitre | retenir | consulté |
| 16 | https://github.com/adobe-fonts/source-serif | README | Dossiers OTF/TTF/VAR/WOFF/WOFF2 | Taille des fichiers non lue | OFL-1.1 | 1 Carnet | retenir | consulté |
| 17 | https://github.com/IBM/plex | README | Sans, Serif, Mono, Condensed, vrais italiques ; zips en Releases ; npm `@ibm/plex-*` | WOFF2 non confirmé sur la page | OFL-1.1 | 3 Pupitre, 5 Épure | retenir | consulté |
| 18 | https://github.com/JetBrains/JetBrainsMono | README | Mono, 8 graisses + italiques, variante NL sans ligatures, variable .ttf, woff2 via script | Section Releases vide sur la capture ; lien direct variable woff2 non donné | OFL-1.1 (police) ; Apache-2.0 (code) | 3 Pupitre | adapter (alternative à Plex Mono) | consulté |
| 19 | https://github.com/undercasetype/Fraunces | README | Variable : opsz 9–144, wght 100–900, SOFT, WONK | Pas de téléchargement direct ni de release ; construction par `make build` ; mention « bientôt sur Google Fonts » peut être périmée | OFL-1.1 | 1 Carnet (titres) | écarter pour le prototype (obtention pénible) | consulté |
| 20 | https://github.com/rsms/inter | README | Variable, chiffres tabulaires, zéro barré | WOFF2 non mentionné ; nom réservé | OFL-1.1 | 4 Fil | retenir | consulté |
| 21 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | 1.4.3 | 4,5:1 normal, 3:1 grand (≥ 24 px, ou ≥ ~18,5 px gras) ; échec F83 pour image de fond insuffisante | Pas de règle « pire zone » écrite (c'est une prudence de ma part) | n/a | toutes | retenir | consulté |
| 22 | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | 2.5.8 | 24×24 px (AA) ; 44×44 px cité comme « 2.5.5, plus strict » ; exceptions espacement/en ligne | Niveau AAA de 2.5.5 non écrit sur la page (connaissance générale) | n/a | 4 Fil surtout | retenir : viser 44–48 px | consulté |
| 23 | https://www.w3.org/WAI/WCAG22/Understanding/reflow.html | 1.4.10 | 320 px de large (= 1280 px à 400 %) sans défilement 2D ; exceptions : tableaux de données, cartes, diagrammes | L'exception ne couvre que la zone concernée, pas le pourtour | n/a | 2, 3, 5 | retenir | consulté |
| 24 | https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html | 2.4.13 | Existe en WCAG 2.2, niveau AAA | 2.4.11 (AA, focus non masqué) non couvert par cette page | n/a | toutes | retenir comme objectif | consulté |
| 25 | https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion | syntaxe | Remplacer le mouvement d'échelle/panoramique par un fondu ; « Baseline » depuis janvier 2020 | Page longue, fin non lue | n/a | toutes | retenir | consulté (partiel) |
| 26 | https://www.bloomberg.com/company/stories/how-bloomberg-terminal-ux-designers-conceal-complexity | principes Terminal | Seul le résumé de WebSearch : gestion de la densité, cohérence « religieuse », clavier, couleurs avec CVD (~20 000 utilisateurs) | Page : HTTP 403, non ouverte ; citations de seconde main | n/a | 3 Pupitre | retenir l'idée, vérifier plus tard | non vérifié |
| 27 | https://www.nngroup.com/articles/mobile-cards/ | cartes mobiles | — | HTTP 404 (URL probablement fausse) ; ne pas citer NN/g | n/a | 4 Fil | n/a | non vérifié |
| 28 | https://css-irl.info/css-halftone-patterns/ ; https://leanrada.com/notes/pure-css-halftone/ | trames CSS | Apparus dans WebSearch comme tutoriels de trame | Non ouverts | non vérifié | 4 Fil | à ouvrir si #13 insuffisant | non vérifié |
| 29 | https://www.shadcn.io/shaders/fluted-glass-shader | verre cannelé | Résultat de recherche : indique que le CSS (`backdrop-filter` + masque en dégradé répété) est l'approximation la plus proche sans shader | Non ouvert, pas de code | non vérifié | 4 Fil | à ouvrir | non vérifié |
| 30 | https://tympanus.net/codrops/?p=97026 (Bayer WebGL) | dither shader | Résultat de recherche seulement | Non ouvert ; WebGL = hors périmètre léger | non vérifié | 4 Fil | écarter (canvas 2D suffit) | non vérifié |

## 2. Techniques par matière (CSS/SVG/canvas pur)

**Grain (grainy gradients, noise, paper).** Filtre SVG `feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" stitchTiles="stitch"` + `feColorMatrix` (saturation 0), enregistré en data-URI SVG et posé en `background-image` d'un pseudo-élément `::before` en `mix-blend-mode: multiply`, `opacity: .06–.12`, `pointer-events: none`. Source : MDN (#12) pour les attributs ; le croquis est de moi, non testé. Coût : le filtre est rastérisé une fois si l'élément est statique ; ne JAMAIS animer `baseFrequency`/`seed`. Piège : le bruit sur de grandes surfaces coûte au premier rendu sur mobile ; préférer une tuile de 200–300 px (`stitchTiles`) répétée. Impression : `@media print { .grain { display: none } }`.

**Trame / halftone / dot matrix / stippling.** `radial-gradient` répété + carte de tons + `contrast()` (#13). Pour les données (pas les photos), le plus léger et accessible est un fond `radial-gradient(circle, currentColor 1px, transparent 1.5px) 0 0/6px 6px` dont l'opacité encode la densité. Piège : `filter: contrast()` sur de grandes surfaces coûte en GPU ; ne jamais le placer sous du texte.

**Tramage ordonné (Bayer), pixel mosaic, dithered images.** Canvas 2D : `getImageData`, luminance, seuil `M[y%4][x%4]` (#15), `putImageData`, `image-rendering: pixelated`, CSS `width` entier multiple de la grille. Calculer une seule fois (pas à chaque image). Mosaïque de pixels : même boucle avec moyenne par bloc.

**Lignes topographiques.** Marching squares sur la grille montant × horizon (#4, #5) : sortie en `<path>` SVG, une par seuil, `vector-effect: non-scaling-stroke`. Hauteurs = la métrique de la grille ; couleurs séquentielles + étiquettes de cote sur chaque 5e ligne ; un repère `<circle>` déplaçable par clavier (flèches) + lecture textuelle `aria-live="polite"` des valeurs. Alternative sans calcul : la même grille en tableau HTML (équivalent accessible obligatoire).

**Verre cannelé.** `backdrop-filter: blur(6px)` sur un calque + `mask-image: repeating-linear-gradient(90deg, #000 0 10px, transparent 10px 14px)`, fond semi-opaque par-dessus ; pièges de #14. Recette non confirmée par une source ouverte (#29 non vérifié) : à tester. Repli : `@supports not (backdrop-filter: blur(1px))` → fond opaque.

**Caustiques d'eau.** Pas de technique légère fiable trouvée et vérifiée : approximation par deux `repeating-radial-gradient` animés lentement en `transform` seul ; désactivé avec `prefers-reduced-motion`. À traiter comme décor facultatif.

**Lentille / distorsion.** `feDisplacementMap` + `feTurbulence` : coûteux et non testé ici ; à n'utiliser que sur un petit cadre statique.

**Comparaison avant/après.** Un `<input type="range">` natif sur une image/panneau clippé par `clip-path: inset(0 calc(100% - var(--p)) 0 0)` : clavier et lecteur d'écran gratuits. `img-comparison-slider` (#11) si on veut le composant clé en main.

**Palette de commandes.** `<dialog>` modal + `<input role="combobox">` + `<ul role="listbox">`, ouverture `Ctrl/⌘+K`, `Échap` ferme, focus rendu à l'élément déclencheur. cmdk exige React (#9) ; ninja-keys (#10) exige Lit.

## 3. Les cinq directions

### 1. Carnet (éditorial)
Recommandations
1. Colonne de lecture 62–70 caractères ; marge droite ≥ 14 rem à ≥ 1000 px pour les notes. En dessous, notes en ligne sous le paragraphe, **ouvertes par défaut** (ne pas copier le masquage par case à cocher de Tufte, #2).
2. Notes en `<aside>` avec `aria-labelledby` du renvoi ; renvoi = `<a href="#n3">` avec numéro réel dans le DOM (pas de `counter` seul).
3. Modifications = corrections visibles : `<del>` barré rouge sépia + `<ins>` souligné, jamais la couleur seule (barre/soulignement). `@media print` conserve le marquage.
4. Papier : fond `#f6f1e6` + grain `feTurbulence` à 6–8 % (§2) ; texte ≥ 7:1 sur le fond.
5. Chiffres tabulaires (`font-variant-numeric: tabular-nums`) pour les montants.
Risque principal : les notes en marge disparaissent ou se chevauchent sur mobile et à 200 % de zoom (1.4.4/1.4.10, #23). Idée : ajouter un mode « relecture » qui affiche d'un seul clic toutes les corrections d'une simulation à l'autre, comme un document annoté.

### 2. Relief (topographique)
1. Grille d'échantillonnage 40×30 à 80×60, `contours()` de d3 (#5) ou ~40 lignes de marching squares maison ; 8–12 seuils.
2. Une seule teinte (séquentielle) + remplissages à faible opacité : un dégradé arc-en-ciel nuit à la lecture des écarts.
3. Repère : un point `tabindex=0`, flèches = un pas de la grille, `Maj+flèche` = 5 pas ; une `<output>` lisible à droite donne montant, horizon, valeur.
4. Équivalent non visuel obligatoire : tableau HTML de la même grille (exception de reflow pour données, #23, mais seulement dans son conteneur).
5. Étiquettes de cote en `paint-order: stroke` (halo clair) pour garder le contraste sur les lignes.
Risque principal : la carte laisse croire à un relief « physique » alors que l'incertitude de la grille ne l'est pas ; une pente ne signale pas un danger. Idée : tracer en pointillé la zone où la valeur est extrapolée (hors données validées), plutôt que de lisser partout (`smooth`, #5).

### 3. Pupitre (dense professionnel)
1. Monospace, interligne 1,3, chiffres alignés ; densité réglable (confortable/compacte) ; couleur jamais seule porteuse du sens (Bloomberg le souligne côté daltonisme, #26 non vérifié).
2. Palette `Ctrl/⌘+K` en `<dialog>` (§2), raccourcis affichés dans l'interface.
3. Diff côte à côte : deux colonnes `display:grid; grid-template-columns:1fr 1fr`, ligne par ligne alignée, `<ins>/<del>` plus symbole `+`/`−` ; défilement synchronisé facultatif, bascule en une colonne sous 700 px.
4. Trame ASCII/dot matrix pour les sparklines : `░▒▓█` dans un `<span aria-hidden>` avec `<span class="sr-only">` donnant la valeur.
5. Cibles ≥ 24 px (AA, #22), ≥ 44 px en tactile ; `:focus-visible` épais, 3:1 contre fond (#24).
Risque principal : densité qui contredit les cibles tactiles et le zoom 200 % ; un terminal est pensé pour clavier + grand écran. Idée : un bouton « plan de travail » qui imprime/exporte le diff en texte brut ; ou remplacer le thème sombre par un thème clair « liste de cotation » pour limiter la fatigue.

### 4. Fil (mobile d'abord)
1. Cartes empilées : un seul message par carte, hauteur variable, `scroll-snap-type: y proximity`.
2. Dégradé thermique granuleux : deux/trois `radial-gradient` + grain §2 ; **le texte repose sur un panneau opaque ou semi-opaque**, pas directement sur le dégradé (#21 : mesurer le pire point).
3. Verre cannelé : décoratif sur l'en-tête de carte uniquement (#14) ; repli opaque.
4. Cibles 44–48 px, espacement 8 px ; zone de pouce en bas de l'écran ; contrôles de comparaison en pile (sans curseur horizontal fin).
5. Image tramée : canvas Bayer calculé une fois, 1 par carte, `loading=lazy`.
Risque principal : les cartes cachent les comparaisons : l'information dense (écarts entre scénarios) se lit mal quand chaque carte est isolée (non vérifié : l'article NN/g n'a pas pu être ouvert, #27). Idée : une carte « comparer » qui épingle deux cartes côte à côte (ou superposées avec bascule) plutôt qu'un fil linéaire.

### 5. Épure (blueprint avant/après)
1. Grille de plan : deux `repeating-linear-gradient` (pas 8 px, mailles 40 px plus marquées), fond bleu `#0b2a4a`, traits clairs ; vérifier le contraste du texte sur la grille (#21).
2. Écran partagé : `<input type="range">` natif (§2) + clip-path ; ou `img-comparison-slider` (#11, < 4 Ko gzip) ; alternative clavier : touches ← → par pas de 5 %.
3. Cotes : `<svg>` avec flèches `marker-start/end`, trait d'extension, texte centré sur la ligne, valeur de l'écart + unité ; texte en `<text>` (zoomable), pas en image.
4. Cartouche (title block) en bas à droite : version, hypothèses, date : discipline qui fait aussi la traçabilité.
5. Impression : fond blanc, traits noirs (`@media print`).
Risque principal : contraste texte clair sur bleu avec grille, et les cotes qui se chevauchent quand les écarts sont petits. Idée : décaler automatiquement les cotes en « escalier » (comme en dessin industriel), ou remplacer le curseur par une superposition avec différence colorée si le public ne sait pas lire un plan.

## 4. Polices libres par direction (prévoir repli système hors ligne)

| Direction | Police | Licence (page du dépôt) | Où |
|---|---|---|---|
| 1 Carnet | Source Serif 4 (texte) ; repli `Georgia, "Times New Roman", serif` | OFL-1.1 | github.com/adobe-fonts/source-serif (dossier WOFF2/VAR) |
| 2 Relief | IBM Plex Sans (étiquettes) + Plex Mono (cotes) ; repli `system-ui, sans-serif` | OFL-1.1 | github.com/IBM/plex/releases |
| 3 Pupitre | JetBrains Mono (variante NL sans ligatures) ou IBM Plex Mono ; repli `ui-monospace, "SF Mono", Menlo, Consolas, monospace` | OFL-1.1 (police) | github.com/JetBrains/JetBrainsMono ; IBM/plex |
| 4 Fil | Inter (variable) ; repli `system-ui, -apple-system, "Segoe UI", sans-serif` | OFL-1.1 | github.com/rsms/inter (releases) |
| 5 Épure | IBM Plex Mono / Plex Sans Condensed (cotes, cartouche) ; repli `ui-monospace, "Arial Narrow", sans-serif` | OFL-1.1 | github.com/IBM/plex/releases |

Notes. Les polices sont à copier dans `fonts/` en `.woff2` avec `@font-face` + `font-display: swap`, et la pile de repli à la suite : le prototype doit rester lisible sans elles. Écartées : ET Book (MIT, mais jeu limité pour le français, non vérifié) et Fraunces (OFL mais pas de release directe, #19). Je n'ai pas vérifié que les WOFF2 existent dans les releases de Plex ou JetBrains Mono (dépôt : non confirmé) : prévoir une conversion `.ttf → .woff2` si besoin.

## 5. Règles d'accessibilité décisives (chaque point est tracé au journal)
- Contraste : 4,5:1 (texte normal), 3:1 (grand texte) (#21). Texte jamais directement sur dégradé/grain ; panneau opaque ou semi-opaque dessous ; mesurer au point le plus défavorable (ma prudence, pas la règle écrite).
- Cibles : minimum 24×24 px (AA) ; objectif 44–48 px en tactile (#22).
- Focus : `:focus-visible` épais ≥ 2 px, bien contrasté ; 2.4.13 est de niveau AAA (#24). Éviter qu'une barre collante masque le focus (2.4.11 : non ouvert, non vérifié).
- Zoom/reflow : 320 px de large sans défilement 2D ; exception pour tableaux/cartes, limitée au conteneur (#23). Tester à 200 % et 400 %.
- Mouvement réduit : désactiver toute animation de fond ; remplacer échelle/panoramique par fondu (#25).
- Impression : couper grain/verre ; fond blanc ; garder `<ins>/<del>` lisibles.

## 6. Limites de la recherche
- Produits réels (cartes d'isolignes non géographiques, terminaux financiers, apps mobiles en cartes, dessins techniques) : pages Bloomberg (#26) et NN/g (#27) non ouvertes (403/404). Aucun site de produit (Linear, Stripe, Revolut, etc.) n'a été ouvert ; je n'en cite donc aucun comme référence. À faire : ouvrir des exemples réels avec le navigateur du Mac (Chrome/Browser) pour la phase suivante.
- Les résumés de WebFetch sont produits par un modèle : les licences sont celles rapportées par la page mais le texte de LICENSE n'a pas été lu (d3-contour, cmdk, etc.).
- Aucune extraction ni exécution de code ; les extraits sont des croquis non testés, sauf le code halftone repris de #13.
