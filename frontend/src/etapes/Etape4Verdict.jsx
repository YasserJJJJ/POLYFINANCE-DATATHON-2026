import { dollars } from '../api.js'
import { Etiquette, PuceIssue, PuceNiveau, PuceVerdict, PucesFaits } from '../composants/Base.jsx'
import GraphiqueChute from '../composants/GraphiqueChute.jsx'
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

function Option({ o, principal }) {
  return (
    <div className={`carte option ${principal ? 'principale' : ''}`}>
      <p className="option-nom">{o.nom}</p>
      {o.ticker && <p className="muted petit">{o.libelle_actif ? `${o.libelle_actif} (${o.ticker})` : o.ticker}</p>}
      <PuceVerdict etat={o.etat} />
      <dl className="option-chiffres">
        <div><dt>Montant</dt><dd>{dollars(o.montant_cad)}</dd></div>
        <div><dt>Horizon</dt><dd>{o.horizon_ans} an(s)</dd></div>
      </dl>
      {o.note && <p className="muted petit">{o.note}</p>}
    </div>
  )
}

const PERSONAS_NOMS = ['Amira', 'Mateo', 'Robert']

export default function Etape4Verdict({ dossier, ouvrirFait, onBascule, onModifier }) {
  const { verdict, texte, regles, options, faits, objections, qualite_donnees: qualite, demande, profil } = dossier
  const estPersona = PERSONAS_NOMS.includes(profil?.nom)
  const ids = demande.ids_faits || {}
  const ordre = { rouge: 0, orange: 1, gris: 2, ok: 3, non_evaluee: 4 }
  const reglesTriees = [...regles].sort((a, b) => ordre[a.niveau] - ordre[b.niveau])

  return (
    <section className="etape4">
      <div className={`verdict-tete carte etat-${verdict.etat}`}>
        <p className="surtitre">Le second avis</p>
        <PuceVerdict etat={verdict.etat} grand libelle={verdict.libelle} />
        <p className="compte-regles"><strong>{verdict.respectees}</strong> règle(s) respectée(s) sur <strong>{verdict.evaluees}</strong></p>
        {texte?.reformulation && <p className="reformulation">{texte.reformulation}</p>}
        {texte?.tensions?.map((t) => <p key={t} className="tension">{t}</p>)}
      </div>

      {verdict.etat === 'indetermine' && dossier.questions?.length > 0 && (
        <div className="carte manque">
          <h2>Ce qu'il me faut pour conclure</h2>
          <ul>{dossier.questions.map((q) => <li key={q}>{q}</li>)}</ul>
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

      <div className="trois-options">
        {options.map((o, i) => <Option key={o.nom} o={o} principal={i === 1 && options.length === 3} />)}
      </div>
      {texte?.ce_qui_changerait?.length > 0 && (
        <ul className="phrases">{texte.ce_qui_changerait.map((p, i) => <Phrase key={i} p={p} ouvrir={ouvrirFait} />)}</ul>
      )}
      <div className="actions">
        {dossier.bascule?.cases?.length > 0
          ? <button type="button" className="bouton principal" onClick={onBascule}>Bouger les curseurs</button>
          : <p className="muted petit">Les curseurs de bascule s'ouvrent dès que le verdict peut être calculé.</p>}
        <button type="button" className="bouton discret" onClick={onModifier}>Modifier mes réponses</button>
      </div>

      <div className="colonnes">
        <div className="carte">
          <h2>Les règles appliquées</h2>
          <ul className="regles">
            {reglesTriees.map((r) => (
              <li key={r.code} className={`regle n-${r.niveau}`}>
                <div className="regle-tete"><strong>{r.libelle}</strong><PuceNiveau niveau={r.niveau} /></div>
                <p>{r.type && <Etiquette type={r.type} />} {r.explication}</p>
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

        <div className="pile">
          <div className="carte">
            <h2>La pire chute observée</h2>
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
        </div>
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
                  <td className="nombre">{typeof f.valeur === 'object' ? Object.entries(f.valeur).map(([k, v]) => `${k} ${v}`).join(', ') : `${f.valeur} ${f.unite}`}</td>
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
    </section>
  )
}
