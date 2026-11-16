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
| `objections` | `[{id: "O-1", cible: "F-2", texte, recalcul, resolue, reponse, issue}]` — `resolue` : la vérification a été exécutée par le code ; `issue` : `confirmee` (elle donne raison au Sceptique), `ecartee` (le fait tient tel quel) ou `limite` (limite de méthode, rien à trancher) |
| `options` | Ta demande / Version ajustée (si elle existe) / Placement large, même montant (XIU.TO, jugé par le Gardien), ou l'alternative compatible avec les exclusions : `{nom, ticker, montant_cad, horizon_ans, etat, changement?, libelle_actif?, faits?, note?}` |
| `bascule` | `{montants: [...], horizons: [...], cases: [{montant_cad, horizon_ans, etat}]}` pour les curseurs |
| `profil.evaluation` | Les 2 jauges : `tolerance`, `capacite`, `capacite_raisons`, `score_retenu`, `perte_max_*_pct`, `seuil_concentration_pct`, `seuil_titre_unique_pct` |
| `profil.tensions` | Tensions repérées (effet de mode, écart tolérance/capacité), en mots factuels |
| `qualite_donnees` | `[{code, libelle, statut: ok/alerte/echec, detail}]` |
| `questions` | Questions à poser quand une information manque |
| `texte` | `{reformulation, verdict, tensions, miroir[], pourquoi[], ce_qui_changerait[], limites[], avertissement}` ; chaque phrase `{texte, type, faits}` |
| `trace` | `[{agent, action, detail, faits, duree_ms}]` dans l'ordre d'exécution |

## Ajouts du 15 novembre (branche `fusion-corrections-deploiement`, à valider par l'équipe)

Tous **optionnels et rétrocompatibles** : un client qui les ignore continue de fonctionner.

| Champ | Contenu |
|---|---|
| `faits[].references` | Identifiants du registre des sources (`GET /api/sources`) : données utilisées, méthode, base théorique ou réglementaire |
| `faits[]` de type `HYPOTHESE` | Les seuils et barèmes de l'équipe (perte supportable, capacité, concentration, volatilité, corrélation) entrent au registre comme faits, cités par les règles qui les appliquent |
| `regles[].type` | Nature de l'explication : `FAIT`, `HYPOTHESE` ou `SCENARIO` (source unique : `gardien.TYPE_REGLE`) |
| `regles[].references` | Sur quoi repose la règle |
| `trace[].references` | Pourquoi l'agent est conçu ainsi (études citées) |
| phrase `{texte, type, faits, references?}` | `references` présent pour les limites tirées du dossier de recherche |
| `profil.evaluation.poids_pct` | Part de l'épargne placée, arrondie une seule fois en code |
| `demande.texte_lu` | `true` quand la personne a relu l'étape 2 : l'analyse ne re-remplit pas un champ qu'elle a vidé |
| `GET /api/sources` | `{references, justifications, agents}` : le registre complet (`backend/alphaforge/sources.py`) |

## Contrat 2 (fusion)

Source normative : [cadre commun, section 6](fusion/CADRE-COMMUN.md#6-contrats-communs).


**K1 — Portefeuille pondéré.** `profil.portefeuille_actuel` accepte la liste de symboles actuelle (`["XIU.TO", "XBB.TO"]`) ou un dictionnaire de poids en fractions de l'épargne totale (`{"XIU.TO": 0.5, "XBB.TO": 0.5}`, somme 1). Une liste sans poids est lue comme équipondérée, et cette lecture entre au dossier comme fait `HYPOTHESE`. Une fonction unique rend `(poids, origine)` avec `origine` ∈ `declare`, `hypothese_equiponderee`, ou `None` si le portefeuille est inconnu.

**K2 — Allocation après la demande.** `part = montant_cad / epargne_totale_cad`. Les lignes existantes sont réduites proportionnellement et la part s'ajoute à la ligne demandée (sémantique de `blend` de A : le placement **s'ajoute** à ce qui est détenu). Ne pas employer `set_target_weight` de B pour cela : il **fixe** un poids cible, ce qui est une autre opération.

**K3 — Comparaison appariée.** Nouveau champ facultatif `Dossier.comparaison` :

```json
{
  "disponible": true, "raison": null,
  "moteur": "historique-B", "version_moteur": "<MODEL_VERSION de analytics.py>",
  "politique": "achat-conservation, grille commune des séances, CAD, change daté au plus tard du jour",
  "fenetre": {"debut": "2021-11-12", "fin": "2026-11-12", "observations": 1228},
  "origine_poids": "declare | hypothese_equiponderee",
  "poids_avant": {"XIU.TO": 0.3333}, "poids_apres": {"TSLA": 0.2},
  "avant": {"pire_chute_pct": -14.3, "volatilite_pct": 10.1, "rendement_annualise_pct": 6.2, "valeur_finale_cad": 541000},
  "apres": {"pire_chute_pct": -20.6, "volatilite_pct": 14.5, "rendement_annualise_pct": 5.5, "valeur_finale_cad": 524000},
  "ecarts": {"pire_chute_pts": -6.3, "volatilite_pts": 4.4, "sens_pire_chute": "aggrave | ameliore | neutre"},
  "limites": ["…"], "faits": {"avant_pire_chute": "F-n", "apres_pire_chute": "F-n", "ecart_pire_chute": "F-n"}
}
```

