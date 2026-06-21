"""
Scoring engine. Reads ideas.md and prints top 3 recommended items to stdout.
No Claude calls. CLI: python3 recommend.py
"""
import json
import re
from datetime import date, datetime
from pathlib import Path

_SKILL_DIR = Path(__file__).parent.parent
IDEAS_PATH = Path(
    __import__("os").environ.get("IDEA_BACKLOG_PATH",
    str(Path.home() / "Idea_Backlog/ideas.md"))
)
FOCUS_PATH = _SKILL_DIR / "references/focus.txt"
LIFE_LENS_PATH = Path.home() / ".claude/skills/life-lens/references/filter-matrix.md"
BACKLOG_SIGNAL_PATH = Path.home() / ".claude/skills/life-lens/references/backlog_signal.json"

PRIORITY_SCORES = {"High": 9, "Medium": 6, "Low": 3}
_PRIORITY_SCORES_CI = {k.lower(): v for k, v in PRIORITY_SCORES.items()}
CATEGORY_BOOSTS = {
    "Pipeline Fix": 4,
    "Infrastructure": 3,
    "Career/BD": 2,
    "Personal Tools": 1,
    "Finance": 1,
    "Content": 0,
}
DONE_STATUSES = {"Done"}
SKIP_STATUSES = {"Parked"}
TERMINAL_STATUSES = DONE_STATUSES | SKIP_STATUSES

FOCUS_CATEGORY_MAP = {
    "career": "Career/BD",
    "infrastructure": "Infrastructure",
    "content": "Content",
    "finance": "Finance",
    "tools": "Personal Tools",
    "pipeline": "Pipeline Fix",
}

USAGE_LOG_PATH = _SKILL_DIR / "references/usage_log.jsonl"


