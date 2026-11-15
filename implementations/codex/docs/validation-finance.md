# Validation financière AlphaForge

Relevé du **15 novembre 2026 à 12:03:37 UTC** — 07:03:37 à Montréal. Les mesures ci-dessous proviennent d’appels directs à `calculate` avec les trois scénarios de [personas.py](../alphaforge_app/personas.py). Aucun modèle n’intervient dans ces chiffres et aucun fichier de données n’a été modifié.

## Périmètre et reproductibilité

- Moteur : `cad-buy-and-hold-v1`, mode `retrospective_replay`.
- Instantané : données acquises par les organisateurs le 13 novembre 2026, copie locale dans `data/alphaforge_starter`.
- Période de prix : **2021-11-12 → 2026-11-12**, 1 228 observations, 1 227 intervalles, 4,99941819 années écoulées.
- Valorisation conventionnelle D+1 à 00:00 UTC : première le **2021-11-13T00:00:00Z**, dernière le **2026-11-13T00:00:00Z**.
- Capital initial : **10 000 CAD** pour chaque option. Achat-conservation, distributions réinvesties via les prix ajustés, aucun rééquilibrage entre instruments, versement ou retrait. Frais de transaction/change et impôts exclus.
- Dix dates emploient un taux FX antérieur ; ancienneté maximale observée de trois jours. Aucun taux d’une date future n’est choisi.
- Les taux affichés ci-dessous sont exactement ceux du contrat JSON : six décimales pour les mesures en pourcentage, deux pour les valeurs monétaires. Ils restent des résultats arrondis de calcul en virgule flottante.

### Empreintes des fichiers lus par le moteur

| Fichier | Lignes de données | SHA-256 |
| --- | ---: | --- |
| `assets_universe.csv` | 31 | `f78de8ecb36d914a3448db63498cc9a04a34d805bccb79c481dda1650755467d` |
| `prices_daily.csv` | 40 049 | `ff2a3f2d0a7d72ea835e8d616d041e0510f018340cef3d3e55b918830e8a569d` |
| `fx_usdcad_daily.csv` | 1 245 | `f04e218ac5b0145fd552b3d0dcfbf73e5e17bb9a6fb4562460dbec95cb8972b3` |
| `sources_metadata.csv` | 6 | `7ff17052c8235888c4984430830610ae0d81c0df71585afaacb87ba5fe531bdf` |

Le fichier de métadonnées décrit aussi `corporate_actions.csv` et `macro_rates.csv`. Ces deux séries n’entrent pas dans les calculs rapportés.

## Hypothèses des trois démonstrations

Les personas officiels ne fournissent pas ces avoirs, ces capitaux ni ces repères de perte : **AlphaForge les a ajoutés comme hypothèses modifiables**. L’âge ne détermine aucun coefficient du moteur.

| Profil | Allocation initiale de référence | Modification étudiée | Horizon déclaré ; repère de perte |
| --- | --- | --- | --- |
| Robert | XBB.TO 35 % ; ZST.TO 20 % ; XIU.TO 20 % ; TSLA 25 % | TSLA → 5 % ; XBB.TO → 44,333333… % ; ZST.TO et XIU.TO → 25,333333… % chacun | 4 ans ; 15 % |
| Amira | QQQ 40 % ; NVDA 30 % ; BTC-USD 20 % ; XIU.TO 10 % | NVDA → 10 % ; QQQ → 51,428571… % ; BTC-USD → 25,714285… % ; XIU.TO → 12,857142… % | 15 ans ; 35 % |
| Mateo | ESGV 40 % ; XIU.TO 20 % ; XBB.TO 30 % ; XOM 10 % | XOM → 0 % ; ESGV → 44,444444… % ; XIU.TO → 22,222222… % ; XBB.TO → 33,333333… % | 10 ans ; 20 % |

Les autres positions sont redimensionnées proportionnellement ; les poids complets sont conservés en précision machine dans le résultat. Modifier l’horizon ne prolonge pas les séries ni ne produit une prévision.

## Mesures sur la période complète

| Profil et option | Valeur finale CAD | Rendement cumulé % | CAGR % | Volatilité annualisée % | Drawdown maximal % |
| --- | ---: | ---: | ---: | ---: | ---: |
| Robert — référence | 13 057,36 | 30,573572 | 5,480882 | 14,433788 | −23,396233 |
| Robert — modifiée | 13 048,72 | 30,487167 | 5,466917 | 6,343142 | −11,324237 |
| Amira — référence | 31 266,18 | 212,661783 | 25,610656 | 32,688433 | −44,642436 |
| Amira — modifiée | 22 395,29 | 123,952895 | 17,500438 | 25,590834 | −39,517028 |
| Mateo — référence | 17 772,24 | 77,722433 | 12,190030 | 10,779947 | −12,678804 |
| Mateo — modifiée | 15 804,05 | 58,040465 | 9,586810 | 11,214151 | −18,568820 |

