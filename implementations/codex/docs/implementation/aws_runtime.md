# Runtime et recherche documentaires — construction Prompt 4

État du 15 novembre 2026. Fichiers : `alphaforge_app/decision/workflow.py`,
`alphaforge_app/decision/research.py`, leurs tests et
`scripts/qualify_decision_runtime.py`. Aucun service cloud déployé.

## Choix et qualification du moteur

**LangGraph 1.2.22 avec langgraph-checkpoint-sqlite 3.1.3 est retenu pour
l’intégration locale.** La [qualification exécutée](proofs/runtime_qualification.json)
compare une petite machine explicite et LangGraph sur le même scénario :
Agent0 → Agent1 → erreur Agent2, fermeture de l’instance, réouverture du
checkpoint SQLite et reprise Agent2 → Agent3. Les deux réussissent. Une attente
humaine reste une attente après `resume` et ne réexécute pas le rôle.

Les durées observées, 29 ms et 9 ms dans cet essai sans modèle ni outil réseau,
ne constituent pas un benchmark de performance. Le choix LangGraph conserve
les mécanismes de graphe/checkpoint de la bibliothèque tout en isolant le
contrat du dossier. La machine de référence appartient uniquement au script
de qualification ; il n’existe pas deux moteurs produit à maintenir.
Strands reste une alternative documentée lors du Prompt 3, **non installée et
non exécutée dans cette comparaison**.

Les six tests `test_decision_workflow.py` couvrent aussi :

- panne après commit du dossier mais avant checkpoint, avec retour sauvegardé
  et un seul effet métier par tâche ;
- cycle Agent2 → Agent1 → Agent2 avec compteurs distincts et budget borné ;
- conflit de réutilisation d’un identifiant de run avec d’autres entrées ;
- télémétrie LangSmith désactivée même si ses variables d’environnement
  d’activation sont héritées.

Ces tests ont passé. Les huit tests de recherche passent également ; la
[dernière sortie ciblée](proofs/targeted_checks.json) conserve cette vérification
et la comparaison. La qualification ne démontre pas une reprise distribuée
entre plusieurs processus concurrents, une résistance à une coupure électrique
ou la réussite du parcours utilisateur complet ; ce dernier relève de
l’intégration du service et du noyau.

## API d’intégration

```python
workflow = DecisionWorkflow(
    checkpoint_path,
    role_callback,          # (role: str, state: dict) -> dict
    max_transitions=24,
)
workflow.run(run_id, {"dossier_id": dossier_id, "step_index": 0,
                      "next_role": "agent0", "status": "running"})
workflow.inspect(run_id)
workflow.resume(run_id)
```

Le callback reçoit l’un des quatre rôles. Il applique le protocole du noyau :
`task_id = run_id + ":" + step_index`, lecture des entrées observées,
opérations autorisées, commit et sauvegarde du retour dans une transaction.
Il rend `step_index + 1`, `status`, `next_role`, les références et la révision.
Lors d’une reprise d’une tâche déjà commise, il rend le retour sauvegardé.
Le workflow ne lit ni ne modifie les tables du dossier.

`run` ne remplace jamais les entrées d’un run existant. `resume` relance
uniquement les nœuds encore en attente après échec ; les états `complete`,
`waiting` et `cancelled` restent inchangés. Une clarification utilisateur
crée normalement un nouveau run dans le service. L’option interne
`resume_state` exige un `resume_event_ref` préalablement validé par le noyau ;
elle ne doit jamais recevoir directement le corps d’une requête HTTP.

Une exception est rendue avec `status=error`, `current_role`, un code et les
métadonnées d’erreur disponibles ; elle reste inspectable après fermeture de
l’instance. Les erreurs Bedrock structurées conservent leur identifiant de
requête. Les limites de transitions sont cumulatives dans le run. Le service
reste responsable de la propagation de cet état dans le dossier et de la
conservation des tentatives d’outils.

Chaque run est verrouillé dans l’instance locale. Les verrous d’une instance
ne constituent pas des leases distribués ; un déploiement avec plusieurs
workers doit qualifier ce point avant d’être activé.

## Route et preuve AWS

Route conservée : profil `alphaforge`, compte `471112821226`, région d’entrée
`us-east-1`, modèle `global.openai.gpt-6-astra`, service Bedrock Runtime.
Le test du 15 novembre est enregistré dans
[aws_connection.json](proofs/aws_connection.json) :

