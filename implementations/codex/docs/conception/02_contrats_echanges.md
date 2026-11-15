# Contrats du dossier et des quatre agents

**Prompt 3 · Conception du 15 novembre 2026 · À valider avant construction.**

Ces contrats définissent des responsabilités et des formats logiques. Ils ne constituent ni un moteur implémenté, ni un schéma de stockage définitivement choisi. Les noms de champs sont proposés pour rendre les échanges vérifiables.

## 1. Objets partagés

Tout objet porte `id`, `version`, `type`, `scope`, `created_by`, `created_event`, `input_refs`, `content_hash` et un statut contextualisé. Les références pointent vers des versions précises. L’empreinte est produite par le logiciel sur les octets enregistrés, jamais déclarée comme preuve par le modèle.

| Objet | Contenu minimal | Propriétaire de la proposition |
|---|---|---|
| `ProblemSpec` | Question originale, unité de décision, objectifs, horizon/échéances, contraintes, préférences, inconnus, périmètre fictif, critères de réponse | Agent0 |
| `Assertion` | Proposition/valeur, unité, origine, temps, référence de provenance, vérification, portée | Agent0 pour déclarations ; Agent1 pour extractions documentaires |
| `QuestionNode` | Question, type, propriétaire, parents, dépendances, critère de résolution, manques, réouverture, état | Rôle responsable du sous-problème ; réaffectation journalisée |
| `EvidenceRecord` | Référence et version, capture/passage, niveau de lecture réel, résultat utilisé, nature de preuve, hypothèses, limites, contradictions, droits | Agent1 |
| `MethodCandidate` | Problème traité, source, formulation, hypothèses, données, alternatives, évaluation proposée et état d’admission | Agent1 pour revue ; Agent2 pour évaluation/usage |
| `AnalysisPlan` | Formulation, variables/unités, paramètres, contraintes, méthode/outil admis, scénarios, contrôles et critères d’arrêt | Agent2 |
| `CalculationRecord` | Reçu d’outil, entrées exactes, code/méthode, versions, résultats bruts, diagnostics, tolérances, contrôles, limites | Adaptateur de calcul ; Agent2 contextualise |
| `VerificationRecord` | Assertion contrôlée, type de contrôle, mécanisme, auteur, références, résultat, indépendance et limites | Contrôleur approprié, attribution conservée |
| `ConclusionClaim` | Assertion analytique proposée, réponse à quel nœud, appuis/réfutations/hypothèses, contrôles requis et portée | Agent2 ; Agent3 produit une formulation distincte liée à cette pièce |
| `ViewPacket` | Mandat/révision, assertions, emplacements de valeurs, citations, alternatives, limites, changements et suite utile | Agent3 |
| `HumanEvent` | Déclaration, correction, question, examen ou choix ; objet/version/portée ; contenu original | Entrée utilisateur, enregistrée par le noyau |
| `DisplayEvent` | Paquet/révision effectivement affichés et horodatage ; ne prouve ni examen ni accord | Canal de présentation, enregistré par le noyau |
| `Task`, `Attempt`, `CommitEvent` | Travail, exécution, changement accepté/rejeté et motif | Noyau technique |

Les champs internes des contrôles demeurent attribués à leurs producteurs. Agent3 peut demander un contrôle manquant ; il ne peut pas transformer « non examiné » en « vérifié » dans un champ d’Agent2.

### Origine et nature : champs orthogonaux

```text
Assertion
  origin = declared | extracted | assumed | unknown
  value = valeur typée, intervalle ou null
  provenance_ref = déclaration, passage ou justification d'hypothèse
  verification = non_examined | corroborated | disputed | insufficient
  temporal_scope = date/période/échéance concernée
  nature = descriptive_fact | preference | constraint | scenario_assumption
  unknown_reason = obligatoire si origin=unknown

EvidenceRecord
  evidence_kind = theoretical | empirical | professional |
                  technical_documentation | commercial_claim
  reading_level = located | abstract_read | targeted_passages |
                  full_text_read | code_inspected | executed
  locator = pages/sections/lignes réellement examinées

CalculationRecord
  raw_result + units + conventions + diagnostics + input_refs

ArtifactUse (relation contextuelle, distincte de la pièce immuable)
  artifact_ref + branch_id + dossier_revision
  usability = usable | conditional | stale | blocked
```

