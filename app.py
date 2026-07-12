import streamlit as st

from core import ask_llm_stream, ground, needs_safety_disclaimer, SAFETY_DISCLAIMER
from retrieval import DOC_COUNT

EXAMPLE_QUESTIONS = [
    "I have 5 acres in Multan, just harvested wheat. Water is short. What should I sow next?",
    "What is the sowing window for cotton in southern Punjab?",
    "Roughly how much does one acre of wheat cost to grow, seed to harvest?",
    "میرے پاس فیصل آباد میں تین ایکڑ زمین ہے، ربیع میں کیا کاشت کروں؟ (Urdu question — answered in English)",
]

st.set_page_config(page_title="Crop Advisor Lite", page_icon="🌾")

with st.sidebar:
    st.title("🌾 Crop Advisor Lite")
    st.markdown(
        "AI crop advisory for Pakistani smallholder farmers - crop selection, "
        "sowing windows, and input costs. Understands English or Urdu questions; "
        "always answers in English."
    )
    st.markdown(
        "**Stack:** gpt-oss-120b (open-weight) · Fireworks AI API (AMD-hosted inference) · Streamlit"
    )
    st.markdown(
        f"**Grounding:** answers cite passages retrieved (BM25) from "
        f"{DOC_COUNT} Pakistani agricultural documents — see `corpus/SOURCES.md`."
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


st.title("Crop Advisor Lite")
st.markdown("Ask about crops, sowing windows, or costs - in **English, or Urdu** (answers are always in English).")

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
    grounded_content, passages = ground(prompt)
    api_messages = list(st.session_state.messages)
    api_messages[-1] = {"role": "user", "content": grounded_content}
    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(ask_llm_stream(api_messages))
        except Exception as exc:
            answer = f"⚠️ Could not reach the model: {exc}"
            st.markdown(answer)
        if needs_safety_disclaimer(prompt) and SAFETY_DISCLAIMER not in answer:
            st.warning(
                "Before you spray anything: confirm the exact product and dose with "
                "your local agriculture extension office (Zarai Taraqiati office) or "
                "a qualified agronomist. This app does not recommend specific "
                "pesticides or doses."
            )
            answer += SAFETY_DISCLAIMER
        if passages:
            with st.expander(f"📚 Sources used ({len(passages)} passages)"):
                for p in passages:
                    st.markdown(f"**{p['title']}** ({p['year']}, {p['tier']}) — relevance {p['score']}")
                    st.caption(p["text"][:400] + "…")
    st.session_state.messages.append({"role": "assistant", "content": answer})
