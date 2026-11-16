> **Conception, non construite** (15 novembre 2026). Rien de ce document n'est en service dans le produit. Les passages sur le calendrier, les décisions à prendre et l'organisation du travail sont historiques : ce ne sont pas des consignes. Certaines pièces de travail citées (`research/fiches/`, `research/R08-…`, `docs/etat.md`, `docs/coordination.md`) ne sont pas dans cette archive. Entrée de l'archive : `LIRE_EN_PREMIER.md`.

# 04 — Graphes de résolution et règles de révision

Une étude ne se déroule pas en ligne droite : une preuve peut manquer, un test peut écarter une méthode, la personne peut corriger sa demande. Ce document dit comment le travail se décompose, qui répond de quoi, ce qui rouvre une question, et comment une révision ne refait que ce qui doit l'être. Les exemples entre parenthèses sont ceux du dossier de Robert (document 07). Les numéros entre crochets renvoient à la table de résolution (document 01).

## 1. De l'objectif à la conclusion

| Nœud | Exemple | Critère de résolution | Dépend de | Responsable | Rouvert par |
|---|---|---|---|---|---|
| **Objectif** | Préserver le capital à trois à cinq ans | Rendu par une ou plusieurs grandeurs mesurables, ou déclaré « à départager » avec le fait qui départagerait | Faits déclarés | Agent 0 | Une correction d'un fait d'objectif ou d'horizon |
| **Décision** | Ajouter un titre isolé au portefeuille : faut-il, et jusqu'où ? | Rattachée à une décision du catalogue ; variables nécessaires présentes, ou question posée | Objectif, demande | Agent 0 | Une correction ou une variante de la demande |
| **Sous-problème de recherche** | Que sait-on du titre ? Quelle mesure correspond à l'objectif ? Quelles méthodes s'appliquent à ces données ? | Une réponse « étayée », « étayée avec réserve » ou « sans preuve », avec ses liens de preuve ; jamais le silence | Décision et signaux retenus ; table des questions du catalogue ; bibliothèque ; données | Agent 1 | Une preuve contradictoire ; une fiche retirée ou périmée ; une source contestée par la personne ; un événement de l'agent 2 (formulation manquante, condition en échec) |
| **Données et preuves** | Jeu de données qualifié ; fiches de preuve | Empreintes contrôlées ; conditions d'application testées | Fichiers ; bibliothèque | Qualification des données ; agent 1 | Un nouvel instantané ; un retrait de fiche |
| **Méthode candidate** | Écarts appariés sur trajectoires rééchantillonnées | Test de condition passé, et statut inscrit sur la ligne du plan des méthodes | Données ; fiches ; lignes du catalogue employées (formulation, tests de condition, seuils) | Le code pour le test et le statut plancher ; agent 1 pour le statut | Un test qui échoue ; une preuve candidate qui ajoute une réserve ; un changement du catalogue |
| **Sous-problème de calcul** | L'option est-elle plus défavorable que « ne rien changer » ? De combien ? Que faudrait-il pour qu'elle se vaille ? | Calculs admis par la porte, sous toute la batterie fixe | La ligne du plan des méthodes que le calcul exécute ; sa ligne du plan d'analyse scellé (une option, une formulation) ; les lignes du catalogue qu'il emploie | Agent 2 ; le code calcule | Une entrée remplacée ; la ligne du plan amendée |
| **Conclusion** | Ce qui tient, ce qui dépend d'une hypothèse, de la personne, ce qu'aucun calcul ne donne | Chaque affirmation typée, reliée et munie de ses rendus ; confrontation close : aucun effet requis en attente | Calculs ; rendus ; objections et effets requis | Agent 2 | Un verdict « amendée » ou « change » ; un calcul périmé ; une réponse de la personne qui sort du domaine balayé |
| **Restitution** | Le document remis, à trois profondeurs | Porte passée : aucune affirmation omise, aucun fait nouveau, tournures conformes au type, réserves présentes | Conclusion ; registre, réserves et bilan de confrontation ; abstentions et lacunes | Agent 3 | Une conclusion remplacée ; une contestation |

**Récursion.** Les questions de recherche de base sont instanciées par le code, depuis la table du catalogue, pour la décision et les signaux que l'agent 0 a retenus [R01]. Un agent peut ensuite ouvrir des sous-questions dans son domaine : l'agent 0 des questions typées que la table ne prévoit pas, l'agent 1 des sous-questions de recherche, l'agent 2 des sous-questions de calcul. Une sous-question porte une clé (type, objet, paramètres) : si la clé existe déjà dans le dossier, la question n'est pas dupliquée, elle est reliée. La profondeur est bornée (trois niveaux sous la décision, valeur du catalogue).

