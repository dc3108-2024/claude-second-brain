---
name: document-8020
description: >
  Apply the 80/20 principle to any long, dense, or complex document — extracting
  the 20% of content that delivers 80% of the practical value and turning it into
  a clean, actionable reference PDF. Use this skill whenever the user says "80/20
  this", "give me the key bits", "I don't want to read the whole thing", "make a
  cheat sheet from this", "summarise for action", "extract what I actually need",
  "boil this down", "I need a reference guide from this doc", or drops a long PDF/
  doc/book and wants to know what matters. Also trigger when the user wants to turn
  dense documentation, a technical guide, a course book, or a research paper into
  something they can actually use day-to-day without re-reading the source.
---

# Document 80/20 Skill

The goal is not a summary — it's a **reference artefact the user will actually reach for**. A good summary tells you what a document says. A good 80/20 tells you what to *do* and what to *remember*, stripped of everything that doesn't pull its weight.

## The 80/20 filter

When reading the source, apply this value hierarchy (high → low):

1. **Do-it steps** — commands, workflows, exact procedures, configuration patterns
2. **Decision rules** — when to use X vs Y, criteria, conditions ("use this when...")
3. **Core mental models** — the 2–3 frameworks that explain everything else in the doc
4. **Key facts / numbers** — thresholds, limits, defaults you'll actually look up
5. **Warnings / gotchas** — the things that trip people up, things not to do
6. **Background / theory** — only include if it directly helps you act; skip the rest

Everything that exists purely to fill pages, pad chapters, or give examples of things you already understand gets dropped.

## Step 1 — Extract source to text (PDFs)

For PDFs, **always extract to markdown first** using pdfplumber before reading with Claude.
This costs zero LLM tokens for extraction, strips boilerplate headers/footers automatically,
and cuts vision token usage by 10-20x.

```bash
# Extract PDF → /tmp/<stem>.md  (prints output path to stdout)
md_path=$(python3 ~/.claude/skills/document-8020/scripts/extract_pdf_to_md.py "<pdf_path>")

# Then read the .md file — cheap text tokens, not image tokens
```

Then use the `Read` tool on the output `.md` file. Read in chunks if large (limit 200 lines at a time).

**Fall back to vision (Read tool on PDF directly) only when:**
- The doc is diagram-heavy and figures are essential to the 80/20 content
- pdfplumber extraction produces garbled output (complex multi-column layouts)
- The PDF is image-only / scanned (no text layer)

For docx: read with python-docx or the docx skill.
For URLs or pasted content: read directly.

As you read, mentally tag each section: **keep / trim / skip**. Keep only what scores 1–3 on the hierarchy above, unless a 4 or 5 is genuinely lookup-worthy.

## Step 2 — Structure the output

Organise extracted content into these sections (adapt if the doc warrants something different):

```
1. What this is & why it matters       (2–4 sentences, not a chapter)
2. Quick-start / TL;DR                 (the 3–5 things to do first)
3. Core concepts                       (table or tight bullet list — name + 1-line explanation)
4. Key workflows / step-by-step        (numbered steps for the most common tasks)
5. Decision guide / when to use what   (table or if/then rules)
6. Cheat sheet                         (commands, shortcuts, syntax, config snippets)
7. Gotchas & things to avoid           (the stuff that bites people)
8. What you can safely skip            (sections of the original that aren't worth your time)
```

Not all sections are needed for every doc. A command-line tool guide needs a cheat sheet; a business framework book doesn't. Use judgment.

## Step 3 — Build the PDF

Use the bundled script `scripts/build_8020_pdf.py` to render the output. Pass it a structured data dict:

```bash
python3 <skill_dir>/scripts/build_8020_pdf.py \
  --data <path_to_content.json> \
  --output <output_path.pdf> \
  --title "80/20: [Doc Title]" \
  --source "[Original doc name]"
```

The content JSON format:
```json
{
  "title": "80/20: Claude Code for the Rest of Us",
  "source": "Original: Claude Code for the Rest of Us",
  "sections": [
    {
      "heading": "What this is",
      "type": "prose",
      "content": "..."
    },
    {
      "heading": "Quick-start",
      "type": "bullets",
      "content": ["Step 1: ...", "Step 2: ..."]
    },
    {
      "heading": "Core concepts",
      "type": "table",
      "headers": ["Concept", "What it means"],
      "rows": [["Claude Code", "..."], ["MCP", "..."]]
    },
    {
      "heading": "Cheat sheet",
      "type": "code",
      "content": "claude\nclaude --continue\nclaude --model claude-opus-4-5"
    }
  ]
}
```

Supported section types: `prose`, `bullets`, `numbered`, `table`, `code`, `warning`

## Step 4 — Save and share

Save the PDF to the user's Downloads folder (or wherever they specify).
Name it: `[OriginalDocName]_8020.pdf`

Tell the user:
- How many pages the original was vs how many the 80/20 is
- Which sections you dropped and why (one sentence each)
- Any caveats — if something was genuinely hard to cut, say so

## Quality bar

Before finishing, ask yourself:
- Could someone who never read the original use this PDF to get 80% of the benefit? If not, you cut too much or structured it poorly.
- Is there anything in here a practitioner would never look up? If so, cut it.
- Does every section pass the "would I reach for this?" test? If a section is just nice-to-know, trim it.

## Matplotlib PDF text layout rules (applies when building combined or custom PDFs)

matplotlib does NOT auto-wrap or clip text. Violating these rules causes text to bleed across
element boundaries — the most common failure mode in custom PDF builds.

**Hard rules:**
- Hard-wrap all strings in Python at ≤65 chars before passing to `ax.text()` — insert `\n` explicitly
- Add `clip_on=True` to every `ax.text()` call — prevents overflow being visible if sizing is off
- Size containers to content: calculate line count first, then draw the rectangle
- Body text: fontsize 7.5–8.5, max 2 lines, max 65 chars per line
- Card titles: fontsize 9–11, single line only — shorten title if it would wrap
- Never stack more than 4 text elements in a card without explicit height testing
- Add ≥15% vertical padding inside every container — text never starts within 10px of a border
- Test each page function independently before full render
