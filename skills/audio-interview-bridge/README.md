# Audio Interview Bridge

Convert a voice recording of a stakeholder interview into a full PM backlog entry — without manual note-taking.

Drop a `.m4a` file. Get a Confluence PRD, a JIRA epic, and user stories with acceptance criteria. The only manual step is dropping the file and approving via Slack.

---

## How it works

```
┌─────────────────────────────────────────────────────────────────┐
│                  Audio Interview Bridge                         │
│              Voice → Structured PM Backlog                      │
└─────────────────────────────────────────────────────────────────┘

  [Voice Recording]
        │  file drop to watch folder (only manual step)
        ▼
  [Watch Folder Daemon]  ← launchd / systemd, polls every 30s
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
  [prd_drafter.py]  ← Claude: structured PRD JSON
        │
        ├── Confluence page created  (PRD — feature_name)
        ├── JIRA epic created        (feature_name, linked to PRD)
        └── JIRA stories created    (with AC + dependency links)
```

---

## Trigger phrases

- `"process interview recording"`
- `"bridge this voice memo"`
- `"run audio bridge"`
- Drop a `.m4a` file into the watch folder (daemon mode)

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Full workflow documentation |
| `scripts/audio_bridge.py` | Watch daemon — poll loop + orchestration |
| `scripts/distil.py` | Claude: transcript → sound bytes |
| `scripts/router.py` | Claude: sound bytes → JIRA project |
| `references/routing_config.json` | Watch folder, Whisper settings, project routing table |

---

## Prerequisites / setup

```bash
# 1. Install Whisper and ffmpeg
pip install openai-whisper
brew install ffmpeg

# 2. Configure routing_config.json
#    Set voice_memos_path, whisper_model, and your JIRA project descriptions

# 3. Configure Slack webhook
#    Set up ~/.claude/skills/shared/slack_config.json with your bot token

# 4. The skill depends on jira-pm/scripts/prd_drafter.py for the final step
#    Install the jira-pm skill alongside this one

# 5. Run the daemon
python3 ~/.claude/skills/audio-interview-bridge/scripts/audio_bridge.py
```

### macOS launchd

Create `~/Library/LaunchAgents/com.yourname.audio-bridge.plist` and load with:
```bash
launchctl load ~/Library/LaunchAgents/com.yourname.audio-bridge.plist
```

---

## Slack HITL commands

After distillation, the daemon posts a summary to Slack. Reply:

| Command | Action |
|---|---|
| `yes` | Approve requirements as-is, trigger PRD creation |
| `edit <new text>` | Replace requirements with your edit, then trigger |
| `skip` | Archive the recording, take no action |

---

## See Also

The bridge delivers requirements into the PM pipeline. For the full lifecycle from
that point — PRD creation, JIRA epic, BUILD, CLOSE, and BRIDGE auto-close — see the
[PM Pipeline Runbook](../../docs/pm-pipeline-runbook.md).

---

## Customising the router

Edit `references/routing_config.json` — add a description for each JIRA project that tells Claude what kinds of interviews belong there. The router uses these descriptions for semantic matching, not keyword rules.

```json
{
  "smart_routes": [
    {
      "jira_project": "MYPROJECT",
      "confluence_space": "my-space",
      "slack_channel": "#my-channel",
      "description": "What kinds of topics belong in this project — described naturally"
    }
  ]
}
```
