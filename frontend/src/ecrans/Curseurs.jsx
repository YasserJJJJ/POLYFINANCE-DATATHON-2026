import { useMemo, useState } from 'react'
import { Copy, Download } from 'lucide-react'
import { dollars } from '@/api.js'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Slider } from '@/components/ui/slider'
import { ETATS, PuceVerdict, TONS, ans } from '@/components/Base.jsx'
import { PERSONAS_NOMS, SECTEURS_FR } from '@/components/Profil.jsx'
import { sourcesDuDossier, useRegistre } from '@/components/Sources.jsx'
import { cn } from '@/lib/utils'

const LEXIQUE = {
  'Pire chute': 'La plus forte baisse entre un sommet et le creux qui suit, sur la période observée.',
  Volatilité: "L'ampleur habituelle des variations de prix. Plus elle est haute, plus le prix bouge fort, dans les deux sens.",
  Horizon: "Le temps avant d'avoir besoin de l'argent.",
  'Capacité de perte': "La baisse que ta situation te permet d'encaisser sans changer tes projets.",
  'Tolérance au risque': 'La baisse que tu es prêt·e à vivre sans paniquer.',
  Corrélation: 'À quel point deux placements montent et baissent en même temps (1 = toujours ensemble).',
}

// La fiche à apporter au conseiller (pré-rendez-vous), écrite par le code à partir du dossier.
function fiche(d, registre) {
  const p = d.profil, ev = p.evaluation, v = d.verdict
  const estPersona = PERSONAS_NOMS.includes(p.nom)
  const bloquees = d.regles.filter((r) => r.niveau === 'rouge' || r.niveau === 'orange')
  const volatil = (d.demande.mesures?.volatilite_pct ?? 0) > 25
  const questions = [
    volatil ? 'Quelle part de mon épargne serait raisonnable pour un placement aussi volatil ?' : 'Quelle part de mon épargne serait raisonnable pour ce placement ?',
    ...(bloquees.some((r) => r.code === 'exclusion') ? ['Quelles options respectent mes exclusions avec un profil de risque comparable ?'] : []),
    ...(bloquees.some((r) => r.code === 'horizon' || r.code === 'retrait') ? ["Comment protéger l'argent dont j'aurai besoin avant la fin de mon horizon ?"] : []),
    "Comment ce placement s'intègre-t-il à ce que je détiens déjà ?",
  ]
  return [
    '# Ma demande, préparée pour mon rendez-vous', '',
    '## Ce que je veux faire', d.texte.reformulation, '',
    '## Ma situation',
    `- Horizon : ${p.horizon_ans} an(s)`,
    `- Tolérance au risque : ${ev.tolerance}/100 · Capacité de perte : ${ev.capacite}/100 (on retient ${ev.score_retenu}/100)`,
    `- Somme à ne jamais risquer : ${dollars(p.somme_a_preserver_cad)}`,
    p.exclusions?.length ? `- Secteurs que je veux éviter : ${p.exclusions.map((s) => SECTEURS_FR[s] || s).join(', ')}` : '- Aucune exclusion déclarée', '',
    '## Le second avis obtenu',
    `**${v.libelle}** (${v.respectees} règle(s) respectée(s) sur ${v.evaluees})`,
    ...bloquees.map((r) => `- ${r.libelle} : ${r.explication}`), '',
    '## Les options comparées',
    ...d.options.map((o) => `- ${o.nom} : ${dollars(o.montant_cad)}, horizon ${o.horizon_ans} an(s) → ${ETATS[o.etat].libelle}`), '',
    '## Mes questions pour le conseiller', ...questions.map((q) => `- ${q}`), '',
    '## Sur quoi repose ce second avis',
    ...sourcesDuDossier(d).map((id) => registre?.references?.[id]).filter(Boolean)
      .map((r) => `- ${r.auteurs} (${r.annee}). ${r.titre}.${r.lien ? ` ${r.lien}` : ''} (examen : ${r.examen})`), '',
    '## Les mots à connaître', ...Object.entries(LEXIQUE).map(([m, def]) => `- **${m}** : ${def}`), '',
    `_${d.texte.avertissement} Données 2021-11-12 → 2026-11-12 ; le passé ne prédit pas l'avenir. `
      + "Les scores et les seuils sont des hypothèses de l'équipe (barèmes publiés dans l'application)"
      + `${estPersona ? ', et les montants de ce profil sont fictifs' : ''}._`,
  ].join('\n')
}

const VIDE = { montants: [], horizons: [], cases: [] }

