---
name: learning-capture
description: >
  Converts raw learning into structured Knowledge Base entries.
  AUTO-TRIGGERS without a phrase when the user shares a concept, insight, principle,
  or idea in chat — even casually — across any domain: AI, fintech, banking, insurance,
  philosophy, personal finance, mental models, or general frameworks.
  Also triggers on: "capture this", "I just learned", "add to kb", "save this insight",
  "make this compound", or pasted content from a course, book, or session.
  Also runs daily at a scheduled time to drain the Apple Notes "Learning dump" note.
  When in doubt, capture — never skip a concept because no trigger phrase was used.
---

# Learning Capture — Orchestrator

Detects inline vs drain mode and routes to the correct pipeline. Pass all output verbatim between steps — never summarise or compress.

## Persona
Read `~/.claude/persona.json`. Use these values throughout — never hardcode them:
- `professional.domain` — sector expertise, e.g. ["Banking", "Life Insurance", "FinServ", "Agentic AI"]
- `retirement.target_year` — FIRE target year, e.g. 2036

## Branch Detection

**DRAIN MODE** — invoke when triggered by:
- "drain my learning dump"
- "process learning dump"
- Scheduled daily run (configure time in your crontab/launchd)

**INLINE MODE** — invoke for everything else:
- A concept shared in conversation
- "capture this", "I just learned", "add to kb", "save this insight"
- Auto-trigger: any concept, principle, or insight shared casually in chat

---

## Drain Mode

### Step 1 — Extract items
Invoke the `learning-dump-drain` skill.
Capture its full output verbatim. This is DRAIN_RESULT.

If DRAIN_RESULT reports empty or "not found": stop and report that message.

### Step 2 — Process each item (sequential loop)
For each numbered item in DRAIN_RESULT, in order:

**a.** Invoke `kb-synthesiser` with the item text verbatim.
Capture its full KB_RESULT output verbatim.

**b.** Invoke `learning-os-logger` with KB_RESULT verbatim.

**c.** Invoke `lattice-updater` with KB_RESULT + the word "assess" verbatim.

**d.** Invoke `life-lens-updater` with KB_RESULT verbatim.

**Important:** Process items sequentially — complete all 4 sub-skills for one item before starting the next. Do not fan out in parallel (KB file writes would conflict).

### Step 3 — Clear the note
After all items are processed, clear the Learning dump note body using `mcp__apple-notes__update-note`:
Replace content with: `<!-- Drained [YYYY-MM-DD] — all items captured to KB -->`

### Step 4 — Report batch summary
Report (keep tight):
- N concepts captured
- Any lattice connections added
- Any life-lens updates made

---

## Inline Mode

### Step 1 — Synthesise and write
Invoke `kb-synthesiser` with the raw input verbatim.
Capture its full output as KB_RESULT.

### Step 2 — Log
Invoke `learning-os-logger` with KB_RESULT verbatim.

### Step 3 — Lattice
Invoke `lattice-updater` with KB_RESULT + the word "assess" verbatim.

### Step 4 — Life lens
Invoke `life-lens-updater` with KB_RESULT verbatim.

### Step 5 — Confirm
Report (keep tight):
- Concept name + KB path written
- Client-ready sentence
- Any lattice connection added
- Any life-lens update made

---

## Monitoring

At the end of every successful run, execute:

```bash
MONITOR_BLOCK
python3 ~/.claude/monitor/monitor.py --log '{"skill":"learning-capture","est_input_tokens":3500,"est_output_tokens":500,"steps_taken":4,"outputs_written":1,"success":true,"model":"claude-sonnet-4-6","model_tier":"balanced","model_verdict":"appropriate"}'
```