| Action réelle | Résultat | Identifiant AWS |
|---|---|---|
| STS GetCallerIdentity | Compte attendu, rôle WSParticipantRole | `4623e89d-441e-46ed-9bc2-81e4d0f68bfc` |
| GetInferenceProfile | Profil Astra ACTIVE | `e830f02d-a4ab-4e44-98e8-965cfbed2279` |
| Converse, schéma JSON strict | `{"connected":true}`, `end_turn`, 63 tokens, 1 119 ms client | `939fa3c6-447c-46a3-9cb9-8362c9a3d1cf` |
| AgentCore InvokeWebSearch | Trois résultats, sans WebAnswer | `06737a2b-bef7-4587-a53b-9bbd93b5679b` |

Le profil global et la région d’entrée ne prouvent pas le pays physique
d’exécution. La petite invocation utilise un effort faible pour un simple
test de connexion ; elle ne change pas la configuration des rôles produit.
Aucun modèle auxiliaire ni service de réponse opaque n’est appelé par la
recherche ou le workflow.

LangGraph est utilisé comme graphe local, sans modèle LangChain ni service
LangGraph hébergé. `tracing_context(enabled=False)` et une liste vide de
callbacks bornent les invocations et lectures de checkpoints. La présence
de `langsmith` parmi les dépendances installées n’est pas présentée comme
une connexion ou un export autorisé.

## Recherche, citations et dates

```python
research(problem, *, query=None, allow_web=True)
# evidence, methods, gaps, contradictions, receipts, limitations
```

Le corpus local sélectionné comprend, selon la question, les documents
CFA, les textes sur diversification/optimisation, la documentation de change,
le chapitre 4.3 de Boyd et Vandenberghe, la CVaR et la documentation HiGHS.
Ce petit index reste une aide de sélection, pas la limite des sujets admis :
la requête documentaire peut être différente et la recherche AWS reste ouverte
aux sources externes pertinentes.

Pour chaque source locale, les octets originaux sont relus et leur SHA-256
comparé à la capture du Prompt 2. Le texte est réextrait de ces octets :
un fichier texte voisin ne devient pas une citation authentifiée par son
seul emplacement. Les passages retenus sont des fenêtres textuelles exactes,
avec lignes, empreinte du texte et chemin de capture. Pour Boyd, les pages PDF
160 à 166 couvrent le chapitre de programmation linéaire. Le résultat distingue
`targeted_passages` et `extracted_for_role_review` : le choix de fenêtres par
code n’est pas une revue critique effectuée par un modèle.

La recherche réseau vérifie STS avant `InvokeWebSearch`. Un reçu contient
requête, bornes, compte, région, identifiant AWS et résultats. Les snippets
restent dans les reçus ; seul un document récupéré et lisible peut produire
une pièce documentaire. HTTPS public, redirections revalidées, absence
d’identifiants/cookies fournis, taille maximale de 10 Mio et PDF borné à
60 pages encadrent la récupération. L’extraction ne fait pas d’OCR.

`known_at` est la date de capture de la version exacte, distincte d’une date
déclarée dans un index ou dans les métadonnées du document. Avec
`knowledge_date`, les captures ultérieures sont exclues et une recherche
actuelle est suspendue pour une date passée. Ce choix conservateur peut
écarter un article ancien dont seule une capture récente est disponible :
il faut alors une version historiquement vérifiable, et non rétrodatée par
le titre ou l’année de publication.

Les statuts d’autorité distinguent document institutionnel, texte primaire
hébergé par l’auteur, registre bibliographique/résumé, dépôt logiciel et
encyclopédie secondaire. Aucun de ces statuts ne démontre à lui seul
l’applicabilité. Les divergences de dates et les conclusions empiriques
différentes sont signalées avec leur portée, sans résolution par vote.

## Essais réels et défauts conservés

La [recherche réelle](proofs/research_live.json) a trouvé puis capturé deux pages
CDIC et une page Wikipédia. L’opérateur `site:cdic.ca` placé dans la chaîne
n’a pas suffi à exclure la troisième. Le code a donc été corrigé : les opérateurs
de domaine deviennent un filtre `domainFilter.include` de l’API, et les URLs
retournées sont contrôlées avant capture. Le test de ce correctif est local ;
aucun second appel AWS n’a été présenté comme preuve du filtre corrigé.

L’extraction initiale du PDF Boyd a averti que fontTools manquait pour
certaines polices. La dépendance a été ajoutée et une
[nouvelle extraction locale](proofs/research_local.json) conserve les passages
après correction, sans nouvel appel AWS. L’ancienne preuve n’est pas effacée.

