# Protocole de recherche discriminante

Fixé le 15 novembre 2026 avant calcul des résultats comparatifs. Aucun appel de
modèle, aucune modification du produit ou des données. Environnement local
`experiences/.venv`, versions et résultats enregistrés. Les essais préalables de
l'API HiGHS ont révélé une sortie vide par défaut : le script compare explicitement
la stratégie légère et la stratégie irréductible. Ce n'est pas un essai prospectif
aveugle de HiGHS.

1. **IIS et faisabilité.** Exemple analytique x ≥ 0,4 et x ≤ 0,3. Vérifier l'état du
   problème, les côtés des bornes, puis re-résoudre après chaque suppression avec
   une autre interface (SciPy/HiGHS, donc interface indépendante mais même famille
   de solveur). Prouver aussi par inégalités que le conflit est réel. Vérifier le
   plan de retrait Robert 30/40 % par LP et par borne inférieure analytique
   turnover ≥ augmentation de la réserve. Les hypothèses de réserve et les
   chocs sont illustratifs ; aucune garantie sur des produits réels.
2. **Covariance.** Univers fixé de huit titres : GLD, QQQ, SPY, TSLA, XIU.TO,
   XBB.TO, ZST.TO, TLT. Prix ajustés du starter, USD convertis au dernier FX
   daté au plus tard D, dates communes. Rendements simples ; pas de réestimation
   des moyennes. GMV long seulement, plafond uniforme 35 %, somme un. Comparer
   covariance empirique et Ledoit–Wolf vers identité scalaire (estimateur de
   scikit-learn, distinct de la cible corrélation constante de Honey 2004).
   Contrôle 1/N sous les mêmes bornes. Fenêtres de 252 rendements, blocs suivants
   de 63 rendements, entraînement strictement antérieur. Volatilité agrégée hors
   échantillon à convention √252 et poids/rotation aux frontières ; aucune
   inférence de surperformance. Sensibilité sur la dernière fenêtre admissible :
   100 bootstrap en blocs contigus de cinq observations, même tirages entre
   méthodes ; variation L1 des poids. Sensibilité ne signifie pas justesse.
3. **Référence mathématique indépendante.** GMV sans contraintes contre
   Σ⁻¹1/(1ᵀΣ⁻¹1) sur une matrice positive définie fixée, plus contrôles numériques
   des contraintes. ES empirique sur masses discrètes contre formulation LP
   auxiliaire : cela teste la fraction de masse au quantile.
4. **Sharpe sous modèle nul.** 100 000 simulations de 20 estimations normales
   indépendantes N(0,1/5), puis essais équicorrélés ρ=0,8, graine fixe. Comparer
   moyenne du maximum et son quantile 95 % ; contrôle analytique
   Φ⁻¹(0,95^(1/20))/√5. Cette approximation suppose volatilité connue et
   normalité ; ce n'est ni le DSR complet ni une borne de tous les backtests.

Critères : écarts de référence ≤ 1e-6, contraintes LP/QP ≤ 1e-7 en fraction
de capital sauf tolérance documentée, états/erreurs conservés. Un estimateur est
un candidat, pas un choix de production. Aucun classement n'est fixé après
observation des résultats et aucune multiplication d'essais pour gagner un
classement.
