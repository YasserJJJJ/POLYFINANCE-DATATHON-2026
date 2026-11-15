import { useCallback, useEffect, useState } from 'react'
import { Info } from 'lucide-react'
import { api } from './api.js'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Marque, NOM_PRODUIT } from '@/components/Marque.jsx'
import { PROFIL_VIERGE } from '@/components/Profil.jsx'
import { RegistreContext } from '@/components/Sources.jsx'
import TiroirFait from '@/components/TiroirFait.jsx'
import Accueil from '@/ecrans/Accueil.jsx'
import Conversation from '@/ecrans/Conversation.jsx'
import Analyse from '@/ecrans/Analyse.jsx'
import Verdict from '@/ecrans/Verdict.jsx'
import Curseurs from '@/ecrans/Curseurs.jsx'
import Comparer from '@/ecrans/Comparer.jsx'
import { cn } from '@/lib/utils'

const ETAPES = ['Décris ton idée', 'Vérifie ce que j’ai compris', 'Analyse par les agents', 'Le verdict', 'Les curseurs de bascule']
const DEMANDE_VIERGE = { texte: '', ticker: null, montant_cad: null }

export default function App() {
  const [vue, setVue] = useState('accueil') // accueil | parcours | comparer
  const [etape, setEtape] = useState(0)
  const [conversation, setConversation] = useState(0)
  const [personas, setPersonas] = useState(null)
  const [actifs, setActifs] = useState([])
  const [questions, setQuestions] = useState([])
  const [sante, setSante] = useState(null)
  const [registre, setRegistre] = useState(null)
  const [profil, setProfil] = useState(PROFIL_VIERGE)
  const [demande, setDemande] = useState(DEMANDE_VIERGE)
  const [dossier, setDossier] = useState(null)
  const [lance, setLance] = useState(false)
  const [faitOuvert, setFaitOuvert] = useState(null)
  const [erreur, setErreur] = useState(null)

  useEffect(() => {
    Promise.all([api.personas(), api.actifs(), api.questions(), api.sante()])
      .then(([p, a, q, s]) => { setPersonas(p); setActifs(a); setQuestions(q); setSante(s) })
      .then(() => api.sources().then(setRegistre).catch(() => setRegistre(null)))
      .catch((e) => setErreur(`Impossible de joindre l'API. Lance-la avec « uvicorn api:app --port 8000 » dans backend/. (${e.message})`))
  }, [])

  const allerA = (n) => { setEtape(n); window.scrollTo(0, 0) }
  const phaseConversation = useCallback((n) => setEtape((e) => (e <= 1 ? n : e)), [])

  const lancer = async () => {
    setDossier(null)
    setLance(true)
    allerA(2)
    try {
      // texte_lu : la personne a relu et corrigé le résumé ; l'analyse ne re-remplit pas un champ qu'elle a vidé.
      setDossier(await api.analyser(profil, { ...demande, texte_lu: true }))
    } catch (e) {
      setLance(false)
      allerA(1)
      setErreur(`L'analyse n'a pas pu aboutir. Vérifie tes réponses, puis relance. (${e.message})`)
    }
  }

  const recommencer = () => {
    setEtape(0); setDossier(null); setLance(false); setProfil(PROFIL_VIERGE); setDemande(DEMANDE_VIERGE)
    setConversation((n) => n + 1)
    window.scrollTo(0, 0)
  }

  if (vue === 'accueil') {
    return <Accueil onCommencer={() => { recommencer(); setVue('parcours') }} onComparer={() => { setVue('comparer'); window.scrollTo(0, 0) }} />
  }

  const large = vue === 'comparer' || etape >= 2

  return (
    <RegistreContext.Provider value={registre}>
      <div className="flex min-h-screen flex-col bg-background">
        <header className="sticky top-0 z-30 border-b border-border bg-background/95 backdrop-blur">
          <div className="mx-auto flex max-w-[980px] flex-wrap items-center justify-between gap-x-3 gap-y-2 px-4 py-3">
            <button type="button" className="cursor-pointer" aria-label={`${NOM_PRODUIT}, retour à l'accueil`} onClick={() => { recommencer(); setVue('accueil') }}>
              <Marque />
            </button>
            <div className="flex flex-wrap items-center gap-1.5">
              {sante && (
                <Badge title={sante.llm ? `${sante.modeles.principal} et ${sante.modeles.leger}` : sante.raison || ''}>
                  <i aria-hidden="true" className={cn('size-1.5 rounded-full', sante.llm ? 'bg-ok' : 'bg-grey')} />
                  {sante.llm ? 'Agents IA : Bedrock' : 'Agents : mode hors ligne'}
                </Badge>
              )}
              <Button variant="ghost" size="sm" onClick={() => { setVue(vue === 'comparer' ? 'parcours' : 'comparer'); window.scrollTo(0, 0) }}>
                {vue === 'comparer' ? 'Retour au parcours' : 'Comparer les 3 profils'}
              </Button>
              {vue === 'parcours' && (etape > 0 || dossier) && <Button variant="ghost" size="sm" onClick={recommencer}>Recommencer</Button>}
            </div>
          </div>
        </header>

        <main className={cn('mx-auto w-full flex-1 px-4 pb-12 pt-6', large ? 'max-w-[980px]' : 'max-w-[640px]')}>
          {erreur && (
            <div role="alert" className="mb-5 flex items-start justify-between gap-3 rounded-lg border border-bad-bd bg-bad-bg px-4 py-3 text-[13.5px] text-bad">
              <span>{erreur}</span>
              <Button variant="ghost" size="sm" onClick={() => setErreur(null)}>Fermer</Button>
            </div>
          )}

          {vue === 'comparer' && personas && <Comparer personas={personas} />}

          {vue === 'parcours' && (
            <>
              <p className="mb-4 text-[13px] font-medium text-muted-foreground">Étape {etape + 1} sur 5 · {ETAPES[etape]}</p>
              {/* Les étapes 1 et 2 forment une seule conversation, gardée en mémoire pendant l'analyse :
                  « Modifier mes réponses » ramène au résumé sans rien perdre. */}
              <div hidden={etape > 1}>
                <Conversation key={conversation} personas={personas} actifs={actifs} questions={questions}
                  profil={profil} setProfil={(f) => { setLance(false); setProfil(f) }} demande={demande}
                  setDemande={(f) => { setLance(false); setDemande(f) }} onPhase={phaseConversation} onLancer={lancer} lance={lance} />
              </div>
              {etape === 2 && <Analyse dossier={dossier} onFini={() => allerA(3)} ouvrirFait={setFaitOuvert} />}
              {etape === 3 && dossier && <Verdict dossier={dossier} ouvrirFait={setFaitOuvert} onBascule={() => allerA(4)} onModifier={() => { setLance(false); allerA(1) }} />}
              {etape === 4 && dossier && <Curseurs dossier={dossier} onRetour={() => allerA(3)} onRecommencer={recommencer} />}
            </>
          )}
        </main>

        <footer className="border-t border-border px-4 py-5">
          <p className="mx-auto flex max-w-[980px] items-start gap-2 text-xs text-muted-foreground">
            <Info className="mt-px size-4 flex-none" />
            <span>Simulation éducative. Aucune transaction réelle, aucun conseil financier personnalisé. Données publiques 2021-11-12 → 2026-11-12
              (prix Yahoo Finance, taux de change Banque du Canada). Montants des profils fictifs. Le passé ne prédit pas l'avenir.</span>
          </p>
        </footer>

        {faitOuvert && dossier && <TiroirFait fait={dossier.faits.find((f) => f.id === faitOuvert)} onFermer={() => setFaitOuvert(null)} />}
      </div>
    </RegistreContext.Provider>
  )
}
