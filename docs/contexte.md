# Contexte complet du projet (passation)

> **À lire en premier** par toute nouvelle session Claude et par chaque membre de l'équipe.
> Mis à jour le 2026-11-14 vers 23 h 45. Il rassemble tout ce qui a été décidé et construit jusqu'ici.
> Pour reprendre : lire ce fichier, puis `README.md`, `docs/plan.md`, `docs/contrats.md`.

---

## 1. Le défi

**Datathon PolyFinances 2026 · Banque Nationale × AWS · défi « AlphaForge AI ».**
Concevoir une **solution agentique auto-explicative** qui exploite des données financières publiques pour éclairer
une décision d'investissement selon différents profils. Les actifs, les outils et l'architecture sont libres.
« AlphaForge AI » est le nom du **défi** ; aucun nom de solution n'est imposé (on garde « AlphaForge AI » + sous-titre
« Second avis »).

### Les 3 personas (énoncé officiel)

| Persona | Profil | Ce qu'elle teste |
|---|---|---|
| **Amira**, 26 ans, ingénieure logicielle | Risque **élevé**, horizon **15 ans et plus**, expérience intermédiaire. IA, technologies émergentes, cryptoactifs, mais veut rester diversifiée | « Risque élevé » ne veut pas dire « tout est acceptable » ; garder une diversification cohérente |
| **Mateo**, 41 ans, gestionnaire des opérations, 2 enfants | Risque **modéré**, horizon **8 à 12 ans**, expérience intermédiaire. ESG important, éviter les controverses environnementales et sociales, équilibre croissance / stabilité, peu intéressé par le spéculatif | Intégrer autre chose que rendement et risque : ses préférences personnelles |
| **Robert**, 59 ans, professionnel de la santé, retraite proche | Risque **faible à modéré**, horizon **3 à 5 ans**, expérience avancée. Préserver le capital, entreprises établies, peu intéressé par la crypto, **tenté par une entreprise très médiatisée** | Remettre en question une demande incohérente avec le profil, expliquer les risques, ne pas acquiescer automatiquement |

### Grille d'évaluation

| Critère | Poids |
|---|---|
| Qualité, pertinence et innovation de la solution | 20 % |
| Intelligence agentique et explicabilité | 20 % |
| Capacité d'analyse et traitement des données | 20 % |
| Expérience utilisateur (UX/UI) | 10 % |
| Qualité de l'intégration AWS | 15 % |
| Présentation, valeur business et marketing | 15 % |

**AWS est une condition d'admissibilité** : il doit contribuer réellement et de façon démontrable au fonctionnement.
Sans intégration effective, le projet n'est pas évalué en finale.

### Livrables

1. **Prototype + code** : un cas d'utilisation complet et démontrable ; dépôt avec README (dépendances, données,
   configuration, reproduction).
2. **Vidéo** d'environ 5 min : problème, rôle des agents, données et outils, résultat, explication. Deux situations
   d'investisseurs distinctes peuvent illustrer l'adaptation.
3. **Documentation technique** : méthodes et justification ; sources, actifs, traitements, hypothèses ; mécanisme
   d'explicabilité avec un exemple qui relie une conclusion aux données ou aux traces ; validations, limites, améliorations.
4. **One-pager** : problème, approche agentique, originalité, sources, explicabilité, bénéfices.

### Cadre responsable

Simulation uniquement, aucune transaction réelle, aucun conseil financier personnalisé, aucune donnée bancaire.
Distinguer **faits, hypothèses et scénarios fictifs** ; présenter les incertitudes ; explications fidèles aux sources et
aux actions observables, sans justification inventée. Le passé ne prédit pas le futur : ne pas assimiler un profil à
un actif de façon automatique. Pistes suggérées par l'énoncé : un agent d'explicabilité, un agent de gouvernance qui
vérifie les contraintes et rend les contrôles visibles.

### Échéances (critiques)

