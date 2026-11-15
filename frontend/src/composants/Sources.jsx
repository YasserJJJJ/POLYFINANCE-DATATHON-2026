// Affichage des sources : chaque chiffre, règle et agent renvoie au registre du backend (GET /api/sources).
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

// « Markowitz (1952) » : forme courte pour une puce.
function court(ref) {
  const premier = String(ref.auteurs).split(/[,;(]/)[0].trim()
  return `${premier} (${ref.annee})`
}

/** Petites puces cliquables (lien vers la source, détail au survol). */
export function SourcesCompactes({ ids, prefixe = 'Sources :' }) {
  const registre = useRegistre()
  const refs = (ids || []).map((id) => [id, registre?.references?.[id]]).filter(([, r]) => r)
  if (!refs.length) return null
  return (
    <p className="sources-compactes">
      <span className="muted">{prefixe}</span>{' '}
      {refs.map(([id, r], i) => (
        <span key={id}>
          {i > 0 && ' · '}
          {r.lien
            ? <a href={r.lien} target="_blank" rel="noreferrer" title={`${r.titre}. ${r.apport} (Examen : ${r.examen})`}>{court(r)}</a>
            : <abbr title={`${r.titre}. ${r.apport} (Examen : ${r.examen})`}>{court(r)}</abbr>}
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
    <ul className="liste-sources">
      {refs.map(([id, r]) => (
        <li key={id}>
          <p>
            <strong>{r.auteurs}</strong> ({r.annee}). {r.lien ? <a href={r.lien} target="_blank" rel="noreferrer">{r.titre}</a> : r.titre}.{' '}
            <span className="muted">{r.publication}.</span>
          </p>
          <p className="petit">{r.apport}</p>
          <p className="muted petit">Niveau d'examen : {r.examen}.</p>
        </li>
      ))}
    </ul>
  )
}

/** Toutes les sources d'un dossier (faits, règles, trace, limites), regroupées par type. */
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
  if (!registre) return <p className="muted petit">Registre des sources indisponible.</p>
  const groupes = Object.keys(TYPES_SOURCE)
    .map((type) => [type, ids.filter((id) => registre.references[id]?.type === type)])
    .filter(([, liste]) => liste.length)
  return groupes.map(([type, liste]) => (
    <div key={type} className="groupe-sources">
      <h3>{TYPES_SOURCE[type]} ({liste.length})</h3>
      <ListeSources ids={liste} />
    </div>
  ))
}
