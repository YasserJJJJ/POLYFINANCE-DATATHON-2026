# Revue indépendante du prototype — Prompt 6

**Périmètre : prototype local sur `http://127.0.0.1:8770`, avant intégration au produit. Dernière contre-vérification : 15 novembre 2026, 20:01 UTC.** Les cinq défauts démontrés ci-dessous sont corrigés et les comportements concernés ont été revérifiés. La revue vérifie des tâches et des contre-exemples ; elle ne tient pas lieu de validation humaine de la direction visuelle.

Le relecteur n’a écrit ni le prototype ni son adaptateur. Il a inspecté le rendu, les interactions et les données consommées. Navigation Chromium/Playwright, calculs locaux et axe-core sont sans inférence auxiliaire. La session du relecteur conserve la route AWS documentée dans l’[audit initial](audit_initial.md).

## Tâches effectivement essayées

| Tâche | Observation |
|---|---|
| Ouvrir le dossier Robert | L’état r5 montre le minimum calculé de 30 000 CAD, la réserve abstraite et la limite de la référence simple. |
| Changer le niveau de lecture | Les trois niveaux gardent la même valeur principale. « Les options » ajoute les allocations et pertes sous scénarios ; « La méthode » ajoute sources et contrôles. Le réglage n’appelle pas de calcul. |
| Retrouver la raison d’un chiffre | Le panneau de preuve donne la question, les entrées, le critère, sa portée, le lien exact et l’accès aux sources. Ouverture au clavier et retour du focus après Échap observés. |
| Chercher une source | Une recherche sans correspondance produit un état vide explicite ; « Boyd » retrouve une source. Les passages et métadonnées restent accessibles. |
| Examiner les révisions réelles | Les états r5, r10 et r15 montrent 30 000, 40 000 et 74 400 CAD. Les changements humains et les pièces conservées sont distingués. |
| Calculer une variante | Passer le retrait de 30 000 à 40 000 CAD appelle le moteur réel du prototype. Le résultat local peut être adopté dans une copie puis annulé en revenant à r5. |
| Reprendre après une erreur | L’erreur explicitement simulée conserve 35 000 CAD saisis ; la reprise calcule cette valeur. Le dossier archivé ne change pas. |
| Examiner Amira | Résultats rétrospectifs, courbe et table de toutes les observations. Aucun rendement futur n’est présenté comme calculé. |
| Demande incomplète et retrait impossible | Aucune allocation inventée ; l’absence de données et le certificat d’écart budgétaire restent des états différents. |
| Petites tailles d’écran | Parcours à 390 et 320 px. Les cartes, boutons, preuves et tables ont été rendus. Le débordement du certificat à 320 px a été détecté puis corrigé. |

Les [preuves du parcours initial](proofs/audit/prototype/report-before-fixes.json) contiennent 34 vérifications fonctionnelles, dont deux échecs démontrés. Les analyses axe sont consignées séparément : ne pas additionner ces nombres pour prétendre mesurer une fiabilité générale.

## Défauts démontrés et corrections ciblées

| Critique | Observation reproductible | Impact | Correction / résultat de contre-vérification |
|---|---|---|---|
| **P1 — Mauvaise base d’une copie adoptée** | Calculer depuis r5, retrouver ce calcul depuis r15, puis adopter affichait « Revenir à l’archive r15 », bien que le calcul ait r5 pour base. | Confusion entre version de départ, résultat local et retour à l’archive. | L’adoption rétablit désormais `base_version_id`; la restauration retrouve r5 et son minimum de 30 000 CAD. |
| **P1 — Multiplicité affirmée sans témoin** | Robert r15 affichait « Même minimum, expositions différentes » alors que `non_unique_witness_found=false`. | Le texte allait au-delà de la preuve numérique. | Les deux textes, synthèse et graphique, sont maintenant conditionnés au résultat. r15 indique qu’aucun témoin d’optimum multiple n’a été trouvé, sans proclamer un théorème d’unicité. |
| **P2 — Contraste d’étiquettes du graphique** | Les quatre étiquettes blanches de XIU sur `#7593b4` avaient un contraste de 3,18:1 à 10 px. | Chiffres difficiles à lire, sous le seuil AA de 4,5:1. | Couleur de texte corrigée. Contre-vérification axe de l’écran d’options : aucune violation détectée. |
| **P2 — Débordement du certificat** | À 320 px, le bloc d’équation dépassait jusqu’à 350 px. | Perte du signe ou de la valeur d’écart sans défilement latéral. | Mise en page responsive corrigée ; largeur de page observée = 320 px. |
| **P2 — Réponse asynchrone après navigation** | Une réponse de calcul retardée de 700 ms, suivie d’un retour aux dossiers pendant le chargement, produisait `Cannot set properties of null (setting 'disabled')`. | Le retour de l’opération cherchait à mettre à jour un formulaire qui n’existait plus. | Le calcul capture son formulaire et son contexte. Après correction : aucun `pageerror`, accueil préservé, résultat conservé avec sa base r5 ; réouverture depuis r15, adoption puis retour à r5 vérifiés. |

