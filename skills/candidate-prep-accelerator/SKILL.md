---
name: candidate-prep-accelerator
description: Use when asked to prepare a candidate for a client interview, generate interview prep materials, create a domain briefing kit, or produce prep materials from a job description — especially for BA, PM, IT Integrator, or tech roles at enterprise accounts in banking, insurance, or financial services.
---

# Candidate Prep Accelerator

## Overview

Given a job description, generates two polished outputs:
1. **Word doc** (Tech Primer) — terminology, systems, process flows, glossary, interview prep
2. **PPT** (Domain Briefing) — enterprise context, mental models, process lifecycle slides, competency profile

Showcaseable as a candidate readiness accelerator.

## Trigger Phrases

- "prepare me for [JD / role / company]"
- "generate interview prep for [role] at [company]"
- "create a candidate prep kit for this JD"
- "run prep accelerator on this JD"
- "build a domain primer for [company/role]"

## Setup (first run only)

```bash
cd ~/.claude/skills/candidate-prep-accelerator/scripts && npm install
```

## Input

JD as pasted text OR a file path. Optionally specify:
- `depth`: `101` (broad BA/PM) or `102` (more technical) — default `101`
- `output_dir`: output folder — default `~/Desktop`

---

## Workflow

### Step 1 — Parse the JD

Extract and write to `/tmp/prep_jd_struct.json`:

```json
{
  "company": "Full legal/trading name of the client organisation",
  "role_title": "Exact role title from JD",
  "role_type": "BA | PM | IT | hybrid",
  "domains": ["Corporate Lending", "Payments", "Trade Finance"],
  "key_technologies": ["LoanIQ", "SWIFT", "ISO 20022"],
  "required_skills": ["API integration", "Agile delivery"],
  "seniority": "entry | mid | senior | lead"
}
```

### Step 2 — Web Research (3–4 searches)

Run these searches and save a research brief to `/tmp/prep_research.md`:

1. `"[company] [primary domain] technology platform 2025"`
2. `"[company] digital transformation [domain] strategy"`
3. `"[company] annual report 2024 wholesale banking overview"` (or relevant segment)
4. `"[company] brand colors hex"` — capture primary and accent hex codes for the PPT

Synthesise into:
- Company size, key business segments, revenue figures
- Named tech platforms (not generic — actual vendor/system names)
- Strategic priorities and live transformation programmes
- Brand primary hex, dark variant hex, accent hex

### Step 3 — Generate Word Content JSON

Based on JD + research, produce `/tmp/prep_word_content.json` with this exact schema:

```json
{
  "meta": {
    "company": "",
    "role": "",
    "domain": "",
    "generated": "Month YYYY",
    "depth": "101",
    "brand_primary": "RRGGBB hex, no #"
  },
  "role_context": {
    "overview": "2-3 sentences on what this role does and why it exists",
    "reporting_structure": "Who this role reports to and key stakeholder map",
    "success_looks_like": ["bullet 1", "bullet 2", "bullet 3"]
  },
  "domain_primer": {
    "overview": "2-3 sentences on the business line(s) this role serves",
    "sub_domains": [
      {
        "name": "Domain name",
        "summary": "2 sentence summary",
        "key_concepts": ["term1", "term2", "term3"]
      }
    ]
  },
  "systems_landscape": [
    {
      "system": "Finastra LoanIQ",
      "vendor": "Finastra",
      "purpose": "What it does in 1 sentence",
      "category": "Core Lending | Payments | Risk | CRM | Data | Compliance"
    }
  ],
  "process_flows": [
    {
      "name": "Process name",
      "steps": [
        "Step 1: description",
        "Step 2: description"
      ]
    }
  ],
  "glossary": [
    {
      "term": "Term",
      "definition": "Clear definition in plain English",
      "context": "Domain or product area"
    }
  ],
  "regulatory_context": [
    {
      "regulation": "Name / acronym",
      "relevance": "Why it matters to this role"
    }
  ],
  "interview_prep": {
    "likely_questions": ["Q1", "Q2", "Q3"],
    "talking_points": ["Point 1", "Point 2"],
    "questions_to_ask": ["Q to ask them 1", "Q to ask them 2"]
  }
}
```

**Quality targets:** 15–20 glossary terms (A–Z sortable), 2 process flows, 6–10 systems, 4–6 regulatory items, 6–8 interview questions.

Write to `/tmp/prep_word_content.json`.

