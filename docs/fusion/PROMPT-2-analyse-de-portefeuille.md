# PROMPT 2 — Analyse de portefeuille appariée (après le prompt 1, en parallèle du prompt 3)

```
AUTORISATIONS (à remplir par le porteur avant l'envoi)
- git push : NON
- création de ressources AWS : NON
COMMIT DE DÉPART (fin de la tranche 1) : ____________
```

Tu es l'agent intégrateur de la fusion AlphaForge, **tranche 2 sur 4**. Le socle C juge une demande d'achat avec la formule `part × pire chute du titre`, qui suppose que le reste du portefeuille ne bouge pas. Tu y transfères le moteur historique de B pour mesurer le portefeuille **avant et après** la demande, tu fais juger la règle « perte supportable » sur cette mesure, et tu rends décisive une information manquante que le socle ignore en silence. Un autre agent exécute en même temps la tranche 3 (AWS) dans un autre arbre de travail : ne touche pas à ses fichiers.

## Avant tout

1. Lis en entier `docs/fusion/CADRE-COMMUN.md` (dans le dépôt depuis la tranche 1), en particulier les invariants (section 5), les contrats K1 à K5 (section 6) et les règles d'écriture (section 9).
2. Crée ton arbre de travail : depuis `/Users/vpro/Documents/ChatGPT/POLYFINANCE-DATATHON-2026`, `git worktree add ../POLYFINANCE-fusion-analyse -b fusion/analyse <commit de départ>`. Travaille uniquement là.
3. Vérifie le départ : `cd backend && python -m pytest -q` (201 tests du socle + ceux de la tranche 1, tous verts), et les champs `comparaison`, `appels_modele`, `version_contrat` présents dans `dossier.py`. Sinon arrête-toi et dis ce qui manque.

## Faits établis par l'évaluation (ne les redécouvre pas, vérifie-les au passage)

- `alphaforge_app/analytics.py` et `alphaforge_app/datasets.py` de l'archive B n'importent que la bibliothèque standard. `load_dataset(chemin)` lit `assets_universe.csv`, `prices_daily.csv`, `fx_usdcad_daily.csv` du jeu de départ sans adaptation ; `compare_portfolios(options, capital_cad, dataset=…)` rend pour chaque option `max_drawdown_pct`, `volatility_pct`, `cagr_pct`, `ending_value_cad`, des dates, et un bloc `meta` avec conventions et `limitations`. Trois portefeuilles comparés : environ 0,3 s, chargement compris.
- Expérience de référence (`docs/fusion/preuves/EXP-couplage-B-vers-C.json`, script `exp_couplage.py`), poids équipondérés, placement obtenu par `set_target_weight` :

| Persona | Pire baisse avant | Pire baisse après | Écart | Formule actuelle de C |
|---|---|---|---|---|
| Robert, 20 % TSLA sur XIU/XBB/RY | −14,26 % | −20,60 % | −6,34 points | 14,2 % (sous la limite de 15,5 %) |
| Amira, 25 % BTC sur QQQ/NVDA | −46,81 % | −50,61 % | −3,80 points | 18,4 % |
| Mateo, 12,5 % ENB.TO sur XIU/XBB | −13,16 % | −12,06 % | +1,10 point | 2,7 % |

- Les deux moteurs ne donnent pas la même valeur pour un titre seul (TSLA : −70,9 % chez C, −69,8 % chez B) parce que B travaille sur la grille commune de 1 228 séances. C'est attendu ; règle K4.
- `set_target_weight` de B **fixe** un poids ; `blend` de A (`src/datathon2026/analytics.py:192-198`) **ajoute** une part. Le produit dit « ce placement s'y ajoute » : c'est `blend` qu'il faut (K2).

## Résultat attendu

Pour toute demande dont le portefeuille actuel est connu, le dossier contient une comparaison appariée avant/après (K3) dont chaque nombre est un fait sourcé ; la règle « perte supportable » la juge (K5) ; une donnée manquante qui changerait le verdict devient une question marquée décisive. Tous les invariants tiennent, en particulier : aucun modèle n'influence un chiffre ni le verdict, et la grille reste monotone en montant.

## Étapes, par ordre de priorité

