---
name: self-correction
description: >
  Invoked automatically by the shell-level retry wrapper when a skill fails.
  Diagnoses the failure, applies the fix, re-executes the full skill workflow,
  and logs the outcome to skill_error_log.md. Not typically invoked directly.
---

# Self-Correction Skill

You receive a failure context block. Your job: diagnose, fix, re-execute, log.

---

## Input context fields

The caller provides these fields:
- `FAILED_SKILL` — name of the skill that failed
- `SKILL_PATH` — path to the SKILL.md file
- `EXPECTED_OUTPUT_DIR` — directory where the output file should appear
- `ATTEMPT` — which retry attempt this is
- `LAST 70 LINES FROM EXECUTION LOG` — the raw log to diagnose from

---

## Step 1 — Classify the failure

Read the log lines and identify the error type:

| Error type | Log pattern | Fix |
|---|---|---|
| `AUTH_ERROR` | "Not logged in", "Please run /login", "401" | Cannot self-correct — log UNRECOVERED, notify, abort |
| `IMPORT_ERROR` | "ModuleNotFoundError", "ImportError", "No module named" | Run `pip3 install [package]` then re-execute |
| `SCRIPT_ERROR` | "Traceback", "SyntaxError", "TypeError", "AttributeError", error in `/tmp/*.py` | Read the /tmp/ script, identify the bug, fix it, re-execute |
| `NETWORK_ERROR` | "ConnectionError", "Timeout", "HTTPError", "rate limit" | Wait 10 seconds, rephrase web search queries, retry step |
| `EMPTY_RESULT` | No findings, empty sections, placeholder text still present | Broaden search terms, retry web search with alternative queries |
| `FILE_NOT_FOUND` | "FileNotFoundError", missing output dir | Create the directory, re-execute |
| `PERMISSION_ERROR` | "Permission denied", "PermissionError" | Log UNRECOVERED — cannot self-correct permissions |
| `PARTIAL_OUTPUT` | PDF created but < 50KB, or still contains "INJECT:" or "PLACEHOLDER" | Re-read the skill, re-populate all INJECT blocks, re-execute |

If the error type is not in the table above: classify as `UNKNOWN_ERROR` and attempt a full re-run of the skill.

---

## Step 2 — Apply the fix

### AUTH_ERROR or PERMISSION_ERROR
- Do not retry
- Log UNRECOVERED
- Stop here

### IMPORT_ERROR
```bash
pip3 install [missing_package_name]
```
Then proceed to Step 3.

### SCRIPT_ERROR
1. Read the failing script from `/tmp/` (or whatever path appears in the traceback)
2. Identify the exact line causing the error
3. Fix the specific issue (do not rewrite the whole script)
4. Write the corrected script back to `/tmp/`
5. Proceed to Step 3

### NETWORK_ERROR
- Wait: `import time; time.sleep(10)`
- If web search failed: rephrase the query, retry once with broader or narrower terms
- If fetch failed: try an alternative source
- Proceed to Step 3

### EMPTY_RESULT
- Broaden search queries (remove restrictive date filters or add OR terms)
- Retry the search step
- If still empty after retry: accept "Nothing signal-worthy" and continue to PDF generation

### PARTIAL_OUTPUT
- Re-read the skill's SKILL.md at `SKILL_PATH`
- Re-populate ALL `# INJECT:` blocks with real content
- Ensure no placeholder text remains
- Re-execute the PDF script

### FILE_NOT_FOUND
```python
import os
os.makedirs("[missing_dir]", exist_ok=True)
```

### UNKNOWN_ERROR
- Re-read the skill at `SKILL_PATH` from scratch
- Re-execute the full skill workflow as if running for the first time

---

## Step 3 — Re-execute the skill

After applying the fix, re-run the COMPLETE skill workflow from Step 1 of the original SKILL.md at `SKILL_PATH`. Do not skip steps.

If the skill produces a PDF: verify the output file exists in `EXPECTED_OUTPUT_DIR` before proceeding to Step 4.

---

## Step 4 — Log the outcome

Append one row to the skill error log (path: `~/.claude/projects/-Users-<username>/memory/skill_error_log.md`):

```
| [DATE] | [FAILED_SKILL] | [step_that_failed] | [ERROR_TYPE] | [fix applied — one sentence] | [RECOVERED or UNRECOVERED] |
```

Example recovered entry:
```
| 2026-05-24 07:45 | my-skill | PDF generation | SCRIPT_ERROR | Fixed TableStyle row count mismatch in /tmp/ script | RECOVERED |
```

Example unrecovered entry:
```
| 2026-05-24 07:45 | my-skill | skill-launch | AUTH_ERROR | Claude not logged in — cannot self-correct | UNRECOVERED |
```

---

## What NOT to do

- Do not ask for confirmation — this runs unattended
- Do not reduce scope (skip sections, produce a shorter PDF) unless truly no data was found
- Do not re-run forever — this skill is invoked at most 2 times before the shell wrapper gives up
- Do not modify the SKILL.md files during self-correction — only fix /tmp/ scripts or search queries
