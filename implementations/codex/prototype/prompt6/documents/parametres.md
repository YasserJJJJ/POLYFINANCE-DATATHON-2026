# Paramètres, provenance et réversibilité

**Référence : prototype v0.1.** Une valeur initiale vient de la version
ouverte. Une nouvelle saisie est une déclaration d'exploration locale ;
elle ne réécrit pas les faits archivés. Aucune préférence n'est créée par
un curseur silencieusement initialisé.

## Paramètres financiers modifiables dans l'atelier Robert

L'interface envoie les quatre valeurs à
`POST /api/prototype/explore`. Le serveur copie le problème de la version
choisie, valide les entrées et appelle
`alphaforge_app.decision.finance.analyze`. Pas de nouvelle inférence,
pas d'écriture dans le magasin de dossiers.

| Paramètre | Signification / provenance | Valeurs initiales archivées | Unité et domaine exposé | Effet et recalcul | Annulation |
|---|---|---|---|---|---|
| **Retrait prévu** `withdrawal_cad` | Montant à réserver à l'échéance, distinct d'une perte de marché. r5 déclaré ; r10 corrigé dans une vraie demande. | r5 : 30 000 ; r10/r15 : 40 000. | CAD ; interface entière, de 0 à 10¹² ; serveur exige un nombre fini dans ces bornes. Le plafond technique n'est pas une règle de convenance. | Change le besoin de réserve, l'allocation et ses contraintes. Peut établir `retrait > capital`. Recherche générique, chocs et pertes initiales restent indépendants si le capital ne change pas. | Réinitialiser le formulaire ou écarter l'essai ; l'archive garde son montant. |
| **Perte admissible par choc** `scenario_loss_limit_cad` | Contrainte déclarée sur chacun des chocs fournis ; aucun quantile ou niveau de confiance implicite. | r5/r10 : 15 000 ; r15 : 1 000. | CAD ; 0 à 10¹² ; pas de montants booléens/non finis. | Change l'ensemble admissible et le capital minimal déplacé. Ne change ni rendements des chocs ni pertes du portefeuille initial. | Même mécanisme ; aucune hausse automatique de la contrainte pour obtenir une solution. |
| **Capital initial** `capital_cad` | Base du portefeuille et des montants. Le 100 000 de Robert a été extrait de sa demande puis conservé par provenance immuable. | 100 000 aux trois états. | CAD ; interface de 1 à 10¹², pas de 1 ; serveur strictement positif ≤10¹². | Change tous les montants CAD et la faisabilité. Les pertes initiales CAD deviennent dépendantes de la correction ; les poids et chocs restent les mêmes. | Retour au capital de la version consultée ; aucune écriture de l'archive. |
| **Plafond initial de TSLA** `tsla_cap` | Contrainte de poids à l'allocation initiale, pas un plafond continuellement garanti après variation des prix. | 10 %. | Interface 0–100 %, pas de 0,1 point ; API fraction 0–1. Conversion `% / 100` explicite. | Change les allocations admissibles, le minimum et les sensibilités ; ne modifie pas les chocs. | Retour au plafond initial ; ne remplace pas une préférence souple par une nouvelle contrainte durable. |

Les valeurs de 0 CAD sont des valeurs, pas des absences. Une case vide,
une valeur non finie, un booléen transmis à l'API ou un champ hors liste
doit produire une erreur explicite. Dans les données incomplètes,
`null` signifie inconnu et n'est pas transformé en zéro.

L'atelier n'envoie pas automatiquement une saisie au calcul. Le bouton
**Calculer cette variante** déclenche la requête. Le reçu lie le résultat
aux paramètres exacts, au code et à une empreinte ; ce lien reste la
référence lorsqu'un brouillon de champ change.

## Paramètres financiers consultables, non édités ici

