"""Annexe distincte au registre initial ; aucun réseau, SDK AWS ou modèle."""
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
inventory = json.loads((BASE / "inventaire_urls.json").read_text())

deep = {
    372: ("Source initiale inaccessible ; substitution officielle lue",
          "sources/atelier_codex_bedrock_officiel.txt:1630–1710,1770–1855,1900–1965",
          "La page Help retourne403. Substitution https://learn.chatgpt.com/docs/amazon-bedrock : Runtime, profil Astra, authentification AWS et recherche hébergée indisponible ; aucune reconfiguration."),
    377: ("Passages de fonctionnement approfondis + docstring SDK locale",
          "../collecte/U377.extrait.txt:1–225,292–350,428–500 ; sources/atelier_botocore_retries.json",
          "Page soumise à opt-in AWS_NEW_RETRIES_2026. Standard/adaptive, budget, jitter et bornes ; dans Config botocore max_attempts compte les retries après initial, total_max_attempts inclut initial. Ne pas supposer activation actuelle."),
    421: ("Passages outils/délégation approfondis",
          "../collecte/U421.extrait.txt:1080–1167,1230–1295",
          "Outils intégrés au Harness SDK ; shell/HTTP/fichiers et délégation ont des pouvoirs différents. Enfants héritent par défaut outils/modèle/interventions ; Fixed et Inherit explicitables. Un graphe créé par modèle ne garantit pas les quatre rôles fixes."),
    456: ("Passages intégration/transports/filtrage approfondis",
          "../collecte/U456.extrait.txt:1080–1280,1448–1608,1740–1840",
          "Lifecycle géré ou contexte explicite ; stdio/HTTP/SSE dépendent du serveur. allowed/rejected et préfixes limitent outils exposés, pas droits IAM du serveur. Exemples @latest à épingler avant usage ; aucun lancement uvx."),
    458: ("README ciblé : périmètre/transports/installation/licence",
          "../collecte/U458.extrait.txt:350–375,512–550,564–605,1630–1770",
          "Distinguer serveurs locaux du dépôt, services distants Knowledge/AWS MCP et successeur Agent Toolkit annoncé. Serveur documentaire AWS ≠ recherche scientifique générale ; API MCP peut agir sur ressources. README annonce Apache2.0, code/dépendances non audités."),
    375: ("Introduction/politiques lues pour éventuel hébergement",
          "../collecte/U375.extrait.txt:1–65",
          "Block Public Access applique combinaison restrictive aux niveaux pertinents ; futur stockage privé, aucun paramètre ni bucket modifié. Ne prouve ni rétention ni sauvegarde hors compte."),
    379: ("Corps documentaire lu pour portée future",
          "../collecte/U379.extrait.txt:1–135",
          "Code space possède volume/configuration/compute ; arrêt/redémarrage perd modifications non sauvegardées et suppression détruit volume. EBS n'est pas copie hors compte ; Amazon Q documenté non invoqué."),
    401: ("Introduction et droits IAM lus pour portée future",
          "../collecte/U401.extrait.txt:1–78",
          "Function URL AWS_IAM vs NONE ; nouvelles URL depuis octobre2025 exigent InvokeFunctionUrl et InvokeFunction. IAM n'est pas accessibilité réseau privée et un lien seul ne donne pas interface publique authentifiée. Rien déployé."),
    439: ("Corps documentaire lu pour portée future",
          "../collecte/U439.extrait.txt:1–173",
          "CloudShell : aucun port entrant/IP publique, session interactive et échéances ; VPC sans persistance. Ne pas en faire hébergeur ou stockage durable d'une nuit ; aucune session CloudShell lancée."),
}

