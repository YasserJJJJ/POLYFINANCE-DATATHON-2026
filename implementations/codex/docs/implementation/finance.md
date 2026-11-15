# Moteur financier exécuté — Prompt 4

Le module `alphaforge_app/decision/finance.py` expose `analyze(problem) -> dict`
et `examples() -> list[dict]`. Deux calculs sont effectivement exécutés :
un programme linéaire de réallocation avec réserve abstraite, et une comparaison
historique en CAD. Les entrées des exemples sont explicites et modifiables.
Aucune sortie du dossier illustratif Prompt 3 n'est recopiée.

Le moteur est un outil numérique de l'Agent 2. Il ne qualifie pas seul la demande,
ne remplace pas la revue documentaire et ne fabrique ni consentement ni preuve
d'affichage. Il n'appelle aucun LLM, service web ou téléchargement de marché.

## Contrat et provenance

Le résultat respecte [CONTRAT_INTEGRATION.md](CONTRAT_INTEGRATION.md) :
`status`, `method`, `inputs`, `options`, `checks`, `claims`, `limitations`,
`missing`, `provenance`, avec `sensitivity` et éventuellement `optimal_face`.

- `options[].metrics.<nom>` contient `{value, unit}` ; les poids sont des
  fractions du capital initial. Les pertes de scénario sont en CAD.
- Les claims sont construits par code et leurs `result_refs` désignent des
  JSON pointers dans **ce résultat**, avec unités. La restitution peut retrouver
  le nombre original, au-delà de son arrondi textuel.
- Chaque exécution consigne l'heure UTC, le hash SHA-256 des entrées JSON
  canoniques, les hashes du code financier et des deux modules réutilisés,
  les versions NumPy/SciPy et les hashes des paramètres ou fichiers utilisés.
- `conditional` signifie calcul réalisé dans son domaine documenté ;
  `missing_input`, `unsupported`, `infeasible` et `error` restent distincts.
  Une erreur opérationnelle ne devient pas une infaisabilité économique.
- Une clarification explicitement bloquante empêche le calcul. Ni une réserve
  réelle inconnue ni un rendement manquant ne reçoit une valeur implicite.

Les exemples passent par les mêmes fonctions que tout autre problème. Ils ne
contiennent aucune règle « âge → allocation » ni allocation officielle de persona.

## 1. Réallocation et réserve abstraite

Soient \(V_0>0\), les poids initiaux \(w^0\), un retrait \(Q\), les plafonds
déclarés \(u_i\) et les chocs hypothétiques \(r_{si}\). L'univers comprend les
positions déclarées, y compris celles de poids zéro, et `RESERVE_ABSTRAITE`.
Un identifiant inconnu dans un plafond est refusé.

\[
\begin{aligned}
\min_{w,d}\quad & T=\frac12\sum_i d_i \\
\text{s.c.}\quad & d_i\ge w_i-w_i^0,\quad d_i\ge w_i^0-w_i,\quad d_i\ge0,\\
& \sum_i w_i=1,\quad 0\le w_i\le u_i,\\
& w_R\ge Q/V_0,\\
& -V_0\sum_i w_i r_{si}\le L_{\max}\quad\text{si un budget de perte est fourni.}
\end{aligned}
\]

Sans plafond explicite, la borne supérieure vaut 1 dans ce modèle long-only.
Le capital réalloué est \(V_0T\), égal aux achats et aux ventes séparément,
et non à leur somme. La richesse terminale sous choc vaut
\(V_0(1+\sum_iw_ir_{si})\), puis cette valeur moins \(Q\) après retrait.
Si la réserve exigée n'est pas financée, cette dernière valeur reste `null`
pour la baseline inadmissible.

La politique `abstract_nominal` doit être explicitement choisie. Elle définit
une réserve de rendement nul, disponible au retrait, sans coût, impôt ni
inflation modélisés. **ZST n'est jamais transformé en réserve garantie.**
Tous les autres rendements de choc doivent être fournis, même pour une position
initiale nulle. Ce sont des variations de valeur **en CAD**, sans probabilités,
à la même échéance que le retrait ; pas une projection des prix cotés en USD.
Un scénario de 48 mois n'est pas appliqué à un retrait de 12 mois.

