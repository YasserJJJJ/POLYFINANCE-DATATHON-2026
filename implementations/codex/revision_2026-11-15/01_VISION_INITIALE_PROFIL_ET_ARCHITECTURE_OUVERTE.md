# AlphaForge AI — Vision initiale, profil de collaboration et architecture ouverte

**Document 01 · Restitution structurée de la proposition du porteur et pistes de perfectionnement**  
**Version 2 · 15 novembre 2026 · Intention initiale conservée ; méthode enrichie ; mandat disponible au document 02**

## 1. Intention de ce document

Ce texte conserve la proposition initiale du porteur pour qu’elle reste retrouvable après les recherches, même si l’architecture finale change profondément. Il distingue :

1. **ce qu’il a proposé** ;
2. **ce que ses échanges révèlent de ses préférences de travail** ;
3. **les ajustements proposés par l’analyse** ;
4. **les questions encore ouvertes**.

La restitution reformule les idées ; elle n’est pas une transcription verbatim. Les corrections ne remplacent pas silencieusement l’intention d’origine. Les références `R1` à `R17` renvoient au registre sourcé du [document 00](00_DECORTICAGE_MULTIDIMENSIONNEL.md).

Le porteur a confirmé disposer du compte AWS du datathon. Il exige maintenant que toutes les inférences du développement et du produit suivent la facturation AWS prévue. Il ne souhaite pas de réduction arbitraire d’ambition fondée sur sa taille d’équipe. Les échéances désormais documentées organisent les livraisons sans définir un plafond de recherche.

## 2. La vision initiale, reformulée fidèlement

### 2.1 Proposition de valeur envisagée

> Construire une aide à la décision financière fondée sur la meilleure connaissance pertinente disponible, capable de transformer une demande plus ou moins complète en problème explicite, de rechercher les méthodes existantes adaptées, de produire une solution justifiée et de l’expliquer au niveau de compréhension de son utilisateur.

L’ambition est de **reproduire les fonctions intellectuelles utiles d’une organisation financière de haut niveau** : qualification de la demande, recherche, analyse, confrontation critique et restitution. Il ne s’agit pas nécessairement de reproduire sa taille, ses services ni son organigramme.

Le porteur vise un classement élevé par la rigueur et la qualité de réalisation. Il veut éviter une application générée superficiellement, un assemblage de technologies à la mode ou un assistant qui répond par généralités.

### 2.2 Philosophie de résolution proposée

L’énoncé est traité comme un problème mathématique à analyser : objectifs, critères, contraintes, inconnues et dépendances. Chaque difficulté est décomposée en sous-problèmes ; pour chacun, on recherche les méthodes et réalisations existantes avant de choisir une solution.

Cette démarche est récursive : la recherche peut révéler que le sous-problème était mal formulé, qu’une hypothèse est inutile ou qu’une autre branche de solution est meilleure. Le plan doit pouvoir évoluer.

L’idée de départ est que les outils théoriques et pratiques utiles existent très probablement déjà dans la littérature, les cours, les laboratoires ou des projets ouverts. L’innovation recherchée peut venir de leur **sélection, adaptation et intégration cohérente**, plutôt que de l’invention d’un nouvel algorithme fondamental.

### 2.3 Architecture proposée au départ

| Étape ou rôle initial | Mission envisagée | Sortie attendue |
|---|---|---|
| Entrée / « contrainte 0 » | Accepter une phrase simple ou un dossier détaillé ; déterminer le bon format sans enfermer la demande. | Demande exploitable, informations connues et manquantes. |
| Agent 0 : cadrage et profilage | Comprendre le contexte, profiler l’investisseur, formaliser contraintes et objectifs, identifier les micro-problèmes et le niveau d’effort utile. | Énoncé financier structuré et liste de questions à résoudre. |
| Agent 1 : recherche | Chercher théorie, cours, études et précédents utiles ; sourcer et conserver un journal. | Dossier de connaissances adapté au problème, avec provenance. |
| Agent 2 : résolution | Relier le problème formalisé aux meilleurs éléments de théorie, établir une solution défendable et produire l’aide à la décision. | Solution théorique et numérique accompagnée d’une justification. |
| Agent 3 : restitution | Transformer les résultats en une présentation compréhensible pour un novice ou un professionnel. | Rapport, graphiques, scénarios, preuves accessibles ; nouvelle demande renvoyée au cadrage. |

**Cette division est un point de départ fonctionnel.** Le porteur autorise explicitement sa réorganisation, sa fusion ou son remplacement après recherche. Les numéros ne constituent pas une obligation de créer quatre processus LLM.

### 2.4 Les idées initiales conservées, une par une

