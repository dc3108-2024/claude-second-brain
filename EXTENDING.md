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

**One rule that prevents most PDF layout bugs:**
Hard-wrap text at 65 characters. Set explicit container sizes. Never let ReportLab
infer dimensions from content — it will always guess wrong.

---

## Financial OS

**Scaffold gives you:** One skill for portfolio tracking and FIRE modelling.

**What grows naturally:**

| Addition | When you need it |
|---|---|
| Statement ingestion | When you have 4+ platforms and manual entry is the bottleneck |
| Consolidated workbook | When you want one Excel file with a dashboard, per-platform sheets, and asset class summary — rebuilt from raw statements on demand |
| FIRE scenario modelling | When you want to run "what if I move countries / change income / retire in N years" calculations against your actual numbers |
| Tax situation skill | When cross-border moves (residency changes, CGT timing, wealth tax) make the tax picture complex enough to need a dedicated skill |

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
