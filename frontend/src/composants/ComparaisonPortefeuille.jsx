import { Etiquette, PucesFaits } from './Base.jsx'

export const nombreMesure = (v) => v == null ? '—' : String(v).replace('.', ',')
export const SENS_BAISSE = { aggrave: 'Baisse plus profonde', ameliore: 'Baisse moins profonde', neutre: 'Baisse inchangée' }

// K3 fournit les deux bras et l'écart : aucun calcul de risque dans l'interface.
export default function ComparaisonPortefeuille({ dossier, ouvrirFait }) {
  const c = dossier?.comparaison
  if (!c || !Object.keys(c).length) return null
  if (!c.disponible) return <p className="manque">Comparaison du portefeuille indisponible : {c.raison}</p>
  const ids = c.faits || {}
  const ev = dossier.profil?.evaluation || {}
  const mesure = (v, unite, id, label) => (
    <button type="button" className="mesure-preuve" onClick={() => ouvrirFait([id])}
      aria-label={`${label} : ${nombreMesure(v)} ${unite}. Ouvrir la preuve`}>
      {nombreMesure(v)} {unite}<span aria-hidden="true"> ⓘ</span>
    </button>
  )
  return (
    <section className="comparaison-portefeuille" aria-label="Comparaison du portefeuille entier">
      <h3>Ce que la demande change au portefeuille entier</h3>
      <Etiquette type="SCENARIO" />
      <p className="muted petit">Deux allocations mesurées sur la même fenêtre passée. Aucune prévision de perte future.</p>
      <div className="defile-x">
        <table className="table-comparaison">
          <thead><tr><th scope="col">Mesure historique</th><th scope="col">Avant</th><th scope="col">Après la demande</th></tr></thead>
          <tbody>
            <tr><th scope="row">Pire baisse</th>
              {['avant', 'apres'].map((bras) => <td key={bras}>{mesure(c[bras].pire_chute_pct, '%', ids[`${bras}_pire_chute`], `Pire baisse ${bras}`)}</td>)}</tr>
            <tr><th scope="row">Volatilité</th>
              {['avant', 'apres'].map((bras) => <td key={bras}>{mesure(c[bras].volatilite_pct, '%/an', ids[`${bras}_volatilite`], `Volatilité ${bras}`)}</td>)}</tr>
          </tbody>
        </table>
      </div>
      <p><strong>{SENS_BAISSE[c.ecarts.sens_pire_chute]}</strong> : écart après moins avant de{' '}
        {mesure(c.ecarts.pire_chute_pts, 'points', ids.ecart_pire_chute, 'Écart de pire baisse')}.</p>
      <p>Écart de volatilité : {mesure(c.ecarts.volatilite_pts, 'points', ids.ecart_volatilite, 'Écart de volatilité')}.</p>
      {ev.perte_max_retenue_pct != null && <p><Etiquette type="HYPOTHESE" /> Limite retenue pour ton profil :{' '}
        {mesure(ev.perte_max_retenue_pct, '%', dossier.demande.ids_faits.h_perte, 'Perte supportable retenue')}.
        {' '}Ce barème ne borne pas une perte future.</p>}
      <p><Etiquette type={c.origine_poids === 'declare' ? 'FAIT' : 'HYPOTHESE'} />{' '}
        {c.origine_poids === 'declare' ? 'Poids déclarés' : "Poids inconnus : hypothèse d'équipondération"}
        <PucesFaits ids={[ids.poids_avant, ids.poids_apres]} ouvrir={ouvrirFait} /></p>
      <details>
        <summary>Fenêtre, allocations et limites de la comparaison</summary>
        <p>{c.fenetre.debut} → {c.fenetre.fin} · {mesure(c.fenetre.observations, 'séances communes', ids.fenetre_portefeuille, 'Fenêtre historique')}</p>
        <p>Allocations utilisées : <PucesFaits ids={[ids.poids_avant, ids.poids_apres]} ouvrir={ouvrirFait} /></p>
        <p>Achat-conservation, en CAD. Cinq ans de données, incluant 2022 : cette fenêtre ne couvre pas toutes les crises.</p>
        <ul>{c.limites.map((limite) => <li key={limite}>{limite}</li>)}</ul>
        <PucesFaits ids={[ids.limites_portefeuille]} ouvrir={ouvrirFait} />
      </details>
    </section>
  )
}
