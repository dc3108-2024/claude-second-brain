# Extending the Scaffold

The skills in this repo are starting points, not ceilings. Each one maps to a
richer pattern that emerges once you've used the scaffold for a few weeks and know
where it's slow.

This document describes the natural growth path — from the base scaffold to a
production-grade second brain.

---

## The progression

```
Scaffold        → Working skills, basic memory, config backed up
Intermediate    → Domain-specific skills, scheduled automation, MCP integrations
Advanced        → Composable micro-skills, Python persistence, knowledge graphs
```

You don't need to reach the advanced tier to get value. Most people settle somewhere
in the intermediate tier and that's the right call.

---

## Learning OS

**Scaffold gives you:** One skill covering capture → synthesise → connect → recall.

**What grows naturally:**

The monolithic skill works until your KB grows past ~50 concepts. At that point, the
single-skill approach becomes unwieldy and you'll want to split it:

| Micro-skill | Purpose |
|---|---|
| `kb-synthesiser` | Classify domain, write the structured KB entry, return a result block |
| `lattice-updater` | Assess cross-domain connections, append to `_lattice.md` |
| `kb-quiz` | Weighted flashcard session drawn from the KB; missed cards surface more |
| `concept-review` | Weekly recall pass over what was captured — distinct from a quiz |
| `learning-dump-drain` | Read a running "dump" note (Apple Notes or text file), return numbered items for capture |
| `learning-review` | Weekly retrospective: what moved, what stalled, are you building capability or just logging |

These micro-skills call each other. The `learning-capture` orchestrator accepts raw input,
calls `kb-synthesiser`, then `lattice-updater`, then `learning-os-logger`. Each sub-skill
is also independently invokable.

**Python scripts worth adding:**

- `generate-knowledge-graph.py` — reads `_lattice.md`, builds a D3.js force graph as HTML.
  Run it at the end of every capture session. The graph visualises concept clusters and
  cross-domain connections that aren't obvious from reading flat markdown files.
- Quiz state management — a simple JSON file tracking concept intervals. The `kb-quiz`
  skill reads and writes it; no external DB needed.

---

## Intelligence Pipeline

**Scaffold gives you:** `research-brief` — web search → synthesised briefing on demand.

**What grows naturally:**

A reactive skill (you trigger it) evolves into a proactive pipeline (it runs for you):

| Addition | How it works |
|---|---|
| Domain-specific search skill | Hardcode your trusted sources. Generic web search returns noise; a skill that always checks 8-10 specific sites returns signal. |
| Email digest skill | Gmail MCP + search by label/sender → structured digest of what landed in your inbox |
| Synthesis layer | A skill that takes web findings + email digest and runs them through your personal lens (your goals, your domain) to surface what's actually relevant to *you* |
| Daily brief skill | Orchestrates the three above into a single PDF, auto-saved and auto-opened. Schedule it to run at 7am. |

The key architectural move: **separate the gathering from the synthesis.** One skill
collects raw intelligence, another filters it through your context. Keeping them separate
lets you swap the synthesis layer without rebuilding the search logic.

---

## PM Loop

**Scaffold gives you:** `jira-pm` — an AI-assisted PM lifecycle with three modes:
OPEN (voice/text → PRD → JIRA epic + stories), BUILD (story → in-progress + plan),
and CLOSE (done + PR linked + Confluence updated).

**What grows naturally:**

The `jira-pm` skill gives you the backlog orchestration layer. Extend it with an
automated capture front-end:

| Addition | How it works |
|---|---|
| `audio-interview-bridge` | Drop a voice recording (interview, meeting, brain-dump) and the pipeline auto-transcribes via Whisper, distils requirements via Claude, routes to the right JIRA project, and posts to Slack for your one-word approval before creating the PRD and epic. |
| Smart routing | A Claude classifier reads the distilled content and picks the best JIRA project — not by filename convention but by understanding what the content is about. Confidence + rationale surface in the Slack message so you can verify before approving. |
| HITL gate | The Slack approval step is the only manual moment in the chain. Everything before it is administration. Everything after it is execution. This is the right place for judgment: post-distillation, pre-creation. |
| `idea-backlog` | A centralised backlog outside JIRA for ideas that aren't ready for epics yet. Intake via Slack, chat, or file. Kanban view, autonomous prioritisation, and triage mode. |

