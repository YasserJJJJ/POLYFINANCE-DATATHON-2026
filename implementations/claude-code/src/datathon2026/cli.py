"""Ligne de commande : `uv run alphaforge demo robert` (ou amira, ou tous)."""

from __future__ import annotations

import argparse
import webbrowser
from pathlib import Path

from . import report, workflow
from .paths import ROOT


AWS_HELP = (
    "AWS n'est pas configuré sur cette machine. Suivez docs/acces-aws.md : installer l'AWS CLI, puis configurer "
    "vous-même le profil `alphaforge` (identifiants saisis par vous seul ; le code ne les lit pas). "
    "En attendant, `alphaforge demo` produit les dossiers avec le workflow fixe, étiqueté comme tel."
)


def save(dossier, out_dir: Path) -> Path:
    d = dossier.to_dict()
    target = out_dir / dossier.scenario
    dossier.save(target)
    html_path = target / "dossier.html"
    html_path.write_text(report.render(d), encoding="utf-8")
    v = d["verification"]
    print(f"{dossier.scenario} ({dossier.mode}) : {v['affirmations']} affirmations, {v['valeurs_reliees']} valeurs reliées, "
          f"{len(v['affirmations_en_echec'])} en échec → {html_path}")
    return html_path


def write_index(out_dir: Path) -> Path:
    """Page d'accueil listant les derniers dossiers produits."""
    import json

    dossiers = []
    for f in sorted(out_dir.glob("*/dossier.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        d["_lien"] = f"{f.parent.name}/dossier.html"
        dossiers.append(d)
    path = out_dir / "index.html"
    path.write_text(report.render_index(dossiers), encoding="utf-8")
    return path


def run_agent(name: str, out_dir: Path, model: str | None, region: str | None, profile: str | None = None,
              request: str | None = None, key: str | None = None) -> Path | None:
    """Scénario de démonstration, ou demande libre (`request`) sans hypothèse fournie d'avance."""
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

    from . import tools as T
    from .agent import DEFAULT_MODEL, DEFAULT_PROFILE, DEFAULT_REGION, BedrockAgent

    scenarios = T.load_scenarios()
    if request:
        scenario = {"persona": name, "demande": request, "origine_demande": "demande libre saisie dans l'outil"}
    elif name in scenarios:
        scenario = scenarios[name]
    else:
        print(f"Aucun scénario de démonstration pour « {name} » : précisez la demande avec --demande.")
        return None
    try:
        agent = BedrockAgent(model=model or DEFAULT_MODEL, region=region or DEFAULT_REGION, profile=profile or DEFAULT_PROFILE)
        dossier = agent.run(key or (f"{name}-libre" if request else f"{name}-agent"), scenario)
    except RuntimeError as e:
        print(f"Dossier non produit : {e}")
        return None
    except NoCredentialsError:
        print(AWS_HELP)
        return None
    except (ClientError, BotoCoreError) as e:
        print(f"Appel Bedrock refusé ou en échec : {e}")
        return None
    return save(dossier, out_dir)


def rerender(out_dir: Path) -> list[Path]:
    """Revérifie et régénère chaque dossier enregistré, sans recalcul ni appel de modèle (utilisable sans AWS)."""
    import json

    from .dossier import Dossier

    return [save(Dossier.from_dict(json.loads(f.read_text(encoding="utf-8"))), out_dir) for f in sorted(out_dir.glob("*/dossier.json"))]


def aws_check(region: str | None, model: str | None, profile: str | None = None) -> int:
    """Vérifications en lecture seule : identité et disponibilité du modèle (aucun appel de modèle)."""
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, TokenRetrievalError

    from .agent import DEFAULT_MODEL, DEFAULT_PROFILE, DEFAULT_REGION, aws_session

    region, model, profile = region or DEFAULT_REGION, model or DEFAULT_MODEL, profile or DEFAULT_PROFILE
    try:
        sess = aws_session(profile, region)
        print(f"Profil AWS utilisé : {sess.profile_name}")
        ident = sess.client("sts").get_caller_identity()
        print(f"Identité AWS : compte …{ident['Account'][-4:]}, région {region}")
        bedrock = sess.client("bedrock")
        try:
            listed = bedrock.list_inference_profiles(typeEquals="SYSTEM_DEFINED", maxResults=1000)["inferenceProfileSummaries"]
            claude = sorted(p["inferenceProfileId"] for p in listed if "claude" in p["inferenceProfileId"] and p.get("status") == "ACTIVE")
            print("Profils d'inférence Claude actifs : " + (", ".join(c for c in claude if "-5" in c) or "aucun profil 5.x")
                  + f" ({len(claude)} au total)")
        except ClientError as e:
            print(f"Liste des profils d'inférence refusée : {e.response['Error']['Code']}")
        prof = bedrock.get_inference_profile(inferenceProfileIdentifier=model)
        print(f"Profil d'inférence {model} : {prof.get('status')} ; destinations : "
              + ", ".join(m["modelArn"].split(":")[3] for m in prof.get("models", [])))
    except NoCredentialsError:
        print(AWS_HELP)
        return 1
    except TokenRetrievalError:
        print(f"Session AWS expirée : lancez `aws sso login --profile {profile}` dans votre terminal, puis réessayez.")
        return 1
    except (ClientError, BotoCoreError) as e:
        print(f"Vérification AWS en échec : {e}")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="alphaforge", description="AlphaForge — dossiers de décision vérifiables (simulation).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    demo = sub.add_parser("demo", help="scénario de démonstration avec le workflow fixe (sans AWS)")
    demo.add_argument("scenario", choices=[*workflow.WORKFLOWS, "tous"])
    ag = sub.add_parser("agent", help="scénario ou demande libre traités par l'agent sur Amazon Bedrock")
    ag.add_argument("scenario", choices=["amira", "mateo", "robert"], help="profil fictif (scénario de démonstration si --demande est absent)")
    ag.add_argument("--demande", help="demande libre, sans hypothèse de démonstration fournie d'avance")
    ag.add_argument("--nom", help="nom du dossier produit (défaut : <profil>-agent ou <profil>-libre)")
    ag.add_argument("--modele")
    ag.add_argument("--region")
    chk = sub.add_parser("aws-verifier", help="vérifier l'accès AWS en lecture seule (aucun appel de modèle)")
    chk.add_argument("--modele")
    chk.add_argument("--region")
    rr = sub.add_parser("rendre", help="revérifier et régénérer les dossiers enregistrés (sans AWS, sans recalcul)")
    for p in (ag, chk):
        p.add_argument("--profil", help="profil AWS nommé (défaut : alphaforge)")
    for p in (demo, ag, rr):
        p.add_argument("--sortie", type=Path, default=ROOT / "runs")
        p.add_argument("--ouvrir", action="store_true", help="ouvrir le dossier HTML dans le navigateur")
    args = ap.parse_args(argv)
    if args.cmd == "aws-verifier":
        return aws_check(args.region, args.modele, args.profil)
    if args.cmd == "rendre":
        paths = rerender(args.sortie)
    elif args.cmd == "agent":
        paths = [run_agent(args.scenario, args.sortie, args.modele, args.region, args.profil, args.demande, args.nom)]
    else:
        names = list(workflow.WORKFLOWS) if args.scenario == "tous" else [args.scenario]
        paths = [save(workflow.WORKFLOWS[n](), args.sortie) for n in names]
    write_index(args.sortie)
    if args.ouvrir:
        for p in filter(None, paths):
            webbrowser.open(p.as_uri())
    return 0 if all(paths) else 1


if __name__ == "__main__":
    raise SystemExit(main())
