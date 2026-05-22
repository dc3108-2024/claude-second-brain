---
name: apple-reminders
description: >
  Add a reminder to the Apple Reminders app from natural language. Syncs to iPhone
  automatically via iCloud. Triggers on: "add a reminder", "remind me to", "add to
  reminders", "set a reminder", or any prompt with a task and optional when —
  e.g. "remind me to call John tomorrow", "add a reminder to review the deck Friday 9am",
  "remind me to pay rent on the 1st".
---

# Apple Reminders Skill

Add reminders to the Mac/iPhone Reminders app from natural language. Syncs via iCloud instantly.

## Requirements

**Mac only.** Uses `osascript` to write directly to Reminders.app. No API keys or MCP
server required — just Python stdlib and a running Reminders.app.

## Setup

1. Run `osascript -e 'tell application "Reminders" to get name of every list'`
   to see your list names
2. Edit the **Lists** section below to match your setup
3. Update the `--list` default in `scripts/create_reminder.py` to your preferred default list

---

## Step 1 — Extract the fields

| Field | Default if not stated |
|---|---|
| **Title** | Required — ask if missing |
| **Due date** | Optional — reminder with no date is valid |
| **Due time** | Optional — if date given with no time, sets a date-only reminder |
| **List** | Your default list name (see Setup) |
| **Notes** | _(none)_ |

Resolve relative dates against today's date from system context.

---

## Step 2 — Confirm before creating

One-line summary:

```
🔔 "[Title]" — [Date + Time if set] → [List]
```

Then create immediately.

---

## Step 3 — Create the reminder

Run `scripts/create_reminder.py` via Bash:

```bash
python3 ~/.claude/skills/apple-reminders/scripts/create_reminder.py \
  --title "TITLE" \
  [--date "YYYY-MM-DD"] \
  [--time "HH:MM"] \
  [--list "LIST_NAME"] \
  [--notes "NOTES"]
```

Date and time are both optional. If neither is given, the reminder is created with no due date.

---

## Step 4 — Confirm

On success, confirm with the one-line summary.
On failure, show the error and suggest the user check that Reminders.app is running.

---

## Lists

Replace these with the output of the setup command above. Example structure:

| List | Use for |
|---|---|
| `Reminders` | General tasks and errands (Apple's default list name) |
| `Work` | Work tasks and follow-ups |
| `Shopping` | Errands and purchases |

Add as many lists as you use in Reminders.app — the skill routes to whichever you name.
