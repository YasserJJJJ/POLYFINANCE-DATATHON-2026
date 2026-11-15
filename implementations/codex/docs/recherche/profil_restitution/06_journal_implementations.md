# Journal des méthodes et implémentations candidates — Agents 0 et 3

15 novembre 2026. **Statut général : propositions documentées, non intégrées au produit et non évaluées empiriquement dans cette revue.** Les lectures de dépôts sont statiques ; aucun code tiers n’a été exécuté. Toute éventuelle inférence d’évaluation doit rester sur la route AWS autorisée.

## QUAL-01 — Extraction de mandat avec provenance et contradictions

**Problème.** Une demande libre contient des objectifs, faits, préférences et ellipses ; des valeurs implicites ou anciennes peuvent être traitées à tort comme confirmées.

**Fondements.** FPSB/FP Canada [P004–P007], 31-103/IG/31-368 [P001–P003, U036], Amershi [U354]. Le schéma informatique est notre adaptation.

**Entrées et méthode.** Extraction contrainte en assertions `valeur/unité/source/date/statut`, citations de l’énoncé utilisateur, règles déterministes sur unités et incompatibilités connues. Chaque contradiction forme une paire d’assertions et une question de résolution. Un horizon unique n’écrase pas des échéances par objectif.

**Hypothèses.** L’utilisateur peut corriger et confirmer ; certaines incohérences ont une définition non ambiguë. Les incompatibilités normatives non triviales exigent une analyse, pas un simple test de type.

**Protocole proposé.** Constituer des dossiers fictifs francophones avec demandes factuelles, besoin d’allocation, données manquantes, changements d’avis et valeurs contradictoires. Annotation par deux personnes compétentes avec arbitrage. Comparer extraction seule, extraction avec provenance/règles et entretien structuré. Mesurer exactitude, faits inventés, rappel des contradictions, questions inutiles et correction après réponse. Prévoir un lot de test séparé avant ajustement des prompts.

**Décision d’adoption.** Prioritaire comme socle. Bloquer toute conclusion dépendant d’un fait critique inventé ; mesurer les taux sur un banc défini sans annoncer zéro risque dans le monde réel.

## QUAL-02 — Questions générées et cas limites, inspirés de GATE

