"""Essai 1 — Inventaire en lecture seule : ce qui existe et ce que le rôle a le droit de lister.

Aucun appel de création. Un appel « autorisé » prouve le droit de lire, pas celui de créer
(voir l'essai 2 pour la simulation des droits de création).

    uv run python research/experiences/technique/services_aws/essai1_inventaire.py
"""

from __future__ import annotations

from commun import client, ecrire, maintenant, sonde


def n(cle):
    champs = ("name", "Name", "FunctionName", "logGroupName", "evaluatorId", "id")
    return lambda r: {"nombre": len(r.get(cle, [])),
                      "noms": [str(next((x[c] for c in champs if x.get(c)), x))[:48] if isinstance(x, dict) else str(x)[:48] for x in r.get(cle, [])][:40]}


def main() -> None:
    sts, sfn, s3, ddb = client("sts"), client("stepfunctions"), client("s3"), client("dynamodb")
    br, bra, s3v, lam = client("bedrock"), client("bedrock-agent"), client("s3vectors"), client("lambda")
    acc, logs, ct, cw = client("bedrock-agentcore-control"), client("logs"), client("cloudtrail"), client("cloudwatch")
    ident = sts.get_caller_identity()
    sondes = [
        # Enchaînement
        sonde("stepfunctions.list_state_machines", sfn.list_state_machines, n("stateMachines")),
        sonde("stepfunctions.list_activities", sfn.list_activities, n("activities")),
        sonde("lambda.list_functions", lam.list_functions, n("Functions")),
        sonde("lambda.get_account_settings", lam.get_account_settings,
              lambda r: {"simultanees": r["AccountLimit"]["ConcurrentExecutions"], "non_reservees": r["AccountLimit"]["UnreservedConcurrentExecutions"]}),
        # Persistance
        sonde("s3.list_buckets", s3.list_buckets, n("Buckets")),
        sonde("dynamodb.list_tables", ddb.list_tables, n("TableNames")),
        sonde("dynamodb.describe_limits", ddb.describe_limits, lambda r: {k: v for k, v in r.items() if k != "ResponseMetadata"}),
        # Recherche documentaire
        sonde("bedrock-agent.list_knowledge_bases", bra.list_knowledge_bases, n("knowledgeBaseSummaries")),
        sonde("s3vectors.list_vector_buckets", s3v.list_vector_buckets, n("vectorBuckets")),
        # Garde-fous et observation
        sonde("bedrock.list_guardrails", br.list_guardrails, n("guardrails")),
        sonde("bedrock.get_model_invocation_logging_configuration", br.get_model_invocation_logging_configuration,
              lambda r: {"journal_active": "loggingConfig" in r, "config": r.get("loggingConfig")}),
        sonde("logs.describe_log_groups", lambda: logs.describe_log_groups(limit=50), n("logGroups")),
        sonde("cloudtrail.describe_trails", ct.describe_trails, n("trailList")),
        sonde("cloudwatch.list_metrics(AWS/Bedrock)", lambda: cw.list_metrics(Namespace="AWS/Bedrock"),
              lambda r: {"metriques": sorted({m["MetricName"] for m in r.get("Metrics", [])})}),
        sonde("cloudwatch.list_metrics(AWS/Bedrock-AgentCore)", lambda: cw.list_metrics(Namespace="AWS/Bedrock-AgentCore"),
              lambda r: {"metriques": sorted({m["MetricName"] for m in r.get("Metrics", [])})}),
        # AgentCore, plan de contrôle
        sonde("agentcore.list_agent_runtimes", acc.list_agent_runtimes, n("agentRuntimes")),
        sonde("agentcore.list_memories", acc.list_memories, n("memories")),
        sonde("agentcore.list_gateways", acc.list_gateways, n("items")),
        sonde("agentcore.list_policy_engines", acc.list_policy_engines, n("policyEngines")),
        sonde("agentcore.list_evaluators", acc.list_evaluators, n("evaluators")),
        sonde("agentcore.list_online_evaluation_configs", acc.list_online_evaluation_configs, n("onlineEvaluationConfigs")),
        sonde("agentcore.list_code_interpreters", acc.list_code_interpreters, n("codeInterpreterSummaries")),
        sonde("agentcore.list_browsers", acc.list_browsers, n("browserSummaries")),
        sonde("agentcore.list_harnesses", acc.list_harnesses, lambda r: {k: len(v) for k, v in r.items() if isinstance(v, list)}),
        sonde("agentcore.list_registries", acc.list_registries, lambda r: {k: len(v) for k, v in r.items() if isinstance(v, list)}),
    ]
    sortie = {"quand": maintenant(), "role": ident["Arn"].split("/")[1] if "/" in ident["Arn"] else ident["Arn"],
              "compte_fin": ident["Account"][-4:], "sondes": sondes}
    ecrire("essai1_inventaire.json", sortie)
    print(f"Rôle {sortie['role']}, compte …{sortie['compte_fin']}")
    for s in sondes:
        detail = s.get("resume") if s["etat"] == "autorise" else f"{s.get('code')} — {s.get('message', '')[:110]}"
        print(f"  {s['etat']:9} {s['sonde']:52} {str(detail)[:420]}")


if __name__ == "__main__":
    main()
