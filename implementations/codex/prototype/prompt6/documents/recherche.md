# Recherche de conception — rendre une décision examinable

**Proposition pour validation, 15 novembre 2026.** Cette recherche informe le
canvas et le prototype ; elle ne démontre pas encore leur utilisabilité.
Les captures, métadonnées, empreintes et reçus de recherche sont conservés
dans [le registre documentaire](proofs/recherche/sources.json).

La direction recommandée est un **carnet de décision vivant** : une réponse
lisible, sa limite décisive et la prochaine action apparaissent ensemble ;
une comparaison et un inspecteur de preuves permettent d'approfondir sans
quitter cette décision. Le dossier courant reste distinct des variantes.
Les quatre agents deviennent une activité consultable, pas quatre étapes
de navigation obligatoires.

## Ce qui a été réellement consulté

Cinq recherches par `InvokeWebSearch`, profil AWS `alphaforge`, mode
`ranked_search_no_WebAnswer`, ont réussi et leurs reçus sont conservés.
Les documents ont ensuite été récupérés par HTTP ou navigateur, puis lus
directement ou par extraction déterministe. Aucun résumé d'un assistant
de design externe n'a été utilisé.

La session de cette branche est identifiée dans
[route.json](proofs/recherche/route.json) avec le fournisseur
`amazon-bedrock-runtime`. Cette preuve de route n'est pas une validation
scientifique de nos choix. Les captures sont des pièces de travail locales :
elles ne doivent pas être publiées comme une bibliothèque redistribuable.

