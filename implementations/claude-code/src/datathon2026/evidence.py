"""Registre de preuves et vérification des explications.

Principe (R04) : aucun nombre libre. Chaque valeur affichée provient d'un enregistrement
identifié (résultat calculé, fait de profil, source documentaire). Les textes sont écrits avec
des références ``{{R-0001}}`` que le code remplace par la valeur formatée ; tout chiffre écrit
à la main dans un texte est signalé par le vérificateur.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

# Statuts épistémiques, du plus solide au plus faible. Une affirmation prend le statut le plus
# faible des enregistrements qu'elle cite.
STATUS_ORDER = ("mesuré", "source", "déclaré", "scénario", "hypothèse", "inconnu")
_RANK = {s: i for i, s in enumerate(STATUS_ORDER)}

PREFIXES = {
    "R": "résultat calculé",
    "P": "fait de profil",
    "S": "source documentaire",
    "D": "donnée",
}

# Références dans les textes :
#   {{R-0001}}              valeur formatée
#   {{R-0001.label}}        libellé de l'enregistrement (utile pour une information inconnue)
#   {{cmp:R-0001:R-0002}}   « supérieure à » / « inférieure à » / « égale à », calculé sur les
#                           valeurs arrondies telles qu'affichées
#   {{cmpabs:R-0001:R-0002}} « plus forte que » / « moins forte que » / « aussi forte que »,
#                           sur les valeurs absolues (pertes)
#   {{cmpduree:R-0001:P-0002}} « atteint ou dépasse » / « atteint presque » / « représente une part
#                           importante de » / « reste nettement inférieure à », selon le rapport
#                           de la première valeur à la seconde (une durée face à un horizon)
# Le sens d'une comparaison n'est donc jamais écrit à la main.
PLACEHOLDER = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
CMP_EXPR = re.compile(r"(cmp|cmpabs|cmpduree):([A-Z]-\d{4}):([A-Z]-\d{4})")
_ID = re.compile(r"[A-Z]-\d{4}")
_DIGITS = re.compile(r"\d+(?:[.,]\d+)*")
_DECIMALS = {"pct": 3, "pp": 3, "days": 0, "weeks": 0, "count": 0, "years": 1, "ratio": 2}
_NUMERIC = set(_DECIMALS)

# Garde lexicale : un comparatif écrit à la main n'est relié à aucun calcul. Les superlatifs
# (« le plus … ») et les tournures neutres (« X contre Y ») ne sont pas visés ; les sections
# « question » et « condition », qui formulent des hypothèses et non des constats, en sont dispensées.
_HANDWRITTEN_CMP = [re.compile(p, re.IGNORECASE) for p in (
    r"\b(?:supérieur|inférieur|meilleur)e?s?\b",
    r"\b(?:dépass|excèd|excéd)\w*",
    r"\bau-delà\b|\ben deçà\b|\bau-dessus\b|\bau-dessous\b|\ben dessous\b",
    r"\b(?:plus|moins|aussi|autant|davantage)\s+(?:[\w-]+\s+){0,2}qu(?:e\b|['’])",
    r"(?<!\ble )(?<!\bla )(?<!\bles )\b(?:plus|moins)\s+(?:élevé|faible|fort|bas|haut|grand|petit|important|lourd|risqué"
    r"|volatil|concentré|diversifié|stable|long|court|large)\w*",
    r"\b(?:augment|diminu|grimp|recul)\w+|\bmonte(?:nt|rait|raient)?\b",
)]
# Grandeur écrite en lettres : un nombre suivi d'une unité, ou une fraction (« dix pour cent »,
# « quinze ans », « la moitié »). Un simple dénombrement (« les deux fonds ») n'est pas visé.
_NUMBER_WORD = r"(?:deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|vingt|trente|quarante|cinquante|soixante|cents?|mille)"
_WORDED_NUMBER = re.compile(
    rf"\b{_NUMBER_WORD}(?:[- ]{_NUMBER_WORD})*\s+(?:pour\s+cent|%|ans?|années?|mois|jours?|semaines?|points?|fois)(?!\w)"
    r"|\b(?:moitié|double|triple|quart)\b|\b(?:un|deux)\s+tiers\b", re.IGNORECASE)
_CONDITIONAL = re.compile(r"(?<!même )\b(?:si|s['’]ils?)\s+[^.;:!?,]*", re.IGNORECASE)
SECTIONS_SANS_GARDE = {"question", "condition"}
_VOWELS = "aeiouéèêàâîôû"
_CONTRACTIONS = {("à", "le"): "au", ("à", "les"): "aux", ("de", "le"): "du", ("de", "les"): "des"}
_DETERMINERS = {"un": True, "le": True, "ce": True, "cet": True, "son": True, "aucun": True, "il": True,  # True : masculin
                "une": False, "la": False, "cette": False, "sa": False, "aucune": False, "elle": False}
_PREPOSITIONS = {"de", "à", "dans", "pour", "avec", "sur", "sous", "par", "en", "contre", "vers", "chez", "entre", "sans", "selon"}
_COPULAS = {"est", "sont", "serait", "seraient", "était", "étaient", "reste", "restent", "demeure", "devient", "semble", "paraît"}
_ADVERBS = {"donc", "alors", "ainsi", "aussi", "nettement", "encore", "toujours", "bien", "ici", "désormais"}


def placeholder_ids(template: str) -> list[str]:
    return list(dict.fromkeys(i for expr in PLACEHOLDER.findall(template) for i in _ID.findall(expr)))


def handwritten_comparisons(text: str) -> list[str]:
    """Comparatifs écrits à la main dans un texte déjà débarrassé de ses références. Une proposition
    conditionnelle (« si le filtre compte davantage que l'écart ») formule une hypothèse, pas un
    constat : elle est écartée jusqu'à la ponctuation suivante ; « même si » affirme et reste contrôlé."""
    text = _CONDITIONAL.sub(lambda m: " " * len(m.group(0)), text)
    spans = sorted({m.span() for p in _HANDWRITTEN_CMP for m in p.finditer(text)})
    out, end = [], -1
    for a, b in spans:
        if a >= end:  # une même tournure peut correspondre à deux motifs
            out.append(text[a:b].strip())
        end = max(end, b)
    return out


def rounded_value(value: Any, unit: str) -> float:
    return round(float(value), _DECIMALS[unit])


def comparison_word(kind: str, x: float, y: float) -> str | None:
    """Sens d'une comparaison, calculé sur les valeurs arrondies telles qu'affichées."""
    if kind == "cmpabs":
        x, y = abs(x), abs(y)
        return "plus forte que" if x > y else "moins forte que" if x < y else "aussi forte que"
    if kind == "cmpduree":
        if x < 0 or y <= 0:
            return None
        r = x / y
        return ("atteint ou dépasse" if r >= 1 else "atteint presque" if r >= 0.9
                else "représente une part importante de" if r >= 0.5 else "reste nettement inférieure à")
    return "supérieure à" if x > y else "inférieure à" if x < y else "égale à"


def _genders(words: list[str]) -> list[tuple[bool, bool]]:
    """(masculin ?, introduit par une préposition ?) pour chaque déterminant ou pronom sujet."""
    return [(_DETERMINERS[w], i > 0 and words[i - 1] in _PREPOSITIONS) for i, w in enumerate(words) if w in _DETERMINERS]


def _masculine_noun(before: str) -> bool:
    """Genre du nom qualifié par la comparaison. Heuristique d'accord, féminin par défaut :
    après un verbe d'état (« la part … est »), le sujet de la proposition ; sinon le dernier groupe
    nominal avant la comparaison (« un rendement annualisé », « avec une pire baisse »), en écartant
    un complément (« une part dans le portefeuille » → féminin)."""
    clause = re.split(r"[.;:!?]", PLACEHOLDER.sub(" ", before))[-1].lower()
    words = re.findall(r"[\w'’-]+", clause)
    tail = [w for w in words if w not in _ADVERBS]
    if tail and tail[-1] in _COPULAS:
        subject = [m for m, prep in _genders(words) if not prep]
        return bool(subject) and subject[0]
    for scope in (re.findall(r"[\w'’-]+", clause.rsplit(",", 1)[-1]), words):
        found = _genders(scope)
        if found:
            return ([m for m, prep in found if not prep] or [m for m, _ in found])[-1]
    return False


def join_comparison(word: str, tail: str, before: str = "") -> tuple[str, int]:
    """Accorde une comparaison calculée avec les mots qui l'entourent dans le gabarit.

    « supérieure à » + « le plafond » → « supérieure au plafond » ; un « à » ou un « que » répété est
    absorbé ; « que » et « de » s'élident devant une voyelle ; après un nom masculin (`before`),
    « supérieure » devient « supérieur ». Le sens n'est jamais modifié. Renvoie le texte accordé et
    le nombre de caractères de `tail` absorbés."""
    if _masculine_noun(before):
        word = re.sub(r"\b(supérieur|inférieur|égal|fort)e\b", r"\1", word)
    m = re.match(r"(\s+)([^\s{]+)", tail)
    if not m:
        return word, 0
    stem, _, last = word.rpartition(" ")
    nxt = m.group(2).lower()
    if nxt == last and last in {"à", "que", "de"}:  # mot répété par le rédacteur
        return word, m.end()
    if (last, nxt) in _CONTRACTIONS:
        return f"{stem} {_CONTRACTIONS[(last, nxt)]}", m.end()
    if last == "à" and nxt in {"au", "aux"}:
        return stem, 0
    if last in {"que", "de"} and nxt[0] in _VOWELS:
        return word[:-1] + "'", len(m.group(1))
    return word, 0

NBSP = " "
MINUS = "−"
_MONTHS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def _num(v: float, decimals: int) -> str:
    s = f"{abs(v):,.{decimals}f}".replace(",", " ").replace(".", ",")
    return (MINUS if v < 0 and round(abs(v), decimals) != 0 else "") + s


def format_value(value: Any, unit: str) -> str:
    if value is None:
        return "non disponible"
    if unit == "pct":
        return _num(value * 100, 1) + NBSP + "%"
    if unit == "pp":
        return _num(value * 100, 1) + NBSP + "pt"
    if unit == "days":
        return _num(value, 0) + NBSP + "jours"
    if unit == "weeks":
        return _num(value, 0) + NBSP + "semaines"
    if unit == "years":
        return _num(value, 1) + NBSP + ("an" if abs(round(value, 1)) < 2 else "ans")
    if unit == "ratio":
        return _num(value, 2)
    if unit == "count":
        return _num(value, 0)
    if unit == "date":
        m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(value))
        if not m:
            return str(value)
        y, mo, d = m.groups()
        return f"{int(d)}{NBSP}{_MONTHS[int(mo) - 1]}{NBSP}{y}"
    return str(value)


