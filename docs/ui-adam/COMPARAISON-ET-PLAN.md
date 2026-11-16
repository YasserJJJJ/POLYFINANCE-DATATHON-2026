# Cinq directions — comparaison et plan d'intégration

15 novembre 2026, branche `ui-adam`. Rien n'est intégré à l'interface principale : ce document sert à choisir.

Ouvrir : `prototypes/ui-adam/index.html` (galerie), ou chaque dossier `1-carnet`, `2-relief`, `3-pupitre`, `4-fil`, `5-epure`. Les cinq pages partagent le cas, les paramètres, le niveau de lecture et l'historique.

## 1. Les cinq directions

| | Idée directrice | Mécanisme qui la distingue | Sert surtout | Références qui l'ont nourrie | Risque principal |
|---|---|---|---|---|---|
| **1 Carnet** | Le dossier est un texte annoté ; la conclusion est le début d'une lecture | La phrase du verdict porte ses réglages ; une modification est une correction d'éditeur (ancien barré, nouveau à l'encre rouge, page « à relire ») | Comprendre le pourquoi ; lire les preuves sans quitter le texte | Direction Folio de B, notes de marge de Tufte CSS, phrase réactive de Bret Victor | Page longue (8 000 px) ; le résultat n'est pas visible d'un seul regard |
| **2 Relief** | La décision est un territoire | La grille montant × horizon est une carte ; on déplace sa demande vers la zone acceptable ; l'historique est un itinéraire balisé | Explorer « qu'est-ce qui rendrait ma demande acceptable ? » | Frontière de verdict tracée (recherche 1), cartes d'isolignes | La carte n'a d'intérêt que si la grille varie : Amira est incohérente partout, Mateo se décide sur une préférence. Un dossier détaillé n'existe que pour l'horizon déclaré |
| **3 Pupitre** | Tout le dossier sous les yeux, vérifiable au clavier | Palette de commandes et différence exacte entre deux révisions | Lecteur professionnel, juré technique, conseiller | Terminaux, clients Git, registre de faits | Intimidant pour un novice, même en lecture « Essentiel » |
| **4 Fil** | Une conversation avec ses propres « et si » | Chaque question ajoute une carte ; le fil est l'historique ; « annuler » après coup | Novice, téléphone, première compréhension en dix secondes | Annulation plutôt que confirmation, feuille basse, écran « ce qu'on a compris » | Fil très long après quelques essais ; la comparaison de deux états éloignés demande de défiler |
| **5 Épure** | La comparaison est l'interface | Deux panneaux miroirs « sans / avec », écarts portés par des cotes de dessin technique, rideau avant/après sur les courbes réelles, cartouche de révisions | Voir ce que la demande change, mesuré ; démontrer le gain de la fusion | Écart apparié (recherche de A), comparateur d'images, cartouche de plan | Le verdict et ses règles passent au second plan derrière la mesure ; ton froid pour un particulier |

## 2. Constats observés

Ce que j'ai réellement ouvert et manipulé dans un navigateur, à 1280 × 800 et à 375 × 812.

| | Chargement sans erreur de console | Pas de défilement horizontal à 375 px | Parcours manipulé par moi | Non manipulé par moi |
|---|---|---|---|---|
| Carnet | oui | oui | corriger le montant dans la phrase → page périmée → relire → « ce que la correction change » ; notes de marge visibles | ouverture d'une référence, éditions et restauration, impression |
| Relief | oui | oui | carte, zones, frontières, itinéraire et coupe affichés avec l'historique partagé | déplacement du repère, fiche de relevé |
| Pupitre | oui | oui | palette `/` → `montant 24000` → aperçu périmé → analyse → différence r3 → r4 ; onglets mobiles | tri du registre, `restaurer`, thème clair |
| Fil | oui | oui | puce « retrait non précisé » → aperçu → « Voir l'avis » → carte « ce qui a changé » → notification « Annuler » ; panneau latéral sur ordinateur | feuille de preuve, « revenir à cet avis » |
| Épure | oui | oui | planche, cotes, cartouche et tableau des révisions affichés ; barre basse mobile | rideau, cote de montant, comparaison de deux révisions |

Non vérifié pour aucune : lecteur d'écran, parcours complet au clavier, zoom à 200 %, états de démonstration (chargement, erreur, reprise), navigateurs autres que celui de l'application. Les auteurs de Carnet, Pupitre et Épure déclarent un passage dans un navigateur sans écran ; celui de Fil un faux navigateur en Node ; je n'ai pas ces sorties.

Constats de fidélité, valables pour les cinq :

- Tous les chiffres viennent de 45 analyses du moteur réel, hors ligne. Aucun n'est calculé dans le navigateur.
- Les paramètres modifiables sont ceux qui ont été précalculés (9 montants et la date de retrait pour Robert, 8 montants pour Amira, 8 montants et l'exclusion pour Mateo). Un autre montant, un autre placement ou une réponse libre ne sont pas réalisés, et chaque page le dit.
- Le travail des rôles affiché est une relecture des étapes enregistrées. Les appels de modèle montrés sont ceux de la tranche 4 de la fusion, pour la demande de départ de chaque situation seulement.
- Les numéros de faits (`F-7`) changent d'une analyse à l'autre. Le Pupitre apparie les faits par leur libellé pour comparer deux révisions. C'est une fragilité du produit, pas des prototypes.
- Les courbes sont tracées avec un point toutes les cinq séances : le creux dessiné de Robert (−19,5 %) est un peu moins profond que la mesure (−20,6 %). L'Épure le dit dans sa légende ; les autres devraient le dire aussi.

## 3. Jugements de conception

Cotes de 1 (faible) à 5 (fort). Ce sont mes jugements, pas des mesures ; aucun utilisateur n'a essayé les prototypes.

| Critère | Carnet | Relief | Pupitre | Fil | Épure |
|---|---|---|---|---|---|
| Compréhension immédiate | 4 | 3 | 2 | 5 | 4 |
| Fidélité au processus réel | 4 | 3 | 5 | 4 | 4 |
| Facilité de correction | 5 | 4 | 3 | 5 | 4 |
| Qualité des preuves | 5 | 3 | 5 | 4 | 4 |
| Adaptation aux trois lecteurs | 4 | 3 | 2 | 3 | 3 |
| Singularité visuelle | 4 | 5 | 4 | 3 | 5 |
| Accessibilité | 4 | 2 | 4 | 4 | 3 |
| Coût d'intégration (5 = faible) | 3 | 1 | 2 | 4 | 3 |

Pourquoi ces écarts :

- **Compréhension** : le Fil dit le verdict en très grand, une idée par carte. Le Carnet le dit en une phrase mais demande de lire. Le Pupitre demande de savoir où regarder.
- **Fidélité** : le Pupitre montre tout sans rien mettre en scène. Le Relief donne de l'importance à une grille qui, pour deux situations sur trois, ne varie pas.
- **Correction** : dans le Carnet et le Fil, on modifie là où on lit. Dans le Pupitre, il faut connaître la commande.
- **Preuves** : notes de marge (Carnet) et registre (Pupitre) laissent la preuve visible à côté du chiffre ; les autres l'ouvrent dans un panneau.
- **Lecteurs** : seul le Carnet me semble tenir du novice au professionnel par le seul changement de niveau de lecture. Le Fil reste court pour un professionnel ; le Pupitre reste dense pour un novice.
- **Accessibilité** : une carte en SVG manipulée au doigt (Relief) est la plus difficile à rendre équivalente au clavier et au lecteur d'écran, même avec la liste de repli.
- **Intégration** : le Fil est le plus proche des cartes par étape déjà en place. Le Relief demande un calcul de frontières et, pour tenir sa promesse, des dossiers détaillés par case que le moteur ne fournit pas.

## 4. Recommandation

**Retenir le Carnet comme direction principale, et lui greffer deux mécanismes : la barre « et si » du Fil sur téléphone, et les cotes de l'Épure pour le bloc avant/après.** Garder le Pupitre comme vue professionnelle ultérieure. Écarter le Relief comme direction principale.

Raisons : le Carnet prolonge la direction Folio que vous avez appréciée ; il est le seul où la preuve reste à portée de regard et où modifier se fait dans la phrase ; son coût reste raisonnable parce que le produit rend déjà des phrases reliées à des faits. Sa faiblesse est le téléphone et la longueur : c'est exactement ce que le Fil résout. Le gain propre à la fusion, mesurer le portefeuille avec et sans la demande, est le mieux montré par les cotes de l'Épure.

Ce qui pourrait renverser ce choix :

- Si la démonstration au jury se joue en deux minutes sur un écran projeté, l'**Épure** impressionne plus vite.
- Si le public visé est d'abord le particulier sur téléphone, le **Fil** seul est plus sûr et moins cher.
- Si le produit s'adresse à des conseillers, le **Pupitre**.

## 5. Ce qui demande votre retour

1. La direction, ou la combinaison, à intégrer.
2. Le tutoiement et le ton : le Carnet et le Fil tutoient comme le produit ; le Pupitre et l'Épure sont plus neutres.
3. Où vit l'historique : dans le navigateur seulement (simple, perdu si on change d'appareil), ou archivé côté serveur (le produit archive déjà chaque dossier dans S3 quand il est déployé).
4. Le cas Amira : son portefeuille fictif dépasse déjà sa limite, donc tout montant est « incohérent ». Changer ses poids fictifs rendrait sa situation plus parlante dans toutes les directions.
5. Polices : les prototypes utilisent celles du système. Une serif embarquée (Source Serif, licence OFL) donnerait au Carnet le même rendu partout.

## 6. Plan d'intégration

### Préalables, quelle que soit la direction

| # | Travail | Où | Pourquoi |
|---|---|---|---|
| P1 | Arrondir les mesures dans les textes du Rédacteur (une décimale), valeur exacte dans le fait | `backend/alphaforge/agents/redacteur.py` | le gabarit écrit « −20,595922 % » |
| P2 | Donner à chaque fait une clé stable en plus de son numéro (`cle: "portefeuille.apres.pire_chute"`) | `backend/alphaforge/dossier.py`, `agents/analyste.py`, contrat | comparer deux analyses sans apparier par libellé |
| P3 | État d'aperçu : une modification marque le résultat périmé, l'analyse se relance sur action explicite | `frontend/src/App.jsx` | aujourd'hui toute modification renvoie à l'étape 2 et efface le dossier |
| P4 | Révisions côté navigateur : liste de dossiers reçus, relecture, restauration, annulation | nouveau `frontend/src/revisions.js` (reprendre la logique de `prototypes/ui-adam/socle/socle.js`) | le produit n'a aucun historique |
| P5 | Niveau de lecture en contexte React, lexique commun | nouveau `frontend/src/lecture.js` | deux profondeurs à faits constants |
| P6 | Test automatique : les mêmes nombres et le même verdict dans les deux niveaux de lecture | `frontend/` (premier test d'interface du projet) | empêcher que la simplification change les faits |

Aucun de ces préalables ne change une règle, un seuil ou un calcul. P1 et P2 touchent le backend et demandent de régénérer les références figées.

### Si le Carnet est retenu

| Composant existant | Sort |
|---|---|
| `composants/TiroirFait.jsx`, `Sources.jsx` | **adapter** : le contenu devient la note de marge ; le tiroir reste le repli sur téléphone |
| `composants/Base.jsx` (puces de verdict et de niveau, étiquettes de type) | **adapter** : formes du tampon et signes typographiques, mêmes états |
| `composants/ComparaisonPortefeuille.jsx` | **adapter** : graphique à pente, puis cotes reprises de l'Épure |
| `composants/GraphiqueChute.jsx` | **adapter** : deux courbes avant/après, axe daté, fenêtre observée |
| `composants/PreuveAppels.jsx`, `etapes/Etape3Trace.jsx` | **conserver** le contenu, le présenter en paragraphe-journal |
| `etapes/Etape4Verdict.jsx`, `Etape5Bascule.jsx` | **fondre** dans la page de lecture : verdict, règles, options, « ce qui changerait » |
| `etapes/Etape1Mots.jsx`, `Etape2Verifier.jsx`, `fichierClient.js` | **conserver** : la saisie et la vérification du profil restent des étapes avant la page |
| `etapes/Comparer.jsx` | **conserver**, à relier aux révisions |
| `api.js`, flux progressif | **conserver** |
| à **ajouter** | `PhraseVerdict` (mots modifiables), `Correction` (ancien barré, nouveau inséré, page périmée), `NoteDeMarge`, `Editions` (colophon et liste), `BarreEtSi` (reprise du Fil, téléphone) |

Ordre proposé, chaque étape laissant l'application utilisable :

1. Préalables P1 à P5, sans changement visuel.
2. Page de lecture du résultat (verdict, règles, notes de marge) derrière un interrupteur, l'ancienne étape 4 restant accessible.
3. Phrase modifiable, correction et édition comparée.
4. Éditions : relire, restaurer, annuler.
5. Bloc avant/après coté ; barre « et si » sur téléphone.
6. P6, vérification clavier et lecteur d'écran, puis retrait de l'interrupteur sur votre accord.

Estimation grossière, non mesurée : deux à trois jours pour une personne qui connaît le code, dont un pour les préalables.

### Si une autre direction est retenue

- **Fil** : même liste de préalables ; les étapes actuelles deviennent des cartes ; à ajouter `BarreEtSi`, `CarteCeQuiAChange`, feuille basse. Le moins de travail.
- **Épure** : préalables, plus l'envoi des séries avant/après par l'API (le moteur les calcule, l'adaptateur ne les transmet pas) ; à ajouter `Planche`, `Cote`, `Rideau`, `Cartouche`.
- **Pupitre** : préalables, P2 devient indispensable ; à ajouter palette de commandes (`cmdk`, licence MIT, compatible React 18), `Registre`, `Diff`.
- **Relief** : préalables, plus un point d'entrée qui rend un dossier détaillé par case, et un calcul de frontières. Le plus de travail, pour un bénéfice limité à une situation sur trois.
