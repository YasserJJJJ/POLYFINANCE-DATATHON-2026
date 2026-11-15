# Agent2 — analyse, résolution et validation quantitative

**Responsabilité** : transformer un problème qualifié et des preuves examinées en
résultats financiers calculables, comparer les solutions admissibles et
expliquer les limites de la résolution. Ni profilage automatique ni exécution
d'ordre. Les quatre rôles restent distincts ; les boucles entre eux sont permises.

## Contrat d'entrée

| Objet | Contenu minimal | Contrôle d'Agent2 |
|---|---|---|
| Problème Agent0 | décision demandée, capital simulé, devise, dates/horizons, flux, contraintes incontournables/préférences, seuils et provenance de chaque valeur, inconnues | dimensions, cohérence temporelle, besoin suffisamment défini ; ne pas fabriquer une aversion au risque d'après l'âge |
| Dossier Agent1 | question, versions primaires, passages utilisés, résultats contradictoires, lecture effective, garanties conditionnelles, implémentations candidates | chaque méthode répond à une incertitude du problème ; pas de méthode choisie seulement parce que disponible |
| Données | entités/identifiants, unités, calendrier/timezone, observed_at/published_at/revised_at/retrieved_at, sources, transformations, empreintes, droits d'usage | couverture, doublons, événements, FX, disponibilité à la date simulée, possibilité de réutilisation |
| Plan d'expérience | hypothèses, comparateurs admissibles, pertes/métriques, périodes, paramètres, coût, tolérances, budget pertinent et règle d'arrêt | critères fixés avant résultats ; nouvelles explorations enregistrées |
| État du parcours | version du problème, changements utilisateur, calculs déjà effectués, raisons d'escalade | invalider seulement les résultats dépendants d'une entrée changée |

Un champ manquant n'est pas toujours bloquant. Un scénario peut porter une
hypothèse explicite et réversible. En revanche, une échéance ou un besoin
incontournable inconnu ne devient pas un nombre silencieusement choisi.

## Processus et méthodes envisageables

1. **Audit de l'information et modèle de flux.** Livre des positions et besoins,
   budget et monnaie commune ; trajectoires nettes des apports/retraits/frais.
   Vérifier identité de l'ETF, composition datée, périmètre réellement couvert.
2. **Faisabilité avant classement.** Contraintes nommées, bornes, marge disponible ;
   LP/QP/conique selon le problème. Résultats possibles : admissible,
   infaisable certifié, indéterminé, non borné, erreur de données/formulation.
3. **Comparaison ciblée.** Situation initiale ; ajustement minimal répondant au
   besoin ; référence simple admissible ; stratégie de risque/objectifs justifiée.
   GMV contractée, CVaR, modèle robuste, programmation dynamique, analyse de style
   ou autre méthode peuvent être étudiés. Ce n'est pas un catalogue fermé :
   chacune exige un bénéfice, des hypothèses et un test.
4. **Résolution et diagnostic.** Valeurs, contraintes actives, marges, dualité si
   pertinente, coût de l'ajustement, pluralité des optima, sensibilité. Les prix
   duaux sont locaux et dépendants du modèle ; ils ne sont pas une évaluation
   universelle de la préférence du client.
5. **Validation scientifique.** Formule indépendante sur cas soluble ; contrôle
   numérique ; autres hypothèses et fenêtres ; qualité/couverture de données ;
   tests hors temps adaptés. Un solveur optimal ne valide pas le modèle financier.
6. **Remise à Agent3.** Message orienté décision, résultats exacts et limites,
   ce qui reste inconnu, options à discuter. Tout changement de besoin repasse
   dans le contrat Agent0 ; nouvelle incertitude de méthode/donnée revient à
   Agent1.

## Documents de sortie exigés

- `analysis_contract` : problème, objectif(s), contraintes et unités, hypothèses,
  provenance des seuils, version du jeu de données et date de valorisation.
- `method_card` : formulation mathématique, implémentation/commit/licence,
  hypothèses, domaine de validité, raison de sélection et alternative écartée.
- `solution_bundle` : états du solveur, valeurs non arrondies, allocations
  éventuelles, flux, risques, ensembles de scénarios et leurs dates/probabilités,
  références simples comparables, alternatives proches ou non dominées.
- `validation_report` : références numériques, tolérances, erreurs résiduelles,
  sensibilité, fenêtres, tests et échecs ; ce qui n'a pas été testé.
