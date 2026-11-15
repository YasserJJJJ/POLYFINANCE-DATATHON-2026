# AlphaForge — Livrables du Prompt 2

**Revue du 15 novembre 2026.** Recherche professionnelle et scientifique, inspection de code et petites expériences isolées. Aucune nouvelle interface ni modification du produit.

## Point d’entrée

[**Synthèse, cartographie des fonctions et fonctionnement cible**](01_synthese_et_fonctionnement_cible.md)

La recommandation conserve les quatre agents distincts et un dossier révisable : qualification du besoin, recherche contradictoire, analyse vérifiée, puis restitution permettant de corriger la décision. Les méthodes restent des candidates soumises à leurs hypothèses et à une expérience d’admission.

| Livrable demandé | Où le lire |
|---|---|
| Cartographie professionnelle | Synthèse, section 3 |
| Revue structurée par questions et décisions | Synthèse, section 4 ; [finance](finance/01_revue_par_decision.md), [qualification/restitution](profil_restitution/05_questions_decisions.md), [orchestration](aws_agentique/02_orchestration_critique_et_contrats.md) |
| Fiche Agent 0 | [Qualification, mandat et clarification](profil_restitution/03_agent0.md) |
| Fiche Agent 1 | [Recherche, qualification et confrontation des preuves](methode_sources/01_fondements_et_agent1.md) |
| Fiche Agent 2 | [Analyse, résolution et validation](finance/02_fiche_agent2.md) |
| Fiche Agent 3 | [Restitution, compréhension et révision](profil_restitution/04_agent3.md) |
| Controverses et inconnues | Synthèse, section 8 ; limites explicites dans chaque fiche de source |
| Recommandation argumentée | Synthèse, sections 1, 7 et 9 |
| Journal des implémentations candidates | [18 familles de candidats et leurs expériences](03_journal_candidats.md), avec journaux détaillés liés |
| Ressources et fonctionnement vérifié | [Inventaire commun](02_inventaire_ressources.md), [preuves AWS](aws_agentique/01_preuves_aws_et_recherche.md), [134 liens d’atelier](aws_agentique/04_annexe_atelier_134.md) |
| Expériences réalisées | [Résultats, limites et audit des 35 cellules du notebook](finance/04_experiences_et_notebook.md) |

## Sources et niveau réel d’examen

Les **339 URL distinctes du dossier fourni** ont toutes un état de triage. Les **505 URL distinctes de l’inventaire élargi** ont aussi un rattachement ; ces nombres ne représentent pas des études indépendantes ni des textes intégralement lus. Les références sans URL, les accès refusés, les notices et les coquilles HTML restent visibles.

- [Dossier fourni, copie intégrale](00_prompt2_et_dossier_fourni.md)
- [Inventaire avec occurrences originales](inventaire_urls.json)
- [Registre finance : 133 URL](finance/03_registre_sources.md) et [textes approfondis/références sans URL](finance/06_sources_primaires_et_nv.md)
- [Registre qualification/restitution : 64 entrées du dossier](profil_restitution/01_triage_64_references.md) et [23 fiches décisives](profil_restitution/02_sources_decisives.md)
- [Registre AWS/agentique](aws_agentique/triage_sources.md), [code et ressources](aws_agentique/03_journal_implementations_et_ressources.md)
- [Fondements supplémentaires CFA, PRISMA-S, PRESS et E-23](methode_sources/01_fondements_et_agent1.md)

Les fiches décisives indiquent version, passages réellement lus, nature de preuve, méthode utilisée, hypothèses, limites, décision influencée et confrontation avec le dossier. Les copies tierces dans `collecte/` et `sources/` sont des pièces locales de recherche ; elles ne constituent pas une autorisation de redistribution.

## Vérification et reproduction

Les [scripts et protocoles financiers](finance/experiences/PROTOCOLE.md) s’exécutent dans un environnement isolé. Ils n’appellent aucun LLM et ne modifient pas les données d’origine. Leurs versions, graines, empreintes et résultats sont conservés.

Les [preuves de route des quatre sessions](verification_route_codex.json) déclarent `amazon-bedrock-runtime`. Le contrôle AWS signé et la recherche AgentCore réussie sont documentés séparément. Aucun service auxiliaire d’inférence n’a été ajouté.

Le [contrôle final de couverture et de fichiers](04_verification_livrables.json) rapproche les 339 URL du dossier et les 505 de l’inventaire, vérifie les liens locaux et confirme que les empreintes des données utilisées par les expériences correspondent toujours aux fichiers d’origine. Il ne transforme pas ce contrôle documentaire en validation scientifique.

Les résultats constituent des vérifications ciblées, pas une validation prospective du conseil financier, une étude utilisateur ou une conformité réglementaire. Les expériences proposées et les expériences déjà réalisées sont explicitement séparées.
