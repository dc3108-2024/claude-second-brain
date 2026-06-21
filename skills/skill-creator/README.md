# skill-creator

Create new skills, improve existing ones, and measure skill performance. Handles the full loop: draft → test → eval → iterate → optimize description → package.

---

## How it works

```
  [User intent]
        │
        ▼
  Capture intent
  (what, when, output format, test cases needed?)
        │
        ▼
  Write BDD spec first
  (references/bdd_spec_template.md)
  (Purpose, Triggers, Scenarios, Output Contract)
        │
        ▼
  Write SKILL.md
  (name, description, workflow, references)
        │
        ▼
  Run test cases (parallel)
  with-skill vs baseline (without-skill or old version)
        │
        ▼
  Launch eval viewer
  (generate_review.py → browser UI)
  Human reviews outputs + leaves feedback
        │
        ▼
  Grade assertions (grader.md)
  Aggregate benchmark (aggregate_benchmark.py)
  Analyst pass (analyzer.md)
        │
        ▼
  Improve skill based on feedback
  Repeat until happy
        │
        ▼
  Optimize description (run_loop.py)
  60/40 train/test split, 5 iterations
        │
        ▼
  Package skill (package_skill.py → .skill file)
```

---

## Trigger phrases

- `"create a skill for X"`
- `"build a new skill"` / `"make a skill"`
- `"improve this skill"` / `"optimize skill description"`
- `"run evals on skill X"` / `"benchmark this skill"`

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Full workflow |
| `scripts/run_eval.py` | Run a single eval query against a skill |
| `scripts/run_loop.py` | Optimization loop: eval → improve → re-eval |
| `scripts/aggregate_benchmark.py` | Aggregate grading results into benchmark.json |
| `scripts/generate_report.py` | Build HTML benchmark report |
| `scripts/package_skill.py` | Package skill into distributable .skill file |
| `scripts/improve_description.py` | Claude: propose better skill description |
| `scripts/utils.py` | Shared utilities |
| `agents/grader.md` | Instructions for the grader subagent |
| `agents/comparator.md` | Instructions for blind A/B comparison |
| `agents/analyzer.md` | Instructions for benchmark analysis |
| `references/bdd_spec_template.md` | Spec template to fill in before writing code |
| `references/schemas.md` | JSON schemas for evals.json, grading.json, etc. |

---

## The eval-iterate loop

1. Write a draft skill
2. Create 2-3 test prompts
3. Spawn parallel subagents: with-skill AND baseline (without-skill)
4. Grade assertions, launch browser viewer
5. Human reviews and leaves feedback
6. Improve skill based on feedback
7. Repeat from step 3 until output quality is stable
8. Run description optimization (`run_loop.py`)
9. Package with `package_skill.py`

---

## Description optimization

The `description` field in SKILL.md frontmatter drives when Claude invokes the skill. Bad description = skill never triggers (or triggers when it shouldn't).

```bash
python -m scripts.run_loop \
  --eval-set trigger-eval.json \
  --skill-path /path/to/skill \
  --model <model-id> \
  --max-iterations 5
```

Produces `best_description` — the version with the highest held-out test score.
