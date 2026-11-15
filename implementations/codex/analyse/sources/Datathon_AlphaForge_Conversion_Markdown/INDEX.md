# INDEX : conversion PDF et PPTX vers Markdown (Datathon 2026, AlphaForge AI)

Deux documents convertis, soit 31 pages et diapositives au total. Pour chaque document il y a deux fichiers Markdown : la version principale (avec fac-similé de chaque page ou diapositive en image) et la version `_AI_upload_ready` (sans aucune dépendance aux images, à téléverser seule dans une IA).

| # | Fichier source | Pages ou diapositives | Markdown principal | Version autonome | Images |
|---|---|---|---|---|---|
| 1 | Datathon_Case_Officiel_2026_FR.pdf (« Datathon - Case Officiel 2026 FR », Canva, A4) | 19 | Datathon_Case_Officiel_2026_FR.md | Datathon_Case_Officiel_2026_FR_AI_upload_ready.md | assets/Datathon_Case_Officiel_2026_FR/page-001.png à page-019.png |
| 2 | Presentation_AlphaForge_AI_Participants.pptx (16:9) | 12 | Presentation_AlphaForge_AI_Participants.md | Presentation_AlphaForge_AI_Participants_AI_upload_ready.md | assets/Presentation_AlphaForge_AI_Participants/page-001.png à page-012.png |

## Contenu

- **Énoncé du défi (PDF)** : couverture, sommaire, 1. Challenge (contexte, description, trois personas Amira, Mateo et Robert, démarche proposée, conseils, pistes d'agents), 2. Données (exemples d'actifs, familles de données, structure du jeu de données de départ, sources publiques, période et règles d'utilisation), 3. Livrables attendus (prototype et code, vidéo, documentation technique, one pager), 4. Appréciation générale (encadrement responsable, performance historique et risque), annexe 01 (grille d'évaluation simplifiée).
- **Présentation pour les participants (PPTX)** : douze diapositives qui reprennent le défi : pourquoi ce défi, le challenge, les trois personas, ce que signifie « agentique », le terrain de jeu des données, l'exigence AWS (condition d'admissibilité), la méthode en cinq décisions, les quatre livrables, la grille d'évaluation, le cadre responsable et la diapositive de clôture. Les notes du présentateur (références de sources) sont reproduites.

## Méthode

- Le PDF a été rendu en PNG (110 dpi) et la présentation en PNG (80 dpi, via une conversion PDF). Le texte natif a servi de base (couche de texte du PDF, texte des zones de texte du PPTX) ; chaque page a été vérifiée contre son rendu.
- Dans le PDF, les deux tableaux des pages 10 (classes d'actifs et symboles) et 19 (grille d'évaluation) sont des images : ils sont absents de la couche de texte et ont été transcrits à partir du rendu de la page. Les autres tableaux (page 11) viennent de la couche de texte.
- Les éléments visuels (cartes, encadrés, motifs décoratifs, photo de la diapositive 1) sont décrits objectivement dans « Éléments visuels / structure ».
- Aucune correction silencieuse du contenu : le texte et ses coquilles sont conservés.

## Observations sur les documents sources (conservées telles quelles)

- Coquilles du PPTX : « SIGNaux » et « Cn'est donc pas » (diapositive 6), double point final après « ses choix » (diapositive 4).
- PDF, pages 10 et 12 : la page 12 décrit un jeu de départ de 31 actifs (10 actions canadiennes, 10 américaines, 9 FNB, Bitcoin et Ether), alors que le tableau indicatif de la page 10 énumère davantage de symboles (12 actions canadiennes, 12 américaines, 9 FNB d'actions, 6 FNB obligataires, 2 FNB liés à l'or, 2 cryptoactifs). Le texte précise que le tableau est purement indicatif.
- Les poids de la grille d'évaluation (20, 20, 20, 10, 15 et 15 %) sont identiques dans le PDF (annexe 01) et dans la diapositive 10.
