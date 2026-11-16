# AlphaForge — à lire en premier

Ce fichier fait autorité pour cette archive. En cas de désaccord avec un autre document, le code puis ce fichier priment.

Cette archive décrit **une** implémentation d'AlphaForge (Datathon PolyFinances 2026), préparée pour être comparée puis fusionnée avec deux autres, indépendantes. Elle ne prétend pas servir de base à la fusion et ne dit rien des deux autres, qui n'ont pas été consultées.

Simulation uniquement : aucune transaction réelle, aucun conseil financier personnalisé. Les profils, portefeuilles et demandes sont fictifs.

## 1. Identité et état réel

| | |
|---|---|
| Identifiant | **identifiant à attribuer** (A, B ou C non fourni ; le préfixe `X` des identifiants `X-CAP-nnn` est à remplacer) |
| Paquet | `datathon2026`, version 0.1.0 (`pyproject.toml`) ; commande `alphaforge` |
| Date de l'export | 15 novembre 2026 |
| Source | arbre de travail local ; commit unique `55d164c` ; **modifications non commitées incluses** (dont `src/datathon2026/agent.py`, `evidence.py`, `tests/test_evidence.py`, toute la recherche et la conception du 15 novembre) ; aucun dépôt distant |
| Détail | `MANIFESTE.json` (fichiers, empreintes, origine de chaque fichier) ; `NOTE_DE_SELECTION.md` (ce qui a été retiré, vérifications faites sur l'export) |

L'archive contient trois choses de nature différente. Ne pas les confondre :

1. un **produit implémenté** : `src/datathon2026/`, `tests/`, `config/`, `scripts/`, avec des dossiers déjà produits dans `runs/` ;
2. une **recherche et des expériences hors produit** : `docs/refonte/*.md`, `research/` ; leurs résultats ne sont pas dans le produit ;
3. une **architecture cible à quatre agents, conçue et non construite** : `docs/refonte/architecture/`. Aucune ligne de cette architecture n'est en production ; seul un prototype de son dossier versionné existe, hors produit.

## 2. Ce que cette solution apporte

- **Textes sans nombre écrit par le modèle.** Les textes d'un dossier ne contiennent que des références (`{{R-0001}}`, `{{cmp:A:B}}`) vers des valeurs calculées par du code et inscrites dans un registre. Un vérificateur déterministe refuse un chiffre manuscrit, une grandeur en lettres, un comparatif manuscrit, une référence inconnue (`src/datathon2026/evidence.py`). Le sens des comparaisons et leur accord grammatical sont calculés par le code. Le contrôle est lexical et numérique, pas sémantique (section 6).
- **Dossier de décision revérifiable.** `dossier.json` est la source de vérité : affirmations, enregistrements, trace des outils, empreintes des données, et pour l'agent les identifiants de requête AWS, jetons et latences. `alphaforge rendre` le recontrôle et régénère la page HTML sans modèle ni recalcul.
- **Deux chemins sur les mêmes outils.** Un enchaînement fixe en Python (déterministe, sans AWS) et un agent unique sur Amazon Bedrock (API Converse) qui choisit ses calculs parmi dix outils et accepte une demande libre.
- **Application web locale** : choix du profil, hypothèses modifiables, recalcul, mode agent.
- **Recherche hors produit** : expériences statistiques sur ce que cinq ans de données permettent d'affirmer (`research/R09-experiences-discriminantes-2026-11-15.md`), registre de sources avec niveau de lecture (`research/R07-registre-des-sources-2026-11-15.md`), essais techniques (LangGraph, Strands Agents, services AWS).
- **Conception** : contrat d'un dossier versionné (pièces immuables, journal chaîné), contrats de quatre agents, typologie des résultats, critères de réception (`docs/refonte/architecture/`).

Inventaire détaillé : `evaluation-fusion/CAPACITES.md` (77 contributions, onze champs chacune).

## 3. Architecture actuelle (produit implémenté)

Schémas : `evaluation-fusion/schemas/composants-produit.svg` et `sequence-agent.svg`.

| Module (`src/datathon2026/`) | Rôle | Dépend de |
|---|---|---|
| `evidence.py` | registre typé, syntaxe des références, vérificateur des textes | bibliothèque standard |
| `paths.py`, `data.py` | emplacements, lecture du jeu de données | pandas |
| `analytics.py` | marché en devise de base, mesures, portefeuille, balayages | `data` |
| `tools.py` | `Session` : sept outils déterministes, registre, trace | `analytics`, `data`, `evidence`, `config/` |
| `dossier.py` | `Dossier`, sections, `to_dict` / `from_dict`, contrôle | `evidence` |
| `report.py` | page HTML autonome, graphiques SVG | `evidence` |
| `workflow.py` | enchaînement fixe : `robert`, `amira` | `tools`, `dossier`, `analytics` |
| `agent.py` | `BedrockAgent` : instruction système `SYSTEM`, dix outils, boucle Converse, deux corrections au plus | `tools`, `dossier`, `workflow`, `boto3` |
| `cli.py` | commande `alphaforge` : `demo`, `agent`, `rendre`, `aws-verifier` | tout |
| `app.py` | serveur local `127.0.0.1:8765` et page web | tout |

Parcours : profil et demande → enchaînement fixe ou agent → appels d'outils inscrits au registre → dossier soumis (`soumettre_dossier`) → vérificateur → `dossier.json` → `dossier.html`. L'application renvoie le HTML sans rien écrire sur disque.

Configuration : `config/personas.toml` (trois profils de l'énoncé : Amira, Mateo, Robert), `config/scenarios.toml` (deux scénarios écrits d'avance, Robert et Amira, et la table des groupes d'exposition, écrite à la main). Le prompt chargé à l'exécution est la constante `SYSTEM` de `agent.py` ; il n'y en a pas d'autre.

Détail : `evaluation-fusion/PRESENTATION.md` section 4, `docs/technique.md`.

## 4. Installation et essai

Prérequis : `uv` ; Python 3.12 ou plus (`.python-version` indique 3.13). Dépendances du produit : `boto3`, `numpy`, `pandas` ; `pytest` pour les tests (`uv.lock`).

**Données à fournir.** Le jeu de départ remis aux participants n'est pas dans l'archive (le projet ne le redistribue pas, voir `.gitignore` et `data/README.md`). Copier le dossier `alphaforge_starter` dans `data/raw/`. Le produit lit `prices_daily.csv`, `fx_usdcad_daily.csv` et `assets_universe.csv`. Les empreintes attendues sont dans `MANIFESTE.json`, clé `donnees_non_incluses`. Sans ces fichiers, `alphaforge rendre` fonctionne et 23 des 51 tests passent (dont les 14 de `tests/test_evidence.py`) ; `demo`, `agent` et l'application échouent.

```bash
uv sync
uv run pytest -q                                   # tests ; sans AWS
uv run alphaforge demo tous --sortie /tmp/essai    # enchaînement fixe, Robert et Amira ; sans AWS
cp -R runs /tmp/essai-runs && uv run alphaforge rendre --sortie /tmp/essai-runs   # recontrôle une copie des dossiers joints ; sans AWS, sans données
uv run python -m datathon2026.app --ouvrir         # application locale, http://127.0.0.1:8765
```

Avec AWS (appels facturés ; profil nommé `alphaforge`, région `us-east-1`, accès au modèle `global.anthropic.claude-sonnet-5-5` sur Amazon Bedrock ; aucun identifiant dans le code ; guide : `docs/acces-aws.md`) :

```bash
uv run alphaforge aws-verifier                      # lecture seule, aucun appel de modèle
uv run alphaforge agent robert --sortie /tmp/essai  # scénario de Robert par l'agent
uv run alphaforge agent mateo --demande "…" --sortie /tmp/essai   # demande libre
```

`--sortie` désigne le dossier des dossiers : `demo` et `agent` y écrivent, `rendre` relit et réécrit ceux qui s'y trouvent. Sans `--sortie`, les trois commandes travaillent dans `runs/` et écrasent les dossiers joints.

Parcours représentatif : `uv run alphaforge demo robert --sortie /tmp/essai`, puis ouvrir `/tmp/essai/robert-tsla/dossier.html`. Demande : « J'aimerais consacrer une partie de mon portefeuille à Tesla ; on en parle partout. » Résultat attendu : 15 affirmations, 52 valeurs reliées, 0 en échec.

Ce qui est quoi dans l'archive :

| Élément | Nature |
|---|---|
| `config/personas.toml`, `config/scenarios.toml` | données **fictives** (profils de l'énoncé, portefeuilles et seuils posés comme hypothèses) |
| `runs/*/dossier.json` et `.html` | **résultats précalculés** le 15 novembre 2026 : deux par l'enchaînement fixe (`robert-tsla`, `amira-croissance`), six par l'agent sur Bedrock (exécutions réelles, non reproductibles à l'identique) |
| `evaluation-fusion/preuves/` | sorties de commandes **réellement exécutées** le 15 novembre entre 17 h 50 et 17 h 55 sur le poste d'origine |
| `research/experiences/sorties/` | sorties d'expériences hors produit, non relancées pour cet export |
| `docs/refonte/architecture/07-dossier-illustratif.md` | exemple **illustratif** de conception, pas une sortie du produit |

Reproduction détaillée et effets de bord : `evaluation-fusion/REPRODUCTION.md`.

## 5. État des capacités

Quatre états, à ne pas confondre : **Conçu** (contrats ou architecture décrits), **Implémenté** (code présent), **Exécuté** (fonctionnement observé, avec une trace), **Vérifié** (critère explicite et résultat disponible : test, assertion). L'inventaire emploie en plus **Proposé** (idée documentée).

| Capacité | État | Où |
|---|---|---|
| Vérificateur des textes, registre, comparaisons calculées, statut hérité | Vérifié (tests) | `evidence.py`, `tests/test_evidence.py` |
| Calculs : grille hebdomadaire, pire baisse, fenêtres glissantes, portefeuille rééquilibré, contributions à la variance, balayages | Vérifié (tests) ; rendement annualisé, volatilité et corrélation : Exécuté, sans test dédié | `analytics.py`, `tools.py`, `tests/test_analytics.py` |
| Enchaînement fixe (Robert, Amira) | Vérifié (tests) et Exécuté | `workflow.py`, `runs/robert-tsla`, `runs/amira-croissance` |
| Boucle d'agent, outils, soumission contrôlée | Vérifié contre un **client simulé** (`tests/test_agent.py`) ; appel réel à Bedrock : Exécuté (dix dossiers produits, dont six joints) | `agent.py`, `runs/*-agent`, `runs/*-libre-*` |
| Preuve d'appel AWS dans le dossier | Exécuté | champ `aws` de `dossier.json` |
| Revérification hors ligne | Exécuté | `cli.py`, `evaluation-fusion/preuves/rendre.txt` |
| Rendu HTML et graphiques | Exécuté | `report.py` |
| Application locale | Vérifié pour le recalcul (`tests/test_app.py`) ; mode agent : Exécuté sur déclaration, sans sortie conservée ; historique de séance : Implémenté, sans test | `app.py` |
| Qualification de la demande, recherche pendant la demande, critique de fond, versionnement, reprise | **Absents du produit** | — |
| Méthodes statistiques (rééchantillonnage par blocs, écarts appariés, grille d'hypothèses, comparateurs par règle) | Exécuté ou Vérifié **hors produit** | `research/experiences/`, `research/R09-…` |
| Prototype du dossier versionné et de son greffier | Vérifié hors produit, sans modèle (118 assertions) | `research/experiences/technique/dossier_maison/` |
| Essais LangGraph, Strands Agents, services AWS | Exécuté hors produit | `research/experiences/technique/` |
| Architecture à quatre agents, contradicteur, portes, types de résultats, critères de réception | Conçu ; catalogue de règles : Proposé (aucune table écrite) ; aucune instruction système rédigée | `docs/refonte/architecture/` |
| Déploiement AWS au-delà de l'appel du modèle | Absent : aucune ressource créée | — |

Tests : 51 réussis sur le poste d'origine le 15 novembre (`evaluation-fusion/preuves/pytest.txt`). Les vérifications refaites depuis l'export sont dans `NOTE_DE_SELECTION.md`.

## 6. Méthodes et limites

**Conventions du produit** (`analytics.py`, `docs/technique.md`, `docs/decisions.md`) : valeurs en dollars canadiens au dernier taux de change connu, reporté vers l'avant seulement ; rendements hebdomadaires sur une semaine se terminant le vendredi ; volatilité annualisée par √52 ; pire baisse depuis un sommet ; pire rendement sur fenêtres glissantes ; portefeuille fictif rééquilibré chaque semaine ; contributions à la variance par ligne et par groupe ; parts en fractions ; cinq ans d'historique (12 novembre 2021 au 12 novembre 2026). Les séries macroéconomiques et les opérations sur titres du jeu de départ ne sont pas employées.

**Résultat de recherche à connaître** (hors produit, `research/R09-…`, `docs/refonte/diagnostic-et-contrat.md`) : sur cinq ans, un niveau de risque ou un rendement moyen n'est pas établi par les données ; ce que les expériences soutiennent, sous leurs conditions, ce sont des écarts appariés entre options. Le produit affiche pourtant des niveaux historiques. Les méthodes qui répondent à ce constat ne sont pas intégrées.

**Limites et défauts connus du produit**

- Un agent, pas quatre : ni qualification de la demande, ni critique de fond. Le vérificateur ne juge ni la pertinence d'un calcul ni un raisonnement ; il laisse passer des formulations hors de sa liste lexicale.
- Après deux corrections, un dossier encore en échec est retenu avec `verification.ok = false` au lieu d'être rejeté (`agent.py`, lu dans le code, jamais observé, sans test).
- `share_sweep` rend la borne haute de la grille comme part maximale quand le seuil n'est jamais franchi (cas observé : `runs/robert-libre-or`).
- Aucun versionnement ni reprise ; `dossier.json` n'a pas de numéro de version de format ; les sorties sont écrasées.
- Les messages du modèle ne sont pas conservés ; les sorties de l'agent ne sont pas reproductibles à l'identique ; un seul modèle a été exécuté.
- Aucun coût en dollars mesuré. Mesuré : appels, jetons, latence par exécution (`evaluation-fusion/preuves/dossiers-d-agent.txt`).
- Univers fermé au jeu de départ ; groupes d'exposition écrits à la main ; aucune donnée ESG ; paramètres de scénario posés comme hypothèses.
- Les dossiers de `runs/` produits par l'agent le matin du 15 novembre ont pu l'être avec une version antérieure de `agent.py` ; seule l'exécution de 17 h 51 (`evaluation-fusion/preuves/execution-agent-2026-11-15/`) correspond de façon certaine au code joint.

**Limites de la documentation jointe.** Les sections 4 à 9 de `evaluation-fusion/PRESENTATION.md`, `DEPENDANCES.md`, `REPRODUCTION.md` et `INDEX-DES-PREUVES.md` ont été rédigées par des sous-agents à partir du code et n'ont pas été contre-vérifiées par un second lecteur. Les numéros de ligne valent pour le code joint.

Références scientifiques et techniques : `research/R07-registre-des-sources-2026-11-15.md` (chaque source avec son lien, son niveau de lecture réel et ce qu'elle soutient) et `docs/refonte/architecture/10-pratiques-observees.md`. Les textes des sources ne sont pas joints ; leurs empreintes sont dans `research/sources/manifeste.json` et `manifeste-pratiques.json`.

## 7. Conseils pour la fusion

**Extractible seul**

- `evidence.py` avec `tests/test_evidence.py` : aucune dépendance hors bibliothèque standard. Français seulement.
- Les fonctions de mesure de `analytics.py`.
- `Dossier.from_dict` avec `report.render` : rendre un `dossier.json` existant.
- `BedrockAgent._converse` et le champ `aws` (preuve d'appel) ; `cli.aws_check`.
- `research/experiences/technique/dossier_maison/dossier.py` : prototype du dossier versionné, sans lien avec `src/datathon2026/dossier.py` malgré le nom.
- À l'état de conception : la typologie des résultats (`docs/refonte/architecture/05-types-de-resultats.md`) et les critères de réception (`09-reception.md`).

**À garder ensemble**

- Les outils de `tools.py` avec le registre, `analytics`, `config/` et les données : ils ne rendent que des identifiants.
- L'instruction système `SYSTEM`, le schéma `soumettre_dossier` et le vérificateur : l'instruction décrit ce vérificateur et lui seul ; sa liste lexicale est recopiée de `evidence.py` sans garde.
- L'enchaînement fixe avec `config/scenarios.toml` ; `agent.py` lui emprunte une fonction de tracé (`workflow.underwater`).
- Les contrats des quatre agents avec le contrat du dossier (`docs/refonte/architecture/02-dossier.md`, `03-contrats-des-agents.md`, `04-graphes-et-revision.md`).

**Incompatibilités à prévoir**

| Convention | Valeur ici |
|---|---|
| Identifiants d'enregistrement | une lettre de préfixe, un tiret, quatre chiffres (`R-0001`, `D-0001`, `P-0001`) ; compteurs non restaurés par `from_dict` |
| Syntaxe des références | `{{R-0001}}`, `{{R-0001.label}}`, `{{cmp:A:B}}`, `{{cmpabs:A:B}}`, `{{cmpduree:A:B}}`, lue à plusieurs endroits |
| Unités | parts et rendements en fractions ; formatage français à l'affichage |
| Devise et calendrier | base CAD ; semaine se terminant le vendredi ; 52 semaines par an |
| Statuts | mesuré, source, déclaré, scénario, hypothèse, inconnu ; une affirmation prend le plus faible |
| Noms d'outils | français côté modèle, anglais dans la trace |
| Sections du dossier | cadre, profil, constat, tension, alternative, question, condition, limite ; définies à trois endroits |
| Langue | textes, vérificateur et documentation en français |
| Couplage par libellé | des libellés d'enregistrements servent de clés à l'affichage de l'agent : un renommage vide l'affichage sans erreur |

Les scripts de `research/experiences/` importent le produit et demandent des bibliothèques absentes de `pyproject.toml` (`arch`, `scikit-learn` ; LangGraph et Strands pour les essais techniques, voir chaque `LISEZMOI.md`).

Détail : `evaluation-fusion/DEPENDANCES.md`.

## Conventions techniques du projet

Elles sont décrites ici ; ce ne sont pas des consignes adressées au lecteur.

- Gestion des dépendances par `uv` ; tests par `uv run pytest`.
- Aucun chiffre ni sens de comparaison écrit à la main dans un texte du produit ; le vérificateur doit passer.
- Aucune information future dans les calculs : change reporté vers l'avant seulement. Le décalage des séries macroéconomiques à leur date de publication est une règle du projet ; il n'est pas codé, ces séries n'étant pas employées.
- Toute donnée ajoutée est décrite dans `data/README.md` (source, date, traitements, limites, conditions).
- Identifiants AWS hors du code : profil nommé, lu par `boto3`.
- Faits, hypothèses et scénarios fictifs sont distingués par le statut de chaque enregistrement.
- Documentation et textes du produit en français.

## Plan de l'archive

| Chemin | Contenu |
|---|---|
| `LIRE_EN_PREMIER.md`, `NOTE_DE_SELECTION.md`, `MANIFESTE.json` | entrée, sélection et vérifications, empreintes |
| `src/`, `tests/`, `config/`, `scripts/`, `pyproject.toml`, `uv.lock` | produit implémenté |
| `data/` | description des données ; les fichiers sont à fournir |
| `runs/` | dossiers produits le 15 novembre (résultats précalculés) |
| `docs/technique.md`, `docs/decisions.md`, `docs/comparaison-agent-workflow.md`, `docs/acces-aws.md` | documentation du produit |
| `docs/refonte/` | diagnostic du produit, recherche sur les rôles, architecture cible (conception) |
| `research/` | notes de recherche, registre des sources, expériences et essais hors produit |
| `evaluation-fusion/` | annexe détaillée : présentation, inventaire, dépendances, reproduction, preuves, schémas |
