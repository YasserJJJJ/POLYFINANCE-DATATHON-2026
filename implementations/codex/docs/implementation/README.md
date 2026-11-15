# Implémentation du fonctionnement validé — Prompt 4

**Actualisation Prompt 5 : version 0.5.0.** Le
[dossier de défense](../defense/README.md) contient la revue indépendante,
les défauts corrigés et les démonstrations actuelles. Les chiffres et traces
du Prompt 4 ci-dessous restent un état historique, avec leurs propres versions.
La politique historique est désormais explicite (méthode v2), les demandes
sources sont immuables, les conflits matériels bloquent le calcul dépendant,
et un diagnostic budgétaire séparé traite le retrait supérieur au capital.
Le schéma joint reflète ces corrections.

État : 15 novembre 2026. Le parcours utilisable est servi par
`Ouvrir_AlphaForge.command` et décrit dans le [README principal](../../README.md).
Le [schéma SVG](architecture.svg), sa [source Mermaid](architecture.mmd) et les
[contrats](CONTRAT_INTEGRATION.md) décrivent le même système.

## Ce qui fonctionne

| Capacité | Comportement réel et preuve |
|---|---|
| Quatre contributions | Quatre schémas, contextes, droits d'écriture, outils et appels Bedrock distincts. Robert et Amira ont leurs reçus dans les dossiers de démonstration. |
| Dossier faisant autorité | Transactions SQLite, révisions monotones, événements, faits et artefacts adressés par SHA-256 ; contenu immuable, statut courant séparé. |
| Révision | Le remplacement d'un fait invalide ses descendants et retire immédiatement la vue courante. Le contenu historique reste lisible. |
| Réutilisation | Recherche générique et diagnostic du portefeuille initial conservés lors du changement de retrait. La revue du mandat, l'allocation et sa restitution sont nouvelles. |
| Résolution avec retours | Approfondissement documentaire borné Agent1→Agent1 ; demande incomplète Agent2→Agent3→Agent0 ; clarification humaine→nouveau run. Les états et raisons sont enregistrés. |
| Calcul et données | LP sous scénarios, contrôle primal-dual, borne indépendante, témoins d'optima multiples, sensibilités ; comparaison historique CAD et vérification des versions de données entre Agent1 et Agent2. |
| Restitution fidèle | Agent3 organise des identifiants d'affirmations. Le noyau conserve leur texte calculé, les pointeurs, limites et questions. Affichage ≠ approbation. |
| Reprise | Checkpoint LangGraph + résultat transactionnel par tâche + cache de reçus. Un test interrompt après commit du calcul avant checkpoint, rouvre le service et termine sans second calcul. |
| Parcours utilisable | Création, exemples éditables, activité des rôles, preuves, inspection JSON, correction/variante, comparaison, export, reprise, vues bureau/mobile. |

Le contrat de départ est [la conception validée](../conception/README.md).
Les équations et règles financières n'ont pas été remplacées par le contenu du
JSON illustratif. `finance.examples()` ne retourne que les entrées.

## Décisions techniques prises dans le cadre autorisé

| Décision | Motif, qualification et limite |
|---|---|
| SQLite et objets immuables locaux | Un magasin transactionnel suffit à cette échelle. Corrections, invalidations, écritures et retour de tâche sont commis ensemble. Chaque lecture d'objet vérifie son empreinte. |
| LangGraph 1.2.22 + SqliteSaver | La machine explicite minimale et LangGraph passent panne/reprise/attente. LangGraph apporte un graphe et des checkpoints maintenus ; le dossier reste indépendant du framework. Les 29/9 ms de l'essai sans modèle ne sont pas un classement de performance. |
| Strands conservé comme alternative | Documentation examinée au Prompt 3 ; aucune exécution comparée ici. Rien ne justifie d'embarquer deux orchestrateurs. |
| Client Bedrock existant conservé | Il contrôle le compte atelier, refuse les routes de remplacement et fournit des reçus. LangGraph n'instancie aucun autre fournisseur. LangSmith est désactivé explicitement, y compris en présence de variables d'activation héritées. |
| SciPy/HiGHS plutôt qu'une nouvelle pile de portefeuille | Le premier problème validé est un LP de demi-L1, pas une estimation moyenne-variance. Résidus et borne analytique permettent une vérification directe. Les bibliothèques recensées au Prompt 2 restent des candidates pour leurs problèmes propres. |
| Moteur historique existant adapté | Achat-conservation, prix ajustés employés une fois, CAD, change as-of contrôlé, dates d'acquisition vérifiées. Il ne simule pas une sélection point-in-time ni une projection de retraite. |
| Recherche AWS + extraction déterministe | InvokeWebSearch fournit des liens ; seuls les documents effectivement récupérés produisent des pièces. PDF/HTML, tailles, dates et empreintes bornent le travail. Aucune réponse opaque d'un autre modèle n'est incorporée. |
| Bibliothèque fermée d'outils | Les agents peuvent sélectionner une méthode, demander une recherche ou renvoyer une question ; aucun programme financier généré à la volée n'est exécuté. |
| Interface FastAPI locale | Les réalisations utiles restent en place, l'ancien parcours est sous `/legacy`. Les interactions de la nouvelle interface appellent le vrai service de dossiers. |

