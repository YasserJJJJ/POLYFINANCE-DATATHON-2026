# Questions de recherche qui changent les décisions

15 novembre 2026. Cette note distingue les conclusions appuyées par les lectures et les choix de conception encore à tester. Aucun changement de produit n’a été réalisé.

## Arbitrages méthodologiques

| Question | Ce que les sources permettent de retenir | Décision proposée pour AlphaForge |
|---|---|---|
| Commencer par un questionnaire complet ? | FPSB demande un mandat convenu ; les renseignements nécessaires dépendent du service. Les exigences de convenance visent une relation/activité définie, pas toute demande d’information. | Agent 0 distingue recherche factuelle, pédagogie, comparaison et décision personnelle avant de demander des données. Ne recueillir que ce qui sert le mandat. |
| Un score suffit-il à formaliser le profil ? | 31-368 critique les réponses combinées et divergences ignorées ; la psychométrie renseigne une composante. | Registre multidimensionnel, daté et sourcé ; éventuelle étiquette de synthèse expliquée, jamais substitut au dossier. |
| Faut-il appliquer `min(tolérance, capacité)` ? | L’orientation « plus faible » existe dans U036 ; aucune échelle numérique naturelle commune n’y est donnée. | Contraintes séparées et justification. Ne pas coder une fonction minimum de nombres fabriqués. Un agrégateur numérique exige une validation distincte. |
| Un objectif exigeant autorise-t-il plus de risque ? | FPSB/FP Canada et IG31-103 prévoient discussion d’objectifs irréalistes. | Faire calculer la faisabilité, puis discuter contribution, échéance ou objectif ; ne pas convertir le rendement requis en tolérance. |
| La question suivante doit-elle maximiser la VOI ? | Les méthodes formelles utilisent utilités, distributions/ensembles et conséquences définis. OPEN ajoute un modèle de préférences explicite. | D’abord une règle transparente de matérialité ; tester VOI/regret sur un espace borné avant d’en revendiquer le calcul. |
| Un LLM peut-il confirmer seul un profil ? | Les études de préférences n’établissent pas la validité d’un profil financier ; les pratiques professionnelles requièrent qualité et confirmation des renseignements. | Extraction avec phrase source, inconnues, correction et confirmation explicite des éléments déterminants. |
| Les préférences ESG donnent-elles une note de produit ? | ESMA distingue préférence et caractéristiques des instruments ; le régime européen est spécifique. | Agent 0 définit l’exclusion ou le compromis ; Agent 1 recherche la preuve datée ; Agent 2 marque l’admissibilité comme inconnue si elle manque. |
| Les aides médicales prouvent-elles la qualité financière ? | Cochrane/IPDAS donnent méthodes et effets dans les décisions de santé. | Adapter la structure et les mesures avec prudence ; aucune promesse de taille d’effet financière. |
| Une explication conversationnelle est-elle meilleure ? | Miller fournit un cadre social ; Bansal, Buçinca et Bertrand montrent des effets dépendant de la tâche et des mesures. | Tester fidélité, compréhension et usage approprié séparément ; ne pas optimiser uniquement confiance, satisfaction ou clic d’acceptation. |
| Faut-il imposer une réflexion préalable ? | Certaines interventions réduisent l’accord erroné, avec coûts et effets variables ; attente factice dans une condition de laboratoire. | Intervention ciblée, motivée et honnête ; toujours mesurer charge et abandon. Aucun faux traitement ni délai artificiel présenté comme calcul. |
| Un dotplot rend-il les probabilités « réelles » ? | Les travaux visuels portent sur une distribution donnée et une tâche précise. | Dire de quel modèle viennent les points. Distinguer incertitude de réalisation, de paramètres, de modèle et manque de données. Pas de distribution sans fondement. |
| Quel indicateur de qualité retenir ? | DCS, DQI et numératie mesurent des construits différents ; lisibilité et juges LLM sont insuffisants seuls. | Exactitude, fidélité, adéquation au mandat, compréhension, révision et effort, évalués séparément. |
| Une correction doit-elle réexécuter toute la chaîne ? | Processus professionnel itératif et interaction corrigeable ; pas de prescription de graphe informatique. | Recalculer les dépendances affectées, conserver les autres pièces avec leur périmètre. Cette gestion des dépendances est une proposition d’ingénierie à tester. |

## Une expérience future complète, sans la coder

**Entrée libre.** « J’ai vu beaucoup de nouvelles sur ce titre. Est-ce une bonne idée pour moi ? » Agent 0 commence par préciser le sens de la décision : comprendre le titre, comparer un scénario ou modifier un portefeuille. Il présente les informations déjà connues et demande l’information manquante qui peut modifier le choix.

**Mandat révisable.** Le dossier montre objectifs et échéances distincts, liquidité, faits confirmés, inconnues et contradictions. Un profil de démonstration est explicitement fictif. Le choix Robert/Amira/Mateo ne doit pas remplacer l’entretien ni faire apparaître des convictions non fournies.

**Recherche réelle.** Agent 1 ouvre un plan de recherche : faits sur les instruments, données nécessaires, méthodes et objections plausibles. Il rend un dossier qui sépare une source consultée, un passage soutenant une affirmation et une limite non résolue. « Rien trouvé » reste différent de « cette propriété n’existe pas ».

**Analyse et alternatives.** Agent 2 examine le statu quo et les solutions admissibles, calcule leurs conséquences selon des hypothèses identifiables, et indique ce que les données ne permettent pas de trancher. L’historique ne devient pas une prévision. Une contrainte contradictoire revient à Agent 0 ; un fait indispensable manquant revient à Agent 1.

**Examen adapté.** Agent 3 présente une conclusion courte, ses compromis, les alternatives pertinentes et les facteurs qui pourraient la changer. L’utilisateur peut demander « explique ce terme », « montre la preuve » ou « et si mon échéance change ? ». Ces trois demandes déclenchent respectivement une explication, une recherche ou une nouvelle qualification suivie d’un calcul.

**Révision explicite.** Le dossier indique ce qui change entre les versions, qui l’a demandé et pourquoi. Revenir à la version précédente restaure un dossier identifiable ; cela ne transforme pas un ancien résultat en résultat recalculé. L’export conserve les hypothèses, inconnues et références du résultat effectivement examiné.

**Arrêt motivé.** Une issue valable peut être une option conditionnelle, un maintien du portefeuille, une comparaison pédagogique, une question restante ou l’impossibilité de conclure. L’application n’a pas besoin d’inventer une recommandation pour paraître active.

## Ce que cette revue ne tranche pas

La revue ne choisit pas encore un questionnaire financier, un modèle d’utilité, une pondération ESG, un format graphique universel ni un seuil de qualité humaine. Elle fournit les raisons d’expérimenter ces candidats et les erreurs qu’ils doivent éviter. La fusion ou le remplacement d’une des quatre fonctions reste hors autorisation.

