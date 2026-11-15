# Revue indépendante de l’agent AlphaForge

Revue effectuée le 15 novembre 2026 par le sous-agent AWS. Périmètre :
`alphaforge_app/main.py`, `orchestrator.py`, leur intégration avec le client
`bedrock.py`, les erreurs et l’intégrité du résultat exporté. Le moteur financier
fait l’objet d’une vérification séparée. Aucun déploiement ni ressource AWS
supplémentaire n’a été créé.

## Parcours réellement exécuté

L’appel Python `analyze(AnalyzeRequest(..., persona="robert", use_ai=True))`
a utilisé les avoirs, la demande et les paramètres du persona Robert. Il a abouti
en 7 593 ms, avec `mode="bedrock"` et `agent.status="success"`, sans erreur
d’outil.

Preuve locale :
[`d6d157907ce9446d8d396a04ca9898c6`](../examples/robert-bedrock.json),
créée à `2026-11-15T12:00:09.339707+00:00`.

Le modèle `global.openai.gpt-6-astra` a appelé `compare_scenario` pour tester TSLA
à 5 %, `read_evidence` pour les sources `method`, `case`, `cfa`, puis
`inspect_profile`. Le second appel a produit une conclusion structurée à partir
des résultats d’outils.

| Étape AWS | Request ID | Durée client | Usage retourné |
| --- | --- | ---: | --- |
| Choix des outils | `a86e5872-89c2-4808-bd59-87467f677375` | 1 402 ms | 1 035 entrées, 77 sorties |
| Conclusion JSON | `c8a02474-1dd6-496b-9490-97738ff02b36` | 5 483 ms | 2 entrées, 382 sorties, 3 226 écritures de cache |

Ces appels ont emprunté le client SigV4 Bedrock, avec le profil `alphaforge`,
l’entrée régionale `us-east-1` et le compte d’événement vérifié
`471112821226`. La configuration et ses limites sont documentées dans
[`aws-runtime.md`](aws-runtime.md).

Le récit explique correctement que la réduction de l’exposition atténue la baisse
maximale dans le rejeu historique : le moteur a obtenu −23,396233 % pour le
portefeuille initial et −11,324237 % pour la variante. Il ne transforme pas le
repère de confort en garantie de perte future, et ne présente pas l’horizon du
profil comme une prévision. Les trois observations affichées (`focus`, `comfort`,
`horizon`) sont copiées depuis le moteur. Les questions portent sur les retraits
et la capacité de perte. Aucune contradiction personnelle n’a été inventée dans
cette exécution.

Ce test exerce directement la fonction de service et la sérialisation de
l’export. Il ne constitue pas un test de navigateur ni une mesure de disponibilité
future de la session AWS.

## Validation intégrée d’Amira et de Mateo

Chaque demande complète a été exécutée une fois avec `AnalyzeRequest(use_ai=True)`
et les paramètres de son persona, le 15 novembre 2026 à partir de 12:04:32 UTC.
Les deux parcours ont abouti avec `mode="bedrock"`, `agent.status="success"` et
aucune erreur d’outil. Le même modèle AWS et le même compte que pour Robert ont
été utilisés.

| Persona | Rapport conservé | Durée totale | Variante vérifiée | Usage total retourné |
| --- | --- | ---: | --- | ---: |
| Amira | [`64ab0560c7ac48f48545c2fa5ef8d78f`](../examples/amira-bedrock.json) | 11 651 ms | NVDA de 30 % à 10 % | 4 401 tokens |
| Mateo | [`ca7457a4bca74059ab1dac66a7274598`](../examples/mateo-bedrock.json) | 11 575 ms | XOM de 10 % à 0 % | 4 837 tokens |

| Persona et étape | Request ID AWS | Durée client | Usage retourné |
| --- | --- | ---: | --- |
| Amira, outils | `75913163-cf78-49da-976d-8e979de69fc2` | 1 268 ms | 1 025 entrées, 63 sorties |
| Amira, conclusion | `63ef38a9-1529-4e93-ab99-60f81c82b4c2` | 7 546 ms | 2 entrées, 441 sorties, 2 870 écritures de cache |
| Mateo, outils | `e188b824-c298-4629-91dd-8505edb41588` | 1 680 ms | 1 032 entrées, 77 sorties |
| Mateo, conclusion | `a0ac7c1d-9782-419d-b2af-b0225ecff23a` | 7 072 ms | 2 entrées, 527 sorties, 3 199 écritures de cache |

Les totaux incluent les tokens de cache retournés par AWS ; ils ne sont pas une
estimation de facture.

