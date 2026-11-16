# PROMPT 4 — Intégration, restitution, réception, livrables (seul, en dernier)

```
AUTORISATIONS (à remplir par le porteur avant l'envoi)
- git push de la branche d'intégration : OUI        vers : origin/fusion-corrections-deploiement, sans --force, après réception verte
- redéploiement de l'interface si la tranche 3 a déployé : OUI
- appels Bedrock de vérification : OUI
ÉTAT DES TRANCHES : tranche 2 = fusion/analyse @ ________   tranche 3 = fusion/aws @ ________
```

Tu es l'agent intégrateur de la fusion AlphaForge, **tranche 4 sur 4**. Les tranches 2 et 3 ont produit, chacune sur sa branche, la comparaison de portefeuille avant/après et la preuve d'appel AWS. Tu les réunis, tu les rends visibles et compréhensibles dans le parcours existant, tu fais passer la réception, et tu mets à jour les documents demandés par le défi. Tu n'ajoutes aucune capacité de calcul.

## Avant tout

1. Lis en entier `docs/fusion/CADRE-COMMUN.md` et les sections « Tranche 1 », « Tranche 2 », « Tranche 3 » de `docs/fusion/COMPTE-RENDU.md`. Si une tranche signale une décision en attente ou un écart, tiens-en compte avant d'intégrer.
2. Dans `/Users/vpro/Documents/ChatGPT/POLYFINANCE-DATATHON-2026`, sur `fusion-corrections-deploiement` : fusionne `fusion/analyse` puis `fusion/aws` (`git merge --no-ff`). Les fichiers sont disjoints par construction ; un conflit signifie qu'une tranche a débordé : lis les deux versions, garde le comportement vérifié de chacune, et note-le. Après chaque fusion : `pytest -q` et `npm run build`.
3. Si une tranche manque ou est incomplète, intègre ce qui est vert, laisse le reste hors de la branche, et adapte les étapes ci-dessous (un champ absent ne doit rien casser : les blocs d'interface n'apparaissent que si la donnée existe).

## Résultat attendu

Une personne qui suit le parcours voit, sans rien chercher : ce que la demande change à son portefeuille entier, sur quelle preuve, avec quelles limites ; quels appels de modèle ont réellement eu lieu ; et, quand il manque une information qui changerait la conclusion, laquelle. Les dix cas de réception passent. Les documents du dépôt décrivent le produit fusionné et la provenance de chaque partie.

## Étapes

**A. Restitution (backend, `agents/redacteur.py`).**
- Le gabarit en code (texte hors ligne) dit, quand la comparaison est disponible, la pire baisse du portefeuille après la demande, la valeur avant et le sens de l'écart, chaque phrase reliée à ses faits. Le sens (« plus profonde », « moins profonde ») vient du champ calculé par le code, jamais d'une comparaison faite par le modèle ou écrite en dur.
- Le contexte transmis au modèle inclut ces faits ; le contrôle d'ancrage reste inchangé et doit refuser un écart que le modèle recalculerait lui-même. Ajoute un test d'ancrage avec un texte fautif (écart inventé) et un texte correct.
- Une question marquée décisive par l'orchestrateur est restituée en premier dans les questions, avec ce qui changerait.
- Passe le nom de l'agent à `llm.appeler` là où la tranche 3 l'a laissé en attente.
- Règle de langage reprise de la recherche de A : le texte affirme un **écart entre deux options mesurées de la même façon** ; il ne présente pas une pire baisse passée comme un niveau de risque à venir. Vérifie que les limites du moteur (fenêtre de cinq ans, 2022, achat-conservation, cryptoactif échantillonné aux séances communes) figurent dans `texte.limites`.

**B. Interface (`frontend/`).** Deux composants neufs, petits, sans dépendance nouvelle, dans le style existant, qui ne s'affichent que si leur donnée est présente :
- `ComparaisonPortefeuille` à l'étape « Verdict », près de la règle « Perte supportable » : avant et après côte à côte (pire baisse, volatilité), l'écart et son sens, la limite retenue pour le profil, l'origine des poids (déclarés ou hypothèse d'équipondération, avec son étiquette), les limites du moteur repliées. Chaque nombre ouvre le tiroir de preuve existant. Lisible sans la couleur.
- `PreuveAppels` à l'étape « Analyse » : pour chaque rôle, modèle, identifiant de requête, jetons, latence ; en mode hors ligne, la mention que rien n'a été appelé.
- Messages : « actif hors de l'univers des 31 actifs du jeu de départ » et « le montant dépasse l'épargne totale » remplacent le message générique actuel ; la question décisive est mise en avant à l'étape « Vérifier » ou « Verdict ».
- Étape « Vérifier » : permettre de donner des poids aux placements détenus (facultatif pour la personne ; sans poids, l'hypothèse d'équipondération s'applique et s'affiche). Si cela dépasse le temps disponible, laisse la saisie telle quelle et dis-le.
- Vue « Comparer les 3 profils » : ajoute l'écart de pire baisse par profil.
- Fiche pour le conseiller (étape « Curseurs ») : ajoute la comparaison et la question décisive.
L'habillage reste celui de la branche (décision 3 du cadre). N'importe rien de l'interface de B.

