"""Health check aggregation across registered providers."""

from __future__ import annotations

import asyncio
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .adapters.registry import get_adapter


class ProviderHealth(BaseModel):
    model_config = ConfigDict(strict=True)

    provider: str
    status: str


class HealthStatus(BaseModel):
    model_config = ConfigDict(strict=True)

    status: str
    providers: dict[str, ProviderHealth]
    timestamp: datetime


async def health_check(providers: list[str]) -> HealthStatus:
    adapters = [get_adapter(p) for p in providers]
    results = await asyncio.gather(*[a.health_check() for a in adapters], return_exceptions=True)
    provider_map: dict[str, ProviderHealth] = {}
    overall = "healthy"
    for p, r in zip(providers, results):
        if isinstance(r, Exception):
            provider_map[p] = ProviderHealth(provider=p, status="unhealthy")
            overall = "degraded"
        else:
            provider_map[p] = ProviderHealth(provider=p, status=r.get("status", "unknown"))  # type: ignore[union-attr]
    return HealthStatus(status=overall, providers=provider_map, timestamp=datetime.utcnow())
