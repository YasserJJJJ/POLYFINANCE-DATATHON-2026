# Journal des implémentations et ressources

Statut au 15 novembre 2026 : **inspection documentaire et statique**, aucune bibliothèque d’agents installée, aucun code téléchargé exécuté, aucun produit ni déploiement modifié. Les quatre dépôts approfondis ont été épinglés à un commit obtenu par `git ls-remote`, puis leurs fichiers lus par HTTP. Les originaux et empreintes sont conservés dans `sources/` ; `commits.json` et `collecte_code.json` permettent de retrouver les URL exactes. Un README, une licence ou une API disponible ne prouve pas que l’application fonctionne.

## Quatre candidats approfondis

### Strands — candidat pour le graphe explicite et le fournisseur Bedrock

**U126**, dépôt [strands-agents/sdk-python](https://github.com/strands-agents/sdk-python/tree/c8e1351a5a6218c8f5c2417534aedbd021882a76), commit `c8e1351a5a6218c8f5c2417534aedbd021882a76`. Licence Apache-2.0 identifiée dans `strands-py/pyproject.toml` et `LICENSE.APACHE`. Python ≥3.10 ; version déterminée par tags. Le numéro de version commercial du dossier n’a pas été confirmé par une installation.

Fichiers réellement examinés :

- [`strands-py/src/strands/multiagent/graph.py`](https://github.com/strands-agents/sdk-python/blob/c8e1351a5a6218c8f5c2417534aedbd021882a76/strands-py/src/strands/multiagent/graph.py#L310), constructeur et validation du graphe, lignes 310–505 (`strands_code_2.txt`). Nœuds identifiés, arêtes conditionnelles, options `max_node_executions`, délai global, délai de nœud et gestionnaire de session. Les bornes sont optionnelles ; la validation avertit lorsqu’aucune borne n’est posée. Ne pas annoncer qu’un graphe est automatiquement borné.
- [`session/session_manager.py`](https://github.com/strands-agents/sdk-python/blob/c8e1351a5a6218c8f5c2417534aedbd021882a76/strands-py/src/strands/session/session_manager.py), interface complète lue (`strands_code_3.txt`) : hooks et opérations de synchronisation. Certaines opérations multi-agents restent abstraites ou exigent le support du type de session ; l’existence de l’interface n’implique pas une persistance fonctionnelle.
- [`models/bedrock.py`](https://github.com/strands-agents/sdk-python/blob/c8e1351a5a6218c8f5c2417534aedbd021882a76/strands-py/src/strands/models/bedrock.py#L53), constantes, mécanismes de sortie structurée et initialisation, lignes 53–165 et 220–345 (`strands_code_4.txt`). Les valeurs par défaut sont `global.anthropic.claude-sonnet-4-6` et `us-west-2`. La session boto et le modèle doivent donc être explicitement fournis pour conserver `alphaforge`/`us-east-1`/Astra. Le code contient des branches de compatibilité de résultat d’outil et de contenu de raisonnement selon le modèle ; une compatibilité générique ne remplace pas le test sur Astra.
- `telemetry/config.py` : sections de configuration d’export console/OTLP examinées (`strands_code_5.txt`). Un export doit être configuré et sa destination vérifiée ; il n’est pas une preuve d’observabilité présente dans AlphaForge.

**Adaptation proposée :** quatre nœuds de rôles fixes, sous-phases explicites, états et livrables typés, arêtes de révision bornées, session persistante locale, modèle/profil imposés. Comparer d’abord à une machine à états Python explicite : l’ajout d’un framework doit réduire la complexité réelle de reprise, de routage et de traces.

**Expérience restant à faire :** même mini-scénario sur les deux implémentations, interruption/reprise, double événement, mauvais résultat d’outil et changement de spécification ; vérifier que tous les appels, y compris structured-output/retry, utilisent le fournisseur prévu. Aucun test d’exécution Strands n’a eu lieu ici.

### LangGraph — candidat pour reprise et modifications d’état contrôlées

**U254/U255**, dépôt [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph/tree/08a2016953789a4f579b4d36bd1967941ec62012), commit `08a2016953789a4f579b4d36bd1967941ec62012`. `libs/langgraph/pyproject.toml` indique version `1.2.22`, Python ≥3.10 et MIT ; texte de licence lu intégralement. C’est la version du fichier inspecté, pas une distribution installée.

**Lecture :** documentation [persistence](https://docs.langchain.com/oss/python/langgraph/persistence) complète dans son corps utile ; [`types.py`](https://github.com/langchain-ai/langgraph/blob/08a2016953789a4f579b4d36bd1967941ec62012/libs/langgraph/langgraph/types.py#L843) `Command` et `interrupt`, lignes 843–995 (`langgraph_code_2.txt`) ; structures et interface de checkpoint dans `libs/checkpoint/langgraph/checkpoint/base/__init__.py`, lignes 116–177 et 235–290 (`langgraph_code_3.txt`).

`interrupt` exige un checkpointer et la reprise **réexécute le nœud depuis le début**. L’exemple en mémoire n’assure pas une reprise après arrêt du processus. La documentation distingue l’historique par thread et le magasin partagé. Ces propriétés imposent des outils idempotents ou une séparation entre préparation, opération et enregistrement.

**Adaptation proposée :** état par scénario et révision, stockage SQLite pour une démonstration locale si validé, reprise via événement versionné, sorties de rôle distinctes. LangGraph organise un graphe ; il n’ajoute ni revue financière indépendante ni bonne provenance sans code métier.

**Expérience restant à faire :** arrêt juste après une opération avant checkpoint ; reprise deux fois ; ajout d’une clarification utilisateur ; prouver que le journal ne masque ni ne duplique les effets. Fournisseur Bedrock à brancher explicitement, sans exporter automatiquement les données vers une plateforme de traces.

### OptiGuide — motif de scénario contrefactuel, pas bibliothèque fermée existante

**U054/U020**, dépôt [microsoft/OptiGuide](https://github.com/microsoft/OptiGuide/tree/3da334a48c68af9f82035d6dece9e952a46626a9), commit `3da334a48c68af9f82035d6dece9e952a46626a9`. Licence MIT lue ; droits et licence du solveur Gurobi distincts. Code `what-if/optiguide/optiguide.py` et README `what-if/README.md` lus intégralement ; article [2307.03875](https://arxiv.org/pdf/2307.03875), architecture p.2 et §3.1 p.8 lus (`sources/optiguide_pdf.txt:68–111,385–446`). Ces références apparaissent aussi dans le dossier hors des sections confiées.

Le code utilise un modèle existant et ses résultats de base, puis un assistant rédacteur et un assistant de sécurité. À [`optiguide.py:185`](https://github.com/microsoft/OptiGuide/blob/3da334a48c68af9f82035d6dece9e952a46626a9/what-if/optiguide/optiguide.py#L185), une réponse ne contenant pas `DANGER` conduit à l’exécution. À [ligne 236](https://github.com/microsoft/OptiGuide/blob/3da334a48c68af9f82035d6dece9e952a46626a9/what-if/optiguide/optiguide.py#L236), `exec(src_code, locals_dict, locals_dict)` exécute la source produite. Un délai eventlet n’est pas un bac à sable de sécurité. Le code comporte une boucle bornée de débogage et une gestion de statuts d’optimisation.

**Décision :** reprendre le motif « hypothèse de scénario → modification explicite d’un problème → solveur → comparaison expliquée ». Remplacer la génération de code libre et le verdict `SAFE/DANGER` par un catalogue de fonctions/paramètres validés serait **notre adaptation**, pas la description de l’implémentation OptiGuide inspectée. Un résultat infaisable est un état scientifique utile, pas automatiquement une erreur à effacer.

**Expérience restant à faire :** scénario réalisable, infaisable, contraintes contradictoires, paramètre hors domaine ; oracle analytique ou second calcul indépendant. Pas d’exécution d’OptiGuide, de Gurobi ou d’un exemple connecté à OpenAI/Azure dans cette recherche.

### FinRobot — plusieurs implémentations, motifs de données utiles

**U076–U078**, dépôt [AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot/tree/63e1884a42ea7b729551a5424b4bd6a65af636e0), commit `63e1884a42ea7b729551a5424b4bd6a65af636e0`. En-tête de licence Apache-2.0 identifié ; aucun audit complet des dépendances ou licences des données effectué.

Les résumés et introductions de **U077** (2405.14767v2, 27 mai 2024) et **U078** (2411.08804v1, 13 novembre 2024) décrivent respectivement une plateforme en couches et des agents Data/Concept/Thesis pour l’equity research. Ils ne doivent pas être confondus avec chaque branche du code actuel.

- [`finrobot_desktop/finrobot/engine/agents/factory.py`](https://github.com/AI4Finance-Foundation/FinRobot/blob/63e1884a42ea7b729551a5424b4bd6a65af636e0/finrobot_desktop/finrobot/engine/agents/factory.py), fichier entier lu (`finrobot_code_3.txt`) : cinq rôles, modèle commun de configuration, seul le rôle de données reçoit `query_financial_data`. `ticker` et type de donnée sont validés ; prix/états financiers passent par `fetch_canonical`, nouvelles enveloppées comme non fiables. Le commentaire documente un ancien écart entre prix brut et prix canonique, et un problème de premières barres anciennes ; ce sont des constats des mainteneurs, non des bugs reproduits ici.
- [`finrobot_equity/core/src/modules/equity_agents/agent_manager.py`](https://github.com/AI4Finance-Foundation/FinRobot/blob/63e1884a42ea7b729551a5424b4bd6a65af636e0/finrobot_equity/core/src/modules/equity_agents/agent_manager.py), fichier entier lu (`finrobot_code_4.txt`) : huit sections d’analyse, données en Markdown, appel `Runner.run` du SDK OpenAI Agents. Les intitulés de sections ne suffisent pas à démontrer une recherche professionnelle complète.
- `finrobot_autogen/finrobot/agents/workflow.py`, lignes 1–155 lues et autres paramètres repérés (`finrobot_code_2.txt`) : exemple `UserProxyAgent`, réponses automatiques bornées, mais `code_execution_config` comporte `use_docker=False` par défaut. Ni cette route ni celle du SDK OpenAI ne sont adoptées.

**Adaptation proposée :** source canonique unique pour la donnée chiffrée, distinction fait/concept/thèse, outil de données réservé au rôle autorisé, erreurs de normalisation visibles. Les rôles de FinRobot ne remplacent pas les quatre rôles AlphaForge. Les promesses de recherche professionnelle ou de rendements restent des affirmations à évaluer.

**Expérience restant à faire :** prix contradictoires entre source brute et canonique, mauvaises périodes, actualité injectée, données absentes ; vérifier que la restitution renvoie au registre ou s’abstient. Pas d’installation ni d’exécution FinRobot.

## Autres candidats : triage, sans adoption

Les statuts URL par URL figurent dans `triage_sources.json`.

| Famille | Sources et lecture | Décision et limite |
|---|---|---|
| Systèmes de trading et mémoire | **U004/U043** TradingAgents : sections README de mémoire/reprise et extrait du parseur de rating ; **U005–U008**, **U130–U135/U144** résumés/intros selon registre | Motifs de spécialisation et mémoire ; aucun rendement repris comme preuve. Le parseur de rating accepte un vocabulaire et peut retourner absence de rating : il ne vérifie pas une recommandation. Mémoire d’un rendement futur interdite dans un test antérieur. |
| POC financiers | **U136** AI Hedge Fund README ; **U139** article praticien ; **U137/U138** métadonnées/introduction de licence/README | Catalogue d’outils et données, non produit prêt à intégrer. Vérifier chaque route d’API, dépense, droit sur les données ; aucun accès direct aux API de ces exemples utilisé. |
| Frameworks voisins | **U256–U259/U262/U263**, introductions/métadonnées ; **U370/U371**, pages de portail | AutoGen, Microsoft Agent Framework, AG2, CrewAI, PydanticAI, smolagents : ne pas multiplier les candidats sans une capacité manquante démontrée. Pydantic peut valider une forme sans valider une vérité. Un portail dont le code d’exemple emploie un autre fournisseur ne prouve pas l’accès Bedrock. |
| SDK OpenAI et traces | **U260/U261** métadonnées ; [documentation officielle tracing](https://developers.openai.com/api/docs/guides/agents/integrations-observability), sections SDK/observabilité lues | Les SDK serveur ont un tracing activé par défaut dans le cas courant documenté. L’utilisation d’un autre fournisseur ou d’un wrapper ne suffit pas à garantir l’absence d’export de traces. Configurer et vérifier séparément inférence, évaluation et télémétrie avant tout usage. Aucun SDK OpenAI installé pour cette sous-mission. |
| Observabilité / évaluation | **U264–U271**, notices/introductions selon registre | OpenTelemetry donne un vocabulaire de spans ; Langfuse/Phoenix des infrastructures ; Inspect/Promptfoo/DeepEval des cadres de tests. Aucun ne crée l’oracle financier. Destinations, licences et évaluateurs auxiliaires non audités complètement ; aucun déploiement. |
| Guides industriels | **U014**, passages architecture/budget/évaluation ; **U063/U351**, définitions et motifs ; **U064**, contexte ; **U352**, compaction/mémoire ; **U353**, générateur/évaluateur et contrat de sprint | Les conseils éclairent des mécanismes mais ne sont pas des comparaisons contrôlées transférables. Anthropic U014 attribue une grande partie du gain à plus de tokens et signale un coût élevé. U064 réclame un contexte partagé ; U352 propose aussi des contextes séparés. Résoudre la tension par documents versionnés + références consultables, pas par copie aveugle de toutes les traces. |

## Ressources AWS, données locales et 36 captures de l’atelier

L’atlas `revision_2026-11-15/00B_ATLAS_DES_RESSOURCES_ET_PLAN_EXPLOITATION.md`, catalogue F01–F36, a été lu. Le tableau suivant décrit **ce catalogue**, sans prétendre à une lecture intégrale de chacun des 36 PDF. Le notebook extrait a été inspecté au moins à sa cellule 23 : il indique explicitement « Claude Sonnet 5.5 et Haiku 5.5 ne sont pas disponibles dans les comptes du Datathon ». Cela contredit la recommandation canadienne du dossier si elle est traitée comme un choix actuellement disponible ; ce n’est pas un nouvel essai d’accès à ces modèles.

| Famille et captures | Fonction potentielle | Accès réellement établi pour AlphaForge |
|---|---|---|
| Accès, règles, modèle, SDK : **F01/F02/F03/F06/F07/F10/F11/F16/F17/F20/F27/F31/F35/F36** | Identité temporaire, région, route d’inférence, outils locaux et livraison | STS/profil vérifiés dans note 01, route déclarative des quatre sessions, anciennes inférences produit avec request IDs. Claude Code, Kiro et autres modèles non invoqués ici. |
| Développement et formation : **F08/F19/F29/F32/F33** | Exigences, contrats, parcours pédagogiques, cours | Documents et liens accessibles localement ; ni inscription, ni crédits, ni capacité de modèle démontrés par leur présence. Les 134 liens supplémentaires U372–U505 sont collectés par la racine, pas tous lus par cet agent. |
| Données et documents : **F05/F15/F18/F21/F24/F26/F30** | S3, Athena, Glue, extraction, RAG, données financières publiques | Fichiers starter locaux identifiés. Aucun nouveau bucket, crawl, ingestion, embedding ou requête Athena. La lecture HTTP/PDF actuelle suffit au corpus de recherche ; services non testés. |
| Agents et contrôle : **F13/F14/F22/F23/F25/F28** | Guardrails, graphe, outils, mémoire, MCP, AgentCore | Une recherche AgentCore directe testée ; aucun Gateway/Memory/Code Interpreter/Browser/Guardrail créé ou invoqué. Strands inspecté statiquement. |
| Exécution et restitution : **F04/F09/F12/F34** | Notebook/SageMaker, Lambda, Amazon Quick, hébergement | Notebook lu localement, pas exécuté. La démonstration reste sur Mac. Aucun droit d’exécution de ces services prouvé dans cette sous-mission. |

Les fichiers locaux du projet identifiés sont `data/Datathon_Case_Officiel_2026_FR.md`, `data/alphaforge_starter/{assets_universe,prices_daily,sources_metadata,macro_rates,corporate_actions,fx_usdcad_daily}.csv`, son README et ses avertissements de qualité. Leur présence ne valide ni ajustements, ni couverture, ni point-in-time ; l’analyse financière en examine les limites séparément.

`docs/aws-runtime.md`, section « Hébergement et préservation », rapporte l’inventaire antérieur : zéro bucket S3 et aucune Lambda AlphaForge. Ce constat n’a pas été rafraîchi ici, et aucun bucket du projet connu ne justifiait une exploration de données supplémentaires. Les plafonds de quotas du compte n’ont pas été interrogés : les pages **U111/U315/U326/U116** sont des documentations, pas les quotas effectifs. Un appel court réussi ne démontre pas la capacité d’une charge longue ou parallèle.

Preuve d’invocation antérieure conservée : `artifacts/ui-export.json`, section `agent.calls`, modèle `global.openai.gpt-6-astra`, région `us-east-1`, requêtes `135b729e-1f49-498b-a707-f76f83f8af59` et `37969d33-6b5f-4819-b85c-ad6068d7823e`, arrêts `tool_use` puis `end_turn`. Ces traces produit prouvent une invocation antérieure et évitent un test redondant ; elles ne prouvent pas l’existence de quatre rôles produit ni d’une recherche web dans cette version. L’export décrit au contraire des fiches documentaires locales.

## Conséquences pour le chemin AWS

**U038** documente Step Functions Standard et Express. Les passages d’exécution ont été lus : Standard distingue ses garanties et retries ; Express asynchrone est at-least-once et synchrone at-most-once. Écrire simplement « Express est at-least-once » omet cette distinction. Ces garanties d’orchestrateur ne suppriment pas les questions d’idempotence des outils, de persistance de leurs résultats ou de vérité métier.

La trajectoire proposée est : contrats et preuves d’abord, orchestration locale révisable, inférence AWS existante, recherche documentaire AWS maintenant démontrée. Runtime, stockage distant, suivi centralisé et protection avancée sont des options à évaluer sur un besoin et une expérience définis. Cette trajectoire ne plafonne pas l’ambition des quatre agents ; elle évite de compter des services non configurés comme des fonctionnalités présentes.
