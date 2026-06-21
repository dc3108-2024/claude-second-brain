---
name: jira-pm
description: >
  AI PM lifecycle orchestrator — wraps the build pipeline with JIRA epics,
  Confluence PRDs, user stories, and Slack status updates.
  Trigger on: "start PM cycle for [feature]", "new feature: [description]",
  "close JIRA story [KEY-N]", "build KEY-N", or automatically from finishing-a-branch
  when the branch name contains a JIRA key pattern like KEY-3.
---

# jira-pm Skill

Three modes: **OPEN** (sound bytes → PRD → JIRA epic + stories), **BUILD** (story → In Progress + plan), and **CLOSE** (story Done + PR linked + Confluence updated). A **BRIDGE** auto-triggers CLOSE when finishing-a-branch detects a JIRA key in the branch name.

---

## Mode detection

| Trigger | Mode |
|---|---|
| "start PM cycle for X" / "new feature: X" | OPEN |
| "build KEY-N" / "start KEY-N" / "build [KEY-N]" | BUILD |
| "close JIRA story KEY-N" / "close KEY-N, PR: URL" | CLOSE |
| Branch name matches `[A-Z]+-\d+` after finishing-a-branch | BRIDGE → CLOSE |

---

## OPEN Flow

### Step 1 — Draft PRD

Run:
```bash
python3 ~/.claude/skills/jira-pm/scripts/prd_drafter.py "<sound bytes>"
```

Capture the JSON output. Display to user as a formatted summary:
- **Feature:** `feature_name`
- **Problem:** `problem`
- **Features:** bullet list
- **Success metrics:** bullet list
- **Out of scope:** bullet list

### Step 2 — Dry-run guard check (before Confluence page)

```bash
SKILL_ENV=${SKILL_ENV:-live} python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/skills/jira-pm/scripts')
from dry_run_guard import check_policy, DryRunBlockedError
try:
    check_policy('mcp__mcp-atlassian__create_page')
    print('OK')
except DryRunBlockedError as e:
    print(f'DRY_RUN_BLOCKED:{e}')
"
```

If output starts with `DRY_RUN_BLOCKED:`, print `[DRY RUN] Would create Confluence page for: <feature_name>` and skip Steps 3–9. Summarise what would have happened and stop.

### Step 3 — Create Confluence page

Read `references/confluence_spaces.md`. Based on the feature name and problem statement from the PRD draft, select the space whose domain best matches. Use the Root page ID from that registry as the parent so the PRD nests correctly under the space home. If no space is a clear fit, ask the user before proceeding.

- Tool: `mcp__mcp-atlassian__confluence_create_page`
- Space key: chosen from registry
- Parent page ID: Root page ID from registry for the chosen space
- Title: `PRD — <feature_name>`
- Body: Format PRD as Confluence wiki page with H2 headings: Problem, Personas, Features, Success Metrics, Out of Scope

Save the returned page URL as `confluence_url`.

### Step 3.5 — Infrastructure Classification (conditional)

Run (pass PRD JSON via stdin):
```bash
echo '<prd_json_as_single_line>' | python3 ~/.claude/skills/jira-pm/scripts/infra_classifier.py
```

**If `is_infra_heavy` is false:** Exit Step 3.5 immediately. Show nothing. Continue to Step 4.

**If `is_infra_heavy` is true:** Hold the signal list and rationale. Embed them in the Step 4 HITL 1 prompt as an additional confirmation question:

```
Infrastructure signals detected: <comma-separated signal list>
    Reason: <rationale>
    Generate a technical architecture document? (yes / no — default yes)
```

**Signal categories:**
| Category | Examples |
|---|---|
| `background_process` | watchdog daemon, polling loop, always-on script |
| `external_tool` | CLI tools, ffmpeg, third-party utilities |
| `data_pipeline` | multi-step transformation chain, 3+ distinct processing stages |
| `system_integration` | launchd plist, cron entry, Slack bot command handler |
| `new_skill_script` | new `.py` added to skills directory |
| `config_manifest` | new JSON/YAML config, `.plist`, manifest file |

### Step 3.6 — Architecture Document Generation (conditional)

**Fires only if** `is_infra_heavy` is true AND user confirmed `generate_arch_doc: yes`.

Run (pass PRD JSON + signals via stdin):
```bash
echo '{"prd": <prd_json>, "signals": <signals_list>}' | python3 ~/.claude/skills/jira-pm/scripts/arch_doc_generator.py
```

Create a Confluence child page under the PRD page:
- Title: `Architecture — <feature_name>`
- Body: formatted markdown from `format_as_markdown(feature_name, sections)`

Save the returned page URL as `arch_doc_url`.

### Step 4 — HITL 1: Approve PRD

Display:
```
PRD created: <confluence_url>
[If arch_doc_url is set]: Architecture doc: <arch_doc_url>

Ready to create JIRA epic?
  Epic summary: <feature_name>
  Linked PRD: <confluence_url>

Reply "yes" to create epic, or "edit" to revise the PRD first.
```

Wait for user input. If "edit": return to Step 1 with revised sound bytes. If "yes": continue.

**Comment capture:** After the user responds, extract any observations or notes in their message. Post them as a Confluence comment on the PRD page using `mcp__mcp-atlassian__confluence_add_comment`, prefixed with `[HITL review — <YYYY-MM-DD>]`.

### Step 5 — Create JIRA Epic

