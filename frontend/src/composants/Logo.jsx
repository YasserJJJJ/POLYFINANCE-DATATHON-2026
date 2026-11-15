// Logo : un V en deux tons (deux traits qui se croisent) et le mot « verdict ».
// Les couleurs viennent des variables CSS --logo-a, --logo-b et --logo-mot (voir styles.css).
export default function Logo({ texte = 'verdict' }) {
  return (
    <span className="logo" role="img" aria-label={texte}>
      <svg width="34" height="25" viewBox="0 0 35 26" aria-hidden="true">
        <polygon points="2,3 10,3 16.75,16.5 12.75,24.5" className="logo-a" strokeWidth="1.4" strokeLinejoin="round" />
        <polygon points="25,0 33,0 20.75,24.5 12.75,24.5" className="logo-gap" strokeWidth="3.4" strokeLinejoin="round" />
        <polygon points="25,0 33,0 20.75,24.5 12.75,24.5" className="logo-b" strokeWidth="1.4" strokeLinejoin="round" />
      </svg>
      <span className="logo-mot" aria-hidden="true">{texte}</span>
    </span>
  )
}
