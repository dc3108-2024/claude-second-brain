# document-8020

Apply the 80/20 principle to any long, dense, or complex document. Extract the 20% that delivers 80% of the practical value. Output a clean, actionable reference PDF.

This is not a summariser. A summary tells you what a document says. An 80/20 tells you what to do and what to remember — stripped of everything that doesn't pull its weight.

---

## How it works

```
  [Source document]
  (PDF / EPUB / URL / pasted text)
        │
        ▼
  extract_pdf_to_md.py  ← pdfplumber: text extraction, boilerplate stripped
  (skipped for URLs/paste)
        │
        ▼
  [Read + tag each section]
    keep:  do-it steps, decision rules, core mental models
    trim:  key facts, warnings (only if genuinely lookup-worthy)
    skip:  background, theory, examples of things you already know
        │
        ▼
  [Structure output into sections]
    1. What this is & why it matters
    2. Quick-start / TL;DR
    3. Core concepts (table)
    4. Key workflows (numbered steps)
    5. Decision guide (if/then)
    6. Cheat sheet (commands/shortcuts)
    7. Gotchas & things to avoid
    8. What you can safely skip
        │
        ▼
  build_8020_pdf.py  ← ReportLab: render structured JSON to PDF
        │
        ▼
  [Reference PDF saved to ~/Downloads/]
```

---

## Trigger phrases

- `"80/20 this"` / `"give me the key bits"`
- `"I don't want to read the whole thing"`
- `"make a cheat sheet from this"`
- `"summarise for action"` / `"extract what I actually need"`
- `"boil this down"` / `"I need a reference guide from this doc"`

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Full workflow and quality rules |
| `scripts/extract_pdf_to_md.py` | PDF → clean markdown via pdfplumber |
| `scripts/build_8020_pdf.py` | Structured JSON → reference PDF via ReportLab |

---

## Setup

```bash
pip install pdfplumber reportlab
```

---

## Content JSON format

```json
{
  "title": "80/20: [Doc Title]",
  "source": "Original: [Doc Title] — Author",
  "sections": [
    {"heading": "What this is",  "type": "prose",    "content": "..."},
    {"heading": "Quick-start",   "type": "bullets",  "content": ["...", "..."]},
    {"heading": "Core concepts", "type": "table",    "headers": ["Concept", "Meaning"], "rows": [["X", "..."]]},
    {"heading": "Cheat sheet",   "type": "code",     "content": "command1\ncommand2"},
    {"heading": "Gotchas",       "type": "warning",  "content": ["Never do X", "Watch out for Y"]}
  ]
}
```

Supported types: `prose`, `bullets`, `numbered`, `table`, `code`, `warning`
