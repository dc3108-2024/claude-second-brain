---
name: linkedin-post
description: >
  Use when writing a LinkedIn post — from a topic in the user's head,
  an Apple Note title, a research brief, a document, or an idea from the daily
  intel brief. Triggers on: "write a LinkedIn post about X", "turn this into a
  LinkedIn post", "post from my note [title]", "post from today's brief",
  "LinkedIn article on X", "draft a post on X".
---

# LinkedIn Post Skill

LinkedIn post generator. Framework-first, domain-specific, saved as a
numbered PDF to the user's posts folder. Never generic. Always the user's voice.

PDF scaffold: `scripts/build_post_pdf.py`
Dependencies: `reportlab`, `apple-notes MCP` (for note input mode)

---

## Persona
Read `~/.claude/persona.json`. Use these values throughout — never hardcode them:
- `identity.primary` — user's name
- `relocation.brief_label` — transition label, e.g. "AU→NL"
- `professional.domain` — sector expertise
- `professional.employer` — employer
- `professional.next_role` — next role for positioning
- `retirement.target_year` — FIRE target year

## Step 1 — Identify the source

| Mode | How to handle |
|---|---|
| Topic from user | Use directly |
| Apple Note title/keyword | Read the note via apple-notes MCP, extract core insight |
| "From today's brief" | Read the most recent file in the daily brief location (see `references/config.md`) |
| Uploaded doc or URL | Extract the key argument first, then write from that |

Read before writing. Don't guess the content.

---

## Prerequisite — Load algorithm rules

Before writing a single word, read `references/linkedin-algorithm.md`.

It contains: algorithm mechanics and engagement weight hierarchy · hook engineering rules · optimal post length data · credibility signals · post-publish playbook. Apply these rules throughout all steps below — they override intuition.

---

## Step 2 — Extract the core argument

Every post needs ONE clear argument — not a topic, an argument.

*What is the non-obvious thing I want the reader to believe after reading this?*

- ✅ "Most people who say they have a strategy actually have a plan."
- ❌ "Strategy is important."

If the source has multiple angles, pick the sharpest one. Apply at least one of the lenses from `references/config.md`.

---

## Step 3 — Write in the user's voice

**Non-negotiable voice rules:**

- **Hook = contrarian provocation, under 10 words.** First line challenges a belief the reader holds. Do not start with "I" or a question. First ~210 chars are the only guaranteed real estate before "see more" — make them count. See `references/linkedin-algorithm.md` → Hook Engineering.
- **Personal admission early.** "I've been guilty of this too." Disarms. Builds trust.
- **Short paragraphs.** 1–2 sentences max. Blank line between every paragraph. Mobile-first — 57% of LinkedIn traffic is mobile.
- **Name the framework.** Give it a label. Readers remember labels.
- **Specificity signals credibility.** Named actors, specific numbers, named regulators or institutions. Never "a major bank." Never a surprising stat without a source in the first comment.
- **Concrete examples in order:** AI/agentic AI first → banking/insurance/fintech second.
- **No emojis. No bullet points in post body. No corporate jargon.**
- **Closing triplet or contrast.** Clean, memorable.
- **One engagement question at the end.** Genuine, not a CTA. Must invite a real answer.

**LinkedIn editor compatibility — always apply:**

- **No external links in the post body.** LinkedIn suppresses reach for posts with outbound links.
  Any URL (GitHub repo, article, tool) goes in the first comment only — never inline.
- **Section headings use Unicode bold.** LinkedIn's editor has no markdown. Convert any heading
  or label (e.g. "AI User vs. AI Operator") to Unicode bold characters so it renders visually
  distinct on the platform. Use the `to_unicode_bold()` helper in the PDF script.
  Unicode bold survives copy-paste into LinkedIn's composer intact.

**Length:** 250–320 words (1,300–1,900 characters). This is the data-backed sweet spot for B2B thought leadership reach. Over 350 words = dwell drops. See `references/linkedin-algorithm.md` → Post Length.

