# Ressources AWS — tranche 3

Compte `471112821226`, région `us-east-1`. Création autorisée par le prompt reçu.
Le plan en lecture seule et les tests ont précédé les créations. État du script : **deployee**.

- Interface : https://main.d1d3b8g2y5hkdd.amplifyapp.com
- API : https://ldk3ad4p3grqn3ppbcosvznivm0plyck.lambda-url.us-east-1.on.aws/api/sante
- Sources déployées : commit `b385412` ; l'empreinte du paquet distant est comparée au ZIP local dans `public/lambda.json`.

| Service | Nom / identifiant | ARN retourné ou vérifié | Région | État enregistré |
|---|---|---|---|---|
| amplify | `d1d3b8g2y5hkdd` | `arn:aws:amplify:us-east-1:471112821226:apps/d1d3b8g2y5hkdd` | us-east-1 | cree |
| amplify_branch | `d1d3b8g2y5hkdd/main` | `arn:aws:amplify:us-east-1:471112821226:apps/d1d3b8g2y5hkdd/branches/main` | us-east-1 | cree |
| s3 | `alphaforge-471112821226-us-east-1` | `arn:aws:s3:::alphaforge-471112821226-us-east-1` | us-east-1 | cree |
| iam | `alphaforge-lambda` | `arn:aws:iam::471112821226:role/alphaforge-lambda` | us-east-1 | cree |
| lambda | `alphaforge-api` | `arn:aws:lambda:us-east-1:471112821226:function:alphaforge-api` | us-east-1 | cree |
| logs | `/aws/lambda/alphaforge-api` | `arn:aws:logs:us-east-1:471112821226:log-group:/aws/lambda/alphaforge-api:*` | us-east-1 | cree |
| Bedrock Guardrail, version 1 | `alphaforge-garde-fou` / `xj89p36uyw64` | `arn:aws:bedrock:us-east-1:471112821226:guardrail/xj89p36uyw64` | us-east-1 | publie |

La Function URL appartient à la fonction `alphaforge-api` et partage son ARN ; son mode est `NONE`
(publique), `BUFFERED`. La politique inline `alphaforge-acces` appartient au rôle `alphaforge-lambda`
et n’a pas d’ARN autonome. La version publiée `1` appartient au Guardrail et partage son ARN.
La politique managée AWS `AWSLambdaBasicExecutionRole` est seulement attachée : elle n’a pas été créée.
Les flux de journaux sont créés par Lambda dans le groupe ci-dessus et sont supprimés avec lui.
Les noms et ARN ne couvrent aucune ressource Workshop étrangère à cette tentative.

Inventaires vérifiables : [journal principal](creation-deploiement.json),
[journal Guardrail](creation-guardrail.json), [état lu après publication](etat-aws-deploye.json).
Le bucket conserve `data/`, `code/` et `dossiers/` en privé ; aucun bucket web public n’a été créé.
La politique IAM effective est égale au plan, les quatre protections S3 sont actives,
et la concurrence réservée Lambda vaut 2. Le CORS utilise uniquement l’origine Amplify ci-dessus.

## Suppression, si le porteur décide d'arrêter cette publication

Ces commandes sont consignées pour le nettoyage ; elles **n’ont pas été exécutées** après le succès.
Elles suppriment uniquement les ressources créées dans cette tentative. Exécuter dans cet ordre :

```sh
export AWS_PROFILE=alphaforge
export AWS_REGION=us-east-1
aws lambda delete-function-url-config --function-name alphaforge-api
aws lambda delete-function --function-name alphaforge-api
aws amplify delete-branch --app-id d1d3b8g2y5hkdd --branch-name main
aws amplify delete-app --app-id d1d3b8g2y5hkdd
aws s3 rm s3://alphaforge-471112821226-us-east-1/ --recursive
aws s3api delete-bucket --bucket alphaforge-471112821226-us-east-1
aws iam delete-role-policy --role-name alphaforge-lambda --policy-name alphaforge-acces
aws iam detach-role-policy --role-name alphaforge-lambda --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name alphaforge-lambda
aws logs delete-log-group --log-group-name /aws/lambda/alphaforge-api
aws bedrock delete-guardrail --guardrail-identifier xj89p36uyw64 --guardrail-version 1
aws bedrock delete-guardrail --guardrail-identifier xj89p36uyw64
```

L’arrêt de l’API précède le nettoyage S3 pour éviter de nouveaux dossiers pendant la suppression.
Les dossiers sont aussi copiés dans les preuves Git. Selon les documents de l’événement,
le compte doit être détruit le **16 novembre 2026 à 13 h 59** : les URL, le Guardrail,
les données S3 et les journaux AWS ne survivront pas à cette fermeture.
