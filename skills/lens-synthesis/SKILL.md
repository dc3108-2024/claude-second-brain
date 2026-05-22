---
name: lens-synthesis
description: >
  Apply the user's personal lenses to any content — web intel, emails, PDFs, research
  notes, or any dropped text. Returns a structured multi-lens synthesis block.
  Lenses are defined in references/lenses.md — update that file to change how synthesis
  works without touching this skill.
  Trigger on: "synthesise through my lens", "apply my lens", "lens filter",
  "synthesise this", "filter this through my lens", or content passed by an orchestrator.
  If invoked with no content, ask: "What content should I synthesise through your lens?"
---

# Lens Synthesis

Apply the user's personal lenses to any content. This skill is a pure workflow — it
does not embed any persona data. All lens definitions live in `references/lenses.md`.

---

## Step 0 — Load lenses

Read `references/lenses.md`. This file defines each lens: its name, the question it
answers, and any relevant anchors or examples.

---

## Step 1 — Apply each lens

For each lens defined in `references/lenses.md`, extract from the content:
- The most relevant signal for that lens
- A specific, actionable insight — not a general observation
- Named actors, data points, or decisions where possible

Skip a lens entirely if it has no genuine signal today. Do not pad.

---

## Step 2 — Return synthesis block

Return exactly this structure — no preamble, no explanation:

```
SYNTHESIS — [YYYY-MM-DD]

[LENS 1 NAME]: [specific insight — named actor, problem, or signal]

[LENS 2 NAME]: [specific insight, or "Nothing signal-worthy today."]

[LENS 3 NAME]: [specific insight — must pass the falsifiability test if argumentative]

[LENS N NAME]: [specific insight, or "No material signal today."]
```

---

## Quality Rules

- Each lens: one specific sentence. No generalities.
- Argumentative lenses: the insight must be falsifiable — if the opposite is obviously
  absurd, it's a theme not an argument.
- If a lens has nothing today: write "Nothing signal-worthy in this window." — do not
  force a connection.
