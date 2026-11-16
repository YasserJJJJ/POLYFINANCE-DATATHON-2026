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

# Tranche 2 — Analyse du portefeuille appariée

## 1. Réalisé et commits

Départ vérifié : `f767a3b2b5bb98bac0c23619d973bbb8b9b2aca7` (`fusion/t1`).
Arbre isolé `/Users/vpro/Documents/ChatGPT/POLYFINANCE-fusion-analyse`,
branche `fusion/analyse`. Le dépôt principal reste propre sur ce même SHA ;
aucune lecture ou fusion de `fusion/aws`.

| Commit | Résultat |
|---|---|
| `a61b6bd` | Moteur historique B, tests transférés et opération `blend` de A. |
| `996b849` | K3/K5 actifs, faits sourcés, recherche exacte dans les deux sens, révision de monotonie, retrait décisif et critique du portefeuille. |
| `7e9f24c` | Régénération séparée des trois références ; chaque changement de verdict, de niveau et d'option expliqué dans le message. |

Le commit portant cette clôture reçoit l'étiquette **locale** `fusion/t2`.
Destination autorisée : `origin/fusion/analyse`, sans force, après tests verts.
Aucune fusion dans la branche d'intégration et aucun déploiement.

Les étapes A à E et la critique facultative F sont réalisées. K3 emploie les
poids K1, l'ajout proportionnel de A et un appel apparié à B. Le Gardien conserve
ses seuils et juge la pire baisse du portefeuille après la demande. Les mesures
du titre calculées par C restent séparées des mesures du portefeuille par B.

| Persona et poids fictifs explicites | Avant | Après | Écart | Verdict ; changement de règle |
|---|---:|---:|---:|---|
| Robert : XIU.TO, XBB.TO, RY.TO à 1/3 chacun | −14,256677 % | −20,595922 % | −6,339245 pts | `incoherent` conservé ; capacité `ok → orange` |
| Amira : QQQ et NVDA à 1/2 chacun | −46,806061 % | −50,609205 % | −3,803144 pts | `ajustement → incoherent` ; capacité `ok → rouge` |
| Mateo : XIU.TO et XBB.TO à 1/2 chacun | −13,159563 % | −12,062254 % | +1,097309 pts | `incoherent` conservé par exclusion ; niveaux inchangés |

Robert : l'ajustement le plus proche reste 38 000 CAD, désormais `ajustement`.
Amira/BTC : aucun montant admissible au pas de 100 CAD n'améliore l'état ;
l'ancienne version à 6 800 CAD disparaît. Son option XIU.TO à 10 000 CAD devient
`ajustement`. Les valeurs des **47 faits antérieurs** des trois références sont
inchangées ; 16 faits s'ajoutent à chaque dossier. Voir le
[comparatif complet](preuves/tranche-2/changements-references.json).

Robert sans date de retrait conserve le verdict `ajustement` de ses données.
L'hypothèse d'un retrait à quatre ans donnerait `incoherent` : une question
décisive et un fait HYPOTHESE l'expliquent, sans compléter son profil.

## 2. Provenance et code neuf

Archives originales préservées :

- A, `IMPLEMENTATION_IDENTIFIANT-A-ATTRIBUER_2026-11-15(claude-code).zip` :
  `89fa9270fe7e307287c357c76cbce002744d39c4d33083ddc10b431af4e6b967`.
- B, `IMPLEMENTATION_IDENTIFIANT_A_ATTRIBUER_2026-11-15 (codex).zip` :
  `ecdf7282383886213c3e526b659aa2a404b8a753f998f835b38441f7f128773c`.
- C, `IMPLEMENTATION_identifiant-a-attribuer_2026-11-15 (Yahya).zip` :
  `d05b2736b9fd9a891f55dfa137bb4503d8f02e3c1b1cf10f6d76c5b24a259a75`.

