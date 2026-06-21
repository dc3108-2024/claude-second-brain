"""
audio_bridge.py — Watch-folder daemon: Voice Memos -> Whisper -> distil -> Slack HITL -> prd_drafter.

Run manually or via launchd/systemd:
    python3 audio_bridge.py

Pipeline stages per recording:
    detected -> transcribed -> distilled -> pending_approval -> triggered | skipped

Configuration: see references/routing_config.json
"""
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────────────────────
_SKILL_DIR    = Path.home() / ".claude/skills/audio-interview-bridge"
_REF_DIR      = _SKILL_DIR / "references"
_MANIFEST     = _REF_DIR / "manifest.json"
_PENDING      = _REF_DIR / "pending_approval.json"
_ROUTING_CFG  = _REF_DIR / "routing_config.json"
_SLACK_CFG    = Path.home() / ".claude/skills/shared/slack_config.json"
_DRIVE_UPLOAD = Path.home() / ".config/claude-drive/uploader.py"
_DRIVE_FOLDER_KEY = "interview_transcripts"
_DISTIL      = _SKILL_DIR / "scripts/distil.py"
_PRD_DRAFTER = Path.home() / ".claude/skills/jira-pm/scripts/prd_drafter.py"

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [audio-bridge] %(message)s",
    handlers=[
        logging.FileHandler(Path.home() / ".claude/monitor/logs/audio_bridge.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

def _load_routing() -> dict:
    return json.loads(_ROUTING_CFG.read_text())


def _load_manifest() -> dict:
    return json.loads(_MANIFEST.read_text()) if _MANIFEST.exists() else {}


def _save_manifest(m: dict) -> None:
    _MANIFEST.write_text(json.dumps(m, indent=2))


def _load_pending() -> dict:
    return json.loads(_PENDING.read_text()) if _PENDING.exists() else {}


def _save_pending(p: dict) -> None:
    _PENDING.write_text(json.dumps(p, indent=2))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Routing ───────────────────────────────────────────────────────────────────

def _route(filename: str, cfg: dict) -> dict:
    """Prefix-based fallback router. Used only when smart routing fails."""
    stem = filename.lower()
    for route in cfg.get("prefix_routes", []):
        if stem.startswith(route["prefix"]):
            return route
    return cfg["default_route"]


def _smart_route(distil_result: dict, recording_stem: str, cfg: dict) -> dict:
    """Classify distilled sound bytes to the best JIRA project via Claude."""
    _scripts = Path(__file__).parent
    if str(_scripts) not in sys.path:
        sys.path.insert(0, str(_scripts))
    try:
        from router import classify_route
        sound_bytes = distil_result.get("sound_bytes", [])
        label = distil_result.get("recording_label", recording_stem)
        result = classify_route(sound_bytes, label)
        log.info("Smart route: %s (confidence=%s) — %s",
                 result.get("jira_project"), result.get("confidence"), result.get("rationale"))
        return result
    except Exception as e:
        log.warning("Smart routing failed (%s) — falling back to prefix route", e)
        return _route(recording_stem, cfg)


# ── Stage 1: Transcription ─────────────────────────────────────────────────────

def _transcribe(m4a_path: Path, cfg: dict) -> Optional[Path]:
    """Run Whisper on the audio file. Returns path to .txt output or None on failure."""
    model    = cfg.get("whisper_model", "small")
    language = cfg.get("whisper_language", "en")
    out_dir  = m4a_path.parent

    log.info("Transcribing %s ...", m4a_path.name)
    try:
        r = subprocess.run(
            ["whisper", str(m4a_path),
             "--model", model, "--language", language,
             "--output_format", "txt", "--output_dir", str(out_dir)],
            capture_output=True, text=True, timeout=600,
        )
        txt_path = out_dir / (m4a_path.stem + ".txt")
        if txt_path.exists():
            log.info("Transcript written: %s", txt_path.name)
            return txt_path
        log.error("Whisper ran but no .txt found. stdout=%s stderr=%s", r.stdout[:200], r.stderr[:200])
        return None
    except FileNotFoundError:
        log.error("whisper not found — run: pip install openai-whisper && brew install ffmpeg")
        return None
    except subprocess.TimeoutExpired:
        log.error("Whisper timed out on %s", m4a_path.name)
        return None


# ── Stage 1.5: Google Drive upload ───────────────────────────────────────────

def _upload_to_drive(txt_path: Path) -> Optional[str]:
    """Upload transcript .txt to a Drive folder. Returns view URL or None."""
    try:
        import json as _json
        folders = _json.loads((_DRIVE_UPLOAD.parent / "fos_folders.json").read_text())
        folder_id = folders.get(_DRIVE_FOLDER_KEY)
        if not folder_id:
            log.warning("Drive folder_id for '%s' not found in fos_folders.json", _DRIVE_FOLDER_KEY)
            return None

        sys.path.insert(0, str(_DRIVE_UPLOAD.parent))
        from uploader import drive_upload
        url = drive_upload(txt_path, folder_id)
        log.info("Transcript uploaded to Drive: %s", url)
        return url
    except Exception as e:
        log.error("Drive upload failed: %s", e)
        return None


# ── Stage 2: Distillation ─────────────────────────────────────────────────────

def _distil(txt_path: Path) -> Optional[dict]:
    """Run distil.py on transcript. Returns result dict or None on failure."""
    log.info("Distilling %s ...", txt_path.name)
    try:
        r = subprocess.run(
            [sys.executable, str(_DISTIL), str(txt_path)],
            capture_output=True, text=True, timeout=120,
        )
        raw = r.stdout.strip()
        if not raw:
            log.error("distil.py returned no output. stderr=%s", r.stderr[:300])
            return None
        result = json.loads(raw)
        log.info("Distillation complete: %d sound bytes, %d flags",
                 len(result.get("sound_bytes", [])), len(result.get("flags", [])))
        return result
    except Exception as e:
        log.error("distil.py failed: %s", e)
        return None


# ── Stage 3: Slack HITL post ──────────────────────────────────────────────────

_POST_TO_SLACK = Path.home() / ".claude/skills/shared/post_to_slack.py"


def _post_slack_raw(text: str, cfg: dict) -> bool:
    """Post a raw text message via webhook. Returns True on success."""
    try:
        result = subprocess.run(
            [sys.executable, str(_POST_TO_SLACK)],
            input=text, capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            log.error("post_to_slack.py failed: %s", result.stderr[:200])
            return False
        return True
    except Exception as e:
        log.error("Slack post failed: %s", e)
        return False


def _post_for_approval(recording_path: str, distil_result: dict, route: dict, cfg: dict,
                       drive_url: Optional[str] = None) -> bool:
    """Post distilled requirements to Slack for review. Returns True on success."""
    sound_bytes = distil_result.get("sound_bytes", [])
    flags       = distil_result.get("flags", [])
    label       = distil_result.get("recording_label", Path(recording_path).stem)

    lines = [f"Audio Bridge — {label}", ""]

    if drive_url:
        lines += [f"Transcript: {drive_url}", ""]

    if sound_bytes:
        lines.append("Distilled requirements:")
        for i, sb in enumerate(sound_bytes, 1):
            lines.append(f"  {i}. {sb}")
    else:
        lines.append("(No requirements extracted — see flags below)")

    if flags:
        lines.append("")
        lines.append("Flags:")
        for f in flags:
            lines.append(f"  {f}")

    confidence = route.get("confidence", "")
    rationale  = route.get("rationale", "")
    lines += [
        "",
        f"Target: {route.get('jira_project', 'YOUR_PROJECT')} / {route.get('confluence_space', 'your-space')}"
        + (f"  [{confidence} confidence]" if confidence else ""),
        "",
        *(["Routing rationale: " + rationale] if rationale else []),
        "",
        "Reply to the bot:",
        "  yes               — approve and trigger PRD creation",
        "  edit <new text>   — replace requirements then trigger",
        "  skip              — archive this recording, no action",
    ]

    text = "\n".join(lines)
    ok = _post_slack_raw(text, cfg)
    if ok:
        log.info("Posted approval request for %s", label)
    return ok


# ── Stage 4: Check pending approval ──────────────────────────────────────────

def _check_pending_and_trigger() -> None:
    """If pending_approval.json has status=approved, trigger prd_drafter.py."""
    pending = _load_pending()
    if not pending or pending.get("status") not in ("approved", "skipped"):
        return

    status         = pending["status"]
    recording_path = pending.get("recording_path", "")
    stem           = Path(recording_path).stem

    manifest = _load_manifest()

    if status == "skipped":
        log.info("Recording %s skipped.", stem)
        manifest[stem]["status"] = "skipped"
        _save_manifest(manifest)
        _save_pending({})
        return

    # status == approved
    sound_bytes = pending.get("approved_sound_bytes", pending.get("sound_bytes", []))
    sb_text = " ".join(sound_bytes) if isinstance(sound_bytes, list) else str(sound_bytes)

    log.info("Approval received for %s — triggering prd_drafter.py ...", stem)
    try:
        subprocess.run(
            [sys.executable, str(_PRD_DRAFTER), sb_text],
            timeout=120,
        )
        manifest[stem]["status"] = "triggered"
        manifest[stem]["triggered_at"] = _now_iso()
    except Exception as e:
        log.error("prd_drafter.py failed: %s — sound bytes preserved in pending_approval.json", e)
        manifest[stem]["status"] = "trigger_failed"

    _save_manifest(manifest)
    _save_pending({})


# ── Downloads drain ───────────────────────────────────────────────────────────

_DOWNLOADS = Path.home() / "Downloads"


def _drain_downloads(watch_dir: Path) -> None:
    """Move any .m4a files from ~/Downloads to the watch folder automatically."""
    for m4a in _DOWNLOADS.glob("*.m4a"):
        dest = watch_dir / m4a.name
        if dest.exists():
            log.info("Downloads drain: %s already in watch folder — skipping", m4a.name)
            continue
        try:
            m4a.rename(dest)
            log.info("Downloads drain: moved %s to watch folder", m4a.name)
        except Exception as e:
            log.error("Downloads drain: failed to move %s: %s", m4a.name, e)


# ── Main poll loop ─────────────────────────────────────────────────────────────

def _get_recordings_dir(cfg: dict) -> Path:
    raw = cfg.get("voice_memos_path", "")
    return Path(raw).expanduser()


def poll_once(cfg: dict) -> None:
    """One polling iteration: drain downloads, check pending, scan for new files."""
    recordings_dir = _get_recordings_dir(cfg)
    _drain_downloads(recordings_dir)
    _check_pending_and_trigger()

    if not recordings_dir.exists():
        log.warning("Voice Memos folder not found: %s", recordings_dir)
        return

    manifest = _load_manifest()
    pending  = _load_pending()

    # Don't enqueue new recordings while one is pending approval
    if pending.get("status") == "pending_approval":
        log.debug("Waiting for approval on %s — skipping scan.", pending.get("recording_path", "?"))
        return

    for m4a in sorted(recordings_dir.glob("*.m4a")):
        stem = m4a.stem
        if stem in manifest:
            continue  # already processed

        log.info("New recording detected: %s", m4a.name)
        manifest[stem] = {"status": "detected", "detected_at": _now_iso(), "path": str(m4a)}
        _save_manifest(manifest)

        # Stage 1: transcribe
        txt_path = _transcribe(m4a, cfg)
        if txt_path is None:
            manifest[stem]["status"] = "transcription_failed"
            _save_manifest(manifest)
            continue

        manifest[stem]["transcribed"] = True
        manifest[stem]["transcript_path"] = str(txt_path)
        _save_manifest(manifest)

        # Stage 1.5: upload transcript to Google Drive
        drive_url = _upload_to_drive(txt_path)
        if drive_url:
            manifest[stem]["drive_url"] = drive_url
            _save_manifest(manifest)

        # Stage 2: distil
        distil_result = _distil(txt_path)
        if distil_result is None:
            manifest[stem]["status"] = "distillation_failed"
            _save_manifest(manifest)
            _post_slack_raw(
                f"Audio Bridge: Distillation failed for {m4a.name}. "
                f"Raw transcript at: {txt_path}",
                cfg,
            )
            continue

        manifest[stem]["distilled"] = True
        _save_manifest(manifest)

        # Stage 3: smart route based on content
        route = _smart_route(distil_result, stem, cfg)
        drive_url = manifest[stem].get("drive_url")
        ok = _post_for_approval(str(m4a), distil_result, route, cfg, drive_url=drive_url)

        if ok:
            manifest[stem]["status"] = "pending_approval"
            _save_pending({
                "status": "pending_approval",
                "recording_path": str(m4a),
                "sound_bytes": distil_result.get("sound_bytes", []),
                "flags": distil_result.get("flags", []),
                "recording_label": distil_result.get("recording_label", stem),
                "route": route,
                "drive_url": drive_url,
            })
        else:
            manifest[stem]["status"] = "slack_post_failed"

        _save_manifest(manifest)
        # Only process one new recording per cycle
        break


def main() -> None:
    log.info("Audio Bridge daemon starting ...")
    cfg = _load_routing()
    poll_interval = cfg.get("poll_interval_seconds", 30)

    while True:
        try:
            poll_once(cfg)
        except Exception as e:
            log.error("Unhandled error in poll_once: %s", e)
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
