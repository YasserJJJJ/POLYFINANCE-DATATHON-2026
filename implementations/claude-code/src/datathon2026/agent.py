"""Agent orchestrateur sur Amazon Bedrock (API Converse, outils exécutés dans notre code).

Décision D2 : la boucle est écrite ici pour garder le contrôle du registre de preuves. Le modèle
choisit les outils, rédige le dossier et choisit ce qui est montré (chiffres clés, tableau,
graphique) ; il ne calcule rien. Son dossier est soumis via l'outil `soumettre_dossier`, contrôlé
par le vérificateur ; en cas d'échec, les problèmes lui sont renvoyés (deux corrections au plus).
Chaque appel Bedrock laisse son RequestId dans le dossier.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

from . import analytics as a
from . import tools as T
from .dossier import SECTIONS, Dossier
from .workflow import underwater

DEFAULT_MODEL = os.environ.get("AF_BEDROCK_MODEL", "global.anthropic.claude-sonnet-5-5")
DEFAULT_REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"  # région du compte Workshop Studio du datathon
# Profil AWS nommé (configuré par le porteur avec `aws configure sso --profile alphaforge`, etc.).
# Les identifiants restent dans la configuration AWS locale ; le code ne les lit pas lui-même.
DEFAULT_PROFILE = os.environ.get("AF_AWS_PROFILE") or os.environ.get("AWS_PROFILE") or "alphaforge"
MAX_TURNS = 16
MAX_FIXES = 2
MAX_TOKENS = 8192  # un dossier complet approche 4 000 jetons : une sortie tronquée ferait perdre l'exécution
# Nom d'outil vu par l'agent → nom de l'outil déterministe inscrit dans la trace.
TOOL_NAMES = {"profil": "profile_facts", "sources_donnees": "data_manifest", "metriques_actif": "asset_metrics",
              "metriques_portefeuille": "portfolio_metrics", "balayage_part": "share_sweep",
              "balayage_diversification": "diversification_sweep", "correlation": "correlation"}
PROFILE_CARD = [("Profil de risque", "Profil de risque déclaré"), ("Horizon", "Horizon de placement"), ("Objectif", "Objectif"),
                ("Expérience", "Expérience en placement"), ("Origine de la demande", "Origine de la demande")]


def aws_session(profile: str | None = DEFAULT_PROFILE, region: str = DEFAULT_REGION):
    import boto3
    from botocore.exceptions import ProfileNotFound

    try:
        return boto3.Session(profile_name=profile, region_name=region)
    except ProfileNotFound:
        return boto3.Session(region_name=region)  # repli : chaîne d'identifiants par défaut


WEIGHTS = {"type": "object", "additionalProperties": {"type": "number"}, "description": "ticker → poids (somme 1, sans levier)"}
RECORD_ID = {"type": "string", "description": "identifiant d'enregistrement, ex. R-0012"}

TOOL_SPECS: list[dict] = [
    {"name": "lister_actifs", "description": "Univers disponible : ticker, nom, classe, devise, secteur.",
     "schema": {"type": "object", "properties": {}}},
    {"name": "profil", "description": "Inscrit au registre les faits du profil fictif (déclarés, inconnus) et la demande.",
     "schema": {"type": "object", "properties": {"persona": {"type": "string", "enum": ["amira", "mateo", "robert"]}}, "required": ["persona"]}},
    {"name": "sources_donnees", "description": "Provenance et limites des données : empreintes des fichiers, fraîcheur du taux de change, durée de l'échantillon, biais de l'univers.",
     "schema": {"type": "object", "properties": {}}},
    {"name": "metriques_actif", "description": "Historique d'un actif en CAD : rendement annualisé, volatilité, pire baisse et sa durée, 2022, pire fenêtre de N ans.",
     "schema": {"type": "object", "properties": {"ticker": {"type": "string"}, "horizon_ans": {"type": "number"}}, "required": ["ticker"]}},
    {"name": "metriques_portefeuille", "description": "Portefeuille fictif rééquilibré chaque semaine : volatilité, pire baisse, 2022, contributions au risque par actif et par groupe.",
     "schema": {"type": "object", "properties": {"nom": {"type": "string"}, "poids": WEIGHTS, "horizon_ans": {"type": "number"}}, "required": ["nom", "poids"]}},
    {"name": "melange", "description": "Calcule les poids obtenus en consacrant une part d'un portefeuille à un actif (réduction proportionnelle du reste). N'inscrit rien.",
     "schema": {"type": "object", "properties": {"base": WEIGHTS, "ticker": {"type": "string"}, "part": {"type": "number", "description": "entre 0 et 1, ex. 0.10"}},
                "required": ["base", "ticker", "part"]}},
    {"name": "balayage_part", "description": "Part maximale d'un actif ajoutable à un portefeuille sans que sa pire baisse historique dépasse un seuil.",
     "schema": {"type": "object", "properties": {"nom": {"type": "string"}, "base": WEIGHTS, "ticker": {"type": "string"},
                                                 "seuil_perte": {"type": "number", "description": "négatif, ex. -0.15 pour une baisse de 15 %"}},
                "required": ["nom", "base", "ticker", "seuil_perte"]}},
    {"name": "balayage_diversification", "description": "Plus petite part à déplacer vers un panier pour qu'aucun groupe ne dépasse un plafond de part du risque ; renvoie les poids obtenus.",
     "schema": {"type": "object", "properties": {"nom": {"type": "string"}, "base": WEIGHTS, "panier": WEIGHTS,
                                                 "plafond": {"type": "number", "description": "entre 0 et 1, ex. 0.5"}},
                "required": ["nom", "base", "panier", "plafond"]}},
    {"name": "correlation", "description": "Corrélation des rendements hebdomadaires de deux actifs.",
     "schema": {"type": "object", "properties": {"t1": {"type": "string"}, "t2": {"type": "string"}}, "required": ["t1", "t2"]}},
    {"name": "soumettre_dossier", "description": "Soumet le dossier final. Il est vérifié automatiquement ; en cas de problème, corrigez et soumettez à nouveau.",
     "schema": {"type": "object", "properties": {
         "titre": {"type": "string"},
         "resume": {"type": "string", "description": "deux ou trois phrases à références"},
         "affirmations": {"type": "array", "items": {"type": "object", "properties": {
             "section": {"type": "string", "enum": list(SECTIONS)},
             "texte": {"type": "string"},
             "references": {"type": "array", "items": {"type": "string"}}}, "required": ["section", "texte"]}},
         "chiffres_cles": {"type": "array", "maxItems": 4, "description": "valeurs qui portent la conclusion", "items": {"type": "object", "properties": {
             "libelle": {"type": "string", "description": "sans chiffre"}, "valeur": RECORD_ID,
             "detail": {"type": "string", "description": "courte précision à références"}}, "required": ["libelle", "valeur"]}},
         "tableau": {"type": "object", "description": "options comparées : une ligne par option, une colonne par mesure", "properties": {
             "titre": {"type": "string"}, "colonnes": {"type": "array", "items": {"type": "string"}},
             "lignes": {"type": "array", "items": {"type": "object", "properties": {
                 "nom": {"type": "string"}, "cellules": {"type": "array", "items": {"type": ["string", "null"]}}}, "required": ["nom", "cellules"]}}},
             "required": ["titre", "colonnes", "lignes"]},
         "graphique": {"type": "object", "description": "tracé par le code à partir des données", "properties": {
             "type": {"type": "string", "enum": ["baisses", "groupes"]},
             "series": {"type": "array", "items": {"type": "string"}, "description": "tickers ou noms de portefeuilles déjà analysés"},
             "mise_en_evidence": {"type": "string"}}, "required": ["type", "series"]}},
         "required": ["titre", "resume", "affirmations"]}},
]

SYSTEM = """Tu es l'orchestrateur d'AlphaForge, un laboratoire de décision d'investissement en SIMULATION sur des profils fictifs.
Tu n'exécutes aucune transaction et tu ne donnes pas de conseil personnalisé.

