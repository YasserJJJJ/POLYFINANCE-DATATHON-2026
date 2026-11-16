import { useEffect, useState } from 'react'
import { PuceIssue, PucesFaits } from '../composants/Base.jsx'
import { SourcesCompactes } from '../composants/Sources.jsx'
import { pourClient } from '../affichage.js'
import PreuveAppels from '../composants/PreuveAppels.jsx'

export const AGENTS = {
  Profileur: { role: 'Comprend ta demande et structure ton profil', nature: 'Agent IA' },
  'Contrôle données': { role: 'Vérifie les données avant tout calcul', nature: 'Code' },
  Analyste: { role: 'Appelle les outils de calcul et écrit les faits F-n', nature: 'Code' },
  Sceptique: { role: 'Cherche une faille et force un recalcul', nature: 'Agent IA' },
  Gardien: { role: 'Applique les règles et décide du verdict', nature: 'Code' },
  Rédacteur: { role: 'Explique, sans rien ajouter', nature: 'Agent IA' },
}

const ORDRE = Object.keys(AGENTS)

// Chaque étape s'affiche dès que son agent a fini (flux /api/analyse/flux) : rien n'est rejoué ni simulé.
export default function Etape3Trace({ dossier, direct, onFini, ouvrirFait }) {
  const [secondes, setSecondes] = useState(0)
  const trace = dossier?.trace || direct.trace
  const objections = dossier?.objections || direct.objections
  const totalMs = trace.reduce((s, t) => s + (t.duree_ms || 0), 0)
  const dernier = trace[trace.length - 1]?.agent
  const prochain = dernier ? ORDRE[ORDRE.indexOf(dernier) + 1] : ORDRE[0]

  useEffect(() => {
    if (dossier) return
    const debut = Date.now()
    const t = setInterval(() => setSecondes(Math.round((Date.now() - debut) / 1000)), 250)
    return () => clearInterval(t)
  }, [dossier])

  return (
    <section className="etape3">
      <p className="surtitre">Analyse</p>
      <h1>Six rôles examinent ta demande, chacun à son tour.</h1>
      <p className="lede">Les chiffres viennent du code. Les agents comprennent, contestent et expliquent.</p>
      <p className="muted petit" aria-live="polite">
        {dossier
          ? `Analyse terminée. Durées des rôles : ${(totalMs / 1000).toFixed(1).replace('.', ',')} s au total ; le détail mesuré figure à droite.`
          : `Les agents travaillent (${secondes} s écoulées). Selon la connexion, les étapes peuvent arriver ensemble à la fin.`}
      </p>

      <ol className="trace">
        {trace.map((t, i) => (
          <li key={i} className={`trace-etape ${AGENTS[t.agent]?.nature === 'Code' ? 'code' : 'ia'}`}>
            <div className="trace-agent">
              <strong>{t.agent}</strong>
              <span className="nature">{AGENTS[t.agent]?.nature}</span>
            </div>
            <div className="trace-corps">
              <p className="trace-action">{t.action}</p>
              <p>{pourClient(t.detail)}</p>
              {t.agent === 'Sceptique' && objections.map((o) => (
                <div key={o.id} className="objection">
                  <p>{pourClient(o.texte)}</p>
                  <p className="recalcul">↳ {pourClient(o.reponse)}</p>
                  <PuceIssue issue={o.issue} />
                </div>
              ))}
              <PucesFaits ids={[...new Set(t.faits)]} ouvrir={ouvrirFait} />
              <SourcesCompactes ids={t.references} prefixe="Conçu d'après :" />
            </div>
            <span className="duree mono">{t.duree_ms} ms</span>
          </li>
        ))}
        {!dossier && prochain && (
          <li className="trace-etape attente" aria-live="polite">
            <span className="points" aria-hidden="true"><i /><i /><i /></span>
            {`${prochain} travaille… ${AGENTS[prochain].role.toLowerCase()}.`}
          </li>
        )}
      </ol>
      <PreuveAppels appels={dossier?.appels_modele} />
      {dossier && (
        <button type="button" className="bouton principal" onClick={onFini}>Voir le verdict</button>
      )}
    </section>
  )
}
