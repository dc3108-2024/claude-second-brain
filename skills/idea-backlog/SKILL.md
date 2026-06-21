---
name: idea-backlog
description: Idea Backlog Skill — centralised backlog manager for feature development, pipeline enhancements, bug fixes, and ideas. Multi-source intake (chat + Slack + monitor auto-ingest). Smart prioritisation and Kanban view on demand. Trigger on "add to backlog", "show backlog", "what's next", "kanban", "triage backlog", "recommend from backlog".
---

# Idea Backlog Skill

Centralised backlog manager for feature development, pipeline enhancements, bug fixes, and ideas. Multi-source intake (chat + Slack + monitor auto-ingest). Smart prioritisation and Kanban view on demand.

**Paths, categories, PDF colours:** `references/config.md`

## Backlog file

All items live at the backlog path in `references/config.md`.
If the file doesn't exist, create it with the header structure first.

## Status lifecycle

```
Backlog → In Progress → Done
```

Existing items with `Status: Idea` or `Status: Parked` are treated as `Backlog` by the scorer and Kanban — no migration needed.

## Categories

`Personal Tools | Career/BD | Content | Infrastructure | Finance | Pipeline Fix`

## Modes

### 1. ADD — "add to backlog: [idea]" / "log this idea: [idea]" / "remember this idea: [idea]"

Append a new entry to `ideas.md`:

```markdown
## [Title]
- **Category:** [Personal Tools | Career/BD | Content | Infrastructure | Finance | Pipeline Fix]
- **Priority:** [High | Medium | Low]
- **Status:** Backlog
- **Added:** YYYY-MM-DD
- **Notes:** [brief description, dependencies, urgency]
```

Confirm in conversation: "Added: [title]"

### 2. DUMP — "dump idea backlog" / "show my backlog" / "idea backlog to PDF"

1. Read backlog file (path from `references/config.md`)
2. Parse all entries
3. Generate a PDF (see layout below)
4. Save to PDF output folder, named `Idea_Backlog_[YYYY-MM-DD].pdf`
5. Auto-open
6. Show summary in conversation (count by category and priority)

### 3. UPDATE — "update backlog: [title] → [new status/priority/notes]"

Find the entry by title, update the specified field, save.

**Status-change notification:** If the new status is `In Progress` or `Done`, run:
```bash
echo "\"[Title]\" moved to [new status]" | python3 ~/.claude/skills/shared/post_to_slack.py
```

**Usage log:** Also append an actioned event to `references/usage_log.jsonl`:
```bash
python3 -c "
import json; from datetime import date; from pathlib import Path
log = Path('~/.claude/skills/idea-backlog/references/usage_log.jsonl').expanduser()
event = json.dumps({'event': 'actioned', 'date': date.today().isoformat(), 'title': '[Title]', 'to_status': '[new status]', 'category': '[Category]'})
open(log, 'a').write(event + '\n')
"
```

### 4. REVIEW — "review backlog" / "what's in my backlog"

Read `ideas.md` and display a summary table in conversation. No PDF needed.

### 5. NEXT — "what's next" / "what should I work on" / "next item" / "recommend from backlog"

Run `scripts/recommend.py` and display the top 3 scored items in conversation:

```bash
python3 ~/.claude/skills/idea-backlog/scripts/recommend.py
```

### 6. KANBAN — "kanban" / "show kanban" / "backlog status" / "show board"

Open the live Kanban board (auto-starts on boot, port 8788, refreshes every 30s):

```bash
open http://localhost:8788
```

If the server is not running:
```bash
python3 ~/.claude/skills/idea-backlog/scripts/kanban_server.py &
```

### 7. FOCUS — "set focus: [word]"

Write the focus word to `references/focus.txt`. Valid values: `career`, `infrastructure`, `content`, `finance`, `tools`, `pipeline`. Boosts matching category by +3 in NEXT recommendations. Expires automatically after 7 days.

```bash
echo "[word]" > ~/.claude/skills/idea-backlog/references/focus.txt
```

