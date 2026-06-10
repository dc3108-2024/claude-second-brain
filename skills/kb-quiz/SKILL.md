---
name: kb-quiz
description: Use when the user wants to test recall of concepts from the Knowledge Base. Triggers on: "quiz me", "quiz me [N]", "quiz me on [domain]", "quiz me [N] on [domain]", "flash cards", "test my recall", "test my knowledge". Also runs automatically at session start (once per day). Weighted MCQ flashcard session — missed/guessed cards surface more often; forgotten concepts update kb-frontier.md to bias future briefs.
---

# KB Quiz

Weighted MCQ flashcard quiz drawn from the KB. Every card uses multiple choice. After each answer, a one-keypress reflection (`y/n`) distinguishes genuine recall from lucky guesses — forgotten concepts increase draw weight AND update `shared/kb-frontier.md` so future briefs focus on gaps.

## Step 0 — Session-start check

**If invoked automatically at session start (not by user typing a quiz trigger):**

1. Read `~/.claude/skills/shared/quiz-last-run.txt`
2. If the file contains today's date (`YYYY-MM-DD`), **skip the quiz entirely** — it has already run today. Do not mention the skip; proceed to the user's message.
3. If the file is absent or contains a past date: run with N=4, domain=all. Write today's date to `~/.claude/skills/shared/quiz-last-run.txt` after Step 7 completes.

**If invoked by user trigger:** skip this step, proceed to Step 1.

## Step 1 — Load configuration

Read `~/.claude/skills/_shared/learning-config.md`. Extract KB root path, quiz state path, and the domain list.

## Step 2 — Parse trigger for options

Parse the trigger phrase for:
- **N** (number of cards): default 10; session-start default 4
- **domain** filter: one of the domains listed in learning-config.md, or `all` (default)

| Trigger | N | Domain |
|---------|---|--------|
| "quiz me" | 10 | all |
| "quiz me 15" | 15 | all |
| "quiz me on philosophy" | 10 | philosophy |
| "quiz me 5 on agentic-ai" | 5 | agentic-ai |
| "flash cards" | 10 | all |
| session-start (auto) | 4 | all |

## Step 3 — Load quiz state

Read the quiz state file (path from learning-config.md) using the Read tool.
- If the file does not exist or cannot be read: treat state as `{}`
- If the file content is malformed: treat state as `{}` and note it in the session summary

## Step 4 — Load question pool

**If a domain filter is active (domain ≠ all):**

> ⚠ **MANDATORY — NEVER SKIP OR SUBSTITUTE.** You must run `rag.py` here. Do NOT replace this with `find`, direct file reads, or any sampling of a subset of files. RAG produces a semantically-ranked pool covering the full domain. Skipping it yields a biased, incomplete question set. There is no valid reason to bypass this step.

```bash
python3 ~/LearningOS/rag.py "<domain>" --domain <domain> --top-k 30
```

Parse the printed table into a list of `{name, core_insight, domain}` dicts.
Then read the full KB file for each result to retrieve the complete concept block
(needed for distractors and weighted selection). Use `find <KB_ROOT>/<domain> -name "*.md"`
to confirm file paths match result names.

**If no domain filter (domain = all):**

Run this to get the list of files to parse (KB root from learning-config.md):

```bash
find <KB_ROOT> -name "*.md" -not -name "_lattice.md"
```

For each file returned:
1. Read the file content with the Read tool
2. The **domain** is the parent folder name (e.g. `philosophy`, `frameworks`, `agentic-ai`)
3. Split content on lines beginning with `## ` — each segment is one concept block
4. For each concept block, extract:
   - `name`: text after `## ` on the first line
   - `core_insight`: full text after `**Core insight:**` up to the next `**` or end of block
   - `client_sentence`: text after `**Client-ready sentence:**`, strip quotes; **skip if "N/A"**
   - `framework`: text after `**Framework it extends:**`; **skip if "N/A"**
5. Skip any block where `name` or `core_insight` is empty or absent

