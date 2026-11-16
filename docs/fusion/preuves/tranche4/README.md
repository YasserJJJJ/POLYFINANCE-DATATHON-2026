# Réception de la tranche 4

Exécution sur la branche `fusion-corrections-deploiement`, intégrateur Bedrock/Astra, profil `alphaforge`, région `us-east-1`. [Route](route-execution.json). Aucun sous-agent : sa route distincte n’était pas vérifiable avant appel. Les tests du produit sur Nova/Sonnet ont été autorisés séparément.

## Dix cas — attendu et observé

| Cas | Attendu | Observé | Preuve |
|---|---|---|---|
| 1 Robert/TSLA 80 000 sur 400 000, retrait 4 ans | Incohérent ; perte avant/après ; ajustement et placement large | Incohérent ; −14,256677 → −20,595922 %, écart −6,339245 points ; ajustement 38 000 CAD et XIU.TO présents | [Dossier](robert-hors-ligne.json) |
| 2 Amira/BTC 10 000 sur 40 000, 15 ans | Pas cohérent sans réserve ; concentration ; limite crypto | Incohérent ; concentration orange et capacité rouge ; limite d’échantillonnage crypto reprise | [Dossier](amira-hors-ligne.json) |
| 3 Mateo/ENB 15 000, exclusion Énergie | Incohérent malgré un écart favorable ; alternative compatible | Exclusion rouge ; baisse moins profonde de 1,097309 points ; ESGV proposé comme comparaison compatible | [Dossier](mateo-hors-ligne.json) |
| 4 Robert sans épargne | Indéterminé, question, pas de grille | Indéterminé ; question sur l’épargne ; grille vide | [Dossier](cas4-sans-epargne.json) |
| 5 Robert sans retrait | Verdict courant + question décisive | Ajustement ; question en premier, retrait à 4 ans ferait passer à incohérent ; donnée laissée absente | [Dossier](cas5-sans-retrait.json) |
| 6 Montant 120 000 sur épargne 100 000 | Indéterminé avec raison, sans allocation | « Le montant dépasse l’épargne totale. » ; pas d’allocation ni de grille | [Dossier](cas6-impossible.json) |
| 7 GameStop/GME | Message explicite, pas d’erreur brute | 422 avec la mention des 31 actifs ; le client traduit ce message sans statut technique | [Réponse](cas7-gamestop.json) |
| 8 Retrait à 10 ans puis montant 20 000 | Verdicts accordés à la grille, K3 suit le montant | Incohérent → ajustement → cohérent ; écart passe de −6,339245 à −0,815903 points après modification du montant | [Retrait](cas8-retrait10.json), [montant](cas8-montant20000.json) |
| 9 Chaîne de preuve de la baisse après | Fait → méthode → donnée → registre | Robert F-23 : historique-B, jeu de départ, références de données et de méthode existantes | [Dossier](robert-hors-ligne.json), [registre](registre.json), test 9 |
| 10 Sans identifiants AWS | Fonctionnel, K6 vide, cinq objets égaux avec modèle | Import SDK interdit dans le test ; K6 vide. Avec Bedrock réel, égalité de verdict/règles/options/grille/K3 pour les trois personas | [Bilan réel](bilan-bedrock.json), test 10 |

Les dix tests sont dans `backend/tests/test_reception_fusion.py`. Les références figées comparent le dossier entier hors durée et preuve d’appel ; [seuls les ajouts de texte attendus changent](changements-references.json). Aucun test antérieur n’est supprimé.

## Commandes et sorties

```sh
# Depuis la racine ; Python du venv existant.
ALPHAFORGE_LLM=off ALPHAFORGE_DATA_BUCKET='' backend/.venv/bin/python docs/fusion/preuves/tranche4/reception.py
# API de vérification démarrée sur 18764 avec AWS_PROFILE=alphaforge,
# AWS_REGION=us-east-1, ALPHAFORGE_LLM=auto, bucket vide,
# ALPHAFORGE_GUARDRAIL_ID=xj89p36uyw64, ALPHAFORGE_GUARDRAIL_VERSION=1.
backend/.venv/bin/python docs/fusion/preuves/tranche4/reception.py --url http://127.0.0.1:18764
# Le script refuse de refaire une capture réelle déjà présente.
node frontend/verifier_restitution.mjs
ALPHAFORGE_LLM=off PYTHONPATH=backend backend/.venv/bin/python docs/fusion/preuves/tranche-2/rejouer_performances.py
cd backend
ALPHAFORGE_LLM=off ALPHAFORGE_DATA_BUCKET='' .venv/bin/python -m pytest -q --tb=short
```

