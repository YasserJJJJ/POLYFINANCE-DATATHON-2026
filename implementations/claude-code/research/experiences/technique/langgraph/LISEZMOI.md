# Expérience technique — LangGraph comme moteur d'enchaînement et de persistance

Petite expérience du 15 novembre 2026 pour départager les options d'architecture (cadre de conception, section 7). Ce n'est pas le produit. Rien n'est installé dans le projet : les paquets vivent dans un environnement éphémère de `uv`.

Versions éprouvées : langgraph 1.2.22, langgraph-checkpoint 4.3.2, langgraph-checkpoint-sqlite 3.1.3, langgraph-prebuilt 1.1.2, langchain-core 1.8.1, langchain-aws 1.9.3, langsmith 0.14.17, Python 3.13.0.

## Relancer un essai

Depuis la racine du dépôt (`Datathon-2026/`) :

```
uv run --frozen --with langgraph --with langchain-aws --with langgraph-checkpoint-sqlite \
  python research/experiences/technique/langgraph/<fichier>.py
```

Les essais 2, 9 et 10 appellent Amazon Bedrock (profil `alphaforge`, région `us-east-1`, modèle `global.anthropic.claude-haiku-5-5`). Les autres n'ont besoin d'aucun réseau. Chaque essai repart de zéro : il efface ses propres fichiers dans `sorties/`.

| Essai | Fichier | Appels de modèle | Ce qu'il mesure |
|---|---|---|---|
| 1 | `essai01_installation.py` | 0 | Versions, licences, dépendances tirées ; marque `+` ce qui est absent de l'environnement du projet. |
| 2 | `essai02_bedrock.py` | 2 | Un appel simple, puis une sortie à structure imposée (objet Pydantic). |
| 3 | `essai03_graphe.py` | 0 | Graphe de quatre nœuds, état typé, point de reprise SQLite ; ce que le moteur contrôle sur les types. |
| 4 | `essai04_interruption.py` | 0 | Question à la personne, arrêt du processus, reprise dans un nouveau processus ; panne en plein nœud. Trois processus par scénario, joué en durabilité par défaut puis `sync`. Une phase seule : ajouter `depart`, `reponse` ou `reprise`, puis `defaut` ou `sync`. |
| 5 | `essai05_historique.py` | 0 | Historique des états ; nature des identifiants ; réécriture d'un point existant. |
| 6 | `essai06_correction.py` | 0 | Correction d'une valeur amont puis relance : compteurs d'exécution par nœud, en chaîne et en losange, sans puis avec le cache de nœuds ; relecture du cache depuis un autre processus ; cache et changement de code. |
| 7 | `essai07_bifurcation.py` | 0 | Variante ouverte depuis un point antérieur ; intégrité de la ligne d'origine ; « dernier état » du fil. |
| 8 | `essai08_concurrence.py` | 0 | Deux écritures qui nomment la même tête ; deux processus qui écrivent ou lancent le graphe au même instant. |
| 9 | `essai09_evenements.py [budget]` | 1 | Événements reçus par un appelant (modes `updates`, `values`, `custom`, `messages`, `tasks`, `checkpoints`). Le budget de jetons de l'agent 3 vaut 400 par défaut ; avec 60, le modèle épuise son budget en réflexion et ne rend aucun texte. |
| 10 | `essai10_telemetrie.py` | 1 | Noms résolus et connexions sortantes, sans aucun réglage de traçage. |
| 11 | `essai11_erreurs_et_outils.py` | 0 | Complément : erreurs d'outils, outil demandé hors du rôle, relance d'un nœud. |

`commun.py` contient l'état typé, les quatre nœuds (du code déterministe, sans modèle), les compteurs d'exécution et la route d'inférence.

## Lire les sorties

- `sorties/essaiNN_sortie*.txt` : la sortie de la dernière exécution de chaque essai (l'essai 1 n'écrit que `essai01_paquets.json`).
- `sorties/executions_*.log` : une ligne par exécution réelle d'un nœud (nom, processus, instant). Ce sont les compteurs.
- `sorties/appels_bedrock.log` : une ligne par requête HTTP réellement envoyée à Bedrock, tous essais confondus. Le fichier se cumule d'une exécution à l'autre.
- `sorties/*.sqlite` : les points de reprise et les caches, lisibles avec `sqlite3`.
- `sorties/essai09_evenements_budget*.jsonl` : la suite complète des événements.

## Télémétrie

- Mesuré (essai 10) : sans aucun réglage, l'import des bibliothèques et l'exécution d'un graphe local ne résolvent aucun nom et n'ouvrent aucune connexion ; un appel de modèle ne contacte que `bedrock-runtime.us-east-1.amazonaws.com`. L'espion ne voit que les connexions faites par le module `socket` de Python.
- `langsmith` est une dépendance obligatoire de `langchain-core`. Il n'envoie des traces à un tiers (LangSmith) que si `LANGSMITH_TRACING` ou `LANGCHAIN_TRACING_V2` l'activent. Aucune de ces variables n'existe dans notre environnement. `commun.py` les force quand même à `false`.
- Lu dans le code : `langchain-aws` modifie `boto3` à l'import pour ajouter `x-client-framework:langchain-aws` à l'en-tête `User-Agent` de tous les clients `boto3` du processus. Le destinataire est AWS, pas un tiers.

## Limites de l'expérience

- Les nœuds des essais 3 à 8 sont du code sans modèle : on mesure le moteur, pas la qualité d'un agent.
- Seul le point de reprise SQLite a été éprouvé (ni PostgreSQL, ni DynamoDB, ni S3).
- Aucune ressource AWS n'a été créée. Aucun fichier du projet n'a été modifié.