**Artefact examiné.** [GATE](https://github.com/alextamkin/generative-elicitation) ; article v1 [P013/U083]. Licence MIT effectivement lue : blob `b08df11132991858c0564af3066f648d1b305cd9`. `utils.py` blob `b58443b0300e7a77f9acd527a0b03d594579318d`, lignes 1–170 examinées : imports et appels directs à `openai.ChatCompletion` et `openai.Completion`. Le préenregistrement U199 est repéré, non audité.

**Adaptation nécessaire.** Conserver l’idée de questions ouvertes et de cas discriminants, reconstruire le transport d’inférence AWS, réexaminer les prompts, le cache et les données. Lire le reste du chemin exécutable et les dépendances avant toute exécution ; les deux fichiers inspectés ne constituent pas un audit complet.

**Hypothèses et limites.** Un cas généré peut révéler une préférence, mais aussi la suggérer. Les domaines email/contenu/morale ne valident pas le risque financier. L’assertion « ceci est votre préférence » doit revenir à une déclaration confirmée.

**Protocole.** Comparer à QUAL-01 et à un entretien à questions fixes, sur les mêmes dossiers et budgets. Mesurer changements utiles du mandat, propositions suggestives, incohérences, effort, stabilité lors d’une reformulation et décisions après clarification. Évaluer avec de vrais participants consentants avant toute promesse d’ergonomie ; des utilisateurs simulés ne suffisent pas.

**Décision.** Candidat expérimental, pas code prêt à brancher. Conserver les avis MIT lors de réutilisation ; licences des données et modèles examinées séparément.

## QUAL-03 — Valeur de l’information, information bayésienne ou regret minimax

**Problème.** Choisir une question dont la réponse peut réellement changer la décision, puis savoir quand arrêter.

**Fondements/formulations.**

- **VOI myope** [U037] : valeur attendue de la meilleure décision après une réponse, moins valeur actuelle et coût de la question. Il faut une distribution de réponses/utilités justifiée.
- **OPEN** [P012/U082] : sélection d’expérience informative dans un espace de caractéristiques et un modèle Bradley–Terry ; le gain d’information sur les préférences n’est pas, à lui seul, un gain d’utilité financière.
- **Regret minimax** [P017/U084] : pour une action \(a\), examiner \(\max_{u\in U}[\max_{b\in A}u(b)-u(a)]\), puis choisir \(a\) minimisant cette quantité. \(A\) et \(U\) doivent être définis et non vides.

**Adaptation proposée.** Un petit univers d’alternatives et de conséquences explicites, avec préférences partielles confirmées. Aucun score de capacité ou utilité ne provient d’un stéréotype de persona. Une question susceptible de rendre les contraintes incompatibles doit avoir une issue « contradiction » et non une réponse ajustée.

**Code/licence.** Manuscrits lus ; aucun dépôt exécutable validé pour OPEN ou le solveur original minimax. Ne pas inventer une licence. Une implémentation indépendante, si retenue, doit documenter dérivation, solveur et versions.

**Protocole.** Sur des cas synthétiques aux utilités connues, comparer question fixe, règle de matérialité, VOI et minimax : regret final, nombre/coût de questions, sensibilité au prior, erreurs de réponse, préférences hors modèle, contraintes contradictoires. Vérifier les petits cas par énumération exhaustive. Puis tester validité et acceptabilité avec le public cible.

**Décision.** Retenir seulement si gain démontré sur la référence simple et robustesse aux hypothèses. Le fonctionnement sur utilités synthétiques valide le code conditionnellement ; il ne valide pas l’utilité réelle d’un investisseur.

## QUAL-04 — Banc d’ambiguïté et de nécessité de clarification

**Source.** CLAMBER [U016/U202]. README lu : question, contexte, question de clarification, indicateur de nécessité, catégorie et sous-classe. Inventaire racine examiné : aucune `LICENSE` observée ; cela ne permet pas d’affirmer que les données sont libres.

**Adaptation.** Utiliser la taxonomie comme inspiration de cas originaux : référence ambiguë, date omise, demande inconnue, conflit interne, question parfaitement déterminée. Dossiers financiers français et termes comme « sécurité », « risque » et « vert ».

**Protocole.** Prédire s’il faut clarifier, identifier l’information manquante et proposer une question qui résout le manque sans présupposer une réponse. Mesurer faux positifs sur les demandes déjà claires, rappel des ambiguïtés critiques et résolution après réponse.

**Décision.** Prioritaire pour évaluer Agent 0 ; réutilisation du dataset conditionnée à droits établis et lecture des exemples/étiquettes.

## REST-01 — Matrice de fidélité et restitution à niveaux

**Fondements.** CFA V(B)/V(C) [R002/R003], IPDAS 5.0 [P023], Amershi [U354], Miller [U218]. L’ancrage sur une source et la fidélité à un calcul sont deux contrôles différents.

**Méthode.** Chaque assertion importante renvoie à une pièce, un résultat ou une hypothèse. Un résultat structuré alimente les chiffres et graphiques. Les variantes brève/détaillée changent le vocabulaire et la profondeur ; les faits et limites déterminants restent invariants.

**Protocole.** Injecter mauvais signe, mauvaise devise, période différente, citation voisine mais non probante, résultat ancien et réserve retirée. Vérifier automatiquement égalité des données structurées, puis faire examiner l’implication des phrases et la matérialité des omissions. Mesurer aussi une restitution correcte mais peu compréhensible.

**Décision.** Socle prioritaire. Ne pas mesurer seulement le nombre de citations ou la similarité textuelle entre versions.

## REST-02 — Tableau des compromis et représentations de l’incertitude

**Candidats.** Tableau comparatif original, historique clairement daté, distribution conditionnelle uniquement si fondée ; dotplots/HOPs/fan charts comme formats à comparer [U208–U210, U091]. Option Grid [U207] est un produit avec conditions d’accès non établies ; ne pas copier ses contenus.

**Hypothèses.** Alternatives comparables, coûts et périodes cohérents, données suffisantes. Un générateur de scénarios doit être distingué d’une loi prédictive validée.

**Protocole.** Présenter la même information et les mêmes hypothèses sous plusieurs formats ; contrebalancer l’ordre. Mesurer lecture correcte des probabilités/quantiles, reconnaissance du risque de perte, distinction modèle/réalité et choix conforme à une contrainte explicite. Inclure cas sans distribution crédible : la bonne sortie est de conserver le manque.

**Décision.** Ne choisir aucun format comme universel avant ce test. La préférence esthétique est une mesure secondaire ; un diagramme plus convaincant peut aussi accentuer une confiance injustifiée.

## REST-03 — Compréhension, réflexion ciblée et usage approprié

**Fondements.** Teach-back [P018], Buçinca [P010], Bansal [P011], Bertrand [P027].

**Méthode candidate.** Demander une courte reformulation du compromis décisif ou une réponse initiale avant d’afficher l’explication, seulement quand utile. Accepter « je ne sais pas ». Expliquer pourquoi la question aide ; ne pas simuler un calcul pendant un délai imposé.

**Protocole.** Comparer restitution simple, question volontaire et intervention ciblée, avec recommandations exactes, erronées et indécidables. Randomisation des conditions ; comptabiliser séparément acceptation correcte, rejet correct, rejet excessif, compréhension immédiate/différée, temps, effort et abandon. Examiner variations selon connaissances, langue et accessibilité, sans traiter une catégorie démographique comme déterminant de capacité.

**Décision.** Poursuivre si compréhension et usage approprié s’améliorent avec coût acceptable ; ne pas adopter sur la seule hausse de confiance. Absence de significativité n’est pas preuve d’équivalence ou d’absence d’effet : dimensionner l’étude pour le contraste visé.

## REST-04 — Mémoire, correction et versions

**Fondements.** Revue professionnelle du plan [P004–P007], conservation CFA [R003], correction/mémoire/contrôle Amershi [U354].

**Méthode proposée.** Historique des faits confirmés, hypothèses, résultats et corrections ; dépendances explicites. Un « retour arrière » rétablit une version avec ses dates ; l’export embarque le même identifiant/version que le résultat affiché. Une préférence inférée n’entre pas silencieusement en mémoire durable.

**Protocole.** Conversations avec modification d’horizon, retrait d’une exclusion, correction d’un poids, preuve remplacée, retour arrière puis nouvelle demande. Vérifier absence de mélange entre versions, invalidation des calculs dépendants et conservation des corrections. Tester les demandes concurrentes et réponses arrivant hors ordre.

**Décision.** Prioritaire pour une expérience révisable ; il s’agit d’une proposition future, pas d’une affirmation sur les capacités actuelles du prototype.

## Mesures écartées comme indicateur unique

DCS/DQI, Berlin Numeracy, Big Three, lisibilité automatique ou juge LLM peuvent éclairer certains aspects. Aucun ne mesure seul la qualité d’une décision financière. Les conditions d’usage de DCS sont restrictives pour le profit et les modifications ; l’article Berlin Numeracy ne vaut pas licence de son outil en ligne. Aucune de ces échelles n’est intégrée ou renommée « score de qualité AlphaForge » dans cette revue.

Le plan d’évaluation doit annoncer à l’avance critères principaux, cas critiques, gestion des exclusions, comparateurs, incertitude et méthode d’arbitrage humain. Les budgets et modèles AWS utilisés lors d’un futur essai devront être enregistrés. Les expériences proposées ici ne sont pas des tests déjà réussis.
