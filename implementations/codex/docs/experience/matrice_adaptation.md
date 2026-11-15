# Matrice d'adaptation — changer la lecture, conserver la décision

**Prototype v0.1, proposé pour validation.** Les choix « L'essentiel »,
« Les options » et « La méthode » sont facultatifs, disponibles dans le
même dossier et réversibles. Ils ne représentent pas des catégories de
personnes et ne sont pas déduits d'informations financières.

## Deux espaces de paramètres

| Espace | Exemples | Ce qu'il peut changer | Ce qu'il ne doit pas changer silencieusement |
|---|---|---|---|
| **Profil financier / hypothèses** | Retrait, capital, positions, horizon, plafond TSLA, budget de perte, politique de réserve, devise, préférences. | Admissibilité d'une méthode, contraintes, résultats, conclusions et dépendances. | Une préférence ne devient pas une contrainte ; une inconnue ne devient pas une moyenne ; une correction ne remplace pas une archive. |
| **Présentation** | Profondeur de lecture, répartition/tableau, recherche de passage ; langue ou vocabulaire possibles plus tard. | Ordre et densité d'information, explications et forme de représentation. | Faits, chiffres, unités, période, hypothèses, limites décisives, statut de preuve ou niveau de garantie. |

Un changement de présentation ne déclenche aucun calcul ni appel AWS dans
le prototype. Un changement financier de Robert déclenche, sur demande,
le moteur réel sur une copie ; les autres changements libres restent des
brouillons. L'horizon de quinze ans d'Amira ne transforme pas son analyse
descriptive de cinq ans en projection : un champ de profil peut demeurer
hors du domaine d'effet d'une méthode.

## Noyau invariant, pour tous les niveaux

- dossier, version et distinction archive/copie locale ;
- montants, devise, périodes et liaisons aux valeurs calculées ;
- conditions sans lesquelles la conclusion change ;
- existence d'une référence simple aussi bonne lorsque démontrée ;
- inconnus et contradictions déterminants ;
- distinction scénario/histoire et contrôle/validation externe ;
- action pour accéder à la preuve, au profil et aux limites ;
- absence de nouvelle revue des agents pour une exploration locale.

La version courte conserve les réserves qui changent le sens de la réponse.
La version détaillée ajoute des éléments utiles à la contestation ; elle
n'ajoute pas de certitude.

## Même dossier Robert r5, trois lectures

| Dimension | L'essentiel | Les options | La méthode |
|---|---|---|---|
| Première question | Que signifie 30 000 CAD ? | Quels plans atteignent ce minimum et comment diffèrent-ils ? | Comment ce minimum a-t-il été établi ? |
| Ordre | Réponse → réserve abstraite/chocs → référence simple → deux raisons → prochaine action. | Même noyau, puis poids et pertes sous les deux chocs ; comparaison avant exploration. | Même noyau et comparaisons, puis formulation, domaine admis, liaisons, contrôles, sources et limites. |
| Vocabulaire | « Capital à déplacer », « perte dans ce choc », « plusieurs allocations ». | « Poids initial », « allocation admissible », « montant à réallouer » expliqués par les colonnes. | Identifiant de méthode, objectif, tolérances et références accessibles ; le jargon reste relié à une question concrète. |
| Représentation | Nombre lié à une preuve ; raison en deux blocs ; invitation à comparer. | Répartition empilée ou tableau équivalent ; tableau des pertes et du capital déplacé. | Même comparaison ; fiche méthode et contrôles ; artefact exact à la demande. |
| Détails disponibles | Preuve, profil/origine, référence simple, limites, agents. | Les mêmes, plus lecture précise des poids et compromis. | Les mêmes, plus traces et mécanismes de contrôle. |
| Limites visibles | Réserve abstraite, deux chocs sans probabilités, frais/impôts exclus, absence de supériorité agentique. | Exactement les mêmes ; rappel que minimum de capital déplacé ≠ minimum de risque. | Exactement les mêmes ; distinction garantie mathématique conditionnelle, résultat d'oracle et validité externe. |
| Ce qui reste calculé | Minimum 30 000 CAD ; mêmes allocations/poids/pertes. | Identique. | Identique. |

