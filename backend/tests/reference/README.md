# Références des trois personas

Dossiers complets, en JSON trié, régénérés hors ligne à la tranche 2 après
`996b849`. Les références antérieures restent accessibles par `fusion/t1`
et le commit initial `d2b893e`.

Robert : `incoherent`, capacité `ok → orange` ; Amira :
`ajustement → incoherent`, capacité `ok → rouge` ; Mateo : `incoherent`
par exclusion, niveaux inchangés. Les valeurs des faits antérieurs sont
conservées. Les changements de grille et d'options sont détaillés dans
`docs/fusion/preuves/tranche-2/changements-references.json`.

Régénérées ensuite pour les suggestions (après un verdict « incohérent ») : seuls ajouts, le champ
`suggestions`, 3 faits FAIT en fin de registre (pire chute des placements suggérés) et une phrase dans la
trace du Gardien. Verdict, règles, options, grille, texte et faits existants inchangés pour les trois personas.

Puis pour la liste unique après un « incohérent » : options sans « Alternative » ni « Placement large »,
suggestions recalculées (Robert : XIU.TO remplace SPY), phrase « ce qui changerait » sur les suggestions,
fait de l'alternative de Mateo retiré. Verdict, règles et grille de bascule inchangés.

Puis pour « Version ajustée » quand seul le placement bloque : Mateo (exclusion) et Amira (BTC-USD, aucun
montant ni horizon ne suffit) reçoivent une deuxième option, même montant et même horizon, avec le premier
placement suggéré (ZST.TO, JNJ), et la phrase correspondante en tête de « ce qui changerait ». Robert,
verdicts, règles, faits et grilles inchangés.

`test_reference_personas.py` compare tout le dossier, en neutralisant seulement
les durées de trace et `appels_modele`. La comparaison K3 et la version du
contrat sont désormais figées aussi.

Régénérer uniquement lorsqu'une tranche change intentionnellement un résultat,
dans un commit séparé expliquant les valeurs changées et leur justification.
Depuis `backend/`, avec les dépendances installées :

```sh
ALPHAFORGE_LLM=off ALPHAFORGE_DATA_BUCKET='' ALPHAFORGE_CAPACITE='' python - <<'PY'
import json
from pathlib import Path
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS
for nom in ("robert", "amira", "mateo"):
    p = PERSONAS[nom]
    dossier = analyser(p["profil"], p["demande"])
    for etape in dossier["trace"]:
        etape["duree_ms"] = 0
    Path(f"tests/reference/{nom}.json").write_text(
        json.dumps(dossier, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    )
PY
```