Les détails et expériences sont dans [aws_runtime.md](aws_runtime.md),
[finance.md](finance.md) et [experience.md](experience.md).
Le [journal d'admission](JOURNAL_CANDIDATS.md) relie les briques effectivement
retenues aux candidats et sources du Prompt 2.
Il n'y a pas de changement de promesse exigeant une nouvelle validation.
Les extensions encore absentes sont nommées ci-dessous.

## Transactions, reprise et indépendance

`Store.commit` vérifie le run actif, le `read_set` réellement transmis et
le couple identifiant/type/propriétaire de chaque sortie. Une dépendance
ordinaire doit avoir été lue. Une dépendance produite dans le même commit
est référencée par `$id`, résolue vers sa version exacte avant enregistrement.
Une sortie dépendant d'une entrée invalidée dans ce commit est refusée.

La révision du dossier, la version d'une pièce, l'identifiant du run, la tâche,
la tentative d'outil et le checkpoint sont des identités différentes.
`task_id=run_id:step_index` permet de retourner un commit déjà effectué après
une interruption. Les reçus réussis sont réutilisés pour la même tâche, le même
outil et les mêmes entrées. Les entrées exactes des opérations sont aussi
conservées comme objets immuables.

Des verrous de fichier sérialisent le run et chaque opération dans ce système
local. Deux processus demandant simultanément la même opération ont produit
un seul effet dans le test indépendant. Cela ne constitue pas une garantie
distribuée sur un système de fichiers réseau. Après une coupure entre la
requête AWS et son reçu, l'issue distante peut rester inconnue : la tentative
est signalée, et une reprise peut engendrer un nouvel appel facturé.

Le manifeste logiciel du run contient les hashes du service, des outils, du
client Bedrock et des exigences de dépendances. Le calcul conserve également
ses versions NumPy/SciPy et ses entrées. **Rejouer les reçus enregistrés** est
différent de demander une nouvelle réponse au modèle : la deuxième opération
n'est pas garantie identique.

## Trois représentations séparées

1. **Exécution** : graphe LangGraph, tâches et checkpoints. Il détermine qui
   intervient ensuite, avec un maximum de 24 transitions par run.
2. **Questions et preuves** : nœuds `questions.*`, artefacts, méthodes, assertions,
   pointeurs et dépendances versionnées. Une correction remonte aux conclusions
   dépendantes ; une branche toujours valide garde sa version.
3. **Parcours utilisateur** : projection de la vue courante, activité, preuves et
   comparaison. Les questions de méthode ne sont pas présentées comme des
   informations personnelles que l'utilisateur devrait inventer.

Le graphe de questions représente les deux familles admises et leurs retours ;
il ne synthétise pas encore arbitrairement de nouvelles formulations financières.
Les cycles sont des étapes/révisions successives. Les dépendances d'artefacts
restent dirigées vers des versions déjà produites.

## Démonstrations conservées

Les [résultats finaux](proofs/final_demo/summary.json) relient les dossiers,
les sorties, les transitions et les requêtes AWS. Les exports complets sont
dans le même répertoire.

**Robert** part du même portefeuille de 100 000 CAD dans les deux plans.
Le retrait est corrigé de 30 000 à 40 000 CAD, toujours à douze mois.
Le capital déplacé minimal passe de 30 000 à 40 000 CAD. Il s'agit de deux
plans comparés à la même allocation initiale, pas de 40 000 CAD supplémentaires
après exécution du premier plan.

La recherche indépendante du montant et `baseline_stress@1` sont réutilisés.
Ce dernier conserve les pertes initiales de 18 250 et 13 900 CAD sous les deux
chocs. Il ne prétend pas que l'allocation initiale finance le nouveau retrait.
La nouvelle allocation, son admissibilité, ses sensibilités et la richesse
après retrait sont recalculées. D'autres allocations ont le même minimum :
la restitution ne transforme pas le choix numérique du solveur en préférence.

**Amira** réduit TSLA de 25 % à 10 % dans un portefeuille fictif SPY/XIU/TSLA,
redistribuant proportionnellement le reste. Les deux allocations sont
rejouées sur la grille commune historique disponible, en CAD. La recherche
voit désormais l'inventaire local ; Agent2 contrôle l'égalité des empreintes
et dates avec ses propres entrées.

Un essai antérieur d'Amira s'est arrêté : Agent1 ne voyait pas l'inventaire des
données et avait raison de demander un approfondissement. Cette lacune de
contrat a été corrigée par l'outil `inputs.inspect`, pas en fournissant au
modèle la conclusion attendue. Les anciens dossiers restent conservés.

## Vérification et portée des preuves

La suite Python vérifie des cas contrôlables, des données locales, les
transactions et les reprises ; les agents sont simulés uniquement lorsque
le test l'annonce. Les démonstrations finales et le parcours UI AWS sont
séparés de ces tests. Les compteurs exacts et la sortie de la suite finale
figurent dans [verification.json](proofs/verification.json).
La suite finale compte **132 tests réussis**. Le
[contrôle de livraison après redémarrage](proofs/delivery_checks.json) retrouve
les mêmes dossiers, douze reçus AWS et les empreintes intactes, sans nouvelle
inférence.

Deux relecteurs distincts ont examiné le noyau et le service :
[audit du noyau](audit_noyau_independant.md) et
[revue du service](aws_runtime.md#revue-indépendante-de-lintégration-du-service).
Ils ont reproduit des défauts avant correction : droits d'écriture trop larges,
dépendance invalidée dans le même commit, démarrage d'un ancien run, choix de
clarification ignoré, approfondissement sans effet et double opération
simultanée. La revue financière a également fait corriger l'affichage des
solutions infaisables, les unités historiques et les optima multiples.

Un accord de relecteurs ne remplace pas une vérification indépendante :
résidus, borne analytique, cas de test, reçus AWS et captures UI conservent
des statuts distincts.

## Ce qui reste partiel ou prévu

- **Méthodes financières** : deux familles exécutables. Pas encore d'IIS général,
  coût de transaction calibré, allocation robuste par covariance, CVaR optimisée,
  probabilité d'objectif, valorisation fondamentale ou preuve ESG par actif.
- **Instrument réel de réserve** : non qualifié. La réserve abstraite est une
  hypothèse de calcul, jamais une garantie de ZST ou d'un autre produit.
- **Recherche** : corpus ciblé et trois résultats web par requête, un
  approfondissement supplémentaire par run. Sans OCR ; une capture postérieure
  à la date de connaissance est exclue. Une revue générale exhaustive n'est
  pas promise à chaque demande.
- **Interprétation** : schémas stricts et ancrage lexical des valeurs extraites,
  mais pas certification de toute interprétation sémantique. Les déclarations
  structurées priment ; les doutes demeurent des clarifications.
- **Conformité** : structure inspirée des fonctions professionnelles, aucune
  certification de convenance ni questionnaire psychométrique validé.
- **Résultats** : scénarios sans probabilité, historique descriptif, aucun test
  de performance future ou étude utilisateur de qualité de décision.
- **Infrastructure** : locale avec inférences/recherche AWS. S3, Step Functions,
  AgentCore Runtime, authentification multi-utilisateur et déploiement public
  ne sont pas construits. Le profil global ne démontre pas une résidence canadienne.

La reprise du développement et la sauvegarde sont décrites dans
[ETAT_REPRISE.md](ETAT_REPRISE.md).
