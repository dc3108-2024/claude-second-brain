# The Fingerprint Method — giving an AI agent a consistent voice

Ground an agent in a redacted corpus of your real writing, then put a judge in front of it
that scores every draft against that voice and holds anything below the bar.

Most attempts to give an agent a voice are *descriptions*: "write clearly and professionally,
in a calm, structured tone." A description hands the model an adjective, and adjectives are
shared property — everyone's prompt says the same thing. The output comes back on-brief and
completely generic.

The fix is two moves: **ground**, then **gate**.

---

## The pattern

```
  your real writing            redact PII              grounding block
  (sent messages,   ─────────▶  (names, orgs,  ─────▶  = "the fingerprint"
   presentations)               numbers)                      │
                                                              │ injected before generation
                                                              ▼
                                                      ┌──────────────┐
                                                      │   generate   │
                                                      └──────┬───────┘
                                                             ▼
                                                      ┌──────────────┐   below bar
                                                      │  voice judge │ ───────────▶ HOLD
                                                      │ score vs the │             (human review)
                                                      │  fingerprint │
                                                      └──────┬───────┘
                                                             │ at/above bar
                                                             ▼
                                                           ship
```

**Ground.** Build the grounding from a corpus of your actual output — not a description of it.
Then strip everything identifying. What remains is not content; it is the *shape* of how you
write: how you open a point, carry an argument, close a decision. That redacted corpus is the
fingerprint, and it is injected into every generation prompt.

**Gate.** Grounding alone is not enough — models drift, and voice degrades quietly. So a second
model scores each draft against the fingerprint and holds anything below a set bar. Off-voice
drafts do not ship; they wait for a human. This turns voice from a prompt-writing problem into
an **evaluation problem** — the same eval-harness machinery engineers already use for
correctness, pointed at voice instead.

Simple test for whether it works: *could the output pass as you to someone who knows your
writing?* A description never survives that. A fingerprint does.

---

## Files in this scaffold

| File | What it is |
|---|---|
| [`VOICE_PROFILE.template.md`](./VOICE_PROFILE.template.md) | A blank voice-profile template. Fill it from your own redacted corpus — it is the fingerprint the model writes against. |
| [`grounding_config.example.json`](./grounding_config.example.json) | Config for the register sources, the pass bar, and the PII redaction patterns. |
| [`voice_judge.example.py`](./voice_judge.example.py) | A reference implementation of the judge gate: score a draft against the grounding block, hold below the bar. Provider-agnostic. |

These are **templates**, not a finished system. They show the shape of the pattern; you supply
your own corpus and wire the LLM calls to your provider.

---

## Why redaction is the unlock, not the tax

You cannot ground an agent on raw personal or customer data — that is a leak waiting to happen.
But you do not need the data. You need the *pattern underneath it*. Strip the names, the
numbers, the identifying specifics, and what is left is the voice, which is exactly what you
wanted to capture.

The redaction that feels like a compromise is the thing that makes the whole approach usable —
and, in a regulated setting, compliant.

---

## Where this matters beyond one person

A bank or an insurer has the same problem at industrial scale, with two constraints an
individual does not: their correspondence has to sound like the institution across thousands of
authors (and now across AI agents), and none of it can leak a customer's data. Those constraints
look like they fight. They do not. Build the fingerprint from real correspondence with the data
stripped out — institutional voice kept, liability discarded — and gate every generated message
before it goes out. Brand voice and data protection stop being a trade-off; the same mechanism
serves both.

---

## The compounding property

A described persona is static: you write it once and it slowly goes stale. A fingerprint grows
while you work — every message you write adds to the corpus, so the voice sharpens over time with
no extra effort, and the judge keeps every new agent aligned to it automatically.

Describe your voice, and a model approximates you. Ground it in evidence, and it recognises you.
Gate it with a judge, and it stops drifting.

---

*Part of the [Claude Code personal second-brain reference architecture](../../../README.md).
Templates are MIT-licensed; adapt freely.*
