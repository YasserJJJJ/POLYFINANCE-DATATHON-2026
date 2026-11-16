"""Dossier de décision : l'état partagé que chaque agent lit et complète.

Contrat commun de l'équipe (voir docs/contrats.md). On ne change ces champs
qu'après accord de l'équipe.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

TypeFait = Literal["FAIT", "HYPOTHESE", "SCENARIO"]
EtatVerdict = Literal["coherent", "ajustement", "incoherent", "indetermine"]
NiveauRegle = Literal["ok", "orange", "rouge", "gris", "non_evaluee"]


@dataclass
class Fait:
    """Un chiffre ou un constat, toujours relié à sa source et à sa méthode."""

    id: str
    libelle: str
    valeur: Any
    unite: str
    type: TypeFait
    source: str
    methode: str
    lu_ou_calcule: Literal["lu", "calcule"] = "calcule"
    references: list[str] = field(default_factory=list)  # identifiants de sources.REFERENCES (données, méthode, théorie)


@dataclass
class Regle:
    code: str
    libelle: str
    niveau: NiveauRegle
    explication: str
    faits: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)   # sur quoi repose la règle (sources.py)
    type: TypeFait = "HYPOTHESE"                           # nature de l'explication : FAIT, HYPOTHESE ou SCENARIO


@dataclass
class Objection:
    """Objection du Sceptique : toujours liée à un fait et à un recalcul."""

    id: str
    cible: str
    texte: str
    recalcul: str
    resolue: bool = False                                  # la vérification a été exécutée par le code
    reponse: str = ""
    issue: str = ""                                        # confirmee, ecartee ou limite


@dataclass
class EtapeTrace:
    agent: str
    action: str
    detail: str
    faits: list[str] = field(default_factory=list)
    duree_ms: int = 0
    references: list[str] = field(default_factory=list)   # pourquoi cet agent est conçu ainsi (sources.AGENTS)


@dataclass
class Dossier:
    profil: dict
    demande: dict
    faits: list[Fait] = field(default_factory=list)
    objections: list[Objection] = field(default_factory=list)
    regles: list[Regle] = field(default_factory=list)
    verdict: dict = field(default_factory=dict)
    options: list[dict] = field(default_factory=list)
    bascule: dict = field(default_factory=dict)
    qualite_donnees: list[dict] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    texte: dict = field(default_factory=dict)
    trace: list[EtapeTrace] = field(default_factory=list)
    version_contrat: str = "2"
    comparaison: dict = field(default_factory=dict)  # K3 : rempli par la tranche 2
    appels_modele: list[dict] = field(default_factory=list)  # K6 : rempli par la tranche 3
    plan: dict = field(default_factory=dict)  # plan ouvert : rempli quand aucun placement n'est choisi

    def ajouter_fait(self, libelle: str, valeur: Any, unite: str, type_: TypeFait,
                     source: str, methode: str, lu_ou_calcule: str = "calcule",
                     references: list[str] | None = None) -> Fait:
        fait = Fait(f"F-{len(self.faits) + 1}", libelle, valeur, unite, type_, source,
                    methode, lu_ou_calcule, list(references or []))  # type: ignore[arg-type]
        self.faits.append(fait)
        return fait

    def fait(self, fait_id: str) -> Fait | None:
        return next((f for f in self.faits if f.id == fait_id), None)

    def tracer(self, agent: str, action: str, detail: str, faits: list[str] | None = None,
               debut: float | None = None) -> None:
        from .sources import references_agent
        duree = int((time.perf_counter() - debut) * 1000) if debut else 0
        self.trace.append(EtapeTrace(agent, action, detail, faits or [], duree, references_agent(agent)))

    def to_dict(self) -> dict:
        d = asdict(self)
        if not d["plan"]:
            del d["plan"]   # champ facultatif : absent quand un placement est choisi (contrat K7)
        return d
