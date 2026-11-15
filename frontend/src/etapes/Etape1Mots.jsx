import { useState } from 'react'
import { dollars } from '../api.js'

const AMORCES = ['Je veux ', "J'ai ", "Mais j'ai peur de "]

const PERSONAS_RESUME = {
  amira: { age: 26, risque: 'Risque élevé', horizon: '15 ans et plus', teste: 'Risque élevé ne veut pas dire tout accepter' },
  mateo: { age: 41, risque: 'Risque modéré', horizon: '8 à 12 ans', teste: 'Ses valeurs ESG comptent autant que le rendement' },
  robert: { age: 59, risque: 'Risque faible à modéré', horizon: '3 à 5 ans', teste: 'Une demande médiatisée face à sa retraite proche' },
}

export default function Etape1Mots({ personas, onPersona, onTexte }) {
  const [texte, setTexte] = useState('')

  const ajouterAmorce = (a) => setTexte((t) => (t && !t.endsWith(' ') ? `${t} ${a}` : `${t}${a}`))

  return (
    <section className="etape1">
      <div className="accroche">
        <p className="surtitre">Avant de cliquer sur « acheter »</p>
        <h1>Dis-nous ce que tu veux faire de ton argent. On vérifie si ça tient debout pour toi.</h1>
        <p className="lede">
          On reformule ta demande, on la confronte à ta situation avec des chiffres réels, et on te montre ce qui
          la rendrait raisonnable. On ne te dira jamais quoi acheter.
        </p>
      </div>

      <form className="carte saisie" onSubmit={(e) => { e.preventDefault(); if (texte.trim()) onTexte(texte.trim()) }}>
        <label htmlFor="texte-libre" className="titre-champ">Avec tes mots</label>
        <textarea id="texte-libre" rows={4} value={texte} onChange={(e) => setTexte(e.target.value)}
          placeholder="Ex. : Je veux mettre 10 000 $ en Bitcoin. J'ai 40 000 $ d'épargne. Mais j'ai peur de tout perdre." />
        <div className="amorces" aria-label="Pour t'aider à commencer">
          {AMORCES.map((a) => (
            <button key={a} type="button" className="amorce" onClick={() => ajouterAmorce(a)}>{a.trim()}…</button>
          ))}
        </div>
        <div className="actions">
          <button type="submit" className="bouton principal" disabled={!texte.trim()}>Continuer</button>
        </div>
      </form>

      <div className="separateur"><span>ou essaie avec un profil du défi</span></div>

      <div className="grille-personas">
        {personas ? Object.entries(personas).map(([cle, p]) => {
          const r = PERSONAS_RESUME[cle] || {}
          return (
            <button key={cle} type="button" className="carte persona" onClick={() => onPersona(cle)}>
              <span className="persona-tete">
                <span className="avatar" aria-hidden="true">{p.profil.nom[0]}</span>
                <span>
                  <strong>{p.profil.nom}</strong>
                  <span className="muted"> · {r.age} ans · {p.profil.profession}</span>
                </span>
              </span>
              <span className="persona-tags">
                <span className="tag">{r.risque}</span>
                <span className="tag">{r.horizon}</span>
              </span>
              <span className="persona-citation">« {p.demande.texte} »</span>
              <span className="persona-teste">{r.teste}</span>
              <span className="muted petit">Épargne fictive : {dollars(p.profil.epargne_totale_cad)}</span>
            </button>
          )
        }) : <p className="muted">Chargement des profils…</p>}
      </div>
    </section>
  )
}