Build a flat list: `[{ name, domain, core_insight, client_sentence?, framework? }, ...]`

**If the concept list is empty after filtering:** stop and output: `No concepts found for domain '{domain}'. Check ~/LearningOS/kb/{domain}/ or try a different domain.`

## Step 5 — Generate weighted question pool

For each concept, calculate its draw weight from the state:

| Condition | Weight |
|-----------|--------|
| No entry in state (never seen) | 10 |
| `recall_quality` = "forgot" | 9 |
| `recall_quality` = "forgot", accuracy ≥ 60% | 8 |
| `recall_quality` = "guessed", accuracy < 60% | 6 |
| `recall_quality` = "guessed", accuracy ≥ 60% | 4 |
| `recall_quality` = "recalled", accuracy < 60% | 4 |
| `recall_quality` = "recalled", accuracy 60–79% | 2 |
| `recall_quality` = "recalled", accuracy ≥ 80% | 1 |
| `recall_quality` = "recalled", accuracy ≥ 80%, `last_seen` = today | 1 |

Where `accuracy` = `correct / attempts` from the state entry.

For each concept, eligible question types:

| Type | Eligible when |
|------|--------------|
| `recall_insight` | Always |
| `recall_client` | `client_sentence` is present |
| `name_concept` | Always |
| `framework_link` | `framework` is present |

Each `(concept, question_type)` pair is a **candidate card** with the concept's weight.

**Weighted random sampling without replacement** to draw N cards:
1. Compute total_weight = sum of all remaining candidate weights.
2. Pick a random float r in [0, total_weight).
3. Walk the candidate list, accumulating weights; select where running sum first exceeds r.
4. Remove the selected candidate. Repeat for the next draw.

If total candidates < N: draw all and note "Showing all X available cards" in the header.

## Step 6 — Generate and serve HTML quiz

Build a `questions` JSON array — one entry per drawn card:

```json
{
  "concept":       "{name}",
  "domain":        "{domain}",
  "question_type": "recall_insight | recall_client | name_concept | framework_link",
  "prompt":        "{prompt text}",
  "options":       ["{option A}", "{option B}", "{option C}", "{option D}"],
  "correct_index": 2
}
```

**Prompt text by question type** (same rules as before):
- `recall_insight`: `What's the core insight for: **{name}**?`
- `recall_client`:  `Which is the client-ready sentence for: **{name}**?`
- `name_concept`:   `Which concept does this describe? *"{first 80 chars of core_insight}..."*`
- `framework_link`: `Which framework does **{name}** extend?`

**Options:**
- Pick 3 distractor concepts from the full list (prefer same domain). Use their equivalent field as wrong answers.
- Shuffle all 4 (1 correct + 3 distractors). `correct_index` is the 0-based position of the correct answer **after** shuffling.

**Write and serve:**

1. Read `~/.claude/skills/kb-quiz/scripts/quiz_template.html`
2. Replace the literal string `__QUESTIONS_JSON__` with the JSON-encoded questions array (inline, no pretty-print)
3. Write the result to `/tmp/quiz.html`
4. Delete `/tmp/quiz-results.json` if it exists (clear stale results)
5. Run the server in the background (use Bash tool with `run_in_background=true`):
   ```
   python3 ~/.claude/skills/kb-quiz/scripts/quiz_server.py
   ```
6. Open the browser:
   ```
   open http://localhost:8899
   ```
7. Output exactly one line:
   ```
   Quiz open in your browser — complete all {N} questions, then type anything here to continue.
   ```

Do **not** output the questions, options, or any other text.

## Step 7 — Read results and update state

**When the user types anything after the browser quiz:**

1. Read `/tmp/quiz-results.json`
   - If the file is absent or its `date` field ≠ today: output `No quiz results found — did you click "Save Results → Claude" in the browser?` and stop.
2. Extract the `results` array. Each entry has:
   - `concept`, `domain`, `question_type`
   - `result`: `"correct"` or `"incorrect"`
   - `recall_quality`: `"recalled"` or `"forgot"`
   - `fuzzy`: string or null
