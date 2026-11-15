# Revue indépendante des recherches, preuves et conclusions — Prompt 5

> Addendum d’intégration, postérieur à la revue ci-dessous : `inspection.py`
> lit désormais `docs/implementation/methodes_runtime.md`, sans résultats
> attendus des personas, à la place du compte rendu `finance.md`.
> Les nouveaux exports P5 d’Amira utilisent ce contrat. Le constat PRE-05
> demeure valable pour les essais antérieurs ; cette correction ne constitue
> pas une évaluation aveugle de la qualité des agents. Les nouveaux runs
> conservent aussi un bundle de sources du code, en plus de leurs hashes.
> Voir la [synthèse d’intégration](README.md).

Relecteur : session `/root/critique_preuves`, distincte des auteurs des modules
initiaux. Le 15 novembre 2026, le premier contrôle a lu `session_meta` et confirmé
`amazon-bedrock-runtime`, avant l'examen du dépôt.
[Reçu de route](proofs/preuves_route_session.json).
Aucun moteur externe d'inférence ou de recherche n'a été utilisé. L'essai produit
ci-dessous appelle le client AWS existant ; les autres expériences sont locales,
déterministes et explicitement séparées.

**Conclusion :** la chaîne numérique des démonstrations est réelle, les captures
et les passages contrôlés correspondent aux fichiers conservés, et les limites
économiques sont généralement déclarées honnêtement. En revanche, la première
version perdait des désaccords et des réserves de recherche au moment de la
restitution. Ces défauts ont été reproduits avant correction. La détection et la
portée d'une contradiction sémantique restent un jugement de modèle, pas une
certification indépendante de chaque affirmation.

## Périmètre effectivement examiné

- Conception : architecture, contrats, parcours/contrôles et exemple financier.
- Recherche : synthèse, journal commun J01–J18, fondements d'Agent1,
  expériences financières, sources primaires et niveaux de lecture.
- Implémentation : README, contrat, journal des admissions, modules `research`,
  `inspection`, parties recherche/restitution du service, contrats financiers
  et lecture de l'onglet de preuves.
- Archives : `final_demo/robert-initial.json`, `robert-revised.json` et
  `amira-initial.json`, vérifiées par le
  [script reproductible](proofs/preuves_audit.py).

Ce périmètre ne constitue pas une relecture intégrale des 505 URL, une nouvelle
expertise de chaque cours fournisseur, ni une réplication des publications
académiques. Les registres de recherche distinguent déjà ces niveaux.

## Constats reproductibles et suites

| ID, gravité | Observation vérifiable et effet | Correctif et état |
|---|---|---|
| P5-PRE-01 — majeure | Avant correction, `_agent3` utilisait les limites du calcul et `research.gaps`, mais omettait `research_review.unresolved` et `research.contradictions`. Dans les archives, 5 réserves de Robert initial, 4 de Robert révisé et 6 d'Amira ne sont pas reprises **verbatim** dans `view.limitations`. Certaines sont couvertes par des limites génériques ; il serait incorrect de dire que les 15 thèmes sont totalement absents. La fixture rend la perte d'un désaccord spécifique non ambiguë. | `service.py` transmet maintenant revue, contradictions et métadonnées de lecture à Agent3 ; la vue conserve les désaccords, réserves et issues. Test `test_material_research_disagreement_survives_to_current_view`. **Corrigé et testé.** |
| P5-PRE-02 — majeure | Le nœud `evidence` était `resolved` dès que `gaps` était vide, même avec un conflit documenté et une revue `unresolved`. La fixture P5 reproduisait ce faux état de résolution. | `issues` distingue portée, gravité, preuve et état ; une contradiction du récupérateur omise par la revue devient bloquante, sauf statut contextuel explicite. Un jugement de modèle seul ne peut lever une issue de portée `data` ou `method` déclarée bloquante. Le responsable a ajouté la barrière Agent2 : aucun appel financier pour ces obstacles. **Corrigé et testé.** |
| P5-PRE-03 — modérée | Les archives citent toutes les pièces inspectées : Robert 5 citations pour 3 sélectionnées ; Amira 11 pour 6. « Citation » ne matérialisait donc pas la sélection critique. Le tableau de preuves ne précisait pas cet écart. | La nouvelle vue sépare `citations` sélectionnées et `inspected_evidence`, ajoute `selection_status` et déclare `entailment_status=not_independently_verified_per_claim`. Tests de séparation. L'adaptation de l'affichage a été signalée au responsable ; le présent relecteur n'a pas modifié le JavaScript. |
| P5-PRE-04 — modérée | Dans le reçu AWS de Robert initial, Agent1 qualifie `linear_programming` de méthode non admise ; Agent2 rappelle qu'il faut qualifier avant exécution, puis le service utilise son outil local. Le calcul n'est pas fictif : le contrat confondait le **candidat bibliographique** et l'**outil local enregistré**, dont la qualification est un autre objet. | Nouveau `tool_contracts.executable_contracts()`, communiqué aux deux rôles : domaine, code hashé, matériel de qualification et invariants runtime. Un fichier de test est explicitement un fichier de test, pas un reçu de passage. **Contrat corrigé ; essai AWS historique ne reproduit plus la confusion.** |
| P5-PRE-05 — limite importante d'évaluation | `inspection.py` fournit jusqu'à 12 000 caractères de `docs/implementation/finance.md`. Dans l'archive Amira, ce passage contient les résultats illustratifs exacts de Robert et Amira. Agent1 dit lui-même qu'ils ne remplacent pas l'exécution. Les nombres sont recalculés, mais la démonstration n'est pas une évaluation aveugle du raisonnement des modèles. | Aucune fraude de calcul constatée. Pour un futur benchmark aveugle, séparer le contrat opérationnel des comptes rendus contenant les réponses et utiliser des cas tenus à l'écart. **Limite conservée, pas présentée comme corrigée.** |
| P5-PRE-06 — limite de portée | La chaîne `analysis.chain` relie le résultat à un ensemble d'artefacts ; elle ne prouve pas, pour chaque claim, quel passage établit quelle hypothèse et avec quelle implication. Les claims calculés ont des pointeurs numériques précis, les sources documentaires ont un lien plus large. | Les nouveaux statuts exposent cette limite sans appeler une capture une preuve logique. Une admission assertion→passage→hypothèse, avec contrôle indépendant adapté, reste un travail distinct. **Partiel, non certifié.** |

