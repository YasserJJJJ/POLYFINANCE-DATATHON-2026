# AlphaForge — comprendre avant de décider

**Un laboratoire de décisions financières fictives qui relie une demande,
un changement d’exposition et ses conséquences calculées.**

Une réponse financière convaincante peut masquer des hypothèses implicites,
des chiffres non vérifiés ou des contradictions entre le besoin de l’investisseur
et ses placements. AlphaForge rend ces éléments discutables et vérifiables.

L’utilisateur choisit un profil, édite les avoirs fictifs et formule sa demande.
Il compare l’allocation de référence à une modification explicite. L’interface
montre le parcours de valeur, la baisse maximale et des épisodes historiques,
avec accès aux sources et aux actions exécutées.

Le moteur Python effectue les calculs en CAD sur un instantané de 31 actifs.
L’agent Amazon Bedrock choisit des outils de comparaison, de lecture documentaire
et d’examen du profil. Il sélectionne des observations calculées et explique
les compromis. Les chiffres, leur provenance et les identifiants des appels AWS
restent consultables dans un rapport exportable.

Trois exemples montrent des décisions différentes. Robert explore une réduction
de Tesla à l’approche de son horizon de retrait. Amira examine sa concentration
en technologies et crypto, sans confondre nombre de titres et diversification.
Mateo retire Exxon directement ; sur l’historique fourni, ce changement augmente
la baisse maximale. Sa préférence ESG ne devient donc pas une promesse de risque
plus faible, et l’absence de composition des FNB reste visible.

Le calcul utilise les prix ajustés, une convention explicite de conversion
CAD et un calendrier commun. Les essais vérifient les équations, les profils,
les contraintes, les sources, les échecs d’outils et l’expiration AWS. Une revue
indépendante a corrigé la propagation des paramètres de persona et renforcé
la cohérence du résultat après échec de l’agent.

La solution est démontrable sur Mac. L’inférence passe par le compte AWS de
l’atelier ; le code, les données de travail et les résultats restent conservés
localement. Il s’agit d’un rejeu historique, sans prévision de rendement,
certification ESG, optimisation revendiquée ou transmission d’ordres.

**Apport central :** chaque conclusion reste reliée à une hypothèse modifiable,
une conséquence calculée et une preuve que l’utilisateur peut examiner.
