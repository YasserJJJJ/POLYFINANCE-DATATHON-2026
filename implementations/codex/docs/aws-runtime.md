# AlphaForge — Route AWS vérifiée

État relevé le 15 novembre 2026 à 06:57, heure de Montréal
(`2026-11-15T11:57:05Z`). Le prototype est destiné au Mac du porteur.
Aucune infrastructure n'a été créée ou publiée par ces vérifications.

## Identité et périmètre

| Élément | Valeur constatée |
|---|---|
| Compte attendu et vérifié par STS | `471112821226` |
| Rôle de la session locale | `arn:aws:sts::471112821226:assumed-role/WSParticipantRole/Participant` |
| Profil nommé | `alphaforge` |
| Région d'entrée | `us-east-1` |
| Fournisseur de l'orchestrateur de développement | `amazon-bedrock-runtime` |
| Fournisseur du sous-agent AWS | `amazon-bedrock-runtime`, vérifié dans sa propre métadonnée de session |
| Modèle du produit testé | `global.openai.gpt-6-astra` |
| Endpoint du produit | `https://bedrock-runtime.us-east-1.amazonaws.com` |
| API du produit | Bedrock Runtime `Converse`, authentification AWS SigV4 |
| Identifiant de la vérification STS du client | `db30f177-c84e-49ba-8e4c-367162955d73` |

L'identité correspond au rôle Participant de l'atelier. Le financement et la
fermeture du compte sont documentés dans les sources de l'événement ; le solde
des crédits, les factures et l'expiration exacte des identifiants n'ont pas été
consultés. Le profil global peut exécuter l'inférence dans une autre région AWS :
`us-east-1` décrit la région d'entrée, pas une garantie de résidence des calculs.

Le sous-agent AWS porte l'identifiant
`01a1df0e-3fb7-7343-953c-31488e56a455`. Son enregistrement `session_meta` indique
explicitement `amazon-bedrock-runtime`. L'identité a été revérifiée par un appel
STS dans son propre environnement. Cette observation ne certifie pas les routes
d'autres clients ou sous-agents : chaque responsable doit conserver sa preuve.

### Vérification des sessions de développement par l’orchestrateur

Lors de l’inventaire initial du 15 novembre, l’orchestrateur a également
consulté les métadonnées des quatre sessions de cette équipe :

| Session | Fournisseur relevé | Modèle relevé |
|---|---|---|
| Orchestrateur `/root` | `amazon-bedrock-runtime` | `global.openai.gpt-6-astra` |
| `/root/aws_runtime` | `amazon-bedrock-runtime` | `global.openai.gpt-6-astra` |
| `/root/finance_engine` | `amazon-bedrock-runtime` | `global.openai.gpt-6-astra` |
| `/root/experience` | `amazon-bedrock-runtime` | `global.openai.gpt-6-astra` |

La session racine porte l’identifiant
`01a1df00-0052-7253-bb57-4101b33a51fb`. Cette observation documente la route
déclarée par les sessions contrôlées ; elle ne constitue pas un relevé de
facturation AWS. Les appels réels du produit, avec identité STS vérifiée,
apportent la preuve complémentaire décrite ci-dessous. Les calculs Python,
tests, rendus de PDF et synthèse vocale système sont effectués localement.

## Choix d'API

La fiche AWS actuelle de GPT-6 Astra prend en charge Converse, les outils et les
sorties JSON Schema. Le SDK `boto3` fournit donc directement le transport signé,
les délais d'attente et les erreurs AWS nécessaires. Aucun SDK d'API directe
OpenAI ou Anthropic n'est nécessaire au prototype.

L'alternative Responses demeure disponible sur Bedrock Runtime, sous
`/openai/v1/responses`. Elle est utile si les capacités documentaires ou les
contrats Responses deviennent nécessaires. Elle n'apporte pas de gain requis
pour les trois capacités effectivement testées ici.

Versions exécutées :

- Python du `.venv` du projet ;
- `boto3==1.44.3` et `botocore==1.44.3` ;
- `jsonschema==4.26.0`.

## Contrat du client

Le module `alphaforge_app/bedrock.py` expose :

