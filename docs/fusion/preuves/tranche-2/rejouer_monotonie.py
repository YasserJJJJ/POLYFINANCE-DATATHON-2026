"""Contre-exemple K5 : exécuter avec PYTHONPATH=backend, ALPHAFORGE_LLM=off."""
import json
from alphaforge import gardien, portefeuille
from alphaforge.agents.analyste import mesures_actif
from alphaforge.personas import PERSONAS

p = PERSONAS['amira']['profil']
rows = []
for montant in (14000, 17500):
    demande = {'ticker': 'XIU.TO', 'montant_cad': montant}
    c = portefeuille.comparer(p, demande)
    r = gardien.appliquer_regles(p, demande, mesures_actif('XIU.TO', p['portefeuille_actuel']))
    rows.append({'montant_cad': montant, 'avant': c['avant']['pire_chute_pct'],
                 'apres': c['apres']['pire_chute_pct'], 'verdict': gardien.verdict(r)['etat'],
                 'capacite': next(v.explication for v in r if v.code == 'capacite')})
print(json.dumps(rows, ensure_ascii=False, indent=2))
