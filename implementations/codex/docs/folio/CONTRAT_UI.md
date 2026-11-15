# Folio intégré — contrat de travail

Validation utilisateur acquise. Le prototype Folio et le produit sont sauvegardés dans `artifacts/folio_reference/`. Le moteur financier demeure inchangé.

## Responsabilités

- Racine : intégration, `main.py`, `static/folio/controller.js`, `static/folio/shared.js`, documentation et parcours navigateur.
- p6_recherche : `static/folio/index.html`, `render.js`, `style.css`, polices. Toute la composition Folio (lecture, comparaison, formulaires, bibliothèque, suivi, historique). Aucun backend.
- p6_donnees : `decision/folio_api.py`, `folio_projection.py`, tests dédiés et extensions minimales store/service nécessaires à l'idempotence. Aucun frontend/main.py.
- p6_audit : regard indépendant, tests navigateur, vérification AWS et scénarios réels, rapport. Aucun fichier des autres branches sans coordination.

## Frontend

`render.js` exporte `render(s)` (HTML) et importe les helpers de `./shared.js` : `esc, money, pct, options, allocation, revisionForm, versionSelect, delta, methodDetails, limits, proofButton`. Aucun montage automatique. `controller.js` monte `#app`, possède toutes les actions/états/asynchronismes, ouvre `#evidence` natif et remplit `#proof-content`.

État `s` :
- `v` : projection décrite ci-dessous, ou null en bibliothèque/nouveau dossier.
- `snapshot` : dossier brut (événements, tâches, artefacts), `archives` : révisions disponibles.
- `dossiers`, `examples` : GET existants ; `level`: accessible|deep ; `view`: library|new|profile|study|overview|compare|revise|history.
- `selected`: option id ; `preview`: aperçu local calculé sans agents ou null ; `previous`: projection avant aperçu ; `local`: bool ; `historical`: bool ; `historicalRevision`: number|null.
- `busy`: bool ; `busyLabel`: texte réel ; `error`, `notice`: textes ; `draft` : valeurs saisies ; `revisionIntent`: preview|variant|replace (preview défaut).
- `id`: dossier consulté ; `activeRevision`: révision courante connue ; `query`: recherche ; `pendingRequest`: requête conservée pour reprise.

Actions déléguées via data-action : `view` +data-view, `level` +data-level, `open` +data-id, `new`, `example` +data-example (index), `proof` +data-proof, `select` +data-option, `archive` +data-revision, `latest`, `undo` (aperçu local), `restore` (nouvelle correction rétablissant les entrées de la version consultée), `resume`, `retry`, `discard-draft`, `export` +data-format=json|html, `search`, `close-proof`.

Formulaires : `data-create` textarea name=prompt, textarea name=facts (JSON facultatif) ; `data-revision` champs financiers nommés comme ProblemSpec (capital_cad,withdrawal_cad,withdrawal_months,horizon_years,scenario_loss_limit_cad), tsla_cap en %, comparison_weight en %, holdings JSON et `message`, `intent` preview|variant|replace ; `data-search` input query. Les champs absents ne constituent pas des changements. Les objets complexes peuvent être modifiés via textarea name=advanced (JSON de changements). Profil et réviser partagent les opérations mais expliquent l'intention choisie. Ne jamais créer de valeurs financières par défaut silencieuses.

## Backend Folio (racine inclut router)

Préfixe `/api/folio` :
- GET `/dossiers/{id}?revision=N` → `{snapshot, version: v, archives}` ; sans revision = état actuel. Archives `{revision,status,label,created_at}`.
- POST `/dossiers` `{request_id,prompt,facts,use_ai:true}` → snapshot brut, HTTP202 ; idempotence durable de request_id + corps, conflit409 si réutilisé autrement.
- POST `/dossiers/{id}/revise` `{request_id,message,changes,base_revision,intent:variant|replace}` → snapshot brut HTTP202, idem.
- POST `/dossiers/{id}/preview` `{base_revision,changes}` → `{version:v, comparison, receipt}`. Calcul explicite sans inference, sans mutation du dossier ; entrée actuelle ou historique sélectionnée. Une absence de données n'est pas complétée arbitrairement.
- GET `/dossiers/{id}/export?revision=N` → état sélectionné complet et provenance.

La projection `v` suit le prototype (`prototype/prompt6/build_data.py`), mais dépend uniquement du dossier réel. Champs : id,label,revision,status,request,problem,facts,analysis,stats,claims,limits,proofs,agents,changes,source,controls,simple_reference. Les agents/événements historiques s'arrêtent à la date/révision regardée. `stats.min_reallocation_cad` et champs historiques issus des métriques réelles. `source` conserve dossier/revision/ref/hash, portée/archive/aperçu. `proofs` reprennent passages lus, pointeurs et contrôles, pas des citations inventées. La référence simple du dossier de défense est jointe uniquement si les entrées équivalent exactement au Robert r5 vérifié, avec attribution explicite. Le statut non résolu ne doit jamais afficher un ancien calcul comme actuel.

## Invariants

Les inférences suivent AWS convenu ; les aperçus déterministes l'indiquent et ne sont pas une analyse à quatre agents. Résultats historiques et scénarios sont séparés. Une correction crée une nouvelle version et ne détruit rien. Les préférences de lecture n'appellent ni agents ni calcul. Export = version regardée. Les détails techniques sont dans les preuves/suivi, pas le récit principal.
