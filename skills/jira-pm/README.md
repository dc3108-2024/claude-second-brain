# jira-pm

AI-assisted PM lifecycle skill. Takes a feature description from sound bytes to shipped story, with Confluence PRDs, JIRA epics, user stories, and Slack notifications wired in.

The skill manages three modes: opening new features, driving active builds, and closing shipped stories. A bridge mode auto-triggers close when it detects a JIRA key in a git branch name.

---

## How it works

```
  OPEN  ─── "new feature: X"
    sound bytes → prd_drafter.py → Confluence PRD
                                        │
                                 HITL approval
                                        │
                                  JIRA epic → stories

  BUILD ─── "build KEY-N"
    JIRA story → In Progress → writing-plans → code

  CLOSE ─── "close KEY-N, PR: <url>"
    story → Done → PR linked → Confluence updated → Slack

  BRIDGE ─── auto on branch merge
    branch name contains KEY-N → prompts CLOSE
```

---

## Trigger phrases

| Phrase | Mode |
|---|---|
| `"new feature: X"` or `"start PM cycle for X"` | OPEN |
| `"build KEY-N"` or `"start KEY-N"` | BUILD |
| `"close KEY-N, PR: <url>"` | CLOSE |
| Branch merge with KEY pattern | BRIDGE |

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Full workflow for all three modes |
| `scripts/prd_drafter.py` | Claude: sound bytes → structured PRD JSON |
| `scripts/story_generator.py` | Claude: PRD JSON → user stories with AC |
| `scripts/infra_classifier.py` | Claude: detect infrastructure signals in a PRD |
| `scripts/arch_doc_generator.py` | Claude: generate architecture doc for infra-heavy features |
| `scripts/dry_run_guard.py` | Block MCP writes in test mode (`SKILL_ENV=dry_run`) |
| `references/confluence_spaces.md` | Registry of Confluence spaces + root page IDs |
| `references/jira_transitions.json` | Cached transition IDs per project (auto-populated) |
| `references/prd_template.md` | Field definitions used in the PRD drafting prompt |

---

## Setup

1. **Install mcp-atlassian** and configure Atlassian credentials
2. **Fill in `references/confluence_spaces.md`** with your actual space keys and page IDs
3. **Fill in `references/jira_transitions.json`** with your project keys (IDs auto-populate on first run)
4. **Configure Slack** via `~/.claude/skills/shared/slack_config.json`

### Dry-run mode

Set `SKILL_ENV=dry_run` to block all JIRA and Confluence writes. Useful for testing the PRD and story generation steps without creating anything.

```bash
SKILL_ENV=dry_run claude "new feature: user authentication"
```

---

## HITL approval points

The skill has two mandatory human gates:

1. **After PRD drafting** — review before creating the Confluence page and JIRA epic
2. **After story generation** — review before creating JIRA stories

Both gates capture your inline notes and post them as comments on the relevant JIRA/Confluence artefact.

---

## Infrastructure detection

When a feature is infra-heavy (daemon, CLI dependency, data pipeline, system integration), the skill detects it automatically and offers to generate an Architecture document as a child of the PRD page. This also adds an architecture story to the backlog with acceptance criteria derived from the signal type.
