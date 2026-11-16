# Cahier commun des cinq prototypes `ui-adam`

Produit : « Second avis » (AlphaForge). Une personne dit ce qu'elle veut faire de son argent ; le produit dit si c'est cohérent avec sa situation, pourquoi, et ce qui le rendrait acceptable. Il ne conseille jamais d'acheter ou de vendre et ne prévoit rien. Le verdict est décidé par du code (le Gardien), jamais par un modèle.

Chaque prototype est une page autonome, sans dépendance ni étape de construction, qui s'ouvre par double-clic (`file://`) : `prototypes/ui-adam/<dossier>/index.html` avec son CSS et son JS dans le même dossier. Il charge, dans cet ordre, `../socle/fixtures.js` puis `../socle/socle.js`, et rien d'extérieur (pas de CDN, pas de police distante : piles de polices système).

## Le socle (`window.AF`) : la seule source des faits

Ne recalcule, n'invente et n'arrondis en dur aucun chiffre, aucune source, aucune étape d'agent. Tout vient de `AF`.

- `AF.etat()` → `{cas, montant, retrait, exclusion, niveau}`. `cas` ∈ `robert`, `amira`, `mateo`.
- `AF.dossier()` → le dossier réel de l'état courant ; `AF.dossierDe(etat)` pour un autre état. Champs : `profil` (dont `evaluation`, `tensions`, `citations`), `demande` (`texte`, `ticker`, `montant_cad`), `verdict` `{etat, libelle, respectees, evaluees}`, `regles[]` `{code, libelle, niveau, explication, faits[], type, references[]}`, `faits[]` `{id, libelle, valeur, unite, type, source, methode, lu_ou_calcule, references[]}`, `objections[]` `{id, cible, texte, recalcul, reponse, issue}`, `options[]` `{nom, ticker, montant_cad, etat, constat?, note?}`, `questions[]`, `comparaison` (K3 : `disponible`, `poids_avant/apres`, `avant/apres` `{pire_chute_pct, volatilite_pct, rendement_annualise_pct, valeur_finale_cad}`, `ecarts`, `limites[]`, `fenetre`, `politique`), `texte` `{reformulation, miroir[], pourquoi[], ce_qui_changerait[], limites[], tensions, avertissement}` (phrases `{texte, type, faits[]}`), `trace[]` `{agent, action, detail, duree_ms, faits[]}`, `qualite_donnees[]`, `series_portefeuille` `{avant:[[date, valeur, baisse_pct]…], apres:[…], avant_fenetres[], apres_fenetres[]}`, et, sur l'état de départ de chaque cas seulement, `bascule` `{montants[], horizons[], cases[{montant_cad, horizon_ans, etat}]}`.
- Paramètres modifiables : `AF.parametres()` → `{montant:[…], retrait:[…], exclusion:[…]}` (valeurs réellement précalculées ; aucune autre n'existe). Robert : 9 montants × retrait (dans 4 ans / non précisé). Amira : 8 montants. Mateo : 8 montants × exclusion du secteur Énergie (oui / non).
- Modifier en deux temps : `AF.proposer({montant})` crée un **aperçu** (le résultat affiché devient **périmé**, `AF.perime()` vrai, `AF.brouillon()` rend l'état proposé) ; `AF.appliquer()` l'analyse (nouvelle révision) ; `AF.abandonner()`. Raccourci : `AF.changer(patch)`.
- Historique : `AF.historique()` → `[{i, etat, parent, motif, heure, verdict, courant, nom}]` ; `AF.annuler()`, `AF.retablir()`, `AF.peutAnnuler()`, `AF.peutRetablir()`, `AF.allerA(i)` (relire une révision : statut « archive »), `AF.restaurer(i)` (crée une nouvelle révision identique, rien n'est effacé), `AF.reinitialiser()`.
- `AF.statut()` → `courante` | `archive` | `apercu`. Les trois doivent être visuellement impossibles à confondre.
- `AF.comparer(etatA, etatB)` → `{motif, verdict{avant,apres,change}, regles[{code,libelle,avant,apres,change}], mesures[{cle,titre,unite,avant,apres}]}`.
- `AF.mesures(dossier?)` → les mesures appariées `[{cle, titre, def, unite, avant, apres, ecart, sens?}]` (`titre` suit le niveau de lecture).
- `AF.profilLignes(dossier?)` → `[{cle, libelle, valeur, nature, note}]`, `nature` ∈ `donnee`, `preference`, `contrainte`, `inconnu`.
- `AF.changerCas(cas)`, `AF.cas()`, `AF.nomCas(cas)`.
- Niveau de lecture : `AF.niveau()` ∈ `essentiel` | `approfondi`, `AF.definirNiveau(n)`, `AF.terme(cle)` → `{titre, def}`.
- Preuves : `AF.fait(id)`, `AF.reference(id)` → `{id, type, auteurs, titre, annee, publication, lien, examen, apport}`, `AF.TYPES`, `AF.NIVEAUX_REGLE`, `AF.ETATS[etat]` → `{court, long, rang}`.
- Travail réel des rôles : `dossier.trace` (durées hors ligne) et `AF.execution()` → exécution Bedrock réellement enregistrée pour la demande de départ du cas `{source, appels_modele[{agent, modele, request_id, jetons_entree, jetons_sortie, latence_ms, garde_fou}], trace[{agent, duree_ms}], texte}` (ou `null`). `AF.relireTrace(dossier, (i, phase) => …)` rejoue les étapes enregistrées ; à présenter comme une **relecture**, jamais comme un agent en direct.
- Cas particuliers réels : `AF.speciaux.sans_epargne.dossier` (indéterminé, question), `AF.speciaux.impossible.dossier` (montant supérieur à l'épargne), `AF.speciaux.hors_univers` `{ok:false, message}`.
- Formats : `AF.fmt.cad`, `.pct(n, décimales)`, `.pts`, `.date`, `.ms`, `.retrait`, `.nombre` ; `AF.propre(texte)` arrondit à l'écran les nombres à six décimales des textes du produit (la valeur exacte reste dans le fait : montre-la dans la preuve).
- `AF.serieActif()` → `{ticker, pire_chute{…dates…}, points[{date, valeur}]}` ; `AF.abonner(fn)` (appelé à chaque changement : redessine) ; `AF.lien('index.html')` ; `AF.meta` (date, commit, mode).

L'état est partagé entre les cinq pages par `localStorage` et par l'ancre de l'adresse : ouvrir un autre prototype retrouve le même cas, le même état et le même historique.

## Parcours que chaque prototype doit permettre

demande → profil → analyse → résultat → preuve → modification d'un paramètre → comparaison → retour à l'état précédent. Et aussi :

1. Changer de situation (les trois cas) ; Robert « retrait non précisé » montre une **conclusion conditionnelle** avec sa question décisive ; un accès à au moins un cas particulier (`sans_epargne` ou `impossible` ou `hors_univers`).
2. Le profil : ce que le produit a compris, ligne par ligne, avec la nature de chaque ligne (donnée, préférence, contrainte, inconnue) ; l'inconnu est dit, jamais remplacé en silence. La correction se fait par les paramètres disponibles ; les autres champs sont en lecture seule, **et l'interface le dit**.
3. Le travail des rôles : journal d'étapes réelles, en distinguant code (Analyste, Gardien, contrôle des données) et modèle (Profileur, Sceptique, Rédacteur) ; durées ; appels réels de `AF.execution()` quand ils existent, sinon « aucun appel de modèle : mode hors ligne ». Pas de « l'IA réfléchit ».
4. Le résultat : verdict (quatre états, dont « indéterminé » traité comme un vrai résultat), règles, options comparées, ce qui changerait l'avis.
5. La preuve : de n'importe quel chiffre à son fait (valeur exacte, type, source, méthode) puis à ses références, en deux gestes au plus.
6. Modifier un paramètre → l'ancien résultat est marqué **périmé** tant que l'analyse n'est pas relancée → comparaison de l'avant et de l'après → annuler / rétablir / relire une révision / restaurer.
7. États de chargement, d'erreur et de reprise : un sélecteur discret « États de démonstration » (normal, chargement, erreur, reprise) clairement étiqueté comme démonstration.
8. Deux profondeurs de lecture (Essentiel / Approfondi) par un contrôle toujours visible. Mêmes faits, mêmes limites ; seuls vocabulaire et densité changent.
9. Mobile réellement utilisable à 375 px de large : pas de défilement horizontal de page, cibles tactiles de 44 px, texte lisible.
10. Bandeau permanent et sobre : « Simulation éducative · données de démonstration précalculées par le moteur réel » avec date et commit de `AF.meta`.
11. Un lien « Galerie » vers `../index.html` et des liens vers les quatre autres prototypes (`AF.lien('../<dossier>/index.html')`).

## Règles tirées de la recherche (détail : `docs/ui-adam/recherche/`)

- Le passé se voit dans le dessin : axe daté, fenêtre « 2021-11-12 → 2026-11-12, observé », aucun prolongement vers l'avenir, verbes au passé ou au conditionnel. Un avertissement générique ne suffit pas.
- L'écart apparié (après moins avant) est le message ; les niveaux seuls ne le sont pas. Toujours montrer avant et après mesurés de la même façon.
- Deux niveaux de divulgation : verdict et raisons, puis preuve à la demande. Pas de troisième niveau.
- Jamais la couleur seule : chaque état porte un libellé et une forme ou un motif.
- Texte jamais posé directement sur une texture ou un dégradé : toujours sur un aplat, contraste d'au moins 4,5:1.
- Grain et trames statiques. Tout mouvement respecte `prefers-reduced-motion`.
- Clavier : tout est atteignable, focus visible, `Échap` ferme, `aria-live="polite"` pour les changements de résultat, éléments natifs (`button`, `input type=range`, `dialog`, `details`).
- Une interaction non réalisée est étiquetée « non réalisé dans ce prototype ». Rien de fictif pour remplir.
- Français, tutoiement comme le produit, montants en dollars canadiens. Aucun mot de conseil (« achète », « vends », « tu devrais »).

## Remise

Fichiers dans ton dossier seulement. Vérifie la syntaxe (`node --check` sur tes JS) et relis ton HTML. N'utilise pas les outils de navigateur (partagés) : la vérification visuelle est faite ensuite. Ne touche ni au socle, ni aux autres dossiers, ni à `frontend/`, et ne fais aucun commit. Ajoute `NOTES.md` (30 lignes au plus) : idée directrice, mécanisme distinctif, ce qui est réellement interactif, ce qui n'est pas réalisé, composants du produit existant (`frontend/src`) réutilisables pour l'intégrer.
