---
name: financial-os
description: >
  Personal financial operating system. Aggregates holdings across accounts and
  platforms, tracks net worth over time, models financial independence scenarios,
  and answers questions about your financial position. Triggers on: "what's my
  net worth", "FIRE status", "how am I tracking", "refresh my portfolio",
  "am I on track", "run the numbers", "financial update".
---

# Financial OS

A personal financial operating system built on Claude Code. Aggregates your
holdings, tracks progress toward financial independence, and surfaces the
decisions that actually move the needle.

Adapt the file paths, platforms, and goal parameters in
`references/config.md` before first use.

---

## Step 1 — Load configuration

Read `references/config.md`. Extract:
- **Goal corpus:** the target number for financial independence
- **Annual spend:** projected retirement living cost
- **Withdrawal rate:** safe withdrawal rate (default 4%)
- **Target year:** when you want to reach FI
- **Platforms:** list of investment/savings accounts to aggregate
- **Input folder:** where statement files are stored

---

## Step 2 — Aggregate holdings

For each platform in the config, check the input folder for the latest statement
(PDF, Excel, or CSV). Extract:

| Field | What to capture |
|---|---|
| Platform / account name | As labeled in the statement |
| Asset class | Equities, bonds, cash, property, crypto, other |
| Current value | In local currency |
| Cost base | Original amount invested (if available) |
| Unrealised gain/loss | Current value minus cost base |

If a statement is missing or stale (> 30 days old), flag it — don't fabricate.

Consolidate into a single holdings table sorted by value descending.

---

## Step 3 — Calculate net worth snapshot

```
Total assets     = sum of all platform values
Total liabilities = mortgages + loans + credit balances (from config)
Net worth        = Total assets − Total liabilities
```

Compare to previous snapshot if one exists in `references/snapshots.md`.
Calculate change in absolute terms and percentage.

---

## Step 4 — FIRE projection

```
FI number        = Annual spend ÷ Withdrawal rate
                   (e.g. $40,000 ÷ 0.04 = $1,000,000)

Gap to FI        = FI number − Current net worth (investable assets only)

Years to FI      = solve for N in:
                   FV = PV × (1 + r)^N + PMT × ((1 + r)^N − 1) / r
                   where r = expected annual return (from config)
                         PMT = annual savings rate (from config)
```

Show three scenarios: conservative (r − 2%), base (r), optimistic (r + 2%).

---

## Step 5 — Asset allocation check

Calculate actual allocation vs. target allocation (from config):

| Asset class | Target % | Actual % | Drift |
|---|---|---|---|
| Equities | X% | Y% | ±Z% |
| Bonds | … | … | … |
| Cash | … | … | … |

Flag any class drifted > 5% from target.

---

## Step 6 — Deliver the dashboard

Output format:

```
## Financial Snapshot — [Date]

**Net Worth:** $X  (+$Y / +Z% since last update)
**FI Number:** $X  (based on $Y/yr at Z% withdrawal)
**Progress:**  X% of FI number
**Gap:**       $X remaining
**On track:**  Yes / No — [one sentence why]

### Scenarios
| Scenario | Return | Years to FI | FI date |
|---|---|---|---|
| Conservative | X% | N | YYYY |
| Base | X% | N | YYYY |
| Optimistic | X% | N | YYYY |

### Holdings Summary
[Top-level table by asset class]

### Flags
- [Any missing statements, allocation drift, or decisions pending]
```

---

## Step 7 — Save snapshot

Append the net worth figure and date to `references/snapshots.md` for
longitudinal tracking. One line per update:

```
2026-05-22 | $XXX,XXX | +$X,XXX since last
```

---

## Extending this scaffold

- **Tax module:** add a step that calculates estimated capital gains and income tax
  based on your jurisdiction's rules
- **Budget module:** feed in monthly spending data and compare to plan
- **Scenario module:** model specific decisions — "what if I reduce contributions
  for 12 months?" or "what if I retire 2 years early?"
- **Statement pipeline:** automate extraction from downloaded PDFs using `pdfplumber`
  (see the pdf skill for extraction patterns)

---

## Quality rules

- Never fabricate a number — if data is missing, say so and flag what's needed
- All projections show assumptions explicitly (return rate, savings rate, inflation)
- The dashboard should be readable in under 2 minutes
- One clear "on track / off track" verdict every time
