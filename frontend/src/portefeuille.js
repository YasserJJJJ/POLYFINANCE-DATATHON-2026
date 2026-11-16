// Vue des symboles pour l'interface existante ; les poids du profil restent intacts.
export const symbolesPortefeuille = (portefeuille) =>
  Array.isArray(portefeuille) ? [...portefeuille] : Object.keys(portefeuille ?? {})