Une même pièce peut rester utilisable dans une variante à 30 000 CAD et être périmée pour le mandat actif à 40 000 CAD. Son contenu historique n’est pas modifié pour changer ce statut d’usage.

`executed` exige une trace et ne qualifie que l’essai effectué. Un résumé ne devient pas une lecture intégrale parce qu’il est long. Un document professionnel peut contenir une affirmation empirique : qualifier l’assertion utilisée, pas seulement le type du PDF. Les résultats calculés ne sont pas rangés parmi les faits déclarés.

Un score de confiance du LLM ne remplace aucun de ces champs. Une déclaration explicitement corrigée garde son ancienne version ; deux déclarations incompatibles sans correction explicite demeurent en conflit.

## 2. Enveloppe commune d’échange

Un agent lit un instantané et soumet un **`ChangeSet`**, jamais une écriture libre dans le dossier :

```json
{
  "dossier_id": "ROB-DEMO",
  "branch_id": "main",
  "task_id": "T-ANALYSE-40",
  "attempt_id": "ATT-01",
  "producer_role": "agent2",
  "base_revision": 6,
  "read_set": [
    {"id": "ROB-M2", "version": 1},
    {"id": "ROB-SCENARIOS", "version": 1},
    {"id": "ROB-METHODE-LP", "version": 1}
  ],
  "idempotency_key": "cle-attribuee-par-le-noyau",
  "operations": [
    {"op": "add_artifact", "artifact_ref": "ROB-A2@1"},
    {"op": "propose_resolution", "question_ref": "Q-CALC-40@1",
     "status": "resolved_conditionally", "support_refs": ["ROB-A2@1"]},
    {"op": "request_review", "owner": "agent3",
     "question": "Quelles assertions de cette analyse sont restituables ?"}
  ],
  "reason": "Le retrait corrigé impose de réexaminer l'allocation.",
  "evidence_refs": ["SRC-P2-RESULTATS@1"]
}
```

Cet exemple est conceptuel : les références et la clé doivent exister ou être réservées par le noyau avant usage. La pièce d’analyse est jointe ou déposée par un adaptateur ; le modèle ne peut pas obtenir une preuve en inventant un identifiant.

Le `read_set` est construit ou contrôlé par le noyau et les adaptateurs à partir des entrées effectivement transmises, des lectures d’outils et des dépendances obligatoires. Une liste libre proposée par le modèle ne suffit pas : omettre le mandat utilisé ne doit pas permettre de faire accepter un résultat périmé.

Opérations admises : ajouter une pièce, proposer une nouvelle version, créer une question, proposer une résolution, enregistrer une lacune, demander un examen, soumettre un ensemble d’assertions ou un paquet de restitution. Les corrections passent par des versions, jamais par la suppression des objections antérieures.

### Admission d’un changement

1. Le noyau authentifie rôle/tâche et contrôle les types, champs autorisés et références.
2. Il compare `read_set`, versions courantes, portée, écritures concurrentes et préconditions.
3. Il vérifie unités, invariants, reçus d’outils et critères nécessaires au statut demandé.
4. Il accepte atomiquement le changement et ses invalidations, ou le rejette avec un motif structuré.
5. Il planifie les nouvelles tâches prêtes ; le rendu courant ne lit que des versions cohérentes.

Le commit atteste l’admission selon ces règles et les pièces exigées, pas la vérité scientifique de tout le contenu. Un jugement méthodologique ou documentaire garde son auteur, ses preuves, ses limites et son état de vérification.

Un changement de tête du dossier ne suffit pas à rejeter un travail indépendant : le noyau peut le rattacher à la nouvelle révision si ses entrées et droits sont inchangés. Si une entrée matérielle a changé, la sortie reste archivée comme tentative devenue inapplicable ; elle ne se fusionne pas par une explication du modèle.

