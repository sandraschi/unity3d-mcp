"""
LLM Chat API — streaming + non-streaming endpoints for the webapp chat.

Mounted alongside the MCP ASGI app via Starlette routing.
"""

from __future__ import annotations

import json
import logging
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

log = logging.getLogger(__name__)

chat_app = FastAPI(title="unity3d-mcp-chat")


async def _stream_ollama(base_url: str, model: str, messages: list[dict]):
    url = base_url.rstrip("/") + "/api/chat"
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", url, json={"model": model, "messages": messages, "stream": True}) as resp:
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield f"data: {json.dumps({'c': content})}\n\n"
                except json.JSONDecodeError:
                    pass
            yield "data: [DONE]\n\n"


async def _stream_openai(base_url: str, model: str, messages: list[dict], api_key: str = ""):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    url = base_url.rstrip("/") + "/chat/completions"
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream(
            "POST",
            url,
            json={"model": model, "messages": messages, "stream": True, "max_tokens": 1024},
            headers=headers,
        ) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        yield "data: [DONE]\n\n"
                        return
                    try:
                        chunk = json.loads(data_str)
                        content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if content:
                            yield f"data: {json.dumps({'c': content})}\n\n"
                    except json.JSONDecodeError:
                        pass


@chat_app.post("/llm/chat/stream")
async def llm_chat_stream(request: Request):
    body = await request.json()
    provider = body.get("provider", "ollama")
    model = body.get("model", "llama3.2")
    messages = body.get("messages", [])
    prompt = body.get("prompt", "")
    body.get("personality", "professional")
    system = body.get("system", "")
    base_url = body.get("base_url", "")

    if not base_url:
        base_url = {
            "ollama": "http://localhost:11434",
            "lmstudio": "http://localhost:1234/v1",
            "openai": "https://api.openai.com/v1",
            "deepseek": "https://api.deepseek.com/v1",
        }.get(provider, "http://localhost:11434")

    chat_messages = []
    if system:
        chat_messages.append({"role": "system", "content": system})
    chat_messages.extend(messages)
    if prompt:
        chat_messages.append({"role": "user", "content": prompt})

    if provider == "ollama":
        return StreamingResponse(_stream_ollama(base_url, model, chat_messages), media_type="text/event-stream")
    else:
        api_key = os.environ.get(f"{provider.upper()}_API_KEY", "") if provider in ("openai", "deepseek") else ""
        return StreamingResponse(
            _stream_openai(base_url, model, chat_messages, api_key), media_type="text/event-stream"
        )


@chat_app.post("/llm/chat")
async def llm_chat(request: Request):
    body = await request.json()
    provider = body.get("provider", "ollama")
    model = body.get("model", "llama3.2")
    prompt = body.get("prompt", "")
    system = body.get("system", "")
    base_url = body.get("base_url", "")

    if not base_url:
        base_url = {
            "ollama": "http://localhost:11434",
            "lmstudio": "http://localhost:1234/v1",
            "openai": "https://api.openai.com/v1",
            "deepseek": "https://api.deepseek.com/v1",
        }.get(provider, "http://localhost:11434")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    if prompt:
        messages.append({"role": "user", "content": prompt})

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            if provider == "ollama":
                r = await client.post(
                    base_url.rstrip("/") + "/api/chat", json={"model": model, "messages": messages, "stream": False}
                )
                data = r.json()
                reply = data.get("message", {}).get("content", "")
            else:
                headers = {"Content-Type": "application/json"}
                api_key = os.environ.get(f"{provider.upper()}_API_KEY", "")
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                r = await client.post(
                    base_url.rstrip("/") + "/chat/completions",
                    json={"model": model, "messages": messages, "max_tokens": 1024},
                    headers=headers,
                )
                data = r.json()
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"response": reply}
    except Exception as e:
        return {"error": str(e)}
