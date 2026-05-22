# Memory System

Claude Code supports a persistent memory system that survives across conversations.
Memory files are plain markdown with YAML frontmatter — Claude reads them at session
start and writes to them during conversations.

## Directory

```
~/.claude/projects/-Users-<username>/memory/
├── MEMORY.md           # Index — one line per memory, loaded every session
├── user_*.md           # Who you are: role, finance, learning, values
├── feedback_*.md       # How Claude should behave: corrections + confirmations
└── project_*.md        # What you're working on: goals, decisions, context
```

## How it works

1. `MEMORY.md` is loaded into every conversation as context
2. When Claude learns something worth keeping, it writes a new `.md` file and adds a line to `MEMORY.md`
3. Files are plain markdown — edit them directly at any time

## Memory types

| Type | What it stores | Example |
|---|---|---|
| `user` | Role, goals, expertise, preferences | "Senior engineer, deep Python, new to React" |
| `feedback` | Behavioural corrections and confirmations | "Never mock the database in tests — burned by this before" |
| `project` | Ongoing work, decisions, context | "Auth rewrite is driven by compliance, not tech debt" |
| `reference` | Pointers to external systems | "Pipeline bugs tracked in Linear project INGEST" |

## Auto-sync

The `sync-config.py` script in the root of this repo copies all memory files to
`~/.claude-backup/auto-memory/` on every write. Wire it up with the PostToolUse hook
in `settings.json.example` and your memory is version-controlled automatically.

## Restoring on a new machine

```bash
# Copy auto-memory files back to the right place
cp ~/.claude-backup/auto-memory/*.md \
   ~/.claude/projects/-Users-$(whoami)/memory/
```