Même clé et même contenu déjà commis → même résultat de commit. Même clé avec contenu différent → rejet. Un appel modèle dont l’issue réseau est inconnue peut avoir été facturé : l’idempotence du dossier ne garantit pas celle du fournisseur.

**Atomicité de la correction :** l’adoption d’un nouveau besoin et la mise hors usage courant de ses conclusions dépendantes appartiennent au même changement logique. La présentation ne doit jamais voir « retrait 40 000 » avec « réserve admissible 30 000 » pendant un intervalle de recalcul.

## 3. Agent0 — Qualification et formalisation

**Mission :** transformer une demande en problème de décision compréhensible, avec les informations nécessaires et les critères permettant de reconnaître une réponse utile.

**Frontière :** il ne choisit ni allocation optimale, ni vérité d’une source, ni seuil de risque prétendument scientifique à partir d’une persona. Il ne résout pas une contradiction entre capacité et tolérance en augmentant automatiquement le risque pour atteindre un objectif.

| Contrat | Contenu |
|---|---|
| **Indispensable** | Demande originale, contexte/version du dossier, périmètre et décision visée. Pour une décision de placement : seulement les faits qui changent cette décision, par exemple capital, échéances, liquidité, positions ou contraintes. |
| **Facultatif** | Persona comme contexte fictif, anciennes réponses encore applicables, préférences de présentation, connaissances ou informations financières seulement si non déterminantes pour la question présente. Les connaissances de l’investisseur peuvent être indispensables à une conclusion de convenance. |
| **Outils et sources** | Historique du dossier ; schéma de qualification ; règles explicites issues des cadres professionnels examinés ; catalogue de questions ; comparaisons de valeurs/contradictions par code ; passage à Agent1/2 pour faits ou conséquences inconnus. |
| **Décisions autorisées** | Qualifier l’unité de décision ; décomposer ; identifier manque ou conflit ; choisir une question utile ; distinguer remplacement, ajout et variante ; enregistrer une correction explicite ; définir la portée d’une analyse conditionnelle. |
| **Sortie** | `ProblemSpec`, assertions de déclaration, préférences/contraintes séparées, nœuds de questions, critères de résolution et `ChangeSet`. Chaque champ important indique origine et portée. |
| **Contrôles** | Unités/devise/dates ; horizon du besoin distinct de fenêtre de données ; préférence distincte de contrainte ; déclarations contradictoires ; capacité/tolérance distinctes ; absence d’inférence depuis l’âge ou la seule persona. |
| **Retour** | Agent1 révèle une hypothèse non établie ; Agent2 montre une formulation inadéquate, infaisable ou sensible à un manque ; Agent3 reçoit une correction ou constate que la réponse ne traite pas le besoin. |
| **Absence** | Valeur `unknown` et conséquence. Poser une question si plusieurs réponses changent matériellement la conclusion ; continuer les branches indépendantes ; proposer seulement des scénarios étiquetés lorsqu’ils sont utiles. |

**Transformation observable :** la phrase « modifier le moins possible » devient un choix explicite entre capital déplacé, nombre de lignes, frais ou fiscalité. Tant que ce sens n’est pas fixé, un minimum de turnover ne répond pas nécessairement à la demande.

## 4. Agent1 — Recherche et revue critique

**Mission :** établir ce que les sources permettent réellement de dire et quelles méthodes sont pertinentes, avec leurs alternatives, hypothèses, limites et contradictions.

**Frontière :** il ne fixe pas les préférences de l’utilisateur et ne proclame pas une performance numérique locale sur la foi d’un article. Il peut contester le mandat ou une hypothèse ; il ne les remplace pas silencieusement.

