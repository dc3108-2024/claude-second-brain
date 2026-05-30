# Financial OS — Scaffold

> A production-grade personal financial intelligence system built on Claude Code.
> Drop a bank statement. Get your FIRE status.

This is the scaffold for building a multi-skill financial operating system that:

- Ingests investment statements from any institution (PDF, Excel, CSV, RTF)
- Tracks corpus across all accounts with delta processing (only re-parses changed files)
- Runs retirement projections against multiple scenarios (FIRE math)
- Enriches holdings with cost basis and CGT eligibility from transaction history
- Surfaces portfolio intelligence by cross-referencing your knowledge base
- Fires automatically when new statements land (launchd WatchPaths)

---

## Architecture: three skills, one data flow

```
Statements (PDF / Excel / CSV / RTF)
        │
        ├── Balance files ──────────────────────────┐
        │                                           │
        │   [portfolio-refresh skill]               │   [financial-os skill]
        │     Manifest check (skip unchanged)       │     Manifest check (skip unchanged)
        │     extract_pdf.py / extract_excel.py     │     parse_transactions.py → cost basis
        │     Claude in-context → normalise         │     parse.py (claude -p) → normalise
        │     build_workbook.py → Excel             │     _auto_transform() → enrich
        │                                           │     retirement.py → FIRE math
        └── Transaction CSVs ──────────────────────►┘
                                │
                       portfolio_data.json          ← shared handoff (rich schema)
                                │
                        data/portfolio.json         ← enriched, FX-converted
                       /                \
               FIRE math            portfolio pointers
              (retirement.py)        (KB × portfolio)

financial-pdf-consolidator is a script library — portfolio-refresh calls its scripts.
```

**Key design decisions:**
- `portfolio_data.json` is the handoff between skills — both write the same rich schema
- `statement_manifest.json` prevents re-parsing unchanged files (saves Claude API calls)
- FX rates and platform mappings live in `references/` — not hardcoded in scripts
- `data/portfolio.json` is the single source of truth for FIRE math and intelligence

---

## What to build

This scaffold gives you the skill definitions and config templates. You need to build (or fork from the reference implementation):

| Component | What it does | Language |
|---|---|---|
| `ingestion/extract.py` | PDF/XLSX/CSV/RTF → plain text | Python (pdfplumber, openpyxl) |
| `ingestion/parse.py` | Text → rich schema JSON via `claude -p` | Python + Claude CLI |
| `ingestion/ingest.py` | Orchestrate: manifest → extract → parse → merge | Python |
| `ingestion/statement_manifest.py` | Delta fingerprinting by mtime + size | Python |
| `intelligence/parse_transactions.py` | Transaction CSVs → cost_basis_map | Python |
| `intelligence/transform.py` | portfolio_data.json → data/portfolio.json | Python |
| `intelligence/pointers.py` | KB × portfolio → optimisation actions | Python + Claude CLI |
| `calculations/retirement.py` | SWR FIRE math (corpus needed, projected, gap) | Python |
| `run.py` | Main entry point orchestrating all of the above | Python |
| `cli.py` | Interactive scenario explorer | Python |

**Reference implementation:** see the private `claude-skills` repo, `financial-os/scripts/`.

---

## Adapting the scaffold

### 1 — Fill in `references/financial-config.md`

This is the only file that contains personal data. Everything else is generic workflow.
In the scaffold this is named `references/config.md` — rename it to `financial-config.md`
so it matches the naming convention used by both `financial-os` and `portfolio-refresh`.

Key fields to set:
- `input_folder` — where your statements live
- `platforms` — your actual accounts and institutions
- `goal_corpus` / `annual_spend` / `withdrawal_rate` — your FIRE parameters
- `scenarios` — your retirement scenarios (location, income target, FIRE year)

### 2 — Fill in `references/platform_map.json`

Maps platform name → account type. Controls how `transform.py` categorises each account.

```json
{
  "Vanguard": "investments",
  "Fidelity 401k": "super",
  "Chase Savings": "savings",
  "Coinbase": "crypto"
}
```

### 3 — Fill in `references/fx_rates.json`

Fallback FX rates for non-base-currency accounts. Used when `data/portfolio.json` meta doesn't have a stored rate.

```json
{
  "USD": 1.0,
  "EUR": 1.08,
  "GBP": 1.27,
  "last_updated": "YYYY-MM-DD"
}
```

### 4 — Build the scripts

Follow the patterns:
- All scripts read config from `references/` — never hardcode paths, rates, or names
- `call_claude()` and `parse_json_response()` live in `utils.py` — all Claude calls go through there
- `deserialise_cost_basis_map()` / `serialise_cost_basis_map()` also in `utils.py` — JSON↔tuple key conversion
- Tests live in `scripts/tests/` — run with `pytest scripts/`

### 5 — Set up automation (optional)

Two launchd agents:
- `ingest_on_change.sh` — WatchPaths trigger on your statements folder → runs `run.py --all-scenarios`
- `weekly_check.sh` — every Monday 08:00 → runs `--no-ingest` + portfolio intelligence

Both scripts reference `SCRIPTS=~/.claude/skills/financial-os/scripts` — your launchd plists point to these scripts, not to the data directory.

---

## The rich schema

Both skill paths write to `portfolio_data.json` using this schema (from `portfolio_schema.md` in `financial-pdf-consolidator`):

```json
{
  "platform":   "Vanguard",
  "owner":      "joint",
  "account_id": "****4974",
  "period":     "01 Jan 2024 – 30 Apr 2026",
  "currency":   "AUD",
  "notes":      "",
  "summary": {
    "opening":    0.00,
    "deposits":   50000.00,
    "earnings":   5000.00,
    "closing":    55000.00,
    "net_return": "10.00% p.a."
  },
  "holdings": [
    {
      "name":        "Vanguard Australian Shares Index",
      "asset_class": "Australian Shares",
      "units":       1234.57,
      "unit_price":  2.35,
      "value":       2901.24,
      "income":      123.45,
      "growth":      456.78
    }
  ]
}
```

`transform.py` reads `summary.closing` as the corpus value per account. FX conversion (`USD → base currency`) happens here, not in `parse.py`.

---

## Key patterns worth copying

**Delta manifest** — never re-parse unchanged files:
```python
# statement_manifest.py exposes a CLI:
python3 statement_manifest.py --list-changed ~/Finance/Statements/
# → ["new_statement.pdf", "updated_holdings.csv"]
# Both financial-os and portfolio-refresh call this — one implementation
```

**Externalised config** — nothing hardcoded in scripts:
```
references/platform_map.json   ← platform → account_type
references/fx_rates.json       ← fallback FX rates
references/exclusions.json     ← files to skip in both skill paths
data/profile.json              ← owner age (used by retirement.py)
data/lifestyle.json            ← FIRE scenarios
```

**Shared utils** — one place for all Claude call patterns:
```python
from intelligence.utils import call_claude, parse_json_response
from intelligence.utils import deserialise_cost_basis_map, serialise_cost_basis_map
from intelligence.utils import load_current_age
```

---

## Extending

| Extension | What to add |
|---|---|
| Tax module | Step that estimates CGT and income tax per jurisdiction |
| Budget view | Parses transaction CSVs for spending categories vs plan |
| Net worth tracker | Appends corpus snapshot to a longitudinal log after each run |
| PDF report | Formats FIRE output as a PDF brief saved to Desktop |
| Multi-currency | Extend `fx_rates.json` and `transform.py` for EUR, GBP, etc. |
