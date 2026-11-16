> **Document de recherche daté du 15 novembre 2026**, hors produit. Les passages sur le calendrier, les décisions à prendre et l'organisation du travail sont historiques : ce ne sont pas des consignes. Certaines pièces de travail citées (`research/fiches/`, `research/R08-…`, `docs/etat.md`, `docs/cadrage/`) ne sont pas dans cette archive. Entrée de l'archive : `LIRE_EN_PREMIER.md`.

# AlphaForge — Diagnostic et contrat de refonte

**15 novembre 2026 · proposition soumise au porteur, en attente de validation.** Aucun fichier du produit n'a été modifié pour l'établir. Les chiffres marqués « exploratoire » viennent de `docs/refonte/calcul_exploratoire.py` (hors produit, graine fixe, reproductible). Ce document ne consigne aucune décision : celles de la section 10 reviennent au porteur.

## 1. Verdict

Le produit actuel tient une promesse étroite, et il la tient : chaque chiffre affiché sort d'un calcul identifié. Il ne réalise pas l'intention d'origine. Des cinq fonctions à faire exécuter :

| Fonction visée | État réel dans le produit |
|---|---|
| Qualification et formalisation | remplacée par des hypothèses écrites d'avance par les développeurs |
| Recherche et revue de littérature | absente |
| Analyse quantitative | réelle, mais limitée à des statistiques descriptives sur une seule trajectoire de cinq ans |
| Confrontation des arguments | absente |
| Restitution et interaction | réelle pour l'affichage ; ni adaptée au lecteur, ni dialoguée, ni révisable à partir du travail déjà fait |

Ce que cela change, sur le cas de Robert et de Tesla :

| Le dossier actuel affiche | Le calcul exploratoire montre |
|---|---|
| « Part maximale de Tesla : 9 % », sous un seuil de perte de 15 % choisi par les développeurs | La part va de 0 % à 23 % quand la capacité de perte va de 12,5 % à 25 %. À 12 % ou moins, le portefeuille fictif actuel est déjà hors limite sans Tesla : il a connu une baisse de 12,3 %. |
| « Pire baisse avec 10 % de Tesla : −15,3 % » | C'est une seule trajectoire. En rejouant l'historique par blocs sur trois ans, la baisse franchit 15 % dans 20,9 %, 44,7 % ou 60,3 % des trajectoires selon l'hypothèse de rendement moyen ; sans Tesla : 5,6 %, 19,2 %, 35,4 %. |
| 9 % de Tesla, présenté comme la part compatible | À 9 %, la baisse franchit 15 % dans 17,7 % à 57,0 % des trajectoires. |
| « Rendement annualisé 9,7 % contre 7,7 % », mis en regard du risque | Le rendement moyen n'est pas estimable sur cinq ans : pour Tesla, moyenne arithmétique de +22,7 % par an avec une erreur type de 24,9 points, soit de −27 % à +73 % à deux erreurs types. Aucun rendement ne peut être mis en face du risque. |
| Une « tension » fondée sur la seule baisse en cours de route | Le dossier tait une mesure qu'il a calculée et qui nuance sa thèse : sur les 105 fenêtres glissantes de trois ans de l'échantillon, le rendement le plus bas reste positif pour chaque option (+17,3 % sans Tesla, +17,9 % avec 10 %, +17,3 % avec 20 %). « Préserver le capital » n'est jamais traduit en grandeur mesurable. Or les deux lectures divergent : avec 10 % de Tesla, la part des trajectoires qui finissent sous leur valeur de départ passe de 4,2 % à 6,1 % (moyennes historiques), quand celle des trajectoires qui franchissent 15 % de baisse en route passe de 5,6 % à 20,9 %. |
| Des conventions de calcul posées sans étude | En regardant la valeur chaque jour et non chaque vendredi, la pire baisse avec 10 % de Tesla est de −17,5 % et non de −15,3 %, et la part de 9 % tombe à 6 % : le sommet de Tesla tombe un lundi. Sans rééquilibrage hebdomadaire, le rendement baisse quand on ajoute Tesla (+8,4 %, +8,1 %, +7,8 % pour 0, 10 et 20 %), alors que le dossier affiche une hausse (+7,7 %, +8,8 %, +9,7 %) : le « gain » vient d'un rééquilibrage hebdomadaire sans frais. |
| Un dossier « adapté au profil » | La même demande et le même scénario, sous les profils d'Amira et de Mateo, donnent treize affirmations identiques sur quinze, les mêmes chiffres clés et la même part maximale pour un horizon de trois ans et de quinze ans, avec contrôle conforme. Le test du concours « changez un profil » n'avait jamais été exécuté. |
| « QQQ n'offre pas d'exposition à Tesla elle-même » (affirmation A-013, dossier marqué « contrôle conforme ») | Aucun enregistrement ne la soutient : elle cite la composition du portefeuille fictif et la pire baisse de QQQ. Le jeu de données ne contient aucune composition de fonds ; à ma connaissance, non vérifiée ici, Tesla fait partie de l'indice que ce fonds réplique. |

Les parts de trajectoires sont des scénarios tirés de cinq années observées, pas des probabilités de l'avenir ; l'erreur de simulation est d'environ 0,6 point, l'erreur qui compte vient de l'échantillon (261 semaines, un seul épisode de forte baisse). Elles sont calculées en valorisation hebdomadaire et héritent de cette convention : en valorisation quotidienne, elles seraient plus élevées.

## 2. Ce qui a été examiné