Le changement de code a été autorisé après transmission des défauts au
responsable. Ce relecteur a modifié le schéma de revue, `_agent1`, `_agent3`,
`tool_contracts.py` et ses tests. Les barrières `_agent2`, le noyau, les règles
financières et l'interface ont des responsables distincts.

## Contre-exemple réellement injecté et résultat AWS

Le script crée deux documents **synthétiques explicitement étiquetés** sous
`proofs/preuves_corpus/collecte/`. Aucun des deux n'est présenté comme une vraie
métadonnée du starter :

- [U901](proofs/preuves_corpus/collecte/U901.html), ligne unique : le champ
  `adj_close` de la fixture « inclut les distributions réinvesties ».
- [U902](proofs/preuves_corpus/collecte/U902.html), ligne unique : le même champ
  de la même fixture « exclut les distributions » et corrige les fractionnements.

Les deux sources passent par **`research.research` → `_load_local` → vérification
du SHA-256 original → `_extract` → `_passages`**. Les reçus
`local_corpus_read` réussis portent les empreintes `0a89f975a663…` et
`6a382ecc976d…`. Les passages sont à la ligne 1 de chaque extraction.
Le catalogue est injecté ; ni le lecteur ni l'extracteur ne sont remplacés.
La recherche web est désactivée pour cette fixture. Les métadonnées temporelles
sont elles aussi des données de test, pas une preuve de publication publique.

[Sorties intégrales du récupérateur](proofs/preuves_live_retrievals.json) :
sa liste `contradictions` est **vide**. Aucune réponse attendue ou contradiction
prérédigée n'est ajoutée au résultat de cet essai AWS.

La requête Agent1 **`8867c4bf-80e7-4abd-84b2-61b27d5e96bb`** identifie ensuite :

> « U901 décrit adj_close comme incluant les distributions réinvesties ; U902
> décrit le même champ comme les excluant. Cette contradiction existe malgré la
> liste contradictions vide. »

Elle justifie aussi leur non-applicabilité au vrai starter : les documents
annoncent explicitement porter sur une fixture. La gravité choisie est donc
`informational`, pas `blocking`. Le noyau conserve l'issue comme non résolue,
et l'analyse réelle reste `conditional`. La contradiction se retrouve dans
`current_view.content.limitations`.

**Ce que cet essai démontre :** les documents ont été réellement lus ; un appel
AWS a détecté leur opposition sémantique sans réponse imposée ; sa qualification
et le désaccord restent inspectables dans la vue.

**Ce qu'il ne démontre pas :** le blocage AWS d'une contradiction matériellement
applicable au jeu réel, un rappel général des contradictions, ou la fiabilité
d'un juge sémantique. Présenter la poursuite conditionnelle comme un succès de
blocage serait faux.

La barrière sur un conflit déclaré matériel est éprouvée séparément par les
tests déterministes : même récupérateur réel, annotation de conflit et modèles
**simulés explicitement**. Les tests prouvent l'absence d'appel `finance.analyze`
et de claims numériques lorsque l'issue reste bloquante ; ils ne prétendent pas
prouver que le modèle classifiera toujours correctement un nouveau texte.

[Dossier AWS complet](proofs/preuves_live_counterexample.json) ·
[Résumé et reçus](proofs/preuves_live_counterexample_summary.json).
Dossier `1324588dabee4c1582bc2763c807e5be`, état conservé sous
`runtime/defense_preuves_counterexample`. Quatre appels, tous
`amazon-bedrock-runtime`, modèle `global.openai.gpt-6-astra`, compte
`471112821226`, région d'entrée `us-east-1`. Aucune résidence physique
canadienne n'est inférée de cette région.

