# Démonstration — environ cinq minutes

Préparation : ouvrir `Ouvrir_AlphaForge.command`, vérifier le profil AWS encore
valide, garder un rapport récent exporté. Les trois portefeuilles, capitaux et
repères de perte proposés sont des hypothèses inventées pour l’expérience.

## 0:00–0:40 — La question

« Une recommandation devient plus utile quand on peut changer son hypothèse et
vérifier ce qui change. AlphaForge compare des décisions financières fictives
et conserve les calculs et les preuves. »

Montrer Robert et sa demande. Désigner les contrôles éditables. Préciser que
l’horizon personnel n’est pas une projection du passé.

## 0:40–1:50 — Un compromis calculé

Avec Robert, comparer Tesla à 25 % dans la référence et 5 % dans la variante.
Sur l’instantané, la baisse maximale passe d’environ 23,4 % à 11,3 %, pour un
rendement cumulé proche. Montrer la courbe et un épisode historique.

Changer l’exposition et recalculer. Montrer que la nouvelle hypothèse produit
un nouveau résultat. Revenir à l’état précédent ou aux hypothèses du profil.
Ne pas dire que le passé prédit une future réduction de risque identique.

## 1:50–2:50 — L’agent et ses preuves

Lancer l’analyse Bedrock. Pendant l’attente, expliquer que le modèle appelle
les outils et que Python calcule. Ouvrir les actions : comparaison, lectures
documentaires, examen du profil si choisi, puis restitution.

Montrer les questions utiles, une observation chiffrée et sa source. Une fiche
résume une lecture qualifiée ; elle n’est pas une recherche de nouvelles en direct.
Afficher l’identifiant d’appel AWS dans la trace.

## 2:50–3:40 — Le contre-exemple Mateo

Passer à Mateo, retirer directement XOM et recalculer. La baisse maximale
historique augmente ici d’environ 12,7 % à 18,6 %. Montrer que la réponse
ne rebaptise pas ce changement « plus sûr ».

« Une préférence d’exclusion et un objectif de risque sont deux dimensions
distinctes. Les données du starter ne certifient pas les autres placements ESG. »

## 3:40–4:20 — Amira et les inconnues

Passer à Amira. Réduire NVDA laisse encore une baisse historique importante.
La présence de QQQ et d’actions technologiques peut créer des recouvrements :
leur mesure demanderait les compositions détaillées des FNB.

Montrer la distinction entre préférence, fait calculé et donnée manquante.

## 4:20–5:00 — Vérifier et reprendre

Exporter un rapport. Montrer les hypothèses, la période, les empreintes,
les résultats et la trace AWS. Expliquer que le calcul fonctionne localement
et que l’agent exige le compte atelier actif.

« AlphaForge rend une décision plus vérifiable, et laisse l’utilisateur juge
du compromis. Le résultat n’est ni une promesse de performance ni un ordre. »

## Demandes supplémentaires

- « Teste TSLA à 40 % et explique le compromis avec mon horizon. »
- « Je veux exclure Exxon, mais je ne veux pas aggraver la baisse historique. »
- « J’ai plusieurs fonds : suis-je vraiment diversifié ? »
- « Ajoute un titre absent du jeu. » Le manque de données doit rester explicite.

## Enregistrements livrés

La [vidéo commentée](../artifacts/AlphaForge_demo_commentee.mp4) dure
4 min 54. Elle utilise la voix de synthèse française Amélie sur le Mac et
montre les manipulations réelles de l’application. Les séquences de l’agent
rejouent le rapport Bedrock déjà vérifié, avec un bandeau permanent indiquant
qu’il s’agit d’une preuve enregistrée. Le tournage n’a déclenché aucune nouvelle
inférence. La [transcription horodatée](demo-transcript.md) documente le contenu,
la provenance, les contrôles et la reproduction.

Une [capture brute de 65 secondes](../artifacts/AlphaForge_demo_locale.webm),
sans voix, conserve aussi le parcours de vérification de l’interface, y compris
son véritable appel Bedrock.
