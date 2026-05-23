# Claude Code — Personal Second Brain

A reference architecture for turning Claude Code from a chat interface into
personal infrastructure. Fork it, adapt it to your context, and stop starting
from scratch every session.

---

## The idea

Most people use AI reactively — ask a question, get an answer, move on.
This setup is different. It's built on a single principle:

> **The AI work you do today should make your work next month easier.**

That means persistent memory, reusable skills, version-controlled configuration,
and automation that runs without you having to remember to trigger it.

---

## What's in this repo

```
claude-second-brain/
│
├── CLAUDE.md.template          # Your global Claude instructions — who you are,
│                               # how you think, how you want Claude to behave.
│                               # Loaded into every conversation automatically.
│
├── settings.json.example       # Hook architecture: two PostToolUse hooks that
│                               # auto-commit skills and config to GitHub on every
│                               # write. One PreToolUse hook that blocks accidental
│                               # deletion of skill files.
│
├── sync-config.py              # Config backup script. Copies CLAUDE.md, memory
│                               # files, and settings to ~/.claude-backup/ on every
│                               # change. Wire it up with the hook and your config
│                               # is version-controlled automatically.
│
├── skills/
│   ├── generate-readme.py      # Scans all SKILL.md files, auto-classifies skills
│   │                           # by keyword, and regenerates README.md. Runs via
│   │                           # pre-commit hook — README is always current.
│   │
│   ├── _hooks/
│   │   └── pre-commit          # Git hook: regenerates skills README before every
│   │                           # commit. Install with: cp _hooks/pre-commit
│   │                           # .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
│   │
│   ├── _template/
│   │   └── SKILL.md            # Starter template for any new skill.
│   │
│   ├── research-brief/         # Example: web research → synthesised briefing
│   │   └── SKILL.md
│   │
│   └── process-diagram/        # Example: any process description → draw.io diagram
│       └── SKILL.md
│
└── memory/
    ├── README.md               # How the memory system works
    └── _template.md            # Starter template for any memory file
```

---

## How the automation works

### Skills auto-push to GitHub

Add this `PostToolUse` hook to your `~/.claude/settings.json`:

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "{ f=$(jq -r '.tool_input.file_path // empty'); [[ \"$f\" == */.claude/skills/* ]] && git -C ~/.claude/skills add -A && git -C ~/.claude/skills commit --quiet -m \"auto: skill update\" && git -C ~/.claude/skills push --quiet; } 2>/dev/null || true",
    "async": true
  }]
}
```

Every time you write or edit a skill file, it commits and pushes silently in the
background. You never manually `git push` your skills library.

### Skills README auto-regenerates

Install the pre-commit hook in your skills repo:

```bash
cp skills/_hooks/pre-commit ~/.claude/skills/.git/hooks/pre-commit
chmod +x ~/.claude/skills/.git/hooks/pre-commit
```

Before every commit, `generate-readme.py` scans all `SKILL.md` files, classifies
each skill by keyword matching, and rebuilds `README.md`. Add a new skill, commit
it — the index updates itself.

### Config auto-backs-up

```bash
# 1. Create the backup repo
mkdir ~/.claude-backup && cd ~/.claude-backup
git init && git remote add origin <your-private-github-repo>

# 2. Copy sync-config.py to your Claude config dir
cp sync-config.py ~/.claude/sync-config.py

# 3. Add the config hook from settings.json.example to ~/.claude/settings.json
```

From that point on, every change to `CLAUDE.md`, your memory files, or settings
triggers `sync-config.py` → commits → pushes automatically.

---

## Skills

A skill is a focused instruction set for a repeatable task. Claude loads it on
demand and follows it exactly.

### Anatomy of a skill

```
skill-name/
├── SKILL.md          # The workflow — steps, triggers, quality rules (~150 lines max)
├── scripts/          # Executable code invoked by the workflow (optional)
└── references/       # Persona data and config: lenses, paths, scenarios (optional)
```

**`SKILL.md` only describes the workflow.** Code goes in `scripts/`, data goes in `references/`.

### Blueprint vs Data — the most important pattern

The easiest mistake when building personal skills is letting persona-specific data creep into `SKILL.md`. It starts small: you hardcode your own file path, embed your domain focus, inline your financial targets. Over time every skill becomes a mix of workflow logic and personal data — and changing anything means editing the skill itself.

The fix is a clean separation: **`SKILL.md` is the blueprint, `references/` is the data.**

| What belongs in `SKILL.md` | What belongs in `references/` |
|---|---|
| Steps and decision logic | File paths and folder locations |
| Output format templates | Personal lenses and analytical filters |
| Quality rules and conditions | Financial scenarios and account details |
| Orchestration (which sub-skills to call) | Domain context and professional role |
| Trigger phrases | Search topics and trusted sources |

**Before** — data embedded in the workflow:

```markdown
## Step 2 — Synthesise

