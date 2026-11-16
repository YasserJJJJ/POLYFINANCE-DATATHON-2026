> **Guide écrit pour le compte d'atelier du datathon.** Le produit n'exige qu'un profil AWS nommé `alphaforge` donnant accès à Amazon Bedrock. Les scripts `scripts/configurer-aws-workshop.sh` et `scripts/claude-bedrock.sh` cités plus bas ne sont pas dans cette archive ; la partie sur Claude Code concerne l'outil de développement, non le produit.

# Accès AWS — pour vous et pour l'agent

But : (1) vous connecter vous-même à la console AWS fournie par le datathon ; (2) permettre à l'agent AlphaForge d'appeler Amazon Bedrock depuis ce Mac, **sans que vos identifiants passent par la conversation**.

Principe de sécurité : vous saisissez vos identifiants dans **votre** terminal ou votre navigateur. Ils sont rangés par l'AWS CLI dans la configuration AWS de votre Mac, sous un profil nommé `alphaforge`. Le code AlphaForge demande seulement « utilise le profil `alphaforge` » ; il ne lit pas les fichiers d'identifiants et ne les affiche jamais. **Ne collez jamais une clé, un mot de passe ou un jeton dans le chat.**

## Votre cas : Workshop Studio, région us-east-1 (confirmé le 15 nov. 2026)

AWS CLI 2.40.3 déjà installée sur ce Mac. Trois gestes :

1. **Console (pour vous)** : ouvrez le lien Workshop Studio reçu (ou `https://catalog.workshops.aws/join`), connectez-vous, entrez le code d'événement, acceptez les conditions, puis cliquez sur **« Open AWS console »**. Vérifiez la région **us-east-1** en haut à droite, puis ouvrez **Amazon Bedrock**.
2. **Identifiants pour l'agent** : sur la même page de l'événement, ouvrez **« Get AWS CLI credentials »**, onglet Mac/Linux. Gardez la page ouverte.
3. **Dans votre terminal**, lancez le script ci-dessous et collez les trois valeurs une à une (rien ne s'affiche pendant la saisie, c'est voulu) :

```bash
cd ~/Downloads/Datathon2026/Datathon-2026 && bash scripts/configurer-aws-workshop.sh
```

Le script range les valeurs dans le profil `alphaforge` (région us-east-1) avec la commande officielle `aws configure set`, puis affiche « Connexion vérifiée : compte …XXXX ». Ces identifiants sont **temporaires** : quand l'agent signale une session expirée, relancez le script avec les nouvelles valeurs de la page.

Ensuite, dites-moi « AWS configuré » : je lance la vérification en lecture seule, puis l'agent réel.

### Claude Code facturé sur le compte du datathon (Bedrock)

Configuré le 15 nov. 2026 : lanceur `bash scripts/claude-bedrock.sh` (option `--reprise` pour reprendre le projet) et `.claude/settings.local.json` (ce projet seulement ; exclu de git ; aucun secret) : `CLAUDE_CODE_USE_BEDROCK=1`, profil `alphaforge`, région us-east-1, modèle principal **Fable 5.2** (`us.anthropic.claude-fable-5-2`), Opus, Sonnet et Haiku 5.5 épinglés. Fable exige le mode de conservation `aws_review` du compte, activé le 15 nov. 2026 (décision D4) : les échanges avec Fable sont conservés jusqu'à 30 jours dans AWS et peuvent être relus par AWS, sans transmission à Anthropic. Pour revenir à Opus : `ANTHROPIC_MODEL=us.anthropic.claude-opus-5-5 bash scripts/claude-bedrock.sh`. Les autres projets (dont Calibre) restent sur l'abonnement.

- Ce réglage s'applique à une session **Claude Code en ligne de commande** lancée dans ce dossier. L'onglet Code de l'application de bureau utilise une configuration d'inférence tierce propre à l'application, qui s'appliquerait à toute l'application (non vérifié).
- La CLI `claude` n'est pas installée sur ce Mac à ce jour.
- Une fois installée : dans ce dossier, lancer `claude`, accepter la confiance dans le dossier, puis taper `/status` : le fournisseur doit être Amazon Bedrock, région us-east-1.
- Quand les identifiants Workshop Studio expirent, relancer `scripts/configurer-aws-workshop.sh` avec les nouvelles valeurs, puis réessayer.
- Pour réduire le coût, `/model` permet de passer sur Sonnet 5.5 dans la session.
- Risque : une forte consommation peut épuiser le budget ou les quotas du compte d'atelier, dont dépend aussi la démonstration de l'agent.

Les sections suivantes couvrent les autres cas (portail SSO, utilisateur IAM, compte root), au cas où l'accès changerait.

## Étape 1 — Installer l'AWS CLI (une fois)

Homebrew est installé sur ce Mac :

```bash
brew install awscli
```

```bash
aws --version
```

## Étape 2 — Votre accès à la console

Selon ce que le datathon vous a remis :