**C. Réception.** Écris `backend/tests/test_reception_fusion.py` (hors ligne) et joue une fois les cas 1 à 3 avec Bedrock si c'est autorisé. Pour chaque cas, consigne l'attendu et l'observé.

| # | Cas | Attendu |
|---|---|---|
| 1 | Robert : 80 000 CAD dans TSLA sur 400 000, retrait dans 4 ans | `incoherent` ; la règle de perte cite le portefeuille après et avant ; version ajustée et placement large présents |
| 2 | Amira : 10 000 CAD en BTC-USD sur 40 000, horizon 15 ans | pas `coherent` sans réserve ; concentration signalée ; comparaison disponible avec la limite « cryptoactif » |
| 3 | Mateo : 15 000 CAD dans ENB.TO, exclusion Énergie | `incoherent` par exclusion ; alternative compatible ; la comparaison montre un écart favorable sans changer le verdict (une préférence prime sur une mesure) |
| 4 | Robert sans épargne totale | `indetermine`, question posée, aucune grille |
| 5 | Robert sans date de retrait | verdict des données fournies, plus une question décisive qui dit que la réponse changerait le verdict |
| 6 | 120 000 CAD demandés sur 100 000 | `indetermine` avec la raison ; aucune allocation |
| 7 | Actif hors univers (GameStop) | message explicite, pas d'erreur brute |
| 8 | Profil modifié : retrait repoussé à 10 ans, puis montant ramené à 20 000 | états successifs cohérents avec la grille ; la comparaison suit le montant |
| 9 | Preuve : partir de la pire baisse du portefeuille après | fait → méthode nommant le moteur → source des données → référence du registre, sans rupture |
| 10 | Sans identifiants AWS | tout fonctionne ; `appels_modele` vide ; verdict, règles, options, grille et comparaison identiques au mode avec modèle |

Ajoute la non-régression du cadre (section 10) : références figées, 201 tests du socle, construction de l'interface, durée hors ligne sous 1 s.
Inspecte l'interface dans un navigateur sur les cas 1, 2, 3 et 5 (captures dans `docs/fusion/preuves/tranche4/`). Un affichage non regardé est dit non regardé.

**D. Preuve des gains.** Remplis le tableau de la section 11 du cadre avec les sorties réelles : pour chaque gain, la valeur du produit fusionné, celle du meilleur composant seul (C seul sous `ALPHAFORGE_CAPACITE=approximation` ; B seul d'après `docs/fusion/preuves/`), et ce qui a régressé ou n'a pas pu être vérifié. Si un gain n'est pas confirmé, écris-le et propose soit la bascule de retour, soit la correction.

**E. Documents.**
- `README.md` : ce que fait le produit fusionné, installation, démarrage sur macOS, Linux et Windows (deux commandes ; `demarrer.ps1` n'est pas le seul chemin), profil AWS `alphaforge`, mode hors ligne, une section « Provenance » (ce qui vient de A, de B, de C, avec renvoi à `implementations/REFERENCES.md`).
- `docs/contrats.md` : exemple réel des champs K3 et K6 tiré d'un dossier produit.
- `docs/donnees.md` et `docs/sources.md` : méthodes et conventions des deux moteurs (K4), limites ; registre régénéré.
- Un document technique synthétique pour le défi (`docs/documentation-technique.md`) : méthodes et justification, sources et traitements, mécanisme d'explication avec un exemple reliant une conclusion aux données et à la trace, validations, limites, améliorations envisagées (les éléments réservés de A et B, dits comme tels). Ne décris que ce qui est vérifié ; ce qui est prêt et non exécuté est dit ainsi.
- N'écris ni la vidéo ni la page de présentation ; propose seulement, en fin de compte rendu, le déroulé de démonstration en cinq minutes que les cas 1, 3 et 5 permettent.

**F. Clore.** Étiquette `fusion/t4`. Complète `docs/fusion/COMPTE-RENDU.md` (section « Tranche 4 » et une synthèse finale : état de chaque invariant, tableau des gains, ce qui reste). `git push` seulement si la ligne d'autorisation le dit, vers la branche indiquée, sans `--force`.

## Fichiers que tu possèdes

`frontend/`, `backend/alphaforge/agents/redacteur.py`, `backend/alphaforge/garde_fous.py` si le contrôle d'ancrage doit apprendre le nouveau champ, `backend/tests/` (réception, ancrage), `README.md`, `docs/`. Tu peux corriger un défaut d'intégration dans un fichier d'une autre tranche si un cas de réception l'exige : fais-le dans un commit séparé qui le dit.

## Ce que tu ne fais pas

Pas de nouvelle règle ni de nouveau seuil ; pas de changement de formule ; pas d'import de l'interface de B ni du rendu HTML de A ; pas de nouvelle dépendance ; pas de publication ni de déploiement sans autorisation. Si un cas de réception échoue pour une raison de fond (la règle K5 donne un verdict que l'équipe juge faux), ne maquille pas : documente, propose la bascule `ALPHAFORGE_CAPACITE=approximation`, et demande la décision.

## Critère d'arrêt

Les dix cas sont consignés avec attendu et observé ; la non-régression est verte ; les documents sont à jour ; le compte rendu final est écrit. Ou bien un blocage est décrit avec sa preuve et deux options.
