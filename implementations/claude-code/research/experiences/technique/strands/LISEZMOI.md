# Expérience technique — Strands Agents pour la boucle d'un rôle

Petite expérience du 15 novembre 2026 pour départager les options d'architecture (cadre de conception, section 7). Ce n'est pas le produit. Rien n'est installé dans le projet : chaque essai tourne dans un environnement jetable de `uv`.

## Cadre des essais

- Bibliothèque : `strands-agents` 1.65.0, licence Apache-2.0, Python 3.13.0.
- Inférence : Amazon Bedrock seulement, profil « alphaforge », région us-east-1, modèle `global.anthropic.claude-haiku-5-5`.
- Budget : vingt appels de modèle au plus. Dix-neuf ont été faits. Le journal `sorties/appels_bedrock.jsonl` les liste tous (identifiant de requête AWS, jetons, raison d'arrêt, durée).
- Plafond dur : `commun.py` refuse un appel dès que ce journal compte vingt débuts d'appel. Pour relancer une série complète, il faut d'abord renommer ce journal (décision de l'équipe : chaque relance consomme des appels).
- Télémétrie : Strands n'exporte rien par défaut (voir essai 9). Par précaution, `commun.py` pose `OTEL_SDK_DISABLED=true` et retire les variables `OTEL_EXPORTER_OTLP_*` et `LANGFUSE_BASE_URL`. Chaque essai imprime les noms d'hôtes résolus par le processus : seul `bedrock-runtime.us-east-1.amazonaws.com` apparaît.
- Toutes les valeurs renvoyées par les outils sont fictives et le disent.

## Relancer un essai

Depuis la racine du dépôt :

```
uv run --with strands-agents python research/experiences/technique/strands/essai1_installation.py
uv run --with strands-agents python research/experiences/technique/strands/essai2_agent_outil.py
uv run --with strands-agents python research/experiences/technique/strands/essai3_sortie_structuree.py            # ou : valide | invalide | tronquee
uv run --with strands-agents python research/experiences/technique/strands/essai4_outils_par_role.py
uv run --with strands-agents python research/experiences/technique/strands/essai5_limite_de_tours.py
uv run --with strands-agents python research/experiences/technique/strands/essai6_question_a_la_personne.py
uv run --with strands-agents python research/experiences/technique/strands/essai7_session_deux_processus.py a     # puis la même commande avec b
uv run --with strands-agents python research/experiences/technique/strands/essai8_graphe.py
uv run --with strands-agents python research/experiences/technique/strands/essai8b_reprise_graphe.py a            # puis la même commande avec b
uv run --with strands-agents python research/experiences/technique/strands/essai9_traces.py
```

| Essai | Appels de modèle | Ce qu'il montre | Sortie conservée |
|---|---|---|---|
| 1 | 0 | Version, licence, dépendances tirées | `sorties/essai1.txt` |
| 2 | 2 | Agent, outil Python, identifiant de requête AWS et jetons par appel | `sorties/essai2.txt` |
| 3 | 3 | Sortie Pydantic valide, invalide, tronquée | `sorties/essai3.txt` |
| 4 | 2 | Outils disjoints par rôle, crochet de refus journalisé | `sorties/essai4.txt`, `sorties/essai4_refus.jsonl` |
| 5 | 2 | Limite de tours | `sorties/essai5.txt` |
| 6 | 2 | Question à la personne, reprise dans le même processus | `sorties/essai6.txt` |
| 7 | 2 | Session sur fichiers, reprise dans un nouveau processus | `sorties/essai7a.txt`, `sorties/essai7b.txt`, `sorties/sessions/` |
| 8 | 3 | Entrée exacte du nœud aval d'un graphe | `sorties/essai8_entree_noeud_aval.json`, `sorties/essai8.txt`, `sorties/essai8_premier_passage_exception.txt` |
| 8 bis | 2 | Reprise d'un graphe après un processus tué | `sorties/essai8b_a.txt`, `sorties/essai8b_b.txt`, `sorties/essai8b_entree_noeud_aval.json`, `sorties/sessions_graphe/` |
| 9 | 1 | Ce que Strands trace, et vers où | `sorties/essai9.txt`, `sorties/essai9_segments.json` |

## Réserves sur ces sorties

- Les essais 4, 5 et 6 ont tourné en même temps. Les compteurs « appels de modèle jusqu'ici » imprimés dans `sorties/essai6.txt` comptent donc aussi les appels des deux autres. Le journal par essai fait foi : deux appels pour l'essai 6.
- L'essai 8 a été lancé deux fois, et les deux passages se sont arrêtés sur une troncature (plafond de 300 jetons trop bas). Le second a quand même journalisé l'entrée du nœud aval. Le script corrigé (plafonds à 900) n'a pas été relancé. Le passage complet d'un graphe est celui de l'essai 8 bis.
- Tous les appels ont été faits sur le modèle Haiku. Le modèle Sonnet n'a pas été essayé.
- Chaque conduite a été observée une seule fois.

## Ce qui a été lu sans être testé

Le code installé a été lu pour : la construction de l'entrée d'un nœud de graphe, les limites, la reprise de session d'un graphe, la configuration de la télémétrie, la stratégie de réessai du modèle (six tentatives par défaut sur limitation de débit) et le traitement d'une exception levée par un outil (renvoyée au modèle comme résultat en erreur). Ces deux derniers points n'ont pas été testés.
