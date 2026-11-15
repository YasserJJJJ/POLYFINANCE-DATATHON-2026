import { useEffect, useState } from 'react'
import { PuceIssue, PucesFaits } from '../composants/Base.jsx'
import { SourcesCompactes } from '../composants/Sources.jsx'

export const AGENTS = {
  Profileur: { role: 'Comprend ta demande et structure ton profil', nature: 'Agent IA' },
  'Contrôle données': { role: 'Vérifie les données avant tout calcul', nature: 'Code' },
  Analyste: { role: 'Appelle les outils de calcul et écrit les faits F-n', nature: 'Code' },
  Sceptique: { role: 'Cherche une faille et force un recalcul', nature: 'Agent IA' },
  Gardien: { role: 'Applique les règles et décide du verdict', nature: 'Code' },
  Rédacteur: { role: 'Explique, sans rien ajouter', nature: 'Agent IA' },
}

const DELAI_MS = 750

export default function Etape3Trace({ dossier, onFini, ouvrirFait }) {
  const [visibles, setVisibles] = useState(0)
  const [secondes, setSecondes] = useState(0)
  const trace = dossier?.trace || []
  const totalMs = trace.reduce((s, t) => s + (t.duree_ms || 0), 0)

  // Pendant l'attente : un vrai chronomètre (l'API renvoie le dossier d'un bloc, rien n'est simulé ici).
  useEffect(() => {
    if (dossier) return
    const debut = Date.now()
    const t = setInterval(() => setSecondes(Math.round((Date.now() - debut) / 1000)), 250)
    return () => clearInterval(t)
  }, [dossier])

  // Une fois le dossier reçu : relecture de la trace réelle, étape par étape. Pas de passage automatique au
  // verdict : la personne (ou le jury) lit à son rythme, puis clique.
  useEffect(() => {
    if (!dossier || visibles >= trace.length) return
    const t = setTimeout(() => setVisibles((v) => v + 1), DELAI_MS)
    return () => clearTimeout(t)
  }, [dossier, visibles, trace.length])

  return (
    <section className="etape3">
      <p className="surtitre">Analyse</p>
      <h1>Six rôles examinent ta demande, chacun à son tour.</h1>
      <p className="lede">Les chiffres viennent du code. Les agents comprennent, contestent et expliquent.</p>
      <p className="muted petit" aria-live="polite">
        {dossier
          ? `Analyse terminée en ${(totalMs / 1000).toFixed(1).replace('.', ',')} s. Ci-dessous, la relecture de la trace réelle : chaque étape affiche sa durée mesurée.`
          : `Les agents travaillent (${secondes} s écoulées ; une analyse avec Bedrock prend en général 10 à 15 s).`}
      </p>

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
                  <PuceIssue issue={o.issue} />
                </div>
              ))}
              <PucesFaits ids={[...new Set(t.faits)]} ouvrir={ouvrirFait} />
              <SourcesCompactes ids={t.references} prefixe="Conçu d'après :" />
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
