import { useEffect, useState } from 'react'
import { dollars } from '../api.js'
import { pourClient } from '../affichage.js'
import BarreDemande from '../composants/BarreDemande.jsx'
import CarteRaisonnement from '../composants/CarteRaisonnement.jsx'
import { Etiquette, PuceIssue, PuceNiveau, PuceVerdict, PucesFaits } from '../composants/Base.jsx'
import GraphiqueChute from '../composants/GraphiqueChute.jsx'
import ComparaisonPortefeuille from '../composants/ComparaisonPortefeuille.jsx'
import { ListeSources, SourcesCompactes, SourcesParType, sourcesDuDossier } from '../composants/Sources.jsx'

function Phrase({ p, ouvrir }) {
  return (
    <li className="phrase">
      <Etiquette type={p.type} />
      <span>{pourClient(p.texte)}</span>
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
      {o.constat && <p className="option-note">{pourClient(o.constat)} {o.sens && <span className="muted petit">(Montant {o.sens})</span>}</p>}
      {(o.note || o.faits?.length > 0) && (
        <p className="muted petit option-note">{pourClient(o.note)} <PucesFaits ids={o.faits} ouvrir={ouvrir} /></p>
      )}
    </div>
  )
}

const PERSONAS_NOMS = ['Amira', 'Mateo', 'Robert']

function titreDesOptions(etat, plan) {
  if (plan) {
    return { coherent: 'Ce qui serait cohérent dans ta situation',
      ajustement: 'Ce qui serait cohérent dans ta situation, avec un ajustement',
      incoherent: 'Ce qui bloque ton plan, et ce qui le débloquerait' }[etat]
  }
  return { incoherent: 'Ce qui rendrait ton plan cohérent avec ta situation',
    ajustement: 'Ce qui rendrait ton plan pleinement cohérent',
    coherent: "D'autres façons de faire, pour comparer" }[etat]
}

const minuscule = (t = '') => t.charAt(0).toLowerCase() + t.slice(1)

