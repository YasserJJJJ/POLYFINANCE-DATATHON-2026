/* Socle commun des cinq prototypes ui-adam.
   Il ne calcule aucun chiffre financier : il lit les dossiers précalculés par le moteur réel (fixtures.js),
   tient l'état partagé (cas, paramètres, niveau de lecture), l'historique des révisions et les formats.
   Les cinq prototypes lisent les mêmes faits ; seule leur présentation diffère. */
window.AF = (() => {
  const F = window.AF_FIXTURES;
  const STOCK = 'af-ui-adam-v1';
  const ETATS = {
    coherent: { court: 'Cohérent', long: 'Cohérent avec ta situation', rang: 0 },
    ajustement: { court: 'Ajustement', long: 'Cohérent avec un ajustement', rang: 1 },
    incoherent: { court: 'Incohérent', long: 'Incohérent avec ta situation', rang: 2 },
    indetermine: { court: 'Indéterminé', long: 'Impossible de conclure : il manque une information', rang: 3 },
  };
  const NIVEAUX_REGLE = { ok: 'Respectée', orange: 'À ajuster', rouge: 'Bloquante', gris: 'Information manquante', non_evaluee: 'Non évaluée' };
  const TYPES = { FAIT: 'Fait observé', HYPOTHESE: "Hypothèse de l'équipe", SCENARIO: 'Scénario fictif' };

  /* Vocabulaire des deux profondeurs de lecture. Les faits et les limites sont les mêmes ; seuls les mots changent. */
  const LEXIQUE = {
    pire_chute: { essentiel: 'Plus forte baisse déjà vue', approfondi: 'Pire baisse (drawdown maximal)', def: "La plus grande baisse entre un sommet et le creux qui a suivi, sur la période étudiée. Ce n'est pas une limite pour l'avenir." },
    volatilite: { essentiel: "Ampleur des variations d'une année", approfondi: 'Volatilité annualisée', def: "À quel point la valeur bouge d'un jour à l'autre, ramené à une année." },
    ecart: { essentiel: 'Ce que ta demande change', approfondi: 'Écart apparié, après moins avant', def: 'Différence entre le portefeuille avec la demande et sans, mesurés de la même façon sur la même période.' },
    capacite: { essentiel: 'Ce que ta situation permet de perdre', approfondi: 'Capacité de perte', def: "Baisse du portefeuille que ta situation permet d'absorber, selon un barème de l'équipe." },
    tolerance: { essentiel: "Ce que tu dis vouloir risquer", approfondi: 'Tolérance au risque', def: "Baisse que tu acceptes, d'après tes réponses." },
    concentration: { essentiel: "Part de ton épargne dans ce seul placement", approfondi: 'Concentration', def: "Poids d'un seul placement dans l'épargne totale, comparé à un seuil de l'équipe." },
    rendement: { essentiel: 'Progression moyenne par an sur la période', approfondi: 'Rendement annualisé (TCAC)', def: 'Progression annuelle moyenne observée sur la période. Elle ne dit rien des années à venir.' },
    valeur_finale: { essentiel: 'Valeur en fin de période', approfondi: 'Valeur finale simulée', def: "Valeur qu'aurait eue l'épargne à la fin de la période, en achat-conservation." },
  };

  const lire = () => { try { return JSON.parse(localStorage.getItem(STOCK)) || null; } catch (e) { return null; } };
  const ecrire = () => { try { localStorage.setItem(STOCK, JSON.stringify({ revs, pos, niveau })); } catch (e) { /* stockage indisponible : l'état reste en mémoire */ } };

  const cleDe = (e) => `m=${e.montant};r=${e.retrait == null ? 'na' : e.retrait};x=${e.exclusion ? 1 : 0}`;
  const lireCle = (k) => { const o = Object.fromEntries(k.split(';').map((p) => p.split('='))); return { montant: +o.m, retrait: o.r === 'na' ? null : +o.r, exclusion: o.x === '1' }; };
  const departDe = (cas) => ({ cas, ...lireCle(F.cas[cas].depart) });
  const valide = (e) => e && F.cas[e.cas] && F.cas[e.cas].variantes[cleDe(e)];
  const memes = (a, b) => a.cas === b.cas && cleDe(a) === cleDe(b);

  /* Révisions : liste qui ne perd rien. Chaque révision connaît celle dont elle part. */
  let revs = [], pos = -1, niveau = 'essentiel', brouillon = null, refaire = [];
  const abonnes = new Set();
  const publier = () => { ecrire(); majHash(); abonnes.forEach((f) => f()); };
  const ajouter = (e, motif) => { revs.push({ etat: { cas: e.cas, montant: e.montant, retrait: e.retrait, exclusion: e.exclusion }, parent: pos, motif, heure: Date.now() }); pos = revs.length - 1; refaire = []; };

  function majHash() {
    const e = etat();
    const h = `#cas=${e.cas}&${cleDe(e).replace(/;/g, '&')}&n=${niveau}`;
    try { history.replaceState(null, '', location.pathname + location.search + h); } catch (err) { /* fichier local : sans effet */ }
  }
  function lireHash() {
    const o = Object.fromEntries(location.hash.replace(/^#/, '').split('&').filter(Boolean).map((p) => p.split('=')));
    if (!o.cas) return null;
    return { etat: { cas: o.cas, montant: +o.m, retrait: o.r === 'na' || o.r == null ? null : +o.r, exclusion: o.x === '1' }, niveau: o.n };
  }

  (function demarrer() {
    const s = lire();
    if (s && Array.isArray(s.revs) && s.revs.length && s.revs.every((r) => valide(r.etat))) { revs = s.revs; pos = Math.min(Math.max(s.pos, 0), revs.length - 1); niveau = s.niveau === 'approfondi' ? 'approfondi' : 'essentiel'; }
    const h = lireHash();
    if (h && h.niveau) niveau = h.niveau === 'approfondi' ? 'approfondi' : 'essentiel';
    if (h && valide(h.etat) && (pos < 0 || !memes(h.etat, revs[pos].etat))) ajouter(h.etat, 'Ouvert depuis un lien');
    if (pos < 0) ajouter(departDe('robert'), 'Demande de départ');
    ecrire();
  })();

  const etat = () => ({ ...revs[pos].etat, niveau });
  const dossierDe = (e) => F.cas[e.cas].variantes[cleDe(e)];
  const dossier = () => dossierDe(revs[pos].etat);

  /* Statut de ce qui est affiché : analyse courante, archive relue, ou aperçu non encore analysé. */
  const statut = () => (brouillon ? 'apercu' : pos === revs.length - 1 ? 'courante' : 'archive');

  function proposer(patch) {
    const base = brouillon || revs[pos].etat;
    const e = { ...base, ...patch };
    if (!valide(e)) return false;
    brouillon = memes(e, revs[pos].etat) ? null : e;
    abonnes.forEach((f) => f());
    return true;
  }
  function appliquer(motif) {
    if (!brouillon) return false;
    const e = brouillon; brouillon = null;
    ajouter(e, motif || decrire(revs[pos].etat, e));
    publier();
    return true;
  }
  const abandonner = () => { brouillon = null; abonnes.forEach((f) => f()); };
  const changer = (patch, motif) => proposer(patch) && appliquer(motif);
  const changerCas = (cas) => { brouillon = null; if (cas === revs[pos].etat.cas) return; ajouter(departDe(cas), `Autre situation : ${nomCas(cas)}`); publier(); };
  function annuler() { const p = revs[pos].parent; if (p == null || p < 0) return false; refaire.push(pos); pos = p; brouillon = null; publier(); return true; }
  function retablir() { if (!refaire.length) return false; pos = refaire.pop(); brouillon = null; publier(); return true; }
  function allerA(i) { if (i < 0 || i >= revs.length || i === pos) return false; refaire = []; pos = i; brouillon = null; publier(); return true; }
  /* Restaurer n'efface rien : une nouvelle révision reprend l'état choisi. */
  function restaurer(i) { if (i < 0 || i >= revs.length) return false; brouillon = null; pos = revs.length - 1; ajouter(revs[i].etat, `Retour à la révision ${i + 1}`); publier(); return true; }
  function reinitialiser() { revs = []; pos = -1; brouillon = null; refaire = []; ajouter(departDe('robert'), 'Demande de départ'); publier(); }
  const definirNiveau = (n) => { niveau = n === 'approfondi' ? 'approfondi' : 'essentiel'; publier(); };

  const nomCas = (cas) => F.cas[cas].variantes[F.cas[cas].depart].profil.nom;
  function decrire(a, b) {
    const m = [];
    if (a.cas !== b.cas) m.push(`Situation : ${nomCas(b.cas)}`);
    if (a.montant !== b.montant) m.push(`Montant : ${fmt.cad(a.montant)} → ${fmt.cad(b.montant)}`);
    if (a.retrait !== b.retrait) m.push(`Retrait prévu : ${fmt.retrait(a.retrait)} → ${fmt.retrait(b.retrait)}`);
    if (a.exclusion !== b.exclusion) m.push(`Exclusion de secteur : ${b.exclusion ? 'rétablie' : 'retirée'}`);
    return m.join(' · ') || 'Sans changement';
  }

  const fr = (n, d = 0) => (n == null || isNaN(n) ? '—' : Number(n).toLocaleString('fr-CA', { minimumFractionDigits: d, maximumFractionDigits: d }));
  const fmt = {
    nombre: fr,
    cad: (n) => (n == null ? '—' : `${fr(n)} $`),
    pct: (n, d = 1) => (n == null ? '—' : `${fr(n, d)} %`),
    pts: (n, d = 1) => (n == null ? '—' : `${n > 0 ? '+' : ''}${fr(n, d)} pt${Math.abs(n) >= 2 ? 's' : ''}`),
    retrait: (r) => (r == null ? 'non précisé' : `dans ${r} an${r > 1 ? 's' : ''}`),
    date: (s) => { const d = new Date(s + 'T00:00:00'); return isNaN(d) ? s : d.toLocaleDateString('fr-CA', { year: 'numeric', month: 'short', day: 'numeric' }); },
    ms: (n) => (n >= 1000 ? `${fr(n / 1000, 1)} s` : `${fr(n)} ms`),
  };
  /* Affichage : le gabarit du produit écrit les mesures avec six décimales. On arrondit à l'écran ; la valeur exacte reste dans le fait. */
  const propre = (t) => String(t || '').replace(/(-?\d+),(\d{3,})/g, (m, a, b) => fr(parseFloat(`${a}.${b}`), 1)).replace(/\s+$/, '');

  const fait = (id, d = dossier()) => (d.faits || []).find((f) => f.id === id) || null;
  const reference = (id) => (F.sources.references[id] ? { id, ...F.sources.references[id] } : null);
  const terme = (cle, n = niveau) => ({ titre: LEXIQUE[cle] ? LEXIQUE[cle][n] : cle, def: LEXIQUE[cle] ? LEXIQUE[cle].def : '' });

  /* Mesures appariées avant/après, telles que rendues par le moteur (K3). */
  function mesures(d = dossier()) {
    const k = d.comparaison;
    if (!k || !k.disponible) return [];
    const ligne = (cle, champ, unite, ecart) => ({ cle, ...terme(cle), unite, avant: k.avant[champ], apres: k.apres[champ], ecart: ecart != null ? ecart : k.apres[champ] - k.avant[champ] });
    return [
      { ...ligne('pire_chute', 'pire_chute_pct', '%', k.ecarts.pire_chute_pts), sens: k.ecarts.sens_pire_chute, fait: (k.faits || {}) },
      ligne('volatilite', 'volatilite_pct', '%', k.ecarts.volatilite_pts),
      ligne('rendement', 'rendement_annualise_pct', '%'),
      ligne('valeur_finale', 'valeur_finale_cad', '$'),
    ];
  }

  /* Ce que l'on sait de la personne, avec la nature de chaque ligne : donnée, préférence, contrainte ou inconnue. */
  function profilLignes(d = dossier()) {
    const p = d.profil, ev = p.evaluation || {};
    const L = (cle, libelle, valeur, nature, note) => ({ cle, libelle, valeur, nature: valeur == null || valeur === '' ? 'inconnu' : nature, note });
    const poids = p.portefeuille_actuel && !Array.isArray(p.portefeuille_actuel) ? Object.entries(p.portefeuille_actuel).map(([t, w]) => `${t} ${fr(w * 100)} %`).join(', ') : (p.portefeuille_actuel || []).join(', ');
    return [
      L('epargne', 'Épargne totale', p.epargne_totale_cad == null ? null : fmt.cad(p.epargne_totale_cad), 'donnee', 'Montant fictif du scénario'),
      L('horizon', 'Horizon du placement', p.horizon_ans == null ? null : `${p.horizon_ans} ans`, 'donnee'),
      L('retrait', 'Retrait prévu', p.retrait_prevu_ans == null ? null : fmt.retrait(p.retrait_prevu_ans), 'contrainte', 'Une date de retrait change la règle de concentration'),
      L('preserver', 'Somme à ne jamais risquer', p.somme_a_preserver_cad == null ? null : fmt.cad(p.somme_a_preserver_cad), 'contrainte'),
      L('tolerance', 'Ce que tu dis vouloir risquer', ev.tolerance == null ? null : `${fr(ev.tolerance)} / 100`, 'preference'),
      L('capacite', 'Ce que ta situation permet', ev.capacite == null ? null : `${fr(ev.capacite)} / 100`, 'donnee', (ev.capacite_raisons || []).join(' ; ')),
      L('exclusions', 'Secteurs exclus', (p.exclusions || []).length ? p.exclusions.join(', ') : 'Aucun', 'preference'),
      L('portefeuille', 'Placements actuels', poids || null, 'donnee', 'Poids fictifs validés par le porteur'),
      L('urgence', "Fonds d'urgence", p.fonds_urgence == null ? null : p.fonds_urgence ? 'Oui' : 'Non', 'donnee'),
    ];
  }

  /* Différence entre deux états : ce qui change, règle par règle et mesure par mesure. */
  function comparer(a, b) {
    const da = dossierDe(a), db = dossierDe(b), ma = mesures(da), mb = mesures(db);
    const codes = [...new Set([...da.regles, ...db.regles].map((r) => r.code))];
    return {
      motif: decrire(a, b),
      verdict: { avant: da.verdict.etat, apres: db.verdict.etat, change: da.verdict.etat !== db.verdict.etat },
      regles: codes.map((c) => { const x = da.regles.find((r) => r.code === c), y = db.regles.find((r) => r.code === c); return { code: c, libelle: (y || x).libelle, avant: x ? x.niveau : null, apres: y ? y.niveau : null, change: (x && x.niveau) !== (y && y.niveau) }; }),
      mesures: mb.map((m) => { const x = ma.find((q) => q.cle === m.cle); return { cle: m.cle, titre: m.titre, unite: m.unite, avant: x ? x.apres : null, apres: m.apres }; }),
    };
  }

  const historique = () => revs.map((r, i) => ({ i, etat: r.etat, parent: r.parent, motif: r.motif, heure: r.heure, verdict: dossierDe(r.etat).verdict.etat, courant: i === pos, nom: nomCas(r.etat.cas) }));

  /* Relit les étapes réellement enregistrées (durées mesurées), sans prétendre qu'un agent travaille en direct. */
  function relireTrace(d, surEtape, vitesse = 1) {
    let annule = false; const etapes = d.trace || [];
    (async () => { for (let i = 0; i < etapes.length && !annule; i++) { surEtape(i, 'en_cours'); await new Promise((r) => setTimeout(r, Math.min(900, Math.max(180, etapes[i].duree_ms / 6)) / vitesse)); if (!annule) surEtape(i, 'fait'); } if (!annule) surEtape(etapes.length, 'fin'); })();
    return () => { annule = true; };
  }

  return {
    donnees: F, meta: F.meta, ETATS, NIVEAUX_REGLE, TYPES, LEXIQUE,
    etat, dossier, dossierDe, statut, brouillon: () => brouillon, perime: () => !!brouillon,
    parametres: (cas = revs[pos].etat.cas) => F.cas[cas].parametres, cas: () => Object.keys(F.cas), nomCas,
    proposer, appliquer, abandonner, changer, changerCas, annuler, retablir, allerA, restaurer, reinitialiser,
    peutAnnuler: () => revs[pos].parent != null && revs[pos].parent >= 0, peutRetablir: () => refaire.length > 0,
    niveau: () => niveau, definirNiveau, historique, position: () => pos, comparer, decrire,
    fait, reference, terme, mesures, profilLignes, propre, fmt, relireTrace,
    execution: (cas = revs[pos].etat.cas) => F.cas[cas].execution_reelle, serieActif: (cas = revs[pos].etat.cas) => F.cas[cas].serie_actif,
    speciaux: F.speciaux, abonner: (f) => { abonnes.add(f); return () => abonnes.delete(f); },
    lien: (page) => { const e = etat(); return `${page}#cas=${e.cas}&${cleDe(e).replace(/;/g, '&')}&n=${niveau}`; },
  };
})();
