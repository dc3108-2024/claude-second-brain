"""
memory-extractor — extract implicit memories from a session transcript.

Usage:
  python3 extract.py --latest               # most recent session
  python3 extract.py --session <uuid>       # specific session
  python3 extract.py --all-new              # all unprocessed sessions from last 48h (cron mode)
  python3 extract.py --latest --dry-run     # print without writing

Configure MEMORY_DIR and TRANSCRIPT_DIR for your Claude Code install path.
"""
import argparse
import json as _json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/shared"))
from lib_claude import call_claude_with_critique, parse_json_response, CritiqueResult

SKILL_NAME    = "memory-extractor"
STEP_NAME     = "extract.identify"

# ── Paths — configure for your environment ─────────────────────────────────────
# Replace <username> with your macOS username, or override via environment variables.
# On macOS: ~/.claude/projects/-Users-<username>/
import os
_CLAUDE_PROJECTS = Path(os.environ.get(
    "CLAUDE_PROJECTS_DIR",
    Path.home() / ".claude/projects" / ("-Users-" + Path.home().name)
))
MEMORY_DIR     = _CLAUDE_PROJECTS / "memory"
TRANSCRIPT_DIR = _CLAUDE_PROJECTS
USAGE_LOG      = Path(__file__).parent.parent / "references/usage_log.jsonl"

MAX_TRANSCRIPT_CHARS = 8000
MIN_CONTENT_CHARS    = 300   # skip thin sessions in --all-new mode
ACTIVE_SESSION_GRACE = 7200  # skip files modified within last 2h (likely still open)

PROMPT_TEMPLATE = """You are extracting new persistent memories from a session transcript.

## Existing memory index (do NOT duplicate these)
{memory_index}

## Session transcript (user turns only)
{transcript}

## Your task
Identify facts, preferences, decisions, and corrections that:
1. Are NOT already captured in the memory index above
2. Are NOT temporary/ephemeral ("will check tomorrow", "doing X next")
3. Are NOT tool outputs or search results
4. WOULD be useful to know in a future session
5. Come from explicit user statements — not inferred by the assistant

Memory types:
- "feedback": behavioral rule or correction ("don't do X", "always use Y", "yes exactly that")
- "user": fact about the user (role, preference, constraint, personal detail)
- "project": project state (started, completed milestone, paused, key decision)
- "reference": pointer to an external resource revealed in conversation

PII REDACTION REQUIRED before writing body content:
Replace third-party names, phone numbers, emails, account numbers, and addresses with
[REDACTED-NAME], [REDACTED-PHONE], [REDACTED-EMAIL], [REDACTED-ACCOUNT].

Body format for each memory (required, include verbatim):
---
name: {{slug}}
description: {{one-line summary}}
metadata:
  type: {{feedback|user|project|reference}}
  source_type: implicit
  created_date: {today}
  confidence: medium
---

{{memory content — for feedback/project: lead with rule/fact, then **Why:** line, then **How to apply:** line}}

CRITICAL: Output raw JSON only. No markdown, no code fences, no explanation.
First character must be {{.

Output schema:
{{
  "memories": [
    {{
      "type": "<feedback|user|project|reference>",
      "stability": "<S for feedback/user/reference, E for project, A for action item>",
      "title": "<human-readable title for MEMORY.md link, 3-6 words>",
      "name": "<kebab-case-slug>",
      "filename": "<name>.md",
      "description": "<one-line hook under 120 chars for MEMORY.md>",
      "body": "<full markdown content including frontmatter above>"
    }}
  ],
  "skipped": ["<reason why candidate was not extracted>"]
}}

If nothing new, return: {{"memories": [], "skipped": ["no new implicit memories in this transcript"]}}
"""


def _already_processed(stem: str) -> bool:
    if not USAGE_LOG.exists():
        return False
    with open(USAGE_LOG) as f:
        for line in f:
            try:
                if _json.loads(line).get("session") == stem:
                    return True
            except _json.JSONDecodeError:
                continue
    return False


def _find_transcript(session_id: str | None, latest: bool) -> Path | None:
    jsonl_files = sorted(
        TRANSCRIPT_DIR.glob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if latest:
        return jsonl_files[0] if jsonl_files else None
    if session_id:
        matches = [p for p in jsonl_files if session_id in p.name]
        return matches[0] if matches else None
    return None


def _find_new_transcripts() -> list[Path]:
    """Return sessions modified in last 48h, not active, not already processed."""
    now = datetime.now().timestamp()
    cutoff_old = now - 48 * 3600
    cutoff_new = now - ACTIVE_SESSION_GRACE
    candidates = []
    for p in TRANSCRIPT_DIR.glob("*.jsonl"):
        mtime = p.stat().st_mtime
        if mtime < cutoff_old or mtime > cutoff_new:
            continue
        if _already_processed(p.stem):
            continue
        candidates.append(p)
    return sorted(candidates, key=lambda p: p.stat().st_mtime)


def _parse_transcript(path: Path) -> str:
    """Extract user message text from transcript, capped at MAX_TRANSCRIPT_CHARS."""
    turns = []
    with open(path) as f:
        for line in f:
            try:
                d = _json.loads(line)
            except _json.JSONDecodeError:
                continue
            if d.get("type") != "user":
                continue
            content = d.get("message", {}).get("content", "")
            if isinstance(content, str):
                text = content.strip()
                if len(text) > 10:
                    turns.append(f"USER: {text}")
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "").strip()
                        if len(text) > 10:
                            turns.append(f"USER: {text}")
    combined = "\n\n".join(turns)
    return combined[:MAX_TRANSCRIPT_CHARS]


