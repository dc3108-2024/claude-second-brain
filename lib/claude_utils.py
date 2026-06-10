"""
claude_utils.py — Core LLM harness for Claude Code second brain skills.

Three patterns this module enforces:

1. call_claude_with_critique()
   Every LLM call goes through a critique function. Hard failures retry with
   the failure reason prepended. Soft failures pass through but are flagged.
   Nothing silently produces bad output.

2. parse_json_response()
   Claude frequently wraps JSON in markdown fences or adds preamble text.
   json.loads() fails on all of these. This function handles all three cases:
   direct JSON, fenced JSON, and JSON embedded in surrounding prose.

3. auto_select_tier()
   Rule-based model selection from prompt characteristics. Fast for simple
   extraction tasks, balanced for analysis, creative for writing, heavy for
   multi-step reasoning. Costs stay proportional to task complexity.

Usage
-----
from lib.claude_utils import call_claude_with_critique, parse_json_response, CritiqueResult

def _critique(raw: str) -> CritiqueResult:
    data = parse_json_response(raw)
    if data.get("summary") is None:
        return CritiqueResult("hard", "missing 'summary' field")
    return CritiqueResult("pass", "")

raw, critique = call_claude_with_critique(prompt, _critique, skill="my-skill", step="summarise")
"""

import hashlib
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# Model tiers — edit here to swap models without touching skill code
# ---------------------------------------------------------------------------

_MODELS_FILE = Path(__file__).parent.parent / "lib" / "models.json"

_MODEL_DEFAULTS: dict[str, str] = {
    "fast":     "claude-haiku-4-5-20251001",   # extraction, classification, formatting
    "balanced": "claude-sonnet-4-6",             # analysis, comparison, explanation
    "creative": "claude-fable-5",                # writing, drafting, content generation
    "heavy":    "claude-opus-4-8",               # synthesis, multi-step reasoning, strategy
}


def _load_model_tiers() -> dict[str, str]:
    """Load tier→model mapping from lib/models.json, falling back to defaults."""
    try:
        cfg = json.loads(_MODELS_FILE.read_text()).get("tiers", {})
        return {**_MODEL_DEFAULTS, **cfg}
    except (FileNotFoundError, json.JSONDecodeError):
        return _MODEL_DEFAULTS


MODEL_TIERS: dict[str, str] = _load_model_tiers()

_TIER_RANK: dict[str, int] = {"fast": 1, "balanced": 2, "creative": 2, "heavy": 3}


# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------

_FAST_KEYWORDS = {
    "classify", "summarise", "summarize", "extract", "list", "format",
    "parse", "convert", "translate", "count", "label",
}
_CREATIVE_KEYWORDS = {
    "write", "draft", "compose", "narrate", "craft", "post",
    "article", "blog", "linkedin", "prose", "story",
}
_BALANCED_KEYWORDS = {
    "analyse", "analyze", "compare", "explain", "describe", "review",
}
_HEAVY_KEYWORDS = {
    "synthesise", "synthesize", "reason", "evaluate", "recommend",
    "strategy", "plan", "multi-step", "critique",
}


def auto_select_tier(prompt: str) -> str:
    """
    Infer the best model tier from prompt content alone.

    Rules (first match wins):
      heavy:    prompt > 2000 chars OR heavy-reasoning keywords
      creative: writing/drafting keywords
      balanced: analysis keywords
      fast:     short prompt (<500 chars) OR simple-task keywords
      default:  balanced
    """
    text = prompt.lower()
    n = len(prompt)
    if n > 2000 or any(kw in text for kw in _HEAVY_KEYWORDS):
        return "heavy"
    if any(kw in text for kw in _CREATIVE_KEYWORDS):
        return "creative"
    if any(kw in text for kw in _BALANCED_KEYWORDS):
        return "balanced"
    if n < 500 or any(kw in text for kw in _FAST_KEYWORDS):
        return "fast"
    return "balanced"


def select_model(tier: str) -> str:
    """Return the model ID for a given tier name."""
    return MODEL_TIERS.get(tier, MODEL_TIERS["balanced"])


# ---------------------------------------------------------------------------
# Critique result
# ---------------------------------------------------------------------------

@dataclass
class CritiqueResult:
    """
    Severity levels:
      pass     — output is correct; return immediately
      soft     — output has minor issues; return but log the flag
      hard     — output is unusable; retry with failure reason prepended
      critical — unrecoverable; raise after logging
    """
    severity: str   # "pass" | "soft" | "hard" | "critical"
    reason: str


def _reflect_on_selection(
    model_tier: str,
    critique_severity: str,
    prompt_chars: int,
    response_chars: int,
) -> str:
    """
    Heuristic: was the chosen model tier appropriate for this call?
    Returns "underpowered", "overpowered", or "appropriate".
    """
    rank = _TIER_RANK.get(model_tier, 3)
    if critique_severity == "hard" and rank < 3:
        return "underpowered"
    if (critique_severity in ("pass", "soft")
            and rank > 1
            and prompt_chars < 1200
            and response_chars < 800):
        return "overpowered"
    return "appropriate"


