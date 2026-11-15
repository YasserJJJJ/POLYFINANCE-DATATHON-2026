"""Generate the finance source audit from explicit, human-reviewed annotations."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent

# Level describes this research cycle, not what the supplied dossier claimed.
ANNOTATIONS = """
U001|résumé primaire publié via notice|D2|RFS 2009, 22(5), 1915–1953. Paramètres calibrés US ; pas de borne universelle 3000 mois. PDF primaire non obtenu.
U002|résumé développé via notice|D2|FAJ 2010, 66(2), 31–39. Compare entrées de moyennes/GMV ; contrepoint à DGU, résultats non reproduits.
U003|résumé éditeur lu|D2|JFQA 2012, 47(2), 437–467. Turnover et coûts changent la comparaison ; intégral non lu.
U019|texte partiel §3.3–3.4|D4|arXiv 2508.10047v1. Benchmark/formulation séparés ; erreurs de jeux d'évaluation rapportées. Aucun taux transféré à AlphaForge.
U020|résumé arXiv lu|D1|arXiv 2307.03875. What-if sur modèle d'optimisation existant ; ne prouve pas qualification libre d'un besoin financier.
U028|inaccessible lors collecte|D5|Timeout Python commun ; aucune clause de cette page revendiquée comme lue. Les droits des séries restent distincts de l'API.
U029|repéré, extrait documentaire partiel|D5|Documentation yfinance de réparation ; à confronter aux événements, pas autorité sur un split particulier.
U030|texte primaire, sections méthodologie/disclaimers|D5|Page BoC redirigée : quotes 8–16 ET, taux indicatifs. Même date n'est pas synchronisme ni exécution.
U031|inaccessible, source alternative U297|D5|Éditeur 403 ; ne pas prétendre article complet lu. Résumé développé de revue U297 lu.
U032|résumé institutionnel lu|D5|ECGI WP708/2020, Berg–Fabisik–Sautner ; changements Refinitiv, non conclusion sur tous fournisseurs.
U033|résumé éditeur lu, pas PDF|D5|URL PDF renvoie page HTML de prévisualisation. Corrélation taille/ressources/score ESG ; aucune causalité universelle établie ici.
U045|clauses de licence primaire lues|D2|skfolio BSD-3-Clause, commit fixé dans sources/code. Fonctions non exécutées ; wrapper candidat, pas méthode validée.
U046|inaccessible|D1|JOIM.pdf 401. Le modèle 2018 n'est pas prétendu intégralement lu ; l'article dynamique 2020 est obtenu ailleurs.
U047|texte primaire partiel via autre dépôt auteur|D1|URL SCU401 ; copie auteur srdas GBWM_DP2.pdf, publication CMS2020/online2019. GBM, flux, grille et exemples lus ; cf F-DAS.
U048|résumé primaire via notice|D1|JFQA2010 mental accounts ; équivalence dépend des hypothèses/shorting, pas règle d'âge.
U049|texte primaire partiel + expérience|D3|Tutorial CPAIOR2007 récupéré par curl ; diapositives4,7–9,15,32–33,55–59. IIS, MaxFS et réparation distincts.
U050|code primaire partiel, licence, API testée|D3|HiGHS1.16.0/f3f113d ; stratégie légère vs irréductible. Pas validation de tous types de problèmes.
U051|code documentaire partiel lu|D3|Pyomo6.9.3 MIS : relaxation puis conflit apparent, tolérance et solveur requis ; source déclare BSD3. Non exécuté.
U052|clauses de licence primaire lues|D3|OR-Tools Apache2 commit fixé ; pas appel/benchmark CP-SAT. Contraintes d'entiers changent le solveur approprié.
U053|documentation éditeur lue|D3|Licence restreinte Gurobi : 2000 variables/contraintes ou 200 variables quadratiques ; recherche/évaluation non commerciale. Pas licence obtenue.
U054|README/structure partiels|D1|OptiGuide : sous-projet what-if observé. Pas inspection de sécurité du code généré, pas exécution.
U055|résumé arXiv lu|D1|OptiMUS2402.10172v1 ; formulation et résolution (MI)LP sur benchmarks, pas validation du besoin investisseur.
U094|page de présentation partielle|D5|GDELT : piste pour repérer des événements ; ni source primaire de leur véracité ni verdict ESG. Droits précis non vérifiés.
U095|guide du dashboard lu|D5|SBTi distingue engagement et cible validée ; actualisation hebdomadaire. Une cible n'est pas un résultat environnemental obtenu.
U096|inaccessible|D5|404 de la page Sustainalytics ; règles de citation actuelles non établies ici.
U097|notice secondaire repérée|D5|Osler explique81-334 ; source primaire alternative U301 consultée partiellement. Ne remplace pas le texte applicable.
U098|texte secondaire partiel lu|D5|MLT Aikins30 mars2026 rapporte C15 sanction26 mars ; pas vérification primaire de la loi dans ce sous-dossier.
U099|clauses primaires lues|D5|BoC attribution/modification/exceptions tiers et taux indicatifs ; permission générale n'efface pas réserves tierces.
U100|README partiel|D5|exchange_calendars : calendrier de places, pas prix ni disponibilité fournisseur ; licence indiquée Apache2 non auditée fichier ici.
U101|README partiel|D5|pandas_market_calendars : sessions/fermetures ; licence indiquée MIT non auditée fichier ici.
U102|clauses primaires partielles|D5|Yahoo licence logicielle personnelle et restrictions de revente/exploitation ; pas autorisation de redistribuer tout prix sous licence yfinance.
U103|README partiel, licence non relue|D5|Coin Metrics archives Community ; CC-BY-NC4 annoncé par dossier reste à confirmer pour le fichier/mode d'usage retenu.
U104|inaccessible, primaire alternatif U349|D4|SSRN403 ; papier auteur2015 lu partiellement via U349. PBO n'est pas calculé sur nos expériences.
U105|licence primaire lue|D4|arch, licence de type NCSA, commit fixé ; bootstrap et SPA candidats non exécutés.
U106|licence primaire, repérage README|D4|quantstats Apache2 ; métriques demandent calibration/annuité/rfr corrects. Non exécuté.
U146|résumé via notice lu|D2|Platanakis–Urquhart2019, BL/VBC crypto. Résultat conditionnel ; texte/comparaisons non reproduits.
U147|texte primaire partiel|D2|Chen–Cai arXiv2501.12841v3,27 novembre2025. Introduction coûts/moments lue ; tables de performance non auditées.
U148|texte accepté partiel|D2|Platanakis–Sutcliffe–Urquhart2018, copie Reading récupérée. Quatre cryptos/fréquence hebdomadaire ; pas généralisation multi-actifs.
U149|résumé éditeur lu|D2|Scherer2006 : résultats de resampling/prior peuvent s'inverser. Pas rejet global du bootstrap.
U150|résumé via notice lu|D2|Jain–Jain2019 Risks7(3)74 ; misspécification covariance/HRP. PDF MDPI403 ; conclusions non reproduites.
U151|texte primaire partiel|D2|Cotton2411.05807v1,29 octobre2024 ; connexion Schur/HRP et limites simulations pp.8–9. Pas avantage universel.
U152|texte primaire partiel approfondi|D3|Esfahani–Kuhn1505.05116v3,13 juin2017 ; §§2–3, hypothèse3.3/théorème3.5 et portée. Finitude/calibration du rayon essentielles.
U153|notice partielle seulement|D2|Le lien vise une réimpression chapitre2013, pas directement JPM1993 Chopra–Ziemba ; ratios précis d'erreurs non cités.
U154|résumé via notice lu|D1|Leshno–Levy2002 : almost dominance dépend de classe d'utilités/préférences ; pas règle universelle d'horizon.
U155|résumé via notice lu|D3|Long–Sim–Zhou2023 : cible acceptable/fragilité, DOIopre.2021.2238. Théorèmes non vérifiés ; extension candidate conditionnelle.
U156|résumé via notice lu|D3|Sniedovich2010 critique orientation locale info-gap ; controverse signalée, pas preuve générale contre toute robustesse.
U157|résumé/introduction primaires lus|D1|Shyur–Shih2024 : renversements TOPSIS/normalisation. Pas classement multicritère lancé.
U158|inaccessible|D3|MathWorks403 ; ne fonde pas notre validation. Chinneck et expérience indépendante utilisés.
U159|page auteur institutionnelle partielle|D1|MSR juillet2023 confirme OptiGuide et auteurs ; même travail U020, pas deuxième preuve indépendante.
U160|résumé/notice conférence lus|D4|IJCAI2025 article1192, même survey U019 ; ne compter qu'une famille documentaire.
U161|README/structure partiels|D1|OptiMUS plusieurs branches/versions ; scripts d'exécution repérés non lancés. MIT annoncé README, pas licence relue ici.
U162|résumé arXiv lu|D1|NL4Opt2303.08233v2,27 mars2023, compétition NeurIPS2022. Extraction entités/représentation LP, pas qualification des objectifs.
U163|inaccessible|D1|Certificat Python puis timeout curl ; cours sensibilité GWU non lu, aucune proposition attribuée à ce PDF.
U164|résumé via notice lu|D1|Javelin Diagrams2004 DOI10.1287/deca.1030.0006. Probabilité de changement suppose distributions ; pas information gratuite.
U165|licence primaire lue|D2|Riskfolio-Lib BSD3 au commit fixé, pas bibliothèque exécutée.
U166|licence et code partiels lus|D2/D3|PyPortfolioOpt MIT au commit fixé ; risk_models et EfficientCVaR inspectés, pas exécutés.
U167|licence primaire lue|D3|CVXPY Apache2, solveurs séparés ; DCP/convergence ne valident pas la formulation du besoin.
U168|licence primaire lue|D3|EMAworkbench BSD3, candidats exploratoires/scénarios ; modèle et domaines à définir.
U169|licence primaire lue|D1|pymcdm MIT, scores/normalisations ne sont pas préférences utilisateur établies.
U170|dépôt primaire et licence lus|D1|pymoo Apache2 au commit anyoptimization/pymoo ; multiobjectif candidat, aucun NSGA lancé.
U171|code partiel et clauses GPL lues|D1/D3|cvxportfolio GPLv3 : politiques/simulateur, coûts et flux temporels ; pas exclusion automatique, pas exécution.
U172|licence primaire lue|D4|empyrical-reloaded Apache2 ; conventions métriques à tester avant réutilisation.
U173|licence primaire lue|D4|vectorbt Apache2+Commons Clause1.0, restriction Sell spécifique ; pas simple Apache2.
U174|licence primaire lue|D1/D4|bt MIT ; candidat moteur événements/flux, pas exécuté.
U175|licence primaire + logiciel testé|D3|SciPy BSD3 au commit fixé ; version1.18.1 utilisée LP/SLSQP. Licence de ses composants distincte.
U176|licence primaire lue|D1|pyDecision GPL3-or-later, clause explicite initiale ; MCDA/LLM éventuel non exécuté.
U177|README et clauses AGPL lues|D4|pypbo AGPLv3, ancienneté/tests TODO visibles ; §13 réseau à respecter, pas interdiction automatique.
U178|licence primaire lue|D1|DiCE MIT ; contrefactuels ML ne deviennent pas solutions financières admissibles par eux-mêmes.
U179|licence primaire lue|reproductibilité|marimo Apache2 ; support de recherche possible, aucune UI créée.
U180|texte GPL primaire lu|restitution|ggdist GPLv3, licence de package à préciser avant distribution ; aucune figure R produite.
U272|documentation primaire lue via curl|D5|realtime_start/end délimitent information connue ; données latest + lag ne restituent pas révision. Copie locale fred_realtime.raw.
U273|coquille HTML seulement, schéma API testé U366|D5|Extraction ne contient que Valet API ; ne pas compter une lecture de documentation complète.
U274|licence primaire lue|D5|StatCan Open Licence permet utilisation/adaptation/vente avec conditions et attribution ; pas identique à licence du client Python.
U275|métadonnées PyPI lues|D5|stats-can3.3.0 déclare GPL-3.0-or-later ; fichier licence non relu, code non exécuté.
U276|page institutionnelle partielle lue|D5|Philadelphia Fed fournit historiques de vintages ; absence des observations initiales ne se corrige pas par délai.
U277|notice bibliographique lue|D5|Croushore–Stark2001 JoE105(1)111–130 ; résumé absent, article non lu.
U278|métadonnées PyPI lues|D5|fredapi0.5.2 sans champ licence ; cela ne prouve ni interdiction ni absence de licence, dépôt à examiner si retenu.
U279|métadonnées PyPI lues|D5|pandas-datareader0.11.1 BSD3 déclaré ; conditions des sources séparées.
U280|notice bibliographique lue|D5|Burns–Engle–Mezrich1998, JDerivatives5(4)7–18 ; texte non lu, pas d'estimateur importé par citation.
U281|échec de contenu malgré HTTP200|D5|ProjectEuclid renvoie Request unsuccessful/Incapsula ; Hayashi–Yoshida2005 non lu ici.
U282|repérage dépôt|D5|yfinance : code client distinct des données Yahoo ; aucune collecte de prix nouvelle.
U283|clauses primaires partielles lues|D5|CoinGecko dépend du plan ; ne pas qualifier le plan gratuit de droit universel de diffusion.
U284|inaccessible|D5|SEC documentation403 ; endpoint U369 accessible. Conditions d'accès complet non vérifiées ici.
U285|page commerciale lue partiellement|D5|EODHD distingue plans personnels/B2B et prix indicatifs ; prix commercial n'est pas licence précise du projet.
U286|conditions primaires partielles lues|D5|OpenFIGI droits FIGI, réserves descriptions et marques ; identifiant ≠ données/prix.
U287|documentation primaire partielle lue|D5|Mapping/rate limits observés ; aucune résolution d'identité effectuée.
U288|échec de contenu malgré HTTP200|D5|Stooq challenge JavaScript, conditions et téléchargements non vérifiés.
U289|coquille de page|D5|Tiingo texte vide de conditions ; pas de droit de diffusion établi.
U290|clauses primaires lues|D5|Alpha Vantage personnel/non commercial sauf accord ; notion commercial plus large qu'une vente directe.
U291|inaccessible|D5|Nasdaq URL404 ; licence actuelle non établie.
U292|inaccessible|D5|N-PORT SEC403 ; opportunité source holdings repérée, aucune disponibilité historique revendiquée.
U293|CSV et mentions d'usage lus|D5|iShares MSCI Canada ETF, holdings12 novembre2026 ; pas XIU.TO, ni preuve historique, restrictions personnelles/non commerciales explicites.
U294|texte primaire partiel lu|D5|Sharpe1992 style analysis minimise tracking variance sous contraintes ; facteurs estimés ne sont pas holdings.
U295|échec de contenu malgré HTTP200|D5|Bohrium WAF, pas article lu.
U296|collecté, dossier/notice seulement|D5|PDF Erasmus du contrepoint style analysis disponible mais corps non étudié ; ne fonde pas de claim supplémentaire.
U297|résumé développé de revue lu|D5|Berg–Kölbel–Rigobon2022 : scope/measurement/weights et divergence ne signifient pas analyse ESG futile. Pas article complet.
U298|texte auteur de vulgarisation partiel|D5|Harvard2020, même étude que U032 ; S&P1500 et changements de classement, pas preuve indépendante supplémentaire.
U299|page primaire commerciale lue|D5|Recherche publique renvoie désormais vers MSCI ONE/démo ; accès gratuit aux scores non confirmé.
U300|coquille HTML seulement|D5|Conditions MSCI non extraites ; aucune licence déduite du titre.
U301|texte primaire partiel introduction|D5|CSA81-334 révisé7 mars2024 remplace2022 ; vise disclosure des fonds. Reste à analyser le périmètre exact applicable.
U302|inaccessible|D5|Fasken403 ; pas utilisé pour conclusion juridique.
U303|métadonnées PyPI lues|reproductibilité|DVC3.67.1 Apache2 déclaré ; versionner des fichiers ne valide pas les données.
U304|README/notice de licence partiels|reproductibilité|Apache Hamilton Apache2 annoncé ; lignage d'exécution pas preuve scientifique.
U305|texte de licence partiel lu|reproductibilité|lakeFS1.87.0 BSL1.1, grant de production conditionnel ; distinguer serveur/SDK et usage.
U306|métadonnées et licence incluses lues|reproductibilité|pandera0.36.0 MIT ; validation de schéma ≠ adéquation scientifique.
U307|métadonnées PyPI lues|reproductibilité|prov3.3.0 MIT déclaré ; package et standard séparés.
U308|texte primaire partiel lu|reproductibilité|W3C PROV Overview, Working Group Note30 avril2013, pas lui-même une Recommendation normative ; entités/activités/agents.
U309|résumé primaire lu|reproductibilité|Datasheets arXiv1803.09010v8, CACM2021 ; motivation/composition/collecte/usages à décrire, pas qualité garantie.
U004|dossier + dépôt repéré|D4|TradingAgents, stratégie agentique à comparer à des baselines de même univers/coûts ; audit système porté par autre agent.
U005|dossier seulement dans sous-revue finance|D4|Article TradingAgents ; performances annoncées non répliquées ni reprises comme preuve.
U006|résumé primaire lu|D4|FINSABER texte courant collecte2026 ; extension périodes/univers et biais. Tables complètes non auditées par Agent2.
U007|résumé/introduction primaires lus|D4|Profit Mirage2510.07920 : affirmation de fuite et méthode contrefactuelle à tester, pas preuve causale universelle adoptée.
U008|résumé primaire lu|D4|StockBench2510.02209v2 ; résultats de trading distincts QA, contamination-free est revendication à examiner.
U009|dossier seulement|D4|Sarkar–Vafa poster atelier DataWorld ICML2025 ; pas preuve de l'ensemble de la conférence.
U074|résumé primaire lu|D4|ChronoBERT/ChronoGPT2502.21206 ; biais spécifique au modèle/application, contrepoint aux conclusions universelles de fuite.
U075|résumé primaire lu|D4|TiMaGPT2404.18543v1, NAACL Findings2024 ; modèles temporels candidats non utilisés hors AWS.
U341|page primaire confiée Agent1, lien cadrage|D1|CFA2026 objectifs/contraintes/IPS ; pas attribution d'une formule de portefeuille à un persona.
U342|même source primaire que U030|D5|BoC URL explicite méthodologie ; une famille documentaire, pas seconde preuve indépendante.
U343|livre primaire sections ciblées lu|D3|Boyd–Vandenberghe2004 pp136–137,152,226–227,250–252,263 ; cf F-BOYD.
U344|notice primaire + copie auteur lue|D3|Rockafellar–Uryasev2000 JoR2(3)21–41 ; §§2–3 pp23–27 ; cf F-CVAR.
U345|bibliographie auteur consultée|D3|Lien de téléchargement primaire CVaR résolu depuis cette page ; la page n'est pas une étude indépendante.
U346|échec URL, version apparentée lue|D2|Honey.pdf non obtenu ; note UPF691 juin2003 obtenue, cible corrélation constante. Ne pas confondre avec article JMA identité2004.
U347|inaccessible|D2|Miroir DGU404 malgré extrait index moteur ; texte intégral non lu.
U348|bibliographie auteur lue|D2|Confirme titre/date/revue DGU ; lien LBS200 renvoieHTML et pas le papier.
U349|texte auteur partiel|D4|Bailey–Borwein–LópezdePrado–Zhu, version27 février2015 ; résumé/cadre PBO, pas reproduction CSCV.
U350|résumé auteur lu|D4|Bailey et al.7 octobre2014, outil illustratif d'overfit sur marches aléatoires ; pas étude empirique de nos stratégies.
U363|coquille de documentation|D5|Valet français, schéma et données testés sur U366.
U364|inaccessible lors collecte|D5|Accueil FRED timeout, aucun effet sur réussite CSV obtenue séparément.
U365|inaccessible|D5|SEC documentation403 ; périmètre antérieur couvert par notebook et réponse U369.
U366|réponse JSON primaire parsée/testée|D5|1461FX, dates/positivité/unité ; pas reconstitution de l'instant historique de publication.
U367|CSV primaire obtenu séparément/testé|D5|curl a réussi après timeout Python ;16923lignes,DGS10, pas de vintages.
U368|inaccessible|D5|SEC recherche403 ; pas de découverte d'entités par cet écran.
U369|réponse JSON primaire parsée/testée|D5|AppleCIK320193, revenusannuels24lignes/10fins,8groupesmultidépôts, valeursidentiques danscesgroupes.
"""

def build():
    inv = {x["id"]: x for x in json.loads((BASE/"inventaire_urls.json").read_text())}
    records=[]
    for line in ANNOTATIONS.strip().splitlines():
        uid,level,decision,note=line.split("|",3)
        item=inv[uid]
        meta=json.loads((BASE/"collecte"/(uid+".json")).read_text())
        records.append({"id":uid,"url":item["url"],"reading_level_this_cycle":level,
                        "decision":decision,"review_note":note,
                        "source_lines":[o["line"] for o in item["occurrences"]
                                        if o["file"].endswith("00_prompt2_et_dossier_fourni.md")],
                        "retrieval_status":meta.get("status",meta.get("error")),
                        "sha256":meta.get("sha256"),"retrieved_at":meta.get("retrieved_at")})
    required={uid for uid,item in inv.items() if any(o["section"].startswith(("9.2","9.3","9.7"))
                                                  for o in item["occurrences"])}
    assert required <= {r["id"] for r in records}, required-{r["id"] for r in records}
    (HERE/"registre_urls.json").write_text(json.dumps(records,indent=2,ensure_ascii=False))
    lines=["# Registre de lecture financière", "",
           "15 novembre 2026. Audit de toutes les URL des §9.2, 9.3 et 9.7, plus systèmes pertinents et sources du notebook.",
           "Les niveaux ci-dessous sont ceux de ce cycle. Une notice, un abstract, un document téléchargé et un code testé sont distincts.",
           "Les titres/auteurs complets sont dans le dossier fourni ; les précisions de version et contradictions sont explicitées ici.",
           "Métadonnées de transport et SHA complets : `registre_urls.json`, cache commun et `sources/*.json`.",
           "Une réponse HTTP200 peut être une coquille, une prévisualisation, un challenge ou une autre page : voir U033/U281/U288/U295.",
           "", "| ID / lien | Lecture effective | Décision / passage / influence / limite |",
           "|---|---|---|"]
    for r in sorted(records,key=lambda r:r["id"]):
        lines.append(f"| [{r['id']}]({r['url']}) | {r['reading_level_this_cycle']} | **{r['decision']}** — {r['review_note']} |")
    (HERE/"03_registre_sources.md").write_text("\n".join(lines)+"\n")
    print(f"{len(records)} URL annotées ; couverture des {len(required)} URL des trois sections vérifiée.")

if __name__=="__main__": build()
