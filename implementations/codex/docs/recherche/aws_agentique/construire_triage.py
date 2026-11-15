"""Registre de lecture humain, relié à l'inventaire et aux captures communes.

N'exécute aucun modèle, réseau, outil AWS ou code de dépôt tiers.
Les décisions ci-dessous ont été rédigées après lecture aux niveaux indiqués.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/recherche"
OUT = Path(__file__).resolve().parent
inventory = json.loads((BASE / "inventaire_urls.json").read_text())

# id | niveau réellement lu | localisateur | décision / limite
rows = """
U004|sections README|Persistence and Recovery, mémoire et checkpoint|Étudier mémoire/rating, pas adopter système de trading. Les leçons de rendements réalisés contaminent un test antérieur sans filtre temporel ; aucune exécution.
U005|résumé et introduction|Résumé TradingAgents|Spécialisation bullish/bearish/risk comme motif, gains de trading non répliqués et non transférables.
U006|résumé et introduction|Résumé et ouverture FINSABER|Contrepoint aux évaluations financières trop étroites ; protocole approfondi par autre rôle de recherche, pas réplication locale.
U007|résumé et introduction|Résumé Profit Mirage|Contrepoint données/stratégies et biais ; ne pas généraliser un résultat de banc d'essai à toute stratégie agentique.
U008|résumé|Résumé StockBench|Évaluation quotidienne outillée plus proche d'une activité de trading que QA statique ; ne valide pas notre décision de portefeuille.
U009|notice primaire et résumé|Page poster ICML, résumé|Fuite temporelle du préentraînement : un filtre documentaire ne suffit pas à créer un modèle point-in-time.
U010|méthode et limites ciblées|sources/scaling_full.txt §4.1–4.2, §5, annexe D ; v3|+80,8% relatif de réussite 0,349→0,631, pas rendement ; domaine/budget/architecture conditionnent le gain. BERTScore faible ne prouve pas contradiction.
U011|méthode et preuve ciblées|sources/debatevote_full.txt §4, annexe D.3–D.4 ; v2|Théorème conditionnel sur croyances/voisinage, pas interdiction universelle de critique entre rôles distincts.
U012|définitions et limites ciblées|sources/selfcorrect_pdf.txt introduction et §2 ; v2|Correction intrinsèque sans feedback externe distincte de CRITIC ; contrôler oracle et prompt initial.
U013|méthode et protocoles ciblés|sources/critic_full.txt §3 algorithme1, QA et mathématiques ; v2|Critique appuyée sur outil observé ; distinguer ablation sans outils et variante oracle CRITIC*. Recherche réelle note01 vérifie dates.
U014|sections architecture/budget/évaluation|Archive commune lignes57–147|Guide industriel, gain interne non contrôlé pour notre usage ; coût tokens et dépendances limitent parallélisme, reprise/attribution utiles.
U017|résumé|Notice arXiv, résumé|Préférences utilisateur et biais de confiance ; étude de personas distincte d'une validation d'analyse financière.
U018|métadonnées seulement|PDF collecté, non lu ici|Version de travail de l'étude d'advisors ; doublon thématique U017, ne pas compter comme preuve indépendante.
U020|architecture ciblée|sources/optiguide_pdf.txt pages2 et8, §3.1|LLM génère code puis solveur ; motif what-if retenu, pas preuve de bibliothèque fermée ; détail code U054.
U021|résumé et notice|arXiv2305.04388v2, résumé|Justification verbale pas trace causale fiable ; conserver événements d'outils, sans exiger raisonnement interne.
U038|sémantique et tableau ciblés|Archive commune lignes27–193|Standard et Express sync/async distincts ; idempotence et reprise métier restent à concevoir. Service non invoqué.
U039|métadonnées seulement|Titre de la fiche modèle AWS|Catalogue Haiku5.5 pas preuve d'accès ; cellule23 notebook signale indisponibilité datathon, aucun changement de modèle.
U040|introduction et avis d'accès|Corps introductif agents.html|Pas de nouvelles inscriptions : ne pas écrire fermeture de tous les agents existants ; non adopté.
U041|métadonnées seulement|Titre et URL App Runner|Hébergement non requis pour recherche/Mac ; statut et accès non testés, ne pas reprendre une promesse de disponibilité.
U042|fonctionnement et limites ciblés|Corps AWS Automated Reasoning, langues et cross-region|Validité relative à politique, traduction par modèles, ni protection injection ni vérité financière. Non testé, pas adapté directement au français.
U043|extrait de code|Archive GitHub rating.py lignes470–596|Parseur heuristique vocabulaire/rating absent ; ne vérifie pas recommandation. Même famille U004, version main non épinglée.
U044|résumé|Notice arXiv2606.02528|Biais d'allocation/internal features selon modèles étudiés ; audit de cadrage pertinent, accès aux poids Astra absent.
U054|code intégral des fichiers ciblés|sources/optiguide_code_0/1/2.txt ; commit3da334a|MIT ; exec code généré après SAFE/DANGER ; adapter motif à catalogue fermé serait notre conception, pas implémentation source.
U056|résumé|Résumé PAL|Délégation du calcul à interprète, pas exactitude par définition ; exécution de code généré non retenue sans confinement et validation.
U057|résumé|Résumé Program-of-Thoughts|Motif raisonnement/calcul séparés ; QA financière ne démontre pas adéquation de portefeuille.
U058|résumé|Résumé FinanceBench|Benchmark questions/documents financiers, diagnostic retrieval/calcul ; partitions publiques et évaluation distinctes du corpus annoncé.
U059|résumé|Résumé Lanham CoT faithfulness|Causalité des explications non acquise ; opérations enregistrées plus solides qu'affirmation de vérification.
U060|métriques ciblées|sources/alce_full.txt §3.3 ; v2|Couverture et précision des citations adaptables ; NLI automatique non oracle et route d'inférence distincte.
U061|résumé|Résumé FActScore|Atomisation/assertions soutenues utile ; biographies et évaluateur automatique pas vérité financière garantie.
U062|méthode et menace ciblées|sources/camel_full.txt §3–5 ; même v2 que URL dossier|Doublon versionné U068 : capacités/interprète et séparation réelle, pas immunité par JSON ou quatre agents.
U063|définitions et motifs ciblés|Archive commune workflow/agent, orchestrator-workers, evaluator-optimizer|Guide industriel adaptable, préférence de simplicité ne retire aucun des quatre rôles imposés.
U064|sections contexte et coordination|Archive commune lignes57–119|Position industrielle datée ; partager contexte utile sans donner à toute source externe tous les pouvoirs.
U065|méthode via version HTML|U066 et archive même article MAST v3|URL de notice regroupée avec U066 ; ne pas compter deux études.
U066|taxonomie et annotation ciblées|Archive commune lignes190–304 ; v3|MAST pour coder défauts ; κ humain sur étape annotée distinct du corpus et juge ultérieur.
U067|résumé|Résumé Who & When|Attribution automatique d'échec imparfaite ; relecture humaine et localisateurs d'événements requis.
U068|méthode et menace ciblées|sources/camel_full.txt §3–5 ; v2|CaMeL exige contrôle de flux, limites de manipulation du contenu reconnues ; code dépôt pas audité ici.
U069|métadonnées seulement|Dépôt CaMeL, URL et titre|Implémentation candidate de contrôle de flux, pas exécutée ni sécurité reproduite ; méthode lue dans U062/U068.
U070|méthode et début résultats|sources/agentdojo_full.txt §3 et §4 ; v3|Paires tâche/attaque et contrôles d'état ; mesurer utilité normale/sous attaque/objectif attaquant ; suite adaptée nécessaire.
U071|résumé|Résumé Attacker Moves Second|Attaques adaptatives contre défenses évaluées ; pas preuve que toutes nos variantes non testées seraient déjà cassées.
U072|métadonnées seulement|Notice OWASP LLM01|Taxonomie de risque complémentaire ; pas essai ni garantie technique, méthode retenue fondée sur primaires CaMeL/AgentDojo.
U073|métadonnées seulement|Dépôt FINSABER|Candidat protocole reproductible, pas installé ; traitement financier approfondi par autre rôle.
U074|résumé|Résumé ChronoBERT/GPT|Évaluation temporelle de modèle, fenêtre de préentraînement distincte du filtre retrieval ; poids/modèle actuel fixes.
U075|résumé|Résumé TimeMachineGPT|Modèles temporels hors périmètre actuel ; ne pas promettre absence de fuite par simple date de corpus.
U076|README ciblé et code ciblé|sources/finrobot_code_2/3/4.txt ; commit63e1884|Plusieurs implémentations ; source canonique et permissions utiles, pas fusion des quatre rôles ni adoption SDK externe.
U077|résumé et introduction|arXiv2405.14767v2, couches de plateforme|Perspective FinRobot, pas preuve des capacités de chaque branche actuelle ; code U076 plus concret.
U078|résumé et introduction|arXiv2411.08804v1, Data/Concept/Thesis|Motif recherche equity, promesse de qualité non répliquée ; pas substitution aux quatre métiers AlphaForge.
U107|métadonnées seulement|Table de disponibilité modèle/région collectée|Catalogue ne prouve ni permissions ni invocation ; seul profil Astra et anciennes requêtes prouvés.
U108|métadonnées seulement|Fiche Sonnet5.5|Contredit choix datathon si pris comme accessible ; notebook cellule23 explicitement négatif, aucune tentative.
U109|métadonnées seulement|Page inference profiles|Disponibilité documentée n'est pas accès et profil global n'est pas résidence canadienne garantie.
U110|métadonnées seulement|Page model access|Accès effectif à vérifier par modèle ; pas d'inscription/modification ni extrapolation STS.
U111|métadonnées seulement|Quotas runtime documentés|Aucun quota effectif de compte interrogé ; succès d'un appel bref ne prouve pas charge soutenue.
U112|métadonnées seulement|Tarifs Bedrock collectés|Ne pas chiffrer coût sans modèle/région/usage/tarif datés ; aucune charge de test mesurée.
U113|concepts, scores et exemples ciblés|Corps grounding Classic/Standard, limites|Score d'ancrage/relevance distinct de vérité/source/temps ; pas de service invoqué ni garantie probabiliste.
U114|métadonnées seulement|Page tiers Guardrails|Options à vérifier si besoin ; ni droits ni performance des tiers établis dans compte.
U115|métadonnées seulement|Tarifs Step Functions|Hors prototype local actuel ; coût à estimer après choix de workflow, aucun prix adopté.
U116|métadonnées seulement|Limites Lambda|Pas de fonction propre au projet créée ; doc pas quota de compte ni preuve d'accès.
U117|métadonnées seulement|S3 Versioning|Candidat historique d'artefacts ; ne prouve ni inaltérabilité ni sauvegarde hors compte éphémère.
U118|métadonnées seulement|S3 Object Lock|Option rétention à étudier avant adoption ; aucun verrouillage ni bucket créé.
U119|corps et format de journaux lus|AWS model invocation logging|Désactivé par défaut et configuration vide réellement observée ; traces locales distinctes de CloudWatch.
U120|métadonnées seulement|AWS X-Ray Python|Ne pas adopter par inertie ; préférer protocole OTel évalué, état support SDK non vérifié profondément ici.
U121|métadonnées seulement|AWS Budgets|Documentation coût ; aucun budget configuré ni permission vérifiée.
U122|métadonnées seulement|Aperçu AgentCore|Catalogue de capacités, lecture Runtime et recherche seulement testées dans note01.
U123|métadonnées seulement|Régions AgentCore|Chaque fonctionnalité a ses régions ; ne pas extrapoler de Runtime à WebSearch.
U124|métadonnées seulement|Release notes AgentCore|Historique utile si adoption, aucun numéro de release global ne prouve support d'une opération.
U125|métadonnées seulement|Tarification AgentCore|Prix unitaire recherche non établi ici, API ne retourne pas facture ; ne pas dire gratuit.
U126|code ciblé et configuration|sources/strands_code_1/2/3/4/5.txt ; commitc8e1351|Candidat graphe/sessions ; défaut Sonnet4.6 us-west-2 exige fournisseur explicite, bornes/persistance à configurer.
U127|métadonnées seulement|Dépôt agentcore-samples|Exemples potentiels, non exécutés et non preuve de droits compte ; ne pas provisionner pour remplir catalogue.
U128|résumé|Résumé AI Agents That Matter|Comparer coût et qualité, splits et contrôle de benchmark ; pas un score unique universel.
U129|résumé|Résumé tau-bench|Contrôles de tâche et stabilité répétée, utilisateur simulé n'est pas humain ; adapter sans API externe.
U130|résumé|Résumé Trading-R1|SFT/RL et trading hors choix actuel de modèle fixe ; ne pas attribuer performance à orchestration seule.
U131|résumé et introduction|Résumé AlphaAgents|Recherche/sélection d'actions selon risque ; précision et profit annoncés non reproduits, capacités source à distinguer métier.
U132|résumé et introduction|Résumé MarketSenseAI2.0|SEC/news/prix/macro RAG intéressant ; résultats période sélectionnée non transférables et non répliqués.
U133|résumé|Résumé FinMem|Mémoire en couches/personas, nécessité provenance temporelle ; gain de trading non adopté.
U134|résumé|Résumé FinCon|Manager/analystes et verbal reinforcement, convictions générées pas preuves ; mémoire à filtrer.
U135|résumé|Résumé FinAgent|Multimodal/reflection, jeu de données/actions différent ; pas besoin établi d'ajouter multimodal ici.
U136|sections README|POC, fournisseurs et données|Éducatif sans exécution réelle de trades ; routes externes et données payantes possibles, aucun exemple lancé.
U137|métadonnées licence seulement|Page LICENSE OpenBB|Licence et compatibilité à auditer sur module précis avant copie ; aucune conclusion de licence globale tirée du dossier.
U138|métadonnées/introduction|README FinGPT|Famille financière/fine-tuning distincte d'outillage actuel ; pas besoin de nouveau modèle démontré.
U139|sections article praticien|Phases/validation du POC robo-advisor|Inspiration tax-aware/review, pas validation scientifique ni licence de code inspectée.
U140|résumé|Résumé LLM risk profiles|Persona/prompt ne remplace pas qualification ni préférences confirmées ; pas vérité du profil.
U141|notice bibliographique|Catalogue Kabale, DOI10.1162/99608f92.ec74a002|Original non lu ici ; ne pas citer résultats comme examinés, route de recherche vers primaire.
U142|échantillon de données|Dataset FinanceBench, champs evidence/page/doc/question|Schéma de provenance intéressant ; ni tout corpus ni licence/droits entièrement audités.
U143|résumé|Résumé FinBen|Taxonomie de tâches financières pour couverture, pas score général de qualité du produit.
U144|résumé|Résumé InvestorBench|Trading multi-actifs/produits, pas même objectif de décision que prototype ; comparaison non directe.
U145|résumé et introduction|ConvFinRe2602.16990v1|Distinguer qualité normative et imitation comportementale ; dialogue synthétique et classement horizon fixe ne valident pas conseil client.
U228|sommaire et introduction|Guide pratique OpenAI PDF pages2–3|Guide industriel d'orientation, non protocole comparatif ; route et outils ne se déduisent pas de sa présence.
U229|résumé|More Agents Is All You Need|Échantillonnage/vote ne représente pas quatre responsabilités ; budget de calcul confondu possible.
U230|résumé|Du et al. Multiagent Debate|Contrepoint favorable ; gains dépendants tâches/modèles et non transposés directement.
U231|résumé|Should we MAD|Coût/temps/hyperparamètres à contrôler, pas supériorité universelle.
U232|résumé|Rethinking Bounds of LLM Reasoning|Contrôle du prompt initial et de la baseline, pas raison d'omettre recherche/qualification.
U233|résumé|Stop Overvaluing Multi-agent Debate|Contrôles expérimentaux et hétérogénéité, affirmation universelle des auteurs non adoptée.
U234|résumé|Debate, not Voting, chemistry2610.33002|Contrepoint ancrage externe/registre/affichage, contexte chimie pas finance ; aucun pourcentage transféré.
U235|résumé|Survey When Can LLMs Actually Correct|Taxonomie feedback/évaluation utile ; auto-correction conditionnelle, pas verdict binaire.
U236|résumé|Tyen error location|Localisation/oracle/classifieur distincts d'autoverification libre ; mesurer origine du feedback.
U237|résumé|MT-Bench and Chatbot Arena|Préférence humaine/conversation ne prouve pas exactitude financière.
U238|résumé|Large Language Models are not Fair Evaluators|Position/ordre de présentation : randomiser/calibrer juge, humain sur litiges.
U239|résumé|Self-Recognition and Self-Preference|Juge peut préférer sa propre famille de sorties ; critère externe nécessaire.
U240|résumé|CALM biases|Taxonomie biais de juge, pas correction automatique garantie.
U241|résumé|Correlated Errors in Large Language Models|Plusieurs modèles/voix pas indépendance assurée ; compter erreurs partagées.
U242|résumé|Great Models Think Alike|CAPA/corrélation d'erreurs et préférences ; mesure spécifique non oracle.
U243|résumé|Hallucination is Inevitable finance history|Cas de données boursières, privilégier fonctions vérifiées et état inconnu ; pas extrapolation universelle.
U244|méthode/annotation/limites ciblées|sources/findver_full.txt §3.4–3.6, limites ; v1|Provenance texte/table, adjudication et perturbations ; ajouter insuffisant/ambigu plutôt que binaire forcé.
U245|résumé|Let Me Speak Freely format restrictions|Syntaxe structurée et raisonnement sémantique à mesurer séparément ; ne justifie pas abandon schémas.
U246|définitions et discussion ciblées|sources/ais_full.txt §1–3 et conclusion|Attribuable à source n'est pas vrai dans monde ; qualité source indépendante.
U247|résumé|RAGAS|Évaluation retrieval/génération modulaire ; juge reference-free n'est pas preuve, route à vérifier.
U248|résumé|Indirect Prompt Injection Greshake|Confusion instructions/données, modèle de menace utile ; pas protection par simple wrapper.
U249|notice et résumé|NIST AI100-2e2025 notice|Vocabulaire et taxonomie, pas protocole d'injection appliqué ni certification.
U250|collecté non lu|PDF NIST doublon de noticeU249|Conserver comme source primaire candidate ; ne pas annoncer lecture intégrale.
U251|métadonnées seulement|Dépôt AgentDojo|Cadre candidat pour fixtures, non installé ; méthode papierU070 examinée.
U252|résumé|Spotlighting|Signalement provenance peut aider mais heuristique/adaptatif non garanti ; pas suffisant seul.
U253|motifs et menace ciblés|sources/designpatterns_full.txt §2–3, passages §4 ; v3|Contraindre contrôle/données ; JSON texte libre encore canal d'injection, six motifs à adapter.
U254|code ciblé et licence|sources/langgraph_code_0/1/2/3.txt ; commit08a2016|MIT, pyproject1.2.22 ; interruption rejoue nœud, idempotence requise ; non installé.
U255|corps documentaire lu|LangGraph persistence|Thread/checkpoint/store distincts, InMemory ne survit pas redémarrage ; portée métier à écrire.
U256|métadonnées/introduction|AutoGen README|Alternative framework, pas migration ni compatibilité prouvée ; capacité manquante non établie.
U257|métadonnées/introduction|Microsoft Agent Framework README|Candidat de remplacement distinct d'AutoGen ; pas adopté sans besoin/contrats/route.
U258|métadonnées/introduction|AG2 README|Autre lignée AutoGen ; identité/licence/version à vérifier avant copie, pas équivalence implicite.
U259|métadonnées/introduction|CrewAI README|Rôles textuels n'assurent pas tâches réelles/provenance ; aucun motif irremplaçable identifié.
U260|métadonnées et doc officielle complémentaire|OpenAI SDK repo, sources/openai_sdk_tracing.txt|Cadre d'agents, fournisseur et export tracing séparés ; non installé, ne pas détourner route AWS.
U261|doc officielle complémentaire ciblée|Developer guide integrations-observability sections SDK|Tracing serveur activé par défaut dans cas courant documenté ; contrôler destination, pas supposer isolation d'un wrapper.
U262|métadonnées/introduction|PydanticAI README|Validation et outils candidats, pas vérité métier ; source actuelle FinRobot donne exemple concret, pas exécuté.
U263|métadonnées/introduction|smolagents README|Exécution de code agent nécessite confinement ; non retenu pour calcul fermé sans besoin démontré.
U264|métadonnées seulement|OTel genai conventions dépôt dédié|Schéma de spans candidat, migration/versions à épingler ; pas observabilité déjà configurée.
U265|métadonnées seulement|OTel genai conventions ancien chemin|Ne pas compter double standard indépendant ; vérifier statut du chemin avant adoption.
U266|métadonnées/introduction|Langfuse dépôt|Plateforme observabilité, route des évaluateurs/export et licence par composant non auditées.
U267|métadonnées/introduction|Langfuse self-hosting|Autohébergement possible ne veut pas dire configuré ni gratuit à exploiter ; pas déployé.
U268|métadonnées/introduction|Phoenix README|Candidat observabilité, pas oracle financier ; destinations/licence/évaluateurs à auditer.
U269|métadonnées/introduction|Inspect AI README|Cadre d'évaluation candidat, outils/solveurs/juges à configurer ; aucun score exécuté.
U270|métadonnées/introduction|Promptfoo README|Fixtures et comparaisons possibles, endpoints/juges externes non autorisés par simple exemple.
U271|métadonnées/introduction|DeepEval README|Métriques automatisées pas vérité ; licence/routes/coût non entièrement audités.
U310|métadonnées seulement|Fiche Nova Lite|Autre modèle non invoqué, hors route fixée ; catalogue ne décide pas.
U311|métadonnées seulement|Fiche Nova2 Lite|Autre modèle non invoqué, pas changement de modèle/région.
U312|métadonnées seulement|Fiche Llama3 70B|Hors modèle fixé ; disponibilité/quotas non prouvés.
U313|métadonnées seulement|Fiche Mistral Large|Hors modèle fixé ; aucune inférence comparative.
U314|métadonnées seulement|Geographic cross-region inference|Distinguer région endpoint et périmètre effectif ; résidence Astra pas démontrée par cette page.
U315|métadonnées seulement|Quotas Bedrock|Documentation pas valeur actuelle de compte ; non interrogé.
U316|métadonnées seulement|Endpoints et quotas généraux|Référence technique si besoin, endpoint utilisé us-east-1 ; ne prouve pas pays d'inférence.
U317|métadonnées seulement|Langues Guardrails|Chaque fonction a sa portée linguistique ; ne pas généraliser prise en charge français à ARchecks.
U318|métadonnées seulement|Support Guardrails|Option future, modèle/fonction/région à confirmer ; aucun guardrail exercé.
U319|métadonnées seulement|Historique Bedrock|Pas de dates de fermeture extrapolées ; avis agentsU040 lu directement.
U320|métadonnées seulement|Knowledge Bases|RAG optionnel, embedding/retrieve-and-generate routes auxiliaires à prouver ; rien créé.
U321|métadonnées seulement|Flows|Orchestration optionnelle, pas capacité produit présente ni remplacement implicite quatre rôles.
U322|métadonnées seulement|Prompt Management|Gestion versions potentielle, contrats et provenance peuvent commencer localement ; non utilisé.
U323|métadonnées seulement|Evaluate Bedrock resources|Évaluation gérée optionnelle, modèle juge et droits non vérifiés ; pas oracle.
U324|introduction et fonctionnement|AgentCore observability|OTel/CloudWatch nécessitent instrumentation ; aucun runtime propre ni export testés.
U325|métadonnées seulement|Runtimes Lambda|Référence d'empaquetage future ; pas d'hébergement choisi.
U326|métadonnées seulement|Quotas Step Functions|Pas quotas effectifs du compte ; usage non requis aujourd'hui.
U327|métadonnées seulement|ECS Express Mode|Option hébergement non demandée, accès non testé ; ne pas confondre avec Step Functions Express.
U328|métadonnées seulement|Annonce AWS Free Tier|Compte atelier temporaire distinct d'un nouveau compte personnel ; aucun crédit supposé.
U329|métadonnées seulement|Blog nouveau Free Tier|Même familleU328, pas économie garantie du datathon.
U330|métadonnées seulement|Free Tier FAQ|Conditions non examinées intégralement ; aucune décision de coût fondée dessus.
U331|métadonnées seulement|Tarif Amplify|Déploiement pas dans mission, aucun coût adopté.
U332|métadonnées seulement|Sample genai market data analysis|Exemple AWS de démo, code/licence/routes non audités ; pas réutilisation.
U333|métadonnées seulement|Sample wealth advisor platform|Architecture démonstrative, ne prouve ni conformité ni qualité financière ; non exécutée.
U334|métadonnées seulement|Blog investment research Strands/AgentCore|Candidat guide d'intégration ; pas preuve d'accès dans compte ni benchmark reproduit.
U335|métadonnées seulement|Blog wealth management part1|Illustration de plateforme, pas exigence de multiplier services ni résultat acquis.
U336|métadonnées seulement|Cas Morningstar|Retour industriel contexte/données propres, non transférable sans examen approfondi ; pas preuve.
U337|métadonnées seulement|Cas Heurist Finance|Retour industriel, pas protocole financier contrôlé ni connecteur installé.
U338|métadonnées seulement|EKS/AgentCore finance|Architecture infrastructure, besoin Kubernetes absent du prototype ; pas adopté.
U339|métadonnées seulement|AWS Open Data market-data|Catalogue source potentiel ; accès/licences/dates à examiner par dataset, aucun téléchargement massif.
U351|définitions et motifs via page canonique|Même guide que U063 après redirection|Doublon de guide Anthropic, ne pas compter preuve indépendante ni imposer suppression rôle.
U352|sections ciblées|Compaction, structured note-taking, sub-agent architectures|Compression peut perdre contraintes ; références brutes conservées hors contexte, mémoire pas vérité.
U353|sections ciblées|Generator/evaluator, calibrage, sprint contract|Critères+observation de vraie UI utiles pour équipe de construction ; résultats industriels pas preuve d'agents financiers.
U356|métadonnées seulement|Bedrock multi-agent collaboration|Fonction Classic documentée, accès nouveau non acquis ; quatre rôles produit ne nécessitent pas ce service.
U357|métadonnées seulement|AgentCore getting started CLI|Recette de provisioning non exécutée ; pas nécessaire pour API directe recherche testée.
U358|métadonnées seulement|Bedrock trace events|Trace d'agent géré différente des journaux locaux et pensée interne ; aucun agent Classic utilisé.
U359|sections configuration ciblées|AWS credentials/region, modèle rapide, limitations|Développement Claude Code autre surface ; pas invoquée ici, ne pas confondre WebSearch natif avec APIAgentCore.
U360|corps complet et opération réelle|web-search-api.html, preuve_web_search.json|InvokeWebSearch réussi us-east-1 sans Gateway ;3résultats/651ms ; date d'index erronée détectée, pas facture mesurée.
U361|corps complet|Gateway connector WebSearch, versions/filtres|WebSearch distinct WebAnswer ; Gateway pas créé ni nécessaire pour chemin direct.
U362|page d'entrée/métadonnées|Portail docs Strands|Index mouvant, version code épinglée plus fiable pour décision ; aucun tuto exécuté.
U370|page d'entrée et exemple|Portail Pydantic|Validation/agents/Logfire distincts, exemple fournisseur extérieur non adopté ; typage n'est pas vérité.
U371|page d'entrée/métadonnées|Portail Strands|Offres harness/box/shell/decider ne prouvent pas accès compte ; ne pas changer modèle Astra par défaut commercial.
"""

manual = {}
for line in rows.strip().splitlines():
    key, level, locator, decision = line.split("|", 3)
    manual[key] = {"reading_level": level, "passages": locator, "decision_and_limit": decision}

extra = {"U043", "U062", "U065", "U020", "U054",
         "U351", "U352", "U353", "U356", "U357", "U358", "U359",
         "U360", "U361", "U362", "U370", "U371"}
records = []
for x in inventory:
    relevant = any(o["section"].startswith(("9.1 ", "9.6 ", "9.8 ")) for o in x["occurrences"])
    if not relevant and x["id"] not in extra:
        continue
    if x["id"] not in manual:
        raise ValueError(f"Missing human triage: {x['id']}")
    meta_path = BASE / "collecte" / f"{x['id']}.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    records.append({
        "id": x["id"],
        "url": x["url"],
        "dossier_occurrences": [o for o in x["occurrences"] if "00_prompt2" in o["file"]],
        "capture": str(meta_path.relative_to(ROOT)) if meta_path.exists() else None,
        "http_status": meta.get("status"),
        "final_url": meta.get("final_url"),
        "capture_title": meta.get("title"),
        "captured_at": meta.get("retrieved_at"),
        "capture_sha256": meta.get("sha256"),
        **manual[x["id"]],
        "execution": "InvokeWebSearch unique voir preuve_web_search.json" if x["id"] == "U360" else "Aucune exécution de l'implémentation ou expérience publiée",
        "license_note": (
            "Fichiers de licence identifiés dans sources ; portée précisée note03."
            if x["id"] in {"U054", "U076", "U126", "U254"}
            else "Droits de réutilisation non audités ; collecte/lecture n'autorise pas copie ou redistribution du code/dataset."
        ),
    })

(OUT / "triage_sources.json").write_text(json.dumps({
    "date": "2026-11-15",
    "scope": "Toutes URL §9.1/9.6/9.8 + U043/U062/U065 hors registre + compléments explicitement confiés",
    "warning": "Une URL n'est pas une étude indépendante. HTTP 200 n'est pas un niveau de lecture. Métadonnées/collecté non lu ne soutiennent aucun résultat scientifique.",
    "records": records,
    "unresolved_references": [{
        "reference": "GSN Community Standard — SCSC — scsc.uk",
        "dossier_line": 1270,
        "reading_level": "référence du dossier seulement",
        "access": "Le dossier rapporte une page vide ; ce constat n'a pas été revalidé ici et aucune URL de version précise n'est fournie.",
        "decision": "Norme candidate pour argumentaire d'assurance, ni version ni texte lus ; aucune décision technique n'est fondée sur cette référence.",
    }],
}, ensure_ascii=False, indent=2) + "\n")

header = """# Triage explicite des références

