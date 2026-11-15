# Prisme — mettre le capital en lumière

Ouvrir : **http://127.0.0.1:8770/directions/prisme/**

Cette direction est un prototype local de présentation, connecté au contrôleur commun
et au moteur financier existant pour les explorations. Elle ne remplace pas le produit.
Les archives Robert r5, r10 et r15 sont consultées en lecture seule.

## Parti pris

Le terrain principal est le capital, représenté par un **ruban continu proportionnel
aux poids réels de l’allocation examinée**. Les options ne sont pas des cartes
concurrentes portant un score : trois commandes mettent successivement en lumière
la solution du calcul, l’autre minimum ou la règle simple indépendante. Les valeurs
en CAD sont lisibles sous le ruban ; les pertes se comparent dans une seconde vue
en colonnes alignées.

La première composition a été révisée après critique indépendante du parent :
un grand titre à gauche et un montant à droite ressemblait trop à Folio. La version
retenue utilise un titre centré, une table panoramique, un ruban de capital pleine
largeur et des commandes sous l’objet observé. La distinction subsiste en niveaux
de gris : aire de lecture horizontale et proportions réelles, plutôt qu’article
éditorial ou instrument à grille dense.

Le verre cannelé, les gradients thermiques et les caustiques sont générés en CSS.
Ils structurent les segments et la séparation avant/après. **La couleur ne code pas
le risque** ; ce statut est indiqué près du ruban. Les largeurs, poids et montants
sont des données, tandis que la luminosité et le relief sont décoratifs.

## Deux références visuelles réellement examinées

