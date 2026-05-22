---
name: learning-os
description: >
  Personal learning operating system. Captures concepts from any source, synthesises
  them into a structured knowledge base, surfaces connections across domains, and
  runs spaced recall sessions to turn learning into permanent knowledge. Triggers on:
  "capture this", "I just learned", "add to kb", "save this insight", "quiz me",
  "what did I learn this week", "learning review", or any concept shared in conversation.
  Auto-triggers when you share a new idea, principle, or framework — even casually.
---

# Learning OS

A personal learning operating system built on Claude Code. Captures raw learning
from any source, structures it into a searchable knowledge base, maps connections
across domains, and drives recall through spaced repetition.

Configure your KB path and domains in `references/config.md` before first use.

---

## The four-stage loop

```
CAPTURE → SYNTHESISE → CONNECT → RECALL
```

Every concept enters at Capture and compounds through each stage over time.

---

## Stage 1 — CAPTURE

Accept input from any source:

| Source | How to handle |
|---|---|
| Inline (typed in chat) | Use directly |
| Book / article passage | Extract the core insight — not a summary |
| Course or video note | Distil to the principle, not the example |
| Dump note (batch) | Process items sequentially, one at a time |
| Image or screenshot | Read with vision, then extract the concept |

**One concept per capture.** If the input contains multiple ideas, identify the
most important one and note the others for future capture sessions.

---

## Stage 2 — SYNTHESISE

Transform the raw input into a structured KB entry. Every entry has four fields:

```markdown
## [Concept Name]

**Core insight (1–2 sentences):**
The single most important thing to understand. No fluff.

**Mental model / framework:**
How to think about this. A metaphor, a structure, a named pattern.
If it connects to an existing model (first principles, inversion, etc.), name it.

**Application:**
Where does this show up in practice? Give one concrete example in your domain.

**Source:**
[Author / Course / Book — Date]
```

Write the entry to the correct domain file in your KB folder (see `references/config.md`).

---

## Stage 3 — CONNECT

After synthesising, ask: does this concept connect to anything already in the KB?

A genuine connection is one where understanding concept A changes how you understand
concept B — or where the same underlying principle explains both.

If a connection exists:
1. Note it in the concept entry: `**Connected to:** [[Other Concept]]`
2. Append a line to `references/lattice.md`:
   `[Concept A] ↔ [Concept B] — [one sentence on why they connect]`

The lattice grows over time into a map of how your knowledge fits together.
Cross-domain connections (e.g. a biology principle that explains a market dynamic)
are the most valuable — prioritise finding those.

---

## Stage 4 — RECALL

Spaced repetition: surface concepts for active recall at increasing intervals.

**Running a recall session:**

1. Read `references/quiz-state.md` to see which concepts are due
2. For each due concept, show only the **Concept Name** — hide the entry
3. Ask the user to recall the core insight in their own words
4. Reveal the entry and ask: "Did you get it? (y/n)"
5. Update `references/quiz-state.md`:
   - Correct → next review in 2× current interval
   - Incorrect → reset to 1-day interval, mark for priority review

**Default intervals:** 1d → 3d → 7d → 14d → 30d → 60d → 90d

---

## Weekly review

Once a week, run a learning retrospective:

1. List concepts captured this week (from KB files, sorted by date)
2. For each: did it get connected to anything? Applied anywhere?
3. Identify the most important insight of the week — one sentence
4. Flag any concept that feels uncertain — schedule an extra recall
5. Note what you want to learn next and why

Output as a short report. Save to `references/weekly-reviews/YYYY-WW.md`.

---

## KB structure

```
~/[your-kb-folder]/
├── _index.md              # Master list of all concepts — one line each
├── _lattice.md            # Cross-domain connections log
├── domain-one.md          # e.g. technology.md, finance.md, philosophy.md
├── domain-two.md          # One file per domain — concepts append to the bottom
└── ...
```

Domains are yours to define. Start with 3–5 broad ones and split when a file
gets unwieldy (> ~50 concepts).

---

## Extending this scaffold

- **Anki integration:** export quiz-state concepts to Anki-compatible CSV for
  mobile review
- **Knowledge graph:** generate a D3.js or Obsidian graph from `_lattice.md`
  to visualise concept clusters
- **Learning dump:** maintain a running Apple Note or text file where you drop
  raw ideas throughout the day — run a batch capture session each evening
- **Domain tracker:** add a progress log showing how many concepts are in each
  domain and which are overdue for review

---

## Quality rules

- One concept per KB entry — never bundle multiple ideas into one
- Core insight must be in your own words — not a quote from the source
- A connection must change how you understand something — not just share a keyword
- Recall is active (retrieve from memory) not passive (re-read the entry)
- If you can't explain it simply, you haven't synthesised it yet — rewrite it
