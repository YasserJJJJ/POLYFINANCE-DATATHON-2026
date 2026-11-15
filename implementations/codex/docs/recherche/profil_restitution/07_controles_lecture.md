# Contrôles de lecture, provenance et limites

15 novembre 2026. Le présent journal porte sur la branche Agents 0 et 3, pas sur tous les travaux de la racine.

## Ce qui a effectivement été fait

- Lecture du mandat Prompt 2 et des références §9.4/9.5 ; examen des 64 entrées, soit 74 URL distinctes du dossier. Le contrôle d’ensemble avec l’inventaire commun trouve **zéro URL manquante** dans ces deux sections.
- Ajout du complément Amershi U354/U355 et de 28 URL P001–P028. Ces URL comprennent des tentatives infructueuses, des versions et des dépôts ; elles ne sont pas 28 études indépendantes intégralement lues.
- Recherche web documentaire, téléchargement HTTP sans inférence auxiliaire, extraction locale de texte, inspection statique de dépôts, lectures ciblées et contrôles visuels PDF.
- Création de 23 fiches de sources décisives, de deux fiches de fonctions et de protocoles candidats. **Aucun protocole humain, questionnaire financier, méthode d’élicitation ou nouveau produit n’a été exécuté ou validé par cette branche.**

La métadonnée initiale de la session spécialisée `01a1df0e-7da5-7690-b09d-b15497a722d2` indique `amazon-bedrock-runtime`. La racine conserve la preuve commune de route. Cette observation ne remplace pas un relevé de facturation et ne prouve pas la région physique de chaque calcul interne.

Les [requêtes documentaires](requetes_documentaires.json) sont extraites des appels effectivement consignés dans la session. Les fautes de syntaxe de certaines requêtes, par exemple `site.fpsb.org` au lieu de `site:fpsb.org`, sont conservées ; elles ne sont pas réécrites comme si une recherche mieux restreinte avait eu lieu. Les ouvertures de références trouvées et les téléchargements directs complètent ces requêtes.

## Échelle d’examen

| Statut | Signification |
|---|---|
| Métadonnées / notice | Identité, version ou accès examiné ; contenu scientifique non analysé. |
| Résumé lu | Résumé disponible examiné ; pas d’affirmation que méthode et annexes ont été auditées. |
| Passages analysés | Sections/pages nommées effectivement lues ; les autres parties ne sont pas réputées vérifiées. |
| Texte des critères lu | IPDAS 5.0 : les quatre pages de critères ont été lues. Cela ne signifie pas que l’article méthodologique BMJ associé a été lu. |
| Code inspecté | Fichiers et portions explicitement nommés ; aucun audit complet ni exécution implicite. |
| Protocole proposé | Expérience future décrite ; aucun résultat de réussite revendiqué. |

Les métadonnées des caches indiquent `collecte_automatique_non_lecture_critique`. Elles sont volontairement laissées telles quelles. Le [triage](01_triage_64_references.json) et les [fiches](02_sources_decisives.json) ajoutent le degré de lecture critique réel.

## Contrôles visuels des passages déterminants

La compétence PDF a été lue avant ces travaux : `/Users/vpro/.codex/plugins/cache/openai-primary-runtime/pdf/26.1105.12137/skills/pdf/SKILL.md`. Extraction avec Poppler ; pages rendues puis inspectées visuellement. Les numéros ci-dessous sont ceux du fichier PDF, parfois distincts de la pagination imprimée.

| Fichier examiné | Page PDF / image locale | Objet du contrôle |
|---|---|---|
| U036, avis 31-368 | 5 — [image](lectures_visuelles/U036-5.png) | Portée de « lower of the two », justification, exemples de lacunes. |
| U037, Chajewska | 4 — [image](lectures_visuelles/U037-4.png) | Choix myope, arrêt et hypothèses de calcul de valeur d’information. |
| P005, FPSB | 55 — [image](lectures_visuelles/P005-55.png) | Correspondance processus et pratiques professionnelles. |
| P010, Buçinca | 7 — [image](lectures_visuelles/P010-7.png) | Conditions expérimentales, IA simulée et attente de trente secondes. |
| P014, Ross/Lo | 13 — [image](lectures_visuelles/P014-13.png) | Valeurs détaillées des tableaux et limites de la fourchette de résumé. |
| P017, Boutilier | 12 — [image](lectures_visuelles/P017-12.png) | Définitions de regret et ensembles sur lesquels porte la garantie. |
| P019, Grable–Lytton | 4 — [image](lectures_visuelles/P019-4.png) | Distinction du construit et des mesures comparatrices. |
| P023, IPDAS 5.0 | 1 — [image](lectures_visuelles/P023-1.png) | Critères de qualification, critères essentiels et mentions de version. |
| P027, Bertrand et al. | 10 — [image](lectures_visuelles/P027-10.png) | Figure 4, intervalles, légende des seuils et début des limites. |
| P001/P002, AMF | NI75 / IG79 | Captures PDF affichées par l’outil web et examinées ; pas de PNG local conservé. |

