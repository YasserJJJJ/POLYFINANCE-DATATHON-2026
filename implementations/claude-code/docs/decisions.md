# Journal des décisions

Format : problème → ce que la recherche établit → options → choix → preuve → limite → condition de réouverture. Les idées initiales du porteur (O01–O20) sont conservées dans `cadrage/01_VISION_INITIALE_PROFIL_ET_ARCHITECTURE_OUVERTE.md`.

## D1 — Direction du produit (provisoire, 2026-11-14)

**Problème.** Quelle décision l'outil éclaire-t-il ?

**Critères fixés avant le choix.** (1) couverture des six dimensions de la grille ; (2) données disponibles et réutilisables ; (3) vérifiabilité des affirmations ; (4) contraste visible entre au moins deux profils ; (5) différence avec un chatbot générique ; (6) risque de réalisation.

**Options comparées.**

| Option | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Réf. — LLM seul répondant à partir d'un résumé chiffré | faible (agentique, données) | ✓ | ✗ chiffres non contrôlés | faible | ✗ | faible |
| A — Dossier de décision vérifiable (enveloppe) | ✓ | ✓ prix seuls suffisent pour démarrer | ✓ registre + vérificateur | ✓ | ✓ | moyen |
| B — Diversification cachée | partielle | contributions au risque : ✓ (prix) ; transparence : SPY seulement vérifié (R02) | ✓ | Amira | ✓ | moyen |
| C — ESG sous incertitude | partielle | faits datés NBIM, 10-K, méthodologie FTSE ; aucune note réutilisable (R02) | ✓ trois états | Mateo | ✓ | élevé (curation manuelle) |
| D — Laboratoire d'allocation robuste | partielle | ✓ | ✓ numérique | faible seul | moyen | risque de fausse précision |

**Choix provisoire.** A comme produit : pour chaque demande, un dossier où chaque affirmation chiffrée provient d'un résultat d'outil identifié, porte un statut (mesuré, hypothèse, scénario, inconnu) et indique ce qui ferait changer la conclusion. Profondeur par B (contributions au risque, puis transparence SPY), puis C pour Mateo ; D seulement comme outil quand une allocation fictive est demandée, comparée à une référence simple sous les mêmes contraintes.

**Première tranche.** Robert (demande incohérente avec le profil) contre Amira (risque élevé, diversification) : contraste fort, données de prix suffisantes.

**Preuve qui favorise ce choix.** R04 : déléguer les chiffres à des outils et contrôler l'explication de façon déterministe est faisable et testable ; les cadres agentiques financiers publiés sont évalués sur le rendement, pas sur la fidélité des explications (différence défendable). R03 : les cadres d'adéquation séparent capacité de perte et tolérance, et demandent d'expliquer l'écart et de proposer une alternative face à une demande incohérente (cas Robert).

**Ce qui réfuterait ce choix.** (a) Sur des demandes variées, l'agent choisit les mêmes outils que le workflow fixe : l'agent est décoratif, on garde le workflow et on le dit. (b) Les explications de l'agent échouent trop souvent au vérificateur malgré les gabarits : revoir la répartition entre code et modèle. (c) Les deux profils produisent des dossiers peu différents.

**Résultat de l'essai sur le critère (a), 2026-11-15.** Tableau reproductible : `docs/comparaison-agent-workflow.md`, produit par `scripts/comparer_agent_workflow.py` à partir des dossiers enregistrés. Sur les deux scénarios de démonstration, où le portefeuille, les parts, le seuil et le panier sont fournis, l'agent suit le workflow fixe à quelques appels près : sur ces demandes, le critère (a) se vérifie et l'agent n'apporte pas de choix d'outils propre. Sur quatre demandes libres, l'agent compose un parcours différent pour chacune, qu'aucun workflow fixe ne couvre : comparaison de trois actifs sans portefeuille ; ajout d'or avec des hypothèses posées par l'agent et déclarées comme telles ; préférence ESG sans donnée ESG au registre (l'agent compare les prix et écrit que les controverses ne sont pas mesurées) ; titre absent de l'univers (erreur d'outil rapportée, aucune valeur inventée).

**Conséquence.** Les deux modes restent, étiquetés dans chaque dossier : workflow fixe pour les scénarios connus (instantané, sans jeton, référence et repli sans AWS) ; agent pour les demandes ouvertes, où il est nécessaire. Critère (b) : sur ces exécutions, le vérificateur a demandé au plus une correction par dossier et aucun dossier n'a été accepté en échec. Critère (c) : non réexaminé. **Limite :** un dossier par demande, un seul modèle (Sonnet 5.5) ; la variabilité d'une exécution à l'autre n'est pas mesurée.

