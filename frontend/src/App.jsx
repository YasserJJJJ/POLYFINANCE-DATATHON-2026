import { useEffect, useState } from 'react'
import { api, dollars } from './api.js'
import { CHAMPS_DEMANDE, CHAMPS_PROFIL } from './fichierClient.js'
import Etape1Mots from './etapes/Etape1Mots.jsx'
import Etape2Verifier from './etapes/Etape2Verifier.jsx'
import Etape3Trace from './etapes/Etape3Trace.jsx'
import Etape4Verdict from './etapes/Etape4Verdict.jsx'
import Etape5Bascule from './etapes/Etape5Bascule.jsx'
import Comparer from './etapes/Comparer.jsx'
import TiroirFait from './composants/TiroirFait.jsx'
import { RegistreContext } from './composants/Sources.jsx'
import { installerRepliables } from './repliable.js'

export const NOM_PRODUIT = 'AlphaForge AI'
export const SOUS_TITRE = 'Second avis'

const ETAPES = ['Tes mots', 'On vérifie', 'Analyse', 'Verdict', 'Curseurs']
const ROMAINS = ['I', 'II', 'III', 'IV', 'V']

const DIRECT_VIDE = { trace: [], objections: [], faits: [] }

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
  const [direct, setDirect] = useState(DIRECT_VIDE)   // étapes reçues pendant l'analyse, avant le dossier complet
  const [faitOuvert, setFaitOuvert] = useState(null)
  const [erreur, setErreur] = useState(null)
  const [champsFichier, setChampsFichier] = useState([])   // informations reprises d'un fichier déposé
  const [relance, setRelance] = useState(false)             // nouvelle analyse lancée depuis le verdict
  const [initiale, setInitiale] = useState('')              // demande de départ, gardée dans la conversation
  const [echanges, setEchanges] = useState([])
  const [envoi, setEnvoi] = useState(false)
  const [editions, setEditions] = useState([])   // chaque analyse reçue, gardée telle quelle pour être relue
  const [lue, setLue] = useState(null)           // index de l'édition relue ; null = la dernière

  // Thème : clair (papier) ou sombre. Le choix de la personne est gardé ; à défaut, on suit le réglage du système.
  const [theme, setTheme] = useState(() => {
    try { const t = localStorage.getItem('folio-theme'); if (t === 'clair' || t === 'sombre') return t } catch (e) { /* stockage indisponible */ }
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'sombre' : 'clair'
  })
  useEffect(() => {
    document.documentElement.dataset.theme = theme
    try { localStorage.setItem('folio-theme', theme) } catch (e) { /* le thème reste valable pour cette page */ }
  }, [theme])

  const [sante, setSante] = useState(null)
  useEffect(() => installerRepliables(document.querySelector('.contenu')), [])
  const [registre, setRegistre] = useState(null)

  useEffect(() => {
    Promise.all([api.personas(), api.actifs(), api.questions(), api.sante()])
      .then(([p, a, q, s]) => { setPersonas(p); setActifs(a); setQuestions(q); setSante(s) })
      .then(() => api.sources().then(setRegistre).catch(() => setRegistre(null)))
      .catch((e) => setErreur(`Impossible de joindre l'API. Lance-la avec « uvicorn api:app --port 8000 » dans backend/. (${e.message})`))
  }, [])

  // Même persona, mais la demande ne nomme aucun placement : le Gardien juge le plan sur toute la liste.
  const choisirPersonaSansPlacement = (cle) => {
    const p = personas[cle]
    setProfil({ ...PROFIL_VIERGE, ...p.profil })
    setDemande({ texte: `J'ai ${dollars(p.demande.montant_cad)} à placer.`, ticker: null, montant_cad: p.demande.montant_cad })
    setChampsFichier([])
  }

  const choisirPersona = (cle) => {
    const p = personas[cle]
    setProfil({ ...PROFIL_VIERGE, ...p.profil })
    setDemande({ ...p.demande })
    setChampsFichier([])
  }

  // Phrase seule, fichier seul, ou les deux : le fichier remplit ce qu'il connaît, la phrase complète le reste
  // (le Profileur ne remplit que les champs encore vides).
  const partirDe = ({ texte, fichier }) => {
    const phrases = texte.split(/(?<=[.!?])\s+/).filter((s) => s.trim().length > 3)
    const duFichier = fichier?.profil || {}
    setProfil({ ...PROFIL_VIERGE, ...duFichier, citations: [...(duFichier.citations || []), ...phrases] })
    setDemande({ ticker: null, montant_cad: null, ...(fichier?.demande || {}), texte: texte || fichier?.demande?.texte || '' })
    setChampsFichier(fichier ? fichier.lus : [])
  }

  // surPlace : relance depuis le verdict (puce modifiée) ; l'ancien résultat reste affiché jusqu'au nouveau.
  const lancer = async ({ surPlace = false, profil: p = profil, demande: dm = demande } = {}) => {
    setDirect(DIRECT_VIDE)
    if (surPlace) setRelance(true)
    else { setDossier(null); setEtape(2); setInitiale(dm.texte || ''); setEchanges([]) }
    const suivre = (m) => setDirect((d) => ({
      trace: [...d.trace, m.etape],
      objections: m.objections.length ? m.objections : d.objections,
      faits: m.faits,
    }))
    try {
      // texte_lu : la personne a relu et corrigé l'étape 2 ; l'analyse ne re-remplit pas un champ qu'elle a vidé.
      const nouveau = await api.analyserEnDirect(p, { ...dm, texte_lu: true }, surPlace ? () => {} : suivre)
      setDossier(nouveau)
      setEditions((e) => [...e, { dossier: nouveau, profil: p, demande: dm, heure: Date.now() }])
      setLue(null)
      return nouveau
    } catch (e) {
      // Sans dossier, l'écran d'analyse attendrait sans fin : on revient à l'étape 2, réponses conservées.
      if (!surPlace) setEtape(1)
      setErreur(e.message)
      return null
    } finally {
      setRelance(false)
    }
  }

  const relancer = (p, dm) => {
    const { evaluation, ...saisi } = p   // l'évaluation est recalculée par le backend
    setProfil(saisi)
    setDemande(dm)
    return lancer({ surPlace: true, profil: saisi, demande: dm })
  }

  // Un message après le verdict : s'il change la demande, on relance ; sinon, c'est une question.
  const envoyerMessage = async (texte) => {
    const ajouter = (...m) => setEchanges((e) => [...e, ...m])
    ajouter({ auteur: 'toi', texte })
    setEnvoi(true)
    try {
      // Lu sur un profil vierge : on récupère tout ce que le message dit, pour l'appliquer par-dessus la demande.
      const lu = await api.comprendre({ ...PROFIL_VIERGE, nom: profil.nom }, { texte, ticker: null, montant_cad: null })
      const champs = lu.profil?.extraits?.champs || {}
      const cles = Object.keys(champs).filter((k) => champs[k] !== null && champs[k] !== undefined)
      if (cles.length) {
        const { ticker, montant_cad: montant, ...pourProfil } = Object.fromEntries(cles.map((k) => [k, champs[k]]))
        const affiche = (k, v) => `${(CHAMPS_PROFIL[k] || CHAMPS_DEMANDE[k] || [null, k])[1]} : ${
          k.endsWith('_cad') ? dollars(v) : Array.isArray(v) ? v.join(', ') : typeof v === 'boolean' ? (v ? 'oui' : 'non') : v}`
        ajouter({ auteur: 'outil', texte: `Pris en compte : ${cles.map((k) => affiche(k, champs[k])).join(' · ')}. Nouvelle analyse…` })
        const nouveau = await relancer(
          { ...profil, ...pourProfil, citations: [...(profil.citations || []), texte] },
          { ...demande, ...(ticker ? { ticker } : {}), ...(montant ? { montant_cad: montant } : {}),
            texte: [demande.texte, texte].filter(Boolean).join(' ') })
        if (nouveau) ajouter({ auteur: 'outil', texte: `Nouveau résultat : ${nouveau.verdict.libelle}.` })
      } else {
        const r = await api.preciser(dossier, texte)
        ajouter({ auteur: 'outil', texte: r.reponse, faits: r.faits })
      }
    } catch (e) {
      ajouter({ auteur: 'outil', texte: `Je n'ai pas pu traiter ce message (${e.message}).` })
    } finally {
      setEnvoi(false)
    }
  }

  // Relire une édition : son dossier, avec les entrées qui l'ont produite. Rien n'est recalculé.
  const voirEdition = (i) => {
    const e = editions[i]
    if (!e) return
    setDossier(e.dossier); setProfil(e.profil); setDemande(e.demande)
    setLue(i === editions.length - 1 ? null : i); setEtape(3)
  }
  const indexEdition = lue ?? editions.length - 1

  // Toujours une liste d'identifiants : une phrase peut s'appuyer sur plusieurs chiffres.
  const ouvrirFait = (ids) => setFaitOuvert([].concat(ids))

  const recommencer = () => {
    setEtape(0); setDossier(null); setProfil(PROFIL_VIERGE); setDemande({ texte: '', ticker: null, montant_cad: null })
    setChampsFichier([]); setEchanges([]); setInitiale(''); setEditions([]); setLue(null)
  }

  return (
    <RegistreContext.Provider value={registre}>
    <div className="app">
      <header className="entete">
        <div className="entete-int">
          <div className="manchette-gauche">
            <button type="button" className="lien-retour" onClick={() => { setVue('parcours'); recommencer() }}>← Nouvelle demande</button>
            <button type="button" className="choix-theme" role="switch" aria-checked={theme === 'sombre'}
              onClick={() => setTheme(theme === 'sombre' ? 'clair' : 'sombre')} title="Changer de thème">
              <span aria-hidden="true">{theme === 'sombre' ? '☾' : '☼'}</span> Thème {theme === 'sombre' ? 'sombre' : 'clair'}
            </button>
          </div>
          <button type="button" className="marque" onClick={() => { setVue('parcours'); recommencer() }} aria-label={`${NOM_PRODUIT}, ${SOUS_TITRE} : revenir au début`}>
            {NOM_PRODUIT}
            <span className="marque-sous">{SOUS_TITRE}</span>
          </button>
          <div className="manchette-droite">
            <div>Le dossier de décision</div>
            <div>{editions.length === 0 ? 'Simulation éducative'
              : `${lue !== null ? 'Archive' : 'Édition'} ${indexEdition + 1} sur ${editions.length} · ${relance ? 'analyse en cours' : 'analyse terminée'}`}</div>
            {sante && (
              <span className={`etat-agents ${sante.llm ? 'actifs' : ''}`}
                title={sante.llm ? `${sante.modeles.principal} et ${sante.modeles.leger}` : sante.raison || ''}>
                <i aria-hidden="true" />
                {sante.llm ? 'Agents IA : Bedrock' : 'Agents : mode hors ligne'}
              </span>
            )}
          </div>
          <div className="barre-etapes">
            {vue === 'parcours' ? (
              <ol className="etapes" aria-label="Étapes du parcours">
                {ETAPES.map((nom, i) => (
                  <li key={nom} className={i === etape ? 'actuelle' : i < etape ? 'faite' : ''} aria-current={i === etape ? 'step' : undefined}>
                    <span className="etape-num" aria-hidden="true">{ROMAINS[i]}</span>
                    <span className="etape-nom">{nom}</span>
                  </li>
                ))}
              </ol>
            ) : <span />}
            <button type="button" className="bouton discret" onClick={() => setVue(vue === 'parcours' ? 'comparer' : 'parcours')}>
              {vue === 'parcours' ? 'Comparer les 3 profils' : 'Retour au parcours'}
            </button>
          </div>
        </div>
      </header>

      <main className="contenu">
        {erreur && (
          <div className="alerte" role="alert">
            {erreur}
            <button type="button" className="bouton discret" onClick={() => setErreur(null)}>Fermer</button>
          </div>
        )}

        {vue === 'comparer' && personas && <Comparer personas={personas} />}

        {vue === 'parcours' && (
          <>
            {etape === 0 && (
              <Etape1Mots personas={personas} onPersona={(cle) => { choisirPersona(cle); setEtape(1) }}
                onPersonaSansPlacement={(cle) => { choisirPersonaSansPlacement(cle); setEtape(1) }}
                onDemarrer={(entree) => { partirDe(entree); setEtape(1) }} />
            )}
            {etape === 1 && (
              <Etape2Verifier profil={profil} setProfil={setProfil} demande={demande} setDemande={setDemande} champsFichier={champsFichier}
                actifs={actifs} questions={questions} onRetour={() => setEtape(0)} onLancer={lancer} />
            )}
            {etape === 2 && <Etape3Trace dossier={dossier} direct={direct} onFini={() => setEtape(3)} ouvrirFait={ouvrirFait} />}
            {etape === 3 && dossier && (
              <Etape4Verdict dossier={dossier} ouvrirFait={ouvrirFait} onBascule={() => setEtape(4)}
                onModifier={() => setEtape(1)} saisie={{ profil, demande }} actifs={actifs} relance={relance}
                onRelancer={relancer} onAnalyserPlacement={(t) => relancer(profil, { ...demande, ticker: t })}
                initiale={initiale} echanges={echanges} onMessage={envoyerMessage} envoi={envoi}
                editions={editions} indexEdition={indexEdition} onVoirEdition={voirEdition} />
            )}
            {etape === 4 && dossier && (
              <Etape5Bascule dossier={dossier} onRetour={() => setEtape(3)} onRecommencer={recommencer} ouvrirFait={ouvrirFait} />
            )}
          </>
        )}
      </main>

      <footer className="pied">
        Simulation éducative. Aucune transaction réelle, aucun conseil financier personnalisé. Données publiques
        2021-11-12 → 2026-11-12 (prix Yahoo Finance, taux de change Banque du Canada). Montants des profils fictifs.
      </footer>

      {faitOuvert && (
        <TiroirFait faits={faitOuvert.map((id) => (dossier?.faits || direct.faits).find((f) => f.id === id))}
          onFermer={() => setFaitOuvert(null)} />
      )}
    </div>
    </RegistreContext.Provider>
  )
}
