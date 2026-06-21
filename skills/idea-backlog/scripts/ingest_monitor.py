"""
Delta-only ingestor. Scans pending_fixes/ for new JSON files and appends them
to ideas.md as Pipeline Fix items. Idempotent — safe to run repeatedly.
No Claude calls. CLI: python3 ingest_monitor.py
"""
import re
from datetime import date
from pathlib import Path

_SKILL_DIR = Path(__file__).parent.parent
PENDING_FIXES_DIR = Path.home() / ".claude/monitor/pending_fixes"
IDEAS_PATH = Path(
    __import__("os").environ.get("IDEA_BACKLOG_PATH",
    str(Path.home() / "Idea_Backlog/ideas.md"))
)
MANIFEST_PATH = _SKILL_DIR / "references/ingested.txt"

_FALLBACK_HEADER = "# Idea Backlog\n\n<!-- Add new ideas below. Most recent at top. -->\n\n"


def _load_manifest(manifest_path: Path) -> set[str]:
    if not manifest_path.exists():
        return set()
    return set(line for line in manifest_path.read_text().splitlines() if line.strip())


def _save_manifest(seen: set[str], manifest_path: Path) -> None:
    manifest_path.write_text("\n".join(sorted(seen)) + "\n")


def parse_filename(filename: str) -> tuple[str, str, str]:
    """
    Pattern: YYYY-MM-DD-<waste_type>-<skill>-<step>.json
    Returns (date_str, waste_type, skill_step).
    """
    stem = Path(filename).stem
    m = re.match(r'^(\d{4}-\d{2}-\d{2})-(.+)$', stem)
    if not m:
        return (date.today().isoformat(), "unknown", stem)
    date_str, rest = m.group(1), m.group(2)
    parts = rest.split("-", 1)
    waste_type = parts[0]
    skill_step = parts[1] if len(parts) > 1 else ""
    return date_str, waste_type, skill_step


def build_entry(filename: str) -> str:
    date_str, waste_type, skill_step = parse_filename(filename)
    title = f"Fix: {skill_step} — {waste_type}"
    return (
        f"\n## {title}\n"
        f"- **Category:** Pipeline Fix\n"
        f"- **Priority:** High\n"
        f"- **Status:** Backlog\n"
        f"- **Added:** {date_str}\n"
        f"- **Source:** monitor\n"
        f"- **Notes:** Auto-ingested from pending_fixes. File: {filename}\n"
        f"\n---\n"
    )


def ingest(
    pending_dir: Path = PENDING_FIXES_DIR,
    ideas_path: Path = IDEAS_PATH,
    manifest_path: Path = MANIFEST_PATH,
) -> list[str]:
    """Ingest new pending_fix files. Returns list of filenames added."""
    seen = _load_manifest(manifest_path)
    new_files = [
        f for f in sorted(pending_dir.glob("*.json"))
        if f.name not in seen
    ]
    if not new_files:
        print("No new pending_fixes to ingest.")
        return []

    ideas_text = ideas_path.read_text() if ideas_path.exists() else _FALLBACK_HEADER
    existing_titles = set(
        m.group(1).strip()
        for m in re.finditer(r'^## (.+)$', ideas_text, re.MULTILINE)
    )
    appended = []
    for f in new_files:
        _, waste_type, skill_step = parse_filename(f.name)
        title = f"Fix: {skill_step} — {waste_type}"
        seen.add(f.name)
        if title in existing_titles:
            print(f"Skipped (title exists): {f.name}")
            continue
        ideas_text += build_entry(f.name)
        existing_titles.add(title)
        appended.append(f.name)
        print(f"Ingested: {f.name}")

    ideas_path.write_text(ideas_text)
    _save_manifest(seen, manifest_path)
    return appended


if __name__ == "__main__":
    ingest()
