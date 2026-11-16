# Preuves de la tranche 3

Résultat : publication AWS vérifiée ; 268 tests réussis. Les trois décisions locales Bedrock sont
identiques aux décisions hors ligne pour les mêmes entrées. L’intégration est sur `fusion/aws`, issue de `fusion/t1`.

- [Ressources réelles, URL et suppressions](RESSOURCES.md).
- [Appels, identifiants, jetons et latences par agent](APPELS.md).
- [Bilan HTTP public et archive S3](public/bilan.json) ; [réception NDJSON horodatée](public/reception-ndjson.json).
- [Résultats locaux](local/bilan.json) et les trois dossiers `local/*-bedrock.json`.
- [Guardrail normal corrigé](guardrail-normal-corrige/bilan.json) et [conseil bloqué avec gabarit](guardrail-conseil-corrige.json).
- [Tests finaux](tests-finaux.txt), [construction et déploiement](deploiement.txt).
- [Plan initial sans création](plan-deploiement.json), [plan avec ARN Guardrail](plan-deploiement-avec-guardrail.json), [simulation IAM](simulation-iam.json).
- [Provenance du transfert depuis A](provenance-appels.json), [périmètre intact](controle-perimetre.json), [route d’exécution](ROUTE-EXECUTION.json).

Les fichiers sans suffixe `corrige` relatifs au Guardrail décrivent les défauts avant réparation.
`verification-locale.txt` conserve l’erreur du premier outil de capture : il cherchait la grille sous `grille`
alors que le contrat utilise `bascule`. Le dossier Robert avait déjà été sauvegardé ; il a été réutilisé sans
nouvelle inférence. Sa durée HTTP totale n’a pas été capturée : seule la somme réelle des durées des agents
(8 978 ms) est disponible. Les autres durées HTTP sont conservées.

`construction-avant-deploiement.txt` décrit l’absence de pip dans le venv de tests ;
`construction-avant-deploiement-reprise.txt` montre le conflit dateutil corrigé ensuite.
`verification-publication.txt` décrit un magasin de certificats local incomplet dans ce venv.
La reprise utilise le même Python système que le déploiement, avec vérification TLS active.
Aucune de ces erreurs d’environnement n’a été masquée dans une réussite.

## Commandes de cette exécution

Depuis `/Users/vpro/Documents/ChatGPT/POLYFINANCE-fusion-aws` :

```sh
# Tests, depuis backend/ :
ALPHAFORGE_LLM=off ALPHAFORGE_DATA_BUCKET='' /Users/vpro/Documents/ChatGPT/POLYFINANCE-DATATHON-2026/backend/.venv/bin/python -m pytest -q --tb=short

# Interpréteur de déploiement avec pip et certificats système, SDK existant lu dans le venv :
export PYTHONPATH=/Users/vpro/Documents/ChatGPT/POLYFINANCE-DATATHON-2026/backend/.venv/lib/python3.13/site-packages
export AWS_PROFILE=alphaforge
export AWS_REGION=us-east-1
export PIP_NO_CACHE_DIR=1
export npm_config_cache=/Users/vpro/Documents/ChatGPT/POLYFINANCE-fusion-aws/infra/build/npm-cache
python3 infra/deployer.py --plan
python3 infra/creer_guardrail.py --verifier
python3 infra/deployer.py --seulement-construire
# Commande de création déjà exécutée : ne pas rejouer avec le même journal.
python3 infra/creer_guardrail.py --journal docs/fusion/preuves/tranche3/creation-guardrail.json
export ALPHAFORGE_GUARDRAIL_ID=xj89p36uyw64
export ALPHAFORGE_GUARDRAIL_VERSION=1
python3 infra/deployer.py --plan
python3 infra/deployer.py --journal docs/fusion/preuves/tranche3/creation-deploiement.json
python3 docs/fusion/preuves/tranche3/verifier-publication.py
```

Les créations Guardrail et les plans ont réellement employé l’interpréteur du venv ; le Python système
ci-dessus sert au paquet pip, au déploiement et à la réception publique. Les mêmes sources sont utilisées.
Aucun paquet n’a été installé dans le venv du dépôt principal ; les sorties de construction et caches npm
restent dans cet arbre de travail, ignorés par Git.

```sh
# API locale initiale : sans Guardrail ni archivage S3, port 18763.
env -u ALPHAFORGE_GUARDRAIL_ID -u ALPHAFORGE_GUARDRAIL_VERSION AWS_PROFILE=alphaforge AWS_REGION=us-east-1 ALPHAFORGE_LLM=bedrock ALPHAFORGE_DATA_BUCKET='' python -m uvicorn api:app --host 127.0.0.1 --port 18763
python infra/verifier_tranche3.py --url http://127.0.0.1:18763 --sortie docs/fusion/preuves/tranche3/local --reprendre
# Puis API avec Guardrail, port 18764, même commande et variables ID/version ci-dessus.
python infra/verifier_tranche3.py --url http://127.0.0.1:18764 --sortie docs/fusion/preuves/tranche3/guardrail-normal-corrige --cas robert
ALPHAFORGE_LLM=bedrock python infra/verifier_guardrail.py --dossier docs/fusion/preuves/tranche3/local/robert-hors-ligne.json --sortie docs/fusion/preuves/tranche3/guardrail-conseil-corrige.json
```

Ces dernières vérifications utilisent l’interpréteur du venv de tests ; les serveurs sont lancés depuis
`backend/` et les outils de capture depuis la racine. Les ports d’autres processus n’ont pas été touchés.
