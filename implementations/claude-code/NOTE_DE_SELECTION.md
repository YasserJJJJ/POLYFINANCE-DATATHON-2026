# Note de sélection

Export du 2026-11-15 préparé par `evaluation-fusion/export/preparer_export.py` du projet d'origine (non joint), à partir de l'arbre de travail, modifications non commitées comprises. Le projet d'origine n'a pas été modifié : la sélection et les retouches portent sur une copie.

Fichiers inclus : 260. Chaque fichier a son rôle et son origine dans `MANIFESTE.json`.

## Catégories retirées

| Catégorie | Fichiers | Raison | Conséquence pour la reproduction |
|---|---|---|---|
| Historique Git | 29 | l'export est un instantané ; le commit source est dans le manifeste | aucune |
| Environnement installé et caches | 6504 | réinstallable par `uv sync` | aucune |
| Instructions et réglages de l'assistant de développement | 2 | consignes de travail, non du produit ; leurs conventions techniques sont reprises dans LIRE_EN_PREMIER.md | aucune |
| Données du jeu de départ | 9 | le projet ne les redistribue pas (.gitignore, data/README.md) | à copier dans data/raw/alphaforge_starter/ ; sans elles, `alphaforge rendre` fonctionne et 23 des 51 tests passent ; `demo`, `agent` et l'application échouent |
| Textes de tiers téléchargés pour la recherche | 2047 | aucun droit de redistribution ; 880 Mo | références, liens et empreintes dans research/sources/manifeste*.json et research/R07 |
| Cadrage, mandat et suivi de travail | 11 | consignes historiques, état de séance et coordination entre sessions : remplacés par LIRE_EN_PREMIER.md | quelques documents conservés y renvoient encore (liste en fin de note) |
| Conversions de l'énoncé et de la présentation des organisateurs | 36 | documents des organisateurs, communs aux participants | aucune |
| Livrables vides | 2 | titres seuls ou dossier vide | aucune |
| Lanceurs et scripts propres au poste | 3 | lancement de l'outil de développement et saisie d'identifiants d'atelier ; le dernier, modifié localement, n'a pas été ouvert | docs/acces-aws.md cite ces scripts ; l'accès se configure par un profil AWS nommé `alphaforge` |
| Notes de recherche sur l'outil de développement | 2 | portent sur la session de développement, non sur le produit | quelques documents de conception y renvoient |
| Fiches et journaux intermédiaires de la recherche | 51 | sorties brutes des passes de recherche et de revue (2,8 Mo) ; leurs conclusions sont dans docs/refonte/ et research/R07 | les documents de conception citent ces fiches comme pièces de travail |
| Pièces de l'étape précédente du dossier d'évaluation | 17 | relevés bruts, scripts d'assemblage, manifeste d'une autre archive, doublon de l'inventaire | evaluation-fusion/*.md citent `MANIFESTE.json` : lire celui de la racine ; ils citent aussi outils/ et inventaire/ |
| README d'origine | 1 | contenait des consignes de reprise pour l'assistant de développement ; remplacé par un renvoi vers LIRE_EN_PREMIER.md | aucune ; pyproject.toml exige la présence du fichier |
| Caches et fichiers système | 27 | réinstallables ou sans contenu | aucune |
| Sorties intermédiaires des essais techniques | 50 | bases et journaux régénérables, pages de documentation téléchargées, script lié au poste | les comptes rendus (.txt, .json) et les LISEZMOI.md des essais restent ; relancer un essai recrée ses bases |
| Inventaire brut du compte AWS de l'atelier | 2 | noms de ressources d'un compte | résumé dans research/experiences/technique/services_aws/LISEZMOI.md |
| Anciennes versions de dossiers | 6 | copies antérieures des dossiers de l'agent | trois exécutions d'agent en moins dans les mesures ; elles restent décrites dans evaluation-fusion/preuves/dossiers-d-agent.txt |

