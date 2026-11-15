import { useEffect, useState } from 'react'
import { api, dollars } from '@/api.js'
import { Card } from '@/components/ui/card'
import { ETATS, PuceNiveau, PuceVerdict, TONS, ans } from '@/components/Base.jsx'
import { Choix } from '@/components/Profil.jsx'
import { cn } from '@/lib/utils'

// Analyses déjà faites pendant la session : rouvrir la vue ne relance pas 3 analyses Bedrock (≈ 13 s chacune).
const CACHE = new Map()

// Même question posée par 3 profils : la preuve que le profil change vraiment la réponse.
export default function Comparer({ personas }) {
  const [memeDemande, setMemeDemande] = useState(true)
  const [resultats, setResultats] = useState({})
  const ref = personas.robert.demande

  useEffect(() => {
    let actuel = true
    setResultats({})
    Object.entries(personas).forEach(([cle, p]) => {
      const montant = Math.round(p.profil.epargne_totale_cad * 0.2)
      const demande = memeDemande
        ? { texte: `Je veux mettre ${montant} $ dans Tesla, tout le monde en parle.`, ticker: ref.ticker, montant_cad: montant }
        : p.demande
      const cleCache = `${cle}:${memeDemande}`
      if (!CACHE.has(cleCache)) CACHE.set(cleCache, api.analyser(p.profil, demande).catch((e) => { CACHE.delete(cleCache); throw e }))
      CACHE.get(cleCache)
        .then((d) => actuel && setResultats((r) => ({ ...r, [cle]: d })))
        .catch((e) => actuel && setResultats((r) => ({ ...r, [cle]: { erreur: e.message } })))
    })
    return () => { actuel = false }
  }, [personas, memeDemande, ref])

  return (
    <div className="grid gap-4">
      <div>
        <h1 className="text-[28px] font-bold leading-tight tracking-[-0.02em]">
          {memeDemande ? `La même idée, ${ref.ticker} pour 20 % de l'épargne, dans trois vies différentes.` : 'Chaque profil avec sa propre demande.'}
        </h1>
        <div className="mt-3 flex gap-1.5" role="group" aria-label="Mode de comparaison">
          <Choix actif={memeDemande} onClick={() => setMemeDemande(true)}>Même demande</Choix>
          <Choix actif={!memeDemande} onClick={() => setMemeDemande(false)}>Leur propre demande</Choix>
        </div>
      </div>
      <div className="grid gap-3.5 md:grid-cols-3">
        {Object.entries(personas).map(([cle, p]) => {
          const r = resultats[cle]
          const d = r && !r.erreur ? r : null
          const bloquantes = d?.regles.filter((x) => x.niveau === 'rouge' || x.niveau === 'orange') || []
          const ton = d ? TONS[ETATS[d.verdict.etat]?.ton || 'grey'] : null
          return (
            <Card key={cle} className={cn('grid min-w-0 content-start gap-2.5 border-t-[4px] p-4', ton ? ton.bord : 'border-t-border')}>
              <div className="flex items-center gap-2.5">
                <span className="grid size-9 flex-none place-items-center rounded-full bg-muted text-sm font-semibold" aria-hidden="true">{p.profil.nom[0]}</span>
                <div>
                  <div className="font-semibold">{p.profil.nom}, {p.profil.age} ans</div>
                  <div className="text-xs text-muted-foreground">Horizon {ans(p.profil.horizon_ans)} · épargne fictive {dollars(p.profil.epargne_totale_cad)}</div>
                </div>
              </div>
              {d ? (
                <>
                  <p className="text-[13px] text-muted-foreground">{d.texte.reformulation}</p>
                  <div><PuceVerdict etat={d.verdict.etat} /></div>
                  <p className="text-[13px]">{d.verdict.respectees}/{d.verdict.evaluees} règles respectées</p>
                  <ul className="m-0 grid list-none gap-2 p-0">
                    {bloquantes.map((x) => (
                      <li key={x.code} className="grid gap-1 rounded-md bg-muted px-3 py-2 text-[12.5px]">
                        <div className="flex items-start justify-between gap-2"><strong className="font-semibold">{x.libelle}</strong><PuceNiveau niveau={x.niveau} /></div>
                        <p>{x.explication}</p>
                      </li>
                    ))}
                  </ul>
                  {d.options[1]?.changement && (
                    <p className="text-[13px]">Version ajustée : <strong>{dollars(d.options[1].montant_cad)}</strong> sur {ans(d.options[1].horizon_ans)}</p>
                  )}
                </>
              ) : r?.erreur
                ? <p role="alert" className="rounded-md bg-bad-bg px-3 py-2 text-[13px] text-bad">Analyse impossible pour ce profil. ({r.erreur})</p>
                : <p className="flex items-center gap-2 text-[13px] text-muted-foreground"><span className="size-3.5 animate-spin rounded-full border-2 border-border border-t-primary" /> Analyse en cours…</p>}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
