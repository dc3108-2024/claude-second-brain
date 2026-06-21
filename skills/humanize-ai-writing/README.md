# humanize-ai-writing

Strip the patterns that mark text as AI-generated, then add real personality.

Lightly paraphrasing doesn't fix AI writing. The patterns are structural — rule-of-three lists, em dashes, contrast framing, significance inflation, self-narrating transitions. This skill removes them systematically, then rewrites for voice.

---

## How it works

```
  [AI-generated text]
        │
        ▼
  Pass 1: Pattern removal
    - em dashes → punctuation that fits
    - "leverage/harness/unlock" → "use/enable"
    - rule-of-three lists → broken up or rewritten
    - contrast framing ("it's not X, it's Y") → deleted
    - transition questions ("the catch?") → deleted
    - significance inflation → deleted
    - self-narration ("this highlights...") → deleted
        │
        ▼
  Pass 2: Personality injection
    - opinions added where appropriate
    - rhythm varied (short and long sentences mixed)
    - specifics replace vague claims
    - "I" used where it fits
        │
        ▼
  [Human-sounding text]
```

---

## Trigger phrases

- `"humanize this"` / `"de-AI this"`
- `"make this sound human"` / `"fix this AI text"`
- `"make it less ChatGPT-y"` / `"rewrite in a human voice"`
- `"remove the AI tone"` / `"this sounds AI-generated"`
- `"edit this"` / `"rewrite this"` / `"make this less formal"`

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Full rules + workflow + example |
| `references/banned-list.md` | Complete banned word/phrase/transition/emoji list |

---

## The 10 hard rules

1. No em dashes
2. No rule-of-three lists
3. No contrast framing ("it's not X, it's Y")
4. No staccato bursts (three short sentences in a row)
5. No rhetorical transition questions ("the catch?")
6. No "nobody" dramatic openers
7. No emojis in professional writing
8. No "let's" openers
9. No fake naming ("The 5-Step Method")
10. No self-narration ("this highlights...")

See `references/banned-list.md` for the complete reference.
