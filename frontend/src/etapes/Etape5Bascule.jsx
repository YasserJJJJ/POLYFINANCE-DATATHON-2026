import { useMemo, useState } from 'react'
import { dollars } from '../api.js'
import { ETATS, PuceVerdict } from '../composants/Base.jsx'
import { SECTEURS_FR } from './Etape2Verifier.jsx'
import { sourcesDuDossier, useRegistre } from '../composants/Sources.jsx'

const LEXIQUE = {
  'Pire chute': "La plus forte baisse entre un sommet et le creux qui suit, sur la période observée.",
  Volatilité: "L'ampleur habituelle des variations de prix. Plus elle est haute, plus le prix bouge fort, dans les deux sens.",
  Horizon: "Le temps avant d'avoir besoin de l'argent.",
  'Capacité de perte': "La baisse que ta situation te permet d'encaisser sans changer tes projets.",
  'Tolérance au risque': "La baisse que tu es prêt·e à vivre sans paniquer.",
  Corrélation: "À quel point deux placements montent et baissent en même temps (1 = toujours ensemble).",
}

function fiche(d, registre) {
  const p = d.profil, ev = p.evaluation, v = d.verdict
  const estPersona = ['Amira', 'Mateo', 'Robert'].includes(p.nom)
  const bloquees = d.regles.filter((r) => r.niveau === 'rouge' || r.niveau === 'orange')
  const volatil = (d.demande.mesures?.volatilite_pct ?? 0) > 25
  const questions = [
    volatil ? 'Quelle part de mon épargne serait raisonnable pour un placement aussi volatil ?'
      : 'Quelle part de mon épargne serait raisonnable pour ce placement ?',
    ...(bloquees.some((r) => r.code === 'exclusion') ? ['Quelles options respectent mes exclusions avec un profil de risque comparable ?'] : []),
    ...(bloquees.some((r) => r.code === 'horizon' || r.code === 'retrait') ? ["Comment protéger l'argent dont j'aurai besoin avant la fin de mon horizon ?"] : []),
    'Comment ce placement s\'intègre-t-il à ce que je détiens déjà ?',
  ]
  return [
    `# Ma demande, préparée pour mon rendez-vous`,
    '',
    `## Ce que je veux faire`,
    d.texte.reformulation,
    '',
    `## Ma situation`,
    `- Horizon : ${p.horizon_ans} an(s)`,
    `- Tolérance au risque : ${ev.tolerance}/100 · Capacité de perte : ${ev.capacite}/100 (on retient ${ev.score_retenu}/100)`,
    `- Somme à ne jamais risquer : ${dollars(p.somme_a_preserver_cad)}`,
    p.exclusions?.length ? `- Secteurs que je veux éviter : ${p.exclusions.map((s) => SECTEURS_FR[s] || s).join(', ')}` : '- Aucune exclusion déclarée',
    '',
    `## Le second avis obtenu`,
    `**${v.libelle}** (${v.respectees} règle(s) respectée(s) sur ${v.evaluees})`,
    ...bloquees.map((r) => `- ${r.libelle} : ${r.explication}`),
    '',
    `## Les options comparées`,
    ...d.options.map((o) => `- ${o.nom} : ${dollars(o.montant_cad)}, horizon ${o.horizon_ans} an(s) → ${ETATS[o.etat].libelle}`),
    '',
    `## Mes questions pour le conseiller`,
    ...questions.map((q) => `- ${q}`),
    '',
    `## Sur quoi repose ce second avis`,
    ...sourcesDuDossier(d).map((id) => registre?.references?.[id]).filter(Boolean)
      .map((r) => `- ${r.auteurs} (${r.annee}). ${r.titre}.${r.lien ? ` ${r.lien}` : ''} (examen : ${r.examen})`),
    '',
    `## Les mots à connaître`,
    ...Object.entries(LEXIQUE).map(([m, def]) => `- **${m}** : ${def}`),
    '',
    `_${d.texte.avertissement} Données 2021-11-12 → 2026-11-12 ; le passé ne prédit pas l'avenir. `
      + `Les scores et les seuils sont des hypothèses de l'équipe (barèmes publiés dans l'application)`
      + `${estPersona ? ", et les montants de ce profil sont fictifs" : ''}._`,
  ].join('\n')
}

const VIDE = { montants: [], horizons: [], cases: [] }

