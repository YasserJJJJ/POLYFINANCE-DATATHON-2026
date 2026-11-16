# AlphaForge — évaluation indépendante et stratégie de fusion de A, B et C

15 novembre 2026. Rien n'a été modifié dans le produit commun ni dans les archives. Les prompts d'exécution sont dans ce dossier (`CADRE-COMMUN.md`, `PROMPT-1` à `PROMPT-4`) ; ils ne s'exécutent qu'après votre validation.

## 0. Ce qu'il faut retenir

**Recommandation : garder C comme socle, y transférer le moteur de comparaison de portefeuilles de B et la preuve d'appel AWS de A, conserver le reste de A et de B comme références.** Quatre prompts : le premier seul, les deux suivants en parallèle, le dernier seul.

- **C** est le seul des trois à trancher la question que posent les personas (la demande est-elle cohérente avec le profil ?), avec le parcours le plus complet et le moins de risque d'intégration.
- **B** est le mieux construit (dossier versionné, reprise, preuves) mais ne sait pas représenter un profil ni juger une demande ; il résout deux questions étroites.
- **A** a un produit à agent unique honnête et coûteux, la meilleure recherche de méthode, et une architecture à quatre agents de qualité qui n'est pas construite.
- **Le couplage qui apporte le plus** : C estime la perte par `part × pire chute du titre`. Sur Robert, cela donne 14,2 %, sous sa limite de 15,5 %. Le moteur de B, appliqué au même portefeuille, mesure une pire baisse de −20,6 % après la demande contre −14,3 % avant. La règle de C passe donc à côté d'un dépassement que B mesure, et B ne sait pas en tirer un verdict. Les deux se complètent exactement.
- **Limite de cette recommandation** : avec d'autres poids de critères (AWS et architecture d'abord), B passe devant C au score. La décision tient au défaut décisif de B comme socle et au coût d'intégration, pas à une note.

Trois points demandent votre attention avant de lancer : la branche d'intégration est en retard de 22 commits sur le code de C que vous m'avez remis ; aucun composant du produit n'est déployé sur le compte AWS ; les documents de A et de C situent le dépôt du code ce soir à 23 h 59 et la destruction du compte AWS demain à 13 h 59.

## 1. Accès, environnement, méthode

| Point | Constat |
|---|---|
| Identité AWS | compte `471112821226`, rôle `WSParticipantRole`, profil `alphaforge`, `us-east-1` |
| Modèles disponibles sur Bedrock | tous ceux des trois produits : `global.anthropic.claude-sonnet-5-5` (A), `global.openai.gpt-6-astra` (B), `global.anthropic.claude-sonnet-5` et `global.amazon.nova-2-lite-v1:0` (C) |
| Route de cette évaluation | **exception validée par vous** : cette session et ses trois sous-agents ont tourné sur votre compte Claude (`api.anthropic.com`), pas sur Bedrock. Les appels de modèle des produits testés sont passés par Bedrock, profil `alphaforge` |
| Ressources du produit sur le compte | aucune (ni Lambda, ni S3, ni Amplify, ni Guardrail) ; seules les ressources de l'atelier existent |
| Archives | 6 fichiers. `evaluation_fusion (claude).zip` est identique octet pour octet à `Presentation et evaluation (codex).zip` : c'est le dossier de B. Le dossier de A est dans son archive ; celui de C est `dossier-fusion.zip` |
| Secrets | aucun identifiant trouvé dans les archives ; `infra/enregistrer_identifiants.ps1` (C) est un script d'enregistrement, non ouvert |
| Attribution | **A** = archive « claude-code », **B** = archive « codex », **C** = archive « Yahya ». Les archives ne portaient aucune lettre ; le code révèle l'origine, l'évaluation n'est pas aveugle |

Méthode : énoncé lu en entier, critères fixés avant tout examen ; trois évaluateurs indépendants (un par réalisation, même brief, mêmes dix cas, chacun sans accès aux deux autres), copies de travail séparées, scripts inspectés avant exécution ; revue transversale par moi sur le code des contrats, les trois interfaces vues dans un navigateur, un recalcul indépendant des mesures et une expérience de couplage. Chaque produit a eu au plus trois exécutions réelles sur Bedrock.

**Incident** : l'évaluateur de C a lancé une commande d'arrêt trop large (`pkill -f uvicorn`) qui a aussi arrêté des serveurs locaux qui n'étaient pas les siens : trois `alphaforge_app.main:app` et un `prototype.prompt6.server:app`. Si vous aviez Folio ou un prototype ouverts, ils sont à relancer. Aucun fichier n'a été touché.

