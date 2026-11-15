import { useState } from 'react'
import { ArrowRight } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import FondAnime from '@/components/FondAnime.jsx'
import { Marque, NOM_PRODUIT } from '@/components/Marque.jsx'
import { cn } from '@/lib/utils'

const POINTS = [
  ['Les chiffres viennent du calcul', "Aucun nombre n'est écrit par l'IA. Elle comprend, conteste et explique."],
  ['Chaque chiffre a sa source', 'Un clic ouvre la donnée, la méthode et la référence.'],
  ['Un verdict gris, quand il manque une donnée', "L'outil préfère ne pas conclure plutôt que deviner."],
]

export default function Accueil({ onCommencer, onComparer }) {
  const [depart, setDepart] = useState(false)
  const go = () => { setDepart(true); window.setTimeout(onCommencer, 380) }

  return (
    <div className={cn('relative min-h-screen bg-background transition-opacity duration-[380ms]', depart && 'opacity-0')}>
      <FondAnime className="pointer-events-none fixed inset-0 z-0 h-full w-full" />
      <div className="pointer-events-none fixed inset-0 z-[1]"
        style={{ background: 'linear-gradient(90deg,#fff 0%,rgba(255,255,255,.92) 38%,rgba(255,255,255,0) 78%)' }} />

      <div className="relative z-10 mx-auto flex min-h-screen max-w-[980px] flex-col px-4">
        <header className="flex flex-wrap items-center justify-between gap-3 py-3.5">
          <Marque />
          <Badge>Simulation · profils fictifs</Badge>
        </header>

        <main className="flex flex-1 items-center py-12">
          <div className="max-w-[560px]">
            <h1 className="text-[40px] font-bold leading-[1.08] tracking-[-0.03em] [text-wrap:balance] sm:text-[52px]">
              Avant d'investir, fais vérifier ton idée.
            </h1>
            <p className="mt-4 max-w-[52ch] text-base leading-relaxed text-muted-foreground">
              Dis ce que tu veux faire de ton argent, avec tes mots. {NOM_PRODUIT} reformule ta demande, la confronte à ta
              situation avec des chiffres réels, et te montre ce qui la rendrait acceptable. Il ne te dit jamais quoi acheter.
            </p>
            <div className="mt-7 flex flex-wrap items-center gap-3.5">
              <Button size="lg" onClick={go}>Commencer <ArrowRight className="size-4" /></Button>
              <span className="text-[13px] text-muted-foreground">Environ 2 minutes</span>
            </div>
            <Button variant="link" className="mt-4 text-[13px] text-muted-foreground" onClick={onComparer}>
              Ou voir la même demande pour les 3 profils du défi
            </Button>
          </div>
        </main>

        <footer className="grid gap-5 border-t border-border/80 py-5 sm:grid-cols-3">
          {POINTS.map(([t, d]) => (
            <div key={t} className="min-w-0">
              <div className="text-[13px] font-semibold">{t}</div>
              <p className="mt-0.5 text-[12.5px] leading-snug text-muted-foreground">{d}</p>
            </div>
          ))}
        </footer>
        <p className="pb-5 text-xs text-muted-foreground">
          Simulation éducative. Aucune transaction et aucun conseil financier personnalisé. Le passé ne prédit pas l'avenir.
        </p>
      </div>
    </div>
  )
}
