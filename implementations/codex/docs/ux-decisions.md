# AlphaForge — Choix d’expérience

## Objectif

La personne doit pouvoir comprendre ce qui change entre deux hypothèses, consulter les preuves et modifier le problème. Le résultat financier reste une simulation. Les trois profils officiels sont séparés des avoirs, capitaux et seuils inventés pour la démonstration.

## Référence consultée

Microsoft Research, *Guidelines for Human-AI Interaction* (projet établi le 4 juin 2019), page primaire consultée le 15 novembre 2026 :
https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/

La page présente des recommandations pour l’interaction initiale, l’usage, les erreurs et l’évolution dans le temps. Elle renvoie au papier CHI 2019. La page du projet a été lue ; le texte intégral de l’article n’a pas été relu pour cette implémentation. Cette source oriente la conception, elle ne constitue pas une validation de notre interface.

## Options et choix

| Option | Apport | Limite | Décision |
|---|---|---|---|
| Chat seul | Entrée très libre | Compare mal les chiffres et masque les hypothèses | Garder la demande libre dans l’atelier, pas un fil de chat comme interface principale |
| Tableau de bord riche | Expose de nombreuses mesures | Charge cognitive et risque de détacher les chiffres du contexte | Trois mesures principales, scénario historique et dossier progressif |
| Comparateur accompagné d’un dossier | Relie contexte, hypothèse, résultat et preuve | Nécessite un contrat stable entre calcul et explication | Retenu pour la première version, à vérifier sur des parcours réels |

## Réalisation

- Entrée en français : demande modifiable, trois scénarios fictifs, capital, horizon, portefeuille de départ et poids inspectables.
- L’analyse initiale appelle réellement le moteur, avec `use_ai:false`. Aucun chiffre n’est fabriqué côté navigateur. Le bouton « Analyser avec l’agent » déclenche explicitement AWS Bedrock.
- Deux courbes partagent leur période et leur devise. Valeur de 100 CAD et drawdown sont deux vues des mêmes séries retournées par le moteur. Le survol expose les observations datées.
- Les chiffres bleu grisé sont la référence, les chiffres verts l’hypothèse. Le vert encode la série comparée, pas un jugement de supériorité.
- Une modification marque les résultats précédents comme périmés jusqu’au recalcul. L’interface conserve l’analyse précédente et permet d’y revenir.
- Les conditions de révision et les questions utiles de l’agent apparaissent directement sous la conclusion, en plus du dossier détaillé.
- Les sources et traces se trouvent dans une page dédiée. Les références dans les conclusions ouvrent la source correspondante.
- Un échec d’inférence laisse les résultats du calcul visibles et annonce l’échec. Un statut `partial` n’est pas présenté comme un succès complet.
- Les transitions de chargement reflètent une requête en cours ; aucun faux découpage en agents ni étape fictive n’est affiché.
- L’export contient la dernière analyse effectivement retournée par le serveur. Il ne prétend pas exporter les changements non recalculés.

## Direction visuelle

Atelier de recherche calme : navigation graphite, surface crème, vert végétal et accents citron pâle. Une typographie éditoriale pour les titres distingue l’explication de la lecture des chiffres. Les polices système évitent une dépendance réseau. Aucun logo fournisseur ou badge n’est utilisé comme preuve d’exécution.

## Accessibilité et sécurité

Navigation clavier, labels de champs, focus visible, régions d’état, descriptions SVG, respect du mouvement réduit et adaptation mobile. Le graphique visuel est accompagné de mesures et de fenêtres historiques en texte. Les textes retournés par le serveur sont échappés ; les liens de sources acceptent uniquement HTTP(S).

## Vérification

Les validations visuelles et fonctionnelles doivent être effectuées sur le serveur FastAPI avec les véritables résultats. Vérifications prévues : Robert → Amira → Mateo ; appel AWS explicite ; modifier le poids puis recalculer ; total invalide ; consulter les sources ; exporter ; retour à l’analyse précédente ; viewport mobile.

Vérifications réalisées par l’agent interface : `node --check` sans erreur ; identifiants HTML uniques et sélecteurs statiques complets ; lecture réelle de `/api/bootstrap` (31 actifs, trois profils) ; requête `/api/analyze` Robert sans inférence avec retour conforme des métriques, séries et sources. La validation visuelle et les parcours navigateur sont réalisés par l’orchestrateur sur une instance Chromium isolée. Leur résultat n’est pas présumé dans ce document.

## Route de développement vérifiée

L’agent interface a vérifié sa session `01a1df0e-7da5-7690-b09d-b15497a722d2`, dont les métadonnées déclarent `amazon-bedrock-runtime`. L’appel STS avec le profil `alphaforge` et la région `us-east-1` a retourné le rôle `WSParticipantRole/Participant` dans le compte d’équipe. Aucun identifiant secret n’est présent dans les fichiers de l’interface.
