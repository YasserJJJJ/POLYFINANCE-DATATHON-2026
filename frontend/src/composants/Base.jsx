// Petits composants partagés : puces de verdict, étiquettes de fait, jauges.

export const ETATS = {
  coherent: { libelle: 'Cohérent', classe: 'ok' },
  ajustement: { libelle: 'Cohérent avec ajustement', classe: 'warn' },
  incoherent: { libelle: 'Incohérent avec ta situation', classe: 'bad' },
  indetermine: { libelle: 'Impossible de conclure', classe: 'grey' },
}

export const NIVEAUX = {
  ok: { libelle: 'Respectée', classe: 'ok' },
  orange: { libelle: 'À ajuster', classe: 'warn' },
  rouge: { libelle: 'Bloquante', classe: 'bad' },
  gris: { libelle: 'Information manquante', classe: 'grey' },
  non_evaluee: { libelle: 'Non évaluée', classe: 'muted' },
}

export function PuceVerdict({ etat, grand = false, libelle }) {
  const e = ETATS[etat] || ETATS.indetermine
  return (
    <span className={`puce-verdict ${e.classe} ${grand ? 'grand' : ''}`}>
      <i aria-hidden="true" />
      {libelle || e.libelle}
    </span>
  )
}

const ICONES = {
  coherent: 'm5 12 5 5 9-10',
  ajustement: 'M12 8v5M12 17h.01',
  incoherent: 'M18 6 6 18M6 6l12 12',
  indetermine: 'M9 9a3 3 0 1 1 4.5 2.6c-1 .6-1.5 1.1-1.5 2.4M12 17h.01',
}

// Pastille ronde du bandeau de verdict : coche, point d'exclamation, croix ou point d'interrogation.
export function IconeEtat({ etat }) {
  return (
    <span className="verdict-icone" aria-hidden="true">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6"
        strokeLinecap="round" strokeLinejoin="round">
        <path d={ICONES[etat] || ICONES.indetermine} />
      </svg>
    </span>
  )
}

export function PuceNiveau({ niveau }) {
  const n = NIVEAUX[niveau] || NIVEAUX.non_evaluee
  return <span className={`puce-niveau ${n.classe}`}>{n.libelle}</span>
}

const TYPES = { FAIT: 'Fait', HYPOTHESE: 'Hypothèse', SCENARIO: 'Scénario fictif' }

export function Etiquette({ type }) {
  return <span className={`etiquette t-${(type || '').toLowerCase()}`}>{TYPES[type] || type}</span>
}

export function PucesFaits({ ids, ouvrir }) {
  if (!ids?.length) return null
  return (
    <span className="puces-faits">
      {ids.filter(Boolean).map((id) => (
        <button key={id} type="button" className="puce-fait" onClick={() => ouvrir(id)}>
          {id}
        </button>
      ))}
    </span>
  )
}

export function Jauge({ libelle, valeur, retenue, detail }) {
  const v = valeur ?? 0
  return (
    <div className={`jauge ${retenue ? 'retenue' : ''}`}>
      <div className="jauge-tete">
        <span>{libelle}</span>
        <strong>{valeur == null ? '—' : `${Math.round(v)}/100`}</strong>
      </div>
      <div className="jauge-piste" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={v} aria-label={libelle}>
        <div className="jauge-rempli" style={{ width: `${v}%` }} />
      </div>
      {detail && <p className="jauge-detail">{detail}</p>}
    </div>
  )
}
