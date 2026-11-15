# Contrat d’intégration de construction

Contrat interne réversible, subordonné aux documents de conception.

## Objet financier normalisé

`ProblemSpec` est sérialisable en JSON. Un champ absent reste `null` ou
une liste vide ; aucune valeur métier implicite ne remplace une déclaration.

```text
decision_type: reserve_allocation | historical_comparison | explanation | unsupported
question: str
currency: CAD
capital_cad: float | null
holdings: [{ticker: str, weight: float}]
withdrawal_cad: float | null
withdrawal_months: float | null
horizon_years: float | null
max_asset_weights: {ticker: float}
scenario_loss_limit_cad: float | null
scenarios: [{id, label, returns: {ticker: float}, kind: hypothetical,
             horizon_months: float}]
objective: minimize_reallocated_capital | compare_historical | explain | unknown
comparison: {ticker: str, target_weight: float} | null
reserve_policy: abstract_nominal | real_instrument_unknown | null
knowledge_date: YYYY-MM-DD | null
assumptions: [{id: str, text: str, origin: assumed | declared}]
unknowns: [str]
clarifications: [{field: str, question: str, blocking: bool}]
```

Les assertions de provenance sont conservées séparément par le dossier.
Les exemples préremplis fournissent **des entrées et hypothèses explicites**,
jamais des sorties de l’exemple JSON du Prompt 3.

## Finance — interface Python

`analyze(problem: dict) -> dict` : retourne `status` (`complete`, `conditional`,
`missing_input`, `unsupported`, `infeasible`, `error`), `method`, `inputs`,
`options`, `checks`, `claims`, `limitations`, `missing`, `provenance`.

`method` contient identifiant/version, source(s), hypothèses, domaine.
Chaque option contient `id`, `label`, `weights`, `metrics` avec unités explicites.
Les claims numériques sont produits par code et référencent leurs champs
de résultat ; aucune conclusion modèle n’est recopiée dans le calcul.

`examples() -> list[dict]` fournit `id`, `title`, `prompt`, `facts` et
`suggested_revision` facultatif. Le second exemple utilise une comparaison
historique différente du LP de réserve.

## Recherche — interface Python

`research(problem: dict, *, query: str | None = None, allow_web: bool = True)
 -> dict` : retourne `evidence`, `methods`, `gaps`, `contradictions`, `receipts`,
`limitations`. Captures locales avec provenance ; recherche AWS lorsque permise.
Les reçus ne prouvent que l’action réalisée. Aucun modèle auxiliaire hors AWS.
Les pièces documentaires doivent préciser `known_at`, `reading_level`, source,
passage, portée et limites ; filtrage `knowledge_date`.

## Exécution — interface Python

Le moteur reçoit des callbacks de rôles qui appliquent les contrats et commits.
Le dossier SQLite fait autorité, le checkpoint ne remplace pas ses révisions.
L’API qualifiée est `DecisionWorkflow(path, role_callback, max_transitions=24)`,
avec `run(run_id, initial_state)`, `resume(run_id)`, `inspect(run_id)` et `close()`.
Le callback retourne un état dont le compteur d'étapes a augmenté d'une unité.
Son retour est sauvegardé dans la transaction métier, avant le checkpoint.

## API locale à fournir à l’interface

- `GET /api/dossiers/examples` → `{examples: [...]}`.
- `GET /api/dossiers` → `{dossiers: [...]}`.
- `POST /api/dossiers` corps `{prompt, facts: {}, use_ai: true}` → dossier et run.
- `GET /api/dossiers/{id}` → instantané complet décrit ci-dessous.
- `POST /api/dossiers/{id}/revise` corps `{message, changes: {}, intent: "replace"|"variant",
  base_revision: int}` → nouvel instantané/run ; remplacement explicite par défaut.
- `POST /api/dossiers/{id}/resume` → reprise persistante sans recommencer les étapes
  déjà commises.
- `GET /api/dossiers/{id}/export` → JSON du dossier.
- `GET /api/dossiers/{id}/artifacts/{artifact_id}/{version}` → pièce avec contenu.
- `POST /api/dossiers/{id}/display` corps `{view_ref}` → événement d’affichage
  seulement, jamais d’accord.

