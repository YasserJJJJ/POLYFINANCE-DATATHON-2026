# Révisions — tranche 1

## Raccordement K1 — autorisé par le porteur

Le prompt 1 demande une fonction d'accès unique aux symboles tout en disant
« Ne change aucun appelant » et en réservant l'interface à une autre tranche.

Constat :

```text
$ rg -n 'portefeuille_actuel' backend/alphaforge frontend/src
frontend/src/etapes/Etape2Verifier.jsx:85: ... portefeuille_actuel.includes(t) ...
frontend/src/etapes/Etape2Verifier.jsx:182: ... portefeuille_actuel.map((t) => ...
frontend/src/etapes/Etape2Verifier.jsx:183: ... portefeuille_actuel.filter((x) => ...
```

Les boucles Python itèrent déjà les clés d'un dictionnaire ; les appels React
`.map`, `.includes` et `.filter` exigent une liste.

Options :

1. Remplacer strictement les lectures par un accès aux symboles, sans changer
   calculs ni affichage. Coût : quelques appels et leurs tests, un adaptateur par
   langage, aucune dépendance. Recommandé.
2. Laisser le raccordement en attente. Coût : le contrat pondéré ne peut pas
   traverser tous les appelants ; tranche 1 incomplète.

Réponse explicite du porteur dans la conversation :
**« Oui, uniquement ce pont de compatibilité »**.
Cela autorise les seules adaptations d'accès dans les appelants concernés.
Les poids déclarés restent dans le profil ; leur lecture comme symboles ne les
modifie pas et ne change aucune formule.

## Précisions d'import sans changement de composant

- Le refspec local ne récupérait que la branche d'intégration : récupération
  explicite de la branche C, dont la tête distante est bien `6761d663…`.
- L'archive A contient `data/raw/.gitkeep`, sans données brutes. Exclusion de ce
  seul marqueur conformément à « sans data/raw » ; 259 fichiers préservés.
- `npm install` a supprimé des métadonnées `libc` du verrou ; restauration du
  verrou de C, sans changement des dépendances installées.

## Espaces des références A — conservation conforme au mandat

Commande : `git diff --cached --check`. Sortie : alertes « trailing whitespace »
et « new blank line at EOF » dans des fichiers originaux de A ; liste complète
dans `preuves/tranche-1/espaces-originaux-A.log`.

1. Conserver les octets et appliquer le contrôle des espaces au code neuf :
   coût nul sur le produit, identité des 259 empreintes et blobs vérifiée. **Retenu**,
   conformément à l'obligation de préserver les références.
2. Nettoyer les espaces des références : modifierait leurs empreintes et
   exigerait une révision de la règle de conservation ; non retenu.

Aucun composant n'est remplacé. Ces alertes de mise en forme ne sont pas des
échecs des tests du produit ; les originaux restent intacts.

## Tranche 2 — K5 et monotonie globale incompatibles (décision demandée)

Commande (depuis l'arbre `POLYFINANCE-fusion-analyse`) :

```sh
ALPHAFORGE_LLM=off PYTHONPATH=backend /Users/vpro/Documents/ChatGPT/POLYFINANCE-DATATHON-2026/backend/.venv/bin/python docs/fusion/preuves/tranche-2/rejouer_monotonie.py
```

Sortie complète : `preuves/tranche-2/contre-exemple-monotonie.json`. Amira, QQQ/NVDA à parts égales, demande XIU.TO :

| Montant | Avant | Après | Verdict |
|---|---:|---:|---|
| 14 000 CAD | −46,806061 % | −34,989514 % | ajustement |
| 17 500 CAD | −46,806061 % | −31,977170 % | coherent |

Les seuils sont inchangés (tolérance 33 %, capacité 38,2 %). Un montant **plus petit** laisse davantage du portefeuille risqué initial et dégrade ici le verdict. Les tests de monotonie existants passent sur leurs cas ; la grille d'une demande XIU.TO de 35 000 CAD présente 19 paires qui contredisent l'invariant global. Remplacer la dichotomie par une recherche exhaustive sécurise la recherche d'ajustement, mais ne rend pas ces verdicts monotones.

Deux options :

1. **Recommandée : préserver K5 et la grille exacte du Gardien**, remplacer la garantie globale de monotonie par l'égalité de chaque case au recalcul et conserver les anciens tests sur leurs cas. Recherche au pas de 100 CAD adaptée aux allocations non monotones. Coût : lever explicitement l'invariant global ; vérifier séparément la durée de la recherche exhaustive (le plafond de 1 s peut entrer en conflit).
2. **Préserver la monotonie du modèle antérieur** en gardant `ALPHAFORGE_CAPACITE=approximation` comme défaut et K3 à titre d'éclairage. Coût : renoncer au gain obligatoire C/K5 ; le portefeuille entier ne pilote plus la règle. Cela exige aussi une révision du mandat.

Aucun lissage artificiel de la grille ni modification des formules transférées n'est proposé. La clôture et le push attendent cette décision. Les autres vérifications de la tranche continuent.

### Décision reçue et appliquée — Tranche 2

Le porteur autorise l'option 1 : conserver K5 et les verdicts exacts, avec les conditions suivantes :

1. `_montant_exact` devient exhaustif au pas de 100 CAD ; aucune recherche ne suppose la monotonie.
2. Invariant 7 révisé : monotonie pour les demandes aggravantes ; une demande diversifiante peut améliorer le verdict quand le montant augmente. Le test global devient conditionnel, avec égalité de toutes les cases au Gardien. Aucun autre test supprimé.
3. `plus_petit_ajustement` cherche le montant le plus proche améliorant l'état, à la baisse **et** à la hausse. À égalité de distance, la baisse est examinée d'abord. Le texte donne uniquement un constat de simulation et le sens de variation ; aucun conseil d'acheter davantage.
4. Un fait HYPOTHESE explique cette propriété et renvoie aux faits avant/après/écart. Si une inversion est observée dans la grille, le fait contient l'exemple chiffré.
5. Robert/TSLA et Amira/BTC restent couverts par des tests de monotonie.
6. Le prompt 4 doit adapter les curseurs de l'étape 5 aux grilles non monotones, sans qualifier les inversions d'erreurs.

Le cadre **copié** `docs/fusion/CADRE-COMMUN.md` est modifié uniquement à l'invariant 7, conformément à cette instruction explicite. Son original dans Téléchargements et le manifeste historique de T1 restent intacts.

La recherche exhaustive seule a été mesurée à 1,692 s sur Robert avant optimisation (`essai-recherche-exhaustive.json`). Le cache des réponses exactes de B.fx_on ramène cette variante à 0,585 s (`apres-cache-change.json`). Pour la recherche élargie dans les deux sens, l'adaptateur réutilise les primitives **inchangées** de B (`validate_weights`, `_cad_panel`, `_wealth`, `drawdowns`) afin de calculer uniquement la perte nécessaire à la règle ; le dossier K3 reste produit par un appel complet à `compare_portfolios`. L'égalité des deux chemins et la durée finale sont vérifiées séparément. Les montants déjà exclus par les autres règles sont rejetés par ces mêmes règles, sans mesure financière superflue.

Le fichier `agents/redacteur.py` reste réservé à T4. Le pont dans `orchestrateur.py` remplace uniquement la phrase de changement par `option.constat` après restitution, en code. T4 pourra consommer directement ce champ et le champ `option.sens`, ainsi que `bascule.monotonie_montant`.
