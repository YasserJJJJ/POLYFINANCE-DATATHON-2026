"""Garde-fous du déploiement : aucun service réel n'est appelé."""
import asyncio
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

CHEMIN = Path(__file__).resolve().parents[2] / "infra" / "deployer.py"
SPEC = importlib.util.spec_from_file_location("deployer_fusion", CHEMIN)
deployer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deployer)


class Refus(Exception):
    response = {"Error": {"Code": "AccessDeniedException"}}


class Absent(Exception):
    response = {"Error": {"Code": "ResourceNotFoundException"}}


def test_plan_lecture_seule_et_arns_resolus(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("ALPHAFORGE_GUARDRAIL_ID", raising=False)
    sts = SimpleNamespace(get_caller_identity=lambda: {"Account": deployer.COMPTE_ATTENDU})
    lus = []

    def profil(inferenceProfileIdentifier):
        lus.append(inferenceProfileIdentifier)
        return {"status": "ACTIVE", "inferenceProfileArn": "arn:profil:" + inferenceProfileIdentifier,
                "models": [{"modelArn": "arn:destination:" + inferenceProfileIdentifier}]}

    clients = {"sts": sts, "bedrock": SimpleNamespace(get_inference_profile=profil),
               "logs": SimpleNamespace(describe_log_groups=lambda **k: {"logGroups": []})}
    monkeypatch.setattr(deployer, "session", lambda: SimpleNamespace(client=lambda nom: clients[nom]))
    monkeypatch.setattr(deployer, "BUILD", tmp_path / "construction-interdite")
    monkeypatch.setattr(deployer.sys, "argv", ["deployer.py", "--plan"])
    deployer.main()
    plan = json.loads(capsys.readouterr().out)
    assert lus == deployer.MODELES
    assert not deployer.BUILD.exists()
    bedrock = plan["politique_role"]["Statement"][3]
    assert len(bedrock["Resource"]) == 4
    assert all("*" not in arn for arn in bedrock["Resource"])
    assert plan["ressources"][2]["concurrence_reservee"] == 2
    assert {r["service"] for r in plan["ressources"]} == {"s3", "iam", "lambda", "amplify", "logs"}


def test_plan_compte_et_concurrence_bornes():
    autre = SimpleNamespace(client=lambda _: SimpleNamespace(get_caller_identity=lambda: {"Account": "autre"}))
    with pytest.raises(ValueError, match="471112821226"):
        deployer.plan_deploiement(autre, "amplify", 2)
    autorise = SimpleNamespace(client=lambda _: SimpleNamespace(
        get_caller_identity=lambda: {"Account": deployer.COMPTE_ATTENDU}))
    with pytest.raises(ValueError, match="concurrence"):
        deployer.plan_deploiement(autorise, "amplify", 6)


def test_refus_lecture_s3_ne_declenche_pas_creation():
    client = Mock()
    client.head_bucket.side_effect = Refus()
    with pytest.raises(Refus):
        deployer.bucket_s3(client, deployer.COMPTE_ATTENDU)
    client.create_bucket.assert_not_called()
    client.put_public_access_block.assert_not_called()


def test_lambda_code_guardrail_cors_et_concurrence_avant_publication(monkeypatch, tmp_path):
    monkeypatch.setenv("ALPHAFORGE_GUARDRAIL_ID", "test-guardrail")
    monkeypatch.setenv("ALPHAFORGE_GUARDRAIL_VERSION", "1")
    lam = Mock()
    lam.exceptions = SimpleNamespace(ResourceNotFoundException=Absent)
    lam.get_function.side_effect = Absent()
    lam.create_function.return_value = {"FunctionArn": "arn:fonction"}
    ordre = []
    lam.put_function_concurrency.side_effect = lambda **k: ordre.append(("concurrence", k))
    monkeypatch.setattr(deployer, "fonction_url", lambda _: ordre.append(("url", {})) or "https://api.test/")
    origine = "https://main.interface.test"
    assert deployer.fonction_lambda(lam, Mock(), "bucket", tmp_path / "code.zip", "arn:role", origine, 2)
    args = lam.create_function.call_args.kwargs
    assert args["Code"]["S3Key"] == "code/alphaforge-lambda.zip"
    assert args["Environment"]["Variables"]["ALPHAFORGE_GUARDRAIL_VERSION"] == "1"
    assert args["Environment"]["Variables"]["ALPHAFORGE_ORIGINES_INTERFACE"] == origine
    assert [nom for nom, _ in ordre] == ["concurrence", "url"]
    assert ordre[0][1]["ReservedConcurrentExecutions"] == 2


def test_refus_permission_url_remonte():
    lam = Mock()
    lam.exceptions = SimpleNamespace(ResourceConflictException=Absent)
    lam.create_function_url_config.return_value = {"FunctionUrl": "https://api.test/"}
    lam.add_permission.side_effect = Refus()
    with pytest.raises(Refus):
        deployer.fonction_url(lam)


def test_nettoyage_uniquement_ressources_journalisees(tmp_path):
    suivi = deployer.SuiviCreations(tmp_path / "journal.json", {})
    suivi.ajouter("lambda", "fonction-creee", "arn:creee")
    client = Mock()
    deployer.nettoyer(SimpleNamespace(client=lambda nom: client), suivi)
    client.delete_function.assert_called_once_with(FunctionName="fonction-creee")
    client.list_functions.assert_not_called()
    client.delete_app.assert_not_called()
    assert json.loads(suivi.chemin.read_text())["creations"][0]["etat"] == "supprime"
    deployer.nettoyer(SimpleNamespace(client=lambda nom: client), suivi)
    assert client.delete_function.call_count == 1


def test_echec_deploiement_nettoie_sans_basculer_de_service(monkeypatch, tmp_path):
    plan = {"compte": deployer.COMPTE_ATTENDU, "groupe_journaux_existait": False}
    session = SimpleNamespace(client=Mock())
    monkeypatch.setattr(deployer, "session", lambda: session)
    monkeypatch.setattr(deployer, "plan_deploiement", lambda *a: plan)
    monkeypatch.setattr(deployer, "BUILD", tmp_path)
    monkeypatch.setattr(deployer, "construire_zip_lambda", lambda: tmp_path / "code.zip")
    monkeypatch.setattr(deployer, "construire_interface", lambda _: tmp_path / "web.zip")

    def creation(s, suivi):
        suivi.ajouter("amplify", "app-creee", "arn:app")
        raise Refus()

    monkeypatch.setattr(deployer, "application_amplify", creation)
    s3 = Mock()
    monkeypatch.setattr(deployer, "interface_s3", s3)
    journal = tmp_path / "echec.json"
    monkeypatch.setattr(deployer.sys, "argv", ["deployer.py", "--journal", str(journal)])
    with pytest.raises(Refus):
        deployer.main()
    s3.assert_not_called()
    session.client.return_value.delete_app.assert_called_once_with(appId="app-creee")
    assert json.loads(journal.read_text())["creations"][0]["etat"] == "supprime"


def test_sante_identifiants_et_cors(monkeypatch):
    import api
    from alphaforge import llm

    monkeypatch.setenv("ALPHAFORGE_LLM", "off")
    sante = api.sante()
    assert sante["region"] == llm.REGION
    assert sante["modeles_ids"] == {"principal": llm.MODELE_PRINCIPAL, "leger": llm.MODELE_LEGER}
    assert deployer.COMPTE_ATTENDU not in json.dumps(sante)

    async def preflight(origine):
        messages = []

        async def recevoir():
            return {"type": "http.request", "body": b""}

        async def envoyer(message):
            messages.append(message)

        await api.app({"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
                       "method": "OPTIONS", "path": "/api/analyse", "raw_path": b"/api/analyse",
                       "query_string": b"", "scheme": "http", "server": ("localhost", 80),
                       "client": ("127.0.0.1", 1234), "root_path": "",
                       "headers": [(b"origin", origine.encode()),
                                   (b"access-control-request-method", b"POST")]}, recevoir, envoyer)
        return messages[0]

    autorisee = asyncio.run(preflight(api.ORIGINES_INTERFACE[0]))
    assert autorisee["status"] == 200
    assert dict(autorisee["headers"])[b"access-control-allow-origin"].decode() == api.ORIGINES_INTERFACE[0]
    refusee = asyncio.run(preflight("https://origine-inconnue.example"))
    assert refusee["status"] == 400
    assert b"access-control-allow-origin" not in dict(refusee["headers"])


@pytest.mark.parametrize("existant", [False, True])
def test_guardrail_refus_version_supprime_seulement_creation_locale(monkeypatch, tmp_path, existant):
    import sys

    spec = importlib.util.spec_from_file_location("guardrail_fusion", CHEMIN.with_name("creer_guardrail.py"))
    guardrail = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guardrail)
    client = Mock()
    client.list_guardrails.return_value = {"guardrails": (
        [{"name": guardrail.NOM, "id": "precedent", "arn": "arn:precedent"}] if existant else [])}
    client.create_guardrail.return_value = {"guardrailId": "nouveau", "guardrailArn": "arn:nouveau"}
    client.get_guardrail.return_value = {"status": "READY"}
    client.create_guardrail_version.side_effect = Refus()
    sts = SimpleNamespace(get_caller_identity=lambda: {"Account": deployer.COMPTE_ATTENDU})
    session = Mock(return_value=SimpleNamespace(client=lambda nom: sts if nom == "sts" else client))
    monkeypatch.setitem(sys.modules, "boto3", SimpleNamespace(Session=session))
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    journal = tmp_path / "guardrail.json"
    monkeypatch.setattr(sys, "argv", ["creer_guardrail.py", "--journal", str(journal)])
    with pytest.raises(Refus):
        guardrail.main()
    assert session.call_args.kwargs["profile_name"] == "alphaforge"
    if existant:
        client.delete_guardrail.assert_not_called()
    else:
        client.delete_guardrail.assert_called_once_with(guardrailIdentifier="nouveau")
    assert json.loads(journal.read_text())["cree_par_tentative"] is not existant