**A. Transférer le moteur (obligatoire).**
- Copie depuis l'archive B 0.7.0 (pas depuis `implementations/codex/`) `alphaforge_app/analytics.py` et `alphaforge_app/datasets.py` vers `backend/alphaforge/moteurs/historique/`, **sans modifier leurs formules**. Seules adaptations permises : l'import relatif entre les deux fichiers et un en-tête de provenance (archive, chemin d'origine, SHA-256 du fichier d'origine, date). Vérifie les empreintes d'origine contre le cadre, section 4.
- Copie `tests/test_analytics.py` de B dans `backend/tests/test_moteur_historique.py` en adaptant les imports et le chemin des données ; ces tests doivent passer tels quels. S'ils demandent une marque `market_data` ou une variable de données, branche-les sur `ALPHAFORGE_DATA` du socle.
- Écris l'opération K2 (ajout d'une part) en reprenant `blend` de A, avec son test (part hors de [0, 1] refusée ; ligne déjà détenue : la part s'ajoute).

**B. Adaptateur et faits (obligatoire).** Nouveau module `backend/alphaforge/portefeuille.py` :
- entrée : profil, demande ; sortie : le dictionnaire K3 ;
- poids par la fonction K1 de `profil.py` ; allocation après par K2 ; un seul appel à `compare_portfolios` pour les deux bras ; le jeu de données est chargé une fois et mis en cache comme le fait `donnees.py` ;
- conversion des unités à cette frontière et nulle part ailleurs (le moteur rend des pourcentages en points pour ses métriques ; vérifie-le sur la sortie, ne le suppose pas) ;
- `disponible: false` avec une raison en français pour : portefeuille inconnu, symbole absent, erreur de données (`DataError`), montant supérieur à l'épargne. Aucune exception ne remonte à l'API ;
- les écarts et leur sens (`aggrave`, `ameliore`, `neutre`) sont calculés ici, par le code.
Dans `agents/analyste.py`, ajoute les faits correspondants avec `dossier.ajouter_fait` : pire baisse du portefeuille avant, après, écart ; volatilité avant, après ; l'hypothèse d'équipondération si elle a servi (type `HYPOTHESE`). Type des mesures : `FAIT` pour le portefeuille actuel déclaré, `SCENARIO` pour l'allocation après la demande. La méthode de chaque fait nomme le moteur et sa convention (K4). Ajoute au registre `sources.py` les références de ces faits (moteur, données, limites) en suivant la forme des entrées existantes.

**C. Règle « perte supportable » (obligatoire).** Dans `gardien.py`, règle `capacite` :
- si `ALPHAFORGE_CAPACITE` ne vaut pas `approximation` et que la comparaison est disponible, l'impact jugé est la valeur absolue de la pire baisse du portefeuille après la demande ; les seuils et les niveaux (tolérance → orange, capacité → rouge) ne changent pas ;
- le texte de la règle donne la valeur après, la valeur avant et l'écart, et relie les trois faits ;
- **attribution** : quand le portefeuille actuel dépassait déjà la limite avant la demande, le texte le dit, et la règle ne passe pas au rouge du seul fait de cet état antérieur si la demande ne l'aggrave pas. C'est une décision de règle, donc une hypothèse d'équipe : inscris-la comme fait `HYPOTHESE` et signale-la au porteur dans le compte rendu (décision 4 du cadre) ;
- sinon, calcul actuel inchangé, et son texte dit qu'il suppose le reste du portefeuille stable.
`grille_bascule` et `plus_petit_ajustement` appellent la règle pour chaque montant : la comparaison doit donc être recalculable par montant sans recharger les données (l'horizon ne la modifie pas ; 8 montants plus la dichotomie). Mesure la durée d'une analyse hors ligne avant et après ; elle doit rester sous 1 s.
Contrôle de monotonie : les tests du banc doivent rester verts. La pire baisse d'un mélange n'est pas forcément monotone en fonction de la part ; si un test de monotonie casse, **ne l'efface pas** : remplace la dichotomie de `_montant_exact` par une recherche exhaustive au pas existant sur l'intervalle, ou applique la procédure de révision du cadre.

**D. Personas et références (obligatoire).** Donne aux trois personas de `personas.py` des poids explicites (fictifs, à faire valider : décision 5 du cadre) en gardant les symboles actuels. Régénère les références figées dans un commit séparé dont le message liste chaque changement d'état de verdict ou de niveau de règle, persona par persona. Attendu au minimum : Robert reste `incoherent`, Mateo reste `incoherent` par exclusion. Si l'état d'Amira change, ne le masque pas : décris le changement et laisse la bascule `ALPHAFORGE_CAPACITE=approximation` documentée.

**E. Information décisive manquante (obligatoire, petit).** Aujourd'hui, sans date de retrait, Robert/Tesla passe d'`incoherent` à `ajustement` et aucune question n'est posée. Dans `orchestrateur.py` (et `gardien.py` si nécessaire) : quand `retrait_prevu_ans` est absent, recalcule le verdict sous l'hypothèse « retrait à l'horizon déclaré » ; si l'état diffère, ajoute à `questions` une question marquée décisive qui dit ce qui changerait, et un fait `HYPOTHESE` qui porte l'hypothèse testée. Le verdict affiché reste celui des données fournies ; aucune valeur n'est supposée à la place de la personne. Un test couvre Robert sans retrait.

**F. Critique (si le temps le permet).** Dans `agents/sceptique.py`, ajoute au catalogue fermé une vérification `portefeuille_entier`, applicable quand la comparaison est disponible : elle conteste le fait « perte supportable » par la mesure du portefeuille et rend `confirmee`, `ecartee` ou `limite` selon un test que le code exécute. Elle ne modifie pas le verdict (la règle C l'a déjà pris en compte de façon déterministe) ; elle rend la critique visible. Garde le plafond de trois objections.

**G. Part du risque (facultatif, seulement si A à E sont verts et consignés).** Reprends de A (`analytics.py:159-190`) le calcul de la part de la variance portée par chaque ligne sur rendements hebdomadaires, et ajoute un fait « part du risque portée par <actif> après la demande ». Fait d'éclairage, non relié à une règle.

## Fichiers que tu possèdes

`backend/alphaforge/moteurs/` (nouveau), `backend/alphaforge/portefeuille.py` (nouveau), `backend/alphaforge/gardien.py`, `backend/alphaforge/orchestrateur.py`, `backend/alphaforge/agents/analyste.py`, `backend/alphaforge/agents/sceptique.py`, `backend/alphaforge/personas.py`, `backend/alphaforge/sources.py`, `backend/tests/` (tes tests et les références), `docs/sources.md` (régénéré par `generer_doc_sources.py`).

Tu ne touches pas : `dossier.py`, `profil.py` (tu appelles la fonction K1 ; si elle doit changer, procédure de révision), `llm.py`, `api.py`, `infra/`, `frontend/`, `agents/redacteur.py`, `docs/contrats.md`.

## Vérifications à consigner (commande et sortie)

1. `pytest -q` : aucun test du socle perdu ; tests du moteur transféré verts ; tes tests verts.
2. Test discriminant du gain : pour Robert, `capacite` cite la pire baisse du portefeuille après (proche de −20,6 % avec poids équipondérés ; donne ta valeur avec les poids retenus) et la valeur avant ; le même test, sous `ALPHAFORGE_CAPACITE=approximation`, retrouve 14,2 %.
3. Égalité des deux bras : `avant` recalculé seul par `analyze_portfolio` donne les mêmes valeurs que dans la comparaison.
4. Invariant « sans modèle » : dossier hors ligne et dossier avec un faux client de modèle : verdict, règles, options, grille et `comparaison` identiques.
5. Cas limites : portefeuille vide (`disponible: false`, règle sur l'ancien calcul) ; ligne déjà détenue ; cryptoactif (le moteur signale qu'il l'échantillonne aux séances communes : la limite doit apparaître) ; montant égal à l'épargne.
6. Durée d'une analyse hors ligne avant et après.

## Clore

Ne fusionne rien toi-même dans la branche d'intégration : laisse `fusion/analyse` prête, étiquette `fusion/t2`, complète `docs/fusion/COMPTE-RENDU.md` (section « Tranche 2 », format du cadre) et `JOURNAL.md`. Liste le code neuf avec son motif (adaptation, contrat manquant, incompatibilité) et, pour chaque fichier transféré, archive, chemin et empreinte. Termine par les décisions attendues du porteur.
