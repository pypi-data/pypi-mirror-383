from __future__ import annotations

from .base import BaseAdapter
from .bedrock import BedrockAdapter
from .cerebras import CerebrasAdapter


def get_adapter(provider: str) -> BaseAdapter:
    name = provider.lower()
    if name == "cerebras":
        return CerebrasAdapter()
    if name == "bedrock":
        return BedrockAdapter()
    raise ValueError(f"Unsupported provider: {provider}")


