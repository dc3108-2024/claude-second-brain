# Self-Governing AI Operations Monitor

An observable, auditable, self-correcting observability layer for Claude Code skill pipelines. Every Claude call is logged, classified by root cause, and surfaced — with a human approval gate before any change ships.

---

## What problem does this solve?

Skills that call Claude internally can silently fail. Without instrumentation:

- Failures are invisible until something downstream breaks
- You don't know *which* prompts are failing or *why*
- Wasted tokens on retries go uncounted
- LLM calls used where a deterministic rule would suffice go undetected
- Response variables discarded silently mean the call never needed to happen

This system makes every Claude call observable, classified by root cause, and actionable — with a self-improving loop that runs every Sunday.

---

## The self-governing loop

```
┌─────────────────────────────────────────────────────────────────┐
│  1. INSTRUMENT                                                  │
│     call_claude_with_critique() → token_usage.jsonl             │
│     Logs: skill · step · response_hash · critique severity      │
│     SHA-256[:12] hash per response enables variance tracking    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. ANALYSE  (Sunday 21:00 — weekly cron via weekly_run.sh)     │
│     critique_analysis.py classifies into 4 failure types:      │
│                                                                 │
│     hard_failure     hard_rate > 0% — sporadic failures         │
│     wasted_json      retries exhausted, model returned text     │
│     wasted_critique  retries exhausted, critique rejected valid │
│     low_variance     uniqueness_ratio < 30% over ≥ 5 calls      │
│                                                                 │
│     unnecessary_scan.py finds unused response variables         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. QUEUE                                                       │
│     pending_fixes/ — one JSON per issue with issue_type field   │
│     Session start surfaces count → "fix prompt issues"          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. HITL REVIEW  ("fix prompt issues")                          │
│     hard_failure    → fix prompt or critique                    │
│     wasted_json     → add fallback rule to prompt               │
│     wasted_critique → recalibrate critique thresholds           │
│     No change ships without human: yes / skip / stop            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. ENFORCE  (pre-commit hook — 5 gates)                        │
│     Gate 1: no direct subprocess claude calls                   │
│     Gate 2: parse_json_response() not json.loads()              │
│     Gate 3: critique field checks — is None, not truthiness     │
│     Gate 4: all steps registered in step_map.json               │
│     Gate 5: response variable must be used after assignment     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. RESET                                                       │
│     Measurement baseline resets — new signal detected cleanly   │
│     Accumulated fixes persist — no capability rollback          │
│     Loop repeats next Sunday 21:00                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Failure taxonomy

| Dashboard badge | `issue_type` | Root cause | Right fix |
|---|---|---|---|
| Hard failure | `hard_failure` | Sporadic prompt/critique quality issue | Fix prompt or critique |
| JSON failure | `wasted_json` | All retries exhausted, model returned plain text | Add JSON fallback rule to prompt |
| Critique strict | `wasted_critique` | All retries exhausted, valid output rejected | Recalibrate critique thresholds |
| Low variance | `low_variance` | Uniqueness ratio < 30% — rule would suffice | Replace with deterministic logic |
| Unused response | static scan | Response variable assigned but never consumed | Remove call or wire downstream |

---

## HTML dashboard

```bash
# On-demand report (last 7 days)
python3 ~/.claude/monitor/monitor_report.py

# Live server — regenerates on every request
python3 ~/.claude/monitor/monitor_server.py

# Specific windows
python3 ~/.claude/monitor/monitor_report.py --days 30
python3 ~/.claude/monitor/monitor_report.py --hours 6
python3 ~/.claude/monitor/monitor_report.py --all
```

Dashboard sections:
- **Summary cards** — total calls · tokens · hard failures · soft flags · retries · low-variance steps · wasted (exhausted)
- **Top issues** — steps ranked by hard_rate, with trend vs last week
- **⚡ Unnecessary / wasted calls** — sub-typed: JSON failure · Critique strict · Low variance · Unused response
- **Full breakdown** — all skill/step pairs with cohort chips

---

## HITL fix workflow

```bash
# Trigger from Claude Code
fix prompt issues
```

Reads `pending_fixes/`, traces each issue to source via `step_map.json`, presents a diff for approval. Runs tests and commits only if passing. Marks resolved in queue.

---

## Pre-commit enforcement (5 gates)

```bash
cd ~/.claude/skills/financial-os/scripts
python3 -m pytest tests/test_no_rogue_claude_calls.py
# Must show: 5 passed
```

| Gate | What it catches | Suppression |
|------|----------------|-------------|
| 1 | Direct `subprocess.run(["claude"...])` | exempt list |
| 2 | `json.loads(raw)` on Claude output | — |
| 3 | Bare `if not data.get(field)` in critique | `# noqa: critique-safe` |
| 4 | Step not in `step_map.json` | `# noqa: step-map-exempt` |
| 5 | Response variable never used after assignment | `# noqa: scan-exempt` |

