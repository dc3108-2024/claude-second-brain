# PRD — Audio Interview to PM Cycle Bridge

## Executive Summary

The Audio Interview to PM Cycle Bridge closes the gap between verbal requirements
capture and structured PM artefacts. A PM records a stakeholder interview, and the
pipeline automatically transcribes, distils, and routes the requirements into the
jira-pm OPEN flow — producing a Confluence PRD and JIRA epic with stories, with a
single human approval gate in between. The pipeline is project-agnostic by design.

---

## Problem Statement

Verbal requirements capture is the most natural way to gather stakeholder needs —
especially in informal, conversational settings where a structured form would feel
clinical and produce shallower answers. But the moment the recording ends, the
workflow breaks down.

**Current reality:**

1. The PM records the interview on their phone Voice Memos
2. Must replay the recording manually (often at 1.5× speed)
3. Must mentally filter out their own questions, filler words, tangents
4. Must hand-type distilled notes into a document or directly into `prd_drafter.py`
5. Only then can the PM cycle begin

This manual middle step is slow (typically 2–3× the recording length), lossy
(nuance is dropped under cognitive load), and creates enough friction that PMs
either skip audio capture entirely or delay starting the PM cycle by hours or days.

**Result:** valuable stakeholder insight gets stranded in a recordings folder and
never reaches the backlog.

---

## Personas

| Persona | Role in pipeline |
|---|---|
| PM / Product Owner | Records the interview, reviews the Slack distillation, approves to trigger the PM cycle. Owns the quality of the output. |
| Stakeholder / Business Owner | Speaks the requirements during the interview. No direct interaction with the pipeline — their input arrives as audio. |

---

## Pipeline (How It Works)

```
Voice recording (only manual step: drop file to watch folder)
│
▼
Watch folder daemon ← always-on background process, polls every 30s
│
▼
Whisper transcription → transcript.txt (fully local, no network call)
│
▼
Claude distillation ← call_claude_with_critique()
│  drops: interviewer questions, filler, repetition
│  keeps: stakeholder requirements in their own language
│  flags: [AMBIGUOUS] items for PM review
▼
Slack HITL gate
│  PM sees: distilled requirements + routing confidence + rationale
│  PM replies: yes | edit <revised text> | skip
▼
prd_drafter.py → jira-pm OPEN flow
│
▼
Confluence PRD → JIRA Epic → User Stories (with AC + dependency links)
```

---

## Features

### F1 — Watch-Folder Daemon

Monitors a watch folder for new `.m4a` files. Runs as a launchd (Mac) or systemd
(Linux) agent. Manifest-based delta processing — skips already-processed files.

---

### F2 — Whisper Transcription

Local transcription via OpenAI Whisper (model: `small`). No network call, no cloud
dependency. Falls back to `base` model if `small` is unavailable.

---

### F3 — Claude Distillation

The intellectually significant step. Reads the raw transcript and produces structured
sound bytes:

- Drops all interviewer-side questions and comments
- Removes filler phrases, false starts, repetition
- Consolidates semantically duplicate points
- Preserves the stakeholder's original framing and vocabulary
- Flags ambiguous or contradictory requirements with `[AMBIGUOUS]`

**Output schema:**

```json
{
  "sound_bytes": "...",
  "flags": [],
  "recording_label": "..."
}
```

---

### F4 — Slack HITL Gate

Example Slack message:

```
🎙️ New interview processed: project-requirements-interview.m4a

Distilled requirements:
• Requirement 1 captured in stakeholder's own words
• Requirement 2 — specific constraint noted
• [AMBIGUOUS] unclear reference — flagged for PM review

Routing: PROJECT_A [high confidence] — content matches project scope

Reply ✅ yes | ✏️ edit <revised text> | ⏭️ skip
```

---

### F5 — Smart Project Routing (via `router.py`)

Claude classifier reads the distilled sound bytes and matches them against project
descriptions in `routing_config.json`. Returns:

- Best-matching project
- Confidence level: `high` / `medium` / `low`
- One-sentence rationale

Confidence and rationale surface in the Slack message so the PM can verify or
override. Graceful fallback to filename prefix if classifier fails.

---

### F6 — PM Cycle Trigger

On approval, sound bytes are passed to `prd_drafter.py`. The existing jira-pm OPEN
flow takes over unchanged. The bridge adds zero new steps downstream — it provides
higher-quality, lower-friction input.

---

## Success Metrics

| Metric | Target |
|---|---|
| Manual steps between recording and Slack review post | Zero |
| Filler / interviewer-question lines in distilled output | Zero |
| End-to-end time: recording lands → Slack post | Under 5 minutes (15–40 min interview) |
| PM approval actions per recording | Exactly one |
| Daemon uptime | 99%+ (restart-on-crash) |

---

## Out of Scope

- Real-time / live transcription
- Speaker diarisation
- Auto-firing without HITL (PM approval gate is non-negotiable)
- Non-English transcription (v1)
- Audio sources beyond local file drop (Zoom, WhatsApp in v1)

---

## Design Decisions

| Decision | Rationale |
|---|---|
| Distillation output: JSON | Enables `[AMBIGUOUS]` flagging and structured Slack formatting |
| Routing: content-based (Claude classifier) with filename prefix fallback | Robust to naming conventions; degrades gracefully |
| Daemon: launchd/systemd | Persistent, restarts on crash |
| Whisper model: `small` | Best accuracy/speed tradeoff for 15–40 min interviews |
| Multi-recording queue: sequential | Avoids Slack message collisions |
| HITL: unconditional | No auto-fire path exists by design |

---

## AI PM Showcase Value

This feature demonstrates an end-to-end agentic PM workflow that most AI PM
candidates only describe theoretically:

**Discovery → artefacts in minutes.** Collapses the gap between stakeholder
conversation and structured backlog. The pipeline moves in under 5 minutes; the
PM reviews, approves, and has a live Confluence PRD before the stakeholder's
follow-up email arrives.

**Intelligent filtering, not just transcription.** The distillation step encodes
PM judgement in a prompt. Knowing what to keep is as important as capturing
everything. The PM defines what "distilled requirements" means; Claude executes it
consistently at scale.

**HITL by design.** The approval gate is a deliberate architectural choice, not an
afterthought. The PM remains accountable for what enters the backlog. Automating
past this gate would automate the wrong thing.

**Built on real infrastructure.** Voice Memos, Whisper, Slack, JIRA, Confluence.
No mocks. No simulated runs. The PRD you are reading was produced by the same
pipeline it describes.

---

## Setup

```bash
# 1. Install dependencies
pip install openai-whisper
brew install ffmpeg

# 2. Configure routing
# Edit skills/audio-interview-bridge/references/routing_config.json
# Add your JIRA project descriptions — the router uses these to classify recordings

# 3. Wire up the daemon
# Mac: use the launchd plist in skills/audio-interview-bridge/references/
# Linux: use the systemd unit equivalent

# 4. Ensure mcp-atlassian is connected
# Confluence + JIRA credentials configured in ~/.config/mcp-atlassian/
```

**Dependencies:**
- Slack bot (Socket Mode) — see `skills/audio-interview-bridge/references/routing_config.json.example`
- Confluence + JIRA via `mcp-atlassian`
- `jira-pm` skill (provides the OPEN flow downstream)

---

## See Also

The audio bridge covers the pipeline up to JIRA story creation. For the full lifecycle —
BUILD (story → In Progress → implementation plan), CLOSE (Done → PR → PRD updated),
and BRIDGE (auto-close from branch name) — see the
[PM Pipeline Runbook](../pm-pipeline-runbook.md).
