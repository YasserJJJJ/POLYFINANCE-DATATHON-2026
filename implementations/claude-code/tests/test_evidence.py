"""Vérificateur d'explications : il doit détecter les fautes injectées (R04, mécanisme 3)."""

from datathon2026.evidence import Claim, Registry, check_template, format_value


def reg():
    r = Registry()
    r.add("R", "Rendement 2022 TSLA", -0.6261, "pct", "mesuré", "test", period=("2021-12-31", "2022-12-31"))  # R-0001
    r.add("R", "Seuil", -0.15, "pct", "hypothèse", "test")  # R-0002
    r.add("P", "Capacité de perte", None, "text", "inconnu", "test")  # P-0001
    r.add("R", "Durée", 2.9, "years", "mesuré", "test")  # R-0003
    r.add("R", "Perte A", -0.1534, "pct", "mesuré", "test")  # R-0004
    r.add("R", "Perte B", -0.1231, "pct", "mesuré", "test")  # R-0005
    return r


def kinds(issues):
    return [i.kind for i in issues]


def test_clean_template_passes_and_renders():
    r = reg()
    t = "En 2022, TSLA a rendu {{R-0001}}."
    assert check_template(t, r) == []
    assert r.render(t) == "En 2022, TSLA a rendu −62,6 %."


def test_handwritten_number_is_flagged():
    assert kinds(check_template("TSLA a rendu -62,6 % en 2022.", reg())) == ["nombre non relié", "nombre non relié"]


def test_quantity_written_in_words_is_flagged_but_a_plain_count_is_not():
    r = reg()
    for t in ("Une part de dix pour cent : {{R-0004}}.", "Un horizon de quinze ans : {{R-0003}}.", "La moitié du risque : {{R-0004}}.",
              "Le double du seuil {{R-0002}}.", "Vingt-cinq points : {{R-0004}}."):
        assert kinds(check_template(t, r)) == ["nombre écrit en lettres"], t
    for t in ("Les deux fonds perdent {{R-0004}} et {{R-0005}}.", "Trois options sont comparées : {{R-0004}}.", "Sur un an : {{R-0001}}."):
        assert check_template(t, r) == [], t


def test_year_allowed_only_if_in_cited_record():
    r = reg()
    assert check_template("En 2022 : {{R-0001}}", r) == []
    assert kinds(check_template("En 2023 : {{R-0001}}", r)) == ["nombre non relié"]


def test_unknown_and_malformed_references_are_flagged():
    r = reg()
    assert kinds(check_template("{{R-0999}}", r)) == ["référence inconnue", "comparaison invalide"]
    assert "référence mal formée" in kinds(check_template("{{R-1}}", r))


def test_comparison_direction_is_computed():
    r = reg()
    assert r.render("{{cmpabs:R-0004:R-0005}}") == "plus forte que"
    assert r.render("{{cmpabs:R-0005:R-0004}}") == "moins forte que"
    assert r.render("{{cmp:R-0004:R-0005}}") == "inférieure à"
    assert r.render("{{cmp:R-0004:R-0004}}") == "égale à"


def test_computed_comparison_agrees_with_the_following_word():
    r = reg()
    assert r.render("une baisse {{cmp:R-0004:R-0005}} le seuil") == "une baisse inférieure au seuil"
    assert r.render("une baisse {{cmp:R-0004:R-0005}} les seuils") == "une baisse inférieure aux seuils"
    assert r.render("une baisse {{cmp:R-0004:R-0005}} à son poids") == "une baisse inférieure à son poids"  # « à » répété
    assert r.render("une baisse {{cmp:R-0004:R-0005}} au seuil") == "une baisse inférieure au seuil"
    assert r.render("une baisse {{cmpabs:R-0004:R-0005}} une autre") == "une baisse plus forte qu'une autre"
    assert r.render("{{cmpabs:R-0004:R-0005}} {{R-0005}}") == "plus forte que −12,3 %"


