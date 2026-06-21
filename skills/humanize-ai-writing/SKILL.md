---
name: humanize-ai-writing
description: >
  Edit AI-generated text to remove the patterns that make it sound robotic, then add real
  human personality. Use this skill whenever the user asks to "humanize" text, "de-AI" it,
  "make this sound human," "fix this AI text," "make it less ChatGPT-y," "rewrite in a
  human voice," or pastes a passage that obviously came out of an LLM and wants it to read
  like a person wrote it. Also trigger on requests like "edit this," "rewrite this," "make
  this less formal," "remove the AI tone," "this sounds AI-generated," or any general
  request to revise prose for naturalness or voice. Always use this skill for any
  AI-text-editing or humanizing request — do not just lightly paraphrase from memory.
---

# Humanize AI Writing

Edit AI-generated text so it reads like a human wrote it.

Asking an LLM for a "more natural tone" doesn't fix AI writing. The problem is that LLMs
default to the safest, most statistically average version of every sentence. The result
is text that technically makes sense but feels like it came off an assembly line.

Two things have to happen: remove the specific patterns that mark text as AI-generated,
then add actual personality. Both matter. Text with the AI patterns stripped but no voice
added still reads like a flat press release.

---

## Workflow

### Step 1: Read the input carefully

Read what the user gave you. Notice the obvious tells before editing: em dashes
everywhere, "let's dive in," rule-of-three lists, "it's not X, it's Y" framing, "in
today's rapidly evolving landscape," boldface on every key term, etc.

If the user gave instructions about voice, audience, length, or format, honor those
alongside the rules below.

### Step 2: Apply the rules

Run the input through the rules in this file. Two passes work well:
- First pass: remove the banned patterns (the cleanup).
- Second pass: rewrite for voice and rhythm (the personality injection).

For the comprehensive banned list (full transition words, phrases, adjectives, verbs,
emojis), read `references/banned-list.md`.

### Step 3: Self-check

Before delivering, scan the output for any pattern from the rules. Search for `—`,
"let's," "leverage," "unlock," "navigate," "underscore," and any "it's not X, it's Y"
construction. If you find any, fix them.

Also check: did three short sentences land in a row? Is there a rule-of-three list? Did
a heading get title-cased? Are quotes curly?

### Step 4: Deliver

Hand back the rewritten text. No preamble like "here's the rewrite!" Just the text. If
the user asked for a comparison or explanation, provide it after the rewritten text, not
before.

---

## Hard rules (never break these)

1. **No em dashes.** Use commas, periods, or parentheses.
2. **No rule-of-three lists.** Don't group things into trios ("efficient, effective, and
   reliable"). Two items is fine. Four is fine. Three every time is the giveaway.
3. **No contrast framing.** Don't write "It's not X, it's Y." Don't write the escalation
   version: "It's not A. It's not even B. It's actually C." Just say what you mean.
4. **No staccato bursts.** Don't string three or more short sentences together for drama.
   Vary sentence length.
5. **No rhetorical transition questions.** Delete "The catch?" "The kicker?" "But here's
   the thing." "So what does this mean?" Only ask questions you'd actually ask someone.
6. **No "nobody" as a dramatic opener.** "Nobody tells you this" and "Nobody talks about
   this" feel fake.
7. **No emojis in professional writing.** See the emoji section in the reference file.
8. **No "let's" openers.** "Let's dive in," "Let's break this down," "Let's explore"
   sound like a YouTube intro.
9. **No fake naming.** Don't capitalize ordinary ideas into "The 5-Step Method" or "The
   Growth Paradox." If it doesn't already have a real name people use, just describe it.
10. **No self-narration.** Don't announce or comment on your own points. Delete "this
    highlights," "this underscores," "the key takeaway is," "now for the interesting
    part." If the point landed, the narration is dead weight. If it didn't, the narration
    won't save it.

---

## Top patterns to remove

### Phrases to delete

"It's worth noting that," "in today's rapidly evolving landscape," "at the end of the
day," "that being said," "first and foremost," "needless to say," "rest assured," "make
no mistake," "simply put," "in a nutshell," "the reality is," "let that sink in," "read
that again," "spoiler alert:," "pro tip:," "the takeaway?," "the bottom line?," "here's
why this matters," "here's why that matters," "this highlights," "this underscores,"
"this speaks to," "what does this mean?," "and that's where it gets interesting," "and
here's the thing," "stands out as," "serves as a reminder," "paves the way for," "sheds
light on," "bridges the gap," "strikes a balance," "raises the bar."

### Words to swap or cut

**Adjectives to avoid:** seamless, robust, cutting-edge, innovative, transformative,
comprehensive, holistic, dynamic, scalable, groundbreaking, profound, paramount, pivotal,
remarkable, vibrant, vital, exemplary, unprecedented, multifaceted.

