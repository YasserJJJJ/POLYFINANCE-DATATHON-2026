# Fiche des données

| Donnée | Source | Période | Traitement | Limites |
|---|---|---|---|---|
| Prix quotidiens, 31 actifs | Yahoo Finance via yfinance (jeu de départ, extrait le 2026-11-13) | 2021-11-12 → 2026-11-12 | `adj_close` (dividendes + fractionnements). Titres USD convertis en CAD au taux BdC du jour ou au dernier taux connu | Pas certifié par les bourses ; `adj_close` change si on retélécharge ; biais du survivant (univers choisi en 2026) |
| USD/CAD | Banque du Canada, API Valet | Même fenêtre | Report du dernier taux les jours sans cotation (fériés canadiens, fins de semaine pour les cryptos) | Pas de taux les jours fériés canadiens |
| Secteurs | `assets_universe.csv` (organisateurs) | Statique | Lus tels quels pour les exclusions | Étiquettes simplifiées, pas une classification officielle ; aucune donnée de controverse ESG |
| Taux et inflation | Banque du Canada, FRED | Même fenêtre | Pas encore utilisés | Données mensuelles datées au mois de référence, pas à la publication |

## Licences et attribution

Les données viennent du jeu de départ fourni par les organisateurs (`data/raw/alphaforge_starter/`), avec ses
conditions dans `sources_metadata.csv`. L'autorisation du datathon vaut pour l'événement, pas pour une
redistribution générale : ce dépôt n'ajoute aucune donnée et ne modifie pas `data/raw/`.

| Donnée | Attribution | Conditions |
|---|---|---|
| Prix et opérations sur titres | Yahoo Finance, via la bibliothèque libre yfinance | Conditions de Yahoo : https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html (consultées le 2026-11-13). Données non certifiées par les bourses |
| USD/CAD, taux et IPC canadiens | Banque du Canada, API Valet (série FXUSDCAD, etc.) | https://www.bankofcanada.ca/terms/ |
| Taux et indicateurs américains | FRED, Federal Reserve Bank of St. Louis (séries d'agences gouvernementales américaines) | https://fred.stlouisfed.org/legal/ (pas encore utilisées par le code) |
| Univers d'actifs et secteurs | Organisateurs du datathon | Libre d'utilisation dans le cadre du datathon |

À l'écran, le pied de page cite Yahoo Finance et la Banque du Canada, et chaque fait renvoie à sa source.

## Méthodes de calcul

- **Pire chute** : baisse maximale d'un sommet au creux suivant, en CAD.
- **Temps de récupération** : du creux au premier jour où le sommet précédent est retrouvé. S'il ne l'est pas
  au 2026-11-12, on utilise le temps écoulé depuis le creux comme minimum.
- **Volatilité annualisée** : écart-type des rendements log quotidiens × √252 (actions, FNB) ou × √365 (cryptos).
- **Rendement annualisé** : taux de croissance annuel composé sur la fenêtre. Descriptif, jamais prédictif.
- **Pire période de 12 mois** : rendements sur 52 semaines glissantes (prix du vendredi).
- **Corrélation** : rendements hebdomadaires (vendredi) pour aligner les calendriers TSX, US et crypto.

## Contrôles qualité (avant tout calcul)

Présence, doublons de date, prix positifs, couverture de la fenêtre, trous anormaux, variations journalières
de plus de 40 %, devise. Un échec rend le verdict « impossible de conclure ».


## Deux moteurs, deux autorités (K4)

| Usage | Moteur | Série et annualisation | Exemple vérifié TSLA |
|---|---|---|---|
| Titre seul, récupération, corrélations | C, `calculs.py` | Calendrier propre du titre ; rendements log, √252 pour titres/FNB, √365 pour cryptos ; corrélations hebdomadaires | Pire chute −70,9 %, volatilité 58,8 %/an |
| Portefeuille avant et après | B, `moteurs/historique/analytics.py` | 1 228 séances communes non crypto ; rendements simples, écart-type échantillonnal × √(intervalles/années), années = jours/365,2425 | Titre isolé sur cette grille : pire chute −69,805333 %, volatilité 58,608591 %/an |

Une différence entre ces valeurs n’est pas une erreur d’un des moteurs. Les deux bras d’une comparaison K3 viennent toujours du même appel B, sur la même fenêtre. Aucun écart C/B n’entre dans le verdict ou le texte de comparaison. Les champs publics K3 sont en points de pourcentage ; les poids restent des fractions. Les preuves initiales [B](fusion/preuves/B-mesures.json) et [C](fusion/preuves/C-mesures.json) décrivent fréquence, fenêtre, unités et change.

B valorise les quantités achetées au départ jusqu’à la fin, sans rééquilibrage. Son change est daté du jour ou antérieur, avec âge maximal de sept jours. La grille est l’intersection fixe des dates des actifs non crypto du snapshot, sans imputation de prix. Le cryptoactif y est échantillonné : les mouvements entre séances, notamment de fin de semaine, ne sont pas observés dans le drawdown K3. Le change quotidien indicatif n’est pas un cours exécutable synchronisé.

L’ajout demandé suit `blend` de A : les anciennes lignes sont réduites proportionnellement, puis la part demandée est ajoutée au titre. Ce n’est pas une cible de poids. Un montant dépassant l’épargne produit une raison et aucune allocation. Sans poids déclarés, une liste de titres produit un fait HYPOTHESE d’équipondération.

La fenêtre de cinq ans inclut 2022 mais pas toutes les crises. L’univers et les ajustements de prix connus en 2026 empêchent de présenter cette comparaison comme une stratégie réalisable avec l’information de l’époque. Ni probabilité de perte future, ni conseil, ni score ESG n’en sont déduits. Les exclusions utilisent les secteurs simples, sans transparisation des FNB.

Les limites sont conservées dans `comparaison.limites`, reprises dans `texte.limites` et accessibles dans le bloc de comparaison. Le [registre généré](sources.md) nomme les données, méthodes et hypothèses de chaque famille.
