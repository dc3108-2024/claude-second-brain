---
name: pm-workflow
description: >
  AI-assisted PM workflow — converts raw problem descriptions into structured PRDs
  and user stories with acceptance criteria. Two composable scripts: prd_drafter.py
  (sound bytes → PRD) and story_generator.py (PRD → JIRA-ready user stories).
---

# PM Workflow

Two scripts that compose into a full requirements pipeline:

```
problem description
      │
      ▼
prd_drafter.py          → structured PRD (JSON)
      │
      ▼
story_generator.py      → user stories + acceptance criteria (JSON)
```

## Quick start

```bash
# Full pipeline in one command
python3 skills/pm-workflow/scripts/prd_drafter.py \
    "PMs copy-paste user stories into JIRA manually after every sprint planning. Takes 2 hours." | \
    python3 skills/pm-workflow/scripts/story_generator.py
```

## prd_drafter.py

Takes a 1-3 sentence problem description. Returns a structured PRD with:
- Feature name
- Problem statement (who, what pain, current workaround)
- Personas (1-3)
- Observable feature capabilities
- Measurable success metrics
- Explicit out-of-scope items

```bash
# Interactive
python3 skills/pm-workflow/scripts/prd_drafter.py "your problem here"

# From a file
cat problem.txt | python3 skills/pm-workflow/scripts/prd_drafter.py
```

## story_generator.py

Takes a PRD dict (from prd_drafter.py or a hand-crafted JSON file). Returns 2-4
user stories, each with:
- "As a [persona], I want [capability] so that [outcome]" format
- 2-4 fully self-contained acceptance criteria (implementable without reading the PRD)
- Build-order dependencies between stories

```bash
# From a saved PRD JSON file
python3 skills/pm-workflow/scripts/story_generator.py prd.json

# Paste PRD JSON interactively
python3 skills/pm-workflow/scripts/story_generator.py
```

## Why composable scripts?

Each script is a pure function: JSON in, JSON out. This means you can:
- Stop after `prd_drafter.py` to review the PRD before generating stories
- Replace `prd_drafter.py` with a hand-crafted PRD if you already have one
- Pipe `story_generator.py` output into a JIRA API call or your own tooling

## Design principles

**Critique loops, not raw calls.** Every Claude call goes through a critique function
(`_critique`) that checks the output schema before returning it. Hard failures retry
automatically up to 3 times with the failure reason prepended to the prompt. This is
why you get valid JSON every time, even when Claude decides to add prose.

**Self-contained acceptance criteria.** The story_generator prompt explicitly instructs
Claude to include specific values, data formats, edge cases, and constraints in each AC
so a developer can implement it without asking follow-up questions. The critique function
enforces this — an AC list cannot be empty.

**Dependency graph.** Stories reference each other by 0-based index when one is blocked
by another. The critique validates that no story references itself or an out-of-range index.

## Extending

To push stories into JIRA, add a third script:

```python
# skills/pm-workflow/scripts/jira_pusher.py
import json, sys
stories = json.loads(sys.stdin.read())
for story in stories:
    # create_jira_issue(story["summary"], story["description"])
    pass
```

Then chain it:
```bash
python3 prd_drafter.py "problem" | python3 story_generator.py | python3 jira_pusher.py
```
