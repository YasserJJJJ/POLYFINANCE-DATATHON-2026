# Expérience technique — un dossier maison, sans dépendance

Petite expérience du 15 novembre 2026 pour départager les options d'architecture (cadre de conception, section 7). Ce n'est pas le produit. Aucun appel de modèle, aucun accès au réseau, aucune ressource AWS. Toutes les valeurs de la chaîne jouet sont fictives et le disent.

## Ce qu'il y a ici

| Fichier | Lignes | Rôle |
|---|---|---|
| `dossier.py` | 313 (234 hors lignes vides, commentaires et docstrings) | Le dossier : pièces rangées par empreinte, journal en ajout seul par branche, tête déduite, tâches mémorisées par l'empreinte de leurs entrées, états, branches, refus d'écriture, greffier, contrôle d'intégrité. Bibliothèque standard seulement |
| `export_prov.py` | 79 | Export PROV-JSON par la bibliothèque standard ; relecture facultative par le paquet `prov` |
| `chaine.py` | 84 | Chaîne jouet : six fonctions pures (qualification, preuves, plan, calculs, objections, restitution) et leurs entrées déclarées |
| `essais.py` | 501 | Les assertions |
| `sorties/` | | Sorties conservées ; `sorties/dossier_exemple/` est un dossier complet à ouvrir à la main (`journal/principale.jsonl`, `pieces/*.json`) |

Le plafond de 350 lignes est tenu par `dossier.py` seul. Avec l'export PROV, on arrive à 392.

## Relancer

Depuis la racine du dépôt :

```
python3 research/experiences/technique/dossier_maison/essais.py                       # tous les essais, bibliothèque standard seule
uv run --with prov python research/experiences/technique/dossier_maison/essais.py     # les mêmes, plus la relecture de l'export par le paquet prov
python3 research/experiences/technique/dossier_maison/essais.py --contre-epreuve      # la course de l'essai (d), avec puis sans verrou (20 s)
python3 research/experiences/technique/dossier_maison/verif_sqlite.py                 # trois affirmations du comparatif des supports, pour SQLite
```

`uv run --with prov` fait télécharger le paquet `prov` depuis l'index PyPI dans un environnement jetable ; rien n'est installé dans le projet. Ni le dossier ni `prov` n'envoient de télémétrie : le dossier n'importe aucun module réseau, et le code installé de `prov` 3.3.0 n'importe que `urllib.parse`.

Chaque essai travaille sur une copie d'un dossier de base, dans un répertoire temporaire supprimé à la fin. Un essai qui échoue lève `AssertionError` et arrête le script.