- **Lu** : le mandat initial (`docs/cadrage/02`), la vision d'origine et ses idées O01 à O20 (`docs/cadrage/01` et sa version révisée), le mandat révisé du 15 novembre, le dossier de recherche « Réutiliser des briques éprouvées, prouver leur assemblage » (hors dépôt : synthèse, directions, expériences, objections), le journal des décisions, les notes R01 à R06, le cœur du code.
- **Inspecté** : six dossiers produits ce matin par l'agent réel sur Amazon Bedrock et deux dossiers du workflow fixe (`runs/`) ; l'application lancée et essayée.
- **Exécuté** : le calcul exploratoire, hors produit.
- **Contre-vérifié** : sept lecteurs indépendants puis trois vérificateurs chargés de réfuter leurs constats ; trois conceptions indépendantes du contrat, notées par deux juges. Tous en lecture seule.

## 3. Intention et réalité, rôle par rôle

| Rôle | Ce que tu demandes | Ce que le produit fait | Preuve |
|---|---|---|---|
| **Agent 0** — qualification et formalisation | Comprendre la demande, caractériser le profil, expliciter objectifs et contraintes, détecter les inconnues, formuler les questions de recherche | Recopie la fiche du profil depuis l'énoncé. Trois inconnues identiques pour tous les profils sont codées en dur. Le portefeuille fictif, la part de 10 %, le seuil de 15 %, le plafond de 50 %, l'alternative et le panier sont écrits d'avance. Aucun problème formalisé, aucune question de recherche. La question « décisive » est affichée ; la seule façon d'y répondre est un curseur prérempli à 15 %. | `tools.py:96-125` ; `config/scenarios.toml:10-14, 26` ; `app.py:196` |
| **Agent 1** — recherche et revue de littérature | Chercher connaissances et méthodes, examiner leurs conditions d'application, constituer un dossier de preuves | Rien à l'exécution. Le registre prévoit des sources documentaires (préfixe `S`) ; aucune n'est jamais inscrite. Aucune méthode n'est justifiée par une source. | `evidence.py:23` ; aucun `add("S"` dans `src/` |
| **Agent 2** — analyse et résolution | Analyse financière et computationnelle, comparaison de solutions, conclusion conditionnelle défendue | Statistiques descriptives : rendement composé, volatilité, pire baisse, rendement 2022, pire fenêtre, parts de la variance, corrélation ; deux balayages sur grille. Une seule trajectoire, aucune incertitude, aucune méthode comparée à une référence. Dépendances : `numpy`, `pandas`. La conclusion n'est défendue contre aucune objection. | `analytics.py` ; `tools.py:129-285` ; `pyproject.toml` |
| **Agent 3** — restitution et interaction | Présenter fidèlement au bon niveau, permettre l'examen, organiser la révision | Dossier HTML soigné : chaque valeur renvoie à son calcul. Même texte pour tous les lecteurs. Aucune question possible sur un dossier. Une révision relance tout depuis le début ; l'historique de séance permet de rouvrir un dossier précédent, mais aucune demande ne s'appuie sur le travail d'une autre. | `report.py` ; `app.py:81-118` |
| **Organisation** | Fonctions réellement exécutées par des agents outillés, avec documents de travail | Un seul agent : une conversation Bedrock, dix outils, une consigne de 4 lignes de méthode pour 15 lignes de règles de rédaction. Aucun document intermédiaire. | `agent.py:98-127, 191-240` |

## 4. Classement demandé

**Fonctions opérationnelles.** Conversion en dollars canadiens et alignement hebdomadaire des calendriers, testés. Calculs descriptifs et balayages. Registre de preuves : chaque valeur a un identifiant, une unité, un statut, une origine. Vérificateur : il refuse une référence inconnue, une grandeur en lettres, un comparatif d'une liste fermée, et un chiffre écrit à la main — sauf si ce chiffre coïncide avec un nombre du libellé ou de la période d'un enregistrement cité, auquel cas il passe. Agent réel sur Bedrock, avec l'identifiant de chaque appel. Choix d'outils par le modèle sur les demandes libres. Abstention observée : titre absent de l'univers, absence de données ESG. Relecture hors ligne d'un dossier enregistré : elle recontrôle la cohérence du texte avec le registre enregistré, sans recalculer les valeurs. Recalcul réel quand on déplace un curseur en mode de référence.

**Simulations d'interface.**
- « Contrôle conforme » et « aucun chiffre ni sens de comparaison n'est saisi à la main » (`report.py:502`, `app.py:270`) : vrai pour les chiffres, muet sur le sens. L'affirmation A-013 est passée ; l'audit a injecté quinze affirmations fautives qui passent le vérificateur sans signalement.
- Le titre du dossier et celui des tableaux, écrits librement par le modèle, échappent au vérificateur : un titre comme « Tesla perdra 50 % en 2027 » passe (`dossier.py:53-73`).
- Le vérificateur ne protège pas la règle première du projet. « Il faut vendre Tesla immédiatement » et « Tesla garantit un rendement de 8 % par an » passent, avec le statut « mesuré » ; seules la consigne du modèle et une ligne fixe d'en-tête rappellent qu'il n'y a ni conseil ni prévision.
- Les statuts « mesuré », « hypothèse », « déclaré » sont des étiquettes posées par le code, pas une qualité de preuve : une valeur calculée sur une seule trajectoire est « mesurée » au même titre qu'une valeur robuste, et le statut d'un paragraphe s'affiche aussi sur ses phrases de jugement. Sur une demande libre, les hypothèses posées par le modèle sont attribuées au « scénario de démonstration ».
- Les rubriques « Tensions avec le profil », « Information décisive manquante », « Ce qui ferait changer la conclusion » ont le nom d'une analyse d'adéquation ; leur contenu est un texte du modèle ou un gabarit.
- Le « calcul de référence » est un gabarit de phrases fixes : en choisissant le Bitcoin et l'or dans l'application, on obtient un dossier titré « Robert… est tenté par Tesla », qui qualifie l'or de « FNB diversifié de croissance », avec contrôle conforme.
- Régler le curseur « Baisse maximale supportable » ne vaut pas réponse : le dossier affiche toujours « Capacité de perte : non renseignée ». En mode agent, une question de clarification est impossible par construction : si le modèle répond par du texte au lieu de soumettre un dossier, l'exécution échoue (`agent.py:206-207, 235-236`).
- Dans l'application, en mode agent avec une demande libre, les curseurs restent affichés mais toutes les hypothèses sont retirées avant l'appel (`app.py:95-97`), et le résultat peut encore annoncer « Hypothèses modifiées ». Le mode ouvert par défaut n'appelle aucun modèle.

