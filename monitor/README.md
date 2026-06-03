# Token Usage Monitor

A lightweight self-improving observability layer for Claude Code skill pipelines. Every Claude API call made by a skill is logged, critiqued, and surfaced — so prompt failures get noticed, diagnosed, and fixed before they compound.

---

## What problem does this solve?

Skills that call Claude internally (e.g. parsing a PDF, synthesising a KB entry, generating a financial brief) can silently fail. Claude might return malformed JSON, omit a required field, or produce output that doesn't match the schema the calling code expects. Without instrumentation:

- Failures are invisible until something downstream breaks
- You don't know *which* prompts are failing or *why*
- Wasted tokens on retries go uncounted
- Regressions introduced by prompt edits have no baseline to compare against

This system makes every Claude call observable, categorised, and actionable.

---

## Architecture overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        INSTRUMENTATION                          │
│                                                                 │
│  skill code                                                     │
│    └── call_claude_with_critique(prompt, _critique_fn,          │
│                                  skill="X", step="Y")           │
│          │                                                      │
│          ├── calls Claude CLI                                   │
│          ├── runs critique function on response                 │
│          └── writes to token_usage.jsonl  ◄─── monitor.py      │
│                                                                 │
│  PostToolUse hook (Claude Code)                                 │
│    └── skill_monitor_hook.py                                    │
│          └── writes estimated full_run entry for every skill    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         STORAGE                                 │
│                                                                 │
│  logs/token_usage.jsonl   ← append-only JSONL log              │
│  logs/health_history/     ← weekly snapshot archive            │
│  pending_fixes/           ← actionable issues queue            │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
┌───────────────────────┐     ┌─────────────────────────────────┐
│  ANALYSIS (scheduled) │     │  REPORTING (on demand)          │
│                       │     │                                 │
│  critique_analysis.py │     │  monitor_report.py              │
│  (Sunday 21:00 AEST)  │     │  → /tmp/monitor_report.html     │
│  → prompt_health.md   │     │                                 │
│  → pending_fixes/     │     │  monitor_server.py              │
│                       │     │  → localhost:8787 (live)        │
│  critique_analysis    │     └─────────────────────────────────┘
│  _daily.py            │
│  (daily at session    │
│   start if needed)    │
│  → prompt_health      │
│    _daily.md          │
└───────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REMEDIAL FEEDBACK LOOP                       │
│                                                                 │
│  1. Session start reads prompt_health.md + prompt_health_       │
│     daily.md and surfaces issues as flags                       │
│                                                                 │
│  2. User says "fix prompt issues"                               │
│                                                                 │
│  3. prompt-health-refactor skill reads pending_fixes/,          │
│     traces failures to source code, proposes fixes with         │
│     human approval (HITL), applies, runs tests, commits         │
│                                                                 │
│  4. Next pipeline run generates post-fix monitor entries        │
│     → failure rate measured before and after                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### `monitor.py` — Core logger

The foundation. All other components depend on this.

**Two modes of use:**

**1. Programmatic** — called from `call_claude_with_critique()` inside skill code:
```python
from intelligence.utils import call_claude_with_critique

raw, critique = call_claude_with_critique(
    prompt,
    _critique_fn,          # function that validates the response
    skill="financial-os",  # skill name — shows up in the report
    step="parse.statement" # step name — granular tracking within a skill
)
```
Each call writes one JSONL entry with: timestamp, skill, step, prompt/response size, estimated tokens, latency, retries, critique result (`pass` / `soft` / `hard`), and the failure reason if any.

**2. CLI** — called from a `SKILL.md` MONITOR_BLOCK at the end of a skill run:
```bash
python3 ~/.claude/monitor/monitor.py --log '{"skill":"portfolio-refresh","est_input_tokens":6000,...,"success":true}'
```
This writes an estimated `full_run` entry for skills that don't make individual Claude calls themselves.

**Activation:** monitoring is gated on `CLAUDE_MONITOR_ENABLED=1`. Set this environment variable in `.bashrc` / `.zshrc` or in `launchd` plist entries for scheduled skills.

