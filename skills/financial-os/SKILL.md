---
name: financial-os
description: >
  Personal financial operating system. Ingests investment statements, tracks
  corpus across all accounts, runs FIRE retirement projections, and surfaces
  portfolio intelligence. Triggers on: "what's my FIRE status", "run the
  numbers", "update my corpus", "am I on track", "ingest my statements",
  "portfolio pointers", "financial update". Skip if the user only wants the
  Excel workbook rebuilt — use portfolio-refresh instead.
---

# Financial OS

Personal financial intelligence layer. Ingests statements from all platforms,
normalises to a single corpus figure, and runs retirement math against your
configured FIRE scenarios.

**Configuration:** all persona-specific data is in `references/`. The scripts
never hardcode paths, rates, or personal details.

---

## Triggers

| What the user says | What to run |
|---|---|
| "FIRE status" / "run the numbers" / "am I on track" | `run.py --no-ingest --all-scenarios` — instant, no API calls |
| "Update corpus" / "ingest statements" / file dropped | `run.py --all-scenarios` — full ingest + FIRE sweep |
| "Portfolio pointers" | `python3 -m intelligence.pointers` |
| "Compare scenarios" | `run.py --no-ingest --all-scenarios` |
| Specific scenario | `run.py --no-ingest --scenario <key>` |

---

## Scripts

All scripts live in `~/.claude/skills/financial-os/scripts/`. Always `cd` there first.

```bash
SCRIPTS=~/.claude/skills/financial-os/scripts

# FIRE status — instant (no API)
cd $SCRIPTS && python3 run.py --no-ingest --all-scenarios

# Full ingest — picks up new/changed statements
cd $SCRIPTS && python3 run.py --all-scenarios

# Interactive CLI — change scenario, see yearly buildup
cd $SCRIPTS && python3 cli.py

# Demo mode — hides all figures (safe to share screen)
cd $SCRIPTS && python3 run.py --no-ingest --all-scenarios --demo

# Portfolio intelligence pointers
cd $SCRIPTS && python3 -m intelligence.pointers
```

---

## How the pipeline works

1. `statement_manifest.py` — fingerprint every file; skip unchanged
2. `parse_transactions.py` — transaction CSVs → cost basis (no Claude call)
3. `extract.py` + `parse.py` — balance files → `claude -p` → rich schema JSON
4. `ingest.py` — delta-merge into `portfolio_data.json`
5. `_auto_transform()` in `run.py` — persist cost basis + run `transform.py` → `data/portfolio.json`
6. `retirement.py` — SWR FIRE math per scenario
7. `pointers.py` — cross-reference KB × portfolio (run manually)

---

## Configuration files (in `references/`)

| File | What it controls |
|---|---|
| `financial-config.md` | Snapshot of scenarios, statement sources, last known corpus |
| `platform_map.json` | Platform name → account_type mapping (loaded by transform.py) |
| `fx_rates.json` | Fallback FX rates when data/portfolio.json meta is missing |
| `exclusions.json` | Statement files to skip in both skill paths |

Update `references/` — never edit SKILL.md for data changes.

---

## When to run ingest vs no-ingest

- New statements dropped → `run.py --all-scenarios` (ingest + FIRE)
- Just checking status → `run.py --no-ingest` (instant, free)
- Changed a scenario assumption → `run.py --no-ingest`
- Screen sharing / demo → add `--demo` to any command

---

## Last known corpus

See `references/financial-config.md` for the most recent snapshot.
Update it after every refresh run.
