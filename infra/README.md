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
