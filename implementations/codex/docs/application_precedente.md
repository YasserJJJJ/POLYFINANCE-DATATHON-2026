> Archive de la documentation de la première application, avant le Prompt 4. Les chemins étaient relatifs à la racine du projet. Le parcours actuel est décrit dans ../README.md.

# AlphaForge — laboratoire de décisions

Ouvre **`Ouvrir_AlphaForge.command`** par double-clic. Le navigateur affiche
l’application sur le Mac. Le serveur écoute uniquement sur `127.0.0.1` et
réutilise sa propre instance lorsqu’elle fonctionne déjà.

L’application compare un portefeuille fictif à une modification d’exposition.
Un moteur Python calcule les résultats en dollars canadiens. À la demande,
un agent Amazon Bedrock examine le profil, appelle les outils de calcul et de
lecture documentaire, puis explique les compromis à partir des observations
vérifiées.

## Essayer

1. Choisis Robert, Amira ou Mateo. Les avoirs, le capital et le repère de perte
   sont des hypothèses ajoutées pour la démonstration, modifiables.
2. Change le poids de l’actif étudié et recalcule. Compare le rendement passé,
   la baisse maximale et les épisodes historiques.
3. Formule une demande et lance l’agent. Consulte les sources et la trace
   des outils réellement exécutés.
4. Exporte le rapport JSON : hypothèses, séries, métriques, empreintes de
   données, sources et identifiants des requêtes AWS y sont conservés.

Trois parcours sont détaillés dans [le scénario de démonstration](docs/demo.md).
La [vidéo commentée de 4 min 54](artifacts/AlphaForge_demo_commentee.mp4)
présente ces parcours avec une voix de synthèse française. Les passages
Bedrock rejouent une analyse réelle enregistrée, signalée à l’écran.
La [transcription horodatée](docs/demo-transcript.md) conserve les preuves de
capture et les instructions de reproduction.

Les données sont incluses dans le dossier local ; le calcul n’exige pas AWS.
Une nouvelle analyse d’agent nécessite le profil AWS `alphaforge` encore valide.

## Installer ou restaurer

Configuration exécutée : Python 3.15 sur macOS. Le code utilise Python 3.11+ ;
les autres versions n’ont pas été vérifiées dans cette livraison.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/launch.py
```

Le port préféré est `8766`, puis un port libre jusqu’à `8775`. Le lanceur ne
touche pas aux autres applications. L’URL et le PID propres au projet sont
enregistrés dans `runtime/server.json`. Les journaux sont dans
`runtime/server.log`.

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/aws_probe.py
```

Le probe sans option vérifie STS, sans inférence. L’option `--live` effectue
trois petites inférences facturées au compte atelier vérifié.

## Ce qui est calculé

L’instantané fourni contient 31 actifs et 40 049 observations de prix.
Les deux allocations sont rejouées sur les mêmes 1 228 dates communes.
Les prix ajustés incluent déjà les distributions ; les instruments USD sont
valorisés en CAD avec le dernier taux connu à la date retenue.

Le portefeuille est conservé sans rééquilibrage. La variante change un poids
initial, les autres étant redimensionnés proportionnellement. Chaque épisode
historique recommence avec ces poids initiaux. La méthode, les équations et
les limites de calendrier sont détaillées dans [methodology.md](docs/methodology.md).

Ce rejeu de l’univers choisi en 2026 n’est pas une preuve qu’une stratégie
aurait pu être sélectionnée à l’époque. L’horizon du profil est une préférence,
pas une projection de l’historique. La composition des FNB et les preuves ESG
d’entreprises sont absentes. Aucun ordre n’est transmis.

## Architecture et preuves

- [Dossier de décision](docs/product-decision.md)
- [Architecture et contrats](docs/technical.md)
- [Références qualifiées](docs/references.md)
- [Route AWS et appels réels](docs/aws-runtime.md)
- [Revue indépendante de l’agent](docs/agent-review.md)
- [Vérification financière](docs/validation-finance.md)
- [Vérification de l’interface](docs/validation-ui.md)
- [Résumé du projet](docs/one-page.md)
- [Résumé PDF, une page](output/pdf/AlphaForge_resume.pdf)
- [État de reprise](WORKLOG.md)

Le fournisseur du produit est `amazon-bedrock-runtime`, modèle
`global.openai.gpt-6-astra`, entrée `us-east-1`, profil `alphaforge`.
L’identité STS est contrôlée avant la première inférence. Aucun fournisseur
personnel de remplacement n’est utilisé. Les secrets restent dans la chaîne
d’identifiants AWS du Mac et ne sont pas inclus dans les fichiers du projet.

## Données et partage

Cette livraison reste sur le Mac, suivant le choix du porteur du projet.
Le dépôt Git est local, sans destination distante. Une
[archive de sauvegarde](artifacts/AlphaForge_local_2026-11-15.zip) rassemble le
code, les données, les exemples, la documentation, le PDF et les vidéos.
Le [bilan de restauration](artifacts/backup-verification.json) donne son
empreinte et le commit des sources.

Le dossier `data/` conserve la copie de travail du starter, son README,
ses sources, son script d’origine et ses avertissements. L’application ne
relance pas la collecte.

La possibilité de télécharger ou d’utiliser les données pour le concours ne
constitue pas une licence générale de republication. Avant un dépôt public,
vérifier les conditions des sources ou distribuer les références et le script
de récupération. Le dossier `runtime/` contient les demandes saisies et leurs
rapports ; il est exclu du suivi Git.

## Reproduire les livrables locaux

Le script `scripts/package_local.py` crée l’archive locale, puis la restaure
dans un dossier temporaire. Il vérifie les empreintes de tous les fichiers et
exécute un calcul depuis cette copie.

```bash
.venv/bin/python scripts/package_local.py
```

Le résumé PDF provient de `docs/one-page.md`. Pour le régénérer, installer
`requirements-docs.txt`, puis exécuter `scripts/create_summary.py`.
La vérification visuelle nécessite aussi Poppler (`pdftoppm`) ; l’option
`--no-render` génère seulement le PDF.

La vérification d’interface utilise un navigateur de test isolé :

```bash
npm install --prefix runtime/browser-check playwright@1.65.1
runtime/browser-check/node_modules/.bin/playwright install chromium
node scripts/verify_ui.cjs --record
```

Elle attend le serveur sur le port `8766` et déclenche une véritable analyse
AWS facturée au compte atelier. La capture sans voix est enregistrée sous
`artifacts/AlphaForge_demo_locale.webm`.
