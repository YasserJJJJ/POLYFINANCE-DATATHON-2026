# PROMPT 1 — Socle et contrats (à exécuter seul, en premier)

```
AUTORISATIONS (à remplir par le porteur avant l'envoi)
- git push de la branche d'intégration : OUI, vers origin/fusion-corrections-deploiement, sans --force, après tests verts
- création de ressources AWS : OUI (accordée par le porteur ; cette tranche n'en crée aucune)
```

Tu es l'agent intégrateur de la fusion AlphaForge. Trois réalisations indépendantes du même projet (A, B, C) ont été évaluées ; la décision est d'enrichir le socle C avec des modules précis de B et de A. Tu exécutes la **tranche 1 sur 4** : mettre la branche d'intégration au niveau du socle évalué, ranger les trois références, figer l'état de départ et inscrire les contrats communs dans le code. Tu ne transfères encore aucune fonction de A ou de B.

## Avant tout

1. Lis en entier `/Users/vpro/Downloads/IMPLEMENTATION/fusion-kit/CADRE-COMMUN.md`. Il fixe la décision, les invariants, les contrats K1 à K7, les règles d'écriture et le format du compte rendu. En cas de doute entre ce prompt et le cadre, le cadre prime ; signale la contradiction.
2. Vérifie l'état réel et arrête-toi si l'un de ces points est faux (écris ce que tu constates) :
   - `cd /Users/vpro/Documents/ChatGPT/POLYFINANCE-DATATHON-2026 && git status -sb` : branche `fusion-corrections-deploiement`, arbre propre ;
   - `git fetch origin` puis `git rev-parse origin/feature/interface-parcours` commence par `6761d66` ; `git rev-parse HEAD` commence par `f565abd` (si la branche a avancé, lis les nouveaux commits et dis ce qui change pour ce plan avant de continuer) ;
   - les trois archives existent et leurs SHA-256 sont ceux du cadre, section 3 (`shasum -a 256`).
3. Les inférences de cette session passent par la route convenue par le porteur. Si ce n'est pas le cas, dis-le avant de commencer.

## Résultat attendu

À la fin, la branche `fusion-corrections-deploiement` contient : le code de C tel qu'évalué (`6761d66`), l'import de B déjà présent, la référence A, le kit de fusion sous `docs/fusion/`, les références figées des trois personas, et les champs de contrat K1, K3, K6, K7 présents mais inactifs. Les 201 tests passent, l'interface se construit, et un dossier produit avant et après la tranche est identique aux nouveaux champs près.

## Étapes

**1. Repères.** Pose les étiquettes locales `fusion/ref-avant` sur `f565abd` et `fusion/ref-C` sur `origin/feature/interface-parcours`.

**2. Aligner la branche sur le socle évalué.** Fusionne `origin/feature/interface-parcours` dans `fusion-corrections-deploiement` (`git merge --no-ff`). Six conflits sont attendus (liste dans le cadre, section 2). Résous **chacun en prenant la version de `feature/interface-parcours`** : cette branche contient déjà, portés, les correctifs et le déploiement de la branche d'intégration. Conserve `implementations/codex/` sans y toucher.
   Une fusion Git peut aussi mêler sans conflit des morceaux propres à la branche d'intégration (style clair, logo). Avant de valider la fusion, ramène donc ces dossiers exactement à l'état évalué : `git checkout fusion/ref-C -- backend frontend infra data`, puis retire de l'index les fichiers de ces dossiers que `fusion/ref-C` ne contient pas (par exemple `frontend/src/composants/Logo.jsx`). Liste dans le compte rendu ce qui est ainsi écarté : tout reste récupérable par l'étiquette `fusion/ref-avant`, et le choix d'habillage revient au porteur (décision 3 du cadre).
   Contrôle : `git diff --stat fusion/ref-C -- backend frontend infra data` ne montre aucun écart ; `git diff --stat fusion/ref-avant -- implementations` non plus.
   Contrôle : `cd backend && python -m pytest -q` donne 201 réussis ; `cd frontend && npm install && npm run build` réussit.

**3. Ranger les références.**
   - Extrais l'archive A dans `implementations/claude-code/` (sans `data/raw`, que l'archive ne contient pas). Ajoute `implementations/claude-code/IMPORT.md` : origine, SHA-256 de l'archive, mention « import de fichiers, pas une fusion fonctionnelle », sur le modèle de `implementations/codex/IMPORT.md`.
   - Ne duplique pas B. Écris `implementations/REFERENCES.md` : pour A, B et C, l'archive de référence, son SHA-256, son équivalent Git, et la règle « tout fichier transféré de B se prend dans l'archive 0.7.0, pas dans `implementations/codex/` » (cette copie est plus large et plus ancienne ; `alphaforge_app/analytics.py` y est identique, `datasets.py` non).
   - Vérifie avant de commiter qu'aucun fichier importé ne contient de secret (`grep -rIlE 'AKIA[0-9A-Z]{16}|aws_secret_access_key|BEGIN (RSA|OPENSSH) PRIVATE'`) ; n'ouvre pas `infra/enregistrer_identifiants.ps1`.