Instantané :
```text
id, title, revision, status, active_problem, current_analysis, current_view,
artifacts [{id, version, type, owner, content, input_refs, usable, hash}],
questions [], evidence [], events [], tasks [], attempts [],
runs [{id,status,error,current_role}], revisions [],
comparison {before, after, changed_fields, invalidated, reused} | null,
route, limitations
```

L’interface doit tolérer les champs encore absents pendant l’exécution, montrer
les erreurs, actualiser par polling et ne pas présenter un résultat ancien
comme courant pendant la révision. Les détails de données restent inspectables
en JSON même si une carte spécialisée ne les représente pas.

## Contrats opérationnels des quatre rôles

| Rôle | Entrées réellement transmises | Transformation et sorties autorisées | Décisions et retours |
|---|---|---|---|
| Agent0 | Requête courante, faits utilisables, éventuel résultat incomplet et revue documentaire | `problem`, `qualification`, `fact.*` extraits avec citation/origine, `questions.agent0` | Distinguer problème admis/hors domaine, signaler contradictions ; attendre une clarification bloquante ou passer à Agent1. Une valeur structurée déclarée prime sur l'extraction. |
| Agent1 | Problème, faits de périmètre, pièces et plan documentaire encore valides | `research`, `research_review`, `research_plan`, `research.deepening`, `data_inspection`, `questions.agent1` | Sélection critique, calcul conditionnel, approfondissement réel borné ou retour Agent0. Pièce introuvable/non datable = lacune explicite. |
| Agent2 | Problème, revue et méthodes sourcées, inspection de données, quatre faits du diagnostic initial et diagnostic encore valide | `baseline_stress`, `analysis`, `analysis_review`, `questions.agent2` | Choisir un outil admis ou une clarification. Outil fixe, résultats et contrôles ; absence de données = `missing_input`, hors domaine = `unsupported`. Agent3 rend la limite puis retourne à Agent0 si nécessaire. |
| Agent3 | Problème, analyse, contrôles, preuves et inspection | `view`, `questions.agent3` | Ordonner les identifiants de claims, choisir accent/détail et suivi. Aucun nouveau montant ni conseil libre. La correction humaine revient par un événement versionné vers Agent0. |

Les outils d'Agent1 sont `research.retrieve`, `research.deepen` et
`inputs.inspect`. Agent2 utilise `finance.analyze` et `finance.baseline_stress`.
Chaque rôle utilise une sortie JSON Bedrock propre à sa mission. Les paramètres,
réponses, tentatives et identifiants AWS sont conservés. Le noyau applique les
droits même si une réponse d'agent propose une autre écriture.

Le contrôle de présence lexicale des nombres et symboles dans une citation
empêche certains ajouts arbitraires ; il ne certifie pas toute interprétation
sémantique. Toute hypothèse issue de l'interprétation reste distinguée d'une
déclaration. Une clarification bloquante interdit une allocation courante.

## Deux branches indépendantes effectivement matérialisées

`baseline_stress(projected_inputs)` lit **seulement** `capital_cad`, `holdings`,
`scenarios`, `currency`. Son artefact dépend de leurs versions. Changer le
retrait conserve son contenu et sa version ; changer le capital ou un choc
l'invalide. Il calcule les pertes initiales, jamais l'admissibilité au retrait.
L'analyse principale confronte ses pertes initiales à ce diagnostic conservé.

`inputs.inspect(scope)` lit l'univers, les prix, le change et leurs métadonnées
réels. Il produit `data_manifest`, des captures de documentation technique et
la portée du calcul admis. Agent2 vérifie les hashes, lignes et dates de ce
manifeste contre ses propres données. Une inspection réussie ne rend pas
admissibles des données acquises après la date de connaissance.

## Enveloppe du commit

```text
ChangeSet {
  run_id, task_id, role,
  read_set: [id@version effectivement transmis],
  writes: [{id, type, content, input_refs}],
  next_role, status: running|waiting|complete, reason
}
```

Les références `$id` ne désignent qu'une sortie antérieure dans le même commit.
Le magasin les résout atomiquement vers `id@version`. Les écritures sur un
run remplacé, un `read_set` modifié, une version périmée ou une dépendance non
observée sont refusées. Une correction invalide ses descendants et la vue
avant le lancement du nouveau run ; une variante crée un dossier séparé.