La volatilité emploie **245,428558 intervalles observés par année** ; ce n’est pas une hypothèse de 252 séances ni une volatilité crypto calculée sur 365 jours. Le drawdown est négatif ou nul dans l’API. L’interface compare sa valeur absolue au repère choisi.

| Profil et option | Sommet avant le drawdown maximal | Creux maximal | Pire rendement entre observations % | Perte moyenne de la queue historique à 95 % |
| --- | --- | --- | ---: | ---: |
| Robert — référence | 2022-01-04 | 2022-12-28 | −3,801569 | 2,030158 % |
| Robert — modifiée | 2021-12-29 | 2022-10-20 | −1,548373 | 0,894859 % |
| Amira — référence | 2021-11-29 | 2022-10-14 | −10,742888 | 4,597228 % |
| Amira — modifiée | 2021-11-29 | 2022-11-09 | −7,146532 | 3,713039 % |
| Mateo — référence | 2025-01-30 | 2025-04-08 | −4,750178 | 1,595470 % |
| Mateo — modifiée | 2021-12-29 | 2022-06-16 | −4,283617 | 1,622993 % |

La mesure de queue est positive quand elle exprime une perte ; elle concerne les 5 % plus faibles rendements entre observations du passé. Elle ne donne ni une perte prévue demain ni une CVaR sur l’horizon du persona.

### Compromis effectivement observés

Robert réduit la baisse maximale observée et le rendement cumulé reste très proche. La baisse modifiée de 11,324237 % est sous son repère de 15 %. Amira réduit la baisse maximale, au prix d’un rendement cumulé sensiblement moindre dans cet échantillon ; 39,517028 % reste supérieur à son repère de 35 %. Mateo retire XOM, mais sa baisse maximale augmente à 18,568820 %, sous son repère de 20 %. Le texte de l’API indique bien « plus forte » pour Mateo. Aucun de ces repères ne garantit une limite de perte future.

Réduire la position étudiée n’implique pas que toute concentration diminue :

| Profil | HHI initial des instruments, référence → modifiée | Plus grand instrument, référence → modifiée |
| --- | --- | --- |
| Robert | 0,26500000 → 0,32740000 | XBB.TO : 35,000000 % → 44,333333 % |
| Amira | 0,30000000 → 0,35714286 | QQQ : 40,000000 % → 51,428571 % |
| Mateo | 0,30000000 → 0,35802469 | ESGV : 40,000000 % → 44,444444 % |

Ce HHI porte sur les instruments détenus. Il n’identifie pas les entreprises sous-jacentes aux FNB. Les variantes ne prouvent donc pas une diversification économique accrue, et le retrait direct de XOM ne certifie pas le reste du portefeuille sur le plan ESG.

## Scénarios historiques datés

Chaque fenêtre réinitialise les poids initiaux de chaque option et un capital de 10 000 CAD à son début. Elle n’est pas une continuation des poids ayant dérivé depuis 2021. Les chiffres sont les rendements cumulés en CAD, **référence → modifiée**, en pourcentage.

| Fenêtre réellement observée | Robert | Amira | Mateo |
| --- | ---: | ---: | ---: |
| 2021-12-31 → 2022-12-30 (« année 2022 ») | −20,768607 → −9,602127 | −38,223063 → −35,753266 | −2,289555 → −13,678446 |
| 2023-03-08 → 2023-03-24 | 1,234835 → 0,376415 | 9,796506 → 9,576297 | −0,876800 → −0,305895 |
| 2025-11-12 → 2026-11-12 | 3,125029 → 5,571946 | −2,005582 → 0,994756 | 14,406426 → 10,391455 |

La première fenêtre demandait une fin au 31 décembre 2022 ; le dernier point de la grille commune est le 30. Aucune probabilité future ni explication causale d’événements n’est attribuée à ces fenêtres.

## Contrôles exécutés : 8 tests numériques + 16 cas API

Résultats constatés le 15 novembre 2026 : **8/8 tests du moteur réussis**, puis **16/16 cas API réussis** après correction des paramètres par défaut des personas et du chemin des documents sources. La dernière exécution API a duré 1,51 s sur le Mac de travail. Cet ordre de grandeur n’est pas un benchmark de performance. Un avertissement de dépréciation Starlette/httpx a été émis ; aucun test n’a échoué.

