# self-correction

Automatic skill failure recovery. When a skill fails, this skill diagnoses the error, applies a targeted fix, re-executes the full workflow, and logs the outcome.

Runs unattended — invoked by a shell-level retry wrapper, not directly by the user.

---

## How it works

```
  [Skill fails]
        │
        ▼
  Shell wrapper captures last 70 log lines
  Invokes self-correction with context block:
    - FAILED_SKILL
    - SKILL_PATH
    - EXPECTED_OUTPUT_DIR
    - ATTEMPT number
    - LAST 70 LINES FROM LOG
        │
        ▼
  Classify failure type:
    AUTH_ERROR     → UNRECOVERED (cannot self-fix)
    IMPORT_ERROR   → pip install missing package
    SCRIPT_ERROR   → read /tmp/ script, fix the specific bug
    NETWORK_ERROR  → wait 10s, rephrase search queries
    EMPTY_RESULT   → broaden search terms
    FILE_NOT_FOUND → create missing directory
    PERMISSION_ERROR → UNRECOVERED
    PARTIAL_OUTPUT → re-read skill, re-populate INJECT blocks
    UNKNOWN_ERROR  → full re-run
        │
        ▼
  Apply fix
        │
        ▼
  Re-execute full skill workflow
  (from Step 1 of SKILL_PATH)
        │
        ▼
  Log outcome to skill_error_log.md
  (RECOVERED or UNRECOVERED)
```

---

## Integration

This skill is part of a three-tier reliability system:

| Tier | Mechanism | Purpose |
|---|---|---|
| Tier 1 | `set -e` + try/except + import checks | Fail fast, surface clear errors |
| Tier 2 | watchdog.sh + system alerts | Health monitoring, operator notification |
| Tier 3 | self-correction skill (this) | Automatic diagnosis and recovery |

---

## Error log format

Each run appends one row:

```
| DATE | SKILL | STEP | ERROR_TYPE | FIX_APPLIED | STATUS |
```

Status is either `RECOVERED` (skill produced expected output) or `UNRECOVERED` (fix failed or was not possible).

---

## Constraints

- Maximum 2 invocations per skill run (shell wrapper gives up after that)
- Never modifies SKILL.md files — only fixes `/tmp/` scripts or search parameters
- Never reduces output scope unless the data genuinely doesn't exist
- AUTH_ERROR and PERMISSION_ERROR are always UNRECOVERED — cannot work around them