**Une découverte peut atteindre le parent.** Si l'agent 1 établit qu'aucune méthode ne répond à la mesure choisie, ou si un test de condition échoue sur le titre demandé, il n'ajuste pas le problème lui-même : il émet un événement « hypothèse du parent en cause », qui rouvre la question parente chez son responsable (l'agent 0 pour l'objectif et la décision). Le parent se reformule ou s'abstient ; il ne pose une question à la personne que si une variable nécessaire est devenue indéterminée. Une limite connue d'avance n'est pas une découverte : l'horizon que les données ne portent pas est écarté dès la qualification, par la table des horizons du catalogue.

## 2. Quatre graphes

| Graphe | Nœuds | Arêtes | À quoi il sert | Qui le tient |
|---|---|---|---|---|
| **Questions** | Objectif, décision, sous-questions, questions à la personne | décompose, dépend de | Savoir ce qui reste à résoudre et pourquoi | Les rôles responsables ; le greffier pour les états |
| **Preuves** | Affirmations, passages, calculs, faits déclarés, hypothèses, objections | soutient, contredit, conditionne, éprouve | Répondre à « pourquoi dites-vous cela ? » et à « qu'est-ce qui le contredit ? » | Agents 1 et 2 ; le code pour l'existence et les verdicts |
| **Tâches** | Une exécution d'un rôle ou d'un outil sur des entrées identifiées par leur empreinte | dérive de | Ordonner, reprendre, ne pas refaire | Le greffier |
| **Parcours utilisateur** | Sept étapes lisibles : ce que j'ai compris ; ce qu'on ignore ; ce qu'on a cherché ; ce qu'on a calculé ; ce qui a été contesté ; ce qu'on peut conclure ; vos réponses | suit | Montrer le travail sans exposer la mécanique | L'interface, à partir des trois autres |

Le graphe de tâches se déduit du graphe de questions : une question ouverte dont les dépendances sont résolues engendre une tâche pour son responsable. Quatre tâches sont déclenchées par une règle, et jamais par un modèle : la batterie fixe, au scellement du plan d'analyse ; la confrontation, une fois pour chaque version de la note admise par la porte d'analyse, une version amendée étant réévaluée par le code et non reconfrontée [C16, C15] ; la désignation de la question décisive, après la confrontation ; la sélection du cas de la conclusion, quand la personne répond dans le domaine déjà balayé. Le parcours utilisateur est une vue : il ne contient rien qui ne soit dans les trois autres.

## 3. Ce qui rouvre, et ce qui reste

