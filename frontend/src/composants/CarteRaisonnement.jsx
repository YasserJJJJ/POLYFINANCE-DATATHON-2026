import { useLayoutEffect, useMemo, useRef, useState } from 'react'
import { dollars } from '../api.js'
import { pourClient } from '../affichage.js'
import { NIVEAUX } from './Base.jsx'
import { SECTEURS_FR } from '../etapes/Etape2Verifier.jsx'

// Carte du raisonnement : des sources au verdict, de gauche à droite. Chaque trait vient du dossier lui-même :
// une règle cite les chiffres qu'elle utilise (regles[].faits), un chiffre mesuré vient des données, un seuil
// est un choix de l'équipe, et ce que la personne a déclaré est une source à part. Rien n'est recalculé ici.
const COLONNES = [['source', 'Sources'], ['mesure', 'Ce qui est mesuré ou déclaré'], ['seuil', "Seuils de l'équipe"],
  ['regle', 'Règles'], ['verdict', 'Verdict']]

const nombre = (v) => (Math.abs(v) >= 1000
  ? Math.round(v).toLocaleString('fr-CA') : String(Math.round(v * 10) / 10).replace('.', ','))

function valeurDuFait(f) {
  if (typeof f.valeur === 'number') return f.unite === '$' ? dollars(f.valeur) : `${nombre(f.valeur)} ${f.unite}`.trim()
  if (f.valeur && typeof f.valeur === 'object' && !Array.isArray(f.valeur)) {
    const nombres = Object.values(f.valeur).filter((x) => typeof x === 'number')
    return nombres.length && /corr/i.test(f.libelle) ? `jusqu'à ${nombre(Math.max(...nombres))}` : ''
  }
  return typeof f.valeur === 'string' && f.valeur.length < 30 ? (SECTEURS_FR[f.valeur] || f.valeur) : ''
}

