# AlphaForge — documentation technique du produit fusionné

## Objet et périmètre vérifié

AlphaForge fournit un second avis éducatif sur une demande d’investissement. Il vérifie la cohérence de cette demande avec les informations déclarées, compare deux allocations historiques et produit un dossier explicable. Il ne réalise aucune transaction et ne prévoit pas les pertes futures. Le porteur a validé les poids fictifs de Robert, Amira et Mateo ainsi que l’attribution K5 et sa monotonie conditionnelle.

Le produit fusionne des composants existants : parcours et autorité de décision de C ; moteur historique de B ; ajout proportionnel et collecte des preuves Converse de A. Les archives restent inchangées. [Provenance et empreintes](../implementations/REFERENCES.md), [contrôle des originaux](fusion/preuves/tranche4/controle-origines.json).

## Méthodes et justification

L’ordre est déterministe : Profileur → Contrôle données → Analyste → Sceptique → Gardien → Rédacteur. Le Profileur peut utiliser Nova 2 Lite pour structurer les mots de la personne, qui relit les champs avant analyse. Le Sceptique utilise Sonnet 5 et un catalogue borné de vérifications ; les recalculs sont faits en code. Le Gardien applique les règles et retient le pire niveau. Le Rédacteur utilise Sonnet 5 pour expliquer le résultat.

Le catalogue fermé permet de relier chaque objection à une mesure vérifiable. Il ne remplace pas une recherche documentaire ouverte. Les modèles sont appelés par Amazon Bedrock Converse, avec le profil `alphaforge`, en `us-east-1`. L’intégrateur Astra utilise une route distincte ; il n’est pas un agent du produit.

Le portefeuille après suit `blend` de A : les poids existants sont réduits proportionnellement, puis la part demandée est ajoutée au titre. La comparaison K3 envoie les deux allocations à un même appel du moteur B. Le montant doit être compatible avec l’épargne, les poids doivent former une allocation valide. Une liste de titres sans poids signifie une équipondération explicitement hypothétique.

K5 utilise la pire baisse du portefeuille après pour la règle de perte supportable. La formule de seuil `5 + 0,35 × score` est conservée. Un dépassement déjà présent avant, non aggravé par la demande, ne lui est pas attribué comme nouveau rouge. Ces barèmes et cette attribution sont des choix d’équipe, pas des résultats empiriquement validés. `ALPHAFORGE_CAPACITE=approximation` conserve l’ancien calcul supposant le reste de l’épargne stable.

La recherche du plus petit ajustement parcourt les montants au pas existant de 100 CAD, par distance croissante, vers le bas et le haut. Aucune dichotomie ne suppose une monotonie globale. La grille conserve chaque verdict exact ; un montant supérieur peut améliorer le verdict d’un actif diversifiant. Le texte décrit le respect de la règle sans conseiller de placer plus. Les curseurs explorent la grille jusqu’au montant demandé ; un ajustement au-delà apparaît dans les options. La fiche conseiller conserve la demande initiale.

## Données et traitements

Jeu fourni par les organisateurs : 31 actifs, 2021-11-12 → 2026-11-12. Prix ajustés Yahoo Finance via yfinance ; change USD/CAD Banque du Canada. Les séries macro et FRED fournies ne participent pas au verdict. Secteurs lus depuis l’univers, sans analyse des expositions sous-jacentes des FNB.

- C calcule les mesures du titre seul sur son calendrier de cotation ; volatilité des rendements log, annualisation √252 ou √365. Les corrélations utilisent les rendements hebdomadaires.
- B calcule les deux portefeuilles sur 1 228 séances communes, en CAD, achat-conservation sans rééquilibrage. Volatilité des rendements simples, annualisation selon le nombre d’intervalles et la durée observée. Le change utilisé est du jour ou antérieur, avec âge maximal de sept jours.
- Les cryptoactifs sont échantillonnés aux séances communes de B. Les mouvements entre observations, dont les fins de semaine, ne sont pas intégralement capturés par la pire baisse K3.
- Les unités sont converties une fois à la frontière des modules. Les deux bras et leur écart ne mélangent jamais C et B. TSLA seul donne −70,9 % chez C et −69,805333 % sur la grille B ; ces valeurs décrivent des conventions distinctes.

Les contrôles vérifient présence, doublons, positivité, couverture, trous, variations et devise. Une donnée essentielle absente donne un état indéterminé avec question, jamais une valeur inventée. Les méthodes, limites et conditions de données sont détaillées dans [la fiche de données](donnees.md) et [le registre généré](sources.md).

## Mécanisme d’explication : un exemple complet

[Robert, dossier réel de réception](fusion/preuves/tranche4/robert-bedrock.json) : 80 000 CAD de TSLA sur 400 000 CAD, retrait à quatre ans. Le verdict est incohérent ; la règle de perte supportable est orange. La comparaison mesure −14,256677 % avant et −20,595922 % après, avec un écart de −6,339245 points et le sens `aggrave`.

