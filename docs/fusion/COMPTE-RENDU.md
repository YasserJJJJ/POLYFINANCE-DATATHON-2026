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


# Tranche 3 — AWS : preuve d’appel, robustesse et publication

## 1. Commits et périmètre

- Départ : `f767a3b2b5bb98bac0c23619d973bbb8b9b2aca7` (`fusion/t1`).
- Code : `b385412f60c960509f14e7e3430e7c29bf977e40`, `feat(fusion): tracer Bedrock et durcir le déploiement AWS`.
- Clôture : commit documentaire portant la présente section et les preuves, désigné par l’étiquette locale `fusion/t3`.
- Arbre : `/Users/vpro/Documents/ChatGPT/POLYFINANCE-fusion-aws`, branche `fusion/aws`.
  La branche d’analyse n’a été ni lue ni fusionnée ; aucun fichier protégé, original importé ou archive n’a été modifié.
  Le [contrôle de périmètre](preuves/tranche3/controle-perimetre.json) compare les fichiers au commit de départ.

Le porteur a autorisé le push sans force de `fusion/aws`, les créations AWS après plan,
le Guardrail et quelques analyses réelles. Sa précision est : « Agent intégrateur sur Astra ; tests du produit
autorisés sur Nova/Sonnet via Bedrock alphaforge. » La [route vérifiée](preuves/tranche3/ROUTE-EXECUTION.json)
est Amazon Bedrock / `global.openai.gpt-6-astra`, profil `alphaforge`, région `us-east-1`.
Aucun sous-agent n’a été lancé : sa route séparée n’était pas vérifiable avant appel.
Aucun fichier d’identifiants, `.env` ou script d’enregistrement d’identifiants n’a été ouvert.

## 2. Provenance et justification du code ajouté

**Transfert A → K6.** Les lectures `ResponseMetadata.RequestId`, `stopReason`, `usage.inputTokens`,
`usage.outputTokens`, `metrics.latencyMs` et le calcul de latence de secours proviennent de
`implementations/claude-code/src/datathon2026/agent.py`, méthode `_converse`, lignes 172–188.
L’extrait importé a été comparé à l’archive originale : SHA-256 du fichier
`6cb2dc9841c93ba346ef71bdfed604ab2136312904069ffc89d036ffabf324c2`.
Le [manifeste de provenance](preuves/tranche3/provenance-appels.json) donne la correspondance des champs.

Les ajouts sont des adaptations nécessaires aux contrats et aux défauts observés :

- `llm.py` adapte ces métadonnées à K6, enregistre succès, erreurs, refus d’ancrage et blocages Guardrail,
  sans contenu de requête ou réponse. Un `ContextVar` immuable et une portée ouverte dans le fil d’analyse
  isolent les requêtes ; le crochet final existant livre puis vide le journal.
- L’API ouvre cette portée pour les analyses HTTP et le flux NDJSON, et lie les traces aux indices
  **à partir de zéro** de `appels_modele`. Les appelants des agents restent inchangés : par défaut,
  modèle léger → Profileur ; source d’ancrage → Rédacteur ; principal sans source → Sceptique.
- Le défaut de reprise est corrigé par un délai configurable (15 s par défaut, 1–300 s), un état par modèle,
  et la recréation des clients après erreur d’identifiants. Un refus de Sonnet ne coupe pas Nova.
  STS est revérifié après expiration du cache. Le mode `off` n’importe pas boto3.
- Le script de déploiement C est conservé : mêmes S3, IAM, Lambda/Mangum et Amplify.
  Les ajouts couvrent le plan en lecture seule, les ARN Bedrock résolus, le CORS exact, la concurrence de 2,
  le journal de créations et le nettoyage borné. La branche Amplify est obtenue avant Lambda pour connaître l’origine.
- Les scripts de vérification sont des outils de réception : ils capturent les dossiers et comparent les mêmes entrées.
  Ils n’ajoutent aucun calcul financier ni agent. Les tests d’infrastructure utilisent de faux clients.
- Mangum était déjà déclaré ; aucune nouvelle bibliothèque produit n’est ajoutée. La dépendance transitive
  `python-dateutil` est bornée à `<3` pour respecter botocore. Le paquet publié contient Mangum 0.22.0 et
  dateutil 2.9.0.post0 : [versions et empreinte](preuves/tranche3/paquet-lambda.json).

