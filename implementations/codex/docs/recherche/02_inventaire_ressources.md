# Ressources accessibles et vérifications

**15 novembre 2026 · État observé pendant le Prompt 2.**

L’accès à une documentation, la présence d’un outil et la réussite d’une opération sont trois observations différentes. Cet inventaire les distingue. Aucun abonnement, connecteur, service cloud ou site n’a été créé pour cette recherche.

## Accès réellement utilisés

| Ressource | Vérification réalisée | Utilisation et limite |
|---|---|---|
| Documents locaux 00, 00B, 01, dossier fourni et atlas | Fichiers ouverts, liens extraits et rattachés à leurs occurrences | Base de travail et contraintes du projet ; leurs affirmations sont confrontées aux primaires |
| Page officielle du datathon, U340 | Corps de page et calendrier lus dans la capture du 15 novembre | Annonce une fermeture des comptes AWS le 16 novembre à 13 h 59 ; cela motive la conservation locale, sans prouver l’exécution future de cette fermeture |
| Notebook d’introduction | 35 cellules examinées, sans exécuter ses cellules d’installation, d’acquisition ou d’inférence | [Audit cellule par cellule](finance/04_experiences_et_notebook.md) ; exemples pédagogiques, pas moteur financier validé |
| Starter local | CSV lus par les expériences ; empreintes des entrées conservées | Prix et FX employés dans un protocole limité ; pas de preuve ESG, de positions de FNB ou de disponibilité historique complète |
| SearchService documentaire | Recherches et ouvertures de pages réussies | Découverte de publications et primaires ; aucun service auxiliaire de réponse générative demandé |
| HTTP direct | Collecte des 505 URL, extraction HTML/PDF et enregistrement des erreurs | Des HTTP 200 contiennent des coquilles ou des contrôles d’accès ; le niveau de lecture est consigné séparément |
| Connecteur GitHub | Lecture réussie des métadonnées publiques de `microsoft/OptiGuide`, dépôt `673095495`, branche `main` | Droit de lecture observé, aucun droit d’écriture revendiqué ; aucun inventaire de dépôts privés |
| Git/HTTP sur dépôts publics | Commits résolus, fichiers ciblés de quatre dépôts agentiques lus ; code financier également inspecté | Une inspection statique ne prouve pas l’exécution. Commits, fichiers et licences dans les journaux spécialisés |
| Python, Poppler | Extraction de textes, rendu de pages PDF et petits calculs réellement exécutés | Pas d’OCR génératif ni de modèle auxiliaire local ; environnement d’expérience séparé de celui du produit |
| Banque du Canada Valet | JSON parsé, 1 461 observations contrôlées | Unité CAD/USD, dates et valeurs contrôlées ; pas de reconstitution des publications historiques |
| FRED CSV | CSV DGS10 récupéré et contrôlé | Série courante, sans millésime ; DGS10 ne représente pas un placement quotidien sans risque en CAD |
| SEC company facts | JSON Apple récupéré ; dates `end` et `filed` examinées | Plusieurs dépôts pour une même fin d’exercice ; le filtre chronologique reste à écrire dans une utilisation produit |
| AWS STS et Bedrock | Identité, profil d’inférence et configuration de journalisation consultés | [Requêtes et limites exactes](aws_agentique/01_preuves_aws_et_recherche.md) |
| AWS AgentCore Web Search | Une requête réussie, trois résultats | Recherche effectivement disponible. Une date d’index erronée montre la nécessité de vérifier la source primaire |

Les expériences n’ont pas interrogé Yahoo/yfinance ni les API payantes proposées dans certains dépôts. Les données du starter ont été utilisées localement ; elles n’ont pas été redistribuées par cette recherche.

## Bases documentaires mobilisées

