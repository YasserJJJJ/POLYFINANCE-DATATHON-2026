import {mount, esc, money, pct, options, allocation, revisionForm, versionSelect, delta, methodDetails, limits} from '../shared/experience.js';

const label = o => ({minimum_turnover:'Le minimum calculé', alternative_minimum:'Une autre répartition',simple_reference:'La référence simple',baseline:'Le portefeuille initial'}[o.id] || o.label);
const proof = (id,text,cls='text-link') => `<button class="${cls}" data-action="proof" data-proof="${id}">${text}<span aria-hidden="true"> ↗</span></button>`;
const viewButton = (s,view,num,text) => `<button data-action="view" data-view="${view}" class="chapter ${s.view===view?'active':''}" aria-current="${s.view===view?'page':'false'}"><span>${num}</span>${text}<span aria-hidden="true">↗</span></button>`;

function contours(){
  return `<svg viewBox="0 0 430 380" class="contours" aria-hidden="true"><defs><pattern id="folio-dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="currentColor"/></pattern></defs><path fill="url(#folio-dots)" d="M62 347C-18 230 56 6 217 30s242 147 174 257S142 464 62 347Z"/>${Array.from({length:15},(_,i)=>`<ellipse cx="241" cy="195" rx="${32+i*9}" ry="${47+i*10}" transform="rotate(-33 241 195)" fill="none" stroke="currentColor" stroke-width=".8"/>`).join('')}</svg>`;
}

function facts(s){
  const p=s.v.problem;
  return `<dl class="mandate"><div><dt>Capital déclaré</dt><dd>${money(p.capital_cad)} <small>CAD</small></dd></div><div><dt>Retrait à ${esc(p.withdrawal_months)} mois</dt><dd>${money(p.withdrawal_cad)} <small>CAD</small></dd></div><div><dt>Perte admise par choc</dt><dd>${money(p.scenario_loss_limit_cad)} <small>CAD</small></dd></div><div><dt>Plafond TSLA, au départ</dt><dd>${pct(p.max_asset_weights?.TSLA ?? 0.1)}</dd></div></dl>`;
}

function notice(s){
  return `${s.busy?'<div class="notice busy" role="status"><span class="ink-dot"></span>Calcul en cours sur votre copie locale. L’archive reste intacte.</div>':''}${s.error?`<div class="notice error" role="alert"><strong>Le calcul n’a pas abouti.</strong> ${esc(typeof s.error==='string'?s.error:s.error.message||'Vérifiez les paramètres puis réessayez.')}</div>`:''}${s.notice?`<div class="notice" role="status">${esc(s.notice)}</div>`:''}`;
}

function selectedPlate(s,small=false){
  const all=options(s);const chosen=all.find(o=>o.id===s.selected)||all.find(o=>o.id==='minimum_turnover')||all[0];
  if(!chosen)return `<p class="empty-result">Aucune répartition admissible à présenter. Le dossier et les contraintes restent consultables.</p>`;
  return `<section class="allocation-plate ${small?'compact':''}" aria-label="Répartition sélectionnée">
  <div class="plate-caption"><span class="folio-number">Fig. 01</span><h3>${esc(label(chosen))}</h3><span class="${chosen.admissible?'admissible':'inadmissible'}">${chosen.admissible?'Contraintes satisfaites':'Contraintes non satisfaites'}</span></div>
  ${allocation(chosen)}
  <p class="plate-footnote">Parts du capital initial de ${money(s.v.problem.capital_cad)} CAD. La réserve est abstraite ; aucun instrument réel n’est qualifié.</p>
  <div class="plate-values"><div><span>Capital déplacé</span><strong>${money(chosen.turnover)} <small>CAD</small></strong></div><div><span>Perte · choc actions</span><strong>${money(chosen.losses.actions)} <small>CAD</small></strong></div><div><span>Perte · choc obligations</span><strong>${money(chosen.losses.obligations)} <small>CAD</small></strong></div></div>
  </section>`;
}

