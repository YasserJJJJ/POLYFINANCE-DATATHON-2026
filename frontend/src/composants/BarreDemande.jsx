import { useEffect, useRef, useState } from 'react'
import { dollars } from '../api.js'
import { SECTEURS_FR } from '../etapes/Etape2Verifier.jsx'
import { pourClient } from '../affichage.js'

// La demande reste visible après le résultat : une rangée de puces, chacune modifiable sur place.
// « Appliquer et relancer » refait l'analyse avec la nouvelle valeur, sans quitter le verdict.
const nombre = (v) => (v === '' || v == null ? null : Number(v))

function Editeur({ champ, profil, demande, actifs, onAppliquer, onFermer }) {
  const [valeur, setValeur] = useState(champ.lire(profil, demande))
  const premier = useRef(null)
  useEffect(() => { premier.current?.focus() }, [])
  const appliquer = (e) => { e.preventDefault(); onAppliquer(champ.ecrire(profil, demande, valeur)) }
  const secteurs = [...new Set(actifs.map((a) => a.sector))].filter((s) => SECTEURS_FR[s])

  return (
    <form className="editeur-puce" role="dialog" aria-label={champ.titre} onSubmit={appliquer}
      onKeyDown={(e) => e.key === 'Escape' && onFermer()}>
      <p className="titre-champ">{champ.titre}</p>
      {champ.type === 'placement' && (
        <select ref={premier} value={valeur || ''} onChange={(e) => setValeur(e.target.value || null)}>
          <option value="">Au choix : le Gardien teste toute la liste</option>
          {actifs.map((a) => <option key={a.ticker} value={a.ticker}>{a.name} ({a.ticker})</option>)}
        </select>
      )}
      {champ.type === 'nombre' && (
        <input ref={premier} type="number" min={champ.min ?? 0} max={champ.max} step={champ.pas ?? 1}
          value={valeur ?? ''} placeholder={champ.indice || ''} onChange={(e) => setValeur(nombre(e.target.value))} />
      )}
      {champ.type === 'curseur' && (
        <>
          <input ref={premier} type="range" min={champ.min} max={champ.max} value={valeur ?? champ.min}
            onChange={(e) => setValeur(Number(e.target.value))} aria-valuetext={`${valeur} ${champ.unite}`} />
          <p className="muted petit">{valeur ?? '—'} {champ.unite}</p>
        </>
      )}
      {champ.type === 'secteurs' && (
        <div className="secteurs-editeur">
          {secteurs.map((s, i) => (
            <label key={s}><input ref={i === 0 ? premier : undefined} type="checkbox" checked={valeur.includes(s)}
              onChange={() => setValeur(valeur.includes(s) ? valeur.filter((x) => x !== s) : [...valeur, s])} /> {SECTEURS_FR[s]}</label>
          ))}
        </div>
      )}
      {champ.aide && <p className="muted petit">{champ.aide}</p>}
      <div className="actions">
        <button type="submit" className="bouton principal">Appliquer et relancer</button>
        <button type="button" className="bouton discret" onClick={onFermer}>Annuler</button>
      </div>
    </form>
  )
}

const CHAMPS = [
  { cle: 'montant', titre: 'Montant à placer ($ CA)', type: 'nombre', pas: 500, min: 1,
    lire: (p, d) => d.montant_cad, ecrire: (p, d, v) => ({ profil: p, demande: { ...d, montant_cad: v } }),
    puce: (p, d) => dollars(d.montant_cad) },
  { cle: 'horizon', titre: "Dans combien d'années auras-tu besoin de cet argent ?", type: 'curseur', min: 1, max: 30, unite: 'an(s)',
    lire: (p) => p.horizon_ans, ecrire: (p, d, v) => ({ profil: { ...p, horizon_ans: v }, demande: d }),
    puce: (p) => (p.horizon_ans == null ? 'horizon : ?' : `${p.horizon_ans} an(s)`) },
  { cle: 'placement', titre: 'Placement envisagé (facultatif)', type: 'placement',
    aide: 'Sans placement, le Gardien juge ton plan sur chaque placement de la liste et montre ceux qui passent ses règles.',
    lire: (p, d) => d.ticker, ecrire: (p, d, v) => ({ profil: p, demande: { ...d, ticker: v } }),
    puce: (p, d) => (d.ticker ? `placement : ${d.ticker}` : 'placement : au choix'), vide: (p, d) => !d.ticker },
  { cle: 'epargne', titre: 'Épargne totale ($ CA)', type: 'nombre', pas: 1000, min: 1,
    lire: (p) => p.epargne_totale_cad, ecrire: (p, d, v) => ({ profil: { ...p, epargne_totale_cad: v }, demande: d }),
    puce: (p) => `épargne ${dollars(p.epargne_totale_cad)}` },
  { cle: 'preserver', titre: 'Somme à ne jamais risquer ($ CA)', type: 'nombre', pas: 1000, indice: 'aucune',
    lire: (p) => p.somme_a_preserver_cad, ecrire: (p, d, v) => ({ profil: { ...p, somme_a_preserver_cad: v }, demande: d }),
    puce: (p) => (p.somme_a_preserver_cad == null ? 'à préserver : —' : `à préserver ${dollars(p.somme_a_preserver_cad)}`) },
  { cle: 'retrait', titre: "Retrait prévu dans combien d'années ? (vide : aucun)", type: 'nombre', min: 0, max: 50, indice: 'aucun',
    lire: (p) => p.retrait_prevu_ans, ecrire: (p, d, v) => ({ profil: { ...p, retrait_prevu_ans: v }, demande: d }),
    puce: (p) => (p.retrait_prevu_ans == null ? 'retrait : aucun' : `retrait dans ${p.retrait_prevu_ans} an(s)`) },
  { cle: 'exclusions', titre: 'Secteurs à exclure', type: 'secteurs',
    lire: (p) => p.exclusions || [], ecrire: (p, d, v) => ({ profil: { ...p, exclusions: v }, demande: d }),
    puce: (p) => (p.exclusions?.length ? `sans ${p.exclusions.map((s) => (SECTEURS_FR[s] || s).toLowerCase()).join(', ')}` : 'aucune exclusion') },
  { cle: 'risque', titre: 'Ce que tu veux risquer (0 = rien, 100 = beaucoup)', type: 'curseur', min: 0, max: 100, unite: '/ 100',
    aide: 'Remplace tes réponses au questionnaire par ce score.',
    lire: (p) => p.evaluation?.tolerance ?? p.tolerance,
    // Le score saisi ici remplace les réponses au questionnaire, sinon elles resteraient prioritaires.
    ecrire: (p, d, v) => ({ profil: { ...p, tolerance: v, reponses_tolerance: {} }, demande: d }),
    puce: (p) => `risque ${Math.round(p.evaluation?.tolerance ?? p.tolerance ?? 0)} / 100` },
]

