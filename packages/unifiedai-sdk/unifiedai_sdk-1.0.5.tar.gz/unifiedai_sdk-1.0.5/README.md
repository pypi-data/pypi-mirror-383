# UnifiedAI SDK

OpenAI-compatible Python SDK unifying multiple providers (Cerebras, AWS Bedrock) with Solo and Comparison modes, strict models, and built‑in telemetry.

## Highlights
- OpenAI-like API: `UnifiedAI().chat.completions.create(...)` (sync) and `AsyncUnifiedAI` (async)
- Pluggable adapters: Cerebras, Bedrock (extensible)
- Modes: Solo and side‑by‑side Comparison
- Observability: structured logs, Prometheus metrics (SDK), tracing hooks
- Credentials: pass at client construction or use env

## Install
From PyPI (core):
```bash
pip install unifiedai-sdk
```

Optional extras:
```bash
# Cerebras Cloud SDK integration
pip install "unifiedai-sdk[cerebras]"

# HTTP/2 support for httpx
pip install "unifiedai-sdk[http2]"
```

From GitHub (optional):
```bash
pip install git+https://github.com/<your-org-or-user>/<your-repo>.git#subdirectory=cerebras
```

## Usage

### Sync (scripts/CLI)
```python
from unifiedai import UnifiedAI

client = UnifiedAI(
    provider="cerebras",
    model="llama3",
    credentials={"api_key": "csk-..."},  # or set CEREBRAS_KEY in env
)
resp = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello"}]
)
print(resp.choices[0].message["content"])
```

### Async (web backends)
```python
from unifiedai import AsyncUnifiedAI

async with AsyncUnifiedAI(provider="cerebras", model="llama3") as client:
    resp = await client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello"}]
    )
```

### Streaming (async)
```python
async with AsyncUnifiedAI(provider="cerebras", model="llama3") as client:
    async for chunk in client.chat.completions.stream(
        messages=[{"role": "user", "content": "Stream this"}]
    ):
        print(chunk.delta.get("content", ""), end="")
```

### Comparison (two providers)
```python
from unifiedai import AsyncUnifiedAI

async with AsyncUnifiedAI() as client:
    result = await client.compare(
        providers=["cerebras", "bedrock"],
        model="llama3",
        messages=[{"role": "user", "content": "Compare outputs"}],
    )
    print(result.winner, result.comparative_metrics.speed_difference_ms)
```

## Credentials
- Precedence: per‑provider credentials > global client credentials > environment (SDKConfig).
- Cerebras: set `CEREBRAS_KEY` or pass `credentials={"api_key": "..."}`.
- Bedrock: planned; wire `credentials_by_provider` similarly.

## FastAPI demo (Swagger UI)
```bash
uvicorn apps.chat.backend:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
```

## Project Structure
- `src/unifiedai/`: SDK implementation (clients, adapters, models, core)
- `examples/`: usage examples (solo, streaming, comparison)
- `apps/chat/`: demo FastAPI backend
- `tests/`: unit tests

## License
MIT