def _read_memory_index() -> str:
    index_path = MEMORY_DIR / "MEMORY.md"
    if not index_path.exists():
        return "(empty)"
    lines = index_path.read_text().splitlines()
    entries = [l for l in lines if l.startswith("- ")]
    return "\n".join(entries[:120])


def _critique_response(raw: str) -> CritiqueResult:
    try:
        data = parse_json_response(raw)
    except (_json.JSONDecodeError, ValueError):
        return CritiqueResult("hard", "invalid JSON")

    if not isinstance(data, dict):
        return CritiqueResult("hard", f"expected dict, got {type(data).__name__}")

    if data.get("memories") is None:  # list field — use is None
        return CritiqueResult("hard", "memories field missing")

    if not isinstance(data["memories"], list):
        return CritiqueResult("hard", "memories must be a list")

    for m in data["memories"]:
        if not m.get("filename"):  # noqa: critique-safe — string field
            return CritiqueResult("hard", "memory item missing filename")
        if not m.get("body"):  # noqa: critique-safe — string field
            return CritiqueResult("hard", "memory item missing body")
        if not m.get("title"):  # noqa: critique-safe — string field
            return CritiqueResult("soft", "memory item missing title — will use name")

    return CritiqueResult("pass", "")


def _write_memory_file(memory: dict, dry_run: bool) -> bool:
    filepath = MEMORY_DIR / memory["filename"]
    if filepath.exists():
        print(f"  Skip {memory['filename']} — file already exists")
        return False
    if dry_run:
        print(f"  [DRY RUN] Would create {memory['filename']}: {memory['description']}")
        return True
    filepath.write_text(memory["body"])
    print(f"  Created {memory['filename']}")
    return True


def _append_to_index(memories: list[dict], dry_run: bool) -> None:
    index_path = MEMORY_DIR / "MEMORY.md"
    existing = index_path.read_text()
    new_lines = []
    for m in memories:
        tag = m.get("stability", "E")
        title = m.get("title") or m["name"].replace("-", " ").title()
        hook = m["description"]
        entry = f"- [{tag}] [{title}]({m['filename']}) — {hook}"
        if m["filename"] not in existing:
            new_lines.append(entry)
    if not new_lines:
        return
    if dry_run:
        print(f"\n  [DRY RUN] Would append {len(new_lines)} entries to MEMORY.md")
        return
    updated = existing.rstrip() + "\n" + "\n".join(new_lines) + "\n"
    index_path.write_text(updated)
    print(f"  Appended {len(new_lines)} entries to MEMORY.md")


def _log_run(session_stem: str, written: int) -> None:
    USAGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "date": datetime.now().isoformat()[:19],
        "session": session_stem,
        "memories_written": written,
    }
    with open(USAGE_LOG, "a") as f:
        f.write(_json.dumps(entry) + "\n")


def _process_one(transcript_path: Path, dry_run: bool) -> int:
    """Process a single transcript. Returns number of memories written."""
    print(f"Transcript: {transcript_path.name}")

    transcript = _parse_transcript(transcript_path)
    if len(transcript) < MIN_CONTENT_CHARS:
        print(f"  Skipping — only {len(transcript)} chars (below {MIN_CONTENT_CHARS} threshold)")
        return 0

    print(f"  {len(transcript)} chars of user turns")

    raw, critique = call_claude_with_critique(
        PROMPT_TEMPLATE.format(
            memory_index=_read_memory_index(),
            transcript=transcript,
            today=datetime.now().strftime("%Y-%m-%d"),
        ),
        _critique_response,
        skill=SKILL_NAME,
        step=STEP_NAME,
    )

    if critique.severity == "hard":
        print(f"  Extraction failed: {critique.reason}")
        return 0

    data = parse_json_response(raw)
    memories = data.get("memories", [])
    skipped  = data.get("skipped", [])

    print(f"  {len(memories)} new memories, {len(skipped)} skipped")

    written = 0
    newly_created = []
    for m in memories:
        if _write_memory_file(m, dry_run):
            written += 1
            newly_created.append(m)

    if newly_created:
        _append_to_index(newly_created, dry_run)

    if not dry_run:
        _log_run(transcript_path.stem, written)

    return written


def run(session_id: str | None = None, latest: bool = False,
        all_new: bool = False, dry_run: bool = False) -> None:
    if all_new:
        paths = _find_new_transcripts()
        if not paths:
            print("No new unprocessed sessions found.")
            return
        print(f"Found {len(paths)} session(s) to process")
        total = 0
        for p in paths:
            total += _process_one(p, dry_run)
        print(f"\nAll done. {total} memories written across {len(paths)} session(s).")
        return

    transcript_path = _find_transcript(session_id, latest)
    if not transcript_path:
        print("No transcript found.")
        return

    written = _process_one(transcript_path, dry_run)
    print(f"\nDone. {written} memories written.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract implicit memories from session transcript")
    parser.add_argument("--session", help="Session UUID (partial match OK)")
    parser.add_argument("--latest", action="store_true", help="Use most recent session")
    parser.add_argument("--all-new", action="store_true",
                        help="Process all unprocessed sessions from last 48h (cron mode)")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing files")
    args = parser.parse_args()

    if not args.session and not args.latest and not args.all_new:
        parser.print_help()
        sys.exit(1)

    run(session_id=args.session, latest=args.latest, all_new=args.all_new, dry_run=args.dry_run)
