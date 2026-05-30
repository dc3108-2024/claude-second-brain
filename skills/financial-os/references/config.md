# Financial OS — Configuration

All persona-specific data lives here. Scripts read this file — not SKILL.md.
Update this file when accounts, scenarios, or assumptions change.

---

## Paths

| Key | Value |
|---|---|
| Scripts | `~/.claude/skills/financial-os/scripts/` |
| Statements input | `~/Finance/Statements/`  ← set to your actual folder |
| Runtime data | `~/FinancialOS/` |
| portfolio_data.json | `~/FinancialOS/portfolio_data.json` |
| data/portfolio.json | `~/FinancialOS/data/portfolio.json` |
| Excel output | `~/FinancialOS/Consolidated_Portfolio.xlsx` |

---

## FIRE Scenarios

Active scenario: `[your_active_scenario_key]`

| Key | Label | Income/yr | FIRE year | Contrib/mo | Notes |
|---|---|---|---|---|---|
| `base` | Base case | $XX,000 | 20XX | $X,000 | Your primary plan |
| `lean` | Lean FIRE | $XX,000 | 20XX | $X,000 | Lower spend, earlier date |
| `fat` | Fat FIRE | $XX,000 | 20XX | $X,000 | Higher spend target |
| `conservative` | Conservative | $XX,000 | 20XX | $X,000 | Stress test: lower returns, higher fees |

Source of truth: `~/FinancialOS/data/lifestyle.json` — this table is a snapshot.

---

## Retirement assumptions (active scenario)

| Parameter | Value |
|---|---|
| FIRE target year | 20XX |
| Current age | XX (reads from `data/profile.json` at runtime) |
| Life expectancy | 85 |
| Target retirement income | $XX,000/yr |
| Monthly contribution | $X,000 |
| Accumulation return | 7% pa |
| Withdrawal phase return | 5% pa |
| Inflation | 3% pa |
| Expense ratio | 0.2% pa |
| FX rate (USD→base) | update `references/fx_rates.json` after each refresh |

---

## Statement sources

**Input folder:** `~/Finance/Statements/`

### Balance / holdings files — ingested by both skills

| File | Platform | Owner | Type | Notes |
|---|---|---|---|---|
| `[broker]_statement.pdf` | [Broker name] | you/partner/joint | investments | |
| `[super]_statement.pdf` | [Super/pension fund] | you | super | |
| `[bank]_savings.pdf` | [Bank] | you | savings | |
| `[crypto]_portfolio.pdf` | [Exchange] | you | crypto | USD if non-base |
| `[partner]_balance.rtf` | [Bank] | partner | savings | RTF placeholder — approx |

### Transaction CSVs — cost basis only, not corpus

| File | Platform | Owner | Covers |
|---|---|---|---|
| `[broker]_transactions.csv` | [Broker] | [owner] | Full history |
| `[exchange]_trades.csv` | [Exchange] | [owner] | Full history |

### Excluded files

List superseded or duplicate statements in `references/exclusions.json`:
```json
{
  "excluded": {
    "old_statement_2024.pdf": "Superseded by 2025 annual statement."
  }
}
```

---

## Last known corpus

Update this block after every refresh run.

```
Date:              [YYYY-MM-DD]
Total corpus:      [currency] $X,XXX,XXX
FX rate:           1 USD = X.XXXX [base currency]
Contributions:     [currency] $X,000/mo

Corpus needed:     [currency] $X,XXX,XXX  ([active scenario], [FIRE year])
Projected:         [currency] $X,XXX,XXX
Surplus/shortfall: [currency] ±$XXX,XXX

Scenario sweep:
  [base]          ✅/⚠️  ±$XXX,XXX
  [lean]          ✅/⚠️  ±$XXX,XXX
  [fat]           ✅/⚠️  ±$XXX,XXX
  [conservative]  ✅/⚠️  ±$XXX,XXX
```
