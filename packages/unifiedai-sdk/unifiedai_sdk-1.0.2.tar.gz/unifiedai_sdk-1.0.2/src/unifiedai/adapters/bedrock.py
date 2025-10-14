"""AWS Bedrock adapter (stub implementation).

Translates UnifiedAI requests into Bedrock-specific calls and normalizes
responses back into ``UnifiedChatResponse``. Replace stub logic with real
provider integration.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator

from ..models.request import ChatRequest
from ..models.response import Choice, ProviderMetadata, ResponseMetrics, UnifiedChatResponse, Usage
from ..models.stream import StreamChunk
from .base import BaseAdapter


class BedrockAdapter(BaseAdapter):
    @property
    def provider_name(self) -> str:
        return "bedrock"

    async def invoke(self, request: ChatRequest) -> UnifiedChatResponse:
        started = int(time.time())
        return UnifiedChatResponse(
            id="br-1",
            object="chat.completion",
            created=started,
            model=request.model,
            choices=[Choice(index=0, message={"role": "assistant", "content": "[bedrock stub]"})],
            usage=Usage(),
            provider_metadata=ProviderMetadata(provider=self.provider_name, raw=None),
            metrics=ResponseMetrics(duration_ms=0.0, ttfb_ms=0.0),
        )

    async def invoke_streaming(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        text = "Streaming from Bedrock stub."
        for i, ch in enumerate(text):
            await asyncio.sleep(0.01)
            yield StreamChunk(
                id="br-1", model=request.model, index=i, delta={"role": "assistant", "content": ch}
            )
        yield StreamChunk(
            id="br-1",
            model=request.model,
            index=len(text),
            delta={"role": "assistant", "content": ""},
            finish_reason="stop",
        )

    async def health_check(self) -> dict[str, str]:
        return {"status": "healthy", "provider": self.provider_name}
