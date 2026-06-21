# The Factory Playbook

> The Model is the hype. The Harness is the practical foundation.

This playbook walks you from zero to a self-improving agentic system — and from
individual setup to enterprise deployment. Four phases. Each phase has a "done when"
test. Move to the next only when you pass it.

---

## The mental model

An agent is two things: an **LLM** and a **harness**.

The LLM is the engine. The harness is everything around it — the tooling, the memory,
the context it operates on, the feedback loops that make it improve over time.

Most attention goes to the LLM. Most leverage lives in the harness.

The 80/20 split is inverted from what people expect:

| Component | Leverage | Why |
|---|---|---|
| **Harness** | 80% | Systems that get better over time without blowing up budgets live here |
| **LLM** | 20% | Swap models freely — the harness abstracts it |

The factory model follows from this: build the harness first, then plug in domain
modules. Each new module is cheaper than the last because the shared infrastructure
already exists.

---

## Who this is for

| You are... | Start at |
|---|---|
| Individual — building a personal AI system that compounds | Phase 1 |
| Team lead — extending proven personal patterns to a team | Phase 1 (read fast) → Phase 4 |
| Enterprise architect — setting up shared harness for a department | Phase 3 → Phase 4 |

Read Phase 1–2 even if you're enterprise. The patterns are identical; only the scope changes.

---

## Phase 1 — Foundation

**Goal:** The structural bones of everything that follows. One place to change who
you are. One place to push configuration. Skills that can't accidentally be deleted.

### Milestones

- [ ] `CLAUDE.md` filled in with your context and installed at `~/.claude/CLAUDE.md`
- [ ] Memory system initialised — `memory/` folder with at least one entry
- [ ] First skill built using the template, wired to a trigger phrase
- [ ] Three hooks active: auto-push on Write/Edit, skill protection on Bash, config backup
- [ ] Skills and config committed to a private GitHub repo — restore is one command

### Done when

> Changing something about yourself — a goal, a file path, a preference — requires
> editing one file, not multiple skills.

### Resources

