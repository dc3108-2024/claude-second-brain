#!/usr/bin/env python3
"""
Syncs Claude config files to ~/.claude-backup/ for git-based machine migration.

Run directly:  python3 ~/.claude/sync-config.py
Auto-triggered by the PostToolUse hook in settings.json when config files change.

Setup:
  1. Create ~/.claude-backup/ and init a git repo pointing to your private GitHub repo
  2. Add the PostToolUse hook from settings.json.example to ~/.claude/settings.json
  3. From that point on, every config file change auto-commits and pushes
"""

import shutil
from pathlib import Path

HOME = Path.home()
SRC  = HOME / ".claude"
DST  = HOME / ".claude-backup"

# Config files at ~/.claude/ root
ROOT_FILES = [
    "CLAUDE.md",
    "VOICE_PROFILE.md",   # remove if you don't use one
    "settings.json",
    "settings.local.json",
    "agents.json",
]

# ~/.claude/memory/ → backup/memory/
MEMORY_SRC = SRC / "memory"

# ~/.claude/projects/-Users-<username>/memory/ → backup/auto-memory/
# Claude Code encodes the home directory path as the project key
AUTO_MEMORY_SRC = SRC / "projects" / f"-Users-{HOME.name}" / "memory"


def sync():
    changed = 0

    # Root config files
    for name in ROOT_FILES:
        src = SRC / name
        dst = DST / name
        if src.exists():
            if not dst.exists() or src.read_bytes() != dst.read_bytes():
                shutil.copy2(src, dst)
                changed += 1

    # Legacy memory files
    dst_mem = DST / "memory"
    dst_mem.mkdir(exist_ok=True)
    if MEMORY_SRC.exists():
        for f in MEMORY_SRC.glob("*.md"):
            dst = dst_mem / f.name
            if not dst.exists() or f.read_bytes() != dst.read_bytes():
                shutil.copy2(f, dst)
                changed += 1

    # Auto-memory files (written by Claude across sessions)
    dst_auto = DST / "auto-memory"
    dst_auto.mkdir(exist_ok=True)
    if AUTO_MEMORY_SRC.exists():
        for f in AUTO_MEMORY_SRC.glob("*.md"):
            dst = dst_auto / f.name
            if not dst.exists() or f.read_bytes() != dst.read_bytes():
                shutil.copy2(f, dst)
                changed += 1

    print(f"sync-config: {changed} file(s) updated → {DST}")
    return changed


if __name__ == "__main__":
    sync()