Rapports complets : `preuves/A-rapport.md`, `preuves/B-rapport.md`, `preuves/C-rapport.md`.

## 2. État réel des trois réalisations

L'annonce « deux réalisations complètes, une arrêtée après la conception » est **confirmée avec une nuance** : la réalisation arrêtée est A, mais A contient aussi un produit plus ancien qui fonctionne.

| | A — `datathon2026` 0.1.0 | B — Folio 0.7.0 | C — Second avis |
|---|---|---|---|
| Nature | agent unique sur Bedrock (10 outils) + enchaînement fixe ; page de dossier ; **architecture à quatre agents conçue, non construite** ; recherche hors produit | quatre rôles sur Bedrock, LangGraph, Store SQLite à objets immuables, programmation linéaire, comparaison historique, interface éditoriale | orchestrateur à ordre fixe : Profileur, Analyste, Sceptique, Gardien, Rédacteur ; règles en code ; interface React en 5 étapes |
| Installation neuve | réussie | réussie (Python 3.15 et 3.13) | réussie |
| Tests | 51 réussis | 124 réussis (115 sans données) | 201 réussis |
| Exécution réelle Bedrock | 3 cas, 4 à 6 appels, 36 000 à 63 000 jetons d'entrée, 42 à 56 s | 3 cas, 3 à 4 appels, environ 13 000 jetons, 28 à 38 s | 3 cas, 3 à 4 appels, environ 8 000 jetons, 8 à 14 s |
| Sans AWS | enchaînement fixe seulement (2 scénarios) | calculs complets, sans lecture de texte libre | tout le parcours, textes en gabarit, 0,05 s |
| Question réellement résolue | « que devient le risque d'un portefeuille si ce titre y pèse x % ? », sans décider | « quel capital minimal déplacer pour financer un retrait ? » et « qu'aurait donné cette allocation ? » | « cette demande est-elle cohérente avec ce profil, et qu'est-ce qui la rendrait acceptable ? » |
| Persistance, versions, reprise | aucune dans le produit ; prototype hors produit (118 assertions) | complètes et vérifiées (révisions, invalidation sélective, reprise après arrêt brutal) | aucune |
| AWS au-delà de l'inférence | rien | recherche web AgentCore exécutée ; rien de déployé | scripts Lambda, S3, Amplify, Guardrail écrits, jamais exécutés |

## 3. Comparaisons sur des bases communes

### 3.1 Les trois produits ne répondent pas à la même question

Les dix cas ont été projetés dans chaque produit. Leurs sorties ne se classent pas entre elles ; voici ce que chacun fait de la même demande.

| Cas | A | B | C |
|---|---|---|---|
| **Robert, 80 000 CAD en Tesla sur 400 000, retrait dans 4 ans** | décrit l'écart, ne décide pas. Portefeuille de départ et seuil **choisis par le modèle** ; affiche « patrimoine non renseigné » alors que la demande le donne | devient « minimum 100 000 CAD à réallouer » (égal au retrait posé) ou une comparaison historique ; écrit « pas convenance personnelle » | **incohérent** : 20 % de l'épargne contre un seuil de 9,5 % avec un retrait proche ; version ajustée à 38 000 CAD ; placement large comparé |
| **Amira, 10 000 CAD en Bitcoin sur 40 000** | signale que 25 % de poids porterait 68,7 % du risque ; part maximale 14 % sous un seuil posé par le modèle | comparaison avec et sans ; aucun garde-fou sur le montant | **ajustement** : seuil de concentration 17 %, version ajustée 6 800 CAD |
| **Mateo, Enbridge, préférence ESG** | aucune donnée ESG ; compare des performances | aucune donnée ESG ; la lacune n'est pas signalée dans ce cas | **incohérent** par exclusion du secteur Énergie ; alternative compatible proposée. Étiquette de secteur seulement, pas de donnée de controverse |
| Information manquante | ne bloque jamais ; pose des questions en fin de dossier | `missing_input`, un champ à la fois | **indéterminé** avec question. Défaut : sans date de retrait, le verdict de Robert s'adoucit sans question |
| Contradiction (risque faible, 2 ans, tout en Bitcoin) | vue par le modèle, formulée en question | **3 clarifications bloquantes** de l'agent 0, aucun calcul : meilleur traitement des trois | incohérent, tension affichée |
| Demande impossible (120 000 sur 100 000) | non exprimable en champ | `infeasible` avec certificat : meilleur traitement | traitée comme « 120 % de l'épargne » : défaut |
| Actif hors univers | l'agent le dit et propose des alternatives | `missing_input` | erreur 422 brute : défaut |
| Modification du profil | tout recalculé, rien de versionné, horizon plafonné à 4 ans | **nouvelle révision, invalidation sélective, avant/après conservé** | tout recalculé en 0,05 s, rien de versionné |
| Révision d'une hypothèse | curseurs de scénario | **aperçu sans engagement**, puis révision | seuils dans le code, non modifiables par l'interface ; curseurs montant × horizon |
| Preuve d'un chiffre | nombre → registre → trace, 3 étapes | claim → pointeur → valeur → empreintes du code et des données, 2 appels | chiffre → source et méthode → références, 3 à 4 clics |
| Reprise après interruption | rien | **reprise sans rejouer ce qui est commis** | rien |