Des renforcements connexes ont aussi été vérifiés : modifier un formulaire après calcul signale le résultat périmé et désactive son adoption ; annuler les modifications restaure les valeurs de référence et masque le résultat de l’essai. La fiche d’impossibilité présente bien l’écart **20 000 CAD**, un contrôle algébrique et l’absence de solveur/IIS global.

Les contre-vérifications n’ont pas relancé l’ensemble des parcours. Le premier test ciblé conserve un faux échec de recherche de texte : `innerText` reflétait les majuscules CSS du libellé de base. Le [dernier contrôle](proofs/audit/prototype/retest-async-final.json) utilise le contenu textuel, confirme « depuis r5 » et vérifie l’adoption/restauration. La réponse HTTP 503 du parcours initial provient uniquement de l’erreur de démonstration explicitement demandée.

## Jugement d’expérience, avec ses limites

La direction répond au principal obstacle de l’interface précédente : sur mobile 390 × 844, la conclusion de Robert commence maintenant à **478 px**, contre une première affirmation à **1115 px** dans l’application observée. L’utilisateur n’a plus à parcourir les quatre cartes d’agents avant de savoir ce qu’il apprend.

La réserve abstraite, l’absence de probabilités et l’exclusion des frais restent dans le flux normal, près du montant. Sur ce téléphone, leur bloc commence à 793 px et se termine à 899 px : un petit défilement est encore nécessaire pour tout lire. Ce n’est pas une limite cachée derrière le niveau expert. La restriction rétrospective d’Amira est également proche des résultats, et les détails supplémentaires sont accessibles.

La séparation « archive / exploration / copie locale » est beaucoup plus explicite que dans l’application initiale. Les dépendances prévues ne sont pas animées comme des événements exécutés. La récupération reste compréhensible parce que l’erreur d’essai, les paramètres conservés et l’action de reprise sont nommés.

La présentation conserve toutefois une limite de produit : une demande libre ou la correction d’Amira produit seulement un brouillon. Ce statut est annoncé ; la qualification et l’intégration au produit restent à réaliser après validation. Le passage de l’exemple à une expérience générale n’est donc pas encore démontré.

## Ce que les contrôles ne certifient pas

- Aucun participant humain n’a été observé en train de comprendre ou choisir. Les effets sur l’effort cognitif et la qualité de décision restent à éprouver.
- axe et les mesures DOM ne constituent pas un audit WCAG complet. Lecture d’écran, zoom utilisateur, langues, matériels et préférences d’accessibilité variés restent à examiner lors de l’intégration.
- Le mode réduit des animations a été activé pour les contrôles, mais aucun bénéfice utilisateur n’est inféré de ce seul réglage.
- L’invariance vérifiée concerne les valeurs et limites déterminantes visibles et les opérations déclenchées. Elle n’est pas une preuve formelle de l’équivalence sémantique de toutes les formulations possibles.
- Les calculs du prototype réemploient le moteur existant ; ils ne reproduisent pas une nouvelle revue AWS des quatre agents.

## Traces

[Parcours et captures](proofs/audit/prototype/) ·
[Script du parcours](proofs/audit/inspect_prototype.cjs) ·
[Contre-vérifications ciblées](proofs/audit/prototype/retest.json) ·
[Script ciblé](proofs/audit/retest_prototype.cjs) ·
[Contre-vérification asynchrone finale](proofs/audit/prototype/retest-async-final.json) ·
[Script asynchrone](proofs/audit/retest_async.cjs) ·
[Mesures de lecture mobile](proofs/audit/prototype/mobile_reading.json)
