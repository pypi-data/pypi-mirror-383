"""Cerebras adapter integration.

This adapter uses the official Cerebras Cloud Python SDK to perform chat
completions and normalizes responses to the SDK's ``UnifiedChatResponse``
schema. Streaming is supported when the Cerebras SDK exposes a streaming API;
otherwise, a single terminal chunk is yielded.
"""

from __future__ import annotations

import asyncio
import re
import time
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

# Optional import; we keep a constructor reference to avoid mypy "assign to type" issues
CerebrasCtor: Any
try:  # pragma: no cover - import availability depends on environment
    from cerebras.cloud.sdk import Cerebras as _Cerebras  # type: ignore[import-not-found]

    CerebrasCtor = _Cerebras
except Exception:  # noqa: BLE001
    CerebrasCtor = None


class CerebrasAdapter(BaseAdapter):
    def __init__(
        self,
        max_concurrent: int = 10,
        *,
        credentials: dict[str, str] | None = None,
        return_reasoning: bool = True,
    ) -> None:
        super().__init__(max_concurrent=max_concurrent)
        self._cb_client: Any | None = None
        self._credentials = credentials or {}
        self._return_reasoning = return_reasoning

    @property
    def provider_name(self) -> str:
        return "cerebras"

    async def invoke(self, request: ChatRequest) -> UnifiedChatResponse:
        """Call Cerebras chat API and normalize to UnifiedChatResponse."""
        client = await self._get_or_create_client()

        started_perf = time.perf_counter()
        started_epoch = int(time.time())

        try:
            # The Cerebras SDK is synchronous; run it in a thread to avoid blocking.
            def _call() -> dict[str, Any]:  # Provider response as dict-like
                resp = client.chat.completions.create(
                    model=request.model,
                    messages=[m.model_dump() for m in request.messages],
                )
                # Some SDKs return model objects; ensure dict-like access
                if hasattr(resp, "model_dump"):
                    data = resp.model_dump()
                else:
                    data = resp
                return cast(dict[str, Any], data)

            raw: dict[str, Any] = await asyncio.to_thread(_call)
        except Exception as exc:  # noqa: BLE001
            # Map common auth/validation issues to our taxonomy
            message = str(exc).lower()
            if "api key" in message or "unauthoriz" in message:
                raise AuthenticationError(provider=self.provider_name, original_error=exc) from exc
            if "invalid" in message or "bad request" in message:
                raise InvalidRequestError(str(exc)) from exc
            raise ProviderError(provider=self.provider_name, original_error=exc) from exc

        # Client-measured total time (includes network, SDK overhead, etc.)
        duration_ms = (time.perf_counter() - started_perf) * 1000.0

        reasoning, cleaned = self._extract_reasoning_and_answer(raw)

        unified = self._normalize_response(
            raw=raw,
            fallback_id=raw.get("id") or "cb-unknown",
            created=raw.get("created") or started_epoch,
            model=request.model,
            override_content=cleaned,
        )
        # Extract Cerebras-provided timing metrics (server-side measurements)
        time_info = raw.get("time_info") or {}
        total_time = None
        completion_time = None
        prompt_time = None
        queue_time = None
        try:
            total_time = float(time_info.get("total_time") or 0.0)
            completion_time = float(time_info.get("completion_time") or 0.0)
            prompt_time = float(time_info.get("prompt_time") or 0.0)
            queue_time = float(time_info.get("queue_time") or 0.0)
        except Exception:  # noqa: BLE001
            total_time = completion_time = prompt_time = queue_time = None

        # Use Cerebras server-side metrics when available (more accurate)
        round_trip_time_s = (
            total_time if (total_time and total_time > 0) else (duration_ms / 1000.0)
        )
        inference_time_s = (
            completion_time if (completion_time and completion_time > 0) else round_trip_time_s
        )

        # TTFB: Time to first byte from server (queue wait + prompt processing)
        # Use Cerebras-provided timings when available, else fall back to client measurement
        if (prompt_time or 0) + (queue_time or 0) > 0:
            ttfb_ms = ((prompt_time or 0.0) + (queue_time or 0.0)) * 1000.0
        else:
            # Fallback: use client measurement (less accurate but better than nothing)
            ttfb_ms = duration_ms

        output_tokens = unified.usage.completion_tokens or 0
        total_tokens = unified.usage.total_tokens or 0
        input_tokens = unified.usage.prompt_tokens or 0

        unified.metrics = ResponseMetrics(
            duration_ms=duration_ms,
            ttfb_ms=ttfb_ms,
            round_trip_time_s=round_trip_time_s,
            inference_time_s=inference_time_s,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_tokens=input_tokens,
        )
        meta_raw = dict(raw)
        if self._return_reasoning and reasoning:
            meta_raw["reasoning"] = reasoning
        unified.provider_metadata = ProviderMetadata(provider=self.provider_name, raw=meta_raw)
        return unified

    async def invoke_streaming(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Stream tokens from Cerebras if SDK supports streaming; else one-shot.

        If streaming isn't supported, yields a single terminal chunk built from
        the non-streaming ``invoke`` result.
        """
        client = await self._get_or_create_client()

        # If the SDK exposes a streaming flag/iterator, use it; otherwise fallback.
        if callable(getattr(client.chat.completions, "create", None)):
            try:
                # Attempt to use a streaming mode if available
                def _call_stream() -> list[dict[str, Any]]:
                    # Many SDKs yield chunks when stream=True; coalesce here to simplify
                    stream_resp = client.chat.completions.create(
                        model=request.model,
                        messages=[m.model_dump() for m in request.messages],
                        stream=True,
                    )
                    chunks: list[dict[str, Any]] = []
                    for ev in stream_resp:
                        item = ev.model_dump() if hasattr(ev, "model_dump") else ev
                        chunks.append(cast(dict[str, Any], item))
                    return chunks

                chunks = await asyncio.to_thread(_call_stream)
                idx = 0
                for ev in chunks:
                    delta_text = (((ev.get("choices") or [{}])[0]).get("delta") or {}).get(
                        "content"
                    ) or ""
                    if delta_text:
                        yield StreamChunk(
                            id=str(ev.get("id") or "cb-unknown"),
                            model=request.model,
                            index=idx,
                            delta={"role": "assistant", "content": delta_text},
                        )
                        idx += 1
                yield StreamChunk(
                    id=str((chunks[-1] if chunks else {}).get("id") or "cb-unknown"),
                    model=request.model,
                    index=idx,
                    delta={"role": "assistant", "content": ""},
                    finish_reason="stop",
                )
                return
            except Exception:
                # Fallback to non-streaming if streaming path fails
                pass

        # Fallback: one-shot invoke() then emit a single stop chunk
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
        """Check if the Cerebras client can be created and is healthy.

        Returns:
            Dict with 'status' ('healthy' or 'unhealthy') and 'provider'.
        """
        try:
            await self._get_or_create_client()
            return {"status": "healthy", "provider": self.provider_name}
        except Exception:  # noqa: BLE001
            return {"status": "unhealthy", "provider": self.provider_name}

    async def list_models(self) -> list[Model]:
        """List available models from Cerebras using the SDK's models API.

        Calls the Cerebras SDK's `client.models.list()` to get the current list
        of available models. Falls back to a static list if the API call fails.

        Returns:
            list[Model]: List of available Cerebras models.
        """
        try:
            client = await self._get_or_create_client()

            # Call Cerebras SDK's models.list() API
            def _list_models() -> list[dict[str, Any]]:
                response = client.models.list()
                # Response format: {"object": "list", "data": [{model objects}]}
                if hasattr(response, "data"):
                    # SDK returns a structured response
                    result: list[dict[str, Any]] = [
                        model.model_dump() if hasattr(model, "model_dump") else dict(model)
                        for model in response.data
                    ]
                    return result
                elif isinstance(response, dict) and "data" in response:
                    # Direct dict response
                    return cast(list[dict[str, Any]], response["data"])
                return []

            models_data = await asyncio.to_thread(_list_models)

            # Convert to our Model format
            models = []
            for model_dict in models_data:
                models.append(
                    Model(
                        id=model_dict.get("id", ""),
                        object="model",
                        created=model_dict.get("created", 0),
                        owned_by=model_dict.get("owned_by", "cerebras"),
                    )
                )

            return models if models else self._get_fallback_models()

        except Exception:  # noqa: BLE001
            # Fallback to static list if API call fails
            return self._get_fallback_models()

    def _get_fallback_models(self) -> list[Model]:
        """Return static list of common Cerebras models as fallback."""
        return [
            Model(
                id="llama3.1-8b",
                object="model",
                created=1721692800,
                owned_by="Meta",
            ),
            Model(
                id="llama3.1-70b",
                object="model",
                created=1721692800,
                owned_by="Meta",
            ),
            Model(
                id="llama-3.3-70b",
                object="model",
                created=1733443200,
                owned_by="Meta",
            ),
            Model(
                id="llama-4-scout-17b-16e-instruct",
                object="model",
                created=1735689600,
                owned_by="Meta",
            ),
            Model(
                id="qwen-3-32b",
                object="model",
                created=1735689600,
                owned_by="Qwen",
            ),
            Model(
                id="gpt-oss-120b",
                object="model",
                created=1735689600,
                owned_by="cerebras",
            ),
        ]

    async def _get_or_create_client(self) -> Any:
        """Create or reuse a Cerebras SDK client using SDKConfig secrets."""
        if self._cb_client is not None:
            return self._cb_client
        if CerebrasCtor is None:
            raise ProviderError(
                provider=self.provider_name,
                original_error=ImportError(
                    "cerebras-cloud SDK not installed. Run `pip install cerebras-cloud-sdk`"
                ),
            )
        # Precedence: provided credentials > env config
        api_key = self._credentials.get("api_key")
        if not api_key:
            cfg = SDKConfig.load()
            api_key = cfg.cerebras_key.get_secret_value()
        if not api_key:
            raise AuthenticationError(
                provider=self.provider_name, original_error=Exception("Missing CEREBRAS_KEY")
            ) from None
        # The Cerebras SDK is typically synchronous; construct once and reuse
        self._cb_client = CerebrasCtor(api_key=api_key)
        return self._cb_client

    def _normalize_response(
        self,
        *,
        raw: dict[str, Any],
        fallback_id: str,
        created: int,
        model: str,
        override_content: str | None = None,
    ) -> UnifiedChatResponse:
        """Normalize Cerebras response dict to UnifiedChatResponse."""
        # Choices/message extraction with fallbacks
        choices_raw = raw.get("choices") or []
        first = choices_raw[0] if choices_raw else {}
        message = first.get("message") or {"role": "assistant", "content": first.get("text") or ""}
        if override_content is not None:
            message = {
                "role": str(message.get("role") or "assistant"),
                "content": override_content,
            }

        usage = raw.get("usage") or {}
        u = Usage(
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            total_tokens=int(usage.get("total_tokens") or 0),
        )

        unified = UnifiedChatResponse(
            id=str(raw.get("id") or fallback_id),
            object="chat.completion",
            created=int(raw.get("created") or created),
            model=str(raw.get("model") or model),
            choices=[
                Choice(
                    index=int(first.get("index") or 0),
                    message={
                        "role": str(message.get("role") or "assistant"),
                        "content": str(message.get("content") or ""),
                    },
                    finish_reason=(first.get("finish_reason")),
                )
            ],
            usage=u,
        )
        return unified

    def _extract_reasoning_and_answer(self, raw: dict[str, Any]) -> tuple[str | None, str]:
        """Extract <think>...</think> as reasoning and return cleaned answer.

        Returns (reasoning_or_None, cleaned_content).
        """
        text: str = ""
        try:
            choices = raw.get("choices") or []
            if choices:
                first = choices[0]
                msg = first.get("message") or {}
                text = msg.get("content") or first.get("text") or ""
        except Exception:  # noqa: BLE001
            text = ""

        if not isinstance(text, str):
            text = str(text)

        m = re.search(r"<think>(.*?)</think>", text, flags=re.DOTALL | re.IGNORECASE)
        reasoning = m.group(1).strip() if m else None
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
        return reasoning, cleaned