### 3.2 Les moteurs de calcul concordent, sous des conventions différentes

Recalcul indépendant (`preuves/ORACLE-mesures.json`) : chaque moteur est exact **dans sa convention**.

| TSLA, 2021-11-12 → 2026-11-12, en CAD | A | B | C | Recalcul indépendant |
|---|---|---|---|---|
| Rendement annualisé | 5,53 % | 5,53 % | 5,5 % | 5,53 % |
| Volatilité annualisée | 55,75 % | 58,61 % | 58,8 % | 55,75 % (hebdomadaire, √52) ; 58,79 % (quotidienne, √252) |
| Pire baisse | −70,88 % | −69,81 % | −70,9 % | −70,88 % (toutes les séances du titre) |
| Corrélation TSLA–SPY | 0,513 | absente | 0,51 | 0,513 |

Trois grandeurs portent le même nom et ne sont pas la même chose : la volatilité (hebdomadaire chez A, quotidienne chez B et C ; pour le Bitcoin, √365 chez C sur 1 827 cotations, grille des séances boursières chez B) ; la pire baisse (calendrier du titre chez A et C, grille commune de 1 228 séances chez B ; quotidienne pour un actif et hebdomadaire pour un portefeuille chez A) ; les unités (points chez C, fractions chez A et B). D'où la règle d'autorité du cadre (K4).

### 3.3 Expérience de couplage : le moteur de B sous la règle de C

Script `preuves/exp_couplage.py`, sortie `preuves/EXP-couplage-B-vers-C.json`. Portefeuilles des personas de C, poids supposés égaux, moteur de B sans modification, 0,4 s.

| Persona | Pire baisse du portefeuille avant | après la demande | Écart apparié | Ce que la règle de C calcule |
|---|---|---|---|---|
| Robert, 20 % TSLA | −14,3 % | −20,6 % | −6,3 points | 14,2 %, jugé sous la limite de 15,5 % |
| Amira, 25 % BTC | −46,8 % | −50,6 % | −3,8 points | 18,4 % |
| Mateo, 12,5 % ENB.TO | −13,2 % | −12,1 % | +1,1 point | 2,7 % |

Lecture : pour Robert, la formule de C sous-estime parce qu'en 2022 le reste du portefeuille a baissé en même temps. Pour Amira, le portefeuille actuel dépasse déjà sa limite ; la demande l'aggrave de 3,8 points, tout en réduisant sa volatilité. Pour Mateo, la mesure est favorable et c'est bien la préférence qui bloque. A, avec un autre portefeuille de départ choisi par son modèle, trouve le même sens pour Robert (−12,9 % → −22,5 %). Ces chiffres valent pour des poids supposés ; ils établissent le sens de l'écart, pas un niveau de risque.

## 4. Inventaire comparatif des contributions

État : **V** vérifié par un critère et un résultat, **E** exécuté par nous, **I** implémenté non exécuté, **C** conçu. Détail par contribution (définitions, hypothèses, dépendances, incertitudes) dans les trois rapports.

