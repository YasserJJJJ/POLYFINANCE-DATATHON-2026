# Contrat des données du prototype — version 1

**Statut : proposition de présentation, avant validation et intégration.**

Le prototype utilise des dossiers réellement exécutés au Prompt 5. Il ne
modifie ni leur stockage SQLite, ni leurs pièces, ni les sessions existantes.
Le code du produit reste inchangé. Le calcul exploratoire appelle le moteur
financier existant sur une copie des entrées, sans inférence et sans
orchestration d’agents.

## Ressources et démarrage

```sh
# Régénérer la projection depuis les exports archivés, sans calcul ni modèle
.venv/bin/python prototype/prompt6/build_data.py

# Servir uniquement le prototype local
.venv/bin/python -m uvicorn prototype.prompt6.server:app \
  --host 127.0.0.1 --port 8770
```

Le serveur charge `prototype/prompt6/data/cases.json`. L’interface peut aussi
lire ce fichier statique ; l’exploration exige le serveur Python. Aucun
service payant supplémentaire, bibliothèque de design distante ou modèle
externe n’est requis par cet adaptateur.

## Sources exécutées

| Cas du prototype | Export P5 | Révision | Portée |
|---|---|---:|---|
| Robert, retrait initial | `extracted-initial.json` | 5 | Retrait 30 000 CAD, budget de perte 15 000 CAD |
| Robert, retrait corrigé | `withdrawal_revision.json` | 10 | Retrait 40 000 CAD, mêmes positions initiales |
| Robert, risque corrigé | `profile_revision.json` | 15 | Retrait 40 000 CAD, budget de perte 1 000 CAD |
| Amira | `amira-initial.json` | 5 | Comparaison descriptive achat-conservation, CAD |
| Informations manquantes | `incomplete-initial.json` | 4 | Échéance extraite, pas d’allocation produite |
| Retrait impossible | `impossible-after.json` | 5 | Contradiction algébrique, déficit 20 000 CAD |

Ces exports résident dans `docs/defense/proofs/demo/`. Chaque version
projetée conserve leur chemin et SHA-256, l’identifiant du dossier, la
révision, le run, la référence et l’empreinte de l’analyse, ainsi que
l’horodatage enregistré. `data/manifest.json` réunit ces références.

La référence simple de Robert provient séparément de
`docs/defense/proofs/finance_review.json#/simple_reserve_reference`.
Elle n’est présente que dans **Robert r5**, et n’est pas décrite comme une
production d’agent. Ses contraintes et son horizon sont ceux de cet essai.
Elle atteint elle aussi le minimum de 30 000 CAD. L’adaptateur ne la prolonge
pas aux variantes.

## API de consultation

| Appel | Réponse |
|---|---|
| `GET /api/prototype/health` | Mode prototype, zéro inférence, mutations produit désactivées |
| `GET /api/prototype/cases` | Index des quatre dossiers, statut, nombre de versions, version initiale proposée |
| `GET /api/prototype/cases/{id}` | Toutes les versions de ce dossier |
| `GET /api/prototype/source/{id}/{version}` | Export JSON P5 intégral ; refus si son hash a changé |

Identifiants : `robert`, `amira`, `incomplet`, `impossible`. Versions :
`r5`, `r10`, `r15` pour Robert ; `r5` pour Amira et l’impossibilité ; `r4`
pour le dossier incomplet.

Chaque version contient :

- `problem` : les valeurs du problème actif dans cet instantané ;
- `facts` : valeur, origine, citation éventuelle, référence de déclaration,
  référence et hash de la pièce. Une origine absente devient
  `not_recorded`, jamais une déclaration inventée ;
- `analysis` : contenu du résultat financier, conservé sans réécriture,
  avec options, méthodes, hypothèses, contrôles, limites, séries et calculs ;
- `stats` : raccourcis pratiques vers les mêmes valeurs ; `bindings`
  conserve les pointeurs JSON exacts dans `analysis` ;
- `claims`, `limits`, `documentary_limits`, `controls` : faits de restitution
  séparés des observations documentaires antérieures au calcul ;
- `proofs` : assertions numériques avec valeurs résolues depuis leurs
  pointeurs, et passages documentaires avec profondeur de lecture, statut
  de sélection, version et capture ;
- `agents` : tâches et tentatives réellement enregistrées pour le run,
  outils, dates, identifiants AWS, entrées hashées et références produites ;
- `events` : événements du dossier. Leur affichage est un historique,
  jamais une activité supposée en cours ;
- `questions` : clarifications ouvertes, dédupliquées uniquement à
  formulation et champ identiques ;
- `changes` : références effectivement invalidées ou réutilisées selon
  le comparateur du dossier exécuté ;
