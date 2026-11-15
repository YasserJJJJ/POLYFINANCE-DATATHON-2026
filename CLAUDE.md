# Contexte datathon — équipe AlphaForge

- Défi : AlphaForge AI (PolyFinances × Banque Nationale × AWS). Solution agentique auto-explicative.
- Notre produit : un second avis qui confronte une décision d'investissement au profil de la personne.
  Verdict en 4 états, 3 options, curseurs de bascule, faits cliquables.
- Grille : solution 20 %, agentique et explicabilité 20 %, données 20 %, UX/UI 10 %, AWS 15 %, pitch 15 %.
- Principe non négociable : **les chiffres viennent du code, les mots viennent des agents.** Aucun LLM ne
  produit un chiffre ni ne décide du verdict. Le Gardien (`backend/alphaforge/gardien.py`) décide.
- Toute phrase montrée à l'utilisateur est étiquetée FAIT / HYPOTHESE / SCENARIO et cite ses F-n.
- Jamais « achetez », « vendez », « je recommande ». Simulation, pas de conseil personnalisé.
- Données : `data/raw/` ne se modifie jamais. Utiliser `adj_close`, convertir en CAD avec le taux BdC.
  Fenêtre 2021-11-12 → 2026-11-12. Les montants des personas sont fictifs.
- Contrats communs : `docs/contrats.md`. On ne les change qu'après accord de l'équipe.
- Python 3.12+, code dans `backend/alphaforge/`, tests dans `backend/tests/` (`pytest -q` depuis `backend/`).
- Interface : React + Vite dans `frontend/`, textes en français.
- Git : branche `feature/nom-court`, Conventional Commits, jamais de clé AWS ni de `.env` dans le dépôt.