| # | Contribution | Origine | État | Valeur pour le défi | Preuve | Dépend de | Transfert | Décision |
|---|---|---|---|---|---|---|---|---|
| 1 | Verdict par règles en code, pire niveau, 4 états | C `gardien.py` | V | forte : seul mécanisme qui tranche | 201 tests, 14 880 cases de grille | `profil.py`, mesures | socle | **Retenu** |
| 2 | Profil à deux jauges (tolérance, capacité) | C `profil.py` | E | forte ; barèmes d'équipe non étalonnés | cas rejoués | — | socle | **Retenu** |
| 3 | Contrat `Dossier` : fait, source, méthode, type | C `dossier.py` | E | forte | tous les cas | `sources.py` | socle | **Retenu**, étendu (K3, K6) |
| 4 | Contrôle d'ancrage du texte, boucle de correction | C `redacteur.py`, `garde_fous.py` | E | forte | refus réel observé sur Bedrock | contrat 3 | socle | **Retenu** |
| 5 | Vérificateur de textes à références `{{R-0001}}` | A `evidence.py` | V | forte ; lexical | 14 tests ; 8 exécutions sur 9 corrigées | registre de A | seul, bibliothèque standard | **Réservé** : même fonction que 4, déjà câblée au parcours |
| 6 | Claims à pointeurs, empreintes du code et des données | B `finance.py`, `models.py` | V | forte | 2 appels pour remonter | Store | avec le Store | **Réservé** |
| 7 | Mesures d'un actif en CAD | C `calculs.py` | V | forte | écart ≤ 0,05 point | CSV | socle | **Retenu** (autorité pour l'actif seul) |
| 8 | **Comparaison historique de portefeuilles** | B `analytics.py`, `datasets.py` | V | forte : mesure le portefeuille entier | recalcul identique ; expérience 3.3 | CSV, bibliothèque standard | **seul, faible effort** | **Transféré** (autorité pour le portefeuille) |
| 9 | Portefeuille rééquilibré, part du risque par ligne | A `analytics.py` | V | moyenne à forte | tests ; C1, C2 | pandas | fonctions pures | **Transféré en option** (part du risque) ; `blend` transféré |
| 10 | Réallocation minimale par programmation linéaire | B `finance.py` | V | faible ici : le minimum égale souvent le retrait ; pas de mesure de risque | oracles | SciPy | seul | **Réservé** |
| 11 | Grille de bascule, plus petit ajustement | C `gardien.py` | V | forte : « ce qui changerait l'avis » | monotonie vérifiée | règle 1 | socle | **Retenu** |
| 12 | Balayage « part maximale sous un seuil » | A `tools.py` | E | moyenne ; dépend de l'histoire tirée | C1 | 9 | — | **Écarté** : même fonction que 11, seuil choisi par le modèle |
| 13 | Qualification d'un texte libre | C Profileur (Nova) ; B agent 0 | E ; E | forte | cas rejoués | modèle | — | **C retenu** ; la détection de contradiction de B est une extension |
| 14 | Critique outillée à catalogue fermé | C Sceptique | E | moyenne : bornée, sans effet sur le verdict | cas rejoués | modèle | socle | **Retenu**, catalogue étendu |
| 15 | Recherche documentaire datée + recherche web AgentCore | B agent 1, `research.py` | E en partie | potentiellement forte ; corpus absent, source promotionnelle retenue, dépend de l'heure UTC | E2 | corpus, Store | bloc | **Réservé** |
| 16 | Dossier versionné, commits, invalidation, reprise | B Store, service, workflow | V | forte pour révision et reprise | tests, arrêt brutal | SQLite, POSIX, LangGraph | bloc, effort substantiel | **Réservé** |
| 17 | Prototype de dossier versionné | A `dossier_maison` | V hors produit | potentielle | 118 assertions | POSIX | seul | **Réservé** (doublon de 16, moins mûr) |
| 18 | Architecture à quatre agents, contradicteur, 7 types de résultats, critères de réception | A `docs/refonte/architecture/` | C | forte comme spécification | cohérence des contrats ; rien d'exécutable | catalogue non écrit | spécification | **Réservé** ; une règle reprise (19) |
| 19 | Règle « écarts appariés établis, niveaux non établis » | A recherche R09 | E (6 scripts relancés, sorties identiques) | forte pour l'honnêteté de l'analyse | diffs vides | — | règle de présentation | **Retenu** comme règle de langage et forme de K3 |
| 20 | Preuve d'appel AWS (identifiant, jetons, latence) | A `agent.py` | E | moyenne (critère AWS, étapes observables) | 3 dossiers | — | 15 lignes | **Transféré** |
| 21 | Agent unique à 10 outils pour demandes libres | A `agent.py` | E | moyenne : souple, 5 à 8 fois plus coûteux, hypothèses décisives laissées au modèle | 3 exécutions | vérificateur 5 | couplé | **Réservé** |
| 22 | Registre des sources avec niveau de lecture | C `sources.py` (30 références) ; A R07 (72) | E ; document | forte | API ; 2 liens testés sur 72 | — | socle | **C retenu** ; R07 en référence |
| 23 | Interface | C 5 étapes ; B Folio ; A laboratoire | vues toutes les trois | C : parcours guidé, verdict lisible ; B : la plus soignée, preuves et révisions ; A : fonctionnelle | navigateur | contrat | — | **C retenu** ; B réservé |
| 24 | Flux progressif de la trace | C `api.py` | E en local | bonne | étapes à 0,01 → 7,8 s | — | socle | **Retenu** |
| 25 | Déploiement Lambda, S3, Amplify, Guardrail | C `infra/` | I | potentielle (critère AWS) | aucune exécution | compte AWS | socle | **Retenu, à durcir avant exécution** |
| 26 | Certificat « demande impossible », états d'analyse | B `finance.py` | V | bonne | cas rejoués | — | comportement | **Repris comme comportement** dans la règle `donnees` de C |

