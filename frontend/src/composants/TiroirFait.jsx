import { useEffect } from 'react'
import { Etiquette } from './Base.jsx'
import { ListeSources } from './Sources.jsx'

const affiche = (v) => (typeof v === 'object' && v !== null
  ? Object.entries(v).map(([k, x]) => `${k} : ${x}`).join(' · ')
  : String(v))

function Fait({ fait }) {
  return (
    <section className="tiroir-fait">
      <div className="tiroir-fait-tete">
        <Etiquette type={fait.type} />
        <span className="mono muted">{fait.id}</span>
      </div>
      <h3>{fait.libelle}</h3>
      <p className="tiroir-valeur">{affiche(fait.valeur)} {fait.unite}</p>
      <dl>
        <dt>{fait.lu_ou_calcule === 'lu' ? 'Lu dans' : 'Source des données'}</dt>
        <dd>{fait.source}</dd>
        <dt>Méthode</dt>
        <dd>{fait.methode}</dd>
      </dl>
      {fait.references?.length > 0 && (
        <>
          <h4 className="tiroir-sous-titre">Sur quoi repose ce chiffre</h4>
          <ListeSources ids={fait.references} />
        </>
      )}
      <p className="muted petit">
        {fait.type === 'HYPOTHESE'
          ? "Ce seuil est un choix de l'équipe, publié et appliqué par le code. Ce n'est pas un fait observé."
          : 'Ce chiffre a été produit par du code, pas par un modèle de langage.'}
      </p>
    </section>
  )
}

// Détail des chiffres d'une phrase ou d'une règle : ouvert seulement quand la personne clique sur « i ».
export default function TiroirFait({ faits, onFermer }) {
  useEffect(() => {
    const echap = (e) => e.key === 'Escape' && onFermer()
    window.addEventListener('keydown', echap)
    return () => window.removeEventListener('keydown', echap)
  }, [onFermer])
  const liste = (faits || []).filter(Boolean)
  if (!liste.length) return null
  return (
    <div className="voile" onClick={onFermer}>
      <aside className="tiroir" role="dialog" aria-modal="true" aria-labelledby="tiroir-titre" onClick={(e) => e.stopPropagation()}>
        <div className="tiroir-tete">
          <h2 id="tiroir-titre">{liste.length > 1 ? "D'où viennent ces chiffres" : "D'où vient ce chiffre"}</h2>
          <button type="button" className="bouton discret" onClick={onFermer} autoFocus>Fermer</button>
        </div>
        {liste.map((f) => <Fait key={f.id} fait={f} />)}
      </aside>
    </div>
  )
}
