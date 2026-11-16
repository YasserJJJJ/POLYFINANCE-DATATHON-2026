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
