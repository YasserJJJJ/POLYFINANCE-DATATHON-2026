# AlphaForge AI — Décorticage multidimensionnel du datathon

**Document 00 · Analyse de l’énoncé, des données et de l’espace des solutions**  
**Version 2 · 15 novembre 2026 · Cadrage enrichi des ressources AWS ; architecture ouverte**

## Mise à jour du 15 novembre : ce que les nouvelles ressources changent

Cette version remplace le cadrage du 14 novembre pour la suite du projet. Elle conserve l’analyse de l’énoncé et les mesures sur le starter, puis intègre **36 PDF de l’atelier AWS, 254 135 caractères extraits et un notebook d’introduction de 35 cellules récupéré par son lien fourni**. Les PDF sont des captures de pages longues : 36 pages PDF ne signifient pas 36 pages de lecture ordinaire. Les répétitions de navigation gonflent aussi ce volume. Ce sont principalement des ressources techniques et pédagogiques, **pas 36 articles scientifiques financiers**.

L’extraction a couvert les 36 fichiers ; les passages déterminants ont été analysés, et des zones du calendrier, de Claude Code et d’AgentCore ont été contrôlées visuellement. Les exemples n’ont pas été exécutés sur AWS. Les mesures du starter proviennent de l’audit antérieur, conservé sans retélécharger les marchés. Les références nouvelles F01–F36 sont détaillées dans [00B — ressources](00B_ATLAS_DES_RESSOURCES_ET_PLAN_EXPLOITATION.md).

### Trois décisions de cadrage nouvelles

