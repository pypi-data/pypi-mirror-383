# Unified AI SDK

OpenAI-compatible Python SDK that unifies multiple providers (Cerebras, AWS Bedrock) with Solo and Comparison modes and built-in telemetry.

## Highlights
- OpenAI-like API surface: `UnifiedAI().chat.completions.create(...)`
- Providers via adapters: Cerebras, Bedrock (extensible)
- Modes: Solo and side-by-side Comparison
- Telemetry: total round-trip time, time-to-first-byte, tokens, costs (extensible)

## Install
```bash
pip install unifiedai
```

### Install from GitHub (optional)
```bash
pip install git+https://github.com/<your-org-or-user>/<your-repo>.git#subdirectory=cerebras
```
Note: The `subdirectory=cerebras` flag installs the package defined under `cerebras/pyproject.toml`.

## Quickstart
```python
from unifiedai import UnifiedAI

client = UnifiedAI(provider="cerebras", model="llama3")
resp = client.chat.completions.create(messages=[{"role": "user", "content": "Hello"}])
print(resp.choices[0].message["content"])  # OpenAI-like shape
```

## Project Structure
- `src/unifiedai/`: SDK implementation
- `tests/`: unit tests
- `examples/`: usage examples
- `apps/chat/`: demo chat UI

## License
MIT
