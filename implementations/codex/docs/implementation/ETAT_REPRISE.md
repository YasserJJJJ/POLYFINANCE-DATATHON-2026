# État de reprise — Prompt 5 livré

Version **0.5.0**, 15 novembre 2026. Instance locale à
`http://127.0.0.1:8768` ; PID/port dans `runtime/server.json`.
Les autorisations de construction et correction restent acquises.

La [défense du résultat](../defense/README.md), les
[décisions de correction](../defense/decisions_corrections.md) et les
[preuves de vérification](../defense/proofs/verification.json) constituent
le dernier état. Trois nouvelles sessions indépendantes ont revu finance,
chaîne et preuves ; leurs routes AWS sont conservées.

| Dossier Prompt 5 | ID | État |
|---|---|---|
| Robert extrait, retrait corrigé puis risque corrigé | `4089e4b0d70f40b6b20d832fa261e1dc` | r15, terminé ; analyses@1/2/3 : 30k, 40k, 74,4k CAD |
| Amira politique v2 | `f281a9067e4544138fa178fa4ee0b850` | r5, terminé, descriptif conditionnel |
| Demande incomplète | `e6405c6c61f64c5b89c11262ce9b9669` | r4, attente légitime, 12 mois, aucune allocation |
| Retrait impossible corrigé | `1f7d3a73d5924a09ba73925655dce389` | r5, terminé ; certificat infeasible, aucun portefeuille |
| Retrait impossible avant correction de routage | `5ea414c5e4aa487f95045ae3f3d2010d` | r5, attente conservée comme contre-exemple |

Les exports successifs sont dans `docs/defense/proofs/demo/`.
L’essai de sources contradictoires `1324588dabee4c1582bc2763c807e5be`
est dans un état séparé, `runtime/defense_preuves_counterexample/`, et exporté
dans `docs/defense/proofs/preuves_live_counterexample.json`.
Ses deux sources sont fictives ; ne pas les ajouter au corpus de production.

Les derniers changements de code : sources de demande immuables, conservation
des vues d’attente, contrôle des checks, politique historique explicite,
diagnostic budgétaire borné, types numériques sans booléens, conflits
documentaires bloquants, citations sélectionnées, registre des outils,
bundles source et CLI de recalcul. Les questions sont regroupées par champ
en conservant les formulations ; les observations A1 sont datées avant A2.

```bash
.venv/bin/python scripts/launch.py
.venv/bin/python scripts/replay_calculation.py 4089e4b0d70f40b6b20d832fa261e1dc
```

Le recalcul ne fait aucune inférence. Le script `run_critical_demo.py --live`
réutilise les IDs déjà enregistrés ; pour une expérience volontairement
nouvelle, fournir un autre `--output`. Il utilise alors le compte AWS.
Ne pas relancer toutes les suites sans modification ou incertitude nouvelle :
178 tests intégrés ont passé, puis 63 et 101 tests ciblés se recouvrant,
avec contrôles UI et oracles distincts.

Le bundle de code des nouveaux runs est dans les objets immuables.
Un export JSON seul ne suffit pas à une restauration complète. Conserver
`runtime/decision/`, le projet, les données et les captures documentaires.
La [sauvegarde Prompt 5](../../artifacts/AlphaForge_Prompt5_etat_2026-11-15.tar.gz)
et son [contrôle](../defense/proofs/state_backup.json) sauvegardent l’état
local, avec copies SQLite cohérentes ; elles ne remplacent pas le corpus
et les données du projet.

## État historique de la livraison Prompt 4

15 novembre 2026. Le fonctionnement cible du Prompt 3 est validé ; la
construction et les choix techniques réversibles sont autorisés. Ne pas
redemander cette validation. Aucun déploiement cloud n'a été effectué.

## Ouvrir et reprendre un dossier

Double-cliquer `Ouvrir_AlphaForge.command`, ou :

```bash
.venv/bin/python scripts/launch.py
```

L'instance courante est à `http://127.0.0.1:8768`. Vérifier
`runtime/server.json` et `/api/health` pour retrouver le port ; ne pas arrêter
un autre processus occupant 8766/8767. L'ancien parcours reste `/legacy`.

| Dossier | ID | État enregistré |
|---|---|---|
| Robert final | `46715c504cfa4443add54daf90ce9c25` | Terminé, r10 ; 30→40 kCAD, huit appels Bedrock, diagnostic initial et recherche réutilisés |
| Amira finale | `8cddaec5d89642de8f38d0b704658763` | Terminé, r5 ; quatre appels Bedrock, comparaison historique et inspection réelle des données |
| Robert, première vérification UI | `471bf771807a4956b5e19cd731fabf6d` | Terminé, r10 ; première tranche visuelle réelle |
| Amira, premier cas incomplet | `6f6c96167c114d6c9d8dfa194e00bb23` | Attente conservée : conventions initialement insuffisantes |
| Amira, intégration incomplète | `c4721cee82a0455f8ec130205818748a` | Attente conservée : Agent1 ne voyait pas encore l'inventaire local ; défaut corrigé dans le service actuel |

