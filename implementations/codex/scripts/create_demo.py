#!/usr/bin/env python3
"""Make a local, narrated AlphaForge demo with macOS speech and an isolated browser.

Requirements: macOS say, ffmpeg/ffprobe, Node, the existing Playwright installation,
and the app running at ALPHAFORGE_DEMO_URL (default http://127.0.0.1:8766).
No TTS API and no new model inference are used. Only use_ai=true requests are
replayed from the explicitly labelled, previously recorded ui-export.json.
All intermediate files stay in a temporary directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

STORY = [
    {
        "id": "intro",
        "title": "Comprendre avant de choisir",
        "kind": "Démonstration locale · Voix synthétique",
        "text": (
            "Cette démonstration utilise une voix de synthèse française, produite "
            "localement. Alpha Forge est un atelier de décision financière. "
            "Son principe est simple : formuler une question, modifier une hypothèse, "
            "puis examiner les conséquences calculées et les preuves."
        ),
    },
    {
        "id": "contexte",
        "title": "01 · La question de Robert",
        "kind": "Profils et avoirs de démonstration",
        "text": (
            "Robert prépare un besoin de capital dans quatre ans. Tesla l'attire, "
            "mais il souhaite comprendre le risque de concentration. Sa demande "
            "est libre et modifiable. À droite, l'horizon, le capital et les poids "
            "du portefeuille sont explicites. Les avoirs affichés sont des hypothèses "
            "inventées pour cette démonstration. L'horizon personnel décrit un besoin ; "
            "il ne transforme pas les données passées en prévision."
        ),
    },
    {
        "id": "robert",
        "title": "02 · Deux hypothèses, un historique commun",
        "kind": "Calcul réel · CAD · Achat et conservation",
        "text": (
            "La référence contient vingt-cinq pour cent de Tesla. L'hypothèse "
            "modifiée en contient cinq pour cent ; les autres positions sont "
            "ajustées proportionnellement. Sur cet instantané, la baisse maximale "
            "observée passe d'environ vingt-trois virgule quatre à onze virgule "
            "trois pour cent, pour un rendement cumulé proche. Les courbes utilisent "
            "la même période. Ce résultat décrit le passé : il ne garantit pas "
            "une réduction identique du risque futur."
        ),
    },
    {
        "id": "recalcul",
        "title": "03 · Modifier et recalculer vraiment",
        "kind": "Interaction réelle · Calcul local",
        "text": (
            "Vérifions que le calcul répond aux contrôles. Je remets l'exposition "
            "à vingt-cinq pour cent et je recalcule. Les deux portefeuilles "
            "deviennent identiques : leurs courbes et leurs indicateurs se "
            "superposent. Les résultats proviennent bien du moteur de calcul. "
            "Je reviens ensuite à l'analyse précédente. Le bouton Reculs permet "
            "d'examiner les pertes depuis les sommets, au-delà du seul résultat final."
        ),
    },
    {
        "id": "fenetres",
        "title": "04 · Observer les périodes difficiles",
        "kind": "Fenêtres historiques descriptives",
        "text": (
            "Plus bas, les fenêtres historiques comparent les deux allocations "
            "pendant des épisodes difficiles. Chaque fenêtre recommence avec "
            "les poids initiaux indiqués. Ce sont des comparaisons descriptives, "
            "sans probabilité attribuée à un scénario futur. Le repère personnel "
            "de baisse reste, lui aussi, un sujet de discussion : il ne constitue "
            "jamais un plafond de perte garanti."
        ),
    },
    {
        "id": "mateo",
        "title": "05 · Une exclusion ne signifie pas moins de risque",
        "kind": "Mateo · Calcul local réel",
        "text": (
            "Mateo veut exclure sa détention directe dans Exxon. Ici, elle passe "
            "de dix à zéro pour cent. Le moteur redistribue simplement les autres "
            "poids : il ne cherche pas une allocation optimale. Sur cet historique, "
            "la baisse maximale augmente d'environ douze virgule sept à dix-huit "
            "virgule six pour cent. L'application ne présente donc pas l'exclusion "
            "comme une amélioration automatique de la sécurité."
        ),
    },
    {
        "id": "agent",
        "title": "06 · Examiner une analyse Bedrock enregistrée",
        "kind": "PREUVE BEDROCK ENREGISTRÉE · Aucun nouvel appel",
        "text": (
            "Ouvrons maintenant une véritable analyse de Mateo, déjà enregistrée "
            "lors du test de connexion à Amazon Bedrock. Cette séquence rejoue "
            "le rapport conservé ; elle ne lance pas un nouvel appel. Le modèle "
            "s'appuie sur des outils de comparaison, de lecture documentaire et "
            "d'examen du profil. Les chiffres financiers sont calculés par Python, "
            "puis utilisés pour expliquer le compromis."
        ),
    },
    {
        "id": "preuves",
        "title": "07 · Remonter aux sources et aux actions",
        "kind": "PREUVE BEDROCK ENREGISTRÉE · Trace conservée",
        "text": (
            "Le dossier de preuves rend ce travail inspectable. À gauche, "
            "les références indiquent leur provenance et leur niveau de lecture. "
            "À droite, la trace montre les actions effectivement exécutées "
            "et les identifiants des deux appels Amazon Bedrock enregistrés. "
            "Ces fiches documentaires qualifiées ne sont pas une recherche "
            "de nouvelles en direct. Le dossier permet de distinguer une donnée "
            "calculée, une explication et une limite documentaire."
        ),
    },
    {
        "id": "questions",
        "title": "08 · Garder les inconnues visibles",
        "kind": "PREUVE BEDROCK ENREGISTRÉE · Conclusions conditionnelles",
        "text": (
            "La conclusion conserve les questions qui comptent : faut-il exclure "
            "seulement Exxon en direct, ou aussi les expositions indirectes ? "
            "Quels retraits pourraient être nécessaires ? Sans les compositions "
            "détaillées des fonds et les documents pertinents, le dossier ne "
            "certifie ni l'absence d'exposition indirecte, ni la qualité "
            "environnementale ou sociale des placements conservés. L'absence "
            "de preuve reste une inconnue."
        ),
    },
    {
        "id": "amira",
        "title": "09 · Diversifier se vérifie",
        "kind": "Amira · Calcul local réel",
        "text": (
            "Amira recherche la croissance sur un horizon plus long. Réduire "
            "Nvidia laisse encore une baisse historique importante. Plusieurs "
            "lignes ne suffisent pas à prouver une bonne diversification : "
            "un fonds technologique et des actions individuelles peuvent "
            "se recouper. Pour mesurer ces recouvrements, il faudrait les "
            "compositions détaillées des fonds. Alpha Forge distingue ainsi "
            "la préférence exprimée, le résultat calculé et les données manquantes."
        ),
    },
    {
        "id": "methode",
        "title": "10 · Comprendre ce qui est calculé",
        "kind": "Méthode documentée · Pas de projection",
        "text": (
            "La méthode explicite ses conventions. Les actifs sont comparés "
            "en dollars canadiens, avec des prix ajustés qui intègrent "
            "les dividendes. Le portefeuille est conservé sans rééquilibrage "
            "entre actifs. Frais de transaction, frais de change et impôts "
            "sont exclus. Cette relecture d'un instantané acquis en deux mille "
            "vingt-six ne démontre pas qu'une stratégie aurait pu être choisie "
            "à l'époque."
        ),
    },
    {
        "id": "export",
        "title": "11 · Conserver un dossier vérifiable",
        "kind": "PREUVE BEDROCK ENREGISTRÉE · Export local du rapport",
        "text": (
            "Le rapport enregistré peut être réexporté localement. Il conserve "
            "les hypothèses, la période, les résultats, les empreintes des "
            "fichiers et la trace des appels Amazon Bedrock. On peut ainsi "
            "reprendre l'analyse et vérifier exactement ce qui a été utilisé. "
            "Les comparaisons restent disponibles localement ; une nouvelle "
            "analyse par l'agent demande un accès actif au compte de l'atelier."
        ),
    },
    {
        "id": "fin",
        "title": "Une décision plus vérifiable",
        "kind": "Voix synthétique locale · Fin de la démonstration",
        "text": (
            "Alpha Forge laisse l'utilisateur juge du compromis. On peut "
            "modifier les hypothèses, comparer leurs conséquences et demander "
            "les preuves. Le résultat n'est ni une promesse de performance "
            "ni un ordre de transaction. Cette démonstration a été produite "
            "localement, avec une voix de synthèse, sans publication externe."
        ),
    },
]


def run(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, check=True, **kwargs)


def probe(path: Path) -> dict:
    return json.loads(run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
        capture_output=True, text=True,
    ).stdout)


def timecode(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 60:02d}:{total % 60:02d}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", default="Amélie")
    parser.add_argument("--rate", type=int, default=185)
    parser.add_argument("--url", default=os.environ.get("ALPHAFORGE_DEMO_URL", "http://127.0.0.1:8766"))
    parser.add_argument("--workdir", type=Path, help="Keep intermediates in this directory.")
    parser.add_argument("--prepare-only", action="store_true", help="Generate narration and manifest without capture.")
    parser.add_argument("--render-only", action="store_true", help="Reuse capture.json from --workdir.")
    args = parser.parse_args()
    for name in ("say", "ffmpeg", "ffprobe", "node"):
        if not shutil.which(name):
            raise SystemExit(f"Required local command missing: {name}")
    voices = run(["say", "-v", "?"], capture_output=True, text=True).stdout
    if not any(line.startswith(args.voice + " ") and "fr_" in line for line in voices.splitlines()):
        raise SystemExit(f"French macOS voice unavailable: {args.voice}")
    archive = ROOT / "artifacts/ui-export.json"
    report = json.loads(archive.read_text())
    assert report["mode"] == "bedrock" and report["agent"]["status"] == "success"
    assert len(report["agent"]["calls"]) == 2
    assert all(call.get("request_id") for call in report["agent"]["calls"])
    work = args.workdir or Path(tempfile.mkdtemp(prefix="alphaforge-commented-demo-"))
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    print(f"Intermediate files: {work}", flush=True)

    scenes = []
    for index, item in enumerate(STORY, 1):
        scene = dict(item, number=index)
        audio = work / f"{index:02d}-{item['id']}.aiff"
        text = work / f"{index:02d}-{item['id']}.txt"
        text.write_text(item["text"], encoding="utf-8")
        if not args.render_only:
            run(["say", "-v", args.voice, "-r", str(args.rate), "-f", str(text), "-o", str(audio)])
        scene["audio"] = str(audio)
        scene["audio_duration"] = float(probe(audio)["format"]["duration"])
        scenes.append(scene)
        print(f"{index:02d} {item['id']}: {scene['audio_duration']:.2f}s", flush=True)
    manifest = {
        "root": str(ROOT), "work": str(work), "url": args.url,
        "archive": str(archive), "voice": args.voice, "rate": args.rate,
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "scenes": scenes,
    }
    manifest_path = work / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"Narration: {sum(s['audio_duration'] for s in scenes):.2f}s", flush=True)
    if args.prepare_only:
        return
    if not args.render_only:
        run(["node", str(ROOT / "scripts/create_demo.cjs"), str(manifest_path)])

    capture = json.loads((work / "capture.json").read_text())
    assert not capture["javascript_errors"], capture["javascript_errors"]
    assert capture["new_aws_requests"] == 0
    assert capture["same_weights_identical"]
    assert capture["export_identical"]
    recording = Path(capture["video"])
    recording_duration = float(probe(recording)["format"]["duration"])
    # Screencast begins just after page creation. Use its actual duration to
    # reconcile the recording clock rather than assume a launch delay.
    clock_offset = recording_duration - capture["wall_duration"]
    start = max(0, capture["scenes"][0]["start"] + clock_offset)
    finish = capture["end"] + clock_offset
    length = finish - start
    if not 240 <= length <= 305:
        raise SystemExit(f"Expected an approximately 4–5 minute demo, got {length:.2f}s; adjust --rate.")
    out = ROOT / "artifacts/AlphaForge_demo_commentee.mp4"
    candidate = work / "final.mp4"
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y", "-i", str(recording)]
    for scene in scenes:
        cmd.extend(["-i", scene["audio"]])
    filters = [f"[0:v]trim=start={start:.4f}:duration={length:.4f},setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,fps=25[v]"]
    inputs = []
    for index, actual in enumerate(capture["scenes"], 1):
        delay = round((actual["start"] - capture["scenes"][0]["start"]) * 1000)
        filters.append(f"[{index}:a]aresample=48000,adelay={delay}:all=1[a{index}]")
        inputs.append(f"[a{index}]")
    filters.append(
        "".join(inputs)
        + f"amix=inputs={len(inputs)}:normalize=0:duration=longest,"
        + f"loudnorm=I=-18:TP=-1.5:LRA=11,apad,atrim=duration={length:.4f}[a]"
    )
    metadata = work / "chapters.ffmeta"
    lines = [
        ";FFMETADATA1", "title=AlphaForge — Démonstration commentée",
        "comment=Voix macOS Amélie. Calculs locaux réels. Séquences Bedrock explicitement enregistrées.",
    ]
    for i, actual in enumerate(capture["scenes"]):
        begin = actual["start"] - capture["scenes"][0]["start"]
        end = (capture["scenes"][i + 1]["start"] - capture["scenes"][0]["start"]) if i + 1 < len(scenes) else length
        lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={round(begin * 1000)}",
                  f"END={round(end * 1000)}", f"title={scenes[i]['title']}"]
    metadata.write_text("\n".join(lines) + "\n")
    metadata_index = len(scenes) + 1
    cmd += [
        "-i", str(metadata), "-filter_complex", ";".join(filters),
        "-map", "[v]", "-map", "[a]", "-map_metadata", str(metadata_index),
        "-map_chapters", str(metadata_index),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
        "-movflags", "+faststart", "-t", f"{length:.4f}", str(candidate),
    ]
    print(f"Rendering {length:.1f}s, H.264/AAC, 1920×1080…", flush=True)
    run(cmd)
    info = probe(candidate)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    audio = next(s for s in info["streams"] if s["codec_type"] == "audio")
    assert video["codec_name"] == "h264"
    assert (video["width"], video["height"]) == (1920, 1080)
    assert audio["codec_name"] == "aac"
    assert abs(float(info["format"]["duration"]) - length) < 0.2
    # Decode the entire delivered file; this catches truncation and mux errors.
    run(["ffmpeg", "-v", "error", "-i", str(candidate), "-f", "null", "-"])
    volume = run(
        ["ffmpeg", "-hide_banner", "-i", str(candidate), "-vn", "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    volume_lines = [line.split("]")[-1].strip() for line in volume.splitlines()
                    if "mean_volume" in line or "max_volume" in line]
    assert "mean_volume: -inf" not in volume
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(candidate, out)
    machine_summary = {
        "duration_seconds": round(float(info["format"]["duration"]), 2),
        "video_codec": video["codec_name"],
        "audio_codec": audio["codec_name"],
        "width": video["width"],
        "height": video["height"],
        "frames_per_second": 25,
        "new_model_inferences": capture["new_aws_requests"],
        "recorded_bedrock_report_id": report["id"],
        "full_decode_passed": True,
        "export_identical_to_archive": capture["export_identical"],
    }

    transcript = [
        "# AlphaForge — transcription de la démonstration commentée", "",
        f"Durée vérifiée : **{timecode(round(length))}** ({length:.2f} secondes). MP4 H.264/AAC, 1920 × 1080, 25 images/s.",
        f"Voix de synthèse locale : **{args.voice}**, macOS `say`, {args.rate} mots/minute.",
        "La voix synthétique est annoncée au début et à la fin. Aucun service de synthèse vocale distant.", "",
        "## Provenance et vérifications", "",
        "- Application réelle capturée avec Chromium isolé, sans utiliser un profil personnel.",
        "- Navigation et calculs Robert, Mateo et Amira effectués dans l’application locale.",
        "- Recalcul de Robert à 25 % : séries des deux portefeuilles strictement identiques ; retour arrière vérifié.",
        "- Les séquences de l’agent et l’export rejouent la réponse Bedrock déjà enregistrée, sous un bandeau explicite.",
        f"- Rapport enregistré : `{report['id']}` ; empreinte SHA-256 : `{manifest['archive_sha256']}`.",
        f"- Appels AWS conservés dans ce rapport : {', '.join('`' + c['request_id'] + '`' for c in report['agent']['calls'])}.",
        "- Aucun nouvel appel AWS pendant la production. Aucun calcul financier modifié pour le montage.",
        "- Export comparé intégralement au rapport archivé. Aucune erreur JavaScript.",
        "- Décodage complet du MP4 effectué sans erreur ; audio présent et non silencieux.",
        f"- Mesure sonore : {' ; '.join(volume_lines)}.",
        "- Aucune publication externe.", "",
        "## Bilan machine", "",
        "```json", json.dumps(machine_summary, ensure_ascii=False, indent=2), "```", "",
        "## Reproduire", "",
        "Prérequis : macOS, voix française Amélie (`say -v '?'`), `ffmpeg`, `ffprobe`, Node,",
        "Chromium et Playwright dans `runtime/browser-check/node_modules/playwright`, et le serveur local démarré.",
        "Les dépendances FFmpeg peuvent être installées par `brew install ffmpeg`.", "",
        "```sh", "python3 scripts/create_demo.py", "```", "",
        "La commande ne lance aucune nouvelle inférence. Elle utilise `artifacts/ui-export.json` comme archive",
        "explicitement désignée, et effectue les autres comparaisons via le vrai serveur local.",
        "Les fichiers intermédiaires vont dans un répertoire temporaire dont le chemin est affiché.",
        "Options : `--voice`, `--rate`, `--url`, `--workdir`, `--prepare-only`, `--render-only`.", "",
        "## Paroles et séquences", "",
    ]
    for scene, actual in zip(scenes, capture["scenes"]):
        at = actual["start"] - capture["scenes"][0]["start"]
        transcript += [
            f"### {timecode(at)} — {scene['title']}", "",
            f"*Bandeau : {scene['kind']}.*", "", scene["text"], "",
        ]
    (ROOT / "docs/demo-transcript.md").write_text("\n".join(transcript), encoding="utf-8")
    verification = {
        "output": str(out), "duration": float(info["format"]["duration"]),
        "bytes": out.stat().st_size, "video": "H.264 1920×1080 25fps",
        "audio": "AAC 48kHz", "volume": volume_lines,
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "capture": capture, "archive_sha256": manifest["archive_sha256"],
    }
    (work / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in verification.items() if k != "capture"}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
