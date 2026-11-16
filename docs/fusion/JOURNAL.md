# Journal de la tranche 1

## Avant tout

- Lecture complète du prompt 1, du cadre commun et du dossier d'évaluation.
- Premières tentatives bloquées par la lecture seule ; reprise après passage effectif en accès complet.
- `git fetch origin` réussi. Le refspec ne récupérait que la branche d'intégration ; récupération explicite de `refs/heads/feature/interface-parcours:refs/remotes/origin/feature/interface-parcours`.
- Branche propre à `f565abdff58ab4ab07c1f0706e266cc03c408d90`, C à `6761d6636c6c712663cdaf76c739d2bc8f991aef` ; trois SHA-256 conformes.
- Métadonnées de session : fournisseur `amazon-bedrock-runtime`, modèle `global.openai.gpt-6-astra`. Environnement : `AWS_PROFILE=alphaforge`, `AWS_REGION=us-east-1`. Aucun sous-agent : sa route n'était pas vérifiable avant lancement. Outils d'exécution locaux ; tests produit hors ligne.

## Étapes 1 et 2 — socle

- Étiquettes locales `fusion/ref-avant` et `fusion/ref-C` posées.
- `git merge --no-ff --no-commit origin/feature/interface-parcours` : six conflits attendus, tous résolus depuis C.
- Alignement exact de `backend frontend infra data` ; retrait de `frontend/src/composants/Logo.jsx`. Ancienne présentation récupérable par `fusion/ref-avant`.
- Installation des dépendances existantes dans `backend/.venv` (Python 3.13.0).
- `npm install` avait retiré les métadonnées `libc` de Rollup du verrou : restauration du fichier de C avant validation. Versions inchangées.
- 201 tests réussis ; construction Vite réussie ; deux diffs d'identité vides.
- Commit de fusion : `c161a55` (`feat(fusion): aligner le socle sur C évalué`).

## Étapes 3 à 5 — références et kit

- A : 259 fichiers copiés octet pour octet ; seul `data/raw/.gitkeep` exclu. Aucun motif de secret correspondant lors du contrôle. B inchangé.
- Origines et empreintes dans `implementations/REFERENCES.md` et les manifestes.
- Kit copié avec manifeste ; seule métadonnée Finder `.DS_Store` omise.
- Robert, Amira et Mateo figés avant les changements : incohérent / ajustement / incohérent.
- Révision du raccordement K1 autorisée par le porteur ; voir `REVISIONS.md`.

## Étape 6 — contrats

- Commit `d2b893e2b9b1e3b489366a11c687957c0bd88bc9` : références enregistrées avant changements.
- Commit `b46fde2043913c4e3bf2f458ac0f04653eb1ab39` : contrats et seul pont de lecture K1 autorisé.
- 30 tests ciblés réussis (références + contrats) ; test Node du pont réussi.
- Aucun champ comparatif rempli ; aucun appel réel ajouté.

## Étape 7 — qualification

- Commit `bce87e5250faf737eace1bfd0cbd36b0b6c9923d` : trois défauts corrigés dans le Gardien et l'API ; champs numériques normalisés à la frontière HTTP.
- 249 tests Python réussis, construction Vite réussie, 1 test Node réussi.
- Contrôles HTTP réels en local : résultats attendus pour les personas, la demande impossible, les types d'entrée et l'actif inconnu ; serveur local arrêté.
- Dossiers complets inchangés hors durées et trois champs nouveaux ; empreintes avant/après identiques.
- Archives originales, kit et import B inchangés ; 259 fichiers et blobs Git de A identiques à l'archive.

## Étape 8 — clôture

- Preuves et compte rendu consolidés dans `docs/fusion/preuves/tranche-1/` et `COMPTE-RENDU.md`.
- Le commit de clôture de ce journal sera étiqueté `fusion/t1`, puis poussé sans force vers `origin/fusion-corrections-deploiement`. La réponse finale donne le SHA vérifié sur le distant.
- Aucune ressource AWS créée et aucun déploiement.

# Tranche 2 — Analyse du portefeuille appariée

## Départ et périmètre

- Prompt 2 externe et cadre commun relus intégralement. Autorisations explicites
  du prompt reçu : push de `fusion/analyse`, sans force, après tests verts.
