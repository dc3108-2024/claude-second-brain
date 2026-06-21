"""
Autonomous Backlog Picker.

Scores open backlog items for autonomy-readiness (low risk, less effort, high impact),
picks the best candidate, notifies Slack + CLI, and optionally drafts the output.

Autonomy-ready categories (Content, Career/BD) can be executed without user.
High-risk categories (Pipeline Fix, Infrastructure, Finance) are excluded.

Usage:
  python3 autonomous_picker.py               # pick + notify only
  python3 autonomous_picker.py --dry-run     # pick + print, no Slack
  python3 autonomous_picker.py --execute     # pick + notify + draft content + notify done
"""
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
_SKILL_DIR = Path(__file__).parent.parent
_SHARED_DIR = Path.home() / ".claude/skills/shared"
_DRAFTS_DIR = Path(__import__("os").environ.get("AUTONOMOUS_DRAFTS_DIR",
    str(Path.home() / "Autonomous_Drafts")))
sys.path.insert(0, str(Path.home() / ".claude/monitor"))
sys.path.insert(0, str(_SHARED_DIR))

from lib_claude import call_claude_with_critique, parse_json_response, CritiqueResult  # noqa: E402
import post_to_slack  # noqa: E402
from recommend import recommend, IDEAS_PATH, USAGE_LOG_PATH  # noqa: E402

SKILL_NAME = "idea-backlog"
STEP_NAME  = "autonomous-draft"

# ── Autonomy scoring ──────────────────────────────────────────────────────────

# Category autonomy weights: positive = can work on, negative = skip entirely
_CATEGORY_AUTONOMY: dict[str, int] = {
    "Content":        8,
    "Career/BD":      5,
    "Personal Tools": 2,
    "Finance":       -99,   # never autonomous — requires user decisions
    "Infrastructure": -99,
    "Pipeline Fix":  -99,
}

_AUTONOMOUS_SIGNALS = [
    "draft", "write", "generate", "post", "search", "research",
    "summarise", "summarize", "run 80-20", "brief", "analyse", "analyze",
]
_BLOCKING_SIGNALS = [
    "prerequisite", "dependency", "once ", "first install", "need user",
    "needs user", "needs to be", "download first", "pending ", "awaiting",
]


def evaluate_autonomy(entry: dict) -> tuple[int, str]:
    """
    Score an item for autonomy-readiness. Returns (score, reason).
    Score < 0 means skip entirely; higher = more suitable for autonomous work.
    """
    cat = entry.get("category", "")
    base = _CATEGORY_AUTONOMY.get(cat, 0)
    if base < 0:
        return base, f"{cat} requires user decision — excluded"

    notes = (entry.get("notes", "") + " " + entry.get("title", "")).lower()

    signal_boost = sum(2 for s in _AUTONOMOUS_SIGNALS if s in notes)
    blocking_penalty = sum(-3 for s in _BLOCKING_SIGNALS if s in notes)

    # Penalise vague items (short notes = unclear scope)
    notes_words = len(entry.get("notes", "").split())
    clarity_score = 1 if notes_words >= 15 else 0

    # Status: already In Progress should not be picked again
    if entry.get("status", "").lower() == "in progress":
        return -99, "already in progress"

    score = base + signal_boost + blocking_penalty + clarity_score
    reasons = [f"Category: {cat} ({base:+d})"]
    if signal_boost:
        reasons.append(f"action signals ({signal_boost:+d})")
    if blocking_penalty:
        reasons.append(f"blocking signals ({blocking_penalty:+d})")
    return score, " | ".join(reasons)


def pick_autonomous(top_n: int = 10) -> dict | None:
    """
    Get up to top_n items from recommend(), filter by autonomy score,
    return the item with the highest combined score, or None if none qualify.
    """
    candidates = recommend()  # returns top 3 by default
    # Extend to top_n by re-running with a wider view
    if top_n > 3:
        from recommend import parse_ideas, life_lens_boosts, score_entry, TERMINAL_STATUSES, _why_now
        from recommend import compute_skip_penalties, compute_velocity_boosts
        text = IDEAS_PATH.read_text()
        all_entries = parse_ideas(text)
        ll_boosts = life_lens_boosts()
        skip_penalties = compute_skip_penalties(USAGE_LOG_PATH)
        velocity_boosts = compute_velocity_boosts(USAGE_LOG_PATH)
        open_items = [e for e in all_entries if e.get("status", "") not in TERMINAL_STATUSES]
        scored = sorted(
            [
                (
                    score_entry(e, all_entries, ll_boosts)
                    + skip_penalties.get(e.get("title", ""), 0)
                    + velocity_boosts.get(e.get("category", ""), 0),
                    e,
                )
                for e in open_items
            ],
            key=lambda x: -x[0],
        )
        candidates = [
            {**e, "score": sc, "why": _why_now(e, ll_boosts, skip_penalties, velocity_boosts)}
            for sc, e in scored[:top_n]
        ]

    best_item = None
    best_combined = -999

    for item in candidates:
        auto_score, auto_reason = evaluate_autonomy(item)
        if auto_score < 0:
            continue
        combined = item.get("score", 0) + auto_score
        if combined > best_combined:
            best_combined = combined
            best_item = {**item, "autonomy_score": auto_score, "autonomy_reason": auto_reason, "combined_score": combined}

    return best_item


# ── Slack / CLI notification ───────────────────────────────────────────────────

def notify(msg: str, dry_run: bool = False) -> None:
    print(msg)
    if not dry_run:
        try:
            post_to_slack.post(msg)
        except Exception as e:
            print(f"[Slack warning] {e}", file=sys.stderr)