Amira a utilisé `compare_scenario` et `read_evidence`, avec les fiches `method`
et `cfa`. Son récit explique que la réduction de NVIDIA atténue la baisse
historique, mais laisse celle-ci au-delà du repère de confort, tout en augmentant
proportionnellement les autres positions, dont les cryptoactifs. Il ne promet ni
diversification ni rendement futur.

Mateo a utilisé `compare_scenario`, `read_evidence` et `inspect_profile`, avec les
fiches `method`, `cfa` et `case`. Son récit distingue correctement l’exclusion
directe d’Exxon de la preuve sur les avoirs indirects et les critères ESG. Il
indique que la baisse historique est plus forte après exclusion, sans en déduire
une inadéquation certaine. Il explique explicitement que l’absence documentaire
ne prouve ni acceptabilité ni non-conformité ESG.

| Mesure calculée | Amira, référence → variante | Mateo, référence → variante |
| --- | --- | --- |
| Valeur finale en CAD, capital fictif initial de 10 000 CAD | 31 266,18 → 22 395,29 | 17 772,24 → 15 804,05 |
| Rendement cumulé historique | 212,661783 % → 123,952895 % | 77,722433 % → 58,040465 % |
| Baisse maximale historique | −44,642436 % → −39,517028 % | −12,678804 % → −18,568820 % |
| Repère de confort déclaré | 35 % : toujours dépassé | 20 % : non dépassé |

Un contrôle sans nouvel appel AWS a relu chaque export, recalculé ses paramètres
avec le moteur et comparé exactement les objets `comparison` et `scenarios`.
Les deux égalités ont réussi. Chaque observation sélectionnée est identique à
l’observation déterministe correspondante et ses sources sont présentes dans le
rapport. Le ticker et le poids affichés correspondent au portefeuille calculé.

Les deux conclusions ont sélectionné `focus`, `comfort` et `horizon`. Le texte
de Mateo explique la limite ESG, mais l’observation déterministe dédiée `esg`
n’a pas été sélectionnée par le modèle dans cette exécution. Les chiffres restent
dans les observations et les métriques ; les champs de prose sont qualitatifs.
Les deux listes de contradictions sont vides, sans contradiction personnelle
inventée.

## Incident réel dans l’interface et correction de la restitution

Un essai ultérieur de Mateo depuis l’interface, à
`2026-11-15T12:08:37.479322+00:00`, a échoué lors de la validation locale après
deux réponses AWS. Le rapport
[`b7560fc5e1f547e69354c16bdde1b41b`](../examples/incident-mateo.json)
est conservé avec `mode="calculation"`, `agent.status="error"` et les calculs
locaux. Les outils de comparaison, de lecture et d’examen du profil avaient
réussi.

Les requêtes AWS étaient `b518c670-1156-415b-8560-5383e1127818` pour les outils
et `5197a9bc-129e-43e5-ae38-d02f40651b73` pour la restitution. La trace finale
enregistrait seulement `ValueError`, sans son message. Elle ne permet donc pas
de déterminer rétrospectivement si la conclusion avait demandé un nouvel outil
ou sélectionné un nombre ou un identifiant d’observations non accepté.

La revue a identifié deux faiblesses du contrat : la liste des observations
n’était pas contrainte dans le schéma envoyé au modèle, et le dernier appel
possédait encore les outils malgré l’attente d’une conclusion JSON. Le
propriétaire de l’orchestrateur a :

- borné le schéma à trois à cinq identifiants parmi les observations existantes ;
- créé un contexte final contenant le dossier vérifié, sans historique d’outil
  ni outil disponible ;
- conservé les erreurs d’outils dans ce dossier, et enrichi les diagnostics avec
  la raison locale, `stop_reason` et les noms d’outils demandés.

Une seule nouvelle exécution réelle de Mateo a vérifié cette correction :
[`5c026e09c0f0489b92879d74323b3b61`](../examples/mateo-corrige.json),
créée à `2026-11-15T12:10:46.417542+00:00`. Elle a réussi en 11 909 ms, avec
4 339 tokens retournés au total et aucune erreur d’outil.

| Étape corrigée | Request ID AWS | Durée client | Usage retourné | Fin |
| --- | --- | ---: | --- | --- |
| Planification | `8970fb14-de6b-4636-a5ac-664187cb001e` | 1 719 ms | 1 032 entrées, 77 sorties | `tool_use` |
| Restitution | `3ba3b21a-4e3b-41da-a402-edd8c6655d52` | 7 508 ms | 2 entrées, 548 sorties, 2 680 écritures de cache | `end_turn` |