| Contrat | Contenu |
|---|---|
| **Indispensable** | Questions à résoudre, portée temporelle/instrument/devise, critères de preuve, mandat applicable, pièces déjà connues et budget de recherche. |
| **Facultatif** | Bibliographie antérieure, sources proposées par l’utilisateur, corpus déjà capturé, contre-exemples connus, code ouvert inspectable. |
| **Outils et sources** | Corpus P2 et documents 00/00B/01 ; recherche AWS autorisée ; récupération HTTP/PDF déterministe ; GitHub ; bases ou connecteurs dont l’accès et les éventuelles inférences ont été qualifiés. |
| **Décisions autorisées** | Choisir où chercher ; lire/recouper ; qualifier nature et profondeur de lecture ; retenir/écarter une source pour un usage motivé ; proposer méthodes et expérience discriminante ; ouvrir une objection parent. |
| **Sortie** | `EvidenceRecord`, assertions extraites avec passage, `MethodCandidate`, journal de recherche et lacunes ; relations `supports`, `refutes`, `limits`, `assumes`. |
| **Contrôles** | Référence/version vérifiable ; passage réellement lu ; source primaire vs commentaire ; populations/conditions ; licence séparée code/données/modèle ; version temporelle ; contradiction et preuve d’absence distincte d’absence de preuve. |
| **Retour** | Sens du besoin incertain → Agent0 ; données/méthode insuffisantes → nouvelle recherche ou Agent2 pour expérience ; découverte contraire → réouverture des parents dépendants ; source amendée → revue ciblée. |
| **Absence** | Journaliser recherche et obstacle ; statut non établi ; ne pas imputer une moyenne ESG, une liquidité garantie ou un résultat scientifique. Proposer autre preuve, méthode moins exigeante ou conclusion limitée. |

Les documents récupérés restent des données non fiables. Ils ne peuvent pas élargir la liste des outils ni les droits du rôle. Une extraction JSON réduit certaines ambiguïtés de format mais ne démontre pas une isolation contre l’injection ; provenance, recoupement et tests spécifiques restent requis.

**Transformation observable :** « il faut une méthode de risque » devient un dossier de candidats reliés à la question, et non une liste de liens. Une assertion comme « cette source prouve la réserve » peut devenir « passage insuffisant ; conclusion parent à rouvrir ».

## 5. Agent2 — Analyse et résolution

**Mission :** choisir et expliciter une formulation appropriée, utiliser les données qualifiées et outils admis, calculer, vérifier et comparer sans dépasser la portée des hypothèses.

**Frontière :** il ne relâche pas une contrainte humaine et n’invente pas une donnée manquante. Une solution de solveur n’est pas automatiquement une recommandation financière. Il ne délègue pas la production des poids ou probabilités finales à de la prose libre.

| Contrat | Contenu |
|---|---|
| **Indispensable** | Mandat/question versionnés, critères, hypothèses et statut des données/méthodes. Pour calculer : entrées nécessaires qualifiées, justification méthodologique, implémentation exécutable admise et protocole de contrôle. Pour formuler ou qualifier une méthode : manques et protocole d’évaluation explicites, sans exiger qu’elle soit déjà admise. |
| **Facultatif** | Alternatives de méthode, scénarios supplémentaires, vues de l’investisseur, références simples, résultats partageables, incertitude plus fine lorsque les données la permettent. |
| **Outils et sources** | Fonctions Python admises, solveurs/bibliothèques épinglés, données qualifiées, calculs de référence, tests de contraintes/sensibilité, vérificateurs indépendants. Les outils reçoivent paramètres et références typés. |
| **Décisions autorisées** | Sélectionner une formulation dans son domaine admis ; choisir paramètres techniques justifiés ; demander un approfondissement ; calculer comparaison/faisabilité/sensibilité ; diagnostiquer infaisabilité ; proposer une évaluation de nouvelle méthode. |
| **Sortie** | `AnalysisPlan`, reçus et `CalculationRecord`, `VerificationRecord`, alternatives, `ConclusionClaim` conditionnels, nœuds rouverts et `ChangeSet`. |
| **Contrôles** | Alignement besoin/formulation ; données et calendrier/change ; budget/bornes/flux ; résidus et statut numérique ; comparaison indépendante adaptée ; optima multiples ; absence d’anticipation ; sensibilité et limites hors modèle. |
| **Retour** | Critère ambigu ou relaxation nécessaire → Agent0 ; preuve/données/méthode manquantes → Agent1 ; erreur numérique → diagnostic/outil ; critique de restitution fondée → réexamen de calcul ou portée. |
| **Absence** | `missing_input`, `unqualified_method`, `tool_failure`, `numerical_uncertainty` ou `certified_infeasibility` distincts. Résultat partiel ou scénario déclaré possible ; pas de valeur inventée ni d’échec technique présenté comme preuve d’impossibilité économique. |