| Événement | Auteur | Ce qui est rouvert | Ce qui reste en vigueur |
|---|---|---|---|
| Correction d'un fait du profil (perte acceptable, horizon, retrait prévu) | La personne | Les questions qui dépendent de ce champ, puis en aval : variantes du plan d'analyse qui l'emploient, partie « dépend de la personne » de la conclusion, restitution | Jeu de données, dossier de preuves, plan des méthodes, calculs qui n'emploient pas ce champ |
| Précision : réponse à la question posée après l'analyse | La personne | La sélection du cas de la conclusion, par le code ; la restitution | Tous les calculs déjà balayés, la note et ses affirmations. L'agent 2 n'est rappelé que si la réponse sort du domaine balayé |
| Correction de la décision (autre titre, autre part) | La personne | Fiche produit, options et comparateurs, tests de condition sur le nouvel actif, calculs comparatifs, objections, conclusion | Faits du profil, données, fiches de méthode, calculs de « ne rien changer » |
| Option nouvelle demandée après un affichage | La personne | Les pièces qui manquent pour cette option ; le plan d'analyse est rescellé avant les nouveaux calculs, et les affirmations qui en sortent portent la mention « ajoutée après le premier affichage » [R13] | Tout le reste |
| Changement de situation (« ma situation a changé ») | La personne | Comme une correction ; l'ancienne conclusion est montrée comme ayant valu jusqu'à cette date | Comme une correction |
| Variante (« et si… ») | La personne | Rien sur la branche principale ; une branche est ouverte | Toute la branche principale ; la branche partage ce qui ne change pas |
| Échéance d'un fait déclaré, d'une vérification de source ou de la validité d'une restitution : c'est un événement du journal, pas une péremption | Le greffier, d'après les durées du catalogue | Une question à la personne, ou une vérification par l'agent 1 ; la restitution affiche que sa date de validité est dépassée | Tout, tant que la réponse ne change rien (coupure anticipée) |
| Le même champ change plusieurs fois de suite | Le greffier le signale | Une question à la personne sur la valeur à retenir | L'étude en cours |
| Preuve candidate qui contredit ou restreint | Agent 1 | La ligne du plan concernée (réserve, variante du catalogue rendue obligatoire) ; une objection d'origine « recherche » est inscrite [R11] | Les autres lignes du plan et leurs calculs |
| Test de condition qui échoue | Le code | La ligne du plan des méthodes (formulation écartée), dans une version marquée « amendée après des résultats » ; les calculs qui exécutaient cette ligne [R07] | Les calculs des autres formulations ; leur antériorité |
| Contestation d'un champ de la fiche par un rôle d'aval | Agents 1 ou 2 | Le champ, que l'agent 0 corrige ou maintient une fois ; maintenu, il part à l'analyse sous ses deux lectures [R02] | Les autres champs et ce qui en dépend |
| Verdict « amendée » ou « change » | Le code, sur une objection | L'affirmation visée, que l'agent 2 amende en une passe ; la porte d'amendement vérifie l'effet requis ; après le nombre de tentatives du catalogue, ou dès que l'agent 2 conteste, l'affirmation est « non résolue » [C15] | Les autres affirmations, que la porte interdit de toucher |
| Pièce retirée comme erronée | Le code pour un calcul, l'agent 1 pour ses sources, ou l'équipe | Tout ce qui en dérive ; si une restitution affichée en dépendait, la personne est prévenue | Le reste |
| Contestation d'une source | La personne | Le lien de preuve (soutien « contesté ») ; un seul réexamen par l'agent 1, qui ne peut qu'ajouter une réserve ou une objection | Les calculs ; les statuts du plan |
| Nouvel instantané de données | L'équipe, hors exécution | Tout ce qui dérive du jeu de données : fiches par actif, tests de condition et statuts planchers, comparateurs, calculs, table des variantes, rendus, verdicts, affirmations qui les citent, restitution | Faits déclarés, passages, sources |
| Nouvelle version du catalogue | L'équipe, hors exécution | Les plans, calculs, tests, comparateurs, verdicts et questions désignées qui emploient une ligne modifiée du catalogue, et eux seuls [C05] | Tout le reste, dont ce qui emploie des lignes inchangées |

La règle est partout la même : **est rouvert ce qui dérive, par les dépendances enregistrées, de la pièce remplacée ; reste en vigueur tout le reste.** Elle n'est pas appliquée par un modèle : le greffier la calcule.

## 4. Progrès, doublons, écritures concurrentes

- **Pas de réouverture sans cause nouvelle.** Une réouverture cite l'événement qui la justifie. Le même événement ne rouvre pas deux fois la même question ; la cause est l'événement, pas la valeur : une personne qui revient à une valeur antérieure crée un événement nouveau, et les pièces qui valaient pour cette valeur redeviennent en vigueur sans recalcul. Les motifs de refus et les pistes déjà écartées sont gardés et consultés avant toute réouverture.
- **Pas de cycle.** Pour un même état en vigueur, le graphe de tâches n'a pas de cycle ; une révision prolonge le journal et donne un nouvel état. Aucune affirmation ne figure dans sa propre chaîne de preuves.
- **Nombre de réouvertures borné** par question (deux, valeur du catalogue). Au-delà, la question est rendue « non résolue », avec les positions en présence, et l'étude continue sans elle. Cette borne vaut pour les réouvertures que provoquent les rôles et le code, à version de la demande constante : une nouvelle version de la demande, venue de la personne, remet les comptes à zéro.
- **Mesure de progrès.** Un tour de révision doit changer au moins une empreinte d'entrée en aval ; sinon il est arrêté et consigné comme « sans effet ».
- **Une confrontation par version de la note.** La confrontation complète a lieu une fois pour chaque version de la note admise par la porte d'analyse. Le code tire d'abord de la table des variantes, calculée au scellement et non recalculée, les objections de la batterie fixe qui visent les affirmations de la note, et rend leurs verdicts ; puis le contradicteur dépose ses objections en un lot. L'agent 2 amende en une passe. La version amendée n'est pas reconfrontée par le contradicteur, qui ne rejuge pas ses propres objections : le code réévalue, sur les seules affirmations amendées, le critère scellé de chaque objection et la batterie, en réemployant les calculs dont les entrées n'ont pas changé. Un nouveau « change » compte comme une tentative de la porte d'amendement. Ces nombres (une confrontation, une passe, le nombre de tentatives) sont des réglages du catalogue, que l'essai d'erreurs semées peut faire réviser.
- **Une affirmation qui ne s'amende pas ne bloque pas sans fin.** Après le nombre de tentatives du catalogue, ou dès une contestation, elle sort de la conclusion, est affichée « non résolue » avec les deux positions, et l'étude a une couverture partielle.
- **Doublons.** Clé de question ; mémorisation des tâches par empreinte d'entrées : la même tâche sur les mêmes entrées n'est jamais relancée.
- **Écritures concurrentes.** Une écriture à la fois par branche (document 02, section 7). Deux corrections simultanées ne se mêlent pas : la seconde est rejouée sur la tête issue de la première. Deux explorations simultanées sont deux branches.
- **Budgets.** Chaque étude a un nombre maximal d'appels de modèle et une durée maximale ; la recherche de l'agent 1 a son propre budget (valeurs du catalogue). Un budget épuisé n'est pas une conclusion.
- **Personne n'attend l'équipe.** Une lacune est consignée, la question reste « sans preuve », l'étude continue [R15].

