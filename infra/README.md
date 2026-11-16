# Infrastructure AWS AlphaForge

Le script existant déploie FastAPI sur Lambda avec Mangum, les données et dossiers dans S3 privé,
et l’interface sur Amplify. Les modèles du produit sont Nova 2 Lite et Claude Sonnet 5 via Bedrock.
L’Analyste et le Gardien restent du code Python ; AgentCore n’est pas utilisé.

Voir [le guide de déploiement](../docs/deploiement.md),
[le plan vérifié](../docs/fusion/preuves/tranche3/plan-deploiement.json) et
[l’état réel des ressources](../docs/fusion/preuves/tranche3/RESSOURCES.md).

```sh
export AWS_PROFILE=alphaforge
export AWS_REGION=us-east-1
python infra/deployer.py --plan
python infra/creer_guardrail.py --verifier
python infra/deployer.py --seulement-construire
# Après autorisation du porteur et affichage du plan :
python infra/deployer.py --journal infra/build/tentative.json
```

`--plan` est en lecture seule. Le déploiement borne la concurrence Lambda à 2 avant de publier l’URL,
restreint Bedrock aux ARN retournés pour les deux profils, et fixe le CORS à l’origine exacte d’Amplify.
L’URL reste publique : le CORS ne bloque pas les clients HTTP directs.
Un échec arrête la tentative et lance le nettoyage des seules créations journalisées ; aucun changement
de service n’est tenté après un refus AWS. Conserver le journal pour constater toute suppression échouée.

Le Guardrail se crée par `creer_guardrail.py --journal <nouveau-fichier.json>` ; reporter son ID et sa version
dans `ALPHAFORGE_GUARDRAIL_ID` et `ALPHAFORGE_GUARDRAIL_VERSION` avant le plan et le déploiement principal.
Les variables sont transmises à Lambda, avec une permission limitée à l’ARN du Guardrail.

Le profil local par défaut est `alphaforge` ; une valeur explicite de `AWS_PROFILE` est respectée.
Les identifiants temporaires s’obtiennent auprès de Workshop Studio. Ne jamais les écrire dans Git.
Les commandes de suppression de la tentative réelle sont dans `RESSOURCES.md`.
