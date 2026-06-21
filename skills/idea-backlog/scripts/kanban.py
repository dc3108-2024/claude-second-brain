"""
Generates a dark-themed HTML Kanban view from ideas.md and opens it in browser.
No Claude calls. CLI: python3 kanban.py
"""
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from recommend import (
    parse_ideas, score_entry, life_lens_boosts,
    DONE_STATUSES, SKIP_STATUSES,
)

IDEAS_PATH = Path(
    __import__("os").environ.get("IDEA_BACKLOG_PATH",
    str(Path.home() / "Idea_Backlog/ideas.md"))
)
OUTPUT_PATH = Path("/tmp/backlog_kanban.html")

_PRIORITY_COLORS = {"High": "#f87171", "Medium": "#fb923c", "Low": "#4ade80"}
_CATEGORY_COLORS = {
    "Pipeline Fix":   {"bg": "#312e81", "fg": "#a5b4fc"},
    "Infrastructure": {"bg": "#1e3a5f", "fg": "#93c5fd"},
    "Career/BD":      {"bg": "#064e3b", "fg": "#6ee7b7"},
    "Personal Tools": {"bg": "#312033", "fg": "#c4b5fd"},
    "Finance":        {"bg": "#3d2d0a", "fg": "#fcd34d"},
    "Content":        {"bg": "#1e293b", "fg": "#94a3b8"},
}

TERMINAL_STATUSES = DONE_STATUSES | SKIP_STATUSES


def _status_bucket(status: str) -> str:
    if status in TERMINAL_STATUSES:
        return "done"
    if status == "In Progress":
        return "in_progress"
    return "backlog"


def _card_html(entry: dict, is_top: bool, today: date) -> str:
    priority = entry.get("priority", "Medium")
    category = entry.get("category", "")
    p_color = _PRIORITY_COLORS.get(priority, "#64748b")
    c_colors = _CATEGORY_COLORS.get(category, {"bg": "#1e293b", "fg": "#94a3b8"})
    age_str = ""
    if entry.get("added"):
        try:
            added = datetime.strptime(entry["added"], "%Y-%m-%d").date()
            age_str = f"{(today - added).days}d"
        except ValueError:
            pass
    notes = (entry.get("notes") or "")[:100]
    if len(entry.get("notes", "")) > 100:
        notes += "…"
    border_style = "border: 2px solid #6366f1;" if is_top else ""
    return (
        f'<div class="card" style="{border_style}">'
        f'<div class="card-header">'
        f'<span class="badge" style="background:{c_colors["bg"]};color:{c_colors["fg"]}">{category}</span>'
        f'<span class="age">{age_str}</span>'
        f"</div>"
        f'<div class="card-title">{entry["title"]}</div>'
        f'<div class="card-meta">'
        f'<span style="color:{p_color}; font-size:0.8em">&#9679; {priority}</span>'
        f"</div>"
        + (f'<div class="card-notes">{notes}</div>' if notes else "")
        + "</div>"
    )


def _col_html(items: list[tuple], label: str, top_title: str | None, today: date) -> str:
    cards = "".join(
        _card_html(e, is_top=(label == "BACKLOG" and e["title"] == top_title), today=today)
        for _, e in items
    )
    count = len(items)
    empty_msg = '<div class="empty">Empty</div>'
    return (
        f'<div class="column">'
        f'<div class="col-header">{label} <span class="col-count">{count}</span></div>'
        f'<div class="cards">{cards or empty_msg}</div>'
        f"</div>"
    )