| ID | Idée du porteur | Interprétation fidèle, sans la transformer en prescription définitive |
|---|---|---|
| O01 | Rétro-ingénierie approfondie de l’énoncé et de la notation | Comprendre ce qui crée de la valeur pour le jury et les obligations réelles avant de choisir la technologie. |
| O02 | Résolution récursive par arbre de problèmes | Décomposer, rechercher, résoudre et réexaminer les dépendances à chaque niveau. |
| O03 | Rechercher les meilleures solutions existantes | Explorer articles, cours, outils et projets remarquables, sans se limiter aux capacités natives de Claude. |
| O04 | Simuler les meilleures organisations financières | Reproduire qualité d’analyse, recherche et prise de décision, dans le contexte fictif du datathon. |
| O05 | Entrée libre mais suffisamment informative | Éviter aussi bien une requête pauvre qu’un formulaire trop rigide. |
| O06 | S’adapter au manque d’informations | Traiter une phrase courte et un dossier précis sans inventer les paramètres absents. |
| O07 | Choix de niveau d’effort | Pouvoir approfondir davantage les demandes complexes ou importantes. |
| O08 | Profilage financier très pertinent | Déterminer les paramètres réellement utiles selon la littérature et le problème. |
| O09 | Formalisation en énoncé de finance computationnelle | Convertir le besoin en objectifs, contraintes, variables et critères de décision explicites. |
| O10 | Revue de littérature spécialisée et journal | Référencer les sources, conserver les découvertes et relier la recherche aux choix. |
| O11 | Solution théorique démontrable et résistante à la critique | Donner une justification explicite et examiner les objections avant de présenter un résultat. |
| O12 | Présentation adaptée au destinataire | Moduler détail, vocabulaire et visualisations sans dégrader le fond scientifique. |
| O13 | Maximiser les paramètres pertinents, étudier leurs interactions | Rechercher une personnalisation riche tout en examinant corrélations, surreprésentation, incertitude et coût. |
| O14 | Définir ce qui distingue réellement la solution | Visualiser un résultat idéal puis vérifier que l’architecture apporte cette différence. |
| O15 | Relier profil client et connaissances scientifiques | Choisir les éléments de preuve et les méthodes selon le contexte plutôt que donner les mêmes conseils à tous. |
| O16 | Relier théorie, calcul et démonstration pratique | Rendre les méthodes exécutables, inspectables et présentables. |
| O17 | Rassembler environ cinquante trouvailles majeures, nombre indicatif | Construire une base de connaissances ambitieuse, sans quota artificiel ni collection déconnectée du produit. |
| O18 | Priorité à une conception solide, puis tests et perfectionnement | Prévenir les erreurs structurelles ; ne pas compter uniquement sur des corrections après construction. |
| O19 | Simuler un contexte réel sans brider les capacités de recherche | Maintenir un niveau professionnel d’analyse tout en respectant le caractère fictif du concours. |
| O20 | Idées initiales non limitantes | Garder la trace des intuitions sans obliger la solution finale à leur ressembler. |

## 3. Profil de collaboration issu de nos échanges

Il s’agit d’un **profil de préférences de travail**, fondé sur tes déclarations et sur cette conversation. Ce n’est ni un diagnostic psychologique ni une connaissance supposée d’autres échanges inaccessibles.

### 3.1 Ce qui est explicitement déclaré

- Tu te décris comme à l’aise en mathématiques et en raisonnement, mais sans connaissances fortes en finance, data science, AWS ou architecture applicative.
- Tu souhaites utiliser l’IA pour accéder aux méthodes existantes, comprendre les choix et réaliser un projet ambitieux.
- Tu tiens à la recherche préalable et refuses que tes premières idées deviennent un plafond.
- Tu préfères une autonomie importante sur les choix ordinaires plutôt qu’une succession de demandes de permission.
- Tu veux des résultats concrets à regarder et essayer, pas seulement des rapports ou des promesses.
- Tu souhaites garder la décision humaine sur l’utilité, la qualité visuelle et les changements importants d’intention.

### 3.2 Préférences observées dans CALIBRE et leur traduction ici

| Observation dans les échanges | Traduction utile pour AlphaForge |
|---|---|
| Frustration face à une interface annoncée fidèle mais restée proche d’un ancien template | Fixer quelques exemples de résultat attendu ; comparer la vraie interface, pas uniquement le code. |
| Forte appréciation d’une première réalisation visuelle convaincante | Montrer tôt une tranche complète et explicable ; utiliser ton retour pour orienter la qualité. |
| Souhait de poursuivre pendant ton sommeil | Maintenir un état de reprise concret et faire avancer les tâches indépendantes. |
| Désaccord avec une finition du bench bloquant les autres lifts | Rendre les dépendances explicites ; éviter qu’une branche monopolise toute la réalisation. |
| Exigence de références scientifiques | Relier chaque décision structurante aux sources et à leurs limites. |
| Refus des contraintes commerciales artificielles pour un projet de démonstration | Ne pas inventer d’obligations ; distinguer cependant les règles explicites du concours. |
| Méfiance envers les tests excessifs | Choisir les vérifications qui peuvent réellement changer le verdict et arrêter les répétitions sans motif. |
| Difficultés liées aux quotas et crédits | Mesurer coût et progression utile, séparer tâches LLM et calculs locaux, prévoir la reprise. |
| Souhait de ne pas limiter les capacités de Claude | Spécifier les résultats et les critères, laisser les moyens ouverts et contestables. |

