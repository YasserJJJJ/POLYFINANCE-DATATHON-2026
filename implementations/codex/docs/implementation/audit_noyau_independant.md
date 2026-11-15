# Revue indépendante du noyau et de deux gardes d'agents

Revue du 15 novembre 2026 par l'agent chargé du moteur financier, sur le noyau
écrit par l'intégrateur. Le réviseur a lu `models.py`, `store.py`, `service.py`
et les parties pertinentes de `workflow.py`. Il n'a pas modifié ces fichiers.
Les correctifs ont été intégrés par leur propriétaire puis revérifiés.

La revue a produit
[`tests/test_decision_store_review.py`](../../tests/test_decision_store_review.py).
Dernier passage : **14 tests passés en 0,97 s**. Les tests emploient des magasins
SQLite temporaires et des réponses simulées explicitement ; aucun modèle,
compte AWS, appel réseau ou service produit n'a été exécuté par cette revue.
Les 36 tests financiers distincts sont décrits dans [finance.md](finance.md).

## Défauts reproduits puis corrigés

| Défaut observé | Effet concret avant correction | Correction lue et contrôle effectué |
|---|---|---|
| Propriété vérifiée par type seulement | Agent0 pouvait créer `id=analysis`, `type=assertion` ; le snapshot l'exposait comme analyse courante | Registre du couple identifiant/type/propriétaire dans `Store.commit` ; tentative rejetée, révision et analyse inchangées |
| Dépendance invalidée dans la même transaction | Une nouvelle version de `fact.capital_cad` pouvait coexister avec un nouveau `problem` utilisable référant l'ancienne version invalidée | Rejet des dépendances invalidées dans ce commit ; rollback vérifié. Dépendances nouvelles `$id` acceptées en ordre et résolues, y compris dans `questions.result_refs` |
| Redémarrage d'un run remplacé | `begin_task` pouvait faire passer un vieux run `superseded` à `running` après correction humaine, avant le rejet de son éventuel commit | Vérification transactionnelle du run actif avant nouvelle tâche ; rejet reproduit. Le rejeu d'une tâche déjà commise demeure possible |
| Nombres imbriqués non contrôlés à la qualification | Une quote « Comparer mon portefeuille. » pouvait permettre d'adopter des poids TSLA/SPY 50/50 jamais déclarés | Parcours récursif des nombres ; absence d'ancrage produit une clarification. Régression testée avec réponse d'Agent0 simulée |
| Choix de clarification ignoré par Agent2 | `plan.tool=clarification` était accepté mais le calcul financier était tout de même appelé | Branche explicite `missing_input` sans appel financier ; compteur d'appels nul dans le test |
| Deux tentatives identiques simultanées | Deux `operation()` avec même tâche/outil/entrées exécutaient deux callbacks ; le second qualifiait l'autre tentative encore active d'issue inconnue | Verrou de fichier autour de la tentative et du cache ; vérification complémentaire ci-dessous |

La normalisation du signe typographique `−`, le contrôle de présence des
symboles dans l'extrait et la conversion explicite pourcentage/fraction ont
également été lus dans la qualification finale. Cette revue n'a pas ajouté
un banc exhaustif de compréhension de texte naturel : une présence lexicale
ne certifie pas à elle seule la bonne association entre actif, montant et intention.

Le choix `deepen` d'Agent1, auparavant sans effet, dispose dans le code relu
d'un approfondissement puis d'une possibilité de retour. Ce chemin a été
**inspecté**, pas exécuté par les 14 tests de cette revue. Il ne faut donc pas
présenter ces tests comme la preuve d'une recherche scientifique AWS réussie.

## Propriétés effectivement vérifiées

1. **Propriété et lecture.** Une écriture avec identifiant/type/rôle incompatible,
   une dépendance non observée ou un `read_set` modifié par le worker est refusée.
2. **Atomicité de correction.** Une correction structurée supprime immédiatement
   le problème, l'analyse et la vue obsolètes du snapshot courant. Les anciens
   octets et hashes restent accessibles comme historique.
