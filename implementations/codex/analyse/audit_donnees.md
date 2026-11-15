# Audit indépendant des données de départ AlphaForge

Date : 14 novembre 2026. Audit local en lecture seule des neuf fichiers fournis, sans retéléchargement, sans exécution de `build_dataset.py`, sans changement des originaux. Le README bilingue, les métadonnées et le générateur ont été lus ; toutes les lignes des six CSV ont été parcourues. Les chiffres ci-dessous sont des mesures sur les fichiers, pas une certification de l'exactitude des fournisseurs.

## 1. Résultat essentiel

Le pack est un **socle de simulation exploitable mais insuffisant pour justifier seul des conseils personnalisés, une conformité ESG ou une supériorité financière**. Ses formats sont propres ; ses risques majeurs sont sémantiques et temporels. Le message « No warnings » n'est pas une validation financière générale.

Le problème le plus immédiatement exploitable pour se distinguer est la chaîne de preuve : requête et contraintes explicites → données disponibles à la date de décision → calcul reproductible → résultat expliqué avec ses limites. Un modèle sophistiqué placé au-dessus d'une jointure temporelle incorrecte produirait une démonstration trompeuse.

## 2. Inventaire mesuré

| Fichier | Lignes de données | Colonnes | Rôle |
|---|---:|---:|---|
| assets_universe.csv | 31 | 7 | Identité et classification simplifiée des actifs |
| prices_daily.csv | 40 049 | 9 | OHLC, close ajusté, volume, devise |
| corporate_actions.csv | 658 | 5 | 651 dividendes et 7 événements étiquetés split |
| fx_usdcad_daily.csv | 1 245 | 3 | CAD par USD et inverse arrondi |
| macro_rates.csv | 8 281 | 7 | Neuf séries, fréquences mélangées |
| sources_metadata.csv | 6 | 10 | Six entrées de provenance pour cinq jeux, macro ayant deux sources |

Les neuf fichiers correspondent à ces six CSV, au README, au script et au fichier d'avertissements.

Univers : 20 actions individuelles, 4 FNB d'actions, 4 FNB obligataires, 1 FNB or et 2 cryptoactifs. Treize instruments sont cotés en CAD et dix-huit en USD. Les labels sectoriels des FNB décrivent des expositions, pas une classification homogène avec les entreprises.

Les 29 instruments hors crypto ont chacun 1 255 observations ; Bitcoin et Ether en ont chacun 1 827. La fenêtre de prix est partout 2021-11-12 → 2026-11-12. La date d'extraction déclarée est le 13 novembre 2026.

## 3. Contrôles de structure et d'intégrité

Mesures effectuées :

- Aucun champ vide parmi les colonnes des six CSV selon le contrôle des valeurs vides usuelles.
- Aucune ligne exacte dupliquée.
- Aucune duplication des clés `(date, ticker)` des prix, `(date, series_id)` de la macro et `(ex_date, ticker, action)` des opérations.
- Tous les tickers présents dans les prix et opérations appartiennent à l'univers.
- Aucun prix OHLC ou ajusté nul/négatif, aucun volume négatif.
- Aucune incohérence `low ≤ open/close ≤ high` détectée à une tolérance numérique de 1e-5.
- Une observation à volume nul : ZST.TO, 2022-07-06, déjà signalée au README. Un cours présent ne suffit donc pas à affirmer qu'une transaction y aurait été possible.
- L'écart maximal entre `cadusd` et l'inverse de `usdcad` est 4,99×10⁻⁷, compatible avec l'arrondi annoncé à six décimales.

Ces tests démontrent la cohérence structurelle observée. Ils ne démontrent ni l'exhaustivité des fournisseurs, ni l'absence de prix périmés, ni la justesse des classifications et événements.

## 4. Calendriers : même nombre de lignes, jours différents

| Comparaison | Mesure |
|---|---:|
| Dates actions canadiennes | 1 255 |
| Dates actions américaines | 1 255 |
| Dates communes | 1 228 |
| Dates canadiennes sans séance américaine correspondante | 27 |
| Dates américaines sans séance canadienne correspondante | 27 |
| Dates actions canadiennes sans taux FX | 10 |
| Dates actions américaines sans taux FX | 37 |
| Dates crypto sans taux FX | 582 |

Les instruments CAD partagent ici un calendrier ; les instruments USD hors crypto en partagent un autre. Ne jamais aligner les observations par numéro de ligne. Utiliser les dates et définir explicitement l'horloge de valorisation, l'horloge de décision et l'horloge d'exécution.

Les dix dates canadiennes sans FX sont : 2022-09-30, 2022-11-11, 2023-10-02, 2023-11-13, 2024-09-30, 2024-11-11, 2025-09-30, 2025-11-11, 2026-09-30 et 2026-11-11.

Un report du dernier taux connu peut convenir à une convention de valorisation, mais doit porter un indicateur de fraîcheur. Il ne crée ni séance de négociation, ni possibilité d'exécution. Remplir les rendements des actifs fermés par zéro sans explication change les estimations de risque et de corrélation ; sélectionner l'intersection des marchés élimine d'autres observations. Ces choix doivent être comparés en fonction de la politique de portefeuille et documentés.

