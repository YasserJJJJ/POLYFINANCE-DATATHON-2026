import { useEffect } from 'react'
import { Etiquette } from './Base.jsx'

const affiche = (v) => (typeof v === 'object' && v !== null
  ? Object.entries(v).map(([k, x]) => `${k} : ${x}`).join(' · ')
  : String(v))

export default function TiroirFait({ fait, onFermer }) {
  useEffect(() => {
    const echap = (e) => e.key === 'Escape' && onFermer()
    window.addEventListener('keydown', echap)
    return () => window.removeEventListener('keydown', echap)
  }, [onFermer])
  if (!fait) return null
  return (
    <div className="voile" onClick={onFermer}>
      <aside className="tiroir" role="dialog" aria-modal="true" aria-labelledby="tiroir-titre" onClick={(e) => e.stopPropagation()}>
        <div className="tiroir-tete">
          <span className="mono">{fait.id}</span>
          <Etiquette type={fait.type} />
          <button type="button" className="bouton discret" onClick={onFermer} autoFocus>Fermer</button>
        </div>
        <h2 id="tiroir-titre">{fait.libelle}</h2>
        <p className="tiroir-valeur">{affiche(fait.valeur)} {fait.unite}</p>
        <dl>
          <dt>{fait.lu_ou_calcule === 'lu' ? 'Lu dans' : 'Source des données'}</dt>
          <dd>{fait.source}</dd>
          <dt>Méthode</dt>
          <dd>{fait.methode}</dd>
        </dl>
        <p className="muted petit">Ce chiffre a été produit par du code, pas par un modèle de langage.</p>
      </aside>
    </div>
  )
}