---

### `skill_monitor_hook.py` — PostToolUse hook

Fires automatically every time a skill is invoked via the `Skill` tool in Claude Code. Writes a fallback `full_run` entry so that skill invocations appear in the monitor even when the skill's own `MONITOR_BLOCK` didn't execute (e.g. conversation was interrupted, sub-skill chaining).

**Deduplication:** if a `full_run` entry for the same skill was already written in the last 90 seconds, the hook skips writing — the authoritative `MONITOR_BLOCK` record takes precedence.

**Token estimates** are looked up from `skill_estimates.json`. If a skill isn't in the file, the default (3,000 input / 600 output tokens) is used.

Registered as a Claude Code `PostToolUse` hook in `settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Skill",
      "hooks": [{"type": "command", "command": "python3 ~/.claude/monitor/skill_monitor_hook.py"}]
    }]
  }
}
```

---

### `skill_estimates.json` — Token estimate registry

Maps skill names to estimated token usage for `full_run` entries. These are intentional approximations — precision is not the goal, coverage is.

```json
{
  "_default": {"est_input_tokens": 3000, "est_output_tokens": 600},
  "financial-os": {"est_input_tokens": 5000, "est_output_tokens": 1000},
  "portfolio-refresh": {"est_input_tokens": 4000, "est_output_tokens": 800}
}
```

Add a new entry whenever a new skill is built.

---

### `critique_analysis.py` — Weekly health analysis

Runs every Sunday at 21:00 AEST via `launchd`. Reads the past 7 days of `token_usage.jsonl`, computes per `skill/step` metrics, and writes `prompt_health.md` to memory.

**What it produces:**
- `memory/prompt_health.md` — the weekly health report (read by session start)
- `pending_fixes/<date>-<skill>-<step>.json` — one file per actionable issue, queued for the HITL refactor workflow
- `logs/health_history/<date>.md` — archive of the previous report before overwriting

**Noise filtering:** entries whose `skill/step` key is marked `fix_type: "none"` in `step_map.json` are excluded from analysis. This prevents known test suite pollution or intentional no-ops from inflating the failure rate.

**Trend tracking:** compares current hard rates against the previous week's snapshot to show `▲` / `▼` movement.

Run manually anytime:
```bash
python3 ~/.claude/monitor/critique_analysis.py
python3 ~/.claude/monitor/critique_analysis.py --days 14
```

---

### `critique_analysis_daily.py` — Daily fast check

A lightweight complement to the weekly analysis. Runs at session start (or on demand) to catch issues in active daily pipelines before they accumulate for a full week.

**Behaviour:**
- Reads the last 24 hours of log entries
- Skips anything below 10% hard failure rate (noise threshold)
- If issues found: writes `memory/prompt_health_daily.md` and exits
- If clean: deletes `prompt_health_daily.md` (no stale alerts) and exits
- Runs once per day — uses a sentinel file (`logs/daily-last-run.txt`) to skip repeat runs

Session start checks `prompt_health_daily.issues > 0` and surfaces the top issue as a flag.

---

### `monitor_report.py` — On-demand HTML report

Generates a self-contained HTML dashboard and opens it in the browser.

```bash
# Basic usage
python3 ~/.claude/monitor/monitor_report.py              # last 7 days (default)
python3 ~/.claude/monitor/monitor_report.py --hours 6   # last 6 hours
python3 ~/.claude/monitor/monitor_report.py --minutes 30
python3 ~/.claude/monitor/monitor_report.py --days 30
python3 ~/.claude/monitor/monitor_report.py --all        # full history

# Live auto-refresh
python3 ~/.claude/monitor/monitor_report.py --live       # refresh every 30s
python3 ~/.claude/monitor/monitor_report.py --live 10    # refresh every 10s

# Combine flags
python3 ~/.claude/monitor/monitor_report.py --hours 1 --live

# Write without opening browser
python3 ~/.claude/monitor/monitor_report.py --no-open
```

Output: `/tmp/monitor_report.html`

