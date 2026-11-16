# Déploiement AWS — fusion, tranche 3

Le mandat du porteur autorise la création de Lambda, S3, Amplify, du rôle IAM et du Guardrail
sur le compte `471112821226`, en `us-east-1`, après durcissement et affichage du plan.
Il remplace pour cette tranche la consigne historique de déployer en réunion. Les autorisations,
mesures et résultats sont conservés dans [les preuves](fusion/preuves/tranche3/) ;
l’état constaté et les commandes de suppression sont dans [RESSOURCES.md](fusion/preuves/tranche3/RESSOURCES.md).

## Préparer et afficher le plan

Depuis la racine du dépôt, avec Python, pip, boto3 et npm disponibles :

```sh
export AWS_PROFILE=alphaforge
export AWS_REGION=us-east-1
aws sts get-caller-identity
python infra/deployer.py --plan
python infra/creer_guardrail.py --verifier
python infra/deployer.py --seulement-construire
```

Les scripts respectent `AWS_PROFILE` et les identifiants injectés dans l’environnement.
Le défaut local est `alphaforge`. Ils refusent une création sur un autre compte ou dans une autre région.
Aucun fichier d’identifiants n’est à ouvrir ou à commiter.
`--plan` interroge seulement STS, les profils Bedrock et les groupes de journaux : pas de création,
pas d’inférence, pas de construction. La simulation IAM de la tranche 3 a autorisé les 33 actions
vérifiées ; elle ne garantit pas l’absence de restrictions supplémentaires du compte.
Aucune ressource de test n’est créée pour sonder les droits.

## Architecture et limites

- S3 privé : données dans `data/`, paquet dans `code/`, dossiers complets dans `dossiers/`.
- Lambda Python 3.12, Mangum, 1 536 Mo, délai de 90 secondes. Concurrence réservée : **2**,
  posée avant l’exposition de la Function URL ; `--concurrence` accepte 1 à 5.
- Function URL publique : les appels directs restent possibles. Le CORS limite les navigateurs
  à l’origine exacte de l’interface ; il ne constitue pas une authentification ni un quota total de dépenses.
- Rôle `alphaforge-lambda` : lecture de `data/`, écriture de `dossiers/`, journaux CloudWatch,
  invocation des deux profils Bedrock et de leurs destinations résolues par AWS, sans joker Bedrock.
- Amplify publie uniquement les fichiers de l’interface. Son domaine est obtenu avant de définir
  `ALPHAFORGE_ORIGINES_INTERFACE` dans Lambda. FastAPI est l’unique source des en-têtes CORS.
- Le Guardrail contrôle le Rédacteur, qui fournit une source d’ancrage. La question reste sous 1 000 caractères ; le dossier et le contenu à contrôler sont des blocs distincts. Le contrôle d’ancrage en code et le repli en phrases déterministes restent actifs.

`requirements-lambda.txt` inclut Mangum et borne la dépendance transitive `python-dateutil` à `<3`,
compatible avec botocore fourni par le runtime. Aucun module d’analyse supplémentaire n’est intégré dans cette branche.

## Exécuter une tentative autorisée

```sh
python infra/creer_guardrail.py --journal infra/build/guardrail-tentative.json
# Reporter l’identifiant et la version réellement affichés, sans inventer de valeur.
export ALPHAFORGE_GUARDRAIL_ID=<identifiant>
export ALPHAFORGE_GUARDRAIL_VERSION=<version>
python infra/deployer.py --plan
python infra/deployer.py --journal infra/build/deploiement-tentative.json
```

Choisir un nouveau nom de journal à chaque tentative. La construction locale précède les créations.
L’application et la branche Amplify donnent l’origine du CORS ; suivent S3, IAM, Lambda, santé publique,
construction de l’interface avec la vraie URL, puis publication Amplify.
Le script attend le résultat du déploiement avant d’annoncer sa réussite.

En cas d’échec, le script s’arrête et nettoie seulement les ressources inscrites comme créées dans son journal.
Il ne supprime aucune ressource préexistante. Le script Guardrail possède son propre journal et supprime sa
nouvelle ressource si la publication de version échoue. Si le déploiement principal échoue après une création
séparée du Guardrail, supprimer aussi ce Guardrail nouvellement créé, conformément à son journal.
Un refus AWS n’autorise ni un changement de service ni une extension de permissions.
Le choix `--frontend s3` reste une option explicite du script d’origine ; ce n’est pas un recours à un refus Amplify.

## Vérifier et conserver les preuves

`GET /api/sante` indique la région et les identifiants réellement configurés, sans numéro de compte.
Son champ `llm` confirme l’accès STS ; la preuve d’inférence vient des identifiants Converse des dossiers.
`ALPHAFORGE_REESSAI_SECONDES` règle la reprise après erreur d’accès (15 s par défaut, borné de 1 à 300 s).
Un refus propre à un modèle ne coupe pas l’autre.

```sh
# API locale lancée séparément avec ALPHAFORGE_LLM=bedrock et sans bucket de stockage :
python infra/verifier_tranche3.py --url http://127.0.0.1:8000 --sortie infra/build/preuves-locales
```

Vérifier aussi une analyse publique, sa copie exacte dans S3 et les heures de réception des lignes NDJSON.
Ne pas conclure que le flux est progressif à partir du seul type MIME. Les observations de cette tranche
sont consignées dans les preuves et doivent être reprises par la tranche 4.

Le compte de l’événement doit être détruit le **16 novembre à 13 h 59** selon les documents des équipes.
Les ressources hébergées et les archives S3 disparaîtront ; le code, les dossiers et les captures enregistrés
sur la branche Git resteront disponibles. Les ressources Workshop étrangères au projet ne sont jamais touchées.
