# Registre des données

L'énoncé exige, pour chaque source : pertinence, origine, date, traitements, limites, conditions d'accès et de réutilisation. Ajouter une ligne par source avant de l'utiliser.

| Dossier / fichier | Source | Extraction | Traitements | Limites | Conditions |
| --- | --- | --- | --- | --- | --- |
| `raw/alphaforge_starter/` | Jeu de départ PolyFinances (Yahoo Finance via yfinance, Banque du Canada Valet, FRED) | 2026-11-13, période 2021-11-12 → 2026-11-12 | Aucun dans ce projet (copie à l'identique) | Voir `raw/alphaforge_starter/README.md` et `sources_metadata.csv` : biais du survivant, macro datée au mois de référence, `adj_close` recalculé à chaque extraction | Yahoo, Banque du Canada, FRED (liens dans `sources_metadata.csv`) ; usage libre dans le datathon |

## Pièges connus du jeu de départ

- Prix en devise de cotation : `.TO` en CAD, le reste en USD → `data.convert_currency`.
- Pas d'alignement de calendrier : TSX, marchés américains et cryptos (7 j/7) diffèrent. Documenter la méthode d'alignement retenue.
- `adj_close` pour les rendements ; les splits sont déjà appliqués.
- CNQ.TO : « split » de 1,021 le 2022-08-22, probablement une distribution spéciale, à vérifier.
- Macro mensuelle (IPC, chômage) datée au mois de référence : décaler à la date de publication avant toute simulation.
- Aucune donnée ESG, fondamentale ni nouvelle : à ajouter et documenter ici si nécessaire.