## 5. Macro : couverture effective et trous discrets

| Série | Observations | Première date | Dernière date | Unité |
|---|---:|---|---|---|
| BD.CDN.10YR.DQ.YLD | 1245 | 2021-11-12 | 2026-11-12 | percent |
| BD.CDN.2YR.DQ.YLD | 1245 | 2021-11-12 | 2026-11-12 | percent |
| CPIAUCSL | 59 | 2021-11-01 | 2026-10-01 | index |
| DFF | 1826 | 2021-11-12 | 2026-11-11 | percent |
| DGS10 | 1248 | 2021-11-12 | 2026-11-10 | percent |
| DGS2 | 1248 | 2021-11-12 | 2026-11-10 | percent |
| STATIC_TOTALCPICHANGE | 58 | 2021-12-01 | 2026-09-01 | percent |
| UNRATE | 59 | 2021-11-01 | 2026-10-01 | percent |
| V39079 | 1293 | 2021-11-12 | 2026-11-12 | percent |

### Défaut important à ne pas masquer

**Octobre 2025 est absent de CPIAUCSL et UNRATE** : chacune comporte 59 observations dans une période de 60 mois. Le générateur supprime les données FRED non numériques ; il n'indique pas le motif de cette absence. La cause ne peut pas être déduite des fichiers. Ne pas interpoler silencieusement, ne pas inventer une publication et ne pas supposer qu'un trou invalide tout le jeu. Documenter, rechercher la cause auprès de la source si la série est retenue, puis choisir un traitement justifié.

Les séries mensuelles américaines commencent au 1er novembre 2021, avant le début nominal du pack le 12 novembre. C'est une date de période de référence, pas une preuve qu'une information était connue ce jour-là. Les extrémités sont aussi décalées : DFF finit le 11 novembre 2026 ; DGS2 et DGS10 le 10 novembre ; l'IPC canadien en septembre et les séries américaines mensuelles en octobre.

### Risque de fuite d'information

Le pack ne contient ni dates de publication effectives ni millésimes historiques complets. Un `merge` sur le mois de référence puis un remplissage utiliserait des chiffres non encore publiés au moment simulé. Un simple décalage fixe ne corrige pas les révisions historiques FRED.

Choix à comparer : reconstruire les disponibilités et millésimes (si les données existent) ; limiter la macro à l'explication actuelle hors backtest ; ou présenter une expérience rétrospective avec une limitation précise, sans la faire passer pour une simulation réalisable point-in-time. Les signaux issus du corpus documentaire ont la même exigence de disponibilité historique.

DFF est un taux effectif quotidien, V39079 un taux cible ; ils ne représentent pas la même chose. DGS2/DGS10 et les séries canadiennes sont des rendements actuariels, pas les rendements réalisés d'un investissement obligataire. CPIAUCSL est un indice, l'IPC canadien fourni un pourcentage annuel. Ne pas les comparer directement comme des variables identiques. Une variation annuelle de CPIAUCSL nécessite douze mois de référence, avec traitement du trou d'octobre 2025 et du calendrier de publication.

## 6. Prix, dividendes, splits et devises

Selon le README, `adj_close` est rétroajusté pour splits et dividendes ; `close` est déjà ajusté pour splits. Il faut donc éviter :

1. d'appliquer à nouveau les ratios de split aux cours ;
2. d'ajouter les dividendes au rendement de `adj_close` ;
3. de traiter `adj_close` comme un prix d'exécution historique ;
4. de mélanger un ratio de rendement en USD et une valeur de portefeuille en CAD.

Pour une série de rendement total en USD `A` et un taux `X` en CAD par USD, une convention de valorisation CAD cohérente donne :

`1 + r_CAD,t = (A_t / A_(t-1)) × (X_t / X_(t-1))`.

Cette identité ne résout pas les problèmes d'horloge, de disponibilité ou de coûts de change. Ceux-ci doivent être définis séparément. Les métadonnées indiquent que le taux FX est publié autour de 16 h 30 ET : l'utiliser pour décider une transaction à la clôture précédente peut introduire de l'information future.

Les barres crypto sont des jours UTC de 00 h à 24 h. Le cours final du jour UTC D n'est pas connu à la clôture des actions nord-américaines du même jour civil D. Une jointure naïve sur `date` peut donc introduire une fuite intrajournalière, même avec des fréquences toutes dites « quotidiennes ».

L'événement CNQ.TO du 2022-08-22 comporte un `split` de 1,021 et un dividende de 0,75 CAD. Le README considère ce split atypique comme probablement lié à une distribution spéciale et demande vérification. Audit : présence confirmée ; explication économique non vérifiée. Le conserver comme événement à examiner, pas comme fractionnement ordinaire certifié.

## 7. Ce que le générateur vérifie vraiment

