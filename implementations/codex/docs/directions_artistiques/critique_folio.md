# Critique indépendante de Folio

**Parcours examiné : http://127.0.0.1:8770/directions/folio/**

Revue du 15 novembre 2026 par la branche Isobare, qui n'a écrit ni le HTML,
ni le CSS, ni le rendu de Folio. Le contrôleur et l'adaptateur de données
sont communs : l'indépendance porte sur la direction et ses affirmations,
pas sur une expertise externe au projet. Aucun fichier Folio n'a été
modifié par le relecteur. Les corrections sont faites par son auteur ou,
pour le contrôleur partagé, par l'intégrateur.

## Observations établies et corrections

| Observation reproductible | Impact | Correction et état |
|---|---|---|
| Après un retrait local de 120 000 CAD puis retour à « Comprendre », le titre signalait l'impossibilité mais le corps disait « Cette valeur minimise… » et « premier optimum ». Le moteur ne produisait ni option ni minimum. | La narration contredisait le résultat et pouvait faire croire qu'une solution existait malgré l'échec. | L'auteur a conditionné toute l'interprétation : aucune allocation établie, contraintes à revoir, résultat précédent non applicable. **Corrigé ; retest ciblé réussi.** |
| Avec retrait 30 000 et budget de perte 0, le moteur calcule 100 000 CAD à réallouer. « Comprendre » affichait encore « sans tout déplacer ». | Le titre déformait une conséquence importante du profil. | Titre conditionné lorsque le minimum atteint le capital : « Le mandat exige de tout déplacer ». **Corrigé ; résultat réel 100 000 et titre revérifiés.** |
| Dans la preuve, le bloc JSON des contrôles défilait mais n'était pas atteignable au clavier dans Safari selon axe. | Les détails de calcul n'étaient pas inspectables de façon équivalente au clavier. | Le contrôleur commun ajoute `tabindex=0`, rôle `region` et nom issu du résumé à chaque bloc. **Corrigé ; axe preuve : 0 violation, 0 incomplet, 27 contrôles réussis.** |
| Les notes marginales utilisaient plusieurs `aside` sans noms distincts ; le choix du niveau de lecture était hors repère de page. | Navigation par régions ambiguë pour les technologies d'assistance. | L'auteur a nommé les notes et placé les réglages de lecture dans une région nommée. **Corrigé ; axe essentiel : 0 violation signalée.** |
| Après impossibilité, le récapitulatif partagé disait encore « Allocation, contraintes, minimum et conclusion » sous « Calculs réexécutés ». La méthode gardait une formulation d'optimum. | La trace visible attribuait au moteur une résolution qui avait été court-circuitée. | L'intégrateur distingue la faisabilité, l'absence d'allocation et le certificat algébrique `120 000 − 100 000 = 20 000 CAD`. **Corrigé ; delta, méthode approfondie et preuve revérifiés.** |

Le premier contrôle automatisé du texte « aucune allocation » cherchait
une minuscule alors que l'interface utilisait « Aucune ». Cette erreur du
script a été corrigée ; aucun nouveau défaut produit n'en a été déduit.
La note et l'extrait réellement lu restent dans les preuves.

## Comportements vérifiés

Les quatorze vérifications ciblées initiales passent : Robert r5 et son
minimum 30 000 ; invariance des chiffres entre lectures ; formulation et
contraintes avant la planche en lecture approfondie ; preuve du chiffre
avec chemin JSON ; retour du focus après Échap ; quatre options comparées ;
calcul local réel du retrait 40 000 sans inférence ; différences avant/après
visibles ; annulation vers r5 ; impossibilité 120 000 sans option ; message
d'impossibilité ; absence de débordement global à 390 px dans les deux
lectures ; aucune erreur JavaScript observée.

Les poids et les pertes affichés sont issus des objets retournés par le
contrôleur. La règle simple est bien présente uniquement dans r5 et son
égalité sur le minimum est expliquée. Elle n'est pas transformée en une
preuve de supériorité des agents. Les alternatives gardent leurs unités
CAD, leurs mêmes chocs et leur même capital initial.

Les captures ont été vues, pas seulement générées :
[bureau](proofs/references/folio-review-desktop.png),
[lecture approfondie](proofs/references/folio-review-deep.png),
[mobile](proofs/references/folio-review-mobile.png),
[impossibilité corrigée](proofs/references/folio-review-impossible-corrected.png).
La lecture approfondie réorganise réellement la page : résultat condensé,
mandat, objectif, contraintes, matrice des chocs, puis conséquences.
Le tiroir de preuve conserve le contexte du dossier.

## Contraste et accessibilité : portée des vérifications

Calcul indépendant sur les couleurs CSS : texte principal **10,54:1**,
secondaire **5,24:1**, accent rouge **5,54:1**, texte du bouton **11,42:1**,
texte de la ligne sélectionnée **9,80:1**. Ces couples dépassent 4,5:1.
La texture, le rendu des glyphes et l'anticrénelage ne sont pas inclus dans
ce calcul. Les séparateurs décoratifs sont à 1,65:1 ; ils ne portent pas à
eux seuls une information financière.

Folio ne présente aucun graphique à axe gradué : la comparaison repose sur
un tableau et des barres de poids. Il n'y a donc pas de « contraste d'axe »
numérique à certifier. Les barres possèdent des libellés et une légende
chiffrée ; la couleur n'est pas l'unique porteur de l'information.
Les courbes derrière le chiffre d'accueil sont décoratives et `aria-hidden`,
sans unités ni donnée financière revendiquée.

Après corrections, **axe 4.14.0** ne signale aucune violation sur la page
essentielle ni sur la preuve. Il laisse cependant **106 nœuds de contraste
à revoir** et un contrôle d'attribut ARIA incomplet sur la page essentielle.
Ces résultats incomplets ne sont pas comptés comme réussites. Les calculs
manuels de contraste ci-dessus sont distincts du résultat automatique.
La preuve ouverte ne laisse aucun contrôle incomplet dans ce passage.

## Limites restantes

La hiérarchie éditoriale, les textes longs et les annotations de petite
taille demandent encore un essai humain ; aucune amélioration mesurée de
compréhension n'est revendiquée. Le clavier a été exercé sur la preuve et
ses retours de focus, pas sur toutes les combinaisons de lecteur d'écran,
OS et navigateur. Les tests portent sur le contrat Robert commun aux trois
directions, pas sur l'intégration générale du produit.

Les reçus, observations avant correction et retests sont conservés dans
[folio-review-checks.json](proofs/references/folio-review-checks.json).
Le rapport axe initial séparé est
[folio-review-axe.json](proofs/references/folio-review-axe.json) ; les résultats
après correction sont dans `correction_verification` du premier fichier.
Aucun nouveau défaut bloquant établi ne reste ouvert sur ces parcours.