- `git fetch origin` réussi ; départ propre de `fusion/t1`,
  `f767a3b2b5bb98bac0c23619d973bbb8b9b2aca7`.
- `git worktree add ../POLYFINANCE-fusion-analyse -b fusion/analyse f767a3b2b5bb98bac0c23619d973bbb8b9b2aca7`.
  Écritures uniquement dans ce nouvel arbre ; dossier et branche vérifiés avant
  chaque commit. Aucun accès à la tranche AWS.
- Champs de contrat présents et baseline **249 passed in 8.83s**.
- Route de session vérifiée : Bedrock, modèle `global.openai.gpt-6-astra`,
  profil `alphaforge`, région `us-east-1`. Outils natifs ; aucun sous-agent,
  sa route n'étant pas vérifiable préalablement. Tests produit hors ligne.

## Transferts et raccordement

- `a61b6bd` : deux modules et huit tests pris dans l'archive B vérifiée ;
  `blend` extrait de A ; cinq tests d'allocation ajoutés. Formules inchangées.
- K3 : un appel apparié, mêmes séances et données pour les deux bras, unités
  publiques vérifiées, données et change mis en cache, erreurs explicites.
- Analyste : faits sourcés et hypothèses ; Gardien : K5, attribution d'un état
  antérieur, fallback inchangé ; personas : poids fictifs explicites.
- Robert : capacité orange, verdict incohérent conservé. Amira/BTC : capacité
  rouge et verdict incohérent. Mateo : exclusion rouge conservée.
- Retrait manquant de Robert : contre-hypothèse à l'horizon, question décisive,
  profil et verdict courant conservés.

## Révision autorisée et performances

- Amira/XIU.TO démontre l'incompatibilité : 14 000 CAD → ajustement,
  17 500 CAD → cohérent. Preuve et options consignées avant l'arbitrage.
- Le porteur choisit K5 exact et la monotonie conditionnelle, puis autorise
  la révision de l'invariant 7. Les six conditions sont appliquées et testées.
- Recherche exhaustive au pas de 100 CAD, distance minimale dans les deux
  sens, texte constatif ; 16 300 CAD est le premier état amélioré depuis
  14 000 CAD de XIU.TO pour Amira.
- Réutilisation des primitives inchangées de B pour la perte seule pendant la
  recherche ; comparaisons complètes conservées pour K3. Égalité vérifiée.
- Critique facultative `portefeuille_entier` : trois issues, au plus trois
  objections, aucun changement du verdict.
- `996b849` : raccordement fonctionnel et tests ; **310 tests verts** avant
  régénération des trois références.

## Références et réception

- `7e9f24c` : commit séparé des références, avec tous les changements d'état
  et de niveau dans son message. Les 47 valeurs des faits antérieurs restent
  identiques ; les références T1 restent disponibles dans Git.
- Réception complète : **313 passed in 18.41s**. Construction Vite :
  **39 modules**, **482 ms**, dépendances et verrou inchangés.
- Trois mesures par cas, caches applicatifs vidés : maximum Robert 319,557 ms,
  Amira/BTC 617,355 ms, Mateo 274,986 ms, Amira/XIU 301,206 ms.
- Trois archives et transferts contrôlés. `implementations/`, données,
  infrastructure, frontend et fichiers réservés inchangés depuis T1.
- Le prompt reçu contient les autorisations et l'isolation ajoutées depuis
  T1 : différence reconnue dans la preuve, manifeste historique préservé.
- Le dépôt principal reste propre sur `f767a3b`.

## Clôture et transmission

- Compte rendu en six parties et preuves rassemblés dans `preuves/tranche-2/`.
  Le commit de clôture sera étiqueté localement `fusion/t2` puis poussé, sans
  force, vers `origin/fusion/analyse`. La réponse finale donne le SHA distant vérifié.
- Prompt 4 : curseurs compatibles avec une grille non monotone ;
  `bascule.monotonie_montant` et `option.sens`/`option.constat` à afficher sans
  qualification d'erreur ni conseil d'achat supplémentaire.
- Poids fictifs signalés au porteur pour validation ; approximation disponible.
- Extension G non réalisée. Aucune ressource AWS, aucun déploiement, aucune
  fusion dans l'intégration et aucune exécution de la tranche 3.