- `source` : provenance de cet instantané et lien vers le produit existant.

L’interface doit conserver la portée de chaque résultat. Le nombre de
références, l’accord des agents et les hashes ne prouvent pas la vérité
externe d’une source. La lecture sélectionnée d’un document ne constitue
pas une vérification indépendante de son implication pour chaque claim.

## Exploration financière séparée

```json
POST /api/prototype/explore
{
  "case_id": "robert",
  "version_id": "r5",
  "changes": {
    "withdrawal_cad": 40000,
    "scenario_loss_limit_cad": 15000,
    "tsla_cap": 0.1
  },
  "simulate_error": false
}
```

| Paramètre accepté | Unité et domaine | Effet |
|---|---|---|
| `capital_cad` | CAD, strictement positif, au plus 10¹² | Montants, réserve relative et pertes CAD changent |
| `withdrawal_cad` | CAD, de 0 à 10¹² | Exigence de réserve ; au-delà du capital, certificat de contradiction |
| `scenario_loss_limit_cad` | CAD, de 0 à 10¹² | Contrainte sur chaque choc déclaré, pas maximum de perte future |
| `tsla_cap` | Fraction, de 0 à 1 | Plafond du poids initial TSLA ; pas poids après variation de cours |

Les valeurs initiales viennent de la version choisie. Les booléens, valeurs
non finies, paramètres inattendus et autres familles de dossier sont
refusés. Aucun horizon n’est interpolé : les chocs ont une échéance donnée.
Les autres entrées restent celles du dossier copié.

Le résultat porte `mode=local_calculation` et le message :
**« Calcul déterministe réel sur une copie des paramètres. Aucun agent
relancé, aucune révision du dossier produit. »**

`analysis`, `stats`, `claims` et `limits` viennent du moteur
`alphaforge_app.decision.finance.analyze`. Le reçu comporte heure,
implémentation, hash du code courant, hash du résultat, zéro inférence et
zéro mutation du produit. Ce reçu ne remplace pas une revue documentaire
et une restitution d’agents dans le vrai dossier.

`dependency_preview` est explicitement une **prévision des dépendances** :
elle indique ce qui devrait être examiné lors d’une future révision, sans
inventer des événements ni des réutilisations déjà commises. À capital,
positions et scénarios inchangés, les entrées du diagnostic initial restent
identiques. Changer le capital rend aussi ses pertes CAD dépendantes.
**Tous les calculs numériques applicables sont réexécutés localement**,
y compris le diagnostic initial lorsque le moteur l’évalue. L’exploration
ne fournit aucun cache d’artefacts à `analyze` et ne réemploie pas un
résultat numérique archivé. La valeur
`baseline_stress=unchanged_inputs_reusable_in_future_revision` signifie
seulement que ce diagnostic serait réutilisable dans une future révision
du produit, sous les mêmes entrées. Le reçu indique
`artifact_cache_reused=false` ; `local_execution` rend cette distinction
explicite. Une impossibilité arithmétique détectée avant les chocs conserve
le court-circuit normal du moteur : aucun diagnostic de scénario absent
n’est prétendu exécuté.

La réponse ne contient aucune référence simple extrapolée. Les résultats
sont ceux du modèle abstrait : pas de frais, impôt, inflation, probabilité
de scénario, instrument réel garanti ou allocation réglementaire.

L’annulation est une opération de présentation : abandonner cette copie
et revenir à l’instantané sélectionné. Aucun rollback du dossier produit
n’est nécessaire puisqu’il n’a pas été écrit.

## Échec et reprise

`simulate_error=true` provoque un HTTP 503 clairement marqué
`prototype_simulated_error`, avant tout calcul. Le message conserve les
paramètres et propose de réessayer avec `simulate_error=false`.
Ce contrôle sert uniquement à évaluer la récupération de l’interface.
Il ne constitue pas une preuve de reprise LangGraph après interruption.

Un vrai échec réseau ou HTTP doit rester distinct d’une impossibilité
financière (`analysis.status=infeasible`). L’interface ne doit pas afficher
une ancienne allocation comme si elle résultait des nouveaux paramètres.

## Qualification effectuée

`prototype/prompt6/data/verification.json` conserve les contrôles de
l’adaptateur : index et exports, calculs 30 000 / 40 000 / 74 400 CAD,
absence d’options dans l’impossibilité, rejets d’entrées hors contrat,
erreur simulée, refus d’origine externe et hash inchangé de la base produit.
Les calculs passent par le moteur existant, pas par les conclusions
préremplies du fichier de conception.

Ces vérifications concernent les données et l’API. Elles ne valident ni
l’utilisabilité, ni la compréhension humaine, ni la direction visuelle.