def format_pick_message(item: dict, executing: bool) -> str:
    action = "Drafting output..." if executing else (
        f"Run with --execute to draft.\n"
        f"  `python3 {Path(__file__).name} --execute`"
    )
    return (
        f"🤖 *Autonomous Pick* — {date.today().isoformat()}\n"
        f"*{item['title']}*\n"
        f"Category: {item.get('category', '')} | "
        f"Recommend score: {item.get('score', 0)} | "
        f"Autonomy score: {item.get('autonomy_score', 0)}\n"
        f"Why: {item.get('why', '')}\n"
        f"Autonomy: {item.get('autonomy_reason', '')}\n"
        f"{action}"
    )


# ── Content drafting ──────────────────────────────────────────────────────────

_DRAFT_PROMPT = """\
You are drafting a LinkedIn post for a senior PM/operator with deep domain expertise \
in their field, now focused on agentic AI for enterprise use cases.

Topic: {title}
Context from backlog: {notes}

Voice rules:
- PM/operator voice, not engineer
- Hook under 10 words (no emojis, no hashtags in hook)
- 250-320 words total
- Plain words, no jargon, no "game-changing" / "paradigm"
- Banking/insurance examples preferred over generic ones
- No didactic scaffolding ("First... Second... Finally...")

CRITICAL: Output raw JSON only. No markdown, no code fences, no explanation.
First character must be {{.

{{
  "hook": "<opening line, under 10 words>",
  "body": "<main content, 200-270 words>",
  "cta": "<closing call to action, 1-2 sentences>",
  "full_post": "<hook + newline + body + newline + cta, full assembled post>"
}}
"""


def _critique_draft(raw: str) -> CritiqueResult:
    data = parse_json_response(raw)
    issues = []
    if data.get("full_post") is None:   # noqa: critique-safe — presence check
        issues.append(("hard", "full_post missing"))
    if data.get("hook") is None:        # noqa: critique-safe
        issues.append(("hard", "hook missing"))
    if data.get("body") is None:        # noqa: critique-safe
        issues.append(("hard", "body missing"))
    full = data.get("full_post") or ""
    word_count = len(full.split())
    if word_count < 200:
        issues.append(("soft", f"post too short ({word_count} words)"))
    if word_count > 370:
        issues.append(("soft", f"post too long ({word_count} words)"))
    hook = data.get("hook") or ""
    if len(hook.split()) > 12:
        issues.append(("soft", f"hook too long ({len(hook.split())} words)"))
    return CritiqueResult(
        hard_failures=[msg for level, msg in issues if level == "hard"],
        soft_warnings=[msg for level, msg in issues if level == "soft"],
        parsed=data,
    )


def draft_content_item(item: dict) -> Path:
    """Generate a LinkedIn post draft and save to ~/Desktop/Autonomous_Drafts/."""
    prompt = _DRAFT_PROMPT.format(
        title=item["title"],
        notes=item.get("notes", "")[:600],
    )
    raw, critique = call_claude_with_critique(
        prompt, _critique_draft, skill=SKILL_NAME, step=STEP_NAME
    )
    data = parse_json_response(raw)

    _DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", item["title"].lower())[:50].strip("-")
    out_path = _DRAFTS_DIR / f"{date.today().isoformat()}-{slug}.md"

    out_path.write_text(
        f"# {item['title']}\n\n"
        f"_Auto-drafted {date.today().isoformat()} | Score: {item.get('combined_score', '')} | Source: autonomous_picker_\n\n"
        f"---\n\n"
        f"{data.get('full_post', raw)}\n\n"
        f"---\n\n"
        f"**Hook:** {data.get('hook', '')}\n\n"
        f"**CTA:** {data.get('cta', '')}\n"
    )
    return out_path


# ── Usage log ─────────────────────────────────────────────────────────────────

def log_autonomous_event(item: dict, status: str, output_path: Path | None = None) -> None:
    payload = {
        "event": "autonomous",
        "date": date.today().isoformat(),
        "title": item.get("title", ""),
        "category": item.get("category", ""),
        "status": status,
        "combined_score": item.get("combined_score", 0),
    }
    if output_path:
        payload["output"] = str(output_path)
    with USAGE_LOG_PATH.open("a") as fh:
        fh.write(json.dumps(payload) + "\n")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    dry_run = "--dry-run" in sys.argv
    execute = "--execute" in sys.argv

    item = pick_autonomous(top_n=10)
    if item is None:
        msg = "🤖 Autonomous picker: no suitable low-risk item found in backlog right now."
        notify(msg, dry_run=dry_run)
        return

    notify(format_pick_message(item, executing=execute), dry_run=dry_run)
    log_autonomous_event(item, status="picked")

    if not execute:
        return

    cat = item.get("category", "")
    if cat not in ("Content", "Career/BD"):
        notify(f"⚠ Autonomous execution only supported for Content and Career/BD items. Skipping draft for: {cat}", dry_run=dry_run)
        return

    try:
        out_path = draft_content_item(item)
        preview = out_path.read_text()[:200].replace("\n", " ")
        notify(
            f"✅ *Autonomous Draft Complete* — {date.today().isoformat()}\n"
            f"*{item['title']}*\n"
            f"Saved: {out_path}\n"
            f"Preview: _{preview}_",
            dry_run=dry_run,
        )
        log_autonomous_event(item, status="drafted", output_path=out_path)
    except Exception as exc:
        notify(f"❌ Draft failed for *{item['title']}*: {exc}", dry_run=dry_run)
        log_autonomous_event(item, status="failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
