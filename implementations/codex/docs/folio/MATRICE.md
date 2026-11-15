# Correspondance entre Folio et le fonctionnement réel

État : intégré et examiné, sauf limites explicitement indiquées. Aucune opération financière de marché n’est exécutée.

| Fonction attendue | Composant Folio | Opération et données réelles | Échec, annulation et rechargement | Preuve |
|---|---|---|---|---|
| Retrouver un dossier | Bibliothèque, recherche locale | GET `/api/folio/dossiers`, métadonnées SQLite ; filtre textuel | Lecture seule ; l’URL permet de rouvrir le dossier | `proofs/final/verification.json` |
| Entrer une demande | Nouvelle étude ; exemple → brouillon | POST création, clé persistante ; faits structurés facultatifs ; quatre rôles réels | Saisie locale ; transmission inconnue réessayée avec même clé | `proofs/incomplete-entry.json`, `tests/folio_entry.cjs` |
| Examiner le profil | Profil, origine, questions | `problem`, faits déclarés/extraits/supposés/inconnus ; questions des agents | Aucun champ absent inventé ; correction explicite | `proofs/incomplete-entry.json`, capture finale profil |
| Lancer/suivre/reprendre | Étude, tâches, pièces, événements | Service existant, LangGraph, reçus Bedrock et artefacts ; reprise du run enregistré | Pas de pourcentage artificiel ; états d’échec et reprise accessibles | `proofs/audit_live_cases.json`, backend tests |
| Lire selon sa préférence | Essentielle / Approfondie | Ordre de présentation, vocabulaire explicatif, priorité aux méthodes ou aux conséquences | Aucune requête de mutation ; niveau enregistré indépendamment des faits | `proofs/browser-read.json`, `proofs/final/verification.json` |
| Comparer équitablement | Planche comparative, sélection | `analysis.options`, mêmes unités/fenêtre ; référence simple uniquement si dossier compatible | Absence de solution = pas d’allocation ; hypothèses et limites conservées | `proofs/audit_live_cases.json`, `proofs/browser-preview.json` |
| Retrouver une preuve | Annotation / panneau de marge | Claim et binding, pointeurs métriques/scénarios, contrôles, sources capturées | Preuve absente nommée ; Escape rend le focus ; version sélectionnée conservée | `proofs/browser-read.json`, `proofs/final/verification.json` |
| Chercher dans le dossier | Recherche contextuelle | Claims, champs du problème, documents, références des pièces | Aucun moteur externe ou inférence ; résultats bornés à la version regardée | `tests/folio_review.cjs`, inspection navigateur |
| Modifier un brouillon | Formulaire de révision | Champs avec provenance, unité, effet ; brouillon séparé | Annuler la saisie ne change pas le dossier ; frappe après lancement conservée | `proofs/browser-latency.json` |
| Explorer sans corriger | Aperçu déterministe | POST `/preview` ; moteur existant et contrôles ; aucune mutation/agent | Base et révision courante distinctes ; cache restauré seulement si compatible ; annuler retourne à la base | `proofs/browser-preview.json`, `proofs/browser-history.json` |
| Corriger le besoin | Correction persistante | POST `/revise`, base_revision, clé ; invalidation et quatre agents | 409 conserve la saisie ; résultat ancien cesse d’être applicable ; histoire conservée | `proofs/browser-revision40.json`, `proofs/browser-revisionloss1000.json` |
| Créer une variante | Variante persistante | Nouveau dossier, origine/source_revision, provenance héritée ; quatre agents | Parent inchangé ; dossier indépendant dans bibliothèque | `proofs/browser-variant.json`, `proofs/audit_variant.json` |
| Comprendre le changement | Tableau avant/après, dépendances | Projection précédente réelle ; valeurs modifiées, pièces réutilisées/invalidées | Un aperçu ne revendique aucune réutilisation de calcul ; variante ≠ correction | `proofs/audit_revisions.json`, `proofs/final/verification.json` |
| Relire et rétablir | Historique, sélecteur de versions | Rejeu des écritures/invalidations à la révision choisie ; restaurer = nouvelle correction | Aucun événement futur, aucun effacement ; archive signalée | `proofs/browser-history.json`, backend tests |
| Exporter la version lue | Export HTML / JSON | HTML statique borné ; JSON HTTP brut épinglé à la révision ; aperçu exporté avec sa réponse brute | Erreur explicite ; aucun parse/stringify des pièces immuables ; export aperçu ancien sans octets refusé | `proofs/browser-export.json`, `proofs/browser-previewexport.json` |
| Supporter interruptions et concurrence | Contrôleur, API idempotente | Clé+empreinte dans même transaction ; navigation token ; verrou service ; localStorage | Réponse tardive ne remplace pas la navigation ; retry commit sans second run | `proofs/browser-latency.json`, `proofs/incomplete-entry.json`, backend tests |
| Écran étroit et clavier | Grille éditoriale, dialogues, régions de tableaux | Réordonnancement CSS ; axes adaptés, unités communes ; focus visible ; reduced motion | Défilement dans régions nommées ; alternatives textuelles des graphiques | `proofs/browser-mobile.json`, `proofs/final/verification.json` |

## Adaptation sur un même dossier

| Dimension | Invariant | Lecture essentielle | Lecture approfondie |
|---|---|---|---|
| Conclusion | Même montant/constat et même portée | Demande → conclusion → contrepoint | Résultat compact → objectif, conventions, hypothèses |
| Robert | Même minimum et même référence indépendante lorsqu’elle est disponible | Capital à déplacer ; autre répartition et conséquence des chocs | Problème linéaire, objectif demi-L1, entrées et contrôles |
| Amira | Même fenêtre CAD, même série et absence de prévision | Conséquence du poids initial sur l’histoire observée | Transformation prix/FX, convention achat-conservation, métriques et dates |
| Incertitude | Limites déterminantes toujours présentes | Phrase concrète au voisinage du résultat | Conventions détaillées, données admissibles et conditions de validité |
| Preuves et actions | Toutes accessibles dans les deux niveaux | Annotation à la demande | Méthode et preuves prioritaires, mêmes annotations |
| Identité de l’utilisateur | Aucun âge, capital ou risque ne détermine le niveau | Choix libre et réversible | Choix libre et réversible |

Le **profil financier** déclenche un nouveau calcul ou une nouvelle chaîne selon l’intention choisie. Le **niveau de lecture** ne change aucune donnée ni conclusion et ne déclenche aucun appel AWS.
