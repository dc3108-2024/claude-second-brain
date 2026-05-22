---
name: voice-profile
description: >
  Apply your personal writing voice to any content — LinkedIn posts, emails,
  articles, summaries, or reports. Reads VOICE_PROFILE.md before writing anything
  public-facing, then rewrites or generates content that sounds like you, not like
  a bot. Triggers on: "write this in my voice", "rewrite this", "draft a post",
  "make this sound like me", "this sounds too generic", or any content creation
  request where tone matters.
---

# Voice Profile Skill

The antidote to sounding like a bot.

Most AI-generated content fails at the same point: it's technically correct but
tonally generic. This skill reads your voice profile before writing anything
public-facing, so the output sounds like a person — specifically, like you.

**Before using this skill:** fill in `VOICE_PROFILE.md` in your `~/.claude/`
directory. Use `VOICE_PROFILE.md.template` in this folder as your starting point.
The more specific you are, the better the output.

---

## Step 1 — Load the voice profile

Read `~/.claude/VOICE_PROFILE.md` before writing a single word.

If the file doesn't exist, stop and tell the user:
> "I need your voice profile before I can write in your voice.
> Fill in the template at `~/.claude/skills/voice-profile/VOICE_PROFILE.md.template`
> and save it as `~/.claude/VOICE_PROFILE.md`."

Do not proceed without it. Generic writing is worse than no writing.

---

## Step 2 — Understand the task

Identify:
- **Format:** Post, email, article, summary, bio, caption, thread, other
- **Platform:** LinkedIn, email, blog, internal doc, other — each has norms
- **Source material:** What is being written or rewritten? Read it fully first.
- **Goal:** Inform, persuade, connect, demonstrate expertise, or entertain?

---

## Step 3 — Extract the core argument

Before writing, state in one sentence:
*What is the single non-obvious thing the reader should believe after reading this?*

If you can't state it, the content isn't ready to write. Go back to the source
material and find the sharpest angle.

A topic is not an argument.
- ❌ "AI is changing how we work"
- ✅ "Most AI productivity gains disappear because people optimise the task, not the system"

---

## Step 4 — Write in voice

Apply every rule in the voice profile without exception. Pay particular attention to:

**What to do:**
- Use the sentence lengths and rhythms described in the profile
- Use the vocabulary the profile flags as natural — avoid the words it flags as unnatural
- Apply the structural patterns (how paragraphs open, how arguments build)
- Match the energy level — some voices are measured, some are punchy, some are warm

**What to never do:**
- Never open with "In today's world" or any variant
- Never use the forbidden phrases list from the profile
- Never pad to fill length — if it's done, it's done
- Never write a list when prose would be stronger
- Never soften a point that should land hard

---

## Step 5 — Self-check before delivering

Read the output aloud (mentally). Ask:

1. Does the first line make someone want to read the second?
2. Would the person whose profile this is recognise this as theirs?
3. Is there a single word that feels out of register — too formal, too casual, too corporate?
4. Does it end with force, or does it trail off?

If any answer is no — rewrite that part. Don't deliver work you wouldn't sign.

---

## Quality rules

- Voice profile is non-negotiable — load it every time, no exceptions
- One pass is rarely enough — read, feel where it goes flat, fix it
- Short is almost always better — cut the last paragraph and see if it's stronger
- The goal is recognition: someone who knows the writer should nod reading this
