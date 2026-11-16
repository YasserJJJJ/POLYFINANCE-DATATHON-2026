/* Pupitre — direction 3 des prototypes ui-adam (Second avis, AlphaForge).
   Poste de contrôle du lecteur professionnel : volets fixes, clavier d'abord, journal, différences exactes.
   Toutes les valeurs viennent de window.AF (socle commun). Ce fichier ne calcule, n'invente ni n'arrondit
   aucun chiffre du produit : il choisit, aligne et met en forme. Les rares opérations locales sont des
   comptes (nombre de faits identiques) ou des sélections (creux d'une série), jamais une mesure nouvelle.
   Plan : utilitaires · état d'interface · barre d'état · volets A B C D · bande S et courbe · commandes · clavier. */
(() => {
  'use strict';
  const AF = window.AF;
  if (!AF) { document.body.textContent = 'Socle introuvable : ../socle/socle.js doit être chargé avant app.js.'; return; }

  /* ---------- utilitaires ---------- */
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  const esc = (v) => String(v == null ? '' : v).replace(/[&<>"']/g, (c) => ESC[c]);
  const norm = (s) => String(s == null ? '' : s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/\s+/g, ' ').trim();
  const lireP = (k, def) => { try { const v = localStorage.getItem('pupitre:' + k); return v == null ? def : JSON.parse(v); } catch (e) { return def; } };
  const ecrireP = (k, v) => { try { localStorage.setItem('pupitre:' + k, JSON.stringify(v)); } catch (e) { /* préférence non mémorisée */ } };
  const etroit = window.matchMedia('(max-width: 999.98px)');
  const fmt = AF.fmt;
  const pluriel = (n, mot) => `${n} ${mot}${n > 1 ? 's' : ''}`;
  const deux = (n) => String(n).padStart(2, '0');
  const heure = (ms) => { const t = new Date(ms); return `${deux(t.getHours())}:${deux(t.getMinutes())}:${deux(t.getSeconds())}`; };
  const idNum = (id) => parseInt(String(id).replace(/\D/g, ''), 10) || 0;
  const lireCle = (k) => { const o = Object.fromEntries(k.split(';').map((p) => p.split('='))); return { montant: +o.m, retrait: o.r === 'na' ? null : +o.r, exclusion: o.x === '1' }; };
  const cleTxt = (e) => `m=${e.montant} r=${e.retrait == null ? 'na' : e.retrait} x=${e.exclusion ? 1 : 0}`;

  /* Valeur exacte : la représentation la plus courte du nombre tel qu'il est stocké, virgule décimale, aucun arrondi. */
  function exact(n) {
    if (typeof n !== 'number' || !isFinite(n)) return String(n);
    const s = String(n);
    if (/e/i.test(s)) return s.replace('.', ',');
    const neg = s[0] === '-';
    const [ent, dec] = (neg ? s.slice(1) : s).split('.');
    return (neg ? '-' : '') + ent.replace(/\B(?=(\d{3})+(?!\d))/g, '\u00a0') + (dec ? ',' + dec : '');
  }
  function valeurTxt(v) {
    if (v == null || v === '') return '—';
    if (typeof v === 'number') return exact(v);
    if (typeof v === 'string') return v;
    if (Array.isArray(v)) return pluriel(v.length, 'élément');
    if (v.debut && v.fin) return `${v.debut} → ${v.fin}${v.observations != null ? ` · ${exact(v.observations)} obs.` : ''}`;
    return Object.entries(v).map(([k, x]) => `${k} ${typeof x === 'number' ? exact(x) : x}`).join(' · ');
  }
  function valeurLongue(f) {
    const v = f.valeur;
    if (Array.isArray(v)) return `<ol class="liste-val">${v.map((x) => `<li>${esc(typeof x === 'number' ? exact(x) : x)}</li>`).join('')}</ol>`;
    if (v && typeof v === 'object' && !(v.debut && v.fin)) {
      return `<table class="t t-val"><tbody>${Object.entries(v).map(([k, x]) => `<tr><th scope="row">${esc(k)}</th><td class="num">${esc(typeof x === 'number' ? exact(x) : x)}</td></tr>`).join('')}</tbody></table>`;
    }
    return `<span class="num grand">${esc(valeurTxt(v))}${f.unite && typeof v === 'number' ? ' ' + esc(f.unite) : ''}</span>`;
  }

  /* Signes : jamais la couleur seule. */
  const SIG = { coherent: '[OK]', ajustement: '[~~]', incoherent: '[XX]', indetermine: '[??]' };
  const SIG_R = { ok: '[OK]', orange: '[~~]', rouge: '[XX]', gris: '[??]', non_evaluee: '[--]' };
  const sigV = (e) => `<span class="sig sig-${esc(e)}" title="${esc((AF.ETATS[e] || {}).long || e)}">${SIG[e] || '[??]'}</span>`;
  const sigR = (n) => (n == null ? '<span class="sig sig-absent" title="règle absente">[  ]</span>' : `<span class="sig sig-${esc(n)}" title="${esc(AF.NIVEAUX_REGLE[n] || n)}">${SIG_R[n] || '[??]'}</span>`);
  const NAT = { donnee: ['DON', 'donnée'], preference: ['PRF', 'préférence'], contrainte: ['CTR', 'contrainte'], inconnu: ['???', 'inconnue'] };
  const TY = { FAIT: 'FAIT', HYPOTHESE: 'HYP', SCENARIO: 'SCÉN' };
  const tyTag = (t) => (t ? `<span class="ty ty-${esc(t)}" title="${esc(AF.TYPES[t] || t)}">${esc(TY[t] || t)}</span>` : '');
  const MODELE = new Set(['Profileur', 'Sceptique', 'Rédacteur']);
  const GR = { incoherent: '█', ajustement: '▒', coherent: '·', indetermine: '?' };
  const SPECIAUX = { sans_epargne: 'sans épargne connue', impossible: "montant supérieur à l'épargne", hors_univers: 'actif hors univers' };
  const PROTOS = [['1-carnet', '1 Carnet'], ['2-relief', '2 Relief'], ['4-fil', '4 Fil'], ['5-epure', '5 Épure']];
  const ISSUES = { confirmee: 'confirmée', limite: 'limite notée', ecartee: 'écartée' };
  const SENS = { aggrave: 'baisse plus profonde', ameliore: 'baisse moins profonde', neutre: 'baisse inchangée' };
  const BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]];

  /* ---------- état d'interface (jamais un chiffre du produit) ---------- */
  const ui = {
    tri: lireP('tri', { cle: 'id', sens: 1 }),
    filtre: '', types: new Set(), origine: 'tous', liesSeuls: false,
    selFait: null, /* libellé : les numéros F-n changent d'une variante à l'autre */
    selRegle: null, etapeOuverte: null,
    diff: null, contexte: lireP('contexte', false),
    onglet: 'a', zoom: null, special: null,
    demo: 'normal', demoEtape: null, demoStop: null,
    relecture: null, relStop: null,
    curseur: null, fenetre: null,
    msg: { texte: 'Prêt. Tape / pour une commande, ? pour les raccourcis.', type: 'info' },
    theme: lireP('theme', 'sombre'),
    ouverts: lireP('ouverts', {}),
    vuLive: '',
  };
  let courbe = null;
  let lastFocus = null;

  function ctx() {
    const base = { hist: AF.historique(), pos: AF.position(), niveau: AF.niveau() };
    if (ui.special) {
      const s = AF.speciaux[ui.special] || {};
      return { ...base, special: ui.special, d: s.dossier || null, erreur: s.dossier ? null : s, statut: 'special', etat: null, brouillon: null };
    }
    return { ...base, special: null, d: AF.dossier(), erreur: null, statut: AF.statut(), etat: AF.etat(), brouillon: AF.brouillon() };
  }
  const message = (texte, type = 'info') => { ui.msg = { texte, type }; };
  const ouvert = (k, def = true) => ((ui.ouverts[k] == null ? def : ui.ouverts[k]) ? 'open' : '');

  /* Puces de faits : de n'importe quel chiffre à sa preuve en un geste. rev = révision d'origine quand ce n'est pas le dossier affiché. */
  function puce(id, d, rev) {
    const f = d ? AF.fait(id, d) : null;
    if (!f) return `<span class="fc-x" title="fait absent de ce dossier">${esc(id)}</span>`;
    return rev == null
      ? `<button type="button" class="fc" data-act="fait" data-id="${esc(id)}" title="${esc(f.libelle)}">${esc(id)}</button>`
      : `<button type="button" class="fc" data-act="faitRev" data-i="${rev}" data-id="${esc(id)}" title="${esc(f.libelle)} (révision r${rev + 1})">${esc(id)}</button>`;
  }
  const puces = (ids, d, rev) => [...new Set(ids || [])].map((id) => puce(id, d, rev)).join(' ');
  const lier = (txt, d, rev) => esc(txt).replace(/\bF-\d+\b/g, (id) => (d && AF.fait(id, d) ? puce(id, d, rev) : id));
  const bouton = (act, label, o = {}) => `<button type="button" data-act="${act}" data-k="${esc(o.k || act)}"${o.i != null ? ` data-i="${o.i}"` : ''}${o.cls ? ` class="${o.cls}"` : ''}${o.dis ? ' disabled' : ''}${o.titre ? ` title="${esc(o.titre)}"` : ''}>${label}</button>`;

  /* ---------- rendu général ---------- */
  function render() {
    const c = ctx();
    const k = document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.k : null;
    const B = document.body;
    B.dataset.niveau = c.niveau;
    B.dataset.statut = c.statut;
    B.dataset.demo = ui.demo;
    B.dataset.onglet = ui.onglet;
    $('#pupitre').dataset.zoom = ui.zoom || '';
    renderBandeau();
    renderEtat(c);
    renderA(c);
    renderB(c);
    renderC(c);
    renderD(c);
    renderBande(c);
    renderCmd(c);
    $$('#onglets [data-o]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.o === ui.onglet)));
    $$('.zoom').forEach((b) => { const on = ui.zoom === b.dataset.v; b.setAttribute('aria-pressed', String(on)); b.textContent = on ? 'réduire' : 'agrandir'; });
    if (k) {
      const a = document.activeElement;
      if (!(a && a.dataset && a.dataset.k === k && document.contains(a))) { const el = document.querySelector(`[data-k="${CSS.escape(k)}"]`); if (el && !el.disabled) el.focus({ preventScroll: true }); }
    }
  }

  function renderBandeau() {
    const m = AF.meta || {};
    $('#meta').textContent = `· ${String(m.genere_le || '').replace('T', ' ')} · commit ${m.commit || '?'}`;
    $('#liens-protos').innerHTML = PROTOS.map(([dir, nom]) => `<a href="${esc(AF.lien(`../${dir}/index.html`))}">${esc(nom)}</a>`).join('');
    $('#demo').value = ui.demo;
    const bt = $('#b-theme');
    bt.textContent = `thème ${ui.theme}`;
    bt.removeAttribute('aria-pressed');
  }

  /* ---------- barre d'état ---------- */
  function paramsTxt(d, e) {
    const p = AF.parametres(e.cas);
    const bits = [`<b>${esc(d.demande.ticker)}</b>`, `montant analysé <b>${esc(fmt.cad(e.montant))}</b>`, `retrait ${esc(fmt.retrait(e.retrait))}`];
    if (p.exclusion.length > 1) bits.push(`exclusion du secteur Énergie : ${e.exclusion ? 'oui' : 'non'}`);
    return bits.join(' · ');
  }
  function liveHtml(c) {
    const { d } = c;
    const rev = `r${c.pos + 1}`;
    let v;
    if (ui.demo === 'erreur') v = '<span class="sig sig-err">[!!]</span> <b>Verdict non rendu</b> <span class="mut">vérifications du Sceptique non exécutées (démonstration)</span>';
    else if (ui.demo === 'chargement' || ui.demo === 'reprise') v = `<span class="sig sig-att">[..]</span> <b>${ui.demo === 'chargement' ? 'Chargement' : 'Reprise'} en cours</b> <span class="mut">(démonstration${ui.demoEtape ? ' · ' + esc(ui.demoEtape) : ''})</span>`;
    else if (c.erreur) v = `<span class="sig sig-err">[!!]</span> <b>Aucun verdict</b> <span class="mut">erreur ${esc(c.erreur.statut)}</span>`;
    else v = `${sigV(d.verdict.etat)} <b>${esc(AF.ETATS[d.verdict.etat].long)}</b> <span class="mut">${d.verdict.respectees}/${d.verdict.evaluees} règles respectées</span>`;
    if (c.statut === 'apercu' && ui.demo === 'normal') v = `<s>${v}</s> <span class="mut">(${rev}, périmé)</span>`;
    const st = {
      courante: `<span class="statut s-courante">■ COURANTE ${rev}</span> <span class="mut">dernière révision analysée</span>`,
      archive: `<span class="statut s-archive">▤ ARCHIVE ${rev}</span> <span class="mut">lecture seule · la courante est r${c.hist.length}</span>`,
      apercu: `<span class="statut s-apercu">◇ APERÇU : RÉSULTAT PÉRIMÉ</span> <span class="mut">${c.brouillon ? esc(AF.decrire(c.etat, c.brouillon)) : ''} · non analysé</span>`,
      special: `<span class="statut s-special">△ CAS PARTICULIER</span> <span class="mut">${esc(SPECIAUX[c.special])} · hors révisions · lecture seule</span>`,
    }[c.statut];
    return `<span class="seg"><span class="eti">Verdict</span> ${v}</span> <span class="seg"><span class="eti">Statut</span> ${st}</span>`;
  }
  function renderEtat(c) {
    const { d } = c;
    $('#etat-cas').innerHTML = AF.cas().map((k) => `<button type="button" data-act="cas" data-cas="${k}" data-k="cas:${k}" aria-pressed="${!c.special && c.etat.cas === k}">${esc(AF.nomCas(k))}</button>`).join('');
    $('#etat-special').value = c.special || '';
    let dem = '';
    if (c.erreur) dem = `<span class="err">Erreur ${esc(c.erreur.statut)} :</span> ${esc(c.erreur.message)}`;
    else if (d) {
      dem = `<q>${esc(d.demande.texte)}</q> <span class="fl" aria-hidden="true">→</span> ${c.special ? `<b>${esc(d.demande.ticker)}</b> · montant <b>${esc(fmt.cad(d.demande.montant_cad))}</b>` : paramsTxt(d, c.etat)}`;
    }
    $('#etat-demande').innerHTML = dem;
    const html = liveHtml(c);
    if (html !== ui.vuLive) { $('#etat-live').innerHTML = html; ui.vuLive = html; }
    const act = [];
    if (c.statut === 'apercu') act.push(bouton('analyser', '<kbd>⏎</kbd> analyser', { cls: 'b-fort', k: 'et-analyser' }), bouton('abandonner', '<kbd>Échap</kbd> abandonner', { k: 'et-abandonner' }));
    if (c.statut === 'archive') act.push(bouton('restaurer', `restaurer r${c.pos + 1}`, { i: c.pos, k: 'et-restaurer' }), bouton('aller', `aller à la courante r${c.hist.length}`, { i: c.hist.length - 1, k: 'et-aller' }));
    if (c.statut === 'special') act.push(bouton('retour', `<kbd>Échap</kbd> retour à r${c.pos + 1}`, { k: 'et-retour' }));
    act.push(bouton('annuler', '<kbd>u</kbd> annuler', { dis: !!c.special || !AF.peutAnnuler(), k: 'et-annuler', titre: 'revient à la révision parente' }));
    act.push(bouton('retablir', '<kbd>U</kbd> rétablir', { dis: !!c.special || !AF.peutRetablir(), k: 'et-retablir' }));
    $('#etat-actions').innerHTML = act.join(' ');
    $('#b-ess').setAttribute('aria-pressed', String(c.niveau === 'essentiel'));
    $('#b-app').setAttribute('aria-pressed', String(c.niveau === 'approfondi'));
  }

  /* ---------- volet A : verdict, règles, ce qui changerait, grille, profil, options ---------- */
  function squelette(note, n = 6) {
    const l = Array.from({ length: n }, (_, i) => `<div class="sq-l" style="width:${[92, 70, 84, 58, 76, 64, 88][i % 7]}%"></div>`).join('');
    return `<div class="squelette" aria-hidden="true">${l}</div><p class="mut">${esc(note)}</p>`;
  }
  function renderA(c) {
    const el = $('#a-corps');
    const { d } = c;
    if (c.erreur) { el.innerHTML = blocErreur(c); $('#a-info').textContent = 'aucune règle évaluée'; return; }
    if (ui.demo === 'chargement' || ui.demo === 'reprise') {
      el.innerHTML = squelette(ui.demo === 'chargement' ? "Démonstration : le Gardien n'a pas encore appliqué les règles. Les étapes se relisent dans le journal (volet C)." : 'Démonstration : reprise à partir du Sceptique ; le Gardien rendra le verdict après lui.');
      $('#a-info').textContent = 'en attente';
      return;
    }
    el.innerHTML = [blocVerdict(c), ui.demo === 'erreur' ? '' : blocRegles(c), blocChangerait(c), blocGrille(c), blocProfil(c), blocOptions(c), blocLimites(c)].join('');
    $('#a-info').textContent = ui.demo === 'erreur' ? 'non arbitré' : `${d.verdict.respectees}/${d.verdict.evaluees} respectées`;
  }
  function blocErreur(c) {
    return `<div class="verdict v-err"><p class="v-l1"><span class="sig sig-err">[!!]</span> <strong>Demande refusée avant analyse</strong></p>
      <p>Erreur ${esc(c.erreur.statut)} : ${esc(c.erreur.message)}</p>
      <p class="mut">Aucun rôle n'a tourné : pas de règle, pas de fait, pas de verdict. Le registre (B) liste les ${AF.donnees.actifs.length} actifs du jeu de départ. Choisir un autre actif n'est pas réalisé dans ce prototype.</p>
      <p>${bouton('retour', `<kbd>Échap</kbd> retour à la révision r${c.pos + 1}`, { k: 'a-retour' })}</p></div>`;
  }
  function boutonReponse(c) {
    if (c.special) return '<p class="mut petit">Répondre n\'est pas réalisé dans ce prototype : cette information n\'est pas un paramètre précalculé.</p>';
    const p = AF.parametres(c.etat.cas);
    const base = c.brouillon || c.etat;
    if (base.retrait == null) {
      return p.retrait.filter((r) => r != null).map((r) => `<p>${`<button type="button" data-act="proposer" data-k="rep:${r}" data-patch="${esc(JSON.stringify({ retrait: r }))}">aperçu : retrait ${esc(fmt.retrait(r))}</button>`} <span class="mut petit">puis ⏎ pour analyser</span></p>`).join('');
    }
    return '';
  }
  function blocVerdict(c) {
    const { d } = c;
    const v = d.verdict;
    const t = d.texte || {};
    if (ui.demo === 'erreur') {
      return `<div class="verdict v-err"><p class="v-l1"><span class="sig sig-err">[!!]</span> <strong>Verdict non rendu</strong> <span class="tag">démonstration</span></p>
        <p>Le Sceptique n'a pas répondu. Le Gardien ne décide pas sans ses vérifications : aucun verdict n'est affiché plutôt qu'un verdict incomplet.</p>
        <p class="mut">Reste valable : ${pluriel((d.faits || []).length, 'fait')} produits par l'Analyste (volet B). Manque : ${pluriel((d.objections || []).length, 'vérification')} du Sceptique, puis l'arbitrage du Gardien et le texte du Rédacteur.</p>
        <p><button type="button" class="b-fort" data-act="reprendre" data-k="reprendre">Reprendre à partir du Sceptique</button></p></div>`;
    }
    const q = d.questions || [];
    const conditionnel = q.length > 0 && v.etat !== 'indetermine';
    let h = `<div class="verdict v-${esc(v.etat)}">
      <p class="v-l1">${sigV(v.etat)} <strong>${esc(AF.ETATS[v.etat].long)}</strong></p>
      <p class="v-l2">${v.respectees}/${v.evaluees} règles respectées · <span class="mut">décidé par le Gardien (code), jamais par un modèle</span></p>`;
    if (t.reformulation) h += `<p class="reform"><span class="eti">compris</span> ${lier(AF.propre(t.reformulation), d)}</p>`;
    if (q.length) h += `<div class="question"><p class="eti">${conditionnel ? 'Conclusion conditionnelle · question décisive' : 'Information manquante'}</p>${q.map((x) => `<p>${lier(AF.propre(x), d)}</p>`).join('')}${boutonReponse(c)}</div>`;
    (t.miroir || []).forEach((p) => { h += `<p class="miroir">${tyTag(p.type)} ${lier(AF.propre(p.texte), d)} ${puces(p.faits, d)}</p>`; });
    return h + '</div>';
  }
  function refsListe(ids) {
    const refs = (ids || []).map(AF.reference).filter(Boolean);
    return refs.length ? `<ol class="refs">${refs.map(refHtml).join('')}</ol>` : '<p class="mut">aucune référence</p>';
  }
  function refHtml(r) {
    return `<li><span class="rid">[${esc(r.id)}]</span> ${esc(r.auteurs)}${r.annee ? ` (${esc(r.annee)})` : ''}. <i>${esc(r.titre)}</i>${r.publication ? `. ${esc(r.publication)}` : ''}. ${r.lien ? `<a href="${esc(r.lien)}" target="_blank" rel="noopener noreferrer">lien ↗<span class="sr"> (nouvel onglet)</span></a>` : '<span class="mut">sans lien public</span>'}
      <br><span class="mut petit">${esc(r.type)} · examen : ${esc(r.examen)}</span>${r.apport ? `<br><span class="petit">apport : ${esc(r.apport)}</span>` : ''}</li>`;
  }
  function blocRegles(c) {
    const { d } = c;
    const rs = d.regles || [];
    let h = `<h3 class="st">Règles du Gardien <span class="mut">${rs.length}</span></h3>`;
    if (c.niveau === 'essentiel') {
      return h + `<ul class="regles-ess">${rs.map((r) => `<li>${sigR(r.niveau)} <b>${esc(r.libelle)}</b> <span class="mut">: ${esc((AF.NIVEAUX_REGLE[r.niveau] || r.niveau).toLowerCase())}</span><br><span class="expl">${lier(AF.propre(r.explication), d)}</span> ${puces(r.faits, d)}</li>`).join('')}</ul>`;
    }
    h += '<table class="t t-regles"><caption class="sr">Règles : niveau, code, libellé, type, nombre de faits liés ; sous chaque règle, son explication et ses faits</caption><thead><tr><th scope="col">niv.</th><th scope="col">code</th><th scope="col">libellé</th><th scope="col">type</th><th scope="col" class="num">faits</th></tr></thead><tbody>';
    rs.forEach((r) => {
      const sel = r.code === ui.selRegle;
      const mot = (AF.NIVEAUX_REGLE[r.niveau] || r.niveau).toLowerCase();
      const n = new Set(r.faits || []).size;
      h += `<tr class="r-l1${sel ? ' sel' : ''}"><td class="niv">${sigR(r.niveau)}<span class="sr"> ${esc(mot)}</span></td>
        <td><button type="button" class="lien-r" data-act="regle" data-code="${esc(r.code)}" data-k="r:${esc(r.code)}" aria-expanded="${sel}" title="déplier ses références et relier ses faits dans le registre">${esc(r.code)}</button></td>
        <td>${esc(r.libelle)}</td><td>${tyTag(r.type)}</td><td class="num">${n || '—'}</td></tr>
        <tr class="r-l2${sel ? ' sel' : ''}"><td></td><td colspan="4"><span class="expl">${lier(AF.propre(r.explication), d)}</span> ${puces(r.faits, d)}${sel ? `<div class="r-refs"><p class="eti">références (${(r.references || []).length})</p>${refsListe(r.references)}</div>` : ''}</td></tr>`;
    });
    return h + '</tbody></table><p class="legende petit">[OK] respectée · [~~] à ajuster · [XX] bloquante · [??] information manquante · un code : ses références, et ses faits marqués ◂ dans le registre</p>';
  }
  function blocChangerait(c) {
    const { d } = c;
    const lignes = (d.texte && d.texte.ce_qui_changerait) || [];
    let h = '<h3 class="st">Ce qui changerait l\'avis</h3>';
    if (!lignes.length) h += '<p class="mut">Le moteur ne signale aucun changement qui modifierait ce verdict dans cette simulation.</p>';
    h += lignes.map((p) => `<p>${tyTag(p.type)} ${lier(AF.propre(p.texte), d)} ${puces(p.faits, d)}</p>`).join('');
    if (!c.special) {
      const p = AF.parametres(c.etat.cas);
      (d.options || []).filter((o) => o.changement && o.changement.montant_cad != null).forEach((o) => {
        const m = o.changement.montant_cad;
        h += p.montant.includes(m)
          ? `<p><button type="button" data-act="proposer" data-k="pp:${m}" data-patch="${esc(JSON.stringify({ montant: m }))}">aperçu : montant ${esc(fmt.cad(m))}</button> <span class="mut petit">puis ⏎ pour analyser</span></p>`
          : `<p class="mut petit">${esc(fmt.cad(m))} : montant non précalculé, aperçu non réalisable dans ce prototype.</p>`;
      });
    }
    return h;
  }
  function blocGrille(c) {
    if (c.special) return '';
    const C = AF.donnees.cas[c.etat.cas];
    const dep = C.variantes[C.depart];
    const b = dep.bascule;
    if (!b || !b.cases || !b.cases.length) return '';
    const de = lireCle(C.depart);
    const base = c.etat;
    const brouillon = c.brouillon && c.brouillon.montant !== base.montant ? c.brouillon.montant : null;
    const applique = base.retrait === de.retrait && base.exclusion === de.exclusion;
    const hz = c.d.profil.horizon_ans;
    const p = AF.parametres(c.etat.cas);
    const etat = {};
    b.cases.forEach((x) => { etat[`${x.montant_cad}|${x.horizon_ans}`] = x.etat; });
    const conditions = [`retrait ${fmt.retrait(de.retrait)}`];
    if (p.exclusion.length > 1) conditions.push(`exclusion du secteur Énergie : ${de.exclusion ? 'oui' : 'non'}`);
    const tete = b.horizons.map((h) => `<th scope="col" class="${h === hz ? 'ici' : ''}"><span aria-hidden="true">${h === 1 || h % 5 === 0 ? h : (h === hz ? '▾' : '')}</span><span class="sr">${h} an${h > 1 ? 's' : ''}</span></th>`).join('');
    const lignes = b.montants.map((m) => {
      const cur = m === base.montant;
      const lab = applique && !cur && p.montant.includes(m)
        ? `<button type="button" class="g-m" data-act="proposer" data-k="gm:${m}" data-patch="${esc(JSON.stringify({ montant: m }))}" title="aperçu avec ce montant"${m === brouillon ? ' aria-pressed="true"' : ''}>${m === brouillon ? '◇ ' : ''}${esc(fmt.cad(m))}</button>`
        : `<span class="g-m">${cur ? '▸ ' : ''}${esc(fmt.cad(m))}</span>`;
      return `<tr class="${cur ? 'ici' : ''}"><th scope="row">${lab}</th>${b.horizons.map((h) => { const e = etat[`${m}|${h}`]; return `<td class="g-${esc(e)}${cur && h === hz ? ' cible' : ''}"><span aria-hidden="true">${GR[e] || ' '}</span><span class="sr">${esc((AF.ETATS[e] || {}).court || '')}</span></td>`; }).join('')}</tr>`;
    }).join('');
    const grille = `<div class="defile" tabindex="0" aria-label="Grille de bascule, défilable"><table class="grille"><caption class="sr">Verdict par montant (lignes) et horizon en années (colonnes), calculé pour la demande de départ</caption><thead><tr><th scope="col"><span class="sr">montant</span><span aria-hidden="true">ans →</span></th>${tete}</tr></thead><tbody>${lignes}</tbody></table></div>
      <p class="legende petit"><span class="g-incoherent">█</span> incohérent · <span class="g-ajustement">▒</span> ajustement · <span class="g-coherent">·</span> cohérent · <span class="g-indetermine">?</span> indéterminé · ▸ montant affiché · ◇ aperçu · colonne marquée : horizon du profil (${esc(hz)} ans). L'horizon n'est pas modifiable dans ce prototype.</p>`;
    let h = `<h3 class="st">Grille de bascule <span class="mut">montant × horizon · ${b.cases.length} cases</span></h3>
      <p class="petit mut">Calculée par le Gardien pour la demande de départ (${esc(conditions.join(', '))}).${!b.montants.includes(base.montant) ? ` ${esc(fmt.cad(base.montant))} n'est pas une ligne de la grille.` : ''}${applique ? ' Clique un montant pour en faire un aperçu.' : ''}</p>`;
    if (!applique) h += `<details class="hors" ${ouvert('grille-hors', false)} data-sec="grille-hors"><summary>Ne s'applique pas à l'état affiché : voir quand même la grille de départ</summary>${grille}</details>`;
    else h += grille;
    return h;
  }
  function blocProfil(c) {
    const { d } = c;
    const ess = c.niveau === 'essentiel';
    const L = AF.profilLignes(d);
    const p = c.special ? null : AF.parametres(c.etat.cas);
    const nInc = L.filter((l) => l.nature === 'inconnu').length;
    const modifiable = { retrait: p && p.retrait.length > 1 ? 'retrait ' : null, exclusions: p && p.exclusion.length > 1 ? 'exclusion ' : null };
    let h = `<h3 class="st">Profil compris <span class="mut">${L.length} lignes · ${pluriel(nInc, 'inconnue')}</span></h3>`;
    h += `<p class="ro petit"><b>Lecture seule.</b> ${c.special ? 'Cas particulier : aucun paramètre modifiable.' : `Corrigeable par commande : montant${modifiable.retrait ? ', retrait' : ''}${modifiable.exclusions ? ', exclusion' : ''}. Les autres lignes ne sont pas modifiables dans ce prototype.`}</p>`;
    if (!c.special) h += `<p class="petit">Demande : <b>${esc(d.demande.ticker)}</b> · montant analysé <b>${esc(fmt.cad(c.etat.montant))}</b>${c.brouillon && c.brouillon.montant !== c.etat.montant ? ` <span class="mut">(aperçu : ${esc(fmt.cad(c.brouillon.montant))}, non analysé)</span>` : ''} <button type="button" data-act="palette" data-pre="montant " data-k="mod-montant">modifier</button></p>`;
    h += `<table class="t t-profil"><caption class="sr">Ce que le produit a compris, avec la nature de chaque ligne</caption><thead><tr><th scope="col">nature</th><th scope="col">ligne</th><th scope="col">valeur</th></tr></thead><tbody>`;
    L.forEach((l) => {
      const n = NAT[l.nature] || [l.nature, l.nature];
      const mod = modifiable[l.cle] ? ` <button type="button" data-act="palette" data-pre="${modifiable[l.cle]}" data-k="mod-${l.cle}">modifier</button>` : '';
      h += `<tr class="n-${esc(l.nature)}"><td><span class="nat nat-${esc(l.nature)}" title="${esc(n[1])}">${esc(ess ? n[1] : n[0])}</span></td><td>${esc(l.libelle)}${l.note ? `<div class="mut petit">${esc(l.note)}</div>` : ''}</td><td>${l.valeur == null || l.valeur === '' ? '<b class="inconnu">inconnue, non remplacée</b>' : esc(l.valeur)}${mod}</td></tr>`;
    });
    h += '</tbody></table>';
    if (!ess) h += '<p class="legende petit">DON donnée · PRF préférence · CTR contrainte · ??? inconnue</p>';
    const cit = (d.profil && d.profil.citations) || [];
    if (cit.length) h += `<p class="petit"><span class="eti">tu as dit</span> ${cit.map((x) => `<q>${esc(x)}</q>`).join(' · ')}</p>`;
    const tens = (d.texte && d.texte.tensions) || (d.profil && d.profil.tensions) || [];
    if (tens.length) h += `<ul class="tensions petit">${tens.map((x) => `<li><span class="eti">tension</span> ${esc(AF.propre(x))}</li>`).join('')}</ul>`;
    return h;
  }
  function blocOptions(c) {
    const { d } = c;
    const os = d.options || [];
    if (!os.length) return '';
    return `<h3 class="st">Options comparées <span class="mut">ordre du moteur, pas un classement</span></h3>
      <table class="t t-options"><thead><tr><th scope="col">état</th><th scope="col">option</th><th scope="col" class="num">montant</th></tr></thead><tbody>${os.map((o) => `<tr><td class="niv">${sigV(o.etat)}<span class="niv-mot">${esc(((AF.ETATS[o.etat] || {}).court || '').toLowerCase())}</span></td>
        <td><b>${esc(o.nom)}</b> · ${esc(o.ticker)}${o.libelle_actif ? ` <span class="mut">${esc(o.libelle_actif)}</span>` : ''}${o.constat || o.note ? `<div class="expl">${lier(AF.propre(o.constat || o.note), d)} ${puces(o.faits, d)}</div>` : ''}</td>
        <td class="num">${esc(fmt.cad(o.montant_cad))}</td></tr>`).join('')}</tbody></table>`;
  }
  function blocLimites(c) {
    const { d } = c;
    const L = (d.texte && d.texte.limites) || [];
    if (!L.length) return '';
    return `<details class="sec" ${ouvert('limites', false)} data-sec="limites"><summary class="st">Limites <span class="mut">${L.length}</span></summary><ol class="limites">${L.map((p) => `<li>${tyTag(p.type)} ${lier(AF.propre(p.texte), d)} ${puces(p.faits, d)}</li>`).join('')}</ol></details>${d.texte.avertissement ? `<p class="petit mut">${esc(d.texte.avertissement)}</p>` : ''}`;
  }

  /* ---------- volet B : registre des faits et preuve ---------- */
  function rail(v, c) {
    const d = c.d;
    const n = d ? (d.faits || []).length : 0;
    const txt = v === 'b' ? `B · Registre des faits · ${pluriel(n, 'fait')}` : `C · Journal · ${pluriel(c.hist.length, 'révision')} · ${pluriel(d && d.trace ? d.trace.length : 0, 'étape')}`;
    return `<button type="button" class="rail-btn" data-act="niveau" data-n="approfondi" data-k="rail-${v}"><span class="rail-txt">${esc(txt)}</span><span class="rail-aide">replié en Essentiel : ouvrir en Approfondi</span></button>`;
  }
  function cmpFaits(a, b, k) {
    if (k === 'id') return idNum(a.id) - idNum(b.id);
    if (k === 'valeur') {
      const x = typeof a.valeur === 'number', y = typeof b.valeur === 'number';
      if (x && y) return a.valeur - b.valeur;
      if (x !== y) return x ? -1 : 1;
      return valeurTxt(a.valeur).localeCompare(valeurTxt(b.valeur), 'fr');
    }
    const va = k === 'lu' ? a.lu_ou_calcule : a[k], vb = k === 'lu' ? b.lu_ou_calcule : b[k];
    return String(va || '').localeCompare(String(vb || ''), 'fr') || idNum(a.id) - idNum(b.id);
  }
  function faitsVisibles(c) {
    const d = c.d;
    const faits = (d && d.faits) || [];
    const regle = ui.selRegle && d ? (d.regles || []).find((r) => r.code === ui.selRegle) : null;
    const lies = regle ? new Set(regle.faits || []) : null;
    const q = norm(ui.filtre);
    const rows = faits.filter((f) => (!ui.types.size || ui.types.has(f.type))
      && (ui.origine === 'tous' || f.lu_ou_calcule === ui.origine)
      && (!ui.liesSeuls || !lies || lies.has(f.id))
      && (!q || norm([f.id, f.libelle, valeurTxt(f.valeur), f.unite, f.source, f.methode, f.type].join(' ')).includes(q)));
    rows.sort((a, b) => cmpFaits(a, b, ui.tri.cle) * ui.tri.sens);
    return { faits, rows, lies, regle };
  }
  function renderB(c) {
    const corps = $('#b-corps'), pu = $('#b-puces'), pr = $('#b-preuve');
    $('#b-rail').innerHTML = rail('b', c);
    if (c.erreur) {
      const A = AF.donnees.actifs || [];
      pu.innerHTML = '';
      corps.innerHTML = `<p class="petit mut">Aucun fait : la demande a été refusée avant les calculs. Univers du jeu de départ (${A.length} actifs), lecture seule :</p>
        <table class="t t-faits"><thead><tr><th scope="col">ticker</th><th scope="col">nom</th><th scope="col">classe</th><th scope="col">marché</th><th scope="col">devise</th><th scope="col">secteur</th></tr></thead><tbody>${A.map((a) => `<tr><td>${esc(a.ticker)}</td><td>${esc(a.name)}</td><td>${esc(a.asset_class)}</td><td>${esc(a.market)}</td><td>${esc(a.currency)}</td><td>${esc(a.sector)}</td></tr>`).join('')}</tbody></table>`;
      pr.innerHTML = '';
      $('#b-info').textContent = `${A.length} actifs`;
      return;
    }
    if (ui.demo === 'chargement') { pu.innerHTML = ''; corps.innerHTML = squelette("Démonstration : l'Analyste n'a pas encore écrit ses faits.", 10); pr.innerHTML = ''; $('#b-info').textContent = 'en attente'; return; }
    const { faits, rows, lies, regle } = faitsVisibles(c);
    const d = c.d;
    const compte = (pred) => faits.filter(pred).length;
    const tb = (act, val, lab, n, on) => `<button type="button" data-act="${act}" data-v="${esc(val)}" data-k="${act}:${esc(val)}" aria-pressed="${on}">${esc(lab)} <span class="mut">${n}</span></button>`;
    pu.innerHTML = `<span role="group" aria-label="Filtrer par type">${['FAIT', 'HYPOTHESE', 'SCENARIO'].map((t) => tb('type', t, TY[t], compte((f) => f.type === t), ui.types.has(t))).join('')}</span>
      <span role="group" aria-label="Filtrer par origine">${tb('origine', 'lu', 'lu', compte((f) => f.lu_ou_calcule === 'lu'), ui.origine === 'lu')}${tb('origine', 'calcule', 'calculé', compte((f) => f.lu_ou_calcule === 'calcule'), ui.origine === 'calcule')}</span>
      ${regle ? `<span role="group" aria-label="Faits liés à une règle">${tb('lies', '1', `liés à ${regle.code}`, lies.size, ui.liesSeuls)}<button type="button" data-act="effacerRegle" data-k="effacerRegle" aria-label="Ne plus relier à la règle ${esc(regle.code)}">×</button></span>` : ''}
      <span class="compte" aria-live="polite">${rows.length}/${faits.length}</span>`;
    const th = (cle, lab, cls = '') => {
      const on = ui.tri.cle === cle;
      return `<th scope="col" class="${cls}" aria-sort="${on ? (ui.tri.sens > 0 ? 'ascending' : 'descending') : 'none'}"><button type="button" class="tri" data-act="trier" data-cle="${cle}" data-k="tri:${cle}">${lab}<span aria-hidden="true">${on ? (ui.tri.sens > 0 ? ' ▲' : ' ▼') : ' ·'}</span></button></th>`;
    };
    const sel = ui.selFait;
    corps.innerHTML = !faits.length
      ? '<p class="mut">Aucun fait dans ce dossier : la demande a été arrêtée avant les calculs.</p>'
      : `<table class="t t-faits"><caption class="sr">Registre des faits du dossier, triable ; ↑ ↓ pour parcourir</caption><thead><tr>${th('id', 'id')}${th('libelle', 'libellé')}${th('valeur', 'valeur exacte', 'num')}${th('unite', 'unité')}${th('type', 'type')}${th('lu', 'origine')}</tr></thead><tbody>
        ${rows.map((f) => { const s = f.libelle === sel, l = lies && lies.has(f.id); return `<tr class="${s ? 'sel' : ''}${l ? ' lie' : ''}"><td><button type="button" class="fid" data-act="fait" data-id="${esc(f.id)}" data-k="f:${esc(f.id)}" aria-pressed="${s}">${esc(f.id)}</button>${l ? '<span class="lie-m" title="lié à la règle sélectionnée">◂</span>' : ''}</td><td class="lib">${esc(f.libelle)}</td><td class="num val" title="${esc(valeurTxt(f.valeur))}">${esc(valeurTxt(f.valeur))}</td><td class="u">${esc(f.unite)}</td><td>${tyTag(f.type)}</td><td>${f.lu_ou_calcule === 'lu' ? 'lu' : 'calculé'}</td></tr>`; }).join('')}
        </tbody></table>${rows.length ? '' : `<p class="mut">Aucun fait ne correspond. <button type="button" data-act="effacerFiltres" data-k="effacerFiltres">effacer les filtres</button></p>`}`;
    const f = sel ? faits.find((x) => x.libelle === sel) : null;
    pr.innerHTML = f ? preuveHtml(f, d, null, !rows.includes(f))
      : `<p class="mut petit"><b>Preuve.</b> Sélectionne un fait (clic, <kbd>j</kbd> <kbd>k</kbd>, ou <code>fait F-12</code>) : valeur exacte, type, source, méthode, puis références. Deux gestes au plus : chiffre → fait → référence.</p>`;
    $('#b-info').textContent = `${rows.length}/${faits.length}`;
    const inp = $('#b-filtre');
    if (inp.value !== ui.filtre) inp.value = ui.filtre;
  }
  function usagesDe(id, d, rev) {
    const u = [];
    (d.regles || []).forEach((r) => { if ((r.faits || []).includes(id)) u.push(rev == null ? `<button type="button" class="lien-r" data-act="regle" data-code="${esc(r.code)}">règle ${esc(r.code)}</button>` : `<span class="tag">règle ${esc(r.code)}</span>`); });
    const t = d.texte || {};
    [['miroir', 'miroir'], ['pourquoi', 'pourquoi'], ['ce_qui_changerait', 'ce qui changerait'], ['limites', 'limite']].forEach(([k, lab]) => (t[k] || []).forEach((p, i) => { if ((p.faits || []).includes(id)) u.push(`<span class="tag">phrase « ${lab} » ${i + 1}</span>`); }));
    (d.trace || []).forEach((s) => { if ((s.faits || []).includes(id)) u.push(`<span class="tag">étape ${esc(s.agent)}</span>`); });
    (d.objections || []).forEach((o) => { if (o.cible === id) u.push(`<span class="tag">objection ${esc(o.id)}</span>`); });
    (d.options || []).forEach((o) => { if ((o.faits || []).includes(id)) u.push(`<span class="tag">option « ${esc(o.nom)} »</span>`); });
    Object.entries((d.comparaison && d.comparaison.faits) || {}).forEach(([k, v]) => { if (v === id) u.push(`<span class="tag">mesure ${esc(k.replace(/_/g, ' '))}</span>`); });
    return u.join(' ');
  }
  function preuveHtml(f, d, rev, masque) {
    const usages = usagesDe(f.id, d, rev);
    return `<div class="preuve">
      <p class="p-tete"><span class="fid-g">${esc(f.id)}</span> ${tyTag(f.type)} <span class="mut">${esc(AF.TYPES[f.type] || f.type)} · ${f.lu_ou_calcule === 'lu' ? 'lu tel quel' : 'calculé'}${rev != null ? ` · révision r${rev + 1}` : ''}${masque ? ' · masqué par le filtre' : ''}</span></p>
      <p class="p-lib">${esc(f.libelle)}</p>
      <dl class="p-dl">
        <dt>valeur exacte</dt><dd>${valeurLongue(f)}${f.unite && typeof f.valeur !== 'number' ? ` <span class="mut">unité : ${esc(f.unite)}</span>` : ''}</dd>
        <dt>source</dt><dd>${esc(f.source)}</dd>
        <dt>méthode</dt><dd>${lier(f.methode, d, rev)}</dd>
        <dt>références <span class="mut">${(f.references || []).length}</span></dt><dd>${refsListe(f.references)}</dd>
        <dt>utilisé par</dt><dd>${usages || '<span class="mut">aucun renvoi dans ce dossier</span>'}</dd>
      </dl></div>`;
  }
  function ouvrirFiche(f, d, titre, rev) {
    $('#fiche-titre').textContent = titre;
    $('#fiche-corps').innerHTML = preuveHtml(f, d, rev);
    const dlg = $('#fiche');
    if (!dlg.open) { lastFocus = document.activeElement; dlg.showModal(); }
  }
  function ouvrirFait(id) {
    const c = ctx();
    const f = c.d ? AF.fait(id, c.d) : null;
    if (!f) return;
    if (c.niveau === 'essentiel' || etroit.matches || $('#fiche').open) { ouvrirFiche(f, c.d, `Fait ${f.id}`); return; }
    ui.selFait = f.libelle;
    render();
    const b = document.querySelector(`#b-corps [data-k="f:${CSS.escape(f.id)}"]`);
    if (b) { b.focus({ preventScroll: true }); b.scrollIntoView({ block: 'nearest' }); }
  }
  function ouvrirFaitRev(i, id) {
    const h = AF.historique()[i];
    if (!h) return;
    const d = AF.dossierDe(h.etat);
    const f = AF.fait(id, d);
    if (f) ouvrirFiche(f, d, `Fait ${f.id} · révision r${i + 1}`, i);
  }
  function deplacerFait(pas) {
    const c = ctx();
    const { rows } = faitsVisibles(c);
    if (!rows.length) return;
    const i = rows.findIndex((f) => f.libelle === ui.selFait);
    const n = rows[Math.max(0, Math.min(rows.length - 1, i < 0 ? 0 : i + pas))];
    ui.selFait = n.libelle;
    render();
    const b = document.querySelector(`#b-corps [data-k="f:${CSS.escape(n.id)}"]`);
    if (b) { b.focus({ preventScroll: true }); b.scrollIntoView({ block: 'nearest' }); }
  }

  /* ---------- volet C : journal ---------- */
  function renderC(c) {
    $('#c-rail').innerHTML = rail('c', c);
    $('#c-corps').innerHTML = blocRevisions(c) + blocEtapes(c) + blocAppels(c);
    $('#c-info').textContent = pluriel(c.hist.length, 'révision');
    /* Pendant une relecture, l'étape en cours reste sous les yeux. */
    if (ui.relecture || ui.demo === 'erreur') {
      const e = $('#c-corps .t-etapes tr.e-cours, #c-corps .t-etapes tr.e-echec') || $('#c-etapes');
      const box = $('#c-corps');
      if (e && box && (!etroit.matches || ui.onglet === 'c')) {
        const top = e.getBoundingClientRect().top - box.getBoundingClientRect().top + box.scrollTop - 60;
        if (!etroit.matches) box.scrollTop = Math.max(0, top);
      }
    }
  }
  function blocRevisions(c) {
    const H = c.hist;
    const s = diffSel(c);
    let h = `<details class="sec" ${ouvert('revisions')} data-sec="revisions"><summary class="st">Révisions <span class="mut">log · ${H.length}</span></summary><ol class="log">`;
    for (let i = H.length - 1; i >= 0; i--) {
      const r = H[i];
      const cur = r.courant;
      const tags = [cur ? 'HEAD' : '', i === H.length - 1 ? 'dernière' : '', cur && c.statut === 'apercu' ? 'aperçu en attente' : ''].filter(Boolean).join(' · ');
      const branche = r.parent >= 0 && r.parent !== i - 1;
      h += `<li class="rev${cur ? ' cur' : ''}">
        <div class="r1"><p><span class="g" aria-hidden="true">${cur ? '●' : '○'}</span> <b>r${i + 1}</b> ${sigV(r.verdict)} <time>${heure(r.heure)}</time>${tags ? ` <span class="tagr">(${tags})</span>` : ''}</p>
          <p class="r4">${bouton('aller', 'lire', { i, k: `rl:${i}`, dis: cur && !c.special, titre: `relire r${i + 1} (archive si ce n'est pas la dernière)` })}${bouton('restaurer', 'restaurer', { i, k: `rr:${i}`, titre: `nouvelle révision identique à r${i + 1} ; rien n'est effacé` })}<button type="button" data-act="diffA" data-i="${i}" data-k="ra:${i}" aria-pressed="${!!s && s.a === i}" title="base du diff (−)" aria-label="r${i + 1} comme base du diff">−</button><button type="button" data-act="diffB" data-i="${i}" data-k="rb:${i}" aria-pressed="${!!s && s.b === i}" title="révision comparée (+)" aria-label="r${i + 1} comme révision comparée">+</button></p></div>
        <p class="r2">${esc(r.motif)}</p>
        <p class="r3 mut">${r.parent >= 0 ? `parent r${r.parent + 1}${branche ? ' (branche)' : ''}` : 'racine'} · ${esc(r.nom)} · ${esc(cleTxt(r.etat))}</p></li>`;
    }
    return h + '</ol></details>';
  }
  const ETAPE_TXT = { fait: '✓ fait', cours: '… en cours', attente: 'en attente', echec: '✗ échec (démo)', non: 'non exécuté' };
  function etatEtape(i) {
    if (ui.demo === 'erreur') return i < 3 ? 'fait' : i === 3 ? 'echec' : 'non';
    const r = ui.relecture;
    if (!r) return null;
    if (i < r.i) return 'fait';
    if (i === r.i) return r.phase === 'fait' ? 'fait' : 'cours';
    return 'attente';
  }
  function detailEtape(s, d) {
    let h = `<p><b>${esc(s.action)}</b> · ${lier(AF.propre(s.detail), d)}</p>`;
    const role = (AF.donnees.sources.agents || {})[s.agent];
    if (role) h += `<p class="mut petit">rôle : ${esc(role.role)}</p>`;
    if (s.faits && s.faits.length) h += `<p class="petit">faits : ${puces(s.faits, d)}</p>`;
    if (s.agent === 'Contrôle données' && (d.qualite_donnees || []).length) h += `<ul class="qual petit">${d.qualite_donnees.map((q) => `<li>${q.statut === 'ok' ? '<span class="sig sig-ok">[OK]</span>' : '<span class="sig sig-rouge">[XX]</span>'} ${esc(q.libelle)} <span class="mut">${esc(q.detail)}</span></li>`).join('')}</ul>`;
    if (s.agent === 'Sceptique' && (d.objections || []).length) h += `<ol class="obj petit">${d.objections.map((o) => `<li><b>${esc(o.id)}</b> → ${puce(o.cible, d)} <q>${esc(o.texte)}</q><br><span class="mut">recalcul exécuté par le code :</span> ${esc(o.recalcul)}<br><span class="mut">réponse :</span> ${lier(AF.propre(o.reponse), d)} <span class="tag">${esc(ISSUES[o.issue] || o.issue)}</span></li>`).join('')}</ol>`;
    if (s.agent === 'Rédacteur' && d.texte && d.texte.source) h += `<p class="petit mut">texte : ${esc(d.texte.source)}${(d.texte.controle || []).length ? ` · contrôle : ${esc(d.texte.controle.join(' ; '))}` : ''}</p>`;
    if ((s.references || []).length) h += `<details class="petit"><summary>références (${s.references.length})</summary>${refsListe(s.references)}</details>`;
    return h;
  }
  function blocEtapes(c) {
    const { d } = c;
    const tr = (d && d.trace) || [];
    const ex = c.special ? null : AF.execution(c.etat.cas);
    const exDur = {};
    ((ex && ex.trace) || []).forEach((t) => { exDur[t.agent] = t.duree_ms; });
    let h = `<details class="sec" id="c-etapes" ${ui.relecture || ui.demo === 'erreur' ? 'open' : ouvert('etapes')} data-sec="etapes"><summary class="st">Étapes des rôles <span class="mut">${tr.length}</span></summary>`;
    if (!tr.length) return h + `<p class="mut">Aucune étape enregistrée pour ce dossier${c.erreur || c.special === 'impossible' ? ' : la demande a été arrêtée avant les rôles' : ''}.</p></details>`;
    if (ui.demo === 'erreur') h += '<p class="petit"><span class="tag">démonstration</span> Échec simulé du Sceptique : Gardien et Rédacteur ne sont pas exécutés. <button type="button" data-act="reprendre" data-k="reprendre-c">reprendre à partir du Sceptique</button></p>';
    h += `<p class="petit mut">CODE : Contrôle données, Analyste, Gardien. MOD (modèle) : Profileur, Sceptique, Rédacteur ; dans ce dossier, ils ont tourné hors ligne (règles et gabarits).</p>
      <p class="petit">${bouton('relire', ui.relecture && ui.demo === 'normal' ? '■ arrêter la relecture' : '▶ relire la trace', { k: 'relire' })} <span class="mut">relecture des étapes enregistrées, pas un agent en direct</span></p>
      <table class="t t-etapes"><caption class="sr">Étapes des rôles, durées hors ligne et durées Bedrock enregistrées</caption><thead><tr><th scope="col">#</th><th scope="col">rôle</th><th scope="col">nature</th><th scope="col" class="num">hors ligne</th><th scope="col" class="num">Bedrock*</th><th scope="col" class="num">faits</th></tr></thead><tbody>`;
    tr.forEach((s, i) => {
      const e = etatEtape(i);
      const o = ui.etapeOuverte === i;
      h += `<tr class="${e ? 'e-' + e : ''}"><td>${i + 1}</td><td><button type="button" class="lien-r" data-act="etape" data-i="${i}" data-k="etp:${i}" aria-expanded="${o}">${esc(s.agent)}</button>${e ? ` <span class="e-tag">${ETAPE_TXT[e]}</span>` : ''}</td><td><span class="nat">${MODELE.has(s.agent) ? 'MOD' : 'CODE'}</span></td><td class="num">${esc(fmt.ms(s.duree_ms))}</td><td class="num">${exDur[s.agent] != null ? esc(fmt.ms(exDur[s.agent])) : '—'}</td><td class="num">${new Set(s.faits || []).size}</td></tr>`;
      if (o) h += `<tr class="det"><td></td><td colspan="5">${detailEtape(s, d)}</td></tr>`;
    });
    h += `</tbody></table><p class="petit mut">* Bedrock : durées de l'exécution réellement enregistrée pour la demande de départ${c.special ? '' : ` de ${esc(AF.nomCas(c.etat.cas))}`}, pas pour cette révision.</p></details>`;
    return h;
  }
  function blocAppels(c) {
    const { d } = c;
    const propres = (d && d.appels_modele) || [];
    let h = `<details class="sec" ${ouvert('appels')} data-sec="appels"><summary class="st">Appels de modèle</summary>`;
    const tab = (L) => `<table class="t t-appels"><caption class="sr">Appels de modèle : rôle, modèle, identifiant de requête, jetons, latence</caption><thead><tr><th scope="col">rôle · modèle · requête</th><th scope="col" class="num">jetons entrée</th><th scope="col" class="num">jetons sortie</th><th scope="col" class="num">latence</th></tr></thead><tbody>${L.map((a) => `<tr><td><b>${esc(a.agent)}</b> <span class="mut">${esc(a.modele)}</span><div class="rq">req ${esc(a.request_id)}</div><div class="mut petit">arrêt ${esc(a.stop_reason || '—')} · garde-fou ${esc(a.garde_fou)}</div></td><td class="num">${esc(exact(a.jetons_entree))}</td><td class="num">${esc(exact(a.jetons_sortie))}</td><td class="num">${esc(exact(a.latence_ms))} ms</td></tr>`).join('')}</tbody></table>`;
    h += propres.length ? tab(propres) : `<p class="petit"><span class="sig sig-non_evaluee">[--]</span> Ce dossier : aucun appel de modèle : mode hors ligne${d && d.texte && (d.texte.controle || []).length ? ` (${esc(d.texte.controle.join(' ; '))})` : ''}.</p>`;
    const ex = c.special ? null : AF.execution(c.etat.cas);
    if (ex) {
      const de = lireCle(AF.donnees.cas[c.etat.cas].depart);
      const meme = de.montant === c.etat.montant && de.retrait === c.etat.retrait && de.exclusion === c.etat.exclusion;
      h += `<p class="petit">Exécution Bedrock <b>réellement enregistrée</b> pour la demande de départ de ${esc(AF.nomCas(c.etat.cas))} (${esc(cleTxt(de))})${meme ? ", c'est l'état affiché" : ', pas pour l\'état affiché'}. <span class="mut">source : ${esc(ex.source)}</span></p>${tab(ex.appels_modele || [])}`;
      const tx = ex.texte;
      if (tx && (tx.pourquoi || []).length) {
        h += `<details class="petit" ${ouvert('ex-texte', false)} data-sec="ex-texte"><summary>texte rédigé par le modèle lors de cette exécution (${pluriel(tx.pourquoi.length, 'phrase')} « pourquoi »)</summary>
          ${tx.reformulation ? `<p>${esc(AF.propre(tx.reformulation))}</p>` : ''}<ol>${tx.pourquoi.map((p) => `<li>${tyTag(p.type)} ${esc(AF.propre(p.texte))} <span class="mut">${esc((p.faits || []).join(', '))}</span></li>`).join('')}</ol>
          <p class="mut">Les numéros cités renvoient au dossier de départ.</p></details>`;
      }
    } else h += '<p class="petit mut">Aucune exécution Bedrock enregistrée pour cette situation.</p>';
    return h + '</details>';
  }

  /* ---------- volet D : diff entre deux révisions ---------- */
  function diffSel(c) {
    const n = c.hist.length;
    if (ui.diff && ui.diff.n === n && ui.diff.a < n && ui.diff.b < n) return ui.diff;
    /* Par défaut : parente → affichée ; une archive relue se compare à la courante. */
    if (c.statut === 'archive') return { a: c.pos, b: n - 1, defaut: true };
    const b = c.pos;
    const p = c.hist[b].parent;
    const a = p >= 0 ? p : (b > 0 ? b - 1 : null);
    return a == null ? null : { a, b, defaut: true };
  }
  const fmtMesure = (v, u, exacte) => (v == null ? '—' : exacte ? `${exact(v)} ${u === '$' ? '$' : '%'}` : u === '$' ? fmt.cad(v) : fmt.pct(v, 1));
  function faitsChanges(dA, dB) {
    const fa = new Map((dA.faits || []).map((f) => [f.libelle, f]));
    const fb = new Map((dB.faits || []).map((f) => [f.libelle, f]));
    const libs = [...new Set([...fa.keys(), ...fb.keys()])];
    let identiques = 0, renum = 0;
    const chg = [];
    libs.forEach((l) => {
      const x = fa.get(l), y = fb.get(l);
      if (x && y && JSON.stringify(x.valeur) === JSON.stringify(y.valeur) && x.unite === y.unite) { identiques++; if (x.id !== y.id) renum++; } else chg.push([x || null, y || null]);
    });
    return { identiques, renum, chg };
  }
  function renderD(c) {
    const out = $('#d-outils'), el = $('#d-corps');
    const H = c.hist;
    const s = diffSel(c);
    const opt = (sel) => H.map((r, i) => `<option value="${i}"${sel === i ? ' selected' : ''}>r${i + 1} ${esc(SIG[r.verdict])} ${esc(r.nom)}</option>`).join('');
    out.innerHTML = H.length < 2 ? '' : `<label title="révision de base (−)"><span class="m-del" aria-hidden="true">−</span><span class="sr">base</span><select data-chg="diffA" data-k="dsa">${opt(s && s.a)}</select></label>
      <label title="révision comparée (+)"><span class="m-ins" aria-hidden="true">+</span><span class="sr">comparée</span><select data-chg="diffB" data-k="dsb">${opt(s && s.b)}</select></label>
      ${bouton('diffDefaut', 'défaut', { dis: !s || s.defaut, k: 'diffDefaut', titre: 'parente → affichée (une archive se compare à la courante)' })}<button type="button" data-act="contexte" data-k="contexte" aria-pressed="${ui.contexte}" title="afficher aussi les lignes inchangées">contexte</button>`;
    let pre = '';
    if (c.statut === 'apercu') pre = `<p class="d-apercu"><span class="statut s-apercu">◇ APERÇU</span> Paramètres en attente, absents du diff tant que l'analyse n'est pas lancée : ${esc(AF.decrire(c.etat, c.brouillon))}. ${bouton('analyser', '<kbd>⏎</kbd> analyser', { k: 'd-analyser', cls: 'b-fort' })}</p>`;
    if (c.special) pre = '<p class="d-apercu petit"><span class="statut s-special">△</span> Le cas particulier est hors révisions : le diff ci-dessous porte sur l\'historique.</p>';
    if (!s) {
      el.innerHTML = pre + videDiff(c);
      $('#d-info').textContent = `r${c.pos + 1} seule`;
      return;
    }
    $('#d-info').textContent = `r${s.a + 1} → r${s.b + 1}${s.defaut ? ' (par défaut)' : ''}`;
    if (s.a === s.b) { el.innerHTML = `${pre}<p>r${s.a + 1} comparée à elle-même : aucune différence.</p>`; return; }
    el.innerHTML = pre + (c.niveau === 'essentiel' ? diffPhrases(c, s) : diffTable(c, s));
  }
  /* Sans deuxième révision, le volet D devient la table des paramètres précalculés : chaque bouton crée un aperçu. */
  function videDiff(c) {
    let h = `<p>Une seule révision (r${c.pos + 1}) : rien à comparer.</p><p class="mut">Crée un aperçu (bouton ci-dessous, ou <kbd>/</kbd> puis <code>montant 38000</code>), puis <kbd>⏎</kbd> pour l'analyser : le diff exact s'affichera ici, ligne à ligne, avec <span class="m-del">−</span> et <span class="m-ins">+</span>.</p>`;
    if (c.special) return h;
    const p = AF.parametres(c.etat.cas);
    const b = c.brouillon || c.etat;
    const grp = (titre, cle, vals, lab) => `<fieldset class="params"><legend>${esc(titre)} <span class="mut">${vals.length} valeur${vals.length > 1 ? 's' : ''} précalculée${vals.length > 1 ? 's' : ''}</span></legend>${vals.map((v) => `<button type="button" data-act="proposer" data-k="dv:${cle}:${v}" data-patch="${esc(JSON.stringify({ [cle]: v }))}" aria-pressed="${v === b[cle]}">${esc(lab(v))}</button>`).join('')}</fieldset>`;
    h += `<h3 class="st">Paramètres modifiables</h3>${grp('montant', 'montant', p.montant, fmt.cad)}`;
    h += p.retrait.length > 1 ? grp('retrait prévu', 'retrait', p.retrait, fmt.retrait) : `<p class="petit mut">retrait prévu : ${esc(fmt.retrait(p.retrait[0]))} (seule valeur précalculée)</p>`;
    h += p.exclusion.length > 1 ? grp('exclusion du secteur Énergie', 'exclusion', p.exclusion, (x) => (x ? 'oui' : 'non')) : '';
    return h + '<p class="petit mut">Valeur enfoncée : celle de la révision affichée (ou de l\'aperçu). Aucune autre valeur n\'existe dans ce prototype.</p>';
  }
  function diffTable(c, s) {
    const A = c.hist[s.a], B = c.hist[s.b];
    const K = AF.comparer(A.etat, B.etat);
    const dA = AF.dossierDe(A.etat), dB = AF.dossierDe(B.etat);
    const rows = [];
    let debutSec = -1;
    const finSec = () => { if (debutSec >= 0 && rows.length === debutSec + 1) rows.push('<tr class="d-ctx"><td colspan="2"><span class="m" aria-hidden="true">=</span>aucun changement</td></tr>'); };
    const sec = (t, n) => { finSec(); rows.push(`<tr class="d-sec"><th colspan="2" scope="colgroup">${t}${n ? ` <span class="mut">${n}</span>` : ''}</th></tr>`); debutSec = rows.length - 1; };
    const cel = (cote, html) => (html == null ? '<td class="d-abs"><span class="m" aria-hidden="true">∅</span> <span class="mut">absent</span></td>'
      : cote === '-' ? `<td class="del"><span class="m" aria-hidden="true">−</span><span class="sr">avant : </span><del>${html}</del></td>`
        : `<td class="ins"><span class="m" aria-hidden="true">+</span><span class="sr">après : </span><ins>${html}</ins></td>`);
    const ligne = (g, dr, change) => {
      if (change) rows.push(`<tr class="d-ch">${cel('-', g)}${cel('+', dr)}</tr>`);
      else if (ui.contexte) rows.push(`<tr class="d-ctx"><td><span class="m" aria-hidden="true"> </span>${g}</td><td><span class="m" aria-hidden="true"> </span>${dr}</td></tr>`);
    };
    rows.push(`<tr class="d-tete"><th scope="col"><span class="m-del">−</span> r${s.a + 1} <span class="mut">${heure(A.heure)} · ${esc(A.nom)}</span></th><th scope="col"><span class="m-ins">+</span> r${s.b + 1} <span class="mut">${heure(B.heure)} · ${esc(B.nom)}</span></th></tr>`);
    sec('Paramètres', esc(K.motif));
    const pr = (e) => ({ situation: AF.nomCas(e.cas), montant: fmt.cad(e.montant), retrait: fmt.retrait(e.retrait), exclusion: e.exclusion ? 'oui' : 'non' });
    const pa = pr(A.etat), pb = pr(B.etat);
    Object.keys(pa).forEach((k) => ligne(`${k} ${esc(pa[k])}`, `${k} ${esc(pb[k])}`, pa[k] !== pb[k]));
    sec('Verdict');
    const vt = (d) => `${sigV(d.verdict.etat)} ${esc(AF.ETATS[d.verdict.etat].court)} · ${d.verdict.respectees}/${d.verdict.evaluees}`;
    const vChange = K.verdict.change || dA.verdict.respectees !== dB.verdict.respectees || dA.verdict.evaluees !== dB.verdict.evaluees;
    if (vChange) ligne(vt(dA), vt(dB), true);
    else rows.push(`<tr class="d-ctx"><td><span class="m" aria-hidden="true">=</span>${vt(dA)}</td><td><span class="m" aria-hidden="true">=</span>${vt(dB)}</td></tr>`);
    const nR = K.regles.filter((r) => r.change).length;
    sec('Règles', `${nR} changée${nR > 1 ? 's' : ''} sur ${K.regles.length}`);
    K.regles.forEach((r) => ligne(r.avant == null ? null : `${sigR(r.avant)} ${esc(r.code)}`, r.apres == null ? null : `${sigR(r.apres)} ${esc(r.code)}`, r.change));
    const nM = K.mesures.filter((m) => m.avant !== m.apres).length;
    sec('Mesures appariées', `${nM} changée${nM > 1 ? 's' : ''} · portefeuille avec la demande, même fenêtre`);
    K.mesures.forEach((m) => ligne(`${esc(m.titre)} <b class="num">${esc(fmtMesure(m.avant, m.unite, true))}</b>`, `${esc(m.titre)} <b class="num">${esc(fmtMesure(m.apres, m.unite, true))}</b>`, m.avant !== m.apres));
    const F = faitsChanges(dA, dB);
    sec('Faits', `${F.chg.length} différent(s) · ${F.identiques} identique(s)${F.renum ? `, dont ${F.renum} renuméroté(s)` : ''}`);
    const fl = (f, rev, d) => (f ? `${puce(f.id, d, rev)} ${esc(f.libelle)}<br><b class="num">${esc(valeurTxt(f.valeur))}${f.unite ? ' ' + esc(f.unite) : ''}</b>` : null);
    F.chg.forEach(([x, y]) => rows.push(`<tr class="d-ch">${cel('-', fl(x, s.a, dA))}${cel('+', fl(y, s.b, dB))}</tr>`));
    const qa = dA.questions || [], qb = dB.questions || [];
    if (qa.length || qb.length) {
      sec('Questions');
      const n = Math.max(qa.length, qb.length);
      for (let i = 0; i < n; i++) ligne(qa[i] == null ? null : esc(AF.propre(qa[i])), qb[i] == null ? null : esc(AF.propre(qb[i])), qa[i] !== qb[i]);
    }
    finSec();
    return `<table class="diff"><caption class="sr">Différence entre r${s.a + 1} (moins) et r${s.b + 1} (plus)</caption><tbody>${rows.join('')}</tbody></table>
      <p class="petit mut">Valeurs exactes du moteur. Les faits sont appariés par libellé : leurs numéros peuvent changer d'une révision à l'autre. Aucun écart n'est recalculé ici.</p>`;
  }
  function diffPhrases(c, s) {
    const A = c.hist[s.a], B = c.hist[s.b];
    const K = AF.comparer(A.etat, B.etat);
    const dA = AF.dossierDe(A.etat), dB = AF.dossierDe(B.etat);
    const niv = (n) => (n == null ? 'absente' : (AF.NIVEAUX_REGLE[n] || n).toLowerCase());
    const P = [];
    P.push(`Tu compares la révision ${s.a + 1} (${heure(A.heure)}) et la révision ${s.b + 1} (${heure(B.heure)}).`);
    P.push(K.motif === 'Sans changement' ? 'Mêmes paramètres des deux côtés.' : `Ce qui a changé : ${esc(K.motif)}.`);
    P.push(K.verdict.change
      ? `Le verdict passe de <del>${sigV(K.verdict.avant)} ${esc(AF.ETATS[K.verdict.avant].long)}</del> à <ins>${sigV(K.verdict.apres)} ${esc(AF.ETATS[K.verdict.apres].long)}</ins>.`
      : `Le verdict ne change pas : ${sigV(K.verdict.apres)} ${esc(AF.ETATS[K.verdict.apres].long)}.`);
    const rc = K.regles.filter((r) => r.change);
    if (rc.length) rc.forEach((r) => P.push(`Règle « ${esc(r.libelle)} » : <del>${sigR(r.avant)} ${niv(r.avant)}</del> → <ins>${sigR(r.apres)} ${niv(r.apres)}</ins>.`));
    else P.push('Aucune règle ne change de niveau.');
    K.mesures.forEach((m) => P.push(m.avant === m.apres ? `${esc(m.titre)} : inchangée (${esc(fmtMesure(m.apres, m.unite))}).` : `${esc(m.titre)} : <del>${esc(fmtMesure(m.avant, m.unite))}</del> → <ins>${esc(fmtMesure(m.apres, m.unite))}</ins>.`));
    const F = faitsChanges(dA, dB);
    P.push(`${pluriel(F.chg.length, 'fait')} ${F.chg.length > 1 ? 'ont' : 'a'} une autre valeur ; le détail exact est en Approfondi.`);
    return `<ol class="d-phrases">${P.map((p) => `<li>${p}</li>`).join('')}</ol><p class="petit mut">Mesures du portefeuille avec la demande, sur la même fenêtre passée ; elles décrivent le passé et ne prédisent rien.</p>`;
  }

  /* ---------- bande S : mesures appariées et courbe des baisses ---------- */
  function renderBande(c) {
    const m = $('#s-mesures'), cb = $('#s-courbe');
    const { d } = c;
    if (c.erreur || !d || !d.comparaison || !d.comparaison.disponible) {
      courbe = null;
      m.innerHTML = `<p class="mut petit">Comparaison sans / avec la demande indisponible${d && d.comparaison && d.comparaison.raison ? ` : ${esc(d.comparaison.raison)}` : ''}.</p>`;
      cb.innerHTML = '<header class="vt"><h2>Courbe des baisses</h2></header><p class="mut petit vide-courbe">Pas de courbe pour ce dossier.</p>';
      return;
    }
    if (ui.demo === 'chargement') { courbe = null; m.innerHTML = squelette('Démonstration : mesures en attente.', 4); cb.innerHTML = '<header class="vt"><h2>Courbe des baisses</h2></header>' + squelette('Démonstration : courbe en attente.', 3); return; }
    m.innerHTML = c.niveau === 'essentiel' ? mesuresPhrases(d) : mesuresTable(d);
    renderCourbe(c);
  }
  const IDS_MESURE = { pire_chute: ['avant_pire_chute', 'apres_pire_chute', 'ecart_pire_chute'], volatilite: ['avant_volatilite', 'apres_volatilite', 'ecart_volatilite'], rendement: ['avant_rendement', 'apres_rendement'], valeur_finale: ['avant_valeur_finale', 'apres_valeur_finale'] };
  function ecartTxt(m, exacte) {
    if (m.ecart == null) return '—';
    if (m.unite === '$') return `${exacte ? exact(Number(m.ecart.toFixed(2))) : fmt.nombre(m.ecart)} $`;
    return fmt.pts(m.ecart, exacte ? 6 : 1);
  }
  function mesuresTable(d) {
    const K = d.comparaison, fx = K.faits || {};
    const M = AF.mesures(d);
    return `<p class="petit mut">${esc(K.fenetre.debut)} → ${esc(K.fenetre.fin)} · ${esc(exact(K.fenetre.observations))} obs. · ${esc(K.politique)} ${puce(fx.fenetre_portefeuille, d)}</p>
      <table class="t t-mesures"><caption class="sr">Mesures appariées : sans la demande, avec la demande, écart après moins avant</caption><thead><tr><th scope="col" class="num">sans la demande</th><th scope="col" class="num">avec</th><th scope="col" class="num" title="après moins avant">écart</th></tr></thead>
      ${M.map((m) => `<tbody><tr class="m-tete"><th scope="colgroup" colspan="3" title="${esc(m.def)}">${esc(m.titre)} <span class="puces">${puces((IDS_MESURE[m.cle] || []).map((k) => fx[k]).filter(Boolean), d)}</span></th></tr>
        <tr class="m-val"><td class="num">${esc(fmtMesure(m.avant, m.unite, true))}</td><td class="num">${esc(fmtMesure(m.apres, m.unite, true))}</td><td class="num"><b>${esc(ecartTxt(m, true))}</b>${m.sens ? `<span class="sens petit">${esc(SENS[m.sens] || m.sens)}</span>` : ''}</td></tr></tbody>`).join('')}
      </table><p class="petit mut">Poids ${puce(fx.poids_avant, d)} → ${puce(fx.poids_apres, d)} · limites ${puce(fx.limites_portefeuille, d)}. Écarts des deux dernières mesures : différence fournie par le socle (après − avant).</p>`;
  }
  function mesuresPhrases(d) {
    const K = d.comparaison, fx = K.faits || {};
    return `<ul class="m-phrases">${AF.mesures(d).map((m) => `<li><b>${esc(m.titre)}</b> : ${esc(fmtMesure(m.avant, m.unite))} sans ta demande, ${esc(fmtMesure(m.apres, m.unite))} avec${m.sens ? ` ; écart ${esc(ecartTxt(m, false))}, ${esc(SENS[m.sens] || m.sens)}` : ''}. ${puces((IDS_MESURE[m.cle] || []).map((k) => fx[k]).filter(Boolean), d)}</li>`).join('')}</ul>
      <p class="petit mut">Observé du ${esc(K.fenetre.debut)} au ${esc(K.fenetre.fin)}, en achat-conservation : cela décrit le passé et ne prédit rien.</p>`;
  }
  const tms = (s) => Date.parse(s + 'T00:00:00Z');
  function argmin(serie) { let k = 0; serie.forEach((p, i) => { if (p[2] < serie[k][2]) k = i; }); return k; }
  function renderCourbe(c) {
    const { d } = c;
    const s = d.series_portefeuille;
    const cb = $('#s-courbe');
    if (!s || !s.avant || !s.avant.length) { courbe = null; cb.innerHTML = '<p class="mut petit vide-courbe">Pas de série pour ce dossier.</p>'; return; }
    const av = s.avant, ap = s.apres;
    const t0 = tms(av[0][0]), t1 = tms(av[av.length - 1][0]);
    const minA = argmin(av), minB = argmin(ap);
    const m = Math.min(av[minA][2], ap[minB][2]);
    const pas = m > -10 ? 2 : m > -30 ? 5 : m > -60 ? 10 : 20;
    const yMin = Math.min(-pas, Math.floor(m / pas) * pas);
    courbe = { av, ap, t0, t1, yMin, pas, minA, minB, d, fen: (s.avant_fenetres || []).map((w, i) => [w, (s.apres_fenetres || [])[i]]) };
    if (ui.curseur != null && ui.curseur >= av.length) ui.curseur = null;
    const pc = (ms) => ((ms - t0) / (t1 - t0) * 100);
    const ticks = [];
    for (let v = 0; v >= yMin; v -= pas) ticks.push(v);
    const ans = [];
    for (let y = new Date(t0).getUTCFullYear() + 1; Date.UTC(y, 0, 1) <= t1; y++) ans.push(y);
    const fen = courbe.fen.map(([w], i) => {
      const g = pc(tms(w.debut)), l = Math.max(0.6, pc(tms(w.fin)) - g);
      return `<button type="button" class="fen${g > 60 ? ' fen-d' : ''}" style="left:${g.toFixed(3)}%;width:${l.toFixed(3)}%" data-act="fenetre" data-i="${i}" data-k="fen:${i}" aria-pressed="${ui.fenetre === i}" title="${esc(w.nom)} : ${esc(w.debut)} → ${esc(w.fin)}"><span>${esc(w.nom)}</span></button>`;
    }).join('');
    cb.innerHTML = `<header class="vt"><h2>Courbe des baisses <span class="mut">sans / avec la demande</span></h2><span class="vt-info">observé ${esc(av[0][0])} → ${esc(av[av.length - 1][0])} · ${esc(exact(av.length))} points hebdomadaires · aucun prolongement</span><span class="tampon">périmé</span></header>
      <div class="c-corps">
        <div class="c-zone">
          <div class="c-y" aria-hidden="true">${ticks.map((v) => `<span style="top:${(v / yMin * 100).toFixed(3)}%">${v} %</span>`).join('')}</div>
          <canvas id="courbe" role="slider" tabindex="0" data-k="courbe" aria-label="Curseur de date sur la courbe des baisses ; flèches gauche et droite" aria-valuemin="0" aria-valuemax="${av.length - 1}"></canvas>
          <div class="c-x" aria-hidden="true">${ans.map((y) => `<span style="left:${pc(Date.UTC(y, 0, 1)).toFixed(3)}%">${y}</span>`).join('')}</div>
          <div class="c-fen" role="group" aria-label="Fenêtres historiques nommées">${fen}</div>
        </div>
        <p class="c-leg petit"><span class="lg-c">░</span> baisse commune · <span class="lg-p">▓</span> baisse en plus avec la demande · <span class="lg-m">╱</span> baisse en moins avec la demande · <span class="lg-a">●</span> trait sans · <span class="lg-b">●</span> trait avec</p>
        <output class="c-lecture petit" id="c-lecture" for="courbe" aria-live="polite"></output>
      </div>`;
    majCurseur(true);
  }
  function lectureHtml() {
    const C = courbe;
    if (!C) return '';
    const { av, ap, d } = C;
    const fx = (d.comparaison && d.comparaison.faits) || {};
    if (ui.fenetre != null && C.fen[ui.fenetre]) {
      const [w, w2] = C.fen[ui.fenetre];
      return `<b>${esc(w.nom)}</b> (${esc(w.debut)} → ${esc(w.fin)}) · rendement sans ${esc(exact(w.rendement_pct))} % / avec ${w2 ? esc(exact(w2.rendement_pct)) : '—'} % · pire chute sans ${esc(exact(w.pire_chute_pct))} % / avec ${w2 ? esc(exact(w2.pire_chute_pct)) : '—'} %`;
    }
    if (ui.curseur == null) {
      return `Creux de la série : sans ${esc(exact(av[C.minA][2]))} % (${esc(av[C.minA][0])}) · avec ${esc(exact(ap[C.minB][2]))} % (${esc(ap[C.minB][0])}) · série hebdomadaire, 1 point sur ${esc(AF.meta.pas_series || '?')} séances ; pire baisse sur toutes les séances : ${puce(fx.avant_pire_chute, d)} / ${puce(fx.apres_pire_chute, d)} · <kbd>←</kbd><kbd>→</kbd> ou survol pour lire une date`;
    }
    const i = ui.curseur;
    return `<b>${esc(av[i][0])}</b> · sans ${esc(exact(av[i][2]))} % (${esc(exact(av[i][1]))} $) · avec ${esc(exact(ap[i][2]))} % (${esc(exact(ap[i][1]))} $)`;
  }
  function majCurseur(sansDessin) {
    const cv = document.getElementById('courbe');
    const o = document.getElementById('c-lecture');
    if (!cv || !courbe) return;
    const i = ui.curseur;
    cv.setAttribute('aria-valuenow', String(i == null ? 0 : i));
    cv.setAttribute('aria-valuetext', i == null ? 'aucune date choisie' : `${courbe.av[i][0]} : sans la demande ${exact(courbe.av[i][2])} %, avec ${exact(courbe.ap[i][2])} %`);
    if (o) o.innerHTML = lectureHtml();
    $$('.fen').forEach((b) => b.setAttribute('aria-pressed', String(+b.dataset.i === ui.fenetre)));
    if (sansDessin) requestAnimationFrame(dessiner); else dessiner();
  }
  function dessiner() {
    const cv = document.getElementById('courbe');
    if (!cv || !courbe) return;
    const C = courbe;
    const r = cv.getBoundingClientRect();
    const W = Math.max(40, Math.floor(r.width)), H = Math.max(24, Math.floor(r.height));
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    if (cv.width !== W * dpr || cv.height !== H * dpr) { cv.width = W * dpr; cv.height = H * dpr; }
    const g = cv.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, W, H);
    const css = getComputedStyle(document.body);
    const col = { txt: css.getPropertyValue('--txt').trim(), mut: css.getPropertyValue('--dim').trim(), acc: css.getPropertyValue('--acc').trim(), line: css.getPropertyValue('--line2').trim() };
    const P = 4, cols = Math.max(1, Math.floor(W / P)), rows = Math.max(1, Math.floor(H / P));
    const colDe = (dt) => Math.min(cols - 1, Math.max(0, Math.floor((tms(dt) - C.t0) / (C.t1 - C.t0) * cols)));
    /* Profondeur par colonne : le point le plus bas tombé dans la colonne (sélection, pas de lissage). */
    const prof = (serie) => {
      const out = new Array(cols).fill(null);
      serie.forEach(([dt, , b]) => { const k = colDe(dt); out[k] = out[k] == null ? b : Math.min(out[k], b); });
      let last = 0;
      for (let k = 0; k < cols; k++) { if (out[k] == null) out[k] = last; else last = out[k]; }
      return out.map((b) => Math.min(rows, Math.round(b / C.yMin * rows)));
    };
    const dA = prof(C.av), dB = prof(C.ap);
    const dot = (k, j, color, s = 2) => { g.fillStyle = color; g.fillRect(k * P + (P - s) / 2, j * P + (P - s) / 2, s, s); };
    for (let v = 0; v >= C.yMin; v -= C.pas) { const j = Math.min(rows - 1, Math.round(v / C.yMin * rows)); for (let k = 0; k < cols; k += 2) dot(k, j, col.line, 1); }
    for (let y = new Date(C.t0).getUTCFullYear() + 1; Date.UTC(y, 0, 1) <= C.t1; y++) { const k = Math.floor((Date.UTC(y, 0, 1) - C.t0) / (C.t1 - C.t0) * cols); for (let j = 0; j < rows; j += 2) dot(k, j, col.line, 1); }
    for (let k = 0; k < cols; k++) {
      const a = dA[k], b = dB[k], lo = Math.min(a, b), hi = Math.max(a, b);
      for (let j = 0; j < hi; j++) {
        const m = BAYER[j % 4][k % 4];
        if (j < lo) { if (m < 4) dot(k, j, col.mut); } else if (b > a) { if (m < 12) dot(k, j, col.acc); } else if ((j + k) % 3 === 0) dot(k, j, col.acc, 1.5);
      }
      dot(k, Math.max(0, a - 1), col.txt, 2.5);
      dot(k, Math.max(0, b - 1), col.acc, 3);
    }
    if (ui.curseur != null) {
      const k = colDe(C.av[ui.curseur][0]);
      for (let j = 0; j < rows; j++) if (j % 2 === 0) dot(k, j, col.txt, 2);
    }
  }
  function curseurDepuisX(clientX) {
    const cv = document.getElementById('courbe');
    if (!cv || !courbe) return;
    const r = cv.getBoundingClientRect();
    const t = courbe.t0 + Math.max(0, Math.min(1, (clientX - r.left) / r.width)) * (courbe.t1 - courbe.t0);
    let best = 0;
    courbe.av.forEach((p, i) => { if (Math.abs(tms(p[0]) - t) < Math.abs(tms(courbe.av[best][0]) - t)) best = i; });
    ui.curseur = best;
    ui.fenetre = null;
    majCurseur();
  }

  /* ---------- ligne de commande ---------- */
  function renderCmd(c) {
    const qui = c.special ? c.special : c.etat.cas;
    $('#prompt').textContent = `${qui}@r${c.pos + 1}${c.statut === 'apercu' ? '*' : ''}${c.statut === 'archive' ? '(archive)' : ''}$ `;
    const m = $('#cmd-msg');
    m.textContent = ui.msg.texte;
    m.className = `cmd-msg m-${ui.msg.type}`;
    $('#cmd-actions').innerHTML = c.statut === 'apercu'
      ? `${bouton('analyser', '<kbd>⏎</kbd> analyser', { cls: 'b-fort', k: 'cmd-analyser' })} ${bouton('abandonner', '<kbd>Échap</kbd> abandonner', { k: 'cmd-abandonner' })}`
      : `${bouton('annuler', 'annuler', { dis: !!c.special || !AF.peutAnnuler(), k: 'cmd-annuler', cls: 'mobile-seul' })} ${bouton('retablir', 'rétablir', { dis: !!c.special || !AF.peutRetablir(), k: 'cmd-retablir', cls: 'mobile-seul' })}`;
  }

  /* ---------- commandes ---------- */
  function proposer(patch) {
    const c = ctx();
    if (c.special) return { err: 'Commande indisponible dans un cas particulier : tape « retour » ou Échap.' };
    if (!AF.proposer(patch)) return { err: 'Cette combinaison de paramètres n\'a pas été précalculée.' };
    if (!AF.perime()) return { ok: true, msg: "C'est déjà la valeur de la révision affichée : aucun aperçu." };
    return { ok: true, msg: `Aperçu créé : ${AF.decrire(AF.etat(), AF.brouillon())}. Résultat périmé : ⏎ pour analyser, Échap pour abandonner.` };
  }
  const valsRev = (c) => c.hist.map((r, i) => ({ arg: String(i + 1), desc: `r${i + 1} · ${AF.ETATS[r.verdict].court} · ${r.motif}`, actuel: i === c.pos }));
  const valsLibres = (L) => () => L.map(([arg, desc]) => ({ arg, desc }));
  const COMMANDES = [
    { nom: 'montant', arg: '<valeur>', aide: 'aperçu avec ce montant (valeurs précalculées)', valeurs: (c) => (c.special ? [] : AF.parametres(c.etat.cas).montant.map((m) => ({ arg: String(m), desc: fmt.cad(m), actuel: m === (c.brouillon || c.etat).montant }))), run: cmdMontant },
    { nom: 'retrait', arg: '<na|années>', aide: 'aperçu avec ce retrait prévu', valeurs: (c) => (c.special ? [] : AF.parametres(c.etat.cas).retrait.map((r) => ({ arg: r == null ? 'na' : String(r), desc: fmt.retrait(r), actuel: r === (c.brouillon || c.etat).retrait }))), run: cmdRetrait },
    { nom: 'exclusion', arg: '<oui|non>', aide: 'aperçu avec ou sans exclusion du secteur Énergie', valeurs: (c) => (c.special ? [] : AF.parametres(c.etat.cas).exclusion.map((x) => ({ arg: x ? 'oui' : 'non', desc: x ? 'secteur Énergie exclu' : 'aucune exclusion', actuel: x === (c.brouillon || c.etat).exclusion }))), run: cmdExclusion },
    { nom: 'analyser', aide: "analyse l'aperçu : nouvelle révision (⏎)", run: () => (AF.perime() ? (AF.appliquer(), ui.diff = null, { ok: true, msg: `Analyse appliquée : révision r${AF.position() + 1} créée. Diff r${AF.historique()[AF.position()].parent + 1} → r${AF.position() + 1} dans le volet D.` }) : { err: 'Aucun aperçu à analyser : modifie d\'abord un paramètre (montant, retrait, exclusion).' }) },
    { nom: 'abandonner', aide: "abandonne l'aperçu (Échap)", run: () => (AF.perime() ? (AF.abandonner(), { ok: true, msg: 'Aperçu abandonné : le résultat affiché est de nouveau à jour.' }) : { err: 'Aucun aperçu en attente.' }) },
    { nom: 'cas', arg: '<situation>', aide: 'change de situation, ou ouvre un cas particulier', valeurs: (c) => [...AF.cas().map((k) => ({ arg: k, desc: `${AF.nomCas(k)} · « ${AF.donnees.cas[k].variantes[AF.donnees.cas[k].depart].demande.texte} »`, actuel: !c.special && c.etat.cas === k })), ...Object.entries(SPECIAUX).map(([k, l]) => ({ arg: k, desc: `cas particulier : ${l}`, actuel: c.special === k }))], run: cmdCas },
    { nom: 'niveau', arg: '<essentiel|approfondi>', aide: 'niveau de lecture (n)', valeurs: (c) => [{ arg: 'essentiel', desc: 'règles, verdict et diff en phrases', actuel: c.niveau === 'essentiel' }, { arg: 'approfondi', desc: 'densité complète : registre et journal', actuel: c.niveau === 'approfondi' }], run: cmdNiveau },
    { nom: 'annuler', aide: 'revient à la révision parente (u)', run: () => (ui.special ? { err: 'Quitte d\'abord le cas particulier (Échap).' } : AF.annuler() ? (ui.diff = null, { ok: true, msg: `Annulé : retour à r${AF.position() + 1}.` }) : { err: "Rien à annuler : la révision affichée n'a pas de parente." }) },
    { nom: 'retablir', aide: 'refait ce qui a été annulé (Maj+U)', run: () => (ui.special ? { err: 'Quitte d\'abord le cas particulier (Échap).' } : AF.retablir() ? (ui.diff = null, { ok: true, msg: `Rétabli : r${AF.position() + 1}.` }) : { err: 'Rien à rétablir.' }) },
    { nom: 'diff', arg: '[a] [b]', opt: true, aide: 'compare deux révisions (par défaut : parente → affichée)', valeurs: (c) => { const s = diffSel(c); const L = s ? [{ arg: '', desc: `par défaut : r${s.a + 1} → r${s.b + 1}` }] : []; c.hist.forEach((r, i) => { if (i !== c.pos) L.push({ arg: `${i + 1} ${c.pos + 1}`, desc: `r${i + 1} → r${c.pos + 1} · ${r.motif}` }); }); return L; }, run: cmdDiff },
    { nom: 'aller', arg: '<n>', aide: 'relit la révision n (archive, lecture seule)', valeurs: valsRev, run: cmdAller },
    { nom: 'restaurer', arg: '<n>', aide: "nouvelle révision identique à n ; rien n'est effacé", valeurs: valsRev, run: cmdRestaurer },
    { nom: 'fait', arg: '<F-n>', aide: "ouvre la preuve d'un fait", valeurs: (c) => ((c.d && c.d.faits) || []).map((f) => ({ arg: f.id, desc: f.libelle })), run: cmdFait },
    { nom: 'filtre', arg: '<texte>', aide: 'filtre le registre des faits (sans texte : efface)', opt: true, run: (a) => { ui.filtre = a; return { ok: true, msg: a ? `Registre filtré sur « ${a} »${AF.niveau() === 'essentiel' ? ' (visible en Approfondi)' : ''}.` : 'Filtre effacé.' }; } },
    { nom: 'relire', aide: 'relit la trace enregistrée des rôles (relecture)', run: cmdRelire },
    { nom: 'etats', arg: '<normal|chargement|erreur|reprise>', aide: 'états de démonstration', valeurs: valsLibres([['normal', 'dossier normal'], ['chargement', 'relecture des étapes, volets en attente'], ['erreur', 'échec simulé du Sceptique'], ['reprise', 'reprise à partir du Sceptique']]), run: cmdEtats },
    { nom: 'theme', arg: '<sombre|clair>', opt: true, aide: 'thème (t)', valeurs: valsLibres([['sombre', 'fond noir, ambre'], ['clair', 'fond papier, ambre brun']]), run: cmdTheme },
    { nom: 'retour', aide: 'quitte le cas particulier (Échap)', run: () => (ui.special ? (ui.special = null, { ok: true, msg: `Retour à la révision r${AF.position() + 1}.` }) : { err: "Aucun cas particulier ouvert." }) },
    { nom: 'reinitialiser', arg: 'confirmer', aide: "efface tout l'historique et repart de Robert", valeurs: valsLibres([['confirmer', 'efface les révisions de ce navigateur (irréversible)']]), run: (a) => (norm(a) === 'confirmer' ? (AF.reinitialiser(), ui.special = null, ui.diff = null, { ok: true, msg: 'Historique effacé : r1 = demande de départ de Robert.' }) : { err: `Cette commande efface les ${pluriel(AF.historique().length, 'révision')}. Tape « reinitialiser confirmer ».` }) },
    { nom: 'aide', aide: 'raccourcis et commandes (?)', run: () => ({ ok: true, msg: 'Aide ouverte.', apres: ouvrirAide }) },
  ];
  const ALIAS = { etat: 'etats', lecture: 'niveau', situation: 'cas', comparer: 'diff', compare: 'diff', lire: 'aller', refaire: 'retablir', help: 'aide', '?': 'aide', ok: 'analyser', appliquer: 'analyser', annule: 'annuler', theme: 'theme', reset: 'reinitialiser' };
  function trouverCommande(t) {
    if (!t) return null;
    const n = ALIAS[t] || t;
    const ex = COMMANDES.find((k) => k.nom === n);
    if (ex) return ex;
    const pref = COMMANDES.filter((k) => k.nom.startsWith(n));
    return pref.length === 1 ? pref[0] : null;
  }
  function cmdMontant(a, c) {
    if (c.special) return { err: 'Commande indisponible dans un cas particulier : tape « retour » ou Échap.' };
    if (!a) return { incomplet: true };
    const p = AF.parametres(c.etat.cas).montant;
    let s = norm(a).replace(/[\s$\u00a0\u202f]/g, '').replace(/cad$/, '');
    const k = /k$/.test(s);
    s = s.replace(/k$/, '').replace(',', '.');
    const v = /^\d+(\.\d+)?$/.test(s) ? Math.round(parseFloat(s) * (k ? 1000 : 1)) : NaN;
    if (!p.includes(v)) return { err: `Montant inconnu : « ${a} » n'a pas été précalculé pour ${AF.nomCas(c.etat.cas)}. Valeurs possibles : ${p.map((m) => fmt.cad(m)).join(', ')}.` };
    return proposer({ montant: v });
  }
  function cmdRetrait(a, c) {
    if (c.special) return { err: 'Commande indisponible dans un cas particulier : tape « retour » ou Échap.' };
    const p = AF.parametres(c.etat.cas).retrait;
    if (p.length < 2) return { err: `Le retrait n'est pas un paramètre précalculé pour ${AF.nomCas(c.etat.cas)} : une seule valeur existe (${fmt.retrait(p[0])}).` };
    if (!a) return { incomplet: true };
    const n = norm(a);
    const v = ['na', 'n/a', 'non', 'np', 'aucun', 'inconnu', 'non precise', 'nonprecise', 'null'].includes(n) ? null : (/\d+/.test(n) ? parseInt(n.match(/\d+/)[0], 10) : undefined);
    if (v === undefined || !p.includes(v)) return { err: `Retrait inconnu : « ${a} ». Valeurs possibles : ${p.map((r) => `${r == null ? 'na' : r} (${fmt.retrait(r)})`).join(', ')}.` };
    return proposer({ retrait: v });
  }
  function cmdExclusion(a, c) {
    if (c.special) return { err: 'Commande indisponible dans un cas particulier : tape « retour » ou Échap.' };
    const p = AF.parametres(c.etat.cas).exclusion;
    if (p.length < 2) return { err: `L'exclusion de secteur n'est pas un paramètre précalculé pour ${AF.nomCas(c.etat.cas)} : seule valeur « ${p[0] ? 'oui' : 'non'} ».` };
    if (!a) return { incomplet: true };
    const n = norm(a);
    const v = ['oui', 'o', '1', 'vrai', 'true', 'avec'].includes(n) ? true : ['non', 'n', '0', 'faux', 'false', 'sans'].includes(n) ? false : undefined;
    if (v === undefined || !p.includes(v)) return { err: `Valeur inconnue : « ${a} ». Valeurs possibles : oui, non.` };
    return proposer({ exclusion: v });
  }
  function cmdCas(a, c) {
    if (!a) return { incomplet: true };
    const n = norm(a).replace(/[\s-]+/g, '_');
    const sp = Object.keys(SPECIAUX).find((k) => k === n || k.replace('_', '') === n.replace('_', ''));
    if (sp) { if (AF.perime()) AF.abandonner(); ui.special = sp; ui.selFait = null; ui.selRegle = null; return { ok: true, msg: `Cas particulier ouvert : ${SPECIAUX[sp]}. Lecture seule, hors révisions ; Échap pour revenir.` }; }
    const k = AF.cas().find((x) => x === n || norm(AF.nomCas(x)) === n);
    if (!k) return { err: `Situation inconnue : « ${a} ». Valeurs possibles : ${AF.cas().join(', ')}, ${Object.keys(SPECIAUX).join(', ')}.` };
    const avant = AF.historique().length;
    ui.special = null;
    AF.changerCas(k);
    ui.diff = null;
    return { ok: true, msg: AF.historique().length > avant ? `Autre situation : ${AF.nomCas(k)} (révision r${AF.position() + 1}).` : `${AF.nomCas(k)} est déjà la situation affichée.` };
  }
  function cmdNiveau(a, c) {
    const n = norm(a);
    const v = !n ? (c.niveau === 'essentiel' ? 'approfondi' : 'essentiel') : 'essentiel'.startsWith(n) ? 'essentiel' : 'approfondi'.startsWith(n) ? 'approfondi' : null;
    if (!v) return { err: `Niveau inconnu : « ${a} ». Valeurs possibles : essentiel, approfondi.` };
    AF.definirNiveau(v);
    return { ok: true, msg: `Lecture ${v === 'essentiel' ? 'Essentielle : registre et journal repliés' : 'Approfondie : densité complète'}. Mêmes faits.` };
  }
  function cmdDiff(a, c) {
    const n = c.hist.length;
    if (n < 2) return { err: 'Une seule révision : rien à comparer. Crée un aperçu (montant, retrait…) puis analyse-le.' };
    const nums = (a.match(/\d+/g) || []).map((x) => parseInt(x, 10) - 1);
    if (nums.some((x) => x < 0 || x >= n)) return { err: `Révision inconnue. Révisions possibles : 1 à ${n}.` };
    if (!nums.length) ui.diff = null;
    else ui.diff = { a: nums[0], b: nums.length > 1 ? nums[1] : c.pos, n };
    const s = diffSel(ctx());
    if (etroit.matches) ui.onglet = 'd';
    return { ok: true, msg: `Diff r${s.a + 1} → r${s.b + 1} dans le volet D.`, apres: () => { if (!etroit.matches) $('#d-corps').focus(); } };
  }
  function cmdAller(a, c) {
    const n = c.hist.length;
    const i = parseInt(a, 10) - 1;
    if (!a) return { incomplet: true };
    if (!(i >= 0 && i < n)) return { err: `Révision inconnue : « ${a} ». Révisions possibles : 1 à ${n}.` };
    if (ui.special) { ui.special = null; if (i === c.pos) return { ok: true, msg: `Retour à r${i + 1}.` }; }
    if (i === c.pos && !AF.perime()) return { err: `r${i + 1} est déjà affichée.` };
    if (i === c.pos) { AF.abandonner(); return { ok: true, msg: `r${i + 1} : aperçu abandonné.` }; }
    AF.allerA(i);
    ui.diff = null;
    return { ok: true, msg: i === n - 1 ? `r${i + 1} : révision courante.` : `r${i + 1} relue en archive (lecture seule). « restaurer ${i + 1} » en fait une nouvelle révision.` };
  }
  function cmdRestaurer(a, c) {
    const n = c.hist.length;
    const i = parseInt(a, 10) - 1;
    if (!a) return { incomplet: true };
    if (!(i >= 0 && i < n)) return { err: `Révision inconnue : « ${a} ». Révisions possibles : 1 à ${n}.` };
    ui.special = null;
    AF.restaurer(i);
    ui.diff = { a: n - 1, b: n, n: n + 1 };
    return { ok: true, msg: `r${n + 1} créée, identique à r${i + 1} ; r${n} est conservée. Diff r${n} → r${n + 1} dans le volet D.` };
  }
  function cmdFait(a, c) {
    if (!a) return { incomplet: true };
    const m = String(a).match(/\d+/);
    const id = m ? `F-${parseInt(m[0], 10)}` : '';
    if (!c.d || !AF.fait(id, c.d)) return { err: `Fait inconnu : « ${a} ». Ce dossier contient ${c.d && (c.d.faits || []).length ? `F-1 à F-${(c.d.faits || []).length}` : 'aucun fait'}.` };
    return { ok: true, msg: `Preuve de ${id}.`, apres: () => ouvrirFait(id) };
  }
  function arreterRelecture() { if (ui.relStop) { ui.relStop(); ui.relStop = null; } ui.relecture = null; }
  function cmdRelire(a, c) {
    if (ui.relecture && ui.demo === 'normal') { arreterRelecture(); return { ok: true, msg: 'Relecture arrêtée.' }; }
    const tr = (c.d && c.d.trace) || [];
    if (!tr.length) return { err: "Rien à relire : ce dossier n'a pas d'étapes enregistrées." };
    arreterRelecture();
    if (AF.niveau() === 'essentiel' && !etroit.matches) AF.definirNiveau('approfondi');
    ui.relecture = { i: 0, phase: 'en_cours' };
    ui.relStop = AF.relireTrace(c.d, (i, phase) => {
      if (phase === 'fin') { ui.relecture = null; ui.relStop = null; message(`Relecture terminée : ${pluriel(tr.length, 'étape')} enregistrées, durées hors ligne.`, 'ok'); render(); return; }
      ui.relecture = { i, phase };
      render();
    });
    if (etroit.matches) ui.onglet = 'c';
    return { ok: true, msg: 'Relecture des étapes enregistrées (pas un agent en direct). Volet C.' };
  }
  function cmdEtats(a) {
    const v = ['normal', 'chargement', 'erreur', 'reprise'].find((x) => x === norm(a));
    if (!v) return { err: `État inconnu : « ${a} ». Valeurs possibles : normal, chargement, erreur, reprise.` };
    definirDemo(v);
    return { ok: true, msg: v === 'normal' ? 'État normal.' : `Démonstration : ${v}.` };
  }
  function cmdTheme(a) {
    const n = norm(a);
    const v = !n ? (ui.theme === 'sombre' ? 'clair' : 'sombre') : ['sombre', 'clair'].find((x) => x.startsWith(n));
    if (!v) return { err: `Thème inconnu : « ${a} ». Valeurs possibles : sombre, clair.` };
    ui.theme = v;
    ecrireP('theme', v);
    document.documentElement.dataset.theme = v;
    requestAnimationFrame(dessiner);
    return { ok: true, msg: `Thème ${v}.` };
  }
  function definirDemo(v) {
    if (ui.demoStop) { ui.demoStop(); ui.demoStop = null; }
    arreterRelecture();
    ui.demo = v;
    ui.demoEtape = null;
    const d = ctx().d;
    const tr = (d && d.trace) || [];
    if ((v === 'chargement' || v === 'reprise') && tr.length) {
      const off = v === 'reprise' ? Math.min(3, tr.length - 1) : 0;
      ui.relecture = { i: off, phase: 'en_cours' };
      ui.demoEtape = `étape ${off + 1}/${tr.length} : ${tr[off].agent}`;
      ui.demoStop = AF.relireTrace({ trace: tr.slice(off) }, (i, phase) => {
        if (phase === 'fin') { ui.relecture = null; ui.demoStop = null; ui.demo = 'normal'; ui.demoEtape = null; message(`${v === 'chargement' ? 'Chargement terminé' : 'Reprise terminée'} (démonstration) : étapes enregistrées relues.`, 'ok'); render(); return; }
        ui.relecture = { i: i + off, phase };
        ui.demoEtape = `étape ${i + off + 1}/${tr.length} : ${tr[i + off].agent}`;
        render();
      });
    } else if (v === 'chargement' || v === 'reprise') {
      ui.demo = 'normal';
      message("Rien à relire : ce dossier n'a pas d'étapes enregistrées.", 'err');
    }
  }
  function executer(texte) {
    const brut = String(texte || '').trim();
    if (!brut) return { incomplet: true };
    const sp = brut.search(/\s/);
    const tete = norm(sp < 0 ? brut : brut.slice(0, sp));
    const arg = sp < 0 ? '' : brut.slice(sp + 1).trim();
    const cmd = trouverCommande(tete);
    if (!cmd) {
      const amb = COMMANDES.filter((k) => k.nom.startsWith(tete)).map((k) => k.nom);
      return { err: amb.length ? `Commande ambiguë : « ${tete} » peut être ${amb.join(', ')}.` : `Commande inconnue : « ${tete} ». Commandes : ${COMMANDES.map((k) => k.nom).join(', ')}.` };
    }
    const r = cmd.run(arg, ctx()) || {};
    if (r.ok) { message(r.msg || '', 'ok'); render(); }
    return r;
  }
  function lancer(texte) {
    const r = executer(texte);
    if (r.err) { message(r.err, 'err'); render(); }
    else if (r.incomplet) ouvrirPalette(`${(trouverCommande(norm(texte.split(/\s/)[0])) || {}).nom || ''} `);
    if (r.apres) r.apres();
    return r;
  }

  /* ---------- palette (dialog) ---------- */
  const pal = $('#palette'), palIn = $('#pal-saisie'), palListe = $('#pal-liste'), palMsg = $('#pal-msg');
  let palSugg = [], palActif = 0, palNav = false;
  function suggestions(txt) {
    const c = ctx();
    const brut = txt.replace(/^\s+/, '');
    const sp = brut.search(/\s/);
    if (sp >= 0) {
      const cmd = trouverCommande(norm(brut.slice(0, sp)));
      if (!cmd) return [];
      const a = norm(brut.slice(sp + 1));
      const a2 = a.replace(/[\s$]/g, '');
      return (cmd.valeurs ? cmd.valeurs(c) : [])
        .filter((v) => !a || norm(v.arg).replace(/\s/g, '').startsWith(a2) || norm(v.desc).includes(a))
        .slice(0, 60).map((v) => ({ cmd: `${cmd.nom}${v.arg ? ' ' + v.arg : ''}`, desc: v.desc, actuel: v.actuel }));
    }
    const n = norm(brut);
    const prio = [];
    if (c.statut === 'apercu') prio.push('analyser', 'abandonner');
    if (c.special) prio.push('retour');
    const L = COMMANDES.filter((k) => !n || k.nom.startsWith(n) || Object.keys(ALIAS).some((al) => ALIAS[al] === k.nom && al.startsWith(n)) || (n.length > 2 && norm(k.aide).includes(n)));
    L.sort((x, y) => (prio.includes(y.nom) ? 1 : 0) - (prio.includes(x.nom) ? 1 : 0));
    return L.map((k) => ({ cmd: k.arg && !k.opt ? `${k.nom} ` : k.nom, label: `${k.nom}${k.arg ? ' ' + k.arg : ''}`, desc: k.aide, partiel: !!k.arg && !k.opt }));
  }
  function majPalette() {
    palSugg = suggestions(palIn.value);
    if (palActif >= palSugg.length) palActif = 0;
    palListe.innerHTML = palSugg.length
      ? palSugg.map((s, i) => `<li role="option" id="pal-o-${i}" data-i="${i}" aria-selected="${i === palActif}" class="${s.actuel ? 'actuel' : ''}"><span class="o-cmd">${esc(s.label || s.cmd)}</span><span class="o-desc">${esc(s.desc || '')}${s.actuel ? ' · valeur affichée' : ''}</span></li>`).join('')
      : '<li class="o-vide" role="presentation">Aucune suggestion : ⏎ pour exécuter tel quel, ou « aide ».</li>';
    if (palSugg.length) palIn.setAttribute('aria-activedescendant', `pal-o-${palActif}`); else palIn.removeAttribute('aria-activedescendant');
    const a = $(`#pal-o-${palActif}`);
    if (a) a.scrollIntoView({ block: 'nearest' });
  }
  function grosBoutons() {
    const c = ctx();
    const grp = (t, items) => `<fieldset class="gros-g"><legend>${esc(t)}</legend>${items.map(([cmd, lab, etat]) => `<button type="button" class="gros${etat === 'fort' ? ' b-fort' : ''}" data-cmd="${esc(cmd)}"${etat === 'actuel' ? ' aria-current="true"' : ''}>${esc(lab)}${etat === 'actuel' ? ' ✓' : ''}</button>`).join('')}</fieldset>`;
    const g = [];
    if (c.statut === 'apercu') g.push(grp('Aperçu en attente', [['analyser', '⏎ Analyser', 'fort'], ['abandonner', 'Abandonner']]));
    if (c.special) g.push(grp('Cas particulier', [['retour', `Retour à r${c.pos + 1}`, 'fort']]));
    else {
      const p = AF.parametres(c.etat.cas);
      const b = c.brouillon || c.etat;
      g.push(grp('Montant', p.montant.map((m) => [`montant ${m}`, fmt.cad(m), m === b.montant ? 'actuel' : ''])));
      if (p.retrait.length > 1) g.push(grp('Retrait prévu', p.retrait.map((r) => [`retrait ${r == null ? 'na' : r}`, fmt.retrait(r), r === b.retrait ? 'actuel' : ''])));
      if (p.exclusion.length > 1) g.push(grp('Exclusion du secteur Énergie', p.exclusion.map((x) => [`exclusion ${x ? 'oui' : 'non'}`, x ? 'oui' : 'non', x === b.exclusion ? 'actuel' : ''])));
    }
    g.push(grp('Situation', [...AF.cas().map((k) => [`cas ${k}`, AF.nomCas(k), !c.special && c.etat.cas === k ? 'actuel' : '']), ...Object.entries(SPECIAUX).map(([k, l]) => [`cas ${k}`, l, c.special === k ? 'actuel' : ''])]));
    g.push(grp('Historique', [['annuler', 'Annuler'], ['retablir', 'Rétablir'], ['diff', 'Diff parente → affichée'], ['relire', 'Relire la trace']]));
    g.push(grp('Lecture', [['niveau essentiel', 'Essentiel', c.niveau === 'essentiel' ? 'actuel' : ''], ['niveau approfondi', 'Approfondi', c.niveau === 'approfondi' ? 'actuel' : '']]));
    g.push(grp('États de démonstration', ['normal', 'chargement', 'erreur', 'reprise'].map((v) => [`etats ${v}`, v, ui.demo === v ? 'actuel' : ''])));
    g.push(grp('Autres', [['theme', `Thème (${ui.theme})`], ['aide', 'Aide']]));
    $('#pal-gros').innerHTML = g.join('');
  }
  function ouvrirPalette(pre = '') {
    if (!pal.open) lastFocus = document.activeElement;
    palIn.value = pre;
    palMsg.textContent = '';
    palActif = 0;
    palNav = false;
    majPalette();
    grosBoutons();
    if (!pal.open) pal.showModal();
    palIn.focus();
    palIn.setSelectionRange(palIn.value.length, palIn.value.length);
  }
  function choisirSuggestion(s) {
    if (s.partiel) { palIn.value = s.cmd; palActif = 0; palNav = false; palMsg.textContent = ''; majPalette(); palIn.focus(); return; }
    validerPalette(s.cmd);
  }
  function validerPalette(texte) {
    const r = executer(texte);
    if (r.incomplet) {
      const cmd = trouverCommande(norm(String(texte).trim().split(/\s/)[0]));
      palIn.value = cmd ? `${cmd.nom} ` : String(texte);
      palActif = 0; palNav = false;
      majPalette();
      palMsg.textContent = cmd ? `« ${cmd.nom} » attend une valeur : choisis-la dans la liste.` : '';
      return;
    }
    if (r.err) { palMsg.textContent = r.err; message(r.err, 'err'); renderCmd(ctx()); return; }
    pal.close();
    if (r.apres) r.apres();
  }
  palIn.addEventListener('input', () => { palNav = false; palActif = 0; palMsg.textContent = ''; majPalette(); });
  palIn.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (!palSugg.length) return;
      palActif = (palActif + (e.key === 'ArrowDown' ? 1 : -1) + palSugg.length) % palSugg.length;
      palNav = true;
      majPalette();
    } else if (e.key === 'Tab' && !e.shiftKey && palSugg.length && palIn.value.trim() !== palSugg[palActif].cmd.trim()) {
      e.preventDefault();
      palIn.value = palSugg[palActif].cmd;
      palActif = 0; palNav = false;
      majPalette();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (palNav && palSugg[palActif]) choisirSuggestion(palSugg[palActif]);
      else if (!palIn.value.trim() && palSugg[0]) choisirSuggestion(palSugg[0]);
      else validerPalette(palIn.value);
    }
  });
  palListe.addEventListener('click', (e) => { const li = e.target.closest('[role="option"]'); if (li) choisirSuggestion(palSugg[+li.dataset.i]); });
  $('#pal-gros').addEventListener('click', (e) => { const b = e.target.closest('[data-cmd]'); if (b) validerPalette(b.dataset.cmd); });

  function ouvrirAide() {
    const T = [['<kbd>/</kbd> ou <kbd>Ctrl</kbd>/<kbd>⌘</kbd> <kbd>K</kbd>', 'palette de commandes'], ['<kbd>⏎</kbd> (hors champ) ou <kbd>Ctrl</kbd>/<kbd>⌘</kbd> <kbd>⏎</kbd>', "analyser l'aperçu"], ['<kbd>Échap</kbd>', "fermer · abandonner l'aperçu · quitter un cas particulier · réduire"], ['<kbd>u</kbd> · <kbd>Maj</kbd> <kbd>U</kbd>', 'annuler · rétablir (aussi <kbd>Ctrl</kbd>/<kbd>⌘</kbd> <kbd>Z</kbd>)'], ['<kbd>n</kbd>', 'Essentiel ↔ Approfondi'], ['<kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> <kbd>4</kbd>', 'volets A, B, C, D (onglets sur mobile)'], ['<kbd>z</kbd>', 'agrandir ou réduire le volet actif'], ['<kbd>f</kbd>', 'filtre du registre'], ['<kbd>j</kbd> <kbd>k</kbd> · <kbd>↓</kbd> <kbd>↑</kbd> sur un fait', 'fait suivant · précédent'], ['<kbd>←</kbd> <kbd>→</kbd> sur la courbe', 'semaine précédente · suivante (<kbd>Maj</kbd> : 13 semaines)'], ['<kbd>t</kbd>', 'thème sombre ou clair'], ['<kbd>?</kbd>', 'cette aide']];
    $('#aide-corps').innerHTML = `<table class="t t-aide"><caption class="sr">Raccourcis clavier</caption><tbody>${T.map(([k, d]) => `<tr><th scope="row">${k}</th><td>${d}</td></tr>`).join('')}</tbody></table>
      <h3 class="st">Commandes</h3><table class="t t-aide"><caption class="sr">Commandes de la palette</caption><tbody>${COMMANDES.map((k) => `<tr><th scope="row"><code>${esc(k.nom)}${k.arg ? ' ' + esc(k.arg) : ''}</code></th><td>${esc(k.aide)}</td></tr>`).join('')}</tbody></table>
      <p class="petit">Exemples : <code>montant 38000</code> · <code>retrait na</code> · <code>exclusion non</code> · <code>cas mateo</code> · <code>diff 1 3</code> · <code>aller 2</code> · <code>restaurer 1</code> · <code>etats erreur</code>.</p>
      <h3 class="st">Non réalisé dans ce prototype</h3><ul class="petit"><li>Modifier l'horizon, l'épargne, les placements ou le texte de la demande : seuls montant, retrait (Robert) et exclusion (Mateo) sont précalculés.</li><li>Choisir un autre actif ; répondre aux questions autrement que par ces paramètres.</li><li>Analyse en direct : « analyser » lit un dossier précalculé par le moteur réel ; « relire » rejoue des durées enregistrées.</li><li>Exporter ou copier le diff.</li></ul>`;
    const dlg = $('#aide');
    if (!dlg.open) { lastFocus = document.activeElement; dlg.showModal(); }
  }
  /* À la fermeture, le navigateur rend déjà le focus ; on ne le reprend que s'il est tombé sur la page (élément redessiné entre-temps). */
  $$('dialog').forEach((dlg) => {
    dlg.addEventListener('close', () => {
      if ($$('dialog').some((x) => x.open)) return;
      const a = document.activeElement;
      if (a && a !== document.body) return;
      const k = lastFocus && lastFocus.dataset ? lastFocus.dataset.k : null;
      const cible = lastFocus && document.contains(lastFocus) ? lastFocus : k ? document.querySelector(`[data-k="${CSS.escape(k)}"]`) : null;
      if (cible) cible.focus({ preventScroll: true });
    });
    dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
  });

  /* ---------- actions (clic, toucher) ---------- */
  function basculerZoom(v) { ui.zoom = v && ui.zoom !== v ? v : null; render(); requestAnimationFrame(dessiner); }
  const ACTIONS = {
    fait: (b) => ouvrirFait(b.dataset.id),
    faitRev: (b) => ouvrirFaitRev(+b.dataset.i, b.dataset.id),
    regle: (b) => { const code = b.dataset.code; ui.selRegle = ui.selRegle === code ? null : code; if (!ui.selRegle) ui.liesSeuls = false; if (b.closest('dialog')) b.closest('dialog').close(); render(); },
    trier: (b) => { const k = b.dataset.cle; ui.tri = { cle: k, sens: ui.tri.cle === k ? -ui.tri.sens : 1 }; ecrireP('tri', ui.tri); render(); },
    type: (b) => { const t = b.dataset.v; if (ui.types.has(t)) ui.types.delete(t); else ui.types.add(t); render(); },
    origine: (b) => { ui.origine = ui.origine === b.dataset.v ? 'tous' : b.dataset.v; render(); },
    lies: () => { ui.liesSeuls = !ui.liesSeuls; render(); },
    effacerRegle: () => { ui.selRegle = null; ui.liesSeuls = false; render(); },
    effacerFiltres: () => { ui.filtre = ''; ui.types.clear(); ui.origine = 'tous'; ui.liesSeuls = false; render(); },
    proposer: (b) => { const r = proposer(JSON.parse(b.dataset.patch)); message(r.err || r.msg, r.err ? 'err' : 'ok'); render(); },
    analyser: () => lancer('analyser'),
    abandonner: () => lancer('abandonner'),
    annuler: () => lancer('annuler'),
    retablir: () => lancer('retablir'),
    aller: (b) => lancer(`aller ${+b.dataset.i + 1}`),
    restaurer: (b) => lancer(`restaurer ${+b.dataset.i + 1}`),
    diffA: (b) => { const c = ctx(); const s = diffSel(c); ui.diff = { a: +b.dataset.i, b: s ? s.b : c.pos, n: c.hist.length }; render(); },
    diffB: (b) => { const c = ctx(); const s = diffSel(c); ui.diff = { a: s ? s.a : 0, b: +b.dataset.i, n: c.hist.length }; render(); },
    diffDefaut: () => { ui.diff = null; render(); },
    contexte: () => { ui.contexte = !ui.contexte; ecrireP('contexte', ui.contexte); render(); },
    cas: (b) => lancer(`cas ${b.dataset.cas}`),
    retour: () => lancer('retour'),
    niveau: (b) => lancer(`niveau ${b.dataset.n}`),
    theme: () => lancer('theme'),
    palette: (b) => ouvrirPalette(b.dataset.pre || ''),
    aide: () => ouvrirAide(),
    'fermer-dlg': (b) => b.closest('dialog').close(),
    onglet: (b) => { ui.onglet = b.dataset.o; render(); },
    zoom: (b) => basculerZoom(b.dataset.v),
    etape: (b) => { const i = +b.dataset.i; ui.etapeOuverte = ui.etapeOuverte === i ? null : i; render(); },
    relire: () => lancer('relire'),
    reprendre: () => lancer('etats reprise'),
    fenetre: (b) => { const i = +b.dataset.i; ui.fenetre = ui.fenetre === i ? null : i; ui.curseur = null; majCurseur(); },
  };
  document.addEventListener('click', (e) => {
    const b = e.target.closest('[data-act]');
    if (!b || b.disabled) return;
    const f = ACTIONS[b.dataset.act];
    if (f) { e.preventDefault(); f(b, e); }
  });
  document.addEventListener('change', (e) => {
    const t = e.target;
    if (t.id === 'demo') lancer(`etats ${t.value}`);
    else if (t.id === 'etat-special') lancer(t.value ? `cas ${t.value}` : 'retour');
    else if (t.dataset.chg === 'diffA' || t.dataset.chg === 'diffB') {
      const c = ctx(); const s = diffSel(c) || { a: 0, b: c.pos };
      ui.diff = { a: t.dataset.chg === 'diffA' ? +t.value : s.a, b: t.dataset.chg === 'diffB' ? +t.value : s.b, n: c.hist.length };
      render();
    }
  });
  document.addEventListener('toggle', (e) => {
    const s = e.target;
    if (s.tagName === 'DETAILS' && s.dataset.sec) { ui.ouverts[s.dataset.sec] = s.open; ecrireP('ouverts', ui.ouverts); }
  }, true);
  $('#b-filtre').addEventListener('input', (e) => { ui.filtre = e.target.value; renderB(ctx()); });
  $('#b-filtre').addEventListener('keydown', (e) => { if (e.key === 'Escape' && e.target.value) { e.preventDefault(); e.stopPropagation(); ui.filtre = ''; e.target.value = ''; renderB(ctx()); } else if (e.key === 'ArrowDown' || e.key === 'Enter') { e.preventDefault(); deplacerFait(0); } });
  /* Courbe : pointeur et clavier. */
  const zoneCourbe = $('#s-courbe');
  zoneCourbe.addEventListener('pointermove', (e) => { if (e.target.id === 'courbe' && e.pointerType === 'mouse') curseurDepuisX(e.clientX); });
  zoneCourbe.addEventListener('pointerdown', (e) => { if (e.target.id === 'courbe') curseurDepuisX(e.clientX); });
  zoneCourbe.addEventListener('keydown', (e) => {
    if (e.target.id !== 'courbe' || !courbe) return;
    const n = courbe.av.length;
    const pas = e.shiftKey ? 13 : 1;
    let i = ui.curseur;
    if (e.key === 'ArrowRight') i = i == null ? 0 : Math.min(n - 1, i + pas);
    else if (e.key === 'ArrowLeft') i = i == null ? n - 1 : Math.max(0, i - pas);
    else if (e.key === 'Home') i = 0;
    else if (e.key === 'End') i = n - 1;
    else if (e.key === 'Escape' && (ui.curseur != null || ui.fenetre != null)) { e.preventDefault(); e.stopPropagation(); ui.curseur = null; ui.fenetre = null; majCurseur(); return; } else return;
    e.preventDefault();
    ui.curseur = i;
    ui.fenetre = null;
    majCurseur();
  });
  /* Registre : ↑ ↓ d'un fait à l'autre. */
  $('#b-corps').addEventListener('keydown', (e) => {
    if (!e.target.classList.contains('fid')) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); deplacerFait(e.key === 'ArrowDown' ? 1 : -1); }
  });
  if (window.ResizeObserver) new ResizeObserver(() => requestAnimationFrame(dessiner)).observe(zoneCourbe);
  etroit.addEventListener('change', () => { render(); });

  /* ---------- clavier global ---------- */
  const PANNEAUX = { 1: 'a', 2: 'b', 3: 'c', 4: 'd' };
  function focusVolet(v) {
    if (etroit.matches) { ui.onglet = v; render(); window.scrollTo(0, 0); }
    if (ui.zoom && ui.zoom !== v) { ui.zoom = null; render(); }
    const replie = AF.niveau() === 'essentiel' && (v === 'b' || v === 'c') && !etroit.matches;
    const el = replie ? $(`#${v}-rail .rail-btn`) : $(`#${v}-corps`);
    if (el) el.focus();
  }
  function echap() {
    if (ui.demo !== 'normal') { definirDemo('normal'); message('Démonstration arrêtée : état normal.', 'ok'); render(); return; }
    if (AF.perime()) { lancer('abandonner'); return; }
    if (ui.special) { lancer('retour'); return; }
    if (ui.zoom) { basculerZoom(null); return; }
    if (ui.curseur != null || ui.fenetre != null) { ui.curseur = null; ui.fenetre = null; majCurseur(); return; }
    if (ui.selRegle || ui.selFait) { ui.selRegle = null; ui.selFait = null; ui.liesSeuls = false; render(); }
  }
  document.addEventListener('keydown', (e) => {
    if ($$('dialog').some((d) => d.open)) return;
    const t = e.target;
    const mod = e.metaKey || e.ctrlKey;
    const k = e.key;
    if (mod && !e.altKey && k.toLowerCase() === 'k') { e.preventDefault(); ouvrirPalette(); return; }
    if (mod && k === 'Enter') { e.preventDefault(); if (AF.perime()) lancer('analyser'); return; }
    const saisie = t.matches && t.matches('input, textarea, select, [contenteditable="true"]');
    if (saisie) return;
    if (mod && !e.altKey && k.toLowerCase() === 'z') { e.preventDefault(); lancer(e.shiftKey ? 'retablir' : 'annuler'); return; }
    if (mod || e.altKey) return;
    if (k === '/') { e.preventDefault(); ouvrirPalette(); return; }
    if (k === '?') { e.preventDefault(); ouvrirAide(); return; }
    if (k === 'Escape') { echap(); return; }
    if (k === 'Enter') {
      if (AF.perime() && !(t.closest && t.closest('button, a, summary, [role="slider"], [role="option"]'))) { e.preventDefault(); lancer('analyser'); }
      return;
    }
    if (t.id === 'courbe' && (k === 'ArrowLeft' || k === 'ArrowRight')) return;
    switch (k) {
      case 'u': e.preventDefault(); lancer('annuler'); break;
      case 'U': e.preventDefault(); lancer('retablir'); break;
      case 'n': e.preventDefault(); lancer('niveau'); break;
      case 't': e.preventDefault(); lancer('theme'); break;
      case 'z': { e.preventDefault(); const v = t.closest && t.closest('.volet'); basculerZoom(v ? v.id.replace('volet-', '') : 'd'); break; }
      case 'f': e.preventDefault(); if (AF.niveau() === 'approfondi' && !etroit.matches) $('#b-filtre').focus(); else ouvrirPalette('filtre '); break;
      case 'j': if (AF.niveau() === 'approfondi') { e.preventDefault(); deplacerFait(1); } break;
      case 'k': if (AF.niveau() === 'approfondi') { e.preventDefault(); deplacerFait(-1); } break;
      default:
        if (PANNEAUX[k]) { e.preventDefault(); focusVolet(PANNEAUX[k]); }
    }
  });

  /* ---------- démarrage ---------- */
  document.documentElement.dataset.theme = ui.theme;
  AF.abonner(render);
  render();
})();
