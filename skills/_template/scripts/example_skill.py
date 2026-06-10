"""
example_skill.py — A complete, runnable second brain skill.

This file demonstrates every pattern the lib/ modules provide:
  - call_claude_with_critique()  with a hard/soft/pass critique function
  - parse_json_response()        handling fenced and prose-wrapped JSON
  - auto_select_tier()           automatic model routing by task type
  - save_memory()                persisting a result to the memory system

Task: given any text, extract a structured summary with key insights and
a one-line "so what" — then save the result as a memory entry.

Run
---
# From the repo root:
python3 skills/_template/scripts/example_skill.py "Your text here"

# Or pipe from a file:
cat my_article.txt | python3 skills/_template/scripts/example_skill.py

Dependencies
------------
pip install  (none — stdlib + claude CLI only)
Claude CLI must be installed and authenticated: https://claude.ai/code
"""

import json
import sys
from pathlib import Path

# Allow running from repo root or from this script's directory
_ROOT = Path(__file__).resolve().parents[3]   # repo root
sys.path.insert(0, str(_ROOT))

from lib.claude_utils import (
    CritiqueResult,
    call_claude_with_critique,
    parse_json_response,
)
from lib.memory import save_memory


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = """\
You are a precise knowledge extractor. Analyse the text below and return ONLY
a JSON object — no markdown fences, no preamble, no explanation.

Required fields:
  "title"     : string — a concise title (5-10 words)
  "summary"   : string — 2-3 sentence summary
  "insights"  : list of strings — 3-5 key insights, each one sentence
  "so_what"   : string — one sentence: why does this matter?
  "domain"    : string — primary domain (e.g. "AI", "Finance", "Product")

TEXT:
{text}
"""


# ---------------------------------------------------------------------------
# Critique function
# ---------------------------------------------------------------------------

def _critique(raw: str) -> CritiqueResult:
    """
    Validate the Claude response before accepting it.

    Pattern: parse first, then check required fields.
    Use `is None` for numeric/list fields — `not []` is True and would
    incorrectly flag a valid empty list as a failure.
    """
    try:
        data = parse_json_response(raw)
    except json.JSONDecodeError as e:
        return CritiqueResult("hard", f"JSON parse failed: {e}")

    if not isinstance(data, dict):
        return CritiqueResult("hard", "expected a JSON object, got a list or scalar")

    required = ["title", "summary", "insights", "so_what", "domain"]
    for field in required:
        if field not in data:
            return CritiqueResult("hard", f"missing required field: {field}")

    # String fields — empty string means the model skipped it
    for field in ["title", "summary", "so_what", "domain"]:
        if not data.get(field):
            return CritiqueResult("hard", f"field '{field}' is empty")

    # List field — use `is None`, not `not data.get(...)`
    if data.get("insights") is None:
        return CritiqueResult("hard", "field 'insights' is missing")
    if len(data["insights"]) < 2:
        return CritiqueResult("soft", f"only {len(data['insights'])} insight(s) — expected 3-5")

    return CritiqueResult("pass", "")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(text: str) -> dict:
    """Extract insights from text and save to memory. Returns the parsed result."""
    if not text.strip():
        raise ValueError("Input text is empty")

    prompt = _PROMPT_TEMPLATE.format(text=text.strip())

    # call_claude_with_critique handles:
    #   - model selection (auto — infers "balanced" for analytical tasks)
    #   - retries on hard failures with failure reason prepended
    #   - logging of latency, model, and critique verdict
    raw, critique = call_claude_with_critique(
        prompt,
        _critique,
        skill="example-skill",
        step="extract-insights",
    )

    result = parse_json_response(raw)

    # Save to memory so future sessions can retrieve this insight
    slug = "insight_" + result["title"].lower().replace(" ", "_")[:40]
    path = save_memory(
        name=slug,
        body=(
            f"**Summary:** {result['summary']}\n\n"
            + "\n".join(f"- {i}" for i in result["insights"])
            + f"\n\n**So what:** {result['so_what']}"
        ),
        description=result["title"],
        memory_type="project",
    )

    print(f"\n{'='*60}")
    print(f"Title:   {result['title']}")
    print(f"Domain:  {result['domain']}")
    print(f"Summary: {result['summary']}")
    print(f"\nInsights:")
    for ins in result["insights"]:
        print(f"  • {ins}")
    print(f"\nSo what: {result['so_what']}")
    print(f"\nSaved → {path}")
    if critique.severity == "soft":
        print(f"[soft flag] {critique.reason}")

    return result


if __name__ == "__main__":
    if not sys.stdin.isatty():
        text = sys.stdin.read()
    elif len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print("Usage: python3 example_skill.py 'Your text here'")
        print("       cat article.txt | python3 example_skill.py")
        sys.exit(1)

    run(text)
