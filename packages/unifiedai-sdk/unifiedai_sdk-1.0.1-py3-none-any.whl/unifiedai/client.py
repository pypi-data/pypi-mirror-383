from __future__ import annotations

import asyncio
import types
from collections.abc import AsyncIterator
from typing import Any

from .adapters.base import BaseAdapter
from .adapters.registry import get_adapter
from .context import RequestContext
from .logging import logger
from .models.config import TimeoutConfig
from .models.request import Message
from .models.response import UnifiedChatResponse
from .models.stream import StreamChunk


class _Completions:
    def __init__(self, client: UnifiedClient) -> None:
        self._client = client

    def create(
        self,
        *,
        provider: str | None = None,
        providers: list[str] | None = None,
        model: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> UnifiedChatResponse:
        if stream:
            raise ValueError("Use chat.completions.stream(...) for streaming responses")
        if providers:
            raise TypeError(
                "create returns UnifiedChatResponse; use compare_async for comparisons"
            )
        if provider or self._client.default_provider:
            adapter = self._client._get_or_create_adapter(
                provider or self._client.default_provider or ""
            )
            ctx = RequestContext.new()
            logger.info(
                "provider_invocation",
                correlation_id=ctx.correlation_id,
                provider=adapter.provider_name,
                model=model or self._client.default_model or "",
            )
            req_messages = [Message(**m) for m in (messages or [])]
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                result: UnifiedChatResponse = loop.run_until_complete(
                    adapter.invoke_with_limit(
                        request=self._client._build_request(
                            adapter.provider_name,
                            model or (self._client.default_model or ""),
                            req_messages,
                        )
                    )
                )
                return result
            finally:
                loop.close()
        raise ValueError("provider or providers must be specified")

    async def create_async(
        self,
        *,
        provider: str | None = None,
        providers: list[str] | None = None,
        model: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> UnifiedChatResponse:
        if providers:
            raise TypeError(
                "create_async returns UnifiedChatResponse; use compare_async for comparisons"
            )
        adapter = self._client._get_or_create_adapter(
            provider or self._client.default_provider or ""
        )
        req_messages = [Message(role=m["role"], content=m["content"]) for m in (messages or [])]
        unified = await adapter.invoke_with_limit(
            request=self._client._build_request(
                adapter.provider_name, model or (self._client.default_model or ""), req_messages
            )
        )
        return unified

    async def stream(
        self,
        *,
        provider: str | None = None,
        model: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        adapter = self._client._get_or_create_adapter(
            provider or self._client.default_provider or ""
        )
        req_messages = [Message(role=m["role"], content=m["content"]) for m in (messages or [])]
        async for chunk in adapter.stream_with_limit(
            request=self._client._build_request(
                adapter.provider_name, model or (self._client.default_model or ""), req_messages
            )
        ):
            yield chunk

    async def create_stream(
        self,
        *,
        provider: str | None = None,
        model: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        async for chunk in self.stream(provider=provider, model=model, messages=messages, **kwargs):
            yield chunk


class _ChatAPI:
    def __init__(self, client: UnifiedClient) -> None:
        self.completions = _Completions(client)


class UnifiedClient:
    def __init__(self, provider: str | None = None, model: str | None = None) -> None:
        self.default_provider = provider
        self.default_model = model
        self.chat = _ChatAPI(self)
        self._adapters: dict[str, BaseAdapter] = {}
        self.timeouts = TimeoutConfig(
            connect_timeout=5.0,
            read_timeout=30.0,
            provider_timeout=60.0,
            sdk_timeout=90.0,
            comparison_timeout=120.0,
        )

    def _get_or_create_adapter(self, provider: str) -> BaseAdapter:
        if provider not in self._adapters:
            self._adapters[provider] = get_adapter(provider)
        return self._adapters[provider]

    def _build_request(self, provider: str, model: str, messages: list[Message]):  # type: ignore[no-untyped-def]
        from .models.request import ChatRequest

        return ChatRequest(
            provider=provider,
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=256,
        )

    async def __aenter__(self) -> UnifiedClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        await asyncio.gather(
            *[adapter.close() for adapter in self._adapters.values()], return_exceptions=True
        )


