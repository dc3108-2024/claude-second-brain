# Claude Code — Personal AI OS Scaffold

Most people use AI reactively — ask a question, get an answer, move on.

This is the infrastructure for the other approach: building a system where the AI
work you do today compounds into better, faster output next month.

---

## Three builds, up close

Start here. Each is a short, plain-English walkthrough of a real build — the problem,
what changed, and the thinking underneath — with the technical detail one click further in.

- **[JIRA PM Factory →](./docs/builds/JIRA_PM_FACTORY.md)** — a stakeholder conversation
  becomes a ready, dependency-mapped JIRA backlog the same day, with a person signing off at
  every gate.
- **[Feedback Loops →](./docs/builds/FEEDBACK_LOOPS.md)** — how an AI system gets *better* the
  more it runs: checks before it ships and while it runs, and a fix that can never quietly regress.
- **[Financial OS →](./docs/builds/FINANCIAL_OS.md)** — a drawer full of statements becomes one
  live position, with personal data stripped before any model sees it.

---

## What this has produced

Not demos. Not examples. Real features, built end to end, with the skills in this repo:

### Voice recording → structured JIRA backlog in under 5 minutes

A stakeholder requirements interview lands in a watch folder. A background daemon
picks it up, transcribes it locally via Whisper, and passes it to Claude — which
strips interviewer questions and filler, preserves the stakeholder's exact framing,
and flags ambiguous requirements. A Slack message appears with the distilled
requirements and routing confidence. One reply. Confluence PRD, JIRA epic, and
dependency-mapped user stories created automatically.

[Read the PRD →](./docs/case-studies/audio-interview-bridge.md)

### Multi-project routing without manual tagging

A Claude classifier reads the distilled content of any voice recording and routes
it to the correct JIRA project — not by filename convention, but by understanding
what the content is about. Confidence and rationale surface in Slack so the PM
can verify before approving. New projects are added via config, not code.

[Read the PRD →](./docs/case-studies/smart-content-routing.md)

### A PM lifecycle in three commands

`new feature: X` → PRD drafted, Confluence page created, JIRA epic opened,
stories generated with acceptance criteria and dependency links, Slack notification
sent. `build KEY-N` → story moved to In Progress, writing plan generated.
`close KEY-N, PR: <url>` → story Done, PR linked, Confluence updated, Slack notified.

The PM owns the full cycle — from raw idea to developer-ready backlog — without
handing off at any step.

[Read the runbook →](./docs/pm-pipeline-runbook.md)

---

## The factory model

The first skill takes weeks. The most recent took a weekend.

Same complexity. Different infrastructure maturity.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Personal AI OS                               │
│            Agentic infrastructure that compounds                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
   [Domain Modules]    [Shared Harness]     [Feedback Loops]
          │                    │                    │
  ┌───────┴──────┐   ┌─────────┴──────┐   ┌────────┴──────────┐
  │ Learning OS  │   │ call_claude_   │   │ token_usage.jsonl │
  │ PM Loop      │   │ with_critique()│   │ critique_analysis │
  │ Financial OS │   │ parse_json_    │   │ prompt_health.md  │
  │ Other domains│   │ response()     │   │ HITL refactor     │
  └──────────────┘   │ Memory system  │   └───────────────────┘
                     │ Slack interface│
                     │ Self-correction│
                     └────────────────┘
```

A step that was failing 89% of the time was fixed once and never failed again.
The monitor caught it. The feedback loop surfaced it. The fix was locked in.

---

## Who this is for

- PMs and operators who want to own their full workflow end to end — not just prompt
- Engineers building personal or team-level AI infrastructure
- Anyone who thinks in systems and wants AI that compounds, not just assists

---

<!-- ARCH-DIAGRAM-START -->
## How it works

The factory's output is **new agentic applications**. The shared infrastructure
makes each one cheaper to build than the last.

```
INPUTS
voice memos · files & data · notes · web research · data feeds
                             │
                             ▼
APPS & WORKFLOWS PRODUCED — marginal cost falls with every new build
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Financial OS │ Learning OS  │   PM Loop    │  Home OS     │
│    weeks     │    days      │    hours     │   weekend    │
└──────────────┴──────────────┴──────────────┴──────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│                      SHARED HARNESS                        │
│  Claude instrumentation  ·  prompt health monitor          │
│  memory layer  ·  self-correcting feedback loops           │
│  single Slack interface across all modules                 │
│                                          ↩ fix once,       │
│                                            all improve     │
└────────────────────────────────────────────────────────────┘
                             │
                             ▼
    New applications. Same complexity. Lower cost every time.
