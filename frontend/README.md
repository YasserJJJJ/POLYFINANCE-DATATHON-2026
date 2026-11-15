# Interface (voie Produit et interface)

React + Vite + Tailwind CSS, composants façon shadcn/ui (`src/components/ui/`), en français, au tutoiement.
Consomme l'API (`backend/api.py`, format : [docs/contrats.md](../docs/contrats.md)) : les agents, le Gardien et
tous les chiffres viennent du backend ; l'interface n'en calcule aucun.

## Lancer en local

```bash
# Terminal 1 : l'API (depuis backend/)
uvicorn api:app --reload --port 8000
# Terminal 2 : l'interface (depuis frontend/)
npm install
npm run dev        # http://localhost:5173  (/api est redirigé vers le port 8000)
```

## Le parcours

| Écran | Fichier | Ce qu'on voit |
|---|---|---|
| Accueil | `src/ecrans/Accueil.jsx` | La promesse sur un fond animé (`src/components/FondAnime.jsx`, canvas décoratif, aucune donnée) |
| 1 et 2 · Conversation | `src/ecrans/Conversation.jsx` | Une phrase libre ou un des 3 profils, lue par le Profileur (`/api/comprendre`). « Voici ce que j'ai compris », puis seulement les questions manquantes, une à la fois, avec leur raison (placement, montant, épargne, horizon, 3 questions de tolérance avec la mise en situation, fonds d'urgence). Résumé corrigeable (« Modifier »), 2 jauges, mots de la personne gardés pour le miroir |
| 3 · Analyse | `src/ecrans/Analyse.jsx` | La trace réelle des agents, objections du Sceptique, faits F-n et références |
| 4 · Verdict | `src/ecrans/Verdict.jsx` | Verdict en 4 états, miroir, raisons, 3 options, règles du Gardien, pire chute, registre des faits, qualité des données, limites, sources |
| 5 · Curseurs | `src/ecrans/Curseurs.jsx` | Curseurs de bascule, carte montant × horizon, fiche pour le conseiller |
| Comparer | `src/ecrans/Comparer.jsx` | La même demande pour Amira, Mateo et Robert, côte à côte |

Chaque F-n s'ouvre dans un tiroir (`src/components/TiroirFait.jsx`) : valeur, source, méthode, références.
Le nom affiché (`AlphaForge AI`, sous-titre `Second avis`) est défini dans `src/components/Marque.jsx`.
