# Folio intégré — décisions techniques

## Identité et périmètre

Folio devient l’entrée de l’application existante, sur le port 8768. Son prototype reste consultable sur 8770 et une copie avec empreintes est conservée dans `artifacts/folio_reference/`. La route `/workbench` conserve l’ancienne interface. Le moteur `finance.py` reste inchangé.

Composition retenue : revue annotée, papier clair, encre verte, contrepoints rouges, Newsreader et DM Sans servies localement. La marge explique et relie ; les chiffres restent associés à leur mandat et à leur unité. Deux chapitres d’analyse (comprendre/comparer), un chapitre de révision ; profil, historique, étude et recherche constituent l’appareil de lecture. Les dossiers historiques et les erreurs reçoivent le même traitement éditorial.

## Modèle d’interaction

Quatre opérations distinctes :

1. **Consulter** le dossier ou une archive : lecture de SQLite et des artefacts immuables, sans calcul ni inférence.
2. **Explorer un aperçu** : exécution du moteur déterministe depuis les entrées sélectionnées ; résultat hors dossier, conservé dans le navigateur et annulable. Aucune revue documentaire renouvelée ni nouvel appel d’agent. Une base modifiée rend l’aperçu non applicable.
3. **Créer une variante** : nouveau dossier lié à l’original et analysé par les quatre agents. L’original reste conservé.
4. **Corriger le dossier** : nouvelle révision, invalidation transitive et reprise de la chaîne. Rétablir des entrées anciennes crée une nouvelle correction ; cela ne supprime aucune version.

Le brouillon est séparé des résultats. Les modes de lecture sont enregistrés indépendamment du profil financier. Ils ne produisent aucune requête de calcul ou d’inférence.

## Transport et persistance

L’API `/api/folio` projette les dossiers existants pour la lecture ; elle ne constitue pas une seconde base métier. Les archives rejouent les écritures et invalidations jusqu’à la révision sélectionnée et excluent les résultats futurs. Les créations et corrections emploient une clé d’idempotence persistante avec empreinte du corps, enregistrée dans la même transaction que la mutation. Une interruption après le commit peut reprendre le même run.

Les appels AWS restent soumis aux limites existantes : une réponse perdue après facturation ne permet pas de promettre exactement une facturation. Les traces conservent cette incertitude. L’idempotence du transport Folio ne transforme pas cette limite en garantie universelle.

Le contrôleur conserve les brouillons, la dernière opération non confirmée et l’aperçu dans localStorage. Un retour 409 conserve la saisie et exige une réconciliation avec la version courante ; il ne remplace pas silencieusement les faits d’un autre travail. Le polling montre les tâches et événements réellement enregistrés, sans pourcentage inventé.

## Dossier de preuve

Les affirmations numériques sont liées aux pointeurs JSON et à l’empreinte de l’analyse. Les documents exposent les passages conservés, la source, le niveau de lecture et leurs limites. La référence simple du dossier de défense n’est jointe que si les entrées et hypothèses correspondent à celles vérifiées. L’export JSON correspond à la version examinée ; l’export HTML fournit une restitution lisible avec sa portée.

## Outils retenus

- HTML/CSS/SVG et JavaScript natifs : composition originale, interactions et graphiques inspectables, sans service d’inférence auxiliaire.
- Playwright et axe-core locaux : parcours, clavier, écrans comparables, contrôles automatiques d’accessibilité.
- SQLite, LangGraph et artefacts immuables existants : versions, reprise et transitions réelles ; qualification conservée des étapes précédentes.
- Bedrock, profil `global.openai.gpt-6-astra`, entrée `us-east-1` : quatre contributions réelles. Cette route mondiale ne constitue pas une résidence canadienne.
- Références visuelles et d’interaction déjà examinées dans `docs/directions_artistiques/` et `docs/experience/` : reprises sans recommencer la recherche. Aucun outil de design à inférence non qualifiée, abonnement ou service payant supplémentaire.

## Limites de portée conservées

Robert : réserve abstraite, chocs hypothétiques sans probabilités, coûts/fiscalité/inflation exclus, optimum du déplacement de capital uniquement. La référence simple atteint également 30 000 CAD pour le cas vérifié.

Amira : description rétrospective sur un snapshot acquis en novembre 2026, pas stratégie connue en 2021 ni projection à quinze ans. Une préférence ESG sans preuve demeure inconnue.

## Dernières corrections de fidélité

L’export JSON télécharge les octets HTTP bruts : un passage par `JSON.stringify` normalisait `100000.0` en `100000` et empêchait la vérification canonique des hashes Python. Les aperçus conservent aussi leur réponse brute après rechargement. Les archives exportées sont épinglées à la révision regardée.

Le profil sépare les questions adressées à l’humain des besoins internes grâce au champ `target` des nœuds de questions ; les formulations regroupées restent consultables. Une nature de réserve inconnue n’est jamais rendue comme une réserve abstraite connue. Les noms de méthodes dans le profil sont traduits en intitulés lisibles, avec les pièces originales accessibles.

Le chargement d’un autre dossier retire le résultat précédent avant de présenter le nouveau. Une réponse de reprise retardée ne ramène pas l’utilisateur dans le dossier qu’il vient de quitter. Une réponse à un dossier encore incomplet propose une correction par les agents ; les aperçus restent le choix initial des dossiers déjà analysés.

Le contrôle d’un aperçu à grands montants (capital fictif d’un milliard CAD, retrait de 300 millions) a révélé un débordement global de 9 px à 320 px. Les grands titres monétaires s’adaptent désormais à la longueur de leur valeur ; les montants secondaires et le sélecteur de version restent dans leur région. Le même aperçu a été recalculé et contrôlé : 320 px de page pour 320 px de viewport, montant intégral, aucune mutation ni inférence. Un aperçu issu d’une archive affiche désormais sa **base historique**, sans prétendre être simultanément l’archive elle-même.

Une transmission non confirmée ne peut pas être remplacée par une seconde commande dans la mémoire du navigateur. La consultation et la préparation d’un autre brouillon restent possibles ; la même clé doit d’abord être résolue. Le test `folio_pending.cjs` utilise deux réponses 503 synthétiques : premier corps conservé, deuxième brouillon conservé, retry du corps original, aucune écriture serveur. La clé de brouillon d’origine est conservée avec la commande pour éviter d’effacer une saisie faite dans un autre contexte.
