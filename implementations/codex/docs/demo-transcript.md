# AlphaForge — transcription de la démonstration commentée

Durée vérifiée : **04:54** (293.58 secondes). MP4 H.264/AAC, 1920 × 1080, 25 images/s.
Voix de synthèse locale : **Amélie**, macOS `say`, 185 mots/minute.
La voix synthétique est annoncée au début et à la fin. Aucun service de synthèse vocale distant.

## Provenance et vérifications

- Application réelle capturée avec Chromium isolé, sans utiliser un profil personnel.
- Navigation et calculs Robert, Mateo et Amira effectués dans l’application locale.
- Recalcul de Robert à 25 % : séries des deux portefeuilles strictement identiques ; retour arrière vérifié.
- Les séquences de l’agent et l’export rejouent la réponse Bedrock déjà enregistrée, sous un bandeau explicite.
- Rapport enregistré : `9861d0b6173640a18d7ede3664aeba25` ; empreinte SHA-256 : `502b8cad2554e371994d3273664a778827d28faf17b6f258842257ae68563c6e`.
- Appels AWS conservés dans ce rapport : `135b729e-1f49-498b-a707-f76f83f8af59`, `37969d33-6b5f-4819-b85c-ad6068d7823e`.
- Aucun nouvel appel AWS pendant la production. Aucun calcul financier modifié pour le montage.
- Export comparé intégralement au rapport archivé. Aucune erreur JavaScript.
- Décodage complet du MP4 effectué sans erreur ; audio présent et non silencieux.
- Mesure sonore : mean_volume: -17.8 dB ; max_volume: -3.5 dB.
- Images du MP4 inspectées à 01:13 (portefeuilles identiques), 02:50 (preuves) et 04:51 (fin) : contenu lisible et bandeaux explicites.
- Aucune publication externe.

## Bilan machine

```json
{
  "duration_seconds": 293.58,
  "video_codec": "h264",
  "audio_codec": "aac",
  "width": 1920,
  "height": 1080,
  "frames_per_second": 25,
  "new_model_inferences": 0,
  "recorded_bedrock_report_id": "9861d0b6173640a18d7ede3664aeba25",
  "full_decode_passed": true,
  "export_identical_to_archive": true
}
```

## Reproduire

Prérequis : macOS, voix française Amélie (`say -v '?'`), `ffmpeg`, `ffprobe`, Node,
Chromium et Playwright dans `runtime/browser-check/node_modules/playwright`, et le serveur local démarré.
Les dépendances FFmpeg peuvent être installées par `brew install ffmpeg`.

```sh
python3 scripts/create_demo.py
```

La commande ne lance aucune nouvelle inférence. Elle utilise `artifacts/ui-export.json` comme archive
explicitement désignée, et effectue les autres comparaisons via le vrai serveur local.
Les fichiers intermédiaires vont dans un répertoire temporaire dont le chemin est affiché.
Options : `--voice`, `--rate`, `--url`, `--workdir`, `--prepare-only`, `--render-only`.

## Paroles et séquences

### 00:00 — Comprendre avant de choisir

*Bandeau : Démonstration locale · Voix synthétique.*

Cette démonstration utilise une voix de synthèse française, produite localement. Alpha Forge est un atelier de décision financière. Son principe est simple : formuler une question, modifier une hypothèse, puis examiner les conséquences calculées et les preuves.

### 00:15 — 01 · La question de Robert

*Bandeau : Profils et avoirs de démonstration.*

Robert prépare un besoin de capital dans quatre ans. Tesla l'attire, mais il souhaite comprendre le risque de concentration. Sa demande est libre et modifiable. À droite, l'horizon, le capital et les poids du portefeuille sont explicites. Les avoirs affichés sont des hypothèses inventées pour cette démonstration. L'horizon personnel décrit un besoin ; il ne transforme pas les données passées en prévision.

### 00:39 — 02 · Deux hypothèses, un historique commun

*Bandeau : Calcul réel · CAD · Achat et conservation.*

La référence contient vingt-cinq pour cent de Tesla. L'hypothèse modifiée en contient cinq pour cent ; les autres positions sont ajustées proportionnellement. Sur cet instantané, la baisse maximale observée passe d'environ vingt-trois virgule quatre à onze virgule trois pour cent, pour un rendement cumulé proche. Les courbes utilisent la même période. Ce résultat décrit le passé : il ne garantit pas une réduction identique du risque futur.

### 01:03 — 03 · Modifier et recalculer vraiment

*Bandeau : Interaction réelle · Calcul local.*

Vérifions que le calcul répond aux contrôles. Je remets l'exposition à vingt-cinq pour cent et je recalcule. Les deux portefeuilles deviennent identiques : leurs courbes et leurs indicateurs se superposent. Les résultats proviennent bien du moteur de calcul. Je reviens ensuite à l'analyse précédente. Le bouton Reculs permet d'examiner les pertes depuis les sommets, au-delà du seul résultat final.

