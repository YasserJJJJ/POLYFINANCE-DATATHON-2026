# Infrastructure AWS (voie Gardien + AWS)

État au 15 nov. : **seul Amazon Bedrock est utilisé** (Profileur sur Nova 2 Lite, Sceptique et Rédacteur sur
Claude Sonnet 5), appelé depuis l'API lancée en local. Rien n'est encore déployé.

Cible, 5 services, chacun avec un vrai rôle :

| Service | Rôle |
|---|---|
| Amazon Bedrock | Modèles : Nova 2 Lite pour le Profileur, Claude Sonnet 5 pour le Sceptique et le Rédacteur (l'Analyste est du code) ; Guardrails : ancrage du texte final et refus du conseil d'achat |
| Bedrock AgentCore Runtime | Héberge l'orchestrateur et les agents (Strands). Plan B : une Lambda Python |
| AWS Lambda | Outils de calcul et Gardien |
| Amazon S3 | Données nettoyées, fiche qualité, dossiers de décision (JSON) |
| AWS Amplify | Héberge l'interface React |

Compte d'équipe valide jusqu'au lundi 16 novembre (supprimé ensuite) : tout le code reste sur GitHub.
Ne jamais commiter de clé : utiliser les variables d'environnement (`AWS_REGION`, `ALPHAFORGE_LLM=bedrock`,
`ALPHAFORGE_MODELE`, `ALPHAFORGE_MODELE_LEGER`).
