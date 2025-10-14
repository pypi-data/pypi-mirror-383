"""Unified error hierarchy for the SDK."""

from __future__ import annotations

from dataclasses import dataclass


class SDKError(Exception):
    """Base exception for all SDK errors"""


@dataclass
class ProviderError(SDKError):
    """Provider-specific error with original error details.

    Attributes:
        provider: Provider identifier (e.g., "cerebras", "bedrock")
        original_error: The underlying exception that caused this error
    """

    provider: str
    original_error: Exception | None = None

    def __str__(self) -> str:
        """Return human-readable error message."""
        if self.original_error:
            return f"Provider '{self.provider}' error: {str(self.original_error)}"
        return f"Provider '{self.provider}' error"


@dataclass
class RateLimitError(ProviderError):
    """Rate limit exceeded error.

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header)
    """

    retry_after: int | None = None

    def __str__(self) -> str:
        """Return human-readable error message."""
        base_msg = f"Provider '{self.provider}' rate limit exceeded"
        if self.retry_after:
            return f"{base_msg}. Retry after {self.retry_after} seconds"
        if self.original_error:
            return f"{base_msg}: {str(self.original_error)}"
        return base_msg


class AuthenticationError(ProviderError):
    """Authentication/authorization error."""

    def __str__(self) -> str:
        """Return human-readable error message."""
        if self.original_error:
            return f"Provider '{self.provider}' authentication failed: {str(self.original_error)}"
        return f"Provider '{self.provider}' authentication failed"


class TimeoutError(ProviderError):
    """Request timeout error."""

    def __str__(self) -> str:
        """Return human-readable error message."""
        if self.original_error:
            return f"Provider '{self.provider}' timeout: {str(self.original_error)}"
        return f"Provider '{self.provider}' timeout"


class InvalidRequestError(SDKError):
    """Invalid request parameters."""

    def __init__(self, message: str = "Invalid request"):
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """Return human-readable error message."""
        return self.message


@dataclass
class ComparisonError(SDKError):
    """Comparison mode error.

    Attributes:
        successful_provider: Provider that succeeded (if any)
        failed_provider: Provider that failed (if any)
    """

    successful_provider: str | None = None
    failed_provider: str | None = None

    def __str__(self) -> str:
        """Return human-readable error message."""
        if self.successful_provider and self.failed_provider:
            return (
                f"Comparison partial failure: '{self.failed_provider}' failed, "
                f"'{self.successful_provider}' succeeded"
            )
        if self.failed_provider:
            return f"Comparison failed for provider '{self.failed_provider}'"
        return "Comparison failed"
