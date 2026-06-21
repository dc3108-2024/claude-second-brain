---
name: prompt-health-refactor
description: Human-in-the-loop prompt refactoring workflow. Reads open issues from prompt_health.md, finds the relevant code, proposes targeted fixes, and applies them after user approval. Trigger on "fix prompt issues", "refactor failing prompts", "apply prompt fixes", or when session-start flags prompt_health issues.
---

# Prompt Health Refactor — HITL Workflow

Reads the top hard-failure issues from `prompt_health.md`, traces them to source code, proposes fixes, and applies them one-by-one with human approval at each step.

---

## Step 1 — Read open issues

Check for queued fixes first:
```bash
ls ~/.claude/monitor/pending_fixes/*.json 2>/dev/null | head -5
```

If pending_fixes exist, read them — they're the pre-digested issue list from the last analysis run. Otherwise read `~/.claude/projects/-Users-<username>/memory/prompt_health.md`.

Extract every issue. Two types are queued:

| `issue_type` | Meaning | Fields |
|---|---|---|
| `hard_failure` | Step fails critique at a measurable rate (sporadic) | `hard_rate`, `hard_count`, `top_reason` |
| `wasted_json` | All retries exhausted — model returned plain text / malformed JSON | `wasted_count`, `top_reason` |
| `wasted_critique` | All retries exhausted — output generated but critique rejected it every time | `wasted_count`, `top_reason` |

If no issues of either type: report "System clean — no issues to fix." and stop.

---

## Step 2 — Load step map

Read `~/.claude/skills/prompt-health-refactor/references/step_map.json`.

For each issue, look up `"{skill}/{step}"` in the map to find:
- `file` — path to the Python source
- `symbols` — function/variable names containing the prompt or critique
- `fix_type` — `prompt_and_critique` | `critique` | `prompt`

If a step is not in the map, note it as **unmapped** and skip (log for future addition).

---

## Step 3 — For each mapped issue (loop with HITL)

Repeat for each issue, one at a time:

### 3a — Read the current code

Read the source file. Extract the relevant symbols (PROMPT_TEMPLATE, critique function, etc.).

### 3b — Diagnose

**If `issue_type == "hard_failure"`** — standard prompt/critique quality fix:
- `"invalid JSON"` → prompt needs stronger output instruction; critique needs `parse_json_response` instead of `json.loads`
- `"missing field: X"` → prompt schema is ambiguous or field name mismatch; critique threshold may be too strict
- `"field too short"` → soft flag only — lower threshold or adjust prompt to request longer output
- Other → read critique logic and identify mismatch between what Claude returns vs what critique expects

**If `issue_type == "wasted_json"`** — model consistently returned plain text or malformed JSON:

Root cause: the model has no JSON-safe way to signal failure so it falls back to plain text.

Fix: add a fallback rule to the prompt — "If extraction fails for any reason, still return valid JSON with zero/empty values and explain in the notes field. Never return plain text."

**If `issue_type == "wasted_critique"`** — model output was valid but critique rejected it every time:

Root cause: the critique function's thresholds are miscalibrated.

Diagnosis:
1. Read the critique function in the source file
2. Find the field check that's failing (it will match `top_reason`)
3. Check if the field is genuinely required or if the check is over-strict
4. Propose: lower the threshold, make the check a soft flag, or remove it if optional

### 3c — Propose fix

**For `hard_failure`**, show:
```
ISSUE: {skill}/{step} — {rate}% hard failure — "{reason}"
FILE:  {file}

CURRENT:
[relevant excerpt — prompt template or critique function]

PROPOSED FIX:
[diff-style or full replacement showing the change]

REASON: [one sentence explaining why this fix addresses the failure]
```

**For `wasted_json`**, show:
```
ISSUE: {skill}/{step} — {wasted_count} exhausted call(s) — JSON failure
FILE:  {file}

PROPOSED FIX — add fallback rule to prompt:
[show the new rule to add]

REASON: Model has no JSON-safe failure signal — add one.
```

**For `wasted_critique`**, show:
```
ISSUE: {skill}/{step} — {wasted_count} exhausted call(s) — critique too strict
FILE:  {file}

CURRENT CRITIQUE CHECK:
[show the specific check that triggered top_reason]

PROPOSED FIX — recalibrate:
[lower threshold / change hard to soft / make field optional]

REASON: [one sentence]
```

### 3d — HITL approval

Ask: **"Apply this fix? (yes / skip / stop)"**
- `yes` → proceed to Step 3e
- `skip` → move to next issue
- `stop` → end the workflow, report what was applied

### 3e — Apply fix

Edit the file with the approved change.

### 3f — Run tests

Run the test suite. If tests fail: show the failure, revert the change, mark as **reverted**, move to next issue.

### 3g — Commit

```bash
git -C ~/.claude/skills add -A
git -C ~/.claude/skills commit -m "fix: reduce hard failure rate for {skill}/{step} — {reason}"
git -C ~/.claude/skills push origin main
```

Mark the pending fix as resolved by updating its status field in the queue file.

### 3h — Verify fix effectiveness

Re-run the pipeline that exercises this step, then check the post-fix failure rate in `token_usage.jsonl`. Report: **"Fixed: {before_rate}% → {after_rate}%"**

---

## Step 4 — Summary report

After all issues are processed:

```
PROMPT REFACTOR COMPLETE
  Applied:  N fix(es)
  Skipped:  N
  Reverted: N (test failures)
  Unmapped: N (add to step_map.json)
```

---

## Step 5 — Update prompt_health.md

Run `python3 ~/.claude/monitor/critique_analysis.py` to regenerate `prompt_health.md` with the current baseline.

---

## Notes

- Always run tests before committing — never ship a fix that breaks the suite
- If the same failure reason appears across multiple steps, fix the shared utility (`parse_json_response`) not each step individually
- Add newly discovered step→file mappings to `references/step_map.json` during the workflow
- The HITL approval at Step 3d is non-negotiable — never auto-apply without explicit user confirmation