- `decision_delta` : entrée changée → contrainte/estimation touchée → résultat
  recalculé → explication ; relations causales du calcul, pas causalité de marché
  prétendue.
- `escalation_record` : question requise, conséquence des réponses possibles,
  preuves manquantes, responsable et travaux indépendants encore possibles.

Ces objets sont sérialisables et contiennent dates, unités, identifiants et liens.
Un nombre arrondi pour Agent3 garde sa valeur source et sa règle d'arrondi.
Un verdict ESG garde `covered`, `unknown` et la date des preuves ; inconnu ≠ zéro.

## Erreurs attendues et réaction

| Erreur ou limite | Réaction nécessaire |
|---|---|
| Contradiction entre retrait et portefeuille disponible | isoler le conflit, proposer des options à quantifier, demander une révision via Agent0 ; aucune relaxation silencieuse |
| IIS vide, indéterminé, ou certificat dépendant des tolérances | conserver état technique ; vérifier sous-problème et bornes ; annoncer « diagnostic non obtenu » si nécessaire |
| Optima multiples avec mêmes coûts | présenter les alternatives pertinentes ou obtenir un critère de départage explicite |
| Estimation de moyenne/covariance instable | intervalle/sensibilité, contraction/paramètres alternatifs, réduire la prétention ; pas d'interdiction générale de l'optimisation |
| Modèle de rendement sans calibration crédible | scénarios conditionnels ; ne pas annoncer une probabilité future réelle |
| Données révisées après la date du test | retrouver vintage ou déclarer analyse rétrospective ; un simple décalage temporel ne répare pas |
| FX/cours non synchrones, jours manquants | convention de valorisation expliquée, analyse de sensibilité, pas de zéros artificiels |
| Somme de scores ESG sans périmètre compatible | suspendre agrégation ; faire rechercher les preuves et clarifier la préférence |
| Licence non comprise ou source personnelle incompatible avec diffusion | examen du mode d'usage ou autre source ; ne pas interdire automatiquement GPL |
| Performance positive après multiples essais | journal complet, validation adaptée ; aucun seuil Sharpe magique |

## Critères d'acceptation pour la future refonte

1. Le besoin de retrait modifie l'ensemble admissible et les calculs ; un commentaire
   ajouté après un backtest inchangé ne suffit pas.
2. Les exemples simples retrouvent formule/borne indépendante ; LP/QP rapportent
   résidus, tolérances et état exact. L'IIS montré est infaisable et chaque
   suppression rétablit la faisabilité dans la portée annoncée.
3. Capital multiplié par k : montants multipliés par k si coûts/contraintes
   proportionnels ; les exceptions (coûts fixes, fiscalité, seuils absolus) sont
   explicites. Les flux ne sont pas comptés comme pertes de marché.
4. Scénarios historiques, chocs hypothétiques et trajectoires probabilistes
   ont des étiquettes et hypothèses distinctes. Le terme « garanti » n'est pas
   inféré d'une bonne performance sur échantillon.
5. Toute solution satisfait les contraintes du problème à la tolérance publiée ;
   un comparateur impossible est marqué comme tel, pas classé avec les autres.
6. Une variation d'échéance, de retrait, de plafond, de coût ou de couverture
   entraîne une révision traçable ; des solutions inchangées sont expliquées par
   une marge/invariance calculée.
7. La validation distingue implémentation, modèle, données, usage et interaction.
   Une seconde réponse du même LLM n'est pas qualifiée de validation indépendante.
8. Agent3 peut vérifier chaque chiffre jusqu'au calcul et chaque prémisse jusqu'à
   Agent0 ou Agent1. Aucune bibliothèque, méthode ou architecture agentique ne
   reçoit un plafond arbitraire sans motif utilisateur/scientifique.

## Appui professionnel et limites de transposition

CFA fournit le cadre objectifs/contraintes/IPS ; Boyd les propriétés de formulation
et d'optimalité ; Chinneck l'analyse de l'infaisabilité ; SR 26-2 sépare finalité,
conception, résultats, suivi et gouvernance proportionnée. Cette dernière guidance
vise des établissements bancaires américains et exclut explicitement les modèles
génératifs/agentiques : elle inspire les contrôles d'Agent2 sans certifier
AlphaForge. Le moteur quantitatif et l'agent qui l'utilise requièrent deux
évaluations articulées, pas un unique score de réponse.