Pour r10 et r15, les résultats deviennent respectivement 40 000 et
74 400 CAD parce que le **profil financier** a changé. La règle simple
attestée pour r5 n'est pas extrapolée à ces états. Le changement de niveau
de lecture ne change aucun de ces résultats.

## Autres états, même règle d'adaptation

| Dossier / état | L'essentiel | Les options | La méthode | Invariant décisif |
|---|---|---|---|---|
| **Amira** | Comparaison passée, rendements cumulés et trajectoires ; limite temporelle explicite. | Ajoute valeurs finales, baisse maximale, même période et convention de redistribution. | Ajoute méthode rétrospective, prix ajustés/change, dates de connaissance et contrôles. | Le résultat de 2021–2026 n'est pas une prévision sur quinze ans ni un choix réalisé avec connaissance de 2021. |
| **Demande incomplète** | Douze mois compris ; capital/retrait/positions manquants ; question utile. | Ne fabrique aucune comparaison faute de données. | Accès à la qualification, questions et sources sans prétendre qu'une méthode a produit des nombres. | Aucune allocation ; toute réponse nouvelle reste un brouillon dans le prototype. |
| **Retrait impossible** | 120 000 CAD demandés pour 100 000 disponibles, écart de 20 000. | La comparaison reste le conflit établi, pas des portefeuilles inventés. | Certificat et hypothèses ; distinction impossibilité du modèle et impossibilité de toute solution financière. | Aucune relaxation automatique, aucun prêt/apport supposé. |
| **Copie calculée de Robert** | Résultat et limite ; bandeau « calcul local, sans nouvelle revue des agents ». | Poids/pertes du calcul local quand admissibles. | Reçu numérique et contrôles disponibles ; absence des cinq contrôles archivés signalée. | La copie n'a pas acquis les preuves documentaires ou reçus AWS de l'état d'origine comme nouvelle validation. |
| **Erreur** | Ce qui n'a pas abouti, paramètres conservés, reprendre/annuler. | Même information. | Détail de reçu ou d'erreur, lorsqu'il existe. | Pas de conclusion à partir d'une panne ; erreur volontaire clairement simulée. |

## Préférences proposées et état réel

| Préférence | Prototype | Cible après validation |
|---|---|---|
| Profondeur | Trois boutons ; valeur conservée par le navigateur. | Même contrôle, préférence explicite distincte du dossier financier. |
| Graphique / tableau | Robert : mêmes options et poids. Amira : graphique, tableau des métriques et données exactes/CSV. | Maintenir la sélection et les unités lors du changement. |
| Familiarité avec la finance | Aucun score ou diagnostic de compétence. Les titres expliquent les concepts utiles. | Choix facultatif « expliquer les termes » si validé, sans effet sur le profil de risque. |
| Langue | Français uniquement. | Traduction qualifiée, mêmes nombres et conditions ; ne pas annoncer aujourd'hui une option absente. |
| Accessibilité | Contrôles natifs, focus visible, zoom du navigateur, styles responsifs et réduction des mouvements. | Compléter selon les besoins observés ; pas de profil médical ou de handicap inféré. |
| Recherche | Filtre des titres et passages documentaires. | Recherche dans le dossier si son volume le justifie ; conserver version et contexte du résultat. |

## Vérifications informatives

Sur un même état, comparer les nombres, unités, dates et limites après les
trois changements de niveau. Contrôler qu'aucune requête de calcul ou
d'inférence n'est envoyée. Vérifier ensuite séparément qu'un retrait
30→40 kCAD modifie le résultat par un vrai calcul, tout en conservant
l'archive.

Pour l'essai humain : demander la conclusion et sa limite, la raison d'un
chiffre, la distinction entre variante et correction, puis le moyen de
revenir. Mesurer erreurs observées et réussite, sans convertir un petit
échantillon en preuve générale d'efficacité.