**The pipeline end-to-end:**

```
Voice recording (only manual step: drop the file)
      │
      ▼
Whisper transcription → Google Drive
      │
      ▼
Claude: distil to structured "sound bytes"
      │
      ▼
Claude: classify to correct JIRA project (with confidence + rationale)
      │
      ▼
Slack: post for your review → reply "yes" / "edit <text>" / "skip"
      │
      ▼
Confluence PRD created
JIRA epic created (linked to PRD)
JIRA stories created (with acceptance criteria + dependency links)
```

**The HITL design principle:**

Automate the pipeline. Preserve the gate.

The approval step is not a concession to automation anxiety. It is the point where
your judgment — which requirements to build, in which priority, for which outcome —
shapes what gets built. Removing it would automate the wrong thing. Keeping it
means the pipeline removes all the administrative overhead while preserving the
PM's actual decision.

**Setup notes:**
- Requires: Whisper (`pip install openai-whisper` + `brew install ffmpeg`), Slack bot (Socket Mode), Confluence + JIRA MCP (`mcp-atlassian`)
- Config: `skills/audio-interview-bridge/references/routing_config.json` — define your JIRA projects and their descriptions; the router uses these to classify
- The daemon runs as a background process (launchd on Mac, systemd on Linux), polling a watch folder every 30 seconds

---

## Document Production

**Scaffold gives you:** `process-diagram` — text description → draw.io XML.

**What grows naturally:**

Process diagrams are one output type. Most knowledge work produces multiple:

| Skill | Produces |
|---|---|
| `pdf` | Any structured content → formatted PDF via ReportLab |
| `pptx` | Structured content → PowerPoint deck via python-pptx |
| `docx` | Reports, memos, SOWs → Word doc via python-docx |
| `xlsx` | Tabular data → formatted Excel workbook via openpyxl |
| `mindmap` | Any document → visual mind-map PDF |
| `document-8020` | Dense document → 20% of content that delivers 80% of value |

All of these follow the same pattern: Claude writes Python inline (via Bash), runs it,
and produces the file. No pre-existing scripts required. The skill just needs to know
which library to use and what the output path should be.

**Stripping AI patterns before publishing:**

Any content produced by Claude for public use — posts, articles, emails, reports —
benefits from a humanize pass before it leaves your system. The `humanize-ai-writing`
skill applies two passes: first stripping the structural patterns that mark AI output
(em dashes, rule-of-three adjective lists, banned verbs like "leverage"/"spearhead"),
then checking that the voice is specific and concrete rather than promotional and generic.

The banned-list in `skills/humanize-ai-writing/references/banned-list.md` is the
working reference — adapt it to your own voice.

**One rule that prevents most PDF layout bugs:**
Hard-wrap text at 65 characters. Set explicit container sizes. Never let ReportLab
infer dimensions from content — it will always guess wrong.

---

## Financial OS

**Scaffold gives you:** One skill for portfolio tracking and net worth modelling.

**What grows naturally:**

| Addition | When you need it |
|---|---|
| Statement ingestion | When you have 4+ platforms and manual entry is the bottleneck |
| Consolidated workbook | When you want one file with a dashboard, per-platform sheets, and asset class summary — rebuilt from raw statements on demand |
| Portfolio modelling | When you want to run "what if I change income / adjust allocations" calculations against your actual numbers |
| Tax situation skill | When your tax situation involves multiple account types or jurisdictions and needs a dedicated skill |

The foundation is a canonical data folder that all financial skills read from. Agree
on its location once, hard-code it into each skill's `references/config.md`, and
you never re-enter account details.

---

## Automation and Scheduling

**Scaffold gives you:** Hooks that auto-commit and auto-push on every file write.

**What grows naturally:**

| Pattern | How to implement |
|---|---|
| Scheduled daily brief | `CronCreate` in Claude Code — runs at a fixed time, generates your brief, saves it to a known folder |
| Post-session memory save | A `PostToolUse` hook that fires `sync-config.py` after every conversation |
| Skill protection | A `PreToolUse` hook that blocks any `rm` or overwrite targeting your skills directory. Skills can be wiped by a misfired eval — protection costs one hook. |

**The hook that pays for itself immediately:**

