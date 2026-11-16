"""Dossier de décision : ce que l'utilisateur voit et ce que le jury peut vérifier."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .evidence import Claim, Record, Registry, verify_claims

SECTIONS = {
    "cadre": "Cadre",
    "profil": "Ce que nous savons du profil",
    "constat": "Constats chiffrés",
    "tension": "Tensions avec le profil",
    "alternative": "Options comparées",
    "question": "Information décisive manquante",
    "condition": "Ce qui ferait changer la conclusion",
    "limite": "Limites",
}


@dataclass
class Dossier:
    scenario: str
    persona: str
    request: str
    mode: str  # « workflow fixe », « agent Bedrock », « agent local sans AWS »
    registry: Registry
    trace: list[dict]
    claims: list[Claim] = field(default_factory=list)
    title: str = ""
    summary: str = ""  # gabarit à références, deux ou trois phrases
    aws: dict = field(default_factory=dict)  # identifiants de requêtes, modèle, région
    # Graphiques : {"titre", "type": "ligne"|"barres", "unite", "series": {nom: [[x, y], …]}, "sources": [ids]}
    charts: list[dict] = field(default_factory=list)
    # Fiche de profil affichée en tête : [(intitulé, id d'enregistrement)]
    profile_card: list[tuple[str, str]] = field(default_factory=list)
    # Chiffres clés : {"libelle", "valeur": id, "detail": gabarit à références}
    highlights: list[dict] = field(default_factory=list)
    # Tableaux : {"titre", "colonnes": [str], "lignes": [{"nom": str, "cellules": [id | None]}]}
    tables: list[dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))

    def add(self, kind: str, text: str, *refs: str) -> Claim:
        if kind not in SECTIONS:
            raise ValueError(f"section inconnue : {kind}")
        c = Claim(f"A-{len(self.claims) + 1:03d}", kind, text, list(refs))
        self.claims.append(c)
        return c

    def _display_claims(self) -> list[Claim]:
        """Textes affichés hors affirmations (chiffres clés, en-têtes de tableaux), soumis aux mêmes règles."""
        out = []
        for i, h in enumerate(self.highlights, 1):
            out.append(Claim(f"K-{i:02d}", "constat", h["libelle"] + " " + h.get("detail", ""), [h["valeur"]]))
        for t, tab in enumerate(self.tables, 1):
            for j, col in enumerate(tab["colonnes"]):
                ids = [r["cellules"][j] for r in tab["lignes"] if r["cellules"][j]]
                out.append(Claim(f"T-{t}-c{j}", "constat", col, ids))
            for k, row in enumerate(tab["lignes"]):
                out.append(Claim(f"T-{t}-l{k}", "constat", row["nom"], [c for c in row["cellules"] if c]))
        return out

    def verification(self) -> dict:
        claims = list(self.claims) + self._display_claims()
        if self.summary:
            claims.append(Claim("A-000", "constat", self.summary))
        out = verify_claims(claims, self.registry)
        out["elements_verifies"] = out["affirmations"]  # affirmations + résumé + chiffres clés + en-têtes de tableaux
        out["affirmations"] = len(self.claims)
        return out

    def to_dict(self) -> dict:
        reg = self.registry
        return {
            "scenario": self.scenario,
            "titre": self.title or self.scenario,
            "persona": self.persona,
            "demande": self.request,
            "mode": self.mode,
            "cree_le": self.created_at,
            "resume": {"gabarit": self.summary, "texte": reg.render(self.summary)},
            "affirmations": [
                {
                    "id": c.id,
                    "section": c.kind,
                    "gabarit": c.text,
                    "texte": reg.render(c.text),
                    "references": c.all_refs(),
                    "statut": c.status(reg),
                }
                for c in self.claims
            ],
            "enregistrements": {rid: r.to_dict() for rid, r in reg.records.items()},
            "trace": self.trace,
            "graphiques": self.charts,
            "fiche_profil": self.profile_card,
            "chiffres_cles": self.highlights,
            "tableaux": self.tables,
            "aws": self.aws,
            "verification": self.verification(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Dossier":
        """Reconstruit un dossier enregistré (dossier.json) pour le revérifier et le rendre à nouveau,
        sans recalcul ni appel de modèle : les enregistrements et les gabarits sont repris tels quels."""
        reg = Registry()
        for rid, r in d["enregistrements"].items():
            reg.records[rid] = Record(rid, r["label"], r["value"], r["unit"], r["status"], r["origin"], subject=r.get("subject", ""),
                                      period=tuple(r["period"]) if r.get("period") else None,
                                      conventions=r.get("conventions", []), inputs=r.get("inputs", {}))
        out = cls(d["scenario"], d["persona"], d["demande"], d["mode"], reg, d.get("trace", []), title=d.get("titre", ""),
                  summary=d["resume"]["gabarit"], aws=d.get("aws", {}), charts=d.get("graphiques", []),
                  profile_card=[tuple(x) for x in d.get("fiche_profil", [])], highlights=d.get("chiffres_cles", []),
                  tables=d.get("tableaux", []), created_at=d["cree_le"])
        out.claims = [Claim(c["id"], c["section"], c["gabarit"], list(c.get("references", []))) for c in d["affirmations"]]
        return out

    def save(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "dossier.json"
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return path
