> **Annexe détaillée**, rédigée le 15 novembre 2026 pour une première archive. Les sections 4 à 9 de la présentation, les dépendances, la reproduction et l'index des preuves n'ont pas été contre-vérifiés par un second lecteur. Le `MANIFESTE.json` cité ici est celui de la racine de cette archive ; `runs/_archives/`, `inventaire/`, `outils/`, `CAPACITES.csv`, `docs/etat.md`, `docs/coordination.md`, `research/R08-…` et `research/fiches/` ne sont pas joints. En cas de désaccord, le code puis `LIRE_EN_PREMIER.md` priment.

# REPRODUCTION

Ce fichier dit comment relancer la réalisation et ce qui a été observé le 15 novembre 2026 entre 17 h 50 et 17 h 55 (`evaluation-fusion/preuves/horodatage.txt` et fichiers voisins). Il porte sur le produit implémenté (`src/datathon2026/`) et, en fin de fichier, sur les expériences hors produit. L'architecture cible à quatre agents (`docs/refonte/architecture/`) est une conception : elle n'a rien à relancer, hormis ses prototypes et essais.

Simulation uniquement : profils fictifs, aucune transaction, aucun conseil financier.

## 1. Prérequis

| Élément | Exigence | Source |
|---|---|---|
| Python | 3.12 ou plus ; `.python-version` désigne 3.13 | `pyproject.toml` (`requires-python`), `.python-version` |
| Gestionnaire | `uv` ; dépendances figées dans `uv.lock` | `pyproject.toml`, `uv.lock` |
| Dépendances | `boto3`, `numpy`, `pandas` ; `pytest` pour les tests | `pyproject.toml` |
| Système | Observé sur macOS seulement, avec `uv` 0.13.0. Autres systèmes : non vérifié. | relevé du 15 novembre |
| AWS | Requis seulement pour `agent`, `aws-verifier` et le mode agent de l'application | section 4 |

La version de Python employée pour les vérifications de 17 h 50 n'est pas inscrite dans les fichiers de preuve, sauf pour le prototype de dossier (Python 3.12.7, `evaluation-fusion/preuves/prototype-dossier.txt`).

## 2. Données : non incluses dans l'archive

L'archive ne contient pas le jeu de départ (motif : aucune autorisation de redistribution constatée, exclusion par prudence et sans analyse de licence ; `evaluation-fusion/MANIFESTE.json`, clé `exclusions`).

1. Copier le dossier `alphaforge_starter` remis aux participants dans `data/raw/alphaforge_starter` (`README.md:14` ; `src/datathon2026/data.py::_read`). Autre possibilité : désigner son emplacement par la variable `DATATHON_STARTER_DIR` (`src/datathon2026/paths.py:9`).
2. Vérifier les empreintes. `MANIFESTE.json`, clé `donnees_non_incluses`, liste neuf fichiers avec taille et SHA-256. Commande, à lancer depuis la racine :

```
python3 - <<'EOF'
import hashlib, json, pathlib
m = json.load(open("evaluation-fusion/MANIFESTE.json"))
for e in m["donnees_non_incluses"]["liste"]:
    p = pathlib.Path(e["chemin"])
    ok = p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == e["sha256"]
    print("conforme" if ok else "ÉCART", e["chemin"])
EOF
```

Observé le 15 novembre vers 18 h sur le poste d'origine : neuf fichiers conformes sur neuf (contrôle fait pour ce document, non consigné dans `preuves/`).

Avec un jeu différent, les dossiers diffèrent : `adj_close` est recalculé à chaque extraction (`data/README.md:7`). Les empreintes de trois fichiers sont aussi inscrites dans chaque dossier produit (enregistrements `D-0001` à `D-0003`).

## 3. Commandes, dans l'ordre

Toutes se lancent depuis la racine du dépôt. Options vérifiées dans `src/datathon2026/cli.py:121-141` et `src/datathon2026/app.py:355-358`.