Every item must connect to one of the four lenses:
Career · Regulatory · Wealth · Thought leadership

### Career
What does this mean for my role or positioning? What specific action does it unlock?
```

**After** — workflow references the data file:

```markdown
## Step 2 — Synthesise

Read `references/lenses.md` for the current lens definitions.
Apply each lens to the content. Every item must connect to at least one.
```

```markdown
# references/lenses.md

## Career
What does this mean for my role or positioning? What specific action does it unlock?
```

**Why it matters:**
- A lens changes → edit `references/lenses.md`, not the skill
- A new account → edit `references/financial-config.md`, not the skill
- Share a skill → swap or strip `references/`, the workflow is intact
- Audit a skill → `SKILL.md` tells you HOW, `references/` tells you FOR WHOM

The `lens-synthesis` skill in this repo is the canonical example of this pattern.

### Adding a new skill

1. Create `~/.claude/skills/<skill-name>/SKILL.md`
2. Use the YAML frontmatter format from `skills/_template/SKILL.md`
3. The description field drives auto-classification — write it to match your trigger phrases
4. Commit — the pre-commit hook regenerates the README automatically

---

## Feedback loops

Skills are one-directional by default — you trigger them, they produce output.
The next level is closing the loop so the system compounds without prompting.

Three patterns that self-reinforce over time:

| Loop | Trigger | What happens |
|---|---|---|
| **Briefs → KB** | After each weekly brief | A sync skill extracts the top structurally significant concepts and writes them to the KB automatically — no manual capture step |
| **Session → alignment** | Every session end (`PostSessionStop` hook) | A script detects explicit goal-revision signals in the transcript and updates your personal alignment filter if found |
| **KB → research bias** | Weekly cron (e.g. Sunday night) | A script scans the KB, classifies sparse vs dense areas, and writes a shared focus-bias file — injected into both briefs and the capture pipeline so the system naturally fills gaps |

The shared state is a single file (`shared/kb-frontier.md`). Written once a week
by a cron script, read by any skill that benefits from knowing where the KB is thin.

See [EXTENDING.md](./EXTENDING.md) for implementation details on all three loops.

---

## Memory

Claude's memory system persists facts, preferences, and project context across
conversations. Files live in:

```
~/.claude/projects/-Users-<username>/memory/
```

The index file `MEMORY.md` is loaded into every session. Individual memory files
are loaded on demand when relevant. See `memory/README.md` for the full breakdown.

---

## Restoring on a new machine

If your skills and config are in separate private GitHub repos (the recommended
setup), restore is two commands:

```bash
gh auth login
gh repo clone <your-username>/claude-config ~/.claude-backup && bash ~/.claude-backup/restore.sh
```

`restore.sh` handles the rest: config files, memory, skills clone, and any
additional project repos you've added to the script (see below).

Everything — skills, memory, hooks, settings, project repos — is back exactly
as you left it.

### Adding project repos to restore.sh

If you have private repos for your KB, financial tools, or other projects that
Claude writes to, add them to `restore.sh` using the same pattern:

```bash
MYPROJECT="$HOME/YourProject"
if [[ -d "$MYPROJECT/.git" ]]; then
  echo "→ YourProject already present — skipping clone"
else
  echo "→ Cloning YourProject..."
  gh repo clone <your-username>/your-project "$MYPROJECT"
  echo "  ✓ YourProject cloned"
fi
```

Pair each clone with the corresponding auto-sync hook in `settings.json.example`
and the repo stays current without any manual `git push`.

---

## Getting started

1. **Fork this repo**
2. **Fill in `CLAUDE.md.template`** with your actual context and rename it to `CLAUDE.md`
3. **Copy `CLAUDE.md` to `~/.claude/CLAUDE.md`**
4. **Create a private GitHub repo for your skills library**, push `skills/` to it
5. **Install the hooks** from `settings.json.example` into `~/.claude/settings.json`
6. **Build your first skill** using the template in `skills/_template/SKILL.md`

The two example skills (`research-brief`, `process-diagram`) are working starting
points — adapt them to your domain and trigger phrases.

---

## Going further

See [`EXTENDING.md`](./EXTENDING.md) for the path from scaffold to production — how
each skill grows, when to split monolithic skills into composable micro-skills, which
MCP integrations unlock the most, and what not to build.

---

## Philosophy

Skills are cheap to build and infinitely reusable. Memory accumulates without effort.
Config is version-controlled and portable. The result is a setup where each session
compounds the ones before it — context grows, quality improves, and the gap between
"I need X" and "X is done" keeps shrinking.

That's the difference between using AI and operating it.