```
<!-- ARCH-DIAGRAM-END -->

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
├── lib/
│   ├── claude_utils.py         # LLM harness: call_claude_with_critique(),
│   │                           # parse_json_response(), auto_select_tier().
│   │                           # Import this in any skill that calls Claude.
│   ├── memory.py               # Memory CRUD: read_memory(), save_memory(),
│   │                           # list_memories(), search_memories().
│   └── models.json             # Tier-to-model mapping. Swap models here without
│                               # touching any skill code.
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
│   │   ├── SKILL.md            # Starter template for any new skill.
│   │   └── scripts/
│   │       └── example_skill.py  # Complete runnable skill using all lib/ patterns.
│   │
│   ├── pm-workflow/            # Runnable Python scripts for PM workflows
│   │   ├── SKILL.md            # Pipeline: sound bytes → PRD → user stories
│   │   ├── scripts/
│   │   │   ├── prd_drafter.py      # Problem description → structured PRD (JSON)
│   │   │   └── story_generator.py  # PRD → user stories + acceptance criteria (JSON)
│   │   └── references/
│   │       └── prd_template.md     # PRD field definitions injected into the prompt
│   │
│   ├── research-brief/         # Web research → synthesised briefing
│   │   └── SKILL.md
│   │
│   ├── process-diagram/        # Any process description → draw.io diagram
│   │   └── SKILL.md
│   │
│   ├── audio-interview-bridge/ # Voice memo → Whisper → distil → JIRA/Confluence
│   │   ├── SKILL.md
│   │   ├── scripts/            # audio_bridge.py, distil.py, router.py
│   │   └── references/         # routing_config.json (project routing table)
│   │
│   ├── jira-pm/                # PM lifecycle: OPEN / BUILD / CLOSE / BRIDGE
│   │   ├── SKILL.md
│   │   ├── scripts/            # prd_drafter.py, story_generator.py, infra_classifier.py
│   │   └── references/         # confluence_spaces.md, jira_transitions.json
│   │
│   ├── humanize-ai-writing/    # Strip AI patterns, add real voice
│   │   ├── SKILL.md
│   │   └── references/         # banned-list.md (comprehensive pattern list)
│   │
│   ├── document-8020/          # Long doc → 80/20 reference PDF
│   │   ├── SKILL.md
│   │   └── scripts/            # build_8020_pdf.py, extract_pdf_to_md.py
│   │
│   ├── memory-extractor/       # Session transcript → implicit memory files
│   │   ├── SKILL.md
│   │   └── scripts/            # extract.py
│   │
│   ├── skill-creator/          # Create, test, eval, and optimize skills
│   │   ├── SKILL.md
│   │   ├── scripts/            # run_eval.py, run_loop.py, aggregate_benchmark.py
│   │   ├── agents/             # grader.md, comparator.md, analyzer.md
│   │   └── references/         # bdd_spec_template.md, schemas.md
│   │
│   ├── prompt-health-refactor/ # HITL: fix failing prompts from monitor reports
│   │   ├── SKILL.md
│   │   └── references/         # step_map.json (skill/step → source file registry)
│   │
│   ├── self-correction/        # Auto-diagnose and recover from skill failures
│   │   └── SKILL.md
│   │
│   └── idea-backlog/           # Centralised backlog: ADD/DUMP/NEXT/KANBAN/TRIAGE
│       ├── SKILL.md
│       ├── scripts/            # recommend.py, kanban_server.py, autonomous_picker.py
│       └── references/         # config.md, usage_log.jsonl
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

Skills with Python scripts are runnable standalone or chained together:

```bash
# Full PM pipeline — problem description → user stories in one command
python3 skills/pm-workflow/scripts/prd_drafter.py \
    "Analysts export data to Excel manually every morning." | \
    python3 skills/pm-workflow/scripts/story_generator.py