| N° | Commande | AWS | Écrit | Résultat attendu | Observé le 15 novembre | Preuve |
|---|---|---|---|---|---|---|
| 1 | `uv sync` | Non | `.venv/` | Environnement installé d'après `uv.lock` | Non consigné : aucune sortie de `uv sync` dans `preuves/` | Rien |
| 2 | `uv run pytest -q` | Non | Cache de pytest | Tous les tests réussis | 51 réussis en 1,67 s | `evaluation-fusion/preuves/pytest.txt` |
| 3 | `uv run alphaforge demo tous --sortie <dossier>` | Non | `<dossier>/robert-tsla/`, `<dossier>/amira-croissance/` (`dossier.json`, `dossier.html`), `<dossier>/index.html` | Robert : 15 affirmations, 52 valeurs reliées, 0 en échec ; Amira : 18, 51, 0 (`docs/etat.md:58`) | Identique à l'attendu ; 0,562 s | `evaluation-fusion/preuves/demo.txt` |
| 4 | `uv run alphaforge rendre --sortie <dossier>` | Non | Réécrit `dossier.json` et `dossier.html` de chaque sous-dossier, et `index.html` | Chaque dossier enregistré repasse le vérificateur, 0 en échec | Huit dossiers, 0 en échec, sur une copie de `runs/` | `evaluation-fusion/preuves/rendre.txt` |
| 5 | `uv run alphaforge aws-verifier` | Oui, lecture seule | Rien | Profil utilisé, quatre derniers chiffres du compte, profil d'inférence du modèle `ACTIVE` ; aucun appel de modèle | Profil `alphaforge`, région `us-east-1`, `global.anthropic.claude-sonnet-5-5` : `ACTIVE` | `evaluation-fusion/preuves/aws-verifier.txt` |
| 6 | `uv run alphaforge agent robert --sortie <dossier>` | Oui, facturé | `<dossier>/robert-agent/`, `<dossier>/index.html` | Un dossier conforme au vérificateur ; contenu non fixé d'avance | 22 affirmations, 97 valeurs reliées, 0 en échec ; 6 appels ; 1 min 07 s | `preuves/agent-robert.txt`, `agent-robert-mesures.txt`, `execution-agent-2026-11-15/` |
| 7 | `bash scripts/lancer-app.sh` ou `uv run python -m datathon2026.app [--port N] [--ouvrir]` | Non pour « Calcul de référence » ; oui pour « Agent sur Amazon Bedrock » | Rien sur disque d'après la lecture de `app.py` (dossiers rendus en mémoire) | Page servie sur `http://127.0.0.1:8765`, machine locale seulement | Non relancée le 15 novembre à 17 h 50 | Tests seulement (`tests/test_app.py`, compris dans la ligne 2) ; déclaration de `docs/etat.md:63` pour le matin |

Précisions vérifiées dans le code :

- `demo` accepte `robert`, `amira` ou `tous` (`cli.py:125`) ; il n'existe pas d'enchaînement fixe pour Mateo (`workflow.py:227`).
- `agent` accepte `amira`, `mateo` ou `robert`, et les options `--demande`, `--nom`, `--modele`, `--region`, `--profil` (`cli.py:127-137`). Sans `--demande`, Mateo n'a pas de scénario et la commande s'arrête avec un message (`cli.py:59-61`).
- `--sortie` et `--ouvrir` existent pour `demo`, `agent` et `rendre` ; la sortie par défaut est `runs/` (`cli.py:138-140`).
- `scripts/lancer-app.sh` ajoute `--ouvrir` : un navigateur s'ouvre.
- Code de retour : 0 si tous les dossiers sont produits, 1 sinon (`cli.py:155`).

Pour comparer un dossier relancé au dossier enregistré, comparer les valeurs feuilles des deux `dossier.json`. Observé : `robert-tsla`, 3 964 valeurs, 7 différentes (`cree_le` et six `duree_ms`) ; `amira-croissance`, 1 660 valeurs, 5 différentes (`cree_le` et quatre `duree_ms`). Cette comparaison ne figure pas dans `preuves/demo.txt` ; elle a été faite à la main sur la sortie conservée hors dépôt.

