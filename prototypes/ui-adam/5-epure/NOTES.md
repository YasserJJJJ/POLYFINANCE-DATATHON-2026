# 5 · Épure : la comparaison est l'interface

**Idée directrice.** Le produit mesure le portefeuille sans la demande et avec elle, de la même façon. La page est cette comparaison, dessinée comme une planche de dessin technique (bleu de plan, traits clairs, texte toujours sur aplat) : deux vues miroirs, des cotes entre elles, un cartouche en bas à droite.

**Mécanisme distinctif.** Les mesures sont des barres en miroir sur une échelle constante pour tout le cas. Dans la vue « Avec », un repère fantôme marque le niveau « Sans » ; l'excédent est hachuré, le manque est en tireté. Entre les deux vues, une ligne de cote (traits d'attache, flèches, valeur au milieu) porte l'écart. Seule la pire baisse est colorée, car c'est le seul sens calculé par le moteur. En Essentiel, la cote est en mots (« 6,3 points, baisse plus profonde »).

**Réellement interactif.**
- **Cote du montant** : curseur cranté sur `AF.parametres().montant`. Chaque cran porte le symbole du verdict précalculé. Le retrait et l'exclusion sont des cases du cartouche. Toute modification crée un aperçu : vue « Avec » en tireté, valeurs barrées, verdict périmé. « Recalculer la planche » appelle `AF.appliquer`.
- **Rideau** : `input type=range` natif et glisser sur la courbe. À gauche du rideau, « avec » en trait fort ; à droite, « sans ». La lecture datée suit le rideau. Les fenêtres I à III sont tracées sur la courbe et reprises en tableau. Rien n'est prolongé après le 12 nov. 2026.
- **Cartouche** : verdict (forme et libellé, `aria-live`), révisions A, B, C… Un clic sur un indice relit la révision : tampon « ARCHIVE : révision B » et bouton « Rétablir cette révision » (`AF.restaurer`). Annuler et Refaire. Épingler deux révisions ouvre une comparaison (`AF.comparer`).
- **Preuve** : chaque chiffre ouvre une fiche (`dialog`) avec la valeur exacte, le type, la source, la méthode et les références, en un seul geste.
- **Repères** : une bulle relie chaque règle bloquante ou à ajuster à sa mesure ou au segment concerné, et renvoie à la nomenclature.
- **Autres fonctions** : gamme d'opérations (code ou modèle, durées, appels Bedrock enregistrés, relecture `AF.relireTrace`), Essentiel/Approfondi, trois cas, trois cas particuliers, états de démonstration, mobile avec cartouche en bandeau repliable.

**Non réalisé.** Saisie libre d'une demande. Correction des lignes du profil autres que le retrait et l'exclusion (dit à l'écran). Essai d'un autre placement ou d'un montant non précalculé (29 700 $, par exemple), étiqueté « non réalisé dans ce prototype ». Impression soignée, seulement esquissée en `@media print`.

**Limites constatées.** Les courbes ont un point toutes les 5 séances : le creux tracé est moins profond que la pire baisse mesurée (Robert : −19,5 % tracé, −20,6 % mesuré). La légende le dit. Les écarts de rendement et de valeur finale n'ont pas de fait F-n : la fiche le précise.

**Réutilisable depuis `frontend/src`.**
- `ComparaisonPortefeuille.jsx` (`SENS_BAISSE`) : à remplacer par les vues cotées.
- `TiroirFait.jsx` et `Sources.jsx` (`ListeSources`) : pour la fiche de mesure.
- `Base.jsx` (`Etiquette`, `PucesFaits`, `PuceVerdict`) : à doter des formes d'état.
- `PreuveAppels.jsx` et `Etape3Trace.jsx` : pour la gamme d'opérations.
- `Etape5Bascule.jsx` : la grille alimente les crans du montant.
- `Comparer.jsx` : point de départ des planches à comparer.

Les vues cotées, le rideau et le cartouche sont des composants neufs.
