# Compte rendu — tranche 1 : socle et contrats

## 1. Réalisé et commits

La branche `fusion-corrections-deploiement` est alignée sur C évalué, les trois
références sont identifiées, A est conservé comme référence et B est inchangé.
Les contrats sont présents et inactifs ; les trois défauts de qualification
visés sont corrigés. Les tranches 2 et 3 partiront du commit désigné par
l'étiquette locale **`fusion/t1`**, dont le SHA final est donné dans la réponse de clôture.

| Étape | Commit | Résultat |
|---|---|---|
| Socle | `c161a55169d90b31f370338a7539cd01efa07769` | Fusion à deux parents ; quatre dossiers identiques à C avant les ajouts. |
| Références | `d2b893e2b9b1e3b489366a11c687957c0bd88bc9` | Import A, identification A/B/C, kit et dossiers complets figés des trois personas. |
| Contrats | `b46fde2043913c4e3bf2f458ac0f04653eb1ab39` | K1/K3/K6/K7, documentation K1 à K7 et pont de lecture autorisé. |
| Qualification | `bce87e5250faf737eace1bfd0cbd36b0b6c9923d` | Demande impossible, actif hors univers et types HTTP. |

Étiquettes locales : `fusion/ref-avant` → `f565abdff58ab4ab07c1f0706e266cc03c408d90` ;
`fusion/ref-C` → `6761d6636c6c712663cdaf76c739d2bc8f991aef` ; `fusion/t1` à la clôture.
La publication est autorisée uniquement vers `origin/fusion-corrections-deploiement`,
sans force, après les contrôles verts ci-dessous. Le push suit le commit de ce
compte rendu ; sa confirmation et le SHA distant sont fournis dans la réponse finale.

Les six conflits attendus ont été résolus depuis C : `backend/api.py`,
`backend/tests/test_banc_12_cas.py`, `frontend/src/App.jsx`,
`frontend/src/etapes/Etape4Verdict.jsx`, `frontend/src/styles.css`, `infra/deployer.py`.
`git checkout fusion/ref-C -- backend frontend infra data` a aussi remplacé les
mélanges automatiques. `frontend/src/composants/Logo.jsx`, absent de C, a été retiré.
Les versions antérieures du style clair (`styles.css`), des composants et des pages
ont cédé la place à C ; les fichiers concernés sont listés dans
[ecarts-interface-avant-C.txt](preuves/tranche-1/ecarts-interface-avant-C.txt).
Tout cet habillage antérieur reste récupérable par `fusion/ref-avant`.
Le seul changement ultérieur de l'interface est le pont K1 explicitement autorisé.

## 2. Provenance des fichiers et motif du code neuf

- **A** : [IMPORT.md](../../implementations/claude-code/IMPORT.md) et
  [IMPORT_MANIFEST.json](../../implementations/claude-code/IMPORT_MANIFEST.json)
  donnent l'archive, son SHA-256, chacun des 259 chemins et son empreinte.
  Les fichiers de travail **et leurs blobs Git** sont identiques aux originaux.
- **B** : aucun fichier transféré ou dupliqué. La copie `implementations/codex/`
  est identique à `fusion/ref-avant`. [REFERENCES.md](../../implementations/REFERENCES.md)
  impose l'archive 0.7.0 pour les transferts suivants. La comparaison des deux
  fichiers confirme `analytics.py` identique et `datasets.py` différent :
  [reference-B.json](preuves/tranche-1/reference-B.json).
- **C** : source `6761d6636c6c712663cdaf76c739d2bc8f991aef` ; chaque chemin et
  identifiant de blob du socle est dans [PROVENANCE-C.json](preuves/tranche-1/PROVENANCE-C.json).
- **Kit** : 17 fichiers copiés sans modification, origines et SHA-256 dans
  [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json).
- [Liste exhaustive des fichiers ajoutés](preuves/tranche-1/FICHIERS-AJOUTES.txt),
  incluant références, tests et preuves. Les trois archives originales ont de
  nouveau été contrôlées : [VERIFICATION-ORIGINAUX.json](preuves/tranche-1/VERIFICATION-ORIGINAUX.json).