Registre de lecture de la sous-mission AWS/agentique. Les notices et captures sont datées et identifiées dans `triage_sources.json`. **HTTP 200 n’est pas une lecture**, et une notice n’est pas un résultat reproduit. Les niveaux modestes ci-dessous sont intentionnellement conservés. Les notes 01–03 approfondissent les sources décisives ; plusieurs URL peuvent désigner le même article ou le même guide.

"""
table = "| ID / URL | Niveau et passage effectivement lu | Décision / limite |\n|---|---|---|\n"
for r in records:
    clean = lambda s: s.replace("|", "\\|").replace("\n", " ")
    table += f"| [{r['id']}]({r['url']}) | {clean(r['reading_level'])} — {clean(r['passages'])} | {clean(r['decision_and_limit'])} |\n"
(OUT / "triage_sources.md").write_text(header + f"{len(records)} URL documentées ; il ne s’agit pas de {len(records)} publications indépendantes.\n\n" + table + "\nRéférence sans URL précise du registre §9.6, ligne1270 : **GSN Community Standard — SCSC — scsc.uk**. Seule la référence du dossier a été lue. Le dossier rapporte une page vide ; ce constat n’a pas été revalidé ici. Version et texte non lus ; aucune décision technique de ces notes ne repose sur cette norme.\n")
print(json.dumps({"records": len(records), "section_9_only": sum(any(o["section"].startswith(("9.1 ", "9.6 ", "9.8 ")) for o in x["occurrences"]) for x in inventory)}))