1. **AWS devient aussi la plateforme d’inférence du développement.** L’utilisateur exige que l’orchestrateur, ses sous-agents et les conversations du produit soient exécutés et facturés dans le compte AWS prévu. Il ne suffit donc plus que l’application finale fasse un appel Bedrock. La route de chaque type d’appel, y compris les traitements auxiliaires, devra être vérifiée. Cette analyse n’a pas configuré ces comptes.
2. **L’écosystème fourni permet une recherche outillée ambitieuse.** Claude Code sur Bedrock, recherche web AgentCore, documentation par MCP, Strands, données publiques, RAG et extraction documentaire sont des capacités à évaluer ensemble. Documenté dans l’atelier ne signifie pas déjà activé, permis ou fonctionnel dans le compte.
3. **Le calendrier est désormais documenté.** Le site officiel consulté le 15 novembre indique : fin sur place le 15 à 16 h ; dépôt GitHub et application le 15 à 23 h 59 ; destruction du compte AWS le 16 à 13 h 59 ; vidéo, one-pager et documentation technique le 16 à 14 h. Le fuseau doit être confirmé dans les consignes opérationnelles ; ne pas déduire le temps restant du compteur figé d’un PDF. [Calendrier officiel](https://polyfinances.ca/datathon), F34–F36.

L’ambition scientifique reste ouverte. L’ordonnancement doit néanmoins produire une version du code soumissible avant sa propre échéance, enregistrer les preuves de fonctionnement avant la disparition du compte, puis finaliser les pièces de présentation. Une nouvelle découverte peut nourrir la suite sans être intégrée en cachette au livrable gelé après la date autorisée.

### Promesse de produit à explorer

**Un laboratoire de décisions financières contextualisées : à partir d’une demande, construire un problème explicite, comparer des options calculables, montrer leurs compromis et fournir un dossier de preuves que l’utilisateur peut examiner et modifier.**

Ce candidat doit concurrencer d’autres produits plausibles : comparaison de FNB, audit de concentration et d’exposition, choix conditionnels sous contraintes, analyse documentaire adaptée au profil. Le gagnant n’est pas présélectionné. La question est : lequel offre la meilleure combinaison démontrable d’utilité, de profondeur, d’adaptation, de qualité des données, d’explicabilité et de présentation selon la grille ?

La singularité recherchée pourrait être une **conclusion révisable accompagnée de ses conditions de validité** : « ce choix se justifie sous ces préférences et ces données ; voici ce qui le ferait changer ». Ce positionnement est une proposition de conception, pas une conclusion empirique déjà validée.

### Tirer parti de toutes les ressources sans tout déployer

Chaque ressource reçoit une décision explicite : utiliser, adapter, garder en réserve, remplacer ou écarter avec justification. Bedrock peut servir les modèles ; AgentCore la recherche ; S3 les jeux et traces ; Strands la coordination ; un moteur déterministe les calculs ; une interface sur mesure la décision. Glue, Athena, Quick, Knowledge Bases, Data Automation et Runtime restent candidats selon le besoin établi. Utiliser davantage de services n’améliore pas automatiquement les points AWS.

### Deux précisions qui empêchent une fausse rigueur

- Une preuve mathématique porte sur un problème défini et des hypothèses. Elle ne prouve ni une prévision financière vraie ni une supériorité universelle. La méthode visera des garanties formelles lorsque possibles, des calculs reproductibles, une comparaison empirique loyale et une utilité visible.
- Une fonction Python peut être incorrecte, même si elle est déterministe. Le notebook pédagogique utilise notamment une annualisation de moyenne arithmétique, qui n’est pas le rendement composé historique. Il télécharge le change sans l’appliquer aux indicateurs comparés. Son code doit être compris puis adapté, pas adopté comme certificat scientifique. Voir l’audit N01 dans le document 00B.

---

## Lecture en deux minutes

Le défi n’est pas de découvrir le portefeuille qui aurait gagné le plus, ni de multiplier les agents. Il est de construire une **aide à la décision d’investissement fictive, agentique, adaptée au contexte et capable de rendre ses conclusions vérifiables**. La sophistication mathématique est utile lorsqu’elle améliore effectivement cette décision.

Le point éliminatoire le plus important est **l’intégration AWS réelle et démontrable**, explicitement exigée dans la présentation participants. L’accès à un compte ou à des crédits AWS a été confirmé par le porteur. Aucun service particulier n’est pour autant imposé ou autorisé à consommer un budget indéfini.

La grille répartit les points entre solution (20 %), agentique et explicabilité (20 %), données (20 %), UX/UI (10 %), AWS (15 %) et présentation/valeur business (15 %). Une preuve mathématique élégante seule ne couvre donc pas le défi. Une démonstration accessible, des calculs traçables et une intégration cloud effective sont des éléments du résultat, pas des accessoires.

L’audit a parcouru les six CSV : **31 actifs, 40 049 prix, 658 opérations sur titres, 1 245 taux de change et 8 281 observations macro**. Les formats sont propres, mais leur interprétation présente des pièges : calendriers différents, heures de disponibilité, données macro révisées, deux séries avec octobre 2025 manquant, exposition réelle des FNB non fournie, absence de preuves ESG. « No warnings » n’est pas un certificat de qualité financière.

La piste la plus prometteuse à ce stade est un **comparateur de décisions et de compromis fondé sur le profil et accompagné d’un dossier de preuves**. C’est une hypothèse de produit à mettre en concurrence, pas un mandat de construction déjà arrêté.

## 1. Périmètre, sources et statut des affirmations

### 1.1 Ce qui a été effectivement inspecté

- L’archive `Datathon_AlphaForge_Conversion_Markdown.zip` : index, conversion du cas officiel de 19 pages, présentation de 12 diapositives, versions autonomes et fac-similés disponibles. Les pages d’admissibilité et de notation ont aussi été vérifiées visuellement lors de la relecture.
- Le `README.md` bilingue du starter, le générateur `build_dataset.py` et `sources_metadata.csv` ont été lus intégralement.
- Toutes les lignes des six CSV ont été parcourues par l’audit local ; les assertions de structure et statistiques sont distinguées des vérifications économiques.
- Le fichier d’avertissements a été lu. Le générateur n’a pas été exécuté, les données n’ont pas été retéléchargées et les originaux n’ont pas été modifiés.
- Des sources externes primaires ont été consultées sur le profilage, la qualité temporelle des données, l’optimisation, l’architecture agentique, AWS et l’interaction humain–IA.

L’archive contient des **conversions**, pas les PDF/PPTX originaux. Leur contenu est traité comme documentation du concours fournie par le porteur, sans prétendre à une authentification indépendante auprès des organisateurs. Les instructions contenues dans ces pièces décrivent le concours ; elles ne constituent pas des autorisations d’exécuter du code, de déployer ou de dépenser.

### 1.2 Convention de lecture

- **Énoncé** : exigence ou suggestion directement présente dans une pièce fournie.
- **Mesure** : observation reproductible sur les fichiers locaux.
- **Source externe** : apport documenté d’une publication ou documentation primaire.
- **Interprétation** : conséquence stratégique proposée ici, qui peut être discutée.
- **Piste** : option à rechercher ou expérimenter, non décision acquise.

Références locales abrégées : **C** = cas officiel converti, page indiquée ; **P** = présentation participants, diapositive indiquée ; **R** = README ; **G** = générateur ; **M** = métadonnées. Les documents sont accessibles dans `/Users/vpro/Documents/ChatGPT/CALIBRE/Datathon_AlphaForge/analyse/sources/Datathon_AlphaForge_Conversion_Markdown/`. Les mesures détaillées et empreintes sont dans `/Users/vpro/Documents/ChatGPT/CALIBRE/Datathon_AlphaForge/analyse/audit_stats.json`.

### 1.3 Ce qui reste volontairement ouvert

La taille d’équipe ne conditionne pas l’ambition de cette analyse. La région de référence de l’atelier est us-east-1 ; le calendrier documenté figure en tête de cette version. Les permissions effectives, modèles invocables, quotas, durée des identifiants et consignes opérationnelles finales restent à vérifier. Le caractère sponsorisé du compte ne prouve pas une capacité illimitée.

## 2. Ce que l’énoncé demande vraiment

### 2.1 Le problème central

Le parcours recherché est :

**Question d’investissement → contexte et contraintes → données pertinentes → outils et analyse → conclusion contextualisée → explication vérifiable.**

L’IA apporte une valeur si elle sélectionne des informations pertinentes, adapte les étapes à la demande, détecte ce qui manque, mobilise les bons outils et rend le résultat compréhensible. Un chatbot récitant des généralités sur des graphiques n’établit pas cette valeur. [C3, C8–9, C17 ; P3, P5]

### 2.2 Obligations, libertés et suggestions

| Élément | Statut dans les pièces | Conséquence pour le projet |
|---|---|---|
| Contribution effective d’AWS | Admissibilité explicite, P7 | Montrer un appel ou traitement cloud réellement utilisé dans le parcours démontré. |
| Prototype démontrable et dépôt avec README | Livrable, C15 | Un cas complet et reproductible ; une maquette seule ne suffit pas. |
| Vidéo de démonstration | Livrable, C15/P9 | Environ cinq minutes à titre indicatif, pas durée stricte inventée. |
| Documentation technique | Livrable, C15 | Méthodes, sources, hypothèses, traces, validations et limites. |
| One pager | Livrable, C16 | Une page maximum. |
| Orientation agentique et auto-explicative | Cœur du défi | Pouvoir montrer ce que l’agent a fait et pourquoi le résultat est soutenu. |
| Nombre d’agents | Libre, C8–9/P5 | Un seul agent outillé peut convenir ; plusieurs doivent apporter un gain. |
| Univers et classes d’actifs | Libres, C10 | Aucun des 31 actifs, ni crypto, ni dérivé obligatoire. |
| Starter dataset | Facultatif, C10–14/R | Le conserver, le compléter ou le remplacer selon la question. |
| Trois personas | Situations de référence, C4–7 | Expliquer l’adaptation ; couverture exhaustive non formulée comme obligation. |
| Deux profils contrastés | Conseil, C8/P4 | Démonstration particulièrement utile, sans en faire une règle inventée. |
| Meilleur rendement / prévision future | Non demandé, C3/C18 | Éviter de consacrer tout le projet à battre un indice rétrospectivement. |
| Transactions réelles et données bancaires confidentielles | Exclues, C10/C14/C17/P11 | Simulation avec cas fictifs. |
| Raisonnement interne détaillé des modèles | Non demandé, explicitement exclu de l’explication, C17 | Fournir faits, calculs, hypothèses, actions et résultats observables. |

**Nuance entre documents :** le cas écrit laisse les exigences d’infrastructure aux consignes techniques/logistiques ; la présentation apporte une exigence AWS explicite. Ce n’est pas une raison de considérer AWS facultatif. Vérifier les éventuelles consignes ultérieures sans attendre pour reconnaître cette exigence. [C15–16 ; P7]

### 2.3 Simulation ambitieuse et cadre officiel

Le porteur souhaite reproduire la qualité méthodologique d’une organisation financière. C’est compatible avec le défi : analyses approfondies, scénarios, allocations fictives et études de risques sont permis.

En revanche, l’idée de présenter le produit comme un véritable conseiller personnalisé puis d’ajouter une réserve uniquement à la fin ne correspond pas au cadre explicite des pièces. La solution peut se présenter dès le départ comme un **laboratoire de décision financière sur profils fictifs**, sans bureaucratie supplémentaire. Cette précision préserve la liberté de recherche et évite une contradiction avec les attentes du jury. [C17 ; P11]

## 3. Décomposer la notation sans inventer la grille cachée

| Critère | Poids | Preuve convaincante possible | Échec typique |
|---|---:|---|---|
| Qualité, pertinence, innovation | 20 % | Une tension d’investissement précise, une fonctionnalité distinctive et un parcours achevé. | Assistant financier générique sans problème identifié. |
| Agentique et explicabilité | 20 % | Des choix d’outils adaptés, des conclusions reliées aux sorties et aux sources. | Agents décoratifs ou justification inventée après le résultat. |
| Analyse et traitement des données | 20 % | Dates, unités et calendriers corrects ; analyses reproductibles et utiles. | Jointures naïves, ESG inventé, rendement sans devise. |
| UX/UI | 10 % | Demande libre, profil corrigible, comparaison lisible, détail à la demande. | Questionnaire interminable ou tableau de bord incompréhensible. |
| AWS | 15 % + admissibilité | Rôle nécessaire, exécution démontrée, architecture lisible, accès et ressources maîtrisés. | Logo AWS, architecture dessinée ou services sans usage effectif. |
| Présentation, valeur business, marketing | 15 % | Bénéfice utilisateur observable, contraste avant/après, démonstration mémorable. | Pitch grandiose que le prototype ne tient pas. |

Sources : C19 et P10. Les preuves et échecs proposés sont des **interprétations**, pas des sous-critères divulgués par le jury.

On peut représenter la grille par `S = 0,20 Q + 0,20 A + 0,20 D + 0,10 U + 0,15 W + 0,15 P`, avec des sous-scores sur la même échelle. Mais aucune fonction exacte donnant ces sous-scores n’est connue. Il ne faut pas simuler une précision de classement ni optimiser des pseudo-notes attribuées par un LLM. Utiliser cette formule pour détecter les dimensions oubliées ; utiliser les preuves concrètes pour décider.

**Conséquence :** un meilleur solveur ne compense pas une absence d’AWS ; cinquante papiers cités ne compensent pas des données mal utilisées ; un grand nombre de tests ne compense pas une explication illisible.

## 4. Les personas sont des tests de décision, pas des étiquettes

| Persona | Tension réelle | Données ou clarification nécessaires | Démonstration utile |
|---|---|---|---|
| Amira, 26 ans, horizon ≥15 ans, risque élevé | Intérêt tech/crypto mais volonté de diversification | Détentions existantes fictives, limite de concentration, expositions des FNB, capacité de perte si nécessaire | Montrer une concentration cachée puis comparer plusieurs façons de la réduire sans supprimer son objectif de croissance. |
| Mateo, 41 ans, horizon 8–12 ans, risque modéré | Croissance/stabilité et exclusions ESG | Définition de « controverse importante », catégories exclues, sources datées, méthodologie des fonds | Montrer ce qui est établi, contesté ou inconnu, puis les compromis d’une préférence ESG plus stricte. |
| Robert, 59 ans, horizon 3–5 ans, faible/modéré | Préservation du capital et attrait pour un titre médiatisé | Besoin de liquidité, horizon précis, part concernée, capacité de perte | Expliquer la tension sans acquiescer automatiquement ni lui imposer une allocation « prudente » arbitraire. |

Les âges ne doivent pas devenir des coefficients automatiques de risque. La capacité financière à supporter une perte, la volonté de prendre du risque et le besoin de liquidité sont des dimensions distinctes. Le profil peut contenir des inconnues ; le système doit les reconnaître. Le cadre d’Investment Policy Statement du CFA est une référence utile pour structurer objectifs et contraintes, pas un formulaire obligatoire à copier. [R1]

**Contre-exemples à préparer :** Amira détient déjà beaucoup de son employeur technologique ; Mateo refuse les controverses mais n’a pas défini leur gravité ; Robert veut seulement étudier un titre, pas en acquérir. Une solution qui transforme ces trois demandes en achat de portefeuille n’est pas correctement contextualisée.

## 5. Audit des fichiers : résultats mesurés

### 5.1 Inventaire exact

| Fichier | Lignes de données | Colonnes | Usage et limite principale |
|---|---:|---:|---|
| assets_universe.csv | 31 | 7 | Identité et catégories simplifiées, pas univers historique complet. |
| prices_daily.csv | 40 049 | 9 | Prix et volumes ; devises et horloges différentes. |
| corporate_actions.csv | 658 | 5 | 651 dividendes et 7 événements étiquetés split ; ne pas ajuster deux fois. |
| fx_usdcad_daily.csv | 1 245 | 3 | CAD par USD et inverse arrondi ; taux indicatif, pas prix exécutable. |
| macro_rates.csv | 8 281 | 7 | Neuf séries hétérogènes ; pas de calendrier de disponibilité complet. |
| sources_metadata.csv | 6 | 10 | Provenance de cinq jeux, macro documentée par deux sources. |

Univers : 20 actions individuelles, 4 FNB actions, 4 FNB obligataires, 1 FNB or et 2 cryptoactifs ; 13 instruments CAD, 18 USD. Chaque instrument hors crypto a 1 255 observations ; chaque crypto en a 1 827. La fenêtre des prix est du 12 novembre 2021 au 12 novembre 2026 ; extraction déclarée le 13 novembre 2026. [Mesures ; R/M]

Contrôles réalisés : aucun champ vide selon les marqueurs vérifiés, aucune ligne exacte dupliquée, aucune clé dupliquée dans prix/macro/actions, pas de ticker étranger à l’univers, pas de prix nul/négatif, pas de volume négatif, aucune incohérence OHLC à la tolérance `1e-5`. Un volume nul existe pour ZST.TO le 6 juillet 2022, déjà documenté. Ces constats ne prouvent pas l’authenticité des cours auprès des fournisseurs.

### 5.2 Piège des calendriers : des longueurs identiques cachent des dates différentes

| Comparaison | Résultat |
|---|---:|
| Dates de marché canadiennes / américaines | 1 255 / 1 255 |
| Dates communes | 1 228 |
| Dates propres à chacun des deux marchés | 27 / 27 |
| Dates canadiennes sans FX | 10 |
| Dates américaines sans FX | 37 |
| Dates crypto sans FX | 582 |

Aligner les tableaux par position serait faux. Joindre sur la date ne suffit pas non plus : définir l’heure de connaissance, de valorisation et d’exécution.

Reporter un taux antérieur peut être une convention de valorisation valide si sa fraîcheur est affichée. Cela ne crée pas une séance ni une possibilité d’exécution. Prendre uniquement l’intersection des marchés retire des observations ; remplir les rendements à zéro en ajoute artificiellement à l’estimation. Comparer les conventions selon la question traitée.

### 5.3 Macro : couverture réelle

| Série | Nombre | Début | Fin | Sens |
|---|---:|---|---|---|
| BD.CDN.10YR.DQ.YLD | 1 245 | 2021-11-12 | 2026-11-12 | Rendement actuariel Canada 10 ans |
| BD.CDN.2YR.DQ.YLD | 1 245 | 2021-11-12 | 2026-11-12 | Rendement actuariel Canada 2 ans |
| CPIAUCSL | 59 | 2021-11-01 | 2026-10-01 | Indice IPC américain |
| DFF | 1 826 | 2021-11-12 | 2026-11-11 | Taux effectif des fonds fédéraux |
| DGS2 et DGS10 | 1 248 chacun | 2021-11-12 | 2026-11-10 | Rendements actuariels américains |
| STATIC_TOTALCPICHANGE | 58 | 2021-12-01 | 2026-09-01 | Inflation canadienne annuelle en % |
| UNRATE | 59 | 2021-11-01 | 2026-10-01 | Chômage américain en % |
| V39079 | 1 293 | 2021-11-12 | 2026-11-12 | Taux cible de la Banque du Canada |

**Observation nouvelle : octobre 2025 manque dans CPIAUCSL et UNRATE.** Le générateur retire les valeurs non numériques. Les fichiers ne permettent pas d’expliquer la cause du manque. Ne pas inventer une cause ni interpoler sans justification.

Un IPC daté du premier jour du mois n’était pas forcément connu à cette date. Les chiffres FRED sont aussi révisés. Un décalage de trente jours ne reconstitue pas les millésimes historiques. ALFRED permet de rechercher les informations connues à une date passée ; la disponibilité exacte de chaque série doit être vérifiée. [R/M ; R2]

Options à comparer : retrouver publications et millésimes ; limiter la macro au contexte descriptif actuel ; ou présenter une analyse rétrospective explicitement non réalisable telle quelle à l’époque. Aucun besoin de tout reconstruire si la question retenue n’utilise pas ces données.

Ne pas confondre taux cible et taux effectif, rendement actuariel d’une obligation et rendement réalisé d’un placement, indice IPC américain et pourcentage annuel canadien.

### 5.4 Prix ajustés, distributions, devises et horloges

Selon les documents du starter, `adj_close` incorpore splits et dividendes, tandis que `close` est déjà ajusté pour les splits. Éviter le double ajustement et l’ajout de dividendes à un rendement qui les inclut déjà. `adj_close` peut servir à une série de rendements historiques ; ce n’est pas un prix d’exécution ancien directement utilisable.

Avec `A_t` une série ajustée en USD et `X_t` le nombre de CAD par USD, une conversion cohérente donne :

`1 + r_CAD,t = (A_t / A_(t−1)) × (X_t / X_(t−1))`.

Cette identité suppose des points de valorisation compatibles. Elle ne corrige ni les écarts d’horloge ni les coûts de change. La Banque du Canada publie des moyennes indicatives journalières d’ici 16 h 30 ET, pas un cours de clôture exécutable. Un signal utilisant ce taux pour une décision à 16 h doit traiter sa disponibilité. [R3]

Les prix crypto couvrent le jour UTC jusqu’à minuit. Le prix final de D n’est pas connu à la clôture des actions nord-américaines du même jour civil. L’étiquette « quotidien » masque une fuite potentielle d’information.

L’événement CNQ.TO du 22 août 2022 contient un « split » de 1,021 et un dividende de 0,75 CAD. Présence confirmée ; interprétation économique non vérifiée ici. Le README le signale comme atypique. Vérifier auprès de l’émetteur si une méthode dépend de cet événement.

### 5.5 Ce que « No warnings » signifie réellement

Le générateur vérifie quelques invariants sur les prix, devises et FX, et détecte de grands mouvements ou de longs trous de cotation. Il ne contrôle pas les mois macro absents ni la disponibilité historique, ne vérifie pas les opérations en profondeur et ne garantit pas la cohérence des horloges.

Son seuil de début tardif utilise le 20 du mois plutôt que le début exact. Une absence isolée de séance peut passer le seuil de cinq jours. Le script n’épingle pas les versions des dépendances ; les README/métadonnées ne sont pas régénérés. Les assertions peuvent être désactivées avec Python `-O`. Ce sont des limites d’un starter, pas une preuve que toutes ses données sont inutilisables. [G]

### 5.6 Lacunes déterminantes selon le cas d’usage

- **Diversification réelle :** les FNB peuvent détenir les mêmes entreprises que les actions directes. Compter les tickers n’est pas mesurer les expositions. Ajouter les compositions datées si cette promesse est centrale.
- **ESG :** aucun score ni dossier de controverse. Un fonds nommé ESG ne prouve pas une adéquation à la définition de Mateo. Distinguer exclusion sectorielle, politique du fonds, controverse constatée et information inconnue.
- **Fondamentaux :** aucun bilan ni multiple de valorisation. Ne pas appeler une entreprise « sous-évaluée » à partir de son prix seul.
- **Exécution :** absence de spreads, frais, glissement, fiscalité et contraintes d’ordres. Une simulation de performance doit préciser ses conventions.
- **Sélection historique :** univers choisi en 2026 ; biais du survivant documenté. Pas de prétention à une sélection sans information future en 2021.
- **Profilage :** pas de données personnelles de clients ; les scénarios doivent expliciter leurs hypothèses fictives.

### 5.7 Estimation et métriques : éviter la fausse précision

Une covariance de 31 actifs comporte 496 coefficients distincts, dont 465 covariances entre actifs. Une longue table de prix ne garantit donc pas une estimation stable, particulièrement si les marchés et régimes diffèrent. L’annualisation doit correspondre au calendrier retenu : mélanger mécaniquement 252 séances et 365 jours crypto produit des comparaisons ambiguës. Un drawdown maximal observé décrit un passé particulier ; ce n’est pas une borne garantie de perte future. La période, la fréquence et la convention doivent accompagner chaque métrique.

## 6. Formalisation mathématique : ce qu’elle apporte et ce qu’elle ne promet pas

### 6.1 Définir le problème avant le solveur

Une demande peut être structurée comme `P = (q, g, h, b, c, p, u, τ)` : question, objectifs, horizon, ressources fictives, contraintes, préférences, inconnues et date de décision. Chaque champ a une provenance : déclaré, dérivé, hypothèse de scénario ou inconnu.

Les données utilisables sont `D_τ`, disponibles à la date `τ`, et non simplement toutes les lignes dont la date d’observation précède `τ`. Les actions candidates `a ∈ A(P)` peuvent être des comparaisons, scénarios, réponses conditionnelles ou allocations fictives. Choisir une allocation avant de savoir ce que demande l’utilisateur est déjà une erreur de formalisation.

Si la question nécessite un choix multiobjectif, étudier une frontière de compromis plutôt qu’un score unique inventé. Les préférences ne sont pas automatiquement convertibles en coefficients fiables. Une préférence dure exige une contrainte ; une préférence négociable exige un arbitrage visible.

### 6.2 Exemple illustratif de problème calculable — pas choix retenu

Pour un cas d’allocation fictive, on pourrait comparer un modèle de variance minimale, une approche robuste et un modèle de pertes en queue. Par exemple :

`min_w CVaR_α(L(w)) + λ × coûts(w,w₀)`

sous `Σw_i = 1`, `w_i ≥ 0`, limites explicites de concentration et contraintes documentées du scénario. Ici le choix long-only sans levier est une hypothèse d’exemple, pas une règle imposée à tout projet. Les contraintes de concentration proviennent du cas ou d’une hypothèse déclarée, jamais d’un seuil présenté comme vérité universelle.

Sur `S` scénarios équiprobables, avec une perte affine `L_s(w)`, la représentation est :

`min_(w,z,u) z + [1 / ((1−α)S)] Σ_s u_s + λ × coûts(w,w₀)`

sous `u_s ≥ L_s(w)−z`, `u_s ≥ 0` et contraintes du portefeuille. Cette formulation peut être convexe avec des coûts et contraintes convexes. Elle offre une voie vers un résultat d’optimisation vérifiable. Elle ne rend pas les scénarios exacts, ne garantit pas le risque futur et ne justifie pas à elle seule un choix d’horizon. [R4, R5]

Un objectif de croissance absent de cette formulation ne réapparaît pas magiquement : il faut l’intégrer explicitement ou montrer la frontière de compromis. Les contraintes de cardinalité, certains coûts ou règles logiques peuvent modifier radicalement la difficulté et la nature des garanties.

### 6.3 Quatre niveaux de preuve à ne pas confondre

| Niveau | Exemple de conclusion légitime | Ce qu’il ne démontre pas |
|---|---|---|
| Logique / mathématique | Un résultat satisfait les contraintes ; optimalité sous les hypothèses du modèle. | Que les hypothèses représentent parfaitement les marchés. |
| Numérique | Solveur convergé, résidus et tolérances vérifiés, calcul reproductible. | Que les estimations d’entrée sont exactes. |
| Empirique | Résultat stable sur des périodes ou scénarios réservés et analyses de sensibilité. | Qu’il sera toujours supérieur à l’avenir. |
| Produit | Utilisateur comprend le compromis et peut retrouver les preuves. | Que toute recommandation est financièrement optimale. |

Les preuves conditionnelles doivent préciser hypothèses, domaine de validité et erreurs possibles. Un texte mathématique convaincant produit par un LLM n’est pas un certificat. La vérification algorithmique et l’expérimentation complètent la théorie ; elles ne sont pas seulement un rattrapage tardif.

### 6.4 Pourquoi la recherche d’optima locaux ne suffit pas

Optimiser chaque micro-problème séparément peut dégrader le système : plus de paramètres enrichit le profil mais augmente les erreurs et la friction ; plus d’agents spécialise le travail mais augmente les coûts et les interfaces ; plus de données accroît la couverture mais complique la disponibilité temporelle.

La décomposition doit donc former **un graphe de dépendances**, avec retours vers le problème global. L’arbre sert à explorer ; le graphe représente les contraintes partagées ; le journal de décision explique les arbitrages. L’optimum global n’est pas la somme automatique des meilleurs composants isolés.

## 7. Espace de solutions à comparer, sans fermeture prématurée

| Candidat | Promesse distinctive | Besoin de données décisif | Risque principal | Expérience discriminante |
|---|---|---|---|---|
| A. Comparateur d’adéquation et de compromis | Expliquer pourquoi une décision fictive change avec le profil. | Prix, contraintes, preuves ciblées ; compositions si concentration étudiée. | Devenir un questionnaire avec réponse standard. | Même demande, profils contrastés, décisions et justifications réellement différentes. |
| B. Analyse de diversification cachée | Montrer les expositions communes derrière plusieurs titres/FNB. | Positions et compositions datées. | Confondre nombre d’actifs et indépendance économique. | Ajouter un FNB qui contient déjà les titres détenus et montrer l’effet calculé. |
| C. Recherche ESG avec couverture des preuves | Relier préférences, controverses et incertitudes à des options. | Sources ESG/émetteurs datées et règles explicites. | Déduire « acceptable » d’une absence d’information. | Même dossier, définition d’exclusion modifiée, résultat traçable et conditionnel. |
| D. Laboratoire d’allocation robuste | Comparer solutions mathématiques sous contraintes et incertitudes. | Rendements alignés, estimation et scénarios crédibles. | Précision numérique masquant fragilité statistique. | Perturber les hypothèses et comparer stabilité à une référence simple admissible. |

**Interprétation actuelle :** A offre une enveloppe cohérente ; B, C ou D peuvent fournir sa profondeur distinctive. Mais leur combinaison complète n’est pas automatiquement meilleure. Un résultat théorique plus fort, une disponibilité de données supérieure ou une meilleure démonstration peut justifier une autre orientation.

Une solution différenciante pourrait afficher, pour chaque conclusion : **ce qui la soutient, ce qui la contredit, ce qui manque et quelle modification ferait changer la décision**. Cette promesse est une synthèse proposée ici, pas une nouveauté scientifique revendiquée.

## 8. Science et références : chercher pour décider

Rechercher d’abord les travaux qui répondent aux questions effectivement ouvertes : profilage, objectifs multiples, risque, estimation, preuves ESG, explication, évaluation et orchestration. Le prestige d’une université ou la popularité d’un dépôt ne remplace pas l’adéquation du résultat.

Quelques pistes démontrant l’intérêt de cette démarche :

- Le **shrinkage de covariance** traite une source d’erreur d’estimation importante pour l’optimisation. C’est une option à comparer, pas un remède à toutes les incertitudes. [R6]
- Les comparaisons de méthodes optimisées avec **1/N** motivent une référence simple ; elles ne prouvent pas que 1/N convient à tous les profils ou gagne toujours. Une référence doit respecter les mêmes contraintes. [R7]
- Les travaux sur le **surajustement de backtests** montrent pourquoi choisir le meilleur parmi de nombreux essais peut produire une fausse découverte. Garder un registre des variantes et une évaluation non utilisée pour régler la solution. [R8]
- **FinRobot et TradingAgents** fournissent des précédents à examiner, notamment séparation des rôles, outillage financier et synthèse. Leur existence ne valide ni leurs performances dans notre contexte ni la nécessité de reprendre leur architecture. [R13–14]

Une étude doit avoir une fiche : question, référence vérifiée, accès réel (texte/résumé), population ou données, méthode, résultat, limites, reproductibilité, décision influencée. La cible indicative de cinquante trouvailles n’est pas une obligation de citer cinquante papiers. Le bon indicateur est la couverture des décisions importantes par des preuves pertinentes.

## 9. Agentique et AWS : contribution utile, visible et actuelle

Séparer **l’IA qui construit le projet** du **système agentique qui répondra aux scénarios**. La première peut explorer largement ; le second doit présenter un parcours cohérent, des outils fiables et une latence acceptable.

Comparer un agent outillé, un workflow à étapes, une orchestration avec spécialistes et une combinaison des deux. L’intérêt d’un spécialiste doit être observable : meilleure récupération de preuves, contrôle d’erreurs indépendant, parallélisation réellement utile. Mesurer aussi les coûts, les appels et les échecs d’interface. [R9]

Options AWS à explorer selon l’accès confirmé : modèles via Bedrock, exécution d’un service de calcul, stockage versionné des jeux et preuves, runtime d’agents, journaux observables. Ne pas choisir une pile complète simplement parce que les services existent. Une seule chaîne bien intégrée peut être plus convaincante qu’une collection d’icônes.

**Point de fraîcheur vérifié :** la documentation AWS consultée présente désormais Bedrock Agents comme « Agents Classic », avec fermeture aux nouvelles inscriptions et continuité pour les utilisateurs existants. Elle renvoie vers AgentCore et Strands pour les agents définis en code. Vérifier l’accès réel du compte avant de reprendre un ancien tutoriel ; la date de transition n’est pas établie ici. AgentCore est une option, pas une exigence du concours. [R15–16]

La preuve d’intégration devrait associer un identifiant de requête, un traitement utile effectivement exécuté et le résultat présent dans l’interface. Les traces d’outils et sorties calculées peuvent soutenir l’explication. Ne pas afficher les raisonnements internes détaillés que certaines traces techniques peuvent contenir ; sélectionner les faits observables appropriés. [R17 ; C17]

Aucun appel AWS, déploiement ou coût cloud n’a été engagé pour cette analyse.

## 10. Validation ciblée et démonstration

### 10.1 Contrats définis avant la construction

Énoncer d’abord ce que signifie « correct » : calcul en devise cohérente ; contraintes respectées ou conflit signalé ; source de chaque chiffre ; aucune information future dans une simulation historique ; distinction entre manque d’information et constat négatif.

Préparer quelques cas contrastés et des cas inconnus de l’implémentation. Les exemples de démonstration seuls ne sont pas un ensemble de validation suffisant. Des reformulations d’une même question devraient préserver les contraintes ; une modification de préférence devrait changer les parties pertinentes sans altérer arbitrairement les autres.

### 10.2 Vérifications à forte valeur

| Aspect | Vérification discriminante |
|---|---|
| Données | Deux marchés de même longueur mais dates différentes ; FX manquant ; macro publiée tardivement. |
| Profil | Champ absent, contradiction entre phrase et fichier, préférence faible vs exclusion stricte. |
| Calcul | Exemple analytique simple ; somme des poids ; contrainte impossible ; unités et devise. |
| Explication | Retrouver chaque chiffre ; vérifier qu’une citation soutient réellement l’affirmation. |
| Agent | Défaillance d’un outil, source indisponible, document externe contenant une instruction hostile. |
| Robustesse | Changer fenêtre, coûts, hypothèses et scénario sans choisir après coup le résultat le plus flatteur. |
| UX | Comprendre la conclusion et retrouver la principale réserve sans lire un rapport entier. |
| AWS | Exécution effective dans le parcours ; erreur cloud expliquée ; démonstration de repli étiquetée. |

Une démonstration enregistrée de repli peut être utile, mais doit être présentée comme telle. Elle ne remplace pas une intégration réelle. Aucun nombre arbitraire de tests ni boucle illimitée de relecture ne constitue un objectif.

### 10.3 Récit possible pour la vidéo

Ouvrir par une question concrète ; montrer les informations utiles extraites ; faire voir une tension ; exécuter un calcul ; afficher les preuves ; modifier une hypothèse ; constater le changement ; montrer le rôle AWS ; terminer par l’utilité et la limite principale. Deux profils contrastés peuvent suffire à rendre l’adaptation visible. Ce scénario de présentation reste ajustable au produit finalement retenu.

## 11. Décisions ouvertes après ce premier document

1. Quel problème utilisateur mérite la démonstration principale, et contre quelles alternatives a-t-il été choisi ?
2. Quelle promesse peut être soutenue par les données effectivement disponibles ?
3. Quelle formalisation rend la décision vérifiable sans masquer les préférences derrière des paramètres arbitraires ?
4. Quelle information supplémentaire vaut réellement la peine d’être demandée au profil fictif ?
5. Quelle architecture agentique améliore le résultat mesurable ?
6. Quel service AWS joue un rôle utile dans le compte disponible ?
7. Quel contre-exemple ferait abandonner la solution favorite ?
8. Quelles preuves permettront au porteur de défendre le projet lui-même devant le jury ?

Il n’est pas nécessaire de résoudre tous les problèmes de la finance pour répondre de façon remarquable à une question choisie. Il est en revanche nécessaire que la profondeur annoncée corresponde à ce qui est montré.

## 12. Registre des références externes consultées

Consultation le 14 novembre 2026. Recherche ciblée, non revue systématique exhaustive. Les références ci-dessous ne sont pas toutes des articles scientifiques : leur nature et le niveau de lecture sont indiqués pour ne pas confondre doctrine, résultat expérimental, documentation et projet logiciel.

| ID | Source primaire / niveau consulté | Apport utilisé et limite |
|---|---|---|
| R1 | [CFA Institute, Basics of Portfolio Planning and Construction, curriculum 2026](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/basics-of-portfolio-planning-and-construction) — introduction, objectifs et synthèse publics ; chapitre complet non consulté | Objectifs, contraintes, capacité/volonté de risque, IPS. Cadre professionnel, pas preuve d’un questionnaire optimal. |
| R2 | [FRED, Real-Time Periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html) — documentation lue | Dates de connaissance et révisions ALFRED. Pas reconstruction effectuée dans cet audit. |
| R3 | [Banque du Canada, Background information on foreign exchange rates](https://www.bankofcanada.ca/rates/exchange/background-information-on-foreign-exchange-rates/) — sections de méthode/publication consultées | Moyennes indicatives et horaire de publication. |
| R4 | [Boyd et Vandenberghe, Convex Optimization](https://stanford.edu/~boyd/cvxbook/) — page des auteurs et ressources repérées ; livre non intégralement analysé | Référence pour convexité, dualité et certificats à approfondir si solveur retenu. |
| R5 | [Rockafellar et Uryasev, Optimization of Conditional Value-at-Risk, 2000](https://doi.org/10.21314/JOR.2000.038) — référence repérée et [bibliographie de l’auteur](https://uryasev.github.io/publications/) | Source de la famille de formulations CVaR ; analyse intégrale à réaliser avant choix final. |
| R6 | [Ledoit et Wolf, Honey, I Shrunk the Sample Covariance Matrix](https://ledoit.net/honey.pdf) — résumé du manuscrit des auteurs, novembre 2003 | Erreur d’estimation et shrinkage ; résultats non reproduits ici. |
| R7 | [DeMiguel, Garlappi et Uppal, Optimal Versus Naive Diversification, 2009](https://moodle.novasbe.pt/pluginfile.php/664905/mod_folder/content/0/Articles/DeMiguel_Garlappi_Uppal_2009.pdf?forcedownload=1) — résumé du papier hébergé par une université ; [bibliographie auteur](https://www.ramanuppal.com/research/) | Comparaison empirique à 1/N ; aucun résultat universel de supériorité. |
| R8 | [Bailey et al., The Probability of Backtest Overfitting, version 2015](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf) — référence et début du manuscrit ; [article associé, résumé](https://www.davidhbailey.com/dhbpapers/overfitting.pdf) | Risque lié à la sélection de nombreuses variantes ; revue mathématique complète non réalisée. |
| R9 | [Anthropic, Building effective agents, 19 décembre 2024](https://www.anthropic.com/research/building-effective-agents) — sections architecture consultées | Workflow, agents et coûts de complexité ; retour d’expérience fournisseur, outils à revérifier. |
| R10 | [Anthropic, Effective context engineering for AI agents, 29 septembre 2025](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) — article consulté | Contexte sélectionné, recherche à la demande, mémoire ; pas nécessité d’un prompt géant. |
| R11 | [Anthropic, Harness design for long-running application development, 24 mars 2026](https://www.anthropic.com/research/harness-design-long-running-apps) — sections génération/évaluation consultées | Séparer production et critique, critères concrets ; ne justifie pas une boucle coûteuse illimitée. |
| R12 | [Amershi et al., Guidelines for Human-AI Interaction, CHI 2019](https://www.microsoft.com/en-us/research/wp-content/uploads/2019/01/Guidelines-for-Human-AI-Interaction-camera-ready.pdf) et [page du projet](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/) — résumé et présentation primaire | Cadre pour compréhension, correction et contrôle utilisateur ; application locale à évaluer. |
| R13 | [AI4Finance Foundation, FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) — README public consulté | Précédent de recherche financière outillée et calcul séparé de la narration ; code non exécuté/audité ici. |
| R14 | [TauricResearch, TradingAgents](https://github.com/TauricResearch/TradingAgents) — page du dépôt consultée | Précédent multi-agent financier à étudier ; aucune performance validée ici. |
| R15 | [AWS, collaboration Bedrock Agents / avertissement Classic](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-multi-agent-collaboration.html) — avertissement de disponibilité lu | Éviter les choix fondés sur un tutoriel obsolète. |
| R16 | [AWS, Get started with Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-get-started-cli.html) — parcours de documentation consulté | Option actuelle à comparer selon compte, région et besoin. |
| R17 | [AWS, Trace events](https://docs.aws.amazon.com/bedrock/latest/userguide/trace-events.html) — structure des traces consultée | Entrées/sorties d’outils observables ; sélectionner ce qui convient à l’explication utilisateur. |

## 13. Portée exacte de ce livrable

Ce document fournit une base documentée pour choisir le projet. Il ne constitue ni une stratégie financière validée, ni un audit exhaustif de la littérature, ni un plan d’exécution verrouillé. Aucune recommandation d’achat réelle n’a été produite.

Le document 00B organise les nouvelles ressources, le document 01 préserve la vision initiale et perfectionne la méthode, et le document 02 fournit désormais le mandat complet de lancement de Claude Code. Ces documents ont été rédigés à la demande explicite du porteur.

## 14. Petit glossaire pour défendre le projet

| Terme | Sens utile ici |
|---|---|
| Agent | Modèle qui choisit des actions ou outils selon le contexte, au-delà d’une réponse textuelle unique. |
| Workflow | Enchaînement organisé d’étapes ; certaines peuvent appeler un modèle sans que tout soit autonome. |
| AWS / Bedrock / AgentCore | AWS est la plateforme cloud ; Bedrock donne notamment accès à des modèles ; AgentCore fournit des capacités pour faire fonctionner des agents. Ce ne sont pas trois synonymes. |
| Point-in-time | Données effectivement connues à la date simulée. |
| Backtest | Simulation d’une règle sur des données passées, avec conventions explicites. |
| Benchmark / baseline | Référence comparable permettant de mesurer le gain réel d’une solution. |
| Out-of-sample | Données non utilisées pour choisir ou ajuster la méthode évaluée. |
| Shrinkage | Régularisation qui réduit certaines estimations extrêmes pour limiter l’erreur. |
| CVaR / expected shortfall | Mesure de pertes en queue de distribution, conditionnelle au modèle ou aux scénarios utilisés. |
| Provenance | Origine d’une donnée ou affirmation et transformations qui ont conduit au résultat. |
| Ablation | Retirer un composant pour voir ce qu’il apporte réellement. |
| RAG | Recherche de documents utiles avant de générer une réponse ; une citation récupérée n’est pas automatiquement une preuve suffisante. |