| Référence vérifiable | Lecture et observation réelles | Principe utilisé | Limites et droits |
|---|---|---|---|
| Studio Olafur Eliasson, *Your rainbow panorama*, œuvre 2006–2011, installée en 2011. [Page officielle](https://olafureliasson.net/artwork/your-rainbow-panorama-2006-2011/), consultée le 2026-11-15. | Recherche par AWS `web-search.v1`, texte de la page extrait et lu, capture Playwright vue : photographie du panorama circulaire sur le toit d’ARoS et bandes spectrales continues. [Capture](proofs/references/prisme-eliasson.png), [texte](proofs/references/prisme-eliasson.txt). | Une même réalité peut être observée sous plusieurs cadrages ; continuité spatiale, filtre optique et horizon commun. Transposé au même capital vu selon plusieurs allocations. | Référence artistique, aucune preuve d’utilisabilité. Photographies créditées aux auteurs sur la page, sans permission de réutilisation présumée. Aucun actif de cette œuvre n’est embarqué. |
| Solomon R. Guggenheim Foundation, exposition *James Turrell*, 21 juin–25 septembre 2013 ; *Aten Reign* (2013). [Microsite officiel](http://web.guggenheim.org/exhibitions/turrell/), consulté le 2026-11-15. | Recherche AWS, lecture de l’introduction et du passage *Aten Reign*, capture vue : anneaux lumineux emboîtés, profondeur créée par les plans de lumière. [Capture](proofs/references/prisme-turrell-guggenheim.png), [texte](proofs/references/prisme-turrell-guggenheim.txt). | La lumière peut construire un espace de comparaison, pas seulement colorer son fond. Transposition : surfaces continues, repères, couches de profondeur et transition spatiale avant/après. | Référence esthétique, aucun effet de compréhension démontré. Microsite © 2013 SRGF, tous droits réservés ; photographie David Heald / SRGF, œuvre © James Turrell. Aucun visuel repris. HTTPS a échoué sur certificat ; le lien HTTP officiel renvoyé par la recherche est accessible. |

La page NGA consacrée à *Within without* a d’abord été repérée, mais le navigateur
a rencontré un écran de vérification. Sa capture est conservée comme **accès
échoué**, pas comme référence visuelle observée. Aucune tentative de contournement.
Les résultats et reçus AWS se trouvent dans `proofs/references/prisme-search*.json`
et `prisme-turrell-search.json`.

## Hiérarchie et système visuel

| Élément | Choix et rôle |
|---|---|
| Typographie | DM Sans locale, titres à chasse compacte, grands nombres tabulaires ; aucune fonte distante. |
| Couleurs | Ivoire froid `#eef1ee`, encre `#172629`, vert-gris lisible ; aqua et ambre dans la matière optique, sans échelle financière implicite. |
| Composition | Longues horizontales, alignements, peu de surfaces fermées ; le capital occupe l’espace principal. |
| Densité | Conclusion courte, objet manipulable, valeurs exactes, limites proches. La profondeur se dévoile par changement de hiérarchie ou preuve contextuelle. |
| Preuves | Panneau natif `<dialog>` à fond opaque, contexte visible derrière un voile, focus géré par le contrôleur commun. |
| Révision | État précédent à gauche, hypothèse à droite, séparateur réfractant ; après calcul, delta avant comparaison. Sur mobile, la lecture devient verticale. |
| Mouvement | Aucun mouvement décoratif permanent, aucun indicateur de progression inventé. Préférence de mouvement réduit respectée. |
| Mobile | Ruban conservant les proportions, pourcentages verticaux et valeurs textuelles sous le ruban ; comparaison en défilement horizontal interne, table précise disponible en mode approfondi. |

## Adaptation de la présentation

| Vue | « Voir clair » | « Voir au-delà » | Invariant |
|---|---|---|---|
| Comprendre | Conclusion centrée, ruban du capital, choix des allocations, limite et règle simple visibles dès le résumé. | Question calculable, objectif, contraintes, nature du résultat et matrice des chocs au premier plan ; résultat condensé puis tableau comparatif. | Même minimum, mêmes allocations, mêmes hypothèses, mêmes limites et mêmes preuves. |
| Mettre côte à côte | Film horizontal : capital déplacé, allocations, pertes par choc, statut. | Tableau précis après la méthode ; les nombres ne changent pas. | Même univers et mêmes unités. Aucun score global inventé. |
| Faire évoluer | Formulaire en CAD et état précédent spatialement séparé. | Même interaction financière ; les préférences de lecture restent indépendantes. | Les valeurs initiales proviennent de l’état courant ; saisie, calcul et annulation restent distincts. |

## Les actions et leurs données

| Action | Élément concret | Donnée / événement réel |
|---|---|---|
| Ouvrir Robert et une archive | Sélecteur r5/r10/r15 | Projection existante `data/cases.json`, sans nouvel appel AWS. |
| Changer de profondeur | « Voir clair / Voir au-delà » | `s.level`, sans modification de `s.v` ni calcul. |
| Examiner une option | Commandes du ruban / sélection du film | `analysis.options[].weights`, `metrics.turnover_cad`, pertes par scénario ; référence indépendante uniquement si présente. |
| Comprendre un chiffre | « Pourquoi ce minimum ? » | Preuve et pointeurs vers le résultat liés au dossier affiché, contrôleur partagé. |
| Modifier une hypothèse | Retrait et budget de perte en CAD | Formulaire `data-scenario` ; pas de curseur ni préférence inférée. |
| Calculer une copie | « Calculer cette variante » | POST `/api/prototype/explore`, moteur réel local, aucune écriture dans le dossier produit, aucun agent relancé. |
| Observer le changement | Delta au-dessus des options | État précédent et courant ; entrées conservées et calculs réexécutés identifiés. Les dépendances ne sont pas animées comme des événements fictifs. |
| Revenir | Annuler la saisie / état précédent / Robert initial | Machine d’état commune ; historique local, archives préservées. |
| Contester / approfondir | Sources, calcul et agents | Passages, contrôles et événements archivés. Aucune activité inventée. |

L’impossibilité n’ouvre pas un ruban vide : elle affiche une conclusion bornée et
les contrôles, avec correction et retour possibles. Pour un retrait de 120 000 CAD
sur 100 000 CAD, le manque de 20 000 CAD vient du certificat algébrique du moteur ;
aucune allocation n’est proposée, aucun IIS global n’est revendiqué.

## Vérifications exécutées

Le script [prisme-qa.cjs](proofs/references/prisme-qa.cjs) a vérifié dix
comportements le 2026-11-15. [Résultats détaillés](proofs/references/prisme-qa.json).

- Changer d’option affiche les poids réels : le second minimum porte TSLA à 0 %.
- Changer de profondeur modifie la hiérarchie et conserve exactement les limites.
- La preuve reçoit le focus, Escape la ferme et rend le focus au déclencheur.
- Quatre options comparables sont présentes pour r5, référence comprise.
- r15 ne revendique pas de multiplicité absente de son calcul.
- Le retrait à 40 000 CAD déclenche le moteur et affiche le delta.
- Le retour restaure l’archive r5.
- Le retrait à 120 000 CAD présente le certificat, sans allocation.
- Aucun débordement horizontal de page à 390 et 320 px.
- Aucune erreur JavaScript ; axe-core WCAG 2 A/AA et 2.1 AA : aucune violation
  détectée sur l’accueil à 320 px.

Les captures desktop, comparaison, méthode, preuve, révision, impossibilité et
mobile sont dans `proofs/references/prisme-*.png`. Desktop, méthode et mobile
390 ont été inspectés visuellement. Le dernier ajout du rappel des limites sous
le titre est contrôlé séparément par [prisme-final-visual.json](proofs/references/prisme-final-visual.json),
sans répéter les calculs financiers déjà validés.

## Limites de cette proposition

- Le verre ne prouve aucune meilleure utilisabilité. Une comparaison humaine avec
  les autres directions reste nécessaire.
- La petite typographie des métadonnées est secondaire ; les nombres et limites
  déterminantes restent disponibles en texte. Les captures ne remplacent pas un
  essai utilisateur, un audit lecteur d’écran ni une mesure de compréhension.
- Les archives sont réellement lues et les explorations réellement calculées,
  mais celles-ci ne relancent pas les quatre agents et ne deviennent pas des
  révisions persistantes du dossier principal.
- Le test axe concerne un état et une taille ; il ne constitue pas une déclaration
  de conformité globale.
- La comparaison conserve la défense du résultat : la règle simple atteint le
  minimum initial de Robert ; aucune supériorité des quatre agents n’en découle.

## Reprise

Fichiers autonomes : `prototype/prompt6/directions/prisme/index.html`, `style.css`,
`app.js`. Dépendance commune : `../shared/experience.js` et `base.css`, détenus par
l’intégrateur. Aucun changement du moteur ou de l’ancien prototype.

Session de conception `/root/p6_audit`, fournisseur vérifié
`amazon-bedrock-runtime`. Recherches par la route AWS existante. Dessin CSS,
navigation Playwright et axe-core déterministes ; aucune inférence auxiliaire
hors AWS, aucun service payant ajouté.