Le dernier appel ne demande aucun outil. Les trois observations sélectionnées
sont valides, distinctes et identiques à celles du moteur. Les comparaisons et
scénarios exportés correspondent exactement à un recalcul des mêmes paramètres.
Le récit reste qualitatif et distingue l’exclusion directe d’Exxon des preuves
ESG manquantes. Cette exécution vérifie la fonction de service corrigée ; la
validation visuelle après redémarrage du serveur appartient à la revue de
l’interface.

## Défauts découverts et corrections vérifiées

La première exécution des tests d’erreur a détecté trois défauts : un échec
d’outil récupéré conservait le statut global `success` ; les champs de titre,
questions et conditions pouvaient afficher des chiffres rédigés par le modèle ;
une expiration AWS perdait son code et son identifiant de requête dans le
diagnostic public.

Le propriétaire de l’orchestrateur a corrigé ces points et ajouté une copie
transactionnelle du résultat. La revue a vérifié les comportements suivants :

| Cas injecté, sans inférence | Résultat observé |
| --- | --- |
| Calcul requis impossible | Arrêt après quatre tours, calcul local conservé, agent en erreur |
| Calcul valide suivi d’un outil invalide | Statut `partial`, erreur tracée et envoyée à Bedrock avec `is_error=True` |
| Chiffres générés dans les champs de texte | Suppression ou remplacement de ces champs ; chiffres du moteur conservés |
| Identifiant d’observation inconnu | Conclusion rejetée, résultat local conservé |
| Session AWS expirée | Calcul conservé ; code `ExpiredToken` et request ID accessibles |
| Variante TSLA à 90 % réussie, conclusion ensuite en erreur | Résultat affiché et exporté revenu à TSLA à 5 % ; tentative visible dans la trace |
| Lot de sept appels d’outils | Arrêt avant leur exécution ; aucun changement des hypothèses |
| Erreur au premier tour, calcul obtenu au second | Erreur transmise au prochain tour avec `is_error=True` ; restitution partielle |
| Sélection trop courte, trop longue ou contenant un identifiant inconnu | Conclusion rejetée et diagnostic local conservé |
| Passage de la planification à la restitution | Aucun outil ni historique d’outil transmis ; dossier d’erreurs conservé et trois observations exactes |

Validation finale :

```text
.venv/bin/python -m pytest -q tests/test_orchestrator.py
10 passed in 1.30s
```

La première série comportait sept tests réussis. Les modifications du contrat
de restitution ont justifié sa mise à jour et trois cas supplémentaires, puis
une nouvelle exécution ciblée. Ces tests emploient un faux client uniquement
pour rendre les erreurs reproductibles ; le calcul et l’export restent ceux de
l’application. Les parcours nominaux ci-dessus ont utilisé le service AWS réel.

## Renouvellement du profil AWS conservé en mémoire

Une revue finale a reproduit un défaut distinct, sans réseau : après lecture
d'identifiants statiques dans le profil `alphaforge`, une session boto3 existante
conservait les anciennes valeurs après renouvellement du fichier. Le cache du
client dans l'orchestrateur pouvait donc prolonger une erreur d'expiration.

La correction se limite à `bedrock.py`. Une erreur d'authentification invalide
la session et la connexion internes. La demande suivante relit le profil avec
une nouvelle session et revérifie le compte STS. L'objet conservé par
l'orchestrateur reste utilisable ; la demande échouée n'est pas rejouée.

Les tests de `test_bedrock_credentials.py` lisent un fichier temporaire via le
vrai SDK, mais remplacent entièrement les services réseau par des objets locaux.
Ils couvrent `ExpiredToken`, `ExpiredTokenException`, `InvalidClientTokenId`,
`UnrecognizedClientException` et le refus d'un profil renouvelé vers un autre
compte. Aucune vraie clé n'a été lue ou copiée dans ces fixtures et aucun appel
AWS n'a été effectué.

Validation ciblée après modification du client :

```text
.venv/bin/python -m pytest -q tests/test_bedrock_credentials.py tests/test_orchestrator.py
15 passed in 1.38s
```

## Limites du constat

Le garde de texte interdit les chiffres et symboles monétaires dans les champs
générés ; il ne démontre pas automatiquement la vérité de toute phrase
qualitative. Les sources sont des fiches documentaires qualifiées, sans recherche
web directe. Les identifiants d’observations et les chiffres du moteur demeurent
la preuve primaire.

L’orchestrateur limite le nombre de tours et le nombre d’outils. Son contrôle
temporel entre tours n’interrompt pas un appel réseau en cours ; le client possède
son propre délai réseau. Le délai logique n’est donc pas une garantie de temps
total maximal.

L’API expose désormais `partial` après une erreur d’outil récupérée. La revue de
l’interface doit conserver cette distinction et présenter une analyse partielle,
sans la transformer en succès global.
