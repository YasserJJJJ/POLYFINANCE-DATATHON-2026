# Agent 3 — Faire comprendre, examiner et réviser la décision

Revue du 15 novembre 2026. **Proposition méthodologique, sans modification de l’interface.** L’Agent 3 reste une fonction distincte de l’Agent 0, de la recherche documentaire et du calcul financier.

## Responsabilité

L’Agent 3 rend une décision **compréhensible, contestable et révisable**. Il explique les solutions examinées, les compromis, les facteurs décisifs et les limites ; il permet de corriger le profil ou une hypothèse et dirige la révision vers l’agent compétent. Il ne se limite ni à reformuler un rapport ni à ajouter un graphique.

Le socle professionnel est la communication de recommandations compréhensibles, l’examen avec le client, la consignation des choix et la révision du plan [P004–P007 ; CFA V(B)/V(C), R002/R003 dans la fiche Agent 1]. La littérature sur l’aide à la décision en santé [P008, P023, U085] apporte des méthodes de présentation et d’évaluation, **pas une preuve de leur efficacité en investissement**.

## Questions dont il est responsable

- La conclusion est-elle fidèle au mandat confirmé, aux résultats calculés et aux preuves effectivement lues ?
- La personne comprend-elle les compromis importants, y compris ceux qui justifient de ne rien changer ?
- Peut-elle distinguer historique, scénario conditionnel, hypothèse et prévision ?
- Quels éléments pourraient modifier la conclusion ? Peut-elle demander leur révision sans recommencer tout le dossier ?
- Un désaccord exprime-t-il une préférence à requalifier, une preuve à rechercher ou un calcul à réexaminer ?

## Entrées, documents de travail, sorties

| Objet | Contenu proposé |
|---|---|
| Entrées | Mandat et version de profil ; dossier de preuves ; comparaison financière avec paramètres et limites ; options non retenues et motifs ; besoins de restitution déclarés. |
| Matrice d’explication | Conclusion → résultat/preuve → hypothèse → limite → conséquence décisionnelle. |
| Tableau de décision | Alternatives comparables, statu quo lorsqu’il est pertinent, bénéfices, risques, coûts, contraintes et inconnues, sur la même période et la même base monétaire. |
| Rapport à niveaux | Vue courte pour décider quoi examiner ; explication des mécanismes et compromis ; détail des sources, données et méthodes. Les limites décisives apparaissent dès la vue courte. |
| Registre d’examen | Questions, corrections, préférences confirmées, accord/désaccord et raisons déclarées. Aucun accord n’est déduit du silence. |
| Demande de révision | Changement demandé, agent destinataire, sorties devenues dépendantes, version précédente et réponse attendue. |
| Dossier exportable | Résultats, paramètres, date des données, versions, sources réellement utilisées, inconnues et raisons d’un éventuel statu quo ou d’une abstention. |

## Méthode proposée

1. **Contrôler la fidélité avant la rédaction.** Vérifier les unités, signes, périodes, options et versions. Une citation doit soutenir la phrase qui la porte ; une trace d’outil indique une action observable, pas la pensée interne du modèle.
2. **Présenter le choix et ses alternatives.** Expliquer ce qui change dans le portefeuille et pourquoi, en tenant compte de l’effet global, des coûts et de la liquidité. Un actif ayant mieux performé historiquement n’est pas pour autant une meilleure solution pour le mandat.
3. **Donner une conclusion conditionnelle.** « Sous ces données et contraintes, A réduit telle exposition, mais implique tel coût ou manque documentaire. » Éviter les labels absolus « optimal », « sûr » ou « conforme » quand le calcul n’en démontre pas les conditions.
4. **Adapter la forme, conserver les faits.** Demander ou observer les besoins exprimés : explication brève/détaillée, vocabulaire, exemple numérique. La version novice et la version experte doivent conserver les mêmes résultats, réserves et alternatives déterminantes.
5. **Rendre les hypothèses examinables.** Pour une modification de capital, d’horizon, de liquidité ou d’exclusion, montrer quelle conclusion dépend de ce paramètre puis lancer une véritable révision. Ne pas afficher un curseur qui ne change que le texte.
6. **Vérifier la compréhension lorsque cela aide.** Une question non punitive peut demander quel compromis l’utilisateur retient, ou ce qui pourrait empêcher de suivre l’option. Le teach-back est une adaptation à tester, non un examen obligatoire de compétence.
7. **Réviser et tracer.** Une correction du profil revient à Agent 0 ; une source manquante à Agent 1 ; une sensibilité ou un calcul à Agent 2. La nouvelle restitution explique ce qui a changé et pourquoi. L’ancienne reste identifiable comme ancienne.

## Incertitude et visualisation

Les courbes historiques décrivent une période observée. Une distribution simulée décrit les sorties d’un modèle sous hypothèses. Ses quantiles ne sont pas des fréquences établies des futurs réels. Une vingtaine de points dans un graphique ne représente donc pas vingt avenirs réels équiprobables. Il faut indiquer le mécanisme générateur, ses paramètres, sa calibration éventuelle et les incertitudes qu’il omet.

