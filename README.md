# AlphaForge AI — un second avis avant d'investir

Datathon PolyFinances 2026 · Banque Nationale × AWS · défi **AlphaForge AI**.

> **Problème.** Un investisseur autonome arrive avec une envie floue ou une décision déjà en tête. Les outils
> existants le classent dans une case et lui proposent un produit. Personne ne l'aide à formuler ce qu'il veut
> vraiment, ni à vérifier si ça tient face à sa situation.
>
> **Promesse.** En 2 minutes, on reformule sa demande, on la confronte à sa situation avec des chiffres réels,
> et on lui montre exactement ce qui la rendrait acceptable, sans jamais lui dire quoi acheter.

Simulation éducative uniquement : aucune transaction réelle, aucun conseil financier personnalisé.

## Le principe

**Les chiffres viennent du code, les mots viennent des agents.** Le verdict est décidé par des règles écrites
en Python (le Gardien). Les agents comprennent la demande, choisissent les calculs, contestent les résultats et
expliquent. Chaque chiffre affiché est un fait `F-n` relié à sa source et à sa méthode, étiqueté
`FAIT`, `HYPOTHESE` ou `SCENARIO`.

## Le parcours

1. **Dis-le avec tes mots** : une phrase libre (« Je veux… J'ai… Mais j'ai peur de… ») ou une persona.
2. **On vérifie ensemble** : champs pré-remplis, curseurs, 1 mise en situation + 3 questions → 2 jauges
   (tolérance et capacité, on retient la plus basse).
3. **Analyse en direct** : la trace des agents défile.
4. **Le verdict** : 4 états (cohérent / avec ajustement / incohérent / impossible de conclure), 3 options
   comparées, miroir de cohérence, faits cliquables.
5. **Curseurs de bascule** : le verdict change en direct quand on bouge le montant ou l'horizon. Fiche à
   apporter à son conseiller.

## Architecture

Ce qui tourne aujourd'hui (local + Amazon Bedrock) :

```
Interface React + Vite (frontend/, lancée en local)
   │  POST /api/analyse, /api/comprendre
   ▼
API FastAPI (backend/api.py)
   │
Orchestrateur en code (ordre fixe) ── dossier de décision partagé (faits F-1…F-n, trace)
   Profileur (Nova 2 Lite) → Contrôle données (code) → Analyste (code) → Sceptique (Claude Sonnet 5)
   → Gardien (code, décide) → Rédacteur (Claude Sonnet 5) → contrôle d'ancrage (code)
   │
   ▼
Outils de calcul Python (calculs.py) ── jeu de départ officiel (data/raw/alphaforge_starter)
```

Visé, **pas encore en place** : déploiement de l'API (Lambda ou AgentCore Runtime), interface sur Amplify ou
S3 + CloudFront, données sur S3, Bedrock Guardrails en plus du contrôle d'ancrage en code. Voir [infra/](infra/).

| Agent | Nature | Rôle |
|---|---|---|
| Profileur | LLM léger | Structure la demande et le profil, repère ce qui manque et les tensions |
| Contrôle données | Code | 7 contrôles avant tout calcul (fiche qualité) |
| Analyste | Code | Appelle les calculs, écrit les faits F-n (pas de modèle pour l'instant) |
| Sceptique | LLM | 1 à 3 objections, chacune liée à un fait et à un recalcul |
| Gardien | Code | Règles explicites → verdict, plus petit ajustement, grille de bascule |
| Rédacteur | LLM | Explique sans rien ajouter, chaque phrase étiquetée |

Service AWS utilisé aujourd'hui : **Amazon Bedrock** (API Converse, profils d'inférence `global.*`, région
us-east-1). Services visés : Bedrock Guardrails, Bedrock AgentCore Runtime ou AWS Lambda, Amazon S3, AWS Amplify.

### Les agents sur Amazon Bedrock

