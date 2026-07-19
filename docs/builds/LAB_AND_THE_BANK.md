# The lab and the bank — one discipline, two proving grounds

The lab and the bank are one discipline on two proving grounds. The personal builds are the part
most people misread.

---

## The lab

I prove agentic patterns on my own system first — the evaluation loops, the human gates, the
EU AI Act and DORA discipline — at my own risk, before any of it goes near a client. It's cheaper
to learn what doesn't hold up on my own work than on a client's regulated one. I only bring the
patterns that survive that.

---

## The bank

Each build is the lab version of a problem I've also delivered for real.

| The pattern | Proven in the lab | Delivered in the enterprise |
|---|---|---|
| Agentic workflow with human gates and an audit trail | **[JIRA PM Factory](./JIRA_PM_FACTORY.md)** | Led AI-tooling adoption across engineering squads — ~20% less build effort |
| Evaluation discipline and governed AI in production | **[Feedback Loops](./FEEDBACK_LOOPS.md)** | An ML solution signed off by Model Risk, under formal risk governance |
| Document extraction with controls, de-identify first | **[Financial OS](./FINANCIAL_OS.md)** | Prudential-compliant regulated data delivery across 12+ connected systems |

```mermaid
flowchart LR
    LAB["🧪 The lab<br/>prove the pattern<br/>at my own risk"]
    ENT["🏦 The enterprise<br/>ship it under<br/>real governance"]
    LAB -->|"only what holds up"| ENT
    ENT -->|"what real constraints teach"| LAB

    classDef lab fill:#1e3a5f,stroke:#4a90d9,color:#fff
    classDef ent fill:#14452f,stroke:#2ecc71,color:#fff
    class LAB lab
    class ENT ent
```

The lab keeps me current on what agentic systems can do. The enterprise shows me what actually
survives Model Risk on a collections remediation, a regulator on a pension merger, and the team
that has to maintain it afterwards.

---

## The method

Lab-proven, then governed. I bring enterprises patterns I've run at my own risk and then shipped
under real governance - not ones I've only read about.

So it's worth asking of anyone selling AI experience: are you buying someone who has read the
patterns, or someone who has already governed them in production?

**[← Back to the builds](../../README.md#three-builds-up-close)**
