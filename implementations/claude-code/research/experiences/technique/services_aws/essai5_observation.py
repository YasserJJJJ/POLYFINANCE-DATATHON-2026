"""Essai 5 — Observer les inférences sans créer de ressource : que voit-on déjà ?

A. CloudWatch : métriques AWS/Bedrock du modèle des essais sur la dernière heure.
B. CloudTrail (historique des événements, 90 jours, sans piste à créer) : nos identifiants de requête
   (sorties/appels_bedrock.jsonl et essai4_appels_du_produit.json) y figurent-ils ?
   CloudTrail livre avec quelques minutes de retard : relancer l'essai si rien n'est encore visible.

Seuls des comptes et nos propres identifiants sont conservés (le compte est partagé).
Aucun appel de modèle.

    uv run python research/experiences/technique/services_aws/essai5_observation.py
"""

from __future__ import annotations

import datetime as dt
import json

from commun import HAIKU, JOURNAL_MODELE, SORTIES, client, ecrire, maintenant, sonde


def nos_identifiants() -> dict[str, str]:
    ids = {}
    if JOURNAL_MODELE.exists():
        for ligne in JOURNAL_MODELE.open(encoding="utf-8"):
            j = json.loads(ligne)
            if j.get("requestId"):
                ids[j["requestId"]] = f"{j['nature']} {j['modele']}"
    e4 = SORTIES / "essai4_appels_du_produit.json"
    if e4.exists():
        ids[json.loads(e4.read_text(encoding="utf-8"))["2_recherche"]["requestId"]] = "recherche web AgentCore"
    return ids


def main() -> None:
    cw, ct = client("cloudwatch"), client("cloudtrail")
    fin = dt.datetime.now(dt.timezone.utc)
    debut = fin - dt.timedelta(hours=1)
    metriques = [sonde(f"cloudwatch[{m} {modele}]", lambda m=m, modele=modele: cw.get_metric_statistics(
        Namespace="AWS/Bedrock", MetricName=m, Dimensions=[{"Name": "ModelId", "Value": modele}],
        StartTime=debut, EndTime=fin, Period=3600, Statistics=["Sum"]),
        lambda r: {"somme_sur_une_heure": sum(p["Sum"] for p in r["Datapoints"])})
        for modele, noms in ((HAIKU, ("Invocations", "InputTokenCount", "OutputTokenCount")), ("amazon.titan-embed-text-v2:0", ("Invocations",)),
                             ("cohere.rerank-v3-5:0", ("Invocations", "SearchUnits"))) for m in noms]

    ids = nos_identifiants()
    trouves, par_evenement = {}, {}
    for nom in ("Converse", "InvokeModel", "Rerank", "InvokeWebSearch"):
        def appel(nom=nom):
            vus, jeton, n = [], None, 0
            while n < 6:  # six pages de 50 au plus
                kw = {"LookupAttributes": [{"AttributeKey": "EventName", "AttributeValue": nom}], "StartTime": debut, "EndTime": fin, "MaxResults": 50}
                rep = ct.lookup_events(**kw, **({"NextToken": jeton} if jeton else {}))
                vus += [json.loads(e["CloudTrailEvent"]) for e in rep["Events"]]
                jeton, n = rep.get("NextToken"), n + 1
                if not jeton:
                    break
            rep["vus"] = vus
            return rep
        s = sonde(f"cloudtrail.lookup_events[{nom}]", appel, lambda r, nom=nom: {
            "evenements_lus": len(r["vus"]), "sources": sorted({e.get("eventSource") for e in r["vus"]}),
            "nature": sorted({e.get("eventCategory", "?") for e in r["vus"]}),
            "les_notres": {e["requestID"]: ids[e["requestID"]] for e in r["vus"] if e.get("requestID") in ids}})
        par_evenement[nom] = s
        trouves |= (s.get("resume") or {}).get("les_notres", {})

    sortie = {"quand": maintenant(), "cloudwatch": metriques, "cloudtrail": par_evenement,
              "nos_identifiants": len(ids), "retrouves_dans_cloudtrail": trouves,
              "non_retrouves": {k: v for k, v in ids.items() if k not in trouves}}
    ecrire("essai5_observation.json", sortie)
    for m in metriques:
        print(m["sonde"], m["etat"], m.get("resume") or m.get("code"))
    for nom, s in par_evenement.items():
        r = s.get("resume") or {}
        print(f"CloudTrail {nom:16} {s['etat']:9} lus={r.get('evenements_lus')} sources={r.get('sources')} nature={r.get('nature')} les nôtres={len(r.get('les_notres', {}))}"
              + ("" if s["etat"] == "autorise" else f" {s.get('code')} {s.get('message', '')[:120]}"))
    print(f"Identifiants de nos appels : {len(ids)} ; retrouvés dans CloudTrail : {len(trouves)}")
    for k, v in trouves.items():
        print("   retrouvé", k, v)


if __name__ == "__main__":
    main()
