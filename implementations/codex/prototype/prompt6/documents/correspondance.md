# Correspondance de référence — expérience et système

État : **prototype v0.1, avant validation**. Aucun composant n’a encore
remplacé `alphaforge_app/static/workbench.*`. La colonne d’intégration
est un engagement à réaliser après accord, pas une capacité déjà raccordée.

| Élément proposé | Composant du prototype | Données ou événements | Vérification / portée actuelle | Après validation |
|---|---|---|---|---|
| Accueil orienté questions | `home()` | Index des quatre cas, Robert r5/r10 | Valeurs de l’aperçu lues dans les exports | Index du magasin réel, titres compréhensibles sans fuite d’un dossier |
| Conclusion conditionnelle | `decision()`, `amira()`, `impossible()` | Claims, métriques, méthode, statut et `optimal_face` | Invariants aux trois niveaux ; non-unicité conditionnelle ; centimes préservés | `ViewPacket` courant, assertion bloquée si contrôle matériel échoue |
| Preuve contextuelle | `proof()`, panneau natif | Pointeurs/valeurs, hash, méthode, portée, contrôles | Déficit lié à `shortfall_cad` ; local lié au hash de calcul | Lectures de versions exactes, conservation du contexte et du focus |
| Origine des informations | `profile()` | Faits avec origine et demande source immuable | Valeurs inconnues conservées ; pas de déduction de compétence | Édition d’une déclaration → événement humain → A0 |
| Niveaux de présentation | `state.level`, `level-picker` | Préférence navigateur, jamais le problème financier | Chiffres et limites identiques ; aucune inférence | Préférence de présentation séparée, sans invalidation de calcul |
| Répartition / tableau | `allocationChart()` | Options, poids et admissibilité de la même version | Même sélection ; référence simple r5 seulement ; contraste contrôlé | Même projection du résultat courant |
| Comparaison des chocs | `stressTable()` | `scenario_results`, unités CAD et échéance | Pas de distribution inventée ; pas d’optimum de risque implicite | Pointeurs cliquables par mesure si disponibles |
| Trajectoires historiques | `historyChart()`, `series` | Deux séries réellement calculées, date et valeur | Axe calendaire, aucun lissage ni prolongement ; CSV identique | Séries admissibles selon date de connaissance et politique |
| Variante sans adoption | `variants()`, `/explore` | Copie de ProblemSpec, quatre changements déclarés | Calcul Python réel, sans revue A0–A3 ; provenance et reçu | Branche séparée avec droit d’adoption explicite à qualifier |
| Résultat lié aux paramètres | `renderResult()` | Base de version + paramètres envoyés | Toute nouvelle édition marque le calcul ancien ; adoption empêchée | Liaison à une révision et blocage atomique des conclusions périmées |
| Correction / annulation | `adopt()`, `restore` | Copie en mémoire et archive d’origine | Retour correct r5 même si l’essai est rappelé depuis r15 | Correction crée une version ; consultation d’archive ne restaure rien |
| Révision causale | `historyView()` | Changements, invalidations et réutilisations archivés | 30→40→74,4 kCAD, même portefeuille initial | Projection des événements courants avec libellés métier |
| Contributions des quatre agents | `agents()` | Tâches, entrées, sorties et reçus AWS archivés | Pas de faux tour de débat ou de progression | Flux réel par événement, gestion des attentes/retours |
| Sources ciblées | `sources()` | Titres, passages capturés, niveau et sélection | Filtre local ; consultation ≠ preuve logique indépendante | Recherche documentaire contrôlée AWS quand nécessaire |
| Attente / impossibilité | `incomplete()`, `impossible()` | Questions ouvertes ou certificat borné | Ni allocation inventée, ni relaxation automatique | Même distinction dans le dossier vivant |
| Erreur / reprise | `calculate()`, `retry` | Vraie requête de calcul ; erreur 503 d’essai identifiée | Paramètres conservés ; navigation pendant requête sûre | Distinguer reprise idempotente et appel distant d’issue inconnue |
| Nouvelle demande / clarification | `newRequest()`, `editProfile()` | Texte en `sessionStorage` | Brouillon sans extraction ou analyse prétendue | Soumission A0 et traitement des inconnus selon contrat |

## Invariants à reprendre dans l’intégration

1. Le changement de présentation ne change ni résultat, ni donnée,
   ni limite décisive.
2. Une correction du profil est distincte d’une préférence d’affichage.
3. Une variante nomme sa base. Adopter, annuler et consulter l’histoire
   sont trois gestes différents.
4. Pendant le recalcul, une ancienne conclusion reste historique :
   elle ne semble pas répondre aux nouveaux paramètres.
5. Seuls des événements effectivement reçus alimentent l’activité.
6. Une preuve affiche son type, sa portée, son auteur et ses limites.
7. Un échec technique ne devient pas une impossibilité financière.
8. Une comparaison conserve unités, données et conventions entre options.
9. Le moteur de calcul ne devient pas un générateur de faits manquants.
10. Les fichiers, données et sessions préexistants demeurent conservés.

## Comparaison de fidélité après intégration

Les captures de référence sont dans `proofs/` et `proofs/audit/prototype/`.
À contenu et taille comparables, examiner Robert r5 dans les trois niveaux,
preuve ouverte, historique, Amira, incomplet et impossible.
Rejouer aussi variante→adoption→retour, modification d’un formulaire après
calcul, erreur→reprise et navigation pendant une requête.

Comparer les intitulés, limites, ordre et actions autant que la mise en
page. Toute contrainte technique empêchant une interaction validée doit
être signalée avec une solution de remplacement explicite.
