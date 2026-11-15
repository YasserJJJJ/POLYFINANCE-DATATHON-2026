# Prompt 3 — Dossier de conception à valider

**15 novembre 2026. Le fonctionnement est conçu ; sa construction attend ta validation.**

La proposition repose sur quatre agents aux responsabilités distinctes, un dossier partagé versionné et des retours ciblés lorsqu’un besoin, une preuve ou un calcul change. Les agents proposent leurs modifications ; un noyau déterministe contrôle les droits, les versions et les dépendances avant de les accepter.

**Commencer par le [schéma visuel](architecture.png), puis le [fonctionnement cible](01_architecture_et_fonctionnement.md).**

| Livrable | Contenu |
|---|---|
| [Architecture et fonctionnement](01_architecture_et_fonctionnement.md) | Quatre transformations, dossier, graphes distincts, résolution récursive, partage, invalidation et décisions soumises à validation |
| [Contrats d’échange](02_contrats_echanges.md) | Contrat de chacun des quatre agents, objets, `ChangeSet`, droits, versions, erreurs et méthodes extensibles |
| [Décisions techniques motivées](03_decisions_techniques.md) | LangGraph, Strands Graph/Harness, moteur explicite, Step Functions, AgentCore ; stockage, concurrence, reprise, route AWS et coûts |
| [Parcours et contrôles](04_parcours_et_controles.md) | Interventions humaines, cinq contrôles, fidélité des explications et 20 scénarios de réception futurs |
| [Robert : dossier expliqué](05_exemple_financier.md) | Retrait 30 000 → 40 000 CAD, lacune de preuve, formulation, résultats antérieurs, optima multiples et réouverture |
| [Robert : dossier rempli en JSON](exemples/robert_dossier.json) | Objets versionnés, questions, preuves, tâches et vues illustratives, avec provenance des résultats P1/P2 |
| [Schéma PNG](architecture.png) · [SVG](architecture.svg) · [Mermaid](architecture.mmd) | Parcours principal, responsabilités/outils, dossier, noyau, retours et interventions humaines |
| [Vérifications documentaires](verification_conception.json) | Contrôles de cohérence des fichiers livrés ; à distinguer des tests du futur système |

## Ce qui est proposé

1. **Quatre rôles réels** : qualifier → rechercher → résoudre → restituer, avec des sorties et droits différents.
2. **Un dossier qui fait autorité** : mandat, questions, preuves, calculs, contrôles et vues portent leurs versions. Une correction ne réécrit pas l’histoire.
3. **Des approfondissements récursifs** : une découverte peut rouvrir une hypothèse parent ; les pièces indépendantes restent réutilisables.
4. **Une conclusion limitée par ses preuves** : déclaré, extrait, supposé et inconnu restent distincts ; le contrôle du calcul ne vaut pas validation de son applicabilité.
5. **Une réalisation locale proposée** : SQLite et artefacts immuables ; LangGraph premier moteur à qualifier, Strands Graph alternative. Toutes les inférences suivent la route AWS convenue.

Le dossier Robert est une **reconstitution pour validation**, pas une nouvelle exécution de quatre agents. Ses nombres viennent des expériences P1/P2 ; les messages, événements de passage entre agents et vues illustrent le fonctionnement futur. Une réserve abstraite permet le calcul conditionnel ; aucun instrument réel n’est déclaré validé.

## Ce qui attend ton accord

La validation demandée porte sur le **fonctionnement cible** et ses contrats. Aucun changement de direction par rapport au cadre précédent n’est proposé.

Après validation, choix final du moteur, versions de bibliothèques, tables, adaptateurs et mécanismes de reprise peuvent être tranchés techniquement dans ce cadre. Fusionner un rôle, réduire les demandes à un allocateur figé, abandonner la provenance, changer la route d’inférence ou passer à un service partagé demanderait un accord distinct.

Aucune interface, aucun moteur ni ressource cloud n’a été construit ou modifié pendant cette conception.
