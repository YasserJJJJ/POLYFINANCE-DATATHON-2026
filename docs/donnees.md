# Fiche des données

| Donnée | Source | Période | Traitement | Limites |
|---|---|---|---|---|
| Prix quotidiens, 31 actifs | Yahoo Finance via yfinance (jeu de départ, extrait le 2026-11-13) | 2021-11-12 → 2026-11-12 | `adj_close` (dividendes + fractionnements). Titres USD convertis en CAD au taux BdC du jour ou au dernier taux connu | Pas certifié par les bourses ; `adj_close` change si on retélécharge ; biais du survivant (univers choisi en 2026) |
| USD/CAD | Banque du Canada, API Valet | Même fenêtre | Report du dernier taux les jours sans cotation (fériés canadiens, fins de semaine pour les cryptos) | Pas de taux les jours fériés canadiens |
| Secteurs | `assets_universe.csv` (organisateurs) | Statique | Lus tels quels pour les exclusions | Étiquettes simplifiées, pas une classification officielle ; aucune donnée de controverse ESG |
| Taux et inflation | Banque du Canada, FRED | Même fenêtre | Pas encore utilisés | Données mensuelles datées au mois de référence, pas à la publication |

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
