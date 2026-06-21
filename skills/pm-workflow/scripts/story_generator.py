"""
story_generator.py — Generate user stories from a PRD.

Takes a PRD dict (from prd_drafter.py) and returns 2-4 user stories in
"As a [persona], I want [capability] so that [outcome]" format, each with
2-4 fully self-contained acceptance criteria and build-order dependencies.

Run
---
# Pipe from prd_drafter.py (recommended):
python3 skills/pm-workflow/scripts/prd_drafter.py "your problem here" | \
    python3 skills/pm-workflow/scripts/story_generator.py

# Or supply a PRD JSON file directly:
python3 skills/pm-workflow/scripts/story_generator.py prd.json

# Or paste raw JSON on stdin:
echo '{"feature_name": "...", "personas": [...], "features": [...]}' | \
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


def _build_prompt(prd: dict) -> str:
    return f"""You are a Product Owner writing JIRA user stories from a PRD.

PRD:
Feature:  {prd.get('feature_name', '')}
Personas: {', '.join(prd.get('personas', []))}
Features:
{chr(10).join('- ' + f for f in prd.get('features', []))}

Write 2-4 business user stories. Each story must:
- Follow "As a [persona], I want [capability] so that [outcome]" format exactly
- Have 2-4 acceptance criteria that are fully self-contained — include specific values,
  data formats, edge cases, and constraints so a developer can implement each criterion
  without reading the PRD or any external document
- Include at least one regression guard ("existing behaviour unchanged" where relevant)
- Not mention implementation details (no class names, file paths, framework names)

Also identify build-order dependencies. A story depends on another if it cannot be built
or tested until the other is complete. Use 0-based indices. Only list hard dependencies.

Output raw JSON only. No markdown, no code fences. First character must be [.

Output schema:
[
  {{
    "summary": "As a <persona>, I want <capability> so that <outcome>",
    "persona": "<persona>",
    "capability": "<capability>",
    "outcome": "<outcome>",
    "acceptance_criteria": ["<measurable, self-contained condition>"],
    "depends_on": [<0-based index of story this one is blocked by>]
  }}
]
"""


def _critique(raw: str) -> CritiqueResult:
    try:
        data = parse_json_response(raw)
    except (json.JSONDecodeError, ValueError):
        return CritiqueResult("hard", "invalid JSON")

    if not isinstance(data, list):
        return CritiqueResult("hard", f"expected list, got {type(data).__name__}")

    if len(data) == 0:
        return CritiqueResult("hard", "stories list is empty — at least 1 story required")

    for i, story in enumerate(data):
        if not story.get("summary"):  # noqa: critique-safe — string field
            return CritiqueResult("hard", f"story[{i}] summary missing or empty")
        if story.get("acceptance_criteria") is None:
            return CritiqueResult("hard", f"story[{i}] acceptance_criteria missing")
        if len(story.get("acceptance_criteria", [])) == 0:
            return CritiqueResult("hard", f"story[{i}] acceptance_criteria is empty")
        for dep in story.get("depends_on", []):
            if not isinstance(dep, int) or dep < 0 or dep >= len(data):
                return CritiqueResult("hard", f"story[{i}] depends_on has invalid index {dep!r}")
            if dep == i:
                return CritiqueResult("hard", f"story[{i}] depends_on references itself")

    return CritiqueResult("pass", "")


def generate_stories(prd: dict) -> list[dict]:
    """Call Claude to generate user stories from a PRD dict. Returns list of story dicts."""
    prompt = _build_prompt(prd)
    raw, _cr = call_claude_with_critique(
        prompt, _critique, skill="pm-workflow", step="stories.generate"
    )
    return parse_json_response(raw)


def _print_stories(stories: list[dict]) -> None:
    for i, story in enumerate(stories):
        deps = story.get("depends_on", [])
        dep_label = f"  [depends on story {deps}]" if deps else ""
        print(f"\nStory {i + 1}{dep_label}")
        print(f"  {story.get('summary', '')}")
        print("  Acceptance criteria:")
        for ac in story.get("acceptance_criteria", []):
            print(f"    ✓ {ac}")


if __name__ == "__main__":
    # Accept PRD from: stdin pipe | file path argument | interactive JSON paste
    if not sys.stdin.isatty():
        raw_input = sys.stdin.read().strip()
    elif len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if not p.exists():
            print(f"Error: file not found: {p}", file=sys.stderr)
            sys.exit(1)
        raw_input = p.read_text().strip()
    else:
        print("Paste PRD JSON then press Ctrl+D:")
        raw_input = sys.stdin.read().strip()

    try:
        prd = json.loads(raw_input)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON input — {e}", file=sys.stderr)
        sys.exit(1)

    stories = generate_stories(prd)

    if sys.stdout.isatty():
        print(f"\nGenerated {len(stories)} user stories for: {prd.get('feature_name', '')}")
        _print_stories(stories)
        print("\n--- raw JSON ---")
        print(json.dumps(stories, indent=2))
    else:
        print(json.dumps(stories))