### Registre extensible de méthodes

Trois statuts sont distincts : **méthode documentée**, **implémentation évaluée**, **outil admis pour un domaine d’usage**. Une publication seule n’autorise pas l’exécution de code trouvé sur Internet.

Agent1 recherche largement ; Agent2 spécifie le besoin, les tests, les hypothèses et la comparaison ; l’admission exige revue technique et méthodologique adaptée, version/empreinte et contrôles enregistrés. Cette revue est un travail de qualification, pas un cinquième agent métier. La personne qui choisit son portefeuille n’est pas sollicitée pour certifier du code.

La proposition interdit l’exécution improvisée de code généré dans le chemin qui produit une conclusion validée. Une future capacité d’expérimentation isolée devrait être qualifiée séparément ; l’absence d’un outil aujourd’hui ne doit pas limiter silencieusement la question à l’allocateur existant.

**Transformation observable :** objectif, contraintes et données deviennent un problème mathématique explicite, une sortie reproduisible et une objection si ce problème ne répond pas au besoin. L’agent ne se contente pas de commenter les nombres d’une carte existante.

## 6. Agent3 — Restitution et interaction

**Mission :** construire une explication vérifiable et proportionnée, faire examiner options et limites, recevoir questions/corrections et déclencher les retours utiles.

**Frontière :** il n’ajoute pas de faits, de calculs ou de certitude pour rendre la réponse plus convaincante. Il ne transforme ni un consensus en preuve, ni une vue affichée en accord humain.

| Contrat | Contenu |
|---|---|
| **Indispensable** | Mandat/révision, assertions proposées, pièces et contrôles nécessaires, alternatives déterminantes, hypothèses/inconnus, état des questions et changements depuis la vue précédente. Une réponse partielle n’exige que les pièces correspondant à sa portée. |
| **Facultatif** | Niveau de détail préféré, explications antérieures, questions de compréhension, format de comparaison ou de visualisation adapté. |
| **Outils et sources** | Lecture du dossier ; assemblage de valeurs depuis références ; contrôles d’unités/arrondis/comparaisons ; extraits cités ; validation des cinq dimensions ; référence à un `HumanEvent` authentique et demandes de revue. |
| **Décisions autorisées** | Choisir assertions et forme de présentation soutenables ; expliquer un manque ; rendre une réponse partielle ou indécidable ; demander un contrôle ; aiguiller question/correction vers le propriétaire. |
| **Sortie** | `ViewPacket` avec question/version, `claims`, `value_bindings`, `citations`, alternatives, limites, `delta`, `open_questions`, actions utiles et références de contrôles. |
| **Contrôles** | Fidélité, exactitude, adéquation, ancrage et validité externe, séparément attribués ; cohérence de version ; absence de limite décisive cachée ; aucun texte de garantie plus fort que la preuve. |
| **Retour** | Correction de besoin → Agent0 ; citation insuffisante → Agent1 ; nombre/calcul/portée contestés → Agent2 ; mauvaise formulation → correction propre d’Agent3. |
| **Absence** | Présenter le manque et sa conséquence ; supprimer l’assertion non soutenue ; maintenir le reste utile. Un contrôle déterminant non examiné bloque l’assertion, pas forcément tout le dossier. |

Un `value_binding` relie le nombre, son unité et son arrondi à un champ de résultat. Les comparaisons chiffrées sont calculées ou contrôlées par code. L’analyse de nombres résiduels dans le texte est un contrôle complémentaire : elle ne suffit pas à détecter « moins risqué » sans chiffre ou une réserve essentielle omise.

