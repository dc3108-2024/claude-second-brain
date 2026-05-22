"""
Create an Apple Calendar event via osascript.
Usage: python3 create_event.py --title "..." --date YYYY-MM-DD --start HH:MM
                                [--duration MINS] [--calendar "..."] [--notes "..."]
"""
import argparse, subprocess, sys
from datetime import datetime, timedelta

def create_event(title, date_str, start_str, duration_mins, calendar, notes):
    start_dt = datetime.strptime(f"{date_str} {start_str}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(minutes=duration_mins)

    notes_line = f'set description of evt to "{notes}"' if notes else ""

    script = f"""
tell application "Calendar"
    tell calendar "{calendar}"
        set startDate to current date
        set year of startDate to {start_dt.year}
        set month of startDate to {start_dt.month}
        set day of startDate to {start_dt.day}
        set hours of startDate to {start_dt.hour}
        set minutes of startDate to {start_dt.minute}
        set seconds of startDate to 0

        set endDate to current date
        set year of endDate to {end_dt.year}
        set month of endDate to {end_dt.month}
        set day of endDate to {end_dt.day}
        set hours of endDate to {end_dt.hour}
        set minutes of endDate to {end_dt.minute}
        set seconds of endDate to 0

        set evt to make new event with properties {{summary:"{title}", start date:startDate, end date:endDate}}
        {notes_line}
    end tell
    reload calendars
end tell
"""
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    day_label = start_dt.strftime("%A, %-d %B %Y")
    start_label = start_dt.strftime("%-I:%M %p")
    end_label = end_dt.strftime("%-I:%M %p")
    print(f'Created: "{title}" — {day_label} {start_label} – {end_label} → {calendar}')

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--start", required=True)
    p.add_argument("--duration", type=int, default=60)
    p.add_argument("--calendar", default="Calendar")  # update to match your calendar name
    p.add_argument("--notes", default="")
    args = p.parse_args()
    create_event(args.title, args.date, args.start, args.duration, args.calendar, args.notes)
