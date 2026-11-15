// Éléments du profil partagés : profil vierge, secteurs en français, choix à trois états, mise en situation.

export const PROFIL_VIERGE = {
  nom: 'Toi', age: null, experience: null, horizon_ans: null, tolerance: null, reponses_tolerance: {},
  epargne_totale_cad: null, somme_a_preserver_cad: null, revenu_stable: null, fonds_urgence: null,
  dettes_importantes: null, retrait_prevu_ans: null, exclusions: [], portefeuille_actuel: [], citations: [],
}

export const SECTEURS_FR = {
  Energy: 'Énergie (pétrole, gaz, pipelines)', 'Crypto asset': 'Cryptoactifs', Financials: 'Finance',
  'Information Technology': 'Technologies', 'Consumer Discretionary': 'Consommation discrétionnaire',
  'Health Care': 'Santé', Utilities: 'Services publics', Industrials: 'Industrie',
  'Consumer Staples': 'Consommation de base', 'Communication Services': 'Communication',
}

export function TroisEtats({ id, libelle, valeur, onChange }) {
  return (
    <fieldset className="trois-etats">
      <legend>{libelle}</legend>
      {[['Oui', true], ['Non', false], ['Je ne sais pas', null]].map(([l, v]) => (
        <label key={l} className={valeur === v ? 'choisi' : ''}>
          <input type="radio" name={id} checked={valeur === v} onChange={() => onChange(v)} />
          {l}
        </label>
      ))}
    </fieldset>
  )
}

export function MiseEnSituation() {
  // Illustration fixe : 10 000 $ qui perdent 20 % en 3 mois (scénario fictif, même chiffre que la question q_chute).
  const pts = [[0, 10000], [1, 9700], [2, 9900], [3, 9300], [4, 9000], [5, 9200], [6, 8600], [7, 8300], [8, 8500], [9, 8000]]
  const x = (i) => 10 + i * 31
  const y = (v) => 10 + (10200 - v) * 0.045
  return (
    <figure className="mise-en-situation">
      <svg viewBox="0 0 300 110" role="img" aria-label="Un placement de 10 000 $ qui descend à 8 000 $ en 3 mois">
        <line x1="10" x2="290" y1={y(10000)} y2={y(10000)} className="ligne-ref" />
        <polyline points={pts.map(([i, v]) => `${x(i)},${y(v)}`).join(' ')} className="ligne-chute" />
        <circle cx={x(9)} cy={y(8000)} r="4" className="point-chute" />
        <text x="12" y={y(10000) - 4} className="txt-graphe">10 000 $</text>
        <text x={x(9) - 4} y={y(8000) + 16} textAnchor="end" className="txt-graphe fort">8 000 $ (−20 %)</text>
      </svg>
      <figcaption>Scénario fictif, pour situer ta réaction.</figcaption>
    </figure>
  )
}