3. **Invalidation dépendante.** Les descendants invalidés ne sont plus utilisables.
   Une capture documentaire explicitement dépendante du seul fait `currency`
   reste réutilisable après changement de `capital_cad`, dans la fixture testée.
4. **Résultat tardif.** Un commit calculé avant la correction ne peut remplacer
   le run actif ; commencer une nouvelle tâche sur ce vieux run est aussi refusé.
5. **Reprise après commit.** Réouvrir le Store retrouve le retour sauvegardé.
   Rejouer `begin_task`, `committed_task` et `commit` n'ajoute pas de révision.
   Ce test couvre la frontière commit/retour, sans tuer réellement un processus
   pendant l'écriture SQLite.
6. **Reprise d'un outil.** Un reçu d'outil réussi est réutilisé après réouverture,
   sans nouvel appel au callback, pour la même tâche/outil/entrées.
7. **Variante.** Une variante reçoit un autre dossier et un autre run, reprend les
   faits utiles et leurs changements explicites. La révision, l'analyse et la vue
   du parent restent inchangées.
8. **Affichage distinct d'un accord.** L'événement d'affichage ne change pas la
   révision financière, indique `accepted=false` et exige une vue encore courante.
   Le test porte sur ce contrat serveur, pas sur la peinture réelle du navigateur.
9. **Garde de qualification.** Une allocation numérique absente de la déclaration
   ne devient pas un fait à partir d'une réponse modèle simulée.
10. **Choix d'Agent2.** Une demande de clarification bloque effectivement
    l'exécution du calcul financier.

Les liens pertinents sont `Store.transaction`, `_invalidate`, `revise`,
`begin_task`, `commit`, `operation`, `snapshot` et `record_display`, dans
[`store.py`](../../alphaforge_app/decision/store.py), et `_agent0` / `_agent2`,
dans [`service.py`](../../alphaforge_app/decision/service.py).

## Vérification complémentaire du verrou de tentative

Après ajout du verrou, deux processus Python distincts ont ouvert **le même
Store temporaire**, puis demandé la même opération identifiée par tâche, nom
d'outil et entrées. Le callback simulé écrivait un marqueur et attendait 0,3 s,
pour que le deuxième processus arrive pendant son exécution. Aucun appel
extérieur n'a eu lieu.

Résultat observé :

```json
{
  "child_exit_codes": [0, 0],
  "execution_count": 1,
  "attempt_count": 1
}
```

Cette vérification ad hoc a été exécutée après le correctif ; elle n'est pas
un test permanent de la suite des 14. Elle couvre deux processus locaux sur
le système de fichiers de cette machine. Elle ne valide pas un montage réseau
ni tous les comportements de verrouillage d'autres plateformes.

## Limites de la conclusion

Le snapshot utilise une transaction de lecture SQLite et les artefacts sont
stockés par hash avec vérification à la lecture. Ces choix ont été inspectés,
mais cette revue ne constitue pas une preuve formelle de toutes les
intercalations concurrentes ni de résistance à une panne matérielle.

Une interruption après envoi AWS et avant enregistrement du reçu peut laisser
l'issue distante inconnue. Le verrou empêche des appels locaux identiques
simultanés dans le cas testé ; il ne garantit pas une facturation exactement
une fois après ce type de panne. Aucun crash en cours d'appel AWS n'a été
provoqué ici.

Les tests de propriété vérifient les contrats d'écriture programmatiques. Ils
ne prouvent pas la fidélité sémantique de toutes les interprétations d'un LLM.
De même, un pointeur résolu et une vue fidèle peuvent référencer un calcul faux :
les contrôles financiers, documentaires, de mandat et de validité externe
doivent rester séparés.

Cette revue n'a ni validé l'interface complète ni revendiqué quatre agents
AWS exécutés. Les essais d'intégration réels, leurs identifiants de requête
et les traces navigateur relèvent des comptes rendus de l'intégrateur.