@dataclass
class Record:
    id: str
    label: str
    value: Any
    unit: str
    status: str
    origin: str
    subject: str = ""
    period: tuple[str, str] | None = None
    conventions: list[str] = field(default_factory=list)
    inputs: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.status not in _RANK:
            raise ValueError(f"statut inconnu : {self.status}")

    def display(self) -> str:
        return format_value(self.value, self.unit)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["display"] = self.display()
        return d


class Registry:
    """Enregistrements identifiés d'une exécution. Les identifiants suivent l'ordre d'ajout."""

    def __init__(self):
        self.records: dict[str, Record] = {}
        self._counters = {p: 0 for p in PREFIXES}

    def add(self, prefix: str, label: str, value: Any, unit: str, status: str, origin: str, **kw) -> Record:
        if prefix not in PREFIXES:
            raise ValueError(f"préfixe inconnu : {prefix}")
        self._counters[prefix] += 1
        rid = f"{prefix}-{self._counters[prefix]:04d}"
        rec = Record(rid, label, value, unit, status, origin, **kw)
        self.records[rid] = rec
        return rec

    def __contains__(self, rid: str) -> bool:
        return rid in self.records

    def __getitem__(self, rid: str) -> Record:
        return self.records[rid]

    def render_expr(self, expr: str) -> str:
        ids = _ID.findall(expr)
        if any(i not in self.records for i in ids) or not ids:
            return f"[{expr} ?]"
        cmp = CMP_EXPR.fullmatch(expr)
        if cmp:
            a, b = self.records[cmp[2]], self.records[cmp[3]]
            if a.unit not in _NUMERIC or a.unit != b.unit or a.value is None or b.value is None:
                return f"[{expr} ?]"
            return comparison_word(cmp[1], rounded_value(a.value, a.unit), rounded_value(b.value, b.unit)) or f"[{expr} ?]"
        rec = self.records[ids[0]]
        return rec.label if expr.endswith(".label") else rec.display()

    def render(self, template: str) -> str:
        out, last = [], 0
        for m in PLACEHOLDER.finditer(template):
            out.append(template[last : m.start()])
            text, last = self.render_expr(m.group(1)), m.end()
            if CMP_EXPR.fullmatch(m.group(1)) and not text.startswith("["):
                text, used = join_comparison(text, template[last:], template[: m.start()])
                last += used
            out.append(text)
        out.append(template[last:])
        return "".join(out)