| Archive, chemin sous sa racine | Destination | SHA-256 du fichier original |
|---|---|---|
| B : `alphaforge_app/analytics.py` | `backend/alphaforge/moteurs/historique/analytics.py` | `fbe8fbdb57080c2652169aea66c5d35fcb54e31087847d05ce72f5e3cbf92b4f` |
| B : `alphaforge_app/datasets.py` | `backend/alphaforge/moteurs/historique/datasets.py` | `fc747e8c8ff8d56ea5d4c0d7d3f0cd4adc4891cf584ec22bdfe261246e1029e9` |
| B : `tests/test_analytics.py` | `backend/tests/test_moteur_historique.py` | `d5f309f489483f6a2495ed82dbb98c788129ff84fe34e0cd614d12170f9d832d` |
| A : `src/datathon2026/analytics.py`, fonction `blend` | `backend/alphaforge/moteurs/allocation.py` | `588ad1ca468e08d233a2b4ec28783e847b45e94729afb356b9f0559583c3e433` |

Les deux modules B sont identiques octet pour octet hors en-tête ; le test B
change seulement ses imports ; le corps de `blend` est identique à l'extrait
original. Ni formule ni dépendance ajoutée. Les `__init__.py` sont les marqueurs
du paquet transféré. [Manifeste](preuves/tranche-2/transferts.json) et
[vérification finale](preuves/tranche-2/controle-origines.json).

| Code neuf ou raccordement | Motif autorisé et rôle |
|---|---|
| `portefeuille.py` | **Adaptation nécessaire** : K1/K2 vers B, K3 en unités publiques vérifiées, validation et raisons d'indisponibilité, écarts, fenêtres et limites. |
| Caches du jeu, des comparaisons et de `fx_on` | **Adaptation nécessaire** : répéter les montants sans recharger les données ni retrier les mêmes dates de change. Réponses exactes de B conservées. |
| Sous-calcul `comparer_pertes` | **Incompatibilité réelle** : recherche exhaustive étendue et plafond d'une seconde. Réutilise `validate_weights`, `_cad_panel`, `_wealth`, `drawdowns` de B ; aucune formule remplacée. Égalité testée avec le calcul complet. K3 reste produit par `compare_portfolios`. |
| `analyste.py`, `sources.py`, `docs/sources.md` | **Contrat manquant** : chaque métrique, poids, fenêtre, écart et limite reliés à des faits ; faits HYPOTHESE pour équipondération, attribution et non-monotonie. Registre régénéré. |
| `gardien.py` | **Adaptation nécessaire** : K5, fallback explicite et règle commune à la restitution et à la recherche ; rejet préalable par les autres règles inchangées. **Incompatibilité réelle** : recherche exhaustive dans les deux sens, conformément à l'arbitrage. |
| `orchestrateur.py` | **Contrat manquant** : question décisive de retrait et exemple de non-monotonie. **Adaptation nécessaire** : seuls champs `sens`/`constat` de l'ajustement et pont de texte neutre, sans réécriture de l'ordre des agents. |
| `sceptique.py` | **Adaptation nécessaire** : vérification fermée `portefeuille_entier`, recalcul et trois issues, plafond de trois objections, sans effet sur le verdict. |
| `personas.py`, tests, références et scripts de preuve | **Contrat manquant** : poids explicites, réception K2–K5, erreurs, exactitude, provenance, performances et faux client sans inférence. |

## 3. Vérifications et sorties

Commandes exécutées dans l'arbre isolé. L'interpréteur existant du dépôt
principal est utilisé en lecture ; les modules, tests et données proviennent
de l'arbre `fusion/analyse`.

```sh
cd /Users/vpro/Documents/ChatGPT/POLYFINANCE-fusion-analyse/backend
ALPHAFORGE_LLM=off ALPHAFORGE_DATA_BUCKET='' /Users/vpro/Documents/ChatGPT/POLYFINANCE-DATATHON-2026/backend/.venv/bin/python -m pytest -q --tb=short
```

Départ : **249 passed in 8.83s**. Final : **313 passed in 18.41s**,
[sortie intégrale](preuves/tranche-2/tests-finaux.txt). Aucun test supprimé.
Les huit tests originaux du moteur B sont compris dans le total.

