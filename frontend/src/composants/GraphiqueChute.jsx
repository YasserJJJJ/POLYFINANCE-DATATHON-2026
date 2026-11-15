import { useEffect, useState } from 'react'
import { api } from '../api.js'

const L = 640, H = 220, M = { g: 44, d: 12, h: 16, b: 28 }

export default function GraphiqueChute({ ticker, faitId, ouvrir }) {
  const [serie, setSerie] = useState(null)
  useEffect(() => { api.serie(ticker).then(setSerie).catch(() => setSerie(null)) }, [ticker])
  if (!serie) return <div className="graphe-vide muted">Chargement du graphique…</div>

  const pts = serie.points
  const vals = pts.map((p) => p.valeur)
  const min = Math.min(...vals), max = Math.max(...vals)
  const x = (i) => M.g + (i / (pts.length - 1)) * (L - M.g - M.d)
  const y = (v) => M.h + (1 - (v - min) / (max - min || 1)) * (H - M.h - M.b)
  const pc = serie.pire_chute
  const idx = (date) => {
    const i = pts.findIndex((p) => p.date >= date)
    return i === -1 ? pts.length - 1 : i
  }
  const iS = idx(pc.date_sommet), iC = idx(pc.date_creux)
  const iR = pc.date_retour ? idx(pc.date_retour) : pts.length - 1
  const chemin = pts.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(p.valeur).toFixed(1)}`).join(' ')
  const zone = `M${x(iS)},${y(pts[iS].valeur)} ` + pts.slice(iS, iR + 1).map((p, k) => `L${x(iS + k)},${y(p.valeur)}`).join(' ')
    + ` L${x(iR)},${y(pts[iS].valeur)} Z`
  const annees = [...new Set(pts.map((p) => p.date.slice(0, 4)))]
  const graduations = [min, (min + max) / 2, max]

  return (
    <figure className="graphe">
      <svg viewBox={`0 0 ${L} ${H}`} role="img"
        aria-label={`${ticker} : pire chute de ${pc.pire_chute_pct} % entre ${pc.date_sommet} et ${pc.date_creux}`}>
        {graduations.map((g) => (
          <g key={g}>
            <line x1={M.g} x2={L - M.d} y1={y(g)} y2={y(g)} className="grille" />
            <text x={M.g - 6} y={y(g) + 4} textAnchor="end" className="txt-graphe">{Math.round(g)}</text>
          </g>
        ))}
        {annees.map((a) => {
          const i = pts.findIndex((p) => p.date.startsWith(a))
          return i > 0 && <text key={a} x={x(i)} y={H - 8} textAnchor="middle" className="txt-graphe">{a}</text>
        })}
        <path d={zone} className="zone-chute" />
        <path d={chemin} className="ligne-prix" />
        <circle cx={x(iS)} cy={y(pts[iS].valeur)} r="4" className="point-sommet" />
        <circle cx={x(iC)} cy={y(pts[iC].valeur)} r="5" className="point-chute" />
        <text x={x(iC)} y={y(pts[iC].valeur) + 18} textAnchor="middle" className="txt-graphe fort">{pc.pire_chute_pct} %</text>
      </svg>
      <figcaption>
        Valeur de {ticker} en $ CA, base 100 au 2021-11-12, prix hebdomadaire. Zone colorée : du sommet ({pc.date_sommet})
        {pc.recupere ? ` au retour au sommet (${pc.date_retour})` : ' à aujourd\'hui, sommet non retrouvé'}.{' '}
        {faitId && <button type="button" className="puce-fait" onClick={() => ouvrir(faitId)}>{faitId}</button>}
      </figcaption>
    </figure>
  )
}
