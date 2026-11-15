# Accès AWS et fiabilité de la recherche — vérifications du 15 novembre 2026

Périmètre : recherche méthodologique ; aucun fichier produit, interface, modèle, infrastructure ou déploiement modifié. Les paramètres testés restent le profil `alphaforge`, la région `us-east-1` et le compte `471112821226`. Les preuves brutes expurgées sont dans `inventaire_verifications.json` et `preuve_web_search.json`.

## Ce qui a effectivement fonctionné

| Vérification | Résultat observé | Identifiant de requête | Limite de la preuve |
|---|---|---|---|
| STS `GetCallerIdentity` | HTTP 200 ; rôle `assumed-role/WSParticipantRole/Participant`, compte attendu | `6748ed55-ddcc-45c7-9cd8-24db5410563b` | L’identité ne prouve aucun autre droit AWS. |
| Bedrock `GetInferenceProfile` | Profil `global.openai.gpt-6-astra` actif, `SYSTEM_DEFINED` | `445e4038-2cf8-4dea-8ae1-4708a0d8ddc6` | Métadonnées de profil, pas nouvel appel d’inférence. L’ARN global et le point d’accès américain ne prouvent pas une résidence canadienne. |
| Bedrock `GetModelInvocationLoggingConfiguration` | HTTP 200, configuration absente | `4fe973c1-15fc-492b-8039-235e16721496` | La journalisation centralisée des invocations Bedrock n’est pas activée dans cette configuration. Cela ne signifie pas absence de toute trace AWS ou locale. |
| AgentCore `ListAgentRuntimes(maxResults=1)` | HTTP 200, zéro runtime, aucune page suivante | `9d885239-20d1-4ca7-9168-177f10f01f3b` | Droit de lecture vérifié ; ni runtime créé ni exécution d’agent AgentCore testée. |
| AgentCore `InvokeWebSearch` | HTTP 200, trois résultats, 651 ms mesurées côté client | `7cc9d3e7-139f-40e9-ba5f-48ab8b81f26e` | Recherche documentaire réellement utilisée, pas `WebAnswer`. Aucune mesure de charge facturée retournée. |

Versions locales relevées : boto3/botocore `1.44.3`, httpx `0.28.1`, jsonschema `4.26.0`. La métadonnée de cette session enfant `01a1df0e-3fb7-7343-953c-31488e56a455`, chemin `/root/aws_runtime`, déclare `model_provider=amazon-bedrock-runtime`. Il s’agit d’une preuve déclarative de route, distincte des requêtes AWS signées ci-dessus ; aucune capture réseau des inférences internes n’a été effectuée.

La vérification de recherche n’a créé aucune ressource et n’a appelé aucune API auxiliaire d’inférence. L’API documentaire a été appelée une seule fois avec :

```json
{
  "webSearchId": "web-search.v1",
  "searchQuery": "CRITIC large language models self-correct tool interactive critiquing",
  "maxResults": 3,
  "filters": {"domainFilter": {"include": ["arxiv.org"]}}
}
```

## Expérience discriminante : une date d’index n’est pas une date primaire

Le résultat no 2 de cette recherche identifie **CRITIC** à `https://arxiv.org/html/2305.11738`, mais renvoie `publishedAt = 2017-05-05 00:00:00+00:00`.

La notice primaire **U013**, `https://arxiv.org/abs/2305.11738`, archivée dans `../collecte/U013.extrait.txt`, ligne 22, indique :

> [Submitted on 19 May 2023 (v1), last revised 21 Feb 2024 (this version, v4)]

Son historique, lignes 57–60, précise la première soumission le **19 mai 2023 à 15:19:44 UTC** puis la **v2 le 30 septembre 2023 à 08:35:29 UTC**. La version méthodologique lue ici est explicitement `https://arxiv.org/html/2305.11738v2` ; son en-tête archivé dans `sources/critic_full.txt:198` est :

> arXiv:2305.11738v2 [cs.CL] 30 Sep 2023

Le HTML de cette version a été obtenu le `2026-11-15T13:53:59.298578+00:00`, SHA-256 `611f39b9237f53b05076e352dbd84fe59284cd0ff31e51285d76e0f9c93c26de`. Le `Last-Modified` HTTP de 2026 correspond au serveur et ne remplace pas non plus la date intellectuelle de publication.

La valeur 2017 du résultat est incompatible avec cet historique. Le résultat no 1 renvoie 2024, compatible avec une révision, mais ce champ ne dit pas explicitement quelle version il date. Cette observation réfute l’hypothèse selon laquelle filtrer uniquement `publishedAt` suffit à construire un corpus historiquement disponible. Elle ne mesure ni le taux d’erreur global du moteur ni la qualité de tous ses résultats.

**Décision Agent1 proposée :** conserver séparément `retrieved_at`, `index_published_at`, `primary_submitted_at`, `version_date`, `effective_date` lorsque pertinente, et `available_as_of`. Toute incompatibilité ouvre une anomalie de provenance. Un résultat trouvé devient une source retenue seulement après récupération du document primaire et choix explicite de version. Garder le lien, le passage, la page ou section et l’empreinte ; ne jamais transformer automatiquement un extrait d’index en preuve suffisante.