```python
from alphaforge_app.bedrock import BedrockClient, BedrockError

client = BedrockClient()
result = client.generate(
    messages,
    tools=tools,
    tool_choice="any",       # premier tour si un outil doit être consulté
    reasoning_effort="medium",
    max_tokens=4096,
)
```

`messages` accepte les rôles `system`, `developer`, `user`, `assistant` et
`tool`. Les appels d'outils peuvent employer le format OpenAI
`{"id": ..., "type": "function", "function": {"name": ..., "arguments": "..."}}`
ou le format normalisé `{"id": ..., "name": ..., "arguments": {...}}`.

Les outils acceptent les schémas `function` avec `name`, `description` et
`parameters`, placés directement ou dans `function`. `tool_choice` accepte
`auto`, `any`, `required` et `{"name": "outil"}`.

Le résultat contient :

- `text`, `tool_calls`, `parsed` ;
- `request_id`, `model`, `provider`, `region`, `account_id` ;
- `usage`, `latency_ms`, `server_latency_ms`, `stop_reason`.

Le client n'exécute aucun outil. L'orchestrateur vérifie l'autorisation, exécute
le calcul, puis ajoute un message `tool` avec `tool_call_id` et `content`.
Si un appel conserve cet historique `toolUse`, les définitions des outils
doivent rester fournies, même si une réponse JSON est demandée : Converse
valide l'historique. Le schéma ne supprime pas à lui seul la possibilité d'un
nouvel appel d'outil.

Le produit distingue désormais cette planification de la restitution finale.
L'orchestrateur construit pour cette dernière un nouveau contexte contenant la
demande, le profil, les hypothèses, les résultats vérifiés, les fiches lues et
les erreurs d'outils éventuelles. Ce contexte ne comporte ni historique
`toolUse` ni capacité d'outil. La conclusion reçoit uniquement `json_schema`,
avec les identifiants d'observations autorisés et une sélection de trois à
cinq observations. Cette séparation prévient une nouvelle demande d'outil au
moment où une conclusion structurée est attendue.

Pour une sortie structurée, passer `json_schema=<schéma>` et éventuellement
`schema_name`. Le client configure les deux champs requis par GPT-6 Astra :
`outputConfig.textFormat` et
`additionalModelRequestFields.text.format.strict=true`. Il valide ensuite le
JSON reçu avec `jsonschema`. Cette vérification de structure ne remplace pas
les invariants financiers ou la provenance des données.

`BedrockError.as_dict()` fournit une erreur exploitable par l'interface :
`message`, `code`, `request_id`, `retryable`. Une réponse tronquée, refusée ou
vide n'est pas traitée comme une réponse utilisable.

Le client Python conservé par l'orchestrateur prend en charge le renouvellement
manuel du profil d'atelier. Une session boto3 existante garde en mémoire les
identifiants statiques qu'elle a déjà chargés, même après réécriture du fichier
de profil. Sur `ExpiredToken`, `ExpiredTokenException`, `InvalidClientTokenId`
ou `UnrecognizedClientException`, le client invalide donc sa connexion et sa
session internes. La demande courante reste en erreur avec son diagnostic ;
aucune inférence supplémentaire n'est tentée automatiquement.

À la demande suivante, le même objet `BedrockClient` crée une nouvelle session
boto3, relit `alphaforge` et revérifie le compte par STS avant l'inférence.
Un profil renouvelé vers un autre compte est refusé. La reconstruction est
protégée contre les accès concurrents et un échec provenant d'une ancienne
connexion n'invalide pas une connexion déjà renouvelée.

## Mesures exécutées

La commande suivante effectue un contrôle STS puis trois petites inférences
facturées au compte vérifié :

```bash
.venv/bin/python scripts/aws_probe.py --live
```

Sans `--live`, elle ne réalise que la vérification d'identité et l'inventaire
des versions. Les essais ne créent aucune ressource.

| Test | Résultat | Tokens entrée / sortie | Durée client | Requête AWS |
|---|---|---:|---:|---|
| Profil en français, horizon déclaré et liquidité inconnue, JSON Schema strict | Réussi | 98 / 62 | 1 846 ms | `5a288d3d-e0f7-4c5a-a573-29f84b1cb424` |
| Choix d'un outil et arguments conformes au schéma | Réussi | 94 / 21 | 1 036 ms | `e3efcada-405a-4e40-8191-f7f3761fd048` |
| Retour d'outil puis restitution JSON exacte de `9876.54 CAD` | Réussi | 183 / 23 | 1 476 ms | `1d48d489-8ad3-4af6-a8a9-85fb988e55be` |

