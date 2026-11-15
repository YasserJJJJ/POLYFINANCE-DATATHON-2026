# Revue indépendante de Folio intégré

Statut au 2026-11-15 : revue de Folio intégré effectuée sur le service local
`127.0.0.1:8768`, version 0.7.0. Études, corrections, variante, calculs,
navigation et exports ont été confrontés à leurs données effectives.

À essayer :

- [Robert initial, r5](http://127.0.0.1:8768/?dossier=71c8fb4b9d5e45fe98a4b4942e07c41e&revision=5&view=overview) : la référence simple atteint aussi 30 000 CAD.
- [Robert corrigé, r20](http://127.0.0.1:8768/?dossier=71c8fb4b9d5e45fe98a4b4942e07c41e&view=overview) : retrait 40 000 CAD, perte admise 1 000 CAD par choc, minimum calculé 74 400 CAD.
- [Amira, comparaison initiale](http://127.0.0.1:8768/?dossier=49ed5ae5903f41c297909b644ff7599a&view=compare).
- [Variante Amira, exposition directe TSLA 5 %](http://127.0.0.1:8768/?dossier=4a654c3cd06646c5a7765ff58820633d&view=compare).

## Indépendance et périmètre

Le relecteur `/root/p6_audit` n’a écrit ni la direction Folio, ni ses composants
intégrés, ni le moteur financier. Il a produit une autre direction visuelle,
Prisme, et examiné les prototypes antérieurs. Le mandat consiste à confronter
l’interface au dossier réel, sans adopter le récit de l’intégrateur.

Seul le dépôt AlphaForge courant et son service local `127.0.0.1:8768` sont
consultés. Les sessions et dossiers préexistants sont conservés. Les deux
nouvelles études destinées à cette revue sont nommées dans
[live_cases.json](proofs/live_cases.json).

## Route et accès effectifs

[Préflight conservé](proofs/aws_preflight.json) :

- Session du relecteur : `amazon-bedrock-runtime`.
- Santé du service : application `alphaforge`, chemin du dépôt attendu.
- STS : profil `alphaforge`, compte attendu, rôle `WSParticipantRole`.
- Point d’entrée explicite : `bedrock-runtime.us-east-1.amazonaws.com`.
- Profil `global.openai.gpt-6-astra` : `ACTIVE`, obtenu par `GetInferenceProfile`.

STS et le profil actif n’attestent pas seuls le droit d’inférence. Chaque reçu
`bedrock.converse` des études est examiné séparément, avec son identifiant
AWS, son rôle, le fournisseur, le modèle et son statut.
Le profil global ne constitue pas une promesse de résidence canadienne.

## Scénarios réels lancés

| Cas | Entrée | API et stockage | État |
|---|---|---|---|
| Robert | Exemple exact de l’API : capital 100 000 CAD, retrait 30 000 à 12 mois, perte par choc 15 000, TSLA ≤10 %, réserve abstraite. | POST `/api/dossiers`, `use_ai:true`; dossier `71c8fb4b9d5e45fe98a4b4942e07c41e`. | `complete`, révision 5, minimum conditionnel 30 000 CAD. |
| Amira | Exemple exact : SPY/XIU/TSLA, capital 25 000 CAD, cible TSLA 10 %. Redistribution proportionnelle et fenêtre commune disponible explicitement déclarées dans `historical_policy`. | POST `/api/dossiers`, `use_ai:true`; dossier `49ed5ae5903f41c297909b644ff7599a`. | `complete`, révision 5 ; valeurs finales 44 515,75 et 46 874,02 CAD. |

Le script [run_live_cases.py](proofs/run_live_cases.py) refuse de recréer les
études si leurs identifiants ont déjà été consignés. Il ne réessaie jamais
automatiquement un POST dont l’issue serait ambiguë.

### Ce qui a réellement été vérifié

[audit_live_cases.py](proofs/audit_live_cases.py) confronte les instantanés
capturés par l’API aux artefacts et aux fichiers bruts, sans appeler les modules
de calcul du produit. [Rapport complet](proofs/audit_live_cases.json).

| Point | Observation vérifiée | Portée |
|---|---|---|
| Inférences | Quatre `bedrock.converse` complets par dossier, chacun avec un rôle et un `request_id` distincts ; fournisseur, compte, région d’entrée et modèle attendus. | Huit inférences du produit prouvées ; la recherche et les calculs locaux sont comptés séparément. |
| Agent0 | Écrit `problem@1`, `qualification@1`, `questions.agent0@1`. Les exemples étant déjà complets, aucune mise à jour inventée ; interprétation et distinction du périmètre consignées. | Contribution réelle de qualification, pas preuve d’utilité marginale sur une entrée déjà structurée. |
| Agent1 | Écrit recherche et revue ; Amira inclut `data_inspection@1`. Sélection de trois preuves pour Robert et cinq pour Amira. Désaccords et lacunes conservés. | Méthodes et conventions bornées par des passages ciblés, pas validation intégrale de chaque article. |
| Agent2 | Route Robert vers `reserve_allocation`, Amira vers `historical_comparison`. Écrit analyse, contrôles, questions ; Robert crée aussi `baseline_stress@1`. | Les nombres viennent du calcul déterministe. Son reçu indique zéro inférence dans le calcul. |
| Agent3 | Écrit `view@1`, choisit les identifiants de claims, leur ordre et l’accent sur les conditions. | Aucun nouveau montant ou rendement créé par le rédacteur. |
| Intégrité | Hashes de 32 artefacts Robert et 33 artefacts Amira concordants ; empreintes des captures et textes documentaires contrôlées. | Intégrité des octets, pas preuve de vérité économique d’une source. |
| Robert | Demi-L1 et pertes sous les deux chocs recalculées indépendamment pour chaque option. La borne nécessaire d’achat de réserve de 30 000 CAD est atteinte. | Périmètre abstrait, sans frais et sans garantie future. |
| Amira | Prix ajustés de début/fin et FX relus en CSV standard : valeurs finales retrouvées à l’arrondi cent près. Fenêtre du 2021-11-12 au 2026-11-12 ; 15 ans n’est pas projeté. | Vérification des valeurs finales ; pas nouvelle validation exhaustive des volatilités et drawdowns. |
| Archives, revue de code exécutée | `at_revision` sur les deux études : 0/1/2/3/4 reçus AWS respectivement en r1/r2/r3/r4/r5 ; pas d’analyse avant r4 ni de vue avant r5. | Premier contrôle direct de projection ; parcours HTTP et navigateur encore à exécuter. |

Deux limites documentaires importantes restent visibles : Robert ne qualifie pas
un instrument réel de réserve ; la réduction du poids **direct** de TSLA d’Amira
ne mesure pas l’exposition Tesla contenue dans les FNB. Les résultats divergents
de la littérature sur l’optimisation n’établissent pas une supériorité universelle.

## Protocole ciblé d’intégration

Les preuves doivent comprendre observations de navigateur, requêtes réseau et
instantanés d’API. Une animation ou un message d’interface ne remplace pas une
preuve de calcul ou de mutation.

| Test | Observation vérifiable demandée | Défaut recherché / impact |
|---|---|---|
| Rechargement | Ouvrir une étude réelle, recharger, retrouver le même dossier/révision et les mêmes montants. Aucun POST lors de la lecture. | Un résultat en mémoire peut disparaître ou déclencher silencieusement une nouvelle étude. |
| Double lancement / reprise réseau | Deux activations ou reprise du même `request_id` retournent le même dossier et le même run. Un corps différent avec la même clé doit produire 409. | Doublons, coûts d’inférence supplémentaires ou confusion de résultats. Vérifier l’état serveur, pas seulement un bouton désactivé. |
| Preuve contextuelle | Cliquer un montant depuis Robert puis Amira ; titre, valeur, unités, méthode et pointeur correspondent au dossier consulté. Focus dans le dialogue, Escape, retour au déclencheur. | Mélange de preuves d’archive et de résultat courant ; perte du contexte ou piège clavier. |
| Aperçu 30→40 kCAD | Calcul explicite sans agent ni mutation du dossier principal ; résultat et limites correspondent à l’aperçu. Annulation remet l’état précédent. | Scénario pris pour une correction persistante, ancien chiffre affiché comme neuf. |
| Correction persistante | Corriger le retrait et attendre la vraie chaîne ; comparer versions, artefacts invalidés et réutilisés. | Écrasement de l’histoire, réutilisation d’un calcul périmé, progression fictive. |
| Historique / export | Ouvrir une révision antérieure, identifier son statut historique ; export = version regardée ; événements postérieurs absents. | L’historique raconte l’état actuel ou exporte silencieusement une autre version. |
| Adaptation de lecture | Même étude en accessible/profond : chiffres, hypothèses et limites inchangés ; aucun appel de calcul ou d’inférence. | La simplicité retire une limite ou modifie la conclusion. |
| Information manquante et impossibilité | Aucune allocation inventée ; questions ou certificat borné ; saisie préservée après échec ; moyen de reprendre. | Un écran vide ou un ancien résultat ressemble à une réponse valide. |
| Mobile et clavier | Tâches principales à 390 et 320 px, focus visible, dialogue et tableau accessibles, pas de débordement de page. | Information ou commande essentielle inaccessible. Axe est un complément, pas une certification complète. |

Le nombre d’études et de reprises doit rester proportionné. Un échec démontré
sera transmis avec **observation → impact → correction possible**, puis seul le
comportement concerné sera rejoué après correction.

## Résultats, corrections et limites

### Défauts établis et corrections

| Réf. | Observation vérifiable | Impact | Correction et vérification |
|---|---|---|---|
| F01 · P1 | L’export JSON courant appelait `/export` sans révision, alors que le HTML utilisait `v.revision`. Une autre session pouvait faire avancer le dossier entre affichage et export. | Export d’une version différente de celle examinée. | Corrigé : révision épinglée. Export r5 vérifié, événements ultérieurs absents ; [preuve](proofs/browser-history.json). |
| F02 · P1 | Un aperçu d’archive utilisait la révision historique au calcul mais sauvegardait la révision courante comme `baseRevision`. | Un scénario d’archive pouvait devenir, après rechargement, un aperçu prétendument courant. | Corrigé : base, bail courant et archive sont séparés. Aperçu de r5 puis retour courant/rechargement vérifiés ; [preuve](proofs/browser-history.json). |
| F03 · P2 | Le succès d’un POST effaçait le brouillon sans vérifier les saisies postérieures à son envoi. | Une information saisie pendant la transmission pouvait disparaître. | Corrigé : effacement conditionnel au brouillon envoyé. Corps 40k, nouvelle saisie 45k : résultat 40k et brouillon 45k distincts ; [latence contrôlée](proofs/browser-latency.json). |
| F04 · P2 | L’aperçu incomplet contenait `version.questions`, tandis que le rendu cherchait ailleurs et affichait « aucune question structurée ». | Une information nécessaire était détectée mais non présentée. | Corrigé. Retrait vide : question réelle et champ concerné visibles, zéro allocation ; [preuve](proofs/browser-missing.json). |
| F05 · P2 | Le formulaire « Retrouver un dossier » utilisait le gestionnaire de recherche des preuves. | La recherche de bibliothèque ouvrait un dialogue hors contexte. | Corrigé : recherche des dossiers séparée. Contrôle ciblé dans `browser-final.json`. |
| F06 · P2 | Le delta des corrections persistantes affichait « Version précédente » au lieu de lire les anciennes valeurs conservées. | Les vrais changements étaient moins intelligibles que les aperçus. | Corrigé : chargement de la projection précédente ; retrait, perte et minimum avant/après visibles. Les identifiants techniques sont maintenant en détails. |
| F07 · P2 | À 320 px, `.revision-delta` défilait sans être focalisable ; axe signalait `scrollable-region-focusable`. | Le contenu horizontal pouvait être inaccessible au clavier. | Corrigé : région nommée et focalisable. Nouvelle exécution : zéro violation axe à 320 et 390 px sur les vues contrôlées ; [résultat](proofs/browser-mobile.json). |
| F08 · P1 | Le JSON exporté passait par `JSON.parse` puis `JSON.stringify` : `100000.0` devenait `100000`. Le hash de `problem@1` passait de `515474…` à `979819…`. | Valeurs financières inchangées, mais intégrité documentaire non reproductible. | Corrigé : octets HTTP bruts. Export r5 : 411 125 octets identiques au serveur, 32 hashes vérifiés en Python. Aperçu : octets et hashes du calcul/entrées vérifiés avant/après reload ; [dossier](proofs/browser-export.json), [aperçu](proofs/browser-previewexport.json). |
| F09 · P2 | La variante Amira affichait « La correction conserve l’historique du dossier ». | Confusion entre un dossier distinct et une correction du parent. | Corrigé : « Variante dans un dossier distinct ; le parent est conservé ». La provenance héritée est distincte des résultats de la nouvelle étude. |

F01–F03 ont d’abord été établis par inspection, puis leurs corrections ont été
testées sur le navigateur. F04, F06–F08 ont été observés sur le rendu ou les
fichiers réellement téléchargés. Le fichier
[export avant correction](proofs/folio-export-r5-before-fix.json) conserve la
preuve de F08 ; il ne doit pas être utilisé comme export fiable.

### Exécutions et contrôles ciblés

| Parcours | Observation vérifiée | Preuve |
|---|---|---|
| Lecture Robert/Amira | Reload sans POST ; mêmes analyses serveur et mêmes limites dans les deux niveaux. Le focus entre dans la preuve, Escape le rend au déclencheur. | [browser-read.json](proofs/browser-read.json) |
| Aperçu | 40k → résultat 40k ; zéro appel d’agent et zéro mutation ; annulation. Retrait absent → incomplet ; retrait 120k → conflit de 20k, aucune allocation/minimum. | [browser-preview.json](proofs/browser-preview.json) |
| Réponse tardive | Un aperçu Robert retardé ne remplace pas Amira après navigation. Une erreur réseau préserve la saisie et permet une nouvelle tentative. | [browser-latency.json](proofs/browser-latency.json) |
| Corrections réelles | r5 : retrait30k/perte15k/min30k ; r10 : retrait40k/perte15k/min40k ; r20 : retrait40k/perte1k/min74,4k. Quatre nouveaux reçus AWS par correction. | [audit_revisions.json](proofs/audit_revisions.json) |
| Idempotence | Même clé et même corps → même dossier/run ; même clé et corps divergent → 409. Nombre de runs augmenté d’un seul. | `browser-revision40.json`, `browser-revisionloss1000.json` |
| Réutilisation | `research@1` et `baseline_stress@1` restent utilisables ; calcul, contrôle et restitution précédents sont invalidés. Demi-L1 et pertes de chaque option recalculées indépendamment ; contraintes des options admissibles revérifiées. | [audit_revisions.py](proofs/audit_revisions.py) |
| Variante Amira | Nouveau dossier lié à r5 du parent, exposition directe TSLA 5 %. Parent strictement inchangé ; quatre appels réels ; origine/hashes des faits hérités conservés. Valeur finale recoupée depuis CSV : 47 660,11 CAD. | [audit_variant.json](proofs/audit_variant.json), [browser-variant.json](proofs/browser-variant.json) |
| Mobile/clavier | Pas de débordement global sur les vues examinées en 320/390 px ; régions défilantes nommées ; zéro violation axe après correction. | [browser-mobile.json](proofs/browser-mobile.json) |
| Intégrité des exports | Version affichée épinglée, octets du serveur conservés, hashes d’artefacts et du calcul d’aperçu vérifiables après téléchargement. | [browser-export.json](proofs/browser-export.json), [browser-previewexport.json](proofs/browser-previewexport.json) |

**Erreur du scénario de revue conservée.** Le relecteur a saisi par erreur un
retrait de 1 000 CAD en r15, au lieu d’une perte admise de 1 000 CAD. Le système
a correctement calculé 15 000 CAD de capital déplacé pour ces entrées. Cette
révision reste visible ; r20 corrige explicitement retrait = 40 000 CAD et
perte admise = 1 000 CAD. Ce n’est pas un défaut du moteur. Le mode de test ayant
produit cette mauvaise saisie est désactivé pour ne pas la répéter.

Le manifeste contient **24 appels AWS complets de cette revue** : huit pour les
deux études initiales, douze pour les trois corrections Robert dont l’erreur
de saisie, quatre pour la variante Amira. Les aperçus, essais réseau, captures,
recalculs Python et axe n’appellent aucun modèle. Les études indépendantes
supplémentaires de l’intégrateur ne sont pas incluses dans ce total.

Les fichiers `robert-r10.json`, `robert-r15.json`, `robert-r20.json` sont des
captures de projection normalisées par JavaScript. Pour vérifier les empreintes,
utiliser leurs homologues `*-source.json`, capturés sans transformation depuis
HTTP. Cette distinction résulte du défaut F08 et évite de masquer la différence
entre égalité numérique et conservation des octets.

### Limites restantes

- L’essai humain reste nécessaire pour juger compréhension, orientation et
  qualité de décision. Axe et les scénarios de clavier ne certifient pas toute
  l’accessibilité ; aucun essai avec lecteur d’écran n’a été mené ici.
- Les quatre agents produisent des transformations distinctes, mais leur valeur
  marginale face à une référence sans LLM n’est pas démontrée par ces parcours.
  La référence simple atteint aussi le minimum initial de Robert.
- Robert conserve un modèle conditionnel sans frais, fiscalité ni instrument
  réel de réserve. Les chocs ne bornent pas les pertes futures. La vérification
  indépendante a recalculé admissibilité et arithmétique ; elle n’est pas une
  seconde résolution indépendante du programme linéaire de r20.
- Amira reste une comparaison historique sur une capture de 2026. Ses quinze
  ans d’horizon ne sont pas projetés. Les positions internes des FNB et
  l’exposition totale à Tesla ne sont pas établies.
- Les questions d’aperçu sont volontairement factuelles et parfois génériques
  (« valeur nécessaire absente ») ; le champ et son rôle dans le calcul
  fournissent le contexte. Leur utilité pédagogique mérite un essai humain.

Reprise : ouvrir les liens en tête, consulter
[live_cases.json](proofs/live_cases.json), puis utiliser
`FOLIO_REVIEW_MODE=read|history|mobile|latency|missing|export|previewexport`
avec [tests/folio_review.cjs](../../tests/folio_review.cjs), un mode par commande.
Les modes de mutation ne doivent pas être relancés pour une simple revue :
leurs requêtes acceptées, états et reçus sont déjà conservés.