## Documentation AWS lue et décisions

| Identifiants et source | Niveau effectivement lu | Ce qu’elle permet de décider |
|---|---|---|
| **U360**, [API Web Search](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/web-search-api.html), documentation courante consultée le 15 novembre | Corps de page complet ; schéma boto3 inspecté ; requête réelle ci-dessus | L’API directe ne nécessite pas de passerelle. `maxResults` est borné de 1 à 25. Disponibilité documentée notamment en `us-east-1` ; aucune région canadienne dans la liste lue. Le chemin retenu est une recherche, suivie d’une lecture HTTP documentaire. |
| **U361**, [connecteur Web Search Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-web-search-tool.html) | Corps de page complet | Une passerelle MCP constitue un autre chemin, nécessitant sa configuration. `WebSearch` et `WebAnswer` sont deux outils distincts ; avoir le premier ne prouve pas la route d’inférence du second. Aucun Gateway n’a été créé ou testé. |
| Complément, [Getting started Web Search](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/web-search-api-get-started.html), archive `sources/aws_search_getstarted.*` | Corps utile complet | Identifiant `web-search.v1`, SDK et ressource IAM dont le segment de compte est littéralement `aws`. Ces paramètres ont été vérifiés par l’appel réussi. |
| **U119**, [model invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) | Corps de page et schéma de trace lus | Fonction désactivée par défaut ; ce compte retourne effectivement une configuration vide. Des journaux locaux structurés restent nécessaires. Ne pas annoncer une traçabilité CloudWatch effective parce que la fonction est documentée. |
| **U324**, [AgentCore observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) | Introduction et fonctionnement lus | OpenTelemetry/CloudWatch sont des possibilités d’instrumentation ; les spans détaillés exigent une intégration. Aucun runtime n’existe dans la liste vérifiée. Une architecture future doit démontrer chaque export et sa rétention. |
| **U042**, [Automated Reasoning checks](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html) | Fonctionnement, limitations et routage régional lus | Vérification logique relative à une politique formalisée, non preuve de vérité financière générale. La traduction du langage naturel fait intervenir des modèles ; la route exacte n’est pas établie pour ce compte. Anglais US seulement, absence de protection contre injection, mode détection ; non retenu comme prérequis du prototype francophone. |
| **U113**, [contextual grounding](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html) | Concepts Classic/Standard, scores, limites et exemples lus ; toute la référence API non lue | Ancrage et pertinence sont deux dimensions. Un score d’ancrage peut approuver une source fausse ou hors date ; ce n’est pas une probabilité calibrée de vérité. Option d’évaluation ultérieure, pas un certificat ni un accès exercé. |
| **U040**, [Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) | Avis d’accès et introduction lus | L’avis lu concerne l’absence d’inscriptions nouvelles ; il ne justifie pas d’écrire que tous les agents existants ont cessé de fonctionner. Aucun agent Classic utilisé. |

Les restrictions de recherche hébergée du client Codex sur Bedrock et l’existence de l’API documentaire AgentCore ne se contredisent pas : ce sont des surfaces différentes. La documentation officielle [Codex sur Bedrock](https://learn.chatgpt.com/docs/amazon-bedrock), vérifiée par l’orchestrateur racine, ne constitue pas à elle seule la preuve d’accès AgentCore ; la requête ci-dessus la fournit.

## Inventaire des outils : capacité déclarée et opération observée

Les outils exposés à cette session incluent terminal/Python, lecture locale, SearchService documentaire, connecteur GitHub, outils de collaboration, contrôle de navigateur, sessions documentaires, Sites et gestion de plugins. Leur présence dans l’interface n’équivaut pas à un compte connecté, une autorisation effective ou une route d’inférence connue. Pour cette sous-mission, seuls HTTP documentaire, lectures locales, terminal, collaboration, SearchService documentaire et les opérations AWS listées ont été utilisés ; le code de dépôts a été obtenu par HTTP en lecture seule. Ni contrôle de navigateur ni Sites ni service d’inférence externe utilisés.

Les découvertes « AWS Data Analytics », « Firecrawl » et « TinyFish » rapportées par la racine correspondent à des plugins non installés : elles sont un inventaire de possibilités, pas des connexions actives. Aucune installation n’était nécessaire pour les vérifications réalisées. La preuve déclarative commune des quatre sessions est conservée dans `../verification_route_codex.json` ; elle n’est ni un relevé de facturation ni une preuve de région physique.

La collection de 36 PDF recensée dans `revision_2026-11-15/00B_ATLAS_DES_RESSOURCES_ET_PLAN_EXPLOITATION.md` apporte des guides d’accès, données, développement, agents et livraison. Elle ne prouve pas que tous ces services existent dans le compte. Le tri fonctionnel de cette collection sera joint à l’inventaire des candidats ; les PDF qui n’ont pas été lus individuellement ne seront pas présentés comme des sources profondément examinées.