Ces trois appels ont consommé 481 tokens au total, avec effort de raisonnement
`medium`. Un appel préliminaire distinct a également obtenu
`alphaforge-aws-ok` avec 27 tokens et 724 ms de latence serveur.

Ces essais établissent l'invocabilité de ce modèle et le fonctionnement des
contrats testés. Ils ne constituent pas un benchmark financier, une garantie
de latence future ou une comparaison générale entre modèles.

## Mesures de routage dans le code

- Le client refuse une région d'entrée autre que `us-east-1`.
- L'identité STS doit correspondre au compte attendu avant la première
  inférence.
- Les endpoints STS et Bedrock sont explicites ; les surcharges d'endpoint
  issues de la configuration ou de l'environnement sont ignorées.
- La signature est imposée à SigV4. Un
  `AWS_BEARER_TOKEN_BEDROCK` présent provoque un arrêt explicite avant l'appel.
- Le profil nommé utilise la chaîne AWS ; aucune clé n'est copiée dans le code.
- Les reprises SDK sont bornées à deux tentatives au total. Aucun changement
  silencieux de compte, de modèle ou de fournisseur n'est prévu.
- Les journaux ne contiennent que modèle, identifiant de requête, statut,
  nombre de tokens et durée. Ils ne contiennent ni prompt ni identifiants ni
  raisonnement interne du modèle.

Quatre vérifications ciblées supplémentaires ont réussi : rejet d'une autre
région, rejet d'un jeton prioritaire factice, rejet d'un compte attendu
différent, et maintien des endpoints AWS explicites malgré trois surcharges
`AWS_ENDPOINT_URL*` vers un domaine de test invalide. Ces vérifications n'ont
effectué aucune inférence.

Le renouvellement du profil a été vérifié sans réseau, avec de véritables
lectures SDK d'un fichier temporaire contenant des identifiants factices et
des services STS/Bedrock simulés. Les quatre codes d'authentification sont
couverts, ainsi que le rejet d'un autre compte après renouvellement.

```text
.venv/bin/python -m pytest -q tests/test_bedrock_credentials.py tests/test_orchestrator.py
15 passed in 1.38s
```

## Hébergement et préservation

Le chemin retenu pour la première démonstration est
**navigateur local → serveur Python local → Bedrock du compte atelier**.
L'apport AWS est l'inférence réellement utilisée pour sélectionner les outils
et produire la restitution structurée. L'application doit montrer ses
identifiants de requêtes et les résultats des outils qui ont soutenu la réponse.

L'inventaire du compte a relevé zéro bucket S3 et aucune Lambda AlphaForge.
Les fonctions et rôles existants appartiennent à l'infrastructure de l'atelier ;
ils n'ont pas été modifiés. Aucun rôle Lambda propre au projet n'a été créé.

Un déploiement ultérieur demanderait de choisir une audience et une destination
avec le porteur, de vérifier le rôle d'exécution du service, puis d'empaqueter la
version validée. Une fonction Lambda invoquée par SDK pourrait rester privée ;
elle ne fournit pas à elle seule un site utilisable sans authentification.
Le script de déploiement n'est pas créé dans cette version, conformément au
choix de démonstration sur Mac.

Code, données autorisées et preuves doivent rester sur le Mac ou une sauvegarde
extérieure au compte éphémère. La fermeture AWS empêchera les nouvelles
inférences ; le prototype doit conserver ses exemples enregistrés en les
distinguant clairement d'une nouvelle exécution.

## Sources primaires consultées

- [AWS — fiche GPT-6 Astra, API, outils et JSON Schema](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-6-astra.html).
- [AWS — Responses API et différences d'endpoint](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-responses-api.html).
- [AWS — appels d'outils exécutés par le client](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-client-side.html).
- [OpenAI — configuration de Codex sur Bedrock](https://learn.chatgpt.com/docs/amazon-bedrock).

Les noms des modèles listés par le service ne garantissent pas leur
invocabilité. Cette version a testé GPT-6 Astra uniquement.