## 4. Prérequis AWS de l'agent

- Un profil AWS nommé, `alphaforge` par défaut, configuré par la personne qui lance la commande (guide : `docs/acces-aws.md`). Le code ne lit ni n'affiche d'identifiant ; aucun identifiant ne doit être écrit dans le dépôt ni dans une commande.
- Région par défaut `us-east-1` ; modèle par défaut `global.anthropic.claude-sonnet-5-5` (`src/datathon2026/agent.py:22-26`).
- Remplacement par option (`--profil`, `--region`, `--modele`) ou par variable (`AF_AWS_PROFILE` ou `AWS_PROFILE` ; `AWS_REGION` ou `AWS_DEFAULT_REGION` ; `AF_BEDROCK_MODEL`).
- Le compte doit avoir accès au profil d'inférence du modèle sur Amazon Bedrock ; `aws-verifier` le contrôle sans appeler de modèle.
- Les identifiants du compte d'atelier sont temporaires : une session expirée donne un message, pas un dossier (`cli.py::aws_check`, `cli.py::run_agent`).
- Sur un autre compte, la disponibilité du modèle n'est pas garantie (`research/R08-outils-routes-et-ressources-2026-11-15.md`, fin de la section des réserves). Ce document écrit `--model` ; l'option réelle est `--modele`.

## 5. Ce qui n'est pas reproductible à l'identique

- **Sorties du modèle.** Titre, texte, nombre d'affirmations, outils appelés, nombre d'appels, jetons et latences changent d'une exécution à l'autre. Quatre exécutions de la demande de Robert donnent 18 à 24 affirmations et 5 ou 6 appels (section 7.2 du dossier factuel). Aucune température ni graine n'est fixée (`agent.py:179`).
- **Identifiants de requête AWS**, date de création, durées.
- **Version du modèle servie** derrière l'identifiant du profil d'inférence : hors du contrôle du dépôt.
- Ce qui reste stable par construction : les valeurs calculées par les outils pour des arguments donnés, et le fait qu'un dossier enregistré a passé le vérificateur.
- **Enchaînement fixe** : reproductible à l'identique hors date de création et durées, à données identiques.

## 6. Effets de bord à connaître

| Action | Effet |
|---|---|
| `demo`, `agent` ou `rendre` sans `--sortie` | Écrit dans `runs/` : remplace le dossier de même nom et `runs/index.html`. Les dossiers enregistrés, qui servent de preuve, sont alors écrasés. Employer `--sortie`. |
| `agent` deux fois sous le même nom | Le second dossier remplace le premier ; aucun archivage automatique (les archives de `runs/_archives/` ont été copiées à la main). |
| `agent`, mode agent de l'application | Appels facturés sur le compte AWS. Coût en dollars non mesuré. |
| `aws-verifier` | Lecture seule : identité, liste et état des profils d'inférence. |
| `uv run pytest` | Crée un cache de pytest dans le dépôt. |
| `uv run python scripts/comparer_agent_workflow.py > docs/comparaison-agent-workflow.md` | Réécrit ce document à partir de `runs/` ; sans redirection, n'écrit rien. |
| `research/experiences/technique/dossier_maison/essais.py` | Réécrit `sorties/dossier_exemple`, `sorties/mesures.json` et les exports PROV du même dossier. |
| `research/experiences/modele_qualification_et_citations.py` | Appelle Amazon Bedrock (facturé) et réécrit `research/experiences/sorties/m1_qualification.json` ou `m2_citations.json`. |
| `evaluation-fusion/outils/preparer_archive.py` | Réécrit `evaluation-fusion/MANIFESTE.json` ; le reste se fait hors dépôt (en-tête du script). |
| Application lancée avant une modification du code | Continue de servir l'ancien code jusqu'à sa relance (`docs/etat.md:64`). |

## 7. Expériences hors produit

