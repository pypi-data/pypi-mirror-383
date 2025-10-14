"""
This module contains mock responses that simulate
OpenAI-style completion outputs for Cerebras and Bedrock.
These are placeholders until real API integration is added.
"""

MOCK_RESPONSE_CEREBRAS = {
    "id": "resp-001",
    "object": "chat.completion",
    "model": "llama3.1-8b",
    "choices": [
        {"message": {"role": "assistant", "content": "This is a mock response from Cerebras."}}
    ],
    "usage": {"prompt_tokens": 5, "completion_tokens": 15, "total_tokens": 20},
    "metrics": {"latency_ms": 320, "ttfb_ms": 110, "payload_size_kb": 4},
}

MOCK_RESPONSE_BEDROCK = {
    "id": "resp-002",
    "object": "chat.completion",
    "model": "qwen-1.5b",
    "choices": [
        {"message": {"role": "assistant", "content": "This is a mock response from AWS Bedrock."}}
    ],
    "usage": {"prompt_tokens": 6, "completion_tokens": 12, "total_tokens": 18},
    "metrics": {"latency_ms": 410, "ttfb_ms": 140, "payload_size_kb": 5},
}