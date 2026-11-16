"""Workflow fixe de référence : mêmes outils que l'agent, ordre et textes décidés par le code.

Il sert de base de comparaison (critère de réfutation (a) de D1) et de repli sans AWS.
Règle d'écriture : aucun chiffre ni sens de comparaison écrit à la main ; les valeurs passent par
``{{R-xxxx}}`` et les comparaisons par ``{{cmp:…}}`` ou ``{{cmpabs:…}}``.
"""

from __future__ import annotations

from . import analytics as a
from . import tools as T
from .dossier import Dossier

CADRE = (
    "Simulation sur un profil fictif à partir de données historiques publiques : aucune transaction, "
    "aucun conseil financier personnalisé. Les performances passées ne préjugent pas des résultats futurs."
)


def ref(out: dict, key: str) -> str:
    return "{{" + out[key]["id"] + "}}"


def rid(out: dict, key: str) -> str:
    return out[key]["id"]


def cmp(x: str, y: str, absolute: bool = False) -> str:
    return "{{" + ("cmpabs:" if absolute else "cmp:") + x + ":" + y + "}}"


def label(record_id: str) -> str:
    return "{{" + record_id + ".label}}"


def underwater(index) -> list[list]:
    """Baisse depuis le dernier sommet, série hebdomadaire, pour les graphiques."""
    dd = index / index.cummax() - 1
    return [[t.date().isoformat(), round(float(x), 4)] for t, x in dd.items()]


