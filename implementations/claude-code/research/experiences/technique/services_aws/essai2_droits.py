"""Essai 2 — Les créations seraient-elles autorisées ? Simulation IAM, sans rien créer.

iam.simulate_principal_policy évalue les politiques du rôle pour une liste d'actions.
Une réponse « allowed » n'est pas un essai réel : une limite de service, une condition de
politique ou une règle d'organisation peut encore refuser. Si la simulation elle-même est
refusée, l'essai le consigne et lit ce que le rôle a le droit de lire sur lui-même.

    uv run python research/experiences/technique/services_aws/essai2_droits.py
"""

from __future__ import annotations

from commun import client, ecrire, maintenant, sonde

ACTIONS = {
    "Step Functions": ["states:CreateStateMachine", "states:StartExecution", "states:SendTaskSuccess", "states:TestState",
                       "states:ValidateStateMachineDefinition"],
    "Rôles d'exécution": ["iam:CreateRole", "iam:PassRole", "iam:PutRolePolicy", "iam:AttachRolePolicy"],
    "S3": ["s3:CreateBucket", "s3:PutBucketVersioning", "s3:PutBucketObjectLockConfiguration", "s3:PutObject", "s3:GetObjectVersion"],
    "DynamoDB": ["dynamodb:CreateTable", "dynamodb:PutItem", "dynamodb:Query", "dynamodb:ExportTableToPointInTime"],
    "Journal Bedrock": ["bedrock:PutModelInvocationLoggingConfiguration", "logs:CreateLogGroup", "logs:PutRetentionPolicy"],
    "Garde-fous": ["bedrock:CreateGuardrail", "bedrock:ApplyGuardrail"],
    "Bases de connaissances": ["bedrock:CreateKnowledgeBase", "bedrock:CreateDataSource", "bedrock:Retrieve", "bedrock:Rerank",
                               "s3vectors:CreateVectorBucket", "s3vectors:CreateIndex", "s3vectors:PutVectors", "s3vectors:QueryVectors"],
    "AgentCore": ["bedrock-agentcore:CreateAgentRuntime", "bedrock-agentcore:InvokeAgentRuntime", "bedrock-agentcore:CreateMemory",
                  "bedrock-agentcore:CreateEvent", "bedrock-agentcore:CreateGateway", "bedrock-agentcore:CreatePolicyEngine",
                  "bedrock-agentcore:CreateEvaluator", "bedrock-agentcore:Evaluate", "bedrock-agentcore:InvokeWebSearch"],
    "Lambda": ["lambda:CreateFunction", "lambda:InvokeFunction"],
    "Inférence": ["bedrock:InvokeModel", "bedrock:Converse"],
}


def main() -> None:
    sts, iam = client("sts"), client("iam")
    ident = sts.get_caller_identity()
    nom_role = ident["Arn"].split("/")[1]
    arn_role = f"arn:aws:iam::{ident['Account']}:role/{nom_role}"
    sortie: dict = {"quand": maintenant(), "role": nom_role, "simulation": {}, "lecture_du_role": []}

    for famille, actions in ACTIONS.items():
        s = sonde(f"iam.simulate_principal_policy[{famille}]",
                  lambda a=actions: iam.simulate_principal_policy(PolicySourceArn=arn_role, ActionNames=a),
                  lambda r: {e["EvalActionName"]: e["EvalDecision"] + ("" if e.get("OrganizationsDecisionDetail", {}).get("AllowedByOrganizations", True)
                                                                      else " (refus d'organisation)") for e in r["EvaluationResults"]})
        sortie["simulation"][famille] = s
        vu = sonde("organisation", lambda a=actions: iam.simulate_principal_policy(PolicySourceArn=arn_role, ActionNames=a[:1]),
                   lambda r: "OrganizationsDecisionDetail" in r["EvaluationResults"][0])
        sortie.setdefault("regles_d_organisation_evaluees", {})[famille] = vu.get("resume")
        print(f"{famille} : {s['etat']}")
        for action, decision in (s.get("resume") or {}).items():
            print(f"    {decision:16} {action}")
        if s["etat"] != "autorise":
            print(f"    {s.get('code')} — {s.get('message', '')[:160]}")

    # Ce que le rôle peut lire sur lui-même : noms des politiques seulement (aucun secret).
    sortie["lecture_du_role"] = [
        sonde("iam.list_attached_role_policies", lambda: iam.list_attached_role_policies(RoleName=nom_role),
              lambda r: [p["PolicyName"] for p in r["AttachedPolicies"]]),
        sonde("iam.list_role_policies", lambda: iam.list_role_policies(RoleName=nom_role), lambda r: r["PolicyNames"]),
        sonde("iam.get_role", lambda: iam.get_role(RoleName=nom_role),
              lambda r: {"limite_de_permissions": r["Role"].get("PermissionsBoundary", {}).get("PermissionsBoundaryArn", "aucune").split("/")[-1],
                         "duree_max_session_s": r["Role"].get("MaxSessionDuration")}),
        sonde("iam.list_roles", lambda: iam.list_roles(MaxItems=200),
              lambda r: {"nombre": len(r["Roles"]),
                         "assumables_par": sorted({svc for role in r["Roles"] for st in role["AssumeRolePolicyDocument"].get("Statement", [])
                                                   for svc in ([st.get("Principal", {}).get("Service")] if isinstance(st.get("Principal", {}).get("Service"), str)
                                                               else st.get("Principal", {}).get("Service") or [])})}),
    ]
    for s in sortie["lecture_du_role"]:
        print(f"{s['etat']:9} {s['sonde']:36} {s.get('resume') if s['etat'] == 'autorise' else s.get('code')}")
    print("Règles d'organisation évaluées par la simulation :", sortie.get("regles_d_organisation_evaluees"))
    ecrire("essai2_droits.json", sortie)


if __name__ == "__main__":
    main()
