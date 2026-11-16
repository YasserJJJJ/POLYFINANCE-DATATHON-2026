import { useEffect, useState } from 'react'
import { dollars } from '../api.js'
import BarreDemande from '../composants/BarreDemande.jsx'
import { Etiquette, PuceIssue, PuceNiveau, PuceVerdict, PucesFaits } from '../composants/Base.jsx'
import GraphiqueChute from '../composants/GraphiqueChute.jsx'
import ComparaisonPortefeuille from '../composants/ComparaisonPortefeuille.jsx'
import { ListeSources, SourcesCompactes, SourcesParType, sourcesDuDossier } from '../composants/Sources.jsx'

function Phrase({ p, ouvrir }) {
  return (
    <li className="phrase">
      <Etiquette type={p.type} />
      <span>{p.texte}</span>
      <PucesFaits ids={p.faits} ouvrir={ouvrir} />
      {p.references?.length > 0 && <SourcesCompactes ids={p.references} prefixe="Source :" />}
    </li>
  )
}

function Option({ o, principal, ouvrir }) {
  return (
    <div className={`carte option ${principal ? 'principale' : ''}`}>
      <p className="option-nom">{o.nom}</p>
      {o.ticker && <p className="muted petit">{o.libelle_actif ? `${o.libelle_actif} (${o.ticker})` : o.ticker}</p>}
      <PuceVerdict etat={o.etat} />
      <dl className="option-chiffres">
        <div><dt>Montant</dt><dd>{dollars(o.montant_cad)}</dd></div>
        <div><dt>Horizon</dt><dd>{o.horizon_ans} an(s)</dd></div>
      </dl>
      {o.constat && <p className="option-note">{o.constat} {o.sens && <span className="muted petit">(Montant {o.sens})</span>}</p>}
      {(o.note || o.faits?.length > 0) && (
        <p className="muted petit option-note">{o.note} <PucesFaits ids={o.faits} ouvrir={ouvrir} /></p>
      )}
    </div>
  )
}

const PERSONAS_NOMS = ['Amira', 'Mateo', 'Robert']