**Corrections révélées par AWS réel.** Le raccordement Guardrail initial envoyait 5 000 caractères comme
question alors qu’AWS limite celle-ci à une unité de 1 000 caractères. Il filtrait aussi le catalogue du Profileur.
Le raccordement corrigé s’applique au Rédacteur disposant d’une source : question courte, source complète
et contenu à contrôler explicitement qualifiés. Les contrôles en code ne sont pas remplacés.
La boucle des variables Guardrail dans le déployeur pouvait également écraser la clé S3 du ZIP ; ce défaut
est corrigé et testé. Les essais initiaux et leur erreur AWS sont conservés, identifiés comme tels.

## 3. Vérifications et résultats

Commandes exactes, environnement et sorties : [index des preuves](preuves/tranche3/README.md).

```text
$ cd backend
$ ALPHAFORGE_LLM=off ALPHAFORGE_DATA_BUCKET='' <python-venv> -m pytest -q --tb=short
268 passed in 8.50s
```

[Sortie finale](preuves/tranche3/tests-finaux.txt). Départ : 249 tests, tous conservés ; 19 tests ajoutés.
Le test de concurrence lance deux vraies requêtes HTTP NDJSON simultanées sur Uvicorn, avec un faux client
Converse synchronisé : aucun identifiant d’appel ne passe d’un dossier à l’autre, même après les refus d’ancrage.
Le test hors ligne enlève le profil et interdit tout import boto3/botocore ; Robert reste égal à la référence figée
hors champs variables autorisés. Les reprises d’erreurs, le CORS, les ARN, l’ordre concurrence/URL publique,
les refus AWS et le nettoyage limité aux créations sont testés.

```text
$ python infra/deployer.py --plan
Compte 471112821226 ; us-east-1 ; S3 privé, IAM, Lambda (concurrence 2), Amplify, CloudWatch.
Bedrock : les deux profils et quatre ARN de modèles retournés par AWS ; aucun joker Bedrock.
$ python infra/creer_guardrail.py --verifier
Rien n’a été créé (--verifier).
```

[Plan initial complet](preuves/tranche3/plan-deploiement.json),
[plan avec ARN du Guardrail](preuves/tranche3/plan-deploiement-avec-guardrail.json).
La [simulation IAM](preuves/tranche3/simulation-iam.json) a rendu `allowed` pour les 33 actions vérifiées
sur le rôle `WSParticipantRole`. Aucune création de sonde n’a été tentée. La création réelle a ensuite réussi.

```text
$ python infra/deployer.py --journal docs/fusion/preuves/tranche3/creation-deploiement.json
alphaforge-lambda.zip : 28.5 Mo
/api/sante : ok=True · agents IA (Bedrock) : oui
vite v6.4.6 : 39 modules transformed ; built in 469ms
Interface : https://main.d1d3b8g2y5hkdd.amplifyapp.com
```

Le paquet fait 93 320 268 octets décompressés. Son SHA-256 distant correspond exactement au ZIP local.
Le build utilise le verrou existant ; les fichiers sources et le verrou du frontend sont inchangés.
[Sortie complète du déploiement](preuves/tranche3/deploiement.txt).

### Les trois analyses locales requises, sans Guardrail

| Cas | Appels | Jetons entrée + sortie | Durée | Verdict, règles, options, grille |
|---|---:|---:|---|---|
| Robert / TSLA | 3 | 6 035 | 8,978 s, somme des agents | strictement identiques hors ligne |
| Amira / BTC-USD | 3 | 5 703 | 10,309 s HTTP | strictement identiques hors ligne |
| Texte libre contradictoire | 4 | 10 371 | 23,224 s HTTP | strictement identiques hors ligne |

Les [trois dossiers complets](preuves/tranche3/local/) et le [tableau par agent](preuves/tranche3/APPELS.md)
contiennent un identifiant de requête pour chaque appel. Le texte contradictoire force un second essai du
Rédacteur après un refus du contrôle en code. La grille du contrat s’appelle `bascule`.
La durée HTTP totale de Robert n’a pas été capturée au premier essai de l’outil ; sa durée d’agents est réelle,
et n’est pas présentée comme une mesure HTTP.

### Réception réelle du Guardrail et de la publication

- Normal : [Robert avec Guardrail corrigé](preuves/tranche3/guardrail-normal-corrige/bilan.json),
  19,134 s, 4 appels, 16 059 jetons. Les deux appels Rédacteur passent Bedrock ; le second passe également
  le contrôle d’ancrage en code. Les quatre décisions restent identiques hors ligne.
- Conseil : [preuve complète](preuves/tranche3/guardrail-conseil-corrige.json), `guardrail_intervened`,
  identifiant `2a3210a5-4b7e-44d2-9cbc-2733a949fcb7`, gabarit du véritable Rédacteur restitué exactement.
