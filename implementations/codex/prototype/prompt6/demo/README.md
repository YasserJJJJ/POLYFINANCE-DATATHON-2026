# Démonstration du prototype de référence

Ouvrir [la vidéo MP4](AlphaForge-prototype-reference.mp4) ou
[la version WebM](AlphaForge-prototype-reference.webm).

Durée : environ **76 secondes**, capture 1440 × 1000. Il s’agit d’interactions
réelles avec le navigateur : clics, saisie, appels au moteur local et
consultation des dossiers exécutés. Aucun montage d’activité d’agents,
animation d’avancement fictive ou appel de modèle n’a été ajouté.

| Temps approximatif | Interaction montrée |
|---|---|
| 0–7 s | Promesse, choix du dossier Robert |
| 7–14 s | Preuve du minimum et retour à la conclusion |
| 14–23 s | Même dossier approfondi ; allocations et référence simple |
| 23–36 s | Retrait corrigé à 40 000 CAD dans une copie ; calcul réel puis adoption locale |
| 36–49 s | Retour à l’archive ; erreur explicitement simulée puis reprise du calcul réel |
| 49–61 s | Trois révisions exécutées de Robert ; ce qui est réutilisé ou recalculé |
| 61–76 s | Dossier Amira, deux trajectoires historiques et accès aux observations exactes |

Les métadonnées, actions horodatées et reçus locaux sont dans
[actions.json](actions.json). Deux calculs réels et une erreur simulée sont
observés ; les reçus indiquent zéro inférence et zéro modification du
produit. Les reçus AWS consultables dans les dossiers proviennent des
exécutions archivées du Prompt 5.

La capture constitue un parcours de référence, pas un test utilisateur.
Le prototype reste explorable en dehors de cette séquence. L’axe du
graphique et d’autres détails peuvent être affinés lors de la validation ;
la vidéo ne remplace pas l’essai direct de la version courante.

## Reproduire

Serveur du prototype actif sur `http://127.0.0.1:8770` :

```sh
node docs/experience/proofs/demo.cjs
ffmpeg -hide_banner -loglevel error -y \
  -i prototype/prompt6/demo/AlphaForge-prototype-reference.webm \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  -movflags +faststart prototype/prompt6/demo/AlphaForge-prototype-reference.mp4
```

FFmpeg transcode le même flux ; il n’ajoute pas de transitions, de voix ou
de contenu synthétique.
