from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

import httpx

from ..models.request import ChatRequest
from ..models.response import UnifiedChatResponse
from ..models.stream import StreamChunk


class BaseAdapter(ABC):
    def __init__(self, max_concurrent: int = 10, timeout: httpx.Timeout | None = None) -> None:
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=20, max_connections=100, keepalive_expiry=30.0
            ),
            timeout=timeout or httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0),
            http2=True,
            verify=True,
        )

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider identifier"""

    @abstractmethod
    async def invoke(self, request: ChatRequest) -> UnifiedChatResponse:
        """Execute provider-specific API call"""

    @abstractmethod
    def invoke_streaming(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Stream responses from provider as StreamChunk"""

    @abstractmethod
    async def health_check(self) -> dict[str, str]:
        """Check provider availability"""

    async def close(self) -> None:
        await self._client.aclose()

    async def invoke_with_limit(self, request: ChatRequest) -> UnifiedChatResponse:
        async with self._semaphore:
            return await self.invoke(request)

    async def stream_with_limit(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        async with self._semaphore:
            async for chunk in self.invoke_streaming(request):
                yield chunk


