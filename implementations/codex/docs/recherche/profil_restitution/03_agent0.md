# Agent 0 — Qualifier la décision avant de rechercher une solution

Revue du 15 novembre 2026. **Proposition méthodologique, sans changement du produit.** Les quatre fonctions demandées restent distinctes. Une fonction professionnelle ne présuppose ni un seul appel au modèle ni un titre professionnel attribué au logiciel.

## Responsabilité

L’Agent 0 transforme la demande en **mandat vérifiable**, en distinguant ce que la personne affirme, ce que le système calcule, les hypothèses provisoires et ce qui reste inconnu. Il ne transforme pas automatiquement toute question sur un titre en proposition d’allocation.

« Explique-moi ce FNB », « compare ces deux titres » et « faut-il modifier mon portefeuille ? » engagent des décisions différentes. Le dernier cas exige davantage d’information personnelle et de contraintes que le premier. Une réponse pédagogique peut être donnée sans simuler une connaissance complète du client.

Cette fonction dérive du cadrage de la relation, de la collecte et de l’évaluation des objectifs décrits par FPSB et FP Canada [P004–P007]. Le règlement canadien 31-103, son instruction générale et l’avis 31-368 donnent un fondement plus précis à la connaissance du client et à la convenance [P001–P003, U036]. **Leurs obligations s’appliquent aux personnes et activités visées par ces textes, avec des exceptions et règles d’organismes d’autoréglementation ; elles ne deviennent pas automatiquement des obligations du prototype fictif AlphaForge.**

## Questions dont il est responsable

- Quelle décision faut-il éclairer, à quelle date, dans quelle devise, et qu’est-ce qui constituerait une réponse utile ?
- Quelles informations proviennent directement de l’utilisateur, lesquelles sont confirmées, contradictoires ou seulement illustratives ?
- Quels objectifs, besoins de liquidité, échéances et contraintes peuvent exclure une option avant même de comparer ses rendements ?
- Quelles informations personnelles sont nécessaires à cette décision précise ?
- Quelles questions documentaires l’Agent 1 doit-il résoudre, et quels calculs de faisabilité l’Agent 2 doit-il examiner ?
- Quelles préférences de restitution l’Agent 3 devra-t-il respecter sans masquer une limite déterminante ?

## Entrées, documents de travail, sorties

| Objet | Contenu proposé |
|---|---|
| Entrées | Demande originale ; corrections et échanges précédents autorisés ; portefeuille fourni ; données personnelles explicitement communiquées ; profil fictif éventuellement sélectionné ; date et périmètre des données. |
| Registre d’assertions | Valeur, unité, provenance exacte, date, auteur, statut `DECLARE`, `CONFIRME`, `CALCULE`, `HYPOTHESE`, `INCONNU` ou `CONTRADICTOIRE`. Ces statuts sont proposés pour AlphaForge. |
| Mandat versionné | Décision et périmètre ; objectifs hiérarchisés ; horizon de chaque objectif ; liquidité ; contraintes fermes et préférences négociables ; ce qui est hors mandat. |
| Registre des contradictions | Deux assertions en conflit, conséquence possible sur la décision, question de résolution et réponse confirmée. Une contradiction reste visible tant qu’elle n’est pas résolue. |
| Plan de clarification | Question, raison de la poser, réponses susceptibles de changer l’analyse, caractère indispensable ou facultatif. |
| Transmission à Agent 1 | Sous-questions de recherche, objets/produits, date d’information, critères ESG définis, preuves manquantes et décision influencée. |
| Transmission à Agent 2 | Contraintes exploitables et unités ; données disponibles ; hypothèses autorisées ; calculs de faisabilité demandés. |
| Transmission à Agent 3 | Niveau de détail souhaité, vocabulaire à expliciter, décisions à faire examiner et questions encore ouvertes. |

La sortie ne doit pas être un simple score « prudent/modéré/dynamique ». Ces étiquettes peuvent résumer un profil documenté ; elles ne remplacent pas ses composantes ni leurs causes.

## Méthode proposée

1. **Déterminer le type de demande.** Éducation, recherche factuelle, comparaison conditionnelle ou modification de portefeuille. Relever les conséquences réelles ou fictives du scénario. Ne pas attribuer à un personnage fictif des avoirs ou convictions officiels absents du dossier.
2. **Extraire sans compléter silencieusement.** « Je veux préserver mon argent » exprime un objectif ; cela ne donne ni un horizon, ni une perte acceptable, ni un revenu, ni une probabilité de succès. Une extraction s’appuie sur une phrase source. Une inférence utile est étiquetée et proposée à confirmation.
3. **Séparer les dimensions.** Situation et capacité financières, volonté de supporter le risque, connaissances/expérience, objectifs/besoins, horizon et liquidité. Les préférences ESG sont décrites en critères opérationnels ; une source absente ne devient pas un score ESG moyen.
4. **Examiner les incompatibilités.** Exemple : échéance proche, absence de réserve liquide et souhait de croissance forte. Le système ne relève pas la tolérance pour rendre la solution faisable. Il demande ce qui peut changer : échéance, contribution, dépenses, montant cible ou choix d’objectif.
5. **Poser la question déterminante suivante.** Au départ, utiliser des règles explicites de matérialité : une information peut-elle modifier les options admissibles, les besoins de recherche ou la conclusion ? Cette procédure est une heuristique vérifiable. Ne pas la présenter comme une valeur de l’information calculée.
6. **Faire confirmer le mandat lisible.** Présenter les faits déterminants, inconnues et hypothèses dans un langage simple. La confirmation d’un scénario hypothétique n’est pas un consentement à une transaction.
7. **Réviser par dépendances.** Quand une réponse change, dater le nouveau mandat et marquer les recherches, calculs et explications qui dépendent de l’ancien comme à réexaminer. Conserver les versions précédentes et le motif de révision.

