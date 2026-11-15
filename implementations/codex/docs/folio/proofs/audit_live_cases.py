"""Independent read-only checks against captured API studies and raw CSVs."""
import csv,datetime,hashlib,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).parent

def sha(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def checked(condition,message):
 if not condition:raise AssertionError(message)
def main():
 manifest=json.loads((OUT/'live_cases.json').read_text());report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{},'limitations':['Une identité AWS et des reçus n’établissent pas une supériorité des agents.','Les calculs recoupés restent conditionnels à la qualité et aux conventions des données.']}
 for name,c in manifest['cases'].items():
  d=json.loads((OUT/c['snapshot']).read_text());checked(d['status']=='complete',name+' incomplete')
  calls=[a for a in d['attempts'] if a['tool']=='bedrock.converse'];checked(len(calls)==4,name+' calls count')
  receipts=[]
  for call in calls:
   r=call['detail'];checked(call['status']=='complete',name+' call incomplete')
   checked(r['provider']=='amazon-bedrock-runtime' and r['model']=='global.openai.gpt-6-astra' and r['region']=='us-east-1' and r['account_id']=='471112821226',name+' bad route')
   checked(bool(r['request_id']),name+' missing receipt')
   receipts.append({k:r[k] for k in ['provider','model','region','account_id','request_id','usage','latency_ms']}|{'role':call['role'],'attempt_id':call['id'],'status':call['status']})
  checked(len({r['request_id'] for r in receipts})==4,name+' duplicate request id')
  checked({r['role'] for r in receipts}=={'agent0','agent1','agent2','agent3'},name+' missing agent')
  hashes=[]
  for a in d['artifacts']:
   checked(sha(a['content'])==a['hash'],name+' artifact hash '+a['ref']);hashes.append(a['ref'])
  analysis=d['current_analysis']['content'];research=next(a['content'] for a in d['artifacts'] if a['id']=='research')
  evidence=[]
  for e in research['evidence']:
   cap=e.get('capture') or {};findings=[]
   for field,hashfield in [('path','sha256'),('text_path','text_sha256')]:
    if cap.get(field) and cap.get(hashfield):
     path=ROOT/cap[field];actual=hashlib.sha256(path.read_bytes()).hexdigest();checked(actual==cap[hashfield],name+' source hash '+e['id']);findings.append(field)
   if e.get('known_at'):checked(e['known_at'][:10]<=research['knowledge_date'],name+' source future '+e['id'])
   evidence.append({'id':e['id'],'hashes_checked':findings,'known_at':e.get('known_at'),'reading_level':e.get('reading_level')})
  checked(analysis['provenance']['model_inference_calls']==0,name+' numerical tool invoked model')
  c['aws_calls']=receipts;c['analysis_method']=analysis['method']['id'];c['agent_transformations']=[{'role':t['role'],'status':t['status'],'outputs':t['output_refs']} for t in d['tasks']];c['verified_at']=report['checked_at']
  entry={'dossier_id':d['id'],'revision':d['revision'],'status':d['status'],'aws_calls':receipts,'transforms':c['agent_transformations'],'artifacts_hashed':len(hashes),'sources_checked':evidence,'method':analysis['method']['id']}
  if name=='robert':
   inputs=analysis['method']['inputs'];capital=inputs['capital_cad'];w0=inputs['weights'];proof=[]
   for o in analysis['options']:
    w=o['weights'];turnover=capital*.5*sum(abs(w.get(t,0)-w0.get(t,0)) for t in set(w)|set(w0));checked(abs(turnover-o['metrics']['turnover_cad']['value'])<1e-6,'robert turnover')
    losses={q['id']:-capital*sum(w[t]*q['returns'][t] for t in w) for q in inputs['scenarios']}
    for q in o['scenario_results']:checked(abs(losses[q['id']]-q['loss_cad'])<1e-6,'robert loss')
    proof.append({'option':o['id'],'turnover_cad':turnover,'losses_cad':losses,'weights_sum':sum(w.values())})
   lower_bound=inputs['withdrawal_cad']-capital*w0.get('RESERVE_ABSTRAITE',0);minimum=next(o for o in proof if o['option']=='minimum_turnover')['turnover_cad'];checked(abs(minimum-lower_bound)<1e-6,'reserve lower bound attained')
   entry['independent_arithmetic']={'options':proof,'necessary_reserve_increase_lower_bound_cad':lower_bound,'attained_by_minimum':True,'scope':'Borne car financement sans vente à découvert ni apport extérieur ; arithmétique des scénarios fournis.'}
   c['result']={'min_reallocation_cad':minimum,'multiple_optima':analysis['optimal_face']['non_unique_witness_found']}
  else:
   directory=ROOT/'data/alphaforge_starter';meta=analysis['method']['metadata'];start,end=meta['start'],meta['end'];rows=list(csv.DictReader((directory/'prices_daily.csv').open()));prices={(r['date'],r['ticker']):r for r in rows if r['date'] in {start,end}};fx={r['date']:float(r['usdcad']) for r in csv.DictReader((directory/'fx_usdcad_daily.csv').open())};fx_dates=sorted(fx)
   def cad(t,date):
    r=prices[(date,t)];multiplier=fx[max(x for x in fx_dates if x<=date)] if r['currency']=='USD' else 1;return float(r['adj_close'])*multiplier
   proof=[]
   for o in analysis['options']:
    ending=sum(25000*w*cad(t,end)/cad(t,start) for t,w in o['weights'].items());recorded=o['metrics']['ending_value_cad']['value'];checked(abs(ending-recorded)<=.0050001,'amira ending wealth from raw CSV');proof.append({'option':o['id'],'raw_csv_ending_cad':ending,'recorded_rounded_cad':recorded,'difference_cad':ending-recorded})
   for f in analysis['provenance']['data']:checked(hashlib.sha256((directory/f['file']).read_bytes()).hexdigest()==f['sha256'],'amira dataset hash')
   entry['independent_arithmetic']={'window':[start,end],'options':proof,'method':'Somme des quantités initiales × prix ajusté final converti CAD ; csv standard, sans appels aux modules financiers du produit.','scope':'Valeur finale seulement ; pas nouvelle validation exhaustive volatilité/drawdown.'};c['result']={'window':[start,end],'options':proof}
  report['checks'][name]=entry
 manifest['status']='verified_complete';manifest['verification_report']='audit_live_cases.json';(OUT/'live_cases.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));(OUT/'audit_live_cases.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({n:{k:v[k] for k in ['dossier_id','revision','status','artifacts_hashed','method']} for n,v in report['checks'].items()},indent=2))
if __name__=='__main__':main()
