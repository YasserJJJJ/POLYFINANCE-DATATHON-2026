# Expérience technique — Les services AWS pour l'enchaînement, la persistance, la recherche et l'observation

Petite expérience du 15 novembre 2026 (14 h 35 à 14 h 55) pour départager les options d'architecture (cadre de conception, section 7). Ce n'est pas le produit. **Aucune ressource AWS n'a été créée, modifiée ni supprimée.** Rien n'est installé dans le projet.

## Cadre des essais

- Bibliothèques : `boto3` 1.44.3 et `botocore` 1.44.3 (Apache-2.0, déjà dans le projet), Python 3.13.0. Pour l'essai 6 seulement : `moto` 5.2.5 (Apache-2.0), dans un environnement jetable de `uv`.
- Compte : rôle `WSParticipantRole`, compte se terminant par 1226, profil « alphaforge », région us-east-1. Les sorties ne gardent que la fin du numéro de compte.
- Inférence : Amazon Bedrock seulement. Cinq appels de modèle sur vingt permis : deux `Converse` sur `global.anthropic.claude-haiku-5-5`, un reclassement `cohere.rerank-v3-5:0`, deux plongements `amazon.titan-embed-text-v2:0`. Le journal `sorties/appels_bedrock.jsonl` les liste avec leur identifiant de requête. `commun.py` refuse un appel au-delà de vingt lignes dans ce journal.
- Recherches web : douze sur douze permises. Onze recherches de documentation (`recherches_documentation.sh`, résultats dans `sorties/doc/`) et une recherche faite par l'essai 4. Trois pages de documentation ont été lues par `curl` (`sorties/doc/11` à `13`).
- Télémétrie : `boto3` et `moto` n'envoient rien à un tiers. `boto3` ne parle qu'aux points d'accès AWS appelés. `moto` intercepte les appels dans le processus et l'essai 6 pose des identifiants factices avant d'importer `boto3`. Rien n'était à désactiver.

## Relancer un essai

Depuis la racine du dépôt :

```
uv run python research/experiences/technique/services_aws/essai1_inventaire.py
uv run python research/experiences/technique/services_aws/essai2_droits.py
uv run python research/experiences/technique/services_aws/essai3_step_functions.py
uv run python research/experiences/technique/services_aws/essai4_appels_du_produit.py      # 5 appels de modèle, 1 recherche web
uv run python research/experiences/technique/services_aws/essai5_observation.py            # à lancer cinq minutes après l'essai 4
uv run --with "moto[s3,dynamodb]" python research/experiences/technique/services_aws/essai6_emulation_locale.py
bash research/experiences/technique/services_aws/recherches_documentation.sh               # 11 recherches web
```

| Essai | Appels de modèle | Ce qu'il montre | Sorties |
|---|---|---|---|
| 1 | 0 | Ce qui existe dans le compte et ce que le rôle peut lister (25 sondes de lecture) | `sorties/essai1.txt`, `sorties/essai1_inventaire.json` |
| 2 | 0 | Ce que le rôle aurait le droit de créer, par simulation IAM (44 actions) | `sorties/essai2.txt`, `sorties/essai2_droits.json` |
| 3 | 0 | Notre chaîne écrite pour Step Functions (`chaine_alphaforge.asl.json`), validée par AWS ; 17 essais d'états isolés avec réponses simulées | `sorties/essai3.txt`, `sorties/essai3_step_functions.json`, `sorties/chaine_variante_activites.asl.json` |
| 4 | 5 | Le produit appelle lui-même la recherche web d'AgentCore, le reclassement et les plongements (`services_produit.py`) | `sorties/essai4.txt`, `sorties/essai4_appels_du_produit.json` |
| 5 | 0 | Ce qu'AWS garde déjà de nos inférences, sans rien créer (CloudWatch, CloudTrail) | `sorties/essai5.txt`, `sorties/essai5_observation.json` |
| 6 | 0 | Nos contrats de dossier écrits pour S3 et DynamoDB, sur un émulateur local | `sorties/essai6.txt`, `sorties/essai6_emulation_locale.json` |

## Ce qui a été testé

**Essai 1.** Le compte ne contient aucune machine Step Functions, aucun compartiment S3, aucune table DynamoDB, aucune base de connaissances, aucun compartiment de vecteurs, aucun garde-fou, aucune ressource AgentCore (runtime, mémoire, passerelle, moteur de règles). Le journal des invocations Bedrock est désactivé. AgentCore liste 32 évaluateurs intégrés (`Builtin.Correctness`, `Builtin.Faithfulness`, etc.). Lambda : 7 fonctions de l'atelier, 110 exécutions simultanées non réservées sur 400. Une seule lecture est refusée (`list_registries`).