Le contrôle visuel ne couvre pas toutes les pages des PDF téléchargés. L’absence d’un défaut dans les pages vues ne prouve pas l’intégrité analytique de toute l’œuvre.

## Accès problématiques et substitutions

| Référence | Constat et traitement |
|---|---|
| U081, rapport OSC IAP | Le cache contient un préfixe d’en-têtes HTTP avant la signature PDF, à l’octet 564. Une copie a été créée à partir de `%PDF`, puis extraite. [Métadonnées de réparation](collecte/U081_repare.json), [PDF](collecte/U081_repare.pdf). L’original commun n’a pas été modifié. |
| U035, CIRO GN3400 | HTTP 403, également infructueux par web ; aucune lecture du corps revendiquée. Les textes primaires actuels P001/P002 et U036 fondent l’analyse retenue. |
| U034, CP2021 | Version ancienne, conservée comme provenance ; actualisation par P001/P002 du 4 juillet 2026. |
| P001–P003 AMF | Téléchargements locaux 403 ; lecture ciblée et captures possibles par l’outil web. Ne pas dire que les fichiers primaires ont été téléchargés localement. |
| U080 ESMA | Miroir 404 ; PDF officiel P025 retrouvé et passages pertinents lus. |
| U184 et U088 | Réponses 202/redirections sans article exploitable ; ni page d’accueil ni page vide comptée comme texte lu. |
| U189/U212/U225 PMC | Pages cookies/captcha à la place du texte ; aucun résultat scientifique repris comme lu sur ces fichiers. |
| U024/U090/U192/U215/U227 | Accès 403. U024 a un résumé accessible U195 ; U227 est remplacé pour l’analyse par le texte éditeur P018. |
| U211 | Erreur de résolution ; résumé de congrès non lu. |
| U214 | URL Cleveland Fed 404 ; document de travail non lu dans cette branche. |
| P009 Cochrane | Texte intégral refusé ; résumé officiel structuré P008 effectivement lu. |
| P016 BMJ/IPDAS | Article complet inaccessible. Seuls les critères officiels P023 et les pages de version/ressources sont analysés. |
| P024 | Le PDF retrouvé est un manuel espagnol de critères, édition 2014, et non l’article Joseph-Williams 2014 recherché. Couverture/sommaire examinés ; écarté comme preuve du nouvel IPDAS 5.0. |
| U220 HAL | Notice désormais accessible ; texte complet P027 retrouvé. La précédente mention d’inaccessibilité dans le dossier est donc corrigée. |
| P026 SEC | HTTP local 403 ; guide officiel lu par web. P028 Cornell est une reproduction du règlement, explicitement distinguée d’une copie primaire officielle. |

Les fichiers bruts tiers sont des copies de travail documentaire. Leurs licences, ainsi que celles des instruments, modèles et données, restent distinctes. Leur présence locale n’autorise pas une diffusion commerciale ou une intégration au produit.

## Contrôles de cohérence documentaire

- Les 64 entrées ont des IDs distincts ; 30 sont rattachées à §9.4 et 34 à §9.5. Les deux URL complémentaires U354/U355 sont regroupées dans une entrée séparée.
- Les 23 fiches distinguent source professionnelle, résultat empirique, théorie et code. Les protocoles du journal ne sont pas décrits comme réalisés.
- Les dates de publication, version et accès ne sont pas interchangeables : Grable–Lytton 2015, Berlin Numeracy 2012 et Amershi 2019 ne deviennent pas des études de 2026 parce que leurs pages ont été consultées cette année.
- Le constat de non-significativité chez Bertrand et al. ne prouve pas une absence d’effet ou une équivalence entre formats. La discussion du protocole conserve cette limite.
- L’absence de `LICENSE` à la racine de CLAMBER ne prouve pas l’absence de droits ailleurs ; les droits sont **non établis**. La licence MIT GATE est vérifiée pour le code inspecté, sans conclure sur les données.
- Les sources non lues ne soutiennent aucun effet chiffré transféré au projet. Les limites de généralisation font partie des fiches et ne sont pas ajoutées seulement en note finale.
