"""
router.py — Classify distilled sound bytes to the right JIRA project and Confluence space.

Usage (called by audio_bridge.py):
    python3 router.py  < {"sound_bytes": [...], "recording_label": "..."}

Output (stdout, JSON):
    {"jira_project": "YOUR_PROJECT_2", "confluence_space": "your-space-2",
     "slack_channel": "#your-channel", "confidence": "high", "rationale": "..."}
"""
import json as _json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/shared"))
from lib_claude import call_claude_with_critique, parse_json_response, CritiqueResult

SKILL_NAME = "audio-bridge"
STEP_NAME  = "router.classify"

_CFG_PATH = Path(__file__).parent.parent / "references/routing_config.json"


def _load_routes() -> list:
    return _json.loads(_CFG_PATH.read_text()).get("smart_routes", [])


def build_prompt(sound_bytes: list, recording_label: str, routes: list) -> str:
    sb_text = "\n".join(f"- {s}" for s in sound_bytes) if sound_bytes else "(no sound bytes — use recording label only)"
    routes_text = "\n".join(
        f"- {r['jira_project']}: {r['description']}" for r in routes
    )
    return f"""You are a project router. Based on the requirements below, choose the single best JIRA project to route this recording to.

Recording label: {recording_label}

Distilled requirements:
{sb_text}

Available projects:
{routes_text}

Rules:
- Choose exactly ONE project — the one whose description best matches the subject matter
- If nothing is a clear match, choose the first project as default
- confidence is "high" if the match is obvious, "low" if it's a judgement call

Output raw JSON only. No markdown, no code fences. First character must be {{.

{{
  "jira_project": "<project key>",
  "confluence_space": "<space key>",
  "slack_channel": "<channel>",
  "confidence": "high" or "low",
  "rationale": "<one sentence explaining the choice>"
}}
"""


def _critique_route(raw: str) -> CritiqueResult:
    try:
        data = parse_json_response(raw)
    except (_json.JSONDecodeError, ValueError):
        return CritiqueResult("hard", "invalid JSON")

    if not isinstance(data, dict):
        return CritiqueResult("hard", f"expected dict, got {type(data).__name__}")

    for field in ("jira_project", "confluence_space", "slack_channel", "confidence", "rationale"):
        if not data.get(field):  # noqa: critique-safe — string fields
            return CritiqueResult("hard", f"{field} missing or empty")

    if data["confidence"] not in ("high", "low"):
        return CritiqueResult("hard", "confidence must be 'high' or 'low'")

    return CritiqueResult("pass", "")


def classify_route(sound_bytes: list, recording_label: str) -> dict:
    """Classify sound bytes to the best JIRA project. Returns route dict."""
    routes = _load_routes()
    if not routes:
        raise RuntimeError("No smart_routes defined in routing_config.json")

    prompt = build_prompt(sound_bytes, recording_label, routes)
    raw, critique = call_claude_with_critique(
        prompt, _critique_route, skill=SKILL_NAME, step=STEP_NAME
    )

    if critique.severity == "hard":
        # Fall back to default route
        cfg = _json.loads(_CFG_PATH.read_text())
        default = cfg.get("default_route", {})
        default["confidence"] = "low"
        default["rationale"] = f"Routing failed ({critique.reason}) — using default"
        return default

    return parse_json_response(raw)


if __name__ == "__main__":
    payload = _json.loads(sys.stdin.read())
    result = classify_route(
        payload.get("sound_bytes", []),
        payload.get("recording_label", ""),
    )
    print(_json.dumps(result, indent=2))