**Réponses simplement générées.** Plus d'une phrase sur quatre des dossiers de l'agent ne porte aucune référence (62 sur 227, hors cadre). Exemples relevés dans les dossiers marqués conformes :
- « L'or ne change pas la structure du risque », pour une part du risque des actions qui passe de 59,1 % à 53,2 % (`robert-libre-or`, A-010).
- « Une part d'or allant jusqu'à 30 %, qui est la part maximale respectant le seuil » : 30 % est la borne de la grille de calcul, pas un résultat (`robert-libre-or`, A-011). La cause est dans le code : l'outil ne dit pas au modèle qu'il a atteint sa borne (`tools.py:217-220`).
- « Tesla diversifie donc peu le risque d'actions déjà détenu », tiré d'une corrélation de 0,51 ; « un seul cycle de la crypto », tiré de la mémoire du modèle.
- En demande libre, le modèle pose lui-même les paramètres décisifs. Le seuil de 15 % y réapparaît parce que la description de l'outil le donne en exemple (`agent.py:67`, ajouté par moi ce matin).

Dans le workflow fixe, ce sont des phrases écrites d'avance par les développeurs, où seuls les chiffres changent. Un tiers des jetons Bedrock des six dossiers de l'agent (91 796 sur 280 030) sert aux passes de correction de forme.

**Fonctions absentes.** Formalisation du problème. Questions de recherche. Recherche de méthodes et de sources. Dossier de preuves. Conditions d'application d'une méthode. Toute méthode au-delà du descriptif (pertes extrêmes, rééchantillonnage, covariance contractée, allocation sous contraintes, probabilité d'objectif). Mesure de l'incertitude. Comparaison systématique à des références simples. Objection éprouvée. Restitution adaptée au niveau. Dialogue et révision partielle. Mémoire. Scénario de référence pour Mateo et toute donnée ESG. Usage des séries macroéconomiques et des opérations sur titres (chargeables, jamais appelées : `data.py:44, 52`) : ni taux sans risque, ni inflation, alors que l'objectif de Robert est de préserver son capital. Tout service AWS autre que l'inférence. Mesure de l'apport de l'agent.

À porter au crédit de l'existant : cinq des neuf objets proposés par le cadrage existent en substance (faits de profil, instantané des données, exécution tracée, affirmation, explication). Manquent la demande structurée, le problème de décision, la question de recherche et la preuve documentaire : exactement le périmètre des agents 0 et 1.

## 5. Les décisions qui ont appauvri le projet

Le constat le plus net de l'audit : qualification, analyse et restitution subsistent, fondues et implicites dans une boucle unique ; la recherche et la confrontation n'existent sous aucune forme. Les décisions les plus lourdes n'ont jamais été consignées — disparition de la recherche, orchestrateur unique sans comparaison, qualification remplacée par des profils statiques. Par équité : le mandat du 14 novembre autorisait la fusion des rôles et un produit focalisé, mais à des conditions (recherche avant tout choix, comparaison d'architectures, démonstration que le choix sert mieux le problème) qui n'ont pas été remplies.

