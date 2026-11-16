// Sections repliables : un clic (ou Entrée / Espace) sur le titre d'une section la réduit à ce titre.
// Sert à lire une page longue sans défiler. Rien n'est retiré du dossier : le contenu est seulement masqué.
// L'état est tenu par titre, pour survivre aux nouveaux rendus de la page.
const SELECTEUR = '.carte > h2, .bloc-options > h2, .ce-qui-change > h2'
// Repliées au départ : les deux sections les plus longues de la lecture approfondie.
const REPLIEES_AU_DEPART = new Set(['Sources de cette analyse', 'Qualité des données'])
const choix = new Map()      // titre → replié ou non, quand la personne a choisi
let toutEstReplie = false    // « Tout replier » vaut aussi pour les sections qui apparaîtront ensuite
const cle = (h) => h.textContent.trim()
const estReplie = (k) => (choix.has(k) ? choix.get(k) : toutEstReplie || REPLIEES_AU_DEPART.has(k))

function decorer(racine = document) {
  racine.querySelectorAll(SELECTEUR).forEach((h) => {
    if (!h.dataset.repliable) {
      h.dataset.repliable = '1'; h.tabIndex = 0; h.setAttribute('role', 'button')
      h.title = 'Replier ou déplier cette section'
    }
    const replie = estReplie(cle(h))
    h.parentElement.classList.toggle('replie', replie)
    h.setAttribute('aria-expanded', String(!replie))
  })
}

export function toutReplier(valeur) {
  toutEstReplie = valeur
  choix.clear()
  if (!valeur) REPLIEES_AU_DEPART.forEach((k) => choix.set(k, false))
  decorer()
}

export function installerRepliables(racine) {
  const basculer = (h) => { const k = cle(h); choix.set(k, !estReplie(k)); decorer(racine) }
  const auClic = (e) => { const h = e.target.closest?.('h2[data-repliable]'); if (h && racine.contains(h)) basculer(h) }
  const auClavier = (e) => {
    if (e.key !== 'Enter' && e.key !== ' ') return
    const h = e.target.matches?.('h2[data-repliable]') ? e.target : null
    if (h) { e.preventDefault(); basculer(h) }
  }
  racine.addEventListener('click', auClic)
  racine.addEventListener('keydown', auClavier)
  const veille = new MutationObserver(() => decorer(racine))
  veille.observe(racine, { childList: true, subtree: true })
  decorer(racine)
  return () => { veille.disconnect(); racine.removeEventListener('click', auClic); racine.removeEventListener('keydown', auClavier) }
}
