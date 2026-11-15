# Interface (voie Produit et interface)

React + Vite, en français. Consomme l'API (`backend/api.py`, format : [docs/contrats.md](../docs/contrats.md)).

## Lancer en local

```bash
# Terminal 1 : l'API (depuis backend/)
uvicorn api:app --reload --port 8000
# Terminal 2 : l'interface (depuis frontend/)
npm install
npm run dev        # http://localhost:5173  (/api est redirigé vers le port 8000)
```

## Le parcours

| Étape | Fichier | Ce qu'on voit |
|---|---|---|
| Accueil | `src/etapes/Accueil.jsx` | Promesse du produit sur un fond animé (`src/composants/FondAnime.jsx`, canvas décoratif, aucune donnée) |
| 1 et 2 · Conversation | `src/etapes/Conversation.jsx` | Une phrase libre (ou un des 3 profils) lue par le Profileur (`/api/comprendre`). « Voici ce que j'ai compris », puis seulement les questions manquantes, une à la fois (placement, montant, épargne, horizon, 3 questions de tolérance avec la mise en situation, fonds d'urgence). Résumé corrigeable (« Modifier »), 2 jauges, mots de la personne gardés pour le miroir |
| 3 · Analyse | `src/etapes/Etape3Trace.jsx` | La trace des agents qui défile, objections du Sceptique |
| 4 · Verdict | `src/etapes/Etape4Verdict.jsx` | Verdict 4 états, miroir, 3 options, règles, graphique de la pire chute, registre des faits cliquables |
| 5 · Curseurs | `src/etapes/Etape5Bascule.jsx` | Curseurs de bascule, carte complète montant × horizon, fiche pour le conseiller |
| Comparer | `src/etapes/Comparer.jsx` | La même demande pour Amira, Mateo et Robert, côte à côte |

Le nom affiché (`AlphaForge AI`, sous-titre `Second avis`) est défini par deux constantes dans `src/App.jsx`.
