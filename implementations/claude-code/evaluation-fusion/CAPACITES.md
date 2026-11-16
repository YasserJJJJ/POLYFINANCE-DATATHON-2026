> **Annexe détaillée**, rédigée le 15 novembre 2026 pour une première archive. Les sections 4 à 9 de la présentation, les dépendances, la reproduction et l'index des preuves n'ont pas été contre-vérifiés par un second lecteur. Le `MANIFESTE.json` cité ici est celui de la racine de cette archive ; `runs/_archives/`, `inventaire/`, `outils/`, `CAPACITES.csv`, `docs/etat.md`, `docs/coordination.md`, `research/R08-…` et `research/fiches/` ne sont pas joints. En cas de désaccord, le code puis `LIRE_EN_PREMIER.md` priment.

# Inventaire détaillé des capacités et contributions

Réalisation : identifiant à attribuer. Le préfixe `X` des identifiants est à remplacer par la lettre attribuée.

Ce fichier est généré par `outils/assembler_capacites.py` à partir des relevés de `inventaire/`. Il donne, pour chaque contribution, les onze champs demandés. Les mêmes données sont dans `CAPACITES.json` et `CAPACITES.csv`.

États : Proposé : idée documentée. Conçu : contrats ou architecture décrits. Implémenté : code présent. Exécuté : fonctionnement observé, avec une trace. Vérifié : critères explicites et résultats disponibles. Ce n'est pas une note de qualité.

Trois strates, à ne pas confondre : le **produit implémenté** ; la **recherche et les expériences hors produit** ; l'**architecture cible conçue, non construite**.

## Qualification de la demande et profilage

### X-CAP-001 — Profils fictifs écrits d'avance et inscrits au registre (outil profile_facts)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Disposer des faits de profil (Amira, Mateo, Robert) sous une forme citable, en séparant ce qui est déclaré de ce qui est inconnu. |
| Valeur apportée | Chaque fait de profil devient un enregistrement P-xxxx avec statut ; trois inconnues sont toujours posées (capacité de perte, liquidité, patrimoine). |
| Fonctionnement | Les profils sont des tables statiques de config/personas.toml (nom, âge, profession, situation, expérience, profil_risque, horizon_ans, objectif, préférences, teste). tools.profile_facts (src/datathon2026/tools.py l.96-126) lit data.load_personas()[persona] et inscrit : prénom, âge, profil de risque, horizon (texte), objectif, expérience, horizon minimal (années), une ligne par préférence (statut « déclaré », source « énoncé, p. 5/6/7 »), trois enregistrements à valeur None de statut « inconnu », puis la demande et son origine (statut « scénario »). Aucune extraction de profil par un modèle, aucun profil saisi par l'utilisateur. |
| État | **Exécuté**. Code dans le produit ; appel visible dans la trace des trois dossiers inspectés (17 enregistrements par appel : runs/robert-agent/dossier.json, runs/mateo-libre-esg/dossier.json, runs/robert-tsla/dossier.json). Aucun test ne porte nommément sur profile_facts ; il n'est couvert qu'indirectement par tests/test_workflow.py::test_dossier_passes_verification_and_renders. |
| Entrées et sorties | Entrée : persona (amira|mateo|robert), scenario facultatif (dict avec demande et origine_demande). Sortie : dict clé → {id, valeur affichée}. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | config/personas.toml ; src/datathon2026/tools.py:96-126 (profile_facts) ; runs/robert-agent/dossier.json (trace[0], enregistrements P-0001…P-0017) |
| Dépendances | data.load_personas, evidence.Registry, config/personas.toml. |
| Limites | Les champs profession, situation et « teste » de personas.toml ne sont pas inscrits au registre (non lus par profile_facts). Persona hors des trois noms : KeyError. Si scenario est fourni sans clé origine_demande : KeyError (l.124). Avec BedrockAgent.run(request=…), l'enregistrement « Demande formulée » reprend scenario['demande'] et non le paramètre request (agent.py l.152, l.193). |
| Transférabilité | **Adaptable**. Fonction courte ; dépend du registre de preuves (préfixe P, statuts) et du format de personas.toml. |
| Inconnues | Aucune. |