Méthode :
1. Inscris le profil (outil `profil`) et la provenance des données (outil `sources_donnees`). Distingue capacité de perte, tolérance, horizon et liquidité ; ne déduis jamais un portefeuille de l'âge ou d'une étiquette de risque.
2. Choisis les outils utiles à CETTE demande, et seulement ceux-là : une demande d'explication ou de comparaison d'actifs n'appelle pas une allocation. Les hypothèses de démonstration fournies peuvent être utilisées ; présente-les comme hypothèses. S'il manque un portefeuille, un seuil ou un plafond dont l'analyse a besoin, pose une hypothèse explicite et dis dans la section cadre qu'elle vient de toi et qu'elle est modifiable.
3. Si la demande est incohérente avec le profil, ne l'approuve pas et ne la refuse pas : montre l'écart chiffré, propose des options comparées, indique l'information décisive manquante et ce qui ferait changer la conclusion.
4. Termine par `soumettre_dossier`.

Règles d'écriture, contrôlées automatiquement :
- N'écris AUCUN chiffre toi-même, ni en chiffres ni en lettres (« dix pour cent », « quinze ans », « la moitié », « le double » sont refusés). Chaque valeur passe par une référence aux enregistrements renvoyés par les outils : {{R-0012}} (valeur), {{P-0003.label}} (libellé).
- N'écris jamais à la main le sens d'une comparaison. Hors sections question et condition, le vérificateur refuse « supérieur », « inférieur », « meilleur », « dépasse », « excède », « au-delà », « au-dessus », « en dessous », « plus … que », « moins … que », « davantage que », « plus élevé », « moins risqué », « augmente », « diminue », « monte », « recule ». Écris à la place :
  · {{cmp:R-0001:R-0002}} → « supérieure à / inférieure à / égale à », après un nom féminin (« une part », « une valeur ») ;
  · {{cmpabs:R-0001:R-0002}} → « plus forte que / moins forte que / aussi forte que », pour des pertes, après « une baisse » ;
  · {{cmpduree:R-0001:P-0002}} → « atteint ou dépasse / atteint presque / représente une part importante de / reste nettement inférieure à », pour une durée face à un horizon (« cette durée {{cmpduree:R-0001:P-0002}} l'horizon minimal ») ;
  · ou une tournure neutre : « X contre Y », « X pour un poids de Y ».
  Les deux enregistrements comparés ont la même unité. L'accord avec le mot suivant est fait par le code : écris « {{cmp:R-0001:R-0002}} le plafond », jamais « à le » ni « au ».
- Décris chaque valeur avec le sens exact de son libellé : un « Rendement 2022 » n'est pas une « pire année » ; une part du risque de QQQ n'est pas « la technologie ».
- Une information inconnue se cite par son libellé seul, en début de phrase ou après deux-points : « {{P-0010.label}} : non renseignée. » Ne cite pas sa valeur et ne répète pas le libellé en mots.
- Une valeur textuelle (objectif, préférence, demande) est une citation : place-la après deux-points ou entre guillemets « … », sans la fondre dans ta phrase.
- Quand une affirmation dépend d'une hypothèse (seuil, plafond, portefeuille fictif), cite aussi l'enregistrement de cette hypothèse.
- Une année n'est permise que si elle figure dans le libellé ou la période d'un enregistrement cité.
- N'invoque aucun événement, aucune actualité ni aucune information absente du registre.
- Sections : cadre, profil, constat, tension, alternative, question, condition, limite. Chaque affirmation (sauf cadre) cite au moins un enregistrement. Dans limite, cite les limites des données renvoyées par `sources_donnees` (fraîcheur du change, durée de l'échantillon, biais de l'univers).
- Français clair, phrases courtes, compréhensibles par un non-spécialiste.

Présentation, contrôlée de la même façon :
- `chiffres_cles` : quatre valeurs au plus, celles qui portent la conclusion ; `libelle` sans chiffre, `valeur` = identifiant d'enregistrement, `detail` = courte précision à références.
- `tableau` : les options comparées ; une ligne par option, une colonne par mesure, cellules = identifiants d'enregistrement (ou null).
- `graphique` : `baisses` (courbes de baisse depuis le sommet ; séries = tickers ou noms de portefeuilles déjà analysés, trois au plus) ou `groupes` (poids et part du risque par groupe ; séries = un ou deux noms de portefeuilles analysés)."""


def _strip(out: Any) -> Any:
    if isinstance(out, dict):
        return {k: _strip(v) for k, v in out.items() if not k.startswith("_")}
    return out


class BedrockAgent:
    def __init__(self, client=None, model: str = DEFAULT_MODEL, region: str = DEFAULT_REGION, session: T.Session | None = None,
                 profile: str | None = DEFAULT_PROFILE):
        if client is None:
            client = aws_session(profile, region).client("bedrock-runtime")
        self.client, self.model, self.region = client, model, region
        self.session = session or T.Session()
        self.requests: list[dict] = []

    # ------------------------------------------------------------ outils
    def _run_tool(self, name: str, args: dict) -> dict:
        s = self.session
        if name == "lister_actifs":
            u = s.market.universe.reset_index()[["ticker", "name", "asset_class", "currency", "sector"]]
            return {"actifs": u.to_dict(orient="records"), "groupes": s.groups}
        if name == "profil":
            return _strip(s.call("profile_facts", T.profile_facts, persona=args["persona"], scenario=self._scenario))
        if name == "sources_donnees":
            return _strip(s.call("data_manifest", T.data_manifest))
        if name == "metriques_actif":
            return _strip(s.call("asset_metrics", T.asset_metrics, ticker=args["ticker"], horizon_years=args.get("horizon_ans", 3)))
        if name == "metriques_portefeuille":
            return _strip(s.call("portfolio_metrics", T.portfolio_metrics, name=args["nom"], weights=args["poids"], horizon_years=args.get("horizon_ans", 3)))
        if name == "melange":
            return {"poids": {t: round(w, 6) for t, w in a.blend(args["base"], args["ticker"], args["part"]).items()}}
        if name == "balayage_part":
            return _strip(s.call("share_sweep", T.share_sweep, name=args["nom"], base=args["base"], ticker=args["ticker"], loss_threshold=args["seuil_perte"]))
        if name == "balayage_diversification":
            out = s.call("diversification_sweep", T.diversification_sweep, name=args["nom"], base=args["base"], sleeve=args["panier"], cap=args["plafond"])
            res = _strip(out)
            res["poids_obtenus"] = out["_brut"]["poids"]
            return res
        if name == "correlation":
            return _strip(s.call("correlation", T.correlation, t1=args["t1"], t2=args["t2"]))
        raise KeyError(f"outil inconnu : {name}")

    def _converse(self, messages: list) -> dict:
        t0 = time.perf_counter()
        resp = self.client.converse(
            modelId=self.model,
            system=[{"text": SYSTEM}],
            messages=messages,
            toolConfig={"tools": [{"toolSpec": {"name": t["name"], "description": t["description"], "inputSchema": {"json": t["schema"]}}} for t in TOOL_SPECS]},
            inferenceConfig={"maxTokens": MAX_TOKENS},
        )
        self.requests.append({
            "requestId": resp.get("ResponseMetadata", {}).get("RequestId"),
            "stopReason": resp.get("stopReason"),
            "inputTokens": resp.get("usage", {}).get("inputTokens"),
            "outputTokens": resp.get("usage", {}).get("outputTokens"),
            "latenceMs": resp.get("metrics", {}).get("latencyMs") or round((time.perf_counter() - t0) * 1000),
        })
        return resp

    # ------------------------------------------------------------ boucle
    def run(self, scenario_key: str, scenario: dict, request: str | None = None) -> Dossier:
        self._scenario = scenario
        request = request or scenario["demande"]
        hyps = {k: v for k, v in scenario.items() if k not in {"demande", "titre", "persona", "origine_demande"}}
        messages = [{"role": "user", "content": [{"text": (
            f"Profil fictif : {scenario['persona']}\n"
            f"Demande de la personne : « {request} »\n"
            + (f"Hypothèses de démonstration disponibles (fictives, à présenter comme telles) :\n{json.dumps(hyps, ensure_ascii=False)}"
               if hyps else "Aucune hypothèse de démonstration n'est fournie pour cette demande.")
        )}]}]
        dossier, fixes = None, 0
        for _ in range(MAX_TURNS):
            resp = self._converse(messages)
            msg = resp["output"]["message"]
            messages.append(msg)
            if resp.get("stopReason") != "tool_use":
                break
            results = []
            for block in msg["content"]:
                if "toolUse" not in block:
                    continue
                use = block["toolUse"]
                if use["name"] == "soumettre_dossier":
                    dossier, layout_issues = self._build(scenario_key, scenario, request, use["input"])
                    ver = dossier.verification()
                    problems = dict(ver["problemes"], **({"presentation": layout_issues} if layout_issues else {}))
                    if not problems or fixes >= MAX_FIXES:
                        results.append({"toolResult": {"toolUseId": use["toolUseId"], "content": [{"json": {"accepte": not problems}}]}})
                    else:
                        fixes += 1
                        results.append({"toolResult": {"toolUseId": use["toolUseId"], "status": "error",
                                                       "content": [{"json": {"problemes": problems, "consigne": "Corrige ces éléments et soumets à nouveau le dossier complet."}}]}})
                        dossier = None
                    continue
                try:
                    out = self._run_tool(use["name"], use.get("input") or {})
                    results.append({"toolResult": {"toolUseId": use["toolUseId"], "content": [{"json": out}]}})
                except Exception as e:  # erreur d'outil renvoyée à l'agent, visible dans la trace
                    self.session.trace.append({"outil": TOOL_NAMES.get(use["name"], use["name"]), "arguments": use.get("input"), "enregistrements": [],
                                               "duree_ms": 0, "erreur": str(e)})
                    results.append({"toolResult": {"toolUseId": use["toolUseId"], "status": "error", "content": [{"text": str(e)}]}})
            messages.append({"role": "user", "content": results})
            if dossier is not None:
                break
        if dossier is None:
            raise RuntimeError("l'agent n'a pas soumis de dossier vérifiable dans la limite de tours")
        dossier.aws = {"service": "Amazon Bedrock Runtime (Converse)", "region": self.region, "modele": self.model,
                       "appels": self.requests, "corrections_demandees": fixes}
        return dossier

    # ------------------------------------------------------------ dossier
    def _build(self, key: str, scenario: dict, request: str, sub: dict) -> tuple[Dossier, list[dict]]:
        """Dossier construit à partir de la soumission. Les éléments de présentation invalides sont
        écartés (le rendu ne doit jamais échouer) et signalés à l'agent."""
        reg = self.session.registry
        d = Dossier(key, scenario["persona"], request, f"agent Bedrock ({self.model})", reg, self.session.trace, title=sub.get("titre", ""))
        d.summary = sub.get("resume", "")
        for c in sub.get("affirmations", []):
            if c.get("section") in SECTIONS:
                d.add(c["section"], c["texte"], *c.get("references", []))
        issues: list[dict] = []

        def known(rid, where: str) -> bool:
            if rid in reg:
                return True
            issues.append({"kind": "référence inconnue", "detail": f"{where} : {rid}"})
            return False

        by_label = {r.label: rid for rid, r in reg.records.items() if rid.startswith("P")}
        d.profile_card = [(title, by_label[label]) for title, label in PROFILE_CARD if label in by_label]
        for h in (sub.get("chiffres_cles") or [])[:4]:
            if known(h.get("valeur"), "chiffres_cles"):
                d.highlights.append({"libelle": h.get("libelle", ""), "valeur": h["valeur"], "detail": h.get("detail", "")})
        tab = sub.get("tableau")
        if tab and tab.get("colonnes") and tab.get("lignes"):
            n = len(tab["colonnes"])
            rows = [{"nom": r.get("nom", ""), "cellules": [c if c and known(c, "tableau") else None for c in ((r.get("cellules") or []) + [None] * n)[:n]]}
                    for r in tab["lignes"]]
            d.tables.append({"titre": tab.get("titre", ""), "colonnes": tab["colonnes"], "lignes": rows})
        if sub.get("graphique"):
            chart = self._chart(sub["graphique"], issues)
            if chart:
                d.charts.append(chart)
        return d, issues

    def _chart(self, spec: dict, issues: list[dict]) -> dict | None:
        """Graphique tracé par le code : l'agent choisit les séries, jamais les valeurs."""
        s, m = self.session, self.session.market
        portfolios = {t["arguments"]["name"]: t for t in s.trace if t["outil"] == "portfolio_metrics" and "erreur" not in t}
        assets = {t["arguments"]["ticker"]: t for t in s.trace if t["outil"] == "asset_metrics" and "erreur" not in t}

        def record(call: dict, prefix: str) -> list[str]:
            return [i for i in call["enregistrements"] if s.registry[i].label.startswith(prefix)]

        names = [n for n in spec.get("series") or [] if n in portfolios or n in assets]
        unknown = [n for n in spec.get("series") or [] if n not in names]
        if unknown or not names:
            issues.append({"kind": "série inconnue", "detail": f"graphique : {unknown or 'aucune série'} ; séries possibles : {sorted(portfolios) + sorted(assets)}"})
        if spec.get("type") == "baisses":
            names = names[:3]
            if not names:
                return None
            raw = {n: dict(underwater(a.portfolio(m, T._weights(portfolios[n]["arguments"]["weights"])).index if n in portfolios
                                      else m.weekly_values[n].dropna()))
                   for n in names}
            common = sorted(set.intersection(*(set(v) for v in raw.values())))  # le tracé suppose des séries alignées
            series = {n: [[x, raw[n][x]] for x in common] for n in names}
            hl = spec.get("mise_en_evidence")
            return {"titre": "Baisse depuis le plus haut précédent : " + ", ".join(names), "sous_titre": "série hebdomadaire en dollars canadiens",
                    "type": "ligne", "unite": "pct", "mise_en_evidence": hl if hl in names else names[0], "series": series,
                    "sources": [i for n in names for i in record(portfolios.get(n) or assets[n], "Pire baisse depuis un sommet")],
                    "note": "Série hebdomadaire : pour un actif seul, la pire baisse citée dans le texte est mesurée sur la série quotidienne et peut être un peu plus profonde."}
        names = [n for n in names if n in portfolios][:2]
        if not names:
            return None

        def groups(name: str, kind: str) -> dict[str, float]:
            prefix = f"{kind} du groupe "
            return {s.registry[i].label[len(prefix):].split(" dans ")[0]: s.registry[i].value for i in record(portfolios[name], prefix)}

        risk = groups(names[0], "Part du risque")
        other = groups(names[1], "Part du risque") if len(names) == 2 else {}
        order = sorted(risk, key=risk.get, reverse=True) + sorted(set(other) - set(risk), key=other.get, reverse=True)
        series = {f"Poids, {names[0]}": [[g, round(groups(names[0], "Poids").get(g, 0.0), 4)] for g in order],
                  f"Risque, {names[0]}": [[g, round(risk.get(g, 0.0), 4)] for g in order]}
        if other:
            series[f"Risque, {names[1]}"] = [[g, round(other.get(g, 0.0), 4)] for g in order]
        chart = {"titre": "Part du poids et part du risque par groupe d'actifs", "type": "barres", "unite": "pct",
                 "mise_en_evidence": f"Risque, {names[0]}", "series": series,
                 "sources": [i for n in names for i in record(portfolios[n], "Part du risque du groupe ")],
                 "note": "Part du risque : contribution de chaque groupe à la variance des rendements hebdomadaires. Regroupement selon config/scenarios.toml."}
        caps = [t["arguments"]["cap"] for t in s.trace if t["outil"] == "diversification_sweep" and "erreur" not in t]
        if caps:
            chart["repere"] = {"valeur": caps[-1], "libelle": "plafond de démonstration"}
        return chart
