// Vérification du rendu React avec les dépendances existantes.
// Ce contrôle statique ne remplace pas une inspection visuelle dans un navigateur.
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { createServer } from 'vite'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'

const racine = fileURLToPath(new URL('./', import.meta.url))
const preuves = new URL('../docs/fusion/preuves/tranche4/', import.meta.url)
const lire = async (nom) => JSON.parse(await fs.readFile(new URL(nom, preuves), 'utf8'))
const serveur = await createServer({ root: racine, server: { middlewareMode: true } })
try {
  const charger = async (p) => (await serveur.ssrLoadModule('/src/' + p)).default
  const Verdict = await charger('etapes/Etape4Verdict.jsx')
  const Trace = await charger('etapes/Etape3Trace.jsx')
  const Bascule = await charger('etapes/Etape5Bascule.jsx')
  const afficher = (C, d) => renderToStaticMarkup(React.createElement(C, {
    dossier: d, ouvrirFait: () => {}, onRetour: () => {}, onRecommencer: () => {},
  }))
  const bilan = { nature: 'Rendu React statique, sans navigateur ni inspection visuelle', cas: [] }
  for (const nom of ['robert', 'amira', 'mateo', 'cas5-sans-retrait', 'cas6-impossible']) {
    const d = await lire(nom.startsWith('cas') ? nom + '.json' : nom + '-hors-ligne.json')
    const html = afficher(Verdict, d)
    if (d.comparaison?.disponible) {
      assert(html.includes(String(d.comparaison.apres.pire_chute_pct).replace('.', ',')))
      assert(html.includes('Comparaison du portefeuille entier'))
      assert(html.includes('Ouvrir la preuve'))
    }
    if (nom === 'cas5-sans-retrait') assert(html.includes('Question décisive') && html.includes('passerait'))
    if (nom === 'cas6-impossible') assert(html.includes('Le montant dépasse'))
    const trace = afficher(Trace, d)
    assert(trace.includes('Aucun modèle'))
    bilan.cas.push({ nom, rendu_verdict: true, appels_hors_ligne: true })
  }
  const d = await lire('amira-xiu14000.json')
  // La grille existante va jusqu'au montant demandé : celle de 35 000 inclut
  // les deux montants du contre-exemple, celle de 14 000 reste en dessous.
  assert(afficher(Bascule, await lire('amira-xiu35000.json')).includes('Une grille non monotone'))
  assert(afficher(Verdict, d).includes('Montant hausse'))
  const retrait = await lire('cas5-sans-retrait.json')
  const fiche = afficher(Bascule, retrait)
  assert(fiche.includes('Question décisive') && fiche.includes('Comparaison historique du portefeuille'))
  for (const nom of ['robert', 'amira', 'mateo']) {
    const reel = await lire(nom + '-bedrock.json')
    const html = afficher(Trace, reel)
    for (const a of reel.appels_modele) assert(html.includes(a.request_id) && html.includes(a.modele))
  }
  const ancien = await lire('robert-hors-ligne.json')
  delete ancien.comparaison
  delete ancien.appels_modele
  assert(!afficher(Verdict, ancien).includes('Comparaison du portefeuille entier'))
  assert(!afficher(Trace, ancien).includes('Les appels réellement effectués'))
  bilan.grille_non_monotone = true
  bilan.fiche_et_question = true
  bilan.identifiants_reels_dans_rendu = true
  bilan.champs_absents_compatibles = true
  await fs.writeFile(new URL('rendu-react.json', preuves), JSON.stringify(bilan, null, 2) + '\n')
  console.log(JSON.stringify(bilan, null, 2))
} finally {
  await serveur.close()
}
