"""Essai 4 — Le produit appelle lui-même la recherche web, les plongements et le reclassement.

Déroulé, tel que l'agent 1 le ferait :
  1. le modèle (Haiku, Converse) ne dispose que de l'outil « recherche_web » et doit rendre une sortie
     à structure imposée par l'outil « deposer_preuve_candidate » ;
  2. le code exécute la recherche par AgentCore, reclasse les extraits par Cohere, et rend au modèle
     les trois premiers ;
  3. le code contrôle que la citation rendue figure mot pour mot dans un extrait (existence) ;
  4. deux plongements Titan mesurent la proximité question / extrait retenu (pour une bibliothèque locale).

Appels de modèle : 2 Converse, 1 reclassement, 2 plongements. Une recherche web.

    uv run python research/experiences/technique/services_aws/essai4_appels_du_produit.py
"""

from __future__ import annotations

from commun import HAIKU, appel_modele, client, ecrire, maintenant
from services_produit import plongement, recherche_web, reclassement

ESSAI = "essai4"
QUESTION = "Combien d'années de rendements faut-il au minimum pour classer le risque d'un fonds d'investissement au Canada ?"
OUTILS = {"tools": [
    {"toolSpec": {"name": "recherche_web", "description": "Recherche sur le web. Rend des extraits de pages, pas des lectures.",
                  "inputSchema": {"json": {"type": "object", "properties": {"requete": {"type": "string"}}, "required": ["requete"]}}}},
    {"toolSpec": {"name": "deposer_preuve_candidate", "description": "Dépose une preuve candidate au dossier.",
                  "inputSchema": {"json": {"type": "object", "additionalProperties": False,
                                           "properties": {"url": {"type": "string"},
                                                          "citation": {"type": "string", "description": "copie mot pour mot d'un extrait, 25 mots au plus"},
                                                          "niveau_de_lecture": {"type": "string", "enum": ["extrait"]},
                                                          "soutien": {"type": "string", "enum": ["non_juge"]}},
                                           "required": ["url", "citation", "niveau_de_lecture", "soutien"]}}}}]}
SYSTEME = [{"text": "Tu es l'agent 1 d'un bureau d'étude simulé. Tu ne réponds jamais de mémoire : tu cherches, puis tu déposes une "
                    "preuve candidate dont la citation est copiée mot pour mot d'un extrait reçu."}]


def converse(messages, choix_outil):
    return appel_modele(ESSAI, HAIKU, "converse", lambda: client("bedrock-runtime").converse(
        modelId=HAIKU, system=SYSTEME, messages=messages, toolConfig=OUTILS | {"toolChoice": choix_outil},
        inferenceConfig={"maxTokens": 400}))


def bloc_outil(rep):
    return next(b["toolUse"] for b in rep["output"]["message"]["content"] if "toolUse" in b)


def main() -> None:
    messages = [{"role": "user", "content": [{"text": QUESTION}]}]
    r1 = converse(messages, {"tool": {"name": "recherche_web"}})
    demande = bloc_outil(r1)
    recherche = recherche_web(demande["input"]["requete"], n=6)
    extraits = [r["extrait"][:1200] for r in recherche["resultats"]]
    classement = reclassement(QUESTION, extraits, ESSAI, n=3)
    retenus = [recherche["resultats"][c["indice"]] for c in classement["classement"]]
    rendu = [{"json": {"url": r["url"], "extrait": r["extrait"][:1200]}} for r in retenus]
    messages += [r1["output"]["message"], {"role": "user", "content": [{"toolResult": {"toolUseId": demande["toolUseId"], "content": rendu}}]}]
    r2 = converse(messages, {"tool": {"name": "deposer_preuve_candidate"}})
    preuve = bloc_outil(r2)["input"]
    source = next((r for r in retenus if r["url"] == preuve.get("url")), None)
    existence = bool(source) and " ".join(preuve["citation"].split()) in " ".join(source["extrait"].split())
    v_question, v_extrait = plongement(QUESTION, ESSAI), plongement(retenus[0]["extrait"][:1200], ESSAI)
    proximite = sum(a * b for a, b in zip(v_question["vecteur"], v_extrait["vecteur"]))

    sortie = {"quand": maintenant(), "question": QUESTION,
              "1_requete_choisie_par_le_modele": demande["input"], "1_requestId_converse": r1["ResponseMetadata"]["RequestId"],
              "2_recherche": {"requestId": recherche["requestId"], "resultats": [{"url": r["url"], "titre": r["titre"]} for r in recherche["resultats"]]},
              "2_reclassement": classement,
              "3_preuve_candidate": preuve, "3_requestId_converse": r2["ResponseMetadata"]["RequestId"],
              "3_controle_existence_par_le_code": existence, "3_url_parmi_les_extraits_rendus": bool(source),
              "4_plongements": {"dimension": len(v_question["vecteur"]), "proximite_question_extrait": round(proximite, 4),
                                "requestIds": [v_question["requestId"], v_extrait["requestId"]]},
              "jetons": {"converse_1": r1["usage"], "converse_2": r2["usage"]}}
    ecrire("essai4_appels_du_produit.json", sortie)
    print("Requête choisie par le modèle :", demande["input"])
    print("Recherche AgentCore :", len(recherche["resultats"]), "résultats, requestId", recherche["requestId"])
    print("Reclassement :", classement["classement"])
    print("Preuve candidate :", preuve)
    print("Citation présente mot pour mot dans l'extrait (contrôle du code) :", existence)
    print("Plongements : dimension", len(v_question["vecteur"]), "proximité", round(proximite, 4))


if __name__ == "__main__":
    main()