- Après fusion T2 : [313 tests](tests-apres-fusion-t2.txt), [build](build-apres-fusion-t2.txt).
- Après fusion T3 : [332 tests](tests-apres-fusion-t3.txt), [build](build-apres-fusion-t3.txt).
- Réception finale : [344 tests réussis](tests-finaux.txt) en 19,42 s ; [build local](build-final.txt).
- [Rendu React statique](rendu-react.json) : cinq dossiers, grille non monotone, option à la hausse, fiche/question, preuves réelles, champs K3/K6 absents. **Aucune interaction de navigateur ni disposition visuelle validée.**
- [Performances](performances.json) : trois passages par cas, caches applicatifs vidés, imports et cache système chauds. Maximum Robert 318,848 ms ; Amira 613,476 ms ; Mateo 274,625 ms ; Amira/XIU 298,301 ms.
- [Bedrock réel](reception-bedrock.txt), trois appels par dossier : Robert 12,631 s / 16 932 jetons ; Amira 12,845 s / 15 784 jetons ; Mateo 12,564 s / 15 718 jetons. Pas d’appel ajouté, mais consommation supérieure à l’objectif initial d’environ 8 000 jetons avec le contexte et le Guardrail.
- [Comparaison C](comparaison-avec-c.json) : bascule de règle `approximation` ; [comparaison B](comparaison-avec-b.json) : huit mesures avant/après égales aux preuves B de départ pour chaque persona.
- [Originaux](controle-origines.json) : archives, imports, données, moteurs, règles et infrastructure préservés.

## Publication et inspection

Le [plan](plan-deploiement.json), le [journal de mise à jour](redéploiement.json), la [sortie](deploiement.txt) et la [réception publique](public/bilan.json) décrivent l’exécution. Le code déployé correspond au commit `1d30724`, sans modification des formules ou de l’infrastructure. Les documents et preuves sont ajoutés ensuite.

**Inspection visuelle non effectuée pour les cas 1, 2, 3 et 5.** [Preuve du blocage](inspection-navigateur.json) : navigateur intégré indisponible et accès Chrome refusé par l’autorisation de Computer Use. Aucune capture n’est inventée. Deux suites possibles : autoriser l’accès au navigateur puis refaire ces quatre parcours ; ou les faire inspecter manuellement et conserver cette réserve jusqu’à leur validation. Le rendu statique ne remplace pas cette étape.

## Échecs intermédiaires conservés

`tests-reception-initiale.txt` contient une assertion trop stricte sur les identifiants F-n lors d’un changement de retrait : les valeurs étaient égales, les numéros locaux différaient. Le test compare désormais les mesures et garde les contrôles de chaîne de preuve.

`tests-avant-references-t4.txt` contient les écarts de textes attendus, un faux appelant ne prenant pas encore l’argument `agent`, et la documentation générée avant sa mise à jour. La capture d’agent a été complétée par une assertion de son nom. Les sorties finales ci-dessus sont vertes.

Le contrôle React a d’abord utilisé la grille de 14 000 CAD pour rechercher une inversion située au-delà de son maximum. La grille existante n’explore que jusqu’au montant demandé. Le contrôle utilise désormais celle de 35 000 CAD, comme le test T2, et vérifie séparément le constat d’ajustement à la hausse depuis 14 000 CAD. Aucun calcul de grille n’a été changé.


## Réception publique constatée

Mise à jour terminée sans création de ressource. Fichiers JS/CSS servis strictement égaux au build local, santé et CORS conformes, ZIP Lambda identique. Robert public conserve les cinq objets métier et sa copie S3 est strictement égale : `dossiers/20261116-013755-e5a9bd3f.json`.

Le premier texte du Rédacteur est refusé pour contradiction du verdict, le second pour une citation non textuelle (« Concentration »). Le repli prévu rend le gabarit déterministe. Quatre appels réels, 30 587 jetons, dernière ligne à 20,583202 s ; réception d’un bloc sur 0,038168 s. La plage de 8–14 s n’est donc **pas tenue pour cette réception publique**. Aucun appel structurel n’a été ajouté : le second essai existant explique la différence. L’optimisation du coût et de la latence reste ouverte, sans assouplir les garde-fous.

Le [script public](verifier-publication.py) réutilise celui de T3 : K3 est ajouté à l’égalité, les ressources JS/CSS sont comparées au build, et la recherche S3 est limitée aux objets de l’instant de la demande. Commande réelle, depuis la racine :

```sh
AWS_PROFILE=alphaforge AWS_REGION=us-east-1 \
PYTHONPATH="$PWD/backend/.venv/lib/python3.13/site-packages" \
python3 docs/fusion/preuves/tranche4/verifier-publication.py
```

Le Python système réutilise les bibliothèques existantes ; TLS reste vérifié. Le redéploiement a utilisé le même environnement, plus `ALPHAFORGE_GUARDRAIL_ID=xj89p36uyw64`, `ALPHAFORGE_GUARDRAIL_VERSION=1`, `PIP_NO_CACHE_DIR=1`, `npm_config_cache=$PWD/infra/build/npm-cache`, puis `python3 infra/deployer.py --journal docs/fusion/preuves/tranche4/redéploiement.json`. Aucun fichier d’identifiants n’a été ouvert.
