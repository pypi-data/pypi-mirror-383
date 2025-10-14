"""Comparison mode orchestration.

Implements side-by-side provider invocation with fairness constraints and
observability. Both providers receive identically preprocessed messages, are
invoked in parallel with per-provider and overall timeouts enforced, and
metrics/traces are emitted for each call.

Returned value is a ``ComparisonResult`` containing per-provider outcomes and a
computed winner signal based on response time (extensible for quality/cost).
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Literal

from opentelemetry import trace

from .._context import RequestContext
from .._exceptions import ComparisonError
from .._logging import logger
from .._retry import with_retry
from ..adapters.registry import get_adapter
from ..metrics.emitter import (
    active_requests,
    request_duration_seconds,
    requests_total,
    ttfb_seconds,
)
from ..models.comparison import ComparativeMetrics, ComparisonResult, ProviderResult
from ..models.config import TimeoutConfig
from ..models.request import ChatRequest, Message
from ..models.response import ResponseMetrics, UnifiedChatResponse

tracer = trace.get_tracer(__name__)


def preprocess_messages(messages: list[dict[str, object]]) -> list[dict[str, str]]:
    """Normalize incoming message dicts into a safe, trimmed format.

    Ensures roles are strings and content is stripped of surrounding whitespace.
    """
    return [
        {
            "role": str(m.get("role", "user")),
            "content": str(m.get("content", "")).strip(),
        }
        for m in messages
    ]


def normalize_role(value: str) -> Literal["system", "user", "assistant"]:
    """Coerce free-form role strings into one of the allowed values."""
    v = value.lower()
    if v == "system":
        return "system"
    if v == "assistant":
        return "assistant"
    return "user"


async def _invoke_with_timeout(
    provider: str, request: ChatRequest, provider_timeout: float
) -> tuple[str, UnifiedChatResponse | Exception, float, float]:
    """Invoke a single provider with retry and timeout, emitting metrics.

    Returns a tuple of (provider, result_or_exception, duration_seconds, ttfb_seconds).
    """
    adapter = get_adapter(provider)
    active_requests.labels(provider=provider).inc()
    start = time.perf_counter()
    ttfb = None
    try:
        with tracer.start_as_current_span(
            "provider.invoke", attributes={"provider": provider, "model": request.model}
        ):

            async def run_invoke() -> UnifiedChatResponse:
                return await with_retry(adapter.invoke_with_limit)(request)

            result = await asyncio.wait_for(run_invoke(), timeout=provider_timeout)
            duration = time.perf_counter() - start
            ttfb = duration
            requests_total.labels(provider=provider, model=request.model, status="success").inc()
            request_duration_seconds.labels(provider=provider, model=request.model).observe(
                duration
            )
            ttfb_seconds.labels(provider=provider, model=request.model).observe(ttfb)
            return provider, result, duration, ttfb
    except Exception as exc:  # noqa: BLE001
        duration = time.perf_counter() - start
        requests_total.labels(provider=provider, model=request.model, status="error").inc()
        logger.error(
            "provider_invocation_failed",
            provider=provider,
            model=request.model,
            error=type(exc).__name__,
            duration_ms=duration * 1000.0,
        )
        return provider, exc, duration, ttfb or duration
    finally:
        active_requests.labels(provider=provider).dec()


async def compare_async(
    *,
    providers: list[str],
    model: str,
    messages: list[dict[str, object]],
    timeouts: TimeoutConfig | None = None,
) -> ComparisonResult:
    """Run a side-by-side comparison of two providers in parallel.

    Enforces fairness (identical inputs), per-provider timeouts, overall
    comparison timeout, and collects metrics and tracing data.
    """
    if len(providers) != 2:
        raise ValueError("Exactly two providers must be specified for comparison")

    timeouts = timeouts or TimeoutConfig(
        connect_timeout=5.0,
        read_timeout=30.0,
        provider_timeout=60.0,
        sdk_timeout=90.0,
        comparison_timeout=120.0,
    )
    assert timeouts.comparison_timeout > timeouts.provider_timeout

    normalized_messages = preprocess_messages(messages)
    ctx = RequestContext.new()

    req = ChatRequest(
        provider="comparison",
        model=model,
        messages=[
            Message(
                role=normalize_role(m["role"]),
                content=m["content"],
            )
            for m in normalized_messages
        ],
        temperature=0.7,
        max_tokens=256,
    )

    provider_timeout = timeouts.provider_timeout
    with tracer.start_as_current_span("comparison.compare"):
        tasks: list[asyncio.Task[tuple[str, UnifiedChatResponse | Exception, float, float]]] = [
            asyncio.create_task(
                _invoke_with_timeout(
                    providers[0],
                    ChatRequest(
                        provider=providers[0],
                        model=model,
                        messages=req.messages,
                        temperature=req.temperature,
                        max_tokens=req.max_tokens,
                    ),
                    provider_timeout,
                )
            ),
            asyncio.create_task(
                _invoke_with_timeout(
                    providers[1],
                    ChatRequest(
                        provider=providers[1],
                        model=model,
                        messages=req.messages,
                        temperature=req.temperature,
                        max_tokens=req.max_tokens,
                    ),
                    provider_timeout,
                )
            ),
        ]
        try:
            done = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=False), timeout=timeouts.comparison_timeout
            )
        except asyncio.TimeoutError:
            results: list[tuple[str, UnifiedChatResponse | Exception, float, float]] = []
            done_tasks = [t for t in tasks if t.done()]
            for t in done_tasks:
                results.append(t.result())
            while len(results) < 2:
                results.append(("unknown", ComparisonError("timeout"), 0.0, 0.0))
            a_provider, a_result, a_duration, a_ttfb = results[0]
            b_provider, b_result, b_duration, b_ttfb = results[1]
        else:
            a_provider, a_result, a_duration, a_ttfb = done[0]
            b_provider, b_result, b_duration, b_ttfb = done[1]

    def to_provider_result(
        provider: str, value: UnifiedChatResponse | Exception, duration: float, ttfb: float
    ) -> ProviderResult:
        if isinstance(value, UnifiedChatResponse):
            return ProviderResult(
                provider=provider,
                model=model,
                success=True,
                response=value,
                error=None,
                metrics=ResponseMetrics(duration_ms=duration * 1000.0, ttfb_ms=ttfb * 1000.0),
            )
        return ProviderResult(
            provider=provider,
            model=model,
            success=False,
            response=None,
            error=type(value).__name__,
            metrics=ResponseMetrics(duration_ms=duration * 1000.0, ttfb_ms=ttfb * 1000.0),
        )

    provider_a = to_provider_result(a_provider, a_result, a_duration, a_ttfb)
    provider_b = to_provider_result(b_provider, b_result, b_duration, b_ttfb)

    speed_diff = (provider_b.metrics.duration_ms or 0.0) - (provider_a.metrics.duration_ms or 0.0)

    return ComparisonResult(
        correlation_id=ctx.correlation_id,
        timestamp=datetime.utcnow(),
        request=req,
        provider_a=provider_a,
        provider_b=provider_b,
        comparative_metrics=ComparativeMetrics(speed_difference_ms=speed_diff),
        winner=("provider_a" if speed_diff > 0 else ("provider_b" if speed_diff < 0 else "tie")),
    )
