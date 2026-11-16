/* Second avis · direction 4 « Fil ».
   Un fil vertical qu'on déroule au pouce. Chaque question « Et si… » ajoute un avis en bas : le fil EST l'historique
   (AF.historique()). Rien n'est effacé ; on revient à un avis par AF.restaurer, on annule par une notification.
   Règle : aucun chiffre n'est calculé ni inventé ici. Tout vient du socle (window.AF) ; l'interface choisit, ordonne,
   arrondit à l'écran et relie chaque chiffre à sa preuve. */
(() => {
  'use strict';

  const AF = window.AF;
  const $ = (s, r = document) => r.querySelector(s);
  if (!AF) { const l = $('#liste-fil'); if (l) l.textContent = 'Socle introuvable : vérifie ../socle/socle.js.'; return; }
  const F = AF.fmt;
  const mouvementReduit = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  const comportement = () => (mouvementReduit.matches ? 'auto' : 'smooth');

  /* Les quatre autres directions (dossiers voisins de celui-ci). */
  const AUTRES = [['1-carnet', 'Carnet'], ['2-relief', 'Relief'], ['3-pupitre', 'Pupitre'], ['5-epure', 'Épure']];
  const ROLES_CODE = new Set(['Contrôle données', 'Analyste', 'Gardien']);
  const NATURES = { donnee: 'Donnée', preference: 'Préférence', contrainte: 'Contrainte', inconnu: 'Inconnue' };
  const SPECIAUX = {
    sans_epargne: 'Sans épargne déclarée',
    impossible: "Montant plus grand que l'épargne",
    hors_univers: 'Actif hors du jeu de données',
  };

  /* ───────────── Construction du DOM (tout texte de données passe par textContent) ───────────── */
  function h(tag, props, ...enfants) {
    const el = document.createElement(tag);
    if (tag === 'button') el.setAttribute('type', 'button');
    if (props) {
      for (const [k, v] of Object.entries(props)) {
        if (v == null || v === false) continue;
        if (k === 'class') el.className = v;
        else if (k === 'svg') el.innerHTML = v; // icônes écrites ci-dessous, jamais des données
        else if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v);
        else el.setAttribute(k, v === true ? '' : String(v));
      }
    }
    poser(el, enfants);
    return el;
  }
  function poser(el, enfants) {
    for (const e of enfants) {
      if (e == null || e === false) continue;
      if (Array.isArray(e)) poser(el, e);
      else el.append(e instanceof Node ? e : document.createTextNode(String(e)));
    }
  }
  const sr = (t) => h('span', { class: 'sr' }, t);

  /* ───────────── Icônes : des formes distinctes, jamais la couleur seule ───────────── */
  const S = (inner) => `<svg viewBox="0 0 24 24" focusable="false">${inner}</svg>`;
  const ICONES = {
    coherent: S('<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M7.2 12.4l3.1 3.1 6.5-6.6" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'),
    ajustement: S('<path d="M10.27 3.5a2 2 0 0 1 3.46 0l8.4 14.6a2 2 0 0 1-1.73 3H3.6a2 2 0 0 1-1.73-3z" fill="currentColor"/><path d="M12 9.2v4.6" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><circle cx="12" cy="17.2" r="1.35" fill="#fff"/>'),
    incoherent: S('<path d="M8.1 2.2h7.8l5.9 5.9v7.8l-5.9 5.9H8.1l-5.9-5.9V8.1z" fill="currentColor" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/><path d="M7.2 12h9.6" stroke="#fff" stroke-width="2.8" stroke-linecap="round"/>'),
    indetermine: S('<circle cx="12" cy="12" r="9.4" fill="none" stroke="currentColor" stroke-width="2.2" stroke-dasharray="3.3 2.5"/><path d="M9.5 9.6a2.6 2.6 0 1 1 3.7 2.4c-.8.4-1.2.9-1.2 1.7v.4" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round"/><circle cx="12" cy="17.1" r="1.3" fill="currentColor"/>'),
    non_evaluee: S('<rect x="3.2" y="3.2" width="17.6" height="17.6" rx="4" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="3 2.4"/><path d="M8 12h8" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>'),
    FAIT: S('<circle cx="12" cy="12" r="6.5" fill="currentColor"/>'),
    HYPOTHESE: S('<circle cx="12" cy="12" r="7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-dasharray="3.2 2.4"/>'),
    SCENARIO: S('<path d="M12 3.6 20.4 12 12 20.4 3.6 12z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M12 8.6 15.4 12 12 15.4 8.6 12z" fill="currentColor"/>'),
    donnee: S('<rect x="5" y="5" width="14" height="14" rx="3" fill="currentColor"/>'),
    preference: S('<circle cx="12" cy="12" r="7.6" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="12" cy="12" r="3.1" fill="currentColor"/>'),
    contrainte: S('<rect x="4.4" y="4.4" width="15.2" height="15.2" rx="3" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M8.2 12h7.6" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>'),
    code: S('<path d="M8.6 6.5 3.8 12l4.8 5.5M15.4 6.5l4.8 5.5-4.8 5.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'),
    modele: S('<path d="M5 4.5h14a2 2 0 0 1 2 2v8.2a2 2 0 0 1-2 2h-6.6L7.5 20.4v-3.7H5a2 2 0 0 1-2-2V6.5a2 2 0 0 1 2-2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'),
    fermer: S('<path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>'),
    retour: S('<path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'),
    menu: S('<path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2.3" stroke-linecap="round"/>'),
    fleche: S('<path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'),
    annuler: S('<path d="M9 6.5 4.5 11 9 15.5" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 11h9.5a5 5 0 0 1 0 10H11" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round"/>'),
    verrou: S('<rect x="5" y="10.5" width="14" height="10" rx="2.5" fill="currentColor"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" fill="none" stroke="currentColor" stroke-width="2.2"/>'),
    lecture: S('<path d="M8 5.5v13l10.5-6.5z" fill="currentColor"/>'),
    plan: S('<circle cx="5.5" cy="6.5" r="1.8" fill="currentColor"/><circle cx="5.5" cy="12" r="1.8" fill="currentColor"/><circle cx="5.5" cy="17.5" r="1.8" fill="currentColor"/><path d="M10 6.5h10M10 12h10M10 17.5h10" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>'),
    archive: S('<rect x="3.5" y="4.5" width="17" height="4.5" rx="1.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M5 9v9.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V9M10 13h4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'),
    perime: S('<path d="M20 12a8 8 0 1 1-2.3-5.6" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round"/><path d="M20 4.5v4.6h-4.6" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>'),
    marque: S('<circle cx="12" cy="12" r="10.5" fill="#1452c4"/><path d="M12 1.5a10.5 10.5 0 0 1 0 21z" fill="#e8322f"/><circle cx="12" cy="12" r="4.2" fill="#fff"/>'),
  };
  const ico = (nom, classe) => h('span', { class: `ico${classe ? ' ' + classe : ''}`, 'aria-hidden': 'true', svg: ICONES[nom] || '' });
  const ICO_ETAT = { coherent: 'coherent', ajustement: 'ajustement', incoherent: 'incoherent', indetermine: 'indetermine' };
  const ICO_NIV = { ok: 'coherent', orange: 'ajustement', rouge: 'incoherent', gris: 'indetermine', non_evaluee: 'non_evaluee' };
  const COUL_NIV = { ok: 'coherent', orange: 'ajustement', rouge: 'incoherent', gris: 'indetermine', non_evaluee: 'indetermine' };

  /* ───────────── État de l'interface (jamais des faits) ───────────── */
  const ui = {
    action: null, // dernière action de la personne : défiler, annoncer, proposer « Annuler »
    connues: new Set(), // cartes déjà affichées : seules les nouvelles « arrivent »
    ouverts: new Set(), fermes: new Set(), // replis ouverts ou fermés à la main
    relecture: null, // { cle, etats[] } pendant une relecture des étapes enregistrées
    demo: 'normal', // états de démonstration : normal, chargement, erreur, reprise
    speciaux: [], numSpecial: 0,
    compA: null, compB: null, compPos: null,
    toastMinuteur: 0, confirmerRaz: false, retourFocus: null, largeur: 0,
  };
  const liste = $('#liste-fil');
  const approfondi = () => AF.niveau() === 'approfondi';

  /* ───────────── Formats d'affichage (l'exact reste dans la preuve) ───────────── */
  const moins = (s) => String(s).replace(/(^|[\s(])-(?=\d)/g, '$1−');
  const decimales = (v) => { const s = String(v); const i = s.indexOf('.'); return i < 0 || /e/i.test(s) ? 0 : s.length - i - 1; };
  function affiche(v, unite) {
    if (typeof v !== 'number' || !isFinite(v)) return v == null ? '—' : String(v);
    const d1 = Number.isInteger(v) ? 0 : 1;
    switch (unite) {
      case '$': return moins(F.cad(v));
      case '%': return moins(F.pct(v, d1));
      case '%/an': return `${moins(F.pct(v, d1))}/an`;
      case 'points': return moins(F.pts(v, 1));
      case 'an(s)': return `${moins(F.nombre(v, d1))} an${Math.abs(v) >= 2 ? 's' : ''}`;
      default: return moins(F.nombre(v, Math.min(2, decimales(v))));
    }
  }
  const exacte = (v, unite) => `${moins(String(v).replace('.', ','))}${unite ? ` ${unite}` : ''}`;
  function valeurCourte(f) {
    if (!f) return '—';
    const v = f.valeur;
    if (typeof v === 'number') return affiche(v, f.unite);
    if (Array.isArray(v)) return `${v.length} éléments`;
    if (v && typeof v === 'object') {
      if (v.debut && v.fin) return `${v.debut} → ${v.fin}`;
      return Object.entries(v).map(([k, x]) => `${k} ${typeof x === 'number' ? moins(F.nombre(x, Math.min(2, decimales(x)))) : x}`).join(' · ');
    }
    const s = String(v);
    return s.length > 70 ? `${s.slice(0, 68)}…` : s;
  }
  const heure = (t) => { try { return new Date(t).toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' }); } catch (e) { return ''; } };
  const compteTexte = (v) => (v && v.evaluees ? `${v.respectees} règle${v.respectees > 1 ? 's' : ''} respectée${v.respectees > 1 ? 's' : ''} sur ${v.evaluees}` : 'Aucune règle évaluée');
  const etatLong = (e) => (AF.ETATS[e] ? AF.ETATS[e].long : e);
  const etatCourt = (e) => (AF.ETATS[e] ? AF.ETATS[e].court : e);
  const libExclusion = (x) => (x ? "avec l'exclusion Énergie" : "sans l'exclusion Énergie");

  function resumeEtat(e) {
    const P = AF.parametres(e.cas), t = [F.cad(e.montant)];
    if (P.retrait.length > 1 || e.retrait != null) t.push(`retrait ${F.retrait(e.retrait)}`);
    if (P.exclusion.length > 1) t.push(e.exclusion ? 'exclusion Énergie' : 'sans exclusion');
    return t.join(' · ');
  }
  /* La question posée, à la première personne, telle qu'elle apparaît dans la bulle. */
  function questionEtSi(a, b) {
    const p = [];
    if (a.cas !== b.cas) p.push(`on parlait de ${AF.nomCas(b.cas)}`);
    if (a.montant !== b.montant) p.push(`je mettais ${F.cad(b.montant)} au lieu de ${F.cad(a.montant)}`);
    if (a.retrait !== b.retrait) p.push(b.retrait == null ? 'je ne précisais pas de date de retrait' : `je prévoyais un retrait ${F.retrait(b.retrait)}`);
    if (a.exclusion !== b.exclusion) p.push(b.exclusion ? "je gardais l'exclusion du secteur Énergie" : "j'enlevais l'exclusion du secteur Énergie");
    return p.length ? `Et si ${p.join(' et si ')} ?` : 'Même question, posée à nouveau';
  }

  /* À quel cas appartient un dossier (pour la source du profil et l'exécution réelle). */
  const casCache = new WeakMap();
  function casDe(d) {
    if (!d || typeof d !== 'object') return null;
    if (casCache.has(d)) return casCache.get(d);
    let trouve = null;
    for (const c of AF.cas()) { const V = AF.donnees.cas[c].variantes; for (const k in V) if (V[k] === d) trouve = c; }
    casCache.set(d, trouve);
    return trouve;
  }
  const estDepart = (d, cas) => !!cas && d === AF.donnees.cas[cas].variantes[AF.donnees.cas[cas].depart];

  /* ───────────── Pastilles : forme + libellé ───────────── */
  const pEtat = (etat) => h('span', { class: `pastille c-${etat}` }, ico(ICO_ETAT[etat] || 'indetermine'), h('span', null, etatCourt(etat)));
  const pNiveau = (niv, vide) => (niv == null
    ? h('span', { class: 'pastille c-indetermine' }, ico('non_evaluee'), h('span', null, vide || 'Non évaluée'))
    : h('span', { class: `pastille c-${COUL_NIV[niv] || 'indetermine'}` }, ico(ICO_NIV[niv] || 'non_evaluee'), h('span', null, AF.NIVEAUX_REGLE[niv] || niv)));
  const pType = (t) => (t ? h('span', { class: `pastille type type-${t}` }, ico(t), h('span', null, AF.TYPES[t] || t)) : null);
  const pNature = (n) => h('span', { class: `nature nature-${n}` }, ico(n === 'inconnu' ? 'indetermine' : n), h('span', null, NATURES[n] || n));

  /* ───────────── Texte riche : chaque chiffre devient un bouton vers sa preuve ───────────── */
  function champsProfil(d) {
    const p = (d && d.profil) || {}, ev = p.evaluation || {}, dm = (d && d.demande) || {};
    return [
      ['demande.montant_cad', 'Montant de ta demande', dm.montant_cad, 'cad'],
      ['epargne_totale_cad', 'Épargne totale', p.epargne_totale_cad, 'cad'],
      ['somme_a_preserver_cad', 'Somme à ne jamais risquer', p.somme_a_preserver_cad, 'cad'],
      ['horizon_ans', 'Horizon du placement', p.horizon_ans, 'ans'],
      ['retrait_prevu_ans', 'Retrait prévu', p.retrait_prevu_ans, 'ans'],
      ['evaluation.tolerance', 'Ce que tu dis vouloir risquer (sur 100)', ev.tolerance, 'score'],
      ['evaluation.capacite', 'Ce que ta situation permet (sur 100)', ev.capacite, 'score'],
      ['evaluation.score_retenu', 'Score retenu (sur 100)', ev.score_retenu, 'score'],
      ['evaluation.poids_pct', 'Part de ton épargne dans ce placement', ev.poids_pct, 'pct'],
      ['evaluation.perte_max_tolerance_pct', 'Perte maximale selon ta tolérance', ev.perte_max_tolerance_pct, 'pct'],
      ['evaluation.perte_max_capacite_pct', 'Perte maximale selon ta situation', ev.perte_max_capacite_pct, 'pct'],
      ['evaluation.perte_max_retenue_pct', 'Perte maximale retenue', ev.perte_max_retenue_pct, 'pct'],
      ['evaluation.seuil_concentration_pct', 'Seuil de concentration (actif très volatil)', ev.seuil_concentration_pct, 'pct'],
      ['evaluation.seuil_titre_unique_pct', 'Seuil pour un seul titre', ev.seuil_titre_unique_pct, 'pct'],
    ].filter((c) => typeof c[2] === 'number').map(([cle, libelle, valeur, cat]) => ({ cle, libelle, valeur, cat }));
  }
  const afficheChamp = (c) => (c.cat === 'cad' ? F.cad(c.valeur) : c.cat === 'pct' ? F.pct(c.valeur, Number.isInteger(c.valeur) ? 0 : 1) : c.cat === 'ans' ? F.retrait(c.valeur).replace('dans ', '') : `${F.nombre(c.valeur)} / 100`);

  const categorie = (u) => (!u ? null : /%|point|pts/.test(u) ? 'pct' : /\$|CAD/.test(u) ? 'cad' : /100/.test(u) ? 'score' : /an/.test(u) ? 'ans' : null);
  const catFait = (u) => (u === '%' || u === '%/an' || u === 'points' ? 'pct' : u === '$' ? 'cad' : u === 'an(s)' ? 'ans' : null);
  const compatible = (cat, f) => !cat || catFait(f.unite) === cat;
  const feuilles = (v) => (typeof v === 'number' ? [v] : v && typeof v === 'object' ? Object.values(v).filter((x) => typeof x === 'number') : []);
  const arrondi = (x, d) => Math.round(x * 10 ** d) / 10 ** d;
  const proche = (a, b) => Math.abs(a - b) < 1e-9 * Math.max(1, Math.abs(b));

  /* Rattacher un nombre écrit à sa source : d'abord les faits que la phrase cite, puis le profil, puis la valeur exacte
     d'un autre fait du dossier. Rien n'est deviné au-delà : sinon le chiffre est dit « sans fait rattaché ». */
  function rattacher(nb, dec, unite, ctx) {
    if (!isFinite(nb) || !ctx.d) return null;
    const cat = categorie(unite);
    const vaut = (v) => feuilles(v).some((x) => proche(arrondi(x, dec), nb) || proche(arrondi(Math.abs(x), dec), Math.abs(nb)));
    for (const id of ctx.faits || []) { const f = AF.fait(id, ctx.d); if (f && compatible(cat, f) && vaut(f.valeur)) return { genre: 'fait', id, mode: 'cite' }; }
    if (ctx.strict || (!unite && !dec)) return null;
    const champs = champsProfil(ctx.d).filter((c) => (!cat || c.cat === cat) && vaut(c.valeur));
    if (champs.length) return { genre: 'profil', champs };
    if (dec > 0 || Math.abs(nb) >= 100) for (const f of ctx.d.faits || []) if (compatible(cat, f) && vaut(f.valeur)) return { genre: 'fait', id: f.id, mode: 'valeur' };
    return null;
  }

  const RE_JETON = new RegExp([
    '(\\d{4}-\\d{2}-\\d{2}(?:\\s?→\\s?\\d{4}-\\d{2}-\\d{2})?|\\d{4}\\s?[-–]\\s?\\d{4}|\\d{4}-\\d{2}(?!\\d))', // dates : texte
    '(\\(?\\bF-\\d+\\b\\)?)', // renvoi explicite à un fait
    '((?:[-−]\\s?)?(?:\\d{1,3}(?:[ \\u00a0\\u202f]\\d{3})+|\\d+)(?:[.,]\\d+)?)(\\s?(?:%\\/an|%|\\$|CAD\\b|points?\\b|pts\\b|an\\(s\\)|ans\\b|an\\b|\\/\\s?100|sur 100))?',
  ].join('|'), 'g');

  function ctxDe(d, faits, origine, strict) { return { d, faits: faits || [], origine: origine || '', strict: !!strict, cas: casDe(d), n: 0, relies: 0 }; }

  function texteRiche(texte, ctx) {
    const frag = document.createDocumentFragment();
    const brut = String(texte || '').replace(/\s+$/, '');
    let dernier = 0, m;
    RE_JETON.lastIndex = 0;
    while ((m = RE_JETON.exec(brut))) {
      if (m.index > dernier) frag.append(brut.slice(dernier, m.index));
      dernier = RE_JETON.lastIndex;
      if (m[1]) { frag.append(m[1]); continue; }
      if (m[2]) {
        const id = /F-\d+/.exec(m[2])[0], k = m[2].indexOf(id);
        frag.append(m[2].slice(0, k), AF.fait(id, ctx.d) ? boutonFait(id, ctx.d, id, 'renvoi') : id, m[2].slice(k + id.length));
        continue;
      }
      const jeton = m[3], unite = m[4] || '';
      const nb = parseFloat(jeton.replace(/[\s  ]/g, '').replace('−', '-').replace(',', '.'));
      const dec = (/[.,](\d+)$/.exec(jeton) || ['', ''])[1].length;
      const lien = rattacher(nb, dec, unite.trim(), ctx);
      const vu = moins(AF.propre(jeton.replace('.', ','))) + unite;
      if (!lien && (ctx.strict || (!unite && !dec))) { frag.append(vu); continue; }
      ctx.n += 1;
      if (lien) ctx.relies += 1;
      frag.append(boutonChiffre(vu, lien, ctx, brut));
    }
    if (dernier < brut.length) frag.append(brut.slice(dernier));
    return frag;
  }
  function boutonChiffre(txt, lien, ctx, phrase) {
    if (lien && lien.genre === 'fait') return boutonFait(lien.id, ctx.d, txt, null, lien.mode);
    if (lien && lien.genre === 'profil') {
      return h('button', { class: 'chiffre ch-profil', 'aria-label': `${txt} : donnée de ton profil`, onclick: () => ouvrirFeuille(() => contenuProfil(lien.champs, ctx.d), 'Donnée de ton profil') }, txt);
    }
    return h('button', { class: 'chiffre ch-libre', 'aria-label': `${txt} : d'où vient ce chiffre`, onclick: () => ouvrirFeuille(() => contenuLibre(txt, phrase, ctx), "D'où vient ce chiffre") }, txt);
  }
  function boutonFait(id, d, texte, classe, mode) {
    const f = AF.fait(id, d);
    if (!f) return texte;
    return h('button', {
      class: `${classe || 'chiffre'} ch-fait ch-${f.type}`,
      'aria-label': `${texte} : preuve, fait ${id}`,
      onclick: () => ouvrirFait(id, d, mode),
    }, texte);
  }
  function compteChiffres(ctx) {
    if (!approfondi() || !ctx.n) return null;
    return h('p', { class: 'compte-chiffres' }, `Chiffres reliés à un fait ou à ton profil : ${ctx.relies} sur ${ctx.n}`);
  }

  /* ───────────── Feuille basse (dialog natif) ───────────── */
  const feuille = $('#feuille');
  const pile = [];
  function ouvrirFeuille(rendu, titre) {
    if (!feuille.open) { pile.length = 0; ui.retourFocus = document.activeElement; }
    pile.push({ rendu, titre });
    dessinerFeuille();
    if (!feuille.open) { try { feuille.showModal(); } catch (e) { feuille.setAttribute('open', ''); } }
    $('#feuille-titre').focus();
  }
  function dessinerFeuille() {
    const haut = pile[pile.length - 1];
    if (!haut) return;
    $('#feuille-titre').textContent = haut.titre;
    $('#feuille-retour').hidden = pile.length < 2;
    $('#feuille-corps').replaceChildren(haut.rendu());
    $('#feuille-corps').scrollTop = 0;
  }
  const fermerFeuille = () => { if (feuille.open) feuille.close(); };
  const redessinerFeuilleOuverte = () => { if (feuille.open && pile.length) dessinerFeuille(); };

  function blocReferences(ids) {
    const refs = [...new Set(ids || [])].map((r) => AF.reference(r)).filter(Boolean);
    if (!refs.length) return h('p', { class: 'petit' }, 'Aucune référence liée.');
    return h('details', { class: 'refs' }, h('summary', null, `Références (${refs.length})`, ico('retour', 'chevron')),
      h('ul', { class: 'refs-liste' }, refs.map((r) => h('li', { class: 'ref' },
        h('p', { class: 'ref-type' }, r.type),
        h('p', { class: 'ref-titre' }, r.titre),
        h('p', { class: 'ref-meta' }, [r.auteurs, r.annee, r.publication].filter(Boolean).join(' · ')),
        r.apport ? h('p', null, h('strong', null, 'Apport : '), r.apport) : null,
        r.examen ? h('p', { class: 'ref-examen' }, h('strong', null, 'Examen : '), r.examen) : null,
        r.lien ? h('a', { href: r.lien, target: '_blank', rel: 'noopener noreferrer', class: 'lien' }, 'Ouvrir la source', sr(' (nouvel onglet)')) : h('p', { class: 'petit' }, 'Pas de lien public.')))));
  }
  const boutonRefs = (ids, titre) => ((ids || []).length
    ? h('button', { class: 'bouton tertiaire petit-bouton', onclick: () => ouvrirFeuille(() => h('div', { class: 'preuve' }, blocReferences(ids)), titre || 'Références') }, `Références (${new Set(ids).size})`)
    : null);
  const puceFaits = (ids, d) => h('ul', { class: 'puces-faits' }, [...new Set(ids)].filter((id) => AF.fait(id, d)).map((id) => h('li', null, boutonFait(id, d, `${id} · ${valeurCourte(AF.fait(id, d))}`, 'puce-fait'))));

  function valeurExacteNoeud(f) {
    const v = f.valeur;
    if (typeof v === 'number') return exacte(v, f.unite === 'fraction' ? '(fraction)' : f.unite);
    if (Array.isArray(v)) return h('ul', { class: 'liste-texte' }, v.map((x) => h('li', null, String(x))));
    if (v && typeof v === 'object') return h('dl', { class: 'preuve-objet' }, Object.entries(v).map(([k, x]) => [h('dt', null, k), h('dd', null, typeof x === 'number' ? exacte(x, '') : String(x))]));
    return String(v);
  }
  function contenuFait(id, d, mode) {
    const f = AF.fait(id, d);
    if (!f) return h('p', null, `Le fait ${id} n'existe pas dans ce dossier.`);
    const arr = typeof f.valeur === 'number' ? affiche(f.valeur, f.unite) : null;
    return h('div', { class: 'preuve' },
      h('p', { class: 'preuve-id' }, h('span', { class: 'id-fait' }, `Fait ${f.id}`), pType(f.type)),
      h('div', { class: `preuve-valeur${typeof f.valeur === 'number' ? '' : ' preuve-valeur-texte'}` }, valeurExacteNoeud(f)),
      arr && arr !== exacte(f.valeur, f.unite) ? h('p', { class: 'petit' }, `Valeur exacte ci-dessus ; à l'écran, arrondie : ${arr}`) : null,
      h('dl', { class: 'preuve-dl' },
        h('dt', null, 'Type'), h('dd', null, AF.TYPES[f.type] || f.type),
        h('dt', null, 'Source'), h('dd', null, f.source || '—'),
        h('dt', null, 'Méthode'), h('dd', null, f.methode || '—'),
        h('dt', null, 'Obtenu'), h('dd', null, f.lu_ou_calcule === 'lu' ? 'Lu tel quel' : f.lu_ou_calcule === 'calcule' ? 'Calculé' : (f.lu_ou_calcule || '—'))),
      mode === 'valeur' ? h('p', { class: 'note' }, 'Rattaché par sa valeur exacte : la phrase ne cite pas ce fait par son numéro.') : null,
      blocReferences(f.references));
  }
  const ouvrirFait = (id, d, mode) => ouvrirFeuille(() => contenuFait(id, d, mode), (AF.fait(id, d) || {}).libelle || id);

  function sourceProfil(d) {
    const cas = casDe(d);
    return cas ? `Profil fictif du scénario · ${AF.donnees.cas[cas].source_profil}` : 'Profil fictif d\'un cas particulier de démonstration';
  }
  function contenuProfil(champs, d) {
    return h('div', { class: 'preuve' },
      h('p', null, champs.length > 1 ? 'Ce chiffre correspond à plusieurs données de ton profil ; la phrase ne dit pas laquelle :' : 'Ce chiffre vient de ton profil ou de son évaluation, pas des prix du marché.'),
      h('dl', { class: 'preuve-dl' }, champs.map((c) => [h('dt', null, c.libelle), h('dd', null, h('span', { class: 'preuve-valeur-ligne' }, moins(afficheChamp(c))), approfondi() ? h('code', { class: 'champ' }, c.cle) : null)])),
      h('dl', { class: 'preuve-dl' }, h('dt', null, 'Source'), h('dd', null, sourceProfil(d))),
      h('p', { class: 'petit' }, ico('verrou'), ' Lecture seule dans ce prototype, sauf ce que propose « Et si… ».'));
  }
  function contenuLigne(l, d) {
    const P = casDe(d) ? AF.parametres(casDe(d)) : null;
    const modifiable = P && ((l.cle === 'retrait' && P.retrait.length > 1) || (l.cle === 'exclusions' && P.exclusion.length > 1));
    return h('div', { class: 'preuve' },
      h('p', { class: 'preuve-id' }, pNature(l.nature)),
      h('div', { class: 'preuve-valeur preuve-valeur-texte' }, l.valeur == null ? 'Non précisé' : l.valeur),
      l.valeur == null ? h('p', null, 'Tu ne l\'as pas dit. Le produit ne suppose rien à ta place : cette ligne reste inconnue.') : null,
      h('dl', { class: 'preuve-dl' },
        h('dt', null, 'Nature'), h('dd', null, NATURES[l.nature] || l.nature),
        l.note ? [h('dt', null, 'Note'), h('dd', null, l.note)] : null,
        h('dt', null, 'Source'), h('dd', null, sourceProfil(d)),
        h('dt', null, 'Modifier'), h('dd', null, modifiable ? 'Par la barre « Et si… », en bas.' : 'Lecture seule dans ce prototype.')));
  }
  function contenuLibre(txt, phrase, ctx) {
    return h('div', { class: 'preuve' },
      h('div', { class: 'preuve-valeur' }, txt),
      h('p', null, 'Ce chiffre figure dans une phrase écrite à partir du dossier, mais le dossier ne le rattache à aucun fait numéroté ni à une donnée de ton profil.'),
      h('dl', { class: 'preuve-dl' },
        h('dt', null, 'Phrase'), h('dd', null, `« ${AF.propre(phrase)} »`),
        h('dt', null, 'Origine'), h('dd', null, ctx.origine || '—')),
      (ctx.faits || []).length ? [h('p', { class: 'petit' }, 'Faits cités par cette phrase :'), puceFaits(ctx.faits, ctx.d)] : null);
  }
  function contenuChamp(txt, chemin, valeur) {
    return h('div', { class: 'preuve' },
      h('div', { class: 'preuve-valeur' }, exacte(valeur, '$')),
      h('dl', { class: 'preuve-dl' }, h('dt', null, 'Où, dans le dossier'), h('dd', null, chemin), h('dt', null, 'Fait rattaché'), h('dd', null, 'Aucun : valeur rendue telle quelle par le moteur.')));
  }
  const boutonChamp = (txt, chemin, valeur) => h('button', { class: 'chiffre ch-libre', 'aria-label': `${txt} : d'où vient ce chiffre`, onclick: () => ouvrirFeuille(() => contenuChamp(txt, chemin, valeur), "D'où vient ce chiffre") }, txt);

  function contenuCompte(d) {
    const v = d.verdict || {};
    return h('div', { class: 'preuve' },
      h('p', null, v.evaluees ? `Le Gardien a évalué ${v.evaluees} règles ; ${v.respectees} sont respectées.` : 'Aucune règle n\'a pu être évaluée.'),
      h('ul', { class: 'liste-regles' }, (d.regles || []).map((r) => h('li', null, pNiveau(r.niveau), h('span', null, r.libelle)))),
      h('p', { class: 'petit' }, ico('code'), ' Le Gardien est du code : il décide seul du verdict, aucun modèle ne le fait.'));
  }

  function listeAppels(appels) {
    return h('ul', { class: 'appels' }, appels.map((a) => h('li', { class: 'appel' },
      h('p', { class: 'appel-tete' }, ico('modele'), h('strong', null, a.agent), ` · ${a.modele}`),
      h('dl', { class: 'preuve-dl compact' },
        h('dt', null, 'Identifiant de requête'), h('dd', null, h('code', null, a.request_id)),
        h('dt', null, 'Jetons'), h('dd', null, `${F.nombre(a.jetons_entree)} en entrée · ${F.nombre(a.jetons_sortie)} en sortie`),
        h('dt', null, 'Latence'), h('dd', null, `${F.nombre(a.latence_ms)} ms`),
        h('dt', null, 'Garde-fou'), h('dd', null, a.garde_fou === 'configure' ? 'configuré' : a.garde_fou),
        a.stop_reason ? [h('dt', null, 'Fin'), h('dd', null, a.stop_reason)] : null))));
  }
  function contenuAppels(cas) {
    const x = AF.execution(cas);
    if (!x) return h('p', null, 'Aucune exécution réelle enregistrée pour cette situation.');
    return h('div', { class: 'preuve' },
      h('p', null, h('span', { class: 'badge-relecture' }, 'relecture'), ` Exécution réellement enregistrée pour la demande de départ de ${AF.nomCas(cas)}. Rien n'est rappelé maintenant.`),
      listeAppels(x.appels_modele || []),
      h('h3', { class: 'h-section' }, 'Durées enregistrées par étape'),
      h('ul', { class: 'durees' }, (x.trace || []).map((t) => h('li', null, ico(ROLES_CODE.has(t.agent) ? 'code' : 'modele'), h('span', null, t.agent), h('span', { class: 'num' }, F.ms(t.duree_ms))))),
      h('dl', { class: 'preuve-dl' }, h('dt', null, 'Fichier de preuve'), h('dd', null, h('code', null, x.source))),
      h('p', { class: 'petit' }, 'Aucun de ces appels ne décide du verdict : le Gardien est du code.'));
  }
  function objections(d) {
    const O = d.objections || [];
    if (!O.length) return null;
    const ISSUE = { confirmee: 'confirmée par le recalcul', ecartee: 'écartée par le recalcul', limite: 'limite notée' };
    return h('div', null, h('h3', { class: 'h-section' }, `Objections du Sceptique (${O.length})`),
      h('ol', { class: 'objections' }, O.map((o) => h('li', null,
        h('p', null, h('strong', null, o.texte)),
        h('p', { class: 'petit' }, `Vérification demandée : ${o.recalcul}`),
        h('p', null, texteRiche(o.reponse, ctxDe(d, [o.cible], `Objection ${o.id}`))),
        h('p', { class: 'issue' }, ISSUE[o.issue] || o.issue)))));
  }
  function qualite(d) {
    const Q = d.qualite_donnees || [];
    if (!Q.length) return null;
    return h('div', null, h('h3', { class: 'h-section' }, `Contrôles des données (${Q.length})`),
      h('ul', { class: 'liste-regles' }, Q.map((q) => h('li', null, pNiveau(q.statut === 'ok' ? 'ok' : 'gris', q.statut), h('span', null, `${q.libelle} — ${q.detail}`)))));
  }
  function contenuEtape(t, d) {
    const cas = casDe(d), code = ROLES_CODE.has(t.agent);
    const role = (AF.donnees.sources.agents || {})[t.agent];
    const x = cas && estDepart(d, cas) ? AF.execution(cas) : null;
    const reel = x ? (x.trace || []).find((e) => e.agent === t.agent) : null;
    const appels = x ? (x.appels_modele || []).filter((a) => a.agent === t.agent) : [];
    const ids = [...new Set(t.faits || [])];
    return h('div', { class: 'preuve' },
      h('p', { class: 'preuve-id' }, h('span', { class: `pastille genre-${code ? 'code' : 'modele'}` }, ico(code ? 'code' : 'modele'), h('span', null, code ? 'Code' : 'Rôle de modèle'))),
      role ? h('p', null, role.role) : null,
      h('dl', { class: 'preuve-dl' },
        h('dt', null, 'Action'), h('dd', null, t.action),
        h('dt', null, 'Détail enregistré'), h('dd', null, texteRiche(t.detail, ctxDe(d, ids, `Étape ${t.agent}`))),
        h('dt', null, 'Durée, ce dossier (hors ligne)'), h('dd', null, `${t.duree_ms} ms`),
        reel ? [h('dt', null, 'Durée, exécution réelle enregistrée'), h('dd', null, `${reel.duree_ms} ms`)] : null),
      appels.length ? [h('h3', { class: 'h-section' }, 'Appel réel enregistré (demande de départ)'), listeAppels(appels)] : null,
      t.agent === 'Sceptique' ? objections(d) : null,
      t.agent === 'Contrôle données' ? qualite(d) : null,
      ids.length ? [h('h3', { class: 'h-section' }, `Faits produits ou utilisés (${ids.length})`), puceFaits(ids, d)] : null,
      blocReferences(t.references || (role && role.references) || []));
  }
  const ouvrirEtape = (t, d) => ouvrirFeuille(() => contenuEtape(t, d), `Étape : ${t.agent}`);
  function contenuEtapes(d) {
    return h('div', { class: 'preuve' },
      h('p', null, "Étapes enregistrées pour cet avis. Le calcul a eu lieu hors ligne : aucun appel de modèle."),
      h('ol', { class: 'etapes' }, (d.trace || []).map((t, i) => ligneEtape(t, i, d, 'fait'))));
  }
  function contenuSerie(fa, fb, d) {
    const k = d.comparaison || {};
    const lim = (k.limites || []).find((l) => /fenêtres historiques/i.test(l));
    const ligne = (lib, f) => (f ? [h('dt', null, lib), h('dd', null, `rendement ${exacte(f.rendement_pct, '%')} · pire baisse ${exacte(f.pire_chute_pct, '%')}`)] : null);
    return h('div', { class: 'preuve' },
      h('p', null, `Du ${fa.debut} au ${fa.fin}. Mesuré sur le passé, sans probabilité attachée.`),
      h('dl', { class: 'preuve-dl' }, ligne('Sans ta demande', fa), ligne('Avec ta demande', fb),
        h('dt', null, 'Source'), h('dd', null, `Séries du dossier, moteur ${k.moteur || '—'} (${k.version_moteur || '—'}) : ${k.politique || ''}`)),
      lim ? h('p', { class: 'note' }, lim) : null);
  }

  /* ───────────── Petits éléments communs ───────────── */
  function li(cle, classe, ...contenu) { return h('li', { 'data-cle': cle, class: classe || null }, contenu); }
  function plie(cle, defaut, resume, ...contenu) {
    const ouvert = ui.ouverts.has(cle) ? true : ui.fermes.has(cle) ? false : defaut;
    const d = h('details', { class: 'plie', open: ouvert }, h('summary', null, h('span', { class: 'plie-resume' }, resume), ico('retour', 'chevron')), h('div', { class: 'plie-corps' }, contenu));
    d.addEventListener('toggle', () => { if (d.open) { ui.ouverts.add(cle); ui.fermes.delete(cle); } else { ui.fermes.add(cle); ui.ouverts.delete(cle); } });
    return d;
  }
  const surTitre = (texte, id) => h('p', { class: 'sur-titre', id: id || null }, texte);
  const rubanPerime = (r) => (AF.perime() ? h('p', { class: 'ruban-perime' }, ico('perime'), `Périmé : correspond à l'avis n°${r.i + 1}, pas à ta question en attente.`) : null);
  function tableFaits(ids, d, titre) {
    const fs = [...new Set(ids || [])].map((id) => AF.fait(id, d)).filter(Boolean);
    if (!fs.length) return null;
    return h('div', { class: 'faits-carte' }, h('p', { class: 'h-section' }, titre || 'Faits de cette carte'),
      h('ul', { class: 'faits' }, fs.map((f) => h('li', null,
        h('span', { class: 'fait-id' }, f.id),
        h('span', { class: 'fait-lib' }, f.libelle),
        boutonFait(f.id, d, valeurCourte(f)),
        pType(f.type)))));
  }
  function proposerEtSi(patch) {
    ui.action = { type: 'proposer' };
    if (!AF.proposer(patch)) { ui.action = null; toast("Cette combinaison n'a pas été précalculée : non réalisé dans ce prototype."); }
  }
  const titreRegle = (r) => (!approfondi() && AF.LEXIQUE[r.code] ? AF.terme(r.code).titre : r.libelle);

  /* ───────────── Cartes du fil ───────────── */
  function separateur(r, rang) {
    const p = AF.dossierDe(r.etat).profil || {};
    return li(`chap-${r.i}`, 'li-chap', h('p', { class: 'chapitre' },
      h('span', null, rang === 0 ? 'Situation' : 'Autre situation'),
      h('strong', null, [p.nom, p.age ? `${p.age} ans` : null].filter(Boolean).join(', '))));
  }

  function carteDemande(d, cle) {
    const p = d.profil || {}, dm = d.demande || {};
    return li(cle, 'li-bulle',
      h('article', { class: 'bulle bulle-demande', 'aria-labelledby': `t-${cle}` },
        h('p', { class: 'sur-titre', id: `t-${cle}` }, 'Ta demande'),
        h('blockquote', { class: 'demande-texte' }, h('p', null, `« ${dm.texte || '—'} »`)),
        h('p', { class: 'demande-qui' }, [p.nom, p.age ? `${p.age} ans` : null, p.profession].filter(Boolean).join(' · ')),
        (p.citations || []).length ? [h('p', { class: 'sur-titre sur-titre-2' }, 'Tu as aussi dit'), h('ul', { class: 'citations' }, p.citations.map((c) => h('li', null, `« ${c} »`)))] : null),
      h('p', { class: 'demande-montant' }, 'Montant analysé : ',
        typeof dm.montant_cad === 'number' ? h('button', { class: 'chiffre ch-profil', 'aria-label': `${F.cad(dm.montant_cad)} : donnée de ta demande`, onclick: () => ouvrirFeuille(() => contenuProfil(champsProfil(d).filter((c) => c.cle === 'demande.montant_cad'), d), 'Donnée de ta demande') }, F.cad(dm.montant_cad)) : '—',
        dm.ticker ? ` · ${dm.ticker}` : ''));
  }

  function carteCompris(d, cle, special) {
    const cas = casDe(d), P = cas ? AF.parametres(cas) : null, e = AF.etat();
    const lignes = AF.profilLignes(d);
    const app = approfondi();
    const ctx = ctxDe(d, [], 'Reformulation de ta demande');
    const reform = d.texte && d.texte.reformulation;
    const modifiables = ['le montant'];
    if (P && P.retrait.length > 1) modifiables.push('la date de retrait');
    if (P && P.exclusion.length > 1) modifiables.push("l'exclusion Énergie");
    const modifiable = (l) => !!P && ((l.cle === 'retrait' && P.retrait.length > 1) || (l.cle === 'exclusions' && P.exclusion.length > 1));
    const etSiLigne = (l) => {
      if (special || !modifiable(l) || cas !== e.cas) return null;
      if (l.cle === 'retrait') { const x = P.retrait.find((v) => v !== e.retrait); return h('button', { class: 'mini-etsi', 'data-fk': `ligne-${cle}-retrait`, onclick: () => proposerEtSi({ retrait: x }) }, `Et si : ${F.retrait(x)}`); }
      return h('button', { class: 'mini-etsi', 'data-fk': `ligne-${cle}-exclusion`, onclick: () => proposerEtSi({ exclusion: !e.exclusion }) }, `Et si : ${libExclusion(!e.exclusion)}`);
    };
    const ligne = (l) => h('li', { class: `ligne ligne-${l.nature}` },
      h('span', { class: 'ligne-lib' }, l.libelle, modifiable(l) ? null : h('span', { class: 'lecture-seule', title: 'Lecture seule dans ce prototype' }, ico('verrou'), sr(' (lecture seule)'))),
      h('span', { class: 'ligne-val' }, l.valeur == null
        ? h('button', { class: 'inconnu-val', onclick: () => ouvrirFeuille(() => contenuLigne(l, d), l.libelle) }, 'Non précisé', sr(' : rien n\'est supposé à ta place'))
        : h('button', { class: 'chiffre ch-profil', 'aria-label': `${l.valeur} : d'où vient cette ligne`, onclick: () => ouvrirFeuille(() => contenuLigne(l, d), l.libelle) }, l.valeur)),
      pNature(l.nature),
      etSiLigne(l),
      app && l.note ? h('span', { class: 'ligne-note' }, l.note) : null);
    /* Essentiel : les lignes qui pèsent (inconnues, contraintes, modifiables, épargne, horizon, tolérance) ; le reste replié. */
    const CLES = ['epargne', 'horizon', 'tolerance'];
    const visibles = app ? lignes : lignes.filter((l) => l.nature === 'inconnu' || l.nature === 'contrainte' || modifiable(l) || CLES.includes(l.cle));
    const autres = app ? [] : lignes.filter((l) => !visibles.includes(l));
    const idsH = d.demande && d.demande.ids_faits ? ['h_perte', 'h_capacite', 'h_concentration', 'h_retrait_proche', 'h_volatil'].map((k) => d.demande.ids_faits[k]).filter(Boolean) : [];
    return li(cle, null, h('article', { class: 'carte compris', 'aria-labelledby': `t-${cle}` },
      surTitre("Ce qu'on a compris", `t-${cle}`),
      reform ? h('p', { class: 'reformulation' }, texteRiche(reform, ctx)) : null,
      h('ul', { class: 'lignes' }, visibles.map(ligne)),
      autres.length ? h('div', { class: 'lignes-plus' }, plie(`${cle}-plus`, false, `${autres.length} autres lignes`, h('ul', { class: 'lignes' }, autres.map(ligne)))) : null,
      lignes.some((l) => l.nature === 'inconnu') ? h('p', { class: 'note note-inconnu' }, ico('indetermine'), ' Une ligne « inconnue » reste inconnue : rien n\'est supposé à ta place.') : null,
      special ? null : h('p', { class: 'petit' }, ico('verrou'), ` Se change par « Et si… » : ${modifiables.join(', ')}. Le reste est en lecture seule dans ce prototype.`),
      (d.profil && d.profil.tensions || []).length ? h('div', { class: 'tensions' }, h('p', { class: 'h-section' }, 'À noter'), h('ul', null, d.profil.tensions.map((t) => h('li', null, texteRiche(t, ctxDe(d, [], 'Tension repérée')))))) : null,
      app && d.profil && d.profil.extraits ? h('p', { class: 'petit' }, `Lecture de ta phrase : ${d.profil.extraits.source}.`) : null,
      app ? tableFaits(idsH, d, "Seuils de l'équipe appliqués à ton profil") : null,
      compteChiffres(ctx)));
  }

  const LIB_ETAPE = { attente: 'en attente', en_cours: 'relecture…', fait: 'fait', conserve: 'conservée', echec: 'échec', non_lance: 'non lancée' };
  function ligneEtape(t, i, d, etat) {
    const code = ROLES_CODE.has(t.agent);
    return h('li', { class: `etape etape-${etat} ${code ? 'est-code' : 'est-modele'}`, 'data-etape': i },
      h('button', { class: 'etape-bouton', onclick: () => ouvrirEtape(t, d) },
        h('span', { class: 'etape-noeud' }, ico(code ? 'code' : 'modele')),
        h('span', { class: 'etape-txt' },
          h('span', { class: 'etape-nom' }, t.agent),
          h('span', { class: 'etape-genre' }, code ? 'code' : 'modèle'),
          approfondi() ? h('span', { class: 'etape-action' }, t.action) : null),
        h('span', { class: 'etape-droite' },
          h('span', { class: 'etape-duree' }, F.ms(t.duree_ms)),
          h('span', { class: 'etape-statut' }, LIB_ETAPE[etat] || etat))));
  }
  function carteTravail(d, cle) {
    const etapes = d.trace || [];
    if (!etapes.length) return null;
    const cas = casDe(d), x = cas ? AF.execution(cas) : null, depart = estDepart(d, cas);
    const R = ui.relecture && ui.relecture.cle === cle ? ui.relecture : null;
    const nbAppels = (d.appels_modele || []).length;
    return li(cle, null, h('article', { class: 'carte travail', 'aria-labelledby': `t-${cle}` },
      h('div', { class: 'travail-tete' }, surTitre('Le travail', `t-${cle}`), R ? h('span', { class: 'badge-relecture' }, 'relecture') : null),
      h('p', { class: 'travail-chapeau' }, `${etapes.length} étapes enregistrées. `, h('span', { class: 'legende-genre' }, ico('code'), ' code'), ' ou ', h('span', { class: 'legende-genre' }, ico('modele'), ' modèle'), ' ; durées de ce dossier, calculé hors ligne.'),
      h('ol', { class: 'etapes' }, etapes.map((t, i) => ligneEtape(t, i, d, R ? R.etats[i] : 'fait'))),
      h('div', { class: 'travail-pied' },
        h('p', null, nbAppels ? `${nbAppels} appels de modèle pour cet avis.` : 'Appels de modèle pour cet avis : aucun (mode hors ligne).'),
        x ? h('p', null, `Une exécution réelle de la demande de départ a été enregistrée : ${(x.appels_modele || []).length} appels de modèle${depart ? '' : ' (pour ce montant-ci, seul le calcul hors ligne existe)'}.`) : null,
        h('div', { class: 'rangee-boutons' },
          h('button', { class: 'bouton secondaire', 'data-fk': `relire-${cle}`, disabled: !!R, onclick: () => lancerRelecture(cle, d) }, ico('lecture'), R ? 'Relecture en cours…' : 'Relire les étapes', sr(' (relecture des étapes enregistrées)')),
          x ? h('button', { class: 'bouton tertiaire', onclick: () => ouvrirFeuille(() => contenuAppels(cas), 'Appels réels enregistrés') }, ico('modele'), 'Appels réels') : null),
        h('p', { class: 'petit' }, 'Une relecture rejoue les étapes enregistrées ; ce n\'est pas un calcul en direct.'))));
  }

  function picto(etat) { return h('span', { class: 'avis-picto' }, ico(ICO_ETAT[etat] || 'indetermine')); }
  function articleAvis(d, r, role, cle) {
    const v = d.verdict || {}, etat = v.etat || 'indetermine';
    const compact = role === 'precedent' || role === 'suivant';
    const perime = (role === 'actuel' || role === 'relu') && AF.perime();
    const H = AF.historique();
    const classes = ['carte', 'avis', `thermo-${etat}`, `c-${etat}`, compact ? 'compact' : '', role === 'relu' ? 'relu' : '', perime ? 'perime' : ''].filter(Boolean).join(' ');
    const libRole = { actuel: 'Avis actuel', relu: 'Archive relue', precedent: 'Avis précédent', suivant: 'Avis plus récent', special: 'Cas particulier · hors historique' }[role];
    const tid = `t-${cle}`;
    const tete = h('div', { class: 'avis-tete' },
      h('span', { class: 'etiq-opaque' }, 'Le second avis', r ? ` · n°${r.i + 1}` : ''),
      h('span', { class: `etiq-opaque role role-${role}` }, role === 'relu' ? ico('archive') : role === 'actuel' ? h('span', { class: 'point-actuel', 'aria-hidden': 'true' }) : null, libRole),
      r && !compact ? h('span', { class: 'etiq-opaque heure' }, heure(r.heure)) : null);
    const compte = h('button', { class: 'lien-compte', onclick: () => ouvrirFeuille(() => contenuCompte(d), 'Le compte des règles') }, compteTexte(v));

    if (compact) {
      return h('article', { class: classes, 'data-avis': r.i, 'aria-labelledby': tid }, tete,
        h('div', { class: 'avis-plaque' },
          h('h3', { class: 'avis-verdict-c', id: tid }, ico(ICO_ETAT[etat] || 'indetermine'), h('span', null, etatLong(etat))),
          h('p', { class: 'avis-params' }, resumeEtat(r.etat), ' · ', compte),
          h('div', { class: 'rangee-boutons' },
            h('button', { class: 'bouton secondaire', onclick: () => { ui.action = { type: 'restaurer', depuis: r.i }; AF.restaurer(r.i); } }, ico('annuler'), 'Revenir à cet avis'),
            h('button', { class: 'bouton tertiaire', onclick: () => { ui.action = { type: 'aller', depuis: AF.position() }; AF.allerA(r.i); } }, 'Relire'))));
    }

    const regles = d.regles || [], nonOk = regles.filter((x) => x.niveau !== 'ok');
    const questions = d.questions || [];
    const cas = casDe(d), P = cas ? AF.parametres(cas) : null;
    const repondre = P && r && etat !== 'indetermine' && r.etat.retrait == null && P.retrait.some((x) => x != null) && r.i === AF.position()
      ? P.retrait.filter((x) => x != null).map((x) => h('button', { class: 'bouton secondaire', 'data-fk': `repondre-${x}`, onclick: () => proposerEtSi({ retrait: x }) }, `Et si le retrait était ${F.retrait(x)} ?`))
      : null;
    const dernier = H.length - 1;
    return h('article', { class: classes, 'data-avis': r ? r.i : null, 'aria-labelledby': tid }, tete,
      h('div', { class: 'avis-plaque' },
        perime ? h('p', { class: 'notice-perime', role: 'note' }, ico('perime'), h('span', null, h('strong', null, 'Ce résultat ne correspond plus à ta question.'), ' Touche « Voir l\'avis » pour l\'analyser.')) : null,
        role === 'relu' ? h('p', { class: 'tampon' }, ico('archive'), `Archive : avis n°${r.i + 1}, relu. Le plus récent est le n°${dernier + 1}.`) : null,
        h('div', { class: 'avis-ligne' }, picto(etat), h('h2', { class: 'avis-verdict', id: tid, tabindex: '-1' }, etatLong(etat))),
        nonOk.length ? h('ul', { class: 'raisons' }, nonOk.map((x) => h('li', { class: `raison c-${COUL_NIV[x.niveau]}` }, ico(ICO_NIV[x.niveau] || 'non_evaluee'), h('span', null, h('strong', null, `${AF.NIVEAUX_REGLE[x.niveau]} : `), x.niveau === 'gris' ? AF.propre(x.explication) : titreRegle(x)))))
          : v.evaluees ? h('p', { class: 'raisons-ok' }, 'Toutes les règles évaluées sont respectées.') : null,
        questions.length ? h('div', { class: etat === 'indetermine' ? 'conditionnel manque' : 'conditionnel' },
          h('p', { class: 'conditionnel-titre' }, ico('indetermine'), etat === 'indetermine' ? 'Il manque une information' : 'Avis conditionnel : il dépend d\'une réponse'),
          questions.map((q) => h('p', null, texteRiche(q, ctxDe(d, [], 'Question du Profileur et du Gardien')))),
          repondre ? h('div', { class: 'rangee-boutons' }, repondre) : (etat === 'indetermine' ? h('p', { class: 'non-realise' }, 'Répondre ici : non réalisé dans ce prototype.') : null)) : null,
        h('p', { class: 'avis-compte' }, compte),
        h('p', { class: 'avis-gardien' }, ico('code'), ' Décidé par le Gardien : du code, pas un modèle.'),
        r && (d.trace || []).length ? h('p', { class: 'avis-pied' }, h('button', { class: 'lien-discret', onclick: () => ouvrirFeuille(() => contenuEtapes(d), `Étapes de l'avis n°${r.i + 1}`) }, `Calculé en ${d.trace.length} étapes, hors ligne · voir`)) : null,
        role === 'relu' ? h('div', { class: 'rangee-boutons' },
          h('button', { class: 'bouton primaire', onclick: () => { ui.action = { type: 'aller', depuis: AF.position() }; AF.allerA(dernier); } }, `Revenir au plus récent (n°${dernier + 1})`),
          h('button', { class: 'bouton secondaire', onclick: () => { ui.action = { type: 'restaurer', depuis: r.i }; AF.restaurer(r.i); } }, ico('annuler'), 'Reprendre cet avis')) : null));
  }
  function carteAvis(d, r, role) {
    const cle = `avis-${r.i}`;
    return li(cle, `li-avis c-${(d.verdict || {}).etat || 'indetermine'}${role === 'precedent' || role === 'suivant' ? ' li-retrait' : ''}`, articleAvis(d, r, role, cle));
  }

  function bulleEtSi(r, H) {
    const p = r.parent != null && r.parent >= 0 ? H[r.parent] : null;
    const m = /^Retour à la révision (\d+)/.exec(r.motif || '');
    const t = m ? `Revenir à l'avis n°${m[1]}` : p && p.etat.cas === r.etat.cas ? questionEtSi(p.etat, r.etat) : (r.motif || 'Nouvelle question');
    return li(`q-${r.i}`, 'li-bulle', h('p', { class: 'bulle bulle-q' }, sr('Ta question : '), t), h('p', { class: 'bulle-heure' }, heure(r.heure)));
  }

  function diffProfil(dA, dB) {
    const a = AF.profilLignes(dA), b = AF.profilLignes(dB);
    return b.map((l) => ({ l, x: a.find((y) => y.cle === l.cle) })).filter(({ l, x }) => x && (x.valeur !== l.valeur || x.nature !== l.nature));
  }
  function valeurMesure(dX, cle, v, unite) {
    const id = dX.comparaison && dX.comparaison.faits ? dX.comparaison.faits[`apres_${cle}`] : null;
    const txt = unite === '$' ? moins(F.cad(v)) : moins(F.pct(v, 1));
    return id ? boutonFait(id, dX, txt) : txt;
  }
  function carteChangement(r, H) {
    const p = r.parent != null && r.parent >= 0 ? H[r.parent] : null;
    if (!p || p.etat.cas !== r.etat.cas) return null;
    const c = AF.comparer(p.etat, r.etat);
    const dA = AF.dossierDe(p.etat), dB = AF.dossierDe(r.etat);
    const regles = c.regles.filter((x) => x.change);
    const mes = c.mesures.filter((x) => x.avant !== x.apres && x.avant != null);
    const prof = diffProfil(dA, dB);
    const cle = `chg-${r.i}`;
    return li(cle, null, h('article', { class: 'carte changement', 'aria-labelledby': `t-${cle}` },
      surTitre(`Ce qui a changé · depuis l'avis n°${p.i + 1}`, `t-${cle}`),
      h('p', { class: 'chg-motif' }, r.motif),
      h('div', { class: 'chg-verdict' }, pEtat(c.verdict.avant), ico('fleche', 'fl'), pEtat(c.verdict.apres), h('span', { class: 'chg-tag' }, c.verdict.change ? 'avis changé' : 'avis inchangé')),
      prof.length ? h('ul', { class: 'chg-liste' }, prof.map(({ l, x }) => h('li', null, h('span', { class: 'chg-lib' }, l.libelle),
        h('span', { class: 'chg-de' }, x.valeur == null ? 'non précisé' : x.valeur, ' ', pNature(x.nature)), ico('fleche', 'fl'), h('span', { class: 'chg-a' }, l.valeur == null ? 'non précisé' : l.valeur, ' ', pNature(l.nature))))) : null,
      regles.length ? h('ul', { class: 'chg-liste' }, regles.map((x) => h('li', null, h('span', { class: 'chg-lib' }, x.libelle), pNiveau(x.avant, 'Non évaluée'), ico('fleche', 'fl'), pNiveau(x.apres, 'Plus évaluée'))))
        : h('p', { class: 'petit' }, 'Aucune règle ne change de niveau.'),
      mes.length ? h('ul', { class: 'chg-liste' }, mes.map((x) => h('li', null, h('span', { class: 'chg-lib' }, x.titre), h('span', { class: 'num' }, valeurMesure(dA, x.cle, x.avant, x.unite)), ico('fleche', 'fl'), h('span', { class: 'num' }, valeurMesure(dB, x.cle, x.apres, x.unite)))))
        : h('p', { class: 'petit' }, 'Mesures du portefeuille : inchangées.')));
  }

  function carteMiroir(d, r) {
    const M = (d.texte && d.texte.miroir) || [];
    if (!M.length) return null;
    const cle = `mir-${r ? r.i : 'x'}`;
    const ctxs = M.map((x) => ctxDe(d, x.faits, 'Miroir : tes mots face au dossier'));
    return li(cle, null, h('article', { class: 'carte miroir', 'aria-labelledby': `t-${cle}` },
      r ? rubanPerime(r) : null,
      surTitre('Tes mots, face au dossier', `t-${cle}`),
      M.map((x, k) => h('div', { class: 'miroir-ligne' }, h('p', { class: 'miroir-texte' }, texteRiche(x.texte, ctxs[k])), pType(x.type))),
      ctxs.map(compteChiffres)));
  }

  function carteRegle(x, d, r, rang, total, cleForcee) {
    const cle = cleForcee || `reg-${r ? r.i : 'x'}-${x.code}`;
    const app = approfondi(), t = AF.LEXIQUE[x.code] ? AF.terme(x.code) : null;
    const ctx = ctxDe(d, x.faits, `Règle « ${x.libelle} »`);
    return li(cle, null, h('article', { class: `carte regle c-${COUL_NIV[x.niveau] || 'indetermine'}`, 'aria-labelledby': `t-${cle}` },
      r ? rubanPerime(r) : null,
      surTitre(`Pourquoi · ${rang} sur ${total}`),
      h('div', { class: 'regle-tete' }, h('span', { class: 'regle-picto' }, ico(ICO_NIV[x.niveau] || 'non_evaluee')),
        h('div', null, h('h3', { id: `t-${cle}` }, titreRegle(x)), h('p', { class: 'regle-niveau' }, AF.NIVEAUX_REGLE[x.niveau] || x.niveau))),
      !app && t && t.titre !== x.libelle ? h('p', { class: 'petit' }, `Règle « ${x.libelle} »`) : null,
      app && t ? h('p', { class: 'petit' }, h('strong', null, `${t.titre} : `), t.def) : null,
      h('p', { class: 'regle-texte' }, texteRiche(x.explication, ctx)),
      h('div', { class: 'regle-pied' }, pType(x.type), boutonRefs(x.references, `Références : ${x.libelle}`)),
      app ? tableFaits(x.faits, d) : null,
      compteChiffres(ctx)));
  }
  function carteReglesOk(oks, d, r) {
    if (!oks.length) return null;
    const cle = `regok-${r ? r.i : 'x'}`;
    return li(cle, null, h('article', { class: 'carte regles-ok', 'aria-labelledby': `t-${cle}` },
      r ? rubanPerime(r) : null,
      surTitre('Pourquoi · le reste', `t-${cle}`),
      plie(cle, approfondi(), `${oks.length} règle${oks.length > 1 ? 's' : ''} respectée${oks.length > 1 ? 's' : ''}`,
        h('ul', { class: 'regles-mini' }, oks.map((x) => {
          const ctx = ctxDe(d, x.faits, `Règle « ${x.libelle} »`);
          return h('li', { class: 'regle-mini c-coherent' }, ico('coherent'),
            h('div', null, h('p', { class: 'regle-mini-titre' }, titreRegle(x)), h('p', null, texteRiche(x.explication, ctx)),
              h('div', { class: 'regle-pied' }, pType(x.type), boutonRefs(x.references, `Références : ${x.libelle}`)),
              approfondi() ? tableFaits(x.faits, d) : null));
        })))));
  }

  /* Deux colonnes appariées : la même mesure, sans puis avec la demande. L'écart est le message. */
  function paire(m, d, baisse) {
    const ids = (d.comparaison && d.comparaison.faits) || {};
    const fa = ids[`avant_${m.cle}`], fb = ids[`apres_${m.cle}`], fe = ids[`ecart_${m.cle}`];
    const max = Math.max(Math.abs(m.avant), Math.abs(m.apres)) || 1;
    const unite = m.cle === 'volatilite' ? '%/an' : '%';
    const col = (v, id, lib, cls) => h('div', { class: `col ${cls}` },
      h('div', { class: 'col-piste', 'aria-hidden': 'true' }, h('div', { class: 'col-barre', style: `--h:${(Math.abs(v) / max * 100).toFixed(1)}%` })),
      h('div', { class: 'col-val' }, id ? boutonFait(id, d, affiche(v, unite)) : affiche(v, unite)),
      h('div', { class: 'col-lib' }, lib));
    const sens = baisse
      ? { aggrave: 'baisse plus profonde', ameliore: 'baisse moins profonde', neutre: 'baisse inchangée' }[m.sens] || ''
      : m.ecart > 0 ? 'variations plus amples' : m.ecart < 0 ? 'variations moins amples' : 'inchangée';
    const app = approfondi();
    return h('figure', { class: `paire ${baisse ? 'paire-baisse' : 'paire-hausse'}` },
      h('figcaption', { class: 'paire-titre' }, m.titre),
      h('div', { class: 'paire-cols' },
        col(m.avant, fa, app ? 'Avant (sans la demande)' : 'Sans ta demande', 'col-avant'),
        col(m.apres, fb, app ? 'Après (avec la demande)' : 'Avec ta demande', 'col-apres')),
      h('p', { class: 'ecart' }, h('span', { class: 'ecart-lib' }, AF.terme('ecart').titre, ' : '),
        fe ? boutonFait(fe, d, moins(F.pts(m.ecart, 1))) : moins(F.pts(m.ecart, 1)), sens ? ` · ${sens}` : ''));
  }

  function courbe(d, largeur) {
    const sp = d.series_portefeuille, k = d.comparaison;
    if (!sp || !sp.avant || sp.avant.length < 2 || !sp.apres || !k || !k.disponible) return null;
    const W = Math.max(260, Math.round(largeur)), Hh = 196, g = 46, dr = 8, ht = 12, bs = 28;
    const t = (s) => Date.parse(`${s}T00:00:00Z`);
    const t0 = t(sp.avant[0][0]), t1 = t(sp.avant[sp.avant.length - 1][0]);
    const creux = Math.min(...sp.avant.map((p) => p[2]), ...sp.apres.map((p) => p[2]), k.avant.pire_chute_pct, k.apres.pire_chute_pct);
    const pas = Math.abs(creux) <= 25 ? 5 : Math.abs(creux) <= 60 ? 10 : 20;
    const bas = -(Math.ceil(Math.abs(creux) / pas) * pas || pas);
    const x = (s) => g + ((t(s) - t0) / (t1 - t0)) * (W - g - dr);
    const y = (v) => ht + (v / bas) * (Hh - ht - bs);
    const chemin = (pts) => pts.map((p, i) => `${i ? 'L' : 'M'}${x(p[0]).toFixed(1)},${y(p[2]).toFixed(1)}`).join('');
    let s = '';
    for (let v = 0; v >= bas; v -= pas) s += `<line class="grille" x1="${g}" x2="${W - dr}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}"/><text class="axe" x="${g - 6}" y="${(y(v) + 4).toFixed(1)}" text-anchor="end">${v === 0 ? '0 %' : moins(F.pct(v, 0))}</text>`;
    const a0 = new Date(t0).getUTCFullYear(), a1 = new Date(t1).getUTCFullYear();
    for (let a = a0 + 1; a <= a1; a++) { const xa = x(`${a}-01-01`).toFixed(1); s += `<line class="tic" x1="${xa}" x2="${xa}" y1="${Hh - bs}" y2="${Hh - bs + 5}"/><text class="axe" x="${xa}" y="${Hh - 8}" text-anchor="middle">${a}</text>`; }
    const pA = chemin(sp.apres), fin = sp.apres[sp.apres.length - 1][0];
    s += `<path class="aire" d="${pA}L${x(fin).toFixed(1)},${y(0).toFixed(1)}L${x(sp.apres[0][0]).toFixed(1)},${y(0).toFixed(1)}Z"/>`;
    s += `<path class="ligne-avant" d="${chemin(sp.avant)}"/><path class="ligne-apres" d="${pA}"/>`;
    s += `<line class="fin" x1="${(W - dr).toFixed(1)}" x2="${(W - dr).toFixed(1)}" y1="${ht - 4}" y2="${Hh - bs}"/>`;
    const minA = sp.avant.reduce((m, p) => (p[2] < m[2] ? p : m)), minB = sp.apres.reduce((m, p) => (p[2] < m[2] ? p : m));
    s += `<circle class="creux-avant" cx="${x(minA[0]).toFixed(1)}" cy="${y(minA[2]).toFixed(1)}" r="4.5"/>`;
    s += `<rect class="creux-apres" x="${(x(minB[0]) - 4.5).toFixed(1)}" y="${(y(minB[2]) - 4.5).toFixed(1)}" width="9" height="9" rx="1.5"/>`;
    const etiquette = `Baisses depuis le dernier sommet, observées du ${sp.avant[0][0]} au ${sp.avant[sp.avant.length - 1][0]}. `
      + `Sans ta demande, creux dessiné ${moins(F.pct(minA[2], 1))} le ${minA[0]} ; avec ta demande, ${moins(F.pct(minB[2], 1))} le ${minB[0]}. `
      + `Courbe échantillonnée, un point sur ${AF.meta.pas_series}. Rien n'est tracé après la fin des données.`;
    const fig = h('div', { class: 'courbe' });
    fig.innerHTML = `<svg viewBox="0 0 ${W} ${Hh}" width="${W}" height="${Hh}" role="img" aria-label="${etiquette.replace(/"/g, '&quot;')}">${s}</svg>`;
    return { fig, minA, minB, n: sp.avant.length };
  }

  function carteEpargne(d, r) {
    const cle = `ep-${r ? r.i : 'x'}`;
    const k = d.comparaison;
    const app = approfondi();
    if (!k || !k.disponible) {
      return li(cle, null, h('article', { class: 'carte epargne', 'aria-labelledby': `t-${cle}` }, surTitre('Ton épargne, avant et après', `t-${cle}`),
        h('p', null, `Comparaison indisponible${k && k.raison ? ` : ${k.raison}` : '.'}`)));
    }
    const M = AF.mesures(d), ids = k.faits || {};
    const pc = M.find((m) => m.cle === 'pire_chute'), vo = M.find((m) => m.cle === 'volatilite');
    const phrase = ((d.texte && d.texte.pourquoi) || []).find((p) => (p.faits || []).includes(ids.ecart_pire_chute) && /fenêtre/i.test(p.texte));
    const ctx = ctxDe(d, phrase ? phrase.faits : [], 'Comparaison appariée');
    const largeur = Math.min(472, (liste.clientWidth || 343) - 40);
    const c = courbe(d, largeur);
    const fen = h('button', { class: 'fenetre-bouton', onclick: () => ouvrirFait(ids.fenetre_portefeuille, d) }, `observé ${k.fenetre.debut} → ${k.fenetre.fin}`);
    return li(cle, null, h('article', { class: 'carte epargne', 'aria-labelledby': `t-${cle}` },
      r ? rubanPerime(r) : null,
      surTitre('Ton épargne, avant et après', `t-${cle}`),
      h('p', { class: 'epargne-chapeau' }, 'Même épargne, même période passée, mesurée de la même façon : une fois sans ta demande, une fois avec. ', ids.fenetre_portefeuille ? fen : `observé ${k.fenetre.debut} → ${k.fenetre.fin}`),
      pc ? paire(pc, d, true) : null,
      app && vo ? paire(vo, d, false) : null,
      phrase ? h('p', { class: 'epargne-phrase' }, texteRiche(phrase.texte, ctx), ' ', pType(phrase.type)) : null,
      c ? h('figure', { class: 'figure-courbe' },
        h('figcaption', { class: 'courbe-titre' }, h('span', null, 'La courbe réelle des baisses'), h('span', { class: 'courbe-fenetre' }, `observé ${k.fenetre.debut} → ${k.fenetre.fin}`)),
        c.fig,
        h('ul', { class: 'legende' },
          h('li', null, h('span', { class: 'trait trait-avant', 'aria-hidden': 'true' }), h('span', { class: 'marq marq-rond', 'aria-hidden': 'true' }),
            h('span', null, 'Sans ta demande · pire baisse mesurée ', ids.avant_pire_chute ? boutonFait(ids.avant_pire_chute, d, affiche(k.avant.pire_chute_pct, '%')) : affiche(k.avant.pire_chute_pct, '%'))),
          h('li', null, h('span', { class: 'trait trait-apres', 'aria-hidden': 'true' }), h('span', { class: 'marq marq-carre', 'aria-hidden': 'true' }),
            h('span', null, 'Avec ta demande · pire baisse mesurée ', ids.apres_pire_chute ? boutonFait(ids.apres_pire_chute, d, affiche(k.apres.pire_chute_pct, '%')) : affiche(k.apres.pire_chute_pct, '%')))),
        h('p', { class: 'petit' }, `Le passé seulement : rien n'est tracé après le ${k.fenetre.fin}. Courbe échantillonnée (un point sur ${AF.meta.pas_series}, ${c.n} points) : son creux peut paraître moins profond que la mesure exacte, qui est dans les faits.`)) : null,
      app ? tableMesures(M, d) : null,
      app ? fenetres(d) : null,
      app ? h('p', { class: 'petit' }, `Méthode : ${k.politique} · moteur ${k.moteur} (${k.version_moteur}).`) : null,
      app ? tableFaits([ids.poids_avant, ids.poids_apres], d, 'Allocations comparées') : null,
      compteChiffres(ctx)));
  }
  function tableMesures(M, d) {
    const ids = (d.comparaison && d.comparaison.faits) || {};
    const cel = (id, v, unite) => (id ? boutonFait(id, d, unite === '$' ? moins(F.cad(v)) : moins(F.pct(v, 1))) : (unite === '$' ? moins(F.cad(v)) : moins(F.pct(v, 1))));
    return h('div', { class: 'mesures' }, h('p', { class: 'h-section' }, 'Les quatre mesures appariées'),
      h('ul', null, M.map((m) => h('li', { class: 'mesure' },
        h('p', { class: 'mesure-titre' }, m.titre),
        h('div', { class: 'mesure-grille' },
          h('span', null, h('span', { class: 'mini-lib' }, 'Avant'), cel(ids[`avant_${m.cle}`], m.avant, m.unite)),
          h('span', null, h('span', { class: 'mini-lib' }, 'Après'), cel(ids[`apres_${m.cle}`], m.apres, m.unite)),
          h('span', null, h('span', { class: 'mini-lib' }, 'Écart'), ids[`ecart_${m.cle}`] ? boutonFait(ids[`ecart_${m.cle}`], d, moins(F.pts(m.ecart, 1))) : h('span', { class: 'sans-fait' }, 'sans fait dédié')))))));
  }
  function fenetres(d) {
    const sp = d.series_portefeuille;
    if (!sp || !(sp.avant_fenetres || []).length) return null;
    return h('div', { class: 'fenetres' }, h('p', { class: 'h-section' }, 'Fenêtres repères (passé, choisies à l\'avance)'),
      h('ul', null, sp.avant_fenetres.map((fa, i) => {
        const fb = (sp.apres_fenetres || [])[i];
        const b = (f) => (f ? h('button', { class: 'chiffre ch-serie', 'aria-label': `${moins(F.pct(f.pire_chute_pct, 1))} : détail de la fenêtre ${fa.nom}`, onclick: () => ouvrirFeuille(() => contenuSerie(fa, fb, d), fa.nom) }, moins(F.pct(f.pire_chute_pct, 1))) : '—');
        return h('li', { class: 'fenetre' }, h('p', { class: 'mesure-titre' }, fa.nom, h('span', { class: 'petit' }, ` · ${fa.debut} → ${fa.fin}`)),
          h('p', null, 'Pire baisse : sans ', b(fa), ' · avec ', b(fb)));
      })));
  }

  function carteChangerait(d, r) {
    const cle = `chgr-${r.i}`;
    const e = r.etat, P = AF.parametres(e.cas), app = approfondi();
    const cellules = P.montant.map((m) => {
      const dv = AF.dossierDe({ ...e, montant: m });
      if (!dv) return null;
      const et = dv.verdict.etat, actuel = m === e.montant;
      return h('li', null, h('button', {
        class: `cellule c-${et}${actuel ? ' est-actuel' : ''}`, 'data-fk': `cellule-${m}`,
        'aria-label': `${F.cad(m)} : ${etatLong(et)}${actuel ? ' (montant actuel)' : ' : poser cette question'}`,
        disabled: actuel || r.i !== AF.position() ? true : null,
        onclick: () => proposerEtSi({ montant: m }),
      }, h('span', { class: 'cellule-m' }, F.cad(m)), h('span', { class: 'cellule-e' }, ico(ICO_ETAT[et] || 'indetermine'), etatCourt(et)), actuel ? h('span', { class: 'cellule-actuel' }, 'actuel') : null));
    });
    const textes = (d.texte && d.texte.ce_qui_changerait) || [];
    const ctxs = textes.map((x) => ctxDe(d, x.faits, 'Ce qui changerait l\'avis'));
    const idsOptions = (d.options || []).flatMap((o) => o.faits || []).concat(textes.flatMap((x) => x.faits || []));
    return li(cle, null, h('article', { class: 'carte changerait', 'aria-labelledby': `t-${cle}` },
      rubanPerime(r),
      surTitre("Ce qui changerait l'avis", `t-${cle}`),
      textes.length ? textes.map((x, k) => h('p', { class: 'changerait-texte' }, texteRiche(x.texte, ctxs[k]), ' ', pType(x.type))) : h('p', null, 'Le dossier ne signale aucun changement simple qui modifierait l\'avis.'),
      h('p', { class: 'h-section' }, 'Selon le montant, tes autres réponses inchangées'),
      h('ul', { class: 'bande-montants' }, cellules),
      h('p', { class: 'petit' }, 'Avis précalculés par le moteur pour chaque montant ; touche un montant pour poser la question.'),
      h('p', { class: 'h-section' }, 'Options comparées'),
      listeOptions(d, r),
      h('p', { class: 'petit' }, 'Ordre fixé par ta demande, pas un classement. Ce sont des comparaisons, pas des conseils.'),
      app ? tableFaits(idsOptions, d) : null,
      ctxs.map(compteChiffres)));
  }
  function listeOptions(d, r) {
    const P = AF.parametres(r.etat.cas), dm = d.demande || {};
    return h('ul', { class: 'options' }, (d.options || []).map((o, k) => {
      const ctx = ctxDe(d, o.faits || [], `Option « ${o.nom} »`);
      const memeActif = o.ticker === dm.ticker;
      const essai = memeActif && o.montant_cad !== r.etat.montant && P.montant.includes(o.montant_cad) && r.i === AF.position();
      return h('li', { class: `option c-${o.etat}` },
        h('div', { class: 'option-tete' }, h('strong', null, o.nom), pEtat(o.etat)),
        h('p', { class: 'option-actif' }, o.ticker, o.libelle_actif ? ` · ${o.libelle_actif}` : '', ' · ', boutonChamp(F.cad(o.montant_cad), `options › ${o.nom} › montant_cad`, o.montant_cad), approfondi() && o.horizon_ans ? ` · horizon ${o.horizon_ans} ans` : ''),
        o.constat || o.note ? h('p', null, texteRiche(o.constat || o.note, ctx)) : null,
        essai ? h('button', { class: 'bouton secondaire', onclick: () => proposerEtSi({ montant: o.montant_cad }) }, `Et si je mettais ${F.cad(o.montant_cad)} ?`)
          : !memeActif ? h('p', { class: 'non-realise' }, "Changer d'actif : non réalisé dans ce prototype.")
            : k > 0 && !P.montant.includes(o.montant_cad) ? h('p', { class: 'non-realise' }, `${F.cad(o.montant_cad)} n'est pas précalculé : essai non réalisé dans ce prototype.`) : null);
    }));
  }

  function carteLimites(d, r) {
    const cle = `lim-${r ? r.i : 'x'}`;
    const L = (d.texte && d.texte.limites) || [];
    if (!L.length) return null;
    const app = approfondi();
    const item = (l) => h('li', null, h('p', null, texteRiche(l.texte, ctxDe(d, l.faits || [], 'Limite', true))), h('div', { class: 'regle-pied' }, pType(l.type), boutonRefs(l.references, 'Références de cette limite')));
    const tete = app ? L : L.slice(0, 3), reste = app ? [] : L.slice(3);
    return li(cle, null, h('article', { class: 'carte limites', 'aria-labelledby': `t-${cle}` },
      r ? rubanPerime(r) : null,
      surTitre('Limites', `t-${cle}`),
      h('ul', { class: 'limites-liste' }, tete.map(item)),
      reste.length ? plie(cle, false, `Voir les ${reste.length} autres limites`, h('ul', { class: 'limites-liste' }, reste.map(item))) : null,
      d.texte && d.texte.avertissement ? h('p', { class: 'avertissement' }, d.texte.avertissement) : null,
      app ? tableFaits(L.flatMap((l) => l.faits || []), d) : null));
  }

  function detailsAvis(d, r) {
    const regles = d.regles || [];
    const ordre = { rouge: 0, orange: 1, gris: 2, non_evaluee: 3 };
    const nonOk = regles.filter((x) => x.niveau !== 'ok').sort((a, b) => (ordre[a.niveau] ?? 9) - (ordre[b.niveau] ?? 9));
    return [
      carteMiroir(d, r),
      ...nonOk.map((x, k) => carteRegle(x, d, r, k + 1, nonOk.length)),
      carteReglesOk(regles.filter((x) => x.niveau === 'ok'), d, r),
      carteEpargne(d, r),
      r ? carteChangerait(d, r) : null,
      carteLimites(d, r),
    ];
  }

  /* États de démonstration : clairement étiquetés, aucun calcul. */
  function carteDemo(d, r) {
    const cle = `demo-${ui.demo}-${r.i}`;
    const etapes = d.trace || [];
    if (ui.demo === 'chargement') {
      return li(cle, null, h('article', { class: 'carte demo', 'aria-busy': 'true', 'aria-labelledby': `t-${cle}` },
        h('p', { class: 'badge-demo' }, 'Démonstration · chargement'),
        surTitre('Le second avis', `t-${cle}`),
        h('div', { class: 'squelette', 'aria-hidden': 'true' }, h('span'), h('span'), h('span')),
        h('p', null, 'Analyse en cours : le verdict apparaîtra ici, après les six étapes. (Rien ne tourne réellement : état de démonstration.)'),
        h('ol', { class: 'etapes' }, etapes.map((t, i) => ligneEtape(t, i, d, 'attente')))));
    }
    if (ui.demo === 'erreur') {
      return li(cle, null, h('article', { class: 'carte demo erreur', 'aria-labelledby': `t-${cle}` },
        h('p', { class: 'badge-demo' }, 'Démonstration · erreur'),
        h('h2', { class: 'demo-titre', id: `t-${cle}` }, ico('indetermine'), "L'analyse s'est arrêtée à l'étape Sceptique"),
        h('p', null, 'Les étapes déjà faites restent affichées. Aucun verdict n\'est montré tant que les vérifications n\'ont pas été exécutées.'),
        h('ol', { class: 'etapes' }, etapes.map((t, i) => ligneEtape(t, i, d, i < 3 ? 'fait' : i === 3 ? 'echec' : 'non_lance'))),
        h('button', { class: 'bouton primaire', onclick: () => choisirDemo('reprise') }, 'Reprendre à partir du Sceptique')));
    }
    const R = ui.relecture && ui.relecture.cle === cle ? ui.relecture : null;
    return li(cle, null, h('article', { class: 'carte demo', 'aria-labelledby': `t-${cle}` },
      h('p', { class: 'badge-demo' }, 'Démonstration · reprise'),
      surTitre('Reprise après interruption', `t-${cle}`),
      h('p', null, 'Les trois premières étapes sont conservées ; on relit les suivantes, puis l\'avis revient.'),
      h('ol', { class: 'etapes' }, etapes.map((t, i) => ligneEtape(t, i, d, i < 3 ? 'conserve' : R ? R.etats[i] : 'attente')))));
  }

  /* Cas particuliers : hors historique, en lecture seule, retirables. */
  function cartesSpeciales(sp) {
    const base = `sp-${sp.n}`;
    const retirer = h('button', { class: 'bouton tertiaire', onclick: () => { ui.speciaux = ui.speciaux.filter((x) => x !== sp); rendreTout(); } }, ico('fermer'), 'Retirer du fil');
    const entete = li(`${base}-chap`, 'li-chap', h('div', { class: 'chapitre chapitre-special' }, h('span', null, 'Cas particulier · hors historique'), h('strong', null, SPECIAUX[sp.type]), retirer));
    const S2 = AF.speciaux[sp.type];
    if (!S2) return [entete];
    if (!S2.dossier) {
      return [entete, li(`${base}-err`, null, h('article', { class: 'carte refus', 'aria-labelledby': `t-${base}-err` },
        surTitre('Demande refusée avant analyse', `t-${base}-err`),
        h('p', { class: 'refus-message' }, S2.message),
        approfondi() && S2.statut ? h('p', { class: 'petit' }, `Code de réponse : ${S2.statut}`) : null,
        h('p', null, "Aucune analyse n'a été lancée : il n'y a pas de dossier pour cette demande, donc pas d'avis.")))];
    }
    const d = S2.dossier;
    const regles = d.regles || [];
    return [entete, carteDemande(d, `${base}-dem`), carteCompris(d, `${base}-comp`, true), carteTravail(d, `${base}-trav`),
      li(`${base}-avis`, `li-avis c-${d.verdict.etat}`, articleAvis(d, null, 'special', `${base}-avis`)),
      ...regles.map((x, k) => carteRegle(x, d, null, k + 1, regles.length, `${base}-reg-${x.code}`))];
  }

  function chapitreReplie(c, pos) {
    const dern = c.revs[c.revs.length - 1], cle = `chapr-${c.revs[0].i}`;
    const resume = [h('strong', null, AF.nomCas(c.cas)), ` · ${c.revs.length} avis · dernier : `, pEtat(dern.verdict)];
    return li(cle, 'li-replie', h('div', { class: 'carte replie' },
      plie(cle, false, resume, c.revs.map((r) => articleAvis(AF.dossierDe(r.etat), r, r.i < pos ? 'precedent' : 'suivant', `avis-${r.i}`)))));
  }

  function bulleAttente() {
    const b = AF.brouillon();
    if (!b) return null;
    return li('att', 'li-bulle', h('div', { class: 'bulle bulle-attente' },
      h('p', { class: 'sur-titre' }, ico('perime'), 'Question en attente · pas encore analysée'),
      h('p', { class: 'bulle-attente-q' }, questionEtSi(AF.etat(), b))));
  }

  /* ───────────── Rendu du fil ───────────── */
  function chapitres(H) {
    const C = [];
    for (const r of H) { const d = C[C.length - 1]; if (!d || d.cas !== r.etat.cas) C.push({ cas: r.etat.cas, revs: [r] }); else d.revs.push(r); }
    return C;
  }
  function rendreFil(H, pos) {
    const items = [];
    const C = chapitres(H), dernier = H.length - 1;
    const kFocus = C.findIndex((c) => c.revs.some((r) => r.i === pos));
    const speciauxApres = (i) => ui.speciaux.filter((sp) => sp.apres === i).forEach((sp) => items.push(...cartesSpeciales(sp)));
    C.forEach((c, k) => {
      if (k !== kFocus) { items.push(chapitreReplie(c, pos)); c.revs.forEach((r) => speciauxApres(r.i)); return; }
      c.revs.forEach((r, j) => {
        const d = AF.dossierDe(r.etat);
        if (j === 0) {
          items.push(separateur(r, k), carteDemande(d, `dem-${r.i}`), carteCompris(d, `comp-${r.i}`), carteTravail(d, `trav-${r.i}`));
        } else {
          items.push(bulleEtSi(r, H), carteChangement(r, H));
        }
        if (r.i === pos && ui.demo !== 'normal') items.push(carteDemo(d, r));
        else {
          const role = r.i === pos ? (pos === dernier ? 'actuel' : 'relu') : r.i < pos ? 'precedent' : 'suivant';
          items.push(carteAvis(d, r, role));
          if (r.i === pos) items.push(...detailsAvis(d, r));
        }
        speciauxApres(r.i);
      });
    });
    items.push(bulleAttente());
    const propres = items.filter(Boolean);
    for (const el of propres) if (!ui.connues.has(el.dataset.cle)) el.classList.add('arrive');
    liste.replaceChildren(...propres);
    ui.connues = new Set(propres.map((el) => el.dataset.cle));
  }

  /* ───────────── Barre « Et si… » ───────────── */
  function rendreBarre() {
    const zone = $('#barre-contenu');
    const e = AF.etat(), b = AF.brouillon(), P = AF.parametres(e.cas);
    const puce = (fk, libelle, actuel, presse, action, aria) => h('button', {
      class: `puce${actuel ? ' est-actuel' : ''}`, 'data-fk': fk, 'aria-pressed': presse ? 'true' : 'false', 'aria-label': aria || null, onclick: action,
    }, actuel ? h('span', { class: 'puce-point', 'aria-hidden': 'true' }) : null, libelle);
    const sep = () => h('span', { class: 'puce-sep', 'aria-hidden': 'true' });
    const puces = [];
    if (P.retrait.length > 1) {
      P.retrait.forEach((x) => puces.push(puce(`r-${x}`, `retrait : ${F.retrait(x)}`, x === e.retrait, !!b && b.retrait === x && x !== e.retrait,
        () => proposerEtSi({ retrait: x }), `Et si le retrait était ${F.retrait(x)}${x === e.retrait ? ' (actuel)' : ''}`)));
      puces.push(sep());
    }
    if (P.exclusion.length > 1) {
      P.exclusion.forEach((x) => puces.push(puce(`x-${x}`, libExclusion(x), x === e.exclusion, !!b && b.exclusion === x && x !== e.exclusion,
        () => proposerEtSi({ exclusion: x }), `Et si : ${libExclusion(x)}${x === e.exclusion ? ' (actuel)' : ''}`)));
      puces.push(sep());
    }
    P.montant.forEach((m) => puces.push(puce(`m-${m}`, F.cad(m), m === e.montant, !!b && b.montant === m && m !== e.montant,
      () => proposerEtSi({ montant: m }), `Et si je mettais ${F.cad(m)}${m === e.montant ? ' (montant actuel)' : ''}`)));
    puces.push(sep(), h('button', { class: 'puce puce-situation', 'data-fk': 'situation', 'aria-haspopup': 'dialog', onclick: ouvrirSituations }, 'Autre situation…'));
    const apercu = b ? h('div', { class: 'barre-apercu' },
      h('p', { class: 'barre-question' }, h('span', { class: 'barre-q-etiq' }, ico('perime'), 'Ta question, pas encore analysée'), h('span', { class: 'barre-q-texte' }, questionEtSi(e, b))),
      h('div', { class: 'barre-actions' },
        h('button', { class: 'bouton secondaire', 'data-fk': 'abandonner', onclick: () => { ui.action = { type: 'abandonner' }; AF.abandonner(); } }, 'Laisser tomber'),
        h('button', { class: 'bouton primaire', 'data-fk': 'appliquer', onclick: () => { ui.action = { type: 'appliquer' }; AF.appliquer(); } }, "Voir l'avis", ico('fleche')))) : null;
    zone.replaceChildren(apercu || '', h('div', { class: 'barre-ligne' },
      h('span', { class: 'barre-etsi', 'aria-hidden': 'true' }, 'Et si…'),
      h('div', { class: 'defile', role: 'group', 'aria-label': 'Et si… : questions possibles' }, puces)));
    $('#barre').classList.toggle('en-apercu', !!b);
  }

  /* ───────────── Bande de statut (archive, aperçu, démonstration) ───────────── */
  function rendreStatut(H, pos, statut) {
    const bande = $('#statut-bande');
    const enfants = [];
    if (ui.demo !== 'normal') enfants.push(h('p', { class: 'statut statut-demo' }, h('span', null, h('strong', null, 'Démonstration'), ` : état « ${ui.demo} ». Rien n'est réellement calculé.`),
      h('button', { class: 'bouton tertiaire', onclick: () => { ui.demo = 'normal'; arreterRelecture(); rendreTout(); } }, 'État normal')));
    if (statut === 'archive' || (statut === 'apercu' && pos !== H.length - 1)) enfants.push(h('p', { class: 'statut statut-archive' }, ico('archive'), h('span', null, h('strong', null, 'Archive'), ` : tu relis l'avis n°${pos + 1} sur ${H.length}.`),
      h('button', { class: 'bouton tertiaire', onclick: () => { ui.action = { type: 'aller', depuis: pos }; AF.allerA(H.length - 1); } }, 'Au plus récent')));
    if (statut === 'apercu') enfants.push(h('p', { class: 'statut statut-apercu' }, ico('perime'), h('span', null, h('strong', null, 'Aperçu'), " : le résultat affiché est périmé tant que ta question n'est pas analysée.")));
    bande.replaceChildren(...enfants);
    bande.hidden = !enfants.length;
  }

  /* ───────────── Panneau (ordinateur) et feuille « Plan » (téléphone) ───────────── */
  function contenuPlan(ou) {
    const sfx = ou === 'panneau' ? 'p' : 'f';
    const H = AF.historique(), pos = AF.position(), dernier = H.length - 1;
    if (ui.compPos !== pos || ui.compA == null || ui.compA > dernier || ui.compB > dernier) {
      ui.compPos = pos; ui.compB = pos;
      ui.compA = H[pos].parent != null && H[pos].parent >= 0 ? H[pos].parent : Math.max(0, pos - 1);
    }
    const tag = (r) => (r.i === pos ? (pos === dernier ? 'actuel' : 'relu') : r.i < pos ? 'précédent' : 'plus récent');
    const option = (r, sel) => h('option', { value: r.i, selected: sel ? true : null }, `n°${r.i + 1} · ${r.nom} · ${resumeEtat(r.etat)} · ${etatCourt(r.verdict)}`);
    const plan = h('section', { class: 'plan', 'aria-labelledby': `plan-titre-${sfx}` },
      h('h2', { class: 'panneau-titre', id: `plan-titre-${sfx}` }, ico('plan'), 'Le fil en un coup d\'œil'),
      h('ol', { class: 'plan-liste' }, H.map((r) => h('li', null, h('button', {
        class: `plan-item c-${r.verdict}${r.i === pos ? ' est-focus' : ''}`, 'aria-current': r.i === pos ? 'true' : null,
        onclick: () => { fermerFeuille(); allerVersAvis(r.i); },
      }, ico(ICO_ETAT[r.verdict] || 'indetermine'),
      h('span', { class: 'plan-txt' }, h('span', { class: 'plan-l1' }, `Avis n°${r.i + 1} · ${r.nom}`, h('span', { class: `plan-tag tag-${tag(r).replace(' ', '-')}` }, tag(r))),
        h('span', { class: 'plan-l2' }, `${etatCourt(r.verdict)} · ${resumeEtat(r.etat)}`)))))));
    const comp = h('section', { class: 'comparer', 'aria-labelledby': `comp-titre-${sfx}` },
      h('h2', { class: 'panneau-titre', id: `comp-titre-${sfx}` }, 'Comparer deux avis'),
      H.length < 2 ? h('p', { class: 'petit' }, 'Pose une question « Et si… » : un deuxième avis apparaîtra et pourra être comparé au premier.') : [
        h('div', { class: 'comp-choix' },
          h('label', null, h('span', null, 'Avis A'), h('select', { onchange: (ev) => { ui.compA = +ev.target.value; rafraichirPlan(); } }, H.map((r) => option(r, r.i === ui.compA)))),
          h('label', null, h('span', null, 'Avis B'), h('select', { onchange: (ev) => { ui.compB = +ev.target.value; rafraichirPlan(); } }, H.map((r) => option(r, r.i === ui.compB))))),
        resultatComparaison(H[ui.compA], H[ui.compB])],
      AF.perime() ? h('p', { class: 'note' }, ico('perime'), " Ta question en attente n'est pas comparée : elle n'est pas encore analysée.") : null);
    return h('div', { class: 'plan-contenu' }, plan, comp);
  }
  function resultatComparaison(A, B) {
    if (!A || !B) return null;
    if (A.i === B.i) return h('p', { class: 'petit' }, 'Choisis deux avis différents.');
    const c = AF.comparer(A.etat, B.etat), dA = AF.dossierDe(A.etat), dB = AF.dossierDe(B.etat);
    return h('div', { class: 'comp-resultat', 'aria-live': 'polite' },
      h('p', { class: 'chg-motif' }, c.motif),
      h('div', { class: 'chg-verdict' }, pEtat(c.verdict.avant), ico('fleche', 'fl'), pEtat(c.verdict.apres)),
      h('table', { class: 'comp-table' },
        h('caption', { class: 'sr' }, 'Règles, avis A puis avis B'),
        h('thead', null, h('tr', null, h('th', { scope: 'col' }, 'Règle'), h('th', { scope: 'col' }, 'A'), h('th', { scope: 'col' }, 'B'))),
        h('tbody', null, c.regles.map((x) => h('tr', { class: x.change ? 'change' : null },
          h('th', { scope: 'row' }, x.libelle, x.change ? h('span', { class: 'chg-tag' }, 'changé') : null),
          h('td', null, pNiveau(x.avant, 'Non évaluée')), h('td', null, pNiveau(x.apres, 'Non évaluée')))))),
      h('table', { class: 'comp-table' },
        h('caption', { class: 'comp-caption' }, 'Ton épargne avec la demande, sur la même période'),
        h('thead', null, h('tr', null, h('th', { scope: 'col' }, 'Mesure'), h('th', { scope: 'col' }, 'A'), h('th', { scope: 'col' }, 'B'))),
        h('tbody', null, c.mesures.map((m) => h('tr', { class: m.avant !== m.apres ? 'change' : null },
          h('th', { scope: 'row' }, m.titre),
          h('td', { class: 'num' }, m.avant == null ? '—' : valeurMesure(dA, m.cle, m.avant, m.unite)),
          h('td', { class: 'num' }, m.apres == null ? '—' : valeurMesure(dB, m.cle, m.apres, m.unite)))))));
  }
  function rafraichirPlan() {
    const p = $('#panneau');
    if (getComputedStyle(p).display !== 'none') p.replaceChildren(contenuPlan('panneau'));
    redessinerFeuilleOuverte();
  }
  function allerVersAvis(i) {
    const el = liste.querySelector(`[data-avis="${i}"]`);
    if (!el) return;
    const det = el.closest('details');
    if (det && !det.open) det.open = true;
    el.scrollIntoView({ block: 'start', behavior: comportement() });
    const t = el.querySelector('h2, h3');
    if (t) { t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true }); }
  }

  /* ───────────── Feuilles : situations et menu ───────────── */
  function ouvrirSituations() { ouvrirFeuille(contenuSituations, 'Changer de situation'); }
  function contenuSituations() {
    const e = AF.etat();
    return h('div', { class: 'menu' },
      h('p', null, 'Une autre situation ouvre un nouveau chapitre en bas du fil. Rien n\'est effacé : « Annuler » ramène ici.'),
      h('ul', { class: 'choix-cas' }, AF.cas().map((c) => {
        const d = AF.donnees.cas[c].variantes[AF.donnees.cas[c].depart], p = d.profil || {};
        const actuel = c === e.cas;
        return h('li', null, h('button', {
          class: `choix${actuel ? ' est-actuel' : ''}`, disabled: actuel ? true : null,
          onclick: () => { fermerFeuille(); ui.action = { type: 'cas' }; AF.changerCas(c); },
        }, h('span', { class: 'choix-nom' }, `${p.nom}, ${p.age} ans`, actuel ? h('span', { class: 'plan-tag tag-actuel' }, 'situation actuelle') : null),
        h('span', { class: 'choix-phrase' }, `« ${d.demande.texte} »`)));
      })),
      h('h3', { class: 'h-section' }, 'Cas particuliers du moteur'),
      h('p', { class: 'petit' }, 'Ajoutés au fil en lecture seule, hors de ton historique.'),
      h('ul', { class: 'choix-cas' }, Object.keys(SPECIAUX).filter((k) => AF.speciaux[k]).map((k) => h('li', null, h('button', {
        class: 'choix', onclick: () => { fermerFeuille(); ajouterSpecial(k); },
      }, h('span', { class: 'choix-nom' }, SPECIAUX[k]), h('span', { class: 'choix-phrase' }, k === 'hors_univers' ? 'Demande refusée avant toute analyse.' : 'Avis « indéterminé » : il manque une information.'))))));
  }
  function ajouterSpecial(type) {
    ui.numSpecial += 1;
    const sp = { n: ui.numSpecial, type, apres: AF.position() };
    ui.speciaux.push(sp);
    ui.action = { type: 'special', cle: `sp-${sp.n}-chap` };
    rendreTout();
  }
  function ouvrirMenu() { ouvrirFeuille(contenuMenu, 'Plus'); }
  function contenuMenu() {
    const lienProto = (dossier, nom) => h('li', null, h('a', { class: 'lien', href: AF.lien(`../${dossier}/index.html`) }, nom));
    const radio = (v, lib) => h('label', { class: 'demo-choix' }, h('input', { type: 'radio', name: 'demo', value: v, checked: ui.demo === v ? true : null, onchange: () => choisirDemo(v) }), h('span', null, lib));
    const m = AF.meta || {};
    return h('div', { class: 'menu' },
      h('section', null, h('h3', { class: 'h-section' }, 'Situation'), h('button', { class: 'bouton secondaire large', onclick: () => { pile.length = 0; ouvrirSituations(); } }, 'Changer de situation ou voir un cas particulier')),
      h('section', { class: 'seulement-mobile' }, h('h3', { class: 'h-section' }, 'Le fil'), h('button', { class: 'bouton secondaire large', onclick: () => ouvrirFeuille(() => contenuPlan('feuille'), 'Plan du fil et comparaison') }, ico('plan'), 'Plan du fil et comparaison')),
      h('section', null, h('h3', { class: 'h-section' }, 'Historique'),
        h('div', { class: 'rangee-boutons' },
          h('button', { class: 'bouton secondaire', disabled: AF.peutAnnuler() ? null : true, onclick: () => { fermerFeuille(); annuler(); } }, ico('annuler'), 'Annuler'),
          h('button', { class: 'bouton secondaire', disabled: AF.peutRetablir() ? null : true, onclick: () => { fermerFeuille(); ui.action = { type: 'retablir' }; AF.retablir(); } }, 'Rétablir')),
        h('button', { class: `bouton tertiaire${ui.confirmerRaz ? ' danger' : ''}`, onclick: (ev) => {
          if (!ui.confirmerRaz) { ui.confirmerRaz = true; ev.currentTarget.textContent = 'Toucher encore : tout le fil sera effacé'; ev.currentTarget.classList.add('danger'); return; }
          ui.confirmerRaz = false; fermerFeuille(); ui.speciaux = []; ui.action = { type: 'raz' }; AF.reinitialiser();
        } }, 'Réinitialiser le fil')),
      h('section', null, h('h3', { class: 'h-section' }, 'États de démonstration'),
        h('p', { class: 'petit' }, 'Pour voir les états de chargement, d\'erreur et de reprise. Rien n\'est réellement calculé.'),
        h('div', { class: 'demo-groupe', role: 'radiogroup', 'aria-label': 'États de démonstration' }, radio('normal', 'Normal'), radio('chargement', 'Chargement'), radio('erreur', 'Erreur'), radio('reprise', 'Reprise'))),
      h('section', null, h('h3', { class: 'h-section' }, 'Les autres prototypes'),
        h('ul', { class: 'liens' }, h('li', null, h('a', { class: 'lien', href: '../index.html' }, 'Galerie')), AUTRES.map(([dos, nom]) => lienProto(dos, nom))),
        h('p', { class: 'petit' }, 'Même situation, même historique : l\'état est partagé.')),
      h('section', null, h('h3', { class: 'h-section' }, 'Données'),
        h('dl', { class: 'preuve-dl compact' }, h('dt', null, 'Généré le'), h('dd', null, m.genere_le || '—'), h('dt', null, 'Commit'), h('dd', null, h('code', null, m.commit || '—')), h('dt', null, 'Mode'), h('dd', null, m.mode || '—')),
        m.avertissement ? h('p', { class: 'petit' }, m.avertissement) : null));
  }
  function choisirDemo(v) {
    ui.demo = v;
    arreterRelecture();
    fermerFeuille();
    rendreTout();
    annoncer(v === 'normal' ? 'État normal.' : `Démonstration : état ${v}.`);
    if (v === 'reprise') lancerReprise();
  }

  /* ───────────── Relecture des étapes enregistrées ───────────── */
  function majEtapes(cle, etats) {
    const bloc = liste.querySelector(`[data-cle="${cle}"]`);
    if (!bloc) return;
    bloc.querySelectorAll('[data-etape]').forEach((el) => {
      const i = +el.dataset.etape, et = etats[i];
      el.className = el.className.replace(/etape-(attente|en_cours|fait|conserve|echec|non_lance)/, `etape-${et}`);
      const s = el.querySelector('.etape-statut');
      if (s) s.textContent = LIB_ETAPE[et] || et;
    });
  }
  function arreterRelecture() { if (ui.relecture && ui.relecture.stop) ui.relecture.stop(); ui.relecture = null; }
  function lancerRelecture(cle, d) {
    arreterRelecture();
    const n = (d.trace || []).length;
    ui.relecture = { cle, etats: Array(n).fill('attente'), stop: null };
    rendreTout();
    const R = ui.relecture;
    R.stop = AF.relireTrace(d, (i, phase) => {
      if (ui.relecture !== R) return;
      if (phase === 'fin') { ui.relecture = null; rendreTout(); annoncer(`Relecture terminée : ${n} étapes enregistrées.`); return; }
      R.etats[i] = phase === 'en_cours' ? 'en_cours' : 'fait';
      majEtapes(cle, R.etats);
    });
  }
  function lancerReprise() {
    const pos = AF.position(), d = AF.dossier(), cle = `demo-reprise-${pos}`;
    const n = (d.trace || []).length;
    const R = { cle, etats: Array(n).fill('attente').map((x, i) => (i < 3 ? 'conserve' : x)), stop: null };
    ui.relecture = R;
    rendreTout();
    R.stop = AF.relireTrace(d, (i, phase) => {
      if (ui.relecture !== R) return;
      if (phase === 'fin') { ui.relecture = null; ui.demo = 'normal'; rendreTout(); annoncer("Reprise terminée (démonstration) : l'avis est de nouveau affiché."); return; }
      if (i < 3) return;
      R.etats[i] = phase === 'en_cours' ? 'en_cours' : 'fait';
      majEtapes(cle, R.etats);
    });
  }

  /* ───────────── Notifications, annonces, défilement ───────────── */
  function annoncer(t) { const a = $('#annonce'); a.textContent = ''; setTimeout(() => { a.textContent = t; }, 60); }
  function cacherToast() { clearTimeout(ui.toastMinuteur); const t = $('#toast'); t.hidden = true; t.replaceChildren(); majSaut(); }
  function toast(texte, libelle, action) {
    const t = $('#toast');
    clearTimeout(ui.toastMinuteur);
    t.replaceChildren(...[h('span', { class: 'toast-texte' }, texte),
      libelle ? h('button', { class: 'toast-action', 'data-fk': 'toast', onclick: () => { cacherToast(); action(); } }, ico('annuler'), libelle) : null,
      h('button', { class: 'toast-fermer', 'aria-label': 'Fermer la notification', onclick: cacherToast }, ico('fermer'))].filter(Boolean));
    t.hidden = false;
    majSaut();
    ui.toastMinuteur = setTimeout(cacherToast, 9000);
  }
  function annuler() { ui.action = { type: 'annuler' }; if (!AF.annuler()) { ui.action = null; toast('Rien à annuler : c\'est le premier avis de ce fil.'); } }
  function defilerVers(cle, bloc) {
    const el = liste.querySelector(`[data-cle="${cle}"]`);
    if (el) el.scrollIntoView({ block: bloc || 'start', behavior: comportement() });
    return !!el;
  }
  function focusAvis(i) {
    const t = liste.querySelector(`[data-cle="avis-${i}"] .avis-verdict`);
    if (t) t.focus({ preventScroll: true });
  }
  function hauteurTete() { const t = $('.tete'); return t ? t.getBoundingClientRect().bottom : 0; }

  /* Pastille « aller à l'avis » : visible quand l'avis affiché sort de l'écran (comme « nouveaux messages »). */
  let observateur = null, dernierSaut = null;
  function observerAvis() {
    if (!('IntersectionObserver' in window)) return;
    if (observateur) observateur.disconnect();
    dernierSaut = null;
    const cible = liste.querySelector(`[data-cle="avis-${AF.position()}"]`) || liste.querySelector('[data-cle^="demo-"]');
    majSaut();
    if (!cible) return;
    observateur = new IntersectionObserver((entrees) => { dernierSaut = entrees[entrees.length - 1]; majSaut(); }, { rootMargin: '-90px 0px -150px 0px' });
    observateur.observe(cible);
  }
  function majSaut() {
    const b = $('#saut');
    const e = dernierSaut;
    if (!e || e.isIntersecting || !$('#toast').hidden || ui.demo !== 'normal') { b.hidden = true; return; }
    const pos = AF.position(), v = AF.dossier().verdict || {}, dessous = e.boundingClientRect.top > 0;
    b.className = `saut c-${v.etat}`;
    b.replaceChildren(ico(ICO_ETAT[v.etat] || 'indetermine'), `Avis n°${pos + 1} : ${etatCourt(v.etat)}`, h('span', { class: 'saut-fleche', 'aria-hidden': 'true' }, dessous ? '↓' : '↑'));
    b.setAttribute('aria-label', `Aller à l'avis n°${pos + 1}, ${etatLong(v.etat)}`);
    b.hidden = false;
  }
  function capturerAncre() {
    const haut = hauteurTete();
    for (const el of liste.children) { const r = el.getBoundingClientRect(); if (r.bottom > haut + 8) return { cle: el.dataset.cle, dy: r.top }; }
    return null;
  }
  function restaurerAncre(a) {
    if (!a) return;
    const el = liste.querySelector(`[data-cle="${a.cle}"]`);
    if (el) window.scrollBy(0, el.getBoundingClientRect().top - a.dy);
  }

  function apresAction(H, pos) {
    const a = ui.action;
    ui.action = null;
    if (!a) return false;
    const d = AF.dossier(), v = d.verdict || {};
    const resume = `${etatLong(v.etat)}. ${compteTexte(v)}.`;
    const cible = () => (defilerVers(`chg-${pos}`) || defilerVers(`chap-${pos}`) || defilerVers(`avis-${pos}`));
    switch (a.type) {
      case 'appliquer': case 'restaurer': case 'cas':
        annoncer(`Nouvel avis n°${pos + 1} : ${resume}`);
        cible(); focusAvis(pos);
        toast(a.type === 'cas' ? `Nouvelle situation : ${AF.nomCas(H[pos].etat.cas)}.` : a.type === 'restaurer' ? `L'avis n°${a.depuis + 1} est repris comme avis n°${pos + 1}.` : `Avis n°${pos + 1} ajouté en bas du fil.`, 'Annuler', annuler);
        return true;
      case 'annuler':
        annoncer(`Retour à l'avis n°${pos + 1} : ${resume}`);
        defilerVers(`avis-${pos}`); focusAvis(pos);
        toast(`Retour à l'avis n°${pos + 1}.`, 'Rétablir', () => { ui.action = { type: 'retablir' }; AF.retablir(); });
        return true;
      case 'retablir':
        annoncer(`Avis n°${pos + 1} rétabli : ${resume}`);
        defilerVers(`avis-${pos}`); focusAvis(pos);
        toast(`Avis n°${pos + 1} rétabli.`, 'Annuler', annuler);
        return true;
      case 'aller':
        annoncer(`Avis n°${pos + 1}${pos === H.length - 1 ? ', le plus récent' : ', archive'} : ${resume}`);
        defilerVers(`avis-${pos}`); focusAvis(pos);
        if (a.depuis != null && a.depuis !== pos) toast(`Tu lis l'avis n°${pos + 1}.`, `Revenir au n°${a.depuis + 1}`, () => { ui.action = { type: 'aller', depuis: pos }; AF.allerA(a.depuis); });
        return true;
      case 'proposer':
        if (AF.perime()) annoncer('Aperçu : ta question n\'est pas encore analysée. Le résultat affiché est périmé. Touche « Voir l\'avis ».');
        return false;
      case 'abandonner':
        annoncer('Question retirée. L\'avis affiché est de nouveau à jour.');
        return false;
      case 'special':
        defilerVers(a.cle);
        annoncer('Cas particulier ajouté au fil, hors historique.');
        return true;
      case 'raz':
        window.scrollTo({ top: 0, behavior: comportement() });
        toast('Fil réinitialisé : il repart de la demande de Robert.');
        annoncer('Fil réinitialisé.');
        return true;
      case 'ouverture': {
        const C = chapitres(H), c = C.find((x) => x.revs.some((r) => r.i === pos));
        if (c && c.revs.length > 1) { const el = liste.querySelector(`[data-cle="avis-${pos}"]`); if (el) el.scrollIntoView({ block: 'start' }); }
        else if (!mouvementReduit.matches && ui.demo === 'normal' && c) {
          let deja = false;
          try { deja = sessionStorage.getItem('af-fil-relu') === '1'; sessionStorage.setItem('af-fil-relu', '1'); } catch (err) { deja = false; }
          if (!deja) setTimeout(() => lancerRelecture(`trav-${c.revs[0].i}`, AF.dossierDe(c.revs[0].etat)), 400);
        }
        return true;
      }
      default: return false;
    }
  }

  /* ───────────── Rendu complet ───────────── */
  function rendreTout() {
    const actif = document.activeElement;
    const fk = actif && actif.dataset ? actif.dataset.fk : null;
    const ancre = capturerAncre();
    const H = AF.historique(), pos = AF.position(), statut = AF.statut();
    document.documentElement.dataset.niveau = AF.niveau();
    const r = document.getElementById(`niveau-${AF.niveau()}`);
    if (r) r.checked = true;
    rendreStatut(H, pos, statut);
    rendreFil(H, pos);
    rendreBarre();
    const p = $('#panneau');
    if (getComputedStyle(p).display !== 'none') p.replaceChildren(contenuPlan('panneau')); else p.replaceChildren();
    rendrePied();
    document.documentElement.style.scrollPaddingTop = `${Math.round(hauteurTete() + 12)}px`;
    const bouge = apresAction(H, pos);
    observerAvis();
    if (!bouge) restaurerAncre(ancre);
    if (fk && !document.activeElement.closest('#liste-fil .avis')) {
      const el = document.querySelector(`[data-fk="${fk}"]`);
      if (el && el !== document.activeElement && !el.disabled) el.focus({ preventScroll: true });
    }
  }
  function rendrePied() {
    const m = AF.meta || {};
    $('#pied').replaceChildren(h('div', { class: 'pied-in' },
      h('p', { class: 'pied-bandeau' }, 'Simulation éducative · données de démonstration précalculées par le moteur réel'),
      h('p', { class: 'petit' }, `Généré le ${m.genere_le || '—'} · commit ${m.commit || '—'}`),
      m.avertissement ? h('p', { class: 'petit' }, m.avertissement) : null,
      h('p', { class: 'petit' }, 'Ce fil compare ta demande à ta situation ; il ne dit pas quoi faire de ton argent. Le passé décrit ne prédit rien.'),
      h('nav', { 'aria-label': 'Autres prototypes' }, h('ul', { class: 'liens' }, h('li', null, h('a', { class: 'lien', href: '../index.html' }, 'Galerie')),
        AUTRES.map(([dos, nom]) => h('li', null, h('a', { class: 'lien', href: AF.lien(`../${dos}/index.html`) }, nom)))))));
  }

  /* ───────────── Démarrage ───────────── */
  function demarrer() {
    const m = AF.meta || {};
    $('#bandeau-meta').textContent = ` · ${(m.genere_le || '').slice(0, 10)} · commit ${m.commit || '—'}`;
    $('.marque-ico').innerHTML = ICONES.marque;
    $('#ico-menu').innerHTML = ICONES.menu;
    $('#ico-retour').innerHTML = ICONES.retour;
    $('#ico-fermer').innerHTML = ICONES.fermer;
    document.querySelectorAll('input[name="niveau"]').forEach((el) => el.addEventListener('change', () => {
      if (!el.checked) return;
      ui.ouverts.clear(); ui.fermes.clear();
      ui.action = null;
      AF.definirNiveau(el.value);
      annoncer(el.value === 'approfondi' ? 'Lecture approfondie : termes techniques, règles et limites dépliées.' : 'Lecture essentielle : une idée par carte.');
    }));
    $('#ouvrir-menu').addEventListener('click', ouvrirMenu);
    $('#marque').addEventListener('click', () => { window.scrollTo({ top: 0, behavior: comportement() }); $('#fil').focus({ preventScroll: true }); });
    $('#saut').addEventListener('click', () => {
      const pos = AF.position();
      const el = liste.querySelector(`[data-cle="avis-${pos}"]`) || liste.querySelector('[data-cle^="demo-"]');
      if (!el) return;
      el.scrollIntoView({ block: 'start', behavior: comportement() });
      const t = el.querySelector('.avis-verdict, h2');
      if (t) { t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true }); }
    });
    $('#feuille-fermer').addEventListener('click', fermerFeuille);
    $('#feuille-retour').addEventListener('click', () => { if (pile.length > 1) { pile.pop(); dessinerFeuille(); $('#feuille-titre').focus(); } });
    feuille.addEventListener('click', (ev) => { if (ev.target === feuille) fermerFeuille(); });
    feuille.addEventListener('close', () => {
      pile.length = 0; ui.confirmerRaz = false;
      const f = ui.retourFocus;
      if (f && document.contains(f) && typeof f.focus === 'function') f.focus({ preventScroll: true });
      else $('#fil').focus({ preventScroll: true });
    });
    const t = $('#toast');
    t.addEventListener('focusin', () => clearTimeout(ui.toastMinuteur));
    t.addEventListener('mouseenter', () => clearTimeout(ui.toastMinuteur));
    t.addEventListener('mouseleave', () => { clearTimeout(ui.toastMinuteur); if (!t.hidden) ui.toastMinuteur = setTimeout(cacherToast, 5000); });
    AF.abonner(rendreTout);
    let minuteur = 0;
    ui.largeur = liste.clientWidth;
    window.addEventListener('resize', () => {
      clearTimeout(minuteur);
      minuteur = setTimeout(() => { if (Math.abs(liste.clientWidth - ui.largeur) > 24) { ui.largeur = liste.clientWidth; rendreTout(); } else rafraichirPlan(); }, 160);
    });
    ui.action = { type: 'ouverture' };
    rendreTout();
  }
  demarrer();
})();
