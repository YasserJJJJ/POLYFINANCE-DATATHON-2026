import { useEffect, useMemo, useRef, useState } from 'react'
import { api, dollars } from '../api.js'
import { Jauge } from '../composants/Base.jsx'
import { MiseEnSituation, PROFIL_VIERGE, SECTEURS_FR, TroisEtats } from '../composants/Profil.jsx'
import { SourcesCompactes, useRegistre } from '../composants/Sources.jsx'

// Étapes 1 et 2 en une seule conversation : la personne écrit une phrase, le Profileur (/api/comprendre) la lit,
// on ne pose ensuite que les questions qui manquent, une à la fois, puis on montre un résumé corrigeable.
// Aucun chiffre n'est inventé ici : tout ce qui est affiché vient de la phrase, des réponses ou du backend.

const EXEMPLES = {
  robert: 'Placer une partie de ma retraite dans une action dont tout le monde parle',
  amira: 'Mettre une part de mon épargne en Bitcoin, sur le long terme',
  mateo: 'Un placement à dividendes pour la famille, en restant fidèle à mes valeurs',
}

const LIBELLES_CHAMPS = {
  ticker: 'placement', montant_cad: 'montant', epargne_totale_cad: 'épargne', somme_a_preserver_cad: 'somme à préserver',
  horizon_ans: 'horizon', retrait_prevu_ans: 'retrait prévu', revenu_stable: 'revenu stable',
  fonds_urgence: "fonds d'urgence", dettes_importantes: 'dettes', exclusions: 'secteurs à éviter',
}

const nombre = (v) => (v === '' || v == null ? null : Number(v))
const ans = (n) => `${n} an${n > 1 ? 's' : ''}`
const pct = (n) => Number(n).toLocaleString('fr-CA', { maximumFractionDigits: 1 })
const ouiNon = (v) => (v === true ? 'Oui' : v === false ? 'Non' : null)

// Ce que le Profileur a lu ne remplit que les champs vides : une valeur déjà là n'est jamais écrasée.
function appliquerLecture(profil, demande, r) {
  const champs = r.profil?.extraits?.champs || {}
  const p = { ...profil }
  for (const [k, v] of Object.entries(champs)) {
    if (k === 'ticker' || k === 'montant_cad') continue
    const vide = p[k] == null || (Array.isArray(p[k]) && p[k].length === 0)
    if (vide) p[k] = v
  }
  for (const k of ['envie', 'peur']) if (r.profil?.[k]) p[k] = r.profil[k]
  const d = { ...demande, ticker: demande.ticker ?? champs.ticker ?? null, montant_cad: demande.montant_cad ?? champs.montant_cad ?? null }
  return { p, d }
}

// Les questions à poser, dans l'ordre, seulement pour ce qui manque et qui change le résultat.
function questionsManquantes(p, d, questionsTolerance) {
  const q = []
  if (!d.ticker) {
    q.push({ id: 'ticker', type: 'actif', texte: 'Quel placement as-tu en tête ?',
      pourquoi: 'Sans placement précis, je ne peux mesurer ni sa pire chute ni ses variations.' })
  }
  if (d.montant_cad == null) {
    q.push({ id: 'montant_cad', type: 'montant', cible: 'demande', texte: 'Quel montant veux-tu placer, environ ?',
      pourquoi: 'Le montant fixe ce que tu pourrais perdre, en dollars.', suggestions: [1000, 5000, 10000, 25000] })
  }
  if (p.epargne_totale_cad == null) {
    q.push({ id: 'epargne_totale_cad', type: 'montant', cible: 'profil', texte: "Combien as-tu d'épargne au total, environ ?",
      pourquoi: 'Je compare le montant à ton épargne : c’est ce qui dit si ce placement pèse lourd pour toi.',
      suggestions: [10000, 40000, 100000, 250000] })
  }
  if (p.horizon_ans == null) {
    q.push({ id: 'horizon_ans', type: 'choix', cible: 'profil', texte: "Dans combien d'années penses-tu avoir besoin de cet argent ?",
      pourquoi: 'Si tu en as besoin avant que le placement ait pu se remettre d’une chute, le verdict change.',
      choix: [1, 2, 3, 5, 10, 15, 20].map((n) => [ans(n), n]) })
  }
  const toleranceConnue = p.tolerance != null || Object.keys(p.reponses_tolerance || {}).length > 0
  if (!toleranceConnue) {
    questionsTolerance.forEach((qt, i) => q.push({
      id: qt.id, type: 'tolerance', texte: qt.texte, choix: qt.choix, miseEnSituation: qt.id === 'q_chute',
      pourquoi: i === 0
        ? '3 questions inspirées de Grable & Lytton (1999) pour situer ce que tu es prêt·e à risquer. Les points de chaque réponse sont un barème de l’équipe.'
        : null,
    }))
  }
  if (p.fonds_urgence == null) {
    q.push({ id: 'fonds_urgence', type: 'choix', cible: 'profil', texte: "As-tu un fonds d'urgence (3 à 6 mois de dépenses) de côté ?",
      pourquoi: 'Sans réserve, une baisse peut forcer une vente au pire moment. C’est une des règles du Gardien.',
      choix: [['Oui', true], ['Non', false], ['Je ne sais pas', null]] })
  }
  return q
}

