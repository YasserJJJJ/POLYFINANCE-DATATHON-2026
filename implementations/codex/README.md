# AlphaForge — dossiers de décision à quatre agents

> **Folio est intégré :** [ouvrir l’application](http://127.0.0.1:8768/), [parcours et captures](docs/folio/README.md), [matrice de réalisation](docs/folio/MATRICE.md), [revue indépendante](docs/folio/REVUE.md). Le prototype choisi est conservé dans `artifacts/folio_reference/`.

**Double-cliquer `Ouvrir_AlphaForge.command`.** Le lanceur ouvre le parcours
actuel et réutilise son serveur local. L'adresse de cette livraison est
http://127.0.0.1:8768 ; le lanceur conserve ce port et signale un conflit au lieu de sonder les autres réalisations.

Le système transforme une demande fictive en dossier versionné : qualification,
recherche de preuves, calcul contrôlé, puis restitution. Les quatre rôles
effectuent des appels distincts à Amazon Bedrock. Les résultats financiers
proviennent d'outils Python ; les agents ne génèrent pas les montants affichés.

## Essayer le parcours

1. Charger **Robert** ou **Amira**. Les exemples remplissent des entrées
   fictives modifiables ; ils ne fournissent aucune conclusion aux agents.
2. Lancer le parcours avec AWS. L'activité montre les quatre contributions et
   les requêtes réellement effectuées. Un passage consomme le compte AWS atelier.
3. Lire la conclusion, ses conditions, les preuves et les artefacts du dossier.
4. Pour Robert, modifier le retrait de **30 000 à 40 000 CAD**. L'ancienne vue
   cesse immédiatement d'être courante. L'historique montre les résultats
   invalidés, les pièces réutilisées et la nouvelle analyse.
5. Exporter le JSON ou rouvrir le dossier depuis la liste. Une erreur de
   service conserve la trace ; **Reprendre** poursuit le run interrompu.

Les dossiers de démonstration conservés peuvent être consultés sans nouvel
appel de modèle :

- [Robert, retrait puis budget de perte révisés](http://127.0.0.1:8768/?dossier=4089e4b0d70f40b6b20d832fa261e1dc)
- [Amira, comparaison historique](http://127.0.0.1:8768/?dossier=f281a9067e4544138fa178fa4ee0b850)
- [Retrait impossible, certificat sans allocation](http://127.0.0.1:8768/?dossier=1f7d3a73d5924a09ba73925655dce389)
- [Demande incomplète, questions ouvertes](http://127.0.0.1:8768/?dossier=e6405c6c61f64c5b89c11262ce9b9669)

La version **0.7.0** intègre Folio et conserve la revue indépendante du Prompt 5.
Le [dossier de défense](docs/defense/README.md) documente les défauts reproduits,
les corrections et les contre-exemples. Les nombres examinés ont été
reproduits indépendamment ; une référence simple atteint aussi le minimum de
Robert. Aucune supériorité financière des quatre agents n’est revendiquée.

Le mode sans AWS est un **bras de contrôle déterministe**, explicitement
étiqueté. Il permet d'essayer les calculs et le dossier ; il ne démontre pas
quatre inférences de modèle.

## Lancer ou restaurer

Environnement vérifié : macOS, Python 3.15.2, versions dans `requirements.txt`.
Le calcul et la consultation locale n'exigent pas de connexion AWS.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/launch.py
```

Le lanceur écoute uniquement sur `127.0.0.1:8768` et ne ferme pas les autres applications. Son état est `runtime/server.json`.
La route applicative est le profil `alphaforge`, compte atelier contrôlé par
STS, entrée `us-east-1`, modèle `global.openai.gpt-6-astra`. Si la session
expire : `aws sso login --profile alphaforge`, puis **Reprendre**.
Le profil global ne garantit pas une résidence canadienne.

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/qualify_decision_runtime.py
```

Ces deux commandes ne déclenchent aucune inférence. Pour une nouvelle
démonstration avec appels AWS réels :

```bash
.venv/bin/python scripts/run_decision_demo.py --live \
  --base http://127.0.0.1:8768 --output runtime/nouvelle-demonstration
```

## Portée réelle

Deux familles sont qualifiées : réallocation minimale sous contraintes et
chocs déclarés avec réserve abstraite ; comparaison historique en CAD.
L'optimisation vérifie des conditions mathématiques sous ses hypothèses.
Les rendements historiques restent descriptifs. Aucun produit garanti, score
ESG, frais de transaction, impôt ou prévision à long terme n'est inventé.
Une méthode hors domaine ou une entrée indispensable absente entraîne une
clarification ou un résultat incomplet.

- [Implémentation, décisions et limites](docs/implementation/README.md)
- [Schéma de l'architecture obtenue](docs/implementation/architecture.svg)
- [Contrats d'échange](docs/implementation/CONTRAT_INTEGRATION.md)
- [Calculs et hypothèses](docs/implementation/finance.md)
- [Preuves des exécutions finales](docs/implementation/proofs/final_demo/summary.json)
- [État de reprise](docs/implementation/ETAT_REPRISE.md)
- [Conception validée, référence historique](docs/conception/README.md)

Le dossier persistant est `runtime/decision/` : **sauvegarder l'ensemble de ce
répertoire**, ainsi que le code, les données et les captures documentaires,
pour poursuivre sur une autre copie. Le détail de la sauvegarde cohérente
figure dans l'état de reprise.

Le Workbench précédent reste accessible à `/workbench` et l’ancienne application à `/legacy`. Ses documents, vidéos
et archives n'ont pas été supprimés ; leur
[ancienne documentation](docs/application_precedente.md) décrit la livraison
antérieure et ne constitue pas la démonstration du présent système.

Cette livraison reste locale. Les conditions du starter et de chaque fournisseur
de données restent applicables ; l'autorisation du datathon ne vaut pas licence
générale de redistribution. Aucun ordre ni déploiement cloud n'est effectué.
