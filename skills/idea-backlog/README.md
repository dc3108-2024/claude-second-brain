# idea-backlog

Centralised backlog manager for features, ideas, and pipeline improvements. Multi-source intake from chat and Slack. Smart scoring for prioritisation. Live Kanban board. Autonomous execution for low-risk items.

---

## How it works

```
  [Idea sources]
  Chat / Slack / Monitor auto-ingest
        │
        ▼
  ideas.md  (flat markdown file)
  One entry per idea:
    Title, Category, Priority, Status, Notes
        │
        ├── REVIEW mode  → table summary in conversation
        │
        ├── DUMP mode    → scored PDF by category
        │
        ├── NEXT mode    → recommend.py scores items
        │   (priority × recency × focus boost)
        │   returns top 3 to work on
        │
        ├── KANBAN mode  → live web UI (port 8788)
        │   (kanban_server.py, refreshes every 30s)
        │
        ├── TRIAGE mode  → surface stale items (>30d)
        │   bulk-park or close old items
        │
        └── AUTONOMOUS   → score for auto-execution eligibility
            Content/Career items can self-draft
            Finance/Infra/Pipeline: never autonomous
```

---

## Trigger phrases

| Phrase | Mode |
|---|---|
| `"add to backlog: X"` / `"log this idea: X"` | ADD |
| `"show my backlog"` / `"backlog to PDF"` | DUMP |
| `"review backlog"` / `"what's in my backlog"` | REVIEW |
| `"update backlog: X"` | UPDATE |
| `"what's next"` / `"recommend from backlog"` | NEXT |
| `"kanban"` / `"show board"` | KANBAN |
| `"set focus: [word]"` / `"clear focus"` | FOCUS |
| `"triage backlog"` / `"stale backlog"` | TRIAGE |
| `"autonomous pick"` / `"what can you work on now"` | AUTONOMOUS |

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Full mode documentation |
| `scripts/recommend.py` | Score items and return top 3 |
| `scripts/kanban_server.py` | Live HTTP Kanban server (port 8788) |
| `scripts/kanban.py` | Kanban logic |
| `scripts/search.py` | Search within backlog |
| `scripts/autonomous_picker.py` | Score + execute eligible items |
| `scripts/autonomous_runner.py` | Draft LinkedIn posts / research briefs autonomously |
| `scripts/ingest_monitor.py` | Auto-ingest from Slack / monitor |
| `references/config.md` | Backlog file path, PDF folder, colours |
| `references/usage_log.jsonl` | Actioned event log |

---

## Setup

1. Edit `references/config.md` to set your backlog file path and PDF output folder
2. Create the `ideas.md` file at that path (the skill creates it on first ADD if missing)
3. Install dependencies: `pip install reportlab`
4. Optional: start Kanban server on boot via launchd/cron

### Slack intake

Wire the Slack bot to call the ingest monitor when a message arrives in a specific channel. The ingestor parses the message and appends a new entry to `ideas.md`.

---

## Focus boost

Set a focus category to boost items in that category when scoring for NEXT:

```
set focus: infrastructure
```

This writes `infrastructure` to `references/focus.txt` and boosts Infrastructure items by +3 for 7 days. Clear with `clear focus`.