3. Treat each entry as one card result — same state-update logic as before.

Update the state for every concept that appeared.

**State entry format:**
```json
{
  "Concept Name": {
    "attempts": 3,
    "correct": 2,
    "last_result": "correct",
    "last_seen": "YYYY-MM-DD",
    "recall_quality": "recalled"
  }
}
```

For each `(concept_name, result, recall_quality)` from the session:

**If no existing entry:** create with attempts=1, correct=(1 if correct else 0), last_result, last_seen=today, recall_quality.

**If existing entry:**
- `attempts` += 1
- `correct` += 1 (only if correct)
- `last_result` = "correct" or "incorrect"
- `last_seen` = today
- `recall_quality` = from this session's reflection

**If concept appeared more than once:** accumulate attempts + correct. Set `last_result` to "incorrect" if any appearance was incorrect. Set `recall_quality` to "forgot" if any appearance was "forgot"; otherwise use the session value.

Write the complete updated state to `<QUIZ_STATE>` (all existing entries included).

## Step 8 — Update kb-frontier and curriculum for forgotten concepts

After saving state, collect all concepts where `recall_quality` = "forgot" this session.

If any forgotten concepts:

**8a — Update kb-frontier:**
1. Read `~/.claude/skills/shared/kb-frontier.md`
2. For each forgotten concept, note its domain
3. Find the line starting with `Prioritise:` in the "This week's focus bias" section
4. If the forgotten domain is not already listed there, append: `, {domain} (quiz gap {YYYY-MM-DD})`
5. Write the updated kb-frontier.md

If a domain already has a quiz gap marker, update its date. Do not duplicate.

**8b — Update curriculum next-actions:**

Domain → curriculum file mapping:
| Domain | Curriculum file |
|---|---|
| `agentic-ai` | `~/LearningOS/curriculum/agentic-ai.md` |
| `frameworks` | `~/LearningOS/curriculum/reading-list.md` |
| `philosophy` | `~/LearningOS/curriculum/reading-list.md` |
| `personal-finance` | `~/LearningOS/curriculum/reading-list.md` |
| `communication` | `~/LearningOS/curriculum/reading-list.md` |

For each forgotten concept:
1. Read the relevant curriculum file
2. Find the `## Next Actions` section
3. Append: `- [ ] Review quiz gap: {concept name} ({YYYY-MM-DD})`
4. Write the updated file

If the same domain has multiple forgotten concepts, append one line per concept. Do not duplicate if the concept already has a quiz gap entry for today.

## Step 9 — Session summary

Output this block (the browser already showed the score — keep this terse):

```
━━━━━━━━━━━━━━━━━━━━━━━━━
Score: {correct}/{total} ({pct}%)
Recalled: {recalled_count} · Forgot: {forgot_count}
{message}
{revisit line if any}
{fuzzy notes if any}
State saved.
━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Message by score:**
- ≥ 80%: `Strong recall. These concepts are compounding.`
- 60–79%: `Decent. Revisit the misses before next session.`
- < 60%: `Knowledge gaps. The weighting will target these next run.`

**Revisit line** (only if any `result` = "incorrect"):
`Revisit: {missed concept names joined by · }`

**Fuzzy notes** (only if any `fuzzy` field is non-null in results):
`Fuzzy: {concept name} — "{fuzzy text}"`

**kb-frontier note** (only if Step 8 updated the file):
`KB frontier updated: {domain list} marked for brief focus.`

## Monitoring

At the end of every successful run, execute the following to log this run to the system-wide monitor:

```bash
python3 ~/.claude/monitor/monitor.py --log '{
  "skill": "kb-quiz",
  "est_input_tokens": 4000,
  "est_output_tokens": 600,
  "steps_taken": 9,
  "outputs_written": 1,
  "success": true
,"model":"claude-sonnet-4-6","model_tier":"balanced","model_verdict":"appropriate"}'
```