La liste complète est `GET /api/dossiers`. Les anciens échecs ne sont pas
effacés et ne constituent pas la démonstration finale. Les IDs de travail
sont aussi dans `runtime/p4_demo_ids.json`.

Un dossier en erreur se reprend par le bouton **Reprendre** ou
`POST /api/dossiers/{id}/resume`. Une attente de clarification nécessite
une correction explicite, pas un clic de reprise qui inventerait la réponse.
Un dossier terminé n'est pas recalculé à l'ouverture.

Si la session AWS a expiré : `aws sso login --profile alphaforge`, puis
reprendre. Les données, dossiers et résultats déjà enregistrés restent
consultables hors connexion. Ne pas configurer un fournisseur de secours.

## État matériel à conserver

- `runtime/decision/dossiers.sqlite3` : dossiers, versions, événements,
  tâches, tentatives et retours de commits.
- `runtime/decision/checkpoints.sqlite3` : checkpoints LangGraph.
- `runtime/decision/objects/` : contenus JSON immuables adressés par hash,
  y compris entrées d'opérations et résultats.
- `runtime/decision/research/` : captures réseau originales.
- Code, `requirements.txt`, `data/`, `docs/recherche/` et documentation de
  conception/implémentation : outils, données et captures locales requises.

SQLite peut utiliser ses fichiers `-wal` et `-shm` pendant l'exécution.
**Ne pas copier uniquement le fichier `.sqlite3` d'un serveur actif.**
Pour une sauvegarde manuelle simple : attendre les runs, arrêter proprement
la seule instance du projet, puis copier l'ensemble de `runtime/decision/`.
Une sauvegarde via l'API SQLite est également possible.

Une [archive locale de l'état](../../artifacts/AlphaForge_Prompt4_etat_2026-11-15.tar.gz)
a été créée après arrêt propre, avec sauvegarde SQLite et vérification des
objets. La [preuve de restauration](proofs/state_backup.json) conserve
l'empreinte de l'archive, les contrôles d'intégrité et les dossiers relus dans
une copie temporaire. **Cette archive contient l'état, pas l'intégralité du
code et des 419 Mio de corpus documentaire** : conserver le répertoire du
projet avec elle. Restaurer dans une copie, jamais par-dessus un historique
plus récent sans examen.

## Vérification achevée

- 132 tests Python passés, dont 43 financiers et 8 sur inspection/provenance ;
  [sortie de suite](proofs/verification.json). Aucun modèle réel dans ces tests.
- Trois passages complets AWS finaux : Robert30, Robert40 et Amira ; douze
  reçus Bedrock dans [final_demo/summary.json](proofs/final_demo/summary.json).
- UI réelle, export, perte réseau, ancienne réponse reçue tardivement,
  bureau/mobile ; [experience.md](experience.md).
- Revue indépendante du noyau et du service, défauts reproduits/corrigés,
  perte simulée après commit avant checkpoint et opération locale concurrente.
- Schéma implémenté dans `architecture.svg` et `architecture.mmd`.

Les treize avertissements de la suite concernent une dépréciation Python
d'une dépendance LangSmith. La télémétrie de ce service est explicitement
désactivée et testée. Aucun changement de route n'a été effectué.

## Repères de code

| Domaine | Fichiers |
|---|---|
| Contrats, transactions | `decision/models.py`, `store.py` |
| Quatre agents et intégration | `decision/service.py`, `api.py`, `main.py` |
| Orchestration | `decision/workflow.py` |
| Recherche et données admissibles | `decision/research.py`, `inspection.py` |
| Calcul | `decision/finance.py`, moteurs historiques existants |
| Interface | `static/workbench.html`, `.css`, `.js` |
| Reproduction | `scripts/launch.py`, `run_decision_demo.py`, `qualify_decision_runtime.py` |

Chemins de code relatifs à `alphaforge_app/`. LangGraph 1.2.22 et
langgraph-checkpoint-sqlite 3.1.3 sont installés. Strands n'a pas été installé.
Les quatre sessions de construction ont été contrôlées via leurs métadonnées :
fournisseur `amazon-bedrock-runtime`. Le produit vérifie STS pour le compte
`471112821226`, profil `alphaforge`, entrée `us-east-1`, modèle
`global.openai.gpt-6-astra`.

## Suite du travail

La tranche exécutable demandée est intégrée. Les extensions documentées sont
dans [README.md](README.md#ce-qui-reste-partiel-ou-prévu) et
[JOURNAL_CANDIDATS.md](JOURNAL_CANDIDATS.md) : qualification d'un instrument réel,
IIS général, méthodes de portefeuille supplémentaires, preuves ESG et évaluation
utilisateur. Ne pas transformer ces pistes en capacités annoncées.

Les réalisations et documents antérieurs sont conservés, y compris de nombreux
fichiers non suivis par Git. Ne pas nettoyer le répertoire ou réinitialiser
l'historique pour simplifier une reprise.
