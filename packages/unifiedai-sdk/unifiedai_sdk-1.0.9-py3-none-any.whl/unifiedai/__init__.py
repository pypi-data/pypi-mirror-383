from __future__ import annotations

__version__ = "1.0.1"

from ._async_client import AsyncUnifiedAI
from ._client import UnifiedClient as UnifiedAI
from ._exceptions import (
    AuthenticationError,
    ComparisonError,
    InvalidRequestError,
    ProviderError,
    RateLimitError,
    SDKError,
    TimeoutError,
)
from ._health import health_check

__all__ = [
    "UnifiedAI",
    "AsyncUnifiedAI",
    "health_check",
    "SDKError",
    "ProviderError",
    "RateLimitError",
    "AuthenticationError",
    "TimeoutError",
    "InvalidRequestError",
    "ComparisonError",
    "__version__",
]
