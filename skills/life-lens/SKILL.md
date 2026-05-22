---
name: life-lens
description: >
  Filter any content, decision, or idea through your personal values and goals.
  Use when you want to know what's actually relevant to you in a document, article,
  research brief, or set of options. Cuts through noise by scoring everything against
  your defined life priorities. Triggers on: "filter this through my lens",
  "what's relevant to me", "apply my values filter", "what matters here for me",
  "is this signal or noise", "run this through my filter", or any time you want
  a personal relevance assessment rather than a generic summary.
---

# Life Lens Skill

A personal relevance filter. Reads your defined life priorities and applies them
to any content — so you get signal, not noise.

Most content consumption is undirected. You read something interesting and file
it under "vaguely useful." This skill changes that: everything gets scored against
what you've said actually matters, and only the relevant parts surface.

**Before using:** define your lenses in `references/lenses.md`. The more honest
you are about what you actually care about, the sharper the filter.

---

## Step 1 — Load the lenses

Read `references/lenses.md`. Extract the full list of defined axes — each one
is a named priority with a description of what counts as relevant to it.

If the file is empty or doesn't exist, stop and prompt the user to define their
lenses. Offer the template structure as a starting point.

---

## Step 2 — Read the input

Accept any of:
- A document or article (read in full before scoring)
- A research brief or set of findings
- A list of options or decisions
- A conversation summary or meeting notes

Read everything before applying the filter. Partial reading produces partial results.

---

## Step 3 — Apply the filter

For each defined lens, scan the input and identify:

1. **Direct hits** — content that explicitly addresses this lens
2. **Indirect hits** — content that affects this lens even if it doesn't name it
3. **Misses** — content that's interesting in general but irrelevant to this lens

Score each lens: **High / Medium / Low / None** relevance.

---

## Step 4 — Deliver the synthesis

Output format:

```
## Lens Filter — [Content title or description]

### [Lens 1 name] — [High / Medium / Low / None]
[1–3 sentences on what's relevant and why. If Low or None, one sentence explaining
why this content doesn't connect to this priority.]

### [Lens 2 name] — [High / Medium / Low / None]
[Same format]

[... repeat for all lenses ...]

---

### What to act on
[Bullet list of 2–5 specific, actionable items that scored High or Medium across
any lens. These are the things worth doing something with.]

### What to file
[1 sentence on whether this is worth saving, and where.]

### What to ignore
[What the content is about that doesn't touch any of your lenses — so you can
consciously set it aside rather than feeling like you missed something.]
```

---

## Step 5 — Update the lens (optional)

After applying the filter, ask:
*Did this content reveal a gap, a new priority, or a shift in an existing one?*

If yes, offer to update `references/lenses.md` to reflect the current state.
The lenses should reflect who you are now — not who you were when you first
defined them.

---

## Quality rules

- Every lens gets a score — no skipping because content seems unrelated
- "None" is a valid and useful answer — it's not a failure, it's signal
- The "What to act on" section must be specific enough to do something with today
- Don't pad the output with context the user already has — they gave you the content
- The filter is only as good as the lenses — if output feels off, the lenses need updating