def generate_html(ideas_text: str | None = None, today: date | None = None, live_refresh_secs: int = 0) -> str:
    if today is None:
        today = date.today()
    text = ideas_text if ideas_text is not None else IDEAS_PATH.read_text()
    entries = parse_ideas(text)
    ll_boosts = life_lens_boosts()

    buckets: dict[str, list] = {"backlog": [], "in_progress": [], "done": []}
    for e in entries:
        bucket = _status_bucket(e.get("status", ""))
        sc = score_entry(e, entries, ll_boosts) if bucket == "backlog" else 0
        buckets[bucket].append((sc, e))

    for key in buckets:
        buckets[key].sort(key=lambda x: -x[0])

    top_title = buckets["backlog"][0][1]["title"] if buckets["backlog"] else None
    total = sum(len(v) for v in buckets.values())

    cols = (
        _col_html(buckets["backlog"], "BACKLOG", top_title, today)
        + _col_html(buckets["in_progress"], "IN PROGRESS", top_title, today)
        + _col_html(buckets["done"], "DONE", top_title, today)
    )

    live_meta = f'<meta http-equiv="refresh" content="{live_refresh_secs}">' if live_refresh_secs else ""
    live_badge = (
        f'<span style="background:#1e2330;border:1px solid #252a38;border-radius:6px;'
        f'padding:2px 9px;font-size:0.72em;color:#6366f1;font-weight:600;margin-left:10px">'
        f'⟳ live · {live_refresh_secs}s</span>'
    ) if live_refresh_secs else ""

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
LIVE_META_PLACEHOLDER
<title>Backlog Kanban — DATE_PLACEHOLDER</title>
<style>
  * { box-sizing:border-box; }
  body { background:#0f1117; color:#e2e8f0; font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif; margin:0; padding:28px; }
  h1 { color:#e2e8f0; margin-bottom:4px; font-size:1.4em; font-weight:600; letter-spacing:-0.3px; }
  .subtitle { color:#475569; font-size:0.82em; margin-bottom:24px; }
  .board { display:flex; gap:14px; }
  .column { flex:1; background:#161a23; border-radius:10px; padding:14px; min-height:200px; border:1px solid #1e2330; }
  .col-header { font-weight:600; font-size:0.72em; letter-spacing:1.8px; text-transform:uppercase; color:#475569; padding-bottom:10px; border-bottom:1px solid #1e2330; margin-bottom:12px; display:flex; align-items:center; gap:8px; }
  .col-count { background:#1e2330; border-radius:8px; padding:1px 7px; font-size:0.95em; color:#64748b; }
  .card { background:#1a1f2e; border-radius:8px; padding:10px 12px; margin-bottom:8px; border:1px solid #252a38; transition:border-color 0.15s; }
  .card-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:7px; }
  .badge { font-size:0.65em; padding:2px 8px; border-radius:6px; font-weight:600; letter-spacing:0.3px; }
  .age { color:#475569; font-size:0.72em; font-variant-numeric:tabular-nums; }
  .card-title { font-weight:500; font-size:0.88em; line-height:1.4; margin-bottom:5px; color:#cbd5e1; }
  .card-meta { margin-bottom:3px; }
  .card-notes { font-size:0.74em; color:#475569; line-height:1.45; }
  .empty { color:#2d3448; font-style:italic; font-size:0.83em; padding:14px 0; }
</style>
</head>
<body>
<h1>Backlog Kanban LIVE_BADGE_PLACEHOLDER</h1>
<div class="subtitle">DATE_PLACEHOLDER &nbsp;&middot;&nbsp; TOTAL_PLACEHOLDER items &nbsp;&middot;&nbsp;
  <span style="color:#6366f1">&#9646;</span> Indigo border = top recommendation</div>
<div class="board">COLS_PLACEHOLDER</div>
</body>
</html>"""
    return (html
        .replace("LIVE_META_PLACEHOLDER", live_meta)
        .replace("LIVE_BADGE_PLACEHOLDER", live_badge)
        .replace("DATE_PLACEHOLDER", str(today))
        .replace("TOTAL_PLACEHOLDER", str(total))
        .replace("COLS_PLACEHOLDER", cols)
    )


if __name__ == "__main__":
    html = generate_html()
    OUTPUT_PATH.write_text(html)
    subprocess.run(["open", str(OUTPUT_PATH)])
    print(f"Kanban saved to {OUTPUT_PATH}")
