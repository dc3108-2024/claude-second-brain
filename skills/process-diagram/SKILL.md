---
name: process-diagram
description: >
  Turn any process description, document, or system into a clean schematic
  draw.io flow diagram. Use when the user says "diagram this", "sketch the
  flow for", "use draw.io", "make a flowchart", "visualise this workflow",
  "diagram this OS/process/system", or drops a document and wants the
  process visualised. Works on any input: inline description, markdown file,
  PDF, Apple Note, memory file, or verbal explanation.
---

# Process Diagram Skill

Turn any described process into a clean, schematic draw.io diagram — open
and ready to edit in the draw.io desktop app.

Node/edge XML templates and layout constants: `references/drawio-templates.md`

---

## Step 1 — Read the input

Accept any of:
- Inline description in the user's message
- A file path (read with the Read tool)
- An Apple Note title (fetch via MCP)
- A memory file or skill description

Extract the full text of what the process does.

---

## Step 2 — Reason about the process structure

Before writing any XML, answer:

**Stages** — What are the 4–8 discrete phases? Name each in 1–2 words.
Too many stages = cluttered. Collapse adjacent minor steps.

**Node type per stage** — see `references/drawio-templates.md` node type table.

**Context annotation** — For each stage, what is the one concrete mechanism
(tool name, file, skill, cron schedule) that makes it real? Goes as a whisper-weight
sub-label inside the node. If none exists, omit it.

**Connections:**
- Main flow: solid gray arrows, left→right
- Branching paths: both connect, labeled if needed
- Derived links (artifact feeds another stage): dashed gray
- Feedback loop: red dashed arc, routed below the diagram, labeled with what flows back

**Feedback** — Does the process have a loop? What triggers re-entry?

---

## Step 3 — Plan the layout

Use layout constants from `references/drawio-templates.md`:
- Horizontal pipeline, ~1200 × 600 canvas
- Main pipeline y-centre = 230
- Node x positions: `x_i = 40 + i * (1060 / (N-1)) - 65`

---

## Step 4 — Write the draw.io XML

Use the file skeleton and node/edge templates from `references/drawio-templates.md`.
Fill in your nodes and edges. Every node must have an id, geometry, and style from the templates.

---

## Step 5 — Save the file

- Input was a file → save alongside it as `[filename]_flow.drawio`
- Input was inline / Apple Note / memory → save to `~/Desktop/[ProcessName]_flow.drawio`
- User specified a path → use that

Write the XML with the Write tool.

---

## Step 6 — Open in draw.io

```bash
open -a "draw.io" "[output-path]"
```

---

## Visual rules — do not break these

1. **Max 8 main pipeline nodes.** Merge minor steps.
2. **No lane backgrounds.** Column dividers only if helpful.
3. **No emoji in node labels** (except floating annotation badges).
4. **Sub-labels are whisper text** — they annotate, they don't compete with stage names.
5. **No colour fills on nodes** — all nodes are `#f9f9f9`. Shape and line style carry meaning.
6. **One feedback arc maximum** — if multiple loops exist, show the dominant one.
7. **Stage names are verbs or nouns, 1–2 words.** Not sentences.
8. **The pattern must be readable at a glance** before the details are read.

---

## Monitoring

At the end of every successful run, execute:

```bash
python3 ~/.claude/monitor/monitor.py --log '{"skill":"process-diagram","est_input_tokens":3000,"est_output_tokens":800,"steps_taken":6,"outputs_written":1,"success":true,"model":"claude-sonnet-4-6","model_tier":"balanced","model_verdict":"appropriate"}'
```

<!-- MONITOR_BLOCK -->
