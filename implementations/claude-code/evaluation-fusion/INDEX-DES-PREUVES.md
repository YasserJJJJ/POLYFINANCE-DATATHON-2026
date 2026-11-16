> **Annexe détaillée**, rédigée le 15 novembre 2026 pour une première archive. Les sections 4 à 9 de la présentation, les dépendances, la reproduction et l'index des preuves n'ont pas été contre-vérifiés par un second lecteur. Le `MANIFESTE.json` cité ici est celui de la racine de cette archive ; `runs/_archives/`, `inventaire/`, `outils/`, `CAPACITES.csv`, `docs/etat.md`, `docs/coordination.md`, `research/R08-…` et `research/fiches/` ne sont pas joints. En cas de désaccord, le code puis `LIRE_EN_PREMIER.md` priment.

## Index des preuves

Cet index relie chaque contribution de `evaluation-fusion/CAPACITES.json` (X-CAP-001 à X-CAP-077) à la pièce qui la fonde et dit de quelle nature est cette pièce. Les chemins sont relatifs à la racine du dépôt. Chaque chemin cité ici a été contrôlé par `ls` ou `grep` le 15 novembre 2026 ; les numéros de ligne des fichiers de `src/datathon2026/` ont été confrontés aux définitions (`grep -n "^def \|^class "`). Les cinq états (Proposé, Conçu, Implémenté, Exécuté, Vérifié) décrivent ce qui est établi ; ils ne notent pas la qualité.

### 1. Nature des preuves

| Catégorie | Où | Ce qu'elle prouve | Ce qu'elle ne prouve pas |
|---|---|---|---|
| Code source | `src/datathon2026/`, `scripts/`, `config/` | Que le mécanisme est écrit (état Implémenté). | Qu'il a tourné, ni qu'il produit un résultat juste. |
| Test automatisé | `tests/*.py` (43 fonctions, 51 cas après paramétrage) | Le critère écrit dans le test, sur les entrées du test. Les tests de l'agent emploient un client Bedrock simulé (`tests/test_agent.py::FakeBedrock`). | La qualité du texte produit, le comportement du modèle réel, l'appel réel à AWS. |
| Sortie de commande observée le 15 novembre | `evaluation-fusion/preuves/*.txt` | Qu'une commande a rendu ce résultat ce jour-là, sur cette machine. | La reproductibilité ailleurs ; pour l'agent, la stabilité d'une exécution à l'autre. |
| Dossier produit enregistré | `runs/*/dossier.json`, `runs/_archives/*/dossier.json`, `evaluation-fusion/preuves/execution-agent-2026-11-15/dossier.json` | Qu'une exécution a eu lieu, avec sa trace d'outils, ses enregistrements et, en mode agent, ses identifiants de requête AWS. `verification.ok` prouve que les textes passent le contrôle déterministe. | Que les affirmations sont pertinentes ou complètes. Le vérificateur contrôle le lien entre texte et enregistrements, pas le raisonnement. |
| Sortie d'expérience | `research/experiences/sorties/`, `research/experiences/technique/*/sorties/` | Un résultat chiffré obtenu hors produit, par un script conservé. | Que le produit emploie la méthode. Aucune de ces sorties n'a été relancée le 15 novembre à 17 h 50, sauf le prototype de dossier. |
| Document de conception | `docs/refonte/architecture/00-synthese.md` à `10-pratiques-observees.md` | Qu'un contrat ou une architecture est décrit (état Conçu ou Proposé). | Aucun fonctionnement. |
| Document de recherche | `docs/refonte/*.md`, `research/R07` à `R09`, `research/fiches/` | Qu'une lecture, une vérification ou une critique a été faite et consignée. | La justesse des conclusions au-delà des sources lues. |
| Source externe consignée | `research/sources/manifeste.json`, `manifeste-pratiques.json`, `research/R07-registre-des-sources-2026-11-15.md` | L'existence d'une référence, avec empreinte du texte téléchargé. | Le contenu : les textes eux-mêmes ne sont pas dans l'archive (section 7). |

### 2. Vérifications du 15 novembre 2026 (17 h 50 à 17 h 55)

Fait observé : `evaluation-fusion/preuves/horodatage.txt` contient `2026-11-15 17:50:11`. Les fichiers `.txt` ne portent pas la commande, sauf `demo.txt` et `agent-robert.txt` (ligne de chronométrage du shell). Les autres commandes sont déduites des chemins de sortie et de `src/datathon2026/cli.py::main` ; elles sont marquées « déduite ».