Commandes relevées dans l'en-tête de chaque script de `research/experiences/`. Les sorties conservées sont dans `research/experiences/sorties/`. Aucune de ces commandes n'a été relancée le 15 novembre entre 17 h 50 et 17 h 55.

| Script | Commande | Exige | Écrit |
|---|---|---|---|
| `calibration_reechantillonnage.py` | `uv run python research/experiences/calibration_reechantillonnage.py` | Rien (processus simulés, sans données réelles) | Sortie standard |
| `methodes_analyse.py` | `uv run --with arch --with scikit-learn python research/experiences/methodes_analyse.py` | Données ; téléchargement de deux paquets | Sortie standard |
| `ecart_et_niveau.py` | `uv run python research/experiences/ecart_et_niveau.py` | Données | Sortie standard |
| `rendement_d_equilibre.py` | `uv run python research/experiences/rendement_d_equilibre.py` | Données | Sortie standard |
| `dossier_illustratif.py` | `uv run python research/experiences/dossier_illustratif.py` | Données | Sortie standard |
| `parcours_contraste.py` | `uv run python research/experiences/parcours_contraste.py` | Données | Sortie standard |
| `multivers_exploratoire.py` | `uv run python research/experiences/multivers_exploratoire.py > research/experiences/sorties/multivers_exploratoire.json` | Données | Le fichier de la redirection |
| `modele_qualification_et_citations.py` | `uv run python research/experiences/modele_qualification_et_citations.py m1`, ou `m2 CHEMIN LIGNE_DEBUT LIGNE_FIN` | AWS, facturé ; pour `m2`, un texte réglementaire non redistribué | `sorties/m1_qualification.json`, `sorties/m2_citations.json` |

Les scripts à graine fixe (`SEED = 2026` dans leur code) sont annoncés déterministes par leur en-tête ; l'identité de leur sortie à la relance n'a pas été contrôlée pour ce document.

Essais techniques de la conception (`research/experiences/technique/`) :

- `dossier_maison/` : `python3 research/experiences/technique/dossier_maison/essais.py`, bibliothèque standard, sans réseau ni modèle. Observé le 15 novembre à 17 h 55 : 118 assertions réussies en 1,354 s, Python 3.12.7 ; contrôle par le paquet `prov` non fait (paquet absent) (`evaluation-fusion/preuves/prototype-dossier.txt`).
- `langgraph/`, `strands/`, `services_aws/` : commandes dans le `LISEZMOI.md` de chaque dossier. Plusieurs essais appellent Amazon Bedrock ou d'autres services AWS et réécrivent leurs sorties. Non relancés ; leurs commandes n'ont pas été contrôlées une à une pour ce document.

## 8. Ce qui n'a pas été revérifié le 15 novembre entre 17 h 50 et 17 h 55

- `uv sync` sur une machine vierge, et l'installation à partir de l'archive extraite avec les données replacées.
- L'application web : ni lancement, ni parcours au clic, ni mode agent. Dernière vérification déclarée : 15 novembre, 07 h 35 (`docs/etat.md:63`), sans fichier de sortie.
- Les demandes libres par l'agent (`mateo-libre-esg`, `robert-libre-gamestop`, `robert-libre-or`, `amira-libre-bitcoin-or`) et `amira-agent` : seuls leurs dossiers enregistrés le matin ont été revérifiés hors ligne par `rendre`, sans nouvel appel de modèle.
- Les options `--demande`, `--nom`, `--modele`, `--region`, `--profil` et `--ouvrir` : lues dans le code, non exercées à 17 h 50.
- `scripts/comparer_agent_workflow.py` et la concordance de `docs/comparaison-agent-workflow.md` avec `runs/` (les six lignes du tableau des agents concordent avec les `dossier.json` lus pour ce document).
- Toutes les expériences de `research/experiences/*.py` et les essais `langgraph`, `strands`, `services_aws`.
- Tout système autre que macOS ; toute version de Python autre que celle du poste.
- Un second compte AWS, une autre région, un autre modèle.
