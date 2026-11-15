# Décisions de correction — Prompt 5

15 novembre 2026. SQLite, artefacts immuables et LangGraph sont conservés.
Ces choix ne sont pas remis en concurrence : les défauts observés venaient
des contrats et des projections, pas d’une incapacité démontrée du framework.

| Décision | Motif démontré | Solution retenue | Conséquence |
|---|---|---|---|
| Provenance de texte stable | Une correction de retrait effaçait le capital extrait. | `request_source.<run_id>` immuable pour citer le texte ; `request` reste l’intention courante. Compatibilité conservatrice des anciennes références de provenance. | Une correction explicite d’un fait invalide toujours ses descendants ; changer la demande ne retire plus tous les faits extraits auparavant. |
| État d’attente séparé | Réécrire le problème au retour A0 invalidait la raison de l’attente. | Qualification et questions séparées ; problème/analyses partiels conservés dans leur contexte. | Attendre n’est pas résoudre ; une vue partielle reste marquée telle. |
| Contrôles fondés sur les checks | Le statut global du calcul pouvait masquer un contrôle échoué. | `assessment.assess_checks`, barrière avant publication, classes de contrôle distinctes. | La fidélité au registre n’est pas une preuve d’arithmétique. |
| Politique historique v2 | Fenêtre et redistribution implicites violaient un mandat différent. | Politique structurée ; domaine étroit explicite, absence ou autre politique refusée. | Les anciens exports ne sont pas migrés implicitement ; un recalcul actuel peut exiger une clarification. |
| Diagnostic d’infaisabilité séparé | Le moteur avait la preuve, mais A1 demandait de l’approfondir avant qu’A2 l’exécute. | Garde sur six paramètres ; `reserve_budget_diagnostic` sans LP, marché ni allocation. L’avis A1 et ses conflits sont conservés. | Une preuve conditionnelle simple peut être affichée malgré d’autres questions ouvertes. Aucune autorisation générale de contourner la barrière documentaire. |
| Entrées numériques sans booléens | Pydantic pouvait coercer `true` en `1.0`. | Validation avant coercition, y compris poids et rendements imbriqués. | Les nombres entiers/flottants valides et les booléens légitimes restent admis. |
| Conflits et citations explicites | Des réserves étaient omises ; toutes les pièces devenaient des citations. | Issues typées et garde ; pièces consultées/retenues distinguées ; preuves bibliographiques/outils exécutables séparés. | Le modèle ne peut résoudre seul un conflit matériel de données en le déclarant clos. |
| Aucun résultat attendu dans le document runtime | La lecture technique d’Amira contenait les réponses des exemples. | `methodes_runtime.md` décrit méthodes, hypothèses et conventions sans résultats de persona. | Les nouvelles démonstrations n’utilisent plus ce document contenant les réponses ; aucune revendication de benchmark aveugle général. |
| Sources archivées | Hash seul insuffisant pour reconstruire le code d’un run. | Bundle source adressé par hash dans les objets pour les nouveaux runs. Recalcul explicite par CLI. | N’exécute pas automatiquement du code historique ; données et captures restent à conserver séparément. |
| Questions et observations datées | Triple provenance des questions ; observation « reçu absent » devenue périmée après A2. | Regroupement visuel par champ, textes distincts conservés ; libellé temporel des observations A1 avant calcul. | Pas de fusion sémantique, pas de résolution documentaire automatique inventée. |

## Contrat précis du diagnostic budgétaire

Il est admissible seulement si :
`decision_type=reserve_allocation`, `currency=CAD`,
`objective=minimize_reallocated_capital`,
`reserve_policy=abstract_nominal`, capital positif fini et retrait supérieur
au capital. Les booléens sont rejetés dès les contrats typés.

La preuve porte sur `retrait ≤ réserve ≤ capital` sous financement initial
long-only, sans apport extérieur et réserve nominale à rendement nul.
Elle produit un certificat et ses pointeurs, **aucune allocation**.
Les six paramètres et les hypothèses sont conservés dans le résultat.
La porte documentaire ordinaire reste fermée pour tout calcul qui dépend
d’un conflit non résolu. Les tests piègent les appels LP, baseline et données
de marché : aucun n’est utilisé dans ce diagnostic.

Le routage est une règle explicite du noyau, enregistrée dans
`research_review.kernel_routing`, avec la décision initialement demandée
par Agent1. L’agent n’est pas forcé à prétendre que les preuves sont résolues.
La fonction bornée et le service ont été relus indépendamment après leur
intégration.

## Ce qui n’a pas changé de direction

Les quatre rôles, l’objet partagé, la provenance, la réutilisation et les
boucles de révision restent ceux du fonctionnement validé. Les contrats
renforcés sont des corrections réversibles autorisées. Aucun déploiement
public, changement de route d’inférence, service AWS supplémentaire ou
nouvelle promesse financière n’a été introduit.

Les versions exactes de sources des nouveaux runs peuvent différer de la
version finale locale lorsque la revue a conduit à une correction ultérieure.
Cette différence est conservée dans leurs manifestes ; ni les reçus ni les
anciens artefacts ne sont remplacés.
