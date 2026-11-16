# 4 · Fil : une conversation avec ses propres « et si »

**Idée directrice.** Sur téléphone, tout tient dans un fil vertical déroulé au pouce. Ta demande (bulle sombre, ta voix) → ce qu'on a compris → le travail → le second avis → pourquoi → ton épargne avant/après → ce qui changerait l'avis → limites. Chaque « Et si… » ajoute en bas une bulle (ta question), une carte « Ce qui a changé » (`AF.comparer`) et un nouvel avis. Le fil **est** `AF.historique()` : rien ne s'efface.

**Mécanisme distinctif.** La température : l'en-tête de chaque avis est un dégradé thermique granuleux (froid = cohérent, chaud = incohérent, brume = indéterminé), le texte toujours sur une plaque blanche ; pictogrammes de forme distincte (rond, triangle, octogone, cercle pointillé). Trois statuts impossibles à confondre : actuel (température pleine), aperçu (en-tête hachuré, verdict barré, « ce résultat ne correspond plus à ta question », bulle pointillée « question en attente »), archive relue (en-tête désaturé, tampon, bande en haut). Barre basse en verre cannelé, repli opaque sans `backdrop-filter`.

**Réellement interactif.**
- Puces « Et si… » : 9 montants, retrait (Robert), exclusion Énergie (Mateo), autre situation → `AF.proposer` puis « Voir l'avis » (`AF.appliquer`) ou « Laisser tomber ». Notification « Annuler » / « Rétablir » après chaque changement ; aussi dans le menu.
- Anciens avis en retrait : « Revenir à cet avis » (`AF.restaurer`), « Relire » (`AF.allerA`, archive). Chapitres d'autres situations repliés.
- Preuve en deux gestes : chaque chiffre ouvre une feuille basse (`<dialog>`) : valeur exacte, type, source, méthode, puis références repliées. Le chiffre est relié au fait cité par la phrase, sinon au profil, sinon par valeur exacte ; à défaut il est dit « sans fait rattaché » (jamais deviné). Soulignement codé : plein fait, tirets hypothèse, points scénario, double profil, ondulé sans fait.
- Essentiel / Approfondi (interrupteur toujours visible) : mêmes faits ; Approfondi ajoute termes techniques, règles ouvertes, tableau des faits par carte, volatilité, 4 mesures, fenêtres repères, limites dépliées.
- Relecture des étapes enregistrées (`AF.relireTrace`, étiquetée « relecture », jouée une fois à l'ouverture) ; appels Bedrock réels (`AF.execution`) dans une feuille.
- Bande « Selon le montant » (avis précalculés), conclusion conditionnelle de Robert avec réponse en un geste, cas particuliers (sans épargne, montant impossible, hors univers) ajoutés hors historique.
- Ordinateur (≥ 1000 px) : fil central 480–520 px + panneau fixe « plan du fil » et « comparer deux avis » (sélecteurs A/B). Téléphone : même panneau dans le menu. Pastille « Avis n°k ↓ » quand l'avis sort de l'écran.
- États de démonstration (chargement, erreur, reprise) dans le menu, étiquetés.

**Non réalisé.** Répondre à « Combien as-tu d'épargne ? » ; changer d'actif ; montants non précalculés (29 700 $) : tout est étiqueté « non réalisé dans ce prototype ». Pas de thème sombre. Liens vers la galerie et les dossiers `1-carnet`, `2-relief`, `3-pupitre`, `5-epure` (présents), avec l'état partagé dans l'ancre.

**Vérification faite.** `node --check app.js` ; parcours complet (3 cas, aperçu, appliquer, annuler, rétablir, restaurer, relire, cas particuliers, démos, plan, comparaison, réinitialiser) rejoué dans un mini-DOM node, en mode téléphone et ordinateur : aucune exception, aucun « undefined/NaN/null » affiché, aucun id en double, 68 rattachements chiffre → fait contrôlés sur Robert. **Pas de vérification visuelle en navigateur** (outils partagés) : à faire à 375 px.

**Réutilisable de `frontend/src`** (vu par en-têtes seulement) : `TiroirFait.jsx` (feuille de preuve), `Base.jsx` (puces verdict/niveau), `ComparaisonPortefeuille.jsx` (paire avant/après), `GraphiqueChute.jsx` (courbe), `Sources.jsx` (références), `PreuveAppels.jsx` (appels), `Etape3Trace.jsx` (travail), `Etape4Verdict.jsx`, `Etape5Bascule.jsx` (bande des montants), `Comparer.jsx` (panneau).