**4. Installer le kit.** Copie `/Users/vpro/Downloads/IMPLEMENTATION/fusion-kit/` dans `docs/fusion/` (cadre, dossier d'évaluation, prompts, preuves). Crée `docs/fusion/JOURNAL.md` et `docs/fusion/COMPTE-RENDU.md`.

**5. Figer l'état de départ.** Écris `backend/tests/reference/` avec, pour Robert, Amira et Mateo (`alphaforge.personas.PERSONAS`), le dossier complet rendu hors ligne (`ALPHAFORGE_LLM=off`), en JSON trié. Ajoute un test `test_reference_personas.py` qui rejoue les trois analyses et compare : état du verdict, code et niveau de chaque règle, libellé / valeur / unité / type de chaque fait, options et grille. Le test neutralise ce qui varie légitimement (durées). Ce test est le filet de non-régression des tranches suivantes ; quand une tranche change volontairement une valeur, elle régénère la référence dans un commit séparé qui dit quoi et pourquoi.

**6. Inscrire les contrats (champs présents, comportement inchangé).** Tu es le seul à modifier `backend/alphaforge/dossier.py` et `docs/contrats.md`.
   - `Dossier` : ajoute `version_contrat: str = "2"`, `comparaison: dict` (vide par défaut, forme K3), `appels_modele: list[dict]` (vide par défaut, forme K6). Rien ne les remplit dans cette tranche.
   - `profil.py` : ajoute la fonction K1 qui normalise `portefeuille_actuel` et rend `(poids, origine)`. Elle accepte la liste actuelle et le dictionnaire de poids, refuse une somme différente de 1, des poids négatifs ou non numériques, et rend `(None, None)` si le portefeuille est vide. Ajoute ses tests. **Ne change aucun appelant** : partout où le code lit `portefeuille_actuel` comme une liste de symboles (`gardien.py`, `orchestrateur.py`, `agents/analyste.py`, `agents/sceptique.py`, `frontend/`), il doit continuer à recevoir une liste ; si un dictionnaire arrive, ces appelants en lisent les clés. Fais ce pont dans une seule fonction d'accès et couvre-le par un test.
   - Point de branchement de la preuve d'appel : ajoute dans `llm.py` une fonction `journal_appels()` qui rend pour l'instant une liste vide, et à la fin de `orchestrateur.analyser` l'affectation `d.appels_modele = llm.journal_appels()`. La tranche 3 remplira le journal sans toucher à l'orchestrateur ; la tranche 2 pourra modifier l'orchestrateur sans toucher à `llm.py`.
   - `docs/contrats.md` : ajoute une section « Contrat 2 (fusion) » qui reprend K1 à K7 et le tableau d'autorité des mesures.
   - Contrôle : références figées inchangées aux trois nouveaux champs près ; 201 tests + les tiens.

**7. Corriger trois défauts du socle constatés à l'évaluation** (petits, dans `gardien.py` et `api.py`, avec un test chacun). Ils touchent la qualification et servent les cas de réception :
   - **Demande impossible** : `montant_cad` supérieur à `epargne_totale_cad` donne aujourd'hui un verdict « incohérent » avec « 120 % de ton épargne ». Il doit donner `indetermine` par la règle `donnees`, avec la raison écrite (« le montant dépasse l'épargne totale »).
   - **Actif hors univers** : un symbole inconnu donne aujourd'hui une erreur 422 brute. La réponse doit rester une erreur, avec un message en français qui dit que l'actif n'est pas dans les 31 actifs du jeu de départ ; l'interface l'affichera en tranche 4.
   - **Types d'entrée** : `horizon_ans: "4"` ou `montant_cad: "80000"` donnent aujourd'hui une erreur 500. Une valeur numérique sous forme de chaîne est convertie ; une valeur non numérique est traitée comme invalide par la règle `donnees` ; `exclusions` en chaîne est lue comme une liste d'un élément.
   Ne corrige rien d'autre du socle dans cette tranche ; note ce que tu vois dans le compte rendu.

**8. Clore.** Étiquette `fusion/t1`. Complète `docs/fusion/COMPTE-RENDU.md` (format du cadre, section 13) avec les sorties de : `pytest -q`, `npm run build`, le `git diff --stat` de l'étape 2, et la liste des fichiers ajoutés. Donne en fin de réponse le commit de fin de tranche : les tranches 2 et 3 partent de lui.

## Fichiers que tu possèdes dans cette tranche

Tout le dépôt pendant la fusion Git de l'étape 2 ; ensuite `backend/alphaforge/dossier.py`, `backend/alphaforge/profil.py`, `backend/alphaforge/gardien.py` et `backend/api.py` (étape 7 seulement), `backend/alphaforge/orchestrateur.py` et `backend/alphaforge/llm.py` (point de branchement de l'étape 6 seulement), `backend/tests/`, `docs/`, `implementations/`.

## Ce que tu ne fais pas

Pas de transfert de `analytics.py` ni d'autre module de A ou B ; pas de changement d'interface ; pas de changement de seuil ; pas de `git push`, pas de déploiement, aucune ressource AWS, sauf autorisation écrite en tête de ce message. Si une étape échoue deux fois, applique la procédure de révision du cadre (section 8) et continue sur le reste.

## Critère d'arrêt

Tous les contrôles ci-dessus sont verts et consignés avec leur sortie, ou bien un blocage est décrit avec la commande, la sortie et deux options. Ne déclare pas la tranche terminée sur la foi d'une lecture de code.