def test_computed_comparison_agrees_in_gender_with_the_qualified_noun():
    r = reg()
    assert r.render("ESGV affiche un rendement {{cmp:R-0004:R-0005}} celui de SPY") == "ESGV affiche un rendement inférieur à celui de SPY"
    assert r.render("Le rendement est une valeur {{cmp:R-0004:R-0005}} celle de SPY") == "Le rendement est une valeur inférieure à celle de SPY"
    assert r.render("une part dans le portefeuille {{cmp:R-0004:R-0005}} son poids") == "une part dans le portefeuille inférieure à son poids"
    assert r.render("Le fonds recule. La baisse d'un portefeuille est {{cmpabs:R-0004:R-0005}} le seuil") == "Le fonds recule. La baisse d'un portefeuille est plus forte que le seuil"
    assert r.render("un recul {{cmpabs:R-0004:R-0005}} un autre") == "un recul plus fort qu'un autre"
    assert (r.render("un rendement {{cmp:R-0004:R-0005}} celui de SPY, avec une pire baisse {{cmpabs:R-0004:R-0005}} celle de SPY")
            == "un rendement inférieur à celui de SPY, avec une pire baisse plus forte que celle de SPY")
    assert r.render("Dans ce portefeuille, la part de TSLA est {{cmp:R-0004:R-0005}} son poids") == "Dans ce portefeuille, la part de TSLA est inférieure à son poids"
    assert r.render("Le rendement annualisé d'ESGV est {{cmp:R-0004:R-0005}} celui de SPY") == "Le rendement annualisé d'ESGV est inférieur à celui de SPY"
    assert r.render("pire baisse {{R-0004}}, {{cmpabs:R-0004:R-0005}} {{R-0005}}") == "pire baisse −15,3 %, plus forte que −12,3 %"


def test_duration_comparison_is_graded_on_the_ratio():
    r = reg()
    for years in (3, 2, 10, 5):  # P-0002 … P-0005
        r.add("P", "Horizon minimal", years, "years", "déclaré", "test")
    assert r.render("{{cmpduree:R-0003:P-0002}} l'horizon") == "atteint presque l'horizon"
    assert r.render("{{cmpduree:R-0003:P-0003}} l'horizon") == "atteint ou dépasse l'horizon"
    assert r.render("{{cmpduree:R-0003:P-0004}} le terme") == "reste nettement inférieure au terme"
    assert r.render("{{cmpduree:R-0003:P-0005}} le terme") == "représente une part importante du terme"
    assert kinds(check_template("{{cmpduree:R-0003:R-0004}}", r)) == ["comparaison invalide"]  # années contre pourcentage


def test_handwritten_comparison_is_flagged_except_in_hypothetical_sections():
    r = reg()
    for t in ("{{R-0004}} dépasse le seuil {{R-0002}}.", "Une baisse plus forte que {{R-0005}}.", "Le rendement est plus élevé : {{R-0001}}.",
              "{{R-0004}}, au-delà du seuil {{R-0002}}.", "La part monte à {{R-0004}}.", "Une valeur supérieure à {{R-0002}}.",
              "SPY a bougé davantage que XBB.TO : {{R-0004}}."):
        assert kinds(check_template(t, r)) == ["comparaison écrite à la main"], t
    for t in ("{{R-0004}} contre {{R-0005}}.", "Une baisse {{cmpabs:R-0004:R-0005}} {{R-0005}}.", "Le groupe le plus lourd : {{R-0001}}.",
              "La pire baisse est de {{R-0004}}."):
        assert check_template(t, r) == [], t
    # une proposition conditionnelle formule une hypothèse ; « même si » et la proposition principale affirment
    assert check_template("ESGV, si le filtre compte davantage pour Mateo que l'écart de rendement : {{R-0004}}.", r) == []
    assert kinds(check_template("Même si la baisse est plus forte que {{R-0005}}, elle reste de {{R-0004}}.", r)) == ["comparaison écrite à la main"]
    assert kinds(check_template("Si le seuil est large, la baisse reste plus forte que {{R-0005}}.", r)) == ["comparaison écrite à la main"]
    assert Claim("A-1", "condition", "Un seuil plus large que {{R-0002}} change la réponse.").issues(r) == []
    assert kinds(Claim("A-2", "constat", "Un seuil plus large que {{R-0002}}.").issues(r)) == ["comparaison écrite à la main"]


def test_comparison_between_incompatible_units_is_invalid():
    r = reg()
    assert kinds(check_template("{{cmp:R-0003:R-0004}}", r)) == ["comparaison invalide"]


def test_claim_status_is_weakest_reference_and_unsupported_claim_flagged():
    r = reg()
    assert Claim("A-1", "constat", "{{R-0001}} contre {{R-0002}}").status(r) == "hypothèse"
    assert Claim("A-2", "question", "{{P-0001.label}} inconnue").status(r) == "inconnu"
    assert kinds(Claim("A-3", "constat", "TSLA est risqué.").issues(r)) == ["affirmation non étayée"]
    assert Claim("A-4", "cadre", "Simulation, aucun conseil.").issues(r) == []


def test_formatting():
    assert format_value(0.0, "pct") == "0,0 %"
    assert format_value(-0.00004, "pct") == "0,0 %"  # pas de « −0,0 »
    assert format_value(1067, "days") == "1 067 jours"
    assert format_value(None, "pct") == "non disponible"


def test_status_inherits_hypothesis_dependencies():
    r = reg()
    r["R-0003"].inputs["depend_de"] = ["R-0002"]  # durée calculée sous une hypothèse de seuil
    assert Claim("A-5", "constat", "{{R-0003}}").status(r) == "hypothèse"
