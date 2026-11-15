/*
 * Real local end-to-end UI exercise. No intercepted success responses or fixture
 * results. --ai explicitly enables billable calls through the application's
 * configured Bedrock route; without it this test requests deterministic mode.
 *
 * WORKBENCH_BASE=http://127.0.0.1:8768 node tests/workbench_ui.cjs --ai
 * WORKBENCH_DOSSIER=<existing id> skips creation and revision, for visual review.
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {chromium} = require("../runtime/browser-check/node_modules/playwright");
const base = process.env.WORKBENCH_BASE || "http://127.0.0.1:8768";
const existing = process.env.WORKBENCH_DOSSIER || null;
const useAI = process.argv.includes("--ai");
const out = path.resolve(process.env.WORKBENCH_OUTPUT || (existing ? "artifacts/workbench-ui/review" : "artifacts/workbench-ui"));
fs.mkdirSync(out, {recursive:true});
const sleep = ms => new Promise(resolve => setTimeout(resolve,ms));
const report = {base,started_at:new Date().toISOString(),use_ai:useAI,existing_dossier:existing,checks:[],console_errors:[],request_ids:[]};
let browser;
async function read(id) {
  const response=await fetch(`${base}/api/dossiers/${id}`);
  assert.equal(response.status,200,"Dossier API must respond");
  return response.json();
}
async function waitTerminal(id) {
  let previous="", snapshot;
  for(let index=0;index<320;index++){
    snapshot=await read(id);
    const run=snapshot.runs.at(-1);
    const status=`${snapshot.status}/${run?.current_role}/r${snapshot.revision}`;
    if(status!==previous){console.log(status);previous=status;}
    if(["complete","waiting","error","failed","paused"].includes(snapshot.status)){
      if(["error","failed"].includes(snapshot.status)) {
        fs.writeFileSync(path.join(out,"failed-snapshot.json"),JSON.stringify(snapshot,null,2));
        throw new Error(`Dossier ${snapshot.status}: ${JSON.stringify(run?.error)}`);
      }
      return snapshot;
    }
    await sleep(1500);
  }
  throw new Error("Dossier did not finish inside 8 minutes; it may still be running.");
}
async function checkOverflow(page,label){
  const overflow=await page.evaluate(()=>({width:innerWidth,document:document.documentElement.scrollWidth}));
  assert.ok(overflow.document<=overflow.width,`${label} overflow ${JSON.stringify(overflow)}`);
  report.checks.push(`${label}: no horizontal page overflow`);
}
async function main(){
  browser=await chromium.launch({headless:true});
  const context=await browser.newContext({viewport:{width:1440,height:1080},deviceScaleFactor:1,acceptDownloads:true});
  const page=await context.newPage();
  page.on("pageerror",error=>report.console_errors.push(error.message));
  await page.goto(`${base}/${existing?`?dossier=${encodeURIComponent(existing)}`:""}`);
  let id=existing,snapshot;
  if(!existing){
    await page.locator('[data-example="robert"]').waitFor();
    await page.screenshot({path:path.join(out,"start-desktop.png"),fullPage:true});
    await page.locator('[data-example="robert"]').click();
    assert.equal(await page.locator("#withdrawal").inputValue(),"30000");
    assert.equal(JSON.parse(await page.locator("#facts-json").inputValue()).capital_cad,100000);
    report.checks.push("Robert loads explicit editable facts without creating a dossier");
    await page.locator("#use-ai").setChecked(useAI);
    const created=page.waitForResponse(response=>response.url()===`${base}/api/dossiers`&&response.request().method()==="POST");
    await page.locator("#create-submit").click();
    const result=await (await created).json();
    id=result.id || result.dossier?.id;
    assert.ok(id,"create must return an id");
    console.log(`CREATED ${id}`);
    report.dossier_id=id;
    fs.writeFileSync(path.join(out,"current-run.json"),JSON.stringify({id,useAI,base},null,2));
    snapshot=await waitTerminal(id);
    fs.writeFileSync(path.join(out,"robert-30000.json"),JSON.stringify(snapshot,null,2));
    assert.equal(snapshot.active_problem.withdrawal_cad,30000);
    assert.ok(snapshot.current_view?.usable,"current view must be usable");
    await page.locator("#refresh").click();
    await page.waitForFunction(()=>document.querySelector("#overview .answer-panel"));
    await page.screenshot({path:path.join(out,"robert-30000-desktop.png"),fullPage:true});
    report.checks.push("Robert 30000 reaches a usable current view through the real UI/API");
    await page.locator("#revision-message").fill("Le retrait sera finalement de 40 000 CAD.");
    await page.locator("#revision-withdrawal").fill("40000");
    const revisionResponse=page.waitForResponse(response=>response.url()===`${base}/api/dossiers/${id}/revise`&&response.request().method()==="POST");
    await page.locator("#revise-submit").click();
    const response=await revisionResponse;
    assert.equal(response.status(),202,"Revision must be accepted");
    const initialRevision=await response.json();
    assert.equal(initialRevision.current_view,null,"Revision must invalidate prior current view atomically");
    report.checks.push("Correction atomically removes previous current view");
    console.log(`REVISED ${id}`);
    snapshot=await waitTerminal(id);
    fs.writeFileSync(path.join(out,"robert-40000.json"),JSON.stringify(snapshot,null,2));
    assert.equal(snapshot.active_problem.withdrawal_cad,40000);
    assert.ok(snapshot.current_view?.usable);
    assert.equal(snapshot.comparison.after.inputs.withdrawal_cad,40000);
    assert.equal(snapshot.comparison.before.inputs.withdrawal_cad,30000);
    await page.locator("#refresh").click();
    await page.waitForFunction(()=>document.querySelector("#context").textContent.match(/40[\s\u00a0\u202f,]*000/));
    report.checks.push("Revised 40000 result and comparison retain 30000 prior scope");
  }else{
    report.dossier_id=id;
    snapshot=await waitTerminal(id);
    await page.waitForFunction(()=>document.querySelector("#overview .answer-panel"));
  }
  await page.locator('[data-tab="overview"]').click();
  await page.screenshot({path:path.join(out,"overview-desktop.png"),fullPage:true});
  await page.screenshot({path:path.join(out,"overview-viewport.png")});
  await checkOverflow(page,"Desktop overview");
  assert.equal(await page.locator(".role-card").count(),4);
  report.checks.push("Four distinct role cards are displayed");
  await page.locator('[data-tab="evidence"]').click();
  await page.waitForTimeout(100);
  await page.screenshot({path:path.join(out,"evidence-desktop.png"),fullPage:true});
  if(await page.locator(".source-card").count()){
    await page.locator(".source-card button").first().click();
    assert.equal(await page.locator("#inspector").evaluate(node=>node.open),true);
    await page.keyboard.press("Escape");
    report.checks.push("Evidence provenance opens in keyboard-dismissable native dialog");
  }
  await page.locator('[data-tab="activity"]').click();
  await page.screenshot({path:path.join(out,"activity-desktop.png"),fullPage:true});
  report.request_ids=snapshot.attempts.filter(item=>item.request_id).map(item=>({role:item.role,tool:item.tool,id:item.request_id}));
  if(useAI || existing)report.checks.push(`${report.request_ids.length} actual provider request identifiers retained`);
  await page.locator('[data-tab="history"]').click();
  await page.screenshot({path:path.join(out,"history-desktop.png"),fullPage:true});
  const downloadPromise=page.waitForEvent("download");
  await page.locator("#export").click();
  const download=await downloadPromise;
  await download.saveAs(path.join(out,"ui-export.json"));
  assert.equal(JSON.parse(fs.readFileSync(path.join(out,"ui-export.json"),"utf8")).id,id);
  report.checks.push("UI export contains the selected dossier identity");
  const oldPath=path.resolve("artifacts/workbench-ui/robert-30000.json");
  if(fs.existsSync(oldPath)){
    const old=JSON.parse(fs.readFileSync(oldPath,"utf8"));
    if(old.id===id && old.revision<snapshot.revision){
      // Browser-only replay of an authentic response captured before revision.
      // Does not modify the server or invent an analysis.
      await page.route(`${base}/api/dossiers/${id}`,route=>route.fulfill({status:200,contentType:"application/json",body:JSON.stringify(old)}),{times:1});
      const stale=page.waitForResponse(response=>response.url()===`${base}/api/dossiers/${id}`&&response.request().method()==="GET");
      await page.locator("#refresh").click();
      await stale;await page.waitForTimeout(150);
      assert.ok((await page.locator("#revision-badge").textContent()).includes(String(snapshot.revision)));
      assert.ok((await page.locator("#context").textContent()).match(/40[\s\u00a0\u202f,]*000/));
      report.checks.push("Browser-only replay of authentic old GET cannot restore prior revision or 30000 mandate");
    }
  }
  await page.route(`${base}/api/dossiers/${id}`,route=>route.abort("connectionfailed"));
  await page.locator("#refresh").click();
  await page.waitForFunction(()=>!document.querySelector("#global-error").hidden);
  assert.ok(await page.locator("#global-error").textContent());
  await page.unroute(`${base}/api/dossiers/${id}`);
  await page.locator("#refresh").click();
  await page.waitForFunction(()=>document.querySelector("#global-error").hidden);
  report.checks.push("Browser-only network failure is visible and refresh recovers");
  await page.setViewportSize({width:390,height:844});
  await page.locator('[data-tab="overview"]').click();
  await page.screenshot({path:path.join(out,"overview-mobile.png"),fullPage:true});
  await page.screenshot({path:path.join(out,"overview-mobile-viewport.png")});
  await checkOverflow(page,"Mobile overview");
  await page.locator('[data-tab="evidence"]').click();
  await page.screenshot({path:path.join(out,"evidence-mobile.png"),fullPage:true});
  await checkOverflow(page,"Mobile evidence");
  await page.locator('[data-tab="mandate"]').click();
  await checkOverflow(page,"Mobile mandate");
  assert.ok((await page.locator("#mandate").textContent()).includes("Une question de preuve ou de méthode ne vous demande pas"));
  report.checks.push("Question graph is separate from personal clarification controls");
  snapshot=await read(id);
  assert.ok(snapshot.events.some(event=>event.kind==="view_displayed"&&event.payload?.accepted===false));
  report.checks.push("Display event is recorded explicitly without acceptance");
  assert.equal(report.console_errors.length,0);
  report.finished_at=new Date().toISOString();
  report.status="passed";
  fs.writeFileSync(path.join(out,"verification.json"),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
}
main().catch(error=>{
  report.status="failed";report.error=error.stack;report.finished_at=new Date().toISOString();
  fs.writeFileSync(path.join(out,"verification.json"),JSON.stringify(report,null,2));
  console.error(error);process.exitCode=1;
}).finally(async()=>{await browser?.close();});
