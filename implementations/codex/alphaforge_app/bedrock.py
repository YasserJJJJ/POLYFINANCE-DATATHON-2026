"""AWS-only inference for AlphaForge.

The SDK resolves credentials from the nominated profile (or an AWS execution
role). STS verifies the account before any inference. No OpenAI/Anthropic direct
endpoint, bearer-token override, or fallback provider is accepted.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from jsonschema import Draft202012Validator, ValidationError

REGION = "us-east-1"
EXPECTED_ACCOUNT = "471112821226"
DEFAULT_MODEL = "global.openai.gpt-6-astra"
RUNTIME_ENDPOINT = f"https://bedrock-runtime.{REGION}.amazonaws.com"
LOGGER = logging.getLogger(__name__)
CREDENTIAL_ERROR_CODES = {
    "ExpiredToken",
    "ExpiredTokenException",
    "InvalidClientTokenId",
    "UnrecognizedClientException",
}


class BedrockError(RuntimeError):
    """An actionable, sanitized inference failure."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "BedrockError",
        request_id: str | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.request_id = request_id
        self.retryable = retryable

    def as_dict(self) -> dict[str, Any]:
        return {
            "message": str(self),
            "code": self.code,
            "request_id": self.request_id,
            "retryable": self.retryable,
        }


def _provider_error(exc: Exception) -> BedrockError:
    if isinstance(exc, ClientError):
        response = exc.response
        code = response.get("Error", {}).get("Code", "AWSClientError")
        request_id = response.get("ResponseMetadata", {}).get("RequestId")
        retryable = code in {
            "ThrottlingException",
            "TooManyRequestsException",
            "ServiceUnavailableException",
            "InternalServerException",
            "ModelNotReadyException",
            "ModelTimeoutException",
        }
        messages = {
            "ExpiredToken": "La session AWS a expiré. Renouvelez le profil alphaforge.",
            "ExpiredTokenException": "La session AWS a expiré. Renouvelez le profil alphaforge.",
            "InvalidClientTokenId": "Les identifiants AWS ne sont plus valides.",
            "UnrecognizedClientException": "Les identifiants AWS ne sont plus valides.",
            "AccessDeniedException": "Le rôle AWS ne permet pas cet appel Bedrock.",
            "ThrottlingException": "Le quota Bedrock est momentanément atteint.",
            "ValidationException": "Bedrock a refusé le format de la requête.",
            "ModelTimeoutException": "Le modèle Bedrock n'a pas terminé dans le délai prévu.",
        }
        # AWS error bodies can contain input fragments: never return them to UI
        # or logs. Request IDs support diagnosis without copying prompts.
        return BedrockError(
            messages.get(code, f"L'appel AWS a échoué ({code})."),
            code=code,
            request_id=request_id,
            retryable=retryable,
        )
    return BedrockError(
        "Connexion AWS indisponible. Vérifiez le réseau et le profil alphaforge.",
        code=type(exc).__name__,
        retryable=True,
    )


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if not isinstance(part, dict):
                raise ValueError("Chaque bloc de message doit être un objet.")
            if part.get("type") in {"text", "input_text", "output_text"}:
                parts.append(str(part.get("text", "")))
            elif "text" in part:
                parts.append(str(part["text"]))
            else:
                raise ValueError("Le client AlphaForge accepte uniquement du texte.")
        return "\n".join(parts)
    if content is None:
        return ""
    return json.dumps(content, ensure_ascii=False, allow_nan=False)


