# AlphaForge AI — un second avis avant d’investir

Datathon PolyFinances 2026 · Banque Nationale × AWS · simulation éducative, sans transaction ni conseil financier personnalisé.

AlphaForge confronte une demande d’investissement à la situation déclarée de la personne. Le Gardien en Python décide du verdict. Le portefeuille entier est comparé avant et après l’ajout demandé, sur les mêmes données historiques. Les modèles comprennent, contestent et expliquent ; ils ne décident ni des chiffres ni des règles.

## Parcours

1. **Tes mots** : demande libre ou persona fictive.
2. **On vérifie** : épargne, horizon, retrait, exclusions, tolérance et portefeuille. Poids facultatifs ; sans poids, l’équipondération est une hypothèse affichée.
3. **Analyse** : six rôles, leurs durées et les appels Bedrock réellement constatés (modèle, identifiant, jetons, latence). Sur Lambda, les étapes peuvent arriver ensemble.
4. **Verdict** : cohérent, avec ajustement, incohérent ou impossible de conclure. Questions décisives, options et comparaison avant/après avec preuves cliquables.
5. **Curseurs** : chaque case est calculée indépendamment. Une demande diversifiante peut donner un meilleur verdict pour un montant supérieur ; c’est un constat de règle, jamais une recommandation. La fiche conseiller conserve la demande initiale et ses limites.

Les trois personas et leurs poids sont des scénarios fictifs validés par le porteur : Robert, un tiers de XIU.TO, XBB.TO et RY.TO ; Amira, moitié QQQ et NVDA ; Mateo, moitié XIU.TO et XBB.TO.

## Installation

Python 3.12 ou plus, Node.js 20 ou plus. Tests locaux de fusion sous Python 3.13 et Node 22 ; Lambda sous Python 3.12. Dépendances déclarées dans `backend/requirements.txt` et verrouillées côté interface. Depuis la racine :

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
npm ci --prefix frontend
```

Sous Windows PowerShell, remplacer les deux premières lignes par :

```powershell
py -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

## Démarrer hors ligne — deux terminaux

macOS et Linux, une commande dans chacun :

```sh
ALPHAFORGE_LLM=off backend/.venv/bin/python -m uvicorn api:app --app-dir backend --port 8000
```

```sh
npm run dev --prefix frontend
```

Windows PowerShell, une commande dans chacun :

```powershell
$env:ALPHAFORGE_LLM="off"; .\backend\.venv\Scripts\python.exe -m uvicorn api:app --app-dir backend --port 8000
```

```powershell
npm run dev --prefix frontend
```

Ouvrir http://localhost:5173. L’API écoute sur http://localhost:8000. `demarrer.ps1` reste disponible ; il n’est pas requis. Les commandes Windows sont documentées, non exécutées pendant cette réception macOS.

## Amazon Bedrock et hébergement

Pour activer les modèles, configurer des identifiants temporaires valides dans le profil AWS **alphaforge**, puis lancer l’API avec `AWS_PROFILE=alphaforge`, `AWS_REGION=us-east-1` et `ALPHAFORGE_LLM=auto`. Aucun identifiant ne va dans Git. Sous PowerShell, définir ces variables avec `$env:NOM="valeur"` avant la commande API.

- Profileur : `global.amazon.nova-2-lite-v1:0`.
- Sceptique et Rédacteur : `global.anthropic.claude-sonnet-5`.
- Le contrôle d’ancrage vérifie nombres, faits, citations, étiquettes et absence de conseil. Un refus persistant rend le gabarit en code.
- `ALPHAFORGE_GUARDRAIL_ID` et `ALPHAFORGE_GUARDRAIL_VERSION` activent le Guardrail supplémentaire du Rédacteur.
- Sans accès AWS, repli déterministe. `ALPHAFORGE_LLM=off` évite tout appel SDK ; les preuves d’appels sont alors vides.

L’agent intégrateur de cette fusion utilise séparément Astra sur Bedrock ; cela ne change pas les modèles du produit.

Interface : https://main.d1d3b8g2y5hkdd.amplifyapp.com
API : https://ldk3ad4p3grqn3ppbcosvznivm0plyck.lambda-url.us-east-1.on.aws/

Amplify sert l’interface ; Lambda/Mangum sert FastAPI ; S3 conserve les données et dossiers en privé. IAM restreint les accès et CloudWatch reçoit les journaux. La Function URL est publique ; la concurrence est bornée à deux. L’inventaire, les commandes d’arrêt et les limites sont dans [la réception AWS](docs/fusion/preuves/tranche3/RESSOURCES.md) et [le compte rendu final](docs/fusion/COMPTE-RENDU.md).

L’hébergement dépend du compte de l’événement, dont la fermeture est annoncée le 16 novembre à 13 h 59 dans les documents d’équipe. Les preuves restent dans Git. La latence et les jetons mesurés ne sont pas des garanties de service.

## Vérifier

```sh
cd backend
ALPHAFORGE_LLM=off .venv/bin/python -m pytest -q
```

Puis, depuis la racine : `npm run build --prefix frontend`. Sous Windows, utiliser le Python du venv et `$env:ALPHAFORGE_LLM="off"`.

[Réception T4](docs/fusion/preuves/tranche4/README.md) : dix cas métier, références figées, appels réels et comparaison objet à objet. Le contrôle React statique est reproductible avec `node frontend/verifier_restitution.mjs` après les captures. Il ne constitue pas une inspection visuelle : celle-ci est signalée séparément dans le compte rendu.

Bascule de comparaison avec l’ancien comportement : `ALPHAFORGE_CAPACITE=approximation`. Elle conserve les seuils et suppose le reste de l’épargne stable. Par défaut, la perte supportable se juge sur le portefeuille après la demande ; cette attribution a été arbitrée par le porteur.

## Provenance

- **C — Second avis / Yahya** : parcours React, dossier et faits, Profileur, Sceptique, Gardien, Rédacteur, calculs d’actif seul, infrastructure et tests du socle.
- **B — Folio, archive 0.7.0** : moteur historique `analytics.py` et `datasets.py`, avec ses tests et conventions de séances communes. Le versionnement de dossiers et la recherche documentaire de B ne sont pas intégrés.
- **A — Claude Code** : fonction `blend` d’ajout proportionnel, collecte des métadonnées Converse et principe d’une comparaison appariée explicitant son sens et ses limites.

Les originaux sont préservés. [Références, archives et empreintes](implementations/REFERENCES.md), [cadre de fusion](docs/fusion/CADRE-COMMUN.md) et [compte rendu](docs/fusion/COMPTE-RENDU.md) détaillent les transferts et adaptations. `implementations/codex/` est une copie antérieure plus large ; les transferts B proviennent de l’archive 0.7.0 vérifiée.

## Données et méthode

Le jeu officiel comprend 31 actifs sur 2021-11-12 → 2026-11-12 : prix Yahoo Finance via yfinance, change Banque du Canada. Les séries FRED et macro fournies ne servent pas aux décisions. Univers choisi en 2026, fenêtre courte incluant 2022, prix ajustés, achat-conservation et échantillonnage des cryptoactifs limitent l’interprétation. Aucune pire baisse passée ne borne une perte future.

[Contrats K1–K7](docs/contrats.md) · [Données et deux moteurs](docs/donnees.md) · [Registre des sources](docs/sources.md) · [Documentation technique du défi](docs/documentation-technique.md).
