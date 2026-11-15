const fs=require('fs'),path=require('path');
const {chromium}=require('../../../../runtime/browser-check/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1050},reducedMotion:'reduce'});
 const page=await context.newPage(); const report={testedAt:new Date().toISOString(),base:'http://127.0.0.1:8768',errors:[],requests:[],cases:{}};
 page.on('pageerror',e=>report.errors.push(e.message));
 await page.route('**/*', async route=>{const req=route.request(); if(req.url().startsWith('http://127.0.0.1:8768')){if(req.method()!=='GET'&&!req.url().endsWith('/display'))throw Error('Unexpected mutation '+req.method()+' '+req.url());if(req.method()!=='GET')report.requests.push({url:req.url(),method:req.method()});return route.continue();}return route.abort();});
 const cases={robert:'4089e4b0d70f40b6b20d832fa261e1dc',amira:'f281a9067e4544138fa178fa4ee0b850',incomplete:'e6405c6c61f64c5b89c11262ce9b9669',impossible:'1f7d3a73d5924a09ba73925655dce389'};
 for (const [name,id]of Object.entries(cases)){
  await page.goto(report.base+'/?dossier='+id);await page.waitForSelector('#dossier-view:not([hidden])');await page.waitForTimeout(250);
  let r=report.cases[name]={id};
  r.overview=await page.locator('#tab-overview').innerText();r.context=await page.locator('#context').innerText();r.title=await page.locator('#dossier-title').innerText();r.buttons=await page.getByRole('button').allTextContents();
  await page.screenshot({path:path.join(__dirname,name+'-desktop.png'),fullPage:false});
  await page.locator('[data-tab=history]').click();r.history=await page.locator('#history').innerText();await page.screenshot({path:path.join(__dirname,name+'-history.png'),fullPage:false});
  await page.locator('[data-tab=evidence]').click();r.evidence=await page.locator('#evidence').innerText();
  await page.locator('[data-tab=activity]').click();r.activity=await page.locator('#activity').innerText();
  await page.locator('[data-tab=mandate]').click();r.mandate=await page.locator('#mandate').innerText();
  await page.locator('[data-tab=overview]').click();
  const proofs=page.locator('#tab-overview button');if(await proofs.count()){r.firstproofbutton=await proofs.first().innerText();await proofs.first().click();if(await page.locator('#inspector').isVisible()){r.inspector=await page.locator('#inspector').innerText();await page.screenshot({path:path.join(__dirname,name+'-proof.png'),fullPage:false});await page.getByRole('button',{name:'Fermer l’inspecteur',exact:true}).click();}}
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(__dirname,name+'-mobile.png'),fullPage:false});r.mobileOverflow=await page.evaluate(()=>({viewport:innerWidth,body:document.body.scrollWidth,page:document.documentElement.scrollWidth}));await page.setViewportSize({width:1440,height:1050});
 }
 fs.writeFileSync(path.join(__dirname,'current_ui.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({errors:report.errors,cases:Object.fromEntries(Object.entries(report.cases).map(([k,v])=>[k,{title:v.title,overviewChars:v.overview.length,historyChars:v.history.length,evidenceChars:v.evidence.length,mobileOverflow:v.mobileOverflow}]))},null,2));
 await browser.close();
})();