Les plafonds portent sur l'allocation initiale après réallocation, pas sur les
poids après choc ou retrait. Ces pertes terminales ne sont pas des drawdowns.
L'horizon du solde, par exemple quatre ans, demeure une entrée de cadrage :
aucun rendement ni risque à cet horizon n'est extrapolé.

### Vérification de l'optimum

SciPy `linprog(method="highs")` résout le LP. Le code vérifie les résidus des
contraintes, des bornes et du budget, la stationnarité, les signes des
multiplicateurs duaux et l'écart primal-dual, avec tolérance `1e-8` en variables
normalisées. Un contrôle séparé recalcule les contraintes sur les poids retournés.
La tolérance monétaire correspondante vaut \(V_0\,10^{-8}\) CAD.

Une borne indépendante du solveur utilise l'identité achats = ventes = demi-L1 :

\[
T \ge \max\left((Q/V_0-w_R^0)_+,\;\sum_i(w_i^0-u_i)_+\right).
\]

Atteindre cette borne prouve le minimum sous les contraintes vérifiées. Quand
les scénarios exigent davantage de ventes, elle peut ne pas être serrée :
le rapport le dit (`partial`), sans transformer cette borne en optimum.

Le moteur minimise et maximise chaque poids sur la face
\(T\le T_{\min}+10^{-9}\). Il conserve des plages et, lorsqu'il en trouve un,
un témoin distinct de plus de `1e-6` en poids. Ce sont des optima à la
tolérance déclarée. L'absence de témoin n'est pas présentée comme une preuve
symbolique d'unicité. Aucun départage par risque, rendement, frais ou préférence
non déclarée n'est introduit.

Les sondages de sensibilité résolvent de nouveaux LP pour un retrait déplacé
de ±10 % du capital et chaque plafond déplacé de ±5 **points** de pourcentage,
avec bornage des plafonds entre 0 et 1. La baseline et la question active ne
sont pas modifiées. Chaque sondage expose son statut et ses diagnostics.
Ces sondages n'ajoutent aucune préférence à la demande.

En cas d'infaisabilité, le moteur ne relâche rien. Il donne le statut du
solveur et, quand disponible, une contradiction simple indépendante :
retrait supérieur au capital, borne inférieure supérieure à la borne supérieure
ou somme des plafonds inférieure à 1. **Aucun IIS n'est actuellement calculé.**
Le choix de la contrainte à réviser relève d'une question supplémentaire.

### Résultats exécutés Robert

Entrées : 100 000 CAD ; XBB 35 %, ZST 20 %, XIU 20 %, TSLA 25 % ;
retrait à 12 mois ; TSLA au plus 10 % à t0 ; budget de perte sous chacun des
deux chocs de 15 000 CAD. Les chocs et leur nature hypothétique sont dans
`examples()[0].facts.scenarios`. Les taux utilisés sont :

| Choc | XBB | ZST | XIU | TSLA | Réserve abstraite |
|---|---:|---:|---:|---:|---:|
| Actions | −5 % | 0 % | −20 % | −50 % | 0 % |
| Obligations | −15 % | −2 % | −10 % | −25 % | 0 % |

Exécution du 15 novembre 2026, SciPy 1.18.1 / NumPy 2.5.4 :

| Résultat | Retrait 30 000 | Retrait 40 000 |
|---|---:|---:|
| Capital réalloué minimal, CAD | 30 000 | 40 000 |
| Borne indépendante, CAD | 30 000 | 40 000 |
| Réserve de l'optimum retourné | 30 % | 40 % |
| TSLA / XBB / XIU / ZST | 10 / 20 / 20 / 20 % | 10 / 10 / 20 / 20 % |
| Perte choc actions, CAD | 10 000 | 9 500 |
| Perte choc obligations, CAD | 7 900 | 6 400 |
| Solde après retrait, choc actions, CAD | 60 000 | 50 500 |
| Solde après retrait, choc obligations, CAD | 62 100 | 53 600 |