**Essai 2.** La simulation IAM répond « allowed » pour les 44 actions essayées, y compris `iam:CreateRole` et `iam:PassRole`. Elle a tenu compte des règles d'organisation. Le rôle porte `AdministratorAccess` et des politiques propres à l'atelier (`ws-default-policy`, `deny-kiro-api-secret-0`, `DenyIAMUserAndKeyCreation`), dont le contenu n'a pas été lu. Aucun rôle du compte n'est endossable par Step Functions, par Bedrock ou par AgentCore : chacun de ces services demanderait de créer aussi un rôle. Une simulation n'est pas une création réussie.

**Essai 3.** `ValidateStateMachineDefinition` accepte notre chaîne (résultat « OK », aucun diagnostic) et sa variante sans Lambda, où chaque rôle est une « activité » que le produit local vient chercher. Il refuse une transition vers un état absent. **Il accepte une attente de réponse humaine qui ne transmet pas son jeton** : il contrôle la forme, pas le sens. `TestState`, avec des réponses simulées et sans rôle, donne les transitions attendues : variable manquante vers la question ; réponse reçue vers l'agent 0 ; délai dépassé vers « interrompue » ; verdict « change » vers l'agent 2 une fois, puis « interrompue » ; limitation de débit « à réessayer » puis, réessais épuisés, « interrompue » ; refus d'une porte vers « interrompue ». En contrôle strict, la réponse simulée d'une intégration Lambda ou Bedrock doit être une chaîne et l'état échoue ensuite (`States.Runtime`) ; il réussit quand le contrôle est levé. L'essai ne dit donc rien de sûr sur la relecture JSON de ces réponses en exécution réelle.

**Essai 4.** Le modèle, qui n'a que l'outil `recherche_web`, choisit une requête. Le code appelle `InvokeWebSearch` (6 résultats), reclasse les extraits, rend les trois premiers. Le modèle rend une preuve candidate par un outil à schéma imposé. Le code vérifie que la citation figure mot pour mot dans l'extrait : oui. La citation retenue (« n = 120 months… ») existe, mais elle ne répond pas clairement à la question : l'existence est contrôlée, le soutien reste « non jugé », comme le prévoit le cadre.

**Essai 5.** À 14 h 46, six minutes après l'essai 4, l'historique CloudTrail (aucune piste à créer) contient nos deux appels `Converse` et nos deux appels `InvokeModel`, retrouvés par leur identifiant de requête. Il ne contient ni le reclassement ni la recherche web, et CloudWatch ne compte aucune invocation sous le modèle de reclassement. Pour ces deux appels, la seule preuve est l'identifiant de requête gardé par le produit.

**Essai 6 (émulateur local, pas AWS).** Une pièce déposée deux fois sous son empreinte est créée puis refusée (`If-None-Match`). Deux écrivains qui prolongent la même tête : le premier passe, le second est refusé (écriture conditionnelle). La tête se déduit du journal. Une correction retire le calcul qui en dépendait. Une variante partage les pièces et laisse la ligne principale intacte. L'invalidation sélective et la bifurcation sont écrites par notre code : aucun des deux services ne les fournit.

## Constat par service

États : D = documenté, P = présent dans le compte, A = autorisé (lecture testée, création simulée seulement), T = testé.

