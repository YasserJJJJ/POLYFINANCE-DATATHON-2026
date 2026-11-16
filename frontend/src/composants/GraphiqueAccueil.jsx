// Illustration de l'accueil : de vraies bougies mensuelles du jeu de départ (calculées par l'API), dessinées
// par le site. Elle montre le passé, ne prédit rien et ne sert à aucun verdict.
import { useEffect, useState } from 'react'
import { api } from '../api.js'

const INDICES = [
  ['XIU.TO', 'TSX 60'],
  ['SPY', 'S&P 500'],
  ['GLD', 'Or'],
  ['BTC-USD', 'Bitcoin'],
]
const L = 620, H = 300, M = { g: 8, d: 46, h: 14, b: 26 }
const fr = (n, d = 1) => Number(n).toLocaleString('fr-CA', { minimumFractionDigits: d, maximumFractionDigits: d }).replace('-', '−')
const MOIS = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
const libelleMois = (m) => `${MOIS[Number(m.slice(5, 7)) - 1]} ${m.slice(0, 4)}`

function moyenneMobile(bougies, n = 6) {
  return bougies.map((_, i) => {
    if (i < n - 1) return null
    const fenetre = bougies.slice(i - n + 1, i + 1)
    return fenetre.reduce((s, b) => s + b.c, 0) / n
  })
}

export default function GraphiqueAccueil({ initiales = {} }) {
  const [donnees, setDonnees] = useState(initiales)
  const [choisi, setChoisi] = useState(INDICES[0][0])
  const [survol, setSurvol] = useState(null)

  useEffect(() => {
    let actuel = true
    INDICES.forEach(([t]) => api.bougies(t)
      .then((d) => actuel && setDonnees((avant) => ({ ...avant, [t]: d })))
      .catch(() => {}))
    return () => { actuel = false }
  }, [])

  const d = donnees[choisi]
  const disponibles = INDICES.filter(([t]) => donnees[t])
  if (!disponibles.length) return <div className="accueil-graphe accueil-graphe-vide" aria-hidden="true" />

  const bougies = d?.bougies || []
  const hauts = bougies.map((b) => b.h), bas = bougies.map((b) => b.b)
  const min = Math.min(...bas), max = Math.max(...hauts)
  const marge = (max - min) * 0.06 || 1
  const y = (v) => M.h + (1 - (v - (min - marge)) / (max - min + 2 * marge)) * (H - M.h - M.b)
  const pas = (L - M.g - M.d) / Math.max(bougies.length, 1)
  const x = (i) => M.g + pas * (i + 0.5)
  const largeur = Math.max(2, pas * 0.62)
  const mm = moyenneMobile(bougies)
  const cheminMM = mm.map((v, i) => (v == null ? null : `${x(i).toFixed(1)},${y(v).toFixed(1)}`)).filter(Boolean)
  const graduations = [0, 1, 2, 3].map((k) => min + ((max - min) * k) / 3)
  const annees = bougies.map((b, i) => [b.mois, i]).filter(([m]) => m.endsWith('-01'))
  const derniere = bougies[bougies.length - 1]
  const lue = survol != null ? bougies[survol] : null

  return (
    <figure className="accueil-graphe">
      <div className="accueil-indices" role="group" aria-label="Choisir l'indice affiché">
        {INDICES.map(([t, nom]) => {
          const v = donnees[t]?.variation_pct
          return (
            <button key={t} type="button" className={`indice ${t === choisi ? 'actif' : ''}`} aria-pressed={t === choisi}
              disabled={!donnees[t]} onClick={() => { setChoisi(t); setSurvol(null) }}>
              <span className="indice-nom">{nom}</span>
              <span className="indice-ticker">{t}</span>
              {v != null && <span className={`indice-var ${v >= 0 ? 'hausse' : 'baisse'}`}>{v >= 0 ? '▲' : '▼'} {fr(Math.abs(v))} % <small>depuis {donnees[t].bougies[0].mois.slice(0, 4)}</small></span>}
            </button>
          )
        })}
      </div>

      {d && (
        <svg key={choisi} viewBox={`0 0 ${L} ${H}`} className="accueil-svg" role="img"
          aria-label={`${d.nom} : bougies mensuelles en CAD, base 100, de ${libelleMois(bougies[0].mois)} à ${libelleMois(derniere.mois)}`}
          onMouseLeave={() => setSurvol(null)}>
          {graduations.map((g) => (
            <g key={g}>
              <line x1={M.g} x2={L - M.d} y1={y(g)} y2={y(g)} className="ag-grille" />
              <text x={L - M.d + 6} y={y(g) + 4} className="ag-txt">{Math.round(g)}</text>
            </g>
          ))}
          <line x1={M.g} x2={L - M.d} y1={y(100)} y2={y(100)} className="ag-base" />
          {annees.map(([m, i]) => (
            <g key={m}>
              <line x1={x(i) - pas / 2} x2={x(i) - pas / 2} y1={M.h} y2={H - M.b} className="ag-annee" />
              <text x={x(i) - pas / 2 + 4} y={H - 8} className="ag-txt">{m.slice(0, 4)}</text>
            </g>
          ))}
          {bougies.map((b, i) => {
            const hausse = b.c >= b.o
            const corps = Math.max(1.5, Math.abs(y(b.o) - y(b.c)))
            return (
              <g key={b.mois} className={`bougie ${hausse ? 'hausse' : 'baisse'} ${survol === i ? 'lue' : ''}`}
                style={{ animationDelay: `${i * 14}ms` }} onMouseEnter={() => setSurvol(i)}>
                <rect x={x(i) - pas / 2} y={M.h} width={pas} height={H - M.h - M.b} className="ag-zone" />
                <line x1={x(i)} x2={x(i)} y1={y(b.h)} y2={y(b.b)} className="meche" />
                <rect x={x(i) - largeur / 2} y={Math.min(y(b.o), y(b.c))} width={largeur} height={corps} className="corps" />
              </g>
            )
          })}
          {cheminMM.length > 1 && <polyline points={cheminMM.join(' ')} className="ag-moyenne" />}
          <g className="ag-dernier">
            <line x1={M.g} x2={L - M.d} y1={y(derniere.c)} y2={y(derniere.c)} />
            <rect x={L - M.d + 1} y={y(derniere.c) - 9} width={M.d - 2} height={18} />
            <text x={L - M.d + 6} y={y(derniere.c) + 4}>{fr(derniere.c)}</text>
          </g>
        </svg>
      )}

      <figcaption className="accueil-legende">
        {lue
          ? <span><strong>{libelleMois(lue.mois)}</strong> · première {fr(lue.o)} · plus haute {fr(lue.h)} · plus basse {fr(lue.b)} · dernière {fr(lue.c)}</span>
          : <span><strong>{d?.nom}</strong> · bougies mensuelles en CAD, base 100 · <i className="ag-cle" /> moyenne sur 6 mois</span>}
        <span className="muted">Données du jeu de départ, 2021–2026. Le passé, pas une prévision.</span>
      </figcaption>
    </figure>
  )
}
