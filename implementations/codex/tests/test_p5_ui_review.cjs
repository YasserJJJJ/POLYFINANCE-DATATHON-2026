/* Browser component regression: injected snapshots, no dossier mutation and
 * no AWS inference. The separate ui_review.json records actual AWS dossiers. */
const assert = require("node:assert/strict");
const {chromium} = require("../runtime/browser-check/node_modules/playwright");
const base = process.env.WORKBENCH_BASE || "http://127.0.0.1:8768";
const capitalAmount = "Quel capital est disponible en CAD ?";
const capitalOwnership = "Ce capital est-il détenu seul ou conjointement ?";
const snapshot = {
  id:"p5-component-only",title:"Test de composant sans inférence",revision:1,status:"waiting",
  active_problem:{clarifications:[{id:"problem-copy",field:"capital_cad",question:capitalAmount}]},
  current_view:{id:"view",ref:"view@1",version:1,usable:true,content:{
    documentary_limitations:["Contrôle runtime reserve_budget_contradiction et reçu d'exécution du diagnostic absents."],
    questions:[
      {id:"view-copy",field:"capital_cad",question:"  quel capital est disponible en CAD ?  ",blocking:true,reason:"La somme détermine le domaine."},
      {field:"withdrawal_cad",question:"Quel retrait faut-il financer ?"},
      "Une autre précision ?", "Une autre précision ?",
    ],
  }},
  current_analysis:null,questions:[
    {id:"same-id",target:"human",field:"capital_cad",question:capitalAmount,status:"waiting",reason:"Indiquer une somme en CAD."},
    {id:"same-id",target:"human",field:"capital_cad",question:capitalOwnership,status:"waiting"},
    {id:"closed",target:"human",field:"capital_cad",question:"Ancienne question résolue ?",status:"resolved"},
    {id:"research",target:"research",type:"subproblem",field:"scenarios",question:"Trouver une méthode ?"},
  ],
  artifacts:[],evidence:[],events:[],tasks:[],attempts:[],runs:[],revisions:[],
  route:{mode:"component_test_no_inference"},limitations:[],
};
let browser;
(async()=>{
  browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const errors = [], unexpectedRequests = [];
  page.on("pageerror",error=>errors.push(error.message));
  await page.route("**/api/dossiers**",async route=>{
    const request = route.request(), url = new URL(request.url());
    if(request.method() !== "GET" && !url.pathname.endsWith("/display")) unexpectedRequests.push(url.pathname);
    const payload = url.pathname.endsWith("/examples") ? {examples:[]} : url.pathname === "/api/dossiers" ? {dossiers:[]} : snapshot;
    await route.fulfill({status:200,contentType:"application/json",body:JSON.stringify(payload)});
  });
  await page.goto(`${base}/?dossier=${snapshot.id}`);
  await page.waitForFunction(()=>document.querySelector("#question-count").textContent === "3");
  assert.equal(await page.locator("#questions .question").count(),3);
  const capitalCard = page.locator("#questions .question").filter({hasText:capitalOwnership});
  assert.equal(await capitalCard.count(),1);
  assert.equal(await capitalCard.locator("p").filter({hasText:capitalAmount}).count(),1);
  assert.equal(await capitalCard.locator("p").filter({hasText:capitalOwnership}).count(),1);
  const rendered = await page.locator("#questions").textContent();
  assert.ok(!rendered.includes("Ancienne question résolue"));
  assert.ok(!rendered.includes("Trouver une méthode"));
  assert.ok((await capitalCard.textContent()).includes("Nécessaire pour la conclusion concernée"));
  assert.ok((await capitalCard.textContent()).includes("Indiquer une somme en CAD."));
  assert.ok((await capitalCard.textContent()).includes("La somme détermine le domaine."));
  assert.ok((await page.locator(".answer-panel").textContent()).includes("Observations à la revue Agent 1, avant le calcul"));
  assert.ok((await page.locator(".answer-panel").textContent()).includes("Les contrôles et reçus Agent 2 ci-dessous indiquent ce qui a été établi ensuite."));
  assert.ok((await page.locator(".answer-panel").textContent()).includes(snapshot.current_view.content.documentary_limitations[0]));
  await page.getByRole("button",{name:"Examiner les liens et citations"}).click();
  const inspected = JSON.parse(await page.locator("#inspector-body").innerText());
  assert.deepEqual(inspected.content.documentary_limitations,snapshot.current_view.content.documentary_limitations);
  await page.getByRole("button",{name:"Fermer l’inspecteur"}).click();
  await capitalCard.getByRole("button",{name:"Apporter une précision"}).click();
  const answerPrompt = await page.locator("#revision-message").inputValue();
  assert.ok(answerPrompt.includes(capitalAmount) && answerPrompt.includes(capitalOwnership));
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth));
  assert.deepEqual(errors,[]);
  assert.deepEqual(unexpectedRequests,[]);
  console.log("P5 UI: 3 provenance layers deduplicated; distinct questions in one field retained; blocking/reasons preserved; answer context complete; documentary observations dated without changing trace; mobile no overflow. Component snapshots only, no AWS call.");
})().catch(error=>{console.error(error);process.exitCode=1;}).finally(async()=>{await browser?.close();});