def _normalize_messages(
    messages: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    """Convert ordinary user/assistant/tool messages into Converse blocks."""
    system: list[dict[str, str]] = []
    turns: list[dict[str, Any]] = []
    for message in messages:
        role = message.get("role")
        content = _message_text(message.get("content"))
        if role in {"system", "developer"}:
            if content:
                system.append({"text": content})
            continue
        if role == "tool":
            call_id = message.get("tool_call_id") or message.get("call_id")
            if not call_id:
                raise ValueError("Un résultat d'outil doit référencer son appel.")
            block = {
                "toolResult": {
                    "toolUseId": call_id,
                    "content": [{"text": content or "{}"}],
                    "status": "error" if message.get("is_error") else "success",
                }
            }
            target_role = "user"
            blocks = [block]
        elif role in {"user", "assistant"}:
            target_role = role
            blocks = [{"text": content}] if content else []
            if role == "assistant":
                for call in message.get("tool_calls") or []:
                    function = call.get("function", call)
                    arguments = function.get("arguments", {})
                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)
                    if not isinstance(arguments, dict):
                        raise ValueError("Les arguments d'outil doivent être un objet.")
                    blocks.append(
                        {
                            "toolUse": {
                                "toolUseId": call["id"],
                                "name": function["name"],
                                "input": arguments,
                            }
                        }
                    )
            if not blocks:
                raise ValueError("Un message de conversation ne peut pas être vide.")
        else:
            raise ValueError(f"Rôle de message non pris en charge : {role!r}.")
        # Several parallel tool results belong to one user turn in Converse.
        if turns and turns[-1]["role"] == target_role:
            turns[-1]["content"].extend(blocks)
        else:
            turns.append({"role": target_role, "content": blocks})
    if not turns or turns[0]["role"] != "user":
        raise ValueError("La conversation doit commencer par une demande utilisateur.")
    return system, turns


def _normalize_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for tool in tools:
        function = tool.get("function", tool)
        if tool.get("type", "function") != "function":
            raise ValueError("Seuls les outils locaux de type function sont acceptés.")
        schema = function.get("parameters", {"type": "object", "properties": {}})
        Draft202012Validator.check_schema(schema)
        spec = {
            "name": function["name"],
            "description": function.get("description") or function["name"],
            "inputSchema": {"json": schema},
        }
        if "strict" in function:
            spec["strict"] = bool(function["strict"])
        result.append({"toolSpec": spec})
    return result


