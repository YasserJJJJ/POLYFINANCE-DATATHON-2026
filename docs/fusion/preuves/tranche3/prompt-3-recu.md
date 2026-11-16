# PROMPT 3 — AWS : preuve d'appel, robustesse, déploiement (après le prompt 1, en parallèle du prompt 2)

```
AUTORISATIONS (à remplir par le porteur avant l'envoi)
- git push : OUI, de la branche fusion/aws vers origin, sans --force, après tests verts
- création de ressources AWS (Lambda, S3, Amplify, rôle IAM) : OUI, sur le compte 471112821226, après le durcissement de l'étape D et l'affichage du plan
- création d'un Guardrail Bedrock : OUI
- appels Bedrock de vérification (quelques analyses réelles) : OUI
COMMIT DE DÉPART (fin de la tranche 1) : ____________
```

## Mode d'exécution : même conversation, tranches étanches

Ce prompt est collé dans la **même conversation** que le prompt 1, et le prompt 2 y sera collé aussi. Il a pourtant été conçu pour une conversation séparée. Tu dois donc reproduire toi-même cette séparation :

- **Une tranche à la fois.** Si la tranche 2 est en cours dans cette conversation, termine-la d'abord (étiquette `fusion/t2`, compte rendu) ; puis exécute cette tranche 3 en entier jusqu'à `fusion/t3`. N'entrelace jamais les deux tranches, et ne lance pas de sous-agent qui travaillerait sur l'autre en même temps dans le même dossier.
- **Ton dossier, ta branche, rien d'autre.** Tu travailles uniquement dans `../POLYFINANCE-fusion-aws`, sur `fusion/aws`. Tu n'écris jamais dans le dossier principal du dépôt ni dans `../POLYFINANCE-fusion-analyse` (`fusion/analyse`). Avant chaque commit : `git rev-parse --show-toplevel` et `git branch --show-current` doivent rendre ce dossier et cette branche.
- **Même point de départ.** Ta branche part du commit de fin de la tranche 1, pas de l'état laissé par l'autre tranche. Ne fusionne pas `fusion/analyse` dans la tienne, ne la lis pas pour t'en inspirer ; la réunion des deux est le travail du prompt 4.
- **Fichiers étanches.** Tu ne modifies que les fichiers listés dans « Fichiers que tu possèdes ». Si tu as besoin d'un changement dans un fichier de l'autre tranche, tu ne le fais pas : tu l'écris dans le compte rendu pour le prompt 4.
- **Ne te fie pas à ta mémoire de la conversation.** Ce que tu as vu ou supposé pendant le prompt 1 ou l'autre tranche ne vaut pas preuve : relis le cadre, relis les fichiers dans ton arbre de travail, relance les tests là. Les seules choses que tu reprends de la conversation sont le commit de fin de la tranche 1 et les autorisations du porteur.
- **Compte rendu et journal** : n'écris que ta section « Tranche 3 » ; ne touche pas à celle de l'autre.

Tu es l'agent intégrateur de la fusion AlphaForge, **tranche 3 sur 4**. Aujourd'hui l'usage d'AWS par le produit se limite à l'inférence Bedrock, sans trace des appels ; les scripts de déploiement existent et n'ont jamais tourné ; le compte ne contient aucune ressource du produit. Tu fais entrer la preuve de chaque appel de modèle dans le dossier (transfert depuis A), tu corriges deux défauts de robustesse du socle, et tu prépares le déploiement, que tu n'exécutes que si la ligne d'autorisation ci-dessus le dit. Un autre agent exécute en même temps la tranche 2 (analyse) dans un autre arbre de travail : ne touche pas à ses fichiers.

## Avant tout

1. Lis en entier `docs/fusion/CADRE-COMMUN.md`, en particulier K6, les invariants et la section 9.
2. Arbre de travail : depuis `/Users/vpro/Documents/ChatGPT/POLYFINANCE-DATATHON-2026`, `git worktree add ../POLYFINANCE-fusion-aws -b fusion/aws <commit de départ>`.
3. Vérifie l'accès en lecture seule : `aws sts get-caller-identity --profile alphaforge` doit rendre le compte `471112821226`. Les modèles du socle sont `global.anthropic.claude-sonnet-5` et `global.amazon.nova-2-lite-v1:0`, région `us-east-1` ; les deux répondaient le 15 novembre. Ne lis aucun fichier d'identifiants ; n'ouvre pas `infra/enregistrer_identifiants.ps1`.
4. Rappel : d'après les documents des équipes, ce compte est détruit le lundi 16 novembre à 13 h 59. Tout ce qui doit être montré tournant sur AWS doit être capturé avant.

