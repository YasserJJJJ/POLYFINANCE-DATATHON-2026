// Métadonnées Converse constatées, jamais déduites de l'état du compte AWS.
export default function PreuveAppels({ appels }) {
  if (!Array.isArray(appels)) return null
  return (
    <section className="carte preuve-appels" aria-label="Preuves des appels de modèles">
      <h2>Les appels réellement effectués</h2>
      {!appels.length
        ? <p>Aucun modèle n'a été appelé pour ce dossier. Le parcours fonctionne hors ligne avec les calculs et les gabarits en code.</p>
        : <ul>{appels.map((a, i) => (
          <li key={`${a.request_id}-${i}`}>
            <h3>{a.agent}</h3>
            <dl>
              <dt>Modèle</dt><dd>{a.modele}</dd>
              <dt>Identifiant de requête</dt><dd className="mono">{a.request_id || 'Aucun identifiant retourné'}</dd>
              <dt>Jetons entrée / sortie</dt><dd>{a.jetons_entree ?? '—'} / {a.jetons_sortie ?? '—'}</dd>
              <dt>Latence mesurée</dt><dd>{a.latence_ms ?? '—'} ms</dd>
              <dt>Fin de l'appel</dt><dd>{a.stop_reason || 'Non renseignée'}</dd>
              {a.garde_fou && <><dt>Garde-fou</dt><dd>{a.garde_fou}</dd></>}
            </dl>
          </li>
        ))}</ul>}
    </section>
  )
}