class BedrockClient:
    """A synchronous client; use a worker thread from an async HTTP handler.

    ``messages`` use role/content and OpenAI-compatible tool_calls/tool_call_id.
    ``tools`` accept Responses-style or Chat-Completions-style function schemas.
    Only final text and observable tool requests are returned; internal reasoning
    is neither requested, exposed nor logged.
    """

    def __init__(
        self,
        *,
        profile: str | None = "alphaforge",
        region: str = REGION,
        expected_account: str = EXPECTED_ACCOUNT,
        model: str = DEFAULT_MODEL,
        timeout: int = 120,
    ) -> None:
        if region != REGION:
            raise BedrockError(
                "Ce projet utilise exclusivement la région d'entrée us-east-1.",
                code="RegionMismatch",
            )
        if os.environ.get("AWS_BEARER_TOKEN_BEDROCK"):
            raise BedrockError(
                "Retirez AWS_BEARER_TOKEN_BEDROCK : le profil AWS vérifié doit être utilisé.",
                code="UnexpectedBearerToken",
            )
        if not expected_account or len(expected_account) != 12 or not expected_account.isdigit():
            raise ValueError("Un compte AWS attendu de 12 chiffres est nécessaire.")
        if not model.startswith(("global.openai.", "us.openai.")):
            raise ValueError("Un profil d'inférence OpenAI sur Bedrock est nécessaire.")
        self.profile = profile
        self.region = region
        self.model = model
        self.expected_account = expected_account
        self._config = Config(
            signature_version="v4",
            ignore_configured_endpoint_urls=True,
            connect_timeout=10,
            read_timeout=timeout,
            retries={"mode": "standard", "total_max_attempts": 2},
        )
        self._connection_lock = threading.Lock()
        self._session = None
        self._runtime = None
        self._get_runtime()

    def _get_runtime(self):
        """Read a renewed profile only after the cached credentials fail."""
        with self._connection_lock:
            if self._runtime is not None:
                return self._runtime
            try:
                session = boto3.Session(
                    profile_name=self.profile, region_name=self.region
                )
                sts = session.client(
                    "sts",
                    endpoint_url=f"https://sts.{self.region}.amazonaws.com",
                    config=self._config,
                )
                identity = sts.get_caller_identity()
                if identity["Account"] != self.expected_account:
                    raise BedrockError(
                        "Le profil AWS pointe vers un autre compte que celui de l'équipe.",
                        code="AccountMismatch",
                    )
                runtime = session.client(
                    "bedrock-runtime",
                    endpoint_url=RUNTIME_ENDPOINT,
                    config=self._config,
                )
                self.identity = {
                    "account_id": identity["Account"],
                    "role_arn": identity["Arn"],
                    "region": self.region,
                    "profile": self.profile,
                    "provider": "amazon-bedrock-runtime",
                    "endpoint": RUNTIME_ENDPOINT,
                    "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "sts_request_id": identity.get("ResponseMetadata", {}).get("RequestId"),
                }
                self._session = session
                self._runtime = runtime
                return runtime
            except BedrockError:
                raise
            except (BotoCoreError, ClientError) as exc:
                raise _provider_error(exc) from exc

    def _invalidate_runtime(self, failed_runtime):
        # A concurrent request may already have refreshed the connection. An old
        # failure must not invalidate that newer, independently verified session.
        with self._connection_lock:
            if self._runtime is failed_runtime:
                self._runtime = None
                self._session = None

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        json_schema: dict[str, Any] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
        *,
        schema_name: str = "alphaforge_output",
        max_tokens: int = 4096,
        reasoning_effort: str = "medium",
    ) -> dict[str, Any]:
        """Generate one agent turn without executing any requested tools.

        The caller validates tool authorization and semantics, executes tools,
        appends their results, and invokes the next turn. JSON Schema validates
        structure only; financial correctness requires the deterministic engine.
        """
        if os.environ.get("AWS_BEARER_TOKEN_BEDROCK"):
            raise BedrockError(
                "Un jeton Bedrock prioritaire est apparu après la vérification AWS.",
                code="UnexpectedBearerToken",
            )
        if not 1 <= max_tokens <= 32768:
            raise ValueError("max_tokens doit être compris entre 1 et 32768.")
        if reasoning_effort not in {"low", "medium", "high"}:
            raise ValueError("reasoning_effort doit être low, medium ou high.")
        system, turns = _normalize_messages(messages)
        request: dict[str, Any] = {
            "modelId": self.model,
            "messages": turns,
            "inferenceConfig": {"maxTokens": max_tokens},
            "additionalModelRequestFields": {"reasoning": {"effort": reasoning_effort}},
        }
        if system:
            request["system"] = system
        if tools:
            request["toolConfig"] = {"tools": _normalize_tools(tools)}
            if tool_choice is None or tool_choice == "auto":
                request["toolConfig"]["toolChoice"] = {"auto": {}}
            elif isinstance(tool_choice, str) and tool_choice in {"required", "any"}:
                request["toolConfig"]["toolChoice"] = {"any": {}}
            elif isinstance(tool_choice, dict):
                name = tool_choice.get("name") or tool_choice.get("function", {}).get("name")
                if not name:
                    raise ValueError("Un choix d'outil explicite doit indiquer son nom.")
                request["toolConfig"]["toolChoice"] = {"tool": {"name": name}}
            else:
                raise ValueError("tool_choice doit être auto, required ou un outil nommé.")
        elif tool_choice is not None:
            raise ValueError("tool_choice exige une liste d'outils.")
        if json_schema is not None:
            Draft202012Validator.check_schema(json_schema)
            request["outputConfig"] = {
                "textFormat": {
                    "type": "json_schema",
                    "structure": {
                        "jsonSchema": {
                            "name": schema_name,
                            "schema": json.dumps(json_schema, ensure_ascii=False),
                        }
                    },
                }
            }
            request["additionalModelRequestFields"]["text"] = {"format": {"strict": True}}

        runtime = self._get_runtime()
        started = time.monotonic()
        try:
            response = runtime.converse(**request)
        except (BotoCoreError, ClientError) as exc:
            error = _provider_error(exc)
            if error.code in CREDENTIAL_ERROR_CODES:
                self._invalidate_runtime(runtime)
            LOGGER.warning(
                "bedrock_failure model=%s code=%s request_id=%s",
                self.model,
                error.code,
                error.request_id,
            )
            raise error from exc
        latency_ms = round((time.monotonic() - started) * 1000)
        request_id = response.get("ResponseMetadata", {}).get("RequestId")
        stop_reason = response.get("stopReason")
        usage = response.get("usage", {})
        LOGGER.info(
            "bedrock_call model=%s request_id=%s stop=%s tokens=%s latency_ms=%s",
            self.model,
            request_id,
            stop_reason,
            usage.get("totalTokens"),
            latency_ms,
        )
        if stop_reason not in {"end_turn", "tool_use", "stop_sequence"}:
            raise BedrockError(
                f"La réponse Bedrock n'est pas exploitable ({stop_reason}).",
                code="IncompleteOrRefusedResponse",
                request_id=request_id,
            )
        texts = []
        tool_calls = []
        tool_schemas = {
            tool.get("function", tool)["name"]: tool.get("function", tool).get("parameters", {})
            for tool in tools or []
        }
        for block in response.get("output", {}).get("message", {}).get("content", []):
            if "text" in block:
                texts.append(block["text"])
            elif "toolUse" in block:
                call = block["toolUse"]
                name = call["name"]
                if name not in tool_schemas:
                    raise BedrockError(
                        "Le modèle a demandé un outil absent de la liste autorisée.",
                        code="UnknownTool",
                        request_id=request_id,
                    )
                try:
                    Draft202012Validator(tool_schemas[name]).validate(call["input"])
                except ValidationError as exc:
                    raise BedrockError(
                        "Les arguments produits pour l'outil ne respectent pas son schéma.",
                        code="InvalidToolArguments",
                        request_id=request_id,
                    ) from exc
                tool_calls.append(
                    {"id": call["toolUseId"], "name": name, "arguments": call["input"]}
                )
        text = "\n".join(texts)
        parsed = None
        if json_schema is not None and not tool_calls:
            try:
                parsed = json.loads(text)
                Draft202012Validator(json_schema).validate(parsed)
            except (json.JSONDecodeError, ValidationError) as exc:
                raise BedrockError(
                    "La réponse structurée ne respecte pas le contrat attendu.",
                    code="InvalidStructuredOutput",
                    request_id=request_id,
                ) from exc
        if not text and not tool_calls:
            raise BedrockError(
                "Bedrock n'a renvoyé ni texte ni appel d'outil.",
                code="EmptyResponse",
                request_id=request_id,
            )
        return {
            "text": text,
            "tool_calls": tool_calls,
            "parsed": parsed,
            "request_id": request_id,
            "model": self.model,
            "usage": {
                "input_tokens": usage.get("inputTokens", 0),
                "output_tokens": usage.get("outputTokens", 0),
                "total_tokens": usage.get("totalTokens", 0),
                "cache_read_input_tokens": usage.get("cacheReadInputTokens", 0),
                "cache_write_input_tokens": usage.get("cacheWriteInputTokens", 0),
            },
            "latency_ms": latency_ms,
            "server_latency_ms": response.get("metrics", {}).get("latencyMs"),
            "stop_reason": stop_reason,
            "provider": "amazon-bedrock-runtime",
            "region": self.region,
            "account_id": self.expected_account,
        }