link_topics = {
    372: "Configurer Codex avec Amazon Bedrock",
    374: "Portail Workshop Studio",
    386: "S3 : analyses et informations de stockage",
    387: "S3 : développement et intégration",
    388: "S3 : exemples SDK",
    422: "Atelier Strands Agents",
    454: "AgentCore : prise en main en français",
    455: "Atelier construction de workflows agentiques",
    460: "Documentation API FRED",
    463: "Portail de dépôts SEDAR+",
    472: "Introduction à l'IA générative : art du possible",
    473: "Amazon Bedrock : prise en main",
    474: "Cloud Quest : IA générative Practitioner",
    475: "Cloud Quest : architecte IA générative",
    476: "SimuLearn : présentation IA générative",
    477: "SimuLearn : commencer avec IA générative",
    478: "IA générative pour dirigeants",
    479: "Bases ML pour décideurs métier et techniques",
    480: "Essentials of Prompt Engineering",
    481: "Foundations of Prompt Engineering",
    482: "Prompt engineering avec Claude",
    483: "Bonnes pratiques prompting modèles Bedrock",
    485: "Construire des agents de production avec AgentCore",
    486: "AgentCore Policy",
    487: "AgentCore Evaluation",
    488: "SimuLearn : AgentCore Runtime",
    489: "SimuLearn : orchestration sur AgentCore Runtime",
    490: "SimuLearn : AgentCore Memory et Gateway",
    491: "Atelier Amazon Bedrock",
    492: "Atelier Bedrock Guardrails",
    495: "Préparation certification AI Practitioner AIF-C01",
}

def decision(n):
    if n in deep:
        return deep[n][2]
    if n in {373, 374}:
        return "Index d'ateliers pour aiguillage ; pas inscription, droit de compte ni capacité exécutée."
    if n == 376:
        return "Bonnes pratiques réseau à relire seulement si VPC nécessaire ; pas nouvelle infrastructure."
    if n in {378, 380}:
        return "Environnement de calcul partagé possible ; rôle console et rôle d'exécution à vérifier séparément avant usage."
    if 381 <= n <= 389:
        return "Stockage/gestion S3 potentiel pour originaux et artefacts ; aucun besoin de créer ici, accès compte et sauvegarde distincts."
    if 390 <= n <= 396:
        return "Documentation Bedrock générale ; support modèle/API, cycle de vie et droits à vérifier sur Astra, pas modèle supplémentaire adopté."
    if n in {397, 398, 470, 471}:
        return "Assistant/specifications Kiro comme ressource pédagogique ; crédits et route d'inférence distincts, ni accès ni invocation vérifiés."
    if n in {399, 400, 402}:
        return "Option Lambda ultérieure ; durée, paquet et audience à définir, démo Mac conservée."
    if n in {403, 405, 440}:
        return "Référence SDK/CLI, lecture de version possible ; la présence du manuel ne prouve aucune permission de service."
    if n == 404:
        return "Framework d'interface candidat seulement ; aucun remplacement ou changement UI dans cette recherche."
    if 406 <= n <= 414:
        return "Identités/permissions/analyse d'accès ; référence future ciblée, aucune modification IAM ou rôle étendu."
    if 415 <= n <= 420:
        return "Amazon Quick/Quick Sight pour restitution éventuelle ; aucun compte service ni route des analyses IA vérifiés."
    if n in {422, 454, 455, 491, 492}:
        return "Atelier agent/Guardrails à explorer si besoin ; contenu de cours non obtenu par capture HTTP, aucune exécution."
    if 423 <= n <= 428:
        return "SQL/Athena/Spark potentiel si volume ou sources le justifient ; aucune requête, catalogue ou frais de scan engagés."
    if 429 <= n <= 438:
        return "Glue ingestion/catalogue/qualité/ETL ; pas gain établi pour volume local, aucune ressource ni pipeline exécuté."
    if 441 <= n <= 451:
        return "Index CLI du service nommé ; syntaxe possible, ni opération autorisée ni modèle auxiliaire de ce service vérifiés."
    if n == 452:
        return "Langage de requête JSON local utile pour inspection ; filtrer un document n'en valide pas le contenu."
    if n == 453:
        return "Catalogue d'outils de développement ; orientation, pas inventaire des outils installés dans notre environnement."
    if n == 457:
        return "Protocole MCP pour interopérabilité ; n'assure ni fournisseur d'inférence ni permissions ni fiabilité documentaire."
    if n == 459:
        return "Documentation yfinance pour données de marché ; ajustements, horodatage, droits et limites à contrôler avant nouvelle acquisition."
    if n == 460:
        return "API FRED pertinente pour macro ; tentative expirée, pas corps obtenu ; historique de vintages/ALFRED à distinguer du décalage de série révisée."
    if n == 461:
        return "Page StatCan obtenue concerne nouvelles données/statistiques ; ce n'est pas une preuve d'accès à une série ou un millésime précis."
    if n == 462:
        return "API StatCan candidate pour séries définies ; aucun téléchargement de série, date de disponibilité ou droit vérifié ici."
    if n == 463:
        return "SEDAR+ potentiel pour dépôts primaires ; HTTP200 est une page Radware, contenu documentaire non obtenu ; ne pas déclarer source lue."
    if n in {464, 465, 466}:
        return "Portail d'émetteur de FNB : piste pour composition, frais, documents datés ; page d'accueil ne prouve pas holdings d'un produit ni historique."
    if n == 467:
        return "Catalogue AWS Open Data ; vérifier chaque jeu, sa provenance et ses conditions, aucun dataset récupéré."
    if n == 468:
        return "GDELT comme piste d'événements/actualités ; extraction médiatique n'est pas jugement ESG, biais de couverture/langue à examiner."
    if n == 469:
        return "Gestionnaire de dépendances uv ; outil de développement possible, aucune installation supplémentaire."
    if 472 <= n <= 483 or 485 <= n <= 490 or n == 495:
        return "Cours/parcours mentionné par l'atelier ; capture limitée à coque JavaScript, contenu non lu, aucune formation suivie ni service activé."
    if n in {484, 500, 501, 502, 504, 505}:
        return "Documentation française du service/sujet déjà cartographié ; traduction/URL supplémentaire, pas preuve indépendante ni nouvel accès."
    if n in {493, 494, 496, 497, 499}:
        return "Formation/certification éducative ; ne prouve pas qualification professionnelle, inscription ou accès technique du projet."
    if n in {498, 503}:
        return "Conditions/coûts à examiner sur le service et compte précis ; aucun crédit gratuit ou coût de l'atelier supposé."
    raise ValueError(n)