Relations : 4 et 5 sont substituables ; 8 et 9 complémentaires (achat-conservation contre rééquilibrage hebdomadaire) et ne doivent pas être mêlés dans une même comparaison ; 11 et 12 équivalents en intention ; 16 et 17 substituables ; 7 et 8 portent les mêmes noms pour des conventions différentes ; 13-C et 13-B utiles à des cas différents (extraction contre détection de contradiction).

## 5. Appréciation par critère

Cotes des trois évaluateurs, recalées par la revue transversale (0 absent, 1 conçu, 2 partiel ou fragile, 3 fonctionne sur les cas, 4 robuste). L'expérience a été cotée après inspection dans un navigateur.

| Critère | A | B | C | Constat décisif |
|---|---|---|---|---|
| Adéquation au problème | 3 | 2 | 3 | B ne traite pas « dois-je acheter X ? » |
| Qualité méthodologique | 3 | 3 | 3 | A : la meilleure recherche, non intégrée ; C : formule de perte simplifiée |
| Justesse des données et calculs | 3 | 3 | 3 | tous exacts dans leur convention |
| Adaptation au profil | 2 | 1 | 3 | A : profil figé, patrimoine ignoré ; B : aucun champ de profil |
| Profondeur et fidélité de l'explication | 3 | 4 | 4 | B et C : chiffres jamais écrits par un modèle, preuve remontable |
| Utilité réelle des agents | 2 | 2 | 2 | **aucun des trois ne démontre un apport fort** : chiffres identiques avec et sans modèle chez B et C ; chez A le modèle fixe des hypothèses décisives |
| Qualité de l'expérience | 2 | 3 | 3 | B la plus aboutie ; C la plus directe |
| Cohérence architecturale | 3 (cible : 1) | 4 | 3 | B : séparation stricte et dossier transactionnel |
| Facilité et risque d'intégration | 3 | 2 | 3 | B : Store, service et flux forment un bloc POSIX |
| Fonctionnement AWS | 2 | 3 | 2 | inférence seulement pour A et C ; B ajoute la recherche AgentCore |
| Reproductibilité et exploitation | 3 | 3 | 3 | — |

**Sensibilité aux poids.** Somme pondérée sur 400, trois jeux de poids raisonnables :

| Jeu de poids | A | B | C |
|---|---|---|---|
| Proche de la grille du jury (AWS 15, adéquation 12, justesse 12, explication 12, méthode 10, agents 10, expérience 10, profil 8, reproductibilité 7, architecture 4) | 257 | 278 | **287** |
| Fusion à court délai (intégration 20, adéquation 12, profil 10, explication 10, reproductibilité 10, justesse 8, expérience 8, AWS 8, méthode 5, agents 5, architecture 4) | 269 | 257 | **297** |
| Architecture et AWS d'abord (AWS 25, architecture 15, explication 15, agents 10, expérience 10, adéquation 8, méthode 6, justesse 6, profil 5) | 250 | **302** | 280 |

Le classement change avec les poids : la note seule ne décide pas. Ce qui décide est un défaut que la note masque : **B comme socle exigerait d'y construire la représentation du profil, le moteur de règles et leur restitution**, donc l'essentiel de C, à l'intérieur d'un dossier transactionnel dont B dit lui-même que le transfert est « substantiel ». À l'inverse, ce que B apporte de plus utile à C tient en deux fichiers sans dépendance.

## 6. Stratégies examinées