@dataclass
class Issue:
    kind: str  # "référence inconnue", "nombre non relié", "nombre écrit en lettres", "comparaison écrite à la main", "affirmation non étayée"
    detail: str


def check_template(template: str, registry: Registry, refs: list[str] | None = None, comparisons: bool = True) -> list[Issue]:
    """Contrôle déterministe d'un texte à références.

    - toute référence ``{{X-0000}}`` doit exister dans le registre ;
    - tout chiffre restant hors référence est un nombre non relié, sauf s'il figure dans le
      libellé ou la période d'un enregistrement cité (ex. « en 2022 » pour un résultat
      intitulé « Rendement 2022 », ou « S&P 500 » pour un actif cité) ;
    - toute grandeur écrite en lettres (« dix pour cent », « la moitié ») est signalée ;
    - tout comparatif écrit à la main est signalé (`comparisons`) : le sens d'une comparaison
      passe par ``{{cmp:…}}``, ``{{cmpabs:…}}`` ou ``{{cmpduree:…}}``.
    """
    issues: list[Issue] = []
    cited = list(dict.fromkeys(placeholder_ids(template) + list(refs or [])))
    for rid in cited:
        if rid not in registry:
            issues.append(Issue("référence inconnue", rid))
    for expr in PLACEHOLDER.findall(template):
        if not _ID.fullmatch(expr) and not re.fullmatch(r"[A-Z]-\d{4}\.label", expr) and not CMP_EXPR.fullmatch(expr):
            issues.append(Issue("référence mal formée", expr))
        elif registry.render_expr(expr).startswith("["):
            issues.append(Issue("comparaison invalide", expr))
    context = " ".join(
        " ".join([registry[r].label, registry[r].subject, *(registry[r].period or ())])
        for r in cited
        if r in registry
    )
    allowed = set(_DIGITS.findall(context)) | {p for d in _DIGITS.findall(context) for p in re.split(r"[-.,]", d)}
    bare = PLACEHOLDER.sub(" ", template)
    for token in _DIGITS.findall(bare):
        if token in allowed:
            continue
        issues.append(Issue("nombre non relié", token))
    issues += [Issue("nombre écrit en lettres", m.group(0)) for m in _WORDED_NUMBER.finditer(bare)]
    if comparisons:
        issues += [Issue("comparaison écrite à la main", w) for w in handwritten_comparisons(bare)]
    return issues