Les nombres de cet exemple sont indicatifs. Les deux bras sont toujours calculés par le même moteur, sur la même grille et la même fenêtre. `disponible: false` avec une raison écrite quand les poids sont inconnus, qu'un symbole manque ou que les données échouent ; jamais de valeur inventée, `null` ne vaut pas zéro. Les limites viennent de `meta.limitations` du moteur.

**K4 — Autorité des mesures (pas de double autorité).**

| Grandeur | Seule source | Convention |
|---|---|---|
| Verdict, niveaux des règles | `gardien.py` | pire niveau |
| Actif seul : pire chute, volatilité, rendement, corrélation | `calculs.py` (C) | quotidien sur le calendrier propre de l'actif, CAD, √252 ou √365 |
| Portefeuille, avant et après | moteur historique (B) | grille commune de 1 228 séances, achat-conservation, CAD |

Ces deux familles donnent des valeurs différentes pour un même titre (TSLA : −70,9 % et −69,8 %) parce que leurs calendriers diffèrent. Une valeur d'une famille n'est jamais soustraite ni comparée à une valeur de l'autre ; la méthode de chaque fait nomme son moteur.

**K5 — Règle « perte supportable ».** Quand `comparaison.disponible`, la règle `capacite` juge la pire baisse du **portefeuille après** la demande, et son texte cite aussi la valeur avant et l'écart. Sinon elle garde le calcul actuel, dont le texte dit qu'il suppose le reste du portefeuille stable. Un seul niveau est affiché pour cette règle. Attribution : si le portefeuille actuel dépassait déjà la limite avant la demande, le texte le dit, et la règle ne passe pas au rouge de ce seul fait quand la demande n'aggrave pas la pire baisse. Bascule de retour : variable d'environnement `ALPHAFORGE_CAPACITE=approximation` (défaut : `portefeuille`). Les seuils (`5 + 0,35 × score`) ne changent pas dans cette fusion.

**K6 — Preuve d'appel.** Nouveau champ facultatif `Dossier.appels_modele` : une entrée par appel Bedrock, `{agent, modele, request_id, stop_reason, jetons_entree, jetons_sortie, latence_ms, garde_fou}`. Liste vide hors ligne. La trace de chaque agent y renvoie.

**K7 — Version du contrat.** `Dossier.version_contrat = "2"`. Les champs K3 et K6 sont absents ou vides pour un client qui les ignore.

**Correspondances à connaître.** Pourcentages en points chez C (`-70.9`), en fractions chez A et B (`0.2`) : convertir à la frontière du module transféré, une seule fois. Pire chute négative partout dans le dossier. États d'analyse de B (`missing_input`, `infeasible`) → `indetermine` avec la question ou la raison ; ils ne deviennent jamais un verdict de cohérence.


### État du contrat à la fin de la tranche 1

- `version_contrat` vaut `"2"` ; `comparaison` et `appels_modele` sont vides. K2 à K5 ne changent aucun calcul à cette étape.
- `profil.normaliser_portefeuille(portefeuille)` rend `(poids, origine)` ; un portefeuille inconnu rend `(None, None)`. Les poids doivent être numériques (pas de booléen ni de chaîne), finis, non négatifs et de somme 1, avec une tolérance de `1e-12` pour l'arrondi machine. Les listes sont équipondérées sur leurs symboles distincts. La fonction rend une copie et ne modifie pas l'entrée.
- Le fait `HYPOTHESE` relatif à l'équipondération sera ajouté lors de l'activation de la comparaison en tranche 2. Aucun fait existant n'est changé ici.
- `profil.symboles_portefeuille(portefeuille)` est le seul accès aux symboles des appelants Python. `frontend/src/portefeuille.js` fournit la même projection pour les opérations de liste de React. Les poids restent dans le profil jusqu'à une modification explicite des lignes par la personne. Ce pont a été autorisé séparément par le porteur ; voir [la révision](fusion/REVISIONS.md).
- `llm.journal_appels()` rend une liste vide dans cette tranche ; `orchestrateur.analyser` la rattache au dossier sur ses deux chemins de sortie. La tranche 3 instrumentera cette fonction.
- Les références des trois personas comparent tout le dossier hors durées et ces trois nouveaux champs : verdict, règles, faits, options et grille notamment.

### Qualification des entrées HTTP

Les routes `/api/comprendre`, `/api/analyse` et `/api/analyse/flux` convertissent
les chaînes numériques finies des champs montant, horizon, épargne, somme à
préserver, retrait prévu et tolérance. Une exclusion en chaîne devient une
liste d'un élément. Le profil et la demande fournis par l'appelant ne sont pas
modifiés.

Les entrées non numériques ou non finies restent invalides : le Gardien émet
la règle `donnees`, niveau `gris`, et le verdict `indetermine`. L'API arrête ces
demandes avant les calculs et la lecture de texte libre ; elle ne remplace pas
une saisie invalide par une valeur extraite du texte. `/api/comprendre` rend
les raisons dans `questions`.

Un montant supérieur à l'épargne totale donne le même verdict, avec la raison
« Le montant dépasse l'épargne totale. ». Un symbole demandé hors univers
reste une erreur 422, expliquée en français en mentionnant les 31 actifs du
jeu de départ. Dans le flux NDJSON, le statut HTTP reste 200 et le message
terminal porte `type: "erreur"` et `statut: 422`, comme dans le protocole existant.

La conversion des chaînes appartient à la frontière HTTP ; les fonctions
Python internes continuent de recevoir des nombres. Aucun seuil ni aucune
formule financière ne change.
