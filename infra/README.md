# Infrastructure AWS (voie Gardien + AWS)

Cible, 5 services, chacun avec un vrai rôle :

| Service | Rôle |
|---|---|
| Amazon Bedrock | Modèles Claude (léger pour le Profileur, principal pour Analyste, Sceptique, Rédacteur) ; Guardrails : ancrage du texte final et refus du conseil d'achat |
| Bedrock AgentCore Runtime | Héberge l'orchestrateur et les agents (Strands). Plan B : une Lambda Python |
| AWS Lambda | Outils de calcul et Gardien |
| Amazon S3 | Données nettoyées, fiche qualité, dossiers de décision (JSON) |
| AWS Amplify | Héberge l'interface React |

Compte d'équipe valide jusqu'au lundi 16 novembre (supprimé ensuite) : tout le code reste sur GitHub.
Ne jamais commiter de clé : utiliser les variables d'environnement (`AWS_REGION`, `ALPHAFORGE_LLM=bedrock`,
`ALPHAFORGE_MODELE`, `ALPHAFORGE_MODELE_LEGER`).

## Déployer (une commande)

`infra/deployer.py` crée tout ce qui est décrit ci-dessus, sauf AgentCore (plan B retenu : une Lambda Python) et
Guardrails (à ajouter ensuite). Il est idempotent : on peut le relancer pour mettre à jour.

```powershell
# 1. Identifiants : coller le bloc « Windows (PowerShell) » de Workshop Studio, puis
.\infra\enregistrer_identifiants.ps1
python backend\verifier_bedrock.py          # doit afficher « OK » pour les deux modèles

# 2. Déploiement (depuis la racine du dépôt, venv activé : boto3 doit être à jour)
python infra\deployer.py                    # interface sur Amplify
python infra\deployer.py --frontend s3      # si Amplify est refusé par le compte
python infra\deployer.py --seulement-construire   # fabrique les zips sans toucher à AWS
```

Ce que ça fait, dans l'ordre : bucket S3 `alphaforge-<compte>-us-east-1` (données du jeu de départ dans `data/`) →
rôle IAM `alphaforge-lambda` → fonction Lambda `alphaforge-api` (Python 3.12, 1,5 Go, 90 s) avec une Function URL
publique → vérification de `/api/sante` → construction de l'interface avec l'URL de l'API → Amplify. À la fin, le
script affiche l'adresse de l'interface et celle de l'API.

Sur AWS, la fonction lit les données dans S3 au démarrage (`ALPHAFORGE_DATA_BUCKET`) et archive chaque dossier de
décision en JSON dans `s3://<bucket>/dossiers/` (`backend/alphaforge/stockage.py`). Les en-têtes CORS viennent de
FastAPI : ne pas les configurer aussi sur la Function URL (valeurs en double, le navigateur refuse).

Si ça échoue :

| Message | Piste |
|---|---|
| `AccessDenied` sur IAM, Lambda ou Amplify | Le compte de l'événement n'autorise pas ce service : noter lequel et le dire à l'équipe |
| Amplify refusé ou `FAILED` | Relancer avec `--frontend s3` |
| Permission « non ajoutée » | `pip install -U boto3`, puis relancer |
| `/api/sante` répond `llm: false` | Le rôle n'a pas accès à Bedrock ou le modèle n'est pas activé : voir les journaux CloudWatch de `alphaforge-api` |
| Le navigateur bloque les appels | Vérifier qu'une seule source ajoute les en-têtes CORS (FastAPI) |

Les tests de ce script ont tourné sur un AWS simulé (moto) et pas sur le vrai compte : la première exécution réelle
peut révéler des différences (permissions du compte, noms de services refusés).
