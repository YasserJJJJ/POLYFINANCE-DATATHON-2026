import { useEffect, useState } from 'react'
import { api, dollars } from '../api.js'
import { PuceNiveau, PuceVerdict } from '../composants/Base.jsx'

// Même question posée par 3 profils : la démonstration que le profil change vraiment la réponse.
export default function Comparer({ personas }) {
  const [memeDemande, setMemeDemande] = useState(true)
  const [resultats, setResultats] = useState({})
  const ref = personas.robert.demande

  useEffect(() => {
    setResultats({})
    Object.entries(personas).forEach(([cle, p]) => {
      const montant = Math.round(p.profil.epargne_totale_cad * 0.2)
      const demande = memeDemande
        ? { texte: `Je veux mettre ${montant} $ dans Tesla, tout le monde en parle.`, ticker: ref.ticker, montant_cad: montant }
        : p.demande
      api.analyser(p.profil, demande).then((d) => setResultats((r) => ({ ...r, [cle]: d })))
    })
  }, [personas, memeDemande, ref])

  return (
    <section className="comparer">
      <p className="surtitre">Comparer</p>
      <h1>{memeDemande ? `La même idée, ${ref.ticker} pour 20 % de l'épargne, dans trois vies différentes.` : 'Chaque profil avec sa propre demande.'}</h1>
      <div className="bascule-mode" role="group" aria-label="Mode de comparaison">
        <button type="button" className={`choix ${memeDemande ? 'actif' : ''}`} aria-pressed={memeDemande} onClick={() => setMemeDemande(true)}>Même demande</button>
        <button type="button" className={`choix ${!memeDemande ? 'actif' : ''}`} aria-pressed={!memeDemande} onClick={() => setMemeDemande(false)}>Leur propre demande</button>
      </div>
      <div className="trois-colonnes">
        {Object.entries(personas).map(([cle, p]) => {
          const d = resultats[cle]
          const bloquantes = d?.regles.filter((r) => r.niveau === 'rouge' || r.niveau === 'orange') || []
          return (
            <article key={cle} className={`carte colonne-persona ${d ? `etat-${d.verdict.etat}` : ''}`}>
              <p className="persona-nom"><span className="avatar" aria-hidden="true">{p.profil.nom[0]}</span>{p.profil.nom}, {p.profil.age} ans</p>
              <p className="muted petit">Horizon {p.profil.horizon_ans} ans · épargne fictive {dollars(p.profil.epargne_totale_cad)}</p>
              {d ? (
                <>
                  <p className="reformulation petite">{d.texte.reformulation}</p>
                  <PuceVerdict etat={d.verdict.etat} />
                  <p className="compte-regles">{d.verdict.respectees}/{d.verdict.evaluees} règles respectées</p>
                  <ul className="regles compactes">
                    {bloquantes.map((r) => (
                      <li key={r.code} className={`regle n-${r.niveau}`}>
                        <div className="regle-tete"><strong>{r.libelle}</strong><PuceNiveau niveau={r.niveau} /></div>
                        <p>{r.explication}</p>
                      </li>
                    ))}
                  </ul>
                  {d.options[1]?.changement && (
                    <p className="ajustement">Version ajustée : {dollars(d.options[1].montant_cad)} sur {d.options[1].horizon_ans} an(s)</p>
                  )}
                </>
              ) : <p className="muted">Analyse en cours…</p>}
            </article>
          )
        })}
      </div>
    </section>
  )
}
