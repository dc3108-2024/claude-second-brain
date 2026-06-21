---
name: your-skill-name
description: >
  One clear sentence describing what this skill does and when to trigger it.
  Include the trigger phrases here so Claude knows when to invoke it automatically.
  Example triggers: "do X", "help me with Y", "I need Z".
---

# Skill Name

One-line purpose statement. What problem does this solve?

<!-- SCRIPTS NOTE (delete this block if your skill has no code)
If this skill calls Claude programmatically or produces structured output,
put the code in scripts/ and call it from the step below.

Runnable example:
  python3 skills/your-skill-name/scripts/your_script.py "input"

Start from: skills/_template/scripts/example_skill.py
Import from: lib/claude_utils.py (LLM harness) and lib/memory.py (memory CRUD)

Production reference: skills/pm-workflow/scripts/ — two composable scripts
that chain via stdin/stdout (prd_drafter.py | story_generator.py).
-->

---

## Step 1 — [First action]

Describe what Claude should do first. Be specific about inputs, tools, and decisions.

If there are branches (e.g. different input types), use a table:

| Input type | How to handle |
|---|---|
| Inline text | Use directly |
| File path | Read with Read tool |
| URL | Fetch with WebFetch |

---

## Step 2 — [Core processing]

The main work of the skill. Be explicit about:
- What to produce
- What format/structure to use
- What quality bar to meet

---

## Step 3 — [Output / save]

How to deliver the result:
- Where to save files (if any)
- What to show in the conversation
- Whether to auto-open anything

---

## Quality rules

- Rule 1: what must always be true about the output
- Rule 2: what to never do
- Rule 3: when to stop and ask vs. make a judgment call