### 3.3 Les points de vigilance qui améliorent cette méthode

Ton ambition pousse à explorer des solutions que des choix trop rapides excluraient. Son risque est d’associer inconsciemment **plus de recherche, plus de paramètres ou plus d’agents** à **plus de qualité**. Ce lien doit être démontré, pas supposé.

La confiance dans le raisonnement mathématique est un atout pour exiger des définitions et des hypothèses précises. En finance, elle doit aussi permettre d’accepter qu’une conclusion soit conditionnelle, qu’une préférence ne soit pas mesurée exactement et qu’une donnée manque.

Comme tu n’es pas spécialiste des domaines techniques, une explication très assurée peut sembler plus solide qu’elle ne l’est. Le bon dispositif doit te permettre de demander : « Montre-moi le calcul, la source, le contre-exemple et ce qui changerait ta conclusion. » Il doit aussi traduire ces éléments en langage simple.

Une belle démonstration ne remplace pas la vérité des calculs ; des tests réussis ne remplacent pas une bonne expérience. Les deux doivent rester visibles séparément.

## 4. Ajustements proposés — préserver l’intention, améliorer la rigueur

### 4.1 « Non limitant » signifie moyens ouverts, critères fermes

Un contexte utile ne prescrit pas d’emblée la méthode, le nombre d’agents, un moteur de recherche, un solveur ou une base de données. Il précise en revanche : la question utile, la définition d’un résultat réussi, la traçabilité, les règles du concours et la manière de comparer les solutions.

Sans ces éléments, « fais le meilleur possible » laisse le modèle optimiser une impression de sophistication. Avec eux, il peut dépasser la proposition initiale en montrant pourquoi son alternative sert mieux le projet.

### 4.2 Remplacer l’optimum absolu par une revendication vérifiable

L’idée d’une solution « absolument déjà existante » est conservée comme conviction initiale, mais ne peut pas devenir un fait. Certaines questions n’ont pas de réponse connue ; d’autres n’ont pas d’optimum unique tant que les préférences, données et contraintes ne sont pas fixées.

La formulation rigoureuse serait : **rechercher les meilleures méthodes pertinentes connues, comparer leur adéquation au cas, établir leurs garanties conditionnelles et mesurer leur comportement sur des situations réservées**.

Cela laisse une grande ambition scientifique. Cela évite de sélectionner la première publication impressionnante puis de présenter son résultat comme une garantie universelle.

### 4.3 Arbre pour explorer, graphe pour coordonner

Une bonne structure de travail pourrait être :

```text
Question globale et promesse utilisateur
├── Profil et décision à éclairer
├── Données et disponibilité temporelle
├── Méthodes et garanties
├── Calculs et scénarios
├── Explication et interaction
├── Architecture agentique et AWS
└── Démonstration et validation
```

Mais les branches communiquent : une exclusion ESG change l’univers ; une donnée manquante change la méthode ; un horizon change la métrique de risque ; la latence influence l’interaction. Une structure de graphe doit enregistrer ces dépendances.

Ne pas imposer une base de données graphe : une représentation simple avec identifiants et relations peut suffire. La structure conceptuelle doit être choisie avant la technologie de stockage.

### 4.4 Recherche récursive avec critères d’arrêt intelligents

Pour chaque nœud important : question → critères → sources → alternatives → expérience → décision → effet sur le problème global.

La recherche continue si une incertitude peut changer la décision. Elle peut s’arrêter provisoirement lorsque :

- une méthode répond aux critères et les autres options crédibles n’apportent pas de gain démontré ;
- l’incertitude restante est mesurée ou explicitement représentée dans la sortie ;
- les nouvelles recherches répètent les mêmes arguments ;
- la question dépend désormais d’un choix humain de préférence, pas d’un fait à découvrir.

Ce ne sont pas des plafonds de qualité. Ce sont des moyens de convertir la recherche en progrès et d’éviter la récursion sans résultat.

Les découvertes remettant en cause le problème parent doivent remonter dans le graphe. Une préférence initiale pour une technologie ne bénéficie pas d’un statut spécial.

### 4.5 La recherche ne se répète pas intégralement à chaque demande client

Séparer deux temporalités :

- **Développement :** recherches larges, comparaison de méthodes, essais et choix d’architecture.
- **Utilisation :** mobilisation de connaissances déjà qualifiées, calculs adaptés, recherche complémentaire seulement lorsqu’une information nouvelle est nécessaire.

