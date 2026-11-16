"""Comment le PRODUIT (et non la session de développement) appellerait la recherche web d'AgentCore,
les plongements et le reclassement : trois fonctions boto3, sans ressource à créer.

Chaque fonction rend le résultat ET l'identifiant de requête AWS, à inscrire au journal du dossier :
c'est la preuve que l'appel est passé par AWS. Le rôle IAM du produit doit porter
bedrock-agentcore:InvokeWebSearch, bedrock:InvokeModel et bedrock:Rerank.
"""

from __future__ import annotations

import hashlib
import json

from commun import REGION, appel_modele, client

TITAN = "amazon.titan-embed-text-v2:0"
RERANK = "cohere.rerank-v3-5:0"


def recherche_web(requete: str, n: int = 5, domaines: list[str] | None = None) -> dict:
    """Outil de l'agent 1 (niveau 2 de la recherche). Rend des extraits : ce n'est pas une lecture."""
    kwargs = {"webSearchId": "web-search.v1", "searchQuery": requete[:200], "maxResults": n}
    if domaines:
        kwargs["filters"] = {"domainFilter": {"include": domaines}}
    rep = client("bedrock-agentcore").invoke_web_search(**kwargs)
    return {"requestId": rep["ResponseMetadata"]["RequestId"],
            "resultats": [{"titre": r.get("title"), "url": r.get("url"), "extrait": r.get("text", ""),
                           "empreinte_extrait": "sha256:" + hashlib.sha256(r.get("text", "").encode()).hexdigest()[:16]}
                          for r in rep.get("results", [])]}


def plongement(texte: str, essai: str, dimensions: int = 256) -> dict:
    """Vecteur d'un passage ou d'une question (Titan v2 : un texte par appel)."""
    rep = appel_modele(essai, TITAN, "plongement", lambda: client("bedrock-runtime").invoke_model(
        modelId=TITAN, body=json.dumps({"inputText": texte, "dimensions": dimensions, "normalize": True})))
    corps = json.loads(rep["body"].read())
    return {"requestId": rep["ResponseMetadata"]["RequestId"], "vecteur": corps["embedding"], "jetons": corps.get("inputTextTokenCount")}


def reclassement(question: str, passages: list[str], essai: str, n: int = 3) -> dict:
    """Classe des passages (fiches de la bibliothèque ou extraits du web) par pertinence pour la question."""
    arn = f"arn:aws:bedrock:{REGION}::foundation-model/{RERANK}"
    rep = appel_modele(essai, RERANK, "reclassement", lambda: client("bedrock-agent-runtime").rerank(
        queries=[{"type": "TEXT", "textQuery": {"text": question}}],
        sources=[{"type": "INLINE", "inlineDocumentSource": {"type": "TEXT", "textDocument": {"text": p}}} for p in passages],
        rerankingConfiguration={"type": "BEDROCK_RERANKING_MODEL",
                                "bedrockRerankingConfiguration": {"numberOfResults": min(n, len(passages)), "modelConfiguration": {"modelArn": arn}}}))
    return {"requestId": rep["ResponseMetadata"]["RequestId"],
            "classement": [{"rang": i + 1, "indice": r["index"], "score": round(r["relevanceScore"], 4)} for i, r in enumerate(rep["results"])]}
