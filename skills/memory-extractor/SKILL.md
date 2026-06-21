---
name: memory-extractor
description: "Extract implicit memories from a session transcript and write them to the memory directory."
trigger: "extract memories from [last/this] session" | "save memories from session [uuid]"
---

# Memory Extractor

Runs `scripts/extract.py` to scan a session transcript, identify new implicit memories (facts, preferences, decisions, corrections), and write them to the memory directory.

## When to invoke
- User says "extract memories from last session"
- User says "save memories from session <uuid>"
- End of a long session with new decisions, corrections, or project state changes

## Usage

```bash
# Process most recent session
python3 ~/.claude/skills/memory-extractor/scripts/extract.py --latest

# Process specific session by UUID
python3 ~/.claude/skills/memory-extractor/scripts/extract.py --session <uuid>

# Process all unprocessed sessions from last 48h (cron mode)
python3 ~/.claude/skills/memory-extractor/scripts/extract.py --all-new

# Dry run (print without writing)
python3 ~/.claude/skills/memory-extractor/scripts/extract.py --latest --dry-run
```

## What it extracts
- **feedback**: behavioral corrections or confirmations ("don't do X", "yes exactly that")
- **user**: new facts about you (role, preferences, constraints)
- **project**: project state changes (started, completed, paused)
- **reference**: pointers to external resources revealed in conversation

## What it skips
- Facts already in MEMORY.md
- Tool outputs and search results
- Temporary/ephemeral state ("will check tomorrow")
- Speculative inferences

## Output
- Writes `.md` files to the memory directory (`~/.claude/projects/-Users-<username>/memory/`)
- Appends new entries to `MEMORY.md`
- Logs run to `references/usage_log.jsonl`

## Memory file format

Each extracted memory is written as a standalone `.md` file with frontmatter:

```markdown
---
name: <slug>
description: <one-line summary>
metadata:
  type: <feedback|user|project|reference>
  source_type: implicit
  created_date: YYYY-MM-DD
  confidence: medium
---

<memory content>
```

## Configuration

The script uses these paths (configurable by editing the constants at the top of `extract.py`):

| Constant | Default | Purpose |
|---|---|---|
| `MEMORY_DIR` | `~/.claude/projects/-Users-<username>/memory` | Where memory files are written |
| `TRANSCRIPT_DIR` | `~/.claude/projects/-Users-<username>` | Where session `.jsonl` files live |
| `MAX_TRANSCRIPT_CHARS` | `8000` | Transcript truncation limit |
| `MIN_CONTENT_CHARS` | `300` | Skip short sessions |
| `ACTIVE_SESSION_GRACE` | `7200` | Skip files modified within last 2h (likely still open) |