| Quand | Quoi |
|---|---|
| Dimanche 15 nov., 23 h 59 | GitHub + application |
| Lundi 16 nov., 13 h 59 | **Comptes AWS détruits** (enregistrer la vidéo AVANT, pendant que l'app tourne) |
| Lundi 16 nov., 14 h | Vidéo, one-pager, documentation technique |

### Données

Jeu de départ officiel dans `data/raw/alphaforge_starter/` : 31 actifs (10 actions CA, 10 actions US, 9 FNB dont
**ESGV** filtré ESG, BTC, ETH), prix quotidiens **2021-11-12 → 2026-11-12** (inclut 2022, actions et obligations en
baisse ensemble), USD/CAD et taux (Banque du Canada), séries US (FRED). Énergie : ENB, CNQ, XOM (pour Mateo).
TSLA et NVDA : titres médiatisés et volatils (pour Robert). Pièges : utiliser `adj_close` ; titres `.TO` en CAD, le
reste en USD ; calendriers non alignés (crypto 7 j/7) ; macro datée au mois de référence, pas à la publication ;
biais du survivant ; **aucune donnée ESG ni nouvelle** incluse (à sourcer si on en ajoute).

---

## 2. L'équipe

| Membre | Rôle proposé | Vision (questionnaire de cadrage) | Peur → garde-fou |
|---|---|---|---|
| **Yahia** | Produit, parcours, interface, pitch, vidéo | Traducteur d'intentions : aider une personne perdue à formuler une demande claire et réaliste, à apporter à son conseiller (service « pré-rendez-vous ») | Trop complexe, pas assez créatif → **un seul moment signature, très soigné** |
| **Rayan** | Données et calculs | Le convaincant : réponse rapide (< 2 min) qui convainc avec les mots de la personne | Ne pas convaincre → **chaque verdict cite une phrase de la personne et un montant en $** |
| **Yasser** | Gardien, AWS, tests, intégration (à confirmer) | Second avis strict : verdict à 4 états, 3 choix, point de bascule ; « le code décide, l'IA explique » | Pas de démo de bout en bout → **squelette d'abord, gel dimanche 16 h** |
| **Adam** | Agents, consignes, architecture | Méthodique : clarifier puis comparer, ne demander que l'info utile, chaque conclusion vérifiable | Impressionnant mais générique → **test anti-générique : changer de persona doit changer le texte** |

Le dépôt GitHub appartient à Yasser. Le plan d'attaque complet (schémas des 4 visions, matrice des réponses) :
artifact **https://claude.ai/artifact/U4F45ZdsweHSkxKQehYh8k** (privé, à partager depuis son menu « Partager »)
et copie hors ligne dans [docs/plan-attaque.html](plan-attaque.html). Réponses brutes au questionnaire : sur
l'ordinateur de Yahia (`Desktop/datathon2026PF/reponses_equipe.md`), volontairement pas dans ce dépôt public.

---

## 3. Ce qui est décidé (plan d'attaque)

**Problème.** Un investisseur autonome arrive avec une envie floue ou une décision déjà en tête. Les outils existants
le classent dans une case et lui proposent un produit. Personne ne l'aide à formuler ce qu'il veut vraiment, ni à
vérifier si ça tient face à sa situation.

**Promesse.** En 2 minutes, on reformule ta demande, on la confronte à ta situation avec des chiffres réels, et on te
montre exactement ce qui la rendrait acceptable, sans jamais te dire quoi acheter.

**Phrase de pitch.** « AlphaForge AI, un second avis qui sait dire non, avec des preuves. »

### Décisions unanimes ou tranchées

- On sert **l'investisseur lui-même** ; fiche « pour ton conseiller » en bonus (idée de Yahia, angle Banque Nationale).
- **Clarifier puis confronter** : reformulation rapide, puis verdict chiffré.
- **Entrée** : phrase libre (amorces « Je veux… / J'ai… / Mais j'ai peur de… ») + champs pré-remplis corrigeables
  (« Voici ce que j'ai compris de toi »).
- **Profil** : curseurs, jamais de case ; **2 jauges** tolérance / capacité, on retient la plus basse (Réformes axées
  sur le client, ACVM / OCRCVM).
- **Psychologie** : 1 mise en situation + 3 questions inspirées de **Grable & Lytton (1999)** ; jamais de diagnostic ;
  on nomme un effet de mode avec des mots factuels.
- **Agents** : Profileur, Analyste, Sceptique, Rédacteur (LLM) + Contrôle données et **Gardien** (code).
- **Coordination** : orchestrateur **en code**, ordre fixe, dossier de décision partagé, renvois limités.
- **Débat** : contradiction outillée ; le Sceptique cite un F-n et force une vérification ; le Gardien arbitre.
- **Désaccord non résolu** : préférence manquante → question à la personne ; problème de données → recalcul ; doute
  restant → « non vérifié », gris si essentiel ; la capacité de perte n'est jamais négociable.
- **Verdict en 4 états** : cohérent / cohérent avec ajustement / incohérent / impossible de conclure (gris) ;
  « X règles respectées sur Y » (pas de % de compatibilité).
- **3 options** : ta demande / version ajustée (ou alternative compatible avec tes valeurs) / ne rien changer.
- **Moment signature** : **curseurs de bascule** en direct + **miroir de cohérence** (ses mots face aux chiffres).
- **Ton** : neutre, clair, tutoiement, jamais « achetez ». Français.

### Ce qu'on a laissé tomber (et ce qui le remplace)

API de nouvelles en direct (→ décrite par la personne) · probabilité d'atteindre l'objectif (→ trop prédictif) ·
NASA-TLX (→ mesure la charge mentale, pas le risque) · questionnaire complet de 13 questions (→ 3) · chef
d'orchestre IA et pair-à-pair libre (→ orchestrateur en code) · 6 agents LLM (→ 4 + 2 en code) · chatbot libre ·
3 seaux de Chhabra comme format (→ champ « somme à préserver ») · bilingue · « % de compatibilité ».

### Script de démo (3 min)

0:00 le problème, Robert écrit sa demande · 0:30 « Voici ce que j'ai compris », il corrige un curseur · 0:50 la trace
défile, le Sceptique objecte · 1:30 verdict, miroir, version ajustée · 2:00 il bouge un curseur, le verdict change ·
2:20 même demande pour Amira et Mateo (vue Comparer) · 2:45 fiche pour le conseiller, phrase de fin.

### Leçons de l'atelier « De la consigne au pipeline qui se corrige » (appliquées)

Consigne qui nomme le cas (`CLAUDE.md`) · agent aux outils bornés (Sceptique) · ce qui se compte sort du modèle
(`calculs.py`) · garde-fou qui **empêche** (contrôle d'ancrage) · personne ne note son propre plat (le code valide le
Rédacteur, le Gardien décide) · le **défaut nommé** devient la consigne de l'essai suivant (boucle du Rédacteur).

---

## 4. Ce qui est construit (état au 14 nov., 23 h 45)

### Architecture

```
Interface React + Vite (frontend/)  ──  POST /api/analyse, /api/comprendre, GET /api/serie, /api/sante…
   │
API FastAPI (backend/api.py)
   │
Orchestrateur en code (backend/alphaforge/orchestrateur.py) — dossier de décision partagé (dossier.py)
   Profileur ─▶ Contrôle données ─▶ Analyste ─▶ Sceptique ─▶ Gardien ─▶ Rédacteur (+ contrôle d'ancrage)
   │
Outils de calcul (calculs.py, donnees.py) sur data/raw/alphaforge_starter
```

| Fichier | Rôle |
|---|---|
| `backend/alphaforge/donnees.py` | Chargement, conversion en CAD (taux BdC), 7 contrôles qualité |
| `backend/alphaforge/calculs.py` | Pire chute, récupération, volatilité, rendement annualisé, pire 12 mois, corrélation hebdo |
| `backend/alphaforge/profil.py` | 3 questions Grable & Lytton, barème de capacité, perte max, seuil de concentration (**hypothèses de l'équipe, à valider par Yasser**) |
| `backend/alphaforge/gardien.py` | 8 règles → verdict 4 états, plus petit ajustement, grille de bascule (montant × horizon) |
| `backend/alphaforge/agents/profileur.py` | Lit la phrase (Nova Lite), le code valide, ne remplit que les champs vides ; tensions (effet de mode, écart tolérance/capacité) |
| `backend/alphaforge/agents/analyste.py` | Appelle les calculs, écrit les faits F-n ; `mesures_actif()` réutilisable |
| `backend/alphaforge/agents/sceptique.py` | Claude choisit 1 à 3 vérifications parmi un **catalogue de 6**, exécutées par le code |
| `backend/alphaforge/agents/redacteur.py` | Claude rédige ; le code refuse tout nombre absent du dossier, F-n inexistant, mot de conseil ; défaut nommé → 2e essai → sinon phrases modèles |
| `backend/alphaforge/orchestrateur.py` | Ordre fixe ; options ; **alternative** compatible avec les exclusions (ESGV, XIU.TO, XBB.TO, FTS.TO) |
| `backend/alphaforge/llm.py` | Bedrock Converse, repli hors ligne automatique, `ALPHAFORGE_LLM=auto/bedrock/off` |
| `backend/alphaforge/personas.py` | Les 3 personas ; **montants fictifs** (épargne, somme à préserver, demandes) |
| `frontend/src/etapes/*.jsx` | Les 5 étapes + vue Comparer (voir `frontend/README.md`) |
| `backend/tests/` | 11 tests (hors ligne) ; `pytest -q` depuis `backend/` |

### Règles du Gardien

Rouge : capacité de perte dépassée · somme à préserver entamée · exclusion violée · retrait prévu avant récupération
sur actif volatil. Orange : impact au-delà de la tolérance (mais dans la capacité) · horizon plus court que le temps
de récupération observé · concentration au-delà du seuil (actif volatil > 30 %/an) · pas de fonds d'urgence ·
corrélation ≥ 0,8 avec le portefeuille. Gris : horizon, épargne, montant ou tolérance manquants, ou données en échec.

### Résultats actuels (montants fictifs)

| Persona | Demande | Verdict | Raison | Option |
|---|---|---|---|---|
| Amira | 10 000 $ en Bitcoin (25 % de 40 000 $) | Cohérent avec ajustement | Concentration > 20 % | 7 500 $ → cohérent |
| Mateo | 15 000 $ dans Enbridge | Incohérent | Exclusion Énergie | Alternative ESGV → cohérent |
| Robert | 80 000 $ dans Tesla (20 % de 400 000 $) | Cohérent avec ajustement | Concentration > 5 % ; effet de mode signalé | 16 000 $ → cohérent |

**Question ouverte** : Robert n'est pas « Incohérent » (perte potentielle 14,2 % de l'épargne, juste sous sa limite
de 15,5 %). Décider avec Yasser s'il faut ajuster les montants fictifs ou les seuils, **sans tricher sur les règles**.

### Lancer

Voir `README.md`. Sous Windows : `.\demarrer.ps1` (API sur :8000, interface sur :5173). Une analyse avec Bedrock
prend 10 à 20 s. Sans clés AWS, tout marche en mode hors ligne (indicateur en haut de l'écran).

---

## 5. AWS et Bedrock

- Compte d'équipe Workshop Studio, **région us-east-1**, valide jusqu'au lundi 16 nov. 13 h 59.
- Identifiants **temporaires** dans `~/.aws/credentials`, profil `datathon`. Pour les renouveler : coller le bloc
  « Windows (PowerShell) » de Workshop Studio dans un terminal, puis `.\infra\enregistrer_identifiants.ps1`.
  **Ne jamais coller de clés dans le dépôt ni dans le chat.** Vérifier : `python backend/verifier_bedrock.py`.
- Modèles : `global.anthropic.claude-sonnet-5` (Sceptique, Rédacteur), `global.amazon.nova-2-lite-v1:0` (Profileur).
  `global.anthropic.claude-sonnet-5.5` existe aussi sur le compte (non testé).
- Pièges rencontrés :
  - Claude Sonnet 5 **refuse le paramètre `temperature`** → on ne l'envoie qu'aux autres modèles ;
  - lire **tous** les blocs texte d'une réponse Converse (certains modèles renvoient d'abord un raisonnement) ;
  - le message d'erreur de Starlette suggérait `pip install httpx2` : **refusé**, ce n'est pas le paquet officiel
    (`httpx`) ; risque de paquet piège.
- Quotas lus sur le compte : Claude Sonnet 5 = 6 M tokens/min ; Nova 2 Lite = 2 000 requêtes et 8 M tokens/min.
  Pas de fenêtre de 5 h comme sur un abonnement Claude : facturation au token sur le compte de l'événement.
- **Claude Code payé par AWS** : `.claude/settings.local.json` (non versionné) contient
  `CLAUDE_CODE_USE_BEDROCK=1`, `AWS_REGION=us-east-1`, `AWS_PROFILE=datathon`,
  `ANTHROPIC_MODEL=global.anthropic.claude-sonnet-5`. Une session ouverte dans ce dossier passe par Bedrock
  (`/status` pour vérifier).
- **Déploiement** : script prêt sur la branche `Yasser` (`infra/deployer.py`, voir `infra/README.md`), testé sur un AWS
  simulé, **pas encore lancé sur le vrai compte**. Il crée S3, un rôle IAM, une Lambda + Function URL et l'interface sur Amplify.

---

## 6. Git

- Dépôt **public** : https://github.com/YasserJJJJ/POLYFINANCE-DATATHON-2026
- `main` : projet de base. `feature/interface-parcours` : tout le travail de Yahia (interface, agents Bedrock,
  garde-fous, nom AlphaForge AI). **Pull request à ouvrir** :
  https://github.com/YasserJJJJ/POLYFINANCE-DATATHON-2026/pull/new/feature/interface-parcours
- Branche `Yasser` (créée depuis `feature/interface-parcours`, 15 nov.) : interface remise au style de la maquette
  validée (fond blanc, logo en V violet, bandeau de verdict teinté) et banc de 12 cas du Gardien. Aucun contrat ni seuil modifié.
- Règles (guide d'équipe) : `main` marche toujours ; une branche par sujet `feature/nom-court` ; Conventional
  Commits ; petites PR avec 1 approbation ; jamais de `.env`, de clé ni de données confidentielles.

---

## 7. Prochaines étapes (par priorité)

1. **Déployer sur AWS** (admissibilité + 15 % de la note + URL pour la vidéo) : API sur Lambda (Function URL ou API
   Gateway) ou AgentCore Runtime ; interface sur S3 + CloudFront ou Amplify ; données dans S3. Garder le repli hors ligne.
2. **Bedrock Guardrails** : ancrage contextuel + sujet refusé « conseil d'achat », en plus du contrôle en code.
3. **Fusionner la PR** dans `main` après relecture d'un coéquipier.
4. ~~**Banc de 12 cas** (Yasser)~~ **Fait sur la branche `Yasser`** : `backend/tests/test_banc_12_cas.py` (12 cas persona ×
   demande avec verdict et règles attendus, monotonie montant et horizon, stabilité, test anti-générique, preuves citées,
   aucun mot de conseil). Les résultats attendus suivent les seuils actuels de `profil.py` (hypothèses à valider).
5. **Trancher** : seuils du Gardien, cas Robert, 3 questions et mise en situation définitives.
6. **Données (Rayan)** : source ESG documentée pour les exclusions ; fréquence historique (bonus).
7. **Livrables** : documentation technique (sections exigées, exemple de trace), one-pager, script vidéo ;
   enregistrer la vidéo **dimanche soir**.

---

## 8. Références

- Énoncé officiel : `Datathon2026/Datathon - Case Officiel 2026 FR.pdf` (hors dépôt, sur les postes de l'équipe).
- Aide-mémoire de l'atelier AWS ; atelier finance « Comprendre l'investisseur avant de bâtir la solution » (BN).
- Inspirations : TradingAgents (débat haussier/baissier), FinRobot, exemples Bedrock/Strands d'AWS ;
  plugins finance d'Anthropic (`anthropics/financial-services`, Apache 2.0) : *prospect-intake* (≈ pré-rendez-vous),
  *compliance* (relecture avant envoi), agent *holdings-sanity* (7 contrôles qualité), règle « lu vs déduit ».
- Théorie : Grable & Lytton (1999), échelle de tolérance au risque ; Chhabra (2005), *Wealth Allocation Framework* ;
  ACVM, Réformes axées sur le client (tolérance vs capacité).