```json
{
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "command": "cmd=$(jq -r '.tool_input.command // empty'); [[ \"$cmd\" == *rm*skills* || \"$cmd\" == *skills*rm* ]] && echo 'BLOCKED: skill deletion requires manual confirmation' && exit 1; exit 0"
  }]
}
```

Add this to your `settings.json` under `PreToolUse`. It blocks accidental skill
deletion without blocking anything else.

**Extending hooks to project repos:**

The same auto-commit pattern that keeps your skills in sync works for any private
repo Claude writes to — a knowledge base, a financial tool, a project workspace.
Add one `Write|Edit` hook and one `Bash` hook per repo:

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "{ f=$(jq -r '.tool_input.file_path // empty'); [[ \"$f\" == */YourProject/* ]] && git -C ~/YourProject add -A && git -C ~/YourProject diff --cached --quiet || { git -C ~/YourProject commit --quiet -m \"auto: update\" && git -C ~/YourProject push --quiet; }; } 2>/dev/null || true",
    "async": true
  }]
},
{
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "command": "{ cmd=$(jq -r '.tool_input.command // empty'); if echo \"$cmd\" | grep -q 'YourProject/'; then git -C ~/YourProject add -A && git -C ~/YourProject diff --cached --quiet || { git -C ~/YourProject commit --quiet -m \"auto: update\" && git -C ~/YourProject push --quiet; }; fi; } 2>/dev/null || true",
    "async": true
  }]
}
```

Both hooks are needed: `Write|Edit` catches files changed via the Edit tool;
`Bash` catches files written via shell commands (`cat >>`, `python3`, etc.).
The `diff --cached --quiet` guard prevents empty commits when nothing actually changed.

---

## Feedback Loops

**Scaffold gives you:** Automation that runs when you trigger it.

**What grows naturally:**

Once your skill library is producing consistent output — weekly briefs, KB captures,
session notes — the next move is closing the feedback loops. Instead of output that
you read once and forget, the system starts feeding its own inputs.

Three loops, in order of implementation complexity:

---

### Loop 1 — Briefs → KB

**Problem:** You read a brief, find a useful concept, and don't capture it.

**Pattern:** After a brief skill generates its PDF, it calls a sync sub-skill that
extracts the top 3 structurally significant concepts — named patterns, not news — and
runs each one through the full KB capture pipeline.

```markdown
## Final step in your brief skill

### Step N — Sync to KB
Invoke `second-brain-sync` with BRIEF_TYPE + the full WEB_INTEL + SYNTHESIS blocks verbatim.
```

```markdown
# second-brain-sync/SKILL.md

Extract exactly 3 concepts that satisfy:
1. A named pattern, framework, or principle — not a news item or vendor announcement
2. Structurally generalisable beyond this week's data
3. Not reducible to "X shipped Y feature"

For each concept, run sequentially:
a. kb-synthesiser
b. learning-os-logger
c. lattice-updater
d. life-lens-updater
```

The rule "named pattern, not news" is what separates KB-worthy from noise. A trend
briefing produces dozens of facts; three durable patterns is a good week.

---

### Loop 2 — Session → alignment

**Problem:** You revise a goal mid-conversation but the change never lands in your
personal alignment filter — so the next session still uses stale criteria.

**Pattern:** A `PostSessionStop` hook fires a Python script after every session ends.
The script reads the transcript, looks for explicit signal phrases, and calls
`life-lens-updater` if it finds one.

```json
{
  "matcher": "PostSessionStop",
  "hooks": [{
    "type": "command",
    "command": "/opt/homebrew/bin/python3 ~/your-workspace/scripts/session_lens_sync.py \"$CLAUDE_SESSION_ID\"",
    "async": true
  }]
}
```

Signal phrases worth detecting (adapt to your vocabulary):

```python
SIGNALS = {
    "GOAL_REVISION":       ["from now on", "I've decided", "I'm dropping", "changing my approach"],
    "MILESTONE_COMPLETE":  ["we've finished", "that's done", "marked complete", "shipped"],
    "PRIORITY_SHIFT":      ["deprioritising", "no longer pursuing", "moving this to later"],
    "STRATEGY_ABANDONED":  ["not doing this", "dropping", "cancelling"],
}
```

The script should: find the signal → build a short summary → pass it to
`life-lens-updater` → exit 0 always (never block the session from closing).

This loop only works if your alignment filter is actually used in synthesis skills.
If `life-lens` drives what your briefs emphasise, updating it has immediate effect
on the next brief.

---

### Loop 3 — KB → research bias

**Problem:** Dense areas of your KB get denser (you keep capturing what you already
know) while sparse areas stay sparse (you never notice the gap).

**Pattern:** A weekly script scans your KB, counts entries per subdirectory, and
writes a shared focus-bias file. Any skill that generates content reads this file
at Step 0 and adjusts its synthesis accordingly.

```python
# scripts/kb_frontier.py — run Sunday night via cron

