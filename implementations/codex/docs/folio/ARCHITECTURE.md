# Architecture réalisée de Folio

```mermaid
flowchart TD
  U[Utilisateur : demande, profil, lecture] --> F[Folio : revue annotée]
  F -->|consulter ou exporter une version| P[Projection Folio en lecture seule]
  F -->|aperçu explicitement sans agents| C[Moteur déterministe existant]
  C -->|résultat et empreinte, hors dossier| F
  F -->|création, variante ou correction / clé idempotente| API[API Folio]
  API --> S[Service de décision existant]
  S --> A0[Agent 0 : qualification et clarifications]
  A0 --> A1[Agent 1 : sources et revue d'applicabilité]
  A1 --> A2[Agent 2 : analyse et contrôles]
  A2 --> A3[Agent 3 : restitution bornée aux preuves]
  A1 -->|preuve absente / contradiction| A0
  A2 -->|entrée ou hypothèse inadmissible| A0
  A3 -->|restitution invalide| A2
  A0 -->|information nécessaire| U
  A2 --> C
  A0 & A1 & A2 & A3 --> B[Bedrock : route AWS convenue]
  A0 & A1 & A2 & A3 --> D[(Dossier SQLite versionné)]
  D --- O[Artefacts immuables / sources / reçus AWS]
  D --- G[LangGraph : checkpoints et reprise]
  D --> P
  P -->|faits, résultats, limites, événements| F
  F -->|correction| API
  D --> I[Invalidation des dépendances / conservation des pièces valides]
  I --> S
```

L'aperçu local ne traverse pas les quatre agents et ne modifie pas le dossier. Les variantes et corrections traversent la chaîne réelle. Les préférences d'affichage ne quittent pas le contrôleur de présentation. Une version ancienne est une archive, avec sa date et sa portée ; l'historique ne représente pas une suite d'opérations de marché.