# ---------------------------------------------------------------------------
# Core Claude call
# ---------------------------------------------------------------------------

def call_claude(prompt: str, timeout: int = 120, model: str = "") -> str:
    """
    Call `claude -p` and return stdout. Retries up to MAX_RETRIES on empty
    response or timeout. Raises RuntimeError if all attempts fail.
    """
    cmd = ["claude", "-p", prompt]
    if model:
        cmd += ["--model", model]
    last_error = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
            )
            raw = result.stdout.strip()
            if raw:
                return raw
            last_error = f"empty response (attempt {attempt}). stderr: {result.stderr[:200]}"
        except subprocess.TimeoutExpired:
            last_error = f"timeout (attempt {attempt})"
    raise RuntimeError(f"claude -p failed after {MAX_RETRIES} attempts: {last_error}")


# ---------------------------------------------------------------------------
# Critique loop
# ---------------------------------------------------------------------------

def call_claude_with_critique(
    prompt: str,
    critique_fn: Callable[[str], CritiqueResult],
    skill: str = "",
    step: str = "",
    timeout: int = 120,
    model_tier: str = "auto",
    model: str = "",
) -> tuple[str, CritiqueResult]:
    """
    Call Claude with a severity-tiered critique and automatic retry.

      pass / soft  → return immediately (soft is logged but not retried)
      hard         → retry up to MAX_RETRIES with failure reason prepended
      critical     → RuntimeError after logging

    Parameters
    ----------
    prompt       : the prompt to send to Claude
    critique_fn  : callable(raw_str) → CritiqueResult; you write this per skill
    skill        : skill name for logging (e.g. "research-brief")
    step         : step name for logging (e.g. "extract-insights")
    model_tier   : "auto" (inferred from prompt), "fast", "balanced", "creative", "heavy"
    model        : explicit model ID; overrides model_tier when set

    Returns
    -------
    (raw_output, critique_result) — the last attempt's output and verdict

    Example critique function
    -------------------------
    def _critique(raw: str) -> CritiqueResult:
        try:
            data = parse_json_response(raw)
        except json.JSONDecodeError as e:
            return CritiqueResult("hard", f"JSON parse failed: {e}")
        if data.get("summary") is None:
            return CritiqueResult("hard", "missing required field: summary")
        if not data.get("insights"):          # list — use `is None` for numeric/list fields
            return CritiqueResult("soft", "insights list is empty")
        return CritiqueResult("pass", "")
    """
    resolved_tier  = auto_select_tier(prompt) if model_tier == "auto" else model_tier
    resolved_model = model or MODEL_TIERS.get(resolved_tier, MODEL_TIERS["balanced"])
    current_prompt = prompt
    last_raw       = ""
    last_critique  = CritiqueResult("pass", "")

    for attempt in range(1, MAX_RETRIES + 1):
        t0 = time.monotonic()
        raw = call_claude(current_prompt, timeout=timeout, model=resolved_model)
        latency_ms = int((time.monotonic() - t0) * 1000)

        critique = critique_fn(raw)
        last_raw, last_critique = raw, critique

        if critique.severity == "critical":
            raise RuntimeError(
                f"[{skill}/{step}] critical failure: {critique.reason}"
            )

        if critique.severity in ("pass", "soft"):
            break

        if attempt < MAX_RETRIES:
            current_prompt = f"Previous attempt failed: {critique.reason}.\n\n{prompt}"

    verdict = _reflect_on_selection(
        resolved_tier, last_critique.severity, len(prompt), len(last_raw)
    )
    _log(skill=skill, step=step, latency_ms=latency_ms, attempt=attempt,
         critique=last_critique.severity, verdict=verdict,
         response_hash=hashlib.sha256(last_raw.encode()).hexdigest()[:12])

    return last_raw, last_critique


def _log(**kwargs) -> None:
    """Lightweight local log. Replace with your monitoring integration."""
    parts = " | ".join(f"{k}={v}" for k, v in kwargs.items() if v)
    print(f"[claude_utils] {parts}")


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------

def parse_json_response(raw: str) -> list | dict:
    """
    Extract JSON from Claude output, handling three common formats:

    1. Direct JSON        — model obeyed the instruction perfectly
    2. Fenced JSON        — model wrapped output in ```json ... ```
    3. Embedded JSON      — model added preamble or postamble around JSON

    Using json.loads() directly fails on cases 2 and 3, which Claude produces
    ~30-40% of the time even when explicitly instructed to return only JSON.

    Raises json.JSONDecodeError if no valid JSON is found anywhere in the output.
    """
    import re
    text = raw.strip()

    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Markdown code fence: ```json ... ``` or ``` ... ```
    m = re.search(r'```(?:json)?\s*\n([\s\S]*?)\n```', text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. First valid JSON object or array in the text
    # raw_decode stops at the end of the first syntactically complete structure,
    # so trailing prose with stray } characters cannot corrupt the result.
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch in "{[":
            try:
                obj, _ = decoder.raw_decode(text, i)
                return obj
            except json.JSONDecodeError:
                continue

    raise json.JSONDecodeError("No valid JSON found in Claude response", text, 0)