export default function Etape5Bascule({ dossier, onRetour, onRecommencer }) {
  // Verdict gris : le Gardien ne calcule pas de grille (bascule = {}). Avant, la page devenait blanche.
  const bascule = dossier.bascule?.cases?.length ? dossier.bascule : VIDE
  const montants = useMemo(() => [...bascule.montants].sort((a, b) => a - b), [bascule])
  // Montant de départ : la case de la demande (fraction 1 de la grille), même si le montant n'est pas entier.
  const [iM, setIM] = useState(Math.max(0, montants.indexOf(Math.round(dossier.demande.montant_cad))))
  const [h, setH] = useState(dossier.profil.horizon_ans)
  const [copie, setCopie] = useState('')
  const montant = montants[iM]
  const caseActuelle = bascule.cases.find((c) => c.montant_cad === montant && c.horizon_ans === h)
  const registre = useRegistre()
  const texteFiche = useMemo(() => fiche(dossier, registre), [dossier, registre])

  const copier = async () => {
    try { await navigator.clipboard.writeText(texteFiche); setCopie('Copié.') } catch { setCopie('Sélectionne le texte et copie-le.') }
  }
  const telecharger = () => {
    const url = URL.createObjectURL(new Blob([texteFiche], { type: 'text/markdown' }))
    const a = Object.assign(document.createElement('a'), { href: url, download: 'ma-demande-pour-mon-conseiller.md' })
    a.click(); URL.revokeObjectURL(url)
  }

  return (
    <section className="etape5">
      <p className="surtitre">Curseurs de bascule</p>
      <h1>Qu'est-ce qui rendrait ta demande raisonnable ?</h1>
      <p className="lede">Bouge le montant ou l'horizon : chaque position est un verdict du Gardien, calculé par le code,
        sans IA ({bascule.cases.length} combinaisons calculées pendant l'analyse).</p>
      {!bascule.cases.length && <p className="manque">Verdict impossible à calculer : complète d'abord les informations manquantes.</p>}

      <div className="colonnes">
        <div className="carte bascule">
          <div className={`bascule-verdict etat-${caseActuelle?.etat}`} aria-live="polite">
            <PuceVerdict etat={caseActuelle?.etat} grand />
          </div>
          <div className="champ">
            <label htmlFor="b-montant">Montant placé : <strong>{dollars(montant)}</strong></label>
            <input id="b-montant" type="range" min="0" max={montants.length - 1} value={iM} onChange={(e) => setIM(Number(e.target.value))} />
          </div>
          <div className="champ">
            <label htmlFor="b-horizon">Horizon : <strong>{h} an(s)</strong></label>
            <input id="b-horizon" type="range" min={bascule.horizons[0]} max={bascule.horizons.at(-1)} value={h ?? bascule.horizons[0] ?? 1} onChange={(e) => setH(Number(e.target.value))} />
          </div>
          <p className="muted petit">Ta demande de départ : {dollars(dossier.demande.montant_cad)} sur {dossier.profil.horizon_ans} an(s).</p>
        </div>

        <div className="carte">
          <h2>La carte complète</h2>
          <div className="defile-x">
            <div className="carte-chaleur" style={{ gridTemplateColumns: `72px repeat(${bascule.horizons.length}, minmax(14px, 1fr))` }}>
              {[...montants].reverse().map((m) => (
                <div key={m} className="rangee" style={{ display: 'contents' }}>
                  <span className="ax-y">{dollars(m)}</span>
                  {bascule.horizons.map((hz) => {
                    const c = bascule.cases.find((x) => x.montant_cad === m && x.horizon_ans === hz)
                    const e = ETATS[c?.etat] || ETATS.indetermine
                    const ici = m === montant && hz === h
                    return (
                      <button key={hz} type="button" title={`${dollars(m)}, ${hz} an(s) : ${e.libelle}`}
                        className={`cellule ${e.classe} ${ici ? 'ici' : ''}`}
                        onClick={() => { setIM(montants.indexOf(m)); setH(hz) }} aria-label={`${dollars(m)}, ${hz} ans`} />
                    )
                  })}
                </div>
              ))}
              <span />
              {bascule.horizons.map((hz) => <span key={hz} className="ax-x">{hz % 5 === 0 || hz === 1 ? hz : ''}</span>)}
            </div>
          </div>
          <ul className="legende-bascule" aria-label="Légende de la carte">
            {Object.entries(ETATS).map(([cle, e]) => (
              <li key={cle} className={e.classe}><i aria-hidden="true" /><span>{e.libelle}</span></li>
            ))}
          </ul>
          <p className="muted petit">Horizontal : horizon en années. Vertical : montant placé. Chaque case = le verdict du Gardien.</p>
        </div>
      </div>

      <div className="carte fiche">
        <div className="fiche-tete">
          <h2>Ta fiche pour ton conseiller</h2>
          <div className="actions">
            <button type="button" className="bouton" onClick={copier}>Copier</button>
            <button type="button" className="bouton" onClick={telecharger}>Télécharger (.md)</button>
            <span className="muted petit" aria-live="polite">{copie}</span>
          </div>
        </div>
        <pre className="fiche-texte">{texteFiche}</pre>
      </div>

      <div className="actions barre-actions">
        <button type="button" className="bouton discret" onClick={onRetour}>Retour au verdict</button>
        <button type="button" className="bouton" onClick={onRecommencer}>Nouvelle demande</button>
      </div>
    </section>
  )
}
