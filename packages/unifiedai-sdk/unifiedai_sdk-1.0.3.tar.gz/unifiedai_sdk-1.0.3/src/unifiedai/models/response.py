"""Response models normalized to OpenAI-compatible schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Choice(BaseModel):
    model_config = ConfigDict(strict=True)
    index: int
    message: dict[str, str]
    finish_reason: str | None = None


class Usage(BaseModel):
    model_config = ConfigDict(strict=True)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ProviderMetadata(BaseModel):
    model_config = ConfigDict(strict=True)
    provider: str
    raw: dict[str, object] | None = None


class ResponseMetrics(BaseModel):
    model_config = ConfigDict(strict=True)
    duration_ms: float | None = None
    ttfb_ms: float | None = None


class UnifiedChatResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    id: str
    object: Literal["chat.completion"]
    created: int
    model: str
    choices: list[Choice]
    usage: Usage = Field(default_factory=Usage)
    provider_metadata: ProviderMetadata | None = None
    metrics: ResponseMetrics | None = None