- [`CLAUDE.md.template`](./CLAUDE.md.template) — fill this in first; it is the harness identity layer
- [`settings.json.example`](./settings.json.example) — all three hook patterns, ready to copy
- [`skills/_template/`](./skills/_template/) — your first skill starting point
- [README.md → Getting started](./README.md#getting-started) — six steps, fifteen minutes

---

## Phase 2 — Domain Modules

**Goal:** 3–5 skills that automate real, repeated work. Each one uses the Blueprint
vs Data discipline — workflow in `SKILL.md`, personal data in `references/`. By the
end of this phase, new skills take hours, not days.

### Milestones

- [ ] All Claude calls go through `lib/claude_utils.py` — no raw subprocess calls
- [ ] Every skill has a `references/` folder — no personal data hardcoded in `SKILL.md`
- [ ] At least two skills compose: output of one feeds input of another
- [ ] Skill #3 takes measurably less time to build than Skill #1

### The discipline that matters here

**Blueprint vs Data** — the single most important pattern in this repo.

| Lives in `SKILL.md` | Lives in `references/` |
|---|---|
| Steps and decision logic | File paths and output folders |
| Quality rules and conditions | Personal lenses and analytical filters |
| Output format templates | Domain context and professional role |
| Trigger phrases | Financial scenarios, account details |

**The contamination test:** if editing a personal goal requires opening a skill file,
the skill is contaminated.

Before: four analytical lenses embedded across six different skills. Change one lens:
edit six files. After: one `references/lenses.md`. Six skills read from it. The lens
changes once, everywhere.

### Done when

> A new skill takes hours. The harness is providing real leverage — not from being
> clever, but because the shared structure already exists.

### Resources

- [`skills/lens-synthesis/`](./skills/lens-synthesis/) — canonical Blueprint vs Data example
- [`lib/README.md`](./lib/README.md) — `call_claude_with_critique()` and `parse_json_response()` usage
- [EXTENDING.md → PM Workflow](./EXTENDING.md#pm-workflow) — composable script pattern (JSON in, JSON out)
- [EXTENDING.md → Skill Architecture](./EXTENDING.md#skill-architecture) — when to split a skill

---

## Phase 3 — Feedback Loops

**Goal:** The system monitors itself, surfaces failures, and applies fixes through a
human approval gate. This is where "automation that runs" becomes "infrastructure
that improves."

### Milestones

- [ ] All Claude calls log results to `token_usage.jsonl` via `call_claude_with_critique()`
- [ ] Weekly `critique_analysis.py` run generates `prompt_health.md`
- [ ] At least one closed feedback loop active (see options below)
- [ ] One failure fixed via `prompt-health-refactor` and locked in — hasn't recurred

### The three loops to build (in order of effort)

| Loop | What it does | When to add it |
|---|---|---|
| **KB ← Briefs** | After each brief, extract 3 durable concepts and capture them to your KB automatically | When your skill library is producing weekly intelligence output |
| **Alignment ← Session** | After each session, scan for goal revisions and update your personal alignment filter | When you notice stale context affecting output quality |
| **Research bias ← KB** | Weekly script scans KB density; briefs and capture skills read it and fill the sparse areas | When dense areas keep getting denser and you're missing gaps |

### The ratchet

A self-healing system fixes the same fault forever. A self-improving system locks each
fix in so it cannot recur. The difference is one step: after approval, an enforcement
test is added. The loop only turns forward.

### Done when

> A step that was failing has been fixed once and hasn't failed since. The monitor
> caught it. The feedback loop surfaced it. The fix was locked in permanently.

### Resources

- [`docs/FEEDBACK_LOOPS.md`](./docs/FEEDBACK_LOOPS.md) — 12-loop visual map, the six-stage pattern, Mermaid diagrams
- [EXTENDING.md → Feedback Loops](./EXTENDING.md#feedback-loops) — the three loops with implementation detail
- [EXTENDING.md → Self-Improving Loop](./EXTENDING.md#self-improving-loop) — monitor + HITL architecture
- [`skills/prompt-health-refactor/`](./skills/prompt-health-refactor/) — HITL fix workflow

---

## Phase 4 — Enterprise / Team Scale

**Goal:** Extract the harness from personal context and make it team-deployable.
The shared harness becomes a production asset; every person who runs a workflow owns
their slice of it.

### What changes at team scale

At the individual level, `references/` holds your personal data. At team scale, each
person or team maintains their own `references/` while sharing the same `SKILL.md`
workflows. The harness splits into two layers:

| Layer | Owned by | Contains |
|---|---|---|
| **Shared infrastructure** | Platform / engineering | `lib/`, monitoring, Slack interface, hooks, model config |
| **Shared workflows** | Domain leads | `SKILL.md` files — generic, portable, no personal data |
| **Per-person data** | Each user | Their own `references/` — goals, lenses, config, role context |

### Milestones

- [ ] Every `SKILL.md` is fully generic — usable by any team member with their own `references/`
- [ ] Shared HITL layer: one Slack interface for approvals across the team
- [ ] All AI calls are logged and traceable to a named skill and step
- [ ] A non-engineer has updated their own `references/` without touching a workflow file
- [ ] Governance baseline: `prompt_health.md` covers the full team's pipeline, not just one person's

### The enterprise unlock

The firms that see positive ROI from agentic AI are not the ones who bought the best
models. They are the ones who trained their entire workforce — not just engineers — to
understand and own the harness. PM, analyst, compliance, operations: everyone who runs
a workflow should own their slice.

> **The governance test:** if a business rule changes and only an engineer can update
> it, the harness is still contaminated. The target is a compliance officer updating
> `references/rules.md` without involving a data scientist.

### The audit property

When a regulator asks "what rule did your AI apply to deny this application?" — you
need to point to a versioned, auditable `references/` file, not explain what the LLM
was probably doing. Blueprint vs Data is not just a maintenance pattern. It is how you
make AI decisions explainable by design.

### Resources

- [`skills/audio-interview-bridge/`](./skills/audio-interview-bridge/) — team-scale intake: voice → JIRA, with routing config per project
- [`skills/jira-pm/`](./skills/jira-pm/) — shared PM lifecycle; routing table in `references/` is the team config
- [`docs/FEEDBACK_LOOPS.md`](./docs/FEEDBACK_LOOPS.md) — Pipeline Governance family: the loops that produce audit evidence
- [EXTENDING.md → MCP Integrations](./EXTENDING.md#mcp-integrations) — the integrations that connect the harness to systems teams already run

---

## Maturity at a glance

| Phase | Signal you've reached it |
|---|---|
| **Foundation** | One file change, one place |
| **Domain Modules** | New skills take hours, not days |
| **Feedback Loops** | A failure was fixed once and has never recurred |
| **Enterprise** | A non-engineer updated the harness without help |

---

## What not to skip

**Phase 1 → 2:** Don't skip the Blueprint vs Data discipline on your first skill. It
feels like overhead early. By Skill #5 you'll see why it isn't.

**Phase 2 → 3:** Don't skip the monitor. Silent failures are worse than obvious
failures. Wrapping Claude calls with `call_claude_with_critique()` is one import
change per script.

**Phase 3 → 4:** Don't skip the governance step. A logging system that produces
time-stamped evidence is the difference between "our AI is good" and "our AI is
auditable." Regulators and clients will ask.

---

*The factory's output is new applications and workflows — each one cheaper and faster
than the last. The playbook gets you to the factory floor. [EXTENDING.md](./EXTENDING.md)
covers what you build there.*