`build_dataset.py` télécharge Yahoo/yfinance, Banque du Canada et FRED ; assemble ; arrondit les cours ; exécute quelques assertions ; écrit les CSV. Il n'a pas été exécuté ici.

Points positifs : clés prix uniques, couverture des tickers, devises cohérentes, cours ajustés positifs, dates FX uniques, alertes de grands mouvements >40 % et de longues lacunes.

Limites du message « No warnings » :

- Le seuil d'alerte sur début d'historique utilise le 20 du mois du début, pas exactement START : une absence initiale courte peut passer.
- Le contrôle des lacunes prix >5 jours hors crypto ne détecte pas nécessairement une séance manquante isolée.
- Le contrôle ne recherche pas explicitement les mois macro manquants, leurs dates de disponibilité ou les révisions.
- Les opérations sont transmises à `check`, mais ne bénéficient pas de contrôles spécifiques.
- Pas de validation des OHLC, volumes nuls, unités macro ou synchronisation des horloges dans `check`.
- Pas de verrouillage des versions de dépendances dans ce script et la commande README ; refaire le téléchargement ultérieurement peut changer les données ajustées et les révisions.
- Les README et métadonnées sont écrits à la main et ne sont pas régénérés : ils peuvent devenir incohérents après changement de fenêtre ou d'univers.
- Les assertions Python peuvent être désactivées avec l'option d'optimisation `-O` ; un pipeline fiable doit utiliser des validations explicites pour les invariants indispensables.

Ces limites n'accusent pas le pack d'être défectueux : son rôle affiché est d'accélérer le démarrage, pas de constituer une infrastructure financière certifiée.

## 8. Ce que ces données ne permettent pas de conclure seules

- **Personnalisation** : aucun profil client, capacité de perte, objectifs, revenus, engagements, détentions ou flux futurs.
- **ESG** : aucun score, controverse, exposition détaillée des FNB ou preuve d'exclusion. Le nom ESGV ne prouve pas l'adéquation à une préférence précise du client.
- **Fondamentaux** : pas de bénéfices, dette, valorisation, bilan ou croissance économique attendue des sociétés.
- **Exécution** : pas de bid-ask, carnet, frais de courtier, glissement, fiscalité ou ordre fractionnaire.
- **Liquidité** : volumes historiques présents, mais insuffisants pour garantir prix/exécution, notamment lorsque le volume est nul.
- **Univers historique** : actifs sélectionnés en 2026 parmi les survivants ; pas de titres délistés ni composition point-in-time. Ne pas prétendre avoir reproduit en 2021 une sélection faite sans connaissance de 2026.
- **Diversification réelle** : positions individuelles et FNB peuvent se recouvrir. Le nombre de tickers ne mesure pas la diversification économique.
- **Espérance future** : cinq ans de rendements réalisés ne prouvent pas les rendements futurs ; la covariance de 31 actifs contient 496 paramètres distincts, dont 465 covariances. La précision apparente de l'optimiseur ne supprime pas l'erreur d'estimation.

Il n'est pas nécessaire d'acquérir toutes ces informations. L'équipe doit choisir la question et le niveau de promesse, puis acquérir uniquement les données dont la décision dépend réellement.

## 9. Socle méthodologique à étudier avant implémentation

Suggestions, non architecture imposée :

1. Geler une copie immuable du pack et son manifeste SHA-256.
2. Garder séparément données brutes, transformations et données décisionnelles.
3. Définir devise de base, calendrier de valorisation, dates de connaissance et politique d'exécution.
4. Enregistrer pour chaque donnée externe sa source, date d'extraction, période couverte, date de publication si pertinente et traitement.
5. Définir une référence simple cohérente avec le profil, les contraintes et les coûts ; toute méthode sophistiquée doit démontrer son apport face à cette référence.
6. Séparer chronologiquement estimation, choix des méthodes et évaluation ; documenter toutes les variantes essayées pour limiter le surajustement de recherche.
7. Rapporter sensibilité aux hypothèses, concentration, drawdown, turnover, frais et limites, pas seulement rendement cumulé.
8. Distinguer garantie d'optimisation **dans un modèle et sous ses hypothèses** d'une garantie financière dans le monde réel.

Aucune architecture particulière, méthode de portefeuille ou allocation n'est validée par cet audit.

## 10. Reproduction et sources locales

Les statistiques détaillées, dates par actif, extrêmes et empreintes sont dans `audit_stats.json`. Sources inspectées :

- `/Users/vpro/Downloads/Datathon2026/alphaforge_starter/README.md`
- `/Users/vpro/Downloads/Datathon2026/alphaforge_starter/build_dataset.py`
- les six CSV du même dossier ;
- `/Users/vpro/Downloads/Datathon2026/alphaforge_starter/data_quality_warnings.txt`.

Les observations propres aux fournisseurs citées ici sont attribuées aux documents du pack. Aucune vérification externe des cours ou des événements n'a été réalisée dans cet audit ; elle serait un chantier distinct. Les erreurs de calcul de stratégie, de conseil ou de performance ne sont pas évaluables tant qu'aucune stratégie n'a été définie.
