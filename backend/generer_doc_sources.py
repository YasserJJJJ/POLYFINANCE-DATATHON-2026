"""Génère docs/sources.md à partir du registre (alphaforge/sources.py), pour la documentation technique.

Lancer depuis backend/ :  python generer_doc_sources.py
Le test tests/test_sources.py::test_doc_sources_a_jour vérifie que le fichier correspond au registre.
"""
from __future__ import annotations

import sys
from pathlib import Path

for _flux in (sys.stdout, sys.stderr):
    if hasattr(_flux, "reconfigure"):
        _flux.reconfigure(encoding="utf-8", errors="replace")

from alphaforge import sources  # noqa: E402

CIBLE = Path(__file__).resolve().parents[1] / "docs" / "sources.md"
TITRES = {"donnees": "Données", "reglementation": "Réglementation", "recherche": "Recherche publiée",
          "methode": "Documentation de méthode", "interne": "Document de l'équipe"}
SECTIONS = [
    ("Faits calculés par l'Analyste", ["chute", "recuperation", "volatilite", "rendement", "pire12", "perte",
                                       "correlation", "secteur", "reference", "devise_usd", "alternative"]),
    ("Seuils et barèmes de l'équipe (faits HYPOTHESE)", ["h_perte", "h_capacite", "h_concentration", "h_volatil",
                                                         "h_correlation"]),
    ("Règles du Gardien", [k for k in sources.JUSTIFICATIONS if k.startswith("regle-")]),
    ("Profil, verdict et explication", ["jauges", "questions", "verdict", "ajustement", "bascule"]),
]


def court(rid: str) -> str:
    r = sources.REFERENCES[rid]
    return f"{str(r['auteurs']).split(',')[0].split(';')[0].strip()} ({r['annee']})"


def generer() -> str:
    lignes = ["# Sources, méthodes et hypothèses", "",
              "> Fichier généré par `backend/generer_doc_sources.py` à partir de `backend/alphaforge/sources.py`. "
              "Ne pas modifier à la main : modifier le registre, puis relancer le script.", "",
              "Chaque élément montré à la personne répond à trois questions : **quelle donnée** (fichier, colonne), "
              "**quelle règle de calcul** (appliquée par le code) et **sur quelle base** (réglementation, recherche, "
              "ou choix de l'équipe dit comme tel). Le niveau d'examen de chaque source vient du dossier de recherche "
              "de l'équipe (14 nov. 2026) : une référence non relue n'est jamais présentée comme vérifiée.", ""]
    for titre, cles in SECTIONS:
        lignes += [f"## {titre}", "", "| Élément | Données | Règle de calcul | Références | Hypothèse de l'équipe |",
                   "|---|---|---|---|---|"]
        for cle in cles:
            j = sources.JUSTIFICATIONS[cle]
            donnees = ", ".join(court(r) for r in j.get("donnees", [])) or "—"
            refs = ", ".join(court(r) for r in j.get("references", [])) or "—"
            lignes.append(f"| `{cle}` | {donnees} | {j['calcul']} | {refs} | {j.get('hypothese', '—')} |")
        lignes.append("")
    lignes += ["## Agents : pourquoi chacun est conçu ainsi", "", "| Agent | Conception | Références |", "|---|---|---|"]
    for agent, a in sources.AGENTS.items():
        lignes.append(f"| {agent} | {a['role']} | {', '.join(court(r) for r in a['references'])} |")
    lignes.append("")
    lignes += ["## Registre des références", ""]
    for type_, titre in TITRES.items():
        refs = [(rid, r) for rid, r in sources.REFERENCES.items() if r["type"] == type_]
        if not refs:
            continue
        lignes += [f"### {titre}", "", "| Id | Référence | Ce qu'elle justifie | Niveau d'examen |", "|---|---|---|---|"]
        for rid, r in refs:
            lien = f" [lien]({r['lien']})" if r["lien"] else ""
            lignes.append(f"| `{rid}` | {r['auteurs']} ({r['annee']}). *{r['titre']}*. {r['publication']}.{lien} | "
                          f"{r['apport']} | {r['examen']} |")
        lignes.append("")
    return "\n".join(lignes)


if __name__ == "__main__":
    CIBLE.write_text(generer(), encoding="utf-8", newline="\n")
    print(f"Écrit : {CIBLE}")
