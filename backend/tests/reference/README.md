# Références des trois personas

Dossiers complets, en JSON trié, produits hors ligne après la fusion `c161a55`,
avant tout ajout de contrat ou correctif. À ce point, `backend`, `frontend`,
`infra` et `data` étaient identiques à C (`6761d6636c6c712663cdaf76c739d2bc8f991aef`).

Robert : `incoherent` ; Amira : `ajustement` ; Mateo : `incoherent`.
`test_reference_personas.py` compare tout le dossier, en neutralisant seulement
les durées de trace et les trois nouveaux champs du contrat 2.

Régénérer uniquement lorsqu'une tranche change intentionnellement un résultat,
dans un commit séparé expliquant les valeurs changées et leur justification.
Depuis `backend/`, avec les dépendances installées :

```sh
ALPHAFORGE_LLM=off .venv/bin/python - <<'PY'
import json
from pathlib import Path
from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS
for nom in ("robert", "amira", "mateo"):
    p = PERSONAS[nom]
    dossier = analyser(p["profil"], p["demande"])
    Path(f"tests/reference/{nom}.json").write_text(
        json.dumps(dossier, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    )
PY
```