Une base de preuves indexée peut éviter de faire relire cinquante papiers à chaque question. Le système reste capable de demander un complément ou d’approfondir un sujet, mais ne promet pas une revue scientifique mondiale instantanée.

### 4.6 Tests : présents dès les contrats, pas inflation de contrôle

Le souhait de solidité initiale est conservé. La meilleure traduction n’est pas « tester uniquement à la fin », mais **définir d’abord les invariants, vérifier les interfaces tôt et réserver les évaluations finales à ce qui n’a pas servi à ajuster le système**.

Un petit test qui révèle une mauvaise devise vaut davantage que mille tests de composants sans enjeu. Une seule critique financière ciblée peut valoir plus que des débats entre agents répétant les mêmes hypothèses.

Le mot « fine-tuning » doit être clarifié : ajuster prompts, récupération et outils ne signifie pas entraîner les poids d’un modèle. Un entraînement n’est à envisager que si un défaut précis, des exemples fiables et une comparaison montrent son intérêt.

### 4.7 Distinguer rigidité du parcours et reproductibilité des calculs

Ton souhait d’éviter le « déterminisme » semble viser surtout des réponses préprogrammées, pauvres et peu adaptées. Il ne faut pas en déduire qu’un calcul financier devrait changer au hasard d’une exécution à l’autre. À mêmes données et hypothèses, un résultat numérique reproductible est une force. La souplesse porte sur la compréhension, la recherche, la sélection des outils et l’adaptation de la présentation. Un calcul stable peut servir une interaction très ouverte.

## 5. Architecture fonctionnelle candidate, encore remplaçable

### 5.1 Fonctions à couvrir plutôt que nombre d’agents à imposer

| Fonction | Entrée | Sortie contrôlable | Agent nécessaire ? |
|---|---|---|---|
| Comprendre la demande | Texte, fichier, contexte fictif | Intention, contradictions, champs sourcés, inconnues | Un LLM peut être utile pour le langage. |
| Formaliser la décision | Profil et question | Objectifs, contraintes, hypothèses, résultats attendus | Mixte : dialogue et validation structurée. |
| Chercher des preuves | Questions documentaires | Sources datées, passages, affirmations et limites | Recherche agentique possible ; filtrage déterministe utile. |
| Préparer les données | Jeux bruts et métadonnées | Tables cohérentes, calendrier de disponibilité, qualité | Principalement code vérifiable. |
| Calculer / optimiser | Problème et données qualifiées | Chiffres, statuts, résidus, sensibilité | Outils numériques ; le LLM ne doit pas inventer les résultats. |
| Vérifier | Contraintes et sorties | Violations, contradictions, preuves manquantes | Contrôles logiciels et critique ciblée ; agent optionnel. |
| Expliquer | Résultats et preuves | Conclusion à plusieurs niveaux de lecture | LLM utile pour la synthèse, chiffres liés aux sorties. |
| Orchestrer | État et dépendances | Prochaine action pertinente, trace et reprise | Agent, workflow ou combinaison à comparer. |

Cela développe l’architecture initiale sans imposer de rôles supplémentaires. L’agent 2 initial contient plusieurs fonctions qu’il est utile de distinguer, même si elles partagent un processus. L’agent 3 ne devrait pas refaire les calculs : il les présente et renvoie les contradictions détectées.

### 5.2 Objets de données suggérés

Ces objets représentent des contrats possibles, pas un schéma définitif :

- `Request` : demande brute, documents associés, intention présumée, mode de simulation.
- `ProfileFact` : champ, valeur, unité, source, statut déclaré/hypothèse/inconnu, date et possibilité de correction.
- `DecisionProblem` : objectifs, contraintes dures, préférences négociables, inconnues critiques, univers, date de décision.
- `ResearchQuestion` : problème, dépendances, méthode de recherche, critères de réponse, état.
- `Evidence` : référence, passage ou tableau, date de publication, période couverte, accès réel, qualité et limites.
- `DataSnapshot` : source, empreinte, extraction, unités, transformations et règles temporelles.
- `AnalysisRun` : entrées, version de méthode, appels d’outils, sorties, erreurs et durée/coût observés.
- `DecisionClaim` : affirmation, données/calculs justificatifs, hypothèses, contre-indications, domaine de validité.
- `Explanation` : présentation courte, détails, visualisations, références et limitations.

Chaîne visée : **demande → contrainte → preuve/donnée → calcul → conclusion → explication**. Une affirmation sans lien devient « non étayée », pas automatiquement « vraie parce que l’agent l’a dite ».

Éviter les pourcentages de confiance fabriqués. Une confiance numérique suppose un sens défini et une calibration ; sinon employer des statuts explicites comme « constat mesuré », « hypothèse sensible » ou « information manquante ».

## 6. Profilage adaptatif : davantage de pertinence, pas davantage de champs par principe

### 6.1 Dimensions candidates à rechercher

