// Éditions : chaque analyse reçue est gardée telle quelle dans le navigateur. On peut relire une édition
// antérieure (archive) et voir ce qu'une modification a changé. Rien n'est recalculé ici : on compare
// deux dossiers rendus par le moteur, règle par règle (par code) et mesure par mesure (champs du contrat K3).
import { dollars } from '../api.js'
import { ETATS, NIVEAUX } from './Base.jsx'

const fr = (n, d = 1) => Number(n).toLocaleString('fr-CA', { minimumFractionDigits: d, maximumFractionDigits: d }).replace('-', '−')

const MESURES = [
  ['pire_chute_pct', 'Pire baisse du portefeuille, après la demande', (v) => `${fr(v)} %`],
  ['volatilite_pct', 'Volatilité du portefeuille, après la demande', (v) => `${fr(v)} %`],
  ['valeur_finale_cad', 'Valeur en fin de période observée', (v) => dollars(Math.round(v))],
]

export function resumeEdition(e) {
  const dm = e.dossier.demande || {}
  return [dm.ticker || 'sans placement choisi', dm.montant_cad != null ? dollars(dm.montant_cad) : null,
    e.dossier.profil?.retrait_prevu_ans != null ? `retrait dans ${e.dossier.profil.retrait_prevu_ans} an(s)` : null]
    .filter(Boolean).join(' · ')
}

// Ce qui diffère entre deux dossiers. Les numéros F-n changent d'une analyse à l'autre : on ne s'en sert pas.
export function differences(avant, apres) {
  const lignes = []
  if (avant.verdict.etat !== apres.verdict.etat) {
    lignes.push({ cle: 'Avis', de: ETATS[avant.verdict.etat]?.libelle, a: ETATS[apres.verdict.etat]?.libelle })
  }
  const da = avant.demande || {}, db = apres.demande || {}
  if (da.ticker !== db.ticker) lignes.push({ cle: 'Placement', de: da.ticker || 'aucun', a: db.ticker || 'aucun' })
  if (da.montant_cad !== db.montant_cad) lignes.push({ cle: 'Montant', de: dollars(da.montant_cad), a: dollars(db.montant_cad) })
  const codes = [...new Set([...avant.regles, ...apres.regles].map((r) => r.code))]
  let inchangees = 0
  codes.forEach((c) => {
    const x = avant.regles.find((r) => r.code === c), y = apres.regles.find((r) => r.code === c)
    if (x?.niveau === y?.niveau) { inchangees += 1; return }
    lignes.push({ cle: `Règle « ${(y || x).libelle} »`, de: x ? NIVEAUX[x.niveau]?.libelle : 'non évaluée', a: y ? NIVEAUX[y.niveau]?.libelle : 'non évaluée' })
  })
  const ka = avant.comparaison, kb = apres.comparaison
  if (ka?.disponible && kb?.disponible) {
    MESURES.forEach(([champ, libelle, f]) => {
      if (f(ka.apres[champ]) !== f(kb.apres[champ])) lignes.push({ cle: libelle, de: f(ka.apres[champ]), a: f(kb.apres[champ]) })
    })
  }
  return { lignes, inchangees }
}

export function CeQuiChange({ editions, index }) {
  if (index < 1) return null
  const { lignes, inchangees } = differences(editions[index - 1].dossier, editions[index].dossier)
  return (
    <section className="ce-qui-change" aria-label="Ce que la modification change">
      <h2>Ce que la modification <em>change</em></h2>
      <p className="muted petit">De l'édition {index} à l'édition {index + 1}. Mêmes règles, mêmes données, même fenêtre observée.</p>
      {lignes.length === 0
        ? <p>Rien ne change : même avis, mêmes niveaux de règles, mêmes mesures.</p>
        : <dl>{lignes.map((l) => (
            <div key={l.cle} style={{ display: 'contents' }}>
              <dt>{l.cle}</dt>
              <dd><del>{l.de}</del><ins>{l.a}</ins></dd>
            </div>
          ))}</dl>}
      {inchangees > 0 && lignes.length > 0 && <p className="inchange">{inchangees} règle(s) au même niveau qu'avant.</p>}
    </section>
  )
}

export default function Editions({ editions, index, onVoir }) {
  if (!editions?.length) return null
  const derniere = editions.length - 1
  return (
    <>
      {index < derniere && (
        <div className="bandeau-archive" role="status">
          <p><strong>Tu lis une archive · édition {index + 1} sur {editions.length}.</strong>
            Ses conclusions valent pour ses entrées. La dernière édition reste conservée ; modifier la demande ici en crée une nouvelle.</p>
          <button type="button" className="bouton" onClick={() => onVoir(derniere)}>Revenir à la dernière édition</button>
        </div>
      )}
      {editions.length > 1 && (
        <details className="editions">
          <summary>Éditions de ce dossier ({editions.length})</summary>
          <ol>
            {editions.map((e, i) => (
              <li key={e.heure} className={i === index ? 'lue' : ''}>
                <span className="numero">{i + 1}</span>
                <span>{resumeEdition(e)}<br /><span className="muted petit">
                  {new Date(e.heure).toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' })}
                  {i === derniere ? ' · dernière édition' : ''}</span></span>
                <span className="muted petit">{ETATS[e.dossier.verdict.etat]?.libelle}</span>
                {i === index
                  ? <span className="muted petit">affichée</span>
                  : <button type="button" className="bouton discret" onClick={() => onVoir(i)}>Relire</button>}
              </li>
            ))}
          </ol>
        </details>
      )}
    </>
  )
}