## D2 — Chemin AWS (provisoire, 2026-11-14)

**Choix.** Boucle Bedrock Converse avec outils exécutés dans notre code (R01, option a). Modèle configurable (`global.anthropic.claude-sonnet-5-5` par défaut ; `ca.anthropic.claude-haiku-5-5` pour un routage limité au Canada). Preuve d'intégration : `RequestId` de chaque appel dans le dossier ; journal d'invocation ; dossier écrit dans S3 versionné.

**Mise à jour du 2026-11-15.** Accès fourni par le datathon via Workshop Studio, région us-east-1 (réponse du porteur). Région par défaut de l'agent : us-east-1 ; profil AWS nommé `alphaforge` ; configuration par `scripts/configurer-aws-workshop.sh` (saisie sans écho). AWS CLI 2.40.3 installée avec l'accord du porteur.

**Limite.** Identifiants à saisir par le porteur ; ils sont temporaires. Toute ressource (journal, compartiment S3) se crée dans le compte du porteur, avec son accord. En attendant, l'agent tourne en mode local étiqueté « sans AWS ».

**Réouverture.** Si le compte n'a pas accès aux modèles 5.5, ou si AgentCore apporte une contribution observable supérieure pour un coût acceptable.

## D3 — Conventions de calcul (provisoire, 2026-11-14)

Devise de base CAD (hypothèse modifiable) ; valeur quotidienne de chaque actif sur son propre calendrier, convertie avec le dernier taux Banque du Canada connu à la date (fraîcheur enregistrée) ; comparaisons entre actifs et portefeuilles sur rendements hebdomadaires (dernière observation de chaque semaine se terminant le vendredi) pour neutraliser les jours fériés TSX/US et la cotation 7 j/7 des cryptos ; volatilité annualisée ×√52 ; portefeuille rééquilibré chaque semaine (hypothèse) ; perte maximale d'un actif sur série quotidienne, d'un portefeuille sur série hebdomadaire (sous-estime légèrement les creux intrasemaine, documenté).

## D4 — Mode de conservation des données du compte AWS (2026-11-15)

**Problème.** Claude Fable 5.2, le modèle le plus capable du compte, est refusé par Bedrock (« data retention mode 'default' is not available for this model »).

**Ce que la documentation établit.** Fable 5, 5.1 et 5.2 exigent le mode de compte `aws_review` (ou l'ancien `provider_data_share`) ; avec ce mode, les entrées et sorties de ces modèles sont conservées jusqu'à 30 jours dans AWS et peuvent être relues par AWS ; elles ne sont pas transmises au fournisseur du modèle ([Bedrock, data retention](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)). Le réglage est par région ; il ne déclenche pas de relecture pour les modèles qui ne l'exigent pas.

**Choix.** Mode du compte passé de `inherit` à `aws_review` en us-east-1, le 2026-11-15 à 11 h 37 UTC, avec l'accord du porteur (« fable 5.2 si pas trop compliqué a seté up et facile et realisable, opus 5.5 sinon absolument pas grave ! »), après exposé des conséquences. Appel de contrôle Fable 5.2 réussi (coût estimé 0,15 USD, dont la mise en cache initiale du contexte de Claude Code).

**Réversibilité.** `put_account_data_retention(mode='inherit')` en us-east-1 rétablit l'état antérieur ; Fable redevient alors indisponible.

**Réouverture.** Si les organisateurs du datathon s'y opposent, si le budget du compte se resserre (Fable est plus cher qu'Opus), ou si le contenu traité devenait sensible.

## D5 — Contrôle du sens et présentation choisie par l'agent (provisoire, 2026-11-15)

**Problème.** La règle « aucun chiffre ni sens de comparaison écrit à la main » n'était contrôlée que pour les chiffres. À la relecture des dossiers de l'agent, des défauts passaient le vérificateur : comparatifs manuscrits (« dépasse le plafond », « plus élevé », « monte à »), grandeur en lettres (« dix pour cent »), fautes d'accord autour des comparaisons calculées (« supérieure à le plafond », « un rendement inférieure »). Par ailleurs, les dossiers de l'agent n'avaient ni chiffres clés, ni tableau, ni graphique, contrairement à ceux du workflow fixe.

**Options.** (1) Consignes seules dans le prompt : déjà en place, insuffisant (défauts observés). (2) Garde lexicale déterministe dans le vérificateur et accord fait par le code. (3) Relecture par un second modèle : couvre le sens, mais non déterministe, non testable par fautes injectées, coût et latence en plus.

