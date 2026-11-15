# Contrats de méthodes — lecture par les agents

Version du 15 novembre 2026, moteur `decision-finance-v2`.
Ce document technique ne contient ni résultat attendu de démonstration ni
allocation de persona. Une implémentation enregistrée, une source théorique
et une exécution vérifiée constituent trois preuves différentes.

## Réallocation sous scénarios

L'outil `reserve_allocation` résout `reserve-turnover-lp-v1` :
minimiser la demi-somme des variations absolues des poids, sous budget égal
à un, positions non négatives, plafonds déclarés à l'instant initial,
réserve abstraite au moins égale au retrait divisé par le capital, et pertes
terminales de chaque scénario ne dépassant pas le budget déclaré.

Le capital déplacé est le capital initial multiplié par la demi-L1.
Achats et ventes sont égaux ; leur somme ne mesure pas le capital déplacé.
Les chocs doivent être explicitement fournis en CAD et à l'échéance du retrait.
La réserve abstraite a un rendement nominal nul ; elle ne constitue pas un
instrument réel, une preuve contractuelle ou une garantie future.
Coûts, fiscalité et inflation ne sont pas modélisés.
L'horizon ultérieur du solde n'est pas extrapolé.

SciPy/HiGHS résout le programme linéaire. Les contrôles exigent les résidus
primal-dual, les contraintes recalculées et la finitude des résultats.
La borne indépendante achats=ventes=demi-L1 peut être non serrée.
Les plages de la face optimale et les témoins exposent l'absence de départage :
un optimum de capital déplacé n'est pas un optimum de risque personnel.
Une infaisabilité n'autorise aucune relaxation implicite.

Si le retrait dépasse le capital et doit être préfinancé en réserve abstraite,
le certificat `reserve-budget-contradiction-v1` utilise seulement les
contraintes `retrait ≤ réserve ≤ capital`. Il suffit à établir
l'infaisabilité du modèle déclaré, même si d'autres questions restent ouvertes.
Ce n'est pas un IIS général ni un choix de réparation.

Fondement théorique : Boyd et Vandenberghe, *Convex Optimization* (2004),
programmes linéaires, reformulation des valeurs absolues et dualité.
Les preuves de calcul sont les contrôles de chaque exécution et les tests
indépendants du projet, pas la seule présence de cette référence.

## Comparaison historique en CAD

L'outil `historical_comparison` utilise `retrospective-comparison-v2`.
Une `historical_policy` doit déclarer explicitement
`redistribution=proportional_other_holdings` et
`window.kind=all_common_available`, sans bornes de dates.
L'absence de politique demande une clarification.
Une fenêtre fixée ou une autre redistribution n'est pas implémentée :
la demande reçoit une limite explicite, sans lui substituer la politique admise.

Le nouveau poids de l'actif cible est déclaré ; les autres poids sont
redimensionnés proportionnellement. Les deux allocations initiales sont
comparées sur la même grille et avec les mêmes conventions d'achat-conservation.
La valeur est `capital × somme(poids initial × indice de rendement total CAD)`.
`adj_close` est utilisé une fois ; aucun ajout de dividende ou split.
Les prix USD sont multipliés par un taux CAD/USD contemporain ou antérieur.
Un taux trop ancien est refusé. Les conventions détaillées sont dans
`docs/methodology.md`.

Les fichiers, leurs hashes, leurs dates d'acquisition et la date de connaissance
sont confrontés entre l'inspection Agent1 et le calcul Agent2.
Une capture ultérieure ne permet pas de reconstruire un ancien millésime.
Les prix ajustés et l'univers sélectionné restent rétrospectifs.
Le CAGR, le drawdown et la volatilité décrivent cette grille ; aucune
probabilité future, allocation personnelle ou projection à l'horizon du client
n'est déduite. Les expositions sous-jacentes des FNB et l'ESG ne sont pas établis.

Les contrôles d'exécution sont obligatoires. Un échec matériel interdit les
claims et options ; un contrôle partiel ne devient pas « suffisant » par
accord des agents. Les désaccords documentaires restent identifiables et
les conflits bloquants de méthode ou de données empêchent la conclusion.
