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

export function PuceNiveau({ niveau }) {
  const n = NIVEAUX[niveau] || NIVEAUX.non_evaluee
  return <span className={`puce-niveau ${n.classe}`}>{n.libelle}</span>
}

// Issue d'une vérification du Sceptique : elle lui donne raison, elle l'écarte, ou elle note une limite de méthode.
const ISSUES = {
  confirmee: { libelle: 'Objection confirmée', classe: 'warn' },
  ecartee: { libelle: 'Objection écartée', classe: 'ok' },
  limite: { libelle: 'Limite notée', classe: 'grey' },
}

export function PuceIssue({ issue }) {
  const i = ISSUES[issue]
  return i ? <span className={`puce-niveau ${i.classe}`}>{i.libelle}</span> : null
}

const TYPES = { FAIT: 'Fait', HYPOTHESE: 'Hypothèse', SCENARIO: 'Scénario fictif' }

export function Etiquette({ type }) {
  return <span className={`etiquette t-${(type || '').toLowerCase()}`}>{TYPES[type] || type}</span>
}

// Un seul bouton « i » par phrase ou par règle : l'écran reste simple, le détail s'ouvre au clic.
export function PucesFaits({ ids, ouvrir }) {
  const liste = [...new Set((ids || []).filter(Boolean))]
  if (!liste.length) return null
  const titre = liste.length > 1 ? "D'où viennent ces chiffres ?" : "D'où vient ce chiffre ?"
  return (
    <button type="button" className="bouton-info" onClick={() => ouvrir(liste)} aria-label={titre} title={titre}>
      i
    </button>
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
