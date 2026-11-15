import { useEffect, useMemo, useRef, useState } from 'react'
import { ArrowRight, Check } from 'lucide-react'
import { api, dollars } from '@/api.js'
import { Button } from '@/components/ui/button'
import { Input, Select } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Textarea } from '@/components/ui/textarea'
import { Logo } from '@/components/Marque.jsx'
import { Jauge, ans, pct } from '@/components/Base.jsx'
import { Choix, MiseEnSituation, PROFIL_VIERGE, SECTEURS_FR, TroisEtats } from '@/components/Profil.jsx'
import { SourcesCompactes, useRegistre } from '@/components/Sources.jsx'

// Étapes 1 et 2 en une seule conversation. La phrase est lue par le Profileur (/api/comprendre), puis on ne pose
// que les questions qui manquent, une à la fois, et on montre un résumé corrigeable avant l'analyse.
// Aucun chiffre n'est inventé ici : tout vient de la phrase, des réponses ou du backend.

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
const ouiNon = (v) => (v === true ? 'Oui' : v === false ? 'Non' : null)

// Ce que le Profileur a lu ne remplit que les champs vides : une valeur déjà là n'est jamais écrasée.
function appliquerLecture(profil, demande, r) {
  const champs = r.profil?.extraits?.champs || {}
  const p = { ...profil }
  for (const [k, v] of Object.entries(champs)) {
    if (k === 'ticker' || k === 'montant_cad') continue
    if (p[k] == null || (Array.isArray(p[k]) && p[k].length === 0)) p[k] = v
  }
  for (const k of ['envie', 'peur']) if (r.profil?.[k]) p[k] = r.profil[k]
  const d = { ...demande, ticker: demande.ticker ?? champs.ticker ?? null, montant_cad: demande.montant_cad ?? champs.montant_cad ?? null }
  return { p, d }
}

// Les questions à poser, dans l'ordre, seulement pour ce qui manque et qui change le résultat.
function questionsManquantes(p, d, questionsTolerance) {
  const q = []
  if (!d.ticker) q.push({ id: 'ticker', type: 'actif', texte: 'Quel placement as-tu en tête ?',
    pourquoi: 'Sans placement précis, je ne peux mesurer ni sa pire chute ni ses variations.' })
  if (d.montant_cad == null) q.push({ id: 'montant_cad', type: 'montant', cible: 'demande', texte: 'Quel montant veux-tu placer, environ ?',
    pourquoi: 'Le montant fixe ce que tu pourrais perdre, en dollars.', suggestions: [1000, 5000, 10000, 25000] })
  if (p.epargne_totale_cad == null) q.push({ id: 'epargne_totale_cad', type: 'montant', cible: 'profil', texte: "Combien as-tu d'épargne au total, environ ?",
    pourquoi: 'Je compare le montant à ton épargne : c’est ce qui dit si ce placement pèse lourd pour toi.', suggestions: [10000, 40000, 100000, 250000] })
  if (p.horizon_ans == null) q.push({ id: 'horizon_ans', type: 'choix', cible: 'profil', texte: "Dans combien d'années penses-tu avoir besoin de cet argent ?",
    pourquoi: 'Si tu en as besoin avant que le placement ait pu se remettre d’une chute, le verdict change.',
    choix: [1, 2, 3, 5, 10, 15, 20].map((n) => [ans(n), n]) })
  if (p.tolerance == null && !Object.keys(p.reponses_tolerance || {}).length) {
    questionsTolerance.forEach((qt, i) => q.push({
      id: qt.id, type: 'tolerance', texte: qt.texte, choix: qt.choix, miseEnSituation: qt.id === 'q_chute',
      pourquoi: i === 0 ? '3 questions inspirées de Grable & Lytton (1999) pour situer ce que tu es prêt·e à risquer. Les points de chaque réponse sont un barème de l’équipe.' : null,
    }))
  }
  if (p.fonds_urgence == null) q.push({ id: 'fonds_urgence', type: 'choix', cible: 'profil', texte: "As-tu un fonds d'urgence (3 à 6 mois de dépenses) de côté ?",
    pourquoi: 'Sans réserve, une baisse peut forcer une vente au pire moment. C’est une des règles du Gardien.',
    choix: [['Oui', true], ['Non', false], ['Je ne sais pas', null]] })
  return q
}