Ce relevé documentaire réutilise ces résultats : les suites n’ont pas été relancées pour rédiger le document. Les mesures des tableaux ont été extraites séparément du moteur courant.

### Tests numériques indépendants

Fichier : [test_analytics.py](../tests/test_analytics.py). Les cas artificiels ont des valeurs de référence calculables sans les données de marché.

| Contrôle | Propriété ou valeur attendue |
| --- | --- |
| FX multiplicatif et antérieur | Cours USD 100→110→100 et FX 1,2→dernier 1,2→1,5 : patrimoine 10 000→11 000→12 500 CAD. Requête avant la première observation FX refusée. |
| Achat-conservation et dérive | Allocation 50/50 de la fixture : 10 000→11 500→10 750 CAD ; poids final CAD = 4 500/10 750. |
| CAGR géométrique | Aller-retour +100 % puis −50 % : CAGR nul ; cas 100→121 vérifié sur le nombre exact de jours. |
| Drawdown depuis le sommet courant | Série 100, 120, 90, 110, 130, 104 : minimum −25 %, nouveau sommet à 130 puis −20 %. |
| Modification de poids | Budget conservé, proportions des autres instruments conservées ; destination impossible refusée. |
| Queue empirique fractionnaire | Rendements −30 %, −10 %, +20 % : queue de 50 % = (30 % + 0,5 × 10 %)/1,5. |
| Entrées erronées | Poids en pourcentages au lieu de fractions, négatifs, NaN, booléens et symbole inconnu refusés par le moteur. |
| Capital et calendrier | Capital multiplié par dix : richesse multipliée par dix, rendement identique ; mêmes dates pour les options. |

### Cas API sur l’instantané fourni

Fichier : [test_api_finance.py](../tests/test_api_finance.py). Tous les appels ont `use_ai=False` ; ils utilisent des répertoires temporaires pour les rapports.

| Groupe | Nombre de cas | Contrat vérifié |
| --- | ---: | --- |
| Robert, Amira, Mateo complets | 3 | Recalcul différent, poids cible/budget, grille commune de 1 228 points, JSON fini, empreinte des prix, références des observations résolues, documents internes accessibles et hypothèses signalées. |
| Persona seule | 3 | Paramètres par défaut du persona choisi, y compris horizon et titre étudié ; aucune reprise silencieuse des valeurs de Robert pour Amira/Mateo. |
| Paramètres partiels | 1 | Modifier seulement le capital d’Amira conserve son horizon et NVDA. |
| Échelle du capital | 1 | Capital ×3 : valeurs monétaires ×3 à l’arrondi près, taux de rendement/CAGR/volatilité/drawdown invariants. |
| Curseur et repère de perte | 1 | Curseur au poids d’origine : séries identiques. Seuil passant de 1 à 90 % : chiffres inchangés, constat de dépassement inversé, absence de garantie conservée. |
| Exclusion ESG | 1 | XOM disparaît de l’exposition directe, ESGV reste ; le drawdown plus fort est signalé et aucune certification ni composition de fonds n’est inventée. |
| Poids ou symboles invalides | 4 | Budget incomplet, poids négatif, doublon et symbole inconnu produisent HTTP 422. |
| Rapport sauvegardé | 1 | Restitution exacte de la comparaison et des empreintes. |
| Source déplacée | 1 | Le README provient du répertoire de données configuré, y compris après restauration ailleurs. |
| **Total** | **16** | |

Commandes de reproduction depuis la racine du projet :

```sh
.venv/bin/python -m unittest discover -s tests -p test_analytics.py -v
.venv/bin/python -m pytest tests/test_api_finance.py -q
```

## Ce que ces résultats n’établissent pas

Les contrôles valident des contrats et exemples ciblés ; ils ne constituent pas une preuve exhaustive d’absence de défaut. L’univers choisi en 2026, les ajustements rétrospectifs, les coûts exclus et l’absence de millésimes empêchent de présenter ces résultats comme une stratégie sélectionnée et exécutée historiquement. La grille commune omet les mouvements crypto des fins de semaine et les mouvements intrajournaliers ; le drawdown observé peut manquer un creux. Les taux FX sont indicatifs et les intervalles inégaux limitent l’interprétation de la volatilité annualisée.

Aucune qualité d’inférence Bedrock, pertinence du profil réel, expérience utilisateur, supériorité d’optimisation ou performance future n’est validée par ces 24 cas. Voir les [décisions et références](references.md) pour les hypothèses et sources qui justifient le périmètre.