export default function Curseurs({ dossier, onRetour, onRecommencer }) {
  // Verdict gris : le Gardien ne calcule pas de grille. On l'explique au lieu d'afficher une page vide.
  const bascule = dossier.bascule?.cases?.length ? dossier.bascule : VIDE
  const montants = useMemo(() => [...bascule.montants].sort((a, b) => a - b), [bascule])
  const [iM, setIM] = useState(Math.max(0, montants.indexOf(Math.round(dossier.demande.montant_cad))))
  const [h, setH] = useState(dossier.profil.horizon_ans ?? bascule.horizons[0] ?? 1)
  const [copie, setCopie] = useState('')
  const montant = montants[iM]
  const caseActuelle = bascule.cases.find((c) => c.montant_cad === montant && c.horizon_ans === h)
  const registre = useRegistre()
  const texteFiche = useMemo(() => fiche(dossier, registre), [dossier, registre])
  const ton = TONS[ETATS[caseActuelle?.etat]?.ton || 'grey']

  const copier = async () => {
    try { await navigator.clipboard.writeText(texteFiche); setCopie('Copié.') } catch { setCopie('Sélectionne le texte et copie-le.') }
  }
  const telecharger = () => {
    const url = URL.createObjectURL(new Blob([texteFiche], { type: 'text/markdown' }))
    const a = Object.assign(document.createElement('a'), { href: url, download: 'ma-demande-pour-mon-conseiller.md' })
    a.click(); URL.revokeObjectURL(url)
  }

  return (
    <div className="grid gap-4">
      <div>
        <h1 className="text-[28px] font-bold leading-tight tracking-[-0.02em]">Qu'est-ce qui rendrait ta demande raisonnable ?</h1>
        <p className="mt-2 text-[15px] text-muted-foreground">Bouge le montant ou l'horizon : chaque position est un verdict du Gardien, calculé par le code,
          sans IA ({bascule.cases.length} combinaisons calculées pendant l'analyse).</p>
      </div>
      {!bascule.cases.length && (
        <p className="rounded-lg border border-grey-bd bg-grey-bg px-4 py-3 text-[13.5px] text-grey">Verdict impossible à calculer : complète d'abord les informations manquantes.</p>
      )}

      {bascule.cases.length > 0 && (
        <div className="grid items-start gap-3.5 md:grid-cols-[1fr_1.15fr]">
          <Card>
            <CardContent className="grid gap-5">
              <div className={cn('grid place-items-center rounded-lg border px-4 py-5', ton.fond, ton.bord)} aria-live="polite">
                <PuceVerdict etat={caseActuelle?.etat} grand />
              </div>
              <div className="grid gap-2">
                <div className="flex justify-between text-[13px]"><span className="font-medium">Montant placé</span><span className="font-mono tabular-nums">{dollars(montant)}</span></div>
                <Slider aria-label="Montant placé" min={0} max={montants.length - 1} step={1} value={[iM]} onValueChange={([v]) => setIM(v)} />
              </div>
              <div className="grid gap-2">
                <div className="flex justify-between text-[13px]"><span className="font-medium">Horizon</span><span className="font-mono tabular-nums">{ans(h)}</span></div>
                <Slider aria-label="Horizon" min={bascule.horizons[0]} max={bascule.horizons.at(-1)} step={1} value={[h]} onValueChange={([v]) => setH(v)} />
              </div>
              <p className="text-xs text-muted-foreground">Ta demande de départ : {dollars(dossier.demande.montant_cad)} sur {ans(dossier.profil.horizon_ans)}.</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>La carte complète</CardTitle>
              <CardDescription>Horizontal : horizon en années. Vertical : montant placé. Chaque case = le verdict du Gardien.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3">
              <div className="overflow-x-auto">
                <div className="grid gap-[3px]" style={{ gridTemplateColumns: `76px repeat(${bascule.horizons.length}, minmax(14px, 1fr))` }}>
                  {[...montants].reverse().map((m) => (
                    <div key={m} className="contents">
                      <span className="pr-1.5 text-right font-mono text-[10.5px] leading-[18px] text-muted-foreground">{dollars(m)}</span>
                      {bascule.horizons.map((hz) => {
                        const c = bascule.cases.find((x) => x.montant_cad === m && x.horizon_ans === hz)
                        const e = ETATS[c?.etat] || ETATS.indetermine
                        const ici = m === montant && hz === h
                        return (
                          <button key={hz} type="button" title={`${dollars(m)}, ${ans(hz)} : ${e.libelle}`} aria-label={`${dollars(m)}, ${ans(hz)} : ${e.libelle}`}
                            onClick={() => { setIM(montants.indexOf(m)); setH(hz) }}
                            className={cn('h-[18px] cursor-pointer rounded-[3px] opacity-80 hover:opacity-100', TONS[e.ton].point, ici && 'opacity-100 outline-2 outline-offset-1 outline-foreground')} />
                        )
                      })}
                    </div>
                  ))}
                  <span />
                  {bascule.horizons.map((hz) => <span key={hz} className="text-center font-mono text-[10.5px] text-muted-foreground">{hz % 5 === 0 || hz === 1 ? hz : ''}</span>)}
                </div>
              </div>
              <ul className="m-0 flex list-none flex-wrap gap-x-4 gap-y-1 p-0 text-xs" aria-label="Légende de la carte">
                {Object.entries(ETATS).map(([cle, e]) => (
                  <li key={cle} className="flex items-center gap-1.5"><i aria-hidden="true" className={cn('size-2.5 rounded-[2px]', TONS[e.ton].point)} />{e.libelle}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <CardTitle>Ta fiche pour ton conseiller</CardTitle>
            <CardDescription>Ta demande reformulée, ta situation, le verdict, les options et les questions à poser.</CardDescription>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="outline" size="sm" onClick={copier}><Copy className="size-3.5" /> Copier</Button>
            <Button variant="outline" size="sm" onClick={telecharger}><Download className="size-3.5" /> Télécharger (.md)</Button>
            <span className="text-xs text-muted-foreground" aria-live="polite">{copie}</span>
          </div>
        </CardHeader>
        <CardContent>
          <pre className="max-h-[360px] overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3.5 font-mono text-xs leading-relaxed">{texteFiche}</pre>
        </CardContent>
      </Card>

      <div className="flex flex-wrap justify-between gap-2.5">
        <Button variant="ghost" onClick={onRetour}>Retour au verdict</Button>
        <Button variant="outline" onClick={onRecommencer}>Nouvelle demande</Button>
      </div>
    </div>
  )
}