Le cadre financier du CFA distingue objectifs, ressources et contraintes, notamment horizon, liquidité et risque. [R1] À partir de cela, les dimensions suivantes sont des pistes :

| Dimension | Utilité possible | Risque si elle est mal employée |
|---|---|---|
| Question exacte | Comparer, comprendre, simuler, allouer, vérifier une contradiction | Traiter une demande d’explication comme un ordre d’achat. |
| Objectif et horizon | Relier croissance, conservation et échéance | Confondre « long terme » avec absence de contrainte. |
| Liquidité et flux fictifs | Représenter retraits, dépenses prévues et engagements | Proposer un actif incompatible avec un besoin proche. |
| Capacité et volonté de risque | Distinguer perte supportable et inconfort subjectif | Utiliser l’âge ou une étiquette comme raccourci absolu. |
| Détentions et expositions | Mesurer concentration et chevauchements | Diversification apparente par nombre de tickers. |
| Devise et contexte fiscal si pertinent | Comparaisons cohérentes | Ajouter des détails inutiles ou des règles non vérifiées. |
| Préférences ESG | Exclusions, arbitrages, niveau de preuve attendu | Confondre absence d’information et absence de controverse. |
| Expérience et format souhaité | Adapter la restitution | Modifier les faits financiers selon le niveau d’expertise. |
| Données absentes ou contradictoires | Décider s’il faut clarifier ou faire des scénarios | Inventer un profil détaillé pour donner une réponse assurée. |

Ne pas demander de vrais renseignements bancaires. Les scénarios peuvent être entièrement fictifs, comme le prévoit le concours.

### 6.2 Politique de clarification

Une phrase courte mérite une première compréhension utile, pas un questionnaire exhaustif. Un dossier complet mérite une extraction et une vérification des contradictions, pas des questions déjà renseignées.

Une question supplémentaire est pertinente si sa réponse peut changer matériellement la décision ou son explication. Une façon conceptuelle de raisonner est la **valeur de l’information** : amélioration espérée de la décision moins coût de clarification, de latence et de calcul. Ce principe ne justifie pas de fabriquer une probabilité précise lorsqu’aucun modèle ne la soutient.

Exemple : avant d’étudier une allocation pour Robert, un retrait important dans un an peut changer l’analyse. En revanche, sa profession ne doit pas être redemandée si elle n’affecte pas le scénario étudié. Pour une simple comparaison historique, une grande partie du profil peut être inutile.

### 6.3 Modes d’effort possibles

Comparer un mode aperçu, un mode analyse et un mode approfondi. Ils modulent la profondeur documentaire, le nombre de scénarios et le niveau de sensibilité, pas la véracité des chiffres ni le respect des contraintes.

L’effort ne doit pas être déduit uniquement du mot « sérieux ». Le système peut proposer une profondeur selon la complexité de la demande et laisser l’utilisateur la changer. Les limites de calcul sont distinctes des limites de validité scientifique.

## 7. Conception de la recherche et de la base de connaissances

### 7.1 Organiser par décisions, pas par célébrité des publications

Familles possibles de recherche : profilage et préférences ; objectifs multiples ; estimation du risque ; diversification et corrélations ; robustesse ; information ESG ; données temporelles ; explications ; interaction ; orchestration et évaluation agentiques.

Pour chaque famille, distinguer théorie fondatrice, résultats empiriques, réplications, critiques et implémentations. Une technique récente n’est pas nécessairement meilleure ; un résultat classique n’est pas forcément adapté aux outils et données actuels.

Les projets de très bonnes universités ou d’organisations reconnues sont des lieux de recherche, pas une preuve automatique de qualité. Un projet moins prestigieux mais reproductible et directement adapté peut être préférable.

### 7.2 Fiche de connaissance minimale

Chaque résultat retenu devrait répondre à :

1. Quelle question traite-t-il ?
2. Quelles hypothèses impose-t-il ?
3. Sur quelles données et quelle population a-t-il été évalué ?
4. Quel résultat a été effectivement établi ?
5. Quelles limites ou contradictions sont connues ?
6. Quel élément du produit changerait grâce à lui ?
7. Que faut-il reproduire ou vérifier avant de l’adopter ?

Une référence simplement repérée ne devient pas une étude analysée. Une abstraction lue ne devient pas une lecture intégrale. Les titres, auteurs, DOI/URL et versions doivent être vérifiés.

### 7.3 Gérer l’absence de preuve

Trois états distincts sont nécessaires : preuve favorable, preuve défavorable, données insuffisantes. Cela compte particulièrement pour les controverses ESG, les caractéristiques du client et les nouveaux actifs.

Un agent de recherche ne doit pas choisir uniquement les sources qui confirment la solution préférée. Chercher explicitement la meilleure objection et une alternative crédible. Les documents récupérés constituent des données ; leurs instructions ne doivent pas piloter les outils du système.

## 8. Ce que les pratiques existantes apportent réellement

