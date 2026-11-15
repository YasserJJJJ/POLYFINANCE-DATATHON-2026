# Dossier de défense — revue indépendante du Prompt 5

**Ouvrir [l’application locale](http://127.0.0.1:8768)** ou double-cliquer
`Ouvrir_AlphaForge.command`. Les dossiers ci-dessous sont déjà exécutés :
les ouvrir ne déclenche aucune nouvelle inférence.

| Parcours à examiner | Accès | Observation |
|---|---|---|
| Robert, correction du retrait puis du risque | [Dossier r15](http://127.0.0.1:8768/?dossier=4089e4b0d70f40b6b20d832fa261e1dc) | Capital conservé, retrait 30→40 kCAD, puis budget de perte 1 kCAD ; comparaison et archives accessibles |
| Demande incomplète | [Dossier en attente](http://127.0.0.1:8768/?dossier=e6405c6c61f64c5b89c11262ce9b9669) | Douze mois reconnus ; capital, positions et retrait inconnus ; aucune allocation inventée |
| Retrait impossible | [Certificat](http://127.0.0.1:8768/?dossier=1f7d3a73d5924a09ba73925655dce389) | 120 kCAD à financer avec 100 kCAD : contradiction de 20 kCAD sous réserve abstraite, sans allocation |
| Amira, autre famille de problème | [Comparaison historique](http://127.0.0.1:8768/?dossier=f281a9067e4544138fa178fa4ee0b850) | Politique explicite, prix et change réellement utilisés ; descriptif rétrospectif |

**Conclusion de la critique : les calculs examinés sont reproduits, mais cela
ne valide pas un conseiller financier général ni la supériorité de quatre
agents.** Les défauts démontrés portaient surtout sur les révisions, le
contrôle des preuves, les conditions d’admission des méthodes et la
présentation des informations manquantes. Ils ont été corrigés dans le
périmètre décrit ci-dessous.

## Indépendance et matériel examiné

Trois nouvelles sessions ont reçu les contrats, la conception, le code, les
données et les résultats, avec mandat de contester le récit de réussite.
Elles n’avaient pas écrit les modules examinés. La revue a commencé en lecture
seule ; les corrections ont ensuite été réparties par fichiers et intégrées.
Le correctif de routage du certificat, écrit par l’intégrateur, a été relu
par le relecteur financier. L’interface a été examinée par un relecteur qui
ne l’avait pas construite.

- [Revue financière](revue_finance.md) : calculs indépendants, hypothèses,
  comparaisons, conventions, certificat et types des entrées.
- [Revue de la chaîne](revue_chaine.md) : versions, invalidations, reprise,
  contrôles et interface.
- [Revue documentaire](revue_preuves.md) : lectures réelles, dates, conflits,
  citations, rôle de la recherche et limites de reproductibilité.

Les [métadonnées de route des sessions](proofs/route_sessions.json) indiquent
`amazon-bedrock-runtime`. Les appels du produit ont leurs propres reçus AWS.
Calculs Python, tests à doubles explicites et navigation Playwright n’exécutent
aucun modèle auxiliaire. **L’indépendance de lecture et d’implémentation ne
signifie pas indépendance statistique entre modèles** : les relecteurs
partagent la même famille de modèle et le même contexte de projet.

## Réponses aux dix questions de critique

| Question | Observation vérifiable | Conséquence et correction ou limite |
|---|---|---|
| Le profil influence-t-il réellement le résultat ? | Robert : retrait 30→40 kCAD fait passer le minimum de réallocation 30→40 kCAD ; budget de perte 15→1 kCAD le porte à 74,4 kCAD. Voir les [exports successifs](proofs/demo/). | Oui pour ces contraintes financières explicites. Ni tolérance psychométrique, ni capacité réelle, ni convenance ne sont validées. |
| La recherche est-elle utilisée ? | Agent1 reçoit les captures et l’inventaire réel. Une contradiction matérielle injectée bloque `finance.analyze` ; les conventions inspectées sont confrontées au calcul d’Amira. | Elle borne l’admissibilité et la restitution. Elle ne choisit pas aujourd’hui parmi une grande bibliothèque d’allocateurs et aucun gain de rendement ne lui est attribuable. |
| Les hypothèses sont-elles satisfaites ? | Robert utilise des chocs CAD déclarés, réserve abstraite, positions fractionnaires, sans frais. Amira exige désormais une politique structurée de redistribution et de fenêtre. | Une politique absente ou hors domaine ne produit plus silencieusement la comparaison prédéfinie. Les instruments réels et les frais restent non qualifiés. |
| Les informations existaient-elles à la date considérée ? | Inspection et calcul confrontent acquisition, connaissance et hashes. La fenêtre 2021–2026 utilise un snapshot acquis en novembre 2026. | Description rétrospective admissible en novembre 2026 ; aucune sélection de portefeuille simulée avec connaissance de 2021 n’est revendiquée. Les tests refusent une capture postérieure à la date de connaissance. |
| Les chiffres et transformations sont-ils corrects ? | Oracle par énumération de sommets indépendant du LP ; oracle CSV indépendant des modules historiques. Robert et Amira concordent. [Preuves financières](proofs/finance_review.json). | Validation des calculs étudiés. Elle ne certifie pas la vérité des ajustements du fournisseur. Les booléens ne peuvent plus devenir des montants ou poids par coercition. |
| Les alternatives sont-elles comparées équitablement ? | Même portefeuille initial pour Robert30/40, mêmes dates/FX/achat-conservation pour Amira. Plusieurs optima du LP sont exposés. | Le premier optimum n’est pas le moins risqué : un autre témoin le domine sous les deux chocs. Frais exclus des deux côtés ; ce n’est pas une comparaison nette de coûts réels. |
| Une référence simple ferait-elle aussi bien ? | Une règle simple admissible atteint aussi les 30 kCAD minimaux de Robert. Le [contrôle sans LLM](proofs/control_ablation_v2.json) reproduit options et claims des problèmes déjà formalisés. | Oui sur ces résultats numériques. L’utilité des agents doit être mesurée sur compréhension, questions, recherche et fidélité ; elle n’est pas démontrée par le rendement ou le nombre de rôles. |
| La restitution exagère-t-elle la preuve ? | Les claims sont issus des calculs ; les contrôles de fidélité, arithmétique, mandat, documentation et validité externe sont séparés. Les citations non sélectionnées ne sont plus présentées comme retenues. | Un contrôle arithmétique échoué supprime les résultats affichables. Les observations documentaires sont datées comme antérieures au calcul ; leur appui logique par claim n’est pas vérifié indépendamment. |
| Chaque agent a-t-il une contribution utile ? | A0 extrait et révise les faits ; A1 lit/sélectionne/conteste ; A2 route et exécute un outil ; A3 choisit l’ordre et le détail d’assertions autorisées. Reçus et transformations distincts. | Contributions réelles, mais l’utilité marginale des quatre inférences n’est pas établie. A3 est volontairement borné ; une étude comparative reste nécessaire. |
| Peut-on reproduire et contester ? | Entrées d’outils, versions, objets hashés, code des nouveaux runs et reçus sont conservés. Quatre recalculs locaux retrouvent les nombres. | Oui pour les calculs archivés avec leurs ressources. Un export JSON seul n’embarque pas tous les objets/captures/données ; les anciens runs n’ont pas tous un bundle source. Une nouvelle génération LLM n’est pas un rejeu identique. |

## Défauts corrigés

Les observations antérieures ne sont pas réécrites. Chaque rapport contient
son protocole, son impact et les preuves avant/après.

| Repère | Défaut observé | Correction et vérification |
|---|---|---|
| CH-01 | Corriger le retrait invalidait aussi le capital extrait de la demande précédente. | Capture immuable de la demande source, distincte de la demande courante. Tests sur anciennes/nouvelles provenances et vraie révision AWS sans capital répété. |
| CH-02 | Un retour Agent3→Agent0 pouvait faire disparaître la vue partielle et les raisons de l’attente. | Qualification d’attente séparée du problème inchangé, questions courantes conservées. Cas incomplet contrôlé et consultation réelle. |
| CH-03 | `status=conditional` pouvait suffire à afficher une arithmétique « suffisante » malgré un contrôle échoué. | Évaluation des contrôles réels ; claims/options retirés en cas d’échec matériel. Injection d’un contrôle indépendant défaillant. |
| CH-04 | « Douze mois » ne passait pas l’ancrage numérique lexical. | Lexique borné, unités conservées ; tests positifs/négatifs et extraction AWS observée à 12 mois. |
| FIN-01 | La redistribution proportionnelle et toute la fenêtre historique étaient imposées même si le mandat les contredisait. | `historical_policy` obligatoire, méthode v2 ; autre fenêtre/redistribution explicitement refusée. |
| FIN-02 | Un retrait supérieur au capital devenait seulement une clarification, puis une boucle documentaire. | Certificat algébrique sur six paramètres. Routage borné vers A2 même si A1 veut approfondir ; aucun LP, aucune donnée de marché, conflits conservés. Vrai run avant/après à mêmes entrées. |
| FIN-03 | Pydantic transformait `true` en montant `1.0` avant le contrôle financier. | Refus avant coercition pour montants, horizons, poids, rendements et révisions ; les booléens légitimes des contrats restent admis. |
| PRE-01/02 | Désaccords et lacunes de revue pouvaient être perdus ; un nœud de preuve pouvait paraître résolu. | Issues typées, conflits non omis par défaut, barrière matérielle avant calcul. Un modèle ne peut certifier seul la résolution d’un conflit de données. |
| PRE-03/04 | Source consultée confondue avec source sélectionnée ; outil local confondu avec méthode bibliographique candidate. | Deux statuts de citation, registre d’outils exécutables et références bibliographiques distincts ; tests de contrats. |
| PRE-05 | Le document technique lu par Agent1 contenait des résultats attendus des exemples. | Nouveau document runtime sans réponses de démonstration. Les nouveaux passages AWS l’utilisent ; cela ne rend pas les anciens essais rétrospectivement aveugles. |
| UI | 21 cartes pour sept champs, dont répétitions exactes ; réserve d’A1 disant « reçu absent » visible après calcul. | Déduplication exacte, regroupement par champ avec les formulations distinctes conservées ; observations A1 explicitement situées avant le calcul, contrôles A2 accessibles. |

La conservation des sources du code pour les nouveaux runs et
`scripts/replay_calculation.py` complètent la correction de traçabilité.
Aucun accord entre agents ne transforme une source, un scénario ou une
hypothèse en fait vérifié.

## Expériences adversariales et résultats

**Demande incomplète.** L’utilisateur ne fournit ni capital, ni positions,
ni montant de retrait. L’échéance « douze mois » est extraite, les autres
champs restent inconnus. Le run s’arrête en attente avant A2 ; aucune
allocation ou réponse finale n’est inventée. L’interface regroupe les
questions par champ et conserve leurs formulations.

**Contrainte impossible.** Le premier passage AWS après correction du seul
moteur s’arrêtait encore à Agent1 : [export de l’échec](proofs/demo/impossible-initial.json).
Ce contre-exemple a révélé la boucle de routage. Le
[passage corrigé](proofs/demo/impossible-after.json) atteint les quatre rôles,
conserve le désaccord et présente le certificat `retrait ≤ réserve ≤ capital`.
Le déficit de 20 kCAD est calculé ; aucune contrainte n’est modifiée.
Le diagnostic est vrai sous les valeurs et le modèle déclarés, sans
certifier que ces valeurs décrivent une situation réelle.

**Source contradictoire.** Deux documents clairement fictifs attribuent des
conventions opposées au même champ `adj_close`. Le récupérateur lit leurs
octets et passages ; [Agent1 AWS détecte l’opposition](proofs/preuves_live_counterexample.json).
Dans cet essai, il la classe hors des données réelles du starter :
le calcul conditionnel continue et la contradiction reste visible.
**Cet essai ne prouve donc pas un blocage AWS de toute source contradictoire.**
Des tests contrôlés distincts établissent qu’un conflit matériel non résolu
empêche le calcul et les claims. Le jugement de pertinence du conflit
reste une limite de l’agent documentaire.

**Modification du profil.** Les trois états de Robert sont :

| État | Retrait CAD | Budget de perte par scénario CAD | Minimum réalloué CAD |
|---|---:|---:|---:|
| Initial | 30 000 | 15 000 | 30 000 |
| Correction libre du retrait | 40 000 | 15 000 | 40 000 |
| Correction du budget de perte | 40 000 | 1 000 | 74 400 |

Le capital de 100 kCAD extrait initialement demeure valable. Les positions
initiales ne changent pas. `baseline_stress@1` et `research@1` gardent leur
version ; qualification, revue documentaire, analyse et restitution
dépendantes sont renouvelées. Les minima ne sont pas des sommes à déplacer
successivement après exécution du plan précédent.

**Généralisation bornée.** Amira utilise une autre famille : comparaison
achat-conservation en CAD, avec politique explicite. Rendements cumulés
observés : 78,0630 % pour l’allocation initiale, 87,4961 % pour la variante
TSLA à 10 %, sur 2021-11-12→2026-11-12. L’oracle indépendant retrouve
ces valeurs. Ce résultat rétrospectif ne justifie pas une recommandation future.

## Vérifications et reproduction

Les [résultats de vérification](proofs/verification.json) distinguent :

- suite intégrée initiale : **178 tests réussis** ;
- suite ciblée après routage : **63 réussis** ;
- suite ciblée après correction des types : **101 réussis** ;
- essais de rendu et navigation réels, plus recalculs locaux et reçus AWS.

Ces nombres se recouvrent et **ne doivent pas être additionnés**.
Treize avertissements connus concernent une dépréciation de LangSmith,
dont la télémétrie est désactivée. Aucune répétition complète sans nouvelle
incertitude n’a été lancée.

```bash
# Recalcul du résultat courant, sans modèle
.venv/bin/python scripts/replay_calculation.py 4089e4b0d70f40b6b20d832fa261e1dc
# Recalcul d’une version antérieure
.venv/bin/python scripts/replay_calculation.py 4089e4b0d70f40b6b20d832fa261e1dc --analysis-ref analysis@1
# Oracles financiers indépendants
.venv/bin/python docs/defense/proofs/finance_review.py
# Parcours critique AWS : réutilise ses IDs enregistrés pour éviter de dupliquer les appels
.venv/bin/python scripts/run_critical_demo.py --live
```

Les [recalculs conservés](proofs/replay/) vérifient aussi les bundles sources.
Ils exécutent le moteur courant, comparent les nombres et signalent une
différence ; ils n’exécutent pas automatiquement du code historique.
L’[état de reprise](../implementation/ETAT_REPRISE.md) précise quoi conserver.

## Limites restantes et portée de la défense

Les deux familles financières restent étroites : pas de preuve de placement
garanti, de CVaR optimisée, de prévision, de gestion fiscale, d’ESG vérifié
par actif ou de convenance réglementaire. La réserve est abstraite.
La provenance ne certifie pas les données fournisseur et les ajustements
historiques ne reconstruisent pas un univers point-in-time.

La recherche est bornée et son jugement reste faillible. L’implication
logique de chaque citation pour chaque claim n’est pas contrôlée
indépendamment. Les observations d’A1 restent historisées ; le rapprochement
automatique de chaque obligation documentaire avec un contrôle ultérieur
d’A2 n’est pas implémenté. Un diagnostic mathématique indépendant de documents
peut encore être empêché opérationnellement par une panne d’étape amont.

Les reprises locales et conflits sont testés ; un arrêt entre un appel AWS
et l’enregistrement de son reçu laisse une issue distante incertaine.
Une nouvelle tentative peut coûter un appel supplémentaire. Les archives
antérieures n’ont pas toutes le code source embarqué ; conserver le projet,
les données et l’ensemble du répertoire d’état.

Enfin, cette critique établit des comportements et des contre-exemples,
pas un taux d’erreur général ni une amélioration de la décision d’investisseurs.
La référence simple et le bras sans LLM limitent explicitement la promesse
agentique. Aucun changement de fonctionnement nécessitant un nouvel accord
n’a été introduit : les corrections renforcent les contrats validés.

[Schéma actualisé](../implementation/architecture.svg) ·
[Décisions de correction](decisions_corrections.md) ·
[Preuves de navigation](proofs/ui_review.json)