IPDAS 5.0 [P023, octobre 2026] recommande notamment des comparaisons équilibrées, des preuves applicables, des sources et dates identifiables ; ses critères détaillés prévoient des périodes, échelles et dénominateurs comparables. Trois de ses critères essentiels concernent spécifiquement le dépistage : ils ne sont pas des exigences financières universelles. Dans cette version, le critère relatif à l’incertitude autour des probabilités est classé parmi les critères d’amélioration. **L’exigence proposée pour AlphaForge de montrer l’incertitude déterminante est notre choix méthodologique, pas une fausse attribution à un seuil IPDAS obligatoire.**

Les résultats favorables aux dotplots dans des décisions de transport [U089/U208] ne permettent pas de déclarer ce format universellement supérieur. D’autres travaux portent sur les révisions du PIB ou les prévisions macroéconomiques [U214, U091] et utilisent d’autres tâches et représentations. Le bon test compare compréhension, décisions et erreurs sous la même information ; il ne se limite pas à une préférence esthétique.

## Explication, confiance et décision : trois objectifs différents

Buçinca et al. [P010] ont étudié des fonctions d’incitation à réfléchir dans une tâche nutritionnelle, avec une IA simulée et des erreurs contrôlées. Une réduction de l’adhésion à une erreur ne suffit pas à établir une amélioration globale de la décision, et certaines interventions imposent un coût aux utilisateurs. Leur condition d’attente de trente secondes avec prétendu traitement est un protocole expérimental, **pas un comportement à reproduire dans AlphaForge**.

Bansal et al. [P011] montrent, dans leurs tâches, que des explications peuvent accroître l’accord avec l’IA même lorsqu’elle se trompe. Une explication persuasive ou appréciée ne prouve donc ni fidélité, ni compréhension, ni usage approprié. Les résultats de Cochrane sur les aides à la décision médicales ne prouvent pas un effet financier quantifié ; la revue ne montre pas non plus que toute aide diminue le regret [P008].

Pour AlphaForge, l’objectif est un **usage approprié** : retenir une conclusion étayée, contester une conclusion erronée, reconnaître une incertitude irrésolue et savoir quelle information manque. Maximiser la confiance, l’adhésion ou l’investissement risqué serait un mauvais objectif isolé.

## Quand clarifier, approfondir ou renvoyer

| Signal pendant l’examen | Suite |
|---|---|
| « Ce n’est pas ce que j’entendais par préserver » | Agent 0 requalifie le but ; les résultats dépendants sont réexaminés. |
| « D’où vient cette exclusion ESG ? » | Agent 1 fournit une preuve datée ou maintient explicitement l’inconnu. |
| « Et avec une échéance de deux ans ? » | Agent 0 confirme le nouveau mandat ; Agent 2 recalcule et examine sa faisabilité. |
| « Ce chiffre ne correspond pas au graphique » | Suspendre cette conclusion, vérifier unités/données/calcul avec Agent 2, puis corriger le dossier. |
| « Je ne comprends pas le risque de change » | Explication adaptée, exemple cohérent avec le dossier ; aucun besoin de modifier le profil pour simplifier la réponse. |
| La préférence déclarée change après explication | Consigner ce changement comme nouvelle déclaration, sans supposer que l’ancienne était une erreur. |
| Désaccord entre le texte et la source | Agent 1 réexamine l’appui ; Agent 3 retire ou qualifie la phrase en attendant. |

## Évaluation proposée

La lisibilité est nécessaire mais insuffisante. Un score de lecture ou un LLM juge ne peut servir seul de référence pour la compréhension ou la qualité de décision [U027, U226]. Les instruments médicaux DCS/DQI ne deviennent pas des échelles financières validées après changement de vocabulaire [U086/U205, U087].

Un protocole doit séparer :

- **Fidélité factuelle :** cohérence texte/chiffres/graphique/source ; rappel des limites ; aucune donnée inventée ; mêmes faits dans toutes les versions de détail.
- **Compréhension :** expliquer un compromis avec ses mots, identifier une incertitude et une condition qui changerait la décision.
- **Usage approprié :** taux d’acceptation de conclusions correctes et de rejet de conclusions erronées, mesurés séparément ; capacité à reconnaître un cas indécidable.
- **Révision :** correction réellement transmise, recalcul approprié, invalidation des anciennes sorties et conservation de l’historique.
- **Expérience :** effort, temps, abandon, accessibilité et satisfaction, sans assimiler satisfaction à vérité.

Tester des erreurs plausibles contrôlées, des résultats contre-intuitifs corrects et des preuves manquantes ; comparer une restitution simple à des interventions ciblées. Faire annoter les erreurs factuelles par un examen indépendant et tester la compréhension auprès de personnes du public visé. Ces protocoles sont proposés ; aucune efficacité humaine n’a été démontrée par le prototype ou par la présente revue.
