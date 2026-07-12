"""Evaluation harness: sends fixed questions through the app's exact code path
(same retrieval, same system prompt, same model) and checks each answer for
key facts sourced from the corpus documents.

Usage:  python eval/run_eval.py        (needs FIREWORKS_API_KEY etc. in env)
Writes: eval/results.json (full answers, for audit)
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import ask_llm, ground, needs_safety_disclaimer, SAFETY_DISCLAIMER  # noqa: E402

QUESTIONS = Path(__file__).parent / "questions.jsonl"
RESULTS = Path(__file__).parent / "results.json"


def grade(answer: str, must_contain: list[list[str]]) -> tuple[bool, list[str]]:
    """Pass iff every fact group has at least one alternate in the answer."""
    # Normalize typographic quotes/apostrophes some models emit (e.g. U+2019 '
    # vs ASCII ') so keyword matching isn't broken by punctuation style alone.
    low = answer.lower().replace("’", "'").replace("‘", "'")
    missing = []
    for group in must_contain:
        if not any(alt.lower() in low for alt in group):
            missing.append(" | ".join(group))
    return (not missing), missing


def main() -> None:
    items = [json.loads(line) for line in QUESTIONS.read_text().splitlines() if line.strip()]
    results, passed = [], 0
    for item in items:
        grounded, passages = ground(item["question"])
        try:
            answer = ask_llm(
                [{"role": "user", "content": grounded}], temperature=0.2, max_tokens=1500
            )
        except Exception as exc:
            answer = f"ERROR: {exc}"
        if needs_safety_disclaimer(item["question"]) and SAFETY_DISCLAIMER not in answer:
            answer += SAFETY_DISCLAIMER
        ok, missing = grade(answer, item["must_contain"])
        passed += ok
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {item['id']}" + (f"  (missing: {missing})" if missing else ""))
        results.append(
            {
                "id": item["id"],
                "question": item["question"],
                "passed": ok,
                "missing": missing,
                "sources": [p["title"] for p in passages],
                "answer": answer,
            }
        )
        time.sleep(2.5)  # stay inside free-tier rate limits
    print(f"\nSCORE: {passed}/{len(items)}")
    RESULTS.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"Full answers written to {RESULTS}")


if __name__ == "__main__":
    main()