| Paramètre | Valeur / provenance actuelle | Effet réel et limite | Cible de correction |
|---|---|---|---|
| **Devise** | CAD déclaré pour Robert/Amira ; inconnue dans la demande incomplète. | Tous les montants de la comparaison partagent cette devise. Aucun sélecteur USD/CAD n'est proposé. | Une nouvelle devise demande conversion de toutes les données et vérification des conventions. |
| **Échéance du retrait** | Robert : 12 mois déclaré ; demande incomplète : 12 mois extraits de « douze mois ». | Doit coïncider avec l'horizon des chocs. Ne pas la confondre avec les quatre ans d'horizon du solde. | Correction future via qualification, avec réexamen de l'admissibilité des chocs. |
| **Horizon du solde** | Robert : 4 ans ; Amira : 15 ans, déclarés. | La méthode de Robert teste des chocs à 12 mois ; la méthode d'Amira décrit 2021–2026. Ces champs ne prolongent pas les calculs. | Formulation et données adaptées nécessaires si l'utilisateur veut une conclusion à cet horizon. |
| **Positions initiales Robert** | XBB 35 %, ZST 20 %, XIU 20 %, TSLA 25 %, déclarés ; même portefeuille initial dans r5/r10/r15. | Base de capital déplacé et de comparaison. Les minima successifs ne sont pas des trades à additionner. | Nouvelle correction de positions invaliderait diagnostic initial et analyses dépendantes. |
| **Positions initiales Amira** | SPY 45 %, XIU 30 %, TSLA 25 %, déclarés. | Achat-conservation ; la variante comparée fixe TSLA à 10 %. | Pas d'éditeur de positions dans ce prototype ; clarification seulement. |
| **Objectif Robert** | `minimize_reallocated_capital`, déclaré dans l'exercice. | Minimum de `C × ½ × Σ|w−w₀|` ; différent du nombre de lignes, des frais ou du risque minimal. | Un autre sens de « changer le moins possible » demande une autre formulation. |
| **Tolérance / capacité / préférences** | Pas de mesure psychométrique validée ni de score complet de convenance dans ces cas. | Ne pas déduire ces propriétés d'un budget de perte, d'un âge ou d'un niveau de capital. | Recueil distinct et explicite si le périmètre futur l'exige. |
| **Contraintes ESG / composition des ETF** | Non établies dans Amira. | Aucun score moyen imputé ; pas de recommandation ESG issue de cette comparaison. | Recherche d'une preuve admissible et de préférences clairement séparées. |

## Hypothèses d'analyse

| Hypothèse | Valeur actuelle et origine | Domaine / effet | Recalcul ou réexamen nécessaire |
|---|---|---|---|
| **Réserve** | `abstract_nominal` ; zéro rendement, hypothèse fictive explicite. | Modèle de réserve stable en CAD, pas un instrument garanti qualifié. | Une réserve réelle exige connaissance du produit, liquidité, frais, échéance et risque. |
| **Choc actions** | À 12 mois : TSLA −50 %, XBB −5 %, XIU −20 %, ZST 0 %, réserve 0 %. Scénario déclaré. | Rendements CAD hypothétiques ; aucune probabilité. | Changer un rendement invalide pertes initiales, allocation et conclusion sous ce choc. Non éditable ici. |
| **Choc obligations** | À 12 mois : TSLA −25 %, XBB −15 %, XIU −10 %, ZST −2 %, réserve 0 %. Scénario déclaré. | Même unité et échéance que le premier. | Même dépendance ; aucun report automatique d'un choc à un horizon différent. |
| **Frais, impôts, apports, emprunt** | Exclus de l'exercice ; pas de simulation implicite. | Le minimum n'est pas net de coûts réels ; le certificat suppose l'absence d'apport/emprunt. | Les ajouter modifie la formulation, pas seulement une phrase de restitution. |
| **Positions fractionnaires** | Admissibles dans le modèle d'allocation. | L'optimum peut ne pas être réalisable avec des lots entiers. | Nouvelle contrainte de lots demande un autre domaine numérique. |
| **Redistribution Amira** | `proportional_other_holdings`, déclarée ; réduction de TSLA redistribuée aux deux autres positions. | Variante initiale SPY 54 %, XIU 36 %, TSLA 10 %. | Une autre règle n'est pas prise en charge silencieusement ; mandat à requalifier. |
| **Fenêtre Amira** | `all_common_available` ; observations communes du 12 novembre 2021 au 12 novembre 2026. | Fenêtre réelle de données, pas l'horizon financier de quinze ans. | Autre fenêtre demande une politique explicite et un calcul approprié. |
| **Change et rendement historique** | Prix ajustés une fois, conversion USD→CAD, achat-conservation ; conventions vérifiées par les calculs existants. | Comparaison des deux options sous les mêmes transformations ; avant frais. | Toute correction des séries/conventions invalide les métriques et les courbes dépendantes. |
| **Date de connaissance** | 15 novembre 2026 ; captures acquises en novembre 2026. | Description rétrospective ; aucune affirmation d'information disponible à la sélection en 2021. | Une date antérieure doit déclencher les contrôles de disponibilité et peut bloquer l'analyse. |

