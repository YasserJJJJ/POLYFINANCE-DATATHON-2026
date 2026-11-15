# Reprise — Prompt 6, validation du prototype attendue

## État à conserver

- Produit 0.5.0 : `http://127.0.0.1:8768`, inchangé.
- Prototype 0.6-prototype : `http://127.0.0.1:8770`.
- Canvas visuel : `/canvas.html`. Vidéo : `/demo.html`.
- Source : `prototype/prompt6/` ; documents : `docs/experience/`.
- Données du prototype : `data/cases.json`, `manifest.json` et sources
  immuables de `docs/defense/proofs/demo/`.
- Système visuel : `style.css`, polices locales `assets/`, licences OFL.
- Scripts de revue, captures et reçus : `docs/experience/proofs/`.
- Dossiers produit : conserver le magasin, les objets et les données déjà
  décrits dans `docs/implementation/ETAT_REPRISE.md`.

L’utilisateur a demandé de valider le canvas et le prototype **avant
l’intégration**. Ne pas interpréter l’autorisation générale de construire
des Prompts 4/5 comme l’approbation de cette direction visuelle.

## Relancer et modifier

```bash
.venv/bin/python scripts/launch_prototype_p6.py
# Sans ouverture de navigateur
.venv/bin/python scripts/launch_prototype_p6.py --no-browser
# Serveur au premier plan, si aucun serveur 8770 n’est déjà lancé
.venv/bin/python -m uvicorn prototype.prompt6.server:app --host 127.0.0.1 --port 8770
```

Le lanceur réutilise le prototype existant et n’arrête aucun autre service.
Les fichiers HTML/CSS/JS sont servis sans cache ; recharger suffit après
édition. Un changement Python du serveur demande son redémarrage.
Ne pas résoudre le symlink `.venv/bin/python` vers le Python système.

Les dossiers du prototype sont préparés par `build_data.py`. Ne les
régénérer que si les exports de référence changent intentionnellement,
et conserver le manifeste précédent. Le prototype ne doit jamais ouvrir
le magasin SQLite pour y écrire.

La préférence de lecture est conservée dans `localStorage`. Les brouillons
et le dernier résultat de variante utilisent `sessionStorage`. La copie
adoptée est en mémoire d’interface : elle n’est pas une branche durable.
La fermeture de l’onglet n’est pas présentée comme une sauvegarde de dossier.

## Reprise du travail après validation

1. Consigner les choix approuvés et les corrections demandées dans le canvas.
2. Figer les captures de référence à contenu et viewport identiques.
3. Intégrer une tranche : dossier vivant → conclusion → preuve → correction.
4. Raccorder les révisions et événements réels, conserver les archives.
5. Qualifier les variantes persistantes si cette interaction est retenue.
6. Rejouer les tâches de `correspondance.md` ; comparer visuel et comportement.
7. Vérifier uniquement les parties modifiées et les nouvelles incertitudes.

## Défauts déjà traités à ne pas réintroduire

- Réutilisation d’un essai r5 depuis r15 sans affichage de sa vraie base.
- Résultat ancien pris pour celui des champs actuellement édités.
- Non-unicité affirmée lorsque le moteur n’a aucun témoin.
- Confusion entre certificat algébrique et preuve d’un solveur.
- Mauvais pointeur pour le déficit, montant fractionnaire arrondi à zéro.
- Réutilisation numérique prétendue dans un simple recalcul local.
- Texte de graphique peu contrasté, overflow à 320 px.
- Réponse asynchrone qui écrit dans un écran déjà quitté.

Il reste à réaliser l’intégration et l’essai humain ; ils ne sont pas
déclarés accomplis par les tests du prototype.
