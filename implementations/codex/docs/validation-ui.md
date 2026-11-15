# Vérification de l’interface et livraison locale

Le 15 novembre 2026, le parcours automatisé s’est terminé à
**12:13:51 UTC, soit 07:13:51 à Montréal**. Il utilise un Chromium de test
isolé avec Playwright, sans ouvrir le profil du navigateur de l’utilisateur.
Ce contrôle technique ne remplace pas un essai par le porteur du projet.

## Parcours observé

| Vérification | Résultat |
|---|---|
| Ordinateur, 1440 × 1000 | Application rendue, courbe visible, aucun débordement horizontal |
| Mobile, 390 × 844 | Réglages empilés, navigation utilisable, aucun débordement horizontal |
| Robert, TSLA ramené à son poids initial de 25 % | Séries de référence et de variante strictement identiques |
| Annulation du réglage | Retour à l’hypothèse précédente de 5 % |
| Vue « Reculs » | Graphique de baisse depuis le sommet affiché |
| Amira puis Mateo | NVDA à 10 % et horizon 15 ans ; XOM à 0 % et horizon 10 ans |
| Contre-exemple Mateo | Baisse maximale historique plus forte après retrait direct de XOM |
| Bouton d’analyse | Appel Bedrock réel, trois outils exécutés, statut `success` |
| Dossier de preuves | Sources et identifiants de requêtes affichés |
| Export JSON | Même identifiant et comparaison strictement identique à la réponse du service |
| Document de méthode | Source locale accessible, HTTP 200 |
| JavaScript | Aucune exception observée dans le parcours ordinateur |

Les captures ont aussi été inspectées visuellement. Une première version
présentait des notes trop petites ; les corps utiles ont été agrandis, les
contrastes renforcés et les réglages mobiles réorganisés avant le parcours
final. Cela ne constitue pas un audit d’accessibilité exhaustif.

## Preuve AWS depuis l’interface

Rapport : [`9861d0b6173640a18d7ede3664aeba25`](../artifacts/ui-export.json),
créé à `2026-11-15T12:13:15.141704+00:00`.

| Appel | Requête AWS | Fin |
|---|---|---|
| Sélection des outils | `135b729e-1f49-498b-a707-f76f83f8af59` | `tool_use` |
| Restitution structurée | `37969d33-6b5f-4819-b85c-ad6068d7823e` | `end_turn`, aucun nouvel outil |

Le modèle a demandé `compare_scenario`, `read_evidence` et `inspect_profile`.
Les deux appels ont consommé 4 349 tokens déclarés au total, cache inclus.
Le diagnostic d’un premier essai rejeté et les corrections sont conservés
dans [la revue indépendante](agent-review.md).

## Artefacts et reproduction

- [Résultat machine du parcours](../artifacts/ui-verification.json)
- [Capture ordinateur](../artifacts/screens/desktop-viewport.png)
- [Capture mobile](../artifacts/screens/mobile-viewport.png)
- [Dossier de preuves](../artifacts/screens/evidence.png)
- [Capture vidéo du parcours réel, sans voix](../artifacts/AlphaForge_demo_locale.webm)
- [Script du parcours](../scripts/verify_ui.cjs)

Une [vidéo commentée de 4 min 54](../artifacts/AlphaForge_demo_commentee.mp4)
a ensuite été produite depuis de nouvelles manipulations locales et la preuve
Bedrock enregistrée, clairement signalée. Aucune nouvelle inférence n’a été
effectuée pour ce tournage. Son décodage complet a réussi ; les contrôles
d’image, de son et d’export sont documentés dans la
[transcription](demo-transcript.md).

Les dépendances et la commande sont dans le [README](../README.md).
Le test exige un serveur sur `127.0.0.1:8766` et un profil AWS valide. Une
exécution supplémentaire du test complet déclenche une inférence facturée.

## Validation finale du code

Après le dernier correctif du renouvellement des identifiants AWS :

```text
.venv/bin/python -m pytest -q
39 passed, 1 warning in 2.48s
```

Les 39 cas couvrent le moteur numérique (8), l’API financière (16), le contrat
de l’agent (10) et le renouvellement du profil AWS (5). Le warning concerne
la dépréciation du transport `httpx` dans le client de test Starlette ; aucun
échec n’a été constaté. Le serveur a ensuite été redémarré pour charger le
correctif. Cette dernière correction a été testée sans nouvelle inférence.

Les calculs passés, les limites des données et les préférences fictives restent
distincts d’une prédiction, d’un conseil adapté à une personne réelle ou d’une
certification ESG.
