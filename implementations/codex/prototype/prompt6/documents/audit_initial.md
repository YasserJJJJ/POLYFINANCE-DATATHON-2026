# Observation de l’application avant conception — Prompt 6

**Périmètre observé : application 0.5.0 sur `http://127.0.0.1:8768`, le 15 novembre 2026.** Les quatre dossiers du dossier de défense ont été ouverts avec Chromium/Playwright, à 1440 × 1050 et 390 × 844. Synthèse, demande, preuves, activité, versions et inspecteur de valeur ont été parcourus. Aucune mutation financière ni nouvelle inférence n’a été déclenchée ; seuls les événements d’affichage prévus par l’application ont été enregistrés.

Le relecteur n’a pas écrit cette interface. Sa session `01a1e0bf-9b5c-78f3-bbeb-726cd456fb5d` indique `model_provider=amazon-bedrock-runtime`, `agent_path=/root/p6_audit`. La navigation et les mesures DOM sont déterministes. L’observation est indépendante de l’implémentation, pas statistiquement indépendante de la famille de modèles.

Matériel : [dossier de défense](../defense/README.md), application et exports courants du même projet. Aucun fichier ni service de l’autre réalisation n’a été consulté.

## Observations qui doivent orienter le prototype

| Observation vérifiable | Effet sur l’expérience | Classement et réponse proposée |
|---|---|---|
| La première affirmation Robert est à **1115 px** du haut de page mobile, pour une hauteur d’écran de **844 px**. La bibliothèque, le titre, l’identifiant et les quatre cartes d’agents précèdent la réponse. | L’utilisateur doit parcourir le fonctionnement technique avant de comprendre ce qu’il apprend. | **Capacité présente, mal exposée.** Mettre la réponse et sa limite déterminante en premier ; rendre le travail des agents inspectable dans un panneau secondaire. |
| « Valeur liée » ouvre exactement `analysis@3`, `/options/1/metrics/turnover_cad/value`, `74400`. Le modal conserve le contexte visuel mais ne donne ni unité dans son contenu, ni signification du critère, ni calcul en langage courant. | La traçabilité existe ; sa compréhension exige de savoir lire JSON et les identifiants internes. | **Capacité présente, mal exposée.** Une fiche contextuelle « pourquoi ce montant » avec valeur/unité, entrées, méthode, portée, contrôle et lien brut. Le JSON reste accessible. |
| Les versions Robert montrent un vrai avant/après 40 000→74 400 CAD et les listes `analysis@2`, `research@1`, `baseline_stress@1`, etc. L’histoire 30→40→74,4 kCAD est répartie entre événements et pièces. | L’utilisateur peut auditer, mais doit recomposer la causalité entre correction, invalidation et résultat. | **Capacité opérationnelle à mieux traduire.** Une frise des changements humains, un delta chiffré et des groupes « conservé / réexaminé », avec références détaillées à la demande. L’ancienne analyse doit rester explicitement historique. |
| La synthèse Robert contient **7652 caractères**, celle d’Amira **9933**, avant les preuves séparées. Les limites de calcul sont répétées autour des options et des commentaires documentaires d’A1. | Les réserves sont conservées, mais leur répétition rend difficile l’identification de celles qui changent la décision. | **Capacité présente, mal exposée.** Séparer limite décisive visible, hypothèses de l’analyse et audit détaillé. Ne jamais cacher « réserve abstraite » ou « rétrospectif, pas prévision » dans une vue simple. |
| Amira affiche réellement deux trajectoires CAD, deux allocations, rendements, replis et fenêtres historiques. Le cadre de droite indique simultanément « horizon 15 ans ». Le texte explique que cet horizon n’est pas prédit. | Les données se prêtent à une comparaison visuelle utile, mais l’utilisateur doit faire lui-même le rapprochement entre horizon souhaité et fenêtre observée. | **Capacité opérationnelle.** Intituler le graphique « Ce que l’on observe sur 2021–2026 » et afficher près de lui « votre horizon de 15 ans n’est pas simulé ». Conserver les conventions CAD et achat-conservation. |
| La demande incomplète affiche une échéance de 12 mois, capital/retrait inconnus et aucune allocation. La synthèse dit « La réponse reste à établir ». Les questions précises sont réparties dans le panneau de droite et la longue vue de qualification. | L’abstention est correcte ; l’action suivante est moins immédiate que le diagnostic d’absence. | **Capacité opérationnelle à mieux guider.** Montrer d’abord ce qui est compris, les champs inconnus déterminants et pourquoi leur réponse est nécessaire. Une séquence de clarification adaptative reste une **interaction nouvelle**, non une capacité déjà démontrée. |
| Le cas impossible donne 120 000−100 000=20 000 CAD et ne présente aucune option. Il conserve les limites : réserve abstraite, pas d’apport, aucun IIS global, aucune relaxation automatique. | C’est une réponse utile, mais l’étape suivante ressemble encore au formulaire générique de révision. | **Capacité opérationnelle.** Mettre en évidence les deux valeurs incompatibles et permettre de les corriger. Une réparation préférée, un apport supposé ou une nouvelle allocation seraient **exploratoires** sans calcul et choix explicites. |
| Les formulaires distinguent déjà « Modifier la demande active » et « Explorer une variante séparée ». En revanche, le seul champ financier rapide est le retrait ; les autres changements passent par texte libre. L’annulation avant envoi ou le retour à une ancienne analyse comme vue de référence ne forment pas encore un parcours explicite. | Le contrat de variante existe mais reste difficile à anticiper : que va-t-on modifier, conserver et recalculer ? | **Capacité partielle / interaction nouvelle.** Éditeur de copie avec champs sourcés, récapitulatif avant envoi, annulation sans effet et comparaison fixe avec le dossier de départ. Ne pas appeler cette copie une nouvelle version validée avant passage du processus réel. |
| Les contrôles de calcul, de fidélité, d’ancrage et de validité externe sont séparés. L’interface emploie encore `historical policy`, `baseline branch consistency`, « Admissible » et « Suffisant » avec une portée détaillée plus bas. | La distinction scientifique est solide, mais les libellés peuvent être pris pour une approbation financière globale. | **Capacité présente, mal exposée.** Libellés orientés question : « Les contraintes de ce modèle sont respectées », « Les nombres correspondent au registre », « Applicabilité à un placement réel non établie ». Garder le détail et l’auteur de chaque contrôle. |
| La règle simple qui atteint également le minimum de Robert30 figure dans la défense, mais pas dans la synthèse de Robert observée. L’interface n’établit aucun gain marginal des quatre agents. | Un nouveau comparateur pourrait involontairement faire paraître l’optimiseur supérieur à une référence absente. | **Donnée de défense à exposer avec provenance.** Montrer la référence simple au seul état où sa comparaison a été vérifiée ; ne pas l’étendre automatiquement aux révisions ou à Amira. |

