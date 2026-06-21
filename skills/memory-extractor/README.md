# memory-extractor

Extract implicit memories from a Claude Code session transcript and write them to your persistent memory directory.

Every session contains decisions, corrections, and preferences that should carry forward. This skill scans the session transcript, identifies what's worth keeping, deduplicates against existing memory, and writes structured `.md` files you'll have in future sessions.

---

## How it works

```
  [Session transcript (.jsonl)]
        │
        ▼
  Parse user turns only
  (cap at 8000 chars)
        │
        ▼
  Load existing MEMORY.md index
  (deduplication check)
        │
        ▼
  Claude: identify new implicit memories
    - feedback: "don't do X", "yes exactly that"
    - user: facts about you (role, preferences, constraints)
    - project: state changes (started, completed, key decision)
    - reference: pointers to external resources
        │
        ▼
  Write .md files to memory/ directory
  Append entries to MEMORY.md index
  Log run to usage_log.jsonl
```

---

## Trigger phrases

- `"extract memories from last session"`
- `"save memories from session <uuid>"`
- `"extract memories from this session"`

---

## Usage

```bash
# Process most recent session
python3 ~/.claude/skills/memory-extractor/scripts/extract.py --latest

# Process specific session
python3 ~/.claude/skills/memory-extractor/scripts/extract.py --session <uuid>

# Process all unprocessed sessions from last 48h (good for cron)
python3 ~/.claude/skills/memory-extractor/scripts/extract.py --all-new

# Dry run — see what would be written without writing anything
python3 ~/.claude/skills/memory-extractor/scripts/extract.py --latest --dry-run
```

---

## Setup

1. Edit `scripts/extract.py` — set `MEMORY_DIR` and `TRANSCRIPT_DIR` to match your Claude Code install path
2. Or set the environment variable: `CLAUDE_PROJECTS_DIR=/path/to/your/projects`

### Cron mode

Schedule daily extraction with cron:
```bash
# Add to crontab: run at 11pm every day
0 23 * * * python3 ~/.claude/skills/memory-extractor/scripts/extract.py --all-new
```

---

## What it skips

- Facts already in MEMORY.md (deduplication)
- Tool outputs and search results
- Temporary state ("will check tomorrow")
- Sessions modified within the last 2 hours (may still be active)
- Sessions shorter than 300 chars (no useful content)

---

## Memory file format

```markdown
---
name: feedback-on-output-format
description: User prefers bullet points over paragraphs for analysis output
metadata:
  type: feedback
  source_type: implicit
  created_date: 2026-01-15
  confidence: medium
---

Always use bullet points for analysis outputs, not paragraphs.

**Why:** User said "this is too wordy, give me bullets" when receiving a paragraph-format response.

**How to apply:** Default to bullet points for any analytical or structured output. Use prose only for narrative content.
```
