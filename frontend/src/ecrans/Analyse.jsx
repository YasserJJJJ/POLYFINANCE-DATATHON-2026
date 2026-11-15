import { useEffect, useState } from 'react'
import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { PucesFaits } from '@/components/Base.jsx'
import { SourcesCompactes } from '@/components/Sources.jsx'
import { cn } from '@/lib/utils'

export const AGENTS = {
  Profileur: { role: 'Comprend ta demande et structure ton profil', nature: 'Agent IA' },
  'Contrôle données': { role: 'Vérifie les données avant tout calcul', nature: 'Code' },
  Analyste: { role: 'Appelle les outils de calcul et écrit les faits F-n', nature: 'Code' },
  Sceptique: { role: 'Cherche une faille et force un recalcul', nature: 'Agent IA' },
  Gardien: { role: 'Applique les règles et décide du verdict', nature: 'Code' },
  Rédacteur: { role: 'Explique, sans rien ajouter', nature: 'Agent IA' },
}

const DELAI_MS = 750

export default function Analyse({ dossier, onFini, ouvrirFait }) {
  const [visibles, setVisibles] = useState(0)
  const [secondes, setSecondes] = useState(0)
  const trace = dossier?.trace || []
  const totalMs = trace.reduce((s, t) => s + (t.duree_ms || 0), 0)

  // Pendant l'attente : un vrai chronomètre (l'API renvoie le dossier d'un bloc, rien n'est simulé ici).
  useEffect(() => {
    if (dossier) return undefined
    const debut = Date.now()
    const t = setInterval(() => setSecondes(Math.round((Date.now() - debut) / 1000)), 250)
    return () => clearInterval(t)
  }, [dossier])

  // Une fois le dossier reçu : relecture de la trace réelle, étape par étape. La personne passe au verdict quand elle veut.
  useEffect(() => {
    if (!dossier || visibles >= trace.length) return undefined
    const t = setTimeout(() => setVisibles((v) => v + 1), DELAI_MS)
    return () => clearTimeout(t)
  }, [dossier, visibles, trace.length])

  return (
    <div className="grid gap-4">
      <div>
        <h1 className="text-[28px] font-bold leading-tight tracking-[-0.02em]">Six rôles examinent ta demande, chacun à son tour.</h1>
        <p className="mt-2 text-[15px] text-muted-foreground">Les chiffres viennent du code. Les agents comprennent, contestent et expliquent.</p>
        <p className="mt-2 text-[13px] text-muted-foreground" aria-live="polite">
          {dossier
            ? `Analyse terminée en ${(totalMs / 1000).toFixed(1).replace('.', ',')} s. Ci-dessous, la relecture de la trace réelle : chaque étape affiche sa durée mesurée.`
            : `Les agents travaillent (${secondes} s écoulées ; une analyse avec Bedrock prend en général 10 à 15 s).`}
        </p>
      </div>

      <ol className="m-0 grid list-none gap-3 p-0">
        {trace.slice(0, visibles).map((t, i) => {
          const ia = AGENTS[t.agent]?.nature !== 'Code'
          return (
            <li key={i} className={cn('grid gap-3 rounded-lg border border-border bg-card p-4 shadow-[0_1px_2px_rgba(0,0,0,.05)] sm:grid-cols-[150px_1fr_auto]',
              ia ? 'border-l-[3px] border-l-accent' : 'border-l-[3px] border-l-foreground')}>
              <div>
                <div className="font-semibold">{t.agent}</div>
                <Badge variant={ia ? 'outline' : 'secondary'} className="mt-1">{AGENTS[t.agent]?.nature || 'Agent'}</Badge>
              </div>
              <div className="grid min-w-0 gap-2 text-[13.5px]">
                <p className="font-medium">{t.action}</p>
                <p className="text-muted-foreground">{t.detail}</p>
                {t.agent === 'Sceptique' && dossier.objections.map((o) => (
                  <div key={o.id} className="rounded-md bg-muted px-3 py-2">
                    <p><span className="font-mono text-xs">{o.id} → {o.cible}</span> {o.texte}</p>
                    <p className="mt-1 text-ok">↳ {o.reponse}</p>
                  </div>
                ))}
                <PucesFaits ids={t.faits} ouvrir={ouvrirFait} />
                <SourcesCompactes ids={t.references} prefixe="Conçu d'après :" />
              </div>
              <span className="font-mono text-xs text-muted-foreground">{t.duree_ms} ms</span>
            </li>
          )
        })}
        {(!dossier || visibles < trace.length) && (
          <li className="flex items-center gap-3 rounded-lg border border-dashed border-border p-4 text-[13.5px] text-muted-foreground" aria-live="polite">
            <span className="size-4 animate-spin rounded-full border-2 border-border border-t-primary" />
            {dossier ? `${trace[visibles]?.agent} travaille…` : 'Préparation du dossier de décision…'}
          </li>
        )}
      </ol>
      {dossier && visibles >= trace.length && (
        <Button size="lg" className="w-full" onClick={onFini}>Voir le verdict <ArrowRight className="size-4" /></Button>
      )}
    </div>
  )
}
