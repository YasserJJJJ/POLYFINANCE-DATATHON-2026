# R04 — Explications fidèles aux sorties d'outils ; précédents agentiques financiers

Recherche déléguée (sous-agent researcher), 2026-11-14. **Niveau d'accès : pages de résumé arXiv/Crossref ; aucun texte intégral lu.** Les mécanismes sont des inférences de l'équipe, pas des résultats publiés. Références non lues signalées.

## Constats sourcés

**Attribution et ancrage**
- AIS — Rashkin et al., [arXiv:2112.12870](https://arxiv.org/abs/2112.12870) (résumé) : cadre d'annotation humaine « attribuable à des sources identifiées » ; testé sur QA conversationnelle, résumé, table-vers-texte.
- ALCE — Gao et al. 2023, [arXiv:2305.14627](https://arxiv.org/abs/2305.14627) (résumé) : métriques automatiques de fluidité, justesse, qualité des citations ; même les meilleurs modèles manquent de support complet environ la moitié du temps sur ELI5 (selon le résumé).
- FActScore — Min et al. 2023, [arXiv:2305.14251](https://arxiv.org/abs/2305.14251) (résumé) : décomposition en faits atomiques, part soutenue par une source.
- RAGAS — Es et al., [arXiv:2309.15217](https://arxiv.org/abs/2309.15217) (résumé) : évaluation sans référence de la fidélité ; métriques exactes **non vérifiées**.

**Chiffres calculés par programme**
- PAL — Gao et al. 2022, [arXiv:2211.10435](https://arxiv.org/abs/2211.10435) (résumé) et Program of Thoughts — Chen et al., [arXiv:2211.12588](https://arxiv.org/abs/2211.12588) (résumé, inclut FinQA, ConvFinQA, TAT-QA) : déléguer le calcul à un interpréteur améliore la justesse.
- FinanceBench — Islam et al. 2023, [arXiv:2311.11944](https://arxiv.org/abs/2311.11944) (résumé) : taux élevé de réponses fausses ou refusées pour un LLM avec récupération sur documents financiers ; **périmètre exact du chiffre à confirmer dans le texte intégral**. Preuve indirecte (QA sur documents, pas arithmétique d'explications).

**Biais d'anticipation des LLM**
- Glasserman et Lin, [arXiv:2309.17322](https://arxiv.org/abs/2309.17322) (résumé) : sur le sentiment de titres, l'effet de distraction dépasse le biais d'anticipation.
- Lopez-Lira, Tang, Zhu, [arXiv:2504.14765](https://arxiv.org/abs/2504.14765) (**extrait de recherche seulement**) : les LLM mémorisent des valeurs économiques antérieures à leur coupure ; consignes et masquage insuffisants.
- Repérés, non lus : arXiv:2512.23847 ; arXiv:2605.24564 ; Somoza et al., Economics Letters 2025.

**Cadres agentiques financiers** (résumés) : FinRobot [arXiv:2405.14767](https://arxiv.org/abs/2405.14767), TradingAgents [arXiv:2412.20138](https://arxiv.org/abs/2412.20138), FinMem [arXiv:2311.13743](https://arxiv.org/abs/2311.13743), FinAgent [arXiv:2402.18485](https://arxiv.org/abs/2402.18485) — évalués sur la performance de trading, pas sur la fidélité des explications. Critiques repérées non lues : FINSABER ; arXiv:2605.16895.

**Compréhension du risque**
- Kaufmann, Weber, Haisley 2013, Management Science 59(2), [doi:10.1287/mnsc.1120.1607](https://doi.org/10.1287/mnsc.1120.1607) (référence vérifiée sur Crossref ; contenu par extraits) : l'expérience simulée modifie perception du risque et appétit — à interpréter prudemment.
- Bradbury, Hens, Zeisberger 2015, Review of Finance 19(3), [doi:10.1093/rof/rfu021](https://doi.org/10.1093/rof/rfu021) (référence vérifiée ; contenu par extraits) : l'expérience simulée améliore la compréhension rendement-risque.

## Mécanismes retenus pour le prototype (inférences)

1. **Aucun nombre libre** : l'agent écrit des références `{{R-0012.valeur}}` ; le code substitue la valeur calculée.
2. **Vérificateur déterministe après rédaction** : nombres orphelins, identifiants inexistants, tolérance d'arrondi explicite ; rejet puis régénération.
3. **Tests à fautes injectées** : chiffre modifié, identifiant inexistant, affirmation sans source → doivent être détectés.
4. **Narration limitée au registre** : aucune information externe hors registre ; « simulation, pas prévision ».
5. **Présentation du risque par scénarios historiques chiffrés** (pertes vécues, trajectoires), évaluée par questions de compréhension.

## Décision influencée

Q3 (carte des questions) : registre de résultats identifiés + gabarits + vérificateur déterministe. Distinction utile : les métriques d'attribution textuelles (AIS, ALCE) servent aux sources documentaires (ESG, méthodologies) ; pour les nombres calculés, un contrôle exact remplace un juge LLM.
