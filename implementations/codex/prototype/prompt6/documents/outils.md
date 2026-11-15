# Outils qualifiés pour le Prompt 6

Inventaire du 15 novembre 2026. « Exposé » signifie disponible dans la
session ; « essayé » signifie qu’un appel ou un comportement a réellement
été observé. Une fiche de plugin n’établit ni une connexion, ni la route de
son modèle.

## Outils retenus

| Outil et version observée | Accès vérifié | Rôle et résultat attendu | Inférence |
|---|---|---|---|
| Sessions de travail et relecture | Métadonnées du parent et des branches : `amazon-bedrock-runtime` | Conception, lecture critique, code et revue indépendante | Route AWS de la session ; pas de fournisseur auxiliaire |
| Recherche AWS `invoke_web_search`, client boto3 1.44.3 | Cinq recherches avec reçus dans [proofs/recherche/](proofs/recherche/) ; identité AWS contrôlée par le client existant | Références HAI, incertitude, divulgation progressive, documentation de produits | Recherche classée AWS, sans `WebAnswer` |
| Récupération HTTP et extraction déterministe | Pages/PDF effectivement capturés, obstacles consignés dans [recherche.md](recherche.md) | Lire le texte primaire et conserver ce qui a réellement été consulté | Aucun modèle |
| Plugin Management | Recherche Figma/design/browser exécutée | Vérifier l’existence et le statut des outils de conception ; décider si une connexion manque réellement | Métadonnées de catalogue, aucune génération de design invoquée |
| Application actuelle, FastAPI 0.163.1 | `/api/health` : version produit 0.5.0, port 8768 ; parcours observés dans [audit_initial.md](audit_initial.md) | Partir des capacités réelles et des limites de la défense | Ouverture d’archives sans nouvel appel modèle |
| Prototype local, FastAPI + Uvicorn 0.54.0 | Port 8770 et API testés ; [contrat](contrat_prototype.md) | Prototype modifiable, dossiers archivés, exploration séparée et téléchargement des preuves | Aucun appel modèle |
| Moteur financier Python, NumPy 2.5.4 et SciPy 1.18.1 | Variantes 30 000 / 40 000 / 74 400 CAD reproduites ; impossibilité sans options | Produire les valeurs de l’exploration, sans recopier les réponses de conception | Calcul déterministe uniquement |
| HTML, CSS et SVG natifs | Écrans et graphiques rendus dans Chromium | Système visuel, panneaux contextuels, tableaux équivalents, répartition et séries historiques | Aucun modèle d’image, aucun service de design distant |
| Playwright 1.65.1, Node 22.23.1, Chromium | Lancement local, captures, clics, clavier et lecture du DOM exécutés | Examiner le produit, vérifier le prototype et filmer des interactions réelles | Navigation et tests déterministes |
| axe-core local | Installé et exécuté par la revue UX ; rapport dans proofs/audit/prototype/ | Contrastes et règles automatiques d’accessibilité, complément au clavier et à la lecture humaine | Aucun modèle |
| FFmpeg local | Transcodage effectué et MP4 contrôlé : H.264, 1440 × 1000, environ 75 secondes | Transcoder l’enregistrement WebM en MP4 sans modifier son contenu | Aucun modèle ; aucun achat |
| FontTools 4.68.0 | Noms, versions et notices lus dans les six fichiers de police | Vérifier la provenance des polices locales et conserver leurs licences | Aucun modèle |

Les polices DM Sans et Newsreader sont servies localement, sous SIL OFL 1.1.
Les licences et références sont conservées dans
[assets/FONTS.md](../../prototype/prompt6/assets/FONTS.md).

## Outils examinés mais non requis

La recherche du catalogue a retourné les outils suivants comme
**disponibles à l’installation, non installés**. Aucune connexion n’a été
créée :

| Outil | Utilité possible | Décision pour cette étape |
|---|---|---|
| Figma | Écrans éditables, composants partagés, commentaires | Le prototype HTML est déjà modifiable et directement consultable. Aucune connexion indispensable ; l’inférence éventuelle d’une fonction Figma n’est pas qualifiée AWS. |
| Product Design | Audit de flux et génération de prototypes | Route des assistants de design non vérifiée. Ne pas lui déléguer une inférence. |
| Canva | Présentation de directions visuelles et supports | Aucun besoin de diapositive ni de génération d’image ; route IA non vérifiée. |
| MagicPath | Canvas et prototype générés | Route IA non vérifiée et aucun avantage nécessaire sur le prototype local. |
| TinyFish | Navigateur agentique distant | Playwright couvre l’inspection requise sans assistant distant. |
| Webflow | Construction et publication hébergées | Pas de publication demandée avant validation ; dépendance superflue. |

Les outils Sites, GitHub et de contrôle documentaire sont exposés dans la
session. Ils ne sont pas employés comme dépendances de ce prototype :
pas de publication, de modification de dépôt distant ou de document Office
nécessaire. Leur exposition ne vaut pas essai d’un compte externe.
Le contrôle natif CUA est également exposé ; Playwright est le navigateur
effectivement essayé et retenu pour les vérifications reproductibles.

## Route et limites de l’inventaire

- La route de la branche données/relecture a été lue dans ses métadonnées :
  session `01a1e0bf-81a7-7ce0-8dd8-8329367f23f9`,
  fournisseur `amazon-bedrock-runtime`.
- La branche recherche conserve sa propre
  [preuve de route](proofs/recherche/route.json), ainsi que les reçus de
  recherche et les captures. Les reçus d’inférence des dossiers P5 restent
  ceux des dossiers sources ; ils ne décrivent pas de nouveaux appels au
  moment où l’on parcourt le prototype.
- Le serveur d’exploration ne construit aucun client Bedrock et ne touche
  pas le `DossierStore`. Les accès HTTP au modèle ne sont pas simulés.
- Aucun assistant de design externe n’a été utilisé. Aucun service payant
  supplémentaire n’a été souscrit.

La présence de Playwright ne garantit pas l’accessibilité : celle-ci est
examinée sur les tâches et états retenus. De même, une capture esthétique
ne constitue pas une validation humaine de compréhension. Les comparaisons
prototype/intégration restent à effectuer **après validation de la
direction**, puisque l’intégration n’a pas encore commencé.