## Faits établis par l'évaluation

- `llm.appeler` (socle) rend seulement le texte ; ni identifiant de requête, ni jetons, ni latence ne sont conservés.
- A enregistre pour chaque appel Converse `requestId` (`ResponseMetadata.RequestId`), `stopReason`, `usage.inputTokens`, `usage.outputTokens`, `metrics.latencyMs` (`implementations/claude-code/src/datathon2026/agent.py:172-188`).
- Coûts mesurés du socle : une analyse complète fait 3 à 4 appels (Nova pour la lecture du texte, Sonnet pour le Sceptique, Sonnet une ou deux fois pour le Rédacteur), environ 8 000 jetons, 8 à 14 s.
- Mode hors ligne « collant » : à la première erreur d'accès, même sur un seul modèle, `llm.py` coupe Bedrock pour tout le processus jusqu'au redémarrage (`_etat["indisponible"]`, résultat STS mis en cache).
- `verifier_bedrock.py`, `infra/deployer.py` et `infra/creer_guardrail.py` retombent sur le profil `datathon` ; le profil convenu est `alphaforge`.
- `infra/deployer.py` crée une adresse de fonction publique sans authentification (`AuthType NONE`, `Principal: "*"`), une politique Bedrock sur `Resource: "*"`, un compartiment web public, et l'API a un CORS ouvert : chaque appel public déclenche des appels Bedrock facturés.
- Sur Lambda, le flux progressif NDJSON arrive d'un bloc (déclaré par C, jamais observé).

## Étapes, par ordre de priorité

**A. Preuve d'appel (obligatoire).** Dans `backend/alphaforge/llm.py` :
- remplis le journal rendu par `journal_appels()` (point de branchement posé en tranche 1) : une entrée K6 par appel Converse, y compris les appels refusés par le contrôle d'ancrage et ceux bloqués par un Guardrail ; l'agent appelant est passé en argument facultatif de `appeler` avec une valeur par défaut, pour ne casser aucun appelant ;
- le journal est propre à une analyse : deux requêtes HTTP simultanées ne mélangent pas leurs entrées (l'API exécute l'analyse du flux dans un fil séparé : choisis un mécanisme qui tient dans ce cas et prouve-le par un test à deux analyses concurrentes) ;
- hors ligne : liste vide, aucun import de `boto3` ;
- aucun contenu de requête ou de réponse dans le journal, seulement les métadonnées.
Tests dans `backend/tests/test_llm.py` avec le faux client existant. Si un agent doit transmettre son nom (`agents/sceptique.py`, `agents/profileur.py` appartiennent à la tranche 2 ou au socle, `agents/redacteur.py` à la tranche 4), ne modifie pas ces fichiers : déduis l'agent d'un paramètre par défaut et laisse à la tranche 4 le soin de passer le nom ; note-le dans le compte rendu.

