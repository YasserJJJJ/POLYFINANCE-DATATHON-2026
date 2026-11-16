import { useEffect, useMemo, useRef, useState } from 'react'
import { api, dollars } from '../api.js'
import { Jauge } from '../composants/Base.jsx'
import { SourcesCompactes, useRegistre } from '../composants/Sources.jsx'
import { symbolesPortefeuille } from '../portefeuille.js'

export const SECTEURS_FR = {
  Energy: 'Énergie (pétrole, gaz, pipelines)', 'Crypto asset': 'Cryptoactifs', Financials: 'Finance',
  'Information Technology': 'Technologies', 'Consumer Discretionary': 'Consommation discrétionnaire',
  'Health Care': 'Santé', Utilities: 'Services publics', Industrials: 'Industrie',
  'Consumer Staples': 'Consommation de base', 'Communication Services': 'Communication',
}

const nombre = (v) => (v === '' || v == null ? null : Number(v))

function TroisEtats({ id, libelle, valeur, onChange }) {
  return (
    <fieldset className="trois-etats">
      <legend>{libelle}</legend>
      {[['Oui', true], ['Non', false], ['Je ne sais pas', null]].map(([l, v]) => (
        <label key={l} className={valeur === v ? 'choisi' : ''}>
          <input type="radio" name={id} checked={valeur === v} onChange={() => onChange(v)} />
          {l}
        </label>
      ))}
    </fieldset>
  )
}

function MiseEnSituation() {
  // Illustration fixe : 10 000 $ qui perdent 20 % en 3 mois (scénario fictif).
  const pts = [[0, 10000], [1, 9700], [2, 9900], [3, 9300], [4, 9000], [5, 9200], [6, 8600], [7, 8300], [8, 8500], [9, 8000]]
  const x = (i) => 10 + i * 31
  const y = (v) => 10 + (10200 - v) * 0.045
  return (
    <figure className="mise-en-situation">
      <svg viewBox="0 0 300 110" role="img" aria-label="Un placement de 10 000 $ qui descend à 8 000 $ en 3 mois">
        <line x1="10" x2="290" y1={y(10000)} y2={y(10000)} className="ligne-ref" />
        <polyline points={pts.map(([i, v]) => `${x(i)},${y(v)}`).join(' ')} className="ligne-chute" />
        <circle cx={x(9)} cy={y(8000)} r="4" className="point-chute" />
        <text x="12" y={y(10000) - 4} className="txt-graphe">10 000 $</text>
        <text x={x(9) - 4} y={y(8000) + 16} textAnchor="end" className="txt-graphe fort">8 000 $ (−20 %)</text>
      </svg>
      <figcaption>Scénario fictif, pour situer ta réaction.</figcaption>
    </figure>
  )
}

