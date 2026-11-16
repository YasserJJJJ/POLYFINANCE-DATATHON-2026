# Agent Bedrock et workflow fixe : comparaison des dossiers enregistrés

Fichier produit par `scripts/comparer_agent_workflow.py` à partir de `runs/*/dossier.json` ; ne pas le modifier à la main.
Critère de réfutation (a) de D1 : « sur des demandes variées, l'agent choisit les mêmes outils que le workflow fixe ».

## Dossiers de l'agent

| Dossier | Demande | Appels Bedrock | Jetons entrée | Jetons sortie | Corrections demandées | Affirmations | Valeurs reliées | Contrôle |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `amira-agent` | Je veux un portefeuille de croissance axé sur l'IA et la crypto, sans tout miser sur la technologie. | 5 | 48997 | 8489 | 1 | 17 | 59 | conforme |
| `amira-libre-bitcoin-or` | Je n'ai pas encore de portefeuille. Explique-moi simplement le risque du Bitcoin comparé à celui de l'or et d'un indice d'actions américaines. | 4 | 33773 | 7102 | 1 | 18 | 50 | conforme |
| `mateo-libre-esg` | Je veux des actions américaines en évitant les entreprises liées à des controverses environnementales importantes. Le fonds ESGV me convient-il mieux que SPY ? | 4 | 32618 | 6480 | 1 | 16 | 50 | conforme |
| `robert-agent` | J'aimerais consacrer une partie de mon portefeuille à Tesla ; on en parle partout. | 5 | 57162 | 10098 | 1 | 18 | 68 | conforme |
| `robert-libre-gamestop` | Un collègue me parle de GameStop (GME). Est-ce que je devrais en mettre un peu dans mon portefeuille ? | 3 | 19559 | 2255 | 0 | 12 | 24 | conforme |
| `robert-libre-or` | Mon portefeuille est fait de 60 % d'obligations canadiennes (XBB.TO) et de 40 % d'actions canadiennes (XIU.TO). Est-ce utile d'y ajouter un peu d'or pour mieux traverser une baisse ? | 5 | 46103 | 7394 | 1 | 16 | 56 | conforme |

## Scénarios de démonstration : outils de l'agent face au workflow fixe

| Scénario | Appels communs | Ajoutés par l'agent | Absents chez l'agent |
|---|---|---|---|
| `robert-agent` / `robert-tsla` | asset_metrics(TSLA), data_manifest, portfolio_metrics ×5, profile_facts, share_sweep(TSLA) | asset_metrics(QQQ), correlation(TSLA, SPY) | — |
| `amira-agent` / `amira-croissance` | data_manifest, diversification_sweep, portfolio_metrics ×2, profile_facts | — | correlation(BTC-USD, ETH-USD) |

## Demandes libres : parcours choisis par l'agent, sans workflow fixe correspondant

| Dossier | Outils appelés |
|---|---|
| `amira-libre-bitcoin-or` | asset_metrics(BTC-USD), asset_metrics(GLD), asset_metrics(SPY), correlation(BTC-USD, SPY), data_manifest, profile_facts |
| `mateo-libre-esg` | asset_metrics(ESGV), asset_metrics(SPY), correlation(ESGV, SPY), data_manifest, profile_facts |
| `robert-libre-gamestop` | asset_metrics(GME) [erreur], data_manifest, profile_facts |
| `robert-libre-or` | asset_metrics(GLD), correlation(GLD, XBB.TO), correlation(GLD, XIU.TO), data_manifest, portfolio_metrics ×2, profile_facts, share_sweep(GLD) |

## Lecture

- Scénarios de démonstration : les hypothèses fournies (portefeuille, parts étudiées, seuil, panier) dictent presque le parcours ; l'agent y suit le workflow fixe à quelques appels près. Sur ces demandes, le workflow fixe suffit et ne coûte aucun jeton.
- Demandes libres : l'agent compose un parcours propre à chaque demande (comparaison d'actifs sans portefeuille, hypothèses posées et déclarées, erreur d'outil rapportée) ; aucun workflow fixe ne les couvre.
- Limite : un dossier par demande, un seul modèle ; la variabilité d'une exécution à l'autre n'est pas mesurée ici.
