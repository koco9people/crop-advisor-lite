import os

import requests
import streamlit as st

from system_prompt import SYSTEM_PROMPT

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.fireworks.ai/inference/v1")
CHAT_COMPLETIONS_URL = f"{API_BASE_URL.rstrip('/')}/chat/completions"
MODEL = os.environ.get(
    "FIREWORKS_MODEL", "accounts/fireworks/models/llama4-maverick-instruct-basic"
)

EXAMPLE_QUESTIONS = [
    "I have 5 acres in Multan, just harvested wheat. Water is short. What should I sow next?",
    "What is the sowing window for cotton in southern Punjab?",
    "Roughly how much does one acre of wheat cost to grow, seed to harvest?",
    "میرے پاس فیصل آباد میں تین ایکڑ زمین ہے، ربیع میں کیا کاشت کروں؟",
]

st.set_page_config(page_title="Crop Advisor Lite", page_icon="🌾")

with st.sidebar:
    st.title("🌾 Crop Advisor Lite")
    st.markdown(
        "AI crop advisory for Pakistani smallholder farmers - crop selection, "
        "sowing windows, and input costs, in English or Urdu."
    )
    st.markdown(
        "**Stack:** Llama 4 Maverick · Fireworks AI API (AMD-hosted inference) · Streamlit"
    )
    st.caption(
        "Advisory tool only - confirm pesticide dosages and large decisions with your "
        "local agriculture extension office."
    )
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []


def ask_fireworks(messages: list[dict]) -> str:
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
            "max_tokens": 1024,
            "temperature": 0.6,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


st.title("Crop Advisor Lite")
st.markdown("Ask about crops, sowing windows, or costs - in **English or Urdu**.")

if not st.session_state.messages:
    st.markdown("**Try an example:**")
    cols = st.columns(2)
    for i, question in enumerate(EXAMPLE_QUESTIONS):
        if cols[i % 2].button(question, key=f"example_{i}"):
            st.session_state.pending = question
            st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask your farming question...") or st.session_state.pop("pending", None)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                answer = ask_fireworks(st.session_state.messages)
        except Exception as exc:
            answer = f"⚠️ Could not reach the model: {exc}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