## Tolérance, capacité et risque nécessaire : ne pas confondre

L’avis 31-368 indique qu’un profil global devrait refléter la plus faible de la tolérance et de la capacité ; un autre choix exige une justification claire [U036, p. 5 PDF]. Il critique aussi les questionnaires sommaires, les questions qui combinent plusieurs dimensions et les divergences non résolues. Ce passage **ne définit pas deux scores numériques commensurables**. Écrire `min(tolerance_score, capacity_score)` exige donc une échelle et une règle de décision justifiées séparément ; le texte réglementaire ne les fournit pas.

La capacité inclut les moyens de supporter une perte et les besoins financiers. La tolérance concerne la volonté d’accepter le risque. Un rendement requis pour atteindre un objectif est un résultat de calcul sous hypothèses ; ce n’est ni une préférence révélée ni une autorisation de prendre davantage de risque. Si ce rendement paraît incompatible avec les contraintes, il faut discuter la faisabilité et réviser le mandat [P002 ; P005–P006].

Une réponse à un questionnaire psychométrique n’est pas une mesure exhaustive de ces dimensions. La cohérence interne de Grable–Lytton ne démontre pas, seule, une validité prospective pour des investisseurs francophones actuels [P019]. Les associations avec des portefeuilles détenus peuvent dépendre des moyens, connaissances et choix antérieurs. Une adaptation de langue, d’items ou de contexte demande un examen de validité et de droits ; un score ne doit pas être inféré depuis l’âge, le genre ou un personnage fictif.

## Élicitation adaptative : progression possible, garanties conditionnelles

Chajewska et al. [U037] utilisent une distribution sur les fonctions d’utilité et une valeur attendue de l’information ; Boutilier et al. [U084/P017] définissent un regret maximal sur un ensemble de fonctions compatibles avec les réponses. Ces formulations peuvent guider une expérimentation, mais elles supposent un ensemble de décisions, des conséquences et des préférences représentables.

OPEN [U082/P012] combine un espace de caractéristiques, un modèle de préférences et des questions générées. Son expérience sur des préférences d’articles de presse ne valide pas un profil financier. Un score de confiance verbal d’un LLM ne constitue pas une distribution d’utilité calibrée. Pour AlphaForge, la priorité est le registre des inconnues et des contradictions ; un mécanisme formel d’élicitation n’est adopté qu’après comparaison expérimentale à ce socle.

## Quand clarifier, approfondir ou renvoyer

| Situation | Action |
|---|---|
| « Préserver » peut signifier capital nominal, pouvoir d’achat ou faible fluctuation | Clarifier avant une proposition d’allocation ; une explication des trois sens peut déjà être utile. |
| Échéance ou besoin de liquidité incompatible avec le portefeuille proposé | Faire préciser ou réviser le mandat ; transmettre une question de faisabilité à Agent 2. |
| Préférence ESG exprimée sans critère ni priorité | Clarifier la préférence ; Agent 1 recherche les preuves correspondantes. |
| Information fiable sur un produit manque | Transmettre à Agent 1, pas inventer une valeur par défaut. |
| Objectif chiffré, versements et horizon connus | Agent 2 calcule les hypothèses nécessaires ; Agent 0 fait examiner les compromis si elles sont incompatibles. |
| Changement de situation, de préférence ou correction de données | Nouvelle version du mandat, puis réexamen des sorties dépendantes. |
| Demande hors compétence, conflit non résolu ou données critiques absentes | Réponse partielle ou abstention explicite, avec la prochaine information ou intervention nécessaire. |

## Erreurs à détecter et critères de réussite

Le banc d’évaluation doit couvrir demandes courtes/longues, français ordinaire, faits manquants, corrections, demandes pédagogiques et contradiction entre profil déclaré et liquidité. Il doit contenir des cas où **aucune clarification supplémentaire n’est nécessaire**, pour ne pas récompenser un interrogatoire excessif.

Mesures proposées : exactitude d’extraction avec provenance ; rappel des contradictions connues ; taux de faits inventés ; qualité des questions qui changent réellement la décision ; questions personnelles inutiles ; effort de réponse ; proportion de mandats correctement révisés ; maintien des inconnues justifiées. La référence est un dossier annoté par des personnes compétentes avec arbitrage des désaccords, pas le jugement du même LLM sur sa propre réponse. Aucun de ces tests n’a été exécuté dans cette revue.

