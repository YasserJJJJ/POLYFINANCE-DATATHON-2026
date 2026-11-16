# R01 — Chemin AWS pour faire tourner l'agent de façon réelle et observable

Recherche déléguée (sous-agent researcher), pages AWS lues le 2026-11-14 (sauf mention). Aucune ressource créée, aucun appel AWS.

## Comparatif

| | (a) Converse + toolConfig | (b) Strands sur Bedrock | (c) AgentCore | (d) Bedrock Agents « Classic » |
|---|---|---|---|---|
| Statut | API Bedrock Runtime ; Converse pris en charge par Sonnet, Haiku et Opus 5.5 (cartes modèles) | SDK Apache 2.0 ([dépôt](https://github.com/strands-agents/sdk-python)) ; version non vérifiée | Runtime, Gateway, Memory, Observability, Code Interpreter ([doc](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)) ; statut GA non vérifié | **Fermé aux nouveaux clients le 30 juillet 2026** ; `CreateAgent` renvoie 403 sans activité Agents dans les 12 derniers mois ([doc](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-classic-maintenance-mode.html)) |
| À écrire | notre boucle `converse` tant que `stopReason == "tool_use"` ; outils exécutés côté client ([tool-use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html)) | agent Python avec outils déclarés | déploiement via CLI `@aws/agentcore` (Node 20.12+, CDK, IAM) | exclu |
| Observabilité | journal d'invocation (désactivé par défaut) vers CloudWatch Logs ou S3 : `requestId`, `modelId`, jetons, `identity.arn` ([doc](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html)) | traces OpenTelemetry | CloudWatch au format OTEL | — |
| Prix | jetons seulement | jetons seulement | Runtime 0,0895 $/vCPU-h, 0,00945 $/Go-h ; Gateway 0,005 $/1 000 appels ([prix](https://aws.amazon.com/bedrock/agentcore/pricing/)) | — |

## Modèles Claude ([cartes modèles](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html), lues)

- Sonnet 5.5 (28 sept. 2026) : profils `us.`, `eu.`, `au.`, `global.anthropic.claude-sonnet-5-5` ; `tool_choice` limité à `auto` et `none`.
- Haiku 5.5 (7 oct. 2026) : profils `us.`, **`ca.`** (destinations ca-central-1 et ca-west-1), `eu.`, `au.`, `jp.`, `global.anthropic.claude-haiku-5-5`.
- Opus 5.5 (22 sept. 2026) : profils `us.`, `eu.`, `au.`, `jp.`, `global.` ; en région seulement eu-west-2.
- us-east-1, us-west-2, ca-central-1 : profils géographiques et global, pas d'inférence en région. Depuis ca-central-1, `us.` route vers les États-Unis.
- Prix par million de jetons des modèles 5.5 : **non vérifié** (facturation via AWS Marketplace).
- Accès activé à la première invocation (permissions `aws-marketplace:Subscribe`…) ; `AccessDeniedException` possible selon le compte.

## Commandes en lecture seule (déduites des pages, non exécutées)

`aws sts get-caller-identity` · `aws bedrock list-foundation-models --by-provider anthropic` · `aws bedrock list-inference-profiles --type-equals SYSTEM_DEFINED` · `aws bedrock get-foundation-model-availability --model-id <id>` (CLI ≥ 2.27.42) · `aws bedrock get-model-invocation-logging-configuration`.

## Recommandation et décision influencée

- **Chemin (a)** : boucle Converse dans notre code. Contrôle total, nécessaire au registre de preuves et au vérificateur ; aucun déploiement. Strands (b) n'apporte que des traces prêtes à l'emploi, que notre registre fournit déjà. AgentCore (c) reste une option de déploiement ultérieure. Classic (d) exclu.
- Modèle configurable ; candidat par défaut `global.anthropic.claude-sonnet-5-5`, variante `ca.anthropic.claude-haiku-5-5` si l'on veut un routage restreint au Canada.
- Preuve d'intégration : afficher dans le dossier le `RequestId` de chaque appel ; journal d'invocation activé (CloudWatch ou S3) ; dossier de preuves écrit dans S3 versionné avec son `VersionId`. **Ces ressources se créent dans le compte du porteur et demandent son accord.**
- S3 versionné : utile si chaque exécution y écrit réellement son dossier. Lambda : risque de décor élevé, écarté pour l'instant.