**Choix.** (2). Le vérificateur refuse les comparatifs manuscrits (hors sections « question » et « condition », qui formulent des hypothèses) et les grandeurs en lettres ; une troisième comparaison calculée, `{{cmpduree:…}}`, remplace le mot de liaison que le workflow choisissait dans le code ; le code accorde la comparaison avec les mots voisins sans jamais en changer le sens. L'agent choisit les chiffres clés, le tableau d'options et les séries du graphique ; le code trace à partir des données, et un élément invalide est écarté et signalé à l'agent. Les outils refusent les entrées invalides au lieu de renvoyer un résultat vide.

**Preuve.** Tests à fautes injectées (`tests/test_evidence.py`, `tests/test_agent.py`, `tests/test_workflow.py`). Le dossier `robert-libre-or`, revérifié hors ligne avec le contrôle renforcé, a été refusé pour « dix pour cent » ; rejoué, il est conforme. Les huit dossiers enregistrés passent le contrôle courant (`alphaforge rendre`).

**Limite.** Contrôle lexical, liste fermée : superlatifs, verbes de variation hors liste (« réduit », « ramène »), connaissances tirées de la mémoire du modèle et interprétations ne sont pas détectés (`docs/technique.md`, section 3). L'accord en genre est une heuristique (féminin par défaut).

**Réouverture.** Si la garde provoque des refus répétés sur des tournures légitimes (plus de deux corrections par dossier), ou si la relecture montre des erreurs de sens fréquentes malgré elle : passer à l'option (3) en complément.

## Rectifications du 15 novembre (audit de refonte)

Relevées par l'audit en lecture seule mené à la demande du porteur (`docs/refonte/diagnostic-et-contrat.md`). Aucune décision nouvelle n'est consignée ici : la refonte proposée attend sa validation.

- **D1, critère (b).** La phrase « le vérificateur a demandé au plus une correction par dossier » est exacte et trompeuse : cinq premiers jets sur six ont été refusés une fois. Le critère (« échouent trop souvent ») n'a pas de seuil ; il ne peut pas être dit satisfait.
- **D1, critère (a).** Sur les demandes libres, aucun workflow fixe n'existe : la différence est acquise par construction, elle ne mesure pas l'apport de l'agent. La section « Lecture » de `docs/comparaison-agent-workflow.md` est écrite en dur dans le script, pas déduite des dossiers. Sur les deux scénarios de démonstration, D1 prévoyait de dire que l'agent est décoratif ; cela n'a pas été fait dans le README ni dans l'application.
- **D1, critère (c).** L'expérience qui devait le trancher — la même demande traitée pour deux profils — n'a jamais été exécutée.
- **D5, réouverture.** La condition « plus de deux corrections par dossier » ne peut pas se produire : la boucle n'en demande jamais plus de deux (`MAX_FIXES = 2`). La garde lexicale refuse des tournures vraies et laisse passer des phrases fausses ; ses passes de correction pèsent environ un tiers des jetons des six dossiers de l'agent. « Contrôle du sens » était un nom trop large pour une liste de mots.
- **Décisions jamais consignées.** La disparition de la fonction de recherche, le remplacement des quatre rôles par un orchestrateur unique sans comparaison avec des spécialistes, et le fait de ne rendre au modèle que des identifiants et des valeurs formatées n'ont fait l'objet d'aucune entrée de ce journal.
- **D1, demandes libres.** La formule « un parcours différent pour chacune » était complaisante : trois des quatre demandes libres n'appellent que les métriques d'actifs, avec ou sans corrélation, sur d'autres symboles. La différence tient surtout aux arguments.
- **D1, critère (c), exécuté le 15 novembre.** La même demande et le même scénario sous trois profils donnent treize affirmations identiques sur quinze et les mêmes chiffres clés (`docs/refonte/calcul_exploratoire.py`, section 8) : le profil ne change pas l'analyse du workflow fixe.
- **D3.** La valorisation hebdomadaire est dite sous-estimer « légèrement » les creux : elle ôte 2,2 points à la pire baisse avec 10 % de Tesla (−15,3 % au lieu de −17,5 % en valorisation quotidienne) et fait passer la part maximale affichée de 6 % à 9 %. Le rééquilibrage hebdomadaire sans frais inverse le sens de l'effet de Tesla sur le rendement annualisé. Ces conventions ont été posées sans étude de sensibilité.