## Source → méthode → calcul → conclusion : confirmations

[Audit calculable des archives](proofs/preuves_final_demo_audit.json) :

- Les 21 occurrences de captures citées dans les trois archives sont présentes
  et leur SHA-256 correspond. Tous les passages avec fichier texte et fenêtres
  de lignes disponibles correspondent à l'extraction conservée.
- Les huit claims affichés ont le même texte que le registre de calcul et leurs
  pointeurs de résultat se résolvent. Cela prouve une fidélité de restitution,
  pas la vérité économique de toutes les hypothèses.
- Robert : la documentation de Boyd concerne la formulation LP, les contraintes
  et la dualité. Elle ne prouve pas une garantie de ZST. Les 30 000 et 40 000 CAD
  proviennent du solveur local, de ses contraintes et de sa borne indépendante.
  Les mêmes claims sont encore reproduits par un appel direct au moteur.
- Amira : une petite implémentation indépendante lit directement les CSV et
  calcule `V0 × Σ wᵢ × (prix ajusté CAD final / prix ajusté CAD initial)`.
  Elle obtient **44 515,7514** et **46 874,0223 CAD** ; les archives affichent
  44 515,75 et 46 874,02 CAD. Les rendements calculés sont 78,06300565 % et
  87,49608928 %. L'accord est à l'arrondi au cent près.
- Ce dernier contrôle reproduit la convention de prix ajusté des archives ; il
  **ne certifie pas** la couverture réelle de toutes les distributions du
  fournisseur. Pendant la revue, le moteur historique est passé à v2 et exige
  une politique typée explicite. Les anciens faits d'Amira ne se rejouent plus
  tels quels par le moteur courant : le champ
  `same_claim_text_from_direct_finance_without_agents=false` est conservé dans
  l'audit, et ne doit pas être caché ni interprété comme une erreur de l'arithmétique
  indépendante ci-dessus.

Les contrôles de `research` confirment également : un hash original différent
ne devient pas une preuve ; les citations sont réextraites du document original,
pas d'un voisin texte modifiable ; les snippets restent des résultats de
recherche tant que le document n'a pas été récupéré ; une capture postérieure à
la date de connaissance est exclue. La date revendiquée par l'index ou une balise
de publication ne rétrodate pas `known_at`. Les tests portent sur ces contrats,
pas sur une qualification économique de chaque source.

Le corpus P2 est utilement prudent : il sépare résumé, passage ciblé, code lu,
expérience isolée et projet non exécuté. J05/J06/J08/J09/J11 restent reportés
dans le journal P4 plutôt que d'être artificiellement crédités au produit. Le
contraste empirique DeMiguel/Kritzman ne tranche ni le LP de réserve ni une
comparaison descriptive sans optimisation ; le code le marque
`context_dependent`, ce qui doit rester une réserve de portée.

## Valeur ajoutée par rapport à une référence simple

Pour Robert, le premier contrôle simple est conservation achat=vente et borne
`max(réserve manquante, excès de plafonds)`. Les deux exemples atteignent cette
borne. La recherche n'est donc pas nécessaire pour produire leurs deux montants ;
son utilité démontrée est de limiter l'interprétation : réserve abstraite,
absence de garantie produit, scénarios sans probabilités, objectifs non
interchangeables et non-unicité des portefeuilles.

Pour Amira, le calcul direct ci-dessus suffit à retrouver les deux richesses
terminales. Les sources contextualisent devises, dates, limites historiques et
risque d'estimation. Aucun essai comparatif ne montre ici que les appels Agent1
améliorent les rendements, la décision d'une personne ou le rappel documentaire
par rapport à un moteur déterministe avec contrat clairement présenté.

La profondeur documentaire est donc un **support de justification et de
limitation** réellement présent, avec un coût et des limites. Elle n'est pas une
preuve de supériorité financière des quatre agents. Les README P2/P4 et les
journaux, dans leur ensemble, ne revendiquent pas cette supériorité.

## Vérification après correction

Commande : `.venv/bin/python -m pytest -q tests/test_p5_evidence_review.py
tests/test_decision_research.py tests/test_decision_service_review.py`.

[Sortie réellement enregistrée](proofs/preuves_tests.txt) : **23 réussites**.
Les avertissements de dépréciation du paquet LangSmith sont consignés ; aucun
service d'inférence LangSmith n'est appelé par ces tests.

Avant correction, la première exécution des quatre tests P5 donnait
**1 réussite et 3 échecs** : conflit perdu dans la vue, nœud indûment résolu et
contexte Agent3 incomplet. Le fichier P5 compte désormais sept tests, incluant
la barrière de calcul, la séparation des citations et le refus d'une résolution
de données par le seul jugement du modèle.

Les contrôles de qualité des données, les autres contrats de rôle et la
validation visuelle complète relèvent des revues parallèles. Les anciens reçus
de démonstration n'ont pas été réécrits pour faire croire qu'ils avaient bénéficié
des corrections nouvelles.