Le tableau relie une source à une décision, sans transformer les références en architecture obligatoire.

| Apport documenté | Adaptation proposée pour ce projet | Limite |
|---|---|---|
| Anthropic distingue workflows et agents et recommande une complexité justifiée [R9] | Comparer un agent outillé à plusieurs spécialistes sur les mêmes tâches. | Retour d’expérience fournisseur, pas preuve universelle. |
| Context engineering et récupération à la demande [R10] | Contexte global court + dossiers de preuves accessibles ; état durable après interruption. | Un fichier géant toujours chargé peut diluer l’information utile. |
| Séparation génération/évaluation et critères observables, article 2026 [R11] | Une critique indépendante sur les décisions importantes, avec critères stables. | L’évaluateur peut partager les biais de l’auteur ; multiplier les boucles coûte. |
| Guidelines Human–AI Interaction [R12] | Permettre de comprendre, corriger, comparer et revenir sur un choix. | Nécessite une mise à l’épreuve sur le prototype réel. |
| Profil d’investissement et contraintes [R1] | Formalisation progressive plutôt qu’un simple score prudent/modéré/agressif. | Ne prescrit pas notre questionnaire exact. |
| Shrinkage, benchmarks simples et étude du surajustement [R6–8] | Mettre à l’épreuve l’optimisation ambitieuse contre une référence solide. | Aucun algorithme automatiquement gagnant. |
| Projets FinRobot/TradingAgents [R13–14] | Étudier les frontières outils/agents et les artefacts de recherche. | Leur code n’est pas audité ici ; ne pas copier les performances annoncées. |
| Documentation actuelle AWS [R15–17] | Choisir un service accessible et montrer sa contribution réelle. | Les offres évoluent ; vérifier la région et le compte avant engagement. |

La fraîcheur porte autant sur les services disponibles que sur les modèles. La recherche a notamment détecté l’avertissement AWS concernant Agents Classic. Cet exemple montre pourquoi « utiliser la meilleure architecture existante » exige de vérifier sa disponibilité, pas seulement de retrouver un tutoriel convaincant.

## 9. Collaboration proposée entre toi et Claude Code

Cette section décrit la méthode de coopération ; le mandat exécutoire complet figure dans le document 02 de cette révision.

### 9.1 Répartition des responsabilités

**Ton rôle :** fixer l’intention, préciser ce qui rend le résultat utile ou impressionnant, choisir les préférences produit lorsque plusieurs options sont légitimes, inspecter la démo et apprendre à défendre les principales décisions.

**Rôle de Claude :** découvrir ce qui manque, rechercher les options, formaliser, comparer, implémenter, vérifier et conserver un état fidèle. Il doit pouvoir contester une idée initiale sans l’effacer ni te renvoyer toutes les décisions techniques.

**Rôle de la critique :** chercher les erreurs importantes, les données inadéquates, les conclusions non soutenues et les écarts entre prototype et promesse. Une seconde instance de modèle n’est pas automatiquement une autorité indépendante ; les résultats reproductibles et sources externes restent centraux.

### 9.2 Format de conversation conseillé

À un point de décision important, une bonne réponse de Claude pourrait contenir :

- **Problème reformulé** en termes que tu comprends.
- **Ce que la recherche établit**, avec références et limites.
- **Options pertinentes**, incluant une référence simple.
- **Choix recommandé**, raisons décisives et contre-argument principal.
- **Preuve concrète** : calcul, comparaison, capture, essai ou exemple.
- **Ce qui reste ouvert**, et s’il s’agit d’un fait à rechercher ou d’une préférence humaine.
- **Prochaine action**, réalisable sans te reposer la même question.

Le détail méthodologique reste accessible, mais les mises à jour ne devraient pas réciter toutes les commandes exécutées. Elles doivent dire ce qui a été appris et ce que cela change.

### 9.3 Ton rôle de juge sans expertise technique préalable

Pour chaque mécanisme important, demander trois niveaux :

1. Une explication en langage courant et un exemple concret.
2. Le modèle, les hypothèses et le calcul exact.
3. Une limite, un contre-exemple et la manière de le détecter.

Cela te permet d’exercer ton raisonnement sans prétendre maîtriser d’emblée chaque domaine. Un dossier de défense pourrait contenir les réponses à : « Pourquoi cette donnée ? », « Pourquoi cet agent ? », « Qu’apporte AWS ? », « Pourquoi cette méthode plutôt qu’une règle simple ? », « Que pouvez-vous vraiment prouver ? ».

### 9.4 Décisions autonomes et décisions humaines

Choix techniques réversibles, recherche, calculs locaux et améliorations ordinaires peuvent relever de l’autonomie déjà souhaitée. Les préférences utilisateur non déductibles doivent rester explicites, éventuellement comparées sous plusieurs scénarios.