**Report sections:**
- **Summary cards** — total calls, estimated tokens, hard failures, soft flags, retries, overall hard rate
- **Top issues** — skill/step pairs with hard rate > 0%, ranked by rate, with token waste estimate
- **Full breakdown** — every skill/step pair: calls, hard%, soft%, retries, tokens, top failure reason, per-date cohort chips

**Colour coding:** 🔴 ≥50% · 🟡 10–49% · 🟢 <10%

---

### `monitor_server.py` — Live streaming server

Starts a local HTTP server that regenerates the report fresh on every browser request. Best for active pipeline runs where you want a live view.

```bash
python3 ~/.claude/monitor/monitor_server.py              # port 8787, last 7 days
python3 ~/.claude/monitor/monitor_server.py --hours 1    # last 1 hour
python3 ~/.claude/monitor/monitor_server.py --port 9000
python3 ~/.claude/monitor/monitor_server.py --refresh 60 # 60s page refresh
```

Opens `http://localhost:8787` in the browser automatically. Unlike `monitor_report.py --live` (which re-reads a static file), the server re-queries the log on every browser request — so it always shows the latest entries, not just a re-read of the same HTML file.

---

## Log format

Every entry in `token_usage.jsonl` is one JSON object per line:

```json
{
  "ts": "2026-06-03T07:29:27Z",
  "skill": "financial-os",
  "step": "parse.statement",
  "prompt_chars": 8400,
  "response_chars": 1200,
  "est_input_tokens": 2100,
  "est_output_tokens": 300,
  "latency_ms": 4320,
  "retries": 1,
  "critique": "pass",
  "critique_reason": "",
  "estimated": false
}
```

| Field | Values | Meaning |
|---|---|---|
| `skill` | string | Skill name — e.g. `financial-os` |
| `step` | string | Step within skill — e.g. `parse.statement` |
| `critique` | `pass` / `soft` / `hard` | **pass** = valid output · **soft** = minor warning, no retry · **hard** = invalid, retried |
| `critique_reason` | string | Why it was flagged — e.g. `"invalid JSON"`, `"missing field: closing"` |
| `retries` | int | Number of additional Claude calls triggered by hard failures |
| `estimated` | bool | `true` = estimated via hook/CLI · `false` = measured from real call |

---

## The remedial feedback loop

This is the closed loop that turns monitoring data into improved prompts:

```
Monitor logs hard failures
        │
        ▼
critique_analysis.py (Sunday) writes pending_fixes/
        │
        ▼
Session start surfaces: "🔧 Prompt health: N issue(s) — say 'fix prompt issues'"
        │
        ▼
User says "fix prompt issues"
        │
        ▼
prompt-health-refactor skill:
  1. Reads pending_fixes/ queue
  2. Looks up skill/step in step_map.json → finds source file + symbols
  3. Diagnoses failure reason (invalid JSON → wrong parser; missing field → schema mismatch)
  4. Shows proposed fix with diff
  5. HITL: "Apply this fix? (yes / skip / stop)"
  6. Applies fix, runs test suite
  7. If tests pass: commits + pushes
  8. Marks pending fix as resolved
        │
        ▼
Next pipeline run generates post-fix entries
        │
        ▼
Failure rate measured: before% → after%
```

**Hard failure types and their fixes:**

| Critique reason | Root cause | Fix |
|---|---|---|
| `"invalid JSON"` | Claude returned markdown-fenced JSON or prose — `json.loads()` can't parse it | Replace `json.loads(raw)` with `parse_json_response(raw)` which strips fences; strengthen prompt with "Output raw JSON only, no markdown" |
| `"missing field: X"` | Prompt schema ambiguous or field name mismatch between prompt and critique | Clarify field name in prompt; check `is None` not `not value` for numeric/list fields in critique |
| `"expected dict, got list"` | Claude returned a JSON array instead of object | Add `if isinstance(data, list): data = data[0]` after parse |
| soft: `"period field missing"` | RTF/approximate balance files don't have a date range | Lower critique threshold to soft-only for this field |

---

