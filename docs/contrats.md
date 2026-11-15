# Contrats communs

Ces formats permettent à chaque voie d'avancer en parallèle. On ne les change qu'après accord de l'équipe.
Source de vérité : [backend/alphaforge/dossier.py](../backend/alphaforge/dossier.py).

## Requête : `POST /api/analyse`

```json
{
  "profil": {
    "nom": "Robert", "age": 59, "experience": "avancée",
    "horizon_ans": 4, "tolerance": 30,
    "reponses_tolerance": {"q_amis": 33, "q_mot": 0, "q_chute": 33},
    "epargne_totale_cad": 400000, "somme_a_preserver_cad": 300000,
    "revenu_stable": true, "fonds_urgence": true, "dettes_importantes": false,
    "retrait_prevu_ans": 4, "exclusions": ["Energy"],
    "portefeuille_actuel": ["XIU.TO", "XBB.TO"],
    "citations": ["Je veux préserver mon capital"]
  },
  "demande": {"texte": "Je veux mettre 80 000 $ dans Tesla", "ticker": "TSLA", "montant_cad": 80000}
}
```

- `tolerance` (0-100) sert si `reponses_tolerance` est absent. Les valeurs des réponses viennent de
  `GET /api/questions`.
- `exclusions` : noms de secteurs de `assets_universe.csv` (ex. `Energy`).
- `ticker` et `montant_cad` peuvent être omis : le Profileur tente de les lire dans `texte`.
- Champ manquant → `null`. Une information essentielle manquante donne un verdict `indetermine`.

## Réponse : le dossier de décision

| Champ | Contenu |
|---|---|
| `verdict` | `{etat, libelle, respectees, evaluees}` ; `etat` ∈ `coherent`, `ajustement`, `incoherent`, `indetermine` |
| `regles` | `[{code, libelle, niveau, explication, faits}]` ; `niveau` ∈ `ok`, `orange`, `rouge`, `gris`, `non_evaluee` |
| `faits` | `[{id: "F-3", libelle, valeur, unite, type, source, methode, lu_ou_calcule}]` ; `type` ∈ `FAIT`, `HYPOTHESE`, `SCENARIO` |
| `objections` | `[{id: "O-1", cible: "F-2", texte, recalcul, resolue, reponse}]` |
| `options` | Ta demande / Version ajustée (si elle existe) / Ne rien changer : `{nom, montant_cad, horizon_ans, etat, changement?}` |
| `bascule` | `{montants: [...], horizons: [...], cases: [{montant_cad, horizon_ans, etat}]}` pour les curseurs |
| `profil.evaluation` | Les 2 jauges : `tolerance`, `capacite`, `capacite_raisons`, `score_retenu`, `perte_max_*_pct`, `seuil_concentration_pct` |
| `profil.tensions` | Tensions repérées (effet de mode, écart tolérance/capacité), en mots factuels |
| `qualite_donnees` | `[{code, libelle, statut: ok/alerte/echec, detail}]` |
| `questions` | Questions à poser quand une information manque |
| `texte` | `{reformulation, verdict, tensions, miroir[], pourquoi[], ce_qui_changerait[], limites[], avertissement}` ; chaque phrase `{texte, type, faits}` |
| `trace` | `[{agent, action, detail, faits, duree_ms}]` dans l'ordre d'exécution |
