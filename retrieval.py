"""BM25 retrieval over the corpus/ documents.

Chunks every corpus/*.md into overlapping ~400-word passages and indexes them
with BM25 (classic keyword relevance ranking). Pure CPU, builds in
milliseconds at this corpus size; no external services.
"""

import re
from pathlib import Path

from rank_bm25 import BM25Okapi

CORPUS_DIR = Path(__file__).parent / "corpus"
CHUNK_WORDS = 400
CHUNK_STRIDE = 320  # 80-word overlap between consecutive chunks

_HEADER_RE = re.compile(r"<!--\n(.*?)\n-->", re.DOTALL)


def _tokenize(text: str) -> list[str]:
    # Latin tokens plus Arabic-script tokens, so Urdu documents and queries
    # index and match directly.
    return re.findall(r"[a-z0-9]+|[؀-ۿ]+", text.lower())


def _parse_header(text: str) -> dict:
    meta = {}
    m = _HEADER_RE.search(text)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
    return meta


def _load_chunks() -> list[dict]:
    chunks = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        if path.name == "SOURCES.md":
            continue
        text = path.read_text()
        meta = _parse_header(text)
        body = _HEADER_RE.sub("", text)
        words = body.split()
        for start in range(0, max(len(words) - CHUNK_WORDS // 2, 1), CHUNK_STRIDE):
            passage = " ".join(words[start : start + CHUNK_WORDS])
            if len(passage.split()) < 40:
                continue
            chunks.append(
                {
                    "text": passage,
                    "title": meta.get("title", path.stem),
                    "year": meta.get("year", "n.d."),
                    "tier": meta.get("tier", "unknown"),
                }
            )
    return chunks


CHUNKS = _load_chunks()
DOC_COUNT = len({c["title"] for c in CHUNKS})
_BM25 = BM25Okapi([_tokenize(c["text"]) for c in CHUNKS]) if CHUNKS else None

# Crop synonyms for query routing: a query naming a crop is answered from that
# crop's documents, not from whichever document happens to share filler words.
CROP_SYNONYMS = {
    "wheat": {"wheat", "gandum"},
    "rice": {"rice", "paddy", "basmati", "chawal"},
    "cotton": {"cotton", "kapas"},
    "maize": {"maize", "corn", "makai"},
    "mungbean": {"mungbean", "mung", "moong"},
    "sugarcane": {"sugarcane", "cane", "ganna"},
}


def _crops_in(tokens: list[str]) -> set[str]:
    tokset = set(tokens)
    return {crop for crop, syns in CROP_SYNONYMS.items() if tokset & syns}


def retrieve(query: str, k: int = 3, min_score: float = 5.0) -> list[dict]:
    """Return up to k passages relevant to the query, best first.

    If the query names a crop, only documents whose title mentions that crop
    compete; otherwise all documents do.
    """
    if _BM25 is None:
        return []
    qtokens = _tokenize(query)
    scores = _BM25.get_scores(qtokens)

    crops = _crops_in(qtokens)
    if crops:
        allowed = [
            i
            for i, c in enumerate(CHUNKS)
            if _crops_in(_tokenize(c["title"])) & crops
        ]
        candidates = allowed if allowed else range(len(CHUNKS))
        if allowed:
            # Routing already guarantees topical relevance; the score floor
            # only needs to reject near-empty matches.
            min_score = min(min_score, 2.0)
    else:
        candidates = range(len(CHUNKS))

    ranked = sorted(candidates, key=lambda i: scores[i], reverse=True)
    results = []
    for i in ranked[:k]:
        if scores[i] < min_score:
            break
        results.append({**CHUNKS[i], "score": round(float(scores[i]), 2)})
    return results


def build_reference_block(passages: list[dict]) -> str:
    """Format retrieved passages for injection into the model prompt."""
    lines = ["Reference passages from Pakistani agricultural sources:"]
    for n, p in enumerate(passages, 1):
        lines.append(f"\n[{n}] {p['title']} ({p['year']}):\n{p['text']}")
    lines.append(
        "\nUse these passages when they are relevant and cite them as "
        "[Source: <title>]. If a passage's year is old, caveat any cost figures. "
        "If the passages do not cover the question, say so briefly and answer "
        "from general knowledge without inventing a citation."
    )
    return "\n".join(lines)
