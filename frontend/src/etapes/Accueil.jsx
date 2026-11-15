import { useState } from 'react'
import FondAnime from '../composants/FondAnime.jsx'

const POINTS = [
  ['Les chiffres viennent du calcul', "Aucun nombre n'est écrit par l'IA : elle comprend, conteste et explique."],
  ['Chaque chiffre a sa source', 'Un clic ouvre la donnée, la méthode et la référence.'],
  ['Un verdict gris quand il manque une donnée', "L'outil préfère ne pas conclure plutôt que deviner."],
]

export default function Accueil({ nom, sousTitre, onCommencer, onComparer }) {
  const [depart, setDepart] = useState(false)

  const commencer = () => {
    setDepart(true)
    window.setTimeout(onCommencer, 350)
  }

  return (
    <div className={`accueil ${depart ? 'accueil-depart' : ''}`}>
      <FondAnime className="accueil-fond" />
      <div className="accueil-voile" aria-hidden="true" />

      <div className="accueil-int">
        <header className="accueil-tete">
          <span className="marque">
            <span className="marque-signe" aria-hidden="true">≠</span>
            {nom}
            <span className="marque-sous">{sousTitre}</span>
          </span>
          <span className="tag">Simulation · profils fictifs</span>
        </header>

        <main className="accueil-centre">
          <div className="accueil-texte">
            <h1>Avant d'investir, fais vérifier ton idée.</h1>
            <p className="lede">
              Dis ce que tu veux faire de ton argent, avec tes mots. {nom} reformule ta demande, la confronte à ta
              situation avec des chiffres réels, et te montre ce qui la rendrait acceptable. Il ne te dira jamais quoi
              acheter.
            </p>
            <div className="actions accueil-actions">
              <button type="button" className="bouton principal grand" onClick={commencer}>Commencer →</button>
              <span className="muted petit">Environ 2 minutes</span>
            </div>
            <button type="button" className="bouton discret accueil-comparer" onClick={onComparer}>
              Ou voir la même demande pour les 3 profils du défi
            </button>
          </div>
        </main>

        <footer className="accueil-points">
          {POINTS.map(([titre, detail]) => (
            <div key={titre}>
              <strong>{titre}</strong>
              <p className="muted petit">{detail}</p>
            </div>
          ))}
        </footer>
        <p className="accueil-avert muted petit">
          Simulation éducative. Aucune transaction réelle et aucun conseil financier personnalisé. Le passé ne prédit pas
          l'avenir.
        </p>
      </div>
    </div>
  )
}