function overview(s){
  const v=s.v, min=v.stats?.min_reallocation_cad;const all=options(s);
  const simple=all.find(o=>o.reference||o.id==='simple_reference');
  const equal=simple&&min!=null&&Math.abs(simple.turnover-min)<.01&&simple.admissible;
  return `<section class="lead-spread">
    <div class="lede">
      <p class="kicker"><span class="red-dot"></span> Dossier Robert / conclusion conditionnelle</p>
      <h1>${min==null?'Les contraintes<br>ne se rencontrent pas.':Math.abs(min-v.problem.capital_cad)<.01?'Le mandat exige<br><em>de tout déplacer.</em>':s.level==='deep'?`Un minimum calculé.<br><em>${v.analysis?.optimal_face?.non_unique_witness_found?'Plusieurs répartitions.':'Sous conditions.'}</em>`:'Préparer le retrait,<br><em>sans tout déplacer.</em>'}</h1>
      <p class="standfirst">Sur ${money(v.problem.capital_cad)} CAD, financer un retrait de <strong>${money(v.problem.withdrawal_cad)} CAD à ${esc(v.problem.withdrawal_months)} mois</strong>, en déplaçant le moins de capital possible.</p>
      <button class="primary" data-action="view" data-view="compare">Comparer les répartitions <span aria-hidden="true">↗</span></button>
    </div>
    <div class="hero-result">${contours()}<p class="result-label">${min==null?'Aucune allocation établie':'Minimum de capital à réallouer'}</p><button class="result-number" data-action="proof" data-proof="minimum_reallocation" aria-label="Examiner le calcul et ses contrôles">${min==null?'—':money(min)}<small>${min==null?'Non résolu':'CAD'} <span aria-hidden="true">↗</span></small></button><p>${min==null?'Aucun résultat numérique admissible n’est présenté.':'Résultat du calcul sous les contraintes du dossier.'}<br><strong>Ni promesse de rendement, ni garantie du capital.</strong></p></div>
  </section>
  <div class="editorial-grid">
    <aside class="margin-note" aria-label="Notes de lecture"><span class="note-index">01 / Lecture</span><p>Un chiffre devient utile quand on connaît ses conditions.</p>${proof('minimum_reallocation','Remonter au calcul')}${proof('sources','Lire les sources')}</aside>
    <section class="interpretation"><p class="kicker">${min==null?'Ce que l’échec permet de dire':'Ce que le résultat permet de dire'}</p><h2>${min==null?'Revoir les contraintes.':equal?'La simplicité fait aussi bien.<sup>1</sup>':'Le minimum ne dit pas tout.'}</h2>${min==null?'<p>Le moteur ne fournit aucune allocation admissible pour ces paramètres. Il faut examiner les contraintes et les diagnostics avant de proposer une nouvelle hypothèse.</p><p>Les résultats de l’archive précédente restent consultables, mais ne répondent pas à cette demande modifiée.</p>':`<p>${equal?`La référence simple atteint elle aussi le minimum de <strong>${money(min)} CAD</strong>. Le solveur ne démontre donc aucun avantage sur cet objectif face à cette référence.`:'Cette valeur minimise le capital déplacé sous les contraintes précisées. Elle ne sélectionne pas automatiquement le risque le plus faible.'}</p><p>Les pertes dépendent de la répartition. Le premier optimum ne minimise ni le risque, ni les frais réels.</p>`}${s.previous?delta(s):''}</section>
    <aside class="annotation" aria-label="Contrepoint du résultat"><span class="annotation-mark">${min==null?'!':'1'}</span><p>${min==null?'Une impossibilité reste une information.':equal?'Même minimum. Répartitions différentes.':'Résultat conditionnel.'}</p><button data-action="view" data-view="${min==null?'revise':'compare'}">${min==null?'Revoir les paramètres':'Voir la planche comparative'} <span aria-hidden="true">→</span></button></aside>
  </div>
  <div class="editorial-grid lower-spread"><aside class="margin-note" aria-label="Notes sur le mandat"><span class="note-index">02 / Le mandat</span><p>Les informations qui orientent ce calcul.</p><button class="text-link" data-action="view" data-view="revise">Faire une correction ↗</button></aside><section class="wide-column">${facts(s)}${selectedPlate(s,true)}</section></div>`;
}

