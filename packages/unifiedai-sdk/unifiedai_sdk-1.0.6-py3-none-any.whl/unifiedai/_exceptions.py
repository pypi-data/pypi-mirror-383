"""Unified error hierarchy for the SDK."""

from __future__ import annotations

from dataclasses import dataclass


class SDKError(Exception):
    """Base exception for all SDK errors"""


@dataclass
class ProviderError(SDKError):
    provider: str
    original_error: Exception | None = None


class RateLimitError(ProviderError):
    retry_after: int | None = None


class AuthenticationError(ProviderError):
    pass


class TimeoutError(ProviderError):
    pass


class InvalidRequestError(SDKError):
    pass


@dataclass
class ComparisonError(SDKError):
    successful_provider: str | None = None
    failed_provider: str | None = None