@dataclass
class Claim:
    id: str
    kind: str  # constat, tension, alternative, limite, question, condition, cadre
    text: str  # gabarit avec références
    refs: list[str] = field(default_factory=list)

    def all_refs(self) -> list[str]:
        return list(dict.fromkeys(placeholder_ids(self.text) + self.refs))

    def status(self, registry: Registry) -> str:
        refs = [r for r in self.all_refs() if r in registry]
        if not refs:
            return "non étayée"
        # Un résultat calculé à partir d'une hypothèse (portefeuille fictif, seuil, plafond) en hérite.
        deps = [d for r in refs for d in registry[r].inputs.get("depend_de", []) if d in registry]
        return max((registry[r].status for r in refs + deps), key=_RANK.__getitem__)

    def issues(self, registry: Registry) -> list[Issue]:
        out = check_template(self.text, registry, self.refs, comparisons=self.kind not in SECTIONS_SANS_GARDE)
        # Le cadre (simulation, absence de conseil) est une règle du produit, pas un constat.
        if not self.all_refs() and self.kind != "cadre":
            out.append(Issue("affirmation non étayée", self.id))
        return out


def verify_claims(claims: list[Claim], registry: Registry) -> dict:
    per_claim = {c.id: [asdict(i) for i in c.issues(registry)] for c in claims}
    n_refs = sum(len(PLACEHOLDER.findall(c.text)) for c in claims)
    failing = [cid for cid, iss in per_claim.items() if iss]
    return {
        "affirmations": len(claims),
        "valeurs_reliees": n_refs,
        "affirmations_en_echec": failing,
        "problemes": {cid: iss for cid, iss in per_claim.items() if iss},
        "ok": not failing,
    }
