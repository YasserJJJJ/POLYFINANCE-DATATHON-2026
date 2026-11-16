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
| `options` | Ta demande / Version ajustée (si elle existe : le montant ou l'horizon change ; si seul le placement bloque, le premier placement de `suggestions`, même montant et même horizon, `changement: {ticker}`) / Placement large, même montant (XIU.TO, jugé par le Gardien) quand il n'y a pas de `suggestions` : `{nom, ticker, montant_cad, horizon_ans, etat, changement?, libelle_actif?, faits?, note?, constat?}` |
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
  "disponible": true,
  "raison": null,
  "moteur": "historique-B",
  "version_moteur": "cad-buy-and-hold-v1",
  "politique": "achat-conservation, grille commune des séances, CAD, change daté au plus tard du jour",
  "fenetre": {
    "debut": "2021-11-12",
    "fin": "2026-11-12",
    "observations": 1228
  },
  "poids_avant": {
    "RY.TO": 0.3333333333333333,
    "XBB.TO": 0.3333333333333333,
    "XIU.TO": 0.3333333333333333
  },
  "poids_apres": {
    "RY.TO": 0.26666666666666666,
    "XBB.TO": 0.26666666666666666,
    "XIU.TO": 0.26666666666666666,
    "TSLA": 0.2
  },
  "avant": {
    "pire_chute_pct": -14.256677,
    "volatilite_pct": 10.047745,
    "rendement_annualise_pct": 13.00306,
    "valeur_finale_cad": 737021.43
  },
  "apres": {
    "pire_chute_pct": -20.595922,
    "volatilite_pct": 14.50247,
    "rendement_annualise_pct": 11.662517,
    "valeur_finale_cad": 694335.21
  },
  "ecarts": {
    "pire_chute_pts": -6.339245,
    "volatilite_pts": 4.454725,
    "sens_pire_chute": "aggrave"
  },
  "limites": [
    "Comparaison rétrospective, pas prévision ni backtest de sélection historiquement réalisable : univers et prix ajustés acquis en 2026.",
    "Le drawdown est le creux observé sur cette grille; il ne borne pas une perte future et ignore les mouvements entre observations.",
    "La volatilité annualisée suppose des intervalles comparables et une mise à l'échelle en racine du temps; week-ends et jours fériés créent des intervalles inégaux.",
    "Le taux FX est une moyenne indicative, pas un cours exécutable synchronisé avec la clôture des actifs.",
    "L'heure de valorisation est une convention documentaire; les fichiers ne contiennent pas l'historique des heures exactes de publication.",
    "Les fenêtres historiques sont descriptives, choisies à l'avance dans le code; aucune probabilité de scénario futur ne leur est attribuée.",
    "Aucun score ESG, exposition réelle des FNB, valorisation fondamentale ou capacité personnelle de perte n'est déduit de ces données.",
    "Les poids portent sur les instruments. Les compositions des FNB ne sont pas disponibles : les expositions communes ne sont pas mesurées."
  ],
  "faits": {
    "fenetre_portefeuille": "F-16",
    "poids_avant": "F-17",
    "poids_apres": "F-18",
    "avant_pire_chute": "F-19",
    "avant_volatilite": "F-20",
    "avant_rendement": "F-21",
    "avant_valeur_finale": "F-22",
    "apres_pire_chute": "F-23",
    "apres_volatilite": "F-24",
    "apres_rendement": "F-25",
    "apres_valeur_finale": "F-26",
    "ecart_pire_chute": "F-27",
    "ecart_volatilite": "F-28",
    "h_attribution": "F-29",
    "h_non_monotonie": "F-30",
    "limites_portefeuille": "F-31"
  },
  "origine_poids": "declare"
}
```

Extrait exact de [Robert avec Bedrock, réception T4](fusion/preuves/tranche4/robert-bedrock.json). Les deux bras sont toujours calculés par le même moteur, sur la même grille et la même fenêtre. `disponible: false` avec une raison écrite quand les poids sont inconnus, qu'un symbole manque ou que les données échouent ; jamais de valeur inventée, `null` ne vaut pas zéro. Les limites viennent de `meta.limitations` du moteur.

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


## Réception du contrat fusionné (T4)

K6 ci-dessous : appel réel du Rédacteur pour le même dossier Robert, via Bedrock `alphaforge` en `us-east-1`. Les champs sont extraits, sans valeur fictive. Les indices `trace[].appels_modele` sont à partir de zéro. Une trace intermédiaire peut ne pas encore contenir ces indices ; le dossier final fait autorité.

```json
{
  "appels_modele": [
    {
      "agent": "Rédacteur",
      "modele": "global.anthropic.claude-sonnet-5",
      "request_id": "d64e5735-94df-4189-a1ca-f42a900d95d3",
      "stop_reason": "end_turn",
      "jetons_entree": 12919,
      "jetons_sortie": 649,
      "latence_ms": 7645,
      "garde_fou": "configure"
    }
  ]
}
```

`questions` place les questions décisives en premier, avec le changement de verdict testé et le fait HYPOTHESE correspondant. La donnée manquante reste absente du profil.

La recherche d’ajustement est exhaustive au pas de 100 CAD, dans les deux sens ; `options[].sens` vaut `baisse` ou `hausse`, et `constat` donne la formulation neutre calculée. La grille existante explore des fractions du montant demandé, jusqu’à ce montant : elle ne couvre pas automatiquement un ajustement proposé à la hausse. Pour une grille couvrant 14 000 et 17 500 CAD de XIU.TO chez Amira, le [dossier de 35 000 CAD](fusion/preuves/tranche4/amira-xiu35000.json) donne :

```json
{
  "observee": false,
  "explication": "Un montant plus élevé peut améliorer le verdict quand le placement diversifie le portefeuille. Les cases sont les résultats exacts du Gardien ; une amélioration n'est pas une erreur de grille.",
  "exemple": {
    "montant_bas_cad": 14000,
    "montant_haut_cad": 17500,
    "horizon_ans": 2,
    "etat_bas": "ajustement",
    "etat_haut": "coherent"
  },
  "faits": [
    "F-28",
    "F-17",
    "F-21",
    "F-25"
  ]
}
```

L’interface conserve les cases exactes et explique cette non-monotonie. La fiche conseiller indique qu’elle décrit la demande de départ. Les mesures K3 ne sont jamais recalculées dans JavaScript.