| Référence et version examinées | Nature et lecture réelle | Principe retenu → application à AlphaForge | Limite ou tension |
|---|---|---|---|
| **R1. Jakob Nielsen, [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/), 3 décembre 2006.** La page donne cette date ; la date 2022 du moteur est une métadonnée d'index, pas une nouvelle publication. | Guide de praticien ; corps de l'article lu intégralement. | Montrer d'abord les fonctions importantes, garder les fonctions spécialisées accessibles avec des intitulés explicites. Le texte distingue divulgation progressive et parcours linéaire : les options interdépendantes doivent rester proches. → Conclusion, limite et action visibles ; paramètres et comparaison côte à côte ; inspecteur de preuve contextuel. | Le guide n'est pas un essai sur un conseiller financier. « Simplifier » ne justifie jamais de cacher une limite qui change la conclusion. Éviter les sous-panneaux imbriqués qui font perdre l'orientation. |
| **R2. Amershi et al., [Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/), CHI 2019 ; [poster des 18 principes](https://www.microsoft.com/en-us/research/uploads/prod/2019/03/AI_Guidelines_Poster_PrintQuality.pdf) et [HAX, correction](https://www.microsoft.com/en-us/haxtoolkit/guideline/support-efficient-correction/).** | Article : notice et résumé lus, pas le PDF intégral ; poster entier et page de correction lus. Le résumé rapporte une évaluation avec 49 praticiens sur 20 produits. | G1/2 : capacités et limites explicites ; G9 : corriger/récupérer ; G10 : préciser ou réduire la portée ; G11 : expliquer ; G16 : conséquences des actions ; G17 : contrôles globaux. → Champs extraits éditables, inconnus explicites, aperçu des conséquences, annulation, séparation entre affichage et profil financier. | L'étude valide surtout la pertinence des principes auprès de praticiens, pas l'amélioration des décisions d'investisseurs. G13 propose l'apprentissage implicite ; nous préférons ici des choix de présentation déclarés et réversibles pour éviter des inférences de compétence non justifiées. |
| **R3. Bansal et al., [Does the Whole Exceed its Parts?](https://arxiv.org/html/2006.14779), arXiv v3 du 12 janvier 2021, CHI 2021, DOI 10.1145/3411764.3445717.** | Résultat empirique ; résumé, passages de méthode et résultats/discussion ciblés lus. Texte HTML complet capturé, pas intégralement lu. | Les explications étudiées n'améliorent pas la performance complémentaire, et expliquer le choix dominant peut augmenter l'adhésion à une réponse erronée. → Ne pas traiter une explication soignée comme une validation ; montrer alternative, condition et preuve ; distinguer contrôle arithmétique et validité externe. | Classification de sentiments et questions LSAT, pas des décisions d'investissement. Les effets ne condamnent pas toute explication ; ils imposent d'évaluer la compréhension et la détection d'erreurs plutôt que la seule confiance déclarée. |
| **R4. van der Bles et al., [The effects of communicating uncertainty on public trust in facts and numbers](https://doi.org/10.1073/pnas.1913678117), PNAS 117(14), 7672–7683, 2020 ; [PDF éditeur archivé à Groningen](https://pure.rug.nl/ws/files/131063442/7672.full.pdf).** | Résultat empirique ; résumé, méta-analyse interne, étude BBC et discussion lus dans l'extraction du PDF version of record. Cinq expériences, n total déclaré 5 780. | Donner l'incertitude numérique lorsqu'elle existe, plutôt qu'un simple mot « estimé ». Le coût moyen sur la confiance est faible pour les intervalles numériques ; il n'est pas nul. → Hypothèses, limites et unités explicites ; intervalles seulement quand le calcul fournit une quantité interprétable. | Étude de confiance envers des statistiques, pas de qualité de portefeuille. **Les deux chocs de Robert ne sont ni un intervalle de confiance ni deux issues équiprobables.** Aucun éventail, probabilité ou score de confiance ne doit être inventé pour appliquer ce principe. |
| **R5. W3C, [WCAG 2.2](https://www.w3.org/TR/2024/REC-WCAG22-20241212/), recommandation du 12 décembre 2024.** | Norme ; critères ciblés lus : 1.4.3/4/10/11, 2.1.1/2, 2.3.3, 2.4.3/7/11, 2.5.8, 3.3.1/2/3/4 et 4.1.3. | Contraste texte 4,5:1 hors exceptions ; fonctionnement clavier ; focus visible non masqué ; reflow à 320 CSS px ; erreurs textuelles ; messages de statut programmatiques. → Boutons natifs, focus restitué après preuve, formulaires associés à leurs erreurs, tableau alternatif au graphique, `aria-live` mesuré, réduction des mouvements. | Une revue ciblée et un outil automatique ne constituent pas une certification WCAG. 24×24 px est le minimum de 2.5.8 avec exceptions ; viser 44 px est notre marge de confort, pas une fausse exigence AA. La désactivation des animations d'interaction relève du critère AAA 2.3.3. |
| **R6. [Our World in Data — Life expectancy](https://ourworldindata.org/grapher/life-expectancy), page capturée le 15 novembre 2026, données indiquées mises à jour le 22 octobre 2025.** | Produit représentatif ; page et métadonnées lues ; navigateur bureau observé, passage Line→Table et panneau Download actionnés. [Capture](proofs/recherche/owid-browser.png). | Définition près du titre, unités et période, labels directs sur les séries, source/transformations, export des données affichées et métadonnées. → Comparaison chiffrée avec son domaine, preuve accessible près du nombre, export portant la révision. | Inspiration d'interaction, aucune preuve causale d'utilisabilité. Le passage au tableau a ouvert le filtre « Countries (237) » plutôt que les six régions de la courbe : la conservation de sélection n'a **pas** été démontrée. AlphaForge doit la garantir explicitement. Ni le code ni les données du produit ne sont repris. |
| **R7. Observable Plot, [Tip mark](https://observablehq.github.io/plot/marks/tip), documentation affichant 0.6.19, capturée le 15 novembre 2026.** | Documentation technique et exemple de produit ; page rendue lue, exemples SVG inspectés visuellement. L'accès HTTP initial était limité (429) ; le navigateur a atteint la documentation officielle redirigée. | Valeurs exactes et unités à la demande ; annotation ancrée ; avertissement sur collisions d'infobulles. → Un point ou chiffre ouvre une explication stable ; une seule preuve active ; contexte conservé. | Le survol seul ne couvre ni clavier ni tactile. La documentation ne démontre pas la supériorité perceptive de l'infobulle. Pour le prototype, un panneau accessible par bouton et un tableau suffisent ; l'adoption de la bibliothèque n'est pas nécessaire. |
| **R8. GitHub Docs, [Comparing commits](https://docs.github.com/en/pull-requests/how-tos/commit-changes/comparing-commits), documentation courante capturée le 15 novembre 2026.** | Documentation technique ; page entièrement lue. Pas de test de création de commit ou de PR. | Choisir explicitement une base et une cible ; identifier précisément les deux versions ; examiner les différences. → Avant/après avec noms de version, champs modifiés et résultats réutilisés ; consultation historique distincte de restauration. | Git sait comparer du texte, pas prouver qu'un calcul financier reste valide. Les dépendances réelles du dossier, pas une différence lexicale, déterminent le recalcul. Copier le vocabulaire Git ferait peser une charge inutile sur les novices. |

Les huit références couvrent des décisions différentes. R1/R2 sont des
principes de conception ; R3/R4 des résultats empiriques ; R5 une norme ;
R6 un produit observé ; R7/R8 des documentations techniques. Aucune référence
esthétique n'est présentée comme une preuve d'utilisabilité.

## Trois directions réellement différentes

| Direction | Organisation et langage visuel | Avantage pour nos tâches | Limite principale | Décision |
|---|---|---|---|---|
| **Conversation guidée** | Dialogue central, une question à la fois, profil latéral, réponses successives. Typographie généreuse, peu d'objets visibles. | Très accessible pour formuler une demande incomplète ; clarification située. | Les comparaisons et les révisions se dispersent dans le fil. L'ancienne réponse peut être prise pour la réponse courante. La prose donne une place excessive au modèle. | Garder l'entrée en langage naturel et les questions ciblées, pas le fil comme objet central. |
| **Laboratoire d'analyse** | Table de paramètres, comparaison dense, graphiques et contrôles simultanés, registre toujours visible. Alignements tabulaires et forte densité. | Rapide pour un utilisateur qui sait quel paramètre examiner ; provenance et méthode immédiatement accessibles. | La première visite demande de comprendre le modèle technique avant de comprendre le résultat. Une abondance de réglages peut suggérer des capacités inexistantes. | Retenir la précision tabulaire et les liens entre calculs pour la profondeur « Méthode ». |
| **Carnet de décision vivant** | Une question financière au centre ; conclusion et limite ; espace de comparaison ; inspecteur latéral pour profil/preuve ; versions en repère permanent. Hiérarchie éditoriale, graphiques sobres, espaces différenciant les fonctions. | Réunit lecture, exploration, correction et contestation. Réduit le trajet vers une preuve et garde la variante séparée du dossier principal. Sert les trois intentions sans changer de résultat. | Exige une gestion rigoureuse des panneaux et du focus ; le niveau « Essentiel » doit préserver les limites ; un graphe complet d'agents risquerait de dominer la tâche. | **Recommandée**, à valider par le prototype et l'essai humain. |

Le choix recommandé combine des contributions utiles des deux premières
directions, mais son objet principal est différent : le lecteur manipule
une décision versionnée, pas une conversation ou une collection de
modules. La couleur et la police accompagnent cette hiérarchie ; elles ne
constituent pas la justification du choix.

## Conséquences précises pour le prototype

1. **Même dossier, plusieurs profondeurs.** Le mode essentiel montre
   résultat, raison principale, limite et suite possible. Le mode méthode
   ajoute formulation, hypothèses, contrôles et sources. Valeurs, unités,
   date, versions et limites déterminantes restent identiques.
2. **Preuve depuis l'affirmation.** Le panneau conserve le texte examiné,
   le champ source, la méthode, les hypothèses et le statut du contrôle.
   « Consultée », « retenue » et « implique cette conclusion » ne sont pas
   synonymes.
3. **Deux gestes distincts.** « Explorer une variante » garde le dossier
   de départ ; « Corriger le dossier » explique ce qui devient périmé avant
   la nouvelle analyse. Fermer ou annuler un brouillon restitue les valeurs
   antérieures.
4. **Révision lisible.** Nommer ce qui change, reste valable ou attend un
   recalcul. Une animation peut expliquer une transition de maquette
   explicitement simulée ; elle ne doit pas prétendre qu'un agent travaille.
5. **Graphiques admissibles.** Robert : montants déplacés et pertes sous
   deux chocs nommés, même unité CAD ; référence simple et plusieurs optima.
   Amira : comparaison rétrospective sur la même fenêtre et la même
   convention ; courbe uniquement si la série réellement calculée est
   disponible, sinon tableau honnête.
6. **Incomplétude utile.** Une question explique quel choix de calcul
   dépend de sa réponse. Une impossibilité affiche le conflit établi et
   son périmètre ; elle n'affiche pas d'allocation fictive.
7. **Retour toujours disponible.** L'orientation indique dossier, version
   et variante. Consulter une ancienne analyse ne la rend pas courante.
   Une restauration future doit être une nouvelle révision explicite.

## Ce qui reste une hypothèse à tester

Le carnet peut aider à retrouver une preuve, mais aucune étude lue ne
mesure cet effet dans AlphaForge. Les contrôles informatifs sont donc :
retrouver la raison de 30 000 CAD ; expliquer pourquoi 40 000 change le
minimum ; retrouver la référence simple ; ouvrir une preuve puis revenir
au même contexte ; corriger et annuler ; comparer sans remplacer le dossier ;
passer à une vue détaillée sans changement de conclusion ; comprendre
qu'un résultat historique d'Amira n'est pas une prévision.

Mesurer réussite et erreurs observées, avec le temps seulement comme
indicateur secondaire. L'essai humain demandé par l'utilisateur demeure
nécessaire. Les tests automatisés peuvent contrôler l'invariance, le clavier,
le focus et l'absence de débordement ; ils ne démontrent pas la compréhension.