## Acquis à préserver

- Les quatre parcours s’ouvrent ; aucun `pageerror` observé.
- Aucun débordement horizontal de page à 390 px dans ces quatre états.
- Un inspecteur s’ouvre au clavier, place le focus dans le dialogue et restitue le focus au bouton déclencheur après Échap.
- Les inconnues, l’infaisabilité, les limites des méthodes, les pièces réutilisées et la distinction entre affichage et accord sont réellement représentées.
- Les courbes d’Amira correspondent à des résultats historiques existants ; aucun tracé de rendement futur n’est nécessaire au prototype.

## Ce que cet audit ne prouve pas

Ce relevé n’est ni un test utilisateur ni un audit WCAG complet. Il n’établit pas la compréhension d’un novice, la qualité de la navigation au lecteur d’écran, ni le succès de modifications nouvelles. Les flux financiers n’ont pas été relancés pendant cette observation ; leurs comportements sont attestés dans la défense. Le prototype doit être évalué séparément sur les tâches essentielles et rester clairement distinct du produit avant validation.

## Preuves et reproduction

- [Script de parcours](proofs/audit/inspect_current.cjs)
- [Textes réellement rendus et mesures](proofs/audit/current_ui.json)
- [Contrôle clavier ponctuel](proofs/audit/keyboard_current.json)
- [Robert bureau](proofs/audit/robert-desktop.png), [mobile](proofs/audit/robert-mobile.png), [preuve](proofs/audit/robert-proof.png), [versions](proofs/audit/robert-history.png)
- [Amira bureau](proofs/audit/amira-desktop.png), [incomplet](proofs/audit/incomplete-desktop.png), [impossible](proofs/audit/impossible-desktop.png)

```bash
node docs/experience/proofs/audit/inspect_current.cjs
```
