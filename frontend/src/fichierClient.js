// Lecture d'un fichier JSON déposé par la personne : même format que la requête POST /api/analyse
// ({ profil, demande }, chaque partie facultative). On ne garde que les champs connus et bien typés ;
// tout le reste est signalé, jamais pris en silence. Le Gardien revérifie ensuite chaque valeur.

const TAILLE_MAX = 200_000

const nombre = (v) => typeof v === 'number' && Number.isFinite(v)
const booleen = (v) => typeof v === 'boolean'
const texte = (v) => typeof v === 'string'
const listeTextes = (v) => Array.isArray(v) && v.every(texte)
const portefeuille = (v) => listeTextes(v) ||
  (v !== null && typeof v === 'object' && !Array.isArray(v) && Object.values(v).every(nombre))
const reponses = (v) => v !== null && typeof v === 'object' && !Array.isArray(v) && Object.values(v).every(nombre)

export const CHAMPS_PROFIL = {
  nom: [texte, 'nom'], age: [nombre, 'âge'], experience: [texte, 'expérience'], profession: [texte, 'profession'],
  horizon_ans: [nombre, 'horizon'], tolerance: [nombre, 'tolérance au risque'],
  reponses_tolerance: [reponses, 'réponses au questionnaire'],
  epargne_totale_cad: [nombre, 'épargne totale'], somme_a_preserver_cad: [nombre, 'somme à préserver'],
  revenu_stable: [booleen, 'revenu stable'], fonds_urgence: [booleen, "fonds d'urgence"],
  dettes_importantes: [booleen, 'dettes importantes'], retrait_prevu_ans: [nombre, 'retrait prévu'],
  exclusions: [listeTextes, 'exclusions'], portefeuille_actuel: [portefeuille, 'portefeuille actuel'],
  citations: [listeTextes, 'citations'], envie: [texte, 'envie'], peur: [texte, 'peur'],
}

export const CHAMPS_DEMANDE = {
  texte: [texte, 'demande en mots'], ticker: [texte, 'placement visé'], montant_cad: [nombre, 'montant'],
}

function trier(source, champs, prefixe, lus, ignores) {
  const garde = {}
  for (const [cle, valeur] of Object.entries(source || {})) {
    if (cle.startsWith('_')) continue                       // notes du modèle (« _aide ») : jamais des données
    const regle = champs[cle]
    if (!regle) { ignores.push(`${prefixe}${cle} (champ inconnu)`); continue }
    // « null » ou vide = pas encore connu, comme dans le contrat : rien n'est repris.
    if (valeur === null || (typeof valeur === 'object' && Object.keys(valeur).length === 0)) continue
    if (!regle[0](valeur)) { ignores.push(`${prefixe}${cle} (format inattendu)`); continue }
    garde[cle] = cle === 'ticker' ? valeur.trim().toUpperCase() : valeur
    lus.push(regle[1])
  }
  return garde
}

export async function lireFichierClient(fichier) {
  if (fichier.size > TAILLE_MAX) throw new Error('Fichier trop lourd (200 Ko au plus).')
  let brut
  try {
    brut = JSON.parse(await fichier.text())
  } catch {
    throw new Error("Ce fichier n'est pas un JSON lisible.")
  }
  if (brut === null || typeof brut !== 'object' || Array.isArray(brut)) {
    throw new Error('Le fichier doit contenir un objet { "profil": {...}, "demande": {...} }.')
  }
  // Un fichier qui ne contient que les champs du profil, sans l'enveloppe « profil », est accepté aussi.
  const enveloppe = 'profil' in brut || 'demande' in brut
  const lus = []
  const ignores = []
  const profil = trier(enveloppe ? brut.profil : brut, CHAMPS_PROFIL, enveloppe ? 'profil.' : '', lus, ignores)
  const demande = enveloppe ? trier(brut.demande, CHAMPS_DEMANDE, 'demande.', lus, ignores) : {}
  if (enveloppe) {
    for (const cle of Object.keys(brut)) if (!['profil', 'demande'].includes(cle) && !cle.startsWith('_')) ignores.push(`${cle} (champ inconnu)`)
  }
  if (!lus.length) throw new Error("Aucune information remplie dans ce fichier : complète au moins un champ (le modèle à télécharger les liste).")
  return { nom: fichier.name, profil, demande, lus, ignores }
}

export const MODELE = {
  _aide: "Remplis ce que tu connais, laisse null le reste. Montants en dollars canadiens, durées en années. "
    + "Tolérance de 0 (aucun risque) à 100. Exclusions : secteurs à éviter (ex. Energy). Portefeuille : liste de "
    + "symboles ([\"XIU.TO\", \"XBB.TO\"]), ou poids en fractions de ton épargne dont la somme vaut 1 "
    + "({\"XIU.TO\": 0.6, \"XBB.TO\": 0.4}). Tu peux aussi écrire ta demande en mots à côté.",
  profil: {
    nom: null, age: null, experience: null, horizon_ans: null, tolerance: null,
    epargne_totale_cad: null, somme_a_preserver_cad: null, revenu_stable: null, fonds_urgence: null,
    dettes_importantes: null, retrait_prevu_ans: null, exclusions: [], portefeuille_actuel: null,
  },
  demande: { texte: null, ticker: null, montant_cad: null },
}

export function telechargerModele() {
  const url = URL.createObjectURL(new Blob([JSON.stringify(MODELE, null, 2) + '\n'], { type: 'application/json' }))
  const lien = Object.assign(document.createElement('a'), { href: url, download: 'alphaforge-modele.json' })
  lien.click()
  URL.revokeObjectURL(url)
}
