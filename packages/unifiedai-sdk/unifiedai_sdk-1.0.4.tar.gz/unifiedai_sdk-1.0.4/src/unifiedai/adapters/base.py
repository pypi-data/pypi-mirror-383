"""Adapter base class and concurrency/HTTP pooling utilities.

All provider adapters must inherit from :class:`BaseAdapter` and implement the
abstract methods. The base class provides:

- A shared, pooled ``httpx.AsyncClient`` for connection reuse and HTTP/2 support
- A semaphore to enforce per-adapter concurrency limits
- Convenience wrappers ``invoke_with_limit`` and ``stream_with_limit`` that
  apply the semaphore around provider calls
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

import httpx

from ..models.request import ChatRequest
from ..models.response import UnifiedChatResponse
from ..models.stream import StreamChunk


class BaseAdapter(ABC):
    """Abstract base class for all provider adapters.

    Subclasses must implement ``provider_name``, ``invoke``, ``invoke_streaming``,
    and ``health_check``. Implementations are responsible for authentication,
    provider-specific request translation, error mapping into the SDK's
    exceptions, and response normalization to ``UnifiedChatResponse``.

    Args:
        max_concurrent: Maximum concurrent requests per adapter instance.
        timeout: Optional custom ``httpx.Timeout`` configuration.
    """

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
        """Return provider identifier.

        Returns:
            str: Short provider key (e.g., "cerebras", "bedrock").
        """

    @abstractmethod
    async def invoke(self, request: ChatRequest) -> UnifiedChatResponse:
        """Execute provider-specific API call.

        Args:
            request: Validated chat request.

        Returns:
            UnifiedChatResponse: Normalized OpenAI-style response.
        """

    @abstractmethod
    def invoke_streaming(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Stream responses from provider as :class:`StreamChunk`.

        Implementations should be async generators yielding incremental deltas.
        """

    @abstractmethod
    async def health_check(self) -> dict[str, str]:
        """Check provider availability.

        Returns:
            dict[str, str]: Minimal provider health payload.
        """

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def invoke_with_limit(self, request: ChatRequest) -> UnifiedChatResponse:
        """Run ``invoke`` under the adapter's concurrency limit."""
        async with self._semaphore:
            return await self.invoke(request)

    async def stream_with_limit(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Run ``invoke_streaming`` under the adapter's concurrency limit."""
        async with self._semaphore:
            async for chunk in self.invoke_streaming(request):
                yield chunk