## 5. Sortir d'une étude

Une étude peut à la fois dépendre d'une inconnue et laisser une question sans preuve : un seul mot ne suffit pas. L'état se calcule donc en deux temps : l'étude est-elle allée au bout, puis, si oui, sur deux axes.

| | Condition | Ce qui est montré |
|---|---|---|
| **Arrêtée à la qualification** | La demande est hors catalogue, ou le gabarit de sa décision est incomplet | L'abstention de l'agent 0 et la reformulation proposée, affichées par l'interface ; ni analyse, ni restitution |
| **En attente de la personne** | Une variable nécessaire a été demandée ; passé le délai du catalogue, la question est « sans réponse » et l'étude est arrêtée faute de réponse | Ce qui manque pour commencer ; aucune conclusion |
| **Interrompue** | Panne ; budget de l'étude épuisé ; tâche du chemin de la conclusion en échec après ses reprises (qualification, plan des méthodes, note hors amendement, batterie fixe, restitution) | « Étude interrompue à telle étape », affiché par l'interface d'après l'état calculé par le greffier, sans tâche de l'agent 3 ; les pièces en vigueur sont consultables ; aucune conclusion n'est présentée |
| **Menée à terme** | Aucun des trois cas précédents, et une restitution a passé sa porte | La conclusion, avec les deux mentions ci-dessous |

Pour une étude menée à terme :

| Axe | Valeur | Condition | Ce que la restitution dit |
|---|---|---|---|
| **Couverture** | Entière | Chaque question issue de la demande a une réponse « étayée » ou « étayée avec réserve », la réserve étant affichée (une réponse qui ne repose que sur des fiches candidates est « étayée avec réserve » : elle ne rend pas la couverture partielle) ; la confrontation a couvert tous les types d'objection applicables | Ce qui est établi, ses preuves, ses limites |
| | Partielle | Une question au moins est « sans preuve » ou « non résolue », une affirmation est « non résolue », une lacune est consignée, une partie de l'horizon ou de la préférence déclarés reste hors de portée, ou la revue du contradicteur est incomplète, y compris parce qu'il a échoué | Ce qui est établi, et à part, au même rang, ce qui ne l'est pas, avec ce qu'il faudrait |
| **Conditions** | Sans condition | Aucune inconnue de la personne ne change le cas qui s'applique, dans le domaine balayé | La conclusion |
| | Conditionnelle | Une inconnue nommée, ou une contradiction non levée, change le cas qui s'applique | La conclusion par cas, et la question qui départage |

La couverture se juge sur les questions que la demande fait ouvrir, pas sur le périmètre du produit : les limites communes à tous les dossiers (coûts, fiscalité, absence de niveau de risque) figurent dans la déclaration de portée et ne rendent pas une étude partielle. Avec cinq ans de données et un profil dont plusieurs composantes sont inconnues, la plupart des études sortiront néanmoins « partielles » ou « conditionnelles », souvent les deux : c'est l'état honnête, et il est affiché. Une interruption technique ne devient jamais une résolution : l'état est calculé par le greffier, et aucune restitution n'est préparée dans une étude interrompue.

## 6. Reprise

Le greffier reconstruit l'état du dossier en relisant le journal. Une tâche terminée ne se refait pas (son résultat est déjà rangé sous l'empreinte de ses entrées). Une tâche en cours au moment de l'arrêt est relancée ; si elle comportait un appel de modèle, l'appel est refait et les deux tentatives sont au journal. Une question posée à la personne suspend la branche sans la bloquer : ce qui ne dépend pas de la réponse continue.