function deepOverview(s){
  const min=s.v.stats?.min_reallocation_cad;
  return `<header class="deep-title"><div><p class="kicker">Dossier Robert / lecture approfondie</p><h1>Rendre le problème<br><em>vérifiable.</em></h1></div><div class="deep-result"><span>Minimum conditionnel à réallouer</span><button data-action="proof" data-proof="minimum_reallocation">${money(min)} <small>CAD ↗</small></button><p>${s.v.simple_reference?'La référence simple atteint aussi ce minimum.':'Aucune comparaison indépendante équivalente n’est établie pour cet état.'}</p></div></header>
  <div class="deep-mandate">${facts(s)}</div>
  <section class="deep-apparatus"><aside class="margin-note" aria-label="Notes sur la méthode"><span class="note-index">01 / Établir</span><p>Objectif, contraintes, puis conséquences. Le minimum est une propriété de ce problème précis.</p>${proof('sources','Lire les passages sources')}${proof('agents','Examiner les traces')}</aside><div>${methodDetails(s)}</div><aside class="deep-side-note" aria-label="Portée mathématique"><span class="annotation-mark">!</span><h3>Une garantie conditionnelle.</h3><p>La résolution du programme linéaire ne prouve ni rendement futur, ni risque minimal.</p><p>Les chocs ne décrivent pas une distribution de probabilités. L’instrument réel de réserve reste inconnu.</p></aside></section>
  <section class="deep-plate"><div><p class="kicker">02 / Examiner les conséquences</p><h2>${s.v.analysis?.optimal_face?.non_unique_witness_found?'Un autre optimum est attesté.':'Ce que produit cette résolution.'}</h2><p>Le capital déplacé et les pertes de scénario répondent à des questions différentes.</p><button class="primary" data-action="view" data-view="compare">Comparer les répartitions ↗</button></div><div>${selectedPlate(s,true)}</div></section>${s.previous?delta(s):''}`;
}

function compare(s){
  const rows=options(s), min=s.v.stats?.min_reallocation_cad;
  const equal=rows.find(o=>o.reference&&o.admissible&&Math.abs(o.turnover-min)<.01);
  return `<header class="section-title"><p class="kicker">Planche comparative / valeurs en CAD</p><h1>${min==null?'Pas de solution établie.<br><em>Des contraintes à revoir.</em>':'Un minimum.<br><em>Des conséquences différentes.</em>'}</h1><p class="standfirst">Même capital initial, mêmes chocs hypothétiques, même échéance de retrait. ${equal?'La référence simple atteint aussi le minimum.':'Les résultats restent conditionnels aux hypothèses du dossier.'}</p></header>
  ${s.previous?`<div class="comparison-delta"><p class="kicker">La correction, rendue visible</p>${delta(s)}</div>`:''}
  <div class="editorial-grid"><aside class="margin-note" aria-label="Notes de comparaison"><span class="note-index">01 / Comparer</span><p>Le meilleur résultat dépend de la question posée. Ici : déplacer le moins de capital.</p>${proof('method','Vérifier la méthode')}</aside><section class="wide-column">
  <div class="table-scroll" tabindex="0" role="region" aria-label="Comparaison des répartitions, défilement horizontal si nécessaire"><table class="comparison-table"><caption>Chocs à ${esc(s.v.problem.withdrawal_months)} mois, sans probabilités. Sélectionnez une ligne pour examiner sa composition.</caption><thead><tr><th scope="col">Répartition</th><th scope="col">Capital déplacé</th><th scope="col">Perte<br>choc actions</th><th scope="col">Perte<br>choc obligations</th><th scope="col">Contraintes</th></tr></thead><tbody>${rows.map((o,i)=>`<tr class="${s.selected===o.id?'selected':''}"><th scope="row"><button data-action="select" data-option="${esc(o.id)}" aria-pressed="${s.selected===o.id}"><span class="row-num">0${i+1}</span>${esc(label(o))}${o.reference?'<small>Référence indépendante</small>':''}</button></th><td>${money(o.turnover)}</td><td>${money(o.losses.actions)}</td><td>${money(o.losses.obligations)}</td><td><span class="${o.admissible?'admissible':'inadmissible'}">${o.admissible?'Satisfaites':'Non satisfaites'}</span></td></tr>`).join('')}</tbody></table></div>
  ${selectedPlate(s)}
  <p class="comparison-warning"><span>À retenir</span> Une perte plus faible dans ces deux chocs n’est pas une garantie de risque inférieur dans tous les futurs possibles.</p>
  </section></div>`;
}