### Step 4 — Generate PPT Content JSON

Produce `/tmp/prep_ppt_content.json` with this schema:

```json
{
  "meta": {
    "company": "",
    "role": "",
    "brand_primary": "RRGGBB hex, no #",
    "brand_dark": "RRGGBB hex, no #",
    "brand_accent": "RRGGBB hex, no #"
  },
  "company_overview": {
    "tagline": "Company's own tagline or mission statement",
    "stats": [
      { "label": "Total Assets", "value": "€1.1T" },
      { "label": "Revenue", "value": "€4.1B" },
      { "label": "Countries", "value": "40+" },
      { "label": "Clients", "value": "5,000+" }
    ],
    "key_segments": ["Segment 1", "Segment 2", "Segment 3"],
    "tech_strategy": "2-3 sentences on the company's tech transformation agenda"
  },
  "domains": [
    {
      "name": "Domain name (e.g. Corporate Lending)",
      "subtitle": "One-liner explaining scope",
      "mental_model": {
        "title": "The Four Lenses of [Domain]",
        "pillars": [
          {
            "title": "Pillar title (e.g. Credit Risk)",
            "bullets": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"]
          }
        ]
      },
      "process_flow": {
        "title": "Process name end-to-end",
        "steps": [
          {
            "label": "Step label (short, 1-3 words)",
            "description": "What happens at this step — 2-3 sentences",
            "system": "System/tool name used here"
          }
        ],
        "footer": "One key insight or standard that governs this process"
      }
    }
  ],
  "tech_themes": [
    {
      "theme": "Theme name (e.g. ISO 20022)",
      "relevance": "Why this matters to the role — 1-2 sentences"
    }
  ],
  "competency_profile": {
    "title": "What Good Looks Like — [Role Title]",
    "quadrants": [
      {
        "title": "Domain Knowledge",
        "bullets": ["Point 1", "Point 2", "Point 3", "Point 4"]
      },
      {
        "title": "Technical Integration Skills",
        "bullets": ["Point 1", "Point 2", "Point 3", "Point 4"]
      },
      {
        "title": "Programme Delivery",
        "bullets": ["Point 1", "Point 2", "Point 3", "Point 4"]
      },
      {
        "title": "[Company] Culture Fit",
        "bullets": ["Point 1", "Point 2", "Point 3", "Point 4"]
      }
    ]
  }
}
```

**Quality targets:** 1–3 domains (each with 4 pillars + 6-step process flow), 4–6 tech themes, 4 competency quadrants.

Write to `/tmp/prep_ppt_content.json`.

### Step 5 — Build Word Doc

```bash
cd ~/.claude/skills/candidate-prep-accelerator/scripts && \
node build_word.js --content /tmp/prep_word_content.json
```

Output: `~/Desktop/[Company]_[Role]_Tech_Primer.docx`

### Step 6 — Build PPT

```bash
cd ~/.claude/skills/candidate-prep-accelerator/scripts && \
node build_ppt.js --content /tmp/prep_ppt_content.json
```

Output: `~/Desktop/[Company]_[Role]_Domain_Primer.pptx`

### Step 7 — Open Both

```bash
open ~/Desktop/[Company]_[Role]_Tech_Primer.docx
open ~/Desktop/[Company]_[Role]_Domain_Primer.pptx
```

Confirm the filenames from the script console output and use the exact paths printed.

---

## Output Naming

Both scripts auto-generate filenames from `meta.company` (first 2 words) and `meta.role` (first 2 tokens):

| Input | Output |
|-------|--------|
| company: "ING Wholesale Banking", role: "IT Integrator / Tech PM" | `ING_Wholesale_IT_Integrator_Tech_Primer.docx` |
| company: "Barclays Corporate Bank", role: "Business Analyst" | `Barclays_Corporate_Business_Analyst_Tech_Primer.docx` |

Override with `--output ~/Desktop/custom_name.docx`.

---

## Common Mistakes

| Issue | Fix |
|-------|-----|
| `Cannot find module 'pptxgenjs'` | Run `npm install` in `scripts/` |
| Hex colours appear wrong | Never include `#` prefix in JSON hex values |
| PPT process flow truncated | Limit to 6 steps; longer processes split into two flows |
| Word TOC empty | Headings must use `HeadingLevel.HEADING_1/2` — already handled by build script |
| File name shows "Tech_Tech_Primer" | The role contains "Tech" — role slug is limited to 2 tokens, already fixed |
