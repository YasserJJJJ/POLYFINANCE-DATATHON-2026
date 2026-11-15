// Le nom affiché est défini ici, à un seul endroit.
export const NOM_PRODUIT = 'AlphaForge AI'
export const SOUS_TITRE = 'Second avis'

export function Logo({ size = 34 }) {
  return (
    <svg width={size} height={size * 0.735} viewBox="0 0 35 26" aria-hidden="true">
      <polygon points="2,3 10,3 16.75,16.5 12.75,24.5" style={{ fill: 'var(--logo-a)', stroke: 'var(--logo-a)' }} strokeWidth="1.4" strokeLinejoin="round" />
      <polygon points="25,0 33,0 20.75,24.5 12.75,24.5" style={{ fill: 'var(--background)', stroke: 'var(--background)' }} strokeWidth="3.4" strokeLinejoin="round" />
      <polygon points="25,0 33,0 20.75,24.5 12.75,24.5" style={{ fill: 'var(--logo-b)', stroke: 'var(--logo-b)' }} strokeWidth="1.4" strokeLinejoin="round" />
    </svg>
  )
}

export function Marque() {
  return (
    <span className="flex items-center gap-2.5">
      <Logo size={30} />
      <span className="pb-[2px] font-logo text-[21px] font-bold leading-none tracking-[-0.03em] text-[var(--logo-w)]">{NOM_PRODUIT}</span>
      <span className="hidden border-l border-border pl-2.5 text-[13px] text-muted-foreground sm:inline">{SOUS_TITRE}</span>
    </span>
  )
}
