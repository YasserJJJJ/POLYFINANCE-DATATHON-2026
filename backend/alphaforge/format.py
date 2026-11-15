def dollars(n: float) -> str:
    """12345.6 → '12 346 $' (espace insécable fine comme séparateur de milliers)."""
    return f"{n:,.0f}".replace(",", " ") + " $"
