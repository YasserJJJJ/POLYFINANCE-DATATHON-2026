# Trois directions AlphaForge — galerie de validation

**Ouvrir [la galerie](http://127.0.0.1:8770/directions/)**, puis
[Folio](http://127.0.0.1:8770/directions/folio/),
[Isobare](http://127.0.0.1:8770/directions/isobare/) ou
[Prisme](http://127.0.0.1:8770/directions/prisme/).
Double-cliquer `Ouvrir_les_directions.command` relance le serveur si nécessaire.

Les trois réalisations sont des propositions à départager. L’application
principale sur le port 8768 et la proposition précédente sur 8770 restent
accessibles. Aucune direction n’est intégrée au produit à cette étape.

## Ce que l’on peut réellement essayer

Chaque direction charge le même dossier fictif Robert, archive r5 du
15 novembre 2026 : capital 100 000 CAD, retrait 30 000 CAD à douze mois,
plafond initial TSLA 10 %, perte au plus 15 000 CAD sous chacun des deux
chocs déclarés. Le résultat de 30 000 CAD à réallouer est un résultat
archivé du moteur, pas une valeur écrite pour la maquette.

Les trois directions permettent de :

1. Lire la demande, la conclusion et sa portée.
2. Comparer le portefeuille initial, le premier optimum, un autre minimum
   lorsqu’il est établi, et la référence simple indépendante disponible en r5.
3. Ouvrir un chiffre, les entrées, la méthode, les contrôles, les passages
   documentaires et l’export source.
4. Préparer puis calculer une variante de retrait ou de budget de perte.
5. Examiner avant/après, les entrées conservées et les calculs réexécutés.
6. Revenir à l’état précédent ou à l’archive initiale.
7. Passer de la conclusion expliquée à l’examen méthodologique.

**Les archives r5/r10/r15 sont précalculées.** Leur ouverture ne lance ni
calcul ni agent. **Les variantes saisies sont calculées réellement**, par
`alphaforge_app.decision.finance.analyze`, sur une copie. Elles ne relancent
aucun agent et ne modifient aucun dossier persistant. Le retour restaure
l’état local ; un rechargement remet le prototype à son état initial.

## Trois partis pris

| Direction | Composition et interaction | Force | Compromis |
|---|---|---|---|
| [Folio](folio.md) | Page éditoriale, hiérarchie serif, notes en marge, planche comparative et erratum | Guide une première lecture et rend la contestation naturelle | Défilement plus long ; moins de mesures visibles simultanément |
| [Isobare](isobare.md) | Console orthogonale, paramètres à gauche, champ de mesure central, registre à droite | Compare précisément sur une échelle commune | Grammaire technique et densité plus exigeantes |
| [Prisme](prisme.md) | Table lumineuse panoramique, capital réparti à l’échelle, options en regard | Rend les proportions et le changement immédiatement explorables | Plus d’espace ; les petits segments demandent leurs valeurs textuelles |

Le critère « reconnaissable en gris sans logo ni décor » est examiné
par des captures dédiées, pas uniquement par les palettes. Le motif papier,
le verre et les lumières ne représentent aucune mesure financière.

## Adaptation et invariants

| Dimension | Lecture accessible | Lecture approfondie |
|---|---|---|
| Ordre | Demande, minimum, raisons, contrepoint et suite possible | Résultat condensé, entrées, objectif, contraintes, chocs et sorties |
| Explication | « Déplacer le moins de capital pour financer le retrait » | Demi-L1 des variations de poids ; programme linéaire sous contraintes |
| Comparaison | Montants et conséquences des options | Même comparaison, avec formulation et hypothèses au premier plan |
| Preuves | Chiffre et liens contextuels | Contrôles, source et provenance inspectables |
| Limites | Toujours présentes | Toujours présentes, plus le domaine mathématique exact |

Les faits, chiffres et limites restent identiques. Le changement de
présentation n’appelle pas le moteur. Le niveau est choisi explicitement ;
aucune compétence n’est déduite de l’âge, du patrimoine ou du risque.

## Une base de données et d’interactions commune

Les trois modules de rendu importent
[`shared/experience.js`](../../prototype/prompt6/directions/shared/experience.js).
Ce contrôleur unique charge `/api/prototype/cases/robert`, normalise les
options, gère les brouillons, la navigation entre archives, le calcul local,
les preuves et l’historique réversible. Chaque direction possède son HTML,
son CSS et une composition JS distincte.

| Élément affiché | Origine |
|---|---|
| Minimum, réserve, pertes | `version.stats`, liés aux valeurs de `analysis.options` |
| Répartitions | Poids de l’option effectivement sélectionnée |
| Règle simple | `version.simple_reference`, revue financière indépendante de r5 |
| Sources | Captures et passages du dossier, statut consultée/sélectionnée distingué |
| Travail des agents | `version.agents` et traces archivées ; jamais activité simulée |
| Différences | Deux états conservés en mémoire, comparaison de champs explicites |
| Calcul local | Reçu d’exécution avec hash du résultat et base archivée exacte |

Le contrôleur ne modifie pas le serveur, le moteur, la base SQLite ou les
artefacts du produit. Le graphe de dépendances d’une variante locale décrit
les entrées conservées et le calcul réellement relancé ; il ne prétend pas
avoir réutilisé un cache d’artefacts ou exécuté quatre agents.

## Limites financières conservées

- Une règle simple atteint aussi le minimum de Robert r5. Aucun avantage
  des agents sur cet objectif n’est démontré.
- Le premier optimum n’est pas un optimum de risque. Un autre témoin peut
  présenter moins de pertes sous les deux chocs.
- Deux chocs hypothétiques sans probabilités ne bornent pas la perte future.
- La réserve à rendement nul est abstraite ; aucun instrument réel n’est
  qualifié ou garanti.
- Frais, fiscalité et inflation sont exclus ; positions fractionnaires.
- Les contraintes portent sur les poids initiaux. Quatre ans sont déclarés,
  mais seuls les chocs à l’échéance du retrait sont calculés.
- La référence simple de r5 n’est jamais extrapolée à une variante.
- Les citations et captures ne constituent pas une vérification indépendante
  de l’appui logique de chaque affirmation.

## Outils effectivement mobilisés

| Outil | Rôle et accès observé |
|---|---|
| Sessions AWS existantes | Création et critiques croisées ; route `amazon-bedrock-runtime` reconfirmée |
| Recherche AWS existante | Références visuelles, requêtes et reçus conservés dans `proofs/references/` |
| HTTP et Playwright 1.65.1 | Lecture de références, inspection du rendu et interactions dans Chromium |
| HTML, CSS, SVG | Trois compositions originales, matières et graphiques sans modèle d’image |
| Contrôleur et moteur existants | Données constantes et variantes réellement calculées sur copie |
| axe-core 4.14.0 | Contrôles automatiques ciblés, complétés par inspection visuelle et clavier |
| Polices locales | DM Sans et Newsreader sous OFL ; polices système pour la console |
| Python et outils locaux | Assemblage des captures, empreintes et état de reprise |

Le catalogue de plugins de design avait été interrogé pendant le Prompt 6 :
Figma, Product Design, Canva, MagicPath et TinyFish n’étaient pas connectés.
Aucune route AWS de leurs éventuelles inférences n’était établie. Aucun
de ces assistants n’est employé ; les outils locaux et la recherche AWS
existante ont un résultat concret sans nouveau service payant.

## Reprise

```sh
.venv/bin/python scripts/launch_prototype_p6.py --no-browser
open http://127.0.0.1:8770/directions/
```

Sources : `prototype/prompt6/directions/`. Documents et contrôles :
`docs/directions_artistiques/`. Captures livrées :
`prototype/prompt6/directions/captures/`.

La prochaine étape dépend du choix de la direction visuelle et des
interactions majeures. Les trois prototypes restent modifiables et
comparables avant cette intégration.
