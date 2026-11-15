import { useEffect, useState } from 'react'
import { PucesFaits } from '../composants/Base.jsx'

export const AGENTS = {
  Profileur: { role: 'Comprend ta demande et structure ton profil', nature: 'Agent IA' },
  'Contrôle données': { role: 'Vérifie les données avant tout calcul', nature: 'Code' },
  Analyste: { role: 'Choisit les mesures et appelle les outils de calcul', nature: 'Agent IA + outils' },
  Sceptique: { role: 'Cherche une faille et force un recalcul', nature: 'Agent IA' },
  Gardien: { role: 'Applique les règles et décide du verdict', nature: 'Code' },
  Rédacteur: { role: 'Explique, sans rien ajouter', nature: 'Agent IA' },
}

const DELAI_MS = 750

export default function Etape3Trace({ dossier, onFini, ouvrirFait }) {
  const [visibles, setVisibles] = useState(0)
  const trace = dossier?.trace || []

  useEffect(() => {
    if (!dossier) return
    if (visibles >= trace.length) {
      const t = setTimeout(onFini, 900)
      return () => clearTimeout(t)
    }
    const t = setTimeout(() => setVisibles((v) => v + 1), DELAI_MS)
    return () => clearTimeout(t)
  }, [dossier, visibles, trace.length, onFini])

  return (
    <section className="etape3">
      <p className="surtitre">Analyse en direct</p>
      <h1>Six rôles examinent ta demande, chacun à son tour.</h1>
      <p className="lede">Les chiffres viennent du code. Les agents comprennent, contestent et expliquent.</p>

      <ol className="trace">
        {trace.slice(0, visibles).map((t, i) => (
          <li key={i} className={`trace-etape ${AGENTS[t.agent]?.nature === 'Code' ? 'code' : 'ia'}`}>
            <div className="trace-agent">
              <strong>{t.agent}</strong>
              <span className="nature">{AGENTS[t.agent]?.nature}</span>
            </div>
            <div className="trace-corps">
              <p className="trace-action">{t.action}</p>
              <p>{t.detail}</p>
              {t.agent === 'Sceptique' && dossier.objections.map((o) => (
                <div key={o.id} className="objection">
                  <p><span className="mono">{o.id} → {o.cible}</span> {o.texte}</p>
                  <p className="recalcul">↳ {o.reponse}</p>
                </div>
              ))}
              <PucesFaits ids={[...new Set(t.faits)]} ouvrir={ouvrirFait} />
            </div>
            <span className="duree mono">{t.duree_ms} ms</span>
          </li>
        ))}
        {(!dossier || visibles < trace.length) && (
          <li className="trace-etape attente" aria-live="polite">
            <span className="points" aria-hidden="true"><i /><i /><i /></span>
            {dossier ? `${trace[visibles]?.agent} travaille…` : 'Préparation du dossier de décision…'}
          </li>
        )}
      </ol>
      {dossier && visibles >= trace.length && (
        <button type="button" className="bouton principal" onClick={onFini}>Voir le verdict</button>
      )}
    </section>
  )
}
