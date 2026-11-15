/* Same data, state machine, numerical engine and provenance for all three designs.
   This layer writes neither the principal dossier nor its artifacts. */
export const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
export function money(value) {
  if (value == null || !Number.isFinite(Number(value))) return "non établi";
  const n=Number(value), digits=Math.abs(n-Math.round(n))<1e-8 ? 0 : Math.abs(n)>0&&Math.abs(n)<1 ? Math.min(8,Math.max(2,Math.ceil(-Math.log10(Math.abs(n)))+1)):2;
  return new Intl.NumberFormat("fr-CA",{minimumFractionDigits:digits,maximumFractionDigits:digits}).format(n);
}
export const pct = n => `${new Intl.NumberFormat("fr-CA",{maximumFractionDigits:2}).format(Number(n)*100)} %`;
const labels={baseline:"Portefeuille initial",minimum_turnover:"Solution du calcul",alternative_minimum:"Autre minimum",simple_reference:"Règle simple"};
const assetNames={RESERVE_ABSTRAITE:"Réserve",TSLA:"TSLA","XBB.TO":"XBB","XIU.TO":"XIU","ZST.TO":"ZST"};
export function options(s) {
  const opts=(s.v.analysis?.options||[]).map(o=>({
    id:o.id,label:labels[o.id]||o.label,weights:o.weights||{},
    turnover:o.metrics?.turnover_cad?.value,
    losses:Object.fromEntries((o.scenario_results||[]).map(c=>[c.id,c.loss_cad])),
    admissible:o.admissible,reference:false,raw:o
  }));
  const r=s.v.simple_reference;
  if(r) opts.push({id:"simple_reference",label:labels.simple_reference,weights:r.weights,
    turnover:r.independent.turnover_cad,losses:r.independent.losses_cad,admissible:true,reference:true,raw:r});
  return opts;
}
export function allocation(o) {
  if(!o) return "";
  return `<div class="allocation" role="img" aria-label="Répartition initiale : ${esc(Object.entries(o.weights).map(([a,w])=>`${assetNames[a]||a} ${pct(w)}`).join(", "))}">
    ${Object.entries(o.weights).filter(([,w])=>w>1e-9).map(([a,w],i)=>`<span class="allocation-segment asset-${i}" style="flex:${w};--asset-index:${i}" title="${esc(assetNames[a]||a)} : ${pct(w)}"><span>${esc(assetNames[a]||a)}<b>${pct(w)}</b></span></span>`).join("")}</div>
    <div class="allocation-legend">${Object.entries(o.weights).map(([a,w])=>`<span>${esc(assetNames[a]||a)} <b>${pct(w)}</b></span>`).join("")}</div>`;
}
export function versionSelect(s) {
  return `<label class="version-select">État à examiner
    <select data-version-select aria-label="État archivé à examiner">
    ${s.local?'<option selected value="local">Variante locale — non enregistrée</option>':""}
    ${s.archives.map(v=>`<option value="${v.id}" ${!s.local&&s.v.id===v.id?"selected":""}>${v.id} · retrait ${money(v.problem.withdrawal_cad)} CAD · perte ≤ ${money(v.problem.scenario_loss_limit_cad)} CAD</option>`).join("")}
    </select></label>`;
}
export function limits(s) {
  return `<div class="essential-limits" data-invariant="limits"><strong>La portée de ce résultat</strong>
    <p>Deux chocs hypothétiques à ${money(s.v.problem.withdrawal_months)} mois, sans probabilité. Réserve abstraite à rendement nul : aucun placement réel garanti. Frais, impôts et inflation exclus.</p>
    <p>Horizon déclaré : ${money(s.v.problem.horizon_years)} ans ; les quatre années ne sont pas simulées. Les plafonds portent sur les poids initiaux.</p>
    ${s.v.simple_reference?'<p><strong>La règle simple atteint aussi ce minimum.</strong> Aucune supériorité des agents n’est démontrée.</p>':s.local?'<p>La règle simple de r5 n’est pas extrapolée à cette variante ; elle reste consultable dans l’archive initiale.</p>':'<p>La règle simple n’a été contrôlée indépendamment que pour r5 ; aucune comparaison équivalente n’est établie pour cet état.</p>'}
    </div>`;
}
export function delta(s) {
  if(!s.previous) return `<p class="no-delta">Vous examinez l’état initial vérifié. Modifiez une hypothèse pour voir ce qui change.</p>`;
  const before=s.previous, after=s.v;
  const rows=[
    ["Retrait à 12 mois",before.problem.withdrawal_cad,after.problem.withdrawal_cad],
    ["Budget de perte par choc",before.problem.scenario_loss_limit_cad,after.problem.scenario_loss_limit_cad],
    ["Minimum à réallouer",before.stats?.min_reallocation_cad,after.stats?.min_reallocation_cad]
  ];
  return `<section class="revision-delta" aria-label="Différences avec l’état précédent">
    <p class="delta-caption">Même portefeuille de départ · comparaison d’états, pas opérations successives.</p>
    <table><caption>Ce qui change, en CAD</caption><thead><tr><th>Grandeur</th><th>Avant</th><th>Après</th><th>Écart</th></tr></thead><tbody>${rows.map(([label,b,a])=>`<tr><th>${label}</th><td>${money(b)}</td><td>${money(a)}</td><td>${a==null||b==null?"—":`${a-b>0?"+":""}${money(a-b)}`}</td></tr>`).join("")}</tbody></table>
    <div class="dependency-pair"><div><strong>Entrées conservées</strong><p>Capital ${money(after.problem.capital_cad)} CAD, positions initiales, chocs, plafond TSLA ${pct(after.problem.max_asset_weights.TSLA)}.</p></div>
    <div><strong>${s.v.analysis.status==="infeasible"?"Faisabilité réexaminée":s.local?"Calculs réexécutés":"Résultats dépendants renouvelés"}</strong><p>${s.v.analysis.status==="infeasible"?"Aucune allocation ni minimum établis ; le contrôle d’infaisabilité arrête la résolution.":"Allocation, contraintes, minimum et conclusion."} ${s.local?"Aucun cache d’artefacts réutilisé ; aucun agent relancé.":"Les archives conservent research@1 et baseline_stress@1."}</p></div></div>
    <button type="button" data-action="undo" class="undo-button">← Revenir à l’état précédent</button></section>`;
}
export function revisionForm(s) {
  return `<div class="revision-form-wrap"><p class="revision-intro">Explorez une copie du dossier. Ces paramètres financiers modifient les calculs ; votre niveau de lecture ne les modifie pas.</p>
    <form data-scenario>
    <label>Retrait à 12 mois <span>CAD · valeur du dossier, puis brouillon si modifiée</span><input name="withdrawal_cad" type="number" min="0" max="1000000000000" step="any" required value="${esc(s.draft?.withdrawal_cad??s.v.problem.withdrawal_cad)}" ${s.busy?"disabled":""}></label>
    <label>Perte maximale sous chaque choc <span>CAD · contrainte déclarée, puis brouillon si modifiée</span><input name="scenario_loss_limit_cad" type="number" min="0" max="1000000000000" step="any" required value="${esc(s.draft?.scenario_loss_limit_cad??s.v.problem.scenario_loss_limit_cad)}" ${s.busy?"disabled":""}></label>
    <div class="form-actions"><button type="submit" ${s.busy?"disabled":""}>${s.busy?"Calcul local en cours…":"Calculer cette variante"}</button><button type="button" data-action="draft" data-withdrawal="40000" ${s.busy?"disabled":""}>Préparer un retrait de 40 000 CAD</button><button type="button" data-action="view" data-view="overview">Annuler la saisie</button></div>
    <p class="draft-status" role="status">${s.draft?"Brouillon conservé. Le résultat reste celui de l’état précédent jusqu’au calcul.":"Les valeurs ci-dessus proviennent de l’état affiché. Aucun calcul avant validation."}</p>
    </form><p class="calculation-notice">Moteur financier existant, exécuté sur une copie. Aucun appel AWS, aucune recherche nouvelle, aucune écriture dans le dossier principal.</p>
    ${s.error?`<div class="calculation-error" role="alert"><strong>Le calcul n’a pas abouti.</strong><p>${esc(s.error)}</p><p>Le résultat précédent reste intact. Réessayez après correction des paramètres ou retour du service.</p></div>`:""}
    </div>`;
}
export function methodDetails(s) {
  const m=s.v.analysis?.method||{}, p=s.v.problem;
  if(s.v.analysis?.status==="infeasible") {
    const certificate=(s.v.analysis.checks||[]).find(c=>c.id==="reserve_budget_contradiction");
    return `<section class="method-details"><h2>Comprendre le conflit</h2><p>Aucune allocation ni minimum établis. ${certificate?"Un certificat algébrique suffit ici ; le programme linéaire n’a pas été exécuté.":"Le modèle ne trouve pas de solution admissible sous les contraintes déclarées."}</p>
      ${certificate?`<p>Le retrait doit être financé par la réserve, elle-même limitée au capital : <strong>retrait ≤ réserve ≤ capital</strong>.</p><p>${money(certificate.withdrawal_cad)} − ${money(certificate.capital_cad)} = <strong>${money(certificate.shortfall_cad)} CAD</strong> de déficit.</p><p>Sans apport extérieur, ces contraintes sont incompatibles. Ce certificat porte sur ce sous-ensemble nécessaire ; il ne constitue pas un IIS global.</p>`:""}
      <ul>${(m.assumptions||[]).map(a=>`<li>${esc(a)}</li>`).join("")}</ul><button data-action="proof" data-proof="method">Inspecter le contrôle de faisabilité</button></section>`;
  }
  return `<section class="method-details"><h2>Le problème, rendu calculable</h2>
    <p>Minimiser le capital déplacé depuis les positions initiales, sous les contraintes déclarées. Cela ne minimise ni la perte ni le risque global.</p>
    <dl><div><dt>Objectif</dt><dd>Capital × ½ Σ |poids − poids initiaux|</dd></div><div><dt>Contraintes</dt><dd>Somme des poids = 100 %, poids ≥ 0 ; réserve ≥ ${money(p.withdrawal_cad)} CAD ; TSLA ≤ ${pct(p.max_asset_weights.TSLA)} ; perte ≤ ${money(p.scenario_loss_limit_cad)} CAD dans chacun des deux chocs.</dd></div><div><dt>Nature du résultat</dt><dd>Optimum conditionnel d’un programme linéaire ; aucune prévision de rendement.</dd></div></dl>
    <div class="table-scroll"><table><caption>Chocs déclarés en CAD, à ${money(p.withdrawal_months)} mois — sans probabilités</caption><thead><tr><th>Actif</th>${p.scenarios.map(c=>`<th>${esc(c.id)}</th>`).join("")}</tr></thead><tbody>${Object.keys(p.scenarios[0].returns).map(a=>`<tr><th>${esc(assetNames[a]||a)}</th>${p.scenarios.map(c=>`<td>${pct(c.returns[a])}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
    <p>Connaissance du dossier : ${esc(p.knowledge_date)}. Positions fractionnaires ; coûts exclus. L’instrument réel de réserve reste à qualifier.</p>
    <div class="method-actions"><button data-action="proof" data-proof="method">Inspecter le calcul et ses contrôles</button><button data-action="proof" data-proof="sources">Lire les passages documentaires</button><button data-action="proof" data-proof="agents">Voir les contributions archivées</button></div>
    </section>`;
}
function resolvePointer(obj,pointer) {
  return pointer.split("/").slice(1).reduce((o,k)=>o?.[k.replace(/~1/g,"/").replace(/~0/g,"~")],obj);
}
function readable(value) {return typeof value==="number"?money(value):typeof value==="string"?value:JSON.stringify(value,null,2);}
function excerpt(p) {
  const passages=p.passages?.length?p.passages:[{text:p.passage||"Aucun passage extrait."}];
  // Two brief verbatim excerpts; complete provenance remains in the source export.
  const useful=passages.find(x=>/Introduction|About HiGHS|4\.3 Linear/.test(x.text))||passages[0];
  const chosen=[useful,...passages.filter(x=>x!==useful)].slice(0,2);
  return chosen.map(x=>`<blockquote>${esc(x.text.split(/\s+/).slice(0,75).join(" "))}${x.text.split(/\s+/).length>75?" […]":""}<footer>Lignes ${esc(x.line_start??"non indiquées")}–${esc(x.line_end??"non indiquées")} de la capture</footer></blockquote>`).join("");
}
function proofContent(s,id) {
  const v=s.v;
  if(id==="sources") {
    const docs=(v.proofs||[]).filter(p=>p.kind==="document");
    return `<h2 id="proof-title">Les sources, dans leur portée</h2><p>Passages archivés et sélection documentaire. Leur présence ne certifie pas indépendamment chaque conclusion.</p>${s.local?'<p class="proof-warning">Ces sources proviennent de la base archivée ; aucune nouvelle lecture documentaire ni revue d’applicabilité n’a eu lieu pour cette variante locale.</p>':""}${docs.length?docs.map(p=>`<article class="source-excerpt"><h3>${esc(p.title)}</h3><p>${esc(p.reading_level)} · ${p.selected_by_agent1?"sélectionnée par l’agent 1":"consultée, non retenue"}</p><p>${esc(p.scope||"")}<br>Connue au ${esc(p.known_at||"non indiqué")} · version ${esc(typeof p.version==="object"?JSON.stringify(p.version):p.version||"capture datée")}</p>${excerpt(p)}${p.url?`<a href="${esc(p.url)}" target="_blank" rel="noopener">Ouvrir la source originale ↗</a>`:""}<details><summary>Provenance et passages complets</summary><pre>${esc(JSON.stringify(p,null,2))}</pre></details></article>`).join(""):"<p>Aucun passage exploitable dans cet état.</p>"}`;
  }
  if(id==="agents") {
    return `<h2 id="proof-title">Quatre contributions inspectables</h2><p>${s.local?"Ces contributions sont celles de la base archivée. La variante locale ne relance aucun agent.":"Exécution archivée, pas activité en direct."}</p>${(v.agents||[]).map((a,i)=>`<article class="agent-proof"><p>Agent ${i} · ${esc(a.status)}</p><h3>${esc(a.name)}</h3><p>${esc(a.mission)}</p><details><summary>Transformation et trace</summary><pre>${esc(JSON.stringify(a,null,2))}</pre></details></article>`).join("")}`;
  }
  const selectedProof=(v.proofs||[]).find(p=>p.id===id);
  const claim=(v.claims||[]).find(p=>p.id===id)||v.claims?.[0];
  const analysis=v.analysis||{};
  const bindings=s.local?(claim?.result_refs||[]).map(b=>({...b,value:resolvePointer(analysis,b.pointer)})):selectedProof?.bindings||v.proofs?.find(p=>p.kind==="calculation")?.bindings||[];
  const selected=options(s).find(o=>o.id===s.selected);
  return `<h2 id="proof-title">${id==="method"?"Du problème au résultat":"Pourquoi ce chiffre ?"}</h2>
    <p class="proof-lead">${esc(claim?.text||"Aucune conclusion numérique disponible pour cet état.")}</p>
    ${bindings.map(b=>`<div class="number-binding"><strong>${esc(readable(b.value))} ${esc(b.unit)}</strong><code>${esc(b.pointer)}</code></div>`).join("")}
    <h3>Ce que le calcul établit</h3><p>${analysis.status==="infeasible"?"L’impossibilité sous les contraintes contrôlées. Aucune allocation ni minimum n’est établi.":"Minimiser le déplacement de capital sous les contraintes de ce dossier. Le budget de perte s’applique uniquement aux deux chocs déclarés."}</p>
    <p>${analysis.optimal_face?.non_unique_witness_found?"Un autre optimum a été trouvé. Le premier n’est pas un optimum de risque.":analysis.status==="infeasible"?"Le certificat ou le diagnostic ci-dessous précise le domaine de cette impossibilité.":"Aucun témoin de multiplicité n’est présenté dans cet état."}</p>
    ${v.simple_reference?`<h3>Le contrepoint indépendant</h3><p>${esc(v.simple_reference.conclusion)}</p><p>${esc(v.simple_reference.construction)}</p><code>${esc(v.simple_reference.source)}${esc(v.simple_reference.pointer)}</code><p class="digest">SHA-256 ${esc(v.simple_reference.source_sha256)}</p>`:""}
    <h3>Hypothèses et contrôles</h3><ul>${(analysis.method?.assumptions||[]).map(a=>`<li>${esc(a)}</li>`).join("")}</ul>
    ${id==="method"&&selected?`<h3>Les pertes de l’option examinée</h3><p>${esc(selected.label)}. Formule : perte = −capital × somme (poids × choc). Les poids et chocs sont des fractions, les sorties en CAD.</p><div class="table-scroll"><table><caption>Entrées des pertes, pour ${money(v.problem.capital_cad)} CAD</caption><thead><tr><th>Actif</th><th>Poids</th>${v.problem.scenarios.map(x=>`<th>${esc(x.id)}</th>`).join("")}</tr></thead><tbody>${Object.entries(selected.weights).map(([a,w])=>`<tr><th>${esc(assetNames[a]||a)}</th><td>${pct(w)}</td>${v.problem.scenarios.map(x=>`<td>${pct(x.returns[a])}</td>`).join("")}</tr>`).join("")}<tr><th>Perte, CAD</th><td>—</td>${v.problem.scenarios.map(x=>`<td>${money(selected.losses[x.id])}</td>`).join("")}</tr></tbody></table></div><p>${selected.reference?"La règle simple est un calcul indépendant de la revue de défense.":"Ces résultats proviennent de l’option "+esc(selected.id)+" dans analysis.options."}</p>`:""}
    <details open><summary>Contrôles numériques exécutés</summary><pre>${esc(JSON.stringify(analysis.checks||selectedProof?.checks||[],null,2))}</pre></details>
    <details><summary>Méthode, équations et entrées</summary><pre>${esc(JSON.stringify(analysis.method||{},null,2))}</pre></details>
    <p class="digest">${s.local?"Résultat local SHA-256 "+esc(s.local.result_sha256):esc(v.source?.analysis_ref)+" · SHA-256 "+esc(v.source?.analysis_sha256)}</p>
    <p>${s.local?"Calcul local sur copie, aucun nouvel appel d’agent.":"Archive issue du dossier versionné."}</p>`;
}
export function mount(render,{name="AlphaForge"}={}) {
  let state, dialog, requestId=0;
  const app=document.getElementById("app");
  function draw() {
    const focus=document.activeElement, key=focus?.dataset?.action, value=focus?.dataset?.level||focus?.dataset?.view;
    app.innerHTML=render(state);
    app.querySelectorAll('[data-action="undo"]').forEach(b=>b.disabled=!state.history.length);
    document.documentElement.dataset.level=state.level;
    document.documentElement.dataset.local=String(!!state.local);
    document.title=`${name} · Robert · AlphaForge`;
    if(key&&value) app.querySelector(`[data-action="${key}"][data-level="${value}"],[data-action="${key}"][data-view="${value}"]`)?.focus({preventScroll:true});
    document.dispatchEvent(new CustomEvent("alphaforge:render",{detail:{level:state.level,version:state.v.id,local:!!state.local}}));
  }
  function snapshot() {return {v:state.v,local:state.local,previous:state.previous,selected:state.selected};}
  function openProof(id,trigger) {
    dialog.innerHTML=`<div class="proof-toolbar"><span>ALPHAFORGE / PREUVE</span><button class="proof-close" aria-label="Fermer la preuve">Fermer ×</button></div><div class="proof-content">${proofContent(state,id)}<div class="proof-downloads">${state.local?'<button data-download-local>Télécharger le résultat local JSON</button>':`<a href="${esc(state.v.source?.download_url)}" download>Télécharger le dossier source JSON</a>`}</div></div>`;
    dialog.querySelectorAll("pre").forEach(pre=>{pre.tabIndex=0;pre.setAttribute("role","region");pre.setAttribute("aria-label",pre.closest("details")?.querySelector("summary")?.textContent||"Données de la preuve");});
    dialog.querySelector(".proof-close").onclick=()=>dialog.close();
    dialog.querySelector("[data-download-local]")?.addEventListener("click",()=>{const b=new Blob([JSON.stringify({problem:state.v.problem,analysis:state.v.analysis,receipt:state.local},null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="robert-variante-locale.json";a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);});
    dialog.showModal();dialog.querySelector(".proof-close").focus();
    dialog.onclose=()=>trigger?.isConnected&&trigger.focus();
  }
  app.addEventListener("click",e=>{
    const b=e.target.closest("[data-action]");if(!b||!state) return;
    const action=b.dataset.action;
    if(action==="proof") {openProof(b.dataset.proof||"minimum_reallocation",b);return;}
    if(action==="draft") {const f=app.querySelector("[data-scenario]");if(f){f.elements.withdrawal_cad.value=b.dataset.withdrawal;state.draft={withdrawal_cad:f.elements.withdrawal_cad.value,scenario_loss_limit_cad:f.elements.scenario_loss_limit_cad.value};f.querySelector(".draft-status").textContent="Brouillon modifié ; le résultat reste celui de l’état précédent jusqu’au calcul.";f.elements.withdrawal_cad.focus();}return;}
    if(action==="level") state.level=b.dataset.level;
    if(action==="select") state.selected=b.dataset.option;
    if(action==="view") {state.view=b.dataset.view;state.error=null;state.draft=null;requestId++;state.busy=false;}
    if(action==="undo"&&state.history.length) {Object.assign(state,state.history.pop());state.view="compare";state.error=null;state.draft=null;requestId++;state.busy=false;state.notice="État précédent restauré. Le dossier principal n’a pas été modifié.";}
    if(action==="reset") {state.history.push(snapshot());state.previous=state.v;state.v=state.archives[0];state.local=false;state.view="overview";state.error=null;state.draft=null;state.busy=false;state.selected="minimum_turnover";state.notice="Archive initiale r5 restaurée. Aucun calcul ni agent relancé.";requestId++;}
    draw();
    if(["view","reset"].includes(action)) {window.scrollTo({top:0,behavior:"instant"});app.querySelector("h1")?.setAttribute("tabindex","-1");app.querySelector("h1")?.focus({preventScroll:true});}
  });
  app.addEventListener("change",e=>{
    if(e.target.matches("[data-version-select]")) {
      const next=state.archives.find(v=>v.id===e.target.value);if(!next)return;
      state.history.push(snapshot());state.previous=state.v;state.v=next;state.local=false;state.busy=false;state.error=null;state.draft=null;state.view="compare";state.selected="minimum_turnover";requestId++;
      state.notice=`Archive ${next.id} ouverte : résultat précalculé. Aucun calcul ni agent relancé.`;draw();
    }
  });
  app.addEventListener("input",e=>{const form=e.target.closest("[data-scenario]");if(form){state.draft={withdrawal_cad:form.elements.withdrawal_cad.value,scenario_loss_limit_cad:form.elements.scenario_loss_limit_cad.value};const status=form.querySelector(".draft-status");if(status)status.textContent="Saisie en cours. Le résultat affiché reste celui de l’état précédent.";}});
  app.addEventListener("submit",async e=>{
    if(!e.target.matches("[data-scenario]"))return;e.preventDefault();
    const f=e.target,changes={withdrawal_cad:Number(f.elements.withdrawal_cad.value),scenario_loss_limit_cad:Number(f.elements.scenario_loss_limit_cad.value)};
    const current=snapshot(), token=++requestId;
    // A local revision always includes both exposed fields and retains the exact archived base.
    const base=state.local?.base_version_id||state.v.id;
    state.busy=true;state.error=null;state.draft=changes;draw();
    try{
      const response=await fetch("/api/prototype/explore",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({case_id:"robert",version_id:base,changes})});
      const data=await response.json();
      if(token!==requestId)return;
      if(!response.ok)throw new Error(typeof data.detail==="string"?data.detail:data.detail?.message||"Service indisponible.");
      const baseVersion=state.archives.find(v=>v.id===data.base_version_id);
      state.history.push(current);state.previous=current.v;
      state.v={...baseVersion,id:`local-${state.history.length}`,problem:data.problem,analysis:data.analysis,stats:data.stats,claims:data.claims,limits:data.limits,simple_reference:data.simple_reference||null,changes:data.changes,localDependency:data.dependency_preview};
      state.local={...data.receipt,base_version_id:data.base_version_id,base_case_id:data.base_case_id};
      state.view="compare";state.selected="minimum_turnover";state.notice="Variante calculée sur une copie. Aucun agent relancé, dossier principal inchangé.";state.busy=false;state.draft=null;draw();
      window.scrollTo({top:0,behavior:"instant"});app.querySelector("h1")?.setAttribute("tabindex","-1");app.querySelector("h1")?.focus({preventScroll:true});
    }catch(err){if(token===requestId){state.busy=false;state.error=err.message;draw();}}
  });
  app.innerHTML='<div class="loading-state" role="status"><p>Ouverture du dossier Robert…</p><p>Lecture de l’archive vérifiée, aucun agent relancé.</p></div>';
  fetch("/api/prototype/cases/robert").then(r=>{if(!r.ok)throw Error("Archive indisponible.");return r.json();}).then(c=>{
    state={v:c.versions[0],archives:c.versions,level:"accessible",view:"overview",selected:"minimum_turnover",local:false,previous:null,history:[],busy:false,error:null,notice:null,draft:null};
    dialog=document.createElement("dialog");dialog.className="evidence-dialog";dialog.setAttribute("aria-labelledby","proof-title");document.body.append(dialog);dialog.addEventListener("click",e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
    window.__alphaForgeReadOnly=()=>JSON.parse(JSON.stringify({version:state.v.id,level:state.level,view:state.view,problem:state.v.problem,stats:state.v.stats,options:options(state),local:state.local,history:state.history.length}));
    draw();
  }).catch(err=>{app.innerHTML=`<div class="loading-state" role="alert"><h1>Le dossier n’est pas accessible.</h1><p>${esc(err.message)} Votre application et ses sessions sont conservées.</p><button onclick="location.reload()">Réessayer</button><a href="../">Retour à la galerie</a></div>`;});
}