| Code neuf ou adapté | Motif autorisé | Portée |
|---|---|---|
| `profil.normaliser_portefeuille`, champs de `Dossier`, `llm.journal_appels`, affectations finales dans l'orchestrateur | Contrat manquant | Poids/origine, version 2, comparaison et journal vides ; aucun calcul financier activé. |
| `profil.symboles_portefeuille`, ses appels dans Gardien/Analyste/Sceptique/orchestrateur, `frontend/src/portefeuille.js` et ses lectures à l'étape 2 | Adaptation nécessaire | Pont K1 autorisé ; les poids du profil ne sont pas modifiés par une lecture. |
| `gardien.erreurs_entree`, validation avant les scores, exclusion en chaîne ; normalisation et précontrôle partagés dans `api.py` | Incompatibilité réelle | Évite les erreurs de types, les conclusions sur un montant impossible et le message brut pour un symbole hors univers. |
| Trois nouveaux fichiers de tests Python, test Node, références JSON et manifests | Adaptation nécessaire | Non-régression, vérification des contrats, des entrées et de la provenance. |

Aucun module fonctionnel de A ou B n'est intégré. `calculs.py`, `donnees.py`,
les dépendances, les données et `infra/` restent identiques à C. Aucun seuil,
modèle du produit ou formule financière n'a été changé.

## 3. Vérifications et sorties

Tests exécutés avec `ALPHAFORGE_LLM=off` et `ALPHAFORGE_DATA_BUCKET=''`.
Python 3.13.0 dans `backend/.venv`, dépendances du socle installées telles quelles.
Les tests de clients Bedrock utilisent les doubles déjà présents dans le socle.

### Socle avant changements

```text
$ cd backend && .venv/bin/python -m pytest -q
201 passed in 15.68s
```

Sortie complète : [tests-socle.log](preuves/tranche-1/tests-socle.log).
`cd frontend && npm install && npm run build` réussi :
[npm-install.log](preuves/tranche-1/npm-install.log),
[build-socle.log](preuves/tranche-1/build-socle.log).

```text
$ git diff --stat fusion/ref-C -- backend frontend infra data
$ git diff --stat fusion/ref-avant -- implementations
```

**Aucune sortie pour les deux commandes à l'étape 2**, avant ajout de A et des
contrats. Sorties conservées : [diff-socle.log](preuves/tranche-1/diff-socle.log)
et [diff-import-B.log](preuves/tranche-1/diff-import-B.log).

### Validation finale

```text
$ cd backend && .venv/bin/python -m pytest -q
249 passed in 8.77s
```

Les 201 tests du socle sont conservés sans modification ; 48 sont ajoutés
(3 références, 27 cas de contrat, 18 cas de qualification).
Sortie complète : [tests-finaux.log](preuves/tranche-1/tests-finaux.log).

```text
$ cd frontend && npm run build
vite v6.4.6 building for production...
✓ 39 modules transformed.
dist/index.html                   0.66 kB │ gzip:  0.39 kB
dist/assets/index-D9CBsb7u.css   18.98 kB │ gzip:  4.93 kB
dist/assets/index-CvQqsOYw.js   191.95 kB │ gzip: 61.83 kB
✓ built in 508ms
```

[Sortie complète](preuves/tranche-1/build-final.log).
`cd frontend && node --test tests/portefeuille.test.js` : **1 test réussi**,
[sortie complète](preuves/tranche-1/test-pont-interface-final.log).

Les dossiers complets avant/après sont égaux en neutralisant uniquement les
`duree_ms` de trace et les trois ajouts `version_contrat`, `comparaison`,
`appels_modele`. Toutes les valeurs, règles, faits, options, textes et grilles
sont comparées. Les empreintes normalisées sont identiques pour chaque persona :
[COMPARAISON-REFERENCES.json](preuves/tranche-1/COMPARAISON-REFERENCES.json).
Les références d'origine n'ont pas été régénérées après ajout des contrats.

| Persona | Verdict conservé | Faits | Durée HTTP locale |
|---|---|---:|---:|
| Robert | `incoherent` | 16 | 70,65 ms |
| Amira | `ajustement` | 15 | 44,48 ms |
| Mateo | `incoherent` | 16 | 37,14 ms |