| Famille | Ressources consultées | Précaution d’usage |
|---|---|---|
| Cadres canadiens | AMF, ACVM/OCRI, FP Canada, BSIF | Version, date d’entrée en vigueur, activité et personne visées ; certains PDF accessibles par recherche web mais refusés en HTTP direct |
| Pratiques professionnelles et cours | CFA Institute, FPSB, cours de Boyd/Vandenberghe et ressources d’analyse de décision | Résumé de cours distingué du cours intégral ; cadre professionnel distingué d’un résultat empirique |
| Publications scientifiques | arXiv, revues/actes, pages d’auteurs, dépôts institutionnels, RePEc | Résumé, manuscrit accepté et version publiée distingués ; métadonnées d’index non prises comme date primaire |
| Aides à la décision | Cochrane, OHRI/IPDAS, publications de psychologie et interaction humain–IA | Transfert à la finance explicitement limité ; droits sur les instruments séparés des droits sur les articles |
| Implémentations ouvertes | GitHub, documentation versionnée, fichiers de licence, métadonnées de distributions | Code, données, modèles et mode de livraison ont des conditions distinctes |
| Documentation technique | AWS, Strands, LangGraph, solveurs, clients de données | Une fonction documentée n’est pas une ressource déployée ni un droit du compte |

Il ne s’agit pas d’un abonnement établi à toutes les revues : les textes payants, les refus et les contenus non obtenus restent signalés dans les registres.

## Route d’inférence

Les métadonnées des quatre sessions de recherche déclarent toutes `amazon-bedrock-runtime`. La [preuve expurgée](verification_route_codex.json) documente cette observation. Le modèle convenu est `global.openai.gpt-6-astra`, avec le profil AWS `alphaforge` et le point d’entrée `us-east-1`.

Les opérations signées ont confirmé le compte attendu et le profil d’inférence actif. Des traces produit antérieures conservent aussi des identifiants d’invocation. Ces éléments ne sont ni une facture ni une capture réseau de chaque inférence interne ; aucune résidence exclusivement canadienne n’est revendiquée.

La recherche AgentCore emploie `InvokeWebSearch`, sans `WebAnswer`. Aucun appel à un embedding, reclassement neuronal, juge LLM tiers, résumé opaque, OCR génératif ou modèle livré par une bibliothèque n’a été effectué dans les expériences. Les inférences des chercheurs restent celles des sessions AWS vérifiées.

Un futur SDK doit imposer explicitement fournisseur, région, modèle et politique de reprise. Les chemins secondaires — validation structurée, récupération, évaluation et télémétrie — doivent être examinés aussi. Par exemple, les valeurs par défaut du fournisseur Strands inspecté ne sont pas celles du projet.

## Ressources exposées mais non établies ou non utilisées

La session expose aussi contrôle de navigateur, sessions documentaires, Sites et gestion de plugins. Ils ne répondaient pas à un besoin non couvert de cette étape ; aucun accès à leurs documents ou comptes n’a été présumé, et aucune nouvelle interface n’a été produite.

La découverte de plugins a repéré **AWS Data Analytics**, **Firecrawl** et **TinyFish**, avec un état non installé. Ils ne constituent pas des connecteurs utilisables ni une preuve de route AWS de leurs traitements. Aucune installation n’était nécessaire pour poursuivre.

La liste AgentCore vérifiée est vide. La journalisation centralisée des invocations Bedrock n’est pas configurée dans la réponse observée. Les quotas de charge du compte, les prix réellement facturés et l’accès aux services non invoqués ne sont pas établis par cette mission.

L’inventaire antérieur du projet rapporte l’absence de bucket S3 et de Lambda AlphaForge ; ce constat n’a pas été rafraîchi ici. S3, Step Functions, Runtime, Guardrails, Knowledge Bases, Athena et les autres services de l’atlas restent des possibilités documentées, avec des expériences à définir lorsque leur utilité est établie. Leur seule présence dans les 36 captures ne prouve aucun déploiement.

Les [134 liens supplémentaires de l’atelier](aws_agentique/04_annexe_atelier_134.md) sont examinés dans une annexe distincte du registre du dossier fourni. La collecte, le triage et les passages approfondis y restent séparés.
