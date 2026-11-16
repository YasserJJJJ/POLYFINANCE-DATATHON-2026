# Rapport d'évaluation indépendante — réalisation C (« Second avis »)

Évaluateur : agent indépendant. Date d'exécution : 2026-11-15. Copie de travail : `work/C` (macOS Darwin, Python 3.12.7 dans `work/C/.venv`, Node 22).
Sorties brutes : `reports/C-sorties/` (JSON des cas, journaux, scripts d'essai dans `scripts/`). Mesures : `reports/C-mesures.json`.
Convention d'état : Proposé / Conçu / Implémenté / Exécuté / Vérifié (définis dans le brief). « Archive » = ce que C déclare.

**Incident à signaler d'emblée** : en fin de session, une commande `pkill -f uvicorn` trop large (erreur de ma part) a arrêté trois serveurs uvicorn qui n'étaient pas les miens (processus `alphaforge_app.main:app` ×3 et `prototype.prompt6.server:app`, vraisemblablement ceux des évaluateurs A et B). À relancer si nécessaire. Mes propres serveurs (8000, 5173) sont arrêtés.

---

## 0. Résumé factuel

| Point | Constat |
|---|---|
| Nature | Application complète et cohérente : API FastAPI (114 lignes) + orchestrateur à ordre fixe + moteur de règles en code + React/Vite 5 étapes. ~2 550 lignes de Python applicatif (backend/alphaforge + api.py), 1 211 lignes de tests, ~1 270 lignes de JSX. |
| Installation neuve | `uv venv` + `uv pip install -r backend/requirements.txt` : OK sur Python 3.12 (l'archive annonce 3.14.7). Aucune adaptation. |
| Tests | **201 passed, 0 échec, 0 ignoré** en 10,4 s (données partielles de l'archive) et 13,9 s (jeu complet). Mode hors ligne forcé par `backend/conftest.py:6`. |
| Interface | `npm install` + `npm run build` : OK (38 modules, 514 ms, JS 192 kB). `vite dev` + proxy `/api` → 8000 : OK (index 200, `/api/sante` via proxy). **Pas de test navigateur** (interdit) : parcours décrit d'après le code. Aucun test frontend (absence observée : pas de dossier de test, pas de script `test` dans `frontend/package.json`). |
| Bedrock | Exécuté : 3 exécutions de bout en bout (voir §2). Les deux modèles annoncés répondent (`verifier_bedrock.txt`). |
| AWS hors Bedrock | Lambda, S3, Amplify, Guardrail : **Implémenté (code), jamais exécuté** — conforme à l'archive. Je ne les ai pas exécutés. |
| Portabilité | Python + npm : multiplateforme (exécuté sur macOS). Seul `demarrer.ps1` est Windows ; il force `AWS_PROFILE=datathon`. |
| Principal point fort | Séparation nette code/LLM : verdict, règles, options et grille de bascule **strictement identiques** avec et sans Bedrock sur C1 et C5b (comparaison objet à objet). Traçabilité chiffre → source → méthode → références. |
| Principale limite | Les agents LLM apportent peu : extraction de texte libre (réel), choix de 1-3 vérifications dans un catalogue de 6 (limité), paraphrase contrôlée (quasi identique au gabarit). Un seul levier (score retenu) différencie les profils. Aucune persistance, aucun versionnage. |

---

## 1. Vérification de l'état

### 1.1 Installation, tests, lancement

| Étape | Commande (résumé) | Résultat |
|---|---|---|
| Venv | `uv venv .venv --python 3.12` ; `uv pip install -r backend/requirements.txt` | OK : pandas 3.1.1, numpy 2.5.4, fastapi 0.163.0, uvicorn 0.54.0, boto3 1.44.3 (pins exacts). |
| Tests (données archive, partielles) | `cd backend && ../.venv/bin/python -m pytest -q -rs` | `201 passed in 10.39s`, aucun `SKIPPED` (`C-sorties/pytest-archive-data.txt`). |
| Tests (jeu complet via `ALPHAFORGE_DATA`) | idem | `201 passed in 13.92s` (`pytest-full.txt`). |
| Décompte | 102 fonctions `def test_` ; 201 cas par paramétrage (`grep -c` par fichier). | Confirme PREUVES.md A2. |
| API | `uvicorn api:app --port 8000` (via un lanceur qui enregistre l'usage Bedrock : `scripts/C-launch.py`, sans modifier le code du produit) | OK. `/api/sante` renvoie `llm:true` avec profil `alphaforge`. |
| Interface | `npm install` (0 vulnérabilité signalée) ; `npm run build` | OK (`npm-build.txt`). |
| Variable de données | `ALPHAFORGE_DATA` (donnees.py:20) | Permet de pointer vers le jeu complet ; l'archive n'inclut que 3 CSV utilisés (universe, prix, fx). `corporate_actions.csv`, `macro_rates.csv`, `sources_metadata.csv` non lus par le code (absence observée par grep, confirme NOTE_SELECTION). |

### 1.2 Ce qui exige une adaptation
- Profil AWS : `verifier_bedrock.py:14` fait `setdefault("AWS_PROFILE","datathon")`, `deployer.py:54` et `creer_guardrail.py:66` retombent sur `datathon`, `demarrer.ps1` impose `datathon`. Avec le profil `alphaforge` il suffit d'exporter `AWS_PROFILE` avant ; le serveur API (`llm.py`) utilise la chaîne par défaut de boto3.
- `backend/requirements.txt` ne contient pas `mangum` (requis par `lambda_handler.py:31`) : il est dans `requirements-lambda.txt` seulement. Pas un défaut tant que Lambda n'est pas visé.
- Messages d'erreur et scripts d'aide orientés PowerShell/Windows (`verifier_bedrock.py:25`, `infra/README.md`).

### 1.3 Portabilité macOS/Linux
- Python : chemins par `pathlib` (donnees.py:19) ; recherche de `C:\` ou `\\` dans `backend/alphaforge`, `backend/*.py`, `infra/*.py` : aucune occurrence. `deployer.py:88,90` gère `shell=windows`.
- Lancement non-Windows = deux commandes (documentées dans LIRE_EN_PREMIER §4) : `uvicorn api:app --port 8000` et `npm run dev`. Exécuté ainsi sur macOS.
- `construire_zip_lambda` (deployer.py:68-70) installe des roues `manylinux2014_x86_64` avec `--platform`, donc cross-plateforme en principe ; **non exécuté**.

### 1.4 Fichiers sensibles
`infra/enregistrer_identifiants.ps1` (1 169 octets) : présent, **non ouvert** (consigne). Son rôle annoncé : enregistrement d'identifiants AWS dans le profil `datathon`. Aucun `.env` dans l'archive (recherche par nom).

---

## 2. Cas communs (rejoués)

Format d'entrée du produit : `POST /api/analyse` `{profil:{...}, demande:{texte,ticker,montant_cad}}`. Le profil comporte des champs numériques (`tolerance` 0-100 posée directement, ou `reponses_tolerance` du questionnaire à 3 questions), `horizon_ans`, `retrait_prevu_ans`, `epargne_totale_cad`, etc. Les trois personas ont des champs **ajoutés par l'équipe** (somme à préserver 300 000 pour Robert, portefeuille actuel, fonds d'urgence) absents du brief ; j'ai donc rejoué chaque cas en deux projections : **a** = persona tel que livré, **b** = projection stricte du brief (uniquement les données du brief + `tolerance`). Fichiers `off-<cas>.json` (hors ligne, `ALPHAFORGE_LLM=off`) et `bedrock-*.json`.

Durées : hors ligne 0,02 à 0,09 s par analyse (mesure client HTTP). Avec Bedrock : voir §2.11.

| Cas | Projection exacte | Question à laquelle le produit répond réellement | Verdict / règles non « ok » | Chiffres clés (CAD, convention §3) |
|---|---|---|---|---|
| **C1a** Robert/TSLA (persona) | âge 59, horizon 4, retrait 4, épargne 400 000, tolérance 30, revenu stable, fonds d'urgence, somme à préserver 300 000, portefeuille XIU/XBB/RY ; demande 80 000 TSLA | « Une part de 20 % de l'épargne dans un actif à volatilité 58,8 % est-elle cohérente avec un score retenu de 30 et un retrait à 4 ans ? » | **incohérent** (6/7 règles ok). Seule règle rouge : `concentration` (20 % > seuil 9,5 % et retrait ≤ 5 ans). `capacite` OK : impact 14,2 % < 15,5 %. | Pire chute −70,9 % (2022-01-03 → 2023-01-03, retour 2024-12-05, 1,9 an) ; vol 58,8 %/an ; perte scénario 56 720 $ ; version ajustée **38 000 $** (= 9,5 %, pile au seuil) → cohérent. Option « placement large » XIU.TO même montant : cohérent. |
| **C1b** Robert (projection stricte) | sans préserver/portefeuille/fonds d'urgence | idem | **incohérent** (3/4). `diversification` non évaluée. | mêmes chiffres de marché ; capacité 40 (au lieu de 60). |
| **C2a** Amira/BTC (persona) | 26 ans, horizon 15, tolérance 80, épargne 40 000, portefeuille QQQ/NVDA ; 10 000 BTC-USD | « Pour un risque élevé, 25 % de l'épargne en BTC dépasse-t-il le seuil de concentration (17 %) ? » | **ajustement** : `concentration` orange. Le « risque élevé » n'autorise pas tout (réponse au test du brief). | Pire chute −74,2 % ; vol 50,3 %/an (√365) ; seuil 17,0 % ; ajustée **6 800 $** → cohérent. |
| **C2b** | projection stricte | idem | **ajustement** (seuil 16,2 % car capacité 75 < tolérance 80 ; ajustée 6 400 $) | — |
| **C3a** Mateo/ENB.TO (persona) | 41 ans, horizon 10, tolérance 50, exclusions `["Energy"]`, 15 000 sur 120 000 | « Le secteur d'ENB.TO (étiquette `Energy`) est-il dans les exclusions ? » | **incohérent** : `exclusion` rouge. Option « alternative compatible » : **ESGV** (même montant) → cohérent. | ENB.TO : vol 16,1 %, pire chute −21,4 %. |
| **C3b/c** (projection stricte) | 150 000, exclusions vides / `["Energy"]` | idem | sans exclusion : **cohérent** (diversification non évaluée) ; avec : **incohérent** | La dimension « ESG/controverses » se réduit à une étiquette sectorielle statique (`assets_universe.csv`). Absence observée de toute donnée de controverse. Les exclusions « ESG » ou « Fossil » ne déclenchent rien (essai : `['ESG']` → ok). |
| **C4a** manque épargne | C1b sans épargne | « Peut-on conclure ? » | **indétermine** (règle `donnees` grise : « Il manque : épargne totale »). Une question posée (épargne). | Pas de grille de bascule. |
| **C4b** manque tout | sans épargne ni horizon | idem | **indétermine**, 2 questions. | — |
| **C4c** (retrait seul manquant) | C1a avec `retrait_prevu_ans: null` | Le retrait n'est pas un champ « essentiel » (`profileur.py:21-23`) : aucune question, règle ignorée. | **ajustement** (orange) au lieu d'**incohérent** (`limites-gardien.txt` : « sans retrait → ajustement »). | **Le verdict s'adoucit silencieusement quand la date de retrait manque.** Dans l'UI, le curseur « Retrait prévu » est sur « Aucun » par défaut (Etape2Verifier.jsx:156-163). |
| **C5** contradiction | tolérance 15, horizon 2, retrait 2, épargne 100 000, 100 000 BTC ; texte « doubler… sans risque » | « Quelle perte la pire chute infligerait-elle vs capacité 8,5 % ? » + détection lexicale d'une tension | **incohérent** : `capacite` rouge (74,2 % de perte) + `concentration` rouge. Tension affichée : « gain rapide et absence de risque ». | Ajustée **6 500 $** → cohérent. Règle `retrait` OK (récupération BTC 1,3 an < retrait 2 ans) — voir §8. |
| **C5t** (texte seul, hors ligne) | « J'ai 100 000 $ d'épargne, besoin dans 2 ans, tout mettre en Bitcoin… » | L'extracteur hors ligne ne lit que ticker/montant/épargne (`profileur.py:146-152`) ; « tout » n'est pas un montant | **indétermine** (2 questions : horizon, montant). | — |
| **C6a** 120 000 sur 100 000 | tolérance 50, horizon 10 | Aucune règle « montant > capital » (absence observée dans `gardien.py`). Le cas est traité comme un poids de 120 %. | **incohérent** : `capacite` rouge (« épargne baisserait de 85,1 % »), `concentration` orange (« représente 120 % de ton épargne »). | Option ajustée 12 500 $. La demande impossible n'est pas déclarée impossible. |
| **C6b/c** « GameStop » | texte seul → pas de ticker ; ticker `GME` | Hors ligne : question générique « Quel placement as-tu en tête ? » ; avec ticker inconnu : **HTTP 422** `Actif inconnu : GME` (`donnees.py:46`). | C6b **indétermine** ; C6c **422** | Le produit ne dit pas explicitement « actif hors de l'univers de 31 actifs » à l'utilisateur ; l'UI retombe sur « L'analyse n'a pas pu aboutir. Vérifie tes réponses » (App.jsx:69). |
| **C7** modification | C7a = C1a ; C7b = retrait et horizon → 10 ; C7c = + montant 20 000 | Le produit **réanalyse tout** (≈ 0,05 s) ; aucun état conservé | C7a incohérent → C7b **ajustement** (concentration rouge → orange car retrait 10 > 5) → C7c **cohérent** (5 % < 9,5 %) | Faits : 16 → 15 → 15 (le fait « retrait jugé proche » disparaît). Les identifiants `F-n` sont renumérotés à chaque analyse (`dossier.py:84`) : « Perte supportable » est F-n différent selon le cas. Aucun versionnage, aucune comparaison avant/après côté API ; la vue « Comparer » ne compare que les 3 personas (Comparer.jsx). |

### 2.1 C7 — recalcul, réutilisation, versionnage (réponse précise)
- Recalculé : tout (mesures de marché, faits, règles, options, grille 8 × 20 = 160 cases). Réutilisé : seulement les `lru_cache` de chargement CSV et de série CAD (donnees.py:26-55) ; l'extraction Nova par texte est aussi cachée (`profileur.py:58`).
- Versionné/comparé : **rien** (absence observée : aucun identifiant d'analyse, aucun endpoint de lecture ; `GET /api/analyse/1`, `/api/dossiers`, `/api/analyses` → 404). Le retour « Modifier » (App.jsx, `onModifier → setEtape(1)`) conserve l'état React local du profil et relance l'analyse ; le dossier précédent est écrasé (`setDossier(null)` au début de `lancer`, App.jsx:57).
- Le curseur de bascule de l'étape 5 compare à l'intérieur d'**une** analyse (grille précalculée), pas entre deux profils.

### 2.2 C8 — révision d'une hypothèse
- Les seuils sont des constantes Python (`gardien.py:14-18`, `profil.py:80-95`). Aucun point d'entrée API ni UI pour les réviser (absence observée : grep « seuil » dans `frontend/src` ne trouve que des textes d'affichage). Révision = modifier le code puis relancer.
- Effet observé (`C8-seuil.txt`, patch d'exécution `SEUIL_TRES_VOLATIL=60`) : Robert passe de **incohérent** à **ajustement**, la règle de concentration bascule en « un seul titre, moins volatil » (seuil ×2), mais le **fait HYPOTHESE affiché reste 30** car `analyste.py:18` copie la valeur à l'import. Dans un patch source unique (modifier la ligne 15 de `gardien.py`), les deux modules lisent la même valeur ; ce n'est donc pas un défaut du produit tel que livré, mais un couplage fragile hors modification source.
- Textes de méthode avec coefficients **écrits en dur** dans des chaînes (`analyste.py:46,51,58` : « 5 + 0,35 × score », « 5 + 0,15 ») et `0,8`/`0,6` dupliqués (`gardien.py:191`, `sceptique.py:79,83`). Changer un coefficient dans `profil.py` ne met pas à jour la prose affichée.
- Traçabilité : les seuils sont exposés comme faits `HYPOTHESE` avec méthode et références (très bon), mais sans historique de leurs valeurs.

### 2.3 C9 — de un chiffre à sa source (cas : « −70,9 % », F-2)
1. Verdict (étape 4) → phrase avec icône « i » → ouvre `TiroirFait` (TiroirFait.jsx:10-33) : valeur, unité, étiquette FAIT/HYPOTHESE/SCENARIO, « Source des données » (`Yahoo Finance via yfinance, jeu de départ…`), **Méthode** (texte avec dates sommet 2022-01-03 / creux 2023-01-03, conversion CAD, fenêtre).
2. « Sur quoi repose ce chiffre » → références du registre (`/api/sources`, 30 références) avec auteurs, lien, **niveau d'examen** déclaré, apport.
3. Graphique de chute (`GET /api/serie/TSLA` : pire chute + série hebdo base 100).
Nombre d'étapes : 3 à 4 clics. **Rupture** : aucun lien vers les lignes de CSV ni vers la fonction (`calculs.py`) ; la formule est une chaîne dans `sources.py`/`docs/sources.md`. Pas d'identifiant de version de données (hash du fichier). Absence observée.

### 2.4 C10 — reprise après interruption
- Persistance : aucune (absence observée). Seule trace durable potentielle : S3 `dossiers/…json` si `ALPHAFORGE_DATA_BUCKET` est défini (stockage.py:14-28), jamais exécuté.
- Essai : flux `/api/analyse/flux` lu une seule ligne puis connexion fermée ; le thread serveur continue en arrière-plan (`api.py:107`, thread daemon + `queue.Queue` sans limite) ; aucun identifiant pour retrouver le résultat. Redémarrage du serveur : tout l'état (caches, analyses en cours) est perdu ; le client doit **relancer l'analyse complète** (App.jsx:63-70 renvoie à l'étape 2 avec les réponses conservées côté navigateur uniquement).
- Aucune reprise partielle (pas de checkpoint par agent), ce qui est cohérent avec un pipeline de 0,05 s hors ligne et ~8-14 s avec Bedrock.

### 2.5 Entrées invalides (essai de robustesse, `/api/analyse`)
`horizon_ans:"4"` → **HTTP 500** ; `montant_cad:"80000"` → **HTTP 500** ; `epargne` en chaîne → indéterminé ; `exclusions:"Energy"` (chaîne) → itérée caractère par caractère → verdict incohérent (secteur contenant « e »…) ; ticker en minuscules → 422. Le modèle Pydantic est `dict` libre (`api.py:28-30`). Défaut mineur (UI typée), mais l'API publique de la Lambda serait exposée à ces 500.

### 2.6 Exécutions Bedrock réelles (budget : 3 de bout en bout)

Profil `alphaforge`, compte `4711…26`, région us-east-1. Pré-vol : `verifier_bedrock.py` (2 appels de 60 jetons max, hors budget, OK pour les 2 modèles). Instrumentation = un crochet botocore dans un lanceur externe (`scripts/C-launch.py`), code du produit intact. Fichier : `bedrock-calls.jsonl` (la 1re exécution n'est pas dans ce fichier : mon crochet avait un défaut ; **jetons de C1 non mesurés**, appels : 1 Nova + 2 Sonnet).

| # | Cas | Appels | Jetons (entrée/sortie) | Latence appels | Durée mur |
|---|---|---|---|---|---|
| R1 | C1a via UI : `/api/comprendre` puis `/api/analyse/flux` | Nova (comprendre) + Sonnet Sceptique + Sonnet Rédacteur | non mesurés | — | comprendre 1,13 s ; flux 7,84 s (Sceptique prêt à 3,41 s, Rédacteur 7,84 s) |
| R2 | C5 texte libre, `/api/comprendre` seul | Nova ×1 | 761 / 128 | 1 490 ms | 1,95 s |
| R3 | C5 complété (montant 100 000 et tolérance 15 saisis comme à l'étape 2) | Sonnet Sceptique ×1 ; Sonnet Rédacteur ×2 (essai 1 refusé, essai 2 accepté) | 957/237 ; 2 990/474 ; 3 056/455 | 3,38 s ; 5,01 s ; 5,22 s | 13,78 s |

Total mesuré R2+R3 : 9 058 jetons (≈ 7 900 entrée, ≈ 1 300 sortie). Aucune erreur de modèle ou de droits. Temps de réponse cohérents avec « 9,2 à 15,4 s » déclarés (R1 plus rapide, R3 plus lent à cause de la reprise).

Constats R1 : texte Rédacteur Bedrock ≈ gabarit hors ligne (différence = espaces insécables ; une phrase « pourquoi » ajoutée). **Verdict, règles, options, grille de bascule : égaux objet à objet** avec la version hors ligne (`C1`). Les objections diffèrent (Sceptique LLM : diversification, marché, fenêtre ; hors ligne : devise, fenêtre) donc les faits et les « limites » diffèrent.
Constats R3 : le contrôle d'ancrage a refusé l'essai 1 (« mot(s) de conseil interdit(s) : sans risque / aucun risque ») puis accepté l'essai 2 : **boucle fermée observée en exécution réelle**. Verdict égal à la version hors ligne avec les mêmes entrées (`off-C5b.json` : verdict, règles, options, bascule identiques ; objections différentes). Le texte accepté comporte « horizon de 2.0 an(s) » (point décimal anglais, nombre du dossier) et une phrase « miroir » paraphrasant (non citée) : « Tu dis être prudent et vouloir doubler ton argent… ».

---

## 3. Mesures de base et conventions de calcul

Valeurs produites par les fonctions du produit (arrondies à 0,1 par le code), fenêtre 2021-11-12 → 2026-11-12, **toujours en CAD**. Détail complet : `C-mesures.json`.

| Actif | Rend. annualisé % | Vol. annualisée % | Pire baisse % | Facteur | Devise source |
|---|---|---|---|---|---|
| TSLA | 5,5 | 58,8 | −70,9 | √252 | USD → CAD |
| BTC-USD | 4,8 | 50,3 | −74,2 | √365 | USD → CAD |
| ENB.TO | 12,8 | 16,1 | −21,4 | √252 | CAD natif |
| SPY | 14,5 | 16,6 | −22,2 | √252 | USD → CAD |
| Corrélation TSLA–SPY | 0,51 (hebdomadaire, vendredi) | | | | |

Fonctions : `calculs.py:45` (rendement : TCAC premier→dernier sur jours/365,25), `:39` (vol : écart-type ddof=1 des rendements log quotidiens × √`jours_par_an`), `:16` (drawdown cummax), `:64` (corrélation de Pearson sur rendements simples du vendredi), `donnees.py:51` (365 pour `crypto`, sinon 252), `donnees.py:55-66` (série CAD).

**Contrôle indépendant TSLA (pandas seul, sans importer le produit)** : CAD : rendement 5,533 %, vol 58,793 %, drawdown −70,881 %, corrélation hebdo 0,5127 ; USD sans conversion : 2,903 % / 59,446 % / −72,97 %. Écart avec le produit ≤ 0,05 point (arrondi). **Conventions concordantes.**

Conventions à retenir pour une fusion :
- **Devise** : les prix USD (TSLA, BTC, SPY…) sont multipliés par USD/CAD du jour (jour absent → dernier taux, puis `bfill` en tête) **avant** tout calcul ; la volatilité et le rendement incluent donc l'effet de change (TSLA : +2,6 points de rendement, drawdown −73,0 % → −70,9 %). Le Sceptique recalcule la chute en USD comme vérification explicite (`sceptique.py:33-41`). Le taux Banque du Canada est une moyenne indicative de journée appliquée à des clôtures (limite écrite dans `redacteur.py:72`).
- **Rendements** : logarithmiques pour la volatilité ; TCAC géométrique pour le rendement ; pas de rendement arithmétique moyen. Pas d'annualisation par √(jours observés) : constante 252/365.
- **Prix ajusté** : `adj_close` (dividendes et fractionnements) ; `close` jamais utilisé.
- **Pire chute** : une seule fenêtre de 5 ans ; « récupération » = premier retour au sommet précédent (une seule observation par actif).
- **Pire 12 mois** : 52 semaines glissantes sur vendredis (approximation déclarée ; TSLA −64,8 %).
- **Calendriers** : non alignés sauf corrélations (hebdo vendredi). BTC : 1 827 cotations (7 j/7), actions : 1 255.
- Contrôle de qualité (7 contrôles : présence, doublons, prix positifs, couverture, trous, sauts > 40 %, devise) ; seul un `echec` rend le verdict gris.

---

## 4. Inventaire des contributions

États constatés : I = Implémenté ; E = Exécuté ; V = Vérifié (critère explicite).

| ID | Nom | Définition / contrat | Provenance | État constaté | Valeur pour le défi | Preuves | Hypothèses | Dépendances | Transfert (effort) | Incertitudes |
|---|---|---|---|---|---|---|---|---|---|---|
| C-01 | Contrat `Dossier` | dataclasses `Fait{id,libelle,valeur,unite,type,source,methode,references}`, `Regle`, `Objection`, `EtapeTrace`, `Dossier.to_dict()` ; types FAIT/HYPOTHESE/SCENARIO | `dossier.py` (99 l.) | **E** (toutes les réponses) | Fort : traçabilité native, chaque chiffre porte source+méthode | JSON de tous les cas | `F-n` séquentiel par analyse | `sources.py` (références) | Bloc avec sources.py et `TYPE_REGLE` ; faible effort si le socle accepte ce format | IDs non stables entre analyses |
| C-02 | Moteur de règles Gardien | 8 règles + porte `donnees` ; pire niveau retenu ; 4 états | `gardien.py:61-206` | **V** (201 tests, 93 grilles) | Fort : décision explicite, non LLM | `grille-monotonie.txt`, tests banc | Seuils d'équipe non validés empiriquement | `profil.py`, `sources.py`, mesures | Extractible avec profil.py (moyen) | Un seul levier de différenciation |
| C-03 | Profil à deux jauges | tolérance (3 questions Grable-Lytton adaptées ou nombre) + capacité (barème +/− points) → min ; perte max 5+0,35·s ; seuil 5+0,15·s | `profil.py` | E/V | Bon : sépare vouloir et pouvoir (RCC/OCRI) | `limites-gardien.txt` | Barèmes d'équipe ; sauts discrets de capacité (horizon 2,9→3 : 45→60 ; 4,9→5 : 60→80) | aucune | Extractible seul (faible) | Barème non validé |
| C-04 | Calcul de marché CAD | pire chute, vol, TCAC, pire 52 sem., corrélation hebdo ; série CAD | `calculs.py`, `donnees.py:55-66` | **V** (recalcul pandas TSLA ≤0,05 pt) | Fort : conventions claires | `C-mesures.json` | √252/√365 fixes ; FX du jour | CSV `adj_close`+`usdcad` | Extractible seul (faible) ; `calculs.py` importe `donnees` | Une seule fenêtre ; pas de corporate actions |
| C-05 | Contrôle qualité données | 7 contrôles ok/alerte/echec | `donnees.py:69-113` | E | Moyen : façade de qualité | `qualite_donnees` dans chaque dossier | Seuils 40 %, 4/6 jours | CSV | Extractible (faible) | Contrôles basiques (pas de cohérence inter-séries) |
| C-06 | Analyste (faits + hypothèses comme faits) | produit 12-16 faits par analyse ; les seuils d'équipe deviennent des `Fait` HYPOTHESE | `agents/analyste.py` | E/V | Fort pour l'explicabilité | JSON des cas | Prose avec coefficients en dur | C-01, C-04 | Avec C-01 | Duplication de constantes |
| C-07 | Sceptique à catalogue fermé | modèle choisit ≤3 codes parmi 6 (devise, récupération, fenêtre, marché, rapidité, diversification) ; le code exécute et classe `confirmee/ecartee/limite` | `agents/sceptique.py` | E | Moyen : critique outillée mais bornée | R1, R3 | Textes d'objection filtrés par thèmes/mots | C-01, llm.py | Extractible (moyen) | Distribution des choix non testée ; `issue` pas toujours une vraie contradiction (`_recuperation` toujours « confirmee ») |
| C-08 | Rédacteur + contrôle d'ancrage | nombres ⊂ dossier, F-n valides, citations textuelles, pas de mots de conseil, pas de contradiction du verdict ; 2 essais puis gabarit | `agents/redacteur.py:254-371`, `garde_fous.py` | **E** (refus réel observé en R3) | Fort : patron réutilisable | R3 (essai 1 refusé) ; tests ancrage/robustesse | Contrôle lexical FR ; normalisation de nombres | C-01, llm.py | Patron extractible (moyen) | Faux négatifs lexicaux possibles |
| C-09 | Correction d'étiquettes | FAIT↔HYPOTHESE↔SCENARIO imposées par motifs | `redacteur.py:216-238` | E (R1 : FAIT→HYPOTHESE) | Moyen | R1 | Motifs FR | C-08 | Avec C-08 | — |
| C-10 | Profileur (extraction de texte libre) | Nova extrait ticker/montants/horizon/exclusions ; le code valide (liste fermée, bornes, ≤60 ans) ; ne remplit que les champs vides | `agents/profileur.py` | E (R2) | Bon pour la qualification | R2 : ticker, horizon 2, épargne ; « tout » non converti en montant | Repli mots-clés limité (ticker/montant/épargne) | llm.py | Extractible (moyen) | Hors ligne perd horizon/retrait |
| C-11 | Grille de bascule + plus petit ajustement | grille 8 montants × horizons 1..max(20,h+5) recalculée par le Gardien ; dichotomie au pas de 100 $ | `gardien.py:209-267` | **V** (0 violation sur 14 880 cases ; 93 grilles) | Fort : « ce qui changerait l'avis » | `grille-monotonie.txt` | Retrait fixe pendant la variation d'horizon | C-02 | Avec C-02 (faible) | Axe horizon quasi inerte si retrait défini (§8) |
| C-12 | Registre de sources | 30 références, 32 justifications, 6 agents ; champ `examen` honnête | `sources.py` (31 kB), `/api/sources`, `docs/sources.md` | E | Fort pour « sources, hypothèses, limites » | `/api/sources` : {references:30, justifications:32, agents:6} | Références non relues déclarées comme telles | — | Extractible (faible) ; données à revalider | DOI non vérifiés par moi |
| C-13 | Orchestrateur à ordre fixe + options | séquence ; arrêt anticipé si ticker/montant absent ; options « version ajustée », « alternative compatible » (liste fixe ESGV, XIU.TO, XBB.TO, FTS.TO), « placement large » | `orchestrateur.py` | E/V | Moyen | tous les cas | Liste d'alternatives codée en dur | agents | Remplaçable (moyen) | « Placement large » toujours proposé |
| C-14 | Flux NDJSON | thread + file ; une ligne par étape puis dossier ; client `fetch`+`ReadableStream` | `api.py:90-114`, `api.js:31-57` | **E** (R1 : étapes à 0,01/0,05/0,06/3,41/3,43/7,84 s) | Bon : trace réellement progressive | R1 | Sur Lambda tout arrive d'un bloc (déclaré) | — | Extractible (faible) | Non testé sur Lambda |
| C-15 | Wrapper Bedrock + repli | Converse ; délais 5 s/40 s ; 2 tentatives ; mode `auto/off` | `llm.py` | E | Moyen | R1-R3, `repli-hors-ligne.txt` | Hors ligne « collant » après 1re erreur d'accès (llm.py:109-110) | boto3 | Extractible (faible) | Pas de journal d'usage ni de coût |
| C-16 | Interface 5 étapes + Comparer | React 18 + Vite 6, français ; stepper ; questionnaire ; trace ; verdict ; curseurs | `frontend/src` | I (build OK), non exécuté en navigateur | Bon (UX orientée explication) | `npm-build.txt` | — | contrat JSON | Lié au contrat (moyen) | Aucun test frontend |
| C-17 | Tiroir de preuve | clic « i » → faits, source, méthode, références | `TiroirFait.jsx`, `Sources.jsx` | I | Fort pour C9 | lecture de code | — | C-01, C-12 | Extractible (faible) | Pas de lien vers lignes de CSV |
| C-18 | Fiche pour conseiller | Markdown généré : situation, verdict, options, questions, sources | `Etape5Bascule.jsx:14-60` | I | Bon pour la valeur business | lecture de code | — | C-01 | Extractible (faible) | Non exécuté |
| C-19 | Banc de tests | 201 cas : monotonie, stabilité, 12 cas, ancrage, robustesse, flux, sources | `backend/tests` | **E** | Bon | `pytest-full.txt` | Tests hors ligne uniquement | — | Réutilisable comme oracle | Aucun test live Bedrock ni frontend |
| C-20 | Scripts de déploiement | S3 + IAM + Lambda (Function URL publique) + Amplify/S3 web | `infra/deployer.py` | **I seulement** | Potentiel AWS | lecture ; tests moto annoncés | Jamais exécuté | boto3 | Réécriture probable | Voir §5/§8 |
| C-21 | Guardrail Bedrock | script de création + câblage `guardrailConfig` dans `llm.py` | `infra/creer_guardrail.py`, `llm.py:93-114` | I (mock) | Défense en profondeur potentielle | `test_llm.py` (faux client) | — | compte AWS | Faible | Jamais créé |
| C-22 | Archivage S3 + Lambda handler | `put_object` JSON best-effort ; Mangum | `stockage.py`, `lambda_handler.py` | I | Persistance potentielle | lecture | Silencieux en cas d'erreur | S3 | Faible | Jamais exécuté |
| C-23 | Personas fictifs | 3 profils + demandes + citations | `personas.py` | E | Utile pour démos | cas C1-C3 | Montants inventés par l'équipe | — | Trivial | — |

---

## 5. Comportement agentique réel

Orchestrateur : fonction Python séquentielle `orchestrateur.analyser` (orchestrateur.py:63-120) ; **aucun agent ne choisit l'ordre ni n'appelle un autre agent** ; aucune boucle entre agents ; aucun outil exposé au modèle (le « tool use » de Bedrock n'est pas utilisé : `llm.appeler` n'envoie ni `toolConfig` ni outils). Absence observée : recherche de `toolConfig`/`tools` dans `llm.py`/`agents`.

| Rôle | Mission | Modèle | Instruction système réellement chargée | Contexte transmis | Appel / condition | Sortie | Validations par le code | Hors ligne |
|---|---|---|---|---|---|---|---|---|
| Profileur | Extraire champs d'une phrase | `global.amazon.nova-2-lite-v1:0` (llm.py:20), `temperature 0.2`, max 600 | `profileur.py:27-40` (1 178 car. mesurés) : « Tu lis la phrase… UNIQUEMENT ce qui y est écrit. Tu ne devines rien… ticker choisi STRICTEMENT dans la liste » | catalogue 31 tickers, secteurs, phrase | Seulement si `demande.texte` non vide et `texte_lu` faux (via `/api/comprendre`) ; **sauté** dans `/api/analyse/flux` envoyé par l'UI (`texte_lu:true`, App.jsx:63) | JSON {ticker, montants, horizon…} | ticker ∈ univers ; nombres 0-1e9 ; horizon ≤ 60 ; exclusions ∈ secteurs ; ne remplace jamais un champ déjà rempli (profileur.py:188-198) ; cache par texte | mots-clés : ticker, montant, épargne seulement |
| Contrôle données + Analyste | Produire les faits | aucun (code) | — | profil, demande | toujours | 12-16 `Fait` | — | identique |
| Sceptique | Choisir 1-3 vérifications | `global.anthropic.claude-sonnet-5` (pas de température), max 700 | `sceptique.py:113-119` (630 car.) : « Tu ne peux demander QUE des vérifications de la liste… Choisis les 1 à 3… sans aucun chiffre que tu inventerais » | profil (nom, horizon, exclusions, portefeuille), phrase, **tous les faits**, liste des vérifications possibles | si LLM actif ; sinon repli | `{"objections":[{code,texte}]}` | `code ∈ possibles`, unique, ≤3 ; `texte` : aucun nombre hors {1,2,3,5,12}, pas de mot de conseil ni rapport en lettres, doit contenir un mot du thème (sceptique.py:143-159) ; sinon texte du catalogue | exécute `devise`, `recuperation_inconnue`, `fenetre_courte` seulement (sceptique.py:176) |
| Gardien | Décider | aucun (code) | — | profil, mesures | toujours | règles, verdict, grille, options | — | identique |
| Rédacteur | Reformuler et expliquer | Claude Sonnet 5, max 1800, source d'ancrage Guardrail si configuré | `redacteur.py:32-49` (1 359 car.) : « Le verdict est déjà décidé… N'écris AUCUN nombre qui n'apparaît pas déjà dans le dossier… Ne dis jamais d'acheter, de vendre » | dossier JSON complet (profil, règles, faits, options, tensions) + phrases de référence | si LLM actif | JSON {reformulation, miroir, pourquoi} | `verifier()` (redacteur.py:254-311) : nombres, F-n, citations mot pour mot, notation, rapport en lettres, contradiction du verdict, mots de conseil ; 2 essais avec défauts renvoyés dans la consigne ; **sinon gabarit** | gabarit `_modele_de_phrases` |

Ce que le modèle décide réellement : (1) comment lire une phrase libre (Profileur) — seul rôle à effet réel sur les **entrées** du verdict, borné par validation ; (2) lesquelles des ≤5-6 vérifications apparaîtront et la formulation de l'objection — modifie le contenu des faits (F-16 « chute en USD » absent de R1) et des « limites » affichées, **pas le verdict** ; (3) la formulation du texte final (surtout une paraphrase du gabarit : R1 = mêmes phrases à l'espace insécable près + 1 phrase « pourquoi » supplémentaire).
Ce que le code décide : tous les chiffres, règles, niveaux, verdict, options, grille, étiquettes, « ce qui changerait l'avis » (volontairement non confié au modèle, redacteur.py:25-27).

**L'agentique apporte-t-elle quelque chose qu'un enchaînement fixe n'apporterait pas ?** Oui, modestement : lecture du texte libre (Nova) et personnalisation du libellé/choix des vérifications ; le contrôle d'ancrage fait boucle réelle (R3). Non pour le raisonnement : pas de planification, d'outil ni de dialogue entre agents. Le produit assume cet état (« ordre fixe, code »), conforme à l'encouragement du défi à une approche simple et vérifiable. Une faiblesse : un modèle **n'ajoute rien de vérifié** à C1 (le texte hors ligne suffit).

Aspects de configuration LLM à connaître (`llm.py`) :
- `extraire_json` prend du premier `{` au dernier `}` (llm.py:119-123) ; tolère le bruit mais pas deux objets.
- Mode `auto` : à la **première** erreur d'accès (`ExpiredTokenException`, `AccessDeniedException`, `NoCredentialsError`…), `_etat["indisponible"]` est fixé **pour tout le processus** (llm.py:25,109-110) ; aucun re-test. Un refus d'accès sur **un seul** modèle (ex. Nova non activé) bascule aussi le Sonnet en hors ligne. Un redémarrage du serveur est requis après renouvellement des identifiants. Comportement hors ligne vérifié (`repli-hors-ligne.txt`, profil inexistant) : `acces_verifie()` → False, `raison: Bedrock indisponible (ProfileNotFound)`, dossier identique au mode `off` pour verdict/règles/options/grille/faits/objections ; seul le journal `texte.controle` change.
- Pas de journal des jetons ni du coût (mon crochet externe a dû être ajouté). L'archive déclare « jetons non mesurés » : exact.
- Les modèles et la région sont surchargeables par `ALPHAFORGE_MODELE`, `ALPHAFORGE_MODELE_LEGER`, `AWS_REGION` ; les identifiants globaux « global.* » sont ceux de l'atelier.

---

## 6. Appréciation par critère (0–4)

| Critère | Constats / forces / défauts | Cote | Justification |
|---|---|---|---|
| Adéquation au problème | Répond à « second avis » : qualification, recherche critique (limitée), analyse, restitution ; personas C1-C3 donnent des verdicts sensés (Robert incohérent, Amira ajustement, Mateo incohérent par exclusion) ; pas de transaction, pas de prédiction ; défaut : « demande impossible » (C6a) et actif hors univers mal signalés. | 3 | Couvre les 4 fonctions sur les cas, avec trous aux limites. |
| Qualité méthodologique | Règles explicites, hypothèses étiquetées et publiées, deux jauges (tolérance/capacité) ; défaut : impact = poids × pire chute de l'actif (suppose le reste du portefeuille inchangé) ; récupération sur une seule observation ; barèmes non validés. | 3 | Transparente et justifiée par des sources, mais non étalonnée. |
| Justesse des données et calculs | Recalcul pandas TSLA concordant ; FX traité ; `adj_close` ; 7 contrôles qualité ; limites écrites ; défaut : univers de 31 actifs, pas de corporate actions utilisées. | 3 | Vérifié sur le cas de référence (TSLA) et les 4 actifs par les fonctions du produit. |
| Adaptation au profil | Différences nettes entre trois profils ; levier unique (score retenu) ; ESG réduit à une étiquette de secteur ; manque de retrait → verdict adouci sans question (C4c) ; axe horizon de la grille inerte quand retrait fixé. | 3 | Fonctionne sur les cas ; fragile sur les omissions. |
| Profondeur et fidélité de l'explication | Fait→source→méthode→références ; étiquettes FAIT/HYPOTHESE/SCENARIO ; contrôle d'ancrage réel avec boucle (R3) ; objections exécutées par code ; défaut : pas de lien vers les lignes de données. | 4 | La meilleure partie : testé par 201 tests dont ancrage/robustesse et observé en exécution réelle. Je plafonne à 4 pour la robustesse du mécanisme, tout en notant que la preuve se limite aux cas rejoués. |
| Utilité réelle des agents | Fixe + 3 appels LLM aux effets limités ; verdict indépendant ; texte ≈ gabarit. | 2 | Implémenté et exécuté, valeur marginale hors extraction de texte libre. |
| Qualité de l'expérience | 5 étapes en français, tiroir de preuve, curseurs, fiche conseiller, comparaison de 3 profils ; build OK ; non exécuté en navigateur (cote prudente) ; aucun test UI ; a11y calculée seulement sur contrastes (VALIDATIONS §5). | 2 | Implémenté et compilé, expérience non éprouvée par moi. |
| Cohérence architecturale | Contrat `Dossier` unique ; couche calcul pure ; LLM dans 3 modules ; défauts : constantes dupliquées en prose, 4 états verdict codés en dur côté UI. | 3 | Propre et lisible, couplages mineurs. |
| Facilité et risque d'intégration | `calculs.py`, `garde_fous.py`, `format.py`, `sources.py` isolables ; `Dossier` comme format d'échange ; API sans état ; verdicts en chaînes françaises ; moteur « pire niveau » à confronter à d'autres logiques. | 3 | Intégration réaliste par blocs, avec adaptateurs de contrat. |
| Fonctionnement AWS | Seul Bedrock Converse réellement exécuté ; usage AWS mince (2 modèles, pas d'AgentCore, Lambda/S3/Amplify/Guardrail non exécutés) ; script de déploiement exposant une API publique sans authentification. | 2 | Bedrock vérifié ; le reste conçu/implémenté seulement. |
| Reproductibilité et exploitation | Versions figées, 201 tests verts sur machine neuve, build OK ; défauts : aucun journal d'usage/coût, aucune persistance, lanceur PowerShell, mode hors ligne collant, pas d'authentification/limitation de débit. | 3 | Reproductible ; exploitation de production non préparée. |

---

## 7. Déclarations confrontées

| # | Déclaration (source) | Verdict | Preuve |
|---|---|---|---|
| 1 | « 201 passed » (LIRE_EN_PREMIER §4) | **Confirmée** | 201 passed en 10,4 s et 13,9 s, 0 ignoré. |
| 2 | « Aucun LLM ne produit ni n'influence un chiffre ou le verdict » (§2) | **Nuancée** | Aucun chiffre de marché ou de règle ne vient du modèle (calculs en code ; R1 et R3 : règles/options/grille égaux hors ligne). Mais le Profileur LLM remplit des **entrées** (épargne, horizon, ticker : R2) et le Sceptique choisit quels faits sont ajoutés (F-16 absent). Pas d'influence sur le verdict à entrées égales. |
| 3 | « Verdicts identiques avec ou sans Bedrock » (§2) | **Confirmée à entrées égales ; nuancée sinon** | C1 et C5b égaux objet à objet (verdict, règles, options, bascule). Mais avec un texte libre seul, l'extracteur hors ligne ne lit pas horizon/retrait (C5t : indéterminé). Objections et faits diffèrent. |
| 4 | « Écarts ≤ 0,1 point au recalcul indépendant » (VALIDATIONS §2) | **Confirmée (TSLA)** | Mon recalcul : écart ≤ 0,05 point (§3). |
| 5 | « Grille de bascule monotone » (§6, VALIDATIONS §1) | **Confirmée** | 93 grilles (3 personas × 31 actifs), 14 880 cases : 0 violation en montant ; 0 violation en horizon. Nuance : l'axe horizon bouge peu quand `retrait_prevu_ans` est fixé (grille Robert/TSLA : seule la colonne « 1 an » diffère). |
| 6 | « Seuils déclarés comme hypothèses » (§6) | **Confirmée** | Faits `HYPOTHESE` F-n avec méthode ; texte « barème non validé empiriquement » (sources.md). |
| 7 | « 9,2 à 15,4 s par analyse » (VALIDATIONS §4) | **Confirmée en ordre de grandeur** | R1 7,84 s (+1,1 s comprendre) ; R3 13,78 s (+2,0 s). |
| 8 | « Contrôle d'ancrage qui empêche » (§2) | **Confirmée** | R3 : essai 1 rejeté (« sans risque »), essai 2 accepté. Limite : le catalogue lexical rate « foncer » (`\bfonce[zs]?\b`) : l'objection O-1 de R1 affiche « Avant de foncer, vérifie… ». |
| 9 | « Catalogue fermé de 6 ; le modèle ne calcule jamais » (§2) | **Confirmée** | sceptique.py:92-111 ; le code exécute `executer_verif`. |
| 10 | « Facteurs √252/√365 ; log-rendements » (§3) | **Confirmée** | donnees.py:51 ; calculs.py:41-42 ; BTC 1 827 cotations. |
| 11 | « USD convertis en CAD » | **Confirmée** | donnees.py:62-64 ; TSLA CAD vs USD : 5,5 % vs 2,9 %. |
| 12 | « Aucun test frontend » | **Confirmée** | aucun test ni script. |
| 13 | « Déploiement AWS, Guardrail, S3 : jamais exécutés » | **Confirmée (par cohérence du code)** ; **invérifiable** quant au passé (je n'ai rien exécuté). Les tests utilisent des faux clients. |
| 14 | « La règle rouge de Robert vient de la concentration (retrait ≤ 5 ans), pas de l'horizon vs récupération » (PRESENTATION §6d) | **Confirmée** | C1a : seule `concentration` rouge ; `horizon` ok. |
| 15 | « Différenciation presque entièrement via un seul levier » | **Confirmée** | `profil.evaluer` : le score retenu fixe perte max et seuils ; vérifié par `limites-gardien.txt`. |
| 16 | « Streaming de la trace pendant l'analyse » | **Confirmée en local** | R1 : lignes à 0,01/0,05/0,06/3,41/3,43/7,84 s. Sur Lambda : non observable. |

---

## 8. Défauts décisifs et surprises

Classés par gravité pour une fusion ou une démonstration.

1. **Absence de persistance et de versionnage** (C7/C10) : aucune identité d'analyse, aucun historique ; modification d'un profil = écrasement ; `F-n` renumérotés. Une démo de « suivre un profil dans le temps » est impossible sans ajout.
2. **Omission de retrait → verdict adouci sans question** (C4c) : `retrait_prevu_ans` n'est pas un champ essentiel ; Robert/TSLA devient « ajustement » au lieu d'« incohérent ». L'UI démarre à « Aucun ». Le cas C4 du brief (sans date de retrait) donne donc un verdict **trop permissif**, alors qu'il devrait demander.
3. **Demande impossible non détectée** (C6a) : pas de règle « montant > épargne » ; le résultat est un verdict incohérent avec « 120 % de ton épargne » mais sans message « impossible ». Actif hors univers (C6c) : 422 brut ou question générique.
4. **Grille de bascule : axe horizon quasi inerte** quand un retrait est défini (la grille ne fait pas varier `retrait_prevu_ans`), donc les « curseurs » d'horizon n'illustrent pas « retarder le retrait » (C7). Incohérence entre ce que le curseur suggère et le levier réel.
5. **Règle `retrait` et `horizon` appuyées sur une seule récupération historique** : BTC (récupération 1,3 an) et TSLA (1,9 an) obtiennent « retrait ok » avec retrait à 2-4 ans, bien que volatilité 50-59 % (`gardien.py:137,149`). La règle `capacite` ou `concentration` rattrape dans les cas testés ; seule, la règle serait trop optimiste.
6. **Mode hors ligne « collant »** (llm.py:109-110) : une erreur d'accès isolée (même sur un seul modèle) coupe Bedrock pour tout le processus jusqu'au redémarrage ; `acces_verifie()` met le résultat STS en cache (llm.py:66-73).
7. **Sécurité/coût des scripts de déploiement** (non exécutés) : Function URL `AuthType NONE` avec `lambda:InvokeFunction` à `Principal:"*"` (deployer.py:184-203), CORS `*` (api.py:25), IAM Bedrock `Resource:"*"` (deployer.py:140-142), bucket web public (deployer.py:246-250), aucune limitation de débit : chaque appel public déclenche des appels Bedrock facturés. Dossiers archivés sur S3 contiennent des données de profil sans politique de rétention.
8. **Données et licences** : le produit n'ajoute pas de données ; `docs/donnees.md` rappelle que l'autorisation du jeu de départ vaut pour l'événement et que les conditions Yahoo (usage personnel) s'appliquent. À prendre en compte avant tout déploiement public.
9. **ESG/controverses** : seule l'étiquette de secteur ; « ESG » ou « Fossil » comme exclusion n'a aucun effet (essai : `['ESG']` → ok).
10. **Entrées non typées** (`api.py:28-30`) : `"4"` pour l'horizon → 500 ; chaîne pour `exclusions` itérée par caractères.
11. **Couplages cachés** : constantes dupliquées dans la prose (`analyste.py:46,51,58`, `gardien.py:191`, `sceptique.py:79,83`) ; `analyste.py` importe les seuils depuis `gardien.py` (couplage agent → moteur) ; états de verdict en français indexés par l'UI.
12. **Conformité lexicale** : `garde_fous.py` repose sur des motifs ; « foncer » passe. Ce n'est pas un contrôle sémantique.
13. **Documentation** : `LIRE_EN_PREMIER` cite 3.14.7/Node 24 ; reproduit ici sur 3.12/Node 22 sans modification ; `infra/README.md` mentionne « AgentCore » comme cible alors que le code utilise Lambda (plan B annoncé).
14. **Surprise positive** : coût en jetons très modeste (~8 100 jetons pour une analyse avec reprise du Rédacteur) et latence de 8 à 14 s ; hors ligne en 0,05 s, d'où une démo de secours fiable.

**Non vérifié par moi** : rendu et ergonomie réels dans un navigateur (interdits) ; comportement de la Function URL/Lambda (non exécutée) ; Guardrail réel ; tokens de la 1re exécution (instrument défaillant) ; exactitude des DOI/références du registre ; accessibilité clavier ; effet de `texte_lu:false` en flux avec Nova (le chemin UI saute le Profileur LLM en flux).