Tests du socle adaptés, avec leur justification :

- `test_banc_12_cas.py` : les douze cas originaux conservés et exécutés dans
  les deux modes ; résultats K5 nouveaux explicites, résultats antérieurs
  toujours exigés avec `approximation`.
- `test_banc.py` : remplacement **autorisé** du seul test de monotonie globale
  par la monotonie conditionnelle et l'égalité de chaque case au recalcul.
  Les contrôles d'horizon et les autres tests sont conservés.
- `test_bout_en_bout.py` : trois signatures de règles distinctes en K5 et
  diversité antérieure des états encore exigée en approximation.
- `test_ancrage.py` : fixture chiffrée de l'ancien mode explicitement placée
  en approximation ; montant proche conservé à 38 000 CAD.
- `test_robustesse.py` : 38 000 CAD attendu au premier état amélioré
  `ajustement`, 38 100 restant `incoherent`.
- Tests T1 `test_contrats_fusion.py` et `test_reference_personas.py` :
  K3 est actif, les poids influencent maintenant le portefeuille ;
  les métriques du titre restent identiques et K3 est désormais figé.

Les nouveaux tests vérifient notamment : Robert à −20,595922 % contre 14,2 %
en approximation ; avant identique à `analyze_portfolio` seul ; égalité exacte
du sous-calcul et de B sur 25 allocations ; 1 228 séances communes ; limites
cryptoactives présentes ; erreurs françaises et portefeuille inconnu ;
ligne déjà détenue ; montant égal ou supérieur à l'épargne ; poids invalides ;
isolation des caches ; question de retrait ; critique fermée.

Le faux client local propose des décisions falsifiées : **verdict, règles,
options, grille et comparaison restent identiques** au mode hors ligne pour
les trois personas. Il n'effectue aucune inférence ni requête réseau.

```sh
cd /Users/vpro/Documents/ChatGPT/POLYFINANCE-fusion-analyse/frontend
npm ci --no-audit --no-fund
npm run build
```

**66 packages**, verrou inchangé ; **39 modules transformed**, **built in
482ms**. [Sortie](preuves/tranche-2/build-final.txt). Aucun fichier source de
l'interface ni fichier de dépendances modifié.

Depuis la racine de l'arbre :

```sh
ALPHAFORGE_LLM=off PYTHONPATH=backend /Users/vpro/Documents/ChatGPT/POLYFINANCE-DATATHON-2026/backend/.venv/bin/python docs/fusion/preuves/tranche-2/rejouer_performances.py
python3 docs/fusion/preuves/tranche-2/verifier_origines.py
git diff --check
```

| Cas | Avant T2, une mesure | Après T2, maximum de trois mesures |
|---|---:|---:|
| Robert | 66,448 ms | 319,557 ms |
| Amira/BTC | 41,791 ms | 617,355 ms |
| Mateo | 33,510 ms | 274,986 ms |
| Amira/XIU.TO, 14 000 CAD | — | 301,206 ms |

Caches applicatifs vidés avant chaque mesure finale ; imports déjà chargés et
cache système de fichiers non purgé. Ces mesures couvrent les cas indiqués,
pas une garantie de latence sur toute taille de portefeuille ou d'épargne.
[Avant](preuves/tranche-2/avant.json), [après](preuves/tranche-2/performances-finales.json).
Le contrôle d'origine réussit ; le contrôle des espaces n'émet aucune erreur.

Route d'inférence de la conversation : `amazon-bedrock-runtime`,
`global.openai.gpt-6-astra`, profil `alphaforge`, région `us-east-1`.
Exécution native pour Python/Git/npm ; aucun sous-agent, sa route préalable
n'étant pas vérifiable. [Preuve](preuves/tranche-2/route-execution.json).

## 4. Écarts et arbitrage du porteur

La monotonie globale est réellement incompatible avec K5. Le porteur a
explicitement choisi **K5 et les verdicts exacts**, puis fixé les six conditions
consignées dans [REVISIONS.md](REVISIONS.md). Toutes sont appliquées :