| | S1 — Enrichir le socle C | S2 — Enrichir le socle B | S3 — Modules derrière des contrats communs (architecture de A) |
|---|---|---|---|
| Principe | C garde parcours, verdict, interface ; modules de B et A transférés | B garde dossier, rôles, Folio ; règles et profil de C portés dedans | nouveau squelette : dossier versionné et quatre agents de la conception de A, moteurs de B et C branchés |
| Gain | corrige le défaut de méthode de C ; prouve les appels ; risque faible | meilleure base pour révisions, reprise, recherche | architecture la plus propre à terme |
| Code neuf | adaptateur, deux composants d'interface | schéma de profil, port du Gardien en outil, claims de verdict, vues Folio nouvelles | greffier, portes, catalogue, quatre instructions système : l'essentiel |
| Risque | faible : 201 tests comme filet, bascule de retour | élevé : toucher au bloc Store-service-flux | très élevé : c'est une reconstruction |
| Coût par analyse | inchangé (8 à 14 s) | 28 s et 13 000 jetons | 15 à 35 appels estimés par A |
| Compatible avec le délai | oui | non | non |
| Verdict | **retenue** | écartée comme socle, B fournit des modules | écartée ; reste la référence pour la suite |

**Pourquoi des contributions fortes sont réservées.** Le Store de B et la recherche documentaire sont les deux manques réels du produit fusionné. Ils sont réservés parce qu'ils se transfèrent en bloc, que le corpus de B n'est pas dans l'archive, que sa recherche web a retenu une source promotionnelle et dépend de l'heure, et qu'aucun des deux n'est nécessaire au parcours commun. Le vérificateur de A est réservé parce qu'il remplit la même fonction que le contrôle d'ancrage de C, déjà relié à l'interface. L'architecture de A est réservée parce que son catalogue, ses instructions et son greffier restent à écrire.

## 7. Architecture recommandée et provenance

```
 Personne
   │  phrase libre ou profil                                              [C]
   ▼
 Interface React, 5 étapes + comparaison des 3 profils                    [C]
   │    + bloc « ton portefeuille avant / après »                         [nouveau, données B]
   │    + bloc « appels de modèle prouvés »                               [nouveau, données A]
   ▼
 API FastAPI, flux progressif                                             [C]
   ▼
 Orchestrateur à ordre fixe, en code                                      [C]
   │
   ├─ 1 QUALIFICATION   Profileur (Nova 2 Lite)                           [C]
   │      + demande impossible et actif hors univers dits clairement      [C corrigé, comportement de B]
   │      + question décisive quand une donnée manquante change le verdict [nouveau, principe de A]
   │
   ├─ 2 ANALYSE         Analyste, sans modèle
   │      mesures de l'actif seul : calculs.py                            [C]
   │      comparaison appariée avant/après : moteur historique            [B, transféré tel quel]
   │      allocation après la demande : ajout d'une part                  [A, transféré]
   │      adaptateur portefeuille.py, faits sourcés                       [nouveau : liaison]
   │
   ├─ 3 CRITIQUE        Sceptique (Claude Sonnet 5), catalogue fermé      [C]
   │      + vérification « portefeuille entier »                          [nouveau, données B]
   │      registre des sources avec niveau de lecture                     [C]
   │
   ├─ DÉCISION          Gardien, règles en code, seule autorité           [C]
   │      règle « perte supportable » jugée sur le portefeuille après     [C adapté, mesure B]
   │      grille de bascule, plus petit ajustement                        [C]
   │
   └─ 4 RESTITUTION     Rédacteur (Claude Sonnet 5) + contrôle d'ancrage  [C]
          affirme des écarts appariés, pas des niveaux                    [règle de A]

 Dossier (source de vérité d'une analyse) : faits, règles, objections, trace   [C]
     + comparaison (K3)   + appels_modele (K6)   + version_contrat             [nouveau]

 Amazon Bedrock, us-east-1 : Converse, 2 modèles                          [C]
     journal des appels : identifiant de requête, jetons, latence         [A, transféré]
 Lambda + S3 + Amplify + Guardrail : scripts durcis, exécution sur autorisation   [C, jamais exécuté]

 Références conservées intactes : implementations/claude-code (A), implementations/codex (B)
```