// Intitulés courts pour la carte ; l'intitulé complet reste dans l'infobulle et pour les lecteurs d'écran.
const COURTS = [
  [/^Temps entre le creux et le retour au sommet.*/i, 'Retour au sommet après la pire chute'],
  [/^Sommet non retrouvé.*/i, 'Sommet pas encore retrouvé'],
  [/^Volatilité annualisée de (.+)/i, 'Volatilité de $1'],
  [/^Pire baisse du portefeuille avant la demande.*/i, "Ton portefeuille aujourd'hui : pire baisse"],
  [/^Pire baisse du portefeuille après la demande.*/i, 'Avec ta demande : pire baisse'],
  [/^Écart de pire baisse.*/i, 'Ce que ta demande change'],
  [/^Corrélation de .+ avec tes placements.*/i, 'Lien avec tes placements'],
  [/^Perte supportable retenue.*/i, 'Perte supportable'],
  [/^Capacité de perte.*/i, 'Capacité de perte'],
  [/^Part maximale de l'épargne dans un actif très volatil.*/i, 'Part maximale, actif très volatil'],
  [/^Part maximale de l'épargne dans un seul titre.*/i, 'Part maximale, un seul titre'],
  [/^Seuil « actif très volatil ».*/i, 'Actif « très volatil » au-delà de'],
  [/^Seuil de fausse diversification.*/i, 'Fausse diversification à partir de'],
  [/^Retrait jugé proche.*/i, 'Retrait jugé proche'],
  [/^Attribution de la perte supportable.*/i, 'Règle de partage de la perte'],
]
const complet = (t) => pourClient(t).replace(/\s*\(hypothèse de l'équipe\)/i, '')
const libelle = (t) => COURTS.reduce((acc, [motif, court]) => (motif.test(acc) ? acc.replace(motif, court) : acc), complet(t))

function construire(dossier) {
  const { profil: p, demande: d, verdict } = dossier
  const regles = dossier.regles.filter((r) => r.niveau !== 'non_evaluee')
  const codes = new Set(regles.map((r) => r.code))
  const faits = Object.fromEntries(dossier.faits.map((f) => [f.id, f]))
  const noeuds = []
  const liens = []
  const ajouter = (n) => { if (!noeuds.some((x) => x.id === n.id)) noeuds.push(n) }

  ajouter({ id: 's-toi', colonne: 'source', nature: 'sit', titre: 'Ce que tu as déclaré' })
  // Ce que la personne a déclaré, relié aux règles qui s'en servent
  const declares = []
  const part = p.evaluation?.poids_pct ?? (p.epargne_totale_cad && d.montant_cad ? Math.round(d.montant_cad / p.epargne_totale_cad * 100) : null)
  if (part != null) declares.push(['d-part', 'Part de ton épargne', `${nombre(part)} %`, ['concentration', 'capacite']])
  if (p.horizon_ans != null) declares.push(['d-horizon', 'Horizon', `${p.horizon_ans} an(s)`, ['horizon']])
  const concRouge = regles.some((r) => r.code === 'concentration' && r.niveau === 'rouge')
  if (p.retrait_prevu_ans != null) declares.push(['d-retrait', 'Retrait prévu dans', `${p.retrait_prevu_ans} an(s)`, ['retrait', ...(concRouge ? ['concentration'] : [])]])
  if (p.somme_a_preserver_cad != null) declares.push(['d-preserver', 'Somme à préserver', dollars(p.somme_a_preserver_cad), ['preserver']])
  if (p.fonds_urgence != null) declares.push(['d-urgence', "Fonds d'urgence", p.fonds_urgence ? 'oui' : 'non', ['coussin']])
  if (p.exclusions?.length) declares.push(['d-excl', 'Tes exclusions', p.exclusions.map((s) => SECTEURS_FR[s] || s).join(', '), ['exclusion']])
  for (const [id, titre, valeur, pour] of declares) {
    const utiles = pour.filter((c) => codes.has(c))
    if (!utiles.length) continue
    ajouter({ id, colonne: 'mesure', nature: 'sit', titre, valeur })
    liens.push(['s-toi', id])
    utiles.forEach((c) => liens.push([id, `r-${c}`]))
  }

  // Chiffres cités par les règles : mesurés (données) ou seuils (choix de l'équipe)
  const usd = d?.mesures?.devise === 'USD' || dossier.faits.some((f) => /USD\/CAD|Banque du Canada|taux BdC/i.test(`${f.methode} ${f.source}`))
  for (const r of regles) {
    for (const fid of new Set((r.faits || []).filter(Boolean))) {
      const f = faits[fid]
      if (!f) continue
      const seuil = f.type === 'HYPOTHESE'
      ajouter({ id: fid, fait: fid, colonne: seuil ? 'seuil' : 'mesure', nature: seuil ? 'hyp' : f.type === 'SCENARIO' ? 'scen' : 'fait',
        titre: libelle(f.libelle), complet: complet(f.libelle), valeur: valeurDuFait(f) })
      liens.push([fid, `r-${r.code}`])
      if (seuil) {
        if (/ton profil|ta situation/i.test(f.libelle)) liens.push(['s-toi', fid])   // le seuil dépend de tes réponses
      } else if (/assets_universe/i.test(f.source)) {
        ajouter({ id: 's-liste', colonne: 'source', nature: 'fait', titre: 'Liste des placements (organisateurs)' })
        liens.push(['s-liste', fid])
      } else {
        ajouter({ id: 's-prix', colonne: 'source', nature: 'fait', titre: 'Prix du marché (Yahoo Finance)' })
        liens.push(['s-prix', fid])
        if (usd) {
          ajouter({ id: 's-bdc', colonne: 'source', nature: 'fait', titre: 'Taux USD/CAD (Banque du Canada)' })
          liens.push(['s-bdc', fid])
        }
        if (f.type === 'SCENARIO') liens.push(['s-toi', fid])   // une simulation part aussi de ta demande
      }
    }
  }
  for (const r of regles) {
    ajouter({ id: `r-${r.code}`, colonne: 'regle', nature: 'regle', titre: r.libelle, niveau: r.niveau })
    liens.push([`r-${r.code}`, 'v'])
  }
  ajouter({ id: 'v', colonne: 'verdict', nature: 'verdict', titre: verdict.libelle, etat: verdict.etat })
  return { noeuds, liens: liens.filter(([a, b]) => noeuds.some((n) => n.id === a) && noeuds.some((n) => n.id === b)) }
}

function voisins(liens, depart, sens) {
  const vus = new Set([depart])
  const pile = [depart]
  while (pile.length) {
    const id = pile.pop()
    for (const [a, b] of liens) {
      const suivant = sens === 'amont' ? (b === id ? a : null) : (a === id ? b : null)
      if (suivant && !vus.has(suivant)) { vus.add(suivant); pile.push(suivant) }
    }
  }
  return vus
}

export default function CarteRaisonnement({ dossier, ouvrirFait, surligne = [] }) {
  const { noeuds, liens } = useMemo(() => construire(dossier), [dossier])
  const [actif, setActif] = useState(null)
  const [traits, setTraits] = useState({ largeur: 0, hauteur: 0, chemins: [] })
  const cadre = useRef(null)
  const elements = useRef({})

  // Un chiffre survolé allume ce dont il vient et ce qu'il décide ; sinon, les chiffres venus de « d'après les analyses ».
  const allumes = useMemo(() => {
    const departs = actif ? [actif] : surligne.filter((id) => noeuds.some((n) => n.id === id))
    const s = new Set()
    departs.forEach((id) => { voisins(liens, id, 'amont').forEach((x) => s.add(x)); voisins(liens, id, 'aval').forEach((x) => s.add(x)) })
    return s
  }, [actif, surligne, liens, noeuds])

  useLayoutEffect(() => {
    const dessiner = () => {
      const base = cadre.current?.getBoundingClientRect()
      if (!base) return
      const chemins = liens.map(([a, b]) => {
        const ea = elements.current[a], eb = elements.current[b]
        if (!ea || !eb) return null
        const ra = ea.getBoundingClientRect(), rb = eb.getBoundingClientRect()
        const x1 = ra.right - base.left, y1 = ra.top + ra.height / 2 - base.top
        const x2 = rb.left - base.left, y2 = rb.top + rb.height / 2 - base.top
        return { a, b, d: `M${x1},${y1} C${(x1 + x2) / 2},${y1} ${(x1 + x2) / 2},${y2} ${x2},${y2}` }
      }).filter(Boolean)
      setTraits({ largeur: base.width, hauteur: base.height, chemins })
    }
    dessiner()
    const obs = new ResizeObserver(dessiner)
    obs.observe(cadre.current)
    return () => obs.disconnect()
  }, [liens, noeuds])

  const allume = actif || surligne.length ? allumes : null
  return (
    <div className="carte-raisonnement" ref={cadre}>
      <svg className="liens-raisonnement" width={traits.largeur} height={traits.hauteur} aria-hidden="true">
        {traits.chemins.map((c, i) => (
          <path key={`${c.a}-${c.b}-${i}`} d={c.d} className={allume ? (allume.has(c.a) && allume.has(c.b) ? 'allume' : 'eteint') : ''} />
        ))}
      </svg>
      <div className="colonnes-raisonnement">
        {COLONNES.map(([cle, nom]) => (
          <div key={cle} className="colonne-raisonnement">
            <p className="titre-colonne">{nom}</p>
            {noeuds.filter((n) => n.colonne === cle).map((n) => {
              const sert = liens.filter(([a]) => a === n.id).map(([, b]) => noeuds.find((x) => x.id === b)?.titre).filter(Boolean)
              const classes = ['noeud-raisonnement', `n-${n.nature}`, n.niveau ? `niveau-${n.niveau}` : '', n.etat ? `etat-${n.etat}` : '',
                allume ? (allume.has(n.id) ? 'allume' : 'eteint') : ''].join(' ')
              return (
                <button key={n.id} type="button" ref={(el) => { elements.current[n.id] = el }} className={classes}
                  data-fait={n.fait} title={n.complet || n.titre} onMouseEnter={() => setActif(n.id)} onMouseLeave={() => setActif(null)}
                  onFocus={() => setActif(n.id)} onBlur={() => setActif(null)}
                  onClick={() => n.fait && ouvrirFait(n.fait)}
                  aria-label={`${n.complet || n.titre}${n.valeur ? ` : ${n.valeur}` : ''}${n.niveau ? ` (${NIVEAUX[n.niveau]?.libelle})` : ''}${sert.length ? `. Sert à : ${sert.join(', ')}` : ''}`}>
                  {n.niveau && <span className={`puce-niveau ${NIVEAUX[n.niveau]?.classe}`}>{NIVEAUX[n.niveau]?.libelle}</span>}
                  <span className="noeud-titre">{n.titre}</span>
                  {n.valeur && <strong className="noeud-valeur">{n.valeur}</strong>}
                </button>
              )
            })}
          </div>
        ))}
      </div>
    </div>
  )
}