| Essai | Ce qu'il établit | Assertions |
|---|---|---|
| (c) | Un processus tué (`os._exit`) pendant « calculs », puis la reprise par un autre processus : seules « calculs » et « objections » sont exécutées, les trois tâches terminées ne le sont pas (compteur d'appels réels). Les deux lancements de « calculs » sont au journal. La question à la personne (`fait:perte_acceptable` absent) suspend la restitution sans bloquer le reste ; la réponse ne lance que la restitution | 12 |
| ligne tronquée | Une ligne du journal coupée par une panne n'est pas un événement ; l'écriture suivante repart sur une ligne neuve ; la chaîne des empreintes tient | 3 |
| (a) | Six champs corrigés un par un. L'ensemble périmé, écrit à la main dans `CAS_A`, est exactement celui observé ; chaque pièce périmée nomme l'événement qui l'a périmée ; le reste garde ses empreintes ; les tâches refaites sont exactement celles attendues. Une reformulation de l'objectif qui rend la même décision ne refait qu'une tâche (coupure anticipée) | 39 |
| (b) | La variante refait quatre tâches, partage la décision et les preuves ; le journal de la ligne principale est identique octet pour octet ; cinq pièces nouvelles sur disque ; bifurcation depuis un état passé | 11 |
| (d) | La seconde écriture préparée sur le même sommet est refusée et n'écrit rien ; rejouée, elle passe. Huit processus au même instant : un accepté, sept refusés. Une correction arrivée pendant une tâche : le résultat arrivé trop tard est gardé comme périmé, la tâche est refaite | 9 |
| (e) | L'horizon revient à sa valeur : la tête d'origine revient empreinte pour empreinte, aucun appel, aucune pièce nouvelle | 5 |
| (f) | Pièce retirée : état « erronée » avec motif, lisible, jamais de retour même si les entrées reviennent ; ce qui en dérive est périmé avec le retrait pour cause ; l'affichage qui en dépendait est signalé ; la tâche n'est pas relancée tant que sa version ne change pas | 11 |
| (g) | Préparer n'est pas afficher ; une réaction qui cite une restitution jamais affichée est refusée ; le choix reste lié à la version montrée, que l'on sait ensuite périmée | 8 |
| (h) | Export PROV-JSON : 156 enregistrements ; une seule invalidation (le retrait), aucune pièce périmée exportée comme invalidée ; relu par `prov` 3.3.0 avec aller-retour identique | 5, ou 6 avec `prov` |
| empreintes et droits | Ordre des clés indifférent ; 1 et 1.0 diffèrent ; deux codages Unicode du même mot diffèrent ; NaN refusé ; la date n'entre pas dans l'empreinte ; l'agent 3 ne peut pas déposer un fait | 8 |
| erreur d'outil | Deux échecs journalisés, étude « interrompue » sans restitution en vigueur ; l'outil réparé, la reprise termine | 4 |
| intégrité | Pièce altérée, événement altéré, événement supprimé : les trois se voient | 3 |

## Mesures (portable sous macOS, disque local)

Les deux derniers passages sont conservés : `sorties/essais.txt` (bibliothèque standard, Python 3.12.7) et `sorties/essais_avec_prov.txt` (Python 3.13.0, `prov` 3.3.0). `sorties/mesures.json`, `sorties/dossier_exemple/` et les deux exports PROV viennent du second.

- 118 assertions en 1,36 s sans `prov` ; 119 en 1,45 s avec. Une seconde sur ce total est l'attente voulue avant la course des huit processus.
- Une étude complète : 21 événements, 14 pièces, 11 299 octets (15 fichiers). Le dossier d'exemple : 35 événements, 20 pièces, 18 991 octets ; 100 Ko occupés sur disque, car chaque petit fichier prend un bloc.
- Journal de 621 événements : relire et déduire la tête prend 2,5 à 2,7 ms ; tous les états, 41 à 43 ms ; contrôle d'intégrité, 25 à 31 ms. Le construire a pris 2,8 à 3,1 s (200 corrections suivies de reprise), parce que chaque opération relit tout le journal.
- Cent dépôts : 0,10 à 0,12 s, avec ou sans `os.fsync`. Sur macOS, `os.fsync` ne force pas l'écriture physique.
- Contre-épreuve du verrou (`sorties/contre_epreuve_verrou.json`), dix tours de huit écrivains, un seul passage : avec le verrou, aucun tour n'accepte deux écritures ; sans lui, huit tours sur dix en acceptent plusieurs, et le contrôle d'intégrité voit 29 ruptures de chaîne.

`verif_sqlite.py` vérifie trois affirmations du comparatif des supports pour SQLite (refus d'une seconde écriture au même rang, ajout seul par déclencheurs, aval d'une pièce en une requête). Ce n'est pas un portage.

## Trois choix que l'expérience a forcés

1. **L'empreinte d'une pièce ne couvre que son contenu** (`type`, `corps`). L'auteur, l'activité, les entrées et la date sont dans l'événement du journal. Si la date ou les entrées entraient dans l'empreinte, ni la coupure anticipée ni le retour en vigueur ne marcheraient. Le contrat 02, section 1, dit que la pièce « porte » ces mentions : il faut préciser qu'elle les porte par le journal.
2. **Une même pièce peut avoir plusieurs productions.** « Preuves », refaite après un changement de part, rend le même contenu, donc la même pièce. La dérivation valable dans une tête est celle dont la clé correspond à cette tête. Le premier passage de l'essai (b) a échoué là-dessus : le registre d'objections jouet ne citait pas le calcul éprouvé, et la variante rendait la même pièce que la ligne principale. Le jouet a été corrigé ; dans le produit, une pièce doit citer ce sur quoi elle porte.
3. **« Invalidé » au sens de PROV est irréversible** : il ne convient qu'au retrait d'une pièce erronée. « Périmée » est un état calculé par rapport à une tête et ne s'exporte pas comme une invalidation.

## Ce qui n'a pas été fait

- Aucun appel de modèle. Le réemploi d'une pièce écrite par un modèle (tâche non déterministe) et les tâches volatiles (recherche web) ne sont pas essayés.
- Le graphe de tâches est fixe : six tâches. Les sous-questions créées en cours d'étude, le nombre maximal de réouvertures et la clé de dédoublonnage des questions ne sont pas faits.
- Pas de portes sur le contenu des pièces ; seuls les droits de dépôt sont contrôlés.
- Le greffier exécute une tâche à la fois, sans délai maximal ni annulation.
- Une panne entre le rangement d'une pièce et son événement n'a pas été provoquée. Une coupure de courant non plus.
- Le verrou (`fcntl.flock`) n'a été essayé que sur un disque local de macOS. Il n'existe pas sous Windows et n'est pas sûr sur un disque partagé.
- Le paquet `prov` relit l'export ; il n'a pas de fonction de validation d'ensemble des contraintes PROV (lu dans le code installé). La conformité à ces contraintes n'est pas établie.
- S3 et DynamoDB ne sont comparés que sur le papier : rien n'a été créé ni appelé sur AWS.
- Chaque conduite a été observée sur quatre passages complets, sur une seule machine. Deux passages antérieurs se sont arrêtés sur une attente fausse du script d'essais, pas sur une erreur du dossier : celle de l'essai (b) décrite plus haut, et un compte de pièces mal posé dans l'essai (a).