| Commande | Fichier de preuve (`evaluation-fusion/preuves/`) | Résultat observé, recopié du fichier | Ce que cela établit |
|---|---|---|---|
| `uv run pytest -q` (déduite) | `pytest.txt` | `51 passed in 1.67s` | Les critères des tests de `tests/` sont tenus. Rien sur AWS ni sur le modèle réel. |
| `uv run alphaforge demo tous --sortie /tmp/af_eval/runs_demo` | `demo.txt` | `robert-tsla (workflow fixe) : 15 affirmations, 52 valeurs reliées, 0 en échec` ; `amira-croissance (workflow fixe) : 18 affirmations, 51 valeurs reliées, 0 en échec` ; `0.562 total` | L'enchaînement fixe s'exécute sans AWS et ses deux dossiers passent le vérificateur. |
| `uv run alphaforge rendre --sortie /tmp/af_eval/runs_copie` (déduite) | `rendre.txt` | Huit lignes, une par dossier de `runs/`, toutes `0 en échec` (affirmations : 17, 18, 18, 16, 18, 12, 16, 15) | Les huit dossiers enregistrés se rechargent et repassent le vérificateur hors ligne, sur une copie. |
| `uv run alphaforge aws-verifier` (déduite) | `aws-verifier.txt` | `Profil AWS utilisé : alphaforge` ; `compte …1226, région us-east-1` ; `Profil d'inférence global.anthropic.claude-sonnet-5-5 : ACTIVE ; destinations : , us-east-1` | L'accès en lecture au compte et l'état actif du profil d'inférence par défaut. Aucun appel de modèle. |
| `uv run alphaforge agent robert --sortie /tmp/af_eval/runs_agent` | `agent-robert.txt` | `robert-agent (agent Bedrock (global.anthropic.claude-sonnet-5-5)) : 22 affirmations, 97 valeurs reliées, 0 en échec` ; `1:07.46 total` | Une exécution réelle de l'agent sur Amazon Bedrock aboutit à un dossier conforme au vérificateur. Une seule exécution. |
| Lecture du dossier ci-dessus (script non conservé) | `agent-robert-mesures.txt`, `execution-agent-2026-11-15/dossier.json` et `.html` | `appels 6 | jetons en entrée 72844 | jetons en sortie 12131 | latence cumulée (s) 66.2 | corrections demandées 1` ; onze appels d'outils dans la trace | Le coût et le déroulement de cette exécution. Le même fichier donne `runs/robert-agent` (5 appels, 18 affirmations) : deux exécutions de la même demande diffèrent. |
| `python3 research/experiences/technique/dossier_maison/essais.py` (déduite) | `prototype-dossier.txt` | `118 assertions réussies en 1.354 s (Python 3.12.7).` ; `paquet « prov » absent : relecture par un lecteur tiers non faite` | Le prototype hors produit du dossier (strate 3, conception) tient ses assertions sur une chaîne jouet, sans modèle. |
| `uv run python evaluation-fusion/outils/releves_de_preuve.py --demo /tmp/af_eval/runs_demo` (relevé de 18 h 20, lecture seule) | `demo-comparaison.txt` | `robert-tsla : 3964 valeurs feuilles enregistrées, 3964 relancées, 7 différentes` ; `amira-croissance : 1660 … 5 différentes` ; toutes sont `cree_le` ou des `duree_ms` | L'enchaînement fixe redonne les mêmes valeurs sur les mêmes données, hors date et durées. Rien sur l'agent. |
| même commande | `dossiers-d-agent.txt` | Dix dossiers d'agent (six dans `runs/`, trois dans `runs/_archives/`, un dans `preuves/`), tous `contrôle ok True` ; total sous `runs/` : 41 appels, 365737 jetons en entrée, 60614 en sortie | Les mesures par exécution relues dans les `dossier.json`. Aucun coût en dollars. |

Fait observé complémentaire, calculé pour cet index par comparaison feuille à feuille des JSON : `/tmp/af_eval/runs_demo/robert-tsla/dossier.json` et `runs/robert-tsla/dossier.json` comptent chacun 3 964 valeurs, dont 7 diffèrent (`cree_le` et six `duree_ms`) ; pour `amira-croissance`, 1 660 valeurs, dont 5 diffèrent (`cree_le` et quatre `duree_ms`). L'empreinte de `execution-agent-2026-11-15/dossier.json` est celle de `/tmp/af_eval/runs_agent/robert-agent/dossier.json`.

Non relancés dans cette fenêtre : l'application web, `scripts/comparer_agent_workflow.py`, les scripts de `research/experiences/` autres que le prototype de dossier.

### 3. Preuves par domaine

Abréviations : `src/` vaut `src/datathon2026/`. « Suite » renvoie à `evaluation-fusion/preuves/pytest.txt`. Colonne « Test » : nom de la fonction lue dans `tests/`. Colonne « Exécution » : dossier ou sortie qui montre le fonctionnement. Les éléments de la strate 3 portent la mention « conception ».

#### 3.1 Qualification de la demande et profilage

| Id | État | Preuve principale | Test | Exécution |
|---|---|---|---|---|
| X-CAP-001 | Exécuté | `src/datathon2026/tools.py::profile_facts` (l. 96) ; `config/personas.toml` | Aucun test nommé ; indirect : `test_workflow.py::test_dossier_passes_verification_and_renders`, `test_data.py::test_personas_load` | `runs/robert-agent/dossier.json` (`trace[0]`) |
| X-CAP-002 | Exécuté | `src/datathon2026/agent.py::BedrockAgent.run` (l. 191) ; `src/datathon2026/app.py::build_scenario` (l. 39) | Aucun sur le message initial ; `test_app.py::test_bootstrap_reads_config_and_excludes_held_assets` pour la configuration | `runs/robert-agent/`, `runs/mateo-libre-esg/` |
| X-CAP-003 | Vérifié (hors produit) | `research/experiences/modele_qualification_et_citations.py` | Rien (script à critères, hors pytest) | `research/experiences/sorties/m2_citations.txt` (« 81 sur 81 », « 10 sur 10 »), `m1_qualification.json` (40 entrées) |

#### 3.2 Recherche, littérature et sélection des preuves

