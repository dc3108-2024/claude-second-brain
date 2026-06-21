# lib/ — Core second brain modules

Reusable Python modules for any skill that calls Claude or reads/writes memory.
Import from here rather than duplicating the patterns in each skill.

---

## claude_utils.py

The LLM harness. Three things it enforces:

**1. Critique loop** — every output is evaluated before use

```python
from lib.claude_utils import call_claude_with_critique, CritiqueResult, parse_json_response

def _critique(raw: str) -> CritiqueResult:
    try:
        data = parse_json_response(raw)
    except Exception as e:
        return CritiqueResult("hard", str(e))
    if not data.get("summary"):
        return CritiqueResult("hard", "missing summary")
    return CritiqueResult("pass", "")

raw, critique = call_claude_with_critique(prompt, _critique, skill="my-skill", step="extract")
```

Severity levels: `pass` → return | `soft` → return + flag | `hard` → retry | `critical` → raise

**2. Safe JSON parsing** — handles markdown fences and preamble text

```python
from lib.claude_utils import parse_json_response

data = parse_json_response(raw)   # works on direct JSON, ```json blocks, and prose-wrapped JSON
```

**3. Automatic model routing** — cost proportional to task complexity

```python
from lib.claude_utils import auto_select_tier, select_model

tier  = auto_select_tier("summarise this document")   # → "fast"
tier  = auto_select_tier("write a LinkedIn post")      # → "creative"
tier  = auto_select_tier("synthesise and recommend")   # → "heavy"
model = select_model(tier)
```

Edit `lib/models.json` to swap models without touching skill code.

---

## memory.py

Read and write the persistent memory system.

```python
from lib.memory import read_memory, list_memories, save_memory

# Read a specific memory by slug
mem = read_memory("user_finance")
print(mem["body"])

# List all memories
for m in list_memories():
    print(m["name"], "—", m["description"])

# Save a new memory
save_memory(
    name="project_sprint_notes",
    body="Sprint 12: auth rewrite. Rationale: ...",
    description="Sprint 12 — auth rewrite notes",
    memory_type="project",
)
```

---

## models.json

Tier-to-model mapping. Edit here to upgrade or swap models without touching any skill code.

```json
{
  "tiers": {
    "fast":     "claude-haiku-4-5-20251001",
    "balanced": "claude-sonnet-4-6",
    "creative": "claude-fable-5",
    "heavy":    "claude-opus-4-8"
  }
}
```

---

## See also

`skills/_template/scripts/example_skill.py` — minimal end-to-end skill using all three modules (good starting point).

`skills/pm-workflow/scripts/` — production example: two composable scripts (`prd_drafter.py`,
`story_generator.py`) that chain together via stdin/stdout. Shows critique functions for structured
JSON output, model-tier selection, and clean piping between Claude calls.