export default function Etape2Verifier({ profil, setProfil, demande, setDemande, actifs, questions, onRetour, onLancer }) {
  const [compris, setCompris] = useState(null)
  const [erreurLecture, setErreurLecture] = useState('')
  const minuterie = useRef(null)
  const texteApplique = useRef(null)
  const maj = (champ, valeur) => setProfil((p) => ({ ...p, [champ]: valeur }))

  useEffect(() => {
    clearTimeout(minuterie.current)
    minuterie.current = setTimeout(() => {
      api.comprendre(profil, demande).then((r) => {
        setCompris(r)
        setErreurLecture('')
        // Ce que le Profileur a lu dans la phrase ne remplit que les champs vides, une seule fois par phrase :
        // une correction faite à la main n'est jamais écrasée.
        if (texteApplique.current === demande.texte) return
        texteApplique.current = demande.texte
        const champs = r.profil?.extraits?.champs || {}
        const pourProfil = Object.fromEntries(Object.entries(champs).filter(([k]) => k !== 'ticker' && k !== 'montant_cad'))
        // L'envie et la peur lues dans la phrase restent dans le profil : le Rédacteur s'en sert au verdict.
        for (const k of ['envie', 'peur']) if (r.profil?.[k]) pourProfil[k] = r.profil[k]
        if (Object.keys(pourProfil).length) setProfil((p) => ({ ...p, ...pourProfil }))
        if (champs.ticker || champs.montant_cad) {
          setDemande((d) => ({ ...d, ticker: d.ticker ?? champs.ticker ?? null, montant_cad: d.montant_cad ?? champs.montant_cad ?? null }))
        }
      }).catch((e) => setErreurLecture(e.message))
    }, 300)
    return () => clearTimeout(minuterie.current)
  }, [profil, demande, setDemande, setProfil])

  const secteurs = useMemo(() => [...new Set(actifs.map((a) => a.sector))].filter((s) => SECTEURS_FR[s]), [actifs])
  const actif = actifs.find((a) => a.ticker === demande.ticker)
  const registre = useRegistre()
  const portefeuille = symbolesPortefeuille(profil.portefeuille_actuel)
  const ev = compris?.profil?.evaluation
  // Le pourcentage vient du backend (même calcul qu'à l'étape du verdict) pour ne jamais diverger
  // d'un arrondi JS à un arrondi Python ; secours si l'appel /api/comprendre n'a pas encore répondu.
  const poids = ev?.poids_pct ??
    (profil.epargne_totale_cad && demande.montant_cad ? Math.round(demande.montant_cad / profil.epargne_totale_cad * 100) : null)
  const basculeExclusion = (s) => maj('exclusions', profil.exclusions.includes(s) ? profil.exclusions.filter((x) => x !== s) : [...profil.exclusions, s])
  const poidsDeclares = profil.portefeuille_actuel != null && !Array.isArray(profil.portefeuille_actuel)
  const ajouterDetenu = (t) => t && !portefeuille.includes(t) && maj('portefeuille_actuel',
    poidsDeclares ? { ...profil.portefeuille_actuel, [t]: 0 } : [...portefeuille, t])
  const retirerDetenu = (t) => maj('portefeuille_actuel', poidsDeclares
    ? Object.fromEntries(Object.entries(profil.portefeuille_actuel).filter(([k]) => k !== t))
    : portefeuille.filter((x) => x !== t))

  return (
    <section className="etape2">
      <div className="compris carte">
        <p className="surtitre">Voici ce que j'ai compris de toi</p>
        <p className="compris-phrase">
          {profil.nom === 'Toi' ? 'Tu envisages' : `${profil.nom} envisage`} de placer{' '}
          <strong>{dollars(demande.montant_cad)}</strong> dans <strong>{actif ? `${actif.name} (${actif.ticker})` : '…'}</strong>
          {poids != null && <>, soit <strong>{poids} %</strong> de l'épargne</>}, avec un horizon de{' '}
          <strong>{profil.horizon_ans ?? '…'} an(s)</strong>.
        </p>
        {demande.texte && <p className="citation">« {demande.texte} »</p>}
        {compris?.profil?.extraits && Object.keys(compris.profil.extraits.champs || {}).length > 0 && (
          <p className="muted petit">
            Lu dans ta phrase par {compris.profil.extraits.source}, puis vérifié par le code :{' '}
            {Object.keys(compris.profil.extraits.champs).join(', ')}.
          </p>
        )}
        {(compris?.profil?.envie || compris?.profil?.peur) && (
          <p className="envie-peur">
            {compris.profil.envie && <span><strong>Ce que tu veux :</strong> {compris.profil.envie}</span>}
            {compris.profil.peur && <span><strong>Ce qui t'inquiète :</strong> {compris.profil.peur}</span>}
          </p>
        )}
        {compris?.profil?.tensions?.map((t) => <p key={t} className="tension">{t}</p>)}
        {compris?.questions?.length > 0 && (
          <div className="manque">
            <strong>Il me manque :</strong>
            <ul>{compris.questions.map((q) => <li key={q}>{q}</li>)}</ul>
          </div>
        )}
        <p className="muted petit">Corrige tout ce qui est faux avant l'analyse. Rien n'est calculé à partir d'une information que tu n'as pas vue.</p>
      </div>
      {erreurLecture && <p className="alerte" role="alert">{erreurLecture}</p>}
      {demande.montant_cad > profil.epargne_totale_cad && profil.epargne_totale_cad != null &&
        <p className="manque">Le montant dépasse l'épargne totale. Vérifie les deux montants ; aucune allocation ne pourra être calculée.</p>}

      <div className="colonnes">
        <div className="carte formulaire">
          <h2>Ta demande</h2>
          <div className="champ">
            <label htmlFor="ticker">Placement envisagé</label>
            <select id="ticker" value={demande.ticker || ''} onChange={(e) => setDemande((d) => ({ ...d, ticker: e.target.value || null }))}>
              <option value="">Choisir…</option>
              {actifs.map((a) => <option key={a.ticker} value={a.ticker}>{a.name} ({a.ticker})</option>)}
            </select>
          </div>
          <div className="champ-ligne">
            <div className="champ">
              <label htmlFor="montant">Montant à placer ($ CA)</label>
              <input id="montant" type="number" min="0" step="500" value={demande.montant_cad ?? ''}
                onChange={(e) => setDemande((d) => ({ ...d, montant_cad: nombre(e.target.value) }))} />
            </div>
            <div className="champ">
              <label htmlFor="epargne">Épargne totale ($ CA)</label>
              <input id="epargne" type="number" min="0" step="1000" value={profil.epargne_totale_cad ?? ''}
                onChange={(e) => maj('epargne_totale_cad', nombre(e.target.value))} />
            </div>
          </div>
          <div className="champ">
            <label htmlFor="preserver">Somme à ne jamais risquer ($ CA)</label>
            <input id="preserver" type="number" min="0" step="1000" value={profil.somme_a_preserver_cad ?? ''}
              onChange={(e) => maj('somme_a_preserver_cad', nombre(e.target.value))} />
          </div>

          <h2>Ta situation</h2>
          <div className="champ">
            <label htmlFor="horizon">Dans combien d'années auras-tu besoin de cet argent ? <strong>{profil.horizon_ans ?? '—'} an(s)</strong></label>
            <input id="horizon" type="range" min="1" max="25" value={profil.horizon_ans ?? 5}
              onChange={(e) => maj('horizon_ans', Number(e.target.value))} />
          </div>
          <div className="champ">
            <label htmlFor="retrait">
              Retrait prévu avant cela ?{' '}
              <strong>{profil.retrait_prevu_ans == null ? 'Non précisé' : `dans ${profil.retrait_prevu_ans} an(s)`}</strong>
            </label>
            <div className="champ-ligne serre">
              <input id="retrait" type="range" min="0" max="15" value={profil.retrait_prevu_ans ?? 0}
                onChange={(e) => maj('retrait_prevu_ans', Number(e.target.value) || null)} />
              <button type="button" className="bouton discret" onClick={() => maj('retrait_prevu_ans', null)}>Non précisé</button>
            </div>
          </div>
          <TroisEtats id="revenu" libelle="Revenu stable ?" valeur={profil.revenu_stable} onChange={(v) => maj('revenu_stable', v)} />
          <TroisEtats id="urgence" libelle="Fonds d'urgence (3 à 6 mois de dépenses) ?" valeur={profil.fonds_urgence} onChange={(v) => maj('fonds_urgence', v)} />
          <TroisEtats id="dettes" libelle="Dettes importantes (hors hypothèque) ?" valeur={profil.dettes_importantes} onChange={(v) => maj('dettes_importantes', v)} />

          <h2>Tes valeurs</h2>
          <p className="muted petit">Secteurs que tu veux éviter :</p>
          <div className="puces-choix">
            {secteurs.map((s) => (
              <button key={s} type="button" aria-pressed={profil.exclusions.includes(s)}
                className={`choix ${profil.exclusions.includes(s) ? 'actif' : ''}`} onClick={() => basculeExclusion(s)}>
                {SECTEURS_FR[s]}
              </button>
            ))}
          </div>

          <h2>Ce que tu détiens déjà</h2>
          <div className="puces-choix">
            {portefeuille.map((t) => (
              <button key={t} type="button" className="choix actif" onClick={() => retirerDetenu(t)}
                aria-label={`Retirer ${t}`}>{t} ×</button>
            ))}
            <select aria-label="Ajouter un placement détenu" value="" onChange={(e) => ajouterDetenu(e.target.value)}>
              <option value="">+ Ajouter</option>
              {actifs.map((a) => <option key={a.ticker} value={a.ticker}>{a.ticker}</option>)}
            </select>
          </div>
          {portefeuille.length > 0 && <>
            <label className="poids-option"><input type="checkbox" checked={poidsDeclares}
              onChange={(e) => maj('portefeuille_actuel', e.target.checked
                ? Object.fromEntries(portefeuille.map((t) => [t, 0])) : portefeuille)} />
              {' '}Je renseigne les poids de mes placements</label>
            {poidsDeclares
              ? <div className="poids-saisie">
                  <p className="muted petit">Fractions de l'épargne, de 0 à 1 : par exemple 0,5 pour la moitié. Leur somme doit être 1. Aucun poids n'est normalisé automatiquement.</p>
                  {portefeuille.map((t) => <div className="champ" key={t}>
                    <label htmlFor={`poids-${t}`}>Poids de {t}</label>
                    <input id={`poids-${t}`} type="number" min="0" max="1" step="any" value={profil.portefeuille_actuel[t] ?? ''}
                      onChange={(e) => maj('portefeuille_actuel', { ...profil.portefeuille_actuel, [t]: nombre(e.target.value) })} />
                  </div>)}
                </div>
              : <p className="muted petit">Hypothèse d'équipondération : chaque placement détenu reçoit le même poids. Tu peux préciser ces poids.</p>}
          </>}
        </div>

        <div className="pile">
          <div className="carte">
            <h2>Ton rapport au risque</h2>
            <p className="muted petit">3 questions adaptées de l'échelle de tolérance de Grable &amp; Lytton (1999). Les points
              attribués à chaque réponse sont un barème de l'équipe, pas celui de l'échelle d'origine.</p>
            {questions.map((q) => (
              <fieldset key={q.id} className="question">
                <legend>{q.texte}</legend>
                {q.id === 'q_chute' && <MiseEnSituation />}
                <div className="reponses">
                  {q.choix.map(([libelle, valeur]) => {
                    const choisi = profil.reponses_tolerance?.[q.id] === valeur
                    return (
                      <label key={libelle} className={`reponse ${choisi ? 'choisi' : ''}`}>
                        <input type="radio" name={q.id} checked={choisi}
                          onChange={() => maj('reponses_tolerance', { ...profil.reponses_tolerance, [q.id]: valeur })} />
                        {libelle}
                      </label>
                    )
                  })}
                </div>
              </fieldset>
            ))}
          </div>

          <div className="carte jauges">
            <h2>Tes deux jauges</h2>
            <Jauge libelle="Ce que tu veux risquer (tolérance)" valeur={ev?.tolerance}
              retenue={ev?.limite === 'tolérance'}
              detail={ev?.perte_max_tolerance_pct == null ? 'Réponds aux 3 questions.'
                : Object.keys(profil.reponses_tolerance || {}).length === 0
                  ? `Valeur fixée par le profil fictif (« ${profil.nom} »), pas une mesure : réponds aux 3 questions pour la mesurer. Baisse acceptée retenue : ${ev.perte_max_tolerance_pct} %.`
                  : `Baisse acceptée : jusqu'à ${ev.perte_max_tolerance_pct} % de ton épargne (barème de l'équipe)`} />
            <Jauge libelle="Ce que ta situation permet (capacité)" valeur={ev?.capacite}
              retenue={ev?.limite === 'capacité'}
              detail={ev?.capacite_raisons?.join(' · ')} />
            {ev?.score_retenu != null && (
              <p className="retenu">
                On retient la plus basse : ta <strong>{ev.limite}</strong>, soit une baisse supportable de{' '}
                <strong>{ev.perte_max_retenue_pct} %</strong> de ton épargne.
              </p>
            )}
            <p className="muted petit">Barèmes : hypothèses de l'équipe, inspirées des Réformes axées sur le client (ACVM).</p>
            <SourcesCompactes ids={[...(registre?.justifications?.jauges?.references || []),
              ...(registre?.justifications?.questions?.references || [])]} />
          </div>
        </div>
      </div>

      <div className="actions barre-actions">
        <button type="button" className="bouton discret" onClick={onRetour}>Retour</button>
        <button type="button" className="bouton principal" onClick={onLancer} disabled={!demande.ticker}>
          Lancer l'analyse
        </button>
      </div>
    </section>
  )
}
