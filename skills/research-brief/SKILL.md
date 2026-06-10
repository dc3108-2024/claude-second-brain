---
name: research-brief
description: >
  Search the web and deliver a synthesised research briefing. Use this skill whenever
  the user says "research X", "brief me on X", "what's happening with X", "find out
  about X", "what do you know about X", "look into X", "I need to understand X",
  "search for X", or drops a topic and wants insight without doing the browsing
  themselves. User context and domain focus in references/persona.md.
  Also trigger when the user asks about trends, news, tools, frameworks, or competitor
  activity in any domain. If information could be found by searching, search — don't
  ask the user to do it themselves.
---

# Research Brief Skill

Automated research: run targeted web searches, synthesise findings into a structured briefing, and deliver analysis — not a pile of links.

## Persona
Read `~/.claude/persona.json`. Use these values throughout — never hardcode them:
- `professional.domain` — domain expertise, e.g. ["Banking", "Life Insurance", "FinServ", "Agentic AI"]
- `professional.employer` — employer, e.g. "TCS"
- `retirement.target_year` — FIRE target year, e.g. 2036
- `relocation.to_name` — destination country for regulatory context

## Step 0 — Load context

Read `references/persona.md`. Apply the user context, domain expertise, and professional goal to every step. This is what makes the brief relevant rather than generic.

## Step 1 — Understand the research intent

Before searching, identify:
- **Topic:** What specifically is being researched?
- **Purpose:** Is this for personal knowledge, professional positioning, client context, or financial decision-making?
- **Depth needed:** Quick orientation (1-2 searches) or thorough brief (3-5 searches)?

If purpose is unclear, infer from context. Do not ask — make a reasonable call and proceed.

## Step 2 — Search strategically

Run 3-5 targeted searches covering different angles of the topic:

1. **Current state** — "what is [topic] 2025/2026"
2. **Industry angle** — "[topic] banking" or "[topic] insurance" or "[topic] fintech" (whichever applies)
3. **Enterprise/consulting angle** — "[topic] enterprise implementation" or "[topic] [your employer]" or "[topic] consulting"
4. **Thought leadership angle** — "[topic] future trends" or "[topic] research report"
5. **Contrarian/critical angle** — "[topic] challenges" or "[topic] limitations" or "[topic] criticism"

Adapt search terms based on topic. For financial topics, add regulatory and regional context.
For AI topics, prioritise Anthropic, OpenAI, enterprise adoption, and fintech-specific use cases.

## Step 3 — Synthesise (not summarise)

Do not produce a list of summaries. Produce a briefing with *analysis*.

Structure:

### [Topic] — Research Brief
*[Date] | [estimated reading time: X min]*

**The One-Line Verdict**
What is the single most important thing to know? One sentence.

**What's Actually Happening**
3-5 bullet points. Facts, numbers, named actors, real examples. No vague generalities.

**What This Means for Banking/Insurance/Fintech**
Specific implications for his domain. If this is a tech topic, what's the adoption curve in financial services? If regulatory, what's the compliance implication? If market, what's the competitive dynamic?

**The Consulting / BD Angle**
If you were in a client conversation tomorrow, what insight or framework could you use from this? What problem does this help solve for your target domain?

**Thought Leadership Angle**
Is there a contrarian take, an underexplored angle, or a framework gap here worth writing or speaking to? One specific suggestion.

**What to Watch Next**
2-3 things to monitor — companies, regulations, research coming out, dates.

**Sources**
List the key sources found. No more than 5.

## Step 4 — Connect to memory

After delivering the brief, check `references/persona.md` for the memory file paths. If any finding warrants capturing, suggest the relevant file. Ask once — do not save without confirmation.

## Step 5 — Optional: save the brief

If the topic warrants keeping, offer to save to the research path in `references/persona.md`. Ask once. If no response or no, skip it.

## Quality bar

- Every fact should be attributable to a real source
- No vague statements like "experts say" — name the expert or the report
- The BD/consulting angle must be specific enough to use in a real client conversation
- The briefing should replace the need to browse, not just point toward browsing

---

## Monitoring

At the end of every successful run, execute:

```bash
python3 ~/.claude/monitor/monitor.py --log '{"skill":"research-brief","est_input_tokens":8000,"est_output_tokens":2000,"steps_taken":8,"outputs_written":1,"success":true,"model":"claude-sonnet-4-6","model_tier":"balanced","model_verdict":"appropriate"}'
```

<!-- MONITOR_BLOCK -->