// La conversation garde la demande de départ ; un nouveau message change la demande (et relance l'analyse)
// ou pose une question, à laquelle le Rédacteur répond sur le dossier, sous les mêmes garde-fous.
function Conversation({ initiale, echanges, onMessage, occupe, onVoirAnalyses }) {
  const [message, setMessage] = useState('')
  const fil = useRef(null)
  useEffect(() => { fil.current?.scrollTo({ top: fil.current.scrollHeight }) }, [echanges.length])
  const envoyer = (e) => {
    e.preventDefault()
    if (!message.trim() || occupe) return
    onMessage(message.trim())
    setMessage('')
  }
  return (
    <div className="conversation">
      <div className="fil" ref={fil} aria-live="polite">
        <p className="bulle toi"><span className="qui">Ta demande de départ</span>{initiale || 'Saisie dans le formulaire, sans phrase.'}</p>
        {echanges.map((m, i) => (
          <p key={i} className={`bulle ${m.auteur}`}>
            <span className="qui">{m.auteur === 'toi' ? 'Toi' : 'AlphaForge'}</span>
            {pourClient(m.texte)}
            {m.faits?.length > 0 && <>{' '}<button type="button" className="lien" onClick={() => onVoirAnalyses(m.faits)}>d'après les analyses</button></>}
            {m.source && <span className="muted petit"> · {m.source}</span>}
          </p>
        ))}
        {occupe && <p className="bulle outil muted">AlphaForge lit ton message…</p>}
      </div>
      <form className="saisie-message" onSubmit={envoyer}>
        <label htmlFor="message-suite" className="visuellement-cache">Change, ajoute ou demande une précision</label>
        <input id="message-suite" type="text" value={message} onChange={(e) => setMessage(e.target.value)} disabled={occupe}
          placeholder="Ex. : Et si j'avais 20 ans devant moi ? · Pourquoi le seuil est de 17 % ?" maxLength={500} />
        <button type="submit" className="bouton principal" disabled={!message.trim() || occupe}>Envoyer</button>
      </form>
    </div>
  )
}

export default function BarreDemande({ profil, demande, actifs, onRelancer, onToutRevoir, relance,
  initiale, echanges = [], onMessage, envoi, onVoirAnalyses }) {
  const [ouvert, setOuvert] = useState(null)
  const champ = CHAMPS.find((c) => c.cle === ouvert)
  return (
    <div className="barre-demande carte">
      {onMessage && <Conversation initiale={initiale} echanges={echanges} onMessage={onMessage}
        occupe={envoi || relance} onVoirAnalyses={onVoirAnalyses} />}
      <div className="puces-demande" role="group" aria-label="Ta demande, modifiable">
        <span className="muted petit">Ta demande :</span>
        {CHAMPS.map((c) => (
          <button key={c.cle} type="button" disabled={relance}
            className={`puce-demande ${c.vide?.(profil, demande) ? 'vide' : ''} ${ouvert === c.cle ? 'ouverte' : ''}`}
            aria-expanded={ouvert === c.cle} onClick={() => setOuvert(ouvert === c.cle ? null : c.cle)}>
            {c.puce(profil, demande)} <span aria-hidden="true">✎</span>
          </button>
        ))}
        <button type="button" className="lien petit" onClick={onToutRevoir} disabled={relance}>Tout revoir</button>
      </div>
      {champ && (
        <Editeur key={champ.cle} champ={champ} profil={profil} demande={demande} actifs={actifs}
          onFermer={() => setOuvert(null)}
          onAppliquer={({ profil: p, demande: d }) => { setOuvert(null); onRelancer(p, d) }} />
      )}
      {relance && <p className="relance" aria-live="polite">Analyse en cours avec ta modification… l'ancien résultat reste affiché en attendant.</p>}
    </div>
  )
}
