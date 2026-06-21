---
name: audio-interview-bridge
description: >
  End-to-end pipeline: voice memo → Whisper transcription → Claude distillation →
  AI-powered project routing → Slack HITL approval → Confluence PRD + JIRA epic + stories.
  Use this skill when you have a recorded stakeholder interview and want to convert it
  into structured PM artefacts automatically. Trigger on: "process interview recording",
  "bridge this voice memo", "run audio bridge", or when a new .m4a drops in the watch
  folder. Also runs as a daemon (always-on, polls every 30s).
---

# Audio Interview Bridge

Converts a voice recording of a stakeholder interview into a full PM backlog entry —
without manual note-taking. The only manual step is dropping the file into the watch folder.

---

## Pipeline overview

```
[Voice Recording]
      │  drop .m4a to watch folder
      ▼
[Watch Daemon]  ← polls every 30s, auto-drains ~/Downloads
      │
      ▼
[Whisper]  → transcript.txt → [Google Drive: Interview_Transcripts/]
      │
      ▼
[distil.py]  ← Claude: extract structured "sound bytes" + flags
      │         sound_bytes: ["need X", "pain point Y", "constraint Z"]
      ▼
[router.py]  ← Claude: classify to best JIRA project
      │         confidence: high/low + rationale
      ▼
[Slack HITL]  ← human reviews distilled requirements + routing
      │         reply: yes / edit <text> / skip
      ▼
[prd_drafter.py]  ← Claude: structured PRD JSON  (from jira-pm skill)
      │
      ├── Confluence page created  (PRD — feature_name)
      ├── JIRA epic created        (feature_name, linked to PRD)
      └── JIRA stories created    (with AC + dependency links)
```

---

## Running as a daemon

```bash
# Start watch daemon
python3 ~/.claude/skills/audio-interview-bridge/scripts/audio_bridge.py

# Or install via launchd (macOS) — runs on boot, restarts on failure
# Copy the provided plist to ~/Library/LaunchAgents/ and load it
```

The daemon:
- Polls the watch folder every 30s (configurable in `routing_config.json`)
- Auto-moves `.m4a` files from `~/Downloads` to the watch folder
- Processes one new recording per cycle (prevents queue flooding)
- Skips recordings already in the manifest

---

## Configuration

Edit `references/routing_config.json` to set:

| Key | Description |
|---|---|
| `voice_memos_path` | Watch folder for `.m4a` files |
| `whisper_model` | Model size: `tiny`, `small`, `base`, `medium`, `large` |
| `whisper_language` | Language code, e.g. `en` |
| `poll_interval_seconds` | How often to scan for new files |
| `smart_routes` | JIRA projects + descriptions used for AI routing |
| `default_route` | Fallback if routing fails |

---

## Slack HITL commands

After each recording is distilled, the daemon posts to Slack:

```
Reply to the bot:
  yes               — approve and trigger PRD creation
  edit <new text>   — replace requirements then trigger
  skip              — archive this recording, no action
```

The response is checked on the next poll cycle.

---

## State files (runtime — do not commit)

| File | Purpose |
|---|---|
| `references/manifest.json` | Per-recording status tracking |
| `references/pending_approval.json` | Current recording awaiting Slack approval |

---

## Prerequisites

```bash
# Whisper + ffmpeg
pip install openai-whisper
brew install ffmpeg

# Slack SDK (for channel ID resolution)
pip install slack-sdk

# Shared skill library
# The scripts import from ~/.claude/skills/shared/lib_claude.py
```

---

## Script reference

| Script | Purpose |
|---|---|
| `audio_bridge.py` | Main daemon — watch loop, orchestrator |
| `distil.py` | Claude: transcript → structured sound bytes |
| `router.py` | Claude: sound bytes → JIRA project classification |

PRD creation is handled by the `jira-pm` skill's `prd_drafter.py`.