Le champ `comparaison.faits.apres_pire_chute` renvoie à F-23. Ce fait porte sa valeur, son type SCENARIO, la source « Jeu de départ AlphaForge et moteur historique B », une méthode nommant historique-B, la fenêtre et les séances. Ses références renvoient notamment aux données de prix/change et à `moteur-historique-b` dans le registre. La règle `capacite` cite les faits des deux bras, de l’écart et des seuils. La phrase de comparaison cite les mêmes faits et prend le sens déjà calculé dans K3. Les nombres du composant React ouvrent le tiroir de faits existant.

La trace donne les rôles et durées. K6 conserve pour chaque appel le modèle, l’identifiant AWS, les jetons, la latence, la fin d’appel et l’état de configuration du garde-fou ; aucun contenu de requête n’entre dans ce journal de métadonnées. Exemple réel du Rédacteur de Robert : `d64e5735-94df-4189-a1ca-f42a900d95d3`, 12 919 jetons d’entrée, 649 de sortie, 7 645 ms. Le dossier final relie les traces aux indices K6.

Le contrôle d’ancrage existant refuse les nombres nouveaux, faits inconnus, fausses citations, formulations de conseil et contradictions de verdict. L’essai fautif « −6,34 points », nouvel arrondi de l’écart, est refusé ; les champs K3 exacts sont acceptés. Deux essais au plus, puis retour au gabarit. Bedrock Guardrails ajoute une vérification du Rédacteur sourcée par le dossier ; il ne remplace pas les contrôles en code. Les limites demeurent écrites par le code.

Robert sans date de retrait reste avec ajustement, mais une question placée en premier indique qu’un retrait à l’horizon déclaré ferait passer à incohérent. La date reste absente ; un fait HYPOTHESE expose le recalcul qui rend la question décisive.

## Validations et limites pratiques

[Réception et sorties](fusion/preuves/tranche4/README.md) : 344 tests Python réussis, contre 201 au socle ; aucun test supprimé. Les fusions intermédiaires passent 313 puis 332 tests. Les seules modifications des références T4 portent sur les textes « pourquoi » et « limites » ; verdicts, règles, faits, options, grilles et K3 restent identiques à T2.

Les dix cas couvrent les trois personas, données manquantes, demande impossible, GameStop hors univers, modifications successives, chaîne de preuve et absence de SDK/identifiants AWS. Avec de vrais appels Bedrock, les cinq objets métier sont égaux objet à objet au mode hors ligne pour Robert, Amira et Mateo. Chaque dossier a trois appels : 12,631 / 12,845 / 12,564 secondes. Avec contexte K3 et Guardrail, la consommation atteint 15 718 à 16 932 jetons ; le coût n’est donc pas resté égal à l’objectif initial d’environ 8 000 jetons. Robert public confirme cette limite : 20,583202 s, quatre appels et 30 587 jetons. Les deux textes du Rédacteur sont refusés (contradiction de verdict puis citation non textuelle) ; le gabarit prévu est restitué. Les décisions et K3 restent identiques, et la copie S3 égale au dossier reçu.

Trois analyses hors ligne par cas, caches applicatifs vidés : maximum 613,476 ms. Imports et cache du système de fichiers restent chauds ; ce n’est pas une mesure de démarrage complet de processus. Le rendu React statique vérifie les dossiers, les champs absents, les identifiants et la non-monotonie. **Les parcours n’ont pas été inspectés visuellement dans un navigateur : l’accès intégré échoue et Computer Use refuse Chrome.** Aucun clic de preuve ni mise en page mobile n’est déclaré validé. Les instructions Windows sont documentées, non exécutées pendant cette réception macOS.

La présence de cinq ans de données incluant 2022 ne couvre pas toutes les crises ; l’univers choisi en 2026 introduit un biais du survivant. Les prix ajustés et la fenêtre rétrospective ne simulent pas une sélection historiquement réalisable. Le change indicatif n’est pas exécutable. Les poids et barèmes ne sont pas vérifiés auprès d’un investisseur réel. Ces limites accompagnent les résultats, sans transformer une mesure passée en niveau de risque futur.

## AWS et suites réservées

Amplify, Lambda/Mangum, S3 privé, IAM, CloudWatch et Guardrail ont été exécutés en T3 puis réunis avec l’analyse K3 en T4. Le [journal T4](fusion/preuves/tranche4/redéploiement.json) et la [réception publique](fusion/preuves/tranche4/public/bilan.json) font foi de l’état publié. La Function URL reste publique, concurrence réservée de deux, délai Lambda de 90 secondes. CORS limite les navigateurs, pas la dépense cumulée. Le flux peut arriver d’un bloc : l’interface le dit. Le compte de l’événement est annoncé comme fermé le 16 novembre à 13 h 59 ; les ressources et données hébergées disparaîtront alors.

Ne sont pas intégrés : versionnement/Store et recherche documentaire de B, architecture à quatre agents et rendu HTML de A, trajectoires conditionnelles plus riches, optimisation de portefeuille, score ESG et passage d’ordres. B reste meilleur sur le versionnement et la recherche documentaire. Ces éléments demanderaient une nouvelle tranche justifiée par des cas et tests ; ils ne sont pas présentés comme disponibles.

Restent à valider : inspection visuelle des cas 1, 2, 3 et 5, interactions et petit écran ; coût/latence sous charge ; revue des barèmes avec le porteur au-delà de l’arbitrage fonctionnel. Aucune vidéo ni page de présentation n’est produite dans cette tranche.