---

## Static scan

```bash
python3 ~/.claude/monitor/unnecessary_scan.py
python3 ~/.claude/monitor/unnecessary_scan.py --skills-dir ~/.claude/skills/my-skill
python3 ~/.claude/monitor/unnecessary_scan.py --log-days 30
```

Unused response sites also appear in the HTML dashboard's unnecessary calls table.

---

## Weekly cron

`~/Library/LaunchAgents/com.yourname.prompt-health-weekly.plist` — Sunday 21:00 local time.

Runs `~/.claude/monitor/weekly_run.sh` which executes:
1. `critique_analysis.py` → `prompt_health.md` + `pending_fixes/`
2. `unnecessary_scan.py` → `logs/unnecessary_scan.log`

---

## File reference

```
~/.claude/monitor/
├── monitor.py                  # Core logger — log_call(), read_log()
│                               # JSONL schema: ts · skill · step · prompt_chars
│                               # response_chars · response_hash · critique
│                               # critique_reason · latency_ms · retries · estimated
├── monitor_report.py           # HTML report + live flag
├── monitor_server.py           # Live HTTP server (localhost:8787)
├── critique_analysis.py        # Weekly analysis — classifies all 4 failure types
├── critique_analysis_daily.py  # Daily fast check
├── unnecessary_scan.py         # Static analysis — unused response variables
├── weekly_run.sh               # Cron wrapper: critique_analysis + unnecessary_scan
├── skill_monitor_hook.py       # PostToolUse hook — full_run entries
├── skill_estimates.json        # Per-skill token estimates
└── logs/
    ├── token_usage.jsonl       # Append-only JSONL log (runtime)
    ├── weekly-analysis.log
    ├── unnecessary_scan.log
    └── health_history/
        └── YYYY-MM-DD.md       # Archived weekly reports

~/.claude/monitor/pending_fixes/
└── YYYY-MM-DD-<type>-<skill>-<step>.json
    # issue_type: hard_failure | wasted_json | wasted_critique
    # status: pending → resolved

~/.claude/skills/prompt-health-refactor/references/
└── step_map.json  # Maps skill/step → source file + symbols + fix_type
```

---

## Adding monitoring to a new skill

**Python skills with Claude calls:**

```python
from intelligence.utils import call_claude_with_critique, parse_json_response, CritiqueResult

def _critique_output(raw: str) -> CritiqueResult:
    try:
        data = parse_json_response(raw)          # never json.loads()
    except (json.JSONDecodeError, ValueError):
        return CritiqueResult("hard", "invalid JSON")
    if data.get("closing") is None:              # is None for numeric/list fields
        return CritiqueResult("hard", "missing field: closing")
    if not data.get("platform"):                 # noqa: critique-safe — string field
        return CritiqueResult("soft", "platform missing")
    return CritiqueResult("pass", "")

raw, critique = call_claude_with_critique(
    prompt, _critique_output, skill="my-skill", step="my.step"
)
result = parse_json_response(raw)    # Gate 5: raw must be used downstream
```

Register in `step_map.json`, then verify:

```bash
python3 ~/.claude/monitor/unnecessary_scan.py --skills-dir ~/.claude/skills/my-skill
cd ~/.claude/skills/financial-os/scripts && python3 -m pytest tests/test_no_rogue_claude_calls.py
```

**SKILL.md-only skills — add MONITOR_BLOCK:**

```bash
python3 ~/.claude/monitor/monitor.py --log '{"skill":"my-skill","est_input_tokens":3000,"est_output_tokens":600,"success":true}'
```

---

## Enterprise framing

This system directly addresses:
- **EU AI Act Articles 13 + 14** — every call logged, every change human-approved, before/after metrics on demand
- **DORA operational resilience** — failures classified and resolved with documented evidence
- **Audit trail** — the monitor dashboard *is* the governance artefact; no separate report needed

*Built and running on personal infrastructure. Available as an enterprise pattern.*
