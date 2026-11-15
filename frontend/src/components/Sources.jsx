// Sources : chaque chiffre, règle et agent renvoie au registre du backend (GET /api/sources).
import { createContext, useContext } from 'react'

export const RegistreContext = createContext(null)
export const useRegistre = () => useContext(RegistreContext)

const TYPES_SOURCE = {
  donnees: 'Données utilisées',
  reglementation: 'Réglementation canadienne et internationale',
  recherche: 'Recherche publiée',
  methode: 'Documentation de méthode',
  interne: 'Document de l’équipe',
}

const court = (ref) => `${String(ref.auteurs).split(/[,;(]/)[0].trim()} (${ref.annee})`
const lien = 'underline decoration-dotted decoration-muted-foreground/60 underline-offset-2 hover:decoration-foreground'

/** Petites références cliquables (lien vers la source, détail au survol). */
export function SourcesCompactes({ ids, prefixe = 'Sources :' }) {
  const registre = useRegistre()
  const refs = (ids || []).map((id) => [id, registre?.references?.[id]]).filter(([, r]) => r)
  if (!refs.length) return null
  return (
    <p className="text-xs text-muted-foreground">
      {prefixe}{' '}
      {refs.map(([id, r], i) => (
        <span key={id}>
          {i > 0 && ' · '}
          {r.lien
            ? <a href={r.lien} target="_blank" rel="noreferrer" className={lien} title={`${r.titre}. ${r.apport} (Examen : ${r.examen})`}>{court(r)}</a>
            : <abbr className={lien} title={`${r.titre}. ${r.apport} (Examen : ${r.examen})`}>{court(r)}</abbr>}
        </span>
      ))}
    </p>
  )
}

/** Liste complète : auteurs, année, titre, publication, lien, apport et niveau d'examen. */
export function ListeSources({ ids }) {
  const registre = useRegistre()
  const refs = [...new Set(ids || [])].map((id) => [id, registre?.references?.[id]]).filter(([, r]) => r)
  if (!refs.length) return null
  return (
    <ul className="m-0 grid list-none gap-3 p-0">
      {refs.map(([id, r]) => (
        <li key={id} className="grid gap-0.5 text-[13px]">
          <p>
            <strong className="font-semibold">{r.auteurs}</strong> ({r.annee}).{' '}
            {r.lien ? <a href={r.lien} target="_blank" rel="noreferrer" className={lien}>{r.titre}</a> : r.titre}.{' '}
            <span className="text-muted-foreground">{r.publication}.</span>
          </p>
          <p className="text-xs">{r.apport}</p>
          <p className="text-xs text-muted-foreground">Niveau d'examen : {r.examen}.</p>
        </li>
      ))}
    </ul>
  )
}

/** Toutes les sources d'un dossier (faits, règles, trace, limites). */
export function sourcesDuDossier(dossier) {
  const ids = new Set()
  const ajouter = (liste) => (liste || []).forEach((x) => ids.add(x))
  dossier.faits?.forEach((f) => ajouter(f.references))
  dossier.regles?.forEach((r) => ajouter(r.references))
  dossier.trace?.forEach((t) => ajouter(t.references))
  Object.values(dossier.texte || {}).forEach((v) => Array.isArray(v) && v.forEach((p) => ajouter(p?.references)))
  return [...ids]
}

export function SourcesParType({ ids }) {
  const registre = useRegistre()
  if (!registre) return <p className="text-xs text-muted-foreground">Registre des sources indisponible.</p>
  return Object.keys(TYPES_SOURCE)
    .map((type) => [type, ids.filter((id) => registre.references[id]?.type === type)])
    .filter(([, liste]) => liste.length)
    .map(([type, liste]) => (
      <div key={type} className="grid gap-2">
        <h3 className="text-[13px] font-semibold">{TYPES_SOURCE[type]} ({liste.length})</h3>
        <ListeSources ids={liste} />
      </div>
    ))
}
