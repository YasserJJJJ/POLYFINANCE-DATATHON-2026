# Déploiement AWS : prêt à lancer, à faire ensemble

**Ne pas exécuter seul.** Décision d'équipe (14 nov.) : on déploie **tous les quatre ensemble**, une fois qu'il y a
une version complète du produit, puis on itère jusqu'à l'amélioration finale. Ce document rassemble ce qui a déjà
été vérifié (sans rien créer) pour que, le jour J, le déploiement prenne des minutes, pas des heures.

## 1. Ce qu'on sait déjà sur le compte (vérifié le 15 nov., lecture seule)

- Compte **AWS Workshop Studio**, rôle `WSParticipantRole`, région `us-east-1`.
- Rôles de garde-fou propres à l'événement : `WSReaperRole` (nettoyage automatique des ressources après un
  certain temps — ne pas compter sur une ressource qui dort), `WSLambdaCurtailerRole` (limite de concurrence
  Lambda), `WSRestrictedActionsRole`. Infra `kiro-ide-browser-*` (Lambdas, 1 stack CloudFormation) : **sans
  rapport avec notre projet, ne pas y toucher, ne pas la confondre avec nos ressources.**
- **Rien n'est encore déployé** : 0 bucket S3, 0 app Amplify, 0 API Gateway, 0 Guardrail Bedrock, 0 runtime
  AgentCore, 0 fonction Lambda à nous.
- **126 modèles Bedrock catalogués** dans la région (Anthropic, Amazon Nova, Meta Llama, DeepSeek, Mistral,
  Stability, embeddings Cohere/TwelveLabs…). Ceux qu'on utilise déjà et qui fonctionnent réellement :
  `global.anthropic.claude-sonnet-5` et `global.amazon.nova-2-lite-v1:0` (vérifiés par de vrais appels pendant
  l'audit du 15 nov.).
- **Simulation IAM (`iam.simulate_principal_policy`, zéro ressource créée)** : toutes les actions de création
  nécessaires au plan ci-dessous sont **autorisées** pour `WSParticipantRole` : `s3:CreateBucket`,
  `lambda:CreateFunction`, `lambda:CreateFunctionUrlConfig`, `amplify:CreateApp`, `apigateway:POST`,
  `bedrock-agentcore:CreateAgentRuntime`, `bedrock:CreateGuardrail`, `iam:CreateRole`/`PassRole`/`AttachRolePolicy`,
  `cloudfront:CreateDistribution`, `dynamodb:CreateTable`, `ecr:CreateRepository`, `cloudformation:CreateStack`.
  **Réserve** : cette simulation ne voit pas d'éventuelle politique au niveau Organisation (SCP) ; à confirmer par
  un essai réel (ex. créer un petit bucket de test) au tout début de la session de déploiement, avant d'investir du
  temps dans le reste.

## 2. Convention de nommage (éviter toute collision, on est 4 sur le même compte)

Préfixer **toute** ressource créée par `alphaforge-` (ex. `alphaforge-api`, `alphaforge-frontend-<initiales>` si
plusieurs essais en parallèle). Avant de créer quoi que ce soit, relancer le sondage en lecture seule
(`../audit_tmp/scripts/` n'existe que sur le poste de Yahia — redemander à Claude de relister S3/Lambda/Amplify
si besoin) pour voir si un membre a déjà commencé.

## 3. Plan de déploiement proposé (à valider ensemble, rien n'est figé)

| Composant | Service | Pourquoi ce choix |
|---|---|---|
| API (`backend/api.py`, FastAPI) | **AWS Lambda + Function URL** (adaptateur [Mangum](https://mangum.io/)) | Pas besoin d'API Gateway (Function URL sert du HTTPS + CORS directement) ; déploiement en une commande (`zip` + `aws lambda create-function` ou SAM/CDK minimal) |
| Interface (`frontend/`, build Vite) | **AWS Amplify Hosting** (dépôt connecté ou `amplify deploy` manuel du dossier `dist/`) | Build + HTTPS + CDN en un clic ; alternative plus simple si Amplify pose souci : S3 (site statique) + CloudFront |
| Garde-fou supplémentaire | **Bedrock Guardrails** | Sujet refusé « conseil d'achat financier » + vérification d'ancrage contextuel, **en plus** du contrôle en code existant (`redacteur.verifier`) — jamais à la place |
| Rôle IAM Lambda | Rôle dédié `alphaforge-lambda-role` avec la politique managée `AmazonBedrockFullAccess` (ou une politique restreinte aux deux modèles utilisés) + `AWSLambdaBasicExecutionRole` | Isolé du reste du compte |

Alternative plus ambitieuse si le temps le permet : **Bedrock AgentCore Runtime** pour héberger l'orchestrateur
lui-même (`bedrock-agentcore:CreateAgentRuntime` est autorisé) — à évaluer le jour J selon le temps restant ; sinon
Lambda suffit et compte pour le critère AWS.

## 4. Checklist du jour J

1. Vérifier que les identifiants AWS du poste qui déploie sont à jour (`python backend/verifier_bedrock.py`).
2. Créer un petit test réel (ex. bucket S3 vide) pour confirmer qu'aucune SCP ne bloque silencieusement.
3. Déployer le backend (Lambda + Function URL), noter l'URL.
4. Mettre à jour `frontend/.env` ou la config de build avec `VITE_API_URL=<url Lambda>`, builder, déployer sur
   Amplify ou S3+CloudFront.
5. Créer le Guardrail Bedrock, le brancher dans `llm.py` (`guardrailConfig` du `converse()`), vérifier qu'un texte
   de conseil est bien bloqué par Guardrails **et** par le contrôle en code (défense en profondeur).
6. Mettre à jour `README.md` et `infra/README.md` avec les URL réelles et l'état « déployé ».
7. **Enregistrer la vidéo pendant que tout tourne**, avant la destruction du compte lundi 13 h 59.
8. Ne rien laisser tourner sans besoin si le compte le permet (coût), mais ne pas compter sur un arrêt manuel : le
   `WSReaperRole` nettoie automatiquement après l'événement.

Voir aussi `docs/audit-2026-11-15.md` §7 (plan d'action P0/P1) pour le contexte complet de cette priorité.
