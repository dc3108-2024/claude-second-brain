"""
distil.py — Distil a raw interview transcript into structured sound bytes.

Usage (called by audio_bridge.py):
    python3 distil.py <transcript_path>

Output (stdout, JSON):
    {"sound_bytes": [...], "flags": [...], "recording_label": "..."}
"""
import json as _json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/shared"))
from lib_claude import call_claude_with_critique, parse_json_response, CritiqueResult

SKILL_NAME = "audio-bridge"
STEP_NAME  = "distil.extract"

PROMPT_TEMPLATE = """You are a requirements analyst extracting structured sound bytes from a raw interview transcript.

The transcript contains: a PM asking questions, a stakeholder answering, filler words, repetition, side conversations.

Your job:
1. Extract only the stakeholder's requirements, constraints, pain points, and goals.
2. Drop all PM questions, greetings, filler, and repetition.
3. Write each sound byte as a single declarative sentence in the stakeholder's voice.
4. If a requirement is ambiguous or contradictory, include it but prefix with [AMBIGUOUS].
5. If the transcript is empty or too short to extract requirements, return empty arrays.

Recording label: {recording_label}

Raw transcript:
---
{transcript}
---

CRITICAL: Output raw JSON only. No markdown, no code fences, no explanation.
First character must be {{.

{{
  "sound_bytes": ["<requirement 1>", "<requirement 2>", ...],
  "flags": ["[AMBIGUOUS] <item that needs clarification>", ...],
  "recording_label": "<short descriptive label for this recording>"
}}

If extraction fails for any reason (empty transcript, inaudible, non-English), still return valid JSON:
{{
  "sound_bytes": [],
  "flags": ["EXTRACTION_FAILED: <reason>"],
  "recording_label": "{recording_label}"
}}
Never return plain text.
"""


def build_prompt(transcript: str, recording_label: str) -> str:
    return PROMPT_TEMPLATE.format(
        transcript=transcript,
        recording_label=recording_label,
    )


def _critique_distil(raw: str) -> CritiqueResult:
    try:
        data = parse_json_response(raw)
    except (_json.JSONDecodeError, ValueError):
        return CritiqueResult("hard", "invalid JSON")

    if not isinstance(data, dict):
        return CritiqueResult("hard", f"expected dict, got {type(data).__name__}")

    if data.get("sound_bytes") is None:
        return CritiqueResult("hard", "sound_bytes field missing")

    if not isinstance(data["sound_bytes"], list):
        return CritiqueResult("hard", "sound_bytes must be a list")

    if data.get("flags") is None:
        return CritiqueResult("hard", "flags field missing")

    if not isinstance(data["flags"], list):
        return CritiqueResult("hard", "flags must be a list")

    if not data.get("recording_label"):  # noqa: critique-safe — string field
        return CritiqueResult("soft", "recording_label empty — using filename as label")

    return CritiqueResult("pass", "")


def distil(transcript: str, recording_label: str) -> dict:
    """Distil raw transcript into sound bytes. Returns dict with sound_bytes, flags, recording_label."""
    if not transcript.strip():
        return {
            "sound_bytes": [],
            "flags": ["EMPTY_TRANSCRIPT"],
            "recording_label": recording_label,
        }

    prompt = build_prompt(transcript, recording_label)
    raw, critique = call_claude_with_critique(
        prompt, _critique_distil, skill=SKILL_NAME, step=STEP_NAME
    )

    if critique.severity == "hard":
        # Claude call exhausted retries — return raw transcript so reviewer can still act
        return {
            "sound_bytes": [transcript.strip()],
            "flags": [f"DISTILLATION_FAILED: {critique.reason} — raw transcript shown"],
            "recording_label": recording_label,
        }

    return parse_json_response(raw)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(_json.dumps({"error": "Usage: distil.py <transcript_path>"}))
        sys.exit(1)

    transcript_path = Path(sys.argv[1])
    if not transcript_path.exists():
        print(_json.dumps({"error": f"File not found: {transcript_path}"}))
        sys.exit(1)

    recording_label = transcript_path.stem
    transcript_text = transcript_path.read_text(encoding="utf-8", errors="replace")

    result = distil(transcript_text, recording_label)
    print(_json.dumps(result, indent=2))