| Décision | Où elle est établie | Ce qu'elle a coûté |
|---|---|---|
| **Le cadrage a lui-même traduit la vision en « conclusions accompagnées de preuves »** et autorisé la fusion des agents | `docs/cadrage/01:47` (« point de départ fonctionnel… sa fusion ou son remplacement »), `01:184` (« fonctions à couvrir plutôt que nombre d'agents »), `01:382` (« orientation recommandée ») ; `docs/cadrage/02:153` (« Tu peux fusionner, répartir ou remplacer ces fonctions ») | L'architecture à quatre rôles est devenue facultative avant la première ligne de code. La session précédente a agi dans le mandat tel qu'il était écrit. |
| **D1 : choix de « l'enveloppe » sur un tableau de coches**, sans prototype comparatif | `docs/decisions.md:13-21` ; le mandat disait pourtant : « Ne la traite pas comme le choix final simplement parce qu'elle est décrite ici » (`02:366`) | Le produit est devenu la forme de la réponse (des chiffres traçables) plutôt que son fond. La profondeur promise « par B, puis C, puis D » (transparence des fonds, ESG, allocation robuste) n'a jamais été construite. |
| **Un orchestrateur unique par défaut** | `docs/technique.md:10` ; `docs/carte-questions.md:13` réduit la question à « agent outillé ou workflow fixe ? » ; le mandat demandait de comparer aussi une orchestration avec spécialistes (`02:315`) | Les quatre rôles n'ont jamais été essayés. La seule comparaison faite oppose l'agent unique à un script. |
| **Pas de méthode au-delà du balayage** | `docs/carte-questions.md:14` : « balayages à règle explicite… plutôt qu'un optimiseur » | L'analyse s'arrête à la description d'une trajectoire. |
| **Hypothèses décisives écrites à la main** | `config/scenarios.toml:10-14, 26, 44-53` | La conclusion de Robert dépend entièrement d'un seuil de 15 % que personne n'a justifié (section 1). Celle d'Amira (52,4 % du risque en technologie, contre un plafond de 50 %) devient 64,4 % ou 38,4 % selon que Tesla est rangée en technologie ou QQQ hors de ce groupe : le regroupement est écrit à la main. Sur ces scénarios, l'agent suit le workflow fixe à quelques appels près (`docs/comparaison-agent-workflow.md`). |
| **Une recherche mince, sans effet sur les calculs** | `research/R04:3` (« aucun texte intégral lu »), `R03:3` (« rapport partiel ») ; six notes sur AWS, les données ESG, l'adéquation, la fidélité des explications, la présentation, la facturation | Aucune note ne traite d'une méthode financière ; aucune méthode du produit ne vient d'une source. Le dossier de recherche approfondi (vingt-cinq fiches avec niveaux de lecture) est resté hors du dépôt. |
| **Données réduites aux prix** | `data.py:44, 52` jamais appelés ; aucun scénario pour Mateo | Le critère « données » (20 %) repose sur un seul fichier ; un profil de l'énoncé sur trois n'est pas traité. |
| **L'effort est allé à la forme** | D5 (`docs/decisions.md:59`), que j'ai prise ce matin : garde lexicale, accords, graphiques. Le même jour, j'ai retiré des prochaines actions la relecture des textes primaires (`docs/etat.md`). | La garde refuse des phrases vraies (« dépasse le plafond ») et laisse passer des phrases fausses ; ses passes de correction pèsent un tiers des jetons. Le calcul n'a reçu ni recherche ni méthode nouvelle depuis la première tranche. J'ai renforcé l'enveloppe au lieu de questionner son contenu. |
| **Le modèle ne voit que des identifiants et des valeurs formatées** | `tools.py:56-57`, `agent.py:130-133` : période, conventions, statut, dépendances et grilles sont retirés des résultats d'outil ; jamais consigné comme décision | Le modèle ne peut pas savoir qu'une valeur est une hypothèse, ni détecter un artefact comme la borne de grille : il ne peut que citer. La fonction d'analyse est bornée par construction. |
| **Des critères de réfutation qui ne peuvent pas échouer** | D5 se rouvre au-delà de « deux corrections par dossier » (`docs/decisions.md:71`), or la boucle n'en demande jamais plus de deux (`agent.py:28`). Le critère (b) de D1 est déclaré satisfait alors que cinq premiers jets sur six ont été refusés. La « lecture » du tableau comparatif dit généré est écrite en dur (`scripts/comparer_agent_workflow.py:67-72`). Ces trois textes sont de moi, ce matin. | Les garde-fous du journal des décisions n'en étaient pas. L'expérience prévue pour départager l'option retenue — la même demande sous deux profils — n'a jamais été faite : aucun des huit dossiers ne la contient. |
| **Le mandat révisé n'a pas été branché sur le travail** | Il n'existe que hors dépôt ; `CLAUDE.md:13` et `scripts/message-reprise.txt` renvoient au mandat du 14 novembre. Je l'ai lu ce matin et j'ai poursuivi l'ancien plan. | Aucune de ses demandes n'a été suivie : registre des ressources à quatre états, recherche web à brancher, critique chargée de réfuter, choix des modèles sur observation. |

À décharge. Une partie de l'effort reproché répondait à des demandes explicites (présentation, facturation sur AWS). La position « un agent outillé, des rôles seulement s'ils apportent un gain mesuré » est aussi celle du cadrage et du dossier de recherche hors dépôt, et le cas officiel encourage une approche simple. Le reproche fondé n'est pas d'avoir choisi : c'est de n'avoir ni soumis ces choix provisoires à validation, ni rouvert ceux dont les conditions de réouverture étaient réunies — le scénario d'Amira demandait une allocation dès le premier jour.

Décisions qui restent bonnes : les conventions de calcul (D3), le registre et le principe « le modèle ne calcule pas », l'abstention plutôt que l'invention, la franchise de la documentation technique sur ce que le contrôle ne voit pas.

## 6. Conserver, reprendre, remplacer

**Conserver.** Dans `evidence.py` : le registre typé, les références, les comparaisons calculées, l'héritage des hypothèses ; ils s'appliqueront au texte de chaque document de travail, et le préfixe `S` servira enfin aux sources. `analytics.py` et ses conventions testées. Les outils de `tools.py`, leur validation des entrées et leur traçage (`Session.call`), comme premières méthodes d'une bibliothèque fermée. Dans `agent.py` : l'appel Bedrock et son traçage (identifiants d'appel, jetons, latence), le renvoi des refus au modèle, les erreurs d'outil visibles ; et le client simulé des tests. `dossier.py`, `report.py`, la relecture hors ligne. La structure de l'application (serveur local, historique, erreurs lisibles). Les tests. L'agent unique et le workflow fixe, non comme produit mais comme témoins de comparaison.

**Reprendre.**
- La boucle de `run()`, où la consigne, la liste d'outils et l'outil de soumission sont en dur : à refaire en boucle paramétrée par rôle, qui conserve les messages et les jets refusés.
- Les résultats d'outil rendus au modèle : ils doivent porter période, conventions, statut et signalement des bornes.
- `profile_facts` : à refaire en profil structuré où chaque champ porte son origine et sa citation.
- `share_sweep` : il calcule déjà toute la courbe, n'en publie qu'un point et rend la borne de sa grille (30 %) comme une « part maximale ».
- La durée sous le sommet : quand le sommet n'est pas retrouvé, elle est tronquée à la fin de l'échantillon et inscrite « mesurée » (`analytics.py:110-111`) ; ce n'est qu'un minorant, et une comparaison calculée en a déjà tiré une conclusion fausse (`robert-libre-or`, A-008).
- Les conventions de D3 : la valorisation et le rééquilibrage hebdomadaires changent les conclusions (section 1) ; elles deviennent des hypothèses affichées et éprouvées.
- Le nombre de fenêtres sans chevauchement : partie entière d'une durée de 4,9993 ans divisée par l'horizon ; le dossier annonce quatre fenêtres d'un an là où cinq tiennent (`analytics.py:144, 152`).
- Les rubriques du dossier : à refaire en aide à la décision.
- Les curseurs : leurs valeurs initiales viendront de la fiche de qualification ou resteront vides.
- La garde lexicale de D5 : elle ne vaut que comme obligation de passer par les comparaisons calculées ; son périmètre doit s'accorder avec des documents qui parlent de dépassements.
- Les séries de taux de `macro_rates.csv` : pour l'hypothèse de rendement au taux sans risque.

**Remplacer.** `config/scenarios.toml` comme source des hypothèses décisives. La conclusion ponctuelle « seuil de 15 %, part de 9 % ». La conversation unique où demande, hypothèses et résultats se mélangent. La mention globale « contrôle conforme », par un état de contrôle par document qui dit ce qu'il ne voit pas. La justification « pourquoi pas plus d'agents » et la conclusion de D1. `runs/` ignoré par git comme seule trace des exécutions réelles.

## 7. Contrat de refonte

Ce que le concours en dit, vérifié dans les pièces : l'architecture et le nombre d'agents sont libres ; « la sophistication technique et le nombre d'agents ne sont pas des fins en soi » (cas officiel) ; « Donnez un rôle clair aux agents. Évitez la complexité décorative. » et « Pourquoi cet agent existe-t-il et quelle valeur apporte-t-il ? » (présentation aux participants). Quatre rôles sont donc permis, à une condition que le contrat reprend à son compte : chacun doit prouver son apport (section 7.4). Les pièces ne demandent pas de revue de littérature ; elles demandent de justifier les méthodes et de documenter chaque source. L'agent 1 se défend devant le jury par là.

### 7.1 Reformulation

AlphaForge traite la demande d'une personne fictive comme un mandat confié à un petit bureau d'étude. Quatre rôles se succèdent ; chacun est un agent outillé sur Amazon Bedrock, et chacun remet un document de travail contrôlé que le suivant est obligé d'utiliser. La conclusion n'est plus un point (« 9 % ») mais une fonction de ce qu'on ignore (« si votre capacité de perte est de tant, voici ce que les calculs montrent »), donnée avec son incertitude et les objections qu'elle a subies. La personne peut ouvrir chaque document, contester, répondre à la question décisive ; la révision ne refait que ce qui dépend de sa réponse. Le modèle comprend, choisit, interroge, conteste et rédige ; le code calcule, contrôle chaque document, tient les versions et rejoue les calculs. Tout reste une simulation sur profils fictifs, sans transaction ni conseil personnalisé.

### 7.2 Les rôles

| Rôle | Document remis | Ce que décide le modèle | Ce que fait le code | Le rôle a travaillé si… |
|---|---|---|---|---|
| **Agent 0** — qualification et formalisation | Fiche de qualification : décision à éclairer (catalogue fermé), profil en six éléments où chaque champ porte sa valeur ou « inconnu », son origine et la citation qui le fonde, contradictions, inconnues classées, questions de recherche, questions à la personne | Comprendre la phrase, rattacher chaque champ à sa citation, formuler les questions | Contrôle que chaque citation figure mot pour mot dans la demande ou l'énoncé ; règles de contradiction ; refus de toute valeur que la personne n'a pas dite | une part de 10 % que Robert n'a pas dite est refusée ; un dossier complet ne déclenche aucune question |
| **Agent 1** — recherche et revue de littérature | Dossier de preuves : une réponse par question de recherche (étayée, partiellement étayée, sans preuve), passages cités avec leur niveau de lecture réel, conditions d'application testées sur les données du cas, plan des méthodes autorisées, écartées, imposées | Choisir les fiches, sélectionner le passage, juger la transposition au cas, conclure sur chaque méthode | Recherche dans la bibliothèque de fiches ; contrôle des citations ; recopie du niveau de lecture ; exécution des tests de condition | le plan change quand la demande change ; retirer une fiche change le plan |
| **Agent 2** — analyse et résolution | Note d'analyse : formulation choisie dans une bibliothèque fermée, options comparées dont « ne rien changer », calculs, conclusion conditionnelle, ce qui la ferait changer | Choisir la formulation, les options et les variantes ; rédiger la conclusion | Tous les nombres ; refus d'une méthode absente du plan ; rejeu des calculs | chaque calcul renvoie à une méthode du plan ; le rejeu hors ligne retrouve chaque valeur |
| **Contradicteur outillé** (spécialiste rattaché à l'agent 2) | Registre des objections : objection, conclusion visée, test, résultat, verdict | Choisir les objections et le test qui les départage | Exécuter les tests ; rendre le verdict selon un critère écrit avant le calcul ; une batterie de tests fixe tourne d'office | il trouve ce que la batterie fixe ne trouve pas |
| **Agent 3** — restitution et interaction | Restitution : décision à prendre, options côte à côte, ce qu'on ignore, ce qui ferait basculer, réserves, limites, question décisive avec son enjeu ; journal de révision | L'ordre, les mots, le niveau de détail ; reconnaître ce qu'une réaction modifie | Aucun enregistrement nouveau ; refus d'une restitution qui omet une ligne de la conclusion ; mêmes faits quel que soit le niveau | une restitution qui tait une ligne, favorable ou défavorable, est refusée |

Deux modules sont du code, sans modèle, et sont nommés comme tels : la **qualification des données** (empreintes, fenêtre, conventions, limites reliées chacune à sa conséquence) et le **greffier** (enchaînement, outils autorisés par rôle, versions, dépendances, rejeu).

### 7.3 Règles

1. Un rôle est un contrat : des entrées nommées, des outils autorisés, un document, un contrôle. Pas de document contrôlé, pas de rôle.
2. Une inconnue reste une inconnue : on la demande si le calcul en a besoin, on la balaie si elle est décisive, on s'abstient si aucune donnée ne l'éclaire. Aucune valeur par défaut silencieuse, ni dans la configuration, ni dans la description d'un outil.
3. Les nombres viennent du code ; le modèle choisit parmi des formulations validées, il n'en écrit pas.
4. Une méthode entre dans l'analyse avec sa condition d'application testée et une référence simple à côté. Si aucune source lue ne la fonde, elle est affichée « méthode non qualifiée par la littérature lue ».
5. Aucune conclusion ne repose sur un rendement moyen passé ; toute part de trajectoires est donnée sous plusieurs hypothèses de rendement.
6. La confrontation passe par un outil : chaque objection désigne un test, et le critère de verdict est écrit avant le calcul.
7. La restitution ne crée aucun fait et ne peut taire aucune ligne de la conclusion, qu'elle aille dans le sens de la demande ou contre elle. Une phrase sans référence est affichée « interprétation, non vérifiée ».
8. Chaque source est affichée comme « passage de notre fiche de lecture », avec son niveau de lecture réel.
9. Une révision ne refait que ce qui dépend du champ modifié ; les autres documents gardent leur version.
10. Tout se rejoue sans AWS, et rejouer veut dire recalculer chaque nombre ; AWS exécute les rôles et conserve l'historique des documents.
11. Les titres sont contrôlés comme le reste, et une formulation d'ordre ou de prévision (« il faut vendre », « garantit ») est refusée dans tout document.

### 7.4 Ce qui prouve que les rôles ne sont pas un décor

- **Outils disjoints, imposés par le code** : l'agent 0 n'a aucun outil de marché, l'agent 1 ne voit que les fiches et les tests de condition, l'agent 2 ne peut appeler que les méthodes du plan, l'agent 3 n'a ni calcul ni fiche. Tout appel hors rôle est refusé et journalisé.
- **Contextes séparés** : chaque rôle ouvre une conversation neuve dont les seules entrées sont des documents validés, avec leur empreinte ; ses identifiants d'appel Bedrock lui sont propres.
- **Essais de substitution** : on modifie un seul document et on observe l'aval.
- **Bras de comparaison équitable** : un agent unique doté de la même bibliothèque, des mêmes règles et des mêmes fiches, produisant les mêmes documents dans une seule conversation. Le résultat est publié dans les deux sens. S'il fait aussi bien, aucune fusion n'aura lieu sans l'accord du porteur.

### 7.5 Ce que le contrat ne promet pas

Une recherche ouverte sur le web pendant la demande. Une allocation optimisée sur les 31 actifs. Des données ESG. Une mesure de la compréhension auprès de personnes. Un contrôle du sens des phrases par un second modèle. Une conformité réglementaire : la structure des régulateurs canadiens sert de cadre de qualité, AlphaForge n'est pas un inscrit. Des probabilités de l'avenir.

## 8. L'expérience visée : l'étude de Robert

Tous les chiffres sont exploratoires. Pour Robert, les calculs ont précédé le dossier de preuves : la propriété « le plan précède les résultats » ne se démontrera que sur une demande neuve.

**Demande.** « J'aimerais consacrer une partie de mon portefeuille à Tesla ; on en parle partout. » Aucun curseur n'est prérempli.

**1. Agent 0 — fiche de qualification.**
- Décision à éclairer : ajout d'un titre à un portefeuille existant.
- Part envisagée : inconnue (citation : « une partie »). Motif déclaré : « on en parle partout ». Demande à l'initiative de la personne.
- Profil : objectif de préservation du capital, horizon de 3 à 5 ans, tolérance « faible à modéré » non chiffrée (déclarés, énoncé page 7) ; capacité de perte, liquidité, patrimoine : inconnus.
- Objectif formalisé : « préserver le capital » peut se mesurer de deux façons, la baisse subie en cours de route et la perte à l'échéance. Laquelle compte dépend des retraits prévus avant l'échéance, inconnus : les deux seront calculées.
- Règles déclenchées : capacité inconnue, donc profil de risque opérant indéterminé ; demande venant de la personne et s'écartant de ses préférences déclarées ; préférence pour « les placements dont il comprend bien le modèle d'affaires » contre le motif invoqué.
- Inconnues : portefeuille de départ, nécessaire au calcul, donc demandé ; capacité de perte et retraits prévus, décisifs, donc balayés ; valorisation de Tesla, aucune donnée, donc abstention.
- Questions de recherche : que doit faire l'analyse quand la personne demande elle-même une opération qui s'écarte de son profil ? Comment mesurer le risque d'ajouter un titre isolé sur cet horizon avec cet échantillon ? Peut-on créditer Tesla d'un rendement espéré tiré de son historique ? Comment présenter le résultat sans nourrir un excès de confiance ? Que les données ne peuvent-elles pas dire ?
- Une seule question posée : la composition du portefeuille. Robert retient le portefeuille fictif proposé, inscrit comme « supposé, retenu par la personne ».

**2. Agent 1 — dossier de preuves.**
- Demande à l'initiative de la personne : étayée. Passages de nos fiches de lecture : le profil retient « le plus bas des deux » entre tolérance et capacité ; noter que le client a dirigé l'opération « est insuffisant » (textes des régulateurs canadiens, lus par extraction automatique). Conséquence : ni acquiescer ni refuser ; montrer l'écart et des options bornées.
- Rendement espéré : question tranchée par un test. Erreur type du rendement moyen de Tesla : 24,9 points pour une moyenne de +22,7 %. La méthode « rendement espéré tiré de l'historique » est écartée ; toute simulation doit aussi être calculée sans ce rendement.
- Mesure du risque : partiellement étayée. Une seule fenêtre de trois ans sans chevauchement : la pire baisse historique ne suffit pas. Le rééchantillonnage par blocs est retenu en complément et affiché « méthode non qualifiée par la littérature lue ».
- Restitution : partiellement étayée, par des études menées en santé. Consignes : options côte à côte dans les mêmes unités, fourchettes, pas de tirages « vécus ».
- Ce que les données ne peuvent pas dire : la valorisation et l'actualité de Tesla ; le contenu des fonds indiciels ; tout horizon plus long que l'échantillon.

**3. Agent 2 — note d'analyse.** Formulation : part de Tesla de 0 à 30 %, le reste réduit au prorata ; options : ne rien changer, 5 %, 10 %, 20 % de Tesla, 10 % de QQQ ; capacité de perte balayée.

| Si la baisse supportable est de | Plus grande part de Tesla qui n'aurait pas franchi ce seuil sur les cinq ans observés |
|---|---|
| 12 % ou moins | aucune : le portefeuille actuel a lui-même connu −12,3 % ; la question précède Tesla |
| 13 % | 2 % |
| 15 % | 9 % |
| 17,5 % | 13 % |
| 20 % | 16 % |
| 25 % | 23 % |

Part des trajectoires de trois ans, selon l'hypothèse de rendement moyen (moyennes historiques / taux sans risque de 3,2 % pour tous les actifs / aucun rendement crédité) :

| Option | Baisse en route au-delà de 15 % | Valeur finale sous la valeur de départ |
|---|---|---|
| Ne rien changer | 5,6 % / 19,2 % / 35,4 % | 4,2 % / 22,9 % / 50,5 % |
| 5 % de Tesla | 10,1 % / 29,0 % / 45,2 % | 4,9 % / 26,3 % / 51,6 % |
| 10 % de Tesla | 20,9 % / 44,7 % / 60,3 % | 6,1 % / 30,6 % / 53,1 % |
| 20 % de Tesla | 64,5 % / 84,1 % / 89,1 % | 10,8 % / 38,6 % / 55,7 % |
| 10 % de QQQ | 10,7 % / 28,9 % / 43,9 % | 4,6 % / 26,0 % / 50,5 % |

Sur l'historique lui-même, aucune des 105 fenêtres glissantes de trois ans ne finit en perte, pour aucune option (une seule fenêtre sans chevauchement).

Conclusion conditionnelle. Ce qui tient sous toutes les hypothèses : à part égale, Tesla pèse plus que QQQ ; 10 % de Tesla multiplie par 1,7 à 3,7 la part des trajectoires qui franchissent 15 % en route ; 20 % de Tesla la porte au-delà d'une sur deux ; à l'échéance, l'écart entre les options est bien moindre. Ce qui dépend d'une hypothèse : le niveau du risque lui-même. Ce qui dépend de la personne : si elle doit retirer de l'argent en route, ou ne supporterait pas de voir une telle baisse, c'est la première colonne qui compte ; sinon, la seconde. Ce qu'aucun calcul ne donne : un rendement à mettre en face.

**4. Contradicteur — registre des objections.**
- « Le résultat dépend de la taille des blocs. » Test : blocs de 4, 13 et 26 semaines. Résultat pour 10 % de Tesla : 23,1 %, 20,9 %, 21,3 %. Verdict : la conclusion tient.
- « Les trajectoires créditent Tesla de son rendement passé. » Test : Tesla seule ramenée à la moyenne du portefeuille. Résultat : 20,9 % devient 27,6 %. Verdict : la conclusion est amendée, les fourchettes sont affichées.
- « Neuf pour cent n'est sûr que sur la trajectoire observée. » Test : rééchantillonnage à 9 %. Résultat : 17,7 % à 57,0 %. Verdict : la borne de 9 % ne peut pas être dite « compatible » sans réserve.
- « À trois ans, aucune fenêtre observée ne finit en perte, même avec 20 % de Tesla. » Test : part des trajectoires finissant sous leur valeur de départ. Résultat : avec 10 % de Tesla, 6,1 % à 53,1 %, contre 4,2 % à 50,5 % sans. Verdict : la conclusion est amendée — le surcroît de risque de Tesla porte surtout sur le parcours, peu sur l'arrivée.
- « La pire baisse n'est vue que le vendredi. » Test : valorisation quotidienne. Résultat : −17,5 % au lieu de −15,3 % avec 10 % de Tesla ; la borne de 9 % devient 6 %. Verdict : la conclusion change — les seuils se lisent en valorisation quotidienne.
- « Le rendement du portefeuille monte avec Tesla. » Test : achat-conservation, sans rééquilibrage. Résultat : +8,4 %, +8,1 %, +7,8 % pour 0, 10 et 20 % de Tesla. Verdict : la conclusion change — la hausse affichée venait du rééquilibrage hebdomadaire sans frais.
- « Les perspectives de Tesla peuvent justifier le risque. » Non testable : ni fondamentaux ni nouvelles dans les données. Inscrite dans les limites.

**5. Agent 3 — restitution.** Pour une personne d'expérience avancée : la décision à prendre (« quelle part de Tesla, s'il y en a une, reste compatible avec la baisse que vous pouvez traverser avant votre retraite ? »), les cinq options côte à côte, la table de bascule, les réserves du contradicteur, les limites. Chaque valeur renvoie à son calcul, chaque source à son passage et à son niveau de lecture. Puis les deux questions décisives, avec leur enjeu : « Quelle baisse de votre portefeuille pourriez-vous traverser sans retarder votre retraite ? Selon votre réponse, la part va de 0 % à 23 %. » et « Prévoyez-vous de retirer de l'argent avant trois ans ? Selon votre réponse, c'est la baisse en route ou la perte à l'échéance qui compte. »

**6. Révision.** Robert répond : « 20 %, pas davantage. »
- Fiche de qualification : refaite, un champ (capacité de perte : seuil déclaré, sous réserve — revenu, liquidités et patrimoine restent inconnus).
- Dossier de preuves : conservé, même version, même empreinte. L'agent 1 n'est pas rappelé.
- Note d'analyse : la table historique est relue (16 %) ; les trajectoires conservées sont relues au seuil de 20 % : à 16 % de Tesla, 16,1 % à 53,9 % d'entre elles le franchissent, contre 0,9 % à 15,1 % sans Tesla.
- Registre des objections : rejoué au nouveau seuil. Restitution : refaite, ouverte sur « Ce qui a changé ».
- Une nouvelle question apparaît : la baisse que Robert accepterait de voir sans vendre, puisque le profil retient la plus basse des deux.

S'il avait répondu « 12 % », l'étude aurait changé de sujet : le portefeuille actuel a déjà connu 12,3 %, et sur trois ans 18,7 % à 52,4 % de ses trajectoires franchissent ce seuil sans Tesla.

**7. Contrôle par un tiers.** Une commande rejoue l'étude enregistrée sans AWS, repasse les contrôles de chaque document et recalcule chaque nombre. Un tableau généré montre, par rôle, les outils appelés, les enregistrements créés et les identifiants d'appel Bedrock.

## 9. Réalisme

Nous sommes le 15 novembre ; le dépôt du code est attendu ce soir à 23 h 59, le compte AWS ferme lundi à 13 h 59.

- **Avant toute refonte, un filet de sécurité** : commiter et étiqueter l'état actuel, le pousser sur un dépôt distant, verser les dossiers réels de l'agent dans un dossier versionné. Aujourd'hui, il y a un seul commit, dix fichiers modifiés non commités, aucune copie hors de cette machine, et la commande `rendre` réécrit en place les dossiers qui servent de preuve d'exécution AWS.
- **Travail estimé** : environ 14,5 heures pour la tranche complète sur Robert (calculs manquants ; documents, chaîne et rejeu ; un lot par rôle ; application ; preuve des rôles). Tenable seulement en parallèle, avec un chemin critique d'environ neuf heures. L'estimation est incertaine : cinq consignes sont à mettre au point avec un modèle dans la boucle.
- **Points de contrôle proposés** : à 15 h, la chaîne tourne avec le client simulé et l'agent 0 est vert sur Bedrock ; à 19 h 30, la chaîne réelle est verte deux fois de suite sur Robert, sinon dépôt de la version actuelle enrichie des nouveaux calculs, les rôles terminés étant livrés comme expérimentaux et étiquetés ; gel à 22 h 30.
- **Ordre de coupe en cas de retard** : miroir S3, frise en direct, contradicteur piloté par le modèle. Ne se coupent pas : les quatre documents contrôlés, le journal de révision, le rejeu.
- **Lundi matin, sans changement de code** : vidéo en direct sur Bedrock, mesures de stabilité sur trois répétitions, essais de substitution, bras de comparaison équitable, export hors du compte.
- **Non construit, annoncé comme limite** : la liste de la section 7.5, plus le traitement complet d'Amira et de Mateo (la même phrase sous le profil d'Amira sert de contraste ; la demande ESG de Mateo donne une abstention expliquée).

Risques principaux : le temps ; la fiabilité de cinq conversations soumises à des contrôles stricts ; la durée d'une étude (plusieurs fois celle de l'agent unique) ; le budget du compte d'atelier, partagé entre le développement et les exécutions ; des citations lues par extraction automatique, à relire dans les textes d'origine avant toute diffusion.