Les résidus primal, de stationnarité et d'écart primal-dual des deux solutions
principales sont nuls dans cette exécution. Un autre optimum trouvé pour 30 000
contient réserve 30 %, TSLA 0 %, XBB 35 %, XIU 15 %, ZST 20 % :
ses pertes sous les deux chocs sont 4 750 et 7 150 CAD. Pour 40 000, le témoin
contient réserve 40 %, TSLA 0 %, XBB 35 %, XIU 5 %, ZST 20 % :
ses pertes sont 2 750 et 6 150 CAD.

Ces témoins montrent qu'un minimum de turnover ne désigne pas un seul
portefeuille. Le solveur peut retourner d'autres poids optimaux selon sa version.
Les tests ne fixent pas arbitrairement ces poids ; ils vérifient admissibilité,
minimum et présence d'un témoin distinct. Aucun des témoins ne reçoit le titre
de meilleure solution personnelle.

## 2. Comparaison historique en CAD

Le module réutilise `analytics.py` et `datasets.py` après lecture de leur
implémentation et tests indépendants. L'option cible redistribue les autres
poids proportionnellement. Les deux allocations sont rejouées en
achat-conservation, distributions réinvesties dans chaque actif via
`adj_close`, sans rééquilibrage entre actifs. Les dividendes et splits ne sont
pas ajoutés une deuxième fois.

Le CAGR utilise la richesse finale/initiale et la durée calendaire réelle :
\((V_f/V_0)^{365.2425/\Delta jours}-1\). Le drawdown est négatif ou nul,
\(\min_t(V_t/\max_{u\le t}V_u-1)\). La volatilité est l'écart-type
échantillonnal des rendements simples, annualisé par la racine du nombre
d'intervalles observés par année écoulée. Cette annualisation descriptive reste
sensible aux intervalles inégaux.

La grille est l'intersection fixe des séances des actifs hors crypto du snapshot,
identique entre options. La ligne D est valorisée conventionnellement à
D+1 00:00 UTC : prix des actions de D et bougie crypto UTC de D achevée.
Les prix USD sont convertis par le FXUSDCAD de D ou de la dernière date antérieure.
Un FX âgé de plus de sept jours est refusé. Les reports sont listés, sans
prétendre disposer d'un prix de change exécutable synchronisé.

La `knowledge_date` est obligatoire. Les dates `retrieved_on` du snapshot pour
l'univers, les prix et le FX nécessaire doivent toutes être documentées et
antérieures ou égales à cette date. **Tronquer des prix d'une capture acquise
ultérieurement ne reconstruit pas un ancien millésime.** La dernière ligne
autorisée est D = `knowledge_date` − un jour, compte tenu de la convention
de valorisation. Les heures de publication exactes restent inconnues.

Même après ces contrôles, l'univers et les prix ajustés 2026 demeurent
rétrospectifs : ce n'est pas un backtest d'une sélection réellement disponible
en 2021. Aucun résultat de macro à date de référence n'entre dans ce calcul.
Les fenêtres de stress sont étiquetées `historical_window` et réinitialisent
l'allocation à leur début. Le mode refuse un retrait ou une contrainte de choc
qu'il ne saurait modéliser. Les éventuels plafonds sont vérifiés sur les poids
initiaux, sans attester la convenance personnelle.

### Résultats exécutés Amira

Entrées fictives explicites : capital 25 000 CAD ; SPY 45 %, XIU 30 %, TSLA 25 %.
La variante fixe initialement TSLA à 10 %, donc SPY 54 % et XIU 36 %.
Snapshot acquis le 2026-11-13 ; connaissance demandée le 2026-11-15.
Période effectivement observée : **2021-11-12 → 2026-11-12**, 1 228 points.
Le FX a été reporté à dix dates ; âge maximum observé trois jours.

| Mesure | Initiale | Cible TSLA 10 % |
|---|---:|---:|
| Valeur finale, CAD | 44 515,75 | 46 874,02 |
| Rendement total, % | 78,063006 | 87,496089 |
| CAGR, % | 12,233000 | 13,397844 |
| Volatilité annualisée descriptive, % | 20,032058 | 15,962031 |
| Drawdown observé, % | −26,871589 | −19,878378 |

Ces différences décrivent cette période et ces données ; elles ne classent
pas les options pour les quinze prochaines années. Les compositions réelles
des FNB, exclusions ESG, fondamentaux et capacité personnelle de perte
restent non établis.