Ces hypothèses sont lisibles dans le dossier et les preuves. Leur absence
d'éditeur dans le prototype est volontairement explicite ; un champ
consultable n'est pas présenté comme un réglage opérationnel.

## Paramètres de présentation et d'essai

| Paramètre | Provenance / valeur | Domaine | Effet | Persistance et annulation |
|---|---|---|---|---|
| **Niveau de lecture** | Choix utilisateur ; « L'essentiel » au premier accès. Ce défaut est un choix de présentation, pas une inférence de compétence. | Essentiel / options / méthode. | Ordre et profondeur seulement ; aucun calcul. | `localStorage` navigateur ; changement immédiat et réversible. Pas d'écriture dans le profil financier. |
| **Répartition / tableau Robert** | Choix utilisateur ; graphique au départ. | Deux représentations des mêmes options. | Forme visuelle uniquement. | État d'interface ; revenir au bouton précédent. |
| **Version consultée** | URL et choix explicite dans les archives. | Robert r5/r10/r15 ; un état pour les autres dossiers. | Sélection d'un résultat historique déjà produit. | Ne crée pas une restauration ni une nouvelle révision ; le bandeau nomme l'archive. |
| **Recherche documentaire** | Texte tapé, vide au départ. | Sous-chaîne des titres et passages. | Filtre les pièces visibles, sans modifier sélection scientifique ni résultat. | Effacer le filtre restitue la liste ; aucune nouvelle recherche AWS. |
| **Nouvelle demande / clarification** | Texte utilisateur, non interprété dans le prototype. | Texte libre non vide. | Brouillon uniquement ; aucun champ financier inventé. | `sessionStorage` de l'onglet ; annulable, modifiable ; pas de sauvegarde serveur annoncée. |
| **Erreur d'essai** | Case « Simuler une erreur » décochée. | Oui / non. | Erreur 503 explicitement simulée avant calcul ; permet d'essayer la reprise. | Reprise avec les mêmes paramètres et simulation désactivée ; dossier inchangé. |
| **Mouvement réduit** | Préférence système/navigateur. | `prefers-reduced-motion`. | Réduit les transitions ; aucune information financière perdue. | Réglage du navigateur/système, pas un attribut financier. |

## Sens précis des actions réversibles

**Annuler les modifications** remet le formulaire à sa référence.
**Conserver le dossier de référence** écarte l'essai affiché.
**Utiliser dans la copie du prototype** permet de lire le nouveau résultat
local avec son bandeau de portée. **Revenir à l'archive** retire cette copie
de la lecture courante. Aucun de ces gestes ne supprime une archive.

Le dernier résultat local et les brouillons ne sont pas une branche
persistante de production. Ils ne garantissent pas une restauration après
fermeture du navigateur. L'intégration devra séparer : annulation du
brouillon, abandon d'une variante, consultation historique et correction
créant une nouvelle version. Le prototype signale déjà un résultat ancien si ses champs ont été modifiés
depuis son calcul et empêche son adoption avant recalcul. Cet invariant
doit être conservé dans l’intégration.