**Post structure:**
1. Hook — 1 provocative line
2. Personal admission — 2–3 lines
3. "Here's why:" — transition
4. Framework named and defined — 3–5 lines
5. Example 1 (AI) — 5–8 lines
6. Example 2 (enterprise/FS) — 3–5 lines (optional if tight)
7. Simple test or rule — 2–3 lines
8. Closing contrast or triplet — 3 lines
9. Engagement question — 1 line, italicised

---

## Step 4 — Select hashtags

6–8 hashtags. Always include:
- **Topic-exact:** one hashtag naming the specific concept
- **Thought leadership:** `#AgenticAI` and/or `#EnterpriseAI`
- **Community:** one PKM/learning tag (`#SecondBrain`, `#KnowledgeManagement`, `#ContinuousLearning`)
- **Domain:** one FS/industry tag when relevant (`#FinancialServices`, `#Banking`, `#InsurTech`)
- **Architecture/tech:** `#AIArchitecture`, `#DigitalTransformation`, or `#AIStrategy` when relevant

Avoid: `#AI` alone (too broad), duplicates, more than 8 tags.

---

## Step 5 — Save as numbered PDF

Read `scripts/build_post_pdf.py`. Set `slug`, `POST_TITLE`, `TOPIC`, and populate `story[]`
with the post body paragraphs. Write the populated script to `/tmp/post_pdf_run.py` and execute:

```bash
python3 /tmp/post_pdf_run.py
```

Auto-open after saving. Never ask "do you want me to save this?"

The PDF must include a **First comment** block below the hashtags — a thin rule, a bold label,
and the ready-to-paste comment copy with any URLs. Use `comment_s` and `comment_body_s` styles
from the script.

---

## Step 6 — Show post text in conversation

After saving, output two blocks:

**Post body** (ready to paste into LinkedIn composer — no URLs):
- Section headings in Unicode bold
- Closing question italicised
- Hashtags on the final line

**First comment** (paste immediately after publishing):
- One sentence of context + the URL
- Post within seconds of publishing so it sits at top

---

## Post-publish playbook

The algorithm tests posts with 2–5% of the network in the first 60–90 minutes. Everything below maximises expansion from that seed:

1. **Post within the B2B window** — Tue–Thu, 7:30–9:00 AM your local morning (optimise for your audience's timezone)
2. **Pin the first comment immediately** — paste it within seconds of publishing; it must sit at top before any other comments appear
3. **Reply to every comment within 30 minutes** — ask a follow-up question in each reply to extend the thread; threads trigger aggressive reach expansion
4. **Never edit the post body** — editing resets the distribution counter
5. **Do not add links to the body after publishing** — reach suppression applies retroactively

Include this reminder block at the bottom of the PDF under a "Publish Checklist" label.

---

## Monitoring

At the end of every successful run, execute:

```bash
MONITOR_BLOCK
python3 ~/.claude/monitor/monitor.py --log '{"skill":"linkedin-post","est_input_tokens":3000,"est_output_tokens":600,"steps_taken":5,"outputs_written":1,"success":true,"model":"claude-sonnet-4-6","model_tier":"balanced","model_verdict":"appropriate"}'
```

---

## Quality checks before saving

**Hook:**
- Does the first line provoke? Would someone scrolling at 3x speed pause?
- Is the hook under 10 words? Is it contrarian (not a question, not "I…")?
- Are the first 210 characters compelling enough to earn the "see more" click?

**Content:**
- Is there a named framework or mental model?
- Is there at least one AI or fintech/banking concrete example with a named actor?
- Does any surprising stat have a source attributed (can go in first comment)?
- Does the post pass the credibility test: one fact only someone following this space would know?

**Format:**
- Are all paragraphs 2 sentences or fewer, with a blank line between each?
- Word count 250–320 (1,300–1,900 chars)? Count before saving.
- Are all section headings in Unicode bold?

**Engagement:**
- Is the closing memorable (triplet, contrast, or clean rule)?
- Does the engagement question invite a real answer (not "thoughts?")?

**Algorithm:**
- Is the post body free of all external URLs?
- Is there a first comment block in the PDF ready to paste?
- Is there a Publish Checklist block in the PDF with the post-publish playbook?

Rewrite before saving if any check fails.
