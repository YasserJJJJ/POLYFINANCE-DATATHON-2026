// Texte montré à la personne : sans les identifiants internes du dossier (F-12, O-1), et sans décimales
// inutiles (« −46,806061 % » → « −46,8 % »). Les chiffres du dossier ne changent pas, seulement leur affichage ;
// les identifiants restent dans le dossier pour la traçabilité et ouvrent le détail au clic.
const ID = /F-\d+|O-\d+/
const PARENTHESE_IDS = /\s*\((?:\s*(?:F-\d+|O-\d+)\s*[,;]?\s*)+\)/g
// Un identifiant dans la phrase (« comme le montrent F-3 et F-4 ») devient « les analyses ».
const IDS_DANS_LA_PHRASE = /\b(?:F|O)-\d+(?:\s*(?:,|et)\s*(?:F|O)-\d+)*/g
const LONGUE_DECIMALE = /(\d+)[,.](\d{3,})/g

export function pourClient(texte) {
  if (texte == null) return ''
  let t = String(texte)
  if (ID.test(t)) t = t.replace(PARENTHESE_IDS, '').replace(IDS_DANS_LA_PHRASE, 'les analyses')
  t = t.replace(LONGUE_DECIMALE, (_, entier, decimales) => {
    const arrondi = Math.round(Number(`${entier}.${decimales}`) * 10) / 10
    return String(arrondi).replace('.', ',')
  })
  return t.replace(/\s+([.,;)])/g, '$1').replace(/\(\s+/g, '(').replace(/\s{2,}/g, ' ').trim()
}
