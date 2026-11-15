/* Component tests only: local finance results are injected into an isolated
 * browser. These snapshots do not claim agent execution, and no server dossier
 * is created. No AWS call. */
const assert=require("node:assert/strict");
const {execFileSync}=require("node:child_process");
const fs=require("node:fs");
const path=require("node:path");
const {chromium}=require("../runtime/browser-check/node_modules/playwright");
const base=process.env.WORKBENCH_BASE || "http://127.0.0.1:8768";
const out=path.resolve("artifacts/workbench-ui/component-tests");
fs.mkdirSync(out,{recursive:true});
const data=JSON.parse(execFileSync(".venv/bin/python",["-c",`
import copy,json
from alphaforge_app.decision.finance import analyze,examples
robert,amira=[x["facts"] for x in examples()]
impossible=copy.deepcopy(robert)
impossible["withdrawal_cad"]=200000
print(json.dumps({"before":analyze(robert),"after":analyze(impossible),"historical":analyze(amira),"problem":impossible,"historical_problem":amira}))
`],{encoding:"utf8",maxBuffer:12*1024*1024}));
assert.equal(data.after.status,"infeasible");
assert.ok(data.historical.options.length>=2);
let snapshot={
  id:"component-test-only",title:"TEST DE RENDU — aucune exécution d’agent",revision:2,status:"complete",
  active_problem:data.problem,current_analysis:{id:"analysis",ref:"analysis@2",version:2,usable:true,content:data.after},
  current_view:null,artifacts:[],questions:[],evidence:[],events:[],tasks:[],attempts:[],runs:[],revisions:[],
  comparison:{before:data.before,after:data.after,changed_fields:["withdrawal_cad"],invalidated:[],reused:[]},
  route:{mode:"test de composant local sans inférence"},limitations:[],
};
let browser;
(async()=>{
  browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:1440,height:1080}});
  const errors=[];page.on("pageerror",e=>errors.push(e.message));
  await page.route("**/api/dossiers**",async route=>{
    const url=new URL(route.request().url());
    const payload=url.pathname.endsWith("/examples")?{examples:[]}:url.pathname==="/api/dossiers"?{dossiers:[]} : snapshot;
    await route.fulfill({status:200,contentType:"application/json",body:JSON.stringify(payload)});
  });
  await page.goto(`${base}/?dossier=component-test-only`);
  await page.locator('[data-tab="history"]').click();
  await page.waitForFunction(()=>document.querySelector("#history").textContent.includes("aucune option admissible dans le modèle"));
  const lastCells=await page.locator("#history .data-table tbody tr td:last-child").allTextContents();
  assert.ok(lastCells.length>0 && lastCells.every(value=>value.trim().startsWith("—")));
  assert.ok((await page.locator("#history").textContent()).includes("témoins de solution"));
  await page.locator("#tab-history").screenshot({path:path.join(out,"infeasible-comparison.png")});
  snapshot={...snapshot,revision:3,active_problem:data.historical_problem,current_analysis:{...snapshot.current_analysis,content:data.historical},comparison:null};
  await page.locator("#refresh").click();
  await page.locator('[data-tab="overview"]').click();
  await page.waitForFunction(()=>!!document.querySelector(".history-chart"));
  const headings=await page.locator("#overview .data-table th").allTextContents();
  assert.ok(headings.some(value=>value.includes("Rendement cumulé")));
  assert.ok(headings.some(value=>value.includes("Repli maximal")));
  assert.equal(await page.locator(".history-chart path").count(),2);
  await page.locator(".history-chart").screenshot({path:path.join(out,"historical-chart-desktop.png")});
  await page.setViewportSize({width:390,height:844});
  await page.locator(".history-chart").screenshot({path:path.join(out,"historical-chart-mobile.png")});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.equal(errors.length,0);
  fs.writeFileSync(path.join(out,"verification.json"),JSON.stringify({
    status:"passed",scope:"Component rendering using current local finance engine; browser-only injected snapshots, not a four-agent execution.",
    new_aws_inferences:0,checks:["Infeasible after-case does not promote baseline to solution","New unavailable option values remain dashes, not zero turnover","Multiple-optima witness qualification visible","Historical windows expose return and drawdown","Two real historical series rendered","390px no page overflow","No JavaScript error"],
    at:new Date().toISOString()
  },null,2));
  console.log("7 component rendering checks passed; no AWS inference.");
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{await browser?.close();});
