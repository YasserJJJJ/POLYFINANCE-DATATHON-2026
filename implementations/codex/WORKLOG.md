# AlphaForge — état de reprise

> **Mise à jour Prompt 5 — 15 novembre 2026.** Version 0.5.0 sur
> http://127.0.0.1:8768. Trois relecteurs indépendants ont reproduit les
> calculs et fait corriger les défauts de révision, preuves, contrats et
> restitution. Robert30→40 puis risque1k, Amira, demande incomplète et
> certificat impossible ont été exécutés avec AWS réel.
> Lire le [dossier de défense](docs/defense/README.md),
> l'[état de reprise actuel](docs/implementation/ETAT_REPRISE.md) et les
> [vérifications distinctes](docs/defense/proofs/verification.json).
> Les sections ci-dessous conservent l'histoire de la première livraison.

## Objectif courant

Livrer sur le Mac un laboratoire de décisions financières simulées, réellement
essayable, dont les calculs sont traçables et l’agent fonctionne sur le compte AWS
de l’atelier. Le 15 novembre 2026, l’utilisateur a choisi **sur mon Mac d’abord,
puis décider du partage**. Aucun déploiement public ni dépôt distant retenu.

## Accès vérifiés le 15 novembre

- Sources v2 intactes, neuf fichiers du ZIP identiques aux copies locales.
- Les 36 PDF du manifeste sont présents.
- Les empreintes des six CSV du starter correspondent à l’audit antérieur.
- Écriture locale et réseau autorisés depuis 06 h 53 (Montréal).
- AWS STS : compte `471112821226`, rôle `WSParticipantRole/Participant`,
  profil `alphaforge`, région `us-east-1`.
- Route de cette conversation : `amazon-bedrock-runtime`,
  `global.openai.gpt-6-astra`. Route vérifiée dans les métadonnées des agents.
- `AWS_BEARER_TOKEN_BEDROCK` absent. Ne jamais conserver de secret ici.
- Pas de dépôt Git préexistant dans ce dossier ou ses parents.
- Premier appel Bedrock Converse réel réussi par la mission AWS.

## Version locale 0.1

Application active sur `http://127.0.0.1:8766`, uniquement sur la boucle locale.
Lanceur : `Ouvrir_AlphaForge.command`. Python 3.15, FastAPI, moteur numérique
Python et interface HTML/CSS/JavaScript sans dépendance distante.

Un dépôt Git local sur la branche `main` a été initialisé. Aucune destination
distante n’est configurée. La préservation finale comporte les sources, les
données de travail, les rapports fictifs enregistrés et les livrables.

## Tâches et preuves

| Responsable | Statut | Sortie et preuve |
|---|---|---|
| Orchestrateur | Vérifié | API, sources, agent outillé, export exact, lancement local ; `docs/technical.md` |
| finance_engine | Vérifié | Calculs CAD et trois profils ; 8 tests numériques et 16 cas API ; `docs/validation-finance.md` |
| aws_runtime | Vérifié | Route AWS réelle, restitution JSON et récupération après expiration ; 15 tests de contrat ; `docs/agent-review.md` |
| experience | Vérifié | Interface française rendue en 1440 × 1000 et 390 × 844 ; `docs/validation-ui.md` |
| finance_engine | Vérifié | Résumé PDF d’une page, paragraphes complets et rendu inspecté ; `output/pdf/AlphaForge_resume.pdf` |
| experience | Vérifié | Vidéo commentée de 4 min 54, voix française du Mac, décodage complet, images et son contrôlés ; `docs/demo-transcript.md` |
| Orchestrateur | Vérifié | Dépôt local et archive restaurée, empreintes et calcul depuis la copie ; `artifacts/backup-verification.json` |

Le dernier contrôle intégré a obtenu **39 tests réussis en 2,48 s**. Un warning
de dépréciation concerne uniquement le client de test Starlette/httpx.
Le serveur a été redémarré avec la correction de renouvellement des identifiants.

L’essai navigateur réel a réussi à 07:13:51 Montréal, sans exception JavaScript
observée sur ordinateur ni débordement horizontal aux deux tailles testées.
Son export est `artifacts/ui-export.json`, identifiant
`9861d0b6173640a18d7ede3664aeba25` ; les deux appels AWS et les contrôles sont
dans `artifacts/ui-verification.json`. Les trois personas ont également fait
l’objet d’inférences réelles, archivées dans `examples/`.

La vidéo commentée ne déclenche aucune nouvelle inférence : ses séquences
Bedrock rejouent cette preuve avec un bandeau explicite. Le PDF, les deux
vidéos, les sources et les données figurent dans
`artifacts/AlphaForge_local_2026-11-15.zip`. Le manifeste interne contient les
empreintes de tous les fichiers ; le bilan externe donne le SHA-256 de
l’archive et le commit des sources. Aucun chantier d’implémentation n’est
encore actif pour cette version.

## Décisions retenues et limites

- Comparer une allocation de référence à une variation explicitement choisie :
  ne pas présenter le meilleur passé comme une prévision.
- Les avoirs des démonstrations sont inventés et éditables ; seuls les
  éléments biographiques des personas viennent du cas officiel.
- Les prix ajustés incluent déjà les distributions ; pas de double comptage.
- Les préférences ESG exigent des preuves documentaires absentes du starter.
- Un calcul local reste disponible explicitement ; une panne AWS ne doit
  jamais être présentée comme une analyse d’agent réussie.
- Le résultat ne revendique ni optimisation robuste, ni composition détaillée
  des FNB, ni score ESG. Les alternatives sont dans `docs/product-decision.md`.
- Le starter acquis en 2026 sert à un rejeu descriptif. Les frais, fiscalité,
  mouvements intrajournaliers et millésimes macro ne sont pas reconstitués.

## Défauts corrigés

- Paramètres partiels : les valeurs manquantes reprennent bien le profil choisi.
- Calcul et export restent cohérents même si l’agent échoue après un outil.
- Les erreurs d’outil récupérées donnent un résultat partiel visible.
- Les chiffres affichés proviennent du moteur ; la prose générée est contrôlée.
- Un premier essai d’interface a rejeté la conclusion. La restitution utilise
  désormais un contexte vérifié sans outils et une sélection d’observations
  contrainte. Le second parcours réel depuis l’interface a réussi.
- Le client relit le profil et revérifie STS après une expiration AWS.
- Les petits textes, contrastes et contrôles mobiles ont été corrigés après rendu.

## Reprise utile

Aucun accès humain supplémentaire n’est requis pour essayer la version locale.
L’essai par le porteur reste à faire : ouvrir Robert, modifier le poids de TSLA,
recalculer, puis demander une analyse et examiner ses preuves.

Le partage, un dépôt distant et un hébergement restent à décider avec le
porteur. Ne rien publier au seul motif que les tests passent.
Le calcul local n’exige pas AWS ; de nouvelles conclusions d’agent exigent
le profil `alphaforge` actif et le compte atelier encore disponible.

## Échéances officielles

Page https://polyfinances.ca/datathon consultée le 15 novembre :
code/application le 15 à 23 h 59 ; compte AWS supprimé le 16 à 13 h 59 ;
vidéo/résumé/documentation le 16 à 14 h. Horaires de l’événement à Montréal,
fuseau non explicité sur la page. Sauvegarder hors compte temporaire.
