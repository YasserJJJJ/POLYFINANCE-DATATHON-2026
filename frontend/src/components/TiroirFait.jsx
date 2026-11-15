import { useEffect } from 'react'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Etiquette } from './Base.jsx'
import { ListeSources } from './Sources.jsx'

const affiche = (v) => (typeof v === 'object' && v !== null ? Object.entries(v).map(([k, x]) => `${k} : ${x}`).join(' · ') : String(v))

// Le détail d'un fait F-n : valeur, source des données, méthode et références.
export default function TiroirFait({ fait, onFermer }) {
  useEffect(() => {
    const echap = (e) => e.key === 'Escape' && onFermer()
    window.addEventListener('keydown', echap)
    return () => window.removeEventListener('keydown', echap)
  }, [onFermer])
  if (!fait) return null
  return (
    <div className="fixed inset-0 z-40 bg-black/45" onClick={onFermer}>
      <aside role="dialog" aria-modal="true" aria-labelledby="tiroir-titre" onClick={(e) => e.stopPropagation()}
        className="absolute inset-y-0 right-0 grid w-[min(440px,100%)] content-start gap-3 overflow-y-auto border-l border-border bg-card p-5 shadow-[-8px_0_24px_rgba(0,0,0,.12)]">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[13px]">{fait.id}</span>
          <Etiquette type={fait.type} />
          <Button variant="ghost" size="sm" className="ml-auto" onClick={onFermer} autoFocus aria-label="Fermer">
            <X className="size-4" />
          </Button>
        </div>
        <h2 id="tiroir-titre" className="text-base font-semibold">{fait.libelle}</h2>
        <p className="font-mono text-lg tabular-nums">{affiche(fait.valeur)} {fait.unite}</p>
        <dl className="m-0 grid gap-3">
          <div>
            <dt className="text-[11.5px] font-semibold uppercase tracking-[0.05em] text-muted-foreground">{fait.lu_ou_calcule === 'lu' ? 'Lu dans' : 'Source des données'}</dt>
            <dd className="m-0 text-[13.5px]">{fait.source}</dd>
          </div>
          <div>
            <dt className="text-[11.5px] font-semibold uppercase tracking-[0.05em] text-muted-foreground">Méthode</dt>
            <dd className="m-0 text-[13.5px]">{fait.methode}</dd>
          </div>
        </dl>
        {fait.references?.length > 0 && (
          <>
            <h3 className="mt-2 text-[13px] font-semibold">Sur quoi repose ce chiffre</h3>
            <ListeSources ids={fait.references} />
          </>
        )}
        <p className="text-xs text-muted-foreground">
          {fait.type === 'HYPOTHESE'
            ? "Ce seuil est un choix de l'équipe, publié et appliqué par le code. Ce n'est pas un fait observé."
            : 'Ce chiffre a été produit par du code, pas par un modèle de langage.'}
        </p>
      </aside>
    </div>
  )
}
