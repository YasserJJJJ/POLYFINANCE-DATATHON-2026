import { useEffect, useState } from 'react'
import { api } from '@/api.js'
import { PucesFaits } from './Base.jsx'

const L = 640, H = 220, M = { g: 44, d: 12, h: 16, b: 28 }

// La pire chute observée du placement, en $ CA (série hebdomadaire de /api/serie, base 100).
export default function GraphiqueChute({ ticker, faitId, ouvrir }) {
  const [serie, setSerie] = useState(null)
  useEffect(() => { api.serie(ticker).then(setSerie).catch(() => setSerie(null)) }, [ticker])
  if (!serie) return <p className="py-10 text-center text-[13px] text-muted-foreground">Chargement du graphique…</p>

  const pts = serie.points
  const vals = pts.map((p) => p.valeur)
  const min = Math.min(...vals), max = Math.max(...vals)
  const x = (i) => M.g + (i / (pts.length - 1)) * (L - M.g - M.d)
  const y = (v) => M.h + (1 - (v - min) / (max - min || 1)) * (H - M.h - M.b)
  const pc = serie.pire_chute
  const idx = (date) => { const i = pts.findIndex((p) => p.date >= date); return i === -1 ? pts.length - 1 : i }
  const iS = idx(pc.date_sommet), iC = idx(pc.date_creux)
  const iR = pc.date_retour ? idx(pc.date_retour) : pts.length - 1
  const chemin = pts.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(p.valeur).toFixed(1)}`).join(' ')
  const zone = `M${x(iS)},${y(pts[iS].valeur)} ` + pts.slice(iS, iR + 1).map((p, k) => `L${x(iS + k)},${y(p.valeur)}`).join(' ')
    + ` L${x(iR)},${y(pts[iS].valeur)} Z`
  const annees = [...new Set(pts.map((p) => p.date.slice(0, 4)))]
  const graduations = [min, (min + max) / 2, max]
  const chute = Number(pc.pire_chute_pct).toLocaleString('fr-CA')

  return (
    <figure className="m-0 grid gap-2">
      <svg viewBox={`0 0 ${L} ${H}`} role="img" className="block h-auto w-full"
        aria-label={`${ticker} : pire chute de ${chute} % entre ${pc.date_sommet} et ${pc.date_creux}`}>
        {graduations.map((g) => (
          <g key={g}>
            <line x1={M.g} x2={L - M.d} y1={y(g)} y2={y(g)} stroke="var(--border)" />
            <text x={M.g - 6} y={y(g) + 4} textAnchor="end" fontSize="11" fill="var(--muted-foreground)">{Math.round(g)}</text>
          </g>
        ))}
        {annees.map((a) => {
          const i = pts.findIndex((p) => p.date.startsWith(a))
          return i > 0 && <text key={a} x={x(i)} y={H - 8} textAnchor="middle" fontSize="11" fill="var(--muted-foreground)">{a}</text>
        })}
        <path d={zone} fill="var(--bad)" fillOpacity="0.1" />
        <path d={chemin} fill="none" stroke="var(--foreground)" strokeWidth="1.8" strokeLinejoin="round" />
        <circle cx={x(iS)} cy={y(pts[iS].valeur)} r="4" fill="var(--foreground)" />
        <circle cx={x(iC)} cy={y(pts[iC].valeur)} r="5" fill="var(--bad)" />
        <text x={x(iC)} y={y(pts[iC].valeur) + 18} textAnchor="middle" fontSize="12" fontWeight="700" fill="var(--bad)">{chute} %</text>
      </svg>
      <figcaption className="text-xs text-muted-foreground">
        Valeur de {ticker} en $ CA, base 100 au 2021-11-12, tracé hebdomadaire (le pourcentage de la pire chute est calculé
        sur les prix quotidiens : le tracé lisse le creux). Zone colorée : du sommet ({pc.date_sommet})
        {pc.recupere ? ` au retour au sommet (${pc.date_retour})` : " à aujourd'hui, sommet non retrouvé"}.{' '}
        {faitId && <PucesFaits ids={[faitId]} ouvrir={ouvrir} />}
      </figcaption>
    </figure>
  )
}
