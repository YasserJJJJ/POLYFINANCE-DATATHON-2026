def dollars(n: float) -> str:
    """12345.6 → '12 346 $' (espace insécable fine comme séparateur de milliers)."""
    return f"{n:,.0f}".replace(",", " ") + " $"


def fr(x) -> str:
    """Nombre à la française pour l'affichage : 14.2 → '14,2' (les entiers restent tels quels)."""
    return str(x).replace(".", ",") if isinstance(x, (int, float)) and not isinstance(x, bool) else str(x)
