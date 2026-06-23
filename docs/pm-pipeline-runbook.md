# PM Pipeline — Operating Guide

This is the actual runbook for the agentic PM pipeline built on this scaffold. It documents
the full lifecycle from voice note to shipped story — including the non-obvious nuances that
are easy to miss when the pipeline is working and painful to debug when it isn't.

It covers three flows: **OPEN** (create), **BUILD** (implement), and **CLOSE** (ship).

---

## Full Lifecycle at a Glance

```
Voice note / "start PM cycle for X"
              ↓
          OPEN flow
   PRD → Epic → Stories/Tasks
              ↓
         BUILD flow
   Story → In Progress → Implementation plan
              ↓
         CLOSE flow
   Done → PR linked → PRD updated → Slack
```

---

## Two Execution Paths

Every feature enters through one of two paths. The path determines the number of approval
gates, the issue types created, and the richness of the output.

| | **Automated Path** | **Interactive Path** |
|---|---|---|
| **Trigger** | Voice note → approval via Slack | `start PM cycle for X` in Claude Code |
| **HITL gates** | 1 — sound bytes + routing review | 2 — PRD review, then stories review |
| **PRD creation** | Auto (same run as epic + tasks) | Step-by-step in Claude Code |
| **Issue type** | Task (all projects) | Story (all projects, see exception below) |
| **AC quality** | Derived from PRD features list — lean | `story_generator.py` — full ACs, dependency links, build waves |
| **Dependency links** | Not generated | Generated (Blocks / is blocked by) |
| **Build wave plan** | Not generated | Generated (Wave 1 / Wave 2 etc.) |
| **Slack on completion** | Posts epic key + task list | Posts same |

---

## Issue Type by Project

Most projects use Stories. Task-based projects are the exception, not the rule.

| Project type | Issue type | Why |
|---|---|---|
| Projects configured for simple tracking | **Task** | Matches lightweight workflow — no dependency modelling needed |
| All other projects | **Story** | Full ACs, dependency links, build wave ordering via `story_generator.py` |

> **Note:** The automated pipeline currently hardcodes Task for all projects. If a non-Task project
> is triggered via voice note, it will create Tasks instead of Stories — missing full ACs and
> dependency links. See Known Gaps.

---

## OPEN Flow — Create Epic + Stories/Tasks

### Automated Path

```
1. Voice note recorded on mobile → AirDropped to Mac (or dropped into watched folder)
2. Audio bridge detects file → Whisper transcribes locally
3. Transcript uploaded to cloud storage
4. Claude distils transcript → extracts sound bytes + suggested routing
5. Smart router classifies domain → project key + confidence
6. Slack approval request posted: sound bytes + routing + transcript link
   ↳ Reply "yes" to approve, "no" or "skip" to discard
7. On approval → prd_drafter.py generates PRD JSON
8. jira_pm_trigger.py fires → claude -p runs headlessly:
   a. Confluence PRD page created
   b. JIRA Epic created (linked to PRD)
   c. JIRA Tasks created (one per feature in PRD)
9. Slack completion notification: 🎫 [EPIC-KEY] — [feature]. Tasks: [keys]. PRD: [url]
```

**The Slack notification at step 9 is a completion notice, not a CTA.** Everything is
already live by the time it arrives. There is no second gate in the automated path.

### Interactive Path

```
1. "start PM cycle for X" in Claude Code
2. prd_drafter.py generates PRD JSON → displayed as formatted summary
3. HITL 1: "PRD created: [url]. Ready to create JIRA epic? Reply yes / edit."
   ↳ Approve to continue, or "edit" to revise
4. JIRA Epic created
5. story_generator.py generates stories with full ACs + dependency links
6. HITL 2: Stories displayed with build wave plan. "Reply yes to create in JIRA."
   ↳ Approve to continue, or "edit N" to revise a specific story
7. JIRA Stories created with Blocks/is-blocked-by links
8. Slack notification posted
9. Build wave order printed — shows which stories to build first
```

### HITL Gates — What Each One Controls

| Gate | Path | What you're approving |
|---|---|---|
| **Sound bytes review** (Slack) | Automated only | Distilled requirements + domain routing. Approving triggers the full run — PRD + Epic + Tasks in one shot |
| **PRD review** (Claude Code) | Interactive only | Confluence PRD content. Approving creates the Epic only — stories come next |
| **Stories review** (Claude Code) | Interactive only | Individual stories + ACs. Approving creates all JIRA stories with dependency links |

---

## BUILD Flow — Start Working on a Story

### Trigger

```
build KEY-N
```

### What happens

```
1. Story/task transitions to In Progress in JIRA
2. Story summary + ACs fetched from JIRA
3. JIRA comments on the story fetched (HITL observations from story approval)
4. Feature branch name printed: feature/KEY-N-short-slug
5. writing-plans skill invoked — generates a step-by-step implementation plan
```

