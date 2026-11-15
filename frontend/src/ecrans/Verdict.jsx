import { ArrowRight } from 'lucide-react'
import { dollars } from '@/api.js'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ETATS, Etiquette, PuceNiveau, PuceVerdict, PucesFaits, TONS, ans } from '@/components/Base.jsx'
import GraphiqueChute from '@/components/GraphiqueChute.jsx'
import { PERSONAS_NOMS } from '@/components/Profil.jsx'
import { ListeSources, SourcesCompactes, SourcesParType, sourcesDuDossier } from '@/components/Sources.jsx'
import { cn } from '@/lib/utils'

// Le verdict : 4 états décidés par le Gardien (code), miroir, raisons, 3 options, règles, faits et sources.

const Titre = ({ children }) => <h2 className="mb-2.5 mt-7 text-xs font-semibold uppercase tracking-[0.06em] text-muted-foreground">{children}</h2>

function Phrases({ phrases, ouvrir }) {
  if (!phrases?.length) return null
  return (
    <ul className="m-0 grid list-none gap-0 p-0">
      {phrases.map((p, i) => (
        <li key={i} className="grid gap-1.5 border-b border-border py-2.5 text-[13.5px] last:border-b-0 sm:grid-cols-[110px_1fr_auto] sm:items-start sm:gap-3">
          <span><Etiquette type={p.type} /></span>
          <span className="min-w-0">
            {p.texte}
            {p.references?.length > 0 && <SourcesCompactes ids={p.references} prefixe="Source :" />}
          </span>
          <PucesFaits ids={p.faits} ouvrir={ouvrir} />
        </li>
      ))}
    </ul>
  )
}

function Option({ o, lettre, meilleure }) {
  return (
    <Card className={cn('grid min-w-0 content-start gap-1.5 p-3.5', meilleure && 'border-primary shadow-[0_0_0_1px_var(--brand)]')}>
      <div className="text-xs font-medium text-muted-foreground">{lettre} · {o.nom}</div>
      <div className="font-mono text-[19px] font-bold tracking-[-0.02em] tabular-nums">{dollars(o.montant_cad)}</div>
      {o.ticker && <div className="text-xs text-muted-foreground">{o.libelle_actif ? `${o.libelle_actif} (${o.ticker})` : o.ticker}</div>}
      <div className="text-xs text-muted-foreground">Horizon : {ans(o.horizon_ans)}</div>
      <div className="mt-1"><PuceVerdict etat={o.etat} /></div>
      {o.changement?.montant_cad != null && <p className="text-xs text-muted-foreground">Montant ramené à {dollars(o.changement.montant_cad)}</p>}
      {o.changement?.horizon_ans != null && <p className="text-xs text-muted-foreground">Horizon porté à {ans(o.changement.horizon_ans)}</p>}
    </Card>
  )
}

