"""Exercise profile renewal with real SDK profile reads and no network calls."""

from __future__ import annotations

import boto3
from botocore.exceptions import ClientError
import pytest

from alphaforge_app import bedrock, orchestrator


@pytest.fixture
def offline_profile(monkeypatch, tmp_path):
    credentials = tmp_path / "credentials"
    config = tmp_path / "config"
    config.write_text("")
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(credentials))
    monkeypatch.setenv("AWS_CONFIG_FILE", str(config))
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    monkeypatch.delenv("AWS_BEARER_TOKEN_BEDROCK", raising=False)
    monkeypatch.setattr(orchestrator, "_client", None)
    original_session = boto3.Session
    events = {"sessions": [], "sts": [], "inference": []}

    def write_profile(label):
        # Deliberately invalid, local-only values; never sent to any endpoint.
        credentials.write_text(
            f"[alphaforge]\naws_access_key_id={label}\n"
            "aws_secret_access_key=offline-only\naws_session_token=offline-only\n"
        )

    def install(error_code):
        class OfflineSession:
            def __init__(self, profile_name, region_name):
                actual_session = original_session(
                    profile_name=profile_name, region_name=region_name
                )
                self.label = actual_session.get_credentials().access_key
                events["sessions"].append(self.label)

            def client(self, service, **kwargs):
                label = self.label
                if service == "sts":
                    class Sts:
                        def get_caller_identity(self):
                            events["sts"].append(label)
                            account = "000000000000" if label == "OFFLINE_OTHER_ACCOUNT" else bedrock.EXPECTED_ACCOUNT
                            return {
                                "Account": account,
                                "Arn": f"arn:aws:sts::{account}:assumed-role/Offline/Test",
                                "ResponseMetadata": {"RequestId": f"sts-{label}"},
                            }
                    return Sts()
                assert service == "bedrock-runtime"

                class Runtime:
                    def converse(self, **request):
                        events["inference"].append(label)
                        if label == "OFFLINE_EXPIRED":
                            raise ClientError(
                                {
                                    "Error": {"Code": error_code, "Message": "offline auth failure"},
                                    "ResponseMetadata": {"RequestId": "expired-request"},
                                },
                                "Converse",
                            )
                        return {
                            "ResponseMetadata": {"RequestId": "renewed-request"},
                            "stopReason": "end_turn",
                            "output": {"message": {"content": [{"text": "Connexion renouvelée."}]}},
                            "usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2},
                        }
                return Runtime()

        monkeypatch.setattr(bedrock.boto3, "Session", OfflineSession)

    write_profile("OFFLINE_EXPIRED")
    return write_profile, install, events


@pytest.mark.parametrize("error_code", [
    "ExpiredToken", "ExpiredTokenException", "InvalidClientTokenId", "UnrecognizedClientException",
])
def test_cached_client_reloads_profile_after_auth_failure(offline_profile, error_code):
    write_profile, install, events = offline_profile
    install(error_code)
    cached_client = orchestrator.get_client()
    messages = [{"role": "user", "content": "Test local."}]

    with pytest.raises(bedrock.BedrockError) as failure:
        cached_client.generate(messages)
    assert failure.value.code == error_code
    assert failure.value.request_id == "expired-request"
    # Report this attempt as failed; renewal waits for the next user request.
    assert events["inference"] == ["OFFLINE_EXPIRED"]

    write_profile("OFFLINE_RENEWED")
    assert orchestrator.get_client() is cached_client
    result = cached_client.generate(messages)
    assert result["text"] == "Connexion renouvelée."
    assert result["request_id"] == "renewed-request"
    assert events["sessions"] == ["OFFLINE_EXPIRED", "OFFLINE_RENEWED"]
    assert events["sts"] == ["OFFLINE_EXPIRED", "OFFLINE_RENEWED"]
    assert events["inference"] == ["OFFLINE_EXPIRED", "OFFLINE_RENEWED"]
    assert cached_client.identity["sts_request_id"] == "sts-OFFLINE_RENEWED"


def test_renewed_profile_must_still_match_the_team_account(offline_profile):
    write_profile, install, events = offline_profile
    install("ExpiredToken")
    cached_client = orchestrator.get_client()
    messages = [{"role": "user", "content": "Test local."}]
    with pytest.raises(bedrock.BedrockError):
        cached_client.generate(messages)

    write_profile("OFFLINE_OTHER_ACCOUNT")
    with pytest.raises(bedrock.BedrockError) as failure:
        cached_client.generate(messages)
    assert failure.value.code == "AccountMismatch"
    assert events["sts"] == ["OFFLINE_EXPIRED", "OFFLINE_OTHER_ACCOUNT"]
    assert events["inference"] == ["OFFLINE_EXPIRED"]