Les contrôles HTTP utilisent un serveur Uvicorn local, en mode hors ligne,
arrêté à la fin en ciblant uniquement son processus. Résultats :
[reception-http.json](preuves/tranche-1/reception-http.json).

| Entrée | Résultat observé |
|---|---|
| 120 000 sur 100 000 CAD | HTTP 200, `indetermine`, règle `donnees`, « Le montant dépasse l'épargne totale. » |
| Horizon `"4"`, montant `"80000"` | HTTP 200 ; même dossier que les valeurs numériques natives. |
| Montant `"inconnu"` ou horizon `"bientôt"` | HTTP 200, `indetermine`, règle `donnees`, raison française ; aucun calcul ni appel de modèle. |
| Symbole inconnu | HTTP 422, « L'actif demandé ne fait pas partie des 31 actifs du jeu de départ. » |
| Symbole inconnu dans le flux | Message terminal `erreur`, `statut: 422` ; protocole NDJSON conservé. |
| Exclusion `"Énergie"` | Même dossier qu'avec `["Énergie"]` ; exclusion de Mateo rouge. |

Contrôle des motifs de secrets demandé avant commit : aucun fichier de A
correspondant ([commande et résultat](preuves/tranche-1/controle-secrets-A.log)).
Aucun `.env`, fichier d'identifiants AWS ou `infra/enregistrer_identifiants.ps1`
n'a été ouvert. [Route d'exécution vérifiée](preuves/tranche-1/ROUTE-EXECUTION.json).

## 4. Écarts et raisons

- Le refspec local ne récupérait que la branche d'intégration : `git fetch origin`
  a été complété par une récupération explicite de la branche C, au SHA attendu.
- Le pont K1 exigeait de toucher ses appelants : **autorisation explicite du
  porteur**, « Oui, uniquement ce pont de compatibilité ». L'affichage et les
  calculs restent identiques. Voir [REVISIONS.md](REVISIONS.md).
- `data/raw/.gitkeep` était présent dans A ; il est exclu conformément à « sans
  data/raw ». Aucune donnée brute n'était dans l'archive. `.DS_Store` du kit omis.
- Les métadonnées `libc` retirées par `npm install` ont été restaurées depuis C.
  Aucun fichier de dépendances n'a changé.
- Les espaces finaux de certains documents originaux de A sont conservés pour
  respecter l'identité des empreintes. Les alertes de `git diff --check` sur ces
  originaux sont consignées ; le code neuf passe ce contrôle.
- Pour les types invalides, la validation HTTP commune arrête les trois routes
  avant le Profileur. Elle utilise la règle du Gardien, afin qu'une chaîne erronée
  ne soit ni calculée ni remplacée par une valeur tirée du texte.

## 5. Non réalisé ou non vérifié

- Tranches 2, 3 et 4 : aucun transfert fonctionnel, comparaison de portefeuilles,
  instrumentation réelle des appels, déploiement ou nouvel écran de restitution.
- Aucun appel réel aux modèles du produit pendant cette tranche ; l'égalité
  avec/sans une inférence Bedrock réelle n'a pas été rejouée ici. Les contrôles
  hors ligne et les tests simulés du socle sont verts.
- Le gain financier de K5 n'est pas encore actif et n'est pas revendiqué.
- Défaut connu laissé à la tranche 2 : Robert avec `retrait_prevu_ans: null`
  passe à `ajustement` sans question. Constat reproduit sans correction :
  [constat-retrait-manquant.json](preuves/tranche-1/constat-retrait-manquant.json).
- Aucun déploiement ni aucune ressource AWS créés. Les scripts d'infrastructure
  n'ont pas été exécutés.

## 6. Décisions attendues

Aucune décision ne bloque la tranche 1. Les choix réservés au porteur pour les
tranches suivantes restent ceux de la section 14 du cadre. L'autorisation de
push est acquise ; celle du pont K1 est consignée. Aucun accord supplémentaire
n'est demandé pour la clôture de cette tranche.
