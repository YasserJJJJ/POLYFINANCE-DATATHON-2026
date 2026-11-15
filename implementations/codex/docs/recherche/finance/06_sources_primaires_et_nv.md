# Lectures primaires approfondies et bibliographie sans URL

15 novembre 2026. Ce complément distingue **ce qui a été effectivement lu**
dans ce cycle de ce que le dossier fourni annonce avoir lu. Il complète le
[registre de 133 URL](03_registre_sources.md) et son
[équivalent JSON](registre_urls.json), lequel couvre les 108 URL uniques des
§9.2, 9.3 et 9.7. Les autres équipes couvrent leurs sections.

Les métadonnées `sources/*.json` conservent URL exacte, date, transport et
empreinte. Les PDF et extraits sont des copies de recherche ; leur accès ne
constitue pas une licence de redistribution publique. Aucun statut HTTP n'est
pris pour une preuve de lecture.
Les 32 entrées bibliographiques, méthodes et outils regroupés sans URL sont également
disponibles dans [registre_nv.json](registre_nv.json).

## Textes primaires approfondis : passage → décision

| ID complémentaire / rattachement | Version réellement consultée et accès primaire | Lecture effective | Conséquence pour le projet, réserve ou contradiction |
|---|---|---|---|
| F01 / U343, NV15 | Boyd & Vandenberghe, *Convex Optimization*, Cambridge, 2004 ; [livre auteur](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf), [métadonnées](sources/boyd_convex.json) | Passages : pp.136–137 convexité et unicité ; p.152 QP ; pp.226–227 Slater ; pp.250–251 sensibilité duale ; p.263 alternatives/Farkas. Pagination imprimée, pas index PDF. | Une solution globale du modèle convexe ne valide pas son adéquation financière. PSD suffit pour convexité du QP ; unicité demande davantage. Dualité/sensibilité nécessitent leurs conditions, pas un score universel de préférence. Livre non lu intégralement. |
| F02 / U049 | Chinneck, *Infeasibility and Feasibility*, tutoriel CPAIOR 2007 ; [PDF auteur](https://sce.carleton.ca/faculty/chinneck/docs/CPAIOR07InfeasibilityTutorial.pdf), [métadonnées](sources/chinneck2007.json) | Diapositives 4, 7–9, 15, 32–33, 55–59 : IIS, filtre par suppression, relaxation élastique, MIP, couverture des IIS. | IIS irréductible ≠ cardinalité minimale ≠ meilleure réparation. L'ordre de suppression peut changer le résultat. Motive notre contre-exemple/API et les vérifications du certificat. |
| F03 / U346, NV03–04 | Ledoit & Wolf, *Honey, I Shrunk the Sample Covariance Matrix*, document UPF 691 de juin 2003, antérieur à JPM 2004 ; [PDF](https://econ-papers.upf.edu/papers/691.pdf), [métadonnées](sources/ledoit_upf.json) | Résumé, pp.6–7 cible à corrélation constante et combinaison ; p.10 conclusion ; annexe B pp.11–12 perte de Frobenius, asymptotique et intensité. | La cible du texte n'est pas l'identité scalaire de notre essai. Ses résultats d'allocation active ne certifient pas notre GMV CAD. Le PDF publié de 2004 n'a pas été obtenu ; ne pas confondre versions ni autres articles Ledoit–Wolf. |
| F04 / U345, NV11 | Rockafellar & Uryasev, *Optimization of Conditional Value-at-Risk*, Journal of Risk 2(3), 2000, pp.21–41 ; copie liée depuis bibliographie auteur U345 ; [métadonnées et URL de téléchargement](sources/cvar2000.json) | Pages imprimées 23–27 : perte, continuité de distribution, fonction auxiliaire, convexité, approximation de scénarios et portefeuille linéaire. | Formulation LP utile. Une distribution empirique discrète requiert une convention de masse au quantile ; `mean(loss≥VaR)` ne convient pas toujours. Le contrôle ES local est indépendant, pas une reproduction de toute l'étude. |
| F05 / U152 | Mohajerin Esfahani & Kuhn, *Data-driven distributionally robust optimization using the Wasserstein metric*, [arXiv 1505.05116 v3](https://arxiv.org/pdf/1505.05116v3), 13 juin 2017 ; publié Mathematical Programming 171, 2018, pp.115–166 ; [métadonnées](sources/wasserstein.json) | §§2–3, pp.5–9 : observations indépendantes sous P commune, mesure produit P^N, certificat probabiliste, 1-Wasserstein, hypothèse 3.3 de queues, théorème 3.5/rayon. Introduction également lue. | Une garantie finie dépend du modèle probabiliste et de sa calibration. Rendements dépendants, ruptures et queues crypto ne satisfont pas automatiquement ces hypothèses. Preuves complètes et toutes reformulations non relues ; aucun DRO testé. |
| F06 / fiche 22, ligne 707 | Bailey & López de Prado, *The Deflated Sharpe Ratio*, version auteur 31 juillet 2014 ; [PDF auteur](https://davidhbailey.com/dhbpapers/deflated-sharpe.pdf), [métadonnées](sources/deflated_sharpe.json) | Principalement pp.6–9 : sélection, maximum attendu de Sharpe, essai multiples, DSR et moments. Annexe 3 repérée, non reproduite intégralement. | Un maximum moyen sous essais multiples n'est pas un quantile critique universel. Notre expérience simule une approximation normale déclarée et teste la dépendance ; elle ne reproduit pas l'intégralité du DSR. |
| F07 / U047 | Das, Ostrov, Radhakrishnan & Srivastav, *Dynamic portfolio allocation in goals-based wealth management*, Computational Management Science 17, 2020, pp.613–640, publication en ligne 4 juin 2019 ; [PDF auteur](https://srdas.github.io/Papers/GBWM_DP2.pdf), [métadonnées](sources/das_dynamic.json) | Résumé ; pp.618–619 dynamique de richesse/flux et grille ; pp.626–627 discrétisation de frontière, exemples ; pp.630–631 sensibilité de grille et horizons. | Les probabilités sont conditionnelles à la dynamique, à la frontière et aux paramètres. Les flux négatifs sont prévus. Une grille de 15 portefeuilles est un choix numérique, pas une ontologie fermée d'allocations. L'exemple de table comporte des poids négatifs : ne pas transférer sans qualification à une contrainte long seulement. Ni résultats du papier ni convergence reproduits. |
| F08 / hors dossier, validation | Réserve fédérale et agences, **SR 26-2**, 17 avril 2026, *Revised Guidance on Model Risk Management* ; [PDF officiel](https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf), [métadonnées](sources/sr26_2.json) | Texte parcouru ; attention particulière pp.3–6 champ, proportionnalité, finalité et contestation ; pp.8–9 solidité conceptuelle, résultats et suivi. | Remplace la référence routinière à SR 11-7 dans ce cadre américain. Exclut explicitement modèles génératifs/agentiques p.3 n.3 ; ne pas revendiquer conformité des quatre agents. Approche proportionnée surtout pertinente aux établissements >30 Md USD. Les simples calculs arithmétiques/règles peuvent aussi être hors définition du modèle. Principes de revue utilisables par analogie, sans force réglementaire attribuée au prototype. |
| F09 / U272, U367 | Federal Reserve Bank of St. Louis, [Real-Time Periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html), documentation courante lue le 15 novembre 2026 ; [métadonnées](sources/fred_realtime.json) | Introduction et exemples : date connue/révisée, FRED aujourd'hui vs ALFRED à date, `realtime_start/end`, bornes inclusives et défaut à aujourd'hui. CSV DGS10 inspecté séparément. | Publication et révision sont différentes. Le CSV courant n'est pas une preuve d'information disponible à une date ancienne. L'accès standard curl a réussi après l'échec de la collecte commune ; TLS conservé. |
| F10 / U147 | Chen & Cai, prépublication [arXiv 2501.12841 v3](https://arxiv.org/pdf/2501.12841v3), 27 novembre 2025 ; [métadonnées](sources/crypto_moments.json) | Introduction pp.1–3 sur moments variables, rotation et coûts. | Contrepoint à l'interdiction générale d'optimiser la crypto ; résultats détaillés et tables non audités, aucun gain transféré au starter. |
| F11 / U148 | Platanakis, Sutcliffe & Urquhart, *Optimal vs naive diversification in cryptocurrencies*, 2018, version acceptée ; [PDF dépôt institutionnel](https://centaur.reading.ac.uk/78105/3/Optimal%20vs%20Naive%20Diversificationin%20Cryptocurrencies%20-%20Final%20Version.pdf), [métadonnées](sources/crypto2018.json) | Résumé et introduction : quatre cryptomonnaies, fréquence hebdomadaire et règles comparées. | Un résultat situé peut contredire le récit de supériorité automatique des méthodes complexes. Ne démontre pas la supériorité de 1/N pour tout univers ou régime. Tables complètes non relues. |
| F12 / U151 | Peter Cotton, *Schur Complementary Allocation*, [arXiv 2411.05807 v1](https://arxiv.org/pdf/2411.05807v1), 2024 ; [métadonnées](sources/schur.json) | Introduction et pp.8–9 sur les expériences/simulations et covariance connue. | Alternative intéressante à la dichotomie naïf/Markowitz ; expériences sur dimensions et hypothèses différentes. Ni validation sur notre univers ni reproduction locale. |

Les copies de code PyPortfolioOpt/cvxportfolio/HiGHS et leurs passages précis
sont documentées dans [05_implementations_candidates.md](05_implementations_candidates.md).
Les cadres CFA et OSFI sont lus et analysés par l'équipe Agent1 ; ils ne sont
pas ajoutés artificiellement à la liste des lectures personnelles de cet agent.

### Échecs d'accès qui bornent les conclusions

- DGU : U001 permet de lire le résumé publié. U347 retourne une 404 ; une URL
  auteur apparemment PDF renvoie en réalité du HTML ; SSRN est bloqué.
  Il n'y a pas de reproduction de leur calcul de 3 000/6 000 mois.
- `ledoit.net/honey.pdf` U346 et autre URL auteur : échecs ; substitution
  explicitement datée par la note UPF 2003, pas équivalence silencieuse.
- Jain 2019 : notice/résumé U150 exploitable, accès article bloqué ; pas de lecture
  de toutes les allocations et statistiques.
- Cours GWU U163 : délai d'accès expiré, donc seuls titre et statut du dossier
  sont repris ; aucun passage de ce cours n'est utilisé comme preuve relue.
- Plusieurs pages primaires fournissent une coquille ou un contrôle d'accès
  malgré HTTP 200 : Valet documentation, MSCI, Stooq, Hayashi–Yoshida, Bohrium.
  Les réponses de données Valet/SEC effectivement obtenues sont des preuves
  distinctes, examinées dans [04_experiences_et_notebook.md](04_experiences_et_notebook.md).

## Triage de chaque référence bibliographique regroupée sans URL

Source commune : dossier fourni, **§9.2 ligne 1103**. L'intitulé de certains
articles ci-dessous sert à résoudre l'identité ; lorsqu'il n'a pas été vérifié
sur une notice primaire, il reste une **identification bibliographique candidate**.
Une référence non lue reste une piste et n'étaye aucun résultat quantitatif.

| ID | Entrée fournie / identité ou ambiguïté | Niveau réel de ce cycle | Décision et prochaine lecture si nécessaire |
|---|---|---|---|
| NV01 | Michaud 1989, *The Markowitz Optimization Enigma: Is “Optimized” Optimal?* | Bibliographie secondaire rencontrée dans textes lus ; original non lu | D2, instabilité des entrées ; ne pas transformer une critique en impossibilité générale. Original requis avant citation détaillée. |
| NV02 | Scherer 2002, *Portfolio Resampling: Review and Critique* | Dossier/bibliographie seulement ; article original non lu | D2, séparer resampling et contraction ; ne pas confondre avec Scherer 2006 U149 dont le résumé a été lu. |
| NV03 | Ledoit–Wolf 2003, notamment *Improved estimation of the covariance matrix of stock returns with an application to portfolio selection* | Identité par bibliographie ; article correspondant non lu | D2 ; la note UPF de juin 2003 F03 est une œuvre/version différente. |
| NV04 | Ledoit–Wolf 2004 : *A well-conditioned estimator for large-dimensional covariance matrices* **et** *Honey, I Shrunk the Sample Covariance Matrix* | Ambiguïté résolue conceptuellement ; note préalable à Honey lue F03, deux articles publiés non lus intégralement | D2 ; préciser identité vs corrélation constante, asymptotique et perte visée. |
| NV05 | Jagannathan–Ma 2003, *Risk Reduction in Large Portfolios: Why Imposing the Wrong Constraints Helps* | Bibliographie secondaire ; original non lu | D2 ; candidat sur effet régularisant des contraintes, pas justification d'un plafond utilisateur inventé. |
| NV06 | Black–Litterman 1992, *Global Portfolio Optimization* | Bibliographie seule | D2 ; les vues et leur confiance doivent avoir une origine. Une méthode bayésienne n'élimine pas l'estimation. |
| NV07 | Maillard–Roncalli–Teiletche 2010, propriétés des portefeuilles à contributions de risque égales | Bibliographie seule | D2 ; lire définitions/existence et contraintes avant d'implémenter ERC ; pas synonyme de 1/N. |
| NV08 | López de Prado 2016, *Building Diversified Portfolios that Outperform Out-of-Sample* | Bibliographie seule ; Schur F12 donne un contexte indirect | D2 ; candidats hiérarchiques à comparer, résultats du titre non repris comme garantie. |
| NV09 | Goldfarb–Iyengar 2003, *Robust Portfolio Selection Problems*, Mathematics of Operations Research 28(1), 1–38 ; DOI `10.1287/moor.28.1.1.14260` | Notice primaire repérée/vérifiée par recherche ; article non lu | D3 ; ensembles d'incertitude, reformulation et calibration à examiner si ce type de robustesse répond au besoin. |
| NV10 | Fabozzi–Huang–Zhou 2010, *Robust portfolios: contributions from operations research and finance*, Annals of OR 176, 191–220 ; DOI `10.1007/s10479-009-0515-6` | Notice éditeur/institutionnelle repérée ; revue non lue | D3 ; carte secondaire de travaux, pas source unique d'une garantie originale. |
| NV11 | Rockafellar–Uryasev 2000 | Texte primaire partiel lu, F04 | D3 ; LP CVaR, hypothèses de continuité ; cas empirique fractionnaire contrôlé séparément. |
| NV12 | Chekhlov–Uryasev–Zabarankin 2005, *Drawdown measure in portfolio optimization*, IJTAF 8(1), 13–58 ; DOI `10.1142/S0219024905002767` | Notice/lien primaire repérés ; texte non lu | D3 ; examiner chemin de richesse, définition de drawdown et convexité avant tout transfert à rendements composés avec retraits. |
| NV13 | Blanchet–Chen–Zhou 2022, *Distributionally Robust Mean-Variance Portfolio Selection with Wasserstein Distances*, Management Science 68(9), 6382–6410 ; DOI `10.1287/mnsc.2021.4155` | Notice primaire repérée/vérifiée ; texte non lu | D3 ; ne pas lui attribuer automatiquement les hypothèses/garanties du 1-Wasserstein F05, notamment pour pertes quadratiques. |
| NV14 | Best–Grauer 1991, *On the Sensitivity of Mean-Variance-Efficient Portfolios to Changes in Asset Means* | Bibliographie seule | D2 ; sensibilité aux moyennes à distinguer du GMV et des effets des contraintes. |
| NV15 | Boyd–Vandenberghe 2004 | Livre primaire, passages analysés F01 | D1/D3 ; propriétés de formulation, dualité et références indépendantes ; livre non lu intégralement. |
| NV16 | Harvey–Liu–Zhu 2016, *… and the Cross-Section of Expected Returns* | Bibliographie seule | D4 ; essais multiples de facteurs, pas source d'un seuil universel de Sharpe. Lire avant transfert du protocole. |

Cela couvre les **16 entrées nommées** de la ligne, dont une entrée Ledoit–Wolf
regroupe plusieurs dates et œuvres. L'examen critique d'une entrée ne signifie
pas la lecture de l'article entier.

### Asynchronisme : trois références sans URL

Source : §9.7, ligne « Asynchronisme », également liée à U280/U281.

| ID | Entrée | Niveau réel | Utilité conditionnelle |
|---|---|---|---|
| NV17 | Epps 1979 | Nom dans dossier ; original non lu | Effet de fréquence/non-synchronisation sur corrélations ; pas correction automatique pour prix quotidiens. |
| NV18 | Scholes–Williams 1977 | Nom dans dossier ; original non lu | Estimation de bêta avec négociation non synchrone ; nécessite lire modèle et hypothèses avant emploi. |
| NV19 | Dimson 1979 | Nom dans dossier ; original non lu | Mesure du risque lorsque les échanges sont peu fréquents ; pas substitut au contrat de calendrier/FX. |

Le contrôle direct des intervalles du notebook suffit à identifier le problème
présent. Il ne justifie pas encore un estimateur d'asynchronisme sophistiqué.

### Ligne regroupée d'outils de provenance

Source : §9.7 ligne 1324. Les sept noms sont tous triés ; seuls deux possèdent
un lien dans cette ligne. Les versions de la colonne fournie ne sont pas toutes
revérifiées.

| ID / outil | Lecture et version réellement vérifiée | Usage possible / limite |
|---|---|---|
| NV20 / DVC, U303 | Métadonnées PyPI 3.67.1 lues, Apache 2.0 déclaré | Versionner artefacts ; dépôt/code non audité, aucune exécution. |
| NV21 / MLflow | Nom/version fournis seulement | Journal d'expériences candidat ; licence et version non revérifiées dans ce cycle. |
| NV22 / OpenLineage | Nom/version fournis seulement | Lignage candidat ; ne garantit pas la véracité des données. Licence non revérifiée. |
| NV23 / Great Expectations | Nom/version fournis seulement | Contrôles de données candidats ; une expectation doit avoir une justification économique. Licence non revérifiée. |
| NV24 / Kedro | Nom/version fournis seulement | Pipeline candidat ; installation/portée/licence non vérifiées ici. |
| NV25 / papermill | Nom/version fournis seulement | Paramétrage/rejeu notebook candidat ; ne corrige pas ses équations. Licence non revérifiée. |
| NV26 / Hamilton, U304 | README Apache Hamilton lu ; licence déclarée Apache 2.0, pas audit de dépendances | Graphe de transformations candidate ; aucun pipeline exécuté. |

W3C PROV U308 a été consulté : *PROV-Overview* est une **Working Group Note**
du 30 avril 2013, pas lui-même une Recommendation. Les spécifications qu'elle
référence ont leurs propres statuts. *Datasheets for Datasets* U309 a été examiné
au niveau du résumé/notice (arXiv, publication CACM 2021), pas questionnaire
intégral. Ces cadres orientent documentation et provenance sans certifier les
prix ou leurs droits d'usage.

## Limite documentaire qui reste une décision

Une nouvelle lecture se justifie lorsqu'elle pourrait modifier la formulation,
la faisabilité, le choix de données ou l'interprétation d'un résultat. Elle est
inscrite avec sa question et son niveau de preuve. Les entrées NV restent visibles
pour permettre ce retour ; elles ne gonflent ni le nombre d'études lues ni la
force des conclusions actuelles.

## Complément d'audit : mentions sans URL hors du registre §9.2

Les six entrées suivantes complètent les 26 précédentes. Elles n'ont donné lieu
à aucune nouvelle recherche externe ni expérience. **Dossier seul** signifie
que la mention fournie a été examinée, pas que la publication originale a été
lue. Les deux dernières lignes sont des familles de méthodes, sans publication
identifiée dans le dossier ; elles ne comptent pas comme articles.

| ID | Mention et emplacement dans le dossier | Niveau réel | Statut et motif |
|---|---|---|---|
| NV27 | Shafer 1976, croyances de Dempster–Shafer ; §5.4, ligne 840, rappel ligne 1050 | Dossier seul ; ouvrage/édition et texte primaire non revérifiés | Non adopté. Combiner des scores ESG via des masses de croyance nécessiterait une définition des événements, des masses et de la dépendance entre sources. La citation ne justifie ni cette calibration ni une réduction arbitraire à un score ; couverture et désaccord restent descriptibles séparément. |
| NV28 | Clemen et Reilly, livre sous-jacent aux notes de cours GWU ; §5.4 ligne 843 et §9.2 ligne 1120 | Dossier seul pour le livre ; édition non identifiée. Le cours U163 a été tenté mais n'a pas été obtenu dans ce cycle | Livre non retenu comme preuve lue. Les bascules et sensibilités restent des candidats calculables, à vérifier sur équations/cas indépendants ; la mention du cours ne vaut pas lecture de l'ouvrage ni justification d'une méthode particulière. |
| NV29 | Hansen, attribution du test SPA ; fiche 22, ligne 712 | Dossier seul pour la publication ; titre, date et version non identifiés ici | Test non exécuté et non retenu comme preuve de performance. À approfondir si comparaison multiple à une référence, dépendance des séries et hypothèses nulles correspondent au futur protocole. La lecture du README arch ne remplace pas celle de la méthode. |
| NV30 | White, attribution de Reality Check ; fiche 22, ligne 712 | Dossier seul pour la publication ; titre, date et version non identifiés ici | Test non exécuté. La liste complète des stratégies essayées et le schéma de rééchantillonnage sont nécessaires avant interprétation ; aucun seuil ou contrôle d'erreur n'est revendiqué à partir de la mention. |
| NV31 | PRIM et RDM ; tableau des méthodes ligne 229, outils lignes 248/775 | Dossier et README EMA Workbench ; aucune publication originale identifiée/lue pour ces méthodes | Pistes, pas choix arrêté ni expérience réalisée. Découvrir des régions où une politique échoue est différent d'estimer une probabilité de ces scénarios. À étudier si incertitudes et ensemble de simulations sont qualifiés. |
| NV32 | StepM et MCS ; tableau outils ligne 246, fiche 22 ligne 712 | Dossier et README arch ; aucune publication originale attribuée/lue ici | Tests non exécutés. Ne pas inventer auteurs/date à partir du nom de l'API ; sélectionner un protocole pertinent et lire ses conditions avant de revendiquer élimination ou ensemble de modèles supérieurs. |

Les autres mentions repérées sans lien **à leur occurrence** renvoient déjà à
une source liée ailleurs : Horvitz 1999 est U221 ; Sharpe 1992 U294 ;
Deflated Sharpe est traité ici en F06 ; W3C PROV/Datasheets en U308/U309 ;
Epps/Scholes–Williams/Dimson en NV17–19. GSN sans URL précise est conservé par
le [registre AWS](../aws_agentique/triage_sources.md), et Reg BI sans URL eCFR
précise par le [registre profil/restitution](../profil_restitution/01_triage_64_references.md).
Cette vérification porte sur les références et méthodes nommées dans le dossier,
pas sur une recherche exhaustive de toutes leurs publications sous-jacentes.
