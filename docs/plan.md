# Plan d'attaque

Synthèse des 4 visions de l'équipe (questionnaire de cadrage du 14 nov.). Version complète avec schémas :
artifact « Plan d'attaque AlphaForge » partagé par Yahia.

## Ce qui est décidé

- On sert **l'investisseur lui-même** ; la fiche pour son conseiller est un bonus.
- **Clarifier, puis confronter** : reformulation rapide, puis verdict chiffré.
- **Entrée** : phrase libre + champs pré-remplis corrigeables (« Voici ce que j'ai compris de toi »).
- **Profil** : des curseurs, jamais de case. Deux jauges : tolérance et capacité ; on retient la plus basse.
- **Psychologie** : 1 mise en situation + 3 questions inspirées de Grable & Lytton (1999). Jamais de diagnostic.
  On peut nommer un effet de mode avec des mots factuels.
- **Agents** : Profileur, Analyste, Sceptique, Rédacteur (LLM) + Contrôle données et Gardien (code).
- **Coordination** : orchestrateur en code, ordre fixe, dossier partagé, renvois limités (2 max).
- **Débat** : contradiction outillée. Le Sceptique cite un F-n et force un recalcul ; le Gardien arbitre.
- **Désaccord non résolu** : préférence manquante → question ; problème de données → recalcul ; doute
  restant → « non vérifié », gris si essentiel. La capacité de perte n'est jamais négociable.
- **Verdict** : 4 états, « X règles respectées sur Y » (pas de % de compatibilité).
- **Moment signature** : curseurs de bascule en direct + miroir de cohérence.
- **Ton** : neutre, clair, jamais « achetez ». Français.

## Ce qu'on laisse tomber

API de nouvelles en direct · probabilité d'atteindre l'objectif · NASA-TLX · questionnaire complet de 13
questions · chef d'orchestre IA · chatbot libre · 3 seaux comme format · bilingue · % de compatibilité.

## Garde-fous (nos 4 peurs)

| Peur | Règle |
|---|---|
| Trop complexe, pas assez créatif | Un seul moment signature, très soigné |
| Ne pas convaincre | Chaque verdict cite une phrase de la personne et un montant en dollars |
| Pas de démo de bout en bout | Squelette déployé samedi soir ; gel dimanche 16 h |
| Générique ou indéfendable | Banc de 12 cas ; si on change de persona et que le texte bouge à peine, échec |

## Calendrier

| Quand | Porte |
|---|---|
| Samedi soir | Squelette de bout en bout (fait en local : `pytest -q`) puis déployé sur AWS |
| Dimanche midi | 3 personas, Sceptique et curseurs de bascule dans l'interface |
| Dimanche 16 h | Gel des fonctionnalités, tests et répétitions |
| Dimanche 23 h 59 | GitHub + application |
| Dimanche nuit | Enregistrer la vidéo avant la destruction des comptes AWS (lundi 13 h 59) |
| Lundi 14 h | Vidéo, one-pager, documentation technique |

## À faire par voie (prochaines étapes)

- **Données (Rayan)** : vérifier les 31 actifs au contrôle qualité ; ajouter une source ESG documentée pour
  les exclusions de Mateo ; calcul de fréquence historique (bonus).
- **Agents (Adam)** : brancher Bedrock dans `llm.py` ; consignes du Profileur (extraction JSON), du Sceptique
  (objections libres au format `{cible, texte, recalcul}`) et du Rédacteur ; l'Analyste propose une
  alternative quand une exclusion bloque (ex. ESGV pour Mateo).
- **Gardien et AWS (Yasser)** : valider les seuils de `profil.py` ; compléter le banc à 12 cas ; déployer
  (Lambda ou AgentCore + S3 + Amplify) ; Guardrails (ancrage + refus du conseil d'achat).
- **Interface et pitch (Yahia)** : les 5 étapes, la trace animée, les curseurs de bascule, la fiche conseiller,
  le script de démo.
