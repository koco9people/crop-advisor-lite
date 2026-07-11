"""Shared model-call path used by the Streamlit app and the eval harness."""

import os

import requests

from retrieval import build_reference_block, retrieve
from system_prompt import SYSTEM_PROMPT

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.fireworks.ai/inference/v1")
CHAT_COMPLETIONS_URL = f"{API_BASE_URL.rstrip('/')}/chat/completions"
MODEL = os.environ.get(
    "FIREWORKS_MODEL", "accounts/fireworks/models/llama4-maverick-instruct-basic"
)


def _retrieval_query(question: str) -> str:
    """Non-English questions can't match the English corpus; translate for
    retrieval only (the farmer still gets their answer in their language)."""
    import re

    if len(re.findall(r"[a-z]{3,}", question.lower())) >= 2:
        return question
    try:
        return ask_llm(
            [
                {
                    "role": "user",
                    "content": "Translate this farming question to English. "
                    f"Reply with only the translation:\n{question}",
                }
            ],
            temperature=0.0,
            max_tokens=100,
        )
    except Exception:
        return question


def ground(question: str) -> tuple[str, list[dict]]:
    """Return (augmented user content, retrieved passages) for a question."""
    passages = retrieve(_retrieval_query(question))
    if not passages:
        return question, []
    return f"{question}\n\n---\n{build_reference_block(passages)}", passages


def ask_llm(messages: list[dict], temperature: float = 0.6, max_tokens: int = 1024) -> str:
    """Send a chat request; `messages` excludes the system prompt."""
    api_key = os.environ.get("FIREWORKS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "FIREWORKS_API_KEY is not set. Pass it with "
            "`docker run -e FIREWORKS_API_KEY=...` or export it before running."
        )
    response = requests.post(
        CHAT_COMPLETIONS_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": MODEL,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def ask_llm_stream(messages: list[dict], temperature: float = 0.6, max_tokens: int = 1024):
    """Yield answer fragments as the model generates them (server-sent events)."""
    import json as _json

    api_key = os.environ.get("FIREWORKS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "FIREWORKS_API_KEY is not set. Pass it with "
            "`docker run -e FIREWORKS_API_KEY=...` or export it before running."
        )
    response = requests.post(
        CHAT_COMPLETIONS_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": MODEL,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        },
        timeout=60,
        stream=True,
    )
    response.raise_for_status()
    for line in response.iter_lines():
        if not line or not line.startswith(b"data: "):
            continue
        payload = line[len(b"data: "):]
        if payload.strip() == b"[DONE]":
            break
        delta = _json.loads(payload)["choices"][0].get("delta", {})
        if "content" in delta and delta["content"]:
            yield delta["content"]