### Non-obvious nuances

**JIRA comments become part of the implementation spec.** Any observations or scope
refinements added during the stories HITL review are injected into the writing-plans spec.
This is how PM decisions made at story approval time flow forward into the build — without
anyone having to re-read the PRD. Comments shorter than 30 characters, or consisting of
approval phrases ("yes", "lgtm", "approved"), are filtered out. Only substantive notes pass through.

**The BUILD spec is the story ACs + JIRA comments — not the Confluence PRD.** The PRD is
the long-form archive. BUILD reads JIRA only. The story already contains the distilled spec.

**Branch naming matters.** Name your branch `feature/<KEY>-<slug>` (e.g.
`feature/FOS-3-drive-output-routing`). Deviate from this and the BRIDGE auto-close won't
fire when you finish the branch.

---

## CLOSE Flow — Mark a Story Done

### Trigger

```
close KEY-N, PR: https://github.com/your-org/your-repo/pull/42
```

### What happens

```
1. Story/task transitions to Done in JIRA
2. PR URL linked to the JIRA story
3. Confluence PRD page updated — "Shipped" section appended automatically:
   ## Shipped — YYYY-MM-DD
   Story: KEY-N
   PR: [url]
4. Slack notification posted: ✅ KEY-N — shipped. PR: [url]
```

### Non-obvious nuances

**The Confluence PRD is updated automatically.** You don't need to touch the PRD page.
The shipped date, story key, and PR link are appended — permanent record of when and
how each story was delivered.

**CLOSE requires a PR URL.** The story stays In Progress until explicitly closed. If you
don't have a PR yet, wait until you do.

---

## BRIDGE — Auto-Close from Branch Name

BRIDGE is not a separate command. It fires automatically when you run
`superpowers:finishing-a-development-branch`.

### How it works

```
1. finishing-a-branch runs
2. Checks current branch name for JIRA key pattern: [A-Z]+-\d+
   e.g. feature/FOS-3-drive-output-routing → extracts FOS-3
3. Prompts: "JIRA key FOS-3 detected. Close this story? Enter PR URL or press Enter to skip."
4. If URL provided → CLOSE flow runs automatically
5. If skipped → nothing happens
```

### Branch naming requirement

| Branch name | BRIDGE fires? |
|---|---|
| `feature/KEY-3-short-description` | Yes |
| `feature/short-description` | No — key missing |
| `KEY-3-short-description` | Yes — key present even without `feature/` prefix |

Name the branch correctly when BUILD prints the suggested name — that's the right moment.

---

## Quick Reference — Commands by Stage

| Stage | Command | What it does |
|---|---|---|
| Create | `start PM cycle for X` | OPEN flow — PRD + epic + stories |
| Build | `build KEY-N` | Transitions to In Progress, generates implementation plan |
| Close | `close KEY-N, PR: [url]` | Transitions to Done, links PR, updates PRD, Slack |
| Auto-close | `feature/KEY-N-slug` branch + finishing-a-branch | BRIDGE triggers CLOSE automatically |
| Sync PRD edits | `sync [EPIC-KEY] from PRD` | Reads current Confluence PRD, updates JIRA epic + tasks |
| Regenerate stories | `Regenerate stories for [EPIC-KEY]` | Runs story_generator.py over existing PRD |

---

## Routing Taxonomy

The smart router classifies voice note content to the correct project space. Classification
happens during distillation — by the time the Slack approval request appears, the routing
decision is already made.

| Domain | What belongs here |
|---|---|
| Infrastructure — harness, memory, skills, context engineering, autonomous runners | Anything touching shared AI OS infrastructure |
| Financial OS — portfolio tracking, planning tools, output pipelines | Financial tracking and planning features |
| Home / relocation logistics — packing, utilities, inventory | Move logistics and task tracking |
| PM tooling — jira-pm skill, lifecycle artefacts, pipeline improvements | Meta: improvements to the PM system itself |
| Job search — CV, applications, interview prep | Job search pipeline |

The router uses confidence scores. If confidence is below threshold, it flags for manual
routing rather than routing silently to the wrong project.

---

## Known Gaps

| Gap | Impact | Status |
|---|---|---|
| Automated path creates Tasks for all projects | Non-Task projects triggered via voice note get Tasks, missing full ACs and dependency links | Open — fix: jira_pm_trigger.py should respect per-project issue type config |
| No Confluence → JIRA sync | Manual edits to a PRD don't update the JIRA epic or tasks | Open — planned: `jira-pm SYNC` mode |
| No second HITL gate in automated path | Once sound bytes are approved, the full run executes with no PRD review step | Open — design decision: is a second gate desirable or does it defeat the automation? |
| Completion Slack notification routing | Posts to default webhook — may not land where you're looking | Workaround: check JIRA directly ~6 min after approving |
| infra.classify JSON failures | Infrastructure classification fails intermittently — breaks the infra signal detection step | Open |