function revise(s){
  return `<header class="section-title erratum-title"><p class="kicker">Erratum / exploration réversible</p><h1>Et si le besoin<br><em>avait changé ?</em></h1><p class="standfirst">Corrigez une hypothèse sur une copie locale. Le moteur refait les calculs nécessaires ; l’archive du dossier reste intacte.</p></header>
  <div class="editorial-grid"><aside class="margin-note" aria-label="Notes de correction"><span class="note-index">01 / Corriger</span><p>Une nouvelle information peut changer la décision. Elle ne réécrit pas le passé.</p>${proof('agents','Voir le travail conservé')}</aside><section class="revision-sheet"><div class="erratum-label">Correction proposée</div><p class="revision-intro">Le retrait actuellement retenu est de <strong>${money(s.v.problem.withdrawal_cad)} CAD</strong> à ${esc(s.v.problem.withdrawal_months)} mois.</p>${revisionForm(s)}<p class="form-footnote">L’exemple remplit le formulaire. Le calcul commence seulement à sa soumission. Aucun appel d’agent n’est simulé.</p></section><aside class="revision-note" aria-label="Dépendances de la correction"><span class="editor-mark">↳</span><h3>Ce qui sera réexaminé</h3><p>Réserve, admissibilité, minimum à déplacer et pertes des répartitions.</p><h3>Ce qui reste une base</h3><p>Positions initiales, sources et chocs, tant que leurs entrées ne changent pas.</p></aside></div>
  ${s.previous?`<section class="revision-result"><p class="kicker">Après correction / différence calculée</p>${delta(s)}${selectedPlate(s,true)}<button class="primary" data-action="undo">Annuler cette exploration <span aria-hidden="true">↶</span></button></section>`:''}`;
}

function render(s){
  return `<div class="paper">
  <header class="masthead"><a href="../" class="back-gallery">← Les directions</a><a class="wordmark" href="./" aria-label="Folio AlphaForge, réouvrir le dossier">folio<span>AlphaForge</span></a><div class="edition"><span>Le dossier de décision</span><strong>Édition ${esc(s.local?'locale':s.v.id)}</strong></div></header>
  <div class="reading-bar" role="region" aria-label="Parcours et niveau de lecture"><nav aria-label="Parcours du dossier">${viewButton(s,'overview','I','Comprendre')}${viewButton(s,'compare','II','Comparer')}${viewButton(s,'revise','III','Réviser')}</nav><div class="reading-level" aria-label="Niveau de présentation"><span>Lecture</span><button data-action="level" data-level="accessible" aria-pressed="${s.level==='accessible'}">Essentielle</button><button data-action="level" data-level="deep" aria-pressed="${s.level==='deep'}">Approfondie</button></div></div>
  ${notice(s)}
  <main>${s.view==='compare'?compare(s):s.view==='revise'?revise(s):s.level==='deep'?deepOverview(s):overview(s)}
  ${s.level==='deep'&&s.view!=='overview'?`<section class="method-spread"><div class="method-heading"><p class="kicker">L’appareil critique</p><h2>Les conditions<br>du calcul.</h2></div><div>${methodDetails(s)}</div></section>`:''}
  <section class="work-strip"><div><p class="kicker">Le travail derrière la page</p><h2>Quatre contributions,<br>une trace consultable.</h2></div><ol><li><span>00</span>Qualifier<small>Demande & contraintes</small></li><li><span>01</span>Documenter<small>Sources & hypothèses</small></li><li><span>02</span>Calculer<small>Options & contrôles</small></li><li><span>03</span>Restituer<small>Conclusion & portée</small></li></ol>${proof('agents','Ouvrir les traces','outline')}</section>
  <section class="conditions-spread"><div><p class="kicker">Notes de portée / à conserver à chaque lecture</p><h2>Les limites font<br>partie du résultat.</h2><p>Quatre ans sont déclarés dans le profil. Les chocs sont calculés uniquement à l’échéance du retrait.</p></div><div>${limits(s)}<p class="fraction-note">Positions fractionnelles admises. Les deux chocs ne bornent pas la perte future. Le minimum de capital déplacé ne minimise ni risque ni frais réels, et ne maximise pas le rendement.</p>${proof('sources','Examiner les preuves disponibles')}</div></section>
  </main>
  <footer class="colophon"><div><span class="folio-seal" aria-hidden="true">f.</span><div><strong>Une décision se lit. Elle se discute. Elle se révise.</strong><p>Prototype Folio · dossier fictif Robert · archives réelles et calcul local</p></div></div><div class="archive-controls">${versionSelect(s)}<button data-action="reset">Revenir à l’édition initiale ↶</button>${s.history?.length?'<button data-action="undo">Annuler la dernière exploration ↶</button>':''}</div></footer>
  </div>`;
}

mount(render,{name:'Folio'});