| Élément d'architecture | Décision |
|---|---|
| Source de vérité | le `Dossier` d'une analyse ; le contrat est `dossier.py` |
| Modèle de dossier et versionnement | un dossier par analyse, sans état serveur ; `version_contrat` ; **pas de versionnement des analyses** (compromis assumé, extension : Store de B) |
| Responsabilités | les modèles lisent, choisissent dans un catalogue et rédigent ; le code calcule, décide et contrôle |
| Contrats d'échange | K1 à K7 du cadre commun |
| Conventions financières et temporelles | CAD ; fenêtre 2021-11-12 → 2026-11-12 ; change daté au plus tard du jour ; pire baisse négative ; points de pourcentage dans le dossier |
| Moteur de calcul | deux moteurs, une autorité par grandeur (K4) ; jamais de comparaison croisée |
| Registre des preuves | faits numérotés par analyse, méthode nommant le moteur, registre des sources |
| Gestion des révisions | recalcul complet, grille de bascule pour explorer ; pas d'historique |
| Restitution | étapes existantes, tiroir de preuve, deux blocs ajoutés |
| Route AWS | Bedrock `us-east-1`, profil `alphaforge` ; modèles de C inchangés |
| Reprise et observation | aucune reprise d'analyse (durée 8 à 14 s) ; journal des appels dans le dossier ; archivage S3 si déployé |

## 8. Comportement agentique du produit fusionné

Les quatre fonctions validées sont préservées. L'organisation reste celle de C : c'est un enchaînement fixe, et je ne propose pas de le rendre plus autonome. C'est conforme à l'énoncé (« simple, focalisée et vérifiable ») mais cela laisse ouverte la question de l'apport réel des agents, que la fusion améliore peu.

