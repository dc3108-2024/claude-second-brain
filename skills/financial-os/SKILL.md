---
name: financial-os
description: Triggers when the user asks about FIRE status, retirement readiness, corpus tracking, net worth, or ingesting statements for retirement math. Triggers on: "what's my FIRE status", "run financial OS", "how am I tracking", "update my corpus", "ingest my statements", "am I on track for my target year", "what's my net worth", "run the numbers". Skip when the user only wants the Excel workbook rebuilt or raw statement extraction — use portfolio-refresh instead.
---

# Financial OS

Personal financial intelligence layer. Ingests statements from all platforms, normalises to a single corpus figure, and runs retirement math against the FIRE target.

**Configuration:** FIRE scenarios, statement sources, retirement assumptions, and last known corpus are in `references/financial-config.md`. Update that file — not this one — when accounts or targets change.

## Persona
Read `~/.claude/persona.json`. Use these values throughout — never hardcode them:
- `relocation.brief_label` — transition label, e.g. "AU→NL"
- `relocation.departure_date` — departure date, e.g. "2026-09-01"
- `tax.au_marginal_rate` — AU marginal tax rate, e.g. 0.37

## How to invoke this skill

Say any of these phrases to Claude Code:

| Use case | What to say | What runs |
|---|---|---|
| Check FIRE status instantly (no API calls) | `"FIRE status"` / `"am I on track"` / `"run the numbers"` | `run.py --no-ingest --all-scenarios` |
| Ingest new statements + recalculate | `"update my corpus"` / `"ingest my statements"` | `run.py --all-scenarios` |
| Run a specific scenario | `"run the conservative scenario"` | `run.py --no-ingest --scenario conservative` |
| Compare all scenarios side by side | `"compare all scenarios"` | `run.py --no-ingest --all-scenarios` |
| Interactive: change scenario, see yearly buildup | `"open financial CLI"` | `cli.py` |
| Portfolio intelligence pointers | `"portfolio pointers"` | `python3 -m intelligence.pointers` |
| Hide figures for screen sharing | `"run in demo mode"` | `run.py --no-ingest --all-scenarios --demo` |
| Force re-parse all statements | `"force full ingest"` | `run.py --all-scenarios --force` |

**Also triggers automatically:** when any file is dropped into your configured statements folder (set in `references/financial-config.md`) — launchd fires `run.py --all-scenarios` and sends a macOS notification.

**Skip this skill** when the user only wants the Excel workbook rebuilt — use `portfolio-refresh` instead.

---

## Component reuse

This skill owns most of the pipeline. One script is shared with `portfolio-refresh` via CLI.

| Component | This skill | Other skill |
|---|---|---|
| `ingestion/statement_manifest.py` | OWNS — Python API used internally | `portfolio-refresh` CALLS via CLI (`list-changed`, `mark-processed`) |
| `intelligence/transform.py` | OWNS — auto-called after ingest | `portfolio-refresh` triggers manually after its run |
| `references/financial-config.md` | OWNS — scenario snapshot + file map | `portfolio-refresh` READS for platform map + paths |
| `references/exclusions.json` | OWNS — skip list | `portfolio-refresh` READS before extracting |
| `portfolio_data.json` (runtime) | WRITES via `ingest.py` | `portfolio-refresh` also WRITES (same schema) |
| `statement_manifest.json` (runtime) | WRITES via `ingest.py` | `portfolio-refresh` READS + WRITES |

---

## Scripts

All scripts live in `~/.claude/skills/financial-os/scripts/`. Run from that directory so package imports resolve.

```bash
SCRIPTS=~/.claude/skills/financial-os/scripts
```

| Command | What it does |
|---|---|
| `python3 $SCRIPTS/cli.py` | **Interactive CLI** — prompts, updates lifestyle.json, calculates |
| `python3 $SCRIPTS/run.py` | Non-interactive: ingest + calculate (active scenario) |
| `python3 $SCRIPTS/run.py --no-ingest` | Non-interactive: recalculate only (fast) |
| `python3 $SCRIPTS/run.py --all-scenarios` | Compare all scenarios side by side |
| `python3 $SCRIPTS/run.py --scenario india_tier2` | Run one specific scenario |
| `python3 $SCRIPTS/run.py --source /path/` | Ingest from a custom folder |
| `python3 $SCRIPTS/run.py --demo` | Redact corpus/projections — safe to share screen |

