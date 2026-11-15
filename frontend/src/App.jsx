import { useEffect, useState } from 'react'
import { api } from './api.js'
import Etape1Mots from './etapes/Etape1Mots.jsx'
import Etape2Verifier from './etapes/Etape2Verifier.jsx'
import Etape3Trace from './etapes/Etape3Trace.jsx'
import Etape4Verdict from './etapes/Etape4Verdict.jsx'
import Etape5Bascule from './etapes/Etape5Bascule.jsx'
import Comparer from './etapes/Comparer.jsx'
import TiroirFait from './composants/TiroirFait.jsx'

export const NOM_PRODUIT = 'AlphaForge AI'
export const SOUS_TITRE = 'Second avis'

const ETAPES = ['Tes mots', 'On vérifie', 'Analyse', 'Verdict', 'Curseurs']

const PROFIL_VIERGE = {
  nom: 'Toi', age: null, experience: null, horizon_ans: null, tolerance: null, reponses_tolerance: {},
  epargne_totale_cad: null, somme_a_preserver_cad: null, revenu_stable: null, fonds_urgence: null,
  dettes_importantes: null, retrait_prevu_ans: null, exclusions: [], portefeuille_actuel: [], citations: [],
}

export default function App() {
  const [etape, setEtape] = useState(0)
  const [vue, setVue] = useState('parcours')
  const [personas, setPersonas] = useState(null)
  const [actifs, setActifs] = useState([])
  const [questions, setQuestions] = useState([])
  const [profil, setProfil] = useState(PROFIL_VIERGE)
  const [demande, setDemande] = useState({ texte: '', ticker: null, montant_cad: null })
  const [dossier, setDossier] = useState(null)
  const [faitOuvert, setFaitOuvert] = useState(null)
  const [erreur, setErreur] = useState(null)

  const [sante, setSante] = useState(null)

  useEffect(() => {
    Promise.all([api.personas(), api.actifs(), api.questions(), api.sante()])
      .then(([p, a, q, s]) => { setPersonas(p); setActifs(a); setQuestions(q); setSante(s) })
      .catch((e) => setErreur(`Impossible de joindre l'API. Lance-la avec « uvicorn api:app --port 8000 » dans backend/. (${e.message})`))
  }, [])

  const choisirPersona = (cle) => {
    const p = personas[cle]
    setProfil({ ...PROFIL_VIERGE, ...p.profil })
    setDemande({ ...p.demande })
  }

  const partirDeMesMots = (texte) => {
    setProfil((p) => ({ ...p, citations: texte.split(/(?<=[.!?])\s+/).filter((s) => s.trim().length > 3) }))
    setDemande({ texte, ticker: null, montant_cad: null })
  }

  const lancer = async () => {
    setDossier(null)
    setEtape(2)
    try {
      setDossier(await api.analyser(profil, demande))
    } catch (e) {
      // Sans dossier, l'écran d'analyse attendrait sans fin : on revient à l'étape 2, réponses conservées.
      setEtape(1)
      setErreur(`L'analyse n'a pas pu aboutir. Vérifie tes réponses, puis relance. (${e.message})`)
    }
  }

  const recommencer = () => { setEtape(0); setDossier(null); setProfil(PROFIL_VIERGE); setDemande({ texte: '', ticker: null, montant_cad: null }) }

  return (
    <div className="app">
      <header className="entete">
        <div className="entete-int">
          <button type="button" className="marque" onClick={() => { setVue('parcours'); recommencer() }}>
            <span className="marque-signe" aria-hidden="true">≠</span>
            {NOM_PRODUIT}
            <span className="marque-sous">{SOUS_TITRE}</span>
          </button>
          {vue === 'parcours' && (
            <ol className="etapes" aria-label="Étapes du parcours">
              {ETAPES.map((nom, i) => (
                <li key={nom} className={i === etape ? 'actuelle' : i < etape ? 'faite' : ''}>
                  <span className="etape-num">{i + 1}</span>
                  <span className="etape-nom">{nom}</span>
                </li>
              ))}
            </ol>
          )}
          {sante && (
            <span className={`etat-agents ${sante.llm ? 'actifs' : ''}`}
              title={sante.llm ? `${sante.modeles.principal} et ${sante.modeles.leger}` : sante.raison || ''}>
              <i aria-hidden="true" />
              {sante.llm ? 'Agents IA : Bedrock' : 'Agents : mode hors ligne'}
            </span>
          )}
          <button type="button" className="bouton discret" onClick={() => setVue(vue === 'parcours' ? 'comparer' : 'parcours')}>
            {vue === 'parcours' ? 'Comparer les 3 profils' : 'Retour au parcours'}
          </button>
        </div>
      </header>

      <main className="contenu">
        {erreur && (
          <div className="alerte" role="alert">
            {erreur}
            <button type="button" className="bouton discret" onClick={() => setErreur(null)}>Fermer</button>
          </div>
        )}

        {vue === 'comparer' && personas && <Comparer personas={personas} ouvrirFait={setFaitOuvert} />}

        {vue === 'parcours' && (
          <>
            {etape === 0 && (
              <Etape1Mots personas={personas} onPersona={(cle) => { choisirPersona(cle); setEtape(1) }}
                onTexte={(t) => { partirDeMesMots(t); setEtape(1) }} />
            )}
            {etape === 1 && (
              <Etape2Verifier profil={profil} setProfil={setProfil} demande={demande} setDemande={setDemande}
                actifs={actifs} questions={questions} onRetour={() => setEtape(0)} onLancer={lancer} />
            )}
            {etape === 2 && <Etape3Trace dossier={dossier} onFini={() => setEtape(3)} ouvrirFait={setFaitOuvert} />}
            {etape === 3 && dossier && (
              <Etape4Verdict dossier={dossier} ouvrirFait={setFaitOuvert} onBascule={() => setEtape(4)}
                onModifier={() => setEtape(1)} />
            )}
            {etape === 4 && dossier && (
              <Etape5Bascule dossier={dossier} onRetour={() => setEtape(3)} onRecommencer={recommencer} />
            )}
          </>
        )}
      </main>

      <footer className="pied">
        Simulation éducative. Aucune transaction réelle, aucun conseil financier personnalisé. Données publiques
        2021-11-12 → 2026-11-12 (Yahoo Finance, Banque du Canada, FRED). Montants des profils fictifs.
      </footer>

      {faitOuvert && dossier && (
        <TiroirFait fait={dossier.faits.find((f) => f.id === faitOuvert)} onFermer={() => setFaitOuvert(null)} />
      )}
    </div>
  )
}