Le fait d’avoir des crédits AWS n’est pas un budget illimité ; une extension payante ou une publication doit respecter l’autorisation réellement donnée. Les consignes du concours ne doivent pas devenir un prétexte à ajouter des démarches inutiles. Les quelques contraintes explicites restent cependant des données du problème.

### 9.5 Mémoire de projet et reprise

Un contexte durable peut être organisé en quelques dossiers conceptuels : mandat court, sources originales, vision initiale, exigences vérifiées, questions de recherche, décisions, état courant, preuves de résultat. Les noms de fichiers et technologies de stockage restent libres.

À chaque interruption, l’état utile indique : version produite, ce qui marche réellement, changements non intégrés, calculs dont l’état a été vérifié, prochaine action par branche et blocages réels. « Préparé », « implémenté », « testé » et « déployé » sont des états distincts.

Les enseignements de CALIBRE sont directement applicables : ne pas annoncer disponible ce qui n’est qu’un script ; ne pas confondre trois tâches prévues avec trois résultats visibles ; ne pas faire attendre toute la réalisation derrière un raffinement local.

## 10. Exemple de boucle complète, sans imposer le produit final

Une personne fictive demande : « Je prépare ma retraite dans quelques années, mais je voudrais étudier une grande entreprise technologique très médiatisée. »

1. **Cadrage :** distinguer exploration d’un actif et demande d’allocation ; conserver l’objectif de retraite et l’horizon, sans inventer le capital.
2. **Clarification ciblée :** déterminer si la liquidité ou la part de portefeuille concernée change matériellement l’analyse. Sinon proposer plusieurs scénarios explicitement fictifs.
3. **Décomposition :** concentration, risque historique, horizon, exposition déjà détenue, données manquantes.
4. **Recherche :** sélectionner les connaissances nécessaires ; ajouter des données fondamentales seulement si une conclusion de valorisation est envisagée.
5. **Calcul :** comparer des scénarios cohérents dans une devise définie ; montrer les hypothèses plutôt que choisir le résultat historique le plus favorable.
6. **Critique :** vérifier la disponibilité temporelle, les contraintes et la portée des conclusions.
7. **Restitution :** expliquer la tension, les possibilités et le paramètre qui ferait évoluer l’analyse.
8. **Interaction :** une modification de l’horizon relance les calculs affectés ; elle ne nécessite pas forcément de refaire toute la recherche.

La différence avec un chatbot générique tient au lien entre chaque conclusion, le profil, les données et les calculs. Le succès de cette boucle doit être montré, pas simplement décrit.

## 11. Questions de recherche à laisser ouvertes à Claude

- Quel cas d’usage permet le meilleur alignement entre utilité réelle, profondeur scientifique et preuves démontrables au jury ?
- Quelle représentation des préférences évite à la fois simplification abusive et précision fictive ?
- Quelles informations ont la plus forte valeur de clarification dans chaque scénario ?
- Quand une conclusion conditionnelle est-elle plus utile qu’une allocation unique ?
- Quel degré de robustesse est justifié par le nombre et la nature des observations disponibles ?
- Comment présenter une contradiction documentaire ou une absence de preuve sans masquer la décision ?
- Quelles fonctions nécessitent vraiment un agent, et lesquelles doivent être du calcul déterministe ?
- Quels précédents ouverts offrent une méthode réutilisable avec une licence et des dépendances adaptées ?
- Quel service AWS améliore effectivement le fonctionnement et la démonstration ?
- Comment mesurer fidélité de l’explication, adaptation au profil et compréhension utilisateur ?
- Quelle expérience ferait abandonner l’architecture favorite ?
- Quelle recherche supplémentaire changerait une décision, et laquelle ne ferait qu’allonger le dossier ?

Ces questions ne sont pas une liste fermée. Leur rôle est d’éviter un départ générique tout en autorisant une reformulation profonde.

## 12. Orientation recommandée à ce stade

La meilleure traduction de ta vision semble être **une aide à la décision dont les conclusions sont accompagnées de preuves consultables et de conditions de révision**. Elle pourrait intégrer une dimension d’allocation robuste, d’ESG ou de diversification selon les recherches et les données, sans devoir simuler toute une banque.

Ce positionnement conserve ton exigence de rigueur et ton goût du raisonnement. Il évite de promettre une solution financière universellement optimale ou d’associer sophistication et nombre d’agents.

La sélection finale devrait comparer plusieurs candidats sur les mêmes critères et montrer un premier résultat concret. Le présent document ne l’a pas encore effectuée par expérimentation et ne prétend donc pas l’avoir démontrée.

## 13. Perfectionnement de la méthode avec les nouvelles ressources

### 13.1 Deux systèmes multi-agents distincts

**L’équipe de construction** peut répartir recherche financière, critique méthodologique, ingénierie des données, AWS, expérience utilisateur et intégration entre plusieurs agents. Ces rôles sont des missions, pas un nombre obligatoire de processus permanents. Ils travaillent avec des contextes sélectionnés, des contrats de sortie et des responsabilités de fichiers.