def robert(scenario: dict | None = None, session: T.Session | None = None) -> Dossier:
    sc = scenario or T.load_scenarios()["robert"]
    s = session or T.Session()
    reg = s.registry
    tk, alt, h = sc["actif_demande"], sc["alternative"], sc["horizon_etude_ans"]
    base = sc["portefeuille_actuel"]
    share = sc["part_declaree"]

    d = s.call("data_manifest", T.data_manifest)
    p = s.call("profile_facts", T.profile_facts, persona=sc["persona"], scenario=sc)
    x = s.call("asset_metrics", T.asset_metrics, ticker=tk, horizon_years=h)
    b = s.call("portfolio_metrics", T.portfolio_metrics, name="portefeuille actuel (fictif)", weights=base, horizon_years=h)
    variants = {
        sh: s.call("portfolio_metrics", T.portfolio_metrics, name=f"portefeuille avec {sh * 100:.0f} % {tk}",
                   weights=a.blend(base, tk, sh), horizon_years=h)
        for sh in sc["parts_etudiees"]
    }
    q = s.call("portfolio_metrics", T.portfolio_metrics, name=f"portefeuille avec {share * 100:.0f} % {alt}",
               weights=a.blend(base, alt, share), horizon_years=h)
    sw = s.call("share_sweep", T.share_sweep, name="portefeuille actuel (fictif)", base=base, ticker=tk, loss_threshold=sc["seuil_perte"])

    D = Dossier("robert-tsla", sc["persona"], sc["demande"], "workflow fixe", reg, s.trace, title=sc.get("titre", ""))
    v = variants[share]
    link = "{{cmpduree:" + rid(x, "duree_sous_sommet") + ":" + rid(p, "horizon_min") + "}}"

    D.add("cadre", CADRE)
    D.add("profil", f"{ref(p, 'nom')} : horizon de {ref(p, 'horizon')}, profil de risque « {ref(p, 'profil_risque')} », objectif : {ref(p, 'objectif')}.")
    D.add("profil", f"Demande : « {ref(p, 'demande')} » ({ref(p, 'origine')}).")
    D.add("profil", f"Non renseignés : {label(rid(p, 'capacite_perte'))} ; {label(rid(p, 'liquidite'))} ; {label(rid(p, 'patrimoine'))}.")

    D.add("constat", f"Volatilité annualisée observée : {ref(x, 'vol')} pour {tk}, contre {ref(b, 'vol')} pour le portefeuille actuel fictif.")
    D.add("constat", f"Pire baisse de {tk} : {ref(x, 'perte_max')}, du {ref(x, 'sommet')} au {ref(x, 'creux')} ; retour au sommet : {ref(x, 'retour_sommet')}, soit {ref(x, 'duree_sous_sommet')} sous le sommet.")
    D.add("constat", f"Rendement 2022 : {ref(x, 'rendement_2022')} pour {tk}, {ref(b, 'rendement_2022')} pour le portefeuille actuel fictif.")

    D.add("tension", f"La durée passée sous le sommet par {tk} ({ref(x, 'duree_sous_sommet')}) {link} l'horizon minimal de Robert ({ref(p, 'horizon_min')}) : une baisse de ce type pourrait ne pas être effacée avant qu'il ait besoin de son capital.")
    D.add("tension", f"Avec {ref(v, f'poids_{tk}')} du portefeuille en {tk}, la pire baisse historique serait {cmp(rid(v, 'perte_max'), rid(b, 'perte_max'), True)} celle du portefeuille actuel ({ref(v, 'perte_max')} contre {ref(b, 'perte_max')}), et {tk} porterait {ref(v, f'risque_{tk}')} du risque total, une part {cmp(rid(v, f'risque_{tk}'), rid(v, f'poids_{tk}'))} son poids.")
    D.add("alternative", f"La même part dans {alt}, FNB diversifié de croissance ({ref(q, f'poids_{alt}')}) : pire baisse {ref(q, 'perte_max')}, {cmp(rid(q, 'perte_max'), rid(v, 'perte_max'), True)} celle de la variante {tk} ; part du risque {ref(q, f'risque_{alt}')}.")

    D.add("question", f"{label(rid(p, 'capacite_perte'))} : non renseignée, c'est l'information qui peut faire basculer la conclusion. Question à poser : quelle baisse de son portefeuille Robert pourrait-il traverser sans retarder sa retraite ?")
    D.add("condition", f"Avec un seuil de perte de démonstration de {ref(sw, 'seuil')}, la part maximale de {tk} compatible avec la pire baisse historique est de {ref(sw, 'part_max')}. Un seuil plus large, ou un horizon plus long, change cette réponse.")
    D.add("condition", f"La demande vient de Robert ({ref(p, 'origine')}) : l'outil montre l'écart et des options, sans acquiescer ni refuser ; la décision lui appartient.")

    D.add("limite", f"L'historique ne contient que {ref(x, 'fenetres_independantes')} fenêtre(s) sans chevauchement de la durée étudiée : la pire fenêtre observée ({ref(x, 'pire_fenetre')}) décrit le passé, pas un risque futur garanti.")
    D.add("limite", f"Conversion USD → CAD au dernier taux Banque du Canada connu (écart maximal {ref(d, 'fx_age_max')}). {label(rid(d, 'biais_univers'))} : {ref(d, 'biais_univers')}.")

    D.profile_card = [("Profil de risque", rid(p, "profil_risque")), ("Horizon", rid(p, "horizon")), ("Objectif", rid(p, "objectif")),
                      ("Expérience", rid(p, "experience")), ("Origine de la demande", rid(p, "origine"))]
    D.highlights = [
        {"libelle": f"Pire baisse de {tk}", "valeur": rid(x, "perte_max"), "detail": f"du {ref(x, 'sommet')} au {ref(x, 'creux')}"},
        {"libelle": "Temps passé sous le sommet", "valeur": rid(x, "duree_sous_sommet"), "detail": f"horizon minimal de Robert : {ref(p, 'horizon_min')}"},
        {"libelle": f"Part du risque portée par {tk}", "valeur": rid(v, f"risque_{tk}"), "detail": f"pour un poids de {ref(v, f'poids_{tk}')} (hypothèse)"},
        {"libelle": f"Part maximale de {tk} sous le seuil", "valeur": rid(sw, "part_max"), "detail": f"seuil de perte de démonstration : {ref(sw, 'seuil')}"},
    ]
    rows = [{"nom": "Ne rien changer (portefeuille actuel)", "cellules": [None, rid(b, "vol"), rid(b, "perte_max"), rid(b, "rendement_2022"), None]}]
    for sh, out in variants.items():
        rows.append({"nom": f"Ajouter {tk}", "cellules": [rid(out, f"poids_{tk}"), rid(out, "vol"), rid(out, "perte_max"), rid(out, "rendement_2022"), rid(out, f"risque_{tk}")]})
    rows.append({"nom": f"Ajouter {alt} (FNB diversifié)", "cellules": [rid(q, f"poids_{alt}"), rid(q, "vol"), rid(q, "perte_max"), rid(q, "rendement_2022"), rid(q, f"risque_{alt}")]})
    D.tables.append({"titre": "Options comparées sur la période observée (portefeuilles fictifs, en CAD)",
                     "colonnes": ["Part de l'actif ajouté", "Volatilité annualisée", "Pire baisse", "Rendement 2022", "Part du risque de l'actif ajouté"],
                     "lignes": rows})

    m = s.market
    D.charts.append({
        "titre": f"Baisse depuis le plus haut précédent : {tk} et portefeuilles fictifs",
        "sous_titre": "série hebdomadaire en dollars canadiens",
        "mise_en_evidence": tk,
        "type": "ligne",
        "unite": "pct",
        "series": {
            tk: underwater(m.weekly_values[tk].dropna()),
            f"Portefeuille avec {share * 100:.0f} % {tk}": underwater(a.portfolio(m, a.blend(base, tk, share)).index),
            "Portefeuille actuel (fictif)": underwater(a.portfolio(m, base).index),
        },
        "sources": [rid(x, "perte_max"), rid(v, "perte_max"), rid(b, "perte_max")],
        "note": f"La pire baisse de {tk} citée plus haut est mesurée sur la série quotidienne ; sur cette série hebdomadaire, le creux peut paraître un peu moins profond.",
        "etiquettes": {f"Portefeuille avec {share * 100:.0f} % {tk}": f"Avec {share * 100:.0f} % {tk}", "Portefeuille actuel (fictif)": "Actuel (fictif)"},
    })

    D.summary = (
        f"{tk} a perdu jusqu'à {ref(x, 'perte_max')} et est resté {ref(x, 'duree_sous_sommet')} sous son sommet, une durée qui {link} "
        f"l'horizon minimal de Robert ({ref(p, 'horizon_min')}). À {ref(v, f'poids_{tk}')} du portefeuille, {tk} porterait {ref(v, f'risque_{tk}')} "
        f"du risque. {label(rid(p, 'capacite_perte'))} : non renseignée, c'est la donnée qui peut changer la conclusion."
    )
    return D


