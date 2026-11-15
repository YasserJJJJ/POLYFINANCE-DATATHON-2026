# État de reprise — Folio 0.7.0

Date de consolidation : 15 novembre 2026. Entrée du produit : **http://127.0.0.1:8768/**.

## Démarrer

```bash
.venv/bin/python scripts/launch.py
```

Le lanceur réutilise le serveur de version 0.7.0 de ce dépôt. Il ne sonde aucun autre port et ne ferme aucun autre service. `runtime/server.json` contient son PID et son répertoire ; le PID n’est pas une identité durable après redémarrage. Le serveur écoute seulement sur `127.0.0.1:8768`.

Environnement préparé : Python 3.15.2 dans `.venv`, dépendances de `requirements.txt`. Ne pas résoudre le lien symbolique `.venv/bin/python` vers un interpréteur système : cela perdrait l’environnement virtuel. En cas de session AWS expirée, renouveler le profil `alphaforge`, puis reprendre le dossier depuis Étude. La consultation et les aperçus n’exigent pas de nouvelle inférence.

## Fichiers faisant autorité

- `alphaforge_app/static/folio/{index.html,controller.js,render.js,shared.js,style.css,fonts/}` : application éditoriale.
- `alphaforge_app/decision/folio_api.py`, `folio_projection.py` : API et archives de présentation.
- `alphaforge_app/decision/store.py`, `service.py` : transactions, idempotence, invalidation, reprise.
- `alphaforge_app/decision/finance.py` : moteur financier **inchangé** ; empreinte dans `proofs/engine_preserved.json`.
- `runtime/decision/dossiers.sqlite3`, `checkpoints.sqlite3`, `objects/`, `research/` : état persistant et captures.
- `docs/recherche/` : corpus documentaire borné utilisé par le produit.
- Données starter : résolution par `alphaforge_app/datasets.py`, ou chemin explicite `ALPHAFORGE_DATA_DIR`.

Les traces et métriques du produit demeurent la source de vérité. Les captures d’écran, projections JavaScript et comptes rendus de tests ne les remplacent pas.

## Versions et sauvegardes

`artifacts/folio_reference/` conserve la copie **avant intégration** : prototype choisi, ancien produit, instantanés SQLite, objets et manifeste. Ne pas la remplacer.

`artifacts/folio_integre/` conserve la livraison intégrée : deux captures via l’API SQLite backup, archive de source/état/corpus/données nécessaires et manifeste. Aucun secret AWS ni environnement virtuel n’est embarqué. Les données et captures restent locales, sous leurs droits existants.

Pour restaurer, extraire l’archive dans une **copie distincte** ; ne pas écraser une base d’un serveur en cours. L’archive replace les sauvegardes cohérentes dans `runtime/decision/*.sqlite3` sans WAL obsolète. Préparer l’environnement à partir de `requirements.txt`, conserver l’accès AWS autorisé et les licences des données. La restauration d’une sauvegarde ancienne ne doit pas effacer les dossiers créés ensuite dans l’application active.

## Reprendre une action dans Folio

- **Lecture interrompue** : rouvrir l’URL contenant dossier, vue et révision.
- **Brouillon** : retrouvé dans le même navigateur ; « Annuler la saisie » ne modifie pas le dossier.
- **Aperçu** : retrouvé uniquement si ses révisions source/courante concordent. Un changement de base le rend non applicable.
- **Transmission non confirmée** : « Réessayer » renvoie la clé et le corps conservés. Une mutation déjà enregistrée retrouve le même dossier et le même run.
- **Étude interrompue** : Étude → Reprendre. Les reçus et checkpoints conservés sont consultables ; un run actif est protégé contre un second worker.
- **Réponse AWS d’issue inconnue** : le système ne promet pas une facturation unique. Une reprise distante peut réinvoquer le modèle ; cette limite reste explicite.
- **Ancienne version** : lecture seule. Rétablir ses entrées produit une nouvelle correction, sans supprimer l’historique.

## Cas de référence persistants

| Dossier | Identifiant | Repères |
|---|---|---|
| Robert initial P5, contrepoint indépendant | `4089e4b0d70f40b6b20d832fa261e1dc` | Ouvrir r5 pour le minimum 30 000 et la référence simple. |
| Robert de la revue Folio | `71c8fb4b9d5e45fe98a4b4942e07c41e` | r5 30 000 ; r10 40 000 ; r15 erreur de saisie conservée ; r20 retrait 40 000/perte 1 000 → minimum 74 400. |
| Amira de la revue Folio | `49ed5ae5903f41c297909b644ff7599a` | Comparaison historique initiale à 10 % de TSLA. |
| Variante persistante Amira | `4a654c3cd06646c5a7765ff58820633d` | 5 % de TSLA ; origine parent r5, parent inchangé. |
| Entrée incomplète, reprise de transmission | `fedca8757f2540e7a2348bc22f63dd54` | `waiting`, un seul run ; capital/retrait/positions inconnus. |
| Impossibilité antérieure | `1f7d3a73d5924a09ba73925655dce389` | Retrait supérieur au capital ; certificat borné, aucune allocation. |

Ne pas relancer les scénarios AWS pour simplement consulter leur résultat. Les scripts qui créent de nouvelles études sont explicitement séparés des tests de lecture.

## Contrôles disponibles

- Backend exécuté : `python -m pytest tests/test_folio_api.py tests/test_decision_store_review.py tests/test_decision_service_review.py -q` — 36 succès, détail dans `proofs/backend-verification.json`.
- `tests/folio_review.cjs` : revue indépendante ; modes documentés. Les modes `revision*` et `variant` déclenchent des opérations AWS, contrairement à lecture/export/aperçu.
- `tests/folio_entry.cjs` : **nouvelle étude AWS** avec perte simulée de réponse HTTP après commit ; ne pas relancer sans objectif nouveau.
- `tests/folio_finish.cjs` : captures, invariance, preuves, responsive et reflow ; aucune mutation ni inférence.
- `tests/folio_navigation.cjs` : chargement et réponse de reprise retardée dans le navigateur ; réponse synthétique, aucune reprise AWS réelle.

Le contrôle de zoom utilise un viewport CSS de 720 × 500, équivalent au reflow à 200 % depuis 1440 × 1000. Un essai initial avec la propriété CSS `zoom:2` a été écarté comme protocole différent du zoom navigateur ; aucun résultat de ce protocole n’est présenté comme une réussite. Axe reste indéterminé sur certains contrastes à cause de la texture ; les couleurs de base ont été contrôlées séparément, avec une hypothèse d’assombrissement du papier.

## Ce qui reste à approfondir

Essai humain de compréhension et de navigation, lecteur d’écran réel et configurations d’accessibilité variées. Le moteur conserve ses deux familles qualifiées et ses exclusions documentaires/financières ; l’interface ne comble pas ces limites. L’intégration ne comporte ni déploiement cloud, ni ordres de bourse, ni résidence canadienne garantie.

Pour refaire la sauvegarde locale après de nouvelles études terminées : `.venv/bin/python scripts/snapshot_folio.py`. Privilégier un moment sans étude en cours ; le script conserve les deux bases via SQLite backup, écrit l’archive par remplacement atomique et relit les hashes du code et des bases. Il remplace la sauvegarde intégrée courante, jamais le dossier `folio_reference/`. Aucun appel AWS n’est effectué.
