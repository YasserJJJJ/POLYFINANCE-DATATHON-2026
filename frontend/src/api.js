const BASE = import.meta.env.VITE_API_URL || ''

async function requete(chemin, options = {}) {
  const rep = await fetch(`${BASE}${chemin}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!rep.ok) {
    const detail = await rep.text()
    throw new Error(`Le serveur a répondu ${rep.status} : ${detail}`)
  }
  return rep.json()
}

export const api = {
  sante: () => requete('/api/sante'),
  sources: () => requete('/api/sources'),
  personas: () => requete('/api/personas'),
  actifs: () => requete('/api/actifs'),
  questions: () => requete('/api/questions'),
  serie: (ticker) => requete(`/api/serie/${encodeURIComponent(ticker)}`),
  comprendre: (profil, demande) =>
    requete('/api/comprendre', { method: 'POST', body: JSON.stringify({ profil, demande }) }),
  analyser: (profil, demande) =>
    requete('/api/analyse', { method: 'POST', body: JSON.stringify({ profil, demande }) }),
  analyserEnDirect,
}

// Une ligne JSON par étape terminée, puis le dossier. Si tout arrive d'un bloc (Lambda), les étapes sont
// simplement reçues ensemble à la fin.
async function analyserEnDirect(profil, demande, surEtape) {
  const rep = await fetch(`${BASE}/api/analyse/flux`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ profil, demande }),
  })
  if (!rep.ok) throw new Error(`Le serveur a répondu ${rep.status} : ${await rep.text()}`)
  const lecteur = rep.body.getReader()
  const decodeur = new TextDecoder()
  let tampon = ''
  let dossier = null
  for (;;) {
    const { value, done } = await lecteur.read()
    if (done) break
    tampon += decodeur.decode(value, { stream: true })
    let fin
    while ((fin = tampon.indexOf('\n')) >= 0) {
      const ligne = tampon.slice(0, fin).trim()
      tampon = tampon.slice(fin + 1)
      if (!ligne) continue
      const m = JSON.parse(ligne)
      if (m.type === 'erreur') throw new Error(`Le serveur a répondu ${m.statut} : ${m.detail}`)
      if (m.type === 'dossier') dossier = m.dossier
      else surEtape(m)
    }
  }
  if (!dossier) throw new Error("L'analyse s'est interrompue avant la fin.")
  return dossier
}

export const dollars = (n) =>
  n == null ? '—' : `${Math.round(n).toLocaleString('fr-CA')} $`
