from __future__ import annotations

from collections.abc import Awaitable
from typing import Callable, TypeVar

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .exceptions import RateLimitError, TimeoutError

T = TypeVar("T")


def with_retry(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitError, TimeoutError)),
        reraise=True,
    )
    async def wrapped(*args, **kwargs):  # type: ignore[no-untyped-def]
        return await func(*args, **kwargs)

    return wrapped