**Le produit présenté au jury** peut nécessiter une orchestration différente, voire un agent principal et des outils déterministes. La richesse de l’équipe de développement ne doit pas être copiée automatiquement dans chaque requête utilisateur. Les deux systèmes utilisent l’inférence AWS, mais leurs objectifs, temps de réponse et droits d’action diffèrent.

### 13.2 La récursion devient un processus exécutable

Un nœud contient : question précise, décision qu’elle influence, inconnues, sources déjà qualifiées, options, dépendances, expérience discriminante, résultat, objection restante, responsable et événement qui justifierait sa réouverture. Les tâches se planifient dans un graphe de dépendances ; les faits et arguments dans un graphe de preuves. Aucune base de données graphe particulière n’est imposée.

On approfondit si la prochaine recherche peut changer le choix ou sa fiabilité. On intègre lorsqu’un choix dispose d’un support suffisant et d’une manière de mesurer son effet. Une incertitude nouvelle peut rouvrir une décision. On ne relance pas toute la revue à chaque détail de code, et on ne prétend pas qu’une amélioration locale optimise automatiquement tout le produit.

### 13.3 Recherche puis choix autonome : portée exacte

Avant une décision importante, consulter les ressources déjà qualifiées ; rechercher à nouveau lorsque le sujet est nouveau, instable, contradictoire ou décisif. Comparer la meilleure option pressentie à une alternative sérieuse et à une référence simple lorsqu’elles existent. Si la recherche ne trouve pas de solution connue, enregistrer ce résultat et construire une combinaison justifiée plutôt qu’inventer un précédent.

Une bibliothèque, un framework ou un modèle proposé ici peut être remplacé. L’orchestrateur doit montrer que son remplacement répond au moins aussi bien aux critères pertinents ; il n’a pas besoin de demander l’autorisation pour une amélioration réversible dans le périmètre confié. « Meilleur » signifie meilleur selon des critères explicités et des preuves accessibles, pas selon l’assurance du texte.

### 13.4 Organisation du contexte et de la mémoire

Le mandat complet est une carte d’orientation. Chaque agent reçoit uniquement les passages, données et outils nécessaires, plus les invariants du projet. Les détails restent dans les documents indexés et sont relus à la demande. Les résultats transmis incluent sources, chemins d’artefacts et points non résolus. Un checkpoint conserve l’état réel pour reprendre après compaction, expiration d’accès ou interruption.

Un agent chargé de vérifier reçoit les données et les critères avant le récit de réussite de l’auteur lorsque c’est utile. Un désaccord déclenche une vérification ciblée ; un vote entre agents ne transforme pas une assertion en vérité.

### 13.5 Autonomie pendant la nuit

Au démarrage : inventorier les accès existants, tester les fonctions indispensables, regrouper les seuls accès manquants et vérifier la pérennité de la session. Ensuite : choisir les meilleures tâches disponibles, livrer des tranches complètes, sauvegarder, et continuer les tâches indépendantes lorsqu’une branche bloque.

Un prompt ne renouvelle pas magiquement des identifiants et ne garde pas un ordinateur éteint en fonctionnement. La continuité repose sur un environnement effectif, un superviseur ou mécanisme de reprise adapté, une file de travail persistante et des sorties durables. Le nombre total de tokens du projet n’est pas plafonné arbitrairement ; les limites techniques par appel et les mécanismes contre les boucles sans progrès restent explicites.

### 13.6 Relation avec l’utilisateur

L’utilisateur juge la valeur, la compréhension et l’expérience réelle. Claude recherche, compare, réalise et explique ses décisions en termes accessibles. Ne pas lui redemander le nombre de coéquipiers pour justifier une version médiocre. Ne pas le réveiller pour une couleur, une bibliothèque interchangeable ou un choix déjà délégué. Lui réserver les accès personnels nécessaires, les engagements hors mandat et les préférences impossibles à inférer.

Le compte d’événement et les dates de soumission sont des ressources factuelles à exploiter correctement. Ils ne servent pas à imposer une solution simpliste ; ils obligent à préserver les acquis et à distinguer la version remise des développements ultérieurs.

## 14. Les documents opérationnels disponibles

- [00 : énoncé, notation, données, espace de solutions](00_DECORTICAGE_MULTIDIMENSIONNEL.md).
- [00B : atlas des 36 PDF et du notebook, décisions d’exploitation](00B_ATLAS_DES_RESSOURCES_ET_PLAN_EXPLOITATION.md).
- [02 : mandat complet à transmettre à Claude Code](02_MANDAT_INTEGRE_ORCHESTRATEUR_AWS.md).

Les idées O01–O20 et les agents 0–3 restent la mémoire de l’intention initiale. Le mandat autorise leur amélioration ou leur remplacement raisonné, sans effacer cette origine.