```

See `skills/_template/scripts/example_skill.py` for the canonical starting point,
and `skills/pm-workflow/scripts/` for a production example using `lib/claude_utils.py`.

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

## 🔄 Feedback loops

Skills are one-directional by default — you trigger them, they produce output.
The next level is closing the loop so the system compounds without prompting.

The full system runs **12 reinforcing loops across 4 families** — Pipeline
Governance, Knowledge Flywheel, Personal Alignment, Operational Resilience —
each an instance of one reusable six-stage pattern:

```
INSTRUMENT → STORE → ANALYSE → SURFACE → ACTUATE → RATCHET
```

The ratchet stage is what separates *self-improving* from merely *self-healing*:
self-healing systems fix the same fault forever; a ratchet (enforcement tests,
weight tables, error memory) makes each fix permanent, so effort compounds.

**[→ docs/FEEDBACK_LOOPS.md](./docs/FEEDBACK_LOOPS.md)** — the full visual map:
Mermaid diagrams for every loop family, the 12-loop index (auto vs HITL), and
the six-stage architecture template for building your own self-improving systems.

See [EXTENDING.md](./EXTENDING.md) for implementation details on the three
knowledge loops.

---

## Self-governing AI operations monitor

Every Claude call made by a skill is logged, classified by root cause, and surfaced in a weekly report — with a human approval gate before any fix ships.

```
Instrument → Analyse → Queue → HITL Review → Enforce → Reset → repeat
```

**Four failure classes detected automatically:**

| Type | What it means | Fix |
|---|---|---|
| Hard failure | Sporadic prompt/critique quality issue | Fix prompt or critique |
| JSON failure | Model returned plain text instead of JSON | Add fallback rule to prompt |
| Critique strict | Valid output rejected by over-strict critique | Recalibrate thresholds |
| Low variance | Same output every run — rule would suffice | Replace with deterministic logic |

**Plus static analysis** — a pre-commit gate blocks any call site where the response variable is assigned but never used downstream.

The monitor also runs as a live HTTP dashboard (`monitor_server.py`) with sub-typed badges per failure class. See [`monitor/README.md`](./monitor/README.md) for the full architecture.

This is the answer to "how do you govern AI in production?" — not a policy document, but a running system with time-stamped evidence.

---

## Design principles aligned with EU AI Act & DORA

This is a personal project, not a regulated system. Neither rule actually applies here,
and for a precise reason, not just "it's personal": the AI Act's high-risk recruitment
category (Annex III, 4(a)) covers systems an *employer* uses to screen candidates — not a
candidate's own tooling used on themselves. DORA binds *regulated financial entities* and
their critical ICT vendors, not an individual's personal automation. Neither rule's actor
model fits what this is.

What it does share with both is the underlying engineering problem. The tables below map
what this repo actually does to the regulatory idea it mirrors — not a compliance claim,
just the same discipline applied voluntarily.

### EU AI Act — risk isn't a one-time check, it's managed continuously

The Act's core idea, for the systems it does cover: risk management is a lifecycle, not
a launch-day checklist — identify it, reduce it, test it, and repeat every time the system
changes. And the tighter the potential for harm, the tighter the controls, applied
unevenly on purpose. This repo works the same way — low-stakes steps degrade quietly;
anything that changes real state or could mislead someone waits for a person and gets
logged.

| Rule | What it asks for | What's actually built |
|---|---|---|
| Art. 9 — Risk management | An ongoing cycle, not a one-time sign-off: find risks, fix them, test, repeat as the system evolves | Every new capability goes through the same loop — build the safeguard, write a test that proves it works, ship it, watch it in production, adjust. Nothing is "done" once and left alone |
| Art. 14 — Human oversight | A person can review and stop things before they happen | Nothing fires on its own. Every action that changes something (an approval, a memory write) waits for a person to say yes first |
| Art. 12 — Record-keeping | Keep a trail of what the system did | Every AI call is logged — what it was, how long it took, which model answered, whether it passed. One live document lists every call site in the whole system, and it updates itself |
| Art. 13 — Transparency | You can see why the system did what it did | Which model answered, and whether it worked, gets logged every single time. Nothing happens in a black box |
| Art. 10 — Data governance | Protect personal data before using it | Personal data gets stripped out before any AI model sees it — not after, before. That step runs on plain code, no AI involved, so it's predictable and testable |
| Art. 15 — Accuracy & robustness | Don't produce made-up information | Anything that could invent facts (like resume content) is only allowed to reuse real material from a source document. If it can't back something up, it has to say so instead of guessing |

### DORA — assume something will break, build to notice and recover fast

DORA's core idea isn't "prevent every failure" — it's treating ICT failure as certain,
not hypothetical, and designing for fast detection, containment, and recovery, with the
same seriousness a bank gives liquidity risk rather than treating it as an IT afterthought.
Same stance here, across its main pillars.

| Area | What's actually built |
|---|---|
| ICT risk management — don't depend on one vendor | If the main AI provider goes down, it switches to a backup automatically — one setting change, no rewrite |
| Incident classification — catch problems early | Every failure gets sorted into a category automatically (bad output, wrong format, etc.) and reviewed on a regular schedule — not discovered by accident |
| Resilience testing — prove it actually works | Nothing new ships without a test that proves it fixes the specific problem it's meant to fix |
| Third-party ICT risk — don't get locked in | Swapping the AI model underneath is a config change, not a rewrite |

### Why this matters, plainly

The point isn't "is this compliant" — neither rule actually reaches a personal project.
The point is that the things regulators worry about — an AI system nobody can stop, one
that makes things up, one with no record of its own decisions, one that depends on a
single vendor with no way out — are also just bad engineering, in any context. Fixing
them because the regulation asks for it, and fixing them because it's the right way to
build a system, turned out to be the same job.

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

**New to the repo?** [`PLAYBOOK.md`](./PLAYBOOK.md) is the sequenced setup guide —
four phases with milestones and "done when" gates, from individual scaffold to
enterprise deployment. Start there if you want to be told what order to do things in.

**Already building?** See [`EXTENDING.md`](./EXTENDING.md) for the path from scaffold
to production — how each skill grows, when to split monolithic skills into composable
micro-skills, which MCP integrations unlock the most, and what not to build.

---

## Philosophy

Skills are cheap to build and infinitely reusable. Memory accumulates without effort.
Config is version-controlled and portable. The result is a setup where each session
compounds the ones before it — context grows, quality improves, and the gap between
"I need X" and "X is done" keeps shrinking.

That's the difference between using AI and operating it.
