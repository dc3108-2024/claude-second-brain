---
name: kb-synthesiser
description: >
  Take any raw concept, classify its domain and curriculum track, synthesise into
  a structured 4-field KB entry, write it to the correct KB file, and return KB_RESULT.
  Trigger on: "synthesise this concept", "add to kb", "capture this".
  If invoked standalone with no input, ask: "What concept should I capture?"
---

# KB Synthesiser

Takes raw concept text and produces a written KB entry. Handles Steps 1-4 of the learning-capture pipeline.

## Step 0 — Load configuration and frontier

Read `~/.claude/skills/_shared/learning-config.md`. Extract:
- KB domain → directory map
- Curriculum track list
- User context note (depth expectations for entries)

Read `~/.claude/skills/shared/kb-frontier.md`.

If the file exists and its `Generated:` date is within the last 7 days:
- Extract the "This week's focus bias" section verbatim as `FOCUS_BIAS`

Otherwise (file absent or stale):
- Set `FOCUS_BIAS = "No frontier data — classify by best fit"`

`FOCUS_BIAS` is applied in Step 1 when a concept could fit multiple domains.

## Step 1 — Classify domain

Map the concept to the correct KB subdirectory using the domain map from learning-config.md.

If the concept could plausibly fit multiple domains, prefer the sparse domain listed in `FOCUS_BIAS`. If it clearly belongs to one domain, `FOCUS_BIAS` does not override.

If it spans multiple domains, write to the primary one and note the secondary connection in **Connected to**. Cross-domain connections are especially valuable — flag them explicitly.

## Step 2 — Identify curriculum track

Map to one of the tracks listed in learning-config.md.

**Inline mode:** If unclear, ask: "Which track is this from?"
**Drain mode (invoked by orchestrator in batch):** Use best judgment; default to `reading-list` if ambiguous — do not ask, do not block batch processing.

## Step 3 — Synthesise the 4-field entry

Extract and structure the insight by answering all four:

1. **Core insight** — one precise sentence. What is the non-obvious key idea?
2. **Framework it extends** — what architectural pattern, mental model, or existing concept does this connect to or extend?
3. **Agentic AI depth** — what architecture, tool, or pattern relates on the Microsoft stack or cross-framework? (Semantic Kernel, AutoGen, Azure AI Foundry, Prompt Flow, LangGraph, crewAI, RAGAS, etc.) Write N/A if not applicable.
4. **Client-ready sentence** — one sentence you could say to a CTO or Head of AI at a bank right now. Concrete, not abstract.

## Step 4 — Write the KB entry

Determine the kebab-case filename from the concept name. Check if a matching file already exists in the target directory — if so, append a new entry. If not, create a new file.

Entry format:

```markdown
---
## [Concept Name]
*Source: [track / course / book], [YYYY-MM-DD]*

**Core insight:** [one precise sentence]

**Framework it extends:** [pattern or model name]

**Client-ready sentence:** "[sentence]"

**Agentic AI depth:** [technical depth on Microsoft stack and/or cross-framework — or N/A]

**Connected to:** [other KB entries or concepts — or N/A]
---
```

## Step 5 — Auto-populate "Connected to" via RAG

After the entry is written, run semantic search to find related KB concepts:
```bash
python3 ~/LearningOS/rag.py "<concept_name>" --top-k 5
```
Replace `<concept_name>` with the name of the concept just written.

From the results:
- Exclude the entry just written (exact name match)
- Take the top 3 results with score > 0.40
- If none exceed 0.40, leave "Connected to" as "N/A" — do not force connections

Update the written entry's "Connected to" field with the comma-separated names of the qualifying results. Then re-upsert to keep the index current:
```bash
python3 ~/LearningOS/rag.py --update ~/LearningOS/kb/<domain>/<slug>.md
```
Replace `<domain>` and `<slug>` with the actual file location of the written entry.

## Step 6 — Return KB_RESULT

Return exactly this block — no preamble, no explanation:

```
KB_RESULT:
Concept: [concept name]
Domain: [domain folder name, e.g. agentic-ai]
KB Path: ~/LearningOS/kb/[domain]/[filename].md
Track: [track name]
Core insight: [one sentence]
Client-ready sentence: [one sentence]
```

---

## Monitoring

At the end of every successful run, execute:

```bash
MONITOR_BLOCK
python3 ~/.claude/monitor/monitor.py --log '{"skill":"kb-synthesiser","est_input_tokens":2500,"est_output_tokens":400,"steps_taken":3,"outputs_written":1,"success":true,"model":"claude-sonnet-4-6","model_tier":"balanced","model_verdict":"appropriate"}'
```