**Verbs to swap:** leverage → use; harness → use; unlock (figurative) → enable; delve →
look at; navigate (figurative) → handle; underscore → show; foster → build; cultivate →
grow; amplify → increase; elevate → raise; empower → let; streamline → simplify; craft
(figurative) → write or make; spearhead → lead; demystify → explain; resonate → connect;
utilize → use; facilitate → help; expedite → speed up; implement → start or build;
optimize → improve; garner → get; embark → start; augment → add to.

**Transition words to avoid:** moreover, furthermore, however (as a sentence opener),
nevertheless, nonetheless, thus, hence, indeed, notably, particularly (as a sentence
opener), accordingly, additionally, consequently, undoubtedly, certainly.

For the complete banned list, read `references/banned-list.md`.

### Style patterns to fix

- **Copula avoidance.** Replace "serves as," "stands as," "functions as," "represents"
  with "is." Replace "boasts," "features," "offers" with "has." LLMs avoid "is" for some
  reason; just use it.
- **-ing phrase padding.** Cut endings like "highlighting the importance of,"
  "underscoring the need for," "reflecting a broader trend toward," "paving the way for,"
  "shedding light on." These add words without meaning.
- **Synonym cycling.** If the same thing gets called "the platform," then "the system,"
  then "the solution," then "the tool" in consecutive sentences, pick one and stick with
  it.
- **False ranges.** Cut "from X to Y" when X and Y aren't on a real spectrum.
- **Boldface abuse.** Don't bold key terms in every sentence. Use bold sparingly or not
  at all.
- **Title case headings.** Use sentence case: "How to write better emails," not "How To
  Write Better Emails."
- **Curly quotes.** Use straight quotes (`"like this"`), not curly quotes.

### Filler to cut

- "in order to" → "to"
- "due to the fact that" → "because"
- "at this point in time" → "now"
- "has the ability to" → "can"
- "in the event that" → "if"
- Delete "it is important to note that" entirely.
- Delete "it's worth considering that" entirely.
- Cut sentences that start with throat-clearing.

### Hedging

Cut excessive qualification. "It could potentially possibly be argued that the policy
might have some effect" becomes "The policy may affect outcomes." One qualifier per claim
is plenty.

### Significance inflation

Remove anything that announces importance instead of showing it: "marking a pivotal
moment," "a testament to," "setting the stage for," "reflects broader trends," "indelible
mark," "deeply rooted." If something matters, explain why with specifics.

### Promotional tone

Remove travel-brochure language: "nestled in," "vibrant," "rich cultural heritage,"
"stunning," "breathtaking," "renowned," "must-visit," "boasts a," "in the heart of,"
"natural beauty." Use concrete facts instead.

### Vague attribution

Replace "experts say," "industry observers note," "some critics argue" with named sources
or cut the claim. If you can't name the source, the claim probably isn't worth including.

### Generic positive conclusions

Remove "The future looks bright," "Exciting times lie ahead," "This represents a major
step in the right direction." End on a real fact instead.

---

## Add personality

Clean text without personality is still boring. After stripping the AI patterns, do this:

- **Have opinions.** React to what you're writing about. "I don't know how to feel about
  this" beats a neutral pros-and-cons list.
- **Vary rhythm.** Mix short sentences with longer ones. When every sentence is the same
  length, it feels generated.
- **Use "I" when it makes sense.** First person sounds like a real person thinking.
- **Be specific.** Not "this is concerning" but "there's something unsettling about a
  system that runs all night with no one watching."
- **Leave some imperfection.** Perfect structure feels algorithmic. An aside, a
  half-formed thought, an honest "I'm not sure" is more convincing than a clean
  five-paragraph essay.
- **Acknowledge mixed feelings.** People rarely feel one way about anything. "This is
  impressive but also kind of unsettling" is more honest than just "This is impressive."

---

## Example

**Before (AI):**

> DataSync is a cutting-edge, AI-powered data integration platform that seamlessly
> connects your entire tech stack. Our innovative solution leverages advanced machine
> learning to streamline workflows, enhance productivity, and drive transformative
> results. It's not just a tool. It's not even a platform. It's a paradigm shift in how
> enterprises harness the power of their data.

**After (human):**

> DataSync moves data between your apps without you having to think about it. You
> connect Salesforce and HubSpot once, set a few rules, and it keeps them in sync. When
> a deal closes in one, the other knows about it within a few minutes. Most customers are
> mid-size sales teams who got tired of copying and pasting between tabs.

What changed: em dashes gone, the "It's not X. It's not even Y. It's Z." escalation
gone, the "leverages... streamline... enhance" verb stack gone, the rule-of-three
adjective lists gone. What got added: a concrete description of who the customer is.

---

## Reference files

- `references/banned-list.md` — Comprehensive list of banned words, phrases, transitions,
  and emojis. Read this when the input has a heavy concentration of patterns not fully
  covered in this file, or when the user wants a thorough top-to-bottom scrub.
