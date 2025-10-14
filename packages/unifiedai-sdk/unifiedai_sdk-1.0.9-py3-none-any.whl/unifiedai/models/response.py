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
    """Performance metrics for a chat completion request.

    Attributes:
        duration_ms: Client-measured total time (includes network, SDK overhead).
            This is measured from request start to response received on the client.
        ttfb_ms: Time to first byte from server perspective (queue + prompt processing).
            For streaming, this is when the first token arrives. For non-streaming,
            this approximates when the server started generating the response.
        round_trip_time_s: Server-side total time (from provider's time_info).
            More accurate than duration_ms as it excludes network latency and SDK overhead.
        inference_time_s: Pure token generation time (from provider's completion_time).
            This is the time spent actually generating tokens, excluding prompt processing.
        output_tokens: Number of tokens generated in the response.
        total_tokens: Total tokens (input + output).
        input_tokens: Number of tokens in the prompt.

    Note:
        - duration_ms >= round_trip_time_s (client time includes network overhead)
        - ttfb_ms is typically much smaller than duration_ms (queue + prompt vs. full request)
        - inference_time_s < round_trip_time_s (excludes prompt processing and queue time)

    Example values from a real request:
        duration_ms: 2824.47        # Client: network + SDK + processing
        ttfb_ms: 213.43             # Server: queue (212ms) + prompt (0.7ms)
        round_trip_time_s: 2.46     # Server: total processing time
        inference_time_s: 2.25      # Server: pure token generation
    """

    model_config = ConfigDict(strict=True)
    duration_ms: float | None = None
    ttfb_ms: float | None = None
    round_trip_time_s: float | None = None
    inference_time_s: float | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    input_tokens: int | None = None


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
