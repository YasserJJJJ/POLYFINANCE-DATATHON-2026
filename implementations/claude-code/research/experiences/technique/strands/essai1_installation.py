"""Essai 1 : version, licence, dépendances tirées par strands-agents.

Relance : uv run --with strands-agents python research/experiences/technique/strands/essai1_installation.py
Aucun appel de modèle.
"""
import importlib.metadata as m
import os
import sys

d = m.distribution("strands-agents")
print("python", sys.version.split()[0])
print("strands-agents", d.version)
print("licence (métadonnées) :", d.metadata.get("License"), "|", d.metadata.get("License-Expression"))
for c in d.metadata.get_all("Classifier") or []:
    if "License" in c:
        print("classifieur :", c)

print("\nDépendances obligatoires (sans extra) :")
for r in d.requires or []:
    if "extra ==" not in r:
        print("  ", r)

print("\nExtras déclarés :", sorted(d.metadata.get_all("Provides-Extra") or []))

print("\nPaquets présents dans l'environnement, avec leur licence déclarée :")
lignes = []
for dist in m.distributions():
    nom = dist.metadata.get("Name")
    lic = dist.metadata.get("License-Expression") or (dist.metadata.get("License") or "").split("\n")[0][:40]
    if not lic:
        cl = [c.split("::")[-1].strip() for c in (dist.metadata.get_all("Classifier") or []) if "License" in c]
        lic = "; ".join(cl) or "?"
    lignes.append((nom.lower(), dist.version, lic))
for nom, v, lic in sorted(set(lignes)):
    print(f"   {nom:42s} {v:14s} {lic}")
print("total :", len(set(lignes)))

import strands

print("\nchemin du code installé :", os.path.dirname(strands.__file__))