// Plan ouvert : les placements de la liste qui passent les règles, en tableau, chacun analysable seul.
function PlacementsDuPlan({ plan, verdict, ouvrir, onAnalyser }) {
  return (
    <div className="carte">
      <h2>{plan.placements.length ? 'Placements de la liste qui passent les règles pour toi' : 'Aucun placement de la liste ne passe les règles'}</h2>
      {plan.placements.length > 0 && (
        <div className="defile-x">
          <table className="registre comparatif">
            <thead><tr><th>Placement</th><th>Famille</th><th>Pire chute observée</th><th>Verdict</th><th /></tr></thead>
            <tbody>
              {plan.placements.map((pl) => (
                <tr key={pl.ticker}>
                  <td><strong>{pl.ticker}</strong><br /><span className="muted petit">{pl.nom}</span></td>
                  <td>{pl.famille}</td>
                  <td className="nombre">{String(pl.pire_chute_pct).replace('.', ',')} % <PucesFaits ids={pl.faits} ouvrir={ouvrir} /></td>
                  <td><PuceVerdict etat={pl.etat} />{pl.a_ajuster.length > 0 && <p className="muted petit">À ajuster : {pl.a_ajuster.join(', ')}</p>}</td>
                  <td><button type="button" className="bouton discret" onClick={() => onAnalyser(pl.ticker)}>Analyse complète</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="muted petit">{plan.critere} Ce que les règles acceptent pour toi, pas une recommandation.
        {verdict.etat === 'incoherent' && plan.bloquante && <> La règle qui bloque le plus souvent : « {plan.bloquante} ».</>}</p>
      {plan.ecartes?.length > 0 && (
        <details className="pourquoi-regle">
          <summary>Pourquoi les autres placements ne sont pas retenus</summary>
          <ul>{plan.ecartes.map((e) => <li key={e.raison}>{e.raison} : {e.nombre} placement(s)</li>)}</ul>
        </details>
      )}
    </div>
  )
}

export default function Etape4Verdict({ dossier, ouvrirFait, onBascule, onModifier, saisie, actifs, onRelancer, relance, onAnalyserPlacement }) {
  const { verdict, texte, regles, options, faits, objections, qualite_donnees: qualite, demande, profil } = dossier
  const [onglet, setOnglet] = useState('essentiel')
  useEffect(() => setOnglet('essentiel'), [dossier])   // un nouveau résultat se lit d'abord par l'essentiel
  const plan = dossier.plan?.ouvert ? dossier.plan : null
  const nbPlacements = plan ? plan.placements.length : options.length
  const onglets = [['essentiel', "L'essentiel"], ['placements', `${plan ? 'Les placements' : 'Les options'} (${nbPlacements})`],
    ['detail', 'Le détail']]
  const estPersona = PERSONAS_NOMS.includes(profil?.nom)
  const ids = demande.ids_faits || {}
  const ordre = { rouge: 0, orange: 1, gris: 2, ok: 3, non_evaluee: 4 }
  const reglesTriees = [...regles].sort((a, b) => ordre[a.niveau] - ordre[b.niveau])

  return (
    <section className={`etape4 ${relance ? 'en-relance' : ''}`} aria-busy={relance}>
      <BarreDemande profil={{ ...saisie.profil, evaluation: profil.evaluation }} demande={saisie.demande} actifs={actifs}
        onRelancer={onRelancer} onToutRevoir={onModifier} relance={relance} />

      <div className="onglets" role="tablist" aria-label="Niveau de détail">
        {onglets.map(([cle, nom]) => (
          <button key={cle} type="button" role="tab" aria-selected={onglet === cle}
            className={`onglet ${onglet === cle ? 'actif' : ''}`} onClick={() => setOnglet(cle)}>{nom}</button>
        ))}
      </div>

      {onglet === 'essentiel' && (<>
      <div className={`verdict-tete carte etat-${verdict.etat}`}>
        <p className="surtitre">Le second avis</p>
        <PuceVerdict etat={verdict.etat} grand libelle={verdict.libelle} />
        {plan
          ? <p className="compte-regles"><strong>{verdict.respectees}</strong> placement(s) sur <strong>{verdict.evaluees}</strong> passent toutes les règles</p>
          : <p className="compte-regles"><strong>{verdict.respectees}</strong> règle(s) respectée(s) sur <strong>{verdict.evaluees}</strong></p>}
        {texte?.reformulation && <p className="reformulation">{texte.reformulation}</p>}
        {texte?.tensions?.map((t) => <p key={t} className="tension">{t}</p>)}
      </div>

      {dossier.questions?.length > 0 && (
        <div className="carte manque">
          <h2>{verdict.etat === 'indetermine' ? "Ce qu'il me faut pour conclure" : 'La question qui pourrait changer cet avis'}</h2>
          <ul>{dossier.questions.map((q) => <li key={q}><strong>{q}</strong>
            <PucesFaits ids={q.match(/F-\d+/g) || []} ouvrir={ouvrirFait} /></li>)}</ul>
        </div>
      )}

      {texte?.miroir?.length > 0 && (
        <div className="carte miroir">
          <h2>Le miroir</h2>
          <ul className="phrases">{texte.miroir.map((p, i) => <Phrase key={i} p={p} ouvrir={ouvrirFait} />)}</ul>
          {estPersona && (
            <p className="muted petit">« Tu as dit » cite une phrase type du profil {profil.nom} (scénario fictif
              de l'équipe), pas une saisie que tu as faite.</p>
          )}
        </div>
      )}

      {texte?.pourquoi?.length > 0 && (
        <div className="carte">
          <h2>Pourquoi ce verdict</h2>
          <ul className="phrases">{texte.pourquoi.map((p, i) => <Phrase key={i} p={p} ouvrir={ouvrirFait} />)}</ul>
        </div>
      )}

      {texte?.ce_qui_changerait?.length > 0 && (
        <ul className="phrases">{texte.ce_qui_changerait.map((p, i) => <Phrase key={i} p={p} ouvrir={ouvrirFait} />)}</ul>
      )}
      <div className="actions">
        <button type="button" className="bouton principal" onClick={() => setOnglet('placements')}>
          {plan ? `Voir les placements (${nbPlacements})` : 'Comparer les options'}
        </button>
        {dossier.bascule?.cases?.length > 0 && <button type="button" className="bouton discret" onClick={onBascule}>Bouger les curseurs</button>}
        <button type="button" className="bouton discret" onClick={() => setOnglet('detail')}>Voir le détail</button>
      </div>
      </>)}

      {onglet === 'placements' && (plan
        ? <PlacementsDuPlan plan={plan} verdict={verdict} ouvrir={ouvrirFait} onAnalyser={onAnalyserPlacement} />
        : (<>
          <div className="trois-options">
            {options.map((o, i) => <Option key={o.nom} o={o} principal={i === 1} ouvrir={ouvrirFait} />)}
          </div>
          {dossier.bascule?.cases?.length > 0 && (
            <div className="actions"><button type="button" className="bouton principal" onClick={onBascule}>Bouger les curseurs</button></div>
          )}
        </>))}

      {onglet === 'detail' && (<>
      {plan && <p className="muted petit">Plan ouvert : les règles ci-dessous sont celles appliquées à {plan.regles_de || 'la liste'}, le premier placement retenu.</p>}
      <div className="colonnes">
        <div className="carte">
          <h2>Les règles appliquées</h2>
          <ul className="regles">
            {reglesTriees.map((r) => (
              <li key={r.code} className={`regle n-${r.niveau}`}>
                <div className="regle-tete"><strong>{r.libelle}</strong><PuceNiveau niveau={r.niveau} /></div>
                <p>{r.type && <Etiquette type={r.type} />} {r.explication}</p>
                {r.code === 'capacite' && <ComparaisonPortefeuille dossier={dossier} ouvrirFait={ouvrirFait} />}
                <PucesFaits ids={r.faits} ouvrir={ouvrirFait} />
                {r.references?.length > 0 && (
                  <details className="pourquoi-regle">
                    <summary>Sur quoi repose cette règle ?</summary>
                    <ListeSources ids={r.references} />
                  </details>
                )}
              </li>
            ))}
          </ul>
          <p className="muted petit">Ces règles sont du code, pas l'avis d'une IA. Le verdict ne peut pas les contredire.
            Les seuils (étiquette Hypothèse) sont des choix de l'équipe, au registre des chiffres ci-dessous.</p>
        </div>

        {!plan && <div className="pile">
          <div className="carte">
            <h2>La pire chute observée du titre seul</h2>
            <p className="muted petit">Cette courbe utilise le calendrier propre du titre. La comparaison du portefeuille utilise ses séances communes.</p>
            <GraphiqueChute ticker={demande.ticker} faitId={ids.chute} ouvrir={ouvrirFait} />
          </div>
          <div className="carte">
            <h2>Ce que le Sceptique a contesté</h2>
            {objections.map((o) => (
              <div key={o.id} className="objection">
                <p><span className="mono">{o.id}</span> {o.texte}</p>
                <p className="recalcul">↳ {o.reponse}</p>
                <PuceIssue issue={o.issue} />
              </div>
            ))}
          </div>
        </div>}
      </div>

      <div className="carte">
        <h2>Tous les chiffres utilisés</h2>
        <div className="defile-x">
          <table className="registre">
            <thead><tr><th>Id</th><th>Ce que c'est</th><th>Valeur</th><th>Type</th></tr></thead>
            <tbody>
              {faits.map((f) => (
                <tr key={f.id}>
                  <td><button type="button" className="puce-fait" onClick={() => ouvrirFait(f.id)}>{f.id}</button></td>
                  <td>{f.libelle}</td>
                  <td className="nombre">{typeof f.valeur === 'object' && f.valeur !== null ? Object.entries(f.valeur).map(([k, v]) => `${k} ${v}`).join(', ') : `${f.valeur ?? '—'} ${f.unite}`}</td>
                  <td><Etiquette type={f.type} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="colonnes">
        <div className="carte">
          <h2>Qualité des données</h2>
          <ul className="qualite">
            {qualite.map((c) => (
              <li key={c.code} className={`q-${c.statut}`}><span className="q-statut">{c.statut === 'ok' ? '✓' : '!'}</span>{c.libelle} <span className="muted">— {c.detail}</span></li>
            ))}
          </ul>
        </div>
        <div className="carte">
          <h2>Limites</h2>
          <ul className="phrases">{texte?.limites?.map((p, i) => <Phrase key={i} p={p} ouvrir={ouvrirFait} />)}</ul>
          <div className="controle">
            <p><strong>Comment ce texte a été vérifié.</strong> Rédigé par : {texte?.source}.</p>
            <p className="muted petit">
              Avant d'être affiché, le code vérifie que chaque nombre existe déjà dans le dossier, que chaque F-n cité
              existe, et qu'aucune phrase ne conseille d'acheter ou de vendre. Un défaut est nommé et renvoyé à l'agent.
            </p>
            {texte?.controle?.length > 0 && (
              <ul className="journal">{texte.controle.map((c) => <li key={c}>{c}</li>)}</ul>
            )}
          </div>
          <p className="avertissement">{texte?.avertissement}</p>
        </div>
      </div>
      <div className="carte sources-analyse">
        <h2>Sources de cette analyse</h2>
        <p className="muted petit">Chaque chiffre vient d'un fichier du jeu de départ et d'une méthode appliquée par le code.
          Chaque règle et chaque agent s'appuient sur les références ci-dessous. Le niveau d'examen indique ce que
          l'équipe a réellement lu : une référence non relue n'est jamais présentée comme vérifiée.</p>
        <SourcesParType ids={sourcesDuDossier(dossier)} />
      </div>
      </>)}
    </section>
  )
}
