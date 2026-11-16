"""Essai 1 — installation : versions, licences et dépendances tirées.

Ne fait aucun appel réseau : lit seulement les métadonnées des paquets installés
par « uv run --with … » dans l'environnement éphémère.
"""
import importlib.metadata as md
import json
import re
import sys
from pathlib import Path

RACINES = ["langgraph", "langchain-aws", "langgraph-checkpoint-sqlite"]
SORTIES = Path(__file__).resolve().parent / "sorties"
SORTIES.mkdir(exist_ok=True)


def norme(nom: str) -> str:
    return re.sub(r"[-_.]+", "-", nom).lower()


def licence(dist: md.Distribution) -> str:
    m = dist.metadata
    if m.get("License-Expression"):
        return m["License-Expression"]
    classes = [c.split("::")[-1].strip() for c in m.get_all("Classifier") or [] if c.startswith("License")]
    if classes:
        return " ; ".join(classes)
    texte = (m.get("License") or "").strip()
    return texte.splitlines()[0][:60] if texte else "non déclarée dans les métadonnées"


def dependances_directes(dist: md.Distribution) -> list[str]:
    noms = []
    for exigence in dist.requires or []:
        if "extra ==" in exigence:  # dépendances optionnelles : non tirées par défaut
            continue
        noms.append(norme(re.split(r"[ ;<>=!~\[(]", exigence, maxsplit=1)[0]))
    return noms


def fermeture(racines: list[str]) -> dict[str, md.Distribution]:
    vues: dict[str, md.Distribution] = {}
    pile = [norme(r) for r in racines]
    while pile:
        nom = pile.pop()
        if nom in vues:
            continue
        try:
            dist = md.distribution(nom)
        except md.PackageNotFoundError:
            continue  # dépendance conditionnelle absente sur cette plateforme
        vues[nom] = dist
        pile.extend(dependances_directes(dist))
    return vues


def paquets_du_projet() -> set[str]:
    """Paquets déjà présents dans l'environnement du projet (.venv), pour isoler ce qui est ajouté."""
    racine = Path(__file__).resolve().parents[4] / ".venv"
    chemins = [str(p) for p in racine.glob("lib/python*/site-packages")]
    return {norme(d.metadata["Name"]) for d in md.distributions(path=chemins)} if chemins else set()


if __name__ == "__main__":
    tout = fermeture(RACINES)
    deja = paquets_du_projet()
    lignes = []
    for nom in sorted(tout):
        d = tout[nom]
        lignes.append({"paquet": nom, "version": d.version, "licence": licence(d),
                       "deja_dans_le_projet": nom in deja})
    print(f"Python {sys.version.split()[0]}")
    for r in RACINES:
        print(f"racine  {r} {tout[norme(r)].version}  [{licence(tout[norme(r)])}]")
    print(f"\n{len(lignes)} paquets dans la fermeture des dépendances, "
          f"dont {sum(not l['deja_dans_le_projet'] for l in lignes)} absents de l'environnement du projet :")
    for l in lignes:
        marque = " " if l["deja_dans_le_projet"] else "+"
        print(f" {marque} {l['paquet']:<34} {l['version']:<12} {l['licence']}")
    print("\nDépendances directes déclarées :")
    for r in RACINES:
        print(f"  {r} -> {', '.join(sorted(dependances_directes(tout[norme(r)])))}")
    (SORTIES / "essai01_paquets.json").write_text(json.dumps(lignes, indent=1, ensure_ascii=False))
