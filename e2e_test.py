"""Smoke test: sends the slide-3 question through the same request app.py builds.

Run inside the container:
  docker run --rm -v "$PWD/e2e_test.py:/app/e2e_test.py" --env-file .env \
    crop-advisor python e2e_test.py
"""

import os

import requests

from system_prompt import SYSTEM_PROMPT

QUESTION = (
    "I have 5 acres in Multan, just harvested wheat. Water is short. "
    "What should I sow next?"
)

response = requests.post(
    "https://api.fireworks.ai/inference/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['FIREWORKS_API_KEY']}"},
    json={
        "model": os.environ.get(
            "FIREWORKS_MODEL",
            "accounts/fireworks/models/llama4-maverick-instruct-basic",
        ),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": QUESTION},
        ],
        "max_tokens": 1024,
        "temperature": 0.6,
    },
    timeout=60,
)
response.raise_for_status()
data = response.json()
print("MODEL:", data.get("model"))
print("TOKENS:", data.get("usage"))
print("--- ANSWER ---")
print(data["choices"][0]["message"]["content"])
