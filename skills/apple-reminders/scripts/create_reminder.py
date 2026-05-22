"""
Add a reminder to Apple Reminders via osascript. Syncs to iPhone via iCloud.
Usage: python3 create_reminder.py --title "..." [--date YYYY-MM-DD] [--time HH:MM]
                                   [--list "..."] [--notes "..."]
"""
import argparse, subprocess, sys
from datetime import datetime

def create_reminder(title, date_str, time_str, list_name, notes):
    has_due = date_str is not None

    if has_due:
        time_part = time_str if time_str else "00:00"
        due_dt = datetime.strptime(f"{date_str} {time_part}", "%Y-%m-%d %H:%M")
        due_block = f"""
        set dueDate to current date
        set year of dueDate to {due_dt.year}
        set month of dueDate to {due_dt.month}
        set day of dueDate to {due_dt.day}
        set hours of dueDate to {due_dt.hour}
        set minutes of dueDate to {due_dt.minute}
        set seconds of dueDate to 0
        set due date of r to dueDate
        set remind me date of r to dueDate
"""
    else:
        due_block = ""

    notes_block = f'set body of r to "{notes}"' if notes else ""

    script = f"""
tell application "Reminders"
    tell list "{list_name}"
        set r to make new reminder with properties {{name:"{title}"}}
        {due_block}
        {notes_block}
    end tell
end tell
"""
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    if has_due:
        fmt = "%-d %B %Y %-I:%M %p" if time_str else "%-d %B %Y"
        due_label = due_dt.strftime(fmt)
        print(f'Created: "{title}" — {due_label} → {list_name}')
    else:
        print(f'Created: "{title}" — no due date → {list_name}')

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--date", default=None)
    p.add_argument("--time", default=None)
    p.add_argument("--list", default="Reminders")  # update to match your default list name
    p.add_argument("--notes", default="")
    args = p.parse_args()
    create_reminder(args.title, args.date, args.time, args.list, args.notes)