def amira(scenario: dict | None = None, session: T.Session | None = None) -> Dossier:
    sc = scenario or T.load_scenarios()["amira"]
    s = session or T.Session()
    reg = s.registry
    h = sc["horizon_etude_ans"]
    tech, cry = "Technologie", "Cryptoactifs"

    d = s.call("data_manifest", T.data_manifest)
    p = s.call("profile_facts", T.profile_facts, persona=sc["persona"], scenario=sc)
    pp = s.call("portfolio_metrics", T.portfolio_metrics, name="portefeuille proposé (fictif)", weights=sc["portefeuille_propose"], horizon_years=h)
    rho = s.call("correlation", T.correlation, t1="BTC-USD", t2="ETH-USD")
    sw = s.call("diversification_sweep", T.diversification_sweep, name="portefeuille proposé (fictif)", base=sc["portefeuille_propose"],
                sleeve=sc["panier_diversification"], cap=sc["plafond_risque_groupe"])
    cap = reg.add("R", "Plafond de part du risque par groupe", sc["plafond_risque_groupe"], "pct", "hypothèse", "scénario de démonstration",
                  subject="Amira").id
    gr = pp["_brut"]["groupes_risque"]
    both = reg.add("R", "Part du risque des groupes Technologie et Cryptoactifs (portefeuille proposé)", gr.get(tech, 0) + gr.get(cry, 0),
                   "pct", "mesuré", T.ORIGIN, subject="portefeuille proposé (fictif)",
                   inputs={"somme_de": [rid(pp, f"groupe_risque_{tech}"), rid(pp, f"groupe_risque_{cry}")]}).id
    va = None
    if sw["_brut"]["poids"] is not None:
        va = s.call("portfolio_metrics", T.portfolio_metrics, name="variante au plafond (fictive)", weights=sw["_brut"]["poids"], horizon_years=h)

    D = Dossier("amira-croissance", sc["persona"], sc["demande"], "workflow fixe", reg, s.trace, title=sc.get("titre", ""))
    top = max(gr, key=gr.get)

    D.add("cadre", CADRE)
    D.add("profil", f"{ref(p, 'nom')} : horizon de {ref(p, 'horizon')}, profil de risque « {ref(p, 'profil_risque')} », objectif : {ref(p, 'objectif')}.")
    D.add("profil", f"Préférence explicite : {ref(p, 'preference_4')}.")
    D.add("profil", f"Demande : « {ref(p, 'demande')} ».")

    for g in (tech, cry):
        if f"groupe_risque_{g}" in pp:
            D.add("constat", f"Groupe {g} : {ref(pp, f'groupe_poids_{g}')} du poids et {ref(pp, f'groupe_risque_{g}')} du risque, une part du risque {cmp(rid(pp, f'groupe_risque_{g}'), rid(pp, f'groupe_poids_{g}'))} sa part du poids.")
    D.add("constat", f"Ensemble, ces deux groupes portent {{{{{both}}}}} du risque ; les trois premières lignes en portent {ref(pp, 'risque_top3')}.")
    D.add("constat", f"Corrélation hebdomadaire Bitcoin / Ether : {ref(rho, 'correlation')} ; deux cryptoactifs ne font pas deux paris indépendants.")
    D.add("constat", f"Profil offensif : pire baisse historique du portefeuille proposé {ref(pp, 'perte_max')}, rendement 2022 {ref(pp, 'rendement_2022')}. L'analyse n'impose pas de seuil de perte ; elle vérifie la diversification demandée.")

    D.add("tension", f"Plafond de démonstration : {{{{{cap}}}}} du risque par groupe. Groupe le plus lourd : {top}, avec {ref(pp, f'groupe_risque_{top}')}, une part {cmp(rid(pp, f'groupe_risque_{top}'), cap)} ce plafond.")
    if va is not None:
        D.add("alternative", f"Règle de comparaison : déplacer la plus petite part possible ({ref(sw, 'part_deplacee')}) vers un panier hors technologie ({ref(sw, 'panier')}) pour respecter le plafond.")
        hyp = (rid(sw, "panier"), rid(sw, "part_deplacee"))
        for g in (tech, cry):
            if f"groupe_risque_{g}" in va:
                D.add("alternative", f"Variante au plafond, groupe {g} : {ref(va, f'groupe_risque_{g}')} du risque, contre {ref(pp, f'groupe_risque_{g}')} dans le portefeuille proposé.", *hyp)
        D.add("alternative", f"Contrepartie observée : rendement annualisé de la variante {ref(va, 'cagr')}, une valeur {cmp(rid(va, 'cagr'), rid(pp, 'cagr'))} celle du portefeuille proposé ({ref(pp, 'cagr')}) ; pire baisse {ref(va, 'perte_max')}, {cmp(rid(va, 'perte_max'), rid(pp, 'perte_max'), True)} {ref(pp, 'perte_max')}.", *hyp)
    else:
        D.add("alternative", f"Aucune part déplacée vers le panier ({ref(sw, 'panier')}) ne permet de respecter le plafond ({ref(sw, 'part_deplacee')}).")

    D.add("question", f"{label(rid(p, 'liquidite'))} et {label(rid(p, 'patrimoine'))} : non renseignés. Un placement déjà important chez son employeur technologique changerait l'analyse de concentration.")
    D.add("condition", f"Le constat dépend du plafond retenu ({{{{{cap}}}}}) et du regroupement des actifs (fichier de configuration) ; un autre regroupement peut déplacer la conclusion.")
    D.add("limite", f"L'horizon minimal d'Amira ({ref(p, 'horizon_min')}) est une durée {cmp(rid(p, 'horizon_min'), rid(d, 'duree_echantillon'))} celle de l'échantillon de prix ({ref(d, 'duree_echantillon')}) : les mesures décrivent la période observée, pas l'horizon visé.", rid(pp, "cagr"))
    D.add("limite", f"QQQ et SPY sont des FNB indiciels dont la composition n'est pas incluse : leur chevauchement avec les titres détenus directement n'est pas mesuré. Conversion USD → CAD au dernier taux connu (écart maximal {ref(d, 'fx_age_max')}). {label(rid(d, 'biais_univers'))} : {ref(d, 'biais_univers')}.")

    D.profile_card = [("Profil de risque", rid(p, "profil_risque")), ("Horizon", rid(p, "horizon")), ("Objectif", rid(p, "objectif")),
                      ("Expérience", rid(p, "experience")), ("Origine de la demande", rid(p, "origine"))]
    D.highlights = [
        {"libelle": "Risque porté par la technologie et la crypto", "valeur": both,
         "detail": f"pour {ref(pp, f'groupe_poids_{tech}')} et {ref(pp, f'groupe_poids_{cry}')} du poids"},
        {"libelle": "Pire baisse historique du portefeuille proposé", "valeur": rid(pp, "perte_max"), "detail": f"rendement 2022 : {ref(pp, 'rendement_2022')}"},
        {"libelle": "Part à déplacer pour respecter le plafond", "valeur": rid(sw, "part_deplacee"),
         "detail": f"plafond de démonstration : {{{{{cap}}}}} du risque par groupe"},
        {"libelle": "Corrélation Bitcoin / Ether", "valeur": rid(rho, "correlation"), "detail": "rendements hebdomadaires"},
    ]
    if va is not None:
        cols = ["Rendement annualisé", "Volatilité annualisée", "Pire baisse", "Rendement 2022", "Risque Technologie", "Risque Cryptoactifs"]
        keys = ["cagr", "vol", "perte_max", "rendement_2022", f"groupe_risque_{tech}", f"groupe_risque_{cry}"]
        D.tables.append({"titre": "Portefeuille proposé et variante au plafond (fictifs, en CAD)", "colonnes": cols, "lignes": [
            {"nom": "Portefeuille proposé", "cellules": [rid(pp, k) if k in pp else None for k in keys]},
            {"nom": "Variante au plafond", "cellules": [rid(va, k) if k in va else None for k in keys]},
        ]})

    groups = sorted(gr, key=gr.get, reverse=True)
    series = {
        "Poids, portefeuille proposé": [[g, round(pp["_brut"]["groupes_poids"].get(g, 0.0), 4)] for g in groups],
        "Risque, portefeuille proposé": [[g, round(gr[g], 4)] for g in groups],
    }
    sources = [rid(pp, f"groupe_risque_{g}") for g in groups]
    if va is not None:
        series["Risque, variante au plafond"] = [[g, round(va["_brut"]["groupes_risque"].get(g, 0.0), 4)] for g in groups]
        sources += [rid(va, f"groupe_risque_{g}") for g in groups if f"groupe_risque_{g}" in va]
    D.charts.append({"titre": "Part du poids et part du risque par groupe d'actifs", "type": "barres", "unite": "pct",
                     "mise_en_evidence": "Risque, portefeuille proposé",
                     "note": "Part du risque : contribution de chaque groupe à la variance des rendements hebdomadaires. Regroupement selon config/scenarios.toml.",
                     "series": series, "sources": sources, "repere": {"valeur": sc["plafond_risque_groupe"], "libelle": "plafond de démonstration"}})

    D.summary = (
        f"Les groupes Technologie et Cryptoactifs portent ensemble {{{{{both}}}}} du risque du portefeuille proposé, "
        f"et les trois premières lignes {ref(pp, 'risque_top3')}. "
        + (
            f"Déplacer {ref(sw, 'part_deplacee')} vers un panier hors technologie suffit à respecter le plafond de démonstration ({{{{{cap}}}}}), "
            f"pour une pire baisse historique de {ref(va, 'perte_max')} contre {ref(pp, 'perte_max')}."
            if va is not None
            else f"Aucune part déplacée ne respecte le plafond de démonstration ({{{{{cap}}}}})."
        )
    )
    return D


WORKFLOWS = {"robert": robert, "amira": amira}
