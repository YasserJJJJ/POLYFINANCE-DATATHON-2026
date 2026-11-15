# Expériences discriminantes et audit du notebook

15 novembre 2026. Les expériences sont hors produit, sous `experiences/`.
Le script principal n'importe pas le moteur AlphaForge ; il relit les deux CSV
figés. Aucun appel LLM n'est effectué. La métadonnée de la session de développement
indique `amazon-bedrock-runtime` / `global.openai.gpt-6-astra` ; cela constate
la route déclarée, pas une preuve indépendante de facturation.

## Protocole, environnement et reproduction

Lire [PROTOCOLE.md](experiences/PROTOCOLE.md), puis exécuter avec l'environnement
isolé ou un environnement neuf créé à partir de
[requirements.lock](experiences/requirements.lock) :

```sh
python docs/recherche/finance/experiences/run_experiments.py
python docs/recherche/finance/experiences/inspect_notebook_inputs.py
```

Python 3.15 ; NumPy 2.5.4, SciPy 1.18.1, highspy 1.16.0, scikit-learn 1.9.1.
Graine 20261115. Les résultats complets avec empreintes sont dans
[results.json](experiences/results.json) et
[notebook_inputs.json](experiences/notebook_inputs.json). La `.venv` du produit
n'a pas été modifiée. Les bibliothèques de recherche ne deviennent pas des
dépendances de production.

## Résultats et interprétation

| Question | Résultat observé | Ce que cela établit / ne prouve pas |
|---|---|---|
| GMV soluble par formule | Poids 0,60809820447 ; 0,24257969952 ; 0,14932209601. Écart maximal solveur/formule 4,44×10⁻¹⁶ | Contrôle numérique indépendant de la formule sur cette matrice ; pas validation universelle de SLSQP |
| ES empirique avec frontière fractionnaire | Pire moitié de pertes −1 %, 2 %, 10 % : 7,333333333 %, identique au LP | Il faut gérer la masse au quantile ; les trois observations ne calibrent pas le risque futur |
| IIS x≥0,4, x≤0,3 | Mode léger : `kOk`, `valid=True`, lignes vides, statut 0 ; stratégie 4 : lignes [0,1], statut 3 | Une sortie API « OK » n'est pas un diagnostic. Chaque suppression est faisable ; preuve indépendante 0,4≤x≤0,3 impossible |
| Robert réserve 30 / 40 % | Rotation minimale 30 / 40 %, maximum de violation 0. Autres optima que C/D | La borne analytique confirme la rotation ; le seul objectif de rotation sous-détermine les poids |
| Maximum de 20 Sharpe N(0,1/5) | Moyenne 0,836097 ; quantile 95 % 1,251304 ; formule exacte 1,251845 | Le chiffre 0,85 n'est pas un seuil universel de signification |
| Même approximation, corrélation 0,8 | Moyenne maximale 0,375295 ; quantile 95 % 1,058106 | La dépendance entre essais change matériellement l'interprétation |

Le contrôle IIS utilise SciPy et highspy : deux interfaces, **pas deux moteurs
indépendants**. La preuve par inégalités et la borne de rotation ne dépendent
pas de HiGHS. Ces exemples ne testent pas les IIS de tous les MILP/QP/coniques,
les problèmes mal conditionnés ni les limites de temps.

### Contraction de covariance et stabilité

Univers fixe : GLD, QQQ, SPY, TLT, TSLA, XBB.TO, XIU.TO, ZST.TO. Prix ajustés
convertis en CAD avant rendements ; intersection de dates : 1 228 cours,
1 227 rendements. Quinze blocs de validation de 63 rendements, soit 945 valeurs,
du 25 novembre 2022 au 30 septembre 2026. Chaque bloc utilise les 252 rendements
strictement antérieurs ; les 30 derniers rendements ne forment pas un bloc complet
et sont exclus selon le protocole. Premier entraînement : cours du 12 novembre
2021 au 23 novembre 2022. Dernier : 18 juin 2025 au 29 juin 2026.

| Mesure | 1/N | GMV empirique | GMV contraction identité |
|---|---:|---:|---:|
| Volatilité OOS, %, convention √252 | 12,476683 | 4,475547 | 4,486743 |
| Demi-L1 moyen des changements de cibles entre blocs | 0 | 0,045377 | 0,044066 |
| L1 moyen de sensibilité bootstrap, dernière fenêtre | — | 0,062186 | 0,055142 |
| Quantile 95 % L1 de sensibilité | — | 0,120520 | 0,107965 |

Contraintes communes : long seulement, somme 1, plafond de 35 % par actif.
La covariance empirique a un nombre de condition entre 8 047 et 34 773, la
contractée entre 84 et 457. Les intensités de contraction sont entre 0,01281
et 0,06558. Le conditionnement s'améliore fortement, la sensibilité des poids
plus modestement, et la volatilité OOS de la contractée est légèrement plus
élevée. **Conditionnement, stabilité, risque réalisé et pertinence pour un
objectif sont quatre résultats différents.**

L'expérience utilise l'identité scalaire de scikit-learn et non la corrélation
constante de la note *Honey*. Le contrôle GMV analytique porte sur une autre
matrice prédéfinie, pas sur les données servant à départager les estimateurs.
Les poids restent constants à chaque journée du bloc : cela implique un
rééquilibrage quotidien sans frais. Le demi-L1 des **cibles** aux frontières
n'est donc ni le turnover total réalisé ni une estimation de coûts.

