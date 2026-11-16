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