// Plan ouvert : les placements de la liste qui passent les règles, en tableau, chacun analysable seul.
function PlacementsDuPlan({ plan, verdict, ouvrir, onAnalyser, suggestion = false }) {
  const [choisi, setChoisi] = useState(plan.placements[0]?.ticker || null)
  useEffect(() => setChoisi(plan.placements[0]?.ticker || null), [plan])
  const selection = plan.placements.find((pl) => pl.ticker === choisi)
  const familles = [...new Set(plan.placements.map((pl) => pl.famille))]
  return (
    <div className="carte">
      <p className="explication-plan"><Etiquette type="SCENARIO" />{' '}
        {suggestion ? 'Ce placement ne correspond pas à ta situation' : "Tu n'as pas choisi de placement"} :
        voici {plan.placements.length > 1 ? `${plan.placements.length} placements` : 'le placement'} de
        la liste qui {plan.placements.length > 1 ? 'passent' : 'passe'} toutes tes règles{familles.length > 1
          ? `, de familles différentes (${familles.map(minuscule).join(', ')})`
          : plan.placements.length > 1 ? `, tous de la même famille (${minuscule(familles[0])}) : aucune autre famille ne passe tes règles` : ''}
        {' '}et hors de tes exclusions. {plan.placements.length > 1 ? 'Ils sont choisis' : 'Il est choisi'} par la pire chute
        observée la plus faible, jamais par le rendement passé. C'est une simulation de ce que les règles acceptent pour toi,
        pas une recommandation.</p>
      {plan.placements.length > 0 && (
        <div className="defile-x">
          <table className="registre comparatif">
            <thead><tr><th>Placement</th><th>Famille</th><th>Pire chute observée</th><th>Verdict</th><th /></tr></thead>
            <tbody>
              {plan.placements.map((pl) => (
                <tr key={pl.ticker} className={pl.ticker === choisi ? 'choisi' : ''}>
                  <td><strong>{pl.ticker}</strong><br /><span className="muted petit">{pl.nom}</span></td>
                  <td>{pl.famille}</td>
                  <td className="nombre">{String(pl.pire_chute_pct).replace('.', ',')} % <PucesFaits ids={pl.faits} ouvrir={ouvrir} /></td>
                  <td><PuceVerdict etat={pl.etat} />{pl.a_ajuster.length > 0 && <p className="muted petit">À ajuster : {pl.a_ajuster.join(', ')}</p>}</td>
                  <td className="actions-ligne">
                    <button type="button" className="bouton discret" aria-pressed={pl.ticker === choisi} onClick={() => setChoisi(pl.ticker)}>
                      {pl.ticker === choisi ? 'Graphique affiché' : 'Voir le graphique'}</button>
                    <button type="button" className="bouton discret" onClick={() => onAnalyser(pl.ticker)}>Analyse complète</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {selection && (
        <div className="graphique-plan">
          <h3>La pire chute observée de {selection.ticker} ({selection.nom})</h3>
          <GraphiqueChute ticker={selection.ticker} faitId={selection.faits[0]} ouvrir={ouvrir} />
        </div>
      )}
      {!suggestion && verdict.etat === 'incoherent' && plan.bloquante && (
        <p className="muted petit">La règle qui bloque le plus souvent : « {plan.bloquante} ». Change ce point de ta demande pour voir le plan basculer.</p>
      )}
      {plan.ecartes?.length > 0 && (
        <details className="pourquoi-regle">
          <summary>Pourquoi les autres placements ne sont pas retenus</summary>
          <ul>{plan.ecartes.map((e) => <li key={e.raison}>{e.raison} : {e.nombre} placement(s)</li>)}</ul>
        </details>
      )}
    </div>
  )
}

export default function Etape4Verdict({ dossier, ouvrirFait, onBascule, onModifier, saisie, actifs, onRelancer, relance,
  onAnalyserPlacement, initiale, echanges, onMessage, envoi }) {
  const { verdict, texte, regles, options, faits, objections, qualite_donnees: qualite, demande, profil } = dossier
  const [onglet, setOnglet] = useState('essentiel')
  const [surligne, setSurligne] = useState([])   // chiffres d'une phrase, montrés dans « Le détail »
  useEffect(() => { setOnglet('essentiel'); setSurligne([]) }, [dossier])   // un nouveau résultat se lit d'abord par l'essentiel
  useEffect(() => {
    if (onglet !== 'detail' || !surligne.length) return
    document.querySelector(`[data-fait="${surligne[0]}"]`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, [onglet, surligne])
  const voirAnalyses = (idsFaits) => { setSurligne(idsFaits); setOnglet('detail') }
  const plan = dossier.plan?.ouvert ? dossier.plan : null
  const titreOptions = titreDesOptions(verdict.etat, plan)
  const onglets = [['essentiel', "L'essentiel"], ['detail', 'Le détail et les sources']]
  const estPersona = PERSONAS_NOMS.includes(profil?.nom)
  const ids = demande.ids_faits || {}
  const ordre = { rouge: 0, orange: 1, gris: 2, ok: 3, non_evaluee: 4 }
  const reglesTriees = [...regles].sort((a, b) => ordre[a.niveau] - ordre[b.niveau])

  return (
    <section className={`etape4 ${relance ? 'en-relance' : ''}`} aria-busy={relance}>
      <BarreDemande profil={{ ...saisie.profil, evaluation: profil.evaluation }} demande={saisie.demande} actifs={actifs}
        onRelancer={onRelancer} onToutRevoir={onModifier} relance={relance}
        initiale={initiale} echanges={echanges} onMessage={onMessage} envoi={envoi} onVoirAnalyses={voirAnalyses} />

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
        {texte?.reformulation && <p className="reformulation">{pourClient(texte.reformulation)}</p>}
        {texte?.miroir?.map((ph, i) => (
          <p key={i} className="reformulation miroir-integre">
            {pourClient(ph.texte).replace(/[.\s]+$/, '')}
            {ph.faits?.length > 0
              ? <>, <button type="button" className="lien" onClick={() => voirAnalyses(ph.faits)}>d'après les analyses</button>.</>
              : '.'}
            {' '}<Etiquette type={ph.type} />
          </p>
        ))}
        {estPersona && texte?.miroir?.length > 0 && (
          <p className="muted petit">« Tu as dit » cite une phrase type du profil {profil.nom} (scénario fictif de l'équipe),
            pas une saisie que tu as faite.</p>
        )}
        {texte?.tensions?.map((t) => <p key={t} className="tension">{pourClient(t)}</p>)}
      </div>

      {dossier.questions?.length > 0 && (
        <div className="carte manque">
          <h2>{verdict.etat === 'indetermine' ? "Ce qu'il me faut pour conclure" : 'La question qui pourrait changer cet avis'}</h2>
          <ul>{dossier.questions.map((q) => <li key={q}><strong>{pourClient(q)}</strong>
            <PucesFaits ids={q.match(/F-\d+/g) || []} ouvrir={ouvrirFait} /></li>)}</ul>
          {verdict.etat === 'indetermine' && (
            <div className="actions"><button type="button" className="bouton principal" onClick={onModifier}>Compléter ma demande</button>
              <span className="muted petit">ou modifie la puce correspondante, en haut de la page.</span></div>
          )}
        </div>
      )}

      {/* 2. Pourquoi ce verdict, avec à sa droite le graphique qui soutient l'avis (un placement choisi seulement). */}
      <div className={!plan && demande.ticker ? 'colonnes' : ''}>
        {texte?.pourquoi?.length > 0 && (
          <div className="carte">
            <h2>Pourquoi ce verdict</h2>
            <ul className="phrases">{texte.pourquoi.map((p, i) => <Phrase key={i} p={p} ouvrir={ouvrirFait} />)}</ul>
          </div>
        )}
        {!plan && demande.ticker && (
          <div className="carte">
            <h2>La pire chute observée de {demande.ticker}</h2>
            <p className="muted petit">Cette courbe utilise le calendrier propre du titre. La comparaison du portefeuille utilise ses séances communes.</p>
            <GraphiqueChute ticker={demande.ticker} faitId={ids.chute} ouvrir={ouvrirFait} />
          </div>
        )}
      </div>

      {titreOptions && (
        <section className="bloc-options" aria-labelledby="titre-options">
          <h2 id="titre-options" className="titre-options">{titreOptions}</h2>
          {texte?.ce_qui_changerait?.length > 0 && (
            <ul className="phrases">{texte.ce_qui_changerait.map((p, i) => <Phrase key={i} p={p} ouvrir={ouvrirFait} />)}</ul>
          )}
          {plan
            ? <PlacementsDuPlan plan={plan} verdict={verdict} ouvrir={ouvrirFait} onAnalyser={onAnalyserPlacement} />
            : <div className="trois-options">
                {options.map((o, i) => <Option key={o.nom} o={o} principal={i === 1} ouvrir={ouvrirFait} />)}
              </div>}
          {dossier.suggestions?.placements?.length > 0 && (<>
            <h3 className="sous-titre-options">D'autres placements de la liste qui passent tes règles</h3>
            <PlacementsDuPlan plan={dossier.suggestions} verdict={verdict} ouvrir={ouvrirFait} onAnalyser={onAnalyserPlacement} suggestion />
          </>)}
        </section>
      )}
      <div className="actions">
        {dossier.bascule?.cases?.length > 0 && <button type="button" className="bouton principal" onClick={onBascule}>Bouger les curseurs</button>}
        <button type="button" className="bouton discret" onClick={() => setOnglet('detail')}>Voir le détail et les sources</button>
      </div>
      </>)}

      {onglet === 'detail' && (<>
      <div className="carte">
        <h2>Comment chaque chiffre mène au verdict</h2>
        <p className="muted petit">De gauche à droite : d'où viennent les données, ce qui est mesuré ou déclaré, les seuils choisis par
          l'équipe, les règles, puis le verdict. Survole ou sélectionne un élément pour suivre son chemin ; clique sur un chiffre pour
          voir sa source et sa méthode.</p>
        <CarteRaisonnement dossier={dossier} ouvrirFait={ouvrirFait} surligne={surligne} />
        <details className="liste-chiffres" open={surligne.length > 0}>
          <summary>La liste de tous les chiffres du dossier ({faits.length})</summary>
        <div className="defile-x">
          <table className="registre">
            <thead><tr><th>Ce que c'est</th><th>Valeur</th><th>Nature</th><th /></tr></thead>
            <tbody>
              {faits.map((f) => (
                <tr key={f.id} data-fait={f.id} className={surligne.includes(f.id) ? 'surligne' : ''}>
                  <td>{pourClient(f.libelle)}</td>
                  <td className="nombre">{pourClient(typeof f.valeur === 'object' && f.valeur !== null ? Object.entries(f.valeur).map(([k, v]) => `${k} ${v}`).join(', ') : `${f.valeur ?? '—'} ${f.unite}`)}</td>
                  <td><Etiquette type={f.type} /></td>
                  <td><PucesFaits ids={[f.id]} ouvrir={ouvrirFait} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </details>
      </div>
      {plan && <p className="muted petit">Plan ouvert : les règles ci-dessous sont celles appliquées à {plan.regles_de || 'la liste'}, le premier placement retenu.</p>}
      <div className={plan ? '' : 'colonnes'}>
        <div className="carte">
          <h2>Les règles appliquées</h2>
          <ul className="regles">
            {reglesTriees.map((r) => (
              <li key={r.code} className={`regle n-${r.niveau}`}>
                <div className="regle-tete"><strong>{r.libelle}</strong><PuceNiveau niveau={r.niveau} /></div>
                <p>{r.type && <Etiquette type={r.type} />} {pourClient(r.explication)}</p>
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
            <h2>Ce que le Sceptique a contesté</h2>
            {objections.map((o) => (
              <div key={o.id} className="objection">
                <p>{pourClient(o.texte)}</p>
                <p className="recalcul">↳ {pourClient(o.reponse)}</p>
                <PuceIssue issue={o.issue} />
              </div>
            ))}
          </div>
        </div>}
      </div>



      <div className={qualite.length ? 'colonnes' : ''}>
        {qualite.length > 0 && <div className="carte">
          <h2>Qualité des données</h2>
          {plan && <p className="muted petit">Les 7 contrôles, faits sur chaque placement de la liste jugé pour ton plan.</p>}
          <ul className="qualite">
            {qualite.map((c) => (
              <li key={c.code} className={`q-${c.statut}`}><span className="q-statut">{c.statut === 'ok' ? '✓' : '!'}</span>{c.libelle} <span className="muted">— {c.detail}</span></li>
            ))}
          </ul>
        </div>}
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