### X-CAP-002 — Cadrage de la demande : aucun étage de qualification, un message initial et des hypothèses de démonstration

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Transformer une demande (scénario prédéfini ou texte libre) en entrée de l'agent. |
| Valeur apportée | Fait à établir pour la comparaison : la qualification n'existe pas comme composant ; elle se réduit au choix d'un des trois profils et à un texte de demande. |
| Fonctionnement | Scénario de démonstration : dict lu dans config/scenarios.toml (robert, amira ; aucun pour mateo) avec demande, origine, actif, parts, seuil, portefeuille, panier, plafond. Demande libre : cli.run_agent (src/datathon2026/cli.py l.55-56) et app.build_scenario/produce (src/datathon2026/app.py l.39-45, l.94-97) construisent {persona, demande, origine_demande: « demande libre saisie dans l'outil »}. BedrockAgent.run (agent.py l.191-200) forme un unique message utilisateur : profil, demande entre guillemets, et soit le JSON des hypothèses de démonstration, soit « Aucune hypothèse de démonstration n'est fournie pour cette demande. ». Aucune classification de la demande, aucune question posée à l'utilisateur en cours d'exécution, aucun tour de dialogue : la « question » est une section du dossier rendu. |
| État | **Exécuté**. Les deux formes de scénario figurent dans les arguments de profile_facts des dossiers enregistrés (complet dans runs/robert-agent, réduit à trois clés dans runs/mateo-libre-esg). Pas de test sur la construction du message initial. |
| Entrées et sorties | Entrée : nom de profil, texte de demande facultatif, hypothèses facultatives. Sortie : un message utilisateur Converse. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:191-200 ; src/datathon2026/cli.py:46-64 ; src/datathon2026/app.py:39-45 et 81-104 ; config/scenarios.toml |
| Dépendances | config/scenarios.toml, cli.py, app.py. |
| Limites | Demande libre toujours rattachée à l'un des trois profils (choices argparse, cli.py l.127 ; PERSONAS, app.py l.25). L'interprétation de la demande (actif visé, type d'analyse) dépend entièrement du modèle. docs/decisions.md (Rectifications, D1 critère c) rapporte que le profil ne change pas l'analyse du workflow fixe. |
| Transférabilité | **Adaptable**. Quelques lignes ; aucun contrat de qualification à reprendre. |
| Inconnues | Aucune. |

### X-CAP-003 — Essais avec modèle M1 (qualification avec schéma imposé) et M2 (citations mot pour mot contrôlées par le code)

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Savoir si un modèle seul extrait une demande sans inventer, et s'il recopie des citations à l'identique. |
| Valeur apportée | M1 : 20 contradictions plantées sur 20 signalées, 0 fausse sur 10, 0 champ inventé sur 80, absence ESG citée 5 fois sur 5. M2 : 145 citations sur 145 retrouvées (64 puis 81), 20 abstentions sur 20. |
| Fonctionnement | API Converse de Bedrock, modèle global.anthropic.claude-sonnet-5-5, sortie structurée par schéma JSON (outputConfig.textFormat json_schema). M1 : huit demandes écrites pour l'essai × cinq répétitions (40 appels). M2 : article 13.2 de l'instruction 31-103CP en anglais (22 336 caractères), huit questions dont deux sans réponse, cinq répétitions ; le code normalise espaces et guillemets puis cherche chaque citation dans le texte ; le motif d'arrêt max_tokens est contrôlé avant lecture. |
| État | **Vérifié**. Critères M1 (a à d) et M2 (a, b) écrits dans l'en-tête du script avant exécution ; résultats enregistrés avec identifiants de requête AWS. Portée étroite : jeu facile, un tour, un modèle. |
| Entrées et sorties | Entrées : demandes libres + profil ; texte réglementaire + questions. Sorties : sorties/m1_qualification.json (40 entrées), sorties/m2_citations.json, sorties/m2_citations.txt. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | research/experiences/modele_qualification_et_citations.py (SYSTEM_M1 l. 88-89, SYSTEM_M2 l. 155-157, SCHEMA_M1, SCHEMA_M2, fonction ask) ; research/experiences/sorties/m2_citations.txt : « M2a … 81 sur 81 », « M2b … 10 sur 10 », 5 appels, 36 800 jetons d'entrée, 14 450 de sortie ; research/experiences/sorties/m1_qualification.json (liste de 40) ; research/R09 §M1, §M2 ; R08 §1 (55 appels relevés par CloudWatch) |
| Dépendances | boto3, profil AWS alphaforge, modèle Sonnet 5.5 ; pour M2, un texte hors dépôt (clé « source » de m2_citations.json : /tmp/af_experiences/cp/cp.txt). |
| Limites | Aucun fichier .txt de résultat pour M1 : les décomptes ne figurent que dans R09 (le JSON brut est présent). m2_citations.txt ne porte que la seconde exécution (81 sur 81) ; la première (64 sur 64) n'a pas de sortie conservée. Hors critère : 20 questions prioritaires sur 40 en contiennent deux ; le modèle a rédigé une question même pour les deux demandes nettes (revue-par-questions.md, agent 0). Le schéma M1 n'a qu'un champ de perte tolérée : la séparation tolérance / capacité n'est pas éprouvée. Le contrôle M2 prouve l'existence de la citation, pas qu'elle soutient l'affirmation. |
| Transférabilité | **Adaptable**. La fonction ask et le contrôle de citation sont réutilisables avec tout client Bedrock ; les demandes et questions sont en dur. |
| Inconnues | Contradictions implicites, messages longs, plusieurs tours, autres modèles : non essayés. M2 non rejouable sans le texte source (non redistribué). |

## Recherche, littérature et sélection des preuves

### X-CAP-004 — Méthode de recherche documentaire : recherche web par AWS, registre de sources à niveau de lecture, vérificateurs chargés de réfuter, critique d'ensemble

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Le produit n'avait aucune recherche de méthode ni de source (diagnostic-et-contrat.md §3, ligne Agent 1 ; §5 « Une recherche mince, sans effet sur les calculs »). |
| Valeur apportée | Fournit 72 sources déterminantes décrites au même standard, avec ce qui a été réellement lu, et un rapport de vérification par source ; sert de matière première à une bibliothèque de fiches pour un agent de recherche. |
| Fonctionnement | Six recherches, une par fonction (qualification, recherche, analyse, confrontation, restitution, organisation). Recherche web par Amazon Bedrock AgentCore (InvokeWebSearch, web-search.v1) via research/outils/recherche_web.py, chaque requête journalisée. Textes téléchargés (curl, pdftotext) et lus directement. Chaque fiche de recherche (research/fiches/recherche-*.json) est relue par un vérificateur chargé de réfuter (research/fiches/verif-*.json) : retéléchargement, recherche de la citation, contrôle de version, sources adverses. Une critique d'ensemble (research/fiches/critique-ensemble.json) relit les six fiches l'une contre l'autre. consolider_recherche.py produit le registre R07 et le manifeste. FAIT À RETENIR : chercheurs, vérificateurs et critique sont des sous-agents du même modèle (us.anthropic.claude-fable-5-2 sur Bedrock, R08 §1), pas des personnes ; recherche-processus-professionnels.md §2 l'écrit (« Les vérificateurs sont des agents du même modèle que les chercheurs… ils ne valent pas une relecture par un spécialiste »). |
| État | **Exécuté**. Traces présentes : research/outils/journal_recherches.jsonl (281 lignes), research/fiches/*.json (6 recherches, 6 vérifications, 1 critique), R07 (1 512 lignes), manifeste.json (1 705 fichiers). Pas « vérifié » : aucun test automatique ni critère écrit d'avance ne porte sur la qualité de la recherche ; les contrôles sont faits par des sous-agents du même modèle. |
| Entrées et sorties | Entrées : six questions, textes publics téléchargés. Sorties : R07 (registre), revue-par-questions.md, fiches-des-agents.md, recherche-processus-professionnels.md, manifestes. |
| Sources théoriques | Sans objet (c'est la méthode qui produit les sources). |
| Preuves locales | research/R07-registre-des-sources-2026-11-15.md, section « Décompte » : 72 sources, 42 confirmées, 30 corrigées, 0 fausse, 140 secondaires ; research/outils/recherche_web.py (fonction search) et research/outils/journal_recherches.jsonl ; research/outils/consolider_recherche.py (commandes extraire, registre, manifeste, assembler) ; research/R08-outils-routes-et-ressources-2026-11-15.md §1 : 211 requêtes web, 2 534 appels du modèle entre 09 h 20 et 13 h 05 ; docs/refonte/recherche-processus-professionnels.md §2 (méthode et limites) ; research/fiches/verif-*.json, research/fiches/critique-ensemble.json |
| Dépendances | Compte AWS de l'atelier (profil alphaforge, us-east-1) pour AgentCore ; fermeture annoncée le 16 novembre à 13 h 59 (R08). Harnais de sous-agents de la session de développement (non versé au dépôt). curl, pdftotext. |
| Limites | Une matinée, interrompue deux heures. Environ une source déterminante sur quatre lue en entier, la plupart par sections (recherche-processus §2). Textes canadiens lus surtout en anglais (site de l'AMF inaccessible par script). R07 qualifie le vérificateur d'« indépendant » dans son en-tête alors que le document de synthèse retire ce mot : incohérence de vocabulaire dans le dépôt. Les chemins de preuve cités dans R07 pointent vers /tmp/af_recherche/…, hors dépôt et volatils. 39 sources sur 72 sont des cadres normatifs : la cartographie décrit ce que des textes prescrivent, pas des pratiques observées (§3, « Le manque principal »). |
| Transférabilité | **Adaptable**. recherche_web.py est autonome (boto3 + profil AWS). Le schéma de fiche (référence, niveau de lecture déclaré puis constaté, résultat, limites, élément influencé, contradiction, passage clé, verdict) est réutilisable tel quel. consolider_recherche.py dépend du format du journal du harnais de sous-agents. |
| Inconnues | Le nombre de recherches et les durées déclarés par les sous-agents ne sont pas vérifiés (10-pratiques-observees.md §4, dernière ligne). Aucune relecture humaine des 72 fiches n'est documentée. |

### X-CAP-005 — Cartographie des fonctions professionnelles, revue par questions et fiches méthodologiques des rôles

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Le découpage en quatre rôles n'était fondé sur aucun texte ; il fallait savoir quelle fonction professionnelle chaque rôle transpose et ce qui n'est pas simulé. |
| Valeur apportée | Dix-huit fonctions décrites (qui, quelle pièce, quel contrôle, ce qui n'est pas simulé) ; par question, ce que les sources établissent, ce que les mesures ajoutent, la décision proposée et sa solidité (forte, moyenne, faible) ; controverses avec « ce qui trancherait ». |
| Fonctionnement | Documents rédigés à partir des fiches de recherche puis relus contre les rapports des vérificateurs. Chaque appui est marqué [XXX-Snn] (registre R07), [R09 …] (expérience) ou [conception] (proposition de l'équipe sans source). La critique d'ensemble relève vingt règles contradictoires et seize passages de relais incohérents entre fiches ; quatorze résolutions sont proposées (§7.7). Une recherche complémentaire sur les pratiques observées (48 références, préfixes PQ, PR, PA, PS, PD, PC) est rapportée dans architecture/10-pratiques-observees.md avec les corrections de son vérificateur (sous-agent du même modèle, dit comme tel dans ce document). |
| État | **Conçu**. Documents présents et détaillés ; aucune de ces décisions n'est appliquée au produit (en-tête : « le produit reste gelé · en attente de validation du porteur »). |
| Entrées et sorties | Entrées : fiches et vérifications. Sorties : docs/refonte/recherche-processus-professionnels.md (388 lignes), revue-par-questions.md (518), fiches-des-agents.md (1 049), architecture/10-pratiques-observees.md (97). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/recherche-processus-professionnels.md §3 (cartographie), §4 (revue), §6 (controverses), §7.4 (neuf règles), §7.7 (quatorze résolutions), §7.8 ; docs/refonte/revue-par-questions.md (dix questions pour l'agent 0, etc.) ; docs/refonte/fiches-des-agents.md (six rubriques par rôle + « Ce qui reste incertain ») ; docs/refonte/architecture/10-pratiques-observees.md §3 et §4 ; research/fiches/redaction/*.md, research/fiches/architecture/pratiques-*.json |
| Dépendances | Registre R07 et expériences R09 pour les renvois. |
| Limites | Constats reconnus dans le texte : aucun texte ne prescrit un découpage en quatre ; rien ne prouve qu'une chaîne de quatre agents fasse mieux qu'un agent unique (§1, §6) ; fiches construites presque toutes sur la seule demande de Robert ; « vérifier une diversification » et « comparer des actifs » sans exemple dans cette recherche ; modules de code (qualification des données, greffier) sans fiche ; coûts, fiscalité, inflation non traités. 10-pratiques §4 : onze lectures allaient plus loin que leurs sources et ont été ramenées ; huit sources corrigées. |
| Transférabilité | **Autonome**. Documents textuels sans dépendance de code ; les identifiants de sources exigent R07. |
| Inconnues | Validation du porteur non constatée dans les fichiers lus (documents marqués « en attente de validation »). |

### X-CAP-006 — Recherche pendant la demande : lecteur de document, preuves candidates et règle d'asymétrie

| Champ | Contenu |
|---|---|
| Strate | architecture cible conçue, non construite |
| Problème traité | La bibliothèque de fiches ne couvre pas toute question ; une source trouvée en quelques minutes n'est relue par personne ; un document téléchargé peut contenir des consignes. |
| Valeur apportée | La recherche peut approfondir sans assouplir : une preuve candidate ajoute une réserve, rend obligatoire une variante ou un test déjà au catalogue, ou fonde une objection ; elle n'autorise pas une formulation écartée. |
| Fonctionnement | 03, Agent 1 et « Quand l'agent 1 approfondit » : six situations (réemploi, vérification ciblée, nouvelle recherche, lecture approfondie, examen d'une méthode, question sans preuve). Statut de qualification d'une fiche : qualifiée (relue par un membre nommé) ou candidate. « Étayée » exige une fiche qualifiée ; sinon plafond « étayée avec réserve ». Lecteur de document : sixième conversation de modèle, un seul outil de lecture, ne rend que des passages soumis à la porte de citation. Le lien de preuve sépare existence contrôlée (code) et soutien jugé (juge nommé). |
| État | **Conçu**. Contrat écrit. Hors produit, une chaîne recherche web -> reclassement -> preuve candidate par outil à schéma imposé -> contrôle mot pour mot a tourné une fois (services_aws, essai 4), sur extraits et non sur document entier. Le lecteur de document n'a pas été essayé (06, « Ce qui reste à vérifier » ; critère E7 « à faire »). |
| Entrées et sorties | Entrées : questions de recherche à clé, fiche de qualification, fiche des données, bibliothèque, formulations et résultats des tests de condition. Sorties : sources, passages, fiches candidates, liens de preuve, plan des méthodes ligne par ligne, fiche produit sans nombre propre, contradictions entre sources, lacunes, journal de recherche. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/architecture/03-contrats-des-agents.md, Agent 1 et « Restriction de la première version, affichée comme telle » ; docs/refonte/architecture/06-comparatif-technique.md section 4, table des moyens de recherche ; research/experiences/technique/services_aws/essai4_appels_du_produit.py et sorties/essai4.txt ; docs/refonte/architecture/09-reception.md critères E1 à E10 |
| Dépendances | Recherche web d'AgentCore, reclassement par Bedrock, bibliothèque de fiches, tests de condition du catalogue, porte de citation. |
| Limites | Dites par les documents : toutes les fiches sont aujourd'hui candidates, écrites et vérifiées par des sous-agents ; le contrôle prouve l'existence, pas le soutien ; dans l'essai 4 la citation obtenue « existe, mais ne répond pas clairement à la question » ; la recherche rend des extraits qui changent dans le temps ; qualité du reclassement en français non mesurée. |
| Transférabilité | **Adaptable**. La règle d'asymétrie et la séparation existence/soutien se transfèrent seules. Le plan des méthodes par formulation suppose le catalogue. |
| Inconnues | Lecture d'un document entier ; résistance à un document piégé ; budget de recherche ; durées de validité des sources. |

## Analyse financière, formulation et calcul

### X-CAP-007 — Dix outils offerts au modèle, dont sept déterministes inscrits au registre

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Fournir au modèle des calculs dont chaque résultat est un enregistrement identifié. |
| Valeur apportée | Le modèle ne reçoit que des couples {id, valeur affichée} ; les valeurs brutes (clés préfixées « _ ») lui sont retirées par _strip, sauf poids_obtenus du balayage de diversification. |
| Fonctionnement | TOOL_SPECS (agent.py l.51-96) : lister_actifs ; profil ; sources_donnees ; metriques_actif(ticker, horizon_ans=3) ; metriques_portefeuille(nom, poids, horizon_ans=3) ; melange(base, ticker, part) ; balayage_part(nom, base, ticker, seuil_perte) ; balayage_diversification(nom, base, panier, plafond) ; correlation(t1, t2) ; soumettre_dossier. Correspondance vers tools.py par TOOL_NAMES et _run_tool (l.146-170). Refus : poids négatifs ou somme hors 1 ± 0,005 (tools._weights) ; seuil_perte hors ]-1, 0[ (share_sweep) ; plafond hors ]0, 1] et panier non positif (diversification_sweep) ; part hors [0, 1] (analytics.blend) ; ticker inconnu (Market.check_tickers, appelé dans asset_metrics) ; nom d'outil inconnu (KeyError). |
| État | **Vérifié**. Refus d'entrées : tests/test_workflow.py::test_tools_reject_invalid_inputs_instead_of_returning_an_empty_result. Cohérence des balayages : ::test_robert_flip_point_is_consistent, ::test_amira_variant_respects_cap. Exécution : traces des dossiers sous runs/. Les schémas d'outils eux-mêmes ne sont pas testés. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Voir fonctionnement ; sortie type : {"perte_max": {"id": "R-0003", "valeur": "−70,9 %"}, …}. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:48-96 et 146-170 ; src/datathon2026/tools.py:56-284 ; tests/test_workflow.py:24-62 |
| Dépendances | analytics.py (Market, portfolio, blend, max_drawdown, worst_window), evidence.Registry, jeu de départ (STARTER_DIR). |
| Limites | lister_actifs et melange ne passent pas par Session.call : ils ne laissent aucune ligne dans la trace. correlation n'appelle pas check_tickers (ticker inconnu → KeyError pandas, message non contrôlé). asset_metrics accepte un horizon plus long que l'échantillon et inscrit une valeur None : runs/mateo-libre-esg, R-0009 « Pire rendement sur une fenêtre de 8 ans ESGV » = None, R-0010 = 0. Aucun outil de recherche, d'actualité ni de données ESG. Libellés « scénario de démonstration » inscrits comme origine des hypothèses même quand c'est le modèle qui les pose (tools.py l.171, 222, 263, 268). |
| Transférabilité | **Adaptable**. tools.py est partagé avec l'enchaînement fixe ; dépend de Session, du registre et d'analytics. |
| Inconnues | Aucune. |

### X-CAP-008 — Hypothèses manquantes posées et déclarées par le modèle

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Une demande libre arrive sans portefeuille, seuil ni plafond. |
| Valeur apportée | Le dossier dit, dans la section cadre, quelles hypothèses ont été fournies ou posées. |
| Fonctionnement | Uniquement par consigne (SYSTEM, Méthode point 2 : « pose une hypothèse explicite et dis dans la section cadre qu'elle vient de toi et qu'elle est modifiable »). Le code n'impose ni ne vérifie cette déclaration : la section cadre est la seule dispensée de référence et son statut d'affirmation est « non étayée ». |
| État | **Exécuté**. Observé : runs/robert-agent, cadre : « Le portefeuille actuel, le seuil de perte, les parts étudiées, l'horizon d'étude et l'alternative QQQ sont des hypothèses de démonstration, modifiables. » ; runs/mateo-libre-esg, cadre : « Aucune hypothèse de démonstration n'a été fournie. Je n'ai posé ni portefeuille, ni seuil, ni plafond ». docs/decisions.md D1 cite runs/robert-libre-or comme cas d'hypothèses posées par l'agent (dossier non inspecté dans cette passe). Aucun test. |
| Entrées et sorties | Texte libre de la section cadre. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:103 ; runs/robert-agent/dossier.json (affirmation de section cadre) ; runs/mateo-libre-esg/dossier.json (affirmation de section cadre) |
| Dépendances | Instruction système ; statuts « hypothèse » inscrits par les outils. |
| Limites | Les enregistrements d'hypothèse portent l'origine « scénario de démonstration » même posés par le modèle. Dans mateo-libre-esg le modèle a choisi horizon_ans = 8 (arguments de asset_metrics) sans que cela figure comme hypothèse au registre, et l'outil a renvoyé des valeurs None. |
| Transférabilité | **Adaptable**. Une phrase de prompt ; rien de structurel à reprendre. |
| Inconnues | Fréquence à laquelle le modèle omet la déclaration : non mesurée. |

### X-CAP-009 — Grille hebdomadaire commune (semaine se terminant le vendredi)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Calendriers TSX, américain et crypto 7 j/7 non alignés dans le jeu de départ. |
| Valeur apportée | Rendements comparables entre actifs sans remplissage quotidien. |
| Fonctionnement | `Market.__init__` lignes 67-73 : `self.daily.resample("W-FRI").last()` (dernière observation non manquante de chaque semaine samedi→vendredi, par actif) ; l'étiquette de la dernière case est ramenée à la dernière date observée si son vendredi la dépasse ; `weekly_returns = weekly_values.pct_change(fill_method=None).iloc[1:]` (rendement simple, première ligne retirée). |
| État | **Vérifié**. Test nommé `test_weekly_grid_neutralises_holidays` (tests/test_analytics.py:52) : aucune valeur manquante dans les rendements hebdomadaires de XIU.TO, SPY, BTC-USD sur les données réelles. Le test ne vérifie pas les 28 autres actifs ni la date réelle de l'observation retenue. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : `Market.daily`. Sorties : `weekly_values`, `weekly_returns` (fraction par semaine, devise de base). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/analytics.py:67-73 ; tests/test_analytics.py:52-55 ; docs/decisions.md D3 |
| Dépendances | pandas resample. |
| Limites | L'observation « de la semaine » n'est pas simultanée : vendredi UTC pour les cryptoactifs, dernière séance pour les actions (jeudi si vendredi férié). Les creux en cours de semaine ne sont pas vus (convention inscrite dans tools.py:179). docs/decisions.md ligne 84 et diagnostic §1 : la valorisation hebdomadaire donne −15,3 % au lieu de −17,5 % en quotidien pour 10 % de Tesla et fait passer la part maximale de 6 % à 9 % (chiffres « exploratoires » de docs/refonte/calcul_exploratoire.py, non revérifiés ici). |
| Transférabilité | **Adaptable**. Trois lignes de pandas ; l'ancre est un paramètre (`Conventions.weekly_anchor`). Tout résultat du produit en dépend. |
| Inconnues | Sensibilité au jour d'ancrage non étudiée dans le produit (décision D3 dite « posée sans étude de sensibilité », docs/decisions.md:84). |

### X-CAP-010 — Rendement annualisé composé et rendement de période

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Décrire le rendement historique d'un actif ou d'un portefeuille fictif. |
| Valeur apportée | Indicateurs descriptifs inscrits au registre avec période et conventions. |
| Fonctionnement | `cagr(v)` = (v_fin / v_début)^(1/années) − 1 avec années = jours calendaires / 365,25 (analytics.py:90-93). `total_return(v)` = v_fin / v_début − 1 (85-87). `period_return(v, start, end)` = rapport des dernières valeurs connues au plus tard à `start` et à `end`, None si la série ne couvre pas (124-130) ; appelé avec "2021-12-31" et "2022-12-31" (tools.py:151, 180). Actif : série quotidienne ; portefeuille : indice hebdomadaire base 1. |
| État | **Exécuté**. Aucun test nommé ne porte sur `cagr`, `total_return` ni `period_return` (tests/test_analytics.py). Valeurs présentes dans runs/robert-tsla/dossier.json et runs/amira-croissance/dossier.json (outils `asset_metrics`, `portfolio_metrics` dans la trace). |
| Entrées et sorties | Entrée : série de valeurs indexée par date. Sortie : fraction (unité de registre « pct », stockée en fraction, ex. 0.09), devise de base. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/analytics.py:85-93, 124-130 ; src/datathon2026/tools.py:138, 151-153, 173, 180 ; runs/robert-tsla/dossier.json |
| Dépendances | `Market`. |
| Limites | `total_return` n'est appelé nulle part dans src/. Diagnostic §1 : le rendement moyen n'est pas estimable sur cinq ans (erreur type 24,9 points pour Tesla, chiffre exploratoire) et le produit le met pourtant en regard du risque ; le rendement du portefeuille inclut un rééquilibrage hebdomadaire sans frais qui inverse le sens de l'effet de Tesla (diagnostic §1, docs/decisions.md:84). Aucune incertitude calculée. Rendement nominal : ni inflation ni taux sans risque. |
| Transférabilité | **Autonome**. Fonctions pures sur `pd.Series`. |
| Inconnues | Exactitude de `period_return` aux bornes non testée. |

### X-CAP-011 — Volatilité annualisée et corrélation sur rendements hebdomadaires

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Décrire la dispersion d'un actif ou portefeuille et le lien entre deux actifs. |
| Valeur apportée | Mesures comparables entre actifs de calendriers différents. |
| Fonctionnement | `annual_vol(weekly_r)` = écart type échantillon (ddof=1) des rendements hebdomadaires simples × √52 (`WEEKS_PER_YEAR = 52`, analytics.py:23, 96-97). `tools.correlation(s, t1, t2)` : corrélation de Pearson des rendements hebdomadaires sur les semaines où les deux sont définis (tools.py:277-284). |
| État | **Exécuté**. Aucun test nommé ne porte sur `annual_vol` ni sur `correlation`. Trace : runs/amira-croissance/dossier.json, R-0030 (corrélation BTC-USD / ETH-USD 0,835) ; volatilités dans les deux dossiers de référence. |
| Entrées et sorties | Entrées : série(s) de rendements hebdomadaires. Sorties : volatilité (fraction annualisée, unité « pct »), corrélation (unité « ratio »). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/analytics.py:96-97 ; src/datathon2026/tools.py:140, 175, 277-284 ; runs/amira-croissance/dossier.json (R-0030) |
| Dépendances | `Market.weekly_returns`. |
| Limites | Annualisation √52 suppose des rendements hebdomadaires non autocorrélés (hypothèse non énoncée dans le dépôt). `correlation` n'appelle pas `check_tickers`. Diagnostic §4 : une corrélation de 0,51 a servi au modèle pour écrire « Tesla diversifie donc peu ». Environ 260 semaines. |
| Transférabilité | **Autonome**. Fonctions courtes ; dépendent seulement de la grille hebdomadaire. |
| Inconnues | Aucun intervalle d'incertitude. |

### X-CAP-012 — Pire baisse depuis un sommet, dates et durée sous le sommet

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Mesurer la baisse la plus profonde observée et le temps de retour. |
| Valeur apportée | Indicateur central des dossiers de Robert (comparé au seuil de perte). |
| Fonctionnement | `max_drawdown(v)` (analytics.py:114-121) : dd = v / cummax(v) − 1 ; creux = argmin ; sommet = argmax de v jusqu'au creux ; retour = première date ≥ creux où v ≥ valeur du sommet, None sinon. `Drawdown.days_to_recover` (creux→retour) ; `days_underwater(end)` = (retour ou fin d'échantillon) − sommet (107-111), publié en années (/365,25, tools.py:149). Actif : série quotidienne ; portefeuille : indice hebdomadaire. |
| État | **Vérifié**. Tests nommés `test_max_drawdown_known_path` (profondeur, sommet, creux, retour sur une trajectoire de 7 points) et `test_max_drawdown_without_recovery` (tests/test_analytics.py:14-23). `days_underwater` et `days_to_recover` n'ont pas de test. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : série de valeurs. Sortie : `Drawdown(depth, peak, trough, recovery)` ; profondeur en fraction négative. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/analytics.py:100-121 ; tests/test_analytics.py:14-23 ; src/datathon2026/tools.py:142-150, 177-179 |
| Dépendances | Aucune hors pandas. |
| Limites | Diagnostic §6 : quand le sommet n'est pas retrouvé, la durée est tronquée à la fin de l'échantillon et inscrite « mesurée » alors que c'est un minorant ; une comparaison calculée en a tiré une conclusion fausse (runs/robert-libre-or, A-008, selon le diagnostic). Une seule trajectoire de cinq ans. Fréquence différente entre actif (quotidien) et portefeuille (hebdomadaire) : les deux profondeurs ne sont pas mesurées de la même façon. |
| Transférabilité | **Autonome**. Fonction pure ; à transférer avec la convention de fréquence explicite. |
| Inconnues | Aucune. |

### X-CAP-013 — Pire rendement sur fenêtres glissantes et décompte des fenêtres indépendantes

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Dire ce que l'échantillon montre à l'horizon du profil et combien de fenêtres indépendantes il contient. |
| Valeur apportée | Rend visible la faiblesse de l'échantillon (une seule fenêtre de 3 ans sans chevauchement). |
| Fonctionnement | `worst_window(v, years)` (analytics.py:141-152) : horizon = round(years × 365,25) jours ; débuts = toutes les dates telles que date + horizon ≤ dernière date ; valeur de fin par report vers l'avant (`reindex(..., method="ffill")`) ; rendement = fin / début − 1 ; minimum et sa date de début ; `n_starts` ; `n_independent = int(span // years)` avec span en années de 365,25 jours. `horizon_years` par défaut 3 (tools.py:129, 163). |
| État | **Vérifié**. Test nommé `test_worst_window_counts_independent_windows` (tests/test_analytics.py:26) : sur une trajectoire linéaire croissante de 6 ans, n_independent == 1 et pire fenêtre > 0. La valeur numérique du pire rendement n'est pas vérifiée contre un calcul connu. Trace : R-0010 = 1 dans runs/robert-tsla/dossier.json. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrées : série, horizon en années. Sortie : `Window(worst, worst_start, n_starts, n_independent)`. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/analytics.py:133-152 ; tests/test_analytics.py:26-30 ; runs/robert-tsla/dossier.json (R-0010, D-0005 = 4,9993 ans) |
| Dépendances | pandas. |
| Limites | Diagnostic §6 : la partie entière de 4,9993 / horizon annonce quatre fenêtres d'un an là où cinq tiennent. Diagnostic §1 : le pire rendement sur 105 fenêtres glissantes reste positif pour chaque option et le dossier ne le dit pas. Fenêtres fortement chevauchantes. Le test attend 1 pour 6 ans / 3 ans alors que 6 // 3 vaudrait 2 : l'échantillon du test fait en réalité un peu moins de 6 ans (2020-01-01 → 2025-12-31), même effet d'arrondi. |
| Transférabilité | **Autonome**. Fonction pure. |
| Inconnues | Aucune. |

### X-CAP-014 — Portefeuille fictif rééquilibré chaque semaine, contributions à la variance par ligne et par groupe

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Décrire un portefeuille à poids donnés et la concentration de son risque. |
| Valeur apportée | Part du risque par ligne, par groupe, et des trois premières lignes ; sert au plafond d'Amira. |
| Fonctionnement | `portfolio(m, weights)` (analytics.py:168-189) : poids ≥ 0, somme = 1 à 1e-9 près ; rendement hebdomadaire = Σ w_i r_i sur les semaines où tous les titres ont un rendement (`dropna`), ce qui équivaut à un rééquilibrage hebdomadaire sans frais ; indice base 1 daté une semaine avant la première semaine ; covariance échantillon ; contribution_i = w_i (Σw)_i / (wᵀΣw), somme 1 ; `weeks_used`, `weeks_dropped`. `tools.portfolio_metrics` (tools.py:163-208) ajoute rendement annualisé, volatilité, pire baisse hebdomadaire, rendement 2022, pire fenêtre, part des trois premières lignes, poids et part du risque par groupe (`[groupes]` de config/scenarios.toml), et lie chaque mesure à la composition (`depend_de`). `blend(base, ticker, share)` réduit proportionnellement la base (192-198). |
| État | **Vérifié**. Tests nommés `test_risk_contributions_sum_to_one` (somme = 1 et weeks_dropped == 0 pour SPY/XBB.TO/BTC-USD), `test_portfolio_rejects_leverage`, `test_blend_keeps_total` (tests/test_analytics.py:58-71). Aucune contribution individuelle n'est comparée à une valeur calculée à la main. Trace : cinq appels `portfolio_metrics` dans runs/robert-tsla/dossier.json. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrées : `Market`, dictionnaire ticker→poids. Sorties : `PortfolioStats(weights, weekly, index, weeks_used, weeks_dropped, risk_contrib)` ; outil : identifiants et valeurs affichées + `_brut`. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/analytics.py:158-198 ; src/datathon2026/tools.py:163-208 ; tests/test_analytics.py:58-71 ; config/scenarios.toml [groupes] |
| Dépendances | `Market.weekly_returns` ; `Session.group_of` ; registre `evidence.Registry`. |
| Limites | Rééquilibrage hebdomadaire sans frais ni impôt (hypothèse affichée) ; diagnostic §1 : sans rééquilibrage le rendement baisse quand on ajoute Tesla, alors que le dossier affiche une hausse. Covariance échantillon brute (diagnostic §4 cite la covariance contractée parmi les méthodes absentes). Contribution à la variance pouvant être négative, non traitée à part. Regroupement fait à la main, QQQ classé « Technologie » sans composition (commentaire de scenarios.toml) ; TSLA classé « Consommation discrétionnaire ». Un titre hors groupes tombe dans « Non classé ». |
| Transférabilité | **Adaptable**. `portfolio` et `blend` ne dépendent que de `Market` ; `portfolio_metrics` dépend du registre et de la table des groupes. |
| Inconnues | Stabilité des contributions dans le temps non mesurée. |

### X-CAP-015 — Balayage d'une part jusqu'à un seuil de perte (`share_sweep`)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Quelle part d'un actif peut être ajoutée à un portefeuille de base sans que la pire baisse historique dépasse un seuil. |
| Valeur apportée | Point de bascule affiché dans le dossier de Robert ; rend la conclusion dépendante d'une hypothèse modifiable. |
| Fonctionnement | tools.py:211-231 : seuil exigé dans ]−1, 0[ ; base renormalisée (`_weights`, tolérance 5e-3) ; grille 0 à `max_share` (0,30 par défaut) par pas de 0,01 ; pour chaque part, `blend` puis `portfolio` puis `max_drawdown` sur l'indice hebdomadaire ; `part_max` = plus grande part de la grille dont la profondeur ≥ seuil (None si aucune) ; courbe complète rangée dans `inputs["profondeurs"]` et `_brut`. |
| État | **Vérifié**. Tests nommés `test_robert_flip_point_is_consistent` (profondeur à la part trouvée ≥ seuil > profondeur à part + 0,01), `test_changing_a_hypothesis_changes_the_conclusion` (seuil −13 % donne une part inférieure à −20 %), `test_tools_reject_invalid_inputs_instead_of_returning_an_empty_result` (tests/test_workflow.py:24-63). Trace : R-0123 = 0,09 dans runs/robert-tsla/dossier.json. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrées : nom, base (poids), ticker, seuil (fraction négative), part maximale de grille. Sorties : enregistrements « seuil » (hypothèse) et « part_max » (mesuré, dépend du seuil), `_brut.profondeurs`. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/tools.py:211-231 ; tests/test_workflow.py:24-30, 43-48, 51-63 ; config/scenarios.toml [robert] ; runs/robert-tsla/dossier.json (R-0123) |
| Dépendances | `analytics.portfolio`, `blend`, `max_drawdown` ; registre. |
| Limites | `max(ok)` ne suppose pas la monotonie : si la profondeur n'est pas monotone en la part, la valeur rendue n'est pas un seuil de bascule (interprétation de ma part, lecture du code). Diagnostic §6 et §4 : l'outil rend la borne de la grille (30 %) comme « part maximale » sans signaler qu'elle est atteinte, et ne publie qu'un point de la courbe. Diagnostic §1 : une seule trajectoire ; la part va de 0 % à 23 % quand le seuil va de 12,5 % à 25 % ; en valorisation quotidienne 6 % au lieu de 9 % (chiffres exploratoires). Seuil de 15 % non issu d'une norme (docs/technique.md §4). |
| Transférabilité | **Adaptable**. Le calcul tient en dix lignes ; l'inscription au registre est propre à ce produit. |
| Inconnues | Monotonie de la courbe non vérifiée par un test. |
| Rectifications après relecture | Un cas observé existe : runs/robert-libre-or, enregistrement R-0048 = 0,3, soit la borne haute de la grille rendue comme part maximale. |

### X-CAP-016 — Balayage vers un panier jusqu'à un plafond de risque par groupe (`diversification_sweep`)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Quelle part minimale déplacer d'un portefeuille vers un panier déclaré pour qu'aucun groupe ne dépasse un plafond de part du risque. |
| Valeur apportée | Remplace une variante choisie à la main par une règle explicite (docs/technique.md §3, « Défaut trouvé pendant la construction »). |
| Fonctionnement | tools.py:234-274 : plafond dans ]0, 1] ; w(α) = (1 − α)·base + α·panier, panier renormalisé ; α de 0 à 1 par pas de 0,05 ; pour chaque α, part maximale de la variance par groupe ; résultat = plus petit α dont la part maximale ≤ plafond (None si aucun) ; chemin complet conservé. |
| État | **Vérifié**. Test nommé `test_amira_variant_respects_cap` (tests/test_workflow.py:32-40) : les poids rendus respectent le plafond de 0,50 ; il ne vérifie pas la minimalité de α. Rejet d'un plafond de 50 testé (ligne 56). Trace : R-0032 = 0,25 dans runs/amira-croissance/dossier.json. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrées : nom, base, panier, plafond (fraction). Sorties : enregistrements panier, part déplacée, plafond ; `_brut` (alpha, poids, chemin). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/tools.py:234-274 ; tests/test_workflow.py:32-40 ; config/scenarios.toml [amira] |
| Dépendances | `analytics.portfolio`, table des groupes, registre. |
| Limites | Pas de 5 points ; panier et plafond écrits d'avance dans config/scenarios.toml (diagnostic §3) ; dépend du regroupement manuel ; aucune optimisation sous contraintes (diagnostic §4, « fonctions absentes »). |
| Transférabilité | **Adaptable**. Couplé à la table des groupes et au registre. |
| Inconnues | Sensibilité au choix du panier non étudiée. |

### X-CAP-017 — Validation des entrées et traçage des appels d'outils de calcul

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Éviter qu'une erreur d'unité de l'appelant (agent compris) produise un résultat vide ou faux. |
| Valeur apportée | Erreur explicite au lieu d'un résultat silencieux ; chaque appel journalisé avec arguments, enregistrements créés et durée. |
| Fonctionnement | `_weights` (tools.py:64-69) : poids ≥ 0, somme à 5e-3 de 1, renormalisée à 1 ; `share_sweep` refuse un seuil hors ]−1, 0[ ; `diversification_sweep` refuse un plafond hors ]0, 1] et un panier non positif ; `analytics.portfolio` refuse levier et vente à découvert ; `blend` refuse une part hors [0, 1] ; `Market.check_tickers` lève KeyError pour un titre absent ; `Session.call` ajoute à `trace` outil, arguments, identifiants créés, durée en ms (tools.py:45-53). |
| État | **Vérifié**. Tests nommés `test_tools_reject_invalid_inputs_instead_of_returning_an_empty_result` (tests/test_workflow.py:51-63, dont la tolérance d'arrondi pour trois tiers) et `test_portfolio_rejects_leverage` (tests/test_analytics.py:64). Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrées : arguments d'outil. Sorties : ValueError/KeyError avec message en français, ou résumé `{clé: {id, valeur}}`. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/tools.py:45-69, 214-215, 238-243 ; src/datathon2026/analytics.py:76-79, 169-170, 194-195 ; tests/test_workflow.py:51-63 |
| Dépendances | `Session`, registre. |
| Limites | `correlation` et `asset_metrics` ne valident pas `horizon_years` ; `correlation` ne passe pas par `check_tickers`. Diagnostic §6 : les résultats rendus au modèle ne portent ni période, ni conventions, ni signalement des bornes. |
| Transférabilité | **Adaptable**. Motif simple ; le format de résumé est propre au registre. |
| Inconnues | Aucune. |

### X-CAP-018 — Rééchantillonnage stationnaire par blocs des rendements hebdomadaires (part des trajectoires franchissant un seuil), avec étude de la longueur de bloc

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Le produit lit la pire baisse sur une seule trajectoire observée (diagnostic §1). |
| Valeur apportée | Donne, pour chaque option de portefeuille, la part de trajectoires simulées de trois ans dont la pire baisse franchit un seuil ou qui finissent sous la valeur de départ ; mesure que la longueur de bloc est le choix le moins influent sur le cas étudié. |
| Fonctionnement | Indices tirés par blocs de longueur géométrique de moyenne `block`, échantillon circulaire (fonctions boot / idx / boot_idx, même code recopié dans chaque script). Rendement de portefeuille = rendements rééchantillonnés × poids ; pire baisse par cumul et maximum courant. X1 compare la longueur automatique (arch.bootstrap.optimal_block_length) à 13 semaines. |
| État | **Vérifié**. Critère X1 écrit dans l'en-tête de methodes_analyse.py avant exécution (écart de plus de 5 points) ; résultat enregistré : non déclenché, 3,6 points au plus entre 1,5 et 13 semaines (sorties/methodes_analyse.txt, bloc X1). Hors produit : script, aucun test pytest. |
| Entrées et sorties | Entrées : m.weekly_returns (261 semaines, CAD), poids des options. Sorties : parts de trajectoires par option, bloc et hypothèse de rendement. |
| Sources théoriques | Politis et White 2004, Patton-Politis-White 2009 (via la bibliothèque arch ; niveau de lecture au registre R07, ANA-S02/S03 : sections). |
| Preuves locales | research/experiences/methodes_analyse.py (critère X1 en en-tête) ; research/experiences/sorties/methodes_analyse.txt, bloc « X1 » : longueurs estimées 1,1 à 1,5 (rendements), 15,6 à 15,8 (valeurs absolues) ; parts par bloc de 1 à 52 ; docs/refonte/calcul_exploratoire.py (fonction boot, SEED=2026, N_PATHS=10 000, BLOCK=13) ; research/experiences/sorties/multivers_exploratoire.json, clés E1_graines (écart type 0,0049 pour 10 % TSLA) et E2_blocs ; research/R09-experiences-discriminantes-2026-11-15.md §X1 |
| Dépendances | numpy ; arch 9.0.0 chargé à la volée (uv run --with arch), absent de pyproject.toml ; datathon2026.tools.Session().market et analytics.blend. |
| Limites | Un portefeuille (Robert), deux ajouts, 261 semaines. La règle automatique donne deux réponses (environ 1 semaine sur les rendements, environ 16 sur les valeurs absolues) et vise la variance d'une moyenne, pas une pire baisse (R09 §X1). Entre 1 et 52 semaines l'écart atteint 9,6 points. La fonction de rééchantillonnage est dupliquée dans six scripts, pas factorisée. |
| Transférabilité | **Adaptable**. La fonction d'indices (une dizaine de lignes numpy) est autonome ; il faut fournir une matrice de rendements alignés et des poids. |
| Inconnues | Validité théorique pour une trajectoire de trois ans tirée de cinq : « aucun théorème lu » (recherche-processus §4, [ANA-S02]) ; source sur un biais à long horizon lue en résumé seulement. |

### X-CAP-019 — Rendement moyen non estimable sur cinq ans et grille d'hypothèses de rendement (moyennes historiques, taux sans risque, aucun rendement)

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Le produit met un rendement annualisé en regard du risque (diagnostic §1). |
| Valeur apportée | Établit sur le cas mesuré que l'écart de rendement Tesla moins portefeuille a un intervalle à 90 % de −26,8 à +51,7 points par an ; remplace un rendement supposé par trois hypothèses calculées côte à côte. |
| Fonctionnement | X3 : erreurs types de la moyenne et de la volatilité par rééchantillonnage stationnaire (5 000 tirages), hebdomadaire et quotidien. Grille : les rendements rééchantillonnés sont recentrés pour créditer soit la moyenne historique, soit le taux sans risque (3,22 % par an, moyenne des obligations du Canada à 2 ans sur la fenêtre), soit zéro. |
| État | **Vérifié**. Critère X3 écrit d'avance (en-tête de methodes_analyse.py) ; résultat enregistré : première partie confirmée (l'intervalle contient zéro), seconde partie manquée (le passage au quotidien ne réduit l'erreur sur la volatilité d'un tiers que pour Tesla ; avec bloc commun, pour aucun actif). La grille elle-même n'a pas de critère : exécutée seulement. |
| Entrées et sorties | Entrées : rendements hebdomadaires et quotidiens, série de taux macro_rates. Sorties : moyenne ± erreur type par actif ; parts de trajectoires sous trois hypothèses. |
| Sources théoriques | [ANA-S01] (précision d'un rendement moyen selon la durée) ; niveau de lecture : voir R07. |
| Preuves locales | research/experiences/sorties/methodes_analyse.txt, blocs « X3 » et « X3 bis » (TSLA hebdo : +0,205 ± 0,249 ; 453 ans pour distinguer une prime de 5 points) ; research/experiences/sorties/ecart_et_niveau.txt, parties B et C (trois hypothèses) ; docs/refonte/calcul_exploratoire.py (sections 3 et 4) ; research/R09 §X3 |
| Dépendances | numpy, pandas ; données de taux du projet. |
| Limites | X3 bis ajouté après coup, sans critère. Erreur corrigée en cours de route sur les jours fériés (R09 §X3). Le taux sans risque est une moyenne sur la fenêtre, appliquée à tous les actifs : hypothèse, pas une prévision. |
| Transférabilité | **Adaptable**. Le recentrage des rendements est une opération numpy indépendante ; le taux vient d'une série propre au jeu de données. |
| Inconnues | Aucune hypothèse de rendement fondée pour trois à cinq ans : « rien dans nos données » (recherche-processus §6). |

### X-CAP-020 — Comparaison des options par écarts appariés sur les mêmes trajectoires, avec intervalle

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Les niveaux de risque de deux options se chevauchent ; le produit compare des niveaux issus d'une seule histoire. |
| Valeur apportée | Sur le cas mesuré, l'écart apparié exclut zéro pour trois mesures alors que les intervalles de niveau se chevauchent pour deux ; la « part maximale de 9 % » du produit vaut de « aucune part » à 25 % selon l'histoire tirée (X4 bis). |
| Fonctionnement | 5 000 histoires rééchantillonnées de cinq ans, mêmes semaines tirées pour les deux options ; différence calculée tirage par tirage ; intervalle à 90 %. Partie C de ecart_et_niveau.py : 400 histoires × 2 000 trajectoires pour l'intervalle d'échantillonnage du niveau et de l'écart. |
| État | **Vérifié**. Critère X4 écrit d'avance ; résultat enregistré : déclenché. X4 bis et la partie C sont des ajouts sans critère (exécutés seulement). |
| Entrées et sorties | Entrées : rendements hebdomadaires, deux vecteurs de poids. Sorties : intervalle du niveau de chaque option, intervalle de l'écart, part des tirages où l'option est plus défavorable. |
| Sources théoriques | Ledoit et Wolf 2008 (différence appariée), trouvé par le vérificateur ; niveau de lecture non précisé dans les fichiers lus. |
| Preuves locales | research/experiences/sorties/methodes_analyse.txt, blocs « X4 » (écart de pire baisse −0,1036 à −0,0016 ; plus défavorable dans 0,961) et « X4 bis » (médiane 0,12 ; aucune part admissible 0,103 au bloc de 13) ; research/experiences/sorties/ecart_et_niveau.txt, partie C (écart positif dans 0,985 / 1,000 / 1,000 des histoires) ; research/experiences/sorties/dossier_illustratif.txt (écarts par longueur de bloc 1, 4, 13, 26) ; research/R09 §X4, §« Écart et niveau » |
| Dépendances | numpy ; marché du projet. |
| Limites | Portefeuille de Robert, 10 % de Tesla, 261 semaines. Les intervalles viennent du rééchantillonnage des mêmes cinq années (R09, « Ce que ces expériences ne disent pas »). La taille de l'écart reste imprécise : +16 à +42 points selon l'hypothèse (partie C). |
| Transférabilité | **Autonome**. Principe indépendant du produit : tirer une fois les indices, appliquer à chaque vecteur de poids. |
| Inconnues | Comportement sur d'autres portefeuilles ou d'autres types de demande : non mesuré, sauf le portefeuille fictif de Mateo (parcours_contraste). |

### X-CAP-021 — Calibration du rééchantillonnage sur processus connus et essai en fenêtre croissante (niveau contre écart)

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Savoir si une part de trajectoires peut être présentée comme un niveau de risque ou une probabilité. |
| Valeur apportée | Sur processus simulés, le niveau à trois ans n'est retrouvé à 10 points près que dans 21 % à 77 % des échantillons de 261 semaines (rendement imposé) ; le signe de l'écart entre deux portefeuilles est correct dans 99 à 100 % des cas à trois ans. Sur les données réelles, quatre mesures de couverture sur huit sortent de l'intervalle fixé. |
| Fonctionnement | X8 : trois processus hebdomadaires de volatilité annuelle voisine de 10 % (gaussien indépendant, GARCH(1,1) 0,10/0,85, deux régimes de 150 et 26 semaines), rendement nul puis 0,17 % par semaine ; 400 échantillons, 2 000 trajectoires, bloc 13, seuil 15 % ; comparaison à la vraie part. X6 : à chaque date, 2 000 scénarios d'un an tirés du seul passé, comparés à l'année réalisée. |
| État | **Vérifié**. Critères X8 et X6 écrits d'avance dans les en-têtes ; résultats enregistrés : X8 déclenché pour le niveau, tenu pour l'écart dans 11 configurations sur 12 ; X6 déclenché. |
| Entrées et sorties | X8 : aucune donnée réelle. X6 : rendements hebdomadaires du projet. Sorties : part d'échantillons à moins de 10 points, part de signes corrects ; taux de couverture et rang médian. |
| Sources théoriques | [ANA-S02], [ANA-S10] (scénarios européens tirés de cinq ans jugés trompeurs) ; deux études de 2026 connues par leur seul résumé (recherche-processus §4). |
| Preuves locales | research/experiences/calibration_reechantillonnage.py (en-tête : critère X8 ; SEED, N, S, PATHS, BLOCK, THR = 2026, 261, 400, 2000, 13, 0.15) ; research/experiences/sorties/calibration_reechantillonnage.txt (13 lignes : 12 configurations) ; research/experiences/sorties/methodes_analyse.txt, bloc « X6 » (rangs médians 0,74 à 0,90) ; research/R09 §X8, §X6 |
| Dépendances | numpy uniquement pour X8. |
| Limites | Processus choisis par l'équipe ; à un an le signe n'est correct que dans 91 % des échantillons pour les deux régimes avec rendement positif. X6 est déclaré « faible » (deux à trois années sans chevauchement). |
| Transférabilité | **Autonome**. calibration_reechantillonnage.py n'importe que numpy : exécutable sans le produit ni les données. |
| Inconnues | Processus à queues épaisses ou à dépendance entre actifs : non essayés. |

### X-CAP-022 — Rendement d'équilibre : surcroît de rendement requis pour qu'une option ne soit pas plus défavorable

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Une analyse qui ne crédite aucun rendement conclut toujours pour « ne rien changer » (critique d'ensemble, recherche-processus §6). |
| Valeur apportée | Sur le cas : 13 points par an au-dessus du taux sans risque pour que 10 % de Tesla ne fasse pas finir plus souvent sous la valeur de départ à trois ans (5e au 95e centile : 8 à 26) ; au-delà de 80 points pour la baisse en route. QQQ : 5 points (3 à 7) et 34 points. |
| Fonctionnement | Tous les actifs crédités du taux sans risque (3,22 %) ; on balaie le surcroît de rendement du titre ajouté sur une grille de 0 à 80 % par pas de 1 point (GRID) et on retient le plus petit pour lequel l'option n'est pas plus défavorable que la référence ; intervalle sur 200 histoires rééchantillonnées ; 4 000 trajectoires, bloc 13. |
| État | **Exécuté**. Sortie enregistrée ; aucun critère écrit d'avance (en-tête du script). |
| Entrées et sorties | Entrées : rendements hebdomadaires, poids, taux. Sorties : surcroît d'équilibre par mesure (perte à l'échéance, baisse en route) avec centiles. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | research/experiences/rendement_d_equilibre.py ; research/experiences/sorties/rendement_d_equilibre.txt (TSLA, QQQ, BTC-USD) ; research/R09 §« Rendement d'équilibre » ; docs/refonte/recherche-processus-professionnels.md §7.4, règle 9 |
| Dépendances | numpy ; marché du projet. |
| Limites | Une seule hypothèse de base, intervalle large, même échantillon de cinq ans (R09). Incohérence interne relevée : l'estimation ponctuelle pour Tesla est 13 % alors que la médiane sur 200 histoires est 16 % (sortie .txt). Hors grille dans 75 % des histoires pour la baisse en route. Le rapprochement avec une « optimisation inverse » a été jugé « faux rapprochement » par le vérificateur (10-pratiques §4). |
| Transférabilité | **Autonome**. Calcul indépendant des autres expériences ; ne demande que le rééchantillonnage et un taux. |
| Inconnues | Aucune source lue ne fonde cette mesure : c'est une proposition de l'équipe après la critique d'ensemble. |

### X-CAP-023 — Contrôle des conventions de calcul : formule d'annualisation du notebook, convention de corrélation, contraction de covariance

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Le notebook d'introduction des organisateurs et la contraction de Ledoit-Wolf sont des reprises courantes ; il fallait savoir si elles sont utilisables sur cet univers. |
| Valeur apportée | Sur les 31 actifs : la formule (1 + moyenne quotidienne)^jours − 1 s'écarte du rendement composé de plus de 2 points pour 18 actifs (Tesla : +22,8 % contre +2,9 %) ; 28,0 % des 465 paires de corrélation diffèrent de plus de 0,10 entre conventions ; la contraction à cible identité fait passer la volatilité prévue du portefeuille de Robert de 7,31 % à 7,86 %. |
| Fonctionnement | X2 : comparaison actif par actif et paire par paire. X5 : sklearn.covariance.LedoitWolf sur 31 actifs, effet sur volatilité et parts de risque de portefeuilles donnés ; variance minimale hors échantillon (104 semaines d'estimation, 26 réalisées). X5 bis : contraction des corrélations à variances conservées, essai sur les 20 actions. |
| État | **Vérifié**. Critères X2 et X5 écrits d'avance ; résultats enregistrés : X2 déclenché deux fois ; X5 contredit pour la méthode courante (critère d'innocuité non tenu ; l'échantillon fait mieux hors échantillon sur l'univers complet). X5 bis ajouté après coup, sans critère. |
| Entrées et sorties | Entrées : prix quotidiens et rendements hebdomadaires. Sorties : tableaux d'écarts, conditionnement (69 023 à 278), volatilités réalisées. |
| Sources théoriques | Ledoit et Wolf 2004 [ANA-C01] : sections lues (recherche-processus §8, ligne R6). |
| Preuves locales | research/experiences/sorties/methodes_analyse.txt, blocs « X2 », « X5 », « X5 bis » ; research/R09 §X2, §X5 ; research/R08 §6 (examen du notebook, 35 cellules lues, non exécuté) |
| Dépendances | scikit-learn 1.9.1 et arch chargés à la volée, absents de pyproject.toml. |
| Limites | Résultat X5 lié à la composition de l'univers (un quasi-placement de trésorerie, ZST.TO, et des cryptoactifs) ; 6 à 8 fenêtres hors échantillon seulement. |
| Transférabilité | **Adaptable**. X2 dépend du notebook des organisateurs ; X5 est réutilisable sur toute matrice de rendements. |
| Inconnues | Aucun agent n'optimise de poids dans le produit ni dans les essais : la règle « contracter si un agent optimise » n'a pas de cas d'usage exécuté. |

### X-CAP-024 — Mesures de concentration et parcours contrasté (portefeuille fictif de Mateo, exclusion d'un secteur, fonds filtré)

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Toute la recherche était construite sur « ajouter un titre » ; il fallait un second type de demande (diversification, préférence ESG par exclusion). |
| Valeur apportée | Nombre effectif de lignes en risque (1 / somme des carrés des parts de risque), part de risque d'un secteur, premier contributeur, comparés par écarts appariés entre « ne rien changer » et quatre options. |
| Fonctionnement | Portefeuille inventé pour l'exemple (P0 : XIU.TO, SPY, ENB.TO, CNQ.TO, RY.TO, XBB.TO) ; options : sans le secteur Énergie, ESGV à la place de SPY, les deux, sans CNQ.TO. Fonction mesures(X, w, k) ; écarts sur 2 000 histoires, quatre longueurs de bloc, hebdomadaire et quotidien. |
| État | **Exécuté**. Sortie enregistrée ; l'en-tête dit « Aucun critère écrit d'avance : ce sont les nombres d'un exemple, pas une expérience discriminante ». |
| Entrées et sorties | Entrées : rendements hebdomadaires et quotidiens (1 227 jours ouvrables communs), secteur par ligne. Sorties : lignes effectives 4,59 (ne rien changer), 2,96 (sans Énergie) ; écart −1,73 à −1,43 ; ESGV-SPY corrélation 0,991. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | research/experiences/parcours_contraste.py (P0, OPTIONS, mesures) ; research/experiences/sorties/parcours_contraste.txt ; research/R09 §« Compléments de l'étape d'architecture » |
| Dépendances | datathon2026.data.load_universe (secteur), m.daily. |
| Limites | Portefeuille non donné par l'énoncé. La part du secteur Énergie à l'intérieur de XIU.TO est « inconnue (aucune composition de fonds dans les données) ». Aucune donnée ESG : seule l'exclusion par secteur et un fonds filtré de l'univers sont praticables. |
| Transférabilité | **Adaptable**. La fonction mesures est réutilisable ; le portefeuille et les options sont en dur. |
| Inconnues | Repères de concentration (par exemple la règle de 10 % par émetteur du Règlement 81-102) repérés mais non appliqués (recherche-processus §6). |

### X-CAP-025 — Sept types de résultats, règle du « sens établi » et quatre parties de la conclusion

| Champ | Contenu |
|---|---|
| Strate | architecture cible conçue, non construite |
| Problème traité | Cinq ans de données n'établissent aucun niveau de risque mais établissent le sens de certaines comparaisons ; il faut empêcher qu'un résultat fragile soit présenté comme un fait. |
| Valeur apportée | Chaque affirmation porte un type qui fixe ce qu'on peut écrire, titrer et dessiner ; un seul rendu par type, calculé par le code avant la restitution. |
| Fonctionnement | 05 section 2 : 1 mesure historique ; 2 estimation avec incertitude ; 3 proportion de trajectoires simulées (illustration seulement) ; 4 comparaison entre options ; 5 condition ou rendement d'équilibre ; 6 résultat sensible aux conventions ; 7 conclusion insuffisamment étayée. Sens « établi » si l'intervalle à 90 % de l'écart apparié exclut zéro sous chaque valeur de base et si le signe est le même dans toute la batterie ; « établi avec réserve » s'il ne se renverse que sous une hypothèse « borne » ; sinon type 7. Quatre parties de conclusion avec les types permis. Quatre éléments affichables sans type (constats sur les déclarations, relevés de l'étude, repères cités, marques). Table de couverture des horizons (trois ans au plus pour les trajectoires). Règles ESG et profil de risque comme fait déclaré. |
| État | **Conçu**. Décrit dans 05 ; le moteur de calcul « refait selon le document 05 » est l'étape 1 de l'ordre de livraison, non faite (00 section 8). Les nombres des deux parcours illustratifs sont calculés par des scripts de research/experiences/ (hors de ce périmètre) ; aucune porte d'analyse ou de restitution n'existe. |
| Entrées et sorties | Entrée : calculs du code (écart apparié, intervalles, signes sur la batterie, valeurs par convention). Sortie : affirmation typée avec portée, conditions de réemploi, sens calculé par le code, rendus. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/architecture/05-types-de-resultats.md sections 1 à 6 ; docs/refonte/architecture/09-reception.md critères D1 à D13 ; docs/refonte/architecture/01-resolutions.md section 10 (ligne « Sens établi était affirmé sur une seule longueur de bloc ») |
| Dépendances | Batterie fixe, hypothèses de rendement à statut, convention des mesures historiques, table d'affichage des statuts. |
| Limites | Dites par le document : le niveau de 90 % est une convention sans source ; la borne de trois ans est « arrêtée après avoir vu les données », deux ans non calibrés ; la grille des longueurs de bloc et le sous-échantillon minimal sont des conventions (00 section 11, « Convention, sans source »). |
| Transférabilité | **Adaptable**. La typologie et les interdits de présentation se transfèrent à tout moteur qui fournit écarts appariés, intervalles et variantes ; la règle du sens établi suppose une batterie croisée. |
| Inconnues | Tolérances ; taux d'erreur de la règle sous hypothèse nulle (K1) ; compréhension par des lecteurs. |

## Contradictions, critique et validation

### X-CAP-026 — Soumission contrôlée du dossier et boucle de correction (deux au plus)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Éviter qu'un dossier contenant un chiffre manuscrit, une comparaison manuscrite ou une référence inconnue soit rendu sans que le modèle ait eu à le corriger. |
| Valeur apportée | Le rejet est renvoyé au modèle sous forme de résultat d'outil en erreur, avec la liste des problèmes. |
| Fonctionnement | agent.py l.213-224 : à chaque soumettre_dossier, _build construit le Dossier, verification() renvoie « problemes », auxquels s'ajoutent les problèmes de présentation (référence ou série inconnue). Si problèmes et fixes < MAX_FIXES (2) : toolResult status=error avec {problemes, consigne: « Corrige ces éléments et soumets à nouveau le dossier complet. »}. Sinon : toolResult {accepte: not problems} et le dossier est retenu. |
| État | **Vérifié**. tests/test_agent.py::test_agent_loop_runs_tools_rejects_handwritten_number_then_accepts (« nombre non relié », corrections_demandees == 1) et ::test_agent_presentation_is_checked_then_rendered (« R-0999 », « comparaison écrite à la main »). Exécutions : corrections_demandees = 1 dans runs/robert-agent et runs/mateo-libre-esg. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : entrée JSON de soumettre_dossier. Sortie vers le modèle : {accepte: bool} ou {problemes, consigne}. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:213-224 ; tests/test_agent.py:27-44 et 58-83 ; docs/decisions.md D5 et Rectifications |
| Dépendances | Dossier.verification (dossier.py, evidence.py), hors de ce périmètre. |
| Limites | À la troisième soumission fautive (fixes == 2), le dossier est retenu MÊME EN ÉCHEC : toolResult {accepte: false} puis sortie de boucle avec dossier non conforme (agent.py l.217-218, l.233). docs/decisions.md (Rectifications, D5) : cinq premiers jets sur six refusés une fois ; passes de correction estimées à environ un tiers des jetons ; garde lexicale à liste fermée. |
| Transférabilité | **Fortement couplée**. Ne vaut qu'avec le vérificateur de preuves et le format des gabarits {{…}}. |
| Inconnues | Aucun dossier enregistré accepté en échec n'a été cherché au-delà des six dossiers du tableau docs/comparaison-agent-workflow.md (tous « conforme »). |
| Rectifications après relecture | Recherche étendue aux dix dossiers d'agent (six de runs/, trois de runs/_archives/, un de evaluation-fusion/preuves/) : aucun n'a été retenu en échec. Le chemin « dossier retenu encore en échec après deux corrections » (src/datathon2026/agent.py:217-218) est donc lu dans le code, jamais observé, et sans test. |

### X-CAP-027 — Comparaison des dossiers de l'agent à l'enchaînement fixe (script hors paquet)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Savoir si l'agent choisit autre chose que l'enchaînement fixe (critère de réfutation (a) de D1). |
| Valeur apportée | Tableau reproductible des appels communs, ajoutés et absents, et des appels, jetons et corrections par dossier. |
| Fonctionnement | scripts/comparer_agent_workflow.py lit runs/*/dossier.json, retient comme dossiers d'agent ceux dont aws.appels est non vide, compare les multiensembles d'appels (Counter) pour les couples REFERENCE = {robert-agent: robert-tsla, amira-agent: amira-croissance}, liste les outils des autres dossiers, écrit du Markdown. Aucun appel AWS ni recalcul. |
| État | **Exécuté**. Sortie enregistrée : docs/comparaison-agent-workflow.md. Le critère (a) était écrit d'avance (docs/decisions.md D1), mais docs/decisions.md (Rectifications) établit que la section « Lecture » est écrite en dur dans le script (l.67-72) et que la comparaison sur demandes libres est acquise par construction ; pas de test du script. |
| Entrées et sorties | Entrée : runs/*/dossier.json. Sortie : Markdown sur la sortie standard. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | scripts/comparer_agent_workflow.py ; docs/comparaison-agent-workflow.md ; docs/decisions.md (D1, Rectifications) |
| Dépendances | Format du dossier (trace, aws, verification, demande). |
| Limites | Un dossier par demande, un seul modèle ; compare des noms d'appels, pas le contenu des dossiers ; conclusions rédigées à la main dans le script. |
| Transférabilité | **Adaptable**. Dépend seulement du format dossier.json. |
| Inconnues | Aucune. |

### X-CAP-028 — Vérificateur déterministe des textes (check_template / verify_claims)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Détecter un chiffre, une grandeur ou un sens de comparaison écrits hors registre. |
| Valeur apportée | Contrôle de forme, déterministe, rejouable hors ligne, testable par fautes injectées. |
| Fonctionnement | Règles réellement appliquées (evidence.py:273-308, 329-334) : (1) « référence inconnue » : identifiant du gabarit ou de `refs` absent du registre ; (2) « référence mal formée » : expression entre accolades qui n'est ni un identifiant, ni `X-0000.label`, ni une comparaison ; (3) « comparaison invalide » : toute expression dont le rendu commence par « [ » (unités non numériques ou différentes, valeur None, cmpduree hors domaine ; aussi émise en double pour une référence inconnue) ; (4) « nombre non relié » : toute suite de chiffres restant après retrait des références, sauf si elle figure dans le libellé, le sujet ou la période d'un enregistrement cité, y compris les fragments obtenus en coupant sur « - . , » ; (5) « nombre écrit en lettres » : mot-nombre d'une liste fermée suivi d'une unité (pour cent, %, an(s), année(s), mois, jour(s), semaine(s), point(s), fois), ou « moitié, double, triple, quart, un/deux tiers » (evidence.py:59-62) ; (6) « comparaison écrite à la main » : six motifs lexicaux (evidence.py:48-56), hors sections `question` et `condition` (evidence.py:64) et hors proposition introduite par « si » jusqu'à la ponctuation suivante, « même si » restant contrôlé (evidence.py:63, 82) ; (7) « affirmation non étayée » : aucune référence et section autre que `cadre`. `verify_claims` (evidence.py:337-347) renvoie affirmations, valeurs_reliees (nombre de références dans les textes), affirmations_en_echec, problemes, ok. |
| État | **Vérifié**. Tests à fautes injectées nommés : `test_handwritten_number_is_flagged`, `test_quantity_written_in_words_is_flagged_but_a_plain_count_is_not`, `test_year_allowed_only_if_in_cited_record`, `test_unknown_and_malformed_references_are_flagged`, `test_handwritten_comparison_is_flagged_except_in_hypothetical_sections`, `test_claim_status_is_weakest_reference_and_unsupported_claim_flagged` (tests/test_evidence.py). Vérifié pour ces formes seulement ; le diagnostic a par ailleurs injecté quinze affirmations fautives qui passent (docs/refonte/diagnostic-et-contrat.md:54). Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : liste d'affirmations + registre. Sortie : dict `verification` du dossier. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/evidence.py:45-64, 78-89, 267-347 ; tests/test_evidence.py:28-51, 96-123 ; docs/decisions.md:59-67 (D5) ; docs/technique.md:20 ; docs/refonte/diagnostic-et-contrat.md:51-57, 111 |
| Dépendances | Registre ; listes lexicales françaises. |
| Limites | Ce qu'il ne voit pas : le sens d'une phrase (« Il faut vendre Tesla immédiatement », « Tesla garantit un rendement de 8 % par an » passent, statut « mesuré », diagnostic:56) ; l'adéquation entre la phrase et la valeur citée (une référence quelconque suffit à « étayer ») ; un chiffre qui coïncide avec un nombre du libellé, du sujet ou de la période d'un enregistrement cité, fragments de dates compris (diagnostic:51) ; le titre du dossier, le titre d'un tableau, le titre, la note, le sous-titre et les étiquettes d'un graphique, les intitulés de la fiche de profil (dossier.py:53-73 ; diagnostic:55) ; tout comparatif hors des six motifs ; les sections `question` et `condition` et les propositions en « si » pour les comparatifs ; les conseils, prévisions, causalités. Lecture du motif `_WORDED_NUMBER` (non exécutée) : « un », « zéro », « million », « vingts » et « le tiers » n'y figurent pas. Il ne recalcule aucune valeur. La mention affichée « aucun chiffre ni sens de comparaison n'est saisi à la main » (report.py:502-503) est jugée par le diagnostic vraie pour les chiffres, muette sur le sens (diagnostic:54). `valeurs_reliees` compte des références dans les textes (comparaisons et libellés compris), pas des valeurs distinctes ; les cellules de tableau n'y entrent pas. |
| Transférabilité | **Autonome**. Module sans dépendance interne. Le diagnostic propose de le conserver comme obligation de passer par les comparaisons calculées, en révisant le périmètre de la garde lexicale (diagnostic:99, 111). |
| Inconnues | Taux de faux positifs de la garde lexicale sur des textes réels : non mesuré. Les quinze affirmations fautives de l'audit ne sont pas listées dans le passage lu. |

### X-CAP-029 — Diagnostic du produit et contrat de refonte

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Savoir ce que le produit implémenté fait réellement au regard des cinq fonctions visées. |
| Valeur apportée | Classement en fonctions opérationnelles, simulations d'interface, réponses simplement générées, fonctions absentes, avec renvoi au fichier et à la ligne du produit ; liste « conserver, reprendre, remplacer » ; onze règles de contrat. |
| Fonctionnement | Lecture du code et de huit dossiers sous runs/, essai de l'application, calcul exploratoire hors produit ; contre-vérification déclarée par sept lecteurs puis trois vérificateurs chargés de réfuter et trois conceptions notées par deux juges (§2) — ce sont des sous-agents, en lecture seule. |
| État | **Exécuté**. Document présent avec références de lignes ; les chiffres « exploratoires » viennent d'un script présent. Pas « vérifié » : aucun critère écrit d'avance, et aucun fichier de sortie du script exploratoire n'est enregistré dans le dépôt. |
| Entrées et sorties | Entrées : src/datathon2026/, config/scenarios.toml, runs/, docs/decisions.md. Sortie : docs/refonte/diagnostic-et-contrat.md (254 lignes). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/diagnostic-et-contrat.md §1 (verdict), §3 (rôle par rôle, avec tools.py:96-125, evidence.py:23, agent.py:98-127), §4 (classement), §5 (décisions), §6, §7 ; docs/refonte/calcul_exploratoire.py (sections 1 à 8 ; la section 8 rejoue la même demande sous trois profils) |
| Dépendances | Bibliothèque du produit (datathon2026.analytics, data, tools) ; dossiers runs/ (ignorés par git, .gitignore:26). |
| Limites | Constats cités sans que leur trace soit dans le dépôt : « quinze affirmations fautives qui passent le vérificateur » (§4), « 62 phrases sur 227 sans référence », « 91 796 jetons sur 280 030 » — je n'ai pas trouvé de fichier de sortie qui les enregistre dans le périmètre lu. Le chiffre −17,5 % en valorisation quotidienne (§1) est contredit par R09 (« Compléments ») : −16,7 % est celui qui a une sortie enregistrée. Une affirmation est marquée « à ma connaissance, non vérifiée ici » (composition de QQQ). |
| Transférabilité | **Fortement couplée**. Porte sur ce produit précis ; seule la grille de classement (opérationnel / simulation d'interface / généré / absent) est réutilisable ailleurs. |
| Inconnues | Trace des quinze injections fautives et des décomptes de phrases : non localisée. |

### X-CAP-030 — Retrait d'une année et multivers à question fixée

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Le registre d'objections de l'exemple du contrat n'éprouvait pas la dépendance à une sous-période. |
| Valeur apportée | Mesure, sur le cas, que retirer la première année (novembre 2021 à novembre 2022) enlève 18,3, 18,7 et 12,3 points au niveau selon l'hypothèse de rendement, sans changer l'ordre des options ; à question fixée, 54 variantes donnent un niveau de 1,0 % à 67,4 % et un écart positif dans les 54. |
| Fonctionnement | Recalcul de la part de trajectoires en retirant tour à tour chaque bloc annuel ; erreur type par retrait d'un bloc (cinq blocs). Multivers : produit cartésien bloc × hypothèse de rendement × échantillon (54 variantes à question fixée) ; version initiale à 486 variantes mêlant aussi seuil et horizon. |
| État | **Exécuté**. Sorties enregistrées, mais aucun critère écrit d'avance (R09 : « ajout après coup, sans critère » ; en-tête de ecart_et_niveau.py). Deux critères d'abord dits « écrits d'avance » avaient été calés sur des résultats déjà vus et ont été retirés (recherche-processus §6). |
| Entrées et sorties | Entrées : rendements hebdomadaires de six actifs. Sorties : niveaux et écarts par variante ; étendue des médianes par choix (rendement 38,3 points, seuil 31,7, année 29,9, horizon 27,4, bloc 1,9). |
| Sources théoriques | [CON-S06], [CON-S07] (analyse multivers) ; Saltelli et collègues 2019 trouvé par un vérificateur. |
| Preuves locales | research/experiences/multivers_exploratoire.py et sorties/multivers_exploratoire.json (clés E1_graines, E2_blocs, E3_retrait_annee, E4_multivers : 486 spécifications) ; research/experiences/ecart_et_niveau.py et sorties/ecart_et_niveau.txt, parties A et B ; research/R09 §X7, §Multivers, §« Deux reproches fondés des vérificateurs » |
| Dépendances | numpy ; marché du projet. |
| Limites | Les 486 variantes viennent des mêmes 261 semaines : une part de variantes de même signe n'est pas une preuve statistique (R09). L'étendue 0,2 % à 90,5 % mêle la question (seuil, horizon) et la méthode et « ne doit pas être citée comme une sensibilité aux choix d'analyse ». Cinq blocs annuels pour une erreur type : ordre de grandeur seulement. |
| Transférabilité | **Adaptable**. Sert de base à une batterie fixe de variantes ; les dimensions du produit cartésien sont écrites en dur dans le script. |
| Inconnues | Marge à partir de laquelle une conclusion « tient » : aucune source ne donne de seuil (recherche-processus §6). |

### X-CAP-031 — Comparateurs désignés par règle : titre de volatilité voisine et fonds le plus corrélé

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Savoir si l'écart attribué au titre demandé lui est propre. |
| Valeur apportée | Sur le cas, 10 % de Bitcoin (volatilité 0,51 contre 0,56) donne un écart de +23,9 à +27,5 points contre +14,7 à +25,2 pour Tesla ; l'écart Tesla moins Bitcoin a un intervalle à 90 % qui contient zéro (−0,138 à +0,186 au taux sans risque) ; l'écart Tesla moins QQQ est positif dans toutes les histoires. |
| Fonctionnement | Partie D : ajout de 10 % de chacun des 27 actifs absents du portefeuille et classement des écarts. dossier_illustratif.py : f_star = fonds de corrélation maximale avec le titre, v_star = titre hors portefeuille de volatilité la plus proche ; stabilité de ces choix en retirant chaque année. |
| État | **Exécuté**. Sorties enregistrées ; aucun critère écrit d'avance (en-têtes des deux scripts). |
| Entrées et sorties | Entrées : rendements hebdomadaires des 31 actifs, table univers (asset_class). Sorties : rang du titre, écarts et intervalles, comparateurs retenus. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | research/experiences/sorties/ecart_et_niveau.txt, partie D (Tesla rang 4 ou 5 sur 27) ; research/experiences/dossier_illustratif.py (variables f_star, v_star) et sorties/dossier_illustratif.txt (QQQ, corrélation 0,59 ; BTC-USD ; « Sans l'année 1 : volatilité la plus proche = SHOP.TO ») ; research/R09 §« Écart et niveau » partie D, §« Compléments » |
| Dépendances | datathon2026.data.load_universe (colonne asset_class commençant par « etf »). |
| Limites | Le comparateur de volatilité change quand on retire la première année (Shopify au lieu de Bitcoin). Un seul titre demandé (Tesla), une seule part (10 %). L'écart Tesla contre QQQ n'est calculé qu'au bloc de 13 semaines. |
| Transférabilité | **Adaptable**. La règle tient en deux lignes ; elle suppose un univers étiqueté fonds / titres. |
| Inconnues | Comportement de la règle pour un titre demandé peu volatil ou un fonds. |

### X-CAP-032 — Contradicteur, objections à test calculé et porte d'amendement

| Champ | Contenu |
|---|---|
| Strate | architecture cible conçue, non construite |
| Problème traité | L'auteur d'une note la conteste mal ; une critique libre n'a pas d'effet vérifiable. |
| Valeur apportée | Une objection n'agit que par un test du catalogue exécuté par le code ; un verdict « change » bloque la restitution jusqu'à un amendement vérifié, un retrait ou une contestation. |
| Fonctionnement | 03, « Le contradicteur » : cinquième conversation de modèle, contexte neuf, lancée par le greffier pour toute version de la note admise par la porte d'analyse. Le code tire d'abord les objections « batterie fixe » de la table des variantes ; le contradicteur dépose un lot d'objections choisies dans une grille (type, affirmation, paramètres en domaines fermés), dont une au moins vise une affirmation favorable et une « ne rien changer ». Le code scelle le critère avant le calcul et rend le verdict : tient, amendée, change, non testable. Effet requis inscrit sur l'affirmation ; l'agent 2 amende en une passe ; une version amendée est réévaluée par le code, non reconfrontée. Une contestation unique rend l'affirmation « non résolue », les deux résultats gardés. Bilan de confrontation calculé par le code. |
| État | **Conçu**. Décrit dans 03 et 04 section 4 ; ni grille des objections, ni seuils, ni code. Aucun essai n'a fait tourner un contradicteur : dans le prototype, « objections » est une fonction pure jouet (chaine.py ligne 20). |
| Entrées et sorties | Entrées : plan scellé, écarts au plan, relevé d'antériorité, note, table des variantes, dossier de preuves, objections « recherche » en attente, grille, catalogue. Sorties : objections en un lot, déclarations de non-couverture ; par le code : résultat, verdict, effet requis, réserves, bilan. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/architecture/03-contrats-des-agents.md, « Le contradicteur, spécialiste de la responsabilité 2 » ; docs/refonte/architecture/04-graphes-et-revision.md section 4 ; docs/refonte/architecture/09-reception.md critères C6, C8, C12, I4 ; docs/refonte/architecture/01-resolutions.md section 10 (corrections sur la reconfrontation et sur les pouvoirs du contradicteur) |
| Dépendances | Table des variantes de la batterie fixe ; grille des objections ; table des seuils ; affirmations à clé stable et sens calculé par le code. |
| Limites | Dites par le contrat (« Limite connue ») : les tolérances chiffrées n'ont aucune source ; seuls rendent un verdict le signe conservé et l'intervalle à 90 % excluant zéro, ce niveau étant une convention sans source ; les types attendant une marge s'exécutent sans verdict. « Ce n'est pas un contrôle indépendant » (00 section 3). Un tour unique est un réglage sans mesure (01 section 8). La revue a relevé que les objections prêtées au contradicteur dans l'exemple étaient déjà faites par le code (01 section 10). |
| Transférabilité | **Adaptable**. Le mécanisme (objection = test du catalogue à critère scellé, verdict par le code, porte d'amendement à trois réponses) se transfère à toute analyse dont les affirmations sont reliées à des calculs ; il suppose une batterie de variantes et une table de seuils. |
| Inconnues | Ce que le contradicteur apporte au-delà de la batterie fixe (mesure I4, non faite) ; son modèle ; la grille. |

### X-CAP-033 — Critères de réception de la future implémentation (onze familles A à K)

| Champ | Contenu |
|---|---|
| Strate | architecture cible conçue, non construite |
| Problème traité | Reconnaître qu'une implémentation réalise l'architecture, et savoir si chaque rôle mérite de rester distinct. |
| Valeur apportée | Liste de critères qui peuvent échouer, avec leur vérification ; sépare conditions de livraison (A à H, J), mesures d'apport (I) et préalables de calibration (K). |
| Fonctionnement | 09 : A dossier (A1 à A13) ; B révision ciblée (B1 à B6) ; C contrats des agents (C1 à C16) ; D types de résultats (D1 à D13) ; E recherche (E1 à E10) ; F sortie, interruption, reprise ; G deux parcours, mêmes contrats ; H route AWS et observation ; I apport de chaque rôle (I1 à I8, dont I6 chaîne contre agent unique, I7 variation entre exécutions, I8 biais de choix) ; J interface ; K calibrations et jeux d'essai (K1 à K10). |
| État | **Conçu**. Critères écrits ; 00 section 11 : « le document 09 ne contient que de l'attendu ». Aucun essai de réception n'est codé ; aucun seuil n'est écrit pour la famille I (« Aucun seuil n'est écrit ici ») ; les jeux d'essai K4, K5 n'existent pas. Quelques critères A et B ont un précédent sur le prototype (A5, A6, A7, A8, forme réduite de B1). |
| Entrées et sorties | Entrées : dossiers produits, journal, jeux d'essai à fabriquer. Sorties : réussite ou échec par critère ; comptes bruts pour I. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/architecture/09-reception.md sections A à K ; docs/refonte/architecture/00-synthese.md section 8, étape 5 |
| Dépendances | Le catalogue (jeux d'essai, table de puissance K3) ; des personnes pour I1, I2, I3, I5, K5, K6, K8, K9. |
| Limites | Dites par le document : « Aucun ne mesure la qualité financière d'une conclusion » ; la moitié des mesures d'apport demandent des personnes (00 section 7). |
| Transférabilité | **Adaptable**. Les familles I et K (apport d'un rôle, agent unique témoin, erreurs semées, placebo) s'appliquent à toute architecture à plusieurs rôles ; A à D sont écrites dans le vocabulaire de ce dossier. |
| Inconnues | Seuils ; jeux d'essai ; faisabilité avant la fermeture du compte. |

## Orchestration, agents et outils

### X-CAP-034 — Boucle d'agent Bedrock Converse à outils exécutés localement

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Laisser un modèle choisir les calculs et rédiger, sans qu'il calcule ni qu'il produise un dossier non contrôlé. |
| Valeur apportée | Un seul modèle, un seul fil de messages ; le code garde la main sur l'exécution des outils, le registre et l'acceptation du dossier. |
| Fonctionnement | BedrockAgent.run (agent.py l.191-239) : au plus MAX_TURNS = 16 appels client.converse (modelId, system=[SYSTEM], toolConfig bâti sur TOOL_SPECS, maxTokens 8192). À chaque tour : si stopReason ≠ tool_use, sortie de boucle ; sinon chaque bloc toolUse est exécuté par _run_tool et son résultat renvoyé en toolResult json ; soumettre_dossier déclenche _build puis Dossier.verification(). Sans dossier accepté à la fin : RuntimeError « l'agent n'a pas soumis de dossier vérifiable dans la limite de tours ». Plusieurs toolUse par tour sont traités en séquence. |
| État | **Vérifié**. tests/test_agent.py::test_agent_loop_runs_tools_rejects_handwritten_number_then_accepts (client simulé FakeBedrock, sans AWS) ; exécutions réelles enregistrées : runs/robert-agent (5 appels), runs/mateo-libre-esg (4 appels). Résultat de la suite de tests non observé dans cette passe (tests non lancés par consigne). Exécution observée le 15 nov. à 17 h 51 : 6 appels Converse, 6 identifiants de requête, 22 affirmations, 97 valeurs reliées, contrôle conforme (evaluation-fusion/preuves/execution-agent-2026-11-15/dossier.json ; preuves/agent-robert-mesures.txt). Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : clé de dossier, dict scénario, demande facultative. Sortie : objet Dossier avec champ aws {service, region, modele, appels[], corrections_demandees}. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:136-239 ; tests/test_agent.py:27-44 ; runs/robert-agent/dossier.json (aws.appels) ; docs/decisions.md D2 |
| Dépendances | boto3 (bedrock-runtime), tools.Session, dossier.Dossier, evidence (vérification), profil AWS nommé « alphaforge ». |
| Limites | Un texte final sans appel d'outil met fin à la boucle et lève RuntimeError (pas de relance). Les messages échangés avec le modèle ne sont pas enregistrés dans le dossier (seuls trace d'outils et métadonnées d'appel le sont). Pas de reprise sur erreur Bedrock dans la boucle (capturée dans cli.run_agent seulement). Variabilité d'une exécution à l'autre non mesurée (docs/comparaison-agent-workflow.md, « Lecture »). |
| Transférabilité | **Adaptable**. Boucle d'environ cinquante lignes ; couplée à Session.call, à Dossier et au vérificateur. |
| Inconnues | Comportement réel quand la limite de 16 tours est atteinte : aucune trace trouvée. |
| Rectifications après relecture | Les tests emploient un client simulé (tests/test_agent.py::FakeBedrock) : la boucle est Vérifiée contre ce client ; l'appel réel à Bedrock est Exécuté, non Vérifié. |

### X-CAP-035 — Erreurs d'outil et demandes hors univers renvoyées au modèle et inscrites dans la trace

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Un appel d'outil invalide ou un titre absent des données ne doit ni arrêter l'exécution ni conduire à une valeur inventée. |
| Valeur apportée | L'erreur est visible dans le dossier (ligne de trace avec clé « erreur ») et le modèle doit rédiger sans la valeur. |
| Fonctionnement | agent.py l.225-231 : toute exception de _run_tool est capturée ; une ligne {outil, arguments, enregistrements: [], duree_ms: 0, erreur} est ajoutée à session.trace et un toolResult status=error contenant str(e) est renvoyé. Pas de liste blanche d'actifs en amont : c'est l'outil qui refuse. |
| État | **Vérifié**. tests/test_agent.py::test_tool_error_is_returned_not_raised (ticker « INCONNU »). Exécution réelle : runs/robert-libre-gamestop/dossier.json, trace « metriques_actif {ticker: GME} » avec erreur « tickers inconnus : ['GME'] », 3 appels Bedrock, 0 correction, résumé commençant par « GME ne figure pas dans l'univers de données du laboratoire ». Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : exception Python. Sortie : toolResult en erreur (texte) et ligne de trace. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:225-231 ; tests/test_agent.py:47-55 ; runs/robert-libre-gamestop/dossier.json |
| Dépendances | Session.trace ; scripts/comparer_agent_workflow.py::call_name gère ce cas. |
| Limites | Dans la trace, un appel en erreur porte le nom vu par le modèle quand TOOL_NAMES ne le traduit pas ; pour metriques_actif, TOOL_NAMES le traduit en asset_metrics, mais le dossier GameStop enregistré porte « metriques_actif » (écart entre le code courant, modifié et non commité, et le dossier enregistré). Que le modèle n'invente pas de valeur ensuite dépend du modèle et du vérificateur, pas de ce mécanisme. |
| Transférabilité | **Autonome**. Motif de sept lignes, réutilisable dans toute boucle d'outils. |
| Inconnues | Aucune. |
| Rectifications après relecture | La ligne d'erreur de runs/robert-libre-gamestop/dossier.json porte le nom « metriques_actif », alors que le code courant écrirait « asset_metrics » : ce dossier a vraisemblablement été produit par une version antérieure de agent.py (interprétation, non vérifiée). |

### X-CAP-036 — Enchaînement fixe de référence (workflow.robert, workflow.amira)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Produire un dossier sans modèle ni AWS, comme référence de comparaison et comme repli. |
| Valeur apportée | Mêmes outils que l'agent, ordre et phrases décidés par le code ; déterministe, sans jeton. |
| Fonctionnement | workflow.py : robert (l.42-125) appelle data_manifest, profile_facts, asset_metrics(actif), portfolio_metrics (actuel, une variante par part étudiée, alternative), share_sweep ; amira (l.128-224) appelle data_manifest, profile_facts, portfolio_metrics, correlation(BTC-USD, ETH-USD), diversification_sweep, puis portfolio_metrics sur la variante si elle existe. Les phrases sont des gabarits f-string remplis de {{R-…}} et {{cmp…}} ; chiffres clés, tableau et graphique sont fixés dans le code. WORKFLOWS = {robert, amira}. |
| État | **Vérifié**. tests/test_workflow.py::test_dossier_passes_verification_and_renders, ::test_changing_a_hypothesis_changes_the_conclusion, ::test_saved_dossier_can_be_reloaded_and_reverified_offline. Exécution : runs/robert-tsla/dossier.json (mode « workflow fixe », 9 appels d'outils, 15 affirmations, 52 valeurs reliées, aws vide), runs/amira-croissance/. Relancé le 15 nov. à 17 h 50 vers un dossier hors dépôt (evaluation-fusion/preuves/demo.txt). Comparaison valeur par valeur aux dossiers enregistrés : robert-tsla, 3 964 valeurs dont 7 différentes ; amira-croissance, 1 660 dont 5 différentes ; toutes sont la date de création ou des durées d'appel (evaluation-fusion/preuves/demo-comparaison.txt). Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : scénario (défaut config/scenarios.toml), session facultative. Sortie : Dossier. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/workflow.py ; tests/test_workflow.py ; runs/robert-tsla/dossier.json |
| Dépendances | tools.py, analytics.py, dossier.py, config/scenarios.toml (clés propres à chaque scénario). |
| Limites | Aucun enchaînement pour Mateo. Textes propres à Robert (« sans retarder sa retraite », l.80) et à Amira (tickers BTC-USD/ETH-USD et groupes « Technologie », « Cryptoactifs » écrits en dur, l.133, 138). Clé de dossier écrite en dur (« robert-tsla », « amira-croissance »). docs/decisions.md (Rectifications) : même demande sous trois profils → treize affirmations identiques sur quinze. |
| Transférabilité | **Fortement couplée**. Deux fonctions écrites pour deux scénarios précis. |
| Inconnues | Aucune. |

### X-CAP-037 — Routage entre agent et enchaînement fixe (ligne de commande et application)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Décider quel mode traite une demande. |
| Valeur apportée | Règle fixe, écrite dans le code : aucun routage par modèle. |
| Fonctionnement | CLI (cli.py l.125-150) : « demo <robert|amira|tous> » → workflow.WORKFLOWS ; « agent <profil> [--demande] [--nom] » → BedrockAgent. Application (app.py produce, l.81-104) : mode « agent » → BedrockAgent ; la demande est dite libre si son texte a été modifié ou si le profil n'a pas d'enchaînement fixe, et seules persona, demande, origine sont alors transmises ; mode « reference » → refus si le profil n'a pas d'enchaînement fixe ou si la demande a été modifiée. Le champ « mode » du dossier indique « workflow fixe » ou « agent Bedrock (<modèle>) ». |
| État | **Exécuté**. Champs « mode » observés dans runs/robert-tsla (« workflow fixe ») et runs/robert-agent (« agent Bedrock (global.anthropic.claude-sonnet-5-5) »). Tests du routage non cherchés (app.py et cli.py hors de la liste de lecture complète). |
| Entrées et sorties | Entrée : commande ou charge utile {profil, mode, demande, hypotheses}. Sortie : Dossier enregistré ou rendu. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/cli.py:46-75, 125-150 ; src/datathon2026/app.py:81-104 ; README.md l.22, 44, 52 |
| Dépendances | workflow.WORKFLOWS, BedrockAgent. |
| Limites | Pas de repli automatique vers l'enchaînement fixe quand Bedrock échoue : cli.run_agent affiche un message et ne produit rien. Mateo n'a que le mode agent. |
| Transférabilité | **Adaptable**. Logique de quelques lignes par point d'entrée. |
| Inconnues | Couverture de test de app.produce : non vérifiée dans cette passe. |

### X-CAP-038 — Essai LangGraph 1.2.22 comme moteur d'enchaînement et de persistance

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Une bibliothèque de graphes peut-elle porter le dossier et le greffier ? |
| Valeur apportée | Établit, par observation, ce que la bibliothèque fait et ne fait pas au regard du contrat : suspension et reprise sur trois processus ; pas d'empreinte, pas de tête par branche, pas de refus d'écriture concurrente, aval entièrement rejoué sans réglage. |
| Fonctionnement | Onze scripts dans un environnement jetable uv ; nœuds des essais 3 à 8 en code déterministe sans modèle ; point de reprise SQLite ; compteurs d'exécution par nœud ; trois essais avec Bedrock (2, 9, 10). |
| État | **Exécuté**. Sorties enregistrées sous research/experiences/technique/langgraph/sorties/ (essaiNN_sortie*.txt, executions_*.log, *.sqlite, appels_bedrock.log à 8 lignes). Statuts dans la fiche : sept « reussi », trois « partiel » (3, 6, 7), un « echoue » (8, écritures concurrentes acceptées). Chaque conduite observée une fois ; modèle global.anthropic.claude-haiku-5-5. Pas de critère écrit d'avance retrouvé, donc pas « verifie ». |
| Entrées et sorties | Entrée : scripts essai01 à essai11 et commun.py. Sortie : fichiers de sortie et verdict « Retenir en partie, au plus. Écarter LangGraph comme dossier et comme greffier ». |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | research/experiences/technique/langgraph/LISEZMOI.md ; research/experiences/technique/langgraph/sorties/essai06_sortie.txt, essai08_sortie.txt, essai04_sortie.txt ; research/fiches/architecture/technique-langgraph.json (verdict, essais) ; docs/refonte/architecture/06-comparatif-technique.md sections 2 à 4 |
| Dépendances | langgraph, langchain-aws, langgraph-checkpoint-sqlite ; 40 paquets nouveaux pour le projet ; profil AWS de l'équipe pour trois essais. |
| Limites | Dites par le LISEZMOI : on mesure le moteur, pas un agent ; seul le point de reprise SQLite éprouvé. La fiche précise : « Je n'ai pas comparé avec les autres options ». |
| Transférabilité | **Autonome**. Scripts indépendants du produit ; relançables par la commande uv du LISEZMOI (les essais 2, 9, 10 demandent Bedrock). |
| Inconnues | Conduite sur d'autres points de reprise ; création de tâches en cours d'exécution (non éprouvée, 06 section 3). |

### X-CAP-039 — Catalogue : dix-neuf tables de règles écrites d'avance par l'équipe, entrées versionnées du dossier

| Champ | Contenu |
|---|---|
| Strate | architecture cible conçue, non construite |
| Problème traité | Le code calcule, rend des verdicts, désigne des comparateurs et la question à poser : ces décisions de fond ne doivent venir ni d'un modèle pendant la demande ni du code de sa propre autorité. |
| Valeur apportée | Localise en un endroit ce qui est décidé avant toute demande ; un seuil modifié ne périme que ce qui l'emploie (02 principe 6, critère A10). |
| Fonctionnement | Tables listées dans 02-dossier.md, « Le catalogue » : décisions et variables (statut nécessaire, à balayer, non informable) ; questions de recherche ; formulations ; hypothèses de rendement (base ou borne d'affichage) ; batterie fixe ; domaines de balayage ; options et comparateurs ; seuils, critères et repères ; convention des mesures historiques ; grille des objections ; préférence vers contrainte ; couverture des horizons ; affichage des statuts ; profondeur proposée ; correspondance professionnelle ; bornes et durées ; plan de supervision ; jeux d'essai ; bibliothèque. Un « gabarit de décision » incomplet ferme le type de demande (« type de demande non ouvert »). |
| État | **Proposé**. Seule la structure est décrite. 02-dossier.md : « Aucune de ces tables n'est encore écrite. » 00-synthese.md section 7 : « Valider l'architecture, c'est valider un contenant ». Les contrats des tables ne sont pas donnés au niveau des champs ; je retiens donc l'état inférieur à « concu » pour le contenu, la structure étant, elle, conçue. |
| Entrées et sorties | Entrée : écriture par l'équipe, hors exécution, toute modification portant deux noms. Sortie : lignes à empreinte lues par les agents (identifiants seulement pour les seuils), les portes, les calculs, le greffier, l'interface. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/architecture/02-dossier.md, « Le catalogue : où vivent les décisions prises d'avance » ; docs/refonte/architecture/01-resolutions.md section 8, ligne « Le catalogue n'est pas écrit » ; docs/refonte/architecture/00-synthese.md section 7 |
| Dépendances | Une équipe qui l'écrit et le relit ; les calibrations K1 à K3 pour ses valeurs chiffrées. |
| Limites | Dites par les documents : contenu donné « de quoi le remplir » pour la seule décision « ajouter un titre » ; « vérifier une diversification » esquissée ; « comparer des actifs » et « jusqu'où accepter le risque » n'ont rien (01 section 8). Valeurs éparses citées (trois ans, quatre longueurs de bloc, deux hypothèses de base) : « premières lignes, pas le catalogue ». |
| Transférabilité | **Adaptable**. L'idée (règles versionnées comme entrées à empreinte, lues par identifiant) se transfère seule ; la liste des tables est liée aux contrats des agents et aux types de résultats de cette conception. |
| Inconnues | Tout le contenu ; le format ; les tolérances de verdict ; les jeux d'essai ; la table de dépendances attendues (critère B1). |

### X-CAP-040 — Contrats des quatre agents en dix points, règles communes et portes

| Champ | Contenu |
|---|---|
| Strate | architecture cible conçue, non construite |
| Problème traité | Donner à chaque rôle (qualification, recherche critique, analyse, restitution) une transformation du dossier reconnaissable et contrôlable, sans conversation partagée ni message d'un rôle à un autre. |
| Valeur apportée | Sépare ce que chaque modèle décide (dans des listes fermées, avec un événement « décision ») de ce que le code vérifie ; rend chaque rôle évaluable par une mesure propre (point 10). |
| Fonctionnement | Neuf règles communes (03-contrats-des-agents.md) : pièces en vigueur remises par le greffier ; outils de la liste seulement ; aucun nombre calculé, seuil ou verdict ; tâche atomique, une tentative et deux reprises, sortie à structure imposée, refus si raison d'arrêt inattendue ; mentions d'appel dans l'événement ; aucune valeur par défaut ; retours typés acheminés par table ; lacune pour ce qui relève de l'équipe ; cinq ou six conversations de modèle. Pour chaque agent : mission et frontières, entrées, outils et droits, décisions autonomes, pièces, format, porte de passage, erreurs et inconnues, retours, vérification de la contribution. Portes : qualification, preuves, analyse, amendement, restitution. Fonctions d'organisation en code : greffier, portes, qualification des données, calculs, batterie fixe, interface. |
| État | **Conçu**. Contrats écrits point par point dans 03 ; aucun code de rôle, de porte ni de consigne n'existe pour cette architecture (00 section 11, « Conçu, non exécuté » : « Les contrats, les portes, les graphes… »). Les prototypes n'exécutent aucun de ces rôles : dans chaine.py les six tâches sont des fonctions pures. |
| Entrées et sorties | Agent 0 : demande, profil, quatre tables -> fiche de qualification. Agent 1 : questions de recherche, bibliothèque, données -> dossier de preuves, plan des méthodes, fiche produit. Agent 2 : fiche, plan des méthodes -> note d'analyse et conclusion en quatre parties. Agent 3 : conclusion, registre, réserves, bilan -> restitution à trois profondeurs, question d'après l'analyse, proposition de classement d'une réaction. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/architecture/03-contrats-des-agents.md (règles communes ; tableaux Agent 0 à Agent 3 ; « Les fonctions d'organisation » ; « Délégations ») ; docs/refonte/architecture/00-synthese.md section 2 ; docs/refonte/architecture/02-dossier.md section 5 (droits) |
| Dépendances | Le dossier, le catalogue, les types de résultats, un moteur de calcul refait « selon le document 05 » (00 section 8, étape 1), une boucle de rôle sur Bedrock. |
| Limites | Dites par les documents : « ces résolutions retirent des décisions aux rôles » et l'apport de chaque rôle n'est pas établi (00 sections 7 et 11 ; 01 section 8) ; le code contrôle des champs, pas le sens d'une phrase (01 section 8, R09, R10) ; aucune fiche de la bibliothèque relue par une personne, donc aucune réponse « étayée » ; durée d'une étude non mesurée, estimée à quinze à trente-cinq appels de modèle (00 section 8). |
| Transférabilité | **Fortement couplée**. Chaque contrat renvoie aux pièces du dossier, aux tables du catalogue et aux types de résultats. La forme en dix points et certaines règles (tâche atomique, question comme pièce de sortie, refus sur raison d'arrêt, décision journalisée avec les candidats) se reprennent seules. |
| Inconnues | Les consignes (aucune n'est écrite) ; le modèle de chaque conversation (00 section 9, décision 5) ; les schémas de sortie ; la tenue des portes sur des sorties réelles. |

### X-CAP-041 — Quatre graphes, table de ce qui rouvre et de ce qui reste, bornes de progrès

| Champ | Contenu |
|---|---|
| Strate | architecture cible conçue, non construite |
| Problème traité | Une étude n'est pas linéaire : une preuve manque, un test écarte une méthode, la personne corrige ; il faut savoir quoi refaire et quand s'arrêter. |
| Valeur apportée | Une règle unique calculée par le greffier : est rouvert ce qui dérive, par les dépendances enregistrées, de la pièce remplacée ; le reste demeure. |
| Fonctionnement | 04 : huit nœuds de l'objectif à la restitution avec critère de résolution et responsable ; quatre graphes (questions, preuves, tâches, parcours utilisateur), le graphe de tâches déduit du graphe de questions ; quatre tâches déclenchées par règle (batterie fixe, confrontation, question décisive, sélection du cas) ; table de seize événements avec ce qu'ils rouvrent ; sous-questions à clé de dédoublonnage, profondeur bornée à trois ; réouvertures bornées à deux par question ; « hypothèse du parent en cause » ; coupure anticipée ; un tour sans changement d'empreinte est arrêté « sans effet » ; budgets ; reprise par relecture du journal. |
| État | **Conçu**. Décrit dans 04. La partie « périmer exactement ce qui dérive » est vérifiée sur le prototype pour six champs et six tâches fixes (essai (a)). Les sous-questions, les bornes de réouverture et la clé de dédoublonnage ne sont pas faites (LISEZMOI dossier_maison). Les quatre graphes ne sont pas dessinés pour un dossier et la table de dépendances attendues n'est pas écrite (01 section 10). |
| Entrées et sorties | Entrées : événements du journal, dépendances enregistrées, bornes du catalogue. Sorties : tâches à lancer, pièces périmées, questions rouvertes ou « non résolues », journal de révision. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/architecture/04-graphes-et-revision.md sections 1 à 4 et 6 ; docs/refonte/architecture/08-schemas.md section 2 (séquence de révision) et schemas/revision-sequence.svg ; research/experiences/technique/dossier_maison/essais.py, CAS_A et essai_a_invalidation ; docs/refonte/architecture/09-reception.md critères B1 à B6 |
| Dépendances | Dossier à dépendances fines (un fait par champ, une ligne par formulation, une affirmation par ligne) ; manifeste d'entrées écrit par le greffier. |
| Limites | Dites par les documents : la révision ciblée « ne vaut que ce que vaut la finesse des liens » (02 section 3) ; les nombres (une confrontation, une passe, deux réouvertures, trois niveaux) sont des réglages du catalogue sans mesure. |
| Transférabilité | **Adaptable**. La règle de dérivation et les bornes se transfèrent avec le dossier ; la table des événements est écrite dans le vocabulaire des pièces de cette conception. |
| Inconnues | Comportement quand les dépendances sont déclarées par un modèle ; terminaison observée sur une étude réelle. |

### X-CAP-042 — État de sortie d'une étude : quatre issues et deux axes (couverture, conditions)

| Champ | Contenu |
|---|---|
| Strate | architecture cible conçue, non construite |
| Problème traité | Une étude peut à la fois dépendre d'une inconnue et laisser une question sans preuve ; une panne ne doit pas passer pour une conclusion. |
| Valeur apportée | L'état est calculé par le greffier et affiché ; aucune restitution n'est préparée dans une étude interrompue. |
| Fonctionnement | 04 section 5 : arrêtée à la qualification ; en attente de la personne ; interrompue ; menée à terme. Pour cette dernière : couverture entière ou partielle, sans condition ou conditionnelle. Règle unique des échecs (03 règle 4) : une tentative et deux reprises ; échec sur le chemin de la conclusion = interruption, sinon couverture partielle. |
| État | **Conçu**. Décrit dans 04 section 5 après correction de la revue (01 section 9 : « Quatre états de sortie qui ne s'excluent pas » ; section 10 : règle unique des échecs). Le prototype a un bilan() à quatre valeurs différentes et vérifie seulement « deux échecs -> interrompue, sans restitution en vigueur » (essai_erreur_outil). |
| Entrées et sorties | Entrées : états des questions, des affirmations et des tâches. Sortie : état de l'étude affiché par l'interface. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/architecture/04-graphes-et-revision.md section 5 ; docs/refonte/architecture/09-reception.md critères F1 à F5 ; research/experiences/technique/dossier_maison/dossier.py, Dossier.bilan |
| Dépendances | États de question (ouverte, résolue, résolue sous condition, sans preuve, non résolue) et d'affirmation (en vigueur, amendée, non résolue). |
| Limites | Dit par le document : « la plupart des études sortiront néanmoins partielles ou conditionnelles, souvent les deux ». |
| Transférabilité | **Autonome**. Vocabulaire d'états applicable à toute chaîne qui distingue interruption technique et résultat ; ne demande que des états de questions et de tâches. |
| Inconnues | Répartition réelle des états sur des demandes. |

## Dossier, mémoire, provenance et versionnement

### X-CAP-043 — Schéma de sortie soumettre_dossier et présentation choisie par le modèle, tracée par le code

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Laisser le modèle choisir chiffres clés, tableau et graphique sans lui laisser écrire de valeurs. |
| Valeur apportée | Chiffres clés et cellules sont des identifiants d'enregistrement ; les séries du graphique sont recalculées par le code à partir de la trace. |
| Fonctionnement | Schéma (agent.py l.75-95) : titre, resume, affirmations[{section (enum SECTIONS), texte, references[]}] requis ; chiffres_cles (maxItems 4 : libelle, valeur=id, detail) ; tableau {titre, colonnes, lignes[{nom, cellules[id|null]}]} ; graphique {type: baisses|groupes, series[], mise_en_evidence}. _build (l.242-274) : sections hors enum ignorées ; identifiant inconnu → problème « référence inconnue », élément écarté ; lignes de tableau complétées ou tronquées à la largeur ; fiche de profil remplie par le code (PROFILE_CARD). _chart (l.276-325) : séries admises = noms de portefeuilles ou tickers déjà passés par portfolio_metrics/asset_metrics sans erreur ; « baisses » limité à 3 séries, alignées sur dates communes ; « groupes » limité à 2 portefeuilles, repère = dernier plafond d'un diversification_sweep. |
| État | **Vérifié**. tests/test_agent.py::test_agent_presentation_is_checked_then_rendered (référence R-0999 rejetée, ligne complétée par None, séries du graphique, rendu sans classe « bad »). Exécution : runs/robert-agent et runs/mateo-libre-esg contiennent 4 chiffres clés, 1 tableau, 1 graphique. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : JSON de l'outil. Sortie : (Dossier, liste de problèmes de présentation). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:75-95, 242-325 ; tests/test_agent.py:58-83 ; runs/robert-agent/dossier.json (chiffres_cles, tableaux, graphiques) |
| Dépendances | dossier.Dossier, report.render, workflow.underwater, analytics.portfolio. |
| Limites | Le schéma JSON n'est pas validé côté code (pas de jsonschema) : seule la tolérance de _build s'applique. Les libellés de lignes et de colonnes du tableau sont du texte libre du modèle ; le contrôle qui leur est appliqué relève de dossier.py/evidence.py, hors périmètre. Deux types de graphique seulement. |
| Transférabilité | **Adaptable**. Dépend des libellés d'enregistrements (« Pire baisse depuis un sommet », « Part du risque du groupe ») pour retrouver les sources. |
| Inconnues | Contrôle exact appliqué aux libellés du tableau et aux chiffres clés : à lire dans dossier.py (hors périmètre). |

### X-CAP-044 — Session d'exécution : registre, trace des appels et retrait des valeurs brutes

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Relier chaque appel d'outil aux enregistrements qu'il crée et garder cette trace dans le dossier. |
| Valeur apportée | La trace liste outil, arguments, identifiants créés et durée ; elle est commune à l'agent et à l'enchaînement fixe. |
| Fonctionnement | tools.Session (tools.py l.27-53) : conv, registry, trace, groups (chargés de config/scenarios.toml [groupes]), market. Session.call(tool, fn, **kwargs) mesure la durée, relève les identifiants ajoutés au registre et ajoute {outil, arguments, enregistrements, duree_ms} à la trace. _summary renvoie {clé: {id, valeur}}. Les outils ajoutent « _brut » (valeurs numériques) pour l'enchaînement fixe ; agent._strip retire toute clé commençant par « _ » avant envoi au modèle. |
| État | **Vérifié**. tests/test_agent.py (assertions d.trace[0]["outil"] == "asset_metrics" et "data_manifest") ; traces des dossiers sous runs/. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Ligne de trace : {outil, arguments, enregistrements[], duree_ms[, erreur]}. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/tools.py:27-57 ; src/datathon2026/agent.py:130-133 (_strip) ; runs/robert-agent/dossier.json (trace : 11 lignes) |
| Dépendances | evidence.Registry, analytics.Market, analytics.Conventions. |
| Limites | Une Session neuve par exécution (pas de cache ni de mémoire entre demandes). lister_actifs et melange hors trace. Les arguments tracés incluent le scénario entier pour profile_facts. |
| Transférabilité | **Adaptable**. Petite classe ; suppose un registre à identifiants séquentiels. |
| Inconnues | Aucune. |
| Rectifications après relecture | Les tests cités ne portent que sur la trace ; le retrait des valeurs brutes (agent.py::_strip) n'a pas de test propre : pour cette partie l'état est Implémenté et Exécuté, non Vérifié. |

### X-CAP-045 — Références dans les textes et formatage français des valeurs

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Empêcher qu'un chiffre soit recopié ou arrondi à la main par le rédacteur (code ou modèle). |
| Valeur apportée | Le texte stocké est un gabarit ; la valeur affichée est produite par le code à partir de l'enregistrement, avec un formatage unique. |
| Fonctionnement | Motif `PLACEHOLDER = \{\{\s*([^{}]+?)\s*\}\}` (evidence.py:38). Formes admises : `{{R-0001}}` (valeur formatée), `{{R-0001.label}}` (libellé), comparaisons (voir entrée suivante). `Registry.render` (evidence.py:254-264) remplace chaque référence ; une référence irrésolue devient `[expr ?]` (evidence.py:243-244). `format_value` (evidence.py:167-190) : pct → valeur×100 à 1 décimale + espace insécable + « % » ; pp → « pt » ; days/weeks/count → entier ; years → 1 décimale, « an » si |valeur arrondie| < 2 sinon « ans » ; ratio → 2 décimales ; date ISO → « 12 nov. 2026 » ; None → « non disponible » ; virgule décimale, espace insécable pour les milliers, signe moins typographique U+2212, pas de « −0,0 » (evidence.py:162-164). |
| État | **Vérifié**. Tests nommés : `test_clean_template_passes_and_renders`, `test_formatting` (tests/test_evidence.py:21-25, 126-130). Résultat des tests non observé par moi (exécution confiée à un autre) ; docs/technique.md:33 les déclare exécutés. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : gabarit + registre. Sortie : texte rendu (`texte` dans le JSON) ou HTML (report.render_html). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/evidence.py:27-43, 157-190, 241-264 ; tests/test_evidence.py:21-25, 126-130 ; runs/robert-agent/dossier.json affirmation A-004 (gabarit et texte) |
| Dépendances | Registre. |
| Limites | Unités fermées : pct, pp, days, weeks, count, years, ratio, date, text ; aucune unité monétaire. `{{X.label}}` insère un libellé libre, que le contrôle des chiffres n'examine pas (il est retiré avec la référence, evidence.py:300). |
| Transférabilité | **Autonome**. Fonctions pures. |
| Inconnues |  |

### X-CAP-046 — Comparaisons calculées {{cmp:…}}, {{cmpabs:…}}, {{cmpduree:…}}

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Le sens d'une comparaison (« supérieur », « plus forte ») peut contredire les chiffres s'il est écrit à la main. |
| Valeur apportée | Le mot de comparaison est choisi par le code à partir des deux valeurs arrondies telles qu'affichées. |
| Fonctionnement | `CMP_EXPR = (cmp|cmpabs|cmpduree):([A-Z]-\d{4}):([A-Z]-\d{4})` (evidence.py:39). `comparison_word` (evidence.py:96-107) : cmp → « supérieure à / inférieure à / égale à » ; cmpabs (valeurs absolues) → « plus forte que / moins forte que / aussi forte que » ; cmpduree, rapport r = x/y → « atteint ou dépasse » (r ≥ 1), « atteint presque » (r ≥ 0,9), « représente une part importante de » (r ≥ 0,5), « reste nettement inférieure à » sinon ; None si x < 0 ou y ≤ 0. Arrondi préalable par `rounded_value` selon `_DECIMALS` (pct et pp : 3 décimales de la fraction, soit 0,1 point ; years : 1 ; ratio : 2 ; days, weeks, count : 0) (evidence.py:42, 92-93). Comparaison invalide (rendue `[… ?]`) si unités non numériques, unités différentes ou valeur None (evidence.py:245-250). report.py refait le même calcul côté HTML (`_cmp_word`, report.py:62-66). |
| État | **Vérifié**. Tests nommés : `test_comparison_direction_is_computed`, `test_duration_comparison_is_graded_on_the_ratio`, `test_comparison_between_incompatible_units_is_invalid` (tests/test_evidence.py:53-58, 85-93, 113-115). Usage observé : `{{cmpduree:R-0007:P-0007}}` dans le résumé de runs/robert-tsla/dossier.json. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : deux identifiants de même unité numérique. Sortie : une locution. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/evidence.py:39, 92-107, 245-250 ; src/datathon2026/report.py:62-66, 75-82 ; tests/test_evidence.py:53-58, 85-93, 113-115 ; docs/decisions.md:65 (D5) |
| Dépendances | Registre, table `_DECIMALS`. |
| Limites | Les seuils 0,9 et 0,5 de cmpduree sont des constantes du code, sans justification écrite trouvée dans le périmètre lu. La comparaison ne dit rien de la pertinence de comparer ces deux grandeurs : le diagnostic relève qu'une comparaison calculée sur une durée tronquée (minorant inscrit « mesuré ») a produit une conclusion fausse (robert-libre-or, A-008 ; docs/refonte/diagnostic-et-contrat.md:106). Aucune tolérance ni incertitude : l'égalité est l'égalité des arrondis. Trois locutions seulement, au féminin par défaut. |
| Transférabilité | **Autonome**. Fonctions pures ; le calcul est dupliqué dans report.py (`_cmp_word`), à transférer ensemble. |
| Inconnues |  |
| Rectifications après relecture | Inexact sur un point : report.py::_cmp_word appelle evidence.comparison_word ; le calcul du mot n'est pas dupliqué. Seules la condition de validité et la boucle de substitution sont écrites deux fois (evidence.py:241-250 et report.py:62-80). |

### X-CAP-047 — Accord grammatical des comparaisons par le code

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Une locution insérée mécaniquement produit des fautes (« supérieure à le plafond », « un rendement inférieure ») constatées à la relecture (docs/decisions.md:61). |
| Valeur apportée | Le texte rendu est accordé sans que le rédacteur écrive le comparatif ; le sens n'est pas modifié. |
| Fonctionnement | `join_comparison(word, tail, before)` (evidence.py:133-155) : contractions à+le → au, à+les → aux, de+le → du, de+les → des ; absorption d'un « à », « que » ou « de » répété par le rédacteur ; élision de « que »/« de » devant voyelle ; passage au masculin (supérieur, inférieur, égal, fort) si `_masculine_noun(before)` : heuristique sur déterminants, prépositions, copules et adverbes listés (evidence.py:66-71, 110-130), féminin par défaut. |
| État | **Vérifié**. Tests nommés : `test_computed_comparison_agrees_with_the_following_word`, `test_computed_comparison_agrees_in_gender_with_the_qualified_noun` (tests/test_evidence.py:61-82), sur 15 phrases. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : locution, texte avant, texte après. Sortie : locution accordée et nombre de caractères absorbés. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/evidence.py:65-71, 110-155 ; tests/test_evidence.py:61-82 |
| Dépendances | Listes fermées de mots français. |
| Limites | Heuristique : listes fermées (`_DETERMINERS` : 13 formes ; pas de pluriel « les/des/ces », pas d'accord en nombre). Validée sur les 15 phrases des tests seulement. Propre au français. |
| Transférabilité | **Adaptable**. Se transfère avec les comparaisons calculées ; sans objet si les locutions sont reformulées de façon invariable. |
| Inconnues | Taux de fautes d'accord sur les dossiers réels : non mesuré. |

### X-CAP-048 — Statut d'une affirmation = statut le plus faible de ses références, avec héritage des hypothèses

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Une conclusion calculée sous une hypothèse ne doit pas s'afficher comme mesurée. |
| Valeur apportée | Chaque affirmation porte un statut dérivé mécaniquement de ce qu'elle cite. |
| Fonctionnement | `STATUS_ORDER = (mesuré, source, déclaré, scénario, hypothèse, inconnu)` (evidence.py:17). `Claim.status` (evidence.py:321-327) : références = identifiants du gabarit + liste `refs` ; ajoute les enregistrements listés dans `inputs['depend_de']` de chaque référence (un seul niveau, pas de fermeture transitive) ; renvoie le statut de rang le plus élevé ; « non étayée » si aucune référence connue. Affiché à droite de chaque affirmation dans le HTML (report.py:279-284), italique pour hypothèse/scénario, grisé pour inconnu (report.py:42-43). |
| État | **Vérifié**. Tests nommés : `test_claim_status_is_weakest_reference_and_unsupported_claim_flagged`, `test_status_inherits_hypothesis_dependencies` (tests/test_evidence.py:118-123, 133-136). Observé : robert-tsla, 15 affirmations : 5 hypothèse, 2 déclaré, 2 scénario, 2 inconnu, 2 mesuré, 1 source, 1 non étayée (A-001, section cadre). Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : affirmation + registre. Sortie : champ `statut` de chaque affirmation dans le JSON. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/evidence.py:17-18, 311-334 ; tests/test_evidence.py:118-123, 133-136 ; runs/robert-tsla/dossier.json clé `affirmations` |
| Dépendances | Champ `inputs.depend_de` posé par les outils. |
| Limites | Le statut est une étiquette, pas une qualité de preuve : une valeur issue d'une seule trajectoire est « mesurée » ; le statut d'un paragraphe couvre aussi ses phrases de jugement ; sur demande libre, les hypothèses posées par le modèle sont attribuées au « scénario de démonstration » (diagnostic:57). L'affirmation de cadre s'enregistre avec le statut « non étayée » (observé A-001). docs/technique.md:21 donne l'ordre sans « source », alors que le code le place en deuxième rang. `STATUS_HELP` (report.py:18-24) n'a pas d'entrée « source » : l'infobulle affiche alors « aucun enregistrement cité ». Héritage sur un seul niveau de `depend_de`. |
| Transférabilité | **Autonome**. Dépend seulement de la convention `depend_de`. |
| Inconnues |  |

### X-CAP-049 — Extension du contrôle aux textes affichés hors affirmations (résumé, chiffres clés, en-têtes et lignes de tableaux)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Les textes de présentation choisis par le modèle peuvent porter des chiffres sans passer par les affirmations. |
| Valeur apportée | Le résumé, les libellés et détails des chiffres clés, les en-têtes de colonnes et les noms de lignes sont soumis aux mêmes règles. |
| Fonctionnement | `Dossier._display_claims` (dossier.py:53-64) fabrique des affirmations synthétiques : `K-NN` (libellé + détail d'un chiffre clé, référence = sa valeur), `T-t-cj` (en-tête de colonne, références = cellules de la colonne), `T-t-lk` (nom de ligne, références = cellules de la ligne) ; le résumé devient `A-000` (dossier.py:68-69). `verification()` (dossier.py:66-73) renvoie `affirmations` = nombre d'affirmations propres et `elements_verifies` = total contrôlé. |
| État | **Exécuté**. Observé : robert-tsla `elements_verifies` 30 pour 15 affirmations ; robert-agent 33 pour 18. Un test `test_agent_presentation_is_checked_then_rendered` existe (tests/test_agent.py:58) mais je ne l'ai pas lu ; je ne l'emploie donc pas pour élever l'état. |
| Entrées et sorties | Entrée : `highlights`, `tables`, `summary`. Sortie : `verification.problemes` indexé par K-, T-, A-000. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/dossier.py:53-73 ; runs/robert-tsla/dossier.json clé `verification` ; runs/robert-agent/dossier.json clé `verification` |
| Dépendances | Vérificateur. |
| Limites | Non couverts : `titre` du dossier, `titre` d'un tableau, tous les textes de graphique, intitulés de `fiche_profil`. Les noms de lignes et en-têtes sont contrôlés comme des « constats », donc soumis à la garde lexicale. |
| Transférabilité | **Adaptable**. Lié à la forme des objets `chiffres_cles` et `tableaux`. |
| Inconnues |  |
| Rectifications après relecture | tests/test_agent.py::test_agent_presentation_is_checked_then_rendered, lu depuis, vérifie le refus d'un résumé à comparaison manuscrite et d'un chiffre clé à référence inconnue : couverture partielle par un test. |

### X-CAP-050 — Contrat du dossier de décision (Dossier.to_dict / from_dict, dossier.json)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Avoir un objet unique, enregistrable et rechargeable, qui porte textes, valeurs, trace et provenance. |
| Valeur apportée | Le JSON contient tout ce qu'il faut pour revérifier et redessiner le dossier sans recalcul ni modèle. |
| Fonctionnement | 16 clés (dossier.py:75-104) : scenario, titre, persona, demande, mode, cree_le, resume{gabarit, texte}, affirmations[{id A-NNN, section, gabarit, texte, references, statut}], enregistrements{id: Record + display}, trace[{outil, arguments, enregistrements, duree_ms, erreur?}], graphiques[{titre, type ligne|barres, unite, series{nom: [[x, y]…]}, sources, mise_en_evidence?, note?, sous_titre?, etiquettes?, repere?}], fiche_profil[[intitulé, id]], chiffres_cles[{libelle, valeur, detail}], tableaux[{titre, colonnes, lignes[{nom, cellules[id|null]}]}], aws{service, region, modele, appels[{requestId, stopReason, inputTokens, outputTokens, latenceMs}], corrections_demandees}, verification{affirmations, valeurs_reliees, affirmations_en_echec, problemes, ok, elements_verifies}. Sections admises : cadre, profil, constat, tension, alternative, question, condition, limite (dossier.py:12-21). `from_dict` (dossier.py:106-120) reprend gabarits et enregistrements et recalcule texte, statut, display et verification. |
| État | **Vérifié**. Test nommé `test_saved_dossier_can_be_reloaded_and_reverified_offline` (tests/test_workflow.py:66-73) : aller-retour identique sur les dossiers du workflow fixe. Les dossiers d'agent ne sont pas couverts par ce test. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Producteurs : workflow.py et agent.py (importent `Dossier`). Consommateurs : report.render, cli.save / rerender / write_index, scripts/comparer_agent_workflow.py (d'après docs/decisions.md:29). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/dossier.py:12-126 ; runs/robert-tsla/dossier.json ; runs/robert-agent/dossier.json ; tests/test_workflow.py:66-73 |
| Dépendances | evidence.py. |
| Limites | Aucun champ de version (ni du schéma, ni du code, ni du vérificateur), aucune empreinte du dossier, aucun lien vers un dossier précédent, aucun identifiant d'exécution autre que `scenario` (qui sert aussi de nom de répertoire, donc écrasé à la réexécution). `texte` et `gabarit` sont redondants ; seul `gabarit` fait foi au rechargement. `trace` consigne les arguments et les identifiants produits, pas les sorties d'outils. Pas de consigne système, pas de messages du modèle, pas de paramètres d'inférence dans le dossier. |
| Transférabilité | **Adaptable**. Structure réutilisable ; les sections et objets de présentation sont ceux de ce produit. Le diagnostic propose de conserver dossier.py (diagnostic:99). |
| Inconnues |  |

### X-CAP-051 — Revérification et régénération hors ligne (commande « rendre »)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Pouvoir recontrôler un dossier d'agent après la fermeture du compte AWS, ou après un durcissement du vérificateur. |
| Valeur apportée | Le vérificateur courant est repassé sur les dossiers enregistrés ; le HTML est régénéré ; aucun appel AWS, aucun recalcul. |
| Fonctionnement | `cli.rerender` (cli.py:77-83) : pour chaque `*/dossier.json` du répertoire de sortie, `Dossier.from_dict` puis `save` (réécrit dossier.json et dossier.html au même endroit, cli.py:20-29) ; `write_index` régénère index.html (cli.py:32-43). Le motif `*/dossier.json` n'atteint pas `_archives/<nom>/dossier.json` (deux niveaux). |
| État | **Exécuté**. docs/decisions.md:67 rapporte que robert-libre-or, revérifié hors ligne avec le contrôle renforcé, a été refusé pour « dix pour cent », puis rejoué, et que les huit dossiers passent le contrôle courant ; les huit dossiers courants ont `verification.ok = true` avec la clé `elements_verifies`. La fonction `rerender` elle-même n'a pas de test nommé ; l'aller-retour `from_dict`/`to_dict` en a un (tests/test_workflow.py:66-73). Relancée le 15 nov. à 17 h 50 sur une copie de runs/ : huit dossiers, zéro affirmation en échec (evaluation-fusion/preuves/rendre.txt). |
| Entrées et sorties | Entrée : runs/*/dossier.json. Sortie : mêmes fichiers réécrits + runs/index.html. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/cli.py:77-83, 135, 144-145 ; src/datathon2026/dossier.py:106-120 ; docs/technique.md:23 ; docs/decisions.md:67 |
| Dépendances | dossier.py, report.py, evidence.py. |
| Limites | Réécriture en place des dossiers qui servent de preuve d'exécution AWS (diagnostic:235) ; `cree_le` est conservé, aucune date ni version de revérification n'est inscrite. Elle recontrôle la cohérence du texte avec le registre enregistré sans recalculer les valeurs (diagnostic:51). Les dossiers archivés ne sont pas revérifiés. |
| Transférabilité | **Adaptable**. Dépend du contrat JSON ; le principe (gabarits + registre enregistrés, rendu rejouable) se transfère. |
| Inconnues | Sortie de la dernière exécution de `rendre` : non enregistrée dans le dépôt. |

### X-CAP-052 — Archivage des versions de dossiers

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Conserver un dossier avant qu'une réexécution ou `rendre` ne l'écrase. |
| Valeur apportée | Trois copies antérieures de dossiers d'agent subsistent pour comparaison manuelle. |
| Fonctionnement | Aucun mécanisme dans le code : aucune occurrence de `_archives` ou d'archivage dans src/datathon2026/. Trois répertoires copiés à la main sous runs/_archives/ : `robert-agent-2026-11-15-avant-corrections` (cree_le 05:22 UTC), `robert-agent-2026-11-15-0642-avant-garde-lexicale` (11:42 UTC), `amira-agent-2026-11-15-0646-avant-garde-lexicale` (11:46 UTC), chacun avec dossier.json et dossier.html. Le nom du répertoire porte la date et le motif. |
| État | **Proposé**. Pratique manuelle constatée par ses résultats, sans code ni procédure écrite trouvée ; ce n'est pas une capacité du produit. `runs/` est exclu de git (.gitignore:26), donc ni les dossiers ni les archives ne sont versionnés. |
| Entrées et sorties | Copies de répertoires. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | runs/_archives/ (trois répertoires) ; .gitignore:26 ; docs/etat.md:85, 114 ; docs/refonte/diagnostic-et-contrat.md:235 |
| Dépendances | Aucune. |
| Limites | Pas d'archivage automatique, pas de numéro de version, pas de lien entre versions, pas de différentiel. docs/etat.md:85 signale deux exécutions de robert-libre-or écrasées. Aucune copie hors de la machine (docs/etat.md:114). |
| Transférabilité | **Autonome**. Rien à transférer hormis la convention de nommage. |
| Inconnues |  |
| Rectifications après relecture | L'état décrit l'absence de mécanisme, non l'absence de fichiers : trois copies manuelles existent sous runs/_archives/. |

### X-CAP-053 — Livrables de présentation : résumé d'une page et plan de vidéo

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | L'énoncé demande un résumé d'une page, une vidéo d'environ cinq minutes et une documentation technique. |
| Valeur apportée | Seuls les intitulés demandés par l'énoncé sont posés. |
| Fonctionnement | docs/one-pager.md : six rubriques sans contenu. docs/video.md : six étapes « à minuter », sans texte ni minutage. docs/exigences.md : matrice E1 à E12 avec une colonne « État ». |
| État | **Proposé**. docs/one-pager.md (10 lignes) et docs/video.md (10 lignes) ne contiennent que des titres. docs/exigences.md:16, 18 les marque « à faire » ; docs/etat.md:104-105 les liste parmi les actions suspendues. Aucun fichier vidéo trouvé dans les fichiers lus. |
| Entrées et sorties | Sans objet. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/one-pager.md:1-10 ; docs/video.md:1-10 ; docs/exigences.md:5-18 ; docs/etat.md:104-105 |
| Dépendances | Compte AWS actif pour enregistrer le parcours agent avant le 16 nov. 13 h 59 (docs/etat.md:104). |
| Limites | La matrice docs/exigences.md n'a pas été mise à jour : E1, E2, E3 y sont « à faire » alors que docs/etat.md décrit des exécutions réelles ; ses « inconnues logistiques » (ligne 22) sont levées ailleurs (docs/etat.md:44-50). |
| Transférabilité | **Autonome**. Gabarits vides. |
| Inconnues | Aucune. |

### X-CAP-054 — Prototype du dossier et du greffier (dossier.py, 313 lignes, bibliothèque standard, sans modèle)

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Savoir si les conduites exigées par le contrat 02 (invalidation ciblée, retour en vigueur, branche, reprise, refus d'écriture concurrente, retrait, affichage et réaction, export des relations) tiennent dans un code court sans dépendance. |
| Valeur apportée | Fournit une réalisation exécutable de la partie mécanique du contrat et trois précisions reportées dans le contrat (empreinte du seul contenu ; une pièce cite ce sur quoi elle porte ; « périmée » n'est pas une invalidation PROV). |
| Fonctionnement | Classe Dossier : ranger() écrit une pièce sous le SHA-256 de canon({type, corps}) par renommage atomique ; ajouter() écrit un événement dans journal/<branche>.jsonl sous fcntl.flock et lève TeteDepassee si « prolonge » n'est pas le sommet ; tete() recalcule emplacement -> pièce à partir des dépôts puis des clés de tâche présentes au journal ; Tache.cle() = empreinte(nom, version, empreintes des entrées) ; etats() rend en vigueur, périmée, remplacée, erronée avec l'événement cause ; ouvrir_branche(), retirer(), afficher(), reagir(), affichages_a_signaler(), bilan(), avancer(), verifier(). Chaîne jouet de six tâches à fonctions pures et valeurs fictives (chaine.py). |
| État | **Vérifié**. Script hors produit à assertions, attendus écrits d'avance dans le code (par exemple CAS_A, essais.py ligne 141), sortie enregistrée : sorties/essais.txt, « 118 assertions réussies en 1.359 s (Python 3.12.7) ». Portée de la vérification : chaîne jouet fixe, sans modèle, une seule machine, quatre passages complets (LISEZMOI, « Ce qui n'a pas été fait »). Non relancé dans le cadre de cet inventaire. Relancé le 15 nov. à 17 h 55 : 118 assertions réussies, code de sortie 0 (evaluation-fusion/preuves/prototype-dossier.txt). |
| Entrées et sorties | Entrées : liste de Tache (nom, auteur, emplacements lus, emplacement écrit, version), table des droits auteur -> préfixes, fonctions par tâche. Sorties : pieces/<empreinte>.json, journal/<branche>.jsonl, dictionnaires tete/etats/bilan, liste d'anomalies, export PROV-JSON (export_prov.py). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | research/experiences/technique/dossier_maison/dossier.py (Dossier, Tache, canon, empreinte, TeteDepassee, EcritureInterdite) ; research/experiences/technique/dossier_maison/essais.py (essai_a_invalidation, essai_b_variante, essai_c_reprise_et_question, essai_d_concurrence, essai_e_retour, essai_f_erronee, essai_g_affichage, essai_h_prov, essai_empreintes_et_droits, essai_erreur_outil, essai_integrite, essai_ligne_tronquee) ; research/experiences/technique/dossier_maison/sorties/essais.txt et essais_avec_prov.txt ; research/experiences/technique/dossier_maison/sorties/contre_epreuve_verrou.json ; research/experiences/technique/dossier_maison/sorties/verif_sqlite.txt ; research/fiches/architecture/technique-dossier-maison.json (champs verdict, essais) |
| Dépendances | Python standard (fcntl, hashlib, json, os, tempfile) ; paquet prov 3.3.0 facultatif pour la relecture de l'export. |
| Limites | Dites par le LISEZMOI : graphe fixe de six tâches, pas de sous-questions ni de bornes de réouverture ; aucune porte de contenu, seuls les droits de dépôt ; une tâche à la fois ; panne entre rangement et événement non provoquée ; fcntl absent sous Windows, verrou non sûr sur disque partagé ; tout le journal relu à chaque opération. Constaté à la lecture du code : la forme canonique exigée par 02 section 8 (précision fixée, textes normalisés) n'est pas implémentée, l'essai constate seulement que 1 et 1.0 diffèrent ; le catalogue est une pièce unique et non des lignes à empreinte propre ; le vocabulaire diffère du contrat (« sommet » = dernier événement, « tête » = état en vigueur, alors que 02 principe 4 appelle « tête » le dernier événement) ; bilan() rend quatre états (à poursuivre, interrompue, en attente de la personne, complète) et non les états de 04 section 5. |
| Transférabilité | **Autonome**. Un fichier sans dépendance ni lien au produit ; il s'emploie avec toute liste de tâches à entrées déclarées. L'adressage est par emplacement nommé, ce qui suppose un graphe de tâches connu d'avance. |
| Inconnues | Conduite avec des tâches non déterministes (modèle) et volatiles (recherche web) ; mêmes empreintes sur deux machines ; tenue au-delà de quelques dizaines d'événements par étude. |
| Rectifications après relecture | Le fichier désigné est research/experiences/technique/dossier_maison/dossier.py, à ne pas confondre avec src/datathon2026/dossier.py (objet différent, même nom de classe). sorties/essais_avec_prov.txt indique 119 assertions sous Python 3.13.0 avec le paquet prov, contre 118 sans. |

### X-CAP-055 — Contrat du dossier de décision : pièces immuables adressées par l'empreinte de leur contenu, journal chaîné, état en vigueur déduit

| Champ | Contenu |
|---|---|
| Strate | architecture cible conçue, non construite |
| Problème traité | Relier quatre rôles et permettre à un tiers de lire comment une demande devient une conclusion, puis pourquoi elle change, sans réécrire ni perdre de version. |
| Valeur apportée | Attribue chaque élément d'une conclusion à l'une de trois mains (règle écrite d'avance, choix d'un modèle, déclaration de la personne) et rend possible une révision qui ne refait que ce qui dérive de la pièce remplacée. |
| Fonctionnement | Six principes (docs/refonte/architecture/02-dossier.md, section 1) : ajout seul ; empreinte du seul contenu, les mentions (auteur, activité, empreintes d'entrées, date, identifiant de requête AWS) étant portées par l'événement de dépôt ; journal chaîné daté par le greffier seul ; état en vigueur calculé à la tête d'une branche ; aucun nombre calculé, seuil ou verdict écrit par un modèle (exception contrôlée : l'agent 0 recopie les valeurs dites) ; lignes du catalogue comptées parmi les empreintes d'entrée. Environ quarante objets en dix familles (section 2), onze relations (section 3), cinq états d'une pièce (section 4), table des droits par auteur (section 5), trois sortes de tâches pour le réemploi (section 7), exigences du support dont la forme canonique (section 8). |
| État | **Conçu**. Contrat décrit en entier dans 02-dossier.md ; le document se dit lui-même « proposition de conception » et précise que « le schéma exact se fixe à la construction ». Aucun code du produit ne l'implémente (00-synthese.md, ligne 3 : « Rien n'est construit »). Une partie réduite est exercée par le prototype hors produit (entrée distincte). |
| Entrées et sorties | Entrées : pièces déposées par les rôles, le code, la personne, l'équipe. Sorties : état en vigueur par branche, vues calculées (registre des essais, écarts au plan, registre des objections, relevé d'antériorité, mémoire de synthèse, parcours utilisateur, état de l'étude), export rejouable sans AWS. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/architecture/02-dossier.md sections 1 à 8 ; docs/refonte/architecture/08-schemas.md section 3 (diagramme d'états) ; docs/refonte/architecture/06-comparatif-technique.md, table « Ce que les essais imposent aux contrats » |
| Dépendances | Le catalogue (principe 6) ; un greffier en code ; des portes par rôle ; une forme canonique des nombres et des textes. |
| Limites | Dites par le document : un lien « dérive de » omis par un modèle peut laisser en vigueur une pièce qui aurait dû être périmée (02 section 3, « Maille des dépendances » ; 01 section 8, R14) ; plusieurs listes fermées restent à tenir en un seul endroit (01 section 10) ; la compréhension n'est pas mesurée (02 section 6). |
| Transférabilité | **Adaptable**. Le noyau (empreinte de contenu, journal chaîné, tête déduite, états) se transfère sans les agents. Les objets métier (affirmation, objection, réserve, plan des méthodes) supposent le catalogue et les contrats des rôles. |
| Inconnues | Schéma exact des champs ; tenue des empreintes sur une autre machine (00 section 11, « Non établi ») ; comportement avec des pièces écrites par un modèle. |

## Interface, adaptation, visualisation et réversibilité

### X-CAP-056 — Rendu HTML autonome du dossier

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Présenter le dossier à un lecteur, chaque valeur restant reliée à son enregistrement. |
| Valeur apportée | Un fichier HTML unique, sans dépendance externe (CSS et JS en ligne), dérivé du JSON. |
| Fonctionnement | `report.render(d)` (report.py:482-549) : en-tête (titre, demande, profil fictif, date `cree_le`, mode, mention « Simulation, aucun conseil personnalisé »), fiche de profil, synthèse, ligne de contrôle, chiffres clés, sections numérotées dans l'ordre de `SECTION_TITLES` (report.py:471-479 ; graphiques dans « constat », tableaux dans « alternative »), annexe repliable : registre des preuves regroupé par sujet, valeurs citées d'abord, conventions numérotées, non cités repliés (report.py:317-378), légende des statuts, contribution AWS (tableau RequestId, jetons, latence, arrêt), problèmes éventuels, trace d'exécution. Chaque valeur est un lien vers la ligne du registre avec infobulle identifiant · libellé · statut · période (report.py:35-59) ; bouton « Afficher les références » ; thème sombre par `prefers-color-scheme`. Pied de page = textes de la section `cadre`. `render_index` (report.py:552-564) liste les dossiers. |
| État | **Exécuté**. Fichiers runs/*/dossier.html présents (huit courants, 29 à 110 ko). `test_dossier_passes_verification_and_renders` (tests/test_workflow.py:16-22) vérifie seulement l'absence de `class="bad"` pour les dossiers du workflow fixe ; aucun test de contenu ou d'affichage. docs/technique.md:37 : rendu à moins de 500 px et compréhension par des utilisateurs non vérifiés. |
| Entrées et sorties | Entrée : dict du dossier. Sortie : chaîne HTML. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/report.py:1-7, 31-106, 244-378, 383-564 ; runs/robert-tsla/dossier.html ; runs/index.html |
| Dépendances | Importe d'evidence.py : `_DECIMALS`, `CMP_EXPR`, `MINUS`, `PLACEHOLDER`, `comparison_word`, `format_value`, `join_comparison`, `rounded_value` (report.py:16). |
| Limites | Un seul gabarit de page, un seul niveau de lecture. `SOURCE_DONNEES` est une constante identique pour toutes les figures (report.py:27). Les valeurs de la fiche de profil sont affichées sans lien. La note de tableau est un texte fixe ; `refs[:0]` y supprime toujours la liste des valeurs citées (report.py:274-275). Arguments de trace tronqués à 110 caractères (report.py:516). Rendu refait à partir du `gabarit`, sauf le pied de page et l'index qui lisent `texte`. |
| Transférabilité | **Adaptable**. Couplé au contrat JSON et aux fonctions d'evidence.py. |
| Inconnues |  |

### X-CAP-057 — Graphiques SVG tracés par le code à partir de séries enregistrées

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Le modèle ne doit ni calculer ni dessiner. |
| Valeur apportée | Le modèle (ou le workflow) choisit les séries ; le code trace ; les points sont dans le JSON, donc le graphique se régénère hors ligne. |
| Fonctionnement | `line_chart` (report.py:138-191) : 3 séries au plus, axe vertical de 0 vers le négatif (conçu pour des baisses depuis le sommet), grille par pas de 0,1 ou 0,2, graduations d'années, une seule couleur d'accent pour la série `mise_en_evidence`, les autres en gris, étiquettes en bout de ligne décalées de 15 px, infobulle JS, table des données une semaine sur quatre. `bar_chart` (report.py:194-238) : barres horizontales depuis zéro, 3 séries au plus, échelle plafonnée à 1,0, repère vertical optionnel (`repere`). Sous chaque figure : sources, note, dernière donnée, identifiants cités (report.py:129-135). |
| État | **Exécuté**. Observé : `graphiques` de robert-tsla et robert-agent contiennent une figure de type ligne, 3 séries de 262 points, `sources` = 3 identifiants. Aucun test nommé ne porte sur le tracé lu dans mon périmètre. |
| Entrées et sorties | Entrée : objet graphique {titre, type, unite, series, sources…}. Sortie : `<figure>` SVG. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/report.py:109-238 ; runs/robert-tsla/dossier.json clé `graphiques` ; docs/technique.md:7 ; docs/decisions.md:65 |
| Dépendances | Aucune bibliothèque de tracé. |
| Limites | Deux types seulement ; le graphique en ligne suppose des valeurs ≤ 0 et un axe X commun pris sur la première série ; sous-titre par défaut « baisse par rapport au plus haut précédent » ; les titres, notes et étiquettes ne passent pas par le vérificateur. |
| Transférabilité | **Adaptable**. Fonctions autonomes prenant un dict ; dépendent des variables CSS de la page. |
| Inconnues |  |

### X-CAP-058 — Application web locale : profil, hypothèses, recalcul par l'enchaînement fixe

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Permettre à une personne de modifier une hypothèse d'un scénario de démonstration et de voir le dossier recalculé, sans ligne de commande. |
| Valeur apportée | Le recalcul est réel (appel de workflow.WORKFLOWS avec le scénario modifié) et le résultat du contrôle de preuves est affiché avec le dossier. |
| Fonctionnement | Serveur http.server lié à 127.0.0.1 (app.py:360), deux routes : GET / (page unique, valeurs initiales injectées par bootstrap(), app.py:119-136) et POST /api/dossier (app.py:326-338). Colonne de gauche : choix parmi trois profils (PERSONAS, app.py:25), zone de demande, hypothèses, mode, bouton « Produire le dossier ». Hypothèses modifiables pour Robert : actif étudié, part (1 à 30 %), seuil de perte (1 à 60 %), horizon (1 à 4 ans), alternative ; pour Amira : plafond de risque par groupe (20 à 90 %) ; pour Mateo : aucune (app.py:54-74, 192-206). build_scenario() valide les bornes, l'appartenance du symbole à l'univers, l'absence de l'actif dans le portefeuille de départ, et renvoie la liste des hypothèses changées. produce() renvoie le HTML du dossier (report.render), le titre, le mode, le résumé, l'état du contrôle, le nombre d'appels AWS, les hypothèses modifiées et la durée. Le dossier est affiché dans un iframe (srcdoc) ; une barre affiche mode, « Contrôle conforme : N valeurs reliées » ou « Contrôle en échec », hypothèses modifiées, durée (app.py:264-275). Au chargement, la page lance d'elle-même le calcul de référence de Robert (app.py:306). |
| État | **Vérifié**. tests/test_app.py : test_bootstrap_reads_config_and_excludes_held_assets, test_changing_a_hypothesis_recomputes_the_dossier, test_other_asset_and_amira_cap_run, test_invalid_inputs_give_readable_errors (7 cas) ; ils portent sur produce() et bootstrap(), pas sur le serveur HTTP ni sur le JavaScript. Observation dans le navigateur rapportée par docs/coordination.md:13 (seuil 15 → 25 %, part maximale 9,0 → 23,0 %) et docs/etat.md:63 (capture 1400 px, port 8767). Je n'ai pas lancé les tests moi-même. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée POST JSON : {profil, mode, demande, hypotheses{part, seuil, horizon, actif, alternative, plafond}}. Sortie : {html, titre, mode, resume, controle{ok, valeurs, affirmations}, appels_aws, hypotheses_modifiees, duree_s} ou {erreur} avec code 400 ou 502. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/app.py:39-116 (build_scenario, produce) ; src/datathon2026/app.py:139-307 (PAGE) ; src/datathon2026/app.py:310-341 (Handler) ; tests/test_app.py:9-43 ; docs/coordination.md:12-14 ; docs/etat.md:63-64 |
| Dépendances | workflow.WORKFLOWS, tools.load_scenarios, data.load_universe, data.load_personas, report.render, Dossier.to_dict, clés de config/scenarios.toml (docs/coordination.md:18). Bibliothèque standard seule pour le serveur. |
| Limites | Un calcul à la fois (verrou _LOCK, app.py:26). Les dossiers produits par l'application ne sont pas écrits sur disque : ils vivent dans la variable JavaScript runs et disparaissent au rechargement de la page. Le calcul de référence garde le titre et les phrases du scénario Tesla quand un autre actif est choisi (docs/coordination.md:45). Écran étroit et parcours complet au clic non vérifiés (docs/etat.md:63). Un serveur lancé avant une modification du cœur sert l'ancien code (docs/etat.md:64). Mateo n'a aucun calcul de référence (bouton désactivé, app.py:249-250). Aucune authentification ; écoute locale seulement. |
| Transférabilité | **Adaptable**. Fichier unique sans dépendance externe ; il suppose le contrat produce → Dossier.to_dict → report.render et les clés de scénario listées dans docs/coordination.md:18. |
| Inconnues | Comportement réel du JavaScript (historique, restauration) : aucun test automatique ; seule une observation manuelle est rapportée. |

### X-CAP-059 — Historique de séance et retour à un état précédent

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Comparer plusieurs dossiers produits avec des hypothèses différentes et revenir à l'un d'eux. |
| Valeur apportée | Seul mécanisme de réversibilité de l'interface : chaque production est conservée avec sa requête ; un clic réaffiche le dossier et remet profil, mode, demande et hypothèses dans le formulaire. |
| Fonctionnement | Côté navigateur uniquement : tableau runs de couples {req, out} (app.py:229, 297) ; history() liste les dossiers du plus récent au plus ancien avec titre, mode et hypothèses modifiées ; restore(i) rétablit le formulaire puis show(i) (app.py:276-289). Aucun recalcul au retour : le HTML mémorisé est réaffiché. |
| État | **Implémenté**. Code présent dans la page (produit). Aucun test automatique ne porte dessus ; aucune trace d'exécution nommant l'historique n'a été trouvée (docs/coordination.md:12 le décrit comme ajouté, la ligne « Vérifié » ne le mentionne pas). |
| Entrées et sorties | Entrée : clic sur une ligne de l'historique. Sortie : formulaire rétabli et dossier réaffiché. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/app.py:217-219, 264-289, 297 |
| Dépendances | Réponse de /api/dossier. |
| Limites | Mémoire de la page seulement : perdu au rechargement ou à la fermeture. Pas d'annulation d'une modification autre que ce retour ; pas de comparaison côte à côte ; pas d'export. |
| Transférabilité | **Autonome**. Une cinquantaine de lignes de JavaScript indépendantes du moteur. |
| Inconnues | Fonctionnement effectif au clic non attesté par une trace. |

### X-CAP-060 — Mode « Agent sur Amazon Bedrock » depuis l'application, avec demande libre

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Traiter depuis l'interface une demande que l'enchaînement fixe ne couvre pas. |
| Valeur apportée | La zone de demande devient modifiable en mode agent ; le dossier rendu porte le nombre d'appels Bedrock dans la barre et les identifiants de requête dans sa section « Contribution AWS » (report.py:505-514, 543). |
| Fonctionnement | produce() en mode agent (app.py:89-98) : importe BedrockAgent, exige une demande non vide, considère la demande comme libre si elle diffère de celle du scénario ou si le profil n'a pas d'enchaînement fixe ; dans ce cas le scénario est réduit à trois clés (persona, demande, origine_demande) et la clé de dossier est « <profil>-libre », sinon « <profil>-agent ». En mode référence la zone de demande est en lecture seule (app.py:255) et une demande modifiée est refusée (app.py:102-103). Les erreurs AWS sont traduites en messages lisibles par _explain() (app.py:344-352), code 502, sans trace renvoyée au navigateur. |
| État | **Exécuté**. docs/etat.md:63 rapporte un essai le 15 nov. à 07 h 35 sur une instance au port 8767 : demande libre pour Mateo, trois appels Bedrock, contrôle conforme, graphique et RequestId présents. Aucun fichier de sortie de cet essai dans le dépôt (l'application n'écrit rien sur disque) ; docs/coordination.md:14, écrit plus tôt par l'autre session, dit ce mode non vérifié. Aucun test automatique du mode agent dans tests/test_app.py. |
| Entrées et sorties | Même contrat que /api/dossier avec mode = "agent". |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/app.py:89-98, 249-255, 344-352 ; docs/etat.md:63 ; docs/coordination.md:14, 45 |
| Dépendances | agent.BedrockAgent.run, profil AWS configuré, accès réseau à Bedrock. |
| Limites | En demande libre, les hypothèses réglées aux curseurs sont retirées avant l'appel alors qu'elles restent affichées (constat d'audit, docs/coordination.md:45 ; app.py:95-97). Requête HTTP bloquante pendant tout le travail de l'agent, sans progression ni annulation ; la mention « comptez environ une minute » (app.py:252) est un texte écrit dans la page, non une mesure. Le verrou bloque tout autre calcul pendant ce temps. Dossier non enregistré sur disque. |
| Transférabilité | **Adaptable**. Dépend de la signature BedrockAgent().run(cle, scenario) et de la levée de RuntimeError. |
| Inconnues | Aucune trace conservée de l'essai du 07 h 35 ; comportement avec identifiants expirés non observé depuis l'interface. |

### X-CAP-061 — Erreurs de saisie et d'accès traduites en messages lisibles

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Éviter qu'une valeur hors bornes ou une panne d'accès AWS produise une trace technique ou un dossier faux. |
| Valeur apportée | Refus explicite avant calcul ; aucune trace Python envoyée au navigateur. |
| Fonctionnement | _float() borne chaque nombre (app.py:29-36) ; build_scenario() refuse symbole inconnu, actif déjà détenu, actif égal à l'alternative ; produce() refuse profil inconnu, mode référence sans enchaînement, demande libre en mode référence. Handler.do_POST : ValueError/KeyError → 400 ; autre exception → 502 avec _explain() (identifiants absents, expirés, RuntimeError de l'agent, autre). Requête limitée à 20 000 octets (app.py:331). Côté ligne de commande : run_agent() et aws_check() interceptent NoCredentialsError, TokenRetrievalError, ClientError, BotoCoreError, RuntimeError et impriment une consigne (cli.py:62-74, 109-117). |
| État | **Vérifié**. test_invalid_inputs_give_readable_errors (7 cas paramétrés, tests/test_app.py:32-43) pour les erreurs de saisie. La traduction des erreurs AWS (_explain, messages de la ligne de commande) n'a pas de test : pour cette partie, état implemente. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : charge utile invalide ou exception. Sortie : {"erreur": texte} et code 400 ou 502 ; code de retour 1 en ligne de commande. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/app.py:29-36, 54-74, 326-352 ; src/datathon2026/cli.py:13-17, 62-74, 109-117 ; tests/test_app.py:32-43 |
| Dépendances | botocore.exceptions pour la ligne de commande ; noms de classes d'exception comparés en chaîne dans _explain. |
| Limites | Aucune reprise automatique : pas de nouvelle tentative au niveau de l'application ni de l'agent, aucun botocore Config de retries (agent.py:38-43, 140) ; seule la politique par défaut du SDK s'applique. Les messages renvoient à scripts/configurer-aws-workshop.sh pour l'application et à « aws sso login » pour aws-verifier (cli.py:113) : deux consignes différentes pour la même cause. |
| Transférabilité | **Autonome**. Validation et traduction d'erreurs locales à app.py et cli.py. |
| Inconnues | Comportement réel face à une limitation de débit Bedrock : non observé dans les fichiers lus. |

### X-CAP-062 — Ligne de commande « alphaforge » : demo, agent, aws-verifier, rendre

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Produire, rejouer et revérifier des dossiers sans interface, et vérifier l'accès AWS. |
| Valeur apportée | Quatre commandes ; les dossiers sont enregistrés (dossier.json et dossier.html) et un index HTML est réécrit. |
| Fonctionnement | Point d'entrée alphaforge = datathon2026.cli:main (pyproject.toml:14). (1) demo <robert|amira|tous> : enchaînement fixe sans AWS, enregistre sous --sortie (défaut runs/), option --ouvrir (cli.py:124-125, 149-150). (2) agent <amira|mateo|robert> [--demande] [--nom] [--modele] [--region] [--profil] [--sortie] [--ouvrir] : scénario de démonstration, ou demande libre réduite à trois clés ; nom de dossier par défaut <profil>-agent ou <profil>-libre (cli.py:46-74, 126-131). (3) aws-verifier [--modele] [--region] [--profil] : lecture seule (voir capacité dédiée). (4) rendre [--sortie] [--ouvrir] : relit chaque */dossier.json, reconstruit par Dossier.from_dict, revérifie et régénère le HTML, sans AWS ni recalcul (cli.py:77-83). save() imprime par dossier le nombre d'affirmations, de valeurs reliées et d'échecs (cli.py:20-29). write_index() réécrit runs/index.html après demo, agent et rendre (cli.py:32-43, 151). Code de retour 1 si un dossier n'a pas été produit. |
| État | **Exécuté**. Traces : runs/robert-tsla, runs/amira-croissance (demo), six dossiers d'agent et trois archives sous runs/, runs/index.html ; docs/etat.md:58-61, 84. Aucun fichier de test ne porte sur cli.py (tests/ : test_agent, test_analytics, test_app, test_data, test_evidence, test_workflow). |
| Entrées et sorties | Entrée : arguments. Sortie : runs/<nom>/dossier.json, runs/<nom>/dossier.html, runs/index.html, lignes sur la sortie standard. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/cli.py:121-155 ; pyproject.toml:13-14 ; README.md:22-65 ; runs/ (8 dossiers, _archives/ 3 dossiers, index.html) |
| Dépendances | workflow, report, dossier, agent, tools ; boto3 pour agent et aws-verifier. |
| Limites | « rendre » réécrit tous les dossiers de runs/ en place. « agent » sans --nom écrase le dossier précédent du même nom (deux exécutions de robert-libre-or ont été écrasées, docs/etat.md:85). L'index ne liste pas runs/_archives. runs/ est exclu de git (.gitignore:26) : les traces ne sont pas dans le dépôt versionné. R08:30 cite l'option « --model » ; l'option réelle est --modele (cli.py:130). |
| Transférabilité | **Adaptable**. Dépend des objets Dossier et report du produit. |
| Inconnues | Aucune. |

### X-CAP-063 — Quatre natures de nouvelle version de la demande : précision, correction, changement, variante

| Champ | Contenu |
|---|---|
| Strate | architecture cible conçue, non construite |
| Problème traité | « Je me suis trompé », « ma situation a changé » et « et si… » n'ont pas le même effet sur l'historique ni sur ce qui doit être refait. |
| Valeur apportée | L'historique distingue une conclusion qui n'a jamais valu, une conclusion qui a valu jusqu'à une date et une exploration qui ne touche pas la ligne principale ; une précision dans le domaine déjà balayé ne relance aucun calcul. |
| Fonctionnement | 02 section 6 et 04 section 3 : précision = valeur donnée à une inconnue, le code sélectionne le cas sans rappeler l'agent 2 si la valeur est dans le domaine balayé ; correction et changement font avancer la branche principale et périment ce qui dépendait de l'ancienne valeur ; variante ouvre une branche à tête propre qui partage les pièces inchangées, comparée et non fusionnée d'office. L'interface offre trois gestes ; l'agent 3 propose le classement d'une réaction, la personne le confirme, une table du greffier achemine. Préparé, affiché, choisi sont trois choses ; une réaction cite l'affichage auquel elle répond. |
| État | **Conçu**. Décrit, sans interface construite. Mécanique sous-jacente vérifiée sur le prototype : correction d'un champ (essai (a)), retour à une valeur antérieure sans appel (essai (e)), branche qui laisse le journal principal identique octet pour octet (essai (b)), réaction refusée sur une restitution non affichée (essai (g)). La distinction correction/changement et la précision par sélection de cas ne sont pas dans le prototype. |
| Entrées et sorties | Entrée : réaction de la personne rattachée à un affichage, avec un répondant écrit par l'interface. Sortie : version de la demande, pièces périmées ou branche, bloc « ce qui a changé » en tête de la restitution révisée. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | docs/refonte/architecture/02-dossier.md section 6 (« Précision, correction, changement ou variante » ; « Préparé, affiché, choisi ») et section 7 ; docs/refonte/architecture/08-schemas.md section 2 ; research/experiences/technique/dossier_maison/essais.py : essai_b_variante, essai_e_retour, essai_g_affichage ; docs/refonte/architecture/09-reception.md critères A5 à A8, B5, J2 |
| Dépendances | Dossier à branches et à états ; domaines de balayage du catalogue pour la précision ; interface qui enregistre les affichages. |
| Limites | Dites par les documents : la compréhension n'est pas mesurée dans la première version ; le classement des réactions reste à mesurer sur un jeu annoté (03, agent 3, point 10). |
| Transférabilité | **Adaptable**. Se transfère avec tout support qui tient des branches et un état déduit ; la précision sans recalcul suppose une analyse faite par balayage des inconnues. |
| Inconnues | Lisibilité des trois gestes pour une personne ; fréquence des réactions ambiguës. |

## Données, ingestion et cohérence temporelle

### X-CAP-064 — Valorisation quotidienne en devise de base avec report du dernier taux de change connu

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Les prix sont en devise de cotation (.TO en CAD, le reste en USD) et le fichier de change n'a pas de ligne les jours fériés canadiens ni la fin de semaine. |
| Valeur apportée | Une série de valeur par actif dans une seule devise, sans information future, avec l'âge du taux utilisé conservé. |
| Fonctionnement | `analytics.Market.__init__` (src/datathon2026/analytics.py:46-74) : filtre des prix sur [start, end] ; `pd.merge_asof(..., direction="backward")` entre la date du prix et la date du taux ; valeur = adj_close × usdcad (base CAD) ou adj_close ÷ usdcad (base USD) pour les lignes dont la devise diffère de la base, × 1 sinon ; `fx_age_days` = date du prix − date du taux ; `fx_age_max` et `fx_stale_share` ; levée de ValueError si un taux manque avant la première date FX ; pivot date × ticker sans remplissage (`self.daily`). Base acceptée : CAD ou USD seulement (ligne 47). |
| État | **Vérifié**. Test nommé `test_weekly_cad_return_matches_usd_return_times_fx` (tests/test_analytics.py:38) : identité 1 + r_CAD = (1 + r_USD)(1 + r_FX) sur une seule semaine de SPY (indices 9 et 10 des vendredis), tolérance relative 1e-9 ; le test peut se sauter (`pytest.skip`) si la semaine n'est pas consécutive. Trace d'exécution : runs/robert-tsla/dossier.json, enregistrement D-0004 (âge maximal 4 jours). Je n'ai pas lancé les tests ; docs/technique.md §4 les déclare exécutés. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrées : `Conventions` (base_currency, start, end, weekly_anchor), prices_daily.csv, fx_usdcad_daily.csv. Sorties : `Market.daily` (DataFrame date × ticker, valeurs en devise de base, NaN les jours sans cotation), `fx_age_max` (jours, entier), `fx_stale_share` (fraction). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/analytics.py:46-74 ; tests/test_analytics.py:38-49 ; runs/robert-tsla/dossier.json (D-0004, D-0005) ; docs/decisions.md D3 (ligne 43) |
| Dépendances | pandas, numpy ; `data.load_prices`, `data.load_fx`, `data.load_universe` ; `paths.STARTER_DIR`. |
| Limites | Taux unique publié vers 16 h 30 HE appliqué à des clôtures d'heures différentes (crypto : jour civil UTC). `fx_stale_share` est calculé mais n'est lu nulle part dans src/ (grep). La base USD n'est couverte par aucun test de `Market` (seul `convert_currency` l'est). Période codée en dur dans `Conventions` (2021-11-12 → 2026-11-12). |
| Transférabilité | **Adaptable**. Classe autonome à condition de fournir des DataFrames aux colonnes du jeu de départ (date, ticker, adj_close, currency ; date, usdcad). Le constructeur accepte `prices` et `fx` en argument mais appelle toujours `data.load_universe()`. |
| Inconnues | Aucune mesure écrite de l'effet du décalage horaire entre taux et clôtures. |
| Rectifications après relecture | « Vérifié » vaut pour la base CAD ; la base USD de Market n'a pas de test. |

### X-CAP-065 — Chargement du jeu de départ et conversion de devise sans report vers l'arrière

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Lire les CSV fournis sans les altérer et convertir des prix sans information future. |
| Valeur apportée | Point d'entrée unique des données ; dossier remplaçable par variable d'environnement. |
| Fonctionnement | `data._read` (message d'erreur explicite si fichier absent), `load_universe`, `load_prices(tickers)` (KeyError si ticker absent, tri ticker/date), `load_corporate_actions`, `load_fx`, `load_macro(series_ids)`, `load_personas` (TOML), `adj_close_wide` (pivot sans remplissage), `convert_currency(prices, target, fx, columns)` (merge_asof backward, NaN avant le premier taux, colonnes open/high/low/close/adj_close) — src/datathon2026/data.py. `paths.STARTER_DIR` lisible depuis `DATATHON_STARTER_DIR` (paths.py:9). |
| État | **Vérifié**. tests/test_data.py : `test_universe_has_31_assets`, `test_prices_cover_universe_without_duplicates` (pas de doublon date/ticker, adj_close > 0), `test_listing_currency_matches_suffix`, `test_wide_table_has_no_fill`, `test_convert_to_cad_uses_same_day_rate_and_carries_forward` (taux du jour, report, CAD inchangé, NaN avant le premier taux), `test_convert_to_usd_divides_cad_prices`, `test_personas_load`. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrées : CSV de data/raw/alphaforge_starter/. Sorties : DataFrames pandas au format long ou large. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/data.py ; src/datathon2026/paths.py ; tests/test_data.py |
| Dépendances | pandas, tomllib ; fichiers présents localement (data/raw/* est ignoré par git, .gitignore:20 ; seuls data/README.md et des .gitkeep sont suivis). |
| Limites | `convert_currency` et `adj_close_wide` ne sont appelés par aucun module du produit hors tests (grep sur src/ et scripts/) : `Market` refait la conversion de son côté, donc deux implémentations de la même règle. `load_macro` et `load_corporate_actions` ne sont appelés par aucun module du produit (diagnostic §4 ; `load_macro` est appelé par docs/refonte/calcul_exploratoire.py:70, hors produit). Aucun test sur `load_macro`, `load_fx`, `load_corporate_actions`. |
| Transférabilité | **Autonome**. Module sans dépendance au reste du produit hormis `paths`. |
| Inconnues | Aucune. |
| Rectifications après relecture | data.convert_currency n'est appelée que par les tests ; le produit refait sa propre jointure dans analytics.Market (analytics.py:53-60). Le test de la conversion ne valide donc pas le chemin employé par le produit. |

### X-CAP-066 — Manifeste de provenance des données (`data_manifest`)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Rattacher chaque dossier à la version exacte des fichiers utilisés et à leurs limites. |
| Valeur apportée | Empreintes SHA-256, âge maximal du change, durée de l'échantillon et biais de l'univers inscrits au registre (préfixe D). |
| Fonctionnement | tools.py:75-93 : SHA-256 de prices_daily.csv, fx_usdcad_daily.csv, assets_universe.csv (16 premiers caractères affichés, empreinte complète dans `inputs`) ; `Market.fx_age_max` ; durée = (dernier jour − premier jour) / 365,25 ; texte fixe sur le biais du survivant. |
| État | **Exécuté**. Enregistrements D-0004 (4 jours) et D-0005 (4,9993 ans) dans runs/robert-tsla/dossier.json et runs/amira-croissance/dossier.json. Un test nommé `test_agent_exposes_data_provenance_tool` existe (tests/test_agent.py:86) mais je n'en ai pas lu le corps : il porte, d'après son nom, sur l'exposition de l'outil à l'agent, pas sur le contenu du manifeste. |
| Entrées et sorties | Entrée : `Session`. Sortie : identifiants D-xxxx et valeurs affichées. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/tools.py:75-93 ; runs/robert-tsla/dossier.json |
| Dépendances | `STARTER_DIR`, registre. |
| Limites | macro_rates.csv et corporate_actions.csv ne sont pas empreints. Aucune vérification de l'empreinte contre une valeur attendue. `fx_stale_share` non publié. |
| Transférabilité | **Adaptable**. Dépend du registre de preuves. |
| Inconnues | Aucune. |
| Rectifications après relecture | tests/test_agent.py::test_agent_exposes_data_provenance_tool, lu depuis, vérifie que l'outil est exposé, tracé et que ses enregistrements sont citables ; il ne vérifie pas le contenu du manifeste. |

### X-CAP-067 — Registre typé d'enregistrements identifiés (Record / Registry)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Relier chaque valeur affichée à un enregistrement unique portant unité, statut, origine, période et conventions. |
| Valeur apportée | Toute valeur d'un dossier a un identifiant stable dans le dossier, une unité qui commande son formatage, un statut épistémique et une origine ; c'est le support de toutes les autres règles. |
| Fonctionnement | `Registry.add(prefix, label, value, unit, status, origin, **kw)` (evidence.py:226-233) attribue un identifiant `<préfixe>-<compteur sur 4 chiffres>` dans l'ordre d'ajout, par préfixe. Préfixes admis : R (résultat calculé), P (fait de profil), S (source documentaire), D (donnée) (evidence.py:20-25). `Record` (evidence.py:193-216) : id, label, value, unit, status, origin, subject, period (couple de dates), conventions (liste de textes), inputs (dict libre, dont `depend_de` et `sha256`). Un statut hors `STATUS_ORDER` lève ValueError (evidence.py:206-208) ; un préfixe inconnu aussi (evidence.py:227-228). `to_dict` ajoute `display` (valeur formatée). |
| État | **Exécuté**. Code dans le produit ; registres observés dans runs/robert-tsla/dossier.json (146 enregistrements : 123 R, 17 P, 6 D) et runs/robert-agent/dossier.json (157 : 134 R, 17 P, 6 D). Aucun test nommé ne porte sur l'attribution des identifiants elle-même ; le registre est exercé indirectement par tous les tests de tests/test_evidence.py (fixture `reg`). Je n'ai pas lancé les tests. |
| Entrées et sorties | Entrée : appels `add` faits par les outils (tools.py importe `Registry`, tools.py:16). Sortie : dict `enregistrements` du dossier.json, clé = identifiant. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/evidence.py:17-25, 193-264 ; runs/robert-tsla/dossier.json clé `enregistrements` ; runs/robert-agent/dossier.json clé `enregistrements` |
| Dépendances | Bibliothèque standard seulement (re, dataclasses). |
| Limites | Le préfixe S n'est jamais utilisé : 0 enregistrement S dans les 11 dossiers sous runs/ (constat repris par docs/refonte/diagnostic-et-contrat.md:44). Les identifiants sont propres à une exécution (R-0003 ne désigne pas la même chose d'un dossier à l'autre, ex. pire baisse du portefeuille : R-0014 dans robert-tsla, R-0024 dans robert-agent). `inputs` est un dict non typé. Le statut est posé par le code appelant, sans critère de qualité (diagnostic:57). Pas d'empreinte de l'enregistrement, pas d'horodatage par enregistrement. |
| Transférabilité | **Autonome**. evidence.py n'importe rien du reste du paquet ; le module se copie tel quel. |
| Inconnues | Qui pose `depend_de` et selon quelle règle (dans tools.py, hors périmètre) ; 69 enregistrements le portent dans chacun des deux dossiers inspectés. |

### X-CAP-068 — Outils réutilisables et manifestes des textes non redistribués

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Les textes téléchargés ne peuvent pas être versés au dépôt « faute de droit de redistribution » (R08 §3) ; il faut pouvoir les retrouver et les contrôler. |
| Valeur apportée | Liste de chaque fichier lu avec taille et empreinte SHA-256 ; pour 276 fichiers, identifiant de source et référence complète avec adresse. |
| Fonctionnement | consolider_recherche.py manifeste DOSSIER calcule l'empreinte de chaque fichier et l'associe à la source du registre. research/sources/textes/ est exclu de git par research/sources/.gitignore (« textes/ »). Pour retrouver un texte : prendre la référence et l'adresse dans manifeste.json ou dans R07, retélécharger, comparer le SHA-256. |
| État | **Exécuté**. Fichiers présents : manifeste.json (1 705 entrées, environ 625 Mo décrits), manifeste-pratiques.json (342 entrées, environ 257 Mo), dossier textes/ présent localement (14 sous-dossiers). Aucun test automatique. |
| Entrées et sorties | Entrée : dossier des textes. Sorties : research/sources/manifeste.json (champs fichier, octets, sha256, source, reference), manifeste-pratiques.json (champs fichier, octets, sha256). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | research/sources/manifeste.json, research/sources/manifeste-pratiques.json ; research/sources/.gitignore ; research/outils/consolider_recherche.py, fonction manifeste (l. 203-221) ; research/outils/recherche_web.py, research/outils/schema_architecture.py (SVG sans dépendance) |
| Dépendances | Python standard (hashlib, json). |
| Limites | Dans manifeste.json, 1 429 entrées sur 1 705 n'ont ni source ni référence (scripts, copies de vérification, fichiers intermédiaires). manifeste-pratiques.json ne contient aucune référence ni adresse : il faut passer par les fiches research/fiches/architecture/pratiques-*.json. Identité des copies locales avec leur adresse d'origine non vérifiée sauf pour une page (10-pratiques §4). Tout le périmètre (docs/refonte/, research/experiences, fiches, outils, sources) est non suivi par git à la date de lecture (git status : « ?? »). |
| Transférabilité | **Autonome**. Le manifeste est un JSON plat ; la fonction de calcul est générique. |
| Inconnues | Conditions de licence texte par texte : non consignées dans les manifestes. |

## AWS, déploiement, exploitation et reprise

### X-CAP-069 — Preuve d'appel AWS dans le dossier : identifiant de requête, jetons et latence par appel

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Montrer que Bedrock a réellement servi à produire le dossier. |
| Valeur apportée | Chaque dossier d'agent contient la liste des appels Converse avec leur RequestId. |
| Fonctionnement | BedrockAgent._converse (agent.py l.172-188) ajoute à self.requests {requestId (ResponseMetadata.RequestId), stopReason, inputTokens, outputTokens, latenceMs} ; run écrit dossier.aws = {service: « Amazon Bedrock Runtime (Converse) », region, modele, appels, corrections_demandees}. Session boto3 créée avec le profil nommé (aws_session, l.38-45), repli sur la chaîne d'identifiants par défaut. |
| État | **Vérifié**. tests/test_agent.py::test_agent_loop_runs_tools_rejects_handwritten_number_then_accepts vérifie la liste des requestId (client simulé). Exécution réelle : runs/robert-agent/dossier.json, 5 appels, premier requestId f2c00678-7cd4-4c26-a41e-35f110497967, région us-east-1, modèle global.anthropic.claude-sonnet-5-5. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Champ aws du dossier. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:22-45, 172-188, 237-238 ; runs/robert-agent/dossier.json (aws) ; runs/mateo-libre-esg/dossier.json (aws) ; docs/decisions.md D2 |
| Dépendances | boto3, profil AWS « alphaforge », variables AF_BEDROCK_MODEL, AWS_REGION, AF_AWS_PROFILE. |
| Limites | Les RequestId ne sont pas vérifiables hors du compte. Journal d'invocation et écriture S3 annoncés dans D2 : non présents dans agent.py. Le service Bedrock n'est utilisé que pour l'inférence Converse. |
| Transférabilité | **Autonome**. Dictionnaire de métadonnées par appel, indépendant du reste. |
| Inconnues | Existence d'un journal d'invocation ou d'un dépôt S3 ailleurs dans le dépôt : non cherchée (hors périmètre). |
| Rectifications après relecture | Les tests emploient un client simulé (tests/test_agent.py::FakeBedrock) : la tenue du journal est Vérifiée ; l'appel réel à Bedrock est Exécuté (dix dossiers). |

### X-CAP-070 — Provenance inscrite dans le dossier (appels Bedrock, empreintes des fichiers, trace d'outils)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Prouver que l'agent a réellement tourné sur AWS et sur quelles données. |
| Valeur apportée | Le dossier porte l'identifiant de chaque appel au modèle et l'empreinte des fichiers de données. |
| Fonctionnement | `aws.appels[]` : requestId, stopReason, inputTokens, outputTokens, latenceMs par appel Converse (agent.py:179-182, 237-238) ; `aws.service`, `region`, `modele`, `corrections_demandees`. Enregistrements D-0001 à D-0003 : nom de fichier, valeur = 16 premiers caractères du SHA-256, `inputs.sha256` complet (tools.py:79-81). `trace[]` : outil, arguments, identifiants produits, durée en ms, erreur éventuelle. `cree_le` : horodatage UTC ISO à la seconde (dossier.py:44). `mode` : « workflow fixe » ou « agent Bedrock (<modèle>) ». Chaque enregistrement calculé porte `period` et `conventions`. |
| État | **Exécuté**. Observé dans runs/robert-agent/dossier.json : 5 appels avec requestId, modèle global.anthropic.claude-sonnet-5-5, région us-east-1, corrections 1 ; D-0001 `prices_daily.csv` avec sha256. robert-tsla : `aws` = {} (workflow fixe). `test_agent_loop_…` vérifie la présence des requestId avec un client simulé ; `test_agent_exposes_data_provenance_tool` existe (tests/test_agent.py:86), non lu. |
| Entrées et sorties | Sortie : clés `aws`, `trace`, enregistrements D du JSON ; tableau « Contribution AWS » de l'annexe HTML (report.py:505-514). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | runs/robert-agent/dossier.json clé `aws` ; runs/robert-tsla/dossier.json enregistrements D-0001…D-0006 ; src/datathon2026/agent.py:179-182, 237-238 ; src/datathon2026/report.py:505-519 |
| Dépendances | Réponse Converse (ResponseMetadata.RequestId). |
| Limites | Pas d'horodatage par appel ni par étape de trace ; pas de version du code (commit), pas d'empreinte de la consigne système ni du fichier de scénarios, pas de paramètres d'inférence, pas de sorties d'outils, pas d'empreinte du dossier. Les requestId ne sont pas vérifiables sans le compte AWS : journal d'invocation et écriture S3 versionnée sont cités comme choix dans docs/decisions.md:35 mais classés « améliorations prévues » dans docs/technique.md:41, et docs/etat.md:114 indique que rien n'est stocké dans le compte. |
| Transférabilité | **Adaptable**. Le format des appels est celui de Bedrock Converse. |
| Inconnues | Empreintes de fx et univers : présentes ; macro et opérations sur titres : non observées parmi les enregistrements D. |

### X-CAP-071 — Appel d'Amazon Bedrock Runtime par l'API Converse, outils exécutés localement

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Faire contribuer AWS à la solution (condition d'admissibilité E1, docs/exigences.md:7). |
| Valeur apportée | Seul appel de modèle du produit : un modèle hébergé sur Bedrock choisit les outils de calcul locaux et rédige le dossier. |
| Fonctionnement | aws_session() crée boto3.Session(profile_name, region_name), avec repli sur la chaîne d'identifiants par défaut si le profil n'existe pas (agent.py:38-45). BedrockAgent crée le client « bedrock-runtime » (agent.py:140) et appelle client.converse(modelId, system, messages, toolConfig, inferenceConfig={maxTokens: 8192}) (agent.py:172-180). Valeurs par défaut : modèle global.anthropic.claude-sonnet-5-5 (profil d'inférence), région us-east-1, profil AWS nommé alphaforge (agent.py:22-26). Bornes : MAX_TURNS = 16, MAX_FIXES = 2, MAX_TOKENS = 8192 (agent.py:27-29). Pas de flux (converse, non converse_stream), pas de température fixée. |
| État | **Vérifié**. Exécution réelle : neuf dossiers enregistrés avec identifiants de requête (runs/ et runs/_archives/). Tests nommés sur la boucle avec client simulé : tests/test_agent.py (test_agent_loop_runs_tools_rejects_handwritten_number_then_accepts, test_tool_error_is_returned_not_raised, test_agent_presentation_is_checked_then_rendered, test_agent_exposes_data_provenance_tool). Les tests ne touchent pas AWS ; la partie AWS réelle est à l'état execute. Suite de tests relancée le 15 nov. à 17 h 50 : 51 tests réussis (evaluation-fusion/preuves/pytest.txt). |
| Entrées et sorties | Entrée : clé de dossier et scénario. Sortie : Dossier avec champ aws {service, region, modele, appels[], corrections_demandees} (agent.py:237-238). |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:22-45, 137-140, 172-188, 237-238 ; runs/robert-agent/dossier.json (champ aws) ; docs/etat.md:82-87 ; research/R08-outils-routes-et-ressources-2026-11-15.md:16 |
| Dépendances | boto3 >= 1.44.3 (pyproject.toml:8), profil AWS local, accès au profil d'inférence dans le compte. |
| Limites | Aucun autre service AWS n'est appelé par le chemin de production d'un dossier. Aucun déploiement : tout s'exécute sur le poste (docs/etat.md:87, 114). Pas de nouvelle tentative applicative. Un seul modèle essayé pour le produit (docs/comparaison-agent-workflow.md, « Lecture »). Prix des modèles non vérifié (docs/etat.md:85). |
| Transférabilité | **Adaptable**. La boucle Converse est isolable ; elle est liée aux outils et au vérificateur du produit. |
| Inconnues | Disponibilité du modèle par défaut sur un autre compte (R08:30). |
| Rectifications après relecture | Les tests emploient un client simulé (tests/test_agent.py::FakeBedrock) : la boucle est Vérifiée contre ce client ; l'appel réel à Bedrock est Exécuté, non Vérifié. |

### X-CAP-072 — Vérification d'accès AWS en lecture seule (alphaforge aws-verifier)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Savoir, sans appeler de modèle, si le profil AWS, la région et le profil d'inférence sont utilisables. |
| Valeur apportée | Diagnostic avant dépense ; n'affiche que les quatre derniers chiffres du compte. |
| Fonctionnement | aws_check() (cli.py:86-118) : session par aws_session ; sts.get_caller_identity ; client « bedrock » : list_inference_profiles(typeEquals=SYSTEM_DEFINED, maxResults=1000), filtrés sur « claude » et statut ACTIVE ; get_inference_profile(inferenceProfileIdentifier=modèle) avec statut et régions de destination. Messages distincts pour identifiants absents, session expirée, autre erreur ; code de retour 1. |
| État | **Exécuté**. docs/etat.md:84 : exécuté le 15 nov. à 06 h 43 (compte …1226, global.anthropic.claude-sonnet-5-5 ACTIVE). Pas de sortie enregistrée dans un fichier, pas de test. Relancée le 15 nov. à 17 h 50 : profil d'inférence du modèle par défaut actif (evaluation-fusion/preuves/aws-verifier.txt). |
| Entrées et sorties | Entrée : --modele, --region, --profil. Sortie : lignes texte, code 0 ou 1. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/cli.py:86-118, 132-137, 142-143 ; docs/acces-aws.md:101-107 ; docs/etat.md:84 |
| Dépendances | boto3 ; droits sts:GetCallerIdentity, bedrock:ListInferenceProfiles, bedrock:GetInferenceProfile. |
| Limites | Ne prouve pas que l'invocation est autorisée (aucun appel de modèle). docs/acces-aws.md:117 : la politique de permissions minimales « reste à confirmer sur le compte ». |
| Transférabilité | **Autonome**. Fonction indépendante du reste du produit, hormis aws_session et les valeurs par défaut. |
| Inconnues | Aucune. |
| Rectifications après relecture | Une sortie est désormais enregistrée : evaluation-fusion/preuves/aws-verifier.txt. |

### X-CAP-073 — Accès AWS sans identifiants dans le code : profil nommé et guide

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Appeler Bedrock depuis le poste sans que le code ou la conversation manipule des secrets. |
| Valeur apportée | Le code ne demande qu'un nom de profil ; la saisie des identifiants temporaires Workshop Studio se fait par l'équipe. |
| Fonctionnement | Profil nommé « alphaforge » résolu par AF_AWS_PROFILE, puis AWS_PROFILE, puis la valeur par défaut (agent.py:26). docs/acces-aws.md décrit quatre cas d'accès (SSO, Workshop Studio, utilisateur IAM, compte racine), la vérification, une politique IAM minimale proposée et un tableau de dépannage. Un script de saisie existe (scripts/configurer-aws-workshop.sh), non ouvert ici conformément à la consigne. |
| État | **Exécuté**. Le profil a servi aux exécutions réelles (docs/etat.md:82-85 ; R08:9). Le guide est de la documentation ; le script de saisie n'a pas été examiné. |
| Entrées et sorties | Entrée : profil AWS local. Sortie : session boto3. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:24-26, 38-45 ; docs/acces-aws.md:1-21, 101-152 ; README.md:31-47 |
| Dépendances | AWS CLI sur le poste (docs/acces-aws.md:9), identifiants temporaires de l'atelier. |
| Limites | Identifiants temporaires : à ressaisir à l'expiration (docs/acces-aws.md:19). docs/etat.md:24 signale que scripts/configurer-aws-workshop.sh a été modifié « par une autre main » et « peut contenir des identifiants » : à vérifier avant tout commit (le fichier est modifié dans git status). |
| Transférabilité | **Autonome**. Convention de profil nommé réutilisable telle quelle. |
| Inconnues | Contenu actuel de scripts/configurer-aws-workshop.sh (non ouvert). |

### X-CAP-074 — Lanceur de Claude Code sur Bedrock pour le développement, avec message de reprise

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Faire passer les inférences de développement par le compte AWS du datathon et reprendre une session après interruption. |
| Valeur apportée | Outil d'exploitation de l'équipe, hors parcours de l'utilisateur final. |
| Fonctionnement | scripts/claude-bedrock.sh fixe CLAUDE_CODE_USE_BEDROCK=1, AWS_PROFILE=alphaforge, AWS_REGION=us-east-1, ANTHROPIC_MODEL (défaut us.anthropic.claude-fable-5-2) et trois modèles épinglés ; vérifie l'identité par « aws sts get-caller-identity » ; l'option --reprise passe scripts/message-reprise.txt comme premier message (lire CLAUDE.md, docs/etat.md, docs/decisions.md, le mandat ; lancer pytest, demo tous, aws-verifier ; règles). |
| État | **Exécuté**. R08:13 : route testée, métrique CloudWatch AWS/Bedrock Invocations pour ce modèle (747 appels de 06 h 20 à 09 h 20). Pas de test automatique. |
| Entrées et sorties | Entrée : arguments passés à claude. Sortie : session Claude Code. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | scripts/claude-bedrock.sh:1-28 ; scripts/message-reprise.txt:1-7 ; docs/acces-aws.md:23-32 ; research/R08-outils-routes-et-ressources-2026-11-15.md:13-15, 34-40 |
| Dépendances | CLI claude, AWS CLI, profil alphaforge, mode de conservation aws_review du compte (décision D4, docs/acces-aws.md:25). |
| Limites | README.md:82 dit « Opus 5.5 » alors que le script lance Fable 5.2 par défaut (scripts/claude-bedrock.sh:13) : documentation non alignée. docs/acces-aws.md:28 dit que la CLI claude n'est pas installée « à ce jour », énoncé antérieur à l'usage constaté dans R08. Le message de reprise renvoie à des « prochaines actions » que docs/etat.md:9 déclare suspendues. |
| Transférabilité | **Autonome**. Script d'environnement ; ne concerne pas le produit livré à l'utilisateur. |
| Inconnues | Coût de la session de développement : non mesuré (docs/etat.md:86). |
| Rectifications après relecture | La mention « Opus 5.5 » est à README.md:81. |

### X-CAP-075 — Essai Strands Agents 1.65.0 pour la boucle d'un rôle

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Quelle boucle tient une tâche de rôle : outils propres, sortie à structure imposée, limite de tours, refus journalisé ? |
| Valeur apportée | Observe que la bibliothèque tient la boucle d'un rôle et que son graphe et ses sessions ne conviennent pas au dossier ; fonde deux règles du contrat (tâche atomique avec question comme pièce de sortie ; refus d'une sortie dont la raison d'arrêt est inattendue). |
| Fonctionnement | Dix essais, dix-neuf appels de modèle plafonnés à vingt par commun.py, journal appels_bedrock.jsonl (identifiant de requête, jetons, raison d'arrêt). Observés : sortie Pydantic valide, invalide, tronquée ; outils disjoints et crochet BeforeToolCallEvent ; limits turns=2 ; interruption et reprise ; session sur deux processus ; graphe à deux nœuds ; reprise de graphe après processus tué (le nœud aval reçoit une entrée vide et le graphe se déclare terminé). |
| État | **Exécuté**. Sorties sous research/experiences/technique/strands/sorties/ (essai1.txt à essai9.txt, essai4_refus.jsonl, appels_bedrock.jsonl). Statuts de la fiche : huit « reussi », deux « partiel » (8, 8 bis). LISEZMOI : « Chaque conduite a été observée une seule fois », modèle Haiku seulement ; essai 8 arrêté deux fois sur troncature, script corrigé non relancé. |
| Entrées et sorties | Entrée : scripts essai1 à essai9, commun.py. Sortie : verdict « Retenir Strands pour la boucle d'un rôle seulement ». |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | research/experiences/technique/strands/LISEZMOI.md ; research/experiences/technique/strands/sorties/essai3.txt, essai4.txt, essai8b_b.txt ; research/fiches/architecture/technique-strands.json (verdict, essais) ; docs/refonte/architecture/06-comparatif-technique.md section 4, « La boucle d'un rôle » |
| Dépendances | strands-agents (40 paquets de plus, Strands compris) ; Bedrock. |
| Limites | Dites par les documents : stratégie de réessai (six tentatives par défaut) et exception d'outil lues, non testées ; l'essai n'a pas construit l'appel direct de Converse et ne départage donc pas les deux voies. Le choix proposé (appel direct d'abord) « n'est pas tiré d'un essai » et inverse le verdict de l'essai (06 section 4 ; 01 section 10). |
| Transférabilité | **Autonome**. Scripts indépendants du produit ; chaque relance consomme des appels et exige de renommer le journal. |
| Inconnues | Conduite sur le modèle par défaut du produit ; comparaison avec la boucle directe (préalable K10). |

### X-CAP-076 — Essai des services AWS sans création de ressource : recherche web AgentCore, reclassement, trace CloudTrail, Step Functions validé, émulateur S3/DynamoDB

| Champ | Contenu |
|---|---|
| Strate | recherche et expériences hors produit |
| Problème traité | Quels services AWS peuvent contribuer à l'enchaînement, à la persistance, à la recherche et à l'observation, la veille de la fermeture du compte ? |
| Valeur apportée | Identifie ce qui fonctionne sans ressource (InvokeWebSearch, rerank, plongements, historique CloudTrail, métriques CloudWatch) et ce qui resterait à écrire quel que soit le service (invalidation sélective, tête déduite, rejeu hors ligne). |
| Fonctionnement | Six essais : inventaire en lecture (25 sondes) ; simulation IAM (44 actions) ; ValidateStateMachineDefinition sur chaine_alphaforge.asl.json et 17 TestState à réponses simulées ; chaîne recherche web -> reclassement cohere.rerank-v3-5:0 -> preuve candidate par outil à schéma imposé -> contrôle de citation ; recherche des appels dans CloudTrail par identifiant de requête ; contrats du dossier sur émulateur moto. services_produit.py contient trois fonctions d'appel sans ressource. |
| État | **Exécuté**. Sorties sous research/experiences/technique/services_aws/sorties/ (essai1.txt à essai6.txt et JSON, appels_bedrock.jsonl à 5 lignes). Statuts de la fiche : essais 1, 3a, 4 et documentation « reussi » ; 2, 3b, 5, 6 « partiel » ; création et exécution réelles « non_fait ». Une seule observation par conduite ; modèle Haiku 5.5. Step Functions : définition validée, aucune exécution ; S3 et DynamoDB : émulateur seulement ; droits : simulés. |
| Entrées et sorties | Entrée : scripts essai1 à essai6, services_produit.py, définition ASL. Sortie : tableau « Constat par service » et verdict « Retenir en partie ». |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | research/experiences/technique/services_aws/LISEZMOI.md (« Ce qui a été testé », « Constat par service », « Ce qui n'est pas établi ») ; research/experiences/technique/services_aws/services_produit.py ; research/experiences/technique/services_aws/sorties/essai4.txt, essai5.txt, essai3.txt ; research/fiches/architecture/technique-services-aws.json (verdict, essais) |
| Dépendances | boto3 1.44.3 ; moto 5.2.5 pour l'essai 6 ; compte d'atelier AWS, fermé lundi 16 novembre 13 h 59 (00 section 8). |
| Limites | Dites par les documents : le reclassement et la recherche web n'apparaissent ni dans CloudTrail ni dans CloudWatch, cause non établie ; la définition Step Functions décrit la chaîne d'avant les corrections de la revue, et une transition au moins n'est plus celle du contrat (06 section 3) ; « Une simulation n'est pas une création réussie ». |
| Transférabilité | **Autonome**. services_produit.py (trois fonctions) se reprend sans le reste, sous réserve d'un compte Bedrock ayant ces droits ; les essais d'inventaire et de droits sont propres au compte d'atelier. |
| Inconnues | Disponibilité de ces appels sur un autre compte ; qualité du reclassement en français ; conduite réelle de Step Functions, S3, DynamoDB, Guardrails. |

## Prompts, contrats de sortie et gestion du contexte

### X-CAP-077 — Instruction système unique de l'orchestrateur (constante SYSTEM)

| Champ | Contenu |
|---|---|
| Strate | produit implémenté |
| Problème traité | Dire au modèle la méthode, les interdits d'écriture contrôlés par le vérificateur et la forme de la présentation. |
| Valeur apportée | Seul prompt du produit ; il porte à la fois le rôle d'orchestrateur, d'analyste et de rédacteur. |
| Fonctionnement | Constante SYSTEM, agent.py l.98-127, passée telle quelle à converse (system=[{"text": SYSTEM}], l.176). Trois blocs : Méthode (4 points), Règles d'écriture (10 puces), Présentation (3 puces). Pas de fichier de prompt séparé, pas de variantes par profil, pas d'exemples. |
| État | **Exécuté**. Chargée à chaque appel ; six dossiers d'agent enregistrés (docs/comparaison-agent-workflow.md). Aucune évaluation du prompt à critère écrit d'avance ; les tests utilisent un client simulé qui n'en dépend pas. |
| Entrées et sorties | Texte statique d'environ 30 lignes. |
| Sources théoriques | Aucune source théorique rattachée. |
| Preuves locales | src/datathon2026/agent.py:98-127 ; src/datathon2026/agent.py:172-180 (_converse) |
| Dépendances | Syntaxe {{R-…}}, {{cmp:…}}, {{cmpabs:…}}, {{cmpduree:…}}, {{X.label}} du vérificateur ; noms de sections de dossier.SECTIONS. |
| Limites | Les consignes « ne déduis jamais un portefeuille de l'âge », « n'invoque aucun événement », « choisis les outils utiles et seulement ceux-là », « montre l'écart, propose des options » ne sont contrôlées par aucun code. docs/decisions.md (Rectifications) note que le remplacement de quatre rôles par un orchestrateur unique n'a pas été consigné comme décision. |
| Transférabilité | **Fortement couplée**. La moitié du texte décrit la grammaire du vérificateur de cette réalisation. |
| Inconnues | Aucune évaluation comparative de versions du prompt trouvée dans le périmètre. |