KB_ROOT = Path("~/LearningOS/kb").expanduser()
FRONTIER_PATH = Path("~/.claude/skills/shared/kb-frontier.md").expanduser()

SPARSE_THRESHOLD = 5
DENSE_THRESHOLD = 15

def count_kb_entries(kb_root):
    counts = {}
    for md_file in kb_root.rglob("*.md"):
        parts = md_file.relative_to(kb_root).parts
        if len(parts) >= 2 and not md_file.name.startswith("_"):
            key = "/".join(parts[:-1])
            counts[key] = counts.get(key, 0) + 1
    return counts
```

The output file (`shared/kb-frontier.md`) is read by any skill that benefits
from knowing where the KB is thin:

```markdown
# KB Frontier
Generated: 2026-05-23

## Sparse areas (boost in this week's briefs)
| KB area | Entry count |
|---|---|
| philosophy | 3 |
| personal-finance | 3 |

## Dense areas (already well covered)
| KB area | Entry count |
|---|---|
| frameworks | 19 |
| agentic-ai | 18 |

## This week's focus bias
Prioritise: philosophy, personal-finance
De-emphasise: frameworks, agentic-ai
```

Inject it into any synthesis prompt:

```markdown
## Step 0 — KB Frontier Check

Read `~/.claude/skills/shared/kb-frontier.md`.

If the file exists and `Generated:` is within the last 7 days:
- Extract the "This week's focus bias" section as FOCUS_BIAS

Otherwise:
- Set FOCUS_BIAS = "No frontier data — treat all areas equally"

FOCUS_BIAS is applied in Step 1 when a concept could fit multiple domains.
```

**Where to inject FOCUS_BIAS:**
- Weekly brief synthesis skills — weight sparse areas in concept extraction
- `kb-synthesiser` — when a concept spans multiple domains, prefer the sparse one
- Any capture pipeline that classifies domain before writing

The frontier file is the shared state that connects all three loops. Loop 1 adds
entries to the KB. Loop 3 reads the KB and adjusts what Loop 1 captures next week.

---

### What makes loops work

Three properties that distinguish a loop from a one-off automation:

1. **Shared state** — a file or DB that persists between runs and carries signal forward
2. **Low-friction read** — any skill can read the shared state in one step at the top
3. **Always-exit-0 scripts** — loop scripts must never block the foreground workflow.
   If `session_lens_sync.py` crashes, the session still closes. If `kb_frontier.py`
   fails, the brief still generates. Loops are additive, not load-bearing.

---

## Self-Improving Loop

**Scaffold gives you:** Static skills that work the same way on run 1 and run 100.

**What grows naturally:**

A skill library that monitors itself, surfaces its own failures, and fixes them
through a human-in-the-loop workflow.

| Component | What it does |
|---|---|
| `call_claude_with_critique()` | Every Claude call is wrapped: auto-retry on hard failure, critique function validates output structure, all results logged to `token_usage.jsonl` |
| `critique_analysis.py` | Weekly script: reads the log, finds steps with high hard-failure rates or exhausted retries, writes issues to `prompt_health.md` |
| `prompt-health-refactor` | HITL skill: reads open issues, traces them to source code, proposes targeted fixes, applies them after your approval |
| `self-correction` | When a skill fails at runtime, diagnoses the error type, applies the appropriate fix, re-runs the workflow, and logs the outcome |

**The loop:**

```
Claude call
    │
    ▼
call_claude_with_critique()   ← retries on hard failure
    │
    ▼
token_usage.jsonl             ← every call logged
    │
    ▼
critique_analysis.py          ← weekly: finds failure patterns
    │
    ▼
prompt_health.md              ← surfaced at session start if issues exist
    │
    ▼