| Vous avez reçu | Pour ouvrir la console |
|---|---|
| **A.** Un lien du type `https://….awsapps.com/start` (portail d'accès AWS, IAM Identity Center) | Ouvrez le lien, connectez-vous, choisissez le compte puis « Management console ». |
| **B.** Un lien Workshop Studio ou un **code d'événement** (`catalog.workshops.aws/join`) | Connectez-vous, entrez le code, puis « Open AWS console » sur la page de l'événement. |
| **C.** Un numéro de compte (12 chiffres), un nom d'utilisateur et un mot de passe (utilisateur IAM) | `https://<numéro-de-compte>.signin.aws.amazon.com/console` |
| **D.** L'adresse courriel et le mot de passe du compte (« root ») | Connexion possible, mais **ne créez pas de clés root** : créez un utilisateur dédié (étape 3, cas D). |

Dans la console : vérifiez la **région** en haut à droite (souvent imposée par l'organisateur), puis ouvrez **Amazon Bedrock**. Dans « Model catalog » ou « Model access », vérifiez que les modèles Anthropic Claude sont disponibles.

## Étape 3 — Donner accès à l'agent (profil `alphaforge`)

**Cas A — portail SSO (recommandé : aucune clé permanente)**

```bash
aws configure sso --profile alphaforge
```

Répondez : nom de session (au choix, par exemple `alphaforge`) ; « SSO start URL » = votre lien `…awsapps.com/start` ; « SSO region » = la région du portail ; puis validez dans le navigateur qui s'ouvre. Choisissez le compte et le rôle, région par défaut = celle de l'étape 2, format `json`. La session expire au bout de quelques heures ; pour la renouveler :

```bash
aws sso login --profile alphaforge
```

**Cas B — Workshop Studio (identifiants temporaires)**

Sur la page de l'événement, ouvrez « Get AWS CLI credentials » (ou « AWS command line interface »). Dans **votre** terminal, saisissez les trois valeurs affichées :

```bash
aws configure --profile alphaforge
```

```bash
aws configure set aws_session_token "COLLEZ_ICI_LE_JETON" --profile alphaforge
```

Ces identifiants expirent (souvent après quelques heures) : refaites ces deux commandes avec les nouvelles valeurs quand l'agent signale une session expirée.

**Cas C — utilisateur IAM**

Dans la console : IAM → Utilisateurs → votre utilisateur → « Security credentials » → « Create access key » → usage « Command Line Interface ». Puis, dans votre terminal :

```bash
aws configure --profile alphaforge
```

Supprimez cette clé dans la console à la fin du datathon.

**Cas D — compte root** : dans la console, créez un utilisateur dans IAM Identity Center (puis cas A) ou un utilisateur IAM (puis cas C) avec la politique ci-dessous. N'utilisez pas de clés root.

## Étape 4 — Vérifier (lecture seule, aucun appel de modèle)

```bash
cd ~/Downloads/Datathon2026/Datathon-2026 && uv run alphaforge aws-verifier --region VOTRE_REGION
```

Résultat attendu : le profil utilisé, les quatre derniers chiffres du compte, et l'état du profil d'inférence `global.anthropic.claude-sonnet-5-5`. Dites-moi alors « AWS configuré » et je lancerai l'agent réel.

## Ce que fera l'agent, et ce que cela coûte

- `uv run alphaforge agent robert --profil alphaforge` : une conversation Bedrock Converse d'une dizaine d'appels au plus. Coût : quelques dizaines de milliers de jetons par dossier (prix exact des modèles 5.5 non vérifié, facturé via AWS Marketplace).
- Chaque appel laisse son `RequestId` dans le dossier ; c'est la preuve d'intégration AWS pour le jury.
- **Je vous redemanderai votre accord** avant de créer quoi que ce soit dans le compte (journal d'invocation Bedrock, compartiment S3 versionné pour les dossiers).

## Permissions minimales (si vous administrez le compte)

Comptes de datathon : les permissions sont souvent déjà fixées par l'organisateur. Si vous devez les définir, cette politique couvre l'agent ; elle est déduite de la documentation consultée (R01) et **reste à confirmer sur le compte** :

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AlphaForgeInvocation",
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
      "Resource": ["arn:aws:bedrock:*::foundation-model/anthropic.*", "arn:aws:bedrock:*:*:inference-profile/*anthropic.*"]
    },
    {
      "Sid": "AlphaForgeLecture",
      "Effect": "Allow",
      "Action": ["bedrock:GetInferenceProfile", "bedrock:ListInferenceProfiles", "bedrock:ListFoundationModels", "bedrock:GetFoundationModelAvailability"],
      "Resource": "*"
    },
    {
      "Sid": "AlphaForgeAccesModeles",
      "Effect": "Allow",
      "Action": ["aws-marketplace:Subscribe", "aws-marketplace:ViewSubscriptions"],
      "Resource": "*"
    }
  ]
}
```

## En cas de problème

| Message | Cause probable | Action |
|---|---|---|
| « AWS n'est pas configuré » | profil `alphaforge` absent | étape 3 |
| « Session AWS expirée » | SSO ou identifiants temporaires expirés | `aws sso login --profile alphaforge` (A) ou nouvelles valeurs (B) |
| `AccessDeniedException` | modèle non activé ou permissions manquantes | console Bedrock → accès aux modèles ; sinon, demander à l'organisateur |
| Profil d'inférence introuvable | région sans ce profil | essayer `--region us-east-1` ou `--modele us.anthropic.claude-sonnet-5-5` |