## Scheduling

Two scripts run on a schedule via macOS `launchd`:

| Script | Schedule | Purpose |
|---|---|---|
| `critique_analysis.py` | Sunday 21:00 AEST | Weekly health report + pending_fixes queue |
| `critique_analysis_daily.py` | Daily at session start | Fast check for new failures in active pipelines |

The weekly cron also runs the financial-os pipeline, so prompt failures in live data extraction are captured naturally.

---

## File reference

```
~/.claude/monitor/
├── monitor.py                    # Core logger — log_call(), read_log()
├── monitor_report.py             # On-demand HTML report generator
├── monitor_server.py             # Live HTTP server (regenerates on each request)
├── critique_analysis.py          # Weekly analysis → prompt_health.md
├── critique_analysis_daily.py    # Daily fast check → prompt_health_daily.md
├── skill_monitor_hook.py         # PostToolUse hook — fallback full_run entries
├── skill_estimates.json          # Per-skill token estimates for hook entries
├── __init__.py                   # Package marker
└── logs/
    ├── token_usage.jsonl         # Append-only log (runtime — not in git)
    ├── daily-last-run.txt        # Sentinel for daily dedup (runtime)
    ├── weekly-analysis.log       # launchd stdout (runtime)
    ├── weekly-analysis-error.log # launchd stderr (runtime)
    └── health_history/
        └── YYYY-MM-DD.md         # Archived weekly reports

~/.claude/monitor/pending_fixes/
└── YYYY-MM-DD-<skill>-<step>.json  # One file per queued issue; status: pending → resolved

~/.claude/skills/prompt-health-refactor/references/
└── step_map.json                 # Maps skill/step → source file + symbols for HITL fixes
```

---

## Quick reference

```bash
# View live report (last 7 days)
python3 ~/.claude/monitor/monitor_report.py

# View with live auto-refresh (30s)
python3 ~/.claude/monitor/monitor_report.py --live

# Start live server (regenerates on every request)
python3 ~/.claude/monitor/monitor_server.py

# Re-run weekly analysis now
python3 ~/.claude/monitor/critique_analysis.py

# Check today's failures only
python3 ~/.claude/monitor/critique_analysis_daily.py

# Log a skill run manually (from SKILL.md MONITOR_BLOCK)
python3 ~/.claude/monitor/monitor.py --log '{"skill":"my-skill","est_input_tokens":3000,"est_output_tokens":600,"success":true}'
```

---

## Adding monitoring to a new skill

**For skills with internal Claude calls (Python):**
```python
from intelligence.utils import call_claude_with_critique, parse_json_response, CritiqueResult

def _critique_output(raw: str) -> CritiqueResult:
    try:
        data = parse_json_response(raw)   # always use this, never json.loads()
    except (json.JSONDecodeError, ValueError):
        return CritiqueResult("hard", "invalid JSON")
    if data.get("closing") is None:       # is None for numeric fields
        return CritiqueResult("hard", "missing field: closing")
    if not data.get("platform"):          # not/bool for string fields
        return CritiqueResult("soft", "platform field missing")
    return CritiqueResult("pass", "")

raw, critique = call_claude_with_critique(
    prompt,
    _critique_output,
    skill="my-skill",    # must match an entry in step_map.json
    step="my.step",
)
```

Then add the step to `step_map.json`:
```json
"my-skill/my.step": {
  "file": "~/.claude/skills/my-skill/scripts/my_script.py",
  "symbols": ["PROMPT_TEMPLATE", "_critique_output"],
  "fix_type": "prompt_and_critique"
}
```

**For skills without Python Claude calls (SKILL.md only):**

Add a `MONITOR_BLOCK` at the end of the skill:
```bash
python3 ~/.claude/monitor/monitor.py --log '{"skill":"my-skill","est_input_tokens":3000,"est_output_tokens":600,"steps_taken":5,"outputs_written":1,"success":true}'
```

Then add an entry to `skill_estimates.json`:
```json
"my-skill": {"est_input_tokens": 3000, "est_output_tokens": 600}
```