## 10. Décisions de direction

1. **Périmètre de ce soir et règle d'arrêt.** Robert en entier, Amira en contraste, Mateo en abstention, avec la règle d'arrêt de 19 h 30 — sachant qu'elle peut conduire à déposer un produit à agent unique enrichi des nouveaux calculs. *Recommandation : oui. Sans règle d'arrêt, le risque est de n'avoir rien de neuf à l'écran à 23 h 59.*
2. **Nature de la recherche de l'agent 1.** Une bibliothèque de fiches qualifiées tirée du dossier de recherche du porteur, versée au dépôt, avec tests de conditions sur le cas — sans recherche ouverte pendant la demande. Conséquence : les sources sont affichées comme passages de nos fiches de lecture, et la méthode centrale reste « non qualifiée par la littérature lue » tant qu'une lecture ciblée n'a pas été faite. *Recommandation : oui. C'est la forme que décrivait la vision d'origine (recherche large au développement, connaissances qualifiées à l'usage) ; la recherche web en direct demande une ressource AWS jamais essayée sur le compte.*
3. **Forme de la confrontation.** Un contradicteur outillé rattaché à l'agent 2, sans débat entre agents. Et, en cas de retard, le droit ou non de le réduire à une batterie de tests exécutée par le code, c'est-à-dire de ne plus faire tenir cette fonction par un agent dans la version déposée. *Recommandation : contradicteur outillé ; la réduction à une batterie fixe est une suppression de rôle, donc soumise à accord.*
4. **Ce que le produit a le droit de conclure.** Une conclusion conditionnelle neutre, qui montre les fréquences sans fixer de seuil acceptable à la place de la personne ; ou un avis explicite de convenance (« ne convient pas tel quel »), plus parlant pour un jury de banque, plus proche d'un conseil. *Recommandation : conclusion conditionnelle neutre, cohérente avec le cadre de simulation sans conseil personnalisé.*
5. **Fin des scénarios écrits d'avance.** Le produit s'arrête et demande le portefeuille de départ et la capacité de perte ; ou il garde des valeurs de démonstration, affichées et modifiables. *Recommandation : il s'arrête et demande, en proposant un portefeuille fictif que la personne peut retenir.*

Restent ouvertes depuis ce matin, et la première bloque le dépôt de ce soir : le dépôt GitHub (emplacement, visibilité, ce qui peut y être versé) ; l'accord pour créer un compartiment S3 versionné et activer le journal des invocations Bedrock ; la route d'inférence de la seconde session de développement.

Après validation, le nouveau régime devra être écrit dans le dépôt : `CLAUDE.md` et `scripts/message-reprise.txt` renvoient encore toute session reprise au mandat du 14 novembre, donc à « Tu peux fusionner ». `CLAUDE.md` est le fichier de consignes du porteur : je ne le modifie pas sans son accord.
