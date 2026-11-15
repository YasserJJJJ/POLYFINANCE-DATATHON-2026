// Petits éléments partagés : puces de verdict et de règle, étiquettes FAIT / HYPOTHÈSE / SCÉNARIO, faits cliquables, jauges.
import { cn } from '@/lib/utils'

export const ETATS = {
  coherent: { libelle: 'Cohérent', ton: 'ok' },
  ajustement: { libelle: 'Cohérent avec ajustement', ton: 'warn' },
  incoherent: { libelle: 'Incohérent avec ta situation', ton: 'bad' },
  indetermine: { libelle: 'Impossible de conclure', ton: 'grey' },
}

export const NIVEAUX = {
  ok: { libelle: 'Respectée', ton: 'ok' },
  orange: { libelle: 'À ajuster', ton: 'warn' },
  rouge: { libelle: 'Bloquante', ton: 'bad' },
  gris: { libelle: 'Information manquante', ton: 'grey' },
  non_evaluee: { libelle: 'Non évaluée', ton: 'muted' },
}

// Classes complètes (Tailwind ne lit que des noms de classes entiers).
export const TONS = {
  ok: { puce: 'bg-ok-bg text-ok border-ok-bd', point: 'bg-ok', bord: 'border-ok', fond: 'bg-ok-bg', texte: 'text-ok' },
  warn: { puce: 'bg-warn-bg text-warn border-warn-bd', point: 'bg-warn', bord: 'border-warn', fond: 'bg-warn-bg', texte: 'text-warn' },
  bad: { puce: 'bg-bad-bg text-bad border-bad-bd', point: 'bg-bad', bord: 'border-bad', fond: 'bg-bad-bg', texte: 'text-bad' },
  grey: { puce: 'bg-grey-bg text-grey border-grey-bd', point: 'bg-grey', bord: 'border-grey', fond: 'bg-grey-bg', texte: 'text-grey' },
  muted: { puce: 'bg-muted text-muted-foreground border-border', point: 'bg-muted-foreground', bord: 'border-border', fond: 'bg-muted', texte: 'text-muted-foreground' },
}

export function PuceVerdict({ etat, grand = false, libelle }) {
  const e = ETATS[etat] || ETATS.indetermine
  const t = TONS[e.ton]
  return (
    <span className={cn('inline-flex items-center gap-1.5 rounded-full border font-semibold', t.puce,
      grand ? 'px-3 py-1 text-sm' : 'px-2.5 py-0.5 text-xs')}>
      <i aria-hidden="true" className={cn('rounded-full', t.point, grand ? 'size-2' : 'size-[7px]')} />
      {libelle || e.libelle}
    </span>
  )
}

export function PuceNiveau({ niveau }) {
  const n = NIVEAUX[niveau] || NIVEAUX.non_evaluee
  return <span className={cn('whitespace-nowrap rounded-full border px-2 py-px text-[11.5px] font-medium', TONS[n.ton].puce)}>{n.libelle}</span>
}

const TYPES = {
  FAIT: ['Fait', 'text-t-fait border-t-fait'],
  HYPOTHESE: ['Hypothèse', 'text-t-hyp border-t-hyp border-dashed'],
  SCENARIO: ['Scénario fictif', 'text-t-scen border-t-scen border-dotted'],
}

export function Etiquette({ type }) {
  const [libelle, classes] = TYPES[type] || [type, 'text-muted-foreground border-border']
  return (
    <span className={cn('inline-block whitespace-nowrap rounded border px-1.5 py-px align-[1px] text-[10.5px] font-semibold uppercase tracking-[0.05em]', classes)}>
      {libelle}
    </span>
  )
}

export function PucesFaits({ ids, ouvrir }) {
  const liste = [...new Set((ids || []).filter(Boolean))]
  if (!liste.length) return null
  return (
    <span className="inline-flex flex-wrap gap-1 align-middle">
      {liste.map((id) => (
        <button key={id} type="button" onClick={() => ouvrir(id)} title={`Voir la source de ${id}`}
          className="cursor-pointer rounded-md border border-input bg-card px-1.5 py-px font-mono text-[11.5px] hover:bg-muted">
          {id}
        </button>
      ))}
    </span>
  )
}

export function Jauge({ libelle, valeur, retenue, detail }) {
  const v = Math.max(0, Math.min(100, valeur ?? 0))
  return (
    <div>
      <div className="mb-1.5 flex justify-between gap-3 text-[13px]">
        <span className={cn(retenue && 'font-semibold')}>{libelle}</span>
        <span className="font-mono tabular-nums">{valeur == null ? '—' : `${Math.round(v)}/100`}</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full border border-border bg-muted" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={v} aria-label={libelle}>
        <div className={cn('h-full rounded-full transition-[width] duration-300', retenue ? 'bg-primary' : 'bg-muted-foreground/60')} style={{ width: `${v}%` }} />
      </div>
      {detail && <p className="mt-1.5 text-xs text-muted-foreground">{detail}</p>}
    </div>
  )
}

export const ans = (n) => `${n} an${n > 1 ? 's' : ''}`
export const pct = (n) => Number(n).toLocaleString('fr-CA', { maximumFractionDigits: 1 })
