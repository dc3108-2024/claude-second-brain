# [Skill Name] — Behaviour Spec

> Store this as `specs/[skill-slug].md` in the skill folder before writing any code.
> This is the source of truth. If docs and code diverge, update this first.

## Purpose
One sentence: what does this skill enable Claude to do?

## Trigger Phrases
- "..."
- "..."

## Scenarios

### Scenario 1: Happy Path
```gherkin
Given [the starting state — what inputs/context exist]
When  [the trigger phrase or event]
Then  [the expected output or side effect]
 And  [secondary assertions if any]
```

### Scenario 2: Missing Input
```gherkin
Given [required input is absent]
When  [trigger]
Then  [graceful failure message or prompt for input]
```

### Scenario 3: External Tool Call
```gherkin
Given [context is populated with [[PLACEHOLDER]] values — e.g., [[TEMP_FILE_PATH]], [[SLACK_CHANNEL]]]
When  [skill executes an external tool call]
Then  [resolve_context() has replaced all [[PLACEHOLDERS]] before execution]
 And  [check_policy() has confirmed tool is allowed in current SKILL_ENV]
```

**Implementation note:** In the skill's execution function, call these before any external tool:
```python
from context_hygiene import resolve_context
from policy_gate import check_policy, PolicyViolation
message = resolve_context(message_template, override_state=state)
check_policy("post_to_slack")  # raises PolicyViolation if blocked in current SKILL_ENV
```
Both are importable from `~/.claude/skills/shared/` — see `lib_claude.py`.

### Scenario 4: [Add edge case specific to your skill]
```gherkin
Given [...]
When  [...]
Then  [...]
```

## Output Contract
- Format: [PDF | Slack message | Apple Note | terminal text | file]
- Location: [path or channel]
- On success: [what the user sees]
- On failure: [what the user sees]

## External Tools Used
List every MCP tool, script, or API this skill calls — used to populate policies.yaml.
- `post_to_slack.py`
- `mcp__apple-notes__create-note`
- ...

## Policy Entries Required
```yaml
# Add to ~/.claude/skills/shared/policies.yaml under dry_run.blocked_tools if appropriate
- [tool-name]
```
