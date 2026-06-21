# prompt-health-refactor

Human-in-the-loop workflow for fixing failing Claude prompts in your skill library. Reads failure reports from the prompt health monitor, traces them to source code, proposes targeted fixes, and applies them after your approval.

Part of the self-governing AI operations loop — the human-approval gate before any prompt change ships.

---

## How it works

```
  [prompt_health.md]
  (generated weekly by critique_analysis.py)
        │
        ▼
  Read open issues
  (hard_failure / wasted_json / wasted_critique)
        │
        ▼
  Load step_map.json
  (maps skill/step → source file + symbols)
        │
        ▼
  For each issue:
    Read source code
    Diagnose root cause
    Propose fix (diff-style)
          │
          ▼
    HITL: "Apply? (yes / skip / stop)"
          │
          ▼
    Apply fix → run tests → commit
    Verify: check post-fix failure rate
        │
        ▼
  Summary: N applied, N skipped, N reverted
        │
        ▼
  Regenerate prompt_health.md
```

---

## Trigger phrases

- `"fix prompt issues"`
- `"refactor failing prompts"`
- `"apply prompt fixes"`
- Session-start flag: `"Prompt health: N issue(s)"`

---

## Three failure types

| Type | Root cause | Fix approach |
|---|---|---|
| `hard_failure` | Prompt or critique quality issue (sporadic) | Fix prompt schema or critique thresholds |
| `wasted_json` | Model returns plain text instead of JSON | Add JSON fallback rule to prompt |
| `wasted_critique` | Valid output rejected by over-strict critique | Recalibrate critique field checks |

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Full HITL workflow |
| `references/step_map.json` | Registry of skill/step → source file mappings |

---

## Setup

1. **Run the monitor** to generate failure data:
   ```bash
   python3 ~/.claude/monitor/critique_analysis.py
   ```

2. **Register your steps** in `references/step_map.json`:
   ```json
   {
     "my-skill/extract.data": {
       "file": "~/.claude/skills/my-skill/scripts/extract.py",
       "symbols": ["build_prompt", "_critique_response"],
       "fix_type": "prompt_and_critique"
     }
   }
   ```

3. **Say "fix prompt issues"** — the skill handles the rest.

---

## HITL approval

Every proposed fix requires explicit approval before being applied. No fix ships without human review. This is by design — the monitor surfaces patterns, but whether to change a prompt is always a human decision.
