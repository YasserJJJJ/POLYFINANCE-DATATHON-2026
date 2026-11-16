/* Carnet — prototype 1 de ui-adam (Second avis).
   Une seule page de lecture. La phrase du titre est l'interface : le montant et le retrait (ou l'exclusion)
   se corrigent sur place, comme sur une épreuve. Chaque chiffre du texte porte un appel de note ; la note,
   dans la marge, donne la valeur exacte, le type, la source, la méthode et les références.
   Rien n'est calculé ici : chiffres, sources, étapes et verdicts viennent de window.AF (socle commun). */
(() => {
  'use strict';
  const AF = window.AF;
  if (!AF) return;
  const F = AF.donnees;
  const SVG = 'http://www.w3.org/2000/svg';

  /* ------------------------------------------------------------------ Outils DOM */
  function poser(el, attrs) {
    if (!attrs) return;
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v);
      else if (k === 'text') el.textContent = v;
      else el.setAttribute(k, v === true ? '' : String(v));
    }
  }
  function remplir(el, enfants) {
    for (const c of enfants.flat(Infinity)) {
      if (c == null || c === false || c === '') continue;
      el.append(c instanceof Node ? c : document.createTextNode(String(c)));
    }
    return el;
  }
  const h = (tag, attrs, ...enfants) => { const el = document.createElement(tag); poser(el, attrs); return remplir(el, enfants); };
  const s = (tag, attrs, ...enfants) => { const el = document.createElementNS(SVG, tag); poser(el, attrs); return remplir(el, enfants); };
  const $ = (sel, r = document) => r.querySelector(sel);
  const reduit = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const approfondi = () => AF.niveau() === 'approfondi';
  const T = (essentiel, profond) => (approfondi() ? profond : essentiel);

  /* ------------------------------------------------------------------ Typographie des nombres (affichage seulement) */
  const moins = (t) => String(t).replace(/(^|[\s(«\u00a0\u202f])-(?=\d)/g, '$1\u2212');
  const espaces = (t) => String(t).replace(/(\d) (\$|%|pts?\b)/g, '$1\u00a0$2');
  const pluriels = (t) => String(t)
    .replace(/(\d+(?:,\d+)?)\s?an\(s\)/g, (m, n) => `${n}\u00a0${parseFloat(n.replace(',', '.')) >= 2 ? 'ans' : 'an'}`)
    .replace(/(\d+(?:,\d+)?)\s?point\(s\)/g, (m, n) => `${n}\u00a0${parseFloat(n.replace(',', '.')) >= 2 ? 'points' : 'point'}`);
  const typo = (t) => espaces(moins(pluriels(t)));
  const fr = AF.fmt.nombre;
  const cad = (n) => typo(AF.fmt.cad(n));
  const pct = (n, d = 1) => typo(AF.fmt.pct(n, d));
  const pts = (n, d = 1) => typo(AF.fmt.pts(n, d));
  const exact = (v) => moins(Number(v).toLocaleString('fr-CA', { maximumFractionDigits: 6 }));
  const ordinal = (n) => (n === 1 ? '1re' : `${n}e`);
  const ord = (n) => [String(n), h('sup', null, n === 1 ? 're' : 'e')];
  const heure = (t) => new Date(t).toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' });
  const pl = (n) => (Math.abs(n) >= 2 ? 's' : '');

  /* ------------------------------------------------------------------ Vocabulaire */
  const SECTEURS = {
    Energy: 'Énergie', 'Crypto asset': 'Cryptoactifs', Financials: 'Finance', 'Information Technology': 'Technologies',
    'Consumer Discretionary': 'Consommation discrétionnaire', 'Health Care': 'Santé', Utilities: 'Services publics',
    Industrials: 'Industrie', 'Consumer Staples': 'Consommation de base', 'Communication Services': 'Communication',
  };
  const secteur = (x) => SECTEURS[x] || x;
  const SIGNE_REGLE = { ok: '✓', orange: '△', rouge: '✕', gris: '?', non_evaluee: '–' };
  const niveauRegle = (n) => (AF.NIVEAUX_REGLE[n] || n || '').toLowerCase();
  const NATURE = { donnee: 'donnée', preference: 'préférence', contrainte: 'contrainte', inconnu: 'inconnue' };
  const ROLES = { Profileur: 'modele', 'Contrôle données': 'code', Analyste: 'code', Sceptique: 'modele', Gardien: 'code', 'Rédacteur': 'modele' };
  const ISSUES = { confirmee: 'confirmée', ecartee: 'écartée', limite: 'limite notée' };
  const SENS = { aggrave: 'baisse plus profonde', ameliore: 'baisse moins profonde', neutre: 'baisse inchangée' };
  const CHAMP = { montant: 'le montant', retrait: 'le retrait prévu', exclusion: 'l’exclusion de secteur' };
  const ROMAINS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'];
  const DIRECTIONS = [{ d: '2-relief', nom: 'Relief' }, { d: '3-pupitre', nom: 'Pupitre' }, { d: '4-fil', nom: 'Fil' }, { d: '5-epure', nom: 'Épure' }];
  const SPECIAUX = [
    { cle: 'sans_epargne', nom: 'épargne inconnue' },
    { cle: 'impossible', nom: 'montant supérieur à l’épargne' },
    { cle: 'hors_univers', nom: 'placement hors univers' },
  ];
  const DEMOS = { normal: 'normal', chargement: 'chargement', erreur: 'erreur', reprise: 'reprise' };

  const actif = (t) => (F.actifs || []).find((a) => a.ticker === t) || null;
  const nomActif = (t) => (actif(t) ? actif(t).name : t || '—');
  const cleEtat = (e) => `m=${e.montant};r=${e.retrait == null ? 'na' : e.retrait};x=${e.exclusion ? 1 : 0}`;
  const exclusionsDeclarees = (cas) => {
    const c = F.cas[cas];
    return c ? ((c.variantes[c.depart].profil || {}).exclusions || []) : [];
  };

  /* ------------------------------------------------------------------ État d'interface (local à cette page) */
  const ui = {
    special: null, demo: 'normal', notesOuvertes: new Set(), focusApres: null,
    arret: null, graphes: [], observateur: null, precedent: null,
  };

  /* ------------------------------------------------------------------ Notes de marge
     Un bloc = un passage de texte et sa marge. Chaque appel enregistre sa note dans le bloc ;
     la marge du bloc liste ses notes, sans doublon. */
  let nBloc = 0;
  const SYMBOLES = ['*', '†', '‡', '§', '‖'];
  class Bloc {
    constructor(nom) { this.id = `b${++nBloc}-${nom}`; this.notes = new Map(); this.libres = 0; }
    appel(note) {
      let n = this.notes.get(note.cle);
      if (!n) {
        n = note;
        if (n.kind === 'libre') n.etiquette = SYMBOLES[this.libres++ % SYMBOLES.length];
        this.notes.set(n.cle, n);
      }
      const nid = `${this.id}-${n.cle}`;
      return h('a', { class: `appel ${n.kind}`, href: `#${nid}`, 'data-note': nid, 'aria-label': `Note ${n.etiquette} : ${n.lib}` }, n.etiquette);
    }
    /* Marge : sur grand écran, les notes sont ouvertes dans la marge ; sur petit écran, un seul repli
       « Notes de ce passage » sous le paragraphe. Un appel ouvre directement sa note. */
    marge(avant) {
      const m = h('div', { class: 'marge' });
      if (avant) remplir(m, [avant]);
      if (this.notes.size) {
        const g = h('details', { class: 'notes-groupe', id: `${this.id}-notes` },
          h('summary', null, h('span', { class: 'pc' }, 'Notes de ce passage'), ` (${this.notes.size})`, h('span', { class: 'n-plus', 'aria-hidden': 'true' })),
          h('p', { class: 'marge-titre', 'aria-hidden': 'true' }, `Notes (${this.notes.size})`));
        for (const [cle, n] of this.notes) g.append(rendreNote(n, `${this.id}-${cle}`));
        m.append(g);
      }
      return m;
    }
  }
  const libCourt = (l) => String(l || '').replace(/\s*\(hypothèse de l['’]équipe\)\s*$/i, '');
  const noteFait = (f, o = {}) => ({ kind: 'fait', cle: (o.prefixe || '') + f.id, etiquette: f.id.replace(/^F-/, '') + (o.prime || ''), lib: libCourt(f.libelle), fait: f, edition: o.edition });
  const noteProfil = (p) => ({ kind: 'profil', cle: `p-${p.cle}`, etiquette: 'p', lib: p.lib, profil: p });
  const noteLibre = (cle, texte, lib) => ({ kind: 'libre', cle: `x-${cle}`, etiquette: '*', lib: lib || 'Chiffre sans fait relié', texte });

  function signeType(type, avecTexte) {
    const lib = type === 'PROFIL' ? 'Donnée du profil' : type === 'LIBRE' ? 'Sans fait relié' : (AF.TYPES[type] || type);
    return [h('span', { class: `signe-type ${type}`, 'aria-hidden': 'true' }), avecTexte ? lib : h('span', { class: 'sr-only' }, `${lib} : `)];
  }

  function valeurExacte(f) {
    const v = f.valeur;
    const u = f.unite && f.unite !== 'fraction' ? ` ${f.unite}` : '';
    if (typeof v === 'number') return typo(exact(v) + u);
    if (Array.isArray(v)) return `${v.length} éléments, détaillés ci-dessous`;
    if (v && typeof v === 'object') {
      if ('debut' in v && 'fin' in v) return `${v.debut} → ${v.fin}${v.observations ? ` · ${fr(v.observations)} observations` : ''}`;
      return Object.entries(v).map(([k, x]) => `${k} ${typeof x === 'number' ? exact(x) : x}`).join(' · ') + (f.unite === 'fraction' ? ' (fractions)' : '');
    }
    return null;
  }

  const domaine = (u) => { try { return `${new URL(u).hostname.replace(/^www\./, '')} ↗`; } catch (e) { return u; } };
  function itemReference(r) {
    const li = h('li', null, `${r.auteurs}${r.annee ? ` (${r.annee})` : ''}. `, h('cite', null, r.titre), r.publication ? `. ${r.publication}.` : '.');
    if (r.lien) li.append(' ', h('a', { href: r.lien, target: '_blank', rel: 'noopener noreferrer' }, domaine(r.lien)));
    else li.append(' ', h('span', { class: 'vide' }, 'sans lien'));
    if (r.examen) li.append(h('span', { class: 'examen' }, `Examen : ${r.examen}`));
    if (approfondi() && r.apport) li.append(h('span', { class: 'examen' }, `Apport : ${r.apport}`));
    return li;
  }
  const listeReferences = (ids) => {
    const refs = (ids || []).map(AF.reference).filter(Boolean);
    return refs.length ? [h('p', null, h('span', { class: 'pc' }, `Références (${refs.length})`)), h('ol', { class: 'n-refs' }, refs.map(itemReference))] : [];
  };

  function rendreNote(n, nid) {
    const det = h('details', { class: `note ${n.kind}`, id: nid });
    const sum = h('summary', null, h('span', { class: 'n-num' }, n.etiquette));
    const corps = h('div', { class: 'n-corps' });
    if (n.kind === 'fait') {
      const f = n.fait, v = valeurExacte(f);
      remplir(sum, [h('span', { class: 'n-lib' }, signeType(f.type), n.lib), v ? h('span', { class: 'n-val' }, v) : null]);
      remplir(corps, [
        h('p', null, signeType(f.type, true), ` · ${f.lu_ou_calcule === 'lu' ? 'lu tel quel' : 'calculé'} · `, h('span', { class: 'id' }, f.id), n.edition ? ` · ${n.edition}` : ''),
        typeof f.valeur === 'string' ? h('p', null, typo(f.valeur)) : null,
        Array.isArray(f.valeur) ? h('ol', { class: 'n-refs' }, f.valeur.map((x) => h('li', null, typo(String(x))))) : null,
        h('p', null, h('span', { class: 'pc' }, 'Source '), f.source || '—'),
        h('p', { class: 'n-meth' }, h('span', { class: 'pc' }, 'Méthode '), typo(f.methode || '—')),
        listeReferences(f.references),
      ]);
    } else if (n.kind === 'profil') {
      const p = n.profil;
      remplir(sum, [h('span', { class: 'n-lib' }, signeType('PROFIL'), n.lib), h('span', { class: 'n-val' }, p.affiche)]);
      remplir(corps, [
        h('p', null, signeType('PROFIL', true), ` · ${p.type}`),
        h('p', null, h('span', { class: 'pc' }, 'Source '), p.src),
        p.detail ? h('p', null, typo(p.detail)) : null,
      ]);
    } else {
      remplir(sum, [h('span', { class: 'n-lib' }, signeType('LIBRE'), n.lib)]);
      remplir(corps, [h('p', null, signeType('LIBRE', true)), h('p', null, n.texte)]);
    }
    sum.append(h('span', { class: 'n-plus', 'aria-hidden': 'true' }));
    det.append(sum, corps);
    return det;
  }

  /* ------------------------------------------------------------------ Annotation : relier chaque chiffre du texte à son fait
     On lit les nombres du texte du produit et on cherche, par valeur et par unité, le fait qui les porte :
     d'abord parmi les faits que la phrase cite, puis parmi tous les faits du dossier, puis dans le profil.
     Un nombre avec unité qu'aucun fait ne porte reçoit une note « sans fait relié » : on ne l'invente pas. */
  const RE_NOMBRE = /\s?\(F-(\d+)\)|\bF-(\d+)\b|(-?\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?:,\d+)?|-?\d+(?:,\d+)?)((?:[ \u00a0\u202f])?(?:%\/an|%|\$|CAD|point\(s\)|points?\b|pts\b|an\(s\)|ans\b|an\b|\/100))?/g;
  function normUnite(t) {
    const x = String(t || '').trim();
    if (!x) return '';
    if (x === '%/an' || x === '%') return x;
    if (x === '$' || x === 'CAD') return '$';
    if (/^(point|pts)/.test(x)) return 'pts';
    if (/^an/.test(x)) return 'an';
    return x;
  }
  function uniteCompatible(u, fu) {
    if (u === '%' || u === '%/an') return fu === '%' || fu === '%/an';
    if (u === '$') return fu === '$';
    if (u === 'pts') return fu === 'points';
    if (u === 'an') return fu === 'an(s)';
    if (u === '') return fu === '';
    return false;
  }
  function chercherFait(v, dec, u, liste) {
    const tol = 0.5 * Math.pow(10, -dec) + 1e-9;
    for (const absolu of [false, true]) {
      if (absolu && u !== '$') break;
      for (const f of liste) {
        const x = f.valeur;
        if (typeof x === 'number') {
          if (uniteCompatible(u, f.unite) && Math.abs((absolu ? Math.abs(x) : x) - (absolu ? Math.abs(v) : v)) <= tol) return f;
        } else if (!absolu && x && typeof x === 'object' && !Array.isArray(x)) {
          for (const y of Object.values(x)) {
            if (typeof y !== 'number') continue;
            const z = f.unite === 'fraction' ? (u === '%' ? y * 100 : null) : (u === '' && f.unite === '' ? y : null);
            if (z != null && Math.abs(z - v) <= tol) return f;
          }
        }
      }
    }
    return null;
  }
  function candidatsProfil(ctx) {
    const d = ctx.d, p = d.profil || {}, ev = p.evaluation || {};
    const src = 'Profil du dossier : scénario fictif de l’équipe';
    const typeP = 'donnée du profil (fictive)';
    const liste = [
      { cle: 'epargne', v: p.epargne_totale_cad, u: '$', lib: 'Épargne totale', affiche: cad(p.epargne_totale_cad), src, type: typeP },
      { cle: 'preserver', v: p.somme_a_preserver_cad, u: '$', lib: 'Somme à ne jamais risquer', affiche: cad(p.somme_a_preserver_cad), src, type: typeP },
      { cle: 'retrait', v: p.retrait_prevu_ans, u: 'an', lib: 'Retrait prévu', affiche: typo(AF.fmt.retrait(p.retrait_prevu_ans)), src, type: typeP, indice: /retir|retrait/i },
      { cle: 'horizon', v: p.horizon_ans, u: 'an', lib: 'Horizon du placement', affiche: `${p.horizon_ans} ans`, src, type: typeP, indice: /horizon/i },
      { cle: 'tolerance', v: ev.tolerance, u: '/100', lib: 'Ce que tu dis vouloir risquer', affiche: `${fr(ev.tolerance)} / 100`, src: 'Évaluation du Profileur, d’après tes réponses', type: 'préférence déclarée', indice: /risquer|tolérance/i },
      { cle: 'capacite', v: ev.capacite, u: '/100', lib: 'Ce que ta situation permet', affiche: `${fr(ev.capacite)} / 100`, src: 'Évaluation du Profileur (barème de l’équipe)', type: 'donnée du profil', detail: (ev.capacite_raisons || []).join(' ; '), indice: /situation|capacit/i },
      { cle: 'poids', v: ev.poids_pct, u: '%', lib: 'Part de l’épargne dans ce placement', affiche: pct(ev.poids_pct, 0), src: 'Évaluation du Profileur : montant rapporté à l’épargne totale', type: 'donnée du profil' },
      { cle: 'montant', v: d.demande && d.demande.montant_cad, u: '$', lib: 'Montant de la demande', affiche: cad(d.demande && d.demande.montant_cad), src: 'Ta demande', type: 'paramètre de la demande' },
    ];
    for (const m of (ctx.params ? ctx.params.montant : [])) {
      liste.push({ cle: `m${m}`, v: m, u: '$', lib: 'Montant testé par le Gardien', affiche: cad(m), src: 'Variante précalculée par le moteur réel (paramètres de ce prototype)', type: 'paramètre précalculé' });
    }
    return liste.filter((c) => c.v != null);
  }
  function chercherProfil(v, dec, u, ctx, contexteAvant) {
    const tol = 0.5 * Math.pow(10, -dec) + 1e-9;
    const ok = candidatsProfil(ctx).filter((c) => c.u === u && Math.abs(c.v - v) <= tol);
    if (!ok.length) return null;
    return ok.find((c) => c.indice && c.indice.test(contexteAvant)) || ok.find((c) => !c.indice) || ok[0];
  }

  /* Rend un texte du produit en nœuds : nombres arrondis à l'écran (AF.propre) et appels de note.
     Les faits cités par la phrase mais absents du texte reçoivent un appel avant la ponctuation finale. */
  const virgule = () => h('span', { class: 'appel-sep', 'aria-hidden': 'true' }, ',');
  function annoter(texte, b, ctx, faitsPhrase, opts = {}) {
    const d = ctx.d, src = String(texte || '');
    const prioritaires = [...new Set(faitsPhrase || [])].map((id) => AF.fait(id, d)).filter(Boolean);
    const tous = d.faits || [];
    const jetons = [];
    let dernier = 0, m;
    RE_NOMBRE.lastIndex = 0;
    while ((m = RE_NOMBRE.exec(src))) {
      if (m.index > dernier) jetons.push({ texte: src.slice(dernier, m.index) });
      dernier = RE_NOMBRE.lastIndex;
      if (m[1] || m[2]) {
        const f = AF.fait(`F-${m[1] || m[2]}`, d);
        jetons.push(f ? { ref: f } : { texte: m[0] });
        continue;
      }
      const brut = m[3], uniteBrute = m[4] || '';
      const v = parseFloat(brut.replace(/[ \u00a0\u202f]/g, '').replace(',', '.'));
      const dec = (brut.split(',')[1] || '').length;
      const u = normUnite(uniteBrute);
      const annee = !u && !dec && Math.abs(v) >= 1900 && Math.abs(v) <= 2100;
      let note = null;
      if (!annee && !isNaN(v)) {
        const f = chercherFait(v, dec, u, prioritaires) || chercherFait(v, dec, u, tous);
        if (f) note = noteFait(f);
        else {
          const p = chercherProfil(v, dec, u, ctx, src.slice(Math.max(0, m.index - 70), m.index));
          if (p) note = noteProfil(p);
          else if (u && !opts.souple) note = noteLibre(`${String(v).replace(/[^\d]/g, '')}${u.replace(/[^a-z]/gi, '')}`, 'Ce chiffre figure dans le texte du produit, mais aucun fait F-n de ce dossier ne le porte directement. Il n’est ni recalculé ni remplacé ici : c’est une limite du texte, signalée telle quelle.');
        }
      }
      jetons.push(annee || (!note && !u) ? { texte: m[0] } : { nombre: typo(AF.propre(brut) + uniteBrute), note });
    }
    if (dernier < src.length) jetons.push({ texte: src.slice(dernier) });
    const parNombre = new Set(jetons.filter((j) => j.note && j.note.kind === 'fait').map((j) => j.note.fait.id));
    const utilises = new Set(parNombre);
    const out = [];
    const finitParAppel = () => {
      const x = out[out.length - 1];
      return x instanceof Element && (x.matches('a.appel') || !!(x.lastElementChild && x.lastElementChild.matches('a.appel')));
    };
    const appel = (note) => { if (finitParAppel()) out.push(virgule()); out.push(b.appel(note)); };
    for (const j of jetons) {
      if (j.ref) { if (!parNombre.has(j.ref.id)) { appel(noteFait(j.ref)); utilises.add(j.ref.id); } }
      else if (j.nombre) out.push(h('span', { class: 'nowrap' }, j.nombre, j.note ? b.appel(j.note) : null));
      else if (j.texte) out.push(j.texte);
    }
    const fin = opts.sansFin ? [] : prioritaires.filter((f) => !utilises.has(f.id));
    if (fin.length) {
      /* Appels des faits cités sans chiffre : avant la ponctuation finale, à la française. */
      let ponct = '';
      const last = out[out.length - 1];
      if (typeof last === 'string') {
        const p = /([.!?…]\s*)$/.exec(last);
        if (p) { ponct = p[1]; out[out.length - 1] = last.slice(0, p.index); if (!out[out.length - 1]) out.pop(); }
      }
      fin.forEach((f) => appel(noteFait(f)));
      if (ponct) out.push(ponct);
    }
    return out;
  }

  /* ------------------------------------------------------------------ Formes des verdicts (jamais la couleur seule) */
  function formeMini(etat) {
    const svg = s('svg', { viewBox: '0 0 16 16', 'aria-hidden': 'true', focusable: 'false' });
    if (etat === 'coherent') svg.append(s('circle', { class: 'trait', cx: 8, cy: 8, r: 6.4 }));
    else if (etat === 'ajustement') svg.append(s('polygon', { class: 'trait', points: '8,1.2 14.8,8 8,14.8 1.2,8' }));
    else if (etat === 'incoherent') svg.append(s('rect', { class: 'trait', x: 2, y: 2, width: 12, height: 12 }), s('rect', { class: 'trait', x: 5, y: 5, width: 6, height: 6, 'stroke-width': 1 }));
    else svg.append(s('circle', { class: 'trait', cx: 8, cy: 8, r: 6.4, 'stroke-dasharray': '2.2 2' }));
    return svg;
  }
  const etatMini = (etat) => h('span', { class: 'etat-mini' }, formeMini(etat), (AF.ETATS[etat] || {}).court || etat);

  let nTampon = 0;
  function tampon(d) {
    const v = d.verdict || { etat: 'indetermine', respectees: 0, evaluees: 0 };
    const E = AF.ETATS[v.etat] || AF.ETATS.indetermine;
    const fid = `encre-${++nTampon}`;
    const rot = { coherent: -2, ajustement: 1.5, incoherent: -3.5, indetermine: 0 }[v.etat] || 0;
    const svg = s('svg', { class: `tampon ${v.etat}`, viewBox: '0 0 240 150', role: 'img', 'aria-label': `Tampon du Gardien : ${E.long}.` });
    svg.append(s('defs', null, s('filter', { id: fid, x: '-4%', y: '-4%', width: '108%', height: '108%' },
      s('feTurbulence', { type: 'fractalNoise', baseFrequency: '1.3', numOctaves: '1', seed: '11', result: 'grain' }),
      s('feDisplacementMap', { in: 'SourceGraphic', in2: 'grain', scale: '1.8', xChannelSelector: 'R', yChannelSelector: 'G' }))));
    const g = s('g', { transform: `rotate(${rot} 120 75)`, filter: `url(#${fid})` });
    if (v.etat === 'coherent') g.append(s('ellipse', { class: 'trait', cx: 120, cy: 75, rx: 113, ry: 68, 'stroke-width': 4 }), s('ellipse', { class: 'trait', cx: 120, cy: 75, rx: 104, ry: 59, 'stroke-width': 1.3 }));
    else if (v.etat === 'ajustement') g.append(s('polygon', { class: 'trait', points: '5,75 40,5 200,5 235,75 200,145 40,145', 'stroke-width': 4 }), s('polygon', { class: 'trait', points: '19,75 47,15 193,15 221,75 193,135 47,135', 'stroke-width': 1.3 }));
    else if (v.etat === 'incoherent') g.append(s('rect', { class: 'trait', x: 5, y: 5, width: 230, height: 140, 'stroke-width': 6 }), s('rect', { class: 'trait', x: 15, y: 15, width: 210, height: 120, 'stroke-width': 1.5 }), s('line', { class: 'trait', x1: 30, x2: 210, y1: 86, y2: 86, 'stroke-width': 1.2 }));
    else g.append(s('rect', { class: 'trait', x: 6, y: 6, width: 228, height: 138, rx: 20, 'stroke-width': 3.5, 'stroke-dasharray': '12 8' }));
    const mot = E.court.toUpperCase();
    const taille = Math.min(29, 196 / (mot.length * 0.82));
    g.append(s('text', { class: 'mot-t', x: 120, y: 75, 'text-anchor': 'middle', 'font-size': taille.toFixed(1) }, mot));
    const sous = v.etat === 'indetermine' ? 'À COMPLÉTER' : `${v.respectees} / ${v.evaluees} RÈGLES`;
    g.append(s('text', { class: 'mot-t', x: 120, y: 110, 'text-anchor': 'middle', 'font-size': 14 }, sous));
    svg.append(g);
    return svg;
  }

  /* ------------------------------------------------------------------ Contexte de rendu */
  function contexte() {
    const special = ui.special && ui.special !== 'hors_univers' ? F.speciaux[ui.special].dossier : null;
    const d = special || AF.dossier();
    const e = special
      ? { cas: 'robert', montant: d.demande && d.demande.montant_cad, retrait: d.profil ? d.profil.retrait_prevu_ans : null, exclusion: !!(d.profil && (d.profil.exclusions || []).length) }
      : AF.etat();
    return { d, e, b: special ? null : AF.brouillon(), special: !!special, params: special ? null : AF.parametres(e.cas) };
  }
  const editable = (ctx, champ) => !ctx.special && ctx.params && (ctx.params[champ] || []).length > 1;
  const estDepart = (ctx) => !ctx.special && F.cas[ctx.e.cas] && cleEtat(ctx.e) === F.cas[ctx.e.cas].depart;

  function libelleValeur(champ, v, cas) {
    if (champ === 'montant') return cad(v);
    if (champ === 'retrait') return typo(AF.fmt.retrait(v));
    const ex = exclusionsDeclarees(cas).map(secteur).join(', ') || 'déclaré';
    return v ? `en excluant le secteur ${ex}` : 'sans exclure de secteur';
  }

  /* Un mot variable de la phrase : souligné en pointillé, il ouvre un sélecteur ancré. */
  function motVariable(ctx, champ) {
    const v = ctx.e[champ];
    const vb = ctx.b ? ctx.b[champ] : v;
    const change = !!ctx.b && vb !== v;
    const lib = libelleValeur(champ, change ? vb : v, ctx.e.cas);
    const mot = editable(ctx, champ)
      ? h('span', {
        class: `mot${champ === 'exclusion' ? ' long' : ''}`, role: 'button', tabindex: '0', 'data-k': `mot-${champ}`, 'data-champ': champ,
        'aria-haspopup': 'listbox', 'aria-expanded': 'false', 'aria-label': `${lib} : corriger ${CHAMP[champ]}`,
        onclick: (ev) => ouvrirSelecteur(ev.currentTarget, champ),
        onkeydown: (ev) => { if (ev.key === 'Enter' || ev.key === ' ' || ev.key === 'ArrowDown') { ev.preventDefault(); ouvrirSelecteur(ev.currentTarget, champ); } },
      }, lib)
      : h('span', { class: 'mot-fixe' }, lib);
    if (!change) return mot;
    return [h('del', { class: 'corr' }, h('span', { class: 'sr-only' }, 'ancienne valeur : '), libelleValeur(champ, v, ctx.e.cas)), ' ',
      h('ins', { class: 'corr' }, h('span', { class: 'sr-only' }, 'correction proposée : '), mot)];
  }

  function phraseTitre(ctx) {
    const { d, e } = ctx, p = d.profil || {}, dem = d.demande || {};
    const morceaux = [`${p.nom || 'La personne'} envisage de placer `, motVariable(ctx, 'montant'), ` dans ${nomActif(dem.ticker)}`];
    if (editable(ctx, 'exclusion') || e.cas === 'mateo') morceaux.push(', ', motVariable(ctx, 'exclusion'));
    else if (editable(ctx, 'retrait') || e.retrait != null) morceaux.push(', avec un retrait ', motVariable(ctx, 'retrait'));
    else if (p.horizon_ans != null) morceaux.push(`, sur un horizon de ${p.horizon_ans}\u00a0ans`);
    morceaux.push('.');
    return morceaux;
  }

  /* ------------------------------------------------------------------ Rendu général */
  function rendre() {
    fermerSelecteur(false);
    arreterRelecture();
    const focus = document.activeElement && document.activeElement.closest ? document.activeElement.closest('[data-k]') : null;
    const fa = ui.focusApres;
    const cleFocus = fa ? fa.k : (focus ? focus.dataset.k : null);
    const viser = !!(fa && fa.viser);
    ui.focusApres = null;
    const statut = ui.special ? 'courante' : AF.statut();
    document.body.dataset.statut = statut;
    document.body.dataset.niveau = AF.niveau();
    rendreTete();
    rendreSommaire();
    rendreBandeaux();
    rendreTexte();
    rendrePied();
    rendreColophon();
    if ($('#editions').open) rendreEditions();
    ouvrirGroupes();
    for (const id of ui.notesOuvertes) { const n = document.getElementById(id); if (n) { n.open = true; const g = n.closest('.notes-groupe'); if (g) g.open = true; } }
    if (cleFocus) {
      const el = document.querySelector(`[data-k="${CSS.escape(cleFocus)}"]`);
      if (el) {
        el.focus({ preventScroll: !viser });
        if (viser) el.scrollIntoView({ block: 'start', behavior: reduit() ? 'auto' : 'smooth' });
      }
    }
    dessinerGraphes();
  }

  const ecranLarge = window.matchMedia('(min-width: 960px)');
  function ouvrirGroupes() { document.querySelectorAll('.notes-groupe').forEach((g) => { g.open = ecranLarge.matches; }); }

  function rendreTete() {
    const m = AF.meta;
    $('#bandeau').textContent = `Simulation éducative · données de démonstration précalculées par le moteur réel · ${AF.fmt.date(String(m.genere_le).slice(0, 10))} · commit ${m.commit}`;
    $('#lien-galerie').href = AF.lien('../index.html');
    document.querySelectorAll('.niveau button').forEach((bt) => bt.setAttribute('aria-pressed', String(bt.dataset.niveau === AF.niveau())));
    document.title = `Carnet · ${ui.special ? 'cas limite' : AF.nomCas(AF.etat().cas)} · Second avis`;
  }

  function rendreSommaire() {
    const nav = $('#sommaire');
    const cas = AF.etat().cas;
    const g1 = h('div', { class: 'groupe' }, h('span', { class: 'etiq pc' }, 'Carnets'));
    AF.cas().forEach((c, i) => {
      if (i) g1.append(h('span', { 'aria-hidden': 'true' }, '·'));
      g1.append(h('button', { type: 'button', 'data-k': `cas-${c}`, 'aria-current': !ui.special && c === cas ? 'true' : null, onclick: () => choisirCas(c) }, AF.nomCas(c)));
    });
    const g2 = h('div', { class: 'groupe' }, h('span', { class: 'etiq pc' }, 'Cas limites'));
    SPECIAUX.forEach((x, i) => {
      if (i) g2.append(h('span', { 'aria-hidden': 'true' }, '·'));
      g2.append(h('button', { type: 'button', 'data-k': `special-${x.cle}`, 'aria-current': ui.special === x.cle ? 'true' : null, onclick: () => choisirSpecial(x.cle) }, x.nom));
    });
    nav.replaceChildren(g1, g2);
  }

  const bouton = (texte, action, k, classe, inactif) => h('button', { type: 'button', class: `btn${classe ? ` ${classe}` : ''}`, 'data-k': k, disabled: !!inactif, onclick: action }, texte);

  function rendreBandeaux() {
    const z = $('#bandeaux');
    z.replaceChildren();
    if (ui.special) {
      z.append(h('div', { class: 'statut-bandeau special', role: 'note' },
        h('p', null, h('strong', null, 'Cas limite. '), 'Dossier réel précalculé par le moteur, hors de tes éditions : il se lit, il ne se corrige pas et ne s’ajoute pas à l’historique.'),
        h('div', { class: 'boutons' }, bouton(`Revenir au carnet de ${AF.nomCas(AF.etat().cas)}`, quitterSpecial, 'quitter-special', 'plein'))));
    } else if (AF.statut() === 'archive') {
      const pos = AF.position(), der = AF.historique().length - 1;
      z.append(h('div', { class: 'statut-bandeau archive', role: 'note' },
        h('p', null, h('strong', null, 'Archive : '), 'tu relis la ', ord(pos + 1), ' édition. La dernière est la ', ord(der + 1), '. Rien n’a été effacé.'),
        h('div', { class: 'boutons' },
          bouton('Revenir à la dernière', () => { ui.focusApres = { k: 'col-editions', viser: false }; AF.allerA(der); }, 'arch-derniere', 'plein'),
          bouton('Restaurer cette édition', () => { ui.focusApres = { k: 'section-correction', viser: true }; AF.restaurer(pos); }, 'arch-restaurer'))));
    }
    if (ui.demo !== 'normal') {
      z.append(h('div', { class: 'statut-bandeau demo', role: 'note' },
        h('p', null, h('strong', null, 'Démonstration. '), `État « ${DEMOS[ui.demo]} » affiché pour montrer l’interface ; ce n’est pas un état réel du produit.`),
        h('div', { class: 'boutons' }, bouton('Revenir à l’état normal', () => changerDemo('normal'), 'demo-retour'))));
    }
  }

  function rendreTexte() {
    nBloc = 0; nTampon = 0;
    ui.graphes = [];
    const main = $('#texte');
    main.replaceChildren();
    if (ui.special === 'hors_univers') { remplir(main, pageHorsUnivers()); return; }
    const ctx = contexte();
    main.append(blocTitre(ctx));
    if (ui.demo !== 'normal') { remplir(main, pageDemo(ctx)); return; }
    main.append(blocVerdict(ctx));
    const corr = sectionCorrection(ctx);
    if (corr) main.append(corr);
    main.append(tableDesMatieres());
    main.append(sectionPourquoi(ctx), sectionRegles(ctx), sectionOptions(ctx), sectionPortefeuille(ctx), sectionProfil(ctx), sectionJournal(ctx), sectionLimites(ctx));
    if (approfondi()) main.append(annexeFaits(ctx));
  }

  function composer(b, contenu, opts = {}) {
    return h('div', { class: `bloc${opts.classe ? ` ${opts.classe}` : ''}` }, h('div', { class: 'texte' }, contenu), b.marge(opts.avantMarge));
  }
  function section(id, num, titre, ...contenu) {
    return h('section', { class: 'section perimable', id: `s-${id}`, 'aria-labelledby': `t-${id}` },
      h('h2', { class: 'section-tete', id: `t-${id}`, tabindex: '-1', 'data-k': `section-${id}` },
        h('span', { class: 'num' }, num), h('span', { class: 'titre' }, titre),
        h('span', { class: 'perime-etiq' }, 'épreuve périmée · à relire')),
      contenu);
  }

  /* ------------------------------------------------------------------ Titre : la phrase, ses mots, le tampon */
  function blocTitre(ctx) {
    const { d } = ctx, p = d.profil || {}, dem = d.demande || {};
    const kicker = h('p', { class: 'kicker' }, h('span', { class: 'pc' }, ctx.special ? 'Cas limite' : 'Dossier'),
      ` · ${p.nom || '—'}${p.age ? `, ${p.age} ans` : ''}${p.profession ? ` · ${p.profession}` : ''}`);
    const titre = h('h1', { class: 'phrase', id: 'phrase' }, phraseTitre(ctx));
    const sesMots = dem.texte ? h('p', { class: 'ses-mots' }, h('span', { class: 'pc' }, 'Ses mots · '), `« ${dem.texte} »`) : null;
    const champs = ['montant', 'retrait', 'exclusion'].filter((c) => editable(ctx, c));
    let consigne = null;
    if (ctx.special) consigne = h('p', { class: 'consigne' }, 'Cas limite : la phrase ne se corrige pas.');
    else if (ui.demo === 'normal' && champs.length) consigne = h('p', { class: 'consigne' }, 'Les mots soulignés en pointillé se corrigent : touche-les pour proposer une autre valeur.');
    let epreuve = null;
    if (ctx.b) {
      epreuve = h('div', { class: 'encadre', role: 'note', 'aria-label': 'Correction proposée' },
        h('h3', null, 'Correction proposée, pas encore relue'),
        h('p', null, typo(AF.decrire(ctx.e, ctx.b)), '. ', 'Tout ce qui suit décrit encore l’ancienne valeur : c’est une épreuve périmée.'),
        h('div', { class: 'actions' }, bouton('Relire avec cette correction', appliquer, 'titre-appliquer', 'rouge'), bouton('Abandonner la correction', () => AF.abandonner(), 'titre-abandonner')));
    }
    let margeTitre;
    if (ui.demo !== 'normal') {
      margeTitre = h('div', { class: 'tampon-zone' }, h('p', { class: 'tampon-legende vide' }, 'Avis non affiché : la page n’est pas composée.'));
    } else {
      const v = d.verdict || {}, E = AF.ETATS[v.etat] || AF.ETATS.indetermine;
      const conditionnel = (d.questions || []).length && v.etat !== 'indetermine';
      margeTitre = h('div', { class: 'tampon-zone' }, tampon(d),
        h('p', { class: 'tampon-legende' }, h('span', { class: 'pc' }, `Avis du Gardien · ${E.court}`),
          conditionnel ? [h('br'), h('span', { class: 'conditionnel' }, 'Conclusion conditionnelle')] : null),
        h('p', { class: 'perime-marque' }, 'Ancien avis : à relire après la correction.'));
    }
    return h('header', { class: 'bloc entete' }, h('div', { class: 'texte' }, kicker, titre, sesMots, consigne, epreuve), h('div', { class: 'marge' }, margeTitre));
  }

  /* ------------------------------------------------------------------ L'avis en une phrase, puis le miroir */
  function blocVerdict(ctx) {
    const { d } = ctx, b = new Bloc('verdict');
    const v = d.verdict || { etat: 'indetermine', respectees: 0, evaluees: 0 };
    const E = AF.ETATS[v.etat] || AF.ETATS.indetermine;
    const lead = h('p', { class: 'verdict-lead' }, h('strong', null, `${E.long}.`), ' ',
      v.evaluees ? `${v.respectees} règle${pl(v.respectees)} respectée${pl(v.respectees)} sur ${v.evaluees}.` : 'Aucune règle n’a pu être évaluée.');
    const nonOk = (d.regles || []).filter((r) => r.niveau !== 'ok');
    for (const niv of ['rouge', 'orange', 'gris']) {
      const rs = nonOk.filter((r) => r.niveau === niv);
      if (!rs.length) continue;
      if (niv === 'gris') { rs.forEach((r) => lead.append(' ', ...annoter(r.explication, b, ctx, r.faits))); continue; }
      const tete = { rouge: 'Ce qui bloque', orange: 'À ajuster' }[niv];
      lead.append(' ', `${tete}\u00a0: `, ...rs.map((r, i) => `${i ? ', ' : ''}«\u00a0${r.libelle}\u00a0»`), '.');
    }
    const contenu = [lead];
    const miroir = (d.texte && d.texte.miroir) || [];
    miroir.forEach((ph, i) => contenu.push(i === 0
      ? h('p', { class: 'lead' }, annoter(ph.texte, b, ctx, ph.faits), ' ', signeType(ph.type))
      : h('p', null, signeType(ph.type), annoter(ph.texte, b, ctx, ph.faits))));
    const qs = d.questions || [];
    if (qs.length) {
      const conditionnel = v.etat !== 'indetermine';
      const enc = h('aside', { class: 'encadre question' });
      qs.forEach((q) => {
        const m = /^Question décisive\s*[—–-]\s*/.exec(q);
        enc.append(h('h3', null, m ? 'Question décisive' : 'À compléter'), h('p', null, annoter(m ? q.slice(m[0].length) : q, b, ctx, [])));
      });
      const r = ctx.params ? ctx.params.retrait.find((x) => x != null) : null;
      if (conditionnel && editable(ctx, 'retrait') && ctx.e.retrait == null && r != null) {
        enc.append(h('p', { class: 'petit' }, 'Cet avis reste conditionnel tant que la date de retrait n’est pas dite.'),
          h('div', { class: 'actions' }, bouton(`Oui : proposer un retrait ${typo(AF.fmt.retrait(r))}`, () => proposerDepuis({ retrait: r }, 'mot-retrait'), 'question-retrait', 'plein')));
      } else {
        enc.append(h('p', { class: 'petit' }, 'Répondre ici n’est pas réalisé dans ce prototype : le dossier reste tel que le moteur l’a rendu.'));
      }
      contenu.push(enc);
    }
    return composer(b, contenu, { classe: 'perimable verdict' });
  }

  function tableDesMatieres() {
    const items = [['pourquoi', 'Pourquoi'], ['regles', 'Les règles'], ['options', 'Les options'], ['portefeuille', 'Le portefeuille'], ['profil', 'Ce que la page sait'], ['journal', 'Le journal'], ['limites', 'Les limites']];
    if (approfondi()) items.push(['faits', 'Tous les faits']);
    return h('nav', { class: 'toc', 'aria-label': 'Dans ce carnet' }, h('span', { class: 'pc' }, 'Dans ce carnet'),
      h('ol', null, items.map(([id, t], i) => h('li', null, h('a', { href: `#s-${id}` }, `${ROMAINS[i]}. ${t}`)))));
  }

  /* ------------------------------------------------------------------ Ce que la correction change (édition comparée) */
  function sectionCorrection(ctx) {
    if (ctx.special) return null;
    const hist = AF.historique(), pos = AF.position(), cur = hist[pos];
    if (cur.parent == null || cur.parent < 0) return null;
    const par = hist[cur.parent];
    if (par.etat.cas !== cur.etat.cas) return null;
    const c = AF.comparer(par.etat, cur.etat);
    const dA = AF.dossierDe(par.etat), dB = ctx.d;
    const b = new Bloc('correction');
    const ancien = { prefixe: 'a-', prime: '′', edition: `fait de la ${ordinal(par.i + 1)} édition` };
    const lignes = h('ul', { class: 'lignes' });
    const E = (x) => (AF.ETATS[x] || {}).long || x;
    const ligne = (lib, ...val) => h('li', null, h('span', { class: 'lib-c' }, lib), h('span', { class: 'val-c' }, val));
    lignes.append(ligne('Avis',
      c.verdict.change ? [h('del', { class: 'corr' }, E(c.verdict.avant)), ' ', h('ins', { class: 'corr' }, E(c.verdict.apres))] : ['inchangé : ', E(c.verdict.apres)]));
    const changees = c.regles.filter((r) => r.change), stables = c.regles.filter((r) => !r.change);
    for (const r of changees) {
      const marque = (n) => `${SIGNE_REGLE[n] || ''} ${niveauRegle(n)}`;
      lignes.append(ligne(r.libelle,
        r.avant == null ? [h('ins', { class: 'corr' }, marque(r.apres)), ' (règle ajoutée)']
          : r.apres == null ? [h('del', { class: 'corr' }, marque(r.avant)), ' (règle retirée)']
            : [h('del', { class: 'corr' }, marque(r.avant)), ' ', h('ins', { class: 'corr' }, marque(r.apres))]));
    }
    if (!changees.length) lignes.append(ligne('Règles', 'aucune ne change de niveau.'));
    const fxA = (dA.comparaison && dA.comparaison.faits) || {}, fxB = (dB.comparaison && dB.comparaison.faits) || {};
    for (const m of c.mesures) {
      if (m.avant == null || m.apres == null) continue;
      const f = (x) => (m.unite === '$' ? cad(x) : pct(x, 1));
      const fa = AF.fait(fxA[`apres_${m.cle}`], dA), fb = AF.fait(fxB[`apres_${m.cle}`], dB);
      const ca = fa ? b.appel(noteFait(fa, ancien)) : null, cb = fb ? b.appel(noteFait(fb)) : null;
      const pareil = Math.abs(m.apres - m.avant) < 1e-9;
      lignes.append(ligne(m.titre,
        pareil ? [h('span', { class: 'nowrap' }, f(m.apres), cb), ' (inchangé)']
          : [h('del', { class: 'corr' }, h('span', { class: 'nowrap' }, f(m.avant)), ca), ' ', h('ins', { class: 'corr' }, h('span', { class: 'nowrap' }, f(m.apres)), cb)]));
    }
    const contenu = [
      h('p', { class: 'chapeau' }, ord(par.i + 1), ' édition → ', ord(pos + 1), ` édition · ${typo(c.motif)}.`),
      lignes,
      stables.length ? h('p', { class: 'inchange' }, `${stables.length} règle${pl(stables.length)} inchangée${pl(stables.length)} : ${stables.map((r) => r.libelle).join(', ')}.`) : null,
      h('p', { class: 'petit' }, T('Les mesures sont celles du portefeuille avec la demande, sur la même période passée, dans les deux éditions.', 'Mesures « après la demande » des deux dossiers (moteur historique B, même fenêtre) ; barré : édition précédente, souligné : cette édition.')),
      h('div', { class: 'actions' }, bouton('Annuler cette correction', () => AF.annuler(), 'corr-annuler'), bouton(`Relire la ${ordinal(par.i + 1)} édition`, () => AF.allerA(par.i), 'corr-relire')),
    ];
    const sec = section('correction', 'Correction', 'Ce que la correction change', composer(b, contenu));
    sec.classList.add('comparee');
    sec.classList.remove('perimable');
    return sec;
  }

  /* ------------------------------------------------------------------ I. Pourquoi, et ce qui changerait l'avis */
  function legendeTypes() {
    return h('ul', { class: 'legende-types', 'aria-label': 'Signes des notes' },
      h('li', null, signeType('FAIT', true)), h('li', null, signeType('HYPOTHESE', true)), h('li', null, signeType('SCENARIO', true)),
      h('li', null, signeType('PROFIL', true)), h('li', null, signeType('LIBRE', true)));
  }

  function sectionPourquoi(ctx) {
    const { d } = ctx, b = new Bloc('pourquoi');
    const ph = (d.texte && d.texte.pourquoi) || [];
    const contenu = [h('p', { class: 'chapeau' }, T('Chaque phrase porte son signe : fait observé, hypothèse de l’équipe ou scénario fictif. Chaque chiffre renvoie à sa note.', 'Phrases du Rédacteur, typées ; chaque nombre est relié à un fait du dossier par sa valeur et son unité.')), legendeTypes()];
    if (ph.length) ph.forEach((p) => contenu.push(h('p', null, signeType(p.type), annoter(p.texte, b, ctx, p.faits))));
    else contenu.push(h('p', { class: 'vide' }, 'Le dossier ne donne pas de raison rédigée pour cet avis.'));
    const cqc = (d.texte && d.texte.ce_qui_changerait) || [];
    const enc = h('aside', { class: 'encadre', 'aria-labelledby': 'enc-cqc' }, h('h3', { id: 'enc-cqc' }, 'Ce qui changerait l’avis'));
    if (!cqc.length) enc.append(h('p', { class: 'vide' }, 'Le dossier ne propose aucun changement de paramètre qui modifierait cet avis.'));
    cqc.forEach((p, i) => {
      enc.append(h('p', null, signeType(p.type), annoter(p.texte, b, ctx, p.faits)));
      const montants = [...String(p.texte).matchAll(/(\d{1,3}(?:[ \u00a0\u202f]\d{3})+|\d+)\s?(?:CAD|\$)/g)].map((x) => +x[1].replace(/[ \u00a0\u202f]/g, ''));
      for (const mt of montants) {
        if (!ctx.params || mt === ctx.e.montant) continue;
        if (ctx.params.montant.includes(mt)) enc.append(h('div', { class: 'actions' }, bouton(`Proposer ${cad(mt)} comme correction`, () => proposerDepuis({ montant: mt }, 'mot-montant'), `cqc-${i}-${mt}`, 'plein')));
        else enc.append(h('p', { class: 'petit' }, `${cad(mt)} n’est pas précalculé dans ce prototype : cette correction ne peut pas être proposée ici.`));
      }
    });
    contenu.push(enc);
    return section('pourquoi', 'I', T('Pourquoi cet avis', 'Motifs du Gardien'), composer(b, contenu));
  }

  /* ------------------------------------------------------------------ II. Les règles */
  function sectionRegles(ctx) {
    const { d } = ctx, b = new Bloc('regles'), rs = d.regles || [];
    const contenu = [h('p', { class: 'chapeau' }, T('Le verdict est décidé par du code, le Gardien, jamais par un modèle. Voici ses règles, dans son ordre.', 'Règles écrites en code, ordre fixe ; le Gardien est l’unique arbitre du verdict.'))];
    if (!rs.length) contenu.push(h('p', { class: 'vide' }, 'Aucune règle dans ce dossier.'));
    else if (!approfondi()) {
      contenu.push(h('ul', { class: 'regles' }, rs.map((r) => h('li', { class: `regle ${r.niveau}` },
        h('div', { class: 'regle-ligne' }, h('span', { class: 'signe', 'aria-hidden': 'true' }, SIGNE_REGLE[r.niveau] || '·'), h('span', { class: 'lib' }, r.libelle), h('span', { class: 'points', 'aria-hidden': 'true' }), h('span', { class: 'niv' }, niveauRegle(r.niveau))),
        r.niveau !== 'ok' ? h('p', { class: 'expl' }, annoter(r.explication, b, ctx, r.faits)) : null))));
      contenu.push(h('p', { class: 'petit' }, 'Le détail de chaque règle, ses faits et ses références sont en lecture « Approfondi ».'));
    } else {
      const table = h('table', { class: 'tableau empile regles-t' },
        h('caption', null, 'Règles évaluées, dans l’ordre du Gardien. Signes : ✓ respectée, △ à ajuster, ✕ bloquante, ? information manquante.'),
        h('thead', null, h('tr', null, h('th', { scope: 'col' }, 'Règle'), h('th', { scope: 'col' }, 'Niveau'), h('th', { scope: 'col' }, 'Type'), h('th', { scope: 'col' }, 'Explication et références'))),
        h('tbody', null, rs.map((r) => h('tr', null,
          h('th', { scope: 'row' }, r.libelle, h('br'), h('span', { class: 'id' }, r.code)),
          h('td', { 'data-label': 'Niveau' }, h('span', { class: 'nowrap' }, h('span', { 'aria-hidden': 'true' }, `${SIGNE_REGLE[r.niveau] || ''} `), niveauRegle(r.niveau))),
          h('td', { 'data-label': 'Type' }, signeType(r.type, true)),
          h('td', { 'data-label': 'Explication' }, annoter(r.explication, b, ctx, r.faits),
            (r.references || []).length ? h('details', null, h('summary', null, `${r.references.length} référence${pl(r.references.length)}`), h('ol', { class: 'n-refs' }, r.references.map(AF.reference).filter(Boolean).map(itemReference))) : null)))));
      contenu.push(h('div', { class: 'tableau-cadre' }, table));
    }
    const v = d.verdict || {};
    return section('regles', 'II', T('Les règles', `Règles évaluées (${v.evaluees || 0})`), composer(b, contenu));
  }

  /* ------------------------------------------------------------------ III. Les options comparées */
  function sectionOptions(ctx) {
    const { d } = ctx, b = new Bloc('options'), os = d.options || [];
    const contenu = [];
    if (!os.length) contenu.push(h('p', { class: 'vide' }, 'Le dossier ne compare aucune option.'));
    else {
      const ticker = (d.demande || {}).ticker;
      const table = h('table', { class: 'tableau empile' },
        h('caption', null, 'Ordre du dossier, pas un classement. Comparer n’est pas recommander : le produit ne dit ni d’acheter ni de vendre.'),
        h('thead', null, h('tr', null, h('th', { scope: 'col' }, 'Option'), h('th', { scope: 'col' }, 'Placement'), h('th', { scope: 'col', class: 'nb' }, 'Montant'), approfondi() ? h('th', { scope: 'col', class: 'nb' }, 'Horizon') : null, h('th', { scope: 'col' }, 'Avis du Gardien'), h('th', { scope: 'col' }, 'Remarque'))),
        h('tbody', null, os.map((o, i) => {
          const remarque = [];
          if (o.note) remarque.push(annoter(o.note, b, ctx, o.faits));
          else if (o.constat) remarque.push(annoter(o.constat, b, ctx, o.faits));
          else if ((o.faits || []).length) remarque.push(annoter('', b, ctx, o.faits));
          if (i === 0) remarque.push(h('span', { class: 'vide' }, 'La demande telle qu’elle est.'));
          else if (ctx.params && o.ticker === ticker && o.montant_cad !== ctx.e.montant && ctx.params.montant.includes(o.montant_cad)) {
            remarque.push(' ', h('button', { type: 'button', class: 'lien-bouton', 'data-k': `opt-${i}`, onclick: () => proposerDepuis({ montant: o.montant_cad }, 'mot-montant') }, `Proposer ${cad(o.montant_cad)} dans la phrase`));
          } else if (o.ticker !== ticker) remarque.push(' ', h('span', { class: 'vide' }, 'Autre placement : non modifiable dans ce prototype.'));
          return h('tr', null,
            h('th', { scope: 'row' }, o.nom),
            h('td', { 'data-label': 'Placement' }, o.libelle_actif || nomActif(o.ticker), ' ', h('span', { class: 'id' }, o.ticker)),
            h('td', { 'data-label': 'Montant', class: 'nb' }, cad(o.montant_cad)),
            approfondi() ? h('td', { 'data-label': 'Horizon', class: 'nb' }, o.horizon_ans != null ? `${o.horizon_ans}\u00a0ans` : '—') : null,
            h('td', { 'data-label': 'Avis' }, etatMini(o.etat)),
            h('td', { 'data-label': 'Remarque' }, remarque));
        })));
      contenu.push(h('div', { class: 'tableau-cadre' }, table));
    }
    return section('options', 'III', T('D’autres façons de le faire', 'Options comparées'), composer(b, contenu));
  }

  /* ------------------------------------------------------------------ IV. Le portefeuille, sans et avec la demande */
  function sectionPortefeuille(ctx) {
    const { d } = ctx, k = d.comparaison || {};
    if (!k.disponible) {
      return section('portefeuille', 'IV', T('Ton portefeuille, sans et avec la demande', 'Comparaison appariée'),
        h('div', { class: 'bloc' }, h('div', { class: 'texte' }, h('p', { class: 'vide' }, `Comparaison indisponible pour ce dossier${k.raison ? ` : ${k.raison}` : '.'}`)), h('div', { class: 'marge' })));
    }
    const b = new Bloc('portefeuille'), fx = k.faits || {};
    const fFen = AF.fait(fx.fenetre_portefeuille, d);
    const contenu = [
      h('p', { class: 'chapeau' }, T('Ton épargne telle qu’elle est, puis la même avec la demande, mesurées de la même façon sur la même période passée. L’écart entre les deux est le message.', `Moteur ${k.moteur} (${k.version_moteur}) : ${k.politique}. Écart apparié = après moins avant.`)),
      h('p', { class: 'fenetre-obs' }, `observé, ${k.fenetre.debut} → ${k.fenetre.fin} · ${fr(k.fenetre.observations)} séances`, fFen ? b.appel(noteFait(fFen)) : null),
      pentes(ctx, b),
      courbe(ctx, b),
    ];
    if (approfondi()) contenu.push(tablePoids(ctx, b), tableFenetres(ctx));
    return section('portefeuille', 'IV', T('Ton portefeuille, sans et avec la demande', 'Comparaison appariée : portefeuille avant et après'), composer(b, contenu));
  }

  function pentes(ctx, b) {
    const d = ctx.d, fx = (d.comparaison && d.comparaison.faits) || {}, ms = AF.mesures(d);
    const pc = ms.filter((m) => m.unite === '%');
    const vals = pc.flatMap((m) => [m.avant, m.apres]).concat(0);
    let lo = Math.min(...vals), hi = Math.max(...vals);
    const marge = (hi - lo) * 0.08; lo -= marge; hi += marge;
    const grille = h('div', { class: 'pentes' });
    for (const m of ms) grille.append(figurePente(ctx, b, m, m.unite === '%' ? [lo, hi] : [0, Math.max(m.avant, m.apres) * 1.12], fx));
    const lexique = h('dl', { class: 'petit lexique' }, ms.map((m) => [h('dt', { class: 'pc' }, m.titre), h('dd', null, m.def)]));
    return [grille,
      h('p', { class: 'pentes-note' }, 'Point creux : sans la demande. Point plein : avec la demande. Les trois mesures en pour cent partagent la même échelle, zéro en tirets ; la valeur finale a sa propre échelle, depuis zéro.'),
      approfondi() ? null : lexique];
  }

  function figurePente(ctx, b, m, dom, fx) {
    const d = ctx.d, W = 160, H = 150, haut = 26, bas = 120, xL = 42, xR = 118;
    const [lo, hi] = dom;
    const Y = (v) => bas - ((v - lo) / (hi - lo || 1)) * (bas - haut);
    const f = (v) => (m.unite === '$' ? cad(v) : pct(v, 1));
    const yA = Y(m.avant), yB = Y(m.apres);
    const svg = s('svg', { viewBox: `0 0 ${W} ${H}`, 'aria-hidden': 'true', focusable: 'false' });
    svg.append(s('line', { class: 'axe', x1: xL, x2: xL, y1: haut - 8, y2: bas + 4 }), s('line', { class: 'axe', x1: xR, x2: xR, y1: haut - 8, y2: bas + 4 }));
    if (lo < 0 && hi > 0) svg.append(s('line', { class: 'zero', x1: 12, x2: W - 6, y1: Y(0), y2: Y(0) }), s('text', { class: 'etiq-pc', x: 2, y: Y(0) + 3, 'font-size': 9 }, '0'));
    if (m.unite === '$') svg.append(s('line', { class: 'zero', x1: 12, x2: W - 6, y1: Y(0), y2: Y(0) }), s('text', { class: 'etiq-pc', x: 2, y: Y(0) + 3, 'font-size': 9 }, '0'));
    svg.append(s('line', { class: 'lien-pente', x1: xL, y1: yA, x2: xR, y2: yB }), s('circle', { class: 'pt-avant', cx: xL, cy: yA, r: 4.6 }), s('circle', { class: 'pt-apres', cx: xR, cy: yB, r: 4.6 }));
    const dessous = (y) => y + 17 <= bas + 12;
    const lA = yB < yA && dessous(yA) ? yA + 17 : yA - 9;
    const lB = yA > yB || !dessous(yB) ? yB - 9 : yB + 17;
    svg.append(s('text', { class: 'etiq', x: xL, y: Math.max(12, lA), 'text-anchor': 'middle', 'font-size': 12 }, f(m.avant)),
      s('text', { class: 'etiq', x: xR, y: Math.max(12, lB), 'text-anchor': 'middle', 'font-size': 12 }, f(m.apres)),
      s('text', { class: 'etiq-pc', x: xL, y: H - 3, 'text-anchor': 'middle', 'font-size': 9 }, 'SANS'),
      s('text', { class: 'etiq-pc', x: xR, y: H - 3, 'text-anchor': 'middle', 'font-size': 9 }, 'AVEC'));
    const fA = AF.fait(fx[`avant_${m.cle}`], d), fB = AF.fait(fx[`apres_${m.cle}`], d), fE = fx[`ecart_${m.cle}`] ? AF.fait(fx[`ecart_${m.cle}`], d) : null;
    const ecartTxt = m.unite === '$' ? `${m.ecart > 0 ? '+' : m.ecart < 0 ? '\u2212' : ''}${cad(Math.abs(m.ecart))}` : pts(m.ecart);
    const noteE = fE ? noteFait(fE) : noteLibre(`ecart-${m.cle}`, `Écart affiché par le socle commun : après moins avant${fA && fB ? `, soit ${fB.id} moins ${fA.id}` : ''}. Le dossier ne porte pas cet écart comme un fait.`, 'Écart affiché, sans fait propre');
    return h('figure', { class: 'pente' },
      h('figcaption', null, m.titre),
      svg,
      h('p', { class: 'valeurs' },
        h('span', null, 'Sans\u00a0: ', h('span', { class: 'nowrap' }, f(m.avant), fA ? b.appel(noteFait(fA)) : null)),
        h('span', null, 'Avec\u00a0: ', h('span', { class: 'nowrap' }, f(m.apres), fB ? b.appel(noteFait(fB)) : null)),
        h('span', { class: 'ecart' }, 'Écart\u00a0: ', h('span', { class: 'nowrap' }, ecartTxt, b.appel(noteE)), m.sens ? h('span', { class: 'vide' }, ` (${SENS[m.sens] || m.sens})`) : null)));
  }

  /* La courbe réelle des baisses, dessinée après insertion (largeur du conteneur). */
  function courbe(ctx, b) {
    const d = ctx.d, sp = d.series_portefeuille, fx = (d.comparaison && d.comparaison.faits) || {};
    if (!sp || !(sp.avant || []).length) return h('p', { class: 'vide' }, 'Pas de série de valeurs dans ce dossier.');
    const n = Math.min(sp.avant.length, sp.apres.length);
    let iMin = 0;
    for (let i = 1; i < n; i++) if (sp.apres[i][2] < sp.apres[iMin][2]) iMin = i;
    const zone = h('div', { class: 'courbe-zone' });
    const out = h('output', { id: 'lecteur-sortie', for: 'lecteur-courbe' });
    const range = h('input', { type: 'range', id: 'lecteur-courbe', min: 0, max: n - 1, step: 1, value: iMin, 'data-k': 'lecteur-courbe', 'aria-describedby': 'lecteur-sortie' });
    const fA = AF.fait(fx.avant_pire_chute, d), fB = AF.fait(fx.apres_pire_chute, d);
    const pas = AF.meta.pas_series;
    ui.graphes.push({ zone, sp, n, range, out });
    return h('figure', { class: 'courbe' },
      h('p', { class: 'petit' }, h('strong', null, T('Baisse depuis le dernier sommet, semaine après semaine', 'Drawdown du portefeuille, série échantillonnée'))),
      h('ul', { class: 'courbe-legende' },
        h('li', null, h('span', { class: 'ech trame', 'aria-hidden': 'true' }), 'trame : sans la demande'),
        h('li', null, h('span', { class: 'ech trait', 'aria-hidden': 'true' }), 'trait : avec la demande')),
      zone,
      h('figcaption', { class: 'fenetre-obs' }, `observé, ${sp.avant[0][0]} → ${sp.avant[n - 1][0]} · aucun prolongement au-delà`),
      h('div', { class: 'lecteur' }, h('label', { for: 'lecteur-courbe' }, 'Parcourir la période passée, point par point (flèches du clavier)'), range, out),
      h('p', { class: 'pentes-note' }, `Courbe tracée ${pas ? `toutes les ${pas} séances` : 'sur une série échantillonnée'} (${fr(n)} points). La plus forte baisse mesurée sur toutes les séances est de `,
        h('span', { class: 'nowrap' }, fA ? pct(fA.valeur, 1) : '—', fA ? b.appel(noteFait(fA)) : null), ' sans la demande et de ',
        h('span', { class: 'nowrap' }, fB ? pct(fB.valeur, 1) : '—', fB ? b.appel(noteFait(fB)) : null), ' avec ; la courbe échantillonnée peut paraître moins profonde.'));
  }

  let nTrame = 0;
  function dessinerCourbe(g) {
    const { zone, sp, n, range, out } = g;
    const W = Math.max(260, Math.round(zone.clientWidth || 600));
    const etroit = W < 520, H = etroit ? 196 : 232;
    const M = { g: 42, d: 10, h: 24, b: 26 };
    const A = sp.avant, B = sp.apres;
    const t = (x) => Date.parse(`${x}T00:00:00Z`);
    const t0 = t(A[0][0]), t1 = t(A[n - 1][0]);
    let minv = 0;
    for (let i = 0; i < n; i++) minv = Math.min(minv, A[i][2], B[i][2]);
    const pas = minv < -30 ? 10 : 5;
    const plancher = -Math.ceil((-minv + 0.5) / pas) * pas;
    const X = (x) => M.g + ((t(x) - t0) / (t1 - t0)) * (W - M.g - M.d);
    const Y = (v) => M.h + (v / plancher) * (H - M.h - M.b);
    const tid = `trame-${++nTrame}`;
    let minA = 0, minB = 0;
    for (let i = 1; i < n; i++) { if (A[i][2] < A[minA][2]) minA = i; if (B[i][2] < B[minB][2]) minB = i; }
    const svg = s('svg', {
      class: 'graphe', viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img',
      'aria-label': `Baisse depuis le dernier sommet, du ${A[0][0]} au ${A[n - 1][0]}, série échantillonnée. Creux de la série tracée : ${pct(A[minA][2], 1)} sans la demande (${A[minA][0]}), ${pct(B[minB][2], 1)} avec la demande (${B[minB][0]}).`,
    });
    svg.append(s('defs', null, s('pattern', { id: tid, width: 4, height: 4, patternUnits: 'userSpaceOnUse' }, s('circle', { class: 'trame-pt', cx: 2, cy: 2, r: 0.95 }))));
    if (approfondi()) {
      (sp.avant_fenetres || []).forEach((fe, i) => {
        if (t(fe.debut) < t0 || t(fe.fin) > t1) return;
        const x1 = X(fe.debut), x2 = Math.max(X(fe.fin), x1 + 3);
        svg.append(s('rect', { class: 'bande', x: x1, y: M.h, width: x2 - x1, height: H - M.h - M.b }),
          s('text', { class: 'etiq-pc', x: (x1 + x2) / 2, y: M.h - 4, 'text-anchor': 'middle', 'font-size': 10 }, String(i + 1)));
      });
    }
    for (let v = 0; v >= plancher; v -= pas) {
      svg.append(s('line', { class: v === 0 ? 'axe' : 'grille', x1: M.g, x2: W - M.d, y1: Y(v), y2: Y(v) }),
        s('text', { class: 'etiq-pc', x: M.g - 6, y: Y(v) + 3.5, 'text-anchor': 'end', 'font-size': 10 }, v === 0 ? '0\u00a0%' : pct(v, 0)));
    }
    const a0 = new Date(t0).getUTCFullYear(), a1 = new Date(t1).getUTCFullYear();
    for (let a = a0 + 1; a <= a1; a++) {
      const x = X(`${a}-01-01`);
      svg.append(s('line', { class: 'axe', x1: x, x2: x, y1: H - M.b, y2: H - M.b + 4 }),
        s('text', { class: 'etiq-pc', x, y: H - 8, 'text-anchor': 'middle', 'font-size': 10 }, String(a)));
    }
    let aire = `M${X(A[0][0]).toFixed(1)},${Y(0).toFixed(1)}`, ligneA = '', ligneB = '';
    for (let i = 0; i < n; i++) {
      const x = X(A[i][0]).toFixed(1);
      aire += ` L${x},${Y(A[i][2]).toFixed(1)}`;
      ligneA += `${i ? ' L' : 'M'}${x},${Y(A[i][2]).toFixed(1)}`;
      ligneB += `${i ? ' L' : 'M'}${X(B[i][0]).toFixed(1)},${Y(B[i][2]).toFixed(1)}`;
    }
    aire += ` L${X(A[n - 1][0]).toFixed(1)},${Y(0).toFixed(1)} Z`;
    svg.append(s('path', { class: 'aire-avant', d: aire, fill: `url(#${tid})` }), s('path', { class: 'ligne-avant', d: ligneA }), s('path', { class: 'ligne-apres', d: ligneB }));
    const xf = X(A[n - 1][0]);
    svg.append(s('line', { class: 'fin', x1: xf, x2: xf, y1: M.h - 14, y2: H - M.b }),
      s('text', { class: 'etiq-pc', x: xf, y: M.h - 16, 'text-anchor': 'end', 'font-size': 10 }, `fin des données · ${A[n - 1][0]}`));
    const curseur = s('g', null);
    svg.append(curseur);
    zone.replaceChildren(svg);
    const maj = () => {
      const i = Math.max(0, Math.min(n - 1, +range.value || 0));
      const x = X(A[i][0]);
      curseur.replaceChildren(s('line', { class: 'curseur', x1: x, x2: x, y1: M.h, y2: H - M.b }),
        s('circle', { class: 'pt-avant', cx: x, cy: Y(A[i][2]), r: 3.6 }), s('circle', { class: 'pt-apres', cx: x, cy: Y(B[i][2]), r: 3.6 }));
      const texte = `${AF.fmt.date(A[i][0])} · baisse sans la demande ${pct(A[i][2], 2)}, avec ${pct(B[i][2], 2)}`;
      out.textContent = approfondi() ? `${texte} · valeur sans ${cad(A[i][1])}, avec ${cad(B[i][1])}` : texte;
      range.setAttribute('aria-valuetext', texte);
    };
    range.oninput = maj;
    maj();
  }

  function dessinerGraphes() {
    if (ui.observateur) ui.observateur.disconnect();
    ui.graphes.forEach(dessinerCourbe);
    if ('ResizeObserver' in window && ui.graphes.length) {
      const largeurs = new Map();
      ui.observateur = new ResizeObserver((entrees) => {
        for (const en of entrees) {
          const g = ui.graphes.find((x) => x.zone === en.target);
          const w = Math.round(en.contentRect.width);
          if (g && largeurs.get(g) !== w) { const premier = !largeurs.has(g); largeurs.set(g, w); if (!premier) dessinerCourbe(g); }
        }
      });
      ui.graphes.forEach((g) => ui.observateur.observe(g.zone));
    }
  }

  function tablePoids(ctx, b) {
    const d = ctx.d, k = d.comparaison, fx = k.faits || {};
    const lignes = [...new Set([...Object.keys(k.poids_avant || {}), ...Object.keys(k.poids_apres || {})])];
    const fA = AF.fait(fx.poids_avant, d), fB = AF.fait(fx.poids_apres, d);
    return h('div', { class: 'tableau-cadre' }, h('table', { class: 'tableau' },
      h('caption', null, `Poids des lignes, ${k.origine_poids === 'declare' ? 'déclarés' : k.origine_poids || ''} ; achat-conservation, sans rééquilibrage.`),
      h('thead', null, h('tr', null, h('th', { scope: 'col' }, 'Ligne'), h('th', { scope: 'col', class: 'nb' }, ['Sans', fA ? b.appel(noteFait(fA)) : null]), h('th', { scope: 'col', class: 'nb' }, ['Avec', fB ? b.appel(noteFait(fB)) : null]))),
      h('tbody', null, lignes.map((t) => h('tr', null, h('th', { scope: 'row' }, nomActif(t), ' ', h('span', { class: 'id' }, t)),
        h('td', { class: 'nb' }, k.poids_avant[t] != null ? pct(k.poids_avant[t] * 100, 1) : '—'),
        h('td', { class: 'nb' }, k.poids_apres[t] != null ? pct(k.poids_apres[t] * 100, 1) : '—'))))));
  }

  function tableFenetres(ctx) {
    const sp = ctx.d.series_portefeuille;
    if (!sp || !(sp.avant_fenetres || []).length) return null;
    return h('div', { class: 'tableau-cadre' }, h('table', { class: 'tableau empile fenetres-t' },
      h('caption', null, 'Fenêtres historiques choisies à l’avance dans le code, numérotées sur la courbe ; descriptives, sans probabilité attribuée.'),
      h('thead', null, h('tr', null, h('th', { scope: 'col' }, 'Fenêtre'), h('th', { scope: 'col', class: 'nb' }, 'Rendement sans'), h('th', { scope: 'col', class: 'nb' }, 'Rendement avec'), h('th', { scope: 'col', class: 'nb' }, 'Pire baisse sans'), h('th', { scope: 'col', class: 'nb' }, 'Pire baisse avec'))),
      h('tbody', null, sp.avant_fenetres.map((fa, i) => {
        const fb = (sp.apres_fenetres || [])[i] || {};
        return h('tr', null, h('th', { scope: 'row' }, `${i + 1}. ${fa.nom}`, h('br'), h('span', { class: 'petit' }, `${fa.debut} → ${fa.fin}`)),
          h('td', { class: 'nb', 'data-label': 'Rendement sans' }, pct(fa.rendement_pct, 1)), h('td', { class: 'nb', 'data-label': 'Rendement avec' }, pct(fb.rendement_pct, 1)),
          h('td', { class: 'nb', 'data-label': 'Pire baisse sans' }, pct(fa.pire_chute_pct, 1)), h('td', { class: 'nb', 'data-label': 'Pire baisse avec' }, pct(fb.pire_chute_pct, 1)));
      }))));
  }

  /* ------------------------------------------------------------------ V. Ce que la page sait de toi */
  function sectionProfil(ctx) {
    const { d } = ctx, b = new Bloc('profil'), p = d.profil || {};
    const lignes = AF.profilLignes(d);
    const champs = ['montant', 'retrait', 'exclusion'].filter((c) => editable(ctx, c));
    const corrigeable = { retrait: 'retrait', exclusions: 'exclusion' };
    const contenu = [h('p', { class: 'chapeau' }, T('Ce que la page a compris de toi, ligne par ligne. Ce qui est inconnu est dit tel quel : rien n’est complété en silence.', 'Profil structuré (Profileur, puis validation par le code) ; nature de chaque ligne : donnée, préférence, contrainte ou inconnue.'))];
    if (ctx.special) contenu.push(h('p', null, h('strong', null, 'Lecture seule. '), 'Cas limite : aucune ligne ne se corrige ici.'));
    else {
      const liens = champs.map((c, i) => [i ? (i === champs.length - 1 ? ' et ' : ', ') : '', h('button', { type: 'button', class: 'lien-texte', 'data-k': `profil-${c}`, onclick: () => ouvrirDepuis(c) }, CHAMP[c])]);
      contenu.push(h('p', null, h('strong', null, 'Lecture seule. '), 'Dans ce prototype, seuls ', liens, ' se corrigent, directement dans la phrase du titre. Les autres lignes viennent du scénario et ne sont pas modifiables ici.'));
    }
    const dl = h('dl', { class: 'profil' });
    for (const l of lignes) {
      let valeur = l.valeur;
      if (l.cle === 'exclusions' && valeur && valeur !== 'Aucun') valeur = valeur.split(', ').map(secteur).join(', ');
      const champ = corrigeable[l.cle];
      const seCorrige = champ && champs.includes(champ);
      dl.append(h('div', { class: `profil-ligne ${l.nature}` },
        h('dt', null, l.libelle),
        h('dd', null, l.nature === 'inconnu' ? 'inconnue, non remplacée' : typo(valeur)),
        h('div', { class: 'meta' }, h('span', { class: `nature ${l.nature}` }, NATURE[l.nature] || l.nature),
          l.note ? h('span', null, typo(l.note)) : null,
          seCorrige ? h('button', { type: 'button', class: 'lien-texte', 'data-k': `profil-ligne-${champ}`, onclick: () => ouvrirDepuis(champ) }, 'se corrige dans le titre') : h('span', null, 'lecture seule'))));
    }
    contenu.push(dl);
    if ((p.citations || []).length) contenu.push(h('p', { class: 'petit' }, h('span', { class: 'pc' }, 'Ses mots, relevés par le Profileur')), h('ul', { class: 'citations' }, p.citations.map((c) => h('li', null, `« ${c} »`))));
    const tensions = (d.texte && d.texte.tensions) || p.tensions || [];
    if (tensions.length) contenu.push(h('p', { class: 'petit' }, h('span', { class: 'pc' }, 'Tensions relevées')), h('ul', { class: 'citations' }, tensions.map((t) => h('li', null, annoter(t, b, ctx, [])))));
    if (approfondi() && p.evaluation) {
      const ev = p.evaluation;
      const L = [['score_retenu', 'Score retenu', (x) => `${fr(x)} / 100`], ['limite', 'Ce qui limite', (x) => x], ['perte_max_tolerance_pct', 'Perte maximale selon la tolérance', (x) => pct(x, 1)], ['perte_max_capacite_pct', 'Perte maximale selon la capacité', (x) => pct(x, 1)], ['perte_max_retenue_pct', 'Perte maximale retenue', (x) => pct(x, 1)], ['seuil_concentration_pct', 'Seuil de concentration (actif très volatil)', (x) => pct(x, 1)], ['seuil_titre_unique_pct', 'Seuil pour un titre unique', (x) => pct(x, 1)], ['poids_pct', 'Part de l’épargne demandée', (x) => pct(x, 0)]];
      contenu.push(h('div', { class: 'tableau-cadre' }, h('table', { class: 'tableau' }, h('caption', null, 'Évaluation du Profileur, telle que rendue par le moteur (barème de l’équipe).'),
        h('tbody', null, L.filter(([cle]) => ev[cle] != null).map(([cle, lib, f]) => h('tr', null, h('th', { scope: 'row' }, lib), h('td', { class: 'nb' }, f(ev[cle]))))))));
    }
    return section('profil', 'V', T('Ce que la page sait de toi', 'Profil structuré'), composer(b, contenu));
  }

  /* ------------------------------------------------------------------ VI. Ce qui a été fait pour écrire cette page */
  function listeJournal(d) {
    const agents = F.sources.agents || {};
    return h('ol', { class: 'journal' }, (d.trace || []).map((t) => {
      const ag = agents[t.agent] || {};
      const modele = ROLES[t.agent] === 'modele';
      return h('li', null,
        h('span', { class: 'duree' }, AF.fmt.ms(t.duree_ms)),
        h('span', { class: 'agent' }, t.agent), ' ',
        h('span', { class: 'nature-role' }, modele ? 'rôle tenu par un modèle' : 'code'), ' ',
        h('span', { class: 'etat-etape' }),
        ` — ${t.action}.`,
        h('span', { class: 'detail' }, typo(t.detail)),
        approfondi() && ag.role ? h('span', { class: 'detail' }, h('em', null, ag.role)) : null,
        approfondi() && (t.references || []).length ? h('details', { class: 'petit' }, h('summary', null, `${t.references.length} référence${pl(t.references.length)} pour ce rôle`), h('ol', { class: 'n-refs' }, t.references.map(AF.reference).filter(Boolean).map(itemReference))) : null);
    }));
  }

  function sectionJournal(ctx) {
    const { d } = ctx, b = new Bloc('journal'), tr = d.trace || [];
    const nModele = tr.filter((t) => ROLES[t.agent] === 'modele').length;
    const contenu = [h('p', { class: 'chapeau' }, tr.length
      ? `${tr.length} étapes enregistrées, dans l’ordre. ${tr.length - nModele} sont du code (calcul, contrôle, décision) ; ${nModele} sont des rôles tenus par un modèle de langage, qui lisent, objectent ou rédigent sans jamais décider du verdict.`
      : 'Le dossier ne contient aucune étape enregistrée.')];
    contenu.push(h('p', { class: 'petit' }, h('span', { class: 'pc' }, 'Mode de cette page · '), AF.meta.mode, '. Durées mesurées lors de la génération des dossiers.'));
    const liste = listeJournal(d);
    contenu.push(liste);
    if (tr.length) contenu.push(h('div', { class: 'actions' }, h('button', { type: 'button', class: 'btn', 'data-k': 'relire-journal', onclick: () => relireJournal(liste, d, 0) }, 'Relire le journal pas à pas'),
      h('span', { class: 'petit' }, ' Relecture des étapes enregistrées, pas un calcul en direct.')));
    const ex = estDepart(ctx) ? AF.execution(ctx.e.cas) : null;
    if (ex && (ex.appels_modele || []).length) {
      contenu.push(h('h3', { class: 'pc' }, 'Appels réels de modèle, demande de départ'),
        h('p', null, `Avec les modèles activés, cette même demande a donné lieu à ${ex.appels_modele.length} appels réels, enregistrés dans `, h('span', { class: 'id' }, ex.source), '. Le texte affiché sur cette page reste celui des modèles de phrases hors ligne.'),
        h('div', { class: 'tableau-cadre' }, h('table', { class: 'tableau empile' },
          h('thead', null, h('tr', null, h('th', { scope: 'col' }, 'Rôle'), h('th', { scope: 'col' }, 'Modèle'), h('th', { scope: 'col', class: 'nb' }, 'Jetons entrée / sortie'), h('th', { scope: 'col', class: 'nb' }, 'Latence'), h('th', { scope: 'col' }, 'Garde-fou'), approfondi() ? h('th', { scope: 'col' }, 'Identifiant') : null)),
          h('tbody', null, ex.appels_modele.map((a) => h('tr', null, h('th', { scope: 'row' }, a.agent),
            h('td', { 'data-label': 'Modèle' }, h('span', { class: 'id' }, a.modele)),
            h('td', { class: 'nb', 'data-label': 'Jetons' }, `${fr(a.jetons_entree)} / ${fr(a.jetons_sortie)}`),
            h('td', { class: 'nb', 'data-label': 'Latence' }, AF.fmt.ms(a.latence_ms)),
            h('td', { 'data-label': 'Garde-fou' }, a.garde_fou === 'configure' ? 'configuré' : a.garde_fou),
            approfondi() ? h('td', { 'data-label': 'Identifiant' }, h('span', { class: 'id' }, a.request_id)) : null))))),
        h('p', { class: 'petit' }, 'Durées de cette exécution : ', (ex.trace || []).map((t, i) => [i ? ' · ' : '', `${t.agent} ${AF.fmt.ms(t.duree_ms)}`]), '.'));
      if (approfondi() && ex.texte) {
        const tx = ex.texte;
        contenu.push(h('details', null, h('summary', { class: 'lien-bouton' }, 'Lire le texte rédigé par le modèle lors de cette exécution'),
          tx.reformulation ? h('p', null, typo(AF.propre(tx.reformulation))) : null,
          [...(tx.miroir || []), ...(tx.pourquoi || [])].map((p) => h('p', null, signeType(p.type), typo(AF.propre(p.texte))))));
      }
    } else {
      const existe = !ctx.special && AF.execution(ctx.e.cas);
      contenu.push(h('p', { class: 'petit' }, 'Aucun appel de modèle pour cette édition : mode hors ligne.', existe ? ` Une exécution réelle avec modèles existe pour la demande de départ de ${AF.nomCas(ctx.e.cas)} ; elle s’affiche quand cette demande est relue.` : ''));
    }
    const obj = d.objections || [];
    if (obj.length) {
      contenu.push(h('h3', { class: 'pc' }, 'Objections du Sceptique, vérifiées par le code'),
        h('ol', { class: 'objections' }, obj.map((o) => h('li', null, h('em', null, o.texte), ' ', h('span', { class: 'issue' }, ISSUES[o.issue] || o.issue),
          approfondi() ? h('span', { class: 'detail' }, ` Recalcul demandé : ${o.recalcul}`) : null,
          h('span', { class: 'detail' }, ' Réponse : ', annoter(o.reponse, b, ctx, [o.cible]))))));
    }
    const q = d.qualite_donnees || [];
    if (q.length) {
      const ok = q.filter((x) => x.statut === 'ok').length;
      contenu.push(h('p', { class: 'petit' }, `Contrôle des données : ${ok} contrôle${pl(ok)} réussi${pl(ok)} sur ${q.length}, avant tout calcul.`));
      if (approfondi()) contenu.push(h('ul', { class: 'regles' }, q.map((x) => h('li', { class: `regle ${x.statut === 'ok' ? 'ok' : 'rouge'}` },
        h('div', { class: 'regle-ligne' }, h('span', { class: 'signe', 'aria-hidden': 'true' }, x.statut === 'ok' ? '✓' : '✕'), h('span', { class: 'lib' }, x.libelle), h('span', { class: 'points', 'aria-hidden': 'true' }), h('span', { class: 'niv' }, x.statut === 'ok' ? 'réussi' : x.statut)),
        h('p', { class: 'expl' }, x.detail)))));
    }
    return section('journal', 'VI', 'Ce qui a été fait pour écrire cette page', composer(b, contenu));
  }

  /* Relecture des étapes enregistrées : jamais présentée comme un travail en direct. */
  function arreterRelecture() { if (ui.arret) { ui.arret(); ui.arret = null; } }
  function relireJournal(liste, d, depart, surFin) {
    arreterRelecture();
    if (!liste.isConnected) return;
    const items = [...liste.children];
    const etiq = (li, txt) => { const e = li.querySelector('.etat-etape'); if (e) e.textContent = txt; };
    liste.classList.add('en-relecture');
    items.forEach((li, i) => { li.classList.remove('en_cours', 'fait', 'echec'); if (i < depart) { li.classList.add('fait'); etiq(li, '(déjà faite, non refaite)'); } else etiq(li, '(en attente)'); });
    annoncer(`Relecture des ${items.length} étapes enregistrées${depart ? `, à partir de l’étape ${depart + 1}` : ''}.`);
    ui.arret = AF.relireTrace(d, (i, phase) => {
      if (phase === 'fin') { ui.arret = null; liste.classList.remove('en-relecture'); annoncer('Fin de la relecture des étapes enregistrées.'); if (surFin) surFin(); return; }
      if (i < depart || !items[i]) return;
      items[i].classList.toggle('en_cours', phase === 'en_cours');
      items[i].classList.toggle('fait', phase === 'fait');
      etiq(items[i], phase === 'en_cours' ? '(relecture en cours)' : '(faite)');
      if (phase === 'en_cours') annoncer(`Étape ${i + 1} sur ${items.length} : ${d.trace[i].agent}.`);
    }, reduit() ? 3 : 1);
  }

  /* ------------------------------------------------------------------ VII. Limites */
  function sectionLimites(ctx) {
    const { d } = ctx, b = new Bloc('limites'), lim = (d.texte && d.texte.limites) || [];
    const item = (l) => h('li', null, h('span', { class: `signe-type ${l.type}`, 'aria-hidden': 'true' }), h('span', null, h('span', { class: 'sr-only' }, `${AF.TYPES[l.type] || l.type} : `), annoter(l.texte, b, ctx, l.faits, { souple: true })));
    const contenu = [h('p', { class: 'chapeau' }, T('Ce que ces chiffres ne disent pas. Le passé décrit le passé : rien ici ne prévoit l’avenir.', 'Limites et réserves, mêmes faits qu’en lecture essentielle, toutes dépliées.'))];
    if (!lim.length) contenu.push(h('p', { class: 'vide' }, 'Le dossier n’énonce pas de limite.'));
    else if (approfondi() || lim.length <= 3) contenu.push(h('ul', { class: 'limites' }, lim.map(item)));
    else {
      contenu.push(h('ul', { class: 'limites' }, lim.slice(0, 3).map(item)),
        h('details', { class: 'limites-plus' }, h('summary', null, `Lire les ${lim.length - 3} autres limites`), h('ul', { class: 'limites' }, lim.slice(3).map(item))));
    }
    if (d.texte && d.texte.avertissement) contenu.push(h('p', { class: 'chapeau' }, d.texte.avertissement));
    return section('limites', 'VII', T('Les limites', 'Limites et réserves'), composer(b, contenu));
  }

  /* ------------------------------------------------------------------ Annexe (Approfondi) : tous les faits */
  function annexeFaits(ctx) {
    const fs = ctx.d.faits || [];
    const table = h('table', { class: 'tableau empile' },
      h('caption', null, 'Tous les faits du dossier, valeur exacte. La méthode et les références se déplient sous chaque fait.'),
      h('thead', null, h('tr', null, h('th', { scope: 'col' }, 'N°'), h('th', { scope: 'col' }, 'Fait'), h('th', { scope: 'col' }, 'Valeur exacte'), h('th', { scope: 'col' }, 'Type'), h('th', { scope: 'col' }, 'Source'))),
      h('tbody', null, fs.map((f) => h('tr', null,
        h('th', { scope: 'row' }, h('span', { class: 'id' }, f.id)),
        h('td', { 'data-label': 'Fait' }, libCourt(f.libelle), h('details', null, h('summary', null, 'méthode et références'), h('p', null, typo(f.methode || '—')), listeReferences(f.references))),
        h('td', { 'data-label': 'Valeur' }, valeurExacte(f) || typo(String(f.valeur))),
        h('td', { 'data-label': 'Type' }, signeType(f.type, true)),
        h('td', { 'data-label': 'Source' }, f.source)))));
    const sec = section('faits', 'VIII', `Annexe : tous les faits (${fs.length})`, h('div', { class: 'bloc' }, h('div', { class: 'texte pleine' }, fs.length ? h('div', { class: 'tableau-cadre' }, table) : h('p', { class: 'vide' }, 'Aucun fait dans ce dossier.'))));
    return sec;
  }

  /* ------------------------------------------------------------------ Cas limite hors univers, états de démonstration */
  function pageHorsUnivers() {
    const r = F.speciaux.hors_univers;
    return [
      h('header', { class: 'bloc entete' },
        h('div', { class: 'texte' }, h('p', { class: 'kicker' }, h('span', { class: 'pc' }, 'Cas limite'), ' · demande refusée'),
          h('h1', { class: 'phrase' }, 'Une demande hors de l’univers du produit.'),
          h('p', { class: 'ses-mots' }, 'Ce cas n’a pas de phrase d’origine : le produit refuse avant toute analyse.')),
        h('div', { class: 'marge' })),
      h('section', { class: 'erratum', 'aria-labelledby': 'hu-t' },
        h('h2', { id: 'hu-t' }, `Réponse du produit · statut ${r.statut}`),
        h('p', null, `« ${r.message} »`),
        h('p', null, 'Aucun verdict, aucune règle, aucun chiffre : rien n’est composé pour remplir la page.'),
        h('p', { class: 'petit' }, 'Saisir un autre placement n’est pas réalisé dans ce prototype.')),
    ];
  }

  function pageDemo(ctx) {
    const d = ctx.d, liste = listeJournal(d), items = [...liste.children];
    const iSceptique = Math.max(0, (d.trace || []).findIndex((t) => t.agent === 'Sceptique'));
    const attente = h('div', { class: 'lignes-attente', 'aria-hidden': 'true' }, h('span'), h('span'), h('span'), h('span'));
    if (ui.demo === 'chargement') {
      setTimeout(() => relireJournal(liste, d, 0, () => { ui.demo = 'normal'; rendre(); annoncer('Épreuve composée : le dossier est lisible.'); }), 0);
      return [h('section', { class: 'composition', 'aria-labelledby': 'demo-t' }, h('h2', { id: 'demo-t' }, 'Épreuve en cours de composition'),
        h('p', { class: 'petit' }, 'Démonstration : relecture des étapes enregistrées pour ce dossier, au rythme de leurs durées mesurées. Ce n’est pas un calcul en direct.'), liste), attente];
    }
    if (ui.demo === 'erreur') {
      liste.classList.add('en-relecture');
      items.forEach((li, i) => {
        const e = li.querySelector('.etat-etape');
        if (i < iSceptique) { li.classList.add('fait'); e.textContent = '(faite)'; }
        else if (i === iSceptique) { li.classList.add('echec'); e.textContent = '(n’a pas abouti : exemple de démonstration)'; }
        else e.textContent = '(non lancée)';
      });
      return [h('section', { class: 'erratum', 'aria-labelledby': 'demo-t' }, h('h2', { id: 'demo-t' }, 'Erratum · démonstration'),
        h('p', null, 'Exemple : l’étape « Sceptique » n’a pas abouti. Rien de réel n’a échoué ; cet état montre comment la page le dirait.'),
        h('p', null, 'Les étapes précédentes restent valides. Aucun avis n’est affiché tant que les vérifications ne sont pas faites : un verdict incomplet ne doit pas se lire comme un verdict.'),
        h('p', null, 'La dernière édition relue reste accessible dans les éditions ; rien n’est perdu.'),
        h('div', { class: 'actions' }, bouton('Reprendre à partir du Sceptique', () => changerDemo('reprise'), 'demo-reprendre', 'plein'), bouton('Voir les éditions', ouvrirEditions, 'demo-editions')),
        liste)];
    }
    setTimeout(() => relireJournal(liste, d, iSceptique, () => { ui.demo = 'normal'; rendre(); annoncer('Reprise terminée : le dossier est lisible.'); }), 0);
    return [h('section', { class: 'composition', 'aria-labelledby': 'demo-t' }, h('h2', { id: 'demo-t' }, 'Reprise · démonstration'),
      h('p', { class: 'petit' }, `Les ${iSceptique} premières étapes ne sont pas refaites ; la relecture reprend au Sceptique. Démonstration : aucune interruption réelle n’a eu lieu.`), liste), attente];
  }

  /* ------------------------------------------------------------------ Pied de feuille */
  function rendrePied() {
    const d = ui.special && ui.special !== 'hors_univers' ? F.speciaux[ui.special].dossier : (ui.special ? null : AF.dossier());
    const demo = h('fieldset', { class: 'demo' }, h('legend', null, 'États de démonstration, pas des états réels'),
      h('div', { class: 'choix' }, Object.keys(DEMOS).map((k) => h('label', null,
        h('input', { type: 'radio', name: 'demo', value: k, 'data-k': `demo-${k}`, checked: ui.demo === k, onchange: () => changerDemo(k) }), DEMOS[k]))));
    $('#pied').replaceChildren(
      h('h2', null, 'Autres directions'),
      h('ul', { class: 'directions' }, DIRECTIONS.map((x) => h('li', null, h('a', { href: AF.lien(`../${x.d}/index.html`) }, x.nom))), h('li', null, h('a', { href: AF.lien('../index.html') }, 'Galerie'))),
      h('h2', null, 'États de l’interface'),
      demo,
      h('h2', null, 'Colophon'),
      h('p', null, `Composé en Iowan Old Style ou, à défaut, Palatino ou Georgia. Données : ${AF.meta.mode}. Dossiers générés le ${String(AF.meta.genere_le).replace('T', ' à ')} (commit ${AF.meta.commit}).`),
      h('p', null, AF.meta.avertissement, d && d.texte && d.texte.avertissement ? ` ${d.texte.avertissement}` : ''),
      h('p', null, bouton('Recommencer le carnet', recommencer, 'recommencer')));
  }

  /* ------------------------------------------------------------------ Colophon collant */
  function rendreColophon() {
    const c = $('#colophon');
    const statut = ui.special ? 'special' : AF.statut();
    c.className = `colophon ${statut}`;
    const hist = AF.historique(), pos = AF.position(), r = hist[pos], der = hist.length - 1;
    const lecture = h('p', { class: 'lecture' }), outils = h('div', { class: 'outils' });
    if (statut === 'special') {
      remplir(lecture, [h('span', { class: 'statut' }, 'cas limite'), 'hors éditions, lecture seule']);
      outils.append(bouton('Revenir au carnet', quitterSpecial, 'col-quitter'));
    } else if (statut === 'apercu') {
      remplir(lecture, [h('span', { class: 'statut' }, 'épreuve corrigée'), typo(AF.decrire(AF.etat(), AF.brouillon())), h('em', null, ' · non relue')]);
      outils.append(bouton('Relire avec cette correction', appliquer, 'col-appliquer', 'rouge'), bouton('Abandonner', () => AF.abandonner(), 'col-abandonner'));
    } else {
      remplir(lecture, [h('span', { class: 'statut' }, statut === 'archive' ? 'archive' : 'édition courante'), ord(pos + 1), ` édition · relue à ${heure(r.heure)}`,
        statut === 'archive' ? [' · la dernière est la ', ord(der + 1)] : null]);
      outils.append(
        h('button', { type: 'button', class: 'btn', 'data-k': 'col-annuler', disabled: !AF.peutAnnuler(), onclick: () => AF.annuler() }, h('span', { 'aria-hidden': 'true' }, '↶'), 'Annuler'),
        h('button', { type: 'button', class: 'btn', 'data-k': 'col-retablir', disabled: !AF.peutRetablir(), onclick: () => AF.retablir() }, h('span', { 'aria-hidden': 'true' }, '↷'), 'Rétablir'),
        bouton(`Éditions (${hist.length})`, ouvrirEditions, 'col-editions'));
    }
    c.replaceChildren(h('div', { class: 'colophon-in' }, lecture, outils));
  }

  /* ------------------------------------------------------------------ Éditions (historique) */
  function ouvrirEditions() {
    const dlg = $('#editions');
    rendreEditions();
    if (!dlg.open) { if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', ''); }
    const f = $('[data-k="ed-fermer"]', dlg);
    if (f) f.focus();
  }
  function fermerEditions() { const dlg = $('#editions'); if (dlg.open) { if (typeof dlg.close === 'function') dlg.close(); else dlg.removeAttribute('open'); } }
  function rendreEditions() {
    const dlg = $('#editions'), hist = AF.historique(), der = hist.length - 1;
    dlg.replaceChildren(
      h('div', { class: 'ed-tete' }, h('h2', { id: 'editions-titre' }, 'Éditions de ce carnet'), bouton('Fermer', fermerEditions, 'ed-fermer')),
      h('div', { class: 'ed-corps' },
        h('p', { class: 'ed-intro' }, 'Chaque relecture produit une édition. Rien ne s’efface : restaurer une édition en crée une nouvelle, identique, à la fin de la liste.'),
        h('ol', null, hist.map((r) => h('li', { class: 'ed' },
          h('div', { class: 'ed-ligne' }, h('span', { class: 'ed-num' }, ord(r.i + 1), ' édition'), h('span', { class: 'ed-heure' }, heure(r.heure)), etatMini(r.verdict),
            r.courant ? h('span', { class: 'ed-tag' }, 'affichée') : null, r.i === der ? h('span', { class: 'ed-tag' }, 'dernière') : null),
          h('span', { class: 'ed-motif' }, `${r.nom} · ${typo(r.motif)}`, r.parent >= 0 ? ` · tirée de la ${ordinal(r.parent + 1)}` : ''),
          h('div', { class: 'ed-actions' },
            !r.courant ? bouton(`Relire la ${ordinal(r.i + 1)}`, () => { fermerEditions(); ui.focusApres = { k: r.i === der ? 'col-editions' : 'arch-derniere', viser: r.i !== der }; AF.allerA(r.i); }, `ed-relire-${r.i}`) : null,
            r.i !== der ? bouton(`Restaurer la ${ordinal(r.i + 1)}`, () => { fermerEditions(); ui.focusApres = { k: 'section-correction', viser: true }; AF.restaurer(r.i); }, `ed-restaurer-${r.i}`) : null)))),
        h('div', { class: 'ed-pied' },
          bouton('Annuler', () => AF.annuler(), 'ed-annuler', null, !AF.peutAnnuler()),
          bouton('Rétablir', () => AF.retablir(), 'ed-retablir', null, !AF.peutRetablir()),
          bouton('Recommencer le carnet', () => { fermerEditions(); recommencer(); }, 'ed-recommencer'))));
  }
  function recommencer() {
    if (window.confirm('Recommencer efface toutes les éditions de ce carnet (et celles des autres prototypes, qui partagent l’historique). Continuer ?')) {
      ui.special = null; ui.demo = 'normal'; AF.reinitialiser();
    }
  }

  /* ------------------------------------------------------------------ Sélecteur ancré au mot */
  let selecteur = null;
  function ouvrirSelecteur(mot, champ) {
    if (selecteur && selecteur.champ === champ) { fermerSelecteur(true); return; }
    fermerSelecteur(false);
    const e = AF.etat(), b = AF.brouillon(), cible = b || e;
    const depart = F.cas[e.cas] ? F.cas[e.cas].depart : '';
    const valeurs = AF.parametres(e.cas)[champ] || [];
    const ordre = champ === 'montant' ? [...valeurs].sort((x, y) => y - x) : valeurs;
    const ul = h('ul', { role: 'listbox', 'aria-label': `Valeurs possibles pour ${CHAMP[champ]}` });
    const choisir = (v) => {
      const k = mot.dataset.k;
      fermerSelecteur(false);
      ui.focusApres = { k, viser: false };
      if (v === cible[champ]) { rendre(); return; }
      if (!AF.proposer({ [champ]: v })) { ui.focusApres = null; annoncer('Cette valeur n’existe pas dans les dossiers précalculés.'); }
    };
    ordre.forEach((v, i) => {
      const relue = v === e[champ], proposee = !!b && v === b[champ] && !relue;
      const deDepart = champ === 'montant' ? depart.startsWith(`m=${v};`) : false;
      const li = h('li', { role: 'option', id: `sel-${i}`, tabindex: '-1', 'aria-selected': String(v === cible[champ]), class: proposee ? 'propose' : null },
        h('span', null, libelleValeur(champ, v, e.cas)),
        h('span', { class: 'marque' }, relue ? 'valeur relue' : proposee ? 'proposée' : deDepart ? 'demande de départ' : ''));
      li.addEventListener('click', () => choisir(v));
      ul.append(li);
    });
    const pop = h('div', { class: 'selecteur', role: 'dialog', 'aria-label': `Corriger ${CHAMP[champ]}` },
      h('p', { class: 'sel-titre' }, `Corriger ${CHAMP[champ]}`), ul,
      h('p', { class: 'sel-note' }, 'Valeurs précalculées par le moteur réel ; aucune autre n’existe dans ce prototype. Choisir ne relance rien : la page devient une épreuve à relire.'));
    document.body.append(pop);
    placer(pop, mot);
    mot.setAttribute('aria-expanded', 'true');
    selecteur = { pop, mot, champ, ul };
    ul.addEventListener('keydown', clavierSelecteur);
    montrer(ul.querySelector('[aria-selected="true"]') || ul.firstElementChild);
  }
  function placer(pop, mot) {
    const rects = mot.getClientRects();
    const r = rects.length ? rects[rects.length - 1] : mot.getBoundingClientRect();
    const premier = rects.length ? rects[0] : r;
    const ul = pop.querySelector('ul');
    const vw = document.documentElement.clientWidth;
    const haut = ($('#tete').getBoundingClientRect().bottom || 0) + 8;
    const bas = window.innerHeight - ($('#colophon').offsetHeight || 0) - 8;
    const autour = pop.offsetHeight - ul.offsetHeight;
    const dessous = bas - (r.bottom + 6), dessus = (premier.top - 6) - haut;
    const enDessous = dessous >= pop.offsetHeight || dessous >= dessus;
    ul.style.maxHeight = `${Math.max(132, Math.floor((enDessous ? dessous : dessus) - autour))}px`;
    const x = Math.max(12, Math.min(r.left, vw - pop.offsetWidth - 12));
    const y = enDessous ? r.bottom + 6 : premier.top - 6 - pop.offsetHeight;
    pop.style.left = `${Math.round(x + window.scrollX)}px`;
    pop.style.top = `${Math.round(y + window.scrollY)}px`;
  }
  /* Montre une option dans la liste sans faire défiler la page. */
  function montrer(li) {
    const ul = li.parentElement;
    li.focus({ preventScroll: true });
    if (li.offsetTop < ul.scrollTop) ul.scrollTop = li.offsetTop;
    else if (li.offsetTop + li.offsetHeight > ul.scrollTop + ul.clientHeight) ul.scrollTop = li.offsetTop + li.offsetHeight - ul.clientHeight;
  }
  function clavierSelecteur(ev) {
    if (!selecteur) return;
    const items = [...selecteur.ul.children];
    let i = items.indexOf(document.activeElement);
    switch (ev.key) {
      case 'ArrowDown': i = Math.min(items.length - 1, i + 1); break;
      case 'ArrowUp': i = Math.max(0, i - 1); break;
      case 'Home': i = 0; break;
      case 'End': i = items.length - 1; break;
      case 'Enter': case ' ': ev.preventDefault(); if (document.activeElement && document.activeElement.click) document.activeElement.click(); return;
      case 'Escape': case 'Tab': ev.preventDefault(); fermerSelecteur(true); return;
      default: return;
    }
    ev.preventDefault();
    montrer(items[i]);
  }
  function fermerSelecteur(rendreFocus) {
    if (!selecteur) return;
    const { pop, mot } = selecteur;
    selecteur = null;
    pop.remove();
    if (mot.isConnected) { mot.setAttribute('aria-expanded', 'false'); if (rendreFocus) mot.focus(); }
  }
  /* Ouvre le sélecteur du mot du titre depuis un autre endroit de la page (profil). */
  function ouvrirDepuis(champ) {
    const mot = document.querySelector(`[data-k="mot-${champ}"]`);
    if (!mot) return;
    mot.scrollIntoView({ block: 'center', behavior: 'auto' });
    mot.focus({ preventScroll: true });
    ouvrirSelecteur(mot, champ);
  }
  /* Propose une correction depuis un encadré ou un tableau, puis ramène le regard sur la phrase corrigée. */
  function proposerDepuis(patch, cle) {
    ui.focusApres = { k: cle, viser: true };
    if (!AF.proposer(patch)) { ui.focusApres = null; annoncer('Cette correction n’existe pas dans les dossiers précalculés.'); }
  }
  function appliquer() { ui.focusApres = { k: 'section-correction', viser: true }; if (!AF.appliquer()) ui.focusApres = null; }

  /* ------------------------------------------------------------------ Situations, cas limites, démonstration */
  function choisirCas(c) {
    ui.special = null; ui.demo = 'normal';
    if (c !== AF.etat().cas) AF.changerCas(c);
    else if (AF.perime()) AF.abandonner();
    else rendre();
  }
  function choisirSpecial(cle) {
    ui.demo = 'normal';
    if (AF.perime()) AF.abandonner();
    ui.special = cle; ui.notesOuvertes.clear();
    rendre();
    annoncer(`Cas limite : ${SPECIAUX.find((x) => x.cle === cle).nom}.`);
  }
  function quitterSpecial() { ui.special = null; ui.notesOuvertes.clear(); ui.focusApres = { k: `cas-${AF.etat().cas}`, viser: false }; rendre(); }
  function changerDemo(k) {
    arreterRelecture();
    ui.demo = k;
    rendre();
    const t = $('#texte');
    t.focus({ preventScroll: true });
    t.scrollIntoView({ block: 'start', behavior: reduit() ? 'auto' : 'smooth' });
    annoncer(k === 'normal' ? 'Retour à l’état normal.' : `État de démonstration : ${DEMOS[k]}.`);
  }

  /* ------------------------------------------------------------------ Annonces et abonnement au socle */
  let minuterieAnnonce = null;
  function annoncer(txt) {
    const z = $('#annonce');
    clearTimeout(minuterieAnnonce);
    z.textContent = '';
    minuterieAnnonce = setTimeout(() => { z.textContent = txt; }, 60);
  }

  function surChangement() {
    const st = AF.statut(), pos = AF.position(), len = AF.historique().length, br = AF.brouillon(), niv = AF.niveau();
    const avant = ui.precedent;
    ui.precedent = { st, pos, len, br: br ? cleEtat(br) : null, niv };
    const deplace = !avant || pos !== avant.pos || len !== avant.len;
    if (deplace) { ui.special = null; ui.notesOuvertes.clear(); ui.demo = 'normal'; }
    else if (br && ui.special) ui.special = null;
    rendre();
    if (!avant) return;
    if (st === 'apercu' && cleEtat(br) !== avant.br) annoncer(`Correction proposée : ${AF.decrire(AF.etat(), br)}. Le texte est une épreuve périmée jusqu’à la relecture.`);
    else if (avant.st === 'apercu' && st !== 'apercu' && !deplace) annoncer('Correction abandonnée : retour à l’édition relue.');
    else if (len > avant.len) { const d = AF.dossier(); annoncer(`${ordinal(pos + 1)} édition relue : ${AF.ETATS[d.verdict.etat].long}, ${d.verdict.respectees} règles respectées sur ${d.verdict.evaluees}.`); }
    else if (pos !== avant.pos) annoncer(st === 'archive' ? `Archive : tu relis la ${ordinal(pos + 1)} édition.` : `Retour à la ${ordinal(pos + 1)} édition, la dernière.`);
    else if (niv !== avant.niv) annoncer(`Lecture ${niv === 'approfondi' ? 'approfondie' : 'essentielle'}.`);
  }

  function init() {
    document.querySelectorAll('.niveau button').forEach((bt) => bt.addEventListener('click', () => { ui.focusApres = { k: `niveau-${bt.dataset.niveau}`, viser: false }; AF.definirNiveau(bt.dataset.niveau); }));
    /* Appel de note : ouvre la note, la montre et y met le focus (un geste). */
    document.addEventListener('click', (ev) => {
      const a = ev.target.closest && ev.target.closest('a.appel');
      if (!a) return;
      const note = document.getElementById(a.dataset.note);
      if (!note) return;
      ev.preventDefault();
      const groupe = note.closest('.notes-groupe');
      if (groupe) groupe.open = true;
      note.open = true;
      ui.notesOuvertes.add(note.id);
      note.classList.add('surligne');
      setTimeout(() => note.classList.remove('surligne'), 1800);
      note.scrollIntoView({ block: 'nearest', behavior: reduit() ? 'auto' : 'smooth' });
      const sm = note.querySelector('summary');
      if (sm) sm.focus({ preventScroll: true });
    });
    document.addEventListener('toggle', (ev) => {
      const t = ev.target;
      if (!t.classList || !t.classList.contains('note')) return;
      if (t.open) ui.notesOuvertes.add(t.id); else ui.notesOuvertes.delete(t.id);
    }, true);
    document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape' && selecteur) { ev.preventDefault(); fermerSelecteur(true); } });
    document.addEventListener('pointerdown', (ev) => { if (selecteur && !selecteur.pop.contains(ev.target) && ev.target !== selecteur.mot) fermerSelecteur(false); });
    let largeur = window.innerWidth;
    window.addEventListener('resize', () => { if (window.innerWidth !== largeur) { largeur = window.innerWidth; fermerSelecteur(false); } });
    const dlg = $('#editions');
    dlg.addEventListener('click', (ev) => { if (ev.target === dlg) fermerEditions(); });
    const majColophon = () => document.documentElement.style.setProperty('--colophon-h', `${$('#colophon').offsetHeight}px`);
    if ('ResizeObserver' in window) new ResizeObserver(majColophon).observe($('#colophon'));
    if (ecranLarge.addEventListener) ecranLarge.addEventListener('change', ouvrirGroupes);
    window.addEventListener('beforeprint', () => document.querySelectorAll('details.limites-plus, details.notes-groupe').forEach((x) => { x.dataset.avantImpression = x.open ? '1' : '0'; x.open = true; }));
    window.addEventListener('afterprint', () => document.querySelectorAll('details.limites-plus, details.notes-groupe').forEach((x) => { if (x.dataset.avantImpression === '0') x.open = false; }));
    AF.abonner(surChangement);
    ui.precedent = { st: AF.statut(), pos: AF.position(), len: AF.historique().length, br: null, niv: AF.niveau() };
    rendre();
    majColophon();
  }
  init();
})();
