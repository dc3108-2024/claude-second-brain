---
name: apple-calendar
description: >
  Create an event in Apple Calendar from natural language. Triggers on: "add to
  calendar", "schedule", "put in my calendar", "create event", "add event", or
  any prompt with a what and a when — e.g. "dentist Friday 10am", "team call
  tomorrow 3pm for 30 mins", "block Tuesday afternoon".
---

# Apple Calendar Skill

Create Apple Calendar events from natural language — no form-filling, no app switching.
Syncs to iPhone automatically via iCloud.

## Requirements

**Mac only.** Uses `osascript` to write directly to Calendar.app. No API keys or MCP
server required — just Python stdlib and a running Calendar.app.

## Setup

1. Run `osascript -e 'tell application "Calendar" to get name of every calendar'`
   to see your calendar names
2. Edit the **Calendar names** section below to match your setup
3. Update the `--calendar` default in `scripts/create_event.py` if needed

---

## Step 1 — Extract the fields

From the user's prompt, extract:

| Field | Default if not stated |
|---|---|
| **Title** | Required — ask if missing |
| **Date** | Required — ask if ambiguous |
| **Start time** | Required — ask if missing |
| **Duration** | 60 minutes |
| **Calendar** | Your default calendar name (see Setup) |
| **Notes** | _(none)_ |

Resolve relative dates against today's date from the system context.
"Tomorrow", "Friday", "next week Monday" are all valid inputs.

If date or time cannot be resolved unambiguously, ask one clarifying question before proceeding.

---

## Step 2 — Confirm before creating

Show a one-line summary:

```
📅 "[Title]" — [Day, Date] [Start time] – [End time] → [Calendar]
```

Then create immediately — do not ask "shall I proceed?"

---

## Step 3 — Create the event

Run `scripts/create_event.py` via Bash, passing all fields as arguments:

```bash
python3 ~/.claude/skills/apple-calendar/scripts/create_event.py \
  --title "TITLE" \
  --date "YYYY-MM-DD" \
  --start "HH:MM" \
  --duration MINUTES \
  --calendar "CALENDAR_NAME" \
  --notes "NOTES"
```

---

## Step 4 — Confirm

On success, confirm with the same one-line summary.
On failure, show the error and suggest the user check that Calendar.app is running and accessible.

---

## Calendar names

Replace these with the output of the setup command above. Common patterns:

| Calendar | Use for |
|---|---|
| `Calendar` | Personal / default (Apple's built-in name) |
| `Work` | Work meetings, deadlines |
| `Home` | Household, appointments |

Tip: if the event context implies work (meeting, call, deadline, client), route to your
work calendar. Otherwise use your personal default.