Le starter a été choisi en 2026, contient des actifs survivants et des prix
ajustés a posteriori. L'expérience ne supprime pas ce biais et ne compare pas
de performance financière significative. Les résultats de faible volatilité
s'expliquent notamment par les poids obligataires ; ils ne prouvent pas
l'atteinte d'un objectif de croissance. Les US/CAD/FX du même jour ne sont pas
parfaitement synchrones. Aucun modèle n'est sélectionné pour la production
sur ces résultats.

## Audit du notebook N01 et des pistes de l'atlas 00B

Source : `revision_2026-11-15/extractions/Introduction-Datathon.ipynb`,
35 cellules lues, numérotation **à partir de zéro** ci-dessous. Aucune cellule
de téléchargement yfinance, d'inférence, de service ou d'installation n'a été
exécutée. Le notebook est une initiation ; ses simplifications ne sont pas
des exigences scientifiques du concours.

| Cellules | Apport à conserver | Reprise nécessaire pour une analyse financière |
|---|---|---|
| 2, 9, 34 | Question, sélection libre des données, simulation, provenance et absence d'information future | Le notebook ne fixe ni univers obligatoire ni allocation par persona ; le contrat doit garder cette liberté |
| 10 | Acquisition de prix avec `auto_adjust=True`, sauvegarde | Dater et versionner la réponse ; ne pas additionner encore les distributions ; préciser dates/identités/devises |
| 12 | Valet, USD→CAD, réponse HTTP contrôlée | Le FX téléchargé n'est ensuite pas appliqué aux cours ; ajouter convention as-of et disponibilité intrajournalière, sans taux d'exécution prétendu |
| 14 | Lecture CSV FRED sans clé, gestion de `.` | DGS10 est un rendement obligataire américain à dix ans, pas le rendement quotidien d'un placement sans risque CAD ; le CSV n'est pas un millésime historique |
| 16 | Extraction structurée SEC avec `filed` et `end` | Filtrer `filed≤date_analyse`, choisir contexte/unité/durée et version ; `drop_duplicates("end")` dépend de l'ordre reçu |
| 19 | Rendements simples, volatilité, drawdown par actif | `(1+mean(r))^p−1` ne donne pas le CAGR réalisé ; avec +50 % et −50 %, il donne 0 sur deux périodes contre −25 % composé. Le ratio rendement/volatilité n'est pas un Sharpe en excès du taux adéquat |
| 19–20 | Distinguer calendrier crypto/action | Le suffixe d'un ticker ne constitue pas un contrat de calendrier. Les paires de rendements natifs n'ont pas forcément les mêmes intervalles ; vérifier covariance PSD et valorisation commune |
| 25 | Explication conditionnée sur nombres calculés | Un mot « prudent » n'est pas un problème qualifié ; la sélection d'actifs ne traite pas retraits, contraintes ni solutions multiples |
| 30 | Schéma JSON et validation Pydantic | La validité structurelle n'assure ni vérité des chiffres extraits, ni causalité du sentiment, ni identité de l'entreprise ; conserver passages et tests d'entailment |
| 33 | Outils numériques plutôt que chiffres inventés | Étendre métadonnées/erreurs/contrats ; `correlation` n'a pas le même contrôle de ticker inconnu que `indicateurs_actif` ; deux outils ne composent pas seuls l'analyse complète |

Les 36 PDF de l'atlas sont principalement ressources d'accès, atelier, outils,
architecture et traçabilité. Leur nombre n'atteste pas de 36 études financières
analysées. Leurs pistes utiles ne doivent ni être ignorées par réflexe de
simplification ni toutes être forcées dans le produit. La recherche récursive
qualifie une incertitude qui pourrait changer la décision, cherche puis compare
les méthodes et revient au problème ; elle ne consiste pas à empiler des citations.

## Contrôles sur les réponses publiques effectivement obtenues

- **Valet U366** : 1 461 observations, 4 janvier 2021–13 novembre 2026 ;
  aucune date de fin de semaine, clés uniques, FX strictement positifs.
  La réponse décrit l'unité CAD par USD. Dernière observation 1,4257 CAD/USD.
  Ces contrôles ne reconstituent pas les publications historiques.
- **FRED U367** : la collecte Python commune avait expiré ; curl système
  standard a obtenu le CSV, sans désactiver TLS. 16 923 lignes, 16 201 non
  manquantes ; dernière DGS10 datée du 12 novembre 2026 à 5,10 %. Colonnes
  `observation_date,DGS10`, sans date de publication ni de révision.
- **SEC U369** : Apple, CIK 320193. Le filtre annuel du notebook produit
  24 lignes pour 10 fins d'exercice. Huit fins d'exercice apparaissent plusieurs
  fois avec plusieurs dates `filed`. Dans ces groupes, les valeurs de revenus
  sont identiques : c'est la répétition des dépôts/comparatifs qui est prouvée,
  pas une révision de montant. Un filtrage à date reste nécessaire.

Les pages Valet U273/U363 sont des coquilles dans l'extraction textuelle ;
la réponse JSON observée fournit ici une preuve de schéma que leur HTTP 200
ne donnait pas. Les réponses SEC 403 sur la documentation ne prouvent pas que
l'endpoint public U369 soit inaccessible : son JSON s'est effectivement chargé.

## Limites de ce cycle

Pas de reproduction intégrale des papiers, de comparaison de rendement après
frais/fiscalité, de calibration prospective des objectifs, de collecte complète
de vintages, d'ESG ou de compositions d'ETF. Les essais sont conçus pour départager
des décisions de conception : interprétation d'IIS, indépendance d'une formule,
contraction et stabilité, signification d'un maximum de Sharpe, audit de dates.
