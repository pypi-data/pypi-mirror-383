from __future__ import annotations

from fastapi import FastAPI, WebSocket
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from unifiedai import UnifiedAI
from unifiedai.health import health_check

app = FastAPI()


@app.post("/chat/solo")
async def chat_solo(payload: dict):  # type: ignore[no-untyped-def]
    async with UnifiedAI() as client:
        return await client.chat.completions.create_async(**payload)


@app.post("/chat/compare")
async def chat_compare(payload: dict):  # type: ignore[no-untyped-def]
    async with UnifiedAI() as client:
        return await client.chat.completions.create_async(**payload)


@app.get("/health")
async def health():
    status = await health_check(["cerebras", "bedrock"])
    return status.dict()


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.websocket("/chat/stream")
async def chat_stream(ws: WebSocket):
    await ws.accept()
    payload = await ws.receive_json()
    provider = payload.get("provider")
    model = payload.get("model")
    messages = payload.get("messages", [])
    async with UnifiedAI(provider=provider, model=model) as client:
        async for chunk in client.chat.completions.stream(
            provider=provider, model=model, messages=messages
        ):
            await ws.send_json({"type": "chunk", "data": chunk.dict()})
    await ws.send_json({"type": "done"})
