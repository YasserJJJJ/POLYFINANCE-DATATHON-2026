/* Independent Folio browser review.
 * Read/preview modes do not create a dossier or invoke any model.
 * revision40 / revision1000 / revisionloss1000 are explicit four-agent operations.
 * revision1000 records an audit-scenario mistake (withdrawal changed to 1000).
 * revisionloss1000 corrects it to withdrawal 40000 / loss limit 1000.
 *
 * FOLIO_REVIEW_MODE=read|preview|history|mobile|latency|missing|export|previewexport
 * Mutation modes revision40, revisionloss1000 and variant require their exact
 * recorded starting state. The erroneous revision1000 mode is disabled.
 * node tests/folio_review.cjs
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require('../runtime/browser-check/node_modules/playwright');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'docs/folio/proofs');
const BASE = process.env.FOLIO_URL || 'http://127.0.0.1:8768';
const MODE = process.env.FOLIO_REVIEW_MODE || 'read';
const CASES = JSON.parse(fs.readFileSync(path.join(OUT, 'live_cases.json'), 'utf8'));
const ID = {
  robert: '71c8fb4b9d5e45fe98a4b4942e07c41e',
  amira: '49ed5ae5903f41c297909b644ff7599a',
};
const report = {mode: MODE, started_at: new Date().toISOString(), observations: [], errors: [], requests: []};
const note = (name, details={}) => {
  report.observations.push({name, ...details});
  console.log(name, JSON.stringify(details));
};
async function get(url) {
  const r = await fetch(BASE + url);
  assert.equal(r.status, 200, `${url}: ${r.status}`);
  return r.json();
}
async function snapshot(id=ID.robert) { return get(`/api/folio/dossiers/${id}`); }
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
let browser, context, page;
async function open(id=ID.robert, view='overview', revision=null) {
  await page.goto(`${BASE}/?dossier=${id}&view=${view}${revision==null?'':'&revision='+revision}`);
  await page.locator('#app .dossier-tools').waitFor();
  await page.locator('#app .notice.busy').waitFor({state:'hidden'});
  await page.locator('#app main h1, #app h1').first().waitFor();
}
async function clickView(view) {
  await page.locator(`[data-action="view"][data-view="${view}"]`).first().click();
}
async function proof(id='method') {
  const trigger = page.locator(`[data-action="proof"][data-proof="${id}"]`).first();
  await trigger.click();
  await page.locator('#evidence[open]').waitFor();
  assert.equal(await page.evaluate(() => document.querySelector('#evidence').contains(document.activeElement)), true);
  const text = await page.locator('#proof-content').innerText();
  await page.keyboard.press('Escape');
  assert.equal(await trigger.evaluate(el => el===document.activeElement), true);
  note('proof_context_and_focus', {id, excerpt: text.slice(0, 300)});
}
async function submitPreview(value) {
  await clickView('revise');
  await page.locator('[name="withdrawal_cad"]').fill(String(value));
  await page.locator('[name="intent"][value="preview"]').check();
  const response = page.waitForResponse(r => r.url().endsWith('/preview') && r.request().method()==='POST');
  await page.locator('form[data-revision] button[type="submit"]').click();
  const r = await response;
  assert.equal(r.status(), 200);
  const valueOut = await r.json();
  await page.waitForURL(/view=compare/);
  return valueOut;
}
async function readReview() {
  for (const name of ['robert', 'amira']) {
    const start = await snapshot(ID[name]);
    await open(ID[name]);
    await page.screenshot({path: path.join(OUT, `${name}-folio-accessible.png`), fullPage: true});
    const conditions = await page.locator('[data-invariant="limits"]').allTextContents();
    assert.ok(conditions.length, 'Limits must be explicit, including in accessible view');
    const postsBefore = report.requests.filter(r=>r.method==='POST').length;
    await page.locator('[data-action="level"][data-level="deep"]').first().click();
    assert.deepEqual(await page.locator('[data-invariant="limits"]').allTextContents(), conditions);
    await proof('method');
    await page.screenshot({path: path.join(OUT, `${name}-folio-deep.png`), fullPage: true});
    await page.reload();
    await page.locator('#app h1').first().waitFor();
    assert.equal(report.requests.filter(r=>r.method==='POST').length, postsBefore);
    const end = await snapshot(ID[name]);
    assert.equal(end.snapshot.revision, start.snapshot.revision);
    assert.deepEqual(end.version.analysis, start.version.analysis);
    note('read_reload_adaptation_no_mutation', {case:name, revision:end.snapshot.revision, conditions:conditions.join('\n')});
    await page.locator('[data-action="level"][data-level="accessible"]').first().click();
  }
}
async function previewReview() {
  const before = await snapshot();
  await open();
  const first = await submitPreview(40000);
  assert.equal(first.receipt.inference_calls, 0);
  assert.equal(first.receipt.product_mutations, 0);
  assert.equal(first.version.stats.min_reallocation_cad, 40000);
  await page.reload();
  await page.locator('[data-action="undo"]').first().waitFor();
  assert.equal(await page.locator('body').getByText('Aperçu local restauré', {exact:false}).count()>0, true);
  await page.locator('[data-action="undo"]').first().click();
  await page.waitForURL(/view=overview/);
  const impossible = await submitPreview(120000);
  assert.equal(impossible.version.analysis.status, 'infeasible');
  assert.deepEqual(impossible.version.analysis.options, []);
  assert.equal(impossible.version.stats.shortfall_cad, 20000);
  assert.equal(impossible.version.stats.min_reallocation_cad, undefined);
  await proof('method');
  await page.screenshot({path:path.join(OUT,'folio-impossible.png'),fullPage:true});
  await page.locator('[data-action="undo"]').first().click();
  await page.waitForURL(/view=overview/);
  const missing = await submitPreview('');
  assert.equal(missing.version.analysis.status, 'missing_input');
  assert.deepEqual(missing.version.analysis.options, []);
  assert.ok(missing.version.questions.length);
  await page.screenshot({path:path.join(OUT,'folio-incomplete.png'),fullPage:true});
  await page.locator('[data-action="undo"]').first().click();
  await page.waitForURL(/view=overview/);
  assert.deepEqual((await snapshot()).snapshot, before.snapshot);
  note('preview_missing_impossible_no_mutation', {initial_revision:before.snapshot.revision, preview_receipt:first.receipt});
}
async function persistentRevision(target, lossLimit=null) {
  const before = await snapshot();
  const expectedBefore = lossLimit!==null?1000:target===40000?30000:40000;
  assert.equal(before.version.problem.withdrawal_cad, expectedBefore,
    'Refuses to rerun a committed review correction or overwrite an unexpected dossier');
  await open(ID.robert, 'revise');
  await page.locator('[name="withdrawal_cad"]').fill(String(target));
  if(lossLimit!==null)await page.locator('[name="scenario_loss_limit_cad"]').fill(String(lossLimit));
  await page.locator('[name="intent"][value="replace"]').check();
  await page.locator('[name="message"]').fill(lossLimit!==null
    ?`Correction du scénario de revue : le retrait reste ${target} CAD ; c’est la perte admise dans chaque choc qui devient ${lossLimit} CAD. Le retrait de 1000 CAD de r15 résultait d’une mauvaise saisie du relecteur. Positions initiales inchangées.`
    :`Revue indépendante Folio : correction explicite du retrait à ${target} CAD, positions initiales inchangées.`);
  const response = page.waitForResponse(r => r.url().endsWith('/revise') && r.request().method()==='POST');
  await page.locator('form[data-revision] button[type="submit"]').click();
  const r = await response;
  assert.equal(r.status(), 202);
  const accepted = await r.json(), body = r.request().postDataJSON();
  fs.writeFileSync(path.join(OUT, `revision-${lossLimit!==null?'loss'+lossLimit:target}-accepted.json`), JSON.stringify({body,response:accepted}, null,2));
  // Replay the identical accepted key: no new operation. Never use a new key here.
  const replay = await fetch(r.url(), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
  assert.equal(replay.status,202);
  const same = await replay.json();
  assert.equal(same.id, accepted.id);
  assert.equal(same.active_run_id, accepted.active_run_id);
  const mismatch = await fetch(r.url(), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({...body,message:body.message+' divergent'})});
  assert.equal(mismatch.status,409);
  let final;
  const until = Date.now()+12*60*1000;
  while(Date.now()<until) {
    final = await snapshot();
    if(final.snapshot.status==='complete') break;
    if(['error','waiting'].includes(final.snapshot.status)) throw new Error(`Study stopped: ${final.snapshot.status}`);
    console.log(`Awaiting real AWS agents: revision ${final.snapshot.revision}, status ${final.snapshot.status}`);
    await pause(15000);
  }
  assert.equal(final.snapshot.status,'complete');
  assert.equal(final.version.problem.withdrawal_cad,target);
  if(lossLimit!==null)assert.equal(final.version.problem.scenario_loss_limit_cad,lossLimit);
  assert.equal(final.snapshot.runs.length,before.snapshot.runs.length+1);
  const calls=final.snapshot.attempts.filter(a=>a.task_id?.startsWith(accepted.active_run_id)&&a.tool==='bedrock.converse');
  assert.equal(calls.length,4);
  assert.ok(calls.every(a=>a.status==='complete'&&a.request_id));
  fs.writeFileSync(path.join(OUT,`robert-r${final.snapshot.revision}.json`),JSON.stringify(final,null,2));
  await open();
  await page.screenshot({path:path.join(OUT,`robert-folio-r${final.snapshot.revision}.png`),fullPage:true});
  note('persistent_revision_and_idempotence',{from:expectedBefore,to:target,loss_limit:lossLimit??final.version.problem.scenario_loss_limit_cad,revision:final.snapshot.revision,run:accepted.active_run_id,minimum:final.version.stats.min_reallocation_cad,aws_request_ids:calls.map(a=>a.request_id)});
}
async function historyReview() {
  const latest=await snapshot();
  assert.ok(latest.current_revision>5,'History review requires committed correction');
  await open(ID.robert,'overview',5);
  await page.locator('.export-menu summary').click();
  const downloadEvent=page.waitForEvent('download');
  await page.locator('[data-action="export"][data-format="json"]').first().click();
  const download=await downloadEvent;
  const file=path.join(OUT,'folio-export-r5.json');
  await download.saveAs(file);
  const content=JSON.parse(fs.readFileSync(file,'utf8'));
  assert.equal(content.revision,5);
  assert.equal(content.active_problem.withdrawal_cad,30000);
  assert.ok(content.events.every(e=>e.revision<=5));
  const preview=await submitPreview(35000);
  assert.equal(preview.receipt.base_revision,5);
  await page.reload();
  await page.locator('[data-action="undo"]').first().waitFor();
  const saved=await page.evaluate(id=>JSON.parse(localStorage.getItem(`alphaforge.folio.v1.preview.${id}`)),ID.robert);
  assert.equal(saved.baseRevision,5);
  assert.equal(saved.currentRevision,latest.current_revision);
  await page.locator('[data-action="latest"]').first().click();
  await page.reload();
  await page.locator('#app h1').first().waitFor();
  assert.equal(await page.locator('[data-action="undo"]').count(),0);
  assert.equal((await snapshot()).snapshot.revision,latest.snapshot.revision);
  note('archive_export_and_preview_scope',{archive:5,current:latest.current_revision,preview_base:preview.receipt.base_revision});
}
async function mobileReview() {
  for (const width of [390,320]) {
    await page.setViewportSize({width,height:844});
    await open();
    const measure=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));
    assert.ok(measure.document<=measure.viewport+1,JSON.stringify(measure));
    await page.screenshot({path:path.join(OUT,`folio-mobile-${width}.png`),fullPage:true});
    await clickView('compare');
    const tableMeasure=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth}));
    assert.ok(tableMeasure.document<=tableMeasure.viewport+1,JSON.stringify(tableMeasure));
    const axeFile=path.join(ROOT,'runtime/p6-audit/node_modules/axe-core/axe.min.js');
    if(fs.existsSync(axeFile)) {
      await page.addScriptTag({path:axeFile});
      const results=await page.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}));
      fs.writeFileSync(path.join(OUT,`folio-axe-${width}.json`),JSON.stringify(results,null,2));
      note('mobile_axe',{width,violations:results.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))});
    }
  }
}
async function latencyReview() {
  // Only response transport is delayed. The real deterministic preview is used.
  // No model request or durable correction is performed by this mode.
  await open(ID.robert,'revise',5);
  let release, reached;
  const arrived=new Promise(resolve=>reached=resolve);
  const gate=new Promise(resolve=>release=resolve);
  const url=`${BASE}/api/folio/dossiers/${ID.robert}/preview`;
  await page.route(url,async route=>{
    const response=await route.fetch();
    reached();
    await gate;
    await route.fulfill({response});
  },{times:1});
  await page.locator('[name="withdrawal_cad"]').fill('40000');
  await page.locator('[name="intent"][value="preview"]').check();
  await page.locator('form[data-revision] button[type="submit"]').click();
  await arrived;
  await page.locator('[name="withdrawal_cad"]').fill('45000');
  release();
  await page.waitForURL(/view=compare/);
  const state=await page.evaluate(id=>({
    draft:JSON.parse(localStorage.getItem(`alphaforge.folio.v1.draft.${id}`)),
    preview:JSON.parse(localStorage.getItem(`alphaforge.folio.v1.preview.${id}`)),
  }),ID.robert);
  assert.equal(state.draft.withdrawal_cad,'45000');
  assert.equal(state.preview.response.version.problem.withdrawal_cad,40000);
  await clickView('revise');
  assert.equal(await page.locator('[name="withdrawal_cad"]').inputValue(),'45000');
  note('post_submit_draft_preserved',{sent:40000,new_draft:45000,result:state.preview.response.version.stats.min_reallocation_cad});
  await page.locator('[data-action="undo"]').first().click();
  await page.waitForURL(/view=overview/);
  await clickView('revise');
  await page.locator('[data-action="discard-draft"]').first().click();
  await page.locator('[name="withdrawal_cad"]').fill('35000');
  let releaseLate, reachedLate;
  const arrivedLate=new Promise(resolve=>reachedLate=resolve);
  const gateLate=new Promise(resolve=>releaseLate=resolve);
  await page.route(url,async route=>{
    const response=await route.fetch();
    reachedLate();
    await gateLate;
    await route.fulfill({response});
  },{times:1});
  await page.locator('form[data-revision] button[type="submit"]').click();
  await arrivedLate;
  await page.locator('[data-action="view"][data-view="library"]').first().click();
  await page.locator(`[data-action="open"][data-id="${ID.amira}"]`).first().click();
  await page.waitForURL(new RegExp(ID.amira));
  releaseLate();
  await pause(300);
  assert.ok(page.url().includes(ID.amira));
  assert.ok((await page.locator('#app').innerText()).includes('Changer l’exposition'));
  note('late_preview_does_not_replace_another_dossier',{retained:ID.amira});
  await open(ID.robert,'revise',5);
  await page.locator('[data-action="discard-draft"]').first().click();
  await page.locator('[name="withdrawal_cad"]').fill('35000');
  await page.route(url,route=>route.abort('connectionfailed'),{times:1});
  await page.locator('form[data-revision] button[type="submit"]').click();
  await page.locator('[role="alert"]').waitFor();
  assert.equal(await page.locator('[name="withdrawal_cad"]').inputValue(),'35000');
  await page.locator('form[data-revision] button[type="submit"]').click();
  await page.waitForURL(/view=compare/);
  note('network_error_preserves_draft_and_can_recover',{withdrawal:35000});
  await page.locator('[data-action="undo"]').first().click();
}
async function missingQuestionReview() {
  await open(ID.robert,'revise',5);
  const result=await submitPreview('');
  assert.equal(result.version.analysis.status,'missing_input');
  for(const q of result.version.questions) {
    assert.ok((await page.locator('#app').innerText()).includes(q.question),
      `A real missing-input question is not visible: ${q.question}`);
  }
  await page.screenshot({path:path.join(OUT,'folio-incomplete-corrected.png'),fullPage:true});
  note('missing_input_question_visible',{questions:result.version.questions});
  await page.locator('[data-action="undo"]').first().click();
}
async function variantReview() {
  const output=path.join(OUT,'amira-variant-created.json');
  assert.equal(fs.existsSync(output),false,'Refuses to create a second review variant');
  const parent=await snapshot(ID.amira);
  await open(ID.amira,'revise',5);
  await page.locator('[name="comparison_weight"]').fill('5');
  await page.locator('[name="intent"][value="variant"]').check();
  await page.locator('[name="message"]').fill('Variante de revue Folio : comparer une exposition directe initiale de 5 % à TSLA, avec la même convention historique et la même fenêtre que la version 5.');
  const response=page.waitForResponse(r=>r.url().endsWith('/revise')&&r.request().method()==='POST');
  await page.locator('form[data-revision] button[type="submit"]').click();
  const r=await response;
  assert.equal(r.status(),202);
  const accepted=await r.json(),body=r.request().postDataJSON();
  assert.notEqual(accepted.id,ID.amira);
  fs.writeFileSync(output,JSON.stringify({body,response:accepted},null,2));
  let final;
  const until=Date.now()+12*60*1000;
  while(Date.now()<until) {
    final=await snapshot(accepted.id);
    if(final.snapshot.status==='complete')break;
    if(['error','waiting'].includes(final.snapshot.status))throw new Error(`Variant stopped: ${final.snapshot.status}`);
    console.log(`Awaiting real variant agents: revision ${final.snapshot.revision}, ${final.snapshot.status}`);
    await pause(15000);
  }
  assert.equal(final.snapshot.status,'complete');
  assert.equal(final.version.problem.comparison.target_weight,.05);
  assert.equal(final.version.origin.source_revision,5);
  assert.equal(final.version.origin.dossier_id,ID.amira);
  assert.deepEqual((await snapshot(ID.amira)).snapshot,parent.snapshot);
  const calls=final.snapshot.attempts.filter(a=>a.tool==='bedrock.converse');
  assert.equal(calls.length,4);
  assert.ok(calls.every(a=>a.status==='complete'&&a.request_id));
  fs.writeFileSync(path.join(OUT,'amira-variant-complete.json'),JSON.stringify(final,null,2));
  await open(accepted.id);
  await clickView('compare');
  await page.screenshot({path:path.join(OUT,'amira-folio-variant.png'),fullPage:true});
  note('historical_variant_preserves_parent',{parent:ID.amira,child:accepted.id,source_revision:5,comparison:.05,aws_request_ids:calls.map(a=>a.request_id),stats:final.version.stats});
}
async function exportReview() {
  await open(ID.robert,'overview',5);
  await page.locator('.export-menu summary').click();
  const next=page.waitForEvent('download');
  await page.locator('[data-action="export"][data-format="json"]').first().click();
  const download=await next, file=path.join(OUT,'folio-export-r5.json');
  await download.saveAs(file);
  const response=await fetch(`${BASE}/api/folio/dossiers/${ID.robert}/export?revision=5`);
  const original=Buffer.from(await response.arrayBuffer()), downloaded=fs.readFileSync(file);
  assert.equal(downloaded.equals(original),true,'Export must preserve server bytes');
  const {execFileSync}=require('node:child_process');
  const result=execFileSync(path.join(ROOT,'.venv/bin/python'),['-c',`
import json,hashlib,sys
d=json.load(open(sys.argv[1]))
for a in d['artifacts']:
 h=hashlib.sha256(json.dumps(a['content'],sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
 assert h==a['hash'],a['ref']
print(json.dumps({'revision':d['revision'],'artifacts_hashed':len(d['artifacts'])}))
`,file],{encoding:'utf8'});
  note('raw_export_bytes_and_artifact_hashes',{bytes:downloaded.length,...JSON.parse(result)});
}
async function previewExportReview() {
  await open(ID.robert,'revise',5);
  const responseEvent=page.waitForResponse(r=>r.url().endsWith('/preview')&&r.request().method()==='POST');
  await submitPreview(35000);
  const original=await (await responseEvent).body();
  const files=[];
  for(const stage of ['before-reload','after-reload']) {
    if(stage==='after-reload') {
      await page.reload();
      await page.locator('[data-action="undo"]').first().waitFor();
    }
    await page.locator('.export-menu summary').click();
    const next=page.waitForEvent('download');
    await page.locator('[data-action="export"][data-format="json"]').first().click();
    const file=path.join(OUT,`folio-preview-export-${stage}.json`);
    await (await next).saveAs(file);
    assert.equal(fs.readFileSync(file).equals(original),true,stage+' bytes changed');
    files.push(file);
  }
  const {execFileSync}=require('node:child_process');
  const result=execFileSync(path.join(ROOT,'.venv/bin/python'),['-c',`
import json,hashlib,sys
d=json.load(open(sys.argv[1]))
digest=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
assert digest(d['version']['analysis'])==d['receipt']['result_sha256']
assert digest(d['version']['problem'])==d['receipt']['inputs_sha256']
assert d['receipt']['inference_calls']==0 and d['receipt']['product_mutations']==0
print(json.dumps({'result_sha256':d['receipt']['result_sha256'],'base_revision':d['receipt']['base_revision']}))
`,files[1]],{encoding:'utf8'});
  note('preview_export_bytes_and_hashes_after_reload',{bytes:original.length,...JSON.parse(result)});
  await page.locator('[data-action="undo"]').first().click();
}
async function finalReadReview() {
  await open();
  const delta=await page.locator('.revision-delta').first().innerText();
  assert.ok(delta.includes('Perte admise'));
  assert.ok(delta.includes('74 400') || delta.includes('74\u00a0400'));
  assert.ok(!delta.includes('Version précédente'),'The actual previous values must be shown');
  await page.screenshot({path:path.join(OUT,'folio-final-robert20.png'),fullPage:true});
  const variant=JSON.parse(fs.readFileSync(path.join(OUT,'amira-variant-created.json'),'utf8')).response.id;
  await open(variant,'compare');
  assert.ok((await page.locator('.delta-caption').innerText()).includes('Variante dans un dossier distinct'));
  await page.screenshot({path:path.join(OUT,'folio-final-amira-variant.png'),fullPage:true});
  await page.locator('[data-action="view"][data-view="library"]').first().click();
  await page.locator('#library-query').fill(ID.amira);
  await page.locator('#library-query').press('Enter');
  assert.equal(await page.locator('#evidence[open]').count(),0);
  assert.equal(await page.locator('.dossier-index li').count(),1);
  assert.equal(await page.locator('.dossier-index [data-action="open"]').getAttribute('data-id'),ID.amira);
  note('library_search_is_separate_from_evidence_search',{matched:ID.amira});
  await open(ID.robert,'overview',5);
  await page.locator('[data-action="search"]').first().click();
  await page.locator('#evidence input[name="query"]').fill('problem@1');
  await page.locator('#evidence form[data-search]').evaluate(form=>form.requestSubmit());
  await page.locator('#evidence [data-proof="artifact:problem@1"]').click();
  assert.ok((await page.locator('#proof-content').innerText()).includes('51547444544929a6182691bccb3d57de01f5dfb36f60082dfd5d6100f9c42cc7'));
  await page.keyboard.press('Escape');
  await page.screenshot({path:path.join(OUT,'folio-final-robert5.png'),fullPage:true});
  note('final_delta_variant_and_search',{revision:20,variant,archive:5});
}
(async()=>{
  assert.ok(['read','preview','revision40','revision1000','revisionloss1000','history','mobile','latency','missing','variant','export','previewexport','final'].includes(MODE));
  const health=await get('/api/health');
  assert.equal(health.application,'alphaforge');
  assert.ok(JSON.stringify(health).includes('Datathon_AlphaForge'));
  report.health=health;
  browser=await chromium.launch({headless:true});
  context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
  page=await context.newPage();
  page.on('pageerror',e=>report.errors.push(e.message));
  page.on('request',r=>{if(r.url().startsWith(BASE+'/api/'))report.requests.push({url:r.url(),method:r.method()});});
  if(MODE==='read')await readReview();
  if(MODE==='preview')await previewReview();
  if(MODE==='revision40')await persistentRevision(40000);
  if(MODE==='revision1000')throw new Error('Archived audit-scenario mistake. This incorrect-field operation is intentionally disabled; see REVUE.md.');
  if(MODE==='revisionloss1000')await persistentRevision(40000,1000);
  if(MODE==='history')await historyReview();
  if(MODE==='mobile')await mobileReview();
  if(MODE==='latency')await latencyReview();
  if(MODE==='missing')await missingQuestionReview();
  if(MODE==='variant')await variantReview();
  if(MODE==='export')await exportReview();
  if(MODE==='previewexport')await previewExportReview();
  if(MODE==='final')await finalReadReview();
  assert.deepEqual(report.errors,[]);
  report.status='passed';
})().catch(e=>{report.status='failed';report.failure=e.stack;console.error(e);process.exitCode=1;})
.finally(async()=>{
  report.finished_at=new Date().toISOString();
  fs.mkdirSync(OUT,{recursive:true});
  fs.writeFileSync(path.join(OUT,`browser-${MODE}.json`),JSON.stringify(report,null,2));
  await browser?.close();
});
