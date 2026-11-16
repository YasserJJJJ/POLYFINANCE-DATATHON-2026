# R02 — Composition des FNB et preuves ESG : disponibilité et conditions

Recherche déléguée (sous-agent researcher), 2026-11-14. Niveaux : [lu] page lue ; [extrait] résultat de recherche seulement ; [PDF illisible] téléchargé, texte non extrait. Aucun fichier de composition téléchargé.

## Composition des FNB

| FNB | Source | Fichier | Conditions |
|---|---|---|---|
| SPY | [SSGA, page produit](https://www.ssga.com/us/en/intermediary/etfs/spdr-sp-500-etf-trust-spy) [lu] | XLSX quotidien « Download All Holdings », motif `/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx` ; page datée du 12 nov. 2026 | conditions du site **non lues** |
| QQQ | [Invesco](https://www.invesco.com/qqq-etf/en/about.html) [lu] | tableau dynamique, pas de lien de fichier vérifié | non vérifié |
| ESGV | [Vanguard](https://investor.vanguard.com/investment-products/etfs/profile/esgv) [contenu vide] ; fiche [F4393.pdf](https://fund-docs.vanguard.com/F4393.pdf) [PDF illisible] | non vérifié | non vérifié |
| XIU.TO | [iShares Canada](https://www.blackrock.com/ca/investors/en/products/239832/ishares-sptsx-60-index-etf) [lu, tronqué] | CSV probable, non confirmé | non vérifié |
| autres | — | non vérifié | — |

Piste primaire à vérifier : formulaires N-PORT (SEC) pour les FNB américains. Sites tiers (Trackinsight, TipRanks) : poids divergents, à ne pas utiliser comme source.

## ESGV

- Indice : FTSE US All Cap Choice Index — [dépôt SEC Vanguard](https://www.sec.gov/Archives/edgar/data/52848/000168386324001465/f37925d0.htm) [extrait].
- Exclusions par activité (selon cet extrait) : divertissement pour adultes, alcool, tabac, armes, combustibles fossiles, jeux d'argent, nucléaire ; exclusions de conduite liées aux principes du Pacte mondial de l'ONU et critère de diversité. Seuils **non vérifiés**.
- Règles primaires à extraire : [FTSE Global Choice Index Series Ground Rules](https://www.lseg.com/content/dam/ftse-russell/en_us/documents/ground-rules/ftse-global-choice-index-series-ground-rules.pdf) [PDF illisible par l'outil].
- Présence : TSLA et JPM présents au 31/12/2025 selon la fiche Vanguard [extrait] ; XOM absent **non vérifié** par source primaire.

## Controverses — sources

| Source | Contenu | Conditions |
|---|---|---|
| [NBIM, exclusion et observation](https://www.nbim.no/en/responsible-investment/exclusion-of-companies/) [lu] | société, catégorie, critère, décision, date ; mise à jour 11 août 2026 ; depuis nov. 2025, plus de nouvelles exclusions (lignes directrices provisoires) | licence non affichée |
| [SEC EDGAR](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data) [lu] | 10-K « Legal Proceedings » | accès libre ; automatisé ≤ 10 requêtes/s avec User-Agent |
| [EPA ECHO](https://echo.epa.gov/tools/data-downloads) [lu] | conformité environnementale par installation | licence non indiquée ; lien installation → société non traité |
| [MSCI ESG Ratings, outil public](https://www.msci.com/our-solutions/esg-investing/esg-ratings-climate-search-tool) [lu] | recherche de notes | conditions non lues ; données complètes réservées aux clients |
| Sustainalytics (via Yahoo) | note de risque | usage interne seulement sans accord écrit selon un livre blanc [extrait] → **à traiter comme non réutilisable** |

## Recommandation retenue

- Exposition par transparence : instantané daté et figé de SPY (XLSX SSGA) ; autres FNB seulement après lecture des conditions ; sinon « non vérifié ». Données conservées localement, non redistribuées.
- ESG (Mateo) : uniquement des faits datés et attribués (liste NBIM, 10-K, méthodologie FTSE) ; **aucune note produite** ; ESGV traité comme filtre indirect, jamais comme preuve sur une société.
- Trois états jamais fusionnés : `defavorable` (source, URL, date, extrait) ; `aucune_trouvee` (sources consultées + date ; afficher « aucune trouvée dans [sources] au [date] ») ; `non_evalue` (état par défaut).

## Reste à vérifier

Conditions SSGA, Invesco, Vanguard, BlackRock ; texte des règles FTSE ; compositions ESGV, XIU, QQQ ; licence NBIM ; SEDAR+, OSHA.