prompt-health-refactor        ← HITL: propose → approve → apply → test
    │
    ▼
Lower failure rate            ← system improves itself
```

**What this costs to set up:**

The `call_claude_with_critique()` wrapper is in `lib/claude_utils.py`. Importing
it instead of calling Claude directly is the only change needed in each skill's
Python scripts. Everything else — logging, analysis, health reporting — is handled
by the shared infrastructure.

The payoff: a step that was failing 89% of the time is fixed once and never fails
again. The monitor caught it. The feedback loop surfaced it. The fix was locked in.

**Step map:**

Every instrumented step must be registered in `references/step_map.json` (inside
`prompt-health-refactor`). This is how the refactor skill traces a failure back to
the source code. Add one entry per `call_claude_with_critique()` call:

```json
"your-skill/step-name": {
  "file": "skills/your-skill/scripts/your_script.py",
  "symbols": ["build_prompt", "_critique_fn"],
  "fix_type": "prompt_and_critique"
}
```

---

## MCP Integrations

**Scaffold gives you:** No MCP dependencies — deliberately, so the base setup works
for anyone.

**What unlocks with MCP:**

| MCP | What it enables |
|---|---|
| Apple Notes | Capture to a running "dump" note; drain it in batch; read back structured content |
| Gmail | Email digest skills; search by label/sender; surface what's relevant without opening the client |
| Google Calendar | Meeting prep skills; pull context before a meeting; suggest agenda items from email threads |
| Google Drive | Read and summarise documents without downloading them |

MCP integrations are the highest-leverage extension because they connect Claude to
systems where your information actually lives — not just files on disk.

Add them one at a time. Each one you add expands what your skills can see.

---

## Mac Integrations

**Scaffold gives you:** `apple-calendar` and `apple-reminders` — create Calendar events
and Reminders entries from natural language, synced to iPhone via iCloud.

Both use `osascript` + a small Python script. No API keys, no MCP server, no external
dependencies — just Claude calling a script that talks directly to the app.

**The pattern is reusable for any scriptable Mac app:**

| App | What you can do |
|---|---|
| Calendar | Create, search, and delete events |
| Reminders | Create reminders with due dates and lists |
| Notes | Read and write note content |
| Contacts | Look up contact details |
| Messages | Send iMessages (use carefully) |
| Music | Control playback, query library |

Any app that supports AppleScript can be wired up with the same `osascript` approach.
The skill just needs to know the right AppleScript vocabulary for that app.

**To add a new Mac integration:**

1. Test the AppleScript in Script Editor first — iterate there before putting it in a skill
2. Move the working script to `scripts/your_script.py` using `subprocess.run(["osascript", "-e", script])`
3. Pass parameters as f-string variables — never let user input touch the script string directly (injection risk)
4. Run `osascript -e 'tell application "AppName" to ...'` to discover available properties before writing the skill

**Setup reminder:** your Calendar and Reminders list names will differ from the defaults.
Run the discovery commands in each skill's Setup section before first use.

---

## Skill Architecture

**Scaffold gives you:** Flat single-file skills. One `SKILL.md` per skill.

**What grows naturally:**

```
skill-name/
├── SKILL.md          # Workflow only — steps, triggers, quality rules
├── scripts/          # Python/shell that the workflow calls
└── references/       # Stable data: config, templates, rubrics, filter matrices
```

The discipline of separating workflow from code from data pays off when skills get
complex. A skill that has 200 lines of Python embedded in `SKILL.md` is hard to
debug and impossible to test. Move the code to `scripts/`, call it from the workflow,
and both become maintainable.

**When to split a skill:**

Split when a skill has two distinct phases that are independently useful, or when
it's getting called by other skills for just one of its steps. The `learning-os`
skill in this scaffold is a candidate — by the time you have 100+ concepts, you'll
want to invoke `kb-quiz` standalone without running a full capture cycle first.

---

## What not to build

Not everything deserves a skill. A skill is worth building when:
- You'll run the workflow more than ~10 times
- The workflow has enough steps that you'd forget one without a checklist
- The output quality meaningfully depends on following a specific sequence

A one-off research question, a quick calculation, a single reformatting task — just
ask Claude directly. The overhead of a skill isn't worth it for things you do once.

The skill library grows best when it's shaped by actual repeated friction, not
anticipation of future needs.
