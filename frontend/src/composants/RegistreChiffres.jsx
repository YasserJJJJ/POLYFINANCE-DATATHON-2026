// Tous les chiffres du dossier, compacts : regroupés par nature (mesuré, hypothèse, scénario), une ligne chacun,
// valeur lisible à droite et bouton « i » pour la source et la méthode. Aucun défilement horizontal.
import { dollars } from '../api.js'
import { pourClient } from '../affichage.js'
import { Etiquette, PucesFaits } from './Base.jsx'

const ORDRE = ['FAIT', 'HYPOTHESE', 'SCENARIO']
const nf = (n, d) => Number(n).toLocaleString('fr-CA', { maximumFractionDigits: d }).replace('-', '−')

function nombre(v, unite) {
  if (unite === '$') return dollars(v).replace('-', '−')
  if (unite === 'fraction') return `${nf(v * 100, 1)} %`
  return `${nf(v, Math.abs(v) < 1 ? 2 : 1)}${unite ? ` ${unite}` : ''}`
}

// Valeur courte pour la ligne ; `long` reçoit un texte à montrer sous le libellé, replié sur deux lignes.
export function valeurCompacte(f) {
  const v = f.valeur
  if (v == null) return { court: '—' }
  if (typeof v === 'number') return { court: nombre(v, f.unite) }
  if (typeof v === 'boolean') return { court: v ? 'oui' : 'non' }
  if (Array.isArray(v)) return { court: `${v.length} élément(s)`, long: v.map(String).join(' · ') }
  if (typeof v === 'object') {
    const e = Object.entries(v)
    if (v.debut && v.fin) return { court: `${v.debut} → ${v.fin}`, long: v.observations ? `${v.observations} séances communes` : null }
    if (e.length && e.every(([, x]) => typeof x === 'number')) {
      return { court: null, long: e.map(([k, x]) => `${k} ${nombre(x, f.unite)}`).join(' · ') }
    }
    return { court: 'voir le détail', long: typeof v.explication === 'string' ? v.explication : null }
  }
  const t = String(v)
  return t.length > 40 ? { court: null, long: t } : { court: t }
}

export default function RegistreChiffres({ faits, surligne = [], ouvrir }) {
  const groupes = ORDRE.map((type) => [type, faits.filter((f) => f.type === type)])
    .concat([['AUTRE', faits.filter((f) => !ORDRE.includes(f.type))]])
    .filter(([, liste]) => liste.length)
  return (
    <div className="registre-chiffres">
      {groupes.map(([type, liste]) => (
        <section key={type} className="rc-groupe" aria-label={`${type} : ${liste.length} chiffre(s)`}>
          <h4 className="rc-tete">{type === 'AUTRE' ? 'Autres' : <Etiquette type={type} />}<span className="muted">{liste.length}</span></h4>
          <ul className="rc-liste">
            {liste.map((f) => {
              const { court, long } = valeurCompacte(f)
              return (
                <li key={f.id} data-fait={f.id} className={surligne.includes(f.id) ? 'surligne' : ''}>
                  <span className="rc-libelle">{pourClient(f.libelle)}
                    {long && <span className="rc-long" title={pourClient(long)}>{pourClient(long)}</span>}</span>
                  {court && <span className="rc-valeur nombre">{pourClient(court)}</span>}
                  <PucesFaits ids={[f.id]} ouvrir={ouvrir} />
                </li>
              )
            })}
          </ul>
        </section>
      ))}
    </div>
  )
}