function Bulle({ children }) {
  return (
    <div className="flex gap-3">
      <div className="mt-0.5 grid size-7 flex-none place-items-center rounded-full bg-muted"><Logo size={15} /></div>
      <div className="grid min-w-0 flex-1 gap-2 text-[15px] leading-relaxed">{children}</div>
    </div>
  )
}

function Reformulation({ profil, demande, actifs, compris }) {
  const actif = actifs.find((a) => a.ticker === demande.ticker)
  const poids = compris?.profil?.evaluation?.poids_pct
  const sujet = profil.nom && profil.nom !== 'Toi' ? `${profil.nom} envisage` : 'Tu envisages'
  const champs = Object.keys(compris?.profil?.extraits?.champs || {})
  return (
    <>
      <p className="text-[13px] font-medium text-muted-foreground">Voici ce que j'ai compris :</p>
      <div className="grid gap-2 rounded-lg border border-border bg-muted/60 px-4 py-3">
        <p>
          {sujet} de placer <strong>{demande.montant_cad != null ? dollars(demande.montant_cad) : 'un montant à préciser'}</strong> dans{' '}
          <strong>{actif ? `${actif.name} (${actif.ticker})` : 'un placement à préciser'}</strong>
          {poids != null && <>, soit <strong>{poids} %</strong> de l'épargne</>}
          {profil.horizon_ans != null && <>, avec un horizon de <strong>{ans(profil.horizon_ans)}</strong></>}.
        </p>
        {(profil.envie || profil.peur) && (
          <p className="grid gap-0.5 text-[13.5px]">
            {profil.envie && <span><strong className="font-semibold">Ce que tu veux :</strong> {profil.envie}</span>}
            {profil.peur && <span><strong className="font-semibold">Ce qui t'inquiète :</strong> {profil.peur}</span>}
          </p>
        )}
        {champs.length > 0 && (
          <p className="text-xs text-muted-foreground">
            Lu dans ta phrase par {compris.profil.extraits.source}, puis vérifié par le code : {champs.map((c) => LIBELLES_CHAMPS[c] || c).join(', ')}.
          </p>
        )}
      </div>
      {compris?.profil?.tensions?.map((t) => (
        <p key={t} className="rounded-lg border border-warn-bd bg-warn-bg px-3.5 py-2.5 text-[13.5px] text-warn">{t}</p>
      ))}
    </>
  )
}

function Question({ q, actifs, active, onRepondre }) {
  const [valeur, setValeur] = useState('')
  const [ticker, setTicker] = useState('')
  return (
    <>
      <p>{q.texte}</p>
      {q.pourquoi && <p className="text-[13px] text-muted-foreground">Pourquoi cette question ? {q.pourquoi}</p>}
      {q.miseEnSituation && <MiseEnSituation />}
      {active && (
        <div className="mt-1 flex flex-wrap items-center gap-2">
          {(q.type === 'choix' || q.type === 'tolerance') && q.choix.map(([libelle, v]) => (
            <Button key={libelle} variant="outline" className="h-10 px-4 text-sm" onClick={() => onRepondre(v, libelle)}>{libelle}</Button>
          ))}
          {q.type === 'montant' && (
            <>
              {q.suggestions.map((s) => (
                <Button key={s} variant="outline" className="h-10 px-4 text-sm" onClick={() => onRepondre(s, dollars(s))}>{dollars(s)}</Button>
              ))}
              <form className="flex w-full gap-2" onSubmit={(e) => { e.preventDefault(); const n = nombre(valeur); if (n != null && n >= 0) onRepondre(n, dollars(n)) }}>
                <Input type="number" min="0" step="500" inputMode="numeric" className="h-10 text-sm" aria-label="Autre montant en dollars canadiens"
                  placeholder="Autre montant ($ CA)" value={valeur} onChange={(e) => setValeur(e.target.value)} />
                <Button type="submit" variant="outline" className="h-10" disabled={valeur === ''}>Valider</Button>
              </form>
            </>
          )}
          {q.type === 'actif' && (
            <form className="flex w-full gap-2" onSubmit={(e) => {
              e.preventDefault()
              const a = actifs.find((x) => x.ticker === ticker)
              if (a) onRepondre(a.ticker, `${a.name} (${a.ticker})`)
            }}>
              <Select className="h-10" aria-label="Placement envisagé" value={ticker} onChange={(e) => setTicker(e.target.value)}>
                <option value="">Choisir un placement…</option>
                {actifs.map((a) => <option key={a.ticker} value={a.ticker}>{a.name} ({a.ticker})</option>)}
              </Select>
              <Button type="submit" variant="outline" className="h-10" disabled={!ticker}>Valider</Button>
            </form>
          )}
        </div>
      )}
    </>
  )
}

function Resume({ profil, setProfil, demande, setDemande, actifs, questions, compris, estPersona, lance, onLancer }) {
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
    ['Durée du placement', profil.horizon_ans != null ? ans(profil.horizon_ans) : null],
    ['Argent à ne jamais risquer', profil.somme_a_preserver_cad != null ? dollars(profil.somme_a_preserver_cad) : null],
    ['Retrait avant la fin', profil.retrait_prevu_ans == null ? 'Aucun' : `dans ${ans(profil.retrait_prevu_ans)}`],
    ["Réserve d'urgence", ouiNon(profil.fonds_urgence)],
    ['À éviter', profil.exclusions?.length ? profil.exclusions.map((s) => SECTEURS_FR[s] || s).join(', ') : 'Aucun secteur'],
    ['Déjà détenu', profil.portefeuille_actuel?.length ? profil.portefeuille_actuel.join(', ') : 'Rien de déclaré'],
  ]

  return (
    <div className="rounded-lg border border-border bg-card shadow-[0_1px_2px_rgba(0,0,0,.05)] sm:ml-10">
      <div className="flex items-start justify-between gap-3 px-4 pt-4">
        <div>
          <h2 className="text-[15px] font-semibold">Ta situation, en résumé</h2>
          <p className="mt-0.5 text-[13px] text-muted-foreground">Ce qui n'est pas indiqué le reste : je n'invente rien.</p>
        </div>
        <Button variant="ghost" size="sm" aria-expanded={edition} onClick={() => setEdition((v) => !v)}>{edition ? 'Terminer' : 'Modifier'}</Button>
      </div>

      {!edition ? (
        <dl className="mt-3 divide-y divide-border border-t border-border px-4 text-[14px]">
          {lignes.map(([k, v]) => (
            <div key={k} className="flex items-baseline justify-between gap-4 py-2.5">
              <dt className="text-muted-foreground">{k}</dt>
              <dd className={v ? 'text-right font-medium' : 'text-right text-muted-foreground/70'}>{v ?? 'Non précisé'}</dd>
            </div>
          ))}
        </dl>
      ) : (
        <div className="mt-3 grid gap-4 border-t border-border px-4 py-4">
          <div className="grid gap-1.5">
            <Label htmlFor="ticker">Placement envisagé</Label>
            <Select id="ticker" value={demande.ticker || ''} onChange={(e) => setDemande((d) => ({ ...d, ticker: e.target.value || null }))}>
              <option value="">Choisir…</option>
              {actifs.map((a) => <option key={a.ticker} value={a.ticker}>{a.name} ({a.ticker})</option>)}
            </Select>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="grid gap-1.5">
              <Label htmlFor="montant">Montant à placer ($ CA)</Label>
              <Input id="montant" type="number" min="0" step="500" value={demande.montant_cad ?? ''} onChange={(e) => setDemande((d) => ({ ...d, montant_cad: nombre(e.target.value) }))} />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="epargne">Épargne totale ($ CA)</Label>
              <Input id="epargne" type="number" min="0" step="1000" value={profil.epargne_totale_cad ?? ''} onChange={(e) => maj('epargne_totale_cad', nombre(e.target.value))} />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="preserver">Argent à ne jamais risquer ($ CA)</Label>
            <Input id="preserver" type="number" min="0" step="1000" value={profil.somme_a_preserver_cad ?? ''} onChange={(e) => maj('somme_a_preserver_cad', nombre(e.target.value))} />
          </div>
          <div className="grid gap-1.5">
            <div className="flex justify-between"><Label>Durée du placement</Label><span className="font-mono text-[13px]">{profil.horizon_ans != null ? ans(profil.horizon_ans) : '—'}</span></div>
            <Slider aria-label="Durée du placement" min={1} max={25} step={1} value={[profil.horizon_ans ?? 5]} onValueChange={([v]) => maj('horizon_ans', v)} />
          </div>
          <div className="grid gap-1.5">
            <div className="flex justify-between">
              <Label>Retrait avant la fin</Label>
              <span className="font-mono text-[13px]">{profil.retrait_prevu_ans == null ? 'Aucun' : `dans ${ans(profil.retrait_prevu_ans)}`}</span>
            </div>
            <div className="flex items-center gap-3">
              <Slider aria-label="Retrait prévu, en années" min={0} max={15} step={1} value={[profil.retrait_prevu_ans ?? 0]} onValueChange={([v]) => maj('retrait_prevu_ans', v || null)} />
              <Button variant="ghost" size="sm" onClick={() => maj('retrait_prevu_ans', null)}>Aucun</Button>
            </div>
          </div>
          <TroisEtats libelle="Réserve d'urgence (3 à 6 mois de dépenses) ?" valeur={profil.fonds_urgence} onChange={(v) => maj('fonds_urgence', v)} />
          <TroisEtats libelle="Revenu stable ?" valeur={profil.revenu_stable} onChange={(v) => maj('revenu_stable', v)} />
          <TroisEtats libelle="Dettes importantes (hors hypothèque) ?" valeur={profil.dettes_importantes} onChange={(v) => maj('dettes_importantes', v)} />
          <div className="grid gap-1.5">
            <span className="text-[13px] font-medium">Secteurs que tu veux éviter</span>
            <div className="flex flex-wrap gap-1.5">
              {secteurs.map((s) => <Choix key={s} actif={profil.exclusions.includes(s)} onClick={() => basculeExclusion(s)}>{SECTEURS_FR[s]}</Choix>)}
            </div>
          </div>
          <div className="grid gap-1.5">
            <span className="text-[13px] font-medium">Ce que tu détiens déjà</span>
            <div className="flex flex-wrap items-center gap-1.5">
              {profil.portefeuille_actuel.map((t) => (
                <Choix key={t} actif aria-label={`Retirer ${t}`} onClick={() => maj('portefeuille_actuel', profil.portefeuille_actuel.filter((x) => x !== t))}>{t} ×</Choix>
              ))}
              <Select className="h-8 w-auto" aria-label="Ajouter un placement détenu" value="" onChange={(e) => ajouterDetenu(e.target.value)}>
                <option value="">+ Ajouter</option>
                {actifs.map((a) => <option key={a.ticker} value={a.ticker}>{a.ticker}</option>)}
              </Select>
            </div>
          </div>
          <div className="grid gap-3">
            <div>
              <span className="text-[13px] font-medium">Ton rapport au risque</span>
              <p className="text-xs text-muted-foreground">3 questions adaptées de l'échelle de Grable &amp; Lytton (1999), barème de l'équipe.</p>
            </div>
            {questions.map((q) => (
              <fieldset key={q.id} className="m-0 border-0 p-0">
                <legend className="mb-1.5 text-[13px]">{q.texte}</legend>
                <div className="flex flex-wrap gap-1.5">
                  {q.choix.map(([libelle, valeur]) => (
                    <Choix key={libelle} actif={profil.reponses_tolerance?.[q.id] === valeur}
                      onClick={() => maj('reponses_tolerance', { ...profil.reponses_tolerance, [q.id]: valeur })}>{libelle}</Choix>
                  ))}
                </div>
              </fieldset>
            ))}
          </div>
        </div>
      )}

      <div className="mx-4 mb-4 grid gap-3 rounded-lg bg-muted px-3.5 py-3.5">
        <Jauge libelle="Ce que tu veux risquer (tolérance)" valeur={ev?.tolerance} retenue={ev?.limite === 'tolérance'}
          detail={ev?.perte_max_tolerance_pct == null ? 'Réponds aux 3 questions pour la mesurer.'
            : !reponsesDonnees && estPersona
              ? `Valeur fixée par le profil fictif (« ${profil.nom} »), pas une mesure. « Modifier » permet de répondre aux 3 questions.`
              : `Baisse acceptée : jusqu'à ${pct(ev.perte_max_tolerance_pct)} % de l'épargne (barème de l'équipe).`} />
        <Jauge libelle="Ce que ta situation permet (capacité)" valeur={ev?.capacite} retenue={ev?.limite === 'capacité'} detail={ev?.capacite_raisons?.join(' · ')} />
        {ev?.score_retenu != null && (
          <p className="rounded-md border border-border bg-card px-3 py-2 text-[13px]">
            On retient la plus basse : ta <strong>{ev.limite}</strong>, soit une baisse supportable de <strong>{pct(ev.perte_max_retenue_pct)} %</strong> de l'épargne.
          </p>
        )}
        <p className="text-xs text-muted-foreground">Barèmes : hypothèses de l'équipe, inspirées des Réformes axées sur le client (ACVM).</p>
        <SourcesCompactes ids={[...(registre?.justifications?.jauges?.references || []), ...(registre?.justifications?.questions?.references || [])]} />
      </div>

      {profil.citations?.length > 0 && (
        <div className="border-t border-border px-4 py-3 text-[13px]">
          <span className="text-muted-foreground">{estPersona ? 'Phrases types du profil (écrites par l’équipe) : ' : 'Tes mots, gardés tels quels : '}</span>
          {profil.citations.map((c, i) => (
            <span key={c}>« <mark className="rounded-sm bg-mark px-0.5 text-inherit">{c}</mark> »{i < profil.citations.length - 1 ? ' ' : ''}</span>
          ))}
          <p className="mt-1 text-xs text-muted-foreground">Ils seront remis à côté des chiffres dans le verdict : c'est le miroir.</p>
        </div>
      )}

      {compris?.questions?.length > 0 && (
        <div className="border-t border-border px-4 py-3 text-[13px]">
          <strong className="font-semibold">Encore à préciser :</strong>
          <ul className="mt-1 list-disc pl-5">{compris.questions.map((q) => <li key={q}>{q}</li>)}</ul>
        </div>
      )}

      <div className="border-t border-border p-4">
        {lance ? (
          <p className="flex items-center gap-2 text-[13.5px]"><Check className="size-4" /> Vérification lancée.</p>
        ) : (
          <>
            <Button size="lg" className="w-full" disabled={!demande.ticker} onClick={() => { setEdition(false); onLancer() }}>
              C'est correct, lancer la vérification <ArrowRight className="size-4" />
            </Button>
            {!demande.ticker && <p className="mt-2 text-xs text-muted-foreground">Choisis d'abord un placement avec « Modifier ».</p>}
          </>
        )}
      </div>
    </div>
  )
}

export default function Conversation({ personas, actifs, questions, profil, setProfil, demande, setDemande, onPhase, onLancer, lance }) {
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
  useEffect(() => { if (messages.length) bas.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }) }, [messages, phase])

  // Au résumé, chaque correction relance le Profileur (sans relire la phrase) pour mettre à jour les jauges.
  useEffect(() => {
    if (phase !== 'resume') return undefined
    clearTimeout(minuterie.current)
    minuterie.current = setTimeout(() => { api.comprendre(profil, { ...demande, texte_lu: true }).then(setCompris).catch(() => {}) }, 300)
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
      ajouter({ de: 'af', type: 'compris', profil: lu.p, demande: lu.d, compris: r })
      const restantes = questionsManquantes(lu.p, lu.d, questions)
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
    <div className="grid gap-5">
      {phase === 'saisie' && messages.length === 0 && (
        <div className="mt-3">
          <h1 className="text-[28px] font-bold leading-tight tracking-[-0.02em]">Que veux-tu faire de ton argent ?</h1>
          <p className="mt-2 text-[15px] text-muted-foreground">Écris-le simplement, comme tu le dirais à un ami. Pas besoin de connaître la finance.</p>
        </div>
      )}

      {messages.length > 0 && (
        <div className="grid gap-5">
          {messages.map((m) => (m.de === 'moi' ? (
            <div key={m.id} className="flex justify-end">
              <p className="max-w-[90%] rounded-lg bg-muted px-4 py-3 text-[15px] leading-relaxed">{m.texte}</p>
            </div>
          ) : (
            <Bulle key={m.id}>
              {m.type === 'compris' && <Reformulation profil={m.profil} demande={m.demande} actifs={actifs} compris={m.compris} />}
              {m.type === 'question' && (
                <Question q={m.q} actifs={actifs} active={phase === 'questions' && !m.repondue} onRepondre={(v, libelle) => repondre(m.q, v, libelle)} />
              )}
              {!m.type && <p>{m.texte}</p>}
            </Bulle>
          )))}
          {phase === 'lecture' && (
            <div className="flex items-center gap-3 pl-10 text-[14px] text-muted-foreground">
              <span className="size-4 animate-spin rounded-full border-2 border-border border-t-primary" /> Je lis ta demande…
            </div>
          )}
          {phase === 'resume' && (
            <Resume profil={profil} setProfil={setProfil} demande={demande} setDemande={setDemande} actifs={actifs}
              questions={questions} compris={compris} estPersona={estPersona} lance={lance} onLancer={onLancer} />
          )}
          <div ref={bas} />
        </div>
      )}

      {phase === 'saisie' && (
        <>
          <form onSubmit={(e) => { e.preventDefault(); envoyer() }}>
            <label htmlFor="texte-libre" className="sr-only">Ta demande, avec tes mots</label>
            <Textarea id="texte-libre" ref={zone} rows={4} value={brouillon} className="min-h-[112px] p-3 text-[15px]"
              onChange={(e) => { setBrouillon(e.target.value); if (!e.target.value) setPersonaChoisie(null) }}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); envoyer() } }}
              placeholder="Ex. : je voudrais mettre 10 000 $ en Bitcoin. J'ai 40 000 $ d'épargne. Mais j'ai peur de tout perdre." />
            <div className="mt-3 flex items-center justify-between gap-3">
              <span className="text-xs text-muted-foreground">Une phrase suffit.</span>
              <Button type="submit" className="h-10 px-4 text-sm" disabled={!brouillon.trim()}>Continuer <ArrowRight className="size-4" /></Button>
            </div>
          </form>

          {messages.length === 0 && personas && (
            <div className="mt-3">
              <div className="mb-2 text-[13px] font-medium">Pas d'idée ? Essaie avec un profil du défi</div>
              <ul className="divide-y divide-border overflow-hidden rounded-lg border border-border">
                {Object.entries(personas).map(([cle, pe]) => (
                  <li key={cle}>
                    <button type="button" onClick={() => choisirExemple(cle)}
                      className={`flex w-full cursor-pointer items-center justify-between gap-3 px-3.5 py-3 text-left text-[14px] transition-colors hover:bg-muted/60 ${personaChoisie === cle ? 'bg-muted/60' : ''}`}>
                      <span>{EXEMPLES[cle] || pe.demande.texte}<span className="ml-2 text-xs text-muted-foreground">{pe.profil.nom}, {pe.profil.age} ans</span></span>
                      <ArrowRight className="size-4 flex-none text-muted-foreground" />
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  )
}