- Public : [santé](preuves/tranche3/public/sante.json), interface HTTP 200, prévol CORS accepté pour l’origine
  Amplify et refusé pour une autre origine. IAM effectif égal au plan ; S3 privé ; concurrence réservée de 2.
- [Dossier public de Robert](preuves/tranche3/public/robert-bedrock.json) : 4 appels réels, 16 087 jetons,
  tous avec identifiants et `end_turn`. Verdict, règles, options et grille inchangés face à la référence hors ligne.
- [Archivage S3](preuves/tranche3/public/archivage.json) : copie JSON strictement égale,
  clé `dossiers/20261116-012751-f1522c45.json` dans `alphaforge-471112821226-us-east-1`.
- [Flux NDJSON mesuré](preuves/tranche3/public/reception-ndjson.json) : première ligne à 18,302999 s,
  dernière à 18,329150 s ; seulement 0,026151 s entre elles. **Réponse reçue d’un bloc**, cohérente avec
  `InvokeMode=BUFFERED` constaté dans la configuration Lambda. Aucun écran n’a été ajusté dans cette tranche.

## 4. Écarts et raisons

- Le Guardrail a été créé avant le déploiement principal, après D et son plan : son ARN exact peut ainsi
  figurer dès la première politique Lambda. Le plan enrichi a été affiché avant les autres créations.
- La plage de 8–14 s et environ 8 000 jetons n’est **pas systématiquement respectée** : le texte contradictoire
  prend 23,2 s ; le Guardrail et les reprises d’ancrage portent Robert à environ 16 000 jetons.
  Les mesures sont publiées telles quelles ; aucune optimisation ni modification des agents hors périmètre n’a été introduite.
- Le premier outil de capture cherchait `grille` au lieu de `bascule`. Il a été corrigé et le dossier Robert
  déjà enregistré a été repris sans nouvel appel. Les sorties de l’échec et de la reprise sont conservées.
- Le venv de tests ne contient pas pip et son magasin de certificats ne valide pas le HTTPS public sur ce poste.
  L’empaquetage et la réception publique utilisent le Python système avec les bibliothèques existantes du venv
  sur `PYTHONPATH`. TLS reste vérifié. Aucun fichier ni paquet du dépôt principal n’a été modifié.
- La première résolution de dépendances prenait dateutil 4, incompatible avec botocore. Le ZIP publié utilise
  la contrainte corrigée ; la première sortie d’avertissement reste dans les preuves.
- Le port local 8765 était occupé. Il n’a pas été touché ; les serveurs propres à cette vérification ont utilisé
  18763 et 18764 et ont été arrêtés après réception.

## 5. Ce qui tourne, ce qui reste à faire et limites

**Tourne sur AWS :** interface Amplify, API Lambda publique, données et archives S3 privées, rôle IAM restreint,
journaux CloudWatch et Guardrail version 1 actif. [Inventaire et suppressions](preuves/tranche3/RESSOURCES.md).
Aucune ressource n’est laissée dans un état d’échec. Aucun contournement de refus AWS n’a été nécessaire.

**Prêt pour la tranche 4 :** les changements restent sur `fusion/aws`, sans fusion dans l’intégration.
Les agents devront passer explicitement leur nom à `appeler` / `appeler_json` ; la convention par défaut
assure la compatibilité dans cette tranche. L’interface devra tenir compte du flux Lambda reçu d’un bloc.
La comparaison de portefeuilles et les changements de la tranche 2 n’ont pas été incorporés ni requalifiés ici.

**Non exécuté :** suppression des ressources après le succès, test de charge public, vidéo de démonstration,
changement de l’interface, fusion de branches, lancement de la tranche 4. Le contrôle de santé confirme STS ;
les appels Converse dans les dossiers constituent la preuve effective d’inférence.

La Function URL reste publique. CORS limite le navigateur ; la concurrence de 2 borne les appels simultanés,
pas la dépense cumulée. Le déploiement conserve une limite Lambda de 90 secondes. Les mesures ne garantissent
pas les futures latences ou la disponibilité du compte de l’événement.
Le **16 novembre à 13 h 59**, selon les documents des équipes, le compte est détruit : hébergement, Guardrail,
données S3 et journaux disparaîtront. Le code et les preuves conservées dans Git subsisteront.

## 6. Décisions attendues

Aucune décision ne bloque la clôture de la tranche 3. Le push sans force de `fusion/aws` est autorisé après
les tests verts ; l’étiquette `fusion/t3` reste locale. Les coûts et durées supplémentaires du Guardrail sont
signalés pour la préparation de la démonstration. La réunion des branches et le traitement de l’affichage
reviennent au prompt 4 ; aucune fusion ni demande d’autorisation supplémentaire n’est faite ici.
