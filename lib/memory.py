"""
memory.py — Read and write the second brain's persistent memory files.

Memory files live in ~/.claude/projects/<project-hash>/memory/ and use a
simple frontmatter + body format:

    ---
    name: my-memory-slug
    description: One-line summary used to decide relevance
    metadata:
      type: user | feedback | project | reference
    ---

    Memory body content here.

This module provides lightweight helpers so skill scripts can load context
without duplicating the path logic or frontmatter parsing.
"""

import re
from pathlib import Path
from datetime import date

# Resolve memory directory relative to ~/.claude/projects/
# Skills that import this module need MEMORY_DIR to point at the right place.
# Override by setting MEMORY_DIR before importing, or pass `memory_dir` explicitly.
_DEFAULT_MEMORY_DIR = Path.home() / ".claude" / "projects"


def _find_memory_dir(base: Path = _DEFAULT_MEMORY_DIR) -> Path | None:
    """Return the first memory/ directory found under the projects base."""
    for candidate in sorted(base.iterdir()) if base.exists() else []:
        mem = candidate / "memory"
        if mem.is_dir():
            return mem
    return None


MEMORY_DIR: Path | None = _find_memory_dir()


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def read_memory(name: str, memory_dir: Path | None = None) -> dict | None:
    """
    Load a memory file by its slug name.

    Returns a dict with keys:
      name        — slug from frontmatter
      description — one-line summary
      type        — user | feedback | project | reference
      body        — full text of the memory body

    Returns None if the file is not found.

    Example
    -------
    mem = read_memory("user_finance")
    if mem:
        print(mem["body"])
    """
    dir_ = memory_dir or MEMORY_DIR
    if dir_ is None:
        return None

    # Accept slug with or without .md extension
    slug = name.removesuffix(".md")
    path = dir_ / f"{slug}.md"
    if not path.exists():
        # Try partial match (slug may differ from filename)
        matches = list(dir_.glob(f"*{slug}*.md"))
        if not matches:
            return None
        path = matches[0]

    text = path.read_text()
    return _parse_memory_file(text)


def list_memories(memory_dir: Path | None = None) -> list[dict]:
    """
    Return a list of all memory files as dicts (name, description, type).
    Body is not included — use read_memory() for full content.
    """
    dir_ = memory_dir or MEMORY_DIR
    if dir_ is None:
        return []
    results = []
    for p in sorted(dir_.glob("*.md")):
        if p.name == "MEMORY.md":
            continue
        try:
            parsed = _parse_memory_file(p.read_text())
            results.append({k: parsed[k] for k in ("name", "description", "type")})
        except (ValueError, KeyError):
            pass
    return results


def search_memories(query: str, memory_dir: Path | None = None) -> list[dict]:
    """
    Simple keyword search across memory names, descriptions, and bodies.
    Returns matching memory dicts (with body included).
    """
    terms = query.lower().split()
    results = []
    dir_ = memory_dir or MEMORY_DIR
    if dir_ is None:
        return []
    for p in sorted(dir_.glob("*.md")):
        if p.name == "MEMORY.md":
            continue
        text = p.read_text().lower()
        if all(t in text for t in terms):
            try:
                results.append(_parse_memory_file(p.read_text()))
            except ValueError:
                pass
    return results


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def save_memory(
    name: str,
    body: str,
    description: str,
    memory_type: str = "project",
    memory_dir: Path | None = None,
) -> Path:
    """
    Write a memory file. Creates or overwrites ~/.../memory/<name>.md.

    Parameters
    ----------
    name         : slug, e.g. "project_my_feature"
    body         : memory body text (plain markdown)
    description  : one-line summary used by the index
    memory_type  : "user" | "feedback" | "project" | "reference"

    Returns the path written.

    Example
    -------
    save_memory(
        name="project_sprint_notes",
        body="Sprint 12 focused on the auth rewrite.\n\n**Why:** ...",
        description="Sprint 12 notes — auth rewrite rationale",
        memory_type="project",
    )
    """
    dir_ = memory_dir or MEMORY_DIR
    if dir_ is None:
        raise RuntimeError("Memory directory not found. Check MEMORY_DIR.")

    slug = name.removesuffix(".md")
    content = (
        f"---\n"
        f"name: {slug}\n"
        f"description: {description}\n"
        f"metadata:\n"
        f"  type: {memory_type}\n"
        f"---\n\n"
        f"{body.strip()}\n"
    )
    path = dir_ / f"{slug}.md"
    path.write_text(content)

    _update_memory_index(dir_, slug, description, path.name)
    return path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)", re.DOTALL)


def _parse_memory_file(text: str) -> dict:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("No frontmatter found")
    fm_raw, body = m.group(1), m.group(2)

    fm: dict = {}
    for line in fm_raw.splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
        elif line.strip().startswith("type:"):
            fm["type"] = line.strip().removeprefix("type:").strip()

    return {
        "name":        fm.get("name", ""),
        "description": fm.get("description", ""),
        "type":        fm.get("type", ""),
        "body":        body.strip(),
    }


def _update_memory_index(dir_: Path, slug: str, description: str, filename: str) -> None:
    """Add or update a line in MEMORY.md for the saved memory."""
    index = dir_ / "MEMORY.md"
    entry = f"- [{slug}]({filename}) — {description}"
    if not index.exists():
        index.write_text(f"# Memory Index\n\n{entry}\n")
        return
    lines = index.read_text().splitlines()
    # Replace existing entry if present
    pattern = f"]({filename})"
    for i, line in enumerate(lines):
        if pattern in line:
            lines[i] = entry
            index.write_text("\n".join(lines) + "\n")
            return
    # Append new entry
    lines.append(entry)
    index.write_text("\n".join(lines) + "\n")