## Retouches faites dans la copie

- `LIRE_EN_PREMIER.md`, `NOTE_DE_SELECTION.md`, `MANIFESTE.json` et `README.md` sont écrits pour l'export.
- Un bandeau d'état est ajouté en tête des documents de `docs/refonte/`, de `docs/acces-aws.md` et des documents de `evaluation-fusion/` : il dit ce qui est conçu et non construit, ce qui est historique et quelles pièces citées ne sont pas jointes. Le texte d'origine suit, inchangé.
- 65 chemin(s) du poste d'origine sont remplacés par `<poste-local>` dans les fichiers texte (surtout des traces d'essais techniques).
- Aucun fichier de code du produit, de test ou de configuration n'est retouché (origine « copié tel quel » dans le manifeste).

## Contrôles faits sur la copie par le script

- Secrets : recherche de 8 motifs (clés et jetons AWS, clés privées, clés d'API, adresses signées, numéro de compte dans un ARN, chemin personnel) dans tous les fichiers texte : aucune occurrence. Les identifiants de requête AWS présents dans les dossiers sont des preuves d'appel, non des secrets ; le compte n'apparaît que par ses quatre derniers chiffres.
- Liens symboliques : aucun dans la copie (0 dans le projet d'origine hors environnement, non copiés).
- Syntaxe : tous les fichiers Python de la copie se compilent (67 fichiers).
- Références documentaires : les chemins cités entre accents graves dans les fichiers Markdown ont été confrontés au contenu de l'archive. 46 désignent une pièce non jointe (liste ci-dessous) ; 14 n'ont pas pu être résolus automatiquement (chemins abrégés ou exemples).

## Vérifications faites depuis l'archive décompressée

Faites le 15 novembre 2026 sur le poste d'origine (macOS, uv 0.13.0, Python 3.13.0), dans un dossier vide, à partir du fichier ZIP et non du projet d'origine.

| Contrôle | Commande | Résultat observé |
|---|---|---|
| Installation | `uv sync` | environnement créé d'après `uv.lock`, sans erreur |
| Sans les données | `uv run pytest -q tests/test_evidence.py` | 14 tests réussis |
| Sans les données | `uv run pytest -q` | 23 réussis, 18 en échec, 10 en erreur : les échecs viennent tous de l'absence du jeu de départ |
| Sans les données | `cp -R runs <copie>` puis `uv run alphaforge rendre --sortie <copie>` | huit dossiers relus, recontrôlés et rendus, 0 affirmation en échec |
| Avec le jeu de départ copié dans `data/raw/alphaforge_starter/` | `uv run pytest -q` | 51 tests réussis |
| Avec le jeu de départ | `uv run alphaforge demo tous --sortie <dossier>` | `robert-tsla` : 15 affirmations, 52 valeurs reliées, 0 en échec ; `amira-croissance` : 18, 51, 0 |
| Avec le jeu de départ | comparaison valeur par valeur de cette relance aux `dossier.json` joints dans `runs/` | 3 964 et 1 660 valeurs ; seules diffèrent la date de création et des durées d'appel |
| Imports | `import datathon2026.app, datathon2026.agent` | réussis ; dix outils déclarés |

Le jeu de départ employé pour ces essais est celui du poste d'origine, aux empreintes inscrites dans `MANIFESTE.json`. Il n'a pas été remplacé par des données simulées et n'est pas dans l'archive.

**Non vérifié depuis l'archive**

- Tout ce qui appelle AWS : `alphaforge aws-verifier`, `alphaforge agent`, le mode agent de l'application. Aucun appel AWS n'a été déclenché pour cet export. La dernière exécution réelle de l'agent date du 15 novembre à 17 h 51, sur le projet d'origine, avec le même `agent.py` (`evaluation-fusion/preuves/`).
- L'application web n'a pas été lancée depuis l'archive : seul l'import du module est vérifié ; ses tests (`tests/test_app.py`) passent.
- Les scripts de `research/experiences/` et les essais techniques n'ont pas été relancés : ils demandent des bibliothèques absentes de `pyproject.toml` et, pour plusieurs, un accès AWS. Leur syntaxe seule est contrôlée.
- Aucun autre système que macOS.

## Références vers des pièces non jointes

Ces renvois subsistent dans des documents conservés tels quels. La pièce visée existe dans le projet d'origine.

| Pièce citée | Citée par |
|---|---|
| `CAPACITES.csv` | `evaluation-fusion/CAPACITES.md`, `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` … |
| `CLAUDE.md` | `docs/refonte/diagnostic-et-contrat.md`, `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/PRESENTATION.md` |
| `__pycache__` | `evaluation-fusion/INDEX-DES-PREUVES.md` |
| `assets_universe.csv` | `LIRE_EN_PREMIER.md`, `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/PRESENTATION.md` |
| `cadrage/01_VISION_INITIALE_PROFIL_ET_ARCHITECTURE_OUVERTE.md` | `docs/decisions.md` |
| `corporate_actions.csv` | `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/PRESENTATION.md` |
| `data/raw/alphaforge_starter` | `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md`, `evaluation-fusion/REPRODUCTION.md` |
| `data/raw/alphaforge_starter/README.md` | `evaluation-fusion/PRESENTATION.md` |
| `docs/cadrage` | `docs/refonte/diagnostic-et-contrat.md`, `docs/refonte/fiches-des-agents.md`, `docs/refonte/recherche-processus-professionnels.md`, `docs/refonte/revue-par-questions.md` |
| `docs/carte-questions.md` | `docs/refonte/diagnostic-et-contrat.md` |
| `docs/coordination.md` | `docs/refonte/architecture/00-synthese.md`, `docs/refonte/architecture/01-resolutions.md`, `docs/refonte/architecture/02-dossier.md`, `docs/refonte/architecture/03-contrats-des-agents.md` … |
| `docs/etat.md` | `docs/refonte/architecture/00-synthese.md`, `docs/refonte/architecture/01-resolutions.md`, `docs/refonte/architecture/02-dossier.md`, `docs/refonte/architecture/03-contrats-des-agents.md` … |
| `docs/exigences.md` | `evaluation-fusion/PRESENTATION.md` |
| `docs/one-pager.md` | `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` |
| `docs/video.md` | `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` |
| `evaluation-fusion/MANIFESTE.json` | `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md`, `evaluation-fusion/REPRODUCTION.md` |
| `evaluation-fusion/inventaire` | `evaluation-fusion/PRESENTATION.md` |
| `evaluation-fusion/outils/preparer_archive.py` | `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/REPRODUCTION.md` |
| `evaluation-fusion/outils/releves_de_preuve.py` | `evaluation-fusion/PRESENTATION.md` |
| `fx_usdcad_daily.csv` | `LIRE_EN_PREMIER.md`, `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/PRESENTATION.md` |
| `inventaire` | `evaluation-fusion/CAPACITES.md`, `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` … |
| `macro_rates.csv` | `docs/refonte/diagnostic-et-contrat.md`, `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/PRESENTATION.md` |
| `outils/assembler_capacites.py` | `evaluation-fusion/CAPACITES.md`, `evaluation-fusion/PRESENTATION.md` |
| `prices_daily.csv` | `LIRE_EN_PREMIER.md`, `evaluation-fusion/CAPACITES.md`, `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/INDEX-DES-PREUVES.md` … |
| `raw/alphaforge_starter` | `data/README.md` |
| `raw/alphaforge_starter/README.md` | `data/README.md` |
| `recherches_documentation.sh` | `research/experiences/technique/services_aws/LISEZMOI.md` |
| `research/R08-outils-routes-et-ressources-2026-11-15.md` | `docs/refonte/architecture/06-comparatif-technique.md`, `docs/refonte/recherche-processus-professionnels.md`, `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` … |
| `research/fiches` | `docs/refonte/architecture/00-synthese.md`, `docs/refonte/architecture/01-resolutions.md`, `docs/refonte/architecture/02-dossier.md`, `docs/refonte/architecture/03-contrats-des-agents.md` … |
| `research/fiches/architecture` | `docs/refonte/architecture/00-synthese.md`, `docs/refonte/architecture/10-pratiques-observees.md` |
| `research/fiches/architecture/pratiques-verification.json` | `docs/refonte/architecture/10-pratiques-observees.md` |
| `research/fiches/redaction` | `docs/refonte/architecture/01-resolutions.md` |
| `research/outils/journal_recherches.jsonl` | `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` |
| `research/sources/textes` | `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` |
| `runs/_archives` | `evaluation-fusion/CAPACITES.md`, `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` … |
| `runs/_archives/amira-agent-2026-11-15-0646-avant-garde-lexicale` | `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` |
| `runs/_archives/robert-agent-2026-11-15-0642-avant-garde-lexicale` | `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` |
| `runs/_archives/robert-agent-2026-11-15-avant-corrections` | `evaluation-fusion/INDEX-DES-PREUVES.md`, `evaluation-fusion/PRESENTATION.md` |
| `scripts/claude-bedrock.sh` | `docs/acces-aws.md`, `docs/refonte/architecture/06-comparatif-technique.md`, `evaluation-fusion/DEPENDANCES.md`, `evaluation-fusion/INDEX-DES-PREUVES.md` … |
| `scripts/configurer-aws-workshop.sh` | `docs/acces-aws.md`, `docs/decisions.md`, `docs/refonte/architecture/00-synthese.md`, `evaluation-fusion/DEPENDANCES.md` … |
| `scripts/message-reprise.txt` | `docs/refonte/diagnostic-et-contrat.md`, `evaluation-fusion/INDEX-DES-PREUVES.md` |
| `sorties/appels_bedrock.log` | `research/experiences/technique/langgraph/LISEZMOI.md` |
| `sorties/doc` | `research/experiences/technique/services_aws/LISEZMOI.md` |
| `sorties/essai1.txt` | `research/experiences/technique/services_aws/LISEZMOI.md` |
| `sorties/essai1_inventaire.json` | `research/experiences/technique/services_aws/LISEZMOI.md` |
| `sources_metadata.csv` | `data/README.md`, `evaluation-fusion/PRESENTATION.md` |

## Chemins cités non résolus automatiquement

Chemins abrégés, noms d'exemple ou fichiers produits à l'exécution.

- `AWS/Bedrock` (docs/refonte/fiches-des-agents.md)
- `Datathon-2026` (research/experiences/technique/langgraph/LISEZMOI.md)
- `catalog.workshops.aws/join` (docs/acces-aws.md)
- `critique-ensemble.json` (evaluation-fusion/INDEX-DES-PREUVES.md)
- `docs/cadrage/01` (docs/refonte/diagnostic-et-contrat.md)
- `docs/cadrage/02` (docs/refonte/diagnostic-et-contrat.md)
- `docs/refonte/architecture/00` (evaluation-fusion/DEPENDANCES.md)
- `fichier.py` (evaluation-fusion/PRESENTATION.md)
- `journal/principale.jsonl` (research/experiences/technique/dossier_maison/LISEZMOI.md)
- `redaction` (evaluation-fusion/INDEX-DES-PREUVES.md)
- `research/R04` (docs/refonte/diagnostic-et-contrat.md)
- `research/R07` (evaluation-fusion/INDEX-DES-PREUVES.md)
- `research/R08` (evaluation-fusion/INDEX-DES-PREUVES.md)
- `sorties/doc/11` (research/experiences/technique/services_aws/LISEZMOI.md)
