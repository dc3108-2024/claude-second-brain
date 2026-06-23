# PRD — Smart Content-Based Routing for Multi-Project PMs

## Executive Summary

A Claude classifier reads the distilled content of any voice recording and routes
it to the correct JIRA project — not by filename convention, but by understanding
what the content is about. Confidence and rationale surface in the Slack HITL
message so the PM can verify before approving.

---

## Problem Statement

Multi-project PMs and POs capture voice recordings across multiple active
workstreams. Without smart routing, every recording needs to be manually tagged or
renamed with a project prefix. This creates friction — especially when capturing
on the go.

Prefix-based routing is fragile: forget the prefix and the recording lands in the
wrong project or defaults to a fallback regardless of content. The cost is either
a misrouted PRD (which must be corrected downstream) or a recording left unprocessed
because the PM doesn't trust the routing.

---

## Persona

**Senior PM/PO managing 3+ concurrent projects** from a single audio capture
workflow. Needs routing to be invisible when it works and transparent when it doesn't.

---

## Features

### F1 — Content-Based Classification

- Claude classifier reads the distilled sound bytes produced by the transcription
  and distillation steps
- Matches content against project descriptions in `routing_config.json`
- Returns: best-matching project + confidence level (`high` / `medium` / `low`) +
  one-sentence rationale
- Confidence and rationale surface in the Slack HITL message — PM can verify or
  override before PRD creation proceeds

### F2 — Graceful Degradation

- Falls back to filename prefix-based routing if the classifier fails
- Pipeline never crashes on a routing failure — the fallback is always available
- Classifier failure is logged; PM is notified in the Slack message

### F3 — Config-Driven Project Registry

- New projects added by editing `routing_config.json` — no code change required
- Each project entry: name, JIRA key, Confluence space, and a plain-language
  description (1–3 sentences) that the classifier uses for matching
- The description quality determines routing accuracy — better descriptions = better routing

---

## Success Metrics

| Metric | Target |
|---|---|
| Zero filename convention errors | Recordings route correctly without any naming discipline |
| Routing accuracy | ≥ 85% (measured by rate of PM overrides in HITL step) |
| Latency added per recording | ≤ 5 seconds for classification |
| Graceful fallback confirmed | Pipeline continues on classifier failure |

---

## Out of Scope

- Multi-project routing (one recording → multiple projects simultaneously)
- Learning from PM overrides to improve future routing
- Routing based on acoustic features (speaker identity, tone, room)

---

## Implementation

**File:** `router.py` in `skills/audio-interview-bridge/scripts/`

**Pattern:**
- Uses `call_claude_with_critique()` — logged, instrumented, retry-on-failure
- Step registered in `step_map.json` for prompt health monitoring
- `routing_config.json` is the single source of truth for project descriptions
  and route metadata

**Config structure:**

```json
{
  "projects": [
    {
      "key": "PROJECT_A",
      "name": "Your first project name",
      "confluence_space": "your-space",
      "description": "Plain-language description of this project's scope — 1-3 sentences that clearly distinguish it from the others."
    },
    {
      "key": "PROJECT_B",
      "name": "Your second project name",
      "confluence_space": "your-space",
      "description": "Plain-language description of this project's scope."
    }
  ],
  "fallback": "prefix"
}
```

The classifier prompt instructs Claude to return structured JSON with `project_key`,
`confidence`, and `rationale` fields. The `parse_json_response()` utility handles
markdown-fenced output, which is common on brief inputs.

---

## How It Fits the Pipeline

This feature is a module within the `audio-interview-bridge` skill, not a standalone
skill. It sits between the Claude distillation step and the Slack HITL gate:

```
Claude distillation (sound bytes produced)
      │
      ▼
router.py — content-based classification
      │
      ▼
Slack HITL gate (routing confidence + rationale included in message)
      │
      ▼
PM approves → PRD creation proceeds in the correct project
```

The PM never sees a raw transcript or a classification API call. They see a Slack
message with distilled requirements, a routing decision, a confidence level, and
one sentence explaining why. That is the right level of visibility — enough to
catch errors, not enough to require effort on every run.

---

## See Also

This document covers the routing module only. For the full pipeline — from approval
through PRD creation, JIRA epic, BUILD, and CLOSE — see the
[PM Pipeline Runbook](../pm-pipeline-runbook.md).