| | Qualification | Recherche critique | Analyse | Restitution |
|---|---|---|---|---|
| Agent | Profileur, Nova 2 Lite | Sceptique, Claude Sonnet 5 | Analyste et Gardien, **sans modèle** | Rédacteur, Claude Sonnet 5 |
| Mission | lire la phrase, remplir seulement ce qui y est écrit | choisir 1 à 3 vérifications et formuler l'objection | produire les faits, comparer avant et après, décider | reformuler, tendre le miroir, expliquer le verdict déjà pris |
| Contexte utile | catalogue des 31 actifs, secteurs, phrase | profil, phrase, tous les faits, vérifications possibles | profil, demande, données | dossier complet, phrases de référence |
| Outils | aucun appel d'outil par le modèle | catalogue fermé exécuté par le code (6 vérifications + « portefeuille entier ») | `calculs.py`, moteur historique, règles | aucun |
| Condition d'appel | texte libre non relu | modèle disponible ; sinon vérifications par défaut | toujours | modèle disponible ; sinon gabarit |
| Sortie | JSON de champs | JSON `{code, texte}` | faits, règles, verdict, options, grille, comparaison | JSON de phrases typées reliées aux faits |
| Incertitude | champ absent → `null` → question ; **donnée décisive manquante → question décisive** | issue `confirmee`, `ecartee` ou `limite` | `disponible: false` avec raison ; règle « non évaluée » | limites affichées ; écart apparié, pas de niveau |
| Validations par le code | symbole dans l'univers, bornes, ne remplace jamais un champ rempli | code dans le catalogue, pas de nombre inventé, pas de mot de conseil | tests, monotonie, égalité des deux bras | nombres présents au dossier, citations exactes, pas de contradiction du verdict, pas de conseil ; 2 essais puis gabarit |
| Retour ou délégation | arrêt à `indetermine` si l'essentiel manque | aucune boucle entre agents | — | correction nommée renvoyée au modèle une fois |
| Évaluation comportementale | phrases annotées : champs extraits et champs laissés vides ; contradiction en texte libre | distribution des vérifications choisies sur 30 demandes (non testée aujourd'hui) | cas de réception 1 à 8 | textes fautifs refusés (écart inventé, conseil), textes justes acceptés |

Contradictions résolues entre les instructions des trois produits : A demande de « ne pas approuver ni refuser », C rend un verdict de cohérence. Le produit fusionné suit C (c'est ce que teste le persona Robert) et garde de A l'interdiction de conseiller et l'obligation de dire l'écart avec ses limites. B et C interdisent tous deux au modèle d'écrire un nombre absent du dossier : même règle, mécanisme de C. Les instructions de C sont courtes (630 à 1 360 caractères) et vérifiées par du code ; aucune raison de les allonger.

## 9. Preuve de gain attendue, compromis, non-régression

Le tableau des gains, de leur point de comparaison et de la preuve à produire est dans le cadre commun, section 11. En résumé : perte jugée sur le portefeuille entier (contre C seul et B seul) ; écarts avec leur sens et leurs limites (contre A, dont le principe n'est pas dans son produit) ; appels de modèle prouvés et visibles (contre A et C) ; demande impossible et donnée manquante traitées sans verdict trompeur (contre B et C) ; déploiement réel si vous l'autorisez.

Ce que la fusion ne fait pas mieux que le meilleur composant : révisions et reprise (B reste meilleur), recherche documentaire (B), souplesse sur demande libre (A), finesse de l'interface (B). À préserver sans régression : les 201 tests, l'identité du verdict avec et sans modèle, la monotonie de la grille, la durée, le mode hors ligne.

Risque propre au couplage : la règle « perte supportable » change de mesure avec les mêmes seuils. Le verdict d'Amira peut changer, parce que son portefeuille fictif dépasse déjà sa limite avant la demande. Le cadre prévoit une règle d'attribution, une bascule de retour (`ALPHAFORGE_CAPACITE=approximation`) et votre validation.

## 10. Plan d'intégration

| Tranche | Résultat | Provenance | Fichiers principaux | Vérification discriminante | Retour arrière |
|---|---|---|---|---|---|
| 1 Socle et contrats (seule) | branche au niveau de C évalué ; A, B, C rangés ; références figées ; champs K1, K3, K6, K7 inactifs ; 3 défauts de qualification corrigés | C `6761d66` ; comportement de B pour l'impossible | `dossier.py`, `profil.py`, `docs/`, `implementations/` | arbre identique à `6761d66` ; 201 tests ; dossiers identiques aux nouveaux champs près | étiquette `fusion/ref-avant` |
| 2 Analyse de portefeuille (parallèle) | comparaison appariée, règle de perte sur le portefeuille, question décisive | B `analytics.py`, `datasets.py` ; A `blend` | `moteurs/`, `portefeuille.py`, `gardien.py`, `analyste.py`, `orchestrateur.py` | Robert : la règle cite avant et après ; même test sous bascule retrouve 14,2 % ; monotonie | variable d'environnement ; `git revert` de la fusion |
| 3 AWS (parallèle) | journal des appels, sortie du mode hors ligne collant, déploiement durci et planifié, exécuté sur autorisation | A `_converse` ; C `infra/` | `llm.py`, `api.py`, `infra/` | identifiants de requête dans un dossier réel ; plan de déploiement ; adresse publique si autorisé | champ facultatif ; suppression des ressources listées |
| 4 Restitution et réception (seule) | deux blocs d'interface, texte en écarts appariés, dix cas, documents | règle de A ; habillage de C | `frontend/`, `redacteur.py`, `README.md`, `docs/` | dix cas attendus/observés ; captures ; tableau des gains | étiquette `fusion/t3` |

Essentiel : tranches 1, 2 (étapes A à E), 3 (étapes A à D), 4 (A à C). Extensions possibles, hors de ce plan : Store et révisions de B ; recherche documentaire ; vérificateur à références de A ; agent à outils pour demandes libres ; données ESG.

## 11. Questions de direction ouvertes

1. **Validez-vous S1** (socle C, modules de B et A) ?
2. **Publication et déploiement** : les prompts partent avec « NON » partout. Autorisez-vous le `git push` de la branche d'intégration, et la création des ressources AWS, sachant que le script actuel ouvre une adresse publique sans authentification (durcie par la tranche 3 avant toute exécution) ?
3. **Échéances** : 23 h 59 ce soir pour le dépôt, 13 h 59 demain pour le compte AWS — est-ce exact ? Si oui, la tranche 2 facultative et le déploiement sont les premiers à sacrifier.
4. **Règle de perte sur le portefeuille** : acceptez-vous que le verdict d'un persona puisse changer, ou préférez-vous que la comparaison reste un éclairage sans effet sur la règle ?
5. **Interface** : la fusion garde l'habillage de `feature/interface-parcours`. Une autre interface (`feature/yasser-interface`, poussée à 18 h 48) existe ; qui tranche ?
6. **Recherche critique** : acceptez-vous qu'elle reste, dans cette fusion, une critique outillée sans recherche documentaire ?
7. **Apport des agents** : les trois évaluations cotent 2 sur 4 ce critère, qui pèse 20 % avec l'explicabilité. La fusion ne le change pas. Voulez-vous une tranche ultérieure qui donne au Sceptique un vrai choix d'outils (transfert de l'agent de A), au prix du coût et de la variabilité mesurés chez A ?
8. **Données** : les droits de redistribution du jeu de départ ne sont établis par aucune des trois équipes ; le dépôt cible le contient. À vérifier avant de rendre le dépôt public.