export default function Verdict({ dossier, ouvrirFait, onBascule, onModifier }) {
  const { verdict, texte, regles, options, faits, objections, qualite_donnees: qualite, demande, profil } = dossier
  const estPersona = PERSONAS_NOMS.includes(profil?.nom)
  const ids = demande.ids_faits || {}
  const ordre = { rouge: 0, orange: 1, gris: 2, ok: 3, non_evaluee: 4 }
  const reglesTriees = [...regles].sort((a, b) => ordre[a.niveau] - ordre[b.niveau])
  const ton = TONS[ETATS[verdict.etat]?.ton || 'grey']
  const meilleure = options.findIndex((o) => o.etat === 'coherent')

  return (
    <div className="grid">
      {/* En-tête du verdict */}
      <div className={cn('flex flex-col gap-4 rounded-lg border px-5 py-[18px] sm:flex-row sm:items-start', ton.fond, ton.bord)}>
        <div className="min-w-0 flex-1">
          <div className={cn('text-xs font-semibold uppercase tracking-[0.06em]', ton.texte)}>Le second avis</div>
          <h1 className={cn('mt-0.5 text-[22px] font-bold tracking-[-0.02em]', ton.texte)}>{verdict.libelle}</h1>
          <p className="mt-1 text-[13.5px]"><strong>{verdict.respectees}</strong> règle(s) respectée(s) sur <strong>{verdict.evaluees}</strong></p>
          {texte?.reformulation && <p className="mt-2 max-w-[62ch] text-[14px]">{texte.reformulation}</p>}
          {texte?.tensions?.map((t) => <p key={t} className="mt-2 rounded-md border border-warn-bd bg-card px-3 py-2 text-[13px] text-warn">{t}</p>)}
        </div>
      </div>

      {verdict.etat === 'indetermine' && dossier.questions?.length > 0 && (
        <Card className="mt-4">
          <CardHeader><CardTitle>Ce qu'il me faut pour conclure</CardTitle></CardHeader>
          <CardContent><ul className="list-disc pl-5 text-[13.5px]">{dossier.questions.map((q) => <li key={q}>{q}</li>)}</ul></CardContent>
        </Card>
      )}

      {texte?.miroir?.length > 0 && (
        <>
          <Titre>Le miroir</Titre>
          <Card><CardContent className="py-1.5">
            <Phrases phrases={texte.miroir} ouvrir={ouvrirFait} />
            {estPersona && <p className="pb-2 pt-1 text-xs text-muted-foreground">« Tu as dit » cite une phrase type du profil {profil.nom} (scénario fictif de l'équipe), pas une saisie que tu as faite.</p>}
          </CardContent></Card>
        </>
      )}

      {texte?.pourquoi?.length > 0 && (
        <>
          <Titre>Pourquoi ce verdict</Titre>
          <Card><CardContent className="py-1.5"><Phrases phrases={texte.pourquoi} ouvrir={ouvrirFait} /></CardContent></Card>
        </>
      )}

      <Titre>Tes trois options</Titre>
      <div className={cn('grid gap-2.5', options.length === 3 ? 'sm:grid-cols-3' : 'sm:grid-cols-2')}>
        {options.map((o, i) => <Option key={o.nom} o={o} lettre={'ABC'[i]} meilleure={i === meilleure && i > 0} />)}
      </div>
      {texte?.ce_qui_changerait?.length > 0 && (
        <Card className="mt-2.5"><CardContent className="py-1.5"><Phrases phrases={texte.ce_qui_changerait} ouvrir={ouvrirFait} /></CardContent></Card>
      )}
      <div className="mt-4 flex flex-wrap items-center gap-2.5">
        {dossier.bascule?.cases?.length > 0
          ? <Button size="lg" onClick={onBascule}>Bouger les curseurs <ArrowRight className="size-4" /></Button>
          : <p className="text-[13px] text-muted-foreground">Les curseurs de bascule s'ouvrent dès que le verdict peut être calculé.</p>}
        <Button variant="outline" size="lg" onClick={onModifier}>Modifier mes réponses</Button>
      </div>

      <Titre>Les règles appliquées</Titre>
      <div className="grid items-start gap-3.5 md:grid-cols-[1.4fr_1fr]">
        <Card>
          <CardContent className="grid gap-0 py-1.5">
            {reglesTriees.map((r) => (
              <div key={r.code} className="grid gap-1.5 border-b border-border py-3 last:border-b-0">
                <div className="flex items-start justify-between gap-3">
                  <strong className="text-[13.5px] font-semibold">{r.libelle}</strong>
                  <PuceNiveau niveau={r.niveau} />
                </div>
                <p className="text-[13px]">{r.type && <Etiquette type={r.type} />} {r.explication}</p>
                <PucesFaits ids={r.faits} ouvrir={ouvrirFait} />
                {r.references?.length > 0 && (
                  <details className="text-[13px]">
                    <summary className="cursor-pointer text-muted-foreground">Sur quoi repose cette règle ?</summary>
                    <div className="mt-2"><ListeSources ids={r.references} /></div>
                  </details>
                )}
              </div>
            ))}
            <p className="py-2.5 text-xs text-muted-foreground">Ces règles sont du code, pas l'avis d'une IA. Le verdict ne peut pas les contredire.
              Les seuils (étiquette Hypothèse) sont des choix de l'équipe, au registre des chiffres plus bas.</p>
          </CardContent>
        </Card>

        <div className="grid min-w-0 gap-3.5">
          <Card>
            <CardHeader><CardTitle>La pire chute observée</CardTitle></CardHeader>
            <CardContent><GraphiqueChute ticker={demande.ticker} faitId={ids.chute} ouvrir={ouvrirFait} /></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Ce que le Sceptique a contesté</CardTitle></CardHeader>
            <CardContent className="grid gap-2.5">
              {objections.length ? objections.map((o) => (
                <div key={o.id} className="rounded-md bg-muted px-3 py-2 text-[13px]">
                  <p><span className="font-mono text-xs">{o.id}</span> {o.texte}</p>
                  <p className="mt-1 text-ok">↳ {o.reponse}</p>
                </div>
              )) : <p className="text-[13px] text-muted-foreground">Aucune objection.</p>}
            </CardContent>
          </Card>
        </div>
      </div>

      <Titre>Tous les chiffres utilisés</Titre>
      <Card className="overflow-x-auto">
        <table className="w-full border-collapse text-[13px]">
          <thead>
            <tr className="text-left text-xs text-muted-foreground">
              {['Id', "Ce que c'est", 'Valeur', 'Type'].map((h) => <th key={h} className="border-b border-border px-3 py-2 font-medium">{h}</th>)}
            </tr>
          </thead>
          <tbody>
            {faits.map((f) => (
              <tr key={f.id} className="border-b border-border last:border-b-0">
                <td className="px-3 py-2.5 align-top"><PucesFaits ids={[f.id]} ouvrir={ouvrirFait} /></td>
                <td className="px-3 py-2.5 align-top">{f.libelle}</td>
                <td className="px-3 py-2.5 align-top font-mono tabular-nums">
                  {typeof f.valeur === 'object' && f.valeur !== null ? Object.entries(f.valeur).map(([k, v]) => `${k} ${v}`).join(', ') : `${f.valeur} ${f.unite}`}
                </td>
                <td className="px-3 py-2.5 align-top"><Etiquette type={f.type} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <div className="mt-7 grid items-start gap-3.5 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Qualité des données</CardTitle></CardHeader>
          <CardContent>
            <ul className="m-0 grid list-none gap-1.5 p-0 text-[13px]">
              {qualite.map((c) => (
                <li key={c.code} className="flex gap-2">
                  <span className={cn('grid size-5 flex-none place-items-center rounded-full text-[11px] font-bold', c.statut === 'ok' ? 'bg-ok-bg text-ok' : 'bg-warn-bg text-warn')}>
                    {c.statut === 'ok' ? '✓' : '!'}
                  </span>
                  <span>{c.libelle} <span className="text-muted-foreground">— {c.detail}</span></span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Limites</CardTitle></CardHeader>
          <CardContent className="grid gap-3 py-1.5">
            <Phrases phrases={texte?.limites} ouvrir={ouvrirFait} />
            <div className="rounded-md bg-muted px-3 py-2.5 text-[13px]">
              <p><strong className="font-semibold">Comment ce texte a été vérifié.</strong> Rédigé par : {texte?.source}.</p>
              <p className="mt-1 text-xs text-muted-foreground">Avant d'être affiché, le code vérifie que chaque nombre existe déjà dans le dossier, que chaque F-n
                cité existe, et qu'aucune phrase ne conseille d'acheter ou de vendre. Un défaut est nommé et renvoyé à l'agent.</p>
              {texte?.controle?.length > 0 && <ul className="mt-1.5 list-disc pl-5 font-mono text-xs">{texte.controle.map((c) => <li key={c}>{c}</li>)}</ul>}
            </div>
            <p className="pb-2 text-xs text-muted-foreground">{texte?.avertissement}</p>
          </CardContent>
        </Card>
      </div>

      <Titre>Sources de cette analyse</Titre>
      <Card>
        <CardHeader>
          <CardDescription>Chaque chiffre vient d'un fichier du jeu de départ et d'une méthode appliquée par le code. Chaque règle et chaque
            agent s'appuient sur les références ci-dessous. Le niveau d'examen indique ce que l'équipe a réellement lu.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-5"><SourcesParType ids={sourcesDuDossier(dossier)} /></CardContent>
      </Card>
    </div>
  )
}