Confirm: "Focus set to [word] — boosts [Category] items in recommendations."

### 8. TRIAGE — "triage backlog" / "clean up backlog" / "stale backlog"

1. Read `ideas.md`
2. Filter to open items (Status ≠ Done/Parked) older than 30 days, sorted by age descending
3. Display a compact table:

| # | Title | Category | Priority | Age | Score |
|---|-------|----------|----------|-----|-------|
| 1 | ...   | ...      | ...      | 60d | 12    |

4. Ask: "For each, say **Keep**, **Park**, or **Done** — or give me a list of numbers to bulk-park."
5. Apply the user's decisions via UPDATE mode logic.

**Threshold:** Default 30 days. If user says "triage backlog 60 days" use 60.

### 9. AUTONOMOUS — "autonomous pick" / "pick from backlog" / "what can you work on now"

Score open backlog items for autonomy-readiness and either notify or execute.

```bash
# Notify only (Slack + CLI)
python3 ~/.claude/skills/idea-backlog/scripts/autonomous_picker.py

# Dry run — prints to CLI only, no Slack
python3 ~/.claude/skills/idea-backlog/scripts/autonomous_picker.py --dry-run

# Pick + draft + notify done — executes for Content / Career/BD items
python3 ~/.claude/skills/idea-backlog/scripts/autonomous_picker.py --execute
```

**Autonomy eligibility:**

| Category | Autonomous? | Notes |
|---|---|---|
| Content | High | LinkedIn post, brief — can draft without user |
| Career/BD | Medium | Research, analysis — can generate |
| Personal Tools | Low | Only if notes are specific enough |
| Finance | Never | Requires user decisions |
| Infrastructure | Never | Too risky |
| Pipeline Fix | Never | Requires code review |

**Output (--execute, Content items):** Draft saved to `~/Desktop/Autonomous_Drafts/YYYY-MM-DD-slug.md`

**To schedule daily at 09:00:**
```bash
crontab -e
# Add:
0 9 * * * python3 ~/.claude/skills/idea-backlog/scripts/autonomous_picker.py
```

### 10. CLEAR FOCUS — "clear focus"

Delete `references/focus.txt`:
```bash
rm -f ~/.claude/skills/idea-backlog/references/focus.txt
```

## PDF layout

Use reportlab.

```python
import os, subprocess, datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle

date_str = datetime.date.today().strftime("%Y-%m-%d")
output_path = f"{folder}/Idea_Backlog_{date_str}.pdf"
```

**Sections (in order):**
1. Title: "Idea Backlog" + date + total count
2. Summary table: count by category × priority
3. Per category: section header + idea cards
4. Each idea card: title (bold), priority badge, status, notes, date added

**Priority colours and categories:** from `references/config.md`

## ideas.md file structure

```markdown
# Idea Backlog

<!-- Add new ideas below. Most recent at top. -->

## [Idea Title]
- **Category:** ...
- **Priority:** ...
- **Status:** ...
- **Added:** ...
- **Source:** ...     ← optional; written by Slack/monitor ingestor
- **Notes:** ...

---
```

## Triggers

Use this skill when the user says:
- "add to backlog", "log this idea", "remember this idea"
- "dump idea backlog", "backlog to PDF", "show my backlog"
- "what's in my backlog", "review backlog"
- "update backlog"
- "what's next", "what should I work on", "next item", "recommend from backlog"
- "kanban", "show kanban", "backlog status", "show board"
- "set focus:", "clear focus"
- "triage backlog", "clean up backlog", "stale backlog"
- "/idea-backlog"

---

## Monitoring

At the end of every successful run (DUMP, NEXT, KANBAN), log the run:

```bash
python3 ~/.claude/monitor/monitor.py --log '{"skill":"idea-backlog","est_input_tokens":500,"est_output_tokens":300,"steps_taken":2,"outputs_written":1,"success":true,"model":"none","model_tier":"none","model_verdict":"no-claude-call"}'
```

Adjust `steps_taken` and `outputs_written` to match the actual run.

<!-- MONITOR_BLOCK -->
