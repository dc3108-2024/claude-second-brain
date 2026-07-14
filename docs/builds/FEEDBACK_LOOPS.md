# Feedback Loops — building an AI system I'd be willing to answer for

In regulated finance you don't get to ship an AI system and walk away. You own it in production,
and one day someone — a regulator, a risk committee, a customer — asks you to account for what it
did. That single fact changes how you build. So I build the way I'd want to answer for it: every
call checked, every fix made permanent, and a human standing on anything that can't be undone.

Most AI systems are built the other way. They're at their best the day they ship and quietly decay
from there — prompts drift, an edge case starts failing, the same fault gets patched three times
because the fix never stuck. That's a *self-healing* system at best: it recovers, but it never
gets structurally better, so the cost of owning it only grows. I wanted the opposite — a system
that improves the more it runs. The honest version of how I got there: I patched one parsing fault
three separate times before it occurred to me that the fix, not the failure, was the thing to
engineer.

---

## The strategic point: the model is the easy 20%

Shipping the model is not the hard part. The hard part is everything that keeps it trustworthy
after launch — how you measure quality, how you catch it slipping, how you make an improvement
permanent. That discipline is the whole difference between an AI demo and an AI product, and it's
exactly what a regulated programme is required to stand up. Get it right and you have something
you can put in front of an auditor. Get it wrong and you have a very impressive liability.

Take a concrete one. An AI step reads loan applications and pulls out the fields that matter. It
works on day one. Then a lender changes a document layout, extraction quality slips, and for weeks
the system is quietly wrong — until a human spot-check catches it. The model didn't break. The
discipline around it was missing.

---

## Two kinds of checking: before it ships, and while it runs

```mermaid
flowchart LR
    subgraph OFF["🧪 Before it ships (offline)"]
        T1["Tests that must pass"]
        T2["Run it many times,<br/>measure how much it wobbles"]
        T3["Checks that run before<br/>any change is let in"]
    end
    subgraph ON["📡 While it runs (online)"]
        C1["A second check on<br/>every live answer"]
        C2["Every failure sorted<br/>by what went wrong"]
        C3["A health report —<br/>daily + weekly trends"]
    end
    OFF -->|"a change only ships<br/>if it passes"| SHIP(["🚀 Ship"])
    SHIP --> ON
    ON -->|"a problem caught live<br/>becomes tomorrow's test"| OFF

    classDef off fill:#1e3a5f,stroke:#4a90d9,color:#fff
    classDef on fill:#14452f,stroke:#2ecc71,color:#fff
    classDef ship fill:#7a5c00,stroke:#f5c518,color:#fff
    class T1,T2,T3 off
    class C1,C2,C3 on
    class SHIP ship
```

- **Before it ships (offline checks):** a change is judged against what "good" looks like, run
  many times to see how consistent it is, and blocked automatically if it fails. This is the
  regression net — proof a fix works before anyone relies on it.
- **While it runs (online checks):** every live answer gets a second look, every failure is sorted
  by what actually went wrong, and a health report shows whether things are trending better or
  worse. This is the smoke alarm — it catches drift while it's still cheap to fix.

The two join up: a problem caught live becomes a new before-it-ships test. That's the mechanism
that makes the quality bar only ever climb. In enterprise language this is *offline and online
evaluation* — and the loop between them is what a serious AI programme lives or dies on.

---

## Zoom in: one pattern under every loop

Once I'd built a few of these, they turned out to be the same machine wearing different clothes.
Every loop in the system runs the same six steps:

```mermaid
flowchart LR
    S1["1 · Notice<br/>every action<br/>leaves a trace"]
    S2[("2 · Record<br/>one log,<br/>one owner")]
    S3["3 · Look<br/>fast checks +<br/>slower pattern-spotting"]
    S4["4 · Surface<br/>put it where I'm<br/>already looking"]
    S5{"5 · Act<br/>fix automatically, or<br/>ask me where judgment matters"}
    S6["6 · Lock in<br/>make the fix<br/>impossible to undo"]

    S1 --> S2 --> S3 --> S4 --> S5 --> S6
    S6 -->|"the system is now better,<br/>so the next trace is cleaner"| S1

    classDef stage fill:#14452f,stroke:#2ecc71,color:#fff
    classDef store fill:#1e3a5f,stroke:#4a90d9,color:#fff
    classDef gate fill:#7a5c00,stroke:#f5c518,color:#fff
    class S1,S3,S4,S6 stage
    class S2 store
    class S5 gate
```

The step that carries the whole idea is the last one: **lock in**. Plenty of systems recover from
a failure — but if the fix isn't made permanent, the same fault returns and you fix it forever.
Locking each fix behind a test means effort *compounds* instead of repeating. That one choice is
why the failure rate trends down over time instead of staying flat. It worked in practice: one
step was failing 89% of the time; notice it, surface it, approve the fix, lock it in — near zero,
and it hasn't come back.

---

## Where this lands in a bank

The words differ but the machinery is the same one a regulated AI programme has to build. This
isn't a compliance claim — it's a personal system — just the same engineering discipline, done
because it's the right way to build. What I find worth saying: the risk habits I learned in
banking and the engineering of a feedback loop turned out to be the same job in two vocabularies.

| What a bank calls it | What it means, plainly | How this does it |
|---|---|---|
| **AI observability** | Know what every AI call did, and whether it worked | Every call traced → one running log → a health report |
| **Model / prompt governance** | Changes are reviewed and can't quietly regress | A human approves the fix; a check then makes it un-undoable |
| **Managing risk over the lifecycle** | Risk is handled continuously, not signed off once | Every change: add the safeguard, test it, ship, watch, adjust |
| **Operational resilience** | Assume things break; notice and recover fast | A watchdog, an auto-retry, and a memory of past failures |
| **Human oversight** | A person can review and stop things | Two deliberate points where I approve before it proceeds |

For AI product leadership, this is a straight answer to *"how do you govern AI once it's live?"* —
not a policy slide, but a running system with a timestamped record of every decision, which I ran
against my own work before I'd put the idea in front of anyone else.

---

## The full technical map

Under the hood this is **12 reinforcing loops across four families** — pipeline governance, a
knowledge flywheel, personal alignment, and operational resilience — each a version of the six
steps above, each with its own fast and slow rhythm. The complete map — diagrams for every loop,
which run on their own versus which ask a human, who owns each log, and a reusable template for
building your own — is here:

**[→ The full feedback-loops architecture](../FEEDBACK_LOOPS.md)**

Related: **[the monitor that watches every call →](../../monitor/README.md)** · **[extending the loops →](../../EXTENDING.md)**
