"""AWS Bedrock adapter integration.

This adapter uses boto3 to interact with AWS Bedrock's Converse API for chat
completions and normalizes responses to the SDK's ``UnifiedChatResponse``
schema. Supports streaming when enabled.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import AsyncIterator
from typing import Any, cast

from .._exceptions import AuthenticationError, InvalidRequestError, ProviderError
from ..models.config import SDKConfig
from ..models.model import Model
from ..models.request import ChatRequest
from ..models.response import (
    Choice,
    ProviderMetadata,
    ResponseMetrics,
    UnifiedChatResponse,
    Usage,
)
from ..models.stream import StreamChunk
from .base import BaseAdapter

try:  # pragma: no cover - import availability depends on environment
    import boto3
except Exception:  # noqa: BLE001
    boto3 = None


class BedrockAdapter(BaseAdapter):
    """AWS Bedrock adapter for chat completions using the Converse API.

    Args:
        max_concurrent: Maximum concurrent requests (default 5 for AWS rate limits).
        credentials: Optional dict with 'aws_access_key_id', 'aws_secret_access_key',
            'aws_session_token', and 'region_name'. Falls back to environment/IAM.
    """

    def __init__(
        self,
        max_concurrent: int = 5,
        *,
        credentials: dict[str, str] | None = None,
    ) -> None:
        super().__init__(max_concurrent=max_concurrent)
        self._bedrock_client: Any | None = None
        self._credentials = credentials or {}

    @property
    def provider_name(self) -> str:
        """Returns 'bedrock' as the provider identifier."""
        return "bedrock"

    async def invoke(self, request: ChatRequest) -> UnifiedChatResponse:
        """Call AWS Bedrock Converse API and normalize to UnifiedChatResponse.

        Args:
            request: ChatRequest with model, messages, and optional parameters.

        Returns:
            UnifiedChatResponse with normalized response and metrics.

        Raises:
            AuthenticationError: If AWS credentials are invalid.
            InvalidRequestError: If the request format is invalid.
            ProviderError: For other provider-specific errors.
        """
        client = await self._get_or_create_client()

        started_perf = time.perf_counter()
        started_epoch = int(time.time())

        # Convert messages to Bedrock format
        bedrock_messages = self._convert_messages_to_bedrock(request.messages)

        try:
            # Bedrock uses boto3, which is synchronous; run in thread
            def _call() -> dict[str, Any]:
                response = client.converse(
                    modelId=request.model,
                    messages=bedrock_messages,
                )
                return cast(dict[str, Any], response)

            raw: dict[str, Any] = await asyncio.to_thread(_call)
        except Exception as exc:  # noqa: BLE001
            # Map AWS exceptions to our taxonomy
            message = str(exc).lower()
            error_type = type(exc).__name__

            if (
                "credentials" in message
                or "unauthorized" in message
                or "accessdenied" in error_type.lower()
            ):
                raise AuthenticationError(provider=self.provider_name, original_error=exc) from exc
            if "validationexception" in error_type.lower() or "invalid" in message:
                raise InvalidRequestError(str(exc)) from exc
            if "throttling" in error_type.lower() or "throttled" in message:
                from .._exceptions import RateLimitError

                raise RateLimitError(provider=self.provider_name, original_error=exc) from exc
            raise ProviderError(provider=self.provider_name, original_error=exc) from exc

        duration_ms = (time.perf_counter() - started_perf) * 1000.0

        # Bedrock provides usage metrics
        usage_data = raw.get("usage", {})
        input_tokens = usage_data.get("inputTokens", 0)
        output_tokens = usage_data.get("outputTokens", 0)
        total_tokens = usage_data.get("totalTokens", input_tokens + output_tokens)

        # Bedrock metrics (latencyMs is provider-reported inference time)
        metrics_data = raw.get("metrics", {})
        latency_ms = metrics_data.get("latencyMs", 0)

        # Use provider-reported latency if available, otherwise use measured duration
        inference_time_s = (latency_ms / 1000.0) if latency_ms > 0 else (duration_ms / 1000.0)
        round_trip_time_s = duration_ms / 1000.0

        # TTFB for non-streaming is approximately the full duration
        ttfb_ms = duration_ms

        # Normalize response
        unified = self._normalize_response(
            raw=raw,
            fallback_id=f"bedrock-{uuid.uuid4()}",
            created=started_epoch,
            model=request.model,
        )

        unified.metrics = ResponseMetrics(
            duration_ms=duration_ms,
            ttfb_ms=ttfb_ms,
            round_trip_time_s=round_trip_time_s,
            inference_time_s=inference_time_s,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_tokens=input_tokens,
        )

        unified.provider_metadata = ProviderMetadata(provider=self.provider_name, raw=dict(raw))

        return unified

    async def invoke_streaming(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Stream tokens from AWS Bedrock using ConverseStream API.

        Args:
            request: ChatRequest with model and messages.

        Yields:
            StreamChunk objects with delta content.
        """
        client = await self._get_or_create_client()
        bedrock_messages = self._convert_messages_to_bedrock(request.messages)

        try:

            def _call_stream() -> Any:
                response = client.converse_stream(
                    modelId=request.model,
                    messages=bedrock_messages,
                )
                return response

            stream_response = await asyncio.to_thread(_call_stream)

            # Process the event stream
            idx = 0
            request_id = f"bedrock-{uuid.uuid4()}"

            def _iterate_stream() -> list[dict[str, Any]]:
                events = []
                stream = stream_response.get("stream", [])
                for event in stream:
                    events.append(event)
                return events

            events = await asyncio.to_thread(_iterate_stream)

            for event in events:
                if "contentBlockDelta" in event:
                    delta = event["contentBlockDelta"].get("delta", {})
                    if "text" in delta:
                        text = delta["text"]
                        yield StreamChunk(
                            id=request_id,
                            model=request.model,
                            index=idx,
                            delta={"role": "assistant", "content": text},
                        )
                        idx += 1

            # Final stop chunk
            yield StreamChunk(
                id=request_id,
                model=request.model,
                index=idx,
                delta={"role": "assistant", "content": ""},
                finish_reason="stop",
            )

        except Exception:  # noqa: BLE001
            # Fallback to non-streaming if streaming fails
            resp = await self.invoke(request)
            content = (resp.choices[0].message.get("content") if resp.choices else "") or ""
            yield StreamChunk(
                id=resp.id,
                model=request.model,
                index=0,
                delta={"role": "assistant", "content": content},
                finish_reason="stop",
            )

    async def health_check(self) -> dict[str, str]:
        """Check if the Bedrock client can be created and is healthy.

        Returns:
            Dict with 'status' ('healthy' or 'unhealthy') and 'provider'.
        """
        try:
            await self._get_or_create_client()
            return {"status": "healthy", "provider": self.provider_name}
        except Exception:  # noqa: BLE001
            return {"status": "unhealthy", "provider": self.provider_name}

    async def list_models(self) -> list[Model]:
        """List available models from AWS Bedrock.

        Attempts to fetch models dynamically from AWS Bedrock API.
        Falls back to a static list if API call fails.

        Returns:
            list[Model]: List of available Bedrock models.
        """
        if boto3 is None:
            # boto3 not installed, return fallback list
            return self._get_fallback_models()

        try:
            # Get resolved credentials
            session_kwargs = self._get_credentials()

            # Create bedrock client (not bedrock-runtime) for listing models
            session = boto3.Session(**session_kwargs)
            bedrock = session.client("bedrock")
            response = bedrock.list_foundation_models()
            summaries = response.get("modelSummaries", [])

            # Try to list foundation models from Bedrock
            def _list_models() -> list[dict[str, Any]]:

                return cast(list[dict[str, Any]], summaries)

            model_summaries = await asyncio.to_thread(_list_models)

            all_models = []
            converse_models = []
            for summary in model_summaries:
                # Only include models that support Converse API
                if (
                    len(summary.get("inputModalities", [])) == 1
                    and "TEXT" in summary.get("inputModalities", [])
                    and "TEXT" in summary.get("outputModalities", [])
                ):
                    all_models.append(
                        Model(
                            id=summary["modelId"],
                            object="model",
                            created=1704067200,  # Approximate Bedrock GA date
                            owned_by=summary.get("providerName", "aws").lower(),
                        )
                    )
            for model in all_models:
                model_id = model.id  # Access attribute, not dict key
                details = bedrock.get_foundation_model(modelIdentifier=model_id)
                capabilities = details["modelDetails"]["inferenceTypesSupported"]
                if "CONVERSE" in capabilities:
                    converse_models.append(model)

            return converse_models if converse_models else self._get_fallback_models()

        except Exception:  # noqa: BLE001
            # Fallback to static list if API call fails
            return self._get_fallback_models()

    def _get_fallback_models(self) -> list[Model]:
        """Return static list of common Bedrock models."""
        return [
            Model(
                id="qwen.qwen3-32b-v1:0",
                object="model",
                created=1735689600,  # January 2025
                owned_by="qwen",
            ),
            Model(
                id="anthropic.claude-3-haiku-20240307-v1:0",
                object="model",
                created=1709769600,  # March 2024
                owned_by="anthropic",
            ),
            Model(
                id="anthropic.claude-3-sonnet-20240229-v1:0",
                object="model",
                created=1709251200,  # February 2024
                owned_by="anthropic",
            ),
            Model(
                id="anthropic.claude-3-5-sonnet-20240620-v1:0",
                object="model",
                created=1718841600,  # June 2024
                owned_by="anthropic",
            ),
            Model(
                id="meta.llama3-70b-instruct-v1:0",
                object="model",
                created=1713398400,  # April 2024
                owned_by="meta",
            ),
        ]

    def _get_credentials(self) -> dict[str, str]:
        """Get AWS credentials with precedence: provided > environment > IAM.

        Returns:
            dict[str, str]: Resolved credentials with keys for boto3 Session.
        """
        cfg = SDKConfig.load()

        # Resolve each credential with fallback chain
        aws_access_key_id = (
            self._credentials.get("aws_access_key_id")
            or cfg.aws_access_key_id.get_secret_value()
            or None
        )
        aws_secret_access_key = (
            self._credentials.get("aws_secret_access_key")
            or cfg.aws_secret_access_key.get_secret_value()
            or None
        )
        aws_session_token = (
            self._credentials.get("aws_session_token")
            or cfg.aws_session_token.get_secret_value()
            or None
        )
        region_name = self._credentials.get("region_name") or cfg.aws_region

        # Build session kwargs (only include non-None values)
        session_kwargs: dict[str, str] = {"region_name": region_name}
        if aws_access_key_id:
            session_kwargs["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            session_kwargs["aws_secret_access_key"] = aws_secret_access_key
        if aws_session_token:
            session_kwargs["aws_session_token"] = aws_session_token

        return session_kwargs

    async def _get_or_create_client(self) -> Any:
        """Create or reuse AWS Bedrock client using boto3.

        Returns:
            boto3 bedrock-runtime client.

        Raises:
            ProviderError: If boto3 is not installed.
            AuthenticationError: If AWS credentials are missing.
        """
        if self._bedrock_client is not None:
            return self._bedrock_client

        if boto3 is None:
            raise ProviderError(
                provider=self.provider_name,
                original_error=ImportError("boto3 not installed. Run `pip install boto3`"),
            )

        # Get resolved credentials
        session_kwargs = self._get_credentials()

        # Create boto3 session (supports env vars and IAM roles automatically)
        session = boto3.Session(**session_kwargs)
        self._bedrock_client = session.client("bedrock-runtime")

        return self._bedrock_client

    def _convert_messages_to_bedrock(self, messages: list[Any]) -> list[dict[str, Any]]:
        """Convert UnifiedAI messages to Bedrock Converse API format.

        Args:
            messages: List of Message objects.

        Returns:
            List of Bedrock-formatted message dicts.
        """
        bedrock_messages = []
        for msg in messages:
            msg_dict = msg.model_dump() if hasattr(msg, "model_dump") else msg
            role = msg_dict.get("role", "user")
            content = msg_dict.get("content", "")

            # Bedrock uses 'user' and 'assistant' roles
            if role == "system":
                # Bedrock handles system messages separately; for now, prepend to first user message
                continue

            bedrock_messages.append({"role": role, "content": [{"text": content}]})

        return bedrock_messages

    def _normalize_response(
        self,
        *,
        raw: dict[str, Any],
        fallback_id: str,
        created: int,
        model: str,
    ) -> UnifiedChatResponse:
        """Normalize Bedrock Converse API response to UnifiedChatResponse.

        Args:
            raw: Raw Bedrock API response from converse().
            fallback_id: ID to use if not present in response.
            created: Timestamp for response creation.
            model: Model name.

        Returns:
            UnifiedChatResponse object.
        """
        # Extract output from Bedrock response
        output = raw.get("output", {})
        message_data = output.get("message", {})
        content_blocks = message_data.get("content", [])

        # Extract text from content blocks (Converse API returns list of content blocks)
        text_content = ""
        for block in content_blocks:
            if "text" in block:
                text_content += block["text"]

        # Extract usage (Bedrock returns inputTokens, outputTokens, totalTokens)
        usage_data = raw.get("usage", {})
        usage = Usage(
            prompt_tokens=int(usage_data.get("inputTokens", 0)),
            completion_tokens=int(usage_data.get("outputTokens", 0)),
            total_tokens=int(usage_data.get("totalTokens", 0)),
        )

        # Get stop reason (Bedrock uses stopReason field)
        stop_reason = raw.get("stopReason", "end_turn")
        # Map Bedrock stop reasons to OpenAI-compatible ones
        stop_reason_map = {
            "end_turn": "stop",
            "max_tokens": "length",
            "stop_sequence": "stop",
            "content_filtered": "content_filter",
        }
        finish_reason = stop_reason_map.get(stop_reason, stop_reason)

        return UnifiedChatResponse(
            id=str(raw.get("ResponseMetadata", {}).get("RequestId", fallback_id)),
            object="chat.completion",
            created=created,
            model=model,
            choices=[
                Choice(
                    index=0,
                    message={
                        "role": "assistant",
                        "content": text_content,
                    },
                    finish_reason=finish_reason,
                )
            ],
            usage=usage,
        )