| Service | Ce qu'il apporterait à nos contrats | État | Ressource à créer | Mise en place | Risque d'ici lundi 13 h 59 | Verdict |
|---|---|---|---|---|---|---|
| Step Functions | Transitions décidées hors modèle, réessais, parallélisme, attente d'une réponse par jeton (jusqu'à un an), reprise au point d'échec (14 jours) | D, A, définition et états testés sans exécution réelle | Machine, rôle IAM, et activités ou fonctions Lambda | 1 à 2 h, sans compter l'adaptation du produit | Élevé : l'historique disparaît ; le produit local ne tourne plus sans réseau ; il faut quand même un greffier local | Écarter comme porteur de l'enchaînement |
| S3 versionné | Dépôt de pièces où le service refuse l'écrasement | D, A, testé sur émulateur seulement | Compartiment | 15 min | Moyen : tout est à exporter | Optionnel, comme copie |
| Verrouillage d'objets S3 | Immuabilité garantie par le service | D, A | Compartiment versionné, verrouillage activé | 15 min | Aucun gain en 23 heures | Écarter |
| DynamoDB | Journal avec une seule écriture à la fois par branche | D, A, testé sur émulateur seulement | Table | 15 min | Moyen : export à faire ; chaque écriture dépend du réseau | Écarter |
| Journal des invocations Bedrock | Texte complet de chaque demande et réponse `Converse` et `InvokeModel` | D, P (désactivé), A | Groupe de journaux et rôle, ou compartiment ; réglage de tout le compte | 20 min | Moyen : le compte est partagé, le réglage capte aussi les autres équipes ; export à faire | Optionnel, décision du porteur |
| Historique CloudTrail et métriques CloudWatch | Preuve, tenue par AWS, que `Converse` et `InvokeModel` ont eu lieu | T | Aucune | Fait | Faible : à exporter avant la fermeture | Retenir |
| AgentCore, recherche web | Niveau 2 de la recherche de l'agent 1 | T, depuis un code de produit | Aucune | Fait | Faible : rend des extraits, pas des textes | Retenir |
| Reclassement et plongements Bedrock | Tri des fiches et des extraits | T, depuis un code de produit | Aucune | Fait | Faible | Retenir le reclassement ; plongements optionnels |
| AgentCore Runtime | Hébergement du produit | D, A | Conteneur ARM64, dépôt d'images, rôle, runtime | Plusieurs heures | Élevé | Écarter |
| AgentCore Memory | Événements en ajout seul, avec branches | D, A, lu dans le code installé | Mémoire, rôle | 30 min | Élevé : pas d'empreintes, pas de rejeu hors ligne | Écarter |
| AgentCore Gateway et Policy | Outils servis par MCP, règles d'accès | D, A | Passerelle, cibles, moteur de règles | 1 h et plus | Élevé pour un gain nul : nos outils sont dans le code | Écarter |
| AgentCore Observability et Evaluations | Traces par agent ; 32 évaluateurs intégrés | D, P (évaluateurs), A | Réglage du compte (Transaction Search), instrumentation | 1 h | Moyen : réglage partagé, traces perdues à la fermeture | Écarter pour ce soir |
| Bases de connaissances et S3 Vectors | Recherche gérée dans la bibliothèque | D, A | Compartiment, index de vecteurs, base, source, rôle | 45 min | Moyen : le découpage n'est pas le nôtre ; 25 fiches se trient sans index | Écarter |
| Guardrails | Second contrôle de la restitution (sujets refusés, ancrage) | D, A | Garde-fou | 15 min, plus les essais | Moyen : conduite en français non établie | Optionnel, à essayer avant d'en dépendre |
| Lambda | Hébergement des calculs ou des rôles | D, P (fonctions de l'atelier), A | Fonctions, rôle, paquet avec numpy et pandas | 1 à 2 h | Élevé pour un gain nul | Écarter |

## Comment le produit appelle la recherche web, le reclassement et les plongements

`services_produit.py` contient les trois fonctions. Elles n'ont besoin d'aucune ressource.

- Recherche web : `boto3.client("bedrock-agentcore").invoke_web_search(webSearchId="web-search.v1", searchQuery=…, maxResults=…, filters=…)`. Droit requis : `bedrock-agentcore:InvokeWebSearch`.
- Reclassement : `boto3.client("bedrock-agent-runtime").rerank(…)` avec le modèle `arn:aws:bedrock:us-east-1::foundation-model/cohere.rerank-v3-5:0`. Droits requis : `bedrock:Rerank` et `bedrock:InvokeModel`.
- Plongements : `boto3.client("bedrock-runtime").invoke_model(modelId="amazon.titan-embed-text-v2:0", …)`, un texte par appel.

Chaque fonction rend l'identifiant de requête AWS, que le produit inscrit au journal du dossier. La recherche est présentée au modèle comme un outil de `Converse` ; c'est le code qui l'exécute, qui garde l'empreinte de chaque extrait et qui contrôle la citation.

## Ce qui a été lu sans être testé

- Dans la documentation, aujourd'hui (extraits dans `sorties/doc/`) : durée maximale d'une exécution standard et d'une attente par jeton (un an) ; historique limité à 25 000 événements et gardé 90 jours ; entrées et sorties limitées à 256 Kio ; reprise (« redrive ») des exécutions échouées dans les 14 jours, sans refaire les étapes réussies ; facturation à la transition, 4 000 transitions gratuites par mois ; verrouillage d'objets qui exige le versionnement ; écritures conditionnelles S3 ; journal des invocations limité aux appels du point d'accès `bedrock-runtime` ; recherche web d'AgentCore sans ressource, dix requêtes par seconde ; AgentCore Runtime par conteneur ARM64 ; observation d'AgentCore subordonnée à « Transaction Search » ; tarifs et limites de Guardrails.
- Dans le code installé (`botocore` 1.44.3) : paramètres de `TestState`, de `InvokeWebSearch`, de `CreateEvent` (champ `branch`), de `Evaluate` ; liste des opérations d'AgentCore et de S3 Vectors.

## Ce qui n'est pas établi

- Aucune création n'a été tentée : « autorisé » veut dire « simulé ».
- Aucune exécution réelle de Step Functions : ni l'attente par jeton, ni la reprise, ni le parallélisme n'ont tourné.
- La conduite réelle de S3 et de DynamoDB (l'essai 6 est un émulateur).
- Le prix unitaire d'une transition Step Functions (la page lue donne la règle, pas le chiffre).
- La conduite de Guardrails sur du texte français et sur notre vocabulaire financier.
- Pourquoi le reclassement et la recherche web n'apparaissent ni dans CloudTrail ni dans CloudWatch : retard, autre nom de métrique ou événements non consignés.
- Chaque conduite a été observée une seule fois, sur le modèle Haiku.