**Must run from `$SCRIPTS` directory** (or set `PYTHONPATH=$SCRIPTS`) so `from ingestion.ingest import ...` resolves.

**Default:** use `cli.py` for conversational use. Use `run.py` for scripting or quick checks.

## Lifestyle Inputs

All retirement assumptions live in `~/[YourProjectFolder]/data/lifestyle.json`. Edit the file or ask Claude to update it.

**To change the active scenario:** edit `"active_scenario"` in lifestyle.json, then run `--no-ingest`.

**To change an assumption** (e.g. income target, FIRE year, return rate): edit the relevant scenario's fields in lifestyle.json.

**To add a custom scenario:** add a new entry under `"scenarios"` following the same structure.

### Built-in scenarios

See `references/financial-config.md` for the full scenario table and active scenario key.

### Scenario fields

```json
{
  "label": "Display name",
  "description": "One-line description",
  "target_yearly_income_aud": 80000,
  "retirement_year": 2036,
  "life_expectancy": 85,
  "monthly_contribution_aud": 8000,
  "accumulation_return": 0.07,
  "retirement_return": 0.05,
  "inflation_rate": 0.03,
  "expense_ratio": 0.002
}
```

## Data

Runtime data stays in `~/[YourProjectFolder]/data/` — not in the skill folder.

| File | Contents |
|---|---|
| `~/[YourProjectFolder]/data/portfolio.json` | Normalised holdings, per-account values, corpus summary |
| `~/[YourProjectFolder]/data/profile.json` | Personal config: ages, income, retirement targets |
| `~/[StatementsFolder]/` | Source statements (canonical input folder — set in financial-config.md) |

## Statement Sources

See `references/financial-config.md` for the full statement file list and input folder path.

To add a new statement: drop any PDF/XLSX/CSV into the source folder and run `python3 $SCRIPTS/run.py`.

## Retirement Assumptions

See `references/financial-config.md` for the full assumptions table.

To change assumptions: edit the relevant scenario fields in `~/[YourProjectFolder]/data/lifestyle.json`, then run `--no-ingest`. Update `references/financial-config.md` snapshot after any material change.

## Last Known Output

See `references/financial-config.md` for the most recent corpus snapshot. Update it after every refresh run.

## How the Pipeline Works

1. `ingestion/statement_manifest.py` fingerprints each file — skips unchanged, processes new/modified only
2. Transaction CSVs are routed to `intelligence/parse_transactions.py` → `cost_basis_map` (in-memory)
3. Balance files: `ingestion/extract.py` → plain text; `ingestion/parse.py` (via `claude -p`) → rich schema JSON (platform, owner, account_id, period, currency, summary.closing, holdings[])
4. `ingestion/ingest.py` deduplicates and delta-merges into `~/[YourProjectFolder]/portfolio_data.json`
5. `run.py._auto_transform()` persists cost basis to `cost_basis_map.json`, then runs `intelligence/transform.py` → `~/[YourProjectFolder]/data/portfolio.json` (enriched schema with FX conversion and per-holding cost basis)
6. `calculations/retirement.py` reads `data/portfolio.json` summary total → runs FIRE math
7. `intelligence/pointers.py` reads `data/portfolio.json` + KB entries → 3–5 actionable portfolio pointers

## When to Run Ingest vs No-Ingest

- New statements dropped in source folder → `run.py` (full ingest)
- Just want to check FIRE status → `run.py --no-ingest` (instant, no API calls)
- Changed retirement assumptions → `run.py --no-ingest`
- Sharing screen / demoing → add `--demo` to any command

## Dependencies

- `claude` CLI (for `ingestion/parse.py` and `intelligence/` modules)
- `openpyxl`, `pdfplumber`, `striprtf` (for extraction)
- `anthropic` SDK (optional, if switching away from CLI invocation)
