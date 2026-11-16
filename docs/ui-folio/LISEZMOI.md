# Habillage Folio du parcours « Second avis » — branche `ui-folio`

Créée depuis `origin/fusion-corrections-deploiement` au commit `1d4c907` (15 novembre 2026). Aucune règle, aucun seuil, aucun calcul n'est modifié : le changement est dans `frontend/`.

## Ce qui est appliqué

Source du style : `FOLIO_UI_KIT` (Folio 0.7.0), voie « transférer le langage visuel » de son `LIRE_EN_PREMIER.md`.

- `frontend/public/fonts/` : DM Sans et Newsreader (six fichiers, licences SIL OFL jointes). Plus aucune police chargée depuis un service externe.
- `frontend/src/folio.css` : palette (papier, encre verte, rouge d'annotation), typographie, filets, manchette, onglets, double page du résultat. Chargée après `styles.css` : elle rhabille les classes existantes, elle n'en retire aucune.
- Manchette : mot-symbole, état du dossier (édition, archive, analyse en cours), étapes en chiffres romains.
- Verdict en double page : l'avis en grand titre à gauche ; à droite le chiffre qui le porte, la pire baisse du portefeuille avec la demande, face à celle d'avant, avec son écart et son sens rendus par le moteur. Le chiffre ouvre sa preuve.
- Lecture « Essentielle » et « Approfondie » : les deux onglets existants, présentés comme dans Folio.

## Ce qui est ajouté, tiré de l'exploration `ui-adam`

- **Éditions** (`composants/Editions.jsx`) : chaque analyse reçue est gardée dans le navigateur. On peut relire une édition antérieure (bandeau d'archive), revenir à la dernière, et toute modification depuis une archive crée une nouvelle édition. Rien n'est effacé ; rien n'est recalculé à la relecture.
- **Ce que la modification change** : entre deux éditions successives, l'avis, les niveaux de règles (appariés par code) et les mesures du portefeuille qui diffèrent, en marques de correction.
- **Épreuve périmée** : pendant une relance, l'ancien résultat reste lisible mais marqué comme périmé.
- États : chaque état garde un libellé et un signe distinct ; la couleur ne porte jamais seule l'information.

## Corrections faites en passant

- Le champ de montant des puces refusait 38 000 $ (pas de 500 à partir de 1) : le pas est libre.
- `vite.config.js` : la cible du proxy se règle par `ALPHAFORGE_API` (défaut inchangé, port 8000).

## Vérifié

Dans un navigateur, à 1280 px et à 375 px, hors ligne : accueil, vérification, analyse, verdict de Robert, modification du montant à 38 000 $, « ce que la modification change », relecture de l'édition 1, lecture approfondie. Aucune erreur de console, pas de défilement horizontal. `npm run build` réussit.

Non vérifié : étape « Curseurs », vue « Comparer les 3 profils », plan ouvert sans placement, exécution avec Bedrock, lecteur d'écran, tests du backend (non relancés : aucun fichier du backend n'a changé).

## Limites

- Les éditions vivent dans la mémoire de la page : elles disparaissent au rechargement.
- Le thème sombre n'existe plus : Folio est un papier clair.
- Le tableau de comparaison de la lecture approfondie affiche encore les mesures avec six décimales.
- Le mot-symbole affiché est « folio », sous-titré « AlphaForge · Second avis » ; les constantes du produit ne changent pas.

## Lancer

```bash
cd backend && uvicorn api:app --port 8000
cd frontend && npm install && npm run dev
```
