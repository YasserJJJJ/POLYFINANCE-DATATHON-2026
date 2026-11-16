# Rapport d'évaluation — réalisation A (AlphaForge, `datathon2026`)

Évalué le 2026-11-15 sur `work/A` (copie de l'archive). Toutes les commandes ont été lancées depuis `work/A`. Les sorties brutes sont dans `reports/A-sorties/`. Les chemins `fichier:ligne` valent pour le code joint.

Trois strates, jugées séparément : **(1) produit** `src/datathon2026` ; **(2) recherche hors produit** `research/`, `docs/refonte/*.md` ; **(3) architecture cible à quatre agents, conçue non construite** `docs/refonte/architecture/00-10`.

## 0. Résumé

| Strate | État constaté aujourd'hui | Note |
|---|---|---|
| Produit | Implémenté, Exécuté (démo fixe, 3 exécutions Bedrock réelles, application), Vérifié sur le vérificateur et les calculs (51 tests) | Agent unique + enchaînement fixe ; vérificateur lexical solide ; aucune qualification, recherche, persistance |
| Recherche | Exécutée : 6 scripts relancés (5 sorties texte identiques) aux sorties conservées (diff vide) ; prototype `dossier_maison` : 118 assertions passent | Résultats statistiques transférables comme méthodes ; non intégrés au produit |
| Architecture cible | Conçue (11 documents, ~3 000 lignes) ; rien d'exécutable sauf le prototype du dossier ; catalogue, instructions système, schémas machine : absents | Contrats précis et cohérents ; reste à écrire l'essentiel de l'exécution |

## 1. Vérification de l'état

| Étape | Commande | Résultat |
|---|---|---|
| Données | copie de `data/alphaforge_starter` vers `data/raw/` | OK (9 fichiers) |
| Installation | `uv sync` | OK, 1,2 s (paquets en cache) ; `boto3`, `numpy`, `pandas`, `pytest` |
| Tests | `uv run pytest -q` | **51 réussis, 0 échec, 0 ignoré, 6,8 s** (14 evidence, 8 analytics, 7 data, 6 workflow, 4 app, 4 agent). Le test d'agent utilise un client Bedrock simulé (`tests/test_agent.py:7-24`) |
| Enchaînement fixe | `alphaforge demo tous --sortie reports/A-sorties/demo` | 1,6 s ; robert-tsla : 15 affirmations, 52 valeurs reliées, 0 échec ; amira-croissance : 18, 51, 0. **Comparaison avec `runs/` joints : identiques** à la date et aux durées près (script en ligne, résultat `True` pour les deux) |
| Revérification hors ligne | `alphaforge rendre --sortie <copie de runs>` | 8 dossiers relus et rendus, 0 échec (sans AWS) |
| AWS lecture seule | `alphaforge aws-verifier` | OK : compte …1226, `global.anthropic.claude-sonnet-5-5` ACTIVE ; 33 profils Claude visibles |
| Application | `python -m datathon2026.app --port 8799`, requêtes `curl` sur `/api/dossier` (sorties `A-sorties/app-port8799/`) | OK, 0,1 à 0,14 s en mode référence ; arrêtée à la fin. **Le port 8765 était déjà occupé par un autre processus étranger à cette évaluation (projet d'origine, ~/Downloads) : mes premières requêtes l'ont atteint et ont été écartées (`NE-PAS-UTILISER-app-autre-serveur-port8765`), puis refaites sur 8799** |
| Hors ligne, mode agent | profil AWS inexistant, identifiants vides | message `AWS_HELP` clair, code de sortie 1. Défaut mineur : si `--sortie` n'existe pas, `write_index` lève `FileNotFoundError` après ce message (`cli.py:135`) |
| Ce qui échoue | Rien d'obligatoire. Les scripts de `research/experiences/` demandent `arch` et `scikit-learn` absents de `pyproject.toml` (`uv run --with …`) | — |

Adaptation nécessaire : aucune pour le produit (hors copie des données). Le profil AWS `alphaforge` est lu par `boto3` ; aucun identifiant dans le code (grep `AKIA`/`secret` : rien d'observé). Des scripts d'enregistrement d'identifiants ont été retirés de l'archive (NOTE_DE_SELECTION) ; je n'ai ouvert aucun fichier d'identifiants.

## 2. Cas communs

Format d'entrée du produit : `alphaforge agent <persona> --demande "…"` (persona parmi trois, fixés dans `config/personas.toml`). **Il n'existe aucun champ structuré** pour l'âge, le patrimoine, le montant ou la date de retrait : les faits de profil viennent du fichier de persona (`tools.py:77-96`), et `patrimoine`, `capacité de perte`, `liquidité` sont **toujours** enregistrés « inconnu » (`tools.py:101-105`). Tout ce que la personne dit dans la demande n'est donc qu'un texte, lu par le modèle ; le profil d'Amira, Mateo ou Robert est celui de l'énoncé, pas celui de la demande.

Trois exécutions Bedrock réelles (limite du brief) : C1, C2, C5. Mesures : sorties `A-sorties/bedrock/*/dossier.json` (champ `aws`).

| Exécution | Appels | Jetons entrée / sortie | Latence modèle cumulée | Durée mur | Corrections demandées | Verdict du vérificateur |
|---|---|---|---|---|---|---|
| C1 `c1-robert-tsla` | 6 | 63 016 / 9 009 | 50,8 s | 53,6 s | 1 | ok, 21 affirmations, 66 valeurs |
| C2 `c2-amira-btc` | 6 | 61 059 / 9 144 | 53,5 s | 56,2 s | 1 | ok, 21 affirmations, 59 valeurs |
| C5 `c5-contradiction` | 4 | 35 710 / 7 141 | 39,4 s | 41,7 s | 1 | ok, 16 affirmations, 52 valeurs |

Aucun coût en dollars : non mesuré par le produit (je n'en calcule pas ici). Observation : sur les 9 exécutions d'agent connues (3 miennes, 6 jointes), 8 ont exigé une correction du vérificateur : la première soumission du modèle enfreint presque toujours les règles lexicales ; la boucle de correction travaille réellement.

### C1 Robert / Tesla — Exécuté (Bedrock)
- **Projection** : persona `robert`, `--demande "Mon patrimoine investi est de 400 000 CAD. J'aimerais mettre 80 000 CAD dans Tesla (TSLA), on en parle partout. Je prévois de retirer cet argent dans 4 ans."`
- **Question à laquelle le produit répond** : « que devient le profil de risque (baisse maximale, volatilité, part du risque) d'un portefeuille *hypothétique inventé par le modèle* (XBB.TO 40, ZST.TO 10, XIU.TO 25, SPY 25) si TSLA y pèse 20 % ? et quelle part de TSLA respecte un seuil de −15 % (hypothèse du modèle) ? ». Le portefeuille de départ et le seuil ne viennent pas de la demande (« hypothèse de ma part, modifiable »).
- **Sortie** : pas de verdict approuvé/refusé (voulu : « sans approuver ni refuser »). Chiffres (CAD, historique 2021-11-12 → 2026-11-12) : TSLA vol 55,7 %, pire baisse −70,9 %, rendement 2022 −62,6 %, durée sous sommet 2,9 ans ; portefeuille de base : pire baisse −12,9 %, vol 7,4 % ; avec TSLA 20 % : −22,5 %, vol 14,7 %, TSLA = 70,7 % du risque ; part maximale de TSLA sous −15 % : 9 % ; option à 9 % : −14,9 %.
- **Fidélité** : tout nombre passe par une référence. Mais **le 20 % (80 000/400 000) a été calculé par le modèle** et passé en argument d'outil : il apparaît comme « hypothèse, scénario de démonstration » sans lien avec la demande. **Défaut observé** : le dossier dit « Patrimoine total : non renseigné » et « retraits prévus : non renseignée » alors que la demande donne 400 000 CAD et 4 ans (le registre `profile_facts` est figé, `tools.py:101-105`). Le « retrait dans 4 ans » n'a servi qu'à fixer une fenêtre de 4 ans pour `asset_metrics` (trace) ; il n'est pas confronté à l'horizon de 3 à 5 ans du persona dans le texte.
- Traçable : chaque chiffre → `R-nnnn` → registre (libellé, statut, période, conventions) → trace des outils.

### C2 Amira / Bitcoin — Exécuté (Bedrock)
- **Projection** : persona `amira`, « Mon épargne investie est de 40 000 CAD. J'aimerais mettre 10 000 CAD en Bitcoin (BTC-USD). »
- **Question réelle** : effet d'une part de 25 % de BTC (calculée par le modèle) sur un portefeuille de base inventé (SPY 40, XIU.TO 20, QQQ 10, XBB.TO 30) et part maximale sous un seuil de −25 % posé par le modèle.
- **Sortie** : BTC vol 50,7 %, pire baisse −74,2 %, durée sous sommet 2,3 ans ; pire baisse du portefeuille −16,9 % → −31,9 %, BTC = 68,7 % du risque ; part maximale 14 % (pire baisse −24,8 %). Teste « risque élevé ≠ tout est acceptable » : oui, le dossier compare à un seuil et signale la concentration du risque (68,7 % pour 25 % de poids). Même défaut : « patrimoine non renseigné » malgré 40 000 CAD dans la demande. « Option B (étaler l'exposition dans le temps) : non simulée » : limite déclarée.

### C3 Mateo / ESG — **non rejoué** (3 exécutions épuisées) ; dossier joint `runs/mateo-libre-esg` examiné
- Demande jointe : ESGV vs SPY (pas ENB.TO). Le produit n'a **aucune donnée ESG** ; l'agent compare rendement/volatilité/pire baisse/corrélation (0,99) et dit que le filtre n'apporte pas d'avantage de performance. La préférence ESG est citée mais non mesurée ; aucune abstention structurée du type « contrôverses non vérifiables ». Une demande « 15 000 CAD dans ENB.TO » est exprimable (ENB.TO est dans l'univers) mais sans mesure de controverse.

### C4 Information manquante — non rejoué ; comportement déduit de C1 et du démonstrateur
- Le produit ne bloque jamais : `inconnu` est un statut du registre (« Capacité de perte… non renseignée », `tools.py:101`), l'analyse continue sur des hypothèses déclarées « de ma part », et la section `question` pose la question décisive (C1 : trois questions). Absence observée d'un mécanisme qui suspende ou distingue « manquant bloquant » de « manquant balayable ». Conçu : agent 0, variables « nécessaire / à balayer / non informable » (`02-dossier.md` table « Décisions et variables », `03-contrats` Agent 0 points 7-8) ; non implémenté.

### C5 Contradiction — Exécuté (Bedrock)
- **Projection** : persona `robert`, « Mon profil est à risque faible et j'aurai besoin de mon capital dans 2 ans. Je veux tout mettre en Bitcoin (BTC-USD) pour doubler mon capital. »
- **Question réelle** : comparer « tout en BTC » à un portefeuille « Prudent » inventé (XBB.TO 40, ZST.TO 30, XIU.TO 20, GLD 10) et à une petite part de BTC sous −15 %.
- **Sortie** : tout-BTC : pire baisse −72,6 %, vol 50,7 %, rendement annualisé 4,8 % (« loin d'un doublement assuré ») ; Prudent : −8,1 %, vol 4,7 %, rendement 6,0 % ; part maximale de BTC 9 %. Le dossier ne refuse ni n'approuve, nomme l'écart, pose la question de la capacité de perte.
- **Défaut observé** : le persona Robert impose « horizon 3 à 5 ans » ; la demande dit 2 ans. Le texte écrit « horizon minimal de 3,0 ans » et formule la contradiction comme une question (« le besoin est-il ferme ou l'horizon 3 à 5 ans s'applique-t-il ? ») ; aucun calcul sur 2 ans (la fenêtre testée est 3 ans). La contradiction est vue par le modèle, pas par du code.

### C6 Demande impossible — Exécuté en partie (application, sans Bedrock) + dossier joint
- Application, mode référence : `hypotheses.part=50` → HTTP 400 « part étudiée (%) : valeur attendue entre 1 et 30 » ; `actif=GME` → HTTP 400 « symbole inconnu du jeu de données » (`app.py:62-67`). Ce sont des validations d'interface, pas une explication.
- Agent : `runs/robert-libre-gamestop` (joint, non rejoué) : l'outil renvoie `tickers inconnus : ['GME']` (`analytics.py:76-79`), l'agent le dit et propose des alternatives de l'univers. Bon comportement, observé sur dossier joint.
- « 120 000 sur 100 000 » : absence observée de champ de montant ; si la demande le contient, c'est au modèle de le remarquer. `blend()` lève `ValueError` si une part dépasse 1 (`analytics.py:194-195`) → erreur d'outil renvoyée au modèle (`agent.py:228-231`). Non rejoué.

### C7 Modification du profil — Exécuté (application, référence) ; Conçu (versionnement)
- Après le dossier de base (part 10 %) : `hypotheses.horizon=10` → **HTTP 400 « valeur attendue entre 1 et 4 »** (`app.py:68-69`) ; `part=5` → HTTP 200, 0,1 s, 52 valeurs reliées, « TSLA porterait 21,8 % du risque » (contre 44,1 %), champ `hypotheses_modifiees: ["part étudiée"]`.
- **Recalculé : tout** (rien n'est réutilisé ; marché rechargé à chaque requête, `tools.Session`). **Versionné : rien** ; la séance garde l'historique en mémoire du navigateur (`app.py:282-297`, tableau `runs` JS, perdu au rechargement, sans test) ; **comparé : rien** (pas de diff). Conçu : tête/événements/périmé (`02`, `04` §3 « ce qui rouvre, et ce qui reste »), prototype (a) : 39 assertions.

### C8 Révision d'une hypothèse — Exécuté (référence)
- `hypotheses.seuil=10` : HTTP 200 (0,09 s) ; la « part maximale de TSLA » devient « non disponible » (le portefeuille de base a déjà −12,9 % de pire baisse) ; R-0123 « part maximale… » dépend de « Seuil de perte retenu » porte le statut `hypothèse`, origine « scénario de démonstration ». La page ne dit pas « modifié par vous » (seule la légende générique « modifiable » figure dans la page) ; seul le JSON de réponse liste `hypotheses_modifiees`. Les paramètres de méthode (grille 1 point, pas de 5 points, 52 semaines, √52) sont des constantes du code (`tools.py`, `analytics.py:23`) : **non modifiables** depuis l'interface.

### C9 Preuve d'un chiffre — Exécuté (HTML)
- Chemin : nombre cliquable (`<a href="#R-0003">`, infobulle : id, libellé, statut, période) → ligne du registre en annexe (conventions en notes numérotées) → trace d'exécution (outil, arguments, durée). **3 étapes.** Ruptures : le registre ne renvoie ni vers les lignes de prix utilisées ni vers la fonction (origine = « datathon2026.tools » ; le fichier source est dans D-0001…, non lié par `depend_de` aux mesures d'actif, `tools.py:134-142`) ; la formule n'est que décrite par les notes de convention.

### C10 Reprise — Exécuté en partie (code lu) ; absence observée
- Redémarrer le serveur : l'application n'écrit rien sur disque (`app.py` : renvoie le HTML), historique de séance perdu. Interrompre l'agent : `save` n'est appelé qu'à la fin (`cli.py:66`) ; messages du modèle non conservés (LIRE_EN_PREMIER §6) ; tout est rejoué (nouveaux appels Bedrock). Seule reprise existante : `rendre` rend à nouveau un `dossier.json` fini. Je n'ai pas interrompu un appel réel (limite d'appels). Conçu : `04` §6, prototype (c) : un processus tué puis repris ne refait que 2 tâches sur 5, 12 assertions, exécuté.

## 3. Mesures de base

Résultats dans `A-mesures.json`, calculés par `tools.asset_metrics` et `tools.correlation` (les fonctions du produit).

| Actif | Rendement annualisé (CAGR, CAD) | Vol annualisée (hebdo × √52) | Pire baisse (quotidienne) |
|---|---|---|---|
| TSLA | 5,53 % | 55,75 % | −70,88 % |
| BTC-USD | 4,76 % | 50,68 % | −74,18 % |
| ENB.TO | 12,80 % | 17,35 % | −21,38 % |
| SPY | 14,47 % | 14,90 % | −22,25 % |
| Corrélation TSLA–SPY (hebdo, n=261) | 0,513 | | |

Conventions : valeurs en CAD (USD converti au dernier taux Banque du Canada connu, `analytics.py:54-61`) : le rendement de TSLA en USD sans change serait 2,90 % (contrôle), donc le change pèse 2,6 points ; CAGR sur jours calendaires/365,25 (`analytics.py:90-93`) ; la volatilité est hebdomadaire (vendredi), et non quotidienne ×√252 (qui donnerait 58,9 % pour TSLA) ; la pire baisse d'un actif est quotidienne, celle d'un portefeuille hebdomadaire (`tools.py:141`, `tools.py:196`) : **incohérence documentée mais réelle** entre actif et portefeuille.

Contrôle indépendant TSLA (pandas, mêmes CSV, même convention) : 5,5333 % / 55,7500 % / −70,8806 % : écart nul, ce qui valide l'implémentation mais pas le choix de convention (algorithme identique). La relecture de `analytics.cagr`, `annual_vol`, `max_drawdown` n'a pas montré d'erreur. Les rendements annualisés, volatilité et corrélation n'ont **pas de test dédié** (LIRE_EN_PREMIER §5) ; les tests couvrent drawdown, fenêtres, grille hebdomadaire, portefeuille.

## 4. Inventaire des contributions

Etat « constaté » = ce que j'ai vu aujourd'hui. L'archive déclare 77 contributions (`CAPACITES.json`) ; j'en retiens 22 que j'ai pu confronter.

| Id | Nom | Contrat (entrée → sortie) | Provenance | État constaté (déclaré) | Valeur pour le défi | Preuves | Transfert |
|---|---|---|---|---|---|---|---|
| A-01 | Vérificateur de textes à références | texte + registre → liste de problèmes (nombre non relié, mot-nombre, comparatif manuscrit, réf. inconnue) | `evidence.py` (347 l.) | **Vérifié** (Vérifié) | Fort : traçabilité de chaque chiffre | 14 tests ; mon essai adverse : admis à tort « environ mille dollars », « excellent et sans risque », une cause inventée, « pour doubler » ; refusés : « 30 % », « un tiers », « plus risqué que », « 2023 » | **Extractible seul** (stdlib), français seulement, 0,5 j |
| A-02 | Registre typé (D/P/R/…) avec statut hérité | `Registry.add(prefix, label, value, unit, status, origin, period, conventions, inputs)` | `evidence.py:194-262` | Vérifié (Vérifié) | Fort | tests, dossiers | Avec A-01 ; compteurs non restaurés à la relecture |
| A-03 | Comparaisons calculées (`{{cmp:A:B}}`) avec accord grammatical | deux ids de même unité → mot (« supérieure à… ») | `evidence.py:96-160` | Vérifié (Vérifié) | Moyen (français seul) | tests | Avec A-01 |
| A-04 | Marché en CAD, grille hebdo | CSV prix+FX → `Market` | `analytics.py:43-80` | Vérifié (Vérifié) | Fort | recalcul identique TSLA | Extractible avec `data.py` ; conventions à aligner |
| A-05 | Mesures d'actif (CAGR, vol, pire baisse, fenêtres) | série → fractions | `analytics.py:85-152`, `tools.py:131-157` | Exécuté sans test dédié pour CAGR/vol (Vérifié partiel) | Fort | 3 mesures TSLA recoupées | Extractible |
| A-06 | Portefeuille fictif rééquilibré, contributions à la variance | poids → vol, pire baisse, part du risque | `analytics.py:168-189`, `tools.py:160-198` | Vérifié (Vérifié) | Fort (concentration) | tests, C1/C2 | Extractible |
| A-07 | Balayages `share_sweep` / `diversification_sweep` | portefeuille + seuil → part max (grille 1 pt, plafond 30 %) | `tools.py:201-260` | Exécuté (Vérifié) | Moyen : R09 montre que la « part maximale » dépend de l'histoire tirée (X4 bis) ; borne de grille rendue comme maximum (défaut déclaré) | C1 (9 %), C8 (non disponible) | Avec A-04..06 ; **à reformuler** |
| A-08 | Agent unique Bedrock Converse | demande → dossier vérifié | `agent.py` (325 l.) | **Exécuté** ×3 (Vérifié contre client simulé) | Moyen-fort | 3 exécutions, preuve d'appel | Boucle (`_converse`) extractible ; consigne couplée au vérificateur |
| A-09 | Instruction système SYSTEM (4 400 caractères) | — | `agent.py:98-127` | Exécuté | Moyen | voir §5 | Couplée à A-01 (liste lexicale recopiée sans garde) |
| A-10 | Dossier JSON revérifiable, `rendre` hors ligne | `dossier.json` → HTML | `dossier.py`, `report.py`, `cli.py:75` | **Exécuté** (Vérifié) | Fort : explicabilité | 8 dossiers relus, 0 échec | Extractible (`Dossier.from_dict` + `report.render`) |
| A-11 | Preuve d'appel AWS dans le dossier | RequestId, jetons, latence | `agent.py:181-187` | Exécuté | Moyen pour le critère AWS | mes 3 dossiers | Extractible |
| A-12 | Enchaînement fixe (Robert, Amira) | scénario → dossier | `workflow.py` | Vérifié (Vérifié) | Fort comme témoin déterministe | identique aux `runs/` | À garder avec `config/scenarios.toml` |
| A-13 | Application locale | profil, hypothèses → HTML | `app.py` (373 l.) | Exécuté (référence) ; mode agent non rejoué ici | Moyen (UX) | `curl`, `tests/test_app.py` | Stdlib ; historique en mémoire seulement |
| A-14 | Rendu HTML autonome, graphiques SVG | dossier → page | `report.py` (564 l.) | Exécuté | Moyen-fort | 100 Ko, infobulles, annexe | Extractible |
| A-15 | R09 : écart apparié vs niveau, rééchantillonnage par blocs, calibration | scripts de recherche | `research/experiences/*.py` | **Exécuté** : 6 scripts, 5 sorties texte identiques | Fort comme méthode (analyse des données) | diffs vides | **Méthodes transférables** ; dépendances `arch`, `scikit-learn` ; hors produit |
| A-16 | Constat « niveau non établi, écart établi » | — | R09 X3-X8 | Exécuté (déclaré Vérifié) | Fort en honnêteté méthodologique | script `ecart_et_niveau` identique | Contredit ce que le produit affiche (niveaux) |
| A-17 | Registre de sources R07 | 72 sources, niveau de lecture, verdict | `research/R07…md` (1 512 l.) | Exécuté partiel : 2 URL réglementaires répondent HTTP 200 | Moyen pour la présentation | 2 URL testées sur 72 ; textes de tiers non joints (empreintes) | Document ; vérification des 70 autres non faite |
| A-18 | Prototype `dossier_maison` | journal chaîné, pièces par empreinte, greffier | `dossier_maison/dossier.py` (313 l.) | **Exécuté** (Vérifié hors produit) | Potentiel pour C7/C10 | 118 assertions, 1,4 s ; course 8 processus ; contre-épreuve sans verrou : 8 tours sur 10 corrompus | Extractible (stdlib, POSIX `flock`, macOS/Linux) ; **ne gère ni modèle ni tâches volatiles** |
| A-19 | Contrat du dossier versionné (02) | objets, relations, droits | `architecture/02-dossier.md` (217 l.) | Conçu | Fort si construit | prototype couvre ~8 conduites | Voir §9 |
| A-20 | Contrats des quatre agents (03) | dix points par agent | `03-contrats-des-agents.md` | Conçu | Fort sur « recherche critique » et « qualification » | aucune instruction système rédigée | Voir §9 |
| A-21 | Types de résultats + règles de présentation (05) | 7 types, règle « sens établi » | `05-types-de-resultats.md` | Conçu ; seuils non calés | Fort (explicabilité honnête) | R09 les motive | Transférable en spécification |
| A-22 | Critères de réception (09) | A à K, essais écrits d'avance | `09-reception.md` | Conçu | Utile à la fusion | — | Directement réutilisable comme cahier de réception |

## 5. Comportement agentique réel

**Un seul agent** : `BedrockAgent`, modèle `global.anthropic.claude-sonnet-5-5` (`agent.py:22`), API Converse (`agent.py:174`), `maxTokens` 8192, 16 tours, 2 corrections (`agent.py:27-29`).

| Élément | Constat |
|---|---|
| Mission | « orchestrateur d'AlphaForge… SIMULATION… ne donne pas de conseil personnalisé » (`agent.py:98-99`) |
| Instruction | `SYSTEM`, 4 400 caractères, 735 mots (`agent.py:98-127`). Passages décisifs : « Choisis les outils utiles à CETTE demande, et seulement ceux-là » ; « pose une hypothèse explicite et dis dans la section cadre qu'elle vient de toi » ; « Si la demande est incohérente avec le profil, ne l'approuve pas et ne la refuse pas : montre l'écart chiffré, propose des options comparées… » ; « N'écris AUCUN chiffre toi-même… » ; liste des mots de comparaison interdits |
| Contexte transmis | profil (nom), demande, hypothèses de démonstration (JSON) s'il y en a ; en demande libre : **aucune hypothèse** (`agent.py:195-200`, `cli.py:52-53`) |
| Outils | 10 (`TOOL_SPECS`, `agent.py:51-96`) : `lister_actifs`, `profil`, `sources_donnees`, `metriques_actif`, `metriques_portefeuille`, `melange`, `balayage_part`, `balayage_diversification`, `correlation`, `soumettre_dossier` ; exécutés en code, résultats inscrits au registre |
| Condition d'appel | à chaque demande ; un seul appel de bout en bout |
| Sortie | `soumettre_dossier` : titre, résumé, affirmations par section (cadre, profil, constat, tension, alternative, question, condition, limite), `chiffres_cles`, `tableau`, `graphique` |
| Validations par code | vérificateur lexical/numérique (`evidence.py`), références connues, graphique construit par le code, présentation écartée si invalide (`agent.py:242-274`) |
| Boucle | échec → problèmes renvoyés (2 fois au plus) ; **au-delà, le dossier est retenu avec `verification.ok=false`** (`agent.py:217-218`, lu, jamais observé) |
| Incertitude | « inconnu » dans le registre, hypothèses déclarées, section `question` |
| Hors ligne | échec propre (`AWS_HELP`) ; le chemin `demo` reste disponible |

**Ce que le modèle décide réellement** : quelles mesures lancer ; **le portefeuille de départ, le seuil de perte, le plafond, le panier d'alternatives** (hors scénarios écrits) ; le calcul des parts à partir des montants (80/400 = 20 %) ; la rédaction, le choix des options, la question décisive. **Ce que le code décide** : tous les chiffres, le sens et l'accord des comparaisons, le tracé des graphiques, l'acceptation lexicale du dossier. **Ce que personne ne vérifie** : que le seuil et le portefeuille choisis soient raisonnables, que la lecture de la demande soit fidèle (le patrimoine cité est ignoré), que l'argumentation soit juste.

**Apport de l'agentique face à un enchaînement fixe** : `docs/comparaison-agent-workflow.md` (généré depuis `runs/`) montre que sur les scénarios de démonstration l'agent refait à peu près le workflow ; sur les demandes libres (GameStop, ESGV vs SPY, or, tout-BTC), le workflow fixe n'existe pas, l'agent compose un parcours (que j'ai observé en C1, C2, C5 : 3 à 5 outils différents). L'apport est donc la **souplesse de formulation et d'hypothèses**, avec le prix de 35 à 63 k jetons d'entrée et ~45 s ; non mesuré : variabilité d'un tirage à l'autre (un tirage par cas).

## 6. Appréciation par critère (0-4)

| Critère | Cote | Justification |
|---|---|---|
| Adéquation au problème | 3 | Dossier explicable, sans conseil, refuse d'approuver ; pas de qualification, pas de donnée ESG ni de recherche pendant la demande |
| Qualité méthodologique | 3 | Rigueur remarquable en recherche (critères écrits d'avance, 6 scripts relancés) mais le produit affiche encore des niveaux sur 5 ans que la recherche juge non établis |
| Justesse des données et calculs | 3 | Recalcul TSLA identique ; changes traités par report vers l'avant ; incohérence quotidien/hebdo actif vs portefeuille ; CAGR/vol sans test dédié |
| Adaptation au profil | 2 | Trois personas figés ; montant, patrimoine, horizon de la demande ignorés ou non confrontés (C1, C2, C5) |
| Profondeur et fidélité de l'explication | 3 | Chaîne chiffre → registre → trace ; défaut : contrôle lexical seulement, contradictions « non renseigné » vs demande |
| Utilité réelle des agents | 2 | Un agent utile pour les demandes libres ; 8 exécutions sur 9 corrigées par le vérificateur ; hypothèses clés laissées au modèle sans garde |
| Qualité de l'expérience | 2 | Application locale propre, recalcul instantané, mais historique volatil, aucune comparaison de versions, plages bloquantes (horizon ≤ 4) ; non inspectée visuellement (navigateur interdit) |
| Cohérence architecturale | 3 produit / 1 cible | Produit modulaire et petit (2 711 lignes) ; cible détaillée mais non exécutée |
| Facilité et risque d'intégration | 3 | `evidence.py` stdlib ; couplages : libellés comme clés, syntaxe de références lue à plusieurs endroits, français seulement |
| Fonctionnement AWS | 2 | Bedrock Converse réel et prouvé (RequestId, jetons) ; aucune autre ressource ; aucun garde-fou ni S3 ni journalisation |
| Reproductibilité et exploitation | 3 | `uv sync`, 51 tests, démo identique aux `runs/` ; données non fournies ; aucune persistance ni reprise |

## 7. Déclarations confrontées

| Déclaration (LIRE_EN_PREMIER / PRESENTATION) | Verdict | Preuve |
|---|---|---|
| « 51 tests réussis » | **Confirmée** | `pytest` : 51 passed en 6,8 s |
| « Sans les données, 23 tests passent » | Invérifiable ici (données copiées) | non testé |
| « Robert-tsla : 15 affirmations, 52 valeurs, 0 échec » | **Confirmée** | `demo` ; comparaison JSON identique |
| « Aucun nombre écrit par le modèle » | **Nuancée** | Aucun nombre libre admis (essai adverse), mais « mille », causalités et jugements passent ; et le modèle calcule les parts (80/400 → 20 %) en argument d'outil |
| « Le contrôle est lexical et numérique, pas sémantique » | **Confirmée** | essai adverse : « excellent et sans risque », cause inventée admis |
| « `rendre` fonctionne sans données ni AWS » | **Confirmée** (8 dossiers relus) | `cli.py:75`, sortie |
| « Dossier encore en échec retenu avec `ok=false` » | **Confirmée par le code, jamais observée** | `agent.py:217-218` |
| « Application : mode agent Exécuté » | Invérifiée par moi (mode référence seul testé via HTTP) ; code lisible `app.py:78-93` | — |
| « Prototype dossier maison 118 assertions » | **Confirmée** | 118 en 1,37 s, Python 3.12.7 ; contre-épreuve : 8 tours sur 10 acceptent plusieurs écritures sans verrou |
| « Sorties de R09 reproductibles » | **Confirmée** pour 5 scripts texte (diff vide) + 1 JSON non comparé ; 1 script qui appelle Bedrock non rejoué ; `rendement_d_equilibre` interrompu (§8) | `A-sorties/exp_*.txt` |
| « `share_sweep` rend la borne haute quand le seuil n'est jamais franchi » | Plausible, non rejoué (cas `robert-libre-or` joint) | `tools.py:201-220` : `flip = max(ok)` plafonné à 30 % |
| « Registre de sources : 72 sources, 42 confirmées, 30 corrigées » | **Invérifiable en entier** ; 2 URL testées répondent 200 | curl |
| « L'architecture cible n'est pas construite » | **Confirmée** | aucun code d'agent 0/1/3/contradicteur dans `src/` |
| « Produit affiche des niveaux que sa propre recherche dit insuffisants » | **Confirmée** | dossiers montrent vol, pire baisse ; R09 X3, X7 |
| « 77 contributions » | Confirmée (comptage JSON) ; j'ai confronté 22 | `CAPACITES.json` |

## 8. Défauts décisifs et surprises

1. **Le profil reste celui du persona, pas celui de la demande** : patrimoine, montant, date de retrait sont des textes ; le dossier peut afficher « Patrimoine non renseigné » alors qu'il a été donné (C1, C2). Bloquant pour un cas C1 « fidèle ».
2. **Le modèle choisit le portefeuille de base et le seuil** sans demande à la personne ; les chiffres clés dépendent de ces hypothèses (déclarées, mais décisives).
3. **Contrôle lexical** : une cause inventée ou un jugement passent ; le dossier est « conforme » à un contrôle qui ne juge pas le fond.
4. **Absence de persistance** : C7, C10 ; l'application ne garde rien ; plages bloquantes (horizon ≤ 4 ans, part ≤ 30 %).
5. **Écart produit–recherche** : le produit affiche des niveaux ; R09 les juge non établis ; aucune méthode R09 n'est intégrée.
6. **Incohérence** pire baisse quotidienne (actif) / hebdomadaire (portefeuille) (`tools.py:141,196`).
7. **Couplages** : liste lexicale du vérificateur recopiée dans `SYSTEM` sans garde ; libellés d'enregistrements servant de clés (`agent.py:259`, `PROFILE_CARD`).
8. **Données non redistribuables** : l'archive ne les contient pas ; licence à vérifier pour une fusion.
9. **`write_index` après échec AWS** : `FileNotFoundError` si le dossier n'existe pas (`cli.py:135`), mineur.
10. `research/experiences/rendement_d_equilibre.py` n'avait pas terminé après plus de dix minutes de calcul (relance interrompue, voir fin de section) ; deux scripts d'expériences appellent Bedrock (40 + 5 appels) et n'ont pas été rejoués.
11. Le répertoire `docs/refonte/` cite de nombreuses pièces non jointes (fiches, R08, `docs/etat.md`) : preuves de la conception non vérifiables.

## 9. Évaluation de la conception (strate 3)

**Ce qui est précis** : `02-dossier.md` définit ~45 objets (champs, créateur, autorité), 22 tables du catalogue, relations (dérive de, remplace, retiré par…), ensembles nommés, vues ; `03` donne dix points par agent (mission, entrées, outils, décisions autonomes, pièces, format, porte, erreurs, retours, vérification) ; `04` quatre graphes, règles « ce qui rouvre/reste », bornes, états de sortie ; `05` sept types de résultats avec règle de « sens établi » appuyée sur R09 ; `09` critères A à K, chacun falsifiable avec vérification nommée ; `01` §8 liste 12 questions ouvertes honnêtement.

**Ce qui est cohérent avec le défi** : fonctions *qualification* (agent 0), *recherche critique* (agent 1, avec bibliothèque, web, lecteur isolé, plafonnement « étayée avec réserve »), *analyse* (agent 2 + batterie fixe + contradicteur), *restitution* (agent 3, trois profondeurs) correspondent aux quatre fonctions validées. Le principe « pas de nombre écrit par un modèle, sauf recopie citée » prolonge le produit.

**Ce qui reste à écrire pour exécuter** (liste vérifiée par absence) :
- le **catalogue** (22 tables) : « aucune table n'existe » (`00` §7, `01` §8) ; seule la décision « ajouter un titre » est esquissée ;
- les **instructions système** des quatre agents, du contradicteur et du lecteur (aucune rédigée : LIRE_EN_PREMIER §5) ; les schémas JSON machine des pièces (aucun fichier de schéma : seuls trois SVG/PNG dans `architecture/schemas/`) ;
- le **greffier** avec modèles, tâches non déterministes, tâches volatiles (web), délais, annulation (le prototype : six tâches, fonctions pures, une à la fois, sans modèle) ;
- les **portes** de contenu (citation mot pour mot, preuves, analyse) : le prototype ne contrôle que les droits de dépôt ;
- la **batterie fixe** et le moteur de calcul de R09 intégrés au produit (aujourd'hui scripts) ;
- le **calage** des seuils (niveau 90 %, blocs) : « sans source » (`01` §8) ;
- la **relecture humaine** des fiches (aucune faite) ; les essais de réception (09, moitié demandent des personnes) ;
- une interface pour les trois gestes (corriger, changer, explorer).

**Dépendances** : Bedrock + AgentCore (recherche web, essayés par script, pas intégrés) ; bibliothèque `prov` facultative ; compte AWS qui ferme le 16 novembre (`00` §8) ; données ESG, frais, hypothèses de rendement publiées : absentes. **Risques** : le même modèle comme relecteur/contradicteur (non indépendant, dit) ; 15 à 35 appels de modèle par étude, durée non mesurée (« plusieurs minutes », `00` §8) ; ces résolutions retirent des décisions aux rôles (`00` §7) ; 125 constats de revue, 30 restes corrigés, trois familles non corrigées (`01` §10).

**Le prototype `dossier_maison` tourne** : `python3 …/essais.py` → 118 assertions réussies en 1,37 s (Python 3.12.7) ; `--contre-epreuve` : avec verrou aucun tour n'accepte deux écritures ; sans verrou 8 tours sur 10 en acceptent plusieurs, 24 ruptures de chaîne vues (autre passage que le document : 29). Il **prouve** : journal chaîné par empreintes, pièces immuables, péremption sélective (39 assertions), branches (11), concurrence entre processus (huit écrivains, un accepté), reprise après un processus tué (12), retrait d'une pièce erronée (11), export PROV-JSON (5). Il **ne prouve pas** : l'emploi avec de vrais modèles, le retour sur dépendance omise (R14), le contrôle de contenu, Windows, un disque partagé, une coupure de courant. Les fonctions jouet n'ont pas de sens financier.

**Valeur** : c'est une spécification de grande qualité, particulièrement sur révision et typage des résultats ; elle répond directement à C4, C7, C8, C9, C10 de façon que le produit n'atteint pas. Coût estimé par l'archive : 7 à 10 h pour la tranche complète (estimation de l'auteur, non vérifiée) ; je juge cette durée optimiste.

## 10. Recherche (strate 2) : ce que les expériences établissent

Relancés par moi (sorties texte identiques aux conservées, diff vide) : `methodes_analyse.py` (9 s), `calibration_reechantillonnage.py` (45 s), `ecart_et_niveau.py` (13 s), `parcours_contraste.py` et `dossier_illustratif.py` (sorties identiques) et `multivers_exploratoire.py` (code retour 0, non comparé : sortie JSON), graine 2026. Non rejoués : `modele_qualification_et_citations.py` (40 + 5 appels Bedrock). `rendement_d_equilibre.py` : interrompu (voir §8).

Ce qu'elles établissent, sous leurs conditions (cas de Robert, 261 semaines) : (X2) la formule d'annualisation du notebook des organisateurs surestime de plus de 2 points pour 18 actifs sur 31 ; (X3/X7/X8) cinq ans n'établissent ni un rendement moyen ni un niveau de risque (le niveau dépend d'une année : 2022) ; (X4) l'écart apparié entre options est établi dans toutes les variantes essayées ; (X6) une proportion de trajectoires n'est pas une probabilité ; (X5) ne pas contracter vers l'identité. **Transférable** : rééchantillonnage par blocs (`arch`), écarts appariés, grille d'hypothèses de rendement, comparateur de volatilité voisine, règles de présentation (05). Ce sont des **constats sur un cas**, à remesurer (le document le dit). Le registre R07 est exceptionnellement détaillé (niveau de lecture réel, passages cités), mais seuls 2 liens sur 72 sources ont été testés par moi.

## 11. Fichiers de preuve

`reports/A-sorties/` : `demo/`, `rendre-copie/`, `bedrock/{c1-robert-tsla,c2-amira-btc,c5-contradiction}/`, `app/*.txt` (réponses HTTP), `methodes_analyse_relance.txt`, `exp_*.txt`, `verif_adversarial.{py,txt}`, `mesures_calc.py`, `mesures_brut.json`, `resume.py`.