| Agent | Modèle | Ce que le code vérifie |
|---|---|---|
| Profileur | Nova Lite | Le symbole existe, les nombres sont plausibles, les secteurs existent ; seuls les champs vides sont remplis |
| Sceptique | Claude Sonnet | Il ne peut choisir que parmi 6 vérifications autorisées, que le code exécute ; objection sans chiffre inventé |
| Rédacteur | Claude Sonnet | Chaque nombre du texte existe déjà dans le dossier (la phrase libre n'autorise aucun nombre), chaque F-n cité existe, citations mot pour mot, aucune formule de conseil, pas de contradiction avec le verdict ; le code corrige les étiquettes FAIT / HYPOTHESE / SCENARIO et l'écrit dans le journal ; « ce qui changerait l'avis » est écrit par le code |

Si le texte du Rédacteur échoue au contrôle, le défaut est **nommé** et renvoyé au modèle pour un second essai ;
s'il persiste, on garde les phrases modèles. Tout est visible dans la trace et sous « Comment ce texte a été vérifié ».

Sans identifiants AWS, chaque agent bascule sur sa version déterministe : la démo marche toujours.
`ALPHAFORGE_LLM=off` force le mode hors ligne (utilisé par les tests).

## Démarrer

Prérequis : **Python 3.12 ou plus** (testé avec 3.14.7) et **Node.js 20 ou plus** (testé avec 24.20.0, npm 11.19).
Les versions des dépendances sont figées dans `backend/requirements.txt` et `frontend/package-lock.json`.
Sans identifiants AWS, tout fonctionne en mode hors ligne (verdicts identiques, textes rédigés par le code).

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate   ·   macOS/Linux : source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
pytest -q                                  # banc de tests (hors ligne, aucun appel à Bedrock)
# Agents IA : le profil AWS doit être fixé AVANT de lancer l'API, sinon tout passe en mode hors ligne.
#   PowerShell : $env:AWS_PROFILE="datathon"; $env:AWS_REGION="us-east-1"
#   bash       : export AWS_PROFILE=datathon AWS_REGION=us-east-1
uvicorn api:app --reload --port 8000       # API locale : http://localhost:8000/docs
cd ../frontend && npm install && npm run dev   # interface : http://localhost:5173
```

Sous Windows, après l'installation : `.\demarrer.ps1` lance l'API, l'interface et le navigateur.

Agents IA : coller le bloc « Windows (PowerShell) » de Workshop Studio dans un terminal, puis
`.\infra\enregistrer_identifiants.ps1` (profil `datathon`, région `us-east-1`). Vérifier avec
`python backend/verifier_bedrock.py`.

## Données

Jeu de départ officiel dans [data/raw/alphaforge_starter/](data/raw/alphaforge_starter/) : 31 actifs, prix
quotidiens du 2021-11-12 au 2026-11-12 (Yahoo Finance via yfinance), USD/CAD et taux (Banque du Canada),
séries américaines (FRED). Sources, traitements et limites : [README du jeu](data/raw/alphaforge_starter/README.md)
et [docs/donnees.md](docs/donnees.md).

## Organisation

| Voie | Propriétaire | Dossier |
|---|---|---|
| Produit, parcours, interface, pitch | Yahia | `frontend/`, `pitch/` |
| Données et calculs | Rayan | `backend/alphaforge/donnees.py`, `calculs.py` |
| Agents, consignes, architecture | Adam | `backend/alphaforge/agents/`, `orchestrateur.py`, `llm.py` |
| Gardien, AWS, tests | Yasser | `backend/alphaforge/gardien.py`, `profil.py`, `infra/`, `backend/tests/` |

Règles Git : `main` marche toujours, une branche par sujet (`feature/nom-court`), commits au format
Conventional Commits, petites PR avec 1 approbation. Contrats communs : [docs/contrats.md](docs/contrats.md).
Plan complet : [docs/plan.md](docs/plan.md).

## Implémentation Codex indépendante pour la fusion

L’implémentation Codex (Folio, dossier de décision versionné, recherches et tests) est conservée dans [`implementations/codex/`](implementations/codex/IMPORT.md). Elle est importée séparément pour comparaison et intégration ultérieure; l’application à la racine reste distincte.