Le message humain brut est capturé à l’entrée authentifiée par le noyau. Les agents peuvent proposer son interprétation et le référencer ; ils ne peuvent créer ni déclaration humaine, ni accord. De même, un `ViewPacket` préparé ne produit un `DisplayEvent` que lorsque le canal de présentation l’a effectivement affiché.

La [spécification de restitution](04_parcours_et_controles.md) détaille les cinq contrôles, les formulations permises, les événements d’examen et les scénarios de réception.

## 7. Retours, conflits et contrôle indépendant

| Événement | Proposition | Application par le noyau |
|---|---|---|
| Nouvelle déclaration explicite | Agent0 révise les champs concernés avec provenance. | Nouvelle révision et invalidation des usages dépendants ; pas de confirmation redondante. |
| Deux déclarations ambiguës | Agent0 ouvre une clarification. | Conflit conservé ; seules conclusions dépendantes attendent. |
| Passage contraire à une hypothèse | Agent1 ajoute réfutation ou limite et ouvre le parent. | Réouverture de question et suspension des assertions concernées. |
| Problème infaisable | Agent2 fournit diagnostic et variantes de relaxation. | Contraintes actives inchangées ; aucune relaxation adoptée sans choix autorisé. |
| Calcul faux mais copié fidèlement | Contrôleur d’exactitude échoue. | Rejet de la conclusion numérique même si le contrôle de fidélité passe. |
| Plusieurs agents d’accord | Accord attribué, avec références éventuelles. | Aucun gain automatique du statut de vérification. |
| Nouvelle source indépendante ou borne analytique | Contrôle avec mécanisme et hypothèses distincts. | Suffisance appréciée pour l’assertion ; indépendance décrite, jamais supposée du seul nombre d’agents. |
| Correction d’un commentaire | Agent3 produit une nouvelle formulation. | Nouvelle vue ; calculs inchangés seulement s’ils n’étaient pas la cause du défaut. |

Une source indépendante peut partager les mêmes données ou biais qu’une autre ; un second solveur peut implémenter la même erreur de formulation. Le dossier distingue indépendance d’implémentation, de données et d’hypothèses. Dans Robert, la borne algébrique contrôle l’optimalité du LP indépendamment du solveur ; elle ne vérifie pas l’existence de la réserve réelle.

## 8. Contrat d’outil et erreurs

Toute opération renvoie un reçu produit par l’adaptateur :

```text
ToolReceipt
  tool_id + version + execution_id
  task_id + attempt_id + input_refs + parameters
  started_at + finished_at
  status = success | partial | failed | outcome_unknown
  output_refs + diagnostics + error_code
  provider_request_id si fourni
  inference_route si l'outil réalise une inférence
```

Les accès réseau, prompts et sorties contenant des secrets ne sont pas copiés indistinctement dans la vue utilisateur. La traçabilité conserve les références et métadonnées nécessaires dans leur périmètre d’accès. Une redaction de secret ne doit pas supprimer les paramètres scientifiques nécessaires au rejeu.

Le rejeu déterministe réutilise données/code/paramètres ; le rejeu d’une conversation peut réutiliser une réponse modèle enregistrée. **Une nouvelle inférence n’est pas garantie identique**, même avec les mêmes paramètres. Le dossier doit indiquer quel sens de « rejouer » est utilisé.

## 9. Conditions de réception après validation

La réalisation devra démontrer les quatre transformations et les boucles sur le même dossier, préserver une correction pendant un calcul, refuser les écritures hors rôle, distinguer résultat historique et actuel, détecter les références inventées, maintenir une lacune de preuve et expliquer les optima multiples.

Les [scénarios utilisateur](04_parcours_et_controles.md) et l’[épreuve des moteurs](03_decisions_techniques.md) complètent ces conditions. Ce document n’affirme pas leur réussite : **l’implémentation attend la validation du fonctionnement cible**.
