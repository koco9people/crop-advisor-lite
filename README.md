# 🌾 Crop Advisor Lite

AI crop advisory for Pakistani smallholder farmers — crop selection, sowing windows, and
per-acre input costs, in **English or Urdu**.

Built for the **AMD Developer Hackathon: ACT II** (Unicorn Track).

## The problem

Pakistan has over 8 million smallholder farms (1–12 acres). Most farmers have no
affordable access to agronomic advice: which crop to sow after harvest, when the sowing
window closes, what an acre will cost in inputs, or what to plant when canal water is
short. Extension services are stretched thin; advice travels by word of mouth.

## The solution

A lightweight chat advisor that answers those questions in the farmer's own language.
It gives decision-ready answers — named crops, months, and rupee ranges — and is honest
about uncertainty: it refuses to invent market prices and directs high-stakes decisions
(pesticide dosages, large investments) to the local agriculture extension office.

## Stack — built on AMD

| Layer | Technology |
|---|---|
| Model | **Meta Llama 4** (open weights — multilingual, handles Urdu; Maverick on Fireworks by default, Scout on Groq via `API_BASE_URL`) |
| Inference | **Fireworks AI API** — AMD-hosted inference for this hackathon |
| App | Streamlit (Python) |
| Packaging | Docker |

## Quickstart (Docker — recommended)

You need a [Fireworks AI](https://fireworks.ai) API key.

```bash
docker build -t crop-advisor .
docker run -p 8501:8501 -e FIREWORKS_API_KEY=your_key_here crop-advisor
```

Open http://localhost:8501 and ask a question.

> Tested end-to-end against Groq's OpenAI-compatible endpoint (see Configuration);
> Fireworks AI is the shipped default.

## Quickstart (local Python)

```bash
pip install -r requirements.txt
export FIREWORKS_API_KEY=your_key_here
streamlit run app.py
```

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `FIREWORKS_API_KEY` | — (required) | API key for the inference provider |
| `FIREWORKS_MODEL` | `accounts/fireworks/models/llama4-maverick-instruct-basic` | Override the model |
| `API_BASE_URL` | `https://api.fireworks.ai/inference/v1` | Any OpenAI-compatible endpoint |

## Example questions

- "I have 5 acres in Multan, just harvested wheat. Water is short. What should I sow next?"
- "What is the sowing window for cotton in southern Punjab?"
- "میرے پاس فیصل آباد میں تین ایکڑ زمین ہے، ربیع میں کیا کاشت کروں؟"

## Disclaimer

Crop Advisor Lite is an advisory tool, not a certified agronomist. Verify pesticide
dosages, soil decisions, and large investments with your local agriculture extension
office.
