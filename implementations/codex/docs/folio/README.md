# Folio — l’application intégrée

**[Ouvrir Folio](http://127.0.0.1:8768/)** · version 0.7.0. Si le serveur est arrêté, double-cliquer [`Ouvrir_AlphaForge.command`](../../Ouvrir_AlphaForge.command).

L’application utilise les dossiers, les quatre agents AWS et le moteur vérifié. Le prototype artistique demeure une référence conservée ; les trois directions ne pilotent plus l’application principale.

## Un parcours à essayer

1. [Lire Robert, version 5](http://127.0.0.1:8768/?dossier=4089e4b0d70f40b6b20d832fa261e1dc&revision=5&view=overview). Cliquer **30 000 CAD**, puis comparer avec la référence simple : elle atteint le même minimum. Passer à la lecture approfondie pour examiner l’objectif et les chocs.
2. Dans **Réviser**, choisir **Explorer un aperçu** et porter le retrait à **40 000 CAD**. Un vrai calcul local produit l’aperçu ; il n’appelle aucun agent et ne modifie pas le dossier principal. **Annuler cet aperçu** retrouve la version source.
3. [Examiner la révision réelle de Robert](http://127.0.0.1:8768/?dossier=71c8fb4b9d5e45fe98a4b4942e07c41e&view=compare). Les versions 5, 10 et 20 documentent respectivement le retrait de 30 000, le retrait de 40 000, puis une limite de perte par choc de 1 000 CAD. Le dernier minimum conditionnel est **74 400 CAD**. L’historique conserve aussi une erreur de saisie de test en version 15 : retrait saisi à 1 000 CAD, résultat 15 000 CAD ; elle n’est pas effacée ni présentée comme le scénario attendu.
4. [Ouvrir Amira](http://127.0.0.1:8768/?dossier=49ed5ae5903f41c297909b644ff7599a) puis [sa variante persistante à 5 % de TSLA](http://127.0.0.1:8768/?dossier=4a654c3cd06646c5a7765ff58820633d&view=compare). Les deux études ont leurs quatre contributions AWS. Le parent demeure inchangé. Les trajectoires restent historiques, sans projection à quinze ans.
5. Revenir à la bibliothèque et **ouvrir un nouveau dossier** : écrire une demande ou charger un exemple fictif, examiner les entrées, puis lancer l’étude. Une nouvelle étude ou correction utilise le compte AWS existant ; ouvrir une archive et changer le niveau de lecture n’appelle pas de modèle.

[Demande incomplète réelle](http://127.0.0.1:8768/?dossier=fedca8757f2540e7a2348bc22f63dd54&view=profile) · [Retrait impossible](http://127.0.0.1:8768/?dossier=1f7d3a73d5924a09ba73925655dce389).

## Ce qui est intégré

Folio est une revue annotée : conclusion et contrepoint, planche comparative, calculs et sources ouverts en marge. L’identité du prototype est étendue aux formulaires, à la bibliothèque, aux études en cours, aux dossiers incomplets et à l’historique.

- **Demande et qualification** : saisie naturelle, exemples modifiables, faits et provenance, questions utiles, saisie conservée.
- **Étude réelle** : tâches, événements, outils, pièces produites et reçus Bedrock consultables. Une attente n’est pas une animation de travail fictif.
- **Lecture progressive** : deux hiérarchies de présentation et le chapitre Comparer. Les faits, résultats et limites restent invariants.
- **Preuves** : montant, rendement ou perte mène à sa valeur, son pointeur, ses unités et ses hypothèses ; les passages documentaires restent accessibles avec leur niveau de lecture. Recherche dans le dossier consulté.
- **Réversibilité** : brouillon annulable, aperçu distinct, variante liée, correction versionnée, restauration d’entrées anciennes par nouvelle correction. L’historique n’est jamais supprimé.
- **Persistance et export** : reprise après rechargement ; retry de transmission avec la même clé ; export HTML lisible et JSON brut de la version examinée. Les octets du JSON sont conservés pour permettre le contrôle des empreintes.

La [matrice de réalisation](MATRICE.md) relie chaque interaction aux opérations et preuves. Le [système visuel](SYSTEME_VISUEL.md), le [schéma](ARCHITECTURE.md), les [décisions](DECISIONS.md) et la [revue indépendante](REVUE.md) exposent le fonctionnement et les corrections.

## Voir le produit

- [Robert : lecture essentielle](proofs/final/robert-essentiel.png), [lecture approfondie](proofs/final/robert-approfondi.png), [comparaison](proofs/final/robert-comparaison.png).
- [Amira : lecture historique](proofs/final/amira-essentiel.png), [variante](proofs/final/amira-variante.png), [mobile](proofs/final/amira-mobile.png).
- [Preuve en contexte](proofs/final/preuve-robert.png), [révision](proofs/final/robert-revision.png), [profil incomplet](proofs/final/profil-incomplet.png), [impossibilité](proofs/final/impossibilite.png).
- [Capture du parcours de consultation](proofs/final/parcours.mp4) : navigation dans des études déjà terminées, sans nouvelle inférence. Les archives et les variantes portent leur statut à l’écran.

## Vérifications décisives

La revue indépendante a confronté les calculs aux entrées et aux CSV, les hashes aux artefacts, les reçus AWS aux quatre rôles, et le navigateur aux réponses HTTP. Les défauts corrigés comprennent l’export d’une autre version, la normalisation des nombres qui cassait les empreintes, le mélange entre aperçu historique et version courante, la perte d’une saisie faite pendant une transmission, et le libellé de correction appliqué à une variante.

Les parcours comprennent : modifications de profil réelles, aperçu impossible ou incomplet, réponse tardive, reprise après perte de réponse HTTP **après commit**, conservation du brouillon, invariance du niveau de lecture, preuve contextuelle, clavier/focus, 320/390/1440 px, grands montants et reflow équivalent au zoom à 200 %. Le test de perte de réponse a retrouvé **un seul dossier et un seul run**. La comparaison Robert/Amira empêche de confondre un rendu réussi sur un seul scénario avec une intégration générale.

Les contrôles automatiques d’accessibilité complètent l’inspection visuelle ; ils ne certifient ni l’accessibilité exhaustive ni la compréhension financière. Aucun test utilisateur indépendant n’est revendiqué.

## Limites précises

Deux familles financières sont qualifiées : réallocation minimale sous chocs déclarés avec réserve abstraite, et comparaison historique en CAD. L’application complète ces parcours ; elle n’est pas un moteur universel de conseil patrimonial. Les situations hors périmètre restent conditionnelles ou demandent une clarification.

Robert : frais, impôts et inflation exclus ; aucune qualification d’un produit garanti ; les chocs ne bornent pas toutes les pertes futures. La référence simple atteint le même minimum dans le cas vérifié.

Amira : instantané acquis en novembre 2026 ; la comparaison ne prouve pas que les informations étaient disponibles au début de l’historique. Ni prévision à quinze ans, ni analyse exhaustive des positions internes des FNB, ni score ESG inventé.

Le profil global Bedrock utilise l’entrée `us-east-1` et **ne garantit pas une résidence canadienne**. Les opérations locales sont idempotentes ; une réponse AWS perdue après facturation peut nécessiter une nouvelle invocation, sans garantie d’une facturation unique. Les traces conservent cette distinction.

Les brouillons et aperçus sont propres au navigateur ; les dossiers et variantes persistants sont sur le serveur local. L’export HTML est une restitution statique, le JSON est la pièce inspectable. L’application et ses données ne sont pas publiées sur Internet.

## Reprise

Lire [REPRISE.md](REPRISE.md). L’ancienne interface reste accessible à [Workbench](http://127.0.0.1:8768/workbench), et le produit antérieur à `/legacy`. Les données et sessions antérieures ont été conservées. La sauvegarde initiale du produit et du prototype est dans `artifacts/folio_reference/`.
