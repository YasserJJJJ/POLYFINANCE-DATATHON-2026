# Architecture réelle — AlphaForge local

## Parcours

```text
Navigateur sur le Mac
  → FastAPI local, 127.0.0.1
    → validation du profil et des hypothèses
    → moteur déterministe → données locales figées → comparaison CAD
    → sur demande : agent Bedrock
      → STS, contrôle du compte atelier
      → Converse, sélection d’outils
      → compare_scenario / read_evidence / inspect_profile
      → sortie structurée, observations et références contrôlées
    → rapport JSON local → interface, courbes et téléchargement
```

Le navigateur ne reçoit aucune clé AWS. Il ne contacte pas de fournisseur
d’inférence. Il n’utilise ni CDN, ni bibliothèque de graphiques distante, ni
police téléchargée. Le serveur n’a pas d’endpoint de transaction financière.

## Modules

| Module | Responsabilité |
|---|---|
| `datasets.py` | Lecture CSV, cohérence des unités, dates, doublons et empreintes |
| `analytics.py` | Valorisation, comparaison, drawdown, volatilité et épisodes |
| `personas.py` | Éléments du cas et hypothèses de démonstration explicites |
| `evidence.py` | Corpus documentaire qualifié et identifiants de références |
| `bedrock.py` | Identité, signature AWS, Converse, schémas et erreurs expurgées |
| `orchestrator.py` | Boucle d’outils bornée et restitution ancrée aux résultats |
| `main.py` | Validation API, persistance, sources et interface |
| `static/` | Interface française, graphiques SVG, comparaison et preuves |

## Routes

| Route | Contrat |
|---|---|
| `GET /api/bootstrap` | Actifs, personas, hypothèses et sources |
| `POST /api/analyze` | Demande, persona, portefeuille, réglages, `use_ai` |
| `GET /api/report/{id}` | Rapport exact de l’exécution locale |
| `GET /api/source/{id}` | Sources locales autorisées : starter, method, case |
| `GET /api/health` | Identité locale du service, aucun appel AWS |
| `GET /api/docs` | Contrat OpenAPI consultable |

Les poids entrants sont des fractions et doivent totaliser un. Le contrôle
`focus_weight` est un pourcentage de zéro à cent. Les paramètres absents sont
complétés depuis le persona choisi, puis seules les valeurs explicitement
saisies les remplacent. Les devises d’affichage sont limitées à CAD.

Le rapport inclut l’instant UTC, les paramètres effectivement calculés, les
séries complètes, les métriques, les hypothèses de calendrier, les empreintes
des CSV, les limites et la trace des appels. La trace rapporte des actions
observables et leurs résultats ; elle n’est pas une transcription du
raisonnement privé du modèle.

## Frontière entre modèle et calcul

L’agent peut appeler trois outils, dans un ordre choisi, et changer l’exposition
si la demande l’explicite. Les autres avoirs ne sont jamais choisis par une
optimisation cachée. Un symbole inconnu renvoie une erreur ; aucun prix n’est
inventé. Les calculs et les unités sont exclusivement produits par Python.

Le contrat exige au moins un calcul et une lecture de preuves réussis avant
la restitution. Celle-ci utilise un nouvel appel, sans outils disponibles,
alimenté par le profil, les calculs et les fiches effectivement lus. L’historique
des appels d’outils reste dans le rapport. Cette séparation évite qu’une demande
d’outil tardive remplace la conclusion attendue.

Le modèle sélectionne trois à cinq identifiants uniques d’observations exactes,
plutôt que de recopier les chiffres. Des identifiants inexistants invalident
la conclusion. Tous les champs de prose générés filtrent les chiffres ;
ce garde-fou ne constitue pas une preuve générale de véracité sémantique.

Le corpus est un ensemble de fiches qualifiées consultables, pas une recherche
web autonome en direct. Une référence lue par le système après la génération
est signalée comme vérification des références, sans prétendre que le modèle
avait lui-même parcouru la publication complète.

La boucle accepte au plus quatre tours et six outils par réponse. Les délais
du SDK et les tentatives sont bornés. Une erreur récupérée demeure visible avec
un statut partiel. Si la conclusion échoue, l’état de calcul initial est
restauré intégralement ; les tentatives et le diagnostic restent dans la trace.

## Stockage, accès et reprise

Les rapports sont écrits atomiquement sous un identifiant aléatoire validé.
Le serveur accepte uniquement les hôtes locaux et refuse les POST provenant
d’une autre origine de navigateur. Cette configuration est destinée à un seul
utilisateur sur son Mac ; une exposition réseau nécessiterait une architecture
d’accès dédiée.

Les fichiers du starter sont copiés localement sans transformation. Le calcul
reste reproductible sans compte AWS. Après expiration de l’atelier, les
rapports enregistrés sont des preuves d’exécutions passées ; ils ne doivent pas
être présentés comme de nouvelles analyses.

La route des agents de développement et celle du produit sont documentées
dans `aws-runtime.md` et le journal de reprise. Aucun service d’hébergement
AWS, Sites ou dépôt distant n’a été créé pour cette livraison locale.
