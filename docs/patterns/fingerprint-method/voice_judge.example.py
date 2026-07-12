"""voice_judge.example.py — reference implementation of the Fingerprint Method's judge gate.

An LLM scores a draft against your voice fingerprint (the grounding block) and holds anything
below the bar. This is an eval harness pointed at voice instead of correctness.

Provider-agnostic: wire `call_llm` to whatever model you use. Nothing here is specific to a
person or a provider — supply your own grounding block and generation function.

    decision = judge_or_hold(generate, grounding_block, bar=8)
    if decision["status"] == "pass":
        ship(decision["draft"])
    else:
        send_for_review(decision["draft"], decision["gaps"])   # below bar after retries
"""
import json
from typing import Callable, Optional


# ── wire this to your provider (Anthropic, OpenAI, local, …) ──────────────────
def call_llm(prompt: str) -> str:
    """Return the model's raw text response. Replace the body with a real API call."""
    raise NotImplementedError("Wire call_llm to your LLM provider.")


# ── the judge ─────────────────────────────────────────────────────────────────
JUDGE_PROMPT = """You are a strict editorial judge. Score the DRAFT against the VOICE PROFILE —
the definition of how this author actually writes and thinks. Be exacting: anything generic,
off-voice, or off-register scores low.

VOICE PROFILE (the bar):
{grounding_block}

DRAFT TO SCORE:
{draft}

Score the draft 0-10 on each axis:
- register_voice: matches the author's voice and register
- thinking_pattern: mirrors how they structure an argument
- worldview: aligns with their values / way of seeing
- rules: obeys their writing rules (structure, concision, formatting)
- vocabulary: free of words this author never uses (higher = cleaner)

Then give ONE overall integer 0-10 — holistic, not an average. A draft must be genuinely in
their voice to score 8+. List specific, actionable gaps to reach 9+.

Output raw JSON only, first character '{{':
{{"score": <int 0-10>, "per_axis": {{...}}, "gaps": ["<fix>"], "verdict": "<one line>"}}
"""


def _parse_json(raw: str) -> dict:
    """Tolerant JSON parse — strips markdown fences some models add."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    return json.loads(raw)


def score_draft(draft: str, grounding_block: str) -> dict:
    """Score one draft against the fingerprint. Fail-safe: an unparseable judge response
    returns score 0, so a draft is never shipped unscored."""
    raw = call_llm(JUDGE_PROMPT.format(grounding_block=grounding_block, draft=draft))
    try:
        data = _parse_json(raw)
        return {"score": int(data["score"]), "per_axis": data.get("per_axis", {}),
                "gaps": data.get("gaps", []), "verdict": data.get("verdict", "")}
    except (ValueError, KeyError, json.JSONDecodeError):
        return {"score": 0, "per_axis": {}, "gaps": ["judge response could not be parsed"],
                "verdict": "judge-error"}


def judge_or_hold(
    generate: Callable[[Optional[str]], str],
    grounding_block: str,
    *,
    bar: int = 8,
    max_attempts: int = 3,
) -> dict:
    """Generate, score, and retry with feedback up to `max_attempts`. A draft scoring >= bar
    passes immediately; otherwise the highest-scoring draft is HELD (not discarded) for review.

    generate(feedback) -> draft : your generation function. `feedback` is None on the first
    attempt, then the previous attempt's gaps on each retry."""
    attempts, best, feedback = [], None, None
    for i in range(1, max_attempts + 1):
        draft = generate(feedback)
        result = score_draft(draft, grounding_block)
        attempts.append({"attempt": i, "score": result["score"], "gaps": result["gaps"]})
        if best is None or result["score"] > best["score"]:
            best = {"draft": draft, "score": result["score"], "gaps": result["gaps"]}
        if result["score"] >= bar:
            return {"status": "pass", "draft": draft, "score": result["score"],
                    "gaps": [], "attempts": attempts}
        feedback = "; ".join(result["gaps"])
    return {"status": "hold", "draft": best["draft"], "score": best["score"],
            "gaps": best["gaps"], "attempts": attempts}


if __name__ == "__main__":
    # Minimal illustration (wire call_llm first).
    fingerprint = open("VOICE_PROFILE.template.md").read()

    def generate(feedback):
        prompt = "Write a 120-word note announcing a project milestone."
        if feedback:
            prompt = f"Revise to fix: {feedback}\n\n{prompt}"
        return call_llm(prompt)

    decision = judge_or_hold(generate, fingerprint, bar=8)
    print(decision["status"], decision["score"])
