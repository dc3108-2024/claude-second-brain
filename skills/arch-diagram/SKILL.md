---
name: arch-diagram
description: >
  Generate or update the architecture PDFs for the Personal AI Operating System (private)
  and the Claude Code Second Brain scaffold (public). Injects live stats, exports PNGs,
  embeds images in both repo READMEs, commits and pushes. Scheduled weekly (Saturday 10am).
  Triggers: "update architecture PDFs", "regenerate architecture", "refresh arch diagram",
  "rebuild architecture", "update arch diagrams".
---

# Arch Diagram Skill

Produces two executive-framed architecture PDFs, exports PNGs, embeds them in both repo
READMEs, and pushes. Runs end-to-end via a single script.

## Step 0 — Read config

Read `references/config.md`. Note output locations and README embed paths.

## Step 1 — Run the all-in-one script

```bash
python3 ~/.claude/skills/arch-diagram/scripts/run_all.py
```

This script:
1. Queries live stats (KB count, skill count, lattice connections) at runtime
2. Generates the personal PDF (`build_personal.py`) → saves to Desktop + skills docs/
3. Generates the public PDF (`build_public.py`) → saves to Desktop + public repo docs/
4. Exports both PDFs as PNG using PyMuPDF (144 dpi)
5. Copies assets into the correct `docs/` folders in each repo
6. Updates the skills README (inserts arch block via `update_skills_readme_header`)
7. Regenerates the full skills README via `generate-readme.py`
8. Updates the public repo README (inserts arch block before "What's in this repo")
9. Git commits and pushes both repos
10. Opens both PDFs on Desktop

## Step 2 — Report

```
Architecture PDFs updated — YYYY-MM-DD
Personal: personal-ai-os-architecture-YYYY-MM-DD.pdf  |  PNG: OK
Public:   second-brain-scaffold-architecture-YYYY-MM-DD.pdf  |  PNG: OK
READMEs: skills README + public README updated and pushed.
```

If PNG export or git push fails, report the error but do not abort.

## Error handling

- `ImportError` on fitz → `pip3 install pymupdf`, retry
- `SCRIPT_ERROR` → read the traceback, fix the specific line in run_all.py, retry
- `GIT_PUSH_FAILED` → log to skill_error_log.md, continue (PDFs are still saved)

## Weekly schedule

Cron: `0 10 * * 6`  (Saturday 10:00 AM)
Command: `python3 ~/.claude/skills/arch-diagram/scripts/run_all.py >> ~/Desktop/Second_Brain_Docs/arch-diagram-cron.log 2>&1`

To install:
```bash
(crontab -l 2>/dev/null; echo "0 10 * * 6 python3 ~/.claude/skills/arch-diagram/scripts/run_all.py >> ~/Desktop/Second_Brain_Docs/arch-diagram-cron.log 2>&1") | crontab -
```

---

## Monitoring

At the end of every successful run, execute:

```bash
python3 ~/.claude/monitor/monitor.py --log '{"skill":"arch-diagram","est_input_tokens":5000,"est_output_tokens":1200,"steps_taken":7,"outputs_written":1,"success":true,"model":"claude-sonnet-4-6","model_tier":"balanced","model_verdict":"appropriate"}'
```

<!-- MONITOR_BLOCK -->