### 01:26 — 04 · Observer les périodes difficiles

*Bandeau : Fenêtres historiques descriptives.*

Plus bas, les fenêtres historiques comparent les deux allocations pendant des épisodes difficiles. Chaque fenêtre recommence avec les poids initiaux indiqués. Ce sont des comparaisons descriptives, sans probabilité attribuée à un scénario futur. Le repère personnel de baisse reste, lui aussi, un sujet de discussion : il ne constitue jamais un plafond de perte garanti.

### 01:49 — 05 · Une exclusion ne signifie pas moins de risque

*Bandeau : Mateo · Calcul local réel.*

Mateo veut exclure sa détention directe dans Exxon. Ici, elle passe de dix à zéro pour cent. Le moteur redistribue simplement les autres poids : il ne cherche pas une allocation optimale. Sur cet historique, la baisse maximale augmente d'environ douze virgule sept à dix-huit virgule six pour cent. L'application ne présente donc pas l'exclusion comme une amélioration automatique de la sécurité.

### 02:12 — 06 · Examiner une analyse Bedrock enregistrée

*Bandeau : PREUVE BEDROCK ENREGISTRÉE · Aucun nouvel appel.*

Ouvrons maintenant une véritable analyse de Mateo, déjà enregistrée lors du test de connexion à Amazon Bedrock. Cette séquence rejoue le rapport conservé ; elle ne lance pas un nouvel appel. Le modèle s'appuie sur des outils de comparaison, de lecture documentaire et d'examen du profil. Les chiffres financiers sont calculés par Python, puis utilisés pour expliquer le compromis.

### 02:34 — 07 · Remonter aux sources et aux actions

*Bandeau : PREUVE BEDROCK ENREGISTRÉE · Trace conservée.*

Le dossier de preuves rend ce travail inspectable. À gauche, les références indiquent leur provenance et leur niveau de lecture. À droite, la trace montre les actions effectivement exécutées et les identifiants des deux appels Amazon Bedrock enregistrés. Ces fiches documentaires qualifiées ne sont pas une recherche de nouvelles en direct. Le dossier permet de distinguer une donnée calculée, une explication et une limite documentaire.

### 02:59 — 08 · Garder les inconnues visibles

*Bandeau : PREUVE BEDROCK ENREGISTRÉE · Conclusions conditionnelles.*

La conclusion conserve les questions qui comptent : faut-il exclure seulement Exxon en direct, ou aussi les expositions indirectes ? Quels retraits pourraient être nécessaires ? Sans les compositions détaillées des fonds et les documents pertinents, le dossier ne certifie ni l'absence d'exposition indirecte, ni la qualité environnementale ou sociale des placements conservés. L'absence de preuve reste une inconnue.

### 03:23 — 09 · Diversifier se vérifie

*Bandeau : Amira · Calcul local réel.*

Amira recherche la croissance sur un horizon plus long. Réduire Nvidia laisse encore une baisse historique importante. Plusieurs lignes ne suffisent pas à prouver une bonne diversification : un fonds technologique et des actions individuelles peuvent se recouper. Pour mesurer ces recouvrements, il faudrait les compositions détaillées des fonds. Alpha Forge distingue ainsi la préférence exprimée, le résultat calculé et les données manquantes.

### 03:48 — 10 · Comprendre ce qui est calculé

*Bandeau : Méthode documentée · Pas de projection.*

La méthode explicite ses conventions. Les actifs sont comparés en dollars canadiens, avec des prix ajustés qui intègrent les dividendes. Le portefeuille est conservé sans rééquilibrage entre actifs. Frais de transaction, frais de change et impôts sont exclus. Cette relecture d'un instantané acquis en deux mille vingt-six ne démontre pas qu'une stratégie aurait pu être choisie à l'époque.

### 04:12 — 11 · Conserver un dossier vérifiable

*Bandeau : PREUVE BEDROCK ENREGISTRÉE · Export local du rapport.*

Le rapport enregistré peut être réexporté localement. Il conserve les hypothèses, la période, les résultats, les empreintes des fichiers et la trace des appels Amazon Bedrock. On peut ainsi reprendre l'analyse et vérifier exactement ce qui a été utilisé. Les comparaisons restent disponibles localement ; une nouvelle analyse par l'agent demande un accès actif au compte de l'atelier.

### 04:36 — Une décision plus vérifiable

*Bandeau : Voix synthétique locale · Fin de la démonstration.*

Alpha Forge laisse l'utilisateur juge du compromis. On peut modifier les hypothèses, comparer leurs conséquences et demander les preuves. Le résultat n'est ni une promesse de performance ni un ordre de transaction. Cette démonstration a été produite localement, avec une voix de synthèse, sans publication externe.