records = []
for x in inventory:
    n = int(x["id"][1:])
    if not 372 <= n <= 505:
        continue
    meta = json.loads((BASE / "collecte" / f"{x['id']}.json").read_text())
    text_path = BASE / "collecte" / f"{x['id']}.extrait.txt"
    text = text_path.read_text() if text_path.exists() else ""
    occurrences = [o for o in x["occurrences"] if o["file"].endswith("RESSOURCES_LIENS_PUBLICS.md")]
    content_status = "Capture textuelle disponible ; disponibilité distincte de lecture"
    if meta.get("status") != 200:
        content_status = f"Texte attendu non obtenu : {meta.get('error', meta.get('status'))}"
    elif "Radware Page" in text:
        content_status = "HTTP200 mais vérification de navigateur Radware ; document non obtenu"
    elif "JavaScript Required" in text or "enable JavaScript to run this app" in text:
        content_status = "HTTP200 mais coque JavaScript ; contenu du cours/atelier non obtenu"
    elif len(text.strip()) < 180:
        content_status = "HTTP200 mais extrait limité au titre ; contenu utile non établi"
    level, locator = ("Titre/sujet/accès seulement ; corps non lu",
                      "Métadonnées de collecte et libellé du registre atelier")
    if n in deep:
        level, locator = deep[n][:2]
    rec = {
        "id": x["id"], "url": x["url"],
        "family": sorted({o["section"] for o in occurrences}),
        "workshop_occurrences": occurrences,
        "captured_title": meta.get("title"),
        "topic": link_topics.get(n) or meta.get("title") or x["url"],
        "topic_basis": "Libellé ou URL de l'atelier ; pas titre d'un cours lu" if n in link_topics else "Titre de la capture",
        "subject_from_workshop_label": [o["context"] for o in occurrences],
        "http_status": meta.get("status"), "final_url": meta.get("final_url"),
        "retrieved_at": meta.get("retrieved_at"), "sha256": meta.get("sha256"),
        "capture": f"../collecte/{x['id']}.json",
        "content_status": content_status,
        "reading_level": level, "passages": locator,
        "decision_and_limit": decision(n),
        "operation_tested": False,
        "installation_or_provisioning": False,
    }
    if n == 372:
        rec["official_substitution"] = {
            "url": "https://learn.chatgpt.com/docs/amazon-bedrock",
            "capture": "sources/atelier_codex_bedrock_officiel.json",
            "status": 200,
            "limitation": "Documentation de route, pas nouvelle vérification de session ni preuve de facturation.",
        }
    records.append(rec)

