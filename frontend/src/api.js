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
  personas: () => requete('/api/personas'),
  actifs: () => requete('/api/actifs'),
  questions: () => requete('/api/questions'),
  serie: (ticker) => requete(`/api/serie/${encodeURIComponent(ticker)}`),
  comprendre: (profil, demande) =>
    requete('/api/comprendre', { method: 'POST', body: JSON.stringify({ profil, demande }) }),
  analyser: (profil, demande) =>
    requete('/api/analyse', { method: 'POST', body: JSON.stringify({ profil, demande }) }),
}

export const dollars = (n) =>
  n == null ? '—' : `${Math.round(n).toLocaleString('fr-CA')} $`
