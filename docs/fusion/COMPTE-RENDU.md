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