assert len(records) == 134
assert {r["id"] for r in records} == {f"U{i}" for i in range(372, 506)}
counts = Counter(r["content_status"] for r in records)
(OUT / "annexe_atelier_134.json").write_text(json.dumps({
    "date": "2026-11-15",
    "scope": "Annexe distincte, aucune modification du triage initial",
    "method": "Titres, libellés, statuts et détection de coques examinés pour134URL ; passages approfondis seulement pour9URL identifiées. Les autres corps ne sont pas déclarés lus.",
    "aws_calls": 0, "inference_calls": 0,
    "count": len(records), "content_status_counts": counts, "records": records,
}, ensure_ascii=False, indent=2) + "\n")

intro = """# Annexe — Exploitation des 134 liens supplémentaires de l’atelier

Cette annexe complète le catalogue des 36 captures et le triage initial, **sans modifier ce dernier**. Elle couvre individuellement **U372–U505** : titre ou libellé de sujet, famille Fxx, accès et pertinence. Un sujet peut être identifié par son URL et son libellé sans que le cours soit lisible. Les corps non lus sont explicitement signalés.

Le JSON associé conserve les occurrences et lignes du registre `revision_2026-11-15/RESSOURCES_LIENS_PUBLICS.md`, les URL finales, horodatages et empreintes. Les niveaux approfondis ci-dessous concernent des passages ciblés, pas la totalité de chaque documentation. Aucun outil MCP n’a été installé ou démarré ; aucun appel AWS ou d’inférence n’a été fait pour cette annexe. Une lecture HTTP documentaire de la substitution officielle U372 et une lecture locale de la documentation botocore ont complété les captures communes.

## Décisions issues des lectures ciblées

- **U377 — retries.** L’avertissement initial soumet le comportement décrit à `AWS_NEW_RETRIES_2026=true`. Les timings et coûts de quota ne sont donc pas des garanties de notre client sans vérification d’activation. Le mode adaptatif peut ralentir aussi le premier appel et partager ce frein entre les ressources d’un client. La documentation locale de botocore **1.44.3** précise que `Config(retries={"max_attempts":2})` autorise deux retries après l’appel initial, tandis que `total_max_attempts` inclut cet appel et prévaut si les deux sont fournis. Fixer explicitement mode et nombre total, journaliser le résultat final ; ne pas empiler des boucles de reprise sans budget global. Ce constat est documentaire, pas un test de panne réelle.
- **U421 — outils intégrés Strands.** La page actuelle décrit les outils du Harness SDK : fichiers, shell, HTTP, notes, MCP et délégation. Par défaut, le constructeur d’enfant reprend outils, modèle et interventions du parent ; l’exemple permet `tools=Fixed(...)` et `model=Inherit()`. Le graphe construit par le modèle n’est pas le graphe fixe de quatre rôles exigé pour AlphaForge. Pour l’adaptation, assigner explicitement outils et responsabilités ; ne pas assimiler le SDK, un serveur MCP et un service distant à une seule capacité.
- **U456 — intégration MCP.** L’API documente lifecycle automatique ou contexte manuel, filtrage des outils autorisés/refusés et préfixes anti-collision. Ce filtrage contrôle ce qui est exposé au modèle ; il ne remplace pas les permissions IAM ou le contrôle d’arguments du serveur. Les exemples lancent un paquet `@latest` : épingler une version avant un essai. Aucune commande de démarrage n’a été exécutée.
- **U458 — dépôt AWS MCP.** Le README distingue serveurs locaux, AWS Knowledge MCP documentaire distant et AWS MCP d’opérations. Il annonce Agent Toolkit comme successeur recommandé, sans annoncer l’arrêt du dépôt. La section des serveurs locaux indique stdio et suppression de SSE dans leurs versions majeures récentes ; la prise en charge de HTTP par un client Strands ne prouve donc pas celle de chaque serveur local. La présence de liens vers des services HTTP distants n’est pas cette contradiction. Apache-2.0 est annoncé dans le README ; ce n’est pas un audit du code, des dépendances ou des appels auxiliaires. Un serveur AWS documentaire ne remplace pas une recherche scientifique généraliste.
- **U372 — route Codex.** La capture de l’URL Help renvoie403. La substitution officielle [ChatGPT Learn](https://learn.chatgpt.com/docs/amazon-bedrock) renvoie200 et documente explicitement Runtime, `global.openai.gpt-6-astra`, l’authentification AWS et l’absence de recherche web hébergée sur Runtime. Elle distingue région source et Global/Geo CRIS. Les suggestions Mantle de cette documentation ne changent pas la route convenue ; la recherche AgentCore déjà testée est une autre surface. Les preuves déclaratives de session et les requêtes AWS restent celles de la note01.
- **U375/U379/U401/U439 — portée future seulement.** S3 Block Public Access n’est pas une sauvegarde hors compte. SageMaker code spaces implique stockage/compute propres et peut perdre les changements non sauvegardés au redémarrage. Les nouvelles Function URLs documentées exigent `lambda:InvokeFunctionUrl` et `lambda:InvokeFunction` ; IAM est une authentification, pas une garantie de réseau privé. CloudShell n’accepte pas de ports entrants, termine les sessions interactives et ne fournit pas de persistance dans ses environnements VPC : il ne constitue pas un hébergeur de démo ou une sauvegarde durable. Aucun de ces services n’a été configuré.

## Limites d’accès effectivement repérées

**U463 SEDAR+** renvoie HTTP200 mais seulement une page Radware de vérification de navigateur. **U460 FRED** a expiré pendant la collecte. Des cours Skill Builder et ateliers Workshop Studio renvoient uniquement une coque JavaScript ; leurs noms sont connus, leur contenu n’a pas été obtenu. **U386–U388** ne contiennent qu’un titre dans l’extraction. Ces adresses ne sont pas présentées comme des cours suivis ou des sources métier lues. Les portails d’émetteurs U464–U466 ne démontrent pas une composition datée de FNB.

## Registre individuel

"""
table = "| ID / source | Famille | Accès et lecture | Utilité / décision |\n|---|---|---|---|\n"
clean = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
for r in records:
    title = r["topic"]
    # The original course label remains available in JSON; page title can be only a shell.
    table += (
        f"| [{r['id']}]({r['url']}) — {clean(title)} "
        f"| {clean('; '.join(r['family']))} "
        f"| {clean(r['content_status'])}. **{clean(r['reading_level'])}**. {clean(r['passages'])} "
        f"| {clean(r['decision_and_limit'])} |\n"
    )
(OUT / "04_annexe_atelier_134.md").write_text(intro + table)
print(json.dumps({"records": len(records), "status_counts": counts}, ensure_ascii=False))
