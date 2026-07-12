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

**Answers are grounded, not guessed.** Each question retrieves relevant passages
(BM25 with crop-aware routing) from a 36-document corpus: Pakistani government
policy analyses (wheat, rice, sugarcane), Economic Survey agriculture chapters,
the Agricultural Statistics yearbook, PCRWR research, SUPARCO satellite crop
estimates, Pakistan Business Council sector reports, FAO material, current
cultivation guides, an Urdu-language census document, and US Department of
Agriculture context documents — every source labeled by country and tier in
[corpus/SOURCES.md](corpus/SOURCES.md) so US content is never presented as
Pakistani guidance. Answers cite sources inline as `[Source: title]`. Urdu
questions retrieve both directly (the index tokenizes Arabic script) and via
internal English translation, so they get cited answers too. When the corpus
doesn't cover a question, the app says so instead of inventing a citation.

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

## Evaluation

A 16-question harness ([eval/](eval/)) sends fixed questions through the app's exact
code path — same retrieval, same system prompt, same model at temperature 0.2 — and
checks each answer for key facts sourced from the corpus documents (sowing windows,
seed rates, water-saving figures), plus behavioral probes: refusing to invent market
prices, referring pesticide dosages to extension services, and answering Urdu
questions with citations.

**Current score: 16/16** (re-verified after each corpus expansion: 9 → 28 → 36
documents, 951 chunks). Full answers are written to `eval/results.json` for audit.
Reproduce with:

```bash
python eval/run_eval.py
```

Honest caveats: the question set is small, written by the developer, and keyword-graded —
it protects against regressions and gross hallucination, it is not an independent
agronomic certification.

## Disclaimer

Crop Advisor Lite is an advisory tool, not a certified agronomist. Verify pesticide
dosages, soil decisions, and large investments with your local agriculture extension
office.