- Invariant 7 du cadre copié révisé ; original du cadre préservé.
- `_montant_exact` exhaustif au pas de 100 CAD ; recherche de l'ajustement par
  distance croissante, dans les deux sens, baisse prioritaire à égalité.
- Aucun lissage des cases. Robert/TSLA et Amira/BTC restent monotones dans les
  tests ; Amira/XIU.TO donne `ajustement` à 14 000 CAD et `coherent` à 17 500 CAD.
- À partir de 14 000 CAD, le plus proche montant améliorant l'état est
  **16 300 CAD**, à la hausse. Le texte constate seulement qu'à ce montant la
  règle serait respectée ; il ne conseille pas d'acheter davantage.
- Fait HYPOTHESE relié à avant/après/écart et exemple observé dans la grille.

**Transmission au prompt 4 :** les curseurs de l'étape 5 doivent accepter
et afficher la grille **non monotone**, sans la présenter comme une erreur.
Afficher `bascule.monotonie_montant.explication`, son exemple et ses références
de faits. Consommer `option.sens` et `option.constat` ; conserver le constat
neutre pour une variation à la hausse. Le pont de restitution actuel est dans
`orchestrateur.py` ; `agents/redacteur.py` et le frontend n'ont pas été touchés.
Une version ajustée signifie « état amélioré » et ne garantit pas l'état vert.

Le sous-calcul exact de la seule perte évite de produire tous les scénarios B
pour chaque palier exhaustif. Il ne remplace ni le moteur choisi ni ses formules.
L'essai intermédiaire à 1,692 s et les sorties antérieures restent conservés
comme historique d'optimisation, sans être présentés comme le résultat final.

Le premier lancement de pytest depuis la racine a collecté à tort les tests des
implémentations de référence ; lancement corrigé depuis `backend/`. Les
échecs intermédiaires de raccordement et les résultats ultérieurs sont conservés.
Les espaces finaux des lignes `E` du journal pytest intermédiaire ont été
retirés pour le contrôle Git des espaces ; les messages d'échec sont conservés.

Le prompt externe reçu diffère de sa copie T1 : le porteur a ajouté les
autorisations et le mode d'isolation. Son SHA reçu est
`d31de60289a340a6837c74be0a818f989dc64966e9b51fc77f8336dfd29ba761` ;
[copie de preuve](preuves/tranche-2/prompt-2-recu.md). Le manifeste T1 reste
historique. Cet écart explique le premier échec du contrôle naïf contre T1 ;
le contrôle final distingue la version reçue des documents restés identiques.

## 5. Non réalisé ou non vérifié

- G, part de variance par ligne : extension facultative non transférée.
- Aucun appel réel aux modèles du produit, aucune ressource AWS créée,
  aucun déploiement, aucune modification du journal d'appels K6/K7.
- Aucun nouvel affichage de portefeuille ni contrôle visuel des curseurs :
  ils appartiennent au prompt 4. La construction de l'interface existante passe.
- Les références figées excluent les durées et `appels_modele` ;
  l'instrumentation réelle appartient à la tranche 3.
- Le dépôt principal, `implementations/`, les données et tous les fichiers
  réservés sont inchangés. La tranche 3 n'a pas été commencée.

## 6. Décisions attendues du porteur

L'arbitrage K5/monotonie est acquis et ne demande aucune nouvelle confirmation.
La règle d'attribution est exposée comme **hypothèse d'équipe** : un excès de
capacité préexistant ne rend pas la demande rouge si celle-ci ne l'aggrave pas ;
les seuils et l'éventuel orange restent applicables.

Restent à valider les **poids fictifs** proposés : tiers égaux pour Robert,
moitiés égales pour Amira et Mateo, avec leurs symboles initiaux. Cette validation
métier est signalée conformément à la décision 5 du cadre ; elle ne bloque pas
la livraison de la tranche autorisée.

La bascule `ALPHAFORGE_CAPACITE=approximation` reste disponible et testée ;
elle conserve le calcul antérieur en indiquant que le reste du portefeuille
est supposé stable. Le push de cette branche est déjà autorisé.
