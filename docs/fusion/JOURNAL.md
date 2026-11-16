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


# Tranche 3 — AWS

## Avant tout et autorisations

- Lecture intégrale du prompt 3 et du cadre ; copie du prompt reçu dans les preuves.
- Arbre `../POLYFINANCE-fusion-aws`, branche `fusion/aws`, au commit T1 `f767a3b2b5bb98bac0c23619d973bbb8b9b2aca7`.
- STS confirme `471112821226` / `WSParticipantRole` ; aucun identifiant lu. Route intégrateur Bedrock/Astra vérifiée.
- Le porteur distingue les inférences de l’intégrateur et celles du produit : Nova/Sonnet autorisés via Bedrock alphaforge.
- Inventaire AWS initial vide pour AlphaForge ; deux profils Bedrock actifs ; simulation des 33 actions autorisée.

## A et B — preuve et reprise

- Collecteur Converse transféré de A et vérifié contre l’archive ; adaptation K6, portées d’analyse et liaison des traces.
- Reprise configurable, isolation des erreurs par modèle, renouvellement des clients après erreur d’identifiants.
- Profil par défaut alphaforge ; santé enrichie sans numéro de compte. Aucun appelant d’agent modifié.
- Deux vraies analyses HTTP NDJSON simultanées avec client simulé prouvent l’isolation des journaux.

## C — appels locaux

- Robert, Amira et texte contradictoire enregistrés avec références hors ligne identiques pour décisions et grille.
- 3 / 3 / 4 appels ; 6 035 / 5 703 / 10 371 jetons. Le dernier dépasse la plage de durée initiale : 23,224 s.
- Première capture corrigée (`bascule`, non `grille`) sans rejouer Robert ; durée HTTP Robert non disponible.

## D — durcissement et construction

- Plans lecture seule enregistrés et affichés ; CORS exact, ARN résolus sans joker Bedrock, concurrence Lambda 2.
- Nettoyage des seules créations journalisées ; aucun essai de ressource pour sonder les permissions.
- Paquet Linux Python 3.12 et interface construits ; dateutil borné à <3 après conflit réel avec botocore.
- Mangum déjà déclaré, 19 tests ajoutés au total ; 268 tests réussis, frontend et références originales inchangés.

## E — Guardrail et publication

- Guardrail `xj89p36uyw64`, version 1, créé après le plan. Premier raccordement défectueux diagnostiqué sur AWS.
- Question d’ancrage ramenée sous 1 000 caractères, blocs qualifiés, périmètre limité au Rédacteur ayant une source.
- Réponse normale acceptée ; conseil bloqué par Bedrock et remplacé exactement par le gabarit du Rédacteur.
- Commit du code `b385412f60c960509f14e7e3430e7c29bf977e40` après contrôles de dossier et branche.
- Script durci exécuté avec Guardrail : Amplify, S3, IAM, Lambda et CloudWatch créés avec journaux d’identité.
- Interface `https://main.d1d3b8g2y5hkdd.amplifyapp.com`, santé publique réussie, CORS vérifié.
- Robert public complet, décisions identiques hors ligne, quatre appels Bedrock et copie S3 strictement égale.
- NDJSON : première ligne 18,302999 s, dernière 18,329150 s. Constat : reçu d’un bloc, à transmettre au prompt 4.
- Empreinte du ZIP distant égale au paquet local ; IAM effectif égal au plan, S3 privé, concurrence réservée 2.
- Réception publique rejouée avec le Python système après erreur de certificats du venv ; TLS jamais désactivé.
- Serveurs locaux de vérification arrêtés. Ressources AWS conservées après succès ; suppression documentée.

## Clôture

- Preuves, tableau d’appels, inventaire, commandes de suppression et compte rendu T3 consolidés.
- Aucun fichier de la tranche 2 ou de l’interface modifié, aucun original altéré, aucune fusion entreprise.
- Le commit documentaire de clôture porte l’étiquette locale `fusion/t3`. Push autorisé sans force vers
  `origin/fusion/aws` après les 268 tests verts ; le SHA distant vérifié est donné dans la réponse finale.
- La publication et les données AWS disparaîtront à la fermeture annoncée du compte le 16 novembre à 13 h 59.
