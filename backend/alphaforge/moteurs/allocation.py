# Provenance : IMPLEMENTATION_IDENTIFIANT-A-ATTRIBUER_2026-11-15(claude-code).zip
# Origine : src/datathon2026/analytics.py
# SHA-256 original : 588ad1ca468e08d233a2b4ec28783e847b45e94729afb356b9f0559583c3e433
# Transfert : 2026-11-15 ; formules inchangées.
def blend(base: dict[str, float], ticker: str, share: float) -> dict[str, float]:
    """Réduit proportionnellement `base` pour consacrer `share` du total à `ticker`."""
    if not 0 <= share <= 1:
        raise ValueError("part attendue entre 0 et 1 (ex. 0.10 pour 10 %)")
    out = {t: w * (1 - share) for t, w in base.items()}
    out[ticker] = out.get(ticker, 0.0) + share
    return {t: w for t, w in out.items() if w > 0}