def _load_events(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []
    events = []
    for line in log_path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


def compute_skip_penalties(log_path: Path = USAGE_LOG_PATH) -> dict[str, int]:
    """Return {title: -2} for items recommended >=3x and never actioned."""
    events = _load_events(log_path)
    rec_counts: dict[str, int] = {}
    actioned_titles: set[str] = set()
    for e in events:
        if e.get("event") == "recommended":
            for title in e.get("items", []):
                rec_counts[title] = rec_counts.get(title, 0) + 1
        elif e.get("event") == "actioned":
            actioned_titles.add(e.get("title", ""))
    return {
        title: -2
        for title, count in rec_counts.items()
        if count >= 3 and title not in actioned_titles
    }


def compute_velocity_boosts(log_path: Path = USAGE_LOG_PATH) -> dict[str, int]:
    """Return {category: +1} where actioned/recommended ratio >= 0.4 over last 30 events."""
    events = _load_events(log_path)[-30:]
    rec_counts: dict[str, int] = {}
    act_counts: dict[str, int] = {}
    for e in events:
        if e.get("event") == "recommended":
            for title in e.get("items", []):
                rec_counts["_total"] = rec_counts.get("_total", 0) + 1
        elif e.get("event") == "actioned":
            cat = e.get("category", "")
            if cat:
                act_counts[cat] = act_counts.get(cat, 0) + 1
    total_rec = rec_counts.get("_total", 0)
    if total_rec == 0:
        return {}
    return {
        cat: 1
        for cat, count in act_counts.items()
        if count / total_rec >= 0.4
    }


def log_recommended_event(titles: list[str], log_path: Path | None = None) -> None:
    """Append a recommended event to usage_log.jsonl."""
    if log_path is None:
        log_path = USAGE_LOG_PATH
    if not log_path.parent.exists():
        return
    event = json.dumps({"event": "recommended", "date": date.today().isoformat(), "items": titles})
    with log_path.open("a") as fh:
        fh.write(event + "\n")


def parse_ideas(text: str) -> list[dict]:
    """Parse ideas.md markdown into a list of entry dicts."""
    entries = []
    blocks = re.split(r'^---\s*$', text, flags=re.MULTILINE)
    for block in blocks:
        title_m = re.search(r'^## (.+)$', block, re.MULTILINE)
        if not title_m:
            continue
        entry: dict = {"title": title_m.group(1).strip()}
        for field in ["Category", "Priority", "Status", "Added", "Notes", "Source"]:
            m = re.search(rf'\*\*{field}:\*\*\s*(.+)', block)
            entry[field.lower()] = m.group(1).strip() if m else ""
        entries.append(entry)
    return entries


def age_boost(added_str: str) -> int:
    """One point per week old, capped at 10."""
    if not added_str:
        return 0
    try:
        added = datetime.strptime(added_str, "%Y-%m-%d").date()
        days = (date.today() - added).days
        return min(days // 7, 10)
    except ValueError:
        return 0


def category_boost(category: str) -> int:
    return CATEGORY_BOOSTS.get(category, 0)


def focus_boost(category: str) -> int:
    """Boost matching category by 3. Expires after 7 days by file mtime."""
    if not FOCUS_PATH.exists():
        return 0
    mtime = datetime.fromtimestamp(FOCUS_PATH.stat().st_mtime).date()
    if (date.today() - mtime).days > 7:
        return 0
    focus = FOCUS_PATH.read_text().strip().lower()
    return 3 if FOCUS_CATEGORY_MAP.get(focus) == category else 0


# Keyword patterns per life-lens axis → (keywords, boost, reason label)
# Ordered highest-boost first; first match wins per item.
_RELEVANCE_RULES: list[tuple[list[str], int, str]] = [
    (["agentic", " agent ", "mcp ", "thought leader",
      " bd ", "client pitch", "orchestration"], 2, "AI alignment"),
    (["second brain", "learning os", " kb ", "knowledge graph", "skill library",
      "mental model"], 1, "knowledge compounding"),
    (["infrastructure", "pipeline", "automation", "daemon", "cron"], 1, "infrastructure priority"),
]


def content_relevance_boost(entry: dict) -> tuple[int, str]:
    """Keyword match on title+notes against life-lens axes. Returns (boost, reason)."""
    text = f" {entry.get('title', '')} {entry.get('notes', '')} ".lower()
    for keywords, boost, reason in _RELEVANCE_RULES:
        if any(kw in text for kw in keywords):
            return boost, reason
    return 0, ""


def life_lens_boosts() -> dict[str, int]:
    """Read filter-matrix.md + backlog_signal.json and merge into category boosts."""
    boosts: dict[str, int] = {}
    if LIFE_LENS_PATH.exists():
        text = LIFE_LENS_PATH.read_text()
        if re.search(r'infrastructure|pipeline|automation', text, re.IGNORECASE):
            boosts["Infrastructure"] = boosts.get("Infrastructure", 0) + 2
        if re.search(r'BD\s+entry|thought\s+leader|client\s+pitch', text, re.IGNORECASE):
            boosts["Career/BD"] = boosts.get("Career/BD", 0) + 1
            boosts["Content"] = boosts.get("Content", 0) + 1
    if BACKLOG_SIGNAL_PATH.exists():
        try:
            signal = json.loads(BACKLOG_SIGNAL_PATH.read_text()).get("signals", {})
            for cat, val in signal.items():
                boosts[cat] = boosts.get(cat, 0) + val
        except (json.JSONDecodeError, KeyError):
            pass
    return boosts


def backlog_priority_signal(all_entries: list[dict]) -> dict[str, int]:
    """
    Derive category boosts from the user's own priority assignments.
    Categories where user-created items are majority High → +1.
    Categories where majority Low → -1.
    Excludes auto-ingested Pipeline Fix items (source=monitor) to keep signal clean.
    """
    cat_score: dict[str, int] = {}
    cat_count: dict[str, int] = {}
    for e in all_entries:
        if e.get("source") == "monitor":
            continue
        cat = e.get("category", "")
        priority = e.get("priority", "").lower()
        if not cat or priority not in ("high", "medium", "low"):
            continue
        cat_count[cat] = cat_count.get(cat, 0) + 1
        cat_score[cat] = cat_score.get(cat, 0) + {"high": 1, "medium": 0, "low": -1}[priority]
    result: dict[str, int] = {}
    for cat, count in cat_count.items():
        if count == 0:
            continue
        ratio = cat_score[cat] / count
        if ratio > 0.4:
            result[cat] = 1
        elif ratio < -0.4:
            result[cat] = -1
    return result


def write_backlog_signal(all_entries: list[dict]) -> None:
    """Persist priority signal to life-lens/references/backlog_signal.json."""
    signal = backlog_priority_signal(all_entries)
    payload = {"updated": date.today().isoformat(), "signals": signal}
    try:
        BACKLOG_SIGNAL_PATH.write_text(json.dumps(payload, indent=2))
    except OSError:
        pass  # life-lens dir missing in test environments


def recency_boost(entries: list[dict], category: str) -> int:
    """If 3+ of the last 5 added entries share a category, boost it by 1."""
    def _parse(s: str):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            return None
    valid = [(e, _parse(e["added"])) for e in entries if e.get("added")]
    recent = [e for e, d in sorted(valid, key=lambda x: x[1] or date.min, reverse=True) if d][:5]
    return 1 if sum(1 for e in recent if e.get("category") == category) >= 3 else 0


def score_entry(entry: dict, all_entries: list[dict], ll_boosts: dict[str, int]) -> int:
    cat = entry.get("category", "")
    rel_boost, _ = content_relevance_boost(entry)
    fresh_premium = 0
    if rel_boost > 0 and entry.get("added"):
        try:
            days_old = (date.today() - datetime.strptime(entry["added"], "%Y-%m-%d").date()).days
            fresh_premium = 3 if days_old <= 7 else 0
        except ValueError:
            pass
    return (
        _PRIORITY_SCORES_CI.get(entry.get("priority", "").lower(), 3)
        + age_boost(entry.get("added", ""))
        + category_boost(cat)
        + focus_boost(cat)
        + recency_boost(all_entries, cat)
        + ll_boosts.get(cat, 0)
        + rel_boost
        + fresh_premium
    )


def _why_now(
    entry: dict,
    ll_boosts: dict[str, int],
    skip_penalties: dict[str, int] | None = None,
    velocity_boosts: dict[str, int] | None = None,
) -> str:
    skip_penalties = skip_penalties or {}
    velocity_boosts = velocity_boosts or {}
    reasons = []
    if entry.get("priority", "").lower() == "high":
        reasons.append("High priority")
    a = age_boost(entry.get("added", ""))
    if a >= 4:
        reasons.append(f"aging ({a * 7}+ days old)")
    cat = entry.get("category", "")
    if cat and CATEGORY_BOOSTS.get(cat, 0) >= 3:
        reasons.append(f"{cat} category boost")
    if focus_boost(cat) > 0:
        reasons.append("matches current focus")
    if ll_boosts.get(cat, 0) > 0:
        reasons.append("life-lens alignment")
    rel_boost, rel_reason = content_relevance_boost(entry)
    if rel_boost > 0:
        reasons.append(rel_reason)
        if entry.get("added"):
            try:
                days_old = (date.today() - datetime.strptime(entry["added"], "%Y-%m-%d").date()).days
                if days_old <= 7:
                    reasons.append("fresh + relevant (+2)")
            except ValueError:
                pass
    if velocity_boosts.get(cat, 0) > 0:
        reasons.append("category velocity boost (+1)")
    if skip_penalties.get(entry.get("title", ""), 0) < 0:
        reasons.append("skip penalty applied (-2)")
    return " + ".join(reasons) if reasons else "queued"


def recommend(ideas_text: str | None = None, log_path: Path = USAGE_LOG_PATH) -> list[dict]:
    """Score all open items, apply usage calibration, return top 3. Logs the run."""
    text = ideas_text if ideas_text is not None else IDEAS_PATH.read_text()
    entries = parse_ideas(text)
    write_backlog_signal(entries)
    ll_boosts = life_lens_boosts()
    skip_penalties = compute_skip_penalties(log_path)
    velocity_boosts = compute_velocity_boosts(log_path)

    open_items = [
        e for e in entries
        if e.get("status", "") not in TERMINAL_STATUSES
    ]
    scored = sorted(
        [
            (
                score_entry(e, entries, ll_boosts)
                + skip_penalties.get(e.get("title", ""), 0)
                + velocity_boosts.get(e.get("category", ""), 0),
                e,
                skip_penalties,
                velocity_boosts,
            )
            for e in open_items
        ],
        key=lambda x: -x[0],
    )
    top3 = [
        {
            **e,
            "score": sc,
            "why": _why_now(e, ll_boosts, skip_penalties, velocity_boosts),
        }
        for sc, e, skip_penalties, velocity_boosts in scored[:3]
    ]
    # Only log when reading real ideas.md (not in tests with fixture text)
    if ideas_text is None and top3:
        log_recommended_event([item["title"] for item in top3], log_path)
    return top3


def format_output(items: list[dict]) -> str:
    if not items:
        return "Backlog is empty or all items are Done/Parked."
    lines = ["*Top 3 items to work on:*\n"]
    for i, item in enumerate(items, 1):
        age_str = ""
        if item.get("added"):
            try:
                added = datetime.strptime(item["added"], "%Y-%m-%d").date()
                age_str = f" | Age: {(date.today() - added).days}d"
            except ValueError:
                pass
        lines.append(
            f"{i}. *{item['title']}* (score: {item['score']})\n"
            f"   Category: {item.get('category', '')} | "
            f"Priority: {item.get('priority', '')}{age_str}\n"
            f"   Why now: {item['why']}\n"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_output(recommend()))