Dry-run guard check: tool `mcp__mcp-atlassian__jira_create_issue`.

- Tool: `mcp__mcp-atlassian__jira_create_issue`
- Project key: use project key from confluence_spaces.md or ask user
- Issue type: Epic
- Summary: `<feature_name>`
- Labels: `ai-pm-showcase`
- Description: compact feature summary (name, personas, capabilities) — NOT the full PRD

Save returned issue key as `epic_key` (e.g. `YOUR_PROJECT-1`).

### Step 6 — Generate user stories

Run (pass PRD JSON via stdin):
```bash
echo '<prd_json_as_single_line>' | python3 ~/.claude/skills/jira-pm/scripts/story_generator.py
```

Display stories as a numbered list with acceptance criteria.

### Step 7 — HITL 2: Approve stories

Display:
```
Stories ready for epic <epic_key>:

1. <story 1 summary>
   AC:
   - <criterion 1>
   - <criterion 2>

Reply "yes" to create stories in JIRA, or "edit N" to revise story N.
```

**Comment capture:** After the user responds, post any per-story observations as JIRA comments using `mcp__mcp-atlassian__jira_add_comment`, prefixed with `[HITL review — <YYYY-MM-DD>]`.

### Step 8 — Create JIRA stories

For each story, create a JIRA issue:
- Tool: `mcp__mcp-atlassian__jira_create_issue`
- Issue type: Story
- Summary: `<story.summary>`
- Description: `<story.description>` (pre-formatted by story_generator.py)
- Parent: `<epic_key>`

Then create dependency links for every `depends_on` entry:
- Tool: `mcp__mcp-atlassian__jira_create_issue_link`
- link_type: `Blocks`

### Step 9 — Slack notification + build order

```bash
echo "<epic_key> — <feature_name> created, <N> stories ready" | python3 ~/.claude/skills/shared/post_to_slack.py
```

Compute and display a dependency-aware build order, grouping stories into waves:
```
Build order for <epic_key>:
  Wave 1 (build in parallel): <KEY-N>, <KEY-M>
  Wave 2 (after Wave 1):      <KEY-P>
```

### Step 10 — Brainstorm (conditional)

Invoke `superpowers:brainstorming` only if:
- The epic has 3 or more stories, OR
- Any story has a non-empty `depends_on` list

---

## BUILD Flow

### Step 1 — Parse story key

Extract `story_key` from trigger (e.g. `build YOUR_PROJECT-2`). If not found, ask.

### Step 2 — Transition to In Progress

Check `references/jira_transitions.json` for the project key "In Progress" ID.
If non-null, use it directly — skip `jira_get_transitions`.
If null, call `mcp__mcp-atlassian__jira_get_transitions`, then update the cache file.

### Step 3 — Load story context

- Tool: `mcp__mcp-atlassian__jira_get_issue`
- Fetch summary, description (acceptance criteria), and comments.

Extract filtered JIRA comments (>30 chars, not just "yes"/"approved"/"lgtm") — these represent scope refinements made after story creation.

### Step 4 — Create feature branch name

Print:
```
Branch: feature/<story_key>-<slug>
```

### Step 5 — Invoke writing-plans

Invoke `superpowers:writing-plans` with:
- Story summary
- Acceptance criteria
- Filtered JIRA comments (as "scope refinements and decisions")

---

## CLOSE Flow

### Step 1 — Parse inputs

Extract from trigger:
- `story_key` — e.g. `YOUR_PROJECT-3`
- `pr_url` — e.g. `https://github.com/your-username/your-repo/pull/42`

### Step 2 — Update JIRA story → Done

Check `references/jira_transitions.json` for "Done" ID. Use it or discover and cache it.

### Step 3 — Link PR to story

- Tool: `mcp__mcp-atlassian__jira_update_issue`
- Add remote link: `{"url": "<pr_url>", "title": "Pull Request"}`

### Step 4 — Update Confluence PRD

Find the Confluence PRD page linked in the parent epic. Append:
```
## Shipped — <YYYY-MM-DD>
Story: <story_key>
PR: <pr_url>
```

### Step 5 — Slack notification

```bash
echo "<story_key> — shipped. PR: <pr_url>" | python3 ~/.claude/skills/shared/post_to_slack.py
```

---

## BRIDGE — Auto-trigger from finishing-a-branch

When `superpowers:finishing-a-development-branch` completes, check the current branch:

```bash
git branch --show-current
```

If branch name contains a JIRA key pattern (`[A-Z]+-\d+`), extract the key and prompt:

```
JIRA key KEY-N detected in branch name. Close this story?
Enter the merged PR URL (or press Enter to skip):
```

On URL provided: run CLOSE flow. On Enter/skip: do nothing.

---

## Branch naming convention

```
feature/<KEY>-<slug>
```
Example: `feature/YOUR_PROJECT-3-drive-output-routing`

---

<!-- MONITOR_BLOCK -->
## Monitoring

All Claude calls route through `call_claude_with_critique()` and are logged automatically.
Steps registered in `references/step_map.json`:
- `jira-pm/prd.draft` → `prd_drafter.py`
- `jira-pm/stories.generate` → `story_generator.py`
- `jira-pm/infra.classify` → `infra_classifier.py`
- `jira-pm/arch.generate` → `arch_doc_generator.py`

MCP writes (JIRA/Confluence) are protected by `dry_run_guard.py`. Set `SKILL_ENV=dry_run` to block all writes during testing.
