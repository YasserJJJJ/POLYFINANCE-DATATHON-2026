"""Create exactly two fresh, authorized AWS studies; never auto-retry POST."""
import datetime,json,pathlib,urllib.request,time
BASE='http://127.0.0.1:8768'
OUT=pathlib.Path(__file__).parent
STATE=OUT/'live_cases.json'
def get(path): return json.load(urllib.request.urlopen(BASE+path,timeout=15))
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(value):
 tmp=STATE.with_suffix('.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2));tmp.replace(STATE)
def main():
 if STATE.exists(): raise SystemExit('Already recorded: inspect existing IDs before any new create.')
 examples=get('/api/dossiers/examples')['examples'];record={'created_at':now(),'api':BASE,'use_ai':True,'preflight':'aws_preflight.json','cases':{},'status':'launching'};save(record)
 for name in ('robert','amira'):
  e=next(x for x in examples if x['id']==name);payload={'prompt':e['prompt'],'facts':e['facts'],'use_ai':True}
  if name=='amira': assert payload['facts']['historical_policy']=={'redistribution':'proportional_other_holdings','window':{'kind':'all_common_available'}}
  (OUT/(name+'-request.json')).write_text(json.dumps(payload,ensure_ascii=False,indent=2))
  request=urllib.request.Request(BASE+'/api/dossiers',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
  with urllib.request.urlopen(request,timeout=20) as response:
   data=json.load(response);status=response.status
  (OUT/(name+'-created.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2))
  record['cases'][name]={'id':data['id'],'active_run_id':data.get('active_run_id'),'http_status':status,'created_at':now(),'request':name+'-request.json','latest_status':data['status'],'latest_revision':data['revision'],'snapshot':name+'-created.json'};save(record)
  print(name,data['id'],status,data['status'],flush=True)
 record['status']='running';save(record)
 if len(record['cases'])!=2: raise RuntimeError('Both cases were not launched.')
if __name__=='__main__':main()
