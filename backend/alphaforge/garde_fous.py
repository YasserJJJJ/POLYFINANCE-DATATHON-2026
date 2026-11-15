"""Garde-fous partagés par les agents qui écrivent du texte montré à la personne.

Les motifs sont comparés à un texte en minuscules et SANS accents : « achète », « achete » et « ACHÈTE »
sont la même chose. On vise les formules qui poussent à agir ou promettent un résultat, pas le vocabulaire
neutre (« une vente forcée au mauvais moment », « rien ne garantit » restent permis).
"""
from __future__ import annotations

import re
import unicodedata

MOTS_CONSEIL = {
    "acheter / achète": r"\bachet(?:e|es|ez|er|ons|erais|erait)\b",
    "vends / vendez": r"\bvend(?:s|ez|ons)\b",
    "il faut / tu dois acheter": r"\b(?:il faut|tu dois|tu devrais|vous devriez) (?:acheter|vendre|investir|placer|miser)",
    "je (te) conseille / recommande": r"\b(?:je|nous) (?:te |vous )?(?:conseill|recommand)",
    "garanti": r"(?<!ne )(?<!pas )\bgaranti(?:e|s|es)?\b",
    "sans risque / aucun risque": r"\bsans (?:aucun )?risque\b|\baucun risque\b|\brisque nul\b",
    "fonce / vas-y": r"\bfonce[zs]?\b|\bvas-y\b|\ballez-y\b|\bn'hesite pas\b",
    "c'est le moment": r"c'est le (?:bon )?moment",
    "rapportera / va monter": r"\brapporter(?:a|ait|as)\b|\bmontera\b|\bva (?:monter|remonter|rapporter|exploser)\b",
    "buy / sell": r"\b(?:buy|sell)\b",
}


def sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texte or "") if not unicodedata.combining(c))


def mots_de_conseil(texte: str) -> list[str]:
    """Libellés des formules de conseil trouvées (liste vide = rien à signaler)."""
    bas = " " + sans_accents(str(texte).lower()).replace("’", "'") + " "
    return [nom for nom, motif in MOTS_CONSEIL.items() if re.search(motif, bas)]


# Un rapport ou un nombre écrit en lettres (« presque cinq fois plus faible », « la moitié ») échappe au contrôle
# des chiffres : c'est pourtant un calcul fait par le modèle. On le refuse.
NOMBRE_EN_LETTRES = (r"\b(?:deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|quinze|vingt|trente|quarante|"
                     r"cinquante|soixante|cent|mille)\b")
RAPPORT = re.compile(NOMBRE_EN_LETTRES + r"[^.]{0,20}\bfois\b|\bmoitie\b|\bdouble\b|\btriple\b|\bquart\b|"
                     + NOMBRE_EN_LETTRES + r"\s+(?:pour ?cent|points?|ans|annees|mois|dollars)\b")


def rapport_calcule(texte: str) -> bool:
    """Vrai si le texte contient un rapport ou une quantité écrite en lettres (calcul non fait par le code)."""
    return bool(RAPPORT.search(sans_accents(str(texte).lower())))
