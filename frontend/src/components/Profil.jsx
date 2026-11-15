// Éléments du profil : profil vierge, secteurs en français, choix à trois états, mise en situation.
import { cn } from '@/lib/utils'

export const PROFIL_VIERGE = {
  nom: 'Toi', age: null, experience: null, horizon_ans: null, tolerance: null, reponses_tolerance: {},
  epargne_totale_cad: null, somme_a_preserver_cad: null, revenu_stable: null, fonds_urgence: null,
  dettes_importantes: null, retrait_prevu_ans: null, exclusions: [], portefeuille_actuel: [], citations: [],
}

export const PERSONAS_NOMS = ['Amira', 'Mateo', 'Robert']

export const SECTEURS_FR = {
  Energy: 'Énergie (pétrole, gaz, pipelines)', 'Crypto asset': 'Cryptoactifs', Financials: 'Finance',
  'Information Technology': 'Technologies', 'Consumer Discretionary': 'Consommation discrétionnaire',
  'Health Care': 'Santé', Utilities: 'Services publics', Industrials: 'Industrie',
  'Consumer Staples': 'Consommation de base', 'Communication Services': 'Communication',
}

export function Choix({ actif, className, ...p }) {
  return (
    <button type="button" aria-pressed={actif}
      className={cn('cursor-pointer rounded-md border px-2.5 py-1 text-[13px] transition-colors',
        actif ? 'border-primary bg-primary text-primary-foreground' : 'border-input hover:bg-muted', className)} {...p} />
  )
}

export function TroisEtats({ libelle, valeur, onChange }) {
  return (
    <fieldset className="m-0 border-0 p-0">
      <legend className="mb-1.5 text-[13px] font-medium">{libelle}</legend>
      <div className="flex flex-wrap gap-1.5">
        {[['Oui', true], ['Non', false], ['Je ne sais pas', null]].map(([l, v]) => (
          <Choix key={l} actif={valeur === v} onClick={() => onChange(v)}>{l}</Choix>
        ))}
      </div>
    </fieldset>
  )
}

export function MiseEnSituation() {
  // Illustration fixe : 10 000 $ qui perdent 20 % en 3 mois (scénario fictif, même chiffre que la question q_chute).
  const pts = [[0, 10000], [1, 9700], [2, 9900], [3, 9300], [4, 9000], [5, 9200], [6, 8600], [7, 8300], [8, 8500], [9, 8000]]
  const x = (i) => 10 + i * 31
  const y = (v) => 10 + (10200 - v) * 0.045
  return (
    <figure className="m-0 rounded-lg border border-border bg-muted px-3 py-2.5">
      <svg viewBox="0 0 300 110" role="img" aria-label="Un placement de 10 000 $ qui descend à 8 000 $ en 3 mois" className="block w-full max-w-[360px]">
        <line x1="10" x2="290" y1={y(10000)} y2={y(10000)} stroke="var(--input)" strokeDasharray="4 4" />
        <polyline points={pts.map(([i, v]) => `${x(i)},${y(v)}`).join(' ')} fill="none" stroke="var(--bad)" strokeWidth="2.5" strokeLinejoin="round" />
        <circle cx={x(9)} cy={y(8000)} r="4" fill="var(--bad)" />
        <text x="12" y={y(10000) - 4} fontSize="11" fill="var(--muted-foreground)">10 000 $</text>
        <text x={x(9) - 4} y={y(8000) + 16} textAnchor="end" fontSize="11" fontWeight="700" fill="var(--bad)">8 000 $ (−20 %)</text>
      </svg>
      <figcaption className="text-xs text-t-scen">Scénario fictif, pour situer ta réaction.</figcaption>
    </figure>
  )
}