**B. Robustesse (obligatoire).**
- Mode hors ligne collant : après une erreur d'accès, Bedrock est retenté au plus tard après un délai court et configurable, et une erreur sur un modèle ne coupe pas l'autre. Le comportement « sans identifiants, tout fonctionne » reste intact. Test avec faux client : erreur, puis rétablissement sans redémarrage.
- Profil : `verifier_bedrock.py` et les scripts d'`infra/` lisent `AWS_PROFILE` s'il est défini et n'imposent plus `datathon` ; le défaut documenté devient `alphaforge`.
- `GET /api/sante` indique en plus la région et les identifiants de modèles réellement utilisés (pas d'identifiant de compte).

**C. Vérification réelle sur Bedrock (obligatoire si autorisée).** Lance l'API locale avec le profil `alphaforge` et exécute Robert, Amira et un texte libre contradictoire. Enregistre les trois dossiers sous `docs/fusion/preuves/tranche3/`. Contrôles : `appels_modele` contient un identifiant de requête par appel ; les totaux de jetons et la durée sont dans la plage mesurée ; verdict, règles, options et grille identiques à l'exécution hors ligne des mêmes entrées.

**D. Durcir le déploiement avant toute exécution (obligatoire, sans rien créer).** Dans `infra/deployer.py` et `backend/api.py` :
- CORS limité à l'origine de l'interface déployée (variable d'environnement), au lieu de `*` ;
- politique Bedrock limitée aux deux profils d'inférence utilisés et aux modèles qu'ils routent, au lieu de `Resource: "*"` ;
- une limite simple de débit ou de concurrence sur la fonction (concurrence réservée basse), pour borner la dépense si l'adresse fuit ;
- un mode `--plan` (ou équivalent) qui affiche chaque ressource que le script créerait, sans rien créer ; exécute-le et joins sa sortie au compte rendu ;
- `backend/requirements-lambda.txt` cohérent avec les imports réels (`mangum`) ; les modules transférés en tranche 2 n'ajoutent aucune dépendance.
Vérifie que le rôle `WSParticipantRole` a le droit de créer ces ressources **par simulation ou appels en lecture** (`iam simulate-principal-policy` si autorisé, sinon dis que c'est non vérifié). Ne tente aucune création pour « voir ».

**E. Déployer (seulement si la ligne d'autorisation dit OUI).**
- Exécute le script durci, consigne chaque ressource créée (nom, ARN, région) dans `docs/fusion/preuves/tranche3/RESSOURCES.md`, avec la commande de suppression de chacune.
- Vérifie par l'adresse publique : `/api/sante`, une analyse de Robert de bout en bout, l'archivage du dossier dans S3 (`stockage.py`), et le comportement réel du flux NDJSON sur Lambda (progressif ou d'un bloc : dis ce que tu observes, n'ajuste pas l'interface, c'est la tranche 4).
- Guardrail : seulement si sa ligne d'autorisation dit OUI. Crée-le par `infra/creer_guardrail.py`, branche `ALPHAFORGE_GUARDRAIL_ID`, vérifie qu'une réponse normale passe et qu'un texte de conseil est bloqué puis remplacé par le gabarit. Le Guardrail s'ajoute au contrôle d'ancrage en code ; il ne le remplace pas.
- Si une création échoue pour un droit manquant : arrête le déploiement, ne contourne pas, laisse l'état propre (supprime ce que tu as créé dans cette tentative) et rends compte.
Sans autorisation : arrête-toi après D et écris dans le compte rendu la commande exacte que le porteur ou un agent autorisé devra lancer, et sa durée estimée.

## Fichiers que tu possèdes

`backend/alphaforge/llm.py`, `backend/alphaforge/stockage.py`, `backend/lambda_handler.py`, `backend/verifier_bedrock.py`, `backend/api.py`, `backend/requirements-lambda.txt`, `backend/tests/test_llm.py` et tes nouveaux tests, `infra/` (sauf `enregistrer_identifiants.ps1`, que tu n'ouvres pas), `docs/deploiement.md`, `docs/fusion/preuves/tranche3/`.

Tu ne touches pas : `dossier.py`, `orchestrateur.py`, `gardien.py`, `agents/`, `personas.py`, `sources.py`, `frontend/`, `docs/contrats.md`.

## Vérifications à consigner (commande et sortie)

1. `pytest -q` : rien de perdu ; tests du journal et de la reprise après erreur verts.
2. Hors ligne (`ALPHAFORGE_LLM=off`, sans profil) : analyse de Robert identique à la référence figée, `appels_modele` vide.
3. Si C est autorisée : les trois dossiers réels, avec le tableau appels / jetons / latence par agent.
4. Sortie du mode `--plan`.
5. Si E est exécutée : `RESSOURCES.md`, réponse de `/api/sante` par l'adresse publique, dossier réel obtenu par cette adresse, clé S3 du dossier archivé.

## Clore

Laisse `fusion/aws` prête sans la fusionner, étiquette `fusion/t3`, complète `docs/fusion/COMPTE-RENDU.md` (section « Tranche 3 ») et `JOURNAL.md`. Dis explicitement ce qui tourne sur AWS, ce qui est prêt et non exécuté, et ce qui disparaîtra à la fermeture du compte.
