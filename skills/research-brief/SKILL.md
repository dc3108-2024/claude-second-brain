---
name: research-brief
description: >
  Search the web and deliver a synthesised research briefing. Use whenever the user
  says "research X", "brief me on X", "what's happening with X", "find out about X",
  "look into X", "I need to understand X", or drops a topic and wants insight without
  doing the browsing themselves. If information could be found by searching, search —
  don't ask the user to do it themselves.
---

# Research Brief Skill

Automated research: run targeted web searches, synthesise findings into a structured
briefing, and deliver analysis — not a pile of links.

---

## Step 1 — Understand the research intent

Before searching, identify:
- **Topic:** What specifically is being researched?
- **Purpose:** Personal knowledge, professional context, or decision-making?
- **Depth:** Quick orientation (2–3 searches) or thorough brief (4–6 searches)?

Infer from context. Do not ask — make a reasonable call and proceed.

---

## Step 2 — Search strategically

Run 3–5 targeted searches covering different angles:

1. **Current state** — `[topic] 2025` or `[topic] 2026`
2. **Domain angle** — `[topic] [relevant industry]` (finance, healthcare, enterprise, etc.)
3. **Implementation angle** — `[topic] enterprise implementation` or `[topic] how it works`
4. **Trends angle** — `[topic] future trends` or `[topic] research report`
5. **Critical angle** — `[topic] challenges` or `[topic] limitations`

Adapt search terms to the topic. For technical topics, search for real-world adoption
and vendor implementations. For market topics, search for data and named examples.

---

## Step 3 — Synthesise (not summarise)

Produce a briefing with analysis, not a list of summaries.

Structure:

```
### [Topic] — Research Brief
*[Date] | ~[X] min read*

**The One-Line Verdict**
The single most important thing to understand. One sentence.

**What's Actually Happening**
3–5 bullets. Facts, numbers, named actors, real examples. No vague generalities.

**Domain Implications**
What does this mean for [the user's field]? Specific, not generic.

**What to Watch Next**
2–3 things to monitor — companies, regulations, upcoming research, key dates.

**Sources**
Key sources found. Max 5 links.
```

---

## Step 4 — Offer to save

If the topic warrants keeping, offer to save the brief as a markdown file.
Suggest a path like `~/research/[topic-slug]-[date].md`. Ask once — if no response, skip.

---

## Quality bar

- Every fact attributable to a named source, report, or company
- No "experts say" — name the expert or the report
- The briefing should replace the need to browse, not just point toward browsing
- Reading time should be under 5 minutes
