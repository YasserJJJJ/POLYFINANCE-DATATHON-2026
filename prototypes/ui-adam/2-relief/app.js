/* Relief : la décision comme un territoire.
   Toute valeur vient de window.AF (socle commun). Ce fichier ne calcule aucun chiffre financier :
   il place sur une carte les états que le moteur a calculés et relie chaque nombre affiché à son fait.
   Les courbes de niveau sont un décor déterministe (aucune mesure) ; la légende le dit. */
(() => {
  'use strict';
  const AF = window.AF;
  if (!AF) {
    document.body.insertAdjacentHTML('afterbegin', '<p role="alert" style="padding:16px;background:#fff">Socle introuvable : ../socle/socle.js n’a pas été chargé.</p>');
    return;
  }
  const F = AF.donnees;
  const fmt = AF.fmt;
  const SVGNS = 'http://www.w3.org/2000/svg';

  /* ---------- Outils ---------- */
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const px = (n) => Math.round(n * 10) / 10; // arrondi de coordonnées de dessin, jamais de données
  const court = (e) => (AF.ETATS[e] ? AF.ETATS[e].court : 'Indéterminé');
  const approfondi = () => AF.niveau() === 'approfondi';
  const mobile = () => window.matchMedia('(max-width: 760px)').matches;
  const pos = () => AF.position();
  const hist = () => AF.historique();
  const heure = (t) => new Date(t).toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' });
  const pluriel = (n, mot) => `${n} ${mot}${n > 1 ? 's' : ''}`;

  const MOTIF_NIV = { ok: 'coherent', orange: 'ajustement', rouge: 'incoherent', gris: 'indetermine', non_evaluee: 'vide' };
  const RANG = { coherent: 0, ajustement: 1, incoherent: 2, indetermine: 1 };
  const CODE = new Set(['Contrôle données', 'Analyste', 'Gardien']);
  const NATURES = { donnee: 'Donnée', preference: 'Préférence', contrainte: 'Contrainte', inconnu: 'Inconnue' };
  const SENS = { aggrave: 'baisse plus profonde', ameliore: 'baisse moins profonde', neutre: 'baisse inchangée' };
  const SECTEURS = { Energy: 'Énergie' };
  const AUTRES = [['1-carnet', 'Carnet'], ['3-pupitre', 'Pupitre'], ['4-fil', 'Fil'], ['5-epure', 'Épure']];
  const SPECIAUX = { sans_epargne: 'Épargne totale inconnue', impossible: 'Montant supérieur à l’épargne', hors_univers: 'Actif hors de l’univers' };

  const vue = { special: null, demo: 'normal', sonde: null, survol: null, feuille: false, glisse: false, arretRelecture: null, arretDemo: null, demoEtapes: {}, boiteSonder: null };

  const lireCle = (k) => { const o = Object.fromEntries(k.split(';').map((p) => p.split('='))); return { montant: +o.m, retrait: o.r === 'na' ? null : +o.r, exclusion: o.x === '1' }; };
  const departDe = (cas) => ({ cas, ...lireCle(F.cas[cas].depart) });
  const dossierDepart = (cas) => F.cas[cas].variantes[F.cas[cas].depart];
  const dossierAffiche = () => (vue.special ? (F.speciaux[vue.special].dossier || null) : AF.dossier());
  const nomActif = (t) => { const a = (F.actifs || []).find((x) => x.ticker === t); return a ? a.name : t; };
  const secteurExclu = (cas) => { const ex = dossierDepart(cas).profil.exclusions || []; return ex.length ? ex.map((s) => SECTEURS[s] || s).join(', ') : 'Énergie'; };
  function paramTexte(e) {
    const p = AF.parametres(e.cas);
    let t = `retrait ${fmt.retrait(e.retrait)}`;
    if (p.exclusion.length > 1) t += e.exclusion ? ` · secteur ${secteurExclu(e.cas)} exclu` : ' · sans exclusion de secteur';
    return t;
  }

  /* Mesure de texte (police de carte) pour placer les étiquettes sur aplat sans débordement. */
  const ctx = document.createElement('canvas').getContext('2d');
  const POLICE = getComputedStyle(document.documentElement).getPropertyValue('--f-carte').trim() || 'sans-serif';
  const STYLES = { 't-repere': [12.5, 700, 0.06, 1.12], 't-etiq': [12, 400, 0, 1], 't-etiq-fort': [12.5, 700, 0.06, 1.12], 't-zone': [13.5, 700, 0.14, 1.12], 't-zone-sous': [11, 400, 0, 1] };
  function largeur(t, cls) {
    const [taille, gras, ls, sc] = STYLES[cls] || STYLES['t-etiq'];
    ctx.font = `${gras} ${taille}px ${POLICE}`;
    return ctx.measureText(t).width * sc + t.length * ls * taille;
  }
  function couper(t, cls, max) {
    const mots = String(t).split(' '); const lignes = []; let l = '';
    mots.forEach((m) => { const essai = l ? `${l} ${m}` : m; if (l && largeur(essai, cls) > max) { lignes.push(l); l = m; } else l = essai; });
    if (l) lignes.push(l);
    return lignes;
  }

  /* ---------- Liaison des nombres d'une phrase à leurs faits ---------- */
  const RX = /\bF-\d+\b|(?<![\p{L}\d,\-])-?\d{1,3}(?:[\u202f\u00a0]\d{3})+(?:,\d+)?|(?<![\p{L}\d,\-])-?\d+(?:,\d+)?/gu;
  const valeurs = (v) => (typeof v === 'number' ? [v] : v && typeof v === 'object' && !Array.isArray(v) ? Object.values(v).filter((x) => typeof x === 'number') : []);
  function trouverFait(tok, ids, d) {
    const t = parseFloat(tok.replace(/[\u202f\u00a0]/g, '').replace(',', '.'));
    if (isNaN(t)) return null;
    const dec = (tok.split(',')[1] || '').length;
    const tol = 0.5 * Math.pow(10, -dec) + 1e-9;
    const ok = (f) => valeurs(f.valeur).some((v) => Math.abs(v - t) <= tol || (dec === 0 && Math.abs(t) >= 100 && Math.abs(-v - t) <= tol));
    const faits = d.faits || [];
    const cand = faits.filter((f) => (ids || []).includes(f.id));
    return cand.find(ok) || (dec >= 2 ? faits.find(ok) : null) || null;
  }
  function phrase(texte, ids, d) {
    const s = String(texte || '').replace(/\s+$/, '');
    if (!d) return esc(AF.propre(s));
    let out = '', i = 0;
    for (const m of s.matchAll(RX)) {
      out += esc(s.slice(i, m.index));
      const tok = m[0];
      if (/^F-\d+$/.test(tok)) {
        const f = (d.faits || []).find((x) => x.id === tok);
        out += f ? `<button type="button" class="num" data-action="fait" data-valeur="${tok}" aria-label="Fiche ${tok} : ${esc(f.libelle)}">${tok}</button>` : esc(tok);
      } else {
        const f = trouverFait(tok, ids, d);
        const aff = AF.propre(tok);
        out += f ? `<button type="button" class="num" data-action="fait" data-valeur="${f.id}" aria-label="${esc(aff)} : fiche ${f.id}, ${esc(f.libelle)}">${esc(aff)}</button>` : esc(aff);
      }
      i = m.index + tok.length;
    }
    return out + esc(s.slice(i));
  }
  function valFait(f) {
    const v = f.valeur;
    if (typeof v === 'number') {
      const u = f.unite || '';
      if (u === '%') return fmt.pct(v, 1);
      if (u === '%/an') return `${fmt.pct(v, 1)}/an`;
      if (u === '$') return fmt.cad(v);
      if (u === 'points') return fmt.pts(v, 1);
      const dec = (String(v).split('.')[1] || '').length;
      return `${fmt.nombre(v, dec >= 3 ? 1 : dec)}${u && u !== 'fraction' ? ` ${u}` : ''}`;
    }
    if (Array.isArray(v)) return `${v.length} éléments`;
    if (v && typeof v === 'object') return 'détail';
    const t = String(v || '');
    return t.length > 42 ? `${t.slice(0, 40)}…` : t;
  }
  const puceFait = (id, d) => { const f = (d.faits || []).find((x) => x.id === id); return f ? `<button type="button" class="fait" data-action="fait" data-valeur="${f.id}" title="${esc(f.libelle)}"><span class="fait-id">${f.id}</span>${esc(valFait(f))}</button>` : ''; };
  const courtRef = (r) => { const a = String(r.auteurs || r.id).split(/[;,&]/)[0].trim(); const t = `${a} ${r.annee || ''}`.trim(); return t.length > 30 ? `${t.slice(0, 28)}…` : t; };
  const puceRef = (id) => { const r = AF.reference(id); return r ? `<button type="button" class="fait ref" data-action="ref" data-valeur="${esc(id)}" title="${esc(r.titre)}"><span class="fait-id">Réf.</span>${esc(courtRef(r))}</button>` : ''; };
  const badgeType = (t) => (t && AF.TYPES[t] ? `<span class="badge t-${t}">${esc(AF.TYPES[t])}</span>` : '');

  /* ---------- Terrain : ce que la carte connaît ---------- */
  function terrain() {
    const e = AF.etat();
    const cas = e.cas;
    const b = dossierDepart(cas).bascule;
    const dep = departDe(cas);
    const montants = [...b.montants].sort((x, y) => x - y);
    const horizons = [...b.horizons].sort((x, y) => x - y);
    const cases = new Map(b.cases.map((c) => [`${c.montant_cad}|${c.horizon_ans}`, c.etat]));
    const hDecl = AF.dossier().profil.horizon_ans;
    const grille = e.retrait === dep.retrait && e.exclusion === dep.exclusion;
    const stations = AF.parametres(cas).montant.slice().sort((x, y) => x - y).map((m) => {
      const d = AF.dossierDe({ cas, montant: m, retrait: e.retrait, exclusion: e.exclusion });
      return d ? { montant: m, etat: d.verdict.etat, dossier: d, dansGrille: montants.includes(m) } : null;
    }).filter(Boolean);
    return { cas, e, dep, montants, horizons, cases, hDecl, grille, stations, cle: `${cas}|${e.retrait}|${e.exclusion}` };
  }
  const etatStation = (T, m) => (T.stations.find((s) => s.montant === m) || {}).etat;

  function geometrie(T, W, H, bandeH) {
    const etroit = W < 600;
    const m = { g: etroit ? 66 : 84, d: etroit ? 8 : 18, h: (etroit ? 42 : 46) + bandeH, b: etroit ? 30 : 34 };
    const x0 = m.g, x1 = W - m.d, y0 = m.h, y1 = H - m.b;
    const nC = T.horizons.length, nR = T.montants.length;
    const cw = (x1 - x0) / nC, rh = (y1 - y0) / nR;
    let ic = T.horizons.indexOf(T.hDecl); if (ic < 0) ic = 0;
    const ms = T.montants;
    const yRow = (k) => y1 - (k + 0.5) * rh;
    /* Rangées égales (une par montant calculé) ; un montant hors grille est placé à sa position proportionnelle entre ses voisins. */
    const yM = (mt) => {
      const k = ms.indexOf(mt);
      if (k >= 0) return yRow(k);
      if (mt < ms[0]) return Math.min(y1 - 6, yRow(0) + ((ms[0] - mt) / (ms[1] - ms[0])) * rh);
      const n = ms.length - 1;
      if (mt > ms[n]) return Math.max(y0 + 6, yRow(n) - ((mt - ms[n]) / (ms[n] - ms[n - 1])) * rh);
      for (let j = 0; j < n; j++) if (mt > ms[j] && mt < ms[j + 1]) return yRow(j) + (yRow(j + 1) - yRow(j)) * ((mt - ms[j]) / (ms[j + 1] - ms[j]));
      return yRow(0);
    };
    const xg = x0 + ic * cw;
    return { W, H, x0, x1, y0, y1, cw, rh, ic, nC, nR, yRow, yM, xg, xdr: xg + cw, xd: xg + cw / 2, cote: (nC - 1 - ic) >= ic ? 1 : -1, etroit };
  }

  /* Intervalles par colonne. La colonne de l'horizon déclaré est découpée par les dossiers réels (stations). */
  function colonnes(T, G) {
    return T.horizons.map((h, c) => {
      if (c === G.ic) {
        const ys = T.stations.map((s) => G.yM(s.montant));
        return T.stations.map((s, k) => ({ haut: k === T.stations.length - 1 ? G.y0 : (ys[k] + ys[k + 1]) / 2, bas: k === 0 ? G.y1 : (ys[k] + ys[k - 1]) / 2, etat: s.etat }));
      }
      if (!T.grille) return null;
      return T.montants.map((mt, k) => ({ haut: G.y1 - (k + 1) * G.rh, bas: G.y1 - k * G.rh, etat: T.cases.get(`${mt}|${h}`) || 'indetermine' }));
    });
  }
  const etatA = (iv, y) => (iv.find((v) => y >= v.haut - 0.01 && y <= v.bas + 0.01) || {}).etat;
  function frontieres(cols, G) {
    const s = [];
    cols.forEach((iv, c) => {
      if (!iv) return;
      const xl = G.x0 + c * G.cw;
      for (let k = 0; k < iv.length - 1; k++) if (iv[k].etat !== iv[k + 1].etat) s.push([xl, iv[k].haut, xl + G.cw, iv[k].haut]);
    });
    for (let c = 0; c < cols.length - 1; c++) {
      const A = cols[c], B = cols[c + 1];
      if (!A || !B) continue;
      const x = G.x0 + (c + 1) * G.cw;
      const ys = [...new Set([...A, ...B].flatMap((v) => [px(v.haut), px(v.bas)]))].sort((p, q) => p - q);
      for (let k = 0; k < ys.length - 1; k++) {
        const ym = (ys[k] + ys[k + 1]) / 2, ea = etatA(A, ym), eb = etatA(B, ym);
        if (ea && eb && ea !== eb) s.push([x, ys[k], x, ys[k + 1]]);
      }
    }
    return s.map((g) => `M${px(g[0])} ${px(g[1])}L${px(g[2])} ${px(g[3])}`).join('');
  }

  /* Bascules lues dans les dossiers voisins de la colonne déclarée (règles qui changent d'un montant au suivant). */
  function bascules(T) {
    const out = [];
    for (let k = 0; k < T.stations.length - 1; k++) {
      const a = T.stations[k], b = T.stations[k + 1];
      const ea = { cas: T.cas, montant: a.montant, retrait: T.e.retrait, exclusion: T.e.exclusion };
      const regles = AF.comparer(ea, { ...ea, montant: b.montant }).regles.filter((r) => r.change);
      if (regles.length || a.etat !== b.etat) out.push({ a, b, verdict: a.etat !== b.etat, regles });
    }
    return out;
  }
  const nivMin = (n) => (n == null ? 'absente' : (AF.NIVEAUX_REGLE[n] || n).toLowerCase());

  /* ---------- Courbes de niveau décoratives : champ déterministe + marching squares ---------- */
  const cacheCourbes = new Map();
  function courbes(T) {
    const cle = T.cle;
    if (cacheCourbes.has(cle)) return cacheCourbes.get(cle);
    const nC = T.horizons.length, nR = T.montants.length, S = 3;
    const rang = (c, r) => {
      let e = null;
      if (T.grille) e = T.cases.get(`${T.montants[r]}|${T.horizons[c]}`);
      else if (T.horizons[c] === T.hDecl) e = etatStation(T, T.montants[r]);
      return e == null ? 0.8 : RANG[e];
    };
    const centres = [];
    for (let c = 0; c < nC; c++) for (let r = 0; r < nR; r++) centres.push([c + 0.5, r + 0.5, rang(c, r)]);
    let graine = 7;
    for (const ch of cle) graine = (graine * 31 + ch.charCodeAt(0)) % 9973;
    const ph = (i) => (graine * (i + 3) * 0.6180339) % 6.2832;
    const nu = nC * S + 1, nv = nR * S + 1, val = new Float64Array(nu * nv);
    for (let j = 0; j < nv; j++) for (let i = 0; i < nu; i++) {
      const u = i / S, v = j / S;
      let sw = 0, sv = 0;
      for (const [cu, cv, rk] of centres) {
        const d2 = (u - cu) * (u - cu) + (v - cv) * (v - cv) * 1.8;
        if (d2 > 9) continue;
        const w = Math.exp(-d2 / 1.7); sw += w; sv += w * rk;
      }
      const base = sw ? sv / sw : 0.8;
      const bruit = 0.32 * Math.sin(0.55 * u + ph(1)) * Math.cos(0.95 * v + ph(2)) + 0.2 * Math.sin(0.23 * u - 0.71 * v + ph(3)) + 0.1 * Math.sin(1.27 * u + 0.83 * v + ph(4)) + 0.05 * Math.cos(2.3 * u - 1.1 * v + ph(5));
      val[j * nu + i] = base * 1.1 + bruit;
    }
    let lo = Infinity, hi = -Infinity;
    for (const x of val) { if (x < lo) lo = x; if (x > hi) hi = x; }
    const PAS = 0.19, lignes = [];
    for (let n = Math.ceil(lo / PAS) + 1; n * PAS < hi; n++) {
      const segs = [];
      marche(val, nu, nv, n * PAS, n, S, segs);
      joindre(segs).forEach((l) => lignes.push({ n, l }));
    }
    cacheCourbes.set(cle, lignes);
    return lignes;
  }
  /* Assemble les segments en lignes continues et retire les petites boucles (qui ressembleraient à un signe). */
  function joindre(segs) {
    const k = (u, v) => `${Math.round(u * 1e4)},${Math.round(v * 1e4)}`;
    const bouts = new Map();
    segs.forEach((s, i) => { [k(s[0], s[1]), k(s[2], s[3])].forEach((c) => { if (!bouts.has(c)) bouts.set(c, []); bouts.get(c).push(i); }); });
    const pris = new Uint8Array(segs.length), out = [];
    const suivant = (cle, sauf) => (bouts.get(cle) || []).find((j) => j !== sauf && !pris[j]);
    segs.forEach((s, i) => {
      if (pris[i]) return;
      pris[i] = 1;
      const pts = [[s[0], s[1]], [s[2], s[3]]];
      for (const sens of [1, 0]) {
        let bout = sens ? pts[pts.length - 1] : pts[0], j;
        while ((j = suivant(k(bout[0], bout[1]), -1)) !== undefined) {
          pris[j] = 1;
          const t = segs[j], a = [t[0], t[1]], b = [t[2], t[3]];
          const nouv = k(a[0], a[1]) === k(bout[0], bout[1]) ? b : a;
          if (sens) pts.push(nouv); else pts.unshift(nouv);
          bout = nouv;
        }
      }
      const us = pts.map((p) => p[0]), vs = pts.map((p) => p[1]);
      const ferme = k(pts[0][0], pts[0][1]) === k(pts[pts.length - 1][0], pts[pts.length - 1][1]);
      if (ferme && Math.max(...us) - Math.min(...us) < 0.9 && Math.max(...vs) - Math.min(...vs) < 0.9) return;
      out.push(pts);
    });
    return out;
  }
  function marche(val, nu, nv, t, n, S, segs) {
    const lerp = (p, q) => (t - p) / (q - p || 1e-9);
    for (let j = 0; j < nv - 1; j++) for (let i = 0; i < nu - 1; i++) {
      const a = val[j * nu + i], b = val[j * nu + i + 1], c = val[(j + 1) * nu + i + 1], d = val[(j + 1) * nu + i];
      const idx = (a > t ? 1 : 0) | (b > t ? 2 : 0) | (c > t ? 4 : 0) | (d > t ? 8 : 0);
      if (idx === 0 || idx === 15) continue;
      const u = i / S, v = j / S, k = 1 / S;
      const E = [
        [u + lerp(a, b) * k, v], // bas
        [u + k, v + lerp(b, c) * k], // droite
        [u + lerp(d, c) * k, v + k], // haut
        [u, v + lerp(a, d) * k], // gauche
      ];
      const ajoute = (p, q) => segs.push([E[p][0], E[p][1], E[q][0], E[q][1], n]);
      const centre = (a + b + c + d) / 4 > t;
      switch (idx) {
        case 1: case 14: ajoute(3, 0); break;
        case 2: case 13: ajoute(0, 1); break;
        case 3: case 12: ajoute(3, 1); break;
        case 4: case 11: ajoute(1, 2); break;
        case 6: case 9: ajoute(0, 2); break;
        case 7: case 8: ajoute(3, 2); break;
        case 5: if (centre) { ajoute(0, 1); ajoute(2, 3); } else { ajoute(3, 0); ajoute(1, 2); } break;
        case 10: if (centre) { ajoute(3, 0); ajoute(1, 2); } else { ajoute(0, 1); ajoute(2, 3); } break;
        default: break;
      }
    }
  }

  /* ---------- Définitions SVG (motifs des zones) ---------- */
  const DEFS = `
    <pattern id="m-coherent" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#ecefea"/><circle cx="2" cy="2" r="1" fill="#7f8f88"/><circle cx="6" cy="6" r="1" fill="#7f8f88"/></pattern>
    <pattern id="m-ajustement" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="7" height="7" fill="#e1e6e2"/><line x1="0" y1="0" x2="0" y2="7" stroke="#64776f" stroke-width="1.4"/></pattern>
    <pattern id="m-incoherent" width="5.5" height="5.5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5.5" height="5.5" fill="#cdd5d0"/><path d="M0 0V5.5M0 0H5.5" stroke="#3a4d47" stroke-width="1.05" stroke-opacity=".75"/></pattern>
    <pattern id="m-indetermine" width="11" height="8" patternUnits="userSpaceOnUse"><rect width="11" height="8" fill="#f4f4f0"/><line x1="1" y1="4" x2="6.5" y2="4" stroke="#64776f" stroke-width="1.3"/></pattern>
    <pattern id="m-horsleve" width="12" height="12" patternUnits="userSpaceOnUse"><rect width="12" height="12" fill="#f0f1ec"/><circle cx="6" cy="6" r=".85" fill="#9fada7"/></pattern>
    <marker id="fl-accent" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#b33c0a"/></marker>`;

  /* ---------- Carte : fond (mis en cache) ---------- */
  const cacheFond = { cle: null };
  let Tc = null, Gc = null;

  /* Zone libre pour la note : au-delà des étiquettes (côté des repères) ou avant les balises (autre côté). */
  function boiteNote(T, G) {
    const lignes = noteCarte(T);
    if (!lignes.length || G.etroit) return null;
    const finEtiq = G.cote > 0 ? G.xdr + 300 : G.xg - 300;
    const finBalises = G.cote > 0 ? G.xg - 80 : G.xdr + 80;
    const zones = G.cote > 0
      ? [{ x: finEtiq, w: G.x1 - 10 - finEtiq }, { x: G.x0 + 10, w: finBalises - G.x0 - 10 }]
      : [{ x: G.x0 + 10, w: finEtiq - G.x0 - 10 }, { x: finBalises, w: G.x1 - 10 - finBalises }];
    const z = zones[0].w >= zones[1].w ? zones[0] : zones[1];
    const w = Math.min(340, z.w);
    if (w < 200) return null;
    const txt = lignes.flatMap((l, i) => couper(l, i === 0 ? 't-etiq-fort' : 't-etiq', w - 18).map((t) => ({ t, cls: i === 0 ? 't-etiq-fort' : 't-etiq' })));
    const h = txt.length * 15 + 14;
    return { x: z.x + (z.w - w) / 2, y: (G.y0 + G.y1) / 2 - h / 2, w, h, txt };
  }
  function noteCarte(T) {
    const st = T.stations;
    const tous = st.length && st.every((s) => s.etat === st[0].etat);
    const rougesCommuns = () => {
      const libs = [];
      (st[0] ? st[0].dossier.regles : []).forEach((r) => { if (st.every((s) => (s.dossier.regles.find((q) => q.code === r.code) || {}).niveau === 'rouge')) libs.push(r.libelle); });
      return libs;
    };
    if (!T.grille) {
      const dep = T.dep, p = AF.parametres(T.cas);
      const quoi = dep.retrait !== T.e.retrait ? `un retrait ${fmt.retrait(dep.retrait)}` : `le secteur ${secteurExclu(T.cas)} exclu`;
      const ici = dep.retrait !== T.e.retrait ? `retrait ${fmt.retrait(T.e.retrait)}` : 'sans exclusion';
      const l = ['Terrain non levé hors de ta colonne.', `La grille montant × horizon a été calculée avec ${quoi}. Avec « ${ici} », elle ne s’applique plus : seule la colonne de ton horizon (${T.hDecl} ans) est connue, à partir de ${st.length} dossiers réels.`];
      if (tous) l.push(`Tous les montants levés : « ${court(st[0].etat)} ».`);
      if (p.retrait.length > 1 || p.exclusion.length > 1) l.push('La légende permet de revenir au paramètre de la grille.');
      return l;
    }
    const etats = new Set(T.cases.values());
    if (etats.size === 1 && tous) {
      const e = [...etats][0], r = rougesCommuns();
      const l = ['Aucune frontière sur cette carte.', `À tous les montants et horizons calculés, le verdict reste « ${court(e)} » : le montant seul ne le fait pas changer.`];
      if (r.length) l.push(`Règle bloquante dans les ${st.length} dossiers de ta colonne : ${r.join(', ')}.`);
      const p = AF.parametres(T.cas);
      if (p.exclusion.length > 1 || p.retrait.length > 1) l.push('Un paramètre de la légende change le terrain.');
      return l;
    }
    return [];
  }

  function fond(T, G, cols) {
    const o = [];
    o.push(`<rect x="${px(G.x0)}" y="${px(G.y0)}" width="${px(G.x1 - G.x0)}" height="${px(G.y1 - G.y0)}" fill="url(#m-horsleve)"/>`);
    cols.forEach((iv, c) => {
      if (!iv) return;
      const x = G.x0 + c * G.cw;
      iv.forEach((v) => o.push(`<rect x="${px(x)}" y="${px(v.haut)}" width="${px(G.cw + 0.6)}" height="${px(v.bas - v.haut + 0.6)}" fill="url(#m-${v.etat})"/>`));
    });
    /* Courbes de niveau : décor sans valeur de mesure. */
    const fines = [], maitresses = [];
    const X = (u) => px(G.x0 + u * G.cw), Y = (v) => px(G.y1 - v * G.rh);
    courbes(T).forEach(({ n, l }) => {
      if (!approfondi() && n % 2) return;
      const d = l.map((q, i) => `${i ? 'L' : 'M'}${X(q[0])} ${Y(q[1])}`).join('');
      (n % 4 === 0 ? maitresses : fines).push(d);
    });
    const pale = T.grille ? '' : ' style="opacity:.28"';
    o.push(`<path class="courbes" d="${fines.join('')}"${pale}/><path class="courbes-maitresses" d="${maitresses.join('')}"${pale}/>`);
    for (let h = 5; h < T.horizons.length; h += 5) { const x = px(G.x0 + h * G.cw); o.push(`<line class="graticule" x1="${x}" y1="${px(G.y0)}" x2="${x}" y2="${px(G.y1)}"/>`); }
    const fr = frontieres(cols, G);
    if (fr) o.push(`<path class="frontiere-halo" d="${fr}"/><path class="frontiere" d="${fr}"/>`);
    o.push(`<rect class="cadre-plot" x="${px(G.x0)}" y="${px(G.y0)}" width="${px(G.x1 - G.x0)}" height="${px(G.y1 - G.y0)}"/>`);
    /* Axes */
    T.montants.forEach((m, k) => o.push(`<text class="t-axe" x="${px(G.x0 - 8)}" y="${px(G.yRow(k) + 4)}" text-anchor="end">${esc(fmt.cad(m))}</text>`));
    o.push(`<text class="t-titre-axe" x="${px(G.x0 - 8)}" y="${px(G.y0 - 10)}" text-anchor="end">montant ↑</text>`);
    T.horizons.forEach((h, c) => {
      const voir = !G.etroit || c === G.ic || h === 1 || h % 5 === 0;
      if (voir && c !== G.ic) o.push(`<text class="t-axe" x="${px(G.x0 + (c + 0.5) * G.cw)}" y="${px(G.y0 - 8)}" text-anchor="middle">${h}</text>`);
    });
    o.push(`<text class="t-titre-axe" x="${px((G.x0 + G.x1) / 2)}" y="${px(G.H - 10)}" text-anchor="middle">horizon (années) →</text>`);
    /* Note posée sur aplat (ordinateur) */
    const nb = boiteNote(T, G);
    if (nb) {
      o.push(`<rect class="aplat" x="${px(nb.x)}" y="${px(nb.y)}" width="${px(nb.w)}" height="${px(nb.h)}" rx="2"/>`);
      nb.txt.forEach((l, i) => o.push(`<text class="${l.cls}" x="${px(nb.x + 9)}" y="${px(nb.y + 19 + i * 15)}">${esc(l.t)}</text>`));
    }
    return o.join('');
  }

  /* ---------- Carte : premier plan (repère, aperçu, balises, étiquettes) ---------- */
  /* Placement par priorité : le repère et l'aperçu restent contre leur point ; les étiquettes secondaires
     prennent la place libre la plus proche, ou s'effacent si elles tomberaient trop loin de leur ancre. */
  function placer(items, ymin, ymax) {
    const poses = [];
    items.slice().sort((a, b) => a.prio - b.prio || a.y - b.y).forEach((it) => {
      const voulu = Math.min(Math.max(it.y - it.h / 2, ymin), ymax - it.h);
      const cands = [voulu];
      poses.forEach((p) => cands.push(p.top - it.h - 5, p.top + p.h + 5));
      let best = null;
      cands.forEach((t) => {
        if (t < ymin - 0.5 || t + it.h > ymax + 0.5) return;
        if (poses.some((p) => t < p.top + p.h + 5 - 0.01 && p.top < t + it.h + 5 - 0.01)) return;
        if (best == null || Math.abs(t - voulu) < Math.abs(best - voulu)) best = t;
      });
      if (best == null || (it.prio >= 3 && Math.abs(best - voulu) > 110)) { if (it.prio <= 1) best = voulu; else { it.cache = true; return; } }
      it.top = best;
      poses.push(it);
    });
    return items.filter((it) => !it.cache);
  }
  const chevauche = (a, b) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;

  function avant(T, G) {
    const o = [], etiq = [], d = AF.dossier(), st = AF.statut(), br = AF.brouillon();
    const bMeme = br && br.cas === T.cas;
    const yCour = G.yM(T.e.montant);
    const bord = G.cote > 0 ? G.xdr : G.xg;
    const dispo = G.cote > 0 ? G.x1 - G.xdr - 30 : G.xg - G.x0 - 30;
    const maxL = Math.max(120, Math.min(260, dispo));
    const ajouter = (y, lignes, genre, prio, extra = {}) => {
      const lg = lignes.flatMap((l) => couper(l.t, l.cls, maxL - 16).map((t) => ({ t, cls: l.cls })));
      const w = Math.min(maxL, Math.max(...lg.map((l) => largeur(l.t, l.cls))) + 16);
      const h = lg.length * 15 + 9;
      etiq.push({ y, lignes: lg, w, h, h0: h, genre, prio, ...extra });
      return etiq[etiq.length - 1];
    };
    const ops = (d.options || []).filter((op) => op.nom !== 'Ta demande' && op.ticker === d.demande.ticker && op.horizon_ans === T.hDecl && op.montant_cad !== T.e.montant);
    const montantsOptions = new Set(ops.map((op) => op.montant_cad));

    /* Couloir de l'horizon déclaré */
    o.push(`<rect class="couloir" x="${px(G.xg - 2)}" y="${px(G.y0 - 2)}" width="${px(G.cw + 4)}" height="${px(G.y1 - G.y0 + 4)}"/>`);
    o.push(`<rect class="couloir-int" x="${px(G.xg + 1.5)}" y="${px(G.y0 + 1.5)}" width="${px(G.cw - 3)}" height="${px(G.y1 - G.y0 - 3)}"/>`);
    const titreC = `Ton horizon · ${T.hDecl} ans`;
    const wT = largeur(titreC, 't-etiq-fort') + 16;
    const xT = Math.min(Math.max(G.xd - wT / 2, G.x0), G.x1 - wT);
    o.push(`<rect class="aplat" x="${px(xT)}" y="${px(G.y0 - 36)}" width="${px(wT)}" height="20" rx="2"/><text class="t-etiq-fort" x="${px(xT + 8)}" y="${px(G.y0 - 22)}">${esc(titreC)}</text>`);

    /* Stations : un dossier réel par montant précalculé */
    T.stations.forEach((s) => {
      const y = px(G.yM(s.montant));
      if (s.dansGrille) o.push(`<path class="station" d="M${px(G.xg - 7)} ${px(y - 5)}L${px(G.xg - 1)} ${y}L${px(G.xg - 7)} ${px(y + 5)}Z M${px(G.xdr + 7)} ${px(y - 5)}L${px(G.xdr + 1)} ${y}L${px(G.xdr + 7)} ${px(y + 5)}Z"/>`);
      else {
        o.push(`<path class="station-hors" d="M${px(G.xg - 8)} ${px(y - 5)}L${px(G.xg - 1)} ${y}L${px(G.xg - 8)} ${px(y + 5)}Z M${px(G.xdr + 8)} ${px(y - 5)}L${px(G.xdr + 1)} ${y}L${px(G.xdr + 8)} ${px(y + 5)}Z"/><line class="couloir-int" x1="${px(G.xg)}" y1="${y}" x2="${px(G.xdr)}" y2="${y}" stroke-dasharray="2 2"/>`);
        if (approfondi() && !montantsOptions.has(s.montant)) ajouter(G.yM(s.montant), [{ t: `${fmt.cad(s.montant)} · dossier hors grille`, cls: 't-etiq-fort' }, { t: `${court(s.etat)} (verdict de son propre dossier)`, cls: 't-etiq' }], 'doux', 5);
      }
    });
    if (!T.grille) {
      /* Colonne seule : chaque série d'états identiques est nommée à côté de la colonne. */
      let k = 0;
      while (k < T.stations.length) {
        let j = k; while (j + 1 < T.stations.length && T.stations[j + 1].etat === T.stations[k].etat) j++;
        const yA = G.yM(T.stations[k].montant), yB = G.yM(T.stations[j].montant);
        ajouter((yA + yB) / 2, [{ t: court(T.stations[k].etat), cls: 't-zone' }, { t: k === j ? fmt.cad(T.stations[k].montant) : `${fmt.cad(T.stations[k].montant)} à ${fmt.cad(T.stations[j].montant)}`, cls: 't-zone-sous' }], 'zone', 2);
        k = j + 1;
      }
    }

    /* Frontières annotées (Approfondi) : la règle qui bascule, lue dans les dossiers voisins */
    if (approfondi()) {
      bascules(T).forEach((bq) => {
        const y = (G.yM(bq.a.montant) + G.yM(bq.b.montant)) / 2;
        if (!bq.verdict) o.push(`<line class="frontiere-regle" x1="${px(G.xg - 10)}" y1="${px(y)}" x2="${px(G.xdr + 10)}" y2="${px(y)}"/>`);
        const lignes = [{ t: `${bq.verdict ? 'Frontière lue' : 'Règle seule'} · ${fmt.cad(bq.a.montant)} → ${fmt.cad(bq.b.montant)}`, cls: 't-etiq-fort' }];
        if (bq.verdict) lignes.push({ t: `Verdict : ${court(bq.a.etat)} → ${court(bq.b.etat)}`, cls: 't-etiq' });
        bq.regles.forEach((r) => lignes.push({ t: `${r.libelle} : ${nivMin(r.avant)} → ${nivMin(r.apres)}`, cls: 't-etiq' }));
        ajouter(y, lignes, bq.verdict ? 'fort' : 'doux', bq.verdict ? 2 : 4);
      });
    }

    /* Options du dossier sur le même actif et le même horizon */
    ops.forEach((op) => {
      const y = G.yM(op.montant_cad), sta = T.stations.find((s) => s.montant === op.montant_cad);
      const x = G.cote > 0 ? G.xdr + 16 : G.xg - 16;
      o.push(`<g class="option-g" ${sta ? `data-action="montant" data-valeur="${op.montant_cad}" style="cursor:pointer"` : ''}><title>${esc(op.nom)} : ${esc(fmt.cad(op.montant_cad))}</title><circle cx="${px(x)}" cy="${px(y)}" r="14" fill="transparent"/><path class="option-mark" d="M${px(x)} ${px(y - 6)}L${px(x + 6)} ${px(y)}L${px(x)} ${px(y + 6)}L${px(x - 6)} ${px(y)}Z"/></g>`);
      ajouter(y, [{ t: `◆ ${op.nom}`, cls: 't-etiq-fort' }, { t: `${fmt.cad(op.montant_cad)} · ${court(op.etat)}${!sta ? ' · sans dossier' : sta.dansGrille ? '' : ' · hors grille'}`, cls: 't-etiq' }], 'doux', 3, { ax: x + G.cote * 7 });
    });

    /* Itinéraire : une balise numérotée par révision de cette situation, reliées dans l'ordre */
    const H = hist(), p = pos(), dernier = H.length - 1;
    const vus = new Map(), balises = [];
    H.forEach((h, i) => {
      if (h.etat.cas !== T.cas) return;
      const k = vus.get(h.etat.montant) || 0; vus.set(h.etat.montant, k + 1);
      const libre = G.cote > 0 ? G.xd - G.cw / 2 - 14 - (G.x0 + 10) : G.x1 - 10 - (G.xd + G.cw / 2 + 14);
      const x = G.xd - G.cote * (G.cw / 2 + 14 + Math.min(k, 4, Math.max(0, Math.floor(libre / 21))) * 21);
      balises.push({ i, x, y: G.yM(h.etat.montant), h });
    });
    let trace = '';
    for (let k = 0; k < balises.length - 1; k++) {
      const a = balises[k], b = balises[k + 1];
      if (b.i !== a.i + 1) continue;
      const cx = (a.x + b.x) / 2 - G.cote * (12 + Math.min(40, Math.abs(b.y - a.y) * 0.15));
      trace += `M${px(a.x)} ${px(a.y)}Q${px(cx)} ${px((a.y + b.y) / 2)} ${px(b.x)} ${px(b.y)}`;
    }
    if (trace) o.push(`<path class="trajet" d="${trace}"/>`);
    const rB = G.etroit ? 10 : 9;
    balises.forEach((b) => {
      const cls = `balise${b.i === p ? ' affichee' : ''}`;
      o.push(`<g class="${cls}" data-action="rev" data-valeur="${b.i}"><title>Révision ${b.i + 1} · ${esc(fmt.cad(b.h.etat.montant))} · ${esc(court(b.h.verdict))}${b.i === dernier ? ' · dernière' : ''}</title><circle class="b-cible" cx="${px(b.x)}" cy="${px(b.y)}" r="${G.etroit ? 20 : 15}"/>${b.i === dernier ? `<circle cx="${px(b.x)}" cy="${px(b.y)}" r="${rB + 3.5}" fill="none" stroke="#17241f" stroke-width="1"/>` : ''}<circle class="b-fond" cx="${px(b.x)}" cy="${px(b.y)}" r="${rB}"/><text class="t-balise" x="${px(b.x)}" y="${px(b.y + 0.5)}">${b.i + 1}</text></g>`);
    });

    /* Repère sur l'axe des montants */
    o.push(`<path d="M${px(G.x0 - 2)} ${px(yCour - 5)}L${px(G.x0 + 5)} ${px(yCour)}L${px(G.x0 - 2)} ${px(yCour + 5)}Z" fill="#b33c0a"/>`);

    /* Repère « ta demande » (ou archive) */
    const xr = G.xd;
    if (st === 'archive') {
      o.push(`<rect class="repere-archive" x="${px(xr - 9)}" y="${px(yCour - 9)}" width="18" height="18"/>`);
      ajouter(yCour, [{ t: `Archive · révision ${p + 1} · ${fmt.cad(T.e.montant)}`, cls: 't-etiq-fort' }, { t: `${court(d.verdict.etat)} · relue, non courante`, cls: 't-etiq' }], 'fort', 0, { ax: xr + G.cote * 10 });
    } else {
      o.push(`<line class="repere-croix" x1="${px(G.xg)}" y1="${px(yCour)}" x2="${px(G.xdr)}" y2="${px(yCour)}"/><circle class="repere-plein" cx="${px(xr)}" cy="${px(yCour)}" r="8"/><circle class="repere-cercle" cx="${px(xr)}" cy="${px(yCour)}" r="12.5"/>`);
      ajouter(yCour, [{ t: `Ta demande · ${fmt.cad(T.e.montant)}`, cls: 't-repere' }, { t: `${court(d.verdict.etat)} · révision ${p + 1}${st === 'apercu' ? ' (sondée)' : ''}`, cls: 't-etiq' }], 'accent', 0, { ax: xr + G.cote * 13 });
    }

    /* Aperçu : repère fantôme, non sondé ; on réserve la place du bouton « Sonder ici » contre son étiquette */
    vue.boiteSonder = null;
    let fantome = null;
    const bw = 108, bh = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--cible')) || 32;
    if (bMeme) {
      const yF = G.yM(br.montant);
      const memeMontant = br.montant === T.e.montant;
      if (!memeMontant) o.push(`<line class="deplacement" x1="${px(xr)}" y1="${px(yCour + (yF < yCour ? -14 : 14))}" x2="${px(xr)}" y2="${px(yF + (yF < yCour ? 16 : -16))}" marker-end="url(#fl-accent)"/>`);
      o.push(`<circle class="repere-fantome" cx="${px(xr)}" cy="${px(yF)}" r="${memeMontant ? 17 : 11}"/>`);
      const params = br.retrait !== T.e.retrait || br.exclusion !== T.e.exclusion;
      fantome = ajouter(yF, [{ t: `Aperçu · ${fmt.cad(br.montant)}`, cls: 't-repere' }, { t: params ? 'non sondé · terrain à relever' : `non sondé · zone ${court(etatStation(T, br.montant))} sur la carte`, cls: 't-etiq' }], 'accent', 0, { ax: xr + G.cote * (memeMontant ? 18 : 12) });
      fantome.cote = fantome.w + 8 + bw <= dispo;
      fantome.h = fantome.cote ? Math.max(fantome.h0, bh) : fantome.h0 + bh + 5;
    }

    /* Placement des étiquettes sur le côté libre, sans chevauchement */
    const visibles = placer(etiq, G.y0 + 2, G.y1 - 2);
    const boites = [];
    visibles.forEach((it) => {
      const x = G.cote > 0 ? Math.min(bord + 22, G.x1 - it.w - 2) : Math.max(bord - 22 - it.w, G.x0 + 2);
      const ax = it.ax != null ? it.ax : bord + G.cote * 2;
      const bx = G.cote > 0 ? x : x + it.w;
      const by = Math.min(Math.max(it.y, it.top + 6), it.top + it.h0 - 6);
      const cls = it.genre === 'accent' ? 'aplat-accent' : it.genre === 'doux' ? 'aplat-doux' : 'aplat';
      o.push(`<path class="${it.genre === 'accent' ? 'leader-accent' : 'leader'}" d="M${px(ax)} ${px(it.y)}L${px((ax + bx) / 2)} ${px(it.y)}L${px(bx)} ${px(by)}"/>`);
      o.push(`<rect class="${cls}" x="${px(x)}" y="${px(it.top)}" width="${px(it.w)}" height="${px(it.h0)}" rx="2"/>`);
      it.lignes.forEach((l, i) => o.push(`<text class="${l.cls}" x="${px(x + 8)}" y="${px(it.top + 16 + i * 15)}">${esc(l.t)}</text>`));
      boites.push({ x, y: it.top, w: it.w, h: it.h0 });
      if (it === fantome) {
        const sb = it.cote
          ? { x: G.cote > 0 ? x + it.w + 8 : x - 8 - bw, y: it.top + (Math.max(it.h0, bh) - bh) / 2, w: bw, h: bh }
          : { x, y: it.top + it.h0 + 5, w: bw, h: bh };
        vue.boiteSonder = sb;
        boites.push(sb);
      }
    });

    /* Libellés des zones, posés sur aplat là où ils ne gênent rien */
    if (T.grille) o.push(etiquettesZones(T, G, boites));
    return o.join('');
  }

  function etiquettesZones(T, G, obstacles) {
    const nC = T.horizons.length, nR = T.montants.length;
    const st = (c, r) => T.cases.get(`${T.montants[r]}|${T.horizons[c]}`);
    const obs = obstacles.slice();
    const xa = G.cote > 0 ? G.xg - 64 : G.xg - 6, xb = G.cote > 0 ? G.xdr + 6 : G.xdr + 64; // couloir et balises
    obs.push({ x: xa, y: G.y0 - 40, w: xb - xa, h: G.y1 - G.y0 + 40 });
    const nb = boiteNote(T, G); if (nb) obs.push(nb);
    const vu = new Set(), comps = [];
    for (let c = 0; c < nC; c++) for (let r = 0; r < nR; r++) {
      if (vu.has(`${c},${r}`)) continue;
      const e = st(c, r), cells = [], pile = [[c, r]]; vu.add(`${c},${r}`);
      while (pile.length) {
        const [a, b] = pile.pop(); cells.push([a, b]);
        [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(([da, db]) => {
          const na = a + da, nb2 = b + db, k = `${na},${nb2}`;
          if (na < 0 || nb2 < 0 || na >= nC || nb2 >= nR || vu.has(k) || st(na, nb2) !== e) return;
          vu.add(k); pile.push([na, nb2]);
        });
      }
      comps.push({ e, cells });
    }
    comps.sort((a, b) => b.cells.length - a.cells.length);
    const faits = new Set(), out = [];
    comps.forEach((comp) => {
      if (comp.cells.length < 3 && faits.has(comp.e)) return;
      const dans = new Set(comp.cells.map(([a, b]) => `${a},${b}`));
      const t1 = court(comp.e), t2 = approfondi() ? `${pluriel(comp.cells.length, 'case')} calculée${comp.cells.length > 1 ? 's' : ''}` : '';
      const w = Math.max(largeur(t1, 't-zone'), t2 ? largeur(t2, 't-zone-sous') : 0) + 18, h = t2 ? 34 : 22;
      const cu = comp.cells.reduce((s, [a]) => s + a, 0) / comp.cells.length, cv = comp.cells.reduce((s, [, b]) => s + b, 0) / comp.cells.length;
      let best = null;
      comp.cells.forEach(([c, r]) => {
        if (c === G.ic) return;
        let cl = c, cr = c;
        while (cl - 1 >= 0 && cl - 1 !== G.ic && dans.has(`${cl - 1},${r}`)) cl--;
        while (cr + 1 < nC && cr + 1 !== G.ic && dans.has(`${cr + 1},${r}`)) cr++;
        const xa = G.x0 + cl * G.cw, xb = G.x0 + (cr + 1) * G.cw;
        if (xb - xa < w + 6 || G.rh < h - 4) return;
        const xc = Math.min(Math.max(G.x0 + (c + 0.5) * G.cw, xa + w / 2 + 3), xb - w / 2 - 3);
        const yc = G.yRow(r);
        const boite = { x: xc - w / 2, y: yc - h / 2, w, h };
        if (obs.some((b) => chevauche(boite, b)) || out.some((b) => chevauche(boite, b))) return;
        const score = -Math.hypot(c + 0.5 - cu, (r + 0.5 - cv) * 1.6);
        if (!best || score > best.score) best = { ...boite, score };
      });
      if (!best) return;
      faits.add(comp.e); out.push(best);
      best.html = `<rect class="aplat-doux" x="${px(best.x)}" y="${px(best.y)}" width="${px(best.w)}" height="${px(best.h)}" rx="2"/><text class="t-zone" x="${px(best.x + best.w / 2)}" y="${px(best.y + 15.5)}" text-anchor="middle">${esc(t1)}</text>${t2 ? `<text class="t-zone-sous" x="${px(best.x + best.w / 2)}" y="${px(best.y + 28)}" text-anchor="middle">${esc(t2)}</text>` : ''}`;
    });
    return out.map((b) => b.html).join('');
  }

  /* ---------- Carte : orchestration ---------- */
  function rendreBande() {
    const el = $('#bande-carte');
    let html = '', cls = '';
    const s = AF.statut(), n = hist().length, p = pos();
    if (vue.special) {
      /* Le voile du cas particulier porte déjà son message et son retour. */
    } else if (s === 'archive') {
      cls = 'b-archive';
      html = `<span class="pc">Archive · R${p + 1}</span><span class="bande-txt">Tu relis la révision ${p + 1} sur ${n}, telle qu’elle a été sondée. Rien n’est modifié.</span><button type="button" class="bouton bouton-plein" data-action="restaurer" data-cle="restaurer-carte">Revenir ici</button><button type="button" class="bouton" data-action="courante" data-cle="courante-carte"><span class="txt-ordi">Révision courante</span><span class="txt-mobile">Courante</span> (${n})</button>`;
    } else if (s === 'apercu') {
      const b = AF.brouillon(), e = AF.etat();
      if (b.cas === e.cas && (b.retrait !== e.retrait || b.exclusion !== e.exclusion)) {
        cls = 'b-apercu';
        html = `<span class="pc">Aperçu</span><span class="bande-txt">${esc(AF.decrire(e, b))}. Le terrain changera après le sondage.</span><button type="button" class="bouton bouton-accent" data-action="sonder" data-cle="sonder-bande">Sonder ici</button><button type="button" class="bouton" data-action="abandonner" data-cle="abandonner-bande">Abandonner</button>`;
      }
    }
    el.className = `bande-carte ${cls}`;
    el.hidden = !html;
    el.innerHTML = html;
    return html ? el.offsetHeight : 0;
  }

  function rendreCarte() {
    const cadre = $('#carte-cadre'), svg = $('#carte');
    const W = cadre.clientWidth, H = cadre.clientHeight;
    if (!W || !H) return;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const bandeH = rendreBande();
    cadre.classList.toggle('archive', AF.statut() === 'archive' && !vue.special);
    const poignee = $('#poignee');
    if (vue.special) {
      const y0 = 24 + bandeH;
      $('#c-fond').innerHTML = `<rect x="24" y="${y0}" width="${W - 48}" height="${Math.max(0, H - y0 - 24)}" fill="url(#m-indetermine)"/><rect class="cadre-plot" x="24" y="${y0}" width="${W - 48}" height="${Math.max(0, H - y0 - 24)}"/>`;
      cacheFond.cle = null;
      $('#c-avant').innerHTML = '';
      poignee.setAttribute('aria-disabled', 'true'); poignee.tabIndex = -1;
      $('#sonder-carte').hidden = true;
      vue.sonde = vue.survol = null; rendreSonde();
      $('#carte-desc').textContent = `Cas particulier : ${SPECIAUX[vue.special]}. Aucune carte n’est levée.`;
      $('#note-carte').hidden = true;
      Tc = Gc = null;
      return;
    }
    const T = terrain(), G = geometrie(T, W, H, bandeH), cols = colonnes(T, G);
    Tc = T; Gc = G;
    const cle = [T.cle, W, H, bandeH, AF.niveau()].join('#');
    if (cacheFond.cle !== cle) { $('#c-fond').innerHTML = fond(T, G, cols); cacheFond.cle = cle; }
    $('#c-avant').innerHTML = avant(T, G);

    /* Poignée (élément HTML persistant : le focus clavier survit aux redessins) */
    const br = AF.brouillon(), vise = br && br.cas === T.cas ? br.montant : T.e.montant;
    const ms = T.stations.map((s) => s.montant);
    poignee.removeAttribute('aria-disabled'); poignee.tabIndex = 0;
    poignee.style.left = `${px(G.xd)}px`; poignee.style.top = `${px(G.yM(vise))}px`;
    poignee.setAttribute('aria-label', `Ta demande sur la carte, colonne ${T.hDecl} ans. Flèches haut et bas : changer de montant. Entrée : sonder. Échap : abandonner l’aperçu.`);
    poignee.setAttribute('aria-valuemin', String(ms[0]));
    poignee.setAttribute('aria-valuemax', String(ms[ms.length - 1]));
    poignee.setAttribute('aria-valuenow', String(vise));
    poignee.setAttribute('aria-valuetext', br && br.cas === T.cas
      ? `${fmt.cad(vise)} : aperçu non sondé, zone ${court(etatStation(T, vise))} sur la carte. Entrée pour sonder.`
      : `${fmt.cad(vise)} : révision ${pos() + 1}, ${AF.dossier().verdict.libelle}${AF.statut() === 'archive' ? ' (archive)' : ''}.`);

    /* Bouton « Sonder ici » posé contre l'étiquette de l'aperçu */
    const bs = $('#sonder-carte');
    if (AF.perime() && vue.boiteSonder) {
      const b = vue.boiteSonder;
      bs.hidden = false;
      bs.style.left = `${px(Math.min(Math.max(b.x, 4), W - b.w - 4))}px`;
      bs.style.top = `${px(Math.min(Math.max(b.y, 4 + bandeH), H - b.h - 4))}px`;
    } else bs.hidden = true;

    /* Note de carte en flux sur petit écran */
    const note = $('#note-carte'), lignes = noteCarte(T);
    if (lignes.length && !boiteNote(T, G)) { note.hidden = false; note.innerHTML = `<strong>${esc(lignes[0])}</strong> ${esc(lignes.slice(1).join(' '))}`; } else note.hidden = true;

    $('#carte-desc').textContent = descCarte(T);
    rendreSonde();
  }

  function descCarte(T) {
    const d = AF.dossier(), b = bascules(T).filter((x) => x.verdict);
    let t = `Carte de ${AF.nomCas(T.cas)} : ${T.horizons.length} horizons de ${T.horizons[0]} à ${T.horizons[T.horizons.length - 1]} ans en colonnes, ${T.montants.length} montants de ${fmt.cad(T.montants[0])} à ${fmt.cad(T.montants[T.montants.length - 1])} en rangées. `;
    t += `Ta demande : ${fmt.cad(T.e.montant)} à ${T.hDecl} ans, ${d.verdict.libelle}. `;
    if (!T.grille) t += 'Hors de ta colonne, le terrain n’est pas levé avec ce paramètre. ';
    if (b.length) t += `Frontières lues dans ta colonne : ${b.map((x) => `entre ${fmt.cad(x.a.montant)} et ${fmt.cad(x.b.montant)}`).join(' ; ')}. `;
    return `${t}Équivalent en tableau : section « Tableau » de la coupe.`;
  }

  /* ---------- Sonde : état d'une case (survol ou clic) ---------- */
  function cible(x, y) {
    const T = Tc, G = Gc;
    if (!T || x < G.x0 || x > G.x1 || y < G.y0 || y > G.y1) return null;
    const c = Math.min(G.nC - 1, Math.floor((x - G.x0) / G.cw)), r = Math.min(G.nR - 1, Math.floor((G.y1 - y) / G.rh));
    if (c === G.ic || Math.abs(x - G.xd) <= Math.max(G.cw / 2, 22)) {
      let m = T.stations[0].montant, dm = Infinity;
      T.stations.forEach((s) => { const dd = Math.abs(G.yM(s.montant) - y); if (dd < dm) { dm = dd; m = s.montant; } });
      return { type: 'station', m };
    }
    return { type: 'case', c, r };
  }
  const memeCible = (a, b) => !!a && !!b && a.type === b.type && a.m === b.m && a.c === b.c && a.r === b.r;

  function rendreSonde() {
    const el = $('#sonde'), g = $('#c-sonde');
    const s = vue.sonde || vue.survol;
    if (!s || !Tc || vue.special) { el.hidden = true; g.innerHTML = ''; return; }
    const T = Tc, G = Gc;
    let html = '', x, y, w, h;
    if (s.type === 'case') {
      const m = T.montants[s.r], hz = T.horizons[s.c];
      x = G.x0 + s.c * G.cw; y = G.y1 - (s.r + 1) * G.rh; w = G.cw; h = G.rh;
      html = `<p class="sonde-coord">${esc(fmt.cad(m))} × ${pluriel(hz, 'an')}</p>`;
      if (T.grille) {
        const e = T.cases.get(`${m}|${hz}`);
        html += `<p class="sonde-etat"><span class="leg-swatch motif-${e}" aria-hidden="true"></span><strong>${esc(court(e))}</strong></p><p class="sonde-note">État calculé par le moteur ; détail non précalculé dans ce prototype.</p>`;
        if (approfondi()) html += `<p class="sonde-note">Un dossier complet n’existe que dans ta colonne (${T.hDecl} ans), pour chaque montant précalculé.</p>`;
      } else {
        html += `<p class="sonde-etat"><span class="leg-swatch" style="background:#f0f1ec" aria-hidden="true"></span><strong>Terrain non levé</strong></p><p class="sonde-note">La grille de départ ne s’applique pas avec ${esc(paramTexte(T.e))}. Seule ta colonne est connue.</p>`;
      }
    } else {
      const sta = T.stations.find((q) => q.montant === s.m);
      x = G.xg; y = G.yM(s.m) - 14; w = G.cw; h = 28;
      html = `<p class="sonde-coord">${esc(fmt.cad(s.m))} × ${pluriel(T.hDecl, 'an')}</p><p class="sonde-etat"><span class="leg-swatch motif-${sta.etat}" aria-hidden="true"></span><strong>${esc(court(sta.etat))}</strong></p><p class="sonde-note">Dossier réel précalculé${sta.dansGrille ? '' : ', hors de la grille'}. Cliquer place l’aperçu ici ; « Sonder ici » l’analyse.</p>`;
    }
    if (vue.sonde) html += '<button type="button" class="sonde-fermer" data-action="fermer-sonde" data-cle="fermer-sonde" aria-label="Fermer la sonde">✕</button>';
    g.innerHTML = `<rect class="sonde-case" x="${px(x + 1)}" y="${px(y + 1)}" width="${px(w - 2)}" height="${px(h - 2)}"/>`;
    el.innerHTML = html;
    el.hidden = false;
    el.classList.toggle('survol', !vue.sonde);
    if (vue.sonde) { el.setAttribute('role', 'region'); el.setAttribute('aria-label', 'Sonde de la carte'); el.removeAttribute('aria-hidden'); }
    else { el.removeAttribute('role'); el.setAttribute('aria-hidden', 'true'); }
    const ew = el.offsetWidth, eh = el.offsetHeight;
    let left = x + w + 10;
    if (left + ew > G.W - 6) left = x - ew - 10;
    el.style.left = `${px(Math.max(6, left))}px`;
    el.style.top = `${px(Math.min(Math.max(6, y - 6), G.H - eh - 6))}px`;
  }

  /* ---------- Manipulation du repère ---------- */
  function montantVise() { const b = AF.brouillon(), e = AF.etat(); return b && b.cas === e.cas ? b.montant : e.montant; }
  function proposerMontant(m) { if (vue.special) return; if (m !== montantVise()) AF.proposer({ montant: m }); }
  function stationPlusProche(yLocal) {
    let m = Tc.stations[0].montant, dm = Infinity;
    Tc.stations.forEach((s) => { const dd = Math.abs(Gc.yM(s.montant) - yLocal); if (dd < dm) { dm = dd; m = s.montant; } });
    return m;
  }
  function sonder() {
    if (!AF.perime()) return;
    AF.appliquer();
  }
  function annuler() {
    if (AF.perime()) { AF.abandonner(); return; }
    if (!AF.annuler()) annoncer('Rien à annuler : cette révision n’a pas de révision parente.');
  }
  function retablir() { if (!AF.retablir()) annoncer('Rien à rétablir.'); }

  /* ---------- En-tête, légende, liste, itinéraire, cartouche ---------- */
  function rendreEntete() {
    const m = AF.meta;
    $('#meta').textContent = `généré le ${fmt.date(String(m.genere_le).slice(0, 10))} · commit ${m.commit}`;
    $('#meta').title = m.mode;
    const e = AF.etat();
    $('#choix-cas').innerHTML = AF.cas().map((c) => `<button type="button" data-action="cas" data-valeur="${c}" data-cle="cas-${c}" aria-pressed="${!vue.special && e.cas === c}">${esc(AF.nomCas(c))}</button>`).join('');
    $('#speciaux-corps').innerHTML = `${Object.entries(SPECIAUX).map(([k, l]) => `<button type="button" class="bouton" data-action="special" data-valeur="${k}" data-cle="sp-${k}" aria-pressed="${vue.special === k}">${esc(l)}</button>`).join('')}<p class="menu-note">Résultats réels du moteur, hors itinéraire. « Indéterminé » y est un vrai verdict.</p>`;
    $$('[data-niveau]').forEach((b) => { b.setAttribute('aria-pressed', String(AF.niveau() === b.dataset.niveau)); b.dataset.action = 'niveau'; b.dataset.valeur = b.dataset.niveau; });
    $('#liens-corps').innerHTML = `<a class="bouton" href="${esc(AF.lien('../index.html'))}">Galerie des cinq directions</a>${AUTRES.map(([d, n]) => `<a class="bouton" href="${esc(AF.lien(`../${d}/index.html`))}">${esc(n)}</a>`).join('')}<p class="menu-note">Les autres pages retrouvent le même cas, le même état et le même historique.</p>`;
    $('#demo').value = vue.demo;
  }

  function rendreLegende() {
    $('#leg-zones').innerHTML = `${['coherent', 'ajustement', 'incoherent', 'indetermine'].map((e) => `<span class="leg-zone"><span class="leg-swatch motif-${e}" aria-hidden="true"></span><span class="pc">${esc(court(e))}</span></span>`).join('')}`;
    const params = $('#leg-params');
    if (vue.special) { params.innerHTML = '<span class="leg-fixe">Cas particulier : aucun paramètre.</span>'; }
    else {
      const e = AF.etat(), b = AF.brouillon(), cible2 = b && b.cas === e.cas ? b : e, p = AF.parametres();
      let h = '';
      if (p.retrait.length > 1) h += `<span class="leg-param"><span class="petit-titre" id="lp-r">Retrait</span><span class="segment" role="group" aria-labelledby="lp-r">${p.retrait.map((r) => `<button type="button" data-action="param" data-valeur='${JSON.stringify({ retrait: r })}' data-cle="p-r-${r}" aria-pressed="${cible2.retrait === r}">${esc(r == null ? 'non précisé' : fmt.retrait(r))}</button>`).join('')}</span></span>`;
      if (p.exclusion.length > 1) h += `<span class="leg-param"><span class="petit-titre" id="lp-x">Exclure ${esc(secteurExclu(e.cas))}</span><span class="segment" role="group" aria-labelledby="lp-x">${p.exclusion.map((x) => `<button type="button" data-action="param" data-valeur='${JSON.stringify({ exclusion: x })}' data-cle="p-x-${x}" aria-pressed="${cible2.exclusion === x}">${x ? 'oui' : 'non'}</button>`).join('')}</span></span>`;
      if (!h) h = '<span class="leg-fixe">Montant seul précalculé</span>';
      params.innerHTML = h;
    }
    $('#liste-montants').innerHTML = htmlListe();
    $('#signes').innerHTML = htmlSignes();
  }

  function htmlListe() {
    if (vue.special || !Tc) return '<p class="note">Cas particulier : aucune carte levée, aucun montant à parcourir.</p>';
    const T = Tc, b = AF.brouillon(), ap = b && b.cas === T.cas ? b.montant : null;
    const items = [...T.stations].reverse().map((s) => {
      const cour = s.montant === T.e.montant, prop = ap === s.montant && !cour;
      return `<li><button type="button" data-action="montant" data-valeur="${s.montant}" data-cle="m-${s.montant}" aria-current="${cour}" class="${prop ? 'propose' : ''}"><span class="mini motif-${s.etat}" aria-hidden="true"></span><span><span class="m-val">${esc(fmt.cad(s.montant))}</span>${s.dansGrille ? '' : ' <span class="m-etat">hors grille</span>'}</span><span class="m-etat">${esc(court(s.etat))}${cour ? ' · ta demande' : ''}${prop ? ' · aperçu' : ''}</span></button></li>`;
    }).join('');
    return `<p class="note">Chaque montant a un dossier réel précalculé pour ton horizon de ${T.hDecl} ans (${esc(paramTexte(T.e))}). Choisir un montant place l’aperçu ; « Sonder ici » l’analyse.</p><ul class="liste-m">${items}</ul>${AF.perime() ? '<p style="margin-top:8px"><button type="button" class="bouton bouton-accent" data-action="sonder" data-cle="sonder-liste">Sonder ici</button></p>' : ''}`;
  }

  function htmlSignes() {
    const ico = (svg) => `<svg width="30" height="22" viewBox="0 0 30 22" aria-hidden="true">${svg}</svg>`;
    return `<ul class="signes">
      <li>${ico('<circle cx="15" cy="11" r="6" fill="#b33c0a" stroke="#fbfbf8" stroke-width="2"/><circle cx="15" cy="11" r="9.5" fill="none" stroke="#b33c0a" stroke-width="1.6"/>')}<span>Ta demande : la révision affichée. Seule la couleur d’accent de la carte.</span></li>
      <li>${ico('<circle cx="15" cy="11" r="8" fill="#f7e2d6" stroke="#b33c0a" stroke-width="2" stroke-dasharray="4 3"/>')}<span>Aperçu : point proposé, non sondé. La coupe devient périmée.</span></li>
      <li>${ico('<rect x="7" y="3" width="16" height="16" fill="#fbfbf8" stroke="#17241f" stroke-width="2" stroke-dasharray="2 2.5"/>')}<span>Archive : révision relue, non courante.</span></li>
      <li>${ico('<path d="M8 6L14 11L8 16Z M22 6L16 11L22 16Z" fill="#17241f"/>')}<span>Station : un dossier réel précalculé (ta colonne seulement). Creuse : hors grille.</span></li>
      <li>${ico('<circle cx="15" cy="11" r="8" fill="#fbfbf8" stroke="#17241f" stroke-width="1.5"/><text x="15" y="14.5" font-size="10" text-anchor="middle" font-weight="700" fill="#17241f">2</text>')}<span>Balise : une révision de l’itinéraire ; cliquer la relit.</span></li>
      <li>${ico('<path d="M15 4L21 11L15 18L9 11Z" fill="#fbfbf8" stroke="#17241f" stroke-width="1.5"/>')}<span>Option du dossier sur le même actif.</span></li>
      <li>${ico('<path d="M2 11H28" stroke="#fbfbf8" stroke-width="6"/><path d="M2 11H28" stroke="#17241f" stroke-width="3"/>')}<span>Frontière de verdict. Dans ta colonne, la règle qui bascule est lue dans les dossiers voisins (Approfondi) ; ailleurs, elle n’est pas lue.</span></li>
      <li>${ico('<path d="M2 11H28" stroke="#17241f" stroke-width="1.5" stroke-dasharray="5 4"/>')}<span>Frontière de règle : une règle change, le verdict non (Approfondi).</span></li>
      <li>${ico('<path d="M2 15C8 5 14 17 20 8S26 10 28 6" fill="none" stroke="#64776f" stroke-width="1"/>')}<span>Courbes fines : matière décorative, sans aucune valeur de mesure.</span></li>
      <li>${ico('<rect x="3" y="3" width="24" height="16" fill="url(#m-horsleve)" stroke="#17241f"/>')}<span>Terrain non levé : aucun état connu.</span></li>
    </ul>`;
  }

  function rendreItineraire() {
    const H = hist(), p = pos(), n = H.length;
    $('#iti-liste').innerHTML = H.map((h, i) => {
      const saut = i > 0 && H[i - 1].etat.cas !== h.etat.cas;
      const label = `Révision ${i + 1} : ${h.nom}, ${fmt.cad(h.etat.montant)}, ${paramTexte(h.etat)}. ${AF.ETATS[h.verdict] ? AF.ETATS[h.verdict].long : h.verdict}. ${h.motif}.${i === p && !vue.special ? ' Affichée.' : ''}${i === n - 1 ? ' Dernière.' : ''}`;
      return `<li class="${saut ? 'saut' : ''}"><button type="button" class="iti-btn" data-action="rev" data-valeur="${i}" data-cle="rev-${i}" aria-current="${i === p && !vue.special}" aria-label="${esc(label)}"><span class="no">${i + 1}</span><span class="mini motif-${h.verdict}" aria-hidden="true"></span><span class="txt">${esc(h.nom)} · ${esc(fmt.cad(h.etat.montant))}</span>${i === n - 1 ? '<span class="derniere">dernière</span>' : ''}</button></li>`;
    }).join('');
    const an = $('#annuler'), re = $('#retablir');
    an.setAttribute('aria-disabled', String(!(AF.perime() || AF.peutAnnuler())));
    re.setAttribute('aria-disabled', String(!AF.peutRetablir()));
    an.dataset.action = 'annuler'; re.dataset.action = 'retablir';
    const ol = $('#iti-liste'), cur = ol.children[p];
    if (cur) { const l = cur.offsetLeft, r = l + cur.offsetWidth; if (l < ol.scrollLeft) ol.scrollLeft = l - 8; else if (r > ol.scrollLeft + ol.clientWidth) ol.scrollLeft = r - ol.clientWidth + 8; }
  }

  function rendreCartouche() {
    const d = dossierAffiche() || dossierDepart('robert');
    const pr = d.profil, k = d.comparaison;
    const fen = k && k.fenetre ? `${k.fenetre.debut} → ${k.fenetre.fin}` : '—';
    const cw = Gc ? Gc.cw : 20;
    const na = Math.max(1, Math.min(5, Math.floor(110 / cw))), L = px(cw * na);
    const echelle = `<svg width="${px(L + 44)}" height="22" viewBox="0 0 ${px(L + 44)} 22" role="img" aria-label="Échelle : ${na} an${na > 1 ? 's' : ''} d’horizon"><path d="M2 12H${px(L + 2)}" stroke="#17241f" stroke-width="2"/><path d="M2 7V16M${px(L + 2)} 7V16M${px(cw + 2)} 9V14" stroke="#17241f" stroke-width="1.5"/><rect x="2" y="10" width="${px(cw)}" height="4" fill="#17241f"/><text x="${px(L + 7)}" y="16" font-size="11" fill="#17241f">${na} an${na > 1 ? 's' : ''}</text></svg>`;
    const rose = '<svg width="44" height="44" viewBox="0 0 44 44" role="img" aria-label="Rose : vers le haut, montant plus élevé ; vers la droite, horizon plus long"><circle cx="22" cy="22" r="11" fill="none" stroke="#3a4d47"/><path d="M22 3L25 19L22 22L19 19Z" fill="#17241f"/><path d="M41 22L25 25L22 22L25 19Z" fill="#17241f"/><path d="M22 41L19 25L22 22L25 25Z M3 22L19 19L22 22L19 25Z" fill="#fbfbf8" stroke="#17241f"/><text x="27.5" y="9" font-size="8.5" font-weight="700" fill="#17241f">$</text><text x="35" y="33" font-size="8" font-weight="700" fill="#17241f">an</text></svg>';
    $('#cartouche').innerHTML = `<div class="cart-grille">
      <div class="cart-titre">SECOND AVIS — RELIEF</div><div class="cart-no">${vue.special ? 'hors feuille' : `feuille R${pos() + 1}`}</div>
      <div class="plein"><span class="cart-k">Levé</span>${esc(pr.nom)}, ${esc(pr.age)} ans · <strong>${esc(d.demande.ticker)}</strong> ${esc(nomActif(d.demande.ticker))}</div>
      <div class="plein cart-demande" title="${esc(d.demande.texte)}">« ${esc(d.demande.texte)} »</div>
      <div class="obs"><span class="cart-k">Observé</span>${esc(fen)}</div><div class="cart-rose dernier" style="grid-row: span 3">${rose}</div>
      <div class="cart-echelle masquable"><span class="cart-k">Échelle</span>${vue.special ? '—' : `${echelle}<span>montants : une rangée chacun, écarts inégaux</span>`}</div>
      <div class="dernier masquable"><span class="cart-k">Moteur</span>commit ${esc(AF.meta.commit)} · ${esc(fmt.date(String(AF.meta.genere_le).slice(0, 10)))}</div>
    </div>`;
  }

  /* ---------- Coupe ---------- */
  let sigCoupe = null;
  function rendreCoupe() {
    const d = dossierAffiche();
    const coupe = $('#coupe');
    coupe.classList.toggle('perimee', AF.perime() && !vue.special);
    $('#coupe-tete').innerHTML = htmlStatut() + htmlTeteVerdict(d);
    const ident = [vue.special, pos(), hist().length, Tc ? Tc.cle : ''].join('|');
    const sig = `${ident}|${vue.demo}|${AF.niveau()}`;
    if (sig === sigCoupe) return;
    const autreDossier = !sigCoupe || !sigCoupe.startsWith(`${ident}|`);
    sigCoupe = sig;
    if (autreDossier) $('#coupe-corps').scrollTop = 0;
    const nav = [['s-lecture', 'Lecture'], ['s-strates', 'Règles'], ['s-profil', 'Profil en long'], ['s-options', 'Options'], ['s-situation', 'Situation'], ['s-limites', 'Limites'], ['s-releves', 'Relevés'], ['s-tableau', 'Tableau']];
    $('#coupe-nav').innerHTML = d ? nav.map(([id, l]) => `<a href="#${id}" data-action="aller" data-valeur="${id}">${l}</a>`).join('') : '';
    const corps = $('#coupe-corps');
    if (vue.demo === 'chargement') { corps.innerHTML = '<div class="squelette" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span><span></span></div><p class="note" style="margin-top:10px">État de démonstration : la coupe s’affichera à la fin de la relecture.</p>'; return; }
    if (!d) { corps.innerHTML = secHorsUnivers(); return; }
    let h = '';
    if (vue.demo === 'erreur' || vue.demo === 'reprise') h += `<div class="lecture-seule" style="margin-top:14px"><span class="tag-demo">État de démonstration</span> ${vue.demo === 'erreur' ? 'Erreur simulée : la coupe ci-dessous est celle de la dernière révision, inchangée.' : 'Reprise : la révision a été relue depuis l’historique, rien n’a été recalculé.'}</div>`;
    h += secLecture(d) + secStrates(d) + secProfil(d) + secOptions(d) + secSituation(d) + secLimites(d) + secReleves(d) + secTableau();
    corps.innerHTML = h;
  }

  function htmlStatut() {
    if (vue.special) return `<div class="statut statut-special"><span class="pc">Cas particulier</span><span>${esc(SPECIAUX[vue.special])} · hors itinéraire</span><span class="statut-actions"><button type="button" class="bouton" data-action="quitter-special" data-cle="quitter-special">Revenir à la carte</button></span></div>`;
    const s = AF.statut(), p = pos(), H = hist(), n = H.length;
    if (s === 'apercu') {
      return `<div class="statut statut-apercu"><span class="pc">Aperçu non sondé</span><span class="statut-motif">${esc(AF.decrire(AF.etat(), AF.brouillon()))}</span><span class="statut-actions"><button type="button" class="bouton bouton-accent" data-action="sonder" data-cle="sonder-coupe">Sonder ici</button><button type="button" class="bouton" data-action="abandonner" data-cle="abandonner">Abandonner</button></span><p class="note" style="flex-basis:100%">La coupe décrit encore la révision ${p + 1} : elle est périmée tant que le point n’est pas sondé.</p></div>`;
    }
    if (s === 'archive') return `<div class="statut statut-archive"><span class="pc">Archive · R${p + 1}</span><span class="statut-motif">Relecture de la révision ${p + 1} sur ${n}. Rien n’est modifié.</span><span class="statut-actions"><button type="button" class="bouton bouton-plein" data-action="restaurer" data-cle="restaurer">Revenir ici</button><button type="button" class="bouton" data-action="courante" data-cle="courante"><span class="txt-ordi">Révision courante</span><span class="txt-mobile">Courante</span> (${n})</button></span></div>`;
    return `<div class="statut statut-courante"><span class="pc">Analyse courante</span><span class="statut-sous">révision ${p + 1} · ${heure(H[p].heure)}<span class="motif"> · ${esc(H[p].motif)}</span></span></div>`;
  }

  function htmlTeteVerdict(d) {
    if (vue.demo === 'chargement') return '<div class="tete-verdict"><span class="pastille motif-vide" aria-hidden="true"></span><div><p class="tete-coord"><span class="tag-demo">État de démonstration</span></p><p class="verdict-long">Levé en cours…</p><p class="verdict-compte">Relecture des étapes enregistrées.</p></div></div>';
    if (!d) {
      const hu = F.speciaux.hors_univers;
      return `<div class="tete-verdict"><span class="pastille motif-indetermine" aria-hidden="true"></span><div><p class="tete-coord">Réponse du moteur · statut ${esc(hu.statut)}</p><p class="verdict-long">Demande refusée avant l’analyse</p><p class="verdict-compte">${esc(hu.message)}</p></div></div>`;
    }
    const v = d.verdict, cond = (d.questions || []).length > 0 && v.etat !== 'indetermine';
    const e = AF.etat();
    const coord = vue.special ? `Demande : ${fmt.cad(d.demande.montant_cad)} · ${d.demande.ticker}` : `Point : ${fmt.cad(e.montant)} · horizon ${d.profil.horizon_ans} ans · ${paramTexte(e)}`;
    const compte = v.evaluees ? `${v.respectees} règle${v.respectees > 1 ? 's' : ''} respectée${v.respectees > 1 ? 's' : ''} sur ${v.evaluees}` : 'Aucune règle évaluable';
    return `<div class="tete-verdict"><span class="pastille motif-${v.etat}" aria-hidden="true"></span><div><p class="tete-coord">${esc(coord)}</p><p class="verdict-long">${esc(v.libelle)}</p><p class="verdict-compte">${compte} ${cond ? '<span class="cond">Conclusion conditionnelle</span>' : ''} ${AF.perime() && !vue.special ? '<span class="perime-tag">Périmé</span>' : ''}</p></div></div>`;
  }

  const titre = (id, t, sous) => `<section class="section" id="${id}" tabindex="-1"><h3 class="section-titre">${t}${sous ? ` <span class="sous">${sous}</span>` : ''}</h3>`;

  function secLecture(d) {
    const t = d.texte || {};
    let h = titre('s-lecture', 'Lecture', 'ce que dit le dossier');
    if (t.reformulation) h += `<p class="texte">${phrase(t.reformulation, [], d)}</p>`;
    (t.miroir || []).forEach((p) => { h += `<p class="texte citation">${phrase(p.texte, p.faits, d)} ${badgeType(p.type)}</p>`; });
    (d.questions || []).forEach((q, i) => { h += htmlQuestion(q, d, i); });
    h += htmlDeplacement(d);
    if (approfondi() && (t.pourquoi || []).length) {
      h += `<p class="petit-titre" style="margin-top:12px">Pourquoi, selon le Rédacteur</p><ul class="puces">${t.pourquoi.map((p) => `<li>${phrase(p.texte, p.faits, d)} ${badgeType(p.type)}</li>`).join('')}</ul>`;
    }
    return `${h}</section>`;
  }

  function htmlQuestion(q, d, i) {
    let actions = '<span class="note">Répondre ici : non réalisé dans ce prototype.</span>';
    if (!vue.special) {
      const p = AF.parametres(), e = AF.etat();
      const oui = p.retrait.find((r) => r != null);
      if (p.retrait.length > 1 && /retrait/i.test(q) && oui != null && e.retrait !== oui) {
        actions = `<button type="button" class="bouton bouton-plein" data-action="param" data-valeur='${JSON.stringify({ retrait: oui })}' data-cle="q-oui-${i}">Oui, retrait ${esc(fmt.retrait(oui))} : placer l’aperçu</button><span class="note">Sans réponse, la conclusion reste conditionnelle.</span>`;
      }
    }
    return `<div class="question"><p class="question-tete pc">${vue.special ? 'Question pour lever l’indétermination' : 'Question décisive'}</p><div class="question-corps"><p class="texte">${phrase(q.replace(/^Question décisive\s*[—-]\s*/, ''), [], d)}</p><div class="question-actions">${actions}</div></div></div>`;
  }

  /* Comparaison de révisions : ce qui a bougé, règle par règle et mesure par mesure (AF.comparer). */
  function htmlDeplacement(d) {
    if (vue.special) return '';
    const H = hist(), p = pos(), n = H.length, s = AF.statut();
    let a, b, titreD;
    if (s === 'archive') { a = H[p].etat; b = H[n - 1].etat; titreD = `Écart avec la révision courante : R${p + 1} → R${n}`; }
    else { const par = H[p].parent; if (par == null || par < 0) return ''; a = H[par].etat; b = H[p].etat; titreD = `Relevé du déplacement : R${par + 1} → R${p + 1}`; }
    if (a.cas !== b.cas) return '';
    const c = AF.comparer(a, b);
    if (c.motif === 'Sans changement') return `<div class="deplac"><p class="deplac-tete"><strong>${esc(titreD)}</strong> · même point, aucun écart.</p></div>`;
    const lignes = [`<tr><th scope="row">Verdict</th><td class="${c.verdict.change ? 'bouge' : ''}">${esc(court(c.verdict.avant))}<span class="fleche">→</span>${esc(court(c.verdict.apres))}</td></tr>`];
    const regles = c.regles.filter((r) => r.change || approfondi());
    regles.forEach((r) => lignes.push(`<tr><th scope="row">${esc(r.libelle)}</th><td class="${r.change ? 'bouge' : ''}">${esc(nivMin(r.avant))}<span class="fleche">→</span>${esc(nivMin(r.apres))}</td></tr>`));
    c.mesures.forEach((m) => {
      if (!approfondi() && !['pire_chute', 'volatilite'].includes(m.cle)) return;
      const f = (v) => (m.unite === '$' ? fmt.cad(v) : fmt.pct(v, 1));
      lignes.push(`<tr><th scope="row">${esc(m.titre)} <span class="def">portefeuille avec la demande</span></th><td>${esc(f(m.avant))}<span class="fleche">→</span>${esc(f(m.apres))}</td></tr>`);
    });
    return `<div class="deplac"><p class="deplac-tete"><strong>${esc(titreD)}</strong> · ${esc(c.motif)}</p><table><tbody>${lignes.join('')}</tbody></table></div>`;
  }

  function changementsParent() {
    if (vue.special) return new Map();
    const H = hist(), p = pos(), par = H[p].parent;
    if (par == null || par < 0 || H[par].etat.cas !== H[p].etat.cas) return new Map();
    return new Map(AF.comparer(H[par].etat, H[p].etat).regles.filter((r) => r.change).map((r) => [r.code, r]));
  }

  function secStrates(d) {
    const v = d.verdict, regles = d.regles || [], bouge = changementsParent();
    const strate = (r) => {
      const ch = bouge.get(r.code);
      const puces = approfondi() ? `<p class="strate-faits">${(r.faits || []).map((id) => puceFait(id, d)).join('')}${(r.references || []).map(puceRef).join('')}</p>` : '';
      return `<li class="strate niv-${r.niveau}"><span class="strate-carotte motif-${MOTIF_NIV[r.niveau] || 'vide'}" aria-hidden="true"></span><div class="strate-corps"><p class="strate-tete"><span class="pc strate-nom">${esc(r.libelle)}</span><span class="badge ${r.niveau === 'rouge' ? 'fort' : ''}">${esc(AF.NIVEAUX_REGLE[r.niveau] || r.niveau)}</span>${badgeType(r.type)}</p><p class="strate-txt">${phrase(r.explication, r.faits, d)}</p>${ch ? `<p class="strate-bouge">A bougé depuis la révision parente : ${esc(nivMin(ch.avant))} → ${esc(nivMin(ch.apres))}</p>` : ''}${puces}</div></li>`;
    };
    let h = titre('s-strates', 'Coupe des règles', 'une strate par règle du Gardien');
    h += `<p class="note" style="margin-bottom:8px">Le Gardien est du code : il applique les règles dans un ordre fixe et décide seul du verdict. ${v.evaluees ? `${v.respectees} sur ${v.evaluees} respectées.` : 'Aucune règle n’a pu être évaluée.'}</p>`;
    if (approfondi()) h += `<ol class="strates">${regles.map(strate).join('')}</ol>`;
    else {
      const ok = regles.filter((r) => r.niveau === 'ok'), autres = regles.filter((r) => r.niveau !== 'ok');
      h += `<ol class="strates">${autres.map(strate).join('')}${ok.length ? `<li class="strate niv-ok"><span class="strate-carotte motif-coherent" aria-hidden="true"></span><div class="strate-corps"><details class="strate-resume"><summary><span class="pc strate-nom">${pluriel(ok.length, 'règle')} respectée${ok.length > 1 ? 's' : ''}</span></summary><ul class="strate-mini">${ok.map((r) => `<li><strong>${esc(r.libelle)}</strong> · ${phrase(r.explication, r.faits, d)}</li>`).join('')}</ul></details></div></li>` : ''}</ol>`;
    }
    return `${h}</section>`;
  }

  /* Profil en long : courbes réelles des baisses du portefeuille, avant et après, sur la fenêtre observée seulement. */
  function svgProfil(d) {
    const s = d.series_portefeuille, k = d.comparaison;
    const W = 400, H = 214, m = { g: 42, d: 66, h: 16, b: 40 };
    const t = (iso) => Date.parse(`${iso}T00:00:00Z`);
    const t0 = t(s.avant[0][0]), t1 = t(s.avant[s.avant.length - 1][0]);
    const vmin = Math.min(k.avant.pire_chute_pct, k.apres.pire_chute_pct, ...s.avant.map((q) => q[2]), ...s.apres.map((q) => q[2]));
    const pas = vmin < -30 ? 10 : 5;
    const bas = Math.floor(vmin / pas) * pas - (vmin % pas === 0 ? pas : 0);
    const X = (iso) => m.g + ((t(iso) - t0) / (t1 - t0)) * (W - m.g - m.d);
    const Y = (v) => m.h + (v / bas) * (H - m.h - m.b);
    const chemin = (serie) => serie.map((q, i) => `${i ? 'L' : 'M'}${px(X(q[0]))} ${px(Y(q[2]))}`).join('');
    const o = [`<defs><pattern id="pl-hachure" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="6" height="6" fill="#eef1ed"/><line x1="0" y1="0" x2="0" y2="6" stroke="#9fada7" stroke-width="1"/></pattern><marker id="pl-fl" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 2L5 8L10 2" fill="none" stroke="#17241f" stroke-width="1.6"/></marker></defs>`];
    if (approfondi()) (s.avant_fenetres || []).forEach((f, i) => {
      const xa = X(f.debut), xb = X(f.fin), l = Math.max(2, xb - xa);
      o.push(`<rect class="pl-fenetre" x="${px(xa)}" y="${m.h}" width="${px(l)}" height="${H - m.h - m.b}"><title>${esc(f.nom)} : ${esc(f.debut)} → ${esc(f.fin)}</title></rect><text class="pl-axe" x="${px(xa + l / 2)}" y="${m.h + 10}" text-anchor="middle" font-size="10" font-weight="700">${i + 1}</text>`);
    });
    for (let v = 0; v >= bas; v -= pas) o.push(`<line class="pl-grille" x1="${m.g}" y1="${px(Y(v))}" x2="${W - m.d}" y2="${px(Y(v))}"/><text class="pl-axe" x="${m.g - 5}" y="${px(Y(v) + 4)}" text-anchor="end">${esc(fmt.pct(v, 0))}</text>`);
    const a0 = new Date(t0).getUTCFullYear(), a1 = new Date(t1).getUTCFullYear();
    for (let a = a0 + 1; a <= a1; a++) { const x = X(`${a}-01-01`); o.push(`<line class="pl-grille" x1="${px(x)}" y1="${m.h}" x2="${px(x)}" y2="${H - m.b}"/><text class="pl-axe" x="${px(x)}" y="${H - m.b + 14}" text-anchor="middle">${a}</text>`); }
    o.push(`<path class="pl-terrain" d="M${px(X(s.apres[0][0]))} ${px(Y(0))}${chemin(s.apres).replace(/^M/, 'L')}L${px(X(s.apres[s.apres.length - 1][0]))} ${px(Y(0))}Z"/>`);
    o.push(`<path class="pl-avant" d="${chemin(s.avant)}"/><path class="pl-apres" d="${chemin(s.apres)}"/>`);
    o.push(`<line x1="${m.g}" y1="${px(Y(0))}" x2="${W - m.d}" y2="${px(Y(0))}" stroke="#17241f" stroke-width="1.2"/><line x1="${m.g}" y1="${m.h}" x2="${m.g}" y2="${H - m.b}" stroke="#17241f" stroke-width="1.2"/>`);
    /* Pires baisses cotées (faits) et écart apparié en cote verticale */
    const yA = Y(k.avant.pire_chute_pct), yP = Y(k.apres.pire_chute_pct);
    o.push(`<line class="pl-ref" x1="${m.g}" y1="${px(yA)}" x2="${W - m.d + 4}" y2="${px(yA)}"/><line class="pl-ref" x1="${m.g}" y1="${px(yP)}" x2="${W - m.d + 4}" y2="${px(yP)}"/>`);
    const xc = W - m.d + 10;
    if (Math.abs(yP - yA) > 7) o.push(`<line class="pl-cote" x1="${xc}" y1="${px(yA)}" x2="${xc}" y2="${px(yP)}" marker-start="url(#pl-fl)" marker-end="url(#pl-fl)"/>`);
    const F2 = k.faits || {};
    const lien = (id, x, y, txt, anchor = 'start', cls = 'pl-fort') => (id ? `<a class="lien-fait" href="#" data-action="fait" data-valeur="${id}" aria-label="${esc(txt)} : fiche ${id}"><text class="${cls}" x="${px(x)}" y="${px(y)}" text-anchor="${anchor}" paint-order="stroke" stroke="#fbfbf8" stroke-width="3">${esc(txt)}</text></a>` : `<text class="${cls}" x="${px(x)}" y="${px(y)}">${esc(txt)}</text>`);
    let ya = yA - 4, yp = yP + 13;
    if (yp - ya < 15) yp = ya + 15;
    o.push(lien(F2.avant_pire_chute, W - m.d - 2, ya, `sans : ${fmt.pct(k.avant.pire_chute_pct, 1)}`, 'end'));
    o.push(lien(F2.apres_pire_chute, W - m.d - 2, yp, `avec : ${fmt.pct(k.apres.pire_chute_pct, 1)}`, 'end'));
    const ym = (yA + yP) / 2;
    o.push(`<text class="pl-axe" x="${xc + 6}" y="${px(ym - 4)}">écart</text>`);
    o.push(lien(F2.ecart_pire_chute, xc + 6, ym + 10, fmt.pts(k.ecarts.pire_chute_pts, 1)));
    o.push(`<text class="pl-axe" x="${m.g}" y="${H - 6}">observé ${esc(k.fenetre.debut)} → ${esc(k.fenetre.fin)} · rien n’est prolongé au-delà</text>`);
    return `<svg class="profil-long" viewBox="0 0 ${W} ${H}" role="img" aria-label="Profil en long : baisses du portefeuille sans et avec ta demande, du ${esc(k.fenetre.debut)} au ${esc(k.fenetre.fin)}. Pire baisse ${esc(fmt.pct(k.avant.pire_chute_pct, 1))} sans, ${esc(fmt.pct(k.apres.pire_chute_pct, 1))} avec ; écart ${esc(fmt.pts(k.ecarts.pire_chute_pts, 1))}.">${o.join('')}</svg>`;
  }

  function secProfil(d) {
    const k = d.comparaison;
    let h = titre('s-profil', 'Profil en long', 'ton portefeuille, sans et avec la demande');
    if (!k || !k.disponible || !d.series_portefeuille) return `${h}<p class="note">Comparaison indisponible : ${esc((k && k.raison) || 'non calculée pour ce dossier')}.</p></section>`;
    const s = d.series_portefeuille, F2 = k.faits || {};
    h += svgProfil(d);
    h += `<p class="legende-pl"><span><span class="trait-avant" aria-hidden="true"></span>sans la demande (avant)</span><span><span class="trait-apres" aria-hidden="true"></span>avec la demande (après)</span></p>`;
    h += `<p class="note">Baisses depuis le plus haut précédent, passé observé seulement. Courbes tracées sur ${s.avant.length} points ; les pires baisses cotées viennent des ${esc(k.fenetre.observations)} observations du moteur${F2.fenetre_portefeuille ? ` (fenêtre : <button type="button" class="num" data-action="fait" data-valeur="${F2.fenetre_portefeuille}">${F2.fenetre_portefeuille}</button>)` : ''}.</p>`;
    const ids = { pire_chute: ['avant_pire_chute', 'apres_pire_chute', 'ecart_pire_chute'], volatilite: ['avant_volatilite', 'apres_volatilite', 'ecart_volatilite'], rendement: ['avant_rendement', 'apres_rendement', null], valeur_finale: ['avant_valeur_finale', 'apres_valeur_finale', null] };
    const cell = (cle, txt) => (cle && F2[cle] ? `<button type="button" class="num" data-action="fait" data-valeur="${F2[cle]}" aria-label="${esc(txt)} : fiche ${F2[cle]}">${esc(txt)}</button>` : esc(txt));
    const lignes = AF.mesures(d).map((m) => {
      const [ia, ip, ie] = ids[m.cle] || [];
      const fv = (v) => (m.unite === '$' ? fmt.cad(v) : fmt.pct(v, 1));
      const fe = (v) => (m.unite === '$' ? `${v > 0 ? '+' : ''}${fmt.cad(v)}` : fmt.pts(v, 1));
      return `<tr><th scope="row">${esc(m.titre)}${approfondi() ? '' : `<span class="def">${esc(m.def)}</span>`}</th><td>${cell(ia, fv(m.avant))}</td><td>${cell(ip, fv(m.apres))}</td><td class="ecart">${cell(ie, fe(m.ecart))}${m.sens ? `<span class="def">${esc(SENS[m.sens] || m.sens)}</span>` : ''}</td></tr>`;
    }).join('');
    h += `<table class="mesures"><caption>Mêmes mesures, même fenêtre. ${esc(AF.terme('ecart').titre)}${approfondi() ? '' : ' : après moins avant'}.</caption><thead><tr><th scope="col">Mesure</th><th scope="col">Sans</th><th scope="col">Avec</th><th scope="col">Écart</th></tr></thead><tbody>${lignes}</tbody></table>`;
    if (approfondi()) {
      const fa = s.avant_fenetres || [], fp = s.apres_fenetres || [];
      if (fa.length) h += `<p class="petit-titre" style="margin-top:12px">Fenêtres historiques choisies par le moteur (bandes numérotées)</p><div class="tableau-cont"><table class="releves"><thead><tr><th>Fenêtre</th><th>Pire baisse sans</th><th>avec</th><th>Rendement sans</th><th>avec</th></tr></thead><tbody>${fa.map((f, i) => { const g = fp[i] || {}; return `<tr><td>${i + 1} · ${esc(f.nom)}<span class="def">${esc(f.debut)} → ${esc(f.fin)}</span></td><td>${esc(fmt.pct(f.pire_chute_pct, 1))}</td><td>${esc(fmt.pct(g.pire_chute_pct, 1))}</td><td>${esc(fmt.pct(f.rendement_pct, 1))}</td><td>${esc(fmt.pct(g.rendement_pct, 1))}</td></tr>`; }).join('')}</tbody></table></div>`;
      const idf = d.demande.ids_faits || {};
      h += `<p class="note" style="margin-top:8px">Poids : ${puceFait(F2.poids_avant, d)} ${puceFait(F2.poids_apres, d)} · ${esc(d.demande.ticker)} seul : ${puceFait(idf.chute, d)} ${puceFait(idf.volatilite, d)}</p>`;
    }
    return `${h}</section>`;
  }

  function secOptions(d) {
    const t = d.texte || {};
    let h = titre('s-options', 'Options et ce qui changerait l’avis');
    (t.ce_qui_changerait || []).forEach((p) => { h += `<p class="texte">${phrase(p.texte, p.faits, d)} ${badgeType(p.type)}</p>`; });
    if (!(t.ce_qui_changerait || []).length) h += '<p class="note">Le dossier ne nomme aucun changement de montant qui ferait basculer le verdict.</p>';
    const stations = vue.special ? [] : AF.parametres().montant;
    h += `<ul class="options" style="margin-top:10px">${(d.options || []).map((o, i) => {
      const meme = o.ticker === d.demande.ticker, estDemande = o.nom === 'Ta demande';
      let act = '';
      if (!estDemande && !vue.special) {
        if (meme && stations.includes(o.montant_cad)) act = `<button type="button" class="bouton" data-action="montant" data-valeur="${o.montant_cad}" data-cle="opt-${i}">Placer l’aperçu à ${esc(fmt.cad(o.montant_cad))}</button>`;
        else if (meme) act = `<span class="note">Aucun dossier précalculé à ${esc(fmt.cad(o.montant_cad))} dans ce prototype : la carte le montre comme repère ◆, sans coupe.</span>`;
        else act = `<span class="note">Autre actif : hors de cette carte, qui ne couvre que ${esc(d.demande.ticker)}.</span>`;
      }
      const txt = o.constat || o.note;
      return `<li class="option"><span class="opt-motif motif-${o.etat}" aria-hidden="true"></span><div class="opt-corps"><p class="opt-nom">${esc(o.nom)} <span class="badge">${esc(court(o.etat))}</span></p><p class="opt-meta">${esc(o.ticker)} · ${esc(o.libelle_actif || nomActif(o.ticker))} · ${esc(fmt.cad(o.montant_cad))} · horizon ${esc(o.horizon_ans)} ans</p>${txt ? `<p class="opt-txt">${phrase(txt, o.faits || [], d)}</p>` : ''}${act ? `<div class="opt-actions">${act}</div>` : ''}</div></li>`;
    }).join('')}</ul><p class="note" style="margin-top:8px">L’ordre est celui du dossier ; ce n’est ni un classement ni une recommandation.</p>`;
    return `${h}</section>`;
  }

  function secSituation(d) {
    const p = d.profil;
    let h = titre('s-situation', 'Ta situation', 'ce que le produit a compris');
    h += `<p class="texte citation">« ${esc(d.demande.texte)} »</p><p class="note" style="margin-top:6px">Compris comme : ${esc(d.demande.ticker)} (${esc(nomActif(d.demande.ticker))}) pour ${esc(fmt.cad(d.demande.montant_cad))}. Lecture de la phrase : ${esc((p.extraits && p.extraits.source) || '—')}.</p>`;
    h += `<ul class="lignes" style="margin-top:10px">${AF.profilLignes(d).map((l) => `<li class="ligne"><span class="ligne-lib">${esc(l.libelle)}</span><span class="ligne-nat"><span class="nat nat-${l.nature}">${esc(NATURES[l.nature] || l.nature)}</span></span><span class="ligne-val">${l.valeur == null ? 'Non fourni' : esc(l.valeur)}</span>${l.note ? `<span class="ligne-note">${esc(l.note)}</span>` : ''}</li>`).join('')}</ul>`;
    if (!vue.special) {
      const pr = AF.parametres();
      const modif = ['le montant (carte ou liste)'];
      if (pr.retrait.length > 1) modif.push('le retrait prévu (légende)');
      if (pr.exclusion.length > 1) modif.push(`l’exclusion du secteur ${secteurExclu(AF.etat().cas)} (légende)`);
      h += `<p class="lecture-seule"><strong>Lecture seule.</strong> Seuls se corrigent ici : ${esc(modif.join(', '))}. Les autres lignes ne sont pas modifiables : non réalisé dans ce prototype. Une donnée inconnue est dite, jamais remplacée.</p>`;
    } else h += '<p class="lecture-seule"><strong>Lecture seule.</strong> Cas particulier : la correction n’est pas réalisée dans ce prototype.</p>';
    if ((p.citations || []).length) h += `<p class="petit-titre" style="margin-top:12px">Tu as dit</p><ul class="puces">${p.citations.map((c) => `<li>« ${esc(c)} »</li>`).join('')}</ul>`;
    if ((p.tensions || []).length) h += `<p class="petit-titre" style="margin-top:10px">Tensions relevées</p><ul class="puces">${p.tensions.map((c) => `<li>${phrase(c, [], d)}</li>`).join('')}</ul>`;
    return `${h}</section>`;
  }

  function secLimites(d) {
    const L = (d.texte && d.texte.limites) || [];
    const li = (p) => `<li>${phrase(p.texte, p.faits, d)} ${badgeType(p.type)}${(p.references || []).map(puceRef).join('')}</li>`;
    let h = titre('s-limites', 'Limites', `${L.length} au total`);
    if (approfondi() || L.length <= 3) h += `<ul class="puces">${L.map(li).join('')}</ul>`;
    else h += `<ul class="puces">${L.slice(0, 3).map(li).join('')}</ul><details class="plie"><summary>Les ${L.length - 3} autres limites</summary><ul class="puces">${L.slice(3).map(li).join('')}</ul></details>`;
    if (d.texte && d.texte.avertissement) h += `<p class="note" style="margin-top:8px">${esc(d.texte.avertissement)}</p>`;
    return `${h}</section>`;
  }

  function secReleves(d) {
    const faits = d.faits || [];
    const table = `<div class="tableau-cont"><table class="releves"><thead><tr><th>Fait</th><th>Libellé</th><th>Valeur</th><th>Type</th></tr></thead><tbody>${faits.map((f) => `<tr><td><button type="button" class="num" data-action="fait" data-valeur="${f.id}">${f.id}</button></td><td>${esc(f.libelle)}</td><td>${esc(valFait(f))}</td><td>${esc(AF.TYPES[f.type] || f.type)}</td></tr>`).join('')}</tbody></table></div>`;
    let h = titre('s-releves', 'Relevés', `${faits.length} faits du dossier`);
    if (!faits.length) h += '<p class="note">Aucun fait : le dossier s’arrête avant les calculs.</p>';
    else if (approfondi()) h += table;
    else h += `<details class="plie"><summary>Afficher le tableau des ${faits.length} faits</summary>${table}</details>`;
    if (approfondi()) {
      const q = d.qualite_donnees || [], ob = d.objections || [];
      if (q.length) h += `<p class="petit-titre" style="margin-top:12px">Contrôle des données (code)</p><ul class="puces">${q.map((c) => `<li><strong>${esc(c.libelle)}</strong> · ${esc(c.statut === 'ok' ? 'réussi' : c.statut)} · ${esc(c.detail)}</li>`).join('')}</ul>`;
      if (ob.length) h += `<p class="petit-titre" style="margin-top:12px">Objections du Sceptique, vérifiées par le code</p><ul class="puces">${ob.map((o) => `<li>${esc(o.texte)} <span class="def">${esc(o.recalcul)} → ${phrase(o.reponse, [o.cible], d)} (${esc(o.issue)})</span></li>`).join('')}</ul>`;
    }
    return `${h}</section>`;
  }

  function secTableau() {
    if (vue.special || !Tc) return '';
    const T = Tc, ab = { coherent: 'C', ajustement: 'A', incoherent: 'I', indetermine: '?' };
    const tete = `<tr><th scope="col">Montant</th>${T.horizons.map((h) => `<th scope="col" class="${h === T.hDecl ? 'declare' : ''}">${h}</th>`).join('')}</tr>`;
    const lignes = [...T.stations].reverse().map((s) => `<tr><th scope="row">${esc(fmt.cad(s.montant))}</th>${T.horizons.map((h) => {
      const e = h === T.hDecl ? s.etat : T.grille && s.dansGrille ? T.cases.get(`${s.montant}|${h}`) : null;
      return e ? `<td class="c-${e}${h === T.hDecl ? ' declare' : ''}" title="${esc(court(e))}">${ab[e]}</td>` : `<td${h === T.hDecl ? ' class="declare"' : ''}>—</td>`;
    }).join('')}</tr>`).join('');
    let h = titre('s-tableau', 'La carte en tableau', 'équivalent accessible');
    h += `<details class="plie"${approfondi() ? ' open' : ''}><summary>Afficher la grille montant × horizon</summary><p class="note">C = Cohérent, A = Ajustement, I = Incohérent, ? = Indéterminé, — = non levé. Colonne encadrée : ton horizon (${T.hDecl} ans), d’après les dossiers réels.${T.grille ? '' : ' Avec ce paramètre, la grille de départ ne s’applique pas.'}</p><div class="tableau-cont"><table class="grille-tab"><thead>${tete}</thead><tbody>${lignes}</tbody></table></div></details>`;
    return `${h}</section>`;
  }

  function secHorsUnivers() {
    const hu = F.speciaux.hors_univers;
    return `${titre('s-lecture', 'Hors de la carte')}<p class="texte">${esc(hu.message)}</p><p class="note" style="margin-top:6px">Réponse réelle du moteur (statut ${esc(hu.statut)}). Aucun dossier n’est produit : ni règle, ni relevé, ni carte. Ce refus n’est pas un verdict sur la personne.</p><p style="margin-top:12px"><button type="button" class="bouton" data-action="quitter-special" data-cle="quitter-special-corps">Revenir à la carte</button></p></section>`;
  }

  /* ---------- Feuille de route des rôles ---------- */
  let sigRoute = null;
  function rendreRoute() {
    const d = dossierAffiche();
    const sig = [vue.special, pos(), AF.niveau(), Tc ? Tc.cle : ''].join('|');
    if (sig === sigRoute) return;
    sigRoute = sig;
    if (vue.arretRelecture) { vue.arretRelecture(); vue.arretRelecture = null; }
    const el = $('#route');
    if (!d) { el.innerHTML = `<p class="route-note">Aucune étape : la demande a été refusée avant l’analyse (${esc(F.speciaux.hors_univers.message)}).</p>`; return; }
    const cas = vue.special ? 'robert' : AF.etat().cas;
    const appels = d.appels_modele || [];
    const etapes = (d.trace || []).map((t, i) => {
      const code = CODE.has(t.agent);
      const genre = code ? 'code' : appels.some((a) => a.agent === t.agent) ? 'modèle' : 'rôle de modèle · ici sans appel (hors ligne)';
      return `<li class="etape ${code ? 'code' : 'modele'}" id="etape-${i}"><span class="etape-signe" aria-hidden="true"></span><div><p class="etape-nom">${esc(t.agent)} <span class="etape-genre">${esc(genre)}</span></p><p class="etape-act">${esc(t.action)}</p></div><span class="etape-duree">${esc(fmt.ms(t.duree_ms))}</span>${approfondi() ? `<p class="etape-det">${esc(AF.propre(t.detail))}${(t.faits || []).length ? ` · ${pluriel(t.faits.length, 'fait')} cité${t.faits.length > 1 ? 's' : ''}` : ''}</p>` : ''}</li>`;
    }).join('');
    let h = `<p class="route-note">Étapes enregistrées pour ce dossier (${esc(AF.meta.mode)}). Durées mesurées par le moteur.</p>`;
    h += '<p class="route-note">■ code : Contrôle des données, Analyste, Gardien · ● rôle de modèle : Profileur, Sceptique, Rédacteur.</p>';
    h += `<ol class="route-etapes">${etapes}</ol>`;
    h += '<div class="route-actions"><button type="button" class="bouton" data-action="relire" data-cle="relire">Relire les étapes enregistrées</button></div><p class="route-statut" id="route-statut" role="status">Relecture, pas un calcul en direct.</p>';
    h += appels.length ? `<p class="route-h">Appels de modèle de ce dossier</p>${tableAppels(appels)}` : '<p class="note">Aucun appel de modèle pour ce dossier : mode hors ligne.</p>';
    const ex = AF.execution(cas);
    if (ex) {
      const dep = departDe(cas), e = vue.special ? null : AF.etat();
      const autre = !e || e.montant !== dep.montant || e.retrait !== dep.retrait || e.exclusion !== dep.exclusion;
      h += `<p class="route-h">Exécution Bedrock enregistrée</p><p class="note">Demande de départ de ${esc(AF.nomCas(cas))} (${esc(fmt.cad(dep.montant))}, ${esc(paramTexte(dep))}). Source : <code>${esc(ex.source)}</code>.${autre ? ' Ce relevé ne concerne pas le point affiché.' : ''}</p>${tableAppels(ex.appels_modele || [])}<p class="note" style="margin-top:6px">Durées de cette exécution : ${(ex.trace || []).map((t) => `${esc(t.agent)} ${esc(fmt.ms(t.duree_ms))}`).join(' · ')}.</p>`;
    } else h += '<p class="note">Aucun appel de modèle enregistré pour cette situation : mode hors ligne.</p>';
    el.innerHTML = h;
  }
  function tableAppels(appels) {
    const ap = approfondi();
    return `<div class="tableau-cont"><table class="appels"><thead><tr><th>Rôle</th><th>Modèle</th><th>Jetons entrée / sortie</th><th>Latence</th>${ap ? '<th>Garde-fou</th><th>Requête</th>' : ''}</tr></thead><tbody>${appels.map((a) => `<tr><td>${esc(a.agent)}</td><td><code>${esc(a.modele)}</code></td><td>${esc(fmt.nombre(a.jetons_entree))} / ${esc(fmt.nombre(a.jetons_sortie))}</td><td>${esc(fmt.ms(a.latence_ms))}</td>${ap ? `<td>${esc(a.garde_fou === 'configure' ? 'configuré' : a.garde_fou)}</td><td><code>${esc(a.request_id)}</code></td>` : ''}</tr>`).join('')}</tbody></table></div>`;
  }
  function relireRoute() {
    const d = dossierAffiche();
    if (!d || !(d.trace || []).length) return;
    if (vue.arretRelecture) vue.arretRelecture();
    $$('#route .etape').forEach((e) => e.classList.remove('en_cours', 'fait'));
    vue.arretRelecture = AF.relireTrace(d, (i, phase) => {
      const st = $('#route-statut');
      if (phase === 'fin') { if (st) st.textContent = `Relecture terminée : ${pluriel(d.trace.length, 'étape')} enregistrée${d.trace.length > 1 ? 's' : ''}.`; vue.arretRelecture = null; return; }
      const el = $(`#etape-${i}`);
      if (el) { el.classList.remove('en_cours'); el.classList.add(phase); }
      const t = d.trace[i];
      if (st) st.textContent = phase === 'en_cours' ? `Relecture : ${t.agent} (${i + 1} sur ${d.trace.length})` : `${t.agent} : étape enregistrée, ${fmt.ms(t.duree_ms)}.`;
    });
  }

  /* ---------- Voile : états de démonstration et cas particuliers ---------- */
  function rendreVoile() {
    const v = $('#voile');
    if (vue.demo === 'chargement') {
      const d = AF.dossier();
      v.hidden = false;
      v.innerHTML = `<div class="voile-boite" role="status"><span class="tag-demo">État de démonstration</span><h3>Levé en cours</h3><p class="note">Relecture des étapes enregistrées de ce dossier ; aucun calcul n’est relancé.</p><ol class="route-etapes" style="margin-top:10px">${(d.trace || []).map((t, i) => `<li class="etape ${CODE.has(t.agent) ? 'code' : 'modele'} ${vue.demoEtapes[i] || ''}" id="voile-etape-${i}"><span class="etape-signe" aria-hidden="true"></span><div><p class="etape-nom">${esc(t.agent)}</p><p class="etape-act">${esc(t.action)}</p></div><span class="etape-duree">${esc(fmt.ms(t.duree_ms))}</span></li>`).join('')}</ol><button type="button" class="bouton" data-action="demo" data-valeur="normal" data-cle="demo-fin">Afficher le résultat</button></div>`;
      return;
    }
    if (vue.demo === 'erreur') {
      v.hidden = false;
      v.innerHTML = `<div class="voile-boite" role="alert"><span class="tag-demo">État de démonstration</span><h3>Le levé n’a pas abouti</h3><p>Erreur simulée : rien n’a été recalculé et rien n’est perdu. La carte et la coupe restent celles de la révision ${pos() + 1}.</p><p class="note" style="margin-top:6px">Dans le produit, le message nommerait le rôle en échec et la donnée manquante.</p><button type="button" class="bouton bouton-plein" data-action="demo" data-valeur="reprise" data-cle="demo-reprendre">Reprendre</button></div>`;
      return;
    }
    if (vue.demo === 'reprise') {
      v.hidden = false;
      v.innerHTML = `<div class="voile-boite" role="status"><span class="tag-demo">État de démonstration</span><h3>Reprise</h3><p>La révision ${pos() + 1} a été relue depuis l’historique enregistré dans ce navigateur. Aucune valeur n’a été remplacée.</p><button type="button" class="bouton bouton-plein" data-action="demo" data-valeur="normal" data-cle="demo-retour">Revenir à la carte</button></div>`;
      return;
    }
    if (vue.special) {
      const d = F.speciaux[vue.special].dossier;
      let corps;
      if (vue.special === 'hors_univers') corps = `<h3>Hors de la carte : actif inconnu</h3><p>${esc(F.speciaux.hors_univers.message)}</p><p class="note" style="margin-top:6px">Réponse réelle du moteur, statut ${esc(F.speciaux.hors_univers.statut)}. Aucun dossier n’est produit.</p>`;
      else if (vue.special === 'impossible') corps = `<h3>Hors de la carte : le montant dépasse l’épargne</h3><p>Demande : ${esc(fmt.cad(d.demande.montant_cad))} pour une épargne déclarée de ${esc(fmt.cad(d.profil.epargne_totale_cad))}.</p><p class="note" style="margin-top:6px">Verdict réel du moteur : « ${esc(d.verdict.libelle)} ». ${esc((d.questions || [])[0] || '')}</p>`;
      else corps = `<h3>Terrain non levé : il manque l’épargne totale</h3><p>Verdict réel du moteur : « ${esc(d.verdict.libelle)} ».</p><p class="note" style="margin-top:6px">Question pour lever l’indétermination : ${esc((d.questions || [])[0] || '')} Y répondre : non réalisé dans ce prototype.</p>`;
      v.hidden = false;
      v.innerHTML = `<div class="voile-boite"><span class="pc">Cas particulier</span>${corps}<button type="button" class="bouton" data-action="quitter-special" data-cle="quitter-special-voile">Revenir à la carte</button></div>`;
      return;
    }
    v.hidden = true; v.innerHTML = '';
  }
  function majVoileEtapes() {
    Object.entries(vue.demoEtapes).forEach(([i, ph]) => { const el = $(`#voile-etape-${i}`); if (el) { el.classList.remove('en_cours'); el.classList.add(ph); } });
  }
  function definirDemo(v) {
    if (vue.arretDemo) { vue.arretDemo(); vue.arretDemo = null; }
    vue.demo = v; vue.demoEtapes = {};
    if (v === 'chargement') {
      vue.arretDemo = AF.relireTrace(AF.dossier(), (i, phase) => {
        if (phase === 'fin') { vue.arretDemo = null; vue.demo = 'normal'; annoncer('Démonstration : relecture terminée, résultat affiché.'); rendre(); return; }
        vue.demoEtapes[i] = phase; majVoileEtapes();
      });
    }
    rendre();
    annoncer(v === 'normal' ? 'État normal.' : `État de démonstration : ${v}.`);
  }

  /* ---------- Fiche de relevé (preuve) ---------- */
  let ouvreur = null;
  function valeurExacte(v, unite) {
    if (v == null) return '—';
    if (typeof v === 'number') return `<span class="v">${esc(String(v).replace('.', ','))}${unite ? ` ${esc(unite)}` : ''}</span>`;
    if (Array.isArray(v)) return `<ol class="puces">${v.map((x) => `<li>${esc(x)}</li>`).join('')}</ol>`;
    if (typeof v === 'object') return `<table class="petite-table"><tbody>${Object.entries(v).map(([k, x]) => `<tr><td>${esc(k)}</td><td><strong>${esc(typeof x === 'number' ? String(x).replace('.', ',') : x)}</strong></td></tr>`).join('')}</tbody></table>`;
    return `<span>${esc(v)}</span>`;
  }
  function htmlRef(r, ouvert) {
    return `<li><details${ouvert ? ' open' : ''}><summary><strong>${esc(courtRef(r))}</strong> · ${esc(r.titre)}</summary><div class="ref-corps"><p><span class="cart-k">Type</span>${esc(r.type)}</p><p><span class="cart-k">Auteurs</span>${esc(r.auteurs)} (${esc(r.annee)})</p><p><span class="cart-k">Publication</span>${esc(r.publication)}</p>${r.examen ? `<p><span class="cart-k">Examen</span>${esc(r.examen)}</p>` : ''}${r.apport ? `<p><span class="cart-k">Apport</span>${esc(r.apport)}</p>` : ''}${r.lien ? `<p><span class="cart-k">Lien</span><a href="${esc(r.lien)}" target="_blank" rel="noopener noreferrer">${esc(r.lien)}</a></p>` : '<p class="note">Pas de lien public : source interne ou donnée du projet.</p>'}</div></details></li>`;
  }
  function ouvrirFiche(sur, titreF, corps) {
    const dlg = $('#fiche');
    ouvreur = document.activeElement;
    $('#fiche-sur').textContent = sur;
    $('#fiche-titre').textContent = titreF;
    $('#fiche-corps').innerHTML = corps;
    if (!dlg.open) dlg.showModal();
    $('#fiche-corps').scrollTop = 0;
  }
  function ouvrirFait(id) {
    const d = dossierAffiche();
    const f = d && (d.faits || []).find((x) => x.id === id);
    if (!f) return;
    const regles = (d.regles || []).filter((r) => (r.faits || []).includes(id)).map((r) => r.libelle);
    const obj = (d.objections || []).filter((o) => o.cible === id);
    const refs = (f.references || []).map(AF.reference).filter(Boolean);
    const affiche = valFait(f);
    let h = `<div class="fiche-valeur">${valeurExacte(f.valeur, f.unite)}${typeof f.valeur === 'number' ? `<span class="v-aff">valeur exacte · affichée « ${esc(affiche)} »</span>` : ''}</div>`;
    h += `<dl><dt>Type</dt><dd><span class="badge t-${esc(f.type)}">${esc(AF.TYPES[f.type] || f.type)}</span></dd><dt>Obtenu</dt><dd>${f.lu_ou_calcule === 'lu' ? 'Lu tel quel dans la source' : 'Calculé par le code'}</dd><dt>Source</dt><dd>${esc(f.source)}</dd><dt>Méthode</dt><dd>${esc(f.methode)}</dd>${regles.length ? `<dt>Utilisé par</dt><dd>${esc(regles.join(', '))}</dd>` : ''}${obj.length ? `<dt>Sceptique</dt><dd>${obj.map((o) => `${esc(o.texte)} → ${esc(o.issue)}`).join('<br>')}</dd>` : ''}</dl>`;
    h += `<h3>Références (${refs.length})</h3>${refs.length ? `<ul class="refs">${refs.map((r) => htmlRef(r, refs.length === 1)).join('')}</ul>` : '<p class="note">Aucune référence attachée à ce fait.</p>'}`;
    h += `<p class="note" style="margin-top:12px">Dossier : ${vue.special ? esc(SPECIAUX[vue.special]) : `révision ${pos() + 1}${AF.statut() === 'archive' ? ' (archive)' : ''}`}.</p>`;
    ouvrirFiche(`Fiche de relevé · ${f.id}`, f.libelle, h);
  }
  function ouvrirReference(id) {
    const r = AF.reference(id);
    if (!r) return;
    ouvrirFiche('Fiche de référence', r.titre, `<ul class="refs">${htmlRef(r, true)}</ul>`);
  }

  /* ---------- Annonces (aria-live) ---------- */
  let minuteAnnonce = null;
  function annoncer(msg) {
    const el = $('#annonce');
    el.textContent = '';
    clearTimeout(minuteAnnonce);
    minuteAnnonce = setTimeout(() => { el.textContent = msg; }, 60);
  }
  let precedent = null;
  function annonces() {
    const b = AF.brouillon();
    const c = { p: pos(), s: AF.statut(), n: hist().length, b: b ? JSON.stringify(b) : '', sp: vue.special, niv: AF.niveau() };
    if (!precedent) { precedent = c; return; }
    const d = AF.dossier();
    let msg = '';
    if (c.sp !== precedent.sp) msg = c.sp ? `Cas particulier : ${SPECIAUX[c.sp]}.` : 'Retour à la carte.';
    else if (c.b && c.b !== precedent.b) msg = `Aperçu : ${fmt.cad(b.montant)}, non sondé${Tc && !(b.retrait !== AF.etat().retrait || b.exclusion !== AF.etat().exclusion) ? `, zone ${court(etatStation(Tc, b.montant))} sur la carte` : ', paramètre modifié'}. Entrée pour sonder, Échap pour abandonner.`;
    else if (!c.b && precedent.b && c.n === precedent.n && c.p === precedent.p) msg = 'Aperçu abandonné.';
    else if (c.n > precedent.n) msg = `Révision ${c.p + 1} (${hist()[c.p].motif}), ${AF.nomCas(AF.etat().cas)} : ${fmt.cad(AF.etat().montant)}. ${d.verdict.libelle}.`;
    else if (c.p !== precedent.p) msg = c.s === 'archive' ? `Archive : relecture de la révision ${c.p + 1}. ${d.verdict.libelle}.` : `Révision courante ${c.p + 1}. ${d.verdict.libelle}.`;
    else if (c.niv !== precedent.niv) msg = `Lecture ${c.niv === 'approfondi' ? 'approfondie' : 'essentielle'}.`;
    precedent = c;
    if (msg) annoncer(msg);
  }

  /* ---------- Feuille basse (mobile) ---------- */
  function mesurerFeuille() {
    const c = $('#coupe'), bt = $('#feuille-bascule');
    if (!mobile()) { c.classList.remove('ouverte'); $('#coupe-corps').inert = false; $('#coupe-nav').inert = false; return; }
    const peek = bt.offsetHeight + $('#coupe-tete').offsetHeight + 2;
    document.documentElement.style.setProperty('--peek', `${peek}px`);
    c.classList.toggle('ouverte', vue.feuille);
    $('#coupe-corps').inert = !vue.feuille; $('#coupe-nav').inert = !vue.feuille;
    bt.setAttribute('aria-expanded', String(vue.feuille));
    $('#feuille-txt').textContent = vue.feuille ? 'Replier la coupe' : 'Déplier la coupe';
  }

  /* ---------- Rendu complet ---------- */
  function rendre() {
    const actif = document.activeElement;
    const cle = actif && actif.dataset ? actif.dataset.cle : null;
    rendreEntete();
    rendreCarte();
    rendreLegende();
    rendreItineraire();
    rendreCartouche();
    rendreCoupe();
    rendreVoile();
    rendreRoute();
    mesurerFeuille();
    annonces();
    if (cle && (!document.activeElement || document.activeElement === document.body)) {
      const el = document.querySelector(`[data-cle="${cle}"]`);
      if (el && !el.closest('[hidden]')) el.focus({ preventScroll: true });
      else if (actif && actif.closest && actif.closest('#coupe')) $('#coupe').focus({ preventScroll: true });
    }
  }

  /* ---------- Événements ---------- */
  function fermerMenus(sauf) { $$('details.menu[open]').forEach((m) => { if (m !== sauf) m.open = false; }); }

  document.addEventListener('click', (ev) => {
    const menu = ev.target.closest('details.menu');
    fermerMenus(menu);
    const b = ev.target.closest('[data-action]');
    if (!b || b.getAttribute('aria-disabled') === 'true') return;
    const a = b.dataset.action, v = b.dataset.valeur;
    switch (a) {
      case 'cas': vue.special = null; vue.sonde = null; fermerMenus(); if (v === AF.etat().cas) rendre(); else AF.changerCas(v); break;
      case 'special': vue.special = v; vue.sonde = null; fermerMenus(); sigCoupe = null; rendre(); break;
      case 'quitter-special': vue.special = null; sigCoupe = null; rendre(); break;
      case 'niveau': AF.definirNiveau(v); break;
      case 'param': AF.proposer(JSON.parse(v)); break;
      case 'montant': proposerMontant(+v); break;
      case 'sonder': sonder(); break;
      case 'abandonner': AF.abandonner(); break;
      case 'rev': { const i = +v; vue.special = null; if (!AF.allerA(i)) rendre(); break; }
      case 'restaurer': AF.restaurer(pos()); break;
      case 'courante': AF.allerA(hist().length - 1); break;
      case 'annuler': annuler(); break;
      case 'retablir': retablir(); break;
      case 'fait': ev.preventDefault(); ouvrirFait(v); break;
      case 'ref': ouvrirReference(v); break;
      case 'relire': relireRoute(); break;
      case 'demo': definirDemo(v); break;
      case 'fermer-sonde': vue.sonde = null; rendreSonde(); break;
      case 'aller': { ev.preventDefault(); const s = document.getElementById(v); if (s) { s.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }); s.focus({ preventScroll: true }); } break; }
      default: break;
    }
  });

  $('#feuille-bascule').addEventListener('click', () => { vue.feuille = !vue.feuille; mesurerFeuille(); });
  $('#demo').addEventListener('change', (ev) => definirDemo(ev.target.value));
  $('.evitement').addEventListener('click', (ev) => { ev.preventDefault(); if (mobile()) { vue.feuille = true; mesurerFeuille(); } $('#coupe').focus(); });
  $('#fiche-fermer').addEventListener('click', () => $('#fiche').close());
  $('#fiche').addEventListener('click', (ev) => { if (ev.target === ev.currentTarget) ev.currentTarget.close(); });
  $('#fiche').addEventListener('close', () => { if (ouvreur && ouvreur.isConnected) ouvreur.focus(); ouvreur = null; });

  /* Carte : survol, clic, glisser */
  const svg = $('#carte'), cadre = $('#carte-cadre'), poignee = $('#poignee');
  const local = (ev) => { const r = cadre.getBoundingClientRect(); return { x: ev.clientX - r.left, y: ev.clientY - r.top }; };
  svg.addEventListener('pointermove', (ev) => {
    if (vue.glisse) { const p = local(ev); proposerMontant(stationPlusProche(p.y)); return; }
    if (ev.pointerType !== 'mouse' || vue.sonde || vue.special) return;
    const p = local(ev), s = cible(p.x, p.y);
    if (!memeCible(s, vue.survol)) { vue.survol = s; rendreSonde(); }
  });
  svg.addEventListener('pointerleave', () => { if (vue.survol) { vue.survol = null; rendreSonde(); } });
  svg.addEventListener('pointerdown', (ev) => {
    if (ev.pointerType !== 'mouse' || ev.button !== 0 || vue.special || ev.target.closest('[data-action]')) return;
    const p = local(ev), s = cible(p.x, p.y);
    if (s && s.type === 'station') { vue.glisse = true; svg.setPointerCapture(ev.pointerId); proposerMontant(s.m); }
  });
  const finGlisse = (ev) => { if (vue.glisse) { vue.glisse = false; try { svg.releasePointerCapture(ev.pointerId); } catch (e) { /* déjà relâché */ } } };
  svg.addEventListener('pointerup', finGlisse);
  svg.addEventListener('pointercancel', finGlisse);
  svg.addEventListener('click', (ev) => {
    if (vue.special || ev.target.closest('[data-action]')) return;
    const p = local(ev), s = cible(p.x, p.y);
    if (!s) { vue.sonde = null; rendreSonde(); return; }
    if (s.type === 'station') { vue.sonde = null; vue.survol = null; proposerMontant(s.m); return; }
    vue.sonde = memeCible(s, vue.sonde) ? null : s; vue.survol = null; rendreSonde();
  });

  let glissePoignee = false;
  poignee.addEventListener('pointerdown', (ev) => {
    if (vue.special || !Tc) return;
    glissePoignee = true; poignee.setPointerCapture(ev.pointerId); poignee.focus({ preventScroll: true }); ev.preventDefault();
  });
  poignee.addEventListener('pointermove', (ev) => { if (glissePoignee) proposerMontant(stationPlusProche(local(ev).y)); });
  const finPoignee = (ev) => { glissePoignee = false; try { poignee.releasePointerCapture(ev.pointerId); } catch (e) { /* déjà relâché */ } };
  poignee.addEventListener('pointerup', finPoignee);
  poignee.addEventListener('pointercancel', finPoignee);
  poignee.addEventListener('keydown', (ev) => {
    if (vue.special || !Tc) return;
    const ms = Tc.stations.map((s) => s.montant), cur = montantVise();
    let k = ms.indexOf(cur); if (k < 0) k = 0;
    switch (ev.key) {
      case 'ArrowUp': case 'ArrowRight': k = Math.min(ms.length - 1, k + 1); break;
      case 'ArrowDown': case 'ArrowLeft': k = Math.max(0, k - 1); break;
      case 'PageUp': k = Math.min(ms.length - 1, k + 3); break;
      case 'PageDown': k = Math.max(0, k - 3); break;
      case 'Home': k = 0; break;
      case 'End': k = ms.length - 1; break;
      case 'Enter': case ' ': ev.preventDefault(); sonder(); return;
      case 'Escape': if (AF.perime()) { ev.preventDefault(); ev.stopPropagation(); AF.abandonner(); } return;
      default: return;
    }
    ev.preventDefault();
    proposerMontant(ms[k]);
  });

  document.addEventListener('keydown', (ev) => {
    const mod = ev.metaKey || ev.ctrlKey;
    if ($('#fiche').open) return;
    if (mod && !ev.altKey && (ev.key === 'z' || ev.key === 'Z')) { ev.preventDefault(); if (ev.shiftKey) retablir(); else annuler(); return; }
    if (mod && !ev.altKey && (ev.key === 'y' || ev.key === 'Y')) { ev.preventDefault(); retablir(); return; }
    if (ev.key === 'Escape') {
      const ouvert = $('details.menu[open]');
      if (ouvert) { ouvert.open = false; ouvert.querySelector('summary').focus(); return; }
      if (vue.sonde) { vue.sonde = null; rendreSonde(); return; }
      if (mobile() && vue.feuille) { vue.feuille = false; mesurerFeuille(); $('#feuille-bascule').focus(); }
    }
  });

  /* ---------- Démarrage ---------- */
  $('#c-defs').innerHTML = DEFS;
  const gSonde = document.createElementNS(SVGNS, 'g'); gSonde.id = 'c-sonde'; svg.appendChild(gSonde);
  const note = document.createElement('p'); note.id = 'note-carte'; note.className = 'note-carte'; note.hidden = true;
  cadre.insertAdjacentElement('afterend', note);
  AF.abonner(rendre);
  if ('ResizeObserver' in window) new ResizeObserver(() => { rendreCarte(); rendreCartouche(); mesurerFeuille(); }).observe(cadre);
  window.addEventListener('resize', mesurerFeuille);
  rendre();
})();