| Id | État | Preuve principale | Test | Exécution |
|---|---|---|---|---|
| X-CAP-004 | Exécuté (hors produit) | `research/R07-registre-des-sources-2026-11-15.md`, section « Décompte » ; `research/outils/recherche_web.py`, `consolider_recherche.py` | Rien | `research/outils/journal_recherches.jsonl` ; `research/fiches/verif-*.json`, `critique-ensemble.json` |
| X-CAP-005 | Conçu | `docs/refonte/recherche-processus-professionnels.md` ; `docs/refonte/revue-par-questions.md` ; `docs/refonte/fiches-des-agents.md` | Rien | Rien |
| X-CAP-006 | Conçu (conception) | `docs/refonte/architecture/03-contrats-des-agents.md`, « Agent 1 — Recherche critique » ; `09-reception.md`, section E | Rien | Essai voisin seulement : `research/experiences/technique/services_aws/sorties/essai4.txt` |

#### 3.3 Analyse financière, formulation et calcul

| Id | État | Preuve principale | Test | Exécution |
|---|---|---|---|---|
| X-CAP-007 | Vérifié | `src/datathon2026/agent.py:48-96` (schémas d'outils), `::_run_tool` (l. 146) ; `src/datathon2026/tools.py` | `test_agent.py` (quatre fonctions, client simulé) ; `test_workflow.py::test_robert_flip_point_is_consistent` | Suite ; traces de `runs/*/dossier.json` |
| X-CAP-008 | Exécuté | `src/datathon2026/agent.py::SYSTEM` (l. 98-127) | Aucun | `runs/robert-agent/`, `runs/mateo-libre-esg/` (section cadre) |
| X-CAP-009 | Vérifié | `src/datathon2026/analytics.py::Market.__init__` (l. 46-74) | `test_analytics.py::test_weekly_grid_neutralises_holidays` | Suite |
| X-CAP-010 | Exécuté | `src/datathon2026/analytics.py::total_return`, `::cagr`, `::period_return` | Aucun test nommé | `runs/robert-tsla/dossier.json` |
| X-CAP-011 | Exécuté | `src/datathon2026/analytics.py::annual_vol` ; `src/datathon2026/tools.py::correlation` (l. 277) | Aucun test nommé | `runs/amira-croissance/dossier.json` (R-0030) |
| X-CAP-012 | Vérifié | `src/datathon2026/analytics.py::max_drawdown` (l. 114) | `test_analytics.py::test_max_drawdown_known_path`, `::test_max_drawdown_without_recovery` | Suite |
| X-CAP-013 | Vérifié | `src/datathon2026/analytics.py::worst_window` (l. 141) | `test_analytics.py::test_worst_window_counts_independent_windows` | Suite ; `runs/robert-tsla/dossier.json` (D-0005) |
| X-CAP-014 | Vérifié | `src/datathon2026/analytics.py::portfolio` (l. 168), `::blend` (l. 192) | `test_analytics.py::test_risk_contributions_sum_to_one`, `::test_portfolio_rejects_leverage`, `::test_blend_keeps_total` | Suite |
| X-CAP-015 | Vérifié | `src/datathon2026/tools.py::share_sweep` (l. 211) | `test_workflow.py::test_robert_flip_point_is_consistent`, `::test_changing_a_hypothesis_changes_the_conclusion` | Suite ; `runs/robert-tsla/dossier.json` (R-0123) |
| X-CAP-016 | Vérifié | `src/datathon2026/tools.py::diversification_sweep` (l. 234) | `test_workflow.py::test_amira_variant_respects_cap` | Suite ; `runs/amira-croissance/` |
| X-CAP-017 | Vérifié | `src/datathon2026/tools.py::Session.call` (l. 45), `::_weights` (l. 64) ; `src/datathon2026/analytics.py::Market.check_tickers` | `test_workflow.py::test_tools_reject_invalid_inputs_instead_of_returning_an_empty_result` | Suite |
| X-CAP-018 | Vérifié (hors produit) | `research/experiences/methodes_analyse.py` (critère X1 en en-tête) | Rien | `research/experiences/sorties/methodes_analyse.txt`, bloc X1 ; `multivers_exploratoire.json` |
| X-CAP-019 | Vérifié (hors produit) | idem, critère X3 | Rien | `methodes_analyse.txt`, blocs X3 et X3 bis ; `ecart_et_niveau.txt` |
| X-CAP-020 | Vérifié (hors produit) | idem, critère X4 | Rien | `methodes_analyse.txt`, blocs X4 et X4 bis ; `dossier_illustratif.txt` |
| X-CAP-021 | Vérifié (hors produit) | `research/experiences/calibration_reechantillonnage.py` (critère X8) | Rien | `research/experiences/sorties/calibration_reechantillonnage.txt` ; `methodes_analyse.txt`, bloc X6 |
| X-CAP-022 | Exécuté (hors produit) | `research/experiences/rendement_d_equilibre.py` | Rien | `research/experiences/sorties/rendement_d_equilibre.txt` |
| X-CAP-023 | Vérifié (hors produit) | `research/experiences/methodes_analyse.py` (critères X2, X5) | Rien | `methodes_analyse.txt`, blocs X2, X5, X5 bis |
| X-CAP-024 | Exécuté (hors produit) | `research/experiences/parcours_contraste.py` | Rien | `research/experiences/sorties/parcours_contraste.txt` |
| X-CAP-025 | Conçu (conception) | `docs/refonte/architecture/05-types-de-resultats.md` ; `09-reception.md`, section D | Rien | Rien |

#### 3.4 Contradictions, critique et validation

| Id | État | Preuve principale | Test | Exécution |
|---|---|---|---|---|
| X-CAP-026 | Vérifié | `src/datathon2026/agent.py:213-224` ; `MAX_FIXES` (l. 28) | `test_agent.py::test_agent_loop_runs_tools_rejects_handwritten_number_then_accepts`, `::test_agent_presentation_is_checked_then_rendered` | Suite ; `aws.corrections_demandees` des dossiers (section 4) |
| X-CAP-027 | Exécuté | `scripts/comparer_agent_workflow.py` | Aucun | `docs/comparaison-agent-workflow.md` ; réserve dans `docs/decisions.md`, « Rectifications du 15 novembre » |
| X-CAP-028 | Vérifié | `src/datathon2026/evidence.py::check_template` (l. 273), `::verify_claims` (l. 337), `::handwritten_comparisons` (l. 78) | `test_evidence.py::test_handwritten_number_is_flagged`, `::test_quantity_written_in_words_is_flagged_but_a_plain_count_is_not`, `::test_year_allowed_only_if_in_cited_record`, `::test_unknown_and_malformed_references_are_flagged`, `::test_handwritten_comparison_is_flagged_except_in_hypothetical_sections` | Suite ; `rendre.txt` |
| X-CAP-029 | Exécuté (recherche) | `docs/refonte/diagnostic-et-contrat.md` ; `docs/refonte/calcul_exploratoire.py` | Rien | Aucune sortie enregistrée de `calcul_exploratoire.py` trouvée sous son nom |
| X-CAP-030 | Exécuté (hors produit) | `research/experiences/multivers_exploratoire.py` ; `ecart_et_niveau.py` | Rien | `research/experiences/sorties/multivers_exploratoire.json` (clés `E1_graines` à `E4_multivers`) ; `ecart_et_niveau.txt` |
| X-CAP-031 | Exécuté (hors produit) | `research/experiences/dossier_illustratif.py` | Rien | `research/experiences/sorties/dossier_illustratif.txt` ; `ecart_et_niveau.txt` |
| X-CAP-032 | Conçu (conception) | `docs/refonte/architecture/03-contrats-des-agents.md`, « Le contradicteur… » ; `04-graphes-et-revision.md`, section 4 | Rien | Rien |
| X-CAP-033 | Conçu (conception) | `docs/refonte/architecture/09-reception.md`, sections A à K | Rien | Rien : critères écrits pour une implémentation qui n'existe pas |

#### 3.5 Orchestration, agents et outils

| Id | État | Preuve principale | Test | Exécution |
|---|---|---|---|---|
| X-CAP-034 | Vérifié (boucle, client simulé) ; Exécuté (appel réel) | `src/datathon2026/agent.py::BedrockAgent` (l. 136-239) | `test_agent.py::test_agent_loop_runs_tools_rejects_handwritten_number_then_accepts` | `agent-robert.txt` ; `execution-agent-2026-11-15/dossier.json` ; six dossiers d'agent de `runs/` |
| X-CAP-035 | Vérifié | `src/datathon2026/agent.py:225-231` | `test_agent.py::test_tool_error_is_returned_not_raised` | `runs/robert-libre-gamestop/dossier.json` (ligne de trace avec `erreur`) |
| X-CAP-036 | Vérifié | `src/datathon2026/workflow.py::robert` (l. 42), `::amira` (l. 128) | `test_workflow.py::test_dossier_passes_verification_and_renders`, `::test_changing_a_hypothesis_changes_the_conclusion` | `demo.txt` ; `runs/robert-tsla/`, `runs/amira-croissance/` |
| X-CAP-037 | Exécuté | `src/datathon2026/cli.py::run_agent` (l. 46), `::main` (l. 121) ; `src/datathon2026/app.py::produce` (l. 81) | Partiel : `test_app.py::test_invalid_inputs_give_readable_errors` (refus du mode de référence pour Mateo) | Champ `mode` des dossiers de `runs/` |
| X-CAP-038 | Exécuté (hors produit) | `research/experiences/technique/langgraph/LISEZMOI.md` ; `essai01` à `essai11` | Rien | `research/experiences/technique/langgraph/sorties/essai04_sortie.txt`, `essai06_sortie.txt`, `essai08_sortie.txt` |
| X-CAP-039 | Proposé (conception) | `docs/refonte/architecture/02-dossier.md`, « Le catalogue… » (l. 66) ; `01-resolutions.md`, section 8 | Rien | Rien : le catalogue n'est pas écrit |
| X-CAP-040 | Conçu (conception) | `docs/refonte/architecture/03-contrats-des-agents.md` | Rien | Rien |
| X-CAP-041 | Conçu (conception) | `docs/refonte/architecture/04-graphes-et-revision.md` ; `08-schemas.md`, section 2 | Rien | Prototype seulement : `prototype-dossier.txt`, essai (a) |
| X-CAP-042 | Conçu (conception) | `docs/refonte/architecture/04-graphes-et-revision.md`, section 5 | Rien | Prototype seulement : `research/experiences/technique/dossier_maison/dossier.py` |

#### 3.6 Dossier, mémoire, provenance et versionnement

| Id | État | Preuve principale | Test | Exécution |
|---|---|---|---|---|
| X-CAP-043 | Vérifié | `src/datathon2026/agent.py::BedrockAgent._build` (l. 242), `::_chart` (l. 276) | `test_agent.py::test_agent_presentation_is_checked_then_rendered` | `runs/robert-agent/dossier.json` (`chiffres_cles`, `tableaux`, `graphiques`) |
| X-CAP-044 | Vérifié (trace) ; Implémenté (`_strip`) | `src/datathon2026/tools.py::Session` (l. 28) ; `src/datathon2026/agent.py::_strip` (l. 130) | `test_agent.py` : assertions sur `d.trace[0]["outil"]` seulement | Clé `trace` des dossiers de `runs/` |
| X-CAP-045 | Vérifié | `src/datathon2026/evidence.py::format_value` (l. 167), `::Registry.render` (l. 254) | `test_evidence.py::test_clean_template_passes_and_renders`, `::test_formatting` | Suite |
| X-CAP-046 | Vérifié | `src/datathon2026/evidence.py::comparison_word` (l. 96), `CMP_EXPR` (l. 39) ; `src/datathon2026/report.py::_cmp_word` | `test_evidence.py::test_comparison_direction_is_computed`, `::test_duration_comparison_is_graded_on_the_ratio`, `::test_comparison_between_incompatible_units_is_invalid` | Suite |
| X-CAP-047 | Vérifié | `src/datathon2026/evidence.py::join_comparison` (l. 133) | `test_evidence.py::test_computed_comparison_agrees_with_the_following_word`, `::test_computed_comparison_agrees_in_gender_with_the_qualified_noun` | Suite |
| X-CAP-048 | Vérifié | `src/datathon2026/evidence.py::Claim.status` (l. 321), `STATUS_ORDER` (l. 17) | `test_evidence.py::test_claim_status_is_weakest_reference_and_unsupported_claim_flagged`, `::test_status_inherits_hypothesis_dependencies` | Suite |
| X-CAP-049 | Exécuté | `src/datathon2026/dossier.py::Dossier._display_claims` (l. 53), `::verification` (l. 66) | Partiel : `test_agent.py::test_agent_presentation_is_checked_then_rendered` (refus d'un résumé et d'un chiffre clé fautifs) | `verification.elements_verifies` des dossiers de `runs/` |
| X-CAP-050 | Vérifié | `src/datathon2026/dossier.py::Dossier.to_dict` (l. 75), `::from_dict` (l. 107) | `test_workflow.py::test_saved_dossier_can_be_reloaded_and_reverified_offline` | `rendre.txt` |
| X-CAP-051 | Exécuté | `src/datathon2026/cli.py::rerender` (l. 77) | Aucun sur la commande ; le rechargement est couvert par le test ci-dessus | `rendre.txt` |
| X-CAP-052 | Proposé | `runs/_archives/` (trois dossiers) ; `.gitignore:26` | Rien | Rien : pratique manuelle, sans code |
| X-CAP-053 | Proposé | `docs/one-pager.md`, `docs/video.md` (dix lignes chacun, titres seulement) | Rien | Rien |
| X-CAP-054 | Vérifié (prototype hors produit, conception) | `research/experiences/technique/dossier_maison/dossier.py`, `essais.py` | Rien dans pytest ; assertions internes du script | `prototype-dossier.txt` ; `research/experiences/technique/dossier_maison/sorties/essais.txt` |
| X-CAP-055 | Conçu (conception) | `docs/refonte/architecture/02-dossier.md`, sections 1 à 8 | Rien | Rien dans le produit ; voir X-CAP-054 |

#### 3.7 Interface, adaptation, visualisation et réversibilité

| Id | État | Preuve principale | Test | Exécution |
|---|---|---|---|---|
| X-CAP-056 | Exécuté | `src/datathon2026/report.py::render` (l. 482), `::render_html` (l. 69) | Partiel : `test_workflow.py::test_dossier_passes_verification_and_renders` (absence de `class="bad"`) | `runs/*/dossier.html`, `runs/index.html` |
| X-CAP-057 | Exécuté | `src/datathon2026/report.py::line_chart` (l. 138), `::bar_chart` (l. 194) | Partiel : `test_agent.py::test_agent_presentation_is_checked_then_rendered` (« Graphique 1 » présent) | Clé `graphiques` de `runs/robert-tsla/dossier.json` |
| X-CAP-058 | Vérifié | `src/datathon2026/app.py::build_scenario`, `::produce`, `::Handler` (l. 310) | `test_app.py::test_bootstrap_reads_config_and_excludes_held_assets`, `::test_changing_a_hypothesis_recomputes_the_dossier`, `::test_other_asset_and_amira_cap_run` | Suite. Serveur non relancé à 17 h 50 ; `docs/etat.md:63` rapporte un essai du matin, sans fichier de sortie |
| X-CAP-059 | Implémenté | `src/datathon2026/app.py:264-289` (code de la page) | Aucun | Rien |
| X-CAP-060 | Exécuté (déclaré) | `src/datathon2026/app.py:89-98` | Aucun | Déclaration de `docs/etat.md:63` seulement ; aucun fichier de sortie |
| X-CAP-061 | Vérifié | `src/datathon2026/app.py::_float` (l. 29), `::_explain` (l. 344) ; `src/datathon2026/cli.py::AWS_HELP` (l. 13) | `test_app.py::test_invalid_inputs_give_readable_errors` (sept cas) | Suite |
| X-CAP-062 | Exécuté | `src/datathon2026/cli.py::main` (l. 121) ; `pyproject.toml:13-14` | Aucun fichier de test sur `cli.py` | `demo.txt`, `rendre.txt`, `aws-verifier.txt`, `agent-robert.txt` |
| X-CAP-063 | Conçu (conception) | `docs/refonte/architecture/02-dossier.md`, sections 6 et 7 | Rien | Prototype seulement : `prototype-dossier.txt`, essais (b), (e), (g) |

#### 3.8 Données, ingestion et cohérence temporelle

| Id | État | Preuve principale | Test | Exécution |
|---|---|---|---|---|
| X-CAP-064 | Vérifié | `src/datathon2026/analytics.py::Market.__init__` (l. 46-74) | `test_analytics.py::test_weekly_cad_return_matches_usd_return_times_fx` | Suite ; `runs/robert-tsla/dossier.json` (D-0004, D-0005) |
| X-CAP-065 | Vérifié | `src/datathon2026/data.py::convert_currency` (l. 71), `::load_prices` ; `src/datathon2026/paths.py` | `test_data.py` (sept fonctions, dont `::test_convert_to_cad_uses_same_day_rate_and_carries_forward`, `::test_wide_table_has_no_fill`) | Suite |
| X-CAP-066 | Exécuté | `src/datathon2026/tools.py::data_manifest` (l. 75) | Partiel : `test_agent.py::test_agent_exposes_data_provenance_tool` (outil exposé, D-0005 et D-0006 citables) | `runs/robert-tsla/dossier.json` (D-0001 à D-0006) |
| X-CAP-067 | Exécuté | `src/datathon2026/evidence.py::Record` (l. 194), `::Registry` (l. 219) | Indirect : tous les tests de `test_evidence.py` | Clé `enregistrements` de `runs/robert-tsla/dossier.json` (123 R, 17 P, 6 D) |
| X-CAP-068 | Exécuté (hors produit) | `research/outils/consolider_recherche.py`, `recherche_web.py`, `schema_architecture.py` | Rien | `research/sources/manifeste.json`, `manifeste-pratiques.json` ; `docs/refonte/architecture/schemas/*.svg` |

#### 3.9 AWS, déploiement, exploitation et reprise

| Id | État | Preuve principale | Test | Exécution |
|---|---|---|---|---|
| X-CAP-069 | Vérifié (journal, client simulé) ; Exécuté (appel réel) | `src/datathon2026/agent.py::BedrockAgent._converse` (l. 172) | `test_agent.py::test_agent_loop_runs_tools_rejects_handwritten_number_then_accepts` (liste des `requestId`) | Clé `aws.appels` des dossiers d'agent ; `agent-robert-mesures.txt` |
| X-CAP-070 | Exécuté | `src/datathon2026/agent.py:237-238` ; `src/datathon2026/report.py:505-519` | Partiel : voir X-CAP-066 et X-CAP-069 | `runs/robert-agent/dossier.json` (`aws`) ; `runs/robert-tsla/dossier.json` (D-0001, champ `sha256`) |
| X-CAP-071 | Vérifié (boucle, client simulé) ; Exécuté (Bedrock réel) | `src/datathon2026/agent.py::aws_session` (l. 38), `::_converse` | `test_agent.py` (quatre fonctions, aucune ne touche AWS) | `agent-robert.txt` ; six dossiers d'agent de `runs/` et trois de `runs/_archives/` |
| X-CAP-072 | Exécuté | `src/datathon2026/cli.py::aws_check` (l. 86) | Aucun | `aws-verifier.txt` |
| X-CAP-073 | Exécuté | `src/datathon2026/agent.py:22-26`, `::aws_session` ; `docs/acces-aws.md` | Aucun | Indirect : `aws-verifier.txt` (`Profil AWS utilisé : alphaforge`) |
| X-CAP-074 | Exécuté (outil de développement, hors produit livré) | `scripts/claude-bedrock.sh` ; `scripts/message-reprise.txt` | Aucun | Déclaration de `research/R08-outils-routes-et-ressources-2026-11-15.md`, section 1 ; aucun fichier de sortie |
| X-CAP-075 | Exécuté (hors produit) | `research/experiences/technique/strands/LISEZMOI.md` ; `essai1` à `essai9` | Rien | `research/experiences/technique/strands/sorties/essai3.txt`, `essai4.txt`, `essai8b_b.txt` |
| X-CAP-076 | Exécuté (hors produit) | `research/experiences/technique/services_aws/LISEZMOI.md` ; `services_produit.py` | Rien | `research/experiences/technique/services_aws/sorties/essai3.txt`, `essai4.txt`, `essai5.txt` |

#### 3.10 Prompts, contrats de sortie et gestion du contexte

| Id | État | Preuve principale | Test | Exécution |
|---|---|---|---|---|
| X-CAP-077 | Exécuté | `src/datathon2026/agent.py::SYSTEM` (l. 98-127) ; `::_converse` (l. 172) | Aucun : le client simulé ne dépend pas de l'instruction | Six dossiers d'agent de `runs/` ; `execution-agent-2026-11-15/dossier.json`. Aucune évaluation du prompt à critère écrit d'avance |

### 4. Dossiers produits enregistrés

Tableau établi par un script Python en lecture seule sur chaque `dossier.json` (clés `mode`, `persona`, `aws`, `affirmations`, `verification`, `trace`). Jetons : somme de `inputTokens` et de `outputTokens` sur `aws.appels`. Tous les dossiers d'agent indiquent le modèle `global.anthropic.claude-sonnet-5-5`, la région `us-east-1` et un `requestId` par appel.

| Dossier | Mode | Profil | Affirmations | Valeurs reliées | `verification.ok` | Appels Bedrock | Jetons entrée / sortie | Corrections | Outils dans la trace |
|---|---|---|---|---|---|---|---|---|---|
| `runs/robert-tsla` | enchaînement fixe | robert | 15 | 52 | True | 0 | sans objet | sans objet | 9 |
| `runs/amira-croissance` | enchaînement fixe | amira | 18 | 51 | True | 0 | sans objet | sans objet | 6 |
| `runs/robert-agent` | agent | robert | 18 | 68 | True | 5 | 57 162 / 10 098 | 1 | 11 |
| `runs/amira-agent` | agent | amira | 17 | 59 | True | 5 | 48 997 / 8 489 | 1 | 5 |
| `runs/amira-libre-bitcoin-or` | agent, demande libre | amira | 18 | 50 | True | 4 | 33 773 / 7 102 | 1 | 6 |
| `runs/mateo-libre-esg` | agent, demande libre | mateo | 16 | 50 | True | 4 | 32 618 / 6 480 | 1 | 5 |
| `runs/robert-libre-gamestop` | agent, demande libre | robert | 12 | 24 | True | 3 | 19 559 / 2 255 | 0 | 3, dont 1 en erreur |
| `runs/robert-libre-or` | agent, demande libre | robert | 16 | 56 | True | 5 | 46 103 / 7 394 | 1 | 8 |
| `runs/_archives/robert-agent-2026-11-15-avant-corrections` | agent | robert | 21 | 69 | True | 5 | 41 145 / 5 511 | 0 | 10 |
| `runs/_archives/robert-agent-2026-11-15-0642-avant-garde-lexicale` | agent | robert | 24 | 91 | True | 6 | 60 374 / 9 344 | 1 | 11 |
| `runs/_archives/amira-agent-2026-11-15-0646-avant-garde-lexicale` | agent | amira | 18 | 72 | True | 4 | 26 006 / 3 941 | 0 | 4 |
| `evaluation-fusion/preuves/execution-agent-2026-11-15` | agent (17 h 51) | robert | 22 | 97 | True | 6 | 72 844 / 12 131 | 1 | 11 |

Lecture, à tenir pour une interprétation : `verification.ok` vaut True partout parce que la boucle ne rend un dossier qu'après contrôle (`src/datathon2026/agent.py:213-224`) ; ce champ n'est donc pas une mesure de qualité. Cinq dossiers d'agent courants sur six ont demandé une correction. Les trois archives ont été produites par des versions antérieures du code ; leur `verification.ok` a été calculé à leur date, et `rendre.txt` ne les couvre pas.

### 5. Documents de conception et de recherche

| Chemin | Contenu | État |
|---|---|---|
| `docs/refonte/diagnostic-et-contrat.md` | Diagnostic du produit rôle par rôle, contrat de refonte | Recherche exécutée (lecture critique du code) |
| `docs/refonte/recherche-processus-professionnels.md` | Méthode de recherche, cartographie des fonctions, controverses, règles | Recherche exécutée |
| `docs/refonte/revue-par-questions.md`, `docs/refonte/fiches-des-agents.md` | Revue par questions ; fiches méthodologiques des quatre rôles | Conçu |
| `docs/refonte/calcul_exploratoire.py` | Calcul exploratoire du diagnostic (rééchantillonnage, trois profils) | Implémenté hors produit ; exécution rapportée dans le diagnostic |
| `docs/refonte/architecture/00-synthese.md` | Synthèse de l'architecture à quatre agents, décisions réservées au porteur, index des livrables | Conçu (conception), en attente de validation |
| `docs/refonte/architecture/01-resolutions.md` | Résolution des contradictions et lacunes ; ce qui reste ouvert | Conçu (conception) |
| `docs/refonte/architecture/02-dossier.md` | Contrat du dossier : pièces, journal, états, droits, catalogue | Conçu (conception) ; catalogue Proposé |
| `docs/refonte/architecture/03-contrats-des-agents.md` | Contrats des agents 0 à 3, contradicteur, fonctions d'organisation | Conçu (conception) |
| `docs/refonte/architecture/04-graphes-et-revision.md` | Quatre graphes, table de révision, sortie d'étude, reprise | Conçu (conception) |
| `docs/refonte/architecture/05-types-de-resultats.md` | Sept types de résultats, règle du sens établi | Conçu (conception) |
| `docs/refonte/architecture/06-comparatif-technique.md` | Options techniques, essais, choix proposé, briques candidates | Conçu (conception), appuyé sur des essais exécutés hors produit |
| `docs/refonte/architecture/07-dossier-illustratif.md` | Deux parcours rédigés à la main (Robert, Mateo), marqués illustratifs | Proposé (conception) : aucun agent ne les a produits |
| `docs/refonte/architecture/08-schemas.md`, `schemas/*.svg` | Trois schémas (ensemble, révision, états d'une pièce) | Conçu (conception) |
| `docs/refonte/architecture/09-reception.md` | Critères de réception A à K d'une implémentation future | Conçu (conception) ; aucun critère n'a été passé |
| `docs/refonte/architecture/10-pratiques-observees.md` | Pratiques observées, effets sur la conception, ce qui reste non observé | Recherche exécutée |
| `research/R07-registre-des-sources-2026-11-15.md` | Registre des sources, verdicts des vérificateurs | Recherche exécutée |
| `research/R08-outils-routes-et-ressources-2026-11-15.md` | Routes d'inférence, outils, ressources AWS, examen du notebook | Recherche exécutée ; les décomptes d'appels y sont déclarés, sans fichier brut joint |
| `research/R09-experiences-discriminantes-2026-11-15.md` | Expériences X1 à X8, M1, M2 et ajouts sans critère | Recherche exécutée ; sorties dans `research/experiences/sorties/` |
| `research/fiches/` (`recherche-*.json`, `verif-*.json`, `critique-ensemble.json`, `architecture/`, `redaction/`) | Fiches des chercheurs, des vérificateurs et des revues de la conception | Recherche exécutée |
| `docs/decisions.md`, `docs/etat.md`, `docs/technique.md` | Décisions D1 à D5 et rectifications ; état courant ; description technique du produit | Documents du produit ; les affirmations d'exécution y sont déclaratives |

### 6. Ce qui n'a pas de preuve d'exécution

- **Proposé** : X-CAP-039 (catalogue de règles, conception, non écrit) ; X-CAP-052 (archivage des dossiers, pratique manuelle sans code) ; X-CAP-053 (résumé d'une page et vidéo, fichiers réduits à des titres).
- **Conçu, sans exécution** : X-CAP-005, X-CAP-006, X-CAP-025, X-CAP-032, X-CAP-033, X-CAP-040, X-CAP-041, X-CAP-042, X-CAP-055, X-CAP-063. Tous relèvent de la conception, sauf X-CAP-005 (recherche). Pour X-CAP-041, X-CAP-042, X-CAP-055 et X-CAP-063, seul le prototype X-CAP-054 a tourné, sur une chaîne jouet sans modèle.
- **Implémenté, sans exécution observée** : X-CAP-059 (historique de séance de l'application). La fonction `_strip` de X-CAP-044 n'a pas de test propre.
- **Exécution déclarée, sans fichier de sortie** : X-CAP-060 (mode agent depuis l'application, `docs/etat.md:63`) ; X-CAP-074 (lanceur de développement, `research/R08`, section 1) ; le serveur de X-CAP-058 (tests seulement).
- **Exécuté une seule fois ou sans critère** : X-CAP-077 (aucune évaluation de l'instruction système) ; X-CAP-022, X-CAP-024, X-CAP-030, X-CAP-031 (sorties sans critère écrit d'avance) ; X-CAP-027 (la section « Lecture » de la comparaison est écrite en dur, selon `docs/decisions.md`, « Rectifications »).
- **Aucun agent 0, 1, 2 ou 3 de l'architecture cible n'a été exécuté.** Aucun critère de `09-reception.md` n'a été passé.

### 7. Preuves non incluses dans l'archive

D'après `evaluation-fusion/outils/preparer_archive.py` (liste `EXCLUSIONS`) et l'essai à blanc `evaluation-fusion/MANIFESTE.json`.

| Élément exclu | Volume dans l'essai à blanc | Motif | Comment le retrouver |
|---|---|---|---|
| Données du jeu de départ (`data/raw/alphaforge_starter/`) | 9 fichiers | Conditions de redistribution (`data/README.md`) | Copier le dossier remis aux participants dans `data/raw/` ; comparer aux empreintes de `MANIFESTE.json`, clé `donnees_non_incluses`. L'empreinte de `prices_daily.csv` figure aussi dans chaque dossier produit (enregistrement D-0001). |
| Textes de tiers (`research/sources/textes/`) | 2 047 fichiers | Aucun droit de redistribution | Références et empreintes dans `research/sources/manifeste.json` et `manifeste-pratiques.json` ; liste commentée dans `research/R07`. |
| Inventaire brut du compte AWS (`research/experiences/technique/services_aws/sorties/essai1*`) | 2 fichiers | Noms de ressources du compte de l'atelier | Résumé dans `research/experiences/technique/services_aws/LISEZMOI.md` ; relance par `essai1_inventaire.py` avec un accès au compte. |
| Historique git (`.git/`) | 29 fichiers | L'instantané est l'arbre de travail | Un seul commit, `55d164c` ; état décrit dans `MANIFESTE.json`, clé `instantane.git`. Le travail du 15 novembre n'est pas dans ce commit. |
| Environnement et caches (`.venv/`, `__pycache__/`) | 6 531 fichiers | Reconstructibles | `uv sync` (dépendances figées dans `uv.lock`). |
| Version locale de `scripts/configurer-aws-workshop.sh` | 1 fichier | Modifiée par une autre main, non relue ; remplacée par la version du commit | `git show HEAD:scripts/configurer-aws-workshop.sh`. |
| `.env`, `.claude/` | 1 fichier pour `.claude/` | Jamais lus ni copiés ; réglages locaux | Sans objet. |

Conséquences pour l'évaluateur : sans le jeu de départ, `uv run pytest` et `alphaforge demo` ne peuvent pas être relancés (les tests lisent les données réelles) ; sans accès AWS, `alphaforge agent` et `aws-verifier` non plus. `alphaforge rendre` reste possible sur les dossiers de `runs/`, qui sont inclus : la commande relit chaque `dossier.json` sans recalcul ni appel de modèle (`src/datathon2026/cli.py::rerender`, `docs/technique.md:23`). Réserve : l'essai à blanc du manifeste est daté de 17 h 54 min 19 s, avant l'écriture de `evaluation-fusion/preuves/` ; il ne liste aucun fichier de ce dossier et devra être régénéré.