La recherche conserve explicitement la lacune « instrument de réserve réel
non qualifié », même lorsque la CDIC décrit ses règles générales. Ces pages
ne prouvent ni les conditions d’un instrument particulier, ni la protection
de ZST, ni sa disponibilité à l’échéance. Aucun score ESG n’est inventé.

Versions ajoutées pour ce sous-ensemble : `langgraph==1.2.22`,
`langgraph-checkpoint-sqlite==3.1.3`, `beautifulsoup4==4.15.0`,
`fonttools==4.68.0`. `pypdf==7.1.0`, déjà présent, est conservé.
Les versions transitives figurent dans la preuve de qualification.

Pour reproduire la qualification locale, utiliser
`.venv/bin/python scripts/qualify_decision_runtime.py`.
Le drapeau `--aws` déclenche explicitement une nouvelle petite inférence et
une recherche AWS ; il n’est pas nécessaire pour relire les preuves existantes.

## Revue indépendante de l’intégration du service

La revue de `service.py` et de son API a produit huit tests dans
`tests/test_decision_service_review.py`. Le premier passage, limité aux six
premiers tests, a donné **un succès et cinq échecs** : les défauts n’ont donc
pas été déduits seulement d’une lecture. L’intégrateur les a corrigés dans
le service ; deux autres contrats ont été ajoutés après la lecture de la
sélection des méthodes et des dépendances documentaires.

La [vérification après correction](proofs/service_review_checks.json) donne
**8 tests réussis en 0,62 s**. Ils injectent explicitement un faux modèle,
une recherche documentaire de test et un calcul de test. Ils ne prouvent
ni la qualité d’une réponse modèle réelle, ni un nouveau parcours UI, ni
une nouvelle invocation AWS.

| Contrat vérifié | Défaut initial ou risque couvert | Résultat après correction |
|---|---|---|
| Quatre rôles distincts | Risque de confondre quatre noms avec quatre exécutions | Quatre appels séparés au faux modèle, quatre tâches commises et entrées observées enregistrées ; aucune acceptation humaine inventée |
| Erreur et reprise | Le niveau run perdait le code AWS et l’identifiant de requête en réemballant l’exception | `ExpiredToken` et l’identifiant restent présents ; la reprise rejoue seulement Agent2 puis Agent3 et conserve la tentative échouée |
| Décision de clarification | Agent2 demandait une clarification mais l’outil financier était quand même appelé | Zéro appel `finance.analyze`, état final `waiting` |
| Approfondissement | La décision `deepen` d’Agent1 n’entraînait pas de nouvelle recherche | Une recherche supplémentaire est exécutée et capturée ; son budget est borné, avec un plan et une pièce distincts |
| Extraction imbriquée | Des poids inventés étaient adoptés lorsque la citation ne contenait aucun nombre | Le poids non cité est refusé et une clarification est conservée |
| Lecture locale | Construire le service déclenchait STS, rendant la lecture locale dépendante de credentials valides | Le client Bedrock est créé au premier besoin d’inférence ; l’ouverture du magasin local ne l’instancie pas |
| Méthode documentaire | Un identifiant de méthode absent des résultats pouvait être conservé | La sélection est filtrée contre les méthodes réellement présentes |
| Révision du sujet | Une explication pouvait rechercher un libellé générique et réutiliser ses documents après changement de sujet | La question réelle est transmise ; passer de CVaR à Sharpe produit une nouvelle version de la recherche |

Les `read_set` testés couvrent les artefacts transmis aux rôles et les
résultats documentaires réellement présents dans le contexte d’Agent1.
La dépendance au problème entier pour une demande d’explication est
conservatrice : elle peut provoquer une recherche supplémentaire, mais
évite de déclarer indépendante une capture dépendant de la question.
La preuve de reprise après fermeture du moteur et celle de la panne
commit–checkpoint restent les tests de workflow décrits plus haut ; le
test de service couvre ici une reprise dans la même instance.

La présence d’un nombre dans un extrait n’établit pas à elle seule sa
bonne affectation à un actif, une unité ou une échéance. Le test
d’extraction garantit le rejet du cas reproduit ; il ne démontre pas une
interprétation sémantique parfaite de toute phrase. Les méthodes retenues
par Agent1 restent des candidats documentaires, et non des algorithmes
admis automatiquement à l’exécution.

Commande locale : `.venv/bin/python -m pytest -q tests/test_decision_service_review.py`.
Les treize avertissements observés concernent une dépréciation Python
dans une dépendance LangSmith ; ils ne signalent pas une exportation de
traces. La désactivation de cette télémétrie est vérifiée séparément par
le test du workflow.
