/* Épure · Second avis — prototype 5.
   La comparaison est l'interface : le portefeuille sans et avec la demande, mesurés de la même façon,
   dessinés comme une planche technique (deux vues, des cotes, un cartouche).
   Aucun chiffre n'est calculé ici : tout vient de window.AF (socle commun, dossiers précalculés). */
(() => {
  'use strict';
  const AF = window.AF;
  if (!AF) {
    document.body.insertAdjacentHTML('afterbegin', '<p role="alert" style="padding:16px">Socle introuvable : ../socle/socle.js n’a pas été chargé.</p>');
    return;
  }

  /* ------------------------------------------------------------------ outils */
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fr = AF.fmt.nombre;
  /* Vrai signe moins à l'écran (typographie seulement ; la valeur ne change pas). */
  const moins = (s) => String(s).replace(/(^|[\s(«])-(?=\d)/g, '$1−');
  const N = {
    pct: (v, d = 1) => moins(AF.fmt.pct(v, d)),
    cad: (v) => moins(AF.fmt.cad(v)),
    pts: (v, d = 1) => moins(AF.fmt.pts(v, d)),
  };
  const propre = (t) => moins(AF.propre(t));
  const exact = (x) => (typeof x === 'number' ? moins(String(x).replace('.', ',')) : String(x));
  const reduit = window.matchMedia('(prefers-reduced-motion: reduce)');

  const ETATS = AF.ETATS;
  const NIV_ETAT = { ok: 'coherent', orange: 'ajustement', rouge: 'incoherent', gris: 'indetermine', non_evaluee: 'indetermine' };
  const SENS = { aggrave: 'aggrave', ameliore: 'améliore', neutre: 'neutre' };
  const TYPE_COURT = { FAIT: 'Fait', HYPOTHESE: 'Hypothèse', SCENARIO: 'Scénario' };
  const TYPE_CLASSE = { FAIT: 't-fait', HYPOTHESE: 't-hyp', SCENARIO: 't-scen' };
  const NATURES = { donnee: 'Donnée', preference: 'Préférence', contrainte: 'Contrainte', inconnu: 'Inconnue' };
  const CODE = new Set(['Analyste', 'Gardien', 'Contrôle données']);
  /* Où la règle se voit sur la planche : la mesure ou la barre de répartition qu'elle concerne. */
  const CIBLE = { capacite: 'pire_chute', concentration: 'repartition', exclusion: 'repartition', retrait: 'repartition' };
  const SECTEURS = { Energy: 'Énergie' };
  const LIB_SPECIAL = {
    sans_epargne: 'Épargne totale inconnue : le profil ne dit pas combien tu as d’épargne.',
    impossible: 'Montant demandé supérieur à l’épargne totale déclarée.',
    hors_univers: 'Placement absent des 31 actifs du jeu de départ.',
  };
  const LIB_PHASE = { fait: 'rejoué', 'en-cours': 'relecture…', attente: 'en attente' };

  /* ------------------------------------------------------------------ état de la page (pas des faits) */
  let special = null;          // cas particulier affiché hors historique
  let demo = 'normal';         // états de démonstration : normal | chargement | erreur | reprise
  let epingles = [];           // révisions épinglées pour « planches à comparer » (au plus deux)
  const rideau = { idx: null, cle: '' };
  let relecture = null, arretRelecture = null;
  let limitesOuvert = null;    // null : suit le niveau de lecture
  let fiches = new Map(), nFiche = 0, declencheur = null;
  let cleVerdict = '', dernierStatut = '', dernierDossier = null;
  let planifie = false, focusApres = null;
  let geo = null;              // géométrie du graphe du rideau

  /* ------------------------------------------------------------------ petites fabriques */
  function indice(i) {
    let s = '', k = i + 1;
    while (k > 0) { const r = (k - 1) % 26; s = String.fromCharCode(65 + r) + s; k = Math.floor((k - 1) / 26); }
    return s;
  }
  /* Formes distinctes par état (jamais la couleur seule). */
  const SYMB = {
    coherent: '<circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/>',
    ajustement: '<path d="M12 2.8 L21.2 12 L12 21.2 L2.8 12 Z" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M2.8 12 L21.2 12 L12 21.2 Z" fill="currentColor"/>',
    incoherent: '<rect x="3.6" y="3.6" width="16.8" height="16.8" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M3.6 3.6 L20.4 20.4 M20.4 3.6 L3.6 20.4" stroke="currentColor" stroke-width="2.2"/>',
    indetermine: '<circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-dasharray="3.2 2.4"/><path d="M9.6 9.4 C9.6 6.6 14.6 6.6 14.6 9.4 C14.6 11.2 12 11.4 12 13.6" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="16.6" r="1.3" fill="currentColor"/>',
  };
  const symbole = (etat) => `<svg class="symb s-${etat}" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false" style="color:var(--${{ coherent: 'ok', ajustement: 'aj', incoherent: 'ko', indetermine: 'ind' }[etat] || 'ind'})">${SYMB[etat] || SYMB.indetermine}</svg>`;
  const typeTag = (t) => (t ? `<span class="type ${TYPE_CLASSE[t] || 't-fait'}">${esc(AF.niveau() === 'approfondi' ? AF.TYPES[t] || t : TYPE_COURT[t] || t)}</span>` : '');

  /* Registre des preuves : chaque valeur cliquable porte la description de sa fiche. */
  const enregistrer = (desc) => { const k = `f${++nFiche}`; fiches.set(k, desc); return k; };
  const preuve = (desc, contenu, o = {}) => `<button type="button" class="${o.cls || 'preuve'}" data-action="fiche" data-fiche="${enregistrer(desc)}"${o.id ? ` id="${o.id}"` : ''}${o.label ? ` aria-label="${esc(o.label)}"` : ''}>${contenu}</button>`;
  const puces = (ids, d) => [...new Set((ids || []).filter(Boolean))].map((id) => {
    const f = AF.fait(id, d);
    return preuve({ titre: f ? f.libelle : `Fait ${id}`, faits: [id], d }, esc(id), { cls: 'puce-fait', label: `Fait ${id}${f ? ` (${f.libelle})` : ''} : ouvrir la fiche` });
  }).join('');

  function departDe(cas) {
    const o = Object.fromEntries(AF.donnees.cas[cas].depart.split(';').map((p) => p.split('=')));
    return { cas, montant: +o.m, retrait: o.r === 'na' ? null : +o.r, exclusion: o.x === '1' };
  }
  const estEtatDepart = (e) => { const p = departDe(e.cas); return p.montant === e.montant && p.retrait === e.retrait && p.exclusion === e.exclusion; };
  function secteurExclu(cas) {
    const dep = AF.dossierDe(departDe(cas));
    const ex = (dep && dep.profil.exclusions) || [];
    return ex.map((s) => SECTEURS[s] || s).join(', ');
  }
  const heure = (ts) => { try { return new Date(ts).toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' }); } catch (e) { return ''; } };
  const kCourt = (v) => (v < 1000 ? `${fr(v)} $` : `${fr(v / 1000, v % 1000 === 0 ? 0 : v % 100 === 0 ? 1 : 2)} k`);

  /* Contexte d'affichage : dossier courant, ou cas particulier. */
  function contexte() {
    const n = AF.niveau();
    if (special === 'hors_univers') return { special, n, hu: AF.speciaux.hors_univers, d: null, st: 'special' };
    if (special) return { special, n, d: AF.speciaux[special].dossier, st: 'special' };
    return { n, d: AF.dossier(), e: AF.etat(), b: AF.brouillon(), st: AF.statut(), pos: AF.position(), hist: AF.historique() };
  }

  /* ------------------------------------------------------------------ mesures et cotes */
  /* Échelle graphique commune aux deux vues, constante pour tout le cas : les barres bougent sur la même règle. */
  const echelles = {};
  function pasJoli(v) { if (!(v > 0)) return 1; const p = Math.pow(10, Math.floor(Math.log10(v))), n = v / p; return (n < 1.5 ? 1 : n < 3 ? 2 : n < 7 ? 5 : 10) * p; }
  function arrondiHaut(v) { if (!(v > 0)) return 1; const p = Math.pow(10, Math.floor(Math.log10(v))), n = v / p; return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * p; }
  function echelleCas(cas) {
    if (echelles[cas]) return echelles[cas];
    const max = {};
    Object.values(AF.donnees.cas[cas].variantes).forEach((d) => AF.mesures(d).forEach((m) => {
      max[m.cle] = Math.max(max[m.cle] || 0, Math.abs(m.avant || 0), Math.abs(m.apres || 0));
    }));
    Object.keys(max).forEach((k) => { max[k] = arrondiHaut(max[k] * 1.05); });
    echelles[cas] = max;
    return max;
  }
  const echelleTexte = (m, max) => (m.unite === '$' ? AF.fmt.cad(max) : `${fr(max)} %`);

  function valeurMesure(m, v) {
    if (v == null) return '—';
    if (m.unite === '$') return N.cad(v);
    const s = N.pct(v, 1);
    return AF.niveau() === 'approfondi' && (m.cle === 'volatilite' || m.cle === 'rendement') ? `${s}/an` : s;
  }
  const pointsMots = (v) => { const a = Math.abs(v); return `${fr(a, 1)} point${a >= 2 ? 's' : ''}`; };
  /* Essentiel : la grandeur en mots ; approfondi : l'écart signé, après moins avant. */
  function ecartAffiche(m) {
    if (AF.niveau() === 'essentiel') return m.unite === '$' ? AF.fmt.cad(Math.abs(m.ecart)) : pointsMots(m.ecart);
    return m.unite === '$' ? `${m.ecart > 0 ? '+' : ''}${N.cad(m.ecart)}` : N.pts(m.ecart, 1);
  }
  /* Le sens n'est calculé par le moteur que pour la pire baisse ; ailleurs, on décrit la direction sans juger. */
  const MOTS = {
    pire_chute: (m) => ({ aggrave: 'baisse plus profonde', ameliore: 'baisse moins profonde' }[m.sens] || 'baisse inchangée'),
    volatilite: (m) => (m.ecart > 0 ? 'variations plus amples' : m.ecart < 0 ? 'variations moins amples' : 'variations inchangées'),
    rendement: (m) => (m.ecart > 0 ? 'progression plus rapide' : m.ecart < 0 ? 'progression plus lente' : 'progression inchangée'),
    valeur_finale: (m) => (m.ecart > 0 ? 'valeur de fin plus haute' : m.ecart < 0 ? 'valeur de fin plus basse' : 'valeur de fin inchangée'),
  };
  const sensCote = (m) => (m.sens ? m.sens : m.ecart > 0 ? 'hausse' : m.ecart < 0 ? 'baisse' : 'neutre');
  const idMesure = (d, cle, bras) => ((d.comparaison && d.comparaison.faits) || {})[`${bras === 'sans' ? 'avant' : 'apres'}_${cle}`];
  const idEcart = (d, cle) => ((d.comparaison && d.comparaison.faits) || {})[`ecart_${cle}`];
  function reperes(d) {
    return (d.regles || []).map((r, i) => ({ ...r, rep: i + 1, cible: CIBLE[r.code] }))
      .filter((r) => r.cible && (r.niveau === 'rouge' || r.niveau === 'orange'));
  }
  const bulles = (list) => list.map((r) => `<button type="button" class="bulle b-${r.niveau}" id="bulle-${r.code}" data-action="repere" data-code="${r.code}" aria-label="Repère ${r.rep} : règle « ${esc(r.libelle)} », ${esc(AF.NIVEAUX_REGLE[r.niveau])}. Aller à la nomenclature">${r.rep}</button>`).join('');

  /* ------------------------------------------------------------------ rendu général */
  function rendre() {
    planifie = false;
    const actif = document.activeElement;
    const cleFocus = actif && actif !== document.body && actif.id ? actif.id : null;
    fiches = new Map(); nFiche = 0;
    const ctx = contexte();
    document.body.dataset.statut = ctx.st;
    document.body.dataset.niveau = ctx.n;
    document.body.dataset.demo = demo;
    const animer = ctx.d !== dernierDossier && dernierDossier !== null && !reduit.matches;
    dernierDossier = ctx.d;

    rendreOutils(ctx);
    rendreTete(ctx);
    rendreVues(ctx);
    rendreVerdict(ctx);
    rendreCartouche(ctx);
    rendreRideau(ctx);
    rendreNomenclature(ctx);
    rendreNotes(ctx);
    rendreVariantes(ctx);
    rendreGamme(ctx);
    rendreLimites(ctx);
    $('tampon').textContent = ctx.st === 'archive' ? `Archive : révision ${indice(ctx.pos)}` : '';

    const vues = $('vues');
    vues.classList.toggle('trace-anim', animer);
    if (animer) setTimeout(() => vues.classList.remove('trace-anim'), 900);

    annoncerStatut(ctx);
    const cible = focusApres || (cleFocus && document.activeElement !== actif ? cleFocus : null);
    focusApres = null;
    if (cible) {
      const el = $(cible);
      if (el && el.offsetParent !== null) el.focus({ preventScroll: true });
      if (document.activeElement !== el && $('tete-titre')) $('tete-titre').focus({ preventScroll: true });
    }
  }
  const planifier = () => { if (!planifie) { planifie = true; requestAnimationFrame(rendre); } };

  function annoncer(msg) { const a = $('annonce'); a.textContent = ''; setTimeout(() => { a.textContent = msg; }, 80); }
  function annoncerStatut(ctx) {
    let msg = '';
    if (ctx.special) msg = `Cas particulier affiché : ${LIB_SPECIAL[ctx.special]}`;
    else if (ctx.st === 'apercu') msg = `Aperçu : ${AF.decrire(ctx.e, ctx.b)}. La vue avec ta demande et le verdict sont périmés jusqu’au recalcul.`;
    else if (ctx.st === 'archive') msg = `Archive : tu relis la révision ${indice(ctx.pos)}.`;
    else msg = `Révision ${indice(ctx.pos)} en vigueur.`;
    const cle = `${ctx.st}|${ctx.pos}|${msg}`;
    if (cle !== dernierStatut) { if (dernierStatut) annoncer(msg); dernierStatut = cle; }
  }

  /* ------------------------------------------------------------------ barre d'outils */
  function rendreOutils(ctx) {
    const cas = special ? null : ctx.e.cas;
    $('choix-cas').innerHTML = AF.cas().map((c) => `<button type="button" id="cas-${c}" data-action="cas" data-cas="${c}" aria-pressed="${c === cas}">${esc(AF.nomCas(c))}</button>`).join('');
    ['essentiel', 'approfondi'].forEach((n) => $(`niv-${n}`).setAttribute('aria-pressed', String(ctx.n === n)));
    $('nivm').setAttribute('aria-pressed', String(ctx.n === 'approfondi'));
    $('btn-annuler').disabled = !AF.peutAnnuler();
    $('btn-refaire').disabled = !AF.peutRetablir();
    $('lien-galerie').href = AF.lien('../index.html');
    document.querySelectorAll('[data-proto]').forEach((a) => { a.href = AF.lien(`../${a.dataset.proto}/index.html`); });
    $('meta-date').textContent = `générées le ${AF.fmt.date(String(AF.meta.genere_le).slice(0, 10))}`;
    $('meta-commit').textContent = AF.meta.commit;
    $('choix-demo').value = demo;
  }

  /* ------------------------------------------------------------------ en-tête de la planche */
  function phraseTete(ctx) {
    const d = ctx.d, k = d.comparaison || {};
    const perime = ctx.st === 'apercu' ? ' perime' : '';
    if (!k.disponible) {
      const raison = String(k.raison || (d.questions || [])[0] || 'information manquante').replace(/\.\s*$/, '');
      return `<p class="tete-phrase">Aucune comparaison mesurée : ${esc(raison)}.</p>`;
    }
    const pc = AF.mesures(d).find((m) => m.cle === 'pire_chute');
    const f = k.fenetre || {};
    const per = `${f.debut} → ${f.fin}`;
    if (ctx.n === 'essentiel') {
      const verbe = { aggrave: 'aurait creusé', ameliore: 'aurait réduit' }[pc.sens] || 'n’aurait pas changé';
      const de = pc.sens === 'aggrave' || pc.sens === 'ameliore' ? ` de <strong>${esc(pointsMots(pc.ecart))}</strong>` : '';
      return `<p class="tete-phrase${perime}">Sur la période observée (${esc(per)}), ta demande ${verbe}${de} la plus forte baisse de ton portefeuille : ${esc(valeurMesure(pc, pc.apres))} au lieu de ${esc(valeurMesure(pc, pc.avant))}.</p>`;
    }
    return `<p class="tete-phrase${perime}">Écart apparié de la pire baisse, après moins avant : <strong>${esc(N.pts(pc.ecart, 1))}</strong> (sens calculé par le moteur : ${esc(SENS[pc.sens] || pc.sens)}). Même fenêtre ${esc(per)}, ${esc(fr(f.observations))} observations, même méthode (moteur ${esc(k.moteur)}, ${esc(k.version_moteur)}).</p>`;
  }

  function banniereDemo(ctx) {
    const pos = ctx.special ? '' : indice(ctx.pos);
    const t = {
      chargement: ['Démonstration · chargement', 'Les étapes enregistrées de ce dossier sont relues dans leur ordre (gamme d’opérations, plus bas). Aucun calcul n’est relancé et aucun agent ne travaille en direct.', '<button type="button" id="btn-demo-fin" data-action="demo-fin">Arrêter la démonstration</button>'],
      erreur: ['Démonstration · erreur', 'On montre ici une analyse qui n’aurait pas abouti : tant que le Gardien n’a pas appliqué ses règles, aucun verdict n’est affiché, ni deviné.', '<button type="button" class="primaire" id="btn-demo-reprendre" data-action="demo-reprendre">Reprendre l’analyse</button>'],
      reprise: ['Démonstration · reprise', `La planche est reprise depuis la dernière révision enregistrée dans ce navigateur${pos ? ` (révision ${pos})` : ''} : rien n’a été perdu, rien n’a été recalculé.`, '<button type="button" id="btn-demo-fin" data-action="demo-fin">Terminer la démonstration</button>'],
    }[demo];
    return t ? `<div class="banniere b-demo" role="region" aria-label="État de démonstration"><div><p><span class="banniere-l">${t[0]}</span>${esc(t[1])}</p>${t[2]}</div></div>` : '';
  }

  function bannieres(ctx) {
    let h = demo !== 'normal' ? banniereDemo(ctx) : '';
    if (ctx.special) {
      h += `<div class="banniere b-special" role="region" aria-label="Cas particulier"><div><p><span class="banniere-l">Cas particulier · hors historique</span>${esc(LIB_SPECIAL[ctx.special])} Dossier réel du moteur, affiché tel quel : rien n’y est modifiable.</p><button type="button" id="btn-quitter-special" data-action="quitter-special">Revenir à la planche en vigueur</button></div></div>`;
    } else if (ctx.st === 'archive') {
      const der = ctx.hist.length - 1;
      h += `<div class="banniere b-archive" role="region" aria-label="Révision archivée"><div><p><span class="banniere-l">Archive · révision ${indice(ctx.pos)}</span>Tu relis une révision précédente (${esc(ctx.hist[ctx.pos].motif)}). Elle reste consultable ; rien n’est effacé. La révision en vigueur est ${indice(der)}.</p><button type="button" class="primaire" id="btn-restaurer" data-action="restaurer" data-i="${ctx.pos}">Rétablir cette révision</button><button type="button" id="btn-vigueur" data-action="vigueur">Revenir à la révision ${indice(der)}</button></div></div>`;
    } else if (ctx.st === 'apercu') {
      h += `<div class="banniere b-apercu" role="region" aria-label="Aperçu non recalculé"><div><p><span class="banniere-l">Aperçu · non recalculé</span>${esc(AF.decrire(ctx.e, ctx.b))}. La vue « Avec ta demande », les cotes et le verdict affichés sont ceux de la révision ${indice(ctx.pos)} : ils sont périmés jusqu’au recalcul.</p><button type="button" class="primaire" id="btn-appliquer" data-action="appliquer">Recalculer la planche</button><button type="button" id="btn-abandonner" data-action="abandonner">Abandonner l’aperçu</button></div></div>`;
    }
    return h ? `<div class="bannieres">${h}</div>` : '';
  }

  function rendreTete(ctx) {
    const d = ctx.d;
    let h = bannieres(ctx);
    if (ctx.special === 'hors_univers') {
      h += `<div class="plaque tete-plaque"><p class="surtitre"><span>Planche · cas particulier</span><span>Placement hors univers</span></p>
        <h1 id="tete-titre" tabindex="-1">Demande refusée avant toute analyse</h1>
        <p class="tete-phrase">${esc(ctx.hu.message)} <span class="puce-cote">réponse du produit : statut ${esc(ctx.hu.statut)}</span></p>
        <p class="tete-reformulation">Rien n’est mesuré ni coté : sans placement connu, le moteur historique n’a pas de série à comparer.</p></div>`;
      $('tete').innerHTML = h;
      return;
    }
    const qs = d.questions || [];
    let question = '';
    if (qs.length) {
      const p = ctx.special ? null : AF.parametres();
      const peut = !ctx.special && ctx.e.retrait == null && p.retrait.some((r) => r != null);
      const actions = peut
        ? `<div class="question-actions">${p.retrait.filter((r) => r != null).map((r) => `<button type="button" class="primaire" id="rep-retrait-${r}" data-action="proposer" data-patch="${esc(JSON.stringify({ retrait: r }))}">Répondre : oui, retrait ${esc(AF.fmt.retrait(r))}</button>`).join('')}<span class="question-note">Répondre crée un aperçu ; la planche devra être recalculée. La même réponse se donne par la case « Retrait prévu » du cartouche.</span></div>`
        : ctx.special ? '<p class="question-note">La réponse se saisit dans le produit : non réalisé dans ce prototype.</p>' : '';
      question = `<div class="question" role="region" aria-labelledby="q-titre"><p class="question-l" id="q-titre">${ctx.special ? 'Ce qui manque pour conclure' : 'Conclusion conditionnelle · question décisive'}</p>${qs.map((q) => `<p>${esc(propre(String(q).replace(/^Question décisive\s*[—-]\s*/, '')))}</p>`).join('')}${actions}</div>`;
    }
    const reform = ctx.n === 'approfondi' && d.texte && d.texte.reformulation ? `<p class="tete-reformulation">Reformulation du Profileur : ${esc(propre(d.texte.reformulation))}</p>` : '';
    h += `<div class="plaque tete-plaque">
      <p class="surtitre"><span>Planche · ${esc(d.profil.nom)}${ctx.special ? ' · cas particulier' : ` · révision ${indice(ctx.pos)}`}</span><span>Placement demandé : ${esc(d.demande.ticker)}</span><span>Montant étudié : ${esc(AF.fmt.cad(d.demande.montant_cad))}</span></p>
      <h1 id="tete-titre" tabindex="-1">« ${esc(d.demande.texte)} »</h1>
      ${phraseTete(ctx)}${reform}
    </div>${question}`;
    $('tete').innerHTML = h;
  }

  /* ------------------------------------------------------------------ les deux vues et leurs cotes */
  function tetePanneau(bras, ctx, d) {
    const sans = bras === 'sans';
    const sous = !d ? '' : sans ? 'tes placements actuels, sans rien changer' : `+ ${AF.fmt.cad(d.demande.montant_cad)} dans ${d.demande.ticker}, même mesure`;
    const perime = !sans && ctx.st === 'apercu'
      ? `<div class="p-perime"><span class="tag tag-perime">Périmé</span><span>tracé de la révision ${indice(ctx.pos)}, à recalculer</span><button type="button" class="primaire" id="btn-appliquer-vue" data-action="appliquer">Recalculer la planche</button></div>`
      : '';
    return `<header class="p-tete"><span class="p-num">Vue ${sans ? 1 : 2}</span><h3 class="p-titre" id="vue-${bras}-titre">${sans ? 'Sans ta demande' : 'Avec ta demande'}</h3>${sous ? `<p class="p-sous">${esc(sous)}</p>` : ''}${perime}</header>`;
  }

  function curseurMontant(ctx) {
    const vals = [...AF.parametres().montant].sort((a, b) => a - b);
    const base = ctx.b || ctx.e;
    const idx = Math.max(0, vals.indexOf(base.montant));
    const etats = vals.map((v) => { const dd = AF.dossierDe({ ...base, montant: v }); return dd ? dd.verdict.etat : 'indetermine'; });
    const pos = (i) => (vals.length > 1 ? (i / (vals.length - 1)) * 100 : 50);
    const apercu = !!ctx.b && ctx.b.montant !== ctx.e.montant;
    const desc = vals.map((v, i) => `${AF.fmt.cad(v)} : ${ETATS[etats[i]].court}`).join(' ; ');
    return `<div class="montant">
      <div class="montant-tete"><label class="montant-l" for="curseur-montant">Cote éditable · montant</label><output class="montant-o${apercu ? ' apercu' : ''}" id="sortie-montant" for="curseur-montant">${esc(AF.fmt.cad(base.montant))}${apercu ? ' · aperçu' : ''}</output></div>
      <div class="montant-piste">
        <input type="range" id="curseur-montant" min="0" max="${vals.length - 1}" step="1" value="${idx}" data-vals="${vals.join(',')}" aria-valuetext="${esc(AF.fmt.cad(base.montant))}" aria-describedby="crans-desc">
        <div class="crans${vals.some((v) => kCourt(v).length >= 6) ? ' dense' : ''}" aria-hidden="true">${vals.map((v, i) => `<span class="cran${v === base.montant ? ' cran-actuel' : ''}" style="left:${pos(i)}%">${symbole(etats[i])}<span class="cran-l">${esc(kCourt(v))}</span></span>`).join('')}</div>
      </div>
      <p class="crans-note" id="crans-desc">${vals.length} crans précalculés, chacun marqué du verdict du Gardien. Lâcher crée un aperçu. <span class="sr">${esc(desc)}.</span></p>
    </div>`;
  }

  function repartition(bras, d, ctx, reps) {
    const k = d.comparaison, sans = bras === 'sans';
    const poids = sans ? k.poids_avant : k.poids_apres;
    const ordre = [...Object.keys(k.poids_avant), ...Object.keys(k.poids_apres).filter((t) => !(t in k.poids_avant))];
    const tk = d.demande.ticker;
    const idF = (k.faits || {})[sans ? 'poids_avant' : 'poids_apres'];
    const fF = AF.fait(idF, d);
    const segs = ordre.filter((t) => poids[t] != null).map((t) => ({ t, w: poids[t] * 100, neuf: !sans && t === tk && !(t in k.poids_avant) }));
    const neuf = segs.find((s) => s.neuf);
    const barre = `<div class="barre-poids">${segs.map((s) => `<span class="seg${s.neuf ? ' seg-neuf' : ''}" style="flex:0 0 ${s.w}%">${s.w >= 17 ? `<span class="seg-t">${esc(s.t)}</span>` : ''}</span>`).join('')}</div>`;
    const legende = `<ul class="legende">${segs.map((s) => `<li class="${s.neuf ? 'neuf' : ''}">${preuve({ titre: fF ? fF.libelle : 'Allocation', faits: [idF], d, affiche: `${s.t} ${N.pct(s.w, 1)}` }, `${esc(s.t)} ${esc(N.pct(s.w, 1))}`, { label: `${s.t}, ${N.pct(s.w, 1)} de l’épargne ${sans ? 'sans' : 'avec'} ta demande : ouvrir la fiche` })}</li>`).join('')}</ul>`;
    let cote;
    if (sans) {
      cote = `<div class="cote-h" aria-hidden="true"><i class="bout bout-g"></i><span class="cote-h-val">épargne ${esc(AF.fmt.cad(d.profil.epargne_totale_cad))}</span><i class="bout bout-d"></i></div>`;
    } else {
      /* En aperçu, la cote dessinée reste celle de la révision affichée, barrée : le nouveau montant se lit sur le curseur. */
      const perime = ctx.st === 'apercu';
      cote = `<div class="cote-h" aria-hidden="true" style="color:transparent">${neuf ? `<span class="cote-seg" style="left:${100 - neuf.w}%;width:${neuf.w}%"><span class="cote-seg-val${perime ? ' perime' : ''}">${esc(AF.fmt.cad(d.demande.montant_cad))}</span></span>` : ''}</div>`;
    }
    const bRep = sans ? [] : reps.filter((r) => r.cible === 'repartition');
    const attache = bRep.length && neuf ? `<i class="attache" style="--a:${100 - neuf.w / 2}%;--c:${bRep[0].niveau === 'rouge' ? 'var(--ko)' : 'var(--aj)'};top:13px"></i>` : '';
    const curseur = !sans && !ctx.special && demo !== 'erreur' ? curseurMontant(ctx) : '';
    return `<div class="repartition">
      <span class="m-titre">${sans ? 'Répartition de l’épargne' : 'Répartition avec ta demande'}</span>
      <div class="r-ligne" style="align-items:flex-start"><div class="r-corps">${cote}<div style="position:relative" aria-hidden="true">${barre}${attache}</div>${legende}${curseur}</div><span class="m-slot" style="padding-top:20px;justify-content:flex-start">${bulles(bRep)}</span></div>
    </div>`;
  }

  function ligneMesure(bras, m, ech, ctx, reps) {
    const d = ctx.d, sans = bras === 'sans';
    const v = sans ? m.avant : m.apres;
    const max = ech[m.cle] || 1;
    const L = Math.min(100, (Math.abs(v) / max) * 100), L0 = Math.min(100, (Math.abs(m.avant) / max) * 100);
    const idF = idMesure(d, m.cle, bras);
    const desc = { titre: `${m.titre} · ${sans ? 'sans' : 'avec'} ta demande`, faits: idF ? [idF] : [], d, affiche: valeurMesure(m, v), note: idF ? '' : 'Aucun fait F-n n’est lié à cette mesure dans ce dossier.' };
    const lab = `${m.titre}, ${sans ? 'sans' : 'avec'} ta demande : ${valeurMesure(m, v)}. Ouvrir la fiche de mesure`;
    let jauge;
    if (sans) jauge = `<span class="barre" style="--l:${L}%"></span>`;
    else {
      jauge = `<span class="barre" style="--l:${Math.min(L, L0)}%"></span>`;
      if (L > L0) jauge += `<span class="surplus" style="--a:${L0}%;--b:${L - L0}%"></span>`;
      if (L < L0) jauge += `<span class="manque" style="--a:${L}%;--b:${L0 - L}%"></span>`;
      jauge += `<span class="fantome" style="--a:${L0}%"></span>`;
    }
    const mes = sans ? [] : reps.filter((r) => r.cible === m.cle);
    const attache = mes.length ? `<i class="attache" style="--a:${L}%;--c:${mes[0].niveau === 'rouge' ? 'var(--ko)' : 'var(--aj)'}"></i>` : '';
    return `<div class="mesure" data-cle="${m.cle}">
      <span class="m-titre">${esc(m.titre)}</span>
      <div class="m-ligne">${preuve(desc, esc(valeurMesure(m, v)), { cls: 'preuve m-val', label: lab })}<div class="jauge" aria-hidden="true">${jauge}${attache}<span class="echelle">échelle 0 → ${esc(echelleTexte(m, max))}</span></div><span class="m-slot">${bulles(mes)}</span></div>
    </div>`;
  }

  function cote(m, ctx) {
    const d = ctx.d;
    const idE = idEcart(d, m.cle);
    const bras = [idMesure(d, m.cle, 'sans'), idMesure(d, m.cle, 'avec')];
    const val = ecartAffiche(m);
    const mots = MOTS[m.cle](m);
    const sensTxt = m.sens ? `sens calculé par le moteur : ${SENS[m.sens] || m.sens}` : 'après moins avant';
    const desc = {
      titre: `Cote · ${m.titre}`, d, affiche: `${val} (${mots})`,
      faits: (idE ? [idE, ...bras] : bras).filter(Boolean),
      note: idE ? '' : 'Écart affiché = après moins avant, soustrait à l’écran par le socle commun à partir des deux faits ci-dessous ; le moteur ne publie pas de fait F-n pour cet écart.',
    };
    return `<div class="cote" data-cle="${m.cle}" data-sens="${sensCote(m)}">
      <span class="c-titre" aria-hidden="true">${esc(m.titre)}</span>
      <span class="c-bouts" aria-hidden="true"><span class="b-sans">sans ${esc(valeurMesure(m, m.avant))}</span><span class="b-avec">avec ${esc(valeurMesure(m, m.apres))}</span></span>
      <span class="c-trait" aria-hidden="true"><i class="c-att"></i><i class="c-fl c-fl-g"></i><i class="c-ligne"></i><i class="c-fl c-fl-d"></i><i class="c-att"></i></span>
      ${preuve(desc, esc(val), { cls: 'preuve c-val', label: `Cote, ${m.titre} : ${val}, ${mots}. Ouvrir la fiche de mesure` })}
      <span class="c-mots">${esc(ctx.n === 'essentiel' ? mots : `${mots} · ${sensTxt}`)}</span>
    </div>`;
  }

  function coteRepartition(d, ctx) {
    const k = d.comparaison, tk = d.demande.ticker;
    const w = (k.poids_apres[tk] || 0) * 100;
    const idF = (k.faits || {}).poids_apres;
    const val = `+ ${N.pct(w, 1)}`;
    const mots = ctx.n === 'essentiel' ? `${tk} : ${AF.fmt.cad(d.demande.montant_cad)} pris sur ton épargne` : `${tk} absent sans ; ${N.pct(w, 1)} avec · chaque autre ligne réduite d’autant`;
    return `<div class="cote" data-cle="repartition" data-sens="neutre">
      <span class="c-titre" aria-hidden="true">Part de la demande</span>
      <span class="c-bouts" aria-hidden="true"><span class="b-sans">sans : 0 ${esc(tk)}</span><span class="b-avec">avec ${esc(N.pct(w, 1))}</span></span>
      <span class="c-trait" aria-hidden="true" style="align-self:start;margin-top:28px"><i class="c-att"></i><i class="c-fl c-fl-g"></i><i class="c-ligne"></i><i class="c-fl c-fl-d"></i><i class="c-att"></i></span>
      ${preuve({ titre: `Part de ${tk} dans l’épargne avec ta demande`, faits: [idF], d, affiche: val }, esc(val), { cls: 'preuve c-val', label: `Part de la demande : ${val} de l’épargne en ${tk}. Ouvrir la fiche` })}
      <span class="c-mots">${esc(mots)}</span>
    </div>`;
  }

  function piedPanneau(bras, d, ctx) {
    const k = d.comparaison, f = k.faits || {}, fen = k.fenetre || {};
    if (bras === 'sans') {
      return `<div class="p-pied">${preuve({ titre: 'Fenêtre commune de comparaison', faits: [f.fenetre_portefeuille], d }, `mesuré du ${esc(fen.debut)} au ${esc(fen.fin)}${ctx.n === 'approfondi' ? ` · ${esc(fr(fen.observations))} observations` : ''}`)}</div>`;
    }
    return `<div class="p-pied">${preuve({ titre: 'Méthode commune aux deux vues', faits: [f.poids_apres, f.limites_portefeuille], d, note: `Politique du moteur ${k.moteur} (${k.version_moteur}) : ${k.politique}.` }, ctx.n === 'approfondi' ? esc(k.politique) : 'même méthode, achat-conservation')}</div>`;
  }

  function rendreVues(ctx) {
    const el = $('vues'); const d = ctx.d;
    let ms = d ? AF.mesures(d) : [];
    if (ctx.n === 'essentiel') ms = ms.filter((m) => m.cle !== 'rendement');
    const attente = demo === 'chargement' || demo === 'erreur';
    const mesure = d && d.comparaison && d.comparaison.disponible && !attente;
    const titre = '<h2 class="sr" id="vues-titre">Vues cotées : ton portefeuille sans et avec ta demande, mesurés de la même façon</h2>';
    if (!mesure) {
      el.style.gridTemplateRows = 'repeat(3, auto)';
      const msg = demo === 'chargement' ? 'Mesure en attente : le moteur historique n’a pas encore rendu les deux allocations.'
        : demo === 'erreur' ? 'Aucune mesure : l’analyse n’a pas abouti (démonstration).'
          : ctx.special === 'hors_univers' ? 'Rien à mesurer : la demande a été refusée avant l’analyse.'
            : `Comparaison non mesurée : ${String((d.comparaison && d.comparaison.raison) || (d.questions || [])[0] || 'information manquante').replace(/\.\s*$/, '')}.`;
      const zone = `<div class="non-mesure"><div class="zone-hachuree${demo === 'erreur' ? ' zone-erreur' : ''}"><span>${esc(msg)}</span></div></div>`;
      el.innerHTML = `${titre}<section class="panneau panneau-sans" aria-labelledby="vue-sans-titre">${tetePanneau('sans', ctx, d)}${zone}<div class="p-pied"></div></section>
        <div class="goutiere"><div class="g-tete"><span class="plaquette">Cotes</span></div><div class="cote-vide"></div><div></div></div>
        <section class="panneau panneau-avec" aria-labelledby="vue-avec-titre">${tetePanneau('avec', ctx, d)}${zone}<div class="p-pied"></div></section>`;
      return;
    }
    const ech = echelleCas(ctx.special ? 'robert' : ctx.e.cas);
    const reps = reperes(d);
    el.style.gridTemplateRows = `repeat(${3 + ms.length}, auto)`;
    const panneau = (bras) => `<section class="panneau panneau-${bras}" aria-labelledby="vue-${bras}-titre">
      ${tetePanneau(bras, ctx, d)}${repartition(bras, d, ctx, reps)}${ms.map((m) => ligneMesure(bras, m, ech, ctx, reps)).join('')}${piedPanneau(bras, d, ctx)}
    </section>`;
    const goutiere = `<div class="goutiere" role="group" aria-label="Cotes : ce que ta demande change">
      <div class="g-tete"><span class="plaquette">${esc(AF.terme('ecart').titre)}</span></div>
      ${coteRepartition(d, ctx)}${ms.map((m) => cote(m, ctx)).join('')}
      <div class="g-tete"><span class="plaquette">même fenêtre · même méthode</span></div>
    </div>`;
    el.innerHTML = titre + panneau('sans') + goutiere + panneau('avec');
  }

  /* ------------------------------------------------------------------ cartouche */
  function rendreVerdict(ctx) {
    const el = $('c-verdict');
    let etat = 'indetermine', html, cle;
    const bloc = (etq, st, long, court, regles, regCourt, stCourt, extra = '') => `<p class="v-etiquette"><span>${etq}</span><span>${esc(st)}</span></p>
      <div class="v-ligne">${symbole(etat)}<p class="v-libelle"><span class="v-long">${esc(long)}</span><span class="v-court">${esc(court)}</span><span class="v-regles-court">${esc(regCourt)}</span><span class="v-statut-court">${esc(stCourt)}</span></p></div>
      <p class="v-regles">${esc(regles)}</p>${extra}`;
    if (demo === 'chargement') {
      cle = 'demo-chargement';
      html = bloc('Verdict', 'démonstration', 'En attente du Gardien', 'En attente', 'Les règles n’ont pas encore été appliquées.', '', 'démo');
    } else if (demo === 'erreur') {
      cle = 'demo-erreur';
      html = bloc('Verdict', 'démonstration', 'Pas de verdict : l’analyse n’a pas abouti', 'Pas de verdict', 'Rien n’est deviné : reprends l’analyse.', '', 'erreur');
    } else if (ctx.special === 'hors_univers') {
      cle = 'hors-univers';
      html = bloc('Verdict', 'cas particulier', 'Aucun verdict : demande refusée avant l’analyse', 'Refusée', ctx.hu.message, '', 'hors univers');
    } else {
      const v = ctx.d.verdict; etat = v.etat;
      const st = ctx.special ? 'cas particulier' : ctx.st === 'archive' ? `révision ${indice(ctx.pos)} · archive` : ctx.st === 'apercu' ? `révision ${indice(ctx.pos)} · périmé` : `révision ${indice(ctx.pos)} · en vigueur`;
      const pl = (n, s) => `${n} ${s}${n > 1 ? 's' : ''}`;
      const regles = v.evaluees ? `${pl(v.respectees, 'règle')} respectée${v.respectees > 1 ? 's' : ''} sur ${v.evaluees}` : 'Aucune règle évaluée : il manque une information';
      const stCourt = ctx.st === 'apercu' ? 'périmé' : ctx.st === 'archive' ? `archive ${indice(ctx.pos)}` : ctx.special ? 'cas particulier' : '';
      cle = [etat, v.respectees, v.evaluees, st].join('|');
      html = bloc('Verdict', st, v.libelle, ETATS[etat].court, regles, `${v.respectees} sur ${v.evaluees}`, stCourt,
        ctx.st === 'apercu' ? `<p class="v-perime">Périmé : c’est le verdict de la révision ${indice(ctx.pos)}. Recalcule la planche.</p>` : '');
    }
    el.className = `c-verdict v-${etat}${ctx.st === 'apercu' ? ' perime' : ''}`;
    if (cle !== cleVerdict) { el.innerHTML = html; cleVerdict = cle; }
  }

  function groupeCases(nom, titre, valeurs, courant, lib, val, apercu) {
    if (valeurs.length < 2) return `<div class="c-param"><span class="c-l">${esc(titre)}</span><span class="c-fixe">${esc(lib(valeurs[0]))} · <span class="non-realise">seule valeur précalculée : non modifiable</span></span></div>`;
    return `<fieldset class="c-param"><legend>${esc(titre)}${apercu ? ' <span class="tag tag-perime">aperçu</span>' : ''}</legend><div class="cases">${valeurs.map((v) => `<label class="case${apercu ? ' apercu' : ''}"><input type="radio" name="${nom}" id="case-${nom}-${val(v)}" value="${val(v)}"${v === courant ? ' checked' : ''}>${esc(lib(v))}</label>`).join('')}</div></fieldset>`;
  }

  function parametres(ctx) {
    if (ctx.special) return '<div class="c-params"><p class="c-note">Cas particulier : aucun paramètre modifiable. Ses données viennent du moteur telles quelles.</p></div>';
    const p = AF.parametres(), base = ctx.b || ctx.e;
    const ap = (k) => !!ctx.b && ctx.b[k] !== ctx.e[k];
    const sect = secteurExclu(ctx.e.cas);
    return `<fieldset class="c-params"><legend>Paramètres · cotes éditables</legend>
      <div class="c-param"><span class="c-l">Montant</span><span class="c-fixe">${esc(AF.fmt.cad(base.montant))}${ap('montant') ? ' <span class="tag tag-perime">aperçu</span>' : ''} · <a href="#curseur-montant" data-action="aller-montant">cote sur la barre de répartition</a></span></div>
      ${groupeCases('retrait', 'Retrait prévu', p.retrait, base.retrait, (r) => AF.fmt.retrait(r), (r) => (r == null ? 'na' : String(r)), ap('retrait'))}
      ${groupeCases('exclusion', sect ? `Exclure le secteur ${sect}` : 'Exclusion de secteur', p.exclusion, base.exclusion, (x) => (x ? 'oui' : 'non'), (x) => (x ? '1' : '0'), ap('exclusion'))}
      <p class="c-note">Le reste du profil est en lecture seule dans ce prototype (notes P).</p>
    </fieldset>`;
  }

  function paireComparaison(ctx) {
    const n = ctx.hist.length;
    const pins = epingles.filter((i) => i < n).sort((x, y) => x - y);
    if (pins.length === 2) return pins;
    const p = ctx.pos, parent = ctx.hist[p] && ctx.hist[p].parent;
    const a = parent != null && parent >= 0 ? parent : Math.max(0, p - 1);
    if (a !== p) return [Math.min(a, p), Math.max(a, p)];
    return n > 1 ? [Math.max(0, n - 2), n - 1] : [0, 0];
  }

  function revisions(ctx) {
    if (ctx.special) return '';
    const h = ctx.hist, der = h.length - 1, appr = ctx.n === 'approfondi';
    const pins = epingles.filter((i) => i <= der);
    const [a, b] = paireComparaison(ctx);
    const lignes = h.slice().reverse().map((r) => `<tr>
      <th scope="row"><button type="button" class="ind" id="rev-${r.i}" data-action="relire" data-i="${r.i}"${r.courant ? ' aria-current="true"' : ''} aria-label="Révision ${indice(r.i)} : ${esc(r.motif)}. ${r.courant ? 'Affichée' : 'Relire'}">${indice(r.i)}</button></th>
      <td>${esc(r.motif)}${r.i === der ? ' <span class="rev-tag vigueur">en vigueur</span>' : ''}${r.courant && r.i !== der ? ' <span class="rev-tag">affichée</span>' : ''}${appr ? `<span class="rev-heure">${esc(heure(r.heure))} · ${esc(r.nom)}${r.parent != null && r.parent >= 0 ? ` · issue de ${indice(r.parent)}` : ''}</span>` : ''}</td>
      <td class="rev-v">${symbole(r.verdict)}${esc(ETATS[r.verdict].court)}</td>
      <td><input type="checkbox" class="pin" id="pin-${r.i}" data-pin="${r.i}"${pins.includes(r.i) ? ' checked' : ''} aria-label="Épingler la révision ${indice(r.i)} pour la comparer"></td>
    </tr>`).join('');
    const note = h.length < 2 ? 'Une seule révision : modifie une cote pour en créer une autre.'
      : pins.length === 2 ? 'Deux planches épinglées.' : 'Épingle deux révisions (⌖) pour choisir la paire ; sinon : la révision affichée et celle dont elle part.';
    return `<div class="c-revs">
      <div class="c-revs-tete"><span class="c-l">Révisions · un indice relit la révision</span></div>
      <div class="revs-defile"><table class="t-revs"><thead><tr><th scope="col">Ind.</th><th scope="col">Motif</th><th scope="col">Verdict</th><th scope="col"><span aria-hidden="true">⌖</span><span class="sr">Épingler</span></th></tr></thead><tbody>${lignes}</tbody></table></div>
      <div class="c-revs-actions"><button type="button" id="btn-comparer" data-action="comparer"${h.length < 2 ? ' disabled' : ''}>Planches à comparer : ${indice(a)} ↔ ${indice(b)}</button></div>
      <p class="c-note">${esc(note)}</p>
    </div>`;
  }

  function rendreCartouche(ctx) {
    const d = ctx.d;
    const date = AF.fmt.date(String(AF.meta.genere_le).slice(0, 10));
    const stLabel = { courante: 'En vigueur', archive: 'Archive', apercu: 'Aperçu périmé', special: 'Cas particulier' }[ctx.st];
    $('c-corps').innerHTML = `<div class="c-grille">
        <div class="c-cell l3"><span class="c-l">Second avis · Épure</span><span class="c-v grand">Planche ${ctx.special ? '—' : indice(ctx.pos)}</span></div>
        <div class="c-cell l3 fin"><span class="c-l">Situation</span><span class="c-v">${d ? `${esc(d.profil.nom)}, ${esc(d.profil.age)} ans` : '—'}</span></div>
        <div class="c-cell l6"><span class="c-l">Demande</span><span class="c-v">${d ? `« ${esc(d.demande.texte)} »` : esc(ctx.hu.message)}</span></div>
        <div class="c-cell l2"><span class="c-l">Date</span><span class="c-v">${esc(date)}</span></div>
        <div class="c-cell l2"><span class="c-l">Commit</span><span class="c-v"><code>${esc(AF.meta.commit)}</code></span></div>
        <div class="c-cell l2 fin"><span class="c-l">Statut</span><span class="c-v"><span class="statut-chip s-${ctx.st}">${esc(stLabel)}</span></span></div>
      </div>${parametres(ctx)}${revisions(ctx)}`;
  }

  function replier(ouvrir) {
    const c = $('cartouche');
    c.classList.toggle('ouvert', ouvrir);
    $('c-repli').setAttribute('aria-expanded', String(ouvrir));
  }

  /* ------------------------------------------------------------------ le rideau (coupe A-A) */
  function graduations(min, max, n) {
    if (max === min) { max += 1; min -= 1; }
    const pas = pasJoli((max - min) / n);
    const a = Math.floor(min / pas) * pas, b = Math.ceil(max / pas) * pas;
    const t = [];
    for (let v = a; v <= b + pas / 2; v += pas) t.push(+v.toFixed(6));
    return { a, b, t };
  }
  const tsDe = (s) => Date.parse(`${s}T00:00:00Z`);
  const ROMAINS = ['I', 'II', 'III', 'IV', 'V', 'VI'];
  const indexCreux = (arr) => arr.reduce((best, p, i) => (p[2] < arr[best][2] ? i : best), 0);

  function tableFenetres(ctx) {
    const d = ctx.d, s = d.series_portefeuille, k = d.comparaison;
    const av = s.avant_fenetres || [], ap = s.apres_fenetres || [];
    if (!av.length) return '';
    const appr = ctx.n === 'approfondi';
    const relies = [(k.faits || {}).fenetre_portefeuille, (k.faits || {}).limites_portefeuille].filter(Boolean);
    const cell = (f, cle, bras) => {
      const quoi = cle === 'pire_chute_pct' ? 'plus forte baisse' : 'rendement';
      return preuve({
        titre: `${f.nom} · ${quoi} ${bras === 'sans' ? 'sans' : 'avec'} ta demande`, d, faits: relies, affiche: N.pct(f[cle], 1),
        extra: [{ libelle: `${f.nom} : ${quoi}, ${bras === 'sans' ? 'sans' : 'avec'} ta demande`, valeur: f[cle], unite: '%', type: bras === 'sans' ? 'FAIT' : 'SCENARIO', lu_ou_calcule: 'calcule',
          source: `series_portefeuille.${bras === 'sans' ? 'avant' : 'apres'}_fenetres, moteur ${k.moteur} (${k.version_moteur})`,
          methode: `Fenêtre « ${f.nom} » du ${f.debut} au ${f.fin}, choisie à l’avance dans le code du moteur. ${k.politique}. Pas de fait F-n propre : voir la fenêtre commune et les limites ci-dessous.`, references: [] }],
      }, esc(N.pct(f[cle], 1)), { label: `${f.nom}, ${quoi} ${bras === 'sans' ? 'sans' : 'avec'} ta demande : ${N.pct(f[cle], 1)}. Ouvrir la fiche` });
    };
    const lignes = av.map((f, i) => {
      const g = ap[i] || f;
      return `<tr><th scope="row"><span class="tag">${ROMAINS[i] || i + 1}</span> ${esc(f.nom)}</th>
        <td data-l="Période">${esc(AF.fmt.date(f.debut))} → ${esc(AF.fmt.date(f.fin))}</td>
        <td data-l="Plus forte baisse, sans" class="num">${cell(f, 'pire_chute_pct', 'sans')}</td>
        <td data-l="Plus forte baisse, avec" class="num">${cell(g, 'pire_chute_pct', 'avec')}</td>
        ${appr ? `<td data-l="Rendement, sans" class="num">${cell(f, 'rendement_pct', 'sans')}</td><td data-l="Rendement, avec" class="num">${cell(g, 'rendement_pct', 'avec')}</td>` : ''}
        <td><button type="button" id="fen-${i}" data-action="fenetre" data-i="${i}">Voir sur la coupe</button></td></tr>`;
    }).join('');
    return `<h3 class="r-fenetres-titre">Fenêtres réelles nommées par le moteur</h3>
      <table class="t-pile t-fenetres"><caption>Mêmes dates pour les deux vues. Valeurs observées sur chaque fenêtre, rien au-delà du ${esc(AF.fmt.date(k.fenetre.fin))}.</caption>
      <thead><tr><th scope="col">Fenêtre</th><th scope="col">Période</th><th scope="col" class="num">Plus forte baisse · sans</th><th scope="col" class="num">· avec</th>${appr ? '<th scope="col" class="num">Rendement · sans</th><th scope="col" class="num">· avec</th>' : ''}<th scope="col"><span class="sr">Action</span></th></tr></thead>
      <tbody>${lignes}</tbody></table>`;
  }

  function rendreRideau(ctx) {
    const el = $('rideau'); const d = ctx.d;
    const s = d && d.series_portefeuille, k = d && d.comparaison;
    const appr = ctx.n === 'approfondi';
    const sous = !k || !k.disponible ? 'Les courbes réelles du portefeuille, sans et avec ta demande.'
      : `Les deux courbes réelles, superposées. Fais glisser le rideau : à sa gauche, l’épargne avec ta demande ; à sa droite, sans. Observé du ${k.fenetre.debut} au ${k.fenetre.fin}, aucun prolongement. Tracé : un point toutes les ${AF.meta.pas_series} séances, donc le creux dessiné peut être un peu moins profond que la pire baisse mesurée sur toutes les séances.${appr ? ` Moteur ${k.moteur} (${k.version_moteur}) : ${k.politique} ; ${fr(k.fenetre.observations)} observations, ${s ? s.avant.length : 0} points tracés.` : ''}`;
    const tete = `<header class="bloc-tete"><h2 id="rideau-titre"><span class="bloc-num">A–A</span>Coupe · le rideau</h2><p class="bloc-sous">${esc(sous)}</p></header>`;
    if (!s || !s.avant || !s.avant.length || demo === 'chargement' || demo === 'erreur') {
      const msg = demo === 'chargement' ? 'Coupe en attente : séries non encore rendues (démonstration).' : demo === 'erreur' ? 'Coupe indisponible : l’analyse n’a pas abouti (démonstration).' : 'Aucune série à tracer pour ce dossier : rien n’est dessiné, rien n’est prolongé.';
      el.innerHTML = `${tete}<div class="zone-hachuree${demo === 'erreur' ? ' zone-erreur' : ''}"><span>${esc(msg)}</span></div>`;
      geo = null;
      return;
    }
    const n = s.avant.length;
    const cleS = ctx.special || ctx.e.cas;
    if (rideau.cle !== cleS || rideau.idx == null || rideau.idx >= n) { rideau.idx = indexCreux(s.apres); rideau.cle = cleS; }
    const perime = ctx.st === 'apercu';
    const limite = ((d.texte && d.texte.limites) || [])[0];
    el.innerHTML = `${tete}
      <p class="r-legende"><span><i class="trait-ech avec" aria-hidden="true"></i>Avec ta demande${perime ? ' (tracé périmé)' : ''}</span><span><i class="trait-ech sans" aria-hidden="true"></i>Sans ta demande</span><span><i class="trait-ech fen" aria-hidden="true"></i>Fenêtres nommées (I, II, III)</span></p>
      <div class="r-graphe" id="r-graphe"></div>
      <div class="r-piste" id="r-piste"><label class="sr" for="rideau-curseur">Position du rideau sur l’axe du temps</label><input type="range" id="rideau-curseur" min="0" max="${n - 1}" step="1" value="${rideau.idx}"></div>
      <output class="r-lecture" id="rideau-lecture" for="rideau-curseur" aria-live="off"></output>
      ${tableFenetres(ctx)}
      ${limite ? `<p class="r-limite">${typeTag(limite.type)}${esc(propre(limite.texte))}</p>` : ''}`;
    dessinerGraphe(ctx);
  }

  function dessinerGraphe(ctx) {
    const box = $('r-graphe'); if (!box) return;
    const d = ctx.d, s = d.series_portefeuille, k = d.comparaison;
    const W = Math.max(280, Math.round(box.clientWidth || 800));
    const etroit = W < 560;
    const G = etroit ? 48 : 66, D = etroit ? 10 : 20, HT = 28, H1 = etroit ? 170 : 236, E = 30, H2 = etroit ? 92 : 120, B = 62;
    const H = HT + H1 + E + H2 + B;
    const top2 = HT + H1 + E, bas2 = top2 + H2;
    const t = s.avant.map((p) => tsDe(p[0]));
    const t0 = t[0], t1 = t[t.length - 1];
    const X = (ts) => G + ((ts - t0) / (t1 - t0)) * (W - G - D);
    const tous = s.avant.concat(s.apres);
    const gv = graduations(Math.min(...tous.map((p) => p[1])), Math.max(...tous.map((p) => p[1])), etroit ? 3 : 4);
    const Y1 = (v) => HT + H1 - ((v - gv.a) / (gv.b - gv.a)) * H1;
    const gb = graduations(Math.min(...tous.map((p) => p[2])), 0, H2 > 100 ? 3 : 2);
    if (gb.a === gb.b) gb.a = gb.b - 1;
    const Y2 = (b) => top2 + ((gb.b - b) / (gb.b - gb.a)) * H2;
    const chemin = (arr, Y, col) => arr.map((p, i) => `${i ? 'L' : 'M'}${X(t[i]).toFixed(1)} ${Y(p[col]).toFixed(1)}`).join('');
    const cs = [chemin(s.avant, Y1, 1), chemin(s.avant, Y2, 2)], ca = [chemin(s.apres, Y1, 1), chemin(s.apres, Y2, 2)];
    const per = ctx.st === 'apercu' ? ' perime' : '';

    let g = '';
    gv.t.forEach((v) => { const y = Y1(v).toFixed(1); g += `<line class="grille" x1="${G}" x2="${W - D}" y1="${y}" y2="${y}"/><text x="${G - 6}" y="${(+y + 4).toFixed(1)}" text-anchor="end">${esc(`${fr(v / 1000)} k$`)}</text>`; });
    gb.t.forEach((b) => { const y = Y2(b).toFixed(1); g += `<line class="grille" x1="${G}" x2="${W - D}" y1="${y}" y2="${y}"/><text x="${G - 6}" y="${(+y + 4).toFixed(1)}" text-anchor="end">${esc(N.pct(b, 0))}</text>`; });
    const a0 = new Date(t0).getUTCFullYear() + 1, a1 = new Date(t1).getUTCFullYear();
    for (let an = a0; an <= a1; an++) {
      const ts = Date.UTC(an, 0, 1); if (ts <= t0 || ts >= t1) continue;
      const x = X(ts).toFixed(1);
      g += `<line class="grille" x1="${x}" x2="${x}" y1="${HT}" y2="${bas2}"/><text x="${x}" y="${bas2 + 40}" text-anchor="middle">${an}</text>`;
    }
    const fens = s.avant_fenetres || [];
    const bandes = fens.map((f, i) => {
      const x1 = X(tsDe(f.debut)), w = Math.max(4, X(tsDe(f.fin)) - x1), cx = x1 + w / 2;
      return `<g class="fen" data-fen="${i}"><rect class="fen-bande" x="${x1.toFixed(1)}" y="${HT}" width="${w.toFixed(1)}" height="${H1}"/><rect class="fen-bande" x="${x1.toFixed(1)}" y="${top2}" width="${w.toFixed(1)}" height="${H2}"/>
        <rect class="plaque-svg" x="${(cx - 13).toFixed(1)}" y="${bas2 + 6}" width="26" height="18"/><text class="t-fen" x="${cx.toFixed(1)}" y="${bas2 + 19}" text-anchor="middle">${ROMAINS[i] || i + 1}</text></g>`;
    }).join('');
    const xf = X(t1);
    const aria = `Valeur et baisse de l’épargne, sans et avec ta demande, observées du ${k.fenetre.debut} au ${k.fenetre.fin}, sans prolongement. Le curseur sous le graphique déplace le rideau ; la lecture s’affiche en dessous.`;
    box.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${esc(aria)}">
      <defs>
        <pattern id="hach-fen" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="#7fa6cf" stroke-opacity=".45" stroke-width="1.2"/></pattern>
        <clipPath id="clip-g"><rect id="clip-g-r" x="0" y="0" width="${G}" height="${H}"/></clipPath>
        <clipPath id="clip-d"><rect id="clip-d-r" x="${G}" y="0" width="${W - G}" height="${H}"/></clipPath>
      </defs>
      <rect class="fond-plot" x="${G}" y="${HT}" width="${W - G - D}" height="${H1}"/>
      <rect class="fond-plot" x="${G}" y="${top2}" width="${W - G - D}" height="${H2}"/>
      ${bandes}${g}
      <g class="fantome"><path class="c-sans" d="${cs[0]}"/><path class="c-sans" d="${cs[1]}"/><path class="c-avec${per}" d="${ca[0]}"/><path class="c-avec${per}" d="${ca[1]}"/></g>
      <g clip-path="url(#clip-g)"><path class="c-avec${per}" d="${ca[0]}"/><path class="c-avec${per}" d="${ca[1]}"/></g>
      <g clip-path="url(#clip-d)"><path class="c-sans" d="${cs[0]}"/><path class="c-sans" d="${cs[1]}"/></g>
      <rect class="plaque-svg" x="${G + 1}" y="${HT + 1}" width="${etroit ? 92 : 112}" height="20"/><text class="t-fort" x="${G + 8}" y="${HT + 15}">Valeur ($ CA)</text>
      <text class="t-fort" x="${G}" y="${top2 - 9}">Baisse depuis le sommet</text>
      <line class="fin-l" x1="${xf.toFixed(1)}" x2="${xf.toFixed(1)}" y1="${HT - 6}" y2="${bas2 + 6}"/>
      <line class="axe" x1="${G}" x2="${G}" y1="${HT - 6}" y2="${bas2 + 6}"/>
      <text x="${G}" y="${H - 4}">${esc(AF.fmt.date(s.avant[0][0]))}</text>
      <text class="t-fort" x="${W - D}" y="${H - 4}" text-anchor="end">${esc(AF.fmt.date(s.avant[s.avant.length - 1][0]))} · fin de l’observation</text>
      <g id="rideau-g">
        <line class="rideau-l" id="rideau-l" x1="0" x2="0" y1="${HT - 4}" y2="${bas2 + 2}"/>
        <rect class="plaque-svg" id="rideau-pl-g" x="0" y="4" width="64" height="18"/><text class="t-avec" id="rideau-tx-g" x="0" y="17" text-anchor="end">◂ avec</text>
        <rect class="plaque-svg" id="rideau-pl-d" x="0" y="4" width="64" height="18"/><text class="t-sans" id="rideau-tx-d" x="0" y="17">sans ▸</text>
        <circle class="pt-avec" id="pt-av" r="5" cx="0" cy="0"/><circle class="pt-sans" id="pt-sv" r="4.5" cx="0" cy="0"/>
        <circle class="pt-avec" id="pt-ab" r="5" cx="0" cy="0"/><circle class="pt-sans" id="pt-sb" r="4.5" cx="0" cy="0"/>
        <rect class="rideau-poignee" id="rideau-p" x="0" y="${top2 - E + 4}" width="14" height="${E - 8}"/>
        <path class="rideau-grip" id="rideau-grip" d=""/>
      </g>
    </svg>`;
    geo = { W, H, G, D, HT, top2, bas2, E, X, Y1, Y2, t, n: t.length, s, fens };
    const input = $('rideau-curseur');
    if (input) {
      const tw = 18;
      input.style.marginLeft = `${G - tw / 2}px`;
      input.style.width = `calc(100% - ${G - tw / 2 + D - tw / 2}px)`;
    }
    brancherGraphe(box.querySelector('svg'));
    placerRideau(rideau.idx);
  }

  function idxPourX(x) {
    const { G, W, D, t } = geo;
    const ts = t[0] + ((x - G) / (W - G - D)) * (t[t.length - 1] - t[0]);
    let lo = 0, hi = t.length - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (t[mid] < ts) lo = mid; else hi = mid; }
    return Math.abs(t[lo] - ts) <= Math.abs(t[hi] - ts) ? lo : hi;
  }

  function placerRideau(idx) {
    if (!geo) return;
    const g = geo, s = g.s;
    idx = Math.max(0, Math.min(g.n - 1, Math.round(idx)));
    rideau.idx = idx;
    const x = g.X(g.t[idx]);
    const set = (id, attrs) => { const el = $(id); if (el) Object.entries(attrs).forEach(([a, v]) => el.setAttribute(a, typeof v === 'number' ? v.toFixed(1) : v)); };
    set('clip-g-r', { width: x });
    set('clip-d-r', { x, width: g.W - x });
    set('rideau-l', { x1: x, x2: x });
    const pa = s.apres[idx], ps = s.avant[idx];
    set('pt-av', { cx: x, cy: g.Y1(pa[1]) }); set('pt-sv', { cx: x, cy: g.Y1(ps[1]) });
    set('pt-ab', { cx: x, cy: g.Y2(pa[2]) }); set('pt-sb', { cx: x, cy: g.Y2(ps[2]) });
    set('rideau-p', { x: x - 7 });
    const ym = g.top2 - g.E / 2;
    set('rideau-grip', { d: `M${(x - 2.5).toFixed(1)} ${ym - 6} V${ym + 6} M${(x + 2.5).toFixed(1)} ${ym - 6} V${ym + 6}` });
    const xg = Math.max(x - 6, g.G + 58), xd = Math.min(x + 6, g.W - 64);
    set('rideau-tx-g', { x: xg }); set('rideau-pl-g', { x: xg - 60 });
    set('rideau-tx-d', { x: xd }); set('rideau-pl-d', { x: xd - 3 });
    const fen = g.fens.findIndex((f) => pa[0] >= f.debut && pa[0] <= f.fin);
    document.querySelectorAll('#r-graphe .fen').forEach((el) => el.querySelectorAll('.fen-bande').forEach((r) => r.classList.toggle('active', +el.dataset.fen === fen)));
    const date = AF.fmt.date(pa[0]);
    const dansFen = fen >= 0 ? ` · dans la fenêtre ${ROMAINS[fen]} « ${g.fens[fen].nom} »` : '';
    const out = $('rideau-lecture');
    if (out) out.innerHTML = `<b>Rideau au ${esc(date)}</b>${esc(dansFen)}<br><span class="l-avec">Avec ta demande</span> ${esc(N.cad(pa[1]))}, baisse depuis le sommet ${esc(N.pct(pa[2], 1))} · <span class="l-sans">Sans</span> ${esc(N.cad(ps[1]))}, baisse ${esc(N.pct(ps[2], 1))}`;
    const input = $('rideau-curseur');
    if (input) {
      if (+input.value !== idx) input.value = String(idx);
      input.setAttribute('aria-valuetext', `${date}${dansFen} : avec ta demande ${N.cad(pa[1])}, baisse ${N.pct(pa[2], 1)} ; sans, ${N.cad(ps[1])}, baisse ${N.pct(ps[2], 1)}`);
    }
  }

  /* Glisser sur le graphe : la souris agit tout de suite ; au doigt, seulement un geste horizontal (le défilement vertical reste libre). */
  function brancherGraphe(svg) {
    if (!svg) return;
    let actif = false, depart = null;
    const versIdx = (ev) => { const r = svg.getBoundingClientRect(); return idxPourX((ev.clientX - r.left) * (geo.W / r.width)); };
    svg.addEventListener('pointerdown', (ev) => {
      if (ev.button !== 0 || !geo) return;
      depart = { x: ev.clientX, y: ev.clientY, id: ev.pointerId };
      if (ev.pointerType === 'mouse') { actif = true; svg.setPointerCapture(ev.pointerId); placerRideau(versIdx(ev)); }
    });
    svg.addEventListener('pointermove', (ev) => {
      if (!geo || !depart) return;
      if (!actif) {
        const dx = Math.abs(ev.clientX - depart.x), dy = Math.abs(ev.clientY - depart.y);
        if (dx > 6 && dx > dy) { actif = true; try { svg.setPointerCapture(ev.pointerId); } catch (e) { /* sans effet */ } } else return;
      }
      placerRideau(versIdx(ev));
    });
    const fin = (ev) => {
      if (depart && !actif && ev.type === 'pointerup' && ev.pointerType !== 'mouse') placerRideau(versIdx(ev));
      actif = false; depart = null;
    };
    svg.addEventListener('pointerup', fin);
    svg.addEventListener('pointercancel', () => { actif = false; depart = null; });
  }

  /* ------------------------------------------------------------------ nomenclature (règles) */
  function rendreNomenclature(ctx) {
    const el = $('nomenclature'); const d = ctx.d;
    const appr = ctx.n === 'approfondi';
    const sous = d && d.verdict && d.verdict.evaluees ? `${d.verdict.respectees} respectée${d.verdict.respectees > 1 ? 's' : ''} sur ${d.verdict.evaluees}. Le Gardien (du code) les applique dans un ordre fixe et décide seul du verdict.` : 'Le Gardien (du code) applique les règles dans un ordre fixe et décide seul du verdict.';
    const tete = `<header class="bloc-tete"><h2 id="nomenclature-titre"><span class="bloc-num">N</span>Nomenclature des règles</h2><p class="bloc-sous">${esc(sous)}${appr ? ' Chaque règle renvoie aux faits qu’elle utilise.' : ''}</p></header>`;
    if (!d || demo === 'chargement' || demo === 'erreur') {
      const msg = !d ? 'Aucune règle appliquée : la demande a été refusée avant l’analyse.' : demo === 'chargement' ? 'Règles en attente du Gardien (démonstration).' : 'Règles non appliquées : l’analyse n’a pas abouti (démonstration).';
      el.innerHTML = `${tete}<div class="zone-hachuree"><span>${esc(msg)}</span></div>`;
      return;
    }
    const reps = new Map(reperes(d).map((r) => [r.code, r]));
    const lignes = d.regles.map((r, i) => {
      const et = NIV_ETAT[r.niveau] || 'indetermine';
      const montrer = appr || r.niveau !== 'ok';
      const faits = [...new Set(r.faits || [])];
      const rep = reps.get(r.code);
      const fiche = preuve({ titre: `Règle « ${r.libelle} »`, d, faits, regle: r }, `Fiche de la règle${faits.length ? ` · ${faits.length} fait${faits.length > 1 ? 's' : ''}` : ''}`, { label: `Fiche de la règle « ${r.libelle} » : texte exact, faits et références` });
      return `<tr id="regle-${r.code}" class="niv-${r.niveau}">
        <td data-l="Repère"><span class="rep-rond">${i + 1}</span></td>
        <th scope="row"><span class="n-lib">${esc(r.libelle)}</span>${montrer ? `<span class="n-expl">${esc(propre(r.explication))}</span>` : ''}${rep && demo === 'normal' || rep && demo === 'reprise' ? `<button type="button" class="n-repere" data-action="voir-repere" data-code="${r.code}">Repérée sur la planche : ${rep.cible === 'pire_chute' ? 'plus forte baisse' : 'barre de répartition'}</button>` : ''}</th>
        <td data-l="Niveau" class="n-niv">${symbole(et)}<span class="n-niv-l">${esc(AF.NIVEAUX_REGLE[r.niveau] || r.niveau)}</span>${appr && r.type ? `<br>${typeTag(r.type)}` : ''}</td>
        <td data-l="Renvois"><div class="renvois">${appr ? puces(faits, d) : ''}${fiche}</div></td>
      </tr>`;
    }).join('');
    el.innerHTML = `${tete}<table class="t-pile t-nomen"><thead><tr><th scope="col">Rep.</th><th scope="col">Règle</th><th scope="col">Niveau</th><th scope="col">Renvois aux faits</th></tr></thead><tbody>${lignes}</tbody></table>`;
  }

  /* ------------------------------------------------------------------ notes : le profil compris */
  function rendreNotes(ctx) {
    const el = $('notes'); const d = ctx.d; const appr = ctx.n === 'approfondi';
    const sous = ctx.special
      ? 'Lecture seule : cas particulier affiché tel que le moteur l’a rendu, aucune ligne n’est modifiable.'
      : 'Lecture seule. Se corrigent ici : le montant (cote sur la barre de répartition), le retrait et l’exclusion (cases du cartouche). Les autres lignes ne sont pas modifiables dans ce prototype.';
    const tete = `<header class="bloc-tete"><h2 id="notes-titre"><span class="bloc-num">P</span>Notes · ce que le produit a compris</h2><p class="bloc-sous">${esc(sous)}</p></header>`;
    if (!d) { el.innerHTML = `${tete}<p class="bloc-sous">Aucun dossier : la demande a été refusée avant l’analyse.</p>`; return; }
    const p = ctx.special ? null : AF.parametres();
    const reglable = { retrait: !!p && p.retrait.length > 1, exclusions: !!p && p.exclusion.length > 1 };
    const items = AF.profilLignes(d).map((l, i) => `<li class="${l.nature === 'inconnu' ? 'inconnu' : ''}">
        <span class="lp-num">${i + 1}</span>
        <span class="lp-lib">${esc(l.libelle)}${reglable[l.cle] ? ' · <span class="reglable">réglable : case du cartouche</span>' : ''}</span>
        <span class="lp-nat"><span class="nat nat-${l.nature}">${esc(NATURES[l.nature] || l.nature)}</span></span>
        <span class="lp-val">${l.nature === 'inconnu' ? 'Non fournie : jamais remplacée en silence' : esc(l.valeur)}</span>
        ${appr && l.note ? `<span class="lp-note">${esc(l.note)}</span>` : ''}
      </li>`).join('');
    const cit = (d.profil.citations || []).map((c) => `<p class="citation">« ${esc(c)} »</p>`).join('');
    const miroir = ((d.texte && d.texte.miroir) || []).map((ph) => `<p class="phrase">${typeTag(ph.type)}${esc(propre(ph.texte))} <span class="renvois" style="display:inline-flex">${puces(ph.faits, d)}</span></p>`).join('');
    const tensions = (d.profil.tensions || []).map((t) => `<li>${esc(t)}</li>`).join('');
    el.innerHTML = `${tete}<ol class="l-profil">${items}</ol>
      <div class="mots">
        ${cit ? `<h3>Tes mots</h3>${cit}` : ''}
        ${miroir ? `<h3>Ce que le produit te renvoie</h3>${miroir}` : ''}
        ${tensions ? `<h3>Tensions relevées</h3><ul class="phrase">${tensions}</ul>` : ''}
      </div>`;
  }

  /* ------------------------------------------------------------------ variantes, ce qui changerait l'avis */
  function rendreVariantes(ctx) {
    const el = $('variantes'); const d = ctx.d; const appr = ctx.n === 'approfondi';
    const tete = '<header class="bloc-tete"><h2 id="variantes-titre"><span class="bloc-num">V</span>Variantes · ce qui changerait l’avis</h2><p class="bloc-sous">Variantes étudiées par le moteur, dans l’ordre où il les rend : ce n’est pas un classement.</p></header>';
    if (!d) { el.innerHTML = `${tete}<p class="bloc-sous">Aucune variante : la demande a été refusée avant l’analyse.</p>`; return; }
    const cqc = (d.texte && d.texte.ce_qui_changerait) || [];
    const liste = cqc.length
      ? `<ul class="l-cqc">${cqc.map((ph) => `<li>${typeTag(ph.type)}${esc(propre(ph.texte))} ${puces(ph.faits, d)}</li>`).join('')}</ul>`
      : `<p class="bloc-sous" style="margin-bottom:12px">Le moteur ne propose aucun changement pour cette demande${d.verdict.etat === 'coherent' ? ' : elle est déjà cohérente avec ta situation' : ''}.</p>`;
    const p = ctx.special ? null : AF.parametres();
    const base = ctx.special ? null : ctx.b || ctx.e;
    const lignes = (d.options || []).map((o, i) => {
      const meme = o.ticker === d.demande.ticker;
      let action;
      if (i === 0) action = '<span class="non-realise">planche affichée</span>';
      else if (!ctx.special && meme && p.montant.includes(o.montant_cad) && o.montant_cad !== base.montant) action = `<button type="button" id="essai-${i}" data-action="proposer" data-patch="${esc(JSON.stringify({ montant: o.montant_cad }))}">Essayer cette cote</button>`;
      else if (meme) action = '<span class="non-realise">montant non précalculé : non réalisé dans ce prototype</span>';
      else action = '<span class="non-realise">autre placement : non réalisé dans ce prototype</span>';
      const et = ETATS[o.etat] ? o.etat : 'indetermine';
      const constat = o.constat || o.note;
      return `<tr><th scope="row">${esc(o.nom)}</th>
        <td data-l="Placement">${esc(o.ticker)}${o.libelle_actif && appr ? `<span class="op-detail">${esc(o.libelle_actif)}</span>` : ''}</td>
        <td data-l="Montant" class="num">${esc(AF.fmt.cad(o.montant_cad))}</td>
        <td data-l="Verdict du moteur">${symbole(et)}${esc(ETATS[et].court)}</td>
        <td data-l="Constat">${constat ? `<span class="op-detail" style="margin:0 0 6px">${esc(propre(constat))}</span>` : ''}<span class="renvois">${puces(o.faits, d)}${action}</span></td></tr>`;
    }).join('');
    el.innerHTML = `${tete}${liste}<table class="t-pile t-options"><thead><tr><th scope="col">Variante</th><th scope="col">Placement</th><th scope="col" class="num">Montant</th><th scope="col">Verdict</th><th scope="col">Constat</th></tr></thead><tbody>${lignes}</tbody></table>`;
  }

  /* ------------------------------------------------------------------ gamme d'opérations (travail des rôles) */
  function phaseOp(i) {
    if (!relecture) return '';
    const { i: k, phase } = relecture;
    if (phase === 'fin' || i < k || (i === k && phase === 'fait')) return 'fait';
    if (i === k && phase === 'en_cours') return 'en-cours';
    return 'attente';
  }
  const appelHtml = (a, exT, appr) => `<span class="appel"><span>étape ${esc(exT ? AF.fmt.ms(exT.duree_ms) : '—')} · appel ${esc(AF.fmt.ms(a.latence_ms))} · ${esc(fr(a.jetons_entree))} → ${esc(fr(a.jetons_sortie))} jetons</span><span class="mono">${esc(a.modele)}</span>${appr ? `<span class="mono">requête ${esc(a.request_id)}</span><span>garde-fou : ${esc(a.garde_fou)} · arrêt : ${esc(a.stop_reason || '—')}</span>` : ''}</span>`;

  function sousListe(t, d) {
    if (t.agent === 'Sceptique' && (d.objections || []).length) {
      return `<ol class="op-sous">${d.objections.map((o) => `<li>${esc(o.texte)} <em>(${esc(o.issue)})</em> ${esc(propre(o.reponse))} ${puces([o.cible], d)}</li>`).join('')}</ol>`;
    }
    if (t.agent === 'Contrôle données' && (d.qualite_donnees || []).length) {
      return `<ul class="op-sous">${d.qualite_donnees.map((q) => `<li>${q.statut === 'ok' ? 'réussi' : 'échec'} · ${esc(q.libelle)} : ${esc(q.detail)}</li>`).join('')}</ul>`;
    }
    if (t.agent === 'Analyste' && (t.faits || []).length) {
      return `<p class="op-sous">${t.faits.length} faits produits, de ${esc(t.faits[0])} à ${esc(t.faits[t.faits.length - 1])}, chacun avec sa source et sa méthode.</p>`;
    }
    if (t.agent === 'Rédacteur' && d.texte && (d.texte.controle || []).length) {
      return `<ul class="op-sous">${d.texte.controle.map((c) => `<li>contrôle : ${esc(c)}</li>`).join('')}</ul>`;
    }
    return '';
  }

  function rendreGamme(ctx) {
    const el = $('gamme'); const d = ctx.d; const appr = ctx.n === 'approfondi';
    const trace = (d && d.trace) || [];
    const tete = `<header class="bloc-tete"><h2 id="gamme-titre"><span class="bloc-num">G</span>Gamme d’opérations · le travail des rôles</h2>
      <p class="bloc-sous">Étapes réellement journalisées pour ce dossier. <strong>Code</strong> : contrôle des données, calcul (Analyste), décision (Gardien). <strong>Modèle</strong> : lecture de la phrase (Profileur), objections (Sceptique), rédaction (Rédacteur).</p>
      <div class="gamme-actions"><button type="button" id="btn-relecture" data-action="relecture"${trace.length ? '' : ' disabled'}>Relire les étapes enregistrées</button><span class="gamme-statut" id="gamme-statut" role="status">Relecture d’un journal : aucun agent ne travaille en direct.</span></div></header>`;
    if (!d) { el.innerHTML = `${tete}<p class="bloc-sous">Aucune étape : la demande a été refusée avant l’analyse (statut ${esc(ctx.hu.statut)}).</p>`; return; }
    const ex = ctx.special ? null : AF.execution();
    const horsLigne = !(d.appels_modele || []).length;
    const roles = (AF.donnees.sources && AF.donnees.sources.agents) || {};
    const lignes = trace.map((t, i) => {
      const code = CODE.has(t.agent);
      const exT = ex && (ex.trace || []).find((x) => x.agent === t.agent);
      const appels = ex ? (ex.appels_modele || []).filter((a) => a.agent === t.agent) : [];
      const reel = !ex ? '<span class="non-realise">aucune exécution réelle enregistrée pour ce dossier</span>'
        : appels.length ? appels.map((a) => appelHtml(a, exT, appr)).join('')
          : `<span class="appel"><span>étape ${esc(exT ? AF.fmt.ms(exT.duree_ms) : '—')}</span><span>code : aucun appel de modèle</span></span>`;
      const ph = phaseOp(i);
      return `<tr data-op="${i}" class="${ph ? `op-${ph}` : ''}">
        <th scope="row" class="op-num">${(i + 1) * 10}</th>
        <td data-l="Poste"><strong>${esc(t.agent)}</strong>${appr && roles[t.agent] ? `<span class="op-detail">${esc(roles[t.agent].role)}</span>` : ''}</td>
        <td data-l="Nature"><span class="nature nature-${code ? 'code' : 'modele'}">${code ? 'Code' : 'Modèle'}</span>${!code && horsLigne ? '<span class="op-detail">ce dossier : hors ligne, sans appel</span>' : ''}</td>
        <td data-l="Opération">${esc(t.action)}${appr ? `<span class="op-detail">${esc(propre(t.detail))}</span>${sousListe(t, d)}` : ''}</td>
        <td data-l="Durée, ce dossier" class="num">${esc(AF.fmt.ms(t.duree_ms))}<span class="op-etat">${ph ? LIB_PHASE[ph] : ''}</span></td>
        <td data-l="Exécution réelle enregistrée">${reel}</td>
      </tr>`;
    }).join('');
    let note = '';
    if (ex) {
      const dep = departDe(ctx.e.cas);
      note = estEtatDepart(ctx.e)
        ? `Colonne de droite : exécution Bedrock réellement enregistrée pour cette demande de départ (${ex.source}).`
        : `Colonne de droite : exécution Bedrock enregistrée pour la demande de départ de ${AF.nomCas(ctx.e.cas)} (${AF.fmt.cad(dep.montant)}, retrait ${AF.fmt.retrait(dep.retrait)}), pas pour cette révision ; source : ${ex.source}.`;
    }
    note += horsLigne ? ` Durées de ce dossier : ${AF.meta.mode}.` : '';
    el.innerHTML = `${tete}<table class="t-pile t-gamme"><thead><tr><th scope="col">Op.</th><th scope="col">Poste</th><th scope="col">Nature</th><th scope="col">Opération</th><th scope="col" class="num">Durée, ce dossier</th><th scope="col">Exécution réelle enregistrée</th></tr></thead><tbody>${lignes}</tbody></table><p class="gamme-note">${esc(note.trim())}</p>`;
  }

  function majGamme() {
    document.querySelectorAll('#gamme tr[data-op]').forEach((tr) => {
      const ph = phaseOp(+tr.dataset.op);
      tr.classList.remove('op-fait', 'op-en-cours', 'op-attente');
      if (ph) tr.classList.add(`op-${ph}`);
      const s = tr.querySelector('.op-etat'); if (s) s.textContent = ph ? LIB_PHASE[ph] : '';
    });
  }

  function arreterRelecture() { if (arretRelecture) { arretRelecture(); arretRelecture = null; } }

  function lancerRelecture(depuisDemo) {
    const ctx = contexte(); const d = ctx.d;
    if (!d || !(d.trace || []).length) return;
    arreterRelecture();
    relecture = { i: -1, phase: 'debut' };
    majGamme();
    const st = $('gamme-statut');
    if (st) st.textContent = 'Relecture des étapes enregistrées : début.';
    arretRelecture = AF.relireTrace(d, (i, phase) => {
      relecture = { i, phase };
      majGamme();
      const s = $('gamme-statut'), t = d.trace[i];
      if (s && phase === 'fait') s.textContent = `Opération ${(i + 1) * 10} rejouée : ${t.agent}, ${AF.fmt.ms(t.duree_ms)} enregistrées.`;
      if (phase === 'fin') {
        arretRelecture = null;
        if (s) s.textContent = 'Relecture terminée : les étapes enregistrées ont été rejouées dans leur ordre ; rien n’a été recalculé.';
        if (depuisDemo && demo === 'chargement') { demo = 'normal'; rendre(); annoncer('Chargement terminé (démonstration) : planche affichée.'); }
      }
    }, reduit.matches ? 25 : 1);
  }

  /* ------------------------------------------------------------------ limites */
  function rendreLimites(ctx) {
    const el = $('limites'); const d = ctx.d;
    if (!d) {
      el.innerHTML = '<header class="bloc-tete"><h2 id="limites-titre" class="bloc-titre"><span class="bloc-num">L</span>Limites</h2><p class="bloc-sous">Aucune mesure, donc aucune limite de mesure à signaler.</p></header>';
      return;
    }
    const vus = new Set(), items = [];
    ((d.texte && d.texte.limites) || []).forEach((l) => { if (!vus.has(l.texte)) { vus.add(l.texte); items.push(l); } });
    ((d.comparaison && d.comparaison.limites) || []).forEach((t) => { if (!vus.has(t)) { vus.add(t); items.push({ texte: t, type: null, faits: [] }); } });
    const ouvert = limitesOuvert != null ? limitesOuvert : ctx.n === 'approfondi';
    el.innerHTML = `<details class="d-limites" id="d-limites"${ouvert ? ' open' : ''}><summary><h2 id="limites-titre" class="bloc-titre"><span class="bloc-num">L</span>Limites du moteur (${items.length})</h2><span class="bloc-sous">${esc(items[0] ? propre(items[0].texte) : '')} ${ouvert ? '' : 'Ouvrir pour lire toutes les limites.'}</span></summary>
      <ol class="l-limites">${items.map((l) => `<li>${typeTag(l.type)}${esc(propre(l.texte))} <span class="renvois" style="display:inline-flex">${puces(l.faits, d)}</span></li>`).join('')}</ol></details>`;
  }

  /* ------------------------------------------------------------------ fiche de mesure (preuve) */
  function valeurExacte(v, unite) {
    const u = unite ? ` ${esc(unite)}` : '';
    if (v == null) return '<span class="f-exact">—</span>';
    if (Array.isArray(v)) return `<ol class="l-limites" style="margin-top:4px">${v.map((x) => `<li>${esc(x)}</li>`).join('')}</ol>`;
    if (typeof v === 'object') return `<dl class="f-obj">${Object.entries(v).map(([k, x]) => `<dt>${esc(k)}</dt><dd>${esc(exact(x))}${typeof x === 'number' ? u : ''}</dd>`).join('')}</dl>`;
    return `<span class="f-exact">${esc(exact(v))}${u}</span>`;
  }
  function refHtml(r) {
    const lien = r.lien && /^https?:\/\//.test(r.lien) ? `<a href="${esc(r.lien)}" target="_blank" rel="noopener noreferrer">${esc(r.lien)}</a>` : '<span class="r-lien">Pas de lien public : document ou donnée interne à l’équipe.</span>';
    return `<li><span class="r-titre">${esc(r.titre)}</span><span class="r-meta">${esc([r.auteurs, r.annee, r.publication].filter(Boolean).join(' · '))}${r.type ? ` · ${esc(r.type)}` : ''}</span>${lien}${r.examen ? `<span class="r-meta">Examen : ${esc(r.examen)}</span>` : ''}${r.apport ? `<span>${esc(r.apport)}</span>` : ''}</li>`;
  }
  const refsDe = (ids) => [...new Set(ids || [])].map((id) => AF.reference(id)).filter(Boolean);
  function blocFait(f) {
    const refs = refsDe(f.references);
    return `<article class="f-fait">
      <div class="f-entete">${f.id ? `<span class="f-id">${esc(f.id)}</span>` : '<span class="f-id">série</span>'}${typeTag(f.type)}<span class="f-lu">${f.lu_ou_calcule === 'lu' ? 'lu tel quel' : f.lu_ou_calcule === 'calcule' ? 'calculé par le code' : esc(f.lu_ou_calcule || '')}</span></div>
      <h3>${esc(f.libelle)}</h3>
      <div class="f-valeur"><span class="c-l">Valeur exacte</span>${valeurExacte(f.valeur, f.unite)}</div>
      <dl class="f-dl"><dt>Type</dt><dd>${esc(AF.TYPES[f.type] || f.type || '—')}</dd><dt>Source</dt><dd>${esc(f.source || '—')}</dd><dt>Méthode</dt><dd>${esc(f.methode || '—')}</dd></dl>
      <p class="f-refs-titre">Références (${refs.length})</p>
      ${refs.length ? `<ul class="f-refs">${refs.map(refHtml).join('')}</ul>` : '<p class="r-lien">Aucune référence n’est liée à cette valeur.</p>'}
    </article>`;
  }
  function blocRegle(r) {
    const refs = refsDe(r.references);
    return `<article class="f-fait">
      <div class="f-entete"><span class="f-id">${esc(r.code)}</span>${typeTag(r.type)}<span class="f-lu">${esc(AF.NIVEAUX_REGLE[r.niveau] || r.niveau)}</span></div>
      <h3>Règle « ${esc(r.libelle)} »</h3>
      <div class="f-valeur"><span class="c-l">Texte exact du moteur</span><p>${esc(r.explication)}</p></div>
      ${(r.faits || []).length ? '' : '<p class="r-lien">Le moteur ne lie aucun fait F-n à cette règle.</p>'}
      <p class="f-refs-titre">Références de la règle (${refs.length})</p>
      ${refs.length ? `<ul class="f-refs">${refs.map(refHtml).join('')}</ul>` : ''}
    </article>`;
  }
  function ouvrirFiche(desc, opener) {
    if (!desc) return;
    const d = desc.d;
    let h = '';
    if (desc.affiche) h += `<p class="f-note">Affiché sur la planche : <strong>${esc(desc.affiche)}</strong>. L’écran arrondit ; la valeur exacte est ci-dessous.</p>`;
    if (desc.note) h += `<p class="f-note">${esc(desc.note)}</p>`;
    if (desc.regle) h += blocRegle(desc.regle);
    (desc.extra || []).forEach((x) => { h += blocFait(x); });
    [...new Set((desc.faits || []).filter(Boolean))].forEach((id) => {
      const f = AF.fait(id, d);
      h += f ? blocFait(f) : `<p class="f-note">Fait ${esc(id)} absent de ce dossier.</p>`;
    });
    $('fiche-titre').textContent = desc.titre;
    $('fiche-corps').innerHTML = h;
    declencheur = opener || document.activeElement;
    const dlg = $('fiche');
    if (!dlg.open) dlg.showModal();
    dlg.scrollTop = 0;
  }

  /* ------------------------------------------------------------------ planches à comparer */
  const nivTexte = (n) => (n ? `${symbole(NIV_ETAT[n] || 'indetermine')} ${esc(AF.NIVEAUX_REGLE[n] || n)}` : '<span class="identique">absente de cette planche</span>');
  function sensCmp(m, ib) {
    if (m.avant == null || m.apres == null) return '—';
    if (m.apres === m.avant) return 'identique';
    if (m.cle === 'pire_chute') return m.apres < m.avant ? `plus profonde en ${ib}` : `moins profonde en ${ib}`;
    return m.apres > m.avant ? `plus élevée en ${ib}` : `plus basse en ${ib}`;
  }
  function ouvrirComparer(opener) {
    const ctx = contexte(); if (ctx.special || ctx.hist.length < 2) return;
    const [a, b] = paireComparaison(ctx);
    const opts = ctx.hist.map((r) => `<option value="${r.i}">Révision ${indice(r.i)} · ${esc(r.motif)}</option>`).join('');
    $('cmp-a').innerHTML = opts; $('cmp-b').innerHTML = opts;
    $('cmp-a').value = String(a); $('cmp-b').value = String(b);
    rendreComparaison();
    declencheur = opener;
    $('comparer').showModal();
  }
  function rendreComparaison() {
    const h = AF.historique(); const a = +$('cmp-a').value, b = +$('cmp-b').value;
    $('cmp-titre').textContent = `Révision ${indice(a)} ↔ révision ${indice(b)}`;
    if (a === b || !h[a] || !h[b]) { $('cmp-corps').innerHTML = '<p class="f-note">Choisis deux révisions différentes.</p>'; return; }
    const c = AF.comparer(h[a].etat, h[b].etat);
    const va = AF.dossierDe(h[a].etat).verdict, vb = AF.dossierDe(h[b].etat).verdict;
    const bloc = (i, v) => `<div class="cmp-v"><span class="c-l">Révision ${indice(i)} · ${esc(h[i].motif)}</span><div class="v-ligne">${symbole(v.etat)}<p class="v-libelle">${esc(v.libelle)}</p></div><p class="v-regles">${v.respectees} sur ${v.evaluees} règles respectées</p><button type="button" id="cmp-relire-${i}" data-action="relire" data-i="${i}">Relire la révision ${indice(i)}</button></div>`;
    const ia = indice(a), ib = indice(b);
    const regles = c.regles.map((r) => `<tr><th scope="row">${esc(r.libelle)}</th><td data-l="Révision ${ia}">${nivTexte(r.avant)}</td><td data-l="Cote">${r.change ? '<span class="change">changée</span>' : '<span class="identique">identique</span>'}</td><td data-l="Révision ${ib}">${nivTexte(r.apres)}</td></tr>`).join('');
    const mesures = c.mesures.map((m) => `<tr><th scope="row">${esc(m.titre)}</th><td data-l="Révision ${ia}" class="num">${esc(valeurMesure(m, m.avant))}</td><td data-l="Cote">${esc(sensCmp(m, ib))}</td><td data-l="Révision ${ib}" class="num">${esc(valeurMesure(m, m.apres))}</td></tr>`).join('');
    $('cmp-corps').innerHTML = `<p class="f-note">Ce qui diffère entre les deux planches : ${esc(c.motif)}.</p>
      <div class="cmp-verdicts">${bloc(a, va)}<div class="cmp-cote"><span class="${c.verdict.change ? 'change' : 'identique'}">${c.verdict.change ? 'verdict changé' : 'verdict identique'}</span></div>${bloc(b, vb)}</div>
      <table class="t-pile"><caption>Règles, révision ${ia} ↔ révision ${ib}</caption><thead><tr><th scope="col">Règle</th><th scope="col">${ia}</th><th scope="col">Cote</th><th scope="col">${ib}</th></tr></thead><tbody>${regles}</tbody></table>
      ${mesures ? `<table class="t-pile"><caption>Mesures du portefeuille avec la demande, révision ${ia} ↔ révision ${ib} (même fenêtre, même méthode)</caption><thead><tr><th scope="col">Mesure</th><th scope="col" class="num">${ia}</th><th scope="col">Cote</th><th scope="col" class="num">${ib}</th></tr></thead><tbody>${mesures}</tbody></table>` : ''}`;
  }

  /* ------------------------------------------------------------------ démonstration */
  function setDemo(v) {
    arreterRelecture();
    relecture = null;
    demo = v;
    rendre();
    if (v === 'chargement') lancerRelecture(true);
    annoncer({ normal: 'Démonstration terminée : planche normale.', chargement: 'Démonstration : chargement, relecture des étapes enregistrées.', erreur: 'Démonstration : erreur, aucun verdict affiché.', reprise: 'Démonstration : reprise depuis la dernière révision enregistrée.' }[v] || '');
  }

  /* ------------------------------------------------------------------ événements */
  const quitterSpecial = () => { special = null; };

  document.addEventListener('click', (ev) => {
    document.querySelectorAll('details.menu[open]').forEach((m) => { if (!m.contains(ev.target)) m.open = false; });
    const el = ev.target.closest('[data-action]');
    if (!el || el.disabled) return;
    const a = el.dataset.action;
    const dlg = el.closest('dialog');
    switch (a) {
      case 'fiche': ouvrirFiche(fiches.get(el.dataset.fiche), el); break;
      case 'fermer': if (dlg && dlg.open) dlg.close(); break;
      case 'cas': {
        const c = el.dataset.cas; const etait = special; quitterSpecial();
        if (c !== AF.etat().cas) AF.changerCas(c); else if (etait) planifier();
        break;
      }
      case 'special': special = el.dataset.cle; $('menu-speciaux').open = false; focusApres = 'tete-titre'; planifier(); break;
      case 'quitter-special': quitterSpecial(); focusApres = 'tete-titre'; planifier(); break;
      case 'niveau': limitesOuvert = null; AF.definirNiveau(el.dataset.n); break;
      case 'niveau-bascule': limitesOuvert = null; AF.definirNiveau(AF.niveau() === 'approfondi' ? 'essentiel' : 'approfondi'); break;
      case 'annuler': quitterSpecial(); if (!AF.annuler()) planifier(); break;
      case 'refaire': quitterSpecial(); if (!AF.retablir()) planifier(); break;
      case 'relire': {
        if (dlg && dlg.open) { declencheur = null; dlg.close(); }
        quitterSpecial(); const i = +el.dataset.i;
        focusApres = $('cartouche').offsetParent !== null && getComputedStyle($('c-corps')).display !== 'none' ? `rev-${i}` : 'tete-titre';
        if (!AF.allerA(i)) planifier();
        break;
      }
      case 'restaurer': focusApres = 'tete-titre'; AF.restaurer(+el.dataset.i); break;
      case 'vigueur': focusApres = 'tete-titre'; AF.allerA(AF.historique().length - 1); break;
      case 'appliquer': focusApres = 'tete-titre'; AF.appliquer(); break;
      case 'abandonner': focusApres = 'tete-titre'; AF.abandonner(); break;
      case 'proposer': {
        quitterSpecial();
        let patch = null; try { patch = JSON.parse(el.dataset.patch); } catch (e) { patch = null; }
        if (patch) { focusApres = 'btn-appliquer'; if (!AF.proposer(patch)) { focusApres = null; annoncer('Cette valeur n’est pas précalculée.'); } }
        break;
      }
      case 'comparer': ouvrirComparer(el); break;
      case 'repere': {
        const tr = $(`regle-${el.dataset.code}`); if (!tr) break;
        tr.scrollIntoView({ block: 'center', behavior: reduit.matches ? 'auto' : 'smooth' });
        tr.classList.remove('eclair'); void tr.offsetWidth; tr.classList.add('eclair');
        const th = tr.querySelector('th'); th.setAttribute('tabindex', '-1'); th.focus({ preventScroll: true });
        break;
      }
      case 'voir-repere': {
        const b = $(`bulle-${el.dataset.code}`); if (!b) break;
        b.scrollIntoView({ block: 'center', behavior: reduit.matches ? 'auto' : 'smooth' }); b.focus({ preventScroll: true });
        break;
      }
      case 'relecture': lancerRelecture(false); break;
      case 'fenetre': {
        if (!geo) break;
        const f = geo.fens[+el.dataset.i]; if (!f) break;
        /* Dernier point observé à l'intérieur de la fenêtre : la fenêtre entière passe du côté « avec ». */
        let j = geo.n - 1; while (j > 0 && geo.t[j] > tsDe(f.fin)) j--;
        placerRideau(j);
        $('r-graphe').scrollIntoView({ block: 'center', behavior: reduit.matches ? 'auto' : 'smooth' });
        const r = $('rideau-curseur'); if (r) r.focus({ preventScroll: true });
        break;
      }
      case 'repli': replier(!$('cartouche').classList.contains('ouvert')); break;
      case 'aller-montant': {
        ev.preventDefault(); replier(false);
        const c = $('curseur-montant');
        if (c) { c.scrollIntoView({ block: 'center', behavior: reduit.matches ? 'auto' : 'smooth' }); c.focus({ preventScroll: true }); }
        break;
      }
      case 'demo-fin': setDemo('normal'); break;
      case 'demo-reprendre': setDemo('reprise'); break;
      default: break;
    }
  });

  document.addEventListener('input', (ev) => {
    const t = ev.target;
    if (t.id === 'curseur-montant') {
      const v = +t.dataset.vals.split(',')[+t.value];
      const o = $('sortie-montant'); if (o) { o.textContent = `${AF.fmt.cad(v)} · aperçu au lâcher`; o.classList.add('apercu'); }
      t.setAttribute('aria-valuetext', AF.fmt.cad(v));
    } else if (t.id === 'rideau-curseur') placerRideau(+t.value);
  });

  document.addEventListener('change', (ev) => {
    const t = ev.target;
    if (t.id === 'curseur-montant') {
      const v = +t.dataset.vals.split(',')[+t.value];
      quitterSpecial(); if (!AF.proposer({ montant: v })) planifier();
    } else if (t.name === 'retrait') AF.proposer({ retrait: t.value === 'na' ? null : +t.value });
    else if (t.name === 'exclusion') AF.proposer({ exclusion: t.value === '1' });
    else if (t.dataset && t.dataset.pin != null) {
      const i = +t.dataset.pin;
      epingles = epingles.filter((x) => x !== i);
      if (t.checked) { epingles.push(i); if (epingles.length > 2) epingles.shift(); }
      planifier();
    } else if (t.id === 'choix-demo') setDemo(t.value);
    else if (t.id === 'cmp-a' || t.id === 'cmp-b') rendreComparaison();
  });

  document.addEventListener('toggle', (ev) => { if (ev.target && ev.target.id === 'd-limites') limitesOuvert = ev.target.open; }, true);

  document.addEventListener('keydown', (ev) => {
    if (ev.key !== 'Escape') return;
    const m = document.querySelector('details.menu[open]');
    if (m) { m.open = false; m.querySelector('summary').focus(); return; }
    if ($('cartouche').classList.contains('ouvert')) { replier(false); $('c-repli').focus(); }
  });

  ['fiche', 'comparer'].forEach((id) => {
    const dlg = $(id);
    dlg.addEventListener('close', () => { if (declencheur && document.contains(declencheur)) declencheur.focus(); declencheur = null; });
    dlg.addEventListener('click', (ev) => { if (ev.target === dlg) dlg.close(); });
  });

  /* Le graphe suit la largeur de la planche (texte jamais étiré). */
  let largeur = 0, minuterie = null;
  if (window.ResizeObserver) {
    new ResizeObserver(() => {
      const w = $('rideau').clientWidth;
      if (Math.abs(w - largeur) < 2) return;
      largeur = w;
      clearTimeout(minuterie);
      minuterie = setTimeout(() => { if (geo) dessinerGraphe(contexte()); }, 60);
    }).observe($('rideau'));
  }

  AF.abonner(() => {
    arreterRelecture();
    relecture = null;
    if (demo === 'chargement') demo = 'normal';
    planifier();
  });

  rendre();
})();