function Reformulation({ profil, demande, actifs, compris }) {
  const actif = actifs.find((a) => a.ticker === demande.ticker)
  const poids = compris?.profil?.evaluation?.poids_pct
  const sujet = profil.nom && profil.nom !== 'Toi' ? `${profil.nom} envisage` : 'Tu envisages'
  const champs = Object.keys(compris?.profil?.extraits?.champs || {})
  return (
    <>
      <p className="conv-etiquette">Voici ce que j'ai compris :</p>
      <div className="conv-compris">
        <p>
          {sujet} de placer <strong>{demande.montant_cad != null ? dollars(demande.montant_cad) : 'un montant à préciser'}</strong>{' '}
          dans <strong>{actif ? `${actif.name} (${actif.ticker})` : 'un placement à préciser'}</strong>
          {poids != null && <>, soit <strong>{poids} %</strong> de l'épargne</>}
          {profil.horizon_ans != null && <>, avec un horizon de <strong>{ans(profil.horizon_ans)}</strong></>}.
        </p>
        {(profil.envie || profil.peur) && (
          <p className="envie-peur">
            {profil.envie && <span><strong>Ce que tu veux :</strong> {profil.envie}</span>}
            {profil.peur && <span><strong>Ce qui t'inquiète :</strong> {profil.peur}</span>}
          </p>
        )}
        {champs.length > 0 && (
          <p className="muted petit">
            Lu dans ta phrase par {compris.profil.extraits.source}, puis vérifié par le code :{' '}
            {champs.map((c) => LIBELLES_CHAMPS[c] || c).join(', ')}.
          </p>
        )}
      </div>
      {compris?.profil?.tensions?.map((t) => <p key={t} className="tension">{t}</p>)}
    </>
  )
}

function Question({ q, actifs, active, onRepondre }) {
  const [valeur, setValeur] = useState('')
  const [ticker, setTicker] = useState('')
  return (
    <>
      <p>{q.texte}</p>
      {q.pourquoi && <p className="conv-pourquoi">Pourquoi cette question ? {q.pourquoi}</p>}
      {q.miseEnSituation && <MiseEnSituation />}
      {active && (
        <div className="conv-reponses">
          {(q.type === 'choix' || q.type === 'tolerance') && q.choix.map(([libelle, v]) => (
            <button key={libelle} type="button" className="bouton conv-choix" onClick={() => onRepondre(v, libelle)}>{libelle}</button>
          ))}
          {q.type === 'montant' && (
            <>
              {q.suggestions.map((s) => (
                <button key={s} type="button" className="bouton conv-choix" onClick={() => onRepondre(s, dollars(s))}>{dollars(s)}</button>
              ))}
              <form className="conv-libre" onSubmit={(e) => { e.preventDefault(); const n = nombre(valeur); if (n != null && n >= 0) onRepondre(n, dollars(n)) }}>
                <input type="number" min="0" step="500" inputMode="numeric" aria-label="Autre montant en dollars canadiens"
                  placeholder="Autre montant ($ CA)" value={valeur} onChange={(e) => setValeur(e.target.value)} />
                <button type="submit" className="bouton" disabled={valeur === ''}>Valider</button>
              </form>
            </>
          )}
          {q.type === 'actif' && (
            <form className="conv-libre" onSubmit={(e) => {
              e.preventDefault()
              const a = actifs.find((x) => x.ticker === ticker)
              if (a) onRepondre(a.ticker, `${a.name} (${a.ticker})`)
            }}>
              <select aria-label="Placement envisagé" value={ticker} onChange={(e) => setTicker(e.target.value)}>
                <option value="">Choisir un placement…</option>
                {actifs.map((a) => <option key={a.ticker} value={a.ticker}>{a.name} ({a.ticker})</option>)}
              </select>
              <button type="submit" className="bouton" disabled={!ticker}>Valider</button>
            </form>
          )}
        </div>
      )}
    </>
  )
}

function Resume({ profil, setProfil, demande, setDemande, actifs, questions, compris, estPersona, onLancer }) {
  const [edition, setEdition] = useState(false)
  const registre = useRegistre()
  const ev = compris?.profil?.evaluation
  const actif = actifs.find((a) => a.ticker === demande.ticker)
  const maj = (champ, valeur) => setProfil((p) => ({ ...p, [champ]: valeur }))
  const secteurs = useMemo(() => [...new Set(actifs.map((a) => a.sector))].filter((s) => SECTEURS_FR[s]), [actifs])
  const basculeExclusion = (s) => maj('exclusions', profil.exclusions.includes(s) ? profil.exclusions.filter((x) => x !== s) : [...profil.exclusions, s])
  const ajouterDetenu = (t) => t && !profil.portefeuille_actuel.includes(t) && maj('portefeuille_actuel', [...profil.portefeuille_actuel, t])
  const reponsesDonnees = Object.keys(profil.reponses_tolerance || {}).length > 0

  const lignes = [
    ['Placement', actif ? `${actif.name} (${actif.ticker})` : null],
    ['Montant à placer', demande.montant_cad != null ? dollars(demande.montant_cad) : null],
    ['Épargne totale', profil.epargne_totale_cad != null ? `${dollars(profil.epargne_totale_cad)}${estPersona ? ' (fictive)' : ''}` : null],
    ["Part de l'épargne", ev?.poids_pct != null ? `${ev.poids_pct} %` : null],
    ['Horizon', profil.horizon_ans != null ? ans(profil.horizon_ans) : null],
    ['Somme à ne jamais risquer', profil.somme_a_preserver_cad != null ? dollars(profil.somme_a_preserver_cad) : null],
    ['Retrait prévu avant', profil.retrait_prevu_ans == null ? 'Aucun' : `dans ${ans(profil.retrait_prevu_ans)}`],
    ["Fonds d'urgence", ouiNon(profil.fonds_urgence)],
    ['Secteurs à éviter', profil.exclusions?.length ? profil.exclusions.map((s) => SECTEURS_FR[s] || s).join(', ') : 'Aucun'],
    ['Déjà détenu', profil.portefeuille_actuel?.length ? profil.portefeuille_actuel.join(', ') : 'Rien de déclaré'],
  ]

  return (
    <div className="carte conv-resume">
      <div className="conv-resume-tete">
        <div>
          <h2>Ta situation, en résumé</h2>
          <p className="muted petit">Corrige ce qui est faux. Ce que tu n'as pas dit reste « non précisé » : je n'invente rien.</p>
        </div>
        <button type="button" className="bouton discret" aria-expanded={edition} onClick={() => setEdition((v) => !v)}>
          {edition ? 'Terminer' : 'Modifier'}
        </button>
      </div>

      {!edition ? (
        <dl className="conv-liste">
          {lignes.map(([k, v]) => (
            <div key={k}>
              <dt>{k}</dt>
              <dd className={v == null ? 'muted' : ''}>{v ?? 'Non précisé'}</dd>
            </div>
          ))}
        </dl>
      ) : (
        <div className="formulaire conv-edition">
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
          <div className="champ">
            <label htmlFor="horizon">Dans combien d'années auras-tu besoin de cet argent ? <strong>{profil.horizon_ans != null ? ans(profil.horizon_ans) : '—'}</strong></label>
            <input id="horizon" type="range" min="1" max="25" value={profil.horizon_ans ?? 5}
              onChange={(e) => maj('horizon_ans', Number(e.target.value))} />
          </div>
          <div className="champ">
            <label htmlFor="retrait">
              Retrait prévu avant cela ? <strong>{profil.retrait_prevu_ans == null ? 'Aucun' : `dans ${ans(profil.retrait_prevu_ans)}`}</strong>
            </label>
            <div className="champ-ligne serre">
              <input id="retrait" type="range" min="0" max="15" value={profil.retrait_prevu_ans ?? 0}
                onChange={(e) => maj('retrait_prevu_ans', Number(e.target.value) || null)} />
              <button type="button" className="bouton discret" onClick={() => maj('retrait_prevu_ans', null)}>Aucun</button>
            </div>
          </div>
          <TroisEtats id="urgence" libelle="Fonds d'urgence (3 à 6 mois de dépenses) ?" valeur={profil.fonds_urgence} onChange={(v) => maj('fonds_urgence', v)} />
          <TroisEtats id="revenu" libelle="Revenu stable ?" valeur={profil.revenu_stable} onChange={(v) => maj('revenu_stable', v)} />
          <TroisEtats id="dettes" libelle="Dettes importantes (hors hypothèque) ?" valeur={profil.dettes_importantes} onChange={(v) => maj('dettes_importantes', v)} />

          <div className="champ">
            <span className="champ-titre">Secteurs que tu veux éviter</span>
            <div className="puces-choix">
              {secteurs.map((s) => (
                <button key={s} type="button" aria-pressed={profil.exclusions.includes(s)}
                  className={`choix ${profil.exclusions.includes(s) ? 'actif' : ''}`} onClick={() => basculeExclusion(s)}>
                  {SECTEURS_FR[s]}
                </button>
              ))}
            </div>
          </div>
          <div className="champ">
            <span className="champ-titre">Ce que tu détiens déjà</span>
            <div className="puces-choix">
              {profil.portefeuille_actuel.map((t) => (
                <button key={t} type="button" className="choix actif" aria-label={`Retirer ${t}`}
                  onClick={() => maj('portefeuille_actuel', profil.portefeuille_actuel.filter((x) => x !== t))}>{t} ×</button>
              ))}
              <select aria-label="Ajouter un placement détenu" value="" onChange={(e) => ajouterDetenu(e.target.value)}>
                <option value="">+ Ajouter</option>
                {actifs.map((a) => <option key={a.ticker} value={a.ticker}>{a.ticker}</option>)}
              </select>
            </div>
          </div>

          <div className="champ">
            <span className="champ-titre">Ton rapport au risque</span>
            <p className="muted petit">3 questions adaptées de l'échelle de Grable &amp; Lytton (1999), barème de l'équipe.</p>
            {questions.map((q) => (
              <fieldset key={q.id} className="question">
                <legend>{q.texte}</legend>
                <div className="reponses">
                  {q.choix.map(([libelle, valeur]) => {
                    const choisi = profil.reponses_tolerance?.[q.id] === valeur
                    return (
                      <label key={libelle} className={`reponse ${choisi ? 'choisi' : ''}`}>
                        <input type="radio" name={`r-${q.id}`} checked={choisi}
                          onChange={() => maj('reponses_tolerance', { ...profil.reponses_tolerance, [q.id]: valeur })} />
                        {libelle}
                      </label>
                    )
                  })}
                </div>
              </fieldset>
            ))}
          </div>
        </div>
      )}

      <div className="conv-jauges">
        <Jauge libelle="Ce que tu veux risquer (tolérance)" valeur={ev?.tolerance} retenue={ev?.limite === 'tolérance'}
          detail={ev?.perte_max_tolerance_pct == null ? 'Réponds aux 3 questions pour la mesurer.'
            : !reponsesDonnees && estPersona
              ? `Valeur fixée par le profil fictif (« ${profil.nom} »), pas une mesure. Clique sur « Modifier » pour répondre aux 3 questions.`
              : `Baisse acceptée : jusqu'à ${pct(ev.perte_max_tolerance_pct)} % de l'épargne (barème de l'équipe).`} />
        <Jauge libelle="Ce que ta situation permet (capacité)" valeur={ev?.capacite} retenue={ev?.limite === 'capacité'}
          detail={ev?.capacite_raisons?.join(' · ')} />
        {ev?.score_retenu != null && (
          <p className="retenu">
            On retient la plus basse : ta <strong>{ev.limite}</strong>, soit une baisse supportable de{' '}
            <strong>{pct(ev.perte_max_retenue_pct)} %</strong> de l'épargne.
          </p>
        )}
        <p className="muted petit">Barèmes : hypothèses de l'équipe, inspirées des Réformes axées sur le client (ACVM).</p>
        <SourcesCompactes ids={[...(registre?.justifications?.jauges?.references || []),
          ...(registre?.justifications?.questions?.references || [])]} />
      </div>

      {profil.citations?.length > 0 && (
        <div className="conv-mots">
          <span className="muted">{estPersona ? 'Phrases types du profil (écrites par l’équipe) : ' : 'Tes mots, gardés tels quels : '}</span>
          {profil.citations.map((c) => <mark key={c}>« {c} »</mark>)}
          <p className="muted petit">Ils seront remis à côté des chiffres dans le verdict (le miroir).</p>
        </div>
      )}

      {compris?.questions?.length > 0 && (
        <div className="manque">
          <strong>Encore à préciser :</strong>
          <ul>{compris.questions.map((q) => <li key={q}>{q}</li>)}</ul>
        </div>
      )}

      <button type="button" className="bouton principal grand plein" onClick={onLancer} disabled={!demande.ticker}>
        C'est correct, lancer la vérification →
      </button>
      {!demande.ticker && <p className="muted petit">Choisis d'abord un placement (bouton « Modifier »).</p>}
    </div>
  )
}

export default function Conversation({ personas, actifs, questions, profil, setProfil, demande, setDemande, onPhase, onLancer }) {
  const [phase, setPhase] = useState('saisie') // saisie → lecture → questions → resume
  const [brouillon, setBrouillon] = useState('')
  const [personaChoisie, setPersonaChoisie] = useState(null)
  const [estPersona, setEstPersona] = useState(false)
  const [messages, setMessages] = useState([])
  const [file, setFile] = useState([])
  const [compris, setCompris] = useState(null)
  const idSuivant = useRef(1)
  const bas = useRef(null)
  const zone = useRef(null)
  const minuterie = useRef(null)

  const ajouter = (m) => setMessages((l) => [...l, { ...m, id: idSuivant.current++ }])

  useEffect(() => { onPhase(phase === 'resume' ? 1 : 0) }, [phase, onPhase])
  useEffect(() => {
    if (messages.length) bas.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, phase])

  // Au résumé, chaque correction relance le Profileur (sans relire la phrase) pour mettre à jour les jauges.
  useEffect(() => {
    if (phase !== 'resume') return undefined
    clearTimeout(minuterie.current)
    minuterie.current = setTimeout(() => {
      api.comprendre(profil, { ...demande, texte_lu: true }).then(setCompris).catch(() => {})
    }, 300)
    return () => clearTimeout(minuterie.current)
  }, [phase, profil, demande])

  const allerAuResume = (p, d) => {
    ajouter({ de: 'af', texte: "Merci. Voici ta situation telle que je l'ai comprise. Si tout est correct, lance la vérification." })
    setPhase('resume')
    api.comprendre(p, { ...d, texte_lu: true }).then(setCompris).catch(() => {})
  }

  const envoyer = async () => {
    const texte = brouillon.trim()
    if (!texte || phase !== 'saisie') return
    const persona = personaChoisie && personas?.[personaChoisie]
    let p
    let d
    if (persona) {
      p = { ...PROFIL_VIERGE, ...persona.profil }
      d = texte === persona.demande.texte ? { ...persona.demande } : { texte, ticker: null, montant_cad: null }
    } else {
      p = { ...PROFIL_VIERGE, citations: texte.split(/(?<=[.!?])\s+/).filter((s) => s.trim().length > 3) }
      d = { texte, ticker: null, montant_cad: null }
    }
    setEstPersona(Boolean(persona))
    setBrouillon('')
    ajouter({ de: 'moi', texte })
    setPhase('lecture')
    try {
      const r = await api.comprendre(p, d)
      const lu = appliquerLecture(p, d, r)
      setProfil(lu.p)
      setDemande(lu.d)
      setCompris(r)
      const restantes = questionsManquantes(lu.p, lu.d, questions)
      ajouter({ de: 'af', type: 'compris', profil: lu.p, demande: lu.d, compris: r })
      if (restantes.length) {
        ajouter({ de: 'af', texte: restantes.length === 1
          ? 'Il me manque une seule information. Je ne te demande que ce qui change le résultat.'
          : `Il me manque ${restantes.length} informations. Je ne te demande que ce qui change le résultat, une à la fois.` })
        setFile(restantes.slice(1))
        ajouter({ de: 'af', type: 'question', q: restantes[0] })
        setPhase('questions')
      } else {
        allerAuResume(lu.p, lu.d)
      }
    } catch (e) {
      ajouter({ de: 'af', texte: `Je n'arrive pas à joindre l'analyse pour l'instant (${e.message}). Réessaie dans un instant.` })
      setBrouillon(texte)
      setPhase('saisie')
    }
  }

  const repondre = (q, valeur, libelle) => {
    ajouter({ de: 'moi', texte: libelle })
    let p = profil
    let d = demande
    if (q.type === 'actif') d = { ...d, ticker: valeur }
    else if (q.type === 'tolerance') p = { ...p, reponses_tolerance: { ...(p.reponses_tolerance || {}), [q.id]: valeur } }
    else if (q.cible === 'demande') d = { ...d, [q.id]: valeur }
    else p = { ...p, [q.id]: valeur }
    setProfil(p)
    setDemande(d)
    setMessages((l) => l.map((m) => (m.type === 'question' && m.q.id === q.id ? { ...m, repondue: true } : m)))
    if (file.length) {
      ajouter({ de: 'af', type: 'question', q: file[0] })
      setFile(file.slice(1))
    } else {
      allerAuResume(p, d)
    }
  }

  const choisirExemple = (cle) => {
    setPersonaChoisie(cle)
    setBrouillon(personas[cle].demande.texte)
    zone.current?.focus()
  }

  return (
    <section className="conversation">
      {phase === 'saisie' && messages.length === 0 && (
        <div className="conv-accueil">
          <h1>Que veux-tu faire de ton argent ?</h1>
          <p className="lede">Écris-le simplement, comme tu le dirais à un ami. Pas besoin de connaître la finance.</p>
        </div>
      )}

      {messages.length > 0 && (
        <div className="conv-fil">
          {messages.map((m) => (m.de === 'moi' ? (
            <div key={m.id} className="conv-moi"><p>{m.texte}</p></div>
          ) : (
            <div key={m.id} className="conv-af">
              <span className="conv-avatar" aria-hidden="true">≠</span>
              <div className="conv-corps">
                {m.type === 'compris' && <Reformulation profil={m.profil} demande={m.demande} actifs={actifs} compris={m.compris} />}
                {m.type === 'question' && (
                  <Question q={m.q} actifs={actifs} active={phase === 'questions' && !m.repondue}
                    onRepondre={(v, libelle) => repondre(m.q, v, libelle)} />
                )}
                {!m.type && <p>{m.texte}</p>}
              </div>
            </div>
          )))}
          {phase === 'lecture' && (
            <div className="conv-attente"><span className="roue" aria-hidden="true" /> Je lis ta demande…</div>
          )}
          {phase === 'resume' && (
            <div className="conv-decale">
              <Resume profil={profil} setProfil={setProfil} demande={demande} setDemande={setDemande} actifs={actifs}
                questions={questions} compris={compris} estPersona={estPersona} onLancer={onLancer} />
            </div>
          )}
          <div ref={bas} />
        </div>
      )}

      {phase === 'saisie' && (
        <>
          <form className="conv-saisie" onSubmit={(e) => { e.preventDefault(); envoyer() }}>
            <label htmlFor="texte-libre" className="sr-only">Ta demande, avec tes mots</label>
            <textarea id="texte-libre" ref={zone} rows={4} value={brouillon}
              onChange={(e) => { setBrouillon(e.target.value); if (!e.target.value) setPersonaChoisie(null) }}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); envoyer() } }}
              placeholder="Ex. : je voudrais mettre 10 000 $ en Bitcoin. J'ai 40 000 $ d'épargne. Mais j'ai peur de tout perdre." />
            <div className="conv-saisie-bas">
              <span className="muted petit">Une phrase suffit. « Je veux… J'ai… Mais j'ai peur de… »</span>
              <button type="submit" className="bouton principal" disabled={!brouillon.trim()}>Continuer →</button>
            </div>
          </form>

          {messages.length === 0 && personas && (
            <div className="conv-exemples">
              <p className="champ-titre">Pas d'idée ? Essaie avec un profil du défi</p>
              <ul>
                {Object.entries(personas).map(([cle, pe]) => (
                  <li key={cle}>
                    <button type="button" onClick={() => choisirExemple(cle)} className={personaChoisie === cle ? 'actif' : ''}>
                      <span>{EXEMPLES[cle] || pe.demande.texte}<span className="muted petit"> · {pe.profil.nom}, {pe.profil.age} ans</span></span>
                      <span aria-hidden="true">→</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </section>
  )
}
