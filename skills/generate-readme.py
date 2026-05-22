#!/usr/bin/env python3
"""
Regenerates README.md from skill metadata.
Run directly:  python3 generate-readme.py
Auto-runs via .git/hooks/pre-commit before every commit.

Install the hook:
  cp _hooks/pre-commit .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit
"""

import re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent

# Category definitions — skills are auto-classified by keyword if not listed here.
# Add your own categories and skill names as your library grows.
CATEGORIES = [
    (
        "Intelligence & Research",
        "Automated web research and synthesised briefings",
        ["research-brief"],
    ),
    (
        "Document & Diagram",
        "Generate, manipulate, and visualise any document or process",
        ["process-diagram"],
    ),
    (
        "Learning OS",
        "Capture, synthesise, connect, and recall knowledge systematically",
        ["learning-os"],
    ),
    (
        "Financial OS",
        "Portfolio aggregation, net worth tracking, and financial independence modelling",
        ["financial-os"],
    ),
    (
        "Voice & Content",
        "Write in your own voice — not a bot's. Templates for thought leadership and communication.",
        ["voice-profile"],
    ),
    (
        "Values & Alignment",
        "Filter decisions and content through what actually matters to you",
        ["life-lens"],
    ),
    (
        "Mac Integrations",
        "Native Mac app integrations — Calendar, Reminders, and beyond. Mac only, no API keys required.",
        ["apple-calendar", "apple-reminders"],
    ),
    (
        "System & Infrastructure",
        "Skills for building skills, managing memory, and maintaining your setup",
        [],   # add your system skills here
    ),
]

# Keyword rules for auto-classifying new skills not in any explicit list.
# First rule that matches wins. Matching is case-insensitive on name + description.
AUTO_RULES = [
    (0, ["research", "brief", "intel", "search", "web"],   ["briefing", "web search"]),
    (1, ["pdf", "doc", "diagram", "chart", "draw", "visual"], ["document", "diagram"]),
    (2, ["learn", "kb", "quiz", "capture", "knowledge"],   ["knowledge base", "learning"]),
    (3, ["finance", "portfolio", "invest", "fire", "money"], ["retirement", "portfolio"]),
    (4, ["post", "linkedin", "meeting", "draft", "write"], ["linkedin", "meeting"]),
    (5, ["skill", "memory", "setup", "config", "migrate"], ["skill", "memory"]),
]

SKIP = {"_template", "_hooks"}


def read_description(skill_dir: Path) -> str:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ""
    content = skill_md.read_text(encoding="utf-8")
    fm = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if fm:
        block = fm.group(1)
        multi = re.search(r"description:\s*>\s*\n((?:[ \t]+.+\n?)+)", block)
        if multi:
            lines = [l.strip() for l in multi.group(1).strip().splitlines()]
            return _trim(" ".join(lines))
        single = re.search(r'description:\s*["\'>]?\s*(.+?)["\'<]?\s*$', block, re.MULTILINE)
        if single:
            return _trim(single.group(1).strip().strip("\"'>"))
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("---"):
            return _trim(line)
    return ""


def _trim(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    dot = text.find(". ")
    if dot != -1 and dot < 140:
        return text[:dot + 1]
    if len(text) > 140:
        chunk = text[:137]
        last_space = chunk.rfind(" ")
        return (chunk[:last_space] if last_space > 80 else chunk) + "..."
    return text


def _auto_classify(name: str, description: str) -> int:
    haystack = f"{name} {description}".lower()
    for cat_idx, name_kws, desc_kws in AUTO_RULES:
        if any(kw in haystack for kw in name_kws + desc_kws):
            return cat_idx
    return -1


def collect_skills() -> dict[str, str]:
    return {
        d.name: read_description(d)
        for d in sorted(ROOT.iterdir())
        if d.is_dir() and not d.name.startswith(".") and d.name not in SKIP
        and (d / "SKILL.md").exists()
    }


def build_readme(skills: dict[str, str]) -> str:
    cat_rows: list[list[str]] = [[] for _ in CATEGORIES]
    categorised: set[str] = set()

    for cat_idx, (_, _, names) in enumerate(CATEGORIES):
        for s in names:
            if s in skills:
                cat_rows[cat_idx].append(s)
                categorised.add(s)

    for s in sorted(skills.keys() - categorised):
        idx = _auto_classify(s, skills[s])
        if idx >= 0:
            cat_rows[idx].append(s)
            categorised.add(s)

    sections = []
    for cat_idx, (cat_name, cat_tagline, _) in enumerate(CATEGORIES):
        if not cat_rows[cat_idx]:
            continue
        rows = [f"| [`{s}`](./{s}/SKILL.md) | {skills[s] or '—'} |" for s in cat_rows[cat_idx]]
        block = f"### {cat_name}\n\n> {cat_tagline}\n\n"
        block += "| Skill | What it does |\n|-------|--------------|\n"
        block += "\n".join(rows)
        sections.append(block)

    truly_other = sorted(skills.keys() - categorised)
    if truly_other:
        rows = [f"| [`{s}`](./{s}/SKILL.md) | {skills[s] or '—'} |" for s in truly_other]
        block = "### Other\n\n> Add keywords to AUTO_RULES in generate-readme.py to classify these.\n\n"
        block += "| Skill | What it does |\n|-------|--------------|\n"
        block += "\n".join(rows)
        sections.append(block)

    skill_count = len(skills)
    cat_count   = sum(1 for rows in cat_rows if rows)
    sections_md = "\n\n".join(sections)

    return f"""\
# Skills Library

> {skill_count} skill{"s" if skill_count != 1 else ""} across {cat_count} {"categories" if cat_count != 1 else "category"}.

{sections_md}

---

*Auto-generated by [`generate-readme.py`](./generate-readme.py) · {date.today().strftime("%d %b %Y")}*
"""


def main():
    skills = collect_skills()
    readme = build_readme(skills)
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"README.md updated — {len(skills)} skill(s)")


if __name__ == "__main__":
    main()
