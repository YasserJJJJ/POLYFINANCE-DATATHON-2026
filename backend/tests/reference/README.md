# Références des trois personas

Dossiers complets, en JSON trié, régénérés hors ligne à la tranche 2 après
`996b849`. Les références antérieures restent accessibles par `fusion/t1`
et le commit initial `d2b893e`.

Robert : `incoherent`, capacité `ok → orange` ; Amira :
`ajustement → incoherent`, capacité `ok → rouge` ; Mateo : `incoherent`
par exclusion, niveaux inchangés. Les valeurs des faits antérieurs sont
conservées. Les changements de grille et d'options sont détaillés dans
`docs/fusion/preuves/tranche-2/changements-references.json`.

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