Empreintes des données utilisées :

| Fichier | SHA-256 |
|---|---|
| `assets_universe.csv` | `f78de8ecb36d914a3448db63498cc9a04a34d805bccb79c481dda1650755467d` |
| `prices_daily.csv` | `ff2a3f2d0a7d72ea835e8d616d041e0510f018340cef3d3e55b918830e8a569d` |
| `fx_usdcad_daily.csv` | `f04e218ac5b0145fd552b3d0dcfbf73e5e17bb9a6fb4562460dbec95cb8972b3` |
| `sources_metadata.csv` | `7ff17052c8235888c4984430830610ae0d81c0df71585afaacb87ba5fe531bdf` |

Les hashes du code courant sont produits à chaque appel plutôt que figés dans
cette note ; la sérialisation complète est destinée au registre du dossier.

## Validation effectivement réalisée

Commande : `.venv/bin/python -m pytest -q tests/test_decision_finance.py`

Résultat du 15 novembre 2026 : **36 tests passés en 0,97 s**, avec Python 3.15.2,
NumPy 2.5.4 et SciPy 1.18.1. Treize avertissements de dépréciation proviennent
du plugin pytest LangSmith installé ; aucun n'est un échec du moteur.

La suite vérifie notamment :

- Robert 30/40, sans imposer un portefeuille optimal arbitraire ; borne
  indépendante, contraintes et équation du solde.
- Nouveau cas A seul, plafond 60 % : retrait 25 sur capital 100, mais vente
  minimale 40 ; réserve déjà présente : aucune vente inutile.
- Nouveau cas de perte maximale : choc de −50 % sur A et budget 10 sur
  capital 100 ; \(w_A\le0,2\), donc rotation minimale 80, alors que la borne
  réserve/plafonds seule vaut zéro.
- Mise à l'échelle du capital, sensibilités réellement résolues, entrées intactes,
  clarifications bloquantes, rendements absents même pour un actif de poids zéro,
  incohérence d'échéance, doublons, nombres invalides, contraintes infaisables,
  distinction panne solveur/infaisabilité.
- Références historiques synthétiques indépendantes : prix CAD 100→80→120,
  prix USD constant 100 et FX 1→2→2. Drawdown CAD −20 %, CAGR calculé par
  formule indépendante ; allocation moitié CAD/moitié USD : richesse finale 160.
- FX absent ou périmé, prix absent, date d'acquisition absente ou future,
  refus d'un retrait non modélisé ; reproduction Amira sur le vrai snapshot.
- Sérialisation JSON sans NaN, résolution des pointeurs de claims et vérification
  des hashes du code présent sur disque.

Cette validation ne couvre pas les transactions SQLite, les quatre rôles AWS,
l'interface ou les preuves de consentement. Elle ne transforme pas des chocs
hypothétiques en données observées ni une reproduction historique en validation
prédictive.

## Sources et suites admissibles

La formulation et les contrôles LP suivent les notions de programmes linéaires
et de dualité de Boyd & Vandenberghe,
[*Convex Optimization*](https://web.stanford.edu/~boyd/cvxbook/), déjà examinées
dans la recherche Prompt 2. Les contrôles d'infaisabilité sont volontairement
décrits à leur niveau réel, conformément à
[la revue des méthodes](../recherche/finance/01_revue_par_decision.md) et au
[journal d'implémentations candidates](../recherche/finance/05_implementations_candidates.md).
SciPy/NumPy sont des dépendances ouvertes ; le choix de ces deux méthodes
n'interdit pas l'admission ultérieure d'autres bibliothèques.

Les conventions de données viennent du README et des métadonnées du starter,
avec leurs limites Yahoo et Banque du Canada. Les résultats de recherche sur
contraction de covariance, GMV, CVaR, IIS et validation chronologique restent
dans [les expériences Prompt 2](../recherche/finance/04_experiences_et_notebook.md).
Ils ne sont pas présentés comme exécutés dans ce nouveau moteur. Une demande
de risque de trajectoire, rendement futur, instrument de réserve réel ou coût
fiscal rouvre la qualification et la sélection de méthode au lieu de prolonger
silencieusement les présentes hypothèses.
