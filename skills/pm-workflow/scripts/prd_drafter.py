"""
prd_drafter.py — Turn raw requirements into a structured PRD.

Takes a short "sound bytes" description of a problem (1-3 sentences) and
returns a structured JSON PRD with problem statement, personas, features,
success metrics, and explicit out-of-scope items.

Run
---
# Pass as a command-line argument:
python3 skills/pm-workflow/scripts/prd_drafter.py "PMs copy-paste user stories into JIRA manually. Takes 2 hours per sprint."

# Or pipe from stdin:
echo "Users can't see which invoices are overdue without exporting to Excel." | \
    python3 skills/pm-workflow/scripts/prd_drafter.py

# Chain with story_generator.py:
python3 skills/pm-workflow/scripts/prd_drafter.py "your problem here" | \
    python3 skills/pm-workflow/scripts/story_generator.py

Dependencies
------------
pip install  (none — stdlib + claude CLI only)
Claude CLI must be installed and authenticated: https://claude.ai/code
"""

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT))

from lib.claude_utils import CritiqueResult, call_claude_with_critique, parse_json_response

_TEMPLATE_PATH = Path(__file__).parent.parent / "references" / "prd_template.md"


def _build_prompt(sound_bytes: str) -> str:
    template = _TEMPLATE_PATH.read_text()
    return f"""You are a Product Manager writing a Product Requirements Document.

Sound bytes / pain point description:
{sound_bytes}

PRD section definitions (follow these exactly):
{template}

Output raw JSON only. No markdown, no code fences, no prose. Your entire response is the JSON
object — first character {{, last character }}, nothing before or after. If uncertain about any
field value, use a short placeholder string rather than explaining in prose.

Output schema:
{{
  "feature_name": "<concise feature name, e.g. Automated Invoice Overdue Alerts>",
  "problem": "<one paragraph describing the pain, who feels it, current workaround>",
  "personas": ["<Name — role description>"],
  "features": ["<observable capability bullet>"],
  "success_metrics": ["<measurable outcome bullet>"],
  "out_of_scope": ["<explicitly excluded item>"]
}}
"""


def _critique(raw: str) -> CritiqueResult:
    try:
        data = parse_json_response(raw)
    except (json.JSONDecodeError, ValueError):
        return CritiqueResult("hard", "invalid JSON")

    if not isinstance(data, dict):
        return CritiqueResult("hard", f"expected dict, got {type(data).__name__}")

    if not data.get("feature_name"):  # noqa: critique-safe — string field
        return CritiqueResult("hard", "feature_name missing or empty")

    if not data.get("problem"):  # noqa: critique-safe — string field
        return CritiqueResult("hard", "problem missing or empty")

    if data.get("features") is None:
        return CritiqueResult("hard", "features field missing")

    if len(data.get("features", [])) == 0:
        return CritiqueResult("hard", "features list is empty — at least one feature required")

    if data.get("success_metrics") is None:
        return CritiqueResult("hard", "success_metrics field missing")

    return CritiqueResult("pass", "")


def draft_prd(sound_bytes: str) -> dict:
    """Call Claude to draft a PRD from a sound-byte description. Returns parsed dict."""
    prompt = _build_prompt(sound_bytes)
    raw, _cr = call_claude_with_critique(prompt, _critique, skill="pm-workflow", step="prd.draft")
    return parse_json_response(raw)


def _print_prd(prd: dict) -> None:
    print(f"\nFeature:  {prd.get('feature_name', '')}")
    print(f"Problem:  {prd.get('problem', '')}\n")

    print("Personas:")
    for p in prd.get("personas", []):
        print(f"  • {p}")

    print("\nFeatures:")
    for f in prd.get("features", []):
        print(f"  • {f}")

    print("\nSuccess metrics:")
    for m in prd.get("success_metrics", []):
        print(f"  • {m}")

    print("\nOut of scope:")
    for o in prd.get("out_of_scope", []):
        print(f"  • {o}")


if __name__ == "__main__":
    if not sys.stdin.isatty():
        sound_bytes = sys.stdin.read().strip()
    else:
        sound_bytes = " ".join(sys.argv[1:]) or input("Describe the problem (1-3 sentences): ")

    if not sound_bytes:
        print("Error: no input provided.", file=sys.stderr)
        sys.exit(1)

    prd = draft_prd(sound_bytes)

    # If piped to another script, output raw JSON; otherwise pretty-print for humans
    if sys.stdout.isatty():
        _print_prd(prd)
        print("\n--- raw JSON (pipe this to story_generator.py) ---")
        print(json.dumps(prd, indent=2))
    else:
        print(json.dumps(prd))
